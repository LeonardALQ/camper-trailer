"""Every cable and pipe of the home trailer in 3D (H28), from data/routes.yaml on the solved layout.

Each run names its system, what it feeds, its two ends (a line of data/assemblies/trailer.yaml or a fixture of
data/routes.yaml, and a point on that line's envelope box) and its path through the ways: the ceiling bulkheads, the
chase behind the plinth, the under-floor runs along the rails and the glands of data/services.yaml. A path point is
three expressions over the layout's parameters, the envelope boxes (EL_04.x0 for line EL-04's box) and the ways'
constants, and "." repeats the previous point's value. resolve() turns the runs into filleted centrelines at the
cable's or pipe's minimum bend radius, sizes every DC circuit by its current and its voltage drop at the routed length
(report 20's 2 % limit), and adds up the lengths, masses and prices. checks() measures SVC-01 to SVC-12.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "data"
ROUTES = DATA / "routes.yaml"
SYSTEMS = ("dc48", "pv", "dc24", "dc12", "data", "ac230", "lamps", "fresh", "hot", "waste", "vent", "diesel", "refrigerant")
ELECTRICAL = ("dc48", "pv", "dc24", "dc12", "data", "ac230", "lamps")
ELV = ("dc48", "pv", "dc24", "dc12", "data", "lamps")
WETS = ("fresh", "hot", "waste", "vent", "diesel")


class B:
    """An envelope box with its faces and centre, for the path expressions."""

    def __init__(self, box):
        self.x0, self.y0, self.z0, self.x1, self.y1, self.z1 = box
        self.cx, self.cy, self.cz = (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2, (self.z0 + self.z1) / 2
        self.box = tuple(box)


def key(iid: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", iid)


def cell_half(c) -> tuple:
    """A transit frame's cell [dx, dy, m] or [dx, dy, m, n, axis]: n modules of m side by side along the frame's X or
    Y (a pair's two cores, each in its own module). Its half-widths in X and Y."""
    m, n = c[2], (c[3] if len(c) > 3 else 1)
    along_x = len(c) > 4 and str(c[4]).lower() == "x"
    return (n * m / 2, m / 2) if along_x else (m / 2, n * m / 2)


def load() -> dict:
    return yaml.safe_load(ROUTES.read_text(encoding="utf-8"))


def _eval(expr, ns: dict) -> float:
    if isinstance(expr, (int, float)):
        return float(expr)
    return float(eval(str(expr), {"__builtins__": {}, "min": min, "max": max, "abs": abs}, ns))


def namespace(V: dict, blocks: list, data: dict, glands: dict | None = None) -> dict:
    """Parameters, envelope boxes (by line and instance id), the glands, the ways' constants, then the fixtures."""
    ns = dict(V)
    for b in blocks:
        if b.get("box"):
            ns[key(b["iid"])] = B(b["box"])
            ns.setdefault(key(b["id"]), ns[key(b["iid"])])
    for gid, g in (glands or {}).items():
        x, y, z = g["p"]
        hx, hy = g.get("w", g["d"]) / 2, g.get("h", g["d"]) / 2
        ns[gid] = B((x - hx, y - hy, z - hy, x + hx, y + hy, z + hy)) if g["at"] in ("floor", "roof") else \
            B((x - g["d"] / 2, y - g["d"] / 2, z - g["d"] / 2, x + g["d"] / 2, y + g["d"] / 2, z + g["d"] / 2))
        for rid, c in (g.get("cells") or {}).items():   # a transit frame's module for each run, by its centre
            hx, hy = cell_half(c)                       # a pair's two cores lie in two modules side by side
            dx, dy, m = c[:3]
            ns[f"{gid}_{key(rid)}"] = B((x + dx - hx, y + dy - hy, z - m / 2, x + dx + hx, y + dy + hy, z + m / 2))
    for k, v in (data.get("consts") or {}).items():
        ns[k] = _eval(v, ns)
    for f in data.get("fixtures") or []:
        c = [_eval(v, ns) for v in f["at"]]
        s = [_eval(v, ns) for v in f.get("size", [40, 40, 40])]
        ns[key(f["id"])] = B((c[0] - s[0] / 2, c[1] - s[1] / 2, c[2] - s[2] / 2, c[0] + s[0] / 2, c[1] + s[1] / 2, c[2] + s[2] / 2))
    return ns


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _add(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)


def _spec_points(specs: list, ns: dict, prev=None) -> list[tuple]:
    out = []
    for spec in specs:
        p = tuple(prev[i] if (v == "." and prev) else _eval(v, ns) for i, v in enumerate(spec))
        out.append(p)
        prev = p
    return out


def bundle_points(way: dict, k: float, n: int, pitch: float, ns: dict) -> list[tuple]:
    """A member's centreline through a bundle way: the way's centreline offset by the member's place in the way's grid
    (`cols` across, rows after, centred), the offset carried through every corner so the inside of a turn stays the
    inside, each corner the mitre of the two offset legs. The grid's first axis is the way's `side` (a direction across
    its first leg), the second the first leg crossed with it."""
    C = _spec_points(way["path"], ns)
    cols = int(way.get("cols", 1))
    rows = max(1, math.ceil(n / cols))
    u = ((k % cols) - (cols - 1) / 2) * pitch
    v = ((k // cols) - (rows - 1) / 2) * pitch
    d, _ = _unit(_sub(C[1], C[0]))
    side = tuple(float(x) for x in way.get("side", (0.0, 0.0, 1.0)))
    e1, _ = _unit(_add(side, d, -_dot(side, d)))
    e2 = _cross(d, e1)
    o = _add(_add((0.0, 0.0, 0.0), e1, u), e2, v)
    pts = [_add(C[0], o)]
    for i in range(1, len(C) - 1):
        d1, _ = _unit(_sub(C[i], C[i - 1]))
        d2, _ = _unit(_sub(C[i + 1], C[i]))
        c = _dot(d1, d2)
        if c > 1 - 1e-9:
            pts.append(_add(C[i], o))
            continue
        a, _ = _unit(_cross(d1, d2))
        th = math.acos(max(-1.0, min(1.0, c)))
        o2 = _add(_add(_add((0.0, 0.0, 0.0), o, math.cos(th)), _cross(a, o), math.sin(th)), a, _dot(a, o) * (1 - math.cos(th)))
        w = _sub(o, o2)
        t = (_dot(w, d1) - c * _dot(w, d2)) / (c * c - 1)
        pts.append(_add(_add(C[i], o), d1, t))
        o = o2
    pts.append(_add(C[-1], o))
    return pts


def _points(run: dict, ns: dict, bundles: dict | None = None) -> list[tuple]:
    """The run's points: its ends and path, where a path entry "@<way>" follows that bundle way at the run's place."""
    pts, prev = [], None
    for spec in [run["from"]["at"]] + list(run.get("path") or []) + [run["to"]["at"]]:
        if isinstance(spec, str) and spec.startswith("@"):
            w, *cut = spec[1:].split(":")   # "@W" the whole bundle way, "@W:a:b" its points a to b
            b = bundles[w]
            seq = bundle_points(b["way"], lane_of(run, w), b["n"], b["pitch"], ns)
            if cut:
                seq = seq[int(cut[0]):int(cut[1]) + 1]
        else:
            seq = [tuple(prev[i] if (v == "." and prev) else _eval(v, ns) for i, v in enumerate(spec))]
        for p in seq:
            if prev is None or math.dist(p, prev) > 0.5:
                pts.append(tuple(p))
            prev = p
    return pts


def _apply_fall(pts: list[tuple], slope: float) -> list[tuple]:
    """A gravity waste's centreline lowered so each leg falls at least the slope, its last point (the tank inlet)
    kept where the data puts it."""
    out = [pts[0]]
    for i, p in enumerate(pts[1:], 1):
        q = out[-1]
        if i < len(pts) - 1:
            h = math.hypot(p[0] - q[0], p[1] - q[1])
            p = (p[0], p[1], min(p[2], q[2] - h * slope))
        out.append(p)
    return out


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _unit(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return (v[0] / n, v[1] / n, v[2] / n), n


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def smooth_jogs(pts: list[tuple], r: float) -> list[tuple]:
    """A flexible cable or hose steps between lanes, or round a small offset, as an S: two corners that turn back to
    the first direction a short leg apart. Where that leg is too short for both bends at radius r, the step is spread
    along the straights either side as a slant, which is how the cable lies, so each corner keeps its radius. A step
    the straights cannot take is left for SVC-02 to report."""
    pts = [tuple(float(c) for c in p) for p in pts]

    def turns(j):
        if j <= 0 or j >= len(pts) - 1:
            return False
        a, _ = _unit(_sub(pts[j], pts[j - 1]))
        b, _ = _unit(_sub(pts[j + 1], pts[j]))
        return _dot(a, b) < 1 - 1e-6

    for _ in range(60):
        done = True
        for i in range(1, len(pts) - 2):
            a, b, c, d = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
            if min(math.dist(a, b), math.dist(b, c), math.dist(c, d)) < 1e-6:
                continue
            (u, l0), (w, l1), (v, l2) = _unit(_sub(b, a)), _unit(_sub(c, b)), _unit(_sub(d, c))
            if _dot(u, v) < 0.999 or abs(_dot(u, w)) > 0.999:
                continue
            phi = math.acos(max(-1.0, min(1.0, _dot(u, w))))
            if l1 >= 2 * r * math.tan(phi / 2) - 1e-6:
                continue
            sh0 = 0.5 if turns(i - 1) else 1.0
            sh2 = 0.5 if turns(i + 2) else 1.0

            def t_at(j):  # the tangent length the neighbouring corner j needs at radius r
                if not turns(j):
                    return 0.0
                p, _ = _unit(_sub(pts[j], pts[j - 1]))
                q, _ = _unit(_sub(pts[j + 1], pts[j]))
                return r * math.tan(math.acos(max(-1.0, min(1.0, _dot(p, q)))) / 2)

            t0, t2 = t_at(i - 1), t_at(i + 2)
            s, best = 1.0, None
            while s < min(l0, l2):
                b2 = (b[0] - u[0] * s, b[1] - u[1] * s, b[2] - u[2] * s)
                c2 = (c[0] + u[0] * s, c[1] + u[1] * s, c[2] + u[2] * s)
                wd, ld = _unit(_sub(c2, b2))
                t = r * math.tan(math.acos(max(-1.0, min(1.0, _dot(u, wd)))) / 2)
                if (t <= ld / 2 and t <= (l0 - s) * sh0 and t <= (l2 - s) * sh2
                        and t0 <= (l0 - s) * sh0 + 1e-6 and t2 <= (l2 - s) * sh2 + 1e-6):
                    best = (b2, c2)
                    break
                s += 1.0
            if best:
                pts[i], pts[i + 1] = best
                done = False
                break
        if done:
            break
    return _drop_steps(pts, r)


def _off_line(p, a, b) -> float:
    """Distance of p from the segment a-b."""
    d, ln = _unit(_sub(b, a))
    t = max(0.0, min(ln, _dot(_sub(p, a), d)))
    return math.dist(p, (a[0] + d[0] * t, a[1] + d[1] * t, a[2] + d[2] * t))


def _drop_steps(pts: list[tuple], r: float, max_deg: float = 3.0, max_mm: float = 12.0) -> list[tuple]:
    """A lane step or a small offset that turns out of the run's plane (up, a few millimetres across, then along)
    is two corners a short leg apart that cannot both take the bend radius. The cable lies on the slant instead: the
    step's corner is dropped where the straight it merges into turns by no more than `max_deg` and the corner lies
    within `max_mm` of the slant, so a deliberate offset (out of a rail, round a part) keeps its corners."""
    pts = list(pts)

    def turn(j):
        if j <= 0 or j >= len(pts) - 1:
            return 0.0
        a, _ = _unit(_sub(pts[j], pts[j - 1]))
        b, _ = _unit(_sub(pts[j + 1], pts[j]))
        return math.acos(max(-1.0, min(1.0, _dot(a, b))))

    def fits(j):
        phi = turn(j)
        if phi < 1e-3:
            return True
        sh0 = 0.5 if turn(j - 1) >= 1e-3 else 1.0
        sh1 = 0.5 if turn(j + 1) >= 1e-3 else 1.0
        t = r * math.tan(phi / 2)
        return t <= min(math.dist(pts[j - 1], pts[j]) * sh0, math.dist(pts[j], pts[j + 1]) * sh1) + 1e-6

    def angle(p, q, s):  # between the leg p->q and p->s
        a, la = _unit(_sub(q, p))
        b, lb = _unit(_sub(s, p))
        return 0.0 if la < 1e-9 or lb < 1e-9 else math.degrees(math.acos(max(-1.0, min(1.0, _dot(a, b)))))

    skip = set()
    for _ in range(80):
        bad = [j for j in range(1, len(pts) - 1) if not fits(j) and pts[j] not in skip]
        if not bad:
            break
        j = bad[0]
        options = []
        for k in (j, j - 1, j + 1):
            if not 0 < k < len(pts) - 1:
                continue
            # dropping k merges the legs k-1 -> k and k -> k+1; the longer one must keep its direction
            long_from = math.dist(pts[k - 1], pts[k]) >= math.dist(pts[k], pts[k + 1])
            dev = angle(pts[k - 1], pts[k], pts[k + 1]) if long_from else angle(pts[k + 1], pts[k], pts[k - 1])
            if dev > max_deg or _off_line(pts[k], pts[k - 1], pts[k + 1]) > max_mm:
                continue
            trial = pts[:k] + pts[k + 1:]
            options.append((dev, k, trial))
        took = False
        for dev, k, trial in sorted(options, key=lambda o: o[0]):
            before = sum(1 for m in range(max(1, k - 2), min(len(pts) - 1, k + 3)) if not fits(m))
            saved, pts = pts, trial
            after = sum(1 for m in range(max(1, k - 2), min(len(pts) - 1, k + 2)) if not fits(m))
            if after < before:
                took = True
                break
            pts = saved
        if not took:
            skip.add(pts[j])
    return pts


def fillet(pts: list[tuple], r: float, elbow_r: float | None = None, rigid: bool = False) -> dict:
    """The centreline with each corner bent at radius r: the corners' largest radius the straight lengths allow, the
    routed length and a dense polyline (arcs every 10 degrees) for the clearance tests and the drawings. A pipe that
    may use fittings (`elbow_r`) turns at an elbow where its bend does not fit, and a rigid pipe turns at a bend
    fitting at every corner. Each such corner is marked as a fitting."""
    n = len(pts)
    seg = [_unit(_sub(pts[i + 1], pts[i])) for i in range(n - 1)]
    corners, dense, length = [], [pts[0]], 0.0
    phis = {}
    for i in range(1, n - 1):
        cosang = max(-1.0, min(1.0, sum(a * b for a, b in zip(seg[i - 1][0], seg[i][0]))))
        phis[i] = math.acos(cosang)
    turns = lambda j: 0 < j < n - 1 and phis[j] >= 1e-3  # noqa: E731
    for i in range(1, n - 1):
        (d0, l0), (d1, l1) = seg[i - 1], seg[i]
        phi = phis[i]
        if phi < 1e-3:
            corners.append(dict(i=i, phi=0.0, r_max=math.inf, r=0.0, t=0.0))
            continue
        # a leg is shared with the corner at its other end only if that corner turns too
        share0 = 0.5 if turns(i - 1) else 1.0
        share1 = 0.5 if turns(i + 1) else 1.0
        t_avail = min(l0 * share0, l1 * share1)
        r_max = t_avail / math.tan(phi / 2)
        elbow = rigid or (elbow_r is not None and r_max < r)
        rr = min(elbow_r if elbow else r, r_max)
        corners.append(dict(i=i, phi=phi, r_max=r_max, r=rr, t=rr * math.tan(phi / 2), at=pts[i], elbow=elbow))
    tan_at = {c["i"]: c for c in corners}
    for i in range(1, n):
        a, b = pts[i - 1], pts[i]
        d, ln = seg[i - 1]
        ta = tan_at.get(i - 1, {}).get("t", 0.0)
        tb = tan_at.get(i, {}).get("t", 0.0)
        p_end = (b[0] - d[0] * tb, b[1] - d[1] * tb, b[2] - d[2] * tb)
        length += max(0.0, ln - ta - tb)
        dense.append(p_end)
        c = tan_at.get(i)
        if c and c["t"] > 0:
            d1 = seg[i][0]
            # arc from p_end to the next tangent point, centre on the bisector inside the bend
            q = (b[0] + d1[0] * c["t"], b[1] + d1[1] * c["t"], b[2] + d1[2] * c["t"])
            centre_d = c["r"] / math.cos(c["phi"] / 2)
            bis2, _ = _unit((d1[0] - d[0], d1[1] - d[1], d1[2] - d[2]))
            ctr = (b[0] + bis2[0] * centre_d, b[1] + bis2[1] * centre_d, b[2] + bis2[2] * centre_d)
            u, _ = _unit(_sub(p_end, ctr))
            w, _ = _unit(_sub(q, ctr))
            hm = 2 * math.cos(c["phi"] / 2)
            mid = tuple(ctr[k] + (u[k] + w[k]) / hm * c["r"] for k in range(3))
            c.update(p0=p_end, p1=q, mid=mid)   # the bend's tangent points and its midpoint, for the swept model
            steps = max(2, int(math.degrees(c["phi"]) / 10))
            for k in range(1, steps):
                s = k / steps
                # slerp between u and w
                om = c["phi"]
                f0, f1 = math.sin((1 - s) * om) / math.sin(om), math.sin(s * om) / math.sin(om)
                v = (u[0] * f0 + w[0] * f1, u[1] * f0 + w[1] * f1, u[2] * f0 + w[2] * f1)
                dense.append((ctr[0] + v[0] * c["r"], ctr[1] + v[1] * c["r"], ctr[2] + v[2] * c["r"]))
            length += c["r"] * c["phi"]
            dense.append(q)
    return dict(corners=corners, dense=dense, length=length)


# ------------------------------------------------------------------ cable and pipe sizes
def kinds(data: dict) -> dict:
    """Every cable and pipe kind with its sizes: outside diameter, mass a metre, minimum bend radius, price a metre and,
    for a conductor, the drop in mV per amp and metre of route and the current rating (data/routes.yaml `cables`)."""
    cond = {float(k): v for k, v in data["conductors"].items()}
    out = {}
    for kid, k in data["kinds"].items():
        sizes = {}
        for s in k.get("sizes") or [None]:
            s = float(s) if s is not None else None
            c = cond.get(s) if s is not None else None
            ns = dict(mm2=float(s or 0), od1=c["od"] if c else 0.0, kg1=c["kg_m"] if c else 0.0, r1=c["r"] if c else 0.0)
            od = _eval(k["od"], ns)
            ns["od"] = od
            sizes[s] = dict(size=s, od=od, kg_m=_eval(k["kg_m"], ns), bend_r=_eval(k["bend_r"], ns), aud_m=_eval(k["aud_m"], ns),
                            mv_am=c["mv"] if c else None,
                            amps=c["free" if k.get("rating") == "free" else "amps"] * k.get("derate", 1.0) if c else None)
        out[kid] = dict(k, sizes=sizes)
    return out


def _label(kind: dict, size) -> str:
    return kind["what"].format(size=f"{size:g}" if isinstance(size, (int, float)) else size)


def size_dc(run: dict, length_m: float, kind: dict, limit_pct: float, least: float | None = None) -> tuple:
    """The smallest size of the run's kind whose drop at the design current over the routed length stays within the
    limit and whose rating carries the current, and at least `least`, the size SVC-10's rating where the run lies asks
    for. A run that fixes its size keeps it, and the drop is reported."""
    amps, volts = run["amps"], run["volts"]
    lim = limit_pct / 100 * volts
    up = upstream_v(run)
    order = sorted(s for s in kind["sizes"] if s is not None)
    fixed = float(run["size"]) if run.get("size") is not None else None
    for s in ([fixed] if fixed is not None else order):
        k = kind["sizes"][s]
        vd = k["mv_am"] * amps * length_m / 1000 + up
        if fixed is not None or (vd <= lim and amps <= k["amps"] and s >= (least or 0.0) - 1e-9):
            smaller = [x for x in order if x < s]
            if fixed is not None:
                why = run.get("size_why") or "Report 20's size"
            elif least and s <= least + 1e-9 and smaller:
                why = f"{smaller[-1]:g} mm2 is rated under its current or its fuse where it lies (SVC-10)"
            elif smaller:
                p = smaller[-1]
                kp = kind["sizes"][p]
                vdp = kp["mv_am"] * amps * length_m / 1000 + up
                why = (f"{p:g} mm2 would drop {100 * vdp / volts:.1f} %{' end to end' if up else ''}" if vdp > lim else
                       f"{p:g} mm2 is rated {kp['amps']:.0f} A in the bulkhead")
            else:
                why = f"The smallest size used, {s:g} mm2, for strength"
            return s, vd, why
    s = order[-1]
    k = kind["sizes"][s]
    return s, k["mv_am"] * amps * length_m / 1000 + up, "Largest size listed, still over the limit"


def upstream_v(run: dict) -> float:
    """The drop at the run's design current in the part of its circuit outside the trailer (`upstream`, the ute half
    of the ute feed), which SVC-06 adds to the run's own, so the limit holds from the source to the load."""
    u = run.get("upstream")
    return 0.0 if not u else float(u["mv"]) * run["amps"] * float(u["m"]) / 1000


# ------------------------------------------------------------------ the layout's boxes and the glands
def _blocks_of(lay) -> tuple[dict, list]:
    """The parameters and the envelope blocks of a Layout (cad/trailer.py), as plain dicts. A chassis fitting with more
    than one position has no box of its own, so each of its positions is a block (cad/chassis.py fitting_boxes): each
    D-ring, and each corner steady over the box its leg sweeps from folded for travel to standing at 90 degrees."""
    bl = [dict(iid=b.iid, id=b.id, name=b.name, system=b.system, box=b.box, hollow=b.hollow, keep_clear=b.keep_clear,
               role=b.extra.get("role")) for b in lay.blocks if b.box is not None]
    ch = getattr(lay, "chassis", None)
    for b in lay.blocks:
        f = b.extra.get("fitting") if b.box is None else None
        if f is None or ch is None:
            continue
        spec = next(d for d in ch.data["fittings"] if d["id"] == f.id)
        if spec.get("poses") == "steadies":
            boxes = [(f"{b.name.split(',')[0]} {k}, folded to standing", p["sweep"]) for k, p in enumerate(ch.steady_poses(), 1)]
        else:
            from .chassis import fitting_boxes
            boxes = [(f"{b.name.split(',')[0]} {k}", bx) for k, bx in enumerate(fitting_boxes(ch, f), 1)]
        bl += [dict(iid=f"{b.iid} #{k}", id=b.id, name=name, system=b.system, box=tuple(bx), hollow=False, keep_clear=False)
               for k, (name, bx) in enumerate(boxes, 1)]
    return dict(lay.V), bl


def bed_travel(V: dict, blocks: list) -> list:
    """The lift bed's platform, underlay and mattress over their whole travel, from the night stop to the day position
    (H1), so no run stands in the bed's way at either end or between."""
    dz = V["bed_night_h"] - V["bed_day_h"]
    out = []
    for b in blocks:
        if b["id"] in ("LB-01", "LB-02", "LB-03") and b.get("box"):
            x0, y0, z0, x1, y1, z1 = b["box"]
            out.append(dict(b, iid=b["iid"] + " travel", name=b["name"] + ", over its travel", box=(x0, y0, z0 + min(0, dz), x1, y1, z1 + max(0, dz))))
    return out


def gland_points(V: dict, glands: list) -> dict:
    """Each gland's centre in DIM-01, in the middle of the panel it passes through."""
    wall = (V["half_bw"] + V["half_in"]) / 2
    endw = V["end_wall_t"] / 2
    out = {}
    for g in glands:
        at = g["at"]
        if at == "kerb":
            p = (g["x"], -wall, g["z"])
        elif at == "road":
            p = (g["x"], wall, g["z"])
        elif at == "rear":
            p = (V["body_x1"] - endw, g["y"], g["z"])
        elif at == "front":
            p = (V["body_x0"] + endw, g["y"], g["z"])
        elif at == "floor":
            p = (g["x"], g["y"], (V["floor_z"] + V["floor_underside_z"]) / 2)
        else:
            p = (g["x"], g["y"], (V["ceiling_z"] + V["roof_top_z"]) / 2)
        out[g["id"]] = dict(g, p=p)
    return out


# ------------------------------------------------------------------ the shared ways and their lanes
WAY_RE = re.compile(r"\bL_([A-Za-z0-9]+)\b")


def way_members(data: dict) -> dict:
    """Each way of data/routes.yaml `ways` and the runs in it: a run is in a way when its ends or path name the way's
    lane offset, L_<way>."""
    out = {w: [] for w in data.get("ways") or {}}
    for r in data["runs"]:
        spec = [r["from"]["at"], *(r.get("path") or []), r["to"]["at"]]
        named = set(WAY_RE.findall(str(spec))) | {s[1:].split(":")[0] for s in spec if isinstance(s, str) and s.startswith("@")}
        named |= set(r.get("ways") or [])   # a loom the run shares with no lane offset of its own
        for w in sorted(named):
            if w not in out:
                raise KeyError(f"{r['id']} names the way {w}, which data/routes.yaml `ways` does not list")
            out[w].append(r["id"])
    return out


def _way_what(v) -> str:
    return v if isinstance(v, str) else v["what"]


def _min_pitch(v) -> float:
    """A way's least pitch, where a fitting sets it (a transit frame's modules), else none."""
    return 0.0 if isinstance(v, str) else float(v.get("min_pitch", 0.0))


def lane_of(run: dict, way: str) -> float:
    """A run's lane in a way: one number for every way it is in, or a map by way."""
    v = run.get("lane", 0)
    return float(v.get(way, 0) if isinstance(v, dict) else v)


# ------------------------------------------------------------------ resolve every run
def resolve(lay=None, V: dict | None = None, blocks: list | None = None) -> dict:
    """Every run's centreline, length, size, drop, mass and price on the layout. A way's lane pitch is the largest
    outside diameter among its runs, rounded up to the next mm, and a DC run's size follows its routed length, so the
    two are worked out together until neither changes."""
    bars = []
    if lay is not None:
        V, blocks = _blocks_of(lay)
        bars = _bar_capsules(lay)
    data = load()
    svc = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8"))
    glands = gland_points(V, svc["glands"])
    ns = namespace(V, blocks, data, glands)
    K = kinds(data)
    fixtures = {f["id"]: dict(f, box=ns[key(f["id"])].box) for f in data.get("fixtures") or []}
    members = way_members(data)
    pitch = {w: 0.0 for w in members}
    bend = {}   # a nesting way's lanes turn in one plane side by side, so each bends at the way's largest radius
    least = {}  # a sized run's least size from SVC-10, where its rating where it lies is under its current or its device
    for _ in range(16):
        bundles = {w: dict(way=v, n=len(members[w]), pitch=pitch[w]) for w, v in data["ways"].items() if isinstance(v, dict) and v.get("path")}
        runs = [_resolve_run(r, ns, K, data["rules"], fixtures, pitch, bundles, bend.get(r["id"], 0.0), least.get(r["id"])) for r in data["runs"]]
        own = {r["id"]: r["bend_r"] for r in runs}
        nest = {w: ids for w, ids in members.items() if isinstance(data["ways"][w], dict) and data["ways"][w].get("nest")}
        way_r = {w: max((own[i] for i in ids), default=0.0) for w, ids in nest.items()}
        new_bend = {i: max(way_r[w] for w, ids in nest.items() if i in ids) for i in own if any(i in ids for ids in nest.values())}
        od = {r["id"]: r["od"] for r in runs}
        new = {w: max(float(math.ceil(max((od[i] for i in ids), default=0.0) - 1e-6)), _min_pitch(data["ways"][w]))
               for w, ids in members.items()}
        grow = _rating_sizes(dict(runs=runs, data=data, blocks=blocks, ns=ns, svc=svc, V=V, glands=glands,
                                  ways={w: dict(runs=ids) for w, ids in members.items()}), K)
        if new == pitch and new_bend == bend and not grow:
            break
        pitch, bend = new, new_bend
        least.update(grow)
    ways = {w: dict(what=_way_what(data["ways"][w]), runs=ids, pitch_mm=pitch[w], bundle=w in bundles) for w, ids in members.items()}
    return dict(runs=runs, data=data, kinds=K, V=V, blocks=blocks, glands=glands, fixtures=fixtures, svc=svc, ns=ns, bars=bars,
                ways=ways)


def _rating_sizes(res: dict, K: dict) -> dict:
    """The next size up for each run that sizes itself (no `size` of its own) and whose SVC-10 rating where it lies is
    under its design current or its device, so resolve() sizes it again."""
    out = {}
    runs = {r["id"]: r for r in res["runs"]}
    fixed = {x["id"] for x in res["data"]["runs"] if x.get("size") is not None}
    for row in ratings(res)["rows"]:
        r = runs[row["run"]]
        if row["spare"] >= -1e-6 or r["id"] in fixed:
            continue
        bigger = sorted(s for s in K[r["kind"]]["sizes"] if s is not None and s > r["size"] + 1e-9)
        if bigger:
            out[r["id"]] = bigger[0]
    return out


def _resolve_run(r: dict, ns: dict, K: dict, rule: dict, fixtures: dict, pitch: dict, bundles: dict, way_bend: float = 0.0,
                 least: float | None = None) -> dict:
    """One run on the layout, with its lane offset in each way it shares. A run in a way bends at the way's largest
    radius (`way_bend`), or its own if larger, so the lanes' bends are concentric enough to keep their pitch. `least`
    is the size SVC-10 asks for where the run lies."""
    kind = K[r["kind"]]
    for w, p in pitch.items():
        ns[f"L_{w}"] = lane_of(r, w) * p
    pts = _points(r, ns, bundles)
    if r["system"] == "waste" and not r.get("pumped"):
        pts = _apply_fall(pts, rule["fall"])
    raw = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) / 1000
    row = dict(r, points=pts, kind_what=kind["what"], group=kind.get("group", r["system"]))
    conductor = any(v["mv_am"] is not None for v in kind["sizes"].values())
    if r.get("amps") is not None and r.get("volts") is not None and conductor:
        size, vd, why = size_dc(r, raw, kind, rule["drop_pct"] if r["system"] != "ac230" else rule["drop_ac_pct"], least)
    else:
        size = float(r["size"]) if r.get("size") is not None else next(iter(kind["sizes"]))
        vd, why = None, r.get("size_why")
    k = kind["sizes"][size]
    rigid = bool(kind.get("rigid"))
    elbow_r = k["od"] * kind["elbow_r"] if kind.get("elbow_r") else None
    if not rigid:
        pts = smooth_jogs(pts, k["bend_r"])
        row["points"] = pts
    f = fillet(pts, max(k["bend_r"], way_bend), elbow_r=elbow_r, rigid=rigid)
    length_m = f["length"] / 1000
    if vd is not None:
        vd = k["mv_am"] * r["amps"] * length_m / 1000 + upstream_v(r)
    cores = kind.get("cores", 1)
    row.update(size=size, cable=_label(kind, size), od=k["od"], bend_r=k["bend_r"], dense=f["dense"], corners=f["corners"],
               length_m=round(length_m, 2), mass_kg=round(k["kg_m"] * length_m, 3),
               aud=round(k["aud_m"] * length_m * (1 + rule["waste_pct"] / 100), 2), aud_m=k["aud_m"], kg_m=k["kg_m"],
               fittings=sum(1 for c in f["corners"] if c.get("elbow")), rigid=rigid,
               vd_v=None if vd is None else round(vd, 3), vd_pct=None if vd is None else round(100 * vd / r["volts"], 2),
               size_why=why, cores=cores, price_basis=kind.get("price_basis"), mass_basis=kind.get("mass_basis"),
               rating_a=k["amps"], priced_in=r.get("priced_in") or kind.get("priced_in"))
    ends = {r["from"]["line"], r["to"]["line"]} | _ids(r, "ends_also")
    row["ends"] = ends | {fixtures[e]["line"] for e in list(ends) if e in fixtures}
    return row


# ------------------------------------------------------------------ geometry for the checks
def _pt_box(p, b) -> float:
    dx = max(b[0] - p[0], 0.0, p[0] - b[3])
    dy = max(b[1] - p[1], 0.0, p[1] - b[4])
    dz = max(b[2] - p[2], 0.0, p[2] - b[5])
    if dx == dy == dz == 0.0:   # inside: the depth to the nearest face, negative
        return -min(p[0] - b[0], b[3] - p[0], p[1] - b[1], b[4] - p[1], p[2] - b[2], b[5] - p[2])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _walled(p, q, floor_z: float, zones: list) -> bool:
    """A 230 V stretch in its own conduit: both ends and the middle of segment pq are under the floor or inside one
    of the rule's conduit zones, so a stretch through a floor gland counts as well."""
    pts = (p, q, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2))
    return all(t[2] <= floor_z + 1 or any(_pt_box(t, z) <= 0 for z in zones) for t in pts)


def seg_box(a, b, box) -> tuple[float, tuple]:
    """Least distance from segment ab to a box (negative inside it), and the point of the segment where it occurs."""
    lo, hi = 0.0, 1.0
    f = lambda t: _pt_box((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t), box)  # noqa: E731
    for _ in range(40):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if f(m1) < f(m2):
            hi = m2
        else:
            lo = m1
    t = (lo + hi) / 2
    best = min((f(0.0), 0.0), (f(t), t), (f(1.0), 1.0))
    t = best[1]
    return best[0], (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def seg_seg(p1, q1, p2, q2) -> float:
    """Least distance between two segments (Ericson's closest points of two segments)."""
    d1, d2, r = _sub(q1, p1), _sub(q2, p2), _sub(p1, p2)
    dot = lambda u, v: u[0] * v[0] + u[1] * v[1] + u[2] * v[2]  # noqa: E731
    a, e, f = dot(d1, d1), dot(d2, d2), dot(d2, r)
    if a <= 1e-9 and e <= 1e-9:
        return math.dist(p1, p2)
    if a <= 1e-9:
        s, t = 0.0, min(1.0, max(0.0, f / e))
    else:
        c = dot(d1, r)
        if e <= 1e-9:
            t, s = 0.0, min(1.0, max(0.0, -c / a))
        else:
            b = dot(d1, d2)
            den = a * e - b * b
            s = min(1.0, max(0.0, (b * f - c * e) / den)) if den > 1e-9 else 0.0
            t = (b * s + f) / e
            if t < 0:
                t, s = 0.0, min(1.0, max(0.0, -c / a))
            elif t > 1:
                t, s = 1.0, min(1.0, max(0.0, (b - c) / a))
    c1 = (p1[0] + d1[0] * s, p1[1] + d1[1] * s, p1[2] + d1[2] * s)
    c2 = (p2[0] + d2[0] * t, p2[1] + d2[1] * t, p2[2] + d2[2] * t)
    return math.dist(c1, c2)


def _aabb(pts, pad=0.0):
    xs, ys, zs = zip(*pts)
    return (min(xs) - pad, min(ys) - pad, min(zs) - pad, max(xs) + pad, max(ys) + pad, max(zs) + pad)


def _hit(a, b) -> bool:
    return all(a[i] <= b[i + 3] and b[i] <= a[i + 3] for i in range(3))


def _segs(dense):
    return [(dense[i], dense[i + 1]) for i in range(len(dense) - 1) if math.dist(dense[i], dense[i + 1]) > 1e-6]


def _ids(run: dict, which: str) -> set:
    v = run.get(which) or []
    return set([v] if isinstance(v, str) else v)


def _end_lines(run: dict) -> set:
    """The run's two ends, the lines its fixture ends belong to, and any it names in `ends_also`."""
    if "ends" in run:
        return run["ends"]
    return {run["from"]["line"], run["to"]["line"]} | _ids(run, "ends_also")


def _matches(b: dict, names: set) -> bool:
    return b["iid"] in names or b["id"] in names or b["iid"].split(" ")[0] in names


def _bar_capsules(lay) -> list:
    """The layout's bar members (plan braces, drawbar members) as capsules: axis and radius."""
    out = []
    for b in getattr(lay, "blocks", []) or []:
        if getattr(b, "bar", None):
            out.append(dict(iid=b.iid, id=b.id, name=b.name, p0=tuple(b.bar["p0"]), p1=tuple(b.bar["p1"]),
                            r=max(b.bar["w"], b.bar["h"]) / 2, w=b.bar["w"], h=b.bar["h"]))
    return out


def _bar_gap(segs: list, c: dict, step: float = 15.0) -> float:
    """Least distance from a run's centreline to a bar member's real rectangular section (w across, h deep, along its
    axis), negative inside it. The centreline is sampled every `step` mm."""
    p0 = c["p0"]
    u, ln = _unit(_sub(c["p1"], p0))
    v, _ = _unit((-u[1], u[0], 0.0)) if abs(u[2]) < 0.99 else ((1.0, 0.0, 0.0), 1.0)
    w = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    hw, hh = c["w"] / 2, c["h"] / 2
    best = math.inf
    for a, b in segs:
        n = max(1, int(math.dist(a, b) / step))
        for k in range(n + 1):
            t = k / n
            d = _sub((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t), p0)
            x, y, z = _dot(d, u), abs(_dot(d, v)), abs(_dot(d, w))
            dx, dy, dz = max(0.0, -x, x - ln), max(0.0, y - hw), max(0.0, z - hh)
            g = math.sqrt(dx * dx + dy * dy + dz * dz) if (dx or dy or dz) else -min(hw - y, hh - z, x, ln - x)
            best = min(best, g)
    return best


# ------------------------------------------------------------------ the checks, SVC-01 to SVC-12
PANELS = ("BD-01", "BD-02", "BD-03", "BD-04")


def _solids(res: dict) -> list:
    skip = set(res["data"]["rules"].get("not_tested", []))
    bars = {c["iid"] for c in res.get("bars", [])}
    out = [b for b in res["blocks"] if b.get("box") and not b.get("hollow") and not b.get("keep_clear")
           and b["id"] not in skip and b["iid"] not in bars]
    out += bed_travel(res["V"], res["blocks"])
    out += [dict(iid=k, id=k, name=f["what"], system="fixture", box=f["box"]) for k, f in res["fixtures"].items()
            if f.get("obstacle", True)]
    return out


STRIP_ROLES = ("raiser", "outrigger", "cm_floor")   # the members whose bearer strips carry the floor (CH-S01)
WEDGE_STACK, WEDGE_SLACK, WEDGE_DEPTH = 34.0, 5.0, 84.0   # Roxtec's C wedge: 34 mm of the stack, 84 mm deep, and 5 mm of slack (est.)


def bearer_strips(res: dict) -> list[dict]:
    """The floor's bearer strips (CH-S01) as boxes: on the top of every raiser, outrigger and floor crossmember, up to
    the floor's underside, as cad/trailer_model.py draws them."""
    top = res["V"]["floor_underside_z"]
    return [dict(iid=f"strip on {b['iid']}", id="CH-S01", name=f"Bearer strip on {b['name'].split(',')[0]}",
                 box=(b["box"][0], b["box"][1], b["box"][5], b["box"][3], b["box"][4], top))
            for b in res["blocks"] if b.get("role") in STRIP_ROLES and b.get("box") and top - b["box"][5] > 1]


def frame_room(g: dict) -> tuple:
    """A transit frame's room inside its walls, (x0, y0, x1, y1): its packing space (`w` along X, `h` along Y about
    the gland's point) and, where it names its `stack`, the C wedge's 34 mm and 5 mm of slack past the packing at the
    stack's `wedge_end` (I2-33). A frame whose wedge sits inside the stack (`wedge_at`) has the same room, the
    wedge's slot taken out of the packing there."""
    x, y = g["p"][0], g["p"][1]
    x0, y0, x1, y1 = x - g["w"] / 2, y - g["h"] / 2, x + g["w"] / 2, y + g["h"] / 2
    add = WEDGE_STACK + WEDGE_SLACK if g.get("stack") else 0.0
    end = "+" if g.get("wedge_at") is not None else g.get("wedge_end", "+")
    if g.get("stack") == "x":
        x0, x1 = (x0 - add, x1) if end == "-" else (x0, x1 + add)
    elif g.get("stack") == "y":
        y0, y1 = (y0 - add, y1) if end == "-" else (y0, y1 + add)
    return x0, y0, x1, y1


def frame_wedge(g: dict) -> tuple | None:
    """The C wedge's footprint in plan, (x0, y0, x1, y1): 34 mm along the stack and the packing's width across it, at
    the stack's `wedge_end` past 5 mm of slack, or `wedge_at` mm along the stack from the packing's start with the slack
    ahead of it (Roxtec 124037: the wedge may sit anywhere in the frame)."""
    if not g.get("stack"):
        return None
    rx0, ry0, rx1, ry1 = frame_room(g)
    along = g["stack"] == "x"
    s0, s1 = (rx0, rx1) if along else (ry0, ry1)
    if g.get("wedge_at") is not None:
        a = s0 + float(g["wedge_at"]) + WEDGE_SLACK
    elif g.get("wedge_end", "+") == "+":
        a = s1 - WEDGE_STACK
    else:
        a = s0
    return (a, ry0, a + WEDGE_STACK, ry1) if along else (rx0, a, rx1, a + WEDGE_STACK)


def frame_packing(g: dict) -> list[tuple]:
    """The packing space in plan, one rectangle or the two either side of a wedge inside the stack (`wedge_at`)."""
    rx0, ry0, rx1, ry1 = frame_room(g)
    if not g.get("stack"):
        return [(rx0, ry0, rx1, ry1)]
    along = g["stack"] == "x"
    s0, s1 = (rx0, rx1) if along else (ry0, ry1)
    if g.get("wedge_at") is not None:
        cuts = [(s0, s0 + float(g["wedge_at"])), (s0 + float(g["wedge_at"]) + WEDGE_STACK + WEDGE_SLACK, s1)]
    elif g.get("wedge_end", "+") == "+":
        cuts = [(s0, s1 - WEDGE_STACK - WEDGE_SLACK)]
    else:
        cuts = [(s0 + WEDGE_STACK + WEDGE_SLACK, s1)]
    return [(a, ry0, b, ry1) if along else (rx0, a, rx1, b) for a, b in cuts]


def _frame_column(g: dict, z0: float, z1: float) -> tuple:
    """A frame's room in plan between two heights, where its modules lie: the packing and its wedge's room."""
    x0, y0, x1, y1 = frame_room(g)
    return (x0, y0, z0, x1, y1, z1)


def frame_solids(res: dict) -> list[dict]:
    """Each floor transit frame as solids at its real depth (I2-34): its body, the 4 mm walls round its room, 60 mm deep
    like its modules, flush with the floor's top face and 30 mm under its underside, or standing 30 mm on the floor
    where its `side` is above; its rim, 8 mm past the walls on the floor's top face; and the C wedge, 84 mm deep, so
    it stands 24 mm proud of the frame's top where it is driven from above."""
    V, fits = res["V"], res["svc"]["fittings"]
    wall, rim = float(fits["frame_wall_mm"]), float(fits["frame_rim_mm"]) - float(fits["frame_wall_mm"])
    out = []
    for gid, g in res["glands"].items():
        if not g.get("cells") or g["at"] != "floor":
            continue
        x0, y0, x1, y1 = frame_room(g)
        z0, z1 = (V["floor_underside_z"], V["floor_underside_z"] + FRAME_DEPTH) if g.get("side") == "above" else (V["floor_z"] - FRAME_DEPTH, V["floor_z"])
        out.append(dict(gland=gid, part="body", box=(x0 - wall, y0 - wall, z0, x1 + wall, y1 + wall, z1)))
        out.append(dict(gland=gid, part="rim", box=(x0 - wall - rim, y0 - wall - rim, V["floor_z"], x1 + wall + rim, y1 + wall + rim, V["floor_z"] + 3)))
        wb = frame_wedge(g)
        if wb:
            out.append(dict(gland=gid, part="C wedge", box=(wb[0], wb[1], z0, wb[2], wb[3], z0 + WEDGE_DEPTH)))
    return out


def _in_box(p, box, tol: float = 0.5) -> bool:
    return all(box[k] - tol <= p[k] <= box[k + 3] + tol for k in range(3))


def _box_gap(a, b) -> float:
    return math.sqrt(sum(max(0.0, b[k] - a[k + 3], a[k] - b[k + 3]) ** 2 for k in range(3)))


def clearance(res: dict) -> dict:
    """SVC-01: each run keeps the rule's clearance from every envelope box and bar member except its own two ends,
    the parts it passes through by design (`passes`), the parts it is clipped to (`along`, touching allowed but not
    entering), the body's panels where it crosses them at one of its glands, and, along the stretches threaded through
    a closed chassis member (`inside`), the parts welded to that member's faces. Hollow carcasses are the cabinets the
    runs pass inside, so they are not obstacles. The keep-clear boxes (aisles, landings, the chair space) are tested
    too, above the floor, up to their own tops or the ceiling's services zone (keep_clear_boxes)."""
    clear = res["data"]["rules"]["clear_mm"]
    solids = _solids(res)
    keep = keep_clear_boxes(res)
    hollow = [b["box"] for b in res["blocks"] if b.get("hollow") and b.get("box")]
    floor_z = res["V"]["floor_z"]
    problems, gaps = [], []
    for run in res["runs"]:
        r = run["od"] / 2
        ends, passes, along = _end_lines(run), _ids(run, "passes") | _ids(run, "inside"), _ids(run, "along")
        # a run threaded through a closed chassis member (`inside`) is walled off from the parts welded to the
        # member's faces wherever it lies within the member, so only those stretches skip them
        members = [m["box"] for m in solids if _matches(m, _ids(run, "inside"))]
        gl = [res["glands"][g]["p"] + (res["glands"][g].get("w", res["glands"][g]["d"]),) for g in _ids(run, "glands")]
        segs = _segs(run["dense"])
        box = _aabb(run["dense"], r + clear)
        for b in solids:
            if not _hit(box, b["box"]) or _matches(b, ends) or _matches(b, passes):
                continue
            lim = 0.0 if _matches(b, along) else clear
            panel = b["id"] in PANELS
            worst = (math.inf, None)
            walled = [m for m in members if _box_gap(m, b["box"]) < 1.0]
            for a, c in segs:
                if not _hit(_aabb((a, c), r + clear), b["box"]):
                    continue
                if walled and any(_in_box(a, m) for m in members) and any(_in_box(c, m) for m in members):
                    continue
                d, p = seg_box(a, c, b["box"])
                if panel and any(math.dist(p, g[:3]) <= g[3] / 2 + r + 80 for g in gl):
                    continue
                if d - r < worst[0]:
                    worst = (d - r, p)
            if worst[1] is None:
                continue
            gaps.append(dict(run=run["id"], part=b["iid"], name=b["name"], gap=round(worst[0], 1), limit=lim, at=[round(v) for v in worst[1]]))
            if worst[0] < lim - 0.05:
                problems.append(f"{run['id']} {'enters' if worst[0] < 0 else 'passes'} {b['iid']} ({b['name'][:40]}) "
                                f"{abs(worst[0]):.0f} mm {'deep' if worst[0] < 0 else 'clear'} at X {worst[1][0]:.0f} Y {worst[1][1]:.0f} Z {worst[1][2]:.0f}")
        for c in res.get("bars", []):
            if _matches(c, ends) or _matches(c, passes):
                continue
            lim = 0.0 if _matches(c, along) else clear
            if min(seg_seg(a, b_, c["p0"], c["p1"]) for a, b_ in segs) - c["r"] - r >= clear + 50:
                continue   # far from the capsule round the member: no closer look needed
            m = _bar_gap(segs, c) - r
            if m < clear + 50:
                gaps.append(dict(run=run["id"], part=c["iid"], name=c["name"], gap=round(m, 1), limit=lim, at=None))
            if m < lim - 0.05:
                problems.append(f"{run['id']} passes the bar {c['iid']} ({c['name'][:40]}) {m:.0f} mm clear")
        own = [res["ns"][key(e)].box for e in ends if key(e) in res["ns"]] + hollow
        for b, kb in keep:
            # a keep-clear box from the floor to the ceiling's services zone: the run's stretches above the floor,
            # outside its own ends' boxes and outside the cabinets (behind their panels), keep the clearance beside
            # it and may run over it in the services zone, so a run may end at an outlet on a cabinet's face
            if not _hit(box, kb):
                continue
            worst = (math.inf, None, clear)
            for a, c in segs:
                if min(a[2], c[2]) < floor_z - 0.5 or any(_in_box(a, o, 1.0) and _in_box(c, o, 1.0) for o in own):
                    continue
                d, p = seg_box(a, c, kb)
                lim = 0.0 if p[2] - r >= kb[5] - 0.5 else clear
                if d - r - lim < worst[0] - worst[2]:
                    worst = (d - r, p, lim)
            if worst[1] is None:
                continue
            gaps.append(dict(run=run["id"], part=b["iid"], name=b["name"], gap=round(worst[0], 1), limit=worst[2], at=[round(v) for v in worst[1]]))
            if worst[0] < worst[2] - 0.05:
                problems.append(f"{run['id']} {'enters' if worst[0] < 0 else 'passes'} the keep-clear {b['iid']} ({b['name'][:40]}) "
                                f"{abs(worst[0]):.0f} mm {'deep' if worst[0] < 0 else 'clear'} at X {worst[1][0]:.0f} Y {worst[1][1]:.0f} Z {worst[1][2]:.0f}")
    # the floor's transit frames at their real depth (I2-34): every run but those through a frame keeps the clearance from
    # its body and its wedge, and no frame enters a part, a bearer strip or another part's box
    frames = frame_solids(res)
    for run in res["runs"]:
        r, own = run["od"] / 2, _ids(run, "glands")
        segs, box = _segs(run["dense"]), _aabb(run["dense"], run["od"] / 2 + clear)
        for f in frames:
            if f["gland"] in own or f["part"] == "rim" or not _hit(box, f["box"]):
                continue
            d, p = min((seg_box(a, c, f["box"]) for a, c in segs), key=lambda t: t[0])
            gaps.append(dict(run=run["id"], part=f"{f['gland']} {f['part']}", name=f"transit frame {f['gland']}", gap=round(d - r, 1), limit=clear,
                             at=[round(v) for v in p]))
            if d - r < clear - 0.05:
                problems.append(f"{run['id']} {'enters' if d < r else 'passes'} {f['gland']}'s {f['part']} {abs(d - r):.0f} mm "
                                f"{'deep' if d < r else 'clear'} at X {p[0]:.0f} Y {p[1]:.0f} Z {p[2]:.0f}")
    parts = [b for b in solids if b["id"] not in PANELS] + bearer_strips(res)
    frame_gaps = []
    for f in (x for x in frames if x["part"] != "rim"):
        for b in parts:
            g = _box_gap(f["box"], b["box"])
            if g > 50:
                continue
            depth = min(min(f["box"][k + 3], b["box"][k + 3]) - max(f["box"][k], b["box"][k]) for k in range(3))
            frame_gaps.append(dict(frame=f"{f['gland']} {f['part']}", part=b["iid"], gap=round(g if g > 0 else -depth, 1)))
            if g <= 0 and depth > 0.05:
                problems.append(f"{f['gland']}'s {f['part']} enters {b['iid']} ({b['name'][:40]}) by {depth:.0f} mm")
    frame_gaps.sort(key=lambda x: x["gap"])
    tested = sorted((g for g in gaps if g["limit"] > 0), key=lambda g: g["gap"])
    return dict(ok=not problems, problems=problems, closest=tested[:10], smallest=tested[0]["gap"] if tested else None, limit=clear,
                frames=frame_gaps[:10])


def keep_clear_boxes(res: dict) -> list:
    """The layout's keep-clear boxes (aisles, landings, the chair space) as SVC-01 tests them: from their own floor to
    their own top, but no higher than the ceiling's services zone, where the cables run in the ceiling's covers over
    the aisles (data/routes.yaml rules.keep_clear)."""
    top = res["V"]["ceiling_z"] - res["data"]["rules"]["keep_clear"]["overhead_mm"]
    return [(b, (*b["box"][:5], min(b["box"][5], top))) for b in res["blocks"] if b.get("keep_clear") and b.get("box")]


def bends(res: dict) -> dict:
    """SVC-02: every corner of a cable or a flexible hose leaves room for its minimum bend radius. A pipe that may
    turn at a fitting (PEX at a push-fit elbow, DWV at a bend) does so where its radius does not fit."""
    problems, worst = [], math.inf
    for run in res["runs"]:
        for c in run["corners"]:
            if c["phi"] < 1e-3 or c.get("elbow"):
                continue
            m = c["r_max"] - run["bend_r"]
            worst = min(worst, m)
            if m < -0.5:
                problems.append(f"{run['id']}: {math.degrees(c['phi']):.0f} degree corner at X {c['at'][0]:.0f} Y {c['at'][1]:.0f} "
                                f"Z {c['at'][2]:.0f} allows {c['r_max']:.0f} mm, the {run['cable']} needs {run['bend_r']:.0f} mm")
    return dict(ok=not problems, problems=problems, margin=None if worst == math.inf else round(worst, 1))


def _seg_list(run: dict, pad: float) -> list:
    return [(a, b, _aabb((a, b), pad)) for a, b in _segs(run["dense"])]


def separation(res: dict) -> dict:
    """SVC-03: every 230 V run keeps the rule's distance from every extra-low-voltage run, in its own bulkhead or
    conduit, except within the rule's reach of the board and of an appliance both runs feed, where they meet at the
    appliance's own terminals, and where the floor panel is between them, a barrier."""
    rule = res["data"]["rules"]
    sep, reach = rule["segregation_mm"], rule["segregation_reach_mm"]
    boxes = {b["id"]: b["box"] for b in res["blocks"] if b.get("box")}
    boxes |= {b["iid"]: b["box"] for b in res["blocks"] if b.get("box")}
    boxes |= {k: f["box"] for k, f in res["fixtures"].items()}
    ac = [r for r in res["runs"] if r["system"] == "ac230"]
    elv = [r for r in res["runs"] if r["system"] in ELV]
    floor = res["V"]["floor_z"]
    zones = [tuple(_eval(v, res["ns"]) for v in z["box"]) for z in rule.get("conduit", [])]
    under = res["V"]["floor_underside_z"]

    def floored(p1, q1, r1, p2, q2, r2):
        # the floor panel between them, a barrier: one segment wholly under its underside, the other wholly in or above it
        lo1, hi1 = min(p1[2], q1[2]) - r1["od"] / 2, max(p1[2], q1[2]) + r1["od"] / 2
        lo2, hi2 = min(p2[2], q2[2]) - r2["od"] / 2, max(p2[2], q2[2]) + r2["od"] / 2
        return (hi1 <= under + 0.5 and lo2 >= under - 0.5) or (hi2 <= under + 0.5 and lo1 >= under - 0.5)

    problems, worst = [], (math.inf, "")
    for a in ac:
        # under the floor, through the floor glands and in the rule's conduit zones every 230 V run is in its own
        # conduit, a separate wiring enclosure, so the distance applies everywhere else
        sa = [s_ for s_ in _seg_list(a, a["od"] / 2 + sep) if not _walled(s_[0], s_[1], floor, zones)]
        for e in elv:
            shared = [boxes[k] for k in ({rule["board"]} | (_end_lines(a) & _end_lines(e))) if k in boxes]
            free = lambda p, q: not any(_pt_box(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2), s) <= reach for s in shared)  # noqa: E731
            m = math.inf
            for p2, q2, bb2 in _seg_list(e, e["od"] / 2):
                if not free(p2, q2):
                    continue
                for p1, q1, bb1 in sa:
                    if _hit(bb1, bb2) and free(p1, q1) and not floored(p1, q1, a, p2, q2, e):
                        m = min(m, seg_seg(p1, q1, p2, q2) - a["od"] / 2 - e["od"] / 2)
            if m < worst[0]:
                worst = (m, f"{a['id']} to {e['id']}")
            if m < sep - 0.05:
                problems.append(f"{a['id']} ({a['feeds'][:32]}) is {m:.0f} mm from {e['id']} ({e['feeds'][:32]})")
    return dict(ok=not problems, problems=problems, limit=sep, governing=worst[1],
                smallest=None if worst[0] == math.inf else round(worst[0], 1))


def terminal_face(res: dict) -> dict:
    """SVC-04: no water, waste or diesel line within the rule's distance of the battery's terminal face (the top of
    the modules, terminals up, AS/NZS 3001.2 clause 5.4.10.2), except the runs the rule names, in their sleeve."""
    rule = res["data"]["rules"]
    tf = rule["terminal_face"]
    b = res["ns"][key(tf["line"])]
    face = (b.x0, b.y0, b.z1, b.x1, b.y1, b.z1)
    problems, rows = [], []
    for run in res["runs"]:
        if run["system"] not in WETS:
            continue
        d = min((seg_box(p, q, face)[0] for p, q in _segs(run["dense"])), default=math.inf) - run["od"] / 2
        exempt = run["id"] in tf["exempt"]
        if d < tf["mm"] + 200:
            rows.append(dict(run=run["id"], feeds=run["feeds"], mm=round(d), sleeved=exempt))
        if d < tf["mm"] and not exempt:
            problems.append(f"{run['id']} ({run['feeds'][:40]}) is {d:.0f} mm from the terminal face")
        if exempt and not run.get("sleeve"):
            problems.append(f"{run['id']} is exempt only in its dielectric sleeve, and has none")
    cone = drip_cone(res)
    problems += cone["problems"]
    rows.sort(key=lambda r: r["mm"])
    return dict(ok=not problems, problems=problems, near=rows, limit=tf["mm"], exempt=tf["exempt"],
                smallest=min((r["mm"] for r in rows if not r["sleeved"]), default=None), cone=cone)


def tray_plane(res: dict) -> tuple:
    """The drip tray's floor height and its footprint (x0, y0, x1, y1), read from the tray line's own box in the layout
    (I2-35), so SVC-04 tests the tray that is modelled."""
    tray = res["data"]["rules"]["terminal_face"]["tray"]
    b = res["ns"][key(tray["line"])]
    return b.z0 + float(tray.get("floor_mm", 0.0)), (b.x0, b.y0, b.x1, b.y1)


def drip_cone(res: dict) -> dict:
    """SVC-04's drip cone (I2-18 c): no water, waste or diesel line over the terminal face inside a cone that widens by
    the rule's ratio as it rises (the trailer parked off level), but where the drip tray lies between the line and the
    face, and the tray covers the cone where it lies, so it catches every drip that would reach the face. The sleeved
    hoses keep their exemption. Each line's depth into the cone is reported."""
    tf = res["data"]["rules"]["terminal_face"]
    b = res["ns"][key(tf["line"])]
    k = float(tf["cone"])
    tray = tf.get("tray")
    tz, tb = tray_plane(res) if tray else (None, None)
    problems, rows = [], []
    if tray:
        spread = (tz - b.z1) * k   # the cone's reach past the face's edges where the tray lies
        short = max(tb[0] - (b.x0 - spread), tb[1] - (b.y0 - spread), (b.x1 + spread) - tb[2], (b.y1 + spread) - tb[3])
        if short > 1e-6:
            problems.append(f"the drip tray {tray['line']} falls {short:.0f} mm short of the cone where it lies")
    for run in res["runs"]:
        if run["system"] not in WETS or run["id"] in tf["exempt"]:
            continue
        r = run["od"] / 2
        worst, bare = None, None   # the deepest point in the cone, and the deepest one the tray does not cover from above
        for p in run["dense"]:
            h = p[2] - r - b.z1
            if h <= 0:
                continue
            reach = h * k + r
            depth = min(p[0] - (b.x0 - reach), (b.x1 + reach) - p[0], p[1] - (b.y0 - reach), (b.y1 + reach) - p[1])
            if depth <= 0:
                continue
            if worst is None or depth > worst[0]:
                worst = (depth, p)
            if (tray is None or p[2] - r <= tz) and (bare is None or depth > bare[0]):
                bare = (depth, p)
        if worst is None:
            continue
        rows.append(dict(run=run["id"], depth=round(worst[0]), at=[round(v) for v in worst[1]], caught=bare is None))
        if bare is not None:
            problems.append(f"{run['id']} ({run['feeds'][:40]}) is {bare[0]:.0f} mm inside the drip cone over the terminal face at "
                            f"X {bare[1][0]:.0f} Y {bare[1][1]:.0f} Z {bare[1][2]:.0f}")
    return dict(ok=not problems, problems=problems, rows=sorted(rows, key=lambda r: -r["depth"]), ratio=k, tray=tray and tray["line"])


def _samples(dense: list, step: float = 25.0) -> list[tuple]:
    """Points along a polyline at most `step` apart, each with its distance along it."""
    out, s = [(tuple(dense[0]), 0.0)], 0.0
    for a, b in zip(dense, dense[1:]):
        ln = math.dist(a, b)
        n = max(1, int(math.ceil(ln / step)))
        for k in range(1, n + 1):
            t = k / n
            out.append(((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t), s + ln * t))
        s += ln
    return out


def supports(res: dict) -> dict:
    """SVC-12 (I2-18 a, I2-36): no cable lies unsupported over more than VSB1 7.1's 600 mm. A point is held inside a
    chassis member the run is threaded through, within the clip's reach of a part in its `along` (inside a cabinet's
    carcass, of the carcass's panels), of a support fixture (`support: true`, the cleats, trays and saddles the design
    adds) or of a cabinet's outer face, inside the board cabinet, a 230 V conduit zone (under the floor, the only hold a
    230 V cable has but its glands), a box it ends at or a part it passes through, a gland or a frame, or beside a held
    cable of a way it shares. The longest stretch between held points is each run's unsupported span."""
    rule = res["data"]["rules"]["supports"]
    clip, top = float(rule["clip_mm"]), float(rule["max_mm"])
    ns, V = res["ns"], res["V"]
    by_id = defaultdict(list)
    for b in res["blocks"]:
        if b.get("box"):
            by_id[b["id"]].append(b["box"])
            by_id[b["iid"]].append(b["box"])
    for k, f in res["fixtures"].items():
        by_id[k].append(f["box"])
    bars = defaultdict(list)
    for c in res.get("bars", []):
        bars[c["id"]].append(c)
        bars[c["iid"]].append(c)
    board = ns[key(res["data"]["rules"]["board"])].box
    zones = [tuple(_eval(v, ns) for v in z["box"]) for z in res["data"]["rules"].get("conduit", [])]
    gl = res["glands"]
    panels = [b["box"] for b in res["blocks"] if b.get("box") and b["id"] in PANELS]
    carcasses = [b["box"] for b in res["blocks"] if b.get("box") and b.get("hollow")]
    holders = [f["box"] for f in res["fixtures"].values() if f.get("support")]

    def reach(p, bx) -> float:
        """How far a point lies from a part's face it could be clipped to: outside a box, its gap to the box, inside a
        cabinet's carcass, its depth to the nearest panel, so a point deep inside a cabinet is held by nothing there."""
        g = _pt_box(p, bx)
        return -g if g < 0 and bx in carcasses else g

    held, pts = {}, {}
    cables = [r for r in res["runs"] if r["system"] in ELECTRICAL]
    for r in cables:
        rad = r["od"] / 2
        inside = [bx for m in _ids(r, "inside") for bx in by_id.get(m, [])]
        along = [bx for m in _ids(r, "along") for bx in by_id.get(m, [])]
        along_bars = [c for m in _ids(r, "along") for c in bars.get(m, [])]
        ends = [bx for e in _end_lines(r) | _ids(r, "passes") for bx in by_id.get(e, []) if bx not in carcasses]
        glands = [gl[g] for g in _ids(r, "glands") if g in gl]
        sm = _samples(r["dense"])
        pts[r["id"]] = sm
        h = []
        for p, _ in sm:
            ok = (any(_in_box(p, bx, 0.5) for bx in inside) or any(reach(p, bx) - rad <= clip for bx in along)
                  or any(_bar_gap([(p, p)], c) - rad <= clip for c in along_bars)
                  or _in_box(p, board, 0.0) or any(_in_box(p, bx, 1.0) for bx in ends)
                  or any(_pt_box(p, bx) - rad <= clip for bx in holders)
                  or any(0 <= _pt_box(p, bx) and _pt_box(p, bx) - rad <= clip for bx in carcasses)
                  or (r["system"] == "ac230" and any(_in_box(p, z, 0.0) for z in zones))
                  or any(any(_in_box(p, pb, 1.0) for pb in panels) and math.dist(p[:2] if g["at"] in ("floor", "roof") else p, g["p"][:2] if g["at"] in ("floor", "roof") else g["p"])
                         <= max(g.get("w", g["d"]), g.get("h", g["d"])) for g in glands))
            h.append(ok)
        held[r["id"]] = h
    for _ in range(3):   # a way's lanes share their clips: a cable beside a held cable of its way is held there too
        for w, v in (res.get("ways") or {}).items():
            ids = [i for i in v["runs"] if i in held]
            for i in ids:
                ri = next(x for x in cables if x["id"] == i)
                for k, (p, _) in enumerate(pts[i]):
                    if held[i][k]:
                        continue
                    for j in ids:
                        if j == i:
                            continue
                        rj = next(x for x in cables if x["id"] == j)
                        if any(held[j][m] and math.dist(p, q) - ri["od"] / 2 - rj["od"] / 2 <= clip for m, (q, _) in enumerate(pts[j])
                               if abs(q[0] - p[0]) < 80 and abs(q[1] - p[1]) < 80 and abs(q[2] - p[2]) < 80):
                            held[i][k] = True
                            break
    problems, rows = [], []
    for r in cables:
        sm, h = pts[r["id"]], held[r["id"]]
        last, worst = 0.0, (0.0, None)
        for (p, s), ok in zip(sm, h):
            if ok:
                if s - last > worst[0]:
                    worst = (s - last, p)
                last = s
        if sm[-1][1] - last > worst[0]:
            worst = (sm[-1][1] - last, sm[-1][0])
        rows.append(dict(run=r["id"], span=round(worst[0]), at=worst[1] and [round(v) for v in worst[1]]))
        if worst[0] > top + 1e-6:
            problems.append(f"{r['id']} lies {worst[0]:.0f} mm unsupported up to X {worst[1][0]:.0f} Y {worst[1][1]:.0f} Z {worst[1][2]:.0f}, {top:g} mm at most")
    rows.sort(key=lambda x: -x["span"])
    return dict(ok=not problems, problems=problems, rows=rows, longest=rows[0]["span"] if rows else None,
                governing=rows[0]["run"] if rows else None, limit=top, margin=round(top - rows[0]["span"], 1) if rows else None)


def heat(res: dict) -> dict:
    """SVC-11 (I2-18 d): every cable keeps its band's distance from each hot line (rules.heat.lines) everywhere, under
    the floor too, and every run of the kinds a hot surface names keeps its distance from it (the Combi's exhaust behind
    it, the floor under its hot base, the oven's case), but the runs that end there. Inside a transit frame both pass,
    each line is in its own module, so that stretch is not measured."""
    rule = res["data"]["rules"]["heat"]
    ns = res["ns"]
    runs = {r["id"]: r for r in res["runs"]}
    floor_z = res["V"]["floor_z"]
    frames = {g: _frame_column(v, floor_z - FRAME_DEPTH, floor_z) for g, v in res["glands"].items() if v.get("cells")}
    problems, rows = [], []
    for hid in rule["lines"]:
        h = runs[hid]
        hs = _seg_list(h, h["od"] / 2)
        hb = _aabb(h["dense"], h["od"] / 2 + max(rule["line_mm"].values()))
        for c in res["runs"]:
            if not band(c) or not _hit(hb, _aabb(c["dense"], c["od"] / 2)):
                continue
            need = float(rule["line_mm"][band(c)])
            common = [frames[g] for g in _ids(h, "glands") & _ids(c, "glands") if g in frames]
            inside = lambda p, q: any(_in_box(p, f, 1.0) and _in_box(q, f, 1.0) for f in common)  # noqa: E731
            m, at = math.inf, None
            for p1, q1, b1 in hs:
                if inside(p1, q1):
                    continue
                for p2, q2, b2 in _seg_list(c, c["od"] / 2):
                    if _hit(_aabb([b1[:3], b1[3:]], need), b2) and not inside(p2, q2):
                        d = seg_seg(p1, q1, p2, q2) - h["od"] / 2 - c["od"] / 2
                        if d < m:
                            m, at = d, p1
            if at is None:
                continue
            rows.append(dict(a=hid, b=c["id"], gap=round(m, 1), need=need))
            if m < need - 0.05:
                problems.append(f"{c['id']} passes {m:.0f} mm from the hot line {hid} at X {at[0]:.0f} Y {at[1]:.0f} Z {at[2]:.0f}, {need:g} mm needed")
    for s in rule["surfaces"]:
        box = tuple(_eval(v, ns) for v in s["box"])
        test = set(s["test"])
        for r in res["runs"]:
            kind = "cable" if band(r) else ("diesel" if r["system"] == "diesel" else ("wet" if r["system"] in WETS else None))
            if kind not in test or _ids(r, "ends") & set(s.get("ends") or []) or _end_lines(r) & set(s.get("ends") or []):
                continue
            if not _hit(_aabb(r["dense"], r["od"] / 2 + s["mm"]), box):
                continue
            within = tuple(_eval(v, ns) for v in s["within"]) if s.get("within") else None
            segs = [(a, b_) for a, b_ in _segs(r["dense"]) if within is None or _in_box(tuple((a[i] + b_[i]) / 2 for i in range(3)), within, 0.0)]
            if not segs:
                continue
            d, p = min((seg_box(a, b_, box) for a, b_ in segs), key=lambda x: x[0])
            d -= r["od"] / 2
            rows.append(dict(a=s["what"][:40], b=r["id"], gap=round(d, 1), need=float(s["mm"])))
            if d < s["mm"] - 0.05:
                problems.append(f"{r['id']} {'enters' if d < 0 else 'passes'} {s['what']} {abs(d):.0f} mm "
                                f"{'deep' if d < 0 else 'clear'} at X {p[0]:.0f} Y {p[1]:.0f} Z {p[2]:.0f}, {s['mm']:g} mm needed")
    tight = sorted(rows, key=lambda r: r["gap"] - r["need"])
    return dict(ok=not problems, problems=problems, closest=tight[:10],
                margin=round(tight[0]["gap"] - tight[0]["need"], 1) if tight else None,
                governing=f"{tight[0]['b']} to {tight[0]['a']}" if tight else None)


def coverage(res: dict) -> dict:
    """SVC-05: every 230 V circuit of data/services.yaml, every load on the 12 V and 24 V buses, every outlet and DC
    point the zones list, and every water outlet has its runs, from its source to the load."""
    svc, data = res["svc"]["electrical"], res["data"]
    runs = res["runs"]
    def feeds_(tag):
        out = []
        for r in runs:
            touched = {f"fixture: {x}" for x in _end_lines(r) | _ids(r, "passes")}
            if tag in (r.get("serves") or []) or tag in touched:
                out.append(r["id"])
        return out
    missing, rows = [], []
    need = [(c["id"], f"230 V circuit {c['id']}, {c['load']}") for c in svc["circuits"]]
    for bus, text in (("12 V", svc["bus_12v"]), ("24 V", svc["bus_24v"])):
        need += [(f"{bus}: {t.strip()}", f"{bus} bus: {t.strip()}") for t in text.split(",")]
    need += [(f"water: {w}", f"Water outlet: {w}") for w in data["water_outlets"]]
    need += [(f"fixture: {f['id']}", f"{f['what']}") for f in data["fixtures"] if f.get("needs_run", True)]
    for tag, what in need:
        got = feeds_(tag)
        rows.append(dict(need=what, runs=got))
        if not got:
            missing.append(what)
    problems = [f"no run serves {m}" for m in missing] + continuity(res)
    return dict(ok=not problems, problems=problems, rows=rows, n=len(need))


def continuity(res: dict) -> list:
    """SVC-05's second half (I2-18 e): the runs that serve a tag join up end to end, one run's end line the next one's,
    and each 230 V circuit's runs reach from a source fixture (`needs_run: false`, the board's AC bar) to the circuit's
    load line or an outlet whose `for` is that line. A run that stops short or starts from the wrong part fails."""
    data = res["data"]
    sources = {f["id"] for f in data["fixtures"] if f.get("needs_run") is False}
    serves_ = defaultdict(set)
    for f in data["fixtures"]:
        if f.get("for"):
            serves_[f["for"]].add(f["id"])
    tagged = defaultdict(list)
    for r in res["runs"]:
        for t in r.get("serves") or []:
            tagged[t].append(r)
    problems = []
    for tag, rs in tagged.items():
        adj = defaultdict(set)
        for r in rs:
            a, b = r["from"]["line"], r["to"]["line"]
            adj[a].add(b)
            adj[b].add(a)
        seen, todo = set(), [next(iter(adj))]
        while todo:
            x = todo.pop()
            if x not in seen:
                seen.add(x)
                todo += list(adj[x] - seen)
        if seen != set(adj):
            problems.append(f"{tag}'s runs do not join up end to end: " +
                            ", ".join(f"{r['id']} {r['from']['line']} to {r['to']['line']}" for r in rs))
    for c in res["svc"]["electrical"]["circuits"]:
        ends = {e for r in tagged.get(c["id"], []) for e in (r["from"]["line"], r["to"]["line"])}
        if not ends:
            continue
        loads = {c["at"]} | serves_[c["at"]]
        if not ends & sources:
            problems.append(f"{c['id']}'s runs start from no source (the board's AC bar)")
        if not ends & loads:
            problems.append(f"{c['id']}'s runs reach neither its load {c['at']} nor an outlet for it")
    return problems


def drops(res: dict) -> dict:
    """SVC-06: every sized circuit's voltage drop at its design current over its routed length within the limit."""
    lim = res["data"]["rules"]
    problems, worst = [], (-math.inf, "")
    for r in res["runs"]:
        if r["vd_pct"] is None:
            continue
        cap = lim["drop_ac_pct"] if r["system"] == "ac230" else lim["drop_pct"]
        if r["vd_pct"] / cap > worst[0]:
            worst = (r["vd_pct"] / cap, f"{r['id']} {r['vd_pct']:.2f} % of {cap:g} %")
        if r["vd_pct"] > cap + 1e-6:
            problems.append(f"{r['id']} drops {r['vd_pct']:.2f} %, over {cap:g} %")
        if r.get("amps") and r.get("rating_a") and r["amps"] > r["rating_a"] + 1e-6:
            problems.append(f"{r['id']} carries {r['amps']:g} A over its {r['rating_a']:.0f} A rating")
    return dict(ok=not problems, problems=problems, governing=worst[1], use=round(worst[0], 3))


def falls(res: dict) -> dict:
    """SVC-07: every gravity waste falls all the way to the grey tank, at least the rule's slope on each level run."""
    slope = res["data"]["rules"]["fall"]
    problems, worst = [], math.inf
    for r in res["runs"]:
        if r["system"] != "waste" or r.get("pumped"):
            continue
        p = r["points"]
        for a, b in zip(p, p[1:]):
            h = math.hypot(b[0] - a[0], b[1] - a[1])
            dz = a[2] - b[2]
            if dz < -0.5:
                problems.append(f"{r['id']} rises {-dz:.0f} mm at X {a[0]:.0f} Y {a[1]:.0f}")
            elif h > 1:
                worst = min(worst, dz / h)
                if dz / h < slope - 1e-6:
                    problems.append(f"{r['id']} falls 1:{h / max(dz, 1e-6):.0f} over {h:.0f} mm, under 1:{1 / slope:.0f}")
    return dict(ok=not problems, problems=problems, slope=None if worst == math.inf else round(worst, 4))


def band(run: dict) -> str | None:
    """A cable's voltage band, ELV or 230 V, for the runs it may touch. Pipes and hoses have none."""
    return "ELV" if run["system"] in ELV else ("ac230" if run["system"] == "ac230" else None)


def _shared_ways(res: dict) -> set:
    """The pairs of runs that share a way, so are lane neighbours there."""
    out = set()
    for w in res.get("ways", {}).values():
        ids = w["runs"]
        out |= {frozenset((a, b)) for i, a in enumerate(ids) for b in ids[i + 1:]}
    return out


def need_mm(a: dict, b: dict, rule: dict, neighbours: set) -> float:
    """SVC-08's least gap between two runs' surfaces: none between cables of one band that share a way (one loom),
    a water, waste, vent or diesel line's own distance from a cable of each band (rule spacing.wet, by the line's
    system), else the rule's gap."""
    sp = rule["spacing"]
    if band(a) and band(a) == band(b) and band(a) in sp["touch"] and frozenset((a["id"], b["id"])) in neighbours:
        return 0.0
    for w, c in ((a, b), (b, a)):
        if w["system"] in WETS and band(c):
            kind = "fresh" if w["id"] in (sp.get("tempered") or []) else w["system"]
            if kind == "waste" and w.get("rigid") and band(c) == "ELV" and sp.get("rigid_waste_elv_gap"):
                return float(sp["gap_mm"])   # a solvent-welded pipe: no joint between the trap and the tank
            return float(max(sp["gap_mm"], (sp["wet"].get(kind) or {}).get(band(c), 0.0)))
    return float(sp["gap_mm"])


def _xy_seg(p, a, b):
    """The point of segment ab nearest p in plan, and the plan distance."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = 0.0 if n < 1e-9 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / n))
    q = (a[0] + dx * t, a[1] + dy * t, a[2] + (b[2] - a[2]) * t)
    if n < 1e-9:   # a vertical leg: its top is what a drip would reach first
        q = (a[0], a[1], max(a[2], b[2]))
    return q, math.hypot(p[0] - q[0], p[1] - q[1])


def _over(wet: dict, ac: dict, reach: float, floor: tuple, zones: list | None = None, step: float = 10.0):
    """Where the wet line passes over the 230 V run within `reach` in plan, the floor not between them: the wet point
    and the cable's point under it, or None. The 230 V's stretches in its own conduit (`zones`, and everywhere under the
    floor) are sealed from a drip, so they are not tested."""
    ra, rw = ac["od"] / 2, wet["od"] / 2
    segs = [(a, b) for a, b in _segs(ac["dense"]) if not _walled(a, b, floor[0], zones or [])]
    box = _aabb(ac["dense"], ra + rw + reach)
    for p0, p1 in _segs(wet["dense"]):
        if not _hit(_aabb((p0, p1), 0.0), (box[0], box[1], -1e9, box[3], box[4], 1e9)):
            continue
        n = max(1, int(math.dist(p0, p1) / step))
        for k in range(n + 1):
            t = k / n
            p = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t)
            for a, b in segs:
                q, d = _xy_seg(p, a, b)
                if d >= ra + rw + reach or p[2] - rw <= q[2] + ra:
                    continue
                if q[2] < floor[1] and p[2] > floor[0]:   # the floor panel is between them
                    continue
                return p, q
    return None


FRAME_DEPTH = 60.0   # a Roxtec RM module's depth, flush with the floor's top face and 30 mm below its underside


def _split_z(pts: list, zs) -> list:
    """The polyline with a point added wherever a segment crosses one of the heights `zs`."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        cuts = sorted(((z - a[2]) / (b[2] - a[2]) for z in zs if (a[2] - z) * (b[2] - z) < 0), key=float)
        for t in cuts:
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t))
        out.append(b)
    return out


def spacing(res: dict) -> dict:
    """SVC-08: every run keeps its own radius plus a gap from every other run, so no two pass through each other and
    each can be clipped on its own. Cables of one band that share a way are one loom and may touch their lane
    neighbours. A water, waste, vent or diesel line keeps its kind's distance from each cable (rule spacing.wet) and
    never passes over a 230 V run within the rule's over_mm in plan, the floor panel aside. The stretches inside a box
    both runs end at are on its terminals, and those inside a transit frame both pass are in their own modules, so
    neither is measured."""
    rule = res["data"]["rules"]
    sp = rule["spacing"]
    neighbours = _shared_ways(res)
    boxes = {b["iid"]: b["box"] for b in res["blocks"] if b.get("box")} | {b["id"]: b["box"] for b in res["blocks"] if b.get("box")}
    boxes |= {k: f["box"] for k, f in res["fixtures"].items()}
    runs = res["runs"]
    floor = (res["V"]["floor_z"], res["V"]["floor_underside_z"])
    # the floor's planes and a frame's foot split each run, so a stretch is wholly under the floor, in a frame or above
    planes = (floor[1], floor[0], floor[0] - FRAME_DEPTH)
    segs = {r["id"]: [(p, q, _aabb((p, q), r["od"] / 2)) for p, q in _segs(_split_z(r["dense"], planes))] for r in runs}
    hull = {r["id"]: _aabb(r["dense"], r["od"] / 2) for r in runs}
    frames = {g: _frame_column(v, floor[0] - FRAME_DEPTH, floor[0]) for g, v in res["glands"].items() if v.get("cells")}
    reach = max([sp["gap_mm"], sp["over_mm"]] + [v for d in sp["wet"].values() for v in (d or {}).values()])
    duct = [boxes[sp["duct"]]] if sp.get("duct") in boxes else []
    problems, rows, n_pairs, overlaps = [], [], 0, 0
    for i, a in enumerate(runs):
        for b in runs[i + 1:]:
            if not _hit(_aabb([hull[a["id"]][:3], hull[a["id"]][3:]], reach), hull[b["id"]]):
                continue
            need = need_mm(a, b, rule, neighbours)
            # a hot line's or a waste's distance from the extra-low-voltage cables holds inside the trailer: under the
            # floor every run is open to the road's spray and a waste's drip falls to the road, so the gap holds there
            under = sp.get("elv_inside_only") and band(a) != "ac230" and band(b) != "ac230" and need > sp["gap_mm"]
            # inside a transit frame both runs pass, each lies in its own sealed module
            common = [boxes[k] for k in _end_lines(a) & _end_lines(b) if k in boxes] + duct + \
                [frames[g] for g in _ids(a, "glands") & _ids(b, "glands") if g in frames]
            inside = lambda p, q: any(_in_box(p, c, 1.0) and _in_box(q, c, 1.0) for c in common)  # noqa: E731
            m, at = math.inf, None
            for p1, q1, b1 in segs[a["id"]]:
                if not _hit(_aabb([b1[:3], b1[3:]], need), hull[b["id"]]) or inside(p1, q1):
                    continue
                for p2, q2, b2 in segs[b["id"]]:
                    if _hit(_aabb([b1[:3], b1[3:]], need), b2) and not inside(p2, q2):
                        d = seg_seg(p1, q1, p2, q2) - a["od"] / 2 - b["od"] / 2
                        if under and max(p1[2], q1[2], p2[2], q2[2]) <= floor[1] + 0.5:
                            d += need - sp["gap_mm"]   # both stretches under the floor: measured against the gap
                        if d < m:
                            m, at = d, p1
            if at is None:
                continue
            n_pairs += 1
            overlaps += m < -0.05
            rows.append(dict(a=a["id"], b=b["id"], gap=round(m, 1), need=need, at=[round(v) for v in at]))
            if m < need - 0.05:
                problems.append(f"{a['id']} and {b['id']} are {'overlapping ' if m < 0 else ''}{abs(m):.0f} mm "
                                f"{'deep' if m < 0 else 'apart'} at X {at[0]:.0f} Y {at[1]:.0f} Z {at[2]:.0f}, {need:g} mm needed")
    wet = [r for r in runs if r["system"] in WETS]
    zones = [tuple(_eval(v, res["ns"]) for v in z["box"]) for z in rule.get("conduit", [])]
    for w in wet:
        for c in (r for r in runs if r["system"] == "ac230"):
            hit = _over(w, c, sp["over_mm"], floor, zones)
            if hit:
                p, q = hit
                problems.append(f"{w['id']} passes over the 230 V run {c['id']} at X {p[0]:.0f} Y {p[1]:.0f}, {p[2] - q[2]:.0f} mm above it")
    tight = sorted(rows, key=lambda r: r["gap"] - r["need"])
    return dict(ok=not problems, problems=problems, closest=tight[:10], pairs=n_pairs, overlaps=overlaps,
                margin=round(tight[0]["gap"] - tight[0]["need"], 1) if tight else None,
                governing=f"{tight[0]['a']} to {tight[0]['b']}" if tight else None, limit=sp["gap_mm"])


def fitting(g: dict, fits: dict) -> dict:
    """A gland's fitting in the plane of its panel (data/services.yaml `fit`, else by its shape): its footprint on the
    inner face and the outer face, each a circle (`r`) or a rectangle's half sizes (`hx`, `hy`) about the gland's
    centre, and whether a nut is turned with a spanner there. A round gland with no `fit` is a cable gland of its
    hole's metric thread, its body above and its locknut below, a gland with `w` and `h` a transit frame bonded into
    the cut-out and compressed from above, so nothing is turned under it."""
    f = dict(g.get("fit") or {})
    kind = f.get("kind") or ("frame" if g.get("w") and g.get("h") else "gland")
    if kind == "gland":
        r = fits["locknut_ac"][int(f.get("thread", g["d"]))] / 2
        return dict(kind=kind, inner=dict(r=r), outer=dict(r=r), turned=True, what=f"M{int(f.get('thread', g['d']))} gland and locknut")
    if kind == "frame":
        rim = float(f.get("rim", fits["frame_rim_mm"]))
        x0, y0, x1, y1 = frame_room(dict(g, p=(0.0, 0.0)))   # the packing space and the wedge's room, about the gland's point
        hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
        wedge = f", C wedge {g['wedge']:g}" if g.get("wedge") else ""
        return dict(kind=kind, inner=dict(hx=hx + rim, hy=hy + rim), outer=dict(hx=hx + fits["frame_wall_mm"], hy=hy + fits["frame_wall_mm"]),
                    off=((x0 + x1) / 2, (y0 + y1) / 2), turned=False, what=f"transit frame {g['w']:g} x {g['h']:g} packing{wedge}, {rim:g} mm rim")
    if kind == "grommet":
        r = g["d"] / 2 + float(f.get("lip", fits["grommet_lip_mm"]))
        return dict(kind=kind, inner=dict(r=r), outer=dict(r=r), turned=False, what=f"grommet, {g['d']:g} mm hole")
    if kind == "plate":
        hx, hy = f["w"] / 2, f["h"] / 2
        return dict(kind=kind, inner=dict(hx=hx, hy=hy), outer=dict(hx=hx, hy=hy), turned=False, what=f"plate {f['w']:g} x {f['h']:g}")
    raise ValueError(f"{g['id']}: fitting kind {kind} is not one of gland, frame, grommet, plate")


def _plane_xy(g: dict, p: tuple) -> tuple:
    """A gland's centre in its panel's own plane: X and Y on the floor and roof, X and Z on a side wall, Y and Z on
    an end wall."""
    return {"floor": (p[0], p[1]), "roof": (p[0], p[1]), "kerb": (p[0], p[2]), "road": (p[0], p[2])}.get(g["at"], (p[1], p[2]))


def _fp_gap(c1, f1: dict, c2, f2: dict) -> float:
    """The least distance between two footprints in one plane, negative where they overlap (by the depth along the
    centre line for two circles, by the smaller axis overlap otherwise)."""
    def rect(c, f):
        if "r" in f:
            return None
        return (c[0] - f["hx"], c[1] - f["hy"], c[0] + f["hx"], c[1] + f["hy"])
    r1, r2 = rect(c1, f1), rect(c2, f2)
    if r1 is None and r2 is None:
        return math.dist(c1, c2) - f1["r"] - f2["r"]
    if r1 is not None and r2 is not None:
        dx = max(r2[0] - r1[2], r1[0] - r2[2])
        dy = max(r2[1] - r1[3], r1[1] - r2[3])
        return math.hypot(max(dx, 0), max(dy, 0)) if (dx > 0 or dy > 0) else max(dx, dy)
    (c, f), rc = ((c1, f1), r2) if r1 is None else ((c2, f2), r1)
    dx = max(rc[0] - c[0], 0.0, c[0] - rc[2])
    dy = max(rc[1] - c[1], 0.0, c[1] - rc[3])
    if dx == dy == 0.0:
        return -min(c[0] - rc[0], rc[2] - c[0], c[1] - rc[1], rc[3] - c[1]) - f["r"]
    return math.hypot(dx, dy) - f["r"]


def glands(res: dict) -> dict:
    """SVC-09: every gland's fitting has room in its panel. Two fittings in one panel keep the fittings' web between
    their footprints on each face, the spanner's room where a nut is turned there, and a floor fitting stands clear of
    the keep-clear boxes and of the parts that stand on the floor (data/services.yaml `fittings`)."""
    svc = res["svc"]
    fits = svc["fittings"]
    pts = res["glands"]
    fit = {g["id"]: fitting(g, fits) for g in svc["glands"]}
    floor_z = res["V"]["floor_z"]
    problems, rows = [], []
    gl = svc["glands"]
    for i, a in enumerate(gl):
        for b in gl[i + 1:]:
            if a["at"] != b["at"]:
                continue
            ca, cb = _plane_xy(a, pts[a["id"]]["p"]), _plane_xy(b, pts[b["id"]]["p"])
            ca = (ca[0] + fit[a["id"]].get("off", (0, 0))[0], ca[1] + fit[a["id"]].get("off", (0, 0))[1])
            cb = (cb[0] + fit[b["id"]].get("off", (0, 0))[0], cb[1] + fit[b["id"]].get("off", (0, 0))[1])
            if math.dist(ca, cb) > 400:
                continue
            for face in ("inner", "outer"):
                need = fits["spanner_mm"] if (fit[a["id"]]["turned"] or fit[b["id"]]["turned"]) else fits["web_mm"]
                gap = _fp_gap(ca, fit[a["id"]][face], cb, fit[b["id"]][face])
                rows.append(dict(a=a["id"], b=b["id"], face=face, gap=round(gap, 1), need=need))
                if gap < need - 0.05:
                    problems.append(f"{a['id']} and {b['id']} leave {gap:.0f} mm between their fittings "
                                    f"{'inside' if face == 'inner' else 'under the floor' if a['at'] == 'floor' else 'outside'}, {need:g} mm needed")
    standing = [s for s in _solids(res) if s["box"][2] <= floor_z + 5 and s["box"][5] > floor_z + 5 and s["id"] not in PANELS]
    for g in (x for x in gl if x["at"] == "floor"):
        c, f = _plane_xy(g, pts[g["id"]]["p"]), fit[g["id"]]["inner"]
        c = (c[0] + fit[g["id"]].get("off", (0, 0))[0], c[1] + fit[g["id"]].get("off", (0, 0))[1])
        under = set(g.get("under") or [])
        flush = bool((g.get("fit") or {}).get("flush"))
        for b, kb in ([] if flush else keep_clear_boxes(res)):
            gap = _fp_gap(c, f, ((kb[0] + kb[3]) / 2, (kb[1] + kb[4]) / 2), dict(hx=(kb[3] - kb[0]) / 2, hy=(kb[4] - kb[1]) / 2))
            rows.append(dict(a=g["id"], b=b["iid"], face="inner", gap=round(gap, 1), need=0.0))
            if gap < -0.05:
                problems.append(f"{g['id']}'s fitting stands {-gap:.0f} mm into the keep-clear {b['iid']} ({b['name'][:40]})")
        for s in standing:
            if _matches(s, under):
                continue
            sb = s["box"]
            gap = _fp_gap(c, f, ((sb[0] + sb[3]) / 2, (sb[1] + sb[4]) / 2), dict(hx=(sb[3] - sb[0]) / 2, hy=(sb[4] - sb[1]) / 2))
            if gap < -0.05:
                problems.append(f"{g['id']}'s fitting is {-gap:.0f} mm under {s['iid']} ({s['name'][:40]}), which stands on the floor")
    tight = sorted((r for r in rows if r["need"] > 0), key=lambda r: r["gap"] - r["need"])
    return dict(ok=not problems, problems=problems, closest=tight[:10], fittings={k: v["what"] for k, v in fit.items()},
                margin=round(tight[0]["gap"] - tight[0]["need"], 1) if tight else None,
                governing=f"{tight[0]['a']} to {tight[0]['b']}" if tight else None, limit=fits["spanner_mm"])


def _lerp(x: float, xs: list, ys: list) -> float:
    """ys over xs (rising) at x, straight between the points and held at the ends."""
    pts = [(float(a), float(b)) for a, b in zip(xs, ys) if b is not None]
    if x > pts[-1][0] + 1e-9 and len(pts) < len(xs):
        raise ValueError(f"no rating at {x:g} mm2 for this method")
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (x - x0) / (x1 - x0) * (y1 - y0)
    return pts[-1][1]


def _table_amps(table: dict, mm2: float) -> float:
    """A cable table's rating at a size, by conductor area between its sizes."""
    xs = sorted(float(k) for k in table)
    return _lerp(mm2, xs, [table[k] for k in sorted(table, key=float)])


def method_factor(rt: dict, method: str, mm2: float) -> float:
    """AS/NZS 3008.1.1's rating for an installation method over its rating in free air, at the cable's size (Prysmian's
    table for two single cores, data/routes.yaml rules.ratings.methods)."""
    m = rt["methods"]
    return _lerp(mm2, m["sizes"], m[method]) / _lerp(mm2, m["sizes"], m["free"])


def ambient_factor(rt: dict, band_: str, t: float) -> float:
    """The ambient factor at t C: Tycab's table for its DC cables (from 30 C), AS/NZS 3008.1.1's for the 230 V cables and
    the 48 V pairs (from 40 C)."""
    if band_ in ("ac230", "as3008"):
        c = rt["ac"]["conductor_c"]
        return math.sqrt((c - t) / (c - 40.0))
    tab = rt["dc"]["ambient"]
    return _lerp(t, sorted(tab), [tab[k] for k in sorted(tab)])


def free_air_amps(rt: dict, run: dict, t: float) -> float | None:
    """A cable's rating in free air at t C: Prysmian's 2C+E unenclosed spaced for the 230 V cables and cords, AS/NZS
    3008.1.1's two single cores by Prysmian's table for the 48 V double-insulated pairs (I2-31), and Tycab's single core
    times its pair factor for the other DC cables."""
    if run["system"] == "ac230":
        return _table_amps(rt["ac"]["amps"], run["size"]) * ambient_factor(rt, "ac230", t)
    if run.get("kind") in (rt.get("pairs") or {}).get("kinds", []):
        m = rt["methods"]
        return _lerp(run["size"], m["sizes"], m["free"]) * ambient_factor(rt, "as3008", t)
    if run["system"] in ("dc48", "dc24", "dc12", "pv"):
        return _table_amps(rt["dc"]["amps"], run["size"]) * rt["dc"]["pair"] * ambient_factor(rt, "dc", t)
    return None


def rating_zone(p, run: dict, ctx: dict) -> str:
    """The zone a point of a run lies in (data/routes.yaml rules.ratings), for its method and the air round it."""
    V = ctx["V"]
    if any(_in_box(p, b, 0.0) for b in ctx["inside"].get(run["id"], [])):
        return "member"
    if any(_in_box(p, b, 0.0) for b in ctx["cores"]):
        return "core"
    if ctx["floor"] is not None and _in_box(p, ctx["floor"], 0.0):
        return "frame" if any(_in_box(p, f, 0.0) for f in ctx["frames"]) else "floor"
    if p[2] < V["floor_underside_z"]:
        return "drawbar" if p[0] < V["body_x0"] else "under"
    if p[0] < V["body_x0"] or p[0] > V["body_x1"] or abs(p[1]) > V["half_bw"] or p[2] > V["roof_top_z"]:
        return "outside"
    for name in ("board", "battery"):
        if ctx[name] is not None and _in_box(p, ctx[name], 0.0):
            return name
    if run["system"] == "ac230" and any(_in_box(p, z, 0.0) for z in ctx["conduit"]):
        return "conduit"
    return "ceiling" if p[2] >= V["ceiling_z"] - ctx["covers"] else "cabin"


def stretches(run: dict, ctx: dict) -> list[dict]:
    """A run cut where its zone changes, the centreline taken every 10 mm so a zone is found inside a long straight too
    (D-06's last 165 mm in the board cabinet): each stretch's zone, method, air and length."""
    rt, out = ctx["rt"], []
    for a, b in _segs([p for p, _ in _samples(run["dense"], 10.0)]):
        z = rating_zone(tuple((a[k] + b[k]) / 2 for k in range(3)), run, ctx)
        if out and out[-1]["zone"] == z:
            out[-1]["mm"] += math.dist(a, b)
        else:
            out.append(dict(zone=z, mm=math.dist(a, b), at=a))
    for s in out:
        zd = rt["zones"][s["zone"]]
        s["method"] = zd.get(run["system"], zd["method"])
        s["crossing"] = s["zone"] in ("core", "floor", "frame") and s["mm"] <= rt["core_max_mm"]
        s["short"] = 1.0
        if s["zone"] in ("core", "floor") and not s["crossing"]:
            s["method"] = "surrounded"
        elif s["zone"] in ("core", "floor"):
            tab = rt["short"]
            s["short"] = _lerp(s["mm"], sorted(tab), [tab[k] for k in sorted(tab)])
        s["ambient"] = float(zd["ambient"])
    return [s for s in out if not (s["zone"] == "frame" and s["crossing"])] or out


def _group_factor(rt: dict, way: str, n: int, dc: bool, zone: str = "") -> float:
    """A group's factor for n loaded circuits: AS/NZS 3008.1.1 Table 22 for a single layer of lanes (under the ceiling
    where the stretch is in the ceiling's covers) and for the 230 V conduits, Tycab's bundling by its loaded cables (two a
    circuit) over the pair's own factor for DC cables bundled."""
    g = rt["groups"]
    if n <= 1:
        return 1.0
    if way in (g.get("layer_ways") or []):
        tab = g["layer_ceiling"] if zone == "ceiling" else g["layer"]
    elif dc:
        b = rt["dc"]["bundle"]
        return b[min(2 * n, len(b)) - 1] / rt["dc"]["pair"]
    else:
        tab = g["bunched"]
    keys = sorted(int(k) for k in tab)
    return float(tab[next((k for k in keys if k >= n), keys[-1])])


def _most_together(ids: set, shed: list, must: str) -> int:
    """The most circuits of a group, `must` among them, that carry their current at once, where the load shedding never
    runs a rule's `stops` circuits with its `when` circuits."""
    rest = sorted(ids - {must})
    shed = [r for r in shed if (set(r["stops"]) | set(r["when"])) & (ids | {must})]
    if not shed:
        return len(rest) + 1
    best = 1
    for mask in range(1 << len(rest)):
        on = {rest[i] for i in range(len(rest)) if mask >> i & 1} | {must}
        if len(on) > best and not any(on & set(r["stops"]) and on & set(r["when"]) for r in shed):
            best = len(on)
    return best


def device_of(run: dict, rt: dict) -> tuple[float | None, float | None, int]:
    """The protective device's rating In from the run's protection text (its first rating in A), or the override in
    rules.ratings.devices, the circuit's own design current Ib and how many circuits the run carries."""
    o = (rt.get("devices") or {}).get(run["id"])
    if o and o.get("in") is not None:
        return float(o["in"]), float(o.get("ib", run.get("amps") or 0.0)), int(o.get("circuits", 1))
    m = re.match(r"\s*(\d+(?:\.\d+)?) A\b", run.get("protection") or "")
    return (float(m.group(1)) if m else None), (float(run["amps"]) if run.get("amps") is not None else None), 1


def ratings(res: dict) -> dict:
    """SVC-10 (I2-15 b): every cable that carries a design current, rated where it lies. Each stretch takes its zone's
    method and air (rules.ratings.zones), the cable's free-air rating (Tycab for DC, Prysmian's 2C+E for 230 V) times the
    ambient's and the method's factors, and times the group's factor in each shared way the run is in, but at a short
    crossing of a panel, where each cable has its own gland or module. The least stretch is the run's Iz. The design
    current Ib must not exceed Iz, and Ib <= In <= Iz against the device that protects the circuit (AS/NZS 3000 clause
    2.5.3). A run with a design current and no device fails, unless its line's `no_device` says why it cannot be
    overloaded (I2-31). A group counts its loaded circuits: not data or control cables, not a circuit at or under 30 %
    of its grouped rating, and the circuits the load shedding never runs together once."""
    rt = res["data"]["rules"]["ratings"]
    blocks = res["blocks"]
    by_id = defaultdict(list)
    for b in blocks:
        if b.get("box"):
            by_id[b["id"]].append(b["box"])
            by_id[b["iid"]].append(b["box"])
    ns = res["ns"]
    board = key(res["data"]["rules"]["board"])
    ctx = dict(V=res["V"], rt=rt, covers=rt["covers_mm"],
               cores=[b["box"] for b in blocks if b.get("box") and b["id"] in PANELS[1:]],
               floor=next((b["box"] for b in blocks if b.get("box") and b["id"] == PANELS[0]), None),
               board=ns[board].box if board in ns else None, battery=ns["EL_02"].box if "EL_02" in ns else None,
               frames=[_frame_column(g, -1e9, 1e9) for g in res["glands"].values() if g.get("cells")],
               conduit=[tuple(_eval(v, ns) for v in z["box"]) for z in res["data"]["rules"].get("conduit", [])],
               inside={r["id"]: [bx for m in _ids(r, "inside") for bx in by_id.get(m, [])] for r in res["runs"]})
    circuits = {c["id"] for c in res["svc"]["electrical"]["circuits"]}

    def circuit(r):
        return r["id"] if r["id"] in circuits else next((t for t in r.get("serves") or [] if t in circuits), r["id"])

    rows = {}
    for r in res["runs"]:
        if r.get("amps") is None or free_air_amps(rt, r, 40.0) is None:
            continue
        inn, ib, n_own = device_of(r, rt)
        parts = [dict(s, amps=free_air_amps(rt, r, s["ambient"]) * method_factor(rt, s["method"], r["size"]) * s["short"])
                 for s in stretches(r, ctx)]
        rows[r["id"]] = dict(run=r["id"], circuit=circuit(r), ib=ib, device=inn, own=n_own, parts=parts, dc=r["system"] != "ac230", ways=[])
    for w, v in res.get("ways", {}).items():
        for i in v["runs"]:
            if i in rows:
                rows[i]["ways"].append(w)
    shed = rt["groups"].get("shed") or []
    runs = {r["id"]: r for r in res["runs"]}
    counted = set(rows)
    for _ in range(12):
        for row in rows.values():
            groups = []
            for w in row["ways"] or [None]:
                members = [rows[i] for i in (res["ways"][w]["runs"] if w else [row["run"]]) if i in rows]
                on = {m["circuit"] for m in members if m["run"] in counted}
                groups.append((w, _most_together(on | {row["circuit"]}, shed, row["circuit"]) + row["own"] - 1))
            best = None
            for s in row["parts"]:
                f, g = 1.0, (None, 1)
                if not s["crossing"]:
                    f, g = min(((_group_factor(rt, w or "", n, row["dc"], s["zone"]), (w, n)) for w, n in groups), key=lambda x: x[0])
                if best is None or s["amps"] * f < best[0]:
                    best = (s["amps"] * f, f, g, s)
            row.update(iz=best[0], factor=best[1], group=best[2], worst=best[3])
        light = {i for i, row in rows.items() if row["ib"] is not None and row["ib"] <= rt["groups"]["light_pct"] / 100 * row["iz"]}
        new = set(rows) - light
        if new == counted:
            break
        counted = new
    problems, out = [], []
    for row in rows.values():
        ib, inn, iz, w = row["ib"], row["device"], row["iz"], row["worst"]
        need = max(ib or 0.0, inn or 0.0)
        out.append(dict(run=row["run"], ib=ib, device=inn, iz=round(iz, 1), margin=round(iz - need, 1), spare=iz - need, zone=w["zone"], method=w["method"],
                        ambient=w["ambient"], group=row["group"], factor=round(row["factor"], 3), counted=row["run"] in counted))
        where = f"{w['method']}, {w['zone']}, {w['ambient']:g} C, {row['group'][1]} circuits" + (f" in {row['group'][0]}" if row["group"][0] else "")
        if ib is not None and ib > iz + 1e-6:
            problems.append(f"{row['run']} carries {ib:g} A over its {iz:.0f} A ({where})")
        if ib is not None and inn is None and not (runs[row["run"]].get("no_device") or (rt.get("devices") or {}).get(row["run"], {}).get("no_device")):
            problems.append(f"{row['run']} carries {ib:g} A with no protective device, and its line gives no reason it cannot be overloaded")
        if inn is not None and ib is not None and ib > inn + 1e-6:
            problems.append(f"{row['run']}'s {inn:g} A device is under its {ib:g} A design current")
        if inn is not None and inn > iz + 1e-6:
            problems.append(f"{row['run']}'s {inn:g} A device is over its {iz:.0f} A rating ({where})")
    out.sort(key=lambda x: x["margin"])
    return dict(ok=not problems, problems=problems, rows=out, margin=out[0]["margin"] if out else None,
                governing=out[0]["run"] if out else None)


MEMBERS = ("RL-", "RS-", "CM-", "OR-", "DB-K", "DB-R")   # the chassis members a run may pass through (`inside`)
FACE_NAMES = {"x0": "front", "x1": "rear", "y0": "kerb side", "y1": "road side", "z0": "bottom", "z1": "top"}
BUSH_MM = 6.0   # (est.) a hole's bush or grommet round the run, added to its outside diameter


def member_holes(res: dict) -> list[dict]:
    """Every hole a run makes in a chassis member's wall: where the run, threaded through the member (`inside`), crosses
    its box's face. Each hole is the run's outside diameter plus a bush across, and as long along the face as the run's
    slant through it makes it (a slot where it passes obliquely), for the structural checks (data/services.yaml holes)."""
    mem = [b for b in res["blocks"] if b.get("box") and b["id"].startswith(MEMBERS)]
    out = []
    for r in res["runs"]:
        inn = _ids(r, "inside")
        pts = r["dense"]
        for b in (m for m in mem if _matches(m, inn)):
            box = b["box"]
            inside = lambda p: all(box[k] + 0.5 < p[k] < box[k + 3] - 0.5 for k in range(3))  # noqa: E731
            for a, c in zip(pts, pts[1:]):
                ia, ic = inside(a), inside(c)
                if ia == ic:
                    continue
                lo, hi = (a, c) if ia else (c, a)
                for _ in range(30):
                    m = tuple((lo[k] + hi[k]) / 2 for k in range(3))
                    lo, hi = (m, hi) if inside(m) else (lo, m)
                p = hi
                gaps = [abs(p[0] - box[0]), abs(p[1] - box[1]), abs(p[2] - box[2]), abs(p[0] - box[3]), abs(p[1] - box[4]), abs(p[2] - box[5])]
                f = gaps.index(min(gaps))
                u, n = _unit(_sub(c, a))
                cos = abs(u[f % 3]) if n > 0 else 1.0
                d = r["od"] + BUSH_MM
                hole = dict(member=b["iid"], face=FACE_NAMES[("x0", "y0", "z0", "x1", "y1", "z1")[f]], run=r["id"],
                            x=round(p[0]), y=round(p[1]), z=round(p[2]), d=round(d), length=round(min(d / max(cos, 0.2), 5 * d)))
                if not any(h["run"] == hole["run"] and h["member"] == hole["member"] and
                           math.dist((h["x"], h["y"], h["z"]), (hole["x"], hole["y"], hole["z"])) < 5 for h in out):
                    out.append(hole)
    return sorted(out, key=lambda h: (h["member"], h["x"], h["run"]))


CHECKS = {"clearance": clearance, "bends": bends, "separation": separation, "terminal_face": terminal_face,
          "coverage": coverage, "drops": drops, "falls": falls, "spacing": spacing, "glands": glands, "ratings": ratings, "heat": heat,
          "supports": supports}


def evaluate(res: dict) -> dict:
    """Every SVC check's result by its kind (data/checks.yaml names the kind in `item`)."""
    return {k: f(res) for k, f in CHECKS.items()}


def totals(res: dict) -> dict:
    """The schedules' totals by group and by the priced line that carries them, against BD-11's allowance."""
    groups: dict[str, dict] = {}
    lines: dict[str, dict] = {}
    for r in res["runs"]:
        g = groups.setdefault(r["group"], dict(length_m=0.0, mass_kg=0.0, aud=0.0, runs=0, fittings=0))
        g["length_m"] += r["length_m"]
        g["mass_kg"] += r["mass_kg"]
        g["aud"] += r["aud"]
        g["runs"] += 1
        g["fittings"] += r["fittings"]
        ln = lines.setdefault(r["priced_in"] or "-", dict(length_m=0.0, mass_kg=0.0, aud=0.0, runs=0))
        ln["length_m"] += r["length_m"]
        ln["mass_kg"] += r["mass_kg"]
        ln["aud"] += r["aud"]
        ln["runs"] += 1
    rnd = lambda d: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items()}  # noqa: E731
    ele = [r for r in res["runs"] if r["system"] in ELECTRICAL]
    pip = [r for r in res["runs"] if r["system"] not in ELECTRICAL]
    tot = lambda rs, k: round(sum(r[k] for r in rs), 2)  # noqa: E731
    return dict(groups={k: rnd(v) for k, v in groups.items()}, lines={k: rnd(v) for k, v in lines.items()},
                electrical=dict(length_m=tot(ele, "length_m"), mass_kg=tot(ele, "mass_kg"), aud=tot(ele, "aud"), runs=len(ele)),
                plumbing=dict(length_m=tot(pip, "length_m"), mass_kg=tot(pip, "mass_kg"), aud=tot(pip, "aud"), runs=len(pip),
                              fittings=sum(r["fittings"] for r in pip)))

"""Every cable and pipe of the home trailer in 3D (H28), from data/routes.yaml on the solved layout.

Each run names its system, what it feeds, its two ends (a line of data/assemblies/trailer.yaml or a fixture of
data/routes.yaml, and a point on that line's envelope box) and its path through the ways: the ceiling bulkheads, the
chase behind the plinth, the under-floor runs along the rails and the glands of data/services.yaml. A path point is
three expressions over the layout's parameters, the envelope boxes (EL_04.x0 for line EL-04's box) and the ways'
constants, and "." repeats the previous point's value. resolve() turns the runs into filleted centrelines at the
cable's or pipe's minimum bend radius, sizes every DC circuit by its current and its voltage drop at the routed length
(report 20's 2 % limit), and adds up the lengths, masses and prices. checks() measures SVC-01 to SVC-06.
"""
from __future__ import annotations

import math
import re
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
        h = g["d"] / 2
        ns[gid] = B((x - h, y - h, z - h, x + h, y + h, z + h))
    for k, v in (data.get("consts") or {}).items():
        ns[k] = _eval(v, ns)
    for f in data.get("fixtures") or []:
        c = [_eval(v, ns) for v in f["at"]]
        s = f.get("size", [40, 40, 40])
        ns[key(f["id"])] = B((c[0] - s[0] / 2, c[1] - s[1] / 2, c[2] - s[2] / 2, c[0] + s[0] / 2, c[1] + s[1] / 2, c[2] + s[2] / 2))
    return ns


def _points(run: dict, ns: dict) -> list[tuple]:
    pts, prev = [], None
    for spec in [run["from"]["at"]] + list(run.get("path") or []) + [run["to"]["at"]]:
        p = [prev[i] if (v == "." and prev) else _eval(v, ns) for i, v in enumerate(spec)]
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


def size_dc(run: dict, length_m: float, kind: dict, limit_pct: float) -> tuple:
    """The smallest size of the run's kind whose drop at the design current over the routed length stays within the
    limit and whose rating carries the current. A run that fixes its size keeps it, and the drop is reported."""
    amps, volts = run["amps"], run["volts"]
    lim = limit_pct / 100 * volts
    order = sorted(s for s in kind["sizes"] if s is not None)
    fixed = float(run["size"]) if run.get("size") is not None else None
    for s in ([fixed] if fixed is not None else order):
        k = kind["sizes"][s]
        vd = k["mv_am"] * amps * length_m / 1000
        if fixed is not None or (vd <= lim and amps <= k["amps"]):
            smaller = [x for x in order if x < s]
            if fixed is not None:
                why = run.get("size_why") or "Report 20's size"
            elif smaller:
                p = smaller[-1]
                kp = kind["sizes"][p]
                vdp = kp["mv_am"] * amps * length_m / 1000
                why = (f"{p:g} mm2 would drop {100 * vdp / volts:.1f} %" if vdp > lim else
                       f"{p:g} mm2 is rated {kp['amps']:.0f} A in the bulkhead")
            else:
                why = f"The smallest size used, {s:g} mm2, for strength"
            return s, vd, why
    s = order[-1]
    k = kind["sizes"][s]
    return s, k["mv_am"] * amps * length_m / 1000, "Largest size listed, still over the limit"


# ------------------------------------------------------------------ the layout's boxes and the glands
def _blocks_of(lay) -> tuple[dict, list]:
    """The parameters and the envelope blocks of a Layout (cad/trailer.py), as plain dicts."""
    bl = [dict(iid=b.iid, id=b.id, name=b.name, system=b.system, box=b.box, hollow=b.hollow, keep_clear=b.keep_clear)
          for b in lay.blocks if b.box is not None]
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
        for w in sorted(set(WAY_RE.findall(str([r["from"]["at"], r.get("path"), r["to"]["at"]])))):
            if w not in out:
                raise KeyError(f"{r['id']} names the way {w}, which data/routes.yaml `ways` does not list")
            out[w].append(r["id"])
    return out


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
    for _ in range(8):
        runs = [_resolve_run(r, ns, K, data["rules"], fixtures, pitch) for r in data["runs"]]
        od = {r["id"]: r["od"] for r in runs}
        new = {w: float(math.ceil(max((od[i] for i in ids), default=0.0) - 1e-6)) for w, ids in members.items()}
        if new == pitch:
            break
        pitch = new
    ways = {w: dict(what=data["ways"][w], runs=ids, pitch_mm=pitch[w]) for w, ids in members.items()}
    return dict(runs=runs, data=data, kinds=K, V=V, blocks=blocks, glands=glands, fixtures=fixtures, svc=svc, ns=ns, bars=bars,
                ways=ways)


def _resolve_run(r: dict, ns: dict, K: dict, rule: dict, fixtures: dict, pitch: dict) -> dict:
    """One run on the layout, with its lane offset in each way it shares."""
    kind = K[r["kind"]]
    for w, p in pitch.items():
        ns[f"L_{w}"] = lane_of(r, w) * p
    pts = _points(r, ns)
    if r["system"] == "waste" and not r.get("pumped"):
        pts = _apply_fall(pts, rule["fall"])
    raw = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) / 1000
    row = dict(r, points=pts, kind_what=kind["what"], group=kind.get("group", r["system"]))
    conductor = any(v["mv_am"] is not None for v in kind["sizes"].values())
    if r.get("amps") is not None and r.get("volts") is not None and conductor:
        size, vd, why = size_dc(r, raw, kind, rule["drop_pct"] if r["system"] != "ac230" else rule["drop_ac_pct"])
    else:
        size = float(r["size"]) if r.get("size") is not None else next(iter(kind["sizes"]))
        vd, why = None, r.get("size_why")
    k = kind["sizes"][size]
    rigid = bool(kind.get("rigid"))
    elbow_r = k["od"] * kind["elbow_r"] if kind.get("elbow_r") else None
    if not rigid:
        pts = smooth_jogs(pts, k["bend_r"])
        row["points"] = pts
    f = fillet(pts, k["bend_r"], elbow_r=elbow_r, rigid=rigid)
    length_m = f["length"] / 1000
    if vd is not None:
        vd = k["mv_am"] * r["amps"] * length_m / 1000
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


# ------------------------------------------------------------------ the checks, SVC-01 to SVC-07
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


def _in_box(p, box, tol: float = 0.5) -> bool:
    return all(box[k] - tol <= p[k] <= box[k + 3] + tol for k in range(3))


def _box_gap(a, b) -> float:
    return math.sqrt(sum(max(0.0, b[k] - a[k + 3], a[k] - b[k + 3]) ** 2 for k in range(3)))


def clearance(res: dict) -> dict:
    """SVC-01: each run keeps the rule's clearance from every envelope box and bar member except its own two ends,
    the parts it passes through by design (`passes`), the parts it is clipped to (`along`, touching allowed but not
    entering), the body's panels where it crosses them at one of its glands, and, along the stretches threaded through
    a closed chassis member (`inside`), the parts welded to that member's faces. Hollow carcasses are the cabinets the
    runs pass inside, so they are not obstacles."""
    clear = res["data"]["rules"]["clear_mm"]
    solids = _solids(res)
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
    tested = sorted((g for g in gaps if g["limit"] > 0), key=lambda g: g["gap"])
    return dict(ok=not problems, problems=problems, closest=tested[:10], smallest=tested[0]["gap"] if tested else None, limit=clear)


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
    appliance's own terminals."""
    rule = res["data"]["rules"]
    sep, reach = rule["segregation_mm"], rule["segregation_reach_mm"]
    boxes = {b["id"]: b["box"] for b in res["blocks"] if b.get("box")}
    boxes |= {b["iid"]: b["box"] for b in res["blocks"] if b.get("box")}
    boxes |= {k: f["box"] for k, f in res["fixtures"].items()}
    ac = [r for r in res["runs"] if r["system"] == "ac230"]
    elv = [r for r in res["runs"] if r["system"] in ELV]
    floor = res["V"]["floor_z"]
    zones = [tuple(_eval(v, res["ns"]) for v in z["box"]) for z in rule.get("conduit", [])]
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2)  # noqa: E731
    walled = lambda p, q: max(p[2], q[2]) <= floor + 1 or any(_pt_box(mid(p, q), z) <= 0 for z in zones)  # noqa: E731
    problems, worst = [], (math.inf, "")
    for a in ac:
        # under the floor, through the floor glands and in the rule's conduit zones every 230 V run is in its own
        # conduit, a separate wiring enclosure, so the distance applies everywhere else
        sa = [s_ for s_ in _seg_list(a, a["od"] / 2 + sep) if not walled(s_[0], s_[1])]
        for e in elv:
            shared = [boxes[k] for k in ({rule["board"]} | (_end_lines(a) & _end_lines(e))) if k in boxes]
            free = lambda p, q: not any(_pt_box(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2), s) <= reach for s in shared)  # noqa: E731
            m = math.inf
            for p2, q2, bb2 in _seg_list(e, e["od"] / 2):
                if not free(p2, q2):
                    continue
                for p1, q1, bb1 in sa:
                    if _hit(bb1, bb2) and free(p1, q1):
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
    rows.sort(key=lambda r: r["mm"])
    return dict(ok=not problems, problems=problems, near=rows, limit=tf["mm"], exempt=tf["exempt"],
                smallest=min((r["mm"] for r in rows if not r["sleeved"]), default=None))


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
    return dict(ok=not missing, problems=[f"no run serves {m}" for m in missing], rows=rows, n=len(need))


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
    the wet lines' distance between a water, waste or diesel line and a 230 V run, else the rule's gap."""
    sp = rule["spacing"]
    if band(a) and band(a) == band(b) and band(a) in sp["touch"] and frozenset((a["id"], b["id"])) in neighbours:
        return 0.0
    wet = {a["system"], b["system"]} & set(WETS)
    if wet and "ac230" in (a["system"], b["system"]):
        return float(sp["wet_ac_mm"])
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


def _over(wet: dict, ac: dict, reach: float, floor: tuple, step: float = 10.0):
    """Where the wet line passes over the 230 V run within `reach` in plan, the floor not between them: the wet point
    and the cable's point under it, or None."""
    ra, rw = ac["od"] / 2, wet["od"] / 2
    segs = _segs(ac["dense"])
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


def spacing(res: dict) -> dict:
    """SVC-08: every run keeps its own radius plus a gap from every other run, so no two pass through each other and
    each can be clipped on its own. Cables of one band that share a way are one loom and may touch their lane
    neighbours. A water, waste or diesel line keeps the wet lines' distance from a 230 V run and never passes over one
    within that distance in plan, the floor panel aside. The stretches inside a box both runs end at are on its
    terminals and are not measured."""
    rule = res["data"]["rules"]
    sp = rule["spacing"]
    neighbours = _shared_ways(res)
    boxes = {b["iid"]: b["box"] for b in res["blocks"] if b.get("box")} | {b["id"]: b["box"] for b in res["blocks"] if b.get("box")}
    boxes |= {k: f["box"] for k, f in res["fixtures"].items()}
    runs = res["runs"]
    segs = {r["id"]: [(p, q, _aabb((p, q), r["od"] / 2)) for p, q in _segs(r["dense"])] for r in runs}
    hull = {r["id"]: _aabb(r["dense"], r["od"] / 2) for r in runs}
    floor = (res["V"]["floor_z"], res["V"]["floor_underside_z"])
    reach = max(sp["gap_mm"], sp["wet_ac_mm"])
    duct = [boxes[sp["duct"]]] if sp.get("duct") in boxes else []
    problems, rows, n_pairs, overlaps = [], [], 0, 0
    for i, a in enumerate(runs):
        for b in runs[i + 1:]:
            if not _hit(_aabb([hull[a["id"]][:3], hull[a["id"]][3:]], reach), hull[b["id"]]):
                continue
            need = need_mm(a, b, rule, neighbours)
            common = [boxes[k] for k in _end_lines(a) & _end_lines(b) if k in boxes] + duct
            inside = lambda p, q: any(_in_box(p, c, 1.0) and _in_box(q, c, 1.0) for c in common)  # noqa: E731
            m, at = math.inf, None
            for p1, q1, b1 in segs[a["id"]]:
                if not _hit(_aabb([b1[:3], b1[3:]], need), hull[b["id"]]) or inside(p1, q1):
                    continue
                for p2, q2, b2 in segs[b["id"]]:
                    if _hit(_aabb([b1[:3], b1[3:]], need), b2) and not inside(p2, q2):
                        d = seg_seg(p1, q1, p2, q2) - a["od"] / 2 - b["od"] / 2
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
    for w in wet:
        for c in (r for r in runs if r["system"] == "ac230"):
            hit = _over(w, c, sp["wet_ac_mm"], floor)
            if hit:
                p, q = hit
                problems.append(f"{w['id']} passes over the 230 V run {c['id']} at X {p[0]:.0f} Y {p[1]:.0f}, {p[2] - q[2]:.0f} mm above it")
    tight = sorted(rows, key=lambda r: r["gap"] - r["need"])
    return dict(ok=not problems, problems=problems, closest=tight[:10], pairs=n_pairs, overlaps=overlaps,
                margin=round(tight[0]["gap"] - tight[0]["need"], 1) if tight else None,
                governing=f"{tight[0]['a']} to {tight[0]['b']}" if tight else None, limit=sp["gap_mm"])


CHECKS = {"clearance": clearance, "bends": bends, "separation": separation, "terminal_face": terminal_face,
          "coverage": coverage, "drops": drops, "falls": falls, "spacing": spacing}


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

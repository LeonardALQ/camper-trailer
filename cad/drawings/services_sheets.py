"""The home trailer's services sheets (TRAILER.md revision J, the H11 set), A3:

CT-601: electrical single-line diagram: the 48 V battery, BMS, Lynx Distributor, MultiPlus-II, solar, converters, the
        ute's charging feed, the 230 V board and its circuits, and the load-shedding order (research report 20).
CT-602: electrical layout: the plinth, board and inverter in plan, the cable routes, glands and outlets, and the cable
        schedule.
CT-611: plumbing schematic: fill, fresh tanks, pump, filters, cold and hot lines, the drains to the grey tank and the dump
        (report 21).
CT-612: plumbing layout: the tanks, the pump cabinet, the drains with their falls, the shower well, fill and dump points.
CT-621: HVAC and ventilation: the split, the heat-recovery pairs, the extract, towing pressurisation, the relief valve,
        the range hood, the Combi's ducts and the modes (report 19).

Positions come from the layout (data/assemblies/trailer.yaml) and the glands from data/services.yaml. Routes between
them are drawn as the design intent: the installer fixes each run at fit-out, inside the bulkheads named here.
"""
from __future__ import annotations

import math
import re
import time

from . import sheet as S
from .home_common import (Proj, arrow_line, body_plan, box, ctx, label_in, short, stamp, textblock, title, tw, wire, wrap,
                          write, wtable)


ELEC_STYLE = {"dc48": "dc", "pv": "pv", "ac230": "ac", "dc24": "bus", "dc12": "bus", "data": "bus", "lamps": "bus"}
PIPE_STYLE = {"fresh": "cold", "hot": "hot", "waste": "drain", "vent": "thin", "diesel": "thin", "refrigerant": "thin"}
_ROUTED: dict = {}


def _routes(lay) -> dict:
    """data/routes.yaml resolved on the sheet's layout by cad/routes.py, once per build (H28)."""
    if id(lay) not in _ROUTED:
        from .. import routes as R
        _ROUTED[id(lay)] = R.resolve(lay)
    return _ROUTED[id(lay)]


def _by_system(rr: dict, styles: dict) -> list[list[str]]:
    from ..routes_model import SYSTEM_STYLE
    tot: dict[str, list] = {}
    for run in rr["runs"]:
        if run["system"] in styles:
            t = tot.setdefault(run["system"], [0, 0.0, 0.0])
            t[0] += 1
            t[1] += run["length_m"]
            t[2] += run["mass_kg"]
    return [[SYSTEM_STYLE[s_][1].upper(), str(v[0]), f"{v[1]:.1f}", f"{v[2]:.2f}"] for s_, v in tot.items()]


def _centre(b):
    bb = b.box
    if bb is None:
        return tuple(b.cog)
    return ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)


def _route(pr, pts, sty, arrow=False):
    q = [pr.p(x, y, 0) for x, y in pts]
    pr.sh.path(q, sty)
    if arrow and len(q) > 1:
        arrow_line(pr.sh, q[-2], q[-1], sty, 1.6)


def _clip_x(pts, x_min):
    """The pieces of a plan polyline at X >= x_min, cut where it crosses that line: the runs that leave the body for the
    drawbar stop at the sheet's frame."""
    pieces, cur = [], []
    for a, b in zip(pts, pts[1:]):
        ina, inb = a[0] >= x_min, b[0] >= x_min
        if ina and not cur:
            cur = [a]
        if ina != inb:
            t = (x_min - a[0]) / (b[0] - a[0])
            q = (x_min, a[1] + t * (b[1] - a[1]))
            if ina:
                pieces.append(cur + [q])
                cur = []
            else:
                cur = [q, b]
        elif inb:
            cur.append(b)
    if len(cur) > 1:
        pieces.append(cur)
    return pieces


def _gland_xy(g, V):
    """A gland's plan position: on its wall's outer face, or where the data puts it on the floor or the roof."""
    return {"kerb": (g.get("x"), -V["half_bw"]), "road": (g.get("x"), V["half_bw"]), "rear": (V["body_x1"], g.get("y")),
            "front": (V["body_x0"], g.get("y"))}.get(g["at"], (g.get("x"), g.get("y")))


def _gland(sh, pr, g, V, size=1.15, label=True, right=False, inset=0.0):
    """A gland from data/services.yaml as a small circle with its id, on its wall, the floor or the roof. `label` False
    where the plan already names it as an opening, `right` puts the id beside the circle, `inset` draws a rear-wall
    gland that far inside the wall's outer face, clear of an opening's id."""
    at = g["at"]
    p = pr.p(*_gland_xy(g, V), 0)
    if at == "rear" and inset:
        p = (p[0] - inset, p[1])
    sh.circle(p[0], p[1], 0.9, "box")
    sh.circle(p[0], p[1], 0.9, "medium")
    if right:
        sh.text(p[0] + 1.4, p[1] - 0.4, g["id"], size, bold=True)
    elif label:
        sh.text(p[0], p[1] + (-2.6 if at == "kerb" else 1.3), g["id"], size, "middle", bold=True)
    return p


def _legend(sh, x, y, items, size=1.3):
    sh.text(x, y, "LEGEND", 1.8, bold=True)
    for i, (sty, t) in enumerate(items):
        yy = y - 3.6 - i * 3.2
        sh.line(x, yy + 0.6, x + 8, yy + 0.6, sty)
        sh.text(x + 9.5, yy, t, size)
    return y - 3.6 - len(items) * 3.2


def _glands_of(run: dict) -> set:
    """The glands a run passes (its `glands`) and the wall glands it starts or ends at (fixtures G2-IN, G3-PO, G1-FL)."""
    ends = {m[1] for m in (re.match(r"(G\d+)-", run[k]["line"]) for k in ("from", "to") if run.get(k)) if m}
    return set(run.get("glands") or []) | ends


def _gland_runs(rr: dict, gid: str, styles: dict) -> str:
    return id_list(run["id"] for run in rr["runs"] if run["system"] in styles and gid in _glands_of(run))


def _tag_legend(sh, x, y, width=74.0, size=1.15) -> float:
    """The run tags' key under a legend: a sample tag, what its codes mean and the four levels. Returns the y below."""
    sh.circle(x + 1.1, y + 0.4, 0.32, "fill")
    sh.line(x + 1.1, y + 0.4, x + 3.4, y + 0.4, "thin")
    sh.text(x + 3.7, y + 1.1, "G20", TAG_SIZE, bold=True)
    sh.text(x + 3.7, y - 0.35, "F/U", TAG_SIZE, bold=True)
    sh.text(x + 3.7 + S.text_mm("F/U", TAG_SIZE, True) + 0.7, y - 0.35, "C1, C2", TAG_SIZE)
    text = ("RUN TAG ON A LEADER: THE GLAND IT MARKS, IF ANY, THEN EACH LEVEL CODE IN BOLD WITH ITS RUNS. AT A RUN'S END THE "
            "CODE IS THE LEVEL THERE. WHERE A RUN RISES OR DROPS IT IS FROM/TO: F/U DROPS FROM THE FLOOR TO UNDER IT. "
            "LEVELS: " + ", ".join(f"{k} {t}" for k, t in LEVELS) + f" (F UP TO {FLOOR_BAND:.0f} mm OVER THE FLOOR, "
            f"C THE LAST {CEILING_BAND:.0f} mm UNDER THE CEILING).")
    yy = y - 3.4
    for part in S.wrap_mm(text, width, size):
        sh.text(x, yy, part, size)
        yy -= size + 0.75
    return yy


# ------------------------------------------------------------------ run tags (I2-17)
# A run's level along its routed centreline, from its height: under the floor, in the floor's own band (the floor
# bulkheads, the kick lanes and the plinth's end slot, up to 200 mm over the floor), in the ceiling's band (the
# bulkheads clipped to the ceiling, the last 200 mm under it), or in a wall, the partition or a cabinet between.
LEVELS = (("C", "CEILING AND ITS BULKHEADS"), ("W", "WALL, PARTITION, CABINET OR BOARD"),
          ("F", "FLOOR: KICK LANES, FLOOR BULKHEADS, PLINTH SLOT"), ("U", "UNDER THE FLOOR"))
FLOOR_BAND, CEILING_BAND = 200.0, 200.0
RISE_MM = 40.0      # a stretch shorter than this in plan is the run rising or dropping from one level to the next
CLUSTER_MM = 150.0  # tags closer than this in plan share one tag
GLAND_MM = 80.0     # a tag this close in plan to a gland its run passes is that gland's tag
TAG_SIZE, TAG_W = 1.0, 31.0


def level(z: float, V: dict) -> str:
    if z < V["floor_underside_z"]:
        return "U"
    if z <= V["floor_z"] + FLOOR_BAND:
        return "F"
    if z >= V["ceiling_z"] - CEILING_BAND:
        return "C"
    return "W"


def _plan_len(pts) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def run_events(run: dict, V: dict) -> list[tuple]:
    """A run's tags as (plan point, code): each end with its level, and every change of level as FROM/TO where the run
    rises or drops. A rise or a drop at an end goes into that end's code (W/F: starts in the board, drops to the floor)."""
    d = run["dense"]
    st: list[list] = []
    for a, b in zip(d, d[1:]):
        lv = level((a[2] + b[2]) / 2, V)
        if st and st[-1][0] == lv:
            st[-1][1].append(b)
        else:
            st.append([lv, [a, b]])
    real: list[list] = []
    for lv, pts in st:
        if _plan_len(pts) < RISE_MM:
            continue
        if real and real[-1][0] == lv:
            real[-1][1] += pts
        else:
            real.append([lv, list(pts)])
    p0, p1 = (d[0][0], d[0][1]), (d[-1][0], d[-1][1])
    l0, l1 = level(d[0][2], V), level(d[-1][2], V)
    if not real:    # a run that only rises or drops: its end tag is the whole change
        return [(p0, l0), (p1, l1 if l1 == l0 else f"{l0}/{l1}")]
    out = [(p0, l0 if real[0][0] == l0 else f"{l0}/{real[0][0]}")]
    for (la, pa), (lb, _) in zip(real, real[1:]):
        out.append(((pa[-1][0], pa[-1][1]), f"{la}/{lb}"))
    out.append((p1, l1 if real[-1][0] == l1 else f"{real[-1][0]}/{l1}"))
    return out


def _natural(rid: str):
    m = re.match(r"([A-Z]+)-?(\d+)([A-Z]*)$", rid)
    return (m[1], int(m[2]), m[3]) if m else (rid, 0, "")


def id_list(ids) -> str:
    """Run ids in order, three or more consecutive ids written as a range (B-04 TO B-06)."""
    ids = sorted(set(ids), key=_natural)
    out, i = [], 0
    while i < len(ids):
        j = i
        while j + 1 < len(ids):
            a, b = _natural(ids[j]), _natural(ids[j + 1])
            if a[0] != b[0] or a[2] or b[2] or b[1] != a[1] + 1:
                break
            j += 1
        out.append(f"{ids[i]} TO {ids[j]}" if j - i >= 2 else ", ".join(ids[i:j + 1]))
        i = j + 1
    return ", ".join(out)


def _merged(codes: list[str]) -> str:
    """One run's codes at one tag, in route order, as one path of levels: W and W/F make W/F."""
    seq: list[str] = []
    for c in codes:
        for lv in c.split("/"):
            if not seq or seq[-1] != lv:
                seq.append(lv)
    return "/".join(seq)


def tag_clusters(runs: list[dict], V: dict, glands: dict, clip_x: float | None = None, clip_header: str = "") -> list[dict]:
    """The runs' tags gathered where they meet. A tag at a gland the run passes is that gland's, anchored on it. The
    rest gather round the densest points first. Tags ahead of clip_x (on the drawbar, off the plan) share one tag at
    the cut. Each cluster: anchor (plan, mm), header, and lines of (code, runs)."""
    ev = []
    for r in runs:
        gl = [(gid, _gland_xy(glands[gid], V)) for gid in r.get("glands") or [] if gid in glands]
        mine = []
        for k, (p, code) in enumerate(run_events(r, V)):
            near = min(((math.dist(p, q), gid) for gid, q in gl if q[0] is not None and q[1] is not None), default=(1e9, None))
            mine.append(dict(p=p, code=code, run=r["id"], k=k, gland=near[1] if near[0] < GLAND_MM else None))
        # a gland the run passes with no change of level there still names it, at the level it passes
        for gid, q in gl:
            if q[0] is None or q[1] is None or any(e["gland"] == gid for e in mine):
                continue
            z = min(r["dense"], key=lambda p: math.dist((p[0], p[1]), q))[2]
            mine.append(dict(p=q, code=level(z, V), run=r["id"], k=0.5, gland=gid))
        ev += mine
    clusters: list[dict] = []
    off = [e for e in ev if clip_x is not None and e["p"][0] < clip_x]
    if off:
        ys = [e["p"][1] for e in off]
        clusters.append(dict(anchor=(clip_x, (min(ys) + max(ys)) / 2), header=clip_header, events=off))
    ev = [e for e in ev if not (clip_x is not None and e["p"][0] < clip_x)]
    by_gland: dict[str, list] = {}
    for e in ev:
        if e["gland"]:
            by_gland.setdefault(e["gland"], []).append(e)
    for gid in sorted(by_gland, key=lambda s_: int(s_[1:])):
        clusters.append(dict(anchor=_gland_xy(glands[gid], V), header=gid, events=by_gland[gid]))
    rest = [e for e in ev if not e["gland"]]
    while rest:
        nb = [[f for f in rest if math.dist(e["p"], f["p"]) < CLUSTER_MM] for e in rest]
        i = max(range(len(rest)), key=lambda i: (len(nb[i]), -rest[i]["p"][0], -rest[i]["p"][1]))
        clusters.append(dict(anchor=rest[i]["p"], header=None, events=nb[i]))
        taken = {id(f) for f in nb[i]}
        rest = [e for e in rest if id(e) not in taken]
    order = {k: i for i, (k, _) in enumerate(LEVELS)}
    for c in clusters:
        per_run: dict[str, list] = {}
        for e in sorted(c["events"], key=lambda e: e["k"]):
            per_run.setdefault(e["run"], []).append(e["code"])
        codes: dict[str, list] = {}
        for rid, cs in per_run.items():
            codes.setdefault(_merged(cs), []).append(rid)
        c["lines"] = [(code, id_list(ids)) for code, ids in
                      sorted(codes.items(), key=lambda kv: (kv[0].count("/"), [order.get(x, 9) for x in kv[0].split("/")]))]
        c["runs"] = sorted(per_run, key=_natural)
    return clusters


def _text_box(t: dict) -> tuple:
    """A free text's rectangle on the sheet (x0, y0, x1, y1), y up, rotation included."""
    s = t["s"]
    w = S.text_mm(t["t"], s, t["bold"])
    x, y = t["x"], S.Sheet.H - t["y"]
    x0 = x if t["anchor"] == "start" else x - w / 2 if t["anchor"] == "middle" else x - w
    pts = [(x0, y - 0.25 * s), (x0 + w, y - 0.25 * s), (x0 + w, y + 0.8 * s), (x0, y + 0.8 * s)]
    if t["rot"]:
        a = math.radians(-t["rot"])
        pts = [(x + (px - x) * math.cos(a) - (py - y) * math.sin(a), y + (px - x) * math.sin(a) + (py - y) * math.cos(a))
               for px, py in pts]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def _overlap(a, b, pad=0.0) -> bool:
    return a[0] - pad < b[2] and b[0] - pad < a[2] and a[1] - pad < b[3] and b[1] - pad < a[3]


def _crosses(p, q, b) -> bool:
    """Liang-Barsky: does the segment p-q enter the box (x0, y0, x1, y1)?"""
    u0, u1 = 0.0, 1.0
    dx, dy = q[0] - p[0], q[1] - p[1]
    for a, c in ((-dx, p[0] - b[0]), (dx, b[2] - p[0]), (-dy, p[1] - b[1]), (dy, b[3] - p[1])):
        if abs(a) < 1e-12:
            if c < 0:
                return False
        elif a < 0:
            u0 = max(u0, c / a)
        else:
            u1 = min(u1, c / a)
        if u0 > u1:
            return False
    return True


class Ink:
    """Every stroked line on the sheet so far, in a 4 mm grid, to count the lines a tag would cover."""
    G = 4.0

    def __init__(self, sh):
        self.segs, self.grid = [], {}
        for p, q, _, _ in S._segments(sh.el)[0]:
            self.add((p[0], S.Sheet.H - p[1]), (q[0], S.Sheet.H - q[1]))

    def add(self, a, b):
        k = len(self.segs)
        self.segs.append((a, b))
        for gx in range(int(min(a[0], b[0]) // self.G), int(max(a[0], b[0]) // self.G) + 1):
            for gy in range(int(min(a[1], b[1]) // self.G), int(max(a[1], b[1]) // self.G) + 1):
                self.grid.setdefault((gx, gy), []).append(k)

    def count(self, b) -> int:
        seen = set()
        for gx in range(int(b[0] // self.G), int(b[2] // self.G) + 1):
            for gy in range(int(b[1] // self.G), int(b[3] // self.G) + 1):
                seen.update(self.grid.get((gx, gy), ()))
        return sum(1 for k in seen if _crosses(*self.segs[k], b))


def _symbols(sh) -> list[tuple]:
    """The boxes of the small circles on the sheet (glands, symbols), which a label must never cover."""
    out = []
    for e in sh.el:
        m = S._CIRCLE.match(e)
        if m and 'stroke="none"' not in m[4] and float(m[3]) <= S.SYMBOL_R:
            cx, cy, r = float(m[1]), S.Sheet.H - float(m[2]), float(m[3])
            out.append((cx - r, cy - r, cx + r, cy + r))
    return out


RINGS = (0.6, 1.5, 2.6, 4.0, 5.6, 7.5, 10.0, 13.0, 16.5, 21.0, 26.0, 32.0, 40.0, 50.0, 62.0)


def place_box(anchor, w, h, regions, blocked, taken, ink: Ink, extra_rings: int = 3):
    """Where a w x h label goes near its anchor (sheet mm): inside one of the regions, clear of every blocked box and
    every label placed before, and over as few drawn lines as it can. Rings outward in 16 directions. Returns the box
    or None."""
    best, best_ring = None, None
    for ri, d in enumerate(RINGS):
        if best_ring is not None and ri > best_ring + extra_rings:
            break
        for k in range(16):
            a = math.pi * k / 8
            ux, uy = math.cos(a), math.sin(a)
            e = abs(ux) * w / 2 + abs(uy) * h / 2
            cx, cy = anchor[0] + ux * (d + e), anchor[1] + uy * (d + e)
            b = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            if not any(b[0] >= r[0] and b[1] >= r[1] and b[2] <= r[2] and b[3] <= r[3] for r in regions):
                continue
            if any(_overlap(b, o, 0.25) for o in blocked) or any(_overlap(b, o, 0.5) for o in taken):
                continue
            score = d + 3.0 * ink.count(b)
            if best is None or score < best[0]:
                best = (score, b)
                if best_ring is None:
                    best_ring = ri
        if best is not None and best[0] <= d:
            break
    return best[1] if best else None


def _tag_lines(header: str | None, rows: list[tuple], size: float) -> tuple[list, float]:
    """A tag's lines as [(x offset, text, bold)], the header first, each code in bold with its runs wrapped after it."""
    lines = [[(0.0, header, True)]] if header else []
    for code, ids in rows:
        wc = S.text_mm(code, size, True) + 0.7
        for i, part in enumerate(S.wrap_mm(ids, TAG_W - wc, size)):
            lines.append(([(0.0, code, True)] if i == 0 else []) + [(wc, part, False)])
    width = max(off + S.text_mm(t, size, b) for ln in lines for off, t, b in ln)
    return lines, width


def draw_tags(sh, pr, clusters: list[dict], regions: list[tuple], spill: tuple | None = None, size: float = TAG_SIZE) -> dict:
    """Each cluster's tag beside its anchor, with a leader and a dot where it points. A tag with no room near its
    anchor becomes a numbered mark there, and its lines go into a list at `spill` (x, y top, width). Returns counts."""
    ink = Ink(sh)
    blocked = [_text_box(t) for t in sh.texts] + _symbols(sh)
    anchors = [pr.p(*c["anchor"]) for c in clusters]
    dots = [(a[0] - 0.9, a[1] - 0.9, a[0] + 0.9, a[1] + 0.9) for a in anchors]
    lh = size * 1.45
    taken: list = []
    spilled: list = []
    built = [_tag_lines(c["header"], c["lines"], size) for c in clusters]
    order = sorted(range(len(clusters)), key=lambda i: -(len(built[i][0]) * built[i][1]))

    def draw(i, b, lines):
        a = anchors[i]
        qx, qy = min(max(a[0], b[0]), b[2]), min(max(a[1], b[1]), b[3])
        if math.hypot(qx - a[0], qy - a[1]) > 0.7:
            sh.line(a[0], a[1], qx, qy, "thin")
            ink.add(a, (qx, qy))
        sh.circle(a[0], a[1], 0.32, "fill")
        for j, ln in enumerate(lines):
            for off, t, bold in ln:
                sh.text(b[0] + 0.2 + off, b[3] - (j + 1) * lh + 0.32 * size, t, size, bold=bold)
        taken.append(b)

    for i in order:
        lines, w = built[i]
        others = [o for j, o in enumerate(dots) if j != i]
        b = place_box(anchors[i], w + 0.4, len(lines) * lh, regions, blocked + others, taken, ink)
        if b is None and spill is not None:
            spilled.append(i)
            continue
        if b is None:
            raise RuntimeError(f"no room for the run tag at {clusters[i]['anchor']}: {clusters[i]['lines']}")
        draw(i, b, lines)
    for n, i in enumerate(spilled, 1):
        mark = f"T{n}"
        others = [o for j, o in enumerate(dots) if j != i]
        b = place_box(anchors[i], S.text_mm(mark, size, True) + 0.4, lh, regions, blocked + others, taken, ink)
        if b is None:
            raise RuntimeError(f"no room for the run tag mark {mark} at {clusters[i]['anchor']}")
        draw(i, b, [[(0.0, mark, True)]])
    y = spill[1] if spill and spilled else None
    if spilled:
        sh.text(spill[0], y, "RUN TAGS THAT DID NOT FIT ON THE PLAN", 1.6, bold=True)
        y -= 3.2
        for n, i in enumerate(spilled, 1):
            c = clusters[i]
            head = f"T{n}" + (f" {c['header']}" if c["header"] else "")
            for code, ids in c["lines"]:
                for part in S.wrap_mm(f"{head}: {code} {ids}", spill[2], 1.2):
                    sh.text(spill[0], y, part, 1.2)
                    y -= 1.9
                    head = "   "
    return dict(tags=len(clusters), spilled=len(spilled), bottom=y)


# ------------------------------------------------------------------ CT-601 electrical single line
def ct601(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    svc, V = C["svc"]["electrical"], C["V"]
    # the main cables' sizes, lengths and drops as routed (data/routes.yaml, H28), so the sheet and the cable schedule agree
    rt = {run["id"]: run for run in _routes(C["day"])["runs"]}
    mm2 = lambda rid: f"{rt[rid]['size']:g} mm2"  # noqa: E731
    sh = S.Sheet()
    S.frame(sh)
    # sources
    box(sh, 24, 262, 84, 280, ["PV ARRAY ON THE FIXED ROOF", "4 x SUNMAN eARC 430 W, 1,720 W", "TWO STRINGS OF TWO PANELS", f"{mm2('D-15')} PV CABLE, {rt['D-15']['length_m']:.2f} AND {rt['D-16']['length_m']:.2f} m (G4)"])
    box(sh, 112, 262, 166, 280, ["THE UTE (CAR BUILD TC01)", "2 x ORION-TR SMART 12/48-8", "ON THE STOCK ALTERNATOR", "48 V TO THE TRAILER WHILE DRIVING"])
    box(sh, 172, 262, 226, 280, ["12-PIN PLUG, AS 4177.5", "LAMPS, BRAKES, BREAKAWAY SWITCH", "TSC POWER FROM THE UTE'S HARNESS", "NOT PART OF THE 48 V SYSTEM"], sty="light")
    box(sh, 172, 238, 226, 256, ["TWO 15 A INLETS (G2): SHORE, AND", "GENERATOR FOR THE TWO EU22i IN PARALLEL", "CHANGEOVER SHORE - OFF - GENERATOR",
                                 "ON GEN: e2 C, D OFF, CERBO IN 3, N-E BOND"])
    # MPPTs
    for x0, n in ((24, 1), (54, 2)):
        box(sh, x0, 238, x0 + 26, 254, [f"MPPT {n}", "SMARTSOLAR 150/35", "DC ISOLATOR"])
        wire(sh, [(x0 + 13, 262), (x0 + 13, 254)], "pv", f"STRING {n}", dx=0.8, dy=-0.6)
        wire(sh, [(x0 + 13, 238), (x0 + 13, 233), (100, 233)], "dc")
        sh.text(x0 + 14, 234.2, f"40 A MIDI, {mm2('D-08')}", 1.15)
    # Lynx Distributor, a vertical bus
    sh.fillrect(96, 150, 110, 236, "light")
    sh.rect(96, 150, 110, 236, "thick")
    sh.text(103.6, 193, "LYNX DISTRIBUTOR, FOUR MEGA POSITIONS", 1.5, "middle", rot=-90, bold=True)
    # battery bank, isolator, BMS
    mods = [196, 188, 180, 172, 164]
    for y in mods:
        box(sh, 24, y, 54, y + 6, ["NG 51.2 V 100 Ah"], size=1.2, bold_first=False)
        wire(sh, [(54, y + 3), (63, y + 3)], "dc")
        sh.rect(57, y + 2.2, 60, y + 3.8, "medium")
    sh.line(63, 167, 63, 201, "thick")
    sh.text(24, 203.6, f"EACH MODULE: 60 A MEGA, {mm2('D-01')}", 1.1)
    sh.rect(22.5, 159.5, 66, 206.5, "phantom")
    textblock(sh, 23, 157, ["SEALED BOX EL-02: 5 MODULES IN PARALLEL, 25.6 kWh", f"EACH 60 A MEGA, {mm2('D-01')}, AT MOST {max(rt[f'D-0{i}']['length_m'] for i in range(1, 6)):.2f} m, SLEEVED",
                            "NEGATIVES ON A NEGATIVE BUSBAR, 6TH WAY D-06'S 200 A", "VENTS G6, G7. HEAT DETECTOR TO THE CERBO GX"], size=1.15, gap=0.6)
    box(sh, 67, 196, 92, 206, ["ISOLATOR", "300 A, 60 V DC"], size=1.2)
    wire(sh, [(63, 201), (67, 201)], "dc")
    sh.rect(64, 200.2, 66, 201.8, "medium")
    box(sh, 24, 210, 92, 230, ["LYNX SMART BMS NG 500 A", "CONTACTOR, SHUNT AND PRE-ALARM", "ATC AND ATD STOP THE CHARGERS AND LOADS FIRST",
                               "AUX 1.1 A FEEDS THE CERBO GX", f"200 A MEGA, {mm2('D-06')}, {rt['D-06']['length_m']:.2f} m FROM THE BUSBAR"])
    wire(sh, [(80, 206), (80, 210)], "dc")
    wire(sh, [(92, 220), (96, 220)], "dc")
    # the ute's feed, the MultiPlus and its AC
    wire(sh, [(139, 262), (139, 226), (110, 226)], "dc")
    textblock(sh, 140, 257, ["GREY ANDERSON SB50 AT", f"THE DRAWBAR, {mm2('D-14')} TWIN,", f"{rt['D-14']['length_m']:.2f} m (G20), 40 A MEGA",
                         "16 A, 32 A AFTER TC02"], size=1.15, gap=0.55)
    box(sh, 148, 196, 226, 230, ["VICTRON MULTIPLUS-II 48/6k5/100-50 230 V", "6.0 kW AT 25 C, 5.7 kW AT 40 C", "AC-IN FROM THE CHANGEOVER THROUGH A 16 A RCBO",
                                 "AC-OUT-1 TO THE 230 V BOARD", "AC-OUT-2 SPARE, LIVE ONLY ON SHORE OR GENERATOR",
                                 "BONDS NEUTRAL TO EARTH WHEN INVERTING"])
    wire(sh, [(199, 238), (199, 230)], "ac")
    sh.rect(197.5, 232.5, 200.5, 235.5, "medium")
    sh.text(202, 233.3, "16 A RCBO", 1.15)
    wire(sh, [(110, 210), (148, 210)], "dc")
    sh.text(112, 211.3, f"200 A MEGA, {mm2('D-07')}", 1.15)
    sh.text(112, 207.4, f"{rt['D-07']['length_m']:.2f} m, {rt['D-07']['vd_v']:.2f} V DROP", 1.15)
    # 230 V board
    wire(sh, [(156, 196), (156, 98)], "ac")
    sh.text(158, 192.5, "230 V BOARD, LABELLED INVERTER-SUPPLIED", 1.3, bold=True)
    sh.text(158, 189.6, "EVERY CIRCUIT A 30 mA RCBO (AS/NZS 3001.2, 4777.1)", 1.15)
    ctl = {"C2": "K2", "C4": "K4", "C5": "S1", "C6": "S1", "C7": "S1"}
    for i, c in enumerate(svc["circuits"]):
        y = 184 - i * 9.0
        wire(sh, [(156, y), (172, y)], "ac")
        sh.rect(159, y - 1.3, 162, y + 1.3, "medium")
        sh.text(160.5, y + 2.0, f"{c['rcbo']} A", 1.05, "middle")
        if c["id"] in ctl:
            sh.circle(167, y, 1.4, "medium")
            sh.text(167, y - 0.45, ctl[c["id"]], 0.95, "middle", bold=True)
        amps = f"{c['amps']:.1f} A" if c["amps"] is not None else "USER"
        sh.text(173.5, y + 0.4, f"{c['id']} {c['load'].upper()}", 1.2, bold=True)
        sh.text(173.5, y - 2.0, f"{amps}. {c['control'].upper()}"[:86], 1.05)
    # converters and the DC buses
    box(sh, 114, 168, 146, 182, ["2 x ORION-TR 48/24-16", "IN PARALLEL, 760 W AT 40 C", f"15 A INPUT FUSE EACH, {mm2('D-10')}"], size=1.15)
    wire(sh, [(110, 175), (114, 175)], "dc")
    box(sh, 114, 120, 146, 162, ["24 V FUSE PANEL"] + [f"40 A, {mm2('D-12')}"] + wrap(svc["bus_24v"].upper(), 30), size=1.1)
    wire(sh, [(130, 168), (130, 162)], "bus")
    box(sh, 24, 132, 58, 146, ["2 x ORION-TR 48/12-30", "IN PARALLEL, 720 W AT 40 C", f"15 A INPUT FUSE EACH, {mm2('D-11')}"], size=1.15)
    wire(sh, [(103, 150), (103, 140), (58, 140)], "dc")
    box(sh, 24, 92, 104, 128, [f"12 V FUSE PANEL, 80 A, {mm2('D-13')}"] + wrap(svc["bus_12v"].upper(), 66) +
        ["THE BREAKAWAY KIT'S BATTERY FLOATS ON THIS BUS"], size=1.1)
    wire(sh, [(41, 132), (41, 128)], "bus")
    box(sh, 114, 92, 146, 116, ["CERBO GX MK2", "GX TOUCH 50 BESIDE D1", "BMS AUX FEED", "HEAT DETECTOR INPUT", "NODE-RED: TOTAL", "POWER RULE"], size=1.1)
    _legend(sh, 24, 84, [("dc", "48 V DC, MAIN CABLES"), ("bus", "12 V AND 24 V BUSES"), ("ac", "230 V AC"), ("pv", "PV STRINGS")])
    S.notes(sh, 70, 84, [
        "DESIGN INTENT FROM REPORT 20. A LICENSED ELECTRICIAN DESIGNS THE FINAL INSTALLATION, CHECKS EVERY CABLE AGAINST "
        "AS/NZS 3008.1.1 AND CERTIFIES THE 230 V WORK AND THE BATTERY (AS/NZS 3001.2:2022).",
        "THE DC SIDE IS TWO-WIRE, WITH NO CHASSIS RETURN. THE MULTIPLUS CASE AND THE DC NEGATIVE BOND TO THE CHASSIS AT ONE "
        "POINT (TO CONFIRM WITH THE ELECTRICIAN). THE CHASSIS AND EVERY EXPOSED METAL PART BOND TO THE PROTECTIVE EARTH.",
        "THE BATTERY FUSES ARE WITHIN 1 m OF THE TERMINALS IN A SLEEVE (5.4.7.2). THE BMS DISCONNECTS ON VOLTAGE, TEMPERATURE "
        "AND CURRENT (5.4.12.3.3). THE CERBO GX SHOWS THE STATE OF CHARGE (5.4.12.3.4).",
        "THE SHEDDING ORDER PROTECTS THE COOKING: THE SHOWER HEATER SHEDS FIRST, AND THE SHOWER THEN RUNS WARM ON BOILER WATER "
        "IN ITS 12 V MODE WHILE THE COMBI REHEATS ON DIESEL.",
    ], size=1.3, width_chars=130)
    # ---- right column: circuits and the shedding order
    yb = title(sh, dwg, reg, "ELECTRICAL SYSTEM 335.9 kg (report 20), IN THE MASS SCHEDULE (TB-11).", "SEE THE PRODUCTS NAMED")
    rows = [[c["id"], c["load"], "user" if c["amps"] is None else f"{c['amps']:.1f}", f"{c['rcbo']}", c["control"]] for c in svc["circuits"]]
    y = wtable(sh, 230, yb - 6, [("CIRCUIT", 14), ("LOAD", 52), ("RUNNING A", 18), ("RCBO A", 14), ("CONTROL", 82)], rows, size=1.25,
               title="230 V CIRCUITS (report 20 section 7)")
    rows = [[s["step"], s["sheds"], s["when"], s["after"]] for s in svc["shedding"]]
    y = wtable(sh, 230, y - 7, [("ORDER", 13), ("WHAT SHEDS", 45), ("WHEN", 54), ("THEN", 68)], rows, size=1.25,
               title="LOAD SHEDDING, IN ORDER")
    S.notes(sh, 230, y - 6, [
        "THE MULTIPLUS-II 48/6k5 STAYS: WITH THE SHOWER HEATER SHED, THE HOB, THE OVEN AND THE SPLIT RUN TOGETHER INSIDE ITS RATING, "
        "SO THE 48/10000 IS NOT NEEDED.",
        "K2, K4 AND S1 ARE CONTACTORS ON THE BOARD, DRIVEN BY CURRENT RELAYS ON C1, C2 AND C4. THE CERBO GX'S TOTAL POWER RULE "
        "WARNS BEFORE THE USER OUTLETS (C3, C9, C10) OVERLOAD THE INVERTER.",
        "RECHARGE ORDER: THE SUN, THEN THE DRIVE (THE UTE'S CHARGERS), THEN THE TWO EU22i (8.4 h FOR A DESIGN HOT DAY WITH THE "
        "HOUSEHOLD RUNNING, 6.3 h WITH THE LOADS OFF).",
    ], size=1.3, width_chars=150)
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-602 electrical layout
def ct602(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V, res, lay = C["V"], C["res"], C["day"]
    svc = C["svc"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    hb, hi = V["half_bw"], V["half_in"]
    pr = Proj(sh, "plan", k, 34.0, 166.0, ref=(V["body_x0"], -hb, 0))
    show = {"EL-02", "LA-02", "LA-14", "LA-11E", "EL-04", "AC-01", "LA-11T", "LA-11B", "LA-07A", "LA-09", "WR-09", "WR-06", "LA-03"}
    g = {x["id"]: x for x in svc["glands"]}
    gids = ("G2", "G3", "G4", "G5", "G6", "G7")
    gp = {i: pr.p(*_gland_xy(g[i], V), 0) for i in gids}
    # every cable as routed in data/routes.yaml by cad/routes.py on this layout, its centreline in plan (H28)
    rr = _routes(lay)
    floor_g = sorted({x for run in rr["runs"] if run["system"] in ELEC_STYLE for x in run.get("glands") or []} - set(gids),
                     key=lambda s_: int(s_[1:]))
    fp = {i: pr.p(*_gland_xy(g[i], V), 0) for i in floor_g}
    rects = body_plan(sh, pr, lay, res, cut=1000.0, show=show, size=1.2, keep=False, swings=False, light=("EL-02", "LA-11E", "EL-04"),
                      nolabel=("EL-02", "LA-03", "LA-11B", "LA-02", "EL-04"), avoid=list(gp.values()) + list(fp.values()))
    f = lambda iid: _centre(lay.find(iid))  # noqa: E731
    bd = lay.find("LA-11E").box
    wa, dr = f("LA-02"), f("LA-14")
    x_cut = V["body_x0"] - 250.0    # the runs to the drawbar stop 250 mm ahead of the body, inside the frame
    cuts = []
    for run in rr["runs"]:
        if run["system"] in ELEC_STYLE:
            for piece in _clip_x([(p[0], p[1]) for p in run["dense"]], x_cut):
                _route(pr, piece, ELEC_STYLE[run["system"]])
                cuts += [e for e in (piece[0], piece[-1]) if e[0] == x_cut]
    if cuts:    # the note runs up the margin ahead of the body, over the cut ends
        t, xs = "TO THE DRAWBAR (CT-102)", pr.p(x_cut, 0, 0)[0]
        top = max(pr.p(x, y, 0)[1] for x, y in cuts)
        sh.text(xs - 0.6, top + 2.5 + tw(t, 1.15) / 2, t, 1.15, "middle", bold=True, rot=-90)
    as_openings = {o["id"] for o in res["openings"]}
    elec = [run for run in rr["runs"] if run["system"] in ELEC_STYLE]
    tags = tag_clusters(elec, V, g, clip_x=x_cut, clip_header="ON THE DRAWBAR (CT-102)")
    tagged = {c["header"] for c in tags}
    for gid in gids:
        _gland(sh, pr, g[gid], V, label=gid not in as_openings and gid not in tagged, right=gid == "G7")
    for gid in floor_g:
        _gland(sh, pr, g[gid], V, size=1.0, label=False)   # the floor glands, unlabelled: the note names them
    r = rects["EL-04"]    # the inverter's name in the larger part of its rectangle clear of the floor glands under it
    ys = sorted(q[1] for q in fp.values() if r[0] - 1 <= q[0] <= r[2] + 1 and r[1] - 1 <= q[1] <= r[3] + 1)
    lo, hi = max(((r[1], ys[0] - 1.5), (ys[-1] + 1.5, r[3])), key=lambda s_: s_[1] - s_[0]) if ys else (r[1], r[3])
    label_in(sh, (r[0], lo, r[2], hi), short(lay.find("EL-04")), 1.2)
    r = rects["LA-02"]    # the washer's name over G6, its floor gland, and the gland's id
    label_in(sh, (r[0], gp["G6"][1] + 2.4, r[2], r[3]), short(lay.find("LA-02")), 1.2)
    # outlets, indicative: one symbol for each outlet in its zone (report 20 section 7)
    outs = [(4350, hi - 25, "2"), (4950, hi - 25, "2"), (V["in_x0"] + 25, -350, "2"), (V["in_x0"] + 25, 350, "2"),
            (3300, -hi + 25, "2"), (wa[0], -hi + 25, "1"), (dr[0], -hi + 25, "1"), (bd[0] + 60, -hi + 25, "1")]
    for x, y, t in outs:
        q = pr.p(x, y)
        sh.fillrect(q[0] - 1.1, q[1] - 1.1, q[0] + 1.1, q[1] + 1.1, "box")
        sh.rect(q[0] - 1.1, q[1] - 1.1, q[0] + 1.1, q[1] + 1.1, "medium")
        sh.text(q[0], q[1] - 0.45, t, 1.0, "middle", bold=True)
    tb = lay.find("EL-09").box   # the drip tray over the plinth, dashed (I2-35)
    t0, t1 = pr.p(tb[0] + 6, tb[1] + 6), pr.p(tb[3] - 6, tb[4] - 6)
    sh.rect(min(t0[0], t1[0]), min(t0[1], t1[1]), max(t0[0], t1[0]), max(t0[1], t1[1]), "phantom")
    for iid, t, dy in (("EL-02", "BATTERY PLINTH", -250), ("LA-11E", "BOARD", 0), ("EL-04", "INVERTER", 0)):
        b = lay.find(iid).box
        if iid == "EL-02":
            q = pr.p((b[0] + lay.find("LA-02").box[3]) / 2, (b[4] + lay.find("LA-02").box[4]) / 2)
            sh.text(q[0], q[1] - 0.5, "PLINTH", 1.15, "middle")
    sh.text(34, 166 + 2 * hb / k + 6.0, "PLAN, FRONT LEFT, ROAD SIDE UP: EQUIPMENT, CABLE ROUTES, GLANDS AND OUTLETS", 2.1, bold=True)
    yl = _legend(sh, 34, 150, [("dc", "48 V MAIN CABLES"), ("ac", "230 V CIRCUITS, OWN BULKHEAD"), ("bus", "12 V AND 24 V BUSES"),
                               ("pv", "PV STRINGS AND THE UTE FEED")])
    sh.fillrect(34, yl - 1.0, 36.2, yl + 1.2, "box")
    sh.rect(34, yl - 1.0, 36.2, yl + 1.2, "medium")
    sh.text(38, yl - 0.4, "OUTLET, 1 SINGLE OR 2 DOUBLE (INDICATIVE POSITION)", 1.3)
    sh.circle(35.1, yl - 4.0, 0.9, "medium")
    sh.text(38, yl - 4.5, "GLAND (data/services.yaml), ITS POSITION, SIZE AND FITTING ON CT-603", 1.3)
    _tag_legend(sh, 34, yl - 8.5)
    used = {x for run in rr["runs"] if run["system"] in ELEC_STYLE for x in _glands_of(run)}
    gr = [[x["id"], x["at"].upper(), _gland_runs(rr, x["id"], ELEC_STYLE) or "-"] for x in svc["glands"]
          if x["id"] in used or x["id"] in gids]
    wtable(sh, 112, 150, [("GLAND", 12), ("AT", 12), ("RUNS THROUGH IT, TAGGED ON THE PLAN", 92)], gr, size=1.15,
           title="ELECTRICAL GLANDS (EACH ONE IN FULL ON CT-603)")
    S.notes(sh, 22, 84, [
        "DATUM DIM-01. EVERY CABLE IS DRAWN AS ROUTED IN data/routes.yaml BY cad/routes.py ON THE SOLVED LAYOUT, ITS CENTRELINE IN "
        "PLAN. ITS LENGTH, SIZE, DROP AND PROTECTION ARE IN THE ELECTRICAL PAGE'S CABLE SCHEDULE, AND IN 3D IN trailer-electrical.",
        "THE DC LEAVES THE BOARD BY THE CEILING BULKHEADS AND BY THE CHASE BEHIND THE PLINTH. UNDER THE FLOOR THE RUNS PASS BETWEEN "
        "THE RAILS, OR INSIDE THEM PAST THE ARM HANGERS, AND UP THE FLOOR GLANDS, EACH TAGGED WITH THE RUNS THROUGH IT. THE 230 V RUNS "
        "IN CONDUIT UNDER THE FLOOR AND IN THE PLINTH'S END SLOT, AND 50 mm FROM EXTRA-LOW VOLTAGE ELSEWHERE (SVC-03, AS/NZS 3000 3.9.8.3).",
        "EVERY RUN IS TAGGED AT BOTH ENDS AND WHERE IT CHANGES LEVEL, SO A RUN IS FOLLOWED BY ITS ID FROM TAG TO TAG. A TAG BY A BUNDLE "
        "NAMES EVERY RUN IN IT.",
        "NO WATER OR DIESEL LINE WITHIN 300 mm OF THE BATTERY'S TERMINAL FACE EXCEPT THE WASHER'S TWO HOSES AND THE TRAY'S DRAIN, "
        "WHICH RUN IN A DIELECTRIC SLEEVE (AS/NZS 3001.2 5.4.10.2).",
        "DRIP TRAY EL-09 (DASHED) ON THE MACHINE BASE'S DECK UNDER THE WASHER AND THE DRYER, OVER THE BATTERY BOX AND THE END SLOT, "
        "30 mm UPSTAND. ITS 25 mm DRAIN W-09 LEAVES THE REAR UPSTAND THROUGH THE PARTITION TO A Y JUNCTION ON THE BASIN'S WASTE.",
        "WIRING SUPPORTED AT LEAST EVERY 600 mm, GROMMETS THROUGH METAL, EVERY PENETRATION THROUGH A SEALED GLAND (VSB1 7.1).",
        "THE GX TOUCH 50 SITS BESIDE THE ENTRY DOOR. LIGHTS: CEILING STRIPS, TWO BED READING LIGHTS, AN IP65 WET ROOM LIGHT AND AN AWNING LIGHT.",
    ], size=1.42, width_chars=185)
    # ---- right column: cable schedule and outlets
    yb = title(sh, dwg, reg, "CABLES AND FITTINGS IN BD-11 AND EL-07 (TB-11).", "CABLE TO AS/NZS 3008.1.1, TINNED COPPER")
    y = wtable(sh, 230, yb - 6, [("SYSTEM", 64), ("RUNS", 20), ("ROUTED LENGTH, m", 50), ("MASS, kg", 46)], _by_system(rr, ELEC_STYLE),
               size=1.25, title="ROUTED CABLES BY SYSTEM (data/routes.yaml, H28)")
    rows = [[o["zone"], o["ac"], o["dc"]] for o in svc["electrical"]["outlets"]]
    y = wtable(sh, 230, y - 7, [("ZONE", 34), ("230 V OUTLETS", 70), ("24 V AND USB POINTS", 76)], rows, size=1.25,
               title="OUTLETS AND DC POINTS BY ZONE (report 20 section 7)")
    yn, _ = S.notes(sh, 230, y - 6, [
        "THE OUTLET SYMBOLS ON THE PLAN SHOW HOW MANY GO IN EACH ZONE. THEIR EXACT POSITIONS ARE SET WITH THE CABINETRY.",
        "THE BATTERY BOX'S TWO VENTS (G6, G7) PASS THROUGH THE FLOOR OUTBOARD OF THE KERB RAIL, AWAY FROM THE COMBI'S COWL ON THE ROAD SIDE.",
    ], size=1.3, width_chars=150)
    # every run tagged at its two ends and wherever it changes level (I2-17), last, so the tags keep clear of the rest
    draw_tags(sh, pr, tags, regions=[(21.5, 150.8, 229.0, 266.0)], spill=(230.0, yn - 4.0, 178.0))
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-603 floor and wall penetrations
THROUGH = {"floor": "FLOOR", "roof": "ROOF", "kerb": "KERB WALL", "road": "ROAD WALL", "rear": "REAR WALL", "front": "FRONT WALL"}
UNDER_FLOOR = ("RL-", "RS-", "CM-", "OR-")   # the chassis members under the floor, drawn hidden under the glands


def _fitting(g: dict) -> str:
    """A gland's fitting as data/services.yaml gives it (`fitting`: a text, or a mapping of its parts), else '-'."""
    f = g.get("fitting")
    if isinstance(f, dict):
        return ", ".join(str(v) if k in ("type", "what") else f"{k.replace('_', ' ')} {v}" for k, v in f.items())
    return str(f) if f else "-"


def _hole(g: dict) -> str:
    return f"{g['w']:g} x {g['h']:g}" if g.get("w") and g.get("h") else f"{g['d']:g}"


def _is_frame(g: dict) -> bool:
    return g["at"] in ("floor", "roof") and bool(g.get("w") and g.get("h")) and (g.get("fit") or {}).get("kind", "frame") == "frame"


def _frame(sh, pr, g: dict, xy, fits: dict, cells: bool = True):
    """A transit frame in plan: its packing space (medium), the rim of its frame (thin) and each run's module (thin)."""
    x, y = xy
    hx, hy = g["w"] / 2, g["h"] / 2
    rim = float((g.get("fit") or {}).get("rim", fits["frame_rim_mm"]))
    sh.rect(*pr.rect3((x - hx - rim, y - hy - rim, 0, x + hx + rim, y + hy + rim, 0)), "thin")
    sh.rect(*pr.rect3((x - hx, y - hy, 0, x + hx, y + hy, 0)), "medium")
    if cells:
        from ..routes import cell_half
        for c in (g.get("cells") or {}).values():
            dx, dy, m = c[:3]
            hx, hy = cell_half(c)   # a pair's two cores, each in its own module
            for k in range(round(max(hx, hy) * 2 / m)):
                x0 = x + dx - hx + (k * m if hx > hy else 0)
                y0 = y + dy - hy + (k * m if hy > hx else 0)
                sh.rect(*pr.rect3((x0, y0, 0, x0 + m, y0 + m, 0)), "thin")


def ct603(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    from .. import routes as R
    C = ctx(prj)
    V, res, lay = C["V"], C["res"], C["day"]
    svc = C["svc"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    hb = V["half_bw"]
    pr = Proj(sh, "plan", k, 34.0, 166.0, ref=(V["body_x0"], -hb, 0))
    g = {x["id"]: x for x in svc["glands"]}
    centre = {gid: v["p"] for gid, v in R.gland_points(V, svc["glands"]).items()}
    rr = _routes(lay)
    every = {**ELEC_STYLE, **PIPE_STYLE}
    show = {"EL-02", "LA-11E", "EL-04", "LA-02", "LA-14", "LA-11T", "LA-11B", "LA-09", "WR-06", "WR-08", "WR-09", "WR-10", "LA-03"}
    body_plan(sh, pr, lay, res, cut=1000.0, show=show, size=1.1, keep=False, swings=False, light=(), open_labels=False,
              nolabel=("WR-10", "LA-11E", "EL-04", "WR-09", "LA-14", "LA-02"))
    # under the floor, dashed: the rails, raisers, crossmembers and outriggers, and the tanks
    for b in lay.blocks:
        if b.box is not None and (b.id.startswith(UNDER_FLOOR) or b.id in ("UF-01", "UF-01R", "UF-08", "UF-06")):
            pr.box(b.box, "hidden")
    for b in lay.blocks:
        if b.box is not None and b.id.startswith("CM-"):
            q = pr.p((b.box[0] + b.box[3]) / 2, -hb - 110)
            sh.text(q[0], q[1], b.id, 1.0, "middle")
    # every gland: a floor or roof gland at its hole's size where it passes, a wall gland on its wall's outer face
    labels = []
    for x in svc["glands"]:
        xy = _gland_xy(x, V)
        q = pr.p(*xy, 0)
        r = max(0.45, x["d"] / 2 / k)
        if _is_frame(x):
            _frame(sh, pr, x, xy, svc["fittings"], cells=False)
        elif x["at"] in ("floor", "roof"):
            sh.circle(q[0], q[1], r, "medium" if x["at"] == "floor" else "hidden")
            sh.line(q[0] - r - 0.4, q[1], q[0] + r + 0.4, q[1], "thin")
            sh.line(q[0], q[1] - r - 0.4, q[0], q[1] + r + 0.4, "thin")
        else:
            sh.circle(q[0], q[1], 0.9, "box")
            sh.circle(q[0], q[1], 0.9, "medium")
        labels.append(dict(anchor=xy, header=x["id"], lines=[]))
    sh.text(34, 166 + 2 * hb / k + 6.0, "PLAN, FRONT LEFT, ROAD SIDE UP: EVERY GLAND. THE CHASSIS AND THE TANKS UNDER THE FLOOR, DASHED",
            2.0, bold=True)
    yl = _legend(sh, 34, 150, [("hidden", "UNDER THE FLOOR: RAILS, RAISERS, CROSSMEMBERS, OUTRIGGERS AND TANKS")])
    for i, (sty, t) in enumerate((("medium", "FLOOR GLAND AT ITS HOLE'S SIZE, CROSSED AT ITS CENTRE"), ("hidden", "ROOF GLAND, DASHED"),
                                  ("box", "WALL GLAND ON ITS WALL'S OUTER FACE"))):
        yy = yl - i * 3.2
        sh.circle(38.0, yy + 0.45, 0.9, sty)
        if sty == "box":
            sh.circle(38.0, yy + 0.45, 0.9, "medium")
        sh.text(43.5, yy, t, 1.3)
    yy = yl - 9.6
    sh.rect(36.2, yy - 0.35, 39.8, yy + 1.25, "thin")
    sh.rect(36.8, yy + 0.05, 39.2, yy + 0.85, "medium")
    sh.text(43.5, yy, "TRANSIT FRAME: ITS PACKING SPACE AND ITS RIM, THE MODULES IN THE DETAILS", 1.3)
    sh.circle(37.7, yl - 12.8 + 0.4, 0.32, "fill")
    sh.line(37.7, yl - 12.8 + 0.4, 40.0, yl - 12.8 + 0.4, "thin")
    sh.text(43.5, yl - 12.8, "A GLAND'S ID, ON A LEADER FROM ITS CENTRE", 1.3)
    yn, _ = S.notes(sh, 22, yl - 19, [
        "DATUM DIM-01: X FROM THE BALL REARWARD, Y FROM THE CENTRELINE WITH THE ROAD SIDE POSITIVE, Z UP FROM THE GROUND. EACH POSITION IS "
        "THE GLAND'S CENTRE IN THE PANEL IT PASSES, FROM data/services.yaml, AND THE RUNS THROUGH IT ARE THOSE data/routes.yaml ROUTES "
        "THROUGH IT (cad/routes.py). A DASH IN X, Y OR Z IS THE PANEL'S OWN PLANE.",
        "THE FLOOR GLANDS ARE SET OUT ON THE FLOOR PANEL FROM THIS SHEET BEFORE THE PANEL IS ORDERED (TRAILER.md OPEN POINT 11). "
        "THE CHASSIS MEMBERS AND THE TANKS UNDER THEM ARE DRAWN DASHED.",
        f"THE DETAILS ENLARGE THE FLOOR GLANDS THAT STAND UNDER {GROUP_MM:.0f} mm APART, CENTRE TO CENTRE, WITH THE SPACES KEPT CLEAR "
        "(PHANTOM), EACH TRANSIT FRAME'S MODULES, AND THE WEB LEFT BETWEEN EACH PAIR OF FITTINGS (SVC-09: 12 mm ROUND A LOCKNUT, 10 mm ELSE).",
        "EVERY PENETRATION PASSES A SEALED GLAND OR FITTING (VSB1 7.1), AND A RUN THROUGH METAL PASSES A GROMMET. THE FITTING COLUMN IS "
        "EACH GLAND'S FITTING IN data/services.yaml.",
        "THE ASSUMPTION BEHIND EACH POSITION IS THE GLAND'S est IN data/services.yaml. CT-602 AND CT-612 TAG THE RUNS AT EACH GLAND.",
    ], size=1.42, width_chars=185)
    # ---- right column: every gland
    yb = title(sh, dwg, reg, "GLANDS IN BD-11, TRANSIT FRAMES IN BD-25 (TB-11).", "SEE THE FITTING COLUMN")
    rows = []
    for x in svc["glands"]:
        p = centre[x["id"]]
        own = {"floor": 2, "roof": 2, "kerb": 1, "road": 1, "rear": 0, "front": 0}[x["at"]]
        xyz = ["-" if i == own else f"{v:,.0f}" for i, v in enumerate(p)]
        fit = _fitting(x) if x.get("fitting") else R.fitting(x, svc["fittings"])["what"]
        rows.append([x["id"], THROUGH[x["at"]], *xyz, _hole(x), fit, _gland_runs(rr, x["id"], every) or "-", x["what"]])
    wtable(sh, 230, yb - 6, [("GLAND", 11), ("THROUGH", 14), ("X", 11), ("Y", 11), ("Z", 11), ("HOLE, mm", 13), ("FITTING", 27),
                             ("RUNS THROUGH IT", 31), ("WHAT PASSES", 51)], rows, size=1.1, gap=0.5,
           title="EVERY GLAND (data/services.yaml, the runs from data/routes.yaml)")
    draw_tags(sh, pr, labels, regions=[(21.5, 151.0, 229.0, 266.0)])
    _gland_details(sh, lay, V, svc["glands"], top=yn - 7.0, fits=svc["fittings"])
    write(sh, dwg)
    return time.time() - t0


GROUP_MM = 150.0   # floor glands closer than this, centre to centre, share an enlarged detail on CT-603


def _floor_groups(glands: list[dict]) -> list[list[dict]]:
    """The floor glands closer than GROUP_MM to a neighbour, gathered into groups of two or more, front to rear."""
    groups: list[list[dict]] = []
    for x in (g for g in glands if g["at"] == "floor"):
        hit = [gr for gr in groups if any(math.dist((x["x"], x["y"]), (y["x"], y["y"])) < GROUP_MM for y in gr)]
        groups = [gr for gr in groups if not any(gr is h for h in hit)] + [[x] + [y for gr in hit for y in gr]]
    return sorted((sorted(gr, key=lambda g: (g["x"], g["y"])) for gr in groups if len(gr) > 1 or any(_is_frame(g) for g in gr)),
                  key=lambda gr: gr[0]["x"])


def _gland_details(sh, lay, V, glands, top: float, x0: float = 24.0, x1: float = 226.0, bottom: float = 13.0, fits: dict | None = None):
    """Each group of close floor glands enlarged: every hole at its size with its centre lines and its id, a transit
    frame as its packing space, rim and modules, the chassis members under the floor dashed, the fit-out's parts that
    stand on the floor thin, the spaces kept clear phantom, and under it the centre distance and the web left between
    each pair's fittings on the floor's top face (SVC-09)."""
    from .. import routes as R
    groups = _floor_groups(glands)
    if not groups:
        return
    margin = 110.0
    wins = []
    for gr in groups:
        xs, ys = [g["x"] for g in gr], [g["y"] for g in gr]
        r = max(max(g["d"], g.get("w") or 0, g.get("h") or 0) for g in gr) / 2
        wins.append((min(xs) - r - margin, min(ys) - r - margin, max(xs) + r + margin, max(ys) + r + margin))
    close = [[(a, b) for ia, a in enumerate(gr) for b in gr[ia + 1:] if math.dist((a["x"], a["y"]), (b["x"], b["y"])) < GROUP_MM]
             for gr in groups]

    def web(a, b):
        fa, fb = R.fitting(a, fits), R.fitting(b, fits)
        return R._fp_gap((a["x"], a["y"]), fa["inner"], (b["x"], b["y"]), fb["inner"])
    texts = [[f"{a['id']} TO {b['id']}: {math.dist((a['x'], a['y']), (b['x'], b['y'])):.0f} mm CENTRES, "
              f"{web(a, b):.0f} mm BETWEEN THEIR FITTINGS" for a, b in c] for c in close]
    for k in (5.0, 10.0):
        rows, cur, used = [], [], 0.0
        for i, w in enumerate(wins):
            dw = max([(w[2] - w[0]) / k] + [S.text_mm(t, 1.15) for t in texts[i]])
            if cur and used + dw > x1 - x0:
                rows.append(cur)
                cur, used = [], 0.0
            cur.append(i)
            used += dw + 8.0
        rows.append(cur)
        heights = [max((wins[i][3] - wins[i][1]) / k + 4.0 + 2.0 * len(close[i]) for i in row) for row in rows]
        if top - bottom >= sum(heights) + 5.0 * len(rows):
            break
    y, n = top, 0
    for row, hgt in zip(rows, heights):
        x = x0
        for i in row:
            n += 1
            w, gr = wins[i], groups[i]
            pr = Proj(sh, "plan", k, x, y - 3.0 - (w[3] - w[1]) / k, ref=(w[0], w[1], 0))
            sx0, sy0 = pr.p(w[0], w[1])
            sx1, sy1 = pr.p(w[2], w[3])
            sh.text(sx0, sy1 + 1.2, f"DETAIL {n}: {', '.join(g['id'] for g in gr)}, 1:{k:g}", 1.4, bold=True)
            for b in lay.blocks:
                if b.box is None:
                    continue
                bx = (max(b.box[0], w[0]), max(b.box[1], w[1]), min(b.box[3], w[2]), min(b.box[4], w[3]))
                if bx[0] >= bx[2] - 0.5 or bx[1] >= bx[3] - 0.5:
                    continue
                under = b.id.startswith(UNDER_FLOOR) or b.box[5] <= V["floor_underside_z"]
                if b.keep_clear or under or b.box[2] <= V["floor_z"] + 5:
                    sh.rect(*pr.rect3((bx[0], bx[1], 0, bx[2], bx[3], 0)), "phantom" if b.keep_clear else "hidden" if under else "thin")
            sh.rect(sx0, sy0, sx1, sy1, "medium")
            for g in gr:
                q = pr.p(g["x"], g["y"])
                r = (max(g.get("w") or 0, g.get("h") or 0) if _is_frame(g) else g["d"]) / 2 / k
                if _is_frame(g):
                    _frame(sh, pr, g, (g["x"], g["y"]), fits)
                else:
                    sh.circle(q[0], q[1], r, "medium")
                sh.line(q[0] - r - 0.8, q[1], q[0] + r + 0.8, q[1], "centre")
                sh.line(q[0], q[1] - r - 0.8, q[0], q[1] + r + 0.8, "centre")
            yy = sy0 - 2.6
            for t in texts[i]:
                sh.text(sx0, yy, t, 1.15)
                yy -= 2.0
            draw_tags(sh, pr, [dict(anchor=(g["x"], g["y"]), header=g["id"], lines=[]) for g in gr],
                      regions=[(sx0 + 0.3, sy0 + 0.3, sx1 - 0.3, sy1 - 0.3)], size=1.2)
            x = max([sx1] + [sx0 + S.text_mm(t, 1.15) for t in texts[i]]) + 8.0
        y -= hgt + 5.0


# ------------------------------------------------------------------ CT-611 plumbing schematic
def ct611(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V = C["V"]
    sh = S.Sheet()
    S.frame(sh)
    # fill chain
    box(sh, 24, 256, 86, 280, ["THE SOURCE", "A TOWN WATER HOSE, OR CREEK OR BORE", "WATER THROUGH A COARSE STRAINER AND", "THE 12 V TRANSFER PUMP (2 bar OR MORE)",
                               "BORE: TDS UNDER 1,000 mg/L"])
    box(sh, 24, 228, 86, 246, ["PURETEC CR45 ON THE HOSE", "TWIN STAGE, 1 MICRON NOMINAL", "0 TO 20 L/min (WS-02)"])
    box(sh, 24, 200, 86, 218, ["FILL G1, KERB WALL, LOCKABLE CAP", "AFTER AN UNKNOWN SOURCE: CHLORINE", "TO ABOUT 5 mg/L, 30 min CONTACT"])
    wire(sh, [(55, 256), (55, 246)], "cold", arrow=True)
    wire(sh, [(55, 228), (55, 218)], "cold", arrow=True)
    # tanks
    box(sh, 98, 250, 152, 270, ["FRESH TANK, FRONT BAY (UF-01)", "6 mm HDPE, BAFFLED, ABOUT 220 L", "VENTED TO THE ROAD SIDE"])
    box(sh, 98, 222, 152, 242, ["FRESH TANK, REAR BAY (UF-01R)", "6 mm HDPE, BAFFLED", "VENTED TO THE ROAD SIDE"])
    wire(sh, [(86, 209), (92, 209), (92, 260), (98, 260)], "cold", arrow=True)
    wire(sh, [(92, 232), (98, 232)], "cold", arrow=True)
    sh.text(99, 246.2, f"420 L NET. AT MOST {V['water_travel_l']:.0f} L IN TRAVEL (H13)", 1.15)
    # tank outlets to the pump chain
    wire(sh, [(152, 256), (157, 256), (157, 215), (125, 215), (125, 212)], "cold")
    wire(sh, [(125, 222), (125, 212)], "cold", arrow=True)
    sh.text(158.5, 236, "OUTLETS JOINED", 1.15, rot=-90)
    box(sh, 98, 202, 152, 212, ["40-MESH STRAINER"], size=1.25)
    box(sh, 98, 182, 152, 198, ["SHURFLO TRAIL KING 7, 12 V", "7 L/min, 2.1 bar CUT-OUT", "IN THE SINK CABINET (WS-01)"])
    box(sh, 98, 164, 152, 176, ["ACCUMULATOR ABOUT 0.75 L", "PRE-CHARGE 0.2 bar BELOW CUT-IN"], size=1.2)
    wire(sh, [(125, 202), (125, 198)], "cold", arrow=True)
    wire(sh, [(125, 182), (125, 176)], "cold", arrow=True)
    wire(sh, [(125, 164), (125, 158), (164, 158), (164, 276)], "cold")
    # cold branches
    for y, t in ((272, "SINK, COLD"), (266, "BASIN, COLD"), (260, "WASHER, 0.1 TO 0.6 MPa"), (254, "TOILET FLUSH, THETFORD C223-CS"),
                 (248, "DAUERSHOWER BYPASS MIXER AND HAND SHOWER"), (242, "RINSE BOX COLD, NON-RETURN VALVE")):
        wire(sh, [(164, y), (171, y)], "cold", arrow=True)
        sh.text(172.5, y - 0.5, t, 1.2)
    wire(sh, [(164, 230), (171, 230)], "cold", arrow=True)
    box(sh, 172, 224, 226, 236, ["DRINKING WATER", "PURETEC CR-Z2, THEN ACUVA", "ARROWMAX 2.0 UV-LED, OWN TAP"], size=1.15)
    wire(sh, [(164, 210), (172, 210)], "cold", arrow=True)
    box(sh, 172, 198, 226, 218, ["TRUMA COMBI D 6 E (LA-03)", "10 L BOILER, DIESEL OR ELEMENT", "AT MOST 2.8 bar FROM THE PUMP,", "4.5 bar IN THE SYSTEM"], size=1.2)
    # hot
    wire(sh, [(199, 198), (199, 190), (176, 190), (176, 176)], "hot")
    wire(sh, [(176, 186), (183, 186)], "hot", arrow=True)
    sh.text(184.5, 185.5, "DAUERSHOWER HOT INLET", 1.2)
    sh.text(184.5, 183.0, "(ITS 12 V TOP-UP MODE)", 1.1)
    wire(sh, [(176, 176), (183, 176)], "hot", arrow=True)
    box(sh, 183, 170, 226, 180, ["MIXING VALVE AT 50 C"], size=1.2)
    for i, t in enumerate(("SINK, HOT", "BASIN, HOT", "RINSE BOX HOT, NON-RETURN VALVE")):
        y = 166 - i * 6
        wire(sh, [(204, 170), (204, y), (209, y)] if i == 0 else [(204, y + 6), (204, y), (209, y)], "hot", arrow=True)
        sh.text(210.5, y - 0.5, t, 1.15)
    # drains
    sh.text(24, 148, "DRAINS, ALL BY GRAVITY TO THE GREY TANK", 2.1, bold=True)
    fx = [(24, 54, ["SHOWER ZONE", "OWN DRAIN, 12 mm", "HOSE TO THE UNIT"]), (58, 90, ["WET ROOM FLOOR", "WASTE AND THE", "SAND GRATE (WR-02)"]),
          (94, 116, ["BASIN", "(WR-08)"]), (120, 150, ["SINK, IN THE", "BENCH KICK SPACE"]), (154, 190, ["WASHER PUMP", "AND DRYER", "CONDENSATE"]),
          (194, 226, ["SPLIT", "CONDENSATE", "(AC-01)"])]
    traps = ["SWITCHING UNIT IN THE WELL (WR-10), THEN A MEMBRANE TRAP", "MEMBRANE TRAP", "TRAP", "MEMBRANE TRAP, 1:50 FALL",
             "1:50 FALL, BEHIND THE PLINTH", "TRAP, TO THE FLOOR WASTE"]
    for (x0, x1, lines), t in zip(fx, traps):
        box(sh, x0, 126, x1, 140, lines, size=1.15)
        xc = (x0 + x1) / 2
        if t.startswith("TRAP, TO THE FLOOR"):
            wire(sh, [(xc, 140), (xc, 143), (74, 143), (74, 140)], "drain", arrow=True)
            sh.text(xc - 1, 144.0, "TRAP, THEN TO THE FLOOR WASTE", 1.1, "end")
            continue
        wire(sh, [(xc, 126), (xc, 96)], "drain", arrow=True)
        for i, ln in enumerate(wrap(t, 22)):
            sh.text(xc + 1.0, 112 - i * 2.0, ln, 1.05)
    wire(sh, [(39, 96), (172, 96)], "drain")
    gt = C["day"].find("UF-08").box
    box(sh, 40, 66, 172, 92, ["GREY TANK UF-08, 130 L NET, WELDED 6 mm HDPE, ONE BAFFLE", f"BETWEEN THE RAILS IN THE REAR BAY, TOP AT Z {gt[5]:.0f}",
                              "UNDER EVERY WET ROOM DRAIN, SO EVERY DRAIN FALLS TO IT", "VENTED TO THE ROAD SIDE",
                              "EMPTY FOR TRAVEL. A FULL TANK IS CASES TC7 AND TC8"], size=1.25)
    wire(sh, [(106, 96), (106, 92)], "drain", arrow=True)
    wire(sh, [(172, 79), (180, 79)], "drain", arrow=True)
    box(sh, 180, 70, 226, 88, ["LEVER VALVE AND CAMLOCK", "ON THE KERB SIDE", "TO A DUMP POINT, OR THE", "40 L GREY TOTE (WR-11)"], size=1.2)
    box(sh, 180, 46, 226, 62, ["TOILET: THETFORD C223-CS", "CASSETTE OUT THROUGH S1,", "EMPTIED AT A DUMP POINT,", "TWO SPARES (WR-07)"], size=1.15, sty="light")
    _legend(sh, 24, 58, [("cold", "COLD WATER"), ("hot", "HOT WATER"), ("drain", "DRAIN, FALLING TO THE GREY TANK")])
    S.notes(sh, 70, 58, [
        "THE PUMP CUTS OUT AT 2.1 bar BECAUSE THE COMBI TAKES AT MOST 2.8 bar FROM IT. NO REDUCING VALVE IS NEEDED.",
        "DRINK ONLY THROUGH THE CR-Z2 AND THE UV-LED TAP. THE CR45 IS NOT FOR UNSAFE WATER WITHOUT THE CHLORINE DOSE.",
        "THE SHOWER ZONE DRAINS ONLY TO THE DAUERSHOWER, SO ITS LOOP NEVER CARRIES WATER FROM ROUND THE TOILET.",
    ], size=1.25, width_chars=88)
    # ---- right column
    yb = title(sh, dwg, reg, "PLUMBING IN BD-11, WS-01, WS-02 AND THE WET ROOM LINES (TB-11).", "FOOD-GRADE LINES, 6 mm HDPE TANKS")
    lay = C["day"]
    rows = []
    for iid, what in (("UF-01", "Fresh tank, front bay"), ("UF-01R", "Fresh tank, rear bay"), ("WS-01", "Pump, accumulator, strainer, CR-Z2, UV, mixing valve"),
                      ("WS-02", "CR45 fill filter, transfer pump and hose"), ("LA-03", "Combi D 6 E, the boiler"), ("LA-07B", "Sink"),
                      ("WR-08", "Basin, mixer and traps"), ("WR-09", "DauerShower 2.0"), ("WR-10", "Shower well"), ("WR-01", "Wet room tray, falls 1:60"),
                      ("WR-05", "Rinse box"), ("LA-02", "Washer"), ("UF-08", "Grey tank"), ("WR-11", "Grey tote"), ("WR-06", "Cassette toilet")):
        b = lay.find(iid)
        c = b.cog or _centre(b)
        rows.append([iid, what, f"X {c[0]:,.0f}, Y {c[1]:+,.0f}, Z {c[2]:,.0f}", f"{b.mass_kg:.1f}"])
    y = wtable(sh, 230, yb - 6, [("LINE", 16), ("WHAT", 80), ("CENTRE, mm", 62), ("kg", 22)], rows, size=1.22,
               title="THE PARTS ON THIS SHEET (data/assemblies/trailer.yaml)")
    S.notes(sh, 230, y - 6, [
        f"TRAVEL LIMIT (H13): AT MOST {V['water_travel_l']:.0f} L OF FRESH AND GREY WATER WHILE TOWING (CT-003).",
        "THE WASHER'S HOSES ARE THE ONLY WATER LINES WITHIN 300 mm OF THE BATTERY'S TERMINAL FACE. THEY RUN IN A DIELECTRIC SLEEVE.",
        "FILL-TEST THE WET ROOM TRAY TO ITS LIP FOR 24 h BEFORE FIT-OUT (WR-01). EVERY LINE THROUGH THE FLOOR PASSES A SEALED GLAND.",
        "PRESSURE LIMITS: COMBI 2.8 bar FROM THE PUMP AND 4.5 bar IN THE SYSTEM, DAUERSHOWER UP TO 5 bar, WASHER 0.1 TO 0.6 MPa (report 21).",
    ], size=1.3, width_chars=150)
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-612 plumbing layout
def ct612(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V, res, lay = C["V"], C["res"], C["day"]
    svc = C["svc"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    hb, hi = V["half_bw"], V["half_in"]
    pr = Proj(sh, "plan", k, 34.0, 166.0, ref=(V["body_x0"], -hb, 0))
    show = {"LA-07B", "WR-08", "LA-02", "LA-14", "WR-06", "LA-03", "LA-11B", "LA-11T", "EL-02", "WR-09", "WR-10", "WR-11", "UF-01", "UF-01R",
            "UF-08", "UF-06"}
    body_plan(sh, pr, lay, res, cut=1000.0, show=show, size=1.2, keep=False, swings=False, light=("UF-01", "UF-01R", "UF-08"),
              hidden=("UF-01", "UF-01R", "UF-08", "UF-06", "WR-10"), nolabel=("LA-11B", "LA-11T", "EL-02", "LA-14", "UF-01", "UF-01R", "UF-08"))
    g = {x["id"]: x for x in svc["glands"]}
    ws = lay.find("WS-01").cog
    # every pipe and hose as routed in data/routes.yaml by cad/routes.py on this layout, its centreline in plan (H28)
    rr = _routes(lay)
    for run in rr["runs"]:
        if run["system"] in PIPE_STYLE:
            _route(pr, [(p[0], p[1]) for p in run["dense"]], PIPE_STYLE[run["system"]])
    gt = lay.find("UF-08").box
    wet = [run for run in rr["runs"] if run["system"] in PIPE_STYLE]
    tags = tag_clusters(wet, V, g)
    tagged = {c["header"] for c in tags}
    for gid in sorted({x for run in rr["runs"] if run["system"] in PIPE_STYLE for x in run.get("glands") or []} | {"G1"},
                      key=lambda s_: int(s_[1:])):
        _gland(sh, pr, g[gid], V, label=gid not in ("G5", "G26") and gid not in tagged,   # G5 and G26 sit beside other labels
               inset=1.4 if gid in ("G5", "G26") else 0.0)
    q = pr.p(gt[0] + 450, gt[1])
    sh.path([(q[0] - 1.2, q[1]), (q[0] + 1.2, q[1]), (q[0], q[1] - 1.8)], "fill", closed=True)
    q2 = pr.p(gt[0] + 450, -hb - 330)
    sh.line(q[0], q[1] - 1.8, q2[0], q2[1] + 1.2, "thin")
    sh.text(q2[0], q2[1] - 0.4, "DUMP UNDER THE FLOOR: LEVER VALVE AND CAMLOCK, KERB SIDE", 1.1, "middle")
    q = pr.p(ws[0], ws[1])
    sh.circle(q[0], q[1], 1.0, "fill")
    sh.text(q[0] - 1.4, q[1] - 2.2, "PUMP (WS-01)", 1.1, "end")
    for iid, t in (("UF-01", "FRESH TANK UF-01"), ("UF-01R", "FRESH TANK UF-01R"), ("UF-08", "GREY TANK UF-08")):
        b = lay.find(iid).box
        q = pr.p((b[0] + b[3]) / 2, b[1] + 70)
        sh.text(q[0], q[1], t, 1.15, "middle")
    sh.text(34, 166 + 2 * hb / k + 6.0, "PLAN, FRONT LEFT, ROAD SIDE UP: THE WATER PATHS. TANKS AND THE WELL UNDER THE FLOOR, DASHED", 2.0, bold=True)
    # ---- kerb-side section along the centreline through the tanks, the well and the grey tank, 1:20
    x0, x1 = V["axle_x"] - 1000, V["body_x1"]
    ve = Proj(sh, "kerb", 20, 40.0, 98.0, ref=(x0, 0, 450.0))
    ve.fill((x0, 0, V["floor_underside_z"], x1, 0, V["floor_z"]), "shade")
    ve.box((x0, 0, V["rail_underside_z"], x1, 0, V["rail_top_z"]), "thin")
    for iid in ("UF-01", "UF-01R", "UF-08"):
        b = lay.find(iid).box
        r = ve.fill(b, "light")
        sh.rect(*r, "medium")
        label_in(sh, r, "GREY TANK" if iid == "UF-08" else "FRESH", 1.2, 1.0)
    w = lay.find("WR-10").box
    ve.box(w, "medium")
    wt = lay.find("WR-01").box
    ve.fill((wt[0], 0, V["floor_z"], wt[3], 0, wt[5]), "light")
    for b in lay.blocks:          # the crossmembers cut by the centreline, at their own heights
        if b.id.startswith("CM-") and b.box is not None and x0 <= b.box[0] <= x1:
            ve.fill(b.box, "fill")
    a, b_ = ve.p(w[0] - 40, 0, gt[5]), ve.p(w[0] - 40, 0, w[2])
    S.vdim(sh, a[0], a[1], b_[0], b_[1], a[0], f"{w[2] - gt[5]:.0f}", size=1.15, ext=False)
    a, b_ = ve.p(gt[3] - 60, 0, gt[5]), ve.p(gt[3] - 60, 0, V["floor_underside_z"])
    S.vdim(sh, a[0], a[1], b_[0], b_[1], a[0] - 3.0, f"{V['floor_underside_z'] - gt[5]:.0f}", size=1.15, ext=False)
    p = ve.p(g["G13"]["x"], 0, V["floor_z"])
    arrow_line(sh, (p[0], p[1] + 9), (p[0], ve.p(0, 0, gt[5])[1]), "drain", 1.6)
    sh.text(p[0] + 1.0, p[1] + 9.5, "G13: THE BASIN WASTE STRAIGHT DOWN INTO THE TOP INLET", 1.1)
    sh.text(40, ve.p(x0, 0, V["floor_z"] + 230)[1], "SECTION ON THE CENTRELINE, FROM THE KERB SIDE: TANKS, THE WELL, THE GREY TANK", 1.9, bold=True)
    sh.text(40, ve.p(x0, 0, V["floor_z"] + 230)[1] - 3.2, "SCALE 1:20", 1.5)
    sh.text(ve.p(w[0], 0, 0)[0], ve.p(0, 0, V["floor_z"])[1] + 1.6, "WELL WR-10, 300 x 400 x 120", 1.1)
    S.notes(sh, 22, 84, [
        "DATUM DIM-01. EVERY PIPE AND HOSE IS DRAWN AS ROUTED IN data/routes.yaml BY cad/routes.py, ITS CENTRELINE IN PLAN. THE SINK "
        "WASTE DROPS THROUGH THE ROAD GAP FRAME G15 AND RUNS UNDER THE FLOOR OVER CM-06 AT 1:50 INTO THE GREY TANK'S TOP. THE WASHER'S AND DRYER'S "
        "PUMPED DRAINS RISE BEHIND THE DRYER AND DISCHARGE INTO THE BASIN, WHICH DROPS THROUGH G13.",
        f"THE GREY TANK'S TOP SITS {V['floor_underside_z'] - gt[5]:.0f} mm UNDER THE FLOOR'S UNDERSIDE FOR THE INLETS, AND THE WELL'S "
        f"SHELL BOTTOM {w[2] - gt[5]:.0f} mm ABOVE THE TANK, SO THE SHOWER'S SWITCHING UNIT DRAINS STRAIGHT DOWN (H4A).",
        "EVERY WET ROOM DRAIN SITS OVER THE GREY TANK. THE TRAY FALLS 1:60 TO ITS FLOOR WASTE AND THE SHOWER ZONE TO ITS OWN DRAIN.",
        "THE FRESH TANKS BREATHE THROUGH G12 TO THE FILL CAP AT G1, THE GREY TANK UP THE REAR WALL TO A MESHED OUTLET (G25, G26). "
        "THE GREY TANK'S OUTLET, LEVER VALVE AND CAMLOCK ARE ON THE KERB SIDE FOR THE DUMP HOSE.",
        "THE COMBI'S DIESEL LINE COMES UP FROM THE HEATER FUEL TANK (UF-06) THROUGH G9. NO WATER LINE PASSES THE BATTERY'S TERMINAL FACE UNSLEEVED.",
    ], size=1.42, width_chars=185)
    yb = title(sh, dwg, reg, "TANKS AND FITTINGS IN THE MASS SCHEDULE (TB-11).", "6 mm HDPE TANKS, FOOD-GRADE LINES")
    rows = [["Fill", "G1 on the kerb wall", "The front tank, over CM-04", "Under the bed, down G12"],
            ["Tank outlets", "Both tanks, balanced over CM-05", "G15, the strainer and the pump", "From the rear tank"],
            ["Cold", "Manifold, sink cabinet", "Sink, drinking tap, Combi by G15 and G9", "Push-fit PEX"],
            ["Wet room", "Manifold, shower corner", "Basin, flush, washer tap, bypass, shower, rinse box", "Over the inner door"],
            ["Hot", "Combi, by G9 and G15", "Mixing valve at 50 C, then sink and wet room", "PEX"],
            ["Sink waste", "Sink", "Grey tank's top, by G15", "1:50 under the floor"],
            ["Washer, dryer", "Behind the dryer", "The basin", "Pumped, the washer's sleeved"],
            ["Basin, well, floor", "The wet room", "Grey tank, straight down", "G13, the well's valve, G24"],
            ["Dump", "Grey tank, kerb side", "Dump point or the 40 L tote", "Lever valve and camlock"]]
    y = wtable(sh, 230, yb - 6, [("LINE", 24), ("FROM", 40), ("TO", 66), ("HOW", 50)], rows, size=1.25, title="THE RUNS ON THIS SHEET")
    used = {x for run in rr["runs"] if run["system"] in PIPE_STYLE for x in _glands_of(run)}
    gr = [[x["id"], x["at"].upper(), _gland_runs(rr, x["id"], PIPE_STYLE) or "-", x["what"]] for x in svc["glands"] if x["id"] in used]
    y = wtable(sh, 230, y - 7, [("GLAND", 13), ("AT", 13), ("RUNS", 34), ("WHAT PASSES", 120)], gr, size=1.15,
               title="PLUMBING GLANDS (EACH ONE IN FULL ON CT-603)")
    yl = _legend(sh, 232, y - 7, [("cold", "COLD WATER"), ("hot", "HOT WATER"), ("drain", "DRAIN, FALLING TO THE GREY TANK"),
                                  ("thin", "BREATHERS, DIESEL AND THE LINE SET")])
    yl = _tag_legend(sh, 232, yl - 1.0, width=170.0)
    # every pipe and hose tagged at its two ends and wherever it changes level (I2-17), last, clear of the rest
    draw_tags(sh, pr, tags, regions=[(21.5, 136.5, 229.0, 266.0)], spill=(232.0, yl - 3.0, 174.0))
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-621 HVAC and ventilation
def ct621(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V, res, lay = C["V"], C["res"], C["day"]
    svc = C["svc"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    hb, hi = V["half_bw"], V["half_in"]
    pr = Proj(sh, "plan", k, 34.0, 166.0, ref=(V["body_x0"], -hb, 0))
    show = {"AC-01", "AC-02", "AC-03", "VE-04", "VE-05", "VE-07", "LA-03", "LA-11T", "LA-11B", "EL-02", "WR-06", "LA-09"}
    body_plan(sh, pr, lay, res, cut=1000.0, show=show, size=1.15, keep=False, swings=False, light=("AC-01", "AC-02", "VE-04", "VE-05", "LA-03"),
              nolabel=("LA-11T", "LA-11B", "EL-02", "VE-05", "AC-03"))
    f = lambda iid: _centre(lay.find(iid))  # noqa: E731
    pl = lay.find("EL-02").box
    pr.text(((pl[0] + pl[3]) / 2, (pl[1] + pl[4]) / 2), "PLINTH", 1.2)
    fa, fb, fc, fd = f("VE-01A"), f("VE-01B"), f("VE-01C"), f("VE-01D")
    # the e2 pairs, each sweeping across the trailer
    for a, b, t in ((fc, fa, "PAIR 1, C AND A"), (fd, fb, "PAIR 2, D AND B")):
        pa, pb = pr.p(a[0], a[1]), pr.p(b[0], b[1])
        sh.line(pa[0], pa[1], pb[0], pb[1], "air")
        for p_, q_ in ((pa, pb), (pb, pa)):
            L = math.hypot(q_[0] - p_[0], q_[1] - p_[1]) or 1
            sh.arrow((q_[0] - (q_[0] - p_[0]) * 0.08, q_[1] - (q_[1] - p_[1]) * 0.08), ((q_[0] - p_[0]) / L, (q_[1] - p_[1]) / L), 1.6, 0.45)
        m = (pa[0] + 0.22 * (pb[0] - pa[0]), pa[1] + 0.22 * (pb[1] - pa[1]))
        sh.text(m[0], m[1] + 1.0, t, 1.15, "middle", color="#1a7a3a")
    # towing: the RESPA's supply through the cabin, out through the relief valve
    r4 = f("VE-04")
    rv = f("VE-06")
    _route(pr, [(r4[0], r4[1] - 300), (4300, 200), (V["rear_x0"] - 200, 0), (V["wet_x0"] + 400, -200), (V["in_x1"] - 60, rv[1])], "airx", arrow=True)
    q = pr.p(4300, 230)
    sh.text(q[0], q[1] + 0.8, "TOWING: RESPA SUPPLY TO THE RELIEF VALVE", 1.15, "middle", color="#8a5a00")
    # the wet room extract and the range hood
    ex = f("VE-03")
    _route(pr, [(V["in_x1"] - 500, -700), (V["in_x1"], ex[1])], "airx", arrow=True)
    hood = f("VE-07")
    _route(pr, [(hood[0], hood[1]), (hood[0] + 30, hb)], "airx", arrow=True)
    # the split: indoor unit blowing forward, the line set to the outdoor unit through G5
    ai = f("AC-01")
    _route(pr, [(ai[0] - 150, ai[1] - 200), (ai[0] - 1100, ai[1] - 350)], "air", arrow=True)
    g5 = next(x for x in svc["glands"] if x["id"] == "G5")
    _route(pr, [(V["wet_x0"], g5["y"]), (V["in_x1"], g5["y"])], "thin")
    q = pr.p(V["wet_x0"] + 500, g5["y"] + 60)
    sh.text(q[0], q[1], "LINE SET, WET ROOM CEILING", 1.05, "middle")
    # the Combi's four warm-air ducts (outlets indicative)
    cb = f("LA-03")
    yr_ = hi - 60
    for pts in (((cb[0] - 120, cb[1]), (cb[0] - 120, yr_), (V["in_x0"] + 500, yr_), (V["in_x0"] + 500, yr_ - 250)),
                ((cb[0] - 160, cb[1]), (cb[0] - 160, yr_ - 40), (V["in_x0"] + 60, yr_ - 40), (V["in_x0"] + 60, -800), (V["in_x0"] + 300, -800)),
                ((cb[0] + 120, cb[1] - 200), (cb[0] + 120, 600), (4450, 600), (4450, 420)),
                ((cb[0] + 160, cb[1]), (cb[0] + 160, yr_), (V["wet_x0"] + 300, yr_), (V["wet_x0"] + 300, yr_ - 200))):
        _route(pr, pts, "hot", arrow=True)
    q = pr.p(cb[0], cb[1] - 330)
    sh.text(q[0], q[1], "COMBI DUCTS, IN FLOOR-LEVEL BULKHEADS", 1.1, "middle", color="#c00000")
    for gid, t in (("VE-01A", "A"), ("VE-01B", "B"), ("VE-01C", "C"), ("VE-01D", "D")):
        c = f(gid)
        q = pr.p(c[0], c[1])
        sh.circle(q[0], q[1], 1.3, "box")
        sh.circle(q[0], q[1], 1.3, "air")
        sh.text(q[0], q[1] - 0.45, t, 1.1, "middle", bold=True)
    sh.text(34, 166 + 2 * hb / k + 6.0, "PLAN, FRONT LEFT, ROAD SIDE UP: UNITS, FANS, VENTS, AIR PATHS AND THE COMBI'S DUCTS", 2.0, bold=True)
    _legend(sh, 34, 150, [("air", "HEAT-RECOVERY PAIRS AND THE SPLIT"), ("airx", "EXHAUST AND THE TOWING SUPPLY"), ("hot", "COMBI WARM-AIR DUCTS (INDICATIVE)")])
    rows = [["V1 e2 A", "Kerb wall high over the dryer", "Pair 1 with C"], ["V5 e2 B", "Road wall low in the sink cabinet", "Pair 2 with D"],
            ["V6 e2 C", "Front wall low, kerb side of the desk", "Pair 1 with A"], ["V7 e2 D", "Front wall low, road side of the desk", "Pair 2 with B"],
            ["V2", "Road wall high, intake hood", "RESPA and top-up fan"], ["V3", "Road wall, hood cowl", "Range hood, 100 m3/h"],
            ["V4", "Road wall low, Combi cowl", "Exhaust and combustion air"], ["V8", "Rear wall low, kerb half", "Relief valve, 30 cm2"],
            ["V9", "Rear wall high, kerb half", "RA 15-60 extract"], ["G5", "Rear wall, road half", "Split line set"]]
    wtable(sh, 112, 150, [("MARK", 16), ("WHERE", 56), ("WHAT", 42)], rows, size=1.15, title="VENTS AND FANS (CT-011, CT-013)")
    S.notes(sh, 22, 104, [
        "DATUM DIM-01. EACH e2 PAIR SWEEPS ACROSS THE TRAILER, FROM THE BED ZONE TO THE LIVING AREA. THE BED ZONE'S FANS SIT LOW ON THE FRONT "
        "WALL BECAUSE ITS SIDE WALLS HOLD THE WINDOWS AND THE LIFT RAILS.",
        "TOWING (DUST): THE e2 PAIRS, THE EXTRACT AND THE HOOD STOP. THE RESPA-CF2 SUPPLIES 150 TO 200 m3/h THROUGH ITS MERV 16 FILTER, SO "
        "EVERY LEAK FLOWS OUTWARD AND THE CABIN SITS AT LEAST 20 Pa ABOVE THE REAR WAKE. THE EXCESS LEAVES THROUGH THE RELIEF VALVE (V8) AND "
        "SWEEPS THE WET ROOM ON THE WAY.",
        "PARKED: THE TOP-UP FAN SUPPLIES 15 m3/h MORE THAN THE EXTRACTS, ABOUT +3 Pa IN CALM AIR, 40 m3/h AND ABOUT +20 Pa IN WIND OR DUST.",
        "THE CERBO GX STOPS PAIR 2 WHILE THE COMBI BURNS DIESEL, BECAUSE FAN B IS 630 mm FROM ITS COWL. THE CO ALARM IS THE BACKUP.",
        "THE SPLIT'S CONDENSATE DRAINS THROUGH A TRAP TO THE WET ROOM FLOOR WASTE. THE OUTDOOR UNIT'S DEFROST WATER RUNS BY HOSE CLEAR OF THE RINSE BOX.",
        "THE COMBI'S DUCT OUTLETS ARE INDICATIVE: TWO TO THE BED ZONE, ONE TO THE LIVING AREA, ONE THROUGH THE PARTITION TO THE WET ROOM.",
    ], size=1.42, width_chars=185)
    yb = title(sh, dwg, reg, "HVAC AND VENTILATION 78.4 kg, 85.0 kg WITH GROWTH (TB-11).", "SEE THE PRODUCTS NAMED")
    rows = [[m["mode"], m["e2"], m["ra"], m["topup"], m["respa"], m["split"]] for m in svc["ventilation_modes"]]
    y = wtable(sh, 230, yb - 6, [("MODE", 26), ("e2 PAIRS m3/h", 26), ("RA 15-60 m3/h", 30), ("TOP-UP m3/h", 32), ("RESPA-CF2", 34), ("SPLIT", 32)],
               rows, size=1.25, title="MODES, ONE ROTARY SWITCH OR A CERBO GX PAGE (report 19 section 6)")
    rows = [["Split, Mitsubishi MSZ-AP25VGKD2 and MUZ-AP25VGD2", "2.5 kW cooling, 3.2 kW heating, never shed (C8)", "Its own thermostat, 24 C in summer, 20 C in winter"],
            ["LUNOS e2 60, two pairs", "30 m3/h a pair by day, 22.5 at night, 60 on boost", "5/UNI-FT controller, humidity and switches"],
            ["LUNOS RA 15-60 extract", "15 m3/h base, 60 during each shower and 30 min after", "Same controller"],
            ["Sy-Klone RESPA-CF2, 24 V", "150 to 200 m3/h while towing, MERV 16 and carbon", "The plug's auxiliary feed, or a dust switch"],
            ["Top-up fan, 24 V EC", "15 to 40 m3/h at up to 100 Pa, the smoke mode's fresh air", "A small 24 V controller"],
            ["Range hood, Sphere TCR-001", "About 100 m3/h while cooking", "Its own touch panel"],
            ["Truma Combi D 6 E", "Diesel or 900 / 1,800 W, four warm-air ducts", "Its own Truma panel"]]
    y = wtable(sh, 230, y - 7, [("UNIT", 56), ("RATE", 66), ("CONTROL", 58)], rows, size=1.25, title="UNITS, RATES AND CONTROLS (report 19)")
    S.notes(sh, 230, y - 6, [
        "BODY TIGHTNESS TARGET: AN EFFECTIVE LEAKAGE AREA OF 30 cm2 OR LESS, ABOUT 60 m3/h AT 50 Pa. TEST IT BEFORE THE FIT-OUT CLOSES.",
        "A CABIN PRESSURE GAUGE (0 TO 125 Pa) SHOWS A BLOCKED FILTER OR A FAILED SEAL WHILE TOWING.",
    ], size=1.3, width_chars=150)
    write(sh, dwg)
    return time.time() - t0

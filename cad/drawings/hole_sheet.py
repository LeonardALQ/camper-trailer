"""CT-105, the holes for galvanising by closed section (A3), from the build's hole records (cad/chassis_holes.py), with the
drawbar's square apex cut and its mitre lines drawn and the sealed overlaps' vents (I2-89, report 02 WLD-05).

The schedule gives every hole once, under the closed section it drains or vents: its use, its diameter, its web, the end
it is measured from, its distance along the web from that end and its height over the member's underside. Nothing here
places a hole: a hole the chassis code moves moves on this sheet.
"""
from __future__ import annotations

import math
import time

import numpy as np

from .. import chassis_holes as CH
from . import sheet as S
from .chassis_sheets import OUT, _chassis, _draft_stamp, _layout, _title, plate

SIZE, ROW = 1.4, 2.5            # the schedule's text and row height, mm
COLS = (("HOLE", 9.0), ("USE", 14.0), ("DIA", 6.0), ("WEB", 9.5), ("FROM", 13.5), ("ALONG", 8.5), ("OVER", 7.5))
LEFT = (22.0, 91.0, 160.0)       # the schedule's three columns' left edges, mm
TOP, BOTTOM = 279.0, 12.0
USE_WORDS = {"drain": "DRAIN", "vent": "VENT", "drain and vent": "DRAIN, VENT", "check": "CHECK", "seam vent": "SEAM VENT"}


def _n(v: float) -> str:
    return f"{round(float(v), 1):g}"


def _short(section: str) -> str:
    return section.replace(" x ", "x").replace("_", " ").replace("p", ".")


class Hole:
    """One record read for the schedule: the closed section it serves, its web, the end it is measured from, its distance
    along the web from that end and its height over the underside."""

    def __init__(self, h: dict, ch, words: dict | None = None):
        self.h, self.id, self.d = h, h["id"], float(h["d"])
        galv = next((r for r in h["runs"] if r in CH.GALV_USES), None)
        self.bolt = galv is None                 # a fixing's hole (CH.bolt_records), its use from `words` by its run
        self.use = USE_WORDS[galv] if galv else next(w for k, w in (words or {}).items() if any(str(r).startswith(k) for r in h["runs"]))
        mem = {m.id: m for m in ch.members}
        if h["member"] in mem:
            m = mem[h["member"]]
            self.role, p0, p1, dd, sec = m.role, m.p0, m.p1, m.depth_dir, m.sec
        else:                                    # a hinge gusset CH-P08, carried as a fitting
            g = next(g for g in ch.hinge_gussets() if g["id"] == h["member"])
            self.role, p0, p1, dd = "hinge_gusset", g["p0"], g["p1"], (0.0, 0.0, 1.0)
            sec = ch.sections[next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
        ex, ey, _ = CH.member_axes(p0, p1, dd)
        c = CH.centre(h)
        L = math.dist(p0, p1)
        s = float(np.dot(c - np.asarray(p0, float), ex))
        self.section = {"DB-KA": "DB-K", "DB-KB": "DB-K", "DB-RA": "DB-R", "DB-RB": "DB-R"}.get(h["member"], h["member"])
        split = self.role == "plan_brace" and h["member"].endswith("R")      # cut at the crossing (chassis_dip)
        if split:
            half = 1 if s < L / 2 else 2
            self.section = f"{h['member']}.{half}"
            lo, hi = (0.0, L / 2) if half == 1 else (L / 2, L)
            ends = [(lo, p0 if half == 1 else None), (hi, None if half == 1 else p1)]
        else:
            ends = [(0.0, p0), (L, p1)]
        k = 0 if abs(s - ends[0][0]) <= abs(s - ends[1][0]) else 1
        self.end = k
        self.frm = self._end_name(h["member"], ends[k][1], ends[k][1] is p0)
        self.along = float(h["u_web"]) if "u_web" in h else abs(s - ends[k][0])
        if CH.is_seam(h):
            self.web, self.over = "SEAM", None
        else:
            n = (1.0 if float(np.dot(c - np.asarray(p0, float), ey)) > 0 else -1.0) * ey
            if abs(n[0]) >= abs(n[1]) - 1e-6:
                self.web = "FRONT" if n[0] < 0 else "REAR"
            else:
                self.web = "INNER" if n[1] * c[1] < 0 else "OUTER"
            self.over = float(h["z_under"]) if "z_under" in h else float(c[2]) - (p0[2] - sec.d / 2)

    def _end_name(self, member: str, point, first: bool) -> str:
        if point is None:
            return "CROSSING"
        if self.role == "rail":
            return "FRONT END" if first else "REAR END"
        if member in ("DB-KA", "DB-RA"):
            return "APEX CUT"
        if member in ("DB-KB", "DB-RB"):
            return "MITRE LINE"
        if self.role == "outrigger":
            return "ROOT END"
        if self.role == "hinge_gusset":                 # its first end on the crossmember's rear face (Chassis.hinge_gussets)
            return "CM FACE" if first else "RAIL FACE"
        return "KERB END" if point[1] < 0 else "ROAD END"

    def row(self) -> list[str]:
        return [self.id, self.use, f"{self.d:g}", self.web, self.frm, _n(self.along), "-" if self.over is None else _n(self.over)]


def section_names(chs: dict, ch) -> dict:
    """Each closed section's heading: its marks, what it is, its section and its length."""
    out = {}
    mem = {m["id"]: m for m in chs["members"]}
    for m in chs["members"]:
        sec = _short(m["section"])
        if m["id"].startswith("PB-"):
            side = "KERB" if m["id"].endswith("K") else "ROAD"
            what = f"PLAN BRACE {m['id'][3]} FROM THE {side} SIDE RAIL"
            if side == "ROAD":                   # cut at the crossing, from the road side rail to the kerb side rail
                out[f"{m['id']}.1"] = f"{m['id']}.1 PLAN BRACE {m['id'][3]}, ROAD SIDE RAIL TO THE CROSSING, {sec}"
                out[f"{m['id']}.2"] = f"{m['id']}.2 PLAN BRACE {m['id'][3]}, CROSSING TO THE KERB SIDE RAIL, {sec}"
                continue
        else:
            what = m["name"].upper()
        out[m["id"]] = f"{m['id']} {what}, {sec}, {m['length_mm']:.0f} LONG"
    for s in ("K", "R"):
        a, b = mem[f"DB-{s}A"], mem[f"DB-{s}B"]
        side = "KERB" if s == "K" else "ROAD"
        out[f"DB-{s}"] = (f"DB-{s}A AND DB-{s}B DRAWBAR MEMBER, {side} SIDE, {_short(a['section'])}, "
                          f"{a['length_mm'] + b['length_mm']:.0f} LONG")
    gsec = _short(next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"])
    for g in ch.hinge_gussets():
        out[g["id"]] = f"{g['id']} HINGE GUSSET BEHIND {g['cm']}, {'KERB' if g['side'] < 0 else 'ROAD'} SIDE, {gsec}"
    return out


def schedule(chs: dict, ch, words: dict | None = None) -> list[tuple[str, list[Hole]]]:
    """The holes by closed section, the sections in the members' order and each section's holes by end, distance and web:
    the holes for galvanising and, with `words` naming each fixing's use by its run, the bolt and rivet nut holes of the
    fresh tanks' bearers and the front guard's hangers (I2-109, I2-116)."""
    holes = [Hole(h, ch) for h in CH.records()] + ([Hole(h, ch, words) for h in CH.bolt_records()] if words else [])
    order = {m["id"]: k for k, m in enumerate(chs["members"])}
    first = {}
    for h in holes:
        first.setdefault(h.section, (order.get(h.h["member"], len(order)), h.section))
    out = []
    for sec in sorted(first, key=lambda s: first[s]):
        mine = sorted((h for h in holes if h.section == sec), key=lambda h: (h.end, h.along, h.web, h.over or 0.0))
        out.append((sec, mine))
    return out


# ------------------------------------------------------------------ the schedule
def _column(sh, x: float, top: float, rows: list) -> None:
    """One column of the schedule from `top` down: the column heads, then each section's heading across the column and its
    holes one to a row, ruled, the column lines broken at the headings so no line runs through a heading."""
    w = sum(c[1] for c in COLS)
    n = len(rows) + 1
    sh.rect(x, top - n * ROW, x + w, top, "medium")
    cx = x
    for head, cw in COLS:
        sh.text(cx + 0.6, top - ROW + 0.75, head, SIZE, bold=True, cell=True)
        cx += cw
    runs, start = [], 0
    for i, (kind, val) in enumerate(rows, 1):
        y = top - (i + 1) * ROW + 0.75
        if kind == "head":
            if i > start:
                runs.append((start, i))
            start = i + 1
            sh.text(x + 0.6, y, val, SIZE, cell=True)
        else:
            cx = x
            for (_, cw), v in zip(COLS, val):
                sh.text(cx + 0.6, y, v, SIZE, cell=True)
                cx += cw
        if i < len(rows):
            sh.line(x, top - (i + 1) * ROW, x + w, top - (i + 1) * ROW, "thin")
    sh.line(x, top - ROW, x + w, top - ROW, "thin")
    runs.append((start, n))
    cx = x
    for _, cw in COLS[:-1]:
        cx += cw
        for a, b in runs:
            if b > a:
                sh.line(cx, top - a * ROW, cx, top - b * ROW, "thin")


def columns(sections: list, names: dict, per: int) -> list[list]:
    """The schedule's rows in columns of at most `per` rows: a section never starts on a column's last row, and one that
    runs on into the next column takes its heading again there."""
    cols, cur = [], []
    for sec, holes in sections:
        if len(cur) + 2 > per:
            cols.append(cur)
            cur = []
        cur.append(("head", names[sec]))
        for h in holes:
            if len(cur) >= per:
                cols.append(cur)
                cur = [("head", names[sec] + " (CONT.)")]
            cur.append(("hole", h.row()))
    cols.append(cur)
    return cols


# ------------------------------------------------------------------ the details
def _aligned(sh, a, b, off: float, text: str, size: float = 1.4):
    """An aligned dimension between sheet points a and b, its line `off` mm to the left of a to b (right where negative),
    its text on the far side of the line."""
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -uy, ux
    s = 1.0 if off > 0 else -1.0
    pa, pb = (a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off)
    for p, q in ((a, pa), (b, pb)):
        sh.line(p[0] + nx * S.GAP * s, p[1] + ny * S.GAP * s, q[0] + nx * S.EXT * s, q[1] + ny * S.EXT * s)
    sh.line(pa[0], pa[1], pb[0], pb[1])
    if L > 7:
        sh.arrow(pa, (-ux, -uy), line=False)
        sh.arrow(pb, (ux, uy), line=False)
    else:
        sh.line(pa[0] - ux * 5, pa[1] - uy * 5, pb[0] + ux * 5, pb[1] + uy * 5)
        sh.arrow(pa, (ux, uy), line=False)
        sh.arrow(pb, (-ux, -uy), line=False)
    ang = math.degrees(math.atan2(uy, ux))
    flip = ang > 90 or ang < -90
    if flip:
        ang -= 180 if ang > 0 else -180
    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    up = (-math.sin(math.radians(ang)), math.cos(math.radians(ang)))      # the text's up on the sheet
    side = 1.0 if (up[0] * nx + up[1] * ny) * s > 0 else -1.0
    lift = 0.8 if side > 0 else 0.8 + S.CAPS * size
    sh.text(mx + up[0] * lift * side, my + up[1] * lift * side, text, size, "middle", rot=-ang)


def _edge_on(sh, c, n, d: float, k: float, t: float):
    """A hole in a web seen edge on: its centre line across the web and its bore's two edges through the wall, hidden.
    `c` is the hole's centre on the web's outer face and `n` the web's outward normal, both on the sheet."""
    tx, ty = -n[1], n[0]
    sh.line(c[0] - n[0] * (t / k + 2.0), c[1] - n[1] * (t / k + 2.0), c[0] + n[0] * 2.0, c[1] + n[1] * 2.0, "centre")
    for e in (-1, 1):
        ex, ey = c[0] + tx * e * d / 2 / k, c[1] + ty * e * d / 2 / k
        sh.line(ex, ey, ex - n[0] * t / k, ey - n[1] * t / k, "hidden")


def _detail_title(sh, cx, top, title, scale, note=""):
    sh.text(cx, top, title, 2.0, "middle", bold=True)
    sh.text(cx, top - 3.2, f"SCALE 1:{scale:g}", 1.7, "middle")
    if note:
        sh.text(cx, top - 6.0, note, 1.4, "middle")


def _apex_detail(sh, ch, holes: list, x0: float, y0: float, k: float = 2.5):
    """Detail A: the kerb-side drawbar member's apex end in plan, the road side's mirrored: the end cut square to the
    member through its axis point, and each web's drain and vent their distance along the web from that cut, from the
    records (each record's centre less its distance along the web, which is the cut's corner on that web)."""
    m = next(mm for mm in ch.members if mm.id == "DB-KA")
    ex, ey, _ = CH.member_axes(m.p0, m.p1, m.depth_dir)
    a, hb, t = np.asarray(m.p0, float), m.sec.b / 2, m.sec.t
    xa, ya = a[0] - 20.0, a[1] - 75.0

    def p(q):
        return float(x0 + (q[0] - xa) / k), float(y0 + (q[1] - ya) / k)
    mine = [h for h in holes if h.h["member"] == "DB-KA"]
    for w in (1, -1):
        c0, c1 = a + w * hb * ey, a + w * hb * ey + 125 * ex
        sh.line(*p(c0), *p(c1), "medium")
        sh.line(*p(c0 - w * t * ey), *p(c1 - w * t * ey), "hidden")         # the web's inside face, under the top wall
    sh.line(*p(a + hb * ey), *p(a - hb * ey), "medium")
    sh.line(*p(a + hb * ey + 125 * ex), *p(a - hb * ey + 125 * ex), "thin")
    sh.line(*p(a - 4 * ex), *p(a + 130 * ex), "centre")
    sh.circle(*p(a), 0.5, "medium")
    seen = {}
    for h in mine:
        seen.setdefault(h.web, h)
    for web, h in seen.items():
        c = CH.centre(h.h)
        w = 1 if web == "INNER" else -1
        n = (w * ey[0], w * ey[1])
        _edge_on(sh, p(c), n, h.d, k, t)
        corner = c[:2] - h.along * ex[:2]
        _aligned(sh, p(corner), p(c), 4.0 * w, _n(h.along))
    drain = next(h for h in mine if h.use == "DRAIN")
    vent = next(h for h in mine if h.use == "VENT")
    ang = math.degrees(math.atan2(ey[1], ey[0]))
    lab = p(a - 0.45 * hb * ey - 8.0 * ex)
    sh.text(lab[0], lab[1], "SQUARE CUT", 1.4, "middle", rot=-ang)
    _caption(sh, x0, y0 - 9.0, f"THE APEX END CUT SQUARE TO THE MEMBER THROUGH ITS AXIS POINT X {a[0]:,.0f}, Y {a[1]:,.0f}. IN EACH WEB A "
             f"DRAIN {drain.d:g} AT {_n(drain.over)} AND A VENT {vent.d:g} AT {_n(vent.over)} OVER THE UNDERSIDE, THEIR CENTRES "
             f"{_n(drain.along)} ALONG THE WEB FROM THE CUT.", 80.0)


def _caption(sh, x: float, y: float, text: str, width: float, size: float = 1.4) -> float:
    """Plain lines of text from (x, y) down, wrapped to `width` mm. Returns the y under them."""
    for i, line in enumerate(S.wrap_mm(text, width, size)):
        sh.text(x, y - (size + 0.9) * i, line, size)
    return y - (size + 0.9) * len(S.wrap_mm(text, width, size))


def _meet(p, u, q, v) -> np.ndarray:
    """Where the line through p along u meets the line through q along v, in plan."""
    s = np.linalg.solve(np.array([[u[0], -v[0]], [u[1], -v[1]]], float), np.subtract(q, p, dtype=float))[0]
    return np.asarray(p, float) + s * np.asarray(u, float)


def _mitre_detail(sh, ch, holes: list, x0: float, y0: float, k: float = 2.5):
    """Detail B: the kerb-side drawbar member's mitre at the body front in plan, the road side's mirrored: each web's
    mitre line, where the A-frame length meets the length under the rail, and each web's drain along that web from its
    line, from the records (each drain's centre less its distance along the web)."""
    a_m = next(mm for mm in ch.members if mm.id == "DB-KA")
    b_m = next(mm for mm in ch.members if mm.id == "DB-KB")
    ea, _, _ = CH.member_axes(a_m.p0, a_m.p1, a_m.depth_dir)
    o, hb, t = np.asarray(b_m.p0, float), b_m.sec.b / 2, b_m.sec.t
    xa, ya = o[0] - 70.0, o[1] - 45.0

    def p(x, y):
        return float(x0 + (x - xa) / k), float(y0 + (y - ya) / k)
    mine = {h.web: h for h in holes if h.h["member"] == "DB-KB"}
    pts = {}
    for web, h in mine.items():
        c = CH.centre(h.h)
        line_x = c[0] - h.along
        pts[web] = (line_x, c[1])
        far = (o[0] + 125.0, c[1])
        sh.line(*p(line_x, c[1]), *p(*far), "medium")
        back = (line_x - 75.0 * ea[0], c[1] - 75.0 * ea[1])
        sh.line(*p(line_x, c[1]), *p(*back), "medium")
        w = 1 if web == "INNER" else -1
        _edge_on(sh, p(c[0], c[1]), (0.0, float(w)), h.d, k, t)
        yb = p(0, c[1])[1]
        S.hdim(sh, p(line_x, 0)[0], yb, p(c[0], 0)[0], yb, yb + 4.0 * w, _n(h.along), size=1.4)
    m_in, m_out = np.array(pts["INNER"]), np.array(pts["OUTER"])
    eya = np.array((-ea[1], ea[0]))                       # across the A-frame length, inboard for the kerb side
    for web, w in (("INNER", 1), ("OUTER", -1)):          # each web's inside face, hidden under the top wall
        q = _meet(np.array((0.0, pts[web][1] - w * t)), np.array((1.0, 0.0)), m_in, m_out - m_in)
        sh.line(*p(*q), *p(o[0] + 125.0, pts[web][1] - w * t), "hidden")
        q = _meet(np.array(pts[web]) - w * t * eya, ea[:2], m_in, m_out - m_in)
        sh.line(*p(*q), *p(*(q - 75.0 * ea[:2])), "hidden")
    sh.line(*p(*pts["INNER"]), *p(*pts["OUTER"]), "medium")
    sh.line(*p(o[0] + 125.0, o[1]), *p(o[0], o[1]), "centre")
    sh.line(*p(o[0], o[1]), *p(o[0] - 80.0 * ea[0], o[1] - 80.0 * ea[1]), "centre")
    sh.circle(*p(o[0], o[1]), 0.5, "medium")
    sh.line(*p(o[0] + 125.0, o[1] - hb), *p(o[0] + 125.0, o[1] + hb), "thin")
    behind, ahead = pts["INNER"][0] - o[0], o[0] - pts["OUTER"][0]
    mid = ((pts["INNER"][0] + pts["OUTER"][0]) / 2, (pts["INNER"][1] + pts["OUTER"][1]) / 2)
    tip = p(mid[0] - 0.25 * (pts["INNER"][0] - pts["OUTER"][0]), mid[1] - 0.25 * (pts["INNER"][1] - pts["OUTER"][1]))
    S.leader(sh, tip, (tip[0] - 7.0, tip[1] - 8.0), "MITRE LINE", size=1.4)
    _caption(sh, x0, y0 - 9.0, f"EACH WEB'S MITRE LINE STANDS {behind:.1f} BEHIND THE AXIS POINT X {o[0]:,.0f} ON THE INNER WEB AND "
             f"{ahead:.1f} AHEAD OF IT ON THE OUTER. EACH WEB'S DRAIN {mine['INNER'].d:g}, AT {_n(mine['INNER'].over)} OVER THE "
             f"UNDERSIDE, STANDS {_n(mine['INNER'].along)} ALONG THAT WEB FROM ITS LINE.", 80.0)


def _web_detail(sh, ch, holes: list, x0: float, y0: float, k: float = 5.0):
    """Detail C: what the schedule's ALONG and OVER measure, drawn on the first crossmember's kerb end, its front web, from
    its records: the end at the rail's inner web on the left, the web's flat between its corner radii, the holes."""
    first = next(h for h in holes if h.role in ("cm_end", "cm_xt", "cm_floor") and h.frm == "KERB END" and h.web == "FRONT")
    mine = sorted((h for h in holes if h.section == first.section and h.frm == "KERB END" and h.web == "FRONT"), key=lambda h: h.over)
    sec = next(mm for mm in ch.members if mm.id == first.section).sec
    L = 110.0

    def p(u, z):
        return x0 + u / k, y0 + z / k
    sh.rect(*p(0, 0), *p(L, sec.d), "medium")
    for z in (sec.ro, sec.d - sec.ro):
        sh.line(*p(0, z), *p(L, z), "thin")
    sh.rect(*p(-8.0, -10.0), *p(0, sec.d + 10.0), "thin")
    sh.text(p(-4.0, 0)[0], p(0, -10.0)[1] - 2.4, "RAIL", 1.4, "middle")
    for h in mine:
        c = p(h.along, h.over)
        sh.circle(*c, h.d / 2 / k, "medium")
        sh.line(c[0] - h.d / k, c[1], c[0] + h.d / k, c[1], "centre")
        sh.line(c[0], c[1] - h.d / k, c[0], c[1] + h.d / k, "centre")
    top = p(0, sec.d)[1]
    S.hdim(sh, p(0, 0)[0], top, p(mine[0].along, 0)[0], top, top + 4.0, "ALONG", size=1.4)
    for i, h in enumerate(mine):
        c = p(h.along, h.over)
        S.vdim(sh, c[0], p(0, 0)[1], c[0], c[1], p(L, 0)[0] + 4.0 + 5.0 * i, "OVER", size=1.4)
    _caption(sh, x0 - 2.0, y0 - 8.0, f"{first.section}'S KERB END ON ITS FRONT WEB. ALONG: FROM THE END NAMED, ALONG THE WEB, TO THE "
             "HOLE'S CENTRE. OVER: FROM THE MEMBER'S UNDERSIDE TO THE HOLE'S CENTRE.", 70.0)


def _plate_detail(sh, ch, x0: float, y0: float, k: float = 5.0):
    """Detail D: the kerb-side shock support plate CH-P07 from ahead, its outboard end on the right, the road side's
    mirrored, with its vents through the plate as sealed_overlaps places them (cad/chassis_holes.plate_vents)."""
    vents = [v for v in CH.plate_vents(ch) if v["side"] < 0]
    vents = [v for v in vents if v["box"] == vents[0]["box"]]   # one plate's: every plate is the same and vents alike
    on = sorted({p["member"] for p in ch.shock_plates()})

    def p(u, v):
        return x0 + (vents[0]["l"] - u) / k, y0 + v / k           # u from the outboard end, on the right
    sh.rect(*p(vents[0]["l"], 0), *p(0, vents[0]["w"]), "medium")
    for i, v in enumerate(sorted(vents, key=lambda v: v["u"])):
        c = p(v["u"], v["v"])
        sh.circle(*c, v["d"] / 2 / k, "medium")
        sh.line(c[0] - v["d"] / k, c[1], c[0] + v["d"] / k, c[1], "centre")
        sh.line(c[0], c[1] - v["d"] / k, c[0], c[1] + v["d"] / k, "centre")
        S.hdim(sh, p(0, 0)[0], p(0, 0)[1], c[0], c[1], p(0, 0)[1] - 4.0 - 5.0 * i, _n(v["u"]), size=1.4)
        S.vdim(sh, p(0, 0)[0], p(0, 0)[1], c[0], c[1], p(0, 0)[0] + 4.0 + 5.0 * i, _n(v["v"]), size=1.4)
    sh.text(p(vents[0]["l"], 0)[0], p(0, vents[0]["w"])[1] + 1.2, "INBOARD", 1.4)
    sh.text(p(0, 0)[0], p(0, vents[0]["w"])[1] + 1.2, "OUTBOARD, BY THE RAIL", 1.4, "end")
    _caption(sh, x0 - 2.0, y0 - 15.0, f"{vents[0]['plate']}, {vents[0]['t']:g} PLATE SEAL WELDED TO {' AND '.join(m + chr(39) + 'S' for m in on)} "
             f"FRONT WEBS, VENTED THROUGH EACH PLATE BY {len(vents)} HOLES {vents[0]['d']:g} AT OPPOSITE CORNERS.", 70.0)


def _break(sh, x0: float, x1: float, y: float):
    """A thin break line across a cut-off member, with its zigzag in the middle."""
    m = (x0 + x1) / 2
    sh.path([(x0 - 1.0, y), (m - 1.0, y), (m - 0.4, y + 1.2), (m + 0.4, y - 1.2), (m + 1.0, y), (x1 + 1.0, y)], "thin")


def _seam_detail(sh, ch, holes: list, cx: float, y0: float, k: float = 2.5):
    """Detail E: a section across the rail and its raiser at a seam vent, the rail's top and the raiser's bottom only: the
    vent through the rail's top wall and the raiser's bottom wall on their centreline, from the seam vents' records."""
    rail, raiser = ch.role_sec["rail"], ch.role_sec["raiser"]
    seam = [h for h in holes if h.web == "SEAM"]
    d, reach = seam[0].d, 30.0

    def p(y, z):
        return cx + y / k, y0 + z / k              # y across from the seam's centreline, z up from the seam
    for a, b in ((-rail.b / 2, -d / 2), (d / 2, rail.b / 2)):
        plate(sh, *p(a, -rail.t), *p(b, 0.0))
    for a, b in ((-raiser.b / 2, -d / 2), (d / 2, raiser.b / 2)):
        plate(sh, *p(a, 0.0), *p(b, raiser.t))
    for s in (-1, 1):
        plate(sh, *p(s * (rail.b / 2 - rail.t), -reach), *p(s * rail.b / 2, -rail.t))
        plate(sh, *p(s * (raiser.b / 2 - raiser.t), raiser.t), *p(s * raiser.b / 2, reach))
    _break(sh, p(-rail.b / 2, 0)[0], p(rail.b / 2, 0)[0], p(0, -reach)[1])
    _break(sh, p(-raiser.b / 2, 0)[0], p(raiser.b / 2, 0)[0], p(0, reach)[1])
    sh.line(*p(0, -reach + 6.0), *p(0, reach - 6.0), "centre")
    sh.text(p(rail.b / 2, 0)[0] + 1.5, p(0, -reach + 4.0)[1], "RAIL", 1.4)
    sh.text(p(raiser.b / 2, 0)[0] + 1.5, p(0, reach - 6.0)[1], "RAISER", 1.4)
    S.leader(sh, p(d / 2, -rail.t / 2), (p(rail.b / 2, 0)[0] + 5.0, p(0, -rail.t / 2)[1] + 1.0), f"VENT {d:g}", size=1.4)
    alongs = sorted({_n(h.along) for h in seam})
    _caption(sh, cx - 22.0, y0 - reach / k - 5.0, f"THROUGH THE RAIL'S TOP WALL AND THE RAISER'S BOTTOM WALL ON THEIR CENTRELINE, "
             f"{' AND '.join(alongs)} FROM EACH END OF THE RAIL, ON BOTH RAILS.", 48.0)


def ct105(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, _ = _layout(prj, model)
    ch = lay.chassis
    chs = _chassis()
    sp = lay._bearers_spec() or {}
    hb = sp.get("hanger_bolts") or {}
    words = {"bolt for UF-01B": f"{sp['bolts']['size']} BOLT", "bolt for UF-03": f"{hb['size']} BOLT",
             "rivet nut for UF-03": f"{hb['size']} RIVET NUT"} if sp else {}
    gp = lay._bearer_lines().get("UF-08B") or {}        # the grey tank's bearers and its guard's hangers (I2-122)
    ghb = gp.get("hanger_bolts") or {}
    words.update({"bolt for UF-08B": f"{gp['bolts']['size']} BOLT", "rivet nut for UF-09": f"{ghb['size']} RIVET NUT"} if gp else {})
    sections = schedule(chs, ch, words)
    every = [h for _, hs in sections for h in hs]
    holes = [h for h in every if not h.bolt]
    bolts = [h for h in every if h.bolt]
    names = section_names(chs, ch)
    sh = S.Sheet()
    S.frame(sh)
    per = int((TOP - BOTTOM) / ROW) - 1
    cols = columns(sections, names, per)
    if len(cols) > len(LEFT):
        raise ValueError(f"CT-105's schedule needs {len(cols)} columns where the sheet has {len(LEFT)}")
    sh.text(LEFT[0], TOP + 2.0, f"HOLES BY CLOSED SECTION, {len(holes)} FOR GALVANISING AND {len(bolts)} FOR FIXINGS, IN {len(sections)} SECTIONS",
            2.2, bold=True)
    for x, rows in zip(LEFT, cols):
        _column(sh, x, TOP, rows)
    mirrored = "KERB SIDE, THE ROAD SIDE MIRRORED"
    _detail_title(sh, 275.0, 264.0, "A: DRAWBAR APEX END, PLAN", 2.5, mirrored)
    _apex_detail(sh, ch, holes, 240.0, 210.0)
    _detail_title(sh, 364.0, 264.0, "B: DRAWBAR MITRE, PLAN", 2.5, mirrored)
    _mitre_detail(sh, ch, holes, 325.0, 208.0)
    _detail_title(sh, 268.0, 190.0, "C: ALONG AND OVER, ON A WEB", 5)
    _web_detail(sh, ch, holes, 248.0, 150.0)
    _detail_title(sh, 362.0, 190.0, "D: SHOCK PLATE VENTS, FROM AHEAD", 5, mirrored)
    _plate_detail(sh, ch, 330.0, 150.0)
    _detail_title(sh, 262.0, 133.0, "E: SEAM VENT, SECTION", 2.5)
    _seam_detail(sh, ch, holes, 260.0, 113.0)
    S.notes(sh, 292.0, 127.0, [
        "HOT-DIP GALVANISE TO AS/NZS 4680 IN ONE DIP AS CT-103 NOTE 2 AND DETAIL K SAY. DRILL OR HOLE-SAW AND DEBURR EVERY HOLE BEFORE "
        "WELDING (report 02 WLD-05). THE SCHEDULE LISTS EVERY HOLE CHS-09, CHS-10 AND CHS-11 READ, UNDER THE CLOSED SECTION IT DRAINS OR VENTS, AND THE FIXINGS' HOLES.",
        "DIMENSIONS ARE TO EACH HOLE'S CENTRE (DETAIL C). FROM GIVES THE END THAT ALONG STARTS AT ON THAT WEB: A MEMBER'S END AT ITS WELD, "
        "THE DRAWBAR MEMBER'S SQUARE APEX CUT OR THAT WEB'S MITRE LINE (DETAILS A AND B), A RAIL'S NEARER END, A ROAD SIDE PLAN BRACE'S "
        "CROSSING, OR A HINGE GUSSET'S FACE ON THE CROSSMEMBER OR THE RAIL.",
        "WEB: FRONT AND REAR FACE THE DRAWBAR AND THE REAR, INNER AND OUTER FACE THE CENTRELINE AND THE SIDE. SEAM: THROUGH THE RAIL'S TOP "
        "AND THE RAISER'S BOTTOM WALL (DETAIL E). THE RAILS' INNER-WEB HOLES AT CM-05 AND CM-06 DRAIN AND VENT THEIR FRONT CORNERS, EACH WITH A CHECK "
        "HOLE OPPOSITE IN THE OUTER WEB.",
        "BOLT AND RIVET NUT: THE FIXINGS' HOLES, DRILLED BEFORE GALVANISING. A BOLT GOES THROUGH BOTH WEBS, ITS HOLES IN LINE (UF-01B ON "
        "CM-04 AND CM-05, UF-03 ON CM-04, UF-08B ON CM-06 AND CM-08). EACH RAIL'S HANGER UF-03 OR UF-09 BOLTS INTO A BLIND RIVET NUT IN THE INNER WEB ONLY.",
    ] + [f"{c['member']}'S ENDS ARE ITS RECOVERY TONGUES' FACES, {c['cut']:g} INSIDE THE RAILS."
         for c in ch.data["member_galvanising_holes"].get("cut_ends", [])], width_chars=70, size=1.5)
    _draft_stamp(sh, 350.0, 74.0)
    _title(sh, dwg, reg, "SEE CT-101 FOR MASSES (TB-11).", dwg["scale"], chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

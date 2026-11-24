"""Shared parts of the home trailer's sheets (TRAILER.md revision J, the H11 set): the layout and its results, the title
block, short plain names for the items, and plan, elevation and section projections drawn from the blocks' boxes.

The sheets that use these draw the trailer as the layout places it (data/assemblies/trailer.yaml through cad/trailer.py),
so a change to the data moves the drawings with it. Every view shows its subject as seen (DIM-01 is right-handed).
"""
from __future__ import annotations

import json
import math

import yaml

from ..build import BUILD, git_hash
from ..partsdb import ROOT
from ..trailer import Trailer
from . import sheet as S

def water_without_gcm_revision(rep) -> int:
    """The LandCruiser's fallback water limit if Lovells' GCM revision was refused (decision H20). The Ranger Super Duty
    has Ford's 8,000 kg GCM and no fallback, so GCM-01 gives the travel water itself here. No sheet calls this any more."""
    return next(c for c in rep["checks"] if c["id"] == "GCM-01")["gcm"]["water_without"]

OUT = BUILD / "drawings"

# line styles for the services sheets, added to the sheet's set
S.Sheet.STY.update({
    "dc": 'stroke="#000" stroke-width="0.6" fill="none"',
    "bus": 'stroke="#1f4e9c" stroke-width="0.35" fill="none" stroke-dasharray="2.2,0.8"',
    "ac": 'stroke="#b00000" stroke-width="0.4" fill="none" stroke-dasharray="4,1"',
    "pv": 'stroke="#000" stroke-width="0.35" fill="none" stroke-dasharray="0.8,0.8"',
    "cold": 'stroke="#1f4e9c" stroke-width="0.45" fill="none"',
    "hot": 'stroke="#c00000" stroke-width="0.45" fill="none"',
    "drain": 'stroke="#6b4a1a" stroke-width="0.55" fill="none" stroke-dasharray="3,0.8"',
    "air": 'stroke="#1a7a3a" stroke-width="0.4" fill="none"',
    "airx": 'stroke="#8a5a00" stroke-width="0.4" fill="none" stroke-dasharray="2,0.8"',
    "light": 'fill="#ececec" stroke="#000" stroke-width="0.25"',
    "tint": 'fill="#ececec" stroke="none"',
    "box": 'fill="#fff" stroke="#000" stroke-width="0.35"',
})

_CTX: dict = {}


def ctx(prj) -> dict:
    """The solved layout (bed up and bed down), the trailer and body results and the services data, built once per run."""
    if "rep" not in _CTX:
        rep = json.loads((BUILD / "trailer" / "trailer.json").read_text())
        res = json.loads((BUILD / "body" / "body.json").read_text())
        tr = Trailer(prj)
        ov = rep["solved"]["overrides"]
        day = tr.layout(**ov)
        night = tr.layout(**{**ov, "bed_state": 1})
        svc = yaml.safe_load((ROOT / "data" / "services.yaml").read_text())
        ute = json.loads((BUILD / "ute" / "ute.json").read_text())
        _CTX.update(rep=rep, res=res, tr=tr, day=day, night=night, V=day.V, svc=svc, ute=ute,
                    chk={c["id"]: c for c in rep["checks"]}, cases={c["id"]: c for c in rep["cases"]})
    return _CTX


def title(sh, dwg, reg, mass_note, material, model_ref="trailer.step (ASM-TR rev J)", weld_note=None, rows=7):
    rev = dwg["revisions"][-1]
    S.title_block(
        sh, owner=reg["owner"], project=dwg.get("project") or reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"], engineer="NOT REVIEWED", sheet_no=dwg["sheet"], sheets=reg["sheets_total"],
        size=dwg["size"], scale=dwg["scale"], material=material, mass_note=mass_note, model_ref=model_ref, git=git_hash(),
        weld_note=weld_note)
    return S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                                      checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]], max_rows=rows)


def stamp(sh, x, y, text, w=100.0):
    sh.rect(x - w / 2, y - 6, x + w / 2, y + 6, "fail")
    sh.text(x, y - 1.7, text, 2.0, "middle", bold=True, color="#c00")


def write(sh, dwg):
    S.write(sh, OUT / f"{dwg['number']}.svg")


def tw(s, size) -> float:
    """Rough width of a text on the sheet, mm (DejaVu Sans)."""
    up = sum(1 for c in str(s) if c.isupper() or c.isdigit())
    return size * (0.66 * up + 0.55 * (len(str(s)) - up))


def wrap(s, n) -> list[str]:
    out, cur = [], ""
    for w in str(s).split():
        if cur and len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])


def textblock(sh, x, y, lines, size=1.6, gap=0.9, bold_first=False, anchor="start"):
    """Lines of text downwards from y. Returns the y below the last line."""
    for i, t in enumerate(lines):
        sh.text(x, y, t, size, anchor, bold=bold_first and i == 0)
        y -= size + gap
    return y


def wtable(sh, x, y, cols, rows, size=1.3, title=None, gap=0.65, header=True):
    """A ruled table whose cells wrap to their column width, so a row is as tall as its longest cell. cols: (header,
    width mm). A cell may be (text, colour). Returns the y below the table."""
    w = sum(c[1] for c in cols)
    if title:
        sh.text(x, y + 1.5, title, 2.2, bold=True)
    lh = size + gap

    def cells(r):
        out = []
        for (h, cw), v in zip(cols, r):
            col = "#000"
            if isinstance(v, tuple):
                v, col = v
            n = max(4, int((cw - 1.4) / (size * 0.56)))
            out.append((wrap(v, n) or [""], col))
        return out

    allrows = ([[(h, "#000") for h, _ in cols]] if header else []) + list(rows)
    yy = y
    top = y
    for i, r in enumerate(allrows):
        cs = cells(r)
        hgt = max(len(t) for t, _ in cs) * lh + 0.9
        cx = x
        for (lines, col), (h, cw) in zip(cs, cols):
            for j, t in enumerate(lines):
                sh.text(cx + 0.7, yy - 0.5 - size * 0.85 - j * lh, t, size, bold=header and i == 0, color=col, cell=True)
            cx += cw
        yy -= hgt
        sh.line(x, yy, x + w, yy, "thin")
    sh.rect(x, yy, x + w, top, "medium")
    cx = x
    for h, cw in cols[:-1]:
        cx += cw
        sh.line(cx, top, cx, yy, "thin")
    return yy


def box(sh, x0, y0, x1, y1, lines, size=1.35, sty="box", bold_first=True, gap=0.6):
    """A labelled box for the schematics: its lines centred, the first in bold."""
    sh.fillrect(x0, y0, x1, y1, sty)
    n = len(lines)
    lh = size + gap
    y = (y0 + y1) / 2 + (n - 1) * lh / 2 - 0.36 * size
    for i, t in enumerate(lines):
        sh.text((x0 + x1) / 2, y - i * lh, t, size, "middle", bold=bold_first and i == 0)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def wire(sh, pts, sty="dc", label=None, at=0, dx=0.8, dy=0.6, size=1.2, anchor="start", arrow=False):
    """A schematic line through pts, with an optional label beside segment `at` and an arrow at the end."""
    sh.path(pts, sty)
    if arrow and len(pts) > 1:
        (a, b), (c, d) = pts[-2], pts[-1]
        L = math.hypot(c - a, d - b) or 1
        sh.arrow((c, d), ((c - a) / L, (d - b) / L), 1.8, 0.45)
    if label:
        (a, b), (c, d) = pts[at], pts[at + 1]
        sh.text((a + c) / 2 + dx, (b + d) / 2 + dy, label, size, anchor)


# ------------------------------------------------------------------ short names for the items on the sheets
SHORT = {
    "LA-09": "DESK", "LA-11T": "TOWER", "LA-03": "COMBI", "LA-05": "FRIDGE", "LA-13": "OVEN", "LA-11B": "BENCH",
    "LA-06": "FREEZER", "LA-07A": "HOB", "LA-07B": "SINK", "EL-02": "BATTERY BOX", "EL-01": "BATTERY", "LA-14F": "MACHINE BASE",
    "LA-02": "WASHER", "LA-14": "DRYER", "LA-11L": "LOCKERS", "LA-11E": "BOARD", "EL-04": "INVERTER", "AC-01": "SPLIT INDOOR",
    "AC-02": "SPLIT OUTDOOR", "AC-03": "CRADLE", "VE-01A": "e2 A", "VE-01B": "e2 B", "VE-01C": "e2 C", "VE-01D": "e2 D",
    "VE-03": "EXTRACT", "VE-04": "RESPA", "VE-05": "TOP-UP FAN", "VE-07": "HOOD", "WR-03": "PARTITION", "WR-01": "WET ROOM TRAY",
    "WR-06": "TOILET", "WR-07": "CASSETTES", "WR-08": "BASIN", "WR-09": "SHOWER UNIT", "WR-10": "WELL", "WR-11": "GREY TOTE",
    "LB-01": "MATTRESS", "LB-02": "UNDERLAY", "LB-03": "BED PLATFORM", "UF-01": "FRESH TANK", "UF-01R": "FRESH TANK",
    "UF-03": "TANK GUARD", "UF-06": "HEATER FUEL", "UF-08": "GREY TANK", "UF-09": "GREY GUARD", "DX-01": "DRAWBAR BOX",
    "GS-01": "GENERATORS", "GS-04": "JERRY CANS", "PL-03A": "SHELF", "SP-01": "SPARE", "BD-07": "ENTRY DOOR",
    "BD-15": "REAR DOOR", "BD-17": "CASSETTE DOOR", "RG-03": "TSC", "RG-04": "AIR SUPPLY",
}


def short(b) -> str:
    if b.iid in SHORT:
        return SHORT[b.iid]
    if b.id in SHORT:
        return SHORT[b.id]
    return " ".join(b.name.split(",")[0].split()[:2]).upper()


def label_in(sh, r, text, size=1.4, min_size=1.0, pad=0.6, rot_ok=True, avoid=()) -> bool:
    """Write text centred in the sheet rectangle r = (x0, y0, x1, y1) if it fits, shrinking to min_size, or rotated in a
    tall narrow box. A label that would cover a sheet point in `avoid` (a mark drawn later, such as a run tag's dot)
    slides along its length to the nearest place in the rectangle clear of it. The label names the rectangle, so one
    that clear_labels moves out of it gets a leader into it. Returns whether it was written."""
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    s = size
    while s >= min_size - 1e-9:
        if tw(text, s) + 2 * pad <= w and s + pad <= h:
            cy = (y0 + y1) / 2
            near = [p[0] for p in avoid if abs(p[1] - cy) < s / 2 + 0.4]
            sh.text(_slide((x0 + x1) / 2, tw(text, s), x0 + pad, x1 - pad, near), cy - 0.36 * s, text, s, "middle", names=r)
            return True
        if rot_ok and tw(text, s) + 2 * pad <= h and s + pad <= w:
            cx = (x0 + x1) / 2
            near = [p[1] for p in avoid if abs(p[0] - cx) < s / 2 + 0.4]
            sh.text(cx + 0.36 * s, _slide((y0 + y1) / 2, tw(text, s), y0 + pad, y1 - pad, near), text, s, "middle", rot=-90, names=r)
            return True
        s -= 0.1
    return False


def _slide(c: float, length: float, lo: float, hi: float, pts: list, clear: float = 0.4) -> float:
    """The middle nearest c, from lo to hi, of a label `length` long whose span keeps `clear` mm from the points (each
    point given along the label's length). Where no place clears them all, the label stays at c."""
    def free(m):
        return all(abs(p - m) > length / 2 + clear for p in pts)
    for k in range(int((hi - lo) / 0.25) + 1):
        for m in ((c,) if k == 0 else (c - 0.25 * k, c + 0.25 * k)):
            if lo + length / 2 - 1e-9 <= m <= hi - length / 2 + 1e-9 and free(m):
                return m
    return c


def cog_symbol(sh, x, y, r=1.4):
    sh.circle(x, y, r, "medium")
    sh.el.append(f'<path d="M{x:.2f},{sh._y(y):.2f} L{x + r:.2f},{sh._y(y):.2f} A{r:.2f},{r:.2f} 0 0,0 {x:.2f},{sh._y(y + r):.2f} Z" fill="#000"/>')
    sh.el.append(f'<path d="M{x:.2f},{sh._y(y):.2f} L{x - r:.2f},{sh._y(y):.2f} A{r:.2f},{r:.2f} 0 0,0 {x:.2f},{sh._y(y - r):.2f} Z" fill="#000"/>')


def arrow_line(sh, p0, p1, sty="medium", head=2.0):
    sh.line(p0[0], p0[1], p1[0], p1[1], sty)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1
    sh.arrow(p1, ((p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L), head, 0.45)


# ------------------------------------------------------------------ projections
class Proj:
    """DIM-01 to the sheet at 1:k. kind: plan (X right, Y up), kerb (seen from the kerb side, X right), road (seen from
    the road side, front on the right), front (seen from ahead, kerb side on the right) and rear (seen from behind,
    road side on the right). The model point `ref` lands at (ox, oy)."""
    AX = {"plan": ((1, 0, 0), (0, 1, 0)), "kerb": ((1, 0, 0), (0, 0, 1)), "road": ((-1, 0, 0), (0, 0, 1)),
          "front": ((0, -1, 0), (0, 0, 1)), "rear": ((0, 1, 0), (0, 0, 1))}

    def __init__(self, sh, kind, k, ox, oy, ref=(0.0, 0.0, 0.0)):
        self.sh, self.kind, self.k, self.ox, self.oy, self.ref = sh, kind, float(k), ox, oy, ref
        self.r, self.u = self.AX[kind]

    def p(self, x, y=0.0, z=0.0):
        d = (x - self.ref[0], y - self.ref[1], z - self.ref[2])
        return (self.ox + sum(a * b for a, b in zip(self.r, d)) / self.k, self.oy + sum(a * b for a, b in zip(self.u, d)) / self.k)

    def rect3(self, b):
        a, c = self.p(b[0], b[1], b[2]), self.p(b[3], b[4], b[5])
        return (min(a[0], c[0]), min(a[1], c[1]), max(a[0], c[0]), max(a[1], c[1]))

    def box(self, b, sty="medium"):
        r = self.rect3(b)
        self.sh.rect(*r, sty)
        return r

    def fill(self, b, sty="shade"):
        r = self.rect3(b)
        self.sh.fillrect(*r, sty)
        return r

    def line(self, a, b, sty="thin"):
        p, q = self.p(*a), self.p(*b)
        self.sh.line(p[0], p[1], q[0], q[1], sty)

    def poly(self, pts, sty="thin", closed=False):
        self.sh.path([self.p(*q) for q in pts], sty, closed)

    def text(self, pt, s, size=1.5, anchor="middle", **kw):
        p = self.p(*pt)
        self.sh.text(p[0], p[1] - 0.36 * size, s, size, anchor, **kw)

    def arc_plan(self, cx, cy, r, a0, a1, sty="thin", n=24):
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), 0)
               for i in range(n + 1)]
        self.poly(pts, sty)


def block_box(b):
    """A block's box, or a 200 mm cube round its point when it has none."""
    if b.box is not None:
        return b.box
    c = b.cog
    return (c[0] - 100, c[1] - 100, c[2] - 100, c[0] + 100, c[1] + 100, c[2] + 100) if c else None


# ------------------------------------------------------------------ the body's inside in plan
DOORS = {"BD-07": "hinge_front", "BD-15": "hinge_kerb"}


def body_plan(sh, pr, lay, res, cut=1000.0, show=None, labels=True, size=1.35, keep=True, openings=True, swings=True,
              open_labels=True, light=(), hidden=(), nolabel=(), avoid=()):
    """The body cut at `cut` above the floor, seen from above: the walls and the partition shaded, the openings in them,
    the door swings, the items in `show` (outlined, dashed when wholly above the cut or named in `hidden`) and the spaces
    kept clear (phantom). The openings' marks keep clear of the sheet points in `avoid` (symbols drawn later). Returns a
    dict of the item rectangles on the sheet by line."""
    V = lay.V
    hb, hi = V["half_bw"], V["half_in"]
    x0, x1, i0, i1 = V["body_x0"], V["body_x1"], V["in_x0"], V["in_x1"]
    zc = V["floor_z"] + cut
    for b in ((x0, hi, 0, x1, hb, 0), (x0, -hb, 0, x1, -hi, 0), (x0, -hi, 0, i0, hi, 0), (i1, -hi, 0, x1, hi, 0)):
        pr.fill(b)
    wr = lay.find("WR-03").box
    pr.fill((wr[0], -hi, 0, wr[3], hi, 0))
    # the inner door in the partition: 620 leaf, opens into the wet room's walk band (layout study 2.3)
    k5 = lay.find("LA-K5").box
    d0, d1 = k5[1], k5[4]
    pr.fill((wr[0] - 0.5, d0, 0, wr[3] + 0.5, d1, 0), "white")
    if swings:
        pr.line((wr[3], d0, 0), (wr[3] + (d1 - d0), d0, 0), "medium")
        pr.arc_plan(wr[3], d0, d1 - d0, 90, 0, "thin")
    out = {}
    if openings:
        placed: list = list(avoid)
        for o in res["openings"]:
            _opening_plan(sh, pr, lay, o, swings=swings, label=open_labels, placed=placed)
    picked = []
    for b in lay.blocks:
        if b.box is None or b.keep_clear or (show is not None and b.iid not in show and b.id not in show):
            continue
        if show is None and (b.zone != "inside" or b.system not in ("bed", "living", "electrical", "hvac", "wet_room")):
            continue
        picked.append(b)
    for b in picked:                 # the tints first, so no fill hides another item's outline or label
        if b.iid in light or b.id in light:
            sh.fillrect(*pr.rect3(b.box), "tint")
    for b in picked:
        above = b.box[2] > zc + 1e-6 or b.iid in hidden or b.id in hidden
        r = pr.rect3(b.box)
        sh.rect(*r, "hidden" if above else "medium")
        out[b.iid] = r
    for b in picked:
        if labels and b.iid not in nolabel and b.id not in nolabel:
            label_in(sh, out[b.iid], short(b), size, avoid=avoid)
    if keep:
        for b in (b for b in lay.blocks if b.keep_clear):
            r = pr.rect3(b.box)
            sh.rect(*r, "phantom")
            out[b.iid] = r
    return out


def _opening_plan(sh, pr, lay, o, swings=True, label=True, placed=None):
    V = lay.V
    hb, hi = V["half_bw"], V["half_in"]
    x0, x1, i0, i1 = V["body_x0"], V["body_x1"], V["in_x0"], V["in_x1"]
    w = o["wall"]
    if w in ("kerb", "road"):
        a, b = x0 + o["u0"], x0 + o["u1"]
        ya, yb = (-hb, -hi) if w == "kerb" else (hi, hb)
        box = (a, ya, 0, b, yb, 0)
    else:
        a, b = o["u0"], o["u1"]
        xa, xb = (x0, i0) if w == "front" else (i1, x1)
        box = (xa, a, 0, xb, b, 0)
    r = pr.fill(box, "white")
    line = o.get("line") or ""
    if line.startswith("WN-"):
        for f in (0.35, 0.65):
            if w in ("kerb", "road"):
                y = box[1] + f * (box[4] - box[1])
                pr.line((a, y, 0), (b, y, 0), "thin")
            else:
                x = box[0] + f * (box[3] - box[0])
                pr.line((x, a, 0), (x, b, 0), "thin")
        sh.rect(*r, "thin")
    elif line in DOORS:
        if swings:
            if w == "kerb":            # hinged on its front edge, opens outward (-Y)
                L = b - a
                pr.line((a, -hb, 0), (a, -hb - L, 0), "medium")
                pr.arc_plan(a, -hb, L, 0, -90, "thin")
            elif w == "rear":          # hinged on its kerb edge, opens outward (+X)
                L = b - a
                pr.line((x1, a, 0), (x1 + L, a, 0), "medium")
                pr.arc_plan(x1, a, L, 90, 0, "thin")
    else:
        sh.rect(*r, "thin")
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        sh.line(r[0], r[1], r[2], r[3], "thin")
        sh.line(r[0], r[3], r[2], r[1], "thin")
    if label:
        m = MARK.get(line, o["id"])
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        off = {"kerb": (0, -2.6), "road": (0, 1.2), "front": (-1.2, 0), "rear": (1.2, 0)}[w]
        anchor = {"kerb": "middle", "road": "middle", "front": "end", "rear": "start"}[w]
        if line in DOORS and w == "kerb":
            off = (3.0, -2.6)
        tx, ty = cx + off[0], cy + off[1] - (0.5 if w in ("front", "rear") else 0)
        if placed is not None:
            step = (0, 2.3) if w in ("front", "rear") else (2.6, 0)
            while any(abs(tx - a) < 2.4 and abs(ty - b) < 2.0 for a, b in placed):
                tx, ty = tx + step[0], ty + step[1]
            placed.append((tx, ty))
        sh.text(tx, ty, m, 1.4, anchor, bold=True)


# marks for the openings, by their mass schedule line (layout study section 5)
MARK = {"WN-01": "W1", "WN-02": "W2", "WN-03": "W4", "WN-04": "W6", "BD-07": "D1", "BD-15": "D2", "BD-17": "S1",
        "VE-01A": "V1", "VE-04": "V2", "VE-07": "V3", "LA-03": "V4", "VE-01B": "V5", "VE-01C": "V6", "VE-01D": "V7",
        "VE-06": "V8", "VE-03": "V9", "WR-05": "R1"}


def opening_margins(lay, res, rules) -> dict:
    """Each opening's tightest gap under report 12's rules (data/body/body.yaml): to its nearest neighbour on the same
    wall (300 mm of full wall, or 300 mm apart in height where they share no band), to a panel edge or the roof (150 mm)
    and, on the side walls, to the rear corner zone (300 mm). The same arithmetic as the body's BDY-18 check."""
    V = lay.V
    L, H = V["body_length"], V["interior_h"]
    ops = res["openings"]
    out = {o["id"]: dict(gap=math.inf, what="", rule=0.0) for o in ops}

    def put(oid, margin, gap, what, rule):
        if margin < out[oid]["gap"] - out[oid]["rule"]:
            out[oid].update(gap=gap, what=what, rule=rule)

    for wall in ("kerb", "road", "front", "rear"):
        w = sorted((o for o in ops if o["wall"] == wall), key=lambda o: o["u0"])
        lo, hi = (0.0, L) if wall in ("kerb", "road") else (-V["half_in"], V["half_in"])
        for o in w:
            cands = [(o["u0"] - lo, "panel edge", rules["edge_mm"]), (hi - o["u1"], "panel edge", rules["edge_mm"]),
                     (H - o["z1"], "roof", rules["edge_mm"])]
            if wall in ("kerb", "road"):
                cands.append(((hi - rules["rear_corner_mm"]) - o["u1"] + rules["edge_mm"], "rear corner rule", rules["edge_mm"]))
            for g, what, rule in cands:
                put(o["id"], g - rule, g, what, rule)
        for i, a in enumerate(w):
            for b in w[i + 1:]:
                overlap_z = min(a["z1"], b["z1"]) - max(a["z0"], b["z0"])
                du = b["u0"] - a["u1"]
                dz = max(b["z0"] - a["z1"], a["z0"] - b["z1"])
                gap = du if overlap_z > 0 else (max(du, dz) if du > 0 else dz)
                put(a["id"], gap - rules["between_mm"], gap, MARK.get(b.get("line"), b["id"]), rules["between_mm"])
                put(b["id"], gap - rules["between_mm"], gap, MARK.get(a.get("line"), a["id"]), rules["between_mm"])
    return out

"""CT-106, the XT hinge joint and the rear tank bay's shear panel (A3), from the chassis data (cad/chassis.py).

Detail A draws the XT centre crossmember's kerb-side joint in plan and detail B in section on the rail's inner face,
both at 1:5: the rail, the crossmember's end, the two hinge cheeks, the two gussets on their 45 degree lines with their
cut ends on the crossmember and the rail, their welds and the jacking pad. Detail C draws the rear tank's bay in plan at
1:10 with the shear panel's angles, the 4 mm sheet and its tongues with their radiused roots and its bolts, and detail D a section
across the rail at the panel at 1:2.5. Nothing here places a part: every line is read from Chassis.hinge_gussets,
hinge_cheeks, panel_pieces and shear_panels and the data they read, so a part the chassis code moves moves here.
Cruisemaster's hinge bar is drawn phantom, its size estimated.
"""
from __future__ import annotations

import math
import time

from . import sheet as S
from .chassis_sheets import OUT, _chassis, _draft_stamp, _layout, _title, plate, rhs, weld_symbol
from .hole_sheet import _aligned

LABEL = 1.5         # the details' label size, mm


class View:
    """World to sheet at 1:k: the world point (a, b) at sheet (x0, y0), a along the sheet's x times sa and b along its
    y times sb."""

    def __init__(self, x0, y0, a0, b0, k, sa=1.0, sb=1.0):
        self.x0, self.y0, self.a0, self.b0, self.k, self.sa, self.sb = x0, y0, a0, b0, k, sa, sb

    def p(self, a, b):
        return (self.x0 + self.sa * (a - self.a0) / self.k, self.y0 + self.sb * (b - self.b0) / self.k)

    def line(self, sh, a0, b0, a1, b1, sty="medium"):
        sh.line(*self.p(a0, b0), *self.p(a1, b1), sty)

    def box(self, sh, a0, b0, a1, b1, sty="medium"):
        (x0, y0), (x1, y1) = self.p(a0, b0), self.p(a1, b1)
        sh.rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), sty)

    def solid(self, sh, a0, b0, a1, b1):
        (x0, y0), (x1, y1) = self.p(a0, b0), self.p(a1, b1)
        plate(sh, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def poly(self, sh, pts, sty="medium", closed=True):
        sh.path([self.p(a, b) for a, b in pts], sty, closed=closed)


def _n(v: float) -> str:
    return f"{round(float(v), 1):g}"


def _title_of(sh, cx, top, title, scale, note=""):
    sh.text(cx, top, title, 2.2, "middle", bold=True)
    sh.text(cx, top - 3.5, f"SCALE 1:{scale:g}", 1.9, "middle")
    if note:
        sh.text(cx, top - 6.4, note, LABEL, "middle")


def _brk(sh, p, q):
    """A thin break line from sheet point p to q, with one zigzag at its middle."""
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    L = math.dist(p, q) or 1.0
    ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
    nx, ny = -uy, ux
    sh.path([p, (mx - ux * 1.2, my - uy * 1.2), (mx - ux * 0.4 + nx * 1.6, my - uy * 0.4 + ny * 1.6),
             (mx + ux * 0.4 - nx * 1.6, my + uy * 0.4 - ny * 1.6), (mx + ux * 1.2, my + uy * 1.2), q], "thin")


class Joint:
    """The XT centre crossmember's kerb-side hinge joint as the data has it: the rail, the crossmember, the cheeks
    either side, the gussets either side, the jacking pad and the shear panel's angle along the rail behind it."""

    def __init__(self, ch):
        self.ch, V = ch, ch.V
        self.V = V
        self.rail, self.raiser = ch.role_sec["rail"], ch.role_sec["raiser"]
        self.cm = next(m for m in ch.members if m.station == "XT centre" and m.role == "cm_xt")
        self.x = self.cm.p0[0]
        self.front, self.rear = self.x - self.cm.sec.b / 2, self.x + self.cm.sec.b / 2
        self.y_in = V["rail_c"] - self.rail.b / 2
        self.y_out = V["rail_c"] + self.rail.b / 2
        self.z0, self.z1 = V["rail_underside_z"], V["rail_underside_z"] + self.rail.d
        self.cheeks = [c for c in ch.hinge_cheeks() if c["wheel"] == "RK"]
        self.gussets = [g for g in ch.hinge_gussets() if g["cm"] == self.cm.id and g["side"] < 0]
        self.gdata = ch.data["xt_hinges"]["gusset"]
        self.ck = ch.data["xt_hinges"]["cheek"]
        self.bar = ch.data["xt_hinges"]["bar"]
        pad = next(f for f in ch.data["fittings"] if f["id"] == "CH-P06")
        at = ch.ev(pad["at"])
        self.pad = (at[0] - pad["l"] / 2, -ch.ev(pad["side_y"]) - pad["w"] / 2, at[2] - pad["t"] / 2,
                    at[0] + pad["l"] / 2, -ch.ev(pad["side_y"]) + pad["w"] / 2, at[2] + pad["t"] / 2)
        self.pivot = next(w for w in ch.suspension if w["id"] == "RK")["pivot"]
        self.angle = next(p for p in ch.panel_pieces() if p["use"] == "rail" and p["side"] < 0)
        self.cm_leg = ch.data["member_galvanising_holes"]["cm_xt"]["leg"]


def _cheek_plan(J: Joint, c: dict) -> list[tuple[float, float]]:
    """A hinge cheek in plan (Chassis.hinge_cheeks), its end at the crossmember coped at 45 degrees on the web side,
    `cope` along the rail and the cheek's thickness across, clear of the crossmember's end fillet (I2-100)."""
    b, cope = c["box"], J.ck.get("cope", 0.0)
    y_web = b[1] if c["side"] < 0 else b[4]
    y_face = b[4] if c["side"] < 0 else b[1]
    x_end, sgn = c["face"], float(c["way"])
    x_far = x_end + sgn * c["l"]
    t = abs(y_face - y_web)
    return [(x_end + sgn * cope, y_web), (x_far, y_web), (x_far, y_face), (x_end + sgn * max(0.0, cope - t), y_face)]


def _plan_a(sh, J: Joint, x0: float, y0: float, k: float = 5.0):
    """Detail A: the joint in plan from above, X rearward to the right and the kerb rail at the foot, its lower left
    corner at sheet (x0, y0): the rail, the crossmember's end, the cheeks, the gussets with their axes, the jacking pad
    under the crossmember and the shear panel's angle along the web behind the cheek, hidden under the gusset."""
    lo, hi = J.front - 250.0, J.rear + 280.0
    v = View(x0, y0, lo, -J.y_out - 17.5, k)
    y_in, y_out = -J.y_in, -J.y_out
    top = -J.y_in + 255.0
    for y in (y_out, y_in):
        v.line(sh, lo, y, hi, y)
    for x in (lo, hi):
        _brk(sh, v.p(x, y_out - 4), v.p(x, y_in + 4))
    for x in (J.front, J.rear):
        v.line(sh, x, y_in, x, top)
    _brk(sh, v.p(J.front - 6, top), v.p(J.rear + 6, top))
    for c in J.cheeks:
        v.poly(sh, _cheek_plan(J, c))
    for g in J.gussets:
        v.poly(sh, g["outline"])
        d = g["dir"]
        v.line(sh, g["p0"][0] - 8 * d[0], g["p0"][1] - 8 * d[1], g["p1"][0] + 8 * d[0], g["p1"][1] + 8 * d[1], "centre")
    p = J.pad
    v.box(sh, p[0], p[1], p[3], p[4], "hidden")
    a = J.angle
    v.line(sh, a["x0"], y_in + 50, hi, y_in + 50, "hidden")
    v.line(sh, a["x0"], y_in, a["x0"], y_in + 50, "hidden")
    rear = next(g for g in J.gussets if g["face"] > 0)
    # the rail side's dimensions, under the rail: the cheek, the panel's angle beyond it, and the gusset's axis on the
    # cheek's face, where its rail end lands (I2-99)
    rb = next(c for c in J.cheeks if c["id"].endswith("B"))
    base_end = J.rear + J.ck["l"]
    step_end = J.rear + rb["l"]
    yb = v.p(0, y_out)[1]
    S.hdim(sh, *v.p(J.rear, y_in), *v.p(base_end, y_in), yb - 4.0, _n(J.ck["l"]), size=LABEL)
    S.hdim(sh, *v.p(base_end, y_in), *v.p(step_end, y_in), yb - 4.0, f"{_n(step_end - base_end)} STEP", size=LABEL)
    S.hdim(sh, *v.p(base_end, y_in), *v.p(a["x0"], y_in), yb - 8.5, f"{_n(a['x0'] - base_end)} TO CH-P17", size=LABEL)
    S.hdim(sh, *v.p(J.rear, y_in), *v.p(rear["p1"][0], y_in), yb - 13.0, f"{_n(rear['leg'])}, THE AXIS ON THE CHEEK", size=LABEL)
    _aligned(sh, v.p(*rear["p0"][:2]), v.p(*rear["p1"][:2]), 11.0, f"{_n(rear['length'])} ON THE AXIS", LABEL)
    c = v.p(rear["p1"][0] - 30.0, y_in)
    sh.text(c[0] - 3.0, c[1] + 2.0, "45 DEG", LABEL, "end")
    tip = v.p(rear["p1"][0], y_in)
    weld_symbol(sh, tip, (tip[0] + 6.0, tip[1] + 12.0), _n(J.gdata["weld"]["leg"]), all_round=True)
    tip = v.p(J.rear, 0.5 * (rear["outline"][0][1] + rear["outline"][1][1]))
    weld_symbol(sh, tip, (tip[0] + 12.0, tip[1] + 9.0), _n(J.gdata["weld"]["leg"]), all_round=True)
    tip = v.p(J.front, y_in + 40.0)
    weld_symbol(sh, tip, (tip[0] - 20.0, tip[1] + 6.0), _n(J.cm_leg), all_round=True, note="ALL ROUND")
    S.leader(sh, v.p(J.x, top - 20.0), (v.p(J.x, top)[0] + 6.0, v.p(J.x, top)[1] + 3.0),
             f"{J.cm.id} {J.cm.sec.name.replace(' x ', 'x')}", size=LABEL)
    fc = next(cc for cc in J.cheeks if cc["id"].endswith("F"))
    tip = v.p(0.5 * (fc["box"][0] + fc["box"][3]), fc["box"][4])
    S.leader(sh, tip, (tip[0] - 14.0, yb - 6.0), f"CHEEK {_n(fc['l'])}x{_n(fc['h'])}x{_n(J.ck['t'])}", size=LABEL)
    tip = v.p(p[0], 0.5 * (p[1] + p[4]))
    S.leader(sh, tip, (tip[0] - 14.0, tip[1] + 18.0), "JACKING PAD UNDER", ["CT-103 DETAIL G"], size=LABEL)
    sh.text(v.p(lo + 75.0, 0)[0], v.p(0, 0.5 * (y_in + y_out))[1] - 0.6, f"RAIL {_n(J.rail.d)}x{_n(J.rail.b)}x{_n(J.rail.t)}", LABEL, "middle")


def _section_b(sh, J: Joint, x0: float, y0: float, k: float = 5.0):
    """Detail B: the joint in section on the cheeks' inboard face, looking outboard, so X runs to the left and the front is
    on the right: the rail's inner web, the crossmember cut, the cheeks on the web, the gussets cut and their ends' welds
    on the web, Cruisemaster's hinge bar phantom (est.) and the shear panel's angle, its flat leg and the sheet cut."""
    lo, hi = J.front - 250.0, J.rear + 280.0
    v = View(x0, y0, hi, 470.0, k, sa=-1.0)
    z0, z1, ro = J.z0, J.z1, J.rail.ro
    v.box(sh, lo, z0, hi, z1)
    for z in (z0 + ro, z1 - ro):
        v.line(sh, lo, z, hi, z, "thin")
    v.line(sh, lo, z1 + 18.0, hi, z1 + 18.0, "thin")
    for x in (lo, hi):
        v.line(sh, x, z1, x, z1 + 18.0, "thin")
        _brk(sh, v.p(x, z0 - 4), v.p(x, z1 + 22))
    cx, cy = v.p(J.x, z0 + J.cm.sec.d / 2)
    rhs(sh, cx, cy, J.cm.sec.b, J.cm.sec.d, J.cm.sec.t, J.cm.sec.ro, k)
    for c in J.cheeks:
        for b in c["boxes"]:
            v.box(sh, b[0], b[2], b[3], b[5])
    bar_lo = J.pivot[2] - 25.0
    v.box(sh, J.front, bar_lo, J.rear, z0, "phantom")
    pc = v.p(J.pivot[0], J.pivot[2])
    sh.circle(pc[0], pc[1], 12.0 / k, "phantom")
    sh.line(pc[0] - 4.0, pc[1], pc[0] + 4.0, pc[1], "centre")
    sh.line(pc[0], pc[1] - 4.0, pc[0], pc[1] + 4.0, "centre")
    sec_t = J.ch.sections[next(f for f in J.ch.data["fittings"] if f["id"] == "CH-P08")["section"]].t
    for g in J.gussets:
        e, half = g["face"], 25.0
        u_a, u_b = g["leg"] - half * math.sqrt(2), g["leg"] + half * math.sqrt(2)
        for u in (u_a, u_b):
            v.line(sh, g["rear_x"] + e * u, g["z"] - half, g["rear_x"] + e * u, g["z"] + half)
        cut = J.ck["t"]
        for z in (g["z"] - half, g["z"] + half):
            v.line(sh, g["rear_x"] + e * (u_b - cut), z, g["rear_x"] + e * u_b, z)
        xa, xb = g["rear_x"] + e * (u_a - cut), g["rear_x"] + e * (u_b - cut)
        w = sec_t * math.sqrt(2)
        for za, zb in ((g["z"] + half - sec_t, g["z"] + half), (g["z"] - half, g["z"] - half + sec_t)):
            v.solid(sh, min(xa, xb), za, max(xa, xb), zb)
        for xe in (xa, xb - e * w):
            v.solid(sh, min(xe, xe + e * w), g["z"] - half, max(xe, xe + e * w), g["z"] + half)
    a = J.angle
    zf = a["boxes"][1][2]
    v.box(sh, a["x0"], zf, hi, zf + 50.0)
    v.solid(sh, a["x0"], zf, hi, zf + 5.0)
    panel = J.ch.shear_panels()[0]
    v.solid(sh, panel["sheet"]["front"], zf - panel["t"], hi, zf)
    # the cheeks' and the gussets' welds and dimensions, from the data
    rb = next(c for c in J.cheeks if c["id"].endswith("B"))["box"]
    top_mid = v.p(rb[0] + 75.0, rb[5])
    weld_symbol(sh, top_mid, (top_mid[0] - 4.0, top_mid[1] + 16.0), _n(J.ck["leg"]), note="TOP EDGE")
    fb = next(c for c in J.cheeks if not c["id"].endswith("B"))["box"]
    corner = v.p(fb[0] + 40.0, z0 + ro / 2)
    weld_symbol(sh, corner, (corner[0] + 5.0, corner[1] - 9.0), _n(J.ck["corner"] * ro), flare=True, note="RAIL CORNER")
    bar_tip = v.p(J.rear, z0 - J.ck["bar_d"] / 2)
    weld_symbol(sh, bar_tip, (bar_tip[0] + 9.0, bar_tip[1] - 11.0), _n(J.ck["bar_leg"]), both=True, length=_n(J.ck["bar_d"]),
                note="TO THE BAR")
    S.vdim(sh, *v.p(rb[3], rb[2]), *v.p(rb[3], rb[5]), v.p(rb[3], 0)[0] + 3.5, _n(J.ck["h"]), size=LABEL)
    S.vdim(sh, *v.p(rb[3], rb[2]), *v.p(rb[3], z0), v.p(rb[3], 0)[0] + 8.0, _n(J.ck["below"]), size=LABEL)
    g = next(g for g in J.gussets if g["face"] > 0)
    S.vdim(sh, *v.p(lo, z0), *v.p(lo, g["z"]), v.p(lo, 0)[0] - 4.0, _n(g["z"] - z0), size=LABEL)
    S.vdim(sh, *v.p(a["x0"], zf), *v.p(a["x0"], z0), v.p(a["x0"], 0)[0] + 4.0, _n(z0 - zf), size=LABEL)
    S.leader(sh, v.p(J.front + 10.0, bar_lo + 30.0), (v.p(J.front, 0)[0] + 10.0, v.p(0, bar_lo)[1] - 4.0),
             "CRUISEMASTER HINGE BAR, PHANTOM (est.)", size=LABEL)
    for x, t in ((hi, "REAR"), (lo, "FRONT")):
        q = v.p(x, z1 + 30.0)
        sh.text(q[0], q[1], t, LABEL, "middle")


def _sheet_outline(sheet: dict, steps: int = 6) -> list[tuple[float, float]]:
    """The shear panel's sheet in plan as one outline (Chassis.panel_sheet): its front edge with the front tongues, its
    side, its rear edge with the rear tongues, each tongue's two root corners radiused `root_r`."""
    x0, y0, x1, y1 = sheet["rect"]
    R = sheet["root_r"]

    def along(x: float, way: int) -> list[tuple[float, float]]:
        pts = []
        for r in sorted((r for r in sheet["roots"] if r["way"] == way and abs(r["x"] - x) < 1e-6), key=lambda r: r["y0"]):
            t = next(t for t in sheet["tongues"] if abs(t[1] - r["y0"]) < 1e-6 and abs(t[3] - r["y1"]) < 1e-6)
            toe = t[0] if way < 0 else t[2]
            c0, c1 = (x + way * R, r["y0"] - R), (x + way * R, r["y1"] + R)
            arc0 = [(c0[0] - way * R * math.cos(math.radians(a)), c0[1] + R * math.sin(math.radians(a))) for a in range(0, 91, 90 // steps)]
            arc1 = [(c1[0] - way * R * math.sin(math.radians(a)), c1[1] - R * math.cos(math.radians(a))) for a in range(0, 91, 90 // steps)]
            pts += (arc0 if R else [(x, r["y0"])]) + [(toe, r["y0"]), (toe, r["y1"])] + (arc1 if R else [(x, r["y1"])])
        return pts

    return [(x0, y0)] + along(x0, -1) + [(x0, y1), (x1, y1)] + list(reversed(along(x1, 1))) + [(x1, y0)]


def _bay_c(sh, J: Joint, x0: float, y0: float, k: float = 10.0) -> tuple:
    """Detail C: the rear tank's bay in plan from above at 1:10, X rearward to the right: both rails, the XT centre and XT
    rear shock crossmembers, the cheeks and gussets at the XT centre, the shear panel's angles along the rails and under
    the crossmembers, the sheet with its tongues, their root corners radiused, and its bolts. Returns the
    sheet points of section D's cutting plane."""
    ch, V = J.ch, J.V
    shock = next(m for m in ch.members if m.station == "XT rear shock")
    lo, hi = J.front - 48.0, shock.p0[0] + shock.sec.b / 2 + 42.0
    v = View(x0, y0, lo, -650.0, k)
    for s in (-1, 1):
        for y in (s * J.y_in, s * J.y_out):
            v.line(sh, lo, y, hi, y)
        for x in (lo, hi):
            _brk(sh, v.p(x, s * J.y_out + s * 4), v.p(x, s * J.y_in - s * 4))
    for m in (J.cm, shock):
        for x in (m.p0[0] - m.sec.b / 2, m.p0[0] + m.sec.b / 2):
            v.line(sh, x, -J.y_in, x, J.y_in)
    for c in ch.hinge_cheeks():
        b = c["box"]
        if lo <= b[0] <= hi:
            v.poly(sh, _cheek_plan(J, c))
    for g in ch.hinge_gussets():
        if g["cm"] == J.cm.id and g["face"] > 0:
            v.poly(sh, g["outline"])
    pieces = ch.panel_pieces()
    for p in pieces:
        if p["use"] == "rail":
            yt = p["side"] * (J.y_in - 50.0)
            v.line(sh, p["x0"], yt, p["x1"], yt)
            for x in (p["x0"], p["x1"]):
                v.line(sh, x, p["side"] * J.y_in, x, yt)
        elif p["use"] == "crossmember":
            b = p["boxes"][1]
            v.box(sh, b[0], b[1], b[3], b[4], "hidden")
    sp = ch.shear_panels()[0]
    r = sp["sheet"]["rect"]
    v.poly(sh, _sheet_outline(sp["sheet"]), "thin")
    for b in sp["bolts"]:
        q = v.p(b["x"], b["y"])
        sh.circle(q[0], q[1], sp["fixing"]["hole"] / 2 / k + 0.15, "medium")
    # dimensions over the road rail and beside the bay
    ytop = v.p(0, J.y_out)[1]
    xa, xb = J.rear, shock.p0[0] - shock.sec.b / 2
    S.hdim(sh, *v.p(xa, J.y_out), *v.p(xb, J.y_out), ytop + 4.0, f"{_n(xb - xa)} BAY", size=LABEL)
    rail_angle = next(p for p in pieces if p["use"] == "rail" and p["side"] > 0)
    S.hdim(sh, *v.p(rail_angle["x0"], J.y_out), *v.p(rail_angle["x1"], J.y_out), ytop + 8.5, f"{_n(rail_angle['length'])} ANGLE", size=LABEL)
    xr = v.p(hi, 0)[0]
    S.vdim(sh, *v.p(r[2], r[1]), *v.p(r[2], r[3]), xr + 5.0, f"{r[3] - r[1]:,.0f} SHEET", size=LABEL)
    fix = sp["fixing"]
    front = [b for b in sp["bolts"] if b["group"] == "front"]
    q = v.p(front[0]["x"], front[-1]["y"])
    S.leader(sh, q, (q[0] - 9.0, q[1] + 12.0), f"{len(front)} M{_n(fix['d'])} AT {_n(fix['front_pitch'])}", size=LABEL)
    rb = next(b for b in sp["bolts"] if b["group"] == "rail" and b["y"] < 0)
    q = v.p(rb["x"], rb["y"])
    S.leader(sh, q, (q[0] + 6.0, q[1] + 16.0), f"M{_n(fix['d'])} AT {_n(fix['pitch'])}", size=LABEL)
    front_root = next(q for q in sp["sheet"]["roots"] if q["way"] < 0)
    R = sp["sheet"]["root_r"]
    q = v.p(front_root["x"] - R + R / math.sqrt(2), front_root["y1"] + R - R / math.sqrt(2))
    S.leader(sh, q, (q[0] + 7.0, q[1] + 8.0), f"R{_n(R)} AT EACH TONGUE'S ROOT", size=LABEL)
    q = v.p(0.5 * (r[0] + r[2]) + 120.0, -200.0)
    sh.text(q[0], q[1], f"{_n(sp['t'])} SHEET {sp['id']}", LABEL, "middle")
    x_cut = rail_angle["x0"] + 0.5 * rail_angle["length"]
    return v.p(x_cut, -J.y_out - 20.0), v.p(x_cut, -J.y_in + 90.0), x_cut


def _section_d(sh, J: Joint, x0: float, y0: float, k: float = 2.5):
    """Section D: across the kerb rail at the shear panel, looking rearward, so the kerb side is on the right: the rail and
    its raiser, the panel's angle with its upright leg on the web and its flat leg 26 mm under the rail, its two welds,
    the sheet under the flat leg and an M10 bolt on the leg's gauge."""
    ch = J.ch
    spec = next(f for f in ch.data["fittings"] if f["id"] == "CH-P17")
    v = View(x0, y0, -500.0, 555.0, k, sa=-1.0)
    rail, raiser = J.rail, J.raiser
    cx, cy = v.p(-ch.V["rail_c"], J.z0 + rail.d / 2)
    rhs(sh, cx, cy, rail.b, rail.d, rail.t, rail.ro, k)
    top = J.z1 + 24.0
    for y in (-ch.V["rail_c"] - raiser.b / 2, -ch.V["rail_c"] + raiser.b / 2):
        v.line(sh, y, J.z1, y, top)
    _brk(sh, v.p(-ch.V["rail_c"] - raiser.b / 2 - 4, top), v.p(-ch.V["rail_c"] + raiser.b / 2 + 4, top))
    a = J.angle
    up, flat = a["boxes"]
    v.solid(sh, up[1], up[2], up[4], up[5])
    v.solid(sh, flat[1], flat[2], flat[4], flat[5])
    zf = flat[2]
    panel = ch.shear_panels()[0]
    sheet, ts = panel["sheet"], panel["t"]
    v.solid(sh, -sheet["half"], zf - ts, -505.0, zf)
    _brk(sh, v.p(-505.0, zf - 8.0), v.p(-505.0, zf + 6.0))
    leg = spec["weld"]["leg"]
    y_web = -J.y_in
    sh.path([v.p(y_web, up[5]), v.p(y_web, up[5] + leg), v.p(y_web + leg, up[5])], "fill", closed=True)
    r = rail.ro
    arc = [(y_web - r + r * math.cos(math.radians(t)), J.z0 + r - r * math.sin(math.radians(t))) for t in range(0, 61, 15)]
    sh.path([v.p(y_web, J.z0 + r)] + [v.p(*q) for q in arc] + [v.p(y_web, arc[-1][1])], "fill", closed=True)
    fix = ch.data["shear_panels"][0]["fixing"]
    yb = y_web + spec["gauge"]
    for zz0, zz1, w in ((zf - ts - 6.4, zf - ts, 16.0), (flat[5], flat[5] + 8.4, 16.0)):
        v.box(sh, yb - w / 2, zz0, yb + w / 2, zz1, "medium")
    v.box(sh, yb - fix["d"] / 2, zf - ts, yb + fix["d"] / 2, flat[5], "thin")
    v.line(sh, yb, zf - 14.0, yb, flat[5] + 13.0, "centre")
    # the welds' symbols and the dimensions from the data
    tip = v.p(y_web, up[5] + leg / 2)
    weld_symbol(sh, tip, (tip[0] + 10.0, tip[1] + 11.0), _n(leg), length=_n(a["length"]), note="TOP EDGE")
    tip = v.p(y_web - 2.0, J.z0 + 2.0)
    weld_symbol(sh, tip, (tip[0] + 12.0, tip[1] - 14.0), _n(spec["weld"]["corner_throat"]), flare=True, note="FLARE BEVEL")
    S.vdim(sh, *v.p(-J.y_out, J.z0), *v.p(-J.y_out, zf), v.p(-J.y_out, 0)[0] + 6.0, _n(J.z0 - zf), size=LABEL)
    S.hdim(sh, *v.p(y_web, zf), *v.p(yb, zf), v.p(0, zf - 3.0 - 6.4)[1] - 5.0, _n(spec["gauge"]), size=LABEL)
    S.hdim(sh, *v.p(-sheet["half"], zf - 3.0), *v.p(yb, zf - 3.0), v.p(0, zf - 3.0 - 6.4)[1] - 10.0, _n(yb + sheet["half"]), size=LABEL)
    q = v.p(-530.0, zf - 1.5)
    S.leader(sh, q, (q[0] - 4.0, q[1] - 12.0), f"{_n(ch.data['shear_panels'][0]['t'])} SHEET", size=LABEL)
    q = v.p(-545.0, flat[5])
    S.leader(sh, q, (q[0] - 6.0, q[1] + 12.0), "EA 50x50x5", size=LABEL)


def _parts(sh, J: Joint, x: float, y: float) -> float:
    """The parts this sheet details, from the chassis's fittings and the panel's pieces: mark, what, size, length, count
    and mass."""
    ch = J.ch
    fit = {f.id: f for f in ch.fittings}
    g = J.gussets[0]
    sec = ch.sections[next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
    rows = [["CH-P08", "HINGE GUSSET, BOTH ENDS CUT AT 45 DEG", sec.name.replace(" x ", "x"), _n(g["length"]), str(fit["CH-P08"].qty),
             f"{fit['CH-P08'].mass_each:.2f}"],
            ["CH-P16", "HINGE CHEEK, SHORT, FRONT HINGE'S FRONT", f"PL {_n(J.ck['l'])}x{_n(J.ck['h'])}x{_n(J.ck['t'])}", "",
             str(sum(1 for c in ch.hinge_cheeks() if not c["gusset"])), f"{J.ck['l'] * J.ck['h'] * J.ck['t'] * 7.85e-6:.2f}"],
            ["CH-P16", "HINGE CHEEK, A GUSSET LANDS ON ITS STEP", f"PL {_n(J.ck['under_gusset']['l'])}x{_n(J.ck['under_gusset']['h'])}x{_n(J.ck['t'])}", "",
             str(sum(1 for c in ch.hinge_cheeks() if c["gusset"])),
             f"{next(sum((b[3] - b[0]) * (b[5] - b[2]) for b in c['boxes']) for c in ch.hinge_cheeks() if c['gusset']) * J.ck['t'] * 7.85e-6:.2f}"]]
    seen = {}
    for p in ch.panel_pieces():
        key = (p["use"], p["section"], round(p["length"]))
        seen.setdefault(key, [p, 0])[1] += 1
    words = {"rail": "PANEL ANGLE ALONG A RAIL", "crossmember": "PANEL ANGLE UNDER A CROSSMEMBER"}
    for (use, sid, _), (p, n) in seen.items():
        rows.append(["CH-P17", words[use], sid.replace("_", " ").replace("EA ", "EA "), _n(p["length"]), str(n), f"{p['mass_kg']:.2f}"])
    pad = next(f for f in ch.data["fittings"] if f["id"] == "CH-P06")
    rows.append(["CH-P06", "JACKING PAD, CT-103 DETAIL G", f"PL {_n(pad['l'])}x{_n(pad['w'])}x{_n(pad['t'])}", "", str(fit["CH-P06"].qty),
                 f"{fit['CH-P06'].mass_each:.2f}"])
    cols = [("MARK", 13.0), ("PART", 58.0), ("SECTION OR PLATE", 28.0), ("mm", 11.0), ("QTY", 9.0), ("kg EACH", 13.0)]
    return S.table(sh, x, y, cols, rows, size=1.5, row_h=3.0, title="PARTS DETAILED HERE (CHASSIS.md, CT-101)")


def _notes(J: Joint) -> list[str]:
    ch = J.ch
    w = J.gdata["weld"]
    pw = next(f for f in ch.data["fittings"] if f["id"] == "CH-P17")
    sp = ch.shear_panels()[0]
    fix = sp["fixing"]
    groups = {}
    for b in sp["bolts"]:
        groups[b["group"]] = groups.get(b["group"], 0) + 1
    return [
        f"GUSSETS CH-P08: SHS 50x50x3 AT 45 DEG IN PLAN, {_n(J.gussets[0]['length'])} ON THE AXIS BETWEEN THE CUT FACES, EACH END CUT AT "
        f"45 DEG TO BEAR ON THE CROSSMEMBER'S FACE AND ON ITS CHEEK'S FACE, WHICH DOUBLES THE RAIL'S WEB THERE. WELD ALL ROUND EACH CUT: {_n(w['leg'])} "
        f"FILLETS ON THE TOP AND BOTTOM WALLS, A {_n(w['acute_leg'])} FILLET IN THE 45 DEG ANGLE, ITS PROCEDURE QUALIFIED TO AS/NZS 1554.1, "
        f"AND THE 135 DEG SIDE BEVELLED AND BUTT WELDED TO THE WALL'S {_n(w['obtuse_throat'])} (CHS-16).",
        f"CHEEKS CH-P16: A {_n(J.ck['leg'])} FILLET ALONG THE TOP EDGE ON THE RAIL'S WEB AND A FLARE-BEVEL WELD FILLED FLUSH IN THE "
        f"RAIL'S R{_n(J.rail.ro)} BOTTOM CORNER, EFFECTIVE THROAT {_n(J.ck['corner'] * J.rail.ro)} (5/16 R, AISC 360 TABLE J2.2), NONE "
        f"ACROSS THE RAIL (TB 070), AND {_n(J.ck['bar_leg'])} FILLETS BOTH SIDES DOWN THE HINGE BAR'S FACE OVER ITS TOP "
        f"{_n(J.ck['bar_d'])} (CHS-14). OVER THE WEB EACH CHEEK'S END IS COPED {_n(J.ck['cope'])} x 45 DEG CLEAR OF {J.cm.id}'S "
        f"{_n(J.cm_leg)} END FILLET, ITS WEB WELDS STOPPED THERE. A CHEEK BESIDE A GUSSET IS {_n(J.ck['under_gusset']['h'])} TALL AND STEPS ON "
        f"TO {_n(J.ck['under_gusset']['l'])}, THE STEP {_n(J.ck['under_gusset']['step'])} OVER THE RAIL, A {_n(J.ck['leg'])} FILLET ALONG ITS "
        f"LOWER EDGE, THE GUSSET LANDING ON IT (CHS-16).",
        f"PANEL ANGLES CH-P17: EA 50x50x5, THE FLAT LEG {_n(pw['drop'])} UNDER THE MEMBER. A {_n(pw['weld']['leg'])} FILLET ALONG THE UPRIGHT "
        f"LEG'S TOP EDGE AND A FLARE BEVEL WELD ALONG THE MEMBER'S BOTTOM CORNER, THROAT {_n(pw['weld']['corner_throat'])} (est.). THE RAILS' "
        f"ANGLES START {_n(pw['rails']['gap'])} BEHIND THE CHEEKS SO THE WELDS END APART (FAT-22, FAT-23).",
        f"SHEET {sp['id']}: {_n(sp['t'])} HA250 STEEL, HOT-DIP GALVANISED, M{_n(fix['d'])} 8.8 IN {_n(fix['hole'])} HOLES ON THE ANGLES' "
        f"{_n(pw['gauge'])} GAUGE: {groups.get('rail', 0)} ALONG THE RAILS AT {_n(fix['pitch'])}, {groups.get('front', 0)} AT "
        f"{_n(fix['front_pitch'])} UNDER {J.cm.id}, {groups.get('rear', 0)} UNDER THE XT REAR SHOCK CROSSMEMBER. ITS TONGUES REACH UNDER "
        f"THE CROSSMEMBERS' ANGLES, THEIR ROOT CORNERS R{_n(sp['sheet']['root_r'])}. NO STIFFENER: THE REAR TANK SITS ON THE FRONT EDGE (CHS-13).",
        "THE HINGE BAR IS CRUISEMASTER'S, DRAWN PHANTOM (est.): TAKE ITS SIZE FROM ITS DRAWING 33XT AIR BEFORE CUTTING THE CHEEKS. THE ROAD "
        "SIDE MIRRORS THE KERB SIDE. THE FRONT HINGE HAS ITS REAR GUSSETS ONLY (CT-101).",
    ]


def ct106(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, _ = _layout(prj, model)
    ch = lay.chassis
    chs = _chassis()
    J = Joint(ch)
    sh = S.Sheet()
    S.frame(sh)
    _title_of(sh, 86.0, 279.0, "A: XT CENTRE HINGE JOINT, KERB SIDE, PLAN", 5)
    _plan_a(sh, J, 28.0, 205.0)
    _title_of(sh, 86.0, 186.0, "B: SECTION ON THE CHEEKS' FACE, LOOKING OUTBOARD", 5)
    _section_b(sh, J, 28.0, 112.0)
    _title_of(sh, 196.0, 279.0, "C: REAR TANK BAY, SHEAR PANEL, PLAN", 10)
    p0, p1, _ = _bay_c(sh, J, 166.0, 132.0)
    S.cut_marker(sh, p0, p1, (1.0, 0.0), "D")
    _title_of(sh, 318.0, 262.0, "D-D: ACROSS THE RAIL AT THE PANEL", 2.5, "LOOKING REARWARD")
    _section_d(sh, J, 284.0, 160.0)
    _parts(sh, J, 24.0, 96.0)
    S.notes(sh, 276.0, 146.0, _notes(J), width_chars=74, size=1.5)
    _draft_stamp(sh, 318.0, 74.0)
    _title(sh, dwg, reg, "SEE CT-101 FOR MASSES (TB-11).", dwg["scale"], chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

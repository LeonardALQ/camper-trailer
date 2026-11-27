"""CT-106, the XT hinge joint and the rear tank bay's shear panel (A3), from the chassis data (cad/chassis.py).

Detail A draws the XT centre crossmember's kerb-side joint in plan and detail B in section on the rail's inner face,
both at 1:5: the rail, the crossmember's end, the two hinge cheeks, the gusset behind it on its 45 degree line with its
cut ends on the crossmember and the rail and their welds, and none ahead of it, where the front shocks' brackets stand. Detail C draws the rear tank's bay in plan at
1:10 with the shear panel's angles, the sheet cut clear of the rear airbags and shocks, its tongues with their radiused roots and its bolts, and detail D a section
across the rail at the panel at 1:2.5. Nothing here places a part: every line is read from Chassis.hinge_gussets,
hinge_cheeks, panel_pieces and shear_panels and the data they read, so a part the chassis code moves moves here.
Cruisemaster's hinge bar is drawn phantom, its size estimated.
"""
from __future__ import annotations

import math
import time

from ..chassis import arm_clear
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
    either side, the gussets behind it and the shear panel's angle along the rail behind them."""

    def __init__(self, ch):
        self.ch, V = ch, ch.V
        self.V = V
        self.rail, self.raiser = ch.role_sec["rail"], ch.role_sec["raiser"]
        self.cm = next(m for m in ch.members if m.station == "XT centre" and m.role == "cm_xt")
        self.x = self.cm.p0[0]
        self.front, self.rear = self.x - self.cm.sec.b / 2, self.x + self.cm.sec.b / 2
        self.bar_front = self.rear - ch.data["xt_arms"]["parts"]["bar"].get("w", self.cm.sec.b)   # the bar flush with the rear face
        self.y_in = V["rail_c"] - self.rail.b / 2
        self.y_out = V["rail_c"] + self.rail.b / 2
        self.z0, self.z1 = V["rail_underside_z"], V["rail_underside_z"] + self.rail.d
        self.cheeks = [c for c in ch.hinge_cheeks() if c["wheel"] == "RK"]
        self.gussets = [g for g in ch.hinge_gussets() if g["cm"] == self.cm.id and g["side"] < 0]
        self.gdata = ch.data["xt_hinges"]["gusset"]
        self.ck = ch.data["xt_hinges"]["cheek"]
        self.bar = ch.data["xt_hinges"]["bar"]
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
    corner at sheet (x0, y0): the rail, the crossmember's end, the cheeks, the gussets with their axes and the shear
    panel's angle along the web behind the cheek, hidden under the gusset."""
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
    a = J.angle
    v.line(sh, a["x0"], y_in + 50, min(hi, a["x1"]), y_in + 50, "hidden")
    for x in (a["x0"], a["x1"]):
        if x <= hi:
            v.line(sh, x, y_in, x, y_in + 50, "hidden")
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
    sec = J.cm.sec
    n = getattr(sec, "cells", 1)                    # a twin crossmember's tubes side by side, each its own section
    for kk in range(n):
        cx, cy = v.p(J.x - sec.b / 2 + sec.b / n * (kk + 0.5), z0 + sec.d / 2)
        rhs(sh, cx, cy, sec.b / n, sec.d, sec.t, sec.ro, k)
    for c in J.cheeks:
        for b in c["boxes"]:
            v.box(sh, b[0], b[2], b[3], b[5])
    bar_lo = J.pivot[2] - 25.0
    v.box(sh, J.bar_front, bar_lo, J.rear, z0, "phantom")
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
    v.box(sh, a["x0"], zf, min(hi, a["x1"]), zf + 50.0)
    v.solid(sh, a["x0"], zf, min(hi, a["x1"]), zf + 5.0)
    panel = J.ch.shear_panels()[0]
    v.solid(sh, panel["sheet"]["front"], zf - panel["t"], hi, zf)
    # the cheeks' and the gussets' welds and dimensions, from the data
    rb = next(c for c in J.cheeks if c["id"].endswith("B"))["box"]
    top_mid = v.p(rb[0] + 75.0, rb[5])
    weld_symbol(sh, top_mid, (top_mid[0] - 4.0, top_mid[1] + 16.0), _n(J.ck["leg"]), note="TOP EDGE")
    fb = next(c for c in J.cheeks if not c["id"].endswith("B"))["box"]
    corner = v.p(fb[0] + 40.0, z0 + ro / 2)
    weld_symbol(sh, corner, (corner[0] + 5.0, corner[1] - 9.0), f"{J.ck['corner'] * ro:g}", flare=True, note="RAIL CORNER")
    bar_tip = v.p(J.rear, z0 - J.ck["bar_d"] / 2)
    weld_symbol(sh, bar_tip, (bar_tip[0] + 9.0, bar_tip[1] - 11.0), _n(J.ck["bar_leg"]), both=True, length=_n(J.ck["bar_d"]),
                note="TO THE BAR")
    fl = next((f for f in J.ch.hinge_fillers() if f["wheel"] == "RK"), None)
    if fl:                                               # the front cheek's filler under the crossmember's front half (I2-118)
        ch8 = J.ch.data["xt_hinges"]["filler"]["chamfer"]      # its top rear edge chamfered clear of the bar's first run (I2-123)
        v.poly(sh, [(fl["front"], fl["z0"]), (fl["bar_front"], fl["z0"]), (fl["bar_front"], fl["z1"] - ch8),
                    (fl["bar_front"] - ch8, fl["z1"]), (fl["front"], fl["z1"])])
        depth = fl["z1"] - fl["z0"]
        butt = v.p(fl["front"], fl["z1"] - depth / 2)
        weld_symbol(sh, butt, (butt[0] + 8.0, butt[1] - 14.4), _n(J.ck["bar_leg"]), both=True, length=_n(depth),
                    note="CHEEK TO FILLER")
        foot = v.p(fl["front"] + 10.0, fl["z0"])
        weld_symbol(sh, foot, (foot[0] + 4.0, foot[1] - 14.8), _n(J.ch.data["xt_hinges"]["filler"]["leg"]), note="FILLER, SEE NOTE")
    S.vdim(sh, *v.p(rb[3], rb[2]), *v.p(rb[3], rb[5]), v.p(rb[3], 0)[0] + 3.5, _n(J.ck["h"]), size=LABEL)
    S.vdim(sh, *v.p(rb[3], rb[2]), *v.p(rb[3], z0), v.p(rb[3], 0)[0] + 8.0, _n(J.ck["below"]), size=LABEL)
    g = next(g for g in J.gussets if g["face"] > 0)
    S.vdim(sh, *v.p(lo, z0), *v.p(lo, g["z"]), v.p(lo, 0)[0] - 4.0, _n(g["z"] - z0), size=LABEL)
    S.vdim(sh, *v.p(a["x0"], zf), *v.p(a["x0"], z0), v.p(a["x0"], 0)[0] + 4.0, _n(z0 - zf), size=LABEL)
    S.leader(sh, v.p(J.bar_front + 10.0, bar_lo + 30.0), (v.p(J.bar_front, 0)[0] + 10.0, v.p(0, bar_lo)[1] - 4.0),
             "CRUISEMASTER HINGE BAR, PHANTOM (est.)", size=LABEL)
    for x, t in ((hi, "REAR"), (lo, "FRONT")):
        q = v.p(x, z1 + 30.0)
        sh.text(q[0], q[1], t, LABEL, "middle")


def _sheet_outline(sheet: dict, steps: int = 6) -> list[tuple[float, float]]:
    """The shear panel's sheet in plan as one outline (Chassis.panel_sheet): its front corners stepped clear of the arms
    (`steps`), its front edge with any front tongues, its sides, the cuts clear of the rear airbags and shocks with their
    inner corners radiused `cut_r`, and its rear edge with the rear tongues, each tongue's two root corners radiused
    `root_r`."""
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

    def stairs(side: int) -> list[tuple[float, float]]:
        """The front corner on one side as cut clear of the arm (Chassis.arm_cuts), from the front edge along each step's
        inner side to the sheet's side, or the square corner where it has none."""
        st = sorted((s for s in sheet.get("steps") or [] if (s[1] + s[3]) * side > 0), key=lambda s: s[0])
        if not st:
            return [(x0, y0 if side < 0 else y1)]
        pts = [p for xa, ya, xb, yb in st for p in ((xa, ya if side > 0 else yb), (xb, ya if side > 0 else yb))]
        return pts + [(st[-1][2], y0 if side < 0 else y1)]

    kerb_front, road_front = list(reversed(stairs(-1))), stairs(1)
    if not sheet.get("cut"):
        return kerb_front + along(x0, -1) + road_front + [(x1, y1)] + list(reversed(along(x1, 1))) + [(x1, y0)]
    xc, yc = sheet["cut"]
    rc = sheet["cut_r"]
    road = [(xc + rc - rc * math.cos(math.radians(a)), yc + rc - rc * math.sin(math.radians(a))) for a in range(0, 91, 90 // steps)]
    kerb = [(xc + rc - rc * math.sin(math.radians(a)), -yc - rc + rc * math.cos(math.radians(a))) for a in range(0, 91, 90 // steps)]
    return (kerb_front + along(x0, -1) + road_front + [(xc, y1)] + road + [(x1, yc)] + list(reversed(along(x1, 1)))
            + [(x1, -yc)] + kerb + [(xc, y0)])


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
    yc = sp["sheet"]["cut"][1] if sp["sheet"]["cut"] else r[3]
    S.vdim(sh, *v.p(r[2], -yc), *v.p(r[2], yc), xr + 5.0, f"{2 * yc:,.0f} SHEET", size=LABEL)
    fix = sp["fixing"]
    rails = next(f for f in ch.data["fittings"] if f["id"] == "CH-P17")["rails"]
    side = [b for b in sp["bolts"] if b["group"] == "rail" and b["y"] < 0]
    q = v.p(side[0]["x"], side[0]["y"])
    S.leader(sh, q, (q[0] + 1.9, q[1] + 13.25), f"{len(side)} M{_n(fix['d'])} AT {_n(rails['pitch'])}", size=LABEL)
    if sp["sheet"]["cut"]:
        xc, yc = sp["sheet"]["cut"]
        rc = sp["sheet"]["cut_r"]
        q = v.p(xc + rc - rc / math.sqrt(2), -yc - rc + rc / math.sqrt(2))
        S.leader(sh, q, (q[0] + 5.0, q[1] - 7.0), f"CUT {_n(sp['cut_clear'])} CLEAR OF THE AIRBAG AND SHOCK, R{_n(rc)}", size=LABEL)
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
    front = next(c for c in ch.hinge_cheeks() if not c["gusset"])     # its part under the rail run on to the bar (revision W)
    front_l = max(q[3] for q in front["boxes"]) - min(q[0] for q in front["boxes"])
    rows = [["CH-P08", "HINGE GUSSET, BOTH ENDS CUT AT 45 DEG", sec.name.replace(" x ", "x"), _n(g["length"]), str(fit["CH-P08"].qty),
             f"{fit['CH-P08'].mass_each:.2f}"],
            ["CH-P16", "HINGE CHEEK, SHORT, AHEAD OF ITS CROSSMEMBER", f"PL {_n(front_l)}x{_n(J.ck['h'])}x{_n(J.ck['t'])}", "",
             str(sum(1 for c in ch.hinge_cheeks() if not c["gusset"])), f"{front['area'] * J.ck['t'] * 7.85e-6:.2f}"]]
    if "CH-P18" in fit:                                  # the front cheeks' fillers under the crossmembers (I2-118)
        d = fit["CH-P18"].dims
        rows.append(["CH-P18", "HINGE CHEEK FILLER UNDER ITS CROSSMEMBER", f"BLOCK {_n(d[0])}x{_n(d[1])}x{_n(d[2])}", "",
                     str(fit["CH-P18"].qty), f"{fit['CH-P18'].mass_each:.2f}"])
    sizes = {}
    for c in ch.hinge_cheeks():
        if c["gusset"]:
            sizes.setdefault((round(c["l"], 1), round(c["h"], 1)), []).append(c)
    for (l_, h_), cs in sizes.items():
        rows.append(["CH-P16", f"HINGE CHEEK WITH ITS STEP AT {cs[0]['gusset'][7:12]}", f"PL {_n(l_)}x{_n(h_)}x{_n(J.ck['t'])}", "",
                     str(len(cs)), f"{cs[0]['area'] * J.ck['t'] * 7.85e-6:.2f}"])
    seen = {}
    for p in ch.panel_pieces():
        key = (p["use"], p["section"], round(p["length"]))
        seen.setdefault(key, [p, 0])[1] += 1
    words = {"rail": "PANEL ANGLE ALONG A RAIL", "crossmember": "PANEL ANGLE UNDER A CROSSMEMBER"}
    for (use, sid, _), (p, n) in seen.items():
        rows.append(["CH-P17", words[use], sid.replace("_", " ").replace("EA ", "EA "), _n(p["length"]), str(n), f"{p['mass_kg']:.2f}"])
    cols = [("MARK", 13.0), ("PART", 58.0), ("SECTION OR PLATE", 28.0), ("mm", 11.0), ("QTY", 9.0), ("kg EACH", 13.0)]
    return S.table(sh, x, y, cols, rows, size=1.5, row_h=3.0, title="PARTS DETAILED HERE (CHASSIS.md, CT-101)")


def _notes(J: Joint) -> list[str]:
    ch = J.ch
    w = J.gdata["weld"]
    pw = next(f for f in ch.data["fittings"] if f["id"] == "CH-P17")
    sp = ch.shear_panels()[0]
    fix = sp["fixing"]
    groups = {}
    steps = ", AND ".join(f"{_n(ch.step_size(k, 'l'))} x {_n(ch.step_size(k, 'z1') - ch.step_size(k, 'z0'))} FROM "
                          f"{_n(ch.step_size(k, 'z0'))} OVER THE RAIL AT THE {k.upper()}" for k in J.ck["under_gusset"]["l"])
    for b in sp["bolts"]:
        groups[b["group"]] = groups.get(b["group"], 0) + 1
    return [
        f"GUSSETS CH-P08: SHS 50x50x3 AT 45 DEG IN PLAN, {_n(J.gussets[0]['length'])} ON THE AXIS BETWEEN THE CUT FACES, EACH END CUT AT "
        f"45 DEG TO BEAR ON THE CROSSMEMBER'S FACE AND ON ITS CHEEK'S STEP, WHICH SPREADS IT OVER THE RAIL'S WEB. WELD ALL ROUND EACH CUT: {_n(w['leg'])} "
        f"FILLETS ON THE TOP AND BOTTOM WALLS, A {_n(w['acute_leg'])} FILLET IN THE 45 DEG ANGLE, ITS PROCEDURE QUALIFIED TO AS/NZS 1554.1, "
        f"AND THE 135 DEG SIDE BEVELLED AND BUTT WELDED TO THE WALL'S {_n(w['obtuse_throat'])} (CHS-16).",
        f"CHEEKS CH-P16: A {_n(J.ck['leg'])} FILLET ALONG THE TOP EDGE ON THE RAIL'S WEB AND A FLARE-BEVEL WELD FILLED FLUSH IN THE "
        f"RAIL'S R{_n(J.rail.ro)} BOTTOM CORNER, EFFECTIVE THROAT {J.ck['corner'] * J.rail.ro:g} ({J.ck['corner_rule'].upper()}, "
        f"AISC 360 TABLE J2.2), NONE "
        f"ACROSS THE RAIL (TB 070). A REAR CHEEK TAKES {_n(J.ck['bar_leg'])} FILLETS BOTH SIDES DOWN THE HINGE BAR'S FACE OVER ITS TOP "
        f"{_n(J.ck['bar_d'])}, A FRONT ONE THE SAME DOWN ITS FILLER CH-P18'S FRONT FACE. EACH FILLER TAKES "
        f"{_n(J.ch.data['xt_hinges']['filler']['leg'])} FILLETS ALONG ITS BOTTOM REAR EDGE TO THE BAR AND ITS INBOARD TOP EDGE TO THE "
        f"CROSSMEMBER, AND FLARE BEVELS IN THE CROSSMEMBER'S R{_n(J.cm.sec.ro)} FRONT CORNER INBOARD OF THE CHEEK, THROAT "
        f"{math.floor(J.ck['corner'] * J.cm.sec.ro * 10 + 0.5) / 10:g}, AND ALONG THE RAIL'S OUTER BOTTOM CORNER, THROAT "
        f"{J.ck['corner'] * J.rail.ro:g}, BY GMAW AS THE CHEEKS' ARE, ITS TOP REAR EDGE CHAMFERED "
        f"{_n(J.ch.data['xt_hinges']['filler']['chamfer'])} CLEAR OF THE BAR'S FIRST RUN, AND THE CROSSMEMBER'S END WELD GROUND FLUSH "
        f"IN THE RAIL'S INNER BOTTOM CORNER OVER IT (CHS-14). "
        f"OVER THE WEB EACH CHEEK'S END IS COPED {_n(J.ck['cope'])} x 45 DEG CLEAR OF {J.cm.id}'S "
        f"{_n(J.cm_leg)} END FILLET, ITS WEB WELDS STOPPED THERE. A CHEEK BESIDE A GUSSET CARRIES A STEP CENTRED ON IT, "
        f"{steps}, WITH {_n(J.ck['leg'])} FILLETS ALONG ITS TOP AND LOWER EDGES (CHS-16).",
        f"PANEL ANGLES CH-P17: EA 50x50x5, THE FLAT LEG {_n(pw['drop'])} UNDER THE MEMBER. A {_n(pw['weld']['leg'])} FILLET ALONG THE UPRIGHT "
        f"LEG'S TOP EDGE AND A FLARE BEVEL WELD ALONG THE MEMBER'S BOTTOM CORNER, THROAT {_n(pw['weld']['corner_throat'])} (est.). THE RAILS' "
        f"ANGLES START {_n(pw['rails']['gap'])} BEHIND THE CHEEKS' MAIN PLATES AND STOP {_n(pw['rails']['before'])} SHORT OF THE AIRBAGS' "
        f"BRACKETS, SO THOSE WELDS END APART (FAT-22, FAT-23). THE XT CENTRE'S REAR STEPS RUN OVER THE WHOLE ANGLE: HOT-SPOT CHECK.",
        f"SHEET {sp['id']}: {_n(sp['t'])} HA250 STEEL, HOT-DIP GALVANISED, M{_n(fix['d'])} 8.8 IN {_n(fix['hole'])} HOLES ON THE ANGLES' "
        f"{_n(pw['gauge'])} GAUGE: {groups.get('rail', 0) // 2} ON EACH RAIL'S ANGLE AT {_n(pw['rails']['pitch'])}, {groups.get('rear', 0)} AT "
        f"{_n(pw['crossmembers'][0]['pitch'])} UNDER THE XT REAR SHOCK CROSSMEMBER, WHERE ITS TONGUES REACH UNDER THE ANGLES, THEIR ROOT "
        f"CORNERS R{_n(sp['sheet']['root_r'])}. CUT {_n(sp['cut_clear'])} CLEAR OF THE REAR AIRBAGS AND SHOCKS OVER THEIR TRAVEL, THE INNER "
        f"CORNERS R{_n(sp['sheet']['cut_r'])}. THE FRONT CORNERS CUT IN {len(sp['sheet'].get('steps') or []) // 2} STEPS A SIDE "
        f"{_n(arm_clear())} CLEAR OF THE ARMS OVER THEIR TRAVEL (FIT-05). NO STIFFENER: THE REAR TANK SITS ON IT (CHS-13).",
        "THE HINGE BAR IS CRUISEMASTER'S, DRAWN PHANTOM (est.): TAKE ITS SIZE FROM ITS DRAWING 33XT AIR BEFORE CUTTING THE CHEEKS. THE ROAD "
        "SIDE MIRRORS THE KERB SIDE. EACH HINGE HAS ITS REAR GUSSETS ONLY (CT-101).",
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
    _title_of(sh, 318.0, 257.0, "D-D: ACROSS THE RAIL AT THE PANEL", 2.5, "LOOKING REARWARD")
    _section_d(sh, J, 284.0, 160.0)
    _parts(sh, J, 24.0, 96.0)
    S.notes(sh, 276.0, 146.0, _notes(J), width_chars=108, size=1.5)   # wider since the fillers' note, clear of the stamp (I2-118)
    _draft_stamp(sh, 318.0, 74.0)
    _title(sh, dwg, reg, "SEE CT-101 FOR MASSES (TB-11).", dwg["scale"], chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

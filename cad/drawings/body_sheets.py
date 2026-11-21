"""Body drawings CT-201 to CT-203 and CT-301 (A3, third angle), from the body design (cad/body.py, BODY.md) and its
results (build/body/body.json). Every sheet is DRAFT and not for construction until the engineer reviews BODY.md.

CT-201: body shell, the panel layout and every opening with its size and position.
CT-202: joint details: floor joiner, corner joiner, the roof-to-wall joiner, the bed deck ledger and an insert with
        its crush tube.
CT-203: insert map: every fixing line in the floor, the walls and the roof.
CT-301: body to chassis: the mount positions, the bolt detail, isolation and sealing.
The views are drawn from the layout's numbers as outlines, at the scale shown. Revision B of the body (20 Nov 2026) is
the LandCruiser 79 layout: a 4,420 mm body with a fixed roof, a full rear wall and no garage.
"""
from __future__ import annotations

import json
import time

from ..body import Body
from ..build import BUILD, git_hash
from . import sheet as S
from .chassis_sheets import _layout, rhs, weld_symbol

OUT = BUILD / "drawings"


def _title(sh, dwg, reg, mass_note, scale, material="GRP/XPS AND GRP/PVC SANDWICH, ALUMINIUM 6060-T5, HDG STEEL"):
    rev = dwg["revisions"][-1]
    S.title_block(
        sh, owner=reg["owner"], project=dwg.get("project") or reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"], engineer="NOT REVIEWED", sheet_no=dwg["sheet"], sheets=reg["sheets_total"],
        size=dwg["size"], scale=scale, material=material, mass_note=mass_note,
        model_ref=f"body.step (ASM-BD rev {rev['rev']})", git=git_hash(), weld_note="BONDED JOINTS MS POLYMER, BEAD INSIDE AND OUT. ")
    S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                               checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]])


def _stamp(sh, x, y):
    sh.rect(x - 50, y - 6, x + 50, y + 6, "fail")
    sh.text(x, y - 1.7, "DRAFT, NOT FOR CONSTRUCTION UNTIL THE ENGINEER REVIEWS BODY.md", 2.0, "middle", bold=True, color="#c00")


def _data(prj, model):
    lay, rep = _layout(prj, model)
    res = json.loads((BUILD / "body" / "body.json").read_text())
    return lay, rep, res, Body(lay, None)


def _body_mass(rep) -> tuple[float, float]:
    rows = [r for r in rep["schedule"] if r["system"] == "body"]
    return sum(r["mass_kg"] for r in rows), sum(r["mass_with_growth_kg"] for r in rows)


def _wall(sh, ox, oy, k, L, H, ops, flip=False, label=None):
    """A wall elevation at 1:k with origin (ox, oy) at the floor and the wall's start. Openings as rectangles with
    their ids. `flip` draws it as seen from the other face (u runs right to left)."""
    sh.rect(ox, oy, ox + L / k, oy + H / k, "thick")
    for o in ops:
        u0, u1 = (L - o["u1"], L - o["u0"]) if flip else (o["u0"], o["u1"])
        x0, x1 = ox + u0 / k, ox + u1 / k
        y0, y1 = oy + o["z0"] / k, oy + o["z1"] / k
        sh.rect(x0, y0, x1, y1, "medium")
        sh.line(x0, y0, x1, y1, "thin")
        sh.line(x0, y1, x1, y0, "thin")
        sh.text((x0 + x1) / 2, y1 + 0.8, o["id"], 1.5, "middle")
    if label:
        sh.text(ox, oy + H / k + 4.5, label, 2.2, bold=True)


def _member(b) -> str:
    """The side walls' member section from the body data, for the sheets' notes (data/body/body.yaml `stiffener`)."""
    return b.d["panels"]["wall"]["stiffener"]["name"].split(" 6060")[0]


# ------------------------------------------------------------------ CT-201 body shell
def ct201(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, rep, res, b = _data(prj, model)
    V = lay.V
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    L, H, W = V["body_length"], V["interior_h"], V["body_width"]
    ops = res["openings"]
    # kerb-side wall seen from outside (front to the left), with the floor and the fixed roof
    ox, oy = 22.0, 222.0
    _wall(sh, ox, oy, k, L, H, [o for o in ops if o["wall"] == "kerb"], label="KERB-SIDE WALL, FROM OUTSIDE (FRONT LEFT)")
    sh.rect(ox, oy - V["floor_t"] / k, ox + L / k, oy, "medium")
    sh.rect(ox, oy + H / k, ox + L / k, oy + (H + V["roof_t"]) / k, "medium")
    zb = V["mattress_z"] + V["mattress_t"] - V["floor_z"]
    zn = V["bed_night_h"] + V["deck_t"] + V["underlay_t"] + V["mattress_t"]
    for z, t in ((zb, "DAY"), (zn, "NIGHT")):
        sh.line(ox + V["end_wall_t"] / k, oy + z / k, ox + V["bed_u1"] / k, oy + z / k, "phantom")
        sh.text(ox + V["end_wall_t"] / k + 0.6, oy + z / k + 0.7, t, 1.25)
    # the side-wall stiffener in the living-zone bay (BD-18, BDY-10) and the H12 radius at the roof's front edge
    for yy, flip, iid in ((oy, False, "BD-19"), (166.0, True, "BD-18")):   # the door's rear jamb member, the road wall's stiffener
        us = lay.find(iid).cog[0] - V["body_x0"]
        xs = ox + ((L - us) if flip else us) / k
        sh.line(xs, yy, xs, yy + H / k, "phantom")
        sh.text(xs + 0.8, yy + H / k - 3.0, iid.split(".")[0], 1.3)
        xr = ox + (L / k if flip else 0)
        r = V["roof_front_r"] / k
        sgn = -1 if flip else 1
        sh.fillrect(min(xr, xr + sgn * r), yy + H / k + V["roof_t"] / k - r, max(xr, xr + sgn * r), yy + H / k + V["roof_t"] / k + 0.3, "white")
        import math
        pts = [(xr + sgn * (r - r * math.cos(math.radians(a))), yy + H / k + V["roof_t"] / k - r + r * math.sin(math.radians(a))) for a in range(0, 91, 10)]
        sh.path(pts, "thick")
    sh.text(ox + 1.2, oy + (H + V["roof_t"]) / k + 1.2, f"R{V['roof_front_r']:.0f}", 1.3)
    S.hdim(sh, ox, oy - V["floor_t"] / k, ox + L / k, oy - V["floor_t"] / k, oy - 6, f"{L:.0f} BODY", size=1.7)
    S.vdim(sh, ox + L / k, oy, ox + L / k, oy + H / k, ox + L / k + 8, f"{H:.0f}", size=1.6)
    # road-side wall seen from outside (front to the right)
    oy2 = 166.0
    _wall(sh, ox, oy2, k, L, H, [o for o in ops if o["wall"] == "road"], flip=True, label="ROAD-SIDE WALL, FROM OUTSIDE (FRONT RIGHT)")
    sh.rect(ox, oy2 - V["floor_t"] / k, ox + L / k, oy2, "medium")
    sh.rect(ox, oy2 + H / k, ox + L / k, oy2 + (H + V["roof_t"]) / k, "medium")
    # roof plan with the solar array, no hatches
    oy3 = 104.0
    sh.text(ox, oy3 + W / k + 4.5, "FIXED ROOF, PLAN (FRONT LEFT): SOLAR ARRAY BONDED, NO HATCHES", 2.2, bold=True)
    sh.rect(ox, oy3, ox + L / k, oy3 + W / k, "thick")
    rv = V["front_vert_r"] / k
    import math
    for yc, s_ in ((oy3, 1), (oy3 + W / k, -1)):     # the 250 mm radius on both front verticals (H12), seen from above
        sh.fillrect(ox - 0.4, min(yc, yc + s_ * rv), ox + rv, max(yc, yc + s_ * rv), "white")
        sh.path([(ox + rv - rv * math.sin(math.radians(a)), yc + s_ * (rv - rv * math.cos(math.radians(a)))) for a in range(0, 91, 10)], "thick")
    sh.text(ox + rv + 0.8, oy3 + 1.2, f"R{V['front_vert_r']:.0f}", 1.3)
    sx = (V["solar_x0"] - V["body_x0"]) / k
    sh.rect(ox + sx, oy3 + (W / 2 - V["solar_w"]) / k, ox + sx + 2 * V["solar_l"] / k, oy3 + (W / 2 + V["solar_w"]) / k, "medium")
    sh.line(ox + sx + V["solar_l"] / k, oy3 + (W / 2 - V["solar_w"]) / k, ox + sx + V["solar_l"] / k, oy3 + (W / 2 + V["solar_w"]) / k, "thin")
    sh.line(ox + sx, oy3 + W / 2 / k, ox + sx + 2 * V["solar_l"] / k, oy3 + W / 2 / k, "thin")
    sh.text(ox + sx + V["solar_l"] / k, oy3 + W / 2 / k + 6, f"4 SUNMAN 430 W, {2 * V['solar_l']:.0f} x {2 * V['solar_w']:.0f}", 1.6, "middle")
    S.hdim(sh, ox, oy3, ox + sx, oy3, oy3 - 5, f"{V['solar_x0'] - V['body_x0']:.0f}", size=1.5)
    # end walls
    ex = 128.0
    for wall, yy, lab in (("front", 222.0, "FRONT WALL, FROM THE FRONT"), ("rear", 166.0, "REAR WALL, FROM BEHIND")):
        o2 = [dict(o, u0=o["u0"] + W / 2 - V["wall_t"], u1=o["u1"] + W / 2 - V["wall_t"]) for o in ops if o["wall"] == wall]
        _wall(sh, ex, yy, k, W - 2 * V["wall_t"], H, o2, flip=(wall == "front"), label=lab)
    ew = res["end_wall"]
    S.notes(sh, ex, 160.0, [f"THE FULL REAR WALL IS THE BOX'S REAR DIAPHRAGM: {ew['tau_mpa']:.2f} MPa SKIN SHEAR, {ew['util']:.2f} OF ITS "
                            "ALLOWANCE (BDY-20). NO PORTAL."], title="", width_chars=48, size=1.5)
    rows = [(o["id"], o["wall"].upper(), o["name"].split(",")[0][:44], f"{o['u0']:.0f} TO {o['u1']:.0f}", f"{o['z0']:.0f} TO {o['z1']:.0f}",
             f"{o['w']:.0f} x {o['h']:.0f}") for o in ops]
    y = S.table(sh, 230.0, 232.0, [("ID", 11), ("WALL", 11), ("OPENING", 74), ("ALONG", 27), ("ABOVE FLOOR", 27), ("CUT-OUT", 30)], rows,
                size=1.5, row_h=3.0, title="OPENINGS (ALONG: FROM THE BODY FRONT, END WALLS FROM THE CENTRELINE)")
    pd = res["panel_data"]
    prow = [(pd[kk]["name"].split(":")[0][:60], f"{pd[kk]['t']}", f"{pd[kk]['kg_m2']:.2f}", f"{pd[kk]['D_knm2_per_m']:.1f}")
            for kk in ("floor", "wall", "front_wall", "roof")]
    S.table(sh, 230.0, y - 7, [("PANEL", 110), ("mm", 18), ("kg/m2", 26), ("D kNm2/m", 26)], prow, size=1.5, row_h=3.0, title="PANELS")
    oc = res["openings_check"]
    S.notes(sh, 22, 76, [
        "DATUM DIM-01. SIDE-WALL POSITIONS ALONG THE TRAILER FROM THE BODY FRONT, HEIGHTS FROM THE FLOOR SURFACE (Z "
        f"{V['floor_z']:.0f}). END-WALL POSITIONS FROM THE CENTRELINE, POSITIVE TO THE ROAD SIDE.",
        "FLOOR, BOTH SIDE WALLS AND THE ROOF ARE ONE PIECE EACH. EVERY PANEL EDGE BONDS INTO AN ALUMINIUM EXTRUSION (CT-202). THE ROOF IS FIXED.",
        f"OPENINGS: 300 mm OF FULL WALL BETWEEN THEM, 150 mm TO A PANEL EDGE, NONE WITHIN 300 mm OF THE REAR CORNERS (BDY-18: "
        f"{'PASS' if oc['ok'] else 'FAIL'}). CUT-OUT CORNERS RADIUSED, 68 mm FOR SERVICE DOORS, 90 mm AT THE TOP OF THE DC DOOR.",
        "W1 (OP-01) OVER THE BED IS THE SECOND WAY OUT, 804 x 454 mm CLEAR. D2 (OP-15) OPENS INTO THE WET ROOM. THE PRODUCTS ARE ON "
        "CT-013 AND EACH OPENING'S MARGIN ON CT-011. H12: GRP CORNER PIECES GIVE THE ROOF'S FRONT EDGE A 150 mm RADIUS AND THE FRONT "
        f"VERTICALS 250 mm. BD-18: ONE {_member(b)} STIFFENER ON THE ROAD WALL'S INNER SKIN BEHIND THE TOWER, WITH THE DOOR'S REAR JAMB "
        "MEMBER BD-19 AND THE BED'S FOUR HARDPOINTS LB-06, EACH 10 mm SHORT OF THE JOINERS (BDY-10, BDY-22, FIT-07). PHANTOM DAY AND NIGHT: THE MATTRESS TOP, "
        f"{V['mattress_z'] + V['mattress_t'] - V['floor_z']:.0f} AND "
        f"{V['bed_night_h'] + V['deck_t'] + V['underlay_t'] + V['mattress_t']:.0f} mm ABOVE THE FLOOR (CT-010).",
        "WHERE AN OPENING CROSSES A CHASSIS STATION THE OUTRIGGER-TIP MOUNT MOVES INBOARD OF ITS FRAME AND THE FLOOR JOINER RUNS UNBROKEN.",
    ], width_chars=118, size=1.6)
    _stamp(sh, 320, 96)
    kg, kgg = _body_mass(rep)
    _title(sh, dwg, reg, f"BODY {kg:.0f} kg, {kgg:.0f} kg WITH GROWTH (TB-11).", k)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


def _sandwich(sh, x0, y0, x1, y1, skin, k, vertical=False):
    """A sandwich panel section: outline, the two skins as thick lines, the core hatched."""
    sh.rect(x0, y0, x1, y1, "medium")
    s = skin / k
    if vertical:
        sh.rect(x0, y0, x0 + s, y1, "shade")
        sh.rect(x1 - s, y0, x1, y1, "shade")
        S.hatch_rect(sh, x0 + s, y0, x1 - s, y1, 1.6)
    else:
        sh.rect(x0, y0, x1, y0 + s, "shade")
        sh.rect(x0, y1 - s, x1, y1, "shade")
        S.hatch_rect(sh, x0, y0 + s, x1, y1 - s, 1.6)


def _dt(sh, cx, top, title, scale):
    sh.text(cx, top, title, 2.2, "middle", bold=True)
    sh.text(cx, top - 3.5, f"SCALE 1:{scale:g}", 1.9, "middle")


# ------------------------------------------------------------------ CT-202 joint details
def ct202(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, rep, res, b = _data(prj, model)
    V = lay.V
    sh = S.Sheet()
    S.frame(sh)
    strip = V["floor_underside_z"] - (V["rail_top_z"] + 125)
    # ---- A: floor joiner on the outrigger tip, 1:2
    k, cx, top = 2.0, 60.0, 278.0
    _dt(sh, cx, top, "A: FLOOR JOINER AT THE WALL FOOT", k)
    fy0 = 235.0
    _sandwich(sh, 25, fy0, 75, fy0 + 30 / k, 2.0, k)                    # floor
    _sandwich(sh, 75, fy0, 75 + 35 / k, fy0 + 50 / k, 1.5, k, vertical=True)   # wall foot, 50 mm shown
    sh.path([(73, fy0 - 2 / k), (75 + 35 / k + 2 / k, fy0 - 2 / k), (75 + 35 / k + 2 / k, fy0 + 40 / k), (75 + 35 / k, fy0 + 40 / k)], "thick")
    sh.path([(73, fy0 - 2 / k), (73, fy0 + 32 / k), (60, fy0 + 32 / k)], "thick")
    sh.rect(40, fy0 - (2 + strip) / k, 75 + 35 / k + 2 / k, fy0 - 2 / k, "medium")
    S.hatch_rect(sh, 40, fy0 - (2 + strip) / k, 75 + 35 / k + 2 / k, fy0 - 2 / k, 0.8)
    sh.rect(40, fy0 - (2 + strip + 30) / k, 75 + 35 / k + 2 / k, fy0 - (2 + strip) / k, "medium")
    for i, t in enumerate(("FLOOR JOINER, 2 mm ALUMINIUM, BONDED MS POLYMER BOTH LEGS", f"{strip:.1f} mm EPDM-FACED HDPE BEARER STRIP (CH-S01)",
                           "OUTRIGGER RHS 127x51x3.5 TIP, M12 MOUNT INBOARD (CT-301)", "WALL 35 mm GRP/XPS, FLOOR 30 mm GRP/H80")):
        sh.text(22, 205 - 3 * i, t, 1.5)
    # ---- B: corner joiner, plan, 1:2
    cx, top = 150.0, 278.0
    _dt(sh, cx, top, "B: CORNER JOINER, PLAN", k)
    _sandwich(sh, 130, 232, 130 + 35 / k, 262, 1.5, k, vertical=True)
    _sandwich(sh, 130 + 35 / k + 2 / k, 232, 175, 232 + 35 / k, 1.5, k)
    sh.path([(130 - 2 / k, 262), (130 - 2 / k, 232 - 2 / k), (175, 232 - 2 / k)], "thick")
    sh.path([(130 + 35 / k + 2 / k, 262), (130 + 35 / k + 2 / k, 232 + 35 / k + 2 / k), (175, 232 + 35 / k + 2 / k)], "thick")
    for i, t in enumerate(("CORNER JOINER 2.0 kg/m, OUTER RADIUS, BONDED BOTH WAYS", "BEAD INSIDE AND OUT, EDGES SEALED WITH RESIN",
                           "SHEAR FLOW IN TWIST " f"{max(j['value'] for j in res['joints'] if j['unit'] == 'N/mm'):.1f} N/mm (BDY-14)")):
        sh.text(122, 222 - 3 * i, t, 1.5)
    # ---- C: roof-to-wall joiner, section, 1:2
    cx, top = 60.0, 186.0
    _dt(sh, cx, top, "C: ROOF-TO-WALL JOINER", k)
    wy = 112.0
    _sandwich(sh, 40, wy, 40 + 35 / k, wy + 30, 1.5, k, vertical=True)              # wall top
    sh.path([(40 - 2 / k, wy + 18), (40 - 2 / k, wy + 30 + 2 / k), (40 + 35 / k + 14, wy + 30 + 2 / k)], "thick")   # outer leg and flange
    sh.path([(40 + 35 / k + 2 / k, wy + 22), (40 + 35 / k + 2 / k, wy + 30)], "thick")                               # inner leg
    _sandwich(sh, 40 - 2 / k, wy + 30 + 2 / k, 40 + 35 / k + 14, wy + 30 + 2 / k + 40 / k, 2.0, k)                  # roof edge
    sh.line(40 - 2 / k, wy + 30 + 2 / k + 40 / k, 40 - 4, wy + 30 + 40 / k - 2, "thick")                           # drip edge
    rf = res["roof"]
    for i, t in enumerate(("ROOF-TO-WALL JOINER 1.65 kg/m, BONDED MS POLYMER ALL ROUND, THE WALL'S TOP INSERT STRIP UNDER IT",
                           f"40 m/s UPLIFT {rf['q_n_mm']:.2f} N/mm ON THE BOND, AGAINST {rf['allow_n_mm']:.0f} N/mm (BDY-19)",
                           "ROOF EDGE CAPPED, DRIP EDGE OUTSIDE THE WALL SKIN",
                           f"AWNING BRACKETS: {b.d['awning']['bolts_per_bracket']} {b.d['awning']['bolt'].upper().replace(' MM ', ' mm ')} EACH,",
                           "THROUGH THE KERB-EDGE INSERT STRIP, NYLON WASHERS AND DURALAC ON THE STEEL (BDY-11)")):
        sh.text(22, 106 - 3 * i, t, 1.5)
    # ---- D: lift bed rail on its hardpoint in the side wall, plan section, 1:2
    cx, top = 150.0, 186.0
    _dt(sh, cx, top, "D: LIFT BED RAIL ON ITS HARDPOINT, PLAN", k)
    dy = 112.0
    _sandwich(sh, 125, dy, 125 + 35 / k, dy + 60, 1.5, k, vertical=True)            # side wall, plan section, outer face on the left
    st = b.d["panels"]["wall"]["stiffener"]
    dd, ww, tt = st["depth"], st["width"], st["wall"]
    hx0, hy0 = 125 + (35 - 1.5 - dd) / k, dy + 30 - ww / 2 / k                       # the member on the inner skin, the XPS behind it
    sh.rect(hx0, hy0, hx0 + dd / k, hy0 + ww / k, "shade")
    sh.rect(hx0 + tt / k, hy0 + tt / k, hx0 + (dd - tt) / k, hy0 + (ww - tt) / k, "white")
    sh.rect(hx0 + tt / k, hy0 + tt / k, hx0 + (dd - tt) / k, hy0 + (ww - tt) / k, "medium")
    rx = 125 + 35 / k
    ry0, ry1 = hy0 + (ww - 50) / 2 / k, hy0 + (ww + 50) / 2 / k                       # the rail, 50 mm wide, centred on the member
    sh.path([(rx, ry0), (rx + 20 / k, ry0), (rx + 20 / k, ry0 + 2), (rx + 4 / k, ry0 + 2), (rx + 4 / k, ry1 - 2),
             (rx + 20 / k, ry1 - 2), (rx + 20 / k, ry1), (rx, ry1)], "thick")         # the rail's C-channel
    for yy in (ry0 + 12 / k, ry1 - 12 / k):
        sh.line(hx0 + (dd - tt - 2) / k, yy, rx + 4 / k, yy, "medium")                # 1/4 in screws through the inner skin into the member
    sh.line(hx0 - 8, hy0 + ww / 2 / k, rx + 30 / k, hy0 + ww / 2 / k, "centre")
    sh.text(125 + 1.5 / k + 0.3, dy - 2.6, f"{st['break']:g} mm XPS", 1.2)
    ins = next(i for i in res["inserts"] if i["id"] == "INS-01")
    for i, t in enumerate((f"HARDPOINT {_member(b)} 6060-T5 ON THE INNER SKIN, FULL WALL HEIGHT, BONDED INTO A {dd:g} mm CHANNEL IN THE XPS",
                           f"AS THE PANEL IS MADE. {st['break']:g} mm OF XPS STAYS BEHIND IT, SO NO METAL CROSSES THE CORE (LB-06, BDY-22)",
                           f"HAPPIJAC C-CHANNEL RAIL ON THE INNER SKIN, 1/4 in SELF-TAPPING SCREWS THROUGH IT INTO THE MEMBER'S {tt:g} mm WALL",
                           f"{ins['n']:.0f} N PER SCREW, {ins['case'].upper().replace(' KG', ' kg')}, {ins['util']:.2f} OF HALF ITS RATED SHEAR (BDY-11)",
                           "FOUR RAILS, TWO ON EACH SIDE WALL, 1,067 mm APART ALONG THE TRAILER (CT-203)")):
        sh.text(122, 99 - 3 * i, t, 1.4)
    # ---- F: a wall member's foot at the floor joiner, section, 1:2 (BDY-22, F3-05)
    gap, padw = st["end_gap_mm"], st["foot_pad_mm"]
    xo, yj = 190.0, 118.0
    xi = xo + 35 / k
    _dt(sh, 201.0, 186.0, "F: MEMBER FOOT", k)
    _sandwich(sh, xo, yj + 1.0, xi, 172.0, 1.5, k, vertical=True)                   # the wall, section, outer face on the left
    sh.path([(xo - 1.0, yj + 14.0), (xo - 1.0, yj), (xi + 1.0, yj), (xi + 1.0, yj + 14.0)], "thick")   # the floor joiner round the foot
    mx0, mx1 = xi - (1.5 + dd) / k, xi - 1.5 / k
    sh.rect(mx0, yj + 1.0 + gap / k, mx1, 172.0, "shade")                         # the member, its foot 10 mm off the joiner
    sh.rect(mx0 + tt / k, yj + 1.0 + gap / k + tt / k, mx1 - tt / k, 172.0, "white")
    sh.rect(mx0, yj + 1.0, mx1, yj + 1.0 + gap / k, "medium")                     # the rigid PVC pad
    sh.text(xi + 2.0, yj + 0.6, "FLOOR JOINER", 1.2)
    sh.text(xi + 2.0, yj + 3.6, f"{gap:g} mm PVC PAD", 1.2)
    for i, t in enumerate((f"{_member(b)}", "ON THE INNER SKIN,", f"{st['break']:g} mm OF XPS BEHIND IT.", f"IT STOPS {gap:g} mm SHORT OF",
                           f"THE JOINER ON A {padw:g} mm WIDE", "RIGID PVC PAD, XPS IN THE", "REST OF THE GAP. AT ITS HEAD,",
                           f"{gap:g} mm OF XPS (BDY-22)")):
        sh.text(187.0, 169.0 - 2.4 * i, t, 1.2, "end")
    # ---- E: insert with crush tube at a body mount, 1:2 (the bolt detail is on CT-301)
    k, cx, top = 2.0, 200.0, 278.0
    _dt(sh, cx + 5, top, "E: FLOOR INSERT AND CRUSH TUBE", k)
    _sandwich(sh, 182, 240, 228, 240 + 30 / k, 2.0, k)
    sh.rect(198, 240, 212, 240 + 30 / k, "shade")
    sh.rect(203.5, 240, 206.5, 240 + 30 / k, "white")
    sh.rect(203.5, 240, 206.5, 240 + 30 / k, "medium")
    sh.rect(180 + 2, 240 + 30 / k, 230 - 2, 240 + 30 / k + 1.5, "thick")
    sh.line(205, 228, 205, 262, "centre")
    for i, t in enumerate(("HIGH-DENSITY PVC INSERT 70 x 26 IN PLACE OF CORE", "PULTRUDED GRP CRUSH TUBE, BOLT NEVER IN BARE FOAM",
                           "100 x 100 x 3 ALUMINIUM SPREADER, BONDED, MS POLYMER IN THE HOLE")):
        sh.text(176, 230 - 3 * i, t, 1.5)
    S.notes(sh, 22, 76, [
        "PLANNING-LEVEL DETAILS. EXTRUSION PROFILES ARE DIY CARAVANS' 29 mm RANGE MADE TO ORDER FOR 35 mm PANELS (report 12 open question 8).",
        "EVERY CUT PANEL EDGE IS SEALED WITH RESIN OR AN EDGE INSERT SO WATER CANNOT TRACK ALONG THE SKIN BOND.",
        "ALUMINIUM NEVER TOUCHES THE STEEL: DURALAC ON FAYING SURFACES, NYLON WASHERS AND SLEEVES, TEF-GEL ON STAINLESS THREADS (MAT-04).",
        f"WITH THE ROOF BONDED THE BODY TAKES {100 * res['twist']['closed']['share']:.0f} % OF THE LC5a TWIST, SO EVERY JOINT HERE IS STRUCTURAL.",
    ], width_chars=118, size=1.6)
    _stamp(sh, 320, 96)
    kg, kgg = _body_mass(rep)
    _title(sh, dwg, reg, f"BODY {kg:.0f} kg, {kgg:.0f} kg WITH GROWTH (TB-11).", dwg["scale"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


def _plan_outline(sh, lay, ox, oy, k, chassis=True):
    """The body outline in plan at 1:k (front left, road side up), with the rails and the stations as phantoms."""
    V = lay.V
    W = V["body_width"]
    P = lambda x, y: (ox + (x - V["body_x0"]) / k, oy + (y + W / 2) / k)   # noqa: E731
    a, c = P(V["body_x0"], -W / 2), P(V["body_x1"], W / 2)
    sh.rect(a[0], a[1], c[0], c[1], "thick")
    if chassis:
        for s in (-1, 1):
            p0, p1 = P(V["body_x0"], s * V["rail_c"]), P(V["body_x1"], s * V["rail_c"])
            sh.line(p0[0], p0[1], p1[0], p1[1], "phantom")
        for st in lay.chassis.stations:
            x = lay.chassis.station_x(st)
            p0, p1 = P(x, -W / 2), P(x, W / 2)
            sh.line(p0[0], p0[1], p1[0], p1[1], "phantom")
    return P


# ------------------------------------------------------------------ CT-203 insert map
def ct203(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, rep, res, b = _data(prj, model)
    V = lay.V
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    ox, oy = 22.0, 196.0
    sh.text(ox, oy + V["body_width"] / k + 5, "FLOOR, PLAN (FRONT LEFT, ROAD SIDE UP): MOUNT INSERTS AND FURNITURE FIXINGS", 2.2, bold=True)
    P = _plan_outline(sh, lay, ox, oy, k)
    for st in lay.chassis.stations:
        x = lay.chassis.station_x(st)
        for y in (-V["rail_c"], V["rail_c"], -b.d["mounts"]["outrigger_tip_y"], b.d["mounts"]["outrigger_tip_y"]):
            p = P(x, y)
            sh.line(p[0] - 0.9, p[1] - 0.9, p[0] + 0.9, p[1] + 0.9, "medium")
            sh.line(p[0] - 0.9, p[1] + 0.9, p[0] + 0.9, p[1] - 0.9, "medium")
    # furniture footprints whose fixings go into the floor through inserts
    for iid in ("LA-09", "LA-11T", "LA-11B", "EL-02", "LA-14F", "WR-01", "WR-06", "WR-07"):
        bb = lay.find(iid).box
        p0, p1 = P(bb[0], bb[1]), P(bb[3], bb[4])
        sh.rect(p0[0], p0[1], p1[0], p1[1], "thin")
        if iid != "LA-14F":    # the machine base shares the plinth's footprint
            sh.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 0.6, "EL-02, LA-14F" if iid == "EL-02" else iid, 1.3, "middle")
    # kerb-side wall from inside, with its insert strips
    oy2 = 126.0
    sh.text(ox, oy2 + V["interior_h"] / k + 5, "KERB-SIDE WALL FROM INSIDE (FRONT RIGHT): INSERT STRIPS", 2.2, bold=True)
    L, H = V["body_length"], V["interior_h"]
    sh.rect(ox, oy2, ox + L / k, oy2 + H / k, "thick")
    fz = V["floor_z"]
    for iid in ("LB-04.2", "LB-04.4"):          # the lift bed's hardpoints behind the kerb-side rails (LB-06)
        rb = lay.find(iid).box
        x0, x1 = ox + (L - (rb[3] - V["body_x0"])) / k, ox + (L - (rb[0] - V["body_x0"])) / k
        sh.rect(x0, oy2 + (rb[2] - fz) / k, x1, oy2 + (rb[5] - fz) / k, "fill")
    rb = lay.find("LB-04.2").box
    sh.text(ox + (L - (rb[3] - V["body_x0"])) / k - 1, oy2 + (rb[2] - fz) / k + 1.0, f"LIFT BED HARDPOINTS LB-06, {_member(b)} ON THE INNER SKIN", 1.4, "end")
    lk = lay.find("LA-11L").box                  # the lockers over the plinth hang on an insert strip
    for wall, a, c, _ in res["members"]["strips"]:   # the lockers' strip, stopped 25 mm short of the member it meets (FIT-07)
        if wall == "kerb":
            sh.rect(ox + (L - (c - V["body_x0"])) / k, oy2 + (lk[5] - fz - 60) / k, ox + (L - (a - V["body_x0"])) / k, oy2 + (lk[5] - fz - 25) / k, "fill")
    sh.text(ox + (L - (lk[3] - V["body_x0"])) / k, oy2 + (lk[2] - fz) / k - 2.6, "LOCKERS' INSERT STRIP", 1.3)
    us = lay.find("BD-19").cog[0] - V["body_x0"]
    sh.line(ox + (L - us) / k, oy2, ox + (L - us) / k, oy2 + H / k, "phantom")
    sh.text(ox + (L - us) / k + 0.8, oy2 + 3.0, "JAMB MEMBER BD-19", 1.3)
    sh.rect(ox, oy2 + (H - 25) / k, ox + L / k, oy2 + H / k, "fill")
    sh.text(ox + 1, oy2 + H / k - 3, "TOP INSERT STRIP: ROOF JOINER", 1.4)
    rows = []
    for i in res["inserts"]:
        rows.append((i["what"].split(",")[0].upper()[:38], i["what"].split(",")[1].strip().upper()[:46] if "," in i["what"] else "",
                     f"{i['n'] / 1000:.2f} kN, HALF OF {i['rated_n'] / 1000:.1f}", f"{i['util']:.2f} (BDY-11)"))
    rows += [("FLOOR, BODY MOUNTS", "HD PVC 70 x 26, GRP CRUSH TUBE, SPREADER", f"{res['mounts']['tension_n'] / 1000:.1f} kN TENSION", f"{res['mounts']['util']:.2f} (BDY-16)"),
             ("ROOF EDGE, ROOF JOINER", "BONDED, NO FIXINGS", f"{res['roof']['q_n_mm']:.2f} N/mm UPLIFT", f"{res['roof']['util']:.3f} (BDY-19)"),
             ("ROOF, SOLAR ARRAY", "NONE: BONDED, NO FIXINGS, NO HATCHES", "", ""),
             ("FLOOR, FURNITURE", "M6 INTO HD PVC INSERTS UNDER EACH FOOTPRINT", "LC7 FIXINGS (CHASSIS.md)", ""),
             ("FLOOR, PLINTH AND TOWER", "M10 TO THE RAISERS AND OUTRIGGERS, 100 x 100 SPREADERS", "SEE CT-104", ""),
             ("REAR WALL, SPLIT CRADLE", f"{b.d['cradle']['bolts']} M8 IN THE INSERT STRIP, {b.d['cradle']['stays']['n']} STAYS (AC-04)",
              f"{res['cradle']['tension_n'] / 1000:.2f} kN TENSION", f"{res['cradle']['util']:.2f} (BDY-21)")]
    S.table(sh, 230.0, 232.0, [("FIXING LINE", 46), ("INSERT", 64), ("LOAD", 40), ("UTIL.", 30)], rows, size=1.45, row_h=3.2,
            title="FIXING LINES AND INSERTS")
    S.notes(sh, 22, 76, [
        "LEGEND: CROSS, BODY MOUNT (CT-301). THIN OUTLINE, A FURNITURE FOOTPRINT WITH ITS FLOOR INSERTS. PHANTOM, RAILS AND CHASSIS STATIONS.",
        "EVERY FIXING PASSES THROUGH AN INSERT STRIP AND, THROUGH THE FLOOR, A CRUSH TUBE. NO FIXING INTO BARE FOAM.",
        "THE LIFT BED'S FOUR HARDPOINTS, THE LOCKERS' AND THE TOWER'S INSERT STRIPS AND THE STIFFENERS ARE LAID UP IN THE PANELS. THE PLINTH "
        "AND THE TOWER ALSO BOLT THROUGH THE FLOOR TO THE CHASSIS (HARD POINTS, CT-104). THE SPLIT'S CRADLE (AC-03) BOLTS TO THE REAR WALL'S INSERT STRIP WITH "
        f"{b.d['cradle']['bolts']} M8 AND STANDS ON {b.d['cradle']['stays']['n']} STAYS TO THE REAR CROSSMEMBER (AC-04). THE WALL MEMBERS STOP "
        f"{b.d['panels']['wall']['stiffener']['end_gap_mm']:g} mm SHORT OF THE FLOOR AND ROOF JOINERS, ON A RIGID PVC PAD AT THE FOOT (CT-202 DETAIL F).",
        "PULL-TEST A SAMPLE OF EACH INSERT IN THE REAL PANEL BEFORE THE PANELS ARE ORDERED (report 02 LR-09).",
    ], width_chars=118, size=1.6)
    _stamp(sh, 320, 96)
    kg, kgg = _body_mass(rep)
    _title(sh, dwg, reg, f"BODY {kg:.0f} kg, {kgg:.0f} kg WITH GROWTH (TB-11).", k)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-301 body to chassis
def ct301(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, rep, res, b = _data(prj, model)
    V = lay.V
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    ox, oy = 22.0, 200.0
    sh.text(ox, oy + V["body_width"] / k + 5, "MOUNT POSITIONS, PLAN (FRONT LEFT, ROAD SIDE UP)", 2.2, bold=True)
    P = _plan_outline(sh, lay, ox, oy, k)
    n = 0
    for st in sorted(lay.chassis.stations, key=lambda s: s["x"]):
        x = lay.chassis.station_x(st)
        p = P(x, V["body_width"] / 2)
        sh.text(p[0], p[1] + 1.2, f"{x:.0f}", 1.3, "middle")
        for y in (-b.d["mounts"]["outrigger_tip_y"], -V["rail_c"], V["rail_c"], b.d["mounts"]["outrigger_tip_y"]):
            q = P(x, y)
            sh.circle(q[0], q[1], 0.9, "medium")
            n += 1
    sh.text(ox, oy - 4, f"{n} MOUNTS: ONE INTO EACH RAISER AT Y {V['rail_c']:.0f} AND ONE INTO EACH OUTRIGGER TIP AT Y "
            f"{b.d['mounts']['outrigger_tip_y']:.0f}, AT EVERY STATION (X ABOVE)", 1.5)
    # bolt detail, section across the raiser
    kk, cx, top = 3.0, 70.0, 188.0
    _dt(sh, cx, top, "A: BODY MOUNT, SECTION ACROSS THE RAISER", kk)
    zb = 112.0
    rh = 127
    rhs(sh, cx, zb + rh / 2 / kk, 51, rh, 3.5, 8.75, kk)                             # raiser RHS 127 x 51 x 3.5
    sh.rect(cx - 22 / kk, zb + (rh - 3.5 - 10) / kk, cx + 22 / kk, zb + (rh - 3.5) / kk, "shade")   # nut plate
    st = V["floor_underside_z"] - (V["rail_top_z"] + rh)
    sh.rect(cx - 25 / kk, zb + rh / kk, cx + 25 / kk, zb + (rh + st) / kk, "medium")
    S.hatch_rect(sh, cx - 25 / kk, zb + rh / kk, cx + 25 / kk, zb + (rh + st) / kk, 0.8)
    _sandwich(sh, cx - 60 / kk, zb + (rh + st) / kk, cx + 60 / kk, zb + (rh + st + 30) / kk, 2.0, kk)
    sh.rect(cx - 50 / kk, zb + (rh + st + 30) / kk, cx + 50 / kk, zb + (rh + st + 33) / kk, "fill")
    sh.rect(cx - 6 / kk, zb + (rh - 13) / kk, cx + 6 / kk, zb + (rh + st + 45) / kk, "medium")
    sh.line(cx, zb - 3, cx, zb + (rh + st + 50) / kk, "centre")
    weld_symbol(sh, (cx + 22 / kk, zb + (rh - 8) / kk), (cx + 16, zb + 24), "4", both=True, length="80", note="NUT PLATE")
    fb = b.d["mounts"]["fallback"]
    m = res["mounts"]
    for i, t in enumerate((f"{fb['name'].upper()}",
                           f"M12 8.8 HDG, {m['tension_n'] / 1000:.1f} kN WORST TENSION AGAINST {m['fallback']['bolt_n'] / 1000:.1f} kN (BDY-16)",
                           "100 x 100 x 3 ALUMINIUM SPREADER BONDED ON THE FLOOR, GRP CRUSH TUBE, HD PVC INSERT",
                           f"{st:.1f} mm EPDM-FACED HDPE BEARER STRIP ON THE RAISER (CH-S01). NOT BONDED TO THE STEEL",
                           "SHIM EACH OUTRIGGER TIP TO WITHIN 2 mm OF THE RAISER PLANE")):
        sh.text(22, 96 - 3 * i, t, 1.5)
    tw = res["twist"]
    rows = [(kk2, f"{v['shear'] / 1000:.2f}", f"{v['tension'] / 1000:.2f}", v["note"][:62]) for kk2, v in m["cases"].items()]
    y = S.table(sh, 230.0, 232.0, [("CASE", 14), ("SHEAR kN", 18), ("TENSION kN", 20), ("NOTE", 128)], rows, size=1.45, row_h=3.2,
                title="MOUNT FORCES PER BOLT")
    S.table(sh, 230.0, y - 7, [("TWIST LC5a", 70), ("CHASSIS deg", 25), ("BODY SHARE", 25), ("PEAK BOLT kN", 25)],
            [("BARE CHASSIS", f"{tw['bare_deg']:.3f}", "0 %", ""),
             ("BODY, ROOF JOINT NEGLECTED", f"{tw['open']['chassis_deg']:.3f}", f"{100 * tw['open']['share']:.0f} %", f"{tw['open']['mount_force_n'] / 1000:.1f}"),
             ("BODY, ROOF BONDED (THE DESIGN)", f"{tw['closed']['chassis_deg']:.3f}", f"{100 * tw['closed']['share']:.0f} %", f"{tw['closed']['mount_force_n'] / 1000:.1f}")],
            size=1.45, row_h=3.2, title="TWIST SHARING (FRAME MODEL WITH THE BODY AS A TORSION BOX)")
    hb = m["hb10"]
    S.notes(sh, 160, 176, [
        "ISOLATION (MAT-04): GALVANISED STEEL TOUCHES ONLY THE HDPE STRIP AND THE BOLT. THE CRUSH TUBE KEEPS ALUMINIUM OFF THE STEEL. "
        "DURALAC ON FAYING SURFACES AND A NYLON WASHER AND SLEEVE WHERE AN EXTRUSION SITS OVER STEEL.",
        "SEALING: MS POLYMER IN EVERY HOLE AND UNDER EVERY SPREADER. EVERY BOLT THROUGH AN INSERT, NEVER BARE FOAM.",
        "THE BODY IS NOT BONDED TO THE CHASSIS (report 12 OPTION B). TORQUE THE M12 TO 60 Nm (ESTIMATE, HDG 8.8 WITH A WASHER) AND RE-TORQUE AFTER THE FIRST ROUGH TRIP (FAIL-03).",
        "NUT PLATES CH-P14 ARE WELDED INSIDE THE RAISERS AND OUTRIGGER TIPS BEFORE GALVANISING (CT-101, CT-103). VENT THEM.",
        f"THE DESIGN USES THE NUT PLATE. A HOLLO-BOLT HB10 (report 12) WOULD WORK AT {hb['util']:.2f} OF ITS SAFE LOAD ON THE LIGHTER BODY, "
        "WITH LESS MARGIN THAN THE NUT PLATE.",
    ], width_chars=62, size=1.55)
    _stamp(sh, 320, 96)
    kg, kgg = _body_mass(rep)
    _title(sh, dwg, reg, f"BODY {kg:.0f} kg ON {n} MOUNTS (TB-11).", k)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

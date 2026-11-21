"""CT-001 general arrangement of the whole trailer (A3, third angle): plan section and kerb-side elevation in the
project datum, key dimensions, the bike box's jack-knife sweep, the mass and CoG schedule by load case and the
whole-trailer checks. Revision J: the trailer for the LandCruiser 79 (report 18, layout 1).
"""
from __future__ import annotations

import json
import time

from build123d import Keep, Plane

from ..build import BUILD, git_hash
from ..trailer import Trailer
from ..trailer_model import TrailerModel
from . import sheet as S
from .home_common import water_without_gcm_revision
from .sheets import _leaves

HEIGHT_AT = {"BD-13": "the awning case", "RF-01": "the solar panels"}   # what sets the travel height, by line


def _kg(v: float) -> str:
    """A mass to the whole kg, half up, as the site rounds it (Python's format rounds half to even: 316.5 kg to 316)."""
    from decimal import ROUND_HALF_UP, Decimal
    return f"{Decimal(str(v)).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"


def _cog(sh, x, y, label, r=1.6):
    """Centre of gravity symbol: a circle with two opposite quadrants filled."""
    sh.circle(x, y, r, "medium")
    sh.el.append(f'<path d="M{x:.2f},{sh._y(y):.2f} L{x + r:.2f},{sh._y(y):.2f} A{r:.2f},{r:.2f} 0 0,0 {x:.2f},{sh._y(y + r):.2f} Z" fill="#000"/>')
    sh.el.append(f'<path d="M{x:.2f},{sh._y(y):.2f} L{x - r:.2f},{sh._y(y):.2f} A{r:.2f},{r:.2f} 0 0,0 {x:.2f},{sh._y(y - r):.2f} Z" fill="#000"/>')
    sh.text(x + r + 0.8, y + 0.6, label, 1.7)


def ct001(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    rep = json.loads((BUILD / "trailer" / "trailer.json").read_text())
    tr = Trailer(prj)
    lay = tr.layout(**rep["solved"]["overrides"])
    V = lay.V
    tm = TrailerModel(lay)
    shapes = tm.all_shapes()
    sh = S.Sheet()
    S.frame(sh)
    sc = dwg["scale"]
    ch = rep["chassis"]
    sw = ch["sweep"]
    hb = V["half_bw"]
    fz = V["floor_z"]

    # ---- plan: section at 1,000 above the floor, looking down. Ball on the left, kerb side at the bottom
    zc = fz + 1000
    plan_src = [s for s in shapes if not s.label.startswith(("RF-", "BD-02", "BD-13"))]
    cut = S.section(_leaves(plan_src), Plane.XY.offset(zc), keep=Keep.BOTTOM)
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=40.0, oy=226.0)
    vP.draw(cut, sty="medium")
    S.view_label(sh, 110, 281, f"PLAN, SECTION 1000 ABOVE THE FLOOR (Z {zc:.0f})", sc)
    P = lambda x, y: vP.p(x, y, 0)  # noqa: E731  DIM-01 point (x, y) to the sheet
    a, b = P(-200, 0), P(V["body_x1"] + 200, 0)
    sh.line(a[0], a[1], b[0], b[1], "centre")
    o = P(0, 0)
    sh.circle(o[0], o[1], 1.3, "medium")
    sh.text(o[0] - 1.8, o[1] + 2.0, "DATUM", 1.7, "end")
    sh.text(P(-300, 0)[0], P(0, -hb)[1] - 3.2, "KERB SIDE (Y -)", 1.9)
    sh.text(P(-300, 0)[0], P(0, hb)[1] + 1.4, "ROAD SIDE (Y +)", 1.9)
    # the bike box's sweep about the ball (JK-01): the arc on the trailer's side of the ball
    r = sw["radius_mm"] / sc
    sh.el.append(f'<path d="M{o[0]:.2f},{sh._y(o[1] + r):.2f} A{r:.2f},{r:.2f} 0 0,1 {o[0]:.2f},{sh._y(o[1] - r):.2f}" {sh.STY["phantom"]}/>')
    sh.text(o[0] + 2.0, o[1] - r - 3.2, f"BIKE BOX SWEEP R {sw['radius_mm']:.1f}", 1.5)
    # zone lengths along the road side
    yd = P(0, hb)[1] + 9
    xs = [V["in_x0"], V["bed_x1"], V["rear_x0"], V["in_x1"]]
    labs = [f"{V['bed_x1'] - V['in_x0']:.0f} BED", f"{V['rear_x0'] - V['bed_x1']:.0f} LIVING", f"{V['in_x1'] - V['rear_x0']:.0f} WET ROOM"]
    for (x0, x1), lab in zip(zip(xs, xs[1:]), labs):
        S.hdim(sh, P(x0, hb)[0], P(0, hb)[1], P(x1, hb)[0], P(0, hb)[1], yd, lab, size=1.9)
    S.hdim(sh, P(V["body_x0"], hb)[0], P(0, hb)[1], P(V["body_x1"], hb)[0], P(0, hb)[1], yd + 6, f"{V['body_length']:.0f} BODY", size=1.9)
    xr = P(V["body_x1"], 0)[0]
    S.vdim(sh, xr, P(0, hb)[1], xr, P(0, -hb)[1], xr + 6, f"{V['body_width']:.0f} BODY", size=1.9)
    S.vdim(sh, xr, P(0, ch["width_road_y"])[1], xr, P(0, ch["width_kerb_y"])[1], xr + 12, f"{ch['overall_width']:.0f} OVERALL", size=1.9)
    xh = V["axle_x"] + V["rear_hub_dx"]
    S.vdim(sh, P(xh, V["hub_y"])[0], P(0, V["hub_y"])[1], P(xh, -V["hub_y"])[0], P(0, -V["hub_y"])[1], P(xh + 420, 0)[0],
           f"{V['track']:.0f} TRACK", size=1.8, ext=False)
    for x in (V["axle_x"] + V["front_hub_dx"], xh):
        p0, p1 = P(x, hb + 60), P(x, -hb - 60)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    db = ch["drawbar_box"]
    for x, y, t in (((V["in_x0"] + V["bed_x1"]) / 2, 400, "LIFT BED OVER"), ((V["in_x0"] + V["bed_x1"]) / 2, 250, "DESK UNDER IT"),
                    ((V["bed_x1"] + V["rear_x0"]) / 2, -150, "LIVING"), ((V["rear_x0"] + V["in_x1"]) / 2, 640, "WET ROOM"),
                    ((db[0] + db[3]) / 2, -620, "DRAWBAR BOX"), ((ch["spare_box"][0] + ch["spare_box"][3]) / 2, 520, "SPARE")):
        p = P(x, y)
        sh.text(p[0], p[1] - 0.8, t, 1.6, "middle")
    for k in (b for b in lay.blocks if b.keep_clear):
        x0, y0, _, x1, y1, _ = k.box
        p0, p1 = P(x0, y1), P(x1, y0)
        sh.rect(p0[0], p0[1], p1[0], p1[1], "phantom")
    b = lay.find("BD-07")
    p0, p1 = P(b.box[0], -(hb + 25)), P(b.box[3], -(hb + 25))
    sh.line(p0[0], p0[1], p1[0], p1[1], "thick")
    sh.text((p0[0] + p1[0]) / 2, p0[1] - 3.4, f"ENTRY DOOR {b.box[3] - b.box[0]:.0f}", 1.6, "middle")
    k = lay.find("EL-02")
    p0, p1 = P(k.box[0], -(hb + 25)), P(k.box[3], -(hb + 25))
    sh.line(p0[0], p0[1], p1[0], p1[1], "thick")
    sh.text((p0[0] + p1[0]) / 2 + 4.0, p0[1] - 6.2, f"BATTERY PLINTH {k.box[3] - k.box[0]:.0f}", 1.5, "middle")

    # ---- elevation from the kerb side, ball on the left (third angle: the plan sits above it)
    elev_src = [s for s in shapes if not s.label.startswith(("BD-01",))]
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=40.0, oy=104.0)
    vE.draw(_leaves(elev_src), sty="medium")
    S.view_label(sh, 110, 176, "ELEVATION FROM THE KERB SIDE", sc)
    E = lambda x, z: vE.p(x, 0, z)  # noqa: E731
    g0, g1 = E(-300, 0), E(V["body_x1"] + 300, 0)
    sh.line(g0[0], g0[1], g1[0], g1[1], "thick")
    sh.text(g1[0], g1[1] - 3.2, "GROUND, Z 0", 1.8, "end")
    yb = E(0, 0)[1] - 6
    S.hdim(sh, E(0, 0)[0], E(0, 0)[1], E(V["drawbar_length"], 0)[0], E(0, 0)[1], yb, f"{V['drawbar_length']:.0f} BALL TO BODY", size=1.9)
    S.hdim(sh, E(0, 0)[0], E(0, 0)[1], E(V["axle_x"], 0)[0], E(0, 0)[1], yb - 6, f"{V['axle_x']:.0f} BALL TO AXLE GROUP CENTRE", size=1.9)
    S.hdim(sh, E(ch["overall_x0"], 0)[0], E(0, 0)[1], E(ch["overall_x1"], 0)[0], E(0, 0)[1], yb - 12,
           f"{ch['overall_length']:.0f} OVERALL", size=1.9)
    hx = ch["hubs_x"]
    S.hdim(sh, E(hx[0], V["hub_z"])[0], E(0, V["hub_z"])[1], E(hx[1], V["hub_z"])[0], E(0, V["hub_z"])[1], E(0, V["hub_z"])[1] - 2.0,
           f"{V['axle_spacing']:.0f}", size=1.7, ext=False)
    for x in (*hx, V["axle_x"]):
        p0, p1 = E(x, -150), E(x, V["hub_z"] + 420)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    # the bike box's underside over the drawbar (JK-02), as far as its sweep reaches
    u0, u1 = E(0, sw["underside_z"]), E(sw["radius_mm"], sw["underside_z"])
    sh.line(u0[0], u0[1], u1[0], u1[1], "phantom")
    sh.text(u0[0] - 1.0, u0[1] + 1.0, f"BIKE BOX UNDERSIDE Z {sw['underside_z']:.0f}", 1.5, "end")
    xr = E(V["body_x1"], 0)[0]
    levels = [(V["coupling_z"], f"{V['coupling_z']:.0f} COUPLING POINT"), (V["rail_underside_z"], f"{V['rail_underside_z']:.0f} RAIL UNDERSIDE"),
              (fz, f"{fz:.0f} FLOOR"), (V["mattress_z"] + V["mattress_t"], f"{V['mattress_z'] + V['mattress_t']:.0f} MATTRESS TOP"),
              (V["ceiling_z"], f"{V['ceiling_z']:.0f} CEILING, FIXED ROOF"), (ch["travel_height"], f"{ch['travel_height']:.0f} TRAVEL HEIGHT")]
    ly = []
    for z, _ in levels:
        y = E(0, z)[1]
        ly.append(max(y, ly[-1] + 2.8) if ly else y)
    for (z, lab), yy in zip(levels, ly):
        y = E(0, z)[1]
        sh.line(xr + 1, y, xr + 4, y, "thin")
        sh.line(xr + 4, y, xr + 6, yy, "thin")
        sh.text(xr + 6.5, yy - 0.7, lab, 1.7)
    cz = E(0, V["coupling_z"])
    sh.line(cz[0] - 3, cz[1], cz[0] + 1, cz[1], "thin")
    o = E(0, 0)
    sh.circle(o[0], o[1], 1.3, "medium")
    sh.text(o[0] - 1.8, o[1] - 3.6, "DATUM", 1.7, "end")
    cases = {c["id"]: c for c in rep["cases"]}
    for cid, dy in (("TC1", 2.6), ("TC2", -2.6)):
        c = cases[cid]["nominal"]["cog"]
        p = E(c[0], c[2])
        _cog(sh, p[0], p[1], "")
        sh.text(p[0] + 2.4, p[1] + dy - 0.6, f"CoG {cid} {'TARE' if cid == 'TC1' else 'FULLY LOADED'}, Z {c[2]:.0f}", 1.6)

    # ---- front and rear views (third angle: the front view, seen from ahead, would sit to the right of the elevation's
    # front end. They are placed in the right column with their own labels)
    yr0 = S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                                     checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]], max_rows=8)
    gz = yr0 - 74.0
    vF = S.View(sh, (-1, 0, 0), (0, 0, 1), sc, ox=268.0, oy=gz)
    vF.draw(_leaves([s_ for s_ in shapes if not s_.label.startswith(("BD-01",))]), sty="medium")
    vR = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=362.0, oy=gz)
    vR.draw(_leaves([s_ for s_ in shapes if not s_.label.startswith(("BD-01", "DB-", "GS-", "DX-", "SP-", "PL-03A"))]), sty="medium")
    for vx, lab, left, right in ((268.0, "FRONT VIEW, FROM AHEAD", "ROAD", "KERB"), (362.0, "REAR VIEW, FROM BEHIND", "KERB", "ROAD")):
        sh.line(vx - 30, gz, vx + 30, gz, "thick")
        sh.line(vx, gz - 2, vx, gz + ch["travel_height"] / sc + 2, "centre")
        sh.text(vx, gz + ch["travel_height"] / sc + 5.0, lab, 2.0, "middle", bold=True)
        sh.text(vx, gz + ch["travel_height"] / sc + 2.4, f"SCALE 1:{sc:g}", 1.5, "middle")
        sh.text(vx - 29, gz - 3.0, left, 1.4)
        sh.text(vx + 29, gz - 3.0, right, 1.4, "end")
    S.hdim(sh, 362.0 + ch["width_kerb_y"] / sc, gz, 362.0 + ch["width_road_y"] / sc, gz, gz - 6.0, f"{ch['overall_width']:.0f} OVERALL", size=1.4)
    S.hdim(sh, 268.0 - V["half_bw"] / sc, gz, 268.0 + V["half_bw"] / sc, gz, gz - 6.0, f"{V['body_width']:.0f} BODY", size=1.4)
    xr2 = 362.0 + (V["half_bw"] + 30) / sc
    S.vdim(sh, xr2, gz, xr2, gz + ch["travel_height"] / sc, xr2 + 5, f"{ch['travel_height']:.0f}", size=1.4)
    # ---- key figures, right column (the case table is CT-002, the checks CT-003)
    plate = rep["caps"]["plated"]
    chk = {c["id"]: c for c in rep["checks"]}
    tc2 = cases["TC2"]
    w = rep["solved"]["window"]
    fails = [c["id"] for c in rep["checks"] if c["severity"] == "fail" and not c["ok"]]
    nf = sum(1 for c in rep["checks"] if c["severity"] == "fail")
    lo_ball = min(c["nominal"]["towball_kg"] for c in rep["cases"])
    hi_ball = max(c["nominal"]["towball_kg"] for c in rep["cases"])
    rows = [
        ["Body", f"{V['body_length']:.0f} x {V['body_width']:.0f} mm", f"Fixed roof, {rep['params']['interior_h']:.0f} mm inside, rounded front edges (H12)"],
        ["Overall", f"{ch['overall_length']:.0f} x {ch['overall_width']:.0f} mm", f"Travel height {ch['travel_height']:.0f} mm at the top of {HEIGHT_AT.get(ch['travel_height_at'], ch['travel_height_at'])}"],
        ["Axle group centre", f"X {V['axle_x']:,.0f}", f"Window X {w['x_lo']:,.0f} to {w['x_hi']:,.0f} (H17, MAS-05)"],
        ["Tare", f"{rep['tare_kg']:,.0f} kg", f"{cases['TC1']['growth']['mass_kg']:,.0f} kg with growth"],
        ["Fully loaded, TC2", f"{tc2['nominal']['mass_kg']:,.0f} kg", f"{tc2['growth']['mass_kg']:,.0f} kg with growth, ATM plate {plate:,.0f} kg"],
        ["Towball", f"{lo_ball:.0f} to {hi_ball:.0f} kg", f"{chk['MAS-12']['measured']:.1f} % lowest (TC7), {_kg(chk['MAS-13']['measured'])} kg heaviest with growth"],
        ["Ute rear axle", f"{chk['MAS-03']['measured']:,.0f} kg", f"Against the Elite kit's {rep['tow_vehicle']['limits']['rear_axle_kg']:,.0f} kg with growth (MAS-03)"],
        ["Combination", f"{chk['GCM-01']['measured']:,.0f} kg", f"Against Lovells' {rep['tow_vehicle']['limits']['gcm_kg']:,.0f} kg GCM revision (GCM-01)"],
        ["CoG, fully loaded", f"Z {ch['cog_loaded'][2]:,.0f}", f"Z {ch['cog_loaded_growth'][2]:,.0f} with growth. Across: {chk['MAS-11']['measured']:.1f} mm at worst (MAS-11)"],
        ["Coupling", f"{V['coupling_z']:.0f} mm", "Laden, plus or minus 20 mm (UTE-01). DO35 V3Plus"],
        ["Water", f"{rep['params']['water_full_l']:.0f} L net", f"At most {rep['params']['water_travel_l']:.0f} L in travel (H13), 130 L grey tank"],
        ["Wheels and tyres", f"{ch['tyre_d']:.0f} mm", "ROH Trak 2 16x7 ET 0, LT265/75R16, the ute's wheel"],
        ["Fail checks", f"{nf - len(fails)} of {nf} pass", ("FAILING: " + ", ".join(fails)) if fails else "Every fail check passes (CT-003 lists them by item)"],
    ]
    yk = S.table(sh, 230.0, gz - 14.0, [("KEY FIGURE", 34), ("VALUE", 30), ("NOTE", 116)], rows, size=1.5, row_h=3.1, title="KEY FIGURES")
    S.notes(sh, 230.0, yk - 6.0, [
        "THE SET: CT-002 MASS AND CoG, CT-003 COMPLIANCE, CT-010 TO CT-013 LAYOUT, CT-101 TO CT-104 CHASSIS AND LOAD PATHS, CT-201 TO "
        "CT-301 BODY, CT-601 TO CT-621 SERVICES, CT-701 TO CT-704 THE UTE'S BIKE BOX.",
    ], title="", size=1.4, width_chars=150)
    S.notes(sh, 22, 76, [
        "DATUM DIM-01: X FROM THE BALL CENTRE, POSITIVE REARWARD. Y FROM THE CENTRELINE, POSITIVE TO THE ROAD SIDE. Z UP FROM THE GROUND, "
        "TRAILER LEVEL AT DESIGN RIDE HEIGHT. A RIGHT-HANDED FRAME, SO THE 3D MODEL AND THESE VIEWS SHOW THE TRAILER AS IT IS.",
        (f"AXLE IN THE MIDDLE OF THE TOWBALL WINDOW, X {w['x_lo']:,.0f} TO {w['x_hi']:,.0f}: EVERY CASE KEEPS {w['pct_min']:.1f} % ON THE BALL AND "
         f"THE HEAVIEST TOWBALL WITH GROWTH STAYS AT OR UNDER {w['ball_max']['kg']:.0f} kg (H17, MAS-12, MAS-13). THE UTE'S REAR AXLE STAYS "
         f"WITHIN THE ELITE KIT'S {rep['tow_vehicle']['limits']['rear_axle_kg']:.0f} kg (MAS-03). NO BALLAST IN ANY CASE."),
        "REVISION " + dwg["revisions"][-1]["rev"] + ": THE HOME TRAILER. THE BIKES RIDE IN THE UTE'S BIKE BOX. THE LIFT BED OVER THE DESK ACROSS "
        f"THE FRONT, THE KITCHEN ON THE ROAD SIDE, THE BATTERY PLINTH ON THE KERB SIDE, THE WET ROOM ACROSS THE REAR. AT MOST "
        f"{rep['params']['water_travel_l']:.0f} L OF WATER IN TRAVEL (H13), {water_without_gcm_revision(rep)} L IF LOVELLS' GCM REVISION IS "
        "REFUSED (CT-003).",
        "ROOF (H12): FIXED, WITH ROUNDED FRONT EDGES (ABOUT +6 kg AND AUD 3,500, RESEARCH REPORT 25). TOWING FUEL IS ABOUT 21.3 L/100 km AT "
        "90 km/h AGAINST 25.0 FOR A SQUARE FRONT. A HARD-WALLED TELESCOPING ROOF GIVES 20.6 BUT COSTS +117 kg AND ABOUT AUD 32,900 MORE "
        "AND RULES OUT THE S4 WINDOWS, STOCK DOORS, THE HAPPIJAC BED AND A FULL-HEIGHT WET ROOM. A CANVAS POP-TOP FAILS H3 AND H7.",
        "THE TWO GENERATORS AND THE JERRY CANS RIDE IN A SEALED, VENTED DRAWBAR BOX BEHIND THE STONE GUARD, OUTSIDE THE BIKE BOX'S SWEEP. "
        "NO PETROL IN THE BODY. THE SPARE WHEEL STANDS ON THE FRONT WALL ABOVE THE BOX.",
        "XT AIR 4500 kg BUILD ON LC5 M14 HUBS AT 900 mm. THE UTE'S BALL SITS AT 440 mm LADEN, 1300 mm BEHIND ITS REAR AXLE (UTE-01, UTE-02).",
        "PHANTOM OUTLINES ON THE PLAN ARE FLOOR SPACE KEPT CLEAR (CT-010). THE ARC IS THE BIKE BOX'S SWEEP (JK-01).",
    ], width_chars=150, size=1.5)
    rev = dwg["revisions"][-1]
    tare = cases["TC1"]
    S.title_block(
        sh, owner=reg["owner"], project=dwg.get("project") or reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"], engineer="NOT REVIEWED", sheet_no=dwg["sheet"], sheets=reg["sheets_total"],
        size=dwg["size"], scale=sc, material="BLOCK LAYOUT, NONE CALLED UP",
        mass_note=f"TARE {int(rep['tare_kg'] + 0.5)} kg, {tare['growth']['mass_kg']:.0f} kg WITH GROWTH, ATM PLATE {plate:,.0f} kg (TB-11).",
        model_ref=f"trailer.step (ASM-TR rev {rep['assembly']['revision']})", git=git_hash())
    S.write(sh, BUILD / "drawings" / f"{dwg['number']}.svg")
    return time.time() - t0

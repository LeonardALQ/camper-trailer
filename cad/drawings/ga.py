"""CT-001 general arrangement of the whole trailer (A3, third angle): plan section and kerb-side elevation in the
project datum, key dimensions, the mass and CoG schedule by load case and the whole-trailer checks.

DIM-01 as written in research/02 (X rearward, Y to the kerb, Z up) is a left-handed frame, while the CAD kernel is
right-handed, so the 3D model is the mirror image of the real trailer. This sheet mirrors the shapes about the
centreline before projecting, so both views show the trailer as it will be seen. Labels give DIM-01 values.
"""
from __future__ import annotations

import json
import time

from build123d import Compound, Keep, Plane

from ..build import BUILD, git_hash
from ..trailer import ModuleInfo, Trailer
from ..trailer_model import TrailerModel
from . import sheet as S


def _mirror(shapes):
    out = []
    for s in shapes:
        kids = list(s.children) if isinstance(s, Compound) and s.children else [s]
        for k in kids:
            if isinstance(k, Compound) and k.children:
                out.extend(_mirror([k]))
            else:
                out.append(k.mirror(Plane.XZ))
    return out


def _cog(sh, x, y, label, r=1.6):
    """Centre of gravity symbol: a circle with two opposite quadrants filled."""
    sh.circle(x, y, r, "medium")
    sh.el.append(f'<path d="M{x:.2f},{sh._y(y):.2f} L{x + r:.2f},{sh._y(y):.2f} A{r:.2f},{r:.2f} 0 0,0 {x:.2f},{sh._y(y + r):.2f} Z" fill="#000"/>')
    sh.el.append(f'<path d="M{x:.2f},{sh._y(y):.2f} L{x - r:.2f},{sh._y(y):.2f} A{r:.2f},{r:.2f} 0 0,0 {x:.2f},{sh._y(y - r):.2f} Z" fill="#000"/>')
    sh.text(x + r + 0.8, y + 0.6, label, 1.7)


def ct001(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    rep = json.loads((BUILD / "trailer" / "trailer.json").read_text())
    tr = Trailer(prj, ModuleInfo.from_model(prj, model))
    lay = tr.layout(**rep["solved"]["overrides"])
    V = lay.V
    tm = TrailerModel(lay, model)
    shapes = tm.all_shapes()
    sh = S.Sheet()
    S.frame(sh)
    sc = dwg["scale"]
    ch = rep["chassis"]
    hb = V["half_bw"]
    fz = V["floor_z"]

    # ---- plan: section at 1,000 above the garage floor, looking down. Ball on the left, kerb side at the bottom
    zc = fz + 1000
    plan_src = [s for s in shapes if not s.label.startswith(("RF-", "BD-02", "BD-12", "BD-13"))]
    cut = S.section(_mirror(plan_src), Plane.XY.offset(zc), keep=Keep.BOTTOM)
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=30.0, oy=226.0)
    vP.draw(cut, sty="medium")
    S.view_label(sh, 110, 281, f"PLAN, SECTION 1000 ABOVE THE GARAGE FLOOR (Z {zc:.0f})", sc)
    P = lambda x, y: vP.p(x, -y, 0)  # noqa: E731  DIM-01 point (x, y) to the sheet, on the mirrored plan
    # centreline, datum and side labels
    a, b = P(-200, 0), P(V["body_x1"] + 200, 0)
    sh.line(a[0], a[1], b[0], b[1], "centre")
    o = P(0, 0)
    sh.circle(o[0], o[1], 1.3, "medium")
    sh.text(o[0] - 1.8, o[1] + 2.0, "DATUM", 1.7, "end")
    sh.text(P(300, 0)[0], P(0, hb)[1] + 0.5, "KERB SIDE (Y +)", 1.9)
    sh.text(P(300, 0)[0], P(0, -hb)[1] - 2.5, "ROAD SIDE (Y -)", 1.9)
    # zone lengths along the road side
    yd = P(0, -hb)[1] + 9
    xs = [V["in_x0"], V["part_a_x"], V["module_x0"], V["in_x1"]]
    labs = [f"{V['part_a_x'] - V['in_x0']:.0f} LIVING AREA", "", f"{V['in_x1'] - V['module_x0']:.0f} GARAGE"]
    for (x0, x1), lab in zip(zip(xs, xs[1:]), labs):
        if not lab:
            continue
        S.hdim(sh, P(x0, -hb)[0], P(0, -hb)[1], P(x1, -hb)[0], P(0, -hb)[1], yd, lab, size=1.9)
    S.hdim(sh, P(V["body_x0"], -hb)[0], P(0, -hb)[1], P(V["body_x1"], -hb)[0], P(0, -hb)[1], yd + 6, f"{V['body_length']:.0f} BODY", size=1.9)
    # widths at the rear
    xr = P(V["body_x1"], 0)[0]
    S.vdim(sh, xr, P(0, -hb)[1], xr, P(0, hb)[1], xr + 6, f"{V['body_width']:.0f} BODY", size=1.9)
    S.vdim(sh, xr, P(0, -hb)[1], xr, P(0, hb + 100)[1], xr + 12, f"{ch['overall_width']:.0f} WITH AWNING", size=1.9)
    # track, at the hubs
    xh = V["axle_x"] + V["rear_hub_dx"]
    S.vdim(sh, P(xh, -V["hub_y"])[0], P(0, -V["hub_y"])[1], P(xh, V["hub_y"])[0], P(0, V["hub_y"])[1], P(xh + 420, 0)[0],
           f"{V['track']:.0f} TRACK", size=1.8, ext=False)
    for x in (V["axle_x"] + V["front_hub_dx"], xh):
        p0, p1 = P(x, -hb - 60), P(x, hb + 60)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    # zone and item labels
    for x, y, t in (((V["in_x0"] + V["part_a_x"]) / 2, 0, "LIVING AREA"), ((V["module_x0"] + V["in_x1"]) / 2, -1060, "GARAGE"),
                    (V["module_x0"] + V["mod_locker_x0"] + 380, 900, "GAS LOCKER")):
        p = P(x, y)
        sh.text(p[0], p[1] - 0.8, t, 1.8, "middle")
    # keep-clear spaces as phantom outlines
    for k in (b for b in lay.blocks if b.keep_clear and b.zone == "living"):
        x0, y0, _, x1, y1, _ = k.box
        p0, p1 = P(x0, y0), P(x1, y1)
        sh.rect(p0[0], p0[1], p1[0], p1[1], "phantom")
    # doors
    for iid, side, t in (("BD-06", 1, "GAS HATCH"), ("BD-07", 1, "ENTRY DOOR")):
        b = lay.find(iid)
        p0, p1 = P(b.box[0], side * (hb + 25)), P(b.box[3], side * (hb + 25))
        sh.line(p0[0], p0[1], p1[0], p1[1], "thick")
        sh.text((p0[0] + p1[0]) / 2, p0[1] + (2.4 if side < 0 else -3.4), f"{t} {b.box[3] - b.box[0]:.0f}", 1.6, "middle")
    b = lay.find("BD-05")
    xg = V["body_x1"] + 25
    p0, p1 = P(xg, b.box[1]), P(xg, b.box[4])
    sh.line(p0[0], p0[1], p1[0], p1[1], "thick")
    sh.text(p0[0] + 1.5, (p0[1] + p1[1]) / 2 - 0.6, f"REAR DOOR {b.box[4] - b.box[1]:.0f}", 1.6, rot=-90)

    # ---- elevation from the kerb side, ball on the left (third angle: the plan sits above it)
    elev_src = [s for s in shapes if not s.label.startswith(("BD-01",))]
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=30.0, oy=104.0)
    vE.draw(_mirror(elev_src), sty="medium")
    S.view_label(sh, 110, 176, "ELEVATION FROM THE KERB SIDE, ROOF DOWN", sc)
    E = lambda x, z: vE.p(x, 0, z)  # noqa: E731
    g0, g1 = E(-300, 0), E(V["body_x1"] + 300, 0)
    sh.line(g0[0], g0[1], g1[0], g1[1], "thick")
    sh.text(g1[0], g1[1] - 3.2, "GROUND, Z 0", 1.8, "end")
    # horizontal dimensions below the ground line
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
    # heights on the right
    xr = E(V["body_x1"], 0)[0]
    levels = [(V["coupling_z"], f"{V['coupling_z']:.0f} COUPLING POINT"), (V["rail_underside_z"], f"{V['rail_underside_z']:.0f} RAIL UNDERSIDE"),
              (fz, f"{fz:.0f} GARAGE FLOOR"), (V["ceiling_z"], f"{V['ceiling_z']:.0f} CEILING, ROOF DOWN"),
              (ch["travel_height"], f"{ch['travel_height']:.0f} TRAVEL HEIGHT")]
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
    # centres of gravity
    cases = {c["id"]: c for c in rep["cases"]}
    for cid, dy in (("TC1", 2.6), ("TC2", -2.6)):
        c = cases[cid]["nominal"]["cog"]
        p = E(c[0], c[2])
        _cog(sh, p[0], p[1], "")
        sh.text(p[0] + 2.4, p[1] + dy - 0.6, f"CoG {cid} {'TARE' if cid == 'TC1' else 'FULLY LOADED'}, Z {c[2]:.0f}", 1.6)

    # ---- mass and CoG schedule by load case (MASS-03), right column
    rows = []
    for c in rep["cases"]:
        n, g = c["nominal"], c["growth"]
        rows.append([c["id"], c["name"][:30], f"{n['mass_kg']:.0f}", f"{g['mass_kg']:.0f}", f"{n['cog'][0]:.0f}", f"{n['cog'][2]:.0f}",
                     f"{n['towball_kg']:.0f}", f"{n['towball_pct']:.1f}", f"{n['axle_kg']:.0f}",
                     (f"{3500 - g['mass_kg']:+.0f}", "#000" if g["mass_kg"] <= 3500 else "#c00")])
    yt = S.table(sh, 230.0, 254.0, [("CASE", 10), ("WHAT IS ABOARD", 47), ("kg", 11), ("kg +GR", 13), ("CoG X", 13), ("CoG Z", 12),
                                    ("BALL kg", 14), ("BALL %", 13), ("AXLE kg", 14), ("ATM +GR", 33)], rows, size=1.6, row_h=3.2,
                 title="MASS AND CoG BY LOAD CASE (MASS-03). +GR = WITH MASS-06 GROWTH")
    # ---- whole-trailer checks
    rows = []
    for r in rep["checks"]:
        col = "#000" if r["ok"] else ("#c00" if r["severity"] == "fail" else "#b06000")
        val = "" if r["measured"] is None else f"{r['measured']:.1f} {r['unit']}"
        rows.append([r["id"], r["title"][:95], (val, col), (r["status"], col)])
    yt = S.table(sh, 230.0, yt - 5.5, [("CHECK", 13), ("TITLE", 119), ("MODEL", 25), ("RESULT", 23)], rows, size=1.6, row_h=3.0,
                 title="WHOLE-TRAILER CHECKS (data/checks.yaml)")
    # ---- key figures for the chassis and the engineer
    rows = [
        ["Rail outer width at the XT hinges", f"{ch['rail_outer_width']:.0f}", f"{ch['rail_outer_width_wide_track']:.0f} for a {ch['wide_track']:.0f} track"],
        ["Raiser, rail top to floor underside", f"{ch['raiser_h']:.0f}", f"rails {ch['rail_section'].split(' block')[0]}"],
        ["Axle group centre from the ball", f"{V['axle_x']:.0f}", f"hubs {hx[0]:.0f} and {hx[1]:.0f}"],
        ["CoG height, fully loaded", f"{ch['cog_loaded'][2]:.0f}", f"{ch['cog_loaded_growth'][2]:.0f} with growth"],
        ["Jack-knife at 90 deg, body corners", f"{ch['jackknife_body_mm']:.0f}", "plan clearance to the car"],
        ["Ballast to tow with no bikes", f"{rep['ballast']['kg']:.0f} kg", f"{rep['ballast']['growth_kg']:.0f} kg with growth, at X {rep['ballast']['x']:.0f}"],
    ]
    S.table(sh, 230.0, yt - 5.5, [("KEY FIGURE (mm)", 70), ("VALUE", 30), ("NOTE", 80)], rows, size=1.6, row_h=3.0, title="CHASSIS INPUTS")
    # ---- notes
    S.notes(sh, 22, 66, [
        "DATUM DIM-01: X FROM THE BALL CENTRE, POSITIVE REARWARD. Y FROM THE CENTRELINE, POSITIVE TO THE KERB SIDE. Z UP FROM THE GROUND, "
        "TRAILER LEVEL AT DESIGN RIDE HEIGHT. VIEWS SHOW THE TRAILER AS SEEN (DIM-01 IS LEFT-HANDED, SO THE 3D MODEL IS ITS MIRROR, SEE TRAILER.md).",
        "BLOCK LAYOUT. EVERY ITEM IS AN ENVELOPE WITH A MASS. POSITIONS MARKED PLACEHOLDER IN assemblies/trailer.yaml ARE NOT DESIGNED YET.",
        f"AXLE POSITION SOLVED FOR {rep['target_kg']:.0f} kg ON THE BALL FULLY LOADED. CHASSIS SECTIONS ARE BLOCK SIZES FOR THE ENGINEER TO SET.",
        f"REVISION C: GARAGE AT THE BACK WITH A REAR DOOR, HEAVY ITEMS AFT. WITH NO BIKES ABOARD CARRY {rep['ballast']['kg']:.0f} kg OF BALLAST AT THE BACK OF THE GARAGE "
        f"(TC1, TC4, TC5). THE REGISTRATION TARE EXCLUDES IT.",
        "PHANTOM OUTLINES ON THE PLAN ARE FLOOR SPACE KEPT CLEAR (DOOR LANDINGS, WALKWAY, LADDER LANDING).",
        ("MASS CHECKS " + ", ".join(c["id"] for c in rep["checks"] if c["type"] == "mass" and c["severity"] == "fail" and not c["ok"])
         + " FAIL WITH THE GROWTH ALLOWANCE. SEE TRAILER.md BEFORE ANY ENGINEER REVIEW.") if any(
            c["type"] == "mass" and c["severity"] == "fail" and not c["ok"] for c in rep["checks"]) else "EVERY MASS CHECK PASSES.",
    ], width_chars=118, size=1.7)
    S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                               checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]])
    rev = dwg["revisions"][-1]
    tare = cases["TC1"]
    tare_kg = rep["tare_kg"]
    S.title_block(
        sh, owner=reg["owner"], project=dwg.get("project") or reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"], engineer="NOT REVIEWED", sheet_no=dwg["sheet"], sheets=reg["sheets_total"],
        size=dwg["size"], scale=sc, material="BLOCK LAYOUT, NONE CALLED UP",
        mass_note=f"TARE {tare_kg:.0f} kg WITHOUT BALLAST, {tare['growth']['mass_kg'] - rep['ballast']['kg']:.0f} kg WITH GROWTH (TB-11).",
        model_ref=f"trailer.step (ASM-TR rev {rep['assembly']['revision']})", git=git_hash())
    S.write(sh, BUILD / "drawings" / f"{dwg['number']}.svg")
    return time.time() - t0

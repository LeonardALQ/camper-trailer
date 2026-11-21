"""The home trailer's whole-trailer sheets (TRAILER.md revision J, the H11 set), A3, third angle:

CT-002: mass and centre of gravity: every load case with and without growth, the axle window of decision H17, the
        centre of gravity in elevation and across the trailer, the tare by group and by maturity, and the least
        certain lines.
CT-003: compliance: the trailer's VSB1 items and the standards on one page with the design's figure for each, the
        operating limits (H13's water in travel and its fallback without the GCM revision, the towball range of H17),
        the vehicle plate and what is not designed yet.
CT-010: floor plan with the bed up (day and travel) and down (night), walkways, door swings and the spaces kept clear.
"""
from __future__ import annotations

import time

from build123d import Keep, Plane  # noqa: F401  (kept for the views that cut the model)

from ..trailer_model import TrailerModel
from . import sheet as S
from .home_common import MARK, Proj, body_plan, cog_symbol, ctx, label_in, stamp, textblock, title, tw, wrap, write
from .sheets import _leaves

TOYOTA_GCM = 6900   # Toyota's GCM, which holds if Lovells' 7,400 kg revision is refused (data/ute/ute.yaml gcm_kg source)


def _axes(sh, x0, y0, x1, y1, xr, yr, xt, yt, xl, yl, fmt_x="{:,.0f}", fmt_y="{:g}", right=None):
    """A ruled chart frame. xr, yr are the data ranges, xt, yt the tick values. right = (range, ticks, label, fmt) adds a
    second scale on the right. Returns the two mapping functions."""
    X = lambda v: x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0)  # noqa: E731
    Y = lambda v: y0 + (v - yr[0]) / (yr[1] - yr[0]) * (y1 - y0)  # noqa: E731
    sh.rect(x0, y0, x1, y1, "medium")
    for v in xt:
        sh.line(X(v), y0, X(v), y1, "grey")
        sh.text(X(v), y0 - 3.0, fmt_x.format(v), 1.4, "middle")
    for v in yt:
        sh.line(x0, Y(v), x1, Y(v), "grey")
        sh.text(x0 - 1.0, Y(v) - 0.5, fmt_y.format(v), 1.4, "end")
    sh.text((x0 + x1) / 2, y0 - 6.2, xl, 1.5, "middle")
    sh.text(x0 - 9.5, (y0 + y1) / 2, yl, 1.5, "middle", rot=-90)
    R = None
    if right:
        rr, rt, rl, rf = right
        R = lambda v: y0 + (v - rr[0]) / (rr[1] - rr[0]) * (y1 - y0)  # noqa: E731
        for v in rt:
            sh.line(x1, R(v), x1 + 1.0, R(v), "thin")
            sh.text(x1 + 1.5, R(v) - 0.5, rf.format(v), 1.4)
        sh.text(x1 + 10.5, (y0 + y1) / 2, rl, 1.5, "middle", rot=-90)
    return X, Y, R


def _ticks(lo, hi, step):
    import math
    v = math.ceil(lo / step) * step
    out = []
    while v <= hi + 1e-9:
        out.append(round(v, 6))
        v += step
    return out


def _ssf(c, track):
    x, y, z = c["cog"]
    return (track / 2 - abs(y)) / z


# ------------------------------------------------------------------ CT-002 mass and centre of gravity
def ct002(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    rep, V, tr, chk = C["rep"], C["V"], C["tr"], C["chk"]
    sh = S.Sheet()
    S.frame(sh)
    w = rep["solved"]["window"]
    track = rep["chassis"]["track"]

    # ---- the axle window (H17): lowest share and heaviest towball with growth against the axle position
    span = (w["x_hi"] - w["x_lo"]) + 120
    xs = [w["x_lo"] - 60 + i * span / 24 for i in range(25)]
    vals = [tr._window_values(x) for x in xs]
    pct = [v[0] for v in vals]
    ball = [v[1] for v in vals]
    pr_ = (round(min(min(pct), w["pct_min"]) - 0.6, 1), round(max(pct) + 0.1, 1))
    br_ = (min(ball) - 40, max(max(ball), w["ball_max"]["kg"]) + 15)
    X, Y, R = _axes(sh, 32, 206, 205, 268, (xs[0], xs[-1]), pr_, _ticks(xs[0], xs[-1], 20), _ticks(pr_[0], pr_[1], 0.2),
                    "AXLE GROUP CENTRE, X FROM THE BALL (mm)", "LOWEST TOWBALL SHARE, %", fmt_y="{:.1f}",
                    right=(br_, _ticks(br_[0], br_[1], 10), "HEAVIEST TOWBALL WITH GROWTH, kg", "{:.0f}"))
    sh.fillrect(X(w["x_lo"]), 206, X(w["x_hi"]), 268, "light")
    sh.rect(X(w["x_lo"]), 206, X(w["x_hi"]), 268, "thin")
    sh.path([(X(x), Y(p)) for x, p in zip(xs, pct)], "thick")
    sh.path([(X(x), R(b)) for x, b in zip(xs, ball)], "hidden")
    sh.line(32, Y(w["pct_min"]), 205, Y(w["pct_min"]), "medium")
    sh.line(32, R(w["ball_max"]["kg"]), 205, R(w["ball_max"]["kg"]), "medium")
    sh.text(34, Y(w["pct_min"]) + 0.8, f"{w['pct_min']:.1f} % (MAS-12)", 1.4)
    sh.text(203, R(w["ball_max"]["kg"]) + 0.8, f"{w['ball_max']['kg']:.0f} kg (MAS-13)", 1.4, "end")
    xa = V["axle_x"]
    sh.line(X(xa), 206, X(xa), 268, "centre")
    sh.text(X(xa), 270.0, f"AXLE X {xa:,.1f}, THE MIDDLE OF THE {w['width_mm']:.1f} mm WINDOW (MAS-05)", 1.6, "middle", bold=True)
    sh.text(X(w["x_lo"]) - 0.8, 208, f"X {w['x_lo']:,.1f}", 1.3, "end")
    sh.text(X(w["x_hi"]) + 0.8, 208, f"X {w['x_hi']:,.1f}", 1.3)
    sh.line(150, 213, 156, 213, "thick")
    sh.text(157, 212.5, "LOWEST SHARE, BOTH BASES (LEFT SCALE)", 1.3)
    sh.line(150, 210, 156, 210, "hidden")
    sh.text(157, 209.5, "HEAVIEST BALL WITH GROWTH (RIGHT)", 1.3)
    sh.text(118, 280.5, "THE AXLE WINDOW OF DECISION H17", 2.6, "middle", bold=True)

    # ---- centre of gravity, elevation (X, Z), every case on both bases
    pts = [(c["id"], bs, c[bs]["cog"]) for c in rep["cases"] for bs in ("nominal", "growth")]
    xr = (min(p[2][0] for p in pts) - 15, max(p[2][0] for p in pts) + 15)
    zr = (min(p[2][2] for p in pts) - 15, max(p[2][2] for p in pts) + 15)
    X2, Z2, _ = _axes(sh, 34, 122, 112, 186, xr, zr, _ticks(xr[0], xr[1], 25), _ticks(zr[0], zr[1], 25), "CoG X FROM THE BALL (mm)",
                      "CoG Z ABOVE THE GROUND (mm)")
    for cid, bs, c in pts:
        x, y = X2(c[0]), Z2(c[2])
        if bs == "nominal":
            sh.circle(x, y, 0.9, "medium")
        else:
            sh.circle(x, y, 0.9, "fill")
    for c in rep["cases"]:
        a, b = c["nominal"]["cog"], c["growth"]["cog"]
        sh.line(X2(a[0]), Z2(a[2]), X2(b[0]), Z2(b[2]), "thin")
        sh.text(X2(b[0]) + 1.3, Z2(b[2]) - 0.5, c["id"], 1.25)
    sh.text(34, 188.5, "OPEN: NO GROWTH. FILLED: WITH GROWTH", 1.3)
    sh.text(73, 196, "CENTRE OF GRAVITY IN ELEVATION", 2.2, "middle", bold=True)

    # ---- centre of gravity across the trailer (MAS-11)
    lim = next(c for c in rep["checks"] if c["id"] == "MAS-11")
    m = 50.0
    X3 = lambda i: 140 + i * 9.0  # noqa: E731
    Y3 = lambda v: 154 + v / m * 30  # noqa: E731
    sh.rect(136, 122, 212, 186, "medium")
    for v in (-50, -25, 0, 25, 50):
        sh.line(136, Y3(v), 212, Y3(v), "grey" if v else "thin")
        sh.text(135, Y3(v) - 0.5, f"{v:+.0f}" if v else "0", 1.4, "end")
    for v in (-50, 50):
        sh.line(136, Y3(v), 212, Y3(v), "fail")
    for i, c in enumerate(rep["cases"]):
        for j, bs in enumerate(("nominal", "growth")):
            y = c[bs]["cog"][1]
            x = X3(i) + j * 3.4
            sh.fillrect(x, min(Y3(0), Y3(y)), x + 3.0, max(Y3(0), Y3(y)), "shade" if j else "light")
        sh.text(X3(i) + 3.2, 119.0, c["id"], 1.25, "middle")
    sh.text(126.5, 154, "CoG Y (mm), + ROAD SIDE", 1.5, "middle", rot=-90)
    sh.text(174, 188.5, f"LIGHT: NO GROWTH. GREY: WITH GROWTH. RED: THE 50 mm RULE. WORST {lim['measured']:.1f} mm", 1.3, "middle")
    sh.text(174, 196, "CENTRE OF GRAVITY ACROSS THE TRAILER (MAS-11)", 2.2, "middle", bold=True)

    # ---- tables, right column
    yb = title(sh, dwg, reg, (f"TARE {rep['tare_kg']:.0f} kg, {C['cases']['TC1']['growth']['mass_kg']:.0f} kg WITH GROWTH. FULLY LOADED "
                              f"{C['cases']['TC2']['nominal']['mass_kg']:.0f} kg, {C['cases']['TC2']['growth']['mass_kg']:.0f} kg (TB-11)."),
               "BLOCK LAYOUT, NONE CALLED UP")
    rows = []
    for c in rep["cases"]:
        n, g = c["nominal"], c["growth"]
        rows.append([c["id"], c["name"][:42], f"{c['water_l']:.0f}", f"{n['mass_kg']:.0f}", f"{g['mass_kg']:.0f}", f"{g['cog'][0]:.0f}",
                     f"{g['cog'][1]:+.0f}", f"{g['cog'][2]:.0f}", f"{n['towball_kg']:.0f}", f"{g['towball_kg']:.0f}",
                     f"{min(n['towball_pct'], g['towball_pct']):.1f}", f"{g['axle_kg']:.0f}", f"{g['tyre_load_side_kg']:.0f}",
                     f"{_ssf(g, track):.3f}"])
    y = S.table(sh, 230, yb - 6, [("CASE", 9), ("WHAT IS ABOARD", 33), ("WATER L", 11), ("kg", 10), ("+GR", 10), ("X +GR", 11),
                                   ("Y +GR", 10), ("Z +GR", 10), ("BALL", 10), ("+GR", 9), ("% MIN", 10), ("AXLE +GR", 14),
                                   ("TYRE +GR", 14), ("SSF +GR", 19)], rows, size=1.4, row_h=3.1,
                title="LOAD CASES. +GR WITH THE MASS-06 GROWTH. kg, mm FROM THE BALL, Y + TO THE ROAD SIDE")
    g = rep["tare_by_group"]
    grow = [[k, f"{v['mass_kg']:.1f}", f"{v['growth_kg']:.1f}"] for k, v in g.items()]
    grow.append(["Tare", f"{sum(v['mass_kg'] for v in g.values()):.1f}", f"{sum(v['growth_kg'] for v in g.values()):.1f}"])
    y2 = S.table(sh, 230, y - 6, [("GROUP", 52), ("TARE kg", 20), ("+GR kg", 20)], grow, size=1.4, row_h=3.0, title="TARE BY GROUP")
    mat = {}
    for s in rep["schedule"]:
        if s["load"] != "tare":
            continue
        m_ = mat.setdefault(s["maturity"], [0.0, 0.0, 0])
        m_[0] += s["mass_kg"]
        m_[1] += s["mass_with_growth_kg"] - s["mass_kg"]
        m_[2] += 1
    order = [k for k in ("spec", "calculated", "estimate", "weighed") if k in mat]
    mrows = [[k, f"{mat[k][2]}", f"{mat[k][0]:.1f}", f"{mat[k][1]:.1f}"] for k in order]
    mrows.append(["All", f"{sum(mat[k][2] for k in order)}", f"{sum(mat[k][0] for k in order):.1f}", f"{sum(mat[k][1] for k in order):.1f}"])
    S.table(sh, 327, y - 6, [("BASIS", 22), ("LINES", 13), ("kg", 23), ("GROWTH kg", 25)], mrows, size=1.4, row_h=3.0,
            title="TARE BY BASIS (MASS-06)")
    S.notes(sh, 327, y - 6 - 3.0 * (len(mrows) + 1) - 7, [
        "GROWTH: 20 % ON AN ESTIMATE, 7 % ON A CALCULATED MASS, NONE ON A MAKER'S FIGURE OR A WEIGHING.",
        "A WEIGHED LINE REPLACES ITS ESTIMATE AND LOSES ITS GROWTH (TW-01 TO TW-03).",
    ], title="", size=1.35, width_chars=58)
    lrows = [[f"{u['id']} {u['name'][:58]}", f"{u['mass_kg']:.1f}", f"{u['growth_kg']:.1f}", f"{u['cog_x']:.0f}",
              f"{u['towball_per_20pct_kg']:+.1f}"] for u in rep["least_certain"]]
    S.table(sh, 230, y2 - 6, [("LEAST CERTAIN ESTIMATES", 104), ("kg", 14), ("+20 % kg", 18), ("CoG X", 16), ("BALL kg", 28)], lrows,
            size=1.4, row_h=3.0, title="THE ESTIMATES THAT MOVE THE TOWBALL MOST")

    S.notes(sh, 22, 108, [
        "DATUM DIM-01: X FROM THE BALL CENTRE, POSITIVE REARWARD. Y POSITIVE TO THE ROAD SIDE. Z UP FROM THE GROUND AT DESIGN RIDE HEIGHT.",
        "MASSES FROM THE MASS SCHEDULE (data/assemblies/trailer.yaml, MASS-03). THE TOWBALL AND THE AXLE GROUP LOAD COME FROM MOMENTS "
        "ABOUT THE AXLE GROUP CENTRE (MASS-04). THE TYRE COLUMN IS VSB1'S 120 % OF THE HEAVIER SIDE'S SHARE OVER ITS TWO TYRES (MAS-06).",
        f"WATER: AT MOST {V['water_travel_l']:.0f} L OF FRESH AND GREY WATER IN TRAVEL (H13). TC7 CARRIES A FULL GREY TANK AND THE REST AS "
        "FRESH WATER, SO IT HAS THE LOWEST TOWBALL SHARE. TC8 CARRIES ONLY GREY WATER.",
        f"H17 SETS THE AXLE IN THE MIDDLE OF THE WINDOW BETWEEN {w['pct_min']:.1f} % IN THE LOWEST CASE AND {w['ball_max']['kg']:.0f} kg WITH "
        "GROWTH IN THE HEAVIEST. THE HARD LIMITS SIT OUTSIDE IT: 7.5 % (MAS-04, H2), THE TOWBAR'S 350 kg AND THE UTE'S REAR AXLE (MAS-03).",
        f"SSF IS HALF THE {track:.0f} mm TRACK LESS THE CoG'S OFFSET, OVER THE CoG HEIGHT, WITH GROWTH. NO RULE SETS A MINIMUM. "
        f"THE LOWEST IS {min(_ssf(c['growth'], track) for c in rep['cases']):.3f}.",
        f"WEIGH THE FINISHED TRAILER (TW-03) AND THE TOWBALL (TBS-01: WITHIN 10 % OF THE MODEL'S "
        f"{C['cases']['TC2']['nominal']['towball_kg']:.0f} kg FULLY LOADED) "
        "BEFORE THE FIRST TOW. A WEIGHED TOWBALL OUTSIDE THE WINDOW MOVES THE AXLE BEFORE THE CHASSIS IS WELDED.",
    ], width_chars=185, size=1.5)
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-003 compliance
def ct003(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    rep, V, chk, lay = C["rep"], C["V"], C["chk"], C["day"]
    ch, tv = rep["chassis"], rep["tow_vehicle"]
    sh = S.Sheet()
    S.frame(sh)
    sc = dwg["scale"]
    shapes = _leaves(TrailerModel(lay).all_shapes())
    # ---- kerb-side elevation and rear view with the compliance dimensions
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=32.0, oy=214.0)
    vE.draw([s for s in shapes if not s.label.startswith("BD-01")], sty="medium")
    E = lambda x, z: vE.p(x, 0, z)  # noqa: E731
    g0, g1 = E(-400, 0), E(V["body_x1"] + 500, 0)
    sh.line(g0[0], g0[1], g1[0], g1[1], "thick")
    S.hdim(sh, E(ch["overall_x0"], 0)[0], E(0, 0)[1], E(ch["overall_x1"], 0)[0], E(0, 0)[1], E(0, 0)[1] - 13,
           f"{ch['overall_length']:.0f} OVERALL", size=1.6)
    S.hdim(sh, E(V["body_x0"], 0)[0], E(0, 0)[1], E(V["axle_x"], 0)[0], E(0, 0)[1], E(0, 0)[1] - 7,
           f"{V['axle_x'] - V['body_x0']:.0f} FRONT LOAD SPACE", size=1.4)
    S.hdim(sh, E(V["axle_x"], 0)[0], E(0, 0)[1], E(ch["overall_x1"], 0)[0], E(0, 0)[1], E(0, 0)[1] - 7,
           f"{ch['overall_x1'] - V['axle_x']:.0f} REAR OVERHANG", size=1.4)
    xr = E(ch["overall_x1"], 0)[0]
    S.vdim(sh, xr, E(0, 0)[1], xr, E(0, ch["travel_height"])[1], xr + 5, f"{ch['travel_height']:.0f} TRAVEL HEIGHT", size=1.4)
    cz = E(0, V["coupling_z"])
    S.vdim(sh, cz[0], E(0, 0)[1], cz[0], cz[1], cz[0] - 4, f"{V['coupling_z']:.0f}", size=1.4)
    sh.text(cz[0] - 7.5, cz[1] + 2.2, "COUPLING", 1.3, "middle")
    p = E(V["axle_x"], 0)
    sh.line(p[0], p[1] - 2, p[0], p[1] + 16, "centre")
    sh.text(E(V["body_x0"], 0)[0] + 1, E(0, ch["travel_height"])[1] + 7.5, "ELEVATION FROM THE KERB SIDE", 2.2, bold=True)
    sh.text(E(V["body_x0"], 0)[0] + 1, E(0, ch["travel_height"])[1] + 4.2, f"SCALE 1:{sc:g}", 1.6)
    vR = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=192.0, oy=214.0)
    vR.draw([s for s in shapes if not s.label.startswith(("BD-01", "DB-"))], sty="medium")
    Rr = lambda y, z: vR.p(0, y, z)  # noqa: E731
    sh.line(Rr(-1500, 0)[0], Rr(0, 0)[1], Rr(1500, 0)[0], Rr(0, 0)[1], "thick")
    yt = Rr(0, ch["travel_height"])[1] + 4
    S.hdim(sh, Rr(-V["half_bw"] - 100, 0)[0], yt - 4, Rr(V["half_bw"], 0)[0], yt - 4, yt + 2, f"{ch['overall_width']:.0f} WITH THE AWNING", size=1.4)
    S.hdim(sh, Rr(-V["half_bw"], 0)[0], Rr(0, 0)[1], Rr(V["half_bw"], 0)[0], Rr(0, 0)[1], Rr(0, 0)[1] - 6, f"{V['body_width']:.0f} BODY", size=1.4)
    sh.text(Rr(0, 0)[0], yt + 6.5, "REAR VIEW", 2.2, "middle", bold=True)

    # ---- the compliance table, item by item (report 02 section 2, VSB1 Rev 6)
    def st(cid):
        c = chk.get(cid)
        if not c:
            return ("", "#000")
        return (f"{c['status']} ({cid})", "#000" if c["ok"] else ("#c00" if c["severity"] == "fail" else "#b06000"))

    def mv(cid, fmt="{:,.0f}"):
        c = chk[cid]
        return fmt.format(c["measured"]) + (f" {c['unit']}" if c.get("unit") else "")

    gcm = chk["GCM-01"]["gcm"]
    uc = {c["id"]: c for c in C["ute"]["checks"]}
    rows = [
        ["ATM", "Builder's rating from the chassis, axles, tyres and stability (VSB1 p. 9). Plate H2", f"{rep['caps']['plated']:,.0f} kg plate. Heaviest case with growth {mv('MAS-01')}", st("MAS-01")],
        ["Design margin", "Every case with growth at most 3,400 kg (H2, MAS-10)", f"{mv('MAS-10')} (TC2)", st("MAS-10")],
        ["GTM, NSW cap", "Lowest of the tyre, coupling, chain and brake ratings (report 02 section 2.1)", f"Cap {rep['caps']['gtm']:,.0f} kg. Axle group with growth {mv('MAS-07')}", st("MAS-07")],
        ["Axle kit", "Axles carry 120 % of their share where they do not share load (VSB1)", f"Kit GTM {rep['supplier']['kit_gtm']:,.0f} kg against {mv('MAS-02')}", st("MAS-02")],
        ["Tyres", "LT265/75R16 123/120 E, 1,550 kg each, with VSB1's 120 % on the heavier side", f"{mv('MAS-06')} on the heavier side", st("MAS-06")],
        ["Wheels", "ROH Trak 2 rating (WHL-01), with the same 120 % rule", f"{mv('MAS-09')} on the heavier side", st("MAS-09")],
        ["Brakes", "Over 2,000 kg GTM: brakes on every wheel, breakaway held 15 min (VSB1 8.2)", "12 in electric drums on four wheels, Bosch TSC, breakaway kit DB-07", ("ALL WHEELS", "#000")],
        ["Coupling", "AS 4177.3 50 mm ball, or an off-road coupling with a type approval (VSB1 9.3)", "Cruisemaster DO35 V3Plus, ADR rated 3,500 kg", ("RATED 3,500 kg", "#000")],
        ["Safety chains", "Two above 2,500 kg ATM to AS 4177.4, 4177-35 (VSB1 9.2.1)", "Two chains DB-06. Lugs at 34.3 kN and 17.2 kN (VSB1 9.2.2)", st("LOC-02")],
        ["Drawbar", "9.81 x ATM along and 0.5 x 9.81 x ATM down (VSB1 9.1)", f"Peak {chk['CHS-06']['measured']:.0f} MPa at 17.2 kN up, {chk['CHS-06B']['measured']:.0f} MPa down", st("CHS-06")],
        ["Towball height", "Ball 350 to 460 mm loaded, trailer level in it (VSB1 9.3.2)", f"{V['coupling_z']:.0f} mm, plus or minus 20 mm (UTE-01)", st("DIM-03")],
        ["Towball load", "Every case at least 7.5 % (H2), design at least 8.0 % and 320 kg (H17)", f"{chk['MAS-12']['measured']:.1f} % lowest, {chk['MAS-13']['measured']:.0f} kg heaviest with growth", st("MAS-12")],
        ["Running clearance", "At least 100 mm, unladen (VSB1 5.4)", f"{mv('DIM-04')}, the coupling's handbrake", st("DIM-04")],
        ["Width", "Across the body, guards and awning, at most 2,500 mm (VSB1 2, 5.2)", f"{mv('DIM-01')} with the awning", st("DIM-01")],
        ["Overhang", "Front load space at least the rear overhang (VSB1 5.1.1)", f"{V['axle_x'] - V['body_x0']:.0f} against {ch['overall_x1'] - V['axle_x']:.0f} mm", st("DIM-02")],
        ["Combination", "Ute and trailer within Lovells' 7,400 kg GCM revision (H2, GV06)", f"{gcm['plan']:,.0f} kg plan, {gcm['model']:,.0f} kg on the model", st("GCM-01")],
        ["Ute rear axle", "Towball keeps the Elite kit's 2,850 kg rear axle with growth (H14, H17)", f"{mv('MAS-03')} at the heaviest ball", st("MAS-03")],
        ["Jack-knife", "Front parts 100 mm outside the bike box's sweep, 50 mm under it (JK-01, JK-02)", f"{chk['JK-01']['measured']:.0f} mm and {chk['JK-02']['measured']:.0f} mm", st("JK-01")],
        ["Plug", "7 or 12 pin to AS 4177.5 (VSB1 7.2)", "12-pin flat plug, and a grey Anderson SB50 for the 48 V charging feed", ("AS 4177.5", "#000")],
        ["Wiring", "Supported every 600 mm, insulated joints, grommets through metal, earth wire (VSB1 7.1)", "Two-wire DC, no chassis return (report 20). Glands on CT-602", ("CT-601, CT-602", "#000")],
        ["230 V", "AS/NZS 3001.2:2022: RCD on the inverter's output, labelled (VSB1 7.3)", "30 mA RCBO on every circuit, board labelled, licensed electrician", ("CT-601", "#000")],
        ["Battery", "Sealed compartment vented outside, BMS, fuse within 1 m sleeved (AS/NZS 3001.2 5.4)", "Sealed 2 mm 5052 box, two 20 mm vents through the floor (G6, G7)", ("CT-602", "#000")],
        ["Doors", "Outward opening, one on the left (kerb) side or the rear (VSB1 13.2.1)", "D1 kerb side and D2 rear, both outward, triple locks", ("CT-010, CT-013", "#000")],
        ["Extinguisher", "1A:5B, one a compartment, smoke alarm (VSB1 13.2.2)", "1A:20B:(E) and fire blanket at D1, smoke and CO alarms (LA-12, LA-15)", ("ASK THE INSPECTOR", "#b06000")],
        ["LPG", "Caravan LPG code and AS/NZS 5601 (VSB1 13.2.4)", "None fitted. Cooking, hot water and heat are electric or diesel", ("NONE", "#000")],
        ["Mud flaps", "Behind the rear wheels", "610 x 455 mm rubber on the XT rear shock outriggers (BD-10)", ("BD-10", "#000")],
        ["Number plate", "No part above 1,300 mm, lit (VSB1 3.1)", "Not designed yet", ("OPEN", "#b06000")],
        ["Lamps, reflectors", "ADR positions and heights (report 02 CT-003)", "Not designed yet", ("OPEN", "#b06000")],
    ]
    y = S.table(sh, 22, 186, [("ITEM", 25), ("THE RULE AND ITS SOURCE", 84), ("THE DESIGN", 72), ("RESULT", 25)], rows, size=1.32,
                row_h=2.95, title="VSB1 AND THE STANDARDS, ITEM BY ITEM (report 02 section 2, VSB1 REV 6)")
    S.notes(sh, 22, y - 5, [
        "WIDTH, HEIGHT AND LENGTHS ARE MEASURED ON THE 3D MODEL AT DESIGN RIDE HEIGHT. THE BODY IS 2,400 mm, THE AWNING TAKES IT TO 2,500 mm.",
        "LAMPS, REFLECTORS AND THE NUMBER PLATE ARE NOT DESIGNED YET. THEY GO ON THIS SHEET WITH THEIR HEIGHTS WHEN THE LAMPS ARE CHOSEN.",
        "THE WET ROOM HAS ITS OWN OUTSIDE DOOR. ASK THE INSPECTOR WHETHER IT COUNTS AS A SECOND COMPARTMENT FOR VSB1 13.2.2 (A SECOND EXTINGUISHER).",
    ], width_chars=185, size=1.45)

    # ---- right column: operating limits, the plate, notes
    yb = title(sh, dwg, reg, f"ATM PLATE {rep['caps']['plated']:,.0f} kg. TARE ON THE PLATE FROM THE WEIGHBRIDGE (TW-03) (TB-11).",
               "AS NOTED, SEE THE SHEETS NAMED")
    lim = tv["limits"]
    model_over = gcm["model"] - TOYOTA_GCM
    water_fb = int(V["water_travel_l"] - max(0.0, model_over))
    plate_fb = TOYOTA_GCM - (gcm["plan"] - rep["caps"]["plated"])
    lines = [
        ("WATER IN TRAVEL (H13)", f"AT MOST {V['water_travel_l']:.0f} L OF FRESH AND GREY WATER WHILE TOWING. FILL THE TANKS AT CAMP (420 L NET)."),
        ("WITHOUT THE GCM REVISION", f"IF LOVELLS' {lim['gcm_kg']:,.0f} kg GCM REVISION (GV06) IS REFUSED, TOYOTA'S {TOYOTA_GCM:,} kg HOLDS: AT MOST "
                                     f"{water_fb} L OF WATER IN TRAVEL ({model_over:.0f} kg LESS THAN THE MODEL'S {gcm['model']:,.0f} kg), AND THE "
                                     f"TRAILER PLATED AT OR BELOW {plate_fb:,.0f} kg FOR THE PLAN'S SUM."),
        ("GCM (GCM-01)", f"{lim['gcm_kg']:,.0f} kg WITH THE REVISION. THE UTE WEIGHED AT MOST {lim['weighed_max_kg']:,.0f} kg WITH THE BALL LOAD (UTE-04)."),
        ("ATM AND DESIGN LIMIT", f"PLATE {rep['caps']['plated']:,.0f} kg. EVERY CASE WITH GROWTH AT MOST 3,400 kg (MAS-10)."),
        ("TOWBALL (H17)", f"AT LEAST {rep['solved']['window']['pct_min']:.1f} % OF THE TRAILER IN EVERY CASE AND AT MOST "
                          f"{rep['solved']['window']['ball_max']['kg']:.0f} kg WITH GROWTH. TOWBAR AND DO35 {lim['towball_rating_kg']:.0f} kg."),
        ("THE UTE (H17)", f"LOVELLS ELITE, {lim['gvm_kg']:,.0f} kg GVM, REAR AXLE {lim['rear_axle_kg']:,.0f} kg ({uc['UTE-03']['measured']:,.0f} kg "
                          f"TOWING WITH GROWTH). {lim['platinum_rear_axle_kg']:,.0f} kg IF CUT CUT7 RETURNS TO THE PLATINUM."),
        ("COUPLING HEIGHT", f"{V['coupling_z']:.0f} mm LADEN, PLUS OR MINUS 20 mm. SET THE TONGUE'S DROP AT THE FINAL WEIGHING (TW08)."),
        ("GREY WATER", f"EMPTY FOR TRAVEL. A FULL {V['grey_full_l']:.0f} L TANK IS CHECKED IN CASES TC7 AND TC8."),
    ]
    yy = yb - 13
    top = yb - 4
    sh.text(232, yb - 8.5, "OPERATING LIMITS (FOR THE PLATE, THE OWNER'S MANUAL AND THE INSPECTOR)", 2.2, bold=True)
    for head, body in lines:
        sh.text(232, yy, head, 1.4, bold=True)
        wl = wrap(body, 112)
        for i, t in enumerate(wl):
            sh.text(270, yy - i * 2.2, t, 1.4)
        yy -= 2.2 * max(1, len(wl)) + 1.2
    sh.rect(230, yy + 0.4, 410, top, "thick")
    yp = yy - 6
    sh.text(232, yp, "VEHICLE PLATE (VSB1 13.1.1)", 2.2, bold=True)
    yq = textblock(sh, 232, yp - 4, wrap(
        "MAKE (CONCESSIONAL TRAILER), VIN, ATM, GTM AND TARE, EMBOSSED, ETCHED OR ENGRAVED IN BLOCK LETTERS AT LEAST 2.5 mm HIGH, "
        "MATCHING THE RAV ENTRY. NSW ALSO LOOKS FOR THE MODEL AND THE DATE OF MANUFACTURE (VIB 78). THE GTM TO PLATE IS SET WITH THE "
        f"ENGINEER, AT MOST THE NSW CAP OF {rep['caps']['gtm']:,.0f} kg. THE PLATE AND VIN POSITIONS ARE NOT DESIGNED YET. PHOTOGRAPH "
        "THE VIN STAMPING BEFORE AND AFTER GALVANISING (REG-02).", 150), size=1.4, gap=0.85)
    S.notes(sh, 232, yq - 4, [
        "EVERY FIGURE ON THIS SHEET COMES FROM THE MODEL'S CHECKS (data/checks.yaml, data/ute/ute.yaml) AT THE SOLVED AXLE.",
        "A RESULT IN AMBER IS A QUESTION FOR THE INSPECTOR OR AN ITEM NOT DESIGNED YET. NO CHECK FAILS.",
    ], size=1.4, width_chars=150)
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-010 floor plan
def _bed_section(sh, lay_day, lay_night, k, ox, oy):
    """A small kerb-side elevation of the bed zone: the desk, the bed by day (phantom) and by night."""
    V = lay_day.V
    pr = Proj(sh, "kerb", k, ox, oy, ref=(V["in_x0"], 0, V["floor_z"]))
    x0, x1 = V["in_x0"], V["bed_x1"]
    pr.box((x0, 0, V["floor_z"], x1, 0, V["ceiling_z"]), "thin")
    pr.fill((x0 - 35, 0, V["floor_z"] - 30, x1, 0, V["floor_z"]), "shade")
    pr.fill((x0 - 35, 0, V["ceiling_z"], x1, 0, V["ceiling_z"] + 40), "shade")
    pr.fill((x0 - 35, 0, V["floor_z"] - 30, x0, 0, V["ceiling_z"] + 40), "shade")
    d = lay_day.find("LA-09").box
    pr.fill((d[0], 0, d[2], d[3], 0, d[5]), "light")
    pr.box((d[0], 0, d[2], d[3], 0, d[5]), "medium")
    pr.line((d[3] - 30, 0, d[2]), (d[3] - 30, 0, V["floor_z"]), "medium")
    for lay, sty in ((lay_day, "phantom"), (lay_night, "medium")):
        for iid in ("LB-03", "LB-01"):
            b = lay.find(iid).box
            pr.box((b[0], 0, b[2], b[3], 0, b[5]), sty)
    bd, bn = lay_day.find("LB-03").box, lay_night.find("LB-03").box
    mt = lay_night.find("LB-01").box[5]
    fz = V["floor_z"]
    xd = pr.p(x1, 0, 0)[0]
    for z, t in ((bd[2], f"{bd[2] - fz:.0f} DAY UNDERSIDE"), (bn[2], f"{bn[2] - fz:.0f} NIGHT UNDERSIDE"),
                 (mt, f"{mt - fz:.0f} NIGHT MATTRESS TOP"), (d[5], f"{d[5] - fz:.0f} DESK TOP")):
        p = pr.p(x1, 0, z)
        sh.line(xd + 0.5, p[1], xd + 3, p[1], "thin")
        sh.text(xd + 3.5, p[1] - 0.5, t, 1.3)
    p0, p1 = pr.p(x0 + 300, 0, d[5]), pr.p(x0 + 300, 0, bn[2])
    sh.text(p0[0] + 1, (p0[1] + p1[1]) / 2 - 0.5, f"{bn[2] - d[5]:.0f}", 1.3)
    p2 = pr.p(x0 + 700, 0, mt)
    p3 = pr.p(x0 + 700, 0, V["ceiling_z"])
    S.vdim(sh, p2[0], p2[1], p3[0], p3[1], p2[0], f"{V['ceiling_z'] - mt:.0f} CLEAR", size=1.2, ext=False)
    sh.text(pr.p(x0, 0, 0)[0], pr.p(0, 0, V["ceiling_z"] + 40)[1] + 2.0, "BED ZONE FROM THE KERB SIDE (PHANTOM: DAY)", 1.6, bold=True)


def ct010(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    rep, res, V = C["rep"], C["res"], C["V"]
    day, night = C["day"], C["night"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    hb = V["half_bw"]
    show = {"LA-09", "LA-11T", "LA-11B", "LA-07A", "LA-07B", "EL-02", "LA-02", "LA-14", "EL-04",
            "WR-06", "WR-07", "WR-08", "WR-09", "WR-10", "WR-11", "LB-01", "LB-04.1", "LB-04.2", "LB-04.3", "LB-04.4"}
    for lay, oy, head, cut in ((day, 205.0, "DAY AND TRAVEL: BED UP. PLAN 1000 ABOVE THE FLOOR", 1000.0),
                               (night, 110.0, "NIGHT: BED DOWN. PLAN 1000 ABOVE THE FLOOR", 1000.0)):
        pr = Proj(sh, "plan", k, 30.0, oy, ref=(V["body_x0"], -hb, 0))
        r = body_plan(sh, pr, lay, res, cut=cut, show=show, size=1.3, light=("LB-01",) if lay is night else (),
                      hidden=("LA-09",) if lay is night else (), nolabel=("EL-02", "LA-11B"))
        pl, bn = lay.find("EL-02").box, lay.find("LA-11B").box
        pr.text(((pl[0] + lay.find("LA-02").box[3]) / 2, (pl[4] + lay.find("LA-02").box[4]) / 2), "PLINTH", 1.25)
        pr.text(((bn[0] + bn[3]) / 2 + 60, bn[1] + 70), "BENCH", 1.25)
        # zone lengths along the road side
        yd = pr.p(0, hb)[1] + 3.5
        xs = [V["in_x0"], V["bed_x1"], V["rear_x0"], V["in_x1"]]
        for (a, b), lab in zip(zip(xs, xs[1:]), (f"{V['bed_x1'] - V['in_x0']:.0f} BED AND DESK", f"{V['rear_x0'] - V['bed_x1']:.0f} LIVING",
                                                 f"{V['in_x1'] - V['rear_x0']:.0f} WET ROOM")):
            S.hdim(sh, pr.p(a, hb)[0], pr.p(0, hb)[1], pr.p(b, hb)[0], pr.p(0, hb)[1], yd, lab, size=1.3)
        sh.text(30, yd + 6.0, head, 2.2, bold=True)
        # walkway widths
        k4 = lay.find("LA-K4").box
        xa = (k4[0] + k4[3]) / 2 + 120
        p0, p1 = pr.p(xa, k4[1]), pr.p(xa, k4[4])
        S.vdim(sh, p0[0], p0[1], p1[0], p1[1], p0[0], f"{k4[4] - k4[1]:.0f}", size=1.25, ext=False)
        k5 = lay.find("LA-K5").box
        p0, p1 = pr.p(k5[3] - 60, k5[1]), pr.p(k5[3] - 60, k5[4])
        S.vdim(sh, p0[0], p0[1], p1[0], p1[1], p0[0], f"{k5[4] - k5[1]:.0f}", size=1.2, ext=False)
        if lay is day:
            tx = pr.p((V["in_x0"] + V["bed_x1"]) / 2, -880)
            sh.text(tx[0], tx[1], "BED ABOVE, DASHED", 1.25, "middle")
        for kid in ("LA-K1", "LA-K2", "LA-K3", "LA-K4", "LA-K5", "LA-K6"):
            if kid in r:
                rr = r[kid]
                sh.text(rr[0] + 0.8, rr[1] + 0.8, kid.split("-")[1], 1.2, color="#555")
        wl = lay.find("WR-10").box
        q = pr.p((wl[0] + wl[3]) / 2, wl[4] + 200)
        sh.text(q[0], q[1], "SHOWER ZONE", 1.25, "middle")
    # legend beside the day plan
    lx, ly = 168, 262
    sh.text(lx, ly, "LEGEND", 1.8, bold=True)
    items = [("medium", "AN ITEM CUT OR BELOW THE PLAN"), ("hidden", "AN ITEM ABOVE IT"), ("phantom", "SPACE KEPT CLEAR, K1 TO K6"),
             ("thin", "DOOR SWING")]
    for i, (st_, t) in enumerate(items):
        y = ly - 4 - i * 3.4
        sh.line(lx, y + 0.6, lx + 7, y + 0.6, st_)
        sh.text(lx + 8.5, y, t, 1.3)
    sh.fillrect(lx, ly - 18.6, lx + 7, ly - 16.4, "shade")
    sh.text(lx + 8.5, ly - 18.2, "WALL OR PARTITION, CUT", 1.3)
    textblock(sh, lx, ly - 23, ["W WINDOW, D DOOR, S SERVICE DOOR,", "V VENT OR COWL, R RINSE BOX", "(SCHEDULE CT-013)"], size=1.3, gap=0.8)
    _bed_section(sh, day, night, k, 168.0, 120.0)

    # ---- right column
    yb = title(sh, dwg, reg, "FIT-OUT MASSES ON CT-002 (TB-11).", "SEE CT-013 FOR THE OPENINGS")
    rows = []
    for b in (b for b in day.blocks if b.keep_clear):
        x0, y0, z0, x1, y1, z1 = b.box
        rows.append([b.iid.split("-")[1], b.name[:60], f"{x1 - x0:.0f} x {y1 - y0:.0f}", f"{z1 - z0:.0f}"])
    y = S.table(sh, 230, yb - 6, [("", 8), ("SPACE KEPT CLEAR (FIT-01, FIT-06)", 112), ("PLAN mm", 36), ("HIGH", 24)], rows, size=1.38,
                row_h=3.1, title="SPACES KEPT CLEAR. NOTHING STANDS IN THEM, BED UP OR DOWN")
    bd, bn = day.find("LB-03").box, night.find("LB-03").box
    md, mn = day.find("LB-01").box[5], night.find("LB-01").box[5]
    fz = V["floor_z"]
    desk = day.find("LA-09").box[5]
    chk = C["chk"]
    rows = [["Day and travel", f"{bd[2] - fz:.0f}", f"{md - fz:.0f}", f"{V['ceiling_z'] - md:.0f} to the ceiling", "Locked at the rail tops (LB-05)"],
            ["Night", f"{bn[2] - fz:.0f}", f"{mn - fz:.0f}", f"{V['ceiling_z'] - mn:.0f} above the mattress", f"{bn[2] - desk:.0f} over the desk top"]]
    y = S.table(sh, 230, y - 7, [("BED", 24), ("UNDERSIDE", 20), ("MATTRESS TOP", 24), ("CLEAR", 46), ("NOTE", 66)], rows, size=1.38,
                row_h=3.1, title=f"BED POSITIONS ABOVE THE FLOOR, mm ({chk['BED-01']['status']}, BED-01, H1)")
    d1, d2 = day.find("BD-07").box, day.find("BD-15").box
    rows = [["D1 entry", f"{d1[3] - d1[0]:.0f}", "Kerb wall, hinged on its front edge, opens outward", "Fold-out step BD-16"],
            ["D2 rear", f"{d2[4] - d2[1]:.0f}", "Rear wall, hinged on its kerb edge, opens outward", "Step BD-16, stows in K6"],
            ["Inner", "620", "Partition, opens into the wet room's walk band (hinge side to confirm)", "About 560 clear"],
            ["S1", "450", "Cassette service door, kerb wall, from outside", "Gasket, two latches"]]
    y = S.table(sh, 230, y - 7, [("DOOR", 20), ("LEAF", 12), ("WHERE AND HOW IT OPENS", 104), ("NOTE", 44)], rows, size=1.38, row_h=3.1,
                title="DOORS AND STEPS")
    S.notes(sh, 230, y - 6, [
        "DATUM DIM-01. FRONT TO THE LEFT, ROAD SIDE UP. BOTH PLANS AT 1000 mm ABOVE THE FLOOR (Z "
        f"{fz + 1000:.0f}), THE FLOOR AT Z {fz:.0f}.",
        "H1: BY DAY THE BED'S FOOTPRINT HOLDS ONLY THE DESK AND THE CHAIR SPACE (K2). THE TWO CHAIRS STOW IN A BENCH DRAWER FOR TRAVEL.",
        "H4: THE REAR DOOR OPENS STRAIGHT INTO THE WALK BAND (K5), WITH THE STEP ZONE (K6) AND THE SAND GRATE JUST INSIDE IT.",
        "THE BATTERY PLINTH STANDS 125 mm OFF THE KERB WALL WITH THE WASHER AND DRYER ON IT. ITS FRONT PANEL FACES THE AISLE.",
        "ITEMS ON THE PARTITION: THE BOARD AT THE KERB END, THE INVERTER AND THE SPLIT'S INDOOR UNIT AT THE ROAD END.",
    ], size=1.4, width_chars=150)
    S.notes(sh, 22, 86, [
        f"THE AISLE (K4) IS {lay_w(day, 'LA-K4'):.0f} mm WIDE AT FULL HEIGHT BETWEEN THE BENCH AND THE PLINTH, 1,030 mm AT FLOOR LEVEL. THE WET ROOM'S "
        f"WALK BAND (K5) IS {lay_w(day, 'LA-K5'):.0f} mm. EVERY WALKWAY IS AT LEAST 550 mm.",
        "DOOR SWINGS ARE DRAWN OPEN AT 90 DEGREES. D1'S OPEN LEAF LIES UNDER THE AWNING TOWARD W1. D2'S LIES ON THE KERB HALF, AWAY "
        "FROM THE SPLIT'S OUTDOOR UNIT ON THE ROAD HALF.",
        "AT NIGHT THE BED COVERS THE DESK AND THE CHAIR SPACE. THE LIFT RAILS ON BOTH SIDE WALLS ARE THE SMALL SOLID STRIPS.",
    ], size=1.5, width_chars=185)
    write(sh, dwg)
    return time.time() - t0


def lay_w(lay, iid):
    b = lay.find(iid).box
    return b[4] - b[1]

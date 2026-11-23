"""The home trailer's whole-trailer sheets (TRAILER.md revision J, the H11 set), A3, third angle:

CT-002: mass and centre of gravity: every load case with and without growth, the axle window of decision H17, the
        centre of gravity in elevation and across the trailer, the tare by group and by maturity, and the least
        certain lines.
CT-003: compliance: the trailer's VSB1 items and the standards on one page with the design's figure for each, the
        operating limits (H13's water in travel and its fallback without the GCM revision, the towball range of H17),
        the vehicle plate and what is not designed yet.

The floor plan CT-010 is drawn from the 3D model's plan cut in cad/drawings/layout_sheets.py (decision H28).
"""
from __future__ import annotations

import time

from build123d import Keep, Plane  # noqa: F401  (kept for the views that cut the model)

from ..lamps import resolve as resolve_lamps
from ..trailer import _kg
from ..trailer_model import TrailerModel
from . import sheet as S
from .home_common import (MARK, cog_symbol, ctx, label_in, stamp, textblock, title, tw,
                          write)
from .sheets import _leaves


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
        "GROWTH IN THE HEAVIEST. THE HARD LIMITS SIT OUTSIDE IT: 7.5 % (MAS-04, H2), THE UTE'S TOW BALL LIMIT AND ITS REAR AXLE (MAS-03).",
        f"SSF IS HALF THE {track:.0f} mm TRACK LESS THE CoG'S OFFSET, OVER THE CoG HEIGHT, WITH GROWTH. THE LOWEST IS "
        f"{min(_ssf(c['growth'], track) for c in rep['cases']):.3f}. WITH THE BODY ROLLED ONTO ITS BUMP STOPS AND TYRES THE STATIC ROLLOVER "
        f"THRESHOLD IS {next(c for c in rep['checks'] if c['id'] == 'STB-01')['measured']:.2f} g (EST.), AGAINST PBS LEVEL 1'S 0.35 g (STB-01) "
        "AND A 0.40 g TARGET (STB-02).",
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
    S.hdim(sh, Rr(ch["width_kerb_y"], 0)[0], yt - 4, Rr(ch["width_road_y"], 0)[0], yt - 4, yt + 2, f"{ch['overall_width']:.0f} OVERALL", size=1.4)
    S.hdim(sh, Rr(-V["half_bw"], 0)[0], Rr(0, 0)[1], Rr(V["half_bw"], 0)[0], Rr(0, 0)[1], Rr(0, 0)[1] - 6, f"{V['body_width']:.0f} BODY", size=1.4)
    sh.text(Rr(0, 0)[0], yt + 6.5, "REAR VIEW", 2.2, "middle", bold=True)
    # the lamps, reflectors and the plate (CT-011): on the rear view with three heights, the side markers on the elevation
    LM = resolve_lamps(lay)
    pl = LM["plate"]

    def box(pa, pb, sty):
        sh.rect(min(pa[0], pb[0]), min(pa[1], pb[1]), max(pa[0], pb[0]), max(pa[1], pb[1]), sty)
    for i in LM["devices"]:
        if i["face"] == "rear":
            box(Rr(i["y0"], i["z0"]), Rr(i["y1"], i["z1"]), "thin")
        elif i["face"] == "side" and i["side"] == "kerb":
            box(E(i["x0"], i["z0"]), E(i["x1"], i["z1"]), "thin")
    box(Rr(pl["y0"], pl["z0"]), Rr(pl["y1"], pl["z1"]), "medium")
    xs = (Rr(-V["half_bw"], 0)[0], Rr(V["half_bw"], 0)[0])
    kerb = lambda f: next(i for i in LM["devices"] if f in i["does"] and i["side"] == "kerb")  # noqa: E731
    eo, rf = kerb("rear_end_outline"), kerb("rear_reflector")
    for n, (yv, zv, txt) in enumerate(((pl["y"], pl["z1"], f"{pl['z1']:,.0f} PLATE TOP"), (rf["y"], rf["z1"], f"{rf['z1']:,.0f}"),
                                       (eo["y"], eo["z1"], f"{eo['z1']:,.0f}"))):
        x = Rr(yv, zv)[0]
        xd = min(xs) - 3 - 3.5 * n if x < Rr(0, 0)[0] else max(xs) + 3 + 3.5 * n
        S.vdim(sh, x, Rr(0, 0)[1], x, Rr(yv, zv)[1], xd, txt, size=1.2)

    # ---- the compliance table, item by item (report 02 section 2, VSB1 Rev 6)
    def st(cid):
        c = chk.get(cid)
        if not c:
            return ("", "#000")
        return (f"{c['status']} ({cid})", "#000" if c["ok"] else ("#c00" if c["severity"] == "fail" else "#b06000"))

    def mv(cid, fmt=None):
        # whole numbers round half up, as the site rounds them (F2-08)
        c = chk[cid]
        v = _kg(c["measured"]) if fmt is None else fmt.format(c["measured"])
        return v + (f" {c['unit']}" if c.get("unit") else "")

    gcm = chk["GCM-01"]["gcm"]
    n_ok = sum(c["ok"] for c in LM["checks"])
    lc = {c["id"]: c for c in LM["checks"]}
    lst = lambda cid: (f"{'PASS' if lc[cid]['ok'] else 'FAIL'} ({cid})", "#000" if lc[cid]["ok"] else "#c00")  # noqa: E731
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
        ["Towball load", "Every case at least 7.5 % (H2), design at least 8.0 % and 320 kg (H17)", f"{chk['MAS-12']['measured']:.1f} % lowest, {_kg(chk['MAS-13']['measured'])} kg heaviest with growth", st("MAS-12")],
        ["Running clearance", "At least 100 mm, unladen (VSB1 5.4). Design at least 290 mm (DIM-06)",
         f"{mv('DIM-04', '{:.1f}')} at {chk['DIM-04']['line']}, breakover {mv('DIM-07', '{:.1f}')} (DIM-07)", st("DIM-06")],
        ["Width", "Across the body and everything on its sides, at most 2,500 mm, side lamps left out (ADR 43/04 6.2.6.1, VSB1 5.2)", f"{mv('DIM-01')}, design at most 2,490 mm (DIM-05)", st("DIM-05")],
        ["Overhang", "Front load space at least the rear overhang (VSB1 5.1.1)", f"{V['axle_x'] - V['body_x0']:.0f} against {ch['overall_x1'] - V['axle_x']:.0f} mm", st("DIM-02")],
        ["Combination", f"Ute and trailer within Ford's {tv['limits']['gcm_kg']:,.0f} kg GCM (BEMM p. 33)", f"{_kg(gcm['sum'])} kg, the ute with growth plus the plate (H20)", st("GCM-01")],
        ["Ute rear axle", f"Towball keeps the Super Duty's {tv['limits']['rear_axle_kg']:,.0f} kg rear axle with growth (H14)", f"{mv('MAS-03')} at the heaviest ball", st("MAS-03")],
        ["Jack-knife", "Front parts 100 mm outside the bike box's sweep, 50 mm under it (JK-01, JK-02)", f"{chk['JK-01']['measured']:.0f} mm and {chk['JK-02']['measured']:.0f} mm", st("JK-01")],
        ["Plug", "7 or 12 pin to AS 4177.5 (VSB1 7.2)", "12-pin flat plug, and a grey Anderson SB50 for the 48 V charging feed", ("AS 4177.5", "#000")],
        ["Wiring", "Supported every 600 mm, insulated joints, grommets through metal, earth wire (VSB1 7.1)", "Two-wire DC, no chassis return (report 20). Glands on CT-602", ("CT-601, CT-602", "#000")],
        ["230 V", "AS/NZS 3001.2:2022: RCD on the inverter's output, labelled (VSB1 7.3)", "30 mA RCBO on every circuit, board labelled, licensed electrician", ("CT-601", "#000")],
        ["Battery", "Sealed compartment vented outside, BMS, fuse within 1 m sleeved (AS/NZS 3001.2 5.4)", "Sealed 2 mm 5052 box, two 20 mm vents through the floor (G6, G7)", ("CT-602", "#000")],
        ["Doors", "Outward opening, one on the left (kerb) side or the rear (VSB1 13.2.1)", "D1 kerb side and D2 rear, both outward, triple locks", ("CT-010, CT-013", "#000")],
        ["Extinguisher", "1A:5B, one a compartment, smoke alarm (VSB1 13.2.2)", "2 kg ABE at D1 and D2, fire blanket at D1, smoke and CO alarms (LA-12, LA-15, LA-16)", ("ONE AT EACH DOOR", "#000")],
        ["LPG", "Caravan LPG code and AS/NZS 5601 (VSB1 13.2.4)", "None fitted. Cooking, hot water and heat are electric or diesel", ("NONE", "#000")],
        ["Mud flaps", "Behind the rear wheels", "610 x 455 mm rubber on the XT rear shock outriggers (BD-10)", ("BD-10", "#000")],
        ["Number plate", "Upright, no part above 1,300 mm, lit white, legible from 20 m (VSB1 3.1)",
         f"{pl['w']} x {pl['h']} mm on the rear wall's kerb half, top at {pl['z1']:,.0f} mm, its lamp over it", lst("LMP-14")],
        ["Lamps, reflectors", "ADR 13/00 positions, heights and spacings (UNECE R48/03 Appendix A)",
         f"{LM['n_lamps']} lamps and {LM['n_reflectors']} reflecting devices on CT-011, {n_ok} of {len(LM['checks'])} checks pass",
         (f"PASS (LMP-01 TO {len(LM['checks']):02d})" if LM["ok"] else "FAIL", "#000" if LM["ok"] else "#c00")],
    ]
    y = S.table(sh, 22, 186, [("ITEM", 25), ("THE RULE AND ITS SOURCE", 84), ("THE DESIGN", 72), ("RESULT", 25)], rows, size=1.32,
                row_h=2.95, title="VSB1 AND THE STANDARDS, ITEM BY ITEM (report 02 section 2, VSB1 REV 6)")
    S.notes(sh, 22, y - 5, [
        f"WIDTH, HEIGHT AND LENGTHS ARE MEASURED ON THE 3D MODEL AT DESIGN RIDE HEIGHT. THE BODY IS {V['body_width']:,.0f} mm. THE ENTRY DOOR'S HANDLE, THE WINDOW FRAMES AND THE HOODS TAKE IT TO {ch['overall_width']:,.0f} mm. THE AWNING SITS ON THE ROOF INSIDE THE BODY WIDTH.",
        "LAMPS, REFLECTORS AND THE NUMBER PLATE ARE SCHEDULED ON CT-011 AND DRAWN ON EACH WALL THERE. THE REAR VIEW SHOWS THEM WITH THEIR "
        "HEIGHTS, AND THE TABLE AT RIGHT GIVES EVERY CHECK (cad/lamps.py, data/services.yaml).",
        "THE WET ROOM HAS ITS OWN OUTSIDE DOOR, SO A 2 kg ABE EXTINGUISHER STANDS BY EACH OUTSIDE DOOR. THE WET ROOM IS COVERED WHETHER OR NOT IT COUNTS AS A SECOND COMPARTMENT FOR VSB1 13.2.2.",
    ], width_chars=185, size=1.45)

    # ---- right column: operating limits, the plate, notes
    yb = title(sh, dwg, reg, f"ATM PLATE {rep['caps']['plated']:,.0f} kg. TARE ON THE PLATE FROM THE WEIGHBRIDGE (TW-03) (TB-11).",
               "AS NOTED, SEE THE SHEETS NAMED")
    lim = tv["limits"]
    aw = C["res"]["awning"]
    ot = chk["STB-04"]["overturn"]
    td_case = chk["STB-05"]["tie_down"]["cases"][0]
    an = td_case["anchors"][0]
    ang, sa, pg = td_case["angles"], an["set_above_mm"], an["plate_gap_mm"]
    lines = [
        ("WATER IN TRAVEL (H13)", f"AT MOST {V['water_travel_l']:.0f} L OF FRESH AND GREY WATER WHILE TOWING. FILL THE TANKS AT CAMP (420 L NET)."),
        ("GCM (GCM-01)", f"FORD'S {lim['gcm_kg']:,.0f} kg. THE UTE WITH GROWTH, {_kg(gcm['ute_kg_growth'])} kg, PLUS THE "
                         f"{gcm['plate']:,.0f} kg PLATE IS {_kg(gcm['sum'])} kg (UTE-06, H20)."),
        ("ATM AND DESIGN LIMIT", f"PLATE {rep['caps']['plated']:,.0f} kg. EVERY CASE WITH GROWTH AT MOST 3,400 kg (MAS-10)."),
        ("TOWBALL (H17)", f"AT LEAST {rep['solved']['window']['pct_min']:.1f} % OF THE TRAILER IN EVERY CASE AND AT MOST "
                          f"{rep['solved']['window']['ball_max']['kg']:.0f} kg WITH GROWTH. THE UTE {lim['towball_rating_kg']:.0f} kg (EST.)."),
        ("THE UTE (H14)", f"FORD RANGER SUPER DUTY ON FORD'S RATINGS: {lim['gvm_kg']:,.0f} kg GVM, REAR AXLE {lim['rear_axle_kg']:,.0f} kg "
                          f"({_kg(uc['UTE-03']['measured'])} kg TOWING WITH GROWTH)."),
        ("COUPLING HEIGHT", f"{V['coupling_z']:.0f} mm LADEN, PLUS OR MINUS 20 mm. SET THE TONGUE'S DROP AT THE FINAL WEIGHING (TW08)."),
        ("GREY WATER", f"EMPTY FOR TRAVEL. A FULL {V['grey_full_l']:.0f} L TANK IS CHECKED IN CASES TC7 AND TC8."),
        ("AWNING (BDY-11, BDY-23)", f"CLOSE THE AWNING IN WIND, LEGS PEGGED: PEG THE LEGS WHENEVER IT IS OUT, AND CLOSE IT BEFORE GUSTS REACH "
                                    f"{aw['close_kmh']:.0f} km/h AND WHENEVER THE TRAILER IS LEFT. SET THE LEGS FOR A {aw['pitch_deg']:.0f} DEGREE FALL."),
        ("PARKED IN WIND (H23, STB-04, STB-05)", f"AT A FORECAST GUST OF {ot['act_kmh']:.0f} km/h OR MORE (A BUREAU WARNING OF DAMAGING WINDS, "
                                         f"{ot['warning_kmh']:.0f} km/h, ALWAYS IS ONE), CLOSE THE AWNING, AND HITCH THE TRAILER TO THE UTE, STRAP IT DOWN "
                                         "AT ITS FOUR LASHING POINTS OR MOVE IT. NO STAYS IN CYCLONIC REGIONS C AND D FROM NOVEMBER TO APRIL. THE TIE-DOWN "
                                         "KIT RIDES IN THE UTE WHILE TOWING AND STAYS WITH THE TRAILER WHENEVER THE UTE IS UNHITCHED FOR MORE THAN A DAY: "
                                         f"FOUR STRAPS, FOUR {an['name'].split(',')[0].upper()} ANCHORS, FOUR {an['plate_no']} STABILIZER PLATES AND A SOIL "
                                         "TEST PROBE."),
        ("SETTING EACH ANCHOR (STB-05)", [
            f"1. MARK THE ANCHOR'S PLACE {td_case['head_mm'][0]:,.0f} TO {td_case['head_mm'][1]:,.0f} mm OUT FROM THE POINT UNDER ITS "
            f"LASHING POINT AND PROBE THERE TO THE HELIX DEPTH, {an['helix_mm'] / 1000:.1f} m. LESS THAN {an['min_probe_inlb']} in-lb: "
            "HITCH THE TRAILER OR MOVE IT.",
            f"2. WIND THE ANCHOR INTO UNDISTURBED SOIL AT A {an['back_angle_deg']:g} DEGREE BACK ANGLE, HEAD TOWARD THE TRAILER, TO ABOUT "
            f"2/3 DEPTH, {sa[0]} TO {sa[1]} mm ({an['set_above_in'][0]} TO {an['set_above_in'][1]} in) LEFT ABOVE GROUND.",
            f"3. DRIVE THE PLATE VERTICALLY ON THE TRAILER SIDE OF THE ROD, {pg[0]} TO {pg[1]} mm ({an['plate_gap_in'][0]} TO "
            f"{an['plate_gap_in'][1]} in) FROM IT.",
            "4. WIND THE ANCHOR TO FULL DEPTH, ITS HEAD AT THE GROUND.",
            f"5. TENSION THE STRAP UNTIL THE ROD BEARS ON THE PLATE. CHECK ITS ANGLE ALONG IT WITH AN ANGLE FINDER: {min(ang):g} TO "
            f"{max(ang):g} DEGREES, {min(ang) - an['min_angle_deg']:g} DEGREES CLEAR OF THE LISTING'S {an['min_angle_deg']:g}.",
            "NEVER DIG A HOLE AND BACKFILL IT: TIE DOWN WARNS THAT LOOSE SOIL MAY THEN NEED A LOAD TEST. "
            f"STEPS FROM TIE DOWN'S MANUAL, {an['steps_src'].upper()}."]),
    ]
    yy = yb - 13
    top = yb - 4
    sh.text(232, yb - 8.5, "OPERATING LIMITS (FOR THE PLATE, THE OWNER'S MANUAL AND THE INSPECTOR)", 2.2, bold=True)
    for head, body in lines:
        sh.text(232, yy, head, 1.4, bold=True)
        wl = [t for p in ([body] if isinstance(body, str) else body) for t in S.wrap_mm(p, 410 - 2 - 270, 1.4)]
        for i, t in enumerate(wl):
            sh.text(270, yy - i * 2.2, t, 1.4)
        yy -= 2.2 * max(1, len(wl)) + 1.2
    sh.rect(230, yy + 0.4, 410, top, "thick")
    yp = yy - 6
    sh.text(232, yp, "VEHICLE PLATE (VSB1 13.1.1)", 2.2, bold=True)
    yq = textblock(sh, 232, yp - 4, S.wrap_mm(
        "MAKE (CONCESSIONAL TRAILER), VIN, ATM, GTM AND TARE, EMBOSSED, ETCHED OR ENGRAVED IN BLOCK LETTERS AT LEAST 2.5 mm HIGH, "
        "MATCHING THE RAV ENTRY. NSW ALSO LOOKS FOR THE MODEL AND THE DATE OF MANUFACTURE (VIB 78). THE GTM TO PLATE IS SET WITH THE "
        f"ENGINEER, AT MOST THE NSW CAP OF {rep['caps']['gtm']:,.0f} kg. THE PLATE AND VIN POSITIONS ARE NOT DESIGNED YET. PHOTOGRAPH "
        "THE VIN STAMPING BEFORE AND AFTER GALVANISING (REG-02).", 410 - 2 - 232, 1.4), size=1.4, gap=0.85)
    yn, _ = S.notes(sh, 232, yq - 4, [
        "EVERY FIGURE ON THIS SHEET COMES FROM THE MODEL'S CHECKS (data/checks.yaml, data/ute/ute.yaml) AT THE SOLVED AXLE.",
        "A RESULT IN AMBER IS A QUESTION FOR THE INSPECTOR. NO CHECK FAILS.",
    ], size=1.4, width_chars=150)
    _lamp_checks(sh, LM, yn - 5)
    write(sh, dwg)
    return time.time() - t0


def _lamp_checks(sh, LM, y):
    """CT-003's table of the lamp, reflector and plate checks from cad/lamps.py, in the right column."""
    rows = [[c["id"], c["what"], c["clause"], c["measured"], c["limit"],
             ("PASS" if c["ok"] else "FAIL", "#000" if c["ok"] else "#c00")] for c in LM["checks"]]
    S.table(sh, 230, y, [("ID", 13), ("CHECK", 45), ("CLAUSE", 14), ("THE DESIGN, mm", 58), ("THE LIMIT, mm", 36), ("RESULT", 14)],
            rows, size=1.2, row_h=2.7, title="LAMPS, REFLECTORS AND THE NUMBER PLATE (ADR 13/00 APPENDIX A, VSB1 3.1)")

"""The bikes' envelope models, for the drawings only (cad/drawings/ute_sheets.py).

These are the envelope builders the 3D model used until decision H27 (commit 31ed437), kept so that CT-701 and CT-704
draw each bike as the sheets always have: hidden-line removal of the product models (cad/model/vehicles/tuareg.py and
street_triple.py) inside the box takes minutes a view. They read the same points and estimates, so each envelope
holds its product model's outline. Shapes are in cad/model/bike.py's local frame.
"""
from __future__ import annotations

import math
import re

from ..bike import BikeModel
from ..prims import box_span, cyl, disc_x_axis, prism_xy, prism_yz, tyre_x_axis


def _v(d):
    """05 values are {v: ...}; return the number."""
    return d["v"] if isinstance(d, dict) else d


def _mid(v):
    return (v[0] + v[1]) / 2 if isinstance(v, (list, tuple)) else v


def _y05(y):
    """05 lateral value (y to the bike's left) in the model's bike frame (y to the bike's right)."""
    return -y


def P(x, y, z):
    """Bike frame (x rear, y right, z up) to the local module-aligned frame."""
    return (y, x, z)


def _tyres(g, est, solids):
    t = g["tyres"]
    pts = g["points"]
    Df, Wf = _v(t["front"]["diameter"]), _v(t["front"]["width"])
    Dr, Wr = _v(t["rear"]["diameter"]), _v(t["rear"]["width"])
    # rim diameters in inches from the size codes (21, 18, 17)

    rf_in = float(re.findall(r"(?:-|ZR|R)\s?(\d\d)", t["front"]["size"])[0])
    rr_in = float(re.findall(r"(?:-|ZR|R)\s?(\d\d)", t["rear"]["size"])[0])
    rim_rf, rim_rr = rf_in * 25.4 / 2, rr_in * 25.4 / 2
    xf = pts["front_axle"]["x"]
    xr = pts["rear_axle"]["x"]
    zf, zr = Df / 2, Dr / 2  # axle height = tyre radius, so both tyres sit on the ground
    solids["front tyre"] = tyre_x_axis(xf, zf, Df, Wf, rim_rf)
    solids["rear tyre"] = tyre_x_axis(xr, zr, Dr, Wr, rim_rr)
    rw = est.get("rim_width", {"front": 40, "rear": 60})
    solids["front wheel"] = disc_x_axis(xf, zf, rim_rf, rw["front"])
    solids["rear wheel"] = disc_x_axis(xr, zr, rim_rr, rw["rear"])
    return (xf, zf, Df / 2, Wf), (xr, zr, Dr / 2, Wr, rim_rr)


def _fork(solids, axle, rake_deg, top_z, half, dia):
    xf, zf = axle
    t = math.tan(math.radians(rake_deg))
    top = (xf + (top_z - zf) * t, top_z)
    for s in (1, -1):
        solids[f"fork leg {'right' if s > 0 else 'left'}"] = cyl(P(xf, s * half, zf), P(top[0], s * half, top[1]), dia / 2)
    return top


def tuareg(g, prm) -> BikeModel:  # noqa: C901
    est = prm["estimates"]
    pts = g["points"]
    solids: dict[str, object] = {}
    (xf, zf, rf, wf), (xr, zr, rr, wr, rim_rr) = _tyres(g, est, solids)
    length = prm.get("length", prm["owner"]["length"])
    x_end = length - prm["front_overhang"]          # rear-most point (plate face)
    screen_z = prm.get("screen_top_z", prm["screen_top"]["z"])
    screen_x = prm["screen_top"]["x"]

    # Forks along the rake (05: rake 26.7 deg; legs and top height estimated)
    fk = est["fork"]
    _fork(solids, (xf, zf), g["published"]["rake"]["v"], fk["top_z"], fk["half_spacing"], fk.get("diameter", fk.get("outer", 48)))

    # High front mudguard (05: tip at x -156, z 775)
    mg = pts["front_mudguard_tip"]
    hw = est["mudguard_half_width"]["v"]
    solids["front mudguard"] = prism_yz([(mg["x"] - 4, mg["z"] - 15), (mg["x"], mg["z"] + 15), (40, 805), (200, 795),
                                         (200, 772), (40, 782)], -hw, hw)

    # Fairing and radiator shrouds: half-width 300 between z 900 and 1,100 (estimate), tapered at the front
    fw = est["fairing_half_width"]["v"]
    ff = est["fairing_front_half_width"]["v"]
    hl = pts["headlight_fairing_front"]
    tank = pts["tank_top"]
    side = prism_yz([(hl["x"], 900), (hl["x"], hl["z"][1]), (260, 1060), (tank["x"], tank["z"]), (700, tank["z"] - 3), (700, 900)], -fw, fw)
    plan = prism_xy([(-ff, hl["x"]), (ff, hl["x"]), (fw, 300), (fw, 700), (-fw, 700), (-fw, 300)], 899, 1101)
    solids["fairing and shrouds"] = side & plan

    # Screen: from the fairing top to the screen top (owner height governs the top)
    sw = est["screen_half_width"]["v"]
    solids["screen"] = prism_yz([(hl["x"] + 10, hl["z"][1] - 5), (screen_x, screen_z), (screen_x + 6, screen_z - 2),
                                 (hl["x"] + 18, hl["z"][1] - 8)], -sw, sw)

    # Tank, seat and tail following the side profile (05 points), widths estimated
    seat = pts["seat_low_point"]
    rack = pts["tail_rack_top"]
    tl = pts["tail_light_tip"]
    upper = [(600, 900), (tank["x"], tank["z"]), (900, 1010), (seat["x"][0], seat["z"][1]), (seat["x"][1], seat["z"][0]),
             (rack["x"][0], rack["z"][0]), (rack["x"][1], rack["z"][1]), (tl["x"], tl["z"]), (1810, 845), (1450, 800),
             (1150, 700), (900, 800), (700, 880)]
    tw, sw2, rw2 = est["tank_half_width"]["v"], est["seat_half_width"]["v"], est["tail_half_width"]["v"]
    prof = prism_yz(upper, -tw, tw)
    widths = prism_xy([(-tw, 590), (tw, 590), (tw, 950), (sw2, 1000), (sw2, 1450), (rw2, 1500), (rw2, 1870),
                       (-rw2, 1870), (-rw2, 1500), (-sw2, 1450), (-sw2, 1000), (-tw, 950)], 600, 1200)
    solids["tank, seat and tail"] = prof & widths

    # Engine, frame and skid plate (05 skid plate z 244 over x 600 to 800), width estimated
    sk = pts["lowest_point_skid_plate"]
    ew = est["engine_half_width"]["v"]
    pp = pts["pillion_peg_hanger"]
    lower = [(380, 905), (430, 470), (sk["x"][0], sk["z"]), (sk["x"][1], sk["z"]), (980, 380), (pp["x"], pp["z"] - 20),
             (pp["x"], 700), (900, 805), (700, 905)]
    solids["engine and frame"] = prism_yz(lower, -ew, ew)

    # Swingarm (pivot estimated) to the rear axle, arms either side of the tyre
    sp = est["swingarm_pivot"]
    for s in (1, -1):
        y = s * (wr / 2 + 25)
        solids[f"swingarm {'right' if s > 0 else 'left'}"] = cyl(P(sp["x"], y, sp["z"]), P(xr, y, zr), 22)

    # Bars, bar ends and handguards
    bc = est["bar_clamp"]
    be = pts["bar_ends_handguards"]
    by = est["bar_end_y"]["v"]
    for s, nm in ((1, "right"), (-1, "left")):
        solids[f"handlebar {nm}"] = cyl(P(bc["x"], s * 40, bc["z"]), P(be["x"], s * (by - 15), be["z"]), 14)
        solids[f"bar end {nm}"] = cyl(P(be["x"], s * (by - 15), be["z"]), P(be["x"], s * by, be["z"]), 16)
        hg = est["handguard"]
        y0, y1 = sorted((s * hg["y"][0], s * hg["y"][1]))
        tip = pts["handguard_front_tip"]
        solids[f"handguard {nm}"] = prism_yz([(tip["x"], tip["z"] - 10), (tip["x"] + 5, hg["z"][1]), (hg["x"][1], be["z"] + 15),
                                              (hg["x"][1], hg["z"][0]), (tip["x"] + 40, hg["z"][0])], y0, y1)
        mf = est["mirror_folded"]
        m0, m1 = sorted((s * mf["y"][0], s * mf["y"][1]))
        solids[f"mirror {nm} (folded)"] = box_span(m0, m1, mf["x"][0], mf["x"][1], mf["z"][0], mf["z"][1])
        # Footpegs (05 x 955, z 360; tip y estimated at 320)
        fp = pts["rider_footpegs"]
        solids[f"footpeg {nm}"] = cyl(P(fp["x"], s * est["peg_root_y"]["v"], fp["z"]), P(fp["x"], s * est["peg_tip_y"]["v"], fp["z"]), 14)

    # Right-side silencer (05 x 1,380 to 1,780, z 510 to 800; y and diameter estimated)
    sl = est["silencer"]
    solids["silencer (right)"] = cyl(P(*sl["start"]), P(*sl["end"]), sl["diameter"] / 2)

    # Number plate hanger and plate. The plate face is the rear-most point (owner length governs).
    pl = est["plate"]
    solids["plate hanger"] = prism_yz([(1790, 850), (1812, 858), (x_end - 6, pl["z"][1]), (x_end - 6, pl["z"][1] - 14),
                                       (1800, 836)], -40, 40)
    solids["number plate"] = box_span(-pl["half_width"], pl["half_width"], x_end - 6, x_end, pl["z"][0], pl["z"][1])

    # Folded side stand on the left (05 says TODO, so pivot and foot are estimates)
    ss = est["side_stand"]
    solids["side stand (folded)"] = cyl(P(*ss["pivot"]), P(*ss["foot"]), 13)
    fx, fy, fz = ss["foot"]
    solids["side stand foot"] = box_span(fy - 40, fy + 10, fx - 35, fx + 35, fz - 8, fz + 8)

    # Crash bars as a box envelope (estimate, widths and top from measurements.yaml)
    cb = est.get("crash_bars")
    if cb:
        solids["crash bars (envelope)"] = box_span(-cb["half_width"], cb["half_width"], cb["x"][0], cb["x"][1], cb["z"][0], cb["z"][1])

    # Mosko Moto panniers, left on in the garage (outer width owner's measurement, size Mosko Moto's, position estimated)
    pn = est.get("panniers")
    if pn:
        for s, nm in ((1, "right"), (-1, "left")):
            y0, y1 = sorted((s * (pn["outer_y"] - pn["thickness"]), s * pn["outer_y"]))
            solids[f"pannier {nm} (Mosko Moto)"] = box_span(y0, y1, pn["x"][0], pn["x"][1], pn["z"][0], pn["z"][1])

    tyd = prm["tie_down_y"]
    td = g["tie_downs"]
    tie = {
        "handlebar_inboard": (_mid(td["handlebar_inboard"]["x"]), tyd["handlebar_inboard"]["v"], _mid(td["handlebar_inboard"]["z"])),
        "pillion_peg_hangers": (td["pillion_peg_hangers"]["x"], tyd["pillion_peg_hangers"]["v"], td["pillion_peg_hangers"]["z"]),
    }
    com = prm["centre_of_mass"]
    return BikeModel("tuareg_660_rally", solids, tie, (com["x"], 0.0, com["z"]), xr - xf, (xf, zf), (xr, zr), rim_rr, wr)


def street_triple(g, prm) -> BikeModel:
    est = prm["estimates"]
    pts = g["points"]
    solids: dict[str, object] = {}
    (xf, zf, rf, wf), (xr, zr, rr, wr, rim_rr) = _tyres(g, est, solids)
    length = prm.get("length", prm["owner"]["length"])
    x_end = length - prm["front_overhang"]

    fk = est["fork"]
    ty = pts["top_yoke"]
    _fork(solids, (xf, zf), g["published_2023_on"]["rake_rs"]["v"], ty["z"], fk["half_spacing"], fk.get("diameter", fk.get("outer", 48)))

    hw = est["mudguard_half_width"]["v"]
    solids["front mudguard"] = prism_yz([(-200, 555), (-120, 600), (0, 625), (140, 600), (180, 575), (140, 585), (0, 612), (-120, 590)], -hw, hw)

    hl = pts["headlight_front"]
    hh = est["headlight_half_width"]["v"]
    solids["headlight cowl"] = prism_yz([(hl["x"], 740), (hl["x"], 860), (60, 905), (200, 905), (200, 740)], -hh, hh)

    tank = pts["tank_top"]
    seat = pts["seat_low_point"]
    tail = pts["tail_top"]
    tl = pts["tail_light_tip"]
    upper = [(330, 900), (420, 975), (tank["x"], tank["z"]), (850, 940), (seat["x"][0], seat["z"]), (seat["x"][1], seat["z"]),
             (tail["x"][0], tail["z"]), (tail["x"][1], tail["z"]), (tl["x"], tl["z"]), (1520, 900), (1250, 760), (980, 640),
             (819, 560), (500, 680), (330, 780)]
    tw, sw, rw = est["tank_half_width"]["v"], est["seat_half_width"]["v"], est["tail_half_width"]["v"]
    prof = prism_yz(upper, -tw, tw)
    widths = prism_xy([(-tw, 320), (tw, 320), (tw, 860), (sw, 900), (sw, 1290), (rw, 1340), (rw, 1600),
                       (-rw, 1600), (-rw, 1340), (-sw, 1290), (-sw, 900), (-tw, 860)], 500, 1100)
    solids["tank, seat and tail"] = prof & widths

    bp = pts["lowest_point_belly_pan"]
    su = pts["silencer_underside"]
    sp = pts["swingarm_pivot"]
    ew = est["engine_half_width"]["v"]
    lower = [(335, 790), (338, 335), (bp["x"][0], bp["z"]), (bp["x"][1], bp["z"]), (su["x"][0], su["z"]), (su["x"][1], su["z"]),
             (960, 260), (900, 450), (sp["x"], 540), (600, 720), (500, 790)]
    solids["engine, radiator and belly pan"] = prism_yz(lower, -ew, ew)

    for s in (1, -1):
        y = s * (wr / 2 + 25)
        solids[f"swingarm {'right' if s > 0 else 'left'}"] = cyl(P(sp["x"], y, sp["z"]), P(xr, y, zr), 25)

    hc = pts["handlebar_clamp"]
    be = pts["bar_ends"]
    by = max(_y05(y) for y in be["y"])
    cy = est["bar_clamp_y"]["v"]
    for s, nm in ((1, "right"), (-1, "left")):
        solids[f"handlebar {nm}"] = cyl(P(hc["x"], s * cy, hc["z"]), P(be["x"], s * (by - 15), be["z"]), 11)
        solids[f"bar end {nm}"] = cyl(P(be["x"], s * (by - 15), be["z"]), P(be["x"], s * by, be["z"]), 13)
        fp = pts["rider_footpegs"]
        solids[f"footpeg {nm}"] = cyl(P(fp["x"], s * est["peg_root_y"]["v"], fp["z"]), P(fp["x"], s * est["peg_tip_y"]["v"], fp["z"]), 12)

    top = pts["top_without_mirrors"]
    rv = est["reservoir"]
    solids["brake reservoir (right)"] = box_span(rv["y"][0], rv["y"][1], rv["x"][0], rv["x"][1], top["z"] - 40, top["z"])

    pl = est["plate"]
    solids["plate hanger"] = prism_yz([(1450, 880), (1475, 890), (x_end - 6, pl["z"][1]), (x_end - 6, pl["z"][1] - 14), (1460, 865)], -40, 40)
    solids["number plate"] = box_span(-pl["half_width"], pl["half_width"], x_end - 6, x_end, pl["z"][0], pl["z"][1])

    ssp = pts["side_stand_pivot_left"]
    ssf = pts["side_stand_foot_folded"]
    sy = est["side_stand_y"]
    solids["side stand (folded)"] = cyl(P(ssp["x"], sy["pivot"], ssp["z"]), P(ssf["x"], sy["foot"], ssf["z"]), 12)
    solids["side stand foot"] = box_span(sy["foot"] - 35, sy["foot"] + 10, ssf["x"] - 30, ssf["x"] + 30, ssf["z"] - 7, ssf["z"] + 7)

    tyd = prm["tie_down_y"]
    td = g["tie_downs"]
    tie = {
        "handlebar_beside_risers": (_mid(td["handlebar_beside_risers"]["x"]), tyd["handlebar_beside_risers"]["v"],
                                    _mid(td["handlebar_beside_risers"]["z"])),
        "pillion_peg_hangers": (td["pillion_peg_hangers"]["x"], tyd["pillion_peg_hangers"]["v"], td["pillion_peg_hangers"]["z"]),
    }
    com = prm["centre_of_mass"]
    return BikeModel("street_triple_765", solids, tie, (com["x"], 0.0, com["z"]), xr - xf, (xf, zf), (xr, zr), rim_rr, wr)




BUILDERS = {"tuareg_660_rally": tuareg, "street_triple_765": street_triple}

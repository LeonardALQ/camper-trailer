"""The Triumph Street Triple 765 RS (2023-on), the owner's track bike without mirrors, built to Triumph's figures and
report 05's points (research/29). Every part touches the part that carries it (cad/tests/test_ute_supported.py).
"""
from __future__ import annotations

from . import kit
from .moto import Fork, bar, blk, chain, mirrored, rod, side, wheel

# Sizes come from data/parts/bikes.yaml (`estimates`), where each carries its source. research/29 lists them.
COLOURS = {"tyre": "#1b1b1b", "wheel": "#26292b", "metal": "#b8b8b8", "frame": "#3b3f44", "engine": "#2f3236",
           "body": "#1f3a5f", "seat": "#202020", "gold": "#c9a227", "lamp": "#e8f1f5", "shock": "#e1b12c",
           "alloy": "#9ea4a8", "red": "#b03a2e"}


def street_triple(g, prm):
    from ..bike import BikeModel
    est = prm["estimates"]
    pts = g["points"]
    t = g["tyres"]
    S, C = {}, {}

    def add(name, shape, colour):
        S[name], C[name] = shape, COLOURS[colour]

    rims, wh, dsc, fk = est["rims"], est["wheels"], est["discs"], est["fork"]
    RIM_W = {"front": rims["front"] * 25.4, "rear": rims["rear"] * 25.4}
    HUB = {"front": tuple(wh["hub_front"]), "rear": tuple(wh["hub_rear"])}
    DISC = {"front": dsc["front"] / 2, "rear": dsc["rear"] / 2}
    STANCHION_R, OUTER_R = fk["stanchion"] / 2, fk["outer"] / 2

    Df, Wf = t["front"]["diameter"]["v"], t["front"]["width"]["v"]
    Dr, Wr = t["rear"]["diameter"]["v"], t["rear"]["width"]["v"]
    rim = 17 * 25.4 / 2
    xf, zf = pts["front_axle"]["x"], Df / 2
    xr, zr = pts["rear_axle"]["x"], Dr / 2
    length = prm.get("length", prm["owner"]["length"])
    x_end = length - prm["front_overhang"]

    # ---------------------------------------------------------------- wheels
    add("front tyre", wheel(kit.road_tyre(Df, Wf, rim, RIM_W["front"]), xf, zf), "tyre")
    add("rear tyre", wheel(kit.road_tyre(Dr, Wr, rim, RIM_W["rear"]), xr, zr), "tyre")
    hr, hw = HUB["front"]
    hr2, hw2 = HUB["rear"]
    add("front wheel", wheel(kit.cast_wheel(rim, RIM_W["front"] + 8, hr, hw), xf, zf), "wheel")
    add("rear wheel", wheel(kit.cast_wheel(rim, RIM_W["rear"] + 8, hr2, hw2), xr, zr), "wheel")
    add("front brake discs", kit.fuse([wheel(kit.disc(DISC["front"], hr - 2, s * (hw / 2 + 1)), xf, zf) for s in (1, -1)]), "metal")
    add("rear brake disc", wheel(kit.disc(DISC["rear"], hr2 - 2, hw2 / 2 + 1), xr, zr), "metal")
    cy = -(Wr / 2 + 15)                      # chain line, between the tyre and the left swingarm arm (est.)
    add("rear sprocket", wheel(kit.lathe([(hr2 - 2, -hw2 / 2), (hr2 + 25, -hw2 / 2), (hr2 + 25, cy + 3), (124.0, cy + 3), (124.0, cy - 3),
                                          (hr2 - 2, cy - 3)]), xr, zr), "metal")
    add("front axle", rod((xf, -130, zf), (xf, 130, zf), 12.5), "metal")
    add("rear axle", rod((xr, -(Wr / 2 + 62), zr), (xr, Wr / 2 + 62, zr), 13.0), "metal")

    # ---------------------------------------------------------------- fork, yokes, steering head
    hs = fk["half_spacing"]
    f = Fork(xf, zf, g["published_2023_on"]["rake_rs"]["v"], 29.0)   # 29 mm offset from Triumph's rake and trail (research/29)
    ty = pts["top_yoke"]
    lt = pts["lower_triple_clamp"]
    s_top = (ty["z"] - zf) / f.u[1]
    s_low = (lt["z"] - zf) / f.u[1]
    legs = []
    for s in (1, -1):
        y = s * hs
        legs += [f.tube(y, -30, 330, STANCHION_R), f.tube(y, 290, s_top + 25, OUTER_R)]
        legs.append(side([f.leg(-40, -28), f.leg(55, -28), f.leg(55, 28), f.leg(-40, 28)], y - 25, y + 25))
    add("fork legs", kit.fuse(legs), "gold")
    add("lower triple clamp", f.clamp(s_low - 15, s_low + 15, 36, 38, hs + OUTER_R + 6), "alloy")
    add("top yoke", f.clamp(s_top - 22, s_top, 36, 38, hs + OUTER_R + 6), "alloy")
    (a0x, a0z), (a1x, a1z) = f.axis(s_low - 20), f.axis(s_top + 5)
    add("steering head", rod((a0x, 0, a0z), (a1x, 0, a1z), 30), "frame")
    cal = [f.leg(80, 8), f.leg(150, 8), f.leg(150, 68), f.leg(80, 68)]
    add("front brake calipers", kit.fuse([side(cal, s * (hw / 2 - 12), s * (hw / 2 + 22)) for s in (1, -1)]), "red")
    hwm = est["mudguard_half_width"]["v"]
    add("front mudguard", kit.fuse([side([(-200, 555), (-120, 600), (0, 625), (140, 600), (180, 575), (140, 585), (0, 612), (-120, 590)], -hwm, hwm)]
                                   + [blk(85, 135, s * (hwm - 4), s * (hs - 16), 560, 600) for s in (1, -1)]), "body")

    # ---------------------------------------------------------------- twin headlights, fly screen
    hl = pts["headlight_front"]
    hh = est["headlight_half_width"]["v"]
    lamps = [rod((hl["x"], s * (hh - 52), hl["z"]), (hl["x"] + 95, s * (hh - 52), hl["z"]), 50) for s in (1, -1)]
    lamps.append(blk(hl["x"] + 80, f.leg((hl["z"] - zf) / f.u[1])[0] + 5, -(hs + 5), hs + 5, hl["z"] - 12, hl["z"] + 12))
    add("headlights", kit.fuse(lamps), "lamp")
    add("fly screen", side([(hl["x"] + 20, hl["z"] + 45), (40, 925), (140, 938), (150, 915), (hl["x"] + 60, hl["z"] + 40)], -hh + 10, hh - 10), "body")

    # ---------------------------------------------------------------- frame: aluminium twin spar, steel subframe (est.)
    sp = pts["swingarm_pivot"]
    spars = [side([(300, 905), (520, 885), (sp["x"] + 10, 650), (sp["x"] + 35, 560), (sp["x"] + 35, 330), (sp["x"] - 30, 330),
                   (sp["x"] - 40, 560), (500, 795), (300, 830)], s * 125, s * 150) for s in (1, -1)]
    spars.append(blk(290, 400, -150, 150, 830, 905))
    sub = []
    for s in (1, -1):
        sub.append(bar([(sp["x"] + 5, s * 130, 640), (1450, s * 92, 905)], 11))
        sub.append(bar([(sp["x"] + 30, s * 130, 560), (1233, s * 110, 640), (1450, s * 92, 905)], 11))
    sub.append(rod((1450, -92, 905), (1450, 92, 905), 9))
    sub.append(rod((870, -140, 640), (870, 140, 640), 12))
    add("frame", kit.fuse(spars + sub), "frame")

    # ---------------------------------------------------------------- engine, radiator, belly pan, exhaust (est.)
    ew = est["engine_half_width"]["v"]
    add("radiator", blk(335, 378, -(ew - 10), ew - 10, 470, 790), "engine")
    crank = side([(380, 430), (450, 300), (700, 262), (900, 290), (940, 420), (900, 560), (700, 700), (450, 720), (390, 650)], -165, 165)
    head = side([(450, 720), (700, 700), (690, 800), (480, 830)], -150, 150)
    covers = [rod((720, 150, 380), (720, ew - 12, 380), 95), rod((560, -150, 360), (560, -(ew - 10), 360), 85)]
    add("engine", kit.fuse([crank, head, blk(370, 440, -140, 140, 560, 650)] + covers), "engine")
    bp = pts["lowest_point_belly_pan"]
    # the belly pan under the engine and the exhaust collector, as wide as the engine (est.), its lowest line on 05's
    add("belly pan", side([(bp["x"][0] + 10, 290), (bp["x"][0], bp["z"] + 8), (bp["x"][0] + 10, bp["z"]), (bp["x"][1], bp["z"]), (660, 205),
                           (690, 275), (600, 290)], -ew, ew), "body")
    su = pts["silencer_underside"]
    add("exhaust headers", kit.fuse([bar([(440, y, 650), (395, y, 450), (430, 0.5 * y, 225), (640, 0, 215)], 18) for y in (-60, 0, 60)]), "metal")
    add("silencer (under the engine)", side([(640, 200), (su["x"][0], su["z"]), (su["x"][1], su["z"]), (965, 220), (940, 268), (650, 262)],
                                            -110, 150), "metal")

    # ---------------------------------------------------------------- swingarm, shock, chain
    arms = [side([(sp["x"] - 10, sp["z"] + 40), (xr + 25, zr + 26), (xr + 25, zr - 26), (sp["x"] - 10, sp["z"] - 40)],
                 s * (Wr / 2 + 25), s * (Wr / 2 + 55)) for s in (1, -1)]
    arms.append(rod((sp["x"], -168, sp["z"]), (sp["x"], 168, sp["z"]), 12))
    arms.append(rod((1000, -(Wr / 2 + 30), 380), (1000, Wr / 2 + 30, 380), 15))
    add("swingarm", kit.fuse(arms), "alloy")
    add("rear shock", kit.fuse([rod((1000, 0, 388), (870, 0, 640), 20), rod((975, 0, 440), (895, 0, 590), 32)]), "shock")
    add("chain", chain((780, 390), 43.0, (xr, zr), 119.0, cy, 12.0), "metal")

    # ---------------------------------------------------------------- bodywork
    tank = pts["tank_top"]
    tw = est["tank_half_width"]["v"]
    add("tank", side([(330, 905), (420, 975), (tank["x"], tank["z"]), (850, 940), (880, 870), (700, 835), (420, 835)], -tw, tw), "body")
    seat = pts["seat_low_point"]
    sw = est["seat_half_width"]["v"]
    add("rider seat", side([(840, 905), (seat["x"][0], seat["z"]), (seat["x"][1], seat["z"]), (1100, 862), (1110, 845), (900, 805),
                            (840, 850)], -sw, sw), "seat")
    tail = pts["tail_top"]
    tl = pts["tail_light_tip"]
    rw = est["tail_half_width"]["v"]
    add("pillion seat", side([(1105, 870), (1280, 950), (tail["x"][0], tail["z"] - 12), (1300, 920), (1120, 848)], -rw + 15, rw - 15), "seat")
    add("tail", side([(1100, 840), (tail["x"][0], tail["z"] - 15), (tail["x"][1], tail["z"]), (tl["x"], tl["z"]), (1520, 900), (1250, 820),
                      (1100, 820)], -rw, rw), "body")
    add("tail light", blk(tl["x"] - 14, tl["x"] + 1, -35, 35, tl["z"] - 25, tl["z"] - 3), "red")
    pl = est["plate"]
    add("plate hanger", side([(1450, 880), (1475, 890), (x_end - 6, pl["z"][1]), (x_end - 6, pl["z"][1] - 14), (1460, 865)], -40, 40), "seat")
    from ..prims import box_span
    add("number plate", box_span(-pl["half_width"], pl["half_width"], x_end - 6, x_end, pl["z"][0], pl["z"][1]), "lamp")

    # ---------------------------------------------------------------- bars, pegs, stand
    hc = pts["handlebar_clamp"]
    be = pts["bar_ends"]
    by = max(-y for y in be["y"])
    cy = est["bar_clamp_y"]["v"]
    td = g["tie_downs"]
    tx = (td["handlebar_beside_risers"]["x"][0] + td["handlebar_beside_risers"]["x"][1]) / 2
    tz = (td["handlebar_beside_risers"]["z"][0] + td["handlebar_beside_risers"]["z"][1]) / 2
    tyy = prm["tie_down_y"]["handlebar_beside_risers"]["v"]
    add("handlebar", bar([(be["x"], -(by - 15), be["z"]), (tx, -tyy, tz), (hc["x"], -cy, hc["z"]), (hc["x"], cy, hc["z"]), (tx, tyy, tz),
                          (be["x"], by - 15, be["z"])], 11), "frame")
    tcl = f.axis(s_top, -4)
    add("bar risers", kit.fuse([rod((tcl[0], s * cy, tcl[1] - 4), (hc["x"], s * cy, hc["z"]), 13) for s in (1, -1)]), "alloy")
    for s, nm in ((1, "right"), (-1, "left")):
        add(f"bar end {nm}", rod((be["x"], s * (by - 15), be["z"]), (be["x"], s * by, be["z"]), 13), "metal")
    top = pts["top_without_mirrors"]
    rv = est["reservoir"]
    add("brake reservoir (right)", kit.fuse([blk(rv["x"][0], rv["x"][1], rv["y"][0], rv["y"][1], top["z"] - 40, top["z"]),
                                             rod((300, 60, hc["z"] + 4), (300, 60, top["z"] - 38), 8)]), "seat")
    fp = pts["rider_footpegs"]
    pr, pt = est["peg_root_y"]["v"], est["peg_tip_y"]["v"]
    for s, nm in ((1, "right"), (-1, "left")):
        add(f"footpeg {nm}", kit.fuse([rod((fp["x"], s * pr, fp["z"]), (fp["x"], s * pt, fp["z"]), 12),
                                       blk(sp["x"] + 10, fp["x"] + 20, s * 125, s * (pr + 6), fp["z"] - 20, 420)]), "alloy")
    pp = pts["pillion_peg_pivot"]
    pyy = prm["tie_down_y"]["pillion_peg_hangers"]["v"]
    add("pillion peg hangers", mirrored(lambda s: kit.fuse([blk(pp["x"] - 28, pp["x"] + 27, s * (pyy - 25), s * (pyy + 20), pp["z"] - 24, 660),
                                                            rod((pp["x"], s * (pyy + 15), pp["z"]), (pp["x"], s * (pyy + 75), pp["z"]), 10)])), "alloy")
    ssp = pts["side_stand_pivot_left"]
    ssf = pts["side_stand_foot_folded"]
    sy = est["side_stand_y"]
    add("side stand (folded)", rod((ssp["x"], sy["pivot"], ssp["z"]), (ssf["x"], sy["foot"], ssf["z"]), 12), "frame")
    add("side stand foot", blk(ssf["x"] - 30, ssf["x"] + 30, sy["foot"] - 35, sy["foot"] + 10, ssf["z"] - 7, ssf["z"] + 7), "frame")

    tyd = prm["tie_down_y"]
    ties = {
        "handlebar_beside_risers": (tx, tyd["handlebar_beside_risers"]["v"], tz),
        "pillion_peg_hangers": (td["pillion_peg_hangers"]["x"], tyd["pillion_peg_hangers"]["v"], td["pillion_peg_hangers"]["z"]),
    }
    com = prm["centre_of_mass"]
    fine = {"front tyre", "rear tyre", "front wheel", "rear wheel", "chain", "front brake discs", "rear brake disc", "rear sprocket",
            "front brake calipers", "exhaust headers", "bar risers"}
    from .tuareg import plain_wheels
    plain = plain_wheels(xf, zf, Df, Wf, rim, RIM_W["front"], xr, zr, Dr, Wr, rim, RIM_W["rear"])
    hx, hz = f.leg(s_low, -36)                    # the front face of the lower triple clamp, where the winch's soft loop goes
    return BikeModel("street_triple_765", S, ties, (com["x"], 0.0, com["z"]), xr - xf, (xf, zf), (xr, zr), rim, Wr, colors=C, fine=fine,
                     hooks={"winch": (hx, 0.0, hz)},
                     plain=plain)

"""The Aprilia Tuareg 660 Rally (2025-on), built to Aprilia's figures and report 05's points (research/29).

Points come from research/05-bike-geometry.yaml (`g`) and the estimates in data/parts/bikes.yaml (`prm`), which the
owner's measurements patch (cad/inputs.py). The shapes between them are estimates from Aprilia's side image. Every
part touches the part that carries it, so the bike stands on its tyres (cad/tests/test_ute_supported.py).
"""
from __future__ import annotations

import re

from . import kit
from .moto import Fork, P, bar, blk, chain, mirrored, plan, rod, side, wheel

# Sizes come from data/parts/bikes.yaml (`estimates`), where each carries its source. research/29 lists them.
COLOURS = {"tyre": "#1b1b1b", "rim": "#c9a227", "metal": "#b8b8b8", "frame": "#26292b", "engine": "#3a3d40",
           "body": "#f1f1f1", "red": "#b03a2e", "seat": "#202020", "glass": "#a9c6d8", "gold": "#c9a227",
           "alloy": "#c3c7c9", "lamp": "#e8f1f5", "bag": "#4b4f3a", "ti": "#9aa0a6"}


def _rim_inch(size):
    return float(re.findall(r"(?:-|ZR|R)\s?(\d\d)", size)[0])


def tuareg(g, prm):
    from ..bike import BikeModel
    est = prm["estimates"]
    pts = g["points"]
    t = g["tyres"]
    S, C = {}, {}

    def add(name, shape, colour):
        S[name], C[name] = shape, COLOURS[colour]

    rims, wh, dsc, fk = est["rims"], est["wheels"], est["discs"], est["fork"]
    RIM_W = {"front": rims["front"] * 25.4, "rear": rims["rear"] * 25.4}
    SPOKES = wh["spokes"]
    KNOB = {"front": wh["knob_front"], "rear": wh["knob_rear"]}
    HUB = {"front": tuple(wh["hub_front"]), "rear": tuple(wh["hub_rear"])}
    DISC = {"front": dsc["front"] / 2, "rear": dsc["rear"] / 2}
    STANCHION_R, OUTER_R = fk["stanchion"] / 2, fk["outer"] / 2

    Df, Wf = t["front"]["diameter"]["v"], t["front"]["width"]["v"]
    Dr, Wr = t["rear"]["diameter"]["v"], t["rear"]["width"]["v"]
    rim_f, rim_r = _rim_inch(t["front"]["size"]) * 25.4 / 2, _rim_inch(t["rear"]["size"]) * 25.4 / 2
    xf, zf = pts["front_axle"]["x"], Df / 2
    xr, zr = pts["rear_axle"]["x"], Dr / 2
    length = prm.get("length", prm["owner"]["length"])
    x_end = length - prm["front_overhang"]
    screen_z = prm.get("screen_top_z", prm["screen_top"]["z"])
    screen_x = prm["screen_top"]["x"]

    # ---------------------------------------------------------------- wheels
    add("front tyre", wheel(kit.moto_tyre(Df, Wf, rim_f, RIM_W["front"], KNOB["front"], 30), xf, zf), "tyre")
    add("rear tyre", wheel(kit.moto_tyre(Dr, Wr, rim_r, RIM_W["rear"], KNOB["rear"], 30), xr, zr), "tyre")
    hr, hw, hf = HUB["front"]
    add("front wheel", wheel(kit.spoked_wheel(rim_f, RIM_W["front"] + 8, hr, hw, hf, SPOKES), xf, zf), "rim")
    hr2, hw2, hf2 = HUB["rear"]
    add("rear wheel", wheel(kit.spoked_wheel(rim_r, RIM_W["rear"] + 8, hr2, hw2, hf2, SPOKES, down_r=0.55 * rim_r), xr, zr), "rim")
    add("front brake discs", kit.fuse([wheel(kit.disc(DISC["front"], hr - 2, s * (hw / 2 + 1)), xf, zf) for s in (1, -1)]), "metal")
    add("rear brake disc", wheel(kit.disc(DISC["rear"], hr2 - 2, hw2 / 2 + 1), xr, zr), "metal")
    cy = -(Wr / 2 + 15)                      # chain line, between the tyre and the left swingarm arm (est.)
    add("rear sprocket", wheel(kit.lathe([(hr2 - 2, -hw2 / 2), (hr2 + 25, -hw2 / 2), (hr2 + 25, cy + 3), (112.0, cy + 3), (112.0, cy - 3),
                                          (hr2 - 2, cy - 3)]), xr, zr), "metal")
    add("front axle", rod((xf, -140, zf), (xf, 140, zf), 12.5), "metal")
    add("rear axle", rod((xr, -(Wr / 2 + 62), zr), (xr, Wr / 2 + 62, zr), 12.5), "metal")

    # ---------------------------------------------------------------- fork, clamps and steering head
    hs = fk["half_spacing"]
    f = Fork(xf, zf, g["published"]["rake"]["v"], 55.0)   # 55 mm offset from Aprilia's rake and trail (research/29)
    s_top = (fk["top_z"] - zf) / f.u[1]
    legs = []
    for s in (1, -1):
        y = s * hs
        legs += [f.tube(y, -35, 470, STANCHION_R), f.tube(y, 420, s_top + 20, OUTER_R)]
        lug = [f.leg(-45, -30), f.leg(60, -30), f.leg(60, 30), f.leg(-45, 30)]
        legs.append(side(lug, y - 26, y + 26))
    add("fork legs", kit.fuse(legs), "gold")
    add("lower triple clamp", f.clamp(s_top - 245, s_top - 215, 38, 40, hs + OUTER_R + 6), "alloy")
    add("top triple clamp", f.clamp(s_top - 25, s_top, 38, 40, hs + OUTER_R + 6), "alloy")
    (a0x, a0z), (a1x, a1z) = f.axis(s_top - 250), f.axis(s_top + 5)
    add("steering head", rod((a0x, 0, a0z), (a1x, 0, a1z), 30), "frame")
    cal = [f.leg(85, 10), f.leg(150, 10), f.leg(150, 75), f.leg(85, 75)]
    add("front brake calipers", kit.fuse([side(cal, s * (hw / 2 - 12), s * (hw / 2 + 22)) for s in (1, -1)]), "gold")

    # high front mudguard, on the lower clamp (05 tip x -156, z 775)
    mg = pts["front_mudguard_tip"]
    hwm = est["mudguard_half_width"]["v"]
    lc = f.leg(s_top - 245, 10)
    add("front mudguard", side([(mg["x"] - 4, mg["z"] - 15), (mg["x"], mg["z"] + 15), (40, 812), (200, 806), (lc[0] + 10, lc[1] + 4),
                                (lc[0] + 10, lc[1] - 14), (200, 784), (40, 790)], -hwm, hwm), "body")

    # ---------------------------------------------------------------- frame (steel tube trellis, est.)
    top = f.axis(s_top - 20)
    low = f.axis(s_top - 230)
    tubes = []
    for s in (1, -1):
        tubes.append(bar([(top[0] + 10, 0, top[1] - 20), (560, s * 150, 960), (850, s * 150, 900), (930, s * 150, 600)], 14))
        tubes.append(bar([(low[0] + 10, 0, low[1]), (450, s * 120, 822), (470, s * 150, 560), (560, s * 150, 300), (930, s * 150, 330)], 14))
        tubes.append(bar([(470, s * 150, 560), (560, s * 150, 960)], 11))
        tubes.append(bar([(850, s * 150, 900), (1460, s * 110, 905)], 12))
        tubes.append(bar([(930, s * 150, 600), (1260, s * 115, 700), (1460, s * 110, 905)], 12))
    tubes.append(rod((919, -150, 640), (919, 150, 640), 12))
    tubes.append(rod((1460, -110, 905), (1460, 110, 905), 10))
    tubes += [blk(895, 965, s * 140, s * 166, 330, 620) for s in (1, -1)]            # swingarm pivot plates
    add("frame", kit.fuse(tubes), "frame")
    add("radiator", kit.fuse([blk(360, 395, -165, 165, 600, 840)] + [blk(390, 462, s * 112, s * 132, 790, 812) for s in (1, -1)]), "engine")

    # ---------------------------------------------------------------- engine, skid plate, exhaust (est.)
    ew = est["engine_half_width"]["v"]
    crank = side([(450, 300), (520, 262), (880, 262), (930, 330), (930, 520), (830, 562), (560, 582), (470, 520)], -150, 150)
    block = side([(470, 520), (560, 582), (610, 770), (560, 805), (440, 805), (415, 700)], -125, 125)
    covers = [rod((760, 140, 400), (760, ew - 10, 400), 100), rod((690, -140, 425), (690, -(ew - 10), 425), 92)]
    add("engine", kit.fuse([crank, block] + covers), "engine")
    sk = pts["lowest_point_skid_plate"]
    # the Rally's aluminium skid plate wraps the engine's underside as wide as the engine (est.), its lowest edge on 05's line
    add("skid plate", side([(398, 470), (380, 470), (430, 300), (sk["x"][0], sk["z"]), (sk["x"][1], sk["z"]), (920, 300), (920, 318),
                            (sk["x"][1], sk["z"] + 18), (sk["x"][0], sk["z"] + 18), (445, 318)], -ew, ew), "alloy")
    sl = est["silencer"]
    sx0, sy0, sz0 = sl["start"]
    add("exhaust headers", kit.fuse([bar([(440, s * 45, 760), (400, s * 45, 560), (430, 110, 335), (900, 160, 330), (1100, sy0, 420),
                                          (sx0 + 30, sy0, sz0 + 14)], 22) for s in (1, -1)]), "ti")
    add("silencer (right)", kit.fuse([rod(sl["start"], sl["end"], sl["diameter"] / 2),
                                      bar([(1560, sy0, 640), (1500, 128, 740), (1430, 111, 874)], 9)]), "ti")

    # ---------------------------------------------------------------- swingarm, shock, chain
    sp = est["swingarm_pivot"]
    arms = []
    for s in (1, -1):
        arms.append(side([(sp["x"] - 10, sp["z"] + 38), (xr + 25, zr + 24), (xr + 25, zr - 24), (sp["x"] - 10, sp["z"] - 38)],
                         s * (Wr / 2 + 25), s * (Wr / 2 + 55)))
    arms.append(rod((sp["x"], -168, sp["z"]), (sp["x"], 168, sp["z"]), 12))
    arms.append(rod((1080, -(Wr / 2 + 30), 398), (1080, Wr / 2 + 30, 398), 15))
    add("swingarm", kit.fuse(arms), "alloy")
    add("rear shock", kit.fuse([rod((1080, 0, 405), (919, 0, 640), 22), rod((1040, 0, 465), (950, 0, 595), 34)]), "red")
    add("chain", chain((885, 395), 40.0, (xr, zr), 107.0, cy, 12.0), "metal")

    # ---------------------------------------------------------------- bodywork
    fw = est["fairing_half_width"]["v"]
    ff = est["fairing_front_half_width"]["v"]
    hl = pts["headlight_fairing_front"]
    tank = pts["tank_top"]
    prof = side([(hl["x"], 900), (hl["x"], hl["z"][1]), (260, 1060), (tank["x"], tank["z"]), (700, tank["z"] - 3), (700, 900),
                 (600, 760), (330, 760)], -fw, fw)
    wide = plan([(hl["x"], -ff), (hl["x"], ff), (300, fw), (700, fw), (700, -fw), (300, -fw)], 759, 1101)
    channel = blk(330, 720, -185, 185, 700, 1120)
    add("fairing and shrouds", (prof & wide).cut(channel), "body")
    add("headlight", blk(hl["x"] - 6, hl["x"] + 1, -75, 75, hl["z"][0] - 25, hl["z"][1] - 5), "lamp")
    add("dash", blk(300, 330, -80, 80, 1040, 1100), "seat")
    sw = est["screen_half_width"]["v"]
    add("screen", side([(hl["x"] + 10, hl["z"][1] - 5), (screen_x, screen_z), (screen_x + 6, screen_z - 2), (hl["x"] + 18, hl["z"][1] - 8)],
                       -sw, sw), "glass")
    tw = est["tank_half_width"]["v"]
    tk = side([(400, 960), (470, 1060), (tank["x"], tank["z"]), (760, 1085), (900, 1010), (900, 930), (560, 900), (420, 880)], -tw, tw)
    add("tank", tk & plan([(395, -150), (395, 150), (560, tw), (760, tw), (905, 160), (905, -160), (760, -tw), (560, -tw)], 870, 1100), "red")
    seat = pts["seat_low_point"]
    sw2 = est["seat_half_width"]["v"]
    sz = (seat["z"][0] + seat["z"][1]) / 2
    add("seat", side([(880, 965), (960, 905), (seat["x"][0], sz), (seat["x"][1], sz + 2), (1440, 925), (1460, 900), (1100, 850), (900, 885)],
                     -sw2, sw2), "seat")
    rack = pts["tail_rack_top"]
    tl = pts["tail_light_tip"]
    rw2 = est["tail_half_width"]["v"]
    tail = side([(1380, 905), (rack["x"][0], rack["z"][0] - 8), (rack["x"][1] - 10, rack["z"][1] - 10), (tl["x"], tl["z"]), (1810, 845),
                 (1460, 805), (1380, 820)], -rw2, rw2)
    add("tail", tail, "body")
    add("tail light", blk(tl["x"] - 14, tl["x"] + 1, -40, 40, tl["z"] - 25, tl["z"] - 3), "red")
    rk = [bar([(rack["x"][0], s * (rw2 - 10), rack["z"][0]), (rack["x"][1], s * (rw2 - 10), rack["z"][1])], 9) for s in (1, -1)]
    rk += [rod((x, -(rw2 - 10), z), (x, rw2 - 10, z), 8) for x, z in ((rack["x"][0], rack["z"][0]), (rack["x"][1], rack["z"][1]))]
    add("tail rack", kit.fuse(rk), "frame")
    pl = est["plate"]
    add("plate hanger", side([(1790, 850), (1812, 858), (x_end - 6, pl["z"][1]), (x_end - 6, pl["z"][1] - 14), (1800, 836)], -40, 40), "seat")
    from ..prims import box_span
    add("number plate", box_span(-pl["half_width"], pl["half_width"], x_end - 6, x_end, pl["z"][0], pl["z"][1]), "body")

    # ---------------------------------------------------------------- bars, controls, pegs, stand, crash bars
    bc = est["bar_clamp"]
    be = pts["bar_ends_handguards"]
    by = est["bar_end_y"]["v"]
    tie = (prm["tie_down_y"]["handlebar_inboard"]["v"], (g["tie_downs"]["handlebar_inboard"]["x"][0] + g["tie_downs"]["handlebar_inboard"]["x"][1]) / 2,
           g["tie_downs"]["handlebar_inboard"]["z"])
    ty, tx, tz = tie
    add("handlebar", bar([(be["x"], -(by - 15), be["z"]), (tx, -ty, tz), (bc["x"], -80, bc["z"] + 5), (bc["x"], 80, bc["z"] + 5),
                          (tx, ty, tz), (be["x"], by - 15, be["z"])], 14), "frame")
    tcl = f.axis(s_top, -5)
    add("bar risers", kit.fuse([rod((tcl[0], s * 40, tcl[1] - 4), (bc["x"], s * 40, bc["z"] + 5), 14) for s in (1, -1)]), "frame")
    for s, nm in ((1, "right"), (-1, "left")):
        add(f"bar end {nm}", rod((be["x"], s * (by - 15), be["z"]), (be["x"], s * by, be["z"]), 16), "metal")
    hg = est["handguard"]
    tip = pts["handguard_front_tip"]
    add("handguards", mirrored(lambda s: side([(tip["x"], tip["z"] - 10), (tip["x"] + 5, hg["z"][1]), (hg["x"][1], be["z"] + 15),
                                                (hg["x"][1], hg["z"][0]), (tip["x"] + 40, hg["z"][0])], s * hg["y"][0], s * hg["y"][1])), "body")
    mf = est["mirror_folded"]
    for s, nm in ((1, "right"), (-1, "left")):
        head = blk(mf["x"][0], mf["x"][1], s * mf["y"][0], s * mf["y"][1], mf["z"][0], mf["z"][1])
        stem = bar([(bc["x"] + 14, s * 240, bc["z"] + 12), ((mf["x"][0] + mf["x"][1]) / 2, s * 275, mf["z"][0] + 6)], 6)
        add(f"mirror {nm} (folded)", kit.fuse([head, stem]), "seat")
    fp = pts["rider_footpegs"]
    pr, pt = est["peg_root_y"]["v"], est["peg_tip_y"]["v"]
    for s, nm in ((1, "right"), (-1, "left")):
        add(f"footpeg {nm}", kit.fuse([rod((fp["x"], s * pr, fp["z"]), (fp["x"], s * pt, fp["z"]), 14),
                                       blk(fp["x"] - 30, fp["x"] + 20, s * 140, s * (pr + 6), fp["z"] - 20, 480)]), "frame")
    pp = pts["pillion_peg_hanger"]
    pyy = prm["tie_down_y"]["pillion_peg_hangers"]["v"]
    add("pillion peg hangers", mirrored(lambda s: kit.fuse([blk(pp["x"] - 25, pp["x"] + 25, s * (pyy - 35), s * (pyy + 15), pp["z"] - 25, 700),
                                                            rod((pp["x"], s * (pyy + 10), pp["z"]), (pp["x"], s * (pyy + 80), pp["z"]), 11)])), "frame")
    ss = est["side_stand"]
    fx, fy, fz = ss["foot"]
    add("side stand (folded)", rod(ss["pivot"], ss["foot"], 13), "frame")
    add("side stand foot", blk(fx - 35, fx + 35, fy - 40, fy + 10, fz - 8, fz + 8), "frame")
    cb = est.get("crash_bars")
    if cb:
        w, cz1 = cb["bar_half_width"], cb["z"][1]
        # from the down tube, out round the radiator to the bars' outer width (est.), with their top at TU-09
        add("crash bars", mirrored(lambda s: bar([(455, s * 128, 750), (395, s * 0.85 * w, cz1 - 12), (360, s * w, cz1 - 60), (345, s * w, 600),
                                                   (470, s * (w - 70), 520), (500, s * 150, 475)], 12)), "frame")

    # ---------------------------------------------------------------- Mosko Moto panniers on their racks
    pn = est.get("panniers")
    if pn:
        for s, nm in ((1, "right"), (-1, "left")):
            y0, y1 = sorted((s * (pn["outer_y"] - pn["thickness"]), s * pn["outer_y"]))
            add(f"pannier {nm} (Mosko Moto)", blk(pn["x"][0], pn["x"][1], y0, y1, pn["z"][0], pn["z"][1]), "bag")
        yi = pn["outer_y"] - pn["thickness"] - 8
        x0, x1, z0, z1 = pn["x"][0] + 25, pn["x"][1] - 25, pn["z"][0] + 30, pn["z"][1] - 40
        add("luggage racks", mirrored(lambda s: kit.fuse([bar([(x0, s * yi, z1), (x0, s * yi, z0), (x1, s * yi, z0), (x1, s * yi, z1)], 8),
                                                           bar([(x0 - 6, s * yi, z1), (x1 + 6, s * yi, z1)], 8),
                                                           bar([(x0, s * yi, 700), (1260, s * 115, 700)], 8),
                                                           bar([(x1, s * yi, z1), (1460, s * 110, 905)], 8)])), "frame")

    tyd = prm["tie_down_y"]
    td = g["tie_downs"]
    ties = {
        "handlebar_inboard": ((td["handlebar_inboard"]["x"][0] + td["handlebar_inboard"]["x"][1]) / 2, tyd["handlebar_inboard"]["v"],
                              td["handlebar_inboard"]["z"]),
        "pillion_peg_hangers": (td["pillion_peg_hangers"]["x"], tyd["pillion_peg_hangers"]["v"], td["pillion_peg_hangers"]["z"]),
    }
    com = prm["centre_of_mass"]
    fine = {"front tyre", "rear tyre", "front wheel", "rear wheel", "chain", "front brake discs", "rear brake disc", "rear sprocket",
            "front brake calipers", "luggage racks", "tail rack", "exhaust headers", "bar risers", "dash"}
    hx, hz = f.leg(s_top - 230, -38)              # the front face of the lower triple clamp, where the winch's soft loop goes
    return BikeModel("tuareg_660_rally", S, ties, (com["x"], 0.0, com["z"]), xr - xf, (xf, zf), (xr, zr), rim_r, Wr, colors=C, fine=fine,
                     hooks={"winch": (hx, 0.0, hz)},
                     plain=plain_wheels(xf, zf, Df, Wf, rim_f, RIM_W["front"], xr, zr, Dr, Wr, rim_r, RIM_W["rear"]))


def plain_wheels(xf, zf, Df, Wf, rim_f, wf, xr, zr, Dr, Wr, rim_r, wr):
    """Wheels for the drawings: each tyre and rim as plain solids, without knobs or spokes."""
    from ..prims import disc_x_axis, tyre_x_axis
    return {"front tyre": tyre_x_axis(xf, zf, Df, Wf, rim_f), "rear tyre": tyre_x_axis(xr, zr, Dr, Wr, rim_r),
            "front wheel": disc_x_axis(xf, zf, rim_f, wf), "rear wheel": disc_x_axis(xr, zr, rim_r, wr)}

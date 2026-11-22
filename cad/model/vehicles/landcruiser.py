"""The Toyota LandCruiser 79 single cab chassis, V8 (VDJ79R GXL, 2017 to 2022), as a product model in the ute frame
(DIM-U1: X rearward from the front axle, Y to the road side, Z up from the ground).

The envelope every check reads stays in data/ute/ute.yaml: wheelbase, tracks, the cab's back, width and roof height,
the bumper, the frame's rails, the tyres and the coupling. The shapes between come from Toyota's cab and chassis drawing
for the VDJ79R (LC70BBG, drawing 1-5), raised 61 mm for the 805 mm tyres and the Lovells lift so that its roof meets
the 1,955 mm of ute.yaml, with the front 150 mm longer for the 2017 front end (860 mm to the bumper). research/29 lists
every dimension and its source. Every part stands on, hangs from or is fixed to another, down to the tyres
(cad/tests/test_ute_supported.py).

`build(V, plain)` returns {id: [(label, shape, colour, alpha), ...]} for the parts in ute.yaml's `solids`, and the wheels.
With plain=True the tyres have no tread and the wheels no nuts, for the drawings.
"""
from __future__ import annotations

import math

from build123d import Plane

from ..prims import box_span, cyl, prism_xz
from . import kit

WHITE, GLASS, BLACK, STEEL, CHASSIS = "#f4f4f2", "#8fb3c9", "#1e1e1e", "#b8b8b8", "#1c2833"
LAMP, AMBER, TYRE, RIM, BAR = "#e8f1f5", "#f39c12", "#1b1b1b", "#f2f2f2", "#2d3436"

# Toyota's drawing 1-5, side view, at 3.20 mm a pixel, raised 61 mm (research/29)
COWL = (700.0, 1326.0)          # the windscreen's foot
SCREEN_TOP = (1150.0, 1880.0)   # the windscreen's top, under the roof's front edge
DOOR = (712.0, 1782.0)          # the door's front and rear edges
SILL_Z, BELT_Z = 563.0, 1299.0  # the door's foot and the belt line
FLOOR_Z = 820.0                 # the cab floor on its mounts, 46 mm over the frame (est.)
NOSE_X = -805.0                 # the grille's face, 55 mm behind the 860 mm bumper line, which the bull bar replaces
HALF_W = 895.0                  # half the 1,790 mm cab, mirrors excluded
GREEN_W = 870.0                 # the cab above the belt line, 25 mm in on each side (est.)


def _side(pts, y0, y1):
    """A side profile of (x, z) points extruded across the ute from y0 to y1."""
    return prism_xz(pts, min(y0, y1), max(y0, y1))


def _along(p0, p1, t):
    return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))


def cab(V):
    """The cab: the body to the belt line with its rockers outside the rails, the glasshouse and roof, the windscreen, the
    door and rear glass, the door shut lines and handles, the mirrors on their arms, the roof gutters, the body mounts on
    the frame and the factory snorkel up the road-side A-pillar."""
    back, top = V["cab_back_x"], V["cab_height"]
    out = []
    body = _side([(DOOR[0], FLOOR_Z), (back, FLOOR_Z), (back, BELT_Z), (DOOR[0], BELT_Z)], -HALF_W, HALF_W)
    for s in (1, -1):
        body = body + _side([(DOOR[0], SILL_Z), (back - 30, SILL_Z), (back, SILL_Z + 30), (back, FLOOR_Z + 1),
                             (DOOR[0], FLOOR_Z + 1)], s * 700, s * HALF_W)
    # door shut lines, 3 mm grooves round each door
    for s in (1, -1):
        y0, y1 = sorted((s * (HALF_W - 3), s * (HALF_W + 1)))
        body = body - box_span(DOOR[1] - 2, DOOR[1] + 2, y0, y1, SILL_Z + 20, BELT_Z + 1)
        body = body - box_span(DOOR[0] + 2, DOOR[1], y0, y1, SILL_Z + 18, SILL_Z + 22)
    glass_house = _side([(DOOR[0], BELT_Z), (back, BELT_Z), (back, top - 30), (back - 30, top), (1260, top), SCREEN_TOP,
                         (COWL[0] + 20, BELT_Z + 40)], -GREEN_W, GREEN_W)
    out.append(("cab body", body + glass_house, WHITE, 1.0))
    # windscreen: 40 mm of pillar along each edge, 1 mm proud of the glasshouse's sloped face
    p0, p1 = (COWL[0] + 20, BELT_Z + 40), SCREEN_TOP
    L = math.dist(p0, p1)
    n = ((p0[1] - p1[1]) / L, (p1[0] - p0[0]) / L)          # outward, forward and up
    a, b = _along(p0, p1, 45 / L), _along(p0, p1, 1 - 40 / L)
    screen = _side([(a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1]), (b[0] - 3 * n[0], b[1] - 3 * n[1]),
                    (a[0] - 3 * n[0], a[1] - 3 * n[1])], -(GREEN_W - 70), GREEN_W - 70)
    side = [box_span(860, DOOR[1] - 40, s * (GREEN_W - 2), s * (GREEN_W + 1), BELT_Z + 15, 1800) for s in (1, -1)]
    rear = box_span(back - 2, back + 2, -520, 520, 1400, 1740)
    out.append(("windscreen, door and rear glass", kit.fuse([screen] + side + [rear]), GLASS, 0.55))
    trim = []
    for s in (1, -1):
        y0, y1 = sorted((s * HALF_W, s * (HALF_W + 8)))
        trim.append(box_span(DOOR[1] - 110, DOOR[1] - 30, y0, y1, BELT_Z - 85, BELT_Z - 60))       # door handle
        g0, g1 = sorted((s * (GREEN_W - 6), s * (GREEN_W + 6)))
        trim.append(box_span(1240, back - 10, g0, g1, top - 22, top - 8))                          # roof gutter
        trim.append(box_span(1000, 1080, y0, y1, BELT_Z - 40, BELT_Z - 10))                       # mirror base
    out.append(("door handles, mirror bases and roof gutters", kit.fuse(trim), BLACK, 1.0))
    mirrors = []
    for s in (1, -1):
        arm = kit.tube([(1040, s * (HALF_W + 4), BELT_Z - 25), (1080, s * (HALF_W + 55), BELT_Z + 10),
                        (1085, s * (HALF_W + 70), BELT_Z + 40)], 11)
        y0, y1 = sorted((s * (HALF_W + 20), s * (HALF_W + 130)))
        head = box_span(1060, 1110, y0, y1, BELT_Z - 40, BELT_Z + 200)
        mirrors.append(arm + head)
    out.append(("mirrors", kit.fuse(mirrors), BLACK, 1.0))
    # the factory snorkel: up the road-side A-pillar, 60 mm ahead of it, from the guard to its head at the roof's corner
    lo, hi = _along(p0, p1, -0.05), _along(p0, p1, 0.96)
    off = 62
    pipe = kit.tube([(lo[0] + off * n[0] - 40, GREEN_W - 25, lo[1] + off * n[1] - 40), (lo[0] + off * n[0], GREEN_W - 25, lo[1] + off * n[1]),
                     (hi[0] + off * n[0], GREEN_W - 25, hi[1] + off * n[1])], 45)
    head = cyl((hi[0] + off * n[0] - 70, GREEN_W - 25, hi[1] + off * n[1] + 30), (hi[0] + off * n[0] + 90, GREEN_W - 25, hi[1] + off * n[1] + 30), 72)
    out.append(("snorkel", pipe + head, BLACK, 1.0))
    mounts = [box_span(x - 40, x + 40, s * 463, s * 523, V["frame_top_z"], FLOOR_Z) for x in (DOOR[0] + 120, back - 110) for s in (1, -1)]
    out.append(("body mounts", kit.fuse(mounts), BLACK, 1.0))
    return out


def _bonnet_z(x):
    """The bonnet's top line, from its front edge at Z 1,195 to the cowl at Z 1,322 (Toyota's drawing, raised)."""
    return 1195 + (x + 785) * 127 / 1475


def front(V):
    """Bonnet with the V8's scoop, the front guards cut round the wheels with their flares, the radiator panel, the grille
    with its slats, the headlights and the indicators."""
    out = []
    bonnet = _side([(NOSE_X, 900), (NOSE_X, 1175), (-785, 1195), (690, 1322), (DOOR[0], 1322), (DOOR[0], 900)], -760, 760)
    arch = []
    for s in (1, -1):
        bonnet = bonnet + _side([(NOSE_X, 560), (NOSE_X, 1160), (-785, 1180), (690, 1300), (DOOR[0], 1300), (DOOR[0], 560)],
                                s * 760, s * HALF_W)
        y0, y1 = sorted((s * 600, s * 1000))
        arch.append(cyl((0, y0, V["tyre_slr"]), (0, y1, V["tyre_slr"]), 470))
    bonnet = bonnet - arch[0] - arch[1]
    bonnet = bonnet + box_span(NOSE_X, NOSE_X + 15, -450, 450, 600, 901)                    # radiator panel
    scoop = _side([(-380, _bonnet_z(-380) - 5), (-380, _bonnet_z(-380) + 40), (-60, _bonnet_z(-60) + 58), (-40, _bonnet_z(-40) - 5)],
                  -350, 350)
    out.append(("bonnet and front guards", bonnet + scoop, WHITE, 1.0))
    out.append(("bonnet scoop's intake", box_span(-384, -379, -320, 320, _bonnet_z(-380) + 8, _bonnet_z(-380) + 34), BLACK, 1.0))
    flares = []
    for s in (1, -1):
        y0, y1 = sorted((s * HALF_W, s * (V["track_front"] / 2 + 160)))
        ring = cyl((0, y0, V["tyre_slr"]), (0, y1, V["tyre_slr"]), 530) - cyl((0, y0 - 1, V["tyre_slr"]), (0, y1 + 1, V["tyre_slr"]), 470)
        flares.append(ring & box_span(-600, 600, y0, y1, 560, 1000))
    out.append(("wheel arch flares", kit.fuse(flares), BLACK, 1.0))
    out.append(("grille", box_span(NOSE_X - 7, NOSE_X, -520, 520, 990, 1170), BLACK, 1.0))
    out.append(("grille slats", kit.fuse([box_span(NOSE_X - 10, NOSE_X - 7, -510, 510, z, z + 10) for z in (1030, 1075, 1120)]), WHITE, 1.0))
    lamps = [box_span(NOSE_X - 10, NOSE_X, s * 560, s * 860, 985, 1080) for s in (1, -1)]
    out.append(("headlights", kit.fuse(lamps), LAMP, 1.0))
    ind = [box_span(NOSE_X - 7, NOSE_X, s * 600, s * 820, 945, 975) for s in (1, -1)]
    ind += [box_span(-560, -520, *sorted((s * HALF_W, s * (HALF_W + 4))), 1060, 1080) for s in (1, -1)]
    out.append(("indicators", kit.fuse(ind), AMBER, 1.0))
    return out


def bull_bar(V):
    """The steel bull bar on the frame's front: the pan with the winch in its recess, the centre hoop, the wing tubes over
    the lamps and the plates that bolt it to the rails, inside report 16's envelope from X -940 mm."""
    x0 = -V["front_overhang"] - 80
    pan = box_span(x0 + 20, x0 + 110, -900, 900, 420, 690) - box_span(x0 + 15, x0 + 90, -300, 300, 470, 640)
    hoop = kit.tube([(x0 + 60, -430, 680), (x0 + 60, -430, 990), (x0 + 60, 430, 990), (x0 + 60, 430, 680)], 38)
    wings = [kit.tube([(x0 + 65, s * 880, 680), (x0 + 65, s * 880, 880), (x0 + 70, s * 620, 960), (x0 + 60, s * 430, 975)], 30) for s in (1, -1)]
    plates = [box_span(x0 + 105, V["frame_x0"] + 65, *sorted((s * 523, s * 531)), 630, 760) for s in (1, -1)]
    out = [("bar", kit.fuse([pan, hoop] + wings + plates), BAR, 1.0)]
    drum = cyl((x0 + 52, -260, 555), (x0 + 52, 260, 555), 35)
    ends = [box_span(x0 + 15, x0 + 90, *sorted((s * 260, s * 300)), 500, 610) for s in (1, -1)]
    out.append(("winch", kit.fuse([drum] + ends), STEEL, 1.0))
    return out


def frame(V):
    """The two C-section rails, their webs outboard and flanges in, the crossmembers between the webs, and the frame's
    front horns where the bull bar bolts on. The rails' outer faces and top flanges are the ones the box's brackets and
    rubber strip sit on (data/assemblies/ute-garage.yaml)."""
    zt, h, t = V["frame_top_z"], V["rail_h"], 6.0
    yo = V["frame_w"] / 2
    yi = yo - V["rail_w"]
    x0, x1 = V["frame_x0"], V["frame_x1"]
    rails = []
    for s in (1, -1):
        web = box_span(x0, x1, *sorted((s * (yo - t), s * yo)), zt - h, zt)
        top = box_span(x0, x1, *sorted((s * yi, s * (yo - t + 0.5))), zt - t, zt)
        bot = box_span(x0, x1, *sorted((s * yi, s * (yo - t + 0.5))), zt - h, zt - h + t)
        rails.append(kit.fuse([web, top, bot]))
    cross = [box_span(x - 40, x + 40, -(yo - t), yo - t, zt - h + 26, zt - 34) for x in (x0 + 65, 250, 1300, 1950, 3400, x1 - 40)]
    return [("rails", kit.fuse(rails), CHASSIS, 1.0), ("crossmembers", kit.fuse(cross), CHASSIS, 1.0)]


def _hubs(V, x, track):
    """The axle tube between its hubs, and a brake drum on each hub whose face carries the wheel's mounting face."""
    z, hy = V["tyre_slr"], track / 2 - 4                  # ET 0: the wheel's centre disc is 4 mm thick, inboard of its centre plane
    tube = cyl((x, -(hy - 120), z), (x, hy - 120, z), 50)
    hubs = [cyl((x, s * (hy - 140), z), (x, s * hy, z), 140) for s in (1, -1)]
    return tube, hubs


def front_axle(V, plain=False):
    """The front beam axle with its diff, hubs and drums, and the two coil springs on their seats, from the axle tube to
    the rails' bottom flanges. Each coil is a 16 mm wire on a 62 mm radius, eight straight runs a turn with mitred bends,
    which reads as a coil at a small part of a true helix's facets. The drawings take each coil as its outline cylinder."""
    z, zb = V["tyre_slr"], V["frame_top_z"] - V["rail_h"]
    tube, hubs = _hubs(V, 0.0, V["track_front"])
    diff = cyl((-130, 120, z), (130, 120, z), 125)
    out = [("axle", kit.fuse([tube, diff] + hubs), CHASSIS, 1.0)]
    yc = V["frame_w"] / 2 - V["rail_w"] / 2
    coils, seats = [], []
    z0, z1, pitch = z + 52, zb - 8, 36.0
    for s in (1, -1):
        seats += [cyl((0, s * yc, z + 45), (0, s * yc, z + 55), 80), cyl((0, s * yc, zb - 10), (0, s * yc, zb), 80)]
        if plain:
            coils.append(cyl((0, s * yc, z0 - 8), (0, s * yc, z1 + 8), 70))
            continue
        n = int((z1 - z0) / pitch * 8)
        pts = [(62 * math.cos(math.pi * k / 4), s * yc + 62 * math.sin(math.pi * k / 4), z0 + (z1 - z0) * k / n) for k in range(n + 1)]
        coils.append(kit.tube(pts, 8, mitred=True))
    out += [("coil springs", kit.fuse(coils), "#c0392b", 1.0), ("spring seats", kit.fuse(seats), CHASSIS, 1.0)]
    return out


def rear_axle(V):
    """The Lovells Elite's wide-track rear housing with its diff, hubs and drums on the two leaf springs, slung under it,
    and the springs' hangers and shackles under the rails."""
    x, z, zb = V["wheelbase"], V["tyre_slr"], V["frame_top_z"] - V["rail_h"]
    tube, hubs = _hubs(V, x, V["track_rear"])
    diff = cyl((x - 150, 0, z), (x + 140, 0, z), 140)
    out = [("axle", kit.fuse([tube, diff] + hubs), CHASSIS, 1.0)]
    yo, w = V["frame_w"] / 2, V["rail_w"]
    half = 700.0                                         # eye to eye 1,400 mm (est.)
    leaves, brackets = [], []
    for s in (1, -1):
        top, bot = [], []
        for k in range(9):
            u = -1 + k / 4
            zt = z - 48 + 120 * u * u
            top.append((x + half * u, zt))
            bot.append((x + half * u, zt - 25 - 45 * (1 - abs(u))))
        y0, y1 = sorted((s * (yo - w / 2 - 35), s * (yo - w / 2 + 35)))
        leaves.append(_side(top + bot[::-1], y0, y1))
        y0, y1 = sorted((s * (yo - w), s * yo))
        brackets += [box_span(x - half - 35, x - half + 35, y0, y1, z + 40, zb), box_span(x + half - 35, x + half + 35, y0, y1, z + 40, zb)]
    out += [("leaf springs", kit.fuse(leaves), CHASSIS, 1.0), ("spring hangers and shackles", kit.fuse(brackets), STEEL, 1.0)]
    return out


def tank(V):
    """The ARB Frontier tank between the rails, shaped round the propeller shaft, hung on two straps under the rails'
    bottom flanges. The UT-02 line puts its centre about 2,500 mm behind the front axle."""
    zb, yo = V["frame_top_z"] - V["rail_h"], V["frame_w"] / 2
    body = box_span(2150, 2850, -440, 440, zb - 314, zb - 14) - box_span(2140, 2860, -90, 90, zb - 315, zb - 175)
    straps = [box_span(x - 30, x + 30, -yo, yo, zb - 14, zb) for x in (2250, 2750)]
    return [("tank", body, "#2f3640", 1.0), ("tank straps", kit.fuse(straps), CHASSIS, 1.0)]


def towbar(V):
    """The Hayman Reese 03186RW: side arms bolted to the rails' outer faces, its crossbar under their rear ends behind the
    spare, the receiver, the 50 mm tongue and the DO35's ute half, the coupling point at the ball (ute.yaml)."""
    zt, yo = V["frame_top_z"], V["frame_w"] / 2
    bx, cz = V["ball_x"], V["coupling_z"]
    arms = [box_span(V["frame_x1"] - 300, V["frame_x1"] + 105, *sorted((s * yo, s * (yo + 8))), 520, zt - 24) for s in (1, -1)]
    xb = V["frame_x1"] + 35
    cross = box_span(xb, xb + 70, -(yo + 8), yo + 8, 445, 520)
    receiver = box_span(xb + 70, xb + 150, -30, 30, 452, 512) - box_span(xb + 69, xb + 151, -25, 25, 457, 507)
    tongue = box_span(xb + 75, bx, -25, 25, 457, 507)
    coupling = box_span(bx - 40, bx + 60, -40, 40, cz - 20, cz + 60)
    return [("towbar", kit.fuse(arms + [cross, receiver]), "#34495e", 1.0), ("tongue and DO35 coupling", tongue + coupling, STEEL, 1.0)]


# The ROH Trak 2 16 x 7 ET 0 on 5 x 150 studs and the LT265/75R16 all-terrain tyre (ute.yaml, research/29)
RIM_R, RIM_W = 16 * 25.4 / 2, 7 * 25.4


def wheel_parts(V, plain=False):
    """One wheel built about Z (cad/model/vehicles/kit.py): the tyre, the steel wheel, and its nuts and centre cap. The
    drawings take the wheel and tyre as their outline cylinder, as the sheets drew them before."""
    if plain:
        return [("tyre", cyl((0, 0, -V["tyre_w"] / 2), (0, 0, V["tyre_w"] / 2), V["tyre_d"] / 2), TYRE, 1.0)]
    tyre = kit.truck_tyre(V["tyre_d"], V["tyre_w"], RIM_R, RIM_W)
    out = [("tyre", tyre, TYRE, 1.0), ("wheel", kit.steel_wheel(RIM_R, RIM_W), RIM, 1.0)]
    if not plain:
        nuts = [cyl((75 * math.cos(a), 75 * math.sin(a), 0), (75 * math.cos(a), 75 * math.sin(a), 22), 14)
                for a in (2 * math.pi * k / 5 for k in range(5))]
        out.append(("wheel nuts and centre cap", kit.fuse(nuts + [cyl((0, 0, 0), (0, 0, 30), 62)]), STEEL, 1.0))
    return out


def spare(V, plain=False):
    """The spare under the tray, face down on Toyota's carrier: the cradle under its centre, the cable through its bore
    and the carrier's crossmember between the rails. Its centre is ute.yaml's UT-05 line."""
    x, y, z = V["wheelbase"] + 700, 0.0, 420.0
    lay = Plane(origin=(x, y, z), x_dir=(1, 0, 0), z_dir=(0, 0, -1))
    out = [(n, lay * s, c, a) for n, s, c, a in wheel_parts(V, plain) if n != "wheel nuts and centre cap"]
    zt, h, t = V["frame_top_z"], V["rail_h"], 6.0
    yo = V["frame_w"] / 2 - t
    carrier = [box_span(x - 30, x + 30, -yo, yo, zt - h + 26, zt - 34), cyl((x, y, z - 10), (x, y, zt - h + 26), 12),
               cyl((x, y, z - 10), (x, y, z), 95)]
    out.append(("carrier", kit.fuse(carrier), CHASSIS, 1.0))
    return out


def build(V, plain=False) -> dict:
    """Every part of the LandCruiser, by the ids of data/ute/ute.yaml's `solids`. plain=True builds the drawings'
    version: straight tubes, the coils as cylinders, no tread and no wheel nuts."""
    if plain:
        # the drawings' LandCruiser: its outline at A3, without the parts too small to read at 1:50 and with the bull
        # bar, the rails and the wheels as the sheets' blocks, because hidden-line removal is slow on fine detail
        x0, zt = -V["front_overhang"] - 80, V["frame_top_z"]
        drop = {"door handles, mirror bases and roof gutters", "bonnet scoop's intake", "grille slats", "winch"}
        with kit.straight():
            parts = {k: [p for p in v if p[0] not in drop] for k, v in build(V).items()}
        parts["BAR"] = [("bar", box_span(x0, x0 + 120, -HALF_W - 20, HALF_W + 20, 380, 1030), BAR, 1.0)]
        yo, yi = V["frame_w"] / 2, V["frame_w"] / 2 - V["rail_w"]
        parts["FRAME"] = [("rails", kit.fuse([box_span(V["frame_x0"], V["frame_x1"], *sorted((s * yi, s * yo)), zt - V["rail_h"], zt)
                                              for s in (1, -1)]), CHASSIS, 1.0)]
        parts["FAXLE"] = front_axle(V, plain=True)
        parts["SPARE"] = spare(V, plain=True)
        return parts
    return {"CAB": cab(V), "FRONT": front(V), "BAR": bull_bar(V), "FRAME": frame(V), "FAXLE": front_axle(V),
            "RAXLE": rear_axle(V), "TANK": tank(V), "TOWBAR": towbar(V), "SPARE": spare(V)}


def place_wheel(shape, centre, outward_y):
    return kit.on_axle(shape, centre, (0.0, outward_y, 0.0))

"""The Ford Ranger Super Duty single cab chassis (P703 RA, 2026MY) as a product model in the ute frame (DIM-U1: X
rearward from the front axle, Y to the road side, Z up from the ground, laden at GVM with the rear axle at its rating).

The envelope every check reads stays in data/ute/ute.yaml: wheelbase, track, the cab's back, width and roof, the front
overhang, the frame's rails, the tyres and the coupling, from Ford's body equipment mounting manual (BEMM, 03/2026) and
dealer specification sheet (2026MY). The shapes between are estimates read from Ford's published images of the truck,
and research/29 lists every dimension and its source. Every part stands on, hangs from or is fixed to another, down to
the tyres (cad/tests/test_ute_supported.py).

`build(V, plain)` returns {id: [(label, shape, colour, alpha), ...]} for the parts in ute.yaml's `solids`. With
plain=True the tyres have no tread and the wheels no nuts, for the drawings.
"""
from __future__ import annotations

import math

from build123d import Plane

from ..prims import box_span, cyl, prism_xz
from . import kit

BLUE, GLASS, BLACK, STEEL, CHASSIS = "#2e4a62", "#8fb3c9", "#1e1e1e", "#b8b8b8", "#1c2833"
LAMP, AMBER, TYRE, RIM, GREY = "#e8f1f5", "#f39c12", "#1b1b1b", "#c9ccce", "#4b5155"

# The cab and front end, ute frame, laden (est., read from Ford's side images against the 3,270 mm wheelbase)
COWL = (905.0, 1255.0)          # the windscreen's foot
SCREEN_TOP = (1395.0, 1820.0)   # the windscreen's top, under the roof's front edge
DOOR = (985.0, 1925.0)          # the door's front and rear edges
SILL_Z, BELT_Z = 585.0, 1290.0  # the door's foot and the belt line
FLOOR_Z = 790.0                 # the cab floor on its mounts
NOSE_X = -905.0                 # the grille's face, 40 mm behind the steel bar's face at the 945 mm front overhang
HALF_W = 930.0                  # half the cab body, 1,860 mm without the flares (est.)
GREEN_W = 895.0                 # the cab above the belt line, 35 mm in on each side (est.)
FLARE_W = 1016.0                # half Ford's 2,032 mm over the wheel flares


def _side(pts, y0, y1):
    """A side profile of (x, z) points extruded across the ute from y0 to y1."""
    return prism_xz(pts, min(y0, y1), max(y0, y1))


def _along(p0, p1, t):
    return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))


def cab(V):
    """The single cab: the body to the belt line with its sills, the glasshouse and roof, the windscreen, the door and rear
    glass, the door shut lines and handles, the mirrors on their arms, the body mounts on the frame and the Super Duty's
    sealed snorkel up the kerb-side A-pillar."""
    back, top = V["cab_back_x"], V["cab_height"]
    out = []
    body = _side([(DOOR[0] - 80, FLOOR_Z), (back, FLOOR_Z), (back, BELT_Z), (DOOR[0] - 80, BELT_Z)], -HALF_W, HALF_W)
    for s in (1, -1):
        body = body + _side([(DOOR[0], SILL_Z), (back - 40, SILL_Z), (back, SILL_Z + 40), (back, FLOOR_Z + 1),
                             (DOOR[0], FLOOR_Z + 1)], s * 700, s * HALF_W)
    for s in (1, -1):
        y0, y1 = sorted((s * (HALF_W - 3), s * (HALF_W + 1)))
        body = body - box_span(DOOR[1] - 2, DOOR[1] + 2, y0, y1, SILL_Z + 20, BELT_Z + 1)
        body = body - box_span(DOOR[0] + 2, DOOR[1], y0, y1, SILL_Z + 18, SILL_Z + 22)
    glass_house = _side([(DOOR[0] - 80, BELT_Z), (back, BELT_Z), (back - 10, top - 40), (back - 50, top), (1560, top),
                         SCREEN_TOP, (COWL[0] + 20, BELT_Z + 30)], -GREEN_W, GREEN_W)
    out.append(("cab body", body + glass_house, BLUE, 1.0))
    p0, p1 = (COWL[0] + 20, BELT_Z + 30), SCREEN_TOP
    L = math.dist(p0, p1)
    n = ((p0[1] - p1[1]) / L, (p1[0] - p0[0]) / L)          # outward, forward and up
    a, b = _along(p0, p1, 45 / L), _along(p0, p1, 1 - 40 / L)
    screen = _side([(a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1]), (b[0] - 3 * n[0], b[1] - 3 * n[1]),
                    (a[0] - 3 * n[0], a[1] - 3 * n[1])], -(GREEN_W - 70), GREEN_W - 70)
    side = [box_span(1180, DOOR[1] - 60, s * (GREEN_W - 2), s * (GREEN_W + 1), BELT_Z + 20, top - 90) for s in (1, -1)]
    rear = box_span(back - 2, back + 2, -560, 560, 1420, top - 110)
    out.append(("windscreen, door and rear glass", kit.fuse([screen] + side + [rear]), GLASS, 0.55))
    trim = []
    for s in (1, -1):
        y0, y1 = sorted((s * HALF_W, s * (HALF_W + 8)))
        trim.append(box_span(DOOR[1] - 150, DOOR[1] - 60, y0, y1, BELT_Z - 95, BELT_Z - 70))      # door handle
        trim.append(box_span(1060, 1150, y0, y1, BELT_Z - 40, BELT_Z - 5))                        # mirror base
        g0, g1 = sorted((s * (GREEN_W - 6), s * (GREEN_W + 6)))
        trim.append(box_span(1580, back - 60, g0, g1, top - 20, top - 6))                         # roof drip rail
    out.append(("door handles, mirror bases and drip rails", kit.fuse(trim), BLACK, 1.0))
    mirrors = []
    for s in (1, -1):
        arm = kit.tube([(1100, s * (HALF_W + 4), BELT_Z - 20), (1135, s * (HALF_W + 50), BELT_Z + 15),
                        (1140, s * (HALF_W + 75), BELT_Z + 40)], 11)
        y0, y1 = sorted((s * (HALF_W + 25), s * 1098.0))             # heads out to Ford's 2,197 mm, extended
        mirrors.append(arm + box_span(1115, 1165, y0, y1, BELT_Z - 50, BELT_Z + 190))
    out.append(("mirrors", kit.fuse(mirrors), BLACK, 1.0))
    # the sealed snorkel: from the kerb-side guard up the A-pillar to its head at the roof's corner
    lo, hi = _along(p0, p1, -0.05), _along(p0, p1, 0.95)
    off, y = 46, -(GREEN_W - 30)          # the pipe 1 mm off the pillar
    pipe = kit.tube([(lo[0] + off * n[0] - 40, y, lo[1] + off * n[1] - 40), (lo[0] + off * n[0], y, lo[1] + off * n[1]),
                     (hi[0] + off * n[0], y, hi[1] + off * n[1])], 45)
    head = box_span(hi[0] + off * n[0] - 60, hi[0] + off * n[0] + 110, y - 55, y + 55, hi[1] + off * n[1] - 10, hi[1] + off * n[1] + 75)
    out.append(("snorkel", pipe + head, BLACK, 1.0))
    yo = V["rail_y"] + V["rail_w"] / 2
    mounts = [box_span(x - 40, x + 40, *sorted((s * (yo - 60), s * yo)), V["frame_front_z"], FLOOR_Z) for x in (DOOR[0] + 60, back - 120) for s in (1, -1)]
    out.append(("body mounts", kit.fuse(mounts), BLACK, 1.0))
    return out


def _bonnet_z(x):
    """The bonnet's top line, from its front edge at Z 1,145 to the cowl at Z 1,250 (est.)."""
    return 1145 + (x + 880) * 105 / (COWL[0] + 880)


def front(V):
    """Bonnet and front guards cut round the wheels, the wide wheel flares, the grille with its bars, the C-clamp
    headlights and the indicators."""
    out = []
    zb = V["tyre_slr"]
    bonnet = _side([(NOSE_X, 860), (NOSE_X, 1120), (-880, 1145), (COWL[0], 1250), (DOOR[0] - 80, 1252), (DOOR[0] - 80, 860)], -800, 800)
    arch = []
    for s in (1, -1):
        bonnet = bonnet + _side([(NOSE_X, 560), (NOSE_X, 1110), (-880, 1135), (COWL[0], 1235), (DOOR[0] - 80, 1240), (DOOR[0] - 80, 560)],
                                s * 800, s * HALF_W)
        y0, y1 = sorted((s * 600, s * 1040))
        arch.append(cyl((0, y0, zb), (0, y1, zb), 490))
    bonnet = bonnet - arch[0] - arch[1]
    out.append(("bonnet and front guards", bonnet, BLUE, 1.0))
    flares = []
    for s in (1, -1):
        y0, y1 = sorted((s * (HALF_W - 1), s * FLARE_W))
        ring = cyl((0, y0, zb), (0, y1, zb), 560) - cyl((0, y0 - 1, zb), (0, y1 + 1, zb), 490)
        flares.append(ring & box_span(-650, 650, y0, y1, zb - 60, 1100))
    out.append(("wheel arch flares", kit.fuse(flares), BLACK, 1.0))
    out.append(("grille", box_span(NOSE_X - 8, NOSE_X, -560, 560, 870, 1105), BLACK, 1.0))
    out.append(("grille bars", kit.fuse([box_span(NOSE_X - 12, NOSE_X - 8, -545, 545, z, z + 14) for z in (930, 990, 1050)]), GREY, 1.0))
    lamps = []
    for s in (1, -1):
        y0, y1 = sorted((s * 590, s * 880))
        c = box_span(NOSE_X - 10, NOSE_X, y0, y1, 905, 1100) - box_span(NOSE_X - 11, NOSE_X + 1, *sorted((s * 625, s * 850)), 935, 1070)
        lamps.append(c + box_span(NOSE_X - 6, NOSE_X, *sorted((s * 640, s * 835)), 990, 1030))
    out.append(("headlights", kit.fuse(lamps), LAMP, 1.0))
    ind = [box_span(-640, -600, *sorted((s * HALF_W, s * (HALF_W + 4))), 1030, 1050) for s in (1, -1)]
    out.append(("indicators", kit.fuse(ind), AMBER, 1.0))
    return out


def front_bar(V):
    """Ford's frame-mounted steel front bar (standard on the Super Duty): its face, the lower steel bash plate and the two
    plates that bolt it to the rails' front ends."""
    x0, yo = -V["front_overhang"], V["rail_y"] + V["rail_w"] / 2
    face = box_span(x0, x0 + 40, -900, 900, 420, 760) - box_span(x0 - 1, x0 + 41, -240, 240, 560, 640)
    plate = box_span(x0 + 10, V["frame_x0"], -560, 560, 400, 425)
    lugs = [box_span(x0 + 40, V["frame_x0"] + 60, *sorted((s * yo, s * (yo + 10))), 560, V["frame_front_z"]) for s in (1, -1)]
    return [("bar", kit.fuse([face, plate] + lugs), CHASSIS, 1.0),
            ("recovery points", kit.fuse([box_span(x0 - 25, x0, *sorted((s * 340, s * 380)), 470, 520) for s in (1, -1)]), "#c0392b", 1.0)]


def frame(V):
    """The two C-section rails, their webs outboard and flanges in, level at the laden height, and the crossmembers between
    the webs. The rails' centrelines are Ford's 446 mm from the truck's centreline (BEMM p. 131, est.). Ford's body
    mounting pads on their brackets belong to the box's module (data/assemblies/ute-garage.yaml)."""
    zt, h, t = V["frame_top_z"], V["rail_h"], 7.0
    yo = V["rail_y"] + V["rail_w"] / 2
    yi = yo - V["rail_w"]
    x0, x1 = V["frame_x0"], V["frame_x1"]
    rails = []
    for s in (1, -1):
        web = box_span(x0, x1, *sorted((s * (yo - t), s * yo)), zt - h, zt)
        top = box_span(x0, x1, *sorted((s * yi, s * (yo - t + 0.5))), zt - t, zt)
        bot = box_span(x0, x1, *sorted((s * yi, s * (yo - t + 0.5))), zt - h, zt - h + t)
        rails.append(kit.fuse([web, top, bot]))
    cross = [box_span(x - 40, x + 40, -(yo - t), yo - t, zt - h + 30, zt - 40) for x in (x0 + 60, 420, 1500, 2350, 3700, x1 - 60)]
    return [("rails", kit.fuse(rails), CHASSIS, 1.0), ("crossmembers", kit.fuse(cross), CHASSIS, 1.0)]


def _hub(V, x, s, track):
    """A wheel hub on its knuckle or axle end: the drum whose outer face is the wheel's mounting face."""
    z, hy = V["tyre_slr"], hub_face(V, track)
    return cyl((x, s * (hy - 140), z), (x, s * hy, z), 135)


def hub_face(V, track):
    """The hub's outer face, where the wheel's centre disc seats: half the track less the disc's 4 mm, moved out by the
    wheel's offset."""
    return track / 2 - 4 + V["wheel_offset"]


def front_suspension(V, plain=False):
    """Independent front suspension: on each side a knuckle on the hub, upper and lower control arms to the front
    crossmember and a coil-over damper from the lower arm up to its tower under the rail, the front differential and its
    half shafts. The drawings take each coil as its outline cylinder."""
    z, zb, yr = V["tyre_slr"], V["frame_front_z"] - V["rail_h"], V["rail_y"]
    out, parts = [], []
    xm = box_span(-160, 160, -(yr - 30), yr - 30, z - 120, z - 40)            # the front crossmember under the engine
    diff = cyl((-120, 60, z), (130, 60, z), 115)
    parts += [xm, diff]
    coils, towers = [], []
    for s in (1, -1):
        hub = _hub(V, 0.0, s, V["track_front"])
        hy = hub_face(V, V["track_front"]) - 140
        knuckle = box_span(-60, 60, *sorted((s * (hy - 70), s * (hy + 1))), z - 170, z + 200)
        lower = box_span(-110, 110, *sorted((s * (yr - 40), s * (hy - 60))), z - 120, z - 80)
        upper = box_span(-70, 70, *sorted((s * (yr + 45), s * (hy - 60))), z + 150, z + 180)
        shaft = cyl((0, s * 140, z), (0, s * (hy - 70), z), 30)
        parts += [hub, knuckle, lower, upper, shaft]
        yc = s * (yr - 20)
        z0, z1 = z - 80, zb - 12
        towers.append(box_span(-70, 70, *sorted((yc - 70, yc + 70)), zb - 12, zb))
        if plain:
            coils.append(cyl((0, yc, z0), (0, yc, z1), 64))
            continue
        seats = [cyl((0, yc, z0), (0, yc, z0 + 10), 64), cyl((0, yc, z1 - 10), (0, yc, z1), 64)]
        damper = cyl((0, yc, z0 + 10), (0, yc, z1 - 10), 30)
        n = int((z1 - z0 - 24) / 38.0 * 8)
        pts = [(56 * math.cos(math.pi * k / 4), yc + 56 * math.sin(math.pi * k / 4), z0 + 12 + (z1 - z0 - 24) * k / n) for k in range(n + 1)]
        coils.append(kit.fuse(seats + [damper, kit.tube(pts, 7, mitred=True)]))
    out.append(("knuckles, control arms, crossmember, differential and half shafts", kit.fuse(parts + towers), CHASSIS, 1.0))
    out.append(("coil-over dampers", kit.fuse(coils), "#c0392b", 1.0))
    return out


def rear_axle(V):
    """The heavy-duty rear axle with its differential and hubs on the two leaf springs over it, and the springs'
    hangers and shackles under the rails."""
    x, z, zb = V["wheelbase"], V["tyre_slr"], V["frame_top_z"] - V["rail_h"]
    hubs = [_hub(V, x, s, V["track_rear"]) for s in (1, -1)]
    hy = hub_face(V, V["track_rear"]) - 120
    tube = cyl((x, -hy, z), (x, hy, z), 55)
    diff = cyl((x - 160, 0, z), (x + 150, 0, z), 150)
    out = [("axle", kit.fuse([tube, diff] + hubs), CHASSIS, 1.0)]
    yr, half = V["rail_y"], 700.0                       # eye to eye 1,400 mm (est.)
    leaves, brackets = [], []
    for s in (1, -1):
        top, bot = [], []
        for k in range(9):
            u = -1 + k / 4
            zc = z + 61 + 75 * u * u                     # the pack's lower face on its U-bolt plate, rising to the eyes
            top.append((x + half * u, zc + 75 - 35 * abs(u)))
            bot.append((x + half * u, zc))
        y0, y1 = sorted((s * (yr - 37), s * (yr + 37)))
        leaves.append(_side(top + bot[::-1], y0, y1))
        y0, y1 = sorted((s * (yr - 35), s * (yr + 35)))
        eye = z + 61 + 75 + 34                           # 6 mm into the spring's end
        brackets += [box_span(x - half - 35, x - half + 35, y0, y1, eye, zb), box_span(x + half - 35, x + half + 35, y0, y1, eye, zb)]
        brackets.append(box_span(x - 45, x + 45, y0, y1, z + 54, z + 61))      # the U-bolt plate on the axle tube
    out += [("leaf springs", kit.fuse(leaves), CHASSIS, 1.0), ("spring hangers, shackles and U-bolt plates", kit.fuse(brackets), STEEL, 1.0)]
    return out


def tank(V):
    """The 130 L fuel tank between the rails ahead of the rear axle, on two straps under the rails' bottom flanges."""
    zb, yo = V["frame_top_z"] - V["rail_h"], V["rail_y"] + V["rail_w"] / 2
    body = box_span(2100, 2850, -(yo - 70), yo - 70, zb - 250, zb - 14) - box_span(2090, 2860, -80, 80, zb - 251, zb - 130)
    straps = [box_span(x - 30, x + 30, -yo, yo, zb - 14, zb) for x in (2200, 2750)]
    return [("tank", body, "#2f3640", 1.0), ("tank straps", kit.fuse(straps), CHASSIS, 1.0)]


def urea(V):
    """The diesel exhaust fluid tank on its bracket outside the kerb-side rail, between the cab and the rear wheel and
    clear of the box's runner. Its top stands 47 mm over the rail top (BEMM p. 128), under the box's outriggers (est.)."""
    zt, yo = V["frame_top_z"], V["rail_y"] + V["rail_w"] / 2
    body = box_span(2150, 2500, -(yo + 400), -(yo + 180), zt - 120, zt + 47)
    bracket = box_span(2200, 2450, -(yo + 400), -yo, zt - 140, zt - 120)
    return [("diesel exhaust fluid tank", body, "#dfe6e9", 1.0), ("its bracket", bracket, CHASSIS, 1.0)]


def towbar(V):
    """Ford's standard 4.5 t tow bar: side arms bolted to the rails' outer faces and its crossbar and receiver at the
    frame's end, 1,255 mm behind the rear axle (dealer sheet), and in the receiver the tongue for the DO45-type coupling's
    truck half, its tow pin at the coupling point (ute.yaml). The tongue's drop sets the pin's height (UTE-01)."""
    zt, yo = V["frame_top_z"], V["rail_y"] + V["rail_w"] / 2
    bx, cz = V["ball_x"], V["coupling_z"]
    xr = V["wheelbase"] + V["towbar_behind_axle"]
    arms = [box_span(V["frame_x1"] - 320, V["frame_x1"] + 60, *sorted((s * yo, s * (yo + 8))), zt - V["rail_h"] - 80, zt - 30) for s in (1, -1)]
    zr = zt - V["rail_h"] - 70                          # the receiver's centre, under the crossbar (est.)
    cross = box_span(V["frame_x1"] - 10, V["frame_x1"] + 60, -(yo + 8), yo + 8, zr - 40, zr + 60)
    receiver = box_span(V["frame_x1"] + 60, xr, -38, 38, zr - 38, zr + 38) - box_span(V["frame_x1"] + 59, xr + 1, -33, 33, zr - 33, zr + 33)
    shank = box_span(V["frame_x1"] + 70, xr + 30, -32, 32, zr - 32, zr + 32)
    drop = box_span(xr + 30, xr + 90, -32, 32, cz - 30, zr + 32)
    tongue = box_span(xr + 90, bx + 55, -40, 40, cz - 30, cz)
    pin = cyl((bx, 0, cz), (bx, 0, cz + 70), 28) + cyl((bx, 0, cz - 60), (bx, 0, cz), 16)
    return [("tow bar and receiver", kit.fuse(arms + [cross, receiver]), "#34495e", 1.0),
            ("hitch tongue and the DO45-type tow pin", kit.fuse([shank, drop, tongue, pin]), STEEL, 1.0)]


RIM_R, RIM_W = 18 * 25.4 / 2, 8 * 25.4


def wheel_parts(V, plain=False):
    """One wheel built about Z (kit.py): the LT275/70R18 all-terrain tyre, Ford's 18 x 8 steel wheel on eight studs, and
    its nuts and centre cap. The drawings take the wheel and tyre as their outline cylinder."""
    if plain:
        return [("tyre", cyl((0, 0, -V["tyre_w"] / 2), (0, 0, V["tyre_w"] / 2), V["tyre_d"] / 2), TYRE, 1.0)]
    tyre = kit.truck_tyre(V["tyre_d"], V["tyre_w"], RIM_R, RIM_W)
    out = [("tyre", tyre, TYRE, 1.0), ("wheel", kit.steel_wheel(RIM_R, RIM_W, windows=10, studs=8, pcd=170.0, bore=125.0,
                                                                    offset=V["wheel_offset"]), RIM, 1.0)]
    nuts = [cyl((85 * math.cos(a), 85 * math.sin(a), V["wheel_offset"]), (85 * math.cos(a), 85 * math.sin(a), V["wheel_offset"] + 22), 13)
            for a in (2 * math.pi * k / 8 for k in range(8))]
    out.append(("wheel nuts and centre cap", kit.fuse(nuts + [cyl((0, 0, V["wheel_offset"]), (0, 0, V["wheel_offset"] + 30), 66)]), STEEL, 1.0))
    return out


def spare(V, plain=False):
    """The full-size steel spare under the rear of the frame, face down on Ford's winch carrier: the cradle under its
    centre, the cable through its bore, and the winch on its crossmember between the rails."""
    x, z = V["spare_x"], V["spare_z"]
    lay = Plane(origin=(x, 0.0, z), x_dir=(1, 0, 0), z_dir=(0, 0, -1))
    out = [(n, lay * s, c, a) for n, s, c, a in wheel_parts(V, plain) if n != "wheel nuts and centre cap"]
    zt, h, t = V["frame_top_z"], V["rail_h"], 7.0
    yo = V["rail_y"] + V["rail_w"] / 2 - t
    carrier = [box_span(x - 35, x + 35, -yo, yo, zt - h + 30, zt - 40), cyl((x, 0, z - V["tyre_w"] / 2 - 12), (x, 0, zt - h + 30), 12),
               cyl((x, 0, z - V["tyre_w"] / 2 - 12), (x, 0, z - V["tyre_w"] / 2 + 2), 95)]
    out.append(("winch carrier", kit.fuse(carrier), CHASSIS, 1.0))
    return out


def build(V, plain=False) -> dict:
    """Every part of the Ranger Super Duty, by the ids of data/ute/ute.yaml's `solids`. plain=True builds the drawings'
    version: straight tubes, the coils as cylinders, no tread and no wheel nuts."""
    if plain:
        drop = {"door handles, mirror bases and drip rails", "grille bars", "recovery points", "indicators"}
        with kit.straight():
            parts = {k: [p for p in v if p[0] not in drop] for k, v in build(V).items()}
        yo, yi = V["rail_y"] + V["rail_w"] / 2, V["rail_y"] - V["rail_w"] / 2
        zt = V["frame_top_z"]
        parts["FRAME"] = [("rails", kit.fuse([box_span(V["frame_x0"], V["frame_x1"], *sorted((s * yi, s * yo)), zt - V["rail_h"], zt)
                                              for s in (1, -1)]), CHASSIS, 1.0)]
        parts["FAXLE"] = front_suspension(V, plain=True)
        parts["SPARE"] = spare(V, plain=True)
        return parts
    return {"CAB": cab(V), "FRONT": front(V), "BAR": front_bar(V), "FRAME": frame(V), "FAXLE": front_suspension(V),
            "RAXLE": rear_axle(V), "TANK": tank(V), "UREA": urea(V), "TOWBAR": towbar(V), "SPARE": spare(V)}


def place_wheel(shape, centre, outward_y):
    return kit.on_axle(shape, centre, (0.0, outward_y, 0.0))

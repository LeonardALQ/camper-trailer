"""The wet room's products (research report 28 section 1): the tray, the Thetford C223-CS, the cassette bin, the basin
and its fittings, the DauerShower 2.0, the drains, the grey tote, the partition with its inner door."""
from __future__ import annotations

from build123d import Ellipse, Plane, extrude

from . import ALU, BLACK, CHROME, DARK, GLASS, GREY, RUBBER, STEEL, WHITE, product

GRP = "#eef2f3"
TRAY = "#dfe9ea"


def _ell(fr, u, v, a_u, b_v, w0, w1):
    """An elliptical cylinder standing up from w0 to w1, its semi-axes a_u along u and b_v along v."""
    x, y, z = fr.pt(u, v, w0)
    along_y = fr.front in ("+y", "-y")
    ax, ay = (a_u, b_v) if along_y else (b_v, a_u)
    return extrude(Plane.XY.offset(z).shift_origin((x, y, z)) * Ellipse(ax, ay), amount=w1 - w0)


@product("wet_room_tray")
def tray(fr, V, sp, b):
    """One moulded GRP tray: a 30 mm floor on its H80 wedge, 100 mm upstands at the walls, 30 mm lips at both doors,
    and the shower zone's 20 mm lip round the DauerShower's drain (report 21 section 6). Seen from the partition."""
    W, D, t = fr.W, fr.D, 5.0
    out = [("floor, GRP on the H80 wedge", fr.box(0, 0, 0, W, D, 30), TRAY, 1.0)]
    for side, v0 in (("partition", 0.0), ("rear wall", D - t)):
        u = 0.0
        for g in sorted([tuple(d["u"]) for d in sp.get("doors", []) if d["wall"] == side]) + [(W, W)]:
            if g[0] > u:
                out.append((f"upstand at the {side}", fr.box(u, v0, 30, g[0] - u, t, 100), TRAY, 1.0))
            if g[1] > g[0]:
                out.append((f"lip at the {side} door", fr.box(g[0], v0, 30, g[1] - g[0], t, 30), TRAY, 1.0))
            u = max(u, g[1])
    for u0 in (0.0, W - t):
        out.append(("upstand at the side wall", fr.box(u0, t, 30, t, D - 2 * t, 100), TRAY, 1.0))
    sz = sp.get("shower_zone")
    if sz:
        u0, u1, v0, v1 = sz
        out.append(("shower zone lip, 20 mm", fr.box(u0, v1 - 30, 30, u1 - u0, 30, 20), TRAY, 1.0))
        out.append(("shower zone lip, 20 mm", fr.box(u1 - 30, v0, 30, 30, v1 - v0 - 30, 20), TRAY, 1.0))
    return out


@product("thetford_c223cs")
def toilet(fr, V, sp, b):
    """Thetford C223-CS: 394 wide, 580 deep and 534 high overall, the seat 492 mm up (Thetford), the swivel bowl on a
    moulded base, the flush panel on the back pedestal. Front faces the room, its back to the wall and the service door."""
    W, D, H = fr.W, fr.D, fr.H
    seat = 492.0
    base = fr.rbox(12, 40, 0, W - 24, D - 40, seat - 70, 60, "w")
    ped = fr.rbox(0, D - 170, 0, W, 170, H - 10, 25, "w")
    panel = fr.box(60, D - 171, H - 70, W - 120, 1.5, 45)
    button = fr.cyl_v(W - 80, H - 47, 14, D - 174, D - 170)
    bowl = _ell(fr, W / 2, 230, 175, 215, seat - 70, seat - 22)
    seat_ring = _ell(fr, W / 2, 225, 172, 212, seat - 22, seat) - _ell(fr, W / 2, 225, 110, 140, seat - 23, seat + 1)
    lid = _ell(fr, W / 2, 230, 178, 218, seat, seat + 18)
    hinge = fr.box(W / 2 - 90, D - 200, seat - 10, 180, 32, 34)
    return [("base", base, WHITE, 1.0), ("back pedestal with the flush panel", ped, WHITE, 1.0),
            ("flush panel", panel, DARK, 1.0), ("flush button", button, GREY, 1.0), ("swivel bowl", bowl, WHITE, 1.0),
            ("seat", seat_ring, "#e5e8e8", 1.0), ("lid", lid, WHITE, 1.0), ("seat hinge", hinge, GREY, 1.0)]


@product("cassette_bin")
def cassette_bin(fr, V, sp, b):
    """The sealed GRP bin for two spare Thetford 50046 cassettes, with a gasketed lid, standing on the tray."""
    W, D, H = fr.W, fr.D, fr.H
    body = fr.rbox(0, 0, 0, W, D, H - 25, 20, "w")
    lid = fr.rbox(0, 0, H - 25, W, D, 25, 15, "w")
    seal = fr.box(-0.5, 10, H - 28, 1.0, D - 20, 6)
    latch = fr.box(W / 2 - 30, -1, H - 60, 60, 1.0, 40)
    return [("bin", body, GRP, 1.0), ("gasketed lid", lid, GRP, 1.0), ("lid seal", seal, RUBBER, 1.0), ("latch", latch, STEEL, 1.0)]


@product("basin_vanity")
def basin(fr, V, sp, b):
    """The 385 x 285 x 115 caravan basin set in a 15 mm GRP vanity shelf on two brackets screwed to the partition.
    Frame front +x: the room side, the partition at the back."""
    W, D, H = fr.W, fr.D, fr.H
    shelf = fr.box(0, 0, H - 15, W, D, 15)
    bowl_out = fr.rbox(25, 20, 0, W - 50, D - 40, H - 14, 30, "w")
    bowl_in = fr.rbox(40, 35, 15, W - 80, D - 70, H, 25, "w")
    bowl = bowl_out - bowl_in
    shelf = shelf - fr.box(40, 35, H - 16, W - 80, D - 70, 17)
    waste = fr.cyl_w(W / 2, D / 2, 20, 14, 16)
    out = [("vanity shelf", shelf, GRP, 1.0), ("basin", bowl, WHITE, 1.0), ("waste", waste, CHROME, 1.0)]
    for u in (2.0, W - 8.0):
        tri = fr.prism_vw([(D - 0.5, H - 15), (D - 0.5, 5), (D - 140, H - 15)], u, u + 6)
        out.append(("shelf bracket", tri, STEEL, 1.0))
    return out


@product("mirror_cabinet")
def mirror_cabinet(fr, V, sp, b):
    """Aluminium-framed mirror cabinet 450 x 120 x 600, screwed to the partition."""
    W, D, H = fr.W, fr.D, fr.H
    body = fr.box(0, 3, 0, W, D - 3, H)
    door = fr.box(4, 0, 4, W - 8, 3, H - 8)
    frame = fr.box(0, 0, 0, W, 3, H) - fr.box(10, -1, 10, W - 20, 5, H - 20)
    return [("cabinet", body, ALU, 1.0), ("mirror door", door, "#d6eaf8", 1.0), ("frame", frame, ALU, 1.0)]


@product("basin_mixer")
def basin_mixer(fr, V, sp, b):
    """A wall-mounted basin mixer with a single lever and a 4 L/min regulator, its spout over the bowl."""
    W, D, H = fr.W, fr.D, fr.H
    plate = fr.cyl_v(W / 2, 40, 30, D - 8, D)
    body = fr.cyl_v(W / 2, 40, 18, 30, D - 8)
    spout = fr.box(W / 2 - 10, 0, 25, 20, 60, 16)
    lever = fr.box(W / 2 - 6, D - 60, 55, 12, 30, H - 60)
    return [("wall plate", plate, CHROME, 1.0), ("mixer body", body, CHROME, 1.0), ("spout", spout, CHROME, 1.0),
            ("lever", lever, CHROME, 1.0)]


@product("towel_rail")
def towel_rail(fr, V, sp, b):
    """A 600 mm stainless double towel rail on two wall brackets."""
    W, D, H = fr.W, fr.D, fr.H
    out = []
    for u in (30.0, W - 30.0):
        out.append(("bracket", fr.box(u - 6, 0, H / 2 - 35, 12, D - 6, 70), STEEL, 1.0))
        out.append(("wall rose", fr.cyl_v(u, H / 2, 25, D - 6, D), STEEL, 1.0))
    for w in (H / 2 - 22, H / 2 + 22):
        out.append(("rail", fr.cyl_u(14, w, 9, 0, W), STEEL, 1.0))
    return out


@product("dauershower_tech")
def ds_tech(fr, V, sp, b):
    """The DauerShower 2.0's technical unit (pump, 2.4 kW heater, filter and UV-C) in its dry cabinet on the
    partition's living face. Frame front -x: the cabinet's door faces the kitchen."""
    W, D, H = fr.W, fr.D, fr.H
    cab = fr.box(0, 0, 0, W, D, H) - fr.box(12, 12, 12, W - 24, D, H - 24)
    unit = fr.rbox(20, 14, 20, W - 40, D - 14, H - 40, 8, "v")
    lamp = fr.cyl_v(W - 40, H - 40, 6, -0.9, 0.1)
    return [("dry cabinet with its door", cab, "#d9c3a0", 1.0), ("technical unit", unit, "#2c3e50", 1.0), ("status lamp", lamp, "#2ecc71", 1.0)]


@product("dauershower_panel")
def ds_panel(fr, V, sp, b):
    """The DauerShower's control panel on the partition's wet face, with its two touch keys and display (est.)."""
    W, D, H = fr.W, fr.D, fr.H
    body = fr.rbox(0, 4, 0, W, D - 4, H, 12, "v")
    glass = fr.box(10, 0, 10, W - 20, 4, H - 20)
    keys = [fr.cyl_v(W * k, H * 0.3, 14, -0.5, 0.5) for k in (0.3, 0.7)]
    disp = fr.box(W * 0.2, -0.5, H * 0.55, W * 0.6, 1.0, H * 0.28)
    return [("panel", body, WHITE, 1.0), ("glass front", glass, BLACK, 1.0), ("touch key", keys[0], GREY, 1.0),
            ("touch key", keys[1], GREY, 1.0), ("display", disp, "#5dade2", 1.0)]


@product("shower_column")
def shower_column(fr, V, sp, b):
    """The hand shower on its slide rail with the hose, and the bypass mixer under it (WR-08)."""
    W, D, H = fr.W, fr.D, fr.H
    rail = fr.cyl_w(W / 2, D - 25, 11, 600, H - 40)
    brackets = [fr.box(W / 2 - 15, D - 25, w, 30, 25, 30) for w in (600, H - 70)]
    slider = fr.box(W / 2 - 22, D - 60, H - 380, 44, 36, 60)
    handle = fr.cyl((W / 2, D - 59, H - 350), (W / 2, 40, H - 330), 15)
    head = fr.cyl((W / 2, 45, H - 330), (W / 2, 15, H - 330), 55)
    mixer = fr.cyl_v(W / 2, 450, 35, D - 70, D)
    lever = fr.box(W / 2 - 8, D - 100, 440, 16, 31, 20)
    hose = fr.cyl((W / 2, D - 70, 420), (W / 2, D - 70, H - 360), 7)
    return [("slide rail", rail, CHROME, 1.0), ("rail bracket", brackets[0], CHROME, 1.0), ("rail bracket", brackets[1], CHROME, 1.0),
            ("slider", slider, CHROME, 1.0), ("hand shower handle", handle, CHROME, 1.0), ("hand shower head", head, CHROME, 1.0),
            ("bypass mixer", mixer, CHROME, 1.0), ("mixer lever", lever, CHROME, 1.0), ("hose", hose, GREY, 1.0)]


@product("floor_drain")
def floor_drain(fr, V, sp, b):
    """A round stainless drain grate let into the tray, with its 6 mm hair strainer under it."""
    W, D, H = fr.W, fr.D, fr.H
    r = min(W, D) / 2
    body = fr.cyl_w(W / 2, D / 2, r - 10, 0, H - 4)
    grate = fr.cyl_w(W / 2, D / 2, r, H - 4, H)
    return [("drain body", body, GREY, 1.0), ("grate", grate, STEEL, 1.0)]


@product("sand_grate")
def sand_grate(fr, V, sp, b):
    """The stainless linear grate over its lift-out sand basket, let into the tray inside the rear door."""
    W, D, H = fr.W, fr.D, fr.H
    basket = fr.box(10, 10, 0, W - 20, D - 20, H - 4) - fr.box(14, 14, 4, W - 28, D - 28, H)
    grate = fr.box(0, 0, H - 4, W, D, 4)
    for k in range(12):
        grate = grate - fr.box(k * (W - 16) / 12 + 10, 8, H - 5, 0.5 * (W - 16) / 12, D - 16, 6)
    return [("sand basket", basket, GREY, 1.0), ("linear grate", grate, STEEL, 1.0)]


@product("grey_tote")
def grey_tote(fr, V, sp, b):
    """A 40 L wheeled grey water tote with its handle, wheels, cap and hose, strapped in the corner (est. shape)."""
    W, D, H = fr.W, fr.D, fr.H
    body = fr.rbox(0, 0, 40, W, D, H - 120, 40, "w")
    out = [("tank", body, "#2c3e50", 1.0)]
    for u in (40.0, W - 100):
        out.append(("front foot", fr.box(u, 15, 0, 60, 40, 41), DARK, 1.0))
    for u in (40.0, W - 40.0):
        out.append(("wheel", fr.cyl((u - 25, D - 46, 45), (u + 25, D - 46, 45), 45), RUBBER, 1.0))
    out.append(("handle", fr.box(W / 2 - 60, D - 60, H - 81, 120, 40, 81), DARK, 1.0))
    out.append(("cap and camlock", fr.cyl_w(W / 2, 70, 30, H - 81, H - 40), "#f1c40f", 1.0))
    out.append(("strap to the wall", fr.box(0, D - 1, H - 260, W, 1, 30), BLACK, 1.0))
    return out


@product("partition_door")
def partition(fr, V, sp, b):
    """The 20 mm honeycomb partition, bonded to the tray, the walls and the ceiling, with the inner door's opening.
    Frame front -x, so u runs across the trailer from the road wall."""
    W, D, H = fr.W, fr.D, fr.H
    u0, u1, h = sp["door"]
    panel = fr.box(0, 0, 0, W, D, H) - fr.box(u0, -1, 0, u1 - u0, D + 2, h)
    return [("partition panel", panel, "#e8eaea", 1.0)]


@product("inner_door")
def inner_door(fr, V, sp, b):
    """The inner door: a 620 x 1,850 honeycomb leaf in an aluminium frame, hinged on its road-side edge, with a lever
    latch on both faces and a seal. Frame front -x, u from the road side."""
    W, H = fr.W, fr.H
    t0, t = sp.get("face", 30.0), sp.get("t", 20.0)      # the partition's living face and its thickness, in v
    frame = fr.box(0, t0, 0, W, t, H) - fr.box(25, t0 - 1, 0, W - 50, t + 2, H - 25)
    leaf = fr.box(26, t0 + 2, 1, W - 52, t - 4, H - 27)
    out = [("door frame", frame, ALU, 1.0), ("door leaf", leaf, "#d5dbdb", 1.0)]
    for w in (200.0, H - 300):
        out.append(("hinge", fr.box(20, t0 - 2, w, 12, t + 4, 90), STEEL, 1.0))
    for v0, nm in ((t0 - 27, "lever, living side"), (t0 + t - 3, "lever, wet room side")):
        out.append((nm, fr.box(W - 160, v0, 1000, 110, 30, 18), CHROME, 1.0))
    return out


@product("shower_well")
def shower_well(fr, V, sp, b):
    """The DauerShower's floor well under the shower drain: an insulated GRP shell let through the floor under the tray,
    the switching unit inside it, and the service panel underneath."""
    W, D, H = fr.W, fr.D, fr.H
    return [("insulated GRP well", fr.box(0, 0, 0, W, D, H) - fr.box(12, 12, 12, W - 24, D - 24, H), GRP, 1.0),
            ("switching unit", fr.box(50, 60, 12, W - 100, D - 120, 70), "#2c3e50", 1.0),
            ("service panel", fr.box(20, 20, 0, W - 40, D - 40, 4), GREY, 1.0)]

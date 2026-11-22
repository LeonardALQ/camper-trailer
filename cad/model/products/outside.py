"""Outside the body (research report 28 section 6): the Cruisemaster XT arms and the wheels, the drawbar box with the
two Honda EU22i and the jerry cans, the ARK jockey wheel and corner steadies, the lashing points, the spare wheel on
its carrier, the tanks, the solar panels and the awning's case."""
from __future__ import annotations

import math

from build123d import Plane, RectangleRounded, Solid, Vector, extrude

from . import ALU, BLACK, CHROME, DARK, GREY, RUBBER, STEEL, WHITE, product

GALV = "#a6acaf"
HONDA = "#c0392b"
HDPE = "#ecf0f1"


def _from_front(fr):
    """Box and cylinder makers whose u runs from the front of the trailer, on either side of it."""
    flip = fr.front == "+y"

    def bx(u0, v0, w0, du, dv, dw):
        return fr.box(fr.W - u0 - du if flip else u0, v0, w0, du, dv, dw)

    def cy(p, q, r):
        m = (lambda t: (fr.W - t[0], t[1], t[2])) if flip else (lambda t: t)
        return fr.cyl(m(p), m(q), r)
    return bx, cy, (lambda u: fr.W - u) if flip else (lambda u: u)


@product("xt_arm")
def xt_arm(fr, V, sp, b):
    """One Cruisemaster XT Freestyle trailing arm between the rail and the wheel: the pivot hanger welded to the rail's
    outer face, the arm down to the stub axle, the shock to its bracket on the rail, and the LC5 hub on the 12 inch
    electric drum. `hub` and `hub_w` place the hub centre in the envelope, `top` is the rail's underside and `slot` the
    clear width between the rail and the tyre. The airbag stands under the outrigger inside the tyre's envelope and is
    not shown."""
    bx, cy, mu = _from_front(fr)
    D, H = fr.D, fr.H
    hu, hw, top, slot = sp["hub"], sp["hub_w"], sp["top"], sp["slot"]
    pw = top - 110                                  # the pivot, 110 mm under the rail
    profile = [(mu(55), pw + 40), (mu(hu + 30), hw + 45), (mu(hu + 30), hw - 45), (mu(55), pw - 40)]
    return [("pivot hanger", bx(0, 0, pw - 40, 110, 12, H - pw + 40), GALV, 1.0),
            ("pivot bush", cy((55, 12, pw), (55, slot - 2, pw), 30), BLACK, 1.0),
            ("trailing arm", fr.prism_uw(profile, 14, slot - 4), "#7b7d7d", 1.0),
            ("shock bracket", bx(hu - 170, 0, top - 10, 80, 12, H - top + 10), GALV, 1.0),
            ("shock absorber", cy((hu - 130, slot / 2, top - 10), (hu - 40, slot / 2, hw + 40), 22), "#f1c40f", 1.0),
            ("stub axle", cy((hu, 14, hw), (hu, D - 90, hw), 35), STEEL, 1.0)]


@product("xt_hub")
def xt_hub(fr, V, sp, b):
    """The arm's LC5 M14 hub on its 12 inch ABS-enabled electric drum, inside the wheel: the drum with its backing
    plate on the stub axle, and the hub flange the wheel bolts to on the tyre's centre plane."""
    W, D, H = fr.W, fr.D, fr.H
    return [("brake drum and backing plate", fr.cyl_v(W / 2, H / 2, min(W, H) / 2 - 2, 0, D - 20), DARK, 1.0),
            ("hub flange", fr.cyl_v(W / 2, H / 2, 95, D - 25, D), GREY, 1.0)]


@product("steel_wheel")
def wheel(fr, V, sp, b):
    """ROH Trak 2 16 x 7 ET 0 steel wheel: the rim with its flanges and the disc on the centre plane, with the 110 mm
    centre bore. `hub` says which side of the centre plane the hub is: the disc lies on the other side of it."""
    W, D, H = fr.W, fr.D, fr.H
    u, w = W / 2, H / 2
    rim = fr.cyl_v(u, w, 203, 8, D - 8) - fr.cyl_v(u, w, 197, 0, D)
    flanges = [fr.cyl_v(u, w, W / 2, v0, v0 + 8) - fr.cyl_v(u, w, 197, v0 - 1, v0 + 9) for v0 in (0.0, D - 8)]
    v0 = D / 2 - 8 if sp.get("hub") == "out" else D / 2
    disc = fr.cyl_v(u, w, 199, v0, v0 + 8) - fr.cyl_v(u, w, 55, v0 - 1, v0 + 9)
    return [("rim", rim, "#f4f6f6", 1.0), ("rim flange", flanges[0], "#f4f6f6", 1.0), ("rim flange", flanges[1], "#f4f6f6", 1.0),
            ("disc", disc, "#f4f6f6", 1.0)]


@product("tyre")
def tyre(fr, V, sp, b):
    """LT265/75R16 123/120 Yokohama Geolandar A/T G015: the tyre on the rim's bead seats, with its tread band."""
    W, D, H = fr.W, fr.D, fr.H
    u, w = W / 2, H / 2
    R = min(W, H) / 2
    return [("tyre", fr.cyl_v(u, w, R - 10, 0, D) - fr.cyl_v(u, w, 202, -1, D + 1), RUBBER, 1.0),
            ("tread", fr.cyl_v(u, w, R, 25, D - 25) - fr.cyl_v(u, w, R - 11, 24, D - 24), "#17202a", 1.0)]


@product("spare_carrier")
def spare_carrier(fr, V, sp, b):
    """The spare's carrier on the two posts: a 6 mm hub plate at the wheel's mounting face, two 6 mm cleats from it back
    to the posts, and five M14 studs on the 5 x 150 circle through the wheel's disc. Frame front -x: v runs to the wall,
    `studs` is the hub plate's front face and `cleat_u` the cleats' offset from the centre."""
    W, D, H = fr.W, fr.D, fr.H
    s, c = sp["studs"], sp["cleat_u"]
    out = [("hub plate", fr.box(W / 2 - 100, s, H / 2 - 100, 200, 6, 200), GALV, 1.0)]
    for u0 in (W / 2 - c - 3, W / 2 + c - 3):
        out.append(("cleat", fr.box(u0, s + 6, H / 2 - 100, 6, D - s - 6, 200), GALV, 1.0))
    for k in range(5):
        a = 2 * math.pi * k / 5
        out.append(("wheel stud and nut", fr.cyl_v(W / 2 + 75 * math.cos(a), H / 2 + 75 * math.sin(a), 9, 0, s + 6), CHROME, 1.0))
    return out


@product("ark_xo750")
def jockey(fr, V, sp, b):
    """ARK XO750 jockey wheel swung up for travel: the swivel clamp bolted to its bracket plate, the post along the
    drawbar with the crank at its back end, and the twin wheels forward (ARK). Frame front +y: v runs outboard."""
    W, D, H = fr.W, fr.D, fr.H
    w = H / 2
    return [("swivel clamp", fr.box(20, 0, w - 60, 120, 14, 120), GALV, 1.0),
            ("clamp body", fr.box(30, 14, w - 45, 100, 40, 90), GALV, 1.0),
            ("post", fr.cyl_u(D / 2 + 10, w, 32, 10, W - 180), "#7f8c8d", 1.0),
            ("crank", fr.box(0, D / 2 - 10, w - 15, 15, 40, 140), BLACK, 1.0),
            ("fork", fr.box(W - 200, 30, w - 40, 60, D - 30, 80), "#7f8c8d", 1.0),
            ("wheel", fr.cyl((W - 100, 30, w), (W - 100, 70, w), 99), RUBBER, 1.0),
            ("wheel", fr.cyl((W - 100, D - 40, w), (W - 100, D, w), 99), RUBBER, 1.0),
            ("axle", fr.cyl((W - 100, 30, w), (W - 100, D, w), 10), STEEL, 1.0)]


@product("ark_steady")
def steady(fr, V, sp, b):
    """ARK XO DDS650 drop-down corner steady, wound up for travel: the top plate bolted under the rail and to its
    bracket, the outer leg, the wind-down nut and the foot pad (ARK)."""
    W, D, H = fr.W, fr.D, fr.H
    return [("top plate", fr.box(0, 0, H - 8, W, D, 8), GALV, 1.0),
            ("outer leg", fr.box(W / 2 - 30, D / 2 - 30, 10, 60, 60, H - 18), GALV, 1.0),
            ("wind-down nut", fr.cyl_w(W / 2, D / 2, 18, H - 30, H - 8), STEEL, 1.0),
            ("foot pad", fr.box(W / 2 - 55, 0, 0, 110, D, 10), GALV, 1.0)]


@product("d_ring")
def d_ring(fr, V, sp, b):
    """A forged 1/2 in weld-on D-ring: its clip welded under the outrigger's end and the ring hanging from it."""
    W, D, H = fr.W, fr.D, fr.H
    clip = fr.box(5, 5, H - 6, W - 10, D - 10, 6) + fr.box(5, D / 2 - 4, H - 20, W - 10, 8, 14)
    ring = fr.box(0, D / 2 - 6, 0, W, 12, H - 18) - fr.box(12, D / 2 - 7, 12, W - 24, 14, H - 32)
    return [("weld-on clip", clip, GALV, 1.0), ("D-ring", ring, GALV, 1.0)]


@product("drawbar_box")
def drawbar_box(fr, V, sp, b):
    """The sealed 1.6 mm aluminium drawbar box on its brackets across the drawbar members, its lockable lid, and the
    shelf over the generators on angles along the front and back walls. `shelf` is the shelf's top from the box's base."""
    W, D, H = fr.W, fr.D, fr.H
    t, sh = 1.6, sp["shelf"]
    out = [("box", fr.box(0, 0, 0, W, D, H - t) - fr.box(t, t, t, W - 2 * t, D - 2 * t, H), ALU, 0.45),
           ("lid", fr.box(0, 0, H - t, W, D, t), ALU, 0.45),
           ("lid hinge", fr.box(W - 20, 50, H - t - 20, 20, D - 100, 20), STEEL, 1.0),
           ("latch", fr.box(0, D / 2 - 40, H - 80, 3, 80, 60), BLACK, 1.0),
           ("shelf", fr.box(t + 3, t, sh - 3, W - 2 * t - 6, D - 2 * t, 3), ALU, 1.0)]
    for u0, leg in ((t, t), (W - t - 20, W - t - 3)):
        angle = fr.box(u0, t, sh - 23, 20, D - 2 * t, 3) + fr.box(leg, t, sh - 23, 3, D - 2 * t, 20)
        out.append(("shelf angle", angle, ALU, 1.0))
    return out


@product("honda_eu22i")
def eu22i(fr, V, sp, b):
    """Two Honda EU22i side by side, each 509 long, 290 wide and 425 high (Honda): the red casing on its rubber feet,
    the carry handle along the top, the fuel cap, and the control panel at the outer end."""
    W, D, H = fr.W, fr.D, fr.H
    L = 509.0
    out = []
    for k, v0 in enumerate((0.0, D - L)):
        out.append(("casing", fr.rbox(0, v0, 10, W, L, H - 70, 45, "u"), HONDA, 1.0))
        for v in (v0 + 60, v0 + L - 60):
            out.append(("rubber foot", fr.box(30, v - 25, 0, W - 60, 50, 10), RUBBER, 1.0))
            out.append(("handle post", fr.box(W / 2 - 20, v - 15, H - 60, 40, 30, 35), BLACK, 1.0))
        out.append(("carry handle", fr.box(W / 2 - 20, v0 + 45, H - 25, 40, L - 90, 25), BLACK, 1.0))
        out.append(("fuel cap", fr.cyl_w(W / 2 + 70, v0 + L * 0.35, 30, H - 60, H - 45), BLACK, 1.0))
        out.append(("control panel", fr.box(40, v0 if k == 0 else D - 2, 80, W - 80, 2, 200), "#2c3e50", 1.0))
    return out


@product("jerry_cans")
def jerry_cans(fr, V, sp, b):
    """Two 10 L jerry cans standing side by side, petrol in red and diesel in yellow, with their handles and caps,
    and the strap that holds them beside the generators."""
    W, D, H = fr.W, fr.D, fr.H
    out = []
    for k, (col, fuel) in enumerate((("#c0392b", "petrol"), ("#f1c40f", "diesel"))):
        v0 = k * D / 2
        out.append((f"{fuel} can", fr.rbox(0, v0 + 5, 0, W, D / 2 - 10, H - 60, 20, "v"), col, 1.0))
        out.append((f"{fuel} can handle", fr.box(W * 0.3, v0 + D / 4 - 15, H - 60, W * 0.4, 30, 50), col, 1.0))
        out.append((f"{fuel} can cap", fr.cyl_w(W - 50, v0 + D / 4, 22, H - 60, H - 20), BLACK, 1.0))
    out.append(("strap", fr.box(0, 5, H / 2, 2, D - 10, 40), BLACK, 1.0))
    return out


@product("hdpe_tank")
def tank(fr, V, sp, b):
    """A welded HDPE tank with `wall` mm walls, its outlet fitting and two padded stainless straps over its top."""
    W, D, H = fr.W, fr.D, fr.H
    t = sp.get("wall", 6.0)
    out = [("tank", fr.box(0, 0, 0, W, D, H) - fr.box(t, t, t, W - 2 * t, D - 2 * t, H - 2 * t), HDPE, 0.9),
           ("outlet fitting", fr.cyl_v(W - 60, 40, 20, 0, t), GREY, 1.0)]
    for u0 in (W * 0.2, W * 0.8 - 40):
        out.append(("strap", fr.box(u0, 0, H - 2, 40, D, 2), STEEL, 1.0))
    return out


@product("tank_cradle")
def tank_cradle(fr, V, sp, b):
    """The diesel tank's cradle: two 25 x 25 x 3 aluminium angles across the bay, their ends bolted to the raisers' inner
    faces, with a 3 mm rubber strip under the tank on each. `at` gives each angle's u and `tank` the tank's v range."""
    W, D, H = fr.W, fr.D, fr.H
    v0, v1 = sp["tank"]
    out = []
    for u0 in sp["at"]:
        angle = fr.box(u0, 0, H - 6, 25, D, 3) + fr.box(u0, 0, 0, 3, D, H - 3)
        out.append(("angle bearer", angle, ALU, 1.0))
        out.append(("rubber strip", fr.box(u0, v0, H - 3, 25, v1 - v0, 3), RUBBER, 1.0))
    return out


@product("jockey_spacers")
def jockey_spacers(fr, V, sp, b):
    """Four zinc-plated spacer tubes on M12 bolts between the jockey's bracket plate and the angled drawbar member, each
    from the plate's inner face to 3 mm inside the member's outer face. `face` is two points of that face in plan."""
    (xa, ya), (xb, yb) = sp["face"]
    out = []
    for x in sp["xs"]:
        y_face = ya + (yb - ya) * (x - xa) / (xb - xa)
        for z in sp["zs"]:
            p, q = Vector(x, sp["plate"], z), Vector(x, y_face + 3, z)
            out.append(("spacer tube on its bolt", Solid.make_cylinder(12.5, (q - p).length, Plane(origin=p, z_dir=q - p)), CHROME, 1.0))
    return out


@product("solar_panel")
def solar(fr, V, sp, b):
    """Sunman eArc SMF430F, 2,054 x 1,084 x 2 mm, glass-free and frameless, bonded to the roof: the dark cell laminate
    inside its clear border."""
    W, D, H = fr.W, fr.D, fr.H
    return [("laminate border", fr.box(0, 0, 0, W, D, H) - fr.box(15, 15, -1, W - 30, D - 30, H + 2), "#d6eaf8", 1.0),
            ("cells", fr.box(15, 15, 0, W - 30, D - 30, H), "#1b2631", 1.0)]


@product("awning_case")
def awning(fr, V, sp, b):
    """Fiamma F80s 400 case, 153 x 113 mm in section on its brackets (Fiamma): the rounded aluminium case, its black end
    caps, and five brackets bolted through the roof's insert strip. Frame front -y: u runs along the case."""
    W, D, H = fr.W, fr.D, fr.H
    bh = 20.0
    pl = Plane(origin=fr.pt(30, D / 2, bh + (H - bh) / 2), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    out = [("awning case", extrude(pl * RectangleRounded(D, H - bh, 30), amount=W - 60), WHITE, 1.0)]
    for u0 in (0.0, W - 30):
        out.append(("end cap", fr.box(u0, 0, bh, 30, D, H - bh), BLACK, 1.0))
    for k in range(5):
        out.append(("bracket", fr.box(200 + k * (W - 400) / 4 - 25, 20, 0, 50, D - 40, bh + 5), ALU, 1.0))
    return out

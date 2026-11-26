"""Outside the body (research report 28 section 6): the Cruisemaster XT arms and the wheels, the drawbar box with the
two Honda EU22i and the jerry cans, the ARK jockey wheel and corner steadies, the lashing points, the spare wheel on
its carrier, the tanks, the solar panels and the awning's case."""
from __future__ import annotations

import math

from build123d import Keep, Plane, RectangleRounded, Solid, Vector, extrude, split

from . import ALU, BLACK, CHROME, DARK, GREY, RUBBER, STEEL, WHITE, Frame, product

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


def _world(fr):
    """Box and cylinder makers in the model's own coordinates (x, y, z), for parts placed from the chassis data."""
    z0 = fr.bx[2]

    def wbox(q):
        (ua, va), (ub, vb) = fr.uv(q[0], q[1]), fr.uv(q[3], q[4])
        return fr.box(ua, va, q[2] - z0, ub - ua, vb - va, q[5] - q[2])

    def wcyl(p, q, r):
        return fr.cyl((*fr.uv(p[0], p[1]), p[2] - z0), (*fr.uv(q[0], q[1]), q[2] - z0), r)
    return wbox, wcyl


def _wcone(fr, p, q, r0, r1):
    """A cone from r0 at the point p to r1 at q, both in the model's own coordinates (x, y, z)."""
    z0 = fr.bx[2]
    a, c = Vector(*fr.pt(*fr.uv(p[0], p[1]), p[2] - z0)), Vector(*fr.pt(*fr.uv(q[0], q[1]), q[2] - z0))
    return Solid.make_cone(r0, r1, (c - a).length, Plane(origin=a, z_dir=c - a))


@product("xt_arm")
def xt_arm(fr, V, sp, b):
    """One Cruisemaster XT Freestyle arm's stub axle, in the slot between the rail and the wheel. `hub` and `hub_w`
    place the hub centre in the envelope. The arm itself, the A-frame from its pivot tube back to the hub that sheet 4
    draws, is xt_kit's with the kit's other parts."""
    _, cy, mu = _from_front(fr)
    hu, hw = sp["hub"], sp["hub_w"]
    return [("stub axle", cy((hu, 14, hw), (hu, fr.D - 90, hw), 35), STEEL, 1.0)]


@product("xt_kit")
def xt_kit(fr, V, sp, b):
    """One XT arm's parts between the rails at their places in Cruisemaster's 33XT AIR sheets 2 to 4 (Chassis.xt_parts,
    est.), which its line carries: the hinge bar under its crossmember with the arm's four hinge plates, its pivot tube
    and the A-frame's two legs from the bushes back to the hub at ride (Chassis.arm_bars), the airbag at ride under its
    top bracket 33SA 013 on the rail's inner face, and the shock absorber at ride from its eye on the arm to its bracket
    on the next crossmember."""
    wbox, wcyl = _world(fr)
    out = []
    for p in (b.extra.get("xt") or []) if b is not None else []:
        kind = p["id"].rsplit("-", 1)[0]
        if kind == "XT-BAR":
            out.append(("hinge bar", wbox(p["boxes"][0]), GALV, 1.0))
        elif kind == "XT-HINGE":
            out += [("hinge plate", wbox(q), GALV, 1.0) for q in p["plates"]]
            out.append(("pivot tube and bushes", wcyl(*p["tube"], 32), BLACK, 1.0))
            out += [("arm's leg from its bush back to the hub", _wcone(fr, *leg), "#7b7d7d", 1.0) for leg in p["legs"]]
        elif kind == "XT-BAG":
            (cx, cy), (za, zb) = p["centre"], p["z"]
            out.append(("airbag", wcyl((cx, cy, za), (cx, cy, zb), p["d"] / 2), BLACK, 1.0))
        elif kind == "XT-BAGBKT":
            out.append(("airbag top bracket", wbox(p["boxes"][0]), GALV, 1.0))
        elif kind == "XT-SHKBKT":
            out.append(("shock bracket", wbox(p["boxes"][0]), GALV, 1.0))
        elif kind == "XT-SHOCK":
            out.append(("shock absorber", wcyl(*p["line"], p["d"] / 2), "#f1c40f", 1.0))
    return out


@product("xt_hub")
def xt_hub(fr, V, sp, b):
    """The arm's LC5 M14 hub on its 12 inch ABS-enabled electric drum, inside the wheel: the drum with its backing
    plate on the stub axle, and the hub flange the wheel bolts to on the tyre's centre plane."""
    W, D, H = fr.W, fr.D, fr.H
    return [("brake drum and backing plate", fr.cyl_v(W / 2, H / 2, min(W, H) / 2 - 2, 0, D - 20), DARK, 1.0),
            ("hub flange", fr.cyl_v(W / 2, H / 2, 95, D - 25, D), GREY, 1.0)]


@product("steel_wheel")
def wheel(fr, V, sp, b):
    """ROH Trak 2 16 x 7 ET 0 steel wheel: the rim with its flanges and the disc against the centre plane, with the
    110 mm centre bore. `hub_side` says which side of the centre plane, low or high v, the hub or the carrier's hub plate
    is: the disc lies on the other side, its mounting face on the centre plane."""
    W, D, H = fr.W, fr.D, fr.H
    u, w = W / 2, H / 2
    rim = fr.cyl_v(u, w, 203, 8, D - 8) - fr.cyl_v(u, w, 197, 0, D)
    flanges = [fr.cyl_v(u, w, W / 2, v0, v0 + 8) - fr.cyl_v(u, w, 197, v0 - 1, v0 + 9) for v0 in (0.0, D - 8)]
    v0 = D / 2 - 8 if sp.get("hub_side") == "high" else D / 2
    disc = fr.cyl_v(u, w, 199, v0, v0 + 8) - fr.cyl_v(u, w, 55, v0 - 1, v0 + 9)
    return [("rim", rim, "#f4f6f6", 1.0), ("rim flange", flanges[0], "#f4f6f6", 1.0), ("rim flange", flanges[1], "#f4f6f6", 1.0),
            ("disc", disc, "#f4f6f6", 1.0)]


@product("tyre")
def tyre(fr, V, sp, b):
    """LT265/75R16 123/120 Yokohama Geolandar A/T G015: the tyre on the rim's bead seats, with its tread band."""
    W, D, H = fr.W, fr.D, fr.H
    u, w = W / 2, H / 2
    R = min(W, H) / 2
    return [("tyre", fr.cyl_v(u, w, R - 10, 0, D) - fr.cyl_v(u, w, 202.5, -1, D + 1), RUBBER, 1.0),
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
            ("crank", fr.box(0, D / 2 - 10, w - 70, 15, 40, 140), BLACK, 1.0),
            ("fork", fr.box(W - 200, 30, w - 40, 60, D - 30, 80), "#7f8c8d", 1.0),
            ("wheel", fr.cyl((W - 100, 30, w), (W - 100, 70, w), 99), RUBBER, 1.0),
            ("wheel", fr.cyl((W - 100, D - 40, w), (W - 100, D, w), 99), RUBBER, 1.0),
            ("axle", fr.cyl((W - 100, 30, w), (W - 100, D, w), 10), STEEL, 1.0)]


STEADY_BRACKET = 117.0      # ARK's chassis mount bracket along the fold (data/chassis/chassis.yaml `steadies`)


def _steady_frame(fr):
    """The folded steady's frame: u along the fold from the bracket's end, v across, w up. The envelope's long side is
    the fold. A fold across the trailer has its bracket at the outboard end, a fold along it at the rear end, as
    data/chassis/chassis.yaml places the pairs (the front pair folds inboard, the rear pair forward)."""
    x0, y0, _, x1, y1, _ = fr.bx
    if x1 - x0 >= y1 - y0:
        return Frame(fr.bx, "+y")                       # u runs forward from the rear end
    return Frame(fr.bx, "+x" if y0 + y1 < 0 else "-x")  # u runs inboard from the outer end


@product("ark_steady")
def steady(fr, V, sp, b):
    """ARK XO DDS650 drop-down corner steady folded flat at 0 degrees for travel (ARK's XO fitting guide, RTC614 V1
    1/21): ARK's chassis mount bracket welded under the rail, the head and its locking handle in the bracket on two
    8 mm bolts at 78 mm centres, the 19 mm hex drive, the outer and inner legs along the fold and the foot plate at the
    leg's end."""
    f = _steady_frame(fr)
    W, D, H = f.W, f.D, f.H
    L, c = STEADY_BRACKET, D / 2
    bracket = f.box(0, 0, H - 35, L, D, 35) - f.box(-1, 5, H - 36, L + 2, D - 10, 31)
    out = [("chassis mount bracket, welded under the rail", bracket, GALV, 1.0),
           ("head", f.box(12, 5, H - 95, L - 24, D - 10, 90), STEEL, 1.0),
           ("locking handle", f.box(L - 12, c - 10, H - 80, 20, 20, 20), BLACK, 1.0),
           ("hex drive, 19 mm", f.cyl_u(c, H - 65, 11, 1, 12), STEEL, 1.0),
           ("outer leg", f.box(L - 12, c - 30, H - 95, W - 160 - L, 60, 60), GALV, 1.0),
           ("inner leg", f.box(W - 172, c - 25, H - 90, 147, 50, 50), GALV, 1.0),
           ("foot plate", f.box(W - 25, 0, 0, 15, D, H - 30), GALV, 1.0)]
    for u in (L / 2 - 39, L / 2 + 39):
        out.append(("8 mm bolt", f.cyl_v(u, H - 20, 4, 0, D), CHROME, 1.0))
    return out


@product("ark_steady_use")
def steady_use(fr, V, sp, b):
    """The same steady locked at 90 degrees for use, wound down to the ground at design ride height: the outer leg
    hanging from the head, the inner leg out of it and the foot plate flat on the ground (ARK's guide: the rated and
    only jacking position). Drawn see-through beside the folded steady on the chassis model."""
    W, D, H = fr.W, fr.D, fr.H
    return [("outer leg at 90 degrees", fr.box(W / 2 - 30, D / 2 - 30, H - 365, 60, 60, 365), GALV, 0.35),
            ("inner leg at 90 degrees", fr.box(W / 2 - 25, D / 2 - 25, 15, 50, 50, H - 380), GALV, 0.35),
            ("foot plate on the ground", fr.box(0, 0, 0, W, D, 15), GALV, 0.35)]


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
    """A welded HDPE tank with `wall` mm walls, its outlet fitting and two padded stainless straps over its top. Its
    corners are notched round the chassis fittings that reach into its box (Layout.tank_notches): each notch cut from
    the outside, and grown by the wall, from the inside, so the pocket keeps the tank's walls."""
    W, D, H = fr.W, fr.D, fr.H
    t = sp.get("wall", 6.0)
    outer, inner = fr.box(0, 0, 0, W, D, H), fr.box(t, t, t, W - 2 * t, D - 2 * t, H - 2 * t)
    z0 = fr.bx[2]
    for nt in (b.extra.get("notches") or []) if b is not None else []:
        if nt.get("kind") == "box":                 # a pocket round one of the XT kit's parts (Layout._part_notches)
            for bx, grown in ((nt["box"], False), (nt["inner"], True)):
                (ua, va), (ub, vb) = fr.uv(bx[0], bx[1]), fr.uv(bx[3], bx[4])
                cut = fr.box(ua, va, bx[2] - z0, ub - ua, vb - va, bx[5] - bx[2])
                if grown:
                    inner = inner - cut
                else:
                    outer = outer - cut
            continue
        (cx, cy), (nx, ny) = nt["corner"], nt["normal"]
        for k, (za, zb), grown in ((nt["keep"], (nt["z0"], nt["z1"]), False), (nt["keep"] + t * 2 ** 0.5, nt["inner_z"], True)):
            prism = fr.prism_uv([fr.uv(cx, cy), fr.uv(cx + nx * k, cy), fr.uv(cx, cy + ny * k)], za - z0, zb - z0)
            if grown:
                inner = inner - prism
            else:
                outer = outer - prism
    def walled(u):                                  # the outlet's place on the front wall is not cut by a pocket
        x, y, z = fr.pt(u, t / 2, 40)
        return not any(nt.get("kind") == "box" and all(nt["inner"][i] - 20 <= (x, y, z)[i] <= nt["inner"][i + 3] + 20 for i in range(3))
                       for nt in ((b.extra.get("notches") or []) if b is not None else []))
    u_out = next((u for u in (W - 60, 60, W / 2) if walled(u)), W - 60)
    out = [("tank", outer - inner, HDPE, 0.9),
           ("outlet fitting", fr.cyl_v(u_out, 40, 20, 0, t), GREY, 1.0)]
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
        for v in (0.0, D - 3):              # the end cleats the bolts pass through into the raisers
            out.append(("end cleat", fr.box(u0 - 7.5, v, 0, 40, 3, H - 3), ALU, 1.0))
    return out


@product("tank_guard")
def tank_guard(fr, V, sp, b):
    """A tank guard plate between the rails, in pieces round the `gaps` (u ranges kept open), `half` wide either side of
    the envelope's centre (the envelope's own half width if not given). Frame front -y: u runs rearward along X. Where
    the line carries the rear bay's shear panel (Chassis.shear_panels, UF-03), the piece behind the last gap is the
    panel, which shear_panel draws."""
    W, D, H = fr.W, fr.D, fr.H
    half = sp.get("half", D / 2)
    cuts = [0.0] + [u for g in sorted(sp.get("gaps", [])) for u in g] + [W]
    pieces = list(zip(cuts[::2], cuts[1::2]))
    pn = (b.extra.get("panel") if b is not None else None)
    plates = [fr.box(u0, D / 2 - half, 0, u1 - u0, 2 * half, H) for u0, u1 in (pieces[:-1] if pn else pieces)]
    openings = (b.extra.get("openings") or []) if b is not None else []
    if openings and plates:                  # the front piece cut round the airbags and shocks over their travel (Layout.guard_openings)
        wbox, _ = _world(fr)
        z0 = fr.bx[2]
        plates[0] = plates[0].cut(*[wbox((x0, y0, z0 - 1, x1, y1, z0 + H + 1)) for x0, y0, x1, y1 in openings])
    return [("guard plate", p, ALU, 1.0) for p in plates]


@product("shear_panel")
def shear_panel(fr, V, sp, b):
    """The rear tank bay's shear panel as the chassis data cuts it, which the guards' line carries (Chassis.shear_panels):
    the galvanised sheet at the data's thickness and its tongues under the crossmembers' angles."""
    pn = (b.extra.get("panel") if b is not None else None)
    if not pn:
        return []
    wbox, _ = _world(fr)
    zt, zb = pn["z_top"], pn["z_top"] - pn["t"]
    sh = pn["sheet"]
    out = [("shear panel sheet", wbox((x0, y0, zb, x1, y1, zt)), GALV, 1.0) for x0, y0, x1, y1 in sh["parts"]]
    out += [("shear panel tongue", wbox((x0, y0, zb, x1, y1, zt)), GALV, 1.0) for x0, y0, x1, y1 in sh["tongues"]]
    return out


@product("guard_hangers")
def guard_hangers(fr, V, sp, b):
    """The 50 mm long aluminium angles a tank guard hangs on, a pair at each u station `at`: each angle's upright leg
    bolted to a rail's inner face, the envelope's side, and its foot `foot` mm long under the plate's edge at the
    envelope's base."""
    D, H, f = fr.D, fr.H, sp["foot"]
    out = []
    for u in sp["at"]:
        kerb = fr.box(u - 25, 0, 0, 50, 3, H) + fr.box(u - 25, 0, 0, 50, f, 3)
        road = fr.box(u - 25, D - 3, 0, 50, 3, H) + fr.box(u - 25, D - f, 0, 50, f, 3)
        out += [("hanger angle", kerb, ALU, 1.0), ("hanger angle", road, ALU, 1.0)]
    return out


@product("jockey_spacers")
def jockey_spacers(fr, V, sp, b):
    """Four zinc-plated spacer tubes on M12 bolts between the jockey's bracket plate and the angled drawbar member, each
    from the plate's inner face to the member's outer face, its end cut to the member's angle so it sits flat on the
    face. `face` is two points of that face in plan."""
    (xa, ya), (xb, yb) = sp["face"]
    along = Vector(xb - xa, yb - ya, 0).normalized()
    into = Vector(-along.Y, along.X, 0) if along.X > 0 else Vector(along.Y, -along.X, 0)   # from the plate to the member
    face = Plane(origin=(xa, ya, 0), x_dir=along, z_dir=-into)
    out = []
    for x in sp["xs"]:
        y_face = ya + (yb - ya) * (x - xa) / (xb - xa)
        for z in sp["zs"]:
            p, q = Vector(x, sp["plate"], z), Vector(x, y_face + 15, z)
            tube = Solid.make_cylinder(12.5, (q - p).length, Plane(origin=p, z_dir=q - p))
            out.append(("spacer tube on its bolt", split(tube, bisect_by=face, keep=Keep.TOP), CHROME, 1.0))
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

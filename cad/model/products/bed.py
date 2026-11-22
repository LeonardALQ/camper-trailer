"""The lift bed and the desk (research report 28 section 3): the Lippert HappiJac 42 in kit's rails, carriages,
support rails and drive, the honeycomb platform, the Pure Sleep mattress, the desk on its wall cleat and two legs,
and the two Helinox Cafe chairs at it."""
from __future__ import annotations

from . import ALU, BLACK, DARK, GREY, STEEL, product

FABRIC = "#34495e"


@product("happijac_rail")
def rail(fr, V, sp, b):
    """One HappiJac rail: a 50 x 20 steel C-channel screwed through the wall's inner skin into its hardpoint, open to
    the cabin, with the carriage inside it at the platform's height (Lippert's HappiJac manual)."""
    W, D, H = fr.W, fr.D, fr.H
    wc = sp["deck"] - fr.bx[2]                     # the platform's underside, from the rail's foot
    return [("rail web", fr.box(0, D - 3, 0, W, 3, H), STEEL, 1.0),
            ("rail flange", fr.box(0, 0, 0, 3, D - 3, H), STEEL, 1.0),
            ("rail flange", fr.box(W - 3, 0, 0, 3, D - 3, H), STEEL, 1.0),
            ("carriage", fr.box(4, 0, wc - 130, W - 8, D - 3, 170), DARK, 1.0)]


@product("happijac_support_rail")
def support_rail(fr, V, sp, b):
    """The kit's support rail along one wall: a 40 x 45 x 4 angle under the platform's edge from the front carriage to
    the rear one, bolted to each carriage through a tab out of the rail's open face."""
    W, D, H = fr.W, fr.D, fr.H
    out = [("support rail, top leg", fr.box(0, 0, H - 4, W, D, 4), STEEL, 1.0),
           ("support rail, wall leg", fr.box(0, D - 4, 0, W, 4, H - 4), STEEL, 1.0)]
    for u0 in (0.0, W - 50):
        out.append(("carriage tab", fr.box(u0 + 5, D - 4, 0, 40, 4, H - 4), DARK, 1.0))
    return out


@product("happijac_drive")
def drive(fr, V, sp, b):
    """The HappiJac drive under the ceiling: the 12 V gearmotor with its brake in the middle, the cross shaft to a corner
    gearbox at each wall, and along each wall the drive tube over the rails' tops that carries the chains to the
    carriages. The tubes are screwed to the ceiling."""
    W, D, H = fr.W, fr.D, fr.H
    ut = 40.0                                      # the drive tubes' depth off the rails
    m = sp["shaft_u"]
    out = []
    for v0 in (0.0, D - ut):
        out.append(("drive tube", fr.box(0, v0, H - 40, W, ut, 40), GREY, 1.0))
        out.append(("corner gearbox", fr.box(m - 40, v0, H - 70, 80, ut, 70), DARK, 1.0))
    out.append(("cross shaft", fr.cyl_v(m, H - 35, 13, ut, D - ut), STEEL, 1.0))
    out.append(("gearmotor", fr.box(m - 60, D / 2 - 90, H - 70, 120, 180, 70), BLACK, 1.0))
    out.append(("motor", fr.cyl_v(m, H - 36, 32, D / 2 - 230, D / 2 - 90), BLACK, 1.0))
    return out


@product("bed_platform")
def platform(fr, V, sp, b):
    """The platform: 40 mm aluminium honeycomb with 0.8 and 0.5 mm skins and a bonded aluminium edge channel, lying on
    the two support rails, with the rubber safety edge on its underside round the front and the ends."""
    W, D, H = fr.W, fr.D, fr.H
    core = fr.box(3, 3, 0, W - 6, D - 6, H)
    edge = fr.box(0, 0, 0, W, D, H) - fr.box(3, 3, -1, W - 6, D - 6, H + 2)
    return [("honeycomb panel", core, "#d6eaf8", 1.0), ("edge channel", edge, ALU, 1.0)]


@product("mattress")
def mattress(fr, V, sp, b):
    """Pure Sleep Orion Caravan Deluxe queen, 1,530 x 2,030 x 180 mm: a flat underside on the underlay, rounded top
    edges and the border's piping."""
    W, D, H = fr.W, fr.D, fr.H
    return [("mattress", fr.rbox(0, 0, 0, W, D, H - 30, 40, "w"), "#f8f9f9", 1.0),
            ("quilted top", fr.rbox(15, 15, H - 30, W - 30, D - 30, 30, 30, "w"), "#fdfefe", 1.0)]


@product("desk")
def desk(fr, V, sp, b):
    """The desk: a 25 mm aluminium honeycomb top with HPL facing, its back edge on an aluminium angle cleat screwed to
    the front wall, its front corners on two 40 mm square aluminium legs standing on the floor."""
    W, D, H = fr.W, fr.D, fr.H
    t = 25.0
    out = [("desk top", fr.box(0, 0, H - t, W, D, t), "#f2f3f4", 1.0),
           ("wall cleat", fr.box(0, D - 40, H - t - 40, W, 40, 40) - fr.box(-1, -1, H - t - 44, W + 2, D - 3, 40), ALU, 1.0)]
    for u0 in (20.0, W - 60):
        out.append(("leg", fr.box(u0, 20, 0, 40, 40, H - t), ALU, 1.0))
        out.append(("leg foot", fr.box(u0 - 5, 15, 0, 50, 50, 5), BLACK, 1.0))
    return out


@product("helinox_cafe")
def chairs(fr, V, sp, b):
    """Helinox Cafe Chair, 560 wide, 505 deep and 850 high assembled (Helinox): the aluminium pole frame on four feet
    and the polyester seat and back. `count` chairs stand side by side across the envelope."""
    n = int(sp.get("count", 1))
    W, D, H = fr.W, fr.D, fr.H
    cw = 560.0
    gap = (W - n * cw) / max(n - 1, 1)
    seat = 450.0
    out = []
    for k in range(n):
        u0 = k * (cw + gap)
        for u in (u0 + 40, u0 + cw - 40):
            for v, top in ((40.0, seat), (D - 40, H)):
                out.append(("foot", fr.cyl_w(u, v, 14, 0, 6), BLACK, 1.0))
                out.append(("frame pole", fr.cyl_w(u, v, 8, 0, top), GREY, 1.0))
        out.append(("seat", fr.box(u0 + 25, 25, seat - 30, cw - 50, D - 50, 30), FABRIC, 1.0))
        out.append(("back", fr.box(u0 + 25, D - 50, seat + 80, cw - 50, 20, H - seat - 100), FABRIC, 1.0))
    return out

"""Heating, cooling and fresh air (research report 28 section 5): the Mitsubishi Electric split's indoor and outdoor
units, the outdoor unit's cradle on its wire-rope isolators, and the LUNOS e2 60 and RA 15-60 fans."""
from __future__ import annotations

from . import ALU, DARK, GREY, STEEL, WHITE, product


@product("msz_ap25")
def indoor(fr, V, sp, b):
    """Mitsubishi Electric MSZ-AP25VGKD2, 798 wide, 299 high and 219 deep (Mitsubishi Electric): the white body with
    its rounded front, the front panel, the outlet's horizontal vane at the bottom, the display, and the installation
    plate it hangs on, screwed to the partition."""
    W, D, H = fr.W, fr.D, fr.H
    return [("installation plate", fr.box(40, D - 6, 40, W - 80, 6, H - 80), STEEL, 1.0),
            ("body", fr.rbox(0, 30, 0, W, D - 36, H, 40, "u"), WHITE, 1.0),
            ("front panel", fr.rbox(5, 0, 70, W - 10, 32, H - 75, 14, "u"), "#fbfcfc", 1.0),
            ("outlet vane", fr.box(40, 10, 10, W - 80, 30, 25), "#e5e8e8", 1.0),
            ("display", fr.box(W - 120, 0, 120, 70, 1.0, 15), "#2e86c1", 1.0)]


@product("muz_ap25")
def outdoor(fr, V, sp, b):
    """Mitsubishi Electric MUZ-AP25VGD2, 800 wide, 550 high and 285 deep (Mitsubishi Electric): the casing, the round
    fan grille on the left of the front, the service cover and valves on the right end, and the two feet the isolators
    hold."""
    W, D, H = fr.W, fr.D, fr.H
    grille = fr.cyl_v(W * 0.38, H * 0.53, H * 0.4, 0, 6) - fr.cyl_v(W * 0.38, H * 0.53, H * 0.4 - 8, -1, 7)
    out = [("feet", fr.box(30, 20, 0, W - 60, D - 40, 20), DARK, 1.0),
           ("casing", fr.box(0, 6, 20, W, D - 6, H - 20), "#f2f3f4", 1.0),
           ("fan grille ring", grille, DARK, 1.0),
           ("fan grille", fr.cyl_v(W * 0.38, H * 0.53, H * 0.4 - 8, 2, 6), "#7f8c8d", 0.8),
           ("service cover", fr.box(W - 170, 5, 60, 150, 1.0, 220), "#d5d8dc", 1.0)]
    for w in (90.0, 140.0):
        out.append(("service valve", fr.box(W - 60, 0, w, 40, 6, 25), "#b7950b", 1.0))
    return out


@product("split_cradle")
def cradle(fr, V, sp, b):
    """The vehicle mounting package: an aluminium cradle bolted to the rear wall and standing on its two stays, four
    stainless wire-rope isolators under the outdoor unit's feet, and the perforated guard round it. `iso` is the
    isolators' height under the unit and `unit` the unit's envelope inside the cradle, from the wall."""
    W, D, H = fr.W, fr.D, fr.H
    t = 5.0
    h = sp["iso"]
    u0, u1, v0, v1 = sp["unit"]
    out = [("back plate on the rear wall", fr.box(0, D - t, 0, W, t, H - 10), ALU, 1.0),
           ("cradle floor", fr.box(0, 0, 0, W, D - t, t), ALU, 1.0),
           ("cradle side", fr.box(0, 0, t, t, D - t, 60), ALU, 1.0),
           ("cradle side", fr.box(W - t, 0, t, t, D - t, 60), ALU, 1.0)]
    for u in (u0 + 60, u1 - 60):
        for v in (v0 + 45, v1 - 45):
            out.append(("wire-rope isolator", fr.box(u - 35, v - 25, t, 70, 50, h - t), STEEL, 1.0))
    guard = fr.box(0, 0, t, W, D - t, H - t) - fr.box(3, 3, t, W - 6, D - t + 1, H - t - 3)
    out.append(("perforated guard", guard, "#aab7b8", 0.25))
    return out


@product("lunos_e2")
def lunos_e2(fr, V, sp, b):
    """A LUNOS e2 60 short: the fan and its ceramic regenerator in a 160 mm sleeve let into the wall, and the square
    MERV 13 inner cover on the cabin side (LUNOS)."""
    W, D, H = fr.W, fr.D, fr.H
    return [("sleeve with the fan and regenerator", fr.cyl_v(W / 2, H / 2, 75, 25, D), "#bdc3c7", 1.0),
            ("inner cover", fr.rbox(0, 0, 0, W, 25, H, 15, "v"), WHITE, 1.0),
            ("cover filter", fr.box(25, 0, 25, W - 50, 1.0, H - 50), GREY, 1.0)]


@product("lunos_ra15")
def lunos_ra(fr, V, sp, b):
    """The LUNOS RA 15-60 radial extract fan in its 9/R 160 sleeve let into the rear wall, with its inner cover."""
    W, D, H = fr.W, fr.D, fr.H
    return [("sleeve with the fan", fr.cyl_v(W / 2, H / 2, 78, 20, D), "#bdc3c7", 1.0),
            ("inner cover", fr.cyl_v(W / 2, H / 2, min(W, H) / 2, 0, 20), WHITE, 1.0),
            ("cover slots", fr.box(W / 2 - 40, 0, H / 2 - 30, 80, 1.0, 60), GREY, 1.0)]

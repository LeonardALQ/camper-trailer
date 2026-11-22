"""The laundry and the plinth under it (research report 28 section 2): the Camec Compact RV II washer, the Haier
HDHPS70LW1 dryer, the machine base, the battery box with its five Victron modules, the end slot's cover and the
lockers over the machines."""
from __future__ import annotations

from . import ALU, BLACK, CHROME, DARK, GLASS, GREY, PLY, RUBBER, STEEL, WHITE, product

VICTRON = "#2f5d9e"


@product("camec_compact_rv2")
def washer(fr, V, sp, b):
    """Camec Compact RV II 051879, 3.5 kg top loader, 445 x 460 x 730 mm (Camec): a white cabinet, the lid with its
    drum window, the control console across the back of the top, four feet. Front faces the aisle."""
    W, D, H = fr.W, fr.D, fr.H
    feet = [fr.cyl_w(u, v, 18, 0, 12) for u in (40, W - 40) for v in (40, D - 40)]
    cab = fr.rbox(0, 0, 12, W, D, H - 12 - 110, 18, "w")
    console = fr.rbox(0, D - 130, H - 110, W, 130, 110, 12, "u")
    deck = fr.box(10, 10, H - 110, W - 20, D - 140, 8)
    lid = fr.rbox(20, 15, H - 102, W - 40, D - 165, 14, 25, "w")
    window = fr.box(70, 50, H - 89, W - 140, D - 260, 1.5)
    dial = fr.cyl((W - 90, D - 131, H - 55), (W - 90, D - 141, H - 55), 26)
    keys = fr.box(60, D - 131.5, H - 70, 180, 1.5, 30)
    out = [(f"foot", f, RUBBER, 1.0) for f in feet]
    out += [("cabinet", cab, WHITE, 1.0), ("control console", console, WHITE, 1.0), ("top deck", deck, "#e5e8e8", 1.0),
            ("lid", lid, "#d6eaf8", 0.8), ("drum window", window, GLASS, 0.6), ("programme dial", dial, GREY, 1.0),
            ("control keys and display", keys, DARK, 1.0)]
    return out


@product("haier_hdhps70")
def dryer(fr, V, sp, b):
    """Haier HDHPS70LW1, 7 kg heat-pump dryer, 595 wide, 590 deep and 850 high (Haier): the round door with its
    tinted window and chrome ring, the control strip with the programme dial, the water tank drawer, adjustable feet."""
    W, D, H = fr.W, fr.D, fr.H
    feet = [fr.cyl_w(u, v, 20, 0, 15) for u in (45, W - 45) for v in (45, D - 45)]
    cab = fr.rbox(0, 2, 15, W, D - 2, H - 15, 10, "w")
    strip = fr.box(0, 0, H - 120, W, 2, 120)
    drawer = fr.box(25, -0.5, H - 100, 180, 2, 70)
    dial = fr.cyl_v(W - 170, H - 60, 30, -0.9, 2)
    disp = fr.box(W / 2 - 70, -0.5, H - 85, 110, 2, 40)
    wc = H - 120 - 330
    ring = fr.cyl_v(W / 2, wc, 205, -0.9, 2) - fr.cyl_v(W / 2, wc, 165, -1, 3)
    glass = fr.cyl_v(W / 2, wc, 166, -0.5, 2)
    handle = fr.box(W / 2 + 150, -0.9, wc - 40, 30, 2, 80)
    kick = fr.box(20, 1, 15, W - 40, 2, 60)
    out = [("foot", f, GREY, 1.0) for f in feet]
    out += [("cabinet", cab, WHITE, 1.0), ("control strip", strip, WHITE, 1.0), ("water tank drawer", drawer, "#e5e8e8", 1.0),
            ("programme dial", dial, CHROME, 1.0), ("display", disp, BLACK, 1.0), ("door ring", ring, CHROME, 1.0),
            ("door window", glass, "#34495e", 0.85), ("door handle", handle, GREY, 1.0), ("plinth panel", kick, "#e5e8e8", 1.0)]
    return out


@product("machine_base")
def machine_base(fr, V, sp, b):
    """The machine base: a 40 mm aluminium angle frame over the battery box and the end slot, with rubber isolator
    pads under each machine's feet and the ratchet straps' anchor rails."""
    W, D, H = fr.W, fr.D, fr.H
    t, deck = 3.0, 4.0
    out = []
    for v0, vl in ((0.0, 0.0), (D - 40, D - t)):
        out.append(("frame rail, 40 x 40 x 3 angle", fr.box(0, v0, 0, W, 40, t) + fr.box(0, vl, 0, W, t, H - deck - 3), ALU, 1.0))
    for u0 in (0.0, W / 2 - 20, W - 40):
        out.append(("cross member, 40 x 40 x 3 angle", fr.box(u0, 40, 0, 40, D - 80, t), ALU, 1.0))
    n = 5
    for k in range(n):
        u = 30 + k * (W - 60) / (n - 1)
        for v in (20.0, D - 20):
            out.append(("rubber isolator", fr.cyl_w(u, v, 15, t, H - deck), RUBBER, 1.0))
    out.append(("deck, 4 mm tread plate", fr.box(0, 0, H - deck, W, D, deck), "#bdc3c7", 1.0))
    return out


@product("battery_box")
def battery_box(fr, V, sp, b):
    """The sealed 2 mm 5052 battery box: walls lined with 3 mm ceramic-fibre paper, the tray with rubber pads, the
    bolted gasketed front panel, cable glands at the end and the two vent spigots through the floor (AS/NZS 3001.2)."""
    W, D, H = fr.W, fr.D, fr.H
    shell = fr.box(0, 0, 0, W, D, H) - fr.box(2, 2, 2, W - 4, D - 4, H)
    lining = fr.box(2, 2, 2, W - 4, D - 4, H - 2) - fr.box(5, 5, 5, W - 10, D - 10, H)
    tray = fr.box(10, 10, 5, W - 20, D - 20, 3) + fr.box(10, 10, 5, 3, D - 20, 40) + fr.box(W - 13, 10, 5, 3, D - 20, 40)
    pads = fr.box(20, 30, 8, W - 40, D - 60, 12)
    front = fr.box(4, 0, 4, W - 8, 1.0, H - 8)
    out = [("box shell", shell, ALU, 1.0), ("ceramic-fibre lining", lining, "#f2f3f4", 1.0), ("tray", tray, ALU, 1.0),
           ("tray pads", pads, RUBBER, 1.0), ("gasketed front panel", front, "#b3b6b7", 1.0)]
    for k in range(4):
        out.append(("panel bolt", fr.cyl_v(30 + k * (W - 60) / 3, H - 20, 6, -0.9, 0.5), STEEL, 1.0))
    for w in (H * 0.35, H * 0.65):
        out.append(("cable gland", fr.cyl((W - 1, D * 0.3, w), (W + 0.9, D * 0.3, w), 14), BLACK, 1.0))
    return out


@product("victron_lithium_ng")
def battery_modules(fr, V, sp, b):
    """Five Victron Lithium NG 51.2 V 100 Ah modules, 235 x 648 x 162 mm each (Victron), side by side 10 mm apart,
    terminals up, with the BMS cables and the hold-down straps. Frame front -y... the modules stand along u."""
    W, D, H = fr.W, fr.D, fr.H
    n, w = 5, 162.0
    gap = (W - n * w) / (n - 1)
    out = []
    for k in range(n):
        u0 = k * (w + gap)
        out.append(("module case", fr.rbox(u0, 0, 0, w, D, H - 12, 6, "w"), VICTRON, 1.0))
        out.append(("module lid", fr.box(u0 + 4, 4, H - 12, w - 8, D - 8, 4), DARK, 1.0))
        for v, col, nm in ((90, "#c0392b", "positive terminal cover"), (D - 90, BLACK, "negative terminal cover")):
            out.append((nm, fr.cyl_w(u0 + w / 2, v, 16, H - 8, H), col, 1.0))
        out.append(("handle", fr.box(u0 + 30, D / 2 - 60, H - 8, w - 60, 120, 6), BLACK, 1.0))
    out.append(("hold-down strap", fr.box(0, D * 0.25, H - 8, W, 25, 2), BLACK, 1.0))
    out.append(("hold-down strap", fr.box(0, D * 0.75 - 25, H - 8, W, 25, 2), BLACK, 1.0))
    return out


@product("slot_cover")
def slot_cover(fr, V, sp, b):
    """The end slot's cover in 18 mm ply: the aisle face and the end panel by the partition, standing on the floor
    and carrying the machine base's end over the slot. Frame front +y: u runs from the partition end."""
    W, D, H = fr.W, fr.D, fr.H
    t = 18.0
    return [("aisle face panel", fr.box(0, 0, 0, W, t, H), PLY, 1.0),
            ("end panel", fr.box(0, t, 0, t, D - t, H), PLY, 1.0),
            ("finger pull", fr.box(W / 2 - 40, -0.9, H - 60, 80, 1.0, 20), DARK, 1.0)]


@product("overhead_lockers")
def lockers(fr, V, sp, b):
    """Overhead lockers in 18 mm Garnica Ultralight ply with lift-up doors on gas stays and push latches, screwed
    through a back rail into the wall's insert strip."""
    W, D, H = fr.W, fr.D, fr.H
    t = 18.0
    n = int(sp.get("doors", 2))
    out = [("carcass", fr.box(0, 0, 0, W, D, H) - fr.box(t, -1, t, W - 2 * t, D - t + 1, H - 2 * t), PLY, 1.0),
           ("back rail", fr.box(t, D - t - 20, H - t - 60, W - 2 * t, 20, 60), "#c8b28a", 1.0),
           ("shelf", fr.box(t, t, H / 2 - t / 2, W - 2 * t, D - 2 * t, t), PLY, 1.0)]
    dw = (W - 2 * t - 3.0 * (n - 1)) / n
    for k in range(n):
        u0 = t + k * (dw + 3.0)
        out.append(("lift-up door", fr.box(u0, 0, t + 1, dw, t, H - 2 * t - 2), "#ecd9b6", 1.0))
        out.append(("push latch", fr.cyl_v(u0 + dw / 2, H - t - 40, 12, -0.9, 0.5), CHROME, 1.0))
    return out

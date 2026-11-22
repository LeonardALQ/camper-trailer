"""The 48 V system's products (research report 28 section 5): the MultiPlus-II on its wall bracket, the board cabinet
on the partition and the Victron gear on its back board, and the GX Touch 50 on the cabinet's door."""
from __future__ import annotations

from . import BLACK, DARK, GREY, PLY, STEEL, WHITE, product

VICTRON, VGREY = "#2f5d9e", "#d0d3d4"
# each unit's size on the board: width along the board, height, depth off the board (mm, Victron's datasheets, est.)
UNITS = {
    "lynx": (180.0, 190.0, 80.0, "Lynx module"),
    "mppt": (130.0, 186.0, 70.0, "SmartSolar MPPT 150/35"),
    "orion": (130.0, 186.0, 80.0, "Orion-Tr isolated converter"),
    "cerbo": (154.0, 78.0, 48.0, "Cerbo GX MK2"),
    "board": (330.0, 190.0, 110.0, "230 V board, DIN enclosure"),
}


@product("multiplus_ii")
def multiplus(fr, V, sp, b):
    """Victron MultiPlus-II 48/6k5 on its wall bracket, front to the kitchen: the blue cover, the grey lower cable
    compartment, the vent slots and the bracket screwed to the partition. Frame front -x."""
    W, D, H = fr.W, fr.D, fr.H
    bracket = fr.box(30, D - 6, H - 160, W - 60, 6, 120)
    body = fr.rbox(0, 0, 0, W, D - 6, H, 10, "v")
    cover = fr.box(8, -0.9, H * 0.3, W - 16, 1.0, H * 0.66)
    lower = fr.box(8, -0.9, 10, W - 16, 1.0, H * 0.27)
    out = [("wall bracket", bracket, STEEL, 1.0), ("housing", body, VGREY, 1.0), ("front cover", cover, VICTRON, 1.0),
           ("cable compartment cover", lower, GREY, 1.0)]
    for k in range(4):
        out.append(("cable gland", fr.cyl_w(40 + k * (W - 80) / 3, D / 2, 11, -0.9, 0.5), BLACK, 1.0))
    return out


@product("board_cabinet")
def board_cabinet(fr, V, sp, b):
    """The vented board cabinet in 18 mm ply on the partition's kerb end, its back screwed to the partition and its
    door labelled inverter-supplied. Frame front -x: the door faces the kitchen."""
    W, D, H = fr.W, fr.D, fr.H
    t = 18.0
    out = [("carcass", fr.box(0, 0, 0, W, D, H) - fr.box(t, -1, t, W - 2 * t, D - t + 1, H - 2 * t), PLY, 1.0),
           ("door", fr.box(t + 1, 0, t + 1, W - 2 * t - 2, t, H - 2 * t - 2), "#ecd9b6", 1.0),
           ("door label, inverter-supplied", fr.box(W / 2 - 60, -0.5, H - 80, 120, 0.6, 30), "#f4d03f", 1.0),
           ("push latch", fr.cyl_v(W - 50, H / 2, 12, -0.9, 2), STEEL, 1.0)]
    for k in range(5):
        out.append(("vent slot", fr.box(W / 2 - 100, -0.4, 40 + k * 14, 200, 0.5, 6), DARK, 1.0))
    return out


@product("victron_unit")
def unit(fr, V, sp, b):
    """One Victron unit on the board, its back on the board panel: the blue case, the label band and, on the
    converters, the cooling fins. Frame front -x: the face toward the cabinet's door."""
    W, D, H = fr.W, fr.D, fr.H
    kind = sp["kind"]
    if kind == "board":
        return [("enclosure", fr.rbox(0, 0, 0, W, D, H, 6, "v"), WHITE, 1.0),
                ("breaker cover", fr.box(20, -0.9, H / 2 - 30, W - 40, 1.0, 60), "#aed6f1", 0.8)]
    body = fr.rbox(0, 0, 0, W, D, H, 5, "v")
    out = [("case", body, VICTRON, 1.0), ("label band", fr.box(10, -0.8, H - 40, W - 20, 0.9, 25), WHITE, 1.0)]
    if kind in ("mppt", "orion"):
        for k in range(6):
            out.append(("cooling fin", fr.box(W * 0.1, -0.9, 10 + k * (H - 60) / 6, W * 0.8, 1.0, 4), DARK, 1.0))
    if kind == "lynx":
        out.append(("busbar cover", fr.box(10, -0.8, 20, W - 20, 0.9, H - 70), BLACK, 0.85))
    if kind == "cerbo":
        out[0] = ("case", body, VGREY, 1.0)
    return out


@product("gx_touch_50")
def gx_touch(fr, V, sp, b):
    """The GX Touch 50 display on the board cabinet's door, 128 x 87 mm (Victron, est.)."""
    W, D, H = fr.W, fr.D, fr.H
    return [("bezel", fr.rbox(0, 0, 0, W, D, H, 4, "v"), BLACK, 1.0), ("screen", fr.box(8, -0.5, 8, W - 16, 0.6, H - 16), "#1a5276", 1.0)]


@product("board_panel")
def board_panel(fr, V, sp, b):
    """The 12 mm ply board panel on the board cabinet's back, which the Victron gear screws to."""
    return [("board panel", fr.box(0, 0, 0, fr.W, fr.D, fr.H), "#f5eedc", 1.0)]

"""The kitchen (research report 28 section 4): the tower and bench carcasses in 18 mm Garnica Ultralight ply, the
Dometic NRX 130C fridge, the CFX3 55IM freezer on its slide, the Camec convection microwave, the Truma Combi D 6 E,
the Dometic CVI1525 hob and CVS1350G sink with the mixer, the range hood, and the RESPA-CF2 and top-up fan in the
tower's top cupboard."""
from __future__ import annotations

from . import ALU, BLACK, CHROME, DARK, DOOR, GREY, PLY, RUBBER, STEEL, product

T = 18.0          # carcass panels
TOP = "#efe7da"   # laminated worktop
INOX = "#d5d8dc"


@product("tower_carcass")
def tower(fr, V, sp, b):
    """The tower: two full-height sides standing on the floor and screwed to the road wall, a top under the ceiling,
    a shelf under each appliance and each cupboard, the Combi's door with its 150 cm2 grille and the top cupboard's
    door. `shelves` gives each shelf's top, from the floor; `doors` each door's bottom and top."""
    W, D, H = fr.W, fr.D, fr.H
    out = [("side panel, bed end", fr.box(0, 0, 0, T, D, H), PLY, 1.0),
           ("side panel, bench end", fr.box(W - T, 0, 0, T, D, H), PLY, 1.0),
           ("top panel", fr.box(T, 0, H - T, W - 2 * T, D, T), PLY, 1.0)]
    for w in sp["shelves"]:
        out.append(("shelf", fr.box(T, 0, w - T, W - 2 * T, D, T), PLY, 1.0))
    for w0, w1 in sp["doors"]:
        out.append(("door", fr.box(T + 1, 0, w0 + 1, W - 2 * T - 2, T, w1 - w0 - 2), DOOR, 1.0))
        out.append(("push latch", fr.cyl_v(W - T - 40, w1 - 60 if w0 > 0 else w1 - 40, 12, -0.9, 2), STEEL, 1.0))
    w0, w1 = sp["doors"][0]
    for k in range(6):
        out.append(("heater air grille", fr.box(W / 2 - 110, -1, w0 + 40 + 14 * k, 220, 1.0, 6), DARK, 1.0))
    return out


@product("bench_carcass")
def bench(fr, V, sp, b):
    """The bench: a 30 mm laminated worktop on the end panel at the partition and on the divider between the freezer
    bay and the sink cabinet, the hob's cut-out and the sink's rebated cut-out in it, two drawers over the freezer on
    runners from the tower's side and the divider, and the sink cabinet's base and door. Its bench-end edge rests on a
    cleat on the tower's side."""
    W, D, H = fr.W, fr.D, fr.H
    du, (hu0, hu1, hv0, hv1), (su0, su1, sv0, sv1) = sp["divider"], sp["hob_cut"], sp["sink_cut"]
    top = fr.box(0, 0, H - 30, W, D, 30)
    top = top - fr.box(hu0, hv0, H - 31, hu1 - hu0, hv1 - hv0, 32)
    top = top - fr.box(su0, sv0, H - 5, su1 - su0, sv1 - sv0, 6)
    top = top - fr.box(su0 + 15, sv0 + 15, H - 31, su1 - su0 - 30, sv1 - sv0 - 30, 32)
    out = [("worktop", top, TOP, 1.0),
           ("end panel at the partition", fr.box(W - T, 0, 0, T, D, H - 30), PLY, 1.0),
           ("divider", fr.box(du, 0, 0, T, D, H - 30), PLY, 1.0),
           ("cleat on the tower's side", fr.box(0, 40, H - 70, 20, D - 80, 40), PLY, 1.0),
           ("sink cabinet base", fr.box(du + T, T, 0, W - du - 2 * T, D - T, T), PLY, 1.0),
           ("sink cabinet door", fr.box(du + T + 1, 0, T + 1, W - du - 2 * T - 2, T, H - 30 - T - 2), DOOR, 1.0),
           ("push latch", fr.cyl_v(du + T + 40, H - 90, 12, -0.9, 2), STEEL, 1.0)]
    for w0, w1 in sp["drawers"]:
        out.append(("drawer front", fr.box(2, 0, w0, du - 4, T, w1 - w0), DOOR, 1.0))
        box_ = fr.box(15, T, w0 + 10, du - 30, D - 80, w1 - w0 - 20) - fr.box(27, T + 12, w0 + 22, du - 54, D - 104, w1 - w0)
        out.append(("drawer box", box_, PLY, 1.0))
        out.append(("drawer runner", fr.box(0, T + 20, w0 + 30, 15, D - 120, 30), STEEL, 1.0))
        out.append(("drawer runner", fr.box(du - 15, T + 20, w0 + 30, 15, D - 120, 30), STEEL, 1.0))
        out.append(("push latch", fr.cyl_v(du / 2, w1 - 40, 12, -0.9, 2), STEEL, 1.0))
    return out


@product("dometic_nrx130")
def fridge(fr, V, sp, b):
    """Dometic NRX 130C, 126 L compressor fridge, 525 wide, 812 high, 568 deep (Dometic): the cabinet behind a black
    mounting frame, the door with its full-height handle, the freezer flap's line. It stands on the tower's shelf."""
    W, D, H = fr.W, fr.D, fr.H
    return [("cabinet", fr.box(10, 40, 0, W - 20, D - 40, H - 10), GREY, 1.0),
            ("mounting frame", fr.box(0, 35, 0, W, 5, H) - fr.box(15, 34, 15, W - 30, 7, H - 30), BLACK, 1.0),
            ("door", fr.rbox(5, 5, 5, W - 10, 30, H - 10, 6, "v"), "#4d5656", 1.0),
            ("handle", fr.box(W - 45, 0, H * 0.35, 20, 5, H * 0.5), BLACK, 1.0),
            ("freezer flap line", fr.box(25, 4, H - 240, W - 50, 1, 4), BLACK, 1.0),
            ("control panel", fr.box(W / 2 - 50, 4, H - 70, 100, 1, 30), "#5dade2", 1.0)]


@product("dometic_cfx3_55im")
def freezer(fr, V, sp, b):
    """Dometic CFX3 55IM, 53 L, 720 x 455 x 480 mm with its handles (Dometic), on its pull-out slide: two runners on the
    floor and a tray with the travel lock. The lid hinges along the wall side, the control panel is on the aisle face."""
    W, D, H = fr.W, fr.D, fr.H
    s = sp.get("slide", 35.0)
    out = [("slide runner", fr.box(40, 10, 0, 50, D - 20, s - 15), STEEL, 1.0),
           ("slide runner", fr.box(W - 90, 10, 0, 50, D - 20, s - 15), STEEL, 1.0),
           ("slide tray", fr.box(10, 5, s - 15, W - 20, D - 10, 15), ALU, 1.0),
           ("travel lock", fr.box(W / 2 - 30, 0, s - 15, 60, 5, 15), DARK, 1.0)]
    out += [("body", fr.rbox(45, 0, s, W - 90, D, H - s - 70, 40, "w"), "#5d6d7e", 1.0),
            ("lid", fr.rbox(45, 0, H - 70, W - 90, D, 70, 40, "w"), "#aab7b8", 1.0),
            ("control panel", fr.box(W / 2 - 80, 0, H - 170, 160, 1.0, 70), BLACK, 1.0)]
    for u0 in (0.0, W - 45):
        out.append(("handle", fr.box(u0, D / 2 - 120, H - 200, 45, 240, 50), DARK, 1.0))
    for u0 in (45.0, W - 105):
        out.append(("corner bumper", fr.box(u0, 0, s, 60, D, 25), RUBBER, 1.0))
    return out


@product("camec_053632")
def oven(fr, V, sp, b):
    """Camec 053632 28 L convection microwave, 510 x 418 x 318 mm: the steel case, the door with its dark window on
    the left, the control panel with its display, dial and door release on the right. It stands on the tower's shelf."""
    W, D, H = fr.W, fr.D, fr.H
    cp = 130.0
    return [("case", fr.box(0, 3, 0, W, D - 3, H), "#bfc9ca", 1.0),
            ("door", fr.box(0, 0, 0, W - cp, 3, H), "#2c3e50", 1.0),
            ("window", fr.box(40, -0.5, 50, W - cp - 110, 1.0, H - 100), "#17202a", 1.0),
            ("door release", fr.box(W - cp + 30, -0.9, 40, cp - 60, 1.9, 30), CHROME, 1.0),
            ("control panel", fr.box(W - cp, 0, 0, cp, 3, H), "#7f8c8d", 1.0),
            ("display", fr.box(W - cp + 20, -0.5, H - 70, cp - 40, 1.0, 30), "#58d68d", 1.0),
            ("dial", fr.cyl_v(W - cp / 2, H / 2 - 20, 28, -0.9, 3), CHROME, 1.0)]


@product("truma_combi_d6e")
def combi(fr, V, sp, b):
    """Truma Combi D 6 E, 525 x 450 x 300 mm (Truma): the grey casing with its 10 L boiler, the black cover, the four
    warm-air outlets on top and the water and fuel connections at the front. It is screwed to the floor."""
    W, D, H = fr.W, fr.D, fr.H
    out = [("casing", fr.rbox(0, 0, 0, W, D, H - 70, 25, "w"), "#99a3a4", 1.0),
           ("cover", fr.rbox(10, 10, H - 70, W - 20, D - 20, 40, 25, "w"), "#2c3e50", 1.0),
           ("connection panel", fr.box(40, 0, 40, 200, 1.0, 120), BLACK, 1.0)]
    for u, v in ((90, 110), (W - 90, 110), (90, D - 110), (W - 90, D - 110)):
        out.append(("warm-air outlet", fr.cyl_w(u, v, 33, H - 30, H), BLACK, 1.0))
    for u in (300.0, 360.0, 420.0):
        out.append(("water and fuel connection", fr.cyl_v(u, 80, 10, 0, 1.0), CHROME, 1.0))
    return out


@product("dometic_cvi1525")
def hob(fr, V, sp, b):
    """Dometic CVI1525 two-zone induction hob, 525 x 350 mm of black glass: the glass rests on the worktop round its
    cut-out, the body hangs below it, two 180 mm zones and the touch strip."""
    W, D, H = fr.W, fr.D, fr.H
    out = [("glass top", fr.box(0, 0, H - 5, W, D, 5), BLACK, 1.0),
           ("body", fr.box(25, 25, 0, W - 50, D - 50, H - 5), DARK, 1.0),
           ("touch controls", fr.box(W / 2 - 90, 15, H - 0.6, 180, 30, 0.6), GREY, 1.0)]
    for u in (W * 0.27, W * 0.73):
        ring = fr.cyl_w(u, D * 0.55, 92, H - 0.6, H) - fr.cyl_w(u, D * 0.55, 88, H - 1, H + 1)
        out.append(("cooking zone", ring, "#e74c3c", 1.0))
    return out


@product("dometic_cvs1350")
def sink(fr, V, sp, b):
    """Dometic CVS1350G sink, 350 x 350 mm: the stainless bowl hangs from its rim in the worktop's rebate, flush, with
    the tempered glass lid closed over it, and the waste below."""
    W, D, H = fr.W, fr.D, fr.H
    rim = fr.box(0, 0, H - 5, W, D, 5) - fr.box(20, 20, H - 6, W - 40, D - 40, 7)
    bowl = fr.rbox(20, 20, 30, W - 40, D - 40, H - 35, 30, "w") - fr.rbox(23, 23, 33, W - 46, D - 46, H, 28, "w")
    return [("rim", rim, INOX, 1.0), ("bowl", bowl, INOX, 1.0),
            ("glass lid", fr.box(20, 20, H - 5, W - 40, D - 40, 5), "#17202a", 0.6),
            ("waste and trap", fr.cyl_w(W / 2, D / 2, 22, 0, 33), GREY, 1.0)]


@product("sink_mixer")
def sink_mixer(fr, V, sp, b):
    """A single-lever sink mixer with a 4 L/min regulator, on the worktop in front of the sink, its spout over the bowl."""
    W, D, H = fr.W, fr.D, fr.H
    u = W / 2
    return [("base", fr.cyl_w(u, 30, 26, 0, 8), CHROME, 1.0),
            ("body", fr.cyl_w(u, 30, 20, 8, 150), CHROME, 1.0),
            ("lever", fr.box(u - 7, 10, 150, 14, 40, 18), CHROME, 1.0),
            ("spout", fr.cyl((u, 30, 140), (u, D - 15, H - 30), 10), CHROME, 1.0),
            ("aerator", fr.cyl_w(u, D - 15, 12, H - 60, H - 25), CHROME, 1.0)]


@product("range_hood")
def range_hood(fr, V, sp, b):
    """Sphere TCR-001 range hood, 600 x 300 mm: the stainless canopy screwed to the road wall, its mesh filter across
    the bottom with the two 12 V fans above it, and the 100 mm duct to its cowl in the wall behind."""
    W, D, H = fr.W, fr.D, fr.H
    canopy = fr.prism_vw([(0, 0), (D, 0), (D, H), (60, H), (0, 40)], 0, W)
    inner = fr.prism_vw([(2, -1), (D - 2, -1), (D - 2, H - 2), (61, H - 2), (2, 39)], 2, W - 2)
    return [("canopy", canopy - inner, INOX, 1.0),
            ("mesh filter", fr.box(2, 2, 2, W - 4, D - 4, 3), GREY, 1.0),
            ("duct", fr.cyl_v(W / 2, H - 55, 50, D - 60, D), ALU, 1.0)]


@product("respa_cf2")
def respa(fr, V, sp, b):
    """Sy-Klone RESPA-CF2: the powered precleaner's drum on its intake from the hood in the road wall, the filter
    housing with the MERV 16 and carbon filters, and the bracket bolted to the wall (Sy-Klone, sizes est.)."""
    W, D, H = fr.W, fr.D, fr.H
    u0 = sp.get("clear", 20.0)
    w = W - u0
    return [("wall bracket", fr.box(u0, D - 8, 20, w, 8, H - 40), STEEL, 1.0),
            ("precleaner drum", fr.cyl_v(u0 + w / 2, H / 2, min(w, H) / 2 - 15, D - 160, D - 8), BLACK, 1.0),
            ("filter housing", fr.cyl_v(u0 + w / 2, H / 2, min(w, H) / 2 - 30, 40, D - 160), "#7f8c8d", 1.0),
            ("outlet", fr.cyl_v(u0 + w / 2, H / 2, 50, 0, 40), DARK, 1.0)]


@product("topup_fan")
def topup_fan(fr, V, sp, b):
    """The parked overpressure fan: a sealed aluminium box with its EC radial fan, the filter door for the ISO coarse,
    ePM1 and carbon stages, and its outlet, screwed to the road wall."""
    W, D, H = fr.W, fr.D, fr.H
    return [("box", fr.box(0, 20, 0, W, D - 20, H), ALU, 1.0),
            ("filter door", fr.box(10, 5, 10, W - 20, 15, H - 20), "#aab7b8", 1.0),
            ("door latch", fr.box(W / 2 - 15, 0, H / 2 - 10, 30, 5, 20), BLACK, 1.0),
            ("outlet", fr.cyl_v(W - 50, H - 40, 30, 0, 5), DARK, 1.0)]

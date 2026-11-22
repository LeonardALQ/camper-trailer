"""Body solids for the 3D model (BODY.md): floor, walls with their openings cut, the fixed roof, the roof-to-wall joiner,
the entry door, windows, vents and the mud flaps. Every solid is an envelope at planning level, placed in the project
datum DIM-01. Revision C: the home trailer's fixed roof 2,000 mm inside, the wet room door in the rear wall and four windows."""
from __future__ import annotations

from build123d import Compound

from .body import Body
from .model.prims import box, rgba
from .model.products import Frame

GLASS, PANEL, RING = ("#5dade2", 0.45), ("#d6dbdf", 0.35), ("#7f8c8d", 1.0)


def _cut(shape, holes):
    for h in holes:
        shape = shape - h
    return shape


def _iid(lay, item, pick) -> str:
    """The instance id of the layout item `item` that `pick` chooses, so each body solid is named by its own mass line."""
    blocks = [b for b in lay.blocks if b.id == item]
    chosen = [b for b in blocks if pick(b)] if len(blocks) > 1 else blocks
    return chosen[0].iid if chosen else item


def _at(b, axis: int) -> float:
    return b.cog[axis] if b.cog else 0.0


def body_solids(lay) -> list[tuple[str, object, tuple[str, float]]]:
    """(label, shape, (colour, alpha)) for every body solid. A label starts with the solid's line in the mass schedule."""
    V = lay.V
    b = Body(lay, None)
    x0, x1, hw, wt, fz, H = V["body_x0"], V["body_x1"], V["half_bw"], V["wall_t"], V["floor_z"], V["interior_h"]
    L = V["body_length"]
    ops = b.openings()
    out = []

    def side_hole(o, y0, depth):
        return box(x0 + o["u0"], y0 - 1, fz + o["z0"], o["w"], depth + 2, o["h"])

    def end_hole(o, x, depth):
        return box(x - 1, o["u0"], fz + o["z0"], depth + 2, o["w"], o["h"])

    def filler(o):
        glass = "Window" in o["name"]
        door = o.get("from") in ("BD-07", "BD-15")
        col = GLASS if glass else ("#b2bec3", 0.5 if door else 0.6)
        name = o["name"].split(",")[0]
        label = f"{o['from']} {name}, closed" if door else f"{o.get('line') or o['id']} {name}"
        return glass, col, label

    def fitted(o, hole, front, plain):
        """A window or a door as its product in its cut-out (`hole`, through the wall, `front` its outward normal),
        anything else as the plain filler."""
        glass, col, label = filler(o)
        if glass or o.get("from") in ("BD-07", "BD-15"):
            return label, (_window if glass else _door)(Frame(hole, front), label), col
        if "service door" in o["name"]:
            return label, _service_door(Frame(hole, front), label), col
        return label, plain, col

    out.append(("BD-01 Floor, 30 mm woven roving and H80", box(x0, -hw, V["floor_underside_z"], L, 2 * hw, V["floor_t"]), ("#8c8c8c", 0.7)))
    for wall, y0 in (("kerb", -hw), ("road", hw - wt)):
        holes = [side_hole(o, y0, wt) for o in ops if o["wall"] == wall]
        iid = _iid(lay, "BD-03", lambda b, w=wall: (_at(b, 1) < 0) == (w == "kerb"))
        out.append((f"{iid} {wall.capitalize()}-side wall, 35 mm GRP and XPS", _cut(box(x0, y0, fz, L, wt, H), holes), PANEL))
        for o in ops:
            if o["wall"] != wall:
                continue
            hole = (x0 + o["u0"], y0, fz + o["z0"], x0 + o["u0"] + o["w"], y0 + wt, fz + o["z0"] + o["h"])
            out.append(fitted(o, hole, "-y" if wall == "kerb" else "+y", box(x0 + o["u0"], y0, fz + o["z0"], o["w"], wt, o["h"])))
    for wall, x in (("front", x0), ("rear", x1 - wt)):
        holes = [end_hole(o, x, wt) for o in ops if o["wall"] == wall]
        iid = _iid(lay, "BD-04", lambda b, w=wall: (_at(b, 0) < x0 + L / 2) == (w == "front"))
        out.append((f"{iid} {wall.capitalize()} wall, 35 mm GRP and XPS", _cut(box(x, -hw + wt, fz, wt, 2 * (hw - wt), H), holes), PANEL))
        for o in ops:
            if o["wall"] != wall:
                continue
            hole = (x, o["u0"], fz + o["z0"], x + wt, o["u0"] + o["w"], fz + o["z0"] + o["h"])
            out.append(fitted(o, hole, "-x" if wall == "front" else "+x", box(x, o["u0"], fz + o["z0"], wt, o["w"], o["h"])))
    # the roof-to-wall joiner round the top of the walls, and the fixed roof on it
    zc = V["ceiling_z"]
    rw, rh = 50, 30
    ring = box(x0, -hw, zc - rh, L, 2 * hw, rh) - box(x0 + rw, -hw + rw, zc - rh - 1, L - 2 * rw, 2 * hw - 2 * rw, rh + 2)
    out.append(("BD-08 Roof-to-wall joiner, bonded", ring, RING))
    out.append(("BD-02 Fixed roof, 40 mm GRP and XPS", box(x0, -hw, zc, L, 2 * hw, V["roof_t"]), ("#f0f3f4", 0.6)))
    # mud flaps behind the rear tyres (BD-10), each on its galvanised hanger from the XT rear shock outrigger
    xf = V["axle_x"] + V["rear_hub_dx"] + V["tyre_d"] / 2 + 60
    for s in (1, -1):
        iid = _iid(lay, "BD-10", lambda b, s=s: (_at(b, 1) > 0) == (s > 0))
        side = "road" if s > 0 else "kerb"
        out.append((f"{iid} Mud flap, {side} side, 610 x 455 rubber", _mud_flap(lay, xf, s), ("#1c2833", 1.0)))
    return out


def _mud_flap(lay, xf, s):
    """The 610 x 455 x 6 mm flap behind a rear tyre, its inboard top corner cut clear of the rail, the raiser and the
    grey tank's guard under the rails, hung from a flat bar off the XT rear shock outrigger's back face (BD-10, CT-003)."""
    V = lay.V
    yc = s * V["hub_y"]
    flap = box(xf - 3, yc - 305, 300, 6, 610, 455)
    clear = V["rail_outer_w"] / 2 + 3                      # 3 mm outboard of the rail's and the raiser's outer face
    inboard = clear - 600 if s > 0 else -clear
    guard = next((g.box for g in lay.blocks if g.id == "UF-09" and g.box), None)
    cut_z = min(V["rail_underside_z"], guard[2] if guard and guard[0] <= xf <= guard[3] else V["rail_underside_z"]) - 5
    flap = flap - box(xf - 4, inboard, cut_z, 8, 600, 300 + 455 - cut_z + 5)
    tips = [b.extra["member"].box() for b in lay.blocks if b.extra.get("role") == "outrigger" and "member" in b.extra]
    ox1, oz0 = next((t[3], t[2]) for t in tips if 0 < xf - t[3] < 100 and (t[1] + t[4] > 0) == (s > 0))
    y0, y1 = (clear + 5, yc + 275) if s > 0 else (yc - 275, -clear - 5)
    return _pieces("mud flap", [("rubber flap", flap, "#1c2833", 1.0),
                                ("hanger bar", box(ox1, y0, 755, xf + 3 - ox1, y1 - y0, 6), "#a6acaf", 1.0),
                                ("hanger plate on the outrigger", box(ox1, y0, 755, 6, y1 - y0, oz0 + 60 - 755), "#a6acaf", 1.0)])


def _pieces(label, parts):
    kids = []
    for name, shp, col, a in parts:
        shp.label, shp.color = name, rgba(col, a)
        kids.append(shp)
    return Compound(label=label, children=kids)


def _window(fr, label):
    """A Dometic S4 top-hinged window in its cut-out: the black outer frame 21 mm proud of the skin, the frame through
    the cut-out, the double acrylic pane, and the white inner frame with the blind and fly screen cassette at its top."""
    W, D, H = fr.W, fr.D, fr.H
    e = 22.0
    return _pieces(label, [
        ("outer frame", fr.box(-25, -21, -25, W + 50, 21, H + 50) - fr.box(e, -22, e, W - 2 * e, 23, H - 2 * e), "#1c2833", 1.0),
        ("frame in the cut-out", fr.box(0, 0, 0, W, D, H) - fr.box(e, -1, e, W - 2 * e, D + 2, H - 2 * e), "#2c3e50", 1.0),
        ("double acrylic pane", fr.box(e, D / 2 - 5, e, W - 2 * e, 10, H - 2 * e), "#5d6d7e", 0.55),
        ("inner frame", fr.box(-15, D, -15, W + 30, 10, H + 30) - fr.box(e, D - 1, e, W - 2 * e, 12, H - 2 * e), "#f4f6f6", 1.0),
        ("blind and fly screen cassette", fr.box(e, D, H - e - 40, W - 2 * e, 10, 40), "#f4f6f6", 1.0)])


def _service_door(fr, label):
    """The Thetford 2680584 service door for the cassette: its white frame 8 mm proud of the skin, the door in it, and
    the lock (Thetford)."""
    W, D, H = fr.W, fr.D, fr.H
    return _pieces(label, [
        ("frame", fr.box(-15, -8, -15, W + 30, 8, H + 30) - fr.box(15, -9, 15, W - 30, 10, H - 30), "#f4f6f6", 1.0),
        ("frame in the cut-out", fr.box(0, 0, 0, W, D, H) - fr.box(15, -1, 15, W - 30, D + 2, H - 30), "#e5e8e8", 1.0),
        ("door", fr.box(16, -6, 16, W - 32, 10, H - 32), "#fdfefe", 1.0),
        ("lock", fr.cyl_v(W - 50, H / 2, 14, -8, -6), "#566573", 1.0)])


def _door(fr, label):
    """An Aussie Traveller DC door, closed, in its cut-out: the aluminium frame, the composite leaf with its tinted window
    and pleated blind, the hinges, and the handle outside, 40 mm proud, and inside."""
    W, D, H = fr.W, fr.D, fr.H
    f = 25.0
    wz0, wz1 = H * 0.55, H - 110
    parts = [("door frame", fr.box(0, 0, 0, W, D, H) - fr.box(f, -1, f, W - 2 * f, D + 2, H - 2 * f), "#d5d8dc", 1.0),
             ("door leaf", fr.box(f + 1, 3, f + 1, W - 2 * f - 2, D - 6, H - 2 * f - 2), "#f4f6f6", 1.0),
             ("tinted window", fr.box(70, 2, wz0, W - 140, D - 10, wz1 - wz0), "#34495e", 0.7),
             ("pleated blind", fr.box(70, D - 8, wz0, W - 140, 3, wz1 - wz0), "#ecf0f1", 1.0),
             ("handle, outside", fr.box(W - 100, -40, H * 0.5 - 60, 28, 44, 120), "#1c2833", 1.0),
             ("handle, inside", fr.box(W - 100, D - 4, H * 0.5 - 50, 28, 34, 100), "#1c2833", 1.0)]
    for w in (250.0, H - 350):
        parts.append(("hinge", fr.box(f - 6, 4, w, 14, D - 8, 90), "#909497", 1.0))
    return _pieces(label, parts)


BODY_IDS = ("BD-01", "BD-02", "BD-03", "BD-04", "BD-07", "BD-15", "BD-17", "WN-01", "WN-02", "WN-03", "WN-04")   # blocks the body solids replace

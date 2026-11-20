"""Body solids for the 3D model (BODY.md): floor, walls with their openings cut, the fixed roof, the roof-to-wall joiner,
the entry door, windows, vents and the mud flaps. Every solid is an envelope at planning level, placed in the project
datum DIM-01. Revision B: the fixed roof of the LandCruiser 79 layout, with no pop-top, garage door or rear portal."""
from __future__ import annotations

from .body import Body
from .model.prims import box

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
        door = o["id"] == "OP-02"
        col = GLASS if glass else ("#b2bec3", 0.5 if door else 0.6)
        label = "BD-07 Entry door, closed" if door else f"{o['id']} {o['name'].split(',')[0]}"
        return glass, col, label

    out.append(("BD-01 Floor, 30 mm woven roving and H80", box(x0, -hw, V["floor_underside_z"], L, 2 * hw, V["floor_t"]), ("#8c8c8c", 0.7)))
    for wall, y0 in (("kerb", -hw), ("road", hw - wt)):
        holes = [side_hole(o, y0, wt) for o in ops if o["wall"] == wall]
        iid = _iid(lay, "BD-03", lambda b, w=wall: (_at(b, 1) < 0) == (w == "kerb"))
        out.append((f"{iid} {wall.capitalize()}-side wall, 35 mm GRP and XPS", _cut(box(x0, y0, fz, L, wt, H), holes), PANEL))
        for o in ops:
            if o["wall"] != wall:
                continue
            glass, col, label = filler(o)
            yy = y0 + (wt / 2 - 5 if glass else 0)
            out.append((label, box(x0 + o["u0"], yy, fz + o["z0"], o["w"], 10 if glass else wt, o["h"]), col))
    for wall, x in (("front", x0), ("rear", x1 - wt)):
        holes = [end_hole(o, x, wt) for o in ops if o["wall"] == wall]
        iid = _iid(lay, "BD-04", lambda b, w=wall: (_at(b, 0) < x0 + L / 2) == (w == "front"))
        out.append((f"{iid} {wall.capitalize()} wall, 35 mm GRP and XPS", _cut(box(x, -hw + wt, fz, wt, 2 * (hw - wt), H), holes), PANEL))
        for o in ops:
            if o["wall"] != wall:
                continue
            glass, col, label = filler(o)
            out.append((label, box(x + (wt / 2 - 5 if glass else 0), o["u0"], fz + o["z0"], 10 if glass else wt, o["w"], o["h"]), col))
    # the roof-to-wall joiner round the top of the walls, and the fixed roof on it
    zc = V["ceiling_z"]
    rw, rh = 50, 30
    ring = box(x0, -hw, zc - rh, L, 2 * hw, rh) - box(x0 + rw, -hw + rw, zc - rh - 1, L - 2 * rw, 2 * hw - 2 * rw, rh + 2)
    out.append(("BD-08 Roof-to-wall joiner, bonded", ring, RING))
    out.append(("BD-02 Fixed roof, 40 mm GRP and XPS", box(x0, -hw, zc, L, 2 * hw, V["roof_t"]), ("#f0f3f4", 0.6)))
    # mud flaps behind the rear tyres (BD-10)
    xf = V["axle_x"] + V["rear_hub_dx"] + V["tyre_d"] / 2 + 60
    for s in (1, -1):
        iid = _iid(lay, "BD-10", lambda b, s=s: (_at(b, 1) > 0) == (s > 0))
        side = "road" if s > 0 else "kerb"
        out.append((f"{iid} Mud flap, {side} side, 610 x 455 rubber", box(xf - 3, s * V["hub_y"] - 305, 300, 6, 610, 455), ("#1c2833", 1.0)))
    return out


BODY_IDS = ("BD-01", "BD-02", "BD-03", "BD-04", "BD-07")   # blocks the body solids replace in the model

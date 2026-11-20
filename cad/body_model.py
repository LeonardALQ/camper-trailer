"""Body solids for the 3D model (BODY.md): floor, walls with their openings cut, the lid roof down or raised, the
pop-top rings and canvas, the rear portal, the doors, windows, vents, roof hatches and the mud flaps. Every solid is
an envelope at planning level, placed in the project datum DIM-01."""
from __future__ import annotations

from .body import Body
from .model.prims import box

GLASS, PANEL, RING, STEEL, CANVAS = ("#5dade2", 0.45), ("#d6dbdf", 0.35), ("#7f8c8d", 1.0), ("#566573", 1.0), ("#c8b88a", 0.45)


def _cut(shape, holes):
    for h in holes:
        shape = shape - h
    return shape


def body_solids(lay, raised: bool = False) -> list[tuple[str, object, tuple[str, float]]]:
    """(label, shape, (colour, alpha)) for every body solid. `raised` lifts the lid, the top ring and the hatches by the
    roof's lift and shows the canvas skirt and the guide posts."""
    V = lay.V
    b = Body(lay, None)
    d = b.d
    lift = d["roof"]["lift"] if raised else 0.0
    x0, x1, hw, wt, fz, H = V["body_x0"], V["body_x1"], V["half_bw"], V["wall_t"], V["floor_z"], V["interior_h"]
    L = V["body_length"]
    ops = b.openings()
    out = []

    def side_hole(o, y0, depth):
        return box(x0 + o["u0"], y0 - 1, fz + o["z0"], o["w"], depth + 2, o["h"])

    def end_hole(o, x, depth):
        return box(x - 1, o["u0"], fz + o["z0"], depth + 2, o["w"], o["h"])

    out.append(("BD-01 Floor, 30 mm woven roving and H80", box(x0, -hw, V["floor_underside_z"], L, 2 * hw, V["floor_t"]), ("#8c8c8c", 0.7)))
    for wall, y0 in (("kerb", -hw), ("road", hw - wt)):
        holes = [side_hole(o, y0, wt) for o in ops if o["wall"] == wall]
        out.append((f"BD-03 {wall.capitalize()}-side wall, 35 mm GRP and XPS", _cut(box(x0, y0, fz, L, wt, H), holes), PANEL))
        for o in ops:
            if o["wall"] != wall:
                continue
            glass = "Window" in o["name"]
            col = GLASS if glass else ("#b2bec3", 0.6)
            yy = y0 + (wt / 2 - 5 if glass else 0)
            dep = 10 if glass else wt
            out.append((f"{o['id']} {o['name'].split(',')[0]}", box(x0 + o["u0"], yy, fz + o["z0"], o["w"], dep, o["h"]), col))
    for wall, x in (("front", x0), ("rear", x1 - wt)):
        holes = [end_hole(o, x, wt) for o in ops if o["wall"] == wall]
        out.append((f"BD-04 {wall.capitalize()} wall, 35 mm GRP and XPS", _cut(box(x, -hw + wt, fz, wt, 2 * (hw - wt), H), holes), PANEL))
        for o in ops:
            if o["wall"] != wall:
                continue
            glass = "Window" in o["name"]
            leaf = o["id"] == "OP-12"
            col = GLASS if glass else (("#b2bec3", 0.35) if leaf else ("#b2bec3", 0.6))
            label = "BD-05 Garage door leaf, closed" if leaf else f"{o['id']} {o['name'].split(',')[0]}"
            out.append((label, box(x + (wt / 2 - 5 if glass else 0), o["u0"], fz + o["z0"], 10 if glass else wt, o["w"], o["h"]), col))
    # the rear portal inside the rear wall: header, kerb-side post and road-side jamb (steel, BODY.md)
    mp = lay.mod.params
    xin = x1 - wt - 50
    ph = d["portal"]["height"]
    y0, y1 = mp["door_y0"], mp["door_y1"]
    out.append(("Rear portal header SHS 50 x 50 x 5", box(xin, y0 - 50, fz + ph - 50, 50, y1 - y0 + 90, 50), STEEL))
    out.append(("Rear portal kerb-side post SHS 50 x 50 x 5", box(xin, y0 - 50, fz, 50, 50, ph - 50), STEEL))
    out.append(("Rear portal road-side jamb SHS 40 x 40 x 5", box(xin + 10, y1, fz, 40, 40, ph - 50), STEEL))
    # pop-top rings, lid, hatches, canvas and guide posts
    zc = V["ceiling_z"]
    rw, rh = 50, 30
    ring = box(x0, -hw, zc - rh, L, 2 * hw, rh) - box(x0 + rw, -hw + rw, zc - rh - 1, L - 2 * rw, 2 * hw - 2 * rw, rh + 2)
    out.append(("BD-08 Pop-top bottom ring", ring, RING))
    top = box(x0, -hw, zc + lift - 2, L, 2 * hw, 2) - box(x0 + rw, -hw + rw, zc + lift - 3, L - 2 * rw, 2 * hw - 2 * rw, 4)
    out.append(("BD-12 Pop-top top ring", top, RING))
    lid = box(x0, -hw, zc + lift, L, 2 * hw, V["roof_t"])
    for h in d["roof"]["hatches"]:
        cx = x0 + h["x"] if h["end"] == "front" else x1 - h["x"]
        lid = lid - box(cx - h["cut"][0] / 2, h["y"] - h["cut"][1] / 2, zc + lift - 1, h["cut"][0], h["cut"][1], V["roof_t"] + 2)
        ox, oy = h["outer"]
        out.append((f"BD-09 {h['id']}", box(cx - ox / 2, h["y"] - oy / 2, zc + lift + V["roof_t"], ox, oy, 60), ("#ecf0f1", 0.8)))
    out.append(("BD-02 Lid, 40 mm GRP and XPS, " + ("raised" if raised else "roof down"), lid, ("#f0f3f4", 0.6)))
    if raised:
        sk = 2.0
        for nm, bx in (("kerb", (x0 + wt, -hw + wt, zc, L - 2 * wt, sk, lift)), ("road", (x0 + wt, hw - wt - sk, zc, L - 2 * wt, sk, lift)),
                       ("front", (x0 + wt, -hw + wt, zc, sk, 2 * (hw - wt), lift)), ("rear", (x1 - wt - sk, -hw + wt, zc, sk, 2 * (hw - wt), lift))):
            out.append((f"BD-12 Canvas skirt, {nm}", box(*bx), CANVAS))
        for cx in (x0 + wt + 40, x1 - wt - 80):
            for cy in (-hw + wt + 40, hw - wt - 80):
                out.append(("BD-12 LA36 actuator and guide post", box(cx, cy, zc - 1075 + lift, 40, 40, 1075), ("#34495e", 1.0)))
    # mud flaps behind the rear tyres (BD-10)
    xf = V["axle_x"] + V["rear_hub_dx"] + V["tyre_d"] / 2 + 60
    for s in (1, -1):
        out.append(("BD-10 Mud flap, 610 x 455 rubber", box(xf - 3, s * V["hub_y"] - 305, 300, 6, 610, 455), ("#1c2833", 1.0)))
    return out


BODY_IDS = ("BD-01", "BD-02", "BD-03", "BD-04", "BD-05", "BD-07")   # blocks the body solids replace in the model

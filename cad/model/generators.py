"""Part generators. Each returns (shape, info) for one instance, already placed in the module frame.
info may hold `length_m` (per-length mass) or `area_m2` (per-area mass) measured from the geometry.

Generators read their sizes from the part's YAML params (merged with the item's params) and the
assembly parameters P. Nothing here holds a dimension of its own except where noted as an envelope.
"""
from __future__ import annotations

import math

from build123d import (
    Axis, Compound, Cylinder, Plane, Pos, Rectangle, RectangleRounded, Rot, extrude, fillet,
)

from .prims import box, box_span, cyl, prism_xy, prism_xz, prism_yz, strap_between


def _fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out + s
    return out


# ------------------------------------------------------------------ made parts
def gen_box(prm, at, P):
    dx, dy, dz = prm["dx"], prm["dy"], prm["dz"]
    s = box(at[0], at[1], at[2], dx, dy, dz)
    if prm.get("fillet"):
        s = fillet(s.edges().filter_by(Axis.Z), prm["fillet"])
    return s, {"area_m2": dx * dy / 1e6}


def gen_panel(prm, at, P):
    dx, dy, dz = prm["dx"], prm["dy"], prm["dz"]
    x0, y0, z0 = at
    s = box(x0, y0, z0, dx, dy, dz)
    normal = prm.get("normal", "x")
    t = {"x": dx, "y": dy, "z": dz}[normal]
    area = dx * dy * dz / t
    for u0, v0, w, h in prm.get("cutouts", []):
        if normal == "x":
            cut = box(x0 - 1, y0 + u0, z0 + v0, dx + 2, w, h)
        elif normal == "z":
            cut = box(x0 + u0, y0 + v0, z0 - 1, w, h, dz + 2)
        else:
            cut = box(x0 + u0, y0 - 1, z0 + v0, w, dy + 2, h)
        s = s - cut
        area -= w * h
    return s, {"area_m2": area / 1e6, "thickness": t}


def gen_rhs(prm, at, P):
    L, H, W, t, r = prm["length"], prm["height"], prm["width"], prm["wall"], prm.get("outer_radius", 0)
    outer = RectangleRounded(W, H, r) if r > 0 else Rectangle(W, H)
    inner = RectangleRounded(W - 2 * t, H - 2 * t, r - t) if r - t > 0.2 else Rectangle(W - 2 * t, H - 2 * t)
    prof = outer - inner
    s = Pos(at[0], at[1], at[2] + H / 2) * extrude(Plane.YZ * prof, amount=L)
    return s, {"length_m": L / 1000}


def gen_froli(prm, at, P):
    dx, dy, dz = prm["dx"], prm["dy"], prm["dz"]
    nx, ny = int(prm.get("nx", 10)), int(prm.get("ny", 6))
    base_t = 8
    x0, y0, z0 = at
    parts = [box(x0, y0, z0, dx, dy, base_t)]
    px, py = dx / nx, dy / ny
    a = min(px, py) * 0.8 / 2          # spring element half-size (square envelope of each element)
    for i in range(nx):
        for j in range(ny):
            cx, cy = x0 + px * (i + 0.5), y0 + py * (j + 0.5)
            parts.append(box_span(cx - a, cx + a, cy - a, cy + a, z0 + base_t, z0 + dz))
    return _fuse(parts), {"area_m2": dx * dy / 1e6}


def _mitred(piece, a_axis, n_dir, s0, s1, e, leg, xr):
    """Mitre both ends of a cleat lying in a Y-Z face plane. a_axis 'y' or 'z' is the length axis,
    n_dir (+1/-1) the inward direction along the other axis, e the edge position on that axis."""
    big = leg + 2
    def tri(pts_an):
        pts = [((a, n) if a_axis == "y" else (n, a)) for a, n in pts_an]
        return prism_yz(pts, xr[0], xr[1])
    n1 = e + n_dir * big
    piece = piece - tri([(s0 - 0.001, e - n_dir * 0.001), (s0 - 0.001, n1), (s0 + big, n1)])
    piece = piece - tri([(s1 + 0.001, e - n_dir * 0.001), (s1 + 0.001, n1), (s1 - big, n1)])
    return piece


def gen_cleat(prm, spec, P):
    """Angle cleat on a partition face. Leg 1 lies on the face, leg 2 stands off the face at the edge."""
    leg, t = prm["leg"], prm["thickness"]
    fx, dxs = spec["face_x"], spec["dir_x"]
    x_face, x_out = fx, fx + dxs * leg
    xr = sorted((x_face - dxs * 0.0, x_out))
    xr = (min(xr) - 0.5, max(xr) + 0.5)
    L = spec["length"]
    corner = spec["corner"]
    if spec["axis"] == "y":
        y0, y1 = spec["at_u"], spec["at_u"] + L
        z = spec["at_z"]
        n = 1 if corner == "floor" else -1          # inward along Z
        leg1 = box_span(fx, fx + dxs * t, y0, y1, z, z + n * leg)
        leg2 = box_span(fx, fx + dxs * leg, y0, y1, z, z + n * t)
        piece = leg1 + leg2
        piece = _mitred(piece, "y", n, y0, y1, z, leg, xr)
    else:
        z0, z1 = spec["at_z"], spec["at_z"] + L
        y = spec["at_u"]
        n = 1 if corner == "wall_neg" else -1       # inward along Y
        leg1 = box_span(fx, fx + dxs * t, y, y + n * leg, z0, z1)
        leg2 = box_span(fx, fx + dxs * leg, y, y + n * t, z0, z1)
        piece = leg1 + leg2
        piece = _mitred(piece, "z", n, z0, z1, y, leg, xr)
    return piece, {"length_m": L / 1000}


def gen_ledger(prm, spec, P):
    """40x40x3 ledger. On a partition the vertical leg hangs below a shelf whose top is `top_z`.
    On a side wall the vertical leg hangs below the shelf that carries the deck edge."""
    leg, t = prm["leg"], prm["thickness"]
    top = spec["top_z"]
    L = spec["length"]
    hw = P.get("half_width")
    gl = P.get("garage_length")
    w = spec["wall"]
    if w in ("partition_a", "partition_b"):
        x0, s = (0.0, 1) if w == "partition_a" else (gl, -1)
        prof = [(x0, top - leg), (x0 + s * t, top - leg), (x0 + s * t, top - t), (x0 + s * leg, top - t), (x0 + s * leg, top), (x0, top)]
        if s < 0:
            prof = prof[::-1]
        shape = prism_xz(prof, -hw, -hw + L)
    else:
        y0, s = (-hw, 1) if w == "road" else (hw, -1)
        prof = [(y0, top - leg), (y0 + s * t, top - leg), (y0 + s * t, top - t), (y0 + s * leg, top - t), (y0 + s * leg, top), (y0, top)]
        if s < 0:
            prof = prof[::-1]
        shape = prism_yz(prof, 0.0, L)
    return shape, {"length_m": L / 1000}


# ------------------------------------------------------------------ bought items (envelopes)
def gen_condor_chock(prm, at, P):
    """Condor SC-2000 envelope: 229 x 635 base, 381 high front hoop, cradle under the tyre.
    Origin: nose centre on the floor at the wall face; the base runs towards +Y."""
    W, Lb, H, rise = prm["base_w"], prm["base_l"], prm["height"], prm["cradle_rise"]
    x, y, z = at
    rail = 25
    parts = [
        box_span(x - W / 2, x - W / 2 + rail, y, y + Lb, z, z + 30),
        box_span(x + W / 2 - rail, x + W / 2, y, y + Lb, z, z + 30),
        box_span(x - W / 2 + rail, x + W / 2 - rail, y, y + rail, z, z + 30),
        box_span(x - W / 2 + rail, x + W / 2 - rail, y + Lb - rail, y + Lb, z, z + 30),
        # cross bars under the cradle (clear of the front track row)
        box_span(x - W / 2 + rail, x + W / 2 - rail, y + 100, y + 125, z, z + rise - 6),
        box_span(x - W / 2 + rail, x + W / 2 - rail, y + 420, y + 445, z, z + rise - 6),
        # cradle plate and cheeks (the tyre sits on the plate, top at the cradle rise)
        box_span(x - 70, x + 70, y + 60, y + 480, z + rise - 6, z + rise),
        box_span(x - 76, x - 70, y + 200, y + 480, z + rise, z + rise + 120),
        box_span(x + 70, x + 76, y + 200, y + 480, z + rise, z + rise + 120),
    ]
    yh = y + 12.5
    for s in (1, -1):
        parts.append(cyl((x + s * 90, yh, z + 30), (x + s * 90, yh, z + H - 12.5), 12.5))
        parts.append(cyl((x + s * 90, yh, z + 300), (x + s * (W / 2 - 12.5), y + 330, z + 30), 10))
    parts.append(cyl((x - 102.5, yh, z + H - 12.5), (x + 102.5, yh, z + H - 12.5), 12.5))
    return _fuse(parts), {}


def gen_l_track(prm, at, P):
    L = prm["length"]
    W, H = prm["width"], prm["height"]
    x, y, z = at
    s = box_span(x, x + L, y - W / 2, y + W / 2, z, z + H)
    s = s - box_span(x - 1, x + L + 1, y - prm["slot_w"] / 2, y + prm["slot_w"] / 2, z + H - prm["slot_d"], z + H + 1)
    return s, {"length_m": L / 1000}


def gen_track_fitting(prm, at, P):
    x, y, z = at
    l, w, h = prm["length"], prm["width"], prm["height"]
    base = box_span(x - l / 2, x + l / 2, y - w / 2, y + w / 2, z, z + h * 0.45)
    ring = Pos(x, y, z + h * 0.45) * Rot(0, 90, 0) * (Cylinder(h * 0.55, 8) - Cylinder(h * 0.3, 10))
    ring = ring - box_span(x - 20, x + 20, y - 20, y + 20, z - 30, z + h * 0.45)
    return base + ring, {}


def gen_winch(prm, at, P):
    x, y, z = at  # y is the road-side wall face
    pl, ph, pt = prm["plate_l"], prm["plate_h"], prm["plate_t"]
    parts = [box_span(x - pl / 2, x + pl / 2, y, y + pt, z, z + ph)]
    if not prm.get("plate_only"):
        L, D, H = prm["length"], prm["depth"], prm["height"]
        zc = z + ph / 2
        parts.append(box_span(x - L / 2, x - L / 2 + 70, y + pt, y + pt + D, zc - H / 2, zc + H / 2))
        parts.append(box_span(x + L / 2 - 70, x + L / 2, y + pt, y + pt + D, zc - H / 2, zc + H / 2))
        parts.append(cyl((x - L / 2 + 70, y + pt + D / 2, zc), (x + L / 2 - 70, y + pt + D / 2, zc), H / 2 - 10))
    return _fuse(parts), {}


def gen_vent(prm, at, P):
    x, y, z = at
    f = prm.get("facing", 1)
    return box_span(x - prm["width"] / 2, x + prm["width"] / 2, y, y + f * prm["depth"], z, z + prm["height"]), {}


def gen_fume_sensor(prm, at, P):
    x, y, z = at
    w, h, d = prm["width"], prm["height"], prm["depth"]
    if "facing_x" in prm:
        f = prm["facing_x"]
        return box_span(x, x + f * d, y - w / 2, y + w / 2, z, z + h), {}
    f = prm.get("facing_y", 1)
    return box_span(x - w / 2, x + w / 2, y, y + f * d, z, z + h), {}


def gen_extinguisher(prm, at, P):
    x, y, z = at
    d, h = prm["diameter"], prm["height"]
    body = Pos(x, y, z + (h - 60) / 2) * Cylinder(d / 2, h - 60)
    head = Pos(x, y, z + h - 30) * Cylinder(d / 4, 60)
    return body + head, {}


def gen_ladder(prm, at, P):
    """Owner-built ladder hooked on the deck edge (revision B).

    `at` is (X of the deck end, Y of the ladder centreline, Z of the deck top). Two square stiles
    (`stile` mm, the SHS 25x1.6 envelope) lean `lean_deg` from vertical into the living area. Each
    stile is `length` mm along its axis between level-cut ends, with its top end at the deck-top level.
    A hook bar on each stile lies on the deck top from `hook_reach` mm inboard of the deck end. The stiles
    hang `clear` mm outboard of the outer edge of the cleat on top of partition B. Rungs are evenly spaced.
    """
    x_end, y, z_top = at
    L, W, s = prm["length"], prm["width"], prm["stile"]
    lean = math.radians(prm["lean_deg"])
    w = s / math.cos(lean)                      # horizontal width of a leaning square stile
    cleat_out = x_end + P.get("cleat_leg")      # outer edge of the cleat on partition B's top edge
    z_cleat = P.get("partition_b_h")            # top of that cleat
    # the stile's inner face clears the cleat edge by `clear` at the cleat's top level
    x_c = cleat_out + prm["clear"] + w / 2 - (z_top - z_cleat) * math.tan(lean)
    dx, dz = L * math.sin(lean), L * math.cos(lean)
    z_foot = z_top - dz
    parts = []
    for side in (1, -1):
        yc = y + side * (W / 2 - s / 2)
        side_view = [(x_c - w / 2, z_top), (x_c + w / 2, z_top), (x_c + dx + w / 2, z_foot), (x_c + dx - w / 2, z_foot)]
        parts.append(prism_xz(side_view, yc - s / 2, yc + s / 2))
        hw = prm["hook_w"] / 2
        parts.append(box_span(x_end - prm["hook_reach"], x_c + w / 2, yc - hw, yc + hw, z_top, z_top + prm["hook_t"]))
    n = int(prm["rungs"])
    for k in range(1, n + 1):
        f = k / (n + 1)
        cx, cz = x_c + dx * f, z_top - dz * f
        parts.append(cyl((cx, y - W / 2 + s, cz), (cx, y + W / 2 - s, cz), prm["rung_d"] / 2))
    return _fuse(parts), {"foot_z": z_foot, "foot_x": x_c + dx, "top_x": x_c, "length": L,
                          "lean_deg": prm["lean_deg"], "drop": dz}


def gen_net(prm, at, P):
    x, y, z = at
    L, H, t = prm["length"], prm["height"], prm["thickness"]
    return box_span(x, x + t, y, y + L, z, z + H), {}


def gen_ramp(prm, spec, P):
    L, W, T = prm["length"], prm["width"], prm["thickness"]
    drop = spec["drop"]
    a = math.degrees(math.asin(drop / L))
    s = Pos(spec["centre_x"], spec["sill_y"], 0) * Rot(-a, 0, 0) * box_span(-W / 2, W / 2, 0, L, -T, 0)
    return s, {"angle_deg": a, "run_mm": L * math.cos(math.radians(a))}


def gen_strap(prm, pts, P):
    segs = [strap_between(a, b, prm["width"], prm["thickness"]) for a, b in zip(pts, pts[1:])]
    length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    return _fuse(segs) if len(segs) > 1 else segs[0], {"strap_length_mm": length, "top": pts[1] if len(pts) == 4 else pts[0]}


# ------------------------------------------------------------------ context
def gen_floor(prm, at, P):
    t = prm["thickness"]
    hw, wt = P.get("half_width"), P.get("wall_t")
    x0, x1 = P.get("body_x0"), P.get("body_x1")
    s = box_span(x0, x1, -hw - wt, hw + wt, -t, 0)
    gl, tw, th = P.get("garage_length"), P.get("track_w"), P.get("track_h")
    for yr in (P.get("front_row_y"), P.get("rear_row_y")):
        s = s - box_span(0, gl, yr - tw / 2, yr + tw / 2, -th, 1)
    return s, {}


def gen_wall(prm, at, P):
    t = prm["thickness"]
    hw = P.get("half_width")
    x0, x1 = P.get("body_x0"), P.get("body_x1")
    zc = P.get("ceiling_z")
    if prm.get("side") == "road":
        s = box_span(x0, x1, -hw - t, -hw, 0, zc)
    else:
        s = box_span(x0, x1, hw, hw + t, 0, zc)
        if prm.get("opening"):
            s = s - box_span(P.get("door_x0"), P.get("door_x1"), hw - 1, hw + t + 1, -1, P.get("door_h"))
    return s, {}


GENERATORS = {
    "box": gen_box, "panel": gen_panel, "rhs": gen_rhs, "froli": gen_froli,
    "condor_chock": gen_condor_chock, "l_track": gen_l_track, "track_fitting": gen_track_fitting,
    "winch": gen_winch, "vent": gen_vent, "fume_sensor": gen_fume_sensor, "extinguisher": gen_extinguisher,
    "ladder": gen_ladder, "net": gen_net, "floor": gen_floor, "wall": gen_wall,
}

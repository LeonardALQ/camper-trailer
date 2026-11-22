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


def _face_x(shape, prm, at):
    """Generators that model an item against a wall facing +Y can turn it to face +X (a partition or end
    wall across the trailer): rotate -90 degrees about Z through `at`, so +Y becomes +X."""
    if prm.get("face") != "x":
        return shape
    x, y, z = at
    return Pos(x, y, z) * Rot(0, 0, -90) * Pos(-x, -y, -z) * shape


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
    normal = prm.get("normal", "x")
    if prm.get("crown") and normal == "z":
        # a sheet across the box crowned to its centre line: it rises `crown` there and falls to both edges
        c = prm["crown"]
        s = prism_yz([(y0, z0), (y0 + dy / 2, z0 + c), (y0 + dy, z0), (y0 + dy, z0 + dz), (y0 + dy / 2, z0 + c + dz), (y0, z0 + dz)],
                     x0, x0 + dx)
    else:
        s = box(x0, y0, z0, dx, dy, dz)
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
    """Hollow section from `at` (its underside centre line start). It runs along X, or along Y with axis: y."""
    L, H, W, t, r = prm["length"], prm["height"], prm["width"], prm["wall"], prm.get("outer_radius", 0)
    outer = RectangleRounded(W, H, r) if r > 0 else Rectangle(W, H)
    inner = RectangleRounded(W - 2 * t, H - 2 * t, r - t) if r - t > 0.2 else Rectangle(W - 2 * t, H - 2 * t)
    prof = outer - inner
    if prm.get("axis") == "y":
        pl = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        s = Pos(at[0], at[1], at[2] + H / 2) * extrude(pl * prof, amount=L)
    else:
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
    """40x40x3 ledger with its vertical leg hanging below a shelf whose top is `top_z`. On partition A or the
    rear wall it runs across the trailer, on a side wall along it."""
    leg, t = prm["leg"], prm["thickness"]
    top = spec["top_z"]
    L = spec["length"]
    hw = P.get("half_width")
    gl = P.get("garage_length")
    w = spec["wall"]
    if w in ("partition_a", "rear"):
        x0, s = (0.0, 1) if w == "partition_a" else (gl, -1)
        prof = [(x0, top - leg), (x0 + s * t, top - leg), (x0 + s * t, top - t), (x0 + s * leg, top - t), (x0 + s * leg, top), (x0, top)]
        if s < 0:
            prof = prof[::-1]
        shape = prism_xz(prof, -hw, -hw + L)
    else:
        y0, s = (hw, -1) if w == "road" else (-hw, 1)
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
        # cradle plate and cheeks (the tyre sits on the plate, top at the cradle rise). The cheeks stand on the plate's
        # edges, welded along them, so the cradle is one part (decision H27)
        box_span(x - 70, x + 70, y + 60, y + 480, z + rise - 6, z + rise),
        box_span(x - 70, x - 64, y + 200, y + 480, z + rise, z + rise + 120),
        box_span(x + 64, x + 70, y + 200, y + 480, z + rise, z + rise + 120),
    ]
    yh = y + 12.5
    for s in (1, -1):
        parts.append(cyl((x + s * 90, yh, z + 30), (x + s * 90, yh, z + H - 12.5), 12.5))
        parts.append(cyl((x + s * 90, yh, z + 300), (x + s * (W / 2 - 12.5), y + 330, z + 30), 10))
    parts.append(cyl((x - 102.5, yh, z + H - 12.5), (x + 102.5, yh, z + H - 12.5), 12.5))
    return _face_x(_fuse(parts), prm, at), {}


def gen_l_track(prm, at, P):
    """Track from `at` along X, or along Y with axis: y (a row across the trailer)."""
    L = prm["length"]
    W, H = prm["width"], prm["height"]
    x, y, z = at
    sw = prm["slot_w"] / 2
    if prm.get("axis") == "y":
        s = box_span(x - W / 2, x + W / 2, y, y + L, z, z + H)
        s = s - box_span(x - sw, x + sw, y - 1, y + L + 1, z + H - prm["slot_d"], z + H + 1)
    else:
        s = box_span(x, x + L, y - W / 2, y + W / 2, z, z + H)
        s = s - box_span(x - 1, x + L + 1, y - sw, y + sw, z + H - prm["slot_d"], z + H + 1)
    return s, {"length_m": L / 1000}


def gen_track_fitting(prm, at, P):
    """Double-stud fitting, its length along the track (X, or Y with axis: y)."""
    x, y, z = at
    l, w, h = prm["length"], prm["width"], prm["height"]
    base = box_span(x - l / 2, x + l / 2, y - w / 2, y + w / 2, z, z + h * 0.45)
    ring = Pos(x, y, z + h * 0.45) * Rot(0, 90, 0) * (Cylinder(h * 0.55, 8) - Cylinder(h * 0.3, 10))
    ring = ring - box_span(x - 20, x + 20, y - 20, y + 20, z - 30, z + h * 0.45)
    s = base + ring
    if prm.get("axis") == "y":
        s = Pos(x, y, z) * Rot(0, 0, 90) * Pos(-x, -y, -z) * s
    return s, {}


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
    return _face_x(_fuse(parts), prm, at), {}


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
    (`stile` mm, the SHS 25x1.6 envelope) lean `lean_deg` from vertical into the living area, which lies
    towards `dir` (-1 is towards -X, in front of partition A in revision D). Each stile is `length` mm along
    its axis between level-cut ends, with its top end at the deck-top level. A hook bar on each stile lies on
    the deck top from `hook_reach` mm inboard of the deck end. The stiles hang `clear` mm outboard of the outer
    edge of the cleat on top of the partition. Rungs are evenly spaced.
    """
    x_end, y, z_top = at
    sx = prm.get("dir", 1)
    L, W, s = prm["length"], prm["width"], prm["stile"]
    lean = math.radians(prm["lean_deg"])
    w = s / math.cos(lean)                      # horizontal width of a leaning square stile
    cleat_out = x_end + sx * P.get("cleat_leg")  # outer edge of the cleat on the partition's top edge
    z_cleat = P.get("partition_a_h")            # top of that cleat
    # the stile's inner face clears the cleat edge by `clear` at the cleat's top level
    x_c = cleat_out + sx * (prm["clear"] + w / 2 - (z_top - z_cleat) * math.tan(lean))
    dx, dz = sx * L * math.sin(lean), L * math.cos(lean)
    z_foot = z_top - dz
    parts = []
    for side in (1, -1):
        yc = y + side * (W / 2 - s / 2)
        side_view = [(x_c - w / 2, z_top), (x_c + w / 2, z_top), (x_c + dx + w / 2, z_foot), (x_c + dx - w / 2, z_foot)]
        parts.append(prism_xz(side_view, yc - s / 2, yc + s / 2))
        hw = prm["hook_w"] / 2
        parts.append(box_span(x_end - sx * prm["hook_reach"], x_c + sx * w / 2, yc - hw, yc + hw, z_top, z_top + prm["hook_t"]))
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
    """Ramp deployed from the sill, running down along +X from `sill_x` (the rear door, revision D) on the
    line Y `centre_y`."""
    L, W, T = prm["length"], prm["width"], prm["thickness"]
    drop = spec["drop"]
    a = math.degrees(math.asin(drop / L))
    place = Pos(spec["sill_x"], spec["centre_y"], 0) * Rot(0, a, 0)
    s = place * box_span(0, L, -W / 2, W / 2, -T, 0)
    # its top end bevelled to stand against the sill, and its foot cut level where it lies on the ground
    x0, cy = spec["sill_x"], spec["centre_y"]
    s = s - box_span(x0 - 500, x0, cy - W, cy + W, -drop - 500, 500) - box_span(x0, x0 + L + 500, cy - W, cy + W, -drop - 500, -drop)
    if prm.get("hook_l"):
        # the hooks at the top end: a plate on the floor inside the sill, bent down onto the ramp's top face
        hl, hw, ht = prm["hook_l"], prm["hook_w"], prm["hook_t"]
        for yo in (W / 2 - hw / 2 - 40, -(W / 2 - hw / 2 - 40)):
            s = s + box_span(x0 - hl, x0 + 10, cy + yo - hw / 2, cy + yo + hw / 2, 0, ht)
            s = s + place * box_span(0, 70, yo - hw / 2, yo + hw / 2, 0, ht)
    return s, {"angle_deg": a, "run_mm": L * math.cos(math.radians(a))}


def gen_strap(prm, pts, P):
    """A ratchet strap through its points, with a snap hook through the track fitting's ring at each anchor: the last
    point, and the first too for a strap round a rear wheel (four points)."""
    segs = [strap_between(a, b, prm["width"], prm["thickness"]) for a, b in zip(pts, pts[1:])]
    for x, y, z in [pts[-1]] + ([pts[0]] if len(pts) == 4 else []):
        segs.append(box_span(x - 6, x + 6, y - 10, y + 10, z - 12, z + 4))
    length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    return _fuse(segs), {"strap_length_mm": length, "top": pts[1] if len(pts) == 4 else pts[0]}


# ------------------------------------------------------------------ context
def gen_floor(prm, at, P):
    """Garage floor with a recess under each track row: the rows across the trailer at front_row_x and
    rear_row_x, and the stowage row along the kerb strip."""
    t = prm["thickness"]
    hw, wt = P.get("half_width"), P.get("wall_t")
    x0, x1 = P.get("body_x0"), P.get("garage_length")
    s = box_span(x0, x1, -hw - wt, hw + wt, -t, 0)
    tw, th = P.get("track_w"), P.get("track_h")
    for xr, y0 in ((P.get("front_row_x"), -hw), (P.get("rear_row_x"), P.get("rear_row_y0"))):
        s = s - box_span(xr - tw / 2, xr + tw / 2, y0, hw, -th, 1)
    ys = P.get("stow_row_y")
    s = s - box_span(P.get("stow_row_x0"), P.get("stow_row_x1"), ys - tw / 2, ys + tw / 2, -th, 1)
    return s, {}


def gen_wall(prm, at, P):
    """Body walls round the garage: the side walls (the kerb one with the gas locker hatch opening) and the
    rear wall with the garage door opening."""
    t = prm["thickness"]
    hw = P.get("half_width")
    x0, x1 = P.get("body_x0"), P.get("garage_length")
    zc = P.get("ceiling_z")
    side = prm.get("side")
    if side == "road":
        s = box_span(x0, x1, hw, hw + t, 0, zc)
    elif side == "kerb":
        s = box_span(x0, x1, -hw - t, -hw, 0, zc)
        if prm.get("opening"):
            s = s - box_span(P.get("hatch_x0"), P.get("hatch_x1"), -hw - t - 1, -hw + 1, P.get("hatch_z0"), P.get("hatch_z1"))
    else:
        s = box_span(x1, x1 + t, -hw - t, hw + t, 0, zc)
        s = s - box_span(x1 - 1, x1 + t + 1, P.get("door_y0"), P.get("door_y1"), -1, P.get("door_h"))
    return s, {}


def gen_sweep(prm, at, P):
    """The rear wall's frame round the door opening, extended forward over the whole garage length. A bike
    rolled straight back along X passes the frame if it clears this solid (check only)."""
    hw = P.get("half_width")
    x1 = P.get("garage_length") + P.get("wall_t")
    s = box_span(0, x1, -hw, hw, 0, P.get("ceiling_z"))
    s = s - box_span(-1, x1 + 1, P.get("door_y0"), P.get("door_y1"), -1, P.get("door_h"))
    return s, {}


# ------------------------------------------------------------------ the ute garage (UTE-GARAGE.md)
def gen_tube(prm, at, P):
    """Hollow section given by its outside extent: `at` is the low corner, dx, dy, dz the outside sizes. It runs
    along its longest side, open at both ends, with walls `wall` thick. Per-length mass uses that length."""
    dx, dy, dz, t = prm["dx"], prm["dy"], prm["dz"], prm["wall"]
    x, y, z = at
    s = box(x, y, z, dx, dy, dz)
    L = max(dx, dy, dz)
    if L == dx:
        inner = box(x - 1, y + t, z + t, dx + 2, dy - 2 * t, dz - 2 * t)
    elif L == dy:
        inner = box(x + t, y - 1, z + t, dx - 2 * t, dy + 2, dz - 2 * t)
    else:
        inner = box(x + t, y + t, z - 1, dx - 2 * t, dy - 2 * t, dz + 2)
    s = s - inner
    if prm.get("crown") and L == dy:
        # a roof bow across the box: its top rises `crown` to the centre line and falls to both ends (the bike box's 1:50)
        c = prm["crown"]
        s = s + prism_yz([(y, z + dz), (y + dy / 2, z + dz + c), (y + dy, z + dz)], x, x + dx)
    return s, {"length_m": L / 1000}


def gen_tyre_sweep(prm, at, P):
    """The space a rear tyre sweeps from its static position up to full bump (check only): a cylinder across the
    ute at each end and the box between. `at` is the wheel centre at static."""
    x, y, z = at
    r, w, rise = prm["radius"], prm["width"], prm["rise"]
    a = cyl((x, y - w / 2, z), (x, y + w / 2, z), r)
    b = cyl((x, y - w / 2, z + rise), (x, y + w / 2, z + rise), r)
    return a + b + box_span(x - r, x + r, y - w / 2, y + w / 2, z, z + rise), {}


def gen_disc(prm, at, P):
    """A round item on a wall (the fan): a short cylinder whose axis is X, Y or Z."""
    x, y, z = at
    r, d = prm["diameter"] / 2, prm["depth"]
    ax = prm.get("axis", "x")
    e = {"x": (x + d, y, z), "y": (x, y + d, z), "z": (x, y, z + d)}[ax]
    return cyl((x, y, z), e, r), {}


GENERATORS = {
    "box": gen_box, "panel": gen_panel, "rhs": gen_rhs, "froli": gen_froli,
    "condor_chock": gen_condor_chock, "l_track": gen_l_track, "track_fitting": gen_track_fitting,
    "winch": gen_winch, "vent": gen_vent, "fume_sensor": gen_fume_sensor, "extinguisher": gen_extinguisher,
    "ladder": gen_ladder, "net": gen_net, "floor": gen_floor, "wall": gen_wall, "sweep": gen_sweep,
    "tube": gen_tube, "tyre_sweep": gen_tyre_sweep, "disc": gen_disc,
}

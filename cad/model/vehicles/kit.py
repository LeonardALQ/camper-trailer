"""Shared shapes for the vehicle models: polygons, solids of revolution, round tubes along a path, and wheels with
their tyres.

A wheel or tyre is built about the Z axis through the origin with its outer face towards +Z and its local +X pointing
at the ground, and `on_axle` sets it on its axle. mm throughout.
"""
from __future__ import annotations

import math
from functools import lru_cache

from build123d import Axis, Face, Plane, Pos, Rot, Solid, Vector, Wire, extrude, revolve

from ..prims import box_span, cyl


def face(pts):
    """Planar face through 3D points."""
    return Face(Wire.make_polygon([Vector(*p) for p in pts], close=True))


def lathe(rz, arc=360.0):
    """Solid of revolution about Z from (radius, z) pairs."""
    return revolve(face([(r, 0.0, z) for r, z in rz]), Axis.Z, arc)


def ball(p, r):
    return Pos(*p) * Solid.make_sphere(r)


def fuse(parts):
    parts = [p for p in parts if p is not None]
    return parts[0].fuse(*parts[1:]) if len(parts) > 1 else parts[0]


def tube(points, r, round_ends=False):
    """Round bar through the points, with a ball at every bend so that the segments join."""
    segs = [cyl(a, b, r) for a, b in zip(points, points[1:]) if math.dist(a, b) > 0.5]
    joints = [ball(p, r) for p in (points if round_ends else points[1:-1])]
    return fuse(segs + joints)


def on_axle(shape, centre, outward):
    """Set a wheel built about Z on its axle at `centre`, its outer face looking along `outward`, local +X down."""
    return Plane(origin=centre, x_dir=(0, 0, -1), z_dir=outward) * shape


def ring(r0, r1, z0, z1):
    """Flat annulus about Z."""
    return lathe([(r0, z0), (r1, z0), (r1, z1), (r0, z1)])


def _ellipse_crown(rim_r, rc, w, bead_w, n=10):
    """(r, z) outline of a tyre's carcass: bead on the rim, sidewalls to the widest point, round crown to radius rc."""
    h = rc - rim_r
    r0 = rim_r + 0.45 * h
    a, b = rc - r0, w / 2
    pts = [(rim_r - 3, -bead_w / 2), (r0 - 0.25 * h, -0.9 * b)]
    pts += [(r0 + a * math.cos(-math.pi / 2 + math.pi * k / n), b * math.sin(-math.pi / 2 + math.pi * k / n)) for k in range(n + 1)]
    pts += [(r0 - 0.25 * h, 0.9 * b), (rim_r - 3, bead_w / 2)]
    return pts, (r0, a, b)


def _crown_r(r0, a, b, z):
    """Radius of the elliptic crown at axial position z."""
    return r0 + a * math.sqrt(max(0.0, 1 - (z / b) ** 2))


def _block(r_in, r_out, z0, z1, half_deg, at_deg):
    """A tread block between two radii and two axial planes, spanning +/-half_deg about the angle at_deg. Its outer face
    reaches r_out at its middle and at both ends."""
    h = math.radians(half_deg)
    pts = [(r_in * math.cos(-h), r_in * math.sin(-h)), (r_out * math.cos(-h), r_out * math.sin(-h)), (r_out, 0.0),
           (r_out * math.cos(h), r_out * math.sin(h)), (r_in * math.cos(h), r_in * math.sin(h))]
    f = face([(x, y, z0) for x, y in pts])
    return Rot(0, 0, at_deg) * extrude(f, amount=z1 - z0, dir=(0, 0, 1))


@lru_cache(maxsize=None)
def moto_tyre(D, W, rim_r, bead_w, knob=0.0, n=40):
    """Motorcycle tyre: a round-crowned carcass seated on the rim, with knobs on its crown when `knob` is set. A knob
    sits at the bottom, so the tyre stands on one, and the knob tops reach the tyre's overall diameter."""
    R = D / 2
    pts, (r0, a, b) = _ellipse_crown(rim_r, R - knob, W, bead_w)
    carcass = lathe(pts)
    if not knob:
        return carcass
    pitch = 360.0 / n
    blocks = []
    for k in range(n):
        ang = k * pitch
        blocks.append(_block(R - knob - 3, R, -0.17 * W, 0.17 * W, 0.28 * pitch, ang))
        for s in (1, -1):
            zc = s * 0.6 * b
            ro = _crown_r(r0, a, b, abs(zc)) + knob
            z0, z1 = sorted((s * 0.42 * b, s * 0.86 * b))
            blocks.append(_block(ro - knob - 6, ro, z0, z1, 0.22 * pitch, ang + pitch / 2))
    return fuse([carcass] + blocks)


@lru_cache(maxsize=None)
def road_tyre(D, W, rim_r, bead_w):
    """Road tyre: the carcass to the full diameter with two shallow grooves cut round its crown."""
    R = D / 2
    pts, _ = _ellipse_crown(rim_r, R, W, bead_w)
    t = lathe(pts)
    grooves = [ring(R - 4, R + 2, z - 3, z + 3) for z in (-0.22 * W, 0.22 * W)]
    return t.cut(*grooves)


@lru_cache(maxsize=None)
def moto_rim(rim_r, width, flange=9.0, depth=16.0):
    """Motorcycle rim: a drop-centre channel with a flange each side."""
    w = width / 2
    return lathe([(rim_r - depth, -w + 6), (rim_r - depth, w - 6), (rim_r - 4, w), (rim_r + flange, w),
                  (rim_r + flange, w - 4), (rim_r, w - 6), (rim_r, -w + 6), (rim_r + flange, -w + 4),
                  (rim_r + flange, -w), (rim_r - 4, -w)])


def _spoke_phase(p0, p1, r):
    """Angle (degrees) at which the segment p0-p1 crosses radius r in the wheel plane."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        x, y = p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1])
        if math.hypot(x, y) < r:
            lo = t
        else:
            hi = t
    return math.degrees(math.atan2(y, x))


@lru_cache(maxsize=None)
def spoked_wheel(rim_r, rim_w, hub_r, hub_w, flange_r, n=36, spoke_r=2.2, cross_deg=24.0, down_r=0.0):
    """Wire wheel: rim, hub with a spoke flange each side, and n tangential spokes. With down_r set, one spoke from
    each flange crosses that radius straight below the axle, where a strap through the wheel bears on them."""
    rim = moto_rim(rim_r, rim_w)
    hub = fuse([cyl((0, 0, -hub_w / 2), (0, 0, hub_w / 2), hub_r),
                ring(hub_r - 2, flange_r, hub_w / 2 - 14, hub_w / 2 - 8), ring(hub_r - 2, flange_r, -hub_w / 2 + 8, -hub_w / 2 + 14)])
    ri = rim_r - 15
    spokes = []
    per = n // 2
    for side in (1, -1):
        zf, zr = side * (hub_w / 2 - 11), side * 3.0
        base = []
        for k in range(per):
            a0 = 360.0 * k / per + (180.0 / per if side < 0 else 0.0)
            a1 = a0 + (cross_deg if k % 2 == 0 else -cross_deg)
            base.append(((flange_r * math.cos(math.radians(a0)), flange_r * math.sin(math.radians(a0)), zf),
                         (ri * math.cos(math.radians(a1)), ri * math.sin(math.radians(a1)), zr)))
        turn = -_spoke_phase(base[0][0], base[0][1], down_r) if down_r else 0.0
        for p0, p1 in base:
            spokes.append(Rot(0, 0, turn) * cyl(p0, p1, spoke_r))
    return fuse([rim, hub] + spokes)


@lru_cache(maxsize=None)
def cast_wheel(rim_r, rim_w, hub_r, hub_w, pairs=5, spoke_w=13.0, spread_deg=11.0):
    """Cast wheel: rim, hub and `pairs` split spokes, one pair either side of the bottom."""
    rim = moto_rim(rim_r, rim_w)
    hub = cyl((0, 0, -hub_w / 2), (0, 0, hub_w / 2), hub_r)
    ri = rim_r - 14
    arms = []
    for k in range(pairs):
        a = 360.0 * k / pairs
        for s in (1, -1):
            p0 = (hub_r - 4, 0.0)
            p1 = (ri * math.cos(math.radians(s * spread_deg)), ri * math.sin(math.radians(s * spread_deg)))
            d = (p1[0] - p0[0], p1[1] - p0[1])
            L = math.hypot(*d)
            n_ = (-d[1] / L * spoke_w / 2, d[0] / L * spoke_w / 2)
            prof = [(p0[0] + n_[0], p0[1] + n_[1]), (p1[0] + n_[0], p1[1] + n_[1]), (p1[0] - n_[0], p1[1] - n_[1]),
                    (p0[0] - n_[0], p0[1] - n_[1])]
            arm = extrude(face([(x, y, -9.0) for x, y in prof]), amount=18.0, dir=(0, 0, 1))
            arms.append(Rot(0, 0, a) * arm)
    return fuse([rim, hub] + arms)


def disc(r_out, r_in, z, t=5.0):
    """Brake disc at axial position z on a hub."""
    return ring(r_in, r_out, z - t / 2, z + t / 2)


def slab(x0, x1, y0, y1, z0, z1):
    return box_span(x0, x1, y0, y1, z0, z1)

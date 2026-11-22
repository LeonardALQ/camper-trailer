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


SWEEP = [True]          # tube() sweeps round bends; straight() turns it off for the drawings, whose hidden-line removal
                        # is slow on swept surfaces


class straight:
    """Within `with straight():` every tube is straight cylinders end to end, for the drawings."""

    def __enter__(self):
        SWEEP.append(False)

    def __exit__(self, *exc):
        SWEEP.pop()


def tube(points, r, round_ends=False):
    """Round bar through the points: a circle swept along the polyline with round bends, as a bent tube is. If OCCT
    cannot sweep the path, the bar is straight segments with a ball at every bend, the balls 5 % larger than the bar so
    that they cut it cleanly instead of meeting it tangentially. Inside `straight()` it is the straight segments alone."""
    pts = [points[0]] + [p for a, p in zip(points, points[1:]) if math.dist(a, p) > 0.5]
    if not SWEEP[-1]:
        return fuse([cyl(a, b, r) for a, b in zip(pts, pts[1:])])
    if len(pts) > 2:
        try:
            from build123d import Circle, Transition, sweep
            path = Wire.make_polygon([Vector(*p) for p in pts], close=False)
            prof = Plane(origin=pts[0], z_dir=Vector(*pts[1]) - Vector(*pts[0])) * Circle(r)
            s = sweep(prof, path=path, transition=Transition.ROUND)
            solids = s.solids()
            if len(solids) == 1 and solids[0].is_valid and solids[0].volume > 0:
                return solids[0]
        except Exception:
            pass
    segs = [cyl(a, b, r) for a, b in zip(pts, pts[1:])]
    joints = [ball(p, 1.05 * r) for p in (pts if round_ends else pts[1:-1])]
    return fuse(segs + joints)


def stick(p0, p1, w):
    """Square bar w wide from p0 to p1, for spokes: twelve triangles in the viewer where a round bar needs a hundred."""
    from build123d import Box
    a, b = Vector(*p0), Vector(*p1)
    d = b - a
    return Plane(origin=a, z_dir=d) * Pos(0, 0, d.length / 2) * Box(w, w, d.length)


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


def tread_ring(r_root, r_tip, z0, z1, n, duty=0.5, phase=0.0):
    """A ring of n tread blocks round the Z axis: a toothed outline between r_root and r_tip, extruded from z0 to z1. One
    block is centred on +X when phase is 0, the direction on_axle turns to the ground, so the tyre stands on a block.
    Each block's top is two flats that reach r_tip at its middle and at both ends. The root lies inside the carcass."""
    half = math.pi * duty / n
    pts = []
    for k in range(n):
        c = 2 * math.pi * k / n + math.radians(phase)
        for r, a in ((r_root, c - half), (r_tip, c - half), (r_tip, c), (r_tip, c + half), (r_root, c + half)):
            pts.append((r * math.cos(a), r * math.sin(a), z0))
    return extrude(face(pts), amount=z1 - z0, dir=(0, 0, 1))


@lru_cache(maxsize=None)
def moto_tyre(D, W, rim_r, bead_w, knob=0.0, n=40):
    """Motorcycle tyre: a round-crowned carcass seated on the rim, with knobs on its crown when `knob` is set: a centre row
    and a shoulder row each side, half a pitch round from it. The centre row's tops reach the tyre's overall diameter,
    and a centre knob sits at the bottom, so the tyre stands on one. The tyre is a compound of the carcass and its three
    rows of knobs, which keeps it light to tessellate and to measure."""
    R = D / 2
    pts, (r0, a, b) = _ellipse_crown(rim_r, R - knob, W, bead_w)
    carcass = lathe(pts)
    if not knob:
        return carcass
    from build123d import Compound
    rows = [tread_ring(_crown_r(r0, a, b, 0.17 * W) - 3, R, -0.17 * W, 0.17 * W, n, 0.56)]
    for s in (1, -1):
        z0, z1 = sorted((s * 0.42 * b, s * 0.86 * b))
        r_out, r_in = _crown_r(r0, a, b, 0.86 * b), _crown_r(r0, a, b, 0.42 * b)
        rows.append(tread_ring(r_out - 4, r_in + knob, z0, z1, n, 0.44, 180.0 / n))
    return Compound([carcass] + rows)


@lru_cache(maxsize=None)
def truck_tyre(D, W, rim_r, bead_w, depth=13.0, n=36, tread=True):
    """Light-truck all-terrain tyre: a square-shouldered carcass with its sidewalls, and five rows of tread blocks, the
    two inner rows and the centre row staggered half a pitch, and shoulder rows that run down onto the sidewall. The
    tread tops reach the overall diameter and a block sits at the bottom. A compound of the carcass and its rows, or with
    tread=False the carcass alone, for the drawings."""
    from build123d import Compound
    R = D / 2
    rc = R - depth                       # carcass at the tread's base
    h = rc - rim_r
    w, bw = W / 2, bead_w / 2
    prof = [(rim_r - 3, -(bw - 10)), (rim_r + 20, -(bw + 6)), (rim_r + 0.45 * h, -w), (rc - 22, -w), (rc - 4, -w + 14), (rc, -w + 40),
            (rc, w - 40), (rc - 4, w - 14), (rc - 22, w), (rim_r + 0.45 * h, w), (rim_r + 20, bw + 6), (rim_r - 3, bw - 10)]
    carcass = lathe(prof)
    if not tread:
        return carcass
    rows = [tread_ring(rc - 3, R, -0.06 * W, 0.06 * W, n, 0.55)]
    for s in (1, -1):
        z0, z1 = sorted((s * 0.09 * W, s * 0.27 * W))
        rows.append(tread_ring(rc - 3, R, z0, z1, n, 0.62, 180.0 / n))
        z0, z1 = sorted((s * 0.30 * W, s * (w - 6)))
        rows.append(tread_ring(rc - 26, R - 3, z0, z1, n, 0.5, 0.0))
    return Compound([carcass] + rows)


@lru_cache(maxsize=None)
def steel_wheel(rim_r, width, windows=8, studs=5, pcd=150.0, bore=110.0, offset=0.0):
    """Steel sunraysia wheel (ROH Trak 2): a rolled rim with its bead seats, flanges and drop centre, and a pressed centre
    disc with `windows` triangular windows, the stud holes on the pitch circle and the centre bore, its mounting face at
    `offset` from the rim's centre plane. Built about Z, +Z the wheel's outer face."""
    w = width / 2
    t = 4.0
    rim = lathe([(rim_r - 2, -w), (rim_r + 17, -w - 3), (rim_r + 17, -w + 3), (rim_r + 2, -w + 6), (rim_r + 2, -w + 30),
                 (rim_r - 22, -w + 48), (rim_r - 22, w - 48), (rim_r + 2, w - 30), (rim_r + 2, w - 6), (rim_r + 17, w - 3),
                 (rim_r + 17, w + 3), (rim_r - 2, w), (rim_r - 2, w - 28), (rim_r - 22 - t, w - 46), (rim_r - 22 - t, -w + 46),
                 (rim_r - 2, -w + 28)])
    z0 = offset
    disc = lathe([(bore / 2, z0), (pcd / 2 + 32, z0), (pcd / 2 + 60, z0 + 22), (rim_r - 40, z0 + 26), (rim_r - 22, z0 + 26),
                  (rim_r - 22, z0 + 26 - t), (rim_r - 40, z0 + 26 - t), (pcd / 2 + 58, z0 + 22 - t), (pcd / 2 + 30, z0 - t),
                  (bore / 2, z0 - t)])
    cuts = []
    r0, r1 = pcd / 2 + 52, rim_r - 46
    for k in range(windows):
        c = 2 * math.pi * (k + 0.5) / windows
        a0, a1 = math.pi / windows * 0.62, math.pi / windows * 0.30
        tri = [(r0 * math.cos(c), r0 * math.sin(c), z0 - 20), (r1 * math.cos(c - a0), r1 * math.sin(c - a0), z0 - 20),
               (r1 * math.cos(c + a0), r1 * math.sin(c + a0), z0 - 20)]
        cuts.append(extrude(face(tri), amount=70, dir=(0, 0, 1)))
    for k in range(studs):
        a = 2 * math.pi * k / studs
        cuts.append(cyl((pcd / 2 * math.cos(a), pcd / 2 * math.sin(a), z0 - 20), (pcd / 2 * math.cos(a), pcd / 2 * math.sin(a), z0 + 20), 11))
    disc = disc.cut(*cuts)
    return rim.fuse(disc)


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
def spoked_wheel(rim_r, rim_w, hub_r, hub_w, flange_r, n=36, spoke_w=4.0, cross_deg=24.0, down_r=0.0):
    """Wire wheel: rim, hub with a spoke flange each side, and n tangential spokes, each running from inside its flange
    into the rim. With down_r set, one spoke from each flange crosses that radius straight below the axle, where a strap
    through the wheel bears on them. A compound of the rim, the hub and the spokes, which are not fused: fusing them
    cuts every spoke's outline into the rim and the flanges and makes the wheel several times heavier to draw."""
    from build123d import Compound
    rim = moto_rim(rim_r, rim_w)
    hub = fuse([cyl((0, 0, -hub_w / 2), (0, 0, hub_w / 2), hub_r),
                ring(hub_r - 2, flange_r, hub_w / 2 - 14, hub_w / 2 - 8), ring(hub_r - 2, flange_r, -hub_w / 2 + 8, -hub_w / 2 + 14)])
    ri, rf = rim_r - 13, flange_r - 4
    spokes = []
    per = n // 2
    for side in (1, -1):
        zf, zr = side * (hub_w / 2 - 11), side * 3.0
        base = []
        for k in range(per):
            a0 = 360.0 * k / per + (180.0 / per if side < 0 else 0.0)
            a1 = a0 + (cross_deg if k % 2 == 0 else -cross_deg)
            base.append(((rf * math.cos(math.radians(a0)), rf * math.sin(math.radians(a0)), zf),
                         (ri * math.cos(math.radians(a1)), ri * math.sin(math.radians(a1)), zr)))
        turn = -_spoke_phase(base[0][0], base[0][1], down_r) if down_r else 0.0
        for p0, p1 in base:
            spokes.append(Rot(0, 0, turn) * stick(p0, p1, spoke_w))
    return Compound([rim, hub] + spokes)


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

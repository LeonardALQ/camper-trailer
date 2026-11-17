"""Small geometry helpers on top of build123d, in the module frame (X along, Y across, Z up)."""
from __future__ import annotations

import math

from build123d import (
    Box, Color, Compound, Cylinder, Plane, Polygon, Pos, Rot, Solid, Torus, Vector, extrude,
)


def rgba(hex_color: str, alpha: float = 1.0) -> Color:
    h = hex_color.lstrip("#")
    return Color(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, alpha)


def box(x0, y0, z0, dx, dy, dz):
    """Axis-aligned box from its minimum corner."""
    return Pos(x0 + dx / 2, y0 + dy / 2, z0 + dz / 2) * Box(dx, dy, dz)


def box_span(x0, x1, y0, y1, z0, z1):
    return box(min(x0, x1), min(y0, y1), min(z0, z1), abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))


def cyl(p1, p2, r):
    """Solid cylinder of radius r from point p1 to point p2."""
    a, b = Vector(*p1), Vector(*p2)
    d = b - a
    return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d))


def prism_yz(pts_yz, x0, x1):
    """Polygon in the Y-Z plane (as (y, z) pairs) extruded along X from x0 to x1."""
    face = Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * Polygon(*pts_yz, align=None)
    return extrude(face, amount=x1 - x0, dir=(1, 0, 0))


def prism_xy(pts_xy, z0, z1):
    """Polygon in plan (as (x, y) pairs) extruded along Z from z0 to z1."""
    face = Plane(origin=(0, 0, z0), x_dir=(1, 0, 0), z_dir=(0, 0, 1)) * Polygon(*pts_xy, align=None)
    return extrude(face, amount=z1 - z0, dir=(0, 0, 1))


def prism_xz(pts_xz, y0, y1):
    """Polygon in the X-Z plane (as (x, z) pairs) extruded along Y from y0 to y1."""
    face = Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0)) * Polygon(*[(x, -z) for x, z in pts_xz], align=None)
    # Plane with z_dir +Y has y_dir = z x x = (0,0,-1), so local v = -Z. Flip z to keep (x, z) natural.
    return extrude(face, amount=y1 - y0, dir=(0, 1, 0))


def tyre_x_axis(cy, cz, diameter, width, rim_radius):
    """Motorcycle tyre with a round crown, axle along X, centred at (0, cy, cz)."""
    R = diameter / 2
    rc = R - width / 2
    shape = Torus(rc, width / 2)
    if rc > rim_radius + 1:
        shape = shape + (Cylinder(rc, width) - Cylinder(rim_radius, width))
    return Pos(0, cy, cz) * Rot(0, 90, 0) * shape


def disc_x_axis(cy, cz, radius, width):
    return Pos(0, cy, cz) * Rot(0, 90, 0) * Cylinder(radius, width)


def strap_between(p1, p2, width=35.0, thickness=3.0):
    """Thin flat strap from p1 to p2. Its wide face is kept as close to vertical-plane as possible."""
    a, b = Vector(*p1), Vector(*p2)
    d = b - a
    L = d.length
    z_dir = d.normalized()
    ref = Vector(0, 0, 1) if abs(z_dir.Z) < 0.95 else Vector(1, 0, 0)
    x_dir = ref.cross(z_dir).normalized()          # horizontal, across the strap
    pl = Plane(origin=a, x_dir=x_dir, z_dir=z_dir)
    return pl * Pos(0, 0, L / 2) * Box(width, thickness, L)


def compound(label, children):
    c = Compound(label=label, children=children)
    return c


def deg(rad):
    return rad * 180.0 / math.pi

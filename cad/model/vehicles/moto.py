"""Bike-frame helpers for the motorcycle models.

A bike is built in cad/model/bike.py's local frame: local X is the bike's y (to its right), local Y the bike's x
(rearward from the front axle) and local Z its z (up from the ground). These helpers take bike-frame points (x, y, z)
so that the builders read in the bike's own terms.
"""
from __future__ import annotations

import math

from ..prims import box_span, cyl, prism_xy, prism_yz
from . import kit


def P(x, y, z):
    return (y, x, z)


def side(pts_xz, y0, y1):
    """Side-profile prism: a polygon of (x, z) points extruded across the bike from y0 to y1."""
    return prism_yz(pts_xz, min(y0, y1), max(y0, y1))


def plan(pts_xy, z0, z1):
    """Plan prism: a polygon of (x, y) points extruded from z0 to z1."""
    return prism_xy([(y, x) for x, y in pts_xy], z0, z1)


def blk(x0, x1, y0, y1, z0, z1):
    return box_span(y0, y1, x0, x1, z0, z1)


def rod(p0, p1, r):
    return cyl(P(*p0), P(*p1), r)


def bar(points, r, round_ends=False):
    return kit.tube([P(*p) for p in points], r, round_ends)


def mirrored(fn):
    """The same part on both sides: fn(s) for s = +1 (right) and -1 (left), fused."""
    return kit.fuse([fn(1), fn(-1)])


def wheel(shape, x, z, right=True):
    """A wheel built about Z (cad/model/vehicles/kit.py), set on the axle at (x, z) with its +Z face to the bike's right."""
    return kit.on_axle(shape, P(x, 0, z), (1.0 if right else -1.0, 0.0, 0.0))


class Fork:
    """A telescopic fork's geometry in side view: legs through the axle along the rake, the steering axis `offset`
    behind them."""

    def __init__(self, axle_x, axle_z, rake_deg, offset):
        self.x, self.z = axle_x, axle_z
        r = math.radians(rake_deg)
        self.u = (math.sin(r), math.cos(r))        # up the legs
        self.n = (math.cos(r), -math.sin(r))       # rearward, square to the legs
        self.offset = offset

    def leg(self, s, back=0.0):
        """Point s along the leg axis from the axle, moved `back` square to it."""
        return (self.x + s * self.u[0] + back * self.n[0], self.z + s * self.u[1] + back * self.n[1])

    def axis(self, s, back=0.0):
        """Point on the steering axis level with leg point s."""
        return self.leg(s, self.offset + back)

    def clamp(self, s0, s1, front, rear, half_w):
        """Triple clamp between leg stations s0 and s1: from `front` ahead of the legs to `rear` behind the steering axis."""
        pts = [self.leg(s0, -front), self.leg(s1, -front), self.axis(s1, rear), self.axis(s0, rear)]
        return side(pts, -half_w, half_w)

    def tube(self, y, s0, s1, r):
        (x0, z0), (x1, z1) = self.leg(s0), self.leg(s1)
        return rod((x0, y, z0), (x1, y, z1), r)


def chain(c1, r1, c2, r2, y, width, t=7.0, n=12):
    """A chain loop in the plane y round two sprockets (x, z centres, pitch radii): its outer and inner hulls."""
    def hull(ra, rb):
        (xa, za), (xb, zb) = c1, c2
        d = math.hypot(xb - xa, zb - za)
        base = math.atan2(zb - za, xb - xa)
        phi = math.acos((ra - rb) / d)
        pts = []
        for k in range(n + 1):
            a = base + phi + (2 * math.pi - 2 * phi) * k / n
            pts.append((xa + ra * math.cos(a), za + ra * math.sin(a)))
        for k in range(n + 1):
            a = base - phi + 2 * phi * k / n
            pts.append((xb + rb * math.cos(a), zb + rb * math.sin(a)))
        return pts
    outer = side(hull(r1 + t / 2, r2 + t / 2), y - width / 2, y + width / 2)
    inner = side(hull(r1 - t / 2, r2 - t / 2), y - width, y + width)
    return outer.cut(inner)

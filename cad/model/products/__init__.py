"""Real product models for the trailer's 3D model (decision H27), one function per product, at the maker's published
dimensions with the features that make it recognisable (research report 28).

A line in data/assemblies/trailer.yaml picks its product with a `model:` key: the product's name, or a mapping with
`name` and options such as `front`, the face that looks into the cabin. A line that has only a mass point gives its
model an envelope with `box: [x0, y0, z0, dx, dy, dz]`, expressions over the layout's parameters. Chassis fittings take
their product from FITTING_MODELS. Every model stays inside its envelope within 1 mm (cad/tests/test_products.py). The
models are visual: the line's mass and centre of gravity stay the schedule's.

A product function takes a Frame on its envelope and the layout's values, and returns its pieces as
(label, shape, colour, alpha). The pieces' labels are plain words, so a pointer on any piece names the product's line.
"""
from __future__ import annotations

from build123d import Axis, Box, Compound, Plane, Pos, Solid, Vector, extrude, fillet

from ..prims import rgba

REGISTRY: dict = {}
# chassis fittings (data/chassis/chassis.yaml) by fitting id, and the product each one shows
FITTING_MODELS: dict[str, str] = {}

WHITE, GREY, DARK, BLACK, STEEL, ALU = "#f4f6f6", "#aab7b8", "#566573", "#1c2833", "#909497", "#c8cfd2"
GLASS, PLY, RUBBER, CHROME, BLUE = "#5dade2", "#d9c3a0", "#212f3c", "#dfe6e9", "#2e86c1"


def product(name: str):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


class Frame:
    """An envelope box (x0, y0, z0, x1, y1, z1) seen from its front: u runs from the viewer's left along the front face,
    v from the front face inward and w up from the base. `front` is the outward normal of the front face."""

    def __init__(self, bx, front: str = "-y"):
        self.bx, self.front = tuple(bx), front
        x0, y0, z0, x1, y1, z1 = bx
        self.H = z1 - z0
        if front in ("+y", "-y"):
            self.W, self.D = x1 - x0, y1 - y0
        else:
            self.W, self.D = y1 - y0, x1 - x0

    def pt(self, u, v, w) -> tuple:
        x0, y0, z0, x1, y1, z1 = self.bx
        f = self.front
        if f == "+y":
            return (x1 - u, y1 - v, z0 + w)
        if f == "-y":
            return (x0 + u, y0 + v, z0 + w)
        if f == "+x":
            return (x1 - v, y0 + u, z0 + w)
        return (x0 + v, y1 - u, z0 + w)

    def box(self, u0, v0, w0, du, dv, dw):
        a, b = self.pt(u0, v0, w0), self.pt(u0 + du, v0 + dv, w0 + dw)
        lo = [min(p, q) for p, q in zip(a, b)]
        size = [abs(p - q) for p, q in zip(a, b)]
        return Pos(lo[0] + size[0] / 2, lo[1] + size[1] / 2, lo[2] + size[2] / 2) * Box(*size)

    def rbox(self, u0, v0, w0, du, dv, dw, r, edges="w"):
        """A box with rounded edges: along w (upright edges), along v (front-to-back edges) or all."""
        s = self.box(u0, v0, w0, du, dv, dw)
        r = min(r, du / 2 - 0.1, dv / 2 - 0.1, dw / 2 - 0.1)
        if r <= 0.2:
            return s
        if edges == "all":
            return fillet(s.edges(), r)
        return fillet(s.edges().filter_by(self.axis(edges)), r)

    def axis(self, a: str):
        if a == "w":
            return Axis.Z
        along_y = self.front in ("+y", "-y")
        if a == "v":
            return Axis.Y if along_y else Axis.X
        return Axis.X if along_y else Axis.Y

    def cyl(self, p, q, r):
        """A cylinder of radius r between two frame points (u, v, w)."""
        a, b = Vector(*self.pt(*p)), Vector(*self.pt(*q))
        d = b - a
        return Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d))

    def cyl_v(self, u, w, r, v0, v1):
        return self.cyl((u, v0, w), (u, v1, w), r)

    def cyl_w(self, u, v, r, w0, w1):
        return self.cyl((u, v, w0), (u, v, w1), r)

    def cyl_u(self, v, w, r, u0, u1):
        return self.cyl((u0, v, w), (u1, v, w), r)

    def prism_vw(self, pts, u0, u1):
        """A polygon in the side view, (v, w) pairs, extruded across the width from u0 to u1."""
        a = [Vector(*self.pt(u0, v, w)) for v, w in pts]
        n = Vector(*self.pt(u1, 0, 0)) - Vector(*self.pt(u0, 0, 0))
        return extrude(_face(a), amount=n.length, dir=n.normalized())

    def prism_uv(self, pts, w0, w1):
        """A polygon in plan, (u, v) pairs, extruded up from w0 to w1."""
        a = [Vector(*self.pt(u, v, w0)) for u, v in pts]
        return extrude(_face(a), amount=w1 - w0, dir=(0, 0, 1))

    def prism_uw(self, pts, v0, v1):
        """A polygon in the front view, (u, w) pairs, extruded inward from v0 to v1."""
        a = [Vector(*self.pt(u, v0, w)) for u, w in pts]
        n = Vector(*self.pt(0, v1, 0)) - Vector(*self.pt(0, v0, 0))
        return extrude(_face(a), amount=n.length, dir=n.normalized())


def _face(pts):
    from build123d import Face, Wire
    return Face(Wire.make_polygon([tuple(p) for p in pts], close=True))


def spec_of(spec) -> dict:
    return {"name": spec} if isinstance(spec, str) else dict(spec)


def envelope(spec: dict, block, P) -> tuple:
    """The box a line's model must fit: its `box` under `model:` if it has one, else the line's own box."""
    if "box" in spec:
        x0, y0, z0, dx, dy, dz = P.eval(spec["box"], {})
        return (min(x0, x0 + dx), min(y0, y0 + dy), min(z0, z0 + dz), max(x0, x0 + dx), max(y0, y0 + dy), max(z0, z0 + dz))
    return tuple(block.box)


def build(spec, block, V: dict, bx: tuple, label: str, colour: tuple):
    """The product's pieces as one labelled compound: pointing at any piece names the line."""
    from . import catalogue  # noqa: F401  registers every product
    sp = spec_of(spec)
    fn = REGISTRY[sp["name"]]
    fr = Frame(bx, sp.get("front", "-y"))
    kids = []
    for name, shp, col, a in fn(fr, V, sp, block):
        s = shp
        s.label = name
        s.color = rgba(col, a)
        kids.append(s)
    out = Compound(label=label, children=kids)
    out.color = rgba(*colour)
    return out

"""Real product models for the trailer's 3D model (decision H27), one function per product, at the maker's published
dimensions with the features that make it recognisable (research report 28).

A line in data/assemblies/trailer.yaml picks its product with a `model:` key: the product's name, or a mapping with
`name` and options, such as `front`, the face that looks into the cabin (-y, +y, -x or +x). The options are
expressions over the layout's parameters and the line's loop values. A line that has only a mass point gives its model
an envelope with `box: [x0, y0, z0, dx, dy, dz]`. `extras` places more products for the same line, each with its own
envelope, where a line's parts stand in more than one place (the DauerShower's unit behind the partition and its panel
in the wet room), and a placement with a false `when` is left out. Chassis fittings take their product from
FITTING_MODELS. Every model stays inside its envelope within 1 mm (cad/tests/test_products.py). The models are
visual: the line's mass and centre of gravity stay the schedule's.

A product function takes a Frame on its envelope, the layout's values and its options, and returns its pieces as
(label, shape, colour, alpha). A piece's label is plain words, so a pointer on any piece names the product's line.
"""
from __future__ import annotations

import itertools

from build123d import Axis, Box, Compound, Face, Plane, Pos, Solid, Vector, Wire, extrude, fillet

from ..prims import rgba

REGISTRY: dict = {}
# chassis fittings (data/chassis/chassis.yaml) by fitting id, and the product each one shows
FITTING_MODELS: dict[str, dict] = {
    "CH-B01": {"name": "ark_steady"},
    "CH-B02": {"name": "d_ring"},
    "DB-05": {"name": "ark_xo750", "front": "+y"},
    "CH-P09": {"name": "spare_carrier", "front": "-x", "studs": 24, "cleat_u": 100},
}
RAW = ("name", "front", "when", "extras", "hub_side")

WHITE, GREY, DARK, BLACK, STEEL, ALU = "#f4f6f6", "#aab7b8", "#566573", "#1c2833", "#909497", "#c8cfd2"
GLASS, PLY, RUBBER, CHROME, BLUE = "#5dade2", "#d9c3a0", "#212f3c", "#dfe6e9", "#2e86c1"
DOOR = "#ecd9b6"


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

    def uv(self, x, y) -> tuple:
        """The frame's (u, v) of the plan point (x, y), as pt places them."""
        x0, y0, _, x1, y1, _ = self.bx
        f = self.front
        if f == "+y":
            return (x1 - x, y1 - y)
        if f == "-y":
            return (x - x0, y - y0)
        if f == "+x":
            return (y - y0, x1 - x)
        return (y1 - y, x - x0)

    def box(self, u0, v0, w0, du, dv, dw):
        a, b = self.pt(u0, v0, w0), self.pt(u0 + du, v0 + dv, w0 + dw)
        lo = [min(p, q) for p, q in zip(a, b)]
        size = [abs(p - q) for p, q in zip(a, b)]
        return Pos(lo[0] + size[0] / 2, lo[1] + size[1] / 2, lo[2] + size[2] / 2) * Box(*size)

    def rbox(self, u0, v0, w0, du, dv, dw, r, edges="w"):
        """A box with rounded edges along w (the upright edges), along v (front to back) or along u (across)."""
        s = self.box(u0, v0, w0, du, dv, dw)
        r = min(r, du / 2 - 0.1, dv / 2 - 0.1, dw / 2 - 0.1)
        if r <= 0.2:
            return s
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
    return Face(Wire.make_polygon([tuple(p) for p in pts], close=True))


def spec_of(spec) -> dict:
    return {"name": spec} if isinstance(spec, str) else dict(spec)


def loop_values(block, lay) -> dict:
    """The loop values (the line's `for`) of one instance of a line, from its instance number."""
    it = next((i for i in lay.td["items"] if i["id"] == block.id), None)
    loops = (it or {}).get("for") or {}
    if not loops or "." not in block.iid:
        return {}
    names = list(loops)
    combos = list(itertools.product(*[lay.P.eval(loops[n], {}) for n in names]))
    return dict(zip(names, combos[int(block.iid.rsplit(".", 1)[1]) - 1]))


def _box6(v) -> tuple:
    x0, y0, z0, dx, dy, dz = v
    return (min(x0, x0 + dx), min(y0, y0 + dy), min(z0, z0 + dz), max(x0, x0 + dx), max(y0, y0 + dy), max(z0, z0 + dz))


def placements(spec, block, lay) -> list[tuple[dict, tuple]]:
    """Each product the spec places, with its options evaluated and its envelope: the main one, then its `extras`.
    The main product's envelope is the line's box unless it gives its own `box`."""
    sp = spec_of(spec)
    local = loop_values(block, lay)
    out = []
    for n, p in enumerate([sp] + [spec_of(e) for e in sp.get("extras", [])]):
        if "when" in p and not lay.P.eval(p["when"], local):
            continue
        opts = {k: (v if k in RAW else lay.P.eval(v, local)) for k, v in p.items()}
        if "box" in opts:
            bx = _box6(opts["box"])
        elif n == 0 and block.box is not None:
            bx = tuple(block.box)
        else:
            raise ValueError(f"{block.iid}: the model {p['name']} needs a box")
        out.append((opts, bx))
    return out


def pieces(p: dict, bx: tuple, V: dict, block) -> list:
    """One product's pieces in its envelope, labelled and coloured."""
    from . import catalogue  # noqa: F401  registers every product
    front = p.get("front", "-y")
    if front == "in_y":                    # on a side wall, facing the centreline
        front = "-y" if (bx[1] + bx[4]) / 2 > 0 else "+y"
    fr = Frame(bx, front)
    kids = []
    for name, shp, col, a in REGISTRY[p["name"]](fr, V, p, block):
        shp.label, shp.color = name, rgba(col, a)
        kids.append(shp)
    return kids


def build(spec, block, lay, label: str, bx: tuple | None = None):
    """The product's pieces as one labelled compound, so pointing at any piece names the line, each piece in its own
    colour. None if nothing is placed. `bx` gives the envelope directly (a chassis fitting at one of its positions)."""
    if bx is not None:
        p = {k: (v if k in RAW else lay.P.eval(v, {})) for k, v in spec_of(spec).items()}
        kids = pieces(p, bx, lay.V, block)
    else:
        kids = [k for p, b in placements(spec, block, lay) for k in pieces(p, b, lay.V, block)]
    return Compound(label=label, children=kids) if kids else None

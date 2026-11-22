"""Bike models built from research/05-bike-geometry.yaml and data/parts/bikes.yaml.

The Aprilia Tuareg 660 Rally and the Triumph Street Triple 765 RS are product models (decision H27): their builders
are cad/model/vehicles/tuareg.py and street_triple.py, and research/29 lists every dimension and its source. Shapes are
built in a local frame: local X = bike y (bike's right), local Y = bike x (towards the bike's rear), local Z = z (up),
origin on the ground under the front axle. `place_bike` pitches the bike nose-up by the chock cradle rise (rotation
about the rear axle, so the rear tyre stays on the floor), then swaps local X and Y so that bike x runs along module X
and bike y along module Y (DESIGN.md revision D: the bikes stand along the box, noses towards its front wall), and moves
it to its bay. `place_on_slope` stands a bike on the ramp instead. 05 records y to the bike's left, so the models negate
every lateral value they read from 05.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from build123d import Compound, Plane, Pos, Rot, Vector, Vertex



def _v(d):
    """05 values are {v: ...}; return the number."""
    return d["v"] if isinstance(d, dict) else d


def _mid(v):
    return (v[0] + v[1]) / 2 if isinstance(v, (list, tuple)) else v


def _y05(y):
    """05 lateral value (y to the bike's left) in the model's bike frame (y to the bike's right)."""
    return -y


def P(x, y, z):
    """Bike frame (x rear, y right, z up) to the local module-aligned frame."""
    return (y, x, z)


@dataclass
class BikeModel:
    key: str
    solids: dict[str, object]                      # name -> solid, local frame
    tie_downs: dict[str, tuple[float, float, float]]  # bike-frame points (x, y, z); y is the + side
    com: tuple[float, float, float]                 # bike frame
    wheelbase: float
    front_axle: tuple[float, float]                 # (x, z) bike frame
    rear_axle: tuple[float, float]
    rear_rim_radius: float
    rear_tyre_width: float
    notes: list[str] = field(default_factory=list)
    colors: dict[str, str] = field(default_factory=dict)     # name -> hex colour of each solid
    fine: set[str] = field(default_factory=set)              # solids the drawings leave out (spokes, chain, discs)
    plain: dict[str, object] = field(default_factory=dict)   # plain tyres and wheels for the drawings
    hooks: dict[str, tuple[float, float, float]] = field(default_factory=dict)   # bike-frame points ropes attach to


def _builders():
    from .vehicles.street_triple import street_triple
    from .vehicles.tuareg import tuareg
    return {"tuareg_660_rally": tuareg, "street_triple_765": street_triple}


def build_bike(geo05: dict, prm: dict) -> BikeModel:
    key = prm["source_key"]
    return _builders()[key](geo05["bikes"][key], prm)


def xform(loc, p) -> Vector:
    """Apply a Location to a point."""
    return (loc * Vertex(*p)).center()


# Mirror plane X = Y: swaps local X (bike y) and local Y (bike x), so bike x runs along module X
SWAP = Plane(origin=(0, 0, 0), x_dir=(1, 1, 0), z_dir=(1, -1, 0))


@dataclass
class PlacedBike:
    model: BikeModel
    rot: object          # build123d Location: the chock pitch in the local frame
    move: object         # build123d Location: from the swapped frame to the bike's bay
    pitch_deg: float

    def point(self, x, y, z) -> Vector:
        """Bike-frame point to the module frame."""
        p = xform(self.rot, P(x, y, z))
        return xform(self.move, (p.Y, p.X, p.Z))

    def place(self, shape):
        """Local-frame solid to the module frame."""
        return self.move * (self.rot * shape).mirror(SWAP)


def place_bike(model: BikeModel, centre_y: float, front_tyre_x: float, front_overhang: float, front_rise: float) -> PlacedBike:
    """Pitch nose-up about the rear axle so the front tyre's lowest point rises by `front_rise`, then put the
    front axle at X = front_tyre_x + front_overhang (DESIGN.md) on the bike centreline Y = centre_y."""
    xf, zf = model.front_axle
    xr, zr = model.rear_axle
    L = xr - xf
    theta = math.degrees(math.asin(front_rise / L)) if front_rise else 0.0
    # rotation about the local X axis through the rear axle; negative angle lifts points with smaller Y (the front)
    rot = Pos(0, xr, zr) * Rot(-theta, 0, 0) * Pos(0, -xr, -zr)
    fa = xform(rot, (0, xf, zf))
    move = Pos(front_tyre_x + front_overhang - fa.Y, centre_y - fa.X, 0)
    return PlacedBike(model, rot, move, theta)


def place_on_slope(model: BikeModel, centre_y: float, contact_x: float, contact_z: float, slope_deg: float) -> PlacedBike:
    """Stand the bike on a slope that rises towards -X, the ramp up into the box: pitch it nose-up by slope_deg about the
    ground point under its front axle, where its front tyre touches the ground, and put that point at
    (contact_x, centre_y, contact_z). Both tyres then touch the slope."""
    rot = Rot(-slope_deg, 0, 0)
    move = Pos(contact_x, centre_y, contact_z)
    return PlacedBike(model, rot, move, slope_deg)


def bike_compound(pb: PlacedBike, label: str, plain: bool = False):
    """The placed bike, one child per named solid in its own colour. With plain=True, the drawings' version: plain
    tyres and wheels, and none of the fine parts."""
    from .prims import rgba
    children = []
    m_ = pb.model
    for name, s in m_.solids.items():
        if plain and name in m_.fine and name not in m_.plain:
            continue
        m = pb.place(m_.plain[name] if plain and name in m_.plain else s)
        m.label = name
        if name in m_.colors:
            m.color = rgba(m_.colors[name])
        children.append(m)
    return Compound(label=label, children=children)

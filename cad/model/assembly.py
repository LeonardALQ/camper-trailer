"""Build every placed instance of the garage and bed module from the data."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from build123d import Compound

from ..partsdb import Instance, Project
from . import generators as G
from .bike import PlacedBike, bike_compound, build_bike, place_bike, xform
from .prims import rgba

GROUP_LABELS = {
    "bikes": "Bikes", "restraint": "Restraint", "bed": "Bed", "partitions": "Partitions",
    "safety": "Garage safety", "context": "Context",
}


@dataclass
class Built:
    inst: Instance
    shape: object
    info: dict = field(default_factory=dict)
    bike: PlacedBike | None = None
    cog_override: tuple[float, float, float] | None = None

    @property
    def name(self) -> str:
        return f"{self.inst.iid} {self.inst.part}"


class Model:
    def __init__(self, prj: Project, include_check_only: bool = True, only: set[str] | None = None):
        self.prj = prj
        self.P = prj.P
        self.built: dict[str, Built] = {}
        self.timings: dict[str, float] = {}
        t0 = time.time()
        geo05 = prj.bike_geometry
        # bikes first, the straps hang off them
        def wanted(inst):
            if inst.check_only and not include_check_only:
                return False
            return only is None or inst.ref in only or inst.iid in only
        for inst in prj.instances:
            if "bike" in inst.special and (wanted(inst) or only is not None and inst.ref in ("TU", "ST")):
                self.built[inst.iid] = self._bike(inst, geo05)
        for inst in prj.instances:
            if inst.iid in self.built or not wanted(inst):
                continue
            self.built[inst.iid] = self._one(inst)
        for b in self.built.values():
            part = prj.parts[b.inst.part]
            b.shape.label = b.name
            b.shape.color = rgba(part.color, part.alpha)
        self.timings["build_s"] = round(time.time() - t0, 3)

    # ------------------------------------------------------------------
    def _bike(self, inst: Instance, geo05) -> Built:
        part = self.prj.parts[inst.part]
        prm = dict(part.geometry.params)
        sp = inst.special["bike"]
        for k in ("length", "screen_top_z"):
            if k in sp:
                prm[k] = sp[k]
        model = build_bike(geo05, prm)
        pb = place_bike(model, sp["centre_x"], sp["front_tyre_y"], prm["front_overhang"], sp["front_rise"])
        if sp.get("luggage_only"):
            # check-only copy that holds just the luggage, for checks that must not see the bike itself
            model.solids = {k: v for k, v in model.solids.items() if k.startswith("pannier")}
        comp = bike_compound(pb, f"{inst.iid} {inst.part}")
        cx, cy, cz = model.com
        c = pb.point(cx, cy, cz)
        own = [v for k, v in model.solids.items() if not k.startswith("pannier")] or list(model.solids.values())
        bb = Compound(children=own).bounding_box()
        info = {"pitch_deg": pb.pitch_deg,
                "local_size": {"length": bb.max.Y - bb.min.Y, "width": bb.max.X - bb.min.X, "height": bb.max.Z},
                "owner": prm["owner"], "length_param": prm.get("length", prm["owner"]["length"])}
        bags = [v for k, v in model.solids.items() if k.startswith("pannier")]
        if bags:
            bbb = Compound(children=bags).bounding_box()
            info["width_with_bags"] = max(bb.max.X, bbb.max.X) - min(bb.min.X, bbb.min.X)
        return Built(inst, comp, info, bike=pb, cog_override=(c.X, c.Y, c.Z))

    def _one(self, inst: Instance) -> Built:
        part = self.prj.parts[inst.part]
        prm = dict(inst.params)
        sp = inst.special
        gen = part.geometry.generator if part.geometry else None
        if "strap" in sp:
            pts = self._strap_points(sp["strap"])
            shape, info = G.gen_strap(prm, pts, self.P)
            info["points"] = [tuple(round(v, 1) for v in p) for p in pts]
            return Built(inst, shape, info)
        if "cleat" in sp:
            shape, info = G.gen_cleat(prm, sp["cleat"], self.P)
            return Built(inst, shape, info)
        if "ledger" in sp:
            shape, info = G.gen_ledger(prm, sp["ledger"], self.P)
            return Built(inst, shape, info)
        if "ramp" in sp:
            shape, info = G.gen_ramp(prm, sp["ramp"], self.P)
            cog = None
            if part.cog and part.cog.at:
                cog = tuple(self.P.eval(part.cog.at, {}))
            return Built(inst, shape, info, cog_override=cog)
        if gen not in G.GENERATORS:
            raise ValueError(f"{inst.iid}: no generator '{gen}'")
        shape, info = G.GENERATORS[gen](prm, inst.at, self.P)
        return Built(inst, shape, info)

    def _strap_points(self, s):
        pb = self.built[s["bike"]].bike
        m = pb.model
        if s["point"] == "rear_wheel":
            xr, zr = m.rear_axle
            yw = m.rear_tyre_width / 2 + 12
            zw = zr - 0.55 * m.rear_rim_radius
            a, b = s["anchors"]
            pl, pr = pb.point(xr, -yw, zw), pb.point(xr, yw, zw)
            return [tuple(a), (pl.X, pl.Y, pl.Z), (pr.X, pr.Y, pr.Z), tuple(b)]
        x, y, z = m.tie_downs[s["point"]]
        top = pb.point(x, s["side"] * y, z)
        return [(top.X, top.Y, top.Z), tuple(s["anchor"])]

    # ------------------------------------------------------------------
    def shapes(self, names: list[str]) -> list:
        return [self.built[i.iid].shape for i in self.prj.select(names) if i.iid in self.built]

    def compound_of(self, names: list[str]):
        return Compound(children=self.shapes(names))

    def grouped(self, predicate=lambda b: True, label: str | None = None):
        """Assembly tree: top compound with one sub-compound per group."""
        groups: dict[str, list] = {}
        for b in self.built.values():
            if predicate(b):
                groups.setdefault(b.inst.group, []).append(b.shape)
        kids = [Compound(label=GROUP_LABELS[g], children=v) for g, v in groups.items()]
        return Compound(label=label or f"{self.prj.assembly.id} {self.prj.assembly.name}", children=kids)

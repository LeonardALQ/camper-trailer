"""Whole-trailer block layout: placement, mass schedule, load cases, axle solve, checks and the body length
comparison (TRAILER.md).

Everything is in the project datum DIM-01 (research/02): X from the coupling ball centre, positive rearward,
Y from the centreline, positive to the road side, Z up from the ground at design ride height. Blocks are
axis-aligned boxes, wheels are cylinders and the drawbar members are bars between two points.

The garage and bed module is a sub-assembly at the back of the body (revision C). Its mass lines, the bikes and
their centres of gravity come from the module model (massprops), moved by (module_x0, 0, floor_z). The axle solve
moves the axle group and everything tied to it (the tanks, their guards and the suspension) along X until the
towball load meets the target. The ballast solve then finds the least ballast at the back of the garage that keeps
the cases without bikes at or under 280 kg on the ball. Neither changes a limit or a block size.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any

import yaml

from .partsdb import DATA, Mass, Params, Project

TRAILER_YAML = DATA / "assemblies" / "trailer.yaml"
GROWTH = {"estimate": 0.20, "calculated": 0.07, "spec": 0.0, "weighed": 0.0}
STAGE_IDS = {"drawbar_structure": ("DB-01", "DB-02", "DB-03", "DB-04"), "stowage": ("GS-01", "GS-02", "GS-05")}
SYSTEM_LABELS = {
    "drawbar": "Drawbar and coupling", "chassis": "Chassis", "running_gear": "Running gear", "body": "Body",
    "roof": "Roof", "underfloor": "Under the floor", "living": "Living area", "module": "Garage and bed module",
    "stowage": "Garage stowage", "spare": "Spare wheel", "payload": "Payload",
}
TOL = 0.5  # mm: boxes that only touch do not overlap


# ------------------------------------------------------------------ module data the layout needs
@dataclass
class ModuleInfo:
    """What the trailer needs from the garage and bed module, in the module frame."""
    lines: list[dict]                 # BOM lines with mass, maturity, CoG and the removable flag
    bikes: dict[str, dict]            # TU, ST: mass, CoG, source, maturity
    bags_cog: tuple[float, float, float]
    ladder_box: tuple[float, ...]     # x0, y0, z0, x1, y1, z1
    params: dict[str, Any]

    @classmethod
    def from_model(cls, prj: Project, model) -> "ModuleInfo":
        from . import massprops as MP
        lines = MP.line_masses(prj, model)
        bikes = {b["id"]: b for b in MP.bike_rows(prj, model)}
        bb = model.built["TU-BAGS"].shape.bounding_box()
        lb = model.built["18"].shape.bounding_box()
        return cls(lines=lines, bikes=bikes,
                   bags_cog=((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2),
                   ladder_box=(lb.min.X, lb.min.Y, lb.min.Z, lb.max.X, lb.max.Y, lb.max.Z),
                   params=dict(prj.P.values))

    def injected(self) -> dict[str, float]:
        tu, st = self.bikes["TU"], self.bikes["ST"]
        x = (tu["mass_kg"] * tu["cog"][0] + st["mass_kg"] * st["cog"][0]) / (tu["mass_kg"] + st["mass_kg"])
        out = {f"mod_{k}": v for k, v in self.params.items() if isinstance(v, float)}
        out.update(mod_bikes_cog_x=x, mod_ladder_x0=self.ladder_box[0], mod_ladder_w=self.ladder_box[4] - self.ladder_box[1])
        return out


# ------------------------------------------------------------------ blocks
@dataclass
class Block:
    iid: str
    id: str
    name: str
    system: str
    zone: str | None = None
    box: tuple[float, ...] | None = None       # x0, y0, z0, x1, y1, z1
    cyl: dict | None = None                    # c, r, w (axis along Y)
    bar: dict | None = None                    # p0, p1, w, h
    cog: tuple[float, float, float] | None = None
    mass_kg: float = 0.0
    maturity: str = "estimate"
    source: str = ""
    mass_note: str | None = None
    basis: str = "declared"
    unit_mass: float | None = None
    qty: float | None = None
    load: str = "tare"                         # tare, gas, fuel, gear, luggage, water, module, bike
    keep_clear: bool = False
    hollow: bool = False
    note: str | None = None
    removable: bool = False                     # module lines
    generated: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def growth(self) -> float:
        return GROWTH[self.maturity]

    @property
    def solid(self) -> bool:
        return self.box is not None and not self.keep_clear


def _box(x0, y0, z0, dx, dy, dz):
    return (min(x0, x0 + dx), min(y0, y0 + dy), min(z0, z0 + dz), max(x0, x0 + dx), max(y0, y0 + dy), max(z0, z0 + dz))


def _centre(b):
    return ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)


def overlap(a, b) -> float:
    """Overlap volume of two boxes (mm3), 0 if they only touch."""
    d = [min(a[i + 3], b[i + 3]) - max(a[i], b[i]) for i in range(3)]
    return 0.0 if min(d) <= TOL else d[0] * d[1] * d[2]


def gap(a, b) -> float:
    """Clear distance between two boxes, negative (the smallest penetration) if they overlap."""
    d = [max(a[i], b[i]) - min(a[i + 3], b[i + 3]) for i in range(3)]
    if max(d) > 0:
        return math.sqrt(sum(max(0.0, v) ** 2 for v in d))
    return max(d)


def inside(a, z) -> bool:
    return all(a[i] >= z[i] - TOL and a[i + 3] <= z[i + 3] + TOL for i in range(3))


# ------------------------------------------------------------------ layout
class Layout:
    """One evaluation of the block layout for a set of parameter values."""

    def __init__(self, td: dict, mod: ModuleInfo, prj: Project, overrides: dict | None = None):
        self.td, self.mod, self.prj = td, mod, prj
        raw = dict(td["params"])
        raw.update(mod.injected())
        for k, v in (overrides or {}).items():
            if k not in raw:
                raise KeyError(f"override of unknown trailer parameter {k}")
            raw[k] = v
        self.overrides = dict(overrides or {})
        self.P = Params(raw)
        self.V = self.P.values
        self.blocks: list[Block] = []
        for it in td["items"]:
            self.blocks.extend(self._expand(it))
        self.blocks.extend(self._crossmembers())
        self.blocks.extend(self._module_blocks())
        self.zones = {k: dict(name=z["name"], box=_box(*self.P.eval(z["box"], {}))) for k, z in td["zones"].items()}
        ids = [b.iid for b in self.blocks]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise ValueError(f"duplicate trailer block ids {sorted(dup)}")

    # -- expansion -------------------------------------------------------
    def _expand(self, it: dict) -> list[Block]:
        known = {"id", "name", "system", "zone", "for", "box", "cyl", "bar", "point", "cog", "mass", "note",
                 "load", "keep_clear", "hollow", "tank", "water", "module_cog"}
        extra = set(it) - known
        if extra:
            raise ValueError(f"trailer item {it.get('id')}: unknown keys {sorted(extra)}")
        mass = Mass.model_validate({k: v for k, v in it["mass"].items() if k != "measure"}) if "mass" in it else None
        loops = it.get("for") or {}
        names = list(loops)
        values = [self.P.eval(loops[n], {}) for n in names]
        combos = list(itertools.product(*values)) if names else [()]
        out = []
        for k, combo in enumerate(combos, 1):
            local = dict(zip(names, combo))
            iid = f"{it['id']}.{k}" if len(combos) > 1 else it["id"]
            b = Block(iid=iid, id=it["id"], name=it["name"], system=it["system"], zone=it.get("zone"),
                      load=it.get("load", "tare"), keep_clear=bool(it.get("keep_clear")), hollow=bool(it.get("hollow")),
                      note=it.get("note"))
            dims = {}
            if "box" in it:
                x0, y0, z0, dx, dy, dz = self.P.eval(it["box"], local)
                b.box = _box(x0, y0, z0, dx, dy, dz)
                dims = dict(dx=abs(dx), dy=abs(dy), dz=abs(dz))
            if "cyl" in it:
                c = self.P.eval(it["cyl"], local)
                b.cyl = dict(c=tuple(c["c"]), r=c["r"], w=c["w"])
                cx, cy, cz = c["c"]
                b.box = (cx - c["r"], cy - c["w"] / 2, cz - c["r"], cx + c["r"], cy + c["w"] / 2, cz + c["r"])
            if "bar" in it:
                br = self.P.eval(it["bar"], local)
                b.bar = dict(p0=tuple(br["p0"]), p1=tuple(br["p1"]), w=br["w"], h=br["h"])
                dims = dict(length=math.dist(br["p0"], br["p1"]))
            if "point" in it:
                b.cog = tuple(self.P.eval(it["point"], local))
            if "cog" in it:
                b.cog = tuple(self.P.eval(it["cog"], local))
            if b.cog is None and b.box is not None:
                b.cog = _centre(b.box)
            if b.bar is not None and b.cog is None:
                b.cog = tuple((p + q) / 2 for p, q in zip(b.bar["p0"], b.bar["p1"]))
            if it.get("module_cog"):
                cx, cy, cz = self.mod.bags_cog
                b.cog = (cx + self.V["module_x0"], cy, cz + self.V["floor_z"])
            if it.get("tank"):
                b.extra["tank"] = True
            if it.get("water"):
                b.load = "water"
            if mass is not None:
                self._mass(b, mass, it, dims, local)
            out.append(b)
        return out

    def _mass(self, b: Block, m: Mass, it: dict, dims: dict, local: dict):
        b.maturity, b.source, b.mass_note, b.basis = m.maturity, m.source, m.note, m.basis
        if m.basis == "declared":
            b.mass_kg = m.unit_kg if m.unit_kg is not None else m.total_kg
            b.unit_mass, b.qty = m.unit_kg, 1
        else:
            meas = it["mass"].get("measure")
            if meas is not None:
                v = self.P.eval(meas, {**local, **dims})
            elif "length" in dims:
                v = dims["length"]
            else:
                raise ValueError(f"{b.iid}: per-length or per-area mass needs `measure`")
            if m.basis == "per_length":
                b.qty, b.unit_mass = v / 1000, m.kg_per_m
            else:
                b.qty, b.unit_mass = v / 1e6, m.kg_per_m2
            b.mass_kg = b.qty * b.unit_mass

    def _crossmembers(self) -> list[Block]:
        """Fixed crossmembers, intermediate ones at no more than xm_max_pitch, and outriggers at the same
        stations wherever the tyres are not."""
        cm = self.td["crossmembers"]
        V = self.V
        w = V["xm_w"]
        fixed = [dict(id=f["id"], x=self.P.eval(f["x"], {}), section=f["section"]) for f in cm["fixed"]]
        fixed.sort(key=lambda f: f["x"])
        keep_out = {tuple(k) for k in cm["keep_out"]}
        stations = []
        for a, b in zip(fixed, fixed[1:]):
            stations.append(a)
            if (a["id"], b["id"]) in keep_out:
                continue
            span = b["x"] - (a["x"] + w)
            n = math.ceil(span / V["xm_max_pitch"]) - 1 if span > V["xm_max_pitch"] else 0
            for k in range(1, n + 1):
                stations.append(dict(id=f"between {a['id']} and {b['id']} ({k})", x=a["x"] + w + span * k / (n + 1) - w / 2,
                                     section="body", generated=True))
        stations.append(fixed[-1])
        out = []
        rin, rail_out = V["rail_in"], V["rail_outer_w"] / 2
        z0, z1 = V["rail_underside_z"], V["rail_top_z"]
        tyres = [b for b in self.blocks if b.id == "RG-02"]
        ok = cm["outrigger"]["tyre_keep_out"]
        for k, s in enumerate(stations, 1):
            sec = cm["sections"][s["section"]]
            b = Block(iid=f"CM-{k:02d}", id="CM", name=f"Crossmember, {s['id']}", system="chassis",
                      box=(s["x"], -rin, z0, s["x"] + w, rin, z1), generated=s.get("generated", False),
                      note=sec["name"] + (". PLACEHOLDER station from the pitch rule" if s.get("generated") else ""))
            b.cog = _centre(b.box)
            b.maturity, b.source, b.basis = sec["maturity"], sec["source"], "per_length"
            b.qty, b.unit_mass = 2 * rin / 1000, sec["kg_per_m"]
            b.mass_kg = b.qty * b.unit_mass
            b.extra["station"] = s["id"]
            out.append(b)
            # outriggers, both sides, at the raiser level, unless a tyre's swept space is there
            if s["x"] + w < V["body_x0"] or s["x"] > V["body_x1"]:
                continue
            clash = any(s["x"] - ok < t.box[3] and s["x"] + w + ok > t.box[0] for t in tyres)
            if clash:
                continue
            osec = cm["outrigger"]
            for side in (1, -1):
                ys = sorted((side * rail_out, side * V["half_bw"]))
                o = Block(iid=f"OR-{k:02d}{'R' if side > 0 else 'K'}", id="OR", name=f"Outrigger, {s['id']}, {'road' if side > 0 else 'kerb'} side",
                          system="chassis", box=(s["x"], ys[0], z1, s["x"] + w, ys[1], V["floor_underside_z"]),
                          generated=True, note=osec["name"])
                o.cog = _centre(o.box)
                o.maturity, o.source, o.basis = osec["maturity"], osec["source"], "per_length"
                o.qty, o.unit_mass = (ys[1] - ys[0]) / 1000, osec["kg_per_m"]
                o.mass_kg = o.qty * o.unit_mass
                out.append(o)
        return out

    def _module_blocks(self) -> list[Block]:
        """The module's BOM lines and bikes as mass lines in the datum, plus its envelope and ladder for the fit checks."""
        dx, dz = self.V["module_x0"], self.V["floor_z"]
        out = []
        for r in self.mod.lines:
            c = r["cog"]
            out.append(Block(iid=f"GB {r['id']}", id=r["id"], name=r["item"], system="module", load="module",
                             cog=(c[0] + dx, c[1], c[2] + dz), mass_kg=r["mass_kg"], maturity=r["maturity"],
                             source=r["source"], basis=r["basis"], unit_mass=r["unit_mass"], qty=r["qty"],
                             removable=r["removable"]))
        for ref, b in self.mod.bikes.items():
            c = b["cog"]
            out.append(Block(iid=f"GB {ref}", id=b["part"], name=b["item"], system="module", load="bike",
                             cog=(c[0] + dx, c[1], c[2] + dz), mass_kg=b["mass_kg"], maturity=b["maturity"],
                             source=b["source"], extra=dict(bike=ref)))
        lb = self.mod.ladder_box
        out.append(Block(iid="GB ladder", id="A-01", name="Ladder (module item 18), envelope for the fit check",
                         system="module", load="none", box=(lb[0] + dx, lb[1], lb[2] + dz, lb[3] + dx, lb[4], lb[5] + dz)))
        P = self.mod.params
        out.append(Block(iid="GB envelope", id="ASM-GB", name="Garage and bed module, partition A to partition B",
                         system="module", load="none",
                         box=(dx - P["partition_t"], -P["half_width"], dz, dx + P["garage_length"] + P["partition_t"], P["half_width"],
                              dz + P["ceiling_z"]), hollow=True))
        return out

    def apply_weighed(self, stages: list[dict]) -> list[dict]:
        """Scale the built parts of each weighed stage to its weighbridge figure (report 02 MASS-07)."""
        out = []
        for st in stages:
            lines = [b for b in self.blocks if b.load in ("tare", "module") and b.mass_kg > 0 and _stage_of(b) in st["stage"]]
            model = sum(b.mass_kg for b in lines)
            f = st["mass_kg"] / model if model else 1.0
            for b in lines:
                b.mass_kg *= f
                b.maturity = "weighed"
            out.append(dict(id=st["id"], model_kg=model, weighed_kg=st["mass_kg"], difference_pct=100 * (f - 1)))
        return out

    # -- views of the layout ---------------------------------------------
    def find(self, iid) -> Block:
        return next(b for b in self.blocks if b.iid == iid)

    def tanks(self) -> list[Block]:
        return [b for b in self.blocks if b.extra.get("tank")]

    def tank_capacity_l(self) -> float:
        return sum((t.box[3] - t.box[0]) * (t.box[4] - t.box[1]) * (t.box[5] - t.box[2]) for t in self.tanks()) / 1e6

    def water_cog(self, litres: float):
        ts = self.tanks()
        area = sum((t.box[3] - t.box[0]) * (t.box[4] - t.box[1]) for t in ts)
        h = litres * 1e6 / area if area else 0
        x = sum((t.box[3] - t.box[0]) * (t.box[4] - t.box[1]) * _centre(t.box)[0] for t in ts) / area
        y = sum((t.box[3] - t.box[0]) * (t.box[4] - t.box[1]) * _centre(t.box)[1] for t in ts) / area
        return (x, y, ts[0].box[2] + h / 2)

    def zone_lengths(self) -> dict:
        V = self.V
        return dict(living=V["part_a_x"] - V["in_x0"], interior=V["in_x1"] - V["in_x0"],
                    garage=V["in_x1"] - V["module_x0"], garage_with_partition=V["in_x1"] - V["part_a_x"])

    # -- mass and load cases ---------------------------------------------
    def case_lines(self, case) -> list[tuple[Block, float]]:
        """(block, mass) aboard in a load case."""
        water = self.P.eval(case.water_l, {})
        out = []
        for b in self.blocks:
            if b.load == "none" or b.keep_clear:
                continue
            if b.load == "tare":
                out.append((b, b.mass_kg))
            elif b.load == "module":
                if case.module == "all" or not b.removable:
                    out.append((b, b.mass_kg))
            elif b.load == "bike":
                if b.extra["bike"] in case.bikes:
                    out.append((b, b.mass_kg))
            elif b.load == "water":
                if water > 0:
                    w = Block(**{**b.__dict__, "cog": self.water_cog(water), "mass_kg": water})
                    out.append((w, water))
            elif b.load == "ballast":
                if case.ballast and self.V["ballast_kg"] > 0:
                    out.append((b, self.V["ballast_kg"]))
            elif b.load == "luggage":
                if "luggage" in case.load and "TU" in case.bikes:
                    out.append((b, b.mass_kg))
            elif b.load in case.load:
                out.append((b, b.mass_kg))
        return out

    def evaluate_case(self, case, car: dict | None = None) -> dict:
        xa = self.V["axle_x"]
        res = {}
        for basis in ("nominal", "growth"):
            items = [(m * (1 + b.growth) if basis == "growth" else m, b.cog) for b, m in self.case_lines(case)]
            M = sum(m for m, _ in items)
            cog = [sum(m * c[i] for m, c in items) / M for i in range(3)]
            ball = sum(m * (xa - c[0]) for m, c in items) / xa
            axle = M - ball
            res[basis] = dict(mass_kg=M, cog=cog, towball_kg=ball, towball_pct=100 * ball / M, axle_kg=axle,
                              tyre_load_kg=1.2 * axle / 4)
        water = self.P.eval(case.water_l, {})
        return dict(id=case.id, name=case.name, aboard=case.aboard, water_l=water, **res)

    # -- geometry checks ------------------------------------------------------
    def fit(self, zone: str, skip: tuple = ()) -> dict:
        z = self.zones[zone]["box"]
        items = [b for b in self.blocks if b.zone == zone and b.box is not None and b.id not in skip]
        solids = [b for b in items if not b.keep_clear]
        keep = [b for b in items if b.keep_clear]
        others = [b for b in self.blocks if b.solid and not b.hollow and b.zone != zone and overlap(b.box, z) > 0]
        problems, worst = [], math.inf
        worst_pair = ""
        for b in solids:
            if not inside(b.box, z):
                problems.append(f"{b.name} ({b.iid}) is outside the zone")
        pool = [b for b in solids if not b.hollow] + others
        for i, a in enumerate(pool):
            for b in pool[i + 1:]:
                if a.zone != zone and b.zone != zone:
                    continue
                g = gap(a.box, b.box)
                if g < worst:
                    worst, worst_pair = g, f"{a.name} to {b.name}"
                if overlap(a.box, b.box) > 0:
                    problems.append(f"{a.name} ({a.iid}) overlaps {b.name} ({b.iid}) by {-g:.0f} mm")
        for k in keep:
            for b in pool:
                if overlap(k.box, b.box) > 0:
                    problems.append(f"{b.name} ({b.iid}) stands in the {k.name.lower()} ({k.iid}) by {-gap(k.box, b.box):.0f} mm")
        return dict(ok=not problems, problems=problems, smallest_gap_mm=None if worst == math.inf else round(worst, 1),
                    governing=worst_pair, items=len(solids), keep_clear=len(keep))

    def tyre_envelopes(self) -> list[tuple[Block, tuple]]:
        V = self.V
        out = []
        for t in self.blocks:
            if t.id != "RG-02":
                continue
            cx, cy, cz = t.cyl["c"]
            r, w = t.cyl["r"], t.cyl["w"]
            out.append((t, (cx - r, cy - w / 2, 0.0, cx + r, cy + w / 2, cz + V["bump_travel"] + r)))
        return out

    def tyre_check(self) -> dict:
        worst, who = math.inf, ""
        for t, env in self.tyre_envelopes():
            for b in self.blocks:
                if not b.solid or b.system in ("running_gear",) or b.hollow:
                    continue
                g = gap(env, b.box)
                if g < worst:
                    worst, who = g, f"{t.name} ({t.iid}) at full bump to {b.name} ({b.iid})"
        return dict(gap_mm=worst, governing=who)

    def width(self) -> dict:
        ys = [(b.box[1], b.box[4], b) for b in self.blocks if b.solid]
        lo = min(ys, key=lambda t: t[0])
        hi = max(ys, key=lambda t: t[1])
        return dict(width_mm=hi[1] - lo[0], road=hi[2].name, kerb=lo[2].name)

    def ground_clearance(self) -> dict:
        cand = [b for b in self.blocks if b.solid and b.system in ("drawbar", "chassis", "underfloor", "body")]
        low = min(cand, key=lambda b: b.box[2])
        return dict(z_mm=low.box[2], governing=f"{low.name} ({low.iid})")

    def overall(self) -> dict:
        sol = [b for b in self.blocks if b.solid]
        return dict(x0=min(b.box[0] for b in sol), x1=max(b.box[3] for b in sol), z1=max(b.box[5] for b in sol))

    # -- jack-knife (plan view about the ball) ---------------------------------
    def plan_polys(self) -> dict[str, list[list[tuple[float, float]]]]:
        V = self.V
        out = {"body": [[(V["body_x0"], -V["half_bw"]), (V["body_x1"], -V["half_bw"]), (V["body_x1"], V["half_bw"]), (V["body_x0"], V["half_bw"])]]}
        mem = []
        for b in self.blocks:
            if b.bar:
                (x0, y0, _), (x1, y1, _) = b.bar["p0"], b.bar["p1"]
                L = math.hypot(x1 - x0, y1 - y0)
                nx, ny = -(y1 - y0) / L * b.bar["w"] / 2, (x1 - x0) / L * b.bar["w"] / 2
                mem.append([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
        out["drawbar members"] = mem
        sg = self.find("DB-04").box
        out["stone guard"] = [[(sg[0], sg[1]), (sg[3], sg[1]), (sg[3], sg[4]), (sg[0], sg[4])]]
        sp = [b.box for b in self.blocks if b.system == "spare" and b.box is not None]
        out["spare wheel"] = [[(min(b[0] for b in sp), min(b[1] for b in sp)), (max(b[3] for b in sp), min(b[1] for b in sp)),
                               (max(b[3] for b in sp), max(b[4] for b in sp)), (min(b[0] for b in sp), max(b[4] for b in sp))]]
        return out

    def jackknife(self, car: dict) -> dict:
        half = car["body_width_mm"]["v"] / 2
        res = {}
        for a in car["ball_behind_axle_mm"]["v"]:
            c = a - car["rear_overhang_mm"]["v"]  # ball to the rear bumper face
            rect = [(-c - 5000, -half), (-c, -half), (-c, half), (-c - 5000, half)]
            rows = {}
            for name, polys in self.plan_polys().items():
                d90 = min(_poly_dist(_rot(p, 90), rect) for p in polys)
                first = None
                for k in range(0, 181):
                    th = k * 0.5
                    if min(_poly_dist(_rot(p, th), rect) for p in polys) <= 0:
                        first = th
                        break
                rows[name] = dict(clearance_90_mm=d90, first_contact_deg=first)
            res[f"{a:.0f}"] = dict(ball_to_bumper_mm=c, parts=rows)
        return res


def _stage_of(b: Block) -> str:
    for k, ids in STAGE_IDS.items():
        if b.id in ids:
            return k
    return b.system


def _rot(poly, deg):
    t = math.radians(deg)
    return [(x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)) for x, y in poly]


def _seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _overlaps(P, Q):
    """Separating-axis test for two convex polygons."""
    for poly in (P, Q):
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            nx, ny = y1 - y2, x2 - x1
            a = [nx * x + ny * y for x, y in P]
            b = [nx * x + ny * y for x, y in Q]
            if max(a) <= min(b) or max(b) <= min(a):
                return False
    return True


def _poly_dist(P, Q) -> float:
    """Clear distance between convex polygons, 0 if they touch or overlap."""
    if _overlaps(P, Q):
        return 0.0
    d = math.inf
    for A, B in ((P, Q), (Q, P)):
        for p in A:
            for i in range(len(B)):
                d = min(d, _seg_dist(p, B[i], B[(i + 1) % len(B)]))
    return d


# ------------------------------------------------------------------ the car (report 07 load budget)
def car_axles(car: dict, towball_kg: float, ball_behind_axle_mm: float | None = None) -> dict:
    v = lambda k: car[k]["v"]  # noqa: E731
    bu = {k: d["v"] for k, d in car["budget"].items()}
    L = v("wheelbase_mm")
    a = ball_behind_axle_mm if ball_behind_axle_mm is not None else bu["ball_behind_axle_mm"]
    kerb = v("kerb_kg")
    rear = kerb * (1 - bu["front_share_of_kerb"])
    front = kerb * bu["front_share_of_kerb"]
    spare = bu.get("spare_kg", 0.0)
    for m, x in ((bu["occupants_kg"], bu["occupants_behind_front_axle_mm"]), (-bu["rear_seats_out_kg"], bu["gear_behind_front_axle_mm"]),
                 (bu["towbar_kg"], L + a), (towball_kg, L + a), (spare, L + bu.get("spare_behind_rear_axle_mm", 0.0))):
        rear += m * x / L
        front += m * (L - x) / L
    total = kerb + bu["occupants_kg"] - bu["rear_seats_out_kg"] + bu["towbar_kg"] + towball_kg + spare
    per_kg = bu["gear_behind_front_axle_mm"] / L
    by_axle = (v("rear_axle_limit_kg") - rear) / per_kg
    by_gvm = v("gvm_kg") - total
    return dict(rear_kg=rear, front_kg=front, car_kg=total, ball_behind_axle_mm=a,
                gear_budget_kg=min(by_axle, by_gvm), gear_by_rear_axle_kg=by_axle, gear_by_gvm_kg=by_gvm,
                binds="rear axle" if by_axle < by_gvm else "GVM")


# ------------------------------------------------------------------ the trailer: solve, cases, checks
class Trailer:
    def __init__(self, prj: Project, mod: ModuleInfo, overrides: dict | None = None):
        self.prj, self.mod = prj, mod
        self.td = yaml.safe_load(TRAILER_YAML.read_text())
        self.base = dict(overrides or {})
        self.cases = prj.load.trailer_cases
        self.reg = prj.load.registration
        inp = self.inputs = prj.inputs
        self.car = inp.car(prj.load.car)
        self.target, self.target_why = inp.towball_target(self.car, self.car["towball_rating_kg"]["v"])
        atm = self.car["braked_towing_kg"]["v"]
        self.supplier = inp.supplier(atm, self.target)
        self.wheel = inp.wheel(self.td["wheel"])
        self.base.setdefault("coupling_z", inp.coupling_z())
        offset = self.base.get("wheel_offset", self.td["params"]["wheel_offset"])
        self.base.setdefault("cf", inp.cf(offset, self.td["params"]["tyre_w"]))
        self.weighed = inp.weighed()
        self.weighed_rows: list[dict] = []
        self.target_case = next(c for c in self.cases if c.towball_target)

    def layout(self, **over) -> Layout:
        lay = Layout(self.td, self.mod, self.prj, {**self.base, **over})
        self.weighed_rows = lay.apply_weighed(self.weighed)
        return lay

    def caps(self) -> dict:
        r = {k: v["v"] for k, v in self.reg["ratings"].items()}
        gtm = min(r["tyre_kg"] * 4, r["coupling_kg"], r["chains_kg"], r["brakes_kg"])
        atm = min(r["coupling_kg"], r["chains_kg"])
        return dict(gtm=gtm, atm=atm, ratings=r)

    def _towball(self, **over) -> float:
        lay = self.layout(**over)
        return lay.evaluate_case(self.target_case)["nominal"]["towball_kg"]

    def _bisect(self, f, lo, hi, it=60):
        flo, fhi = f(lo), f(hi)
        if flo * fhi > 0:
            return None
        for _ in range(it):
            mid = (lo + hi) / 2
            fm = f(mid)
            if flo * fm <= 0:
                hi, fhi = mid, fm
            else:
                lo, flo = mid, fm
        return (lo + hi) / 2

    def zone_minimum(self, zone: str = "living", skip: tuple = ()) -> float:
        """Shortest living area (10 mm steps) at which its fit check passes, optionally without some items. The
        garage stays the same, so the length is found by moving partition A in a body of the same length."""
        V = self.layout().V
        pt = V["mod_partition_t"]
        for L in range(800, 5001, 10):
            if self.layout(module_x0=V["in_x0"] + L + pt).fit(zone, skip)["ok"]:
                return float(L)
        return math.inf

    def fit_options(self) -> list[dict]:
        """Living-area minimum for the layout as modelled and each option in fit_options, and what that leaves at
        each compared body length."""
        rows = []
        avail = {}
        for L in self.td["lengths_compared"]:
            V = Trailer(self.prj, self.mod, {**self.base, "body_length": L}).layout().V
            avail[L] = V["part_a_x"] - V["in_x0"]
        base = self.zone_minimum()
        for o in [dict(id="BASE", title="The layout as modelled", skip=[], overrides={}, mass_change_kg=0)] + (self.td.get("fit_options") or []):
            t = Trailer(self.prj, self.mod, {**self.base, **o.get("overrides", {})})
            m = t.zone_minimum("living", tuple(o.get("skip", [])))
            rows.append(dict(id=o["id"], title=o["title"], living_min_mm=m, saved_mm=base - m,
                             mass_change_kg=o.get("mass_change_kg", 0), mass_note=o.get("mass_note"),
                             slack_mm={str(L): a - m for L, a in avail.items()}))
        return rows

    def zone_costs(self) -> list[dict]:
        """For each item in the living area: how much shorter the living area could be without it."""
        lay = self.layout()
        rows = []
        base = self.zone_minimum()
        for iid in dict.fromkeys(b.id for b in lay.blocks if b.zone == "living"):
            b = next(x for x in lay.blocks if x.id == iid)
            saved = base - self.zone_minimum("living", (iid,))
            rows.append(dict(zone="living", id=iid, name=b.name, keep_clear=b.keep_clear, mass_kg=b.mass_kg,
                             zone_min_mm=base, saved_mm=saved))
        return rows

    def least_certain(self, ev: dict, n: int = 5) -> list[dict]:
        """The estimate lines with the largest growth allowance, and how far that allowance moves the fully loaded towball."""
        lay = ev["layout"]
        xa = lay.V["axle_x"]
        groups: dict[str, dict] = {}
        for b, m in lay.case_lines(self.target_case):
            if b.maturity != "estimate" or m <= 0:
                continue
            g = groups.setdefault(b.id, dict(id=b.id, name=b.name, mass_kg=0.0, moment=0.0, system=b.system, count=0))
            g["mass_kg"] += m
            g["moment"] += m * (xa - b.cog[0])
            g["count"] += 1
        rows = []
        for g in groups.values():
            allow = 0.2 * g["mass_kg"]
            rows.append(dict(id=g["id"], name=g["name"], system=g["system"], mass_kg=g["mass_kg"], count=g["count"],
                             growth_kg=allow, cog_x=xa - g["moment"] / g["mass_kg"],
                             towball_per_20pct_kg=0.2 * g["moment"] / xa))
        rows.sort(key=lambda r: -r["growth_kg"])
        return rows[:n]

    def solve(self) -> dict:
        """Axle position for the towball target. The garage sits at the back of the body (revision C), so only the
        axle group moves. VSB1 5.1.1 keeps the axle at or behind the middle of the body."""
        V = self.layout().V
        f = lambda x: self._towball(axle_x=x) - self.target  # noqa: E731
        xa = self._bisect(f, V["body_x0"] + 500, V["body_x1"] - 500)
        living_min = self.zone_minimum()
        living = V["part_a_x"] - V["in_x0"]
        out = dict(living_min_mm=living_min, living_mm=living, fits=living >= living_min - 1e-6)
        if xa is None:
            out.update(method="no solution", axle_x=None, overrides={}, notes=[])
            return out
        mid = V["body_x0"] + V["body_length"] / 2
        notes = []
        if xa < mid:
            notes.append(f"the towball target puts the axle {mid - xa:.0f} mm ahead of the middle of the body, so VSB1 5.1.1 holds it at the middle")
            xa = mid
        out.update(method="axle moved, garage at the rear", axle_x=xa, overrides=dict(axle_x=xa), notes=notes,
                   bikes_behind_axle_mm=V["module_x0"] + V["mod_bikes_cog_x"] - xa)
        return out

    def ballast(self, overrides: dict) -> dict:
        """Least ballast at the back of the garage that keeps every case marked `ballast` at or under the towball
        ceiling (MAS-03), on base weights and, for BAL-01, with growth. Ballast carries no growth allowance."""
        cap = next(c.max for c in self.prj.trailer_checks if c.id == "MAS-03")
        lay = self.layout(**overrides, ballast_kg=0)
        xa, xb = lay.V["axle_x"], lay.V["in_x1"] - lay.V["ballast_from_rear"]
        need = {}
        for c in self.cases:
            if not c.ballast:
                continue
            ev = lay.evaluate_case(c)
            need[c.id] = {b: max(0.0, (ev[b]["towball_kg"] - cap) * xa / (xb - xa)) for b in ("nominal", "growth")}
        base = max((n["nominal"] for n in need.values()), default=0.0)
        growth = max((n["growth"] for n in need.values()), default=0.0)
        return dict(kg=base, growth_kg=growth, x=xb, cap_kg=cap, per_case=need,
                    governing=max(need, key=lambda k: need[k]["nominal"]) if need else None,
                    governing_growth=max(need, key=lambda k: need[k]["growth"]) if need else None)

    def evaluate(self, solved: dict | None = None) -> dict:
        solved = solved or self.solve()
        bal = self.ballast(solved["overrides"])
        lay = self.layout(**solved["overrides"], ballast_kg=bal["kg"])
        cases = [lay.evaluate_case(c) for c in self.cases]
        self.ballast_result = bal
        checks = self.checks(lay, cases)
        return dict(layout=lay, solved=solved, cases=cases, checks=checks, ballast=bal)

    # -- checks ----------------------------------------------------------------
    def checks(self, lay: Layout, cases: list[dict]) -> list[dict]:
        out = []
        by_id = {c["id"]: c for c in cases}
        for c in self.prj.trailer_checks:
            row = dict(id=c.id, title=c.title, type=c.type, severity=c.severity, why=c.why, sub="")
            if c.type == "mass":
                ids = [x["id"] for x in cases] if c.cases == "all" else c.cases
                bases = ["nominal", "growth"] if c.basis == "both" else [c.basis]
                key = {"mass": "mass_kg", "axle": "axle_kg", "axle_vsb1": "axle_kg", "towball": "towball_kg",
                       "towball_pct": "towball_pct", "tyre_load": "tyre_load_kg"}[c.quantity]
                factor = 1.2 if c.quantity == "axle_vsb1" and not self.supplier["includes_120"] else 1.0
                unit = "%" if c.quantity == "towball_pct" else "kg"
                cmin, cmax = c.min, c.max
                caps = self.caps()
                if c.limit == "kit_gtm":
                    cmax = self.supplier["kit_gtm"]
                elif c.limit == "nsw_gtm_cap":
                    cmax = caps["gtm"]
                elif c.limit == "nsw_atm_cap":
                    cmax = caps["atm"]
                elif c.limit == "tyre_rating":
                    cmax = caps["ratings"]["tyre_kg"]
                elif c.limit == "wheel_rating":
                    cmax = self.inputs.v("WHL-01")
                elif c.limit == "target":
                    cmin, cmax = self.target - c.tolerance, self.target + c.tolerance
                c = c.model_copy(update=dict(min=cmin, max=cmax))
                worst = None
                for cid in ids:
                    for bs in bases:
                        v = by_id[cid][bs][key] * factor
                        margins = []
                        if c.min is not None:
                            margins.append(v - c.min)
                        if c.max is not None:
                            margins.append(c.max - v)
                        m = min(margins)
                        if worst is None or m < worst[0]:
                            worst = (m, cid, bs, v)
                m, cid, bs, v = worst
                g = lambda x: f"{round(x):,}" if abs(x) >= 100 else f"{x:g}"  # noqa: E731
                lim = " to ".join(g(x) for x in (c.min, c.max) if x is not None) if c.min is not None and c.max is not None else \
                    (f"<= {g(c.max)}" if c.max is not None else f">= {g(c.min)}")
                if factor != 1.0:
                    lim += " (1.2 x the axle load)"
                row.update(limit=f"{lim} {unit}", measured=round(v, 1), unit=unit, margin=round(m, 1), ok=m >= -1e-6,
                           governing=f"{cid} {by_id[cid]['name']} ({'with growth' if bs == 'growth' else 'no growth'})",
                           detail=f"worst case {cid} {by_id[cid]['name']}, {'with growth' if bs == 'growth' else 'no growth'}: {v:.1f} {unit}, margin {m:.1f} {unit}")
            elif c.type == "car_axle":
                cid = c.cases[0]
                ball = by_id[cid]["nominal"]["towball_kg"]
                ax = car_axles(self.car, ball)
                lo = car_axles(self.car, ball, self.car["ball_behind_axle_mm"]["v"][0])
                hi = car_axles(self.car, ball, self.car["ball_behind_axle_mm"]["v"][1])
                m = c.max - ax["rear_kg"]
                row.update(limit=f"<= {c.max:g} kg", measured=round(ax["rear_kg"], 1), unit="kg", margin=round(m, 1), ok=m >= 0,
                           governing=f"towball {ball:.0f} kg ({cid})",
                           detail=(f"rear axle {ax['rear_kg']:.0f} kg before gear, front {ax['front_kg']:.0f} kg. Gear the car can carry: "
                                   f"{ax['gear_budget_kg']:.0f} kg ({ax['binds']} binds). Ball 1.06 to 1.23 m behind the axle gives a rear axle of "
                                   f"{lo['rear_kg']:.0f} to {hi['rear_kg']:.0f} kg"),
                           car=dict(nominal=ax, short=lo, long=hi))
            elif c.type == "ballast":
                bal = self.ballast_result
                ok = bal["growth_kg"] <= bal["kg"] + 1e-6
                row.update(limit="reported", measured=round(bal["growth_kg"], 1), unit="kg", margin=None, ok=ok,
                           governing=f"{bal['governing_growth']} with growth",
                           detail=(f"{bal['kg']:.0f} kg on base weights ({bal['governing']}), {bal['growth_kg']:.0f} kg with growth "
                                   f"({bal['governing_growth']}), at X {bal['x']:.0f}, to keep the towball at or under {bal['cap_kg']:.0f} kg "
                                   "with no bikes aboard"), ballast=bal)
            elif c.type == "towball_scale":
                m = self.inputs.v("CAR-07")
                model = by_id[self.target_case.id]["nominal"]["towball_kg"]
                if m is None:
                    row.update(limit=f"within {100 * c.tolerance:.0f} % of the model", measured=None, unit="kg", margin=None, ok=False,
                               governing="not measured yet", detail=f"model {model:.0f} kg fully loaded. Not measured yet")
                else:
                    d = (m - model) / model
                    row.update(limit=f"within {100 * c.tolerance:.0f} % of the model", measured=m, unit="kg", margin=round(100 * (c.tolerance - abs(d)), 1),
                               ok=abs(d) <= c.tolerance, governing=f"model {model:.0f} kg", detail=f"scale {m:.0f} kg, model {model:.0f} kg ({100 * d:+.1f} %)")
            elif c.type == "fit":
                f = lay.fit(c.zone)
                row.update(limit="inside the zone, no overlap", measured=f["smallest_gap_mm"], unit="mm", margin=f["smallest_gap_mm"],
                           ok=f["ok"], governing=f["governing"], problems=f["problems"],
                           detail=("all fit" if f["ok"] else "; ".join(f["problems"][:4])) + f", {f['items']} items, {f['keep_clear']} keep-clear spaces",
                           sub=lay.zones[c.zone]["name"])
            elif c.type == "tyre":
                t = lay.tyre_check()
                row.update(limit=f">= {c.min_gap_mm:g} mm", measured=round(t["gap_mm"], 1), unit="mm",
                           margin=round(t["gap_mm"] - c.min_gap_mm, 1), ok=t["gap_mm"] >= c.min_gap_mm - 1e-6, governing=t["governing"],
                           detail=f"smallest gap {t['gap_mm']:.1f} mm, {t['governing']}")
            elif c.type == "width":
                w = lay.width()
                row.update(limit=f"<= {c.max:g} mm", measured=round(w["width_mm"], 1), unit="mm", margin=round(c.max - w["width_mm"], 1),
                           ok=w["width_mm"] <= c.max + 1e-6, governing=f"{w['road']} to {w['kerb']}",
                           detail=f"{w['width_mm']:.0f} mm from the {w['road'].lower()} to the {w['kerb'].lower()}")
            elif c.type == "overhang":
                V = lay.V
                front = V["axle_x"] - V["body_x0"]
                rear = V["body_x1"] - V["axle_x"]
                row.update(limit="front load space >= rear overhang", measured=round(front, 1), unit="mm", margin=round(front - rear, 1),
                           ok=front >= rear - 1e-6, governing=f"axle at X {V['axle_x']:.0f}",
                           detail=f"front load space {front:.0f} mm, rear overhang {rear:.0f} mm")
            elif c.type == "coupling":
                z = lay.V["coupling_z"]
                lo_z, hi_z = z - 20, z + 20
                m = min(lo_z - c.min, c.max - hi_z)
                row.update(limit=f"{c.min:g} to {c.max:g} mm", measured=z, unit="mm", margin=m, ok=m >= -1e-6,
                           governing="coupling point 440 +/- 20 mm", detail=f"{lo_z:.0f} to {hi_z:.0f} mm")
            elif c.type == "clearance_ground":
                g = lay.ground_clearance()
                row.update(limit=f">= {c.min:g} mm", measured=round(g["z_mm"], 1), unit="mm", margin=round(g["z_mm"] - c.min, 1),
                           ok=g["z_mm"] >= c.min, governing=g["governing"],
                           detail=f"lowest sprung part {g['z_mm']:.0f} mm above the ground at design ride height, {g['governing']}")
            elif c.type in ("jackknife", "jackknife_aframe"):
                jk = lay.jackknife(self.car)
                if c.type == "jackknife":
                    vals = [(r["parts"][p]["clearance_90_mm"], a, p) for a, r in jk.items() for p in ("body", "spare wheel")]
                    v, a, p = min(vals)
                    each = ", ".join(f"{p2} {min(r['parts'][p2]['clearance_90_mm'] for r in jk.values()):.0f} mm" for p2 in ("body", "spare wheel"))
                    row.update(limit=f">= {c.min_gap_mm:g} mm at 90 degrees", measured=round(v, 1), unit="mm", margin=round(v - c.min_gap_mm, 1),
                               ok=v >= c.min_gap_mm - 1e-6, governing=f"{p}, ball {a} mm behind the car's rear axle",
                               detail=f"{p} {v:.0f} mm from the car's side at 90 degrees ({each})", jackknife=jk)
                else:
                    firsts = [(r["parts"][p]["first_contact_deg"] or 999, a, p) for a, r in jk.items() for p in ("drawbar members", "stone guard")]
                    v, a, p = min(firsts)
                    each = ", ".join(f"{p2} {min(r['parts'][p2]['first_contact_deg'] or 999 for r in jk.values()):.1f} to "
                                     f"{max(r['parts'][p2]['first_contact_deg'] or 999 for r in jk.values()):.1f} degrees"
                                     for p2 in ("drawbar members", "stone guard"))
                    row.update(limit="reported", measured=None if v == 999 else v, unit="deg", margin=None, ok=v == 999,
                               governing=f"{p}, ball {a} mm behind the car's rear axle",
                               detail=("no contact in plan up to 90 degrees" if v == 999 else
                                       f"in plan the car's rear corner is first over the {each}, for the ball 1,230 to 1,060 mm "
                                       f"behind the car's axle. The heights decide whether they touch"), jackknife=jk)
            row["inputs"] = c.inputs
            row["status"] = ("PASS" if row["ok"] else "FAIL") if c.severity == "fail" else ("MEETS LIMIT" if row["ok"] else "REPORTED")
            out.append(row)
        return out

    # -- body length comparison ---------------------------------------------------
    def compare_lengths(self) -> list[dict]:
        rows = []
        for L in self.td["lengths_compared"]:
            t = Trailer(self.prj, self.mod, {**self.base, "body_length": L})
            ev = t.evaluate()
            lay = ev["layout"]
            s = ev["solved"]
            zl = lay.zone_lengths()
            fails = [r for r in ev["checks"] if r["severity"] == "fail" and not r["ok"]]
            mass_fails = [r for r in fails if r["type"] in ("mass",)]
            fit_fails = [r for r in fails if r["type"] == "fit"]
            tc2 = next(c for c in ev["cases"] if c["id"] == t.target_case.id)
            nominal = {c["id"]: c["nominal"]["towball_kg"] for c in ev["cases"]}
            growth = {c["id"]: c["growth"]["towball_kg"] for c in ev["cases"]}
            rows.append(dict(
                body_length=L, living=zl["living"], living_min=s["living_min_mm"], slack=zl["living"] - s["living_min_mm"],
                fits=s["fits"], method=s["method"], axle_x=lay.V["axle_x"],
                bikes_behind_axle=lay.V["module_x0"] + lay.V["mod_bikes_cog_x"] - lay.V["axle_x"],
                tare=tare_mass(lay, t), loaded=tc2["nominal"]["mass_kg"], loaded_growth=tc2["growth"]["mass_kg"],
                atm_margin_growth=3500 - max(c["growth"]["mass_kg"] for c in ev["cases"]),
                towball=nominal, towball_growth=growth, ballast_kg=ev["ballast"]["kg"], ballast_growth_kg=ev["ballast"]["growth_kg"],
                towball_min=min(min(c[b]["towball_kg"] for b in ("nominal", "growth")) for c in ev["cases"]),
                towball_max=max(max(c[b]["towball_kg"] for b in ("nominal", "growth")) for c in ev["cases"]),
                pct_min=min(min(c[b]["towball_pct"] for b in ("nominal", "growth")) for c in ev["cases"]),
                failed=[f"{r['id']}" for r in fails], mass_ok=not mass_fails, fit_ok=not fit_fails,
                overall_length=lay.overall()["x1"] - lay.overall()["x0"]))
        return rows


def tare_mass(lay: Layout, tr: Trailer) -> float:
    """The registration tare: TC1 as built, without the ballast."""
    tc1 = next(c for c in tr.cases if c.id == "TC1")
    return sum(m for b, m in lay.case_lines(tc1) if b.load != "ballast")


def load(prj: Project | None = None, model=None) -> Trailer:
    from .model.assembly import Model
    prj = prj or Project()
    model = model or Model(prj)
    return Trailer(prj, ModuleInfo.from_model(prj, model))


# ------------------------------------------------------------------ outputs for the site, the drawing and TRAILER.md
def _r(v, n=1):
    if isinstance(v, float):
        return round(v, n)
    if isinstance(v, (list, tuple)):
        return [_r(x, n) for x in v]
    if isinstance(v, dict):
        return {k: _r(x, n) for k, x in v.items()}
    return v


def chassis_inputs(tr: Trailer, ev: dict) -> dict:
    lay = ev["layout"]
    V = lay.V
    cases = {c["id"]: c for c in ev["cases"]}
    tc2 = cases[tr.target_case.id]
    jk = next(r for r in ev["checks"] if r["id"] == "JK-01")
    mod0, mod1 = V["part_a_x"], V["in_x1"]
    xms = []
    for b in lay.blocks:
        if b.id != "CM":
            continue
        x = b.box[0]
        under = []
        if mod0 - 1 <= x <= mod1 + 1:
            under.append("garage")
        for t in lay.tanks():
            if t.box[0] - 60 <= x <= t.box[3] + 10:
                under.append("water tank bay")
        bat = lay.find("UF-04").box
        if bat[0] - 60 <= x <= bat[3] + 10:
            under.append("battery bay")
        if x < mod0 - 1:
            under.append("living area" if x >= V["body_x0"] else "drawbar")
        if x > mod1 + 1:
            under.append("rear wall")
        xms.append(dict(x_front=x, x_rear=b.box[3], station=b.extra.get("station"), section=b.note,
                        under=", ".join(dict.fromkeys(under)), generated=b.generated, mass_kg=b.mass_kg))
    outriggers = sorted({o.box[0] for o in lay.blocks if o.id == "OR"})
    bars = [b for b in lay.blocks if b.bar]
    ov = lay.overall()
    alt_track = 2000
    return _r(dict(
        datum="X from the ball centre, positive rearward. Y from the centreline, positive to the road side. Z up from the ground at design ride height.",
        rail_outer_width=V["rail_outer_w"], rail_inner_width=2 * V["rail_in"], rail_centres=2 * V["rail_c"],
        rail_outer_width_wide_track=alt_track - 2 * (V["cf"] - V["wheel_offset"]), track=V["track"], wide_track=alt_track,
        cf=V["cf"], wheel_offset=V["wheel_offset"],
        rail_section=f"{V['rail_h']:.0f} x {V['rail_w']:.0f} mm block size (the engineer sizes it)",
        rail_x0=V["body_x0"], rail_x1=V["body_x1"], rail_length=V["body_length"],
        rail_underside_z=V["rail_underside_z"], rail_top_z=V["rail_top_z"], raiser_h=V["raiser_h"],
        floor_underside_z=V["floor_underside_z"], floor_z=V["floor_z"], ceiling_z=V["ceiling_z"],
        drawbar_length=V["drawbar_length"], drawbar_member_length=[math.dist(b.bar["p0"][:2], b.bar["p1"][:2]) for b in bars][0],
        drawbar_tail=V["db_tail"], coupling_z=V["coupling_z"], drop_rail_to_coupling=V["rail_underside_z"] - V["coupling_z"],
        crossmembers=xms, outriggers_x=outriggers,
        axle_x=V["axle_x"], hubs_x=[V["axle_x"] + V["front_hub_dx"], V["axle_x"] + V["rear_hub_dx"]],
        hub_z=V["hub_z"], hub_y=V["hub_y"], axle_spacing=V["axle_spacing"],
        xt_front_hinge_rear_x=V["axle_x"] + V["xt_front_hinge_rear"], xt_rear_shock_front_x=V["axle_x"] + V["xt_rear_shock_front"],
        overall_length=ov["x1"] - ov["x0"], overall_x0=ov["x0"], overall_x1=ov["x1"], travel_height=ov["z1"],
        overall_width=lay.width()["width_mm"], body_x0=V["body_x0"], body_x1=V["body_x1"],
        cog_loaded=tc2["nominal"]["cog"], cog_loaded_growth=tc2["growth"]["cog"],
        cog_height_above_hub=tc2["nominal"]["cog"][2] - V["hub_z"],
        cog_by_case={c["id"]: dict(nominal=c["nominal"]["cog"], growth=c["growth"]["cog"]) for c in ev["cases"]},
        jackknife_body_mm=min(r["parts"]["body"]["clearance_90_mm"] for r in jk["jackknife"].values()),
        jackknife_spare_mm=min(r["parts"]["spare wheel"]["clearance_90_mm"] for r in jk["jackknife"].values()),
        spare_box=[min(b.box[i] for b in lay.blocks if b.system == "spare" and b.box) if i < 3 else
                   max(b.box[i] for b in lay.blocks if b.system == "spare" and b.box) for i in range(6)],
        tyre_d=V["tyre_d"],
        tyre_floor_clearance=V["tyre_clearance"], tank_capacity_l=lay.tank_capacity_l(),
        module_x0=V["module_x0"], part_a_x=V["part_a_x"], garage_x1=V["in_x1"],
        battery_box=lay.find("UF-04").box, tanks=[t.box for t in lay.tanks()],
    ))


def schedule(lay: Layout, tr: Trailer) -> list[dict]:
    """MASS-01 mass schedule with the MASS-02 load-case flags."""
    flags = {}
    for c in tr.cases:
        for b, m in lay.case_lines(c):
            flags.setdefault(b.iid, set()).add(c.id)
    rows = []
    for b in lay.blocks:
        if b.load == "none" or b.keep_clear:
            continue
        m = lay.V["ballast_kg"] if b.load == "ballast" else b.mass_kg
        rows.append(_r(dict(
            iid=b.iid, id=b.id, item=b.name, system=b.system, group=SYSTEM_LABELS[b.system], drawing="CT-001",
            qty=b.qty, unit_mass=b.unit_mass, basis=b.basis, mass_kg=m, maturity=b.maturity,
            growth_pct=round(b.growth * 100), mass_with_growth_kg=m * (1 + b.growth),
            source=b.source, note=b.note, mass_note=b.mass_note, load=b.load, removable=b.removable,
            cog=list(b.cog) if b.cog else None, box=list(b.box) if b.box else None, generated=b.generated,
            cases=sorted(flags.get(b.iid, [])))))
    return rows


def report(tr: Trailer) -> dict:
    ev = tr.evaluate()
    lay = ev["layout"]
    V = lay.V
    zl = lay.zone_lengths()
    lengths = tr.compare_lengths()
    sys_tot: dict[str, dict] = {}
    for b, m in lay.case_lines(next(c for c in tr.cases if c.id == "TC1")):
        if b.load == "ballast":
            continue
        g = sys_tot.setdefault(SYSTEM_LABELS[b.system], dict(mass_kg=0.0, growth_kg=0.0))
        g["mass_kg"] += m
        g["growth_kg"] += m * (1 + b.growth)
    fitting = [r for r in lengths if r["fit_ok"]]
    passing = [r for r in fitting if r["mass_ok"]]
    rec = (passing or fitting or lengths)[0]
    return _r(dict(
        assembly=dict(id=tr.td["id"], name=tr.td["name"], revision=tr.td["revision"]),
        body_length=V["body_length"], recommended=dict(body_length=rec["body_length"], passes_mass=bool(passing),
                                                       fits=rec["fit_ok"], matches_data=rec["body_length"] == V["body_length"]),
        solved=ev["solved"], target_kg=tr.target, params={k: V[k] for k in sorted(V) if isinstance(V[k], (int, float))},
        zones=zl, zone_names={k: z["name"] for k, z in lay.zones.items()},
        cases=ev["cases"], checks=ev["checks"], lengths=lengths, fit_options=tr.fit_options(), zone_costs=tr.zone_costs(),
        least_certain=tr.least_certain(ev), chassis=chassis_inputs(tr, ev), schedule=schedule(lay, tr),
        tare_by_group=sys_tot, tare_kg=tare_mass(lay, tr), ballast=ev["ballast"], car=car_axles(tr.car, next(c for c in ev["cases"] if c["id"] == tr.target_case.id)["nominal"]["towball_kg"]),
        car_limits={k: v["v"] for k, v in tr.car.items() if isinstance(v, dict) and "v" in v},
        target_why=tr.target_why, wheel=tr.wheel, supplier=tr.supplier, caps=tr.caps(), registration=tr.reg,
        weighed=tr.weighed_rows, spacing=dict(rule=tr.inputs.rule_spacing, solved=tr.inputs.solved,
                                              in_use=tr.prj.P.values["bike_spacing"], garage=tr.prj.P.values["garage_length"],
                                              fits=tr.inputs.spacing_fits),
        measurements=tr.inputs.report(),
    ))

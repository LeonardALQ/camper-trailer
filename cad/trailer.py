"""Whole-trailer block layout: placement, mass schedule, load cases, axle solve and checks (TRAILER.md).

Everything is in the project datum DIM-01 (research/02): X from the coupling ball centre, positive rearward,
Y from the centreline, positive to the road side, Z up from the ground at design ride height. Blocks are
axis-aligned boxes, wheels are cylinders and the drawbar members are bars between two points.

Revision J (21 Nov 2026) is the home trailer (home/layout-home.md): the bikes ride in the ute's bike box (UTE-GARAGE.md),
so the trailer has no garage module. The axle solve moves the axle group and everything tied to it (the tanks, their
guards and the suspension) along X to the middle of the towball window of decision H17: from the position where the
lightest case keeps 8.0 % of its mass on the ball to the one where the heaviest towball with growth reaches 320 kg
(data/load_cases.yaml `axle_window`). The solve needs nothing from the ute model (cad/towball.py caches its result for
the ute's towing cases). It never changes a limit or a block size. The tow vehicle's limits come from data/ute/ute.yaml
and its masses and the bike box's sweep from the ute model (build/ute/ute.json), for the checks.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any

import json

import yaml

from .partsdb import DATA, ROOT, Mass, Params, Project

TRAILER_YAML = DATA / "assemblies" / "trailer.yaml"
GROWTH = {"estimate": 0.20, "calculated": 0.07, "spec": 0.0, "weighed": 0.0}
STAGE_IDS = {"drawbar_structure": ("DB-KA", "DB-KB", "DB-RA", "DB-RB", "DB-BR", "DB-03", "DB-04"), "stowage": ("DX-01", "GS-01")}
SYSTEM_LABELS = {
    "drawbar": "Coupling and drawbar fittings", "chassis": "Chassis and drawbar", "running_gear": "Running gear", "body": "Body",
    "roof": "Roof", "underfloor": "Under the floor", "bed": "Bed", "living": "Living area",
    "stowage": "Drawbar box", "spare": "Spare wheel", "payload": "Payload",
    "electrical": "Electrical", "hvac": "HVAC and ventilation", "wet_room": "Wet room",
}
TOL = 0.5  # mm: boxes that only touch do not overlap


# ------------------------------------------------------------------ the tow vehicle
def tow_vehicle(prj: Project) -> dict:
    """The LandCruiser 79 (data/ute/ute.yaml) and what the ute model gives the trailer (build/ute/ute.json): the ute's
    mass with the bikes aboard for the GCM, and the bike box's sweep about the ball for the jack-knife checks."""
    tv = prj.load.tow_vehicle
    d = yaml.safe_load((ROOT / tv["data"]).read_text())
    lim = {k: v["v"] for k, v in d["limits"].items()}
    src = {k: v["src"] for k, v in d["limits"].items()}
    path = ROOT / tv["model"]
    if not path.exists():
        raise FileNotFoundError(f"{tv['model']} is missing: build the ute first (make ute)")
    rep = json.loads(path.read_text())
    case = next(c for c in rep["cases"] if c["id"] == tv["gcm_case"])
    # the ute's rear axle at a ball load (H14): its value with the bikes aboard and no ball (UC2), plus what each kilogram
    # on the ball adds, from the towing case (UC3) against UC2, both with growth. The lever is the ute model's own
    tow = next(c for c in rep["cases"] if c["growth"].get("towball_kg"))
    rear0 = case["growth"]["rear_kg"]
    per_ball = (tow["growth"]["rear_kg"] - rear0) / tow["growth"]["towball_kg"]
    # what the Elite kit adds over the Platinum on the rear axle, so the Platinum's return (cut CUT7) can be read off
    wb = rep["params"]["wheelbase"]
    elite = sum(ln["kg"] * ln["x"] / wb for ln in rep["lines"] if ln.get("elite") and tv["gcm_case"] in ln["cases"])
    return dict(name=tv["name"], limits=lim, limit_src=src, gcm_case=tv["gcm_case"], case_name=case["name"],
                ute_kg=case["nominal"]["mass_kg"], ute_kg_growth=case["growth"]["mass_kg"], sweep=rep["bike_box_sweep"],
                rear_kg_growth=rear0, rear_kg_nominal=case["nominal"]["rear_kg"], elite_rear_kg=elite, rear_per_ball=per_ball,
                design_ball_kg=tow["growth"]["towball_kg"], tow_case=tow["id"],
                ute_checks=[dict(id=c["id"], title=c["title"], status=c["status"], detail=c["detail"], measured=c.get("measured"))
                            for c in rep["checks"]])


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
    load: str = "tare"                         # tare, fuel, gear, water, none
    keep_clear: bool = False
    hollow: bool = False
    note: str | None = None
    material: str | None = None                # what it is made of (the item's `material`, or the chassis section and grade)
    generated: bool = False
    extra: dict = field(default_factory=dict)
    growth_frac: float | None = None            # set when the line is made of parts with their own maturity

    @property
    def growth(self) -> float:
        if self.growth_frac is not None and self.maturity != "weighed":
            return self.growth_frac
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

    def __init__(self, td: dict, prj: Project, overrides: dict | None = None):
        self.td, self.prj = td, prj
        raw = dict(td["params"])
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
        self.zones = {k: dict(name=z["name"], box=_box(*self.P.eval(z["box"], {}))) for k, z in td["zones"].items()}
        ids = [b.iid for b in self.blocks]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise ValueError(f"duplicate trailer block ids {sorted(dup)}")

    # -- expansion -------------------------------------------------------
    def _expand(self, it: dict) -> list[Block]:
        known = {"id", "name", "system", "zone", "for", "box", "cyl", "bar", "point", "cog", "mass", "note",
                 "load", "keep_clear", "hollow", "tank", "water", "when", "parts", "material", "price"}
        extra = set(it) - known
        if extra:
            raise ValueError(f"trailer item {it.get('id')}: unknown keys {sorted(extra)}")
        if "mass" in it and "parts" in it:
            raise ValueError(f"trailer item {it['id']}: give `mass` or `parts`, not both")
        mass = Mass.model_validate({k: v for k, v in it["mass"].items() if k != "measure"}) if "mass" in it else None
        loops = it.get("for") or {}
        names = list(loops)
        values = [self.P.eval(loops[n], {}) for n in names]
        combos = list(itertools.product(*values)) if names else [()]
        out = []
        for k, combo in enumerate(combos, 1):
            local = dict(zip(names, combo))
            if "when" in it and not self.P.eval(it["when"], local):
                continue   # an owner option that is off (TRAILER.md, open questions)
            iid = f"{it['id']}.{k}" if len(combos) > 1 else it["id"]
            b = Block(iid=iid, id=it["id"], name=it["name"], system=it["system"], zone=it.get("zone"),
                      load=it.get("load", "tare"), keep_clear=bool(it.get("keep_clear")), hollow=bool(it.get("hollow")),
                      note=it.get("note"), material=it.get("material"))
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
            if it.get("tank"):
                b.extra["tank"] = True
            if it.get("water"):
                b.load = "water"
            if mass is not None:
                self._mass(b, mass, it, dims, local)
            if "parts" in it:
                self._parts(b, [dict(p, kg=self.P.eval(p["kg"], local)) for p in it["parts"]])
            out.append(b)
        return out

    @staticmethod
    def _parts(b: Block, parts: list[dict]):
        """A line made of bought and made parts, each with its own mass basis (report 13): maker and retailer figures
        are spec (0 % growth), calculated 7 % and estimates 20 % (MASS-06)."""
        mat = {"maker": "spec", "retailer": "spec", "spec": "spec", "calculated": "calculated", "estimate": "estimate"}
        rows = [dict(item=p["item"], kg=float(p["kg"]), maturity=mat[p["basis"]], source=p.get("source", "")) for p in parts if float(p["kg"]) > 0]
        b.mass_kg = sum(r["kg"] for r in rows)
        b.basis, b.qty, b.unit_mass = "declared", 1, b.mass_kg
        b.growth_frac = sum(r["kg"] * GROWTH[r["maturity"]] for r in rows) / b.mass_kg if b.mass_kg else 0.0
        by = {}
        for r in rows:
            by[r["maturity"]] = by.get(r["maturity"], 0.0) + r["kg"]
        b.maturity = max(by, key=by.get)
        b.extra["parts"] = rows
        b.source = ". ".join(f"{r['item']} {r['kg']:g} kg ({'maker or retailer' if r['maturity'] == 'spec' else r['maturity']}"
                             f"{', ' + r['source'] if r['source'] else ''})" for r in rows)
        b.mass_note = ", ".join(f"{v:.1f} kg {'maker or retailer' if k == 'spec' else k}" for k, v in by.items())

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

    def _stations(self) -> list[dict]:
        """Crossmember stations: the fixed ones (body ends, XT kit, battery bay) and intermediate ones at no more than
        xm_max_pitch, except in the tank and battery bays. Each gives the station's front face X."""
        cm = self.td["crossmembers"]
        V = self.V
        w = V["xm_w"]
        fixed = [dict(id=f["id"], x=self.P.eval(f["x"], {})) for f in cm["fixed"]]
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
                                     generated=True))
        stations.append(fixed[-1])
        return stations

    def _crossmembers(self) -> list[Block]:
        """The designed chassis and drawbar (cad/chassis.py, CHASSIS.md) as mass lines and envelopes: every member,
        fitting and the galvanising."""
        from .chassis import Chassis
        self.stations = self._stations()
        ch = self.chassis = Chassis(self.V, self.stations)
        galv = "hot-dip galvanised after fabrication"
        plate = ch.data["material"]["plate"].split(" (")[0]
        out = []
        for m in ch.members:
            b = Block(iid=m.id, id=m.id, name=m.name, system="chassis", cog=m.cog, mass_kg=m.mass_kg, maturity="calculated",
                      source=f"Calculated: {m.length:.0f} mm of {m.sec.name} at {m.sec.kg_m} kg/m (report 11 section table, Austube Mills DCT)",
                      basis="per_length", unit_mass=m.sec.kg_m, qty=m.length / 1000, note=m.note or None,
                      material=f"{m.sec.name}, {m.sec.grade} steel (AS/NZS 1163), {galv}",
                      extra=dict(member=m, role=m.role, station=m.station))
            if m.role == "drawbar" and m.p0[1] != m.p1[1]:
                b.bar = dict(p0=m.p0, p1=m.p1, w=m.sec.b, h=m.sec.d)
            else:
                b.box = m.box()
            out.append(b)
        for f in ch.fittings:
            n = len(f.at)
            cog = tuple(sum(p[i] for p in f.at) / n for i in range(3))
            system = "drawbar" if f.id.startswith("DB-") else "chassis"
            spec = next(d for d in ch.data["fittings"] if d["id"] == f.id)
            if f.kind == "plate":
                material = f"{f.t:g} mm plate, {plate}, {galv}"
            elif f.kind == "tube":
                sec = ch.sections[spec["section"]]
                material = f"{sec.name}, {sec.grade} steel (AS/NZS 1163), {galv}"
            else:
                material = spec.get("material")
            b = Block(iid=f.id, id=f.id, name=f.name, system=system, cog=cog, mass_kg=f.mass_kg, maturity=f.maturity, source=f.source,
                      unit_mass=f.mass_each, qty=f.qty, material=material, extra=dict(fitting=f))
            if "box" in spec:
                b.box = _box(*ch.P.eval(spec["box"], {}))
            out.append(b)
        g = ch.galvanising()
        zinc = [(m.area_m2 * ch.galv_rate(m.sec.t), m.cog) for m in ch.members] + \
            [(f.area_m2_each * ch.galv_rate(f.t) / len(f.at) * f.qty, p) for f in ch.fittings if f.kind in ("plate", "tube") for p in f.at]
        tot = sum(m for m, _ in zinc)
        cog = tuple(sum(m * c[i] for m, c in zinc) / tot for i in range(3))
        out.append(Block(iid="CH-G01", id="CH-G01", name="Hot-dip galvanising to AS/NZS 4680 after fabrication, inside and out",
                         system="chassis", cog=cog, mass_kg=g["mass_kg"], maturity="calculated", material="Zinc",
                         source=(f"Calculated: {g['area_m2']:.1f} m2 inside and out at the AS/NZS 4680 minimum average coating masses "
                                 "(report 11 section 1.4)")))
        return out

    def apply_weighed(self, stages: list[dict]) -> list[dict]:
        """Scale the built parts of each weighed stage to its weighbridge figure (report 02 MASS-07)."""
        out = []
        for st in stages:
            lines = [b for b in self.blocks if b.load == "tare" and b.mass_kg > 0 and _stage_of(b) in st["stage"]]
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
        return dict(bed=V["bed_x1"] - V["in_x0"], living=V["rear_x0"] - V["bed_x1"], rear=V["in_x1"] - V["rear_x0"],
                    interior=V["in_x1"] - V["in_x0"])

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
            elif b.load == "water":
                if water > 0:
                    w = Block(**{**b.__dict__, "cog": self.water_cog(water), "mass_kg": water})
                    out.append((w, water))
            elif b.load in case.load:
                out.append((b, b.mass_kg))
        return out

    def evaluate_case(self, case) -> dict:
        xa = self.V["axle_x"]
        res = {}
        for basis in ("nominal", "growth"):
            items = [(m * (1 + b.growth) if basis == "growth" else m, b.cog) for b, m in self.case_lines(case)]
            M = sum(m for m, _ in items)
            cog = [sum(m * c[i] for m, c in items) / M for i in range(3)]
            ball = sum(m * (xa - c[0]) for m, c in items) / xa
            axle = M - ball
            # the ball sits on the centreline, so the axle group's two sides carry the whole lateral moment
            side = M * cog[1] / self.V["track"]
            road, kerb = axle / 2 + side, axle / 2 - side
            res[basis] = dict(mass_kg=M, cog=cog, towball_kg=ball, towball_pct=100 * ball / M, axle_kg=axle,
                              tyre_load_kg=1.2 * axle / 4, side_kg=dict(road=road, kerb=kerb),
                              tyre_load_side_kg=1.2 * max(road, kerb) / 2)
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

    # -- jack-knife with the ute's bike box (plan view about the ball) ----------------
    def footprints(self) -> list[dict]:
        """Every solid block's plan footprint as a convex polygon, its nearest distance to the ball in plan, and its top Z.
        As the trailer swings about the ball, the bike box's corners sweep a circle about it, so these two numbers decide
        whether a part can meet the box (JK-01 and JK-02)."""
        out = []
        for b in self.blocks:
            if b.keep_clear or b.load == "none":
                continue
            if b.bar:
                (x0, y0, z0), (x1, y1, z1) = b.bar["p0"], b.bar["p1"]
                L = math.hypot(x1 - x0, y1 - y0)
                nx, ny = -(y1 - y0) / L * b.bar["w"] / 2, (x1 - x0) / L * b.bar["w"] / 2
                poly = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
                top = max(z0, z1) + b.bar["h"] / 2
            elif b.box is not None:
                x0, y0, _, x1, y1, top = b.box
                poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            else:
                continue
            out.append(dict(iid=b.iid, name=b.name, system=b.system, dist=_origin_dist(poly), top=top))
        return out


def _lc(name: str) -> str:
    """Lower-case a name's first letter to run it into a sentence, unless it starts an acronym (ARK, XT)."""
    return name if name[1:2].isupper() else name[:1].lower() + name[1:]


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


def _origin_dist(poly) -> float:
    """Distance from the ball (the origin) to a convex polygon in plan, 0 if the polygon covers it."""
    n = len(poly)
    sides = [(poly[(i + 1) % n][0] - poly[i][0]) * (0 - poly[i][1]) - (poly[(i + 1) % n][1] - poly[i][1]) * (0 - poly[i][0]) for i in range(n)]
    if all(v >= 0 for v in sides) or all(v <= 0 for v in sides):
        return 0.0
    return min(_seg_dist((0.0, 0.0), poly[i], poly[(i + 1) % n]) for i in range(n))


# ------------------------------------------------------------------ the trailer: solve, cases, checks
class Trailer:
    def __init__(self, prj: Project | None = None, overrides: dict | None = None, ute: bool = True):
        """`ute` reads the ute model (build/ute/ute.json) for the checks against the tow vehicle. The axle solve needs
        nothing from it, so the ute's own build can solve the trailer first (cad/towball.py)."""
        self.prj = prj = prj or Project()
        self.td = yaml.safe_load(TRAILER_YAML.read_text())
        self.base = dict(overrides or {})
        self.cases = prj.load.trailer_cases
        self.reg = prj.load.registration
        inp = self.inputs = prj.inputs
        self.tv = tow_vehicle(prj) if ute else None
        self.target = prj.load.towball_target_kg
        self.aw = prj.load.axle_window
        self.target_why = (f"the axle sits in the middle of the window between {self.aw['towball_pct_min']:.1f} % on the ball in the "
                           f"lightest case and {self.aw['towball_max_kg']:.0f} kg with growth in the heaviest (H17). The supplier's 120 % "
                           f"note uses {self.target:.1f} kg, {100 * self.target / self.reg['plated_atm_kg']['v']:.1f} % of the "
                           f"{self.reg['plated_atm_kg']['v']:,.0f} kg plate")
        self.supplier = inp.supplier(self.reg["plated_atm_kg"]["v"], self.target)
        self.wheel = inp.wheel(self.td["wheel"])
        self.base.setdefault("coupling_z", inp.coupling_z())
        offset = self.base.get("wheel_offset", self.td["params"]["wheel_offset"])
        self.base.setdefault("cf", inp.cf(offset, self.td["params"]["tyre_w"]))
        self.weighed = inp.weighed()
        self.weighed_rows: list[dict] = []
        self.target_case = next(c for c in self.cases if c.towball_target)
        self.analyse_chassis = True
        self._chassis = None
        self._body = None

    def chassis_model(self, lay):
        return lay.chassis

    def chassis_results(self, lay) -> dict:
        """The frame analysis of the chassis for this layout (cad/chassis_fea.py), run once."""
        if self._chassis is None or self._chassis[0] is not lay:
            from .chassis_fea import Analysis
            ch = self.chassis_model(lay)
            self._chassis = (lay, ch, Analysis(lay, self, ch).run())
        return self._chassis[2]

    def body_results(self, lay) -> dict:
        """The body checks for this layout (cad/body.py, BODY.md), run once."""
        if self._body is None or self._body[0] is not lay:
            from .body import Body
            self._body = (lay, Body(lay, self).results())
        return self._body[1]

    def tyre_arc(self, lay) -> dict:
        """FIT-05: each tyre swung about its arm pivot through its travel (report 11 section 5), against every chassis
        member at its true outer size. The gap to the floor underside and the rest of the body is reported too."""
        from .chassis import tyre_clearance
        ch = self.chassis_model(lay)
        w = lay.V["tyre_w"]
        t = tyre_clearance(ch, [(m.id + " " + m.name, m.box()) for m in ch.members], w)
        others = [(f"{b.name} ({b.iid})", b.box) for b in lay.blocks
                  if b.solid and not b.hollow and b.system not in ("running_gear", "chassis", "drawbar")]
        o = tyre_clearance(ch, others, w)
        who = f"tyre {t['tyre']} at {t['travel_mm']:+.0f} mm travel to {t['member']}"
        return dict(gap_mm=t["gap_mm"], governing=who, body_gap_mm=o["gap_mm"], body_governing=o["member"],
                    detail=(f"{t['gap_mm']:.1f} mm, {who}. The {lay.V['tyre_d']:.0f} mm tyre comes {o['gap_mm']:.1f} mm from the "
                            f"{o['member']} at {o['travel_mm']:+.0f} mm travel"))

    def layout(self, **over) -> Layout:
        lay = Layout(self.td, self.prj, {**self.base, **over})
        self.weighed_rows = lay.apply_weighed(self.weighed)
        return lay

    def caps(self) -> dict:
        r = {k: v["v"] for k, v in self.reg["ratings"].items()}
        gtm = min(r["tyre_kg"] * 4, r["coupling_kg"], r["chains_kg"], r["brakes_kg"])
        atm = min(r["coupling_kg"], r["chains_kg"])
        return dict(gtm=gtm, atm=atm, plated=self.reg["plated_atm_kg"]["v"], ratings=r)

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

    def ball_max(self) -> dict:
        """The heaviest towball the ute takes (H14): its rear axle at its rating with growth, from the ute model, or the
        towbar's 350 kg, whichever is lower."""
        tv, lim = self.tv, self.tv["limits"]
        axle = (lim["rear_axle_kg"] - tv["rear_kg_growth"]) / tv["rear_per_ball"]
        rating = lim["towball_rating_kg"]
        return dict(kg=min(axle, rating), axle_kg=axle, rating_kg=rating, governing="the ute's rear axle" if axle <= rating else "the towbar")

    def _window_values(self, x: float) -> tuple[float, float]:
        """At axle X: the lowest towball share over every case on both bases, and the heaviest towball with growth."""
        lay = self.layout(axle_x=x)
        ev = [lay.evaluate_case(c) for c in self.cases]
        pct = min(min(e["nominal"]["towball_pct"], e["growth"]["towball_pct"]) for e in ev)
        return pct, max(e["growth"]["towball_kg"] for e in ev)

    def window(self) -> dict:
        """The axle positions that meet decision H17's design targets together: the lightest case keeps the target share
        of its mass on the ball (both bases) and the heaviest towball with growth stays under the target ceiling. The
        hard limits, MAS-03 and MAS-04, sit outside it."""
        V = self.layout().V
        pct_min, kg_max = self.aw["towball_pct_min"], self.aw["towball_max_kg"]
        lo, hi = V["body_x0"] + 500, V["body_x1"] - 500
        x_lo = self._bisect(lambda x: self._window_values(x)[0] - pct_min, lo, hi, it=40)
        x_hi = self._bisect(lambda x: kg_max - self._window_values(x)[1], lo, hi, it=40)
        return dict(x_lo=x_lo, x_hi=x_hi, width_mm=None if x_lo is None or x_hi is None else x_hi - x_lo, pct_min=pct_min,
                    ball_max=dict(kg=kg_max, governing="H17's towball ceiling"))

    def solve(self) -> dict:
        """Axle position: the middle of the towball window (H14, H17). VSB1 5.1.1 keeps the axle at or behind the middle of the body."""
        V = self.layout().V
        w = self.window()
        if w["x_lo"] is None or w["x_hi"] is None:
            return dict(method="no solution", axle_x=None, overrides={}, notes=[], window=w)
        xa = (w["x_lo"] + w["x_hi"]) / 2
        mid = V["body_x0"] + V["body_length"] / 2
        notes = []
        if w["width_mm"] < 0:
            notes.append(f"the window is shut by {-w['width_mm']:.0f} mm: no axle position meets H17's two towball targets together")
        if xa < mid:
            notes.append(f"the window puts the axle {mid - xa:.0f} mm ahead of the middle of the body, so VSB1 5.1.1 holds it at the middle")
            xa = mid
        return dict(method="axle in the middle of the towball window", axle_x=xa, overrides=dict(axle_x=xa), notes=notes,
                    behind_body_middle_mm=xa - mid, window=w)

    def evaluate(self, solved: dict | None = None) -> dict:
        solved = solved or self.solve()
        self.last_solved = solved
        lay = self.layout(**solved["overrides"])
        cases = [lay.evaluate_case(c) for c in self.cases]
        self.last_layout = lay
        checks = self.checks(lay, cases)
        return dict(layout=lay, solved=solved, cases=cases, checks=checks)

    # -- checks ----------------------------------------------------------------
    def checks(self, lay: Layout, cases: list[dict]) -> list[dict]:
        out = []
        by_id = {c["id"]: c for c in cases}
        for c in self.prj.trailer_checks:
            if c.when is not None and not lay.P.eval(c.when, {}):
                continue   # an owner option that is off (FIT-02 without LPG, for example)
            row = dict(id=c.id, title=c.title, type=c.type, severity=c.severity, why=c.why, sub="")
            if c.type == "mass":
                ids = [x["id"] for x in cases] if c.cases == "all" else c.cases
                bases = ["nominal", "growth"] if c.basis == "both" else [c.basis]
                key = {"mass": "mass_kg", "axle": "axle_kg", "axle_vsb1": "axle_kg", "towball": "towball_kg",
                       "towball_pct": "towball_pct", "tyre_load": "tyre_load_kg", "tyre_load_side": "tyre_load_side_kg"}[c.quantity]
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
                elif c.limit == "plated_atm":
                    cmax = caps["plated"]
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
            elif c.type == "gcm":
                tv = self.tv
                lim = tv["limits"]["gcm_kg"]
                light = min(x["nominal"]["towball_kg"] for x in cases)   # the lightest ball leaves the most of the plate behind it
                plan = tv["limits"]["weighed_max_kg"] + self.caps()["plated"] - light
                heavy = max(cases, key=lambda x: x["growth"]["mass_kg"])
                model = tv["ute_kg_growth"] + heavy["growth"]["mass_kg"]
                v = max(plan, model)
                row.update(limit=f"<= {lim:,.0f} kg", measured=round(v, 1), unit="kg", margin=round(lim - v, 1), ok=v <= lim + 1e-6,
                           governing="the plan's sum" if plan >= model else f"the model's sum ({heavy['id']})",
                           detail=(f"plan: the ute at its {tv['limits']['weighed_max_kg']:,.0f} kg weighed limit plus the {self.caps()['plated']:,.0f} kg "
                                   f"plate less the lightest towball, {light:.0f} kg, is {plan:,.0f} kg. Model: the ute with the bikes "
                                   f"aboard ({tv['gcm_case']}, {tv['ute_kg_growth']:,.0f} kg with growth) plus {heavy['id']} with growth "
                                   f"({heavy['growth']['mass_kg']:,.0f} kg) is {model:,.0f} kg"),
                           gcm=dict(plan=plan, model=model, ute_kg_growth=tv["ute_kg_growth"], trailer_case=heavy["id"]))
            elif c.type in ("towball_ute", "towball_ute_input"):
                tv, ids = self.tv, ([x["id"] for x in cases] if c.cases == "all" else c.cases)
                bs = "growth" if c.basis != "nominal" else "nominal"
                heavy = max(ids, key=lambda i: by_id[i][bs]["towball_kg"])
                ball = by_id[heavy][bs]["towball_kg"]
                if c.type == "towball_ute":
                    bm = self.ball_max()
                    rear = tv["rear_kg_growth"] + tv["rear_per_ball"] * ball
                    m_axle, m_bar = tv["limits"]["rear_axle_kg"] - rear, bm["rating_kg"] - ball
                    row.update(limit=f"rear axle <= {tv['limits']['rear_axle_kg']:,.0f} kg and ball <= {bm['rating_kg']:.0f} kg", measured=round(rear, 1),
                               unit="kg", margin=round(min(m_axle, m_bar), 1), ok=min(m_axle, m_bar) >= -1e-6,
                               governing=f"{heavy} {by_id[heavy]['name']} (with growth)",
                               detail=(f"heaviest towball {ball:.1f} kg ({heavy}, with growth). The ute's rear axle: {tv['rear_kg_growth']:,.1f} kg with "
                                       f"the bikes aboard ({tv['gcm_case']}, with growth) plus {tv['rear_per_ball']:.3f} kg per kg on the ball "
                                       f"({tv['tow_case']} against {tv['gcm_case']}) is {rear:,.1f} kg, margin {m_axle:.1f} kg. Towbar margin {m_bar:.1f} kg"),
                               ball_max=bm)
                else:
                    d = tv["design_ball_kg"]
                    row.update(limit=f"<= {d:.1f} kg, the ute's design towball ({tv['tow_case']})", measured=round(ball, 1), unit="kg",
                               margin=round(d - ball, 1), ok=ball <= d + 1e-6, governing=f"{heavy} {by_id[heavy]['name']} (with growth)",
                               detail=f"heaviest towball {ball:.1f} kg against the {d:.1f} kg the ute model carries in {tv['tow_case']}")
            elif c.type == "platinum_return":
                tv, lim = self.tv, self.tv["limits"]
                heavy = max((x["id"] for x in cases), key=lambda i: by_id[i]["nominal"]["towball_kg"])
                ball = by_id[heavy]["nominal"]["towball_kg"]
                plat = tv["rear_kg_nominal"] - tv["elite_rear_kg"]
                rear = plat + tv["rear_per_ball"] * ball
                cap = lim["platinum_rear_axle_kg"] - lim["platinum_return_margin_kg"]
                row.update(limit=(f"<= {cap:,.0f} kg, the Platinum's {lim['platinum_rear_axle_kg']:,.0f} kg less "
                                  f"{lim['platinum_return_margin_kg']:.0f} kg"), measured=round(rear, 1), unit="kg",
                           margin=round(cap - rear, 1), ok=rear <= cap + 1e-6, governing=f"{heavy} {by_id[heavy]['name']} (no growth)",
                           detail=(f"on the model without growth the ute's rear axle on the Platinum is {plat:,.1f} kg with the bikes aboard "
                                   f"({tv['gcm_case']}), plus {tv['rear_per_ball']:.3f} kg per kg of the trailer's heaviest towball "
                                   f"({ball:.1f} kg, {heavy}): {rear:,.1f} kg. The S3 weighing decides cut CUT7"))
            elif c.type == "axle_window":
                w = (getattr(self, "last_solved", None) or {}).get("window") or self.window()
                width = w["width_mm"] if w["width_mm"] is not None else -1e9
                row.update(limit=f">= {c.min:g} mm", measured=round(width, 1), unit="mm", margin=round(width - c.min, 1), ok=width >= c.min - 1e-6,
                           governing=f"towball {w['pct_min']:.1f} % at X {w['x_lo'] or 0:,.0f}, {w['ball_max']['governing']} at X {w['x_hi'] or 0:,.0f}",
                           detail=(f"axle from X {w['x_lo'] or 0:,.1f} (the lightest case at {w['pct_min']:.1f} %) to X {w['x_hi'] or 0:,.1f} (the heaviest towball "
                                   f"at {w['ball_max']['kg']:.1f} kg, {w['ball_max']['governing']}), set at X {lay.V['axle_x']:,.1f}"), window=w)
            elif c.type == "lateral":
                ids = [x["id"] for x in cases] if c.cases == "all" else c.cases
                bases = ["nominal", "growth"] if c.basis == "both" else [c.basis]
                worst = max(((abs(by_id[i][b]["cog"][1]), i, b) for i in ids for b in bases))
                v, cid, bs = worst
                y = by_id[cid][bs]["cog"][1]
                sides = by_id[cid][bs]["side_kg"]
                row.update(limit=f"<= {c.max:g} mm from the centreline", measured=round(v, 1), unit="mm", margin=round(c.max - v, 1), ok=v <= c.max + 1e-6,
                           governing=f"{cid} {by_id[cid]['name']} ({'with growth' if bs == 'growth' else 'no growth'})",
                           detail=(f"centre of gravity {abs(y):.1f} mm to the {'road' if y > 0 else 'kerb'} side in {cid}. Axle group sides: road "
                                   f"{sides['road']:,.0f} kg, kerb {sides['kerb']:,.0f} kg"))
            elif c.type == "bed":
                V = lay.V
                top = V["bed_night_h"] + V["deck_t"] + V["underlay_t"] + V["mattress_t"]
                parts = [("day underside", V["bed_day_h"] - 1600), ("night mattress top from 950", top - 950), ("night mattress top to 1,050", 1050 - top),
                         ("clear over the night mattress", V["interior_h"] - top - 900), ("night stop over the desk", V["bed_night_h"] - V["desk_top_h"] - 40)]
                gov = min(parts, key=lambda q: q[1])
                row.update(limit="H1: day underside >= 1,600, night top 950 to 1,050 with 900 clear, 40 above the desk", measured=round(top, 1), unit="mm",
                           margin=round(gov[1], 1), ok=gov[1] >= -1e-6, governing=gov[0],
                           detail=(f"day underside {V['bed_day_h']:.0f} mm, night underside {V['bed_night_h']:.0f} mm, night mattress top {top:.0f} mm with "
                                   f"{V['interior_h'] - top:.0f} mm clear above it, {V['bed_night_h'] - V['desk_top_h']:.0f} mm over the {V['desk_top_h']:.0f} mm desk"))
            elif c.type == "towball_scale":
                m = self.inputs.v("UTE-03")
                model = by_id[self.target_case.id]["nominal"]["towball_kg"]
                if m is None:
                    row.update(limit=f"within {100 * c.tolerance:.0f} % of the model", measured=None, unit="kg", margin=None, ok=False,
                               governing="not measured yet", detail=f"model {model:.0f} kg fully loaded. Not measured yet")
                else:
                    d = (m - model) / model
                    row.update(limit=f"within {100 * c.tolerance:.0f} % of the model", measured=m, unit="kg", margin=round(100 * (c.tolerance - abs(d)), 1),
                               ok=abs(d) <= c.tolerance, governing=f"model {model:.0f} kg", detail=f"scale {m:.0f} kg, model {model:.0f} kg ({100 * d:+.1f} %)")
            elif c.type == "fit":
                f = (self.layout(**{**lay.overrides, **c.state}) if c.state else lay).fit(c.zone)
                row.update(limit="inside the zone, no overlap", measured=f["smallest_gap_mm"], unit="mm", margin=f["smallest_gap_mm"],
                           ok=f["ok"], governing=f["governing"], problems=f["problems"],
                           detail=("all fit" if f["ok"] else ". ".join(f["problems"][:4])) + f", {f['items']} items, {f['keep_clear']} keep-clear spaces",
                           sub=lay.zones[c.zone]["name"])
            elif c.type == "tyre":
                t = self.tyre_arc(lay)
                row.update(limit=f">= {c.min_gap_mm:g} mm to every chassis member", measured=round(t["gap_mm"], 1), unit="mm",
                           margin=round(t["gap_mm"] - c.min_gap_mm, 1), ok=t["gap_mm"] >= c.min_gap_mm - 1e-6, governing=t["governing"],
                           detail=t["detail"], tyre=t)
            elif c.type.startswith("body_"):
                if not self.analyse_chassis:
                    continue
                from .body import check_row
                row.update(check_row(c, self.body_results(lay)))
            elif c.type.startswith("chassis_"):
                if not self.analyse_chassis:
                    continue
                from .chassis_checks import chassis_row
                row.update(chassis_row(c, self.chassis_results(lay)))
            elif c.type == "width":
                w = lay.width()
                row.update(limit=f"<= {c.max:g} mm", measured=round(w["width_mm"], 1), unit="mm", margin=round(c.max - w["width_mm"], 1),
                           ok=w["width_mm"] <= c.max + 1e-6, governing=f"{w['road']} to {w['kerb']}",
                           detail=f"{w['width_mm']:.0f} mm from the {w['road'].lower()} to the {w['kerb'].lower()}")
            elif c.type == "overhang":
                V = lay.V
                front = V["axle_x"] - V["body_x0"]
                end = lay.overall()["x1"]   # the rear-most part, the split's outdoor unit on the rear wall
                rear = end - V["axle_x"]
                row.update(limit="front load space >= rear overhang", measured=round(front, 1), unit="mm", margin=round(front - rear, 1),
                           ok=front >= rear - 1e-6, governing=f"axle at X {V['axle_x']:.0f}, rear-most part at X {end:.0f}",
                           detail=f"front load space {front:.0f} mm, rear overhang {rear:.0f} mm to X {end:.0f} ({V['body_x1'] - V['axle_x']:.0f} mm to the rear wall)")
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
            elif c.type in ("jackknife", "jackknife_height"):
                sw = self.tv["sweep"]
                R, under = sw["radius_mm"], sw["underside_z"]
                jk2 = next(x for x in self.prj.trailer_checks if x.type == "jackknife_height").min_gap_mm
                jk1 = next(x for x in self.prj.trailer_checks if x.type == "jackknife").min_gap_mm
                fps = lay.footprints()
                if c.type == "jackknife":
                    high = [f for f in fps if f["top"] > under - jk2]
                    w = min(high, key=lambda f: f["dist"])
                    v = w["dist"] - R
                    row.update(limit=f">= {c.min_gap_mm:g} mm outside the sweep", measured=round(v, 1), unit="mm", margin=round(v - c.min_gap_mm, 1),
                               ok=v >= c.min_gap_mm - 1e-6, governing=f"{w['name']} ({w['iid']})",
                               detail=(f"the bike box's rear corners sweep {R:.1f} mm about the ball ({sw['governing']}). Of the parts higher than "
                                       f"Z {under - jk2:.0f}, the nearest is {_lc(w['name'])}, {w['dist']:.0f} mm from the ball in plan, "
                                       f"{v:.0f} mm outside the sweep"), sweep=sw)
                else:
                    low = [f for f in fps if f["dist"] < R + jk1]
                    w = max(low, key=lambda f: f["top"])
                    v = under - w["top"]
                    row.update(limit=f">= {c.min_gap_mm:g} mm below the box", measured=round(v, 1), unit="mm", margin=round(v - c.min_gap_mm, 1),
                               ok=v >= c.min_gap_mm - 1e-6, governing=f"{w['name']} ({w['iid']})",
                               detail=(f"{len(low)} parts lie within {R + jk1:.0f} mm of the ball. The highest is {_lc(w['name'])}, "
                                       f"its top at Z {w['top']:.0f}, {v:.0f} mm under the bike box's underside at Z {under:.0f}"), sweep=sw)
            row["inputs"] = c.inputs
            row["status"] = ("PASS" if row["ok"] else "FAIL") if c.severity == "fail" else ("MEETS LIMIT" if row["ok"] else "REPORTED")
            out.append(row)
        return out


def tare_mass(lay: Layout, tr: Trailer) -> float:
    """The registration tare: TC1 as built."""
    tc1 = next(c for c in tr.cases if c.id == "TC1")
    return sum(m for b, m in lay.case_lines(tc1))


def load(prj: Project | None = None) -> Trailer:
    return Trailer(prj or Project())


# ------------------------------------------------------------------ outputs for the site, the drawing and TRAILER.md
def _r(v, n=1):
    if isinstance(v, float):
        return round(v, n)
    if isinstance(v, (list, tuple)):
        return [_r(x, n) for x in v]
    if isinstance(v, dict):
        return {k: _r(x, 3 if k in ("util", "measured", "margin") else 2 if k == "price_aud" else n) for k, x in v.items()}
    return v


def chassis_inputs(tr: Trailer, ev: dict) -> dict:
    lay = ev["layout"]
    V = lay.V
    cases = {c["id"]: c for c in ev["cases"]}
    tc2 = cases[tr.target_case.id]
    jk = next(r for r in ev["checks"] if r["id"] == "JK-01")
    xms = []
    for b in lay.blocks:
        if not b.extra.get("role", "").startswith("cm"):
            continue
        x = b.box[0]
        under = []
        for t in lay.tanks():
            if t.box[0] - 60 <= x <= t.box[3] + 10:
                under.append("water tank bay")
        grey = lay.find("UF-08").box
        if grey[0] - 60 <= x <= grey[3] + 10:
            under.append("grey tank bay")
        if x < V["body_x0"] - 1:
            under.append("drawbar")
        elif x < V["bed_x1"]:
            under.append("bed")
        elif x < V["rear_x0"]:
            under.append("living area")
        elif x < V["body_x1"] - 60:
            under.append("wet room")
        else:
            under.append("rear wall")
        xms.append(dict(x_front=x, x_rear=b.box[3], station=b.extra.get("station"), section=b.note,
                        under=", ".join(dict.fromkeys(under)), generated=b.generated, mass_kg=b.mass_kg))
    outriggers = sorted({o.box[0] for o in lay.blocks if o.extra.get("role") == "outrigger"})
    bars = [b for b in lay.blocks if b.bar]
    ov = lay.overall()
    spare = [b for b in lay.blocks if b.system == "spare" and b.box]
    return _r(dict(
        datum="X from the ball centre, positive rearward. Y from the centreline, positive to the road side. Z up from the ground at design ride height.",
        rail_outer_width=V["rail_outer_w"], rail_inner_width=2 * V["rail_in"], rail_centres=2 * V["rail_c"],
        track=V["track"], cf=V["cf"], wheel_offset=V["wheel_offset"],
        rail_section="RHS 150 x 50 x 3 C450L0 with a continuous RHS 127 x 51 x 3.5 C350L0 raiser (CHASSIS.md)",
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
        jackknife_mm=jk["measured"], jackknife_governing=jk["governing"], sweep=tr.tv["sweep"],
        spare_box=[min(b.box[i] for b in spare) if i < 3 else max(b.box[i] for b in spare) for i in range(6)],
        drawbar_box=list(lay.find("DX-01").box),
        tyre_d=V["tyre_d"], tyre_floor_clearance=V["tyre_clearance"], tank_capacity_l=lay.tank_capacity_l(),
        bed_x1=V["bed_x1"], rear_x0=V["rear_x0"],
        grey_tank_box=lay.find("UF-08").box, tanks=[t.box for t in lay.tanks()],
    ))


def schedule(lay: Layout, tr: Trailer) -> list[dict]:
    """MASS-01 mass schedule with the MASS-02 load-case flags, and each block's price (cad/trailer_costs.py)."""
    from .trailer_costs import block_prices
    flags = {}
    for c in tr.cases:
        for b, m in lay.case_lines(c):
            flags.setdefault(b.iid, set()).add(c.id)
    prices = block_prices(lay.blocks)
    rows = []
    for b in lay.blocks:
        if b.load == "none" or b.keep_clear:
            continue
        m = b.mass_kg
        price = prices.get(b.iid, {})
        rows.append(_r(dict(
            iid=b.iid, id=b.id, item=b.name, system=b.system, group=SYSTEM_LABELS[b.system], drawing="CT-001",
            qty=b.qty, unit_mass=b.unit_mass, basis=b.basis, mass_kg=m, maturity=b.maturity,
            growth_pct=round(b.growth * 100), mass_with_growth_kg=m * (1 + b.growth),
            source=b.source, note=b.note, mass_note=b.mass_note, load=b.load, material=b.material,
            cog=list(b.cog) if b.cog else None, box=list(b.box) if b.box else None, generated=b.generated,
            cases=sorted(flags.get(b.iid, [])), price_aud=price.get("price_aud"), price_basis=price.get("price_basis"),
            price_url=price.get("price_url"), price_date=price.get("price_date"), price_line=price.get("price_line"))))
    return rows


def measurement_refs(tr: Trailer, ev: dict) -> dict:
    """The model's figures that the measured inputs' ranges refer to ({ref: name} in data/measurements.yaml): the fully
    loaded towball, the model's mass at each weighbridge stage, the wheel and kit ratings the checks need, and the
    shortest ball reach and smallest C/F the clearance checks allow."""
    lay = ev["layout"]
    chk = {c["id"]: c for c in ev["checks"]}
    ute = {c["id"]: c for c in tr.tv["ute_checks"]}
    case = next(c for c in ev["cases"] if c["id"] == tr.target_case.id)
    refs = dict(
        towball_model=case["nominal"]["towball_kg"],
        wheel_need=max(chk["MAS-09"]["measured"], ute["UTE-12"]["measured"] or 0),
        gtm_need=max(chk["MAS-02"]["measured"], tr.supplier["need_kg"]),
        ball_reach_min=tr.inputs.v("UTE-02") - chk["JK-01"]["margin"],
        cf_min=tr.inputs.v("SUP-04") - chk["FIT-05"]["margin"],
    )
    # a weighbridge reading includes every stage built by then, so each stage's model figure adds the ones before. The
    # last one weighs the finished trailer, so its figure is the whole tare
    covered: set[str] = set()
    for iid in ("TW-01", "TW-02"):
        covered |= set(tr.inputs.items[iid].extra["covers"])
        refs[f"model_{iid}"] = sum(b.mass_kg for b in lay.blocks if b.load == "tare" and _stage_of(b) in covered)
    refs["model_TW-03"] = sum(b.mass_kg for b in lay.blocks if b.load == "tare")
    return refs


def report(tr: Trailer) -> dict:
    ev = tr.evaluate()
    lay = ev["layout"]
    V = lay.V
    zl = lay.zone_lengths()
    tr.inputs.resolve_ranges(measurement_refs(tr, ev))
    sys_tot: dict[str, dict] = {}
    for b, m in lay.case_lines(next(c for c in tr.cases if c.id == "TC1")):
        g = sys_tot.setdefault(SYSTEM_LABELS[b.system], dict(mass_kg=0.0, growth_kg=0.0))
        g["mass_kg"] += m
        g["growth_kg"] += m * (1 + b.growth)
    # the bike and chock inputs set the ute's bike box: their notes come from the ute garage's project
    tr.inputs.ball_behind_axle()
    ute_prj = Project(assembly="ute-garage")
    for k, v in ute_prj.inputs.outcomes.items():
        tr.inputs.outcomes.setdefault(k, v)
    tr.inputs.rule_spacing = ute_prj.inputs.rule_spacing
    tr.inputs.solved = ute_prj.inputs.solved
    tr.inputs.spacing_fits = ute_prj.inputs.spacing_fits
    tv = {k: v for k, v in tr.tv.items() if k != "ute_checks"}
    return _r(dict(
        assembly=dict(id=tr.td["id"], name=tr.td["name"], revision=tr.td["revision"]),
        body_length=V["body_length"], solved=ev["solved"], target_kg=tr.target,
        params={k: V[k] for k in sorted(V) if isinstance(V[k], (int, float))},
        zones=zl, zone_names={k: z["name"] for k, z in lay.zones.items()},
        cases=ev["cases"], checks=ev["checks"], least_certain=tr.least_certain(ev), chassis=chassis_inputs(tr, ev),
        schedule=schedule(lay, tr), tare_by_group=sys_tot, tare_kg=tare_mass(lay, tr), tow_vehicle=tv,
        target_why=tr.target_why, wheel=tr.wheel, supplier=tr.supplier, caps=tr.caps(), registration=tr.reg,
        weighed=tr.weighed_rows, spacing=dict(rule=ute_prj.inputs.rule_spacing, solved=ute_prj.inputs.solved,
                                              in_use=ute_prj.P.values["bike_spacing"], fits=ute_prj.inputs.spacing_fits),
        measurements=tr.inputs.report(),
    ))

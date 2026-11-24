"""Whole-trailer block layout: placement, mass schedule, load cases, axle solve and checks (TRAILER.md).

Everything is in the project datum DIM-01 (research/02): X from the coupling ball centre, positive rearward,
Y from the centreline, positive to the road side, Z up from the ground at design ride height. Blocks are
axis-aligned boxes, wheels are cylinders and the drawbar members are bars between two points.

Revision J (21 Nov 2026) is the home trailer (TRAILER.md): the bikes ride in the ute's bike box (UTE-GARAGE.md),
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
WEIGHINGS = ("TW-01", "TW-02", "TW-03")
SYSTEM_LABELS = {
    "drawbar": "Coupling and drawbar fittings", "chassis": "Chassis and drawbar", "running_gear": "Running gear", "body": "Body",
    "roof": "Roof", "underfloor": "Under the floor", "bed": "Bed", "living": "Living area",
    "stowage": "Drawbar box", "spare": "Spare wheel", "payload": "Payload",
    "electrical": "Electrical", "hvac": "HVAC and ventilation", "wet_room": "Wet room",
}
TOL = 0.5  # mm: boxes that only touch do not overlap
# the build order (data/assemblies/trailer.yaml build_order): the stage that fits each line, by its id or else its system
BUILD_ORDER = yaml.safe_load(TRAILER_YAML.read_text())["build_order"]
FIT_BY_ID = {k: s["stage"] for s in BUILD_ORDER for k in s["fits"] if k not in SYSTEM_LABELS}
FIT_BY_SYSTEM = {k: s["stage"] for s in BUILD_ORDER for k in s["fits"] if k in SYSTEM_LABELS}
WEIGH_LABELS = {s["stage"]: f"{s['label']} ({s['stage']})" for s in BUILD_ORDER}


# ------------------------------------------------------------------ the tow vehicle
def tow_vehicle(prj: Project) -> dict:
    """The Ranger Super Duty (data/ute/ute.yaml) and what the ute model gives the trailer (build/ute/ute.json): the ute's
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
    return dict(name=tv["name"], limits=lim, limit_src=src, gcm_case=tv["gcm_case"], case_name=case["name"],
                ute_kg=case["nominal"]["mass_kg"], ute_kg_growth=case["growth"]["mass_kg"], sweep=rep["bike_box_sweep"],
                rear_kg_growth=rear0, rear_kg_nominal=case["nominal"]["rear_kg"], rear_per_ball=per_ball,
                ball_behind_axle=rep["params"]["ball_behind_axle"], coupling_z=rep["params"]["coupling_z"],
                coupling_tol=rep["params"]["coupling_tol"],
                design_ball_kg=tow["growth"]["towball_kg"], tow_case=tow["id"], box_kg=rep["garage"]["box_kg"],
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


def _no_pts(x: dict) -> dict:
    """A lead's row from between_reach without its drawn points, for the checks' output."""
    out = {k: v for k, v in x.items() if k != "straight_pts"}
    if isinstance(out.get("low_ball"), dict):
        out["low_ball"] = {k: v for k, v in out["low_ball"].items() if k != "straight_pts"}
    return out


def _short(name: str) -> str:
    """A part's or fixture's name up to its first comma and space, so a figure such as "X 1,790" stays whole (I2-56)."""
    return name.split(", ")[0]


def _bar_box(bar) -> tuple:
    """The box round a member that runs at an angle in plan: its plan rectangle's corners and its depth."""
    (x0, y0, z0), (x1, y1, z1) = bar["p0"], bar["p1"]
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * bar["w"] / 2, (x1 - x0) / L * bar["w"] / 2
    xs, ys = [x0 + nx, x0 - nx, x1 + nx, x1 - nx], [y0 + ny, y0 - ny, y1 + ny, y1 - ny]
    return (min(xs), min(ys), min(z0, z1) - bar["h"] / 2, max(xs), max(ys), max(z0, z1) + bar["h"] / 2)


FLEXIBLE = ("DB-06",)   # the safety chains hang and swing, so the ground clearance checks leave them out


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
                 "load", "keep_clear", "hollow", "tank", "water", "when", "parts", "material", "price", "model", "net"}
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
            if it.get("net"):
                b.extra["net"] = dict(it["net"])
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

    def tank_nets(self) -> dict:
        """Each water tank's net capacity (review I2-40), by the grey tank's rule: the inside of its walls less a 10 mm air
        gap under its top and its baffles, each a sheet of the wall's thickness across the tank (`cross`) or along it
        (`along`), for the inside's height less the air gap. The fresh tanks' sum is what `water_full_l` may be."""
        out = {}
        for b in self.blocks:
            n = b.extra.get("net")
            if not n or b.box is None:
                continue
            t, gap = float(n["wall"]), float(n["air_gap"])
            lx, ly, lz = (b.box[3] - b.box[0] - 2 * t, b.box[4] - b.box[1] - 2 * t, b.box[5] - b.box[2] - 2 * t)
            h = lz - gap
            cross, along = int(n.get("cross", 0)), int(n.get("along", 0))
            baffles = (cross * ly + along * lx - cross * along * t) * t * h
            out[b.id] = dict(inside_mm=[round(lx, 1), round(ly, 1), round(lz, 1)], inside_l=lx * ly * lz / 1e6,
                             water_h_mm=h, baffles_l=baffles / 1e6, net_l=(lx * ly * h - baffles) / 1e6,
                             cross=cross, along=along, wall_mm=t, air_gap_mm=gap, fresh=bool(b.extra.get("tank")))
        return out

    def fresh_net_l(self) -> float:
        return sum(v["net_l"] for v in self.tank_nets().values() if v["fresh"])

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
        """Overall width over the solid blocks and everything that stands proud of the side walls (cad/body.py
        side_projections). Lamps and reflectors are left out, as ADR 43/04's definition and VSB1 5.2 leave them out."""
        from .body import side_projections
        ys = [(b.box[1], b.box[4], b.name, None) for b in self.blocks if b.solid and not b.extra.get("lamp")]
        ys += [(p["y0"], p["y1"], p["name"], p["proj"]) for p in side_projections(self)]
        lo = min(ys, key=lambda t: t[0])
        hi = max(ys, key=lambda t: t[1])
        return dict(width_mm=hi[1] - lo[0], road=hi[2], kerb=lo[2], road_y=hi[1], kerb_y=lo[0], road_proj=hi[3], kerb_proj=lo[3])

    def sprung_boxes(self) -> list[tuple]:
        """Every rigid part the suspension carries, as (block, box): each solid block, each angled drawbar member, each
        chassis fitting at each of its positions and each product's envelope, the spare wheel's included. What rides on
        the arms (UNSPRUNG) and the parts that bend (FLEXIBLE) are left out."""
        from .chassis import fitting_boxes
        from .chassis_fea import UNSPRUNG
        from .model import products as PR
        from .trailer_model import model_specs
        specs = model_specs(self)
        out = []
        for b in self.blocks:
            if b.keep_clear or b.load == "none" or b.id in UNSPRUNG or b.id in FLEXIBLE:
                continue
            if "fitting" in b.extra:
                boxes = fitting_boxes(self.chassis, b.extra["fitting"])
            elif b.id in specs:
                boxes = [bx for _, bx in PR.placements(specs[b.id], b, self)]
            elif b.bar:
                boxes = [_bar_box(b.bar)]
            else:
                boxes = [b.box] if b.box is not None else []
            out += [(b, bx) for bx in boxes]
        return out

    def underside_items(self) -> list[tuple]:
        """The parts the running clearance and the breakover look at, as (name, line, box): each rigid part the
        suspension carries (sprung_boxes). The trailer adds the services' fixtures and runs (Trailer.underside_items)."""
        return [(f"{b.name} ({b.iid})", b.id, bx) for b, bx in self.sprung_boxes()]

    def ground_clearance(self, items: list[tuple] | None = None) -> dict:
        """The lowest rigid part the suspension carries, at design ride height."""
        name, line, bx = min(items or self.underside_items(), key=lambda p: p[2][2])
        return dict(z_mm=bx[2], governing=name, line=line)

    def breakover(self, x_front: float, items: list[tuple] | None = None) -> dict:
        """The crest angle at which the ground between two contact lines, the ute's rear tyres at X x_front and the
        trailer's axle group, first touches a rigid sprung part: the sum of the slopes from each line up to the part's
        underside. For each part the sum is least at the point of its underside nearest the middle of the span."""
        xa = self.V["axle_x"]
        mid = (x_front + xa) / 2
        best = None
        for name, _, (x0, _, z0, x1, _, _) in items or self.underside_items():
            if x1 <= x_front or x0 >= xa:
                continue
            x = min(max(mid, x0, x_front + 1), x1, xa - 1)
            deg = math.degrees(math.atan2(z0, x - x_front) + math.atan2(z0, xa - x))
            if best is None or deg < best["deg"]:
                best = dict(deg=deg, x_mm=x, z_mm=z0, governing=name)
        return best

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
    """The build stage that fits a line (TRAILER.md build order): the stage that names its id, or else its system's."""
    return FIT_BY_ID.get(b.id) or FIT_BY_SYSTEM.get(b.system, "")


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
                           f"lightest case and {self.aw['towball_max_kg']:.0f} kg with growth in the heaviest (H17). The supplier's "
                           f"note on the axle group at the plate uses {self.target:.1f} kg, {100 * self.target / self.reg['plated_atm_kg']['v']:.1f} % of the "
                           f"{self.reg['plated_atm_kg']['v']:,.0f} kg plate")
        self.supplier = inp.supplier(self.reg["plated_atm_kg"]["v"], self.target, bool(self.td["params"].get("load_sharing", 0)))
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
        self._routes = None

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

    def routes(self, lay) -> dict:
        """The services' runs and fixtures resolved on this layout (cad/routes.py), once."""
        if self._routes is None or self._routes[0] is not lay:
            from . import routes as R
            self._routes = (lay, R.resolve(lay))
        return self._routes[1]

    def tyre_arc(self, lay) -> dict:
        """FIT-05: each tyre and each XT arm swung about the arm's pivot through its travel (report 11 section 5), against
        every rigid part the suspension carries (Layout.sprung_boxes: each solid block, chassis member, fitting and
        product envelope at its true size), every fixture of the services (data/routes.yaml) and every run at its outside
        diameter. The tyres' least gap to the chassis members alone is kept too: it is the one a smaller C/F closes (SUP-04)."""
        from . import routes as R
        from .chassis import tyre_clearance, wheel_sweep
        ch = self.chassis_model(lay)
        w = lay.V["tyre_w"]
        members = tyre_clearance(ch, [(m.id + " " + m.name, m.box()) for m in ch.members], w)
        res = self.routes(lay)
        boxes = [(f"{_short(b.name)} ({b.iid})", bx) for b, bx in lay.sprung_boxes()]
        boxes += [(f"{_short(f['what'])} ({k})", tuple(f["box"])) for k, f in res["fixtures"].items() if f.get("box") and not f.get("rides")]
        points = [(f"run {r['id']}", p, r["od"] / 2) for r in res["runs"] if not r.get("rides") for p, _ in R._samples(r["dense"], 10.0)]
        s = wheel_sweep(ch, w, boxes, points)
        lead = self._lead_sweep(ch, w, res, boxes, points)
        who = lambda b: f"the {b['part']} {b['wheel']} at {b['travel_mm']:+.0f} mm travel to {b['what']}"  # noqa: E731
        t, a = s["tyre"], s["arm"]
        worst = s if lead is None or s["gap_mm"] <= lead["gap_mm"] else lead
        leads = "" if lead is None else f", and the drum leads' arm parts {lead['gap_mm']:.1f} mm ({who(lead)})"
        return dict(gap_mm=worst["gap_mm"], governing=who(worst), tyre_gap_mm=t["gap_mm"], arm_gap_mm=a["gap_mm"],
                    lead_gap_mm=None if lead is None else lead["gap_mm"],
                    members_gap_mm=members["gap_mm"], members_governing=f"tyre {members['tyre']} to {members['member']}",
                    near=s["near"][:8], parts=len(boxes), run_points=len(points),
                    detail=(f"{worst['gap_mm']:.1f} mm, {who(worst)}. The tyres' least is {t['gap_mm']:.1f} mm ({who(t)}), the arms' "
                            f"{a['gap_mm']:.1f} mm ({who(a)}){leads}, over {len(boxes)} rigid parts and fixtures and every run"))

    def _lead_sweep(self, ch, tyre_w: float, res: dict, boxes: list, points: list, steps: int = 25, reach: float = 150.0) -> dict | None:
        """FIT-05 for the drum leads' arm parts (`rides: arm`, I2-50): each point of the part turns with its wheel's arm
        about the pivot through the arm's travel, against the rigid parts and fixtures and every run, as the arm does,
        but its own clip and its own sprung part (`joins`), which it is one cable with."""
        from . import routes as R
        from .chassis import swept_parts
        riders = [r for r in res["runs"] if r.get("rides") == "arm"]
        if not riders:
            return None
        travel = ch.V["travel"]
        travels = [-travel + 2 * travel * k / steps for k in range(steps + 1)]

        def arm_at(s):
            return {p["wheel"]: p for p in swept_parts(ch, tyre_w, s) if p["part"] == "arm"}

        angle = lambda p: math.atan2(p["hub"][1] - p["pivot"][1], p["hub"][0] - p["pivot"][0])  # noqa: E731
        rest = arm_at(0.0)
        turns = {s: {wid: angle(p) - angle(rest[wid]) for wid, p in arm_at(s).items()} for s in travels}
        best = None
        for r in riders:
            (px, pz), rq = rest[r["wheel"]]["pivot"], r["od"] / 2
            own = {f"run {r['id']}", f"run {r.get('joins')}"}
            ends = {r["from"]["line"], r["to"]["line"]}
            pts = [p for p, _ in R._samples(r["dense"], 10.0)]
            lo = [min(p[i] for p in pts) - reach for i in range(3)]
            hi = [max(p[i] for p in pts) + reach for i in range(3)]
            nb = [(n, b) for n, b in boxes if not any(n.endswith(f"({e})") for e in ends)
                  and all(b[i] <= hi[i] and b[i + 3] >= lo[i] for i in range(3))]
            nq = [(n, q, rr) for n, q, rr in points if n not in own and all(lo[i] <= q[i] <= hi[i] for i in range(3))]
            for s in travels:
                da = turns[s][r["wheel"]]
                c, sn = math.cos(da), math.sin(da)
                for q in pts:
                    dx, dz = q[0] - px, q[2] - pz
                    p = (px + dx * c - dz * sn, q[1], pz + dx * sn + dz * c)
                    for n, b in nb:
                        g = R._pt_box(p, b) - rq
                        if best is None or g < best["gap_mm"]:
                            best = dict(gap_mm=g, part=f"lead {r['id']}", wheel=r["wheel"], travel_mm=s, what=n)
                    for n, q2, r2 in nq:
                        g = math.dist(p, q2) - rq - r2
                        if best is None or g < best["gap_mm"]:
                            best = dict(gap_mm=g, part=f"lead {r['id']}", wheel=r["wheel"], travel_mm=s, what=n)
        return best

    def underside_items(self, lay) -> list[tuple]:
        """I2-41: what the running clearance (DIM-04, DIM-06) and the breakover (DIM-07) look at, as (name, line, box):
        every rigid part the suspension carries, every fixture of the services (data/routes.yaml) and every run's points
        at its outside diameter, as FIT-05 has them. A run that rides on the arms is left out, as the arms and the chains
        are, and so is the truck's socket. The leads between the vehicles are read as drawn, over their saddle with their
        bight hanging at their cut length (I2-63)."""
        from . import routes as R
        res = self.routes(lay)
        out = lay.underside_items()
        out += [(f"{_short(f['what'])} ({k})", k, tuple(f["box"])) for k, f in res["fixtures"].items() if f.get("box") and not f.get("rides")]
        for r in res["runs"]:
            if r.get("rides") == "arm":
                continue
            h = r["od"] / 2
            out += [(f"run {r['id']}", r["id"], (p[0] - h, p[1] - h, p[2] - h, p[0] + h, p[1] + h, p[2] + h))
                    for p, _ in R._samples(r["dense"], 10.0)]
        return out

    def leads_turned(self, lay, low: float) -> dict:
        """DIM-08 (I2-70, I2-78): the leads between the vehicles in every turn and pitch of rules.between, each lead's
        lowest point where its sprung arm holds it, at the design's coupling height and with the truck's ball at UTE-13's
        low end, its tolerance under it, the trailer turned nose down about its axle group (cad/routes.py between_reach)."""
        tol = self.tv["coupling_tol"]
        rows = self.leads_rows(lay)
        z = lay.V["coupling_z"]
        cases = [(x["turn_low_mm"], x["run"], z, x["turn_yaw"], x["turn_pitch"]) for x in rows]
        cases += [(x["low_ball"]["turn_low_mm"], x["run"], z - tol, x["low_ball"]["turn_yaw"], x["low_ball"]["turn_pitch"]) for x in rows]
        v, run, ball, yaw, pitch = min(cases)
        each = ". ".join(f"{x['run']} {x['turn_low_mm']:.1f} mm at the {z:.0f} mm ball and {x['low_ball']['turn_low_mm']:.1f} mm at "
                         f"{z - tol:.0f} mm, {x['turn_model']}" for x in rows)
        taut = sum(x.get("taut", 0) + x["low_ball"].get("taut", 0) for x in rows)
        ok = v >= low - 1e-6 and taut == 0
        return dict(limit=f">= {low:g} mm", measured=v, unit="mm", margin=round(v - low, 1), ok=ok,
                    governing=f"{run} with the ball at {ball:.0f} mm", leads=[_no_pts(x) for x in rows],
                    detail=(f"lowest {v:.1f} mm, {run} turned {abs(yaw)} degrees with a {abs(pitch)} degree pitch, the ball at {ball:.0f} mm. "
                            f"Each lead's lowest in any turn: {each}. Positions whose cut, less its margin, would pull a span taut: {taut}."))

    def leads_rows(self, lay) -> list:
        """The leads between the vehicles over every turn and pitch at both ball heights (cad/routes.py between_reach),
        worked once for each layout and shared by DIM-07 and DIM-08."""
        from . import routes as R
        key = id(lay)
        if getattr(self, "_leads", (None,))[0] != key:
            self._leads = (key, R.between_reach(self.routes(lay), ball_drop=self.tv["coupling_tol"]))
        return self._leads[1]

    def leads_breakover(self, lay, ahead: float) -> list:
        """DIM-07's look at the leads between the vehicles (I2-78): each as its sprung arm holds it straight ahead, by
        the model, at the design ball and with the ball at UTE-13's low end, as breakover rows."""
        out = []
        for x in self.leads_rows(lay):
            for ball, pts in (("the design ball", x.get("straight_pts")), ("the ball low", (x.get("low_ball") or {}).get("straight_pts"))):
                if not pts:
                    continue
                h = x["od"] / 2
                items = [(f"lead {x['run']} held up by its arm straight ahead", x["run"], (p[0] - h, p[1] - h, p[2] - h, p[0] + h, p[1] + h, p[2] + h))
                         for p in pts]
                bo = lay.breakover(-ahead, items)
                if bo:
                    out.append(dict(bo, run=x["run"], ball=ball))
        return out

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
                factor = 1.2 if c.quantity == "axle_vsb1" and not (self.supplier["includes_120"] or self.supplier["load_sharing"]) else 1.0
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
                # H20's one sum: the ute with growth, ball off, plus the trailer's plate (UTE-06), against Ford's GCM. There
                # is no revision to be refused, so no fallback plate and no water limit hang on it. `water_without` stays
                # the travel water for the drawings that still quote it
                tv, lim = self.tv, self.tv["limits"]
                plate = self.caps()["plated"]
                total = tv["ute_kg_growth"] + plate
                heavy = max(cases, key=lambda x: x["growth"]["mass_kg"])
                row.update(limit=f"<= {lim['gcm_kg']:,.0f} kg", measured=round(total, 1), unit="kg", margin=round(lim["gcm_kg"] - total, 1),
                           ok=total <= lim["gcm_kg"] + 1e-6, governing="the ute with growth plus the trailer's plate (UTE-06)",
                           detail=(f"the ute with the bikes aboard ({tv['gcm_case']}, {_kg(tv['ute_kg_growth'])} kg with growth) plus the "
                                   f"{plate:,.0f} kg plate is {_kg(total)} kg against Ford's {lim['gcm_kg']:,.0f} kg. The heaviest trailer case "
                                   f"with growth, {heavy['id']}, weighs {heavy['growth']['mass_kg']:,.0f} kg, under the plate"),
                           gcm=dict(sum=total, ute_kg_growth=tv["ute_kg_growth"], plate=plate, water_without=math.floor(lay.V["water_travel_l"]),
                                    trailer_case=heavy["id"], trailer_kg_growth=heavy["growth"]["mass_kg"]))
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
            elif c.type == "coupling_dv":
                # ADR 62/02 12.3.3 rates a coupling over 3.5 t by its D-value and V-value. The combination's own values, as
                # AS 2213.1 clauses 6 and 7 and UN R55 work them out, stay within the coupling's ratings
                cp, plate = self.reg["coupling"], self.caps()["plated"]
                T, R = self.tv["limits"]["gvm_kg"] / 1000, plate / 1000
                d_val = 9.81 * T * R / (T + R)
                ratio = max(1.0, (lay.V["body_length"] / lay.V["axle_x"]) ** 2)
                axles_t = (plate - self.reg["ball_floor_pct"] / 100 * plate) / 1000
                v_val = cp["a"] * ratio * axles_t
                m_d, m_v = cp["d_kn"] - d_val, cp["v_kn"] - v_val
                row.update(limit=f"D <= {cp['d_kn']:g} kN and V <= {cp['v_kn']:g} kN", measured=round(max(d_val / cp["d_kn"], v_val / cp["v_kn"]) * 100, 1),
                           unit="%", margin=round(100 * min(m_d / cp["d_kn"], m_v / cp["v_kn"]), 1), ok=min(m_d, m_v) >= -1e-6,
                           governing="D-value" if d_val / cp["d_kn"] >= v_val / cp["v_kn"] else "V-value",
                           detail=(f"D = 9.81 x {T:.3f} t x {R:.3f} t / {T + R:.3f} t = {d_val:.1f} kN against {cp['d_kn']:g} kN, the ute's "
                                   f"{T * 1000:,.0f} kg GVM with the {plate:,.0f} kg plate. V = {cp['a']:g} m/s2 x {ratio:.2f} x {axles_t:.2f} t = "
                                   f"{v_val:.1f} kN against {cp['v_kn']:g} kN: X/l is the {lay.V['body_length']:,.0f} mm body over the "
                                   f"{lay.V['axle_x']:,.0f} mm from the ball to the axle group, squared and at least 1, and C the axle group at the "
                                   f"plate with {self.reg['ball_floor_pct']:g} % on the ball"),
                           coupling=dict(d_kn=d_val, v_kn=v_val, d_rating=cp["d_kn"], v_rating=cp["v_kn"]))
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
            elif c.type == "bed_load":
                from .body import load_data
                L = load_data()["loads"]
                night, moving = L["bed_kg"], L["bed_travel_kg"]
                m_s, m_m = L["bed_static_rating_kg"] - night, L["bed_moving_rating_kg"] - moving
                row.update(limit=f"<= {L['bed_static_rating_kg']:.0f} kg static, <= {L['bed_moving_rating_kg']:.0f} kg moving", measured=night, unit="kg",
                           margin=min(m_s, m_m), ok=min(m_s, m_m) >= 0, governing="the bed at night with two sleepers" if m_s <= m_m else "the bed moving",
                           detail=(f"at night {night:.0f} kg, the {moving:.0f} kg moving bed and two sleepers, against the {L['bed_static_rating_kg']:.0f} kg static "
                                   f"rating ({100 * night / L['bed_static_rating_kg']:.0f} %, so the two together at most about "
                                   f"{L['bed_static_rating_kg'] - moving:.0f} kg). Moving, {moving:.0f} kg against {L['bed_moving_rating_kg']:.0f} kg"))
            elif c.type == "rollover":
                st = self.td["stability"]
                rs = [rollover(lay, by_id[x["id"]], st, bs) for x in cases for bs in ("nominal", "growth")]
                w = min(rs, key=lambda q: q["srt"])
                ssf = min(q["ssf"] for q in rs)
                ute = next((u for u in self.tv["ute_checks"] if u["id"] == "UTE-11"), None)
                per100 = min(rollover(lay, by_id[x["id"]], st, bs, 100.0)["srt"] for x in cases for bs in ("nominal", "growth")) - w["srt"]
                row.update(limit=f">= {c.min:.2f} g", measured=round(w["srt"], 3), unit="g", margin=round(w["srt"] - c.min, 3),
                           ok=w["srt"] >= c.min - 1e-9, governing=f"{w['case']}, centre of gravity {w['h']:,.0f} mm up and {w['y0']:.0f} mm off the centreline",
                           detail=(f"lowest {w['srt']:.2f} g ({w['case']}), against a static stability factor of {w['ssf']:.2f} there and {ssf:.2f} at the "
                                   f"lowest. At the threshold the body has rolled {w['roll_deg']:.1f} degrees, "
                                   f"{'onto its bump stops, ' if w['on_stops'] else ''}and the centre of gravity has moved {w['shift_mm']:.0f} mm toward the "
                                   f"outer wheels. Each 100 mm more track, through the rails, adds about {per100:.2f} g"
                                   + (f". The ute with the bikes aboard: static stability factor {ute['measured']:.2f} (UTE-11)" if ute and ute.get("measured") else "")),
                           rollover=w)
            elif c.type == "yaw":
                low = min(cases, key=lambda x: min(x["nominal"]["towball_pct"], x["growth"]["towball_pct"]))
                pct = min(low["nominal"]["towball_pct"], low["growth"]["towball_pct"])
                heavy = max(cases, key=lambda x: x["growth"]["mass_kg"])
                yi = yaw_inertia(lay, next(cc for cc in self.cases if cc.id == heavy["id"]))
                yl = yaw_inertia(lay, next(cc for cc in self.cases if cc.id == low["id"]))
                row.update(limit="reported", measured=round(yi["I_kgm2"], 0), unit="kg m2", margin=None, ok=True,
                           governing=f"{low['id']}, the lowest towball share", yaw=dict(heavy=yi, low=yl, pct=pct),
                           detail=(f"yaw inertia about the centre of gravity {yi['I_kgm2']:,.0f} kg m2 in {heavy['id']} with growth, radius of gyration "
                                   f"{yi['k_m']:.2f} m against {lay.V['axle_x'] / 1000:.2f} m from the ball to the axles. In {low['id']}, the lowest towball "
                                   f"share at {pct:.1f} %, {yl['I_kgm2']:,.0f} kg m2 with its centre of gravity {yl['x_cg'] - lay.V['axle_x']:+,.0f} mm "
                                   f"from the axles. No snaking speed: the published car and trailer models need the ute's and the trailer's tyre cornering "
                                   f"stiffnesses and the hitch's geometry, none of them known"))
            elif c.type == "overturn":
                from .body import load_data
                st, wd = self.td["stability"], load_data()["wind"]
                sil = side_silhouette(lay, st["overturn"]["cell_mm"])
                ids = [x["id"] for x in cases] if c.cases == "all" else c.cases
                rs = [overturn(lay, by_id[i], st, sil, wd["Mzcat"]) for i in ids]
                w, hv = min(rs, key=lambda q: q["v_low"]), max(rs, key=lambda q: q["v"])
                o = st["overturn"]
                act = min(q["act_kmh"] for q in rs)
                v_act = act / 3.6 * wd["Mzcat"]
                f_slide, f_tip = (w["v_slide"] / v_act) ** 2, (w["v"] / v_act) ** 2
                how = "slides" if w["v_slide"] <= w["v"] else "tips"
                row.update(limit="reported", measured=round(w["v_low"], 1), unit="m/s", margin=None, ok=True,
                           governing=f"{w['case']} {by_id[w['case']]['name']}, no growth, {how} first",
                           detail=(f"side silhouette {sil['area_m2']:.1f} m2, its centroid {sil['z_mm']:,.0f} mm up, Cf {o['cf']:g} for both. "
                                   + ". ".join(f"{q['case']} at {q['mass_kg']:,.0f} kg slides at {q['v_slide']:.1f} m/s at the trailer on wet grass "
                                               f"(friction {o['friction']:g}, est.), a {q['slide_forecast_kmh']:.0f} km/h forecast gust, and tips at "
                                               f"{q['v']:.1f} m/s, a {q['forecast_kmh']:.0f} km/h forecast gust" for q in rs)
                                   + f". With a box's Cf of {o['cf_box']:g} the heaviest would tip at {hv['v_box']:.1f} m/s. The operating rule acts "
                                   f"at forecast gusts of {act:.0f} km/h, the lower speed over the square root of {o['moment_factor']:g}, rounded down to "
                                   f"5 km/h, so in the lightest case the wind's force has a factor of {f_slide:.2f} against sliding and {f_tip:.2f} "
                                   f"against tipping. The Bureau warns of damaging winds from {o['warning_kmh']:.0f} km/h gusts, so a warning always "
                                   f"meets the rule. Strapped down it holds to region B's 500-year gust (STB-05). The walls' strength wind, "
                                   f"{wd['V_u']:g} m/s, covers the highest overturning speed, {max(hv['v'], hv['v_box']):.1f} m/s with a box's Cf (H23)"),
                           overturn=dict(cases=rs, silhouette=sil, act_kmh=act, warning_kmh=o["warning_kmh"], v_low=w["v_low"], low_case=w["case"],
                                         how=how, v_u=wd["V_u"], cf=o["cf"], cf_box=o["cf_box"], factor=o["moment_factor"], friction=o["friction"],
                                         slide_factor=f_slide, tip_factor=f_tip))
            elif c.type == "tie_down":
                from .body import load_data
                st, wd = self.td["stability"], load_data()["wind"]
                o = st["overturn"]
                td = o["tie_down"]
                sil = side_silhouette(lay, o["cell_mm"])
                ids = [x["id"] for x in cases] if c.cases == "all" else c.cases
                rs = [tie_down(lay, overturn(lay, by_id[i], st, sil, wd["Mzcat"]), st, sil, wd["Mzcat"]) for i in ids]
                w = max(rs, key=lambda q: q["util"])
                row.update(limit="<= 1.00 utilisation", measured=round(w["util"], 2), unit="", margin=round(1 - w["util"], 2), ok=w["util"] <= 1.0,
                           governing=f"{w['case']}, {w['governs']}, the {w['governing']}",
                           detail=(f"region B's 500-year gust at 3 m, {td['v_r_ms']:g} m/s times {wd['Mzcat']:g}, {w['v']:.1f} m/s, with Cf {o['cf']:g} on "
                                   f"the {sil['area_m2']:.1f} m2 side silhouette, {w['push_n'] / 1000:.1f} kN. "
                                   + ". ".join(f"{q['case']} at {q['mass_kg']:,.0f} kg: each windward strap {q['t_tip_n'] / 1000:.1f} kN against tipping "
                                               f"and {q['t_slide_n'] / 1000:.1f} kN against sliding on wet grass (friction {o['friction']:g}, est.)" for q in rs)
                                   + f". At {w['t_n'] / 1000:.1f} kN the strap works at {w['utils']['strap']:.2f} of its {td['strap_lc_n'] / 1000:.1f} kN "
                                   f"lashing capacity, the D-ring at {w['utils']['lug']:.2f} of its {td['lug_wll_n'] / 1000:.1f} kN working load limit and "
                                   f"the outrigger at {w['outrigger_mpa']:.0f} MPa, {w['utils']['outrigger']:.2f} of its yield over 1.5. Each strap runs at "
                                   f"{min(w['angles']):g} to {max(w['angles']):g} degrees to the ground, each force taken at its worst angle there, with "
                                   f"the anchor's head {w['head_mm'][0]:,.0f} to {w['head_mm'][1]:,.0f} mm out from the point under its lashing point on "
                                   "level ground. "
                                   + ". ".join(_anchor_txt(a, td) for a in w["anchors"])),
                           tie_down=dict(cases=rs, v=w["v"]))
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
                row.update(limit=f">= {c.min_gap_mm:g} mm from every rigid part, fixture and run", measured=round(t["gap_mm"], 1), unit="mm",
                           margin=round(t["gap_mm"] - c.min_gap_mm, 1), ok=t["gap_mm"] >= c.min_gap_mm - 1e-6, governing=t["governing"],
                           detail=t["detail"], tyre=dict(t, members_margin=round(t["members_gap_mm"] - c.min_gap_mm, 1)))
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
                side = lambda s: (f"{_lc(w[s])}, {w[s + '_proj']:.0f} mm proud of the skin" if w[s + "_proj"] is not None  # noqa: E731
                                  else _lc(w[s]))
                row.update(limit=f"<= {c.max:,.0f} mm", measured=round(w["width_mm"], 1), unit="mm", margin=round(c.max - w["width_mm"], 1),
                           ok=w["width_mm"] <= c.max + 1e-6, governing=f"{w['road']} to {w['kerb']}",
                           detail=(f"{w['width_mm']:,.0f} mm over the {lay.V['body_width']:,.0f} mm body. Road side: {side('road')}. "
                                   f"Kerb side: {side('kerb')}. The side marker lamps and reflectors are left out"))
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
                g = lay.ground_clearance(self.underside_items(lay))
                row.update(limit=f">= {c.min:g} mm", measured=round(g["z_mm"], 1), unit="mm", margin=round(g["z_mm"] - c.min, 1),
                           ok=g["z_mm"] >= c.min, governing=g["governing"], line=g["line"],
                           detail=f"lowest rigid sprung part {g['z_mm']:.1f} mm above the ground at design ride height, {g['governing']}")
            elif c.type == "clearance_leads":
                row.update(self.leads_turned(lay, c.min))
            elif c.type == "breakover":
                ahead = self.tv["ball_behind_axle"]
                leads = self.leads_breakover(lay, ahead)
                held = {x["run"] for x in leads}
                items = [i for i in self.underside_items(lay) if i[1] not in held]
                items += [(x["governing"], x["run"], (x["x_mm"] - 1, 0.0, x["z_mm"], x["x_mm"] + 1, 0.0, x["z_mm"]))
                          for x in leads if x["ball"] == "the design ball"]
                bo = lay.breakover(-ahead, items)
                each = ", ".join(f"{x['run']} {x['deg']:.1f} degrees with {x['ball']}" for x in leads)
                row.update(limit="reported", measured=round(bo["deg"], 1), unit="deg", margin=None, ok=True, governing=bo["governing"],
                           detail=(f"{bo['deg']:.1f} degrees, a crest under {bo['governing']} at X {bo['x_mm']:,.0f} mm, its underside "
                                   f"{bo['z_mm']:.1f} mm up, between the ute's rear axle {ahead:,.0f} mm ahead of the ball and the trailer's "
                                   f"axle group at X {lay.V['axle_x']:,.1f} mm. The leads between the vehicles as their sprung arms hold "
                                   f"them straight ahead (cad/routes.py lifted): {each}"))
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


def _kg(v: float) -> str:
    """A mass to the whole kg, rounded half up as the site rounds it, so a figure such as the combination's 7,120.5 kg
    reads the same in every check, sheet and page (Python's format rounds half to even)."""
    from decimal import ROUND_HALF_UP, Decimal
    return f"{Decimal(str(round(v, 6))).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"


def rollover(lay: Layout, ev: dict, st: dict, basis: str = "growth", dtrack: float = 0.0) -> dict:
    """Static rollover threshold of one case (data/assemblies/trailer.yaml `stability`, Gillespie 1992 chapter 9): the
    steady lateral acceleration, in g, at which the inner wheels lift. The roll centre is at the ground under the XT's
    trailing arms. The body rolls on its air springs until the outer bump stops land and squash, and on its tyres, and
    the centre of gravity moves out by its height times the roll plus the outer tyres' lateral give. `dtrack` widens the
    track through the rails, so the air springs move out by half of it too (H22)."""
    V = lay.V
    r = ev[basis]
    W, h, y0 = r["mass_kg"] * 9.81, r["cog"][2], abs(r["cog"][1])
    half = (V["track"] + dtrack) / 2
    ys = V["rail_c"] + dtrack / 2                      # the air springs and bump stops sit under the rails
    k_s = 4 * st["air_spring_rate"] * ys ** 2          # N mm/rad, four air springs
    k_t = 4 * st["tyre_rate"] * half ** 2              # N mm/rad, four tyres
    phi_stop = (st["bump_gap_mm"] + st["bump_squash_mm"]) / ys
    a = (half - y0) / h
    phi = dy = 0.0
    for _ in range(200):
        for _ in range(100):                           # roll under the lateral load and the centre of gravity's own shift
            m = W * h * (a + phi)
            phi = min(m / k_s, phi_stop) + m / k_t
        dy = h * phi + W * a / (2 * st["tyre_lateral_rate"])
        a_new = (half - y0 - dy) / h
        if abs(a_new - a) < 1e-6:
            break
        a = 0.5 * (a + a_new)
    return dict(srt=a, ssf=(half - y0) / h, roll_deg=math.degrees(phi), shift_mm=dy, on_stops=W * h * (a + phi) / k_s >= phi_stop,
                h=h, y0=y0, case=ev["id"])


def side_silhouette(lay: Layout, cell: float = 10.0) -> dict:
    """The trailer seen from the side: every solid block, wheel and frame member projected on the X-Z plane on a `cell`
    mm grid, lamps and keep-clear spaces left out. The area and its centroid height, for the wind on the parked trailer
    (STB-04). Gaps between the frame members, the tanks and the wheels stay open."""
    import numpy as np
    shapes = []
    for b in lay.blocks:
        if b.keep_clear or b.load == "none" or b.extra.get("lamp"):
            continue
        if b.box is not None:
            shapes.append(("box", b.box[0], b.box[2], b.box[3], b.box[5]))
        elif b.cyl:
            c, r = b.cyl["c"], b.cyl["r"]
            shapes.append(("cyl", c[0], c[2], r, r))
        elif b.bar:
            (x0, _, z0), (x1, _, z1) = b.bar["p0"], b.bar["p1"]
            shapes.append(("bar", x0, z0, x1, z1, b.bar["h"]))
    def extent(s):     # x0, x1, z1 of a shape
        if s[0] == "box":
            return s[1], s[3], s[4]
        if s[0] == "cyl":
            return s[1] - s[3], s[1] + s[3], s[2] + s[3]
        return min(s[1], s[3]), max(s[1], s[3]), max(s[2], s[4]) + s[5] / 2
    ext = [extent(s) for s in shapes]
    x_lo = min(e[0] for e in ext) - cell
    x_hi = max(e[1] for e in ext) + cell
    z_hi = max(e[2] for e in ext) + cell
    gx = np.arange(x_lo, x_hi, cell) + cell / 2
    gz = np.arange(0.0, z_hi, cell) + cell / 2
    Z, X = np.meshgrid(gz, gx, indexing="ij")
    on = np.zeros(X.shape, dtype=bool)
    for s in shapes:
        if s[0] == "box":
            on |= (X >= s[1]) & (X <= s[3]) & (Z >= s[2]) & (Z <= s[4])
        elif s[0] == "cyl":
            on |= (X - s[1]) ** 2 + (Z - s[2]) ** 2 <= s[3] ** 2
        else:
            x0, z0, x1, z1, hh = s[1:]
            L = math.hypot(x1 - x0, z1 - z0) or 1.0
            t = ((X - x0) * (x1 - x0) + (Z - z0) * (z1 - z0)) / L ** 2
            d = np.abs((X - x0) * (z1 - z0) - (Z - z0) * (x1 - x0)) / L
            on |= (t >= 0) & (t <= 1) & (d <= hh / 2)
    area = on.sum() * cell ** 2
    return dict(area_m2=area / 1e6, z_mm=float((Z * on).sum() * cell ** 2 / area), x_mm=float((X * on).sum() * cell ** 2 / area),
                x0=float(x_lo), x1=float(x_hi))


def overturn(lay: Layout, ev: dict, st: dict, sil: dict, mzcat: float, basis: str = "nominal") -> dict:
    """STB-04 (decision H23): the side wind at which the parked trailer, unhitched on its corner steadies, starts to tip
    about its leeward wheels. The wind is taken toward the side the centre of gravity already leans to. The steadies stand
    under the rails, inboard of the wheels, so they widen nothing, but wound down they hold the body on its springs. The
    weight's lever is the half track less that lean,
    less the roll on the tyres as the leeward pair takes the whole weight and their sideways give under the wind's push
    (the `stability` rates). The push is 0.6 V^2 Cf on the side silhouette, at its centroid height. V is the gust at the
    trailer's height in terrain category 2. The forecast gust, at 10 m in open country, is V over M_z,cat."""
    V, o = lay.V, st["overturn"]
    r = ev[basis]
    W, h, y0 = r["mass_kg"] * 9.81, r["cog"][2], abs(r["cog"][1])
    half = V["track"] / 2
    roll = W / (2 * st["tyre_rate"] * V["track"])           # rad: the leeward tyres take W / 2 each, the windward ones lift
    zc = sil["z_mm"]
    lever = (half - y0 - h * roll) / (1 + W / (4 * st["tyre_lateral_rate"] * zc))
    out = dict(case=ev["id"], basis=basis, mass_kg=r["mass_kg"], lever_mm=lever, h=h, y0=y0, area_m2=sil["area_m2"], z_cp=zc,
               push_n=W * lever / zc)
    for key, cf in (("v", o["cf"]), ("v_box", o["cf_box"])):
        q = W * lever / (cf * sil["area_m2"] * zc)            # Pa: N mm over (m2 mm)
        out[key] = math.sqrt(q / 0.6)
    out["v_slide"] = math.sqrt(o["friction"] * W / (0.6 * o["cf"] * sil["area_m2"]))   # the push passes the friction on wet grass
    out["slide_forecast_kmh"] = out["v_slide"] / mzcat * 3.6
    out["forecast_kmh"] = out["v"] / mzcat * 3.6
    # the rule (H23, F4-06): the lower of the two speeds with the same Cf, over the square root of the factor on force
    out["v_low"] = min(out["v"], out["v_slide"])
    out["v_act"] = out["v_low"] / math.sqrt(o["moment_factor"])
    out["act_kmh"] = 5 * math.floor(out["v_act"] / mzcat * 3.6 / 5)
    return out


def _anchor_txt(a: dict, td: dict) -> str:
    """STB-05's sentences for the kit's anchor (F5-01, F6-01): the product, the installation its listing tested, the plate
    the kit takes for the listing's device, its listed loads in HUD's soil classes, quoted term by term from 24 CFR
    3285.202's table, and the probe value the soil must read."""
    cl = td["hud_classes"]

    def q(c):
        t = [f'"{x}"' for x in cl[c]["terms"]]
        return ", ".join(t[:-1]) + " and " + t[-1]

    lo, hi = cl[a["soil_class"]]["probe_inlb"]
    name, _, spec = a["name"].partition(", ")
    model = spec.split(",")[0].split()[-1]
    return (f"Each anchor is a {name} ({spec}), installed as {a['listing']} tested it: wound into undisturbed soil, never dug in and "
            f"backfilled, at a {a['back_angle_deg']:g} degree back angle to its full depth, its head at the ground and its helix about "
            f"{a['helix_mm'] / 1000:.2f} m down, with {a['plate']} driven vertically on the trailer side of its rod, and pulled at no less "
            f"than the listing's {a['min_angle_deg']:g} degree minimum angle. The listing's Table 1 names stabilizer {a['listed_plate']} for "
            f"the {model}. The kit takes the {a['plate_no']}, which Tie Down's anchor chart and plate sheet give for the {name.split()[-1]}, "
            f"on the assumption that it is the listing's device under its catalogue number, and Tie Down confirms it in writing before the "
            f"plates are bought (TRAILER.md, open points). The listing rates it at {a['wll_lb']:,} lb ({a['wll_n'] / 1000:.1f} kN) working and {a['ultimate_lb']:,} lb "
            f"({a['ultimate_n'] / 1000:.1f} kN) ultimate in HUD's class {a['soil_class']}, {q(a['soil_class'])}, {lo} to {hi} in-lb on the "
            f"torque probe, and in the firmer classes. It works at {a['util']:.2f} of its working load, a factor of {a['factor']:.2f} on its "
            f"ultimate. The soil is measured, not judged: {td['probe']}, driven to the helix depth, must read at least {a['min_probe_inlb']} "
            f"in-lb ({a['probe_nm']:.1f} N m), the Missouri Public Service Commission's figure for this anchor, above HUD's {lo} in-lb for "
            f"class {a['soil_class']}. Where it reads less, as in class 5, {q('5')}, under {cl['5']['probe_inlb'][1] + 1} in-lb, or where an "
            f"anchor will not wind in to its full depth, no anchor in the kit is rated: hitch the trailer or move it")


def tie_down(lay: Layout, ot: dict, st: dict, sil: dict, mzcat: float) -> dict:
    """STB-05 (F3-03, F5-01): the windward pair of straps from the lashing points under the outrigger ends, holding the
    parked trailer against tipping and sliding in region B's 500-year gust at 3 m. Moments about the leeward wheels' line
    on the ground, with STB-04's weight and lever. Each strap runs down and out to windward at any angle in `angle_deg`,
    so each force is taken at its worst angle there: tipping at the shallowest, sliding and the outrigger at the steepest.
    The anchor counts at its listed working load only if the shallowest angle is no less than its listed minimum."""
    V, o = lay.V, st["overturn"]
    td = o["tie_down"]
    v = td["v_r_ms"] * mzcat
    F = 0.6 * v ** 2 * o["cf"] * sil["area_m2"]
    W = ot["mass_kg"] * 9.81
    angles = list(td["angle_deg"]) if isinstance(td["angle_deg"], (list, tuple)) else [td["angle_deg"]]
    t_tip = t_slide = s_out = 0.0
    for deg in angles:
        a = math.radians(deg)
        sa, ca = math.sin(a), math.cos(a)
        arm = (V["track"] / 2 + td["lug_y_mm"]) * sa + td["lug_z_mm"] * ca       # mm, each strap's restoring lever
        tt = max(0.0, (F * sil["z_mm"] - W * ot["lever_mm"]) / (2 * arm))
        ts = max(0.0, (F - o["friction"] * W) / (2 * (o["friction"] * sa + ca)))
        t_tip, t_slide = max(t_tip, tt), max(t_slide, ts)
        s_out = max(s_out, max(tt, ts) * sa * td["outrigger_l_mm"] / td["outrigger_z_mm3"])
    t = max(t_tip, t_slide)
    utils = dict(strap=t / td["strap_lc_n"], lug=t / td["lug_wll_n"], outrigger=s_out / (td["outrigger_fy"] / 1.5))
    anchors = []
    for an in td["anchors"]:
        listed = min(angles) >= an["min_angle_deg"] - 1e-9
        anchors.append(dict(an, listed=listed, util=t / (an["per_strap"] * an["wll_n"]) if listed else 99.0,
                            factor=an["per_strap"] * an["ultimate_n"] / t if t else 99.0,
                            helix_mm=an["rod_mm"] * math.cos(math.radians(an["back_angle_deg"])), probe_nm=an["min_probe_inlb"] * 0.1129848))
    utils["anchor"] = max(an["util"] for an in anchors)
    gov = max(utils, key=utils.get)
    head = [td["lug_z_mm"] / math.tan(math.radians(d)) for d in angles]
    return dict(case=ot["case"], mass_kg=ot["mass_kg"], v=v, push_n=F, t_tip_n=t_tip, t_slide_n=t_slide, t_n=t, anchors=anchors,
                governs="sliding" if t_slide >= t_tip else "tipping", outrigger_mpa=s_out, utils=utils, governing=gov, util=utils[gov],
                angles=angles, head_mm=(min(head), max(head)))


def yaw_inertia(lay: Layout, case, basis: str = "growth") -> dict:
    """Yaw inertia about the vertical axis through the case's centre of gravity, kg m2: every line as a point mass at its
    centre of gravity plus, for a block, its own inertia as a uniform box."""
    rows = [(m * (1 + b.growth) if basis == "growth" else m, b) for b, m in lay.case_lines(case)]
    M = sum(m for m, _ in rows)
    xc = sum(m * b.cog[0] for m, b in rows) / M
    yc = sum(m * b.cog[1] for m, b in rows) / M
    I = 0.0
    for m, b in rows:
        I += m * ((b.cog[0] - xc) ** 2 + (b.cog[1] - yc) ** 2)
        if b.box is not None and b.load == "tare":
            I += m * ((b.box[3] - b.box[0]) ** 2 + (b.box[4] - b.box[1]) ** 2) / 12
    return dict(I_kgm2=I / 1e6, mass_kg=M, x_cg=xc, k_m=math.sqrt(I / M) / 1000)


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
        return {k: _r(x, 3 if k in ("util", "measured", "margin", "damage") else 2 if k == "price_aud" else n) for k, x in v.items()}
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
        rail_section="RHS 150 x 50 x 4 C450L0 with a continuous RHS 127 x 51 x 3.5 C350L0 raiser (CHASSIS.md)",
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
        overall_width=lay.width()["width_mm"], width_kerb_y=lay.width()["kerb_y"], width_road_y=lay.width()["road_y"],
        travel_height_at=max((b for b in lay.blocks if b.solid), key=lambda b: b.box[5]).id,
        body_x0=V["body_x0"], body_x1=V["body_x1"],
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
    cases = {c["id"]: c for c in ev["cases"]}
    refs = dict(
        towball_model=case["nominal"]["towball_kg"],
        wheel_need=chk["MAS-09"]["measured"],   # the trailer's own wheel since the Super Duty's 8-stud 18 in wheels
        gtm_need=max(chk["MAS-02"]["measured"], tr.supplier["need_kg"]),
        ball_reach_min=tr.inputs.v("UTE-02") - chk["JK-01"]["margin"],
        # the least tow ball download the truck's label may give with the axle where it is: the heaviest towball with
        # growth plus what H17 keeps in hand under the truck's limit (VEH-08)
        towball_label_min=max(c["growth"]["towball_kg"] for c in ev["cases"])
        + tr.tv["limits"]["towball_rating_kg"] - tr.aw["towball_max_kg"],
        cf_min=tr.inputs.v("SUP-04") - chk["FIT-05"]["tyre"]["members_margin"],
        # the fully loaded weighing (TW-04, TW-05) and the tare centre of gravity height (TR-01), without growth
        model_TC2=cases["TC2"]["nominal"]["mass_kg"], axle_TC2=cases["TC2"]["nominal"]["axle_kg"],
        cog_z_TC1=cases["TC1"]["nominal"]["cog"][2],
        # the car build's and the bike box's design values on the measurement sheet, from the ute's model (F4-06)
        ute_rear_towing=ute["UTE-03"]["measured"], ute_front_bikes=ute["UTE-02"]["measured"],
        ute_added_cog_x=ute["UTE-07"]["measured"], ute_gvm_towing=ute["UTE-01"]["measured"],
        combination=tr.tv["ute_kg_growth"] + cases["TC2"]["growth"]["mass_kg"],
        box_kg=tr.tv["box_kg"],
    )
    for iid, st in weighbridge(tr, lay).items():
        refs[f"model_{iid}"] = st["model_kg"]
    return refs


def weighbridge(tr: Trailer, lay: Layout) -> dict:
    """Each weighbridge stage: the parts it adds to the scale with their model mass, and the model's reading, which
    includes every stage before it."""
    kg: dict[str, float] = {}
    for b in lay.blocks:
        if b.load == "tare":
            kg[_stage_of(b)] = kg.get(_stage_of(b), 0.0) + b.mass_kg
    out, reading = {}, 0.0
    for iid in WEIGHINGS:
        covers = tr.inputs.items[iid].extra["covers"]
        reading += sum(kg.get(k, 0.0) for k in covers)
        out[iid] = dict(adds=[dict(part=WEIGH_LABELS[k], kg=kg.get(k, 0.0)) for k in covers], model_kg=reading)
    return out


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
    stages = weighbridge(tr, lay)
    measurements = tr.inputs.report()
    for row in measurements:
        if row["id"] in stages:
            row["adds"] = stages[row["id"]]["adds"]
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
        measurements=measurements, tanks=dict(nets=lay.tank_nets(), fresh_net_l=lay.fresh_net_l()),
    ))

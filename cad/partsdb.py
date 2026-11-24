"""Parts database: typed models for everything under data/, a loader, the expression evaluator
for named parameters, and the expansion of assembly items into placed instances.

Nothing in here imports build123d, so `make data` validates the YAML without the CAD kernel.
"""
from __future__ import annotations

import ast
import datetime as dt
import math
import operator
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BIKE_GEOMETRY = ROOT / "research" / "05-bike-geometry.yaml"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ------------------------------------------------------------------ parts
class Mass(Strict):
    basis: Literal["declared", "per_length", "per_area"]
    unit_kg: float | None = Field(default=None, ge=0)
    total_kg: float | None = Field(default=None, ge=0)
    kg_per_m: float | None = Field(default=None, gt=0)
    kg_per_m2: float | None = Field(default=None, gt=0)
    maturity: Literal["spec", "calculated", "estimate"]
    source: str
    note: str | None = None

    @model_validator(mode="after")
    def _one_figure(self):
        need = {"declared": ("unit_kg", "total_kg"), "per_length": ("kg_per_m",), "per_area": ("kg_per_m2",)}[self.basis]
        if not any(getattr(self, k) is not None for k in need):
            raise ValueError(f"mass basis {self.basis} needs one of {need}")
        return self


class Geometry(Strict):
    generator: str
    params: dict[str, Any] = {}


class Cog(Strict):
    at: list[Any] | None = None
    from_items: str | None = None
    basis: str


class Part(Strict):
    id: str = ""
    group: str = ""
    name: str
    product: str | None = None
    maker: str | None = None
    part_no: str | None = None
    kind: Literal["bom", "context", "sub_part"] = "bom"
    qty: float | None = None
    unit: str | None = None
    mass: Mass | None = None
    size: str | None = None
    rating: str | None = None
    material: str | None = None    # what it is made of, shown in the 3D viewer's part card (S-01)
    use: str | None = None
    links: dict[str, str] = {}
    stockist_au: str | None = None
    notes: str | None = None
    removable: bool = False
    payload: bool = False
    included_in: str | None = None
    geometry: Geometry | None = None
    cog: Cog | None = None
    color: str = Field(default="#999999", pattern=r"^#[0-9a-fA-F]{6}$")
    alpha: float = Field(default=1.0, ge=0, le=1)
    when: str | None = None    # an expression over the module parameters: the part exists only when it is not 0 (owner options)

    @model_validator(mode="after")
    def _rules(self):
        if self.kind == "bom":
            if self.mass is None or self.qty is None:
                raise ValueError(f"BOM line {self.id or self.name} needs qty and mass")
            if self.geometry is None and self.cog is None:
                raise ValueError(f"BOM-only line {self.id or self.name} needs a cog (where its mass sits)")
        else:
            if self.mass is not None:
                raise ValueError(f"{self.kind} part {self.id or self.name} must not carry BOM mass")
        return self


class PartsFile(Strict):
    group: str
    parts: dict[str, Part]


# ------------------------------------------------------------------ assembly
class Item(Strict):
    ref: str
    part: str
    group: Literal["bikes", "restraint", "bed", "partitions", "safety", "context",
                   "body", "subframe", "doors", "security", "tools"]
    label: str
    step: str | None = None
    at: list[Any] | None = None
    rot: list[Any] | None = None
    params: dict[str, Any] = {}
    copies: list[dict[str, Any]] | None = None
    for_: dict[str, Any] | None = Field(default=None, alias="for")
    bike: dict[str, Any] | None = None
    ramp: dict[str, Any] | None = None
    display: Literal["always", "loading_only", "closed_only"] = "always"
    check_only: bool = False
    when: str | None = None    # an expression over the module parameters: the item exists only when it is not 0

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class AssemblyDef(Strict):
    id: str
    name: str
    revision: str
    params: dict[str, Any]
    items: list[Item]


# ------------------------------------------------------------------ checks, load cases, drawings, steps
class Check(Strict):
    id: str
    title: str
    type: Literal["clearance", "height", "contact", "landing", "beam", "restraint", "roof"]
    a: list[str] | None = None
    b: list[str] | None = None
    each: list[str] | None = None
    pairs: list[list[str]] | None = None
    min_gap_mm: float | None = None
    max_gap_mm: float | None = None
    add_mm: Any = None
    max_z: Any = None
    tolerance_mm: float = 0.01
    beam: dict[str, Any] | None = None
    restraint: dict[str, Any] | None = None
    roof: dict[str, Any] | None = None     # roof: the bike box's roof skin (cad/ute_garage.py roof_skin)
    span_ratio: float | None = None
    severity: Literal["fail", "report"]
    added_by_build: bool = False
    inputs: list[str] = []
    why: str


class TrailerCheck(Strict):
    """A whole-trailer check, measured on the block layout (cad/trailer.py)."""
    id: str
    title: str
    type: Literal["mass", "gcm", "fit", "tyre", "width", "overhang", "coupling", "clearance_ground", "clearance_leads", "breakover",
                  "jackknife", "jackknife_height", "wheel", "towball_scale",
                  "towball_ute", "towball_ute_input", "axle_window", "coupling_dv", "lateral", "bed", "platinum_return",
                  "chassis_stress", "chassis_local", "chassis_deflection", "chassis_twist", "chassis_fatigue",
                  "body_panel", "body_deflection", "body_insert", "body_roof", "body_twist", "body_joint",
                  "body_mount", "body_end_wall", "body_openings", "body_cradle", "body_thermal", "body_awning", "body_members", "body_plate_defl", "body_plate_strength", "bed_load",
                  "rollover", "yaw", "overturn", "tie_down"]
    load_case: str | None = None          # chassis_stress: report 11's load case (data/chassis/chassis.yaml)
    item: str | None = None               # chassis_local, chassis_deflection and chassis_fatigue: what is checked
    quantity: Literal["mass", "axle", "axle_vsb1", "towball", "towball_pct", "tyre_load", "tyre_load_side"] | None = None
    limit: Literal["kit_gtm", "nsw_gtm_cap", "nsw_atm_cap", "plated_atm", "target", "tyre_rating", "wheel_rating"] | None = None
    tolerance: float | None = None
    inputs: list[str] = []
    basis: Literal["nominal", "growth", "both"] = "nominal"
    cases: Literal["all"] | list[str] = "all"
    zone: str | None = None
    min: float | None = None
    max: float | None = None
    min_gap_mm: float | None = None
    when: str | None = None               # an expression over the trailer parameters: checked only when it is not 0
    body: dict[str, Any] | None = None    # body_* checks (cad/body.py): what is checked
    state: dict[str, Any] | None = None   # fit: trailer parameters to override for this check (the bed lowered, bed_state 1)
    severity: Literal["fail", "report"]
    why: str


class ChecksFile(Strict):
    checks: list[Check]
    trailer_checks: list[TrailerCheck] = []


class LoadCase(Strict):
    id: str
    name: str
    module: Literal["all", "fixed_only"]
    bikes: list[str]


class Towball(Strict):
    computable: bool
    note: str


class TrailerCase(Strict):
    id: str
    name: str
    aboard: str
    water_l: Any
    load: list[Literal["fuel", "gear", "grey"]]
    towball_target: bool = False


class LoadCasesFile(Strict):
    trailer_cases: list[TrailerCase] = []
    towball_target_kg: float
    axle_window: dict[str, Any] = {}     # the axle solve's design targets (decision H17, cad/trailer.py)
    registration: dict[str, Any] = {}
    tow_vehicle: dict[str, Any] = {}


class Revision(Strict):
    rev: str
    date: dt.date
    description: str
    drawn: str
    checked: str = ""
    approved: str = ""


class DrawingDef(Strict):
    number: str
    title: str
    subtitle: str
    project: str | None = None
    sheet: int
    size: Literal["A3"]
    scale: float | Literal["NTS"]   # NTS: a chart, schematic or schedule with no scaled view
    status: Literal["DRAFT", "FOR REVIEW", "FOR CONSTRUCTION", "AS BUILT", "RETIRED"]
    structural: bool = False
    retired: str | None = None      # why the sheet is no longer drawn, and what replaces it
    revisions: list[Revision]


class DrawingsFile(Strict):
    owner: str
    project: str
    drawn_by: str
    sheets_total: int
    drawings: list[DrawingDef]


class StepPart(Strict):
    part: str
    qty: str


class Step(Strict):
    id: str
    title: str
    action: str
    why: str
    new: list[str]
    hide: list[str] = []
    parts: list[StepPart] = []
    tools: list[str] = []
    consumables: list[str] = []
    drawings: list[str] = []
    checks: list[str] = []
    hold_points: list[str] = []
    attention: list[str] = []
    instructions: list[str] = []
    door: Literal["open", "closed"] = "closed"
    when: str | None = None    # an expression over the module parameters: the step exists only when it is not 0


class StepsFile(Strict):
    steps: list[Step]


# ------------------------------------------------------------------ expressions
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod}
_FUN = {"min": min, "max": max, "abs": abs, "sqrt": math.sqrt, "sin": lambda d: math.sin(math.radians(d)),
        "cos": lambda d: math.cos(math.radians(d)), "round": round}


class Params:
    """Named parameters whose values may be expressions over other parameters."""

    def __init__(self, raw: dict[str, Any]):
        self.raw = dict(raw)
        self.values: dict[str, Any] = {}
        self._busy: set[str] = set()
        for k in self.raw:
            self.get(k)

    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        if name not in self.raw:
            raise KeyError(f"unknown parameter '{name}'")
        if name in self._busy:
            raise ValueError(f"parameter cycle at '{name}'")
        self._busy.add(name)
        val = self.eval(self.raw[name], {})
        self._busy.discard(name)
        self.values[name] = val
        return val

    def eval(self, value, local: dict[str, Any]):
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, list):
            return [self.eval(v, local) for v in value]
        if isinstance(value, dict):
            return {k: self.eval(v, local) for k, v in value.items()}
        if isinstance(value, str):
            try:
                tree = ast.parse(value, mode="eval")
            except SyntaxError:
                return value  # plain text
            if isinstance(tree.body, ast.Name) and tree.body.id not in local and tree.body.id not in self.raw:
                return value  # a bare word that is not a parameter is text (e.g. "x", "road")
            return self._node(tree.body, local, value)
        return value

    def _node(self, n, local, src):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id in local:
                return local[n.id]
            return self.get(n.id)
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            return _BIN[type(n.op)](self._node(n.left, local, src), self._node(n.right, local, src))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = self._node(n.operand, local, src)
            return -v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUN:
            return _FUN[n.func.id](*[self._node(a, local, src) for a in n.args])
        if isinstance(n, ast.List):
            return [self._node(e, local, src) for e in n.elts]
        raise ValueError(f"expression not allowed: {src!r}")


# ------------------------------------------------------------------ instances
class Instance(BaseModel):
    """One placed body: an item, or one copy of an item."""
    iid: str
    ref: str
    part: str
    group: str
    label: str
    step: str | None
    at: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rot: tuple[float, float, float] = (0.0, 0.0, 0.0)
    params: dict[str, Any] = {}
    special: dict[str, Any] = {}
    display: str = "always"
    check_only: bool = False


# Assemblies other than the trailer's garage and bed module. Each names its part files, its checks file and the
# module parameters the measurement rules may set. The ute garage (UTE-GARAGE.md) shares the bikes with the trailer.
# The trailer (TRAILER.md) has no placed module of its own since the bikes moved to the ute (UTE-GARAGE.md): its
# Project carries the trailer checks, load cases, drawings and measurements only.
ASSEMBLIES = {
    "trailer": dict(parts=[], checks="checks.yaml", assembly=False),
    "ute-garage": dict(parts=["parts/bikes.yaml", "ute/parts/*.yaml"], checks="ute/garage-checks.yaml", assembly=True),
}


class Project:
    def __init__(self, root: Path = ROOT, overrides: dict[str, Any] | None = None, use_solved: bool = True,
                 assembly: str = "trailer"):
        self.root = root
        self.overrides = dict(overrides or {})
        self.assembly_name = assembly
        spec = ASSEMBLIES[assembly]
        data = root / "data"
        self.parts: dict[str, Part] = {}
        files = [f for pat in spec["parts"] for f in sorted(data.glob(pat))]
        for f in files:
            pf = PartsFile.model_validate(yaml.safe_load(f.read_text()))
            for pid, p in pf.parts.items():
                if pid in self.parts:
                    raise ValueError(f"duplicate part id {pid} in {f.name}")
                p.id, p.group = pid, pf.group
                self.parts[pid] = p
        self.assembly = (AssemblyDef.model_validate(yaml.safe_load((data / "assemblies" / f"{assembly}.yaml").read_text()))
                         if spec["assembly"] else AssemblyDef(id="ASM-TR", name="Whole trailer (no placed module)", revision="-",
                                                              params={}, items=[]))
        cf = ChecksFile.model_validate(yaml.safe_load((data / spec["checks"]).read_text()))
        self.checks = cf.checks
        self.trailer_checks = cf.trailer_checks
        self.load = LoadCasesFile.model_validate(yaml.safe_load((data / "load_cases.yaml").read_text()))
        self.drawings = DrawingsFile.model_validate(yaml.safe_load((data / "drawings.yaml").read_text()))
        self.steps: list[Step] = []
        self.bike_geometry = yaml.safe_load(BIKE_GEOMETRY.read_text())
        from .inputs import Inputs
        self.inputs = Inputs(root)
        if spec["assembly"]:
            self.inputs.patch_parts(self.parts)
        raw = dict(self.assembly.params)
        if spec["assembly"]:
            for k, v in self.inputs.module_overrides(use_solved).items():
                if k in raw:
                    raw[k] = v
        for k, v in self.overrides.items():
            if k not in raw:
                raise KeyError(f"override of unknown parameter {k}")
            raw[k] = v
        self.P = Params(raw)
        self._apply_options()
        self.instances = self._expand()
        self._validate_refs()

    def _on(self, when: str | None) -> bool:
        return when is None or bool(self.P.eval(when, {}))

    def _apply_options(self):
        """Owner options (the module parameter `lpg`, for example): parts, items and steps with a `when` expression
        that evaluates to 0 are left out, and the checks and steps forget the items they named."""
        self.disabled_refs = {it.ref for it in self.assembly.items if not self._on(it.when)}
        self.parts = {k: p for k, p in self.parts.items() if self._on(p.when)}
        self.assembly.items = [it for it in self.assembly.items if it.ref not in self.disabled_refs]
        self.steps = [s for s in self.steps if self._on(s.when)]
        drop = self.disabled_refs

        def keep(names):
            return None if names is None else [n for n in names if n not in drop]
        for c in self.checks:
            c.a, c.b, c.each = keep(c.a), keep(c.b), keep(c.each)
            if c.pairs is not None:
                c.pairs = [p for p in c.pairs if not set(p) & drop]
        for s in self.steps:
            s.new, s.hide = keep(s.new), keep(s.hide)
            s.parts = [sp for sp in s.parts if sp.part in self.parts]

    # -- expansion -------------------------------------------------------
    def _expand(self) -> list[Instance]:
        out: list[Instance] = []
        specials = ("bike", "strap", "cleat", "ledger", "ramp")
        for it in self.assembly.items:
            part = self.parts[it.part] if it.part in self.parts else None
            if part is None:
                raise ValueError(f"item {it.ref}: unknown part {it.part}")
            base_params = dict(part.geometry.params) if part.geometry else {}
            variants: list[tuple[str, dict[str, Any], dict[str, Any]]] = []  # (suffix, bindings, copy fields)
            if it.for_:
                (var, expr), = it.for_.items()
                vals = self.P.eval(expr, {})
                for i, v in enumerate(vals, 1):
                    variants.append((str(i), {var: v}, {}))
            elif it.copies:
                for c in it.copies:
                    variants.append((str(c["id"]), {}, c))
            else:
                variants.append(("", {}, {}))
            for suffix, local, copy in variants:
                iid = f"{it.ref}.{suffix}" if suffix else it.ref
                at = copy.get("at", it.at)
                params = {**base_params, **it.params, **copy.get("params", {})}
                special = {}
                for k in specials:
                    src = copy.get(k, getattr(it, k, None) if hasattr(it, k) else None)
                    if src is not None:
                        special[k] = self.P.eval(src, local)
                extra = set(copy) - {"id", "at", "params", "step", *specials}
                if extra:
                    raise ValueError(f"item {iid}: unknown copy keys {sorted(extra)}")
                out.append(Instance(
                    iid=iid, ref=it.ref, part=it.part, group=it.group, label=it.label,
                    step=copy.get("step", it.step),
                    at=tuple(self.P.eval(at, local)) if at is not None else (0.0, 0.0, 0.0),
                    rot=tuple(self.P.eval(it.rot, local)) if it.rot else (0.0, 0.0, 0.0),
                    params=self.P.eval(params, local), special=special,
                    display=it.display, check_only=it.check_only))
        seen: set[str] = set()
        for i in out:
            if i.iid in seen:
                raise ValueError(f"duplicate instance id {i.iid}")
            seen.add(i.iid)
        return out

    def _validate_refs(self):
        refs = {i.ref for i in self.instances} | {i.iid for i in self.instances}
        for c in self.checks:
            names = (c.a or []) + (c.b or []) + (c.each or []) + [n for p in (c.pairs or []) for n in p]
            for n in names:
                if n not in refs:
                    raise ValueError(f"check {c.id}: unknown item '{n}'")
        for c in list(self.checks) + list(self.trailer_checks):
            for iid in c.inputs:
                if iid not in self.inputs.items:
                    raise ValueError(f"check {c.id}: unknown measurement {iid}")
        step_ids = {s.id for s in self.steps}
        for i in self.instances:
            if i.step and i.step not in step_ids:
                raise ValueError(f"instance {i.iid}: unknown step {i.step}")
        for s in self.steps:
            for n in s.new + s.hide:
                if n not in refs:
                    raise ValueError(f"step {s.id}: unknown item '{n}'")
            for sp in s.parts:
                if sp.part not in self.parts:
                    raise ValueError(f"step {s.id}: unknown part '{sp.part}'")
        for pid, p in self.parts.items():
            if p.included_in and p.included_in not in self.parts:
                raise ValueError(f"part {pid}: included_in unknown part {p.included_in}")

    # -- helpers -----------------------------------------------------------
    def select(self, names: list[str], *, include_check_only: bool = True) -> list[Instance]:
        """Instances matching item refs ("6") or instance ids ("6.3")."""
        out = []
        for i in self.instances:
            if not include_check_only and i.check_only:
                continue
            if i.iid in names or i.ref in names:
                out.append(i)
        return out

    def bom_lines(self) -> list[Part]:
        lines = [p for p in self.parts.values() if p.kind == "bom"]
        return sorted(lines, key=lambda p: (p.group, p.id))


def schema() -> dict:
    """JSON Schema for the part files, for editor validation."""
    return PartsFile.model_json_schema()


if __name__ == "__main__":
    import json
    prj = Project(assembly="ute-garage")
    print(json.dumps(dict(parts=len(prj.parts), instances=len(prj.instances),
                          params={k: prj.P.values[k] for k in ("deck_z", "tuareg_y", "st_y", "bike_spacing")}), indent=1))

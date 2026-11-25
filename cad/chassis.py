"""Chassis and drawbar geometry (CHASSIS.md), built from data/chassis/chassis.yaml and the trailer layout.

The members sit on their centroid axes in the project datum. Each member has a section from report 11's table
(data/chassis/sections.yaml), a mass from its length and kg/m, and a galvanised area inside and out. The frame
model for cad/chassis_fea.py treats the main rail and its raiser as one composite section, because their seams
are welded continuously, and joins members that meet off-axis with rigid links.
"""
from __future__ import annotations

import copy
import functools
import math
from dataclasses import dataclass, field
from typing import Any

import yaml

from .frame import G_STEEL, RIGID, Frame, Section
from .partsdb import DATA, Params

CHASSIS_YAML = DATA / "chassis" / "chassis.yaml"

# a pin between two nodes 1 mm apart: it passes a force each way and almost no moment (the hinge cheeks' fillets to the
# hinge bar, I2-92). Marked rigid so the stress readings skip it
PIN = Section("pin", A=1.0e5, I_strong=1.0, I_weak=1.0, J=1.0, rigid=True)
SECTIONS_YAML = DATA / "chassis" / "sections.yaml"
SIDES = {-1: "K", 1: "R"}            # kerb side is negative Y, road side positive Y (DIM-01)
SIDE_WORDS = {-1: "kerb side", 1: "road side"}


# ------------------------------------------------------------------ sections
@dataclass(frozen=True)
class Props:
    """Section properties in mm. Z_strong and Z_weak are the moduli used for stress (the AS 4100 effective modulus
    where it is smaller than the elastic one), C is the torsion modulus, Aw_* the shear areas of the walls."""
    id: str
    name: str
    d: float
    b: float
    t: float
    ro: float
    kg_m: float
    A: float
    I_strong: float
    I_weak: float
    J: float
    Z_strong: float
    Z_weak: float
    C: float
    fy: float
    Aw_depth: float
    Aw_width: float
    area_m2_per_m: float
    grade: str = ""
    Ze_strong: float = 0.0       # AS 4100 5.2 effective section moduli, for the section capacity at the ultimate pull
    Ze_weak: float = 0.0

    def frame_section(self) -> Section:
        return Section(self.name, self.A, self.I_strong, self.I_weak, self.J)


# AS 4100 Table 5.2 for a cold-formed RHS or SHS: a flange in uniform compression, supported along both edges, and a web
# in bending, compressed at one edge (plasticity and yield limits)
FLANGE_LIMITS, WEB_LIMITS = (30.0, 40.0), (82.0, 115.0)


def effective_modulus(flat_c: float, flat_w: float, t: float, fy: float, Z: float, S: float) -> float:
    """AS 4100 5.2's effective section modulus Ze for bending that compresses the flat `flat_c` uniformly and bends the
    flat `flat_w` (both clear widths, mm): compact Ze = min(S, 1.5 Z), non-compact by the line between Z and that, slender
    Z times the yield limit over the slenderness (a flange), or its square (a web)."""
    k = math.sqrt(fy / 250.0)
    lf, lw = flat_c / t * k, flat_w / t * k
    (fp, fyl), (wp, wyl) = FLANGE_LIMITS, WEB_LIMITS
    zc = min(S, 1.5 * Z)
    if lf / fyl >= lw / wyl:
        ls, lsp, lsy, power = lf, fp, fyl, 1
    else:
        ls, lsp, lsy, power = lw, wp, wyl, 2
    if ls <= lsp:
        return zc
    if ls <= lsy:
        return Z + (lsy - ls) / (lsy - lsp) * (zc - Z)
    return Z * (lsy / ls) ** power


def _perimeter(d, b, r):
    return 2 * (d + b) - (8 - 2 * math.pi) * r


@functools.lru_cache(maxsize=1)
def load_data() -> dict:
    """data/chassis/chassis.yaml, read once per process (the trailer layout builds the chassis for every axle trial)."""
    return yaml.safe_load(CHASSIS_YAML.read_text())


@functools.lru_cache(maxsize=1)
def load_sections() -> dict[str, Props]:
    raw = yaml.safe_load(SECTIONS_YAML.read_text())
    out = {}
    for s in raw["sections"]:
        if s["shape"] not in ("RHS", "SHS"):
            continue
        d, b, t, ro = s["d"], s["b"], s["t"], s["ro"]
        zx, zy = s["Zx_e3mm3"] * 1e3, s["Zy_e3mm3"] * 1e3
        zey = s.get("Ze_y_e3mm3_C450")
        area = (_perimeter(d, b, ro) + _perimeter(d - 2 * t, b - 2 * t, max(ro - t, 0))) / 1000
        # the Ze values Austube's tables give for C450L0, or AS 4100 5.2 for the section's own grade where they give none
        fy_s = s["fy_mpa"]
        tab_x, tab_y = s.get("Ze_x_e3mm3_C450"), s.get("Ze_y_e3mm3_C450")
        sx, sy = s.get("Sx_e3mm3", s["Zx_e3mm3"]) * 1e3, s.get("Sy_e3mm3", s["Zy_e3mm3"]) * 1e3
        ze_x = tab_x * 1e3 if tab_x and fy_s >= 450 else effective_modulus(b - 2 * t, d - 2 * t, t, fy_s, zx, sx)
        ze_y = tab_y * 1e3 if tab_y and fy_s >= 450 else effective_modulus(d - 2 * t, b - 2 * t, t, fy_s, zy, sy)
        out[s["id"]] = Props(
            id=s["id"], name=s["designation"].replace("x", " x "), d=d, b=b, t=t, ro=ro, kg_m=s["mass_kg_per_m"],
            A=s["A_mm2"], I_strong=s["Ix_e6mm4"] * 1e6, I_weak=s["Iy_e6mm4"] * 1e6, J=s["J_e6mm4"] * 1e6,
            Z_strong=zx, Z_weak=min(zy, zey * 1e3) if zey else zy, C=s["C_e3mm3"] * 1e3, fy=s["fy_mpa"],
            Aw_depth=2 * (d - 2 * t) * t, Aw_width=2 * (b - 2 * t) * t, area_m2_per_m=area, grade=s.get("grade", ""),
            Ze_strong=ze_x, Ze_weak=ze_y)
    return out


@functools.lru_cache(maxsize=1)
def load_angles() -> dict[str, dict]:
    """The equal angles of data/chassis/sections.yaml as their rows: leg `d`, thickness `t` and `mass_kg_per_m`."""
    raw = yaml.safe_load(SECTIONS_YAML.read_text())
    return {s["id"]: s for s in raw["sections"] if s["shape"] == "equal angle"}


def cheek_props(ck: dict, gap: float, n: int = 2) -> Props:
    """The hinge cheeks at one hinge as one member's section: `n` plates `t` thick and `l` long along X, two either side of
    the hinge crossmember, `gap` wide, their centres gap / 2 + l / 2 from its centre, or one alone on its own axis
    (xt_hinges `cheek`). Plate grade 350."""
    t, l = ck["t"], ck["l"]
    e = gap / 2 + l / 2 if n == 2 else 0.0
    I_s = n * (t * l ** 3 / 12 + t * l * e ** 2)
    I_w = n * l * t ** 3 / 12
    J = n * l * t ** 3 / 3
    return Props(id="CH-P16", name=f"Hinge cheeks, {n} x PL {l:g} x {t:g}", d=2 * e + l, b=t, t=t, ro=0.0, kg_m=n * t * l * 7.85e-3,
                 A=n * t * l, I_strong=I_s, I_weak=I_w, J=J, Z_strong=I_s / (e + l / 2), Z_weak=I_w / (t / 2), C=J / t, fy=350.0,
                 Aw_depth=n * t * l / 1.5, Aw_width=n * t * l / 1.5, area_m2_per_m=0.0, grade="AS/NZS 3678 grade 350",
                 Ze_strong=I_s / (e + l / 2), Ze_weak=I_w / (t / 2))


def _tube_strips(p: Props, z0: float, n: int = 200) -> list[tuple[float, float]]:
    """A tube's wall as horizontal strips (z, area) from its underside at z0, the flat walls scaled to its tabled area."""
    dz = p.d / n
    raw = []
    for k in range(n):
        z = z0 + (k + 0.5) * dz
        w = p.b if (z - z0 < p.t or z0 + p.d - z < p.t) else 2 * p.t
        raw.append((z, w * dz))
    k = p.A / sum(a for _, a in raw)
    return [(z, a * k) for z, a in raw]


def _pair_plastic_modulus(rail: Props, raiser: Props) -> float:
    """The plastic modulus of the rail and its raiser welded on it, about the axis that halves their area (mm3)."""
    strips = _tube_strips(rail, 0.0) + _tube_strips(raiser, rail.d)
    half = sum(a for _, a in strips) / 2
    acc, zp = 0.0, 0.0
    for z, a in sorted(strips):
        if acc + a >= half:
            zp = z
            break
        acc += a
    return sum(a * abs(z - zp) for z, a in strips)


@dataclass(frozen=True)
class Composite:
    """The main rail and its raiser welded together continuously, as one section about its own centroid."""
    rail: Props
    raiser: Props
    z_bottom: float
    z_centroid: float
    z_top: float
    A: float
    I_strong: float
    I_weak: float
    J: float
    Z_bottom: float
    Z_top: float
    Z_weak: float
    C: float
    Aw: float
    Ze_strong: float = 0.0      # the pair's plastic modulus about its plastic neutral axis, both tubes compact that way
    Ze_weak: float = 0.0        # the two tubes' effective moduli about the common vertical axis, each slender that way

    @classmethod
    def of(cls, rail: Props, raiser: Props, z_bottom: float) -> "Composite":
        z1, z2 = z_bottom + rail.d / 2, z_bottom + rail.d + raiser.d / 2
        A = rail.A + raiser.A
        zc = (rail.A * z1 + raiser.A * z2) / A
        I = rail.I_strong + rail.A * (z1 - zc) ** 2 + raiser.I_strong + raiser.A * (z2 - zc) ** 2
        top = z_bottom + rail.d + raiser.d
        return cls(rail, raiser, z_bottom, zc, top, A, I, rail.I_weak + raiser.I_weak, rail.J + raiser.J,
                   I / (zc - z_bottom), I / (top - zc), rail.Z_weak + raiser.Z_weak, rail.C + raiser.C,
                   rail.Aw_depth + raiser.Aw_depth, Ze_strong=_pair_plastic_modulus(rail, raiser),
                   Ze_weak=rail.Ze_weak + raiser.Ze_weak)

    def frame_section(self) -> Section:
        return Section("Composite rail", self.A, self.I_strong, self.I_weak, self.J)

    @property
    def Z_strong(self):
        return min(self.Z_bottom, self.Z_top)


# ------------------------------------------------------------------ members and fittings
@dataclass
class Member:
    id: str
    role: str
    name: str
    sec: Props
    p0: tuple[float, float, float]
    p1: tuple[float, float, float]
    depth_dir: tuple[float, float, float] = (0.0, 0.0, 1.0)
    side: int = 0
    station: str | None = None
    note: str = ""
    in_frame: bool = True

    @property
    def length(self) -> float:
        return math.dist(self.p0, self.p1)

    @property
    def mass_kg(self) -> float:
        return self.sec.kg_m * self.length / 1000

    @property
    def cog(self):
        return tuple((a + b) / 2 for a, b in zip(self.p0, self.p1))

    @property
    def area_m2(self) -> float:
        return self.sec.area_m2_per_m * self.length / 1000

    def box(self):
        """Axis-aligned bounding box of the tube with its true outer sizes."""
        ax = [b - a for a, b in zip(self.p0, self.p1)]
        L = math.hypot(*ax)
        ex = [v / L for v in ax]
        dz = list(self.depth_dir)
        k = sum(a * b for a, b in zip(dz, ex))
        ez = [a - k * b for a, b in zip(dz, ex)]
        n = math.hypot(*ez)
        ez = [v / n for v in ez]
        ey = [ez[1] * ex[2] - ez[2] * ex[1], ez[2] * ex[0] - ez[0] * ex[2], ez[0] * ex[1] - ez[1] * ex[0]]
        h = [abs(ez[i]) * self.sec.d / 2 + abs(ey[i]) * self.sec.b / 2 for i in range(3)]
        lo = [min(self.p0[i], self.p1[i]) - h[i] for i in range(3)]
        hi = [max(self.p0[i], self.p1[i]) + h[i] for i in range(3)]
        return (*lo, *hi)


@dataclass
class Fitting:
    id: str
    name: str
    kind: str
    qty: int
    at: list[tuple[float, float, float]]
    mass_each: float
    maturity: str
    source: str
    t: float | None = None
    dims: tuple[float, float, float] | None = None
    area_m2_each: float = 0.0

    @property
    def mass_kg(self) -> float:
        return self.mass_each * self.qty


@dataclass
class Joint:
    id: str
    name: str
    members: tuple[str, ...]
    weld: str
    detail: str | None = None
    at: tuple[float, float, float] | None = None


# ------------------------------------------------------------------ the chassis
class Chassis:
    def __init__(self, values: dict[str, Any], stations: list[dict], data: dict | None = None):
        self.data = data or copy.deepcopy(load_data())
        raw = {k: v for k, v in values.items() if isinstance(v, (int, float))}
        raw.update(self.data["params"])
        self.P = Params(raw)
        self.V = self.P.values
        self.sections = load_sections()
        self.stations = [dict(s, x=float(round(s["x"]))) for s in stations]   # each position rounded once, here (F3-09)
        roles = self.data["roles"]
        self.role_sec = {r: self.sections[d["section"]] for r, d in roles.items()}
        self.role_name = {r: d["name"] for r, d in roles.items()}
        V = self.V
        self.comp = Composite.of(self.role_sec["rail"], self.role_sec["raiser"], V["rail_underside_z"])
        self.fy = self.role_sec["rail"].fy
        self.members: list[Member] = []
        self.joints: list[Joint] = []
        self._build_members()
        self.suspension = self._suspension()
        self.fittings = self._build_fittings()

    # -- helpers ------------------------------------------------------
    def ev(self, v):
        return self.P.eval(v, {})

    def role_of(self, st: dict) -> str:
        return self.data["station_roles"]["generated" if st.get("generated") else st["id"]]

    def station_x(self, st: dict) -> float:
        """Centre X of a crossmember station (stations give the front face)."""
        return st["x"] + self.V["xm_w"] / 2

    def db_y(self, x: float) -> float:
        """Centreline Y magnitude of a drawbar member at X (the A-frame part, then along the rail)."""
        V = self.V
        if x >= V["body_x0"]:
            return V["rail_c"]
        return V["db_apex_y"] + (V["rail_c"] - V["db_apex_y"]) * (x - V["db_apex_x"]) / (V["body_x0"] - V["db_apex_x"])

    # -- members ------------------------------------------------------
    def _build_members(self):
        V, rs = self.V, self.role_sec
        x0, x1 = V["body_x0"], V["body_x1"]
        zr = V["rail_underside_z"] + rs["rail"].d / 2
        zs = V["rail_top_z"] + rs["raiser"].d / 2
        add = self.members.append
        for s in (-1, 1):
            y = s * V["rail_c"]
            add(Member(f"RL-{SIDES[s]}", "rail", f"{self.role_name['rail']}, {SIDE_WORDS[s]}", rs["rail"], (x0, y, zr), (x1, y, zr),
                       side=s))
            add(Member(f"RS-{SIDES[s]}", "raiser", f"{self.role_name['raiser']}, {SIDE_WORDS[s]}", rs["raiser"], (x0, y, zs), (x1, y, zs),
                       side=s, in_frame=False, note="Acts with the rail as one composite section in the frame model"))
        y_in = V["rail_c"] - rs["rail"].b / 2
        for k, st in enumerate(self.stations, 1):
            role = self.role_of(st)
            own = self.data.get("station_sections", {}).get(st["id"])   # a station that needs more than its role's section
            sec = self.sections[own] if own else rs[role]
            xc = self.station_x(st)
            z = V["rail_underside_z"] + sec.d / 2 if role in ("cm_xt", "cm_end") else V["raiser_top_z"] - sec.d / 2
            name = f"Crossmember, {st['id']}" if not st.get("generated") else f"Crossmember at X {st['x']:,.0f}"
            add(Member(f"CM-{k:02d}", role, name, sec, (xc, -y_in, z), (xc, y_in, z), depth_dir=(0, 0, 1), station=st["id"],
                       note=self.role_name[role]))
            osec = rs["outrigger"]
            zo = V["raiser_top_z"] - osec.d / 2
            for s in (-1, 1):
                add(Member(f"OR-{k:02d}{SIDES[s]}", "outrigger", f"Outrigger at X {st['x']:,.0f}, {SIDE_WORDS[s]}", osec,
                           (xc, s * V["outrigger_root_y"], zo), (xc, s * V["outrigger_tip_y"], zo), station=st["id"], side=s))
        dsec = rs["drawbar"]
        for s in (-1, 1):
            add(Member(f"DB-{SIDES[s]}A", "drawbar", f"Drawbar member, {SIDE_WORDS[s]}, apex to the body front", dsec,
                       (V["db_apex_x"], s * V["db_apex_y"], V["db_z"]), (x0, s * V["rail_c"], V["db_z"]), side=s))
            add(Member(f"DB-{SIDES[s]}B", "drawbar", f"Drawbar member, {SIDE_WORDS[s]}, under the rail to X {V['db_end_x']:.0f}", dsec,
                       (x0, s * V["rail_c"], V["db_z"]), (V["db_end_x"], s * V["rail_c"], V["db_z"]), side=s,
                       note="Stitch fillets to the rail underside across a 2.5 mm gap, sniped taper end, no transverse weld"))
        yb = self.db_y(V["brace_x"]) - dsec.b / 2
        add(Member("DB-BR", "brace", self.role_name["brace"], rs["brace"], (V["brace_x"], -yb, V["db_z"]), (V["brace_x"], yb, V["db_z"]),
                   note="Welded at the drawbar members' mid-depth"))
        for k, pb in enumerate(self.data.get("plan_braces", []), 1):
            ids = {st["id"]: st for st in self.stations}
            if not all(i in ids for i in pb["between"]):
                continue  # a body length compared in TRAILER.md with fewer stations
            sa, sb = (ids[i] for i in pb["between"])
            xa, xb = sa["x"] + V["xm_w"], sb["x"] - pb.get("rear_ahead", 0.0)
            z = V["rail_underside_z"] + rs["rail"].d / 2
            sec = self.sections[pb["section"]]
            ends = "ends on 6 mm gusset plates welded to the crossmember and the rail web"
            if pb.get("rear_ahead"):
                ends = (f"its front end on a 6 mm gusset plate welded to the crossmember and the rail web, its rear end on one "
                        f"welded to the rail web {pb['rear_ahead']:g} mm ahead of the {pb['between'][1]} crossmember")
            for s in (-1, 1):
                add(Member(f"PB-{k}{SIDES[s]}", "plan_brace", f"Plan brace between the {pb['between'][0]} and {pb['between'][1]} crossmembers, "
                           f"from the {SIDE_WORDS[s]} rail", sec, (xa, s * y_in, z), (xb, -s * y_in, z), depth_dir=(0, 0, 1),
                           note=f"Diagonal at rail height, {ends}"))
        psec = rs["spare_post"]
        xp = x0 - psec.b / 2
        for s in (-1, 1):
            add(Member(f"SP-P{SIDES[s]}", "spare_post", f"{self.role_name['spare_post']}, {SIDE_WORDS[s]}", psec,
                       (xp, s * V["spare_post_y"], V["rail_underside_z"]), (xp, s * V["spare_post_y"], V["spare_post_top_z"]),
                       depth_dir=(1, 0, 0), side=s, in_frame=False, note="Bolted to cleats on the body front crossmember, tied to the wall at the top"))
        self._joints()

    def _joints(self):
        J = self.joints.append
        for m in self.members:
            if m.role in ("cm_xt", "cm_end", "cm_floor"):
                leg = self.data["member_galvanising_holes"]["cm_xt"]["leg"] if m.role == "cm_xt" else 5
                J(Joint(f"J-{m.id}", f"{m.name} to both rails", (m.id, "RL-K", "RL-R"),
                        f"{leg} mm fillet all round each end, SP. No weld across the rail's width beyond the crossmember's own end", "FAT-01, FAT-02, FAT-03"))
            if m.role == "outrigger":
                J(Joint(f"J-{m.id}", f"{m.name} to the raiser's outer face", (m.id, f"RS-{m.id[-1]}"),
                        "5 mm fillet all round, SP", "FAT-04, FAT-05"))
        for s in "KR":
            J(Joint(f"J-RS-{s}", f"Raiser to main rail, {SIDE_WORDS[-1 if s == 'K' else 1]}", (f"RS-{s}", f"RL-{s}"),
                    "Continuous 4 mm fillets along both edges, SP, vented at each end of each bay", "FAT-06"))
            J(Joint(f"J-DB-{s}", f"Drawbar member under the rail, {SIDE_WORDS[-1 if s == 'K' else 1]}", (f"DB-{s}B", f"RL-{s}"),
                    "The lap 2.5 mm open, 8 mm stitch fillets 50 long at 100 along both edges, profiled root gusset at the body front, sniped taper end, toe ground",
                    "FAT-07, FAT-08"))
            J(Joint(f"J-DB-{s}A", f"Drawbar member, A-frame part to its overlap part, {SIDE_WORDS[-1 if s == 'K' else 1]}",
                    (f"DB-{s}A", f"DB-{s}B"), "Mitred full penetration butt weld at the body front, ground flush, SP", "FAT-07"))
        J(Joint("J-BR", "Cross brace to both drawbar members", ("DB-BR", "DB-KA", "DB-RA"), "5 mm fillet all round at mid-depth, SP", "FAT-09"))
        J(Joint("J-APEX", "Drawbar members to the coupling plate", ("DB-KA", "DB-RA", "CH-P01"), "6 mm fillets all round, SP, plate faces cleaned after galvanising"))

    # -- fittings -----------------------------------------------------
    def _build_fittings(self) -> list[Fitting]:
        out = []
        dens = self.data["material"]["density"]
        for f in self.data["fittings"]:
            qty = int(f.get("qty", 1))
            base = self.ev(f["at"]) if "at" in f else [0.0, 0.0, 0.0]
            at = []
            if f.get("poses") == "steadies":       # each folded steady's mass at the middle of its box in travel (est.)
                at = [tuple((p["travel"][i] + p["travel"][i + 3]) / 2 for i in range(3)) for p in self.steady_poses()]
            elif f.get("poses") == "hinge_gussets":   # each gusset's mass at its centre (xt_hinges, I2-88)
                at = [g["centre"] for g in self.hinge_gussets()]
            elif f.get("poses") == "hinge_cheeks":    # each cheek's mass at its centre (xt_hinges)
                at = [c["centre"] for c in self.hinge_cheeks()]
            elif "side_y" in f:
                sy = self.ev(f["side_y"])
                xs = [base[0]] if "rear_x" not in f else [base[0], self.ev(f["rear_x"])]
                for x in xs:
                    for s in (-1, 1):
                        at.append((x, s * sy, base[2]))
            else:
                at = [tuple(base)]
            kind = f["kind"]
            if kind == "plate" and f.get("poses") == "hinge_cheeks":   # each cheek at its own size (xt_hinges `cheek`, I2-99)
                cs = self.hinge_cheeks()
                area = [c["area"] for c in cs]
                kinds = sorted({(round(c["l"], 1), round(c["h"], 1), len(c["boxes"])) for c in cs})
                m = sum(area) * f["t"] * dens / 1e9 / len(cs)
                out.append(Fitting(f["id"], f["name"], kind, len(cs), at, m, "calculated",
                                   "Calculated: " + " and ".join(f"{sum(1 for c in cs if (round(c['l'], 1), round(c['h'], 1), len(c['boxes'])) == k_)} x {k_[0]:g} x {k_[1]:g}"
                                                                 + (" with its step" if k_[2] > 1 else "") for k_ in kinds)
                                   + f" x {f['t']} mm plate at {dens} kg/m3", t=f["t"], dims=(f["l"], f["w"], f["t"]),
                                   area_m2_each=2 * sum(area) / 1e6 / len(cs)))
            elif kind == "plate":
                af = f.get("area_factor", 1.0)
                m = f["l"] * f["w"] * f["t"] * af * dens / 1e9
                out.append(Fitting(f["id"], f["name"], kind, qty, at, m, "calculated",
                                   f"Calculated: {f['l']} x {f['w']} x {f['t']} mm plate" + (f", {af:.0%} of the rectangle" if af != 1 else "")
                                   + f" at {dens} kg/m3", t=f["t"], dims=(f["l"], f["w"], f["t"]),
                                   area_m2_each=2 * f["l"] * f["w"] * af / 1e6))
            elif kind == "tube":
                sec = self.sections[f["section"]]
                L = self.ev(f["length"])
                if f.get("poses") == "hinge_gussets":         # each gusset's own axis, shorter where it lands on a cheek (I2-99)
                    gs = self.hinge_gussets()
                    L = sum(g_["length"] for g_ in gs) / len(gs)
                m = sec.kg_m * L / 1000
                out.append(Fitting(f["id"], f["name"], kind, qty, at, m, "calculated",
                                   f"Calculated: {round(L, 1):g} mm of {sec.name} at {sec.kg_m} kg/m", t=sec.t,
                                   area_m2_each=sec.area_m2_per_m * L / 1000))
            elif kind == "angles":                  # the shear panel's pieces, each at its own centre (panel_pieces)
                ps = self.panel_pieces()
                ctr = [tuple((p["boxes"][0][i] + p["boxes"][0][i + 3]) / 2 for i in range(3)) for p in ps]
                parts = ", ".join(f"{p['length']:.0f} mm of {load_angles()[p['section']]['designation'].replace('x', ' x ')}" for p in ps)
                out.append(Fitting(f["id"], f["name"], kind, 1, ctr, sum(p["mass_kg"] for p in ps), "calculated",
                                   f"Calculated: {parts}, at each section's kg/m", t=5.0, area_m2_each=sum(p["area_m2"] for p in ps)))
            elif kind == "strip":
                L = self.strip_length()
                out.append(Fitting(f["id"], f["name"], kind, 1, [(self.V["body_x0"] + self.V["body_length"] / 2, 0.0, self.V["floor_underside_z"] - 10)],
                                   f["kg_per_m"] * L / 1000, f["maturity"], f"{f['source']}, {L / 1000:.1f} m"))
            else:
                if len(at) < qty:
                    at = (at * qty)[:qty]
                out.append(Fitting(f["id"], f["name"], kind, qty, at, f["mass_kg"], f["maturity"], f["source"]))
        return out

    def strip_length(self) -> float:
        """Floor bearer strip on every member top that carries the floor: raisers, outriggers and floor crossmembers."""
        L = sum(m.length for m in self.members if m.role in ("raiser", "outrigger", "cm_floor"))
        return L

    # -- the corner steadies ------------------------------------------
    def steady_poses(self) -> list[dict]:
        """The four corner steadies (data `steadies`), each with its pair, side and bracket centre (x, y) under the rail,
        the jacking station at 90 degrees, and its boxes (x0, y0, z0, x1, y1, z1): ARK's bracket, the steady folded flat
        for travel, its leg and foot at 90 degrees wound down to the ground, and the box the leg sweeps between the two.
        `twist` is the sign of its load in LC5b's twist couple."""
        if getattr(self, "_steadies", None) is not None:
            return self._steadies
        sd, top = self.data["steadies"], self.V["rail_underside_z"]
        bl, bw, bh = sd["bracket"]
        length, width, depth = sd["folded"]
        head = top - bh - 60                                  # the head's underside, where the leg hangs from at 90 degrees
        foot = depth - 30                                     # the foot plate, its long side along the fold
        out = []
        for pr, pair, sx in zip(sd["pairs"], ("front", "rear"), (1, -1)):
            x, ym = self.ev(pr["x"]), self.ev(pr["y"])
            for s in (-1, 1):
                y = s * ym
                if pr["fold"] == "inboard":
                    outer = y + s * bl / 2
                    lo, hi = sorted((outer, outer - s * length))
                    bracket = (x - bw / 2, y - bl / 2, top - bh, x + bw / 2, y + bl / 2, top)
                    travel = (x - width / 2, lo, top - depth, x + width / 2, hi, top)
                    use = (x - width / 2, y - foot / 2, 0.0, x + width / 2, y + foot / 2, head)
                else:
                    d = -1 if pr["fold"] == "forward" else 1
                    lo, hi = sorted((x - d * bl / 2, x - d * bl / 2 + d * length))
                    bracket = (x - bl / 2, y - bw / 2, top - bh, x + bl / 2, y + bw / 2, top)
                    travel = (lo, y - width / 2, top - depth, hi, y + width / 2, top)
                    use = (x - foot / 2, y - width / 2, 0.0, x + foot / 2, y + width / 2, head)
                sweep = tuple(min(a, b) for a, b in zip(travel[:3], use[:3])) + tuple(max(a, b) for a, b in zip(travel[3:], use[3:]))
                out.append(dict(pair=pair, side=s, x=x, y=y, fold=pr["fold"], bracket=bracket, travel=travel, use=use, sweep=sweep,
                                twist=sx * -s, weld_l=bw if pr["fold"] == "inboard" else bl))
        self._steadies = out
        return out

    # -- the XT hinges and their gussets (I2-88) ---------------------------
    def hinge_crossmembers(self) -> list[Member]:
        """The two XT hinge crossmembers, the front hinge's and the centre's, in that order."""
        return [next(m for m in self.members if m.station == st and m.role == "cm_xt") for st in ("XT front hinge", "XT centre")]

    def hinge_gussets(self) -> list[dict]:
        """The six hinge gussets CH-P08 (xt_hinges `gusset`), the one place the dip, the frame model, the 3D model and the
        sheets read them from: each an SHS on the 45 degree line in plan across the corner between its hinge crossmember's
        face and the rail's inner face, at the rail's mid-depth, both ends cut on those faces. Its axis meets each face
        `leg` = length / sqrt 2 from the corner, `p0` at `cm_y` on the crossmember's face and `p1` at `rail_x` on the rail's,
        the centres of its two end welds. Each side wall ends `b` / 2 inside the axis's ends on the short side, the web
        `short` across the tube, and as far beyond them on the long side (`offsets`, as the dip reads a mitre), and
        `outline` is its plan at the two faces: short and long side on the crossmember, long and short side on the rail."""
        V, g = self.V, self.data["xt_hinges"]["gusset"]
        ck = self.data["xt_hinges"]["cheek"]
        rail = self.role_sec["rail"]
        sec = self.sections[next(f for f in self.data["fittings"] if f["id"] == "CH-P08")["section"]]
        y_in = V["rail_c"] - rail.b / 2
        z = V["rail_underside_z"] + g.get("z_over_underside", rail.d / 2)
        length = self.ev(g["length"])
        leg = length / math.sqrt(2)
        side = sec.b / 2 * math.sqrt(2)                # each side wall's offset from the axis along either face
        cheeks = {c["gusset"] for c in self.hinge_cheeks() if c["gusset"]}
        out = []
        for cm in self.hinge_crossmembers():
            for e in g.get("faces", [1]):              # 1 behind the crossmember's rear face, -1 ahead of its front face
                face = cm.p0[0] + e * cm.sec.b / 2
                for s in (-1, 1):
                    gid = f"{cm.id}{SIDES[s]}" + ("" if e > 0 else "F")
                    if gid in g.get("omit", []):
                        continue
                    tc = ck["t"] if f"CH-P08-{gid}" in cheeks else 0.0   # it lands on its cheek's inboard face (I2-99)
                    lg = leg - tc
                    y_face = y_in - tc
                    p0 = (face, s * (y_in - leg), z)
                    p1 = (face + e * lg, s * y_face, z)
                    short = 1 if e * s > 0 else -1     # the web on the corner's side, across the tube's width (cad/chassis_dip.py axes)
                    out.append(dict(id=f"CH-P08-{gid}", cm=cm.id, side=s, face=e, rear_x=face, length=lg * math.sqrt(2), leg=lg,
                                    centre=tuple((a + b) / 2 for a, b in zip(p0, p1)), dir=(e / math.sqrt(2), s / math.sqrt(2), 0.0),
                                    p0=p0, p1=p1, cm_y=p0[1], rail_x=p1[0], y_in=s * y_face, z=z, short=short, on_cheek=bool(tc),
                                    offsets={short: sec.b / 2, -short: -sec.b / 2},
                                    outline=[(face, s * (y_in - leg + side)), (face, s * (y_in - leg - side)),
                                             (face + e * (lg + side), s * y_face), (face + e * (lg - side), s * y_face)]))
        return out

    def shear_panels(self) -> list[dict]:
        """The steel shear panels under the tanks (shear_panels): each spans its bay from the rear face of one station's
        crossmember to the front face of the next, between the rails' inner faces, as the frame model carries it. `sheet`
        is the sheet as cut (panel_sheet) and `bolts` its bolts, each with its group (panel_pieces)."""
        V, out = self.V, []
        st = {m.station: m for m in self.members if m.role.startswith("cm")}
        for d in self.data.get("shear_panels", []):
            m0, m1 = st[d["from"]], st[d["to"]]
            x0, x1 = m0.p0[0] + m0.sec.b / 2, m1.p0[0] - m1.sec.b / 2
            pieces = self.panel_pieces()
            out.append(dict(id=d["id"], x0=x0, x1=x1, b=2 * (V["rail_c"] - self.role_sec["rail"].b / 2), t=d["t"], fixing=d.get("fixing"),
                            sheet=self.panel_sheet(d, x1, pieces), bolts=[b for p in pieces for b in p["bolts"]]))
        return out

    def panel_mass(self, pid: str) -> dict:
        """Shear panel pid's sheet as cut and drilled (panel_sheet): its area in plan with its tongues and the fillets
        their radiused roots add, less its bolt holes, its steel at the frame's density, its zinc on both faces at
        AS/NZS 4680's rate for its thickness, and the two together, for the line that carries it (UF-03)."""
        d = next(p for p in self.data["shear_panels"] if p["id"] == pid)
        pn = next(p for p in self.shear_panels() if p["id"] == pid)
        sh, r = pn["sheet"], pn["sheet"]["root_r"]
        x0, y0, x1, y1 = sh["rect"]
        tongues = sum(abs((b[2] - b[0]) * (b[3] - b[1])) for b in sh["tongues"])
        fillets = 2 * len(sh["tongues"]) * r * r * (1 - math.pi / 4)
        holes = len(pn["bolts"]) * math.pi * d["fixing"]["hole"] ** 2 / 4
        area = abs((x1 - x0) * (y1 - y0)) + tongues + fillets - holes
        steel = area * d["t"] * self.data["material"]["density"] / 1e9
        zinc = 2 * area / 1e6 * self.galv_rate(d["t"])
        return dict(id=pid, area_m2=area / 1e6, steel_kg=steel, zinc_kg=zinc, kg=steel + zinc, t=d["t"], material=d["material"],
                    density=self.data["material"]["density"], zinc_kg_m2=self.galv_rate(d["t"]), holes=len(pn["bolts"]))

    def panel_sheet(self, d: dict, x_rear: float, pieces: list[dict]) -> dict:
        """The panel's sheet in plan: its front edge at the jacking pads' rear edges, its rear edge at the next crossmember's
        face, its sides `edge` inside the rails' inner faces, and a tongue under each crossmember's angle, as wide as the
        angle and `tongue` short of its flat leg's toe, its two corners at its root radiused `tongue_r` (`root_r`). Each
        as (x0, y0, x1, y1). `roots` gives each tongue's root line, its X on the sheet's edge, and which way the tongue
        runs from it (-1 forward, 1 rearward)."""
        V = self.V
        pad = next(f for f in self.data["fittings"] if f["id"] == "CH-P06")
        half = V["rail_c"] - self.role_sec["rail"].b / 2 - d["edge"]
        front = self.ev(pad["at"])[0] + pad["l"] / 2
        tongues, roots = [], []
        for p in (p for p in pieces if p["use"] == "crossmember"):
            toe = p["toe_x"] + p["face"] * d.get("tongue", 0.0)
            root = front if p["face"] > 0 else x_rear
            xa, xb = sorted((toe, root))
            tongues.append((xa, p["y0"], xb, p["y1"]))
            roots.append(dict(x=root, way=-p["face"], y0=p["y0"], y1=p["y1"], piece=p["id"]))
        return dict(rect=(front, -half, x_rear, half), tongues=tongues, roots=roots, root_r=d.get("tongue_r", 0.0), front=front, half=half)

    def panel_pieces(self) -> list[dict]:
        """The shear panel's pieces CH-P17: each angle with its use (rail or crossmember), its section, its ends,
        its legs' boxes, its mass, its galvanised area, its welds as lines (what, from, to) and its bolts (x, y, group).
        The rails' angles run from `gap` behind the XT centre's rear hinge cheeks' ends to `end` ahead of the XT rear
        shock crossmember, and each crossmember's angles under their Y ranges, their bolts on the flat leg's `gauge`."""
        V, spec = self.V, next(f for f in self.data["fittings"] if f["id"] == "CH-P17")
        ang, rail = load_angles(), self.role_sec["rail"]
        fix = self.data["shear_panels"][0]["fixing"]
        y_in = V["rail_c"] - rail.b / 2
        z_flat = V["rail_underside_z"] - spec["drop"]
        st = {m.station: m for m in self.members if m.role.startswith("cm")}
        centre, shock = st["XT centre"], st["XT rear shock"]
        out = []

        def spaced(a0: float, a1: float, pitch: float, end: float) -> list[float]:
            n = int(math.floor((a1 - a0 - 2 * end) / pitch + 1e-9)) + 1
            first = a0 + (a1 - a0 - (n - 1) * pitch) / 2
            return [first + k * pitch for k in range(n)]

        r = spec["rails"]
        a = ang[r["section"]]
        x0 = max(c["box"][3] for c in self.hinge_cheeks() if c["box"][0] >= centre.p0[0]) + r["gap"]
        x1 = shock.p0[0] - shock.sec.b / 2 - r["end"]
        for s in (-1, 1):
            y_web = s * y_in
            up = (x0, min(y_web, y_web - s * a["t"]), z_flat, x1, max(y_web, y_web - s * a["t"]), z_flat + a["d"])
            flat = (x0, min(y_web, y_web - s * a["d"]), z_flat, x1, max(y_web, y_web - s * a["d"]), z_flat + a["t"])
            yb = y_web - s * spec["gauge"]
            out.append(dict(id=f"CH-P17-R{SIDES[s]}", use="rail", side=s, section=r["section"], x0=x0, x1=x1, length=x1 - x0,
                            boxes=[up, flat], galvanised=True,
                            welds=[("top edge", (x0, y_web, z_flat + a["d"]), (x1, y_web, z_flat + a["d"])),
                                   ("rail's bottom corner", (x0, y_web, V["rail_underside_z"]), (x1, y_web, V["rail_underside_z"]))],
                            bolts=[dict(x=x, y=yb, group="rail", along="x") for x in spaced(x0, x1, fix["pitch"], fix["end"])]))
        for c in spec["crossmembers"]:
            a, m = ang[c["section"]], st[c["station"]]
            f = c["face"]                       # 1 on the crossmember's rear face, -1 on its front face, the flat leg under it
            x_web = m.p0[0] + f * m.sec.b / 2
            heel = x_web + f * a["t"]
            toe = heel - f * a["d"]
            front = c["station"] == "XT centre"
            for k, (y0, y1) in enumerate(c["ys"], 1):
                up = (min(x_web, heel), y0, z_flat, max(x_web, heel), y1, z_flat + a["d"])
                flat = (min(toe, heel), y0, z_flat, max(toe, heel), y1, z_flat + a["t"])
                n = 4 if front else None
                ys = [(y0 + y1) / 2 + (j - (n - 1) / 2) * fix["front_pitch"] for j in range(n)] if front else spaced(y0, y1, fix["pitch"], fix["end"])
                out.append(dict(id=f"CH-P17-{m.id}-{k}", use="crossmember", member=m.id, station=c["station"], face=f, section=c["section"],
                                y0=y0, y1=y1, length=y1 - y0, x_web=x_web, heel_x=heel, toe_x=toe, boxes=[up, flat], galvanised=True,
                                welds=[("top edge", (x_web, y0, z_flat + a["d"]), (x_web, y1, z_flat + a["d"])),
                                       ("crossmember's bottom corner", (x_web, y0, V["rail_underside_z"]), (x_web, y1, V["rail_underside_z"]))],
                                bolts=[dict(x=heel - f * spec["gauge"], y=y, group="front" if front else "rear", along="y") for y in ys]))
        for p in out:
            a = ang[p["section"]]
            p["mass_kg"] = a["mass_kg_per_m"] * p["length"] / 1000
            p["area_m2"] = (4 * a["d"] - 2 * a["t"]) * p["length"] / 1e6 if p["galvanised"] else 0.0
        return out

    @property
    def xm_w(self) -> float:
        return self.V["xm_w"]



    def hinge_cheeks(self) -> list[dict]:
        """The eight hinge cheeks CH-P16 (xt_hinges `cheek`), two at each XT hinge, one either side of its crossmember:
        a plate on the rail's inner face from `below` under the rail's underside up the rail's web, welded to the web
        along its top edge and the rail's bottom corner and to the hinge bar's front or rear face (I2-88)."""
        V, ck = self.V, self.data["xt_hinges"]["cheek"]
        g = self.data["xt_hinges"]["gusset"]
        big = ck.get("under_gusset")
        y_in = V["rail_c"] - self.role_sec["rail"].b / 2
        z0 = V["rail_underside_z"] - ck["below"]
        out = []
        for w in self.suspension:
            cm = next(m for m in self.hinge_crossmembers() if abs(m.p0[0] - w["station_x"]) < 1.0)
            for e, tag in ((-1, "F"), (1, "B")):
                gid = f"{cm.id}{SIDES[w['side']]}" + ("" if e > 0 else "F")
                gusset = big is not None and e in g.get("faces", [1]) and gid not in g.get("omit", [])
                face = w["station_x"] + e * V["xm_w"] / 2
                x0 = face if e > 0 else face - ck["l"]
                y0 = w["side"] * y_in - (ck["t"] if w["side"] > 0 else 0.0)
                box = (x0, y0, z0, x0 + ck["l"], y0 + ck["t"], z0 + ck["h"])
                boxes, area = [box], ck["l"] * ck["h"]
                if gusset:                              # the step where the gusset lands, centred on its footprint (I2-99)
                    xc = face + e * (self.ev(g["length"]) / math.sqrt(2) - ck["t"])
                    za, zb = V["rail_underside_z"] + big["z0"], V["rail_underside_z"] + big["z1"]
                    ls = big["l"][cm.station] if isinstance(big["l"], dict) else big["l"]
                    step = (xc - ls / 2, y0, za, xc + ls / 2, y0 + ck["t"], zb)
                    boxes.append(step)
                    over = max(0.0, min(box[3], step[3]) - max(box[0], step[0])) * max(0.0, min(box[5], step[5]) - max(box[2], step[2]))
                    area += ls * (zb - za) - over
                ends = [b_[0] for b_ in boxes] + [b_[3] for b_ in boxes]
                l = (max(ends) - face) if e > 0 else (face - min(ends))
                h = max(b_[5] for b_ in boxes) - z0
                if f"{w['id']}{tag}" in ck.get("omit", []):
                    continue
                out.append(dict(id=f"CH-P16-{w['id']}{tag}", member=f"CH-P16-{w['id']}", wheel=w["id"], side=w["side"], box=box,
                                centre=tuple((box[i] + box[i + 3]) / 2 for i in range(3)), l=l, h=h, boxes=boxes, area=area, face=face, way=e,
                                gusset=f"CH-P08-{gid}" if gusset else None))
        return out

    def hinge_weld_ys(self, cm: Member) -> list[float]:
        """The Y of each run of a hinge bar's welds to its crossmember (xt_hinges `bar`), both sides, centres measured from
        the rail's inner face."""
        if cm not in self.hinge_crossmembers():
            return []
        y_in = self.V["rail_c"] - self.role_sec["rail"].b / 2
        return [s * (y_in - u) for s in (-1, 1) for u in self.data["xt_hinges"]["bar"]["runs"]]

    # -- galvanising --------------------------------------------------
    def galv_rate(self, t: float) -> float:
        """Coating mass in kg/m2 for steel of thickness t (AS/NZS 4680 minimum average)."""
        return next(r["g_per_m2"] for r in self.data["galvanising"] if t <= r["t_max"]) / 1000

    def galvanising(self) -> dict:
        rate = self.galv_rate
        rows = {}
        for m in self.members:
            r = rows.setdefault(m.sec.t, dict(t=m.sec.t, area_m2=0.0, kg_per_m2=rate(m.sec.t)))
            r["area_m2"] += m.area_m2
        for f in self.fittings:
            if f.kind in ("plate", "tube", "angles"):
                r = rows.setdefault(f.t, dict(t=f.t, area_m2=0.0, kg_per_m2=rate(f.t)))
                r["area_m2"] += f.area_m2_each * f.qty
        for r in rows.values():
            r["mass_kg"] = r["area_m2"] * r["kg_per_m2"]
        tot_a = sum(r["area_m2"] for r in rows.values())
        tot_m = sum(r["mass_kg"] for r in rows.values())
        return dict(rows=sorted(rows.values(), key=lambda r: r["t"]), area_m2=tot_a, mass_kg=tot_m)

    def steel_mass(self) -> float:
        return sum(m.mass_kg for m in self.members) + sum(f.mass_kg for f in self.fittings if f.kind in ("plate", "tube", "angles"))

    # -- suspension geometry (report 11 section 5.1) -------------------
    def _suspension(self) -> list[dict]:
        V = self.V
        stations = {st["id"]: st for st in self.stations}
        out = []
        for axle, st_id in (("front", "XT front hinge"), ("rear", "XT centre")):
            st = stations[st_id]
            rear_face = st["x"] + V["xm_w"]
            px = rear_face - V["pivot_ahead"]
            pz = V["rail_underside_z"] - V["pivot_below"]
            dx = math.sqrt(V["arm_r"] ** 2 - V["arm_drop"] ** 2)
            for s in (-1, 1):
                out.append(dict(id=f"{axle[0].upper()}{SIDES[s]}", axle=axle, side=s, station=st_id, pivot=(px, s * V["rail_c"], pz),
                                hub=(px + dx, s * V["hub_y"], pz - V["arm_drop"]), contact=(px + dx, s * V["hub_y"], 0.0),
                                airbag=(px + dx, s * (V["rail_c"] - self.role_sec["rail"].b / 2), V["rail_underside_z"]),
                                station_x=self.station_x(st)))
        return out

    def hub_x(self, axle: str) -> float:
        return next(w["hub"][0] for w in self.suspension if w["axle"] == axle)

    def xt_arm_turn(self, w: dict, s: float) -> float:
        """How far wheel w's arm turns about its pivot, in radians, from ride to travel s (mm, up positive)."""
        V = self.V
        dz = V["arm_drop"] - s
        return math.atan2(-dz, math.sqrt(V["arm_r"] ** 2 - dz ** 2)) - math.atan2(-V["arm_drop"], math.sqrt(V["arm_r"] ** 2 - V["arm_drop"] ** 2))

    def shock_line(self, w: dict, s: float = 0.0) -> tuple:
        """Wheel w's shock absorber at travel s, from its lower eye on the arm, which turns with the arm about the pivot,
        to its top eye in the inboard clevis of its bracket on the next crossmember's support plate (xt_arms `droop` and
        `parts`, 33XT AIR sheets 2 to 4, est.): ((x, y, z) lower, (x, y, z) upper)."""
        V, d, sh = self.V, self.data["xt_arms"]["droop"], self.data["xt_arms"]["parts"]["shock"]
        cm = next(m for m in self.members if m.station == d["to"][w["axle"]] and m.role.startswith("cm"))
        plate = self.shock_plate_t(cm)
        y = w["side"] * self.ev(d["y"])
        (px, _, pz), (hx, _, hz) = w["pivot"], w["hub"]
        a = self.xt_arm_turn(w, s)
        ex, ez = hx + sh["eye"][0] - px, hz + sh["eye"][1] - pz
        lower = (px + ex * math.cos(a) - ez * math.sin(a), y, pz + ex * math.sin(a) + ez * math.cos(a))
        upper = (cm.p0[0] - cm.sec.b / 2 - plate - sh["e"], y, V["rail_underside_z"] + d["z_over_underside"])
        return lower, upper

    def shock_plate_t(self, cm) -> float:
        """The thickness of the shock support plate CH-P07 on crossmember cm's front face, 0 where the data puts none."""
        f = next(f for f in self.fittings if f.id == "CH-P07")
        face = cm.p0[0] - cm.sec.b / 2
        return f.t if any(abs(p[0] + f.t / 2 - face) < f.t for p in f.at) else 0.0

    def xt_parts(self, steps: int = 12, slab: float = 20.0) -> list[dict]:
        """The XT kit's parts between the rails at their places in 33XT AIR sheets 2 to 4 (xt_arms `parts`, est.), the one
        place the layout's fit checks (FIT-03), the services' clearance (SVC-01), the tanks' notches and the 3D model read
        them from. Each is a dict with its `id`, `what`, wheel and `boxes`: one box for a part fixed to the frame, and for the
        shock, which turns with the arm, its swept envelope over the arm's whole travel as boxes in `slab` mm bands of
        height, each holding every point of the shock's body in that band. Each hinge's bar runs under its crossmember for
        both wheels of its axle."""
        V, pr = self.V, self.data["xt_arms"]["parts"]
        rail = self.role_sec["rail"]
        y_in, y_out, zu = V["rail_c"] - rail.b / 2, V["rail_c"] + rail.b / 2, V["rail_underside_z"]
        out = []
        for w in self.suspension:
            s, wid = w["side"], w["id"]
            ys = lambda a, b: (min(s * (y_in - a), s * (y_in - b)), max(s * (y_in - a), s * (y_in - b)))  # noqa: E731
            cm = next(m for m in self.members if m.station == w["station"] and m.role == "cm_xt")
            xf, xr = cm.p0[0] - cm.sec.b / 2, cm.p0[0] + cm.sec.b / 2
            ya, yb = sorted((s * y_out, s * (y_in - pr["bar"]["inboard"])))
            out.append(dict(id=f"XT-BAR-{wid}", what="Cruisemaster's hinge bar under the crossmember", wheel=wid,
                            boxes=[(xf, ya, zu - pr["bar"]["d"], xr, yb, zu)]))
            px = w["pivot"][0]
            hy = ys(*pr["hinge"]["y_in"])
            pl = pr["plates"]
            plates = [(px - pl["l"] / 2, min(ys(u - pl["t"] / 2, u + pl["t"] / 2)), zu - pl["below"],
                       px + pl["l"] / 2, max(ys(u - pl["t"] / 2, u + pl["t"] / 2)), zu - pr["bar"]["d"]) for u in pl["y_in"]]
            out.append(dict(id=f"XT-HINGE-{wid}", what="the arm's hinge plates, bushes and pivot tube", wheel=wid, plates=plates,
                            tube=((px, s * (y_in - pl["y_in"][0]), w["pivot"][2]), (px, s * (y_in - pl["y_in"][-1]), w["pivot"][2])),
                            leg=((px, s * (y_in - pl["y_in"][0]), w["pivot"][2]), (px, s * (y_out + 24.0), w["pivot"][2])),
                            boxes=[(px - pl["l"] / 2, hy[0], zu - pl["below"], px + pl["l"] / 2, hy[1], zu - pr["bar"]["d"])]))
            ab, bb = pr["airbag"], pr["bag_bracket"]
            bx, by = w["hub"][0] + ab["dx"], s * (y_in - ab["y_in"])
            travel, shift = V["travel"], 12.0                    # the hub's 11.6 mm swing along X over the travel (report 11)
            out.append(dict(id=f"XT-BAG-{wid}", what="the airbag over its travel", wheel=wid, centre=(bx, by), d=ab["d"], z=(zu - ab["h"], zu),
                            boxes=[(bx - ab["d"] / 2 - shift, by - ab["d"] / 2, zu - ab["h"] - travel, bx + ab["d"] / 2 + shift, by + ab["d"] / 2, zu)]))
            yb0 = ys(0.0, bb["reach"])
            out.append(dict(id=f"XT-BAGBKT-{wid}", what="the airbag's top bracket 33SA 013 on the rail's inner face", wheel=wid,
                            boxes=[(bx - bb["l"] / 2, yb0[0], zu, bx + bb["l"] / 2, yb0[1], zu + rail.d)]))
            sb, sh = pr["shock_bracket"], pr["shock"]
            lower, upper = self.shock_line(w)
            face = upper[0] + sh["e"]                     # the support plate's face, or the crossmember's where the data has none
            yk = ys(sb["y_in"], sb["y_in"] + sb["w"])
            out.append(dict(id=f"XT-SHKBKT-{wid}", what="the shock's bracket on its support plate", wheel=wid,
                            boxes=[(face - sb["out"], yk[0], zu + sb["z"], face, yk[1], zu + sb["h"])]))
            r = sh["d"] / 2
            pts = []
            for k in range(steps + 1):
                lo, up = self.shock_line(w, -travel + 2 * travel * k / steps)
                n = max(2, int(math.dist(lo, up) / 5.0))
                pts += [tuple(lo[i] + (up[i] - lo[i]) * j / n for i in range(3)) for j in range(n + 1)]
            z0, z1 = min(p[2] for p in pts) - r, max(p[2] for p in pts) + r
            bands = []
            za = z0
            while za < z1 - 1e-9:
                zb = min(za + slab, z1)
                xs = [p[0] for p in pts if p[2] - r < zb and p[2] + r > za]
                if xs:
                    bands.append((min(xs) - r, upper[1] - r, za, max(xs) + r, upper[1] + r, zb))
                za = zb
            out.append(dict(id=f"XT-SHOCK-{wid}", what="the shock absorber over the arm's travel", wheel=wid, line=(lower, upper), d=sh["d"],
                            boxes=bands))
        return out

    # -- weld toes on the rails and raisers, for the hole checks (CHS-10) ----------
    def weld_toes(self) -> list[tuple[str, tuple]]:
        """Each weld on a rail or raiser as (what, box): the band its fillet covers on the member's face, its toe at the
        band's edge. An end weld round a crossmember or an outrigger is four bands round its footprint, so a hole inside
        the footprint is measured to the nearest band."""
        V, rail, raiser = self.V, self.role_sec["rail"], self.role_sec["raiser"]
        z0, zs, z1 = V["rail_underside_z"], V["rail_top_z"], V["raiser_top_z"]
        out = []

        def ring(what, x0, x1, y, za, zb, leg, toward):
            """An all-round fillet on the face at y, the weld standing off it toward +Y or -Y."""
            ya, yb = sorted((y, y + toward * leg))
            out.extend([(what, (x0 - leg, ya, za - leg, x0, yb, zb + leg)), (what, (x1, ya, za - leg, x1 + leg, yb, zb + leg)),
                        (what, (x0, ya, za - leg, x1, yb, za)), (what, (x0, ya, zb, x1, yb, zb + leg))])

        for s in (-1, 1):
            y_in, y_out = s * (V["rail_c"] - rail.b / 2), s * (V["rail_c"] + rail.b / 2)
            for y, side in ((y_in, "inner"), (y_out, "outer")):
                lo, hi = sorted((y, y + (s if side == "outer" else -s) * 4))
                out.append((f"rail to raiser seam, {side} fillet", (V["body_x0"], lo, zs - 4, V["body_x1"], hi, zs + 4)))
                lo, hi = sorted((y, y + (s if side == "outer" else -s) * 5))
                out.append((f"drawbar overlap's {side} fillet under the rail", (V["body_x0"], lo, z0 - 5, V["db_end_x"], hi, z0 + 5)))
            for m in self.members:
                if m.role in ("cm_xt", "cm_end", "cm_floor"):
                    _, _, za, _, _, zb = m.box()
                    leg = self.data["member_galvanising_holes"]["cm_xt"]["leg"] if m.role == "cm_xt" else 5
                    ring(f"{m.id}'s end weld", m.p0[0] - m.sec.b / 2, m.p0[0] + m.sec.b / 2, y_in, za, zb, leg, -s)      # inboard
                elif m.role == "outrigger" and m.side == s:
                    _, _, za, _, _, zb = m.box()
                    ring(f"{m.id}'s root weld", m.p0[0] - m.sec.b / 2, m.p0[0] + m.sec.b / 2, s * V["outrigger_root_y"], za, zb, 6, s)   # outboard
            for st in self.stations:                                  # the body mount nut plates inside the raiser
                xc = self.station_x(st)
                out.append(("body mount nut plate's welds inside the raiser", (xc - 40, s * V["rail_c"] - raiser.b / 2, z1 - 23,
                                                                               xc + 40, s * V["rail_c"] + raiser.b / 2, z1 - 3)))
            for x in (self.hub_x("front"), self.hub_x("rear")):        # the XT airbag top brackets along the rail's top edge
                lo, hi = sorted((y_in, y_in - s * 6))
                out.append(("airbag top bracket's weld", (x - 80, lo, zs - 6, x + 80, hi, zs + 6)))
            lo, hi = sorted((y_in, y_in - s * 6))
            out.append(("rear recovery tongue's welds", (V["body_x1"] - 200, lo, z0 + 15, V["body_x1"], hi, z0 + 135)))
            lo, hi = sorted((s * (V["rail_c"] - rail.b / 2 - 5), s * (V["rail_c"] + rail.b / 2 + 5)))
            out.append(("rail's end plate's fillets", (V["body_x0"], lo, z0, V["body_x0"] + 5, hi, zs + 5)))   # webs and top flange
        for p in self.steady_poses():                                  # ARK's brackets, welded along the rail's bottom corners
            bx, yc = p["bracket"], p["side"] * V["rail_c"]
            out.append(("corner steady bracket's welds", (bx[0], max(bx[1], yc - rail.b / 2), z0 - 5, bx[3], min(bx[4], yc + rail.b / 2), z0 + 5)))
        return out

    # -- named positions for the checks -------------------------------
    def positions(self) -> dict[str, Any]:
        V = self.V
        jack = next(st for st in self.stations if st["id"] == "XT centre")
        return dict(crossmember_stations=[self.station_x(st) for st in self.stations], body_x0=V["body_x0"], db_end_x=V["db_end_x"],
                    chain_lug_x=V["chain_lug_x"], jack_x=self.station_x(jack), hub_front_x=self.hub_x("front"), hub_rear_x=self.hub_x("rear"),
                    rear_tongue_x=V["body_x1"] - 70, front_recovery_x=V["front_recovery_x"], root_gusset_toe_x=V["root_gusset_toe_x"],
                    steady_x=sorted({p["x"] for p in self.steady_poses()}),
                    cheek_ends_x=sorted({x for c in self.hinge_cheeks() if c["l"] <= 300.0 for b in c["boxes"] for x in (b[0], b[3])}),
                    long_cheek_ends_x=sorted({x for c in self.hinge_cheeks() if c["l"] > 300.0 for b in c["boxes"] for x in (b[0], b[3])}),
                    panel_angle_ends_x=sorted({x for p in self.panel_pieces() if p["use"] == "rail" for x in (p["x0"], p["x1"])}))

    # -- the frame model ----------------------------------------------
    def frame(self, body: list[tuple[float, float, float]] | None = None, hinges: str = "crossmember") -> "FrameModel":
        """The frame model. `body` adds the body as a torsion box (cad/body.py): (x0, x1, GJ in N mm2) per bay between
        stations, tied rigidly to both rails at each station, as the floor's bolts tie it (BODY.md). `hinges` "crossmember"
        ties each XT pivot to its crossmember at the hinge bar's welds, with the gussets as members (CHS-12)."""
        return FrameModel(self, body, hinges)


class FrameModel:
    """Nodes and elements of the chassis and drawbar, with the lookups the load mapping needs."""

    def __init__(self, ch: Chassis, body: list[tuple[float, float, float]] | None = None, hinges: str = "crossmember"):
        self.ch = ch
        self.hinges = hinges
        V = ch.V
        f = self.f = Frame()
        self.sec_props: dict[str, Any] = {}      # member id -> Props or Composite, for stress recovery
        self.member_of_el: list[str] = []
        comp = ch.comp
        zc = comp.z_centroid
        self.zc = zc
        # rail node positions: every station, hub, pivot station, the overlap end, fittings and a mesh limit
        xs = {V["body_x0"], V["body_x1"], V["db_end_x"], V["front_recovery_x"], V["steady_front_x"], V["steady_rear_x"]}
        xs |= {ch.station_x(st) for st in ch.stations}
        xs |= {w["hub"][0] for w in ch.suspension}
        if hinges == "crossmember":
            xs |= {g["rail_x"] for g in ch.hinge_gussets()}             # where each hinge gusset meets the rail
        # where a plan brace's end meets a rail away from every crossmember (plan_braces `rear_ahead`)
        xs |= {p[0] for m in ch.members if m.role == "plan_brace" for p in (m.p0, m.p1)
               if min(abs(p[0] - ch.station_x(st)) for st in ch.stations) > V["xm_w"]}
        xs = sorted(xs)
        xs = [x for k, x in enumerate(xs) if k == 0 or x - xs[k - 1] > 5.0]   # points within 5 mm share a node
        mesh = [xs[0]]
        for a, b in zip(xs, xs[1:]):
            n = max(1, math.ceil((b - a) / V["max_element"]))
            mesh += [a + (b - a) * k / n for k in range(1, n + 1)]
        self.rail_x = mesh
        self.rail_nodes = {}
        csec = comp.frame_section()
        for s in (-1, 1):
            pts = [(x, s * V["rail_c"], zc) for x in mesh]
            idx = f.chain(pts, csec, (0, 0, 1), f"RL-{SIDES[s]}")
            self.rail_nodes[s] = idx
            self.sec_props[f"RL-{SIDES[s]}"] = comp
        # crossmembers and outriggers
        self.out_nodes: dict[tuple[str, int], list[tuple[float, int]]] = {}
        self.cm_nodes: dict[str, list[tuple[float, int]]] = {}
        self.station_nodes: dict[str, float] = {}
        for m in ch.members:
            if m.role in ("cm_xt", "cm_end", "cm_floor"):
                x, z = m.p0[0], m.p0[2]
                ys = sorted({-V["rail_c"], V["rail_c"], 0.0, -V["spare_post_y"], V["spare_post_y"],
                             *[V["rail_c"] * k / 3 for k in (-2, -1, 1, 2)],
                             *(ch.hinge_weld_ys(m) + [g["cm_y"] for g in ch.hinge_gussets() if g["cm"] == m.id] if hinges == "crossmember" else [])})
                ys = [y for k, y in enumerate(ys) if k == 0 or y - ys[k - 1] > 5.0 or abs(y) == V["rail_c"]]
                idx = f.chain([(x, y, z) for y in ys], m.sec.frame_section(), (0, 0, 1), m.id)
                self.cm_nodes[m.id] = list(zip(ys, idx))
                self.sec_props[m.id] = m.sec
                for s, nd in ((-1, idx[0]), (1, idx[-1])):
                    self._link(nd, self.rail_node(s, x), f"link {m.id}")
                self.station_nodes[m.station] = x
            elif m.role == "outrigger":
                x, z, s = m.p0[0], m.p0[2], m.side
                ys = [s * (V["outrigger_root_y"] + (V["outrigger_tip_y"] - V["outrigger_root_y"]) * k / 3) for k in range(4)]
                idx = f.chain([(x, y, z) for y in ys], m.sec.frame_section(), (0, 0, 1), m.id)
                self.out_nodes[(m.station, s)] = list(zip([abs(y) for y in ys], idx))
                self.sec_props[m.id] = m.sec
                self._link(idx[0], self.rail_node(s, x), f"link {m.id}")
        # drawbar
        dsec = ch.role_sec["drawbar"]
        self.db_nodes = {}
        for s in (-1, 1):
            xa = [V["db_apex_x"], V["chain_lug_x"], V["jockey_x"], V["brace_x"], V["root_gusset_toe_x"]]
            n = math.ceil((V["body_x0"] - V["db_apex_x"]) / V["max_element"])
            xa = sorted(set(xa) | {V["db_apex_x"] + (V["body_x0"] - V["db_apex_x"]) * k / n for k in range(n + 1)})
            xa = [x for k, x in enumerate(xa) if k == 0 or x - xa[k - 1] > 5.0]
            pts = [(x, s * ch.db_y(x), V["db_z"]) for x in xa]
            ia = f.chain(pts, dsec.frame_section(), (0, 0, 1), f"DB-{SIDES[s]}A")
            xb = [x for x in mesh if V["body_x0"] <= x <= V["db_end_x"] + 1e-6]
            ib = f.chain([(x, s * V["rail_c"], V["db_z"]) for x in xb], dsec.frame_section(), (0, 0, 1), f"DB-{SIDES[s]}B")
            for x, nd in zip(xb, ib):
                self._link(nd, self.rail_node(s, x), f"weld DB-{SIDES[s]}B")
            self.db_nodes[s] = list(zip(xa, ia)) + list(zip(xb, ib))[1:]
            self.sec_props[f"DB-{SIDES[s]}A"] = dsec
            self.sec_props[f"DB-{SIDES[s]}B"] = dsec
        braces = [m for m in ch.members if m.role == "plan_brace"]
        for m in braces:
            pa, pb = m.p0, m.p1
            mid = tuple((a + b) / 2 for a, b in zip(pa, pb))
            idx = f.chain([pa, mid, pb], m.sec.frame_section(), (0, 0, 1), m.id)
            self.sec_props[m.id] = m.sec
            for nd, p in ((idx[0], pa), (idx[-1], pb)):
                s = 1 if p[1] > 0 else -1
                self._link(nd, self.rail_node(s, p[0]), f"link {m.id}")
        bsec = ch.role_sec["brace"]
        f.add(self.db_node(-1, V["brace_x"]), self.db_node(1, V["brace_x"]), bsec.frame_section(), (0, 0, 1), "DB-BR")
        self.sec_props["DB-BR"] = bsec
        self.ball = f.node((0.0, 0.0, V["coupling_z"]), "ball")
        for s in (-1, 1):
            self._link(self.ball, self.db_node(s, V["db_apex_x"]), "coupling")
        # suspension pivots. On the main model each is tied rigidly to the rail at its hinge crossmember. With `hinges`
        # "crossmember" each is tied to its crossmember at the hinge bar's weld runs, inboard of the rail (xt_hinges
        # `bar`), as Cruisemaster's sheets build it, and the gussets CH-P08 are members, so the hinge's force and moment
        # reach the rail through the crossmember's end, beside its holes (the hinge path study, CHS-12, I2-88)
        self.pivot_nodes = {}
        self.cheek_pins: dict[str, int] = {}        # each hinge's pin at its cheeks' fillets to the hinge bar, by element
        for w in ch.suspension:
            nd = f.node(w["pivot"])
            if hinges == "crossmember":
                cm = next(m for m in ch.members if m.station == w["station"] and m.role == "cm_xt")
                for y in ch.hinge_weld_ys(cm):
                    if y * w["side"] > 0:
                        self._link(nd, self.cm_node(cm.id, y), f"hinge {w['id']}")
            else:
                self._link(nd, self.rail_node(w["side"], w["station_x"]), f"hinge {w['id']}")
            self.pivot_nodes[w["id"]] = nd
            if hinges == "crossmember":
                # the hinge's cheeks (CH-P16) as they are welded (I2-92): the hinge bar rigid from the pivot up to the middle of
                # the cheeks' fillets to it, `bar_d` under the rail, a pin there, since those short fillets pass a force but no
                # moment, and the cheeks as one member from the pin to the rail's underside, held there by their welds along
                # the rail's inner web. So the arm's moment stays in the bar and goes to the crossmember by its weld runs
                ck = ch.data["xt_hinges"]["cheek"]
                n = sum(1 for c in ch.hinge_cheeks() if c["wheel"] == w["id"])
                sp = cheek_props(ck, ch.xm_w, n)
                z_pin = V["rail_underside_z"] - ck["bar_d"] / 2
                bar = f.node((w["pivot"][0], w["pivot"][1], z_pin - 1.0))
                pin = f.node((w["pivot"][0], w["pivot"][1], z_pin))
                top = f.node((w["pivot"][0], w["pivot"][1], V["rail_underside_z"]))
                self._link(nd, bar, f"hinge bar {w['id']}")
                f.add(bar, pin, PIN, (1, 0, 0), f"cheek pin {w['id']}")
                self.cheek_pins[w["id"]] = len(f.elements) - 1
                self._link(top, self.rail_node(w["side"], w["station_x"]), f"cheek welds {w['id']}")
                f.add(pin, top, sp.frame_section(), (1, 0, 0), f"CH-P16-{w['id']}")
                self.sec_props[f"CH-P16-{w['id']}"] = sp
        for g in (ch.hinge_gussets() if hinges == "crossmember" else []):
            gsec = ch.sections[next(fd for fd in ch.data["fittings"] if fd["id"] == "CH-P08")["section"]]
            a = f.node((g["rear_x"], g["cm_y"], g["z"]))
            b = f.node((g["rail_x"], g["y_in"], g["z"]))
            self._link(a, self.cm_node(g["cm"], g["cm_y"]), f"gusset {g['id']}")
            self._link(b, self.rail_node(g["side"], g["rail_x"]), f"gusset {g['id']}")
            f.add(a, b, gsec.frame_section(), (0, 0, 1), g["id"])
            self.sec_props[g["id"]] = gsec
        # shear panels: each bay's plate as two diagonals of the same shear stiffness, A = G t L^3 / (2 E a b), between the
        # rails' nodes at the bay's corners (shear_panels, I2-87)
        self.panels = []
        for sp in ch.shear_panels():
            a, b, t = sp["x1"] - sp["x0"], sp["b"], sp["t"]
            L = math.hypot(a, 2 * V["rail_c"])
            A = G_STEEL * t * L ** 3 / (2 * 200_000.0 * a * b)
            dsec = Section(f"shear panel {sp['id']} diagonal", A=A, I_strong=1.0, I_weak=1.0, J=1.0)
            els = []
            for k, (s0, s1) in enumerate(((-1, 1), (1, -1))):
                n0, n1 = self.rail_node(s0, sp["x0"]), self.rail_node(s1, sp["x1"])
                f.add(n0, n1, dsec, (0, 0, 1), f"{sp['id']}-D{k + 1}")
                els.append(len(f.elements) - 1)
            self.panels.append(dict(sp, elements=els, A=A, L=L, a=a))
        # the body as a torsion box: a chain on the centreline at the floor's mid-plane with torsion stiffness only
        # At each station the body's section is rigid in its plane (a centre node and a node over each raiser) and
        # stands on the raisers through a mount post that carries force along Z only, as the floor bolts do.
        self.body_elements: list[tuple[int, float, float]] = []    # (element index, x0, x1)
        self.body_nodes: dict[float, int] = {}
        self.mount_posts: list[tuple[int, float, int, str]] = []   # (element index, x, side, raiser or outrigger tip)
        if body:
            zb = V["floor_underside_z"] + 15.0
            post = Section("body mount post", A=1.0e5, I_strong=1.0e4, I_weak=1.0e4, J=1.0e4)
            for x0, x1, gj in body:
                for x in (x0, x1):
                    if x not in self.body_nodes:
                        nd = f.node((x, 0.0, zb))
                        self.body_nodes[x] = nd
                        sid = next((k for k, v in self.station_nodes.items() if abs(v - x) < 1.0), None)
                        for s in (-1, 1):
                            side = f.node((x, s * V["rail_c"], zb))
                            self._link(nd, side, "body section")
                            f.add(self.rail_node(s, x), side, post, (1, 0, 0), "BODY-MOUNT")
                            self.mount_posts.append((len(f.elements) - 1, x, s, "raiser"))
                            if (sid, s) in self.out_nodes:
                                tip_y, tip = self.out_nodes[(sid, s)][-1]
                                tb = f.node((x, s * tip_y, zb))
                                self._link(nd, tb, "body section")
                                f.add(tip, tb, post, (1, 0, 0), "BODY-MOUNT")
                                self.mount_posts.append((len(f.elements) - 1, x, s, "outrigger tip"))
                sec = Section("body torsion box", A=1.0, I_strong=1.0, I_weak=1.0, J=gj / G_STEEL)
                f.add(self.body_nodes[x0], self.body_nodes[x1], sec, (0, 0, 1), "BODY")
                self.body_elements.append((len(f.elements) - 1, x0, x1))
        self.member_of_el = [el.member for el in f.elements]

    def panels_by_id(self) -> dict:
        return {p["id"]: p for p in self.panels}

    def _link(self, a: int, b: int, name: str):
        xyz = [self.f.nodes[a], self.f.nodes[b]]
        d = [q - p for p, q in zip(*xyz)]
        ref = (0, 0, 1) if abs(d[2]) < 0.9 * math.hypot(*d) else (1, 0, 0)
        self.f.add(a, b, RIGID, ref, name)

    def rail_node(self, s: int, x: float) -> int:
        k = min(range(len(self.rail_x)), key=lambda i: abs(self.rail_x[i] - x))
        return self.rail_nodes[s][k]

    def cm_node(self, member_id: str, y: float) -> int:
        return min(self.cm_nodes[member_id], key=lambda p: abs(p[0] - y))[1]

    def db_node(self, s: int, x: float) -> int:
        return min(self.db_nodes[s], key=lambda p: abs(p[0] - x))[1] if s in self.db_nodes else \
            self.f.node((x, s * self.ch.db_y(x), self.ch.V["db_z"]))

    # -- fractions for the load mapping -------------------------------
    def rail_fractions(self, s: int, x: float) -> list[tuple[int, float]]:
        xs = self.rail_x
        x = min(max(x, xs[0]), xs[-1])
        for k in range(len(xs) - 1):
            if xs[k] <= x <= xs[k + 1]:
                t = (x - xs[k]) / (xs[k + 1] - xs[k])
                return [(self.rail_nodes[s][k], 1 - t), (self.rail_nodes[s][k + 1], t)]
        return [(self.rail_nodes[s][-1], 1.0)]

    def between_rails(self, x: float, y: float) -> list[tuple[int, float]]:
        c = self.ch.V["rail_c"]
        t = (min(max(y, -c), c) + c) / (2 * c)
        return [(n, w * (1 - t)) for n, w in self.rail_fractions(-1, x)] + [(n, w * t) for n, w in self.rail_fractions(1, x)]

    def outrigger_fractions(self, x: float, y: float) -> list[tuple[int, float]]:
        s = 1 if y > 0 else -1
        st = sorted((xc, sid) for sid, xc in self.station_nodes.items() if (sid, s) in self.out_nodes)
        out = []
        if x <= st[0][0]:
            pairs = [(st[0][1], 1.0)]
        elif x >= st[-1][0]:
            pairs = [(st[-1][1], 1.0)]
        else:
            k = next(i for i in range(len(st) - 1) if st[i][0] <= x <= st[i + 1][0])
            t = (x - st[k][0]) / (st[k + 1][0] - st[k][0])
            pairs = [(st[k][1], 1 - t), (st[k + 1][1], t)]
        ay = abs(y)
        for sid, w in pairs:
            nodes = self.out_nodes[(sid, s)]
            ay_c = min(max(ay, nodes[0][0]), nodes[-1][0])
            for (y0, n0), (y1, n1) in zip(nodes, nodes[1:]):
                if y0 <= ay_c <= y1:
                    t = (ay_c - y0) / (y1 - y0)
                    out += [(n0, w * (1 - t)), (n1, w * t)]
                    break
        return out

    def floor_fractions(self, x: float, y: float) -> list[tuple[int, float]]:
        """The floor spans across the trailer onto the raisers (one-way), and the outriggers carry it outside them."""
        if abs(y) <= self.ch.V["rail_c"]:
            return self.between_rails(x, y)
        return self.outrigger_fractions(x, y)

    def crossmember_fractions(self, member_id: str, y: float) -> list[tuple[int, float]]:
        nodes = self.cm_nodes[member_id]
        for (y0, n0), (y1, n1) in zip(nodes, nodes[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / (y1 - y0)
                return [(n0, 1 - t), (n1, t)]
        return [(nodes[-1][1], 1.0)]

    def drawbar_fractions(self, x: float, y: float) -> list[tuple[int, float]]:
        """Items on the drawbar: shared between the two members by lever rule at X, or on one member if far out."""
        out = []
        yy = self.ch.db_y(x)
        t = (min(max(y, -yy), yy) + yy) / (2 * yy)
        for s, w in ((-1, 1 - t), (1, t)):
            if w > 0:
                nodes = self.db_nodes[s]
                xs = [p[0] for p in nodes]
                xq = min(max(x, xs[0]), xs[-1])
                for (x0, n0), (x1, n1) in zip(nodes, nodes[1:]):
                    if x0 <= xq <= x1:
                        u = (xq - x0) / (x1 - x0) if x1 > x0 else 0.0
                        out += [(n0, w * (1 - u)), (n1, w * u)]
                        break
        return out


# ------------------------------------------------------------------ tyre swept arc (FIT-05)
def tyre_clearance(ch: Chassis, boxes: list[tuple[str, tuple]], tyre_w: float, steps: int = 25) -> dict:
    """Least distance from each tyre, swung about its arm pivot through +/- travel, to each box. The tyre is a
    cylinder of the published diameter in its own vertical plane. A box that overlaps the tyre's width gives the
    in-plane distance, one beside it gives the combined distance."""
    V = ch.V
    R = V["tyre_d"] / 2
    best = dict(gap_mm=math.inf)
    for w in ch.suspension:
        px, py, pz = w["pivot"]
        yc = w["hub"][1]
        for k in range(steps + 1):
            s = -V["travel"] + 2 * V["travel"] * k / steps
            dz = V["arm_drop"] - s
            hx, hz = px + math.sqrt(V["arm_r"] ** 2 - dz ** 2), pz - dz
            for name, b in boxes:
                dx = max(b[0] - hx, 0.0, hx - b[3])
                dzz = max(b[2] - hz, 0.0, hz - b[5])
                d_plane = math.hypot(dx, dzz) - R
                dy = max(b[1] - (yc + tyre_w / 2), 0.0, (yc - tyre_w / 2) - b[4])
                if dy <= 0:
                    g = d_plane
                elif d_plane <= 0:
                    g = dy
                else:
                    g = math.hypot(d_plane, dy)
                if g < best["gap_mm"]:
                    best = dict(gap_mm=g, tyre=w["id"], travel_mm=s, member=name, hub=(hx, hz))
    return best


def _pt_rect(p, r) -> float:
    """Least distance in a plane from the point p (u, v) to the rectangle r (u0, v0, u1, v1), 0 inside it."""
    return math.hypot(max(r[0] - p[0], 0.0, p[0] - r[2]), max(r[1] - p[1], 0.0, p[1] - r[3]))


def _seg_pt(a, b, p) -> float:
    """Least distance in a plane from the segment a-b to the point p."""
    ux, uv = b[0] - a[0], b[1] - a[1]
    n = ux * ux + uv * uv
    k = 0.0 if n == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ux + (p[1] - a[1]) * uv) / n))
    return math.hypot(a[0] + k * ux - p[0], a[1] + k * uv - p[1])


def _seg_meets_rect(a, b, r) -> bool:
    """Whether the segment a-b crosses or lies in the rectangle r, by clipping it to the rectangle's two slabs."""
    t0, t1 = 0.0, 1.0
    for k, lo, hi in ((0, r[0], r[2]), (1, r[1], r[3])):
        d = b[k] - a[k]
        if abs(d) < 1e-12:
            if not lo <= a[k] <= hi:
                return False
            continue
        u0, u1 = sorted(((lo - a[k]) / d, (hi - a[k]) / d))
        t0, t1 = max(t0, u0), min(t1, u1)
        if t0 > t1:
            return False
    return True


def _seg_rect(a, b, r) -> float:
    """Least distance in a plane from the segment a-b to the rectangle r, 0 where they meet."""
    if _seg_meets_rect(a, b, r):
        return 0.0
    corners = ((r[0], r[1]), (r[0], r[3]), (r[2], r[1]), (r[2], r[3]))
    return min(_pt_rect(a, r), _pt_rect(b, r), *(_seg_pt(a, b, c) for c in corners))


def _beside(d_plane: float, dy: float) -> float:
    """The gap between two shapes that are each a plane figure stretched across the trailer: the gap in their plane where
    their spans across overlap, the gap across where their figures overlap, else the two combined."""
    if dy <= 0:
        return d_plane
    if d_plane <= 0:
        return dy
    return math.hypot(d_plane, dy)


def _span_gap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(b0 - a1, a0 - b1, 0.0)


def swept_parts(ch: Chassis, tyre_w: float, s: float) -> list[dict]:
    """Each wheel's tyre and trailing arm at travel s (mm, up positive) about the arm's pivot (report 11 section 5.1).
    The tyre is a cylinder of the published diameter in its own plane. The arm is a bar `arm_depth` deep from the pivot
    to the hub, across the slot from the rail's outer face to the tyre's inner face, where the XT's hanger, bush and
    arm lie (cad/model/products/outside.py)."""
    V = ch.V
    rail_out = V["rail_c"] + ch.role_sec["rail"].b / 2
    out = []
    for w in ch.suspension:
        px, _, pz = w["pivot"]
        dz = V["arm_drop"] - s
        hub = (px + math.sqrt(V["arm_r"] ** 2 - dz ** 2), pz - dz)
        yc, side = w["hub"][1], w["side"]
        arm_y = sorted((side * rail_out, side * (abs(yc) - tyre_w / 2)))
        out.append(dict(wheel=w["id"], part="tyre", hub=hub, r=V["tyre_d"] / 2, y=(yc - tyre_w / 2, yc + tyre_w / 2)))
        out.append(dict(wheel=w["id"], part="arm", hub=hub, pivot=(px, pz), r=V["arm_depth"] / 2, y=tuple(arm_y)))
    return out


def _part_bbox(p: dict) -> tuple:
    (hx, hz), r = p["hub"], p["r"]
    if p["part"] == "tyre":
        return (hx - r, p["y"][0], hz - r, hx + r, p["y"][1], hz + r)
    (px, pz) = p["pivot"]
    return (min(px, hx) - r, p["y"][0], min(pz, hz) - r, max(px, hx) + r, p["y"][1], max(pz, hz) + r)


def wheel_sweep(ch: Chassis, tyre_w: float, boxes: list[tuple[str, tuple]], points: list[tuple[str, tuple, float]],
                steps: int = 25, reach: float = 150.0) -> dict:
    """FIT-05: the least gap from each tyre and each trailing arm, swung through +/- travel, to the rigid boxes
    (name, box) and to the points along the runs (name, (x, y, z), radius). Only what lies within `reach` of a wheel's
    swept tyre and arm is measured. Returns the least gap overall, the least for the tyres and for the arms, and each
    part found within `reach` with its least gap, closest first."""
    V = ch.V
    travels = [-V["travel"] + 2 * V["travel"] * k / steps for k in range(steps + 1)]
    sweeps = {}
    for s in travels:
        for p in swept_parts(ch, tyre_w, s):
            bb = _part_bbox(p)
            key = (p["wheel"], p["part"])
            old = sweeps.get(key)
            sweeps[key] = bb if old is None else tuple(min(a, b) for a, b in zip(old[:3], bb[:3])) + tuple(max(a, b) for a, b in zip(old[3:], bb[3:]))
    near_of = {}
    for key, bb in sweeps.items():
        lo, hi = [v - reach for v in bb[:3]], [v + reach for v in bb[3:]]
        near_of[key] = ([(n, b) for n, b in boxes if all(b[i] <= hi[i] and b[i + 3] >= lo[i] for i in range(3))],
                        [(n, q, r) for n, q, r in points if all(lo[i] - r <= q[i] <= hi[i] + r for i in range(3))])
    best: dict[str, dict] = {}
    least: dict[str, float] = {}
    for s in travels:
        for p in swept_parts(ch, tyre_w, s):
            hub, r, (y0, y1) = p["hub"], p["r"], p["y"]
            nb, npts = near_of[(p["wheel"], p["part"])]
            for name, b in nb:
                rect = (b[0], b[2], b[3], b[5])
                d = (_pt_rect(hub, rect) if p["part"] == "tyre" else _seg_rect(p["pivot"], hub, rect)) - r
                g = _beside(d, _span_gap(y0, y1, b[1], b[4]))
                if g < least.get(name, math.inf):
                    least[name] = g
                if g < best.get(p["part"], {}).get("gap_mm", math.inf):
                    best[p["part"]] = dict(gap_mm=g, part=p["part"], wheel=p["wheel"], travel_mm=s, what=name, hub=hub)
            for name, q, rq in npts:
                c = (q[0], q[2])
                d = (math.dist(hub, c) if p["part"] == "tyre" else _seg_pt(p["pivot"], hub, c)) - r
                g = _beside(d, _span_gap(y0, y1, q[1], q[1])) - rq
                if g < least.get(name, math.inf):
                    least[name] = g
                if g < best.get(p["part"], {}).get("gap_mm", math.inf):
                    best[p["part"]] = dict(gap_mm=g, part=p["part"], wheel=p["wheel"], travel_mm=s, what=name, hub=hub)
    overall = min(best.values(), key=lambda b: b["gap_mm"])
    near = sorted(least.items(), key=lambda kv: kv[1])
    return dict(overall, tyre=best.get("tyre"), arm=best.get("arm"), near=[dict(what=n, gap_mm=round(g, 1)) for n, g in near])


# ------------------------------------------------------------------ solids for the 3D model
def member_solid(m: Member):
    """The member as a hollow tube with its true outer size and corner radii, on its centroid axis."""
    from build123d import Plane, RectangleRounded, Vector, extrude
    p0, p1 = Vector(*m.p0), Vector(*m.p1)
    ax = (p1 - p0).normalized()
    dz = Vector(*m.depth_dir)
    dz = (dz - ax * dz.dot(ax)).normalized()
    s = m.sec
    pl = Plane(origin=p0, x_dir=dz.cross(ax), z_dir=ax)
    prof = RectangleRounded(s.b, s.d, s.ro) - RectangleRounded(s.b - 2 * s.t, s.d - 2 * s.t, max(s.ro - s.t, 0.2))
    from .chassis_holes import cut_member
    return cut_member(m, extrude(pl * prof, amount=m.length))


def gusset_solid(ch: Chassis, g: dict, name: str):
    """A hinge gusset as made: its tube run on past both ends of its axis as far as its long side reaches, and cut off on
    the crossmember's face and the rail's inner face (Chassis.hinge_gussets)."""
    from .model.prims import box
    sec = ch.sections[next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
    run = sec.b / 2
    p0 = tuple(a - run * d for a, d in zip(g["p0"], g["dir"]))
    p1 = tuple(a + run * d for a, d in zip(g["p1"], g["dir"]))
    tube = member_solid(Member(g["id"], "hinge_gusset", name, sec, p0, p1))
    e, s, z, big = g["face"], g["side"], g["z"], 400.0
    x_cm, y_rail = g["rear_x"], g["y_in"]
    beyond_cm = box(x_cm - big if e > 0 else x_cm, min(p0[1], p1[1]) - big, z - big, big, 2 * big + 2 * g["leg"], 2 * big)
    beyond_rail = box(min(p0[0], p1[0]) - big, y_rail if s > 0 else y_rail - big, z - big, 2 * big + 2 * g["leg"], big, 2 * big)
    return tube - beyond_cm - beyond_rail


PLANES = {"xy": (0, 1, 2), "xz": (0, 2, 1), "yz": (1, 2, 0)}   # which axes the plate's length, width and thickness run along


def hole_x(row: dict, member_x) -> float:
    """A services hole's X (data/services.yaml `holes`): its own figure, or for a hole tied to a member that moves with
    the axle's solve, `x: {from: member, dx: mm}`, that member's X from member_x plus dx, so the hole keeps its place on
    the member wherever the axle's window puts it (CHS-10)."""
    x = row["x"]
    if isinstance(x, dict):
        return member_x(x["from"]) + float(x.get("dx", 0.0))
    return float(x)


def fitting_boxes(ch: Chassis, f: Fitting) -> list[tuple]:
    """Each position's box (x0, y0, z0, x1, y1, z1): plates in their plane, bought parts as their envelope or a small
    block. The bearer strips have none of their own (cad/trailer_model.py lays them on the members)."""
    spec = next(d for d in ch.data["fittings"] if d["id"] == f.id)
    if "box" in spec:
        x0, y0, z0, dx, dy, dz = ch.P.eval(spec["box"], {})
        return [(x0, y0, z0, x0 + dx, y0 + dy, z0 + dz)]
    if "boxes" in spec:   # a plate along a slanted member as axis-aligned boxes stepping along its line (CH-P03)
        return [(x0, y0, z0, x0 + dx, y0 + dy, z0 + dz) for x0, y0, z0, dx, dy, dz in (ch.P.eval(b, {}) for b in spec["boxes"])]
    if spec.get("poses") == "steadies":
        return [p["travel"] for p in ch.steady_poses()]
    if spec.get("poses") == "hinge_gussets":                  # each 45 degree gusset's plan between its two cut faces
        h = ch.sections[spec["section"]].d / 2
        return [(min(x for x, _ in g["outline"]), min(y for _, y in g["outline"]), g["z"] - h,
                 max(x for x, _ in g["outline"]), max(y for _, y in g["outline"]), g["z"] + h) for g in ch.hinge_gussets()]
    if spec.get("poses") == "hinge_cheeks":                   # each hinge cheek's plate (xt_hinges)
        return [b for c in ch.hinge_cheeks() for b in c["boxes"]]
    if f.kind == "angles":                                    # the shear panel's welded angles, each leg (panel_pieces)
        return [b for p in ch.panel_pieces() if p["galvanised"] for b in p["boxes"]]
    if f.kind == "strip":
        return []
    if f.kind == "plate":
        size = [0.0, 0.0, 0.0]
        for v, axis in zip(f.dims, PLANES[spec.get("plane", "xy")]):
            size[axis] = v
    elif f.kind == "tube":
        size = [spec["length"], 50.0, 50.0]
    else:
        size = list(spec.get("size", (120, 120, 120)))
    half = [s / 2 for s in size]
    return [(p[0] - half[0], p[1] - half[1], p[2] - half[2], p[0] + half[0], p[1] + half[1], p[2] + half[2]) for p in f.at]


def fitting_solids(ch: Chassis, f: Fitting) -> list:
    """The fitting's boxes as solids, for the 3D model. The hinge gussets are their tubes on the 45 degree line."""
    from .model.prims import box
    spec = next(d for d in ch.data["fittings"] if d["id"] == f.id)
    if spec.get("poses") == "hinge_gussets":
        return [gusset_solid(ch, g, f.name) for g in ch.hinge_gussets()]
    from .chassis_holes import cut_plates
    return cut_plates(ch, f, [box(x0, y0, z0, x1 - x0, y1 - y0, z1 - z0) for x0, y0, z0, x1, y1, z1 in fitting_boxes(ch, f)])

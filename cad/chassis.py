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
# an XT arm's bush between its pair of hinge plates on the elastic hinge bar (I2-114), a 1 mm link down the pivot's
# axis' normal, its depth along X: "free" passes a force each way, stiffly, and almost no moment, so the arm holds none
# of the bar's bending or twist, and "stiff" passes the moments across the pivot's axis too, so the arm's tube holds the
# bar's bending between its bushes, and turns freely about that axis in both. Marked rigid so the stress readings skip it
BUSHES = {"free": Section("bush, free", A=1.0e5, I_strong=100.0, I_weak=100.0, J=100.0, rigid=True),
          "stiff": Section("bush, stiff", A=1.0e5, I_strong=100.0, I_weak=1.0e8, J=1.0e8, rigid=True)}


def weld_spring(length: float, leg: float) -> Section:
    """A point of a fillet weld on the elastic hinge bar (xt_hinges `bar`, I2-121): a link 1 mm long normal to the
    crossmember's underside, its depth along X, standing for `length` mm of a `leg` fillet, so it passes the weld's own
    stiffness and no moment. Per mm of weld the fillet's throat a = 0.7 leg shears over its leg at G a / leg along and
    across its line and stretches at E a / leg normal to the face (est., the weld metal's own stiffness, the parts beside
    it taken as stiff). Marked rigid so the stress readings skip it."""
    a, E = 0.7 * leg, 200_000.0
    k_s, k_n = G_STEEL * a / leg * length, E * a / leg * length
    return Section(f"weld, {length:.1f} mm of a {leg:g} mm fillet", A=k_n / E, I_strong=k_s / (12 * E), I_weak=k_s / (12 * E),
                   J=1.0, rigid=True)
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
def arm_clear() -> float:
    """FIT-05's least gap from the tyres and the XT arms (data/checks.yaml), the one figure the parts over the arms are
    cut clear by (Chassis.arm_cuts)."""
    raw = yaml.safe_load((DATA / "checks.yaml").read_text())
    return float(next(c for c in raw["trailer_checks"] if c["id"] == "FIT-05")["min_gap_mm"])


def rect_minus(rect: tuple, cuts: list) -> list[tuple]:
    """The plan rectangle (x0, y0, x1, y1) less the rectangles `cuts`, as rectangles: cut in strips along X at every
    cut's ends, and each strip across at the sides of the cuts that cover it."""
    x0, y0, x1, y1 = rect
    xs = sorted({x0, x1} | {v for c in cuts for v in (c[0], c[2]) if x0 < v < x1})
    out = []
    for xa, xb in zip(xs, xs[1:]):
        y, free = y0, []
        for a, b in sorted((c[1], c[3]) for c in cuts if c[0] <= xa + 1e-6 and c[2] >= xb - 1e-6 and c[3] > y0 and c[1] < y1):
            if a > y:
                free.append((y, min(a, y1)))
            y = max(y, b)
        if y < y1:
            free.append((y, y1))
        out += [(xa, a, xb, b) for a, b in free if b - a > 1e-6 and xb - xa > 1e-6]
    return out


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

    def station_w(self, st: dict) -> float:
        """A crossmember station's width along X: its own `w` where the layout gives one (the XT hinge crossmembers), else
        xm_w."""
        return st.get("w", self.V["xm_w"])

    def station_x(self, st: dict) -> float:
        """Centre X of a crossmember station (stations give the front face)."""
        return st["x"] + self.station_w(st) / 2

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
            xa, xb = sa["x"] + self.station_w(sa), sb["x"] - pb.get("rear_ahead", 0.0)
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
        out, angles = [], []
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
            elif f.get("poses") == "hinge_fillers":   # each filler's mass at its centre (xt_hinges `filler`, I2-118)
                at = [c["centre"] for c in self.hinge_fillers()]
            elif f.get("poses") == "shock_plates":    # each shock support plate flush on its crossmember's front face
                at = [p["centre"] for p in self.shock_plates()]
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
            elif kind == "plate" and f.get("poses") == "hinge_fillers":   # each filler at its own size (I2-118)
                bs = [c["box"] for c in self.hinge_fillers()]
                dims = tuple(round(bs[0][i + 3] - bs[0][i], 1) for i in range(3))
                m = dims[0] * dims[1] * dims[2] * dens / 1e9
                out.append(Fitting(f["id"], f["name"], "plate", len(bs), at, m, "calculated",
                                   f"Calculated: {dims[0]:g} x {dims[1]:g} x {dims[2]:g} mm of steel at {dens} kg/m3", t=dims[2], dims=dims,
                                   area_m2_each=2 * (dims[0] * dims[1] + dims[1] * dims[2] + dims[0] * dims[2]) / 1e6))
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
            elif kind == "angles":                  # the shear panel's pieces, placed once the others stand (below)
                angles.append((len(out), f))
            elif kind == "strip":
                L = self.strip_length()
                out.append(Fitting(f["id"], f["name"], kind, 1, [(self.V["body_x0"] + self.V["body_length"] / 2, 0.0, self.V["floor_underside_z"] - 10)],
                                   f["kg_per_m"] * L / 1000, f["maturity"], f"{f['source']}, {L / 1000:.1f} m"))
            else:
                if len(at) < qty:
                    at = (at * qty)[:qty]
                out.append(Fitting(f["id"], f["name"], kind, qty, at, f["mass_kg"], f["maturity"], f["source"]))
        # the shear panel's pieces, each at its own centre (panel_pieces): the rails' angles end short of the rear airbags'
        # brackets, which stand where the kit's parts do (xt_parts), and those read the shock plates CH-P07 placed above
        self.fittings = out
        for k, f in reversed(angles):
            ps = self.panel_pieces()
            ctr = [tuple((p["boxes"][0][i] + p["boxes"][0][i + 3]) / 2 for i in range(3)) for p in ps]
            parts = ", ".join(f"{p['length']:.0f} mm of {load_angles()[p['section']]['designation'].replace('x', ' x ')}" for p in ps)
            out.insert(k, Fitting(f["id"], f["name"], f["kind"], 1, ctr, sum(p["mass_kg"] for p in ps), "calculated",
                                  f"Calculated: {parts}, at each section's kg/m", t=5.0, area_m2_each=sum(p["area_m2"] for p in ps)))
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
        crossmember to the front face of the next, between the rails' inner faces. `sheet` is the sheet as cut
        (panel_sheet), `bolts` its bolts, each with its group (panel_pieces), and `ties` the two diagonals the frame model
        carries it as: each from a rail's angle, at its bolts' middle, to the far side's bolts under the next crossmember,
        at their middle."""
        V, out = self.V, []
        st = {m.station: m for m in self.members if m.role.startswith("cm")}
        for d in self.data.get("shear_panels", []):
            m0, m1 = st[d["from"]], st[d["to"]]
            x0, x1 = m0.p0[0] + m0.sec.b / 2, m1.p0[0] - m1.sec.b / 2
            pieces = self.panel_pieces()
            bolts = [b for p in pieces for b in p["bolts"]]
            ties = []
            for s in (-1, 1):
                near = [b for b in bolts if b["group"] == "rail" and b["y"] * s > 0]
                far = [b for b in bolts if b["group"] == "rear" and b["y"] * s < 0]
                ties.append(dict(side=s, rail_x=sum(b["x"] for b in near) / len(near), cm=m1.id,
                                 cm_y=sum(b["y"] for b in far) / len(far)))
            out.append(dict(id=d["id"], x0=x0, x1=x1, b=2 * (V["rail_c"] - self.role_sec["rail"].b / 2), t=d["t"], fixing=d.get("fixing"),
                            sheet=self.panel_sheet(d, x0, x1, pieces), bolts=bolts, ties=ties, cut_clear=(d.get("cut") or {}).get("clear", 0.0)))
        return out

    def panel_mass(self, pid: str) -> dict:
        """Shear panel pid's sheet as cut and drilled (panel_sheet): its area in plan, its parts and tongues with the
        fillets the tongues' radiused roots and the cut's inner corners add, less its bolt holes, its steel at the frame's
        density, its zinc on both faces at AS/NZS 4680's rate for its thickness, and the two together, for the line that
        carries it (UF-03)."""
        d = next(p for p in self.data["shear_panels"] if p["id"] == pid)
        pn = next(p for p in self.shear_panels() if p["id"] == pid)
        sh = pn["sheet"]
        rects = sh["parts"] + sh["tongues"]
        fillets = (2 * len(sh["tongues"]) * sh["root_r"] ** 2 + len(sh["corners"]) * sh["cut_r"] ** 2) * (1 - math.pi / 4)
        holes = len(pn["bolts"]) * math.pi * d["fixing"]["hole"] ** 2 / 4
        area = sum(abs((r[2] - r[0]) * (r[3] - r[1])) for r in rects) + fillets - holes
        steel = area * d["t"] * self.data["material"]["density"] / 1e9
        zinc = 2 * area / 1e6 * self.galv_rate(d["t"])
        return dict(id=pid, area_m2=area / 1e6, steel_kg=steel, zinc_kg=zinc, kg=steel + zinc, t=d["t"], material=d["material"],
                    density=self.data["material"]["density"], zinc_kg_m2=self.galv_rate(d["t"]), holes=len(pn["bolts"]))

    def panel_cut(self, d: dict, x0: float, x1: float) -> tuple[float, float] | None:
        """Where the kit's parts named in `cut` `parts` (xt_parts: the rear airbags over their travel and the rear shocks
        over the arms') pass through the sheet's plane between x0 and x1, each grown by `clear`: the X of the first one's
        front and the least |Y| of their inboard sides, or None where none does."""
        c = d.get("cut")
        if not c:
            return None
        zt = self.V["rail_underside_z"] - next(f for f in self.data["fittings"] if f["id"] == "CH-P17")["drop"]
        za, zb = zt - d["t"] - c["clear"], zt + c["clear"]
        boxes = [bx for p in self.xt_parts() if any(p["id"].startswith(k + "-R") for k in c["parts"]) for bx in p["boxes"]
                 if bx[2] < zb and bx[5] > za and bx[3] + c["clear"] > x0 and bx[0] - c["clear"] < x1]
        if not boxes:
            return None
        return min(bx[0] for bx in boxes) - c["clear"], min(min(abs(bx[1]), abs(bx[4])) for bx in boxes) - c["clear"]

    def panel_sheet(self, d: dict, x0: float, x_rear: float, pieces: list[dict]) -> dict:
        """The panel's sheet in plan: its front edge `front_gap` behind the front crossmember's rear face, its rear edge at
        the next crossmember's face, its sides `edge` inside the rails' inner faces, cut clear of the kit's parts at the
        rails' sides from the cut's X back to the rear edge and outboard of its Y (panel_cut), and a tongue under each
        crossmember angle, as wide as the angle and `tongue` short of its flat leg's toe, its two corners at its root
        radiused `tongue_r` (`root_r`). `parts` are the sheet's rectangles without the tongues, each (x0, y0, x1, y1), the
        cut's two inner corners each radiused `cut` `r` (`cut_r`). `roots` gives each tongue's root line, its X on the
        sheet's edge, and which way the tongue runs from it (-1 forward, 1 rearward), and `wings` each part outboard of
        the cut, ahead of it, with its root line along the main part's side."""
        V = self.V
        half = V["rail_c"] - self.role_sec["rail"].b / 2 - d["edge"]
        front = x0 + d.get("front_gap", 0.0)
        cut = self.panel_cut(d, front, x_rear)
        tongues, roots = [], []
        for p in (p for p in pieces if p["use"] == "crossmember"):
            toe = p["toe_x"] + p["face"] * d.get("tongue", 0.0)
            root = front if p["face"] > 0 else x_rear
            xa, xb = sorted((toe, root))
            tongues.append((xa, p["y0"], xb, p["y1"]))
            roots.append(dict(x=root, way=-p["face"], y0=p["y0"], y1=p["y1"], piece=p["id"]))
        if cut is None:
            parts, corners, wings, holes = [(front, -half, x_rear, half)], [], [], []
        else:
            xc, yc = cut
            parts = [(front, -yc, x_rear, yc), (front, -half, xc, -yc), (front, yc, xc, half)]
            corners = [(xc, -yc), (xc, yc)]
            wings = [dict(side=-1, rect=parts[1], root=(front, xc, -yc)), dict(side=1, rect=parts[2], root=(front, xc, yc))]
            holes = [(xc, -half, x_rear, -yc), (xc, yc, x_rear, half)]
        zt = V["rail_underside_z"] - next(f for f in self.data["fittings"] if f["id"] == "CH-P17")["drop"]
        steps = [(c[0], c[1], c[3], c[4]) for c in self.arm_cuts((front, -half, zt - d["t"], x_rear, half, zt))]
        if steps:                                   # the front corners cut away clear of the arms' pivot tubes and inner legs
            parts = [r for p in parts for r in rect_minus(p, steps)]
            holes = holes + steps
            for wg in wings:
                x0w, x1w, yr = wg["root"]
                cover = sorted((c[0], c[2]) for c in steps if c[1] - 1e-6 <= yr <= c[3] + 1e-6)
                free, x = [], x0w
                for a, b in cover:
                    if a > x:
                        free.append((x, min(a, x1w)))
                    x = max(x, b)
                if x < x1w:
                    free.append((x, x1w))
                wg["root"] = (*max(free, key=lambda f: f[1] - f[0]), yr)
        return dict(rect=(front, -half, x_rear, half), parts=parts, tongues=tongues, roots=roots, root_r=d.get("tongue_r", 0.0),
                    front=front, half=half, cut=cut, corners=corners, wings=wings, cut_r=(d.get("cut") or {}).get("r", 0.0), holes=holes,
                    steps=steps)

    def panel_pieces(self) -> list[dict]:
        """The shear panel's pieces CH-P17: each angle with its use (rail or crossmember), its section, its ends,
        its legs' boxes, its mass, its galvanised area, its welds as lines (what, from, to) and its bolts (x, y, group).
        The rails' angles run from `gap` behind the XT centre's rear hinge cheeks' ends to `before` ahead of the rear
        airbags' top brackets (xt_parts), and each crossmember's angles under their Y ranges, their bolts on the flat leg's
        `gauge` at their own `pitch`, `end` from each angle's ends."""
        V, spec = self.V, next(f for f in self.data["fittings"] if f["id"] == "CH-P17")
        ang, rail = load_angles(), self.role_sec["rail"]
        y_in = V["rail_c"] - rail.b / 2
        z_flat = V["rail_underside_z"] - spec["drop"]
        st = {m.station: m for m in self.members if m.role.startswith("cm")}
        centre = st["XT centre"]
        out = []

        def spaced(a0: float, a1: float, pitch: float, end: float) -> list[float]:
            n = int(math.floor((a1 - a0 - 2 * end) / pitch + 1e-9)) + 1
            first = a0 + (a1 - a0 - (n - 1) * pitch) / 2
            return [first + k * pitch for k in range(n)]

        r = spec["rails"]
        a = ang[r["section"]]
        x0 = max(c["box"][3] for c in self.hinge_cheeks() if c["box"][0] >= centre.p0[0]) + r["gap"]
        x1 = min(p["boxes"][0][0] for p in self.xt_parts() if p["id"].startswith("XT-BAGBKT-R")) - r["before"]
        for s in (-1, 1):
            y_web = s * y_in
            up = (x0, min(y_web, y_web - s * a["t"]), z_flat, x1, max(y_web, y_web - s * a["t"]), z_flat + a["d"])
            flat = (x0, min(y_web, y_web - s * a["d"]), z_flat, x1, max(y_web, y_web - s * a["d"]), z_flat + a["t"])
            yb = y_web - s * spec["gauge"]
            out.append(dict(id=f"CH-P17-R{SIDES[s]}", use="rail", side=s, section=r["section"], x0=x0, x1=x1, length=x1 - x0,
                            boxes=[up, flat], galvanised=True,
                            welds=[("top edge", (x0, y_web, z_flat + a["d"]), (x1, y_web, z_flat + a["d"])),
                                   ("rail's bottom corner", (x0, y_web, V["rail_underside_z"]), (x1, y_web, V["rail_underside_z"]))],
                            bolts=[dict(x=x, y=yb, group="rail", along="x") for x in spaced(x0, x1, r["pitch"], r["end"])]))
        for c in spec["crossmembers"]:
            a, m = ang[c["section"]], st[c["station"]]
            f = c["face"]                       # 1 on the crossmember's rear face, -1 on its front face, the flat leg under it
            x_web = m.p0[0] + f * m.sec.b / 2
            heel = x_web + f * a["t"]
            toe = heel - f * a["d"]
            for k, (y0, y1) in enumerate(c["ys"], 1):
                up = (min(x_web, heel), y0, z_flat, max(x_web, heel), y1, z_flat + a["d"])
                flat = (min(toe, heel), y0, z_flat, max(toe, heel), y1, z_flat + a["t"])
                out.append(dict(id=f"CH-P17-{m.id}-{k}", use="crossmember", member=m.id, station=c["station"], face=f, section=c["section"],
                                y0=y0, y1=y1, length=y1 - y0, x_web=x_web, heel_x=heel, toe_x=toe, boxes=[up, flat], galvanised=True,
                                welds=[("top edge", (x_web, y0, z_flat + a["d"]), (x_web, y1, z_flat + a["d"])),
                                       ("crossmember's bottom corner", (x_web, y0, V["rail_underside_z"]), (x_web, y1, V["rail_underside_z"]))],
                                bolts=[dict(x=heel - f * spec["gauge"], y=y, group="rear", along="y") for y in spaced(y0, y1, c["pitch"], c["end"])]))
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
        along its top edge and the rail's bottom corner and to the hinge bar's front or rear face (I2-88). Where the bar's
        front face stands behind its crossmember's, a front cheek meets the filler CH-P18 there instead (hinge_fillers,
        I2-118), or with no filler its part under the rail runs on under the crossmember to the bar, its `tail`. `joint_x`
        is where each cheek meets the bar or its filler."""
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
                face = w["station_x"] + e * cm.sec.b / 2
                x0 = face if e > 0 else face - ck["l"]
                y0 = w["side"] * y_in - (ck["t"] if w["side"] > 0 else 0.0)
                box = (x0, y0, z0, x0 + ck["l"], y0 + ck["t"], z0 + ck["h"])
                boxes, area = [box], ck["l"] * ck["h"]
                reach = self.hinge_bar_x(cm) - self.data["xt_arms"]["parts"]["bar"].get("w", cm.sec.b) / 2 - face
                tail = reach if e < 0 and reach > 1e-6 and not self.data["xt_hinges"].get("filler") else 0.0
                if tail:                                # the bar's front face behind the crossmember's: the plate's part under the
                    boxes.append((face, y0, z0, face + reach, y0 + ck["t"], V["rail_underside_z"]))   # rail runs on under it to the bar
                    area += reach * (V["rail_underside_z"] - z0)
                if gusset:                              # the step where the gusset lands, centred on its footprint (I2-99)
                    xc = face + e * (self.ev(g["length"]) / math.sqrt(2) - ck["t"])
                    ls, z0s, z1s = (self.step_size(cm.station, k) for k in ("l", "z0", "z1"))
                    za, zb = V["rail_underside_z"] + z0s, V["rail_underside_z"] + z1s
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
                                gusset=f"CH-P08-{gid}" if gusset else None, tail=tail, joint_x=face + tail))
        return out

    def hinge_fillers(self) -> list[dict]:
        """The hinge cheek fillers CH-P18 (xt_hinges `filler`, I2-118): at each XT hinge whose bar's front face stands
        behind its crossmember's, a steel block `d` deep under the crossmember's front half from the crossmember's front face
        to the bar's front face, from `inboard` inboard of the rail's inner face out under the rail to its outer face, where
        the bar's long end stands, so FIT-05 keeps its 50 mm from the arms' pivot tubes (est.). The front cheek's part under
        the rail meets its front face, so the cheek meets it where it met the bar on a 50 mm crossmember, and its `bar_leg`
        fillets weld it there. A `leg` fillet welds the filler to the bar's front face along its bottom rear edge, the bar
        standing deeper, and another to the crossmember's underside along its inboard top edge, and flare-bevel welds join
        it to the crossmember's rounded bottom front corner inboard of the cheek's fillets and to the rail's rounded outer
        bottom corner, along the rail, as the corner steadies' brackets are (TB 070), its top rear edge chamfered `chamfer`
        clear of the bar's first run."""
        fd = self.data["xt_hinges"].get("filler")
        if not fd:
            return []
        V, rail, ck = self.V, self.role_sec["rail"], self.data["xt_hinges"]["cheek"]
        y_in, y_out, zu = V["rail_c"] - rail.b / 2, V["rail_c"] + rail.b / 2, V["rail_underside_z"]
        bar = self.data["xt_arms"]["parts"]["bar"]
        out = []
        for w in self.suspension:
            cm = next(m for m in self.hinge_crossmembers() if abs(m.p0[0] - w["station_x"]) < 1.0)
            front = w["station_x"] - cm.sec.b / 2
            bar_front = self.hinge_bar_x(cm) - bar.get("w", cm.sec.b) / 2
            if bar_front - front < 1e-6:
                continue
            s = w["side"]
            ya, yb = sorted((s * y_out, s * (y_in - fd["inboard"])))
            box = (front, ya, zu - fd["d"], bar_front, yb, zu)
            out.append(dict(id=f"CH-P18-{w['id']}", wheel=w["id"], side=s, box=box, front=front, bar_front=bar_front,
                            inner_y=s * (y_in - fd["inboard"]), outer_y=s * y_out, z0=zu - fd["d"], z1=zu, cm=cm.id,
                            flare_y=s * (y_in - ck["t"] - ck["bar_leg"]), centre=tuple((box[i] + box[i + 3]) / 2 for i in range(3))))
        return out

    def step_size(self, station: str, key: str) -> float:
        """A hinge cheek's step at a hinge crossmember's station (xt_hinges `cheek` `under_gusset`): its length `l` along
        the rail, or its lower and upper edges `z0` and `z1` over the rail's underside, each one figure or one per station."""
        v = self.data["xt_hinges"]["cheek"]["under_gusset"][key]
        return float(v[station] if isinstance(v, dict) else v)

    def hinge_weld_ys(self, cm: Member) -> list[float]:
        """The Y of each run of a hinge bar's welds to its crossmember (xt_hinges `bar`), both sides, centres measured from
        the rail's inner face."""
        if cm not in self.hinge_crossmembers():
            return []
        y_in = self.V["rail_c"] - self.role_sec["rail"].b / 2
        return [s * (y_in - u) for s in (-1, 1) for u in self.data["xt_hinges"]["bar"]["runs"]]

    def hinge_run_points(self, cm: Member) -> list[float]:
        """The Y of each run's two ends and its centre (hinge_weld_ys), both sides, where the elastic hinge bar is tied to
        its crossmember, so each run acts over its whole length (I2-114)."""
        half = self.data["xt_hinges"]["bar"]["run"] / 2
        return [y + k * half for y in self.hinge_weld_ys(cm) for k in (-1, 0, 1)]

    def hinge_bar_section(self, cm: Member) -> Section:
        """The hinge bar under crossmember cm as a beam along Y (xt_hinges `bar` `section`, I2-114): a solid bar xt_arms parts
        `bar` `w` wide, Cruisemaster's 50 mm for a 50 mm crossmember, flush with the crossmember's rear face, and `d` deep
        (est.). Its strong axis bends it in the
        vertical plane, its weak axis across, and J is a solid rectangle's, a b cubed (1/3 - 0.21 (b / a) (1 - b^4 / 12 a^4))
        with a the longer side (Roark, Table 10.7)."""
        if self.data["xt_hinges"]["bar"].get("section", "solid") != "solid":
            raise ValueError("xt_hinges bar section: only a solid bar is modelled")
        bar = self.data["xt_arms"]["parts"]["bar"]
        w, d = bar.get("w", cm.sec.b), bar["d"]
        a, b = max(w, d), min(w, d)
        J = a * b ** 3 * (1 / 3 - 0.21 * (b / a) * (1 - b ** 4 / (12 * a ** 4)))
        return Section(f"hinge bar, solid {w:g} x {d:g}", A=w * d, I_strong=w * d ** 3 / 12, I_weak=d * w ** 3 / 12, J=J)

    def hinge_bar_x(self, cm: Member) -> float:
        """The X of the hinge bar's axis under crossmember cm: the bar flush with the crossmember's rear face, from which
        Cruisemaster's positions run, so on the XT hinge crossmembers 100 mm wide its front face stands 50 mm behind the
        crossmember's (xt_arms parts `bar` `w`)."""
        return cm.p0[0] + cm.sec.b / 2 - self.data["xt_arms"]["parts"]["bar"].get("w", cm.sec.b) / 2

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
            rear_face = st["x"] + self.station_w(st)
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

    def arm_bars(self, w: dict, s: float = 0.0) -> list[tuple]:
        """Wheel w's XT arm as Cruisemaster's 33XT AIR sheet 2's hinge plan and sheet 4's views draw it, at travel s (mm,
        up positive), which turns with the arm about the pivot (xt_arms `parts` `arm`, est.): its pivot tube between the
        outer and the inner hinge plates, the outer leg from its bush straight back along the rail to the rear beam, the
        brace between the legs at its front and rear edges, the rear beam from the inner leg's end out to the hub, which
        carries the airbag's mount, the shocks' clevises and the stub axle, and the inner leg from its bush closing on the
        outer leg to the beam. Each bar is ((x, y, z), (x, y, z), r0, r1) on its axis with its radius at each end: the
        tube and each leg at its bush `d` round, each leg growing to the arm's arm_depth at the beam, the beam at
        arm_depth. The tube comes first, the beam last but one and the inner leg last (routes.arm_lead)."""
        V, pr = self.V, self.data["xt_arms"]["parts"]
        y_in, sd = V["rail_c"] - self.role_sec["rail"].b / 2, w["side"]
        (px, _, pz), (hx, hy, hz) = w["pivot"], w["hub"]
        a = self.xt_arm_turn(w, s)
        arm = pr["arm"]

        def at(t, y_inboard):
            """The arm's point a fraction t of the way from the pivot to the hub in the side view, y_inboard of the rail's
            inner face (negative outboard), turned with the arm."""
            dx, dz = (hx - px) * t, (hz - pz) * t
            return (px + dx * math.cos(a) - dz * math.sin(a), sd * (y_in - y_inboard), pz + dx * math.sin(a) + dz * math.cos(a))

        ys, r, rh = pr["plates"]["y_in"], arm["d"] / 2, V["arm_depth"] / 2
        r_at = lambda t: r + (rh - r) * t  # noqa: E731
        out_y, in_y = arm["roots"]
        t_end, end_y = arm["inner_end"][0] / (hx - px), arm["inner_end"][1]
        hub_in = y_in - abs(hy)                                    # the hub, inboard of the rail's inner face (negative)
        k = (end_y - out_y) / (end_y - hub_in)                     # where the outer leg meets the beam
        t_out = t_end + (1 - t_end) * k
        leg_y = lambda t: in_y + (end_y - in_y) * t / t_end  # noqa: E731
        tube = ((px, sd * (y_in - ys[0] - r), pz), (px, sd * (y_in - ys[-1] + r), pz), r, r)   # its round ends at the end plates
        outer = (at(0.0, out_y), at(t_out, out_y), r, rh)
        braces = [(at(u / (hx - px), out_y), at(u / (hx - px), leg_y(u / (hx - px))), r_at(u / (hx - px)), r_at(u / (hx - px)))
                  for u in arm["brace"]]
        beam = (at(t_end, end_y), at(1.0, hub_in), rh, rh)
        inner = (at(0.0, in_y), at(t_end, end_y), r, rh)
        return [tube, outer, *braces, beam, inner]

    def arm_spheres(self, step: float = 4.0, steps: int = 25) -> list[tuple]:
        """Every XT arm's bars (arm_bars) at FIT-05's travels (wheel_sweep's `steps`), each as balls along its axis `step`
        apart at its radius there, each (x, y, z, r, side, wheel): the arm as FIT-05 sweeps it, which a part over the arms
        is cut clear of (arm_cuts)."""
        if getattr(self, "_arm_spheres", None) is None:
            travel, out = self.V["travel"], []
            for w in self.suspension:
                for k in range(steps + 1):
                    for a, c, r0, r1 in self.arm_bars(w, -travel + 2 * travel * k / steps):
                        n = max(1, math.ceil(math.dist(a, c) / step))
                        out += [(*(a[i] + (c[i] - a[i]) * j / n for i in range(3)), r0 + (r1 - r0) * j / n, w["side"], w["id"])
                                for j in range(n + 1)]
            self._arm_spheres = out
        return self._arm_spheres

    def arm_cuts(self, box: tuple, strip: float = 25.0, margin: float = 0.5) -> list[tuple]:
        """What to cut from a part `box` (x0, y0, z0, x1, y1, z1) over the XT arms so the rest keeps FIT-05's clearance
        (arm_clear) and `margin` from every arm over its travel (arm_spheres): for each arm, in strips `strip` long along X
        from where it first reaches the part's underside grown by that clearance to where it last does, from the least |Y|
        it reaches in the strip out to the part's side on its own side, and from the underside up as far as it reaches in
        that plan, the strips sharing their ends. Each (x0, y0, z0, x1, y1, z1), to 0.1 mm outward, so a plate's corner
        over an arm's pivot tube and inner leg is cut away in steps."""
        x0, y0, z0, x1, y1, z1 = box
        R = arm_clear() + margin
        near = []
        for cx, cy, cz, r, s, wid in self.arm_spheres():
            dz = max(z0 - cz, 0.0, cz - z1)
            if dz >= r + R:
                continue
            rho = math.sqrt((r + R) ** 2 - dz ** 2)
            if cx + rho > x0 and cx - rho < x1 and cy + rho > y0 and cy - rho < y1:
                near.append((cx, cy, cz, r, s, rho, wid))
        out = []
        for wid in sorted({b[6] for b in near}):
            balls = [b[:6] for b in near if b[6] == wid]
            s = balls[0][4]
            xa0 = math.floor(max(x0, min(b[0] - b[5] for b in balls)) * 10) / 10
            xb0 = math.ceil(min(x1, max(b[0] + b[5] for b in balls)) * 10) / 10
            n = max(1, math.ceil((xb0 - xa0) / strip - 1e-9))
            edges = [xa0] + [round(xa0 + (xb0 - xa0) * k / n, 1) for k in range(1, n)] + [xb0]   # shared, so no sliver is left between
            for xa, xb in zip(edges, edges[1:]):
                ys, top = [], z0
                for cx, cy, cz, r, _, rho in balls:
                    d = max(xa - cx, 0.0, cx - xb)
                    if d >= rho:
                        continue
                    h = math.sqrt(rho ** 2 - d ** 2)
                    if cy - h >= y1 or cy + h <= y0:              # it reaches the strip outside the part's sides
                        continue
                    ys.append(abs(cy) - h)
                if not ys:
                    continue
                ya, yb = (y0, -max(min(ys), 0.0)) if s < 0 else (max(min(ys), 0.0), y1)
                if yb <= ya:
                    continue
                for cx, cy, cz, r, _, rho in balls:          # how high it reaches inside the strip's plan
                    dp = math.hypot(max(xa - cx, 0.0, cx - xb), max(ya - cy, 0.0, cy - yb))
                    if dp < r + R:
                        top = max(top, cz + math.sqrt((r + R) ** 2 - dp ** 2))
                if top <= z0:
                    continue
                out.append((xa, math.floor(ya * 10) / 10, z0, xb, math.ceil(yb * 10) / 10, min(z1, math.ceil(top * 10) / 10)))
        return out

    def shock_plates(self) -> list[dict]:
        """The shock support plates CH-P07, a pair flush on the front face of each crossmember the data's `stations` names,
        `side_y` their middles from the centreline, full crossmember height: each with its member, side, box and centre."""
        spec = next(f for f in self.data["fittings"] if f["id"] == "CH-P07")
        sy, out = self.ev(spec["side_y"]), []
        for station in spec["stations"]:
            cm = next(m for m in self.members if m.station == station and m.role.startswith("cm"))
            face, (_, _, z0, _, _, z1) = cm.p0[0] - cm.sec.b / 2, cm.box()
            for s in (-1, 1):
                box = (face - spec["t"], s * sy - spec["l"] / 2, z0, face, s * sy + spec["l"] / 2, z1)
                out.append(dict(id=f"CH-P07-{cm.id}{SIDES[s]}", member=cm.id, side=s, box=box, face=face,
                                centre=tuple((box[i] + box[i + 3]) / 2 for i in range(3))))
        return out

    def shock_plate_t(self, cm) -> float:
        """The thickness of the shock support plate CH-P07 on crossmember cm's front face, 0 where the data puts none."""
        f = next(f for f in self.data["fittings"] if f["id"] == "CH-P07")
        return float(f["t"]) if any(p["member"] == cm.id for p in self.shock_plates()) else 0.0

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
            xr = cm.p0[0] + cm.sec.b / 2
            xf = xr - pr["bar"].get("w", cm.sec.b)                 # the bar flush with the crossmember's rear face
            ya, yb = sorted((s * y_out, s * (y_in - pr["bar"]["inboard"])))
            out.append(dict(id=f"XT-BAR-{wid}", what="Cruisemaster's hinge bar under the crossmember", wheel=wid,
                            boxes=[(xf, ya, zu - pr["bar"]["d"], xr, yb, zu)]))
            px = w["pivot"][0]
            hy = ys(*pr["hinge"]["y_in"])
            pl = pr["plates"]
            plates = [(px - pl["l"] / 2, min(ys(u - pl["t"] / 2, u + pl["t"] / 2)), zu - pl["below"],
                       px + pl["l"] / 2, max(ys(u - pl["t"] / 2, u + pl["t"] / 2)), zu - pr["bar"]["d"]) for u in pl["y_in"]]
            bars = self.arm_bars(w)
            out.append(dict(id=f"XT-HINGE-{wid}", what="the arm's hinge plates, bushes and pivot tube", wheel=wid, plates=plates,
                            tube=((px, s * (y_in - pl["y_in"][0]), w["pivot"][2]), (px, s * (y_in - pl["y_in"][-1]), w["pivot"][2])),
                            legs=bars[1:],
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
        return dict(crossmember_stations=[self.station_x(st) for st in self.stations], body_x0=V["body_x0"], db_end_x=V["db_end_x"],
                    chain_lug_x=V["chain_lug_x"], hub_front_x=self.hub_x("front"), hub_rear_x=self.hub_x("rear"),
                    rear_tongue_x=V["body_x1"] - 70, front_recovery_x=V["front_recovery_x"], root_gusset_toe_x=V["root_gusset_toe_x"],
                    steady_x=sorted({p["x"] for p in self.steady_poses()}),
                    cheek_ends_x=sorted({x for c in self.hinge_cheeks() if c["l"] <= 300.0 for b in c["boxes"] for x in (b[0], b[3])}),
                    panel_angle_ends_x=sorted({x for p in self.panel_pieces() if p["use"] == "rail" for x in (p["x0"], p["x1"])}))

    # -- the frame model ----------------------------------------------
    def frame(self, body: list[tuple[float, float, float]] | None = None, hinges: str = "crossmember",
              hinge_bar: str = "rigid", bushes: str = "free") -> "FrameModel":
        """The frame model. `body` adds the body as a torsion box (cad/body.py): (x0, x1, GJ in N mm2) per bay between
        stations, tied rigidly to both rails at each station, as the floor's bolts tie it (BODY.md). `hinges` "crossmember"
        ties each XT pivot to its crossmember at the hinge bar's welds, with the gussets as members (CHS-12). `hinge_bar`
        is one of xt_hinges `bar` `bounds`: "rigid" holds the bar rigid from the pivot to its runs' centres, "elastic" builds
        it at its own section with each run over its length, its arm on `bushes` "stiff" or "free" (I2-114)."""
        return FrameModel(self, body, hinges, hinge_bar, bushes)


class FrameModel:
    """Nodes and elements of the chassis and drawbar, with the lookups the load mapping needs."""

    def __init__(self, ch: Chassis, body: list[tuple[float, float, float]] | None = None, hinges: str = "crossmember",
                 hinge_bar: str = "rigid", bushes: str = "free"):
        self.ch = ch
        self.hinges = hinges
        self.hinge_bar = hinge_bar if hinges == "crossmember" else "rigid"
        self.bushes = bushes
        elastic = self.hinge_bar == "elastic"
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
        xs |= {t["rail_x"] for sp in ch.shear_panels() for t in sp["ties"]}   # where a shear panel's sheet is bolted to a rail
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
                # the elastic hinge bar's ties at each run's ends and centre keep their nodes, the others within 5 mm go
                runs = set(ch.hinge_run_points(m)) if elastic else set()
                ys = sorted(runs | {y for y in ys if all(abs(y - r) > 5.0 for r in runs)})
                ys = [y for k, y in enumerate(ys) if k == 0 or y - ys[k - 1] > 5.0 or abs(y) == V["rail_c"] or y in runs]
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
                for y in ([] if elastic else ch.hinge_weld_ys(cm)):
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
                sp = cheek_props(ck, cm.sec.b, n)
                z_pin = V["rail_underside_z"] - ck["bar_d"] / 2
                bar = f.node((w["pivot"][0], w["pivot"][1], z_pin - 1.0))
                pin = f.node((w["pivot"][0], w["pivot"][1], z_pin))
                top = f.node((w["pivot"][0], w["pivot"][1], V["rail_underside_z"]))
                if elastic:
                    self._elastic_bar(w, cm, nd, bar)
                else:
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
        # shear panels (shear_panels, I2-87): each sheet as two diagonals, each from a rail's angle at its bolts' middle to
        # the far side's bolts under the next crossmember (Chassis.shear_panels `ties`), of the sheet's shear stiffness over
        # its net width b_n between the cuts and its length a from those bolts to the crossmember's face, G t b_n / a, which
        # two diagonals give as 2 E A (dy / L) squared / L, so A = G t b_n L^3 / (2 E a dy^2) (est.)
        self.panels = []
        for sp in ch.shear_panels():
            t, sh = sp["t"], sp["sheet"]
            b_n = 2 * (sh["cut"][1] if sh["cut"] else sh["half"])
            els, geo = [], []
            for k, tie in enumerate(sp["ties"]):
                n0, n1 = self.rail_node(tie["side"], tie["rail_x"]), self.cm_node(tie["cm"], tie["cm_y"])
                p0, p1 = f.nodes[n0], f.nodes[n1]
                geo.append((math.dist(p0, p1), abs(p1[1] - p0[1]), sp["x1"] - tie["rail_x"]))
                els.append((n0, n1))
            L, dy, a = (sum(g[i] for g in geo) / len(geo) for i in range(3))
            A = G_STEEL * t * b_n * L ** 3 / (2 * 200_000.0 * a * dy ** 2)
            dsec = Section(f"shear panel {sp['id']} diagonal", A=A, I_strong=1.0, I_weak=1.0, J=1.0)
            idx = []
            for k, (n0, n1) in enumerate(els):
                f.add(n0, n1, dsec, (0, 0, 1), f"{sp['id']}-D{k + 1}")
                idx.append(len(f.elements) - 1)
            self.panels.append(dict(sp, elements=idx, A=A, L=L, a=a, dy=dy, b_n=b_n))
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

    def _elastic_bar(self, w: dict, cm, pivot: int, under_pin: int):
        """Wheel w's hinge bar as the beam it is (xt_hinges `bar`, I2-114): Chassis.hinge_bar_section along the
        crossmember's underside, from the cheeks' fillets to it beside the rail's inner web, past the arm's four hinge
        plates and along the three weld runs, each run tied to the crossmember at its two ends and its centre, so it acts
        over its whole length. Each pair of plates hangs rigid from the bar with the bolt through them and the bush's
        sleeve clamped between them, on the pivot's axis. The arm's pivot tube is rigid from the pivot to its two bushes,
        each bush (BUSHES, `self.bushes`) free, passing a force but almost no moment, so the arm holds the bar at its
        plates and none of its bending or twist between the pairs, as Cruisemaster's greased polyurethane bushes nearly
        do, or stiff, holding the bar's bending between them as a rigid tube would. The cheeks hang off the bar at their
        fillets, `under_pin` being the node under their pin."""
        ch, f, V = self.ch, self.f, self.ch.V
        s, wid = w["side"], w["id"]
        parts = ch.data["xt_arms"]["parts"]
        y_in = V["rail_c"] - ch.role_sec["rail"].b / 2
        d = parts["bar"]["d"]
        x, z = ch.hinge_bar_x(cm), V["rail_underside_z"] - d / 2
        pin_y = s * (y_in - ch.data["xt_hinges"]["cheek"]["t"] / 2)
        plates = [s * (y_in - u) for u in parts["plates"]["y_in"]]
        runs = [y for y in ch.hinge_run_points(cm) if y * s > 0]
        ys = sorted({pin_y, *plates, *runs}, key=lambda y: -abs(y))
        at = {y: f.node((x, y, z)) for y in ys}
        sec = ch.hinge_bar_section(cm)
        for a, b in zip(ys, ys[1:]):
            f.add(at[a], at[b], sec, (0, 0, 1), f"XT-BAR-{wid}")
        self._weld_runs(w, cm, at, x)
        self._link(at[pin_y], under_pin, f"hinge bar {wid}")
        px, _, pz = w["pivot"]
        pl = parts["plates"]
        psec = Section(f"hinge plate, {pl['t']:g} x {pl['l']:g}", A=pl["t"] * pl["l"], I_strong=pl["t"] * pl["l"] ** 3 / 12,
                       I_weak=pl["l"] * pl["t"] ** 3 / 12, J=pl["l"] * pl["t"] ** 3 / 3 * (1 - 0.63 * pl["t"] / pl["l"]))
        self.sec_props.setdefault(f"XT-PLATE-{wid}", psec)
        for u, pair in zip(parts["arm"]["roots"], (plates[:2], plates[2:])):
            bolt, tube = f.node((px, s * (y_in - u), pz)), f.node((px, s * (y_in - u), pz - 1.0))
            for y in pair:              # each plate welded under the bar, its own section down to the bolt (I2-121)
                top, foot = f.node((px, y, z - d / 2)), f.node((px, y, pz))
                self._link(at[y], top, f"hinge plate {wid}")
                f.add(top, foot, psec, (1, 0, 0), f"XT-PLATE-{wid}")
                self._link(foot, bolt, f"hinge plate {wid}")
            f.add(tube, bolt, BUSHES[self.bushes], (1, 0, 0), f"bush {wid}")
            self._link(pivot, tube, f"pivot tube {wid}")

    def _weld_runs(self, w: dict, cm, at: dict, x: float):
        """Wheel w's elastic hinge bar welded to crossmember cm by its weld runs (xt_hinges `bar`, I2-121): each run's two
        `leg` fillets along the bar's top edges, `w` apart, each a weld point at the run's two ends and its centre carrying
        a sixth, two thirds and a sixth of its `run` mm (Simpson's rule, so the points give the line's own stiffness along
        it and against turning), each point a weld_spring between the bar's edge and the crossmember's underside. The bar
        and the crossmember reach each point by rigid links from their axes, so a run passes a moment only as its welds'
        forces apart, as its own weld group does, and none at a point."""
        ch, f = self.ch, self.f
        b = ch.data["xt_hinges"]["bar"]
        bw = ch.data["xt_arms"]["parts"]["bar"].get("w", cm.sec.b)
        zf = cm.box()[2]
        for yc in (y for y in ch.hinge_weld_ys(cm) if y * w["side"] > 0):
            for k, share in ((-1, 1 / 6), (0, 2 / 3), (1, 1 / 6)):
                y = yc + k * b["run"] / 2
                spring = weld_spring(share * b["run"], b["leg"])
                for e in (-1, 1):
                    lo, hi = f.node((x + e * bw / 2, y, zf - 0.5)), f.node((x + e * bw / 2, y, zf + 0.5))
                    self._link(at[min(at, key=lambda q: abs(q - y))], lo, f"weld runs {w['id']}")
                    self._link(self.cm_node(cm.id, y), hi, f"weld runs {w['id']}")
                    f.add(lo, hi, spring, (1, 0, 0), f"hinge {w['id']}")

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
    The tyre is a cylinder of the published diameter in its own plane. The arm is Cruisemaster's A-frame as sheets 2
    and 4 draw it (Chassis.arm_bars): its pivot tube between the hinge plates, its two legs from the bushes back to the
    rear beam, the brace between them and the beam out to the hub (est.), whose `bars` FIT-05 measures in space. Its `pivot`, `hub` and `y` give its
    side view and its span across the trailer."""
    V = ch.V
    out = []
    for w in ch.suspension:
        px, _, pz = w["pivot"]
        dz = V["arm_drop"] - s
        hub = (px + math.sqrt(V["arm_r"] ** 2 - dz ** 2), pz - dz)
        yc = w["hub"][1]
        bars = ch.arm_bars(w, s)
        ys = [q[1] for bar in bars for q in bar[:2]]
        out.append(dict(wheel=w["id"], part="tyre", hub=hub, r=V["tyre_d"] / 2, y=(yc - tyre_w / 2, yc + tyre_w / 2)))
        out.append(dict(wheel=w["id"], part="arm", hub=hub, pivot=(px, pz), r=V["arm_depth"] / 2, y=(min(ys), max(ys)), bars=bars))
    return out


def _pt_box3(p, b) -> float:
    return math.sqrt(sum(max(b[i] - p[i], 0.0, p[i] - b[i + 3]) ** 2 for i in range(3)))


def _taper_gap(bar: tuple, dist, n: int = 40) -> float:
    """Least gap from a bar (a, c, r0, r1), its radius growing evenly from r0 at a to r1 at c, to a convex shape whose
    distance from a point is `dist`, by a ternary search along the bar (the distance less a linear radius is convex)."""
    a, c, r0, r1 = bar
    f = lambda t: dist(tuple(a[i] + (c[i] - a[i]) * t for i in range(3))) - (r0 + (r1 - r0) * t)  # noqa: E731
    lo, hi = 0.0, 1.0
    for _ in range(n):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if f(m1) < f(m2):
            hi = m2
        else:
            lo = m1
    return min(f(lo), f(0.0), f(1.0))


def _taper_pt(bar: tuple, q) -> float:
    """The gap from the bar (a, c, r0, r1) to the point q, at the point of its axis nearest q."""
    a, c, r0, r1 = bar
    d = [c[i] - a[i] for i in range(3)]
    dd = sum(v * v for v in d)
    t = 0.0 if dd < 1e-12 else max(0.0, min(1.0, sum((q[i] - a[i]) * d[i] for i in range(3)) / dd))
    return math.dist(q, tuple(a[i] + d[i] * t for i in range(3))) - (r0 + (r1 - r0) * t)


def _part_bbox(p: dict) -> tuple:
    (hx, hz), r = p["hub"], p["r"]
    if p["part"] == "tyre":
        return (hx - r, p["y"][0], hz - r, hx + r, p["y"][1], hz + r)
    pts = [q for bar in p["bars"] for q in bar[:2]]
    return tuple(min(q[i] for q in pts) - r for i in range(3)) + tuple(max(q[i] for q in pts) + r for i in range(3))


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
                if p["part"] == "tyre":
                    g = _beside(_pt_rect(hub, (b[0], b[2], b[3], b[5])) - r, _span_gap(y0, y1, b[1], b[4]))
                else:
                    g = min(_taper_gap(bar, lambda q, b=b: _pt_box3(q, b)) for bar in p["bars"])
                if g < least.get(name, math.inf):
                    least[name] = g
                if g < best.get(p["part"], {}).get("gap_mm", math.inf):
                    best[p["part"]] = dict(gap_mm=g, part=p["part"], wheel=p["wheel"], travel_mm=s, what=name, hub=hub)
            for name, q, rq in npts:
                if p["part"] == "tyre":
                    g = _beside(math.dist(hub, (q[0], q[2])) - r, _span_gap(y0, y1, q[1], q[1])) - rq
                else:
                    g = min(_taper_pt(bar, q) for bar in p["bars"]) - rq
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
    if spec.get("poses") == "hinge_fillers":                  # each filler under its crossmember's front half (I2-118)
        return [c["box"] for c in ch.hinge_fillers()]
    if spec.get("poses") == "shock_plates":                   # flush on their crossmembers' front faces
        return [p["box"] for p in ch.shock_plates()]
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

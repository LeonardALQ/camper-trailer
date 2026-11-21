"""Body design to planning level (BODY.md): sandwich panel, insert, joint, mount, end wall, roof joint and twist
checks for the body in the trailer layout (cad/trailer.py), from data/body/body.yaml and research report 12.

Revision B (20 Nov 2026) is the body for the LandCruiser 79: 4,420 mm long with a fixed roof bonded to the walls, a
full rear wall and no garage. The bike wheel, chock, L-track and generator loads left the body with the garage, so a
person's foot governs the floor. The rear wall replaces the garage portal as the box's rear diaphragm.
"""
from __future__ import annotations

import math
from functools import cached_property

import numpy as np
import yaml

from .partsdb import DATA

BODY_YAML = DATA / "body" / "body.yaml"
G = 9.81
MOUNTED = ("body", "roof", "bed", "living", "payload", "electrical", "hvac", "wet_room")   # systems on the body (the drawbar box is on the drawbar)


def load_data() -> dict:
    return yaml.safe_load(BODY_YAML.read_text())


def side_projections(lay) -> list[dict]:
    """What stands proud of the side walls' outer skins, as Y extents in DIM-01, for the overall width (DIM-01, DIM-05):
    each side-wall opening's `proj` (data/body/body.yaml), each side-wall gland's (data/services.yaml) and the joiners
    along both edges. The side marker lamps and reflectors are left out, as ADR 43/04's definition and VSB1 5.2 leave out
    lamps and reflectors."""
    d, V = load_data(), lay.V
    hb = V["half_bw"]
    glands = yaml.safe_load((DATA / "services.yaml").read_text())["glands"]
    out = [dict(name="floor and roof-to-wall joiners", wall=s, proj=d["width"]["joiner_proj"]) for s in ("kerb", "road")]
    out += [dict(name=o["name"], wall=o["wall"], proj=o["proj"], id=o["id"]) for o in d["openings"] if o.get("proj")]
    out += [dict(name=g["what"], wall=g["at"], proj=g["proj"], id=g["id"]) for g in glands if g.get("proj")]
    for p in out:
        s = 1 if p["wall"] == "road" else -1
        p["y0"], p["y1"] = sorted((s * hb, s * (hb + p["proj"])))
    return out


def _wall_section(th: dict, t_out: float, core: float, t_in: float, member: dict | None) -> dict:
    """Steady conduction in a half strip of the side wall, `th["strip_mm"]` wide, at one member on the inner skin (or
    none), per metre of member length. Cells of `th["cell_mm"]`: x along the wall from the member's centreline, y through
    the wall from the outer face. The outer and inner faces lose heat through Rse and Rsi, the centreline is a symmetry
    plane and the strip's far edge is adiabatic. Returns the coldest inside surface, the member's coldest cell and the
    heat through the strip, W per metre of member."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    h, kk = th["cell_mm"], th["k"]
    depth = t_out + core + t_in
    nx, ny = round(th["strip_mm"] / h), round(depth / h)
    y = (np.arange(ny) + 0.5) * h
    x = (np.arange(nx) + 0.5) * h
    Y, X = np.meshgrid(y, x, indexing="ij")
    k = np.full((ny, nx), kk["xps"])
    k[Y < t_out] = kk["grp"]
    k[Y > depth - t_in] = kk["grp"]
    al = np.zeros((ny, nx), dtype=bool)
    if member:
        y1 = depth - t_in
        y0 = y1 - member["depth"]
        half, t = member["width"] / 2, member["wall"]
        al = (X < half) & (Y > y0) & (Y < y1)
        k[al] = kk["aluminium"]
        k[(X < half - t) & (Y > y0 + t) & (Y < y1 - t)] = kk["air"]
        al &= k == kk["aluminium"]
    idx = np.arange(nx * ny).reshape(ny, nx)
    hm = h / 1000.0
    rows, cols, vals = [], [], []
    diag = np.zeros(nx * ny)
    for a, b in ((k[:, :-1], k[:, 1:]), (k[:-1, :], k[1:, :])):
        g = (2 * a * b / (a + b)).ravel()                         # W/K per metre of member between neighbouring cells
        i, j = ((idx[:, :-1], idx[:, 1:]) if a.shape[1] == nx - 1 else (idx[:-1, :], idx[1:, :]))
        i, j = i.ravel(), j.ravel()
        rows += [i, j]
        cols += [j, i]
        vals += [-g, -g]
        np.add.at(diag, i, g)
        np.add.at(diag, j, g)
    g_out = hm / (th["rse"] + hm / 2 / k[0, :])                   # outer face, per column
    g_in = hm / (th["rsi"] + hm / 2 / k[-1, :])                   # inner face, per column
    rhs = np.zeros(nx * ny)
    np.add.at(diag, idx[0, :], g_out)
    np.add.at(diag, idx[-1, :], g_in)
    rhs[idx[0, :]] += g_out * th["t_out"]
    rhs[idx[-1, :]] += g_in * th["t_in"]
    A = sp.csr_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(nx * ny)]),
                                                        np.concatenate(cols + [np.arange(nx * ny)]))), shape=(nx * ny, nx * ny))
    T = spsolve(A.tocsc(), rhs).reshape(ny, nx)
    q_in = g_in * (th["t_in"] - T[-1, :])                         # W per metre of member through each column's inner face
    tsi = th["t_in"] - q_in / hm * th["rsi"]
    return dict(tsi_min=float(tsi.min()), t_member=float(T[al].min()) if al.any() else None, q_w_m=float(q_in.sum()))


def _w_sat(t: float) -> float:
    """Saturation humidity ratio, g/kg, at t C and 101.3 kPa (Magnus, as research report 19's model)."""
    p = 0.61094 * math.exp(17.625 * t / (t + 243.04))
    return 622 * p / (101.325 - p)


def _dew(w: float) -> float:
    """Dew point, C, of air holding w g/kg."""
    lo, hi = -40.0, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _w_sat(mid) < w else (lo, mid)
    return lo


class Panel:
    def __init__(self, key: str, d: dict):
        self.key, self.d = key, d
        self.name = d["name"]
        self.t1, self.t2 = d["skins"]
        self.c = d["core"]["c"]
        self.dd = self.c + (self.t1 + self.t2) / 2          # skin centre spacing
        self.E, self.G, self.ult = d["E"], d["G"], d["ult"]
        self.core = d["core"]
        st = d.get("stiffener")
        self.D_stiff = st["E"] * st["I"] / st["pitch"] if st else 0.0   # stiffeners smeared over their pitch, N mm2/mm

    @property
    def D(self) -> float:
        """Bending stiffness per mm width, N mm2/mm."""
        return self.E * self.t1 * self.t2 * self.dd ** 2 / (self.t1 + self.t2)

    @property
    def S(self) -> float:
        """Shear stiffness per mm width, N/mm."""
        return self.core["Gc"] * self.dd ** 2 / self.c

    @property
    def wrinkling(self) -> float:
        Ec = 2.5 * self.core["Gc"]                           # foam core, Ec about 2.5 Gc (assumption)
        return 0.5 * (self.E * Ec * self.core["Gc"]) ** (1 / 3)

    @property
    def Gt(self) -> float:
        """In-plane shear stiffness of the two skins, N/mm."""
        return self.G * (self.t1 + self.t2)

    def plate_gj(self, b: float) -> float:
        """Torsion constant times G of a strip of width b twisting on its own, N mm2 (open section)."""
        return b * self.G * min(self.t1, self.t2) * 2 * self.dd ** 2 / 2

    def one_way(self, P: float, patch_w: float, span: float, a: float | None = None) -> dict:
        """Point load P (N) on a one-way span between supports, `a` from the nearer support (midspan if None).
        Effective width = patch width + span / 2."""
        a = span / 2 if a is None else a
        b = patch_w + span / 2
        M = P * a * (span - a) / span
        V = P * max(a, span - a) / span
        sig = M / (min(self.t1, self.t2) * self.dd * b)
        tau = V / (self.dd * b)
        defl = P * a ** 2 * (span - a) ** 2 / (3 * self.D * b * span) + P * a * (span - a) / (self.S * b * span)
        return dict(M=M, V=V, b_eff=b, skin_mpa=sig, core_mpa=tau, defl_mm=defl)

    def uniform(self, w_mpa: float, span: float) -> dict:
        """Uniform pressure w (N/mm2) on a one-way strip, simply supported. The deflection counts the panel's own
        stiffeners, smeared over their pitch. The skin stress leaves them out."""
        M = w_mpa * span ** 2 / 8
        V = w_mpa * span / 2
        return dict(skin_mpa=M / (min(self.t1, self.t2) * self.dd), core_mpa=V / self.dd,
                    defl_mm=5 * w_mpa * span ** 4 / (384 * (self.D + self.D_stiff)) + w_mpa * span ** 2 / (8 * self.S))

    def utils(self, r: dict, crit: dict, compression: bool = True) -> dict:
        """Utilisations against report 12's criteria: skin at half its ultimate (and half the wrinkling stress when
        in compression), core shear at half its strength."""
        us = r["skin_mpa"] / (crit["skin_factor"] * self.ult)
        if compression:
            us = max(us, r["skin_mpa"] / (crit["wrinkling_factor"] * self.wrinkling))
        uc = r["core_mpa"] / (crit["core_factor"] * self.core["shear"])
        return dict(skin=us, core=uc, util=max(us, uc), governing="skin" if us >= uc else "core shear")


class Body:
    """The body checks for one layout of the trailer (cad/trailer.py)."""

    def __init__(self, lay, tr):
        self.lay, self.tr = lay, tr
        self.d = load_data()
        self.V = lay.V
        self.p = {k: Panel(k, v) for k, v in self.d["panels"].items()}
        self.crit = self.d["criteria"]
        V = self.V
        self.raiser_gap = 2 * (V["rail_c"] - V["rail_w"] / 2)        # between the raisers' inner faces
        self.raiser_span = 2 * V["rail_c"]                             # raiser centre to raiser centre
        self.edge_span = V["half_bw"] - V["wall_t"] / 2 - (V["rail_c"] + V["rail_w"] / 2)   # raiser face to the wall
        self.stations = sorted(lay.chassis.station_x(s) for s in lay.chassis.stations)

    # ------------------------------------------------------------------ what stands on the floor
    @cached_property
    def mounted(self) -> dict:
        """Mass on the body mounts per trailer case, scaled as the chassis analysis scales (heaviest case at the ATM)."""
        rows = {}
        for c in self.tr.cases:
            lines = [(b, m) for b, m in self.lay.case_lines(c) if b.system in MOUNTED and m > 0 and b.cog]
            m = sum(mm for _, mm in lines)
            z = sum(mm * b.cog[2] for b, mm in lines) / m
            tot = sum(mm for _, mm in self.lay.case_lines(c))
            rows[c.id] = dict(kg=m, cog_z=z, total_kg=tot)
        k = max(1.0, self.tr.caps()["plated"] / max(r["total_kg"] for r in rows.values()))
        worst = max(rows, key=lambda c: rows[c]["kg"])
        return dict(cases=rows, scale=k, worst=worst, kg=rows[worst]["kg"] * k, cog_z=rows[worst]["cog_z"])

    # ------------------------------------------------------------------ panels (report 12 section 3)
    def panel_checks(self) -> list[dict]:
        L, cr, f, w, rf = self.d["loads"], self.crit, self.p["floor"], self.p["wall"], self.p["roof"]
        V = self.V
        out = []

        def row(cid, what, panel, r, case, compression=True, extra=""):
            u = panel.utils(r, cr, compression)
            out.append(dict(id=cid, what=what, case=case, skin_mpa=r["skin_mpa"], core_mpa=r["core_mpa"],
                            util=u["util"], governing=u["governing"], extra=extra, defl_mm=r.get("defl_mm")))

        span = self.raiser_span
        ft = L["foot"]
        r = f.one_way(3 * ft["kg"] * G, min(ft["patch"]), span)
        bearing = 3 * ft["kg"] * G / (ft["patch"][0] * ft["patch"][1])
        r["core_mpa"] = max(r["core_mpa"], bearing * cr["core_factor"] / cr["bearing_factor"] *
                            f.core["shear"] / f.core["compression"])
        row("BDY-03", "Floor under a foot midway between the raisers, with bearing on the core", f, r, "LC2, 3 g",
            extra=f"bearing {bearing:.2f} MPa against {cr['bearing_factor'] * f.core['compression']:.2f} MPa")
        pitch = max(b - a for a, b in zip(self.stations, self.stations[1:]))
        r = f.uniform(3 * L["floor_edge_kg_m2"] * G / 1e6, pitch)
        row("BDY-04", f"Floor edge beside the raisers between outriggers {pitch:.0f} mm apart", f, r, "LC2, 3 g")
        # side wall in the ultimate wind, spanning from the floor to the roof-to-wall joiner. The skins are checked without
        # the stiffeners, and each stiffener for the share of the load its stiffness draws
        wu, ws = self.wind()
        r = w.uniform(wu["kpa"] / 1000, V["interior_h"])
        st = w.d["stiffener"]
        share = w.D_stiff / (w.D + w.D_stiff)
        m_st = share * wu["kpa"] / 1000 * st["pitch"] * V["interior_h"] ** 2 / 8
        s_st = m_st * st["depth"] / 2 / st["I"]
        u_st = s_st / (st["fy"] / cr["metal_factor"])
        # the member's share reaches it from the outer skin through the XPS behind it, in compression or, in suction, tension
        s_xps = share * wu["kpa"] / 1000 * st["pitch"] / st["width"]
        v250 = self.d["wind"]["V_250"] * self.d["wind"]["Mzcat"]
        f250 = (v250 / wu["V"]) ** 2
        a_xps = cr["core_factor"] * w.core["compression"]
        row("BDY-06", f"Side wall in the ultimate wind, {wu['kpa']:.2f} kPa net at {wu['V']:.0f} m/s, floor to the roof joiner ({V['interior_h']:.0f} mm)",
            w, r, "Wind, ultimate", extra=(f"the member takes {100 * share:.0f} % of its bay's load, {s_st:.0f} MPa against {st['fy'] / cr['metal_factor']:.0f} MPa, "
                                          f"utilisation {u_st:.2f}. The {st['break']:g} mm of XPS behind it carries {s_xps:.3f} MPa against "
                                          f"{a_xps:.2f} MPa. Strapped down (STB-05), at region B's 250-year gust at 3 m, {self.d['wind']['V_250']:g} m/s "
                                          f"times {self.d['wind']['Mzcat']:g}, {v250:.1f} m/s, the member works at {u_st * f250:.2f} and the skins at "
                                          f"{w.utils(r, cr)['util'] * f250:.2f}"))
        if max(u_st, s_xps / a_xps) > out[-1]["util"]:
            out[-1].update(util=max(u_st, s_xps / a_xps), governing="member" if u_st >= s_xps / a_xps else "XPS behind the member")
        # the fixed roof with the bonded solar array and its own weight, spanning between the walls
        sol = sum(b.mass_kg for b in self.lay.blocks if b.system == "roof")
        q = 3 * (rf.d["kg_m2"] + sol / (V["body_length"] * V["body_width"] / 1e6)) * G / 1e6
        r = rf.uniform(q, V["body_width"] - V["wall_t"])
        row("BDY-07", f"Fixed roof with the {sol:.0f} kg solar array, spanning between the walls", rf, r, "LC2, 3 g")
        self.roof_defl = rf.uniform(q / 3, V["body_width"] - V["wall_t"])["defl_mm"]
        self.floor_defl = f.one_way(ft["kg"] * G, min(ft["patch"]), span)["defl_mm"]
        self.wall_defl = w.uniform(ws["kpa"] / 1000, V["interior_h"])["defl_mm"]
        self.wall_defl_bare = Panel("wall", {**w.d, "stiffener": None}).uniform(ws["kpa"] / 1000, V["interior_h"])["defl_mm"]
        return out

    def wind(self) -> tuple[dict, dict]:
        """The ultimate and serviceability net pressures on a side wall, kPa (data/body/body.yaml `wind`, AS/NZS 1170.2)."""
        wd = self.d["wind"]
        c = wd["cpe"] - wd["cpi"]
        vs = wd["V_s"] * wd["Mzcat"]
        return (dict(V=wd["V_u"], kpa=0.6 * wd["V_u"] ** 2 * c / 1000), dict(V=vs, kpa=0.6 * vs ** 2 * c / 1000))

    def deflections(self) -> list[dict]:
        cr, V = self.crit, self.V
        self.panel_checks() if not hasattr(self, "roof_defl") else None
        return [dict(id="DEF-B1", what="Floor under a foot at 1 g", mm=self.floor_defl, limit_mm=self.raiser_span / cr["floor_span_ratio"]),
                dict(id="DEF-B2", what="Fixed roof with the solar array at 1 g", mm=self.roof_defl, limit_mm=(V["body_width"] - V["wall_t"]) / cr["roof_span_ratio"]),
                dict(id="DEF-B3", what=(f"Side wall in region {self.d['wind']['region']}'s 25-year wind, {self.wind()[1]['kpa']:.2f} kPa net at "
                                        f"{self.wind()[1]['V']:.1f} m/s, with its members on the inner skin ({self.wall_defl_bare:.1f} mm without them)"),
                     mm=self.wall_defl, limit_mm=V["interior_h"] / cr["wall_span_ratio"])]

    # ------------------------------------------------------------------ inserts and the roof joint
    def roof(self) -> dict:
        """The fixed roof bonded into the roof-to-wall joiner, in report 12's 40 m/s uplift (roof down at 110 km/h into a
        36 km/h headwind), against the bond's tensile strength over the joiner leg, with half of it allowed."""
        V, tw, L = self.V, self.d["twist"], self.d["loads"]
        perim = 2 * (V["body_length"] + V["body_width"])
        roof_kg = V["body_length"] * V["body_width"] / 1e6 * self.p["roof"].d["kg_m2"] + sum(b.mass_kg for b in self.lay.blocks if b.system == "roof")
        net = max(0.0, L["uplift_40ms_n"] - roof_kg * G)
        q = L["uplift_40ms_n"] / perim
        allow = 0.5 * tw["bond_tension_strength"] * tw["bond_width"]
        return dict(uplift_n=L["uplift_40ms_n"], roof_kg=roof_kg, net_n=net, perimeter_mm=perim, q_n_mm=q, allow_n_mm=allow, util=q / allow)

    def inserts(self) -> list[dict]:
        """Working loads on the panel fixings against half their rated load (report 12 section 3, MAT-05)."""
        L, cr = self.d["loads"], self.crit
        screws = L["bed_rails"] * L["rail_screws"]
        f_night = L["bed_night_factor"] * L["bed_kg"] * G / screws    # the bed down with two sleepers moving on it
        f_travel = 3 * L["bed_travel_kg"] * G / screws               # LC2, 3 g on the moving bed at its day stop
        f_rail = max(f_night, f_travel)
        st = self.p["wall"].d["stiffener"]
        aw = self.awning()
        rows = [dict(id="INS-01", what=(f"Lift-bed rail screw, 1/4 in self-tapping through the inner skin into the {st['name'].split(' 6060')[0]} "
                                        f"hardpoint's {st['wall']:g} mm wall, shear"), n=f_rail, rated_n=L["rail_screw_rated_n"],
                     case=(f"{L['bed_night_factor']:g} x the {L['bed_kg']:.0f} kg bed at night" if f_night >= f_travel else
                           f"LC2, 3 g on the {L['bed_travel_kg']:.0f} kg moving bed") + f", over {screws} screws"),
                dict(id="INS-02", what=f"Awning bracket bolt, {aw['bolt']} through the roof's kerb-edge insert strip, tension in travel",
                     n=aw["travel_n"], rated_n=aw["rated_tension_n"],
                     case=(f"LC2, 3 g on the {aw['kg']:.1f} kg awning taken as a pull, a bracket's share on its inner bolt with prying "
                           f"{aw['cog_lever_mm']:.0f} over {aw['bolt_pitch_mm']:.0f} mm")),
                dict(id="INS-03", what=f"Awning bracket bolt, {aw['bolt']}, tension with the canopy open in a {aw['check_kmh']:.0f} km/h gust, a check of the fixing only",
                     n=aw["open_n"], rated_n=aw["rated_tension_n"],
                     case=(f"{aw['q_pa']:.0f} Pa, Cp,n {aw['cpn']:g} on the {aw['canopy_m2']:g} m2 canopy, half of it at the case "
                           f"({aw['case_n'] / 1000:.2f} kN), the legs pegged, a bracket's share on its inner bolt with prying "
                           f"{aw['canopy_lever_mm']:.0f} over {aw['bolt_pitch_mm']:.0f} mm"))]
        for r in rows:
            r["util"] = r["n"] / (cr["insert_factor"] * r["rated_n"])
        return rows

    def awning(self) -> dict:
        """The Fiamma F80s on the roof's kerb edge (data/body/body.yaml `awning`): its bracket bolts in travel (INS-02) and
        with the canopy open in wind (INS-03), and where its legs put the lead bar (BDY-23)."""
        a, V = self.d["awning"], self.V
        b = self.lay.find(a["line"])
        m = b.mass_kg
        nb = a["brackets"]
        travel = 3 * m * G / nb * max(1.0, a["cog_lever_mm"] / a["bolt_pitch_mm"])
        v = a["check_kmh"] / 3.6
        q = 0.6 * v ** 2
        case_n = 0.5 * q * a["cpn"] * a["canopy_m2"]
        open_n = case_n / nb * max(1.0, a["canopy_lever_mm"] / a["bolt_pitch_mm"])
        z_case = b.box[2] + a["canopy_drop_mm"]                 # where the canopy leaves the case
        z_bar_max = a["leg_max_mm"] + a["leg_head_mm"]          # the lead bar on fully extended legs, level ground
        pitch_full = math.degrees(math.asin(max(0.0, z_case - z_bar_max) / a["extension_mm"]))
        z_bar = z_case - a["extension_mm"] * math.sin(math.radians(a["pitch_deg"]))
        leg = z_bar - a["leg_head_mm"]
        return dict(a, kg=m, travel_n=travel, q_pa=q, case_n=case_n, open_n=open_n, z_case=z_case, z_bar_max=z_bar_max,
                    pitch_full_deg=pitch_full, z_bar=z_bar, leg_mm=leg, reach_mm=a["leg_max_mm"] - leg)

    def cold_bridge(self) -> dict:
        """BDY-22: steady two-dimensional conduction through the side wall at one of its members on the inner skin, on the
        design cold night (data/body/body.yaml `thermal`). Half the strip, from the member's centreline (symmetry) to
        `strip_mm` (adiabatic), on a square grid. Returns the coldest inside surface over the member, the member's own
        temperature (the HappiJac rails screwed to it run at about the same), the plain wall's surface and the extra heat
        loss per metre of member, both ways from its centreline."""
        th, wl = self.d["thermal"], self.p["wall"]
        st = wl.d["stiffener"]
        with_member = _wall_section(th, wl.t1, wl.c, wl.t2, st)
        plain = _wall_section(th, wl.t1, wl.c, wl.t2, None)
        dT = th["t_in"] - th["t_out"]
        heat = dict(th, rsi=th["rsi_heat"])                     # the heat loss figure on ISO 6946's film
        psi = 2 * (_wall_section(heat, wl.t1, wl.c, wl.t2, st)["q_w_m"] - _wall_section(heat, wl.t1, wl.c, wl.t2, None)["q_w_m"]) / dT
        # along the member (F3-05): a fin between the inside and outside air, each end 10 mm from a joiner taken at the
        # outside air (a bound), through a rigid PVC pad at the foot and XPS at the head. One-dimensional conductances over
        # the member's width leave out its side paths, which makes the fin longer and its ends colder
        k = th["k"]
        w, d, t, brk = st["width"], st["depth"], st["wall"], st["break"]
        kA = k["aluminium"] * (w * d - (w - 2 * t) * (d - 2 * t)) * 1e-6
        g_in = w / 1000 / (th["rsi"] + wl.t2 / 1000 / k["grp"])
        g_out = w / 1000 / (brk / 1000 / k["xps"] + wl.t1 / 1000 / k["grp"] + th["rse"])
        m = math.sqrt((g_in + g_out) / kA)
        gap, pad = st["end_gap_mm"] / 1000, st["foot_pad_mm"]
        tm = with_member["t_member"]
        ends = {}
        for name, g in (("foot", (k["pvc"] * pad + k["xps"] * (w - pad)) * d * 1e-6 / gap), ("head", k["xps"] * w * d * 1e-6 / gap)):
            drop = g * (tm - th["t_out"]) / (kA * m + g)
            ends[name] = dict(drop_k=drop, tsi=with_member["tsi_min"] - drop, g_w_k=g)
        # the dew point on the generators: e2 fans A and B and the RESPA-CF2 (report 19's moisture model)
        gm = th["generator_mode"]
        q = gm["e2_m3h"] + gm["respa_m3h"]
        eps = gm["eps_lat"] * gm["e2_m3h"] / q
        dew_gen = _dew(gm["w_out_factor"] * _w_sat(th["t_out"]) + gm["moisture_g_h"] / (1.2 * q * (1 - eps)))
        length_m = sum(b.mass_kg for b in self.lay.blocks if b.id in th["members"]) / st["kg_m"]
        need = th["dew_point"] + th["margin_k"]
        tsi = min(with_member["tsi_min"], ends["foot"]["tsi"], ends["head"]["tsi"])
        return dict(tsi_min=tsi, tsi_mid=with_member["tsi_min"], t_member=tm, tsi_plain=plain["tsi_min"], need=need, ends=ends,
                    fin_mm=1000 / m, gap_mm=st["end_gap_mm"], pad_mm=pad, rsi=th["rsi"], dew_gen=dew_gen,
                    need_gen=dew_gen + th["margin_k"], gen_m3h=q, psi=psi, length_m=length_m, w_k=psi * length_m,
                    members=th["members"], member=st["name"], brk=brk, t_out=th["t_out"], t_in=th["t_in"], dew=th["dew_point"],
                    bare=th["bare_panels_w_k"], bridges=th["bridges_w_k"])

    def members_clear(self) -> dict:
        """FIT-07 (F3-02): each wall member against the cut-outs, insert strips and glands on its side wall, and the bays
        the members, the kitchen tower's sides, the partition and the end walls leave (data/body/body.yaml `members_rule`).
        The lift bed's hardpoints stand behind its rails."""
        V, lay, ru = self.V, self.lay, self.d["members_rule"]
        st = self.p["wall"].d["stiffener"]
        x0, half = V["body_x0"], st["width"] / 2
        side = lambda y: "road" if y > 0 else "kerb"  # noqa: E731
        mem = [(b.iid, side(b.cog[1]), b.cog[0]) for b in lay.blocks if b.id in ("BD-18", "BD-19")]
        mem += [(f"LB-06 at {b.iid}", side(b.cog[1]), b.cog[0]) for b in lay.blocks if b.id == ru["hardpoints_at"]]
        obs = []
        for o in self.openings():
            if o["wall"] not in ("kerb", "road"):
                continue
            strip = ru["strip_mm"] if any(o.get("line", "").startswith(p) for p in ru["strip_lines"]) and o["id"] not in ru["no_side_strips"] else 0
            what = f"{o['id']} ({o['name'].split(',')[0]})" + (f" with its {strip:g} mm insert strip" if strip else "")
            obs.append((o["wall"], x0 + o["u0"] - strip, x0 + o["u1"] + strip, what))
        for g in yaml.safe_load((DATA / "services.yaml").read_text())["glands"]:
            if g["at"] in ("kerb", "road"):
                gw = g.get("w", g["d"])
                obs.append((g["at"], g["x"] - gw / 2, g["x"] + gw / 2, f"gland {g['id']}"))
        strips = []
        for sp in ru.get("strips", []):            # a horizontal fixing strip stops clear_mm short of each member it meets
            bb = lay.find(sp["block"]).box
            wall = side((bb[1] + bb[4]) / 2)
            pieces = [(bb[0], bb[3])]
            for _, w2, x in mem:
                if w2 != wall:
                    continue
                lo, hi = x - half - ru["clear_mm"], x + half + ru["clear_mm"]
                pieces = [q for a, c in pieces for q in (((a, c),) if hi <= a or lo >= c else tuple(
                    p for p in ((a, lo), (hi, c)) if p[1] - p[0] > 1e-6))]
            strips += [(wall, a, c, sp["name"]) for a, c in pieces]
        obs += strips
        rows = []
        for iid, wall, x in mem:
            gaps = [(max(o0 - (x + half), (x - half) - o1), what) for w2, o0, o1, what in obs if w2 == wall]
            g, what = min(gaps)
            rows.append(dict(member=iid, wall=wall, x=x, gap_mm=g, to=what))
        bays = {}
        for wall in ("kerb", "road"):
            xs = [x0 + V["end_wall_t"], V["body_x1"] - V["end_wall_t"]] + [x for _, w2, x in mem if w2 == wall]
            for bid in ru["bounds"]:
                bb = lay.find(bid).box
                if (wall == "road" and bb[4] >= V["half_bw"] - V["wall_t"] - 60) or (wall == "kerb" and bb[1] <= -V["half_bw"] + V["wall_t"] + 60):
                    xs += [bb[0], bb[3]]
            xs = sorted(xs)
            bays[wall] = max(b - a for a, b in zip(xs, xs[1:]))
        worst = min(r["gap_mm"] for r in rows)
        probs = [f"{r['member']} on the {r['wall']} side is {r['gap_mm']:.0f} mm from {r['to']}" for r in rows if r["gap_mm"] < ru["clear_mm"] - 1e-6]
        probs += [f"a {w2} side bay is {v:.0f} mm wide" for w2, v in bays.items() if v > st["pitch"] + 1e-6]
        return dict(ok=not probs, problems=probs, rows=rows, worst_mm=worst, bays=bays, pitch=st["pitch"], clear_mm=ru["clear_mm"],
                    width=st["width"], strips=strips)

    def cradle(self) -> dict:
        """The split's outdoor unit and its cradle on the rear wall (BDY-21): the stays carry the vertical load to the
        chassis, and the wall's bolts the overturning moment, the pull away from the wall and the sideways load, against
        half their rated loads. The pull-through rating uses the body mounts' spreader rule on the bolt's pad."""
        cd, cr, V = self.d["cradle"], self.crit, self.V
        sp = self.d["mounts"]["fallback"]["spreader"]
        lines = [self.lay.find(i) for i in cd["lines"]]
        m = sum(b.mass_kg for b in lines)
        d = sum(b.mass_kg * b.cog[0] for b in lines) / m - V["body_x1"]      # centre of gravity behind the rear wall
        a, n, W = cd["accel"], cd["bolts"], m * G
        wl = self.p["wall"]
        pull_rated = 4 * cd["pad_side_mm"] * (wl.t1 * sp["skin_shear"] + wl.c * sp["insert_shear"]) / 2
        t_moment = a["down_g"] * W * d / cd["row_lever_mm"] / 2                # the top row's two bolts hold the overturning moment
        t_pull = a["along_g"] * W / n                                           # the unit pulled away from the wall
        t_side = a["side_g"] * W * d / cd["column_spacing_mm"] / 2              # the sideways load's twist on the bolt columns
        tension = t_moment + t_pull + t_side
        shear = a["side_g"] * W / n
        st = cd["stays"]
        stay_n = a["down_g"] * W / st["n"]
        p_cr = math.pi ** 2 * st["E"] * st["I_min"] / st["L"] ** 2
        u = dict(bolt_tension=tension / (cr["insert_factor"] * pull_rated), bolt_shear=shear / (cr["insert_factor"] * cd["shear_rated_n"]),
                 stay_buckling=stay_n / (p_cr / st["buckling_factor"]), stay_yield=stay_n / (st["A"] * st["fy"] / cr["metal_factor"]))
        gov = max(u, key=u.get)
        return dict(mass_kg=m, offset_mm=d, tension_n=tension, shear_n=shear, pull_rated_n=pull_rated, shear_rated_n=cd["shear_rated_n"],
                    stay_n=stay_n, stay_pcr_n=p_cr, stays=st, utils=u, governing=gov.replace("_", " "), util=u[gov])

    # ------------------------------------------------------------------ the body as a torsion box (report 12 section 4)
    def box_gj(self, lid_structural: bool) -> dict:
        """GJ of the body box, N mm2. With the roof bonded into its joiner the body is one closed cell of the floor, the walls
        and the roof (`lid_structural`, the upper bound). The lower bound neglects the roof joint: an open U of the floor
        and the walls, as report 12 took for the latched lid."""
        V, p, tw = self.V, self.p, self.d["twist"]
        b = V["body_width"] - V["wall_t"]
        zf = V["floor_z"] - p["floor"].d["t"] / 2
        h = V["ceiling_z"] + p["roof"].d["t"] / 2 - zf
        walls, floor = p["wall"].Gt, p["floor"].Gt
        A = b * h
        gj_c = 4 * A ** 2 / (2 * h / walls + b / floor + b / (p["roof"].Gt * tw["roof_joint_factor"]))
        gj_o = p["floor"].plate_gj(b) + 2 * p["wall"].plate_gj(h)
        return dict(body=gj_c if lid_structural else gj_o, closed=gj_c, open=gj_o, A=A, h=h, b=b)

    def segments(self, lid_structural: bool) -> list[tuple[float, float, float]]:
        """(x0, x1, GJ) per bay between stations: the body box is the same cell all along."""
        gj = self.box_gj(lid_structural)["body"]
        return [(x0, x1, gj) for x0, x1 in zip(self.stations, self.stations[1:])]

    def _run(self, an, items, acc, **kw) -> dict:
        res, _ = an.run_static(items, acc, **kw)
        signed = [-res.forces[k][3] for k, _, _ in an.fm.body_elements]
        tor = [(x0, x1, abs(t)) for (k, x0, x1), t in zip(an.fm.body_elements, signed)]
        xs = [x0 for _, x0, _ in an.fm.body_elements] + [an.fm.body_elements[-1][2]]
        per_station = {round(x): abs((signed[i - 1] if i > 0 else 0.0) - (signed[i] if i < len(signed) else 0.0)) / 1e6
                       for i, x in enumerate(xs)}
        posts = [(x, sd, -res.forces[k][0], where) for k, x, sd, where in an.fm.mount_posts]   # + tension: the bolt is pulled
        gm = max(an.stresses(res).items(), key=lambda kv: kv[1]["eq"])
        worst = max(posts, key=lambda p: abs(p[2]))
        return dict(chassis_deg=an.twist(res), max_body_torque_knm=max(t for *_, t in tor) / 1e6,
                    station_torque_knm=per_station, segments=[dict(x0=x0, x1=x1, torque_knm=t / 1e6) for x0, x1, t in tor],
                    mount_force_n=abs(worst[2]), mount_worst=[worst[0], worst[1], worst[3]], mount_pulled=worst[2] > 0,
                    chassis_mpa=gm[1]["eq"], chassis_member=gm[0])

    def twist(self) -> dict:
        """LC5a (one wheel in a hole, travelling) and LC5b (one corner steady wound to 875 kg at tare, parked) with the
        body tied to the chassis at every station, for both bounds on the roof. LC5a takes the case and diagonal with the
        most chassis twist in the bare-frame analysis. The body's share is the part of the bare chassis twist it
        removes: 1 - (twist with the body) / (bare twist)."""
        from .chassis_fea import Analysis
        ch = self.lay.chassis
        bare = self.tr.chassis_results(self.lay)
        case_id, diag = bare["twist"]["case"].split(" (diagonal ")
        sgn = 1 if diag.startswith("A") else -1
        lcs = {l["id"]: l for l in ch.data["load_cases"]}
        lc, lb = lcs["LC5a"], lcs["LC5b"]
        hub_y = ch.suspension[0]["contact"][1]
        out = dict(case=bare["twist"]["case"], torque_knm=lc["torque_nmm"] / 1e6, bare_deg=bare["twist"]["deg"],
                   bare_lc5a_mpa=bare["governing"]["LC5a"]["eq"], bare_lc5b_mpa=bare["governing"]["LC5b"]["eq"])
        tc1 = next(c for c in self.tr.cases if c.id == "TC1")
        for key, lid in (("open", False), ("closed", True)):
            segs = self.segments(lid)
            an = Analysis(self.lay, self.tr, ch, body=segs)
            c, items, _, _ = next(t for t in an.scaled_cases([case_id]))
            a = self._run(an, items, lc["accel"][0], twist_n=sgn * lc["torque_nmm"] / (2 * abs(hub_y)))
            b = self._run(an, an.items(tc1), lb["accel"][0], steady_n=lb["steady_kg"] * G)
            a["share"] = 1 - a["chassis_deg"] / out["bare_deg"]
            a["torque_share"] = a["max_body_torque_knm"] / out["torque_knm"]
            a["chassis_util"] = a["chassis_mpa"] / (ch.fy / lc["factor"])
            b["chassis_util"] = b["chassis_mpa"] / (ch.fy / lb["factor"])
            a["gj"] = [dict(x0=x0, x1=x1, gj=gj) for x0, x1, gj in segs]
            out[key] = a
            out[key + "_lc5b"] = b
        # the body checks take the bound that loads the body most, per quantity
        both = [out["open"], out["closed"]]
        out["design"] = dict(max_body_torque_knm=max(r["max_body_torque_knm"] for r in both),
                             mount_force_n=max(r["mount_force_n"] for r in both),
                             mount_force_lc5b_n=max(out[k]["mount_force_n"] for k in ("open_lc5b", "closed_lc5b")))
        return out

    # ------------------------------------------------------------------ joints, portal and mounts under the body's share
    @cached_property
    def tw(self) -> dict:
        return self.twist()

    def joints(self) -> list[dict]:
        """Shear flow q = T / 2A from the body's share of LC5a in the skins and the bonded joints, with the larger body
        torque of the two bounds on the roof."""
        gj, cr, p = self.box_gj(True), self.crit, self.p
        T = self.tw["design"]["max_body_torque_knm"] * 1e6
        q = T / (2 * gj["A"])
        bond = self.d["twist"]["bond_shear_strength"] * self.d["twist"]["bond_width"]
        rows = []
        for key, what in (("wall", "Side wall skins in shear"), ("floor", "Floor skins in shear"), ("roof", "Roof skins in shear")):
            pn = p[key]
            tau = q / (pn.t1 + pn.t2)
            allow = cr["skin_factor"] * pn.ult / math.sqrt(3)
            rows.append(dict(id=f"JNT-{key}", what=what, value=tau, unit="MPa", limit=allow, util=tau / allow))
        rows.append(dict(id="JNT-bond", what="Bonded joiner leg, MS polymer, shear flow per mm", value=q, unit="N/mm",
                         limit=0.5 * bond, util=q / (0.5 * bond)))
        return rows

    def end_wall(self) -> dict:
        """The rear wall as the box's rear diaphragm (report 12 section 5). The torque the floor bolts put into the box at the
        stations in its rear half has to be held in shape at the rear wall, so the wall racks under F = T / 2h, h the
        cell height, for LC5a and LC5b and both bounds on the roof. The 2,330 mm panel less its openings at the worst
        height takes F in shear in its skins, and its bonded joiners take F along their length."""
        V, cr, tw = self.V, self.crit, self.d["twist"]
        gj = self.box_gj(True)
        x_mid = (V["body_x0"] + V["body_x1"]) / 2
        runs = {k: self.tw[k] for k in ("open", "closed", "open_lc5b", "closed_lc5b")}
        T_by = {k: sum(v for x, v in r["station_torque_knm"].items() if x >= x_mid) for k, r in runs.items()}
        gov = max(T_by, key=T_by.get)
        T = T_by[gov] * 1e6
        F = T / (2 * gj["h"])
        wl = self.p["wall"]
        rear = [o for o in self.openings() if o["wall"] == "rear"]
        cut = max((sum(o["w"] for o in rear if o["z0"] <= z <= o["z1"]) for z in {q["z0"] for q in rear} | {q["z1"] for q in rear}), default=0.0)
        w = 2 * V["half_in"] - cut
        tau = F / (w * (wl.t1 + wl.t2))
        allow = cr["skin_factor"] * wl.ult / math.sqrt(3)
        q = F / (2 * V["half_in"])
        bond = 0.5 * tw["bond_shear_strength"] * tw["bond_width"]
        util = max(tau / allow, q / bond)
        return dict(case=gov, torque_knm=T / 1e6, force_n=F, width_mm=w, tau_mpa=tau, allow_mpa=allow, q_n_mm=q, bond_n_mm=bond,
                    util=util, governing="skins in shear" if tau / allow >= q / bond else "bonded joiner")

    def face_capacity(self) -> float:
        """Yield-line capacity of the 3 mm raiser or outrigger top face under the Hollo-Bolt's flared sleeve (CIDECT
        design guide 3, transverse plate on an RHS face, with beta = eta = sleeve diameter / face width)."""
        m = self.d["mounts"]
        beta = m["collar"] / m["face_b"]
        return m["fy"] * m["face_t"] ** 2 / (1 - beta) * (2 * beta + 4 * math.sqrt(1 - beta))

    def mounts(self) -> dict:
        """Hollo-Bolt forces at the 36 mounts under LC2 to LC5a (report 12 section 4). One bolt into each raiser and
        each outrigger tip at every station. Shear shares equally. The LC4 overturning moment shares by the bolts' Y
        squared. The twist moment the body takes off the chassis at a station goes to that station's two raiser
        bolts as a couple, with no help from the outrigger tips (conservative). Weight relieves each bolt by its
        share of 1 g."""
        md, V = self.d["mounts"], self.V
        mt = self.mounted
        m, zc = mt["kg"], mt["cog_z"]
        n_st = len(self.stations)
        n = n_st * md["per_station"]
        ys = [V["rail_c"], md["outrigger_tip_y"]]
        sum_y2 = n_st * 2 * sum(y * y for y in ys)
        W1 = m * G / n                                     # 1 g share per bolt
        h = zc - V["floor_underside_z"]
        cases = {}
        cases["LC2"] = dict(shear=0.0, tension=0.0, note=f"3 g down: every bolt in compression, {3 * W1 / 1000:.2f} kN")
        cases["LC3"] = dict(shear=0.8 * m * G / n, tension=0.0, note="0.8 g braking shared by every bolt")
        M4 = 0.5 * m * G * h
        t4 = M4 * md["outrigger_tip_y"] / sum_y2 - W1
        cases["LC4"] = dict(shear=0.5 * m * G / n, tension=max(0.0, t4), note=f"0.5 g sideways, overturning {M4 / 1e6:.1f} kNm")
        W1t = mt["cases"]["TC1"]["kg"] * G / n
        f5b = self.tw["design"]["mount_force_lc5b_n"]
        cases["LC5b"] = dict(shear=0.0, tension=max(0.0, f5b - W1t),
                             note=(f"a corner steady wound to 875 kg at tare: the largest bolt force {f5b / 1000:.2f} kN, either bound "
                                   f"on the roof, less its 1 g share of the tare body's weight"))
        f5 = self.tw["design"]["mount_force_n"]
        cases["LC5a"] = dict(shear=0.0, tension=max(0.0, f5 - W1),
                             note=(f"the largest raiser bolt force in the frame model with the body, {f5 / 1000:.2f} kN, either bound "
                                   f"on the roof, less its 1 g share of weight"))
        face = self.face_capacity()
        worst_t = max(c["tension"] for c in cases.values())
        worst_s = max(c["shear"] for c in cases.values())
        u_t = worst_t / md["swl_tension_n"]
        u_f = worst_t / (face / 1.5)
        u_s = worst_s / md["swl_shear_n"]
        flat = md["face_b"] - 4 * md["face_t"]
        hb = dict(util_tension=u_t, util_face=u_f, util_shear=u_s, util=max(u_t, u_f, u_s), fits=md["collar"] <= flat,
                  passes=max(u_t, u_f, u_s) <= 1.0 and md["collar"] <= flat)
        # the fallback: M12 8.8 into a welded nut plate
        fb = md["fallback"]
        bolt = fb["As"] * fb["fu"] / fb["bolt_factor"]
        pl = fb["plate"]
        plate = 1.5 * pl["fy"] * pl["l"] * pl["t"] ** 2 / 6 / (pl["span"] / 4) / 1.5     # bending capacity at fy / 1.5
        weld = 0.6 * fb["weld"]["fuw"] * 0.7 * fb["weld"]["leg"] * fb["weld"]["length"] * 0.8 / 1.5
        sp = fb["spreader"]
        punch = 4 * sp["side"] * (self.p["floor"].t1 * sp["skin_shear"] + self.p["floor"].c * sp["insert_shear"]) / 2
        fbu = dict(bolt=worst_t / bolt, plate=worst_t / plate, weld=worst_t / weld, pull_through=worst_t / punch, shear=worst_s / (0.62 * fb["As"] * fb["fu"] / 3))
        gov = max(fbu, key=fbu.get)
        use = "fallback" if md.get("design") == "nut_plate" or not hb["passes"] else "HB10"
        return dict(bolts=n, mass_kg=m, cog_z=zc, case=mt["worst"], scale=mt["scale"], cases=cases, face_n=face,
                    tension_n=worst_t, shear_n=worst_s, hb10=hb, flat_mm=flat, fallback=dict(utils=fbu, governing=gov, util=fbu[gov],
                    bolt_n=bolt, plate_n=plate, weld_n=weld, pull_through_n=punch), uses=use,
                    util=hb["util"] if use == "HB10" else fbu[gov],
                    governing=("HB10" if use == "HB10" else f"M12 8.8 nut plate fallback, {gov.replace('_', ' ')}"))

    # ------------------------------------------------------------------ openings (report 12 sections 5 and 7)
    def openings(self) -> list[dict]:
        """Every opening as a rectangle on its wall, in the wall's own (u, z) coordinates: u along the trailer from the
        body front for the side walls, Y for the end walls. The kitchen and the entry door follow their blocks."""
        V, out = self.V, []
        for o in self.d["openings"]:
            r = dict(o)
            if o.get("from"):
                b = self.lay.find(o["from"])
                if o["wall"] in ("kerb", "road"):
                    r["x"] = b.box[0] - V["body_x0"] + (o["w"] - (b.box[3] - b.box[0])) / -2 if o["from"] == "BD-07" else b.box[0] - V["body_x0"]
                    r["w"] = o["w"] if o["from"] == "BD-07" else b.box[3] - b.box[0]
                else:
                    r["y"] = (b.box[1] + b.box[4]) / 2
                    r["w"] = b.box[4] - b.box[1]
            u0 = r["x"] if o["wall"] in ("kerb", "road") else r["y"] - r["w"] / 2
            r.update(u0=u0, u1=u0 + r["w"], z0=r["z"], z1=r["z"] + r["h"], area_m2=r["w"] * r["h"] / 1e6)
            out.append(r)
        return out

    def openings_check(self) -> dict:
        """Report 12's rules: 300 mm of full wall between neighbouring openings, 150 mm to a panel edge and nothing within
        300 mm of the rear corners."""
        V, ru = self.V, self.d["rules"]
        ops = self.openings()
        probs, worst = [], math.inf
        L, Hh = V["body_length"], V["interior_h"]
        for wall in ("kerb", "road", "front", "rear"):
            w = sorted((o for o in ops if o["wall"] == wall), key=lambda o: o["u0"])
            lo, hi = (0.0, L) if wall in ("kerb", "road") else (-V["half_in"], V["half_in"])
            for o in w:
                e = min(o["u0"] - lo, hi - o["u1"], Hh - o["z1"])
                if wall in ("kerb", "road"):
                    e = min(e, (hi - ru["rear_corner_mm"]) - o["u1"] + ru["edge_mm"])
                worst = min(worst, e - ru["edge_mm"])
                if e < ru["edge_mm"] - 1e-6:
                    probs.append(f"{o['id']} is {e:.0f} mm from a panel edge or the rear corner rule")
            for i, a in enumerate(w):
                for b in w[i + 1:]:
                    overlap_z = min(a["z1"], b["z1"]) - max(a["z0"], b["z0"])
                    du = b["u0"] - a["u1"]
                    dz = max(b["z0"] - a["z1"], a["z0"] - b["z1"])
                    gap = du if overlap_z > 0 else (max(du, dz) if du > 0 else dz)
                    worst = min(worst, gap - ru["between_mm"])
                    if gap < ru["between_mm"] - 1e-6:
                        probs.append(f"{a['id']} and {b['id']} on the {wall} wall are {gap:.0f} mm apart")
        return dict(ok=not probs, problems=probs, margin_mm=worst, count=len(ops))

    # ------------------------------------------------------------------ everything, for the build and the checks
    def results(self) -> dict:
        panels = self.panel_checks()
        return dict(panels=panels, deflections=self.deflections(), roof=self.roof(), inserts=self.inserts(), cradle=self.cradle(),
                    thermal=self.cold_bridge(), awning=self.awning(), members=self.members_clear(),
                    openings=self.openings(), openings_check=self.openings_check(),
                    twist=self.tw, gj=self.box_gj(True),
                    joints=self.joints(), end_wall=self.end_wall(), mounts=self.mounts(),
                    mounted=self.mounted, panel_data={k: dict(name=p.name, D_knm2_per_m=p.D / 1e6, S_kn_per_m=p.S,
                                                             wrinkling_mpa=p.wrinkling, kg_m2=p.d["kg_m2"], t=p.d["t"])
                                                      for k, p in self.p.items()})


def check_row(c, res: dict) -> dict:
    """A trailer check row for a body_* check (data/checks.yaml)."""
    item = c.body["item"] if c.body else None
    if c.type == "body_panel":
        r = next(p for p in res["panels"] if p["id"] == item)
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=f"{r['governing']}, {r['case']}",
                    detail=(f"{r['what']}: skin {r['skin_mpa']:.1f} MPa, core shear {r['core_mpa']:.3f} MPa, utilisation "
                            f"{r['util']:.2f} ({r['governing']}){', ' + r['extra'] if r['extra'] else ''}"))
    if c.type == "body_deflection":
        r = next(d for d in res["deflections"] if d["id"] == item)
        return dict(limit=f"<= {r['limit_mm']:.1f} mm", measured=round(r["mm"], 1), unit="mm", margin=round(r["limit_mm"] - r["mm"], 1),
                    ok=r["mm"] <= r["limit_mm"], governing=r["what"], detail=f"{r['what']}: {r['mm']:.1f} mm against {r['limit_mm']:.1f} mm")
    if c.type == "body_insert":
        r = max(res["inserts"], key=lambda r: r["util"])
        return dict(limit="<= half the rated load", measured=round(r["n"] / 1000, 2), unit="kN", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=r["what"],
                    detail=". ".join(f"{i['what']}: {i['n'] / 1000:.2f} kN against {i['rated_n'] / 2000:.2f} kN ({i['case']})" for i in res["inserts"]))
    if c.type == "body_cradle":
        r = res["cradle"]
        u = r["utils"]
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3), ok=r["util"] <= 1.0,
                    governing=r["governing"],
                    detail=(f"{r['mass_kg']:.0f} kg, its centre of gravity {r['offset_mm']:.0f} mm behind the rear wall. Wall bolts: {r['tension_n'] / 1000:.2f} kN "
                            f"of tension against half the {r['pull_rated_n'] / 1000:.0f} kN pull-through ({u['bolt_tension']:.2f}), {r['shear_n'] / 1000:.2f} kN of "
                            f"shear against half of {r['shear_rated_n'] / 1000:.0f} kN ({u['bolt_shear']:.2f}). Each stay, {r['stays']['name']}, "
                            f"{r['stay_n'] / 1000:.2f} kN at 3 g against {r['stay_pcr_n'] / 1000:.1f} kN to buckle over {r['stays']['L']:,.0f} mm "
                            f"({u['stay_buckling']:.2f} with a factor of {r['stays']['buckling_factor']:g})"))
    if c.type == "body_thermal":
        t = res["thermal"]
        need = max(t["need"], t["need_gen"])
        m = t["tsi_min"] - need
        e = t["ends"]
        where = "foot" if t["tsi_min"] == e["foot"]["tsi"] else "head" if t["tsi_min"] == e["head"]["tsi"] else "mid-length"
        return dict(limit=f">= {need:.0f} C, the dew point {t['dew']:.0f} C plus 4 K", measured=round(t["tsi_min"], 1), unit="C",
                    margin=round(m, 1), ok=m >= -1e-6,
                    governing=f"inside surface over a member at its {where}, Rsi {t['rsi']:g} m2K/W, {t['t_out']:.0f} C outside, {t['t_in']:.0f} C inside",
                    detail=(f"{t['member']} with {t['brk']:g} mm of XPS behind it ({', '.join(t['members'])}, {t['length_m']:.1f} m in all), at ISO "
                            f"13788's Rsi of {t['rsi']:g} m2K/W. On the design cold night the inside surface over it is {t['tsi_mid']:.1f} C at "
                            f"mid-length and the member {t['t_member']:.1f} C. It stops {t['gap_mm']:g} mm short of the joiners, on a {t['pad_mm']:g} mm "
                            f"rigid PVC pad at its foot: with the joiner taken at the outside air, the surface is {e['foot']['tsi']:.1f} C at the foot "
                            f"and {e['head']['tsi']:.1f} C at the head (the member a fin of {t['fin_mm']:.0f} mm), against {t['need']:.0f} C. The plain "
                            f"wall is {t['tsi_plain']:.1f} C. On the generators e2 fans A and B and the RESPA-CF2, {t['gen_m3h']:.0f} m3/h, hold the "
                            f"dew point at {t['dew_gen']:.1f} C, so {t['need_gen']:.1f} C there. Each metre of member adds {t['psi']:.3f} W/K of heat "
                            f"loss on ISO 6946's film, {t['w_k']:.2f} W/K in all, {100 * t['w_k'] / t['bare']:.1f} % of the bare panels' {t['bare']:g} W/K "
                            f"beside report 19's {t['bridges']:g} W/K for the joiners, mount bolts and inserts"))
    if c.type == "body_members":
        r = res["members"]
        tight = min(r["rows"], key=lambda q: q["gap_mm"])
        return dict(limit=f">= {r['clear_mm']:g} mm clear, bays <= {r['pitch']:,.0f} mm", measured=round(r["worst_mm"], 0), unit="mm",
                    margin=round(r["worst_mm"] - r["clear_mm"], 0), ok=r["ok"], governing=f"{tight['member']} to {tight['to']}",
                    detail=(". ".join(f"{q['member']} on the {q['wall']} side at X {q['x']:,.0f}: {q['gap_mm']:.0f} mm from {q['to']}" for q in r["rows"])
                            + f". The widest bay is {r['bays']['kerb']:,.0f} mm on the kerb side and {r['bays']['road']:,.0f} mm on the road side, "
                            f"against {r['pitch']:,.0f} mm" + (". " + ". ".join(r["problems"]) if r["problems"] else "")))
    if c.type == "body_awning":
        a = res["awning"]
        return dict(limit="reported", measured=round(a["reach_mm"], 0), unit="mm", margin=None, ok=a["reach_mm"] >= 0,
                    governing=f"the legs at a {a['pitch_deg']:g} degree pitch on level ground",
                    detail=(f"the canopy leaves the case at Z {a['z_case']:,.0f} and runs out {a['extension_mm']:,.0f} mm. With the legs at full reach, "
                            f"{a['leg_max_mm']:,.0f} mm (est.), the lead bar stands at Z {a['z_bar_max']:,.0f} and the canopy falls "
                            f"{a['pitch_full_deg']:.1f} degrees. Set for {a['pitch_deg']:g} degrees, the lead bar stands at Z {a['z_bar']:,.0f} on legs "
                            f"of {a['leg_mm']:,.0f} mm, which keep {a['reach_mm']:,.0f} mm of reach for ground that falls away. Where it falls further, "
                            f"the legs at full reach give a steeper pitch"))
    if c.type == "body_roof":
        r = res["roof"]
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3), ok=r["util"] <= 1.0,
                    governing="roof-to-wall joiner bond in tension",
                    detail=(f"{r['uplift_n'] / 1000:.2f} kN of uplift on the roof ({r['roof_kg']:.0f} kg with the solar array) over "
                            f"{r['perimeter_mm'] / 1000:.1f} m of joiner, {r['q_n_mm']:.2f} N/mm against {r['allow_n_mm']:.0f} N/mm, "
                            "taking none of the roof's weight off"))
    if c.type == "body_twist":
        t = res["twist"]
        o, cl = t["open"], t["closed"]
        return dict(limit="reported", measured=round(cl["share"] * 100, 1), unit="%", margin=None, ok=True,
                    governing=t["case"],
                    detail=(f"LC5a {t['torque_knm']:.1f} kNm, {t['case']}. Bare chassis {t['bare_deg']:.3f} degree. Roof bonded "
                            f"(the design): the body takes {100 * cl['share']:.0f} %, chassis {cl['chassis_deg']:.3f} degree. Lower bound, "
                            f"roof joint neglected: {100 * o['share']:.0f} %, chassis {o['chassis_deg']:.3f} degree"))
    if c.type == "body_joint":
        r = max(res["joints"], key=lambda r: r["util"])
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=r["what"],
                    detail=". ".join(f"{j['what']} {j['value']:.2f} {j['unit']} against {j['limit']:.2f}" for j in res["joints"]))
    if c.type == "body_end_wall":
        e = res["end_wall"]
        return dict(limit="<= 1.00 utilisation", measured=round(e["util"], 3), unit="", margin=round(1 - e["util"], 3), ok=e["util"] <= 1.0,
                    governing=e["governing"],
                    detail=(f"{e['torque_knm']:.1f} kNm into the rear half of the box ({e['case']}), racking {e['force_n'] / 1000:.2f} kN. Rear wall "
                            f"skins {e['tau_mpa']:.2f} MPa in shear against {e['allow_mpa']:.1f} MPa over {e['width_mm']:.0f} mm of full panel, "
                            f"joiner {e['q_n_mm']:.2f} N/mm against {e['bond_n_mm']:.1f} N/mm"))
    if c.type == "body_mount":
        m = res["mounts"]
        hb, fb = m["hb10"], m["fallback"]
        return dict(limit="<= 1.00 utilisation", measured=round(m["util"], 3), unit="", margin=round(1 - m["util"], 3),
                    ok=m["util"] <= 1.0, governing=m["governing"],
                    detail=(f"{m['bolts']} mounts on {m['mass_kg']:.0f} kg ({m['case']} at the ATM): worst tension {m['tension_n'] / 1000:.2f} kN, "
                            f"shear {m['shear_n'] / 1000:.2f} kN. HB10: {hb['util']:.2f} of its 8.5 kN safe working load"
                            f"{'. The design uses the M12 8.8 bolt into a welded nut plate (CH-P14)' if m['uses'] == 'fallback' else ''}: bolt "
                            f"{fb['bolt_n'] / 1000:.1f} kN, plate {fb['plate_n'] / 1000:.1f} kN, weld {fb['weld_n'] / 1000:.1f} kN, floor pull-through "
                            f"{fb['pull_through_n'] / 1000:.1f} kN, governing {fb['governing'].replace('_', ' ')} at {fb['util']:.2f}. "
                            + " ".join(f"{k}: {v['note']}." for k, v in m["cases"].items())))
    if c.type == "body_openings":
        o = res["openings_check"]
        return dict(limit=">= 300 mm between, 150 mm to an edge", measured=round(o["margin_mm"], 0), unit="mm", margin=round(o["margin_mm"], 0),
                    ok=o["ok"], governing=". ".join(o["problems"][:2]) or "every rule met",
                    detail=(f"{o['count']} openings. " + (". ".join(o["problems"]) if o["problems"] else
                            f"Every opening keeps the spacing rules, the tightest by {o['margin_mm']:.0f} mm")))
    raise ValueError(f"unknown body check type {c.type}")

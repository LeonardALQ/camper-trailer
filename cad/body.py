"""Body design to planning level (BODY.md): sandwich panel, insert, joint, mount, hardpoint, rear portal, raising roof
and twist sharing checks, from research report 12 and data/body/body.yaml.

Positions are in the project datum DIM-01 (mm). Panel checks follow report 12 section 3: each panel is a one-way span
with an effective width of the load patch plus half the span. D = E t1 t2 d^2 / (t1 + t2) per unit width and
S = Gc d^2 / c, with d the distance between the skin centres and c the core thickness. The twist sharing puts the body
into the chassis frame model as a torsion box (cad/chassis.py FrameModel `body`).
"""
from __future__ import annotations

import math
from functools import cached_property

import numpy as np
import yaml

from .partsdb import DATA

BODY_YAML = DATA / "body" / "body.yaml"
G = 9.81
MOUNTED = ("body", "roof", "living", "module", "stowage", "payload")   # systems that stand on the floor


def load_data() -> dict:
    return yaml.safe_load(BODY_YAML.read_text())


class Panel:
    def __init__(self, key: str, d: dict):
        self.key, self.d = key, d
        self.name = d["name"]
        self.t1, self.t2 = d["skins"]
        self.c = d["core"]["c"]
        self.dd = self.c + (self.t1 + self.t2) / 2          # skin centre spacing
        self.E, self.G, self.ult = d["E"], d["G"], d["ult"]
        self.core = d["core"]

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
        """Uniform pressure w (N/mm2) on a one-way strip, simply supported."""
        M = w_mpa * span ** 2 / 8
        V = w_mpa * span / 2
        return dict(skin_mpa=M / (min(self.t1, self.t2) * self.dd), core_mpa=V / self.dd,
                    defl_mm=5 * w_mpa * span ** 4 / (384 * self.D) + w_mpa * span ** 2 / (8 * self.S))

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
        k = max(1.0, self.tr.caps()["atm"] / max(r["total_kg"] for r in rows.values()))
        worst = max(rows, key=lambda c: rows[c]["kg"])
        return dict(cases=rows, scale=k, worst=worst, kg=rows[worst]["kg"] * k, cog_z=rows[worst]["cog_z"])

    # ------------------------------------------------------------------ panels (report 12 section 3)
    def panel_checks(self) -> list[dict]:
        L, cr, f, w, lid = self.d["loads"], self.crit, self.p["floor"], self.p["wall"], self.p["lid"]
        V = self.V
        out = []

        def row(cid, what, panel, r, case, compression=True, extra=""):
            u = panel.utils(r, cr, compression)
            out.append(dict(id=cid, what=what, case=case, skin_mpa=r["skin_mpa"], core_mpa=r["core_mpa"],
                            util=u["util"], governing=u["governing"], extra=extra, defl_mm=r.get("defl_mm")))

        span = self.raiser_span
        wh = L["bike_wheel"]
        r = f.one_way(3 * wh["kg"] * G, min(wh["patch"]), span)
        row("BDY-01", "Floor under the bike wheel in the chock, midway between the raisers", f, r, "LC2, 3 g")
        ch = L["chock_base"]
        r = f.one_way(3 * ch["kg"] * G, min(ch["patch"]), span)
        row("BDY-02", "Floor under the chock base with the braking push on its rear edge", f, r, "LC2, 3 g")
        ft = L["foot"]
        r = f.one_way(3 * ft["kg"] * G, min(ft["patch"]), span)
        bearing = 3 * ft["kg"] * G / (ft["patch"][0] * ft["patch"][1])
        r["core_mpa"] = max(r["core_mpa"], bearing * cr["core_factor"] / cr["bearing_factor"] *
                            f.core["shear"] / f.core["compression"])
        row("BDY-03", "Living-area floor under a foot, with bearing on the core", f, r, "LC2, 3 g",
            extra=f"bearing {bearing:.2f} MPa against {cr['bearing_factor'] * f.core['compression']:.2f} MPa")
        pitch = max(b - a for a, b in zip(self.stations, self.stations[1:]))
        r = f.uniform(3 * L["floor_edge_kg_m2"] * G / 1e6, pitch)
        row("BDY-04", f"Floor edge beside the raisers between outriggers {pitch:.0f} mm apart", f, r, "LC2, 3 g")
        g = L["generator"]
        r = f.one_way(3 * g["kg"] * G, min(g["patch"]), pitch)
        row("BDY-05", "Floor edge under the generator and jerry cans between outriggers", f, r, "LC2, 3 g")
        # side wall in wind, spanning from the floor to the pop-top ring
        r = w.uniform(L["wind_kpa"] / 1000, V["interior_h"])
        row("BDY-06", "Side wall in a 0.5 kPa wind, floor to the pop-top ring", w, r, "Wind")
        # lid with the bonded solar array and its own weight, spanning between the walls
        sol = sum(b.mass_kg for b in self.lay.blocks if b.system == "roof")
        q = 3 * (lid.d["kg_m2"] + sol / (V["body_length"] * V["body_width"] / 1e6)) * G / 1e6
        r = lid.uniform(q, V["body_width"] - V["wall_t"])
        row("BDY-07", f"Lid with the {sol:.0f} kg solar array, spanning between the walls", lid, r, "LC2, 3 g")
        self.lid_defl = lid.uniform(q / 3, V["body_width"] - V["wall_t"])["defl_mm"]
        self.floor_defl = f.one_way(wh["kg"] * G, min(wh["patch"]), span)["defl_mm"]
        self.wall_defl = w.uniform(L["wind_kpa"] / 1000, V["interior_h"])["defl_mm"]
        return out

    def deflections(self) -> list[dict]:
        cr, V = self.crit, self.V
        self.panel_checks() if not hasattr(self, "lid_defl") else None
        return [dict(id="DEF-B1", what="Floor under the bike wheel at 1 g", mm=self.floor_defl, limit_mm=self.raiser_span / cr["floor_span_ratio"]),
                dict(id="DEF-B2", what="Lid with the solar array at 1 g", mm=self.lid_defl, limit_mm=(V["body_width"] - V["wall_t"]) / cr["lid_span_ratio"]),
                dict(id="DEF-B3", what="Side wall in a 0.5 kPa wind", mm=self.wall_defl, limit_mm=V["interior_h"] / cr["wall_span_ratio"])]

    # ------------------------------------------------------------------ inserts, ledgers and the raising roof
    def roof(self) -> dict:
        """Lid mass, the lifted mass for the actuators and the latch load (report 12 section 6)."""
        d, V, lid = self.d["roof"], self.V, self.p["lid"]
        area = V["body_length"] * V["body_width"] / 1e6
        cut = sum(h["cut"][0] * h["cut"][1] for h in d["hatches"]) / 1e6
        lid_kg = (area - cut) * lid.d["kg_m2"] + d["insert_strips_kg"]
        solar = sum(b.mass_kg for b in self.lay.blocks if b.system == "roof")
        hatches = sum(h["kg"] for h in d["hatches"])
        lifted = lid_kg + solar + d["top_ring_kg"] + hatches + d["canvas_kg"] / 2
        per_act = lifted * G / d["actuators"]
        latch = d["uplift_40ms_n"] / d["latches"]
        return dict(area_m2=area, cut_m2=cut, lid_kg=lid_kg, solar_kg=solar, hatches_kg=hatches, lifted_kg=lifted,
                    actuator_n=per_act, actuator_util=per_act / d["actuator_n"], latch_n=latch,
                    latch_util=latch / d["latch_rating_n"])

    def inserts(self) -> list[dict]:
        """Working loads on the panel fixings against half their rated load (report 12 section 3, MAT-05)."""
        L, cr = self.d["loads"], self.crit
        perm = 3 * L["bed_kg"] * G / 2 / (2 * self.V["half_in"])   # N/mm per ledger
        f_ledger = perm * L["ledger_pitch"]
        awning = next((b for b in self.lay.blocks if b.id == "BD-13"), None)
        aw_kg = awning.mass_kg if awning else 41.0
        f_awning = math.hypot(3 * aw_kg * G / 6, 3 * aw_kg * G / 6 * 100 / 60)   # six brackets, 100 mm offset, 60 mm bolt pitch
        rows = [dict(id="INS-01", what="Bed ledger fixing in the side wall, Deform-Nut M6 in a pultruded strip, shear", n=f_ledger, rated_n=1700,
                     case="LC2, 3 g on the 255 kg bed"),
                dict(id="INS-02", what="Awning bracket bolt, Panelock APLB-1020 through the wall's top insert strip, tension", n=f_awning, rated_n=20000,
                     case="LC2, 3 g on the awning")]
        for r in rows:
            r["util"] = r["n"] / (cr["insert_factor"] * r["rated_n"])
        return rows

    # ------------------------------------------------------------------ the body as a torsion box (report 12 section 4)
    def box_gj(self, lid_structural: bool) -> dict:
        """GJ of the body box per region, N mm2. The garage is a closed cell of the floor, the walls and the bed deck.
        The living area is closed only if the latched lid carries shear (report 12's assumption), otherwise it is an
        open U of the floor and the walls."""
        V, p, tw = self.V, self.p, self.d["twist"]
        b = V["body_width"] - V["wall_t"]
        zf = V["floor_z"] - p["floor"].d["t"] / 2
        h_g = V["floor_z"] + self.lay.mod.params["deck_z"] + p["deck"].d["t"] / 2 - zf if "deck_z" in self.lay.mod.params else 1535.0
        h_l = V["ceiling_z"] + p["lid"].d["t"] / 2 - zf
        walls, floor = p["wall"].Gt, p["floor"].Gt

        def closed(h, top_gt):
            A = b * h
            return 4 * A ** 2 / (2 * h / walls + b / floor + b / top_gt), A
        gj_g, A_g = closed(h_g, p["deck"].Gt * tw["deck_joint_factor"])
        gj_lc, A_l = closed(h_l, p["lid"].Gt * tw["lid_joint_factor"])
        gj_lo = p["floor"].plate_gj(b) + 2 * p["wall"].plate_gj(h_l)
        return dict(garage=gj_g, living=gj_lc if lid_structural else gj_lo, living_closed=gj_lc, living_open=gj_lo,
                    A_garage=A_g, A_living=A_l, h_garage=h_g, h_living=h_l, b=b)

    def segments(self, lid_structural: bool) -> list[tuple[float, float, float]]:
        """(x0, x1, GJ) per bay between stations, the garage and living stiffnesses in series by length."""
        gj = self.box_gj(lid_structural)
        xa = self.V["part_a_x"]
        out = []
        for x0, x1 in zip(self.stations, self.stations[1:]):
            l_liv = max(0.0, min(x1, xa) - x0)
            l_gar = (x1 - x0) - l_liv
            out.append((x0, x1, (x1 - x0) / (l_liv / gj["living"] + l_gar / gj["garage"])))
        return out

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
                    garage_torque_knm=max((t for x0, x1, t in tor if x0 >= self.V["part_a_x"] - 1), default=0.0) / 1e6,
                    station_torque_knm=per_station, segments=[dict(x0=x0, x1=x1, torque_knm=t / 1e6) for x0, x1, t in tor],
                    mount_force_n=abs(worst[2]), mount_worst=[worst[0], worst[1], worst[3]], mount_pulled=worst[2] > 0,
                    chassis_mpa=gm[1]["eq"], chassis_member=gm[0])

    def twist(self) -> dict:
        """LC5a (one wheel in a hole, travelling) and LC5b (one corner steady wound to 875 kg at tare, parked) with the
        body tied to the chassis at every station, for both bounds on the lid. LC5a takes the case and diagonal with the
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
                             garage_torque_knm=max(r["garage_torque_knm"] for r in both),
                             mount_force_n=max(r["mount_force_n"] for r in both),
                             mount_force_lc5b_n=max(out[k]["mount_force_n"] for k in ("open_lc5b", "closed_lc5b")))
        # parked with the door open the garage cell has no rear diaphragm, so it sheds the twist to the chassis and the
        # rear wall only follows the chassis: its racking is the bare chassis twist between partition A and the rear
        an0 = Analysis(self.lay, self.tr, ch)
        res, _ = an0.run_static(an0.items(tc1), lb["accel"][0], steady_n=lb["steady_kg"] * G)
        rc = ch.V["rail_c"]

        def theta(x):
            return (res.u[6 * an0.fm.rail_node(1, x) + 2] - res.u[6 * an0.fm.rail_node(-1, x) + 2]) / (2 * rc)
        xa = min(x for x in self.stations if x >= self.V["part_a_x"])
        out["design"]["lc5b_garage_twist_rad"] = abs(theta(self.stations[-1]) - theta(xa))
        return out

    # ------------------------------------------------------------------ joints, portal and mounts under the body's share
    @cached_property
    def tw(self) -> dict:
        return self.twist()

    def joints(self) -> list[dict]:
        """Shear flow q = T / 2A from the body's share of LC5a in the skins and the bonded joints, with the larger body
        torque of the two bounds on the lid and the smaller cell area."""
        gj, cr, p = self.box_gj(True), self.crit, self.p
        T = self.tw["design"]["max_body_torque_knm"] * 1e6
        q = T / (2 * min(gj["A_garage"], gj["A_living"]))
        bond = self.d["twist"]["bond_shear_strength"] * self.d["twist"]["bond_width"]
        rows = []
        for key, what in (("wall", "Side wall skins in shear"), ("floor", "Floor skins in shear"), ("lid", "Lid skins in shear")):
            pn = p[key]
            tau = q / (pn.t1 + pn.t2)
            allow = cr["skin_factor"] * pn.ult / math.sqrt(3)
            rows.append(dict(id=f"JNT-{key}", what=what, value=tau, unit="MPa", limit=allow, util=tau / allow))
        rows.append(dict(id="JNT-bond", what="Bonded joiner leg, MS polymer, shear flow per mm", value=q, unit="N/mm",
                         limit=0.5 * bond, util=q / (0.5 * bond)))
        return rows

    def portal(self) -> dict:
        """The rear wall as the garage cell's end diaphragm (report 12 section 5). The torque the floor bolts put into the
        garage cell at the stations in its rear half has to be held in shape at the rear wall, so the wall racks under
        F = T / 2h, h the cell height. The door is taken open (the portal and the 380 mm pier alone), for LC5a and LC5b
        and both bounds on the lid. The portal is solved as a frame with its feet fixed to the rear outriggers.
        Redesign: report 12's aluminium SHS portal on pinned feet racked about 50 mm and reached 94 MPa against
        73 MPa, so the portal is hot-dip galvanised steel with moment base plates (BODY.md)."""
        from .frame import Frame, Section, end_actions
        d, V = self.d["portal"], self.V
        gj = self.box_gj(True)
        h = d["height"]
        mp = self.lay.mod.params
        x_mid = (self.V["part_a_x"] + self.V["body_x1"]) / 2
        runs = {k: self.tw[k] for k in ("open", "closed", "open_lc5b", "closed_lc5b")}
        T_by = {k: sum(v for x, v in r["station_torque_knm"].items() if x >= x_mid) for k, r in runs.items()}
        gov = max(T_by, key=T_by.get)
        T = T_by[gov] * 1e6
        F = T / (2 * gj["h_garage"])
        yk, yr = mp["door_y0"] - 25, mp["door_y1"] + 20
        f = Frame()
        a, b = f.node((0, yk, 0)), f.node((0, yr, 0))
        c, e = f.node((0, yk, h)), f.node((0, yr, h))
        secs = {}
        for key, n0, n1 in (("kerb_post", a, c), ("road_jamb", b, e), ("header", c, e)):
            s = d[key]
            el = f.add(n0, n1, Section(key, s["A"], s["I"], s["I"], s["J"]), (1, 0, 0), key)
            el.E, el.G = d["E"], d["E"] / 2.6
            secs[key] = s
        feet = [(n, k) for n in (a, b) for k in range(6)] if d["feet"] == "fixed" else [(n, k) for n in (a, b) for k in (0, 1, 2)]
        sup = feet + [(n, k) for n in (c, e) for k in (0, 4, 5)]
        w, wl = d["pier"]["w"], self.p["wall"]
        I_p = (wl.t1 + wl.t2) * w ** 3 / 12
        k_pier = 1 / (V["interior_h"] ** 3 / (3 * wl.E * I_p) + V["interior_h"] / (wl.G * (wl.t1 + wl.t2) * w))
        q = np.zeros(6 * len(f.nodes))
        q[6 * c + 1] = 1000.0
        res = f.solve(q, sup)
        k_portal = 1000.0 / abs(res.u[6 * c + 1])
        Fp = F * k_portal / (k_portal + k_pier)
        rows = []
        for el, fl in zip(f.elements, res.forces):
            m = max(abs(v) for act in end_actions(fl) for v in (act["Mz"], act["My"])) * Fp / 1000
            sig = m / secs[el.member]["Z"]
            rows.append(dict(member=el.member, name=secs[el.member]["name"], moment_knm=m / 1e6, stress_mpa=sig))
        worst = max(rows, key=lambda r: r["stress_mpa"])
        lim = d["fy"] / 1.5
        return dict(case=gov, torque_knm=T / 1e6, force_n=F, portal_n=Fp, k_portal=k_portal, k_pier=k_pier,
                    rack_mm=F / (k_portal + k_pier), members=rows, stress_mpa=worst["stress_mpa"], governing=worst["name"],
                    limit_mpa=lim, util=worst["stress_mpa"] / lim, mass_kg=d["mass_kg"])

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
                                   f"on the lid, less its 1 g share of the tare body's weight"))
        f5 = self.tw["design"]["mount_force_n"]
        cases["LC5a"] = dict(shear=0.0, tension=max(0.0, f5 - W1),
                             note=(f"the largest raiser bolt force in the frame model with the body, {f5 / 1000:.2f} kN, either bound "
                                   f"on the lid, less its 1 g share of weight"))
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
        use = "HB10" if hb["passes"] else "fallback"
        return dict(bolts=n, mass_kg=m, cog_z=zc, case=mt["worst"], scale=mt["scale"], cases=cases, face_n=face,
                    tension_n=worst_t, shear_n=worst_s, hb10=hb, flat_mm=flat, fallback=dict(utils=fbu, governing=gov, util=fbu[gov],
                    bolt_n=bolt, plate_n=plate, weld_n=weld, pull_through_n=punch), uses=use,
                    util=hb["util"] if use == "HB10" else fbu[gov],
                    governing=("HB10" if use == "HB10" else f"M12 8.8 nut plate fallback, {gov.replace('_', ' ')}"))

    def hardpoints(self) -> list[dict]:
        """Every L-track anchor at the 20 kN strap breaking load (RES-01). The floor spans across the trailer between
        the raisers, or from a raiser to the wall foot for the anchors outboard of the raisers. The hardpoint strip
        under the row carries the shear into an HB10 at each raiser and into the floor joiner at the wall. Each part
        needs a factor of at least 1.5 on its ultimate (report 12 section 3)."""
        hp, L, V, f = self.d["hardpoint"], self.d["loads"], self.V, self.p["floor"]
        P = L["anchor_n"]
        prj = self.tr.prj
        face = self.face_capacity()
        hb_ult = 5 * self.d["mounts"]["swl_tension_n"]
        strip = hp["w"] * hp["h"] * hp["shear_strength"]
        joiner = hp["joiner_length"] * self.d["twist"]["bond_width"] * hp["joiner_tension"]
        rf = V["rail_c"] + V["rail_w"] / 2
        rows = []
        for i in prj.instances:
            if i.part != "G-03" or i.at[1] is None:
                continue
            x, y = i.at[0] + V["module_x0"], i.at[1]
            if abs(y) <= rf:
                span, a = self.raiser_span, abs(y + V["rail_c"])
                r = f.one_way(P, 300, span, min(a, span - a))
                r_raiser, r_wall = P * max(a, span - a) / span, 0.0
            else:
                span, a = self.edge_span, abs(y) - rf
                r = f.one_way(P, 300, span, min(a, span - a))
                r_raiser, r_wall = P * (span - a) / span, P * a / span
            factors = dict(skin=f.ult / r["skin_mpa"], strip=strip / max(r_raiser, r_wall),
                           bolt=min(hb_ult, face) / r_raiser if r_raiser else None,
                           joiner=joiner / r_wall if r_wall else None)
            factors = {k: v for k, v in factors.items() if v is not None}
            gov = min(factors, key=factors.get)
            rows.append(dict(id=i.iid, x=x, y=y, span=span, factors=factors, factor=factors[gov], governing=gov,
                             util=self.crit["ultimate_factor"] / factors[gov]))
        return rows


    # ------------------------------------------------------------------ openings (report 12 sections 5 and 7)
    def openings(self) -> list[dict]:
        """Every opening as a rectangle on its wall, in the wall's own (u, z) coordinates: u along the trailer from the
        body front for the side walls, Y for the end walls. The kitchen, entry door and garage door follow their blocks."""
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
        """Report 12's rules: 300 mm of full wall between neighbouring openings, 150 mm to a panel edge, nothing within
        300 mm of the rear corners or in the 380 mm pier. The garage door is framed by the portal, so it may come
        within 40 mm of the road-side wall."""
        V, ru = self.V, self.d["rules"]
        ops = self.openings()
        probs, worst = [], math.inf
        L, Hh = V["body_length"], V["interior_h"]
        for wall in ("kerb", "road", "front", "rear"):
            w = sorted((o for o in ops if o["wall"] == wall), key=lambda o: o["u0"])
            lo, hi = (0.0, L) if wall in ("kerb", "road") else (-V["half_in"], V["half_in"])
            for o in w:
                if o["id"] == "OP-12":
                    continue
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
        pier = [o for o in ops if o["wall"] == "rear" and o["id"] != "OP-12" and o["u0"] < -V["half_in"] + ru["pier_mm"]]
        probs += [f"{o['id']} is in the rear wall's kerb-side pier" for o in pier]
        return dict(ok=not probs, problems=probs, margin_mm=worst, count=len(ops))

    # ------------------------------------------------------------------ everything, for the build and the checks
    def results(self) -> dict:
        panels = self.panel_checks()
        hp = self.hardpoints()
        worst_hp = min(hp, key=lambda r: r["factor"]) if hp else None
        return dict(panels=panels, deflections=self.deflections(), roof=self.roof(), inserts=self.inserts(),
                    openings=self.openings(), openings_check=self.openings_check(),
                    twist=self.tw, gj=self.box_gj(True) | dict(living_open=self.box_gj(False)["living"]),
                    joints=self.joints(), portal=self.portal(), mounts=self.mounts(), hardpoints=hp, hardpoint_worst=worst_hp,
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
                    detail="; ".join(f"{i['what']}: {i['n'] / 1000:.2f} kN against {i['rated_n'] / 2000:.2f} kN ({i['case']})" for i in res["inserts"]))
    if c.type == "body_roof":
        r = res["roof"]
        u = max(r["actuator_util"], r["latch_util"])
        return dict(limit="<= 1.00 utilisation", measured=round(u, 3), unit="", margin=round(1 - u, 3), ok=u <= 1.0,
                    governing="latch" if r["latch_util"] >= r["actuator_util"] else "actuator",
                    detail=(f"lifted mass {r['lifted_kg']:.1f} kg (lid {r['lid_kg']:.1f}, solar {r['solar_kg']:.1f}), "
                            f"{r['actuator_n']:.0f} N per actuator against {r['actuator_n'] / r['actuator_util']:.0f} N; "
                            f"{r['latch_n']:.0f} N per latch in the 40 m/s uplift against {r['latch_n'] / r['latch_util']:.0f} N"))
    if c.type == "body_twist":
        t = res["twist"]
        o, cl = t["open"], t["closed"]
        return dict(limit="reported", measured=round(o["share"] * 100, 1), unit="%", margin=None, ok=True,
                    governing=t["case"],
                    detail=(f"LC5a {t['torque_knm']:.1f} kNm, {t['case']}. Bare chassis {t['bare_deg']:.3f} degree. Lid not structural: "
                            f"the body takes {100 * o['share']:.0f} % in the twist zone, chassis {o['chassis_deg']:.3f} degree. Lid structural "
                            f"(report 12): {100 * cl['share']:.0f} %, chassis {cl['chassis_deg']:.3f} degree"))
    if c.type == "body_joint":
        r = max(res["joints"], key=lambda r: r["util"])
        return dict(limit="<= 1.00 utilisation", measured=round(r["util"], 3), unit="", margin=round(1 - r["util"], 3),
                    ok=r["util"] <= 1.0, governing=r["what"],
                    detail="; ".join(f"{j['what']} {j['value']:.2f} {j['unit']} against {j['limit']:.2f}" for j in res["joints"]))
    if c.type == "body_portal":
        p = res["portal"]
        return dict(limit=f"<= {p['limit_mpa']:.0f} MPa", measured=round(p["stress_mpa"], 1), unit="MPa",
                    margin=round(p["limit_mpa"] - p["stress_mpa"], 1), ok=p["util"] <= 1.0, governing=p["governing"],
                    detail=(f"{p['torque_knm']:.1f} kNm put into the rear half of the garage cell ({p['case']}), racking "
                            f"{p['force_n'] / 1000:.2f} kN with the door open. The steel portal ({p['k_portal']:.0f} N/mm, fixed feet) "
                            f"takes {p['portal_n'] / 1000:.2f} kN and the pier ({p['k_pier']:.0f} N/mm) the rest, "
                            f"{p['rack_mm']:.1f} mm of racking. " + ", ".join(f"{m['name']} {m['stress_mpa']:.0f} MPa" for m in p["members"])
                            + f" against {p['limit_mpa']:.0f} MPa"))
    if c.type == "body_mount":
        m = res["mounts"]
        hb, fb = m["hb10"], m["fallback"]
        return dict(limit="<= 1.00 utilisation", measured=round(m["util"], 3), unit="", margin=round(1 - m["util"], 3),
                    ok=m["util"] <= 1.0, governing=m["governing"],
                    detail=(f"{m['bolts']} mounts on {m['mass_kg']:.0f} kg ({m['case']} at the ATM): worst tension {m['tension_n'] / 1000:.2f} kN, "
                            f"shear {m['shear_n'] / 1000:.2f} kN. HB10: {hb['util']:.2f} of its 8.5 kN safe working load"
                            f"{', so the fallback is used' if m['uses'] == 'fallback' else ''}. M12 8.8 into a welded nut plate: bolt "
                            f"{fb['bolt_n'] / 1000:.1f} kN, plate {fb['plate_n'] / 1000:.1f} kN, weld {fb['weld_n'] / 1000:.1f} kN, floor pull-through "
                            f"{fb['pull_through_n'] / 1000:.1f} kN, governing {fb['governing'].replace('_', ' ')} at {fb['util']:.2f}. "
                            + " ".join(f"{k}: {v['note']}." for k, v in m["cases"].items())))
    if c.type == "body_hardpoint":
        w = res["hardpoint_worst"]
        return dict(limit=">= 1.5 on ultimate", measured=round(w["factor"], 2), unit="", margin=round(w["factor"] - 1.5, 2),
                    ok=w["factor"] >= 1.5, governing=f"anchor {w['id']} at X {w['x']:.0f}, Y {w['y']:+.0f}, {w['governing']}",
                    detail=(f"{len(res['hardpoints'])} anchors at 20 kN. Worst {w['id']}: factor {w['factor']:.2f} on the "
                            f"{w['governing']} (" + ", ".join(f"{k} {v:.2f}" for k, v in w["factors"].items()) + ")"))
    if c.type == "body_openings":
        o = res["openings_check"]
        return dict(limit=">= 300 mm between, 150 mm to an edge", measured=round(o["margin_mm"], 0), unit="mm", margin=round(o["margin_mm"], 0),
                    ok=o["ok"], governing="; ".join(o["problems"][:2]) or "every rule met",
                    detail=(f"{o['count']} openings. " + ("; ".join(o["problems"]) if o["problems"] else
                            f"Every opening keeps the spacing rules, the tightest by {o['margin_mm']:.0f} mm")))
    raise ValueError(f"unknown body check type {c.type}")

"""Frame analysis of the chassis and drawbar for report 11's load cases (CHASSIS.md).

Loads come from the trailer layout's mass schedule for each trailer case TC1 to TC8, water included, scaled up to the
plated ATM, plus the designed members and fittings (cad/chassis.py) in place of the layout's chassis and drawbar
blocks. Each mass goes onto the frame by a rule that follows its load path:

- floor: the floor spans across the trailer onto the raisers, so a load between the rails is shared by the two
  composite rails by the lever rule, and a load outside them is shared by the two nearest outriggers on that side;
- roof: walls carry the roof, so roof-borne items go to the two body edges by the lever rule, then as floor loads;
- rails: items hung between the rails (tanks, water, battery, guards) are shared by the two rails;
- spare: the spare wheel on its two carrier posts, onto the body front crossmember;
- drawbar: items on the drawbar onto its members;
- unsprung: the arms, hubs, wheels and tyres ride on the arm, so they reach the chassis through the arm.

Every load keeps its exact resultant: the nodes it is shared between also take the moment of its offset. The ball
and the four wheels react the case by statics (report 11 section 3.1: equal loads on the two axles of a side), each
arm is solved as a free body about its hinge (the airbag takes the moment, the hinge the rest), and the frame is
held only by six kinematic supports whose reactions come out at zero. The drawbar, chain and recovery cases instead
hold the frame at its suspension mounts, as the VSB1 14 test holds the body.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .chassis import SIDES, Chassis, Composite
from .frame import end_actions

G = 9.81
SKIP_SYSTEMS = {"chassis", "drawbar"}           # replaced by the designed members and fittings
SKIP_IDS = {"SP-03"}                            # the spare wheel bracket estimate, replaced by the carrier posts
UNSPRUNG = {"RG-01", "RG-02", "RG-06"}
ROOF = {"BD-02", "BD-08", "RF-01"}
RAILS = {"BD-10", "RG-03", "RG-04", "RG-05"}   # hung from the rails: mud flaps, the TSC unit and the XT Air box under the floor
CELL = 200.0


@dataclass
class Item:
    id: str
    name: str
    m: float                       # kg
    p: tuple[float, float, float]  # where the mass acts
    rule: str
    wheel: str | None = None


class Analysis:
    def __init__(self, lay, tr, ch: Chassis, body=None):
        self.lay, self.tr, self.ch = lay, tr, ch
        self.fm = ch.frame(body)
        self.f = self.fm.f
        self.n = 6 * len(self.f.nodes)
        V = ch.V
        self.atm = tr.caps()["plated"]       # the frame model runs at the plated ATM
        ball = self.fm.ball
        rear = [w for w in ch.suspension if w["axle"] == "rear"]
        rk = self.fm.rail_node(-1, rear[0]["airbag"][0])
        rr = self.fm.rail_node(1, rear[0]["airbag"][0])
        self.kinematic = self.f.prepare([(ball, 0), (ball, 1), (ball, 2), (rk, 2), (rr, 2), (rk, 1)])
        body = []
        for w in ch.suspension:
            body += [(self.fm.pivot_nodes[w["id"]], d) for d in range(3)]
            body.append((self.fm.rail_node(w["side"], w["airbag"][0]), 2))
        self.body = self.f.prepare(body)
        galv = ch.galvanising()
        self.galv_rate = {r["t"]: r["kg_per_m2"] for r in galv["rows"]}
        self.chassis_items = self._chassis_items()

    # ------------------------------------------------------------------ masses
    def _chassis_items(self) -> list[Item]:
        """Designed members and fittings, each with its galvanising."""
        out = []
        V = self.ch.V
        for m in self.ch.members:
            mass = m.mass_kg + m.area_m2 * self.galv_rate[m.sec.t]
            if m.in_frame:
                out.append(Item(m.id, m.name, mass, m.cog, "self"))
            elif m.role == "raiser":
                for k in range(10):
                    x = m.p0[0] + (m.p1[0] - m.p0[0]) * (k + 0.5) / 10
                    out.append(Item(m.id, m.name, mass / 10, (x, m.p0[1], m.p0[2]), "rails"))
            else:
                out.append(Item(m.id, m.name, mass, m.cog, "spare"))
        for f in self.ch.fittings:
            g = f.area_m2_each * self.galv_rate.get(f.t, 0.0) if f.t else 0.0
            if f.kind == "strip":
                for s in (-1, 1):
                    for k in range(10):
                        x = V["body_x0"] + V["body_length"] * (k + 0.5) / 10
                        out.append(Item(f.id, f.name, f.mass_kg / 20, (x, s * V["rail_c"], V["floor_underside_z"] - 10), "rails"))
                continue
            each_g = g * f.qty / len(f.at)
            for p in f.at:
                rule = "drawbar" if p[0] < V["body_x0"] - 100 else ("spare" if f.id == "CH-P09" else "rails")
                out.append(Item(f.id, f.name, f.mass_kg / len(f.at) + each_g, tuple(p), rule))
        return out

    def items(self, case) -> list[Item]:
        lay, V = self.lay, self.ch.V
        out = []
        for b, m in lay.case_lines(case):
            if m <= 0 or b.system in SKIP_SYSTEMS or b.id in SKIP_IDS:
                continue
            if b.id in UNSPRUNG:
                w = min(self.ch.suspension, key=lambda w: abs(w["hub"][0] - b.cog[0]) + abs(w["hub"][1] - b.cog[1]))
                out.append(Item(b.iid, b.name, m, tuple(b.cog), "unsprung", w["id"]))
                continue
            if b.load == "water":
                tanks = lay.tanks()
                area = sum((t.box[3] - t.box[0]) * (t.box[4] - t.box[1]) for t in tanks)
                for t in tanks:
                    share = m * (t.box[3] - t.box[0]) * (t.box[4] - t.box[1]) / area
                    out += self._sliced(b.iid, b.name, share, t.box, b.cog[2], "rails")
                continue
            if b.cog[0] < V["body_x0"] - 100:
                rule = "drawbar"          # the drawbar box and its contents
            elif b.system == "underfloor" or b.id in RAILS:
                rule = "rails"
            elif b.id in ROOF:
                rule = "roof"
            elif b.system == "spare":
                rule = "spare"
            else:
                rule = "floor"
            if b.box is not None and rule in ("floor", "rails", "roof") and b.cog == tuple((b.box[i] + b.box[i + 3]) / 2 for i in range(3)):
                out += self._sliced(b.iid, b.name, m, b.box, b.cog[2], rule)
            else:
                out.append(Item(b.iid, b.name, m, tuple(b.cog), rule))
        return out + list(self.chassis_items)

    @staticmethod
    def _sliced(iid, name, m, box, z, rule) -> list[Item]:
        nx = max(1, math.ceil((box[3] - box[0]) / CELL))
        ny = max(1, math.ceil((box[4] - box[1]) / CELL))
        out = []
        for i in range(nx):
            for j in range(ny):
                x = box[0] + (box[3] - box[0]) * (i + 0.5) / nx
                y = box[1] + (box[4] - box[1]) * (j + 0.5) / ny
                out.append(Item(iid, name, m / (nx * ny), (x, y, z), rule))
        return out

    # ------------------------------------------------------------------ load vector
    def _apply(self, F: np.ndarray, p, fr: list[tuple[int, float]], q: np.ndarray, M: np.ndarray | None = None):
        """Share force F acting at p between nodes by fractions fr, with the moment of the offset kept exact."""
        xyz = self.f.nodes
        tot = sum(w for _, w in fr)
        fr = [(n, w / tot) for n, w in fr]
        c = np.zeros(3)
        for n, w in fr:
            c += w * np.asarray(xyz[n])
        Mres = np.cross(np.asarray(p, float) - c, F) + (M if M is not None else 0.0)
        for n, w in fr:
            q[6 * n:6 * n + 3] += w * F
            q[6 * n + 3:6 * n + 6] += w * Mres

    def _fractions(self, it: Item) -> list[tuple[int, float]]:
        x, y, _ = it.p
        fm, V = self.fm, self.ch.V
        if it.rule == "floor":
            return fm.floor_fractions(x, y)
        if it.rule == "rails":
            return fm.between_rails(x, y)
        if it.rule == "drawbar":
            return fm.drawbar_fractions(x, y)
        if it.rule == "spare":
            cm = next(m.id for m in self.ch.members if m.station == "front" and m.role.startswith("cm"))
            return fm.crossmember_fractions(cm, -V["spare_post_y"]) + fm.crossmember_fractions(cm, V["spare_post_y"])
        raise ValueError(it.rule)

    def _self_weight(self, it: Item, F: np.ndarray, q: np.ndarray):
        """A member's weight along its elements. The frame axis of the composite rail is the composite centroid, so
        each share acts at the member's own axis (`offset`) and its nodes take the moment of the difference."""
        xyz = self.f.nodes
        els = [el for el in self.f.elements if el.member == it.id]
        L = [math.dist(xyz[el.i], xyz[el.j]) for el in els]
        tot = sum(L)
        mids = [(np.asarray(xyz[el.i]) + np.asarray(xyz[el.j])) / 2 for el in els]
        offset = np.asarray(it.p) - sum(l * m for l, m in zip(L, mids)) / tot
        for el, l, mid in zip(els, L, mids):
            self._apply(F * l / tot, mid + offset, [(el.i, 0.5), (el.j, 0.5)], q)

    def sprung_loads(self, items: list[Item], acc) -> np.ndarray:
        q = np.zeros(self.n)
        a = np.asarray(acc, float) * G
        for it in items:
            F = it.m * a
            if it.rule == "unsprung":
                continue
            if it.rule == "self":
                self._self_weight(it, F, q)
            elif it.rule == "roof":
                e = self.ch.V["half_bw"] - self.ch.V["wall_t"] / 2
                t = (min(max(it.p[1], -e), e) + e) / (2 * e)
                for yy, w in ((-e, 1 - t), (e, t)):
                    if w > 0:
                        pe = (it.p[0], yy, it.p[2])
                        self._apply(F * w, pe, self.fm.floor_fractions(it.p[0], yy), q)
            else:
                self._apply(F, it.p, self._fractions(it), q)
        return q

    # ------------------------------------------------------------------ reactions and the arms
    def reactions(self, items: list[Item], acc, twist_n: float = 0.0, lifted: int | None = None):
        """Ball force and the four wheel contact forces that balance the case. Equal vertical loads on the two axles
        of a side. Horizontal tyre forces in proportion to the vertical ones (the ball takes none along X, the brakes
        do it all). `twist_n` adds the diagonal pattern of one wheel in a hole. `lifted` (a side) is the jacking case:
        that side's wheels carry nothing and a pad under its rail at the XT centre crossmember takes the load."""
        ch, V = self.ch, self.ch.V
        a = np.asarray(acc, float) * G
        Fa = np.zeros(3)
        Ma = np.zeros(3)
        for it in items:
            F = it.m * a
            Fa += F
            Ma += np.cross(np.asarray(it.p, float), F)
        B = np.array([0.0, 0.0, V["coupling_z"]])
        wheels = ch.suspension
        if lifted is not None:
            far = [w for w in wheels if w["side"] != lifted]
            pad = next(f for f in ch.fittings if f.id == "CH-P06")
            jx = ch.positions()["jack_x"]
            jy = lifted * abs(pad.at[0][1])
            # unknowns: ball Fz, far wheel Fz (each), pad Fz. Fz, Mx, My
            A = np.array([[1, 2, 1],
                          [0, 2 * far[0]["contact"][1], jy],
                          [0, -(far[0]["contact"][0] + far[1]["contact"][0]), -jx]])
            sol = np.linalg.solve(A, -np.array([Fa[2], Ma[0], Ma[1]]))
            contact = {w["id"]: np.array([0, 0, sol[1]]) if w["side"] != lifted else np.zeros(3) for w in wheels}
            return dict(ball=np.array([0, 0, sol[0]]), contact=contact, pad=(np.array([0, 0, sol[2]]), (jx, jy, V["rail_underside_z"])))
        w_h = {w["id"]: 0.25 for w in wheels}
        for _ in range(6):
            sx = sum(w_h[w["id"]] * w["contact"][0] for w in wheels)
            sy = sum(w_h[w["id"]] * w["contact"][1] for w in wheels)
            xs = {s: sum(w["contact"][0] for w in wheels if w["side"] == s) for s in (-1, 1)}
            ys = {s: sum(w["contact"][1] for w in wheels if w["side"] == s) for s in (-1, 1)}
            # unknowns: Fby, Fbz, FzK (per wheel), FzR (per wheel), Fyw (total), Fxw (total)
            A = np.zeros((6, 6))
            r = -np.r_[Fa, Ma]
            A[0, 5] = 1
            A[1, 0], A[1, 4] = 1, 1
            A[2, 1], A[2, 2], A[2, 3] = 1, 2, 2
            A[3, 0], A[3, 2], A[3, 3] = -B[2], ys[-1], ys[1]
            A[4, 2], A[4, 3] = -xs[-1], -xs[1]
            A[5, 4], A[5, 5] = sx, -sy
            Fby, Fbz, FzK, FzR, Fyw, Fxw = np.linalg.solve(A, r)
            fz = {w["id"]: (FzK if w["side"] < 0 else FzR) for w in wheels}
            tot = sum(fz.values())
            w_new = {k: v / tot for k, v in fz.items()}
            if max(abs(w_new[k] - w_h[k]) for k in w_h) < 1e-9:
                break
            w_h = w_new
        contact = {}
        for w in wheels:
            k = w["id"]
            dz = 0.0
            if twist_n:
                sign = (-1 if w["side"] < 0 else 1) * (1 if w["axle"] == "front" else -1)
                dz = sign * twist_n
            contact[k] = np.array([w_h[k] * Fxw, w_h[k] * Fyw, fz[k] + dz])
        return dict(ball=np.array([0.0, Fby, Fbz]), contact=contact)

    def arm_loads(self, items: list[Item], acc, contact: dict, q: np.ndarray) -> dict:
        """Solve each arm as a free body about its hinge and put the hinge and airbag forces on the frame."""
        a = np.asarray(acc, float) * G
        out = {}
        for w in self.ch.suspension:
            P = np.asarray(w["pivot"], float)
            un = [(it.m * a, np.asarray(it.p, float) - P) for it in items if it.rule == "unsprung" and it.wheel == w["id"]]
            Wu = sum((F for F, _ in un), np.zeros(3))
            Mu = sum((np.cross(r, F) for F, r in un), np.zeros(3))
            C = contact[w["id"]]
            rC = np.asarray(w["contact"]) - P
            rB = np.asarray(w["airbag"]) - P
            m_y = np.cross(rC, C)[1] + Mu[1]
            Fb = -m_y / rB[0]                         # airbag force on the chassis, + up
            Fbag_arm = np.array([0.0, 0.0, -Fb])
            H_arm = -(C + Wu + Fbag_arm)
            M_arm = -(np.cross(rC, C) + Mu + np.cross(rB, Fbag_arm))
            M_arm[1] = 0.0
            self._apply(-H_arm, P, [(self.fm.pivot_nodes[w["id"]], 1.0)], q, M=-M_arm)
            self._apply(np.array([0.0, 0.0, Fb]), w["airbag"], self.fm.rail_fractions(w["side"], w["airbag"][0]), q)
            out[w["id"]] = dict(contact=C, airbag=Fb, hinge=-H_arm, hinge_moment=-M_arm)
        return out

    # ------------------------------------------------------------------ cases
    def scaled_cases(self, ids=None):
        out = []
        for c in self.tr.cases:
            if ids and c.id not in ids:
                continue
            items = self.items(c)
            m = sum(it.m for it in items)
            out.append((c, items, m))
        # one factor for every case, so the heaviest case sits at the plated ATM and the others keep their proportion
        k = max(1.0, self.atm / max(m for _, _, m in out))
        return [(c, [Item(it.id, it.name, it.m * k, it.p, it.rule, it.wheel) for it in items], m, k) for c, items, m in out]

    def run_static(self, items, acc, twist_n=0.0, steady_n=0.0, lifted=None):
        q = self.sprung_loads(items, acc)
        R = self.reactions(items, acc, twist_n=twist_n, lifted=lifted)
        self._apply(R["ball"], (0.0, 0.0, self.ch.V["coupling_z"]), [(self.fm.ball, 1.0)], q)
        arms = self.arm_loads(items, acc, R["contact"], q)
        if lifted is not None:
            F, p = R["pad"]
            cm = next(m.id for m in self.ch.members if m.station == "XT centre" and m.role.startswith("cm"))
            self._apply(F, p, self.fm.crossmember_fractions(cm, p[1]), q)
        if steady_n:
            V = self.ch.V
            # each steady at 90 degrees under its bracket, one diagonal up and one down. The couple balances in roll, so a
            # pair standing wider than the other takes its share of the wound steady's load in the ratio of the widths
            poses = self.ch.steady_poses()
            ref = min(abs(p["y"]) for p in poses)
            for p in poses:
                F = np.array([0.0, 0.0, p["twist"] * steady_n * ref / abs(p["y"])])
                self._apply(F, (p["x"], p["y"], V["rail_underside_z"]), self.fm.rail_fractions(p["side"], p["x"]), q)
        res = self.kinematic.solve(q)
        resid = max(abs(v) for v in res.reactions.values())
        return res, dict(ball=R["ball"], arms=arms, residual_n=resid, pad=R.get("pad", [None])[0])

    def run_body(self, F, p, fractions):
        q = np.zeros(self.n)
        self._apply(np.asarray(F, float), p, fractions, q)
        return self.body.solve(q)

    # ------------------------------------------------------------------ stress
    def stresses(self, res) -> dict[str, dict]:
        """Peak stress in each member: normal stress (axial plus both bending axes at a corner), shear from torsion
        and the wall shear, combined as sqrt(sigma^2 + 3 tau^2)."""
        out = {}
        nodes = self.f.nodes
        for el, fl in zip(self.f.elements, res.forces):
            if el.sec.rigid or el.member in ("BODY", "BODY-MOUNT"):
                continue
            sp = self.fm.sec_props[el.member]
            for end, act in zip((el.i, el.j), end_actions(fl)):
                if isinstance(sp, Composite):
                    A, Zs, Zw, C, Awd, Aww = sp.A, sp.Z_strong, sp.Z_weak, sp.C, sp.Aw, sp.rail.Aw_width + sp.raiser.Aw_width
                else:
                    A, Zs, Zw, C, Awd, Aww = sp.A, sp.Z_strong, sp.Z_weak, sp.C, sp.Aw_depth, sp.Aw_width
                sig = abs(act["N"]) / A + abs(act["My"]) / Zs + abs(act["Mz"]) / Zw
                tau = abs(act["T"]) / C + max(abs(act["Vz"]) / Awd, abs(act["Vy"]) / Aww)
                eq = math.sqrt(sig ** 2 + 3 * tau ** 2)
                r = out.get(el.member)
                if r is None or eq > r["eq"]:
                    out[el.member] = dict(eq=eq, sigma=sig, tau=tau, at=tuple(round(v) for v in nodes[end]),
                                          N=act["N"], M_strong=act["My"], M_weak=act["Mz"], T=act["T"])
        return out

    def normal_at(self, res, member: str, x: float | None = None, end: str | None = None) -> float:
        """Normal stress (no torsion) in a member: at the end nearest X, at its rail ends, or the largest anywhere."""
        best, bd = 0.0, math.inf
        nodes = self.f.nodes
        for el, fl in zip(self.f.elements, res.forces):
            if el.member != member:
                continue
            sp = self.fm.sec_props[member]
            for nd, act in zip((el.i, el.j), end_actions(fl)):
                sig = abs(act["N"]) / sp.A + abs(act["My"]) / sp.Z_strong + abs(act["Mz"]) / sp.Z_weak
                if x is None:
                    best = max(best, sig)
                else:
                    d = abs(nodes[nd][0] - x)
                    if d < bd - 1e-6 or (abs(d - bd) < 1e-6 and sig > best):
                        best, bd = sig, d
        return best

    def normal_at_level(self, res, member: str, x: float, z: float) -> float:
        """Normal stress in the composite rail at height z (a weld along the seam), at the end nearest X."""
        sp = self.fm.sec_props[member]
        best, bd = 0.0, math.inf
        for el, fl in zip(self.f.elements, res.forces):
            if el.member != member:
                continue
            for nd, act in zip((el.i, el.j), end_actions(fl)):
                sig = abs(act["N"]) / sp.A + abs(act["My"]) * abs(z - sp.z_centroid) / sp.I_strong + abs(act["Mz"]) / sp.Z_weak
                d = abs(self.f.nodes[nd][0] - x) if x is not None else 0.0
                if x is None:
                    best = max(best, sig)
                elif d < bd - 1e-6 or (abs(d - bd) < 1e-6 and sig > best):
                    best, bd = sig, d
        return best

    def member_end_stress(self, res, member: str) -> float:
        """Normal stress at the ends of a member's element chain (where it is welded to the rail or raiser)."""
        els = [(el, fl) for el, fl in zip(self.f.elements, res.forces) if el.member == member]
        sp = self.fm.sec_props[member]
        vals = []
        for k, (el, fl) in ((0, els[0]), (1, els[-1])):
            act = end_actions(fl)[k]
            vals.append(abs(act["N"]) / sp.A + abs(act["My"]) / sp.Z_strong + abs(act["Mz"]) / sp.Z_weak)
        if self.ch.members and next(m for m in self.ch.members if m.id == member).role == "outrigger":
            return vals[0]
        return max(vals)

    # ------------------------------------------------------------------ the whole analysis
    def run(self) -> dict:
        ch, V = self.ch, self.ch.V
        lcs = {lc["id"]: lc for lc in ch.data["load_cases"]}
        fy = ch.fy
        # each member against its own grade. The rails act with their raisers as one section, so they take the lower fy
        fy_of = {m.id: (min(m.sec.fy, ch.role_sec["raiser"].fy) if m.role == "rail" else m.sec.fy) for m in ch.members}
        cases = self.scaled_cases()
        env: dict[str, dict] = {}
        self.resid = 0.0
        sites = self.hole_sites()
        hole_env: dict[str, dict] = {}

        def take(lc_id, res, label, extra=None):
            for mem, r in self.stresses(res).items():
                e = env.setdefault(lc_id, {})
                if mem not in e or r["eq"] > e[mem]["eq"]:
                    e[mem] = dict(r, case=label, **(extra or {}))
            he = hole_env.setdefault(lc_id, {})
            for k, h in enumerate(sites):
                if h.get("open"):
                    continue
                eq = self.hole_stress(res, h)["eq"]
                if k not in he or eq > he[k]["eq"]:
                    he[k] = dict(eq=eq, case=label)

        lc1 = {}
        defl = {}
        twist = {}
        balls = {}
        for c, items, m0, k in cases:
            for lc_id in ("LC1", "LC2", "LC3", "LC4"):
                for j, acc in enumerate(lcs[lc_id]["accel"]):
                    res, info = self.run_static(items, acc)
                    self.resid = max(self.resid, info["residual_n"])
                    take(lc_id, res, f"{c.id}" + (f" ({'+' if acc[1] > 0 else '-'}Y)" if acc[1] else ""))
                    if lc_id == "LC1":
                        lc1[c.id] = res
                        defl[c.id] = self.deflections(res)
                        balls[c.id] = dict(ball_kg=info["ball"][2] / G, scale=k, model_kg=m0)
            lc = lcs["LC5a"]
            hub_y = ch.suspension[0]["contact"][1]
            for sgn in (1, -1):
                res, info = self.run_static(items, lc["accel"][0], twist_n=sgn * lc["torque_nmm"] / (2 * abs(hub_y)))
                self.resid = max(self.resid, info["residual_n"])
                take("LC5a", res, f"{c.id} (diagonal {'A' if sgn > 0 else 'B'})")
                t = self.twist(res)
                if t > twist.get("deg", -1):
                    twist = dict(deg=t, case=f"{c.id} (diagonal {'A' if sgn > 0 else 'B'})")
            for side in (-1, 1):
                res, info = self.run_static(items, lcs["LC8b"]["accel"][0], lifted=side)
                self.resid = max(self.resid, info["residual_n"])
                pad = float(info["pad"][2])
                take("LC8b", res, f"{c.id}, {'kerb' if side < 0 else 'road'} side jacked", dict(pad_n=pad))
                env["LC8b"].setdefault("_pad", dict(eq=0.0))
                if pad > env["LC8b"]["_pad"].get("pad_n", 0):
                    env["LC8b"]["_pad"] = dict(eq=0.0, pad_n=pad, case=f"{c.id}, {'kerb' if side < 0 else 'road'} side")
        # LC5b at tare, unscaled
        tc1 = next(c for c in self.tr.cases if c.id == "TC1")
        lc = lcs["LC5b"]
        res, info = self.run_static(self.items(tc1), lc["accel"][0], steady_n=lc["steady_kg"] * G)
        self.resid = max(self.resid, info["residual_n"])
        take("LC5b", res, "TC1 tare, one steady wound to 875 kg")
        # LC6 at the coupling, LC6b at each chain lug, LC8a at each recovery point
        ball_p = (0.0, 0.0, V["coupling_z"])
        lc6 = {}
        for F in lcs["LC6"]["forces_n"]:
            res = self.run_body(F, ball_p, [(self.fm.ball, 1.0)])
            lab = f"{_dir(F)} {max(abs(v) for v in F) / 1000:.1f} kN"
            take("LC6", res, lab)
            lc6[lab] = res
        for s in (-1, 1):
            lug = (V["chain_lug_x"], s * (ch.db_y(V["chain_lug_x"]) + 30), V["db_z"] - 60)
            for F in lcs["LC6b"]["forces_n"]:
                res = self.run_body(F, lug, [(self.fm.db_node(s, V["chain_lug_x"]), 1.0)])
                take("LC6b", res, f"{'kerb' if s < 0 else 'road'}-side lug, {_dir(F)} {max(abs(v) for v in F) / 1000:.1f} kN")
        Fr = lcs["LC8a"]["force_n"]
        for where, x, sx in (("front", V["front_recovery_x"], -1), ("rear", V["body_x1"] - 70, 1)):
            for s in (-1, 1):
                y = s * (V["rail_c"] + 35) if where == "front" else s * (V["rail_c"] - 35)
                p = (x, y, V["db_z"] if where == "front" else V["rail_underside_z"] + 75)
                fr = [(self.fm.db_node(s, x), 1.0)] if where == "front" else self.fm.rail_fractions(s, x)
                for h in (-30, 0, 30):
                    for v in (-15, 0, 15):
                        F = Fr * np.array([sx * math.cos(math.radians(h)) * math.cos(math.radians(v)),
                                           math.sin(math.radians(h)) * math.cos(math.radians(v)), math.sin(math.radians(v))])
                        res = self.run_body(F, p, fr)
                        take("LC8a", res, f"{where} {'kerb' if s < 0 else 'road'}-side point, {h:+d} deg sideways, {v:+d} deg up")
        out = dict(envelope={}, governing={}, deflections={}, twist=twist, balls=balls, residual_n=self.resid,
                   frame=dict(nodes=len(self.f.nodes), elements=sum(1 for e in self.f.elements if not e.sec.rigid),
                              rigid_links=sum(1 for e in self.f.elements if e.sec.rigid)))
        for lc_id, e in env.items():
            fac = lcs[lc_id]["factor"]
            rows = {m: dict(r, util=r["eq"] / (fy_of.get(m, fy) / fac), fy=fy_of.get(m, fy)) for m, r in e.items() if not m.startswith("_")}
            out["envelope"][lc_id] = rows
            g = max(rows.items(), key=lambda kv: kv[1]["util"])
            out["governing"][lc_id] = dict(member=g[0], **g[1], limit=g[1]["fy"] / fac, factor=fac)
        out["pad_n"] = env["LC8b"]["_pad"]
        out["deflections"] = self._worst_deflections(defl)
        out["fatigue"] = self.fatigue(lc1)
        out["holes"] = self.holes(hole_env, lc1, sites)
        out["local"] = self.local_checks(out["pad_n"]["pad_n"])
        out["fixings"] = self.fixings()
        out["cross_checks"] = self.cross_checks(out, lc6)
        out["lc1_ball"] = balls
        return out

    # ------------------------------------------------------------------ deflection and twist
    def _w(self, res, node):
        return res.u[6 * node + 2]

    def deflections(self, res) -> dict:
        ch, V, fm = self.ch, self.ch.V, self.fm
        xf, xr = ch.hub_x("front"), ch.hub_x("rear")
        out = dict(span=0.0, tip=0.0, outrigger=0.0)
        for s in (-1, 1):
            xs, nodes = fm.rail_x, fm.rail_nodes[s]
            w = {x: self._w(res, n) for x, n in zip(xs, nodes)}
            wf = np.interp(xf, xs, [w[x] for x in xs])
            wr = np.interp(xr, xs, [w[x] for x in xs])
            w0 = w[xs[0]]
            for x in xs:
                if xs[0] <= x <= xf:
                    out["span"] = max(out["span"], abs(w[x] - (w0 + (wf - w0) * (x - xs[0]) / (xf - xs[0]))))
            line = wf + (wr - wf) * (xs[-1] - xf) / (xr - xf)
            out["tip"] = max(out["tip"], abs(w[xs[-1]] - line))
        for (sid, s), nodes in fm.out_nodes.items():
            x = fm.station_nodes[sid]
            out["outrigger"] = max(out["outrigger"], abs(self._w(res, nodes[-1][1]) - self._w(res, fm.rail_node(s, x))))
        return out

    def _worst_deflections(self, defl) -> dict:
        V = self.ch.V
        lim = dict(span=(self.ch.hub_x("front") - V["body_x0"]) / 500, tip=(V["body_x1"] - V["axle_x"]) / 300, outrigger=2.0)
        out = {}
        for k in ("span", "tip", "outrigger"):
            cid = max(defl, key=lambda c: defl[c][k])
            out[k] = dict(mm=defl[cid][k], limit_mm=lim[k], case=cid)
        return out

    def twist(self, res) -> float:
        ch, fm, V = self.ch, self.fm, self.ch.V
        st = {s["id"]: ch.station_x(s) for s in ch.stations}

        def theta(x):
            return (self._w(res, fm.rail_node(1, x)) - self._w(res, fm.rail_node(-1, x))) / (2 * V["rail_c"])
        return abs(math.degrees(theta(st["XT front hinge"]) - theta(st["XT rear shock"])))

    # ------------------------------------------------------------------ fatigue (LC10)
    def fatigue(self, lc1: dict) -> list[dict]:
        ch, V = self.ch, self.ch.V
        pos = ch.positions()
        lc = next(l for l in ch.data["load_cases"] if l["id"] == "LC10")
        throat = ch.data["fillet_throat"]
        cms = [m for m in ch.members if m.role.startswith("cm")]
        groups = {"crossmember": cms, "outrigger": [m for m in ch.members if m.role == "outrigger"],
                  "brace": [m for m in ch.members if m.role == "brace"],
                  "hinge_crossmember": [m for m in cms if m.station in ("XT front hinge", "XT centre")],
                  "jack_crossmember": [m for m in cms if m.station == "XT centre"]}

        def xs_of(where):
            if where == "all":
                return [None]
            if isinstance(where, str):
                v = pos[where]
                return list(v) if isinstance(v, list) else [v]
            return [pos[v] if isinstance(v, str) else v for v in where]

        def candidates(d, res):
            k = d["stress"]
            out = []
            if k == "rail_extreme":
                for s in (-1, 1):
                    for x in xs_of(d["where"]):
                        out.append((self.normal_at(res, f"RL-{SIDES[s]}", x), f"RL-{SIDES[s]}" + (f" at X {x:.0f}" if x else "")))
            elif k == "rail_level":
                z = self.ch.ev(d["z"])
                for s in (-1, 1):
                    for x in xs_of(d["where"]):
                        out.append((self.normal_at_level(res, f"RL-{SIDES[s]}", x, z), f"RL-{SIDES[s]}" + (f" at X {x:.0f}" if x else "")))
            elif k == "cm_toe_in_rail":
                # the end weld's toe on the rail web sits just inside the rail's (or raiser's) corner radius
                for m in (c for c in cms if c.role in d["roles"]):
                    if m.role in ("cm_xt", "cm_end"):
                        z = V["rail_underside_z"] + ch.role_sec["rail"].ro
                    else:
                        z = V["raiser_top_z"] - ch.role_sec["raiser"].ro
                    for s in (-1, 1):
                        out.append((self.normal_at_level(res, f"RL-{SIDES[s]}", m.p0[0], z), f"RL-{SIDES[s]} at {m.id}"))
            elif k == "member_at":
                for s in (-1, 1):
                    for x in xs_of(d["x"]):
                        if abs(x - V["body_x0"]) < 1:
                            mems = [f"DB-{SIDES[s]}A", f"DB-{SIDES[s]}B"]
                        else:
                            mems = [f"DB-{SIDES[s]}A" if x < V["body_x0"] else f"DB-{SIDES[s]}B"]
                        out.append((max(self.normal_at(res, m, x) for m in mems), f"DB-{SIDES[s]} at X {x:.0f}"))
            else:
                for m in groups[d["member"]]:
                    sig = self.member_end_stress(res, m.id)
                    if k == "weld_root":
                        sig *= m.sec.t / throat.get(m.role, throat["default"])
                    out.append((sig, m.id))
            return out

        out = []
        for d in ch.data["fatigue_details"]:
            best = (0.0, "", "")
            for cid, res in lc1.items():
                s, where = max(candidates(d, res))
                if s > best[0]:
                    best = (s, where, cid)
            ds, where, cid = best
            cafl = 0.585 * d["fat"]
            ds_o = lc["occasional_factor"] * ds
            if ds_o <= cafl:
                N = math.inf
            elif 2e6 * (d["fat"] / ds_o) ** 3 <= 1e7:
                N = 2e6 * (d["fat"] / ds_o) ** 3
            else:
                N = 1e7 * (cafl / ds_o) ** 22
            D = lc["occasional_cycles"] / N if N != math.inf else 0.0
            out.append(dict(id=d["id"], name=d["name"], iiw=d["iiw"], fat=d["fat"], cafl=cafl, range_mpa=ds, where=where, case=cid,
                            occasional_range_mpa=ds_o, damage=D, ok=ds <= cafl and D <= lc["miner_limit"],
                            hot_spot=bool(d.get("hot_spot"))))
        return out

    # ------------------------------------------------------------------ holes in the members (CHS-09, CHS-10)
    def hole_sites(self) -> list[dict]:
        """Each hole a run makes in a rail or a raiser (data/services.yaml `holes`), once: a hole through the seam of a rail
        and its raiser is one hole in two walls, and an outrigger's root face is the raiser's outer web. Each carries its
        wall, its net section in the composite rail, its edge distance and its clear distance to the nearest weld toe.
        An outrigger's open end under a side marker's cap has no wall."""
        import yaml
        from .partsdb import DATA
        ch, V, comp = self.ch, self.ch.V, self.ch.comp
        rail, raiser = comp.rail, comp.raiser
        rules = ch.data["hole_rules"]
        rows = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8")).get("holes") or []
        toes = ch.weld_toes()
        z0, zs, z1 = V["rail_underside_z"], V["rail_top_z"], V["raiser_top_z"]
        sites: list[dict] = []
        for r in rows:
            s = 1 if r["y"] > 0 else -1
            yc = s * V["rail_c"]
            face, member = r["face"], r["member"]
            outer = face == ("road side" if s > 0 else "kerb side")
            if member.startswith("OR-"):
                if abs(abs(r["y"]) - V["outrigger_tip_y"]) < 5:
                    sites.append(dict(r, runs=[r["run"]], wall="the outrigger's open end, under the side marker's cap", open=True))
                    continue
                member, face, outer = f"RS-{SIDES[s]}", "road side" if s > 0 else "kerb side", True
            same = next((h for h in sites if not h.get("open") and abs(h["x"] - r["x"]) < 5 and abs(h["y"] - r["y"]) < 5
                         and abs(h["z"] - r["z"]) < 5 and h["frame"] == f"RL-{SIDES[s]}"), None)
            if same is not None:
                same["runs"] = sorted(set(same["runs"]) | {r["run"]})
                same["rows"].append(f"{r['member']} {r['face']}")
                continue
            in_rail = member.startswith("RL-")
            tube, zb, zt = (rail, z0, zs) if in_rail else (raiser, zs, z1)
            fu = rules["fu"]["rail" if in_rail else "raiser"]
            d, L = float(r["d"]), float(r["length"])
            if face in ("top", "bottom"):
                seam = (in_rail and face == "top") or (not in_rail and face == "bottom")
                if seam:
                    fu = min(rules["fu"].values())
                    walls = [(rail, zs - rail.t / 2), (raiser, zs + raiser.t / 2)]
                    wall, z_fibre = "the seam of the rail and its raiser, through both walls", zs
                    half = min(rail.b / 2 - rail.ro, raiser.b / 2 - raiser.ro)
                else:
                    walls = [(tube, zb + tube.t / 2 if face == "bottom" else zt - tube.t / 2)]
                    wall = "the rail's bottom face" if in_rail else "the raiser's top face"
                    z_fibre, half = (zb if face == "bottom" else zt), tube.b / 2 - tube.ro
                strips = [dict(dA=t.t * d, z=z, own=d * t.t ** 3 / 12, y=abs(r["y"] - yc), own_z=t.t * d ** 3 / 12, web=False) for t, z in walls]
                edge = half - abs(r["y"] - yc)
                hole_box = (r["x"] - L / 2, r["y"] - d / 2, r["z"] - 1, r["x"] + L / 2, r["y"] + d / 2, r["z"] + 1)
                z_lever_pts, y_lever = [z_fibre], abs(r["y"] - yc) + d / 2
                face_w = min(t.b - t.t for t, _ in walls)          # the wall's width on its centreline, corners included
            else:
                wall = f"the {'rail' if in_rail else 'raiser'}'s {'outer' if outer else 'inner'} web"
                y_off = (tube.b - tube.t) / 2
                strips = [dict(dA=tube.t * d, z=r["z"], own=tube.t * d ** 3 / 12, y=y_off, own_z=d * tube.t ** 3 / 12, web=True)]
                edge = min(r["z"] - (zb + tube.ro), (zt - tube.ro) - r["z"])
                hole_box = (r["x"] - L / 2, r["y"] - 1, r["z"] - d / 2, r["x"] + L / 2, r["y"] + 1, r["z"] + d / 2)
                z_lever_pts, y_lever = [r["z"] - d / 2, r["z"] + d / 2], max(rail.b, raiser.b) / 2
                face_w = tube.d - tube.t
            A = comp.A - sum(p["dA"] for p in strips)
            zc = (comp.A * comp.z_centroid - sum(p["dA"] * p["z"] for p in strips)) / A
            I = comp.I_strong + comp.A * (zc - comp.z_centroid) ** 2 - sum(p["own"] + p["dA"] * (p["z"] - zc) ** 2 for p in strips)
            Iw = comp.I_weak - sum(p["own_z"] + p["dA"] * p["y"] ** 2 for p in strips)
            Aw = comp.Aw - sum(p["dA"] for p in strips if p["web"])
            Aww = rail.Aw_width + raiser.Aw_width - sum(p["dA"] for p in strips if not p["web"])
            gap, weld = min(((_box_gap(hole_box, bx), what) for what, bx in toes), key=lambda t: t[0])
            sites.append(dict(r, runs=[r["run"]], rows=[f"{r['member']} {r['face']}"], frame=f"RL-{SIDES[s]}", wall=wall, open=False,
                              d=d, length=L, fu=fu, box=hole_box, edge_mm=edge, edge_need=rules["edge_factor"] * d, toe_mm=gap, toe_need=rules["toe_factor"] * d,
                              toe_weld=weld, net=dict(A=A, I=I, I_weak=Iw, Aw=Aw, Aw_width=Aww, z_lever=max(abs(z - zc) for z in z_lever_pts),
                                                      y_lever=y_lever, k_torsion=face_w / max(face_w - d, 1.0))))
        walled = [h for h in sites if not h.get("open")]
        for h in walled:
            # the member's sawn ends are edges too (AS 4100 Table 9.6.2, 1.5 d), and two holes keep the larger one's diameter
            # between their edges, as a weld toe does (Kirsch)
            end = min(h["x"] - V["body_x0"], V["body_x1"] - h["x"]) - (h["length"] - h["d"]) / 2
            if end < rules["end_factor"] / rules["edge_factor"] * h["edge_mm"]:
                h["edge_mm"], h["edge_need"] = end, rules["end_factor"] * h["d"]
            others = [(_box_gap(h["box"], o["box"]), o) for o in walled if o is not h and o["frame"] == h["frame"]]
            if others:
                g, o = min(others, key=lambda t: t[0])
                need = rules["toe_factor"] * max(h["d"], o["d"])
                if g - need < h["toe_mm"] - h["toe_need"]:
                    h["toe_mm"], h["toe_need"], h["toe_weld"] = g, need, f"hole for {', '.join(o['runs'])}"
        for k, h in enumerate(sites, 1):
            h["id"] = f"H-{k:02d}"
        return sites

    def hole_stress(self, res, h) -> dict:
        """Normal and combined stress at a hole's edge on the composite rail's net section, at the element end nearest it."""
        best, bd = None, math.inf
        for el, fl in zip(self.f.elements, res.forces):
            if el.member != h["frame"]:
                continue
            for nd, act in zip((el.i, el.j), end_actions(fl)):
                dist = abs(self.f.nodes[nd][0] - h["x"])
                if dist < bd - 1e-6 or (abs(dist - bd) < 1e-6 and abs(act["My"]) > abs(best["My"])):
                    best, bd = act, dist
        n, comp = h["net"], self.ch.comp
        y_max = max(comp.rail.b, comp.raiser.b) / 2
        sig = (abs(best["N"]) / n["A"] + abs(best["My"]) * n["z_lever"] / n["I"]
               + abs(best["Mz"]) / comp.Z_weak * (comp.I_weak / n["I_weak"]) * (n["y_lever"] / y_max))
        tau = abs(best["T"]) / comp.C * n["k_torsion"] + max(abs(best["Vz"]) / n["Aw"], abs(best["Vy"]) / n["Aw_width"])
        return dict(sigma=sig, eq=math.sqrt(sig ** 2 + 3 * tau ** 2))

    def holes(self, env: dict, lc1: dict, sites: list[dict]) -> list[dict]:
        """CHS-09 and CHS-10 at each hole: the worst net-section stress of LC1 to LC8b against each case's limit, the
        frequent range at the hole's edge with Kirsch's factor against IIW no. 121's CAFL, the edge and toe distances."""
        ch = self.ch
        rules = ch.data["hole_rules"]
        lcs = {l["id"]: l for l in ch.data["load_cases"]}
        lc10 = lcs["LC10"]
        fy = min(ch.role_sec["rail"].fy, ch.role_sec["raiser"].fy)          # the composite rail's checks use the raiser's fy
        out = []
        for k, h in enumerate(sites):
            row = {key: h[key] for key in ("id", "member", "face", "x", "y", "z", "d", "length", "runs", "wall", "open") if key in h}
            if h.get("open"):
                out.append(dict(row, ok=True, static_ok=True, place_ok=True, util=0.0))
                continue
            worst = None
            for lc_id, e in env.items():
                r = e.get(k)
                if r is None:
                    continue
                lim = min(fy, rules["fu_factor"] * h["fu"]) / lcs[lc_id]["factor"]
                u = r["eq"] / lim
                if worst is None or u > worst["util"]:
                    worst = dict(util=u, mpa=r["eq"], limit=lim, lc=lc_id, case=r["case"])
            ds, cid = max(((self.hole_stress(res, h)["sigma"], c) for c, res in lc1.items()), key=lambda t: t[0])
            peak = rules["kt"] * ds
            cafl = 0.585 * rules["fat"]
            dmg = _miner(rules["fat"], lc10["occasional_factor"] * peak, lc10)
            fat_ok = peak <= cafl and dmg <= lc10["miner_limit"]
            edge_ok, toe_ok = h["edge_mm"] >= h["edge_need"] - 1e-6, h["toe_mm"] >= h["toe_need"] - 1e-6
            out.append(dict(row, rows=h["rows"], frame=h["frame"], static=worst, static_ok=worst["util"] <= 1 + 1e-9, util=worst["util"],
                            range_mpa=ds, peak_mpa=peak, cafl=cafl, damage=dmg, fat_case=cid, fat_ok=fat_ok,
                            edge_mm=h["edge_mm"], edge_need=h["edge_need"], edge_ok=edge_ok, toe_mm=h["toe_mm"], toe_need=h["toe_need"],
                            toe_weld=h["toe_weld"], toe_ok=toe_ok, place_ok=edge_ok and toe_ok and fat_ok,
                            ok=worst["util"] <= 1 + 1e-9 and edge_ok and toe_ok and fat_ok))
        return out

    # ------------------------------------------------------------------ fittings
    def local_checks(self, pad_n: float) -> dict:
        ch, V = self.ch, self.ch.V
        mat = ch.data["material"]
        fyp, fup = mat["plate_fy"], mat["plate_fu"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        lcs = {l["id"]: l for l in ch.data["load_cases"]}
        L = ch.data["local_checks"]
        fit = {f["id"]: f for f in ch.data["fittings"]}
        out = {}
        # chain lugs, VSB1 9.2.2, in the plane of the lug
        c = L["chain_lug"]
        t = fit[c["fitting"]]["t"]
        a = 0.7 * c["weld_leg"]
        rows = []
        f_along = max(abs(f[0]) for f in lcs["LC6b"]["forces_n"])
        f_up = max(abs(f[2]) for f in lcs["LC6b"]["forces_n"])
        for F in (f_along, f_up):
            Ip = 2 * (c["weld_l"] ** 3 / 12 + c["weld_l"] * (c["weld_h"] / 2) ** 2)
            rmax = math.hypot(c["weld_l"] / 2, c["weld_h"] / 2)
            q = F / (2 * c["weld_l"]) + F * c["ecc"] * rmax / Ip
            rows += [("net tension", F / ((c["net_w"] - c["hole"]) * t), fyp), ("bearing", F / (c["pin"] * t), 1.5 * fyp),
                     ("tear-out", F / (2 * t * (c["edge"] - c["hole"] / 2)), 0.6 * fyp), ("weld", q / a, wcap)]
        out["chain_lug"] = _local("Chain lug, 10 mm (CH-P02)", rows,
                                  f"{f_along / 1000:.1f} kN longitudinal and {f_up / 1000:.1f} kN vertical, each in the lug's plane")
        # recovery points, LC8a, the worst direction: 30 degrees sideways is out of the plate's plane
        for key, name in (("front_recovery", "Front recovery lug, 20 mm (CH-P04)"), ("rear_recovery", "Rear recovery tongue, 20 mm (CH-P05)")):
            c = L[key]
            t = fit[c["fitting"]]["t"]
            a = 0.7 * c["weld_leg"]
            rows = []
            pull, ult = lcs["LC8a"]["force_n"], lcs["LC8a"]["ultimate_n"]
            for F, lim_p, lim_w, lab in ((pull, fyp, wcap, f"{pull / 1000:.1f} kN"), (ult, fup, 0.6 * mat["weld_fuw"], f"{ult / 1000:.1f} kN ultimate")):
                Fin, Flat = F * math.cos(math.radians(30)), F * math.sin(math.radians(30))
                sig = Fin / ((c["net_w"] - c["hole"]) * t) + Flat * c["lever"] / (c["net_w"] * t ** 2 / 6)
                q = math.hypot(Fin, Flat) / (2 * c["weld_l"]) + Flat * c["lever"] / (t + a) / c["weld_l"]
                rows += [(f"plate, {lab}", sig, lim_p), (f"bearing, {lab}", F / (c["pin"] * t), 1.5 * lim_p),
                         (f"tear-out, {lab}", F / (2 * t * (c["edge"] - c["hole"] / 2)), 0.6 * lim_p), (f"weld, {lab}", q / a, lim_w)]
            out[key] = _local(name, rows, f"{pull / 1000:.1f} kN within 30 degrees sideways and 15 degrees up or down, {ult / 1000:.1f} kN without fracture")
        # jacking pads, LC8b
        c = L["jacking_pad"]
        rail = ch.role_sec["rail"]
        t = fit[c["fitting"]]["t"]
        F = max(pad_n, lcs["LC8b"]["pad_n"])
        bb = fit[c["fitting"]]["l"] + 5 * rail.t
        rows = [("rail web bearing", F / (2 * rail.t * bb), rail.fy), ("pad bending between the webs", F * c["span"] / 8 / (fit[c["fitting"]]["w"] * t ** 2 / 6), fyp)]
        out["jacking_pad"] = _local("Jacking pad, 10 mm (CH-P06)", rows,
                                    f"{F / 1000:.1f} kN on one pad (the larger of LC8b's {lcs['LC8b']['pad_n'] / 1000:.1f} kN at the plate and the frame analysis)")
        # spare carrier posts, 4 g on the fixing (LC2) and the LC7 forward case
        c = L["spare_posts"]
        post = next(m for m in ch.members if m.role == "spare_post")
        spare_kg = sum(b.mass_kg for b in self.lay.blocks if b.system == "spare" and b.id != "SP-03")
        hz = V["spare_z"] - post.p0[2]
        M4 = 4 * spare_kg * G * c["lever_x"] / 2
        M7 = 1.6 * spare_kg * G * hz / 2
        rows = [("post base, 4 g vertical", M4 / post.sec.Z_strong, post.sec.fy), ("post base, 1.6 g forward", M7 / post.sec.Z_strong, post.sec.fy / 1.5)]
        out["spare_posts"] = _local("Spare carrier posts, SHS 50 x 50 x 2.5", rows, f"the {spare_kg:.1f} kg wheel and tyre, 155 mm ahead of the posts")
        # corner steady brackets: at 90 degrees the steady's rating goes up through ARK's bracket, welded along the rail's
        # bottom corners only, into the rail's two webs. The pairs' brackets lie differently, so each pair's welds differ
        c = L["steady_bracket"]
        F = c["steady_kg"] * G
        a = 0.7 * ch.data["steadies"]["weld_leg"]
        rows = []
        for p in ch.steady_poses()[::2]:
            lw = p["weld_l"]
            y0, y1 = abs(p["bracket"][1]), abs(p["bracket"][4])
            webs = sum(min(y0, y1) <= V["rail_c"] + k * (rail.b - rail.t) / 2 <= max(y0, y1) for k in (-1, 1))   # the webs over it
            rows += [(f"{p['pair']} welds, 2 x {lw:g} mm", F / (2 * lw * a), wcap),
                     (f"{p['pair']} {'webs' if webs > 1 else 'web'} bearing, {lw:g} mm", F / (webs * rail.t * (lw + 5 * rail.t)), rail.fy / 1.5)]
        out["steady_bracket"] = _local("Corner steady bracket, ARK's (CH-B01)", rows,
                                       f"the steady's {c['steady_kg']:.0f} kg rating at 90 degrees, its bracket welded under the rail")
        out["coupling_plate"] = self.coupling_plate(lcs, fit, fyp)
        return out

    def coupling_plate(self, lcs: dict, fit: dict, fyp: float) -> dict:
        """The coupling's bolts and its plate under LC6 (AS 4100 9.3.2): the pull or the thrust shears the bolts and, on its
        lever down to the plate's face, lifts one row or one side in tension, with the vertical force's share added."""
        c = self.ch.data["local_checks"]["coupling_plate"]
        t = fit[c["fitting"]]["t"]
        along = max(abs(f[0]) for f in lcs["LC6"]["forces_n"])
        across = max(abs(f[1]) for f in lcs["LC6"]["forces_n"])
        up = max(abs(f[2]) for f in lcs["LC6"]["forces_n"])
        n, d = c["bolts"], c["bolt_d"]
        shear_lim, tension_lim = 0.8 * 0.62 * c["bolt_fuf"], 0.8 * c["bolt_fuf"]
        v = max(along, across) / n
        tens = max(along * c["lever"] / c["row_pitch"], across * c["lever"] / c["col_pitch"]) / (n / 2) + up / n
        inter = math.hypot(v / c["bolt_ac"] / shear_lim, tens / c["bolt_as"] / tension_lim)
        rows = [("bolt shear, the pull", v / c["bolt_ac"], shear_lim), ("bolt tension, the pull on its lever and the vertical force", tens / c["bolt_as"], tension_lim),
                ("bolt, shear and tension together", inter * tension_lim, tension_lim), ("plate bearing at a bolt", v / (d * t), 3.2 * 0.9 * fyp)]
        return _local(f"Coupling plate, {t:g} mm, and {n} x M{d:g} 8.8 bolts (CH-P01)", rows,
                      f"{along / 1000:.1f} kN along, {across / 1000:.1f} kN across and {up / 1000:.1f} kN vertical at the coupling, separately")

    def fixings(self) -> list[dict]:
        """LC7 design forces for the fixings of the heavy items, in the heaviest case of each."""
        lc = next(l for l in self.ch.data["load_cases"] if l["id"] == "LC7")
        best: dict[str, dict] = {}
        for c in self.tr.cases:
            sums: dict[str, dict] = {}
            for it in self.items(c):
                base = it.id.split(".")[0] if not it.id.startswith("GB ") else it.id
                r = sums.setdefault(base, dict(id=base, name=it.name, kg=0.0))
                r["kg"] += it.m
            for k, r in sums.items():
                if k not in best or r["kg"] > best[k]["kg"]:
                    best[k] = dict(r, case=c.id)
        rows = []
        for r in sorted(best.values(), key=lambda r: -r["kg"]):
            if r["kg"] < 25 or r["id"].startswith(("RL-", "RS-", "CM-", "OR-", "DB-", "RG-", "BD-0", "BD-1", "CH-")):
                continue
            f = [r["kg"] * G * abs(sum(a)) / 1000 for a in lc["accel"]]
            rows.append(dict(id=r["id"], name=r["name"], kg=r["kg"], case=r["case"], forward_kn=f[0], rearward_kn=f[1], sideways_kn=f[2], up_kn=f[3]))
        return rows

    # ------------------------------------------------------------------ against report 11's hand numbers
    def cross_checks(self, out: dict, lc6: dict) -> list[dict]:
        ch, V = self.ch, self.ch.V
        rows = []
        g = max(((m, r) for m, r in out["envelope"]["LC2"].items() if m.startswith("RL-")), key=lambda kv: kv[1]["sigma"])
        comp = ch.comp
        rows.append(dict(id="rail-LC2", what="Composite rail, LC2 (3 g)", hand_mpa=130.0, model_mpa=g[1]["sigma"],
                         model_moment_knm=abs(g[1]["M_strong"]) / 1e6, model_z=comp.Z_strong, hand_moment_knm=13.5, hand_z=104e3,
                         at=g[1]["at"], case=g[1]["case"]))
        vert = [lc6[k] for k in lc6 if "Z" in k]
        sig = max(max(self.normal_at(r, f"DB-{s}A", V["body_x0"]), self.normal_at(r, f"DB-{s}B", V["body_x0"])) for r in vert for s in "KR")
        f_up = max(abs(f[2]) for f in next(l for l in ch.data["load_cases"] if l["id"] == "LC6")["forces_n"])
        rows.append(dict(id="drawbar-LC6", what=(f"Drawbar member at the body front, LC6 vertical (report 11's hand figure, 264 MPa at 17.2 kN, "
                                                 f"scaled to the plate's {f_up / 1000:.1f} kN)"), hand_mpa=264.0 * f_up / 17200, model_mpa=sig))
        o = max(((m, r) for m, r in out["envelope"]["LC2"].items() if m.startswith("OR-")), key=lambda kv: kv[1]["sigma"])
        L = V["outrigger_tip_y"] - V["outrigger_root_y"]
        tip = abs(o[1]["M_strong"]) / (3 * G * L)
        rows.append(dict(id="outrigger-LC2", what="Outrigger root, LC2 (3 g)", hand_mpa=177.0, model_mpa=o[1]["sigma"], member=o[0],
                         equivalent_tip_kg=tip, hand_tip_kg=150.0, case=o[1]["case"]))
        return rows


def _dir(F) -> str:
    i = int(np.argmax(np.abs(F)))
    return ("+" if F[i] > 0 else "-") + "XYZ"[i]


def _box_gap(a, b) -> float:
    """The clear distance between two boxes (x0, y0, z0, x1, y1, z1), 0 where they meet or overlap."""
    return math.sqrt(sum(max(0.0, b[k] - a[k + 3], a[k] - b[k + 3]) ** 2 for k in range(3)))


def _miner(fat: float, ds_o: float, lc: dict) -> float:
    """LC10's Miner damage from the occasional range ds_o on IIW's curve for FAT, slope 3 to 10^7 cycles, then 22."""
    cafl = 0.585 * fat
    if ds_o <= cafl:
        return 0.0
    n = 2e6 * (fat / ds_o) ** 3
    if n > 1e7:
        n = 1e7 * (cafl / ds_o) ** 22
    return lc["occasional_cycles"] / n


def _local(name, rows, load) -> dict:
    parts = [dict(part=p, mpa=s, limit_mpa=l, util=s / l) for p, s, l in rows]
    g = max(parts, key=lambda r: r["util"])
    return dict(name=name, load=load, parts=parts, util=g["util"], governing=g["part"], mpa=g["mpa"], limit_mpa=g["limit_mpa"])

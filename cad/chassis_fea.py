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
ROOT_GUSSET, ROOT_END_PLATE = "CH-P03", "CH-P15"   # the drawbar root's gusset and the rail's end plate its heel is welded to
ROOT_PLACES = {"root_splice": "DB-{side}A's mitre at X {x:.0f}", "root_heel_weld": "CH-P03's heel, DB-{side}",
               "root_end_plate": "CH-P15 on RL-{side}", "root_end_plate_weld": "CH-P15's welds to RL-{side}, {weld}"}
NU = 0.3


@dataclass
class Item:
    id: str
    name: str
    m: float                       # kg
    p: tuple[float, float, float]  # where the mass acts
    rule: str
    wheel: str | None = None


class Analysis:
    def __init__(self, lay, tr, ch: Chassis, body=None, hinges: str = "crossmember"):
        self.lay, self.tr, self.ch = lay, tr, ch
        self.hinges = hinges
        self.fm = ch.frame(body, hinges)
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

    def airbag_force(self, w: dict, items: list[Item], acc, C: np.ndarray, hub_f: np.ndarray | None = None) -> float:
        """The force an arm's airbag must push the chassis up with (+) for the arm to balance about its hinge's Y axis,
        under its tyre's contact force C, its unsprung weight and any force at its hub."""
        a = np.asarray(acc, float) * G
        P = np.asarray(w["pivot"], float)
        m_y = np.cross(np.asarray(w["contact"]) - P, C)[1]
        m_y += sum(np.cross(np.asarray(it.p, float) - P, it.m * a)[1] for it in items if it.rule == "unsprung" and it.wheel == w["id"])
        if hub_f is not None:
            m_y += np.cross(np.asarray(w["hub"], float) - P, hub_f)[1]
        return -m_y / (w["airbag"][0] - P[0])

    def arm_loads(self, items: list[Item], acc, contact: dict, q: np.ndarray, hub: dict | None = None, bag_min: dict | None = None) -> dict:
        """Solve each arm as a free body about its hinge and put the hinge, airbag and droop limit forces on the frame.
        `hub` adds a force at a wheel's hub, where an obstacle holds the wheel in LC8a. `bag_min` gives each airbag's force
        with its arm on its droop limit (LC8a, I2-94): an airbag cannot pull, so where the arm's balance asks less of it the
        arm drops onto its droop limit (droop_limits), the airbag pushes with that force and the limit takes the rest of
        the arm's moment, pulling the frame down at its bracket."""
        a = np.asarray(acc, float) * G
        limits = self.droop_limits() if bag_min else {}
        out = {}
        for w in self.ch.suspension:
            P = np.asarray(w["pivot"], float)
            un = [(it.m * a, np.asarray(it.p, float) - P) for it in items if it.rule == "unsprung" and it.wheel == w["id"]]
            if hub and w["id"] in hub:
                un.append((np.asarray(hub[w["id"]], float), np.asarray(w["hub"], float) - P))
            Wu = sum((F for F, _ in un), np.zeros(3))
            Mu = sum((np.cross(r, F) for F, r in un), np.zeros(3))
            C = contact[w["id"]]
            rC = np.asarray(w["contact"]) - P
            rB = np.asarray(w["airbag"]) - P
            m_y = np.cross(rC, C)[1] + Mu[1]
            Fb = -m_y / rB[0]                         # airbag force on the chassis, + up
            T, F_lim = 0.0, np.zeros(3)
            if bag_min and Fb < bag_min[w["id"]]:
                lim = limits[w["id"]]
                Fb = bag_min[w["id"]]
                T = -(m_y + rB[0] * Fb) / lim["lever"]                   # the limit's tension along its line, N
                F_lim = T * lim["u"]                                     # its pull on the arm, toward its bracket
            Fbag_arm = np.array([0.0, 0.0, -Fb])
            H_arm = -(C + Wu + Fbag_arm + F_lim)
            M_arm = -(np.cross(rC, C) + Mu + np.cross(rB, Fbag_arm) + (np.cross(limits[w["id"]]["arm"] - P, F_lim) if T else 0.0))
            M_arm[1] = 0.0
            self._apply(-H_arm, P, [(self.fm.pivot_nodes[w["id"]], 1.0)], q, M=-M_arm)
            self._apply(np.array([0.0, 0.0, Fb]), w["airbag"], self.fm.rail_fractions(w["side"], w["airbag"][0]), q)
            if T:
                lim = limits[w["id"]]
                self._apply(-F_lim, lim["frame"], self.fm.crossmember_fractions(lim["cm"], lim["frame"][1]), q)
            out[w["id"]] = dict(contact=C, airbag=Fb, hinge=-H_arm, hinge_moment=-M_arm, droop_n=T)
        return out

    def droop_limits(self) -> dict:
        """Each XT arm's droop limit (xt_arms `droop`): its shock absorber at full extension (est., Cruisemaster's XT kit
        has no droop strap), from its eye on the arm at the hub to its bracket on the next crossmember's front face, the
        front arms' on the XT centre crossmember and the rear arms' on the XT rear shock crossmember, at the crossmember's
        mid-height and the shock support plate's Y. `u` is the unit vector from the arm's eye to the bracket and `lever`
        the moment about the pivot's Y axis of a unit pull along it, negative for a pull that lifts the hub."""
        if getattr(self, "_droop", None):
            return self._droop
        ch, V = self.ch, self.ch.V
        d = ch.data["xt_arms"]["droop"]
        cms = {m.station: m for m in ch.members if m.role.startswith("cm")}
        out = {}
        for w in ch.suspension:
            cm = cms[d["to"][w["axle"]]]
            y = w["side"] * ch.ev(d["y"])
            arm = np.array([w["hub"][0], y, w["hub"][2]])
            frame = np.array([cm.p0[0] - cm.sec.b / 2, y, V["rail_underside_z"] + d["z_over_underside"]])
            u = (frame - arm) / np.linalg.norm(frame - arm)
            lever = np.cross(arm - np.asarray(w["pivot"], float), u)[1]
            out[w["id"]] = dict(arm=arm, frame=frame, u=u, lever=lever, cm=cm.id, length=float(np.linalg.norm(frame - arm)))
        self._droop = out
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

    def recovery_reactions(self, F, p, held: str | None = None, base: dict | None = None, nose: dict | None = None) -> dict:
        """LC8a's reaction, which report 11 does not give: the ground at the four tyres, the trailer a rigid body on each
        wheel's support stiffness, its tyre and arm in series (LC8a's reaction, est.). The wheels are unbraked, so the
        ground's force on each passes through its hub: along the trailer every wheel takes its share there, or with `held`
        that wheel is held fast against an obstacle at its hub's height and the other three roll free. Across and up every
        tyre works at its lateral and vertical rate at its contact. The forces along and across hold the pull in plan, as
        they always have, and the forces up hold what that leaves, its lift and its moments in roll and pitch.

        `base` is the trailer's weight as the static case reacts it (reactions, 1 g down): each tyre and the nose start
        from that load (I2-94). No tyre can pull the ground, so one that would leaves it and the trailer pitches or rolls
        onto the supports that remain, the `nose` at the ball among them: on its jockey wheel, which cannot pull either, or
        held both ways by the coupled truck (LC8a `reaction` `nose`, est.). A bogged tyre that lifts is taken to stay in its
        rut, which holds it along and across at its rates (est., `lift` gives each one's rise on the rates). The set of supports in contact is
        iterated until every one in contact pushes and none off the ground would. Where no set holds the trailer at the
        whole pull, it tips first, so the pull is taken at the largest share of it that the trailer holds (`scale`).
        Returns the force the ground puts on each tyre at its contact and on each wheel at its hub, the nose's force, the
        tyres off the ground, their rise and the scale."""
        r = next(lc for lc in self.ch.data["load_cases"] if lc["id"] == "LC8a")["reaction"]
        springs = []
        for w in self.ch.suspension:
            pre = float(base["contact"][w["id"]][2]) if base else 0.0
            for d, k in ((0, r["kx"]), (1, r["ky"]), (2, r["kz"])):
                at = w["hub"] if d == 0 else w["contact"]
                obstacle = held is not None and w["id"] == held and d < 2
                if held is not None and d < 2:
                    k = r["held_k"] if obstacle else (0.0 if d == 0 else k)
                    at = w["hub"] if obstacle else at
                if k:
                    springs.append(dict(w=w["id"], d=d, k=k, e=np.eye(3)[d], at=np.asarray(at, float), pre=pre if d == 2 else 0.0,
                                        on="hub" if obstacle or d == 0 else "contact", contact=w["id"] if d == 2 else None))
        if base and nose:
            springs.append(dict(w="nose", d=2, k=nose["kz"], e=np.eye(3)[2], at=np.array([0.0, 0.0, self.ch.V["coupling_z"]]),
                                pre=float(base["ball"][2]), on="nose", contact=None if nose.get("holds_down") else "nose"))
        for s in springs:
            s["g"] = np.r_[s["e"], np.cross(s["at"], s["e"])]
        F = np.asarray(F, float)
        load = np.r_[F, np.cross(np.asarray(p, float), F)]
        # in plan: X, Y and yaw on the forces along and across
        plan, up = [0, 1, 5], [2, 3, 4]
        flat = [s for s in springs if s["d"] < 2]
        Kh = sum(s["k"] * np.outer(s["g"][plan], s["g"][plan]) for s in flat)
        uh = np.linalg.solve(Kh, load[plan])
        fh = {id(s): -s["k"] * (s["g"][plan] @ uh) for s in flat}
        left = load + sum((fh[id(s)] * s["g"] for s in flat), np.zeros(6))      # what the plan leaves, up, in roll and in pitch
        vert = [s for s in springs if s["d"] == 2]
        ground = [s for s in vert if s["contact"]]                               # the supports that can only push
        sc = np.array([1.0, 1e-3, 1e-3])                                          # rotations as mm at 1 m

        def solve(lam: float):
            off: set[str] = set()
            for _ in range(40):
                act = [s for s in vert if s["contact"] not in off]
                K = sum((s["k"] * np.outer(s["g"][up], s["g"][up]) for s in act), np.zeros((3, 3)))
                ev = np.linalg.eigvalsh(K * sc[:, None] * sc[None, :])
                if ev[0] < 1e-6 * ev[-1]:
                    return None
                rhs = lam * left[up] - sum((s["pre"] * s["g"][up] for s in vert if s["contact"] in off), np.zeros(3))
                u = np.linalg.solve(K, rhs)
                f = {id(s): s["pre"] - s["k"] * (s["g"][up] @ u) for s in vert}
                neg = [s for s in ground if s["contact"] not in off and f[id(s)] < -1e-6]
                back = [s for s in ground if s["contact"] in off and f[id(s)] > 1e-6]
                if neg:
                    off.add(min(neg, key=lambda s: f[id(s)])["contact"])
                elif back:
                    off.discard(max(back, key=lambda s: f[id(s)])["contact"])
                else:
                    return f, off, {s["contact"]: -f[id(s)] / s["k"] for s in ground if s["contact"] in off}
            return None

        lam, got = 1.0, solve(1.0)
        if got is None:
            lo, hi, got = 0.0, 1.0, solve(0.0)
            for _ in range(14):
                mid = (lo + hi) / 2
                trial = solve(mid)
                if trial is None:
                    hi = mid
                else:
                    lo, got = mid, trial
            lam = lo
        f, off, lift = got
        contact = {w["id"]: np.zeros(3) for w in self.ch.suspension}
        hub, nose_f = {}, np.zeros(3)
        for s in springs:
            if s["contact"] in off:
                continue
            v = (lam * fh[id(s)] if s["d"] < 2 else f[id(s)]) * s["e"]
            if s["on"] == "nose":
                nose_f = nose_f + v
            elif s["on"] == "hub":
                hub[s["w"]] = hub.get(s["w"], np.zeros(3)) + v
            else:
                contact[s["w"]] = contact[s["w"]] + v
        return dict(contact=contact, hub=hub, nose=nose_f, off=sorted(off), scale=lam, lift=lift)

    def run_recovery(self, F, p, fractions, held: str | None = None, support: dict | None = None):
        """LC8a: the pull at its recovery point with the trailer's weight and its nose's support (`support`, I2-94), the
        tyres' and the nose's reactions through supports that cannot pull (recovery_reactions), each arm a free body about
        its hinge, its airbag taking its moment or its droop limit the part its airbag cannot (arm_loads), and the frame
        held only by the six kinematic supports."""
        q = np.zeros(self.n)
        acc = (0.0, 0.0, -1.0) if support else (0.0, 0.0, 0.0)
        items = support["items"] if support else []
        base = support["base"] if support else None
        R = self.recovery_reactions(F, p, held, base, support["nose"] if support else None)
        self._apply(R["scale"] * np.asarray(F, float), p, fractions, q)
        bag_min = None
        if support:
            q += support["q"]
            self._apply(R["nose"], (0.0, 0.0, self.ch.V["coupling_z"]), [(self.fm.ball, 1.0)], q)
            bag_min = support["bag_min"]
        arms = self.arm_loads(items, acc, R["contact"], q, hub=R["hub"], bag_min=bag_min)
        res = self.kinematic.solve(q)
        self.resid = max(self.resid, max(abs(v) for v in res.reactions.values()))
        return res, dict(R, arms=arms, bag_min=bag_min)

    def recovery_supports(self, cases) -> list[dict]:
        """The weights and nose supports LC8a is read with (LC8a `reaction` `weight` and `nose`): each trailer case at
        tare, as the layout gives it, or at the plate, scaled as the other cases are, on each nose support. Each carries its
        weight's frame loads and static reactions, and each airbag's force with its arm at full droop, its force at ride
        less the air spring's rate (stability `air_spring_rate`, est.) over the droop limit's travel."""
        r = next(lc for lc in self.ch.data["load_cases"] if lc["id"] == "LC8a")["reaction"]
        rate, travel = self.tr.td["stability"]["air_spring_rate"], self.ch.data["xt_arms"]["droop"]["travel"]
        acc = (0.0, 0.0, -1.0)
        out = []
        for wd in r["weight"]:
            if wd["at"] == "tare":
                c = next(c for c in self.tr.cases if c.id == wd["case"])
                label, items = f"{c.id} at tare", self.items(c)
            else:
                c, items, _, _ = next(x for x in cases if x[0].id == wd["case"])
                label = f"{c.id} at the plate"
            base = self.reactions(items, acc)
            q = self.sprung_loads(items, acc)
            bag_min = {w["id"]: max(0.0, self.airbag_force(w, items, acc, base["contact"][w["id"]]) - rate * travel) for w in self.ch.suspension}
            for nose in r["nose"]:
                out.append(dict(label=f"{label}, {'coupled' if nose.get('holds_down') else 'uncoupled'}", items=items, base=base, q=q,
                                bag_min=bag_min, nose=nose))
        return out

    def _recovery_envelope(self, lc_id: str, label: str, info: dict, held: str | None):
        """LC8a's supports in each case (I2-94): the largest force on each arm's droop limit and airbag, the tyres off the
        ground, the pulls the trailer tips under before they reach their full size, and each held hinge's force."""
        e = self.lc8_arms.setdefault(lc_id, dict(cases=0, lifted=0, nose_off=0, tipped=[], droop={}, bag={}, hinge={}, lift=dict(mm=0.0),
                                                 nose=dict(up=0.0, down=0.0)))
        e["cases"] += 1
        e["nose"]["up"] = max(e["nose"]["up"], float(info["nose"][2]))
        e["nose"]["down"] = max(e["nose"]["down"], -float(info["nose"][2]))
        off = info["off"]
        for k, mm in info["lift"].items():
            if k != "nose" and mm > e["lift"]["mm"]:
                e["lift"] = dict(mm=mm, wheel=k, case=label)
        e["lifted"] += sum(1 for o in off if o != "nose")
        e["nose_off"] += "nose" in off
        if info["scale"] < 1.0 - 1e-9:
            e["tipped"].append(dict(case=label, scale=info["scale"]))
        for wid, a in info["arms"].items():
            if a["droop_n"] > e["droop"].get(wid, {}).get("n", 0.0):
                e["droop"][wid] = dict(n=a["droop_n"], case=label, airbag_n=a["airbag"], off=off)
            if a["airbag"] > e["bag"].get(wid, {}).get("n", -math.inf):
                e["bag"][wid] = dict(n=a["airbag"], case=label, off=off)
            if held == wid:
                h = np.asarray(a["hinge"], float)
                if abs(h[0]) > abs(e["hinge"].get(wid, {}).get("f", np.zeros(3))[0]):
                    e["hinge"][wid] = dict(f=h, case=label, droop_n=a["droop_n"])

    def run_body(self, F, p, fractions):
        q = np.zeros(self.n)
        self._apply(np.asarray(F, float), p, fractions, q)
        return self.body.solve(q)

    # ------------------------------------------------------------------ stress
    def stresses(self, res, ultimate: bool = False) -> dict[str, dict]:
        """Peak stress in each member: normal stress (axial plus both bending axes at a corner), shear from torsion
        and the wall shear, combined as sqrt(sigma^2 + 3 tau^2). `ultimate` reads each axis's bending on the AS 4100 5.2
        effective section, Ze, so the stress against fy is the section capacity's linear interaction (AS 4100 8.3.4)."""
        out = {}
        nodes = self.f.nodes
        for el, fl in zip(self.f.elements, res.forces):
            if el.sec.rigid or el.member in ("BODY", "BODY-MOUNT") or el.member.startswith("PNL-"):
                continue
            sp = self.fm.sec_props[el.member]
            for end, act in zip((el.i, el.j), end_actions(fl)):
                if isinstance(sp, Composite):
                    A, Zs, Zw, C, Awd, Aww = sp.A, sp.Z_strong, sp.Z_weak, sp.C, sp.Aw, sp.rail.Aw_width + sp.raiser.Aw_width
                    if ultimate:
                        Zs, Zw = min(sp.Ze_strong, 1.5 * sp.Z_strong), sp.Ze_weak
                else:
                    A, Zs, Zw, C, Awd, Aww = sp.A, sp.Z_strong, sp.Z_weak, sp.C, sp.Aw_depth, sp.Aw_width
                    if ultimate:
                        Zs, Zw = sp.Ze_strong, sp.Ze_weak
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
        self.panel_env: dict[str, dict] = {}

        def take(lc_id, res, label, extra=None, ultimate=False):
            for mem, r in self.stresses(res, ultimate).items():
                e = env.setdefault(lc_id, {})
                if mem not in e or r["eq"] > e[mem]["eq"]:
                    e[mem] = dict(r, case=label, **(extra or {}))
            for sp in self.fm.panels_by_id().values():
                v = self.panel_shear(res, sp)
                pe = self.panel_env.setdefault(lc_id, {})
                if sp["id"] not in pe or v > pe[sp["id"]]["v_n"]:
                    pe[sp["id"]] = dict(v_n=v, case=label)
            he = hole_env.setdefault(lc_id, {})
            for k, h in enumerate(sites):
                if h.get("open") or h.get("placement_only"):
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
        # LC8a at each recovery point, at the 58.9 kN pull (no yield) and at the 78.5 kN ultimate (no fracture, LC8u): the
        # members on their AS 4100 effective sections against fy, the holes on their net sections against 0.85 fu. A rear
        # tongue's pull acts at its shackle hole and enters the frame at the rear crossmember's end, where the tongue is
        # welded through the crossmember and along the rail's web (rear_recovery_point, I2-87)
        lc8 = lcs["LC8a"]
        supports = self.recovery_supports(cases)
        self.lc8_arms: dict[str, dict] = {}
        for lc_id, Fr in (("LC8a", lc8["force_n"]), ("LC8u", lc8["ultimate_n"])):
            for where in ("front", "rear"):
                for s in (-1, 1):
                    if where == "front":
                        x, sx = V["front_recovery_x"], -1
                        p, fr = (x, s * (V["rail_c"] + 35), V["db_z"]), [(self.fm.db_node(s, x), 1.0)]
                    else:
                        sx = 1
                        p, cm = self.rear_recovery_point(s)
                        fr = [(self.fm.cm_node(cm, s * V["rail_c"]), 1.0)]
                    pulls = [(f"{h:+d} deg sideways", None, math.radians(h)) for h in (-30, 0, 30)]
                    for w in ch.suspension:
                        hdg = math.atan2(p[1] - w["hub"][1], sx * (p[0] - w["hub"][0]))
                        if abs(hdg) <= math.radians(30) + 1e-9:
                            pulls.append((f"{math.degrees(hdg):+.1f} deg sideways through wheel {w['id']}, held", w["id"], hdg))
                    for lab, held, hdg in pulls:
                        for v in (-15, 0, 15):
                            F = Fr * np.array([sx * math.cos(hdg) * math.cos(math.radians(v)), math.sin(hdg) * math.cos(math.radians(v)),
                                               math.sin(math.radians(v))])
                            for sup in supports:
                                res, info = self.run_recovery(F, p, fr, held, sup)
                                label = (f"{where} {'kerb' if s < 0 else 'road'}-side point, {lab}, {v:+d} deg up, {sup['label']}"
                                         + (f", {Fr / 1000:.1f} kN" if lc_id == "LC8u" else "")
                                         + (f", tipping at {info['scale'] * Fr / 1000:.1f} kN" if info["scale"] < 1.0 - 1e-9 else ""))
                                take(lc_id, res, label, ultimate=lc_id == "LC8u")
                                self._recovery_envelope(lc_id, label, info, held)
        out = dict(envelope={}, governing={}, deflections={}, twist=twist, balls=balls, residual_n=self.resid,
                   frame=dict(nodes=len(self.f.nodes), elements=sum(1 for e in self.f.elements if not e.sec.rigid),
                              rigid_links=sum(1 for e in self.f.elements if e.sec.rigid)))
        for lc_id, e in env.items():
            fac = lcs[lc_id]["factor"] if lc_id in lcs else 1
            rows = {m: dict(r, util=r["eq"] / (fy_of.get(m, self.fy_of_part(m)) / fac), fy=fy_of.get(m, self.fy_of_part(m)))
                    for m, r in e.items() if not m.startswith("_")}
            out["envelope"][lc_id] = rows
            g = max(rows.items(), key=lambda kv: kv[1]["util"])
            out["governing"][lc_id] = dict(member=g[0], **g[1], limit=g[1]["fy"] / fac, factor=fac)
        out["pad_n"] = env["LC8b"]["_pad"]
        out["deflections"] = self._worst_deflections(defl)
        out["fatigue"] = self.fatigue(lc1)
        out["holes"] = self.holes(hole_env, lc1, sites)
        from .chassis_dip import check as galvanising_check
        out["galvanising"] = galvanising_check(ch)
        out["local"] = self.local_checks(out["pad_n"]["pad_n"])
        out["local"].update(self.panel_checks(), hinge_cheeks=self.cheek_check(), arm_limits=self.arm_limits())
        out["recovery"] = self.recovery_summary()
        out["fixings"] = self.fixings()
        out["cross_checks"] = self.cross_checks(out, lc6)
        out["lc1_ball"] = balls
        out["hinge_joints"] = self.hinge_joints(out)
        return out

    def hinge_joints(self, out: dict) -> dict:
        """CHS-12 (I2-88): the XT hinge joints as built, each pivot tied to its crossmember at the hinge bar's weld runs and
        to the rail through the hinge's two cheeks, with the gussets either side: the hinge crossmembers, the gussets, the
        cheeks and the crossmembers' holes in every case against that case's limit, and FAT-03 and FAT-13."""
        ch = self.ch
        parts = {m.id for m in ch.hinge_crossmembers()} | {g["id"] for g in ch.hinge_gussets()} | {c["member"] for c in ch.hinge_cheeks()}
        rows = []
        for lc_id, env in out["envelope"].items():
            for m, r in env.items():
                if m in parts:
                    rows.append(dict(part=m, lc=lc_id, mpa=r["eq"], limit=r["eq"] / r["util"] if r["util"] else r["fy"],
                                     util=r["util"], case=r["case"], at=r["at"]))
        for h in (h for h in out["holes"] if not h.get("open") and h.get("member") in parts):
            for key in ("static", "ultimate"):
                v = h.get(key)
                if v:
                    rows.append(dict(part=f"{h['id']} in {h['member']}", lc=v["lc"], mpa=v["mpa"], limit=v["limit"], util=v["util"], case=v["case"]))
        fat = [dict(id=f["id"], range_mpa=f["range_mpa"], cafl=f["cafl"], util=f["range_mpa"] / f["cafl"], where=f["where"])
               for f in out["fatigue"] if f["id"] in ("FAT-03", "FAT-13")]
        worst = max(rows, key=lambda r: r["util"])
        return dict(rows=sorted(rows, key=lambda r: -r["util"])[:12], worst=worst, fatigue=fat,
                    ok=worst["util"] <= 1 + 1e-9 and all(f["util"] <= 1 + 1e-9 for f in fat))

    def panel_shear(self, res, sp: dict) -> float:
        """The racking shear a shear panel carries, from its two diagonals' axial forces: V = (N1 - N2) b / L, in N."""
        n1, n2 = (float(res.forces[e][6]) for e in sp["elements"])
        return abs(n1 - n2) * 2 * self.ch.V["rail_c"] / sp["L"]

    def panel_checks(self) -> dict:
        """Each shear panel (shear_panels) in its worst case of every load case: the plate's shear stress V / (b t) against
        its shear yield over the case's factor and its elastic shear buckling stress, and the M8 bolts to its angles, each
        taking the panel's shear V over the angles' `transverse` length under each crossmember times their pitch, against
        AS 4100 9.3.2's bolt shear capacity with the threads in the plane."""
        ch = self.ch
        lcs = {lc["id"]: lc for lc in ch.data["load_cases"]}
        out = {}
        for sp in ch.shear_panels():
            d = next(x for x in ch.data["shear_panels"] if x["id"] == sp["id"])
            a, b, t = sp["x1"] - sp["x0"], sp["b"], sp["t"]
            lo, hi = sorted((a, b))
            k = 5.35 + 4.0 * (lo / hi) ** 2
            tau_cr = k * math.pi ** 2 * 200_000.0 / (12 * (1 - NU ** 2)) * (t / lo) ** 2
            bolt = d["fixing"]
            cap = 0.8 * 0.62 * bolt["fuf"]                     # MPa on the bolt's minor diameter area
            size = bolt["bolt"].split()[0]
            rows = []
            for lc_id, e in self.panel_env.items():
                r = e[sp["id"]]
                fac = lcs[lc_id]["factor"] if lc_id in lcs else 1
                tau = r["v_n"] / (b * t)
                rows += [(f"plate shear, {lc_id}", tau, min(0.6 * d["fy"], tau_cr) / fac),
                         (f"{size} bolt to its angles, {lc_id}", r["v_n"] / bolt.get("transverse", b) * bolt["pitch"] / bolt["a_c"], cap / fac)]
            w = max(self.panel_env.items(), key=lambda kv: kv[1][sp["id"]]["v_n"])
            res = _local(f"Shear panel {sp['id']}, {t:g} mm steel, {a:,.0f} x {b:,.0f} mm", [(p, s_, l) for p, s_, l in rows],
                         f"its worst racking shear, {w[1][sp['id']]['v_n'] / 1000:.1f} kN in {w[0]}, {w[1][sp['id']]['case']}")
            res.update(tau_cr=tau_cr, v_n=w[1][sp["id"]]["v_n"], lc=w[0])
            out["shear_panel"] = res
        return out

    def cheek_check(self) -> dict:
        """CHS-14 (I2-92): the hinge cheeks' welds (CH-P16) at the 78.5 kN ultimate pull, all of it along the trailer through
        one cheek, as a held wheel puts it through a front hinge, which has one, with the largest force across and up that
        LC8a's solve puts on a held wheel's hinge at the ultimate. The force acts at the cheek's pin, the middle of its
        `bar_leg` fillets each side down the hinge bar's front or rear face over the bar's top `bar_d` (est.), which pass
        it but no moment, at the cheek's end. Its two lines on the rail's inner web, the `leg` fillet along its top edge and
        the flare-bevel weld along the rail's bottom corner, are read as one weld group by the elastic vector method, the
        force and its moments about the group's centroid, each line on its throat: the fillet's 0.7 leg and the flare
        bevel's `corner` share of the rail's outside radius, AISC 360 Table J2.2's 5/16 R for a manual metal arc weld."""
        ch = self.ch
        mat = ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        ck = ch.data["xt_hinges"]["cheek"]
        F = next(lc for lc in ch.data["load_cases"] if lc["id"] == "LC8a")["ultimate_n"]
        hinge = getattr(self, "lc8_arms", {}).get("LC8u", {}).get("hinge", {})
        fy_ = max((abs(float(h["f"][1])) for h in hinge.values()), default=0.0)
        fz_ = max((abs(float(h["f"][2])) for h in hinge.values()), default=0.0)
        bar = math.sqrt(F ** 2 + fy_ ** 2 + fz_ ** 2) / (2 * ck["bar_d"] * 0.7 * ck["bar_leg"])
        l, ro = ck["l"], ch.role_sec["rail"].ro
        lines = [("its top edge's fillet", ck["h"] - ck["below"], 0.7 * ck["leg"]),
                 ("the flare-bevel weld at the rail's bottom corner", 0.0, ck["corner"] * ro)]
        A = sum(a * l for _, _, a in lines)
        zc = sum(a * l * z for _, z, a in lines) / A
        Ix = sum(a * l * (z - zc) ** 2 for _, z, a in lines)
        Iz = sum(a * l ** 3 / 12 for _, _, a in lines)
        lever = zc + ck["bar_d"] / 2                     # the pin under the group's centroid, at the cheek's end
        M_in = F * lever + fz_ * l / 2                   # in the web's plane
        M_x, M_z = fy_ * lever, fy_ * l / 2              # out of it
        rows = [("to the hinge bar", bar, wcap)]
        for name, z, a in lines:
            dz = abs(z - zc)
            t_x = F / A + M_in * dz / (Ix + Iz)
            t_z = fz_ / A + M_in * (l / 2) / (Ix + Iz)
            s_n = fy_ / A + M_x * dz / Ix + M_z * (l / 2) / Iz
            rows.append((f"to the rail's web, {name}", math.sqrt(t_x ** 2 + t_z ** 2 + s_n ** 2), wcap))
        return _local("Hinge cheeks' welds (CH-P16)", rows,
                      f"the {F / 1000:.1f} kN ultimate pull along the trailer through one cheek, with {fy_ / 1000:.1f} kN across and "
                      f"{fz_ / 1000:.1f} kN up or down, the held hinges' largest at the ultimate")

    def arm_limits(self) -> dict:
        """CHS-15 (I2-94): what LC8a's arms put on their limits and mounts, the worst over every LC8a case at 58.9 kN and
        at the 78.5 kN ultimate: the droop limit's tension on its M12 eye bolts in double shear (AS 4100 9.3.2.1, threads
        in a shear plane) and on its bracket's fillets to the crossmember's face as a weld group, the eye `e` off the face,
        and the airbag's push with its bump stop, its bump load, on its top bracket's fillets along the rail's web."""
        ch = self.ch
        mat = ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        d, ab = ch.data["xt_arms"]["droop"], ch.data["xt_arms"]["airbag"]["bracket"]
        b, br = d["bolt"], d["bracket"]
        lim = self.droop_limits()
        rows = []
        for lc_id in ("LC8a", "LC8u"):
            e = self.lc8_arms[lc_id]
            wid, dr = max(e["droop"].items(), key=lambda kv: kv[1]["n"], default=(None, dict(n=0.0)))
            T = dr["n"]
            u = lim[wid]["u"] if wid else np.array([1.0, 0.0, 0.0])
            a = 0.7 * br["leg"]
            A = 2 * br["l"] * a
            I = 2 * a * br["l"] ** 3 / 12
            n_ = abs(T * u[0]) / A + abs(T * u[2]) * br["e"] * (br["l"] / 2) / I
            rows += [(f"droop limit's {b['size']} eye bolt, {lc_id}", T / (b["planes"] * b["a_c"]), 0.8 * 0.62 * b["fuf"]),
                     (f"droop limit's bracket fillets, {lc_id}", math.hypot(n_, abs(T * u[2]) / A), wcap)]
            bag = max((x["n"] for x in e["bag"].values()), default=0.0)
            rows.append((f"airbag's top bracket fillets under its bump load, {lc_id}", bag / ((ab["l"] + 2 * ab["returns"]) * 0.7 * ab["leg"]), wcap))
        u8 = self.lc8_arms["LC8u"]
        wid, dr = max(u8["droop"].items(), key=lambda kv: kv[1]["n"])
        return _local("XT arms' droop limits and airbag brackets", rows,
                      f"LC8a's arms, the worst droop limit {dr['n'] / 1000:.1f} kN at {wid} in {dr['case']}")

    def recovery_summary(self) -> dict:
        """LC8a's supports over its cases (I2-94), for CHASSIS.md and Cruisemaster's items: the cases read, the tyres off the
        ground, the pulls the trailer tips under and the least share of the pull it holds, each droop limit's and airbag's
        largest force, and the held hinges' largest force along the trailer with the hinge bar's moment from the pivot up to
        the cheek's pin."""
        ck = self.ch.data["xt_hinges"]["cheek"]
        depth = self.ch.V["pivot_below"] - ck["bar_d"] / 2
        out = {}
        for lc_id, e in self.lc8_arms.items():
            dw, dr = max(e["droop"].items(), key=lambda kv: kv[1]["n"])
            bw, bg = max(e["bag"].items(), key=lambda kv: kv[1]["n"])
            hw, hg = max(e["hinge"].items(), key=lambda kv: abs(kv[1]["f"][0]))
            least = min(e["tipped"], key=lambda t: t["scale"]) if e["tipped"] else None
            out[lc_id] = dict(cases=e["cases"], lifted=e["lifted"], nose_off=e["nose_off"], tipped=len(e["tipped"]), least=least, lift=e["lift"], nose=e["nose"],
                              droop=dict(wheel=dw, n=dr["n"], case=dr["case"], airbag_n=dr["airbag_n"], off=dr["off"]),
                              droop_by_wheel={k: v["n"] for k, v in e["droop"].items()},
                              bag=dict(wheel=bw, n=bg["n"], case=bg["case"]),
                              hinge=dict(wheel=hw, f=[float(x) for x in hg["f"]], case=hg["case"], bar_moment_nmm=abs(float(hg["f"][0])) * depth))
        return out

    def fy_of_part(self, member: str) -> float:
        """The yield stress of a frame part that is not a member (a hinge gusset), from its section."""
        sp = self.fm.sec_props.get(member)
        return getattr(sp, "fy", None) or self.ch.fy

    def rear_recovery_point(self, s: int) -> tuple[tuple[float, float, float], str]:
        """A rear recovery tongue's shackle hole (CH-P05 and local_checks rear_recovery's edge from the hole to the
        tongue's rear edge) and the rear crossmember the tongue is welded through, on side s."""
        ch, V = self.ch, self.ch.V
        f = next(d for d in ch.data["fittings"] if d["id"] == "CH-P05")
        at = ch.ev(f["at"])
        x = at[0] + f["l"] / 2 - ch.data["local_checks"]["rear_recovery"]["edge"]
        cm = next(m.id for m in ch.members if m.station == "rear" and m.role.startswith("cm"))
        return (x, s * ch.ev(f["side_y"]), at[2]), cm

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
            if isinstance(where, dict):          # a stretch of the member, read every 50 mm (FAT-21's lap)
                x0, x1 = ch.ev(where["from"]), ch.ev(where["to"])
                return [x0 + (x1 - x0) * k / max(round((x1 - x0) / 50), 1) for k in range(max(round((x1 - x0) / 50), 1) + 1)]
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
                        dz = ch.role_sec["drawbar"].d / 2
                        out.append((max(self.normal_at(res, m, x) for m in mems) * max(self.hole_field(s, x, z) for z in (-dz, dz)),
                                    f"DB-{SIDES[s]} at X {x:.0f}"))
            elif k in ROOT_PLACES:
                for s in (-1, 1):
                    r = self.root_stresses(res, s)
                    out.append((r[k], ROOT_PLACES[k].format(side=SIDES[s], x=V["body_x0"], weld=r["weld"])))
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

    def root_stresses(self, res, s: int) -> dict:
        """The body front under the root gusset's heel (FAT-17 to FAT-20, I2-51, I2-60), from the A-frame member's end
        actions there, on the section of the member and the gusset's heel together, as the heel is welded to the rail's
        end plate: the mitred splice at the member's far corner, the heel's two fillets on the smaller of their throats at
        the gusset's top, their T-joint skewed (I2-72), the end plate in bending under the heel's line load, simply
        supported on the rail's walls, and its welds to the rail on their maximum principal stress range (I2-67). The heel
        stands `zg` off the member's axis (root_gusset_heel_y), so the section is unsymmetric, and its product of inertia
        adds each moment's coupling to the other axis, taken on the safe side."""
        ch, V = self.ch, self.ch.V
        fit = {f["id"]: f for f in ch.data["fittings"]}
        g, ep, rail = fit[ROOT_GUSSET], fit[ROOT_END_PLATE], ch.role_sec["rail"]
        sp = self.fm.sec_props[f"DB-{SIDES[s]}A"]
        act = self.end_actions_at(res, f"DB-{SIDES[s]}A", V["body_x0"])
        n, my, mz = abs(act["N"]), abs(act["My"]), abs(act["Mz"])
        tg, hg = g["t"], g["w"]
        ag, yg = tg * hg, sp.d / 2 + hg / 2
        member = math.atan2(V["rail_c"] - V["db_apex_y"], V["body_x0"] - V["db_apex_x"])
        zg = (V["root_gusset_heel_y"] - ch.db_y(V["root_gusset_toe_x"] + g["l"])) * math.cos(member)
        area = sp.A + ag
        e, ez = ag * yg / area, ag * zg / area               # the joint section's centroid above and across from the member's
        i_s = sp.I_strong + sp.A * e ** 2 + tg * hg ** 3 / 12 + ag * (yg - e) ** 2
        i_w = sp.I_weak + sp.A * ez ** 2 + hg * tg ** 3 / 12 + ag * (zg - ez) ** 2
        i_sw = ag * (yg - e) * (zg - ez) + sp.A * e * ez
        den = i_s * i_w - i_sw ** 2

        def at(y, z):
            return n / area + (my * (abs(y) * i_w + abs(z) * i_sw) + mz * (abs(z) * i_s + abs(y) * i_sw)) / den
        g_bot, g_top = at(sp.d / 2 - e, zg - ez), at(sp.d / 2 + hg - e, zg - ez)
        plate = self.end_plate_under_heel(g_bot * tg, g_top * tg)
        throat = min(heel_throats(g["heel_legs"], plate["angle"]))

        def welds():
            """Each weld's normal range across its wall and its shear range along it come from the heel's one pull, so
            they vary in phase, and IIW 4.2 b) and 4.3 read their maximum principal stress range."""
            for name, q, wall, tau in (("the inboard web", plate["webs"][0], rail.t, plate["tau_web"]),
                                       ("the outboard web", plate["webs"][1], rail.t, plate["tau_web"]),
                                       ("the top", plate["top"], plate["top_t"], plate["tau_top"])):
                rng, angle = principal_range(np.abs(q).max() / wall, tau)
                yield rng, f"{name}, its principal stress {angle:.0f} degrees off the weld's normal"
        weld, where = max(welds())
        return dict(root_splice=at(sp.d / 2 + e, sp.b / 2 + ez) * self.hole_field(s, V["body_x0"], -sp.d / 2), root_heel_weld=g_top * tg / (2 * throat),
                    root_end_plate=6 * plate["moment"] / ep["t"] ** 2, root_end_plate_weld=weld, weld=where, plate=plate)

    def plate_field(self, res, h) -> tuple[float, float]:
        """The end plate's own field in the rail's web at a hole close behind it (I2-80): the normal line force the plate's
        weld puts into that web at the hole's height (root_stresses' Kirchhoff edge shear), over the wall, and the shear
        along the weld, taken undiminished at the hole, on the safe side (est.: it spreads into the web behind the weld)."""
        V, rail = self.ch.V, self.ch.role_sec["rail"]
        s = 1 if h["y"] > 0 else -1
        p = self.root_stresses(res, s)["plate"]
        web = p["webs"][1 if h["wall"] == "the rail's outer web" else 0]
        lift = next(f for f in self.ch.data["fittings"] if f["id"] == ROOT_END_PLATE).get("lift", 0.0)
        j = min(max(int(round((h["z"] - V["rail_underside_z"] - lift) / p["h"])) - 1, 0), len(web) - 1)
        return abs(float(web[j])) / rail.t, p["tau_web"]

    def hole_field(self, s: int, x: float, z_l: float) -> float:
        """Kirsch's field from the drawbar member's holes for galvanising at a point on its web, X along the frame and
        z_l over its axis: the largest factor on the stress along the member that any hole on that side puts there, 1
        where none stands near (I2-84). FAT-07 and FAT-17 read their nominal ranges with it at the drawbar root."""
        from .chassis_dip import frame_sections
        if not hasattr(self, "_db_holes"):
            self._db_holes = [h for h in frame_sections(self.ch)[1] if h["tube"].startswith("DB-") and h["tube"] != "DB-BR"]
        side = SIDES[s]
        k = 1.0
        ang = math.atan2(self.ch.V["rail_c"] - self.ch.V["db_apex_y"], self.ch.V["body_x0"] - self.ch.V["db_apex_x"])
        for h in self._db_holes:
            if h["tube"][3] != side:
                continue
            dx = abs(float(h["centre"][0]) - x) / (math.cos(ang) if h["tube"].endswith("A") else 1.0)
            k = max(k, kirsch_along(h["d"] / 2, dx, h["z_l"] - z_l))
        return k

    def end_plate_under_heel(self, q_foot: float, q_top: float) -> dict:
        """The rail's end plate CH-P15 under the gusset heel's pull, q_foot at the heel's foot rising to q_top N/mm at its
        top along the gusset's line (FAT-19, FAT-20, I2-57, I2-60). The plate's bottom edge stands `lift` over the rail's
        underside, clear of the drawbar member and unwelded (I2-75), so it is free. Its sides and top are welded to the
        rail's webs and top flange with full penetration
        single bevel welds made from outside, the plate behind each wall's end as the backing, and the plate stands up
        over the raiser's bottom wall, so its top weld joins both walls (`top_t`). The plate spans between the webs'
        mid-planes and from its free bottom edge (`edge` over the bottom wall's mid-plane) up to the middle of the walls
        its top weld joins, as end_plate takes it, and the heel's pull below that edge goes into the plate there, on the
        safe side. The heel stands where the gusset's data puts it (root_gusset_heel_y), and the gusset's line runs from
        the member's line at its toe to there, `angle` off the plate's normal in plan. The pull's part normal to the
        plate bends it (end_plate), spread across the heel's foot: the gusset's cut across the plate, its thickness over
        the cosine of that angle, and its two fillets' legs on the plate (I2-72). Its part along the plate, inboard, is
        applied at the plate's front face: half the
        plate's thickness off its mid-plane, so it is a line moment on the plate as well (km), which pulls the outboard
        web harder. The top weld takes that part as shear along its length (`tau_top`), and its moment about the plate's
        normal, from the heel's centroid up to the top weld, goes into the two webs as shear along their welds, a couple
        across the span (`tau_web`, est.: the plate taken as rigid in its plane, the shear even along the webs)."""
        ch, V = self.ch, self.ch.V
        ep = next(f for f in ch.data["fittings"] if f["id"] == ROOT_END_PLATE)
        g = next(f for f in ch.data["fittings"] if f["id"] == ROOT_GUSSET)
        rail = ch.role_sec["rail"]
        lift = ep.get("lift", 0.0)                 # the plate's bottom edge over the rail's underside (I2-75)
        top_t = rail.t + lift + ep["w"] - rail.d   # the rail's top flange and the raiser's bottom wall the plate covers
        height = rail.d - 1.5 * rail.t + top_t / 2
        span, z1 = rail.b - rail.t, g["w"] - rail.t / 2
        edge = max(lift - rail.t / 2, 0.0)         # the plate's free bottom edge over the bottom wall's mid-plane
        centre = span / 2 - (V["rail_c"] - V["root_gusset_heel_y"])     # from the inboard web
        angle = math.atan2(V["root_gusset_heel_y"] - V["root_gusset_toe_y"], g["l"])
        cn, sn = math.cos(angle), math.sin(angle)
        foot = g["t"] / cn + sum(g["heel_legs"])      # the gusset's cut across the plate and its two fillets' legs on it
        # the heel's pull below the plate's bottom edge goes into the plate at that edge, on the safe side: the load over
        # the plate keeps its top and the whole pull
        q_edge = (q_foot + q_top) * z1 / (z1 - edge) - q_top
        out = end_plate(span, height - edge, 0.0, z1 - edge, q_edge * cn, q_top * cn, foot, centre=centre,
                        km=math.tan(angle) * ep["t"] / 2)
        along = (q_foot + q_top) / 2 * z1 * sn
        zc = z1 * (q_foot + 2 * q_top) / (3 * (q_foot + q_top))
        return dict(out, top_t=top_t, centre=centre, angle=angle, along=along, tau_top=along / (span * top_t),
                    tau_web=along * (height - zc) / (span * (height - edge) * rail.t), edge=edge)

    def end_actions_at(self, res, member: str, x: float) -> dict:
        """A member's end actions at its element end nearest X."""
        best, bd = None, math.inf
        for el, fl in zip(self.f.elements, res.forces):
            if el.member != member:
                continue
            for nd, act in zip((el.i, el.j), end_actions(fl)):
                d = abs(self.f.nodes[nd][0] - x)
                if d < bd:
                    best, bd = act, d
        return best

    # ------------------------------------------------------------------ holes in the members (CHS-09, CHS-10)
    def hole_sites(self) -> list[dict]:
        """Each hole a run makes in a rail or a raiser (data/services.yaml `holes`), once: a hole through the seam of a rail
        and its raiser is one hole in two walls, and an outrigger's root face is the raiser's outer web. Each carries its
        wall, its net section in the composite rail, its edge distance and its clear distance to the nearest weld toe.
        An outrigger's open end under a side marker's cap has no wall. The vent and drain holes for galvanising at each
        rail's front end (galvanising_holes, I2-75) follow the services' holes, on both rails, their use as their run."""
        import yaml
        from .partsdb import DATA
        ch, V, comp = self.ch, self.ch.V, self.ch.comp
        rail, raiser = comp.rail, comp.raiser
        rules = ch.data["hole_rules"]
        rows = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8")).get("holes") or []
        for s in (-1, 1):
            for g in ch.data.get("galvanising_holes") or []:
                d = float(g["d"])
                inner = g.get("web") == "inner"
                outer_face = "road side" if s > 0 else "kerb side"
                face = ("kerb side" if s > 0 else "road side") if inner else outer_face
                y = s * (V["rail_c"] - rail.b / 2 + 0.5) if inner else s * (V["rail_c"] + rail.b / 2 - 0.5)
                rows.append(dict(member=f"RL-{SIDES[s]}", face=face, run=g["use"], x=ch.ev(g["x"]), y=y, z=ch.ev(g["z"]),
                                 d=d, length=d, plate_field=True))
            # the vents into each rail-to-raiser seam through both walls on its centreline (sealed_overlaps SEAM, I2-90)
            for o in ch.data.get("sealed_overlaps") or []:
                if o.get("through") != "seam":
                    continue
                for v in o["vents"]:
                    d = float(v["d"])
                    rows.append(dict(member=f"RL-{SIDES[s]}", face="top", run="seam vent", x=V["body_x0"] + ch.ev(v["u"]),
                                     y=s * V["rail_c"], z=V["rail_top_z"], d=d, length=d, late=True))
        # the holes CHS-11 puts in the rails' inner webs inside a crossmember's end, where a fitting covers that web of the
        # crossmember (member_galvanising_holes blocked_webs), each location with its 10 mm check hole in the rail's
        # outer web opposite (the guide's page 19)
        from .chassis_dip import frame_sections
        for h in frame_sections(ch)[1]:
            if h["via"] != "host":
                continue
            s = -1 if h["host"].endswith("K") else 1
            c = h["centre"]
            rows.append(dict(member=h["host"], face="kerb side" if s > 0 else "road side", run=h["use"], x=float(c[0]),
                             y=s * (V["rail_c"] - rail.b / 2 + 0.5), z=float(c[2]), d=float(h["d"]), length=float(h["d"]), new=True))
            if h["use"] == "drain":
                rows.append(dict(member=h["host"], face="road side" if s > 0 else "kerb side", run="check", x=float(c[0]),
                                 y=s * (V["rail_c"] + rail.b / 2 - 0.5), z=V["rail_underside_z"] + rail.d / 2, d=10.0, length=10.0, new=True))
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
        late = [h for h in sites if h.get("late")]           # the seam vents keep the ids after every other hole's
        sites = [h for h in sites if not h.get("new") and not h.get("late")] + self._drawbar_hole_sites(rules) + [h for h in sites if h.get("new")]
        sites += self._member_hole_sites(rules) + late
        for k, h in enumerate(sites, 1):
            h["id"] = f"H-{k:02d}"
        return sites

    def _drawbar_hole_sites(self, rules) -> list[dict]:
        """The drawbar members' apex drains for galvanising, H-33 to H-36, from the dip's own holes (cad/chassis_dip.py, the
        one place every hole for galvanising stands, I2-89), each a hole in the A-frame member's own section: its net
        section, its edge distance to the web's flat and to the member's square-cut apex end along its web, and its clear
        distance to the coupling plate's fillets, the capped apex end's weld and the chain lug's welds, on the member's web
        in its own plane (u along the member from its apex end, z up)."""
        from .chassis_dip import frame_sections
        ch, V = self.ch, self.ch.V
        sec = ch.role_sec["drawbar"]
        out = []
        ang = math.atan2(V["rail_c"] - V["db_apex_y"], V["body_x0"] - V["db_apex_x"])
        zb, zt = V["db_z"] - sec.d / 2, V["db_z"] + sec.d / 2
        lug = next(f for f in ch.data["fittings"] if f["id"] == "CH-P02")
        plate = next(f for f in ch.data["fittings"] if f["id"] == "CH-P01")
        plate_x1 = ch.ev(plate["at"][0]) + plate["l"] / 2
        lug_top = ch.ev(lug["at"][2]) + lug["w"] / 2
        apex = [h for h in frame_sections(ch)[1] if h["tube"] in ("DB-KA", "DB-RA") and h["use"] == "drain"]
        for g in sorted(apex, key=lambda h: (h["tube"] != "DB-KA", abs(h["centre"][1]) > ch.db_y(h["centre"][0]))):
            s = -1 if g["tube"] == "DB-KA" else 1
            web = "outer" if abs(g["centre"][1]) > ch.db_y(g["centre"][0]) else "inner"
            d, (x, y, z), u = float(g["d"]), (float(c) for c in g["centre"]), float(g["u_web"])
            toes = [("coupling plate's fillets", (0.0, zb, (plate_x1 - V["db_apex_x"]) / math.cos(ang), zb + 6)),
                    ("member's capped apex end", (0.0, zb, 6.0, zt))]
            if web == "outer":
                u0 = (ch.ev(lug["at"][0]) - lug["l"] / 2 - V["db_apex_x"]) / math.cos(ang)
                toes.append(("chain lug's welds", (u0 - 6, lug_top - 6, u0 + lug["l"] + 6, lug_top + 6)))
            box = (u - d / 2, z - d / 2, u + d / 2, z + d / 2)
            gap, weld = min(((math.hypot(max(b[0] - box[2], box[0] - b[2], 0.0), max(b[1] - box[3], box[1] - b[3], 0.0)), what)
                             for what, b in toes), key=lambda t: t[0])
            strip = sec.t * d
            A = sec.A - strip
            zc = (sec.A * V["db_z"] - strip * z) / A
            I = sec.I_strong + sec.A * (zc - V["db_z"]) ** 2 - (sec.t * d ** 3 / 12 + strip * (z - zc) ** 2)
            Iw = sec.I_weak - (d * sec.t ** 3 / 12 + strip * ((sec.b - sec.t) / 2) ** 2)
            edge = min(z - (zb + sec.ro), (zt - sec.ro) - z)
            edge_need = rules["edge_factor"] * d
            if u / rules["end_factor"] < edge / rules["edge_factor"]:      # the member's sawn end, 1.5 d (Table 9.6.2)
                edge, edge_need = u, rules["end_factor"] * d
            member = f"DB-{SIDES[s]}A"
            out.append(dict(member=member, face=f"{web} web", run=g["use"], x=x, y=y, z=z, d=d, length=d, runs=[g["use"]],
                            rows=[f"{member} {web} web"], frame=member, wall=f"the drawbar member's {web} web", open=False,
                            fu=rules["fu"]["rail"], fy=sec.fy, box=(x - d / 2, y - 1, z - d / 2, x + d / 2, y + 1, z + d / 2),
                            edge_mm=edge, edge_need=edge_need, toe_mm=gap, toe_need=rules["toe_factor"] * d, toe_weld=weld,
                            u_web=u, z_under=float(g["z_under"]),
                            net=dict(A=A, I=I, I_weak=Iw, Aw=sec.Aw_depth - strip, Aw_width=sec.Aw_width,
                                     z_lever=max(abs(z - d / 2 - zc), abs(z + d / 2 - zc)), y_lever=sec.b / 2,
                                     k_torsion=(sec.d - sec.t) / max(sec.d - sec.t - d, 1.0),
                                     base=dict(Z_weak=sec.Z_weak, I_weak=sec.I_weak, C=sec.C, y_max=sec.b / 2))))
        return out

    def _member_hole_sites(self, rules) -> list[dict]:
        """The holes for galvanising CHS-11 asks of the frame's other closed sections (cad/chassis_dip.py, I2-84), each in
        its member's own web: its net section, its edge distance to the web's flat and to the member's end, and its clear
        distance to the end weld's toe, to fillets along the member's bottom edges, to the fittings welded on it and to
        the member's other holes, in the web's own plane (u along the member, z across it). A hole in a rail's inner web
        inside a crossmember's end is read with the rails' holes (hole_sites). The drawbar members' apex drains are
        H-33 to H-36 already. A hinge gusset carries no frame load in the model, so its holes are placed by CHS-10's edge
        and toe rules only, as the snipe caps' vents were."""
        from .chassis import fitting_boxes
        from .chassis_dip import frame_sections
        ch, V = self.ch, self.ch.V
        mem = {m.id: m for m in ch.members}
        gr = ch.data["member_galvanising_holes"]
        _, holes = frame_sections(ch)
        attach = {"CM-05": ["CH-P06"], "CM-06": ["CH-P07"], "CM-08": ["CH-P05"]}
        boxes = {fid: [b for f in ch.fittings if f.id == fid for b in fitting_boxes(ch, f)] for fids in attach.values() for fid in fids}
        own = [h for h in holes if h["via"] == "own" and not (h["tube"].endswith("A") and h["tube"].startswith("DB-") and h["use"] == "drain")]
        out = []
        for h in own:
            m = mem.get(h["member"])
            role = m.role if m else "hinge_gusset"
            sec = m.sec if m else ch.sections[next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
            r = gr[role]
            d, z = h["d"], h["z_l"]
            u_end = h.get("u_web", min(h["u"], h["tube_L"] - h["u"]))
            edge = min((sec.d / 2 - sec.ro) - z, z + (sec.d / 2 - sec.ro))
            edge_need = rules["edge_factor"] * d
            if u_end / rules["end_factor"] < edge / rules["edge_factor"]:
                edge, edge_need = u_end, rules["end_factor"] * d
            leg = r["leg"] + r.get("clear", 0.0)
            toes = [(u_end - d / 2 - leg, "end weld" if not h["tube"].endswith("B") else "mitre's butt weld")]
            if r.get("z_bottom_leg"):
                toes.append(((z - d / 2) - (-sec.d / 2 + r["z_bottom_leg"]), "XT hinges' and jacking pads' fillets"))
            cen = np.array(h["centre"], float)
            hb = (cen[0] - d / 2, cen[1] - d / 2, cen[2] - d / 2, cen[0] + d / 2, cen[1] + d / 2, cen[2] + d / 2)
            for fid in attach.get(h["member"], []):
                for bx in boxes[fid]:
                    gb = (bx[0] - 6, bx[1] - 6, bx[2] - 6, bx[3] + 6, bx[4] + 6, bx[5] + 6)
                    toes.append((_box_gap(hb, gb), f"{fid}'s fillets"))
            for o in own:
                if o is not h and o["tube"] == h["tube"] and o["web"] == h["web"]:
                    g = math.hypot(o["u"] - h["u"], o["z_l"] - z) - (o["d"] + d) / 2
                    toes.append((g - (max(o["d"], d) - d), f"hole for {o['use']}"))
            gap, weld = min(toes, key=lambda t: t[0])
            names = {el.member for el in self.f.elements}
            frame = h["tube"] if h["tube"] in names else (m.id if m and m.id in names else None)
            strip = sec.t * d
            A = sec.A - strip
            zc = -strip * z / A
            I = sec.I_strong + sec.A * zc ** 2 - (sec.t * d ** 3 / 12 + strip * (z - zc) ** 2)
            Iw = sec.I_weak - (d * sec.t ** 3 / 12 + strip * ((sec.b - sec.t) / 2) ** 2)
            word = {"drawbar": "the drawbar member's", "cm_end": "the crossmember's", "cm_floor": "the crossmember's",
                    "cm_xt": "the XT crossmember's", "outrigger": "the outrigger's", "brace": "the cross brace's",
                    "plan_brace": "the plan brace's", "hinge_gusset": "the hinge gusset's"}[role]
            out.append(dict(member=h["member"], face=f"{h['use']}", run=h["use"], x=float(cen[0]), y=float(cen[1]), z=float(cen[2]), d=d,
                            length=d, runs=[h["use"]], rows=[f"{h['member']} {h['use']}"], frame=frame, wall=f"{word} web",
                            open=False, fu=rules["fu"]["raiser" if sec.fy < 400 else "rail"], fy=sec.fy, box=hb, edge_mm=edge, edge_need=edge_need,
                            toe_mm=gap, toe_need=rules["toe_factor"] * d, toe_weld=weld, galv=True, placement_only=frame is None,
                            u_web=u_end, z_under=float(h.get("z_under", z + sec.d / 2)),
                            net=dict(A=A, I=I, I_weak=Iw, Aw=sec.Aw_depth - strip, Aw_width=sec.Aw_width,
                                     z_lever=max(abs(z - d / 2 - zc), abs(z + d / 2 - zc)), y_lever=sec.b / 2,
                                     k_torsion=(sec.d - sec.t) / max(sec.d - sec.t - d, 1.0),
                                     base=dict(Z_weak=sec.Z_weak, I_weak=sec.I_weak, C=sec.C, y_max=sec.b / 2))))
        return out

    def hole_stress(self, res, h) -> dict:
        """Normal and combined stress at a hole's edge on the composite rail's net section, at the element end nearest it.
        A hole for galvanising is read on the element whose span holds it, at that element's end nearer the hole, so a
        load that enters the member between the hole and the next node (a hinge's welds) is counted where it passes."""
        best, bd = None, math.inf
        p = np.asarray((h["x"], h["y"], h["z"]), float)
        for span in ((True, False) if h.get("galv") else (False,)):
            for el, fl in zip(self.f.elements, res.forces):
                if el.member != h["frame"]:
                    continue
                if span:
                    a, b = np.asarray(self.f.nodes[el.i], float), np.asarray(self.f.nodes[el.j], float)
                    L2 = float(np.dot(b - a, b - a))
                    t = float(np.dot(p - a, b - a)) / L2 if L2 > 0 else 0.0
                    if not -1e-6 <= t <= 1 + 1e-6:
                        continue
                for nd, act in zip((el.i, el.j), end_actions(fl)):
                    dist = math.dist(self.f.nodes[nd], (h["x"], h["y"], h["z"])) if h.get("galv") else abs(self.f.nodes[nd][0] - h["x"])
                    if dist < bd - 1e-6 or (abs(dist - bd) < 1e-6 and abs(act["My"]) > abs(best["My"])):
                        best, bd = act, dist
            if best is not None:
                break
        n, comp = h["net"], self.ch.comp
        base = n.get("base") or dict(Z_weak=comp.Z_weak, I_weak=comp.I_weak, C=comp.C, y_max=max(comp.rail.b, comp.raiser.b) / 2)
        sig = (abs(best["N"]) / n["A"] + abs(best["My"]) * n["z_lever"] / n["I"]
               + abs(best["Mz"]) / base["Z_weak"] * (base["I_weak"] / n["I_weak"]) * (n["y_lever"] / base["y_max"]))
        tau = abs(best["T"]) / base["C"] * n["k_torsion"] + max(abs(best["Vz"]) / n["Aw"], abs(best["Vy"]) / n["Aw_width"])
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
            row = {key: h[key] for key in ("id", "member", "face", "x", "y", "z", "d", "length", "runs", "wall", "open", "u_web", "z_under") if key in h}
            if h.get("open"):
                out.append(dict(row, ok=True, static_ok=True, place_ok=True, util=0.0))
                continue
            if h.get("placement_only"):
                # a hinge gusset's holes: no frame load in the model, so CHS-10's edge and toe rules only
                edge_ok, toe_ok = h["edge_mm"] >= h["edge_need"] - 1e-6, h["toe_mm"] >= h["toe_need"] - 1e-6
                out.append(dict(row, rows=h["rows"], frame=None, static=None, static_ok=True, util=0.0, range_mpa=0.0, peak_mpa=0.0,
                                field=None, cafl=0.585 * rules["fat"], damage=0.0, fat_case=None, fat_ok=True, edge_mm=h["edge_mm"],
                                edge_need=h["edge_need"], edge_ok=edge_ok, toe_mm=h["toe_mm"], toe_need=h["toe_need"], toe_weld=h["toe_weld"],
                                toe_ok=toe_ok, place_ok=edge_ok and toe_ok, ok=edge_ok and toe_ok, placement_only=True))
                continue
            worst = None
            ult = None
            for lc_id, e in env.items():
                r = e.get(k)
                if r is None:
                    continue
                if lc_id == "LC8u":       # the ultimate pull: no fracture of the net section (AS 4100 7.2, 0.85 fu), CHS-08U
                    lim = rules["fu_factor"] * h["fu"]
                    ult = dict(util=r["eq"] / lim, mpa=r["eq"], limit=lim, lc=lc_id, case=r["case"])
                    continue
                lim = min(h.get("fy", fy), rules["fu_factor"] * h["fu"]) / lcs[lc_id]["factor"]
                u = r["eq"] / lim
                if worst is None or u > worst["util"]:
                    worst = dict(util=u, mpa=r["eq"], limit=lim, lc=lc_id, case=r["case"])
            ds, cid = max(((self.hole_stress(res, h)["sigma"], c) for c, res in lc1.items()), key=lambda t: t[0])
            peak = rules["kt"] * ds
            field = None
            if h.get("plate_field"):
                # a drain close behind the end plate stands in the field of the plate's weld into the web (I2-80): its
                # normal range across the weld adds to the beam's along the rail, with the shear along the weld, and
                # Kirsch's largest hoop stress in that biaxial field is 3 s1 - s2 (est., the field undiminished)
                for c, res in lc1.items():
                    sb = self.hole_stress(res, h)["sigma"]
                    sp_, tp = self.plate_field(res, h)
                    sx = sb + sp_
                    r = math.hypot(sx / 2, tp)
                    hoop = 3 * (sx / 2 + r) - (sx / 2 - r)
                    if hoop > peak:
                        peak, ds, cid, field = hoop, sb, c, dict(beam=sb, plate=sp_, shear=tp)
            cafl = 0.585 * rules["fat"]
            dmg = _miner(rules["fat"], lc10["occasional_factor"] * peak, lc10)
            fat_ok = peak <= cafl and dmg <= lc10["miner_limit"]
            edge_ok, toe_ok = h["edge_mm"] >= h["edge_need"] - 1e-6, h["toe_mm"] >= h["toe_need"] - 1e-6
            out.append(dict(row, rows=h["rows"], frame=h["frame"], static=worst, static_ok=worst["util"] <= 1 + 1e-9, util=worst["util"],
                            ultimate=ult,
                            range_mpa=ds, peak_mpa=peak, field=field, cafl=cafl, damage=dmg, fat_case=cid, fat_ok=fat_ok,
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


PLATE_STENCIL = ((0, 0, 20.0), (1, 0, -8.0), (-1, 0, -8.0), (0, 1, -8.0), (0, -1, -8.0), (1, 1, 2.0), (1, -1, 2.0),
                 (-1, 1, 2.0), (-1, -1, 2.0), (2, 0, 1.0), (-2, 0, 1.0), (0, 2, 1.0), (0, -2, 1.0))


def end_plate(span: float, height: float, z0: float, z1: float, q0: float, q1: float, foot: float, h: float = 1.0,
              free_bottom: bool = True, nu: float = NU, centre: float | None = None, km: float = 0.0) -> dict:
    """The rail's end plate under the gusset heel's line load (FAT-19, FAT-20, I2-57, I2-60): a Kirchhoff plate `span` mm
    between the rail's webs and `height` mm from its bottom edge to the rail's top flange, simply supported on the webs
    and the top flange it is welded to, and free along its bottom edge, which rests unwelded on the drawbar member (or
    simply supported there too). The load runs up the plate `centre` mm from the first web (its middle by default) from
    z0 to z1 mm above the bottom edge, rising from q0 to q1 N/mm and spread over `foot` mm across. With it goes a line
    moment of km times the line load (N mm per mm), its axis up the plate, which pulls harder towards the second web: the
    moment of a force along the plate applied at its face. Biharmonic finite differences on a grid h mm apart, the free
    edge's moment and Kirchhoff shear held at zero by two rows of ghost points (Timoshenko and Woinowsky-Krieger, Theory
    of plates and shells, 1959, chapters 4 and 5). Returns the largest moment across the span (N mm per mm), the
    Kirchhoff edge shear each web carries along its height (`webs`, the first web's and the second's) and the top along
    its width (N/mm, positive where the wall holds the plate back against the load, so its weld is pulled), each corner's
    force (N, negative where it presses the plate onto the walls' ends, `_far` at the second web) and the load (N). Two
    webs, the top and the four corners carry the load."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    nx, nz = round(span / h), round(height / h)
    j0 = 0 if free_bottom else 1
    index = {(i, j): n for n, (i, j) in enumerate((i, j) for j in range(j0, nz) for i in range(1, nx))}
    memo: dict = {}

    def comb(*terms):
        out: dict = {}
        for c, d in terms:
            for k, v in d.items():
                out[k] = out.get(k, 0.0) + c * v
        return out

    def w(i, j):
        if (i, j) not in memo:
            memo[i, j] = ghost(i, j)
        return memo[i, j]

    def ghost(i, j):
        """Point (i, j) as a sum over the unknowns: zero on a supported edge, odd across it beyond, and below the free
        edge the two rows that make its moment and Kirchhoff shear vanish."""
        if i in (0, nx) or j == nz or (j == 0 and not free_bottom):
            return {}
        if i < 0 or i > nx:
            return comb((-1.0, w(-i if i < 0 else 2 * nx - i, j)))
        if j > nz or (j < 0 and not free_bottom):
            return comb((-1.0, w(i, 2 * nz - j if j > nz else -j)))
        if j == -1:
            return comb((2 + 2 * nu, w(i, 0)), (-1.0, w(i, 1)), (-nu, w(i + 1, 0)), (-nu, w(i - 1, 0)))
        if j == -2:
            k = 2 - nu
            return comb((1.0, w(i, 2)), (-2.0 - 2 * k, w(i, 1)), (2.0 + 2 * k, w(i, -1)), (k, w(i + 1, 1)), (k, w(i - 1, 1)),
                        (-k, w(i + 1, -1)), (-k, w(i - 1, -1)))
        return {index[i, j]: 1.0}

    uc = span / 2 if centre is None else centre
    feet = [i * h - uc for i in range(1, nx) if abs(i * h - uc) <= foot / 2 + 1e-9]
    ubar = sum(feet) / len(feet)
    lever = sum((u - ubar) ** 2 for u in feet) * h    # spreads the line moment over the foot as a linear pull across it

    def load(i, j):
        z, u = j * h, i * h - uc
        if abs(u) > foot / 2 + 1e-9 or not z0 <= z <= z1:
            return 0.0
        q = q0 + (q1 - q0) * (z - z0) / (z1 - z0)
        return q / (len(feet) * h) + km * q * (u - ubar) / lever

    rows, cols, vals, rhs = [], [], [], np.zeros(len(index))
    for (i, j), n in index.items():
        for k, v in comb(*((c, w(i + di, j + dj)) for di, dj, c in PLATE_STENCIL)).items():
            rows.append(n), cols.append(k), vals.append(v)
        rhs[n] = load(i, j) * h ** 4
    sol = spsolve(sp.csr_matrix((vals, (rows, cols)), shape=(len(index), len(index))), rhs)

    def at(i, j):
        return sum(v * sol[k] for k, v in w(i, j).items())

    def d2(i, j, di, dj):
        return (at(i + di, j + dj) - 2 * at(i, j) + at(i - di, j - dj)) / h ** 2

    def twist(i, j):
        return 2 * (1 - nu) * (at(i + 1, j + 1) - at(i + 1, j - 1) - at(i - 1, j + 1) + at(i - 1, j - 1)) / (4 * h ** 2)
    mx = max(abs(d2(i, j, 1, 0) + nu * d2(i, j, 0, 1)) for i, j in index)

    def edge(i0, di):
        """The Kirchhoff edge shear along the web at column i0, the plate lying on the side di of it."""
        return [-((at(i0 + 2 * di, j) - 2 * at(i0 + di, j) + 2 * at(i0 - di, j) - at(i0 - 2 * di, j)) / (2 * h ** 3)
                  + (2 - nu) * (d2(i0 + di, j, 0, 1) - d2(i0 - di, j, 0, 1)) / (2 * h)) for j in range(1, nz)]
    top = [(at(i, nz + 2) - 2 * at(i, nz + 1) + 2 * at(i, nz - 1) - at(i, nz - 2)) / (2 * h ** 3)
           + (2 - nu) * (d2(i, nz + 1, 1, 0) - d2(i, nz - 1, 1, 0)) / (2 * h) for i in range(1, nx)]
    total = sum(load(i, j) for i, j in index) * h ** 2
    # the corner forces of the plate's twist (2 M_xz), negative where they press the plate onto the walls' ends
    return dict(moment=mx, webs=(np.array(edge(0, 1)), np.array(edge(nx, -1))), top=np.array(top),
                corner_top=twist(0, nz), corner_bottom=-twist(0, 0), corner_top_far=-twist(nx, nz), corner_bottom_far=twist(nx, 0),
                load=total, h=h)


def heel_throats(legs, angle: float) -> tuple[float, float]:
    """The throats (mm) of the root gusset's two heel fillets, `legs` (inboard, outboard) mm along each face, on the
    skewed T-joint the gusset makes with the end plate, its line `angle` radians off the plate's normal in plan and
    running inboard to its toe (I2-72): the inboard fillet lies in the acute dihedral angle of 90 degrees less that and
    the outboard one in the obtuse angle of 90 degrees more, and a flat-faced fillet with equal legs in an angle psi has
    a throat of its leg times cos(psi / 2)."""
    inboard, outboard = legs
    return inboard * math.cos(math.pi / 4 - angle / 2), outboard * math.cos(math.pi / 4 + angle / 2)


def kirsch_along(a: float, dx: float, dz: float) -> float:
    """Kirsch's stress along the load at a point dx along it and dz across it from the centre of a hole of radius a in a
    plate under a uniaxial stress, over that stress: 3 at the hole's side, under 1 ahead of it, and within 8 % at one
    diameter from its edge."""
    r = math.hypot(dx, dz)
    if r <= a:
        return 3.0
    th = math.atan2(dz, dx)
    q2, q4 = (a / r) ** 2, (a / r) ** 4
    srr = 0.5 * (1 - q2) + 0.5 * (1 - 4 * q2 + 3 * q4) * math.cos(2 * th)
    stt = 0.5 * (1 + q2) - 0.5 * (1 + 3 * q4) * math.cos(2 * th)
    trt = -0.5 * (1 + 2 * q2 - 3 * q4) * math.sin(2 * th)
    c, s = math.cos(th), math.sin(th)
    return srr * c * c + stt * s * s - 2 * trt * s * c


def principal_range(sigma: float, tau: float) -> tuple[float, float]:
    """A weld's maximum principal stress range from its normal range `sigma` across it and its shear range `tau` along
    it, the two in phase (IIW-1823-07 section 4.2 b), MPa, and the angle of its direction off the weld's normal,
    degrees. With no stress along the weld that direction lies within 45 degrees of the normal, inside the 60 degrees
    to which IIW 4.3 holds the principal stress, so IIW's interaction of normal and shear, which it keeps for stresses
    out of phase and for directions further off the normal (Table 4.3-1), never applies to such a weld."""
    half = abs(sigma) / 2
    return half + math.hypot(half, tau), math.degrees(math.atan2(2 * abs(tau), abs(sigma))) / 2


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

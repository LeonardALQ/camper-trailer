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
from typing import Any

import numpy as np

from .chassis import SIDES, Chassis, Composite, hole_x
from .frame import end_actions

G = 9.81
SKIP_SYSTEMS = {"chassis", "drawbar"}           # replaced by the designed members and fittings
SKIP_IDS = {"SP-03"}                            # the spare wheel bracket estimate, replaced by the carrier posts
UNSPRUNG = {"RG-01", "RG-02", "RG-06"}
ROOF = {"BD-02", "BD-08", "RF-01"}
RAILS = {"BD-10", "RG-03", "RG-04", "RG-05"}   # hung from the rails: mud flaps, the TSC unit and the XT Air box under the floor
CELL = 200.0
# VSB1's drawbar and chain tests, made with the body held on a rig at its suspension mounts (VSB1 Rev 6 14.2.1): the
# hinge joints' rows give them beside and do not read them (CHS-18, CHS-19, the conductor's ruling of 27 Nov 2026)
RIG_CASES = ("LC6", "LC6b")
UNCAPPED = 1e30                                 # N: the side force cap of a support that holds whatever it is asked (LC8a)
ROOT_GUSSET, ROOT_END_PLATE = "CH-P03", "CH-P15"   # the drawbar root's gusset and the rail's end plate its heel is welded to
ROOT_PLACES = {"root_splice": "DB-{side}A's mitre at X {x:.0f}", "root_heel_weld": "CH-P03's heel, DB-{side}",
               "root_end_plate": "CH-P15 on RL-{side}", "root_end_plate_weld": "CH-P15's welds to RL-{side}, {weld}"}
ROOT_READERS = {"run_root": "run_root_stresses", "cheek_root": "cheek_root_stresses"}   # FAT-26 and FAT-27 (I2-125)
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
        self.body_segs = body
        self._use(ch.frame(body, hinges))
        self.atm = tr.caps()["plated"]       # the frame model runs at the plated ATM
        galv = ch.galvanising()
        self.galv_rate = {r["t"]: r["kg_per_m2"] for r in galv["rows"]}
        self.chassis_items = self._chassis_items()

    def _use(self, fm):
        """Make frame model fm the one every solve and reading uses, its supports factorised once: the kinematic six at
        the ball and the rear airbags' rail nodes, and the body's at the pivots and the airbags."""
        self.fm, self.f = fm, fm.f
        self.n = 6 * len(fm.f.nodes)
        if not hasattr(fm, "solvers"):
            ch = self.ch
            rear = [w for w in ch.suspension if w["axle"] == "rear"]
            rk, rr = (fm.rail_node(s, rear[0]["airbag"][0]) for s in (-1, 1))
            kinematic = fm.f.prepare([(fm.ball, 0), (fm.ball, 1), (fm.ball, 2), (rk, 2), (rr, 2), (rk, 1)])
            body = []
            for w in ch.suspension:
                body += [(fm.pivot_nodes[w["id"]], d) for d in range(3)]
                body.append((fm.rail_node(w["side"], w["airbag"][0]), 2))
            fm.solvers = (kinematic, fm.f.prepare(body))
        self.kinematic, self.body = fm.solvers
        self.__dict__.pop("_gussets", None)

    def bar_models(self) -> list[tuple[str, Any]]:
        """The frame models every check is read on (xt_hinges `bar` `bounds` and `bushes`, I2-114): the hinge bars rigid,
        the model built first, and the hinge bars elastic at their own section on each bound of the arms' bushes, free and
        stiff. Cruisemaster gives no section for the bar and no stiffness for its bushes, so each reading takes the worst
        of them. With the body as a torsion box (cad/body.py) the rigid bars alone."""
        bar = self.ch.data["xt_hinges"]["bar"]
        if self.hinges != "crossmember" or self.body_segs:
            return [("rigid", self.fm)]
        out = []
        for b in bar.get("bounds") or ["rigid"]:
            if b == "rigid":
                out.append(("rigid", self.fm))
            else:
                out += [(f"{b} on {k} bushes", self.ch.frame(None, self.hinges, b, k)) for k in bar.get("bushes") or ["free"]]
        return out

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
                    out += self._tank_items(b.iid, b.name, share, t, b.cog[2])
                continue
            if b.extra.get("tank") and hasattr(lay, "tank_bearers"):
                out += self._tank_items(b.iid, b.name, m, b, b.cog[2])
                continue
            if b.id in ("UF-08", "UF-08W") and hasattr(lay, "tank_bearers"):
                out += self._tank_items(b.iid, b.name, m, lay.find("UF-08"), b.cog[2])
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

    def _tank_items(self, iid, name, m, tank, z) -> list[Item]:
        """A tank's mass m, or its water's share, where its bearers put it on the frame (I2-109, I2-122, Layout.tank_bearers):
        the front tank's two ends on their pairs on the XT crossmembers and the grey tank's, with its grey water, on theirs
        on the XT rear shock and rear crossmembers (UF-08B), each by the tank's centre's place between their bearing
        lines, and the rear tank's front end on its pair on the XT centre crossmember as if the tank spanned to its rear
        end, the rest through the rear bay's shear panel to its bolts on the rails' angles and under the XT rear shock
        crossmember by the lever rule. Each pair's share goes to its crossmember at each bearer's middle, by its length.
        A tank with no bearers is shared by the two rails over its box, as before."""
        lay = self.lay
        brs = [b for b in lay.tank_bearers() if b["tank"] == tank.id]
        if not brs:
            return self._sliced(iid, name, m, tank.box, z, "rails")
        xc = (tank.box[0] + tank.box[3]) / 2
        line = {}
        for b in brs:
            rx0, _, _, rx1, _, _ = b["boxes"]["rubber"]
            line[b["e"]] = (max(rx0, tank.box[0]) + rx1) / 2 if b["e"] > 0 else (rx0 + min(rx1, tank.box[3])) / 2
        out = []

        def on_pair(e, share):
            pair = [b for b in brs if b["e"] == e]
            tot = sum(b["length"] for b in pair)
            for b in pair:
                out.append(Item(iid, name, share * b["length"] / tot, (line[e], (b["y"][0] + b["y"][1]) / 2, z), f"cm:{b['member']}"))

        if len(line) == 2:
            xf, xr = line[1], line[-1]
            front = m * (xr - xc) / (xr - xf)
            on_pair(1, front)
            on_pair(-1, m - front)
            return out
        e = next(iter(line))
        xf, xr = line[e], tank.box[3] - 25.0
        front = m * (xr - xc) / (xr - xf)
        on_pair(e, front)
        pn = self.ch.shear_panels()
        rest = m - front
        if not pn:
            return out + self._sliced(iid, name, rest, tank.box, z, "rails")
        rail_b = [b for b in pn[0]["bolts"] if b["group"] == "rail"]
        rear_b = [b for b in pn[0]["bolts"] if b["group"] == "rear"]
        xa, xb = sum(b["x"] for b in rail_b) / len(rail_b), sum(b["x"] for b in rear_b) / len(rear_b)
        cm6 = pn[0]["ties"][0]["cm"]                      # the crossmember the panel's rear bolts hang under
        to_rear = rest * min(max((xr - xa) / (xb - xa), 0.0), 1.0)
        for b in rail_b:
            out.append(Item(iid, name, (rest - to_rear) / len(rail_b), (b["x"], b["y"], z), "rails"))
        for b in rear_b:
            out.append(Item(iid, name, to_rear / len(rear_b), (b["x"], b["y"], z), f"cm:{cm6}"))
        return out

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
        if it.rule.startswith("cm:"):           # on a crossmember at its Y (a tank's bearers, I2-109, I2-122)
            return fm.crossmember_fractions(it.rule[3:], y)
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
        do it all). `twist_n` adds the diagonal pattern of one wheel in a hole. `lifted` (a side and an axle) is the
        jacking case (LC8b): that side's wheels carry nothing and a jack under that axle's arm on that side, at
        Cruisemaster's jacking point under the arm by the hub, takes the load, the air released from the springs."""
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
            side, axle = lifted
            far = [w for w in wheels if w["side"] != side]
            jw = next(w for w in wheels if w["side"] == side and w["axle"] == axle)
            jx, jy = jw["hub"][0], jw["hub"][1]
            # unknowns: ball Fz, far wheel Fz (each), the jack's Fz. Fz, Mx, My
            A = np.array([[1, 2, 1],
                          [0, 2 * far[0]["contact"][1], jy],
                          [0, -(far[0]["contact"][0] + far[1]["contact"][0]), -jx]])
            sol = np.linalg.solve(A, -np.array([Fa[2], Ma[0], Ma[1]]))
            contact = {w["id"]: np.array([0, 0, sol[1]]) if w["side"] != side else np.zeros(3) for w in wheels}
            return dict(ball=np.array([0, 0, sol[0]]), contact=contact, jack=(np.array([0, 0, sol[2]]), jw["id"]))
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
        has no droop strap), along the shock's own line at ride (Chassis.shock_line), from its lower eye on the arm, 67 mm
        behind and 13 mm under the hub, to its top eye in its bracket's inboard clevis 40 mm off the support plate CH-P07,
        the front arms' on the front shocks' own crossmember and the rear arms' on the XT rear shock crossmember. `u` is the
        unit vector from the arm's eye to the bracket and `lever` the moment about the pivot's Y axis of a unit pull along
        it, negative for a pull that lifts the hub. The pull reaches the frame at the top eye, its moment about the
        crossmember's nodes kept (_apply)."""
        if getattr(self, "_droop", None):
            return self._droop
        ch = self.ch
        d = ch.data["xt_arms"]["droop"]
        cms = {m.station: m for m in ch.members if m.role.startswith("cm")}
        out = {}
        for w in ch.suspension:
            cm = cms[d["to"][w["axle"]]]
            arm, frame = (np.array(p, float) for p in ch.shock_line(w))
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
        # the jack pushes up under its arm by the hub, so its force reaches the frame through the arm's airbag, its bump
        # stop with the air released, and its hinge, as an obstacle's force at a hub does in LC8a
        arms = self.arm_loads(items, acc, R["contact"], q, hub={R["jack"][1]: R["jack"][0]} if lifted is not None else None)
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
        return res, dict(ball=R["ball"], arms=arms, residual_n=resid, jack=R.get("jack", [None, None]))

    def recovery_reactions(self, F, p, held: str | tuple | None = None, base: dict | None = None, nose: dict | None = None,
                           mu: float | None = None) -> dict:
        """LC8a's reaction, which report 11 does not give: the ground at the four tyres, the trailer a rigid body on each
        wheel's support stiffness, its tyre and arm in series (LC8a's reaction, est.). The wheels are unbraked, so the
        ground's force on each passes through its hub: along the trailer every wheel takes its share there, or with `held`
        that wheel is held fast against an obstacle at its hub's height and the other three roll free, or with `held` a
        pair, both wheels of one axle are (I2-93). Up, every tyre works at its vertical rate at its contact, and across at
        its lateral rate up to its grip, `mu` times its load from the vertical solve (LC8a `reaction` `mu`, I2-124): a tyre
        the rates would ask for more slides across at its grip, and one off the ground holds nothing across. With one wheel
        held, its axle-mate rolls along as the trailer turns about the held hub and takes nothing across (est.). Where the
        free tyres' grip cannot hold the pull's moment about that hub, the trailer turns about it until the pull's line
        stands where their grip holds it, each of them sliding across at its grip, and the held hub takes the rest. With
        every wheel free, a side force their grip cannot hold slides the trailer sideways, so the pull is taken at the
        largest share of it the trailer holds, as a pull that tips it is. `mu` None leaves the side rates uncapped.

        `base` is the trailer's weight as the static case reacts it (reactions, 1 g down): each tyre and the nose start
        from that load (I2-94). No tyre can pull the ground, so one that would leaves it and the trailer pitches or rolls
        onto the supports that remain, the `nose` at the ball among them: on its jockey wheel, which cannot pull either, or
        held both ways by the coupled truck (LC8a `reaction` `nose`, est.). A bogged tyre that lifts stays in its rut
        along the trailer, which holds it there at its rate (est.). The set of supports in contact is iterated until every
        one in contact pushes and none off the ground would, and the grip with the tyres' loads until the loads settle.
        Where no set holds the trailer at the whole pull it tips, so the pull is taken at the largest share of it that the
        trailer holds (`scale`, `limit` saying whether it tips or slides). Without `base` no support lifts. Returns the
        force the ground puts on each tyre at its contact and on each wheel at its hub, the nose's force, the pull as the
        trailer takes it (`pull`, scaled and turned), the tyres off the ground, their rise on the rates (`lift`), the turn
        (`turn`, the pull's heading off the rail axis asked, taken and through the held hub, in degrees) and the grip."""
        r = next(lc for lc in self.ch.data["load_cases"] if lc["id"] == "LC8a")["reaction"]
        wheels = self.ch.suspension
        held_ids = () if held is None else (held if isinstance(held, tuple) else (held,))
        one = isinstance(held, str)
        mates = {w["id"] for w in wheels if one and w["id"] != held and w["axle"] == next(x["axle"] for x in wheels if x["id"] == held)}
        flat = []
        for w in wheels:
            obstacle = w["id"] in held_ids
            for d, k in ((0, r["kx"]), (1, r["ky"])):
                at = w["hub"] if (d == 0 or obstacle) else w["contact"]
                if held is not None and not obstacle and (d == 0 or w["id"] in mates):
                    k = 0.0
                elif obstacle:
                    k = r["held_k"]
                if k:
                    flat.append(dict(w=w["id"], d=d, k=float(k), at=np.asarray(at, float), on="hub" if obstacle or d == 0 else "contact",
                                     grip=None if obstacle or d == 0 else w["id"]))
        vert = [dict(w=w["id"], k=r["kz"], at=np.asarray(w["contact"], float), pre=float(base["contact"][w["id"]][2]) if base else 0.0,
                     on="contact", contact=w["id"]) for w in wheels]
        if base and nose:
            vert.append(dict(w="nose", k=nose["kz"], at=np.array([0.0, 0.0, self.ch.V["coupling_z"]]), pre=float(base["ball"][2]),
                             on="nose", contact=None if nose.get("holds_down") else "nose"))
        gp = np.array([[1.0, 0.0, -s["at"][1]] if s["d"] == 0 else [0.0, 1.0, s["at"][0]] for s in flat])   # X, Y and yaw
        kp = np.array([s["k"] for s in flat])
        gripped = np.array([s["grip"] is not None for s in flat])
        gv = np.array([[1.0, s["at"][1], -s["at"][0]] for s in vert])                                      # Z, roll and pitch
        kv = np.array([float(s["k"]) for s in vert])
        pre = np.array([s["pre"] for s in vert])
        ground = np.array([bool(base) and s["contact"] is not None for s in vert])
        sp, sv = np.array([1.0, 1.0, 1e-3]), np.array([1.0, 1e-3, 1e-3])                                # rotations as mm at 1 m
        p = np.asarray(p, float)
        F0 = np.asarray(F, float)

        def plan(Fv, caps):
            """The forces along and across on the rates, each tyre's across up to its cap (elastic, then sliding at its
            grip), or None where no set of them holds the pull in plan."""
            load = np.array([Fv[0], Fv[1], p[0] * Fv[1] - p[1] * Fv[0]])
            sgn = np.zeros(len(flat))
            for _ in range(4 * len(flat) + 4):
                el = sgn == 0
                K = (gp[el].T * kp[el]) @ gp[el]
                ev = np.linalg.eigvalsh(K * sp[:, None] * sp[None, :])
                if ev[0] < 1e-10 * ev[-1]:
                    return None
                u = np.linalg.solve(K, load + (sgn * caps)[~el] @ gp[~el])
                f = -kp * (gp @ u)
                over = np.where(el & gripped & (np.abs(f) > caps + 1e-6))[0]
                back = np.where(~el & (caps > 0) & (sgn * f < caps - 1e-6))[0]
                if len(over):
                    i = over[np.argmax(np.abs(f[over]) - caps[over])]
                    sgn[i] = math.copysign(1.0, f[i])
                elif len(back):
                    sgn[back[np.argmin(sgn[back] * f[back] - caps[back])]] = 0.0
                else:
                    return np.where(el, f, sgn * caps)
            return None

        def turned(Fv, caps):
            """One wheel held and the free tyres' grip short of the pull's moment about its hub: the trailer turns about
            the hub until the moment is what their grip holds, each sliding across against the turn, the hub the rest."""
            h = np.asarray(next(w["hub"] for w in wheels if w["id"] == held), float)
            d = p[:2] - h[:2]
            fh = math.hypot(Fv[0], Fv[1])
            dx = np.array([s["at"][0] - h[0] for s in flat])
            mf = float(np.sum(np.where(gripped, caps * np.abs(dx), 0.0)))
            m0 = d[0] * Fv[1] - d[1] * Fv[0]
            sg = math.copysign(1.0, m0)
            phi = math.atan2(d[1], d[0]) + (sg * math.asin(min(1.0, mf / (math.hypot(*d) * fh))) if fh > 0 else 0.0)
            Ft = np.array([fh * math.cos(phi), fh * math.sin(phi), Fv[2]])
            mt = d[0] * Ft[1] - d[1] * Ft[0]
            f = np.where(gripped, -(mt / mf if mf > 0 else 0.0) * caps * np.sign(dx), 0.0)
            rest = -(Ft[:2] + np.array([0.0, float(np.sum(np.where(gripped, f, 0.0)))]))
            for i, s in enumerate(flat):
                if s["w"] == held:
                    f[i] = rest[s["d"]]
            return Ft, f

        def sliding(Fv, caps):
            """Every wheel free and the tyres' grip short of the side force: each tyre across at its grip against it and
            the hubs along the trailer holding the pull along and in yaw, so the loads up can be found with them before
            the slide is judged on the tyres' settled loads."""
            load = np.array([Fv[0], Fv[1], p[0] * Fv[1] - p[1] * Fv[0]])
            f = np.where(gripped, -math.copysign(1.0, Fv[1]) * caps, 0.0)
            rest = load + f @ gp
            K = (gp[~gripped].T * kp[~gripped]) @ gp[~gripped]
            u = np.zeros(3)
            u[[0, 2]] = np.linalg.solve(K[np.ix_([0, 2], [0, 2])], rest[[0, 2]])
            return np.where(gripped, f, -kp * (gp @ u))

        def vertical(left):
            """The forces up on the supports that can only push, and the tyres off the ground, or None where it tips."""
            off: set = set()
            for _ in range(40):
                on = np.array([s["contact"] not in off for s in vert])
                K = (gv[on].T * kv[on]) @ gv[on]
                ev = np.linalg.eigvalsh(K * sv[:, None] * sv[None, :])
                if ev[0] < 1e-6 * ev[-1]:
                    return None
                u = np.linalg.solve(K, left - (pre[~on] @ gv[~on] if (~on).any() else 0.0))
                f = pre - kv * (gv @ u)
                neg = [i for i, s in enumerate(vert) if ground[i] and on[i] and f[i] < -1e-6]
                back = [i for i, s in enumerate(vert) if ground[i] and not on[i] and f[i] > 1e-6]
                if neg:
                    off.add(vert[min(neg, key=lambda i: f[i])]["contact"])
                elif back:
                    off.discard(vert[max(back, key=lambda i: f[i])]["contact"])
                else:
                    return f, off, {vert[i]["contact"]: -f[i] / kv[i] for i in range(len(vert)) if ground[i] and not on[i]}
            return None

        def state(lam: float):
            """The reaction at `lam` of the pull, the grip iterated with the tyres' loads, or None and why it fails."""
            Fv = lam * F0
            N = {s["w"]: max(s["pre"], 0.0) for s in vert if s["on"] == "contact"}
            out = None
            for _ in range(30):
                caps = np.array([mu * N[s["grip"]] if (mu is not None and s["grip"] is not None) else UNCAPPED for s in flat])
                fp, Ft, turn, slid = plan(Fv, caps), Fv, False, False
                if fp is None and one:
                    (Ft, fp), turn = turned(Fv, caps), True
                elif fp is None:
                    fp, slid = sliding(Fv, caps), True
                left = np.r_[Ft, np.cross(p, Ft)]
                for i, s in enumerate(flat):
                    e = np.eye(3)[s["d"]] * fp[i]
                    left = left + np.r_[e, np.cross(s["at"], e)]
                got = vertical(left[[2, 3, 4]])
                if got is None:
                    return None, "tips"
                f, off, lift = got
                Nn = {s["w"]: (0.0 if s["contact"] in off else max(float(f[i]), 0.0)) for i, s in enumerate(vert) if s["on"] == "contact"}
                out = dict(fp=fp, Ft=Ft, turn=turn, f=f, off=off, lift=lift, N=Nn, caps=caps)
                if mu is None or max(abs(Nn[k] - N[k]) for k in N) < 0.5:
                    break
                N = Nn
            return (None, "slides") if slid else (out, None)

        lam, (st, why) = 1.0, state(1.0)
        limit = None
        if st is None:
            limit = why
            lo, hi, st = 0.0, 1.0, state(0.0)[0]
            for _ in range(14):
                mid = (lo + hi) / 2
                trial, w = state(mid)
                if trial is None:
                    hi, limit = mid, w
                else:
                    lo, st = mid, trial
            lam = lo
        contact = {w["id"]: np.zeros(3) for w in wheels}
        hub, nose_f = {}, np.zeros(3)
        for i, s in enumerate(flat):
            v = np.eye(3)[s["d"]] * float(st["fp"][i])
            if s["on"] == "hub":
                hub[s["w"]] = hub.get(s["w"], np.zeros(3)) + v
            else:
                contact[s["w"]] = contact[s["w"]] + v
        for i, s in enumerate(vert):
            if s["contact"] in st["off"]:
                continue
            v = np.array([0.0, 0.0, float(st["f"][i])])
            if s["on"] == "nose":
                nose_f = nose_f + v
            else:
                contact[s["w"]] = contact[s["w"]] + v
        sx = 1.0 if F0[0] >= 0 else -1.0

        def heading(v) -> float:
            return math.degrees(math.atan2(v[1], sx * v[0])) if math.hypot(v[0], v[1]) > 0 else 0.0
        turn = dict(asked=heading(F0), taken=heading(st["Ft"]), turned=bool(st["turn"]))
        if one:
            h = next(w["hub"] for w in wheels if w["id"] == held)
            turn["through"] = heading(p[:2] - np.asarray(h[:2], float))
        side = float(sum(st["fp"][i] for i in range(len(flat)) if gripped[i]))
        return dict(contact=contact, hub=hub, nose=nose_f, off=sorted(st["off"]), scale=lam, lift=st["lift"], pull=np.asarray(st["Ft"], float),
                    limit=limit, turn=turn, grip=dict(mu=mu, side=side, sliding=[flat[i]["w"] for i in range(len(flat))
                                                                               if gripped[i] and 0 < st["caps"][i] <= abs(st["fp"][i]) + 1e-3]))

    def run_recovery(self, F, p, fractions, held: str | tuple | None = None, support: dict | None = None, mu: float | None = None,
                     R: dict | None = None):
        """LC8a: the pull at its recovery point with the trailer's weight and its nose's support (`support`, I2-94), the
        tyres' and the nose's reactions through supports that cannot pull, the tyres' side forces within their grip `mu`
        (recovery_reactions, or `R` where they are already solved), the pull as the trailer takes it, each arm a free body
        about its hinge, its airbag taking its moment or its droop limit the part its airbag cannot (arm_loads), and the
        frame held only by the six kinematic supports."""
        q = np.zeros(self.n)
        acc = (0.0, 0.0, -1.0) if support else (0.0, 0.0, 0.0)
        items = support["items"] if support else []
        base = support["base"] if support else None
        if R is None:
            R = self.recovery_reactions(F, p, held, base, support["nose"] if support else None, mu)
        self._apply(np.asarray(R["pull"], float), p, fractions, q)
        bag_min = None
        if support:
            q += support["q"]
            self._apply(R["nose"], (0.0, 0.0, self.ch.V["coupling_z"]), [(self.fm.ball, 1.0)], q)
            bag_min = support["bag_min"]
        arms = self.arm_loads(items, acc, R["contact"], q, hub=R["hub"], bag_min=bag_min)
        res = self.kinematic.solve(q)
        self.resid = max(self.resid, max(abs(v) for v in res.reactions.values()))
        return res, dict(R, arms=arms, bag_min=bag_min)

    def recovery_point(self, where: str, s: int) -> tuple[tuple[float, float, float], list[tuple[int, float]], int]:
        """LC8a's pull point, the frame nodes it loads and the sign of its pull along the trailer: a front lug on side s,
        pulled forward, a rear tongue at its shackle hole, pulled rearward (rear_recovery_point), or the coupling's ball."""
        V = self.ch.V
        if where == "front":
            x = V["front_recovery_x"]
            return (x, s * (V["rail_c"] + 35), V["db_z"]), [(self.fm.db_node(s, x), 1.0)], -1
        if where == "rear":
            p, cm = self.rear_recovery_point(s)
            return p, [(self.fm.cm_node(cm, s * V["rail_c"]), 1.0)], 1
        return (0.0, 0.0, V["coupling_z"]), [(self.fm.ball, 1.0)], -1

    def recovery_pulls(self, lc8: dict, s: int) -> list[tuple[str, Any, float, float]]:
        """LC8a's pulls at one point, each its label, the wheels held, its heading off the rail axis and its share of the
        rated pull: every wheel free at the free limit (I2-118, I2-119, I2-127), one wheel held at the held-wheel limit
        (I2-93, I2-124) and both wheels of one axle held at the held-axle limit, each at LC8a's five headings, 30 and 15
        degrees either way and along the axis. At the coupling (s 0) every pull is along the rail axis, a held wheel's
        too, the free tyres' grip turning the trailer about it as far as it does."""
        sd = lc8["sideways_deg"]
        rated = lc8["force_n"]
        free = lc8.get("free_n", rated)
        at_free = f", at the {free / 1000:g} kN limit" if free < rated - 1e-6 else ""
        five = (-sd, -sd // 2, 0, sd // 2, sd) if s else (0,)
        pulls = [(f"{h:+d} deg sideways{at_free}", None, math.radians(h), free / rated) for h in five]
        for w in self.ch.suspension:
            pulls += [(f"{h:+d} deg sideways, wheel {w['id']} held, at the {lc8['held_wheel_n'] / 1000:g} kN limit", w["id"], math.radians(h),
                       lc8["held_wheel_n"] / rated) for h in five]
        for axle in ("front", "rear"):
            pair = tuple(w["id"] for w in self.ch.suspension if w["axle"] == axle)
            pulls += [(f"{h:+d} deg sideways, both {axle} wheels held, at the {lc8['held_axle_n'] / 1000:g} kN limit", pair, math.radians(h),
                       lc8["held_axle_n"] / rated) for h in five]
        return pulls

    @staticmethod
    def recovery_label(where: str, s: int, lab: str, v: int, sup: dict, mus: list, R: dict, shown: float | None, kn: float) -> str:
        """One LC8a case's label: the point, the pull, how far the trailer turned on a held wheel, the bounds of the tyres'
        grip it is read at, the pull at the ultimate (`shown`) and the share of it at which the trailer tips or slides."""
        out = (f"{where} {'kerb' if s < 0 else 'road'}-side point" if s else "the coupling") + f", {lab}, {v:+d} deg up, {sup['label']}"
        t = R["turn"]
        if t.get("turned"):
            out += f", turned to {t['taken']:+.1f} deg (through the hub {t['through']:+.1f})"
        if mus != [None]:
            out += f", mu {' or '.join(f'{m:g}' for m in mus)}"
        if shown is not None:
            out += f", {shown / 1000:.1f} kN"
        if R["scale"] < 1.0 - 1e-9:
            out += f", {'sliding' if R['limit'] == 'slides' else 'tipping'} at {R['scale'] * kn / 1000:.1f} kN"
        return out

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

    def _recovery_envelope(self, lc_id: str, label: str, info: dict, held, pull: dict | None = None):
        """LC8a's supports in each case (I2-94): the largest force on each arm's droop limit and airbag, the tyres off the
        ground, the pulls the trailer tips under before they reach their full size, and each held hinge's force. The counts
        and the tipping pulls are those with every wheel free, at the rated pull, or one held, at the held-wheel limit;
        `pull` gives the pull's direction, its size and whether both wheels of an axle are held, whose tipping pulls are
        kept apart (`axle_tipped`). A pull the trailer slides sideways under before it reaches its full size (`slid`, every
        wheel free, the tyres at their grip) is kept apart from one it tips under, and a held wheel's pulls that turn the
        trailer are counted with the largest turn and side force at each bound of the grip (`turns`, I2-124)."""
        e = self.lc8_arms.setdefault(lc_id, dict(cases=0, lifted=0, nose_off=0, tipped=[], axle_tipped=[], axle_cases=0, droop={}, bag={},
                                                 hinge={}, lift=dict(mm=0.0), nose=dict(up=0.0, down=0.0), slid=[], turns={}))
        off = info["off"]
        pull = pull or {}
        if pull.get("where"):
            key = f"{pull['where']}, {'axle held' if pull.get('axle') else ('wheel held' if held else 'every wheel free')}"
            e.setdefault("points", {})[key] = e.setdefault("points", {}).get(key, 0) + 1
        short = info["scale"] < 1.0 - 1e-9
        if held is not None and not pull.get("axle"):
            t = e["turns"].setdefault(f"{pull.get('mu')}", dict(cases=0, turned=0, deg=0.0, side_kn=0.0))
            t["cases"] += 1
            turn = info.get("turn", {})
            if turn.get("turned"):
                t["turned"] += 1
                deg = abs(turn["taken"] - turn["asked"])
                if deg > t["deg"]:
                    t.update(deg=deg, case=label)
            side = abs(info.get("grip", {}).get("side", 0.0)) / 1000
            if side > t["side_kn"]:
                t.update(side_kn=side, side_case=label)
        if pull.get("axle"):
            e["axle_cases"] += 1
            if short:
                e["axle_tipped"].append(dict(pull, case=label, scale=info["scale"], kn=info["scale"] * pull["kn"], limit=info.get("limit")))
        else:
            e["cases"] += 1
            e["nose"]["up"] = max(e["nose"]["up"], float(info["nose"][2]))
            e["nose"]["down"] = max(e["nose"]["down"], -float(info["nose"][2]))
            for k, mm in info["lift"].items():
                if k != "nose" and mm > e["lift"]["mm"]:
                    e["lift"] = dict(mm=mm, wheel=k, case=label)
            e["lifted"] += sum(1 for o in off if o != "nose")
            e["nose_off"] += "nose" in off
            if short:
                e["slid" if info.get("limit") == "slides" else "tipped"].append(dict(pull, case=label, scale=info["scale"],
                                                                                     kn=info["scale"] * pull.get("kn", 0.0)))
        for wid, a in info["arms"].items():
            if a["droop_n"] > e["droop"].get(wid, {}).get("n", 0.0):
                e["droop"][wid] = dict(n=a["droop_n"], case=label, airbag_n=a["airbag"], off=off)
            if a["airbag"] > e["bag"].get(wid, {}).get("n", -math.inf):
                e["bag"][wid] = dict(n=a["airbag"], case=label, off=off)
            if held is not None and (wid in held if isinstance(held, tuple) else held == wid):
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
            if el.sec.rigid or el.member in ("BODY", "BODY-MOUNT") or el.member.startswith(("PNL-", "XT-BAR-", "XT-PLATE-")):
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
        models = self.bar_models()
        sites: list[dict] = []
        hole_env: dict[str, dict] = {}
        self.panel_env: dict[str, dict] = {}
        self.gusset_env: dict[str, dict] = {}
        self.gusset_web_env: dict[str, dict] = {}

        def take(lc_id, res, label, extra=None, ultimate=False):
            self._hinge_envelope(lc_id, label, res, bar)          # the hinge bars' weld runs in every case (CHS-18, I2-121)
            self._seam_envelope(lc_id, label, res, bar)           # the twin hinge crossmembers' seams in every case (CHS-20)
            for mem, r in self.stresses(res, ultimate).items():
                e = env.setdefault(lc_id, {})
                if mem not in e or r["eq"] > e[mem]["eq"]:
                    e[mem] = dict(r, case=label, **(extra or {}))
            for sp in self.fm.panels_by_id().values():
                v, n = self.panel_shear(res, sp), self.panel_tie(res, sp)
                pe = self.panel_env.setdefault(lc_id, {})
                tie = max(n, pe.get(sp["id"], {}).get("tie_n", 0.0))
                if sp["id"] not in pe or v > pe[sp["id"]]["v_n"]:
                    pe[sp["id"]] = dict(v_n=v, case=label)
                pe[sp["id"]]["tie_n"] = tie
            for k, g in self.gusset_elements():
                web = self.gusset_web(res, k, g)
                we = self.gusset_web_env.setdefault(lc_id, dict(util=-1.0, welds_max=0.0))
                we["welds_max"] = max(we["welds_max"], web["welds"])
                if web["n1"] / web["cap"] > we["util"]:
                    we.update(web, util=web["n1"] / web["cap"], case=label, gusset=g["id"])
                w = self.gusset_weld_stress(res, k, g)
                ge = self.gusset_env.setdefault(lc_id, dict(mpa=-1.0))
                if w > ge["mpa"]:
                    ge.update(mpa=w, case=label, gusset=g["id"])
            he = hole_env.setdefault(lc_id, {})
            for k, h in enumerate(sites):
                if h.get("open") or h.get("placement_only"):
                    continue
                eq = self.hole_stress(res, h)["eq"]
                if k not in he or eq > he[k]["eq"]:
                    he[k] = dict(eq=eq, case=label)

        # every case on each of the frame's models (bar_models, I2-114): the hinge bars rigid, then elastic on free and on
        # stiff bushes, each reading the worst of them. The recovery's supports, the ball's load and the bare frame's twist
        # are the rigid model's: the supports and the ball are statically determined, and the body's share of the twist
        # (cad/body.py) is read on it
        lc1s: list[tuple[Any, dict, list]] = []
        defl: dict[str, dict] = {}
        twist: dict = {}
        balls: dict[str, dict] = {}
        lc6: dict[str, Any] = {}
        self.lc8_arms: dict[str, dict] = {}
        self.cheek_env: dict[str, dict] = {}
        self.run_env: dict[str, dict] = {}
        self.seam_env: dict[str, dict] = {}
        self.bar_env: dict[str, dict] = {}
        main_runs, main_cheeks = self.run_env, self.cheek_env
        self.lc8_mu = {mu: dict(runs={}, cheeks={}) for mu in (lcs["LC8a"]["reaction"].get("mu") or [None])}
        rcache: dict = {}                     # LC8a's reactions, the same on every frame model
        for bar, fm in models:
            self._use(fm)
            sites = self.hole_sites()
            first = fm is models[0][1]
            tag = "" if first else f", the hinge bars {bar}"
            lc1: dict[str, Any] = {}
            lc1s.append((fm, lc1, sites))
            for c, items, m0, k in cases:
                for lc_id in ("LC1", "LC2", "LC3", "LC4"):
                    for j, acc in enumerate(lcs[lc_id]["accel"]):
                        res, info = self.run_static(items, acc)
                        self.resid = max(self.resid, info["residual_n"])
                        take(lc_id, res, f"{c.id}" + (f" ({'+' if acc[1] > 0 else '-'}Y)" if acc[1] else "") + tag)
                        if lc_id == "LC1":
                            lc1[c.id + tag] = res
                            defl[c.id + tag] = self.deflections(res)
                            if first:
                                balls[c.id] = dict(ball_kg=info["ball"][2] / G, scale=k, model_kg=m0)
                lc = lcs["LC5a"]
                hub_y = ch.suspension[0]["contact"][1]
                for sgn in (1, -1):
                    res, info = self.run_static(items, lc["accel"][0], twist_n=sgn * lc["torque_nmm"] / (2 * abs(hub_y)))
                    self.resid = max(self.resid, info["residual_n"])
                    take("LC5a", res, f"{c.id} (diagonal {'A' if sgn > 0 else 'B'})" + tag)
                    t = self.twist(res)
                    if first and t > twist.get("deg", -1):
                        twist = dict(deg=t, case=f"{c.id} (diagonal {'A' if sgn > 0 else 'B'})")
                for side in (-1, 1):
                    for axle in ("front", "rear"):
                        res, info = self.run_static(items, lcs["LC8b"]["accel"][0], lifted=(side, axle))
                        self.resid = max(self.resid, info["residual_n"])
                        jack, wid = float(info["jack"][0][2]), info["jack"][1]
                        bag = float(info["arms"][wid]["airbag"])
                        label = f"{c.id}, {'kerb' if side < 0 else 'road'} side jacked under its {axle} arm{tag}"
                        take("LC8b", res, label, dict(pad_n=jack))
                        e8 = env["LC8b"].setdefault("_pad", dict(eq=0.0, pad_n=0.0, bag_n=0.0))
                        if jack > e8["pad_n"]:
                            e8.update(pad_n=jack, case=label, bag_at=bag)
                        if bag > e8["bag_n"]:
                            e8.update(bag_n=bag, bag_case=label, jack_at=jack)
            # LC5b at tare, unscaled
            tc1 = next(c for c in self.tr.cases if c.id == "TC1")
            lc = lcs["LC5b"]
            res, info = self.run_static(self.items(tc1), lc["accel"][0], steady_n=lc["steady_kg"] * G)
            self.resid = max(self.resid, info["residual_n"])
            take("LC5b", res, "TC1 tare, one steady wound to 875 kg" + tag)
            # LC6 at the coupling, LC6b at each chain lug, LC8a at each recovery point
            ball_p = (0.0, 0.0, V["coupling_z"])
            for F in lcs["LC6"]["forces_n"]:
                res = self.run_body(F, ball_p, [(self.fm.ball, 1.0)])
                lab = f"{_dir(F)} {max(abs(v) for v in F) / 1000:.1f} kN"
                take("LC6", res, lab + tag)
                if first:
                    lc6[lab] = res
            for s in (-1, 1):
                lug = (V["chain_lug_x"], s * (ch.db_y(V["chain_lug_x"]) + 30), V["db_z"] - 60)
                for F in lcs["LC6b"]["forces_n"]:
                    res = self.run_body(F, lug, [(self.fm.db_node(s, V["chain_lug_x"]), 1.0)])
                    take("LC6b", res, f"{'kerb' if s < 0 else 'road'}-side lug, {_dir(F)} {max(abs(v) for v in F) / 1000:.1f} kN" + tag)
            # LC8a at each recovery point, at the 58.9 kN pull (no yield) and at the 78.5 kN ultimate (no fracture, LC8u): the
            # members on their AS 4100 effective sections against fy, the holes on their net sections against 0.85 fu. A rear
            # tongue's pull acts at its shackle hole and enters the frame at the rear crossmember's end, where the tongue is
            # welded through the crossmember and along the rail's web (rear_recovery_point, I2-87). The coupling is a pull point
            # too, since most bogged trailers come out with the truck pulling there, along the rail axis within LC8a's 15
            # degrees up or down (`coupling`, the conductor's ruling of 27 Nov 2026). Each pull is read at each bound of the
            # tyres' grip (`reaction` `mu`, I2-124), the worse governing every check, CHS-14's and CHS-18's readings at each
            # bound kept apart beside them (lc8_mu). A pull whose reaction one already read on this model gives, as a held
            # wheel's pulls that turn the trailer as far as one another do, is counted again and not solved again
            lc8 = lcs["LC8a"]
            supports = self.recovery_supports(cases)
            points = [(where, s) for where in ("front", "rear") for s in (-1, 1)] + ([("coupling", 0)] if lc8.get("coupling") else [])
            mus = lc8["reaction"].get("mu") or [None]
            vd = lc8["vertical_deg"]
            for lc_id, Fr in (("LC8a", lc8["force_n"]), ("LC8u", lc8["ultimate_n"])):
                seen: dict = {}
                for where, s in points:
                    p, fr, sx = self.recovery_point(where, s)
                    for lab, held, hdg, k in self.recovery_pulls(lc8, s):
                        for v in (-vd, 0, vd):
                            F = k * Fr * np.array([sx * math.cos(hdg) * math.cos(math.radians(v)), math.sin(hdg) * math.cos(math.radians(v)),
                                                   math.sin(math.radians(v))])
                            for si, sup in enumerate(supports):
                                groups: dict = {}
                                for mu in mus:
                                    ck = (lc_id, where, s, lab, v, si, mu)
                                    if ck not in rcache:
                                        rcache[ck] = self.recovery_reactions(F, p, held, sup["base"], sup["nose"], mu)
                                    groups.setdefault((where, s, si, _reaction_key(rcache[ck])), []).append(mu)
                                for key, ms in groups.items():
                                    R = rcache[(lc_id, where, s, lab, v, si, ms[0])]
                                    label = self.recovery_label(where, s, lab, v, sup, ms, R, k * Fr if lc_id == "LC8u" else None, k * Fr) + tag
                                    got = seen.get(key)
                                    todo = [m for m in ms if got is None or m not in got["mus"]]
                                    if todo:
                                        res, info = self.run_recovery(F, p, fr, held, sup, R=R)
                                        for j, mu in enumerate(todo):
                                            self.run_env, self.cheek_env = self.lc8_mu[mu]["runs"], self.lc8_mu[mu]["cheeks"]
                                            if j == 0 and got is None:
                                                take(lc_id, res, label, ultimate=lc_id == "LC8u")
                                            else:
                                                self._hinge_envelope(lc_id, label, res, bar)
                                            self._cheek_envelope(lc_id, label, res)
                                        self.run_env, self.cheek_env = main_runs, main_cheeks
                                        got = seen.setdefault(key, dict(info=info, mus=set()))
                                        got["mus"].update(todo)
                                    if first:
                                        for mu in ms:
                                            Rm = rcache[(lc_id, where, s, lab, v, si, mu)]
                                            info = dict(got["info"], turn=Rm["turn"], grip=Rm["grip"], limit=Rm["limit"], scale=Rm["scale"])
                                            self._recovery_envelope(lc_id, label, info, held, dict(
                                                where=where, side=s, h=round(math.degrees(hdg), 1), v=v, kn=k * Fr / 1000, axle=isinstance(held, tuple),
                                                weight=sup["label"].split(",")[0], coupled=bool(sup["nose"].get("holds_down")), mu=mu))
        # each bound of the tyres' grip read apart, and the worse of them in the envelopes CHS-14 and CHS-18 read
        for d in self.lc8_mu.values():
            for name, env_ in (("runs", self.run_env), ("cheeks", self.cheek_env)):
                for lc_id, e in d[name].items():
                    for part, r in e.items():
                        cur = env_.setdefault(lc_id, {}).get(part)
                        if cur is None or r["mpa"] > cur["mpa"]:
                            env_[lc_id][part] = dict(r)

        self._use(models[0][1])
        out = dict(envelope={}, governing={}, deflections={}, twist=twist, balls=balls, residual_n=self.resid,
                   frame=dict(nodes=len(self.f.nodes), elements=sum(1 for e in self.f.elements if not e.sec.rigid),
                              rigid_links=sum(1 for e in self.f.elements if e.sec.rigid)),
                   bars={bar: dict(nodes=len(fm.f.nodes), elements=sum(1 for e in fm.f.elements if not e.sec.rigid),
                                   rigid_links=sum(1 for e in fm.f.elements if e.sec.rigid)) for bar, fm in models})
        for lc_id, e in env.items():
            fac = lcs[lc_id]["factor"] if lc_id in lcs else 1
            rows = {m: dict(r, util=r["eq"] / (fy_of.get(m, self.fy_of_part(m)) / fac), fy=fy_of.get(m, self.fy_of_part(m)))
                    for m, r in e.items() if not m.startswith("_")}
            out["envelope"][lc_id] = rows
            g = max(rows.items(), key=lambda kv: kv[1]["util"])
            out["governing"][lc_id] = dict(member=g[0], **g[1], limit=g[1]["fy"] / fac, factor=fac)
        out["pad_n"] = env["LC8b"]["_pad"]
        out["deflections"] = self._worst_deflections(defl)
        out["fatigue"] = self._worse(lambda lc1, sites: self.fatigue(lc1), lc1s, "range_mpa")
        out["holes"] = self._worse(lambda lc1, sites: self.holes(hole_env, lc1, sites), lc1s, "peak_mpa")
        from .chassis_dip import check as galvanising_check
        out["galvanising"] = galvanising_check(ch)
        out["local"] = self.local_checks(out["pad_n"])
        out["local"].update(self.panel_checks(), hinge_cheeks=self.cheek_check(), arm_limits=self.arm_limits(),
                            hinge_runs=self.hinge_runs(), hinge_bar=self.hinge_bar_report(), hinge_seams=self.seam_welds())
        out["local"]["hinge_gussets"] = self.gusset_welds()
        out["recovery"] = self.recovery_summary()
        out["tipping"] = self.tipping_pulls(self.recovery_supports(cases))
        out["fixings"] = self.fixings()
        out["cross_checks"] = self.cross_checks(out, lc6)
        out["lc1_ball"] = balls
        out["hinge_joints"] = self.hinge_joints(out)
        return out

    def _worse(self, read, models: list[tuple[Any, dict, list]], key: str) -> list[dict]:
        """Rows read on each frame model from its own LC1 results and hole sites (read(lc1, sites)), the rows in the same
        order on each, and each row the worse of them by `key` (I2-114). The first model is the one in use after."""
        best: list[dict] = []
        for fm, lc1, sites in models:
            self._use(fm)
            rows = read(lc1, sites)
            best = rows if not best else [r if r.get(key, 0.0) > b.get(key, 0.0) + 1e-9 else b for b, r in zip(best, rows)]
        self._use(models[0][0])
        return best

    def hinge_joints(self, out: dict) -> dict:
        """CHS-12 (I2-88): the XT hinge joints as built, each pivot tied to its crossmember at the hinge bar's weld runs and
        to the rail through the hinge's two cheeks, with the gussets behind it: the hinge crossmembers, the gussets, the
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
        """The racking shear a shear panel carries across its bay, from its two diagonals' axial forces:
        V = (N1 - N2) dy / L, in N."""
        n1, n2 = (float(res.forces[e][6]) for e in sp["elements"])
        return abs(n1 - n2) * sp["dy"] / sp["L"]

    def panel_tie(self, res, sp: dict) -> float:
        """The larger of a shear panel's two diagonals' axial forces, in N: what each rail's angle passes to the sheet."""
        return max(abs(float(res.forces[e][6])) for e in sp["elements"])

    def panel_bolts(self, sp: dict) -> list[dict]:
        """Each group of the shear panel's bolts (Chassis.shear_panels): its bolts, how many stand on one side, and for
        its worst bolt AS/NZS 4600 5.3.2's e and AS 4100 9.3.2.4's a_e along its angle, either way, and the least distance
        from any bolt's centre to the sheet's edges and cuts in any direction."""
        fix = sp["fixing"]
        dh, df = fix["hole"], fix["d"]
        rects = sp["sheet"]["parts"] + sp["sheet"]["tongues"]

        def reach(c: float, other: float, axis: int, sign: int) -> float:
            """How far the sheet runs from c along `axis` (0 is X, 1 is Y) one way, at `other` across it."""
            spans = []
            for a, b in sorted((r[axis], r[axis + 2]) for r in rects if r[1 - axis] - 1e-6 <= other <= r[3 - axis] + 1e-6):
                if spans and a <= spans[-1][1] + 1e-6:
                    spans[-1][1] = max(spans[-1][1], b)
                else:
                    spans.append([a, b])
            a, b = next(s for s in spans if s[0] - 1e-6 <= c <= s[1] + 1e-6)
            return (b - c) if sign > 0 else (c - a)

        out = []
        for group in ("rail", "rear"):
            bolts = [b for b in sp["bolts"] if b["group"] == group]
            if not bolts:
                continue
            axis = 0 if bolts[0]["along"] == "x" else 1
            e_min = ae_min = edge = math.inf
            for b in bolts:
                at = (b["x"], b["y"])
                c, other = at[axis], at[1 - axis]
                line = [(q["x"], q["y"])[axis] for q in bolts if abs((q["x"], q["y"])[1 - axis] - other) < 1.0]
                for sign in (1, -1):
                    to_edge = reach(c, other, axis, sign)
                    ahead = [sign * (q - c) for q in line if sign * (q - c) > 0]
                    to_hole = min(ahead) if ahead else math.inf
                    e_min = min(e_min, to_edge, to_hole - dh / 2)
                    ae_min = min(ae_min, to_edge - dh / 2 + df / 2, to_hole - dh + df / 2)
                edge = min(edge, *(reach(at[ax], at[1 - ax], ax, sg) for ax in (0, 1) for sg in (1, -1)))
            out.append(dict(group=group, n=len(bolts), n_side=sum(1 for b in bolts if b["y"] > 0) if group == "rail" else len(bolts),
                            e=e_min, a_e=ae_min, edge=edge, e_any=min(e_min, edge), a_e_any=min(ae_min, edge - dh / 2 + df / 2)))
        return out

    def panel_holds(self, sp: dict) -> list[tuple[float, float]]:
        """The points that hold shear panel sp's sheet out of its plane (I2-98): every bolt along the rails' angles, and each
        tongue's root over its straight width every 10 mm, where the tongue joins the sheet's edge. Nothing holds the edges
        between them, since the rear tank sits on the sheet."""
        pts = [(b["x"], b["y"]) for b in sp["bolts"] if b["group"] == "rail"]
        for r in sp["sheet"]["roots"]:
            n = max(1, int(round((r["y1"] - r["y0"]) / 10.0)))
            pts += [(r["x"], r["y0"] + (r["y1"] - r["y0"]) * j / n) for j in range(n + 1)]
        return pts

    def panel_rear_bolts(self, sp: dict, V: float, N: float) -> tuple[float, float]:
        """The rear group's bolts under the next crossmember (fx22-rear): the racking shear V along the crossmember shared
        equally, and the couple of the two diagonals' forces along the trailer, N dx / L at each diagonal's end, shared
        over the group in proportion to each bolt's Y, an elastic bolt group. The force on the outermost bolt along the
        crossmember and along the trailer, in N."""
        rear = [b for b in sp["bolts"] if b["group"] == "rear"]
        dx = math.sqrt(max(0.0, sp["L"] ** 2 - sp["dy"] ** 2))
        M = 2 * N * dx / sp["L"] * abs(sp["ties"][0]["cm_y"])
        y_max, sy2 = max(abs(b["y"]) for b in rear), sum(b["y"] ** 2 for b in rear)
        return V / len(rear), M * y_max / sy2

    def tongue_roots(self, sp: dict) -> list[dict]:
        """Each tongue of shear panel sp's sheet as a free body (I2-98): its bolts' share of the panel's racking shear V,
        each bolt of its crossmember's group an equal share, acts along the crossmember at its bolt line and reaches the
        sheet through the tongue's root in shear and in-plane bending, with the couple's force along the trailer on its
        bolts (panel_rear_bolts) along the tongue. The root's corners are radiused `root_r`, so each section from the start
        of the radius to the sheet's edge is read, its width growing from the tongue's own to that plus twice the radius as
        its lever to the bolt line grows. `axial` is the couple's force on the tongue per unit of that on its outermost bolt."""
        sh, out = sp["sheet"], []
        R = sh["root_r"]
        rear = [b for b in sp["bolts"] if b["group"] == "rear"]
        y_max = max(abs(b["y"]) for b in rear)
        for r in sh["roots"]:
            bolts = [b for b in sp["bolts"] if b["group"] == "rear" and r["y0"] - 1e-6 <= b["y"] <= r["y1"] + 1e-6
                     and r["way"] * (b["x"] - r["x"]) > 0]
            lever = abs(sum(b["x"] for b in bolts) / len(bolts) - r["x"])
            w0 = r["y1"] - r["y0"]
            sections = []
            for j in range(21):
                e = min(R, lever) * j / 20                   # back from the sheet's edge toward the bolts
                w = w0 + 2 * (R - math.sqrt(max(0.0, R ** 2 - (R - e) ** 2))) if R else w0
                sections.append((w, lever - e))
            out.append(dict(piece=r["piece"], group="rear", share=len(bolts) / len(rear), lever=lever, w=w0, sections=sections,
                            axial=abs(sum(b["y"] for b in bolts)) / y_max))
        return out

    @staticmethod
    def tongue_root_reading(F: float, t: float, fy: float, sections, P: float = 0.0) -> tuple[float, float]:
        """A tongue's or a wing's root under its share F (N) across it and P along it: the largest von Mises stress over
        its sections and their fibres, the bending stress M y / I and P / (w t) with the shear 1.5 F / (w t) (1 - (2 y / w)
        squared) by beam theory (est., the part is short), and the largest plastic interaction
        M / Mp + P / Pp + (V / Vp) squared, Mp = fy t w squared / 4, Pp = fy t w and Vp = fy t w / sqrt 3."""
        eta = np.linspace(0.0, 1.0, 41)
        vm = pl = 0.0
        for w, arm in sections:
            M = F * max(0.0, arm)
            sb, sa, tp = 6 * M / (t * w ** 2), P / (t * w), 1.5 * F / (t * w)
            vm = max(vm, float(np.max(np.sqrt((sb * eta + sa) ** 2 + 3 * (tp * (1 - eta ** 2)) ** 2))))
            pl = max(pl, M / (fy * t * w ** 2 / 4) + P / (fy * t * w) + (F / (fy * t * w / math.sqrt(3))) ** 2)
        return vm, pl

    def wing_roots(self, sp: dict) -> list[dict]:
        """Each wing of shear panel sp's sheet, the part outboard of the cut ahead of it, as a free body (fx22-rear): its
        rail's diagonal's force N reaches the sheet at its bolts' middle and passes into the main part through the wing's
        root, the line where it meets the main part's side, the force's component along the root in shear, its component
        across it in tension or compression, and both their moments about the root's middle in in-plane bending (est.,
        each moment taken the worst way). `ux` and `uy` are the diagonal's direction along and across the trailer."""
        out = []
        dx = math.sqrt(max(0.0, sp["L"] ** 2 - sp["dy"] ** 2))
        ux, uy = dx / sp["L"], sp["dy"] / sp["L"]
        for wg in sp["sheet"]["wings"]:
            x0, x1, yr = wg["root"]
            near = [b for b in sp["bolts"] if b["group"] == "rail" and b["y"] * wg["side"] > 0]
            bx, by = sum(b["x"] for b in near) / len(near), sum(b["y"] for b in near) / len(near)
            out.append(dict(side=wg["side"], l=x1 - x0, ux=ux, uy=uy, arm_x=abs(bx - (x0 + x1) / 2), arm_y=abs(by - yr)))
        return out

    def wing_reading(self, wg: dict, N: float, t: float, fy: float) -> tuple[float, float]:
        """A wing's root (wing_roots) under its diagonal's force N (N): its von Mises stress and its plastic interaction, as
        tongue_root_reading reads a root of the wing's length with the force across it and along it and their moments."""
        across, along = N * wg["uy"], N * wg["ux"]
        M = across * wg["arm_x"] + along * wg["arm_y"]
        w = wg["l"]
        sb, sa, tp = 6 * M / (t * w ** 2), across / (t * w), 1.5 * along / (t * w)
        vm = max(abs(sb + sa), math.sqrt(sa ** 2 + 3 * tp ** 2))      # at the root's outer fibre, and at its middle
        pl = M / (fy * t * w ** 2 / 4) + across / (fy * t * w) + (along / (fy * t * w / math.sqrt(3))) ** 2
        return vm, pl

    def panel_checks(self) -> dict:
        """Each shear panel (shear_panels) in its worst case of every load case (fx22-rear): the racking shear V over the
        sheet's net width between its cuts, V / (b_n t), against its shear yield over the case's factor and its elastic
        shear buckling stress on the points that hold it over the sheet as cut (panel_holds, plate_shear_buckling), each
        tongue's root (tongue_roots) and each wing's root (wing_roots) by its von Mises stress against fy over the case's
        factor and at the ultimate by its plastic interaction against 1, the M10 bolts in each group against AS 4100
        9.3.2's 0.8 x 0.62 fuf on their minor diameter area, each rail's two taking its diagonal's force and the rear
        group V and the diagonals' couple (panel_rear_bolts), the rails' angles' welds under the diagonal's force, and the
        sheet at the most loaded bolt in bearing, by AS 4100 9.3.2.4 (0.9 x 3.2 fu on d t) and AS/NZS 4600 5.3.4.2
        (0.6 x alpha C fu, C 3.0 for d / t under 10, alpha 1.0 in single shear with a washer under the head and the nut),
        and in tear-out to its nearest edge in any direction, by AS 4100 9.3.2.4 (0.9 fu on a_e t) and AS/NZS 4600 5.3.2
        (0.7 fu on e t, fu / fy over 1.08)."""
        ch = self.ch
        lcs = {lc["id"]: lc for lc in ch.data["load_cases"]}
        mat = ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        spec = next(f for f in ch.data["fittings"] if f["id"] == "CH-P17")
        out = {}
        for sp in self.fm.panels_by_id().values():
            d = next(x for x in ch.data["shear_panels"] if x["id"] == sp["id"])
            t, sh, b_n = sp["t"], sp["sheet"], sp["b_n"]
            rect = sh["rect"]
            tau_cr = plate_shear_buckling(rect[0], rect[2], rect[1], rect[3], t, self.panel_holds(sp), holes=sh["holes"])
            bolt = d["fixing"]
            cap = 0.8 * 0.62 * bolt["fuf"]                     # MPa on the bolt's minor diameter area
            size = bolt["bolt"].split()[0]
            fu = d["fu"]
            c_4600 = 3.0 if bolt["d"] / t < 10 else max(1.8, 4.0 - 0.1 * bolt["d"] / t)
            phi_f = 0.70 if fu / d["fy"] >= 1.08 else 0.60
            groups = {g["group"]: g for g in self.panel_bolts(sp)}
            e, a_e = min(g["e_any"] for g in groups.values()), min(g["a_e_any"] for g in groups.values())
            roots, wings = self.tongue_roots(sp), self.wing_roots(sp)
            rail = next(p for p in ch.panel_pieces() if p["use"] == "rail")
            weld = rail["length"] * (0.7 * spec["weld"]["leg"] + spec["weld"]["corner_throat"])
            rows = []
            for lc_id, env in self.panel_env.items():
                r = env[sp["id"]]
                fac = lcs[lc_id]["factor"] if lc_id in lcs else 1
                V, N = r["v_n"], r["tie_n"]
                f_rail = N / groups["rail"]["n_side"]
                fy_rear, fx_rear = self.panel_rear_bolts(sp, V, N)
                fb = max(f_rail, math.hypot(fy_rear, fx_rear))
                read = [self.tongue_root_reading(V * q["share"], t, d["fy"], q["sections"], P=fx_rear * q["axial"]) for q in roots]
                read += [self.wing_reading(wg, N, t, d["fy"]) for wg in wings]
                rows.append((f"plate shear on its net width, {lc_id}", V / (b_n * t), min(0.6 * d["fy"], tau_cr) / fac))
                if lc_id == "LC8u":                            # no fracture at the ultimate: the roots' plastic interaction
                    rows.append((f"tongue's and wing's roots, plastic interaction times fy, {lc_id}", max(x[1] for x in read) * d["fy"], d["fy"]))
                else:                                          # no yield at the working loads: their von Mises stress
                    rows.append((f"tongue's and wing's roots, von Mises, {lc_id}", max(x[0] for x in read), d["fy"] / fac))
                rows += [(f"{size} bolt on a rail's angle, {lc_id}", f_rail / bolt["a_c"], cap / fac),
                         (f"{size} bolt under the {sp['ties'][0]['cm']} crossmember, {lc_id}", math.hypot(fy_rear, fx_rear) / bolt["a_c"], cap / fac),
                         (f"rail's angle's welds to the rail, {lc_id}", N / weld, (wcap if lc_id != "LC8u" else 0.6 * mat["weld_fuw"]) / fac),
                         (f"sheet in bearing at a bolt, AS 4100, {lc_id}", fb / (bolt["d"] * t), 0.9 * 3.2 * fu / fac),
                         (f"sheet in bearing at a bolt, AS/NZS 4600, {lc_id}", fb / (bolt["d"] * t), 0.6 * c_4600 * fu / fac),
                         (f"sheet's tear-out at a bolt, AS 4100, {lc_id}", fb / (a_e * t), 0.9 * fu / fac),
                         (f"sheet's tear-out at a bolt, AS/NZS 4600, {lc_id}", fb / (e * t), phi_f * fu / fac)]
            w = max(self.panel_env.items(), key=lambda kv: kv[1][sp["id"]]["v_n"])
            edge = min(g["edge"] for g in groups.values())
            n_tie = max(env[sp["id"]]["tie_n"] for env in self.panel_env.values())
            res = _local(f"Shear panel {sp['id']}, {t:g} mm steel, {sp['x1'] - sp['x0']:,.0f} x {sp['b']:,.0f} mm, cut to {b_n:,.0f} mm wide at the rear airbags", rows,
                         f"its worst racking shear, {w[1][sp['id']]['v_n'] / 1000:.1f} kN in {w[0]}, {w[1][sp['id']]['case']}, and up to "
                         f"{n_tie / 1000:.1f} kN on each rail's {groups['rail']['n_side']} bolts, the sheet {b_n:,.0f} mm wide between its cuts, "
                         f"e {e:.1f} mm, the least bolt edge distance {edge:.1f} mm, the sheet buckling at {tau_cr:.1f} MPa on the points that hold it")
            res.update(tau_cr=tau_cr, v_n=w[1][sp["id"]]["v_n"], tie_n=n_tie, lc=w[0], bolt_groups=list(groups.values()), tongues=roots,
                       wings=wings, b_n=b_n, weld_mm2=weld)
            out["shear_panel"] = res
        return out

    def cheek_lines(self, c: dict) -> tuple[dict, np.ndarray]:
        """Hinge cheek c's welds to the rail (CH-P16, xt_hinges `cheek`, I2-92, I2-118) as one weld group (weld_group), in
        the cheek's own axes: u along the rail from its joint to the hinge bar or its filler, away from it, v inboard from
        the rail's inner face and z up from the rail's underside. On the rail's inner web the `leg` fillet along its top
        edge and the flare-bevel weld along the rail's bottom corner, its throat the `corner` share of the rail's outside
        radius (AISC 360 Table J2.2's 5/8 R for GMAW to a procedure proven by a macro section, `corner_rule`), from the cope at its crossmember's face to its far
        end, each line on its throat, a cheek's `tail` under its crossmember, if it has one, standing between its joint and
        the cope. Returns the group and the pin's place, at the middle of the cheek's joint over the bar's top `bar_d` under
        the rail (est.), at the plate's mid-thickness."""
        ck = self.ch.data["xt_hinges"]["cheek"]
        ro = self.ch.role_sec["rail"].ro
        tail, z1 = c.get("tail", 0.0), ck["h"] - ck["below"]
        u0, u1 = tail + ck.get("cope", 0.0), tail + ck["l"]     # the web's welds start at the cope (I2-100)
        lines = [("top edge's fillet on the rail's web", (u0, 0.0, z1), (u1, 0.0, z1), 0.7 * ck["leg"]),
                 ("flare-bevel weld at the rail's bottom corner", (u0, 0.0, 0.0), (u1, 0.0, 0.0), ck["corner"] * ro)]
        return weld_group(lines), np.array([0.0, ck["t"] / 2, -ck["bar_d"] / 2])

    def filler_of(self, c: dict) -> dict | None:
        """The filler CH-P18 a front cheek c meets (Chassis.hinge_fillers), or None."""
        if c["way"] > 0:
            return None
        return next((fl for fl in self.ch.hinge_fillers() if fl["wheel"] == c["wheel"]), None)

    def cheek_welds(self, F, c: dict) -> dict:
        """The stresses in hinge cheek c's welds (CH-P16, xt_hinges `cheek`, I2-92, I2-118) under the force F (N, along,
        across and up) that its pin passes from the hinge bar at the cheek's joint to it: a rear cheek's two `bar_leg` fillets
        down the bar's rear face over the cheek's `bar_d` under the rail, or a front cheek's two down its filler's front face
        over the filler's depth (filler_of), on their throats, each passing a force but no moment, and the cheek's welds to the
        rail's web as one weld group (cheek_lines), read by the elastic vector method with the force's moments about the
        group's centroid, the components added at the worst corner whatever their signs. A filler's own welds and section
        follow (filler_welds)."""
        ck = self.ch.data["xt_hinges"]["cheek"]
        Fa = np.abs(np.asarray(F, float))
        fl = self.filler_of(c)
        depth = min(ck["bar_d"], fl["z1"] - fl["z0"]) if fl else ck["bar_d"]   # the fillets run down the filler's face
        out = {f"fillets to the {'filler' if fl else 'hinge bar'}": float(np.linalg.norm(Fa)) / (2 * depth * 0.7 * ck["bar_leg"])}
        g, pin = self.cheek_lines(c)
        out.update(group_stress(g, Fa, pin))
        if fl:
            out.update(self.filler_welds(Fa, fl, depth))
        return out

    def filler_lines(self, fl: dict) -> dict:
        """Filler fl's welds (CH-P18, xt_hinges `filler`, I2-118) as one weld group in the trailer's axes, each on its
        throat: a `leg` fillet along its bottom rear edge to the hinge bar's front face, the bar standing deeper than it,
        and one along its inboard top edge to the crossmember's underside, on 0.7 leg, and the flare-bevel welds along the
        crossmember's rounded bottom front corner, inboard of the front cheek's fillets, and along the rail's rounded outer
        bottom corner, each on the cheek's `corner` share of its corner's outside radius (AISC 360 Table J2.2)."""
        ch = self.ch
        fd, ck = ch.data["xt_hinges"]["filler"], ch.data["xt_hinges"]["cheek"]
        a = 0.7 * fd["leg"]
        cm = next(m for m in ch.members if m.id == fl["cm"])
        xf, xb, yi, yo, z0, z1 = fl["front"], fl["bar_front"], fl["inner_y"], fl["outer_y"], fl["z0"], fl["z1"]
        return weld_group([("filler's fillet along its bottom edge to the hinge bar", (xb, yi, z0), (xb, yo, z0), a),
                           ("filler's fillet along its inboard top edge to the crossmember", (xf, yi, z1), (xb, yi, z1), a),
                           ("filler's flare-bevel weld in the crossmember's front corner", (xf, yi, z1), (xf, fl["flare_y"], z1),
                            ck["corner"] * cm.sec.ro),
                           ("filler's flare-bevel weld at the rail's outer bottom corner", (xf, yo, z1), (xb, yo, z1),
                            ck["corner"] * ch.role_sec["rail"].ro)])

    def filler_welds(self, Fa, fl: dict, depth: float) -> dict:
        """Filler fl (I2-118) under its front cheek's share Fa at the middle of the cheek's fillets on its front face,
        `depth` down it: its welds by the elastic vector method at their worst whatever the signs (filler_lines), and its
        section at the hinge bar's face under what its fillet on the bar carries (group_share), N / A and M / Z about each
        axis, the torque by rect_torsion and 1.5 V / A, combined as sqrt(sigma^2 + 3 tau^2), at each sign of the share's
        components."""
        ck = self.ch.data["xt_hinges"]["cheek"]
        g = self.filler_lines(fl)
        y_cheek = fl["side"] * (self.ch.V["rail_c"] - self.ch.role_sec["rail"].b / 2 - ck["t"] / 2)
        at = np.array([fl["front"], y_cheek, fl["z1"] - depth / 2])
        out = group_stress(g, Fa, at)
        b, d = abs(fl["outer_y"] - fl["inner_y"]), fl["z1"] - fl["z0"]
        q = np.array([fl["bar_front"], (fl["inner_y"] + fl["outer_y"]) / 2, (fl["z0"] + fl["z1"]) / 2])
        A, Zy, Zz = b * d, b * d ** 2 / 6, d * b ** 2 / 6
        best = 0.0
        for sx in (1, -1):
            for sy in (1, -1):
                for sz in (1, -1):
                    Fs, Ms = group_share(g, np.asarray(Fa, float) * np.array([sx, sy, sz]), at, [0], q)
                    sig = abs(Fs[0]) / A + abs(Ms[1]) / Zy + abs(Ms[2]) / Zz
                    tau = rect_torsion(Ms[0], b, d) + 1.5 * max(abs(Fs[1]), abs(Fs[2])) / A
                    best = max(best, math.sqrt(sig ** 2 + 3 * tau ** 2))
        out["filler's section at the hinge bar's face"] = best
        return out

    @staticmethod
    def cheek_share(c: dict, mine: list[dict], px: float) -> np.ndarray:
        """The share of its hinge's pin force cheek c takes along, across and up (CHS-14, I2-118). The two cheeks meet the
        bar in line, so each takes half along the rail. Across and up each takes the worse of half, as they share it if the
        bar cannot turn between them, and the lever rule's share from the pivot at X px to the other cheek's joint, as they
        share it if the bar turns freely. A hinge with one cheek gives it the whole force."""
        if len(mine) < 2:
            return np.ones(3)
        o = next(x for x in mine if x is not c)
        s = max(0.5, abs(px - o["joint_x"]) / abs(c["joint_x"] - o["joint_x"]))
        return np.array([0.5, s, s])

    def _cheek_envelope(self, lc_id: str, label: str, res):
        """Each hinge's pin force in one LC8a case, the force each of its cheeks takes from the hinge bar (cheek_share),
        and the largest stress in each of their welds over the case's hinges (cheek_welds, CHS-14)."""
        xyz = np.asarray(self.f.nodes)
        e = self.cheek_env.setdefault(lc_id, {})
        cheeks = self.ch.hinge_cheeks()
        for wid, k in self.fm.cheek_pins.items():
            el = self.f.elements[k]
            R, _ = el.axes(xyz)
            F = -R.T @ np.asarray(res.forces[k][6:9])
            mine = [c for c in cheeks if c["wheel"] == wid]
            px = next(w["pivot"][0] for w in self.ch.suspension if w["id"] == wid)
            for c in mine:
                f = F * self.cheek_share(c, mine, px)
                for part, mpa in self.cheek_welds(f, c).items():
                    key = f"the {'front' if c['way'] < 0 else 'rear'} cheek's {part}"
                    if mpa > e.get(key, {}).get("mpa", 0.0):
                        e[key] = dict(mpa=mpa, case=label, wheel=wid, cheek=c["id"], f=[float(v) for v in f])

    def hinge_run_group(self, w: dict) -> dict:
        """Wheel w's hinge bar's weld runs to its crossmember (xt_hinges `bar`, CHS-18, I2-119) as one weld group in the
        trailer's axes: each of the three `run` mm runs on its side a `leg` fillet along both of the bar's top edges, its
        faces `w` apart (xt_arms parts `bar`), on the crossmember's underside, each on its 0.7 leg throat."""
        ch = self.ch
        cm = next(m for m in ch.members if m.station == w["station"] and m.role == "cm_xt")
        b = ch.data["xt_hinges"]["bar"]
        bw = ch.data["xt_arms"]["parts"]["bar"].get("w", cm.sec.b)
        x, z = ch.hinge_bar_x(cm), cm.box()[2]
        y_in = ch.V["rail_c"] - ch.role_sec["rail"].b / 2
        lines = []
        for y in sorted((y for y in ch.hinge_weld_ys(cm) if y * w["side"] > 0), key=abs):
            for e, edge in ((-1, "front"), (1, "rear")):
                lines.append((f"the run {y_in - abs(y):.0f} mm inboard, its {edge} fillet", (x + e * bw / 2, y - b["run"] / 2, z),
                              (x + e * bw / 2, y + b["run"] / 2, z), 0.7 * b["leg"]))
        return weld_group(lines)

    def _links(self, name: str) -> list[int]:
        """The frame model's elements named `name`, cached on the model in use."""
        cache = self.fm.__dict__.setdefault("_named", {})
        if name not in cache:
            cache[name] = [k for k, el in enumerate(self.f.elements) if el.member == name]
        return cache[name]

    def hinge_runs_alone(self, w: dict) -> list[dict]:
        """Wheel w's hinge bar's weld runs one by one (CHS-18, I2-121): each run's two fillets as its own weld group, the
        lines of hinge_run_group, with the Y of the run's centre."""
        g = self.hinge_run_group(w)
        by_y: dict[float, list[int]] = {}
        for k in range(len(g["names"])):
            by_y.setdefault(round(float(g["m"][k][1]), 1), []).append(k)
        return [dict(y=y, g=weld_group([(g["names"][k], tuple(g["P0"][k]), tuple(g["P1"][k]), float(g["a"][k] / g["L"][k])) for k in ks]))
                for y, ks in sorted(by_y.items())]

    def _run_actions(self, res, wid: str, groups: list[dict]) -> list[tuple[np.ndarray, np.ndarray]]:
        """The force and moment each group in `groups` takes from wheel wid's links to its crossmember (the frame model's
        elements `hinge <wid>`), each link's force and moment at its crossmember's end summed about the group's centroid,
        each link given to the group whose centre is nearest it along Y."""
        xyz = np.asarray(self.f.nodes, float)
        acts = [(np.zeros(3), np.zeros(3)) for _ in groups]
        for k in self._links(f"hinge {wid}"):
            el = self.f.elements[k]
            R, _ = el.axes(xyz)
            fl = np.asarray(res.forces[k], float)
            Fj, Mj = -R.T @ fl[6:9], -R.T @ fl[9:12]
            n = min(range(len(groups)), key=lambda i: abs(groups[i]["g"]["c"][1] - xyz[el.j][1]))
            F, M = acts[n]
            F += Fj
            M += Mj + np.cross(xyz[el.j] - groups[n]["g"]["c"], Fj)
        return acts

    def _hinge_envelope(self, lc_id: str, label: str, res, bar: str):
        """In one case on frame model `bar`: each hinge bar's weld runs read by the elastic vector method (CHS-18). On the
        rigid bars the three runs a side act as one group (hinge_run_group), the actions of the bar's links to the
        crossmember summed about the six lines' centroid, since a rigid bar shares its load among them as the method
        takes it. On the elastic bars each run is read on its own (hinge_runs_alone) under the forces its own welds pass,
        the frame model holding each run at the welds' own stiffness along it (FrameModel._weld_runs, I2-121). In LC8a
        and LC8u on the elastic bars, the bar's largest stress on its estimated section and the force each pair of hinge
        plates takes from its bush follow (CHS-19, I2-119), and in VSB1's rig cases too, for CHS-19 to give beside."""
        xyz = np.asarray(self.f.nodes, float)
        cache = self.__dict__.setdefault("_run_groups", {})
        roots = self.ch.data["xt_arms"]["parts"]["arm"]["roots"]
        y_in = self.ch.V["rail_c"] - self.ch.role_sec["rail"].b / 2
        for w in self.ch.suspension:
            wid = w["id"]
            key = (wid, bar == "rigid")
            if key not in cache:
                cache[key] = [dict(y=None, g=self.hinge_run_group(w))] if bar == "rigid" else self.hinge_runs_alone(w)
            groups = cache[key]
            for grp, (F, M) in zip(groups, self._run_actions(res, wid, groups)):
                line, mpa = max(group_stress(grp["g"], F, grp["g"]["c"], M, worst=False).items(), key=lambda kv: kv[1])
                e = self.run_env.setdefault(lc_id, {}).setdefault(bar, dict(mpa=-1.0))
                if mpa > e["mpa"]:
                    e.update(mpa=mpa, line=line, case=label, wheel=wid, f=[float(v) for v in F], m=[float(v) for v in M],
                             run=grp["y"])
            if bar == "rigid" or lc_id not in ("LC8a", "LC8u") + RIG_CASES:
                continue
            be = self.bar_env.setdefault(lc_id, {}).setdefault(bar, dict(mpa=-1.0, plates={}))
            s = self.bar_stress(res, w)
            if s["eq"] > be["mpa"]:
                be.update(mpa=s["eq"], case=label, wheel=wid, **{k: v for k, v in s.items() if k != "eq"})
            ys = [w["side"] * (y_in - u) for u in roots]
            for k in self._links(f"bush {wid}"):
                el = self.f.elements[k]
                R, _ = el.axes(xyz)
                Fb = -R.T @ np.asarray(res.forces[k][6:9], float)
                pair = "outer" if abs(xyz[el.j][1] - ys[0]) < abs(xyz[el.j][1] - ys[1]) else "inner"
                pe = be["plates"].setdefault(pair, dict(along=0.0, total=0.0))
                if abs(Fb[0]) > pe["along"]:
                    pe.update(along=abs(float(Fb[0])), case=label, wheel=wid)
                pe["total"] = max(pe["total"], float(np.linalg.norm(Fb)))

    def bar_stress(self, res, w: dict) -> dict:
        """Wheel w's elastic hinge bar (XT-BAR, I2-119) on its estimated section (Chassis.hinge_bar_section), its largest
        stress over its elements' ends: N / A and the bending about each axis on the solid rectangle's elastic moduli, the
        torque by rect_torsion and the shear 1.5 V / A, combined as sqrt(sigma^2 + 3 tau^2)."""
        cm = next(m for m in self.ch.members if m.station == w["station"] and m.role == "cm_xt")
        bar = self.ch.data["xt_arms"]["parts"]["bar"]
        bw, d = bar.get("w", cm.sec.b), bar["d"]
        A, Zs, Zw = bw * d, bw * d ** 2 / 6, d * bw ** 2 / 6
        best = dict(eq=0.0)
        for k in self._links(f"XT-BAR-{w['id']}"):
            for act in end_actions(res.forces[k]):
                sig = abs(act["N"]) / A + abs(act["My"]) / Zs + abs(act["Mz"]) / Zw
                tau = rect_torsion(act["T"], bw, d) + 1.5 * max(abs(act["Vy"]), abs(act["Vz"])) / A
                eq = math.sqrt(sig ** 2 + 3 * tau ** 2)
                if eq > best["eq"]:
                    best = dict(eq=eq, sigma=sig, tau=tau, T=act["T"], M_strong=act["My"], M_weak=act["Mz"])
        return best

    def gusset_elements(self) -> list[tuple[int, dict]]:
        """Each hinge gusset's frame element with the gusset (Chassis.hinge_gussets), its i end on the crossmember's face."""
        if not hasattr(self, "_gussets"):
            by_id = {g["id"]: g for g in self.ch.hinge_gussets()}
            self._gussets = [(k, by_id[el.member]) for k, el in enumerate(self.f.elements) if el.member in by_id]
        return self._gussets

    def gusset_weld_group(self, g: dict, end: int) -> dict:
        """The weld round one cut end of hinge gusset g (xt_hinges `gusset` `weld`), end 0 on the crossmember's face and 1 on
        the rail's inner web: the face's normal and its horizontal direction, and the weld's pieces as points along the face
        from the axis's point on it, each with its throat and length. The top and bottom walls' edges run 70.7 mm along the
        face in a 90 degree angle, the short side's wall meets it at 45 degrees and the long side's at 135 degrees."""
        w = self.ch.data["xt_hinges"]["gusset"]["weld"]
        sec = self.ch.sections[next(f for f in self.ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
        half, h = sec.b / 2 * math.sqrt(2), sec.d / 2
        e, s = g["face"], g["side"]
        if end == 0:
            n, along, short = np.array((e, 0.0, 0.0)), np.array((0.0, 1.0, 0.0)), s * half
        else:
            n, along, short = np.array((0.0, -s, 0.0)), np.array((1.0, 0.0, 0.0)), -e * half
        throats = dict(edge=w["leg"] * math.cos(math.pi / 4), acute=w["acute_leg"] * math.cos(math.pi / 8), obtuse=w["obtuse_throat"])
        pts = []
        k = 12
        for j in range(k):
            a = -half + (j + 0.5) * 2 * half / k
            pts += [(a, h, throats["edge"], 2 * half / k), (a, -h, throats["edge"], 2 * half / k)]
            b = -h + (j + 0.5) * 2 * h / k
            pts += [(short, b, throats["acute"], 2 * h / k), (-short, b, throats["obtuse"], 2 * h / k)]
        return dict(n=n, along=along, pts=np.array(pts), throats=throats)

    def gusset_weld_stress(self, res, k: int, g: dict) -> float:
        """The largest throat stress round either cut end of hinge gusset g, frame element k, by the elastic vector method:
        the end's force and moment from the element, moved to the weld's centroid, its normal force and its two moments in
        the face's plane over the weld's throat area and second moments, and its two shears in that plane and its twist
        about the normal over the area and the polar moment, all on the throats (AS 4100 9.7.3.10)."""
        el = self.f.elements[k]
        xyz = np.asarray(self.f.nodes, float)
        R, _ = el.axes(xyz)
        fl = np.asarray(res.forces[k], float)
        worst = 0.0
        for end, node in ((0, el.i), (1, el.j)):
            F, M = R.T @ fl[6 * end:6 * end + 3], R.T @ fl[6 * end + 3:6 * end + 6]
            grp = self.gusset_weld_group(g, end)
            n, along, up = grp["n"], grp["along"], np.array((0.0, 0.0, 1.0))
            a, b, t, ds = grp["pts"].T
            A = t * ds
            ac, bc = float(np.sum(A * a) / A.sum()), float(np.sum(A * b) / A.sum())
            Iaa, Ibb = float(np.sum(A * (a - ac) ** 2)), float(np.sum(A * (b - bc) ** 2))
            Mc = M + np.cross(xyz[node] - (xyz[node] + ac * along + bc * up), F)
            nm = np.cross(n, Mc)
            sig = F @ n / A.sum() + (nm @ up) * (b - bc) / Ibb + (nm @ along) * (a - ac) / Iaa
            r = np.outer(a - ac, along) + np.outer(b - bc, up)
            tau = (F - (F @ n) * n) / A.sum() + (Mc @ n) * np.cross(n, r) / (Iaa + Ibb)
            worst = max(worst, float(np.max(np.sqrt(sig ** 2 + np.sum(tau ** 2, axis=1)))))
        return worst

    def gusset_web(self, res, k: int, g: dict) -> dict:
        """I2-99: the rail's 4 mm inner web under hinge gusset g's rail end, frame element k, read as CIDECT Design Guide 3's
        chord face plastification of an RHS T or Y joint (2nd edition, Table 3.1): N* = fy t squared / (1 - beta) (2 eta +
        4 sqrt(1 - beta)) Qf for a branch square to the face, beta and eta its sides over the face's width, and for the
        gusset at 45 degrees on the bare web N1* = fy t squared / ((1 - beta) sin theta) (2 eta / sin theta + 4 sqrt(1 -
        beta)) Qf. Where the gusset lands on its cheek's step, the step is read as the plate it is (I2-102): a patch on the
        web of the step's height and of the length its own bending spreads the gusset's push normal to the web over, the
        gusset's cut face along the web, a = its width times root 2, and a cantilever c each side, the web's reaction
        uniform under it, so N c squared = 2 Mp (a + 2 c) with the step's plastic moment Mp = fy t squared h / 4, and at
        most the step's own length (est.: the patch is not the guide's full-width reinforcing plate). Qf = (1 - |n|) to
        the power 0.6 - 0.5 beta, n the rail's own normal stress at the gusset's height over its fy, taken as compression
        whatever its sign (est.). Returns the gusset's axial force at that end `n1`, the capacity in the gusset's axis
        `cap`, n, Qf, the patch's length `patch` and the step's two welds' stress under the gusset's pull over it."""
        rail = self.ch.role_sec["rail"]
        sec = self.ch.sections[next(f for f in self.ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
        ck = self.ch.data["xt_hinges"]["cheek"]
        b0, t0, fy0 = rail.d, rail.t, rail.fy
        th = math.radians(45.0)
        sig = self.normal_at_level(res, f"RL-{SIDES[g['side']]}", g["p1"][0], g["p1"][2])
        n = min(0.99, sig / fy0)
        n1 = abs(float(res.forces[k][6]))
        if g.get("on_cheek"):                            # the step spreads it as far as its own bending lets it (I2-102)
            station = next(m.station for m in self.ch.members if m.id == g["cm"])
            ls, z0, z1 = (self.ch.step_size(station, k) for k in ("l", "z0", "z1"))
            a = sec.b * math.sqrt(2)                     # the gusset's cut face along the web
            mp = self.ch.data["material"]["plate_fy"] * ck["t"] ** 2 * (z1 - z0) / 4
            push = max(n1 * math.sin(th), 1.0)
            c = (4 * mp + math.sqrt(16 * mp ** 2 + 8 * push * mp * a)) / (2 * push)
            patch = min(ls, a + 2 * c)
            bb, ee = (z1 - z0) / b0, patch / b0
            qf = (1 - n) ** (0.6 - 0.5 * bb)
            cap = fy0 * t0 ** 2 / (1 - bb) * (2 * ee + 4 * math.sqrt(1 - bb)) * qf / math.sin(th)
            welds = n1 * math.sin(th) / (2 * patch * 0.7 * ck["leg"])
        else:
            bb, ee = sec.d / b0, sec.b / b0
            qf = (1 - n) ** (0.6 - 0.5 * bb)
            cap = fy0 * t0 ** 2 / ((1 - bb) * math.sin(th)) * (2 * ee / math.sin(th) + 4 * math.sqrt(1 - bb)) * qf
            welds, patch = 0.0, None
        return dict(n1=n1, cap=cap, n=n, qf=qf, sigma=sig, welds=welds, patch=patch)

    def gusset_welds(self) -> dict:
        """CHS-16: the hinge gussets' end welds in every load case, the largest throat stress round either cut end of any
        gusset (gusset_weld_stress) against AS 4100 9.7.3's 0.8 x 0.6 fuw over the case's factor, and the rail's web under
        each gusset's rail end (gusset_web), the gusset's axial stress against the stress at which the web plastifies under
        it, over the case's factor (I2-99)."""
        mat = self.ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        lcs = {lc["id"]: lc for lc in self.ch.data["load_cases"]}
        fac = {lc_id: (lcs[lc_id]["factor"] if lc_id in lcs else 1) for lc_id in self.gusset_env}
        A1 = self.ch.sections[next(f for f in self.ch.data["fittings"] if f["id"] == "CH-P08")["section"]].A
        rows = [(f"end welds, {lc_id}", e["mpa"], wcap / fac[lc_id]) for lc_id, e in self.gusset_env.items()]
        rows += [(f"rail's web under the rail end, chord face plastification, {lc_id}", e["n1"] / A1, e["cap"] / A1 / fac[lc_id])
                 for lc_id, e in self.gusset_web_env.items()]
        rows += [(f"its step's two welds to the web under a gusset's pull, {lc_id}", e["welds_max"], wcap / fac[lc_id])
                 for lc_id, e in self.gusset_web_env.items() if e["welds_max"] > 0]
        lc_id, e = max(self.gusset_env.items(), key=lambda kv: kv[1]["mpa"] * fac[kv[0]])
        wl, we = max(self.gusset_web_env.items(), key=lambda kv: kv[1]["util"] * fac[kv[0]])
        return _local("Hinge gussets' end welds and the rail's web under them (CH-P08)", rows,
                      f"{e['gusset']} in {lc_id}, {e['case']}, and on the web {we['n1'] / 1000:.1f} kN along {we['gusset']} against "
                      f"{we['cap'] / 1000:.1f} kN" + (f" over its step's {we['patch']:.0f} mm" if we.get("patch") else "") +
                      f", Qf {we['qf']:.2f} for the rail's {we['sigma']:.0f} MPa, in {wl}, {we['case']}")

    def cheek_check(self) -> dict:
        """CHS-14 (I2-92): the hinge cheeks' welds (CH-P16) in every LC8a case at 58.9 kN and at the 78.5 kN ultimate, each
        under the force the frame model's pin passes from the hinge bar into the hinge's cheeks, shared equally where a
        hinge has two (cheek_welds), against AS 4100 9.7.3's 0.8 x 0.6 fuw."""
        mat = self.ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]

        def cap(part):                                   # a filler's own section against the plate's fy, the welds on their throats
            return mat["plate_fy"] if "section" in part else wcap
        rows = [(f"{part}, {lc_id}", r["mpa"], cap(part)) for lc_id in ("LC8a", "LC8u") for part, r in self.cheek_env[lc_id].items()]
        w = max(((lc_id, part, r) for lc_id in ("LC8a", "LC8u") for part, r in self.cheek_env[lc_id].items()),
                key=lambda t: t[2]["mpa"] / cap(t[1]))
        lc_id, part, r = w
        return _local("Hinge cheeks' welds (CH-P16)", rows,
                      f"the pin's force from the hinge bar into {r['cheek']}, its share, {r['f'][0] / 1000:+.1f} kN along, {r['f'][1] / 1000:+.1f} kN "
                      f"across and {r['f'][2] / 1000:+.1f} kN up, at {r['wheel']} in {r['case']}")

    def hinge_runs(self) -> dict:
        """CHS-18 (I2-119, I2-121, the conductor's ruling of 27 Nov 2026): each hinge bar's three weld runs a side to its crossmember in every case in which
        the trailer's own loads pass through the hinge joint, LC1 to LC5b, LC8a at the pull and at its ultimate and LC8b,
        on each of the frame's models (_hinge_envelope), the rigid bars' runs as one group and the elastic bars' each on its
        own, by the elastic vector method against AS 4100 9.7.3's 0.8 x 0.6 fuw over each case's factor. VSB1's drawbar and
        chain tests (LC6, LC6b) hold the body on a rig at its suspension mounts (VSB1 Rev 6 14.2.1), and 14.3 judges the
        drawbar, its attachments and the chain points, not the suspension's joints under the rig's forces, so their readings
        are given beside the row in `beside` and do not fail it."""
        mat = self.ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        lcs = {lc["id"]: lc for lc in self.ch.data["load_cases"]}
        fac = {lc_id: (lcs[lc_id]["factor"] if lc_id in lcs else 1) for lc_id in self.run_env}
        read = [k for k in self.run_env if k not in RIG_CASES]
        rows = [(f"{lc_id}, the hinge bars {bar}", r["mpa"], wcap / fac[lc_id]) for lc_id in read for bar, r in self.run_env[lc_id].items()]
        lc_id, bar, r = max(((k, b, r) for k in read for b, r in self.run_env[k].items()), key=lambda t: t[2]["mpa"] * fac[t[0]])
        about = "the runs' centroid" if r.get("run") is None else "the run's centroid"
        out = _local("Hinge bars' weld runs to their crossmembers (XT-BAR)", rows,
                     f"{r['line']} at {r['wheel']}, {abs(r['f'][0]) / 1000:.1f} kN along, {abs(r['f'][1]) / 1000:.1f} kN across and "
                     f"{abs(r['f'][2]) / 1000:.1f} kN up with {math.hypot(*r['m']) / 1e6:.2f} kNm about {about}, the hinge bars {bar}, "
                     f"in {lc_id}, {r['case']}")
        out["beside"] = {f"{k}, the hinge bars {b}": dict(util=v["mpa"] * fac[k] / wcap, mpa=v["mpa"], limit_mpa=wcap / fac[k], case=v["case"],
                                                          wheel=v["wheel"], line=v["line"])
                         for k, e in self.run_env.items() if k in RIG_CASES for b, v in e.items()}
        return out

    def seam_section(self, cm) -> dict:
        """The seams of a twin hinge crossmember (xt_hinges `seam`, CHS-20): its outer mid-line's enclosed area for Bredt's
        shear flow, one cell's first moment about the pair's middle and the pair's weak-axis second moment for the shear
        flow between the halves, the two seams, top and bottom, and each seam's throat, 5/8 R by GMAW, read at no more than
        the tubes' walls either side of it carry, what the corners allow (est.)."""
        sec, sd = cm.sec, self.ch.data["xt_hinges"]["seam"]
        rm = sec.ro - sec.t / 2
        am = (sec.b - sec.t) * (sec.d - sec.t) - (4 - math.pi) * rm ** 2
        a_cell = sec.A / sec.cells
        return dict(am=am, q=a_cell * sec.cell_b / 2, i=sec.I_weak, seams=2 * (sec.cells - 1),
                    throat=min(sd["throat_r"] * sec.ro, sec.t), share=float(sd["share"]), run=self.ch.data["xt_hinges"]["bar"]["run"])

    def _seam_envelope(self, lc_id: str, label: str, res, bar: str):
        """In one case on frame model `bar`: each twin hinge crossmember's seams (CHS-20). Along the crossmember each
        element end's torque puts the outer perimeter's shear flow T / 2 Am through the seams, and its shear across the
        trailer's line V Q / I between the halves, half on each seam, the two taken together on the seam where they add.
        At each run of its hinge bars the rear tube alone takes the run's force and moment (_run_actions), and the front
        tube's `share` of them crosses the seams over the run's own length, the force spread evenly and each moment about
        the run's centroid as a linear spread, 6 M / L^2, on the safe side of the seams' length beyond the run. A rigid
        bar's runs act as one group, as CHS-18 reads them, so its force crosses over the runs' welded length and its
        moment over the group's length. Each seam is read on its throat by the vector sum of its flow along it and the
        run's force across it."""
        ch = self.ch
        if not ch.data["xt_hinges"].get("seam"):
            return
        xyz = np.asarray(self.f.nodes, float)
        for cm in ch.hinge_crossmembers():
            if getattr(cm.sec, "cells", 1) < 2:
                continue
            p = self.seam_section(cm)
            flow = 0.0
            for k in self._links(cm.id):
                for act in end_actions(res.forces[k]):
                    flow = max(flow, abs(act["T"]) / (2 * p["am"]) + abs(act["Vy"]) * p["q"] / p["i"] / (p["seams"] / 2) / 2)
            best = (flow, 0.0, 0.0, None, np.zeros(3), np.zeros(3))
            runs = ch.data["xt_hinges"]["bar"]["runs"]
            for w in ch.suspension:
                if w["station"] != cm.station:
                    continue
                key = (w["id"], bar == "rigid")
                cache = self.__dict__.setdefault("_run_groups", {})
                if key not in cache:
                    cache[key] = [dict(y=None, g=self.hinge_run_group(w))] if bar == "rigid" else self.hinge_runs_alone(w)
                # a rigid bar's runs act as one group, as CHS-18 reads them: its force over the runs' welded length and its
                # moment over the group's length, where each run of an elastic bar passes its own over its own length
                lf, lm = (len(runs) * p["run"], max(runs) - min(runs) + p["run"]) if bar == "rigid" else (p["run"], p["run"])
                for grp, (F, M) in zip(cache[key], self._run_actions(res, w["id"], cache[key])):
                    qx = p["share"] * (abs(F[0]) / lf + 6 * abs(M[2]) / lm ** 2) / p["seams"]
                    qz = p["share"] * (abs(F[2]) / lf + 6 * abs(M[0]) / lm ** 2) / p["seams"]
                    if math.hypot(flow, qx, qz) > math.hypot(*best[:3]):
                        at = f"{w['id']}'s runs" if grp["y"] is None else f"{w['id']}'s run {grp['y']:+.0f} mm off the centreline"
                        best = (flow, qx, qz, at, F, M)
            q = math.hypot(*best[:3])
            e = self.seam_env.setdefault(lc_id, {}).setdefault(bar, dict(mpa=-1.0))
            if q / p["throat"] > e["mpa"]:
                e.update(mpa=q / p["throat"], n_mm=q, along=best[0], across=best[1], up=best[2], at=best[3] or "between the runs",
                         member=cm.id, case=label, throat=p["throat"], f=[float(v) for v in best[4]], m=[float(v) for v in best[5]])

    def seam_welds(self) -> dict:
        """CHS-20: each twin hinge crossmember's two seams, flare-V groove welds in the R15 corners where its tubes meet, in
        every case through the hinge joint, LC1 to LC5b, LC8a at the pull and at its ultimate and LC8b, on each of the
        frame's models (_seam_envelope), against AS 4100 9.7.3's 0.8 x 0.6 fuw over each case's factor, as CHS-18 reads the
        runs. VSB1's rig cases LC6 and LC6b are given beside and do not fail it, for CHS-18's reason."""
        mat = self.ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        lcs = {lc["id"]: lc for lc in self.ch.data["load_cases"]}
        fac = {lc_id: (lcs[lc_id]["factor"] if lc_id in lcs else 1) for lc_id in self.seam_env}
        read = [k for k in self.seam_env if k not in RIG_CASES]
        if not read:
            return dict(_local("Twin hinge crossmembers' seams", [("no twin crossmember", 0.0, wcap)], "no seam"), beside={})
        rows = [(f"{lc_id}, the hinge bars {bar}", r["mpa"], wcap / fac[lc_id]) for lc_id in read for bar, r in self.seam_env[lc_id].items()]
        lc_id, bar, r = max(((k, b, r) for k in read for b, r in self.seam_env[k].items()), key=lambda t: t[2]["mpa"] * fac[t[0]])
        out = _local("Twin hinge crossmembers' seams", rows,
                     f"the seam of {r['member']} at {r['at']}, {r['along']:.0f} N/mm along it from its torque and shear and "
                     f"{math.hypot(r['across'], r['up']):.0f} N/mm across it from the run, {r['n_mm']:.0f} N/mm on its {r['throat']:.1f} mm "
                     f"throat, the hinge bars {bar}, in {lc_id}, {r['case']}")
        out["beside"] = {f"{k}, the hinge bars {b}": dict(util=v["mpa"] * fac[k] / wcap, mpa=v["mpa"], limit_mpa=wcap / fac[k], case=v["case"],
                                                          member=v["member"], at=v["at"])
                         for k, e in self.seam_env.items() if k in RIG_CASES for b, v in e.items()}
        out["throat_mm"] = r["throat"]
        return out

    def hinge_bar_report(self) -> dict:
        """CHS-19 (I2-119), reported: Cruisemaster's hinge bars and hinge plates, whose section and grade are not published,
        in every LC8a case at the pull and at its ultimate on the elastic bars: each bar's largest stress on its estimated
        section (bar_stress) against the 350 MPa of a grade 350 bar (est.), and each pair of hinge plates' largest force
        from its bush along the trailer and in all, for Cruisemaster to rate. The rigid bars carry no stress of their own."""
        rows, plates = [], {}
        for lc_id in ("LC8a", "LC8u"):
            for bar, r in self.bar_env.get(lc_id, {}).items():
                rows.append((f"the bar, {lc_id}, {bar}", r["mpa"], self.ch.data["material"]["plate_fy"]))
                for pair, p in r["plates"].items():
                    plates[f"{lc_id}, {bar}, {pair} pair"] = dict(p)
        if not rows:
            return dict(name="Hinge bars and hinge plates (reported)", load="no elastic bar", parts=[], util=0.0, governing="", mpa=0.0,
                        limit_mpa=0.0, plates={}, bars={})
        lc_id, bar, r = max(((lc_id, bar, r) for lc_id in ("LC8a", "LC8u") for bar, r in self.bar_env[lc_id].items()), key=lambda t: t[2]["mpa"])
        out = _local("Hinge bars and hinge plates, Cruisemaster's (reported)", rows,
                     f"the bar at {r['wheel']} on its estimated section, the hinge bars {bar}, in {r['case']}")
        out["plates"] = plates
        out["bars"] = {f"{lc_id}, {bar}": dict(mpa=v["mpa"], case=v["case"], wheel=v["wheel"]) for lc_id in ("LC8a", "LC8u")
                       for bar, v in self.bar_env.get(lc_id, {}).items()}
        # VSB1's rig cases beside the rows, not read by them (hinge_runs)
        out["beside"] = {f"{lc_id}, {bar}": dict(mpa=v["mpa"], case=v["case"], wheel=v["wheel"],
                                                 plates={k: dict(p) for k, p in v["plates"].items()})
                         for lc_id in RIG_CASES for bar, v in self.bar_env.get(lc_id, {}).items()}
        return out

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
        wid, dr = max(u8["droop"].items(), key=lambda kv: kv[1]["n"], default=(None, None))
        worst = (f"the worst droop limit {dr['n'] / 1000:.1f} kN at {wid} in {dr['case']}" if wid else
                 "no arm reaches its droop limit, so the limits and their brackets take nothing")
        return _local("XT arms' droop limits and airbag brackets", rows, f"LC8a's arms, {worst}")

    def recovery_summary(self) -> dict:
        """LC8a's supports over its cases (I2-94), for CHASSIS.md and Cruisemaster's items: the cases read, the tyres off the
        ground, the pulls the trailer tips under and the least share of the pull it holds, each droop limit's and airbag's
        largest force, and the held hinges' largest force along the trailer with the hinge bar's moment from the pivot up to
        the cheek's pin. With them, the pulls the trailer slides sideways under with every wheel free, the least pull that
        tips it at the coupling up and down, a held wheel's turns at each bound of the tyres' grip, and CHS-18's and CHS-14's
        readings at each bound (`mu`, I2-124), the worse of which their rows read."""
        ck = self.ch.data["xt_hinges"]["cheek"]
        depth = self.ch.V["pivot_below"] - ck["bar_d"] / 2
        mat = self.ch.data["material"]
        wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
        out = {}
        for lc_id, e in self.lc8_arms.items():
            dw, dr = max(e["droop"].items(), key=lambda kv: kv[1]["n"], default=(None, dict(n=0.0, case="", airbag_n=0.0, off=[])))
            bw, bg = max(e["bag"].items(), key=lambda kv: kv[1]["n"])
            hw, hg = max(e["hinge"].items(), key=lambda kv: abs(kv[1]["f"][0]), default=(None, dict(f=np.zeros(3), case="")))
            least = min(e["tipped"], key=lambda t: t["kn"]) if e["tipped"] else None
            classes, coupling = {}, {}                     # the lugs' and tongues' tipping pulls, and the coupling's apart
            for t in e["tipped"]:
                if t.get("where") == "coupling":
                    if t["kn"] < coupling.get(f"{t['v']:+d}", dict(kn=math.inf))["kn"]:
                        coupling[f"{t['v']:+d}"] = dict(kn=t["kn"], case=t["case"], weight=t["weight"], coupled=t["coupled"])
                    continue
                key = f"{'sideways' if abs(t['h']) >= 20 else 'along'} {t['v']:+d}"
                if key not in classes or t["kn"] < classes[key]["kn"]:
                    classes[key] = dict(kn=t["kn"], case=t["case"], weight=t["weight"], coupled=t["coupled"])
            slid = min(e["slid"], key=lambda t: t["kn"]) if e["slid"] else None
            axle_least = min(e["axle_tipped"], key=lambda t: t["kn"]) if e["axle_tipped"] else None
            by_mu = {}
            for mu, d in getattr(self, "lc8_mu", {}).items():
                runs = {bar: dict(util=r["mpa"] / wcap, mpa=r["mpa"], case=r["case"], wheel=r["wheel"], line=r["line"])
                        for bar, r in d["runs"].get(lc_id, {}).items()}
                cheeks = d["cheeks"].get(lc_id, {})
                part, c = max(cheeks.items(), key=lambda kv: kv[1]["mpa"] / (mat["plate_fy"] if "section" in kv[0] else wcap), default=(None, None))
                by_mu[f"{mu:g}" if mu is not None else "none"] = dict(
                    runs=runs, cheeks=dict(part=part, util=c["mpa"] / (mat["plate_fy"] if "section" in part else wcap), case=c["case"]) if part else None,
                    turns=e["turns"].get(f"{mu}"))
            out[lc_id] = dict(points=dict(e.get("points", {})), cases=e["cases"], lifted=e["lifted"], nose_off=e["nose_off"], tipped=len(e["tipped"]), least=least, lift=e["lift"], nose=e["nose"],
                              tip_classes=classes, coupling_tips=coupling, slid=dict(cases=len(e["slid"]), least=slid),
                              axle=dict(cases=e["axle_cases"], tipped=len(e["axle_tipped"]), least=axle_least),
                              droop=dict(wheel=dw, n=dr["n"], case=dr["case"], airbag_n=dr["airbag_n"], off=dr["off"]),
                              droop_by_wheel={k: v["n"] for k, v in e["droop"].items()},
                              bag=dict(wheel=bw, n=bg["n"], case=bg["case"]),
                              hinge=dict(wheel=hw, f=[float(x) for x in hg["f"]], case=hg["case"], bar_moment_nmm=abs(float(hg["f"][0])) * depth),
                              mu=by_mu)
        return out

    def tipping_pulls(self, supports: list[dict]) -> dict:
        """The least pull that tips the trailer (I2-127, LC8a `tip`), which the frame's readings cannot give, since a pull
        that tips it never reaches the frame at its full size. At each recovery point, with every wheel free, each wheel
        held and each axle held, on each of LC8a's weights and nose supports and at each bound of the grip, each line up,
        level and down is read across the headings: at the lugs and tongues every `step_deg` within LC8a's sideways range
        and then every `fine_deg` within one step of the series' least, where the trailer may start to slide just past it,
        and at the coupling along the rail axis only. Each pull is solved at the `reach_n` (recovery_reactions), which
        takes it at the largest share the trailer holds, so a pull that tips it within the reach gives its tipping pull,
        one that slides it its sliding pull, and one it holds to the reach neither. Returns the table at LC8a's own
        headings, each point's wheel state and line its least tip and slide there, and each point's wheel state and line's
        least over every heading read (`least`)."""
        lc8 = next(lc for lc in self.ch.data["load_cases"] if lc["id"] == "LC8a")
        tp = lc8["tip"]
        reach, step, fine = tp["reach_n"], tp["step_deg"], tp["fine_deg"]
        sd, vd = lc8["sideways_deg"], lc8["vertical_deg"]
        mus = lc8["reaction"].get("mu") or [None]
        wheels = self.ch.suspension
        states = [("free", None)] + [("wheel", w["id"]) for w in wheels]
        states += [("axle", tuple(w["id"] for w in wheels if w["axle"] == a)) for a in ("front", "rear")]
        points = [(where, s) for where in ("front", "rear") for s in (-1, 1)] + ([("coupling", 0)] if lc8.get("coupling") else [])
        own = (-sd, -sd // 2, 0, sd // 2, sd)
        table, least = [], []
        for where, s in points:
            p, _, sx = self.recovery_point(where, s)
            spot = (f"{where} {'kerb' if s < 0 else 'road'}-side point" if s else "the coupling")
            grid = list(range(-sd, sd + 1, step)) if s else [0]
            for kind in ("free", "wheel", "axle"):
                for v in (-vd, 0, vd):
                    got: dict = {}

                    def read(h, held, sup, mu):
                        hr, vr = math.radians(h), math.radians(v)
                        F = reach * np.array([sx * math.cos(hr) * math.cos(vr), math.sin(hr) * math.cos(vr), math.sin(vr)])
                        R = self.recovery_reactions(F, p, held, sup["base"], sup["nose"], mu)
                        here = got.setdefault(h, {})
                        if R["limit"] is None:
                            return None
                        who = "" if held is None else (f", wheel {held} held" if isinstance(held, str) else
                                                       f", both {next(w['axle'] for w in wheels if w['id'] == held[0])} wheels held")
                        kn = R["scale"] * reach / 1000
                        out = dict(kn=kn, where=where, side=s, h=h, v=v, held=held,
                                   case=f"{spot}, {h:+d} deg sideways{who}, {v:+d} deg up, {sup['label']}" + (f", mu {mu:g}" if mu is not None else ""),
                                   weight=sup["label"].split(",")[0], coupled=bool(sup["nose"].get("holds_down")), mu=mu)
                        if R["limit"] not in here or kn < here[R["limit"]]["kn"]:
                            here[R["limit"]] = out
                        return R["limit"], kn

                    for held in [x for k, x in states if k == kind]:
                        for sup in supports:
                            for mu in mus:
                                series = {h: read(h, held, sup, mu) for h in grid}
                                tips = [(r[1], h) for h, r in series.items() if r and r[0] == "tips"]
                                if tips and s:
                                    h0 = min(tips)[1]
                                    for h in range(max(-sd, h0 - step + fine), min(sd, h0 + step - fine) + 1, fine):
                                        if h not in series:
                                            read(h, held, sup, mu)
                    for h in own if s else (0,):
                        r = got.get(h, {})
                        table.append(dict(where=where, side=s, wheels=kind, h=h, v=v, tip=r.get("tips"), slide=r.get("slides")))
                    tip = min((r["tips"] for r in got.values() if "tips" in r), key=lambda t: t["kn"], default=None)
                    slide = min((r["slides"] for r in got.values() if "slides" in r), key=lambda t: t["kn"], default=None)
                    least.append(dict(where=where, side=s, wheels=kind, v=v, tip=tip, slide=slide,
                                      headings=len(got) if s else 1))
        return dict(reach_kn=reach / 1000, step_deg=step, fine_deg=fine, table=table, least=least)

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
                  "hinge_crossmember": [m for m in cms if m.station in ("XT front hinge", "XT centre")]}

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
            elif k == "wall_toe":
                out += self.wall_toe_stresses(res) or [(0.0, "no elastic bar")]
            else:
                for m in groups[d["member"]]:
                    sig = self.member_end_stress(res, m.id)
                    if k == "weld_root":
                        sig *= m.sec.t / throat.get(m.role, throat["default"])
                    out.append((sig, m.id))
            return out

        out = []
        for d in ch.data["fatigue_details"]:
            if d["stress"] in ROOT_READERS:
                out.append(self.root_fatigue(d, lc1, lc))
                continue
            best = (0.0, "", "")
            for cid, res in lc1.items():
                s, where = max(candidates(d, res))
                if s > best[0] or not best[1]:       # a row that reads nothing still says where and why (FAT-25 on the twin)
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

    def wall_toe_stresses(self, res) -> list[tuple[float, str]]:
        """FAT-25: the structural stress at each hinge bar run's front fillet's toe in its crossmember's bottom wall on the
        elastic bars, the wall's own bending there, its plate model's `toe_mpa_kn` times the force the run's front weld
        points pass (each point's force taken whole, whatever its sign), plus the crossmember's nominal stress at its
        ends (member_end_stress), both at their largest together. The rigid bars pass no fillet's force of their own. Where
        no run's front fillet stands on a wall's flat (wall_flats), as on the twin hinge crossmembers whose fillets all
        stand over webs, the row reads no wall."""
        from .chassis import wall_flats
        ch, V = self.ch, self.ch.V
        b = ch.data["xt_hinges"]["bar"]
        wall = b.get("wall")
        if not isinstance(wall, dict):
            return []
        xyz = np.asarray(self.f.nodes, float)
        y_in = V["rail_c"] - ch.role_sec["rail"].b / 2
        bw = ch.data["xt_arms"]["parts"]["bar"]["w"]
        out = []
        for w in ch.suspension:
            links = self._links(f"hinge {w['id']}")
            if not links:
                continue
            cm = next(m for m in ch.members if m.station == w["station"] and m.role == "cm_xt")
            xb = ch.hinge_bar_x(cm)
            if not wall_flats(ch, cm, xb, bw)[-1]:
                out.append((0.0, f"no wall's flat under {w['id']}'s runs on {cm.id}, both fillets over webs"))
                continue
            per = [0.0] * len(b["runs"])
            for k in links:
                p = xyz[self.f.elements[k].i]
                if p[0] < xb:
                    r = min(range(len(b["runs"])), key=lambda i: abs(b["runs"][i] - (y_in - abs(p[1]))))
                    per[r] += abs(float(res.forces[k][0]))
            sig = self.member_end_stress(res, cm.id)
            out += [(n / 1000 * wall["toe_mpa_kn"][r] + sig, f"{w['id']}'s run {b['runs'][r]:g} mm inboard on {cm.id}") for r, n in enumerate(per)]
        return out

    def run_root_stresses(self, res) -> list[tuple[float, float, str]]:
        """FAT-26 (I2-125): the roots of the hinge bars' weld runs in one case, each run read as CHS-18 reads it
        (_hinge_envelope), the rigid bars' three runs a side as one group and the elastic bars' each on its own under the
        forces its own welds pass, at each fillet's two ends by the elastic vector method, the throat stress there split
        into sigma_w normal to the fillet's axis and tau_w along it (group_throat), as (sigma_w, tau_w, where)."""
        if self.hinges != "crossmember":
            return []
        cache = self.__dict__.setdefault("_run_groups", {})
        rigid = self.fm.hinge_bar != "elastic"
        out = []
        for w in self.ch.suspension:
            key = (w["id"], rigid)
            if key not in cache:
                cache[key] = [dict(y=None, g=self.hinge_run_group(w))] if rigid else self.hinge_runs_alone(w)
            groups = cache[key]
            for grp, (F, M) in zip(groups, self._run_actions(res, w["id"], groups)):
                out += [(s, t, f"{name} at {w['id']}" + (", the runs as one group" if rigid else ""))
                        for name, s, t in group_throat(grp["g"], F, M)]
        return out

    def cheek_root_stresses(self, res) -> list[tuple[float, float, str]]:
        """FAT-27 (I2-125): the roots of the hinge cheeks' and fillers' load-carrying welds in one case, under each
        hinge's pin force and each cheek's share of it, as CHS-14 reads them in LC8a (_cheek_envelope, cheek_welds), each
        weld's stress taken whole as normal to its throat, on the safe side, with none along it. The filler's own section
        is no weld and is left out."""
        if self.hinges != "crossmember":
            return []
        xyz = np.asarray(self.f.nodes)
        cheeks = self.ch.hinge_cheeks()
        out = []
        for wid, k in self.fm.cheek_pins.items():
            el = self.f.elements[k]
            R, _ = el.axes(xyz)
            F = -R.T @ np.asarray(res.forces[k][6:9])
            mine = [c for c in cheeks if c["wheel"] == wid]
            px = next(w["pivot"][0] for w in self.ch.suspension if w["id"] == wid)
            for c in mine:
                out += [(mpa, 0.0, f"the {'front' if c['way'] < 0 else 'rear'} cheek's {part} at {wid}")
                        for part, mpa in self.cheek_welds(F * self.cheek_share(c, mine, px), c).items() if "section" not in part]
        return out

    def root_fatigue(self, d: dict, lc1: dict, lc: dict) -> dict:
        """FAT-26 and FAT-27 (I2-125): a weld's root in LC10 on IIW-1823-07's two curves for the stress in its throat, FAT
        `fat` on sigma_w normal to the weld's axis (414, slope 3 to its knee at 10 million cycles) and FAT `fat_shear` on
        tau_w along it (Table 3.2-2 no. 2, slope 5 to its knee at 100 million), the two in phase and combined by IIW's
        interaction (4.3.1, Table 4.3-1, CV 1.0). The frequent ranges pass when (sigma_w / its CAFL)^2 + (tau_w / its
        CAFL)^2 is at most 1, and the occasional ranges when the Miner damage they use up by the same interaction
        (root_damage) is at most LC10's miner_limit, each at its worst point, case and frame model. range_mpa is the
        frequent's equivalent normal range, the normal CAFL times the root of that sum, so the row compares with its CAFL
        as the others do."""
        read = getattr(self, ROOT_READERS[d["stress"]])
        fat, fs = d["fat"], d["fat_shear"]
        c_n, c_s = sn_range(fat, 3, 1e7, 1e7), sn_range(fs, 5, 1e8, 1e8)
        k, n = lc["occasional_factor"], lc["occasional_cycles"]
        freq, occ = (0.0, 0.0, 0.0, "no weld read", ""), (0.0, 0.0, 0.0, "no weld read", "")
        for cid, res in lc1.items():
            for sw, tw, where in read(res):
                u = math.hypot(sw / c_n, tw / c_s)
                if u > freq[0]:
                    freq = (u, sw, tw, where, cid)
                dmg = root_damage(k * sw, k * tw, fat, fs, n)
                if dmg > occ[0]:
                    occ = (dmg, sw, tw, where, cid)
        u, sw, tw, where, cid = freq
        return dict(id=d["id"], name=d["name"], iiw=d["iiw"], fat=fat, cafl=c_n, range_mpa=u * c_n, where=where, case=cid,
                    occasional_range_mpa=k * occ[1], damage=occ[0], ok=u <= 1 + 1e-9 and occ[0] <= lc["miner_limit"],
                    hot_spot=False, fat_shear=fs, shear_cafl=c_s, util=u, normal_mpa=sw, shear_mpa=tw,
                    occasional_shear_mpa=k * occ[2], occasional_where=occ[3], occasional_case=occ[4])

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
        rail's front end (galvanising_holes, I2-75) follow the services' holes, on both rails, their use as their run. The
        bolt holes of the fresh tanks' bearers and the front guard's hangers (Layout.fixing_holes, I2-109) come after every
        other hole, so no hole's id moves: those in the rails' webs as the services' are, those in the XT crossmembers'
        webs on their crossmember's own section (_member_hole_sites)."""
        import yaml
        from .partsdb import DATA
        ch, V, comp = self.ch, self.ch.V, self.ch.comp
        rail, raiser = comp.rail, comp.raiser
        rules = ch.data["hole_rules"]
        rows = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8")).get("holes") or []
        at = {m.id: m.p0[0] for m in ch.members}
        rows = [dict(r, x=hole_x(r, at.__getitem__)) for r in rows]
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
        # crossmember (member_galvanising_holes shock_plate_web), each location with its 10 mm check hole in the rail's
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
        fixings = self.lay.fixing_holes() if hasattr(self.lay, "fixing_holes") else []
        for f in (f for f in fixings if f["member"].startswith("RL-")):
            s = 1 if f["y"] > 0 else -1
            inner = f["face"] == "inner web"
            face = ("kerb side" if s > 0 else "road side") if inner else ("road side" if s > 0 else "kerb side")
            rows.append(dict(member=f["member"], face=face, run=f["use"], x=f["x"], y=f["y"], z=f["z"], d=float(f["d"]),
                             length=float(f["length"]), late=True))
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
            gross = dict(A=comp.A, z=comp.z_centroid, I=comp.I_strong, I_weak=comp.I_weak, Aw=comp.Aw, Aw_width=rail.Aw_width + raiser.Aw_width)
            gap, weld = min(((_box_gap(hole_box, bx), what) for what, bx in toes), key=lambda t: t[0])
            sites.append(dict(r, runs=[r["run"]], rows=[f"{r['member']} {r['face']}"], frame=f"RL-{SIDES[s]}", wall=wall, open=False,
                              d=d, length=L, fu=fu, box=hole_box, edge_mm=edge, edge_need=rules["edge_factor"] * d, toe_mm=gap, toe_need=rules["toe_factor"] * d,
                              toe_weld=weld, gross=gross, strips=strips, levers=z_lever_pts, face_w=face_w,
                              net=net_section(gross, strips, z_lever_pts, y_lever, face_w, d)))
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
        bolts = self._fixing_member_holes(fixings)
        members = self._member_hole_sites(rules, bolts)
        k = len(members) - len(bolts)
        sites += members[:k] + late + members[k:]
        for k, h in enumerate(sites, 1):
            h["id"] = f"H-{k:02d}"
        self._read_together(sites)
        return sites

    def _read_together(self, sites: list[dict]):
        """Holes that stand within a diameter of one another along their member, the larger of the two, a slot's length
        added, are read on one net section (I2-111): each hole's section loses every such hole's strip, so a section that
        cuts several holes, beside the XT centre crossmember a service hole in a raiser's outer web and the drain, check
        hole and vent in its rail's webs, is read as the section it is. Each hole keeps its own lever to the net section's
        centroid and its own wall's torsion factor, its wall less every such hole in that wall. Holes a diameter or more
        apart along the member are read alone. A hinge gusset's holes carry no frame load and are placed only."""
        axes = {}
        for el in self.f.elements:
            if el.member not in axes and not el.sec.rigid:
                a, b = (np.asarray(self.f.nodes[n], float) for n in (el.i, el.j))
                axes[el.member] = (b - a) / np.linalg.norm(b - a)
        walled = [h for h in sites if not h.get("open") and not h.get("placement_only") and h.get("frame") in axes]
        along = {id(h): float(np.dot((h["x"], h["y"], h["z"]), axes[h["frame"]])) for h in walled}

        def near(a, b):
            reach = max(a["d"], b["d"]) + (a["length"] - a["d"]) / 2 + (b["length"] - b["d"]) / 2
            return a["frame"] == b["frame"] and abs(along[id(a)] - along[id(b)]) < reach

        for h in walled:
            group = [o for o in walled if near(h, o)]
            if len(group) < 2:
                continue
            strips = [p for o in group for p in o["strips"]]
            d_wall = sum(o["d"] for o in group if o.get("wall_id", o["wall"]) == h.get("wall_id", h["wall"]))
            net = net_section(h["gross"], strips, h["levers"], h["net"]["y_lever"], h["face_w"], d_wall)
            h["net"] = dict(net, **({"base": h["net"]["base"]} if "base" in h["net"] else {}))
            h["with"] = [o["id"] for o in group if o is not h]

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
            # heights from the member's axis, as _member_hole_sites gives the member's other holes, so both read together
            z_l = z - V["db_z"]
            gross = dict(A=sec.A, z=0.0, I=sec.I_strong, I_weak=sec.I_weak, Aw=sec.Aw_depth, Aw_width=sec.Aw_width)
            strips = [dict(dA=sec.t * d, z=z_l, own=sec.t * d ** 3 / 12, y=(sec.b - sec.t) / 2, own_z=d * sec.t ** 3 / 12, web=True)]
            levers, face_w = [z_l - d / 2, z_l + d / 2], sec.d - sec.t
            edge = min(z - (zb + sec.ro), (zt - sec.ro) - z)
            edge_need = rules["edge_factor"] * d
            if u / rules["end_factor"] < edge / rules["edge_factor"]:      # the member's sawn end, 1.5 d (Table 9.6.2)
                edge, edge_need = u, rules["end_factor"] * d
            member = f"DB-{SIDES[s]}A"
            out.append(dict(member=member, face=f"{web} web", run=g["use"], x=x, y=y, z=z, d=d, length=d, runs=[g["use"]],
                            rows=[f"{member} {web} web"], frame=member, wall=f"the drawbar member's {web} web", open=False,
                            fu=rules["fu"]["rail"], fy=sec.fy, box=(x - d / 2, y - 1, z - d / 2, x + d / 2, y + 1, z + d / 2),
                            edge_mm=edge, edge_need=edge_need, toe_mm=gap, toe_need=rules["toe_factor"] * d, toe_weld=weld,
                            u_web=u, z_under=float(g["z_under"]), gross=gross, strips=strips, levers=levers, face_w=face_w,
                            net=dict(net_section(gross, strips, levers, sec.b / 2, face_w, d),
                                     base=dict(Z_weak=sec.Z_weak, I_weak=sec.I_weak, C=sec.C, y_max=sec.b / 2))))
        return out

    def _fixing_member_holes(self, fixings: list[dict]) -> list[dict]:
        """The bolt holes the fresh tanks' bearers and the front guard's hanger make in the XT crossmembers' webs
        (Layout.fixing_holes, I2-109), each as the dip gives a hole in its member's web (cad/chassis_dip.py), its place
        along the member and across it read from its centre, for _member_hole_sites."""
        from .chassis_dip import Tube
        mem = {m.id: m for m in self.ch.members}
        out = []
        for f in fixings:
            m = mem.get(f["member"])
            if m is None or m.id.startswith("RL-"):
                continue
            t = Tube(m.id, m.p0, m.p1, m.sec, m.depth_dir)
            c = np.array((f["x"], f["y"], f["z"]), float)
            u, z_l = float(np.dot(c - t.p0, t.ex)), float(np.dot(c - t.p0, t.ez))
            row = dict(member=m.id, tube=t.name, tube_L=t.L, end=0 if u < t.L / 2 else 1, u=u, z_l=z_l, d=float(f["d"]),
                       use=f["use"], via="own", u_web=min(u, t.L - u), z_under=z_l + m.sec.d / 2)
            if getattr(m.sec, "cells", 1) > 1:       # a twin: the bolt's hole in each tube's webs, as the dip names them
                k, web = {"front web": (1, 1), "front tube's rear web": (1, -1), "rear tube's front web": (0, 1), "rear web": (0, -1)}[f["face"]]
                csec, bc = self.ch.sections[m.sec.cell], m.sec.cell_b
                off = -m.sec.b / 2 + bc / 2 + k * bc
                tc = Tube(f"{m.id}.{k + 1}", np.add(m.p0, off * t.ey), np.add(m.p1, off * t.ey), csec, m.depth_dir)
                inner = (k == 0) == (web > 0)
                out.append(dict(row, tube=tc.name, web=web, centre=tc.point(u, web * csec.b / 2, z_l), normal=web * tc.ey,
                                web_id=f"{tc.name} web {web}",
                                y_web=abs(off) - csec.b / 2 + csec.t / 2 if inner else abs(off) + csec.b / 2 - csec.t / 2))
                continue
            web = 1 if float(np.dot(c - t.p0, t.ey)) > 0 else -1
            out.append(dict(row, web=web, centre=t.point(u, web * m.sec.b / 2, z_l), normal=web * t.ey))
        return out

    def _member_hole_sites(self, rules, bolts=()) -> list[dict]:
        """The holes for galvanising CHS-11 asks of the frame's other closed sections (cad/chassis_dip.py, I2-84), each in
        its member's own web: its net section, its edge distance to the web's flat and to the member's end, and its clear
        distance to the end weld's toe, to fillets along the member's bottom edges, to the fittings welded on it, to the
        hinge gussets' end welds on a hinge crossmember's face and to the member's other holes, in the web's own plane (u
        along the member, z across it). A hole in a rail's inner web inside a crossmember's end is read with the rails'
        holes (hole_sites). The drawbar members' apex drains are H-33 to H-36 already. The hinge gussets are members of
        the frame model, so their holes are read on their net sections as the members' are. `bolts`, the fixings' bolt
        holes in the crossmembers' webs (_fixing_member_holes), are read the same way, after the dip's holes."""
        from .chassis import fitting_boxes
        from .chassis_dip import frame_sections
        ch, V = self.ch, self.ch.V
        mem = {m.id: m for m in ch.members}
        gr = ch.data["member_galvanising_holes"]
        _, holes = frame_sections(ch)
        attach = {"CM-08": ["CH-P05"]}                       # the shock plates on each crossmember they stand on (I2-107)
        for p in ch.shock_plates():
            attach.setdefault(p["member"], [])
            if "CH-P07" not in attach[p["member"]]:
                attach[p["member"]].append("CH-P07")
        boxes = {fid: [b for f in ch.fittings if f.id == fid for b in fitting_boxes(ch, f)] for fids in attach.values() for fid in fids}
        feet: dict[str, list] = {}                        # each hinge gusset's end weld on its crossmember's face, to its toe
        gsec = ch.sections[next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
        g_leg = ch.data["xt_hinges"]["gusset"]["weld"]["leg"]
        for g in ch.hinge_gussets():
            (fx, ya), (_, yb) = g["outline"][:2]
            feet.setdefault(g["cm"], []).append((g["id"], (fx - g_leg, min(ya, yb) - g_leg, g["z"] - gsec.d / 2 - g_leg,
                                                           fx + g_leg, max(ya, yb) + g_leg, g["z"] + gsec.d / 2 + g_leg)))
        own = [h for h in holes if h["via"] == "own" and not (h["tube"].endswith("A") and h["tube"].startswith("DB-") and h["use"] == "drain")]
        own += list(bolts)
        run_nodes, span_nodes = self._run_nodes(own)
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
                toes.append(((z - d / 2) - (-sec.d / 2 + r["z_bottom_leg"]), "XT hinges' fillets"))
            cen = np.array(h["centre"], float)
            hb = (cen[0] - d / 2, cen[1] - d / 2, cen[2] - d / 2, cen[0] + d / 2, cen[1] + d / 2, cen[2] + d / 2)
            for fid in attach.get(h["member"], []):
                for bx in boxes[fid]:
                    gb = (bx[0] - 6, bx[1] - 6, bx[2] - 6, bx[3] + 6, bx[4] + 6, bx[5] + 6)
                    toes.append((_box_gap(hb, gb), f"{fid}'s fillets"))
            for gid, gb in feet.get(h["member"], []):
                toes.append((_box_gap(hb, gb), f"{gid}'s end weld"))
            for o in own:
                if o is not h and o["tube"] == h["tube"] and o["web"] == h["web"]:
                    g = math.hypot(o["u"] - h["u"], o["z_l"] - z) - (o["d"] + d) / 2
                    toes.append((g - (max(o["d"], d) - d), f"hole for {o['use']}"))
            gap, weld = min(toes, key=lambda t: t[0])
            names = {el.member for el in self.f.elements}
            frame = h["tube"] if h["tube"] in names else (m.id if m and m.id in names else None)
            gross = dict(A=sec.A, z=0.0, I=sec.I_strong, I_weak=sec.I_weak, Aw=sec.Aw_depth, Aw_width=sec.Aw_width)
            strips = [dict(dA=sec.t * d, z=z, own=sec.t * d ** 3 / 12, y=h.get("y_web", (sec.b - sec.t) / 2), own_z=d * sec.t ** 3 / 12, web=True)]
            levers, face_w = [z - d / 2, z + d / 2], sec.d - sec.t
            word = {"drawbar": "the drawbar member's", "cm_end": "the crossmember's", "cm_floor": "the crossmember's",
                    "cm_xt": "the XT crossmember's", "outrigger": "the outrigger's", "brace": "the cross brace's",
                    "plan_brace": "the plan brace's", "hinge_gusset": "the hinge gusset's"}[role]
            out.append(dict(member=h["member"], face=f"{h['use']}", run=h["use"], x=float(cen[0]), y=float(cen[1]), z=float(cen[2]), d=d,
                            length=d, runs=[h["use"]], rows=[f"{h['member']} {h['use']}"], frame=frame, wall=f"{word} web",
                            open=False, fu=rules["fu"]["raiser" if sec.fy < 400 else "rail"], fy=sec.fy, box=hb, edge_mm=edge, edge_need=edge_need,
                            toe_mm=gap, toe_need=rules["toe_factor"] * d, toe_weld=weld, galv=True, placement_only=frame is None,
                            u_web=u_end, z_under=float(h.get("z_under", z + sec.d / 2)), run_node=run_nodes.get(id(h)),
                            span_nodes=span_nodes.get(id(h)),
                            own=self.fm.hinge_bar == "elastic" and (id(h) in run_nodes or id(h) in span_nodes),
                            gross=gross, strips=strips, levers=levers, face_w=face_w, wall_id=h.get("web_id", f"{h['member']} web {h['web']}"),
                            net=dict(net_section(gross, strips, levers, sec.b / 2, face_w, d),
                                     base=dict(Z_weak=sec.Z_weak, I_weak=sec.I_weak, C=sec.C, y_max=sec.b / 2))))
        return out

    def _run_nodes(self, holes: list[dict]) -> tuple[dict[int, int], dict[int, list]]:
        """Where each hole in a hinge crossmember is read against the hinge bar's weld runs (I2-112, I2-109). The frame model
        lumps each run at its centre and ties the runs' nodes together through the rigid hinge bar, so between the
        outermost and the innermost run's nodes the crossmember carries next to nothing. A hole within the outermost run's
        length, its centre either side of that node, is read on the element outboard of the node, which carries the
        runs' share of the hinge's force into the rail, on the safe side: the first dict, the node. Any other hole that
        reaches into the runs' span, from the innermost run's inner end out, is read at both ends of the span, on the
        element outboard of the outermost run's node and on the element inboard of the innermost run's node, which
        carries the force across the crossmember, the worse of the two: the second dict, each (node, outboard)."""
        ch = self.ch
        run = ch.data["xt_hinges"]["bar"]["run"]
        outer, span = {}, {}
        for cm in ch.hinge_crossmembers():
            ys = ch.hinge_weld_ys(cm)
            for h in holes:
                if h["member"] != cm.id:
                    continue
                y, r = float(h["centre"][1]), h["d"] / 2
                side = sorted((yr for yr in ys if yr * y > 0), key=abs)
                if not side:
                    continue
                y_in, y_out = side[0], side[-1]
                if abs(y - y_out) < run / 2 + r:
                    outer[id(h)] = self.fm.cm_node(cm.id, y_out)
                elif abs(y) + r > abs(y_in) - run / 2 and abs(y) - r < abs(y_out) + run / 2:
                    span[id(h)] = [(self.fm.cm_node(cm.id, y_out), True), (self.fm.cm_node(cm.id, y_in), False)]
        return outer, span

    def hole_stress(self, res, h) -> dict:
        """Normal and combined stress at a hole's edge on the composite rail's net section, at the element end nearest it.
        A hole for galvanising is read on the element whose span holds it, at that element's end nearer the hole, so a
        load that enters the member between the hole and the next node (a hinge's welds) is counted where it passes. A hole
        within the outermost of a hinge bar's weld runs is read on the element outboard of that run's node, at that node,
        whichever side of it the hole's centre falls (I2-112), and any other hole in the runs' span at both of the span's
        ends, the worse (_run_nodes). On the elastic hinge bar, whose crossmember carries its share between the runs, each
        of those holes is also read on the element whose span holds it, the worse (`own`, I2-114)."""
        if h.get("own"):
            return max(self.hole_stress(res, dict(h, own=False, run_node=None, span_nodes=None)), self.hole_stress(res, dict(h, own=False)),
                       key=lambda r: r["eq"])
        if h.get("span_nodes"):
            return max((self.hole_stress(res, dict(h, span_nodes=None, run_node=nd, inboard=not outward))
                        for nd, outward in h["span_nodes"]), key=lambda r: r["eq"])
        best, bd = None, math.inf
        p = np.asarray((h["x"], h["y"], h["z"]), float)
        nd0 = h.get("run_node")
        if nd0 is not None:
            for el, fl in zip(self.f.elements, res.forces):
                if el.member == h["frame"] and nd0 in (el.i, el.j):
                    far = el.j if el.i == nd0 else el.i
                    if (abs(self.f.nodes[far][1]) > abs(self.f.nodes[nd0][1])) != bool(h.get("inboard")):
                        best, bd = end_actions(fl)[0 if el.i == nd0 else 1], 0.0
        for span in (() if best is not None else (True, False) if h.get("galv") else (False,)):
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
            row = {key: h[key] for key in ("id", "member", "face", "x", "y", "z", "d", "length", "runs", "wall", "open", "u_web", "z_under", "with") if key in h}
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
    def local_checks(self, jack: dict) -> dict:
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
        # the jacking points, LC8b: Cruisemaster's, under each arm by its hub (its XT user guide), the air released from
        # the springs first, so the jack's push reaches the frame through the arm's bump stop on its airbag's top bracket,
        # welded along the rail's inner web, and the little left through its hinge. The bump stop's push at the frame
        # analysis's jack force is scaled to the larger of that and LC8b's force, and read on the bracket's fillets along
        # the rail's web, the bracket's length and its returns, and on the web in shear along them
        rail = ch.role_sec["rail"]
        ab = ch.data["xt_arms"]["airbag"]["bracket"]
        F = max(jack["pad_n"], lcs["LC8b"]["pad_n"])
        Fb = max(jack["bag_n"] * F / jack["jack_at"], jack["bag_at"] * F / jack["pad_n"])
        lw = ab["l"] + 2 * ab["returns"]
        rows = [("airbag's top bracket fillets under the bump stop's push", Fb / (lw * 0.7 * ab["leg"]), wcap),
                ("rail's web in shear along the bracket's fillets", Fb / (rail.t * lw), 0.6 * rail.fy)]
        out["jacking_point"] = _local("Jacking point under each XT arm, Cruisemaster's", rows,
                                      f"{F / 1000:.1f} kN at one arm's jacking point by its hub (the larger of LC8b's {lcs['LC8b']['pad_n'] / 1000:.1f} kN "
                                      f"at the plate and the frame analysis), {Fb / 1000:.1f} kN of it through the arm's bump stop onto its airbag's top bracket")
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


def _reaction_key(R: dict) -> tuple:
    """LC8a's reaction as the frame takes it, to the mN: two reactions with one key load the frame alike."""
    parts = [R["pull"], R["nose"]] + [R["contact"][k] for k in sorted(R["contact"])] + [R["hub"][k] for k in sorted(R["hub"])]
    return tuple(sorted(R["hub"])) + tuple(np.round(np.concatenate([np.asarray(x, float) for x in parts]), 3).tolist())


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


def plate_shear_buckling(x0: float, x1: float, y0: float, y1: float, t: float, holds, deg: int = 28, E: float = 200_000.0,
                         holes=()) -> float:
    """The least uniform shear stress (MPa) at which a flat plate x0 to x1 by y0 to y1 and t thick buckles, held out of its
    plane only at the points `holds` (x, y) and free elsewhere (I2-98), by the Rayleigh-Ritz method on a Legendre basis
    to `deg` in each direction, each point a stiff spring. The shear is taken uniform over the whole plate, its free edges
    too, which overstates what reaches them (est., on the safe side). Held along every edge it gives the closed form's
    k = 5.35 + 4 (a / b) squared within 1 % (cad/tests/test_chassis.py). `holes` are rectangles (x0, y0, x1, y1) cut out
    of the plate: its strain energy and the shear's work are then taken over what is left, on the quadrature's points
    outside them (fx22-rear)."""
    from numpy.polynomial import legendre as leg
    a, b = x1 - x0, y1 - y0
    D = E * t ** 3 / (12 * (1 - NU ** 2))
    g, wq = leg.leggauss(2 * deg + 4)
    n = deg + 1
    eye = np.eye(n)
    P = np.array([leg.legval(g, eye[i]) for i in range(n)])
    dP = np.array([leg.legval(g, leg.legder(eye[i])) for i in range(n)])
    d2P = np.array([leg.legval(g, leg.legder(eye[i], 2)) for i in range(n)])
    sx, sy, jac = 2 / a, 2 / b, a * b / 4

    def integral(A, B):
        return (A * wq) @ B.T

    if holes:
        xs, ys = x0 + (g + 1) * a / 2, y0 + (g + 1) * b / 2
        keep = np.ones((len(g), len(g)))
        for hx0, hy0, hx1, hy1 in holes:
            keep[np.ix_((xs > hx0) & (xs < hx1), (ys > hy0) & (ys < hy1))] = 0.0
        w2 = (np.outer(wq, wq) * keep).ravel()

        def basis(A, B):                 # each basis function A_i(xi) B_j(eta) at every point, (points, n * n)
            return np.einsum("ip,jq->pqij", A, B).reshape(len(g) ** 2, n * n)

        def integral2(U, W):
            return (U * w2[:, None]).T @ W

        Bxx, Byy, Bxy, Bx, By = basis(d2P, P), basis(P, d2P), basis(dP, dP), basis(dP, P), basis(P, dP)
        K = D * jac * (sx ** 4 * integral2(Bxx, Bxx) + sy ** 4 * integral2(Byy, Byy)
                       + NU * sx ** 2 * sy ** 2 * (integral2(Bxx, Byy) + integral2(Byy, Bxx))
                       + 2 * (1 - NU) * sx ** 2 * sy ** 2 * integral2(Bxy, Bxy))
        G = t * jac * sx * sy * (integral2(Bx, By) + integral2(By, Bx))
    else:
        X00, X11, X22, X02, X01 = integral(P, P), integral(dP, dP), integral(d2P, d2P), integral(P, d2P), integral(P, dP)
        K = D * jac * (sx ** 4 * np.kron(X22, X00) + sy ** 4 * np.kron(X00, X22) + NU * sx ** 2 * sy ** 2 * (np.kron(X02.T, X02) + np.kron(X02, X02.T))
                       + 2 * (1 - NU) * sx ** 2 * sy ** 2 * np.kron(X11, X11))
        G = t * jac * sx * sy * (np.kron(X01.T, X01) + np.kron(X01, X01.T))
    k = 1e4 * float(np.max(np.diag(K)))
    for px, py in holds:
        v = np.kron(leg.legval(2 * (px - x0) / a - 1, eye), leg.legval(2 * (py - y0) / b - 1, eye))
        K = K + k * np.outer(v, v)
    mu = np.linalg.eigvals(np.linalg.solve(K, G))
    mu = mu[np.abs(mu.imag) <= 1e-9 * np.max(np.abs(mu))].real
    return float(1.0 / np.max(np.abs(mu)))


RECOVERY_LINES = {"low": (-1, 0), "up": (0, 1), "any": (-1, 0, 1)}       # a class's lines, in LC8a's vertical_deg
RECOVERY_WHEELS = {"free": ("free",), "unseen": ("free", "wheel", "axle")}   # a wheel not seen free counts as held


def recovery_class_cells(tipping: dict, lc8: dict, c: dict) -> list[dict]:
    """The tipping table's least entries (Analysis.tipping_pulls) a recovery class covers: its point, both sides, the
    wheel states it allows and its lines."""
    vd = lc8["vertical_deg"]
    return [x for x in tipping["least"] if x["where"] == c["at"] and x["wheels"] in RECOVERY_WHEELS[c["wheels"]]
            and x["v"] in [k * vd for k in RECOVERY_LINES[c["line"]]]]


def recovery_rule(results: dict, lc8: dict) -> dict:
    """The user's recovery rule (I2-93, I2-100, I2-114, I2-119, I2-127), from LC8a's data and the frame analysis: the pull
    each point is rated for, the directions it may be pulled in, the fail checks' limits with every wheel free, one wheel
    held and both wheels of one axle held fast (`free_n`, `held_wheel_n`, `held_axle_n`), and the user's classes (LC8a
    `classes`), each its limit from the data with the two figures it is the lesser of: the fail checks' limit for the
    wheel states it allows, and LC8a `tip` `margin` of the least pull that tips the trailer in it (tipping_pulls), rounded
    down to 5 kN, with which of them governs. With them the least pull that slides the trailer sideways with every wheel
    free, in kN, and whether any level pull tips it within the reach."""
    tp = results["tipping"]
    margin = lc8["tip"]["margin"]
    rule = {"free": lc8.get("free_n", lc8["force_n"]), "wheel": lc8["held_wheel_n"], "axle": lc8["held_axle_n"]}
    classes = []
    for c in lc8["classes"]:
        cells = recovery_class_cells(tp, lc8, c)
        tip = min((x["tip"] for x in cells if x["tip"]), key=lambda t: t["kn"], default=None)
        rule_n = min(rule[k] for k in RECOVERY_WHEELS[c["wheels"]])
        by_tip = None if tip is None else 5000.0 * math.floor(margin * tip["kn"] / 5.0 + 1e-9)
        lesser = rule_n if by_tip is None else min(rule_n, by_tip)
        governs = "fail checks" if by_tip is None or rule_n < by_tip else ("tipping" if by_tip < rule_n else "both")
        classes.append(dict(id=c["id"], name=c["name"], at=c["at"], wheels=c["wheels"], line=c["line"], limit_kn=c["limit_n"] / 1000,
                            rule_kn=rule_n / 1000, tip=tip, share_kn=None if tip is None else margin * tip["kn"],
                            by_tip_kn=None if by_tip is None else by_tip / 1000, lesser_kn=lesser / 1000, governs=governs,
                            cells=len(cells)))
    free = [x for x in tp["least"] if x["wheels"] == "free" and x["where"] != "coupling"]
    slide = min((x["slide"] for x in free if x["slide"]), key=lambda t: t["kn"], default=None)
    return dict(rated_kn=lc8["force_n"] / 1000, free_kn=rule["free"] / 1000, held_wheel_kn=rule["wheel"] / 1000,
                held_axle_kn=rule["axle"] / 1000, sideways_deg=lc8["sideways_deg"], vertical_deg=lc8["vertical_deg"],
                coupling=bool(lc8.get("coupling")), margin=margin, reach_kn=tp["reach_kn"], classes=classes, slide=slide,
                mu_hi=max(lc8["reaction"]["mu"]), level_tips=any(x["tip"] for x in tp["least"] if x["v"] == 0))


def net_section(gross: dict, strips: list[dict], levers, y_lever: float, face_w: float, d_wall: float) -> dict:
    """A member's net section with strips of wall taken out for its holes: `gross` the whole section's area, centroid
    height, second moments and shear areas, each strip its area, height, own second moments and offset across, in a web
    or a face. The lever runs from the net centroid to the farthest of `levers`, and the wall's torsion factor is its
    width over its width less `d_wall`, the holes in it."""
    A = gross["A"] - sum(p["dA"] for p in strips)
    zc = (gross["A"] * gross["z"] - sum(p["dA"] * p["z"] for p in strips)) / A
    I = gross["I"] + gross["A"] * (zc - gross["z"]) ** 2 - sum(p["own"] + p["dA"] * (p["z"] - zc) ** 2 for p in strips)
    Iw = gross["I_weak"] - sum(p["own_z"] + p["dA"] * p["y"] ** 2 for p in strips)
    return dict(A=A, I=I, I_weak=Iw, Aw=gross["Aw"] - sum(p["dA"] for p in strips if p["web"]),
                Aw_width=gross["Aw_width"] - sum(p["dA"] for p in strips if not p["web"]),
                z_lever=max(abs(z - zc) for z in levers), y_lever=y_lever, k_torsion=face_w / max(face_w - d_wall, 1.0))


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


def sn_range(fat: float, m: float, knee: float, n: float) -> float:
    """The stress range IIW-1823-07's curve for FAT allows for n cycles, MPa: slope m from 2 million cycles down to the
    knee at `knee` cycles, then slope 22 (Table 4.3-2), so at n = knee it is the CAFL."""
    if n <= knee:
        return fat * (2e6 / n) ** (1 / m)
    return fat * (2e6 / knee) ** (1 / m) * (knee / n) ** (1 / 22)


def root_damage(sigma: float, tau: float, fat: float, fat_shear: float, n: float) -> float:
    """The Miner damage that n cycles of a weld throat's normal range sigma and shear range tau, in phase, use up by
    IIW's interaction (IIW-1823-07 4.3.1, Table 4.3-1, CV 1.0): the D at which (sigma / the normal range FAT allows for
    n / D cycles)^2 + (tau / the shear range FAT_shear allows for n / D)^2 reaches 1 (sn_range, the normal curve's
    slope 3 to its knee at 10^7 cycles and the shear curve's slope 5 to 10^8). Within the two CAFLs by the same
    interaction it is none, as _miner takes a range under its CAFL, so with no shear it is _miner's damage."""
    if math.hypot(sigma / sn_range(fat, 3, 1e7, 1e7), tau / sn_range(fat_shear, 5, 1e8, 1e8)) <= 1:
        return 0.0

    def over(d):
        return (sigma / sn_range(fat, 3, 1e7, n / d)) ** 2 + (tau / sn_range(fat_shear, 5, 1e8, n / d)) ** 2 > 1
    lo, hi = -30.0, 30.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if over(10 ** mid) else (lo, mid)
    return 10 ** hi


def weld_group(lines: list[tuple[str, tuple, tuple, float]]) -> dict:
    """A weld group for the elastic vector method in three dimensions (CHS-14, CHS-18): each line (name, p0, p1, throat)
    a straight weld from p0 to p1 on its throat. Its throat area A, its centroid c and the inverse of its polar tensor
    about c, the sum over the lines of a (|r|^2 1 - r r^T) at each line's centre and a L^2 / 12 (1 - e e^T) along it."""
    P0 = np.array([ln[1] for ln in lines], float)
    P1 = np.array([ln[2] for ln in lines], float)
    d = P1 - P0
    L = np.linalg.norm(d, axis=1)
    a = np.array([ln[3] for ln in lines], float) * L
    m = (P0 + P1) / 2
    A = float(a.sum())
    c = (a[:, None] * m).sum(axis=0) / A
    eye = np.eye(3)
    I = np.zeros((3, 3))
    for ak, mk, dk, Lk in zip(a, m, d, L):
        r, e = mk - c, dk / Lk
        I += ak * (r @ r * eye - np.outer(r, r)) + ak * Lk ** 2 / 12 * (eye - np.outer(e, e))
    return dict(names=[ln[0] for ln in lines], P0=P0, P1=P1, a=a, m=m, e=d / L[:, None], L=L, A=A, c=c, Iinv=np.linalg.inv(I))


def _cross(v) -> np.ndarray:
    """The matrix [v]x, so that [v]x @ u is v x u."""
    return np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])


def group_stress(g: dict, F, at, M=None, worst: bool = True) -> dict:
    """The largest throat stress along each line of weld group g under the force F (N) at the point `at` and the moment M
    about it, by the elastic vector method: at each point F / A and theta x r, theta = I^-1 Mc with Mc the moment about
    the centroid, at each line's two ends. `worst` adds each force component's direct and turning parts at their worst
    whatever their signs, as CHS-14 reads the cheeks, and leaves M out; otherwise the signed vectors."""
    F = np.asarray(F, float)
    d = np.asarray(at, float) - g["c"]
    out: dict[str, float] = {}
    if worst:
        Fa, D = np.abs(F), g["Iinv"] @ _cross(d)
        for k, name in enumerate(g["names"]):
            s = max(float(np.linalg.norm(Fa / g["A"] + np.abs(_cross(p - g["c"]) @ D) @ Fa)) for p in (g["P0"][k], g["P1"][k]))
            out[name] = max(out.get(name, 0.0), s)
        return out
    th = g["Iinv"] @ ((np.zeros(3) if M is None else np.asarray(M, float)) + np.cross(d, F))
    for k, name in enumerate(g["names"]):
        s = max(float(np.linalg.norm(F / g["A"] + np.cross(th, p - g["c"]))) for p in (g["P0"][k], g["P1"][k]))
        out[name] = max(out.get(name, 0.0), s)
    return out


def group_throat(g: dict, F, M) -> list[tuple[str, float, float]]:
    """Each line of weld group g at its two ends under the force F at the group's centroid and the moment M about it, by
    the elastic vector method as group_stress reads it with its signs (FAT-26): the throat stress's part along the line,
    tau_w, and the rest, normal to the line's axis, sigma_w, the resultant of sigma and tau across it (IIW-1823-07
    2.2.2.2, the stress in a weld's throat), as (name, sigma_w, tau_w) in MPa."""
    F = np.asarray(F, float)
    th = g["Iinv"] @ np.asarray(M, float)
    out = []
    for k, name in enumerate(g["names"]):
        e = g["e"][k]
        for p in (g["P0"][k], g["P1"][k]):
            s = F / g["A"] + np.cross(th, p - g["c"])
            t = float(s @ e)
            out.append((name, float(np.linalg.norm(s - t * e)), abs(t)))
    return out


def group_share(g: dict, F, at, lines: list[int], q) -> tuple[np.ndarray, np.ndarray]:
    """The force and its moment about q that the lines `lines` of weld group g carry under the force F at `at`, signed,
    by the elastic vector method: each line's a (F / A + theta x (m - c)) at its centre m, and its own a L^2 / 12
    (theta - e (e . theta)) along it."""
    F = np.asarray(F, float)
    th = g["Iinv"] @ np.cross(np.asarray(at, float) - g["c"], F)
    Fs, Ms = np.zeros(3), np.zeros(3)
    for k in lines:
        f = g["a"][k] * (F / g["A"] + np.cross(th, g["m"][k] - g["c"]))
        e = g["e"][k]
        Fs += f
        Ms += np.cross(g["m"][k] - np.asarray(q, float), f) + g["a"][k] * g["L"][k] ** 2 / 12 * (th - e * (e @ th))
    return Fs, Ms


def rect_torsion(T: float, a: float, b: float) -> float:
    """The largest shear stress from torque T in a solid rectangle a by b (Roark, Table 10.7): 3 T / (8 a' b'^2) times
    (1 + 0.6095 r + 0.8865 r^2 - 1.8023 r^3 + 0.9100 r^4), a' and b' the half sides, a' >= b', r = b' / a'."""
    a, b = max(a, b) / 2, min(a, b) / 2
    r = b / a
    return 3 * abs(T) / (8 * a * b ** 2) * (1 + 0.6095 * r + 0.8865 * r ** 2 - 1.8023 * r ** 3 + 0.9100 * r ** 4)


def _local(name, rows, load) -> dict:
    parts = [dict(part=p, mpa=s, limit_mpa=l, util=s / l) for p, s, l in rows]
    g = max(parts, key=lambda r: r["util"])
    return dict(name=name, load=load, parts=parts, util=g["util"], governing=g["part"], mpa=g["mpa"], limit_mpa=g["limit_mpa"])

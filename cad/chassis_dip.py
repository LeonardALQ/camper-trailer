"""The frame's closed sections in the galvanising dip (CHS-11, I2-84).

Every closed section of the welded frame is read from its members' axes, rolled and pitched as galvanising_dip gives the
hang (data/chassis/chassis.yaml), in both rolls and across the pitch range. Each section's inside is sliced along its
axis, each slice the tube's inner section with its corner radii, and its lowest and highest inside points found in each
hang. Liquid leaves a section only through a drain, the rails' slot under their end plates, an internal hole into the
member a section is welded to, or an open end, so the liquid it keeps is what lies below the lowest edge of every
opening it can reach, and the air it keeps on immersion is what lies above the top edge of every opening it can reach.
Each low point must reach an opening whose lowest edge stands at most max_depth over it, and each high point one whose
top edge stands at most max_depth under it. Each hole is at least the guide's least 10 mm and its wall's thickness
(pages 8 and 13), and the openings at each otherwise closed end give at least the area of the one hole Tables 1 to 3
give that section, the guide's equal area for several holes (page 13).

The model leaves out the galvaniser's chains, the swing as the frame goes in and comes out, the bush in a cable's
hole, which is taken as closed, and the snipe's taper at a drawbar member's rear end, which it reads as the tube at full
depth to its open end. The galvaniser's trial hang and the inspection of every hole before dipping replace it.
"""
from __future__ import annotations

import math

import numpy as np

from .chassis import Chassis, Member

ZINC_KG_PER_L = 6.6       # molten zinc
TABLES = {                # the guide's Tables 1 to 3, one hole's diameter for each otherwise closed end
    "RHS_150x50x3": 40, "RHS_150x50x4": 40, "RHS_150x50x6": 40, "RHS_75x50x3": 25, "SHS_40x40x2p5": 14,
    "SHS_50x50x3": 18, "SHS_50x50x2p5": 18,
}


def one_hole_d(sec) -> float:
    """Tables 1 to 3's one hole for the section, or a quarter of its diagonal, rounded up, where the tables omit it."""
    return TABLES.get(sec.id) or math.ceil(0.25 * math.hypot(sec.d, sec.b))


def up_vector(roll: float, pitch: float, kerb_down: bool) -> np.ndarray:
    """The upward unit vector in the frame's axes, rolled `roll` degrees about X with that side down and pitched
    `pitch` degrees drawbar end down."""
    phi, th = math.radians(roll), math.radians(pitch)
    s = 1.0 if kerb_down else -1.0
    return np.array([math.sin(th), s * math.sin(phi) * math.cos(th), math.cos(phi) * math.cos(th)])


def axes(p0, p1, depth_dir=(0.0, 0.0, 1.0)):
    """A tube's unit vectors: along its axis, across its width (the webs' normal) and along its depth."""
    ex = np.subtract(p1, p0, dtype=float)
    ex /= np.linalg.norm(ex)
    ez = np.array(depth_dir, float) - ex * np.dot(depth_dir, ex)
    ez /= np.linalg.norm(ez)
    return ex, np.cross(ez, ex), ez


class Tube:
    """One straight piece of a closed section: its axis, section, inner cells and slices."""

    def __init__(self, name, p0, p1, sec, depth_dir=(0.0, 0.0, 1.0), ds=5.0, cell=2.0):
        self.name, self.sec = name, sec
        self.p0, self.p1 = np.array(p0, float), np.array(p1, float)
        self.ex, self.ey, self.ez = axes(p0, p1, depth_dir)
        self.L = float(np.linalg.norm(self.p1 - self.p0))
        n = max(2, int(math.ceil(self.L / ds)))
        self.u = np.linspace(0.0, self.L, n + 1)
        self.ds = self.L / n
        self.hy, self.hz, self.ri = sec.b / 2 - sec.t, sec.d / 2 - sec.t, max(sec.ro - sec.t, 0.0)
        ys = np.arange(-self.hy + cell / 2, self.hy, cell)
        zs = np.arange(-self.hz + cell / 2, self.hz, cell)
        Y, Z = np.meshgrid(ys, zs)
        cy, cz = np.clip(np.abs(Y) - (self.hy - self.ri), 0, None), np.clip(np.abs(Z) - (self.hz - self.ri), 0, None)
        keep = cy ** 2 + cz ** 2 <= self.ri ** 2 + 1e-9
        self.cy, self.cz, self.cell_a = Y[keep], Z[keep], cell * cell

    def heights(self, up):
        """Each slice's axis height, its inside's lowest and highest points, and its cells' heights about the axis."""
        a, c = float(np.dot(up, self.ey)), float(np.dot(up, self.ez))
        ext = (self.hy - self.ri) * abs(a) + (self.hz - self.ri) * abs(c) + self.ri * math.hypot(a, c)
        h = float(np.dot(up, self.p0)) + self.u * float(np.dot(up, self.ex))
        rel = np.sort(self.cy * a + self.cz * c)
        return h, h - ext, h + ext, rel

    def point(self, u, y=0.0, z=0.0):
        return self.p0 + u * self.ex + y * self.ey + z * self.ez


class Section:
    """A closed section: one tube or tubes joined end to end through open mitres, its two ends open or closed, and
    the openings on it, each at a slice."""

    def __init__(self, sid, name, tubes, ends):
        self.id, self.name, self.tubes, self.ends = sid, name, tubes, ends      # ends: ("open" | "closed", ...)
        self.openings: list[dict] = []
        self.offset = []
        k = 0
        for t in tubes:
            self.offset.append(k)
            k += len(t.u)
        self.n = k

    def add_hole(self, tube: int, u: float, centre, normal, d: float, use: str, end=None, wall_t=None, label=""):
        self.openings.append(dict(kind="hole", tube=tube, u=u, centre=np.array(centre, float), normal=np.array(normal, float),
                                  d=float(d), use=use, end=end, wall_t=wall_t, label=label))

    def add_slot(self, end: int, height: float, width: float, label=""):
        """A slot over the floor at an end: the floor itself to `height` over it, across `width`."""
        self.openings.append(dict(kind="slot", end=end, height=height, width=width, use="drain", label=label))

    def slice_of(self, tube: int, u: float) -> int:
        t = self.tubes[tube]
        return self.offset[tube] + int(np.argmin(np.abs(t.u - u)))

    def read(self, up, max_depth: float) -> dict:
        """The section in one hang: its low and high points, the depth of each under or over the opening it reaches,
        and the liquid and air it keeps."""
        hs, lo, hi, rel, ds = [], [], [], [], []
        for t in self.tubes:
            h, f, c, r = t.heights(up)
            hs.append(h), lo.append(f), hi.append(c), rel.append(r), ds.append(t.ds)
        f, c = np.concatenate(lo), np.concatenate(hi)
        o_low, o_high = np.full(self.n, np.inf), np.full(self.n, -np.inf)
        ends_ix = (0, self.n - 1)
        for e, kind in enumerate(self.ends):
            if kind == "open":
                o_low[ends_ix[e]], o_high[ends_ix[e]] = f[ends_ix[e]], c[ends_ix[e]]
        for o in self.openings:
            if o["kind"] == "slot":
                i = ends_ix[o["end"]]
                t = self.tubes[0 if o["end"] == 0 else -1]
                a, cz = abs(float(np.dot(up, t.ey))), float(np.dot(up, t.ez))
                top = (hs[0][0] if o["end"] == 0 else hs[-1][-1]) + a * t.hy + max(-cz * t.hz, cz * (-t.hz + o["height"]))
                o_low[i], o_high[i] = min(o_low[i], f[i]), max(o_high[i], top)
                continue
            i = self.slice_of(o["tube"], o["u"])
            hc = float(np.dot(up, o["centre"]))
            m = math.sqrt(max(0.0, 1.0 - float(np.dot(up, o["normal"])) ** 2))
            o_low[i], o_high[i] = min(o_low[i], hc - o["d"] / 2 * m), max(o_high[i], hc + o["d"] / 2 * m)
        level = _levels(f, o_low)
        air = -_levels(-c, -o_high)
        area = np.zeros(self.n)
        airea = np.zeros(self.n)
        dsl = np.zeros(self.n)
        for k, t in enumerate(self.tubes):
            sl = slice(self.offset[k], self.offset[k] + len(t.u))
            r = rel[k]
            hk = hs[k]
            lv, av = level[sl], air[sl]
            area[sl] = np.where(np.isfinite(lv), np.searchsorted(r, np.where(np.isfinite(lv), lv - hk, 0.0)), len(r)) * t.cell_a
            airea[sl] = np.where(np.isfinite(av), len(r) - np.searchsorted(r, np.where(np.isfinite(av), av - hk, 0.0)), len(r)) * t.cell_a
            dsl[sl] = t.ds
        lows = [(i, level[i] - f[i]) for i in _extrema(f, -1)]
        highs = [(i, c[i] - air[i]) for i in _extrema(c, 1)]
        held, kept = float(np.sum(area * dsl)) / 1e6, float(np.sum(airea * dsl)) / 1e6
        worst_low = max(lows, key=lambda t: t[1])
        worst_high = max(highs, key=lambda t: t[1])
        return dict(low_depth=float(worst_low[1]), low_at=self._where(worst_low[0]), high_depth=float(worst_high[1]),
                    high_at=self._where(worst_high[0]), liquid_l=held, air_l=kept, lows=len(lows), highs=len(highs),
                    ok=worst_low[1] <= max_depth + 1e-9 and worst_high[1] <= max_depth + 1e-9)

    def _where(self, i: int) -> dict:
        k = max(j for j, o in enumerate(self.offset) if o <= i)
        t = self.tubes[k]
        p = t.point(float(t.u[i - self.offset[k]]))
        return dict(tube=t.name, x=float(p[0]), y=float(p[1]), z=float(p[2]))


def _levels(f: np.ndarray, o: np.ndarray) -> np.ndarray:
    """The level liquid settles at in each slice: the lowest opening edge it can reach along the section without
    climbing over a floor higher than that edge (each slice's floor f, the lowest opening edge o in it)."""
    n = len(f)
    g, h = np.empty(n), np.empty(n)
    run = np.inf
    for i in range(n):
        run = max(f[i], min(o[i], run))
        g[i] = run
    run = np.inf
    for i in range(n - 1, -1, -1):
        run = max(f[i], min(o[i], run))
        h[i] = run
    return np.minimum(g, h)


def _extrema(v: np.ndarray, sign: int) -> list[int]:
    """The section's low points (sign -1) or high points (sign +1): each slice no lower (higher) than its neighbours,
    a run of equal slices taken once."""
    w = sign * v
    out = []
    n = len(w)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(w[j + 1] - w[i]) < 1e-9:
            j += 1
        left = w[i - 1] if i > 0 else -np.inf
        right = w[j + 1] if j + 1 < n else -np.inf
        if w[i] >= left - 1e-9 and w[i] >= right - 1e-9:
            out.append((i + j) // 2)
        i = j + 1
    return out


# ------------------------------------------------------------------ the holes for galvanising, by the hole rules
def _web_hole(t: Tube, member: str, end: int, web: int, z_l: float, d: float, u_end: float, use: str, offset: float = 0.0) -> dict:
    """A hole in one of a tube's webs, `u_end` along the web from the end it serves, that web's end standing `offset` along
    the axis from the axis's end (a mitre's line on that web). `u_web` and `z_under`, its height over the tube's
    underside, are the figures the drawings dimension (I2-89)."""
    u = u_end + offset if end == 0 else t.L - u_end - offset
    return dict(member=member, tube=t.name, tube_L=t.L, end=end, web=web, u=u, z_l=z_l, d=d, use=use, via="own",
                u_web=u_end, z_under=z_l + t.sec.d / 2, centre=t.point(u, web * t.sec.b / 2, z_l), normal=web * t.ey)


def end_holes(t: Tube, member: str, end: int, rule: dict, webs=(-1, 1), d=None, offsets=None) -> list[dict]:
    """The holes at one closed end, each at the least distances CHS-10 lets it stand: its centre 1.25 d from the end of
    its web's flat, or 1.5 d over `z_bottom_leg` where fillets of that leg run along the bottom edges, and its edge a
    diameter from the end weld's toe. `corners` puts a drain by the floor and a vent by the top of each web, `middle` one
    hole at mid-depth in each web, where a small section's flat takes no more. `offsets` gives each web's end along the
    axis from the axis's end, where the end is a mitre."""
    d = float(d or rule["d"])
    u = rule["leg"] + rule.get("clear", 0.0) + 1.5 * d
    off = offsets or {}
    if rule["holes"] == "middle":
        return [_web_hole(t, member, end, w, 0.0, d, u, "drain and vent", off.get(w, 0.0)) for w in webs]
    zb = -t.sec.d / 2 + max(t.sec.ro + 1.25 * d, rule.get("z_bottom_leg", 0.0) + 1.5 * d)
    zt = t.sec.d / 2 - (t.sec.ro + 1.25 * d)
    out = []
    for w in webs:
        out += [_web_hole(t, member, end, w, zb, d, u, "drain", off.get(w, 0.0)), _web_hole(t, member, end, w, zt, d, u, "vent", off.get(w, 0.0))]
    return out


def _front_web(t: Tube) -> int:
    """The web facing the drawbar, -X, as +1 or -1 along the tube's width."""
    return 1 if float(t.ey[0]) < 0 else -1


def frame_sections(ch: Chassis) -> tuple[list[Section], list[dict]]:
    """Every closed section of the welded frame with its openings, and every hole for galvanising in it. The spare
    carrier posts bolt on after galvanising and are dipped apart, so they are not of this dip."""
    V, data = ch.V, ch.data
    rules = data["member_galvanising_holes"]
    ds = data["galvanising_check"].get("slice", 5.0)
    sections, holes = [], []
    mem = {m.id: m for m in ch.members}

    def tube(m: Member, p0=None, p1=None, name=None):
        return Tube(name or m.id, p0 if p0 is not None else m.p0, p1 if p1 is not None else m.p1, m.sec, m.depth_dir, ds)

    def add(sec: Section, hs: list[dict], tix: int = 0):
        for h in hs:
            sec.add_hole(tix, h["u"], h["centre"], h["normal"], h["d"], h["use"], end=h["end"], wall_t=sec.tubes[tix].sec.t)
            holes.append(dict(h, section=sec.id))
        return sec

    rail_holes = data.get("galvanising_holes") or []
    for s in (-1, 1):
        side = "K" if s < 0 else "R"
        rl = mem[f"RL-{side}"]
        t = tube(rl)
        sec = Section(rl.id, rl.name, [t], ("closed", "open"))
        ep = next(f for f in data["fittings"] if f["id"] == "CH-P15")
        sec.add_slot(0, ep.get("lift", 0.0) - rl.sec.t, rl.sec.b - 2 * rl.sec.t, label="the slot under the end plate")
        for g in rail_holes:
            x, z, d = ch.ev(g["x"]), ch.ev(g["z"]), float(g["d"])
            w = (1 if g["web"] == "outer" else -1) * s * (1 if float(t.ey[1]) > 0 else -1)
            sec.add_hole(0, x - V["body_x0"], t.point(x - V["body_x0"], w * rl.sec.b / 2, z - rl.p0[2]), w * t.ey, d, g["use"],
                         end=0, wall_t=rl.sec.t)
        sections.append(sec)
        rs = mem[f"RS-{side}"]
        sections.append(Section(rs.id, rs.name, [tube(rs)], ("open", "open")))
    # the drawbar members: the A-frame length and the lap length one tube through the open mitre, the apex end capped,
    # the snipe at the lap's rear end open. The apex end is cut square to the member through its axis point (`apex_cut`),
    # so both webs end there. The mitre's plane halves the angle between the two lengths, so on the web inside the bend
    # the mitre's line stands half the width times the tangent of half that angle behind the axis point, and on the other
    # web as far ahead, and each mitre drain stands its distance along its own web from that web's line (I2-89)
    dbr = rules["drawbar"]
    half = math.atan2(V["rail_c"] - V["db_apex_y"], V["body_x0"] - V["db_apex_x"]) / 2
    for side in ("K", "R"):
        a, b = mem[f"DB-{side}A"], mem[f"DB-{side}B"]
        ta, tb = tube(a), tube(b)
        sec = Section(f"DB-{side}", f"Drawbar member, {a.name.split(', ')[1]}, apex end to the snipe", [ta, tb],
                      ("closed", "open" if dbr.get("snipe") == "open" else "closed"))
        apex = [h for h in end_holes(ta, a.id, 0, dict(dbr, holes="corners"))]
        add(sec, apex, 0)
        inside = 1 if side == "K" else -1                  # the web toward the centreline, along the lap's width
        m = tb.sec.b / 2 * math.tan(half)
        mitre = [h for h in end_holes(tb, b.id, 0, dict(dbr, holes="corners"), offsets={inside: m, -inside: -m}) if h["use"] == "drain"]
        add(sec, mitre, 1)
        sections.append(sec)
    # crossmembers, outriggers, the cross brace, the plan braces and the hinge crossmembers' gussets: each end welded to
    # the member it meets is closed, an outrigger's tip under its side marker's cap is open
    for m in ch.members:
        if m.role == "cm_xt" and getattr(m.sec, "cells", 1) > 1:
            sections += _twin_sections(ch, m, rules, ds, holes)
            continue
        if m.role in ("cm_end", "cm_floor", "cm_xt"):
            r = rules[m.role]
            r = dict(r, **r.get("by_section", {}).get(m.sec.id, {}))     # a wider section's own holes (the XT hinge crossmembers)
            cut = next((c for c in rules.get("cut_ends", []) if c["member"] == m.id), None)
            if cut:                                  # the rear crossmember's ends at its recovery tongues' faces
                ex = np.subtract(m.p1, m.p0) / m.length
                t = tube(m, np.add(m.p0, ex * cut["cut"]), np.subtract(m.p1, ex * cut["cut"]))
                r = dict(r, leg=cut["leg"])
            else:
                t = tube(m)
            sec = Section(m.id, m.name, [t], ("closed", "closed"))
            # a crossmember whose front web the shock support plates cover drains and vents its front corners through the
            # rails' webs (I2-107): the members come from the plates' own places, Chassis.shock_plates
            plated = {p["member"] for p in ch.shock_plates()}
            blocked = rules["shock_plate_web"] if m.id in plated else None
            if blocked:
                blocked = dict(blocked, **blocked.get("by_section", {}).get(m.sec.id, {}))
            for e in (0, 1):
                if blocked:
                    free = -_front_web(t) if blocked["web"] == "front" else _front_web(t)
                    add(sec, end_holes(t, m.id, e, r, webs=(free,), d=blocked["free_d"]))
                    for zh in blocked["internal_z"]:
                        u = 0.0 if e == 0 else t.L
                        c = t.point(u, 0.0, zh)
                        hh = dict(member=m.id, tube=t.name, end=e, web=0, u=u, z_l=zh, d=float(blocked["internal_d"]),
                                  use="drain" if zh < 0 else "vent", via="host", host=f"RL-{'K' if (e == 0) == (float(t.ex[1]) > 0) else 'R'}",
                                  centre=c, normal=t.ex)
                        add(sec, [hh])
                else:
                    add(sec, end_holes(t, m.id, e, r))
            sections.append(sec)
        elif m.role == "outrigger":
            t = tube(m)
            sections.append(add(Section(m.id, m.name, [t], ("closed", "open")), end_holes(t, m.id, 0, rules["outrigger"])))
        elif m.role == "brace":
            t = tube(m)
            sections.append(add(Section(m.id, m.name, [t], ("closed", "closed")),
                                end_holes(t, m.id, 0, rules["brace"]) + end_holes(t, m.id, 1, rules["brace"])))
        elif m.role == "plan_brace":
            r = rules["plan_brace"]
            if m.id.endswith("R"):                   # cut at the crossing and welded to the continuous diagonal (est.)
                mid = np.add(m.p0, m.p1) / 2
                for k, (p0, p1) in enumerate(((m.p0, mid), (mid, m.p1)), 1):
                    t = tube(m, p0, p1, name=f"{m.id}.{k}")
                    sections.append(add(Section(f"{m.id}.{k}", f"{m.name}, half {k}", [t], ("closed", "closed")),
                                        end_holes(t, m.id, 0, r) + end_holes(t, m.id, 1, r)))
            else:
                t = tube(m)
                sections.append(add(Section(m.id, m.name, [t], ("closed", "closed")), end_holes(t, m.id, 0, r) + end_holes(t, m.id, 1, r)))
    g = rules["hinge_gusset"]
    gsec = ch.sections[next(f for f in data["fittings"] if f["id"] == "CH-P08")["section"]]
    for hg in ch.hinge_gussets():                 # its axis between its two cut faces, each web's end at its mitre
        t = Tube(hg["id"], hg["p0"], hg["p1"], gsec, (0, 0, 1), ds)
        sections.append(add(Section(hg["id"], f"Hinge crossmember gusset {'behind' if hg['face'] > 0 else 'ahead of'} {hg['cm']}, "
                                    f"{'kerb' if hg['side'] < 0 else 'road'} side", [t], ("closed", "closed")),
                            end_holes(t, hg["id"], 0, g, offsets=hg["offsets"]) + end_holes(t, hg["id"], 1, g, offsets=hg["offsets"])))
    return sections, holes


def _twin_sections(ch: Chassis, m: Member, rules: dict, ds: float, holes: list[dict]) -> list[Section]:
    """A twin hinge crossmember's tubes, each its own closed section between the rails' webs (member_galvanising_holes
    twin): at each end its outer web's drain and vent where that web is free, and a drain and a vent through the rail's
    inner web inside its end. Where the shock support plates cover a tube's outer web its drain and vent at each end
    pass through both webs face to face into the other tube, which also vents the overlap between them, and elsewhere
    that overlap vents through both webs at two corners diagonally opposite (sealed_overlaps TWIN). A hole through both
    webs is an opening of the covered tube only, and a hole in each web for the hole checks. Each hole gives its web
    (`web_id`) and that web's offset from the member's axis (`y_web`)."""
    tw = rules["twin"]
    r = dict(rules["cm_xt"], d=tw["own_d"])
    csec = ch.sections[m.sec.cell]
    plated = {p["member"] for p in ch.shock_plates()}
    blocked = rules["shock_plate_web"]["web"] if m.id in plated else None
    probe = Tube(m.id, m.p0, m.p1, csec, m.depth_dir, ds)
    bc, n = m.sec.cell_b, m.sec.cells
    tubes = []
    for k in range(n):                       # k 0 the tube on -ey, the rear one for a crossmember from kerb to road
        off = -m.sec.b / 2 + bc / 2 + k * bc
        t = Tube(f"{m.id}.{k + 1}", np.add(m.p0, off * probe.ey), np.add(m.p1, off * probe.ey), csec, m.depth_dir, ds)
        outer = -1 if k == 0 else 1
        front = _front_web(t) == outer
        tubes.append((t, outer, front, off))
    out = []

    def tag(hs, t, off, inner=False):
        for h in hs:
            h["web_id"] = f"{t.name} web {h['web']}"
            h["y_web"] = abs(off) - csec.b / 2 + csec.t / 2 if inner else abs(off) + csec.b / 2 - csec.t / 2
        return hs

    for k, (t, outer, front, off) in enumerate(tubes):
        sec = Section(t.name, f"{m.name}, its {'front' if front else 'rear'} tube", [t], ("closed", "closed"))
        covered = blocked == "front" and front
        for e in (0, 1):
            hs = [] if covered else tag(end_holes(t, m.id, e, r, webs=(outer,)), t, off)
            u = 0.0 if e == 0 else t.L
            for zh in tw["internal_z"]:
                hs.append(dict(member=m.id, tube=t.name, end=e, web=0, u=u, z_l=zh, d=float(tw["internal_d"]),
                               use="drain" if zh < 0 else "vent", via="host",
                               host=f"RL-{'K' if (e == 0) == (float(t.ex[1]) > 0) else 'R'}", centre=t.point(u, 0.0, zh), normal=t.ex))
            if covered:
                hs += tag(end_holes(t, m.id, e, dict(r, d=tw["through_d"]), webs=(-outer,)), t, off, inner=True)
                for h in hs:
                    if h["via"] == "own":
                        h["through"] = True
            for h in hs:
                sec.add_hole(0, h["u"], h["centre"], h["normal"], h["d"], h["use"], end=h["end"], wall_t=csec.t)
                holes.append(dict(h, section=sec.id))
        out.append(sec)
    # each through hole's twin in the other tube's web face to face, and the overlap's vents where no tube is covered
    other = {t.name: tubes[1 - k] for k, (t, *_r) in enumerate(tubes)} if n == 2 else {}
    for h in [h for h in holes if h.get("through") and h["member"] == m.id]:
        t2, outer2, _, off2 = other[h["tube"]]
        twin = _web_hole(t2, m.id, h["end"], -outer2, h["z_l"], h["d"], h["u_web"], h["use"])
        holes.append(dict(tag([twin], t2, off2, inner=True)[0], section=t2.name, through=True))
    if not any(blocked == "front" and front for _t, _o, front, _off in tubes):
        for e, low in ((0, True), (1, False)):       # the kerb end low and the road end high, diagonally opposite
            for t, outer, _, off in tubes:
                hv = [h for h in end_holes(t, m.id, e, dict(r, d=tw["vent_d"]), webs=(-outer,)) if (h["use"] == "drain") == low]
                holes.append(dict(tag(hv, t, off, inner=True)[0], use="vent for the webs' overlap", section=t.name, through=True))
    return out


def end_areas(sec: Section, zone: float) -> list[dict]:
    """The openings at each closed end of a section and the area the guide asks there."""
    out = []
    for e, kind in enumerate(sec.ends):
        if kind != "closed":
            continue
        t = sec.tubes[0 if e == 0 else -1]
        tix = 0 if e == 0 else len(sec.tubes) - 1
        near = [o for o in sec.openings if o["kind"] == "hole" and o["tube"] == tix and (o["u"] if e == 0 else t.L - o["u"]) <= zone]
        slot = sum(o["height"] * o["width"] for o in sec.openings if o["kind"] == "slot" and o["end"] == e)
        need = math.pi / 4 * one_hole_d(t.sec) ** 2
        have = sum(math.pi / 4 * o["d"] ** 2 for o in near) + slot
        out.append(dict(end=e, holes=len(near), area=have, need=need, ok=have >= need - 0.5,
                        small=[o["d"] for o in near if o["d"] < max(10.0, o["wall_t"] or 0.0) - 1e-9]))
    return out


def overlap_rule(area: float) -> tuple[float, int]:
    """The guide's least vent for a seal welded overlap of `area` mm2 and how many it asks at least (pages 29 and 30):
    none under 10,000 mm2, 10 mm to 40,000, 12 mm above, 20 mm from 250,000 and one every 250,000, two for the best outcome."""
    if area < 10000:
        return 0.0, 0
    if area >= 250000:
        return 20.0, max(2, math.ceil(area / 250000))
    return (10.0 if area <= 40000 else 12.0), 2


def overlaps(ch: Chassis) -> list[dict]:
    """Each seal welded overlap (sealed_overlaps) against the guide's vents, each vent at least the steel's thickness."""
    out = []
    for o in ch.data.get("sealed_overlaps") or []:
        L, W = float(ch.ev(o["l"])), float(o["w"])
        area = L * W
        need_d, need_n = overlap_rule(area)
        ds = [float(v["d"]) for v in o["vents"]]
        least = max(need_d, float(o["t"]))
        ok = len(ds) >= need_n and all(d >= least - 1e-9 for d in ds)
        out.append(dict(id=o["id"], what=o["what"], qty=o["qty"], area=area, need_d=least if need_n else 0.0, need_n=need_n,
                        vents=ds, ok=ok))
    return out


def check(ch: Chassis) -> dict:
    """CHS-11: every closed section in every hang the dip takes, each low point drained and each high point vented
    within max_depth, every hole at least the guide's least and each closed end's holes at least its table's area."""
    cfg = ch.data["galvanising_check"]
    dip = ch.data["galvanising_dip"]
    p0, p1 = cfg["pitch_deg"]
    pitches = [p0 + k * cfg["step_deg"] for k in range(int(round((p1 - p0) / cfg["step_deg"])) + 1)]
    sections, holes = frame_sections(ch)
    rows = []
    for sec in sections:
        reads = []
        for kerb_down in (True, False):
            for p in pitches:
                r = sec.read(up_vector(dip["roll_deg"], p, kerb_down), cfg["max_depth"])
                r.update(hang=f"{'kerb' if kerb_down else 'road'} side down, pitched {p:g} deg")
                reads.append(r)
        low = max(reads, key=lambda r: r["low_depth"])
        high = max(reads, key=lambda r: r["high_depth"])
        ends = end_areas(sec, cfg["end_zone"])
        size_ok = all(e["ok"] and not e["small"] for e in ends)
        depth_ok = all(r["ok"] for r in reads)
        rows.append(dict(id=sec.id, name=sec.name, ends=ends, size_ok=size_ok, depth_ok=depth_ok, ok=depth_ok and size_ok,
                         holes=sum(1 for o in sec.openings if o["kind"] == "hole"),
                         low_depth=low["low_depth"], low_at=low["low_at"], low_hang=low["hang"],
                         high_depth=high["high_depth"], high_at=high["high_at"], high_hang=high["hang"],
                         liquid_l=max(r["liquid_l"] for r in reads), air_l=max(r["air_l"] for r in reads)))
    plain = [dict({k: v for k, v in h.items() if k not in ("centre", "normal")}, x=float(h["centre"][0]), y=float(h["centre"][1]),
                  z=float(h["centre"][2])) for h in holes]
    return dict(sections=rows, holes=plain, pitches=pitches, roll=dip["roll_deg"], max_depth=cfg["max_depth"], overlaps=overlaps(ch))

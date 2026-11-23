"""The ute's bike garage (UTE-GARAGE.md, research report 17).

Builds data/assemblies/ute-garage.yaml with the trailer module's machinery (cad/model), measures the clearance,
restraint and contact checks of data/ute/garage-checks.yaml on the B-rep model, works out the deck mount loads, the
anchor loads, the ramp angle, the tub height and the box mass, and hands cad/ute.py the garage's mass lines in the ute
frame (DIM-U1). Module X 0 sits at ute X `module_x0` and module Z 0 at the deck height `deck_z`.
"""
from __future__ import annotations

import math

from build123d import Compound

from .checks import evaluate
from .massprops import GROWTH, bike_rows, line_masses
from .model.assembly import Model
from .partsdb import Project

G = 9.81
BOX_CASES = ["UC1", "UC2", "UC3", "UC4"]
BIKE_CASES = ["UC2", "UC3"]
TOOL_CASES = ["UC2", "UC3", "UC4"]
DESIGN_H = {"TU": 700, "ST": 600}          # report 03's design centre of gravity heights above the floor
PANNIERS_KG = 9.0                          # Mosko Moto panniers on the Tuareg (estimate, data/ute/ute.yaml UT-09)


def _status(ok: bool, severity: str) -> str:
    return ("PASS" if ok else "FAIL") if severity == "fail" else ("MEETS LIMIT" if ok else "REPORTED")


def _row(cid, title, severity, limit, measured, margin, ok, governing, detail, why, unit="", **extra):
    return dict(id=cid, sub="", title=title, type="computed", severity=severity, added_by_build=False, a=[], b=[],
                limit=limit, measured_mm=measured, margin_mm=margin, overlap_mm3=0.0, ok=ok, status=_status(ok, severity),
                governing=governing, points=[], detail=detail, why=why, unit=unit, **extra)


def strip_membrane(q: float, t: float, span: float, E: float, n: int = 400) -> dict:
    """A unit-width strip of sheet welded to two bows (clamped, ends held) under a uniform pressure q (N/mm2), with bending
    and membrane tension together: the closed-form clamped beam-column, iterated until the tension matches the strip's
    stretch. Returns the centre deflection, the tension and the stress at the bow."""
    I = t ** 3 / 12.0
    N = 1e-6

    def w(x, N):
        k = math.sqrt(N / (E * I))
        a = k * span / 2.0
        if a < 1e-4:
            return q * x * x * (span - x) ** 2 / (24 * E * I)
        u = abs(k * (x - span / 2))
        d = 1 - math.exp(-2 * a)
        ratio = (math.exp(u - a) + math.exp(-u - a)) / d - (1 + math.exp(-2 * a)) / d
        return q / (2 * N) * x * (span - x) - q * span / (2 * N * k) * ratio
    for _ in range(2000):
        h = span / n
        s = sum(((w((i + 1) * h, N) - w(i * h, N)) / h) ** 2 * h for i in range(n))
        N_new = E * t / (2 * span) * s
        if abs(N_new - N) < 1e-6 * max(N_new, 1e-9):
            break
        N = 0.5 * N + 0.5 * N_new
    hh = 1e-3
    M_end = E * I * abs((w(2 * hh, N) - 2 * w(hh, N) + w(0, N)) / hh ** 2)
    return dict(defl_mm=w(span / 2, N), tension_n_mm=N, end_mpa=6 * M_end / t ** 2 + N / t)


def roof_skin(prj, c) -> dict:
    """UGF-01: the roof skin between its bows (data/ute/garage-checks.yaml `roof`). Highway suction with membrane action
    against welded 5052's yield at the bow, standing water against the 1:50 fall from the crown to each edge, and a
    knee against the sheet's yield-line punching load, which is the reason for the no-step rule (reported)."""
    P, r = prj.P, c.roof
    t, fs = P.get("roof_t"), P.get("frame_s")
    centres = sorted([-fs / 2] + [x + fs / 2 for x in P.get("bow_x")] + [P.get("garage_length") + P.get("leaf_t") / 2])
    span = max(b - a for a, b in zip(centres, centres[1:]))
    q = 0.6 * (r["speed_kmh"] / 3.6) ** 2 * r["cp"] / 1e6
    s = strip_membrane(q, t, span, r["E_mpa"])
    u_suction = s["end_mpa"] / r["fy_haz_mpa"]
    fall = P.get("half_width") / r["fall"]
    q_w = r["water_kpa"] * 1e-3 + 2.68e-6 * 9.81 * t      # the water film and the sheet's own weight, N/mm2
    sag = strip_membrane(q_w, t, span, r["E_mpa"])["defl_mm"]
    u_pond = sag / fall
    knee = 2 * math.pi * r["fy_mpa"] * t ** 2 / 4 / 1000
    # where the skin is not welded, the adhesive bead along each bow holds it: the strip's membrane tension in shear across
    # the bead's width, and the suction on the two half spans either side of the bow pulling it off the bow
    bd = r["bond"]
    allow = bd["factor"] * bd["lap_shear_mpa"]
    tau = s["tension_n_mm"] / bd["width_mm"]
    pull = q * span / bd["width_mm"]
    u_bond = max(tau, pull) / allow
    # the rivets through the bead, alone, as if it had let go: the membrane tension in shear, against the rivet's shear and
    # the 1.6 mm skin's bearing, and the suction's pull in tension, each at `factor` of its rating
    rv = r["rivets"]
    v_rivet = s["tension_n_mm"] * rv["pitch_mm"]
    t_rivet = q * span * rv["pitch_mm"]
    bearing = 1.5 * rv["bearing_fu_mpa"] * 4.8 * t
    u_rivet = max(v_rivet / (rv["factor"] * min(rv["shear_n"], bearing)), t_rivet / (rv["factor"] * rv["tensile_n"]))
    util = max(u_suction, u_pond, u_bond, u_rivet)
    ok = util <= 1.0
    gov = max((u_suction, "suction at the bow"), (u_pond, "standing water"), (u_bond, "the bow's adhesive bead"), (u_rivet, "the bow's rivets"))[1]
    return _row(c.id, c.title, c.severity, f"bow stress <= {r['fy_haz_mpa']:g} MPa, sag under the fall, bead within half its strength",
                round(s["end_mpa"], 1), round(r["fy_haz_mpa"] - s["end_mpa"], 1), ok, gov,
                (f"{t:g} mm 5052-H32 over bows {span:.0f} mm apart, held at every bow: welded along the front edge, the first bow and the "
                 f"butt joints, and rivet-bonded along every other bow, {bd['name']} with {rv['name']} at {rv['pitch_mm']:g} mm through it and no welds there. Suction at {r['speed_kmh']:.0f} km/h with "
                 f"Cp -{r['cp']:g}, {q * 1e6 / 1000:.2f} kPa: the sheet drums {s['defl_mm']:.1f} mm and reaches {s['end_mpa']:.0f} MPa at the bow "
                 f"with membrane action, against welded 5052's {r['fy_haz_mpa']:g} MPa ({u_suction:.2f}). The {bd['width_mm']:g} mm bead would carry "
                 f"the sheet's {s['tension_n_mm']:.1f} N/mm of tension at {tau:.2f} MPa even where the skin ended at a bow, and the suction's pull at {pull:.3f} MPa, against half its "
                 f"{bd['lap_shear_mpa']:g} MPa lap shear ({u_bond:.2f}). Alone, each rivet would carry {v_rivet:.0f} N of that tension in shear "
                 f"and {t_rivet:.0f} N of the pull, against half its {min(rv['shear_n'], bearing):,.0f} N and {rv['tensile_n']:,.0f} N ({u_rivet:.2f}). "
                 f"A {r['water_kpa'] * 100:.0f} mm water film sags it "
                 f"{sag:.2f} mm against the 1:{r['fall']:g} fall's {fall:.1f} mm, so water runs off. A knee of {r['knee_kn']:g} kN punches "
                 f"through at {knee:.2f} kN, so the roof is marked no step, no kneeling, on a label on the roof itself"),
                c.why, unit="MPa", roof=dict(span_mm=span, suction_kpa=q * 1000, drum_mm=s["defl_mm"], bow_mpa=s["end_mpa"], sag_mm=sag,
                                             fall_mm=fall, knee_capacity_kn=knee, knee_kn=r["knee_kn"], bond_mpa=max(tau, pull),
                                             bond_util=u_bond, tension_n_mm=s["tension_n_mm"], rivet_shear_n=v_rivet,
                                             rivet_pull_n=t_rivet, rivet_util=u_rivet, rivet_pitch_mm=rv["pitch_mm"]))


def rhs_plastic_modulus(b: float, d: float, t: float) -> float:
    """Plastic section modulus (mm3) of an RHS b wide and d deep, bent about the axis along its width, with Australian
    Tube Mills' corner radii (outer 2.0 t up to 3 mm wall and 2.5 t above, inner the outer less t), as
    data/chassis/sections.yaml computes them."""
    ro = (2.0 if t <= 3 else 2.5) * t
    ri = ro - t
    k = (10 - 3 * math.pi) / (12 - 3 * math.pi)      # a corner spandrel's centroid from the corner, as a fraction of r

    def spandrels(r, half):
        return 4 * (1 - math.pi / 4) * r * r * (half - k * r)
    return b * d * d / 4 - (b - 2 * t) * (d - 2 * t) ** 2 / 4 - spandrels(ro, d / 2) + spandrels(ri, d / 2 - t)


def crossmember_check(prj, model, P) -> dict:
    """UGR-03: a steel crossmember under a track row carries a strap's breaking load at any of its anchors (report 24). The
    crossmember bears on the runners or the steel stubs over Ford's two pads at its station and runs on outboard of them
    to the walls. The vertical part of the breaking load bends it: simply supported between the pads, or as a cantilever
    outboard.
    The capacity is AS 4100's 0.9 fy Ze, with Ze the plastic modulus of the compact RHS laid flat."""
    worst = None
    yb = P.get("pad_y")                               # the crossmember bears on the runners or stubs over Ford's pads
    loads = anchor_loads(prj, model)
    for a in loads:
        y = abs(a["y"])
        lever = y - yb if y > yb else (yb - a["y"]) * (yb + a["y"]) / (2 * yb)
        m = a["f_kn"] * a["cz"] * lever / 1000            # kN m
        if worst is None or m > worst["m"]:
            worst = dict(m=m, strap=a["strap"], y=a["y"], cz=a["cz"], lever=lever, outboard=y > yb)
    f_kn = loads[0]["f_kn"]
    b, h, t, fy = P.get("steel_w"), P.get("steel_h"), P.get("steel_t"), P.get("steel_fy")
    s_mm3 = rhs_plastic_modulus(b, h, t)
    cap = 0.9 * fy * s_mm3 / 1e6                          # kN m
    u = worst["m"] / cap
    where = "outboard of" if worst["outboard"] else "between"
    return _row("UGR-03", "Steel crossmember carries a strap's breaking load at its worst anchor", "fail", "<= 1.00",
                round(u, 3), round(1 - u, 3), u <= 1.0, f"{worst['strap']} anchor at Y {worst['y']:.0f}, {where} Ford's pads",
                f"{f_kn:.1f} kN breaking load x {worst['cz']:.2f} vertical x {worst['lever']:.0f} mm = {worst['m']:.2f} kN m, against "
                f"0.9 x {fy:.0f} MPa x {s_mm3:,.0f} mm3 = {cap:.2f} kN m for the RHS {b:g} x {h:g} x {t:g} laid flat. Supports at Y +/-{yb:.0f}, "
                "over Ford's pads",
                "Research report 24: an anchor withstands its strap's breaking load (NTC guide p. 201), so the crossmember under it must too. "
                "AS 4100 clause 5.1: the section is compact, so Ze is the plastic modulus.", unit="")


def anchor_loads(prj, model) -> list[dict]:
    """Every strap's anchor in the module frame with its breaking load (twice its LC, AS/NZS 4380) and the vertical
    cosine of its pull."""
    lc = next(c for c in prj.checks if c.id == "UGR-01").restraint["lc_kg"]
    f_kn = 2 * lc * G / 1000
    out = []
    for iid, s in model.built.items():
        sp = s.inst.special.get("strap")
        if not sp:
            continue
        pts = s.info["points"]
        ends = [(pts[0], pts[1]), (pts[-1], pts[-2])] if sp["point"] == "rear_wheel" else [(pts[1], pts[0])]
        for anchor, towards in ends:
            d = [towards[i] - anchor[i] for i in range(3)]
            out.append(dict(strap=iid, x=anchor[0], y=anchor[1], f_kn=f_kn, cz=abs(d[2]) / math.sqrt(sum(v * v for v in d))))
    return out


def stub_check(prj, model, P) -> dict:
    """UGR-04: Ford's first pads are under the front wall, so the front track row's steel crossmember reaches them through
    two steel stubs, and the aluminium runners start where the stubs end. A strap's breaking load at the front row is
    taken as a point load on the line from the first pad to the second, simply supported at both (est.): the steel at the
    row and the aluminium runner at the joint are each checked in bending. Steel: AS 4100's 0.9 fy Ze. Aluminium: welded
    6061-T6's 103 MPa yield times 0.85 (est., AS/NZS 1664.1) on the plastic modulus."""
    yb, xr = P.get("pad_y"), P.get("front_row_x")
    x1, x2, xj = P.get("mount1_x"), P.get("mount2_x"), P.get("stub_x1")
    L, a = x2 - x1, xr - x1
    worst = None
    for an in anchor_loads(prj, model):
        if abs(an["x"] - xr) > 1.0:
            continue
        r = an["f_kn"] * an["cz"] * (yb + abs(an["y"])) / (2 * yb)       # the nearer support's share
        if worst is None or r > worst["r"]:
            worst = dict(r=r, strap=an["strap"], y=an["y"], cz=an["cz"])
    m_row = worst["r"] * a * (L - a) / L / 1000                          # kN m under the row, in the steel
    m_joint = worst["r"] * a * (L - (xj - x1)) / L / 1000                 # at the joint, in the aluminium
    zs = rhs_plastic_modulus(P.get("stub_w"), P.get("sub_h"), P.get("stub_t"))
    za = rhs_plastic_modulus(P.get("runner_w"), P.get("sub_h"), 3.0)
    cap_s, cap_a = 0.9 * P.get("steel_fy") * zs / 1e6, 0.85 * 103 * za / 1e6
    u = max(m_row / cap_s, m_joint / cap_a)
    gov = "the steel at the row" if m_row / cap_s >= m_joint / cap_a else "the aluminium runner at the joint"
    return _row("UGR-04", "Steel stubs and runners carry a strap's breaking load at the front row to Ford's first two pads", "fail",
                "<= 1.00", round(u, 3), round(1 - u, 3), u <= 1.0, f"{worst['strap']}, {gov}",
                (f"{worst['r']:.1f} kN on the nearer stub ({worst['strap']}, Y {worst['y']:.0f}), {a:.0f} mm behind the first pad on the "
                 f"{L:.0f} mm between the first two: {m_row:.2f} kN m in the steel RHS {P.get('stub_w'):g} x {P.get('sub_h'):g} x "
                 f"{P.get('stub_t'):g} against {cap_s:.2f} kN m, and {m_joint:.2f} kN m in the aluminium runner at the joint "
                 f"{xj - x1:.0f} mm behind the first pad against {cap_a:.2f} kN m"),
                "Research report 24's rule, that an anchor withstands its strap's breaking load, carried from the front row to Ford's pads.",
                unit="")


def _extent(model, P, x0, dz, skip_parts=()) -> dict:
    """Outside extent of the box in the ute frame, as it travels: everything but the loading view and the context. With
    skip_parts=("U-FLARE",) it is the body's extent without the rear tub flares (UTE-09's body limit, decision H19)."""
    shapes = [b.shape for b in model.built.values()
              if not b.inst.check_only and b.inst.display != "loading_only" and b.inst.group not in ("context", "bikes")
              and b.inst.part not in skip_parts]
    bb = Compound(children=shapes).bounding_box()
    return dict(x0=bb.min.X + x0, x1=bb.max.X + x0, y0=bb.min.Y, y1=bb.max.Y, z0=bb.min.Z + dz, z1=bb.max.Z + dz)


STATIONS = 4                               # Ford's body mounting pad pairs on the single cab (BEMM p. 125)


def mount_loads(lines: list[dict], P, limits: dict) -> dict:
    """Vertical and horizontal loads on Ford's body mounting pads from the box and everything in it, with growth.

    The box is taken as rigid on Ford's four pairs of pads. Vertical reactions vary linearly along the ute (the least
    squares share of a rigid body on equal supports). Ford's road-load inputs of up to 2 g in x, y and z at each pad
    (BEMM p. 124, limit `mount_g`): braking 2 g forward and cornering 2 g sideways, each with gravity, a bump of 2 g
    down on top of gravity, and a net 1 g upward. The flexible mounts at the first pair take no horizontal load, so the
    six rigid mounts carry it all. One M14 10.9 bolt per pad.
    """
    x0 = P.get("module_x0")
    xs = [P.get(f"mount{i}_x") + x0 for i in range(1, STATIONS + 1)]
    firm = [False] + [True] * (STATIONS - 1)
    bolts = [1] * STATIONS
    carried = [ln for ln in lines if set(ln["cases"]) & {"UC2"}]
    M = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) for ln in carried)
    xc = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) * ln["x"] for ln in carried) / M
    zc = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) * ln["z"] for ln in carried) / M
    z_if = P.get("frame_top_z") + P.get("pad_h")        # the pads' top
    h = zc - z_if
    W = M * G / 1000                                    # kN
    g = limits["mount_g"]
    n = len(xs)
    xb = sum(xs) / n
    S = sum((x - xb) ** 2 for x in xs)
    b_track = 2 * P.get("pad_y")                        # bolt line to bolt line across the ute, over Ford's pads

    def vertical(Wz, Fx):
        """Upward reaction per station (kN) for a downward load Wz at xc and a forward force Fx at height h."""
        a = Wz / n
        b = (Wz * (xc - xb) - Fx * h) / S
        return [a + b * (x - xb) for x in xs]

    # Each case: station reactions R, horizontal loads, and the roll couple's vertical force per pad (cornering,
    # shared equally by the four stations, plus on the leeward side and minus on the windward side).
    cases = {}
    fb = g * W
    cases["braking"] = dict(R=vertical(W, fb), shear_x=fb, shear_y=0.0, roll=0.0, sides=(("each", 0),))
    fl = g * W
    cases["cornering"] = dict(R=vertical(W, 0.0), shear_x=0.0, shear_y=fl, roll=fl * h / b_track / n,
                              sides=(("windward", -1), ("leeward", 1)))
    cases["bump"] = dict(R=vertical((1 + g) * W, 0.0), shear_x=0.0, shear_y=0.0, roll=0.0, sides=(("each", 0),))
    cases["upward"] = dict(R=[-r for r in vertical((g - 1) * W, 0.0)], shear_x=0.0, shear_y=0.0, roll=0.0, sides=(("each", 0),))
    nt, vf = limits["bolt_tension_kn"], limits["bolt_shear_kn"]
    firm_bolts = 2 * sum(b for b, f in zip(bolts, firm) if f)       # two pads per station
    rows, worst = [], None
    for cname, c in cases.items():
        V = math.hypot(c["shear_x"], c["shear_y"]) / firm_bolts          # per firm bolt
        for i, (x, R) in enumerate(zip(xs, c["R"])):
            for side, sgn in c["sides"]:
                Rb = R / 2 + sgn * c["roll"]
                tension = max(0.0, -Rb)
                Nb = tension / bolts[i]
                Vb = V if firm[i] else 0.0
                u = (Vb / vf) ** 2 + (Nb / nt) ** 2
                r = dict(case=cname, station=i + 1, x=round(x), dx_axle=round(x - P.get("rear_axle_x")), mount="rigid" if firm[i] else "flexible",
                         side=side, bracket_kn=round(Rb, 2), tension_kn=round(tension, 2), bolt_tension_kn=round(Nb, 2),
                         bolt_shear_kn=round(Vb, 2), interaction=round(u, 4))
                rows.append(r)
                if worst is None or u > worst["interaction"]:
                    worst = r
    return dict(mass_kg=round(M, 1), cog_x=round(xc, 1), cog_z=round(zc, 1), h_mm=round(h, 1), stations=[round(x) for x in xs],
                rows=rows, worst=worst, max_tension_kn=max(r["tension_kn"] for r in rows),
                max_down_kn=max(r["bracket_kn"] for r in rows), firm_bolt_shear_kn=round(cases["braking"]["shear_x"] / firm_bolts, 2))


def build_garage(prj: Project | None = None, limits: dict | None = None):
    """Build the ute garage. Returns (garage dict for cad/ute.py, the built Model)."""
    from .ute import load_data
    prj = prj or Project(assembly="ute-garage")
    lim = limits or {k: v["v"] for k, v in load_data()["limits"].items()}
    model = Model(prj)
    P = prj.P
    x0, dz = P.get("module_x0"), P.get("deck_z")

    # ---------------------------------------------------------------- mass lines in the ute frame
    rows = line_masses(prj, model)
    lines = []
    for r in rows:
        x, y, z = r["cog"]
        lines.append(dict(id=r["id"], item=r["item"], kg=r["mass_kg"], x=x + x0, y=y, z=z + dz, maturity=r["maturity"],
                          source=r["source"], cases=list(BOX_CASES), group=r["group"].replace("ute-", ""),
                          qty=r["qty"], unit=r["unit"], product=r["product"], measured=r["measured"]))
    for b in bike_rows(prj, model):
        lines.append(dict(id=f"UB-{b['id']}", item=b["item"], kg=b["mass_kg"], x=b["cog"][0] + x0, y=b["cog"][1],
                          z=dz + DESIGN_H[b["id"]], maturity=b["maturity"], cases=list(BIKE_CASES), group="bikes",
                          source=f"{b['source']}. X and Y from the bike model as parked, height report 03's design figure "
                                 f"of {DESIGN_H[b['id']]} mm above the floor"))
    bags = model.built["TU-BAGS"].shape.bounding_box()
    lines.append(dict(id="UB-TU-BAGS", item="Tuareg's Mosko Moto panniers", kg=PANNIERS_KG, x=bags.center().X + x0, y=bags.center().Y,
                      z=bags.center().Z + dz, maturity="estimate", cases=list(BIKE_CASES), group="bikes",
                      source="9 kg (estimate, data/ute/ute.yaml UT-09). Centre of the pannier envelope in the model"))
    tp = prj.parts["U-TOOLS"]
    tx, ty, tz = P.eval(tp.cog.at, {})
    lines.append(dict(id="U-TOOLS", item=tp.name, kg=tp.mass.total_kg, x=tx + x0, y=ty, z=tz + dz, maturity=tp.mass.maturity,
                      source=tp.mass.source + ". In the two chests on the wheel tubs", cases=list(TOOL_CASES), group="tools"))
    kp = prj.parts["U-TIEDOWN"]                     # the trailer's tie-down straps, in the same chests (STB-05)
    lines.append(dict(id="U-TIEDOWN", item=kp.name, kg=kp.mass.total_kg, x=tx + x0, y=ty, z=tz + dz, maturity=kp.mass.maturity,
                      source=kp.mass.source + ". In the two chests on the wheel tubs", cases=list(TOOL_CASES), group="tools"))
    ap = prj.parts["U-ANCHORS"]                     # and its ground anchors, in their bag between the bikes (F4-03)
    bag = model.built["T2"].shape.bounding_box()
    lines.append(dict(id="U-ANCHORS", item=ap.name, kg=ap.mass.total_kg, x=bag.center().X + x0, y=bag.center().Y, z=bag.center().Z + dz,
                      maturity=ap.mass.maturity, source=ap.mass.source + ". In their bag on the box floor between the bikes",
                      cases=list(TOOL_CASES), group="tools"))
    box_lines = [ln for ln in lines if ln["cases"] == BOX_CASES]
    box_kg = sum(ln["kg"] for ln in box_lines)
    box_kg_g = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) for ln in box_lines)
    by_group: dict[str, float] = {}
    for ln in box_lines:
        by_group[ln["group"]] = by_group.get(ln["group"], 0.0) + ln["kg"]

    # ---------------------------------------------------------------- measured checks
    checks = evaluate(prj, model)

    # ---------------------------------------------------------------- computed checks
    ext = _extent(model, P, x0, dz)
    body_ext = _extent(model, P, x0, dz, skip_parts=("U-FLARE", "U-MUDFLAP", "U-MUDFLAP-BKT"))
    tub_h = P.get("tub_top")
    checks.append(_row("UGD-01", "Wheel tubs no more than 100 mm above the floor, so the lower floor works", "fail",
                       f"<= {lim['tub_height_max_mm']:.0f} mm", round(tub_h, 1), round(lim["tub_height_max_mm"] - tub_h, 1),
                       tub_h <= lim["tub_height_max_mm"], "tub top over the tyre at full bump",
                       f"tub top {tub_h:.1f} mm above the floor: tyre top at full bump {P.get('wheel_z') + P.get('rear_bump') + P.get('tyre_d') / 2 + dz:.1f} mm "
                       f"above the ground, plus {P.get('tub_top_gap'):.0f} mm and the 3 mm plate, against the floor at {dz:.0f} mm",
                       "Report 17 section 6.4: take the lower floor if the bump travel keeps the tubs at or under 100 mm. On the Super "
                       "Duty the tubs follow Ford's wheelhouse envelope (BEMM p. 122).", unit="mm"))
    mass_lim = lim["box_mass_max_kg"]
    checks.append(_row("UGB-01", "Box empty, with its restraint, ramp, winch and security, lighter than report 17's 440 kg", "fail",
                       f"< {mass_lim:.0f} kg", round(box_kg, 1), round(mass_lim - box_kg, 1), box_kg < mass_lim, "box mass, no growth",
                       f"{box_kg:.1f} kg, {box_kg_g:.1f} kg with growth. " + ", ".join(f"{g} {v:.1f} kg" for g, v in sorted(by_group.items())),
                       "The decision log asks for a box lighter than report 17's 440 kg.", unit="kg"))
    ml = mount_loads(lines, P, lim)
    proof = lim["bracket_proof_factor"]
    w = ml["worst"]
    checks.append(_row("UGM-01", "Mount bolts on Ford's pads within M14 10.9 design capacity, combined tension and shear", "fail",
                       "<= 1.00", w["interaction"], round(1 - w["interaction"], 4), w["interaction"] <= 1.0,
                       f"station {w['station']} ({w['mount']}, {w['dx_axle']:+d} mm from the rear axle), {w['case']}",
                       f"worst {w['interaction']:.3f}: {w['bolt_tension_kn']:.1f} kN tension and {w['bolt_shear_kn']:.1f} kN shear per bolt "
                       f"against {lim['bolt_tension_kn']:.1f} kN and {lim['bolt_shear_kn']:.1f} kN. {ml['mass_kg']:.0f} kg with growth, "
                       f"centre of gravity {ml['h_mm']:.0f} mm above the pads",
                       "One M14 property class 10.9 bolt at each of Ford's eight pads (BEMM pp. 124 and 158), at AS 4100 clause 9.3's design "
                       f"capacities with the threads in the shear plane, under Ford's {lim['mount_g']:g} g in x, y and z (BEMM p. 124). "
                       "The flexible mounts at the first pads carry no horizontal load.", mounts=ml))
    checks.append(_row("UGM-02", "Loads on Ford's body mounting pads (reported)", "report", "reported",
                       ml["max_tension_kn"], None, True, "largest uplift and largest downward load on one pad",
                       f"largest uplift {ml['max_tension_kn']:.2f} kN, largest downward load {ml['max_down_kn']:.2f} kN, "
                       f"fore and aft shear {ml['firm_bolt_shear_kn']:.1f} kN per rigid mount's bolt in braking",
                       f"Ford gives the {lim['mount_g']:g} g inputs a body must withstand at each pad but no pad capacity, so build step 9 "
                       f"proof-loads each pad to {proof:g} times these loads (est.), "
                       f"{proof * ml['max_tension_kn']:.2f} kN up and {proof * ml['max_down_kn']:.2f} kN down, "
                       "held 10 s with no permanent set at a dial gauge, and step 11 crack-tests them after the rough-road drive.", unit="kN"))
    res = next(c for c in checks if c["id"] == "UGR-01")["restraint"]
    kn = res["worst"]["worst_kgf"] * G / 1000
    ad = lim["anchor_design_kn"]
    checks.append(_row("UGR-02", f"Worst anchor load within the {ad:g} kN each anchor is designed for", "fail",
                       f"<= {ad:g} kN", round(kn, 2), round(ad - kn, 2),
                       kn <= ad, f"{res['worst']['strap']} {res['worst']['worst_case']}",
                       f"{kn:.2f} kN at the worst strap's anchor, which reaches the frame through the steel crossmember",
                       "An anchor withstands its strap's breaking load (NTC Load Restraint Guide 2018 p. 201, report 03): "
                       f"{ad:g} kN for the LC 500 kg straps (report 24).", unit="kN"))
    checks.append(crossmember_check(prj, model, P))
    checks.append(stub_check(prj, model, P))
    drop, L = P.get("ground_drop"), 3048.0
    ang = math.degrees(math.asin(drop / L))
    ang_l = math.degrees(math.asin(dz / L))
    checks.append(_row("UGL-01", "Ramp angle with the bikes out (reported against report 03's 20 degrees)", "report",
                       f"reported, against {lim['ramp_angle_max_deg']:.0f} deg", round(ang, 2), round(lim["ramp_angle_max_deg"] - ang, 2),
                       ang <= lim["ramp_angle_max_deg"], "floor height with the bikes out",
                       f"{ang:.1f} degrees on the 3,048 mm MF-12038 from a {drop:.0f} mm sill ({ang_l:.1f} degrees at the laden {dz:.0f} mm). "
                       f"Report 17 gave 16.2 degrees for its 850 mm lower tray and 20.7 degrees for the 1,080 mm flat deck",
                       "Report 03 section 10: 20 degrees is the limit for walking a bike up beside it. The winch does the pulling.", unit="deg"))

    gaps = {c["sub"] or c["id"]: c for c in checks if c["id"] == "UGC-02"}
    dims = dict(outside_l=round(ext["x1"] - ext["x0"], 1), outside_l_body=P.get("outside_l"), outside_w=round(body_ext["y1"] - body_ext["y0"], 1),
                outside_w_flares=round(ext["y1"] - ext["y0"], 1), flare_l=P.get("flare_x1") - P.get("flare_x0"), flare_out=P.get("flare_out"),
                wheel_y=P.get("wheel_y"),
                outside_h=round(P.get("top_z"), 1), outside_h_crown=round(P.get("top_z") + P.get("roof_crown"), 1), inside_l=P.get("garage_length"), inside_w=P.get("interior_width"), inside_h=P.get("ceiling_z"),
                opening_w=P.get("door_y1") - P.get("door_y0"), opening_h=P.get("door_h"), deck_z=dz, top_z=round(dz + P.get("top_z"), 1),
                tub_h=round(tub_h, 1), tuareg_y=P.get("tuareg_y"), st_y=P.get("st_y"), bike_spacing=P.get("bike_spacing"),
                ramp_deg=round(ang, 2), ramp_deg_laden=round(ang_l, 2))
    garage = dict(lines=lines, box_extent=ext, body_extent=body_ext, module_x0=x0, deck_z=dz, dims=dims, checks=checks, box_kg=round(box_kg, 1),
                  box_kg_growth=round(box_kg_g, 1), by_group={k: round(v, 1) for k, v in by_group.items()}, mounts=ml,
                  bike_gaps={k: dict(measured=v["measured_mm"], governing=v["governing"]) for k, v in gaps.items()},
                  timings=model.timings)
    return garage, model

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
    """UGR-03: a steel crossmember under a track row carries a strap's breaking load at any of its anchors (R24). The
    crossmember spans between Toyota's two brackets at its station and runs on outboard of them to the walls. The
    vertical part of the breaking load bends it: simply supported between the brackets, or as a cantilever outboard.
    The capacity is AS 4100's 0.9 fy Ze, with Ze the plastic modulus of the compact RHS laid flat."""
    lc = next(c for c in prj.checks if c.id == "UGR-01").restraint["lc_kg"]
    f_kn = 2 * lc * G / 1000                          # AS/NZS 4380: a strap's breaking force is at least twice its LC
    brackets = [bb for bb in (b.shape.bounding_box() for i, b in model.built.items() if b.inst.ref == "C1" and i[3] in "16")]
    yb = sum(abs(bb.center().Y) for bb in brackets) / len(brackets)
    worst = None
    for iid, s in model.built.items():
        sp = s.inst.special.get("strap")
        if not sp:
            continue
        pts = s.info["points"]
        ends = [(pts[0], pts[1]), (pts[-1], pts[-2])] if sp["point"] == "rear_wheel" else [(pts[1], pts[0])]
        for anchor, towards in ends:
            d = [towards[i] - anchor[i] for i in range(3)]
            cz = abs(d[2]) / math.sqrt(sum(v * v for v in d))
            y = abs(anchor[1])
            lever = y - yb if y > yb else (yb - anchor[1]) * (yb + anchor[1]) / (2 * yb)
            m = f_kn * cz * lever / 1000                  # kN m
            if worst is None or m > worst["m"]:
                worst = dict(m=m, strap=iid, y=anchor[1], cz=cz, lever=lever, outboard=y > yb)
    b, h, t, fy = P.get("steel_w"), P.get("steel_h"), P.get("steel_t"), P.get("steel_fy")
    s_mm3 = rhs_plastic_modulus(b, h, t)
    cap = 0.9 * fy * s_mm3 / 1e6                          # kN m
    u = worst["m"] / cap
    where = "outboard of" if worst["outboard"] else "between"
    return _row("UGR-03", "Steel crossmember carries a strap's breaking load at its worst anchor", "fail", "<= 1.00",
                round(u, 3), round(1 - u, 3), u <= 1.0, f"{worst['strap']} anchor at Y {worst['y']:.0f}, {where} the brackets",
                f"{f_kn:.1f} kN breaking load x {worst['cz']:.2f} vertical x {worst['lever']:.0f} mm = {worst['m']:.2f} kN m, against "
                f"0.9 x {fy:.0f} MPa x {s_mm3:,.0f} mm3 = {cap:.2f} kN m for the RHS {b:g} x {h:g} x {t:g} laid flat. Brackets at Y +/-{yb:.0f}",
                "R24: an anchor withstands its strap's breaking load (NTC guide p. 201), so the crossmember under it must too. "
                "AS 4100 clause 5.1: the section is compact, so Ze is the plastic modulus.", unit="")


def _extent(model, P, x0, dz, skip_parts=()) -> dict:
    """Outside extent of the box in the ute frame, as it travels: everything but the loading view and the context. With
    skip_parts=("U-FLARE",) it is the body's extent without the rear tub flares (UTE-09's body limit, decision H19)."""
    shapes = [b.shape for b in model.built.values()
              if not b.inst.check_only and b.inst.display != "loading_only" and b.inst.group not in ("context", "bikes")
              and b.inst.part not in skip_parts]
    bb = Compound(children=shapes).bounding_box()
    return dict(x0=bb.min.X + x0, x1=bb.max.X + x0, y0=bb.min.Y, y1=bb.max.Y, z0=bb.min.Z + dz, z1=bb.max.Z + dz)


def mount_loads(lines: list[dict], P, limits: dict) -> dict:
    """Vertical and horizontal loads on Toyota's deck mount brackets from the box and everything in it, with growth.

    The box is taken as rigid on six pairs of brackets. Vertical reactions vary linearly along the ute (the least
    squares share of a rigid body on equal supports). Report 03's factored cases: braking 1.6 g forward, cornering
    1.0 g sideways, each with gravity, and a net 1.0 g upward. The firm front pairs carry all of the horizontal load,
    two M12 8.8 bolts per bracket. Each compliant rear bracket has one M12 8.8 bolt.
    """
    x0 = P.get("module_x0")
    xs = [P.get(f"mount{i}_x") + x0 for i in range(1, 7)]
    firm = [True, True, False, False, False, False]
    bolts = [2 if f else 1 for f in firm]
    carried = [ln for ln in lines if set(ln["cases"]) & {"UC2"}]
    M = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) for ln in carried)
    xc = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) * ln["x"] for ln in carried) / M
    zc = sum(ln["kg"] * (1 + GROWTH[ln["maturity"]]) * ln["z"] for ln in carried) / M
    z_if = P.get("frame_top_z")                         # bracket flange top, level with the rail top
    h = zc - z_if
    W = M * G / 1000                                    # kN
    n = len(xs)
    xb = sum(xs) / n
    S = sum((x - xb) ** 2 for x in xs)
    # bolt line to bolt line across the ute: the mounts' centres either side, on Toyota's brackets
    b_track = 2 * P.get("runner_y1") + P.get("mount_dy")

    def vertical(Wz, Fx):
        """Upward reaction per station (kN) for a downward load Wz at xc and a forward force Fx at height h."""
        a = Wz / n
        b = (Wz * (xc - xb) - Fx * h) / S
        return [a + b * (x - xb) for x in xs]

    # Each case: station reactions R, horizontal loads, and the roll couple's vertical force per bracket (cornering,
    # shared equally by the six stations, plus on the leeward side and minus on the windward side).
    cases = {}
    fb = 0.8 * 2.0 * W
    cases["braking"] = dict(R=vertical(W, fb), shear_x=fb, shear_y=0.0, roll=0.0, sides=(("each", 0),))
    fl = 0.5 * 2.0 * W
    cases["cornering"] = dict(R=vertical(W, 0.0), shear_x=0.0, shear_y=fl, roll=fl * h / b_track / n,
                              sides=(("windward", -1), ("leeward", 1)))
    cases["upward"] = dict(R=[-r for r in vertical(W, 0.0)], shear_x=0.0, shear_y=0.0, roll=0.0, sides=(("each", 0),))
    nt, vf = limits["m12_tension_kn"], limits["m12_shear_kn"]
    firm_bolts = 2 * sum(b for b, f in zip(bolts, firm) if f)       # two brackets per station
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
                r = dict(case=cname, station=i + 1, x=round(x), dx_axle=round(x - P.get("rear_axle_x")), mount="firm" if firm[i] else "compliant",
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
    body_ext = _extent(model, P, x0, dz, skip_parts=("U-FLARE",))
    tub_h = P.get("tub_top")
    checks.append(_row("UGD-01", "Wheel tubs no more than 100 mm above the floor, so the lower floor works", "fail",
                       f"<= {lim['tub_height_max_mm']:.0f} mm", round(tub_h, 1), round(lim["tub_height_max_mm"] - tub_h, 1),
                       tub_h <= lim["tub_height_max_mm"], "tub top over the tyre at full bump",
                       f"tub top {tub_h:.1f} mm above the floor: tyre top at full bump {P.get('wheel_z') + P.get('rear_bump') + P.get('tyre_d') / 2 + dz:.1f} mm "
                       f"above the ground, plus 25 mm and the 3 mm plate, against the floor at {dz:.0f} mm",
                       "Report 17 section 6.4: take the lower floor if the Lovells kit's bump travel keeps the tubs at or under 100 mm, "
                       "otherwise the flat deck at about 1,080 mm.", unit="mm"))
    mass_lim = lim["box_mass_max_kg"]
    checks.append(_row("UGB-01", "Box empty, with its restraint, ramp, winch and security, lighter than report 17's 440 kg", "fail",
                       f"< {mass_lim:.0f} kg", round(box_kg, 1), round(mass_lim - box_kg, 1), box_kg < mass_lim, "box mass, no growth",
                       f"{box_kg:.1f} kg, {box_kg_g:.1f} kg with growth. " + ", ".join(f"{g} {v:.1f} kg" for g, v in sorted(by_group.items())),
                       "The decision log asks for a box lighter than report 17's 440 kg.", unit="kg"))
    ml = mount_loads(lines, P, lim)
    w = ml["worst"]
    checks.append(_row("UGM-01", "Deck mount bolts within M12 8.8 design capacity, combined tension and shear", "fail",
                       "<= 1.00", w["interaction"], round(1 - w["interaction"], 4), w["interaction"] <= 1.0,
                       f"station {w['station']} ({w['mount']}, {w['dx_axle']:+d} mm from the rear axle), {w['case']}",
                       f"worst {w['interaction']:.3f}: {w['bolt_tension_kn']:.1f} kN tension and {w['bolt_shear_kn']:.1f} kN shear per bolt "
                       f"against {lim['m12_tension_kn']:.1f} kN and {lim['m12_shear_kn']:.1f} kN. {ml['mass_kg']:.0f} kg with growth, "
                       f"centre of gravity {ml['h_mm']:.0f} mm above the brackets",
                       "AS 4100 clause 9.3 design capacities for one M12 property class 8.8 bolt with the threads in the shear plane. "
                       "Report 03's factored cases. Toyota's bracket capacity is not published, so the engineer checks it with the loads of UGM-02.",
                       mounts=ml))
    checks.append(_row("UGM-02", "Deck mount bracket loads for the engineer (reported)", "report", "reported",
                       ml["max_tension_kn"], None, True, "largest uplift and largest downward load on one bracket",
                       f"largest uplift {ml['max_tension_kn']:.1f} kN, largest downward load {ml['max_down_kn']:.1f} kN, "
                       f"fore and aft shear {ml['firm_bolt_shear_kn']:.1f} kN per firm bolt in braking",
                       "Toyota publishes no capacity for its deck mount brackets. The engineer confirms them.", unit="kN"))
    res = next(c for c in checks if c["id"] == "UGR-01")["restraint"]
    kn = res["worst"]["worst_kgf"] * G / 1000
    ad = lim["anchor_design_kn"]
    checks.append(_row("UGR-02", f"Worst anchor load within the {ad:g} kN each anchor is designed for", "fail",
                       f"<= {ad:g} kN", round(kn, 2), round(ad - kn, 2),
                       kn <= ad, f"{res['worst']['strap']} {res['worst']['worst_case']}",
                       f"{kn:.2f} kN at the worst strap's anchor, which reaches the frame through the steel crossmember",
                       "An anchor withstands its strap's breaking load (NTC Load Restraint Guide 2018 p. 201, report 03): "
                       f"{ad:g} kN for the LC 500 kg straps (R24).", unit="kN"))
    checks.append(crossmember_check(prj, model, P))
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
                outside_h=round(P.get("top_z"), 1), inside_l=P.get("garage_length"), inside_w=P.get("interior_width"), inside_h=P.get("ceiling_z"),
                opening_w=P.get("door_y1") - P.get("door_y0"), opening_h=P.get("door_h"), deck_z=dz, top_z=round(dz + P.get("top_z"), 1),
                tub_h=round(tub_h, 1), tuareg_y=P.get("tuareg_y"), st_y=P.get("st_y"), bike_spacing=P.get("bike_spacing"),
                ramp_deg=round(ang, 2), ramp_deg_laden=round(ang_l, 2))
    garage = dict(lines=lines, box_extent=ext, body_extent=body_ext, module_x0=x0, deck_z=dz, dims=dims, checks=checks, box_kg=round(box_kg, 1),
                  box_kg_growth=round(box_kg_g, 1), by_group={k: round(v, 1) for k, v in by_group.items()}, mounts=ml,
                  bike_gaps={k: dict(measured=v["measured_mm"], governing=v["governing"]) for k, v in gaps.items()},
                  timings=model.timings)
    return garage, model

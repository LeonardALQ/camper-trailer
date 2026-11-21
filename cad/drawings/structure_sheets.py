"""CT-104 structural load paths and body mounts (A3, third angle), for the home trailer (TRAILER.md revision J): how the
heavy items reach the chassis, with their masses with growth and the design load cases, and the 32 body mounts.

The loads are the layout's lines (data/assemblies/trailer.yaml) grouped by the way they bear: the battery plinth with
the washer and dryer, the kitchen tower, the bench, the lift bed at night, the split's outdoor unit, the partition with
what hangs on it, the tanks and the drawbar box. The factors are the body's design cases (report 02, cad/body.py):
3 g down (LC2), 0.8 g braking along (LC3) and 0.5 g across (LC4).
"""
from __future__ import annotations

import re
import time

from . import sheet as S
from .home_common import Proj, arrow_line, ctx, label_in, stamp, textblock, title, wrap, wtable, write

G = 9.81
GROUPS = [
    ("Battery plinth, washer and dryer", ("EL-01", "EL-02", "EL-03", "LA-14F", "LA-02", "LA-14", "LA-11P"),
     "Four feet bolt through the floor on 100 x 100 mm spreaders into the kerb raiser and the outrigger at X 4,362"),
    ("Kitchen tower, Combi, fridge, oven, RESPA", ("LA-11T", "LA-03", "LA-05", "LA-13", "VE-04", "VE-05"),
     "Base bolted to the road raiser and the outrigger at X 3,462. Top tied to the wall's insert strip"),
    ("Bench, freezer, hob, sink and pump", ("LA-11B", "LA-06", "LA-07A", "LA-07B", "LA-07D", "WS-01"),
     "Base on floor inserts over the road raiser. Back tied to the road wall's insert strip"),
    ("Lift bed at night, two people", ("LB-01", "LB-02", "LB-03", "LB-04", "LB-04M", "LB-05", "LB-06"), "bed"),
    ("Split outdoor unit and its cradle", ("AC-02", "AC-03", "AC-04"), "cradle"),
    ("Partition, board, inverter, indoor unit", ("WR-03", "LA-11E", "EL-04", "EL-05", "EL-06", "AC-01", "WR-09"),
     "Bonded to the tray upstand, both walls and the ceiling, a diaphragm across the body at X 5,195"),
    ("Fresh tanks at the travel limit", ("UF-01", "UF-01R", "UF-03"),
     "Angle bearers on 10 mm rubber bolted to the XT crossmembers, padded stainless straps"),
    ("Grey tank, full", ("UF-08", "UF-08W", "UF-09"),
     "Angle bearers between the XT rear shock and rear crossmembers, strapped up to the grey-bay crossmember"),
    ("Drawbar box, generators and fuel", ("DX-01", "GS-01", "GS-02", "GS-04", "PL-03A"),
     "Brackets across the drawbar members at X 1,150 to 1,470"),
]


def _paths(bd: dict, chk: dict) -> dict:
    """The load paths that follow the body data (data/body/body.yaml), so the sheet cannot fall behind it."""
    st, cr = bd["panels"]["wall"]["stiffener"], bd["cradle"]
    m = st["name"].split(" 6060")[0]
    return dict(bed=(f"Four rails screwed through the inner skin into {m} hardpoints on it, full height in the side walls (LB-06). "
                     "The walls carry it to the floor joiners"),
                cradle=(f"{cr['bolts']} {cr['bolt'].split(' on ')[0]}s in the rear wall's insert strip hold the cradle to the wall. "
                        f"{cr['stays']['n']} {cr['stays']['name'].split(' 6060')[0]} stays (AC-04) carry its weight to the rear crossmember "
                        f"and outrigger (BDY-21 {chk['BDY-21']['measured']:.2f})"))


def _group_mass(rep, ids, water_l=0.0):
    m, mz = 0.0, 0.0
    for s in rep["schedule"]:
        if s["id"] in ids or s["iid"] in ids:
            kg = s["mass_with_growth_kg"] if s["load"] != "grey" else s["mass_kg"]
            if s["load"] == "water":
                continue
            m += kg
            mz += kg * (s["cog"][2] if s["cog"] else 0)
    return m, (mz / m if m else 0.0)


def ct104(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    rep, res, V, lay, chk = C["rep"], C["res"], C["V"], C["day"], C["chk"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    hb = V["half_bw"]
    # ---- plan: the chassis under the floor, the heavy footprints, the hard points and the 32 body mounts
    pr = Proj(sh, "plan", k, 34.0, 200.0, ref=(V["body_x0"], -hb, 0))
    pr.box((V["body_x0"], -hb, 0, V["body_x1"], hb, 0), "thick")
    for b in lay.blocks:
        if b.system == "chassis" and b.box is not None and b.box[3] > V["body_x0"] - 1:
            pr.box(b.box, "thin")
    heavy = {"EL-02": "PLINTH", "LA-11T": "TOWER", "LA-11B": "BENCH", "WR-03": "", "AC-03": "OUTDOOR UNIT", "UF-01": "FRESH",
             "UF-01R": "FRESH", "UF-08": "GREY TANK", "LB-04.1": "", "LB-04.2": "", "LB-04.3": "", "LB-04.4": ""}
    for iid, t in heavy.items():
        b = lay.find(iid)
        r = pr.fill(b.box, "light")
        sh.rect(*r, "medium")
        if t:
            label_in(sh, r, t, 1.3, 1.0)
    # hard points (layout study section 6): the plinth's and the tower's bolts into the raisers and outriggers
    hp = [(V["plinth_x0"] + 25, -V["rail_c"], "H1"), (V["plinth_x0"] + V["plinth_l"] - 25, -V["rail_c"], "H2"),
          (lay.chassis.station_x(next(s for s in lay.chassis.stations if s["id"] == "XT centre")), -900, "H3"),
          (V["bed_x1"] + 60, V["rail_c"], "H5"),
          (lay.chassis.station_x(next(s for s in lay.chassis.stations if s["id"] == "XT front hinge")), 880, "H6")]
    for x, y, t in hp:
        p = pr.p(x, y)
        sh.path([(p[0], p[1] + 1.4), (p[0] - 1.2, p[1] - 0.8), (p[0] + 1.2, p[1] - 0.8)], "fill", closed=True)
        sh.text(p[0] + 1.5, p[1] + 0.6, t, 1.2, bold=True)
    # the plinth's fourth foot: no member under it (open point)
    xo = V["plinth_x0"] + V["plinth_l"] - 25
    p = pr.p(xo, -900)
    sh.path([(p[0], p[1] + 1.4), (p[0] - 1.2, p[1] - 0.8), (p[0] + 1.2, p[1] - 0.8)], "fail", closed=True)
    sh.text(p[0] + 1.5, p[1] + 0.6, "H4", 1.2, bold=True, color="#c00")
    n = 0
    tip = res.get("mounted") or {}
    oy_tip = 1145.0
    for st in lay.chassis.stations:
        x = lay.chassis.station_x(st)
        for y in (-oy_tip, -V["rail_c"], V["rail_c"], oy_tip):
            q = pr.p(x, y)
            sh.circle(q[0], q[1], 0.8, "medium")
            n += 1
        q = pr.p(x, hb)
        sh.text(q[0], q[1] + 1.2, f"{x:.0f}", 1.15, "middle")
    sh.text(34, 200 + 2 * hb / k + 5.0, "PLAN UNDER THE FLOOR, FRONT LEFT, ROAD SIDE UP: CHASSIS, HEAVY FOOTPRINTS, HARD POINTS AND MOUNTS", 2.0, bold=True)
    # ---- kerb-side elevation with the load paths
    ve = Proj(sh, "kerb", k, 34.0, 112.0, ref=(V["body_x0"], 0, V["rail_underside_z"]))
    ve.box((V["body_x0"], 0, V["floor_underside_z"], V["body_x1"], 0, V["roof_top_z"]), "thick")
    ve.fill((V["body_x0"], 0, V["floor_underside_z"], V["body_x1"], 0, V["floor_z"]), "shade")
    for iid in ("RL-K", "RS-K"):
        ve.fill(lay.find(iid).box, "light")
        ve.box(lay.find(iid).box, "thin")
    for st in lay.chassis.stations:
        x = lay.chassis.station_x(st)
        ve.box((x, 0, V["rail_underside_z"], x + 50, 0, V["floor_underside_z"]), "medium")
    fz = V["floor_z"]
    paths = [("EL-02", "LA-14", "PLINTH"), ("LA-11T", None, "TOWER"), ("AC-03", None, "OUTDOOR UNIT")]
    for iid, top, t in paths:
        b = lay.find(iid).box
        z1 = lay.find(top).box[5] if top else b[5]
        r = ve.fill((b[0], 0, b[2], b[3], 0, z1), "light")
        sh.rect(*r, "medium")
        label_in(sh, r, t, 1.3, 1.0)
    for iid in ("LB-03", "LB-01"):
        b = lay.find(iid).box
        ve.box((b[0], 0, b[2], b[3], 0, b[5]), "medium")
    for iid in ("LB-04.2", "LB-04.4"):
        b = lay.find(iid).box
        ve.fill((b[0], 0, b[2], b[3], 0, b[5]), "shade")
    for iid in ("UF-01", "UF-01R", "UF-08"):
        b = lay.find(iid).box
        r = ve.box((b[0], 0, b[2], b[3], 0, b[5]), "medium")
        label_in(sh, r, "GREY" if iid == "UF-08" else "FRESH", 1.2, 1.0)
    wr = lay.find("WR-03").box
    ve.fill((wr[0], 0, fz, wr[3], 0, V["ceiling_z"]), "shade")
    # arrows: the plinth and tower down to the chassis, the bed into the walls, the outdoor unit into the rear wall
    pl = lay.find("EL-02").box
    tw_ = lay.find("LA-11T").box
    for x in (pl[0] + 120, pl[3] - 120):
        arrow_line(sh, ve.p(x, 0, fz + 150), ve.p(x, 0, V["rail_top_z"]), "medium")
    arrow_line(sh, ve.p((tw_[0] + tw_[3]) / 2, 0, fz + 150), ve.p((tw_[0] + tw_[3]) / 2, 0, V["rail_top_z"]), "medium")
    for iid in ("LB-04.2", "LB-04.4"):
        b = lay.find(iid).box
        arrow_line(sh, ve.p(b[0] - 220, 0, lay.find("LB-03").box[2] - 120), ve.p(b[0], 0, lay.find("LB-03").box[2] - 120), "medium")
    ac = lay.find("AC-03").box
    arrow_line(sh, ve.p(ac[3] - 60, 0, (ac[2] + ac[5]) / 2), ve.p(V["body_x1"], 0, (ac[2] + ac[5]) / 2), "medium")
    sh.text(34, ve.p(0, 0, V["roof_top_z"])[1] + 3.0, "KERB-SIDE ELEVATION: THE LOAD PATHS (ARROWS), PARTITION SHADED", 2.0, bold=True)
    ew = res["end_wall"]
    sh.text(ve.p(V["body_x1"], 0, 0)[0] - 1, ve.p(0, 0, fz + 1100)[1], f"REAR WALL DIAPHRAGM, BDY-20 {ew['util']:.3f}", 1.2, "end")
    # ---- right column: the loads and their paths
    yb = title(sh, dwg, reg, "MASSES WITH GROWTH FROM THE MASS SCHEDULE (TB-11).", "SEE CT-101, CT-201 AND CT-301")
    water = next(c for c in rep["cases"] if c["id"] == "TC2")["water_l"]
    rows = []
    bed_night = None
    ins = next((i for i in res["inserts"] if i["id"] == "INS-01"), None)
    if ins:
        mm = re.search(r"(\d+) kg bed", ins["case"])
        bed_night = float(mm.group(1)) if mm else None
    from ..body import load_data
    bd = load_data()
    named = _paths(bd, chk)
    for name, ids, path in GROUPS:
        path = named.get(path, path)
        m, z = _group_mass(rep, ids)
        if name.startswith("Fresh"):
            m += water
        if name.startswith("Lift bed") and bed_night:
            m = bed_night
        rows.append([name, f"{m:.0f}", f"{z:.0f}" if z else "-", f"{3 * m * G / 1000:.2f}", f"{0.8 * m * G / 1000:.2f}",
                     f"{0.5 * m * G / 1000:.2f}", path])
    y = wtable(sh, 230, yb - 6, [("LOAD", 32), ("kg +GR", 11), ("CoG Z", 10), ("3 g DOWN kN", 13), ("0.8 g kN", 12), ("0.5 g kN", 12),
                                   ("PATH TO THE CHASSIS", 90)], rows, size=1.22,
               title="THE HEAVY LOADS AND HOW THEY BEAR (LC2, LC3, LC4)")
    m_ = res["mounts"]
    mrows = [[kk, f"{v['shear'] / 1000:.2f}", f"{v['tension'] / 1000:.2f}", v["note"]] for kk, v in m_["cases"].items()]
    y = wtable(sh, 230, y - 7, [("CASE", 12), ("SHEAR kN", 14), ("TENSION kN", 16), ("WORST BOLT, AND WHY", 138)], mrows, size=1.22,
               title=f"BODY MOUNTS: {m_['bolts']} x M12 8.8 INTO NUT PLATES, {m_['mass_kg']:.0f} kg OF BODY ON THEM ({m_['case']} AT THE ATM)")
    brows = []
    for cid in ("BDY-03", "BDY-04", "BDY-06", "BDY-10", "BDY-11", "BDY-14", "BDY-16", "BDY-19", "BDY-20", "LOC-04", "CHS-01", "CHS-04"):
        c = chk.get(cid)
        if not c:
            continue
        val = "" if c["measured"] is None else f"{c['measured']:.3g} {c['unit']}".strip()
        brows.append([cid, c["title"], c["limit"], val, (c["status"], "#000" if c["ok"] else "#c00")])
    y = wtable(sh, 230, y - 7, [("CHECK", 13), ("WHAT IT CHECKS", 95), ("LIMIT", 30), ("MODEL", 22), ("RESULT", 20)], brows, size=1.18,
               title="THE CHECKS ON THESE PATHS (CT-001, BODY.md, CHASSIS.md)")
    st = bd["panels"]["wall"]["stiffener"]
    st_name = st["name"].split(" 6060")[0]
    S.notes(sh, 22, 84, [
        "DATUM DIM-01. HARD POINTS H1 TO H6 ARE BOLTS THROUGH THE FLOOR ON 100 x 100 mm SPREADERS INTO A CHASSIS MEMBER, SO THE FLOOR'S "
        "CORE CARRIES NONE OF THESE LOADS (layout study section 6). CIRCLES: THE 32 BODY MOUNTS, FOUR AT EACH STATION (CT-301).",
        f"H4, OPEN POINT: THE PLINTH'S REAR OUTBOARD FOOT HAS NO MEMBER UNDER IT. THE MACHINE BASE ENDS AT X {lay.find('LA-14F').box[3]:,.0f} "
        f"AND THE XT REAR SHOCK OUTRIGGER STARTS AT X {next(s for s in lay.chassis.stations if s['id'] == 'XT rear shock')['x']:,.0f}. "
        "ADD A STUB CROSSMEMBER OR A BRACKET BEFORE THE FLOOR GOES ON.",
        f"THE LIFT BED'S RAILS (SOLID) SCREW THROUGH THE INNER SKIN INTO {st_name} ALUMINIUM HARDPOINTS, FULL HEIGHT AND BONDED TO THE INNER "
        f"SKIN AS THE PANELS ARE MADE (LB-06), SO EACH SCREW BITES {st['wall']:g} mm OF ALUMINIUM AND EACH HARDPOINT STIFFENS THE WALL. "
        f"{st['break']:g} mm OF XPS STAYS BEHIND EACH, SO NO METAL CROSSES THE CORE (BDY-22). IN TRAVEL THE INDEX PLUNGERS HOLD THE BED AT THE RAIL TOPS.",
        "THE REAR WALL WITH THE 625 x 1753 DOOR CUT-OUT IS THE BOX'S REAR DIAPHRAGM (BDY-20). THE PARTITION ADDS A SECOND ONE AT X 5,195.",
        f"THE SIDE WALLS' MEMBERS ON THE INNER SKIN, {st_name} (STIFFENERS BD-18, DOOR JAMB MEMBERS BD-19, BED HARDPOINTS LB-06), "
        f"HOLD THE WALL TO {chk['BDY-10']['measured']:.1f} mm IN REGION {bd['wind']['region']}'S 25-YEAR WIND (BDY-10).",
    ], size=1.45, width_chars=185)
    stamp(sh, 320, 74, "DRAFT, NOT FOR CONSTRUCTION UNTIL THE ENGINEER REVIEWS THE LOAD PATHS", 120)
    write(sh, dwg)
    return time.time() - t0

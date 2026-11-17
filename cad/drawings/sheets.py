"""Drawing sheets CT-401, CT-402 and CT-501 for the garage and bed module (A3, third angle).

Every plan uses the same orientation as CT-401, where the kerb-side section is the front view:
X (towards partition B) runs to the left, and the kerb side is at the bottom of the plan.
"""
from __future__ import annotations

import json
import math
import time

from build123d import Box, Compound, Keep, Plane, Pos

from ..build import BUILD, git_hash
from ..model.assembly import Model
from ..partsdb import Project
from . import sheet as S

OUT = BUILD / "drawings"


# ------------------------------------------------------------------ helpers
def _module_shapes(model, exclude_refs=(), only_refs=None):
    out = []
    for b in model.built.values():
        i = b.inst
        if i.check_only or i.display == "loading_only":
            continue
        if i.ref in exclude_refs or i.iid in exclude_refs:
            continue
        if only_refs is not None and i.ref not in only_refs and i.iid not in only_refs:
            continue
        out.append(b.shape)
    return out


def _leaves(shapes):
    out = []
    for s in shapes:
        if isinstance(s, Compound) and s.children:
            out.extend(_leaves(list(s.children)))
        else:
            out.append(s)
    return out


def _cut_faces(shapes, axis, value, tol=0.05):
    faces = []
    for s in shapes:
        for f in s.faces():
            bb = f.bounding_box()
            if abs(getattr(bb.min, axis) - value) < tol and abs(getattr(bb.max, axis) - value) < tol:
                faces.append(f)
    return faces


def _wire_pts(view, w):
    try:
        edges = w.order_edges()
    except Exception:
        edges = w.edges()
    pts = []
    for e in edges:
        us = [0, 1] if e.geom_type.name == "LINE" else [k / 16 for k in range(17)]
        ep = [view.p(v.X, v.Y, v.Z) for v in (e.position_at(u) for u in us)]
        if pts and math.dist(ep[-1], pts[-1]) < math.dist(ep[0], pts[-1]):
            ep = ep[::-1]
        pts.extend(ep)
    return pts


def _shade(sh, view, faces):
    for f in faces:
        loops = [_wire_pts(view, f.outer_wire())] + [_wire_pts(view, w) for w in f.inner_wires()]
        sh.multipath(loops, "shade")


def _clip(shapes, x0, x1, y0, y1, z0, z1):
    box = Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)
    out = []
    for s in shapes:
        bb = s.bounding_box()
        if bb.max.X < x0 or bb.min.X > x1 or bb.max.Y < y0 or bb.min.Y > y1 or bb.max.Z < z0 or bb.min.Z > z1:
            continue
        try:
            r = s & box
            if r is not None and r.volume > 1e-6:
                out.append(r)
        except Exception:
            pass
    return out


def _title(sh, dwg, reg, mass_note, scale, model_rev="A"):
    rev = dwg["revisions"][-1]
    S.title_block(
        sh, owner=reg["owner"], project=reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"],
        engineer="NOT REVIEWED" if dwg.get("structural") else "N/A", sheet_no=dwg["sheet"], sheets=reg["sheets_total"],
        size=dwg["size"], scale=scale, material="SEE PARTS LIST", mass_note=mass_note,
        model_ref=f"garage-bed.step (ASM-GB rev {model_rev})", git=git_hash())
    S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                               checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]])


def _bom_rows(bom, items):
    lines = {r["id"]: r for r in bom["lines"]}
    bikes = {b["id"]: b for b in bom["bikes"]}
    rows = []
    for item, pid, desc, qty in items:
        if pid in lines:
            r = lines[pid]
            mass, sup = f"{r['mass_kg']:.1f}", (r["maker"] or "")
            if r["maturity"] == "estimate":
                mass += " est."
        elif pid in bikes:
            mass, sup, pid = f"{bikes[pid]['mass_kg']:.0f}", "Payload (owner's bike)", bikes[pid]["part"]
        else:
            mass, sup = "-", ""
        rows.append(dict(item=item, part=pid, description=desc, qty=qty, mass=mass, supplier=sup))
    return rows


def _balloons(sh, specs):
    for lab, tip, centre in specs:
        S.balloon(sh, tip, centre, lab)


# ------------------------------------------------------------------ CT-401
def ct401(prj, model, bom, checks, reg, dwg):
    sh = S.Sheet()
    S.frame(sh)
    P = prj.P.values
    sc = 25.0
    t0 = time.time()
    hw, gl = P["half_width"], P["garage_length"]

    # ---- front view: section A-A just inside the kerb wall, looking towards the road side
    ycut = hw - 5
    cut2 = S.section(_leaves(_module_shapes(model, exclude_refs=("C3", "C4"))), Plane.XZ.offset(-ycut), keep=Keep.TOP)
    vE = S.View(sh, (0, 1, 0), (0, 0, 1), sc, ox=206.0, oy=52.0)
    vE.draw(cut2)
    _shade(sh, vE, _cut_faces(cut2, "Y", ycut))
    S.view_label(sh, 166, 21, "SECTION A-A, FROM THE KERB SIDE", sc)
    d0, d1 = vE.p(P["door_x0"], ycut, 0), vE.p(P["door_x1"], ycut, P["door_h"])
    sh.rect(d1[0], d0[1], d0[0], d1[1], "phantom")
    S.hdim(sh, d0[0], d1[1], d1[0], d1[1], 129.0, "1720 DOOR OPENING (X 40 TO 1760)")
    a0, b0 = vE.p(0, ycut, 0), vE.p(gl, ycut, 0)
    S.hdim(sh, a0[0], a0[1] - 1.5, b0[0], b0[1] - 1.5, 45.0, "1800 GARAGE")
    pt, ps = vE.p(P["tuareg_x"], ycut, 0), vE.p(P["st_x"], ycut, 0)
    for xc in (P["tuareg_x"], P["st_x"]):
        p0, p1 = vE.p(xc, ycut, -40), vE.p(xc, ycut, 1430)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    S.hdim(sh, a0[0], a0[1] - 1.5, pt[0], pt[1] - 1.5, 38.5, "560", ext=True)
    S.hdim(sh, pt[0], pt[1] - 1.5, ps[0], ps[1] - 1.5, 38.5, "760", ext=True)
    # heights on the partition A side (right of the view)
    zr = vE.p(-20, ycut, 0)[0]
    for z, lab, xd in ((P["door_h"], "1440", zr + 6), (P["beam_underside_z"], "1460", zr + 12), (P["ceiling_z"], "1800", zr + 18)):
        S.vdim(sh, zr, vE.p(0, ycut, 0)[1], zr, vE.p(0, ycut, z)[1], xd, lab)
    # cutting plane C-C on the elevation
    c0, c1 = vE.p(-140, ycut, 1000), vE.p(2000, ycut, 1000)
    S.cut_marker(sh, c1, c0, (0, -1), "C")

    # ---- plan: section C-C at Z 1000 looking down (above the front view)
    zcut = 1000.0
    cut3 = S.section(_leaves(_module_shapes(model, exclude_refs=("C5", "C4", "C7"))), Plane.XY.offset(zcut), keep=Keep.BOTTOM)
    vP = S.View(sh, (0, 0, 1), (0, -1, 0), sc, ox=206.0, oy=190.0)
    vP.draw(cut3)
    _shade(sh, vP, _cut_faces(cut3, "Z", zcut))
    S.view_label(sh, 166, 264, "SECTION C-C, PLAN AT Z 1000", sc)
    w0, w1 = vP.p(0, -hw, zcut), vP.p(0, hw, zcut)
    S.vdim(sh, w0[0], w0[1], w1[0], w1[1], w0[0] + 8, "2330")
    l0, l1 = vP.p(0, -hw, 0), vP.p(gl, -hw, 0)
    S.hdim(sh, l0[0], l0[1] + 1.4, l1[0], l1[1] + 1.4, l0[1] + 7.0, "1800")
    for yrow, lab in ((P["front_row_y"], "TRACK Y -915"), (P["rear_row_y"], "TRACK Y +883"), (0.0, "CL Y 0")):
        p0, p1 = vP.p(-80, yrow, 0), vP.p(gl + 60, yrow, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(113.0, p1[1] - 0.7, lab, 1.8, "end")
        sh.line(113.5, p1[1], p1[0], p1[1], "thin")
    for xc in (P["tuareg_x"], P["st_x"]):
        p0, p1 = vP.p(xc, -hw - 60, 0), vP.p(xc, hw + 60, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    sh.text(132.0, vP.p(0, -hw, 0)[1] + 0.6, "ROAD SIDE", 1.8, "end")
    sh.text(132.0, vP.p(0, hw, 0)[1] - 2.2, "KERB SIDE", 1.8, "end")
    o = vP.p(0, 0, 0)
    sh.circle(o[0], o[1], 1.3, "medium")
    sh.line(o[0] - 2.2, o[1], o[0] + 2.2, o[1], "thin")
    sh.line(o[0], o[1] - 2.2, o[0], o[1] + 2.2, "thin")
    S.leader(sh, (o[0] + 0.9, o[1] - 0.9), (o[0] + 6, o[1] - 12), "DATUM")
    # cutting planes on the plan
    S.cut_marker(sh, vP.p(1100, -hw - 30, 0), vP.p(1100, hw + 30, 0), (1, 0), "B")
    S.cut_marker(sh, vP.p(gl + 90, ycut, 0), vP.p(-110, ycut, 0), (0, 1), "A")

    # ---- section B-B looking at partition A (right column, above the parts list)
    xcut = 1100.0
    excl = ("ST", "13.ST-F+", "13.ST-F-", "13.ST-R+", "13.ST-R-", "13.ST-W", "14P", "C4", "C3", "18", "19")
    cut = S.section(_leaves(_module_shapes(model, exclude_refs=excl)), Plane.YZ.offset(xcut), keep=Keep.BOTTOM)
    vA = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=294.0, oy=170.0)
    vA.draw(cut)
    _shade(sh, vA, _cut_faces(cut, "X", xcut))
    S.view_label(sh, 294, 262, "SECTION B-B, LOOKING AT PARTITION A", sc)
    sh.text(294, 254.5, "STREET TRIPLE NOT SHOWN. CUT FACES SHADED.", 1.8, "middle")
    yl, yr = vA.p(0, -hw, 0), vA.p(0, hw, 0)
    S.hdim(sh, yl[0], yl[1] - 1.5, yr[0], yr[1] - 1.5, 163.0, "2330 INTERIOR")
    c0 = vA.p(0, 0, 0)
    pf, pr = vA.p(0, P["front_row_y"], 0), vA.p(0, P["rear_row_y"], 0)
    for p in (pf, pr, c0):
        sh.line(p[0], p[1] - 1, p[0], 155.5, "centre")
    S.hdim(sh, pf[0], 157, c0[0], 157, 157.0, "915", ext=False)
    S.hdim(sh, c0[0], 157, pr[0], 157, 157.0, "883", ext=False)
    levels = [(0, "0 FLOOR"), (P["beam_underside_z"], "1460 BEAM UNDERSIDE"), (P["deck_z"], "1510 DECK UNDERSIDE"),
              (P["froli_z"], "1530 DECK TOP"), (P["mattress_z"], "1573 FROLI TOP"),
              (P["mattress_z"] + P["mattress_t"], "1723 MATTRESS TOP"),
              (P["mattress_z"] + P["mattress_t"] + P["bedding_allowance"], "1773 BEDDING ALLOWANCE (27 SPARE)"),
              (P["ceiling_z"], "1800 CEILING, ROOF DOWN")]
    xr = yr[0] + 2
    ly = []
    for z, lab in levels:
        y = vA.p(0, 0, z)[1]
        ly.append(max(y, ly[-1] + 2.9) if ly else y)
    for (z, lab), yl_ in zip(levels, ly):
        y = vA.p(0, 0, z)[1]
        sh.line(xr, y, xr + 6, y, "thin")
        sh.line(xr + 6, y, xr + 9, yl_, "thin")
        sh.text(xr + 9.5, yl_ - 0.7, lab, 1.8)

    # ---- balloons
    _balloons(sh, [
        ("1", vP.p(-10, -300, 0), (224.0, 226.0)), ("TU", vP.p(560, 120, 0), (224.0, 212.0)),
        ("16", vP.p(15, 0, 0), (224.0, 199.0)), ("17", vP.p(70, 1080, 0), (224.0, 151.0)),
        ("ST", vP.p(1320, 140, 0), (124.0, 186.0)), ("2", vP.p(1810, -300, 0), (124.0, 214.0)),
        ("11", vP.p(1650, P["front_row_y"], 0), (124.0, 233.0)), ("18", vP.p(2030, 800, 0), (124.0, 169.0)),
        ("12", vP.p(1035, P["rear_row_y"], 0), (150.0, 148.5)),
        ("13", vP.p(1027, -800, 300), (154.0, 251.0)), ("15", vP.p(940, -1150, 0), (167.0, 251.0)),
        ("14", vP.p(560, -1100, 0), (180.0, 251.0)), ("10", vP.p(560, -900, 0), (193.0, 251.0)),
        ("3", vE.p(1810, ycut, 700), (100.0, 62.0)),
        ("9", vA.p(0, -800, 1650), (238.0, 238.0)), ("8", vA.p(0, -600, 1551), (238.0, 230.0)),
        ("7", vA.p(0, -1000, 1520), (238.0, 222.0)), ("6", vA.p(0, -932, 1485), (238.0, 214.0)),
        ("5", vA.p(0, -1150, 1490), (238.0, 206.0)),
    ])

    # ---- model check results (left)
    rows = []
    for r in checks:
        if r["type"] == "contact":
            val = f"{len([p for p in r['pairs'] if p['ok']])}/{len(r['pairs'])} touch"
        else:
            val = f"{r['measured_mm']:.1f}"
        sub = {"Aprilia Tuareg 660 Rally": " TU", "Triumph Street Triple 765": " ST"}.get(r["sub"], "")
        color = "#000" if r["ok"] else ("#c00" if r["severity"] == "fail" else "#b06000")
        rows.append([r["id"] + sub, r["limit"].replace(">= ", ">=").replace("touching, no overlap", "touching"),
                     (val, color), (r["status"], color)])
    S.table(sh, 22.0, 150.0, [("CHECK", 18), ("LIMIT", 26), ("MODEL", 16), ("RESULT", 22)], rows, size=1.7, row_h=3.2,
            title="MODEL CHECKS (mm)")
    _, starts = S.notes(sh, 22, 284, [
        "MODULE FRAME: X FROM PARTITION A'S INNER FACE TOWARDS PARTITION B, Y FROM THE CENTRELINE (+ TO THE KERB SIDE), Z FROM THE GARAGE FLOOR. "
        "THE PROJECT DATUM (DIM-01) NEEDS AN OFFSET, AND X CHANGES SIGN IF PARTITION B ENDS UP NEARER THE FRONT OF THE TRAILER.",
        "BIKES ARE ENVELOPES FROM research/05 SCALED TO THE OWNER'S FIGURES, MIRRORS FOLDED, FRONT WHEEL 25 UP IN THE CHOCK CRADLE (ESTIMATE).",
        "MEASURE BOTH BIKES IN A FULL-SIZE MOCK-UP BEFORE ORDERING PANELS (BUILD STEP S01).",
        "DOORWAY POSITION IN PARTITION B, VENTS, SENSORS, EXTINGUISHER AND THE LADDER'S POSITION ACROSS THE TRAILER ARE PLACEHOLDERS.",
    ], width_chars=62, size=1.8)
    S.rev_tag(sh, 98.0, starts[0] + 0.6, "B")
    # ---- revision B: the deck laps over partition B, and the owner-built ladder reaches the living-area floor
    tip = vE.p(2061, ycut, 760)
    S.leader(sh, tip, (104.0, 92.0), "A-01 OWNER-BUILT LADDER, 1580 LONG AT 15° (REV B).",
             ["RUBBER FEET ON THE LIVING-AREA FLOOR, TAKEN AT Z 0 (CLR-07)."], size=1.9)
    S.revision_cloud(sh, 108.0, 48.0, 137.5, 117.0, "B", tag_at="bl")
    items = [("TU", "TU", "Aprilia Tuareg 660 Rally (envelope)", "1"), ("ST", "ST", "Triumph Street Triple 765 (envelope)", "1"),
             ("1", "P-01", "Partition A, 20 honeycomb 2330x1800", "1"), ("2", "P-01", "Partition B, 700x1300 doorway", "1"),
             ("3", "P-01", "Door leaf, cut from partition B", "1"), ("5", "B-05", "Ledger, angle 40x40x3 6060-T5", "4 (8.26 m)"),
             ("6", "B-04", "Beam, RHS 50x25x2.5 6106-T6", "5 x 1800"), ("7", "B-03", "Deck, 20 honeycomb 1845x2330, laps B", "1"),
             ("8", "B-02", "Froli Star Mobil pack", "2"), ("9", "B-01", "Mattress 1530x2030x150", "1"),
             ("10", "G-01", "Condor SC-2000 chock", "2"), ("11", "G-02", "L-track row, recessed", "2 x 1800"),
             ("12", "G-03", "Double-stud track fitting", "12 + 2"), ("13", "G-05", "Ratchet strap 35 mm LC 1000 kg", "10"),
             ("14", "G-11", "Winch on quick-release plate", "1 + 2 plates"), ("15", "G-12", "Vent, 2 low and 1 high", "3"),
             ("16", "G-13", "Fume detector, 2 sensors", "1"), ("17", "G-14", "Extinguisher 2.5 kg ABE", "1"),
             ("18", "A-01", "Ladder, owner-built, SHS 25x1.6", "1 (1580 long)")]
    S.parts_list(sh, _bom_rows(bom, items), ybase=66.0, row_h=4.0, tags={"7": "B", "18": "B"})
    _title(sh, dwg, reg, f"MODULE {bom['totals']['module_empty']:.1f} kg EMPTY, {bom['with_bikes_kg']:.1f} kg WITH BIKES (TB-11).", sc,
           prj.assembly.revision)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-402
def ct402(prj, model, bom, checks, reg, dwg):
    sh = S.Sheet()
    S.frame(sh)
    P = prj.P.values
    sc = 20.0
    t0 = time.time()
    hw, gl = P["half_width"], P["garage_length"]
    cut = S.section(_leaves(_module_shapes(model, only_refs=("C1", "C2", "C3", "1", "2", "10", "11", "12"))),
                    Plane.XY.offset(400.0), keep=Keep.BOTTOM)
    v = S.View(sh, (0, 0, 1), (0, -1, 0), sc, ox=196.0, oy=164.0)
    # bikes as thin grey plan outlines, under the floor items
    for ref in ("TU", "ST"):
        v.draw(_leaves([model.built[ref].shape]), sty="grey")
    v.draw(cut)
    _shade(sh, v, _cut_faces(cut, "Z", 400.0))
    S.view_label(sh, 148, 268, "PLAN OF THE GARAGE FLOOR, ANCHOR LAYOUT", sc)
    sh.text(148, 260.5, "SECTION AT Z 400 LOOKING DOWN. BIKES SHOWN AS THIN GREY OUTLINES.", 1.8, "middle")
    anchors = sorted(((b.inst.iid.split(".", 1)[1], b.inst.at[0], b.inst.at[1]) for b in model.built.values()
                      if b.inst.part == "G-03"), key=lambda a: a[1])
    ytop = v.p(0, -hw - 35, 0)[1] + 4
    ybot = v.p(0, hw + 35, 0)[1] - 4
    for row_y, yline, up in ((P["front_row_y"], ytop + 6, True), (P["rear_row_y"], ybot - 6, False)):
        row = sorted([a for a in anchors if abs(a[2] - row_y) < 1], key=lambda a: v.p(a[1], a[2], 0)[0])
        last_x = -1e9
        for name, x, y in row:
            p = v.p(x, y, 0)
            sh.circle(p[0], p[1], 1.5, "medium")
            sh.line(p[0] - 2.4, p[1], p[0] + 2.4, p[1], "thin")
            # stagger labels that would overlap: jog the leader sideways near its end
            tx = max(p[0], last_x + 3.4)
            yj = yline - (3 if up else -3)
            sh.line(p[0], p[1] + (2 if up else -2), p[0], yj, "thin")
            sh.line(p[0], yj, tx, yline, "thin")
            sh.text(tx + 0.8, yline + (0.8 if up else -0.8), f"{x:.0f}", 2.0, "start" if up else "end", rot=-90)
            last_x = tx
    o = v.p(0, 0, 0)
    for yline, up in ((ytop + 6, True), (ybot - 6, False)):
        sh.line(o[0], o[1], o[0], yline, "thin")
        sh.text(o[0] + 0.8, yline + (0.8 if up else -0.8), "0", 2.0, "start" if up else "end", rot=-90)
    sh.text(o[0] + 4, ytop + 18, "X FROM PARTITION A'S FACE", 1.8, "end")
    xl = v.p(gl + 60, 0, 0)[0] - 4
    for yv, lab in ((P["front_row_y"], "-915"), (0.0, "0 CL"), (P["rear_row_y"], "+883")):
        p = v.p(gl + 40, yv, 0)
        sh.line(p[0], p[1], xl, p[1], "thin")
        sh.text(xl - 0.8, p[1] - 0.7, "Y " + lab, 2.0, "end")
    for yv in (P["front_row_y"], P["rear_row_y"], 0.0):
        p0, p1 = v.p(-60, yv, 0), v.p(gl + 40, yv, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    sh.circle(o[0], o[1], 1.3, "medium")
    S.leader(sh, (o[0] + 0.9, o[1] + 0.9), (o[0] + 7, o[1] + 12), "DATUM X0 Y0")
    sh.text(98.0, v.p(0, -hw, 0)[1] + 0.6, "ROAD SIDE", 1.9, "end")
    sh.text(98.0, v.p(0, hw, 0)[1] - 2.2, "KERB SIDE (DOOR)", 1.9, "end")
    for xc in (P["tuareg_x"], P["st_x"]):
        p0, p1 = v.p(xc, -hw, 0), v.p(xc, hw, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")

    # anchor table (right column)
    use = {"F": "front pair", "R": "rear pair", "W": "rear-wheel strap"}
    side = {"L": "bike's left", "R": "bike's right"}
    rows = []
    for name, x, y in sorted(anchors, key=lambda a: (a[0][:2], "FRW".index(a[0][3]), a[0][4])):
        bike, pos = name.split("-")
        rows.append([name, ("Tuareg " if bike == "TU" else "Street Triple ") + use[pos[0]] + ", " + side[pos[1]],
                     f"{x:.0f}", f"{y:+.0f}"])
    S.table(sh, 232.0, 264.0, [("ANCHOR", 16), ("STRAP", 100), ("X", 16), ("Y", 16)], rows, size=1.8, row_h=3.4,
            title="ANCHOR POSITIONS FROM THE DATUM (CENTRE OF EACH FITTING)")
    # detail D
    dx0, dy0, k = 300.0, 172.0, 2.0
    tw, th = P["track_w"], P["track_h"]
    S.view_label(sh, 320, 206, "DETAIL D: TRACK IN ITS RECESS", k)
    sh.text(320, 198.5, "SCHEMATIC, FLOOR PANEL ASSUMED 30 THICK", 1.8, "middle")
    sh.rect(dx0 - 20, dy0 - 15, dx0 + 60, dy0, "medium")
    S.hatch_rect(sh, dx0 - 20, dy0 - 15, dx0 + 20 - tw / k, dy0, 1.4)
    S.hatch_rect(sh, dx0 + 20 + tw / k, dy0 - 15, dx0 + 60, dy0, 1.4)
    sh.fillrect(dx0 + 20 - tw / k, dy0 - 15, dx0 + 20 + tw / k, dy0)
    sh.rect(dx0 + 20 - tw / k, dy0 - 15, dx0 + 20 + tw / k, dy0 - 15 + 0.01, "thin")
    sh.rect(dx0 + 20 - tw / (2 * k), dy0 - th / k, dx0 + 20 + tw / (2 * k), dy0, "thick")
    sh.rect(dx0 + 20 - tw / k, dy0 - th / k, dx0 + 20 + tw / k, dy0, "thick")
    sh.rect(dx0 + 20 - 2.5, dy0 - 3, dx0 + 20 + 2.5, dy0, "medium")
    sh.line(dx0 + 20, dy0 + 5, dx0 + 20, dy0 - 22, "centre")
    S.hdim(sh, dx0 + 20 - tw / k, dy0, dx0 + 20 + tw / k, dy0, dy0 + 7, "34.5")
    S.vdim(sh, dx0 + 20 + tw / k, dy0, dx0 + 20 + tw / k, dy0 - th / k, dx0 + 48, "13.7")
    S.leader(sh, (dx0 + 20, dy0 - 12), (dx0 + 44, dy0 - 22), "M8 A4-70 THROUGH-BOLT, CRUSH TUBE",
             ["TO THE STEEL ANCHOR RAIL BELOW", "(CHASSIS SCOPE)"])
    S.leader(sh, (dx0 + 20 - tw / k + 2, dy0 - 13), (dx0 - 4, dy0 - 24), "BONDED HARDPOINT STRIP", ["IN PLACE OF THE CORE (G-04)"])
    S.leader(sh, (dx0 - 10, dy0 - 1), (dx0 - 14, dy0 + 10), "FLOOR SKIN, COATED (G-08)")
    items = [("10", "G-01", "Condor SC-2000 chock with trailer adapter", "2"), ("11", "G-02", "L-track row, recessed, 1800 long", "2"),
             ("12", "G-03", "Double-stud L-track fitting", "12 + 2 spare"), ("-", "G-04", "M8 through-bolts, crush tubes, hardpoints", "1 set"),
             ("-", "F-07", "A4-70 bolts, nylon washers and sleeves", "1 lot"), ("-", "F-03", "Plexus MA310 for the hardpoints", "1 lot")]
    S.parts_list(sh, _bom_rows(bom, items), ybase=66.0, row_h=4.2)
    S.notes(sh, 22, 64, [
        "TRACK: KINEDYNE SERIES L MEDIUM DUTY WITH FLANGES (G-02), RECESSED WITH ITS TOP FLUSH WITH THE FLOOR. TWO ROWS ALONG X, EACH 1800 LONG.",
        "BOLT PITCH: M8 A4-70 THROUGH-BOLTS AT 150 mm PITCH OR LESS, WITH CRUSH TUBES, THROUGH A BONDED HARDPOINT STRIP TO THE STEEL RAIL BELOW.",
        "DESIGN LOAD: EVERY ANCHOR AND ITS FLOOR FIXING IS DESIGNED FOR 20 kN, THE BREAKING LOAD OF AN LC 1,000 kg STRAP (NTC GUIDE p. 201).",
        "FITTINGS: DOUBLE-STUD FITTINGS (G-03), BREAK 22.2 kN. HOLD EACH X WITHIN 50 mm. Y MAY GROW BUT NOT SHRINK (research/03 SECTION 4).",
        "CHOCKS: EACH ADAPTER BOLTS THROUGH TO STEEL ON ITS BIKE CENTRELINE (TUAREG X 560, STREET TRIPLE X 1320), NOSE AT THE ROAD-SIDE WALL. TORQUE VALUES ARE NOT SET YET.",
    ], width_chars=125, size=1.8)
    _title(sh, dwg, reg, "ANCHOR DESIGN LOAD 20 kN EACH, 12 ANCHORS IN USE.", sc, prj.assembly.revision)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-501
def ct501(prj, model, bom, checks, reg, dwg):
    sh = S.Sheet()
    S.frame(sh)
    P = prj.P.values
    t0 = time.time()
    hw, gl = P["half_width"], P["garage_length"]
    # ---- beam layout plan, deck and bedding removed
    sc = 20.0
    v = S.View(sh, (0, 0, 1), (0, -1, 0), sc, ox=196.0, oy=196.0)
    v.draw(_leaves(_module_shapes(model, only_refs=("1", "2", "5", "6"))))
    S.view_label(sh, 150, 272, "BEAM LAYOUT PLAN, DECK AND BEDDING REMOVED", sc)
    xl = v.p(gl + 20, 0, 0)[0] - 3
    for yb in P["beam_y"]:
        p0, p1 = v.p(-40, yb, 0), v.p(gl + 20, yb, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.line(p1[0], p1[1], xl, p1[1], "thin")
        sh.text(xl - 0.8, p1[1] - 0.7, f"Y {yb:+.0f}", 2.0, "end")
    a, b = v.p(0, -hw, 0), v.p(gl, -hw, 0)
    S.hdim(sh, a[0], a[1], b[0], b[1], a[1] + 8, "1800 BEAM LENGTH, BETWEEN PARTITION FACES")
    w0, w1 = v.p(0, -hw, 0), v.p(0, hw, 0)
    S.vdim(sh, w0[0], w0[1], w1[0], w1[1], w0[0] + 10, "2330")
    for yb0, yb1 in zip(P["beam_y"], P["beam_y"][1:]):
        p0, p1 = v.p(gl * 0.62, yb0, 0), v.p(gl * 0.62, yb1, 0)
        S.vdim(sh, p0[0], p0[1], p1[0], p1[1], p0[0], f"{yb1 - yb0:.0f}", ext=False)
    S.cut_marker(sh, v.p(900, -hw - 50, 0), v.p(900, hw + 50, 0), (1, 0), "E")
    sh.text(96.0, v.p(0, -hw, 0)[1] + 0.6, "ROAD SIDE", 1.9, "end")
    sh.text(104.0, v.p(0, hw, 0)[1] - 2.2, "KERB SIDE", 1.9, "end")
    _balloons(sh, [("6", v.p(30, 466, 0), (214.0, 182.0)), ("5", v.p(20, -700, 0), (214.0, 238.0)),
                   ("5", v.p(1000, 1145, 0), (150.0, 128.0)), ("1", v.p(-10, 300, 0), (214.0, 166.0)),
                   ("2", v.p(1810, -1000, 0), (102.0, 252.0))])

    # ---- section E-E: bed stack at X 900, kerb end, 1:5
    sc2 = 5.0
    y0, y1, z0, z1 = hw - 430, hw + 36, 1395.0, 1815.0
    shapes = _leaves(_module_shapes(model, only_refs=("1", "5", "6", "7", "8", "9", "C2", "C3", "C5")))
    cut = S.section(shapes, Plane.YZ.offset(900.0), keep=Keep.BOTTOM)
    det = _clip(cut, -30, 900.5, y0, y1, z0, z1)
    vS = S.View(sh, (1, 0, 0), (0, 0, 1), sc2, ox=318.0, oy=160.0, anchor=(900, hw, 1600))
    vS.draw(det)
    _shade(sh, vS, _cut_faces(det, "X", 900.0))
    S.view_label(sh, 300, 222, "SECTION E-E, BED STACK AT X 900", sc2)
    sh.text(300, 214.5, "KERB-SIDE END. CUT FACES SHADED.", 1.8, "middle")
    xr = vS.p(0, y1, 0)[0] + 3
    levels = [(P["beam_underside_z"], "1460 BEAM UNDERSIDE"), (P["deck_z"], "1510 DECK UNDERSIDE"),
              (P["froli_z"], "1530 DECK TOP"), (P["mattress_z"], "1573 FROLI TOP"),
              (P["mattress_z"] + P["mattress_t"], "1723 MATTRESS TOP"),
              (P["mattress_z"] + P["mattress_t"] + P["bedding_allowance"], "1773 BEDDING ALLOWANCE"),
              (P["ceiling_z"], "1800 CEILING, ROOF DOWN")]
    ly = []
    for z, lab in levels:
        y = vS.p(0, 0, z)[1]
        ly.append(max(y, ly[-1] + 3.0) if ly else y)
    for (z, lab), yy in zip(levels, ly):
        y = vS.p(0, 0, z)[1]
        sh.line(xr, y, xr + 5, y, "thin")
        sh.line(xr + 5, y, xr + 8, yy, "thin")
        sh.text(xr + 8.5, yy - 0.7, lab, 1.8)
    zb = P["mattress_z"] + P["mattress_t"] + P["bedding_allowance"]
    sh.line(vS.p(0, y0, zb)[0], vS.p(0, y0, zb)[1], vS.p(0, y1, zb)[0], vS.p(0, y1, zb)[1], "phantom")
    sb = vS.p(0, 932 - 12.5, P["beam_underside_z"])
    S.hdim(sh, sb[0], sb[1], vS.p(0, 932 + 12.5, 0)[0], sb[1], sb[1] - 6, "25")
    _balloons(sh, [("6", vS.p(0, 932, 1470), (241.0, 209.0)), ("7", vS.p(0, 1050, 1520), (252.0, 209.0)),
                   ("8", vS.p(0, 1000, 1550), (263.0, 209.0)), ("9", vS.p(0, 850, 1650), (274.0, 209.0)),
                   ("5", vS.p(0, 1150, 1490), (300.0, 209.0))])

    # ---- detail F: ledger at partition A, section at Y 0, 1:2
    sc3 = 2.0
    shapes = _leaves(_module_shapes(model, only_refs=("1", "5", "6", "7")))
    cutF = S.section(shapes, Plane.XZ.offset(0.0), keep=Keep.BOTTOM)
    detF = _clip(cutF, -30, 120, -0.5, 300, 1405, 1545)
    vD = S.View(sh, (0, -1, 0), (0, 0, 1), sc3, ox=92.0, oy=62.0, anchor=(0, 0, 1460))
    vD.draw(detF)
    _shade(sh, vD, _cut_faces(detF, "Y", 0.0))
    S.view_label(sh, 110, 22, "DETAIL F: LEDGER AT PARTITION A, SECTION AT Y 0", sc3)
    S.leader(sh, vD.p(25, 0, 1458.5), (160.0, 40.0), "LEDGER 40x40x3 6060-T5 (B-05). SHELF TOP AT Z 1460,",
             ["VERTICAL LEG HANGS BELOW. BONDED (F-01) AND", "RIVETED (F-05) TO PARTITION A."])
    S.leader(sh, vD.p(100, 0, 1490), (160.0, 66.0), "BEAM RHS 50x25x2.5 (B-04) ON EDGE.",
             ["END ABUTS PARTITION A. RIVETED", "DOWN THROUGH THE SHELF."])
    S.leader(sh, vD.p(110, 0, 1525), (160.0, 98.0), "DECK 20 HONEYCOMB (B-03),", ["BONDED AND RIVETED"])
    S.leader(sh, vD.p(-10, 0, 1415), (106.0, 31.0), "PARTITION A, 20 HONEYCOMB (P-01)")
    a0, a1 = vD.p(0, 0, 1420), vD.p(0, 0, 1460)
    S.vdim(sh, vD.p(3, 0, 1420)[0], a0[1], vD.p(3, 0, 1460)[0], a1[1], vD.p(0, 0, 0)[0] + 14, "40")
    s0, s1 = vD.p(0, 0, 1460), vD.p(40, 0, 1460)
    S.hdim(sh, s0[0], vD.p(0, 0, 1420)[1], s1[0], vD.p(0, 0, 1420)[1], vD.p(0, 0, 1408)[1], "40")
    z0p, z1p = vD.p(140, 0, 1460), vD.p(140, 0, 1510)
    S.vdim(sh, vD.p(120, 0, 1460)[0], z0p[1], vD.p(120, 0, 1510)[0], z1p[1], vD.p(124, 0, 0)[0], "50")

    # ---- detail G (revision B): the deck laps over the top edge of partition B, section at Y 0, 1:2
    xb = P["garage_length"]
    dl = P["deck_length"]
    shapes = _leaves(_module_shapes(model, only_refs=("2", "4.B-top", "5.on-B", "6.3", "7")))
    cutG = S.section(shapes, Plane.XZ.offset(0.0), keep=Keep.BOTTOM)
    detG = _clip(cutG, xb - 48, xb + 70, -0.5, 300, 1415, 1550)
    vG = S.View(sh, (0, -1, 0), (0, 0, 1), sc3, ox=50.0, oy=187.5, anchor=(xb, 0, P["deck_z"]))
    vG.draw(detG)
    _shade(sh, vG, _cut_faces(detG, "Y", 0.0))
    sh.text(55.0, 133.0, "DETAIL G: DECK LAP AT B", 3.0, "middle", bold=True)
    sh.text(55.0, 129.2, "SECTION AT Y 0, SCALE 1:2", 2.1, "middle")
    sh.text(55.0, 125.8, "GARAGE LEFT, LIVING AREA RIGHT", 1.8, "middle")
    top = P["froli_z"]
    p_b, p_e = vG.p(xb, 0, top), vG.p(dl, 0, top)
    S.hdim(sh, p_b[0], p_b[1], p_e[0], p_e[1], p_b[1] + 6, f"{dl - xb:.0f}")
    _balloons(sh, [("7", vG.p(xb - 15, 0, 1520), (41.0, 221.0)), ("6", vG.p(xb - 38, 0, 1508.8), (30.0, 221.0)),
                   ("2", vG.p(xb + 10, 0, 1470), (80.0, 213.0)), ("4", vG.p(xb + 34, 0, 1509), (80.0, 202.0)),
                   ("5", vG.p(xb - 1.5, 0, 1435), (30.0, 146.0))])
    S.revision_cloud(sh, 23.0, 122.0, 86.5, 227.0, "B", tag_at="tr")

    items = [("1", "P-01", "Partition A, 20 honeycomb 2330x1800", "1"), ("2", "P-01", "Partition B, 700x1300 doorway", "1"),
             ("4", "P-02", "Cleat, angle 25x25x1.6 (detail G)", "19.9 m in all"),
             ("5", "B-05", "Ledger, angle 40x40x3 6060-T5", "4 (8.26 m)"), ("6", "B-04", "Beam, RHS 50x25x2.5 6106-T6", "5 x 1800"),
             ("7", "B-03", "Deck, 20 honeycomb 1845x2330, laps B", "1 (4.30 m2)"), ("8", "B-02", "Froli Star Mobil pack", "2"),
             ("9", "B-01", "Mattress 1530x2030x150", "1"), ("-", "F-01", "Sikaflex-252 structural adhesive", "1.4 l"),
             ("-", "F-02", "Sikaflex-221 seam sealant", "0.3 l"), ("-", "F-05", "Monobolt rivets BAPV-06-04, -08-06", "about 60")]
    S.parts_list(sh, _bom_rows(bom, items), ybase=66.0, row_h=4.2, tags={"4": "B", "7": "B"})
    _, starts = S.notes(sh, 232, 260, [
        "BEAMS ON EDGE AT Y -932, -466, 0, 466 AND 932. EACH END SITS ON A PARTITION LEDGER SHELF AND ABUTS THE PARTITION FACE.",
        "THE SIDE-WALL LEDGERS CARRY THE DECK EDGES WITH THEIR SHELF TOP AT Z 1510.",
        "DECK: 1845 x 2330 FROM X 0, LAPPING OVER THE TOP EDGE OF PARTITION B AND ITS TOP CLEAT (DETAIL G). BONDED (SIKAFLEX-252) TO THE BEAMS, LEDGERS AND "
        "PARTITION B, RIVETED, AND SEALED ALL ROUND (SIKAFLEX-221) AS THE FUEL-SMELL BARRIER (GAR-02). HOLD POINT BEFORE CLOSING.",
        "research/04 ESTIMATES ABOUT 5 mm DEFLECTION UNDER 255 kg SPREAD OVER THE BED. THE ENGINEER CONFIRMS THE BEAM SIZE AND LOAD CASES.",
    ], width_chars=108, size=1.8)
    S.rev_tag(sh, 227.5, starts[2] + 0.6, "B")
    bed = sum(r["mass_kg"] for r in bom["lines"] if r["group"] == "bed")
    _title(sh, dwg, reg, f"BED LINES B-01 TO B-05 {bed:.1f} kg (TB-11).", sc, prj.assembly.revision)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


def main(only: list[str] | None = None):
    import sys
    import yaml
    t0 = time.time()
    prj = Project()
    model = Model(prj, include_check_only=False)
    bom = json.loads((BUILD / "bom" / "bom.json").read_text())
    bom["with_bikes_kg"] = bom["totals"]["module_empty"] + sum(b["mass_kg"] for b in bom["bikes"])
    cp = BUILD / "checks" / "checks.json"
    checks = json.loads(cp.read_text())["results"] if cp.exists() else []
    reg = yaml.safe_load((prj.root / "data" / "drawings.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    only = only or [a for a in sys.argv[2:] if a.startswith("CT-")]
    tm = {}
    fns = {"CT-401": ct401, "CT-402": ct402, "CT-501": ct501}
    for dwg in reg["drawings"]:
        if only and dwg["number"] not in only:
            continue
        tm[dwg["number"]] = round(fns[dwg["number"]](prj, model, bom, checks, reg, dwg), 1)
        print(f"{dwg['number']} written in {tm[dwg['number']]} s", flush=True)
    register = [dict(number=d["number"], title=d["title"], subtitle=d["subtitle"], revision=d["revisions"][-1]["rev"],
                     status=d["status"], date=str(d["revisions"][-1]["date"]), scale=d["scale"], size=d["size"],
                     sheet=d["sheet"]) for d in reg["drawings"]]
    (OUT / "register.json").write_text(json.dumps(dict(drawings=register, timings=tm, total_s=round(time.time() - t0, 1)), indent=1))

"""Drawing sheets CT-401, CT-402 and CT-501 for the garage and bed module (A3, third angle).

Every plan uses the same orientation as CT-401, where the kerb-side section is the front view:
X (rearward, towards the rear door) runs to the right, and the kerb side is at the bottom of the plan.
Every view shows the module as seen, because DIM-01 is right-handed (Y positive to the road side).
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


def _bags_box(model, margin=30.0):
    """Plan extent of the Tuareg's panniers (module frame), for the revision C clouds."""
    bb = model.built["TU-BAGS"].shape.bounding_box()
    return bb.min.X - margin, bb.min.Y - margin, bb.max.X + margin, bb.max.Y + margin


def _placement():
    """Where the module sits in the project datum, from the trailer layout (build/trailer/trailer.json)."""
    ch = json.loads((BUILD / "trailer" / "trailer.json").read_text())["chassis"]
    return ch["module_x0"], ch["floor_z"]


def _bed_sag(checks):
    r = next((c for c in checks if c["id"] == "BED-01"), None)
    return f"{r['measured_mm']:.1f} mm" if r else "NOT CHECKED"


def _q(bom, pid):
    return next(r["qty"] for r in bom["lines"] if r["id"] == pid)


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
def _checks_table(sh, checks, x, y):
    rows = []
    for r in checks:
        if r["type"] == "contact":
            val = f"{len([p for p in r['pairs'] if p['ok']])}/{len(r['pairs'])} touch"
        elif r["type"] == "restraint":
            val = f"{r['measured_mm']:.0f} kgf"
        else:
            val = f"{r['measured_mm']:.1f}"
        sub = {"Aprilia Tuareg 660 Rally": " TU", "Triumph Street Triple 765": " ST"}.get(r["sub"], "")
        color = "#000" if r["ok"] else ("#c00" if r["severity"] == "fail" else "#b06000")
        rows.append([r["id"] + sub, r["limit"].replace(">= ", ">=").replace("<= ", "<=").replace("touching, no overlap", "touching"),
                     (val, color), (r["status"], color)])
    return S.table(sh, x, y, [("CHECK", 15), ("LIMIT", 26), ("MODEL", 14), ("RESULT", 16)], rows, size=1.7, row_h=3.1,
                   title="MODEL CHECKS (mm UNLESS STATED)")


def ct401(prj, model, bom, checks, reg, dwg):
    sh = S.Sheet()
    S.frame(sh)
    P = prj.P.values
    sc = 25.0
    t0 = time.time()
    hw, gl, wt = P["half_width"], P["garage_length"], P["wall_t"]
    ty, sy = P["tuareg_y"], P["st_y"]
    x0 = 206.0 - gl / sc                       # sheet x of partition A's rear face on the plan and section A-A

    # ---- front view: section A-A just inside the kerb wall, looking towards the road side. X runs to the right.
    ycut = -(hw - 5)
    cut2 = S.section(_leaves(_module_shapes(model, exclude_refs=("C3", "C9"))), Plane.XZ.offset(-ycut), keep=Keep.BOTTOM)
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=x0, oy=52.0)
    vE.draw(cut2)
    _shade(sh, vE, _cut_faces(cut2, "Y", ycut))
    S.view_label(sh, 160, 21, "SECTION A-A, FROM THE KERB SIDE", sc)
    a0, b0 = vE.p(0, ycut, 0), vE.p(gl, ycut, 0)
    S.hdim(sh, a0[0], a0[1] - 1.5, b0[0], b0[1] - 1.5, 45.0, f"{gl:.0f} GARAGE, PARTITION A TO THE REAR WALL")
    lx0, lx1 = vE.p(P["locker_x0"], ycut, 0), vE.p(gl, ycut, 0)
    S.hdim(sh, lx0[0], lx0[1], lx1[0], lx1[1], 39.0, f"{P['locker_l']:.0f} {'GAS LOCKER' if P['lpg'] else 'STOWAGE'}", ext=False)
    gx0, gx1 = vE.p(P["fuel_x0"], ycut, 0), vE.p(P["gen_x0"] + P["gen_l"], ycut, 0)
    S.hdim(sh, gx0[0], gx0[1], gx1[0], gx1[1], 39.0, "FUEL, GENERATOR", ext=False)
    # heights at partition A (left of the view) and at the rear wall (right)
    zr = vE.p(-20, ycut, 0)[0]
    for z, lab, xd in ((P["partition_a_h"], f"{P['partition_a_h']:.0f}", zr - 6), (P["ceiling_z"], f"{P['ceiling_z']:.0f}", zr - 12)):
        S.vdim(sh, zr, vE.p(0, ycut, 0)[1], zr, vE.p(0, ycut, z)[1], xd, lab)
    zl = vE.p(gl + wt, ycut, 0)[0]
    for z, lab, xd in ((P["door_h"], f"{P['door_h']:.0f} DOOR", zl + 9), (P["beam_underside_z"], f"{P['beam_underside_z']:.0f} BEAMS", zl + 17)):
        S.vdim(sh, zl, vE.p(0, ycut, 0)[1], zl, vE.p(0, ycut, z)[1], xd, lab)
    # cutting plane C-C on the elevation
    c0, c1 = vE.p(-140, ycut, 1000), vE.p(gl + 50, ycut, 1000)
    S.cut_marker(sh, c1, c0, (0, -1), "C")

    # ---- plan: section C-C at Z 1000 looking down (above the front view). X to the right, kerb side at the bottom
    zcut = 1000.0
    cut3 = S.section(_leaves(_module_shapes(model, exclude_refs=("C5", "C4", "C7"))), Plane.XY.offset(zcut), keep=Keep.BOTTOM)
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=x0, oy=190.0)
    vP.draw(cut3)
    _shade(sh, vP, _cut_faces(cut3, "Z", zcut))
    S.view_label(sh, 160, 264, "SECTION C-C, PLAN AT Z 1000", sc)
    w0, w1 = vP.p(0, hw, zcut), vP.p(0, -hw, zcut)
    S.vdim(sh, w0[0], w0[1], w1[0], w1[1], w0[0] - 8, f"{P['interior_width']:.0f}")
    l0, l1 = vP.p(0, hw, 0), vP.p(gl, hw, 0)
    S.hdim(sh, l0[0], l0[1] + 1.4, l1[0], l1[1] + 1.4, l0[1] + 7.0, f"{gl:.0f}")
    # rear door opening on the rear wall (right end)
    d0, d1 = vP.p(gl + wt, P["door_y0"], 0), vP.p(gl + wt, P["door_y1"], 0)
    S.vdim(sh, d0[0], d0[1], d1[0], d1[1], d0[0] + 6, f"{P['door_y1'] - P['door_y0']:.0f} REAR DOOR")
    for yc, lab in ((ty, f"TU CL Y {ty:+.0f}"), (sy, f"ST CL Y {sy:+.0f}")):
        p0, p1 = vP.p(-80, yc, 0), vP.p(gl + 60, yc, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(p0[0] - 1, p0[1] + 0.6, lab, 1.7, "end")
    for xr, lab in ((P["front_row_x"], f"TRACK X {P['front_row_x']:.0f}"), (P["rear_row_x"], f"TRACK X {P['rear_row_x']:.0f}")):
        p0, p1 = vP.p(xr, hw + 40, 0), vP.p(xr, -hw - 40, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(p0[0], p0[1] + 1.2, lab, 1.7, "middle")
    sh.text(vP.p(gl + 60, 0, 0)[0], vP.p(0, hw, 0)[1] + 0.8, "ROAD SIDE", 1.8)
    sh.text(vP.p(gl + 60, 0, 0)[0], vP.p(0, -hw, 0)[1] - 2.4, "KERB SIDE", 1.8)
    o = vP.p(0, 0, 0)
    sh.circle(o[0], o[1], 1.3, "medium")
    sh.line(o[0] - 2.2, o[1], o[0] + 2.2, o[1], "thin")
    sh.line(o[0], o[1] - 2.2, o[0], o[1] + 2.2, "thin")
    S.leader(sh, (o[0] - 0.9, o[1] - 0.9), (o[0] - 6, o[1] - 12), "DATUM")
    S.cut_marker(sh, vP.p(1100, hw + 30, 0), vP.p(1100, -hw - 30, 0), (-1, 0), "B")
    S.cut_marker(sh, vP.p(gl + 90, ycut, 0), vP.p(-110, ycut, 0), (0, 1), "A")

    # ---- section B-B looking forward at partition A (right column, above the parts list)
    xcut = 1100.0
    excl = ("C4", "C8", "18", "19", "C10")
    cut = S.section(_leaves(_module_shapes(model, exclude_refs=excl)), Plane.YZ.offset(xcut), keep=Keep.BOTTOM)
    vA = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=294.0, oy=161.0)
    vA.draw(cut)
    _shade(sh, vA, _cut_faces(cut, "X", xcut))
    S.view_label(sh, 294, 243.5, "SECTION B-B, LOOKING FORWARD AT PARTITION A", sc)
    sh.text(294, 236.3, "CUT FACES SHADED.", 1.8, "middle")
    yl, yr = vA.p(0, -hw, 0), vA.p(0, hw, 0)
    S.hdim(sh, yl[0], yl[1] - 1.5, yr[0], yr[1] - 1.5, 154.0, "2330 INTERIOR")
    pt_, ps_ = vA.p(0, ty, 0), vA.p(0, sy, 0)
    for pp in (pt_, ps_):
        sh.line(pp[0], pp[1] - 1, pp[0], 147.5, "centre")
    S.hdim(sh, ps_[0], 149, pt_[0], 149, 149.0, f"{P['bike_spacing']:.0f}", ext=False)
    S.hdim(sh, pt_[0], 149, yr[0], 149, 149.0, f"{hw - ty:.0f}", ext=False)
    levels = [(0, "0 FLOOR"), (P["beam_underside_z"], f"{P['beam_underside_z']:.0f} BEAM UNDERSIDE"), (P["deck_z"], f"{P['deck_z']:.0f} DECK UNDERSIDE"),
              (P["froli_z"], f"{P['froli_z']:.0f} DECK TOP"), (P["mattress_z"], f"{P['mattress_z']:.0f} FROLI TOP"),
              (P["mattress_z"] + P["mattress_t"], f"{P['mattress_z'] + P['mattress_t']:.0f} MATTRESS TOP"),
              (P["mattress_z"] + P["mattress_t"] + P["bedding_allowance"], f"{P['mattress_z'] + P['mattress_t'] + P['bedding_allowance']:.0f} BEDDING (27 SPARE)"),
              (P["ceiling_z"], f"{P['ceiling_z']:.0f} CEILING, ROOF DOWN")]
    xr_ = yr[0] + 2
    ly = []
    for z, lab in levels:
        y = vA.p(0, 0, z)[1]
        ly.append(max(y, ly[-1] + 2.9) if ly else y)
    for (z, lab), yl_ in zip(levels, ly):
        y = vA.p(0, 0, z)[1]
        sh.line(xr_, y, xr_ + 6, y, "thin")
        sh.line(xr_ + 6, y, xr_ + 9, yl_, "thin")
        sh.text(xr_ + 9.5, yl_ - 0.7, lab, 1.8)

    # ---- balloons
    _balloons(sh, [
        ("TU", vP.p(1158, ty, 0), (190.8, 236.0)), ("ST", vP.p(1040, sy, 0), (190.8, 146.0)),
        ("1", vP.p(-10, 900, 0), (104.8, 238.0)),
    ] + [("21", vP.p(P["locker_x0"] + 300, -hw + 150, 0), (214.8, 150.0))] * bool(P["lpg"]) + [
        ("17", vP.p(P["garage_length"] - 110, -hw + 160, 0), (214.8, 162.0)),
        ("13", vP.p(1603, ty + 150, 0), (168.8, 246.0)), ("12", vP.p(P["front_row_x"], ty + 450, 0), (128.8, 246.0)),
        ("10", vP.p(300, ty, 0), (142.8, 246.0)), ("14", vP.p(60, sy, 0), (98.0, 166.0)),
        ("15", vP.p(400, -hw, 0), (128.8, 136.0)), ("16", vP.p(0, (ty + sy) / 2, 0), (104.8, 200.0)),
        ("18", vP.p(-300, P["ladder_y"], 0), (86.0, 161.0)),
        ("9", vA.p(0, -800, 1650), (238.0, 233.0)), ("8", vA.p(0, -600, 1551), (238.0, 225.0)),
        ("7", vA.p(0, -1100, 1520), (238.0, 217.0)), ("5", vA.p(0, -1150, 1440), (238.0, 201.0)),
    ])
    # beams are not cut by B-B (they run across the trailer), so the beam balloon goes on the elevation
    _balloons(sh, [("6", vE.p(P["beam_x"][2], ycut, 1485), (168.8, 100.0))])

    _checks_table(sh, checks, 22.0, 150.0)
    mx0, mz0 = _placement()
    _, starts = S.notes(sh, 22, 284, [
        "MODULE FRAME: X FROM PARTITION A'S REAR FACE TOWARDS THE REAR DOOR, Y FROM THE CENTRELINE (+ TO THE ROAD SIDE), Z FROM THE GARAGE FLOOR. "
        f"IN THE PROJECT DATUM (DIM-01, CT-001) MODULE X 0 IS AT X {mx0:.0f} AND Z 0 AT Z {mz0:.0f}, AXES PARALLEL.",
        "REVISION D: GARAGE AT THE BACK WITH A TOP-HINGED REAR DOOR. BIKES ALONG THE TRAILER, NOSES IN CHOCKS AGAINST PARTITION A. WHOLE SHEET REDRAWN.",
        "BIKES ARE ENVELOPES FROM research/05 SCALED TO THE OWNER'S FIGURES, MIRRORS FOLDED, FRONT WHEEL 25 UP IN THE CHOCK CRADLE (ESTIMATE). TUAREG PANNIERS ON.",
        ("GAS LOCKER: TWO 9 kg CYLINDERS, OUTSIDE ACCESS ONLY BY THE KERB HATCH, SEALED TO THE GARAGE, 25 mm DRAIN TO 500 BELOW THE FLOOR (report 02 5.2)."
         if P["lpg"] else "NO LPG (OWNER OPTION, report 13): INDUCTION COOKING. THE KERB-SIDE REAR CORNER IS STOWAGE, THE 380 mm WALL BESIDE THE DOOR STAYS."),
        "MEASURE BOTH BIKES IN A FULL-SIZE MOCK-UP BEFORE ORDERING PANELS (BUILD STEP S01). VENTS, SENSORS AND THE EXTINGUISHER ARE PLACEHOLDERS.",
    ], width_chars=64, size=1.8)
    S.rev_tag(sh, 98.0, starts[1] + 0.6, "D")
    S.rev_tag(sh, 104.0, starts[0] + 0.6, "F")
    items = [("TU", "TU", "Aprilia Tuareg 660 Rally (envelope)", "1"), ("ST", "ST", "Triumph Street Triple 765 (envelope)", "1"),
             ("1", "P-01", f"Partition A, 20 honeycomb 2330x{P['partition_a_h']:.0f}", "1"),
             ("5", "B-05", "Ledger, angle 40x40x3 6060-T5", f"4 ({_q(bom, 'B-05'):.2f} m)"),
             ("6", "B-04", "Beam, SHS 50x50x3 6060-T5, across", f"5 x {P['interior_width']:.0f}"),
             ("7", "B-03", f"Deck, 20 honeycomb {P['deck_length']:.0f}x2330, laps A", "1"),
             ("8", "B-02", "Froli Star Mobil pack", "2"), ("9", "B-01", "Mattress 1530x2030x150, across", "1"),
             ("10", "G-01", "Condor SC-2000 chock", "2"), ("11", "G-02", "L-track rows, recessed", f"3 ({_q(bom, 'G-02'):.2f} m)"),
             ("12", "G-03", "Double-stud track fitting", "16 + 2"), ("13", "G-05", "Ratchet strap 35 mm LC 1000 kg", "12"),
             ("14", "G-11", "Winch on quick-release plate", "1 + 2 plates"), ("15", "G-12", "Vent, 2 low and 1 high", "3"),
             ("16", "G-13", "Fume detector, 2 sensors", "1"), ("17", "G-14", "Extinguisher 2.5 kg ABE", "1"),
             ("18", "A-01", "Ladder, owner-built, SHS 25x1.6", "1 (1580 long)")] + [("21", "G-15", "Gas locker 760x380x690", "1")] * bool(P["lpg"])
    S.parts_list(sh, _bom_rows(bom, items), ybase=66.0, row_h=3.9, tags={"1": "D", "6": "D", "7": "D", "11": "D", "21": "D"})
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
    cut = S.section(_leaves(_module_shapes(model, only_refs=("C1", "C2", "C3", "C8", "1", "10", "11", "12", "21"))),
                    Plane.XY.offset(400.0), keep=Keep.BOTTOM)
    v = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=200.0 - gl / sc, oy=170.0)
    for ref in ("TU", "ST", "C11", "C12", "C10"):
        v.draw(_leaves([model.built[ref].shape]), sty="grey")
    v.draw(cut)
    _shade(sh, v, _cut_faces(cut, "Z", 400.0))
    S.view_label(sh, 140, 272, "PLAN OF THE GARAGE FLOOR, ANCHOR LAYOUT", sc)
    sh.text(140, 264.5, "SECTION AT Z 400 LOOKING DOWN. BIKES AND STOWAGE SHOWN AS THIN GREY OUTLINES.", 1.8, "middle")
    anchors = [(b.inst.iid.split(".", 1)[1], b.inst.at[0], b.inst.at[1]) for b in model.built.values() if b.inst.part == "G-03"]
    # each cross row: Y values of its fittings as ordinates, front row to the left of the plan, rear row to the right
    for row_x, side in ((P["front_row_x"], -1), (P["rear_row_x"], 1)):
        row = sorted([a for a in anchors if abs(a[1] - row_x) < 1], key=lambda a: -v.p(a[1], a[2], 0)[1])
        xt = (v.p(gl + 60, 0, 0)[0] + 6) if side > 0 else (v.p(-60, 0, 0)[0] - 6)
        last = 1e9
        for name, x, y in row:
            p = v.p(x, y, 0)
            sh.circle(p[0], p[1], 1.5, "medium")
            sh.line(p[0], p[1] - 2.4, p[0], p[1] + 2.4, "thin")
            ty_ = min(p[1], last - 3.2)
            sh.line(p[0] + side * 2, p[1], xt - side * 4, ty_, "thin")
            sh.text(xt, ty_ - 0.7, f"{name} Y {y:+.0f}", 1.8, "start" if side > 0 else "end")
            last = ty_
    for xr in (P["front_row_x"], P["rear_row_x"]):
        p0, p1 = v.p(xr, hw + 40, 0), v.p(xr, -hw - 40, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(p0[0], p0[1] + 1.4, f"X {xr:.0f}", 2.0, "middle")
    ys = P["stow_row_y"]
    p0, p1 = v.p(P["stow_row_x0"] - 40, ys, 0), v.p(P["stow_row_x1"] + 40, ys, 0)
    sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    sh.text(p0[0] + 1.5, p0[1] - 3.3, f"STOWAGE ROW Y {ys:+.0f}", 1.8)
    sh.text(p0[0] + 1.5, p0[1] - 6.1, f"X {P['stow_row_x0']:.0f} TO {P['stow_row_x1']:.0f}", 1.8)
    for yc in (P["tuareg_y"], P["st_y"]):
        p0, p1 = v.p(-40, yc, 0), v.p(gl + 40, yc, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    o = v.p(0, 0, 0)
    sh.circle(o[0], o[1], 1.3, "medium")
    S.leader(sh, (o[0] - 0.9, o[1] - 0.9), (o[0] - 7, o[1] - 6), "DATUM X0 Y0")
    sh.text(v.p(gl, 0, 0)[0], v.p(0, hw, 0)[1] + 4.5, "ROAD SIDE", 1.9, "middle")
    sh.text(v.p(gl / 2, 0, 0)[0], v.p(0, -hw, 0)[1] - 5.5, "KERB SIDE", 1.9, "middle")
    sh.text(v.p(gl, 0, 0)[0], v.p(0, -hw, 0)[1] - 5.5, "REAR DOOR END", 1.9, "middle")
    sh.text(v.p(0, 0, 0)[0], v.p(0, -hw, 0)[1] - 5.5, "PARTITION A", 1.9, "middle")

    # anchor table (right column)
    use = {"F": "front pair", "R": "rear pair", "W": "rear-wheel strap"}
    side = {"L": "bike's left", "R": "bike's right"}
    rows = []
    for name, x, y in sorted(anchors, key=lambda a: a[0]):
        if name.startswith("GS"):
            rows.append([name, "Generator and jerry cans, kerb strip", f"{x:.0f}", f"{y:+.0f}"])
            continue
        bike, pos = name.split("-")
        rows.append([name, ("Tuareg " if bike == "TU" else "Street Triple ") + use[pos[0]] + ", " + side[pos[1]],
                     f"{x:.0f}", f"{y:+.0f}"])
    S.table(sh, 232.0, 253.0, [("ANCHOR", 16), ("STRAP", 100), ("X", 16), ("Y", 16)], rows, size=1.8, row_h=3.2,
            title="ANCHOR POSITIONS FROM THE DATUM (CENTRE OF EACH FITTING)")
    # strap loads (RES-01)
    res = next((c.get("restraint") for c in checks if c["id"] == "RES-01"), None)
    if res:
        lab = {"TU-F": "Tuareg front pair", "TU-R": "Tuareg rear pair", "ST-F": "Street Triple front pair", "ST-R": "Street Triple rear pair"}
        rows, seen = [], set()
        for r in res["rows"]:
            k = r["strap"].split(".")[1][:4]
            if k in seen:
                continue
            seen.add(k)
            rows.append([lab[k], f"{r['sideways']:.0f}", f"{r['braking']:.0f}", f"{r['rearward']:.0f}", f"{r['upward']:.0f}", f"{r['worst_kgf']:.0f}"])
        S.table(sh, 232.0, 191.0, [("STRAP (RES-01)", 52), ("SIDEWAYS", 20), ("BRAKING", 20), ("REARWARD", 20), ("UPWARD", 20), ("WORST", 16)],
                rows, size=1.8, row_h=3.3, title="STRAP LOADS, kgf, OFF-ROAD FACTOR 2, ONE STRAP 60 % SIDEWAYS")
    # detail D
    dx0, dy0, k = 300.0, 131.0, 2.0
    tw, th = P["track_w"], P["track_h"]
    S.view_label(sh, 320, 162, "DETAIL D: TRACK IN ITS RECESS", k)
    sh.text(320, 154.5, "SCHEMATIC, FLOOR PANEL ASSUMED 30 THICK", 1.8, "middle")
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
    items = [("10", "G-01", "Condor SC-2000 chock with trailer adapter", "2"),
             ("11", "G-02", f"L-track rows: {P['interior_width']:.0f}, {hw - P['rear_row_y0']:.0f} and {P['stow_row_x1'] - P['stow_row_x0']:.0f} long", "3"),
             ("12", "G-03", "Double-stud L-track fitting", "16 + 2 spare"), ("-", "G-04", "M8 through-bolts, crush tubes, hardpoints", "1 set"),
             ("-", "F-07", "A4-70 bolts, nylon washers and sleeves", "1 lot"), ("-", "F-03", "Plexus MA310 for the hardpoints", "1 lot")]
    S.parts_list(sh, _bom_rows(bom, items), ybase=66.0, row_h=3.8, tags={"11": "D", "12": "D"})
    S.notes(sh, 22, 64, [
        f"REVISION D: THE BIKES STAND ALONG THE TRAILER, SO THE TWO MAIN ROWS RUN ACROSS IT, AT X {P['front_row_x']:.0f} (FULL WIDTH) AND X {P['rear_row_x']:.0f} "
        f"(ROAD-SIDE WALL TO THE GAS LOCKER), ON research/03'S POSITIONS FROM EACH BIKE'S AXLES. A SHORT ROW ALONG THE KERB STRIP HOLDS THE GENERATOR AND JERRY CANS.",
        "TRACK: KINEDYNE SERIES L MEDIUM DUTY WITH FLANGES (G-02), RECESSED WITH ITS TOP FLUSH WITH THE FLOOR. BOLTS: M8 A4-70 AT 150 mm PITCH OR LESS, "
        "WITH CRUSH TUBES, THROUGH A BONDED HARDPOINT STRIP TO THE STEEL RAIL BELOW.",
        "DESIGN LOAD: EVERY ANCHOR AND ITS FLOOR FIXING IS DESIGNED FOR 20 kN, THE BREAKING LOAD OF AN LC 1,000 kg STRAP (NTC GUIDE p. 201). "
        f"WORST STRAP {res['worst']['worst_kgf']:.0f} kgf (RES-01)." if res else "DESIGN LOAD 20 kN PER ANCHOR.",
        f"CHOCKS: EACH ADAPTER BOLTS THROUGH TO STEEL ON ITS BIKE CENTRELINE (TUAREG Y {P['tuareg_y']:+.0f}, STREET TRIPLE Y {P['st_y']:+.0f}), NOSE AGAINST PARTITION A. "
        "THEY TAKE THE BRAKING PUSH (TUAREG ABOUT 330 kgf). TORQUE VALUES ARE NOT SET YET.",
    ], width_chars=125, size=1.8)
    _title(sh, dwg, reg, "ANCHOR DESIGN LOAD 20 kN EACH, 16 ANCHORS IN USE.", sc, prj.assembly.revision)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-501
def ct501(prj, model, bom, checks, reg, dwg):
    sh = S.Sheet()
    S.frame(sh)
    P = prj.P.values
    t0 = time.time()
    hw, gl = P["half_width"], P["garage_length"]
    # ---- beam layout plan, deck and bedding removed. X to the right, kerb side at the bottom
    sc = 20.0
    x0 = 205.0 - gl / sc
    v = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=x0, oy=200.0)
    v.draw(_leaves(_module_shapes(model, only_refs=("1", "5", "6", "C8"))))
    S.view_label(sh, 140, 272, "BEAM LAYOUT PLAN, DECK AND BEDDING REMOVED", sc)
    yl = v.p(0, hw + 20, 0)[1] + 3
    for xb in P["beam_x"]:
        p0, p1 = v.p(xb, hw + 20, 0), v.p(xb, -hw - 20, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(p0[0], yl, f"X {xb:.0f}", 2.0, "middle")
    a, b = v.p(0, -hw, 0), v.p(gl, -hw, 0)
    S.hdim(sh, a[0], a[1], b[0], b[1], a[1] - 11, f"{gl:.0f} PARTITION A TO THE REAR WALL")
    w0, w1 = v.p(0, hw, 0), v.p(0, -hw, 0)
    S.vdim(sh, w0[0], w0[1], w1[0], w1[1], w0[0] - 10, f"{P['interior_width']:.0f} BEAM SPAN, BETWEEN SIDE-WALL FACES")
    for xb0, xb1 in zip(P["beam_x"], P["beam_x"][1:]):
        p0, p1 = v.p(xb0, hw * 0.55, 0), v.p(xb1, hw * 0.55, 0)
        S.hdim(sh, p0[0], p0[1], p1[0], p1[1], p0[1], f"{xb1 - xb0:.0f}", ext=False)
    S.cut_marker(sh, v.p(gl + 50, 0, 0), v.p(-50, 0, 0), (0, 1), "E")
    S.cut_marker(sh, v.p(P["beam_x"][2], -hw - 50, 0), v.p(P["beam_x"][2], -hw + 300, 0), (-1, 0), "F")
    sh.text(v.p(gl + 60, 0, 0)[0] + 2, v.p(0, hw, 0)[1] - 1, "ROAD SIDE", 1.9)
    sh.text(v.p(gl + 60, 0, 0)[0] + 2, v.p(0, -hw, 0)[1] + 0.5, "KERB SIDE", 1.9)
    sh.text(v.p(gl + 60, 0, 0)[0] + 1, v.p(0, 0, 0)[1] - 6, "REAR WALL", 1.9)
    _balloons(sh, [("6", v.p(P["beam_x"][4], -300, 0), (218.5, 212.0)), ("5", v.p(1400, hw - 20, 0), (218.5, 238.0)),
                   ("5", v.p(gl - 20, -600, 0), (218.5, 186.0)), ("1", v.p(-10, -500, 0), (68.5, 180.0))])

    # ---- section E-E: bed stack at the rear wall, section at Y 0, 1:5
    sc2 = 5.0
    x0, x1, z0, z1 = gl - 420, gl + 36, 1395.0, 1815.0
    shapes = _leaves(_module_shapes(model, only_refs=("5", "6", "7", "8", "9", "C8", "C5")))
    cut = S.section(shapes, Plane.XZ.offset(0.0), keep=Keep.BOTTOM)
    det = _clip(cut, x0, x1, -0.5, 1200, z0, z1)
    vS = S.View(sh, (0, -1, 0), (0, 0, 1), sc2, ox=262.0, oy=160.0, anchor=(gl - 420, 0, 1600))
    vS.draw(det)
    _shade(sh, vS, _cut_faces(det, "Y", 0.0))
    S.view_label(sh, 300, 216.5, "SECTION E-E, BED STACK AT THE REAR WALL, Y 0", sc2)
    sh.text(300, 209.5, "LIVING AREA TO THE LEFT, REAR WALL RIGHT. CUT FACES SHADED.", 1.8, "middle")
    xr = vS.p(x1, 0, 0)[0] + 3
    levels = [(P["beam_underside_z"], f"{P['beam_underside_z']:.0f} BEAM UNDERSIDE"), (P["deck_z"], f"{P['deck_z']:.0f} DECK UNDERSIDE"),
              (P["froli_z"], f"{P['froli_z']:.0f} DECK TOP"), (P["mattress_z"], f"{P['mattress_z']:.0f} FROLI TOP"),
              (P["mattress_z"] + P["mattress_t"], f"{P['mattress_z'] + P['mattress_t']:.0f} MATTRESS TOP"),
              (P["mattress_z"] + P["mattress_t"] + P["bedding_allowance"], f"{P['mattress_z'] + P['mattress_t'] + P['bedding_allowance']:.0f} BEDDING ALLOWANCE"),
              (P["ceiling_z"], f"{P['ceiling_z']:.0f} CEILING, ROOF DOWN")]
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
    sh.line(vS.p(x0, 0, zb)[0], vS.p(0, 0, zb)[1], vS.p(x1, 0, zb)[0], vS.p(0, 0, zb)[1], "phantom")
    xb = P["beam_x"][-1]
    sb = vS.p(xb - 25, 0, P["beam_underside_z"])
    S.hdim(sh, sb[0], sb[1], vS.p(xb + 25, 0, 0)[0], sb[1], sb[1] - 6, "50")
    _balloons(sh, [("9", vS.p(gl - 380, 0, 1650), (250.0, 186.0)), ("8", vS.p(gl - 380, 0, 1550), (250.0, 176.0)),
                   ("7", vS.p(gl - 380, 0, 1520), (250.0, 166.0)), ("6", vS.p(xb - 20, 0, 1470), (250.0, 156.0)),
                   ("5", vS.p(gl - 2, 0, 1490), (250.0, 146.0))])

    # ---- detail F: beam end on the kerb-side wall ledger, section at the middle beam, 1:2
    sc3 = 2.0
    xb = P["beam_x"][2]
    shapes = _leaves(_module_shapes(model, only_refs=("5", "6", "7", "C3")))
    cutF = S.section(shapes, Plane.YZ.offset(xb), keep=Keep.BOTTOM)
    detF = _clip(cutF, xb - 30, xb + 0.5, -hw - 36, -hw + 150, 1405, 1545)
    sc3 = 3.0
    vD = S.View(sh, (1, 0, 0), (0, 0, 1), sc3, ox=112.0, oy=82.0, anchor=(xb, -hw, 1460))
    vD.draw(detF)
    _shade(sh, vD, _cut_faces(detF, "X", xb))
    S.view_label(sh, 140, 124, "DETAIL F: BEAM END AT THE KERB WALL", sc3)
    sh.text(140, 117.5, f"SECTION AT X {xb:.0f}, LOOKING FORWARD", 1.8, "middle")
    S.leader(sh, vD.p(xb, -hw + 25, 1458.5), (168.0, 62.0), "LEDGER 40x40x3 (B-05), SHELF AT Z 1460,",
             ["BONDED (F-01) AND RIVETED (F-05)", "TO THE SIDE WALL."])
    S.leader(sh, vD.p(xb, -hw + 100, 1490), (168.0, 80.0), "BEAM SHS 50x50x3 (B-04),",
             ["END ABUTS THE WALL, RIVETED", "DOWN THROUGH THE SHELF."])
    S.leader(sh, vD.p(xb, -hw + 120, 1525), (168.0, 98.0), "DECK 20 HONEYCOMB (B-03),", ["BONDED AND RIVETED"])
    S.leader(sh, vD.p(xb, -hw - 15, 1415), (168.0, 50.0), "KERB-SIDE WALL (BODY)")
    s0, s1 = vD.p(xb, -hw, 1460), vD.p(xb, -hw + 40, 1460)
    S.hdim(sh, s0[0], vD.p(xb, 0, 1420)[1], s1[0], vD.p(xb, 0, 1420)[1], vD.p(xb, 0, 1405)[1] - 2, "40")

    # ---- detail G: the deck laps over the top edge of partition A, section at Y 0, 1:2
    dx0 = P["deck_x0"]
    shapes = _leaves(_module_shapes(model, only_refs=("1", "4.A-top", "5.on-A", "7")))
    cutG = S.section(shapes, Plane.XZ.offset(0.0), keep=Keep.BOTTOM)
    detG = _clip(cutG, dx0 - 25, 120, -0.5, 300, 1415, 1550)
    vG = S.View(sh, (0, -1, 0), (0, 0, 1), sc3, ox=50.0, oy=92.0, anchor=(0, 0, P["deck_z"]))
    vG.draw(detG)
    _shade(sh, vG, _cut_faces(detG, "Y", 0.0))
    S.view_label(sh, 55, 124, "DETAIL G: DECK LAP AT A", sc3)
    sh.text(55.0, 117.5, "SECTION AT Y 0. LIVING AREA LEFT, GARAGE RIGHT", 1.8, "middle")
    top = P["froli_z"]
    p_b, p_e = vG.p(dx0, 0, top), vG.p(0, 0, top)
    S.hdim(sh, p_b[0], p_b[1], p_e[0], p_e[1], p_b[1] + 6, f"{-dx0:.0f}")
    _balloons(sh, [("7", vG.p(60, 0, 1520), (95.0, 108.0)), ("1", vG.p(-10, 0, 1440), (30.0, 60.0)),
                   ("4", vG.p(-34, 0, 1500), (22.0, 72.0)), ("5", vG.p(20, 0, 1480), (95.0, 70.0))])

    items = [("1", "P-01", f"Partition A, 20 honeycomb 2330x{P['partition_a_h']:.0f}", "1"),
             ("4", "P-02", "Cleat, angle 25x25x1.6 (detail G)", f"{_q(bom, 'P-02'):.1f} m in all"),
             ("5", "B-05", "Ledger, angle 40x40x3 6060-T5", f"4 ({_q(bom, 'B-05'):.2f} m)"),
             ("6", "B-04", "Beam, SHS 50x50x3 6060-T5", f"5 x {P['interior_width']:.0f}"),
             ("7", "B-03", f"Deck, 20 honeycomb {P['deck_length']:.0f}x2330, laps A", f"1 ({_q(bom, 'B-03'):.2f} m2)"),
             ("8", "B-02", "Froli Star Mobil pack", "2"), ("9", "B-01", "Mattress 1530x2030x150, across", "1"),
             ("-", "F-01", "Sikaflex-252 structural adhesive", "1.4 l"), ("-", "F-02", "Sikaflex-221 seam sealant", "0.3 l"),
             ("-", "F-05", "Monobolt rivets BAPV-06-04, -08-06", "about 60")]
    S.parts_list(sh, _bom_rows(bom, items), ybase=66.0, row_h=4.2, tags={"5": "D", "6": "D", "7": "D"})
    xs = ", ".join(f"{x:.0f}" for x in P["beam_x"])
    _, starts = S.notes(sh, 232, 252, [
        f"REVISION D, WHOLE SHEET REDRAWN. FIVE BEAMS ACROSS THE TRAILER AT X {xs}. EACH END SITS ON A SIDE-WALL LEDGER SHELF AT Z {P['beam_underside_z']:.0f} AND ABUTS THE WALL.",
        f"THE LEDGERS ON PARTITION A AND ON THE REAR WALL'S DOOR HEADER CARRY THE DECK EDGES WITH THEIR SHELF TOP AT Z {P['deck_z']:.0f}.",
        f"DECK: {P['deck_length']:.0f} x 2330 FROM X {P['deck_x0']:.0f}, LAPPING OVER THE TOP EDGE OF PARTITION A AND ITS TOP CLEAT (DETAIL G). BONDED (SIKAFLEX-252) TO THE BEAMS, "
        "LEDGERS AND PARTITION A, RIVETED, AND SEALED ALL ROUND (SIKAFLEX-221) AS THE FUEL-SMELL BARRIER (GAR-02). HOLD POINT BEFORE CLOSING.",
        f"THE SPAN IS {P['interior_width']:.0f}, SO THE BEAMS ARE SHS 50x50x3 (I 20.8 cm4, CALCULATED). SAG UNDER 255 kg SPREAD OVER THE BED {_bed_sag(checks)} (BED-01). "
        "THE ENGINEER CONFIRMS THE BEAM SIZE AND LOAD CASES.",
    ], width_chars=108, size=1.8)
    S.rev_tag(sh, 227.5, starts[0] + 0.6, "D")
    bed = sum(r["mass_kg"] for r in bom["lines"] if r["group"] == "bed")
    _title(sh, dwg, reg, f"BED LINES B-01 TO B-05 {bed:.1f} kg (TB-11).", sc, prj.assembly.revision)
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


def main(only: list[str] | None = None):
    import sys
    import yaml
    t0 = time.time()
    prj = Project()
    model = Model(prj)
    bom = json.loads((BUILD / "bom" / "bom.json").read_text())
    bom["with_bikes_kg"] = bom["totals"]["module_empty"] + sum(b["mass_kg"] for b in bom["bikes"])
    cp = BUILD / "checks" / "checks.json"
    checks = json.loads(cp.read_text())["results"] if cp.exists() else []
    reg = yaml.safe_load((prj.root / "data" / "drawings.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    only = only or [a for a in sys.argv[2:] if a.startswith("CT-")]
    tm = {}
    from .chassis_sheets import ct101, ct102, ct103
    from .ga import ct001
    from .ute_sheets import ct701, ct702, ct703, ct704
    fns = {"CT-001": ct001, "CT-101": ct101, "CT-102": ct102, "CT-103": ct103, "CT-401": ct401, "CT-402": ct402, "CT-501": ct501,
           "CT-701": ct701, "CT-702": ct702, "CT-703": ct703, "CT-704": ct704}
    for dwg in reg["drawings"]:
        if only and dwg["number"] not in only:
            continue
        tm[dwg["number"]] = round(fns[dwg["number"]](prj, model, bom, checks, reg, dwg), 1)
        print(f"{dwg['number']} written in {tm[dwg['number']]} s", flush=True)
    register = [dict(number=d["number"], title=d["title"], subtitle=d["subtitle"], revision=d["revisions"][-1]["rev"],
                     status=d["status"], date=str(d["revisions"][-1]["date"]), scale=d["scale"], size=d["size"],
                     sheet=d["sheet"]) for d in reg["drawings"]]
    (OUT / "register.json").write_text(json.dumps(dict(drawings=register, timings=tm, total_s=round(time.time() - t0, 1)), indent=1))

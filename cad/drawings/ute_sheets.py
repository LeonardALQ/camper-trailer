"""Ute garage drawings CT-701 to CT-704 (A3, third angle), from the ute (cad/ute.py) and its bike garage module
(cad/ute_garage.py, data/assemblies/ute-garage.yaml). Every sheet is DRAFT until the engineer reviews UTE-GARAGE.md.

CT-701: the ute with the box, general arrangement: kerb-side elevation, plan, rear view, mass by case and the checks.
CT-702: box frame and panels: kerb-side frame elevation, subframe plan with the deck mounts, section at the rear axle.
CT-703: doors and security: rear view, kerb door, plan section through the barn doors, the security layers.
CT-704: restraint layout: plan with the roof off, section at the rear L-track row, strap loads.

Elevations look from the kerb side with the ute's front to the left. Plans look down with the kerb side at the bottom.
"""
from __future__ import annotations

import time

from build123d import Keep, Plane

from ..build import git_hash
from . import sheet as S

_CTX: dict = {}
SIDE_TU, SIDE_ST = "Aprilia Tuareg 660 Rally", "Triumph Street Triple 765"


def ctx() -> dict:
    """Build the ute and its garage once for all four sheets."""
    if not _CTX:
        from ..ute import Ute
        from ..ute_garage import build_garage
        g, m = build_garage()
        _CTX.update(g=g, m=m, ute=Ute(g), P=m.prj.P.values, prj=m.prj)
    return _CTX


def _gs(c, groups=None, exclude=(), only=None, loading=False):
    from ..ute_model import garage_solids
    out = []
    for i, s in garage_solids(c["ute"], c["m"], loading=loading, groups=groups, exclude=exclude):
        if only is not None and i.ref not in only and i.iid not in only:
            continue
        out.append(s)
    return out


def _module(c, groups=None, exclude=(), only=None):
    """Module bodies in the module frame (no move), travel view."""
    out = []
    for b in c["m"].built.values():
        i = b.inst
        if i.check_only or i.display == "loading_only":
            continue
        if (groups and i.group not in groups) or i.ref in exclude or i.iid in exclude:
            continue
        if only is not None and i.ref not in only and i.iid not in only:
            continue
        out.append(b.shape)
    return out


def _leaves(shapes):
    from build123d import Compound
    out = []
    for s in shapes:
        if isinstance(s, Compound) and s.children:
            out.extend(_leaves(list(s.children)))
        else:
            out.append(s)
    return out


def _shade(sh, view, shapes, axis, value, tol=0.05):
    from .sheets import _shade as shade, _cut_faces
    shade(sh, view, _cut_faces(shapes, axis, value, tol))


def _title(sh, dwg, reg, mass_note, scale, c, weld_note=None):
    rev = dwg["revisions"][-1]
    S.title_block(
        sh, owner=reg["owner"], project=dwg.get("project") or reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"], engineer="NOT REVIEWED" if dwg.get("structural") else "N/A",
        sheet_no=dwg["sheet"], sheets=reg["sheets_total"], size=dwg["size"], scale=scale, material="SEE TABLE",
        mass_note=mass_note, model_ref=f"ute.step (ASM-UG rev {c['prj'].assembly.revision}, UTE-79 rev {c['ute'].d['revision']})",
        git=git_hash(), weld_note=weld_note)
    # the sheet's own layout leaves room for this many revision rows. The register (and the site's Drawings page) keeps every one
    rows = {"CT-701": 4, "CT-702": 3, "CT-703": 4, "CT-704": 3}.get(dwg["number"], 7)
    S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                               checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]], max_rows=rows)


def _stamp(sh, x, y):
    sh.text(x, y, "DRAFT, NOT FOR CONSTRUCTION UNTIL THE ENGINEER REVIEWS UTE-GARAGE.md", 2.4, bold=True, color="#b00")


def _mass_note(c):
    g = c["g"]
    return f"BOX {g['box_kg']:.1f} kg EMPTY ({g['box_kg_growth']:.1f} kg WITH GROWTH) AGAINST 440 kg."


def _check_rows(rows):
    out = []
    for r in rows:
        sub = {SIDE_TU: " TU", SIDE_ST: " ST"}.get(r.get("sub", ""), "")
        if "rear tyre" in r.get("sub", ""):
            sub = " " + r["sub"][0]
        m = r.get("measured", r.get("measured_mm"))
        val = f"{m:,.1f}" if isinstance(m, (int, float)) else str(m)
        if r.get("type") == "contact":
            val = f"{len([p for p in r['pairs'] if p['ok']])}/{len(r['pairs'])} touch"
        color = "#000" if r["ok"] else ("#c00" if r["severity"] == "fail" else "#b06000")
        lim = str(r["limit"]).replace("reported, against", "rep. vs").replace("touching, no overlap", "touching")
        out.append([r["id"] + sub, lim[:24], (val, color), (r["status"], color)])
    return out


# ------------------------------------------------------------------ CT-701 general arrangement
def ct701(prj, model, bom, checks, reg, dwg):
    from ..ute_model import vehicle_solids
    t0 = time.time()
    c = ctx()
    ute, g, P = c["ute"], c["g"], c["P"]
    V = ute.V
    sh = S.Sheet()
    S.frame(sh)
    sc = 50.0
    outside = vehicle_solids(ute) + _gs(c, groups=("body", "doors", "subframe", "security"))
    ext = g["box_extent"]
    wb = V["wheelbase"]

    # ---- elevation from the kerb side
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=62.0, oy=222.0)
    vE.draw(outside)
    S.view_label(sh, 100, 209, "ELEVATION FROM THE KERB SIDE, TRAVELLING", sc)
    gnd0, gnd1 = vE.p(-1000, 0, 0), vE.p(V["ball_x"] + 300, 0, 0)
    sh.line(gnd0[0], gnd0[1], gnd1[0], gnd1[1], "phantom")
    fa, ra = vE.p(0, 0, 0), vE.p(wb, 0, 0)
    for p in (fa, ra):
        sh.line(p[0], p[1] - 4, p[0], p[1] + 30, "centre")
    S.hdim(sh, fa[0], fa[1], ra[0], ra[1], fa[1] - 5, f"{wb:.0f} WHEELBASE", size=2.0)
    rb = vE.p(ext["x1"], 0, 0)
    S.hdim(sh, ra[0], ra[1], rb[0], rb[1], fa[1] - 5, f"{ext['x1'] - wb:.0f}", size=2.0)
    sh.text(rb[0] + 1, fa[1] - 9, f"REAR OVERHANG, LIMIT 1908", 1.6)
    bx0, bx1 = vE.p(ext["x0"], 0, ext["z1"]), vE.p(V["box_x0"] + P["outside_l"], 0, ext["z1"])
    S.hdim(sh, bx0[0], bx0[1], bx1[0], bx1[1], bx0[1] + 5, f"{P['outside_l']:.0f} BOX", size=2.0)
    cb = vE.p(V["cab_back_x"], 0, V["cab_height"])
    S.leader(sh, (cb[0] + 0.3, cb[1] - 1), (cb[0] - 12, cb[1] + 8), f"{ext['x0'] - V['cab_back_x']:.0f} TO THE CAB (MIN 39)", size=1.8)
    zr = vE.p(ext["x1"], 0, 0)[0]
    for z, lab, xd in ((V["coupling_z"], f"{V['coupling_z']:.0f} BALL", zr + 4), (g["deck_z"], f"{g['deck_z']:.0f} FLOOR", zr + 8.5),
                       (ext["z1"], f"{ext['z1']:.0f} ROOF", zr + 13)):
        S.vdim(sh, zr, vE.p(0, 0, 0)[1], zr, vE.p(0, 0, z)[1], xd, lab, size=1.8)
    cz = vE.p(-300, 0, V["cab_height"])
    S.leader(sh, (cz[0], cz[1] + 0.2), (cz[0] - 8, cz[1] + 7), f"CAB ROOF {V['cab_height']:.0f}", size=1.8)

    # ---- loading: doors open, ramp on the sill, bikes in
    loading = vehicle_solids(ute) + _gs(c, groups=("body", "doors", "subframe", "security", "bikes", "restraint", "context"), loading=True)
    vL = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=62.0, oy=152.0)
    vL.draw(loading)
    S.view_label(sh, 100, 139, "ELEVATION FROM THE KERB SIDE, LOADING", sc)
    sill = vL.p(P["module_x0"] + P["x_end"], 0, P["ground_drop"])
    S.leader(sh, sill, (sill[0] + 16, sill[1] + 12), f"RAMP {g['dims']['ramp_deg']:.1f} DEG FROM A {P['ground_drop']:.0f} SILL", size=1.8)

    # ---- plan
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=62.0, oy=100.0)
    vP.draw(outside)
    S.view_label(sh, 100, 76, "PLAN", sc)
    for i in range(1, 7):
        x = P[f"mount{i}_x"] + P["module_x0"]
        for yy in (P["rail_y"], -P["rail_y"]):
            p = vP.p(x, yy, 0)
            sh.circle(p[0], p[1], 0.6, "medium")
    L, body = ute.limits, g["body_extent"]
    w0, w1 = vP.p(ext["x1"], body["y1"], 0), vP.p(ext["x1"], body["y0"], 0)
    S.vdim(sh, w0[0], w0[1], w1[0], w1[1], w0[0] + 6, f"{body['y1'] - body['y0']:.0f} BODY (MAX {L['box_width_max_mm']:.0f})", size=1.8)
    fl = vP.p(P["module_x0"] + (P["flare_x0"] + P["flare_x1"]) / 2, ext["y0"], 0)
    S.leader(sh, fl, (fl[0] + 14, fl[1] - 8), f"REAR TUB FLARES, {ext['y1'] - ext['y0']:.0f} OVER THEM (MAX {L['flare_width_max_mm']:.0f}), DETAIL B",
             size=1.8)
    c0, c1 = vP.p(V["cab_back_x"] - 400, V["cab_width"] / 2, 0), vP.p(V["cab_back_x"] - 400, -V["cab_width"] / 2, 0)
    S.vdim(sh, c0[0], c0[1], c1[0], c1[1], c0[0] - 22, f"{V['cab_width']:.0f} CAB", size=1.8)
    sh.text(vP.p(V["ball_x"] + 500, 0, 0)[0], vP.p(0, ext["y1"], 0)[1] + 1, "ROAD SIDE", 1.8)
    sh.text(vP.p(V["ball_x"] + 500, 0, 0)[0], vP.p(0, ext["y0"], 0)[1] - 2.5, "KERB SIDE", 1.8)
    S.leader(sh, vP.p(P["mount1_x"] + P["module_x0"], -P["rail_y"], 0), (vP.p(0, 0, 0)[0] + 10, vP.p(0, ext["y0"], 0)[1] - 8),
             "TOYOTA DECK MOUNTS, 6 PAIRS", size=1.8)

    # ---- rear view
    vR = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=200.0, oy=222.0)
    vR.draw(outside)
    S.view_label(sh, 200, 209, "REAR VIEW", sc)
    y0, y1 = vR.p(0, body["y0"], ext["z1"]), vR.p(0, body["y1"], ext["z1"])
    S.hdim(sh, y0[0], y0[1], y1[0], y1[1], y0[1] + 5, f"{body['y1'] - body['y0']:.0f} BODY", size=1.8)
    t0_, t1_ = vR.p(0, -V["track_rear"] / 2, 0), vR.p(0, V["track_rear"] / 2, 0)
    S.hdim(sh, t0_[0], t0_[1], t1_[0], t1_[1], t0_[1] - 5, f"{V['track_rear']:.0f} TRACK", size=1.8)
    sh.text(vR.p(0, ext["y0"], 0)[0] - 2, vR.p(0, 0, 200)[1], "KERB", 1.8, "end")
    sh.text(vR.p(0, ext["y1"], 0)[0] + 2, vR.p(0, 0, 200)[1], "ROAD", 1.8)

    # ---- mass by case and the ute checks
    rows = []
    for cs in ute.cases():
        n, gr = cs["nominal"], cs["growth"]
        rows.append([cs["id"], f"{n['mass_kg']:,.0f}", f"{n['front_kg']:,.0f}", f"{n['rear_kg']:,.0f}", f"{gr['rear_kg']:,.0f}",
                     f"{n['towball_kg']:.0f}", f"{n['front_share_pct']:.1f}", f"{n['cog'][2]:.0f}", f"{n['ssf']:.3f}"])
    yb = S.table(sh, 230, 252, [("CASE", 12), ("kg", 18), ("FRONT", 18), ("REAR", 18), ("REAR+G", 20), ("BALL", 16),
                                ("FRONT %", 22), ("CoG Z", 18), ("SSF", 18)], rows, size=1.75, row_h=3.2,
                 title="MASS BY CASE (kg AND mm, +G WITH GROWTH)")
    sh.text(230, yb - 3.2, "UC1 UNLADEN, UC2 BIKES ABOARD, UC3 TOWING WITH THE BIKES, UC4 TOWING, BIKES OUT, UCB BIKES IN THE TRAILER.", 1.6)
    S.table(sh, 230, yb - 8, [("CHECK", 22), ("LIMIT", 50), ("MODEL", 44), ("RESULT", 24)],
            [[r["id"], r["limit"], ((f"{r['measured']:.3f}" if r["unit"] == "" else f"{r['measured']:,.1f} {r['unit']}"), "#000" if r["ok"] else ("#c00" if r["severity"] == "fail" else "#b06000")),
              (r["status"], "#000" if r["ok"] else ("#c00" if r["severity"] == "fail" else "#b06000"))] for r in ute.checks()],
            size=1.65, row_h=2.95, title="UTE CHECKS (UTE-GARAGE.md)")

    _, _ = S.notes(sh, 22, 62, [
        "UTE FRAME DIM-U1: X FROM THE FRONT AXLE (+ REARWARD), Y FROM THE CENTRELINE (+ TO THE ROAD SIDE), Z FROM THE GROUND AT LADEN RIDE HEIGHT.",
        f"TOYOTA LANDCRUISER VDJ79 GXL SINGLE CAB, LOVELLS ELITE GVM KIT PLATED AT {L['gvm_kg']:.0f} kg (FRONT {L['front_axle_kg']:.0f}, REAR "
        f"{L['rear_axle_kg']:.0f} kg, TWICE THE ROH WHEEL'S {L['wheel_rating_kg']:.0f} kg, H18), REAR TRACK {V['track_rear']:.0f}. GCM {L['gcm_kg']:.0f} kg "
        f"WITH THE REVISION. TOWBALL {V['towball_design']:.0f} kg WITH GROWTH, AT MOST {L['towball_rating_kg']:.0f} kg.",
        f"BOX FLOOR {g['deck_z']:.0f} ABOVE THE GROUND ON A 50 mm SUBFRAME ON THE RAILS, WITH WHEEL TUBS {g['dims']['tub_h']:.1f} HIGH (ESTIMATE: FRAME TOP 774, BUMP TRAVEL 110). MEASURE BOTH ON THE VEHICLE.",
        f"THE REAR-MOST POINT IS THE CAM BAR ON THE BARN DOORS. BOX OUTSIDE {P['outside_l']:.0f} LONG, {P['outside_w']:.0f} WIDE, "
        f"{P['top_z']:.0f} HIGH ABOVE THE FLOOR AT THE WALLS AND {P['top_z'] + P['roof_crown']:.0f} AT THE ROOF'S CROWN, {P['flare_w']:.0f} WIDE OVER THE REAR TUB FLARES (DETAIL B).",
        f"ROOF: NO STEP, NO KNEELING, ON TWO LABELS ON THE ROOF (BX-C03). {P['roof_t']:g} mm 5052-H32 ON BOWS CROWNED 1:{P['roof_fall']:.0f} TO BOTH "
        "SIDES, WELDED CONTINUOUSLY ALONG THE FRONT EDGE AND THE FIRST BOW BEHIND IT, BONDED ALONG EVERY BOW WITH A SIKAFLEX-252 BEAD AND "
        "STITCHED TO THE OTHER BOWS (UGF-01). A KNEE DENTS THE SHEET.",
        "NO DRILLING OR WELDING OF THE FRAME. THE SUBFRAME BOLTS TO TOYOTA'S DECK MOUNT BRACKETS (CT-702).",
    ], width_chars=100, size=1.75)
    _detail_b(sh, 240, 165, P, V, L)
    _stamp(sh, 22, 282)
    _title(sh, dwg, reg, _mass_note(c), sc, c)
    from .sheets import OUT
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


def _detail_b(sh, x0, ytop, P, V, L):
    """Detail B, the road-side rear tub flare cut at the rear axle, looking forward (the kerb side is its mirror), at 1:2,
    in the free space under the checks. Decision H19, report 26 fix A."""
    k = 0.5
    y_lo, y_hi, z_lo, z_hi = 868.0, 952.0, -16.0, 140.0
    yb = ytop - 12 - (z_hi - z_lo) * k

    def X(y):
        return x0 + (y - y_lo) * k

    def Z(z):
        return yb + (z - z_lo) * k
    hw, fs, ft, st = P["half_width"], P["frame_s"], P["frame_t"], P["skin_t"]
    skin_in, skin_out = hw + fs, P["outside_w"] / 2
    fl_out = skin_out + P["flare_out"]
    fl_in = fl_out - st
    tub, tub_t, fl_top, floor_t = P["tub_top"], P["tub_t"], P["flare_z1"], P["floor_t"]
    tyre_y = P["wheel_y"] + P["tyre_w"] / 2
    bump = P["wheel_z"] + P["rear_bump"] + P["tyre_d"] / 2
    sh.text(x0 + 33, ytop, "DETAIL B: REAR TUB FLARE, ROAD SIDE (KERB SIDE MIRRORED)", 1.9, "middle", bold=True)
    sh.text(x0 + 33, ytop - 3.4, "SECTION AT THE REAR AXLE, LOOKING FORWARD. SCALE 1:2", 1.5, "middle")
    sh.rect(X(skin_in), Z(fl_top), X(skin_out), Z(z_hi), "thick")                    # side skin, cut away below the rail top
    sh.rect(X(hw), Z(tub), X(skin_in), Z(tub + fs), "thick")                           # bottom rail SHS 40 x 40 x 3 on the tub
    sh.rect(X(hw + ft), Z(tub + ft), X(skin_in - ft), Z(tub + fs - ft), "thin")
    sh.rect(X(y_lo), Z(tub - tub_t), X(skin_in), Z(tub), "thick")                       # tub top, 3 mm
    sh.rect(X(fl_in), Z(-floor_t), X(fl_out), Z(fl_top), "thick")                      # flare outer face
    sh.rect(X(skin_in), Z(fl_top - st), X(fl_in), Z(fl_top), "thick")                  # flare top, back to the skin line
    sh.line(X(tyre_y), Z(z_lo), X(tyre_y), Z(bump), "phantom")                          # tyre envelope, static to full bump
    sh.line(X(y_lo), Z(bump), X(tyre_y), Z(bump), "phantom")
    gap = fl_in - tyre_y
    S.hdim(sh, X(tyre_y), Z(20), X(fl_in), Z(20), Z(20), f"{gap:.0f} (MIN 30)", size=1.6, ext=False)
    S.hdim(sh, X(skin_out), Z(z_hi), X(fl_out), Z(fl_top), Z(z_hi) + 3, f"{P['flare_out']:.0f}", size=1.6)
    S.vdim(sh, X(fl_out), Z(-floor_t), X(fl_out), Z(fl_top), X(fl_out) + 5, f"{fl_top + floor_t:.1f}", size=1.6)
    S.vdim(sh, X(890), Z(bump), X(890), Z(tub - tub_t), X(890), f"{tub - tub_t - bump:.0f}", size=1.6, ext=False)
    tx = X(y_hi) + 12
    S.leader(sh, (X(skin_in + 1.2), Z(134)), (tx, Z(134)), "SIDE SKIN 2.5, CUT AWAY OVER THE TUB UP TO THE RAIL TOP", size=1.6)
    S.leader(sh, (X(skin_in - 12), Z(tub + fs - 8)), (tx, Z(112)), "BOTTOM RAIL SHS 40x40x3 ON THE TUB", size=1.6)
    S.leader(sh, (X(fl_out - 1.2), Z(70)), (tx, Z(80)), f"FLARE 2.5 5052-H32, {P['flare_x1'] - P['flare_x0']:.0f} LONG, ENDS WELDED, "
             "TOP WELDED TO THE RAIL", size=1.6)
    S.leader(sh, (X(870), Z(tub - tub_t)), (x0 - 4, Z(40)), "TUB TOP 3.0 5052-H32", size=1.6)
    S.leader(sh, (X(tyre_y), Z(0)), (x0 - 4, Z(10)), "REAR TYRE, STATIC TO FULL BUMP", size=1.6)
    for i, t in enumerate((f"ON THE ELITE'S {V['track_rear']:.0f} REAR TRACK THE TYRE'S OUTER FACE IS",
                           f"{tyre_y:.1f} FROM THE CENTRELINE, {skin_in - tyre_y:.0f} FROM THE BODY'S SKIN (RESEARCH REPORT 26).",
                           "THE FLARE KEEPS TOYOTA'S 30 OUTSIDE THE TYRE (UGW-03).",
                           f"BOX {2 * fl_out:.0f} OVER THE FLARES, MAX {L['flare_width_max_mm']:.0f}, BODY {P['outside_w']:.0f} (UTE-09, H19).")):
        sh.text(tx + 4, Z(48) - 3 * i, t, 1.6)


# ------------------------------------------------------------------ CT-702 box frame and panels
SCHEDULE = [
    ("U-FRAME", "SHS 40x40x3 6061-T6"), ("U-SKIN", "SHEET 2.5 5052-H32"), ("U-FLARE", "SHEET 2.5 5052-H32, FOLDED"),
    ("U-ROOF", "SHEET 1.6 5052-H32"),
    ("U-FLOOR", "PLATE 4.0 5052-H32"), ("U-TUB", "SHEET 3.0 5052-H32"), ("U-RUNNER", "RHS 75x50x3 6061-T6"),
    ("U-CM", "SHS 50x50x3 6061-T6"), ("U-STEEL-CM", "RHS 65x35x4.0 C350L0 GALV"), ("U-PACKER", "PLATE 5.0x65 5052-H32"),
    ("U-STRIP", "FLAT 15x10 6060"), ("U-MOUNT-FIRM", "ANGLE + 2 M12 8.8"), ("U-MOUNT-SPRING", "ANGLE + M12 8.8 + RUBBER"),
    ("U-SUB-FIX", "M8, ISOLATORS, SEALANT"),
]


def ct702(prj, model, bom, checks, reg, dwg):
    from .sheets import _clip
    t0 = time.time()
    c = ctx()
    g, P = c["g"], c["P"]
    sh = S.Sheet()
    S.frame(sh)
    sc = 20.0
    hw, fs = P["half_width"], P["frame_s"]
    structure = _module(c, groups=("body", "subframe", "context"), exclude=("B3", "B4", "C3", "C6"))

    # ---- kerb-side frame elevation: the kerb half only, skins off
    kerb = _clip(_leaves(structure + _module(c, only=("D4",))), -100, 2700, -1000, -400, -200, 1600)
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=48.0, oy=190.0)
    vE.draw(kerb)
    S.view_label(sh, 110, 166, "KERB-SIDE WALL FRAME, SKIN OFF (KERB HALF ONLY)", sc)
    top = vE.p(0, 0, P["top_z"])[1]
    xs = [-fs, P["post1_x"], P["post2_x"], P["post3_x"], P["post4_x"], P["x_end"] - fs]
    S.ordinate_h(sh, [vE.p(x, 0, 0)[0] for x in xs], top + 1, top + 5, [f"{x:.0f}" for x in xs], size=1.7)
    sh.text(vE.p(-fs, 0, 0)[0] - 2, top + 3, "POSTS X", 1.7, "end")
    k0, k1 = vE.p(P["kd_x0"], 0, P["kd_z0"]), vE.p(P["kd_x1"], 0, P["kd_z1"])
    S.hdim(sh, k0[0], k1[1], k1[0], k1[1], k1[1] - 4, f"{P['kd_x1'] - P['kd_x0']:.0f} KERB DOOR", size=1.7, ext=False)
    S.vdim(sh, k1[0], k0[1], k1[0], k1[1], k1[0] + 4, f"{P['kd_z1'] - P['kd_z0']:.0f}", size=1.7, ext=False)
    t0_, t1_ = vE.p(P["tub_x0"], 0, 0), vE.p(P["tub_x1"], 0, 0)
    S.hdim(sh, t0_[0], t0_[1], t1_[0], t1_[1], t0_[1] - 8, f"{P['tub_x1'] - P['tub_x0']:.0f} TUB, {P['tub_top']:.1f} HIGH", size=1.7)
    fk = vE.p(P["flare_x1"] - 20, 0, 40)
    S.leader(sh, fk, (fk[0] + 13, fk[1] - 13), "REAR TUB FLARE, DETAIL B ON CT-701", size=1.6)
    ax = vE.p(P["axle_m"], 0, 0)
    sh.line(ax[0], ax[1] - 12, ax[0], ax[1] + 10, "centre")
    sh.text(ax[0], ax[1] - 14.5, "REAR AXLE", 1.7, "middle")
    zr = vE.p(P["x_end"], 0, 0)[0]
    for z, lab, xd in ((P["ceiling_z"], f"{P['ceiling_z']:.0f} INSIDE", zr + 5), (P["top_z"], f"{P['top_z']:.0f}", zr + 10)):
        S.vdim(sh, zr, vE.p(0, 0, 0)[1], zr, vE.p(0, 0, z)[1], xd, lab, size=1.7)
    S.vdim(sh, zr, vE.p(0, 0, P["sub_z0"])[1], zr, vE.p(0, 0, 0)[1], zr + 5, "", size=1.7)
    sh.text(zr + 6.5, vE.p(0, 0, -60)[1], f"{-P['sub_z0']:.0f} SUBFRAME AND FLOOR", 1.6)

    # ---- subframe plan, floor off
    sub = _leaves(_module(c, groups=("subframe", "context"), exclude=("C3",)) + _module(c, only=("B2",)))
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=48.0, oy=104.0)
    vP.draw(sub)
    S.view_label(sh, 110, 30, "SUBFRAME PLAN, FLOOR OFF", sc)
    bot = vP.p(0, -hw - fs, 0)[1]
    stations = [P[f"mount{i}_x"] for i in range(1, 7)]
    S.ordinate_h(sh, [vP.p(x, 0, 0)[0] for x in stations], bot - 1, bot - 9,
                 [f"{x - P['axle_m']:+.0f}" for x in stations], size=1.7, up=False)
    sh.text(vP.p(-fs, 0, 0)[0] - 1, bot - 5, "MOUNTS FROM", 1.6, "end")
    sh.text(vP.p(-fs, 0, 0)[0] - 1, bot - 7.5, "REAR AXLE", 1.6, "end")
    for i, x in enumerate(stations, 1):
        p = vP.p(x, hw + fs, 0)
        sh.text(p[0], p[1] + 1.5, ("F" if i <= 2 else "C") + str(i), 1.7, "middle", bold=True)
    for x, lab in ((P["front_row_x"], "STEEL CM, FRONT TRACK ROW"), (P["rear_row_x"], "STEEL CM, REAR TRACK ROW")):
        p = vP.p(x, 0, 0)
        S.leader(sh, (p[0], p[1]), (p[0] + 10, p[1] + 12 if x < 1000 else p[1] + 12), lab, size=1.6)
    r0, r1 = vP.p(P["x_end"], P["rail_y"], 0), vP.p(P["x_end"], -P["rail_y"], 0)
    S.vdim(sh, r0[0], r0[1], r1[0], r1[1], r0[0] + 6, f"{2 * P['rail_y']:.0f} RAIL CL", size=1.7)
    sh.text(vP.p(P["x_end"], 0, 0)[0] + 12, vP.p(0, hw, 0)[1], "F = FIRM, C = COMPLIANT", 1.6)

    # ---- section at the rear axle, looking forward
    xcut = P["axle_m"]
    sec_shapes = _leaves(_module(c, groups=("body", "subframe", "context", "tools", "doors"), exclude=("C3",)) +
                         _clip([c["m"].built[i].shape for i in ("C4R", "C4K")], -100, 2700, -1000, 1000, -130, 200))
    cut = S.section(sec_shapes, Plane.YZ.offset(xcut), keep=Keep.BOTTOM)
    vS = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=318.0, oy=180.5)
    vS.draw(cut)
    _shade(sh, vS, cut, "X", xcut)
    S.view_label(sh, 318, 165.5, "SECTION AT THE REAR AXLE, LOOKING FORWARD", sc)
    sh.text(318, 158.5, "TYRE SWEPT FROM STATIC TO FULL BUMP SHOWN CUT", 1.6, "middle")
    w0, w1 = vS.p(0, -P["outside_w"] / 2, 1150), vS.p(0, P["outside_w"] / 2, 1150)
    S.hdim(sh, w0[0], w0[1], w1[0], w1[1], w0[1], f"{P['outside_w']:.0f} BODY OUTSIDE", size=1.7, ext=False)
    fp = vS.p(0, P["outside_w"] / 2 + P["flare_out"], 60)
    S.leader(sh, fp, (fp[0] + 5, fp[1] - 6), "FLARE, DETAIL B ON CT-701", size=1.6)
    i0, i1 = vS.p(0, -hw, 700), vS.p(0, hw, 700)
    S.hdim(sh, i0[0], i0[1], i1[0], i1[1], i0[1], f"{P['interior_width']:.0f} INSIDE", size=1.7, ext=False)
    tb = vS.p(0, P["tub_y0"], P["tub_top"])
    S.leader(sh, tb, (tb[0] + 8, tb[1] + 14), f"TUB TOP {P['tub_top']:.1f}, 25 OVER THE TYRE AT FULL BUMP", size=1.6)
    ti = vS.p(0, -P["tub_y0"], 20)
    S.leader(sh, ti, (ti[0] + 6, ti[1] - 10), "40 INSIDE THE TYRE", size=1.6)

    # ---- member schedule
    lines = {ln["id"]: ln for ln in g["lines"]}
    rows = []
    for pid, sect in SCHEDULE:
        ln = lines[pid]
        q = ln.get("measured") if ln.get("measured") is not None else ln.get("qty")
        unit = {"m": "m", "m2": "m2"}.get(ln.get("unit"), ln.get("unit") or "")
        rows.append([pid, sect, f"{q:.2f} {unit}" if isinstance(q, float) and unit in ("m", "m2") else f"{q:g} {unit}",
                     f"{ln['kg']:.1f}", ln["maturity"]])
    yb = S.table(sh, 230, 155.5, [("PART", 26), ("SECTION / MATERIAL", 58), ("QTY (MODEL)", 34), ("kg", 26), ("BASIS", 36)], rows,
                 size=1.6, row_h=2.85, title="MEMBER AND PANEL SCHEDULE")
    sh.text(230, yb - 3.2, f"BODY {g['by_group'].get('body', 0):.1f} kg, SUBFRAME AND MOUNTS {g['by_group'].get('subframe', 0):.1f} kg (NO GROWTH).", 1.7)

    S.notes(sh, 230, yb - 9, [
        "MODULE FRAME: X FROM THE FRONT WALL'S INNER FACE (+ REARWARD), Y FROM THE CENTRELINE (+ ROAD SIDE), Z FROM THE FLOOR TOP. "
        f"MODULE X 0 IS AT UTE X {P['module_x0']:.1f}, Z 0 AT UTE Z {P['deck_z']:.0f}.",
        "ONE-PIECE BODY: TIG-WELDED 5052-H32 SKINS ON A 6061-T6 FRAME. THE ENGINEER DESIGNS THE WELDS TO THE SOFTENED STRENGTH NEXT TO EACH WELD.",
        "STEEL CROSSMEMBERS ARE GALVANISED AND BOLTED, NEVER WELDED, TO THE ALUMINIUM, WITH NYLON SLEEVES AND WASHERS.",
        "FIRM MOUNTS F1 AND F2: TWO M12 8.8 PER BRACKET. COMPLIANT MOUNTS C3 TO C6: ONE M12 8.8 THROUGH TWO RUBBER CUSHIONS AND A SAFETY WASHER.",
        "TOYOTA'S BRACKETS ARE SHOWN AS ENVELOPES. CONFIRM ON THE VEHICLE WHICH ARE DECK MOUNTS AND WHICH ARE SPRING HANGERS.",
        "BRACKET BOLTS GO IN HEAD UP FROM INSIDE THE SUBFRAME, NYLOC NUT BELOW TOYOTA'S BRACKET, SO THE BOX COMES OFF ONLY FROM INSIDE IT (DETAIL A).",
    ], width_chars=96, size=1.6)
    _detail_a(sh, 332, 106)
    _stamp(sh, 22, 282)
    _title(sh, dwg, reg, _mass_note(c), sc, c, weld_note="WELDS TO AS/NZS 1665 (ALUMINIUM), DETAILS BY THE ENGINEER. ")
    from .sheets import OUT
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


def _detail_a(sh, x0, y0):
    """Detail A, the bracket bolts at stations 1 and 6, looking from the kerb side, in the space right of the notes.
    Schematic, about 1:5."""
    k = 0.2                                     # sheet mm per real mm
    cx, yb = x0 + 20, y0 - 28                   # crossmember centre, bottom of Toyota's bracket flange
    w_cm, h_cm, w_pl, t_pl, w_br, t_br = 65 * k, 35 * k, 145 * k, 6 * k, 160 * k, 8 * k
    sh.text(x0 + 38, y0 - 4, "DETAIL A: BRACKET BOLTS AT STATIONS 1 AND 6", 1.8, "middle", bold=True)
    sh.text(x0 + 38, y0 - 7, "LOOKING FROM THE KERB SIDE, NOT TO SCALE", 1.4, "middle")
    sh.text(x0 + 38, y0 - 9.5, "STATION 6: ONE BOLT THROUGH THE TWO CUSHIONS", 1.4, "middle")
    sh.rect(cx - w_br / 2, yb, cx + w_br / 2, yb + t_br, "thick")                       # Toyota's bracket flange
    sh.rect(cx - w_pl / 2, yb + t_br, cx + w_pl / 2, yb + t_br + t_pl, "thick")          # 145 x 80 x 6 plate
    y_cm = yb + t_br + t_pl
    sh.rect(cx - w_cm / 2, y_cm, cx + w_cm / 2, y_cm + h_cm, "thick")                    # RHS 65 x 35 x 4.0, end on
    sh.rect(cx - w_cm / 2 + 4 * k, y_cm + 4 * k, cx + w_cm / 2 - 4 * k, y_cm + h_cm - 4 * k, "thin")
    for side in (-1, 1):
        bx = cx + side * (w_cm / 2 + 20 * k)
        sh.rect(bx - 9 * k, y_cm, bx + 9 * k, y_cm + 8 * k, "thick")                     # hex head on the plate
        sh.line(bx - 6 * k, yb - 14 * k, bx - 6 * k, y_cm, "thin")
        sh.line(bx + 6 * k, yb - 14 * k, bx + 6 * k, y_cm, "thin")
        sh.rect(bx - 12 * k, yb - 3 * k, bx + 12 * k, yb, "thin")                        # hardened washer
        sh.rect(bx - 9 * k, yb - 13 * k, bx + 9 * k, yb - 3 * k, "thick")                # nyloc nut, below the bracket
    ex = x0 + 40
    S.leader(sh, (cx, y_cm + h_cm), (ex, y_cm + h_cm + 4), "RHS 65x35x4.0 C350L0 GALV", size=1.5)
    S.leader(sh, (cx + w_pl / 2, yb + t_br + t_pl / 2), (ex, yb + 7), "PLATE 145x80x6 C350, WELDED", size=1.5)
    S.leader(sh, (cx + w_br / 2, yb + t_br / 2), (ex, yb + 2), "TOYOTA DECK MOUNT BRACKET", size=1.5)
    S.leader(sh, (cx + w_cm / 2 + 20 * k, yb - 8 * k), (ex, yb - 5), "M12 8.8 HEAD UP, NYLOC BELOW", size=1.5)


# ------------------------------------------------------------------ CT-703 doors and security
SECURITY = [
    ("DOORS", "U-LEAF", "Two barn-door leaves inset in the portal. Kerb leaf shuts first"),
    ("DOORS", "U-LATCHES", "Shoot bolts into header and sill, keyed latches, seals"),
    ("DOORS", "U-CAMBAR", "Full-height cam bar on the road leaf, top and bottom keepers"),
    ("DOORS", "U-HINGES", "Continuous hinges, peened pins, hinge-side dog bolts"),
    ("DOORS", "U-KDOOR", "Kerb lift-up door, keyed latch and hasp"),
    ("LOCKS", "U-HASP", "ABLOY PL362 on shrouded hasps, rear and kerb doors"),
    ("INSIDE", "U-ANCHOR", "ABUS WBA100 floor anchor per bike, crossmember at X 450"),
    ("INSIDE", "U-BIKE-SEC", "ABUS 8008 disc lock, 12 mm chain to the anchor, Monimoto 9"),
    ("ALARM", "U-TRACKER", "Teltonika FMC130, reed switches on 3 doors, siren"),
]


def ct703(prj, model, bom, checks, reg, dwg):
    from .sheets import _clip
    t0 = time.time()
    c = ctx()
    g, P = c["g"], c["P"]
    sh = S.Sheet()
    S.frame(sh)
    sc = 20.0
    hw = P["half_width"]
    closed = _module(c, groups=("body", "doors", "security", "subframe"))

    # ---- rear view
    vR = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=82.0, oy=192.0)
    vR.draw(closed)
    S.view_label(sh, 82, 177, "REAR VIEW, DOORS CLOSED", sc)
    o0, o1 = vR.p(0, P["door_y0"], 0), vR.p(0, P["door_y1"], 0)
    S.hdim(sh, o0[0], o0[1], o1[0], o1[1], o0[1] - 6, f"{P['door_y1'] - P['door_y0']:.0f} CLEAR OPENING", size=1.7)
    h0, h1 = vR.p(0, P["door_y1"], 0), vR.p(0, P["door_y1"], P["door_h"])
    S.vdim(sh, h0[0], h0[1], h1[0], h1[1], h0[0] + 8, f"{P['door_h']:.0f} CLEAR", size=1.7)
    cam = vR.p(0, P["door_y1"] - 105, 900)
    S.leader(sh, cam, (cam[0] + 22, cam[1] + 18), "CAM BAR, TOP AND BOTTOM KEEPERS", size=1.6)
    hp = vR.p(0, P["door_y1"] - 165, 755)
    S.leader(sh, hp, (hp[0] + 22, hp[1] - 14), "SHROUDED HASP, ABLOY PL362", size=1.6)
    kl = vR.p(0, -300, 1200)
    S.leader(sh, kl, (kl[0] - 10, kl[1] + 22), "KERB LEAF: SHOOT BOLTS INSIDE", size=1.6)

    # ---- kerb-side door elevation
    kerb = _clip(_leaves(_module(c, groups=("body", "doors", "security"))), -100, 1500, -1000, -800, -10, 1600)
    vK = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=150.0, oy=192.0)
    vK.draw(kerb)
    S.view_label(sh, 186, 177, "KERB-SIDE DOOR, FRONT OF THE BOX", sc)
    d0, d1 = vK.p(P["kd_x0"], 0, P["kd_z0"]), vK.p(P["kd_x1"], 0, P["kd_z1"])
    S.hdim(sh, d0[0], d1[1], d1[0], d1[1], d1[1] + 5, f"{P['kd_x1'] - P['kd_x0']:.0f}", size=1.7)
    S.vdim(sh, d1[0], d0[1], d1[0], d1[1], d1[0] + 5, f"{P['kd_z1'] - P['kd_z0']:.0f}", size=1.7)
    f0 = vK.p(P["kd_x0"], 0, 0)
    S.vdim(sh, f0[0], f0[1], f0[0], d0[1], f0[0] - 4, f"{P['kd_z0']:.0f}", size=1.7)
    hg = vK.p(600, 0, P["kd_z1"])
    S.leader(sh, hg, (hg[0] + 4, hg[1] + 12), "TOP HINGE, 2 GAS STRUTS", size=1.6)

    # ---- plan section through the barn doors at Z 700, rear of the box, rotated: the rear at the bottom
    zc = 700.0
    rear = _clip(_leaves(_module(c, groups=("body", "doors", "security", "restraint", "safety"), exclude=("13",))),
                 2000, 2700, -1000, 1000, -10, 1600)
    cut = S.section(rear, Plane.XY.offset(zc), keep=Keep.BOTTOM)
    sp = 10.0
    vS = S.View(sh, (0, 0, 1), (-1, 0, 0), sp, ox=120.0, oy=96.0, anchor=(P["x_end"], 0, zc))
    vS.draw(cut)
    _shade(sh, vS, cut, "Z", zc)
    S.view_label(sh, 120, 84, "PLAN SECTION AT Z 700 THROUGH THE BARN DOORS, REAR AT THE BOTTOM", sp)
    for side, lab in ((1, "ROAD"), (-1, "KERB")):
        p = vS.p(P["x_end"], side * P["outside_w"] / 2, zc)
        sh.text(p[0] + 1.2 * side, p[1] + 2, lab, 1.8, "start" if side > 0 else "end")
    rp = vS.p(P["ramp_x0"] + P["ramp_fold_t"] / 2, 0, zc)
    S.leader(sh, rp, (rp[0] + 25, rp[1] + 30), "RAMP FOLDED ON ITS EDGE, COMES OUT FIRST", size=1.6)
    hgp = vS.p(P["x_end"] - 5, hw + 5, zc)
    S.leader(sh, hgp, (hgp[0] + 6, hgp[1] - 6), "CONTINUOUS HINGE IN THE 10 GAP AT THE CORNER POST", size=1.6)

    # ---- security layers
    lines = {ln["id"]: ln for ln in g["lines"]}
    rows = [[lay, pid, txt, f"{lines[pid]['kg']:.1f}"] for lay, pid, txt in SECURITY]
    yb = S.table(sh, 230, 252, [("LAYER", 16), ("PART", 22), ("WHAT IT DOES", 124), ("kg", 18)], rows, size=1.65, row_h=3.1,
                 title="SECURITY LAYERS (REPORT 17 SECTION 4)")
    S.notes(sh, 230, yb - 6, [
        "LOCKING: SHUT THE KERB LEAF AND THROW ITS SHOOT BOLTS. SHUT THE ROAD LEAF OVER IT AND TURN THE CAM BAR. PADLOCK THE HASP OVER THE CAM HANDLE.",
        "THE CAM BAR HOLDS THE ROAD LEAF AT THE HEADER AND THE SILL, SO A PRY BAR AT THE MIDDLE GETS NOTHING. NO LOCK CYLINDER HOLDS A DOOR ON ITS OWN.",
        "DOG BOLTS ON EACH LEAF'S HINGE EDGE ENGAGE THE CORNER POST WHEN SHUT, SO A CUT HINGE DOES NOT FREE A LEAF.",
        "LEAVES FOLD 270 DEG FLAT AGAINST THE SIDE WALLS FOR LOADING. ABOUT 0.9 m CLEAR BEHIND THE UTE TO SWING THEM.",
        "THE FMC130 ALARMS ON ANY DOOR SWITCH AND REPORTS ITS POSITION. EACH BIKE CARRIES ITS OWN MONIMOTO 9.",
        "2.5 mm ALUMINIUM STOPS NOBODY WITH A GRINDER. THE BOX HIDES THE BIKES, DEFEATS THE QUICK WAYS IN AND BUYS TIME FOR THE ALARM.",
    ], title="LOCKING AND SECURITY", width_chars=86, size=1.65)
    S.notes(sh, 22, 62, [
        "DOOR SEALS: EPDM BULB SEALS ON THE LEAVES AND THE KERB DOOR, PULLED IN BY THE CAM BAR AND LATCHES. DRAINS WITH ONE-WAY VALVES AT THE LOW CORNERS.",
        "A FILTERED FAN HIGH IN THE FRONT WALL KEEPS THE BOX ABOVE OUTSIDE PRESSURE. LOW VENTS WITH FLAP VALVES IN THE REAR CORNERS LET PETROL VAPOUR OUT.",
        "PRODUCTS: POLAR 158 OR EQUAL CAM BAR, ABUS 8008 2.0 DISC LOCKS WITH 1.2 m 12KS120 CHAINS, ABUS WBA100 ANCHORS (UTE-GARAGE.md). MASSES ARE ESTIMATES.",
    ], width_chars=100, size=1.7)
    _stamp(sh, 22, 282)
    _title(sh, dwg, reg, _mass_note(c), sc, c)
    from .sheets import OUT
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-704 restraint layout
def ct704(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    c = ctx()
    g, P = c["g"], c["P"]
    sh = S.Sheet()
    S.frame(sh)
    sc = 20.0
    hw = P["half_width"]
    ty, sy = P["tuareg_y"], P["st_y"]
    inside = _module(c, groups=("body", "bikes", "restraint", "safety", "security", "tools", "doors"),
                     exclude=("B4", "B6", "V3", "B3", "B5", "D3", "K1"))
    walls = _module(c, only=("B3",))

    # ---- plan, roof off
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=48.0, oy=196.0)
    vP.draw(inside + walls)
    S.view_label(sh, 110, 141, "PLAN, ROOF OFF", sc)
    for yc, lab in ((ty, f"TU CL Y {ty:+.0f}"), (sy, f"ST CL Y {sy:+.0f}")):
        p0, p1 = vP.p(-80, yc, 0), vP.p(P["x_end"] + 60, yc, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(p1[0] + 1, p1[1] - 0.6, lab, 1.7)
    top = vP.p(0, hw + P["frame_s"] + 2.5, 0)[1]
    for xr, lab in ((P["front_row_x"], f"FRONT ROW X {P['front_row_x']:.1f}"), (P["rear_row_x"], f"REAR ROW X {P['rear_row_x']:.1f}")):
        p0, p1 = vP.p(xr, hw + 120, 0), vP.p(xr, -hw - 60, 0)
        sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
        sh.text(p0[0], p0[1] + 1.2, lab, 1.7, "middle")
    s0, s1 = vP.p(P["x_end"] + 250, sy, 0), vP.p(P["x_end"] + 250, ty, 0)
    S.vdim(sh, s0[0], s0[1], s1[0], s1[1], s0[0] + 14, f"{P['bike_spacing']:.0f}", size=1.7, ext=False)
    gaps = g["bike_gaps"]
    sh.text(vP.p(0, 0, 0)[0], top + 8, "WALL AND STOWAGE GAPS (UGC-02): " + ", ".join(
        f"{('TU' if k == SIDE_TU else 'ST')} {v['measured']:.1f}" for k, v in gaps.items()), 1.7)
    for lab, iid, dxy in (("WINCH", "14", (60, 0)), ("CHESTS ON THE TUBS", "T1.road", (0, 0)), ("CHAIN ANCHORS", "K2.TU", (0, 0))):
        bb = c["m"].built[iid].shape.bounding_box()
        p = vP.p(bb.center().X + dxy[0], bb.center().Y, 0)
        S.leader(sh, p, (p[0] + 12, top + 3), lab, size=1.6)

    # ---- section at the rear row, looking forward
    xcut = P["rear_row_x"] + 60
    sec = _leaves(_module(c, groups=("body", "bikes", "restraint", "subframe", "tools", "security"), exclude=("B4", "R1")))
    cut = S.section(sec, Plane.YZ.offset(xcut), keep=Keep.BOTTOM)
    vS = S.View(sh, (1, 0, 0), (0, 0, 1), sc, ox=318.0, oy=180.0)
    vS.draw(cut)
    _shade(sh, vS, cut, "X", xcut)
    S.view_label(sh, 318, 165, f"SECTION AT X {xcut:.0f}, BEHIND THE REAR ROW, LOOKING FORWARD", sc)
    tr = vS.p(0, ty + P["tu_strap_dy"], 0)
    S.leader(sh, tr, (tr[0] + 4, tr[1] - 10), "TRACK ON A STEEL CROSSMEMBER", size=1.6)

    # ---- strap loads
    res = next(r for r in g["checks"] if r["id"] == "UGR-01")["restraint"]
    rows = [[r["strap"].replace("13.", ""), f"{r['length_mm']}", f"{r['sideways']:.0f}", f"{r['braking']:.0f}", f"{r['rearward']:.0f}",
             f"{r['upward']:.0f}", (f"{r['worst_kgf']:.0f} {r['worst_case'][:4]}", "#000")] for r in res["rows"]]
    yb = S.table(sh, 230, 150, [("STRAP", 18), ("L mm", 16), ("SIDE", 18), ("BRAKE", 18), ("REAR", 18), ("UP", 16), ("WORST kgf", 30)], rows,
                 size=1.7, row_h=3.1, title="STRAP LOADS (kgf), REPORT 03 CASES x 2, 1.0 g UP")
    an = next(r for r in g["checks"] if r["id"] == "UGR-02")
    cm = next(r for r in g["checks"] if r["id"] == "UGR-03")
    lc = next(k for k in c["prj"].checks if k.id == "UGR-01").restraint["lc_kg"]
    sh.text(230, yb - 3.4, f"LC {lc:.0f} kg EACH. WORST {res['worst']['worst_kgf']:.0f} kgf = {an['measured_mm']:.2f} kN AT ITS ANCHOR, AGAINST {an['limit'][3:]}.", 1.7)
    sh.text(230, yb - 6.6, "CHOCK PUSH IN BRAKING: " + ", ".join(f"{b['bike']} {b['chock_push_kgf']:.0f} kgf" for b in res["bikes"]) + ".", 1.7)
    sh.text(230, yb - 9.8, f"STRAP BREAKING LOAD AT THE WORST ANCHOR: STEEL CROSSMEMBER AT {cm['measured_mm']:.2f} OF ITS CAPACITY (UGR-03).", 1.7)

    S.notes(sh, 22, 128, [
        "AS THE TRAILER'S GARAGE (DESIGN.md): CONDOR SC-2000 CHOCK ON EACH BIKE'S CENTRELINE AT THE FRONT WALL, TWO FLUSH L-TRACK ROWS, "
        f"35 mm SPANSET STRAPS OF LC {lc:.0f} kg, A CANYON DANCER HARNESS ON THE STREET TRIPLE AND A REAR-WHEEL STRAP ON EACH BIKE.",
        "EACH TRACK ROW (PLAIN KINEDYNE FE750) SITS ON A 5 mm 5052 PACKER ON A GALVANISED RHS 65x35x4.0 CROSSMEMBER AT TOYOTA'S FIRST AND LAST DECK MOUNTS, SO THE ANCHOR LOAD REACHES THE FRAME THROUGH STEEL. "
        f"M6 A4 BOLTS WITH CRUSH TUBES AT 150 PITCH OR LESS. EACH ANCHOR WITHSTANDS ITS STRAP'S BREAKING LOAD, {an['limit'][3:].upper()} (UGR-02, UGR-03).",
        f"THE TUAREG LOADS FIRST TO THE ROAD SIDE AND IS STRAPPED FROM THE EMPTY STREET TRIPLE BAY. THE STREET TRIPLE'S KERB-SIDE FRONT STRAP IS REACHED THROUGH THE KERB DOOR.",
        "THE WINCH CLIPS ONTO THE PLATE IN FRONT OF THE BIKE BEING LOADED, 650 UP, ABOVE THE 500 mm IGNITION-FREE ZONE.",
        "TOOLS RIDE IN THE TWO CHESTS ON THE WHEEL TUBS. THE OUTER FRONT STRAPS RUN THROUGH THE FRONT CORNERS, SO THE CHESTS CANNOT GO THERE.",
        "BIKES ARE ENVELOPES FROM research/05 SCALED TO THE OWNER'S FIGURES, MIRRORS FOLDED, FRONT WHEEL 25 UP IN THE CHOCK.",
    ], width_chars=100, size=1.7)
    _stamp(sh, 22, 282)
    _title(sh, dwg, reg, _mass_note(c), sc, c)
    from .sheets import OUT
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

"""Chassis drawings CT-101 to CT-103 (A3, third angle), from the chassis design (cad/chassis.py) and its analysis
(build/chassis/chassis.json). Every sheet is DRAFT and not for construction until the engineer reviews CHASSIS.md.

CT-101: general arrangement, plan, side elevation, end views, member schedule and the cut list reference.
CT-102: drawbar and coupling: plan, elevation, coupling plate, chain lugs, jockey wheel bracket, front recovery lugs
        and stone guard.
CT-103: details, drawn as sections at their true sizes: the composite rail, outrigger root, crossmember to rail,
        the drawbar overlap's tapered end, the jacking pad, the rear recovery tongue and the spare carrier posts, with
        weld symbols to AS 1101.3.
"""
from __future__ import annotations

import copy
import json
import math
import time

from ..build import BUILD, git_hash
from ..chassis import fitting_solids, member_solid
from ..trailer import Trailer
from . import sheet as S

OUT = BUILD / "drawings"
SHORT = {"rail": "Main rails", "raiser": "Raisers, continuous fillets to the rails", "cm_end": "Body end crossmembers, full rail height",
         "cm_xt": "XT crossmembers, full rail height", "cm_floor": "Floor crossmembers at raiser height", "outrigger": "Outriggers at raiser height",
         "drawbar": "Drawbar members (A-frame and overlap)", "brace": "Drawbar cross brace", "plan_brace": "Plan brace diagonals (3 bays)",
         "spare_post": "Spare wheel carrier posts"}
WELD_NOTE = "WELDS SP TO AS/NZS 1554.1, SYMBOLS TO AS 1101.3. "


# ------------------------------------------------------------------ helpers
def _chassis():
    data = json.loads((BUILD / "chassis" / "chassis.json").read_text())
    return data


def _forces() -> dict:
    """The plate and the load cases' forces in kN (data/chassis/chassis.yaml), for the sheets' notes."""
    import yaml
    from ..build import ROOT
    lcs = {l["id"]: l for l in yaml.safe_load((ROOT / "data/chassis/chassis.yaml").read_text())["load_cases"]}
    plate = yaml.safe_load((ROOT / "data/load_cases.yaml").read_text())["registration"]["plated_atm_kg"]["v"]
    top = lambda lc, i: max(abs(f[i]) for f in lcs[lc]["forces_n"]) / 1000  # noqa: E731
    return dict(plate=plate, along=top("LC6", 0), across=top("LC6", 1), up=top("LC6", 2), chain=top("LC6b", 0), chain_up=top("LC6b", 2),
                pull=lcs["LC8a"]["force_n"] / 1000, ult=lcs["LC8a"]["ultimate_n"] / 1000, pad=lcs["LC8b"]["pad_n"] / 1000)


def _layout(prj, model):
    rep = json.loads((BUILD / "trailer" / "trailer.json").read_text())
    tr = Trailer(prj)
    tr.analyse_chassis = False
    lay = tr.layout(**rep["solved"]["overrides"])
    return lay, rep


def _shapes(lay, ids=None, roles=None, fittings=True):
    ch = lay.chassis
    out = []
    for m in ch.members:
        if (ids and m.id not in ids) or (roles and m.role not in roles):
            continue
        out.append(member_solid(m))
    if fittings:
        for f in ch.fittings:
            if ids and f.id not in ids:
                continue
            out.extend(fitting_solids(ch, f))
    return out


def _title(sh, dwg, reg, mass_note, scale, rev_model):
    rev = dwg["revisions"][-1]
    S.title_block(
        sh, owner=reg["owner"], project=dwg.get("project") or reg["project"], number=dwg["number"], title=dwg["title"],
        subtitle=dwg["subtitle"], rev=rev["rev"], status=dwg["status"], date=str(rev["date"]), drawn=reg["drawn_by"],
        checked=rev["checked"], approved=rev["approved"], engineer="NOT REVIEWED", sheet_no=dwg["sheet"], sheets=reg["sheets_total"],
        size=dwg["size"], scale=scale, material="C450L0 RHS/SHS, PLATE GR 350, HDG", mass_note=mass_note,
        model_ref=f"chassis.step (ASM-CH rev {rev_model})", git=git_hash(), weld_note=WELD_NOTE)
    # the sheet's own layout leaves room for this many revision rows. The register (and the site's Drawings page) keeps every one
    rows = {"CT-101": 5, "CT-102": 2, "CT-103": 2}.get(dwg["number"], 7)
    S.revision_table(sh, [dict(rev=r["rev"], date=str(r["date"]), description=r["description"], drawn=r["drawn"],
                               checked=r["checked"], approved=r["approved"]) for r in dwg["revisions"]], max_rows=rows)


def _draft_stamp(sh, x, y):
    sh.rect(x - 52, y - 6, x + 52, y + 6, "fail")
    sh.text(x, y - 1.7, "DRAFT, NOT FOR CONSTRUCTION UNTIL THE ENGINEER REVIEWS CHASSIS.md", 2.0, "middle", bold=True, color="#c00")


def weld_symbol(sh, tip, elbow, size: str, other_side=False, both=False, all_round=False, length: str = "", note: str = ""):
    """AS 1101.3 fillet weld symbol: arrow to the joint, reference line, the triangle below the line for the arrow
    side (above for the other side, both for both sides), the leg size on the left and the length on the right, a
    circle at the elbow for all round."""
    (tx, ty), (ex, ey) = tip, elbow
    sh.line(tx, ty, ex, ey, "thin")
    L = math.hypot(tx - ex, ty - ey) or 1
    sh.arrow((tx, ty), ((tx - ex) / L, (ty - ey) / L), 2.0, 0.4)
    s = 1 if ex >= tx else -1
    x1 = ex + s * 16
    sh.line(ex, ey, x1, ey, "medium")
    xm = ex + s * 7
    tri = []
    if not other_side or both:
        tri.append(-1)
    if other_side or both:
        tri.append(1)
    for d in tri:
        sh.path([(xm - 1.3, ey), (xm - 1.3, ey + d * 2.6), (xm + 1.3, ey)], "medium", closed=True)
    sh.text(xm - 2.2, ey - 2.4 if not other_side else ey + 1.0, size, 1.8, "end")
    if length:
        sh.text(xm + 2.0, ey - 2.4 if not other_side else ey + 1.0, length, 1.8)
    if all_round:
        sh.circle(ex, ey, 1.2, "thin")
    if note:
        sh.line(x1, ey, x1 + s * 2, ey + 1.5, "thin")
        sh.line(x1, ey, x1 + s * 2, ey - 1.5, "thin")
        sh.text(x1 + s * 3, ey - 0.6, note, 1.7, "start" if s > 0 else "end")


def rhs(sh, cx, cy, b, d, t, ro, k, rot=0.0, sty="shade"):
    """An RHS section of outer b x d (sheet x by y before rotation) at scale 1:k, centred on (cx, cy), cut face shaded."""
    def loop(w, h, r):
        pts = []
        for (qx, qy), a0 in (((w / 2 - r, h / 2 - r), 0), ((-w / 2 + r, h / 2 - r), 90), ((-w / 2 + r, -h / 2 + r), 180), ((w / 2 - r, -h / 2 + r), 270)):
            for j in range(7):
                a = math.radians(a0 + 15 * j)
                pts.append((qx + r * math.cos(a), qy + r * math.sin(a)))
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        return [(cx + (x * c - y * s) / k, cy + (x * s + y * c) / k) for x, y in pts]
    sh.multipath([loop(b, d, ro), loop(b - 2 * t, d - 2 * t, max(ro - t, 0.3))], sty)


def plate(sh, x0, y0, x1, y1, sty="shade"):
    sh.multipath([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], sty)


# ------------------------------------------------------------------ CT-101
def ct101(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, rep = _layout(prj, model)
    chs = _chassis()
    ch = lay.chassis
    V = ch.V
    sh = S.Sheet()
    S.frame(sh)
    sc = dwg["scale"]
    shapes = _shapes(lay)
    # ---- plan, looking down, X to the right, kerb side at the bottom
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=34.0, oy=246.0)
    vP.draw(shapes, sty="medium")
    S.view_label(sh, 110, 283, "PLAN, CHASSIS AND DRAWBAR", sc)
    hb = V["half_bw"]
    sh.text(vP.p(V["body_x0"], 0, 0)[0] - 3, vP.p(0, hb, 0)[1] - 1, "ROAD SIDE (Y +)", 1.8, "end")
    sh.text(vP.p(V["body_x0"], 0, 0)[0] - 3, vP.p(0, -hb, 0)[1] + 0.2, "KERB SIDE (Y -)", 1.8, "end")
    a, b = vP.p(-150, 0, 0), vP.p(V["body_x1"] + 150, 0, 0)
    sh.line(a[0], a[1], b[0], b[1], "centre")
    o = vP.p(0, 0, 0)
    sh.circle(o[0], o[1], 1.2, "medium")
    sh.text(o[0] - 1.5, o[1] + 1.8, "DATUM", 1.6, "end")
    yd = vP.p(0, hb, 0)[1] + 4
    S.hdim(sh, vP.p(0, 0, 0)[0], vP.p(0, hb, 0)[1], vP.p(V["body_x0"], 0, 0)[0], vP.p(0, hb, 0)[1], yd, f"{V['body_x0']:.0f}", size=1.8)
    S.hdim(sh, vP.p(V["body_x0"], 0, 0)[0], vP.p(0, hb, 0)[1], vP.p(V["body_x1"], 0, 0)[0], vP.p(0, hb, 0)[1], yd,
           f"{V['body_length']:.0f} RAILS", size=1.8)
    xr = vP.p(V["body_x1"], 0, 0)[0] + 12
    S.vdim(sh, xr - 12, vP.p(0, V["rail_outer_w"] / 2, 0)[1], xr - 12, vP.p(0, -V["rail_outer_w"] / 2, 0)[1], xr - 5,
           f"{V['rail_outer_w']:.0f} RAILS", size=1.7)
    S.vdim(sh, xr - 12, vP.p(0, hb, 0)[1], xr - 12, vP.p(0, -hb, 0)[1], xr + 1, f"{2 * hb:.0f} OUTRIGGERS", size=1.7)
    # station positions along the kerb side
    ys = vP.p(0, -hb, 0)[1] - 3
    for st in chs["stations"]:
        p = vP.p(st["x_centre"], -hb, 0)
        sh.line(p[0], p[1] - 0.5, p[0], ys + 0.6, "thin")
        sh.text(p[0] + 0.6, ys - 1.0, f"{st['x_centre']:.0f}", 1.5, rot=-90)
    sh.text(vP.p(V["body_x0"], 0, 0)[0] - 2, ys - 1.2, "STATION X", 1.5, "end")
    for m, txt, (dx, dy) in (("RL-R", "RL", (6, 12)), ("CM-02", "CM", (5, 7)), ("OR-05R", "OR", (-8, -6)), ("PB-2K", "PB", (6, 6)),
                             ("DB-KA", "DB", (-4, -9)), ("SP-PR", "SP", (-6, 8)), ("RS-K", "RS", (-6, -7))):
        mm = next(x for x in ch.members if x.id == m)
        c = mm.cog
        p = vP.p(c[0], c[1], 0)
        S.balloon(sh, p, (p[0] + dx, p[1] + dy), txt, 2.4)
    # ---- side elevation from the kerb side, X to the right
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=34.0, oy=152.0)
    vE.draw(shapes, sty="medium")
    S.view_label(sh, 110, 140, "ELEVATION FROM THE KERB SIDE", sc)
    g0, g1 = vE.p(-200, 0, 0), vE.p(V["body_x1"] + 200, 0, 0)
    sh.line(g0[0], g0[1], g1[0], g1[1], "thin")
    sh.text(g1[0], g1[1] + 0.8, "GROUND Z 0 AT DESIGN RIDE HEIGHT", 1.6, "end")
    levels = [(V["coupling_z"], "440 COUPLING POINT"), (V["rail_underside_z"], f"{V['rail_underside_z']:.0f} RAIL UNDERSIDE"),
              (V["rail_top_z"], f"{V['rail_top_z']:.0f} RAIL TOP"), (V["raiser_top_z"], f"{V['raiser_top_z']:.0f} RAISER TOP"),
              (V["floor_underside_z"], f"{V['floor_underside_z']:.0f} FLOOR UNDERSIDE"), (V["spare_post_top_z"], f"{V['spare_post_top_z']:.0f} SPARE POSTS")]
    xr = vE.p(V["body_x1"], 0, 0)[0] + 3
    ly = []
    for z, _ in levels:
        y = vE.p(0, 0, z)[1]
        ly.append(max(y, ly[-1] + 2.4) if ly else y)
    for (z, lab), yy in zip(levels, ly):
        y = vE.p(0, 0, z)[1]
        sh.line(xr, y, xr + 3, y, "thin")
        sh.line(xr + 3, y, xr + 5, yy, "thin")
        sh.text(xr + 5.5, yy - 0.6, lab, 1.6)
    for w in chs["suspension"]:
        if w["side"] < 0:
            p = vE.p(w["pivot"][0], 0, w["pivot"][2])
            sh.circle(p[0], p[1], 0.8, "medium")
            h = vE.p(w["hub"][0], 0, w["hub"][2])
            sh.line(p[0], p[1], h[0], h[1], "centre")
            sh.circle(h[0], h[1], V["tyre_d"] / 2 / sc, "phantom")
    sh.text(vE.p(V["axle_x"], 0, 0)[0], vE.p(0, 0, -150)[1], "TYRES AND ARMS PHANTOM, AT RIDE HEIGHT", 1.6, "middle")
    # ---- end views at 1:40
    sc2 = 40.0
    zl = V["rail_underside_z"] - 250
    vR = S.View(sh, (1, 0, 0), (0, 0, 1), sc2, ox=70.0, oy=62.0, anchor=(0, 0, zl))
    vR.draw(_shapes(lay, fittings=False), sty="medium")
    S.view_label(sh, 70, 112, "REAR END VIEW, LOOKING FORWARD", sc2)
    sh.text(vR.p(0, hb, 0)[0], 58, "ROAD SIDE", 1.7, "end")
    sh.text(vR.p(0, -hb, 0)[0], 58, "KERB SIDE", 1.7)
    vF = S.View(sh, (-1, 0, 0), (0, 0, 1), sc2, ox=170.0, oy=62.0, anchor=(0, 0, zl))
    vF.draw(_shapes(lay, fittings=False), sty="medium")
    S.view_label(sh, 170, 112, "FRONT END VIEW, LOOKING REARWARD", sc2)
    sh.text(vF.p(0, hb, 0)[0], 58, "ROAD SIDE", 1.7)
    sh.text(vF.p(0, -hb, 0)[0], 58, "KERB SIDE", 1.7, "end")
    for v in (vR, vF):
        a, b = v.p(0, -hb - 50, V["rail_underside_z"]), v.p(0, hb + 50, V["rail_underside_z"])
        sh.line(a[0], a[1], b[0], b[1], "centre")
    # ---- member schedule (right column)
    rows = []
    for r in chs["schedule"]:
        rows.append([r["section"], SHORT.get(r["role"], r["name"])[:46], f"{r['qty']}", f"{r['length_mm'] / 1000:.2f}", f"{r['mass_kg']:.1f}"])
    plates = sum(f["mass_kg"] for f in chs["fittings"] if f["kind"] in ("plate", "tube"))
    rows.append(["PLATE", "Plates, lugs, pads, gussets (CT-102, CT-103)", f"{sum(f['qty'] for f in chs['fittings'] if f['kind'] in ('plate', 'tube'))}",
                 "-", f"{plates:.1f}"])
    rows.append(["HDG", "Galvanising, inside and out", "-", f"{chs['galvanising']['area_m2']:.1f} m2", f"{chs['galvanising']['mass_kg']:.1f}"])
    yt = S.table(sh, 230.0, 247.0, [("SECTION", 30), ("MEMBERS", 84), ("QTY", 12), ("TOTAL m", 26), ("kg", 28)], rows, size=1.7, row_h=3.2,
                 title="MEMBER SCHEDULE (C450L0, LENGTHS ON THE CENTROID AXIS)")
    g = chs["results"]["governing"]
    rows = [[lc, g[lc]["member"], f"{g[lc]['eq']:.0f}", f"{g[lc]['limit']:.0f}", f"{g[lc]['util']:.2f}"]
            for lc in ("LC1", "LC2", "LC3", "LC4", "LC5a", "LC5b", "LC6", "LC6b", "LC8a", "LC8b")]
    yt = S.table(sh, 230.0, yt - 6, [("CASE", 16), ("GOVERNING MEMBER", 60), ("MPa", 30), ("LIMIT MPa", 34), ("UTIL.", 40)], rows,
                 size=1.7, row_h=3.0, title="FRAME ANALYSIS, PEAK COMBINED STRESS (CHASSIS.md)")
    S.notes(sh, 232, yt - 6, [
        f"STEEL {chs['steel_kg']:.0f} kg, GALVANISING {chs['galvanising']['mass_kg']:.0f} kg, BOUGHT PARTS {chs['bought_kg']:.0f} kg (CORNER STEADIES, COUPLING AND DRAWBAR FITTINGS).",
        "CUT LIST: chassis-cut-list.csv ON THE SITE'S DOWNLOADS PAGE, ONE ROW PER MEMBER AND PLATE.",
    ], width_chars=96, size=1.7, title="MASS AND CUT LIST")
    S.notes(sh, 22, 46, [
        "DATUM DIM-01: X FROM THE BALL CENTRE, POSITIVE REARWARD. Y FROM THE CENTRELINE, POSITIVE TO THE ROAD SIDE. Z UP FROM THE GROUND AT DESIGN RIDE HEIGHT.",
        "RAILS RHS 150x50x4 C450L0 WITH A CONTINUOUS RHS 127x51x3.5 C350L0 RAISER (ONE COMPOSITE SECTION), 20.5 mm FLOOR BEARER STRIP. NO WELD ACROSS THE WIDTH OF A RAIL (TB 070).",
        (f"REVISION {dwg['revisions'][-1]['rev']}: THE HOME TRAILER. AXLE GROUP CENTRE AT X {lay.V['axle_x']:,.0f} (H17). THE XT REAR SHOCK "
         "CROSSMEMBER IS RHS 150x50x4, A GREY-BAY FLOOR CROSSMEMBER CARRIES THE GREY TANK, NO PLAN BRACES BEHIND THE XT FRONT HINGE, "
         f"EVERY CASE AT THE {_forces()['plate']:.0f} kg PLATE. LOAD PATHS ON CT-104."),
        "XT CROSSMEMBERS AND BODY END CROSSMEMBERS FULL RAIL HEIGHT, NO HOLES. OTHER CROSSMEMBERS AND ALL OUTRIGGERS AT RAISER HEIGHT, TOPS FLUSH WITH THE RAISER.",
        "BURR-GRIND THE WELD TOES ON THE RAIL AT EVERY FULL-HEIGHT CROSSMEMBER (FAT-01). HOT-DIP GALVANISE THE WHOLE FRAME AFTER WELDING, VENTED TO report 02 WLD-05.",
        "SEE CHASSIS.md FOR THE LOAD CASES, THE RESULTS AND WHAT THE ENGINEER MUST CHECK.",
    ], width_chars=118, size=1.7)
    _draft_stamp(sh, 120, 124)
    _title(sh, dwg, reg, f"CHASSIS AND DRAWBAR {chs['steel_kg'] + chs['galvanising']['mass_kg']:.0f} kg GALVANISED (TB-11).", sc, chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-102
FIT_ITEMS = [("1", "DB-03", "Cruisemaster DO45 Plus, under-mounted, 4 x M14 8.8 at 140 Nm, nyloc nuts"),
             ("2", "CH-P01", "Coupling plate 300 x 220 x 12, both faces flat after galvanising (detail A)"),
             ("3", "CH-P02", "Chain lug 10 mm, 18 mm hole, each side (detail B)"),
             ("4", "DB-06", "Safety chains 8 mm grade 80 (T) to AS 2321, never welded, 2 t D shackles"),
             ("5", "CH-P11", "Jockey wheel bracket 8 mm, bolted to the kerb-side member"),
             ("6", "DB-05", "ARK XO750 jockey wheel, 750 kg, swung up in travel"),
             ("7", "DB-04", "Stone guard on the cross brace and member tops, on rubber"),
             ("8", "DB-BR", "Cross brace RHS 75 x 50 x 3 at mid-depth"),
             ("9", "CH-P03", "Root gusset 10 mm, 160 mm ground radius (FAT 90)"),
             ("10", "CH-P04", "Front recovery lug 20 mm, 22 mm hole, 4.75 t shackle"),
             ("11", "DB-07", "Breakaway kit, switch near the coupling"),
             ("12", "DB-KA", "Drawbar members RHS 150 x 50 x 5 C450L0")]


def ct102(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    lay, rep = _layout(prj, model)
    chs = _chassis()
    ch = lay.chassis
    V = ch.V
    sh = S.Sheet()
    S.frame(sh)
    sc = dwg["scale"]
    shapes = []
    for m in ch.members:
        if m.role in ("drawbar", "brace") or m.id in ("RL-K", "RL-R"):
            mm = m
            if m.role == "rail":
                mm = copy.copy(m)
                mm.p1 = (V["db_end_x"] + 200, m.p1[1], m.p1[2])
            shapes.append(member_solid(mm))
    for f in ch.fittings:
        if f.id.startswith("DB-") or f.id in ("CH-P01", "CH-P02", "CH-P03", "CH-P04", "CH-P11"):
            shapes.extend(fitting_solids(ch, f))
    x0 = -100.0
    # ---- plan, X to the right, kerb side at the bottom
    vP = S.View(sh, (0, 0, 1), (0, 1, 0), sc, ox=30.0, oy=232.0, anchor=(x0, 0, 0))
    vP.draw(shapes, sty="medium")
    S.view_label(sh, 110, 281, "PLAN OF THE DRAWBAR", sc)
    a, b = vP.p(x0, 0, 0), vP.p(V["db_end_x"] + 200, 0, 0)
    sh.line(a[0], a[1], b[0], b[1], "centre")
    yd = vP.p(0, -(V["rail_c"] + 100), 0)[1] - 6
    yb = vP.p(0, -V["rail_c"] - 25, 0)[1]
    S.hdim(sh, vP.p(0, 0, 0)[0], yb, vP.p(V["body_x0"], 0, 0)[0], yb, yd - 4, f"{V['body_x0']:.0f} BALL TO BODY FRONT", size=1.7)
    S.hdim(sh, vP.p(V["body_x0"], 0, 0)[0], yb, vP.p(V["db_end_x"], 0, 0)[0], yb, yd - 4, f"{V['db_tail']:.0f} UNDER THE RAIL", size=1.7)
    S.hdim(sh, vP.p(0, 0, 0)[0], yb, vP.p(V["db_apex_x"], 0, 0)[0], yb, yd - 10, f"{V['db_apex_x']:.0f}", size=1.7)
    S.hdim(sh, vP.p(V["db_apex_x"], 0, 0)[0], yb, vP.p(V["brace_x"], 0, 0)[0], yb, yd - 10, f"{V['brace_x'] - V['db_apex_x']:.0f} TO THE BRACE", size=1.7)
    a, b = vP.p(V["body_x0"] + 400, V["rail_c"], 0), vP.p(V["body_x0"] + 400, -V["rail_c"], 0)
    S.vdim(sh, a[0], a[1], b[0], b[1], a[0], f"{2 * V['rail_c']:.0f}", size=1.7, ext=False)
    sh.text(vP.p(V["db_end_x"] + 200, 0, 0)[0] + 1, vP.p(0, V["rail_c"], 0)[1], "ROAD SIDE", 1.6)
    sh.text(vP.p(V["db_end_x"] + 200, 0, 0)[0] + 1, vP.p(0, -V["rail_c"], 0)[1] - 1.5, "KERB SIDE", 1.6)
    # ---- elevation from the kerb side
    vE = S.View(sh, (0, -1, 0), (0, 0, 1), sc, ox=30.0, oy=112.0, anchor=(x0, 0, 0))
    vE.draw(shapes, sty="medium")
    S.view_label(sh, 110, 165, "ELEVATION FROM THE KERB SIDE", sc)
    g0, g1 = vE.p(x0, 0, 0), vE.p(V["db_end_x"] + 200, 0, 0)
    sh.line(g0[0], g0[1], g1[0], g1[1], "thin")
    sh.text(g1[0], g1[1] + 0.8, "GROUND Z 0", 1.6, "end")
    for z, lab in ((V["coupling_z"], f"{V['coupling_z']:.0f} COUPLING POINT"), (V["rail_underside_z"], f"{V['rail_underside_z']:.0f} RAIL UNDERSIDE")):
        p = vE.p(V["db_end_x"] + 200, 0, z)
        sh.line(p[0] + 1, p[1], p[0] + 4, p[1], "thin")
        sh.text(p[0] + 4.5, p[1] - 0.6, lab, 1.6)
    # ---- balloons to the fittings on the plan
    ch_f = {f.id: f for f in ch.fittings}
    spots = {"DB-03": (-40, 0), "CH-P01": (V["plate_x"] - 40, 60), "CH-P02": (V["chain_lug_x"], -ch.db_y(V["chain_lug_x"]) - 30),
             "DB-06": (V["chain_lug_x"], 0), "CH-P11": (V["jockey_x"], -ch.db_y(V["jockey_x"]) - 90), "DB-05": (V["jockey_x"] - 320, -ch.db_y(V["jockey_x"]) - 160),
             "DB-04": (600, 250), "DB-BR": (V["brace_x"], 120), "CH-P03": (V["body_x0"] - 120, V["rail_c"]),
             "CH-P04": (V["front_recovery_x"], -V["rail_c"] - 35), "DB-07": (700, -60), "DB-KA": (1300, -ch.db_y(1300))}
    up = {"DB-03": 1, "CH-P01": 1, "CH-P02": -1, "DB-06": 1, "CH-P11": -1, "DB-05": -1, "DB-04": 1, "DB-BR": 1, "CH-P03": 1, "CH-P04": -1,
          "DB-07": -1, "DB-KA": -1}
    used = {1: [], -1: []}
    for item, fid, _ in FIT_ITEMS:
        x, y = spots[fid]
        tip = vP.p(x, y, 0)
        d = up[fid]
        yy = vP.p(0, d * (V["rail_c"] + 70), 0)[1] + d * 2
        cx = tip[0]
        while any(abs(cx - u) < 7 for u in used[d]):
            cx += 7
        used[d].append(cx)
        S.balloon(sh, tip, (cx, yy), item, 2.6)
    # ---- detail A: coupling plate, 1:5
    k = 5.0
    cx, cy = 268.0, 235.0
    sh.text(cx, 262, "DETAIL A: COUPLING PLATE (2)", 2.3, "middle", bold=True)
    sh.text(cx, 258.5, "SCALE 1:5", 1.9, "middle")
    sh.rect(cx - 150 / k, cy - 110 / k, cx + 150 / k, cy + 110 / k, "medium")
    cp = ch.data["local_checks"]["coupling_plate"]
    ax, ay = cp["row_pitch"] / 2, cp["col_pitch"] / 2
    for dx in (-ax, ax):
        for dy in (-ay, ay):
            sh.circle(cx + dx / k, cy + dy / k, (cp["bolt_d"] + 1) / 2 / k, "medium")
    S.hdim(sh, cx - 150 / k, cy - 110 / k, cx + 150 / k, cy - 110 / k, cy - 110 / k - 4, "300", size=1.6)
    S.vdim(sh, cx + 150 / k, cy - 110 / k, cx + 150 / k, cy + 110 / k, cx + 150 / k + 4, "220", size=1.6)
    S.hdim(sh, cx - ax / k, cy + ay / k, cx + ax / k, cy + ay / k, cy + ay / k + 5, f"{cp['row_pitch']:.0f}", size=1.6)
    S.vdim(sh, cx - ax / k, cy - ay / k, cx - ax / k, cy + ay / k, cx - ax / k - 5, f"{cp['col_pitch']:.0f}", size=1.6)
    sh.text(cx, cy - 110 / k - 8.5, "4 HOLES 15 (M14) AT THE DO45 PLUS'S PATTERN (EST.): MEASURE ONE", 1.5, "middle")
    sh.text(cx, cy - 110 / k - 11, "BEFORE DRILLING. 12 mm GR 350.", 1.5, "middle")
    # ---- detail B: chain lug, 1:5
    cx, cy = 362.0, 226.0
    sh.text(cx, 262, "DETAIL B: CHAIN LUG (3)", 2.3, "middle", bold=True)
    sh.text(cx, 258.5, "SCALE 1:5", 1.9, "middle")
    sh.rect(cx - 90 / k, cy, cx + 90 / k, cy + 150 / k, "thin")
    sh.text(cx - 90 / k + 1, cy + 150 / k - 3, "MEMBER, OUTER FACE", 1.4)
    plate(sh, cx - 60 / k, cy - 40 / k, cx + 60 / k, cy + 60 / k)
    sh.circle(cx, cy - 15 / k, 9 / k, "medium")
    S.hdim(sh, cx - 60 / k, cy - 40 / k, cx + 60 / k, cy - 40 / k, cy - 40 / k - 4, "120", size=1.6)
    weld_symbol(sh, (cx + 60 / k, cy + 60 / k), (cx + 22, cy + 20), "6", both=True, length="120")
    sh.text(cx, cy - 40 / k - 9, "10 mm GR 350, HOLE 18 FOR THE 16 mm PIN,", 1.5, "middle")
    sh.text(cx, cy - 40 / k - 11.5, "15 BELOW THE MEMBER. WELD TOP AND BOTTOM EDGES.", 1.5, "middle")
    # ---- fittings table and local checks
    rows = []
    for item, fid, desc in FIT_ITEMS:
        f = ch_f.get(fid)
        kg = f"{f.mass_kg:.1f}" if f else next(f"{m['mass_kg']:.1f}" for m in chs["members"] if m["id"] == fid)
        rows.append([item, fid, desc[:70], kg])
    yt = S.table(sh, 232.0, 194.0, [("ITEM", 10), ("MARK", 16), ("DESCRIPTION", 134), ("kg", 16)], rows, size=1.6, row_h=3.0,
                 title="FITTINGS ON THE DRAWBAR")
    loc = chs["results"]["local"]
    rows = [[v["name"][:42], v["governing"][:32], f"{v['mpa']:.0f} / {v['limit_mpa']:.0f}", f"{100 * v['util']:.0f} %"] for v in loc.values()]
    S.table(sh, 232.0, yt - 6, [("FITTING", 70), ("GOVERNING PART", 56), ("MPa / LIMIT", 30), ("USE", 20)], rows, size=1.6, row_h=3.0,
            title="LOCAL CHECKS (CHASSIS.md)")
    S.notes(sh, 22, 64, [
        "DRAWBAR MEMBERS RHS 150x50x5 C450L0 FROM THE APEX (X 250, Y +/-60) TO THE RAIL CENTRES AT THE BODY FRONT, THEN 1000 UNDER EACH RAIL. CONTINUOUS 5 mm FILLETS ON BOTH EDGES TO THE RAIL UNDERSIDE, SNIPED TAPER END WITH THE TOE GROUND (CT-103 DETAIL D).",
        "NO WELD ON THE MEMBERS' TOP OR BOTTOM FACES WITHIN 300 OF THE BODY FRONT EXCEPT THE ROOT GUSSET. THE CROSS BRACE SITS AT MID-DEPTH.",
        ("VSB1 9.1 AT THE {plate:.0f} kg PLATE: {along:.1f} kN ALONG, {across:.1f} kN ACROSS AND {up:.1f} kN UP AND DOWN AT THE COUPLING. VSB1 9.2.2: "
         "{chain:.1f} kN ALONG AND {chain_up:.1f} kN VERTICAL AT EACH CHAIN LUG. EVIDENCE BY TEST OR APPROVED CALCULATION, FOR THE ENGINEER.").format(**_forces()),
        "NEVER USE THE COUPLING OR THE TOW PIN FOR RECOVERY. USE THE RECOVERY LUGS (10) AND THE REAR TONGUES ONLY.",
    ], width_chars=118, size=1.7)
    _draft_stamp(sh, 125, 82)
    _title(sh, dwg, reg, "DRAWBAR MEMBERS 2 x RHS 150x50x5 (TB-11).", sc, chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-103
def _detail_title(sh, cx, top, title, scale):
    sh.text(cx, top, title, 2.2, "middle", bold=True)
    sh.text(cx, top - 3.5, f"SCALE 1:{scale:g}", 1.9, "middle")


def ct103(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    chs = _chassis()
    P = chs["params"]
    comp = chs["composite"]
    rail_c = next(m["p0"][1] for m in chs["members"] if m["id"] == "RL-R")
    sh = S.Sheet()
    S.frame(sh)
    cols, top1, top2 = (56.0, 124.0, 192.0), 270.0, 168.0
    # ---- C: composite rail, section, 1:5
    k = 5.0
    cx = cols[0]
    _detail_title(sh, cx, top1, "C: COMPOSITE RAIL", k)
    zb = 205.0
    rhs(sh, cx, zb + 75 / k, 50, 150, 3, 6, k)
    rhs(sh, cx, zb + 212.5 / k, 50, 125, 3, 6, k)
    sh.rect(cx - 25 / k, zb + 275 / k, cx + 25 / k, zb + (275 + P["strip_t"]) / k, "medium")
    zc = zb + (comp["z_centroid"] - comp["z_bottom"]) / k
    sh.line(cx - 9, zc, cx + 9, zc, "centre")
    sh.text(cx + 9.5, zc - 0.6, "CENTROID", 1.5)
    S.vdim(sh, cx - 6, zb, cx - 6, zb + 150 / k, cx - 9, "150", size=1.6)
    S.vdim(sh, cx - 6, zb + 150 / k, cx - 6, zb + 275 / k, cx - 9, "125", size=1.6)
    S.leader(sh, (cx + 25 / k, zb + (275 + P["strip_t"] / 2) / k), (cx + 9, zb + 61), f"{P['strip_t']:.1f} BEARER STRIP", size=1.5)
    weld_symbol(sh, (cx + 25 / k, zb + 150 / k), (cx + 7, zb + 45), "4", both=True, note="CONTINUOUS")
    for i, t in enumerate((f"RAIL 150x50x4 C450L0 + RAISER 127x51x3.5 C350L0", f"I {comp['I'] / 1e6:.1f} x 10^6 mm4",
                           f"Z {comp['Z_bottom'] / 1e3:.1f} (BOTTOM), {comp['Z_top'] / 1e3:.1f} (TOP) x 10^3 mm3", "VENT EACH END OF EACH BAY")):
        sh.text(cx - 26, zb - 6 - 3 * i, t, 1.5)
    # ---- E: outrigger root, section along the outrigger, 1:10
    k = 10.0
    cx = cols[1]
    _detail_title(sh, cx, top1, "E: OUTRIGGER ROOT", k)
    x0, zb = cx - 30.0, 205.0
    rhs(sh, x0, zb + 75 / k, 50, 150, 3, 6, k, sty="medium")
    rhs(sh, x0, zb + 212.5 / k, 50, 125, 3, 6, k)
    L = (P["outrigger_tip_y"] - P["outrigger_root_y"]) / k
    sh.rect(x0 + 2.5, zb + 150 / k, x0 + 2.5 + L, zb + 275 / k, "medium")
    S.hdim(sh, x0 + 2.5, zb + 275 / k, x0 + 2.5 + L, zb + 275 / k, zb + 275 / k + 5, f"{P['outrigger_tip_y'] - P['outrigger_root_y']:.0f} TO THE BODY EDGE", size=1.6)
    weld_symbol(sh, (x0 + 2.5, zb + 150 / k), (x0 + 10, zb - 6), "6", all_round=True, note="ALL ROUND")
    for i, t in enumerate(("OUTRIGGER RHS 127x51x3.5, THE RAISER'S SECTION,", "TOP FLUSH WITH THE RAISER, BOTTOM AT THE", "RAIL TOP. THE ROOT CLASS (FAT 36) GOVERNS (FAT-05).")):
        sh.text(cx - 32, zb - 14 - 3 * i, t, 1.5)
    # ---- F: crossmember to rail, elevation on the rail's inner face, 1:5
    k = 5.0
    cx = cols[2]
    _detail_title(sh, cx, top1, "F: XT CROSSMEMBER TO RAIL", k)
    zb = 210.0
    sh.rect(cx - 25, zb, cx + 25, zb + 150 / k, "medium")
    sh.text(cx - 24.5, zb + 150 / k + 1, "RAIL, INNER FACE", 1.5)
    rhs(sh, cx, zb + 75 / k, 50, 150, 3, 6, k)
    sh.line(cx - 5, zb + 0.4, cx + 5, zb + 0.4, "thick")
    weld_symbol(sh, (cx + 25 / k, zb + 20), (cx - 8, zb + 40), "6", all_round=True, note="ALL ROUND")
    S.leader(sh, (cx, zb + 0.6), (cx + 10, zb - 6), "GRIND THE TOE ON THE RAIL", ["OVER THE BOTTOM 40 mm (FAT-01)"], size=1.5)
    for i, t in enumerate(("RHS 150x50x3, FULL RAIL HEIGHT, END SQUARE,", "NO HOLES (TB 070). HOT-SPOT CHECK BY THE", "ENGINEER (CIDECT DESIGN GUIDE 8).")):
        sh.text(cx - 26, zb - 16 - 3 * i, t, 1.5)
    # ---- D: end of the drawbar overlap, elevation, 1:10
    k = 10.0
    cx = cols[0]
    _detail_title(sh, cx, top2, "D: END OF THE DRAWBAR OVERLAP", k)
    xs, zb = cx - 30.0, 120.0
    sh.rect(xs, zb, xs + 60, zb + 150 / k, "medium")
    sh.text(xs + 0.5, zb + 150 / k + 1, "MAIN RAIL", 1.5)
    sh.path([(xs, zb), (xs + 25, zb), (xs + 25 + 300 / k, zb), (xs + 25, zb - 150 / k), (xs, zb - 150 / k)], "medium", closed=True)
    sh.text(xs + 0.5, zb - 150 / k - 3, "DRAWBAR RHS 150x50x5, SNIPED OVER 300, CAPPED", 1.5)
    weld_symbol(sh, (xs + 12, zb), (xs + 20, zb + 26), "5", both=True, note="CONTINUOUS")
    S.leader(sh, (xs + 25 + 300 / k, zb), (xs + 62, zb - 6), "WELD ENDS HERE,", ["TOE GROUND (IIW 712)"], size=1.5)
    sh.text(xs + 0.5, zb - 150 / k - 6, "NO TRANSVERSE WELD. ENDS AT X 2,820,", 1.5)
    sh.text(xs + 0.5, zb - 150 / k - 9, "BETWEEN CROSSMEMBERS.", 1.5)
    # ---- G: jacking pad, section across the rail at the XT centre crossmember, 1:5
    k = 5.0
    cx = cols[1]
    _detail_title(sh, cx, top2, "G: JACKING PAD", k)
    zb = 120.0
    rhs(sh, cx - 25, zb + 75 / k, 50, 150, 3, 6, k, sty="medium")
    sh.rect(cx - 25 + 25 / k, zb, cx + 25, zb + 150 / k, "medium")
    sh.text(cx + 1, zb + 150 / k + 1, "XT CENTRE CROSSMEMBER", 1.5, "middle")
    plate(sh, cx - 25 + 25 / k, zb - 10 / k, cx - 25 + 125 / k, zb)
    m = cx - 25 + 75 / k
    sh.path([(m - 5, zb - 2), (m - 3, zb - 6), (m + 3, zb - 6), (m + 5, zb - 2)], "medium")
    weld_symbol(sh, (cx - 25 + 125 / k, zb), (cx + 4, zb - 10), "5", both=True, length="100", note="ALONG THE CM")
    for i, t in enumerate(("PAD 100x100x10 WITH A LOCATING CUP, AGAINST", "THE RAIL'S INNER FACE. NO WELD ON THE RAIL'S",
                           f"BOTTOM FACE (FAT-11). {_forces()['pad']:.1f} kN ON ONE PAD.")):
        sh.text(cx - 32, zb - 18 - 3 * i, t, 1.5)
    # ---- H: rear recovery tongue, plan, 1:10
    k = 10.0
    cx = cols[2]
    _detail_title(sh, cx, top2, "H: REAR RECOVERY TONGUE, PLAN", k)
    yb = 130.0
    sh.rect(cx - 30, yb, cx + 10, yb + 50 / k, "medium")
    sh.text(cx - 29.5, yb + 50 / k + 1, "RAIL", 1.5)
    sh.rect(cx + 10 - 50 / k, yb - 30, cx + 10, yb + 50 / k, "medium")
    sh.text(cx + 11, yb - 29, "REAR CROSSMEMBER", 1.5)
    plate(sh, cx - 16, yb - 20 / k, cx + 10 + 70 / k, yb)
    sh.circle(cx + 10 + 45 / k, yb - 10 / k, 11 / k, "medium")
    weld_symbol(sh, (cx - 8, yb - 2 / k), (cx - 4, yb - 16), "6", both=True, length="200", note="ALONG ONLY")
    for i, t in enumerate(("TONGUE 20 mm GR 350, 22 HOLE, 4.75 t BOW", "SHACKLE, THROUGH A SLOT IN THE CROSSMEMBER.",
                           "{pull:.1f} kN AT 30 deg SIDEWAYS, {ult:.1f} kN ULTIMATE.".format(**_forces()))):
        sh.text(cx - 30, yb - 36 - 3 * i, t, 1.5)
    # ---- J: spare carrier posts, side elevation, 1:20 (right column)
    k = 20.0
    cx, zb = 380.0, 92.0
    h = (P["spare_post_top_z"] - 569.7) / k
    zs = zb + (P["spare_z"] - 569.7) / k
    _detail_title(sh, cx, max(172.0, zs + 375 / k + 7.0), "J: SPARE CARRIER POSTS", k)
    sh.rect(cx, zb, cx + 50 / k, zb + h, "medium")
    sh.rect(cx - 311 / k, zs - 375 / k, cx - 60 / k, zs + 375 / k, "phantom")
    sh.text(cx - 186 / k, zs + 375 / k - 3.0, "SPARE WHEEL", 1.4, "middle")
    sh.rect(cx + 50 / k, zb - 150 / k, cx + 100 / k, zb, "medium")
    sh.text(cx + 4, zb + h - 2, "SHS 50x50x2.5 x 2", 1.5)
    for i, t in enumerate(("POSTS BOLTED (M12) TO CLEATS ON THE FRONT", "CROSSMEMBER, TIED TO THE WALL AT THE TOP.", "NOTHING ON THE DRAWBAR (LOC-05).")):
        sh.text(cx - 55, zb - 12 - 3 * i, t, 1.5)
    # ---- fatigue table (right column)
    rows = []
    for f in chs["results"]["fatigue"]:
        col = "#000" if f["ok"] else "#c00"
        rows.append([f["id"], f["name"][:62], f"{f['fat']:g}", (f"{f['range_mpa']:.0f} / {f['cafl']:.0f}", col), (f"{f['damage']:.2f}", col),
                     "HS" if f["hot_spot"] else ""])
    S.table(sh, 230.0, 262.0, [("DETAIL", 13), ("JOINT", 103), ("FAT", 10), ("RANGE/CAFL", 24), ("MINER", 14), ("", 14)], rows,
            size=1.5, row_h=2.95, title="FATIGUE AT EACH WELDED DETAIL, LC10 (HS = HOT-SPOT CHECK)")
    S.notes(sh, 22, 64, [
        "WELDS SP TO AS/NZS 1554.1, E49XX OR W50X. VISUAL ON EVERY WELD, DYE PENETRANT OR MPI ON THE DRAWBAR TO CHASSIS JOINT, THE COUPLING MOUNT AND THE SUSPENSION BRACKETS (report 02 WLD-03).",
        "HOT-DIP GALVANISE AFTER FABRICATION TO AS/NZS 4680. VENT EVERY CLOSED SECTION AND SEALED SEAM BEFORE WELDING, HOLES AGREED WITH THE GALVANISER (report 02 WLD-05).",
        "FILLET SIZES ARE LEGS: 5 mm UNLESS STATED, 6 mm ON THE XT CROSSMEMBER ENDS, THE OUTRIGGER ROOTS, THE LUGS AND THE TONGUES.",
    ], width_chars=118, size=1.7)
    _draft_stamp(sh, 125, 75)
    _title(sh, dwg, reg, "SEE CT-101 FOR MASSES (TB-11).", 5, chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

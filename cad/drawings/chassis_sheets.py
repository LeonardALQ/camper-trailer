"""Chassis drawings CT-101 to CT-103 (A3, third angle), from the chassis design (cad/chassis.py) and its analysis
(build/chassis/chassis.json). Every sheet is DRAFT and not for construction until the engineer reviews CHASSIS.md.

CT-101: general arrangement, plan, side elevation, end views, member schedule and the cut list reference.
CT-102: drawbar and coupling: plan, elevation, coupling plate, chain lugs, jockey wheel bracket, front recovery lugs
        and stone guard.
CT-103: details, drawn as sections at their true sizes: the composite rail, outrigger root, crossmember to rail,
        the drawbar overlap's tapered end, the jacking pad, the rear recovery tongue and the spare carrier posts, with
        weld symbols to AS 1101.3, and the rails' front ends with their vent and drain holes for galvanising (K).
"""
from __future__ import annotations

import copy
import json
import math
import time

from ..build import BUILD, git_hash
from ..chassis import fitting_solids, member_solid
from ..chassis_fea import heel_throats
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


def weld_symbol(sh, tip, elbow, size: str, other_side=False, both=False, all_round=False, length: str = "", note: str = "",
                bevel=False, size_other: str = ""):
    """AS 1101.3 fillet weld symbol: arrow to the joint, reference line, the triangle below the line for the arrow
    side (above for the other side, both for both sides), the leg size on the left and the length on the right, a
    circle at the elbow for all round. `bevel` draws the single bevel butt weld's symbol in place of the triangle.
    `size_other` gives the other side's leg above the line where both sides are welded to different sizes. The arrow is
    marked as a leader to the joint it points at, so the overrun check sees it (I2-76). With `all_round` it ends on the
    elbow's circle."""
    (tx, ty), (ex, ey) = tip, elbow
    L = math.hypot(tx - ex, ty - ey) or 1
    r_ring = 1.2 if all_round else 0.0
    sh.lead([(tx, ty), (ex + (tx - ex) / L * r_ring, ey + (ty - ey) / L * r_ring)], names=tip)
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
        if bevel:
            sh.path([(xm - 1.3, ey + d * 2.6), (xm - 1.3, ey), (xm + 1.3, ey + d * 2.6)], "medium")
        else:
            sh.path([(xm - 1.3, ey), (xm - 1.3, ey + d * 2.6), (xm + 1.3, ey)], "medium", closed=True)
    sh.text(xm - 2.2, ey - 2.4 if not other_side else ey + 1.0, size, 1.8, "end")
    if size_other:
        sh.text(xm - 2.2, ey + 1.0, size_other, 1.8, "end")
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
            for lc in ("LC1", "LC2", "LC3", "LC4", "LC5a", "LC5b", "LC6", "LC6b", "LC8a", "LC8u", "LC8b")]
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
         "CROSSMEMBER AND THE REAR CROSSMEMBER ARE RHS 150x50x6, A GREY-BAY FLOOR CROSSMEMBER CARRIES THE GREY TANK, NO PLAN BRACES BEHIND THE XT FRONT HINGE, "
         f"EVERY CASE AT THE {_forces()['plate']:.0f} kg PLATE. LC8u IS LC8a AT THE 78.5 kN ULTIMATE ON EFFECTIVE SECTIONS (CHS-08U). LOAD PATHS ON CT-104."),
        "XT CROSSMEMBERS AND BODY END CROSSMEMBERS FULL RAIL HEIGHT, NO HOLES BUT THEIR DRAINS AND VENTS (CT-103). OTHER CROSSMEMBERS AND ALL OUTRIGGERS AT RAISER HEIGHT, TOPS FLUSH WITH THE RAISER.",
        "BURR-GRIND THE WELD TOES ON THE RAIL AT EVERY FULL-HEIGHT CROSSMEMBER (FAT-01). HOT-DIP GALVANISE THE WHOLE FRAME IN ONE DIP AFTER WELDING, HUNG AS CT-103 DETAIL K SAYS, VENTED TO report 02 WLD-05.",
        "SEE CHASSIS.md FOR THE LOAD CASES, THE RESULTS AND WHAT THE ENGINEER MUST CHECK.",
    ], width_chars=118, size=1.7)
    _draft_stamp(sh, 120, 124)
    _title(sh, dwg, reg, f"CHASSIS AND DRAWBAR {chs['steel_kg'] + chs['galvanising']['mass_kg']:.0f} kg GALVANISED (TB-11).", sc, chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-102
FIT_ITEMS = [("1", "DB-03", "Cruisemaster DO45 Plus, under-mounted, 4 x M14 8.8 at 140 Nm, nyloc nuts"),
             ("2", "CH-P01", "Coupling plate 300 x 220 x 12, both faces flat after galvanising (detail A)"),
             ("3", "CH-P02", "Chain lug 10 mm, 14 mm hole, each side (detail B)"),
             ("4", "DB-06", "Chains 8 mm grade 80 (T), pewag CW 8 links at the lugs, never welded"),
             ("5", "CH-P11", "Jockey wheel bracket 8 mm, bolted to the kerb-side member"),
             ("6", "DB-05", "ARK XO750 jockey wheel, 750 kg, swung up in travel"),
             ("7", "DB-04", "Stone guard on rubber, no mount at X 475 to 555 road side (DB-HK)"),
             ("8", "DB-BR", "Cross brace RHS 75 x 50 x 3 at mid-depth"),
             ("9", "CH-P03", "Root gusset 10 mm, 160 radius ground, toe 270 ahead of the body front"),
             ("10", "CH-P04", "Front recovery lug 20 mm, 22 mm hole, 4.75 t shackle"),
             ("11", "DB-07", "Breakaway kit, switch near the coupling"),
             ("12", "DB-KA", "Drawbar members RHS 150 x 50 x 6 C450L0"),
             ("13", "CH-P15", "Rail end plate 16 mm, full penetration to the rail's walls, the heel on it (detail C)")]
GALV_USES = {"vent", "drain", "drain and vent", "check"}       # the galvanising holes' uses among the holes' runs (CT-103 note 2, detail K)


def lift_slot(ch) -> float:
    """The slot over the rail's floor under its end plate CH-P15, mm (I2-79)."""
    return next(f for f in ch.data["fittings"] if f["id"] == "CH-P15").get("lift", 0.0) - ch.role_sec["rail"].t


def _root_detail(sh, ch, x0, y0, k=10.0):
    """Detail C on CT-102: the drawbar root in the root gusset's plane (I2-51), its lower left corner at sheet (x0, y0):
    the A-frame member's top, the gusset with its radius down to its end, the rail's end plate under its heel, the rail
    and the mitre, with the IIW details that hold them."""
    V = ch.V
    fit = {f["id"]: f for f in ch.data["fittings"]}
    g, ep, rail = fit["CH-P03"], fit["CH-P15"], ch.role_sec["rail"]
    xa, zt = V["root_gusset_toe_x"] - 30, V["rail_underside_z"]

    def p(x, z):
        return x0 + (x - xa) / k, y0 + 50 / k + (z - zt) / k

    x_end, x_front = V["body_x0"] - ep["t"], V["body_x0"] + 80
    lift = ep.get("lift", 0.0)
    _detail_title(sh, x0 + 80, y0 + 29, "DETAIL C: DRAWBAR ROOT IN THE GUSSET'S PLANE (9, 13)", k)
    a, b = p(xa, zt - 50), p(x_front, zt)
    sh.rect(a[0], a[1], b[0], b[1], "medium")
    sh.text(a[0] + 0.6, a[1] + 1.4, "MEMBER 150x50x6 (12), ITS TOP 50", 1.3)
    r, c, h, toe = g["r"], g["end_h"], g["w"], V["root_gusset_toe_x"]
    u1, u2 = math.sqrt(r ** 2 - (r - c) ** 2), math.sqrt(r ** 2 - (r - h) ** 2)
    arc = [p(toe - u1 + u, zt + r - math.sqrt(r ** 2 - u ** 2)) for u in (u1 + (u2 - u1) * j / 12 for j in range(13))]
    sh.path([p(toe, zt), p(toe, zt + c)] + arc + [p(x_end, zt + h), p(x_end, zt)], "medium", closed=True)
    plate(sh, *p(x_end, zt + lift), *p(V["body_x0"], zt + lift + ep["w"]))
    a, b = p(V["body_x0"], zt), p(x_front, zt + rail.d)
    sh.rect(a[0], a[1], b[0], b[1], "medium")
    sh.text(a[0] + 0.8, a[1] + 7.0, "RAIL", 1.3)          # between the end plate's leader and the heel's arrow
    m0, m1 = p(V["body_x0"], zt - 50), p(V["body_x0"], zt)
    sh.line(m0[0], m0[1], m1[0], m1[1], "thick")
    S.hdim(sh, p(toe, 0)[0], y0, p(V["body_x0"], 0)[0], y0, y0 - 3, f"{V['body_x0'] - toe:.0f} TO THE BODY FRONT", size=1.4)
    # the labels in a column on the right, top to bottom in the order their arrows reach the drawing, so no two cross
    ex = p(x_front, 0)[0] + 6
    weld_symbol(sh, p(V["body_x0"], zt + 0.85 * rail.d), (ex, y0 + 22.5), "", bevel=True,
                note="PLATE TO THE WEBS AND TOP: FULL PENETRATION FROM OUTSIDE (FAT-20),")
    sh.text(ex + 19, y0 + 19.5, "EACH ROOT INSPECTED BY VIDEOSCOPE FROM INSIDE THE RAIL (NOTE 3)", 1.7)
    weld_symbol(sh, p(x_end, zt + 0.7 * h), (ex, y0 + 16.5), "", both=True, note="HEEL TO THE END PLATE (FAT-18), SIZED AND PLACED AS VIEW C1")
    S.leader(sh, p(V["body_x0"] - ep["t"] / 2, zt + 0.3 * rail.d), (ex, y0 + 11.0),
             f"END PLATE {ep['t']:g} GR 350 (13) OVER THE RAIL AND THE RAISER'S BOTTOM WALL, ITS BOTTOM EDGE {lift:g} UP AND FREE (FAT-19)", size=1.4)
    S.leader(sh, p(toe + 45, zt + r - math.sqrt(r ** 2 - (u1 + 45) ** 2)), (ex, y0 + 7.0),
             f"GUSSET {g['t']:g} GR 350 (9), {h:g} HIGH AT ITS HEEL: R{r:g} GROUND, END {c:g} HIGH (2t = {2 * g['t']:g} AT MOST),",
             ["5 FILLETS BOTH SIDES WRAPPED ROUND THAT END, TOE GROUND (IIW 522, FAT-07)"], size=1.4)
    S.leader(sh, (m0[0], (m0[1] + m1[1]) / 2), (ex, y0 - 0.5), "MITRE: FULL PENETRATION FROM ONE SIDE, WELDED FLAT,",
             ["IIW 234 AT FAT 36, SO ITS ROOT NEEDS NO NDT (FAT-17)"], size=1.4)


def _heel_view(sh, ch, x0, y0, k=2.0):
    """View C1 on CT-102: the kerb side's end plate CH-P15 from ahead, its inboard edge on the left at sheet x0 and its
    bottom edge at y0, with the root gusset's heel cut just ahead of it (I2-60): where the data puts the heel's centre
    across the plate (root_gusset_heel_y), dimensioned from the plate's inboard edge, and the member's line there."""
    V = ch.V
    fit = {f["id"]: f for f in ch.data["fittings"]}
    g, ep, rail = fit["CH-P03"], fit["CH-P15"], ch.role_sec["rail"]
    edge = V["rail_c"] - rail.b / 2
    heel = V["root_gusset_heel_y"] - edge
    member = ch.db_y(V["root_gusset_toe_x"] + g["l"]) - edge
    half = g["t"] / 2 / math.cos(math.atan(V["root_gusset_slope"]))

    def p(u, z):
        return x0 + u / k, y0 + z / k
    lift = ep.get("lift", 0.0)              # the plate's bottom edge over the rail's underside, where the gusset stands (the lap's 2.5 mm not drawn)
    yb = p(0, lift)[1]
    cx = p(rail.b / 2, 0)[0]
    sh.text(cx, y0 + (lift + ep["w"]) / k + 7.5, "VIEW C1: END PLATE FROM AHEAD (13)", 1.7, "middle", bold=True)
    sh.text(cx, y0 + (lift + ep["w"]) / k + 4.8, f"SCALE 1:{k:g}, KERB SIDE, ROAD SIDE MIRRORED", 1.4, "middle")
    sh.rect(*p(0, lift), *p(rail.b, lift + ep["w"]), "medium")
    plate(sh, *p(heel - half, 0), *p(heel + half, g["w"]))
    legs = g["heel_legs"]
    for u0, u1 in ((heel - half - legs[0], heel - half), (heel + half, heel + half + legs[1])):
        sh.rect(*p(u0, lift), *p(u1, g["w"]), "thin")
    throat = min(heel_throats(legs, math.atan(V["root_gusset_slope"])))
    weld_symbol(sh, p(heel - half - legs[0] / 2, 120.0), (x0 - 6.0, y0 + 60.0), f"{legs[0]:g}", both=True, size_other=f"{legs[1]:g}",
                note=f"LEGS {legs[0]:g} INBOARD AND {legs[1]:g} OUTBOARD, THROAT {throat:.1f} BOTH SIDES")
    a, b = p(member, -3), p(member, g["w"] + 6)
    sh.line(a[0], a[1], b[0], b[1], "centre")
    sh.text(x0 - 1.2, y0 + 1.0, "INBOARD", 1.3, rot=-90)
    sh.text(p(rail.b, 0)[0] + 2.3, y0 + 1.0, "OUTBOARD", 1.3, rot=-90)
    S.hdim(sh, x0, yb, p(heel, 0)[0], yb, y0 - 4.5, f"{heel:.0f}", size=1.4)
    S.hdim(sh, x0, yb, p(rail.b, 0)[0], yb, y0 - 9.5, f"{rail.b:.0f}", size=1.4)
    S.leader(sh, p(heel, 0.5 * g["w"]), (x0 - 4.0, y0 + 0.4 * (lift + ep["w"]) / k), "GUSSET (9),", ["CUT AHEAD"], size=1.3)
    note = (f"THE GUSSET'S HEEL STANDS WITH ITS CENTRE {heel:.0f} FROM THE PLATE'S INBOARD EDGE, {rail.b / 2 - heel:.0f} INBOARD OF ITS "
            f"MIDDLE AND {heel - member:.1f} OUTBOARD OF THE MEMBER'S LINE (CENTRE LINE). ITS TOE STAYS ON THE MEMBER'S CENTRE. "
            f"THE WEBS' WELDS THEN SHARE ITS PULL (FAT-20). THE PLATE'S BOTTOM EDGE STANDS {lift:g} OVER THE RAIL'S UNDERSIDE.")
    for i, t in enumerate(S.wrap_mm(note, 42.0, 1.3)):
        sh.text(x0 - 16.0, y0 - 13.0 - 2.2 * i, t, 1.3)


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
        if f.id.startswith("DB-") or f.id in ("CH-P01", "CH-P02", "CH-P03", "CH-P04", "CH-P11", "CH-P15"):
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
             "CH-P04": (V["front_recovery_x"], -V["rail_c"] - 35), "DB-07": (700, -60), "DB-KA": (1300, -ch.db_y(1300)),
             "CH-P15": (V["body_x0"] - 8, -V["rail_c"])}
    up = {"DB-03": 1, "CH-P01": 1, "CH-P02": -1, "DB-06": 1, "CH-P11": -1, "DB-05": -1, "DB-04": 1, "DB-BR": 1, "CH-P03": 1, "CH-P04": -1,
          "DB-07": -1, "DB-KA": -1, "CH-P15": -1}
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
    lug = ch.data["local_checks"]["chain_lug"]
    low = 15 + lug["edge"]                      # the lug's lower edge under the member, the hole 15 under it
    plate(sh, cx - 60 / k, cy - low / k, cx + 60 / k, cy + (100 - low) / k)
    sh.circle(cx, cy - 15 / k, lug["hole"] / 2 / k, "medium")
    S.hdim(sh, cx - 60 / k, cy - low / k, cx + 60 / k, cy - low / k, cy - low / k - 4, "120", size=1.6)
    weld_symbol(sh, (cx + 60 / k, cy + (100 - low) / k), (cx + 22, cy + 20), "6", both=True, length="120")
    sh.text(cx, cy - low / k - 9, f"10 mm GR 350, HOLE {lug['hole']:g} FOR THE CW 8 LINK,", 1.5, "middle")
    sh.text(cx, cy - low / k - 11.5, f"15 BELOW THE MEMBER, {lug['edge'] - lug['hole'] / 2:g} OF PLATE UNDER IT.", 1.5, "middle")
    sh.text(cx, cy - low / k - 14, "WELD TOP AND BOTTOM EDGES. NO SHACKLE HERE.", 1.5, "middle")
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
    _root_detail(sh, ch, 240.0, 80.0)
    _heel_view(sh, ch, 202.0, 36.0)
    g_legs = next(f for f in ch.data["fittings"] if f["id"] == "CH-P03")["heel_legs"]
    g_throat = min(heel_throats(g_legs, math.atan(V["root_gusset_slope"])))
    ep_lift = next(f for f in ch.data["fittings"] if f["id"] == "CH-P15").get("lift", 0)
    gaps = [h["x"] - V["body_x0"] for h in chs["results"]["holes"] if (h.get("frame") or "").startswith("RL-")
            and h["wall"].startswith("the rail's") and 0 < h["x"] - V["body_x0"] <= 150 and not set(h["runs"]) & GALV_USES]
    hole_gap = (min(gaps), max(gaps))      # the front cable holes the videoscope goes in by (FAT-20)
    fat20 = next(f for f in chs["results"]["fatigue"] if f["id"] == "FAT-20")
    S.notes(sh, 22, 72, [
        ("DRAWBAR MEMBERS RHS 150x50x6 C450L0 FROM THE APEX (X 250, Y +/-60) TO THE RAIL CENTRES AT THE BODY FRONT, THEN 1000 UNDER EACH RAIL, "
         "THE LAP 2.5 OPEN ON 8 mm STITCH FILLETS 50 LONG AT 100 ON BOTH EDGES (FAT-21), SNIPED TAPER END WITH THE TOE GROUND (CT-103 DETAIL D). "
         "DRAINS AND VENTS AS CT-103 NOTE 2."),
        ("NO WELD ON THE MEMBERS' TOP OR BOTTOM FACES WITHIN 300 OF THE BODY FRONT EXCEPT THE ROOT GUSSET (9) AND THE MITRE (DETAIL C). THE GUSSET IS IIW 522, "
         "FAT 90 (FAT-07): ITS 160 RADIUS GROUND SMOOTH DOWN TO AN END 10 HIGH, AT MOST TWICE ITS 10 mm, 270 AHEAD OF THE BODY FRONT, ITS FILLETS WRAPPED "
         "ROUND THAT END AND THE TOE GROUND. THE CROSS BRACE SITS AT MID-DEPTH."),
        ("A 16 mm END PLATE (13) CLOSES EACH RAIL'S FRONT END AND THE RAISER'S BOTTOM WALL OVER IT AND TAKES THE GUSSET'S HEEL ON FILLETS "
         f"{g_legs[0]:g} INBOARD AND {g_legs[1]:g} OUTBOARD, THROAT {g_throat:.1f} (VIEW C1, FAT-18, FAT-19). ITS EDGES ON THE WEBS AND THE TOP ARE BEVELLED, "
         "AND THE WALLS ARE WELDED TO IT WITH FULL PENETRATION FROM OUTSIDE, THE INBOARD WEB FROM AHEAD OF THE FRONT CROSSMEMBER, THE PLATE BEHIND EACH "
         f"ROOT. ITS BOTTOM EDGE STANDS {ep_lift:g} UP, UNWELDED, OVER A {ep_lift - ch.role_sec['rail'].t:g} SLOT (CT-103 DETAIL K). BEFORE GALVANISING THE INSPECTOR VIEWS EACH ROOT "
         f"ALONG ITS WHOLE LENGTH BY VIDEOSCOPE THROUGH THE FRONT CABLE HOLES, {hole_gap[0]:.0f} TO {hole_gap[1]:.0f} BEHIND THE PLATE, OR THE "
         "DRAINS, TO A WRITTEN REMOTE VISUAL PROCEDURE (AS 3978) IN WHICH THE SCOPE IS SHOWN TO RESOLVE THE ROOT AT ITS WORKING DISTANCE, AND RECORDS IT. "
         "THE RECORD PASSES ONLY IF IT SHOWS COMPLETE ROOT FUSION ALONG EACH ROOT'S WHOLE LENGTH, THE TOP CORNERS AND THE WEBS' BOTTOM ENDS INCLUDED, "
         f"AND NO CRACK (IIW {fat20['iiw']} AT FAT {fat20['fat']:g}, FAT-20). THE MITRE UNDER IT IS A FULL PENETRATION BUTT WELD MADE FROM ONE SIDE ON "
         "THE BENCH, EACH FACE WELDED FLAT, BEFORE THE MEMBER GOES UNDER THE RAIL: IIW 234 AT FAT 36, SO ITS ROOT NEEDS NO NDT (FAT-17)."),
        ("VSB1 9.1 AT THE {plate:.0f} kg PLATE: {along:.1f} kN ALONG, {across:.1f} kN ACROSS AND {up:.1f} kN UP AND DOWN AT THE COUPLING. VSB1 9.2.2: "
         "{chain:.1f} kN ALONG AND {chain_up:.1f} kN VERTICAL AT EACH CHAIN LUG. EVIDENCE BY TEST OR APPROVED CALCULATION, FOR THE ENGINEER.").format(**_forces()),
        "NEVER USE THE COUPLING OR THE TOW PIN FOR RECOVERY. USE THE RECOVERY LUGS (10) AND THE REAR TONGUES ONLY.",
    ], width_chars=118, size=1.7)
    _draft_stamp(sh, 125, 87)
    _title(sh, dwg, reg, "DRAWBAR MEMBERS 2 x RHS 150x50x6 (TB-11).", sc, chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0


# ------------------------------------------------------------------ CT-103
def _detail_title(sh, cx, top, title, scale):
    sh.text(cx, top, title, 2.2, "middle", bold=True)
    sh.text(cx, top - 3.5, f"SCALE 1:{scale:g}", 1.9, "middle")


def _clip(text: str, n: int) -> str:
    """The text cut at its last whole word within n characters, before a bracket it would leave open, its trailing
    comma dropped."""
    if len(text) <= n:
        return text
    out = text[:n + 1].rsplit(" ", 1)[0]
    if out.count("(") > out.count(")"):
        out = out[:out.rfind(" (")]
    return out.rstrip(",")


def _galv_detail(sh, ch, holes, x0, y0, k=5.0):
    """Detail K on CT-103: the kerb-side rail's front end from outside, at 1:5, its lower left corner at sheet (x0, y0),
    X to the right as CT-102's elevation: the outer web with its drains for galvanising and the front bay's cable hole,
    the inner web's drains beyond it, hidden, the end plate and the slot under it, the drawbar member under the rail and
    the raiser over it (I2-75, I2-79)."""
    V = ch.V
    ep = next(f for f in ch.data["fittings"] if f["id"] == "CH-P15")
    rail = ch.role_sec["rail"]
    xa, xb, za, zb = V["body_x0"] - 40, V["body_x0"] + 160, V["rail_underside_z"] - 37.5, V["raiser_top_z"] - 74.5
    z0, zs, lift = V["rail_underside_z"], V["rail_top_z"], ep.get("lift", 0.0)

    def p(x, z):
        return x0 + (x - xa) / k, y0 + (z - za) / k
    kerb = [h for h in holes if h.get("frame") == "RL-K" and h["wall"] in ("the rail's outer web", "the rail's inner web")
            and h["x"] < V["body_x0"] + 150]
    galv = sorted((h for h in kerb if set(h["runs"]) & GALV_USES), key=lambda h: h["x"])
    outer = [h for h in galv if h["wall"] == "the rail's outer web"]
    inner = [h for h in galv if h["wall"] == "the rail's inner web"]
    cable = [h for h in kerb if not set(h["runs"]) & GALV_USES and h["wall"] == "the rail's outer web"]
    road = next(h for h in holes if h.get("frame") == "RL-R" and h["wall"] == "the rail's outer web" and h["x"] < V["body_x0"] + 150
                and not set(h.get("runs", [])) & GALV_USES)
    _detail_title(sh, p((xa + xb) / 2, 0)[0], y0 + (zb - za) / k + 15.0, "K: RAIL'S FRONT END FOR GALVANISING", k)
    sh.text(p((xa + xb) / 2, 0)[0], y0 + (zb - za) / k + 8.0, "FROM OUTSIDE, KERB SIDE. ROAD SIDE MIRRORED, ITS CABLE", 1.4, "middle")
    sh.text(p((xa + xb) / 2, 0)[0], y0 + (zb - za) / k + 5.6,
            f"HOLE {road['runs'][0]}'S {road['d']:.0f} AT {road['x'] - V['body_x0']:.0f} BEHIND THE PLATE ({road['id']})", 1.4, "middle")
    gw = next(f for f in ch.data["fittings"] if f["id"] == "CH-P03")["w"]
    for (x_0, z_0), (x_1, z_1), sty in (((V["body_x0"], z0), (V["body_x0"], zb), "medium"), ((V["body_x0"], z0), (xb, z0), "medium"),
                                        ((V["body_x0"], zs), (xb, zs), "medium"), ((xa, z0), (V["body_x0"], z0), "medium"),
                                        ((xb, za), (xb, zb), "thin"), ((xa, za), (xb, za), "thin"), ((xa, za), (xa, z0), "thin"),
                                        ((V["body_x0"], zb), (xb, zb), "thin"),
                                        ((xa, z0 + gw), (V["body_x0"] - ep["t"], z0 + gw), "phantom"),      # the gusset beyond
                                        ((V["body_x0"] - ep["t"], z0), (V["body_x0"] - ep["t"], z0 + lift), "phantom")):
        a, b = p(x_0, z_0), p(x_1, z_1)
        sh.line(a[0], a[1], b[0], b[1], sty)
    for z in (z0 + rail.ro, zs - rail.ro):          # the web's flat between the corner radii, which CHS-10 measures from
        a, b = p(V["body_x0"], z), p(xb, z)
        sh.line(a[0], a[1], b[0], b[1], "thin")
    a, b = p(V["body_x0"] - ep["t"], z0 + lift), p(V["body_x0"], z0 + lift + ep["w"])
    sh.rect(a[0], a[1], b[0], b[1], "medium")
    sh.text(p(V["body_x0"] + 100, 0)[0], p(0, za)[1] + 1.0, "MEMBER (CT-102, 12)", 1.3, "middle")      # clear of the plate's leader
    sh.text(p(V["body_x0"], 0)[0] + 0.8, p(0, zb)[1] - 2.4, "RAISER", 1.3)
    for h in outer + cable:
        c = p(h["x"], h["z"])
        sh.circle(c[0], c[1], h["d"] / 2 / k, "medium")
        sh.line(c[0] - h["d"] / k, c[1], c[0] + h["d"] / k, c[1], "centre")
        sh.line(c[0], c[1] - h["d"] / k, c[0], c[1] + h["d"] / k, "centre")
    for h in inner:                              # in the inner web, beyond: hidden
        c = p(h["x"], h["z"])
        sh.circle(c[0], c[1], h["d"] / 2 / k, "hidden")
    ex = p(xb, 0)[0] + 7.0

    def edge_towards(h, elbow):
        c = p(h["x"], h["z"])
        L = math.hypot(elbow[0] - c[0], elbow[1] - c[1])
        r = h["d"] / 2 / k
        return c[0] + (elbow[0] - c[0]) / L * r, c[1] + (elbow[1] - c[1]) / L * r
    if cable:
        elbow = (ex, p(0, cable[0]["z"])[1] - 1.5)
        S.leader(sh, edge_towards(cable[0], elbow), elbow, f"{cable[0]['runs'][0]}'S CABLE HOLE {cable[0]['d']:.0f}",
                 [f"({cable[0]['id']}, CHS-10)"], size=1.5)
    elbow = (ex, p(0, z0)[1] + 4.0)
    S.leader(sh, edge_towards(inner[-1], elbow), elbow, f"{len(galv)} DRAINS {galv[0]['d']:.0f}, {galv[0]['z'] - z0:.0f} OVER THE UNDERSIDE:",
             [f"OUTER WEB {outer[0]['x'] - V['body_x0']:.0f} AND {outer[-1]['x'] - V['body_x0']:.0f} BEHIND THE PLATE ({outer[0]['id']}, {outer[-1]['id']}),",
              f"INNER WEB {inner[0]['x'] - V['body_x0']:.0f} AND {inner[-1]['x'] - V['body_x0']:.0f}, HIDDEN ({inner[0]['id']}, {inner[-1]['id']})"], size=1.5)
    tip = p(V["body_x0"] - ep["t"] / 2, z0 + lift)
    S.leader(sh, tip, (tip[0] + 6.0, y0 - 4.0), f"END PLATE (CT-102, 13), ITS BOTTOM EDGE {lift:g} UP: A {lift - rail.t:g} SLOT OVER THE FLOOR", size=1.5)


def ct103(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    chs = _chassis()
    P = chs["params"]
    comp = chs["composite"]
    rail_c = next(m["p0"][1] for m in chs["members"] if m["id"] == "RL-R")
    lay, _ = _layout(prj, model)
    sec = lay.chassis.role_sec
    rl, rs, xt = sec["rail"], sec["raiser"], sec["cm_xt"]
    sh = S.Sheet()
    S.frame(sh)
    cols, top1, top2 = (56.0, 124.0, 192.0), 270.0, 168.0
    # ---- C: composite rail, section, 1:5, the rail and the raiser at their true sizes and corner radii
    k = 5.0
    cx = cols[0]
    _detail_title(sh, cx, top1, "C: COMPOSITE RAIL", k)
    zb = 205.0
    h_rl, h_all = rl.d / k, (rl.d + rs.d) / k
    rhs(sh, cx, zb + rl.d / 2 / k, rl.b, rl.d, rl.t, rl.ro, k)
    rhs(sh, cx, zb + (rl.d + rs.d / 2) / k, rs.b, rs.d, rs.t, rs.ro, k)
    sh.rect(cx - rs.b / 2 / k, zb + h_all, cx + rs.b / 2 / k, zb + h_all + P["strip_t"] / k, "medium")
    zc = zb + (comp["z_centroid"] - comp["z_bottom"]) / k
    sh.line(cx - 9, zc, cx + 9, zc, "centre")
    sh.text(cx + 9.5, zc - 0.6, "CENTROID", 1.5)
    S.vdim(sh, cx - 6, zb, cx - 6, zb + h_rl, cx - 9, f"{rl.d:g}", size=1.6)
    S.vdim(sh, cx - 6, zb + h_rl, cx - 6, zb + h_all, cx - 9, f"{rs.d:g}", size=1.6)
    S.leader(sh, (cx + rs.b / 2 / k, zb + h_all + P["strip_t"] / 2 / k), (cx + 9, zb + 61), f"{P['strip_t']:.1f} BEARER STRIP", size=1.5)
    weld_symbol(sh, (cx + rl.b / 2 / k, zb + h_rl), (cx + 7, zb + 45), "4", both=True, note="CONTINUOUS")
    for i, t in enumerate((f"RAIL {rl.d:g}x{rl.b:g}x{rl.t:g} C450L0, CORNERS R{rl.ro:g}",
                           f"+ RAISER {rs.d:g}x{rs.b:g}x{rs.t:g} C350L0, CORNERS R{rs.ro:g}",
                           f"I {comp['I'] / 1e6:.1f} x 10^6 mm4",
                           f"Z {comp['Z_bottom'] / 1e3:.1f} (BOTTOM), {comp['Z_top'] / 1e3:.1f} (TOP) x 10^3 mm3", "VENT EACH END OF EACH BAY")):
        sh.text(cx - 26, zb - 6 - 3 * i, t, 1.5)
    # ---- E: outrigger root, section along the outrigger, 1:10
    k = 10.0
    cx = cols[1]
    _detail_title(sh, cx, top1, "E: OUTRIGGER ROOT", k)
    x0, zb = cx - 30.0, 205.0
    h_rl, h_all = rl.d / k, (rl.d + rs.d) / k
    rhs(sh, x0, zb + rl.d / 2 / k, rl.b, rl.d, rl.t, rl.ro, k, sty="medium")
    rhs(sh, x0, zb + (rl.d + rs.d / 2) / k, rs.b, rs.d, rs.t, rs.ro, k)
    L = (P["outrigger_tip_y"] - P["outrigger_root_y"]) / k
    xr = x0 + rs.b / 2 / k
    sh.rect(xr, zb + h_rl, xr + L, zb + h_all, "medium")
    S.hdim(sh, xr, zb + h_all, xr + L, zb + h_all, zb + h_all + 5, f"{P['outrigger_tip_y'] - P['outrigger_root_y']:.0f} TO THE BODY EDGE", size=1.6)
    weld_symbol(sh, (xr, zb + h_rl), (x0 + 10, zb - 6), "6", all_round=True, note="ALL ROUND")
    for i, t in enumerate(("OUTRIGGER RHS 127x51x3.5, THE RAISER'S SECTION,", "TOP FLUSH WITH THE RAISER, BOTTOM AT THE", "RAIL TOP. THE ROOT CLASS (FAT 36) GOVERNS (FAT-05).")):
        sh.text(cx - 32, zb - 14 - 3 * i, t, 1.5)
    # ---- F: crossmember to rail, elevation on the rail's inner face, 1:5, the rail's flat between its corner radii
    k = 5.0
    cx = cols[2]
    _detail_title(sh, cx, top1, "F: XT CROSSMEMBER TO RAIL", k)
    zb = 210.0
    sh.rect(cx - 25, zb, cx + 25, zb + rl.d / k, "medium")
    for z in (rl.ro, rl.d - rl.ro):
        sh.line(cx - 25, zb + z / k, cx + 25, zb + z / k, "thin")
    sh.text(cx - 24.5, zb + rl.d / k + 3.8, f"RAIL {rl.d:g}x{rl.b:g}x{rl.t:g}, R{rl.ro:g},", 1.5)    # clear of the weld symbol's arrow
    sh.text(cx - 24.5, zb + rl.d / k + 1, "ITS INNER FACE", 1.5)
    rhs(sh, cx, zb + xt.d / 2 / k, xt.b, xt.d, xt.t, xt.ro, k)
    sh.line(cx - 5, zb + 0.4, cx + 5, zb + 0.4, "thick")
    weld_symbol(sh, (cx + xt.b / 2 / k, zb + 20), (cx - 8, zb + 40), "6", all_round=True, note="ALL ROUND")
    S.leader(sh, (cx, zb + 0.6), (cx - 10, zb - 6), "GRIND THE TOE ON THE RAIL", ["OVER THE BOTTOM 40 mm (FAT-01)"], size=1.5)   # clear of the fatigue table
    for i, t in enumerate((f"RHS {xt.d:g}x{xt.b:g}x{xt.t:g}, FULL RAIL HEIGHT, END SQUARE,", "ONLY ITS DRAINS AND VENTS (NOTE 2, TB 070,", "CHS-09, CHS-10). HOT-SPOT CHECK BY THE ENGINEER.")):
        sh.text(cx - 26, zb - 16 - 3 * i, t, 1.5)
    # ---- D: end of the drawbar overlap, elevation, 1:10, the lap opened 2.5 and stitch welded (FAT-21)
    k = 10.0
    cx = cols[0]
    _detail_title(sh, cx, top2, "D: END OF THE DRAWBAR OVERLAP", k)
    xs, zb = cx - 30.0, 120.0
    gap = 2.5 / k
    sh.rect(xs, zb, xs + 60, zb + rl.d / k, "medium")
    sh.text(xs + 0.5, zb + rl.d / k + 1, "MAIN RAIL", 1.5)
    sh.path([(xs, zb - gap), (xs + 25, zb - gap), (xs + 25 + 300 / k, zb - gap), (xs + 25, zb - gap - 150 / k), (xs, zb - gap - 150 / k)], "medium", closed=True)
    sh.text(xs + 0.5, zb - gap - 150 / k - 3, "DRAWBAR RHS 150x50x6, SNIPED OVER 300, OPEN", 1.5)
    weld_symbol(sh, (xs + 12, zb), (xs + 20, zb + 26), "8", both=True, length="50-100", note="STITCH, LAP OPEN 2.5")
    S.leader(sh, (xs + 25 + 300 / k, zb), (xs + 62, zb - 6), "WELD ENDS HERE,", ["TOE GROUND (IIW 712)"], size=1.5)
    sh.text(xs + 0.5, zb - gap - 150 / k - 6, "NO TRANSVERSE WELD. ENDS AT X 2,820,", 1.5)
    sh.text(xs + 0.5, zb - gap - 150 / k - 9, "BETWEEN CROSSMEMBERS (FAT-08, FAT-21).", 1.5)
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
    # ---- K: the rails' front ends for galvanising, from outside, 1:5 (I2-75, I2-79)
    _galv_detail(sh, lay.chassis, chs["results"]["holes"], 234.0, 120.0)
    dip = lay.chassis.data["galvanising_dip"]
    galv = ("DRILL OR HOLE-SAW AND DEBURR THE DRAINS BEFORE GALVANISING (report 02 WLD-05). THE GAA'S DESIGN GUIDE ASKS FOUR "
            "20 IN EACH CLOSED END OF AN RHS 150x50 (TABLE 3), AS NEAR ITS LOW AND HIGH POINTS AS CAN BE: THE FOUR DRAINS, THE CABLE HOLES AND "
            f"THE {lift_slot(lay.chassis):g} SLOT UNDER THE PLATE OPEN MORE. ONE DIP AT VALMONT COATINGS HEXHAM ({dip['dip'][0] / 1000:.1f} x "
            f"{dip['dip'][1] / 1000:.1f} x {dip['dip'][2] / 1000:.1f} m): HANG THE FRAME DRAWBAR END DOWN AT UP TO {dip['pitch_deg']:g} deg, ROLLED "
            f"{dip['roll_deg']:g} deg ACROSS, EITHER SIDE DOWN. THE RAILS VENT AT THEIR OPEN REAR ENDS. THE MEMBER'S LAP UNDER THE RAIL STANDS 2.5 "
            "OPEN, STITCH WELDED BOTH SIDES (DETAIL D, FAT-21), SO ITS FACES GALVANISE.")
    for i, t in enumerate(S.wrap_mm(galv, 80.0, 1.5)):
        sh.text(234.0, 109.0 - 2.6 * i, t, 1.5)
    # ---- fatigue table (right column)
    rows = []
    for f in chs["results"]["fatigue"]:
        col = "#000" if f["ok"] else "#c00"
        rows.append([f["id"], _clip(f["name"], 118), f"{f['fat']:g}", (f"{f['range_mpa']:.0f} / {f['cafl']:.0f}", col), (f"{f['damage']:.2f}", col),
                     "HS" if f["hot_spot"] else ""])
    S.table(sh, 230.0, 262.0, [("DETAIL", 13), ("JOINT", 103), ("FAT", 10), ("RANGE/CAFL", 24), ("MINER", 14), ("", 14)], rows,
            size=1.5, row_h=2.95, title="FATIGUE AT EACH WELDED DETAIL, LC10 (HS = HOT-SPOT CHECK)")
    S.notes(sh, 22, 64, [
        "WELDS SP TO AS/NZS 1554.1, E49XX OR W50X. VISUAL ON EVERY WELD, DYE PENETRANT OR MPI ON THE DRAWBAR TO CHASSIS JOINT, THE COUPLING MOUNT AND THE SUSPENSION BRACKETS (report 02 WLD-03). THE RAIL END PLATES' WELD ROOTS BY VIDEOSCOPE FROM INSIDE THE RAILS, RECORDED AS CT-102 NOTE 3 ASKS (FAT-20).",
        "HOT-DIP GALVANISE TO AS/NZS 4680 IN ONE DIP, HUNG AS DETAIL K SAYS, THE SPARE CARRIER POSTS OFF. DRILL BEFORE WELDING (report 02 WLD-05, CHS-11): THE RAILS' FRONT ENDS AS DETAIL K, EACH DRAWBAR MEMBER 20 IN BOTH WEBS 40 BEHIND ITS APEX END, 40 OVER ITS UNDERSIDE AND 40 UNDER ITS TOP, AND 40 BEHIND THE BODY FRONT, 40 OVER ITS UNDERSIDE, ITS SNIPE LEFT OPEN, AND AT EVERY OTHER CLOSED END 20 IN BOTH WEBS BY ITS FLOOR AND ITS TOP, 13 IN THE CROSS BRACE, ONE 10 OR 13 IN EACH WEB OF A PLAN BRACE OR HINGE GUSSET, BUT THE XT REAR SHOCK CROSSMEMBER 25 IN ITS REAR WEB AND 16 THROUGH THE RAILS' INNER WEBS AT ITS FRONT CORNERS, A 10 CHECK HOLE IN EACH RAIL'S OUTER WEB OPPOSITE (CHASSIS.md).",
        "FILLET SIZES ARE LEGS: 5 mm UNLESS STATED, 6 mm ON THE XT CROSSMEMBER ENDS, THE OUTRIGGER ROOTS, THE LUGS AND THE TONGUES.",
    ], width_chars=118, size=1.7)
    _draft_stamp(sh, 125, 75)
    _title(sh, dwg, reg, "SEE CT-101 FOR MASSES (TB-11).", 5, chs["revision"])
    S.write(sh, OUT / f"{dwg['number']}.svg")
    return time.time() - t0

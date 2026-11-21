"""The home trailer's body layout sheets (TRAILER.md revision J, the H11 set), A3, third angle:

CT-011: elevations of the four walls from outside with the 17 openings, their positions and each one's spacing margin.
CT-012: sections through the bed by day and by night, through the plinth and the bench, and through the wet room, the
        shower well and the grey tank.
CT-013: the window, door and hatch schedule: product, cut-out, clear opening, operation, blind, position and mass.

The views come from the layout's blocks and the body's openings (data/assemblies/trailer.yaml, data/body/body.yaml).
"""
from __future__ import annotations

import time

import yaml

from ..partsdb import ROOT
from . import sheet as S
from .home_common import MARK, Proj, ctx, label_in, opening_margins, short, textblock, title, wrap, write

RULES = yaml.safe_load((ROOT / "data" / "body" / "body.yaml").read_text())["rules"]
# clear openings of the Dometic S4 windows (report 19 section 7)
CLEAR = {"WN-01": "804 x 454", "WN-02": "804 x 304", "WN-03": "404 x 304", "WN-04": "404 x 304"}
OPERATION = {
    "WN": "Top-hinged, friction stays hold it open, lock against opening from outside",
    "BD-07": "Hinged on its front edge, opens outward, triple compression lock",
    "BD-15": "Hinged on its kerb edge, opens outward, triple compression lock",
    "BD-17": "Service door from outside, gasket and two compression latches",
    "VE-01": "Sleeve 162 mm, reversing fan with a heat store, stainless hood",
    "VE-03": "Sleeve 162 mm, radial extract fan, 15 to 60 m3/h",
    "VE-04": "Intake hood with a mesh stone guard, to the RESPA and the top-up fan",
    "VE-07": "Duct cowl with a backdraft flap, from the range hood",
    "LA-03": "Truma wall cowl, exhaust and combustion air, 60 cm duct set",
    "VE-06": "Rubber-flap relief valve, 30 cm2 free area, under a hood",
    "WR-05": "Hot and cold, a non-return valve on each line",
}
BLIND = {"WN-01": "Roller blackout blind and fly screen in the frame, clip-in blackout cover (WN-05)",
         "WN-02": "Roller blackout blind and fly screen in the frame, clip-in blackout cover (WN-05)",
         "WN-03": "Roller blackout blind and fly screen in the frame",
         "WN-04": "Roller blind and fly screen, frosted film on the inner pane",
         "BD-07": "Pleated blind in the door", "BD-15": "Pleated blind in the door"}


def _op_key(line):
    if line.startswith("WN-"):
        return "WN"
    if line.startswith("VE-01"):
        return "VE-01"
    return line


# ------------------------------------------------------------------ CT-011 elevations
def _wall_view(sh, V, res, wall, k, ox, oy, lay, title_txt, marks=True, dims=True, small=False):
    """One wall from outside at 1:k. (ox, oy) is the sheet point of the wall's left end at the floor underside.
    Side walls run along the trailer (u from the body front), end walls across it (u is Y). Returns the u to sheet x map."""
    L = V["body_length"] if wall in ("kerb", "road") else V["body_width"]
    zb, zt = -V["floor_t"], V["interior_h"] + V["roof_t"]
    if wall == "kerb":
        X = lambda u: ox + u / k  # noqa: E731
    elif wall == "road":
        X = lambda u: ox + (L - u) / k  # noqa: E731
    elif wall == "front":
        X = lambda u: ox + (V["half_bw"] - u) / k  # noqa: E731   seen from ahead: kerb side on the right
    else:
        X = lambda u: ox + (u + V["half_bw"]) / k  # noqa: E731   seen from behind: road side on the right
    Z = lambda z: oy + (z - zb) / k  # noqa: E731
    left, right = ox, ox + L / k
    r = V["roof_front_r"] / k
    if wall in ("kerb", "road"):
        # the outline with the 150 mm radius where the roof meets the front wall (H12)
        front_left = wall == "kerb"
        pts = []
        if front_left:
            pts = [(left, Z(zb)), (right, Z(zb)), (right, Z(zt)), (left + r, Z(zt))]
            import math
            pts += [(left + r - r * math.sin(math.radians(a)), Z(zt) - r + r * math.cos(math.radians(a))) for a in range(0, 91, 10)]
        else:
            pts = [(right, Z(zb)), (left, Z(zb)), (left, Z(zt)), (right - r, Z(zt))]
            import math
            pts += [(right - r + r * math.sin(math.radians(a)), Z(zt) - r + r * math.cos(math.radians(a))) for a in range(0, 91, 10)]
        sh.path(pts, "thick", closed=True)
        xv = X(V["front_vert_r"])
        sh.line(xv, Z(zb), xv, Z(zt) - (r if not small else 0), "thin")
    else:
        sh.rect(left, Z(zb), right, Z(zt), "thick")
        for s in (-1, 1):
            xv = X(s * (V["half_bw"] - V["front_vert_r"])) if wall == "front" else None
            if xv:
                sh.line(xv, Z(zb), xv, Z(zt), "thin")
    sh.line(left, Z(0), right, Z(0), "phantom")
    sh.line(left, Z(V["interior_h"]), right, Z(V["interior_h"]), "phantom")
    ops = [o for o in res["openings"] if o["wall"] == wall]
    for o in ops:
        x0, x1 = sorted((X(o["u0"]), X(o["u1"])))
        y0, y1 = Z(o["z0"]), Z(o["z1"])
        line = o.get("line") or ""
        if line.startswith("VE-01") or line == "VE-03":
            sh.circle((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, "medium")
        else:
            sh.rect(x0, y0, x1, y1, "medium")
        if line.startswith("WN-"):        # top-hinged: the lines meet at the hinge
            sh.line(x0, y0, (x0 + x1) / 2, y1, "hidden")
            sh.line(x1, y0, (x0 + x1) / 2, y1, "hidden")
        elif line in ("BD-07", "BD-15"):  # side-hinged: the lines meet at the hinge edge
            hinge_u = o["u0"]             # D1 on its front edge, D2 on its kerb edge: the low u in both
            xh = X(hinge_u)
            xf = x1 if abs(xh - x0) < 1e-6 else x0
            sh.line(xf, y0, xh, (y0 + y1) / 2, "hidden")
            sh.line(xf, y1, xh, (y0 + y1) / 2, "hidden")
        if marks:
            m = MARK.get(line, o["id"])
            if not label_in(sh, (x0, y0, x1, y1), m, 1.5 if not small else 1.2, 1.0, rot_ok=False):
                sh.text((x0 + x1) / 2, y1 + 0.8, m, 1.3 if not small else 1.1, "middle", bold=True)
    if dims and ops:
        us = sorted({round(v) for o in ops for v in (o["u0"], o["u1"])})
        yd = Z(zb) - 2.0
        last = -1e9
        for u in us:
            x = X(u)
            sh.line(x, Z(zb) - 0.6, x, yd, "thin")
            tx = x if abs(x - last) > 1.7 else last + 1.7
            sh.text(tx + 0.45, yd - 0.6, f"{u}", 1.2, "end", rot=-90)
            last = tx
        if wall in ("front", "rear"):
            xc = X(0)
            sh.line(xc, Z(zb) - 1, xc, Z(zt) + 1, "centre")
    sh.text(left, Z(zt) + 2.5, title_txt, 1.9 if not small else 1.5, bold=True)
    return X, Z


def ct011(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V, res, lay = C["V"], C["res"], C["day"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    _wall_view(sh, V, res, "kerb", k, 26, 214, lay, "KERB-SIDE WALL FROM OUTSIDE, FRONT LEFT. FIGURES: mm FROM THE BODY FRONT")
    _wall_view(sh, V, res, "front", k, 160, 214, lay, "FRONT WALL, KERB SIDE RIGHT. mm FROM THE CENTRELINE")
    _wall_view(sh, V, res, "road", k, 26, 146, lay, "ROAD-SIDE WALL FROM OUTSIDE, FRONT RIGHT. FIGURES: mm FROM THE BODY FRONT")
    X, Z = _wall_view(sh, V, res, "rear", k, 160, 146, lay, "REAR WALL, ROAD SIDE RIGHT. mm FROM THE CENTRELINE")
    # the split's outdoor unit and its cradle on the rear wall (phantom), and the awning on the kerb wall
    for iid in ("AC-03",):
        b = lay.find(iid).box
        fz = V["floor_z"]
        x0, x1 = sorted((X(b[1]), X(b[4])))
        sh.rect(x0, Z(b[2] - fz), x1, Z(b[5] - fz), "phantom")
        sh.text((x0 + x1) / 2, Z(b[2] - fz) + 1.0, "SPLIT OUTDOOR UNIT", 1.15, "middle")
    aw = lay.find("BD-13").box
    sh.rect(26 + (aw[0] - V["body_x0"]) / k, 214 + (aw[2] - V["floor_z"] + V["floor_t"]) / k,
            26 + (aw[3] - V["body_x0"]) / k, 214 + (aw[5] - V["floor_z"] + V["floor_t"]) / k, "phantom")
    sh.text(26 + 2.0, 214 + (aw[2] - V["floor_z"] + V["floor_t"]) / k - 2.6, "AWNING CASSETTE, PHANTOM", 1.15)
    # ---- margins, right column
    yb = title(sh, dwg, reg, "OPENINGS WITH THEIR MASSES ON CT-013 (TB-11).", "GRP AND XPS SANDWICH, OPENINGS CUT AFTER LAY-UP")
    mg = opening_margins(lay, res, RULES)
    rows = []
    worst = None
    for o in res["openings"]:
        m = mg[o["id"]]
        margin = m["gap"] - m["rule"]
        worst = margin if worst is None else min(worst, margin)
        rows.append([MARK.get(o.get("line"), o["id"]), o["id"], o["wall"].upper(), f"{o['u0']:.0f} TO {o['u1']:.0f}",
                     f"{o['z0']:.0f} TO {o['z1']:.0f}", f"{o['w']:.0f} x {o['h']:.0f}", m["what"].upper(), f"{m['gap']:.0f}",
                     f"{m['rule']:.0f}", (f"{margin:+.0f}", "#000" if margin >= -1e-6 else "#c00")])
    y = S.table(sh, 230, yb - 6, [("MARK", 10), ("ID", 12), ("WALL", 12), ("ALONG", 24), ("ABOVE FLOOR", 22), ("CUT-OUT", 19),
                                   ("TIGHTEST TO", 33), ("GAP", 14), ("RULE", 14), ("MARGIN", 20)], rows, size=1.38, row_h=3.15,
                title="EACH OPENING'S TIGHTEST GAP UNDER THE SPACING RULES (BDY-18)")
    oc = res["openings_check"]
    S.notes(sh, 230, y - 6, [
        f"RULES (report 12 section 5, data/body/body.yaml): {RULES['between_mm']} mm OF FULL WALL BETWEEN NEIGHBOURING OPENINGS, OR "
        f"{RULES['between_mm']} mm APART IN HEIGHT WHERE THEY SHARE NO HEIGHT BAND. {RULES['edge_mm']} mm TO A PANEL EDGE AND TO THE ROOF. "
        f"NOTHING WITHIN {RULES['rear_corner_mm']} mm OF THE REAR CORNERS.",
        f"BDY-18: {oc['count']} OPENINGS, {'EVERY ONE KEEPS THE RULES' if oc['ok'] else 'SOME BREAK THE RULES'}, THE TIGHTEST BY "
        f"{oc['margin_mm']:.0f} mm. A MARGIN OF 0 MEANS THE OPENING SITS EXACTLY ON ITS LIMIT.",
        "ALONG: SIDE WALLS FROM THE BODY FRONT, END WALLS FROM THE CENTRELINE, POSITIVE TO THE ROAD SIDE. ABOVE FLOOR: FROM THE FLOOR "
        f"SURFACE AT Z {V['floor_z']:.0f}.",
        "GLANDS OF 60 mm OR LESS (FILL, PV, SPLIT LINES, THE OUTLET BOXES, THE BATTERY VENTS) ARE NOT OPENINGS. THEY ARE ON CT-602 AND CT-612.",
    ], size=1.38, width_chars=150)
    S.notes(sh, 22, 116, [
        "DATUM DIM-01. EVERY WALL IS DRAWN AS SEEN FROM OUTSIDE. HEIGHTS ABOVE THE FLOOR SURFACE, THE FLOOR AND ROOF THICKNESSES SHOWN.",
        "PHANTOM LINES ACROSS EACH WALL: THE FLOOR SURFACE AND THE CEILING. THE THIN LINES NEAR THE FRONT ARE THE EDGES OF THE "
        f"{V['front_vert_r']:.0f} mm RADIUS CORNER PIECES, AND THE ROOF MEETS THE FRONT WALL ON A {V['roof_front_r']:.0f} mm RADIUS (H12).",
        "DASHED LINES IN A WINDOW OR DOOR MEET AT ITS HINGE: THE WINDOWS ARE TOP-HINGED, D1 HINGES ON ITS FRONT EDGE AND D2 ON ITS KERB EDGE.",
        "THE FIGURES UNDER EACH WALL ARE THE OPENINGS' EDGES ALONG IT. THE SCHEDULE OF PRODUCTS IS CT-013, THE CUT-OUT SIZES ARE THE MAKERS'.",
        "CUT-OUT CORNERS RADIUSED, 68 mm FOR SERVICE DOORS AND 90 mm AT THE TOP OF THE DOOR FRAMES (report 12). EVERY CUT EDGE IS SEALED.",
        "WHERE AN OPENING CROSSES A CHASSIS STATION THE OUTRIGGER-TIP MOUNT MOVES INBOARD OF ITS FRAME AND THE FLOOR JOINER RUNS UNBROKEN.",
    ], size=1.5, width_chars=185)
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-012 sections
SECTIONS = [("A", 2300.0, "day", "THROUGH THE DESK AND THE BED, BED UP"), ("B", 2300.0, "night", "THE SAME, BED DOWN"),
            ("C", 4500.0, "day", "THROUGH THE PLINTH, THE WASHER AND THE BENCH"), ("D", 5600.0, "day", "THROUGH THE WET ROOM, WELL AND GREY TANK")]


def _section(sh, C, lay, x, k, ox, oy, letter, what):
    """Section at X looking forward (road side on the right), drawn from the blocks cut by the plane."""
    V = lay.V
    pr = Proj(sh, "rear", k, ox, oy, ref=(0, 0, 0))
    fz = V["floor_z"]
    cut = [b for b in lay.blocks if b.box is not None and b.box[0] <= x <= b.box[3]]
    body = {"BD-01", "BD-02", "BD-03", "BD-04", "WR-03"}
    labels = []
    for b in cut:
        bb = b.box
        sys_ = b.system
        if b.id in ("UF-08W", "UF-02") or b.load in ("water", "grey"):
            continue
        if b.keep_clear:
            pr.box(bb, "phantom")
            continue
        if b.id in body:
            pr.fill(bb, "shade")
        elif b.id.startswith("WN-"):
            r = pr.fill(bb, "white")
            sh.rect(*r, "thin")
            for f in (0.35, 0.65):
                xx = r[0] + f * (r[2] - r[0])
                sh.line(xx, r[1], xx, r[3], "thin")
        elif sys_ == "chassis":
            pr.fill(bb, "fill")
        elif b.id.startswith("RG-02"):
            pr.fill(bb, "light")
            pr.box(bb, "medium")
        elif sys_ in ("roof",):
            pr.box(bb, "medium")
        else:
            r = pr.box(bb, "medium")
            labels.append((b, r))
    for b, r in labels:
        if b.id not in ("EL-01", "LA-14F", "RG-01"):
            label_in(sh, r, short(b), 1.25, 1.0)
    # ground and the centreline
    g0, g1 = pr.p(0, -1300, 0), pr.p(0, 1300, 0)
    sh.line(g0[0], g0[1], g1[0], g1[1], "thick")
    c0, c1 = pr.p(0, 0, -50), pr.p(0, 0, V["roof_top_z"] + 60)
    sh.line(c0[0], c0[1], c1[0], c1[1], "centre")
    sh.text(pr.p(0, 0, 0)[0], pr.p(0, 0, V["roof_top_z"])[1] + 5.0, f"SECTION {letter}-{letter} AT X {x:,.0f}, LOOKING FORWARD", 1.9, "middle", bold=True)
    sh.text(pr.p(0, 0, 0)[0], pr.p(0, 0, V["roof_top_z"])[1] + 2.4, what, 1.4, "middle")
    sh.text(pr.p(0, -1300, 0)[0], pr.p(0, 0, 0)[1] - 3.0, "KERB", 1.3)
    sh.text(pr.p(0, 1300, 0)[0], pr.p(0, 0, 0)[1] - 3.0, "ROAD", 1.3, "end")
    return pr, cut


def _levels(sh, pr, levels, y_side=1345.0):
    """Height labels beside a section, outside its road side: (z, text), spaced so they do not overlap."""
    xs = pr.p(0, y_side, 0)[0]
    last = None
    for z, t in sorted(levels, key=lambda v: v[0]):
        y = pr.p(0, 0, z)[1]
        yy = y if last is None or y - last >= 2.0 else last + 2.0
        sh.line(xs - 0.6, y, xs + 1.6, yy, "thin")
        sh.text(xs + 2.0, yy - 0.5, t, 1.15)
        last = yy


def ct012(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V = C["V"]
    sh = S.Sheet()
    S.frame(sh)
    k = dwg["scale"]
    fz = V["floor_z"]
    pos = [(58.0, 192.0), (150.0, 192.0), (58.0, 94.0), (150.0, 94.0)]
    for (letter, x, state, what), (ox, oy) in zip(SECTIONS, pos):
        lay = C["day"] if state == "day" else C["night"]
        pr, cut = _section(sh, C, lay, x, k, ox, oy, letter, what)
        ids = {b.iid: b for b in cut}
        lv = [(0, "GROUND 0"), (fz, f"FLOOR Z {fz:.0f}"), (V["ceiling_z"], f"CEILING Z {V['ceiling_z']:.0f}"),
              (V["roof_top_z"], f"ROOF {V['roof_top_z']:.0f}"), (V["rail_underside_z"], f"RAIL UNDERSIDE {V['rail_underside_z']:.0f}")]
        if letter in ("A", "B"):
            bp, mt = lay.find("LB-03").box, lay.find("LB-01").box
            d = lay.find("LA-09").box
            lv += [(bp[2], f"BED UNDERSIDE +{bp[2] - fz:.0f}"), (mt[5], f"MATTRESS TOP +{mt[5] - fz:.0f}"), (d[5], f"DESK TOP +{d[5] - fz:.0f}")]
            p = pr.p(0, d[4] - 150, d[5])
            sh.text(p[0], p[1] - 2.6, "DESK", 1.25, "middle")
        if letter == "C":
            for iid, t in (("LA-11B", "BENCH TOP"), ("EL-02", "PLINTH TOP"), ("LA-02", "WASHER TOP"), ("LA-11L", "LOCKERS")):
                if iid in ids:
                    b = ids[iid].box
                    lv.append((b[5] if iid != "LA-11L" else b[2], f"{t} +{(b[5] if iid != 'LA-11L' else b[2]) - fz:.0f}"))
        if letter == "D":
            g = lay.find("UF-08").box
            w = lay.find("WR-10").box
            lv += [(g[5], f"GREY TANK TOP {g[5]:.0f}"), (w[2], f"WELL BOTTOM {w[2]:.0f}")]
        _levels(sh, pr, lv)
    # ---- right column: key plan with the cutting planes, and notes
    yb = title(sh, dwg, reg, "MASSES ON CT-002 (TB-11).", "SEE CT-201 FOR THE BODY, CT-101 FOR THE CHASSIS")
    kk = 100.0
    lay = C["day"]
    pr = Proj(sh, "plan", kk, 250.0, yb - 46.0, ref=(V["body_x0"], -V["half_bw"], 0))
    pr.box((V["body_x0"], -V["half_bw"], 0, V["body_x1"], V["half_bw"], 0), "thick")
    for iid in ("WR-03", "LA-11T", "LA-11B", "EL-02", "LA-09"):
        pr.box(lay.find(iid).box, "thin")
    sh.text(232, yb - 7, "KEY PLAN 1:100, FRONT LEFT, ROAD SIDE UP: THE CUTTING PLANES", 1.8, bold=True)
    done = set()
    for letter, x, state, what in SECTIONS:
        if x in done:
            continue
        done.add(x)
        p0, p1 = pr.p(x, -V["half_bw"] - 250), pr.p(x, V["half_bw"] + 250)
        S.cut_marker(sh, p0, p1, (-1, 0), letter if x != 2300 else "A, B")
    S.notes(sh, 230, yb - 62, [
        "DATUM DIM-01. EACH SECTION LOOKS FORWARD, SO THE ROAD SIDE IS ON THE RIGHT. HEIGHTS BESIDE EACH SECTION ARE Z FROM THE GROUND, "
        "OR + mm ABOVE THE FLOOR SURFACE.",
        "CUT PANELS ARE SHADED: THE 30 mm FLOOR, THE 35 mm WALLS, THE 40 mm ROOF AND THE PARTITION. CUT STEEL IS BLACK. THE TYRES ARE "
        "SHADED LIGHT. A WINDOW CUT BY THE PLANE SHOWS ITS GLASS. PHANTOM: A SPACE KEPT CLEAR.",
        "A AND B: BY DAY THE BED LIES UNDER THE CEILING WITH THE BEDDING ON IT. AT NIGHT IT STANDS 75 mm OVER THE DESK TOP WITH 956 mm "
        "CLEAR ABOVE THE MATTRESS (BED-01, H1). THE LIFT RAILS ARE ON THE SIDE WALLS AHEAD OF AND BEHIND THIS PLANE (CT-010).",
        "C: THE BATTERY PLINTH ON THE KERB SIDE, 125 mm OFF THE WALL, WITH THE WASHER ON IT AND THE LOCKERS ABOVE. THE BENCH, THE "
        "FREEZER UNDER THE HOB AND THE RANGE HOOD ON THE ROAD SIDE. THE FRESH TANK SITS BETWEEN THE RAILS ON ITS GUARD.",
        "D: THE TOILET ON THE KERB SIDE, THE SHOWER ZONE ON THE ROAD SIDE OVER THE WELL. THE WELL'S SWITCHING UNIT DRAINS STRAIGHT DOWN "
        "INTO THE GREY TANK BETWEEN THE RAILS (H4A). W6 IS OBSCURED.",
        "THE SECTIONS ARE DRAWN FROM THE LAYOUT'S BLOCKS (ENVELOPES). THE CABINETRY'S OWN PANELS ARE NOT DESIGNED YET.",
    ], size=1.4, width_chars=150)
    write(sh, dwg)
    return time.time() - t0


# ------------------------------------------------------------------ CT-013 schedule
def ct013(prj, model, bom, checks, reg, dwg):
    t0 = time.time()
    C = ctx(prj)
    V, res, lay = C["V"], C["res"], C["day"]
    sh = S.Sheet()
    S.frame(sh)
    yb = title(sh, dwg, reg, "THE MASS COLUMN IS THE WHOLE LINE'S, A FAN OR UNIT WITH ITS HOOD (TB-11).",
               "MAKERS' PRODUCTS, CUT-OUTS TO THE MAKERS' SHEETS")
    rows = []
    wall_order = {"kerb": 0, "road": 1, "front": 2, "rear": 3}
    for o in sorted(res["openings"], key=lambda o: (wall_order[o["wall"]], o["u0"])):
        line = o.get("line") or ""
        b = next((bb for bb in lay.blocks if bb.id == line), None)
        name = (b.name if b else o["name"])
        mass = sum(bb.mass_kg for bb in lay.blocks if bb.id == line) / max(1, sum(1 for bb in lay.blocks if bb.id == line)) if b else 0.0
        rows.append([MARK.get(line, o["id"]), o["id"], o["wall"].upper(), name[:175], f"{o['w']:.0f} x {o['h']:.0f}",
                     CLEAR.get(line, "-"), OPERATION.get(_op_key(line), "-"), BLIND.get(line, "-"),
                     f"{o['u0']:.0f} TO {o['u1']:.0f}", f"{o['z0']:.0f} TO {o['z1']:.0f}", line, f"{mass:.1f}"])
    y = S.table(sh, 22, 262, [("MARK", 9), ("ID", 11), ("WALL", 11), ("PRODUCT AND WHERE (THE MASS SCHEDULE LINE)", 128), ("CUT-OUT", 18),
                              ("CLEAR", 18), ("OPERATION", 70), ("BLIND AND SCREEN", 62), ("ALONG", 19), ("ABOVE FLOOR", 18), ("LINE", 13),
                              ("kg", 11)], rows, size=1.2, row_h=3.6,
                title="WINDOWS, DOORS, HATCHES, VENTS AND COWLS: EVERY OPENING IN THE BODY (data/body/body.yaml)")
    # ---- key elevations at 1:100 with the marks
    k = dwg["scale"]
    yk = y - 32
    _wall_view(sh, V, res, "kerb", k, 26, yk, lay, "KERB SIDE FROM OUTSIDE", dims=False, small=True)
    _wall_view(sh, V, res, "road", k, 80, yk, lay, "ROAD SIDE FROM OUTSIDE", dims=False, small=True)
    _wall_view(sh, V, res, "front", k, 134, yk, lay, "FRONT", dims=False, small=True)
    _wall_view(sh, V, res, "rear", k, 168, yk, lay, "REAR", dims=False, small=True)
    S.notes(sh, 22, yk - 6, [
        "MARKS: W WINDOW, D DOOR, S SERVICE DOOR, V VENT, FAN OR COWL, R RINSE BOX (layout study section 5, decision H15: FOUR "
        "WINDOWS, W3 AND W5 DROPPED).",
        "CUT-OUT: THE HOLE IN THE PANEL, W x H. CLEAR: THE OPENING WHEN OPEN (report 19 section 7). W1 IS THE SECOND WAY OUT: "
        "804 x 454 mm CLEAR, 0.365 m2, AGAINST THE PROJECT'S 0.33 m2 WITH NO SIDE UNDER 450 mm.",
        "ALONG: SIDE WALLS FROM THE BODY FRONT, END WALLS FROM THE CENTRELINE, POSITIVE TO THE ROAD SIDE. ABOVE FLOOR: FROM THE FLOOR "
        f"SURFACE AT Z {V['floor_z']:.0f}. POSITIONS AND MARGINS ON CT-011.",
        "WINDOWS STAY LATCHED SHUT WHILE TOWING. EVERY DOOR AND HATCH HAS A COMPRESSION SEAL PULLED UP BY ITS LATCHES (report 19 "
        "section 4, THE DUST PLAN).",
        "BOTH DOORS OPEN OUTWARD (VSB1 13.2.1). EACH HAS A FOLD-OUT STEP THAT STOWS UPRIGHT INSIDE ITS OPENING (BD-16).",
    ], size=1.45, width_chars=125)
    write(sh, dwg)
    return time.time() - t0

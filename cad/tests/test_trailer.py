"""Whole-trailer checks from data/checks.yaml (trailer_checks), measured on the block layout (cad/trailer.py).

A `fail` check that misses its limit fails the test. A `report` check is marked xfail when it misses. The trailer is
the home trailer for the Ford Ranger Super Duty (revision J): it reads the ute's model from build/ute/ute.json, so the ute builds first.
"""
import pytest

from cad.trailer import Trailer

TRAILER = Trailer()
EV = TRAILER.evaluate()
RESULTS = EV["checks"]


@pytest.mark.parametrize("row", RESULTS, ids=[r["id"] for r in RESULTS])
def test_trailer_check(row):
    msg = f"{row['id']} {row['title']}: {row['detail']}"
    if row["severity"] == "report":
        if not row["ok"]:
            pytest.xfail("reported, not a build failure: " + msg)
        return
    assert row["ok"], msg


def test_the_walls_strength_wind_covers_the_overturning_speed():
    """Decision H23: the walls are checked for strength at BDY-19's 40 m/s, or at STB-04's overturning speed if that is
    higher. If a change lets the parked trailer stand in a stronger wind than the walls are checked for, this fails."""
    o = next(r for r in RESULTS if r["id"] == "STB-04")["overturn"]
    for q in o["cases"]:
        v = max(q["v"], q["v_box"])
        assert v <= o["v_u"] + 1e-9, f"{q['case']} overturns at {v:.1f} m/s, above the {o['v_u']:g} m/s the walls are checked at"


def test_the_wall_section_model_matches_a_plain_wall():
    """BDY-22's two-dimensional model, with no member, gives the one-dimensional wall's inside surface and heat flow."""
    from cad.body import _wall_section, load_data
    d = load_data()
    th, wl = d["thermal"], d["panels"]["wall"]
    t_o, t_i = wl["skins"]
    c = wl["core"]["c"]
    r = th["rsi"] + (t_o + t_i) / 1000 / th["k"]["grp"] + c / 1000 / th["k"]["xps"] + th["rse"]
    dT = th["t_in"] - th["t_out"]
    res = _wall_section(th, t_o, c, t_i, None)
    assert abs(res["tsi_min"] - (th["t_in"] - dT * th["rsi"] / r)) < 0.05
    assert abs(res["q_w_m"] - th["strip_mm"] / 1000 * dT / r) < 0.01 * th["strip_mm"] / 1000 * dT / r


def test_every_aboard_line_has_a_source():
    for case in TRAILER.cases:
        for b, m in EV["layout"].case_lines(case):
            assert b.source and b.maturity in ("spec", "calculated", "estimate", "weighed"), f"{b.iid} has no mass source"


def test_no_petrol_inside_the_body():
    """Decision log 12:45: the generator and the jerry cans ride in the drawbar box, outside the body."""
    lay = EV["layout"]
    V = lay.V
    for iid in ("GS-01", "GS-04"):
        b = lay.find(iid)
        assert b.box[3] < V["body_x0"], f"{iid} is inside the body"


def test_the_coupling_matches_the_ute():
    """The trailer's coupling point and the ute's ball are the same measurement (measurements.yaml UTE-01)."""
    from cad.ute import Ute
    assert EV["layout"].V["coupling_z"] == Ute().V["coupling_z"]


def test_the_ute_cases_carry_the_trailers_heaviest_towball():
    """The ute's towing cases carry at least the trailer's heaviest towball with growth, so the ute's rear axle, GVM and
    GCM checks never assume less than the trailer puts on the ball (decision H17). It reads the built ute model, which
    the trailer's checks use, and the ute as the code builds it now."""
    import json
    from cad.partsdb import ROOT
    from cad.ute import Ute
    heavy = max(EV["cases"], key=lambda c: c["growth"]["towball_kg"])
    ball = heavy["growth"]["towball_kg"]
    built = json.loads((ROOT / "build" / "ute" / "ute.json").read_text())["cases"]
    now = Ute().cases()
    for src, cases in (("build/ute/ute.json", built), ("cad/ute.py", now)):
        towing = [c for c in cases if c["growth"]["towball_kg"] > 0]
        assert towing, f"{src} has no towing case"
        for c in towing:
            for bs in ("nominal", "growth"):
                assert c[bs]["towball_kg"] >= ball - 1e-6, (
                    f"{src} {c['id']} ({bs}) carries {c[bs]['towball_kg']:.1f} kg on the ball, less than the trailer's "
                    f"{ball:.1f} kg ({heavy['id']} with growth)")


def test_the_tanks_hold_the_water_the_design_carries():
    """I2-40: each tank's net capacity worked out from its inside by the grey tank's rule (Layout.tank_nets: the inside
    of its 6 mm walls less a 10 mm air gap under its top and its baffles). The fresh tanks hold `water_full_l`, and it
    is their net in H21's 5 L steps, so a change to a tank or the axle that the water does not follow fails here. The
    travel water never passes it, and the grey tank holds `grey_full_l`."""
    lay = EV["layout"]
    V, nets = lay.V, lay.tank_nets()
    fresh = lay.fresh_net_l()
    assert {"UF-01", "UF-01R", "UF-08"} <= set(nets)
    assert V["water_full_l"] <= fresh + 1e-9, f"water_full_l {V['water_full_l']:g} L, the fresh tanks hold {fresh:.1f} L net"
    assert fresh - V["water_full_l"] < 5.0, f"the fresh tanks hold {fresh:.1f} L net, water_full_l is {V['water_full_l']:g} L"
    assert V["water_travel_l"] <= V["water_full_l"] + 1e-9
    assert V["grey_full_l"] <= nets["UF-08"]["net_l"] + 1e-9, f"grey_full_l {V['grey_full_l']:g} L, the grey tank holds {nets['UF-08']['net_l']:.1f} L net"
    for k, n in nets.items():
        assert n["net_l"] < n["inside_l"], f"{k}: its net {n['net_l']:.1f} L is not less than its inside {n['inside_l']:.1f} L"


def test_the_fresh_tanks_keep_their_clearance_to_every_fitting_they_are_notched_round():
    """FIT-03 reads every place of every chassis fitting (Layout.shapes), each hinge gusset as the prism of its cut
    outline, so the gussets that reach into a fresh tank's corners, behind each hinge crossmember, stand in the tank's
    notches (Layout.tank_notches) with the tank's own clearance round them. The XT
    kit's airbags, their top brackets, the shocks over the arm's travel and their brackets stand in the tanks' pockets
    the same way (Layout._part_notches, I2-97). The steps up into the tanks' bottom edges over the arms (Layout._arm_pockets)
    keep FIT-05's clearance from the arms over their travel, which FIT-05 reads on the tanks as stepped."""
    from cad.trailer import shape_gap
    lay = EV["layout"]
    by_id = {b.id: lay.shapes(b) for b in lay.blocks if "fitting" in b.extra}
    by_id.update({b.iid: [(bx, None) for bx in b.extra["boxes"]] for b in lay.xt_blocks()})
    for t in lay.tanks():
        notches = t.extra["notches"]
        assert notches, f"{t.iid} has no notches"
        assert any(nt.get("kind") == "box" for nt in notches), f"{t.iid} has no pockets round the XT kit's parts"
        steps = [nt for nt in notches if nt["fitting"] == "XT arm"]
        assert all(nt.get("kind") == "box" and nt["z0"] == t.box[2] for nt in steps), f"{t.iid}: an arm's step not up from its bottom"
        for fid in {nt["fitting"] for nt in notches} - {"XT arm"}:
            for s in by_id[fid]:
                if shape_gap((t.box, None), s) >= 0:
                    continue
                g = min(shape_gap(piece, s) for piece in lay.tank_pieces(t))
                assert g >= notches[0]["clear"] - 1e-6, f"{t.iid}: {fid} at {[round(v) for v in s[0]]} stands {g:.1f} mm from it"


def test_the_rear_bay_clears_the_rear_airbags_their_brackets_and_the_rear_shocks():
    """FX20-FIT item 4 (fx22-rear): the shear panel's sheet, its angles and the rest of the rear bay's fittings clear the
    rear airbags over their travel, their top brackets and the rear shocks over the arms' travel, by FIT-08's rule, and
    the sheet stands 10 mm clear of the airbags and shocks."""
    lay = EV["layout"]
    f = lay.kit_fit()
    rear = [p for p in f["pairs"] if p["part"].startswith("CH-P17") or "rear piece" in p["part"]]
    assert not rear, rear
    pn = next(b for b in lay.blocks if b.id == "UF-03").extra["panel"]
    zt, t = pn["z_top"], pn["t"]
    for p in lay.xt_parts():
        if p["id"].startswith(("XT-BAG-R", "XT-SHOCK-R")):
            for bx in p["boxes"]:
                for x0, y0, x1, y1 in pn["sheet"]["parts"] + pn["sheet"]["tongues"]:
                    d = max(bx[0] - x1, x0 - bx[3], bx[1] - y1, y0 - bx[4], bx[2] - zt, zt - t - bx[5])
                    assert d >= 10.0 - 1e-6, (p["id"], bx, (x0, y0, x1, y1))


def test_fit08_reads_the_front_guard_less_its_openings():
    """FIT-08 reads UF-03's front piece as the 3D model cuts it (fx23-mrg): the openings round the front airbags and
    shocks come from the one list the line carries for its model (Layout.guard_openings), the convex pieces FIT-08
    reads stand outside every opening, they and the openings fill the piece's plan, and every box of the kit's front
    airbags and shocks that crosses the sheet's height stands at least 10 mm clear of them in plan."""
    from cad.trailer import shape_gap
    lay = EV["layout"]
    uf = next(b for b in lay.blocks if b.id == "UF-03")
    ops = uf.extra["openings"]
    assert ops and ops == lay.guard_openings(uf)
    front = [s for n, s in lay.guard_pieces() if n == "UF-03's front piece"]
    cut = [s for s in front if s[1] is not None]
    assert cut, "FIT-08 reads the front piece whole"
    z0, z1 = cut[0][0][2], cut[0][0][5]
    for s in cut:
        for o in ops:
            assert shape_gap(s, ((o[0], o[1], z0, o[2], o[3], z1), None)) >= -1e-6, (s[0], o)

    def area(pc):
        return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pc, pc[1:] + pc[:1]))) / 2

    x0, y0 = min(s[0][0] for s in cut), min(s[0][1] for s in cut)
    x1, y1 = max(s[0][3] for s in cut), max(s[0][4] for s in cut)
    inside = [(max(o[0], x0), max(o[1], y0), min(o[2], x1), min(o[3], y1)) for o in ops]
    xs = sorted({v for r in inside for v in (r[0], r[2])} | {x0, x1})
    ys = sorted({v for r in inside for v in (r[1], r[3])} | {y0, y1})
    held = sum((xb - xa) * (yb - ya) for xa, xb in zip(xs, xs[1:]) for ya, yb in zip(ys, ys[1:])
               if any(r[0] <= xa and r[2] >= xb and r[1] <= ya and r[3] >= yb for r in inside))
    assert sum(area(s[1]) for s in cut) + held == pytest.approx((x1 - x0) * (y1 - y0), rel=1e-6)
    for p in lay.xt_parts():
        if p["id"].startswith(("XT-BAG-", "XT-SHOCK-")):
            for bx in p["boxes"]:
                if bx[2] < z1 and bx[5] > z0 and bx[0] < x1 and bx[3] > x0:
                    g = min(shape_gap((bx, None), s) for s in cut)
                    assert g >= 10.0 - 1e-6, (p["id"], bx, g)
    assert not [q for q in lay.kit_fit()["pairs"] if q["part"] == "UF-03's front piece"]


def test_the_rear_tank_guard_is_the_shear_panels_sheet_as_the_chassis_data_gives_it():
    """UF-03's rear piece is the shear panel PNL-1's sheet (I2-98): its part line takes its mass and its item from the
    chassis data (Chassis.panel_mass), its price line and its note name the same thickness and grade, and the 3D model
    draws the sheet at that thickness with no stiffener."""
    lay = EV["layout"]
    uf = next(b for b in lay.blocks if b.id == "UF-03")
    m = lay.chassis.panel_mass("PNL-1")
    part = next(p for p in uf.extra["parts"] if "shear panel" in p["item"])
    assert part["kg"] == pytest.approx(m["kg"]) and part["item"].startswith(f"{m['t']:g} mm {m['material']}")
    item = next(it for it in TRAILER.td["items"] if it["id"] == "UF-03")
    grade = m["material"].split(" hot-rolled")[0].split()[-1]
    price = next(p for p in item["price"] if "shear panel" in p["item"])
    assert f"{m['t']:g} mm {grade}" in price["item"] and f"{m['t']:g} mm" in item["note"] and grade in item["note"]
    assert uf.extra["panel"]["t"] == m["t"] and set(uf.extra["panel"]) == {"sheet", "t", "z_top"}

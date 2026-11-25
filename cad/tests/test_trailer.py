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
    outline, so the gussets that reach into a fresh tank's corners, and the jacking pads under the XT centre
    crossmember, stand in the tank's notches (Layout.tank_notches) with the tank's own clearance round them."""
    from cad.trailer import shape_gap
    lay = EV["layout"]
    by_id = {b.id: b for b in lay.blocks if "fitting" in b.extra}
    for t in lay.tanks():
        notches = t.extra["notches"]
        assert notches, f"{t.iid} has no notches"
        for fid in {nt["fitting"] for nt in notches}:
            for s in lay.shapes(by_id[fid]):
                if shape_gap((t.box, None), s) >= 0:
                    continue
                g = min(shape_gap(piece, s) for piece in lay.tank_pieces(t))
                assert g >= notches[0]["clear"] - 1e-6, f"{t.iid}: {fid} at {[round(v) for v in s[0]]} stands {g:.1f} mm from it"

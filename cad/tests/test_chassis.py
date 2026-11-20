"""The chassis frame analysis (cad/chassis_fea.py): the load mapping balances, and the composite rail matches hand
arithmetic."""
import pytest

from cad.tests.test_trailer import EV, TRAILER

RES = TRAILER.chassis_results(EV["layout"])
CH = TRAILER._chassis[1]


def test_loads_and_reactions_balance():
    """The frame is held only by six kinematic supports, so their reactions must come out at zero in every case."""
    assert RES["residual_n"] < 1.0


def test_composite_rail_section():
    rail, raiser = CH.role_sec["rail"], CH.role_sec["raiser"]
    a1, a2 = rail.A, raiser.A
    d = rail.d / 2 + raiser.d / 2
    I = rail.I_strong + raiser.I_strong + a1 * a2 / (a1 + a2) * d ** 2
    assert CH.comp.I_strong == pytest.approx(I, rel=1e-9)
    assert CH.comp.z_centroid == pytest.approx(CH.V["rail_underside_z"] + rail.d / 2 + a2 / (a1 + a2) * d, rel=1e-9)


def test_every_load_case_is_analysed():
    for lc in ("LC1", "LC2", "LC3", "LC4", "LC5a", "LC5b", "LC6", "LC6b", "LC8a", "LC8b"):
        assert lc in RES["governing"], lc


@pytest.mark.xfail(reason="phase 1: the layout still carries the block chassis, the frame the designed one", strict=False)
def test_ball_load_matches_the_layout():
    """The frame statics give the same towball as the trailer layout for the fully loaded case, before ATM scaling."""
    tc2 = next(c for c in EV["cases"] if c["id"] == "TC2")["nominal"]["towball_kg"]
    b = RES["balls"]["TC2"]
    assert b["ball_kg"] / b["scale"] == pytest.approx(tc2, abs=3.0)

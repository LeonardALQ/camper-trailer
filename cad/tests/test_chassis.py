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


def test_ball_load_matches_the_layout():
    """The frame statics give the same towball as the trailer layout for the fully loaded case, before ATM scaling."""
    tc2 = next(c for c in EV["cases"] if c["id"] == "TC2")["nominal"]["towball_kg"]
    b = RES["balls"]["TC2"]
    assert b["ball_kg"] / b["scale"] == pytest.approx(tc2, abs=3.0)


STEADY_GAP = 20.0   # mm (est.): a folded steady's size is estimated from its carton, and it shakes on its bracket in travel


def _gap(a, b) -> float:
    """The clear distance between two boxes, negative where they overlap (the smallest overlap)."""
    d = [max(b[k] - a[k + 3], a[k] - b[k + 3]) for k in range(3)]
    return max(d) if max(d) <= 0 else sum(max(0.0, v) ** 2 for v in d) ** 0.5


def test_folded_steadies_and_their_swing_clear_every_rigid_part():
    """Each corner steady folded for travel keeps STEADY_GAP from every other rigid part under the trailer, the other
    steadies included, and nothing stands in the box its leg sweeps from 0 to 90 degrees. The rail it is welded under is
    the only part it touches."""
    lay = EV["layout"]
    poses = CH.steady_poses()
    others = [(b, bx) for b, bx in lay.sprung_boxes() if b.id != "CH-B01" and not b.id.startswith("RL-")]
    for k, p in enumerate(poses):
        near = [(b.iid, _gap(p["travel"], bx)) for b, bx in others]
        near += [(f"CH-B01 #{j + 1}", _gap(p["travel"], q["travel"])) for j, q in enumerate(poses) if j != k]
        name, gap = min(near, key=lambda t: t[1])
        assert gap >= STEADY_GAP, f"the {p['pair']} steady at Y {p['y']:+.0f}, folded {p['fold']}, is {gap:.0f} mm from {name}"
        hit = [b.iid for b, bx in others if _gap(p["sweep"], bx) < 0]
        assert not hit, f"the {p['pair']} steady at Y {p['y']:+.0f} sweeps through {hit}"


def test_steadies_reach_the_ground_at_90_degrees():
    """At 90 degrees, wound in, each steady's foot clears the ground at design ride height, so it swings down, and at
    full extension its bracket height passes the rail's underside, so it reaches the ground with stroke to spare."""
    sd, top = CH.data["steadies"], CH.V["rail_underside_z"]
    assert sd["retracted"] < top < sd["extended"]

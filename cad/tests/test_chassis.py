"""The chassis frame analysis (cad/chassis_fea.py): the load mapping balances, and the composite rail matches hand
arithmetic."""
import math

import pytest

from cad.chassis_fea import end_plate
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


def test_chain_lug_takes_its_connecting_link():
    """Each chain hangs from its lug on a pewag CW 8 connecting link, with no shackle at the trailer (I2-46, WA's CI-119C):
    the link's bow passes the lug's hole, and the link's eye takes the lug's plate across and the plate under the hole
    along, so the link closes round the lug."""
    c = CH.data["local_checks"]["chain_lug"]
    t = next(f for f in CH.data["fittings"] if f["id"] == c["fitting"])["t"]
    across, along = c["eye"]
    assert c["pin"] < c["hole"]
    assert t < across and c["edge"] - c["hole"] / 2 < along


def test_root_gusset_meets_iiw_522():
    """The root gusset holds IIW 522's FAT 90 (I2-51): its radius over 150 mm, its end at the toe no taller than twice its
    thickness and 25 mm, the fillets wrapped round that end and the toe ground."""
    g = next(f for f in CH.data["fittings"] if f["id"] == "CH-P03")
    assert g["r"] > 150 and g["end_h"] <= min(2 * g["t"], 25)
    assert g["wrapped"] and g["toe_ground"]
    assert next(d for d in CH.data["fatigue_details"] if d["id"] == "FAT-07")["iiw"] == "522"


def test_drawbar_root_is_read_at_the_gussets_toe():
    """FAT-07 takes the drawbar member's own stress at the root gusset's end (IIW 522, I2-47, I2-51): at the gusset's
    toe, ahead of the body front, on a node of the frame model, with the gusset reaching back to the body front."""
    V = CH.V
    toe = V["root_gusset_toe_x"]
    fit = {f["id"]: f for f in CH.data["fittings"]}
    g, ep = fit["CH-P03"], fit["CH-P15"]
    x0 = CH.ev(g["at"])[0] - g["l"] / 2
    assert x0 == pytest.approx(toe) and toe + g["l"] == pytest.approx(V["body_x0"] - ep["t"])
    f = next(r for r in RES["fatigue"] if r["id"] == "FAT-07")
    assert f["where"].endswith(f"at X {toe:.0f}")


def test_root_gusset_area_follows_its_profile():
    """CH-P03's mass is its profile's area: the radius from its end up to its heel's height, then flat to the heel."""
    g = next(f for f in CH.data["fittings"] if f["id"] == "CH-P03")
    r, c, h, length = g["r"], g["end_h"], g["w"], g["l"]
    u1, u2 = math.sqrt(r ** 2 - (r - c) ** 2), math.sqrt(r ** 2 - (r - h) ** 2)

    def under(u):
        return r * u - (u / 2 * math.sqrt(r ** 2 - u ** 2) + r ** 2 / 2 * math.asin(u / r))
    area = under(u2) - under(u1) + (length - (u2 - u1)) * h
    assert g["area_factor"] == pytest.approx(area / (length * h), abs=0.001)


def test_body_front_is_read_under_the_gussets_heel():
    """The body front's four rows (I2-51, I2-57) are read at the A-frame member's end there, and the heel's fillets are
    the ones the data gives CH-P03, on the rail's end plate CH-P15 that closes the rail's front end. The plate is flush
    with the rail's underside and stands over the raiser's bottom wall, so its top weld joins both walls."""
    rows = {r["id"]: r for r in RES["fatigue"]}
    assert rows["FAT-17"]["where"].endswith(f"at X {CH.V['body_x0']:.0f}")
    assert rows["FAT-18"]["where"].startswith("CH-P03") and rows["FAT-19"]["where"].startswith("CH-P15")
    assert rows["FAT-20"]["where"].startswith("CH-P15") and rows["FAT-20"]["iiw"] == "415"
    plate = next(f for f in CH.data["fittings"] if f["id"] == "CH-P15")
    ep = CH.ev(plate["at"])
    assert plate["w"] == pytest.approx(CH.role_sec["rail"].d + CH.role_sec["raiser"].t)
    assert ep[0] < CH.V["body_x0"] and abs(ep[2] - (CH.V["rail_underside_z"] + plate["w"] / 2)) < 1e-6


def test_end_plate_solver_matches_a_strip():
    """Far from its short edges a long plate under a uniform line load bends as a strip simply supported on its long
    edges: half the load times half the span less a quarter of the load's width."""
    q, span, foot = 100.0, 46.0, 26.0
    m = end_plate(span, 600.0, 0.0, 600.0, q, q, foot, free_bottom=False)["moment"]
    assert m == pytest.approx(q / 2 * (span / 2 - foot / 4), rel=0.03)


def test_end_plate_with_a_free_edge_balances_and_bends_as_a_strip():
    """With Poisson's ratio at zero a tall plate under a line load down its whole height bends as a strip near its free
    edge, each web taking half the load. Under the heel's rising load the webs, the top and the corners carry it all."""
    q, span, foot = 100.0, 46.0, 26.0
    c = end_plate(span, 400.0, 0.0, 400.0, q, q, foot, nu=0.0)
    assert c["web"][:20] == pytest.approx(q / 2, rel=0.01)
    r = end_plate(span, 147.75, 0.0, 138.0, 20.0, 183.0, foot)
    carried = (2 * r["web"].sum() + r["top"].sum()) * r["h"] + 2 * (r["corner_top"] + r["corner_bottom"])
    assert carried == pytest.approx(r["load"], rel=0.01) and r["corner_top"] < 0

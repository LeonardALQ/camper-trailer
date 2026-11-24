"""The chassis frame analysis (cad/chassis_fea.py): the load mapping balances, and the composite rail matches hand
arithmetic."""
import math
import re

import pytest

from cad.chassis import fitting_boxes
from cad.chassis_fea import end_plate, principal_range
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
    the ones the data gives CH-P03, on the rail's end plate CH-P15 that closes the rail's front end. The plate stands
    over the raiser's bottom wall, so its top weld joins both walls, and its bottom edge stands `lift` clear of the
    drawbar member (I2-75)."""
    rows = {r["id"]: r for r in RES["fatigue"]}
    assert rows["FAT-17"]["where"].endswith(f"at X {CH.V['body_x0']:.0f}")
    assert rows["FAT-18"]["where"].startswith("CH-P03") and rows["FAT-19"]["where"].startswith("CH-P15")
    assert rows["FAT-20"]["where"].startswith("CH-P15") and rows["FAT-20"]["iiw"] == "424"
    plate = next(f for f in CH.data["fittings"] if f["id"] == "CH-P15")
    ep = CH.ev(plate["at"])
    assert plate["lift"] + plate["w"] == pytest.approx(CH.role_sec["rail"].d + CH.role_sec["raiser"].t)
    assert ep[0] < CH.V["body_x0"] and abs(ep[2] - (CH.V["rail_underside_z"] + plate["lift"] + plate["w"] / 2)) < 1e-6


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
    assert c["webs"][0][:20] == pytest.approx(q / 2, rel=0.01) and c["webs"][1][:20] == pytest.approx(q / 2, rel=0.01)
    r = end_plate(span, 147.75, 0.0, 138.0, 20.0, 183.0, foot, centre=span / 2 - 4.0, km=2.9)
    corners = r["corner_top"] + r["corner_bottom"] + r["corner_top_far"] + r["corner_bottom_far"]
    carried = (r["webs"][0].sum() + r["webs"][1].sum() + r["top"].sum()) * r["h"] + corners
    assert carried == pytest.approx(r["load"], rel=0.01) and r["corner_top"] < 0


def test_moving_the_heel_off_the_middle_raises_the_near_web():
    """The heel's pull moved towards one web loads that web's weld harder and the far one's less (I2-60), and a line
    moment, the moment of the pull's part along the plate applied at its face, adds to one web what it takes from the
    other: on a long strip, the moment over the span."""
    span, foot = 46.0, 26.0
    mid = end_plate(span, 147.75, 0.0, 138.0, 20.0, 183.0, foot)
    off = end_plate(span, 147.75, 0.0, 138.0, 20.0, 183.0, foot, centre=span / 2 - 5.6)
    assert mid["webs"][0].max() == pytest.approx(mid["webs"][1].max(), rel=1e-6)
    assert off["webs"][0].max() > 1.2 * mid["webs"][0].max() and off["webs"][1].max() < mid["webs"][1].max()
    m = 100.0
    strip = end_plate(span, 600.0, 0.0, 600.0, 1.0, 1.0, foot, free_bottom=False, km=m)
    assert strip["webs"][0][300] == pytest.approx(0.5 - m / span, rel=0.01)
    assert strip["webs"][1][300] == pytest.approx(0.5 + m / span, rel=0.01)


def test_fat20_reads_the_heel_where_the_gusset_stands():
    """FAT-20 takes the heel's place across CH-P15 and the pull's direction from CH-P03's data (I2-60): the gusset's boxes
    run from the member's line at its toe to root_gusset_heel_y at the plate's front face, and end_plate_under_heel
    puts the heel there, its pull along that line."""
    from cad.chassis_fea import Analysis
    V = CH.V
    g = next(f for f in CH.data["fittings"] if f["id"] == "CH-P03")
    ch_f = next(f for f in CH.fittings if f.id == "CH-P03")
    road = [b for b in fitting_boxes(CH, ch_f) if b[1] > 0]
    first, last = min(road), max(road)
    assert (first[1] + 5) == pytest.approx(CH.db_y(V["root_gusset_toe_x"]))
    assert (last[4] - 5) == pytest.approx(V["root_gusset_heel_y"]) and last[3] == pytest.approx(V["body_x0"] - 16)
    lay, ch, _ = TRAILER._chassis
    p = Analysis(lay, TRAILER, ch).end_plate_under_heel(20.0, 180.0)
    span = CH.role_sec["rail"].b - CH.role_sec["rail"].t
    assert p["centre"] == pytest.approx(span / 2 - (V["rail_c"] - V["root_gusset_heel_y"]))
    assert math.tan(p["angle"]) == pytest.approx((V["root_gusset_heel_y"] - CH.db_y(V["root_gusset_toe_x"])) / g["l"])
    assert abs(p["webs"][0].max() - p["webs"][1].max()) < 0.05 * p["webs"][0].max()


def test_heel_fillets_on_their_skewed_joint():
    """The gusset meets the end plate about 20 degrees off its normal in plan, so its heel's inboard fillet lies in the
    acute dihedral angle and the outboard one in the obtuse (I2-72): 8 mm legs both sides give throats of 6.55 and
    4.59 mm there and 5.66 mm on a square joint, and the data's legs give both throats at least that 5.66 mm."""
    from cad.chassis_fea import Analysis, heel_throats
    assert heel_throats((8, 8), 0.0) == pytest.approx((8 / math.sqrt(2), 8 / math.sqrt(2)))
    assert heel_throats((8, 8), math.radians(19.91)) == pytest.approx((6.55, 4.59), abs=0.01)
    lay, ch, _ = TRAILER._chassis
    g = next(f for f in CH.data["fittings"] if f["id"] == "CH-P03")
    p = Analysis(lay, TRAILER, ch).end_plate_under_heel(20.0, 180.0)
    assert min(heel_throats(g["heel_legs"], p["angle"])) >= 8 / math.sqrt(2)


def test_principal_range_of_a_weld():
    """FAT-20 reads a weld's normal and shear ranges, in phase, as their maximum principal stress range (IIW 4.2 b,
    I2-67): the normal range alone with no shear, the shear range at 45 degrees with no normal range, and the inboard
    web's 17.47 MPa normal and 10.76 MPa shear of 8e7e9bb as 22.59 MPa, 25.5 degrees off the weld's normal."""
    assert principal_range(17.5, 0.0) == pytest.approx((17.5, 0.0))
    assert principal_range(0.0, 10.0) == pytest.approx((10.0, 45.0))
    rng, angle = principal_range(17.47, 10.76)
    assert rng == pytest.approx(22.59, abs=0.01) and angle == pytest.approx(25.5, abs=0.05)


def test_fat20_reads_the_principal_stress_with_its_roots_inspected():
    """FAT-20 is IIW 424 at FAT 45, a single-sided butt weld of a rectangular hollow section's walls under 8 mm to an
    intermediate plate with its root checked by NDT (I2-74), as the end plates' weld roots are inspected by videoscope,
    and its range is the governing weld's maximum principal stress range, its direction inside the 60 degrees off the
    weld's normal to which IIW 4.3 holds the principal stress (I2-67). The walls it reads are under 8 mm."""
    row = next(r for r in RES["fatigue"] if r["id"] == "FAT-20")
    assert row["iiw"] == "424" and row["fat"] == 45 and row["cafl"] == pytest.approx(0.585 * 45)
    assert int(re.search(r"its principal stress (\d+) degrees off", row["where"]).group(1)) <= 60
    plate = next(f for f in CH.data["fittings"] if f["id"] == "CH-P15")
    rail = CH.role_sec["rail"]
    assert rail.t < 8 and rail.t + plate["lift"] + plate["w"] - rail.d < 8


def test_each_rails_front_end_vents_and_drains_for_galvanising():
    """Each rail's closed front end has a vent near its top and drains near its floor in its outer web, close behind
    the end plate, placed by CHS-10's rules (I2-75), and with the slot the plate's bottom edge leaves over the rail's
    floor and the front bay's cable holes it opens at least the four 20 mm holes the GAA's guide asks of an RHS 150 x 50
    (Table 3). The plate's bottom edge stands at least the guide's 2.5 mm over the rail's floor."""
    V, rail = CH.V, CH.role_sec["rail"]
    plate = next(f for f in CH.data["fittings"] if f["id"] == "CH-P15")
    slot = plate["lift"] - rail.t
    assert slot >= 2.5
    for side in ("K", "R"):
        front = [h for h in RES["holes"] if h.get("frame") == f"RL-{side}" and h["wall"].startswith("the rail's")
                 and 0 < h["x"] - V["body_x0"] <= 150]
        galv = [h for h in front if set(h["runs"]) & {"vent", "drain"}]
        vents = [h for h in galv if h["runs"] == ["vent"] and h["wall"] == "the rail's outer web"]
        drains = [h for h in galv if h["runs"] == ["drain"] and h["wall"] == "the rail's outer web"]
        assert vents and drains and all(h["ok"] for h in galv), side
        assert max(h["z"] + h["d"] / 2 for h in vents) >= V["rail_top_z"] - rail.t - 25, side
        assert min(h["z"] - h["d"] / 2 for h in drains) <= V["rail_underside_z"] + rail.t + 25, side
        assert min(h["x"] for h in galv) - V["body_x0"] <= 40, side
        area = sum(math.pi * h["d"] ** 2 / 4 for h in front) + slot * (rail.b - 2 * rail.t - 2 * (rail.ro - rail.t))
        assert area >= 4 * math.pi * 20 ** 2 / 4, side


def test_the_videoscope_reaches_each_end_plates_weld_roots():
    """FAT-20's class rests on viewing each end plate's weld roots from inside the rail (I2-67), and the videoscope goes
    in through a hole in the rail's web: each rail has one of at least 10 mm, room for a 6 mm probe, within 150 mm
    behind its end plate."""
    for side in ("K", "R"):
        near = [h for h in RES["holes"] if h.get("frame") == f"RL-{side}" and h["wall"].startswith("the rail's")
                and 0 < h["x"] - CH.V["body_x0"] <= 150 and h["d"] >= 10]
        assert near, side

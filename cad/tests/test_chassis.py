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


def test_each_rails_front_end_drains_for_galvanising():
    """Hung drawbar end down and rolled either side down (galvanising_dip, I2-79), each rail's closed front end is its
    low end, so it drains in both webs near its floor, close behind the end plate, placed by CHS-10's rules, and through
    the slot the plate's bottom edge leaves over the floor, at least the guide's least hole of 10 mm. With the front bay's
    cable holes it opens at least the four 20 mm holes the GAA's guide asks of an RHS 150 x 50 (Table 3). No hole stands
    near the rail's top within 150 mm of the plate but the cable holes, out of the peak of the plate's line force (I2-80),
    and each drain is read in that field (CHS-10)."""
    V, rail = CH.V, CH.role_sec["rail"]
    plate = next(f for f in CH.data["fittings"] if f["id"] == "CH-P15")
    slot = plate["lift"] - rail.t
    assert slot >= 10
    dip = CH.data["galvanising_dip"]
    assert all(e + 2 * dip["clearance"] <= lim for e, lim in zip(dip["envelope"], dip["dip"][1:]))
    for side in ("K", "R"):
        front = [h for h in RES["holes"] if h.get("frame") == f"RL-{side}" and h["wall"].startswith("the rail's")
                 and 0 < h["x"] - V["body_x0"] <= 150]
        galv = [h for h in front if set(h["runs"]) & {"vent", "drain"}]
        assert galv and all(h["ok"] and h["runs"] == ["drain"] and h["field"] for h in galv), side
        for web in ("the rail's outer web", "the rail's inner web"):
            drains = [h for h in galv if h["wall"] == web]
            assert len(drains) >= 2 and min(h["z"] - h["d"] / 2 for h in drains) <= V["rail_underside_z"] + rail.t + 25, (side, web)
        assert min(h["x"] for h in galv) - V["body_x0"] <= 40, side
        assert all(h["z"] < V["rail_underside_z"] + rail.d / 2 for h in galv), side
        area = sum(math.pi * h["d"] ** 2 / 4 for h in front) + slot * (rail.b - 2 * rail.t - 2 * (rail.ro - rail.t))
        assert area >= 4 * math.pi * 20 ** 2 / 4, side


def test_every_closed_section_drains_and_vents_in_the_dip():
    """CHS-11 (I2-84): in both rolls and at every pitch of the dip, each closed section's low points reach a drain or an
    open end and its high points a vent or an open end within 50 mm, each closed end's holes give the guide's table
    area, and the lower drawbar member, whose mitre is its low point, drains there."""
    g = RES["galvanising"]
    assert g["sections"] and all(r["ok"] for r in g["sections"])
    assert {"RL-K", "DB-K", "DB-R", "CM-04.1", "CM-04.2", "DB-BR"} <= {r["id"] for r in g["sections"]}   # the twin's two tubes
    mitre = [h for h in g["holes"] if h["tube"] in ("DB-KB", "DB-RB") and h["use"] == "drain"]
    assert len(mitre) == 4 and all(abs(h["x"] - CH.V["body_x0"] - 40) < 10 for h in mitre)
    assert max(r["low_depth"] for r in g["sections"] if r["id"].startswith("DB-") and r["id"] != "DB-BR") <= g["max_depth"]


def test_the_laps_are_opened_and_stitched():
    """The drawbar members' laps under the rails are opened to 2.5 mm and stitch welded, as the guide asks of an overlap
    that is not sealed (I2-79), and FAT-21 reads the stitches' ends at IIW 324's floor along the whole lap."""
    row = next(r for r in RES["fatigue"] if r["id"] == "FAT-21")
    assert row["iiw"] == "324" and row["fat"] == 36 and row["ok"]
    x = float(re.search(r"at X (\d+)", row["where"]).group(1))
    assert CH.V["body_x0"] - 1 <= x <= CH.V["db_end_x"] + 1


def test_the_videoscope_reaches_each_end_plates_weld_roots():
    """FAT-20's class rests on viewing each end plate's weld roots from inside the rail (I2-67), and the videoscope goes
    in through a hole in the rail's web: each rail has one of at least 10 mm, room for a 6 mm probe, within 150 mm
    behind its end plate."""
    for side in ("K", "R"):
        near = [h for h in RES["holes"] if h.get("frame") == f"RL-{side}" and h["wall"].startswith("the rail's")
                and 0 < h["x"] - CH.V["body_x0"] <= 150 and h["d"] >= 10]
        assert near, side


def test_each_hinge_gusset_is_cut_to_bear_on_both_faces():
    """CH-P08 as made (xt_hinges `gusset`): each gusset's axis runs at 45 degrees from the crossmember's face to the step of
    the cheek beside it, 10 mm inboard of the rail's inner face (I2-99), its long side 25 mm beyond each end and its short
    side 25 mm inside, its end on the crossmember where the data's length to the web puts it. The frame model ties it where
    its axis meets the two faces, the centres of its welds."""
    g = CH.data["xt_hinges"]["gusset"]
    length = CH.ev(g["length"])
    y_in = CH.V["rail_c"] - CH.role_sec["rail"].b / 2
    cheek = CH.data["xt_hinges"]["cheek"]
    for hg in CH.hinge_gussets():
        assert hg["on_cheek"]
        assert math.dist(hg["p0"], hg["p1"]) == pytest.approx(length - cheek["t"] * math.sqrt(2), abs=1e-6)
        assert hg["p0"][0] == pytest.approx(hg["rear_x"]) and abs(hg["p1"][1]) == pytest.approx(y_in - cheek["t"])
        assert abs(hg["p0"][1]) == pytest.approx(y_in - length / math.sqrt(2))
    fm = TRAILER._chassis[1].frame()
    for hg in CH.hinge_gussets():
        el = next(e for e in fm.f.elements if e.member == hg["id"])
        ends = {tuple(round(v, 3) for v in fm.f.nodes[n]) for n in (el.i, el.j)}
        assert ends == {tuple(round(v, 3) for v in hg["p0"]), tuple(round(v, 3) for v in hg["p1"])}


def test_the_hinge_gussets_welds_hold():
    """CHS-16: the gussets' end welds, read round each cut face by the elastic vector method in every case."""
    r = RES["local"]["hinge_gussets"]
    assert r["util"] <= 1.0 and any("LC8u" in p["part"] for p in r["parts"])


def test_the_shear_panels_bolts_stand_clear_of_the_sheets_edges():
    """CHS-13's bolts (shear_panels, CH-P17): every bolt's centre stands at least 1.75 d from the sheet's sheared edges
    and cuts (AS 4100 Table 9.6.2) and its neighbours at least 3 d away (AS/NZS 4600 5.3.1), each rail's angle ahead of
    the rear airbag's bracket carries two, which take its diagonal's force, and the sheet's bearing and tear-out at the
    most loaded bolt are read by both standards (fx22-rear)."""
    sp = CH.shear_panels()[0]
    d = sp["fixing"]["d"]
    groups = {g["group"]: g for g in RES["local"]["shear_panel"]["bolt_groups"]}
    assert min(g["edge"] for g in groups.values()) >= 1.75 * d - 1e-6
    assert groups["rail"]["n_side"] == 2 and set(groups) == {"rail", "rear"}
    for a in sp["bolts"]:
        for b in sp["bolts"]:
            if a is not b:
                assert math.hypot(a["x"] - b["x"], a["y"] - b["y"]) >= 3 * d - 1e-6
    parts = " ".join(p["part"] for p in RES["local"]["shear_panel"]["parts"])
    for what in ("bearing at a bolt, AS 4100", "bearing at a bolt, AS/NZS 4600", "tear-out at a bolt, AS 4100", "tear-out at a bolt, AS/NZS 4600"):
        assert what in parts


def test_the_panels_angles_and_the_cheeks_end_apart():
    """I2-95: the shear panel's angles along the rails start a set gap behind the XT centre's rear hinge cheeks, and
    FAT-22 and FAT-23 read both parts' weld ends on the rail."""
    spec = next(f for f in CH.data["fittings"] if f["id"] == "CH-P17")
    rails = [p for p in CH.panel_pieces() if p["use"] == "rail"]
    cheek_ends = [c["box"][3] for c in CH.hinge_cheeks() if c["id"].endswith("B") and c["wheel"].startswith("R")]
    assert rails and cheek_ends
    for p in rails:
        assert p["x0"] - max(cheek_ends) == pytest.approx(spec["rails"]["gap"])
    fat = {f["id"]: f for f in RES["fatigue"]}
    assert fat["FAT-22"]["fat"] == 63 and fat["FAT-23"]["fat"] == 50


def test_the_plate_buckling_reads_the_closed_form_on_four_held_edges():
    """I2-98: chassis_fea.plate_shear_buckling, held at points every 15 mm round all four edges, gives the closed form's
    k = 5.35 + 4 (a / b) squared for a plate in shear within 1 %, the check its reading on the held points rests on."""
    from cad.chassis_fea import NU, plate_shear_buckling
    a, b, t = 755.0, 1169.0, 3.0
    pts = [(x, b * j / 78) for x in (0.0, a) for j in range(79)] + [(a * j / 50, y) for y in (0.0, b) for j in range(1, 50)]
    k = 5.35 + 4 * (a / b) ** 2
    closed = k * math.pi ** 2 * 200_000.0 * t ** 2 / (12 * (1 - NU ** 2) * a ** 2)
    assert plate_shear_buckling(0.0, a, 0.0, b, t, pts, deg=14) == pytest.approx(closed, rel=0.01)


def test_the_panel_reads_its_tongues_roots_and_its_held_points():
    """I2-98: CHS-13 reads every tongue's root, by von Mises in the working cases and by its plastic interaction at the
    ultimate, and the sheet's buckling on the points its bolts and tongues hold, and the sheet has no stiffener."""
    r = RES["local"]["shear_panel"]
    parts = " ".join(p["part"] for p in r["parts"])
    assert "tongue's and wing's roots, von Mises, LC8a" in parts and "tongue's and wing's roots, plastic interaction times fy, LC8u" in parts
    assert len(r["tongues"]) == len(CH.shear_panels()[0]["sheet"]["tongues"])
    assert all(p["use"] in ("rail", "crossmember") for p in CH.panel_pieces())
    assert r["util"] <= 1.0


def test_every_gusset_lands_on_its_cheeks_step():
    """I2-99: each hinge gusset's rail end lands on the step of the cheek beside it, its footprint and its welds inside
    the step, and CHS-16 reads the web under the step and the step's welds."""
    ck = CH.data["xt_hinges"]["cheek"]
    sec = CH.sections[next(f for f in CH.data["fittings"] if f["id"] == "CH-P08")["section"]]
    leg = CH.data["xt_hinges"]["gusset"]["weld"]["leg"]
    cheeks = {c["gusset"]: c for c in CH.hinge_cheeks() if c["gusset"]}
    half = sec.b / 2 * math.sqrt(2)
    for g in CH.hinge_gussets():
        step = cheeks[g["id"]]["boxes"][1]
        assert g["on_cheek"]
        assert step[0] <= g["rail_x"] - half - leg and g["rail_x"] + half + leg <= step[3]
        assert step[2] <= g["z"] - sec.d / 2 - leg and g["z"] + sec.d / 2 + leg <= step[5]
    parts = " ".join(p["part"] for p in RES["local"]["hinge_gussets"]["parts"])
    assert "chord face plastification, LC8u" in parts and "its step's two welds" in parts
    assert RES["local"]["hinge_gussets"]["util"] <= 1.0


def test_lc8a_reads_both_wheels_of_an_axle_held_at_the_recovery_limit():
    """I2-93: LC8a reads every recovery point with both wheels of the front or the rear axle held fast at the data's
    held-axle limit, its ultimate in LC8a's ratio, and the recovery summary keeps those pulls apart from the rated ones."""
    rec = RES["recovery"]["LC8a"]
    lc8 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a")
    k = 3 * len(lc8["reaction"]["weight"]) * len(lc8["reaction"]["nose"]) * len(lc8["reaction"]["mu"])
    # at the front lugs and rear tongues every wheel free and each wheel held at LC8a's 5 headings (I2-127), and at the
    # coupling every wheel free and each wheel held along the rail axis, each up, level and down, on each support and
    # bound of mu
    assert rec["cases"] == 4 * (5 + 5 * len(CH.suspension)) * k + (1 + len(CH.suspension)) * k
    assert rec["axle"]["cases"] == 4 * 2 * 5 * k + 2 * k
    lc8 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a")
    assert lc8["held_axle_n"] % 5000 == 0 and lc8["held_axle_n"] < lc8["force_n"]


def test_lc8a_reads_one_held_wheel_at_the_held_wheel_limit():
    """I2-93 and I2-114: LC8a reads every pull through one held wheel at the data's held-wheel limit, a whole 5 kN at most
    the rated pull and at least the held-axle limit, and every reading a held wheel governs names that limit."""
    lc8 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a")
    # a held wheel may take a lower limit than a held axle, since the free tyres' side forces reach its hub with the pull
    # while an axle held holds the trailer from turning (I2-124)
    assert lc8["held_wheel_n"] % 5000 == 0 and lc8["held_wheel_n"] <= lc8["force_n"]
    cases = [r["case"] for rows in RES["envelope"].values() for r in rows.values()]
    cases += [h[k]["case"] for h in RES["holes"] for k in ("static", "ultimate") if h.get(k)]
    held = [c for c in cases if re.search(r", wheel [FR][KR] held", c)]
    assert held and all(f"held, at the {lc8['held_wheel_n'] / 1000:g} kN limit" in c for c in held)


def test_trailer_md_gives_the_recovery_rule():
    """I2-93, I2-100, I2-114 and I2-127: TRAILER.md's recovery rule quotes LC8a's rating and directions and the frame's
    three limits, the fail checks' rule with every wheel free, one wheel held and an axle held, which the user's classes
    take the lesser of with their tipping pulls (chassis_fea.recovery_rule, test_recovery's tests of the classes)."""
    from pathlib import Path

    from cad.chassis_fea import recovery_rule
    r = recovery_rule(RES, next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a"))
    text = (Path(__file__).resolve().parents[2] / "TRAILER.md").read_text()
    i = next(k for k, x in enumerate(text.splitlines()) if x.startswith("- Recovery:"))
    rest = text.splitlines()[i + 1:]
    block = " ".join([text.splitlines()[i]] + rest[:next((k for k, x in enumerate(rest) if x.startswith(("- ", "#"))), len(rest))])
    frame = (f"{r['free_kn']:g} kN with every wheel free, {r['held_wheel_kn']:g} kN with one wheel held fast and "
             f"{r['held_axle_kn']:g} kN with both wheels of one axle held fast")
    for figure in (f"{r['rated_kn']:.1f} kN", frame, f"{r['sideways_deg']:g} degrees", f"{r['vertical_deg']:g} degrees"):
        assert figure in block, figure
    assert "coupling along the trailer's line only" in block


def test_lc8a_reads_every_wheel_free_at_the_free_limit():
    """I2-118 and I2-119: with every wheel free LC8a reads each pull at the data's free limit where one stands under the
    rated pull, a whole 5 kN at least the held-wheel limit, and every reading such a pull governs names that limit."""
    lc8 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a")
    free = lc8.get("free_n", lc8["force_n"])
    assert lc8["held_wheel_n"] <= free <= lc8["force_n"]
    if free < lc8["force_n"]:
        assert free % 5000 == 0
        cases = [h[k]["case"] for h in RES["holes"] for k in ("static", "ultimate") if h.get(k)]
        cases += [r["case"] for lc_id in ("LC8a", "LC8u") for r in RES["envelope"][lc_id].values()]
        free_cases = [c for c in cases if "point," in c and "held" not in c]
        assert free_cases and all(f"at the {free / 1000:g} kN limit" in c for c in free_cases)


def test_the_hinge_bars_runs_and_the_fillers_are_read():
    """I2-118 and I2-119: CHS-18 reads each hinge bar's weld runs on every frame model at the pull and at its ultimate,
    CHS-19 reports the bars and their plates on the elastic models, and each front cheek meets its filler at its
    crossmember's front face, CHS-14 reading the filler's welds and section with the cheeks'."""
    runs = RES["local"]["hinge_runs"]
    assert {p["part"] for p in runs["parts"]} >= {f"{lc}, the hinge bars {b}" for lc in ("LC8a", "LC8u") for b in
                                                 ("rigid", "elastic on free bushes", "elastic on stiff bushes")}
    bar = RES["local"]["hinge_bar"]
    assert bar["parts"] and bar["plates"]
    fillers = CH.hinge_fillers()
    assert len(fillers) == 4
    for c in CH.hinge_cheeks():
        fl = next((f for f in fillers if f["wheel"] == c["wheel"]), None)
        if c["way"] < 0:
            assert abs(c["joint_x"] - fl["front"]) < 1e-6 and not c["tail"]
    parts = " ".join(p["part"] for p in RES["local"]["hinge_cheeks"]["parts"])
    assert "filler's section" in parts and "flare-bevel weld at the rail's outer bottom corner" in parts


def test_the_elastic_bars_runs_are_held_at_their_welds():
    """I2-121: on the elastic models each hinge bar's runs are welded to the crossmember as weld points at each run's two
    ends and its centre on both fillets, carrying a sixth, two thirds and a sixth of the run at the fillet's own shear
    stiffness and passing next to no moment, the hinge plates are members of their own section, CHS-18 reads each
    elastic run on its own, and the same runs in the service cases are read beside it."""
    from cad.frame import E_STEEL, G_STEEL
    b = CH.data["xt_hinges"]["bar"]
    fm = CH.frame(None, "crossmember", "elastic", "free")
    k_line = G_STEEL * 0.7 * b["leg"] / b["leg"] * b["run"]          # one fillet's shear stiffness over its run, N/mm
    for w in CH.suspension:
        welds = [el for el in fm.f.elements if el.member == f"hinge {w['id']}"]
        assert len(welds) == 2 * 3 * len(b["runs"]), w["id"]
        k = sum(12 * E_STEEL * el.sec.I_strong for el in welds)          # 1 mm links, 12 E I / L^3
        assert abs(k - 2 * len(b["runs"]) * k_line) < 1e-6 * k
        assert all(4 * E_STEEL * el.sec.I_strong < 1e-4 * k_line * b["run"] ** 2 for el in welds)
        assert sum(1 for el in fm.f.elements if el.member == f"XT-PLATE-{w['id']}") == 4
    runs = RES["local"]["hinge_runs"]
    assert {p["part"].split(",")[0] for p in runs["parts"]} >= {"LC8a", "LC8u"}
    assert all(r["util"] >= 0 for r in runs["beside"].values())


def test_the_hinge_runs_fail_on_every_case_through_the_joint_and_give_vsb1s_rig_beside():
    """The conductor's ruling of 27 Nov 2026: CHS-18 fails on every case in which the trailer's own loads pass through
    the hinge joint, LC1 to LC5b, LC8a at the pull and its ultimate and LC8b, each read against the weld's strength over
    the case's factor. VSB1's drawbar and chain tests hold the body on a rig at its suspension mounts (VSB1 Rev 6
    14.2.1), so CHS-18 and CHS-19 give LC6 and LC6b beside their rows and do not read them, and their whys say why."""
    import yaml
    from cad.chassis_fea import RIG_CASES
    runs, bar = RES["local"]["hinge_runs"], RES["local"]["hinge_bar"]
    lcs = {lc["id"]: lc for lc in CH.data["load_cases"]}
    mat = CH.data["material"]
    wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
    assert RIG_CASES == ("LC6", "LC6b")
    assert {p["part"].split(",")[0] for p in runs["parts"]} == {"LC1", "LC2", "LC3", "LC4", "LC5a", "LC5b", "LC8a", "LC8u", "LC8b"}
    for p in runs["parts"]:
        lc = p["part"].split(",")[0]
        assert p["limit_mpa"] == pytest.approx(wcap / (lcs[lc]["factor"] if lc in lcs else 1), rel=1e-12), p["part"]
    assert runs["util"] == pytest.approx(max(p["util"] for p in runs["parts"]), rel=1e-12)
    assert {k.split(",")[0] for k in runs["beside"]} == set(RIG_CASES)
    assert {p["part"].split(", ")[1] for p in bar["parts"]} == {"LC8a", "LC8u"}
    assert {k.split(",")[0] for k in bar["beside"]} == set(RIG_CASES)
    assert all(v["mpa"] > 0 and v["plates"] for v in bar["beside"].values())
    from cad.partsdb import DATA
    checks = {c["id"]: c for c in yaml.safe_load((DATA / "checks.yaml").read_text())["trailer_checks"]}
    for cid in ("CHS-18", "CHS-19"):
        assert "14.2.1" in checks[cid]["why"] and "LC6b" in checks[cid]["why"], cid
    assert "LC1 to LC5b, LC8a and LC8b" in checks["CHS-18"]["why"]


def test_the_bottom_wall_under_the_front_fillets_is_read_as_the_plate_it_is():
    """The conductor's ruling of 27 Nov 2026: the hinge crossmember's bottom wall under each run's front fillet comes from
    its plate model (cad/wall_plate.py), which gives Timoshenko's square plate, and the data keeps its bounds for the
    RHS 150 x 100 x 6 they were read on. Since 27 Nov 2026 the hinge crossmembers are the twin of two RHS 150 x 50 x 6,
    whose fillets all stand over webs, so the frame model puts no wall in series under any weld point but the web's own
    stretch under each (I2-125), the wall's flats read none, and FAT-25 reads no wall and says so. On the single tube
    the front fillet still reads its flat."""
    from dataclasses import replace
    from cad import wall_plate as WP
    from cad.chassis import wall_flats
    from cad.frame import E_STEEL
    b = CH.data["xt_hinges"]["bar"]
    wall = b["wall"]
    assert WP.check_square_plate() == pytest.approx(0.01160, rel=0.01)
    single = CH.sections[wall["section"]]
    assert single.id == "RHS_150x100x6" and single.cells == 1
    y_in = CH.V["rail_c"] - CH.role_sec["rail"].b / 2
    runs = [(u - b["run"] / 2, u + b["run"] / 2) for u in b["runs"]]
    for key, data in (("mid/pinned", wall), ("flat/clamped", wall["other"])):
        r = WP.model(single, 2 * y_in, runs, *key.split("/"))
        assert [q["uniform"] / 1000 for q in r["runs"]] == pytest.approx(data["kn_mm"], abs=0.051), key
        assert [q["hot_even"] * 1000 for q in r["runs"]] == pytest.approx(data["toe_mpa_kn"], abs=0.051), key
        assert all(q["k"] >= q["uniform"] for q in r["runs"])          # the rigid bar's spread is the stiffer
    assert all(a < c for a, c in zip(wall["kn_mm"], wall["other"]["kn_mm"]))
    bw = CH.data["xt_arms"]["parts"]["bar"]["w"]
    for cm in CH.hinge_crossmembers():
        assert cm.sec.cells == 2 and cm.sec.cell == "RHS_150x50x6" and cm.sec.b == 2 * CH.sections["RHS_150x50x6"].b
        assert wall_flats(CH, cm, CH.hinge_bar_x(cm), bw) == {-1: False, 1: False}, cm.id
        one = replace(cm, sec=single)
        assert wall_flats(CH, one, CH.hinge_bar_x(one), bw) == {-1: True, 1: False}, cm.id
    fm = CH.frame(None, "crossmember", "elastic", "free")
    k_weld = E_STEEL * 0.7 * b["leg"] / b["leg"] * b["run"]          # one fillet's normal stiffness over its run, N/mm
    for w in CH.suspension:
        cmw = next(m for m in CH.members if m.station == w["station"] and m.role == "cm_xt")
        xb = CH.hinge_bar_x(cmw)
        web = CH.data["xt_hinges"]["web"]["kn_mm"]
        for side, behind in (("rear", True), ("front", False)):
            k_model = sum(E_STEEL * el.sec.A for el in fm.f.elements
                          if el.member == f"hinge {w['id']}" and (fm.f.nodes[el.i][0] > xb) == behind)
            k_series = sum(1 / (1 / (s * k_weld) + 1 / (s * kw * 1000)) for kw in web[side] for s in (1 / 6, 2 / 3, 1 / 6))
            assert k_model == pytest.approx(k_series, rel=1e-9), (w["id"], side)
    fat = next(f for f in RES["fatigue"] if f["id"] == "FAT-25")
    assert fat["range_mpa"] == 0 and fat["ok"] and "both fillets over webs" in fat["where"]


def test_the_twin_hinge_crossmembers_seams_dip_and_bolts():
    """fx37-twin: each XT hinge crossmember is two RHS 150 x 50 x 6 seam welded. CHS-20 reads the seams in every case
    through the hinge joint, LC1 to LC5b, LC8a at the pull and its ultimate and LC8b, on all three models, against the
    weld's strength over each case's factor, with VSB1's rig cases beside it. The dip reads each tube as its own closed
    section with its own drain and vent through the rail's web at both ends, the two webs face to face are a sealed
    overlap with the guide's vents, and each bolt of the bearers and the front guard's hanger passes all four webs."""
    from cad.chassis_dip import frame_sections
    from cad.chassis_fea import RIG_CASES
    seams = RES["local"]["hinge_seams"]
    lcs = {lc["id"]: lc for lc in CH.data["load_cases"]}
    mat = CH.data["material"]
    wcap = mat["weld_phi"] * 0.6 * mat["weld_fuw"]
    assert {p["part"].split(",")[0] for p in seams["parts"]} == {"LC1", "LC2", "LC3", "LC4", "LC5a", "LC5b", "LC8a", "LC8u", "LC8b"}
    assert {p["part"].split(", the hinge bars ")[1] for p in seams["parts"]} == {"rigid", "elastic on free bushes", "elastic on stiff bushes"}
    for p in seams["parts"]:
        lc = p["part"].split(",")[0]
        assert p["limit_mpa"] == pytest.approx(wcap / (lcs[lc]["factor"] if lc in lcs else 1), rel=1e-12), p["part"]
    assert {k.split(",")[0] for k in seams["beside"]} == set(RIG_CASES)
    sd = CH.data["xt_hinges"]["seam"]
    assert seams["throat_mm"] == pytest.approx(min(sd["throat_r"] * 15.0, 6.0))
    twins = {cm.id for cm in CH.hinge_crossmembers()}
    sections, holes = frame_sections(CH)
    ids = {s.id for s in sections}
    for cm in twins:
        assert cm not in ids and {f"{cm}.1", f"{cm}.2"} <= ids
        for k in (1, 2):
            for e in (0, 1):
                mine = [h for h in holes if h["tube"] == f"{cm}.{k}" and h["end"] == e and h["via"] == "host"]
                assert sorted(h["use"] for h in mine) == ["drain", "vent"], (cm, k, e)
    assert all(r["ok"] for r in RES["galvanising"]["sections"] if r["id"].split(".")[0] in twins)
    tw = next(o for o in RES["galvanising"]["overlaps"] if o["id"] == "TWIN")
    assert tw["ok"] and tw["need_n"] == 2 and tw["need_d"] == 12
    vents = [h for h in holes if h["member"] in twins and h.get("through")]
    assert {h["member"] for h in vents} == twins and all(h["d"] >= tw["need_d"] for h in vents)
    by_bolt: dict = {}
    for f in EV["layout"].fixing_holes():
        if f["member"] in twins:
            by_bolt.setdefault((f["member"], round(f["y"]), round(f["z"])), set()).add(f["face"])
    assert by_bolt and all(v == {"front web", "front tube's rear web", "rear tube's front web", "rear web"} for v in by_bolt.values())


def test_the_coupling_is_a_pull_point_under_the_same_limits():
    """The conductor's ruling of 27 Nov 2026: the recovery limits hold wherever the trailer is pulled from, so LC8a pulls
    at the coupling too, along the rail axis only within 15 degrees up or down, with every wheel free, with each wheel
    held, the free tyres' grip holding the trailer from turning about it as far as it does (I2-124), and with an axle
    held, under the same three limits, at each bound of the tyres' grip."""
    lc8 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a")
    assert lc8["coupling"] is True
    pts = RES["recovery"]["LC8a"]["points"]
    n_sup = len(lc8["reaction"]["weight"]) * len(lc8["reaction"]["nose"]) * len(lc8["reaction"]["mu"])
    assert pts["coupling, every wheel free"] == 3 * n_sup                 # level, 15 degrees up and down, each support
    assert pts["coupling, axle held"] == 2 * 3 * n_sup                    # each axle, along the rail axis
    assert pts["coupling, wheel held"] == len(CH.suspension) * 3 * n_sup  # each wheel, the pull along the rail axis
    assert all(pts[f"{w}, every wheel free"] == 2 * 5 * 3 * n_sup for w in ("front", "rear"))   # LC8a's five headings (I2-127)


def test_holes_in_one_section_are_read_together():
    """I2-111: every pair of holes in a rail and its raiser within the larger diameter of one another along the rail, a
    slot's length added, is read on one net section, each hole with the other, and no pair further apart. Beside the XT
    centre crossmember the service hole into OR-05 stands between its twin tubes' drains, vents and check holes in its
    rail, half a tube either side and more than a diameter from it, so it is read alone."""
    rail = [h for h in RES["holes"] if not h.get("open") and str(h.get("frame", "")).startswith("RL-")]
    assert rail
    for a in rail:
        for b in rail:
            if a is b or a["frame"] != b["frame"]:
                continue
            reach = max(a["d"], b["d"]) + (a["length"] - a["d"]) / 2 + (b["length"] - b["d"]) / 2
            assert (b["id"] in a.get("with", [])) == (abs(a["x"] - b["x"]) < reach), (a["id"], b["id"])
    cm = next(m for m in CH.members if m.station == "XT centre" and m.role == "cm_xt")
    for run in ("K-08", "K-09"):        # on the twin each tube's drain, vent and check hole stand half a tube either side
        svc = next(h for h in rail if h["runs"] == [run] and h["wall"] == "the raiser's outer web")
        corner = [h for h in rail if h["frame"] == svc["frame"] and abs(abs(h["x"] - svc["x"]) - cm.sec.cell_b / 2) < 1
                  and set(h["runs"]) & {"drain", "vent", "check"}]
        assert cm.sec.cells == 2 and len(corner) == 6, run
        assert all(cm.sec.cell_b / 2 >= max(h["d"], svc["d"]) for h in corner) and not {h["id"] for h in corner} & set(svc.get("with", [])), run
        assert abs(svc["x"] - cm.p0[0]) < 1


def test_a_hole_within_a_weld_run_is_read_outboard_of_its_node():
    """I2-112 and I2-109: the frame model lumps each of a hinge bar's 80 mm weld runs at its centre and ties the runs
    together through the rigid bar, so a hole in a hinge crossmember within the outermost run's length is read on the
    element outboard of that run's node, at that node, whichever side of it the hole's centre falls, and any other hole
    that reaches into the runs' span is read at both of the span's ends, on the element outboard of the outermost run's
    node and on the element inboard of the innermost run's node, the worse, and only those holes."""
    import numpy as np

    from cad.chassis_fea import Analysis
    an = Analysis(EV["layout"], TRAILER, CH)
    sites = an.hole_sites()
    run = CH.data["xt_hinges"]["bar"]["run"]
    hinged = {m.id: m for m in CH.hinge_crossmembers()}
    ends = []
    for h in sites:
        m = hinged.get(h["member"])
        side = sorted((yr for yr in (CH.hinge_weld_ys(m) if m else []) if yr * h["y"] > 0), key=abs)
        r = h["d"] / 2
        outer = bool(side) and abs(h["y"] - side[-1]) < run / 2 + r
        span = bool(side) and not outer and abs(h["y"]) + r > abs(side[0]) - run / 2 and abs(h["y"]) - r < abs(side[-1]) + run / 2
        assert (h.get("run_node") is not None) == outer and bool(h.get("span_nodes")) == span, h["id"]
        if outer:
            assert h["run_node"] == an.fm.cm_node(m.id, side[-1])
            ends.append((h, [(h["run_node"], True)]))
        if span:
            assert h["span_nodes"] == [(an.fm.cm_node(m.id, side[-1]), True), (an.fm.cm_node(m.id, side[0]), False)]
            ends.append((h, h["span_nodes"]))
    assert {"CM-04", "CM-05"} <= {h["member"] for h, nodes in ends if len(nodes) == 1}
    assert {"CM-04", "CM-05"} <= {h["member"] for h, nodes in ends if len(nodes) == 2}

    class Res:
        forces = None

    for h, nodes in ends:
        read, near = set(), set()
        for nd, outward in nodes:
            els = [k for k, el in enumerate(an.f.elements) if el.member == h["frame"] and nd in (el.i, el.j)]
            far = {k: an.f.elements[k].j if an.f.elements[k].i == nd else an.f.elements[k].i for k in els}
            on_side = [k for k in els if (abs(an.f.nodes[far[k]][1]) > abs(an.f.nodes[nd][1])) == outward]
            assert len(on_side) == 1, h["id"]
            read.add(on_side[0])
            near.update(els)
        for k in near:
            r = Res()
            r.forces = np.zeros((len(an.f.elements), 12))
            r.forces[k] = 1000.0
            assert (an.hole_stress(r, h)["eq"] > 0) == (k in read), (h["id"], k)


def test_the_bearers_and_hangers_bolt_holes_are_read_by_the_hole_checks():
    """I2-109, I2-116, I2-122: every hole the tanks' bearers' bolts and the guards' hangers' bolts and rivet nuts make
    (Layout.fixing_holes) is a hole CHS-08U, CHS-09, CHS-10 and CHS-12 read, numbered after every other hole so no id
    moves: the rivet nuts' in the rails' inner webs on the composite rail's section, alone, since nothing goes through the
    outer web, the bolts' in the crossmembers' webs the bearers stand on, the XT crossmembers and the rear one, on their
    crossmember's own, each bolt's hole in one web read with its hole in the other, and every one of them passes."""
    fix = EV["layout"].fixing_holes()
    bearing = {b["member"] for b in EV["layout"].tank_bearers()}
    bolts = [h for h in RES["holes"] if any(r.startswith(("bolt for", "rivet nut for")) for r in h.get("runs", []))]
    assert fix and len(bolts) == len(fix)
    assert sorted(int(h["id"][2:]) for h in bolts) == list(range(len(RES["holes"]) - len(fix) + 1, len(RES["holes"]) + 1))
    hinged = {m.id for m in CH.hinge_crossmembers()}
    mem = {m.id: m for m in CH.members}
    for f in fix:
        h = next(h for h in bolts if h["member"] == f["member"] and math.dist((h["x"], h["y"], h["z"]), (f["x"], f["y"], f["z"])) < 1)
        assert h["runs"] == [f["use"]] and h["d"] == f["d"], h["id"]
        rail = f["member"].startswith("RL-")
        assert h["frame"] == f["member"] and (rail or f["member"] in hinged | bearing), h["id"]
        along = (lambda o: o["x"]) if rail else (lambda o: o["y"])
        pair = [o for o in bolts if o is not h and o["member"] == h["member"] and abs(along(o) - along(h)) < 1]
        if f["use"].startswith("rivet nut"):
            assert rail and f["face"] == "inner web" and not pair, h["id"]
        else:                       # a bolt passes every web of its crossmember, four on a twin hinge crossmember
            webs = 2 * getattr(mem[f["member"]].sec, "cells", 1)
            assert len(pair) == webs - 1 and all(o["id"] in h.get("with", []) for o in pair), h["id"]
        assert h["ok"] and h["static_ok"] and h["ultimate"]["util"] <= 1, h["id"]


def test_the_grey_tank_and_its_water_bear_on_the_frame_at_its_bearers():
    """I2-109, I2-122: the frame model puts the grey tank and its grey water on the crossmembers its bearers UF-08B stand
    on, the XT rear shock and rear crossmembers, at each bearer's middle by its length (Analysis._tank_items), as it puts
    the fresh tanks on theirs, never shared between the rails over the tank's box. Each end's share goes by the tank's
    centre's place between the two bearing lines, so the shares keep the tank's mass and its moment about its centre."""
    from cad.chassis_fea import Analysis
    lay = EV["layout"]
    tank = lay.find("UF-08")
    on = {f"cm:{b['member']}" for b in lay.tank_bearers("UF-08B")}
    case = next(c for c in TRAILER.cases if c.id == "TC7")
    lines = {b.iid: m for b, m in lay.case_lines(case) if b.id in ("UF-08", "UF-08W") and m > 0}
    items = Analysis(lay, TRAILER, CH).items(case)
    xc = (tank.box[0] + tank.box[3]) / 2
    assert set(lines) == {"UF-08", "UF-08W"} and len(on) == 2
    for iid, m in lines.items():
        mine = [it for it in items if it.id == iid]
        assert {it.rule for it in mine} == on, (iid, {it.rule for it in mine})
        assert sum(it.m for it in mine) == pytest.approx(m, rel=1e-9), iid
        assert abs(sum(it.m * (it.p[0] - xc) for it in mine)) < 1e-6 * m * (tank.box[3] - tank.box[0]), iid


def test_every_check_is_read_on_the_hinge_bars_bounds():
    """I2-114: the frame analysis reads every check on the hinge bars rigid and elastic at their own section, the elastic
    bar's arm on free and on stiff bushes (xt_hinges `bar` `bounds` and `bushes`), and the elastic models tie each bar to
    its crossmember at each weld run's two ends and its centre."""
    assert set(RES["bars"]) == {"rigid", "elastic on free bushes", "elastic on stiff bushes"}
    assert RES["frame"] == RES["bars"]["rigid"]
    fm = CH.frame(None, "crossmember", "elastic", "free")
    for cm in CH.hinge_crossmembers():
        ys = [y for y, _ in fm.cm_nodes[cm.id]]
        assert all(any(abs(y - r) < 0.5 for y in ys) for r in CH.hinge_run_points(cm)), cm.id
    assert sum(1 for el in fm.f.elements if el.member.startswith("XT-BAR-")) > 0


def test_the_hinge_joints_weld_roots_are_read_in_fatigue():
    """Review I2-125: FAT-26 reads the roots of the hinge bars' weld runs and FAT-27 those of the cheeks' and fillers'
    welds in LC10, each throat stress split into its part normal to the weld's axis on IIW 414's FAT 36 and its part along
    it on Table 3.2-2 no. 2's FAT 80, combined by IIW's interaction, and both fail, since this build makes those welds."""
    import yaml
    from cad.chassis_fea import _miner, group_throat, root_damage, sn_range, weld_group
    from cad.partsdb import DATA
    lc10 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC10")
    assert sn_range(36, 3, 1e7, 1e7) == pytest.approx(21.1, abs=0.05)          # IIW-1823-07 Table 4.3-2's knee points
    assert sn_range(80, 5, 1e8, 1e8) == pytest.approx(36.6, abs=0.05)
    for s in (30.0, 60.0, 120.0):
        assert root_damage(s, 0.0, 36, 80, lc10["occasional_cycles"]) == pytest.approx(_miner(36, s, lc10), rel=1e-6)
    assert root_damage(15.0, 20.0, 36, 80, lc10["occasional_cycles"]) == 0.0
    assert root_damage(60.0, 60.0, 36, 80, 1e5) > root_damage(60.0, 0.0, 36, 80, 1e5)
    g = weld_group([(f"the {e} fillet", (x, -40.0, 0.0), (x, 40.0, 0.0), 4.2) for e, x in (("front", -25.0), ("rear", 25.0))])
    along = group_throat(g, (0.0, 1000.0, 0.0), (0.0, 0.0, 0.0))
    across = group_throat(g, (500.0, 0.0, 1000.0), (0.0, 0.0, 0.0))
    assert all(s == pytest.approx(0.0, abs=1e-9) and t == pytest.approx(1000 / (2 * 80 * 4.2)) for _, s, t in along)
    assert all(t == pytest.approx(0.0, abs=1e-9) and s == pytest.approx(math.hypot(500, 1000) / (2 * 80 * 4.2)) for _, s, t in across)
    checks = {c["id"]: c for c in yaml.safe_load((DATA / "checks.yaml").read_text())["trailer_checks"]}
    rows = {r["id"]: r for r in RES["fatigue"]}
    for fid in ("FAT-26", "FAT-27"):
        r = rows[fid]
        assert checks[fid]["severity"] == "fail" and "I2-125" in checks[fid]["why"]
        assert r["fat"] == 36 and r["fat_shear"] == 80 and not r["hot_spot"]
        assert r["cafl"] == pytest.approx(21.1, abs=0.05) and r["shear_cafl"] == pytest.approx(36.6, abs=0.05)
        assert r["range_mpa"] == pytest.approx(r["cafl"] * r["util"], rel=1e-9)
        assert r["util"] == pytest.approx(math.hypot(r["normal_mpa"] / r["cafl"], r["shear_mpa"] / r["shear_cafl"]), rel=1e-9)
        assert r["ok"] == (r["util"] <= 1 + 1e-9 and r["damage"] <= lc10["miner_limit"])
    assert " inboard, its " in rows["FAT-26"]["where"] and "cheek's" in rows["FAT-27"]["where"]
    assert rows["FAT-27"]["shear_mpa"] == 0.0


def test_the_webs_under_the_fillets_over_them_stretch_in_series_with_the_welds():
    """Review I2-125 and COMMON-RULES-26: a fillet over a web passes its run's force into the web's bottom edge, which the
    frame model's rigid links from the beam's axis do not stretch, so the web's own stretch stands in series with the
    weld's, from a plane-stress model of the web (cad/web_plane.py) that gives a strip's even stretch exactly, the data
    on its stiff bound with the soft one beside, and the frame model's weld points over the webs carry it."""
    from cad import web_plane as WP
    web = CH.data["xt_hinges"]["web"]
    b = CH.data["xt_hinges"]["bar"]
    assert WP.check_strip() == pytest.approx(1.0, abs=1e-6)
    cm = CH.hinge_crossmembers()[0]
    y_in = CH.V["rail_c"] - CH.role_sec["rail"].b / 2
    runs = [(u - b["run"] / 2, u + b["run"] / 2) for u in b["runs"]]
    h = cm.sec.d - cm.sec.t
    for edge in ("front", "rear"):
        t, fl = web["t"][edge], web["flange"][edge]
        assert [k / 1000 for k in WP.model(2 * y_in, h / 2, t, fl, runs, hold="both")] == pytest.approx(web["kn_mm"][edge], abs=0.051), edge
        assert [k / 1000 for k in WP.model(2 * y_in, h, t, fl, runs, hold="up")] == pytest.approx(web["other"]["kn_mm"][edge], abs=0.051), edge
        assert all(s < f for s, f in zip(web["other"]["kn_mm"][edge], web["kn_mm"][edge]))
    assert all(k < 0.7 * 200_000 * b["run"] / 1000 / 4 for k in web["kn_mm"]["rear"])      # the web, not the weld, sets the tie

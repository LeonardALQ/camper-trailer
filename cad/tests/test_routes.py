"""The services' routes (H28): data/routes.yaml resolved by cad/routes.py on the solved layout. Every SVC check passes,
every run ends on a real line at the points the data names, its length is at least the distance between its ends, its
bends are tangent arcs, and the services models (cad/routes_model.py) carry every run with its routing facts."""
from __future__ import annotations

import functools
import math

import pytest

from cad import routes as R
from cad import routes_model as M
from cad.tests.test_trailer import EV

LAY = EV["layout"]
RES = R.resolve(LAY)
EVAL = R.evaluate(RES)
ROWS = M.check_rows(RES, EVAL)


def test_every_check_is_defined_once_with_its_source():
    ids = [c["id"] for c in RES["data"]["checks"]]
    assert ids == [f"SVC-{i:02d}" for i in range(1, len(ids) + 1)] and len(ids) >= 8, ids
    assert {c["kind"] for c in RES["data"]["checks"]} == set(R.CHECKS)
    assert all(c.get("source") and c.get("why") for c in RES["data"]["checks"])


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_services_check(row):
    msg = f"{row['id']} {row['title']}: {row['detail']}"
    if row["severity"] == "report":
        if not row["ok"]:
            pytest.xfail("reported, not a build failure: " + msg)
        return
    assert row["ok"], msg


def test_limits_are_the_rules():
    """Never move a limit to make a check pass: these are the brief's and the standards' values."""
    r = RES["data"]["rules"]
    assert (r["clear_mm"], r["segregation_mm"], r["drop_pct"], r["drop_ac_pct"], r["fall"], r["terminal_face"]["mm"]) == (20, 50, 2.0, 5.0, 0.02, 300)
    assert set(r["terminal_face"]["exempt"]) == {"W-02", "F-10", "W-09"}   # the washer's two hoses and the drip tray's drain (I2-35), each sleeved
    assert all(x.get("sleeve") for x in RES["runs"] if x["id"] in r["terminal_face"]["exempt"])
    sp = r["spacing"]
    assert (sp["gap_mm"], sp["over_mm"], set(sp["touch"])) == (5, 25, {"ELV", "ac230"})
    assert sp["wet"]["fresh"]["ac230"] == 25   # IB 052/2015, cold water above ground
    assert (sp["wet"]["hot"], sp["wet"]["waste"]) == ({"ac230": 50, "ELV": 25}, {"ac230": 50, "ELV": 25})


def test_a_ways_pitch_is_its_largest_cable_or_pipe():
    """I2-13: a shared way's lane pitch is the largest outside diameter in it, so lane neighbours touch at most."""
    od = {r["id"]: r["od"] for r in RES["runs"]}
    assert RES["ways"], "no shared ways"
    for w, way in RES["ways"].items():
        assert way["runs"], w
        assert way["pitch_mm"] >= max(od[i] for i in way["runs"]) - 1e-6, w


def test_no_two_runs_overlap_outside_the_board_duct():
    """SVC-08's measure in one number: no pair of runs passes through another, wherever both are outside the board."""
    e = EVAL["spacing"]
    assert e["overlaps"] == 0, [p for p in e["problems"] if "overlapping" in p][:5]


def test_the_ute_feed_holds_its_drop_from_the_chargers_to_the_lynx():
    """I2-15 (a): SVC-06 adds the ute half (TW06, its `upstream`) to D-14's own drop at the design current."""
    d14 = next(r for r in RES["runs"] if r["id"] == "D-14")
    up = d14["upstream"]
    own = d14["size"] and RES["kinds"]["twin8"]["sizes"][d14["size"]]["mv_am"] * d14["amps"] * d14["length_m"] / 1000
    assert up["m"] == 7 and d14["amps"] == 32 and "TW06" in up["source"]
    assert d14["vd_v"] == pytest.approx(own + up["mv"] * d14["amps"] * up["m"] / 1000, abs=0.002)
    assert d14["vd_pct"] <= RES["data"]["rules"]["drop_pct"]


def test_every_frame_cell_is_inside_its_frame_and_clear_of_the_others():
    """I2-14: a transit frame's modules fit its packing, side by side, each named for the run that passes it."""
    by = {r["id"]: r for r in RES["runs"]}
    ranges = RES["svc"]["fittings"]["modules"]   # Roxtec's cable range for each RM module (I2-29)
    for g in RES["svc"]["glands"]:
        cells = g.get("cells") or {}
        boxes = []
        for rid, c in cells.items():
            dx, dy, m = c[:3]
            n = c[3] if len(c) > 3 else 1   # a pair's two cores in two modules side by side
            hx, hy = R.cell_half(c)
            assert rid in by and g["id"] in (by[rid].get("glands") or []), (g["id"], rid)
            # inside the packing, or one of its two parts either side of a wedge set inside the stack (I2-33)
            assert any(px0 - 1e-6 <= dx - hx and dx + hx <= px1 + 1e-6 and py0 - 1e-6 <= dy - hy and dy + hy <= py1 + 1e-6
                       for px0, py0, px1, py1 in R.frame_packing(dict(g, p=(0.0, 0.0)))), (g["id"], rid)
            assert n == (2 if by[rid]["kind"] == "pair" else 1), (g["id"], rid, "a pair takes a module for each core")
            core = by[rid]["od"] / n
            lo, hi = ranges[m]
            assert lo <= core <= hi, (g["id"], rid, f"{core:.1f} mm outside RM {m}'s {lo} to {hi} mm")
            boxes.append((rid, dx - hx, dy - hy, dx + hx, dy + hy))
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                assert a[3] <= b[1] + 1e-6 or b[3] <= a[1] + 1e-6 or a[4] <= b[2] + 1e-6 or b[4] <= a[2] + 1e-6, (g["id"], a[0], b[0])


def test_bd11s_routed_item_follows_the_routes_and_the_line_adds_to_its_total():
    """I2-19: BD-11's routed item is the routed runs' mass (bd11_routed_kg) above the three items they price, the
    allowance not yet given to a part is the rest, and the items add to the line's 63.5 kg."""
    import yaml
    items = yaml.safe_load((R.DATA / "assemblies" / "trailer.yaml").read_text(encoding="utf-8"))["items"]
    parts = next(it for it in items if it["id"] == "BD-11")["parts"]
    routed = round(R.totals(RES)["lines"]["BD-11"]["mass_kg"], 2)
    priced = sum(p["kg"] for p in parts if p["item"].startswith(("12 and 24 V wiring", "230 V wiring", "Fresh water pipework")))
    item = next(p for p in parts if p["item"].startswith("The routed runs priced here"))
    allow = next(p for p in parts if p["item"].startswith("Allowance not yet given"))
    assert priced == pytest.approx(25.0)
    assert item["kg"] == pytest.approx(routed - priced, abs=0.051), (item["kg"], routed)
    assert f"{routed:.1f} kg routed" in item["item"]
    assert allow["kg"] >= 0 and sum(p["kg"] for p in parts) == pytest.approx(63.5, abs=0.001)   # 53.6 kg until SVC-10, SVC-12 and the round TPS (I2-15 b, I2-18 a, I2-29), 61.0 until the cabinets' cleats and the under-floor conduits (I2-36)


def test_every_hole_in_a_chassis_member_and_every_large_floor_cut_out_is_listed():
    """I2-27: data/services.yaml lists every hole the runs make in a chassis member, at its place within 15 mm and its
    size and slot length within 1 and 2 mm, because CHS-10 reads its edge and toe distances from them, and every floor
    cut-out over 60 mm with its size, so a structural check can read them."""
    listed = RES["svc"]["holes"]
    got = R.member_holes(RES)
    same = lambda a, b: (a["member"], a["run"], a["face"]) == (b["member"], b["run"], b["face"])  # noqa: E731
    for h in got:
        assert any(same(h, x) and math.dist((h["x"], h["y"], h["z"]), (x["x"], x["y"], x["z"])) <= 15 and abs(h["d"] - x["d"]) <= 1
                   and abs(h["length"] - x["length"]) <= 2 for x in listed), h
    assert len(listed) == len(got), (len(listed), len(got))
    cuts = {c["gland"]: c for c in RES["svc"]["cutouts"]}
    for g in RES["svc"]["glands"]:
        if g["at"] == "floor":
            room = R.frame_room(RES["glands"][g["id"]]) if g.get("w") and g.get("h") else None   # its packing and the wedge's room (I2-33)
            w, h = (room[2] - room[0] + 8, room[3] - room[1] + 8) if room else (g["d"], g["d"])
            assert (max(w, h) > 60) == (g["id"] in cuts), g["id"]
            if g["id"] in cuts:
                c = cuts[g["id"]]
                assert (c["w"], c["h"]) == (w, h) and (c["x"], c["y"]) == ((room[0] + room[2]) / 2, (room[1] + room[3]) / 2), g["id"]
    # the kerb frame's three raiser cables stay in the raiser, clear of its seam with the rail (I2-27)
    assert not [h for h in got if h["run"] in ("B-16", "B-18", "D-14") and h["member"] == "RL-K"]


def test_svc01_tests_the_keep_clear_boxes_up_to_the_ceilings_services_zone():
    """I2-14: the aisles, landings and the chair space are obstacles to SVC-01 from the floor up, under the ceiling's
    services zone, so no run or riser stands in them."""
    kc = R.keep_clear_boxes(RES)
    top = RES["V"]["ceiling_z"] - RES["data"]["rules"]["keep_clear"]["overhead_mm"]
    assert len(kc) >= 5 and all(box[5] <= top + 1e-6 for _, box in kc)
    assert {b["id"] for b, _ in kc} >= {"LA-K1", "LA-K2", "LA-K4", "LA-K5"}
    assert not [p for p in EVAL["clearance"]["problems"] if "keep-clear" in p]


def test_every_gland_has_a_fitting_with_room_round_it():
    """I2-14: every gland's fitting is sized (a locknut by its thread, a frame by its packing and rim), and SVC-09 measures
    every pair in a panel on both faces."""
    fits = RES["svc"]["fittings"]
    for g in RES["svc"]["glands"]:
        f = R.fitting(g, fits)
        assert f["inner"] and f["outer"], g["id"]
        if g.get("cells"):
            x0, y0, x1, y1 = R.frame_room(dict(g, p=(0.0, 0.0)))   # the packing and the C wedge's room (I2-33)
            assert f["kind"] == "frame" and not f["turned"], g["id"]
            assert f["inner"]["hx"] == pytest.approx((x1 - x0) / 2 + fits["frame_rim_mm"]), g["id"]
            assert f["inner"]["hy"] == pytest.approx((y1 - y0) / 2 + fits["frame_rim_mm"]), g["id"]
    e = EVAL["glands"]
    assert e["ok"], e["problems"][:5]
    assert e["closest"] and all(c["gap"] >= c["need"] - 0.05 for c in e["closest"])


def test_svc05_finds_a_circuit_whose_runs_stop_short():
    """I2-18 (e): the runs of a tag join end to end, and a 230 V circuit runs from the board to its load or the outlet
    the load plugs into. Moving one end of a run breaks SVC-05."""
    assert R.coverage(RES)["ok"]

    def moved(rid, end, line):
        return [dict(r, **{end: dict(r[end], line=line)}) if r["id"] == rid else r for r in RES["runs"]]
    bad = R.coverage(dict(RES, runs=moved("C9B", "from", "PO-02")))["problems"]
    assert any(p.startswith("C9's runs do not join up") for p in bad), bad
    bad = R.coverage(dict(RES, runs=moved("C2", "to", "PO-08")))["problems"]
    assert any(p.startswith("C2's runs reach neither") for p in bad), bad
    bad = R.coverage(dict(RES, runs=moved("C5", "from", "LA-11E")))["problems"]
    assert any(p.startswith("C5's runs start from no source") for p in bad), bad


def test_ids_are_unique_and_every_end_is_a_real_line():
    ids = [r["id"] for r in RES["runs"]]
    assert len(ids) == len(set(ids))
    known = {b["iid"] for b in RES["blocks"]} | {b["id"] for b in RES["blocks"]} | set(RES["fixtures"])
    for r in RES["runs"]:
        for end in ("from", "to"):
            assert r[end]["line"] in known, f"{r['id']} {end} {r[end]['line']}"


def test_each_run_is_at_least_as_long_as_its_ends_are_apart():
    for r in RES["runs"]:
        p, q = r["points"][0], r["points"][-1]
        assert r["length_m"] * 1000 >= math.dist(p, q) - 6.0, r["id"]   # length_m is rounded to 10 mm
        assert r["length_m"] > 0 and r["mass_kg"] > 0, r["id"]


def test_bends_are_tangent_arcs_at_their_radius():
    for r in RES["runs"]:
        for c in r["corners"]:
            if c.get("t", 0) <= 1e-6:
                continue
            assert abs(math.dist(c["p0"], c["at"]) - c["t"]) < 0.01 and abs(math.dist(c["p1"], c["at"]) - c["t"]) < 0.01, r["id"]
            if not c.get("elbow") and not r["rigid"]:
                assert c["r"] >= r["bend_r"] - 0.5, f"{r['id']} bends at {c['r']:.0f} mm, needs {r['bend_r']:.0f} mm"


def test_dc_sizes_keep_the_drop_and_the_rating():
    for r in RES["runs"]:
        if r.get("vd_pct") is None:
            continue
        cap = RES["data"]["rules"]["drop_ac_pct"] if r["system"] == "ac230" else RES["data"]["rules"]["drop_pct"]
        assert r["vd_pct"] <= cap + 1e-6, f"{r['id']} {r['vd_pct']} %"
        assert r["amps"] <= r["rating_a"] + 1e-6, f"{r['id']} {r['amps']} A over {r['rating_a']} A"


def test_every_run_has_a_system_colour_and_a_model():
    systems = {s for m in M.MODELS.values() for s in m["systems"]}
    for r in RES["runs"]:
        assert r["system"] in M.SYSTEM_STYLE and r["system"] in systems, r["id"]


def test_the_part_card_has_every_routing_fact():
    m = M.meta_of(RES["runs"][0], RES, "CT-602")
    assert {"feeds", "ends", "kind", "cable", "size", "length_m", "protection", "circuit"} <= set(m["route"])
    assert m["iid"] == RES["runs"][0]["id"]


@pytest.mark.parametrize("rid", ["D-07", "C5", "F-09", "W-01", "K-08"])
def test_a_run_sweeps_to_one_valid_solid(rid):
    run = next(r for r in RES["runs"] if r["id"] == rid)
    s = M.run_solid(run)
    assert s.__class__.__name__ == "Solid", f"{rid} fell back to cylinders"
    area = math.pi * (run["od"] / 2) ** 2
    assert s.volume == pytest.approx(area * run["length_m"] * 1000, rel=0.03)


def test_the_priced_comparison_says_which_is_larger():
    for p in M.summary(RES, EVAL)["priced"]:
        assert p["larger"] == ("routed" if p["routed"] > p["quantity"] else "priced"), p


def test_the_new_checks_keep_their_limits():
    """I2-15 b and I2-18 a, c, d: VSB1's 600 mm, the 1 in 5 cone, SVC-08's heated-water distances and Table 22."""
    r = RES["data"]["rules"]
    assert (r["supports"]["max_mm"], r["supports"]["clip_mm"]) == (600, 30)
    assert r["terminal_face"]["cone"] == 0.2
    assert r["heat"]["lines"] == ["H-01"] and r["heat"]["line_mm"] == {"ELV": 25, "ac230": 50}
    g = r["ratings"]["groups"]
    assert (g["bunched"][6], g["layer"][2], g["light_pct"]) == (0.57, 0.85, 30)


def test_svc10_holds_each_fuse_between_its_current_and_the_cables_rating():
    """I2-15 b: D-07's 200 A MEGA sits between its 144 A and its 95 mm2 pair's rating in the board. On the old 50 mm2
    the fuse is over the cable's rating."""
    row = {x["run"]: x for x in EVAL["ratings"]["rows"]}
    d07 = row["D-07"]
    assert d07["ib"] <= d07["device"] <= d07["iz"], d07
    runs = [dict(r, size=50) if r["id"] == "D-07" else r for r in RES["runs"]]
    bad = R.ratings(dict(RES, runs=runs))["problems"]
    assert any(p.startswith("D-07's 200 A device is over") for p in bad), bad


def test_svc10_fails_a_loaded_cable_with_no_device_and_d06_has_its_fuse():
    """I2-31: D-06 carries the bank's 150 A under its own 200 A MEGA, within its pair's rating where it lies. A run with
    a design current and no device fails unless its line says why it cannot be overloaded, as D-06 did on the module
    fuses alone, and every DC rating in the table has a Tycab code or is marked an estimate."""
    row = {x["run"]: x for x in EVAL["ratings"]["rows"]}
    d06 = row["D-06"]
    assert d06["device"] == 200 and d06["ib"] <= d06["device"] <= d06["iz"], d06
    runs = [dict(r, protection="The module fuses and the BMS's contactor") if r["id"] == "D-06" else r for r in RES["runs"]]
    bad = R.ratings(dict(RES, runs=runs))["problems"]
    assert any(p.startswith("D-06 carries 150 A with no protective device") for p in bad), bad
    text = R.ROUTES.read_text(encoding="utf-8")
    block = text[text.index("      amps:\n        1.5:"):text.index("      pair: 0.8")]
    for line in block.splitlines()[1:]:
        assert "# FVK" in line or "# MBS" in line or "(est.)" in line, line


def test_svc11_finds_a_cable_beside_the_hot_line():
    """I2-18 d: a cable laid 10 mm over H-01 (and through its risers) is closer than SVC-08's 25 mm for heated water."""
    h01 = next(r for r in RES["runs"] if r["id"] == "H-01")
    b15 = next(r for r in RES["runs"] if r["id"] == "B-15")
    up = h01["od"] / 2 + b15["od"] / 2 + 10
    runs = [dict(r, dense=[(p[0], p[1], p[2] + up) for p in h01["dense"]], glands=[]) if r["id"] == "B-15" else r for r in RES["runs"]]
    bad = R.heat(dict(RES, runs=runs))["problems"]
    assert any(p.startswith("B-15 passes") and "from the hot line H-01" in p for p in bad), bad


def test_svc04s_cone_spares_a_line_over_the_tray_and_catches_one_under_it():
    """I2-18 c: a line straight over the terminal face is caught by the tray EL-09 above it, never below it."""
    tf = RES["data"]["rules"]["terminal_face"]
    face = RES["ns"][R.key(tf["line"])]
    tz, tb = R.tray_plane(RES)
    tray = RES["ns"][R.key(tf["tray"]["line"])]
    assert tray.box[2] >= RES["ns"]["LA_14F"].z1 - 0.5, "the tray stands on the machine base's deck, clear of its rails and cross members"
    f12 = next(r for r in RES["runs"] if r["id"] == "F-12")

    def at(z):
        line = dict(f12, dense=[(face.cx - 50, face.cy, z), (face.cx + 50, face.cy, z)])
        return R.drip_cone(dict(RES, runs=[line]))
    assert at(tz + f12["od"] / 2 + 20)["ok"]
    low = at((face.z1 + tz) / 2)
    assert not low["ok"] and low["problems"][0].startswith("F-12"), low


def test_svc12_finds_a_cable_left_hanging():
    """I2-18 a: without the raiser it is threaded through and the parts it is clipped to, K-09 hangs over 600 mm."""
    assert EVAL["supports"]["longest"] <= 600
    runs = [dict(r, along=[], inside=[]) if r["id"] == "K-09" else r for r in RES["runs"]]
    bad = R.supports(dict(RES, runs=runs))["problems"]
    assert any(p.startswith("K-09 lies") for p in bad), bad


def test_svc12_holds_a_cable_in_a_cabinet_only_by_a_panel_or_a_cleat_and_the_230v_only_in_its_conduit():
    """I2-36: a point deep inside a cabinet is held by nothing there, so B-11 without the bench's panels and cleats in
    its `along` hangs over 600 mm in the bench. Under the floor every 230 V cable lies inside a conduit listed under the
    floor (SVC-03 and SVC-08 count it as in its own enclosure there), and without those conduits C9B hangs."""
    fixtures = {k: f for k, f in RES["fixtures"].items() if k not in ("SP-KB", "SP-SK", "SP-SP")}
    bad = R.supports(dict(RES, fixtures=fixtures))["problems"]
    assert any(p.startswith("B-11 lies") for p in bad), bad
    V, ns = RES["V"], RES["ns"]
    under = [tuple(R._eval(v, ns) for v in z["box"]) for z in RES["data"]["rules"]["conduit"] if z.get("under")]
    for r in RES["runs"]:
        if r["system"] != "ac230":
            continue
        for p, _ in R._samples(r["dense"], 10.0):
            if p[2] < V["floor_underside_z"]:
                assert any(R._in_box(p, z, 0.0) for z in under), (r["id"], p)
    rules = dict(RES["data"]["rules"], conduit=[z for z in RES["data"]["rules"]["conduit"] if not z.get("under")])
    bad = R.supports(dict(RES, data=dict(RES["data"], rules=rules)))["problems"]
    assert any(p.startswith("C9B lies") for p in bad), bad


def test_k08_and_k09_pass_into_the_outriggers_clear_of_the_seams():
    """I2-27: the marker lamps' looms cross no seam. They enter each raiser through its inner face well above its seam
    with the rail, and leave it into the outrigger OR-05 through the middle of the outrigger's end."""
    boxes = {b["id"]: b["box"] for b in RES["blocks"] if b.get("box")}
    for h in R.member_holes(RES):
        if h["run"] not in ("K-08", "K-09"):
            continue
        assert h["face"] not in ("top", "bottom"), h
        if h["member"].startswith("RS-"):
            seam = boxes[h["member"]][2]
            assert h["z"] - h["d"] / 2 - seam >= 20, h
        if h["member"].startswith("OR-05") and abs(abs(h["y"]) - 638) < 1:
            x0, _, z0, x1, _, _ = boxes[h["member"]]
            assert min(h["x"] - h["length"] / 2 - x0, x1 - h["x"] - h["length"] / 2) >= 10, h
            assert h["z"] - h["d"] / 2 - z0 >= 20, h


def test_the_trap_valve_lies_along_the_wet_face_at_its_real_size():
    """I2-52: TV-09 is the HepvO 32 mm with its knuckle adaptor, its outlet bend and hose tail, lying along the wet face
    (its long side across the trailer), at least Wavin's 181 mm valve and 64 mm inlet nut, clear of the partition, and
    W-09 runs through it along that face and falls all the way."""
    tv = RES["fixtures"]["TV-09"]["box"]
    wet = RES["V"]["wet_x0"]
    assert tv[4] - tv[1] >= 181 + 69 and min(tv[3] - tv[0], tv[5] - tv[2]) >= 64, tv
    assert tv[0] >= wet, (tv, wet)
    w09 = next(r for r in RES["runs"] if r["id"] == "W-09")
    along = [(a, b) for a, b in zip(w09["points"], w09["points"][1:]) if abs(b[1] - a[1]) > 200]
    assert along and all(tv[0] <= a[0] <= tv[3] and b[2] < a[2] for a, b in along), w09["points"]


def test_the_brake_supply_counts_its_lead_and_the_leads_ride():
    """I2-50, I2-61: K-10's drop includes the SB50's lead K-14 ahead of it (`follows`) and the TSC's fuse in the drawbar
    junction (`inline`) within the 2 %, the two leads between the vehicles ride there, and every drum lead's arm part
    rides its arm and joins its sprung part at its clip."""
    by = {r["id"]: r for r in RES["runs"]}
    k10, k14 = by["K-10"], by["K-14"]
    mv = lambda r: RES["kinds"][r["kind"]]["sizes"][r["size"]]["mv_am"]  # noqa: E731
    fuse = sum(p["mohm"] for p in k10["inline"]) * k10["amps"] / 1000
    assert fuse > 0.03, "the TSC's fuse is in K-10's drop"
    want = (mv(k10) * k10["length_m"] + mv(k14) * k14["length_m"]) * k10["amps"] / 1000 + fuse
    assert k10["follows"] == ["K-14"] and k10["vd_v"] == pytest.approx(want, abs=0.002)
    assert k10["vd_pct"] <= RES["data"]["rules"]["drop_pct"]
    assert k10["protection"].startswith("30 A MIDI fuse in the drawbar junction") and R.device_of(k10, RES["data"]["rules"]["ratings"])[0] <= 40
    assert by["K-13"]["rides"] == by["K-14"]["rides"] == "between"
    arms = [r for r in RES["runs"] if r.get("rides") == "arm"]
    assert len(arms) == 4
    for r in arms:
        sprung = by[r["joins"]]
        assert math.dist(r["points"][0], sprung["points"][-1]) < 1.0, r["id"]
        assert r["vd_pct"] <= RES["data"]["rules"]["drop_pct"], r["id"]


def test_svc06_holds_the_tsc_at_its_floor():
    """I2-62: SVC-06 tests the TSC's 10.5 V (est.) as a floor from the battery's 12.0 V, and fails a supply under it."""
    import copy
    feed = EVAL["drops"]["feeds"][0]
    assert feed["floor_v"] == 10.5 and feed["volts_at_load"] >= feed["floor_v"]
    res = dict(data=RES["data"], runs=copy.deepcopy(RES["runs"]))
    k14 = next(r for r in res["runs"] if r["id"] == "K-14")
    k14["feed"]["floor_v"] = feed["volts_at_load"] + 0.05
    worse = R.drops(res)
    assert not worse["ok"] and any("under its" in p for p in worse["problems"]), worse["problems"]


@functools.lru_cache(maxsize=1)
def _reach_rows():
    import yaml
    ute = yaml.safe_load((R.DATA / "ute" / "ute.yaml").read_text())["params"]
    return {x["run"]: x for x in R.between_reach(RES, ball_drop=float(ute["coupling_tol"]))}


def test_the_leads_are_cut_to_their_spans_and_no_turn_pulls_them_taut():
    """I2-63, I2-78: each lead between the vehicles is clamped on the leads' bracket ahead of the stone guard and held
    up by its sprung arm. Its cut is its span from the plug to the strap on the arm's seat, from the strap to the clamp
    and its path to the junction, and with rules.between's margin taken off no turn or pitch pulls its span taut at
    either ball height. Straight ahead it hangs over the coupling's 380 mm, as drawn and where the arm holds it."""
    rows = _reach_rows()
    assert set(rows) == {"K-13", "K-14"}
    guard = next(b["box"] for b in RES["blocks"] if b["id"] == "DB-04")
    plate = next(b["box"] for b in RES["blocks"] if b["id"] == "CH-P01")
    for r in RES["runs"]:
        if r["id"] not in rows:
            continue
        i = next(j for j, q in enumerate(r["points"]) if math.dist(q, r["clamp"]) < 1e-6)
        fixed = R.fillet(r["points"][i:], r["bend_r"])["length"]
        assert r["lift"]["clip_mm"] + r["lift"]["rest_mm"] + fixed == pytest.approx(1000 * r["cut_m"], abs=1.0)
        x = rows[r["id"]]
        assert x["taut"] == 0 and x["low_ball"]["taut"] == 0, x
        assert x["low_mm"] > 380.0 and x["straight"]["low_mm"] > 380.0, x
        assert plate[3] < r["clamp"][0] < guard[0], "the clamp stands behind the coupling plate and ahead of the stone guard"
        assert r["clamp"][2] + r["od"] / 2 <= guard[2] - 20.0, "and keeps SVC-01's 20 mm under the stone guard"


def test_the_leads_hang_clear_of_dim06_in_any_turn_at_both_ball_heights():
    """I2-70, I2-78: in any turn and pitch of rules.between, at the design's coupling height and with the truck's ball
    at UTE-13's low end, each lead between the vehicles hangs at least DIM-06's 200 mm up where its sprung arm holds
    it, which DIM-08 holds it to, and pulls its plug with under half the SB50's 44 N (10 lbf) disconnect force. Its seat
    runs far enough round the arm's tip that the lead leaves it at a kink only where its span hangs slack (I2-83)."""
    import yaml
    checks = {c["id"]: c for c in yaml.safe_load((R.DATA / "checks.yaml").read_text())["trailer_checks"]}
    assert checks["DIM-08"]["min"] == checks["DIM-06"]["min"]
    for x in _reach_rows().values():
        assert x["turn_model"] == "held up by its sprung arm"
        assert x["low_ball"]["turn_low_mm"] < x["turn_low_mm"], x
        assert x["low_ball"]["turn_low_mm"] >= checks["DIM-08"]["min"], f"{x['run']} hangs to {x['low_ball']['turn_low_mm']} mm"
        assert max(x["pull_n"], x["low_ball"]["pull_n"]) < 22.0
        for y in (x, x["low_ball"]):
            assert y["kink_deg"] < 1.0 or y["kink_pull_n"] < 1.0, y


def test_dim08_reads_every_part_of_each_lead():
    """I2-91: DIM-08 reads the lowest point of every part of each lead, not only its plug. K-13 turned 70 degrees with
    the truck 20 degrees nose up relative to the trailer, at the design ball, hangs lowest in its span from the plug,
    whose catenary's vertex lies between its ends more than 30 mm under the plug, and the least in any turn is no
    higher than that sag or than the run from the clamp along the drawbar. The seat stops short of its bottom at every
    place of the arm, so the lead's wrap on it never hangs under the ends of the two spans."""
    V = RES["V"]
    r = next(x for x in RES["runs"] if x["id"] == "K-13")
    lift, w, od = r["lift"], r["kg_m"] * 9.81 / 1000.0, r["od"]
    P0, A, O = R._lift_ends(r, r["points"], V, 0.0)
    P = R._turn(P0, (0.0, 0.0, float(V["coupling_z"])), -70, 20)
    x = R.lift_rest(P, A, O, lift, w, float(lift.get("seat_mm", r["bend_r"])))
    c = x["c1"]
    assert x["low_part"] == "the plug's span" and 0.0 < c["x0"] < c["h"] and c["low"] < P[2] - 30.0, x["low_part"]
    row = _reach_rows()["K-13"]
    assert row["under_plug"]["n"] > 0 and "the plug's span" in row["under_plug"]["spans"]
    assert row["turn_low_mm"] <= min(x["low"] - od / 2, row["run_low_mm"])
    for q in RES["runs"]:
        if q.get("lift"):
            lf = q["lift"]
            assert lf["deg"][0] - lf["strap_deg"] + lf["seat_deg"][0] > -180.0 and lf["deg"][1] - lf["strap_deg"] + lf["seat_deg"][1] < 180.0


def test_tr13_reads_the_model_on_its_ramps_as_the_test_does():
    """I2-91: TR-13's ramps stand the truck nose down by asin(300 / 3,270), its ball rising 300 x (3,270 + 1,455) /
    3,270 = 433.5 mm, and the trailer nose up by asin(433.5 / the axle group's X), each vehicle at its own attitude as
    the trailer swings round. The truck's plug then stands where the truck's own pitch puts it at every lock, so K-14's
    reading, at its plug, is worked by hand from the plug's place ahead of and above the pin. TR-13's estimate is the
    model's least over every lock, its source names the lead it comes from and its procedure names the ramps' height."""
    import yaml
    ute = yaml.safe_load((R.DATA / "ute" / "ute.yaml").read_text())["params"]
    wb, bb, V = float(ute["wheelbase"]), float(ute["ball_behind_axle"]), RES["V"]
    x = R.on_ramps(RES, wb, bb)
    a = math.asin(300.0 / wb)
    rise = 300.0 * (wb + bb) / wb
    b = math.asin(rise / V["axle_x"])
    assert x["truck_deg"] == pytest.approx(math.degrees(a), abs=0.01) and x["rise_mm"] == pytest.approx(rise, abs=0.1)
    assert x["trailer_deg"] == pytest.approx(math.degrees(b), abs=0.01)
    r = next(q for q in RES["runs"] if q["id"] == "K-14")
    plug = r["points"][0]
    up = (plug[2] - V["coupling_z"]) * math.cos(a) + plug[0] * math.sin(a)
    under = next(q["box"][2] for q in RES["blocks"] if q["id"] == "DB-03")
    hand = up - r["od"] / 2 + (V["coupling_z"] - under) / math.cos(b) + under
    assert x["leads"]["K-14"]["part"] == "the plug" and x["leads"]["K-14"]["least_mm"] == pytest.approx(hand, abs=0.1)
    tr13 = next(m for m in yaml.safe_load((R.DATA / "measurements.yaml").read_text())["inputs"] if m["id"] == "TR-13")
    assert tr13["estimate"]["v"] == pytest.approx(x["least_mm"], abs=0.05) and x["run"] in tr13["estimate"]["src"]
    assert f"ramps {x['ramp_mm']:.0f} mm high" in tr13["how"]


def test_each_seat_is_joined_to_its_arm_by_its_web():
    """I2-91: each arm's seat is held on its arm by its web (cad/routes.py seat_parts, CT-601's detail). Every spoke's
    sides run from the hub's edge out to the channel's base, both bolts stand on the arm's centreline inside the hub at
    least two diameters from the tip and from the hub's back edge, and the seat's mass, which the model takes at the
    arm's tip, agrees within 3 % with a hand sum: the channel and its lining as strips of their developed widths round
    the base's radius, the web as the hub and three strips, and the bolts, rivets and strap."""
    sd = RES["data"]["rules"]["between"]["seat"]
    h, L = sd["hub"]
    for r in (x for x in RES["runs"] if x.get("lift")):
        s, lift, od = r["seat"], r["lift"], r["od"]
        assert lift["seat_kg"] == s["kg"]
        fa = math.radians(90.0 + lift["strap_deg"])
        a, n = (math.sin(fa), math.cos(fa)), (math.cos(fa), -math.sin(fa))
        for p0, p1 in s["spokes"]:
            u, v = p0[0] * a[0] + p0[1] * a[1], p0[0] * n[0] + p0[1] * n[1]
            assert (u <= 0.2 and math.hypot(*p0) <= h + 0.2) or (abs(v) <= h + 0.2 and -0.2 <= u <= L), (r["id"], p0)
            assert math.hypot(*p1) == pytest.approx(s["r0"], abs=1e-6)
        for b, q in zip(sd["bolts_mm"], s["bolts"]):
            assert q[0] * n[0] + q[1] * n[1] == pytest.approx(0.0, abs=1e-9) and 10.0 <= b <= L - 10.0
        base = float(lift.get("seat_mm", r["bend_r"])) - od / 2 - sd["lining_t"]
        span = math.radians(lift["seat_deg"][1] - lift["seat_deg"][0])
        channel = sd["channel_t"] * (2 * od + 2 * sd["lining_t"] + 2 * sd["channel_t"]) * base * span * 2.68e-6
        lining = sd["lining_t"] * 2 * od * base * span * 1.3e-6
        web = sd["web_t"] * (math.pi * h * h / 2 + 2 * h * L + 3 * sd["spoke_w"] * (base - sd["channel_t"] - h + sd["spoke_w"])) * 2.68e-6
        fixings = 2 * sd["kg"]["bolt"] + 6 * sd["kg"]["rivet"] + sd["kg"]["strap"]
        assert s["kg"] == pytest.approx(channel + lining + web + fixings, rel=0.03), (r["id"], s["kg_by"])


def test_the_catenary_against_the_parabola_worked_by_hand():
    """I2-78: level supports 1,000 mm apart with 1,020 mm of lead. By hand the parabola gives s - c = 8 d^2 / (3 c),
    so a sag d of 86.6 mm, a = H / w = c^2 / (8 d) = 1,443 mm and a pull at each support of w (a + d), the weight of
    1,530 mm of lead. The catenary agrees within 1 %, and its pull is its horizontal pull plus the weight under it."""
    c = R.catenary((0.0, 0.0, 0.0), (1000.0, 0.0, 0.0), 1020.0)
    assert c["a"] == pytest.approx(1443.0, rel=0.01)
    assert c["y_p"] - c["a"] == pytest.approx(86.6, rel=0.01) and -c["low"] == pytest.approx(86.6, rel=0.01)
    assert c["y_p"] == pytest.approx(1530.0, rel=0.01) and c["y_q"] == pytest.approx(c["y_p"])
    assert R.catenary((0.0, 0.0, 0.0), (1000.0, 0.0, 0.0), 999.0) is None


def test_the_strap_turns_with_the_seat_and_the_arm_balances_by_hand():
    """I2-83: the seat is fixed on the arm, so the strap stands at the seat's top when the arm stands at `strap_deg`
    and as far round towards the rear as the arm stands higher. Worked by hand for K-13 straight ahead at the design
    ball, where its plug's span hangs nearly straight: the spring's torque at the arm's angle, less the arm's weight and
    the clamp's span's moment about the hinge, over the plug's span's lever as a straight line, is that span's pull at
    the seat within 3 %, and its pull at the plug is that less the weight of the lead it rises by. Pulled straight, the
    plug's span holds the arm down, so the spring cannot lift it past the point where that span goes taut."""
    r = next(x for x in RES["runs"] if x["id"] == "K-13")
    lift, V = r["lift"], RES["V"]
    P, A, O = R._lift_ends(r, r["points"], V, 0.0)
    w = r["kg_m"] * 9.81 / 1000.0
    x = R.lift_rest(P, A, O, lift, w, float(lift.get("seat_mm", r["bend_r"])))
    turned = math.degrees(math.atan2(x["strap"][0] - x["C"][0], x["strap"][2] - x["C"][2]))
    assert turned == pytest.approx(x["deg"] - lift["strap_deg"], abs=1e-6)
    (d0, d1), (m0, m1) = lift["deg"], lift["torque_nmm"]
    spring = m1 + (m0 - m1) * (d1 - x["deg"]) / (d1 - d0)
    weight = 9.81 * (lift["arm_kg"] / 2 + lift["seat_kg"]) * lift["arm_mm"] * math.cos(math.radians(x["deg"]))
    F2 = R._cat_pull(x["T2"], A, x["c2"], w, "p")
    clamp = F2[0] * (x["T2"][2] - O[2]) - F2[2] * (x["T2"][0] - O[0])
    u = R._unit(R._sub(P, x["T1"]))[0]
    lever = u[0] * (x["T1"][2] - O[2]) - u[2] * (x["T1"][0] - O[0])
    assert lever < -100.0, "the plug's span pulled straight holds the arm down"
    at_seat = w * x["c1"]["y_q"]
    assert (spring - weight + clamp) / -lever == pytest.approx(at_seat, rel=0.03), (spring, weight, clamp, lever, at_seat)
    assert x["pull_n"] == pytest.approx(at_seat - w * (x["T1"][2] - P[2]), rel=1e-6)


def test_over_a_free_support_the_long_span_takes_the_slack_and_the_arm_holds_it_up():
    """I2-78, the old friction band's order reversed: each side's pull at a support is its horizontal pull plus the
    weight under it, so over a free support a long span from the plug takes the slack from a short bight and hangs
    deeper than it, where the band took the side with more slack to pull less. And K-14 with its arm's spring taken
    away, the arm on its bottom stop, hangs over 100 mm lower in the tightest turn than with it."""
    S, P, J, total = (0.0, 0.0, 0.0), (-700.0, 0.0, -100.0), (270.0, 0.0, -20.0), 1300.0

    def pulls(s):
        a, b = R.catenary(P, S, s), R.catenary(S, J, total - s)
        return None if a is None or b is None else (a["y_q"] - b["y_p"], a, b)

    lo, hi = math.dist(P, S) + 1.0, total - math.dist(S, J) - 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if pulls(mid)[0] > 0 else (lo, mid)
    _, span, bight = pulls((lo + hi) / 2)
    assert span["low"] < bight["low"] - 100.0, (span["low"], bight["low"])
    import copy
    r = next(x for x in RES["runs"] if x["id"] == "K-14")
    rule, V = RES["data"]["rules"]["between"], RES["V"]
    held = R.lifted(r, rule, V)["turn_low_mm"]
    weak = copy.deepcopy(r)
    weak["lift"]["torque_nmm"] = [0.0, 0.0]
    limp = R.lifted(weak, rule, V)["turn_low_mm"]
    assert limp < held - 100.0 and held >= 200.0, (limp, held)


def test_the_drum_leads_arm_parts_clear_fit05():
    """I2-50: FIT-05 sweeps the drum leads' arm parts with the arms and they keep its 50 mm."""
    from cad.tests.test_trailer import TRAILER
    t = TRAILER.tyre_arc(LAY)
    assert t["lead_gap_mm"] is not None and t["lead_gap_mm"] >= 50.0, t["detail"]


def test_d14_runs_between_the_jockey_spacer_tubes():
    """I2-53: the routes take DB-08 as its four tubes, and D-14 runs level between their rows beside the jockey."""
    tubes = [b for b in RES["blocks"] if b["id"] == "DB-08"]
    assert len(tubes) == 4
    d14 = next(r for r in RES["runs"] if r["id"] == "D-14")
    near = [p for p, _ in R._samples(d14["dense"], 10.0) if 880 <= p[0] <= 1120]
    rows = sorted({round(b["box"][2]) for b in tubes})
    assert near and all(rows[0] + 25 + d14["od"] / 2 <= p[2] <= rows[1] - d14["od"] / 2 for p in near), (rows, near[:3])

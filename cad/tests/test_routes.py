"""The services' routes (H28): data/routes.yaml resolved by cad/routes.py on the solved layout. Every SVC check passes,
every run ends on a real line at the points the data names, its length is at least the distance between its ends, its
bends are tangent arcs, and the services models (cad/routes_model.py) carry every run with its routing facts."""
from __future__ import annotations

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
    assert ids == [f"SVC-0{i}" for i in range(1, 8)], ids
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
    assert set(r["terminal_face"]["exempt"]) == {"W-02", "F-10"}


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
        assert r["length_m"] * 1000 >= math.dist(p, q) - 1.0, r["id"]
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


def test_the_priced_comparison_and_the_raised_loom():
    data = M.summary(RES, EVAL)
    loom = next(p for p in data["priced"] if p["line"] == "LGT-01")
    assert loom["routed"] <= loom["quantity"], "LGT-01's loom is shorter than the routed 7-core: raise it"

"""Ute checks from data/ute/ute.yaml (cad/ute.py) and the bike garage checks (cad/ute_garage.py,
data/ute/garage-checks.yaml). A `fail` check that misses its limit fails the test, and a `report` check is marked
xfail when it misses. Every mass line carries a source and a maturity."""
import pytest

from cad.ute import Ute

try:
    from cad.ute_garage import build_garage
    GARAGE, GMODEL = build_garage()
except ImportError:
    GARAGE, GMODEL = None, None

UTE = Ute(GARAGE)
RESULTS = UTE.checks()
GARAGE_RESULTS = GARAGE["checks"] if GARAGE else []


def _check(row, msg):
    if row["severity"] == "report":
        if not row["ok"]:
            pytest.xfail("reported, not a build failure: " + msg)
        return
    assert row["ok"], msg


@pytest.mark.parametrize("row", RESULTS, ids=[r["id"] for r in RESULTS])
def test_ute_check(row):
    _check(row, f"{row['id']} {row['title']}: {row['detail']}")


@pytest.mark.parametrize("row", GARAGE_RESULTS, ids=[r["id"] + (f"-{r['sub'][:12]}" if r["sub"] else "") for r in GARAGE_RESULTS])
def test_garage_check(row):
    _check(row, f"{row['id']} {row['title']}: {row['detail']}")


def test_every_line_has_a_source():
    for ln in UTE.lines:
        assert ln["source"] and ln["maturity"] in ("spec", "calculated", "estimate"), f"{ln['id']} has no mass source"


def test_axle_loads_add_up():
    for c in UTE.cases():
        n = c["nominal"]
        assert abs(n["front_kg"] + n["rear_kg"] - n["mass_kg"]) < 1e-6


def test_garage_replaces_the_block():
    if not GARAGE:
        pytest.skip("no garage module")
    ids = {ln["id"] for ln in UTE.lines}
    assert "UT-08" not in ids and "UT-09" not in ids and "UT-07" not in ids
    assert {"UB-TU", "UB-ST", "U-TOOLS"} <= ids

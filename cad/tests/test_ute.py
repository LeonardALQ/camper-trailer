"""Ute checks from data/ute/ute.yaml (cad/ute.py). A `fail` check that misses its limit fails the test, and a
`report` check is marked xfail when it misses. Every mass line carries a source and a maturity."""
import pytest

from cad.ute import Ute

try:
    from cad.ute_garage import build_garage
    GARAGE, GMODEL = build_garage()
except ImportError:
    GARAGE, GMODEL = None, None

UTE = Ute(GARAGE)
RESULTS = UTE.checks()


@pytest.mark.parametrize("row", RESULTS, ids=[r["id"] for r in RESULTS])
def test_ute_check(row):
    msg = f"{row['id']} {row['title']}: {row['detail']}"
    if row["severity"] == "report":
        if not row["ok"]:
            pytest.xfail("reported, not a build failure: " + msg)
        return
    assert row["ok"], msg


def test_every_line_has_a_source():
    for ln in UTE.lines:
        assert ln["source"] and ln["maturity"] in ("spec", "calculated", "estimate"), f"{ln['id']} has no mass source"


def test_axle_loads_add_up():
    for c in UTE.cases():
        n = c["nominal"]
        assert abs(n["front_kg"] + n["rear_kg"] - n["mass_kg"]) < 1e-6

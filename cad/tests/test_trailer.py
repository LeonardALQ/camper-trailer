"""Whole-trailer checks from data/checks.yaml (trailer_checks), measured on the block layout (cad/trailer.py).

A `fail` check that misses its limit fails the test. A `report` check is marked xfail when it misses, as for
the module checks. The module's ramp drop must match the trailer's garage floor height.
"""
import pytest

from cad.tests.test_checks import MODEL, PRJ
from cad.trailer import ModuleInfo, Trailer

TRAILER = Trailer(PRJ, ModuleInfo.from_model(PRJ, MODEL))
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


def test_ramp_drop_matches_floor_height():
    floor = EV["layout"].V["floor_z"]
    drop = PRJ.P.values["ground_drop"]
    assert abs(floor - drop) <= 1.0, f"garage-bed ground_drop {drop} mm, trailer garage floor {floor:.1f} mm"


def test_every_aboard_line_has_a_source():
    for case in TRAILER.cases:
        for b, m in EV["layout"].case_lines(case):
            assert b.source and b.maturity in ("spec", "calculated", "estimate"), f"{b.iid} has no mass source"

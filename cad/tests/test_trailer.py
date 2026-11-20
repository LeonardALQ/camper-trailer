"""Whole-trailer checks from data/checks.yaml (trailer_checks), measured on the block layout (cad/trailer.py).

A `fail` check that misses its limit fails the test. A `report` check is marked xfail when it misses. The trailer is
the LandCruiser 79's (report 18, layout 1): it reads the ute's model from build/ute/ute.json, so the ute builds first.
"""
import pytest

from cad.trailer import Trailer

TRAILER = Trailer()
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


def test_every_aboard_line_has_a_source():
    for case in TRAILER.cases:
        for b, m in EV["layout"].case_lines(case):
            assert b.source and b.maturity in ("spec", "calculated", "estimate"), f"{b.iid} has no mass source"


def test_no_petrol_inside_the_body():
    """Decision log 12:45: the generator and the jerry cans ride in the drawbar box, outside the body."""
    lay = EV["layout"]
    V = lay.V
    for iid in ("GS-01", "GS-04"):
        b = lay.find(iid)
        assert b.box[3] < V["body_x0"], f"{iid} is inside the body"


def test_the_coupling_matches_the_ute():
    """The trailer's coupling point and the ute's ball are the same measurement (measurements.yaml UTE-01)."""
    from cad.ute import Ute
    assert EV["layout"].V["coupling_z"] == Ute().V["coupling_z"]

"""Whole-trailer checks from data/checks.yaml (trailer_checks), measured on the block layout (cad/trailer.py).

A `fail` check that misses its limit fails the test. A `report` check is marked xfail when it misses. The trailer is
the home trailer for the LandCruiser 79 (revision J): it reads the ute's model from build/ute/ute.json, so the ute builds first.
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
            assert b.source and b.maturity in ("spec", "calculated", "estimate", "weighed"), f"{b.iid} has no mass source"


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


def test_the_ute_cases_carry_the_trailers_heaviest_towball():
    """The ute's towing cases carry at least the trailer's heaviest towball with growth, so the ute's rear axle, GVM and
    GCM checks never assume less than the trailer puts on the ball (decision H17). It reads the built ute model, which
    the trailer's checks use, and the ute as the code builds it now."""
    import json
    from cad.partsdb import ROOT
    from cad.ute import Ute
    heavy = max(EV["cases"], key=lambda c: c["growth"]["towball_kg"])
    ball = heavy["growth"]["towball_kg"]
    built = json.loads((ROOT / "build" / "ute" / "ute.json").read_text())["cases"]
    now = Ute().cases()
    for src, cases in (("build/ute/ute.json", built), ("cad/ute.py", now)):
        towing = [c for c in cases if c["growth"]["towball_kg"] > 0]
        assert towing, f"{src} has no towing case"
        for c in towing:
            for bs in ("nominal", "growth"):
                assert c[bs]["towball_kg"] >= ball - 1e-6, (
                    f"{src} {c['id']} ({bs}) carries {c[bs]['towball_kg']:.1f} kg on the ball, less than the trailer's "
                    f"{ball:.1f} kg ({heavy['id']} with growth)")

"""Measured inputs (data/measurements.yaml): every input says when it is measured and what range the design accepts,
with its source, and the value the design assumes sits inside that range."""
import re

import pytest
import yaml

from cad.inputs import Inputs
from cad.partsdb import DATA, ROOT, Project
from cad.tests.test_trailer import EV, TRAILER
from cad.trailer import BUILD_ORDER, WEIGHINGS, Trailer, _stage_of, measurement_refs

STAGES = {"buy", "build", "weigh", "trailer built"}
INPUTS = TRAILER.inputs
REFS = measurement_refs(TRAILER, EV)
RANGES = INPUTS.resolve_ranges(REFS)
MODEL_READINGS = {iid: REFS[f"model_{iid}"] for iid in WEIGHINGS}
ITEMS = list(INPUTS.items.values())
RAW = yaml.safe_load((DATA / "measurements.yaml").read_text())["inputs"]
# TRAILER.md's build order table, each stage's whole row by its id
BUILD_ROWS = {m.group(1): line for line in (ROOT / "TRAILER.md").read_text().splitlines() if (m := re.match(r"\| (B\d) ", line))}
PARTS = {"car": "Car build", "box": "Bike box", "trailer": None}


@pytest.mark.parametrize("it", ITEMS, ids=[i.id for i in ITEMS])
def test_input_has_a_stage_and_a_range(it):
    r = RANGES[it.id]
    assert it.stage in STAGES, f"{it.id}: stage {it.stage!r}"
    assert it.range and r["src"], f"{it.id} has no range with a source"
    n = len(it.estimate) if isinstance(it.estimate, list) else 1
    for side in ("min", "max"):
        if isinstance(r[side], list):
            assert len(r[side]) == n, f"{it.id}: {side} has {len(r[side])} entries for {n} values"
    lo, hi = r["min"], r["max"]
    for k in range(n):
        a = lo[k] if isinstance(lo, list) else lo
        b = hi[k] if isinstance(hi, list) else hi
        if a is not None and b is not None:
            assert a <= b, f"{it.id}: min {a} above max {b}"
    assert not any(Inputs.outside(it.estimate, r)), f"{it.id}: estimate {it.estimate} outside {lo} to {hi}"


def test_model_references_resolve():
    """The inputs whose range is set by the model get a number for it."""
    for iid in ("UTE-02", "UTE-03", "WHL-01", "SUP-01", "SUP-04", "TW-01", "TW-02", "TW-03", "TW-04", "TW-05", "TR-01"):
        r = RANGES[iid]
        assert r["min"] is not None, f"{iid}: the model gave no figure for its range"


def test_ids_are_unique():
    ids = [d["id"] for d in RAW]
    assert len(ids) == len(set(ids)), f"repeated ids: {sorted({i for i in ids if ids.count(i) > 1})}"


def test_every_input_belongs_to_a_part():
    """car, box or trailer, for the Measurements page's filter. Report 23's car inputs are in group Car build and report 24's box
    inputs in group Bike box."""
    for it in ITEMS:
        part = it.extra.get("part")
        assert part in PARTS, f"{it.id}: part {part!r}"
        for prefix, p in (("VEH-", "car"), ("BOX-", "box")):
            if it.id.startswith(prefix):
                assert part == p and it.group == PARTS[p], f"{it.id}: part {part}, group {it.group!r}"


def _tare(lay):
    return sum(b.mass_kg for b in lay.blocks if b.load == "tare")


def _weighed(readings):
    """The layout and the nominal load cases with these weighbridge readings entered, at the model's axle position."""
    prj = Project()
    for iid, kg in readings.items():
        prj.inputs.items[iid].measured = kg
    lay = Trailer(prj).layout(**EV["solved"]["overrides"])
    return lay, [lay.evaluate_case(c)["nominal"] for c in TRAILER.cases]


def test_every_tare_line_is_weighed_in_one_stage():
    covers = {iid: set(INPUTS.items[iid].extra["covers"]) for iid in WEIGHINGS}
    for b in EV["layout"].blocks:
        if b.load == "tare":
            stages = [iid for iid, c in covers.items() if _stage_of(b) in c]
            assert len(stages) == 1, f"{b.iid} ({_stage_of(b)}) is in {stages or 'no weighbridge stage'}"
    assert MODEL_READINGS["TW-03"] == pytest.approx(_tare(EV["layout"]), abs=0.1)


def test_weighing_at_the_model_changes_nothing():
    lay, cases = _weighed(MODEL_READINGS)
    assert _tare(lay) == pytest.approx(_tare(EV["layout"]), abs=0.1)
    for got, case in zip(cases, EV["cases"]):
        assert got["towball_kg"] == pytest.approx(case["nominal"]["towball_kg"], abs=0.1), case["id"]


def test_a_heavier_finished_trailer_raises_the_tare_by_the_difference():
    lay, _ = _weighed(MODEL_READINGS | {"TW-03": MODEL_READINGS["TW-03"] + 50})
    assert _tare(lay) == pytest.approx(_tare(EV["layout"]) + 50, abs=0.1)


def test_every_tare_line_is_fitted_at_one_stage_whose_row_names_it():
    """Each line goes to one stage of TRAILER.md's build order (data/assemblies/trailer.yaml build_order), and that
    stage's row of the table names it, so a weighing sees exactly what the builder has fitted by then."""
    seen = {}
    for s in BUILD_ORDER:
        for k, words in s["fits"].items():
            assert k not in seen, f"{k} is fitted at {seen[k]} and at {s['stage']}"
            seen[k] = s["stage"]
            assert words.lower() in BUILD_ROWS[s["stage"]].lower(), f"{s['stage']}'s row in TRAILER.md does not name {k} ({words!r})"
    for b in EV["layout"].blocks:
        if b.load == "tare" and b.mass_kg > 0:
            assert _stage_of(b) in BUILD_ROWS, f"{b.iid} ({b.system}) is fitted at no stage of the build order"


def test_each_weighing_covers_the_stages_since_the_one_before():
    """TW-01 to TW-03 cover every stage once, in build order, and the table weighs each at the end of the last stage it
    covers, before the next weighing's first stage starts."""
    order = [s["stage"] for s in BUILD_ORDER]
    covers = [INPUTS.items[iid].extra["covers"] for iid in WEIGHINGS]
    assert [st for c in covers for st in c] == order, f"the weighings cover {covers}, the build order is {order}"
    for k, iid in enumerate(WEIGHINGS):
        named = [st for st, row in BUILD_ROWS.items() if iid in row.split("|")[4]]
        nxt = covers[k + 1][0] if k + 1 < len(covers) else "B99"
        assert named and covers[k][-1] <= named[0] < nxt, f"{iid} covers {covers[k]} but the table weighs it at {named}"

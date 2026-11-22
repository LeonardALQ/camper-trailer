"""The floor plan cut from the 3D model (cad/floorplan.py, decision H28): both bed positions are drawn, every line inside
the body is named in each plan, the walls are cut at their real thickness, and the plan's dimensions are the layout's."""
import json
import re

import pytest

from cad.build import BUILD
from cad.tests.test_trailer import TRAILER

OUT = BUILD / "floorplan"
REP = json.loads((BUILD / "trailer" / "trailer.json").read_text())
DAY = TRAILER.layout(**REP["solved"]["overrides"])
NIGHT = TRAILER.layout(**{**REP["solved"]["overrides"], "bed_state": 1})
LAYOUTS = {"day": DAY, "night": NIGHT}


@pytest.fixture(scope="module")
def plans():
    """The build's plans (make trailer writes them), or the same plans made here when the build has none."""
    if not (OUT / "floorplan.json").exists():
        from cad.floorplan import write_plans
        write_plans(DAY, NIGHT, json.loads((BUILD / "body" / "body.json").read_text()), OUT)
    return json.loads((OUT / "floorplan.json").read_text())


def _svg_iids(state) -> set:
    return set(re.findall(r'data-iid="([^"]+)"', (OUT / f"floorplan-{state}.svg").read_text(encoding="utf-8")))


@pytest.mark.parametrize("state", ["day", "night"])
def test_the_plan_is_drawn_for_both_bed_positions(plans, state):
    svg = (OUT / f"floorplan-{state}.svg").read_text(encoding="utf-8")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>"), f"floorplan-{state}.svg is not an SVG"
    p = plans["plans"][state]
    assert p["cut_z"] == pytest.approx(DAY.V["floor_z"] + 1000.0), "the cut is not 1,000 mm above the floor"
    assert p["parts"] and p["walls"] and len(p["doors"]) == 3 and len(p["clear"]) == 6


@pytest.mark.parametrize("state", ["day", "night"])
def test_every_inside_line_is_named(plans, state):
    """Each block inside the body (its fit-out, the partition and the spaces kept clear) is a named part of the plan,
    and the doors and windows are named by their lines."""
    lay = LAYOUTS[state]
    inside = {b.iid for b in lay.blocks if b.zone == "inside" and b.box is not None}
    openings = {"BD-07", "BD-15", "WR-04", "WN-01", "WN-02", "WN-03", "WN-04"}
    named = _svg_iids(state)
    missing = sorted((inside | openings) - named)
    assert not missing, f"not named in the {state} plan: {missing}"
    names = {b.iid: b.name for b in lay.blocks}
    for q in plans["plans"][state]["parts"]:
        assert q["name"] == names.get(q["iid"], q["name"]), f"{q['iid']} carries another line's name"


@pytest.mark.parametrize("state", ["day", "night"])
def test_the_dimensions_are_the_layouts(plans, state):
    V, lay = DAY.V, LAYOUTS[state]
    d = plans["plans"][state]["dims"]
    k4, k5 = lay.find("LA-K4").box, lay.find("LA-K5").box
    want = dict(inside_length=V["in_x1"] - V["in_x0"], inside_width=2 * V["half_in"], bed=V["bed_x1"] - V["in_x0"],
                living=V["rear_x0"] - V["bed_x1"], rear=V["in_x1"] - V["rear_x0"], aisle=k4[4] - k4[1], walk_band=k5[4] - k5[1])
    assert d == pytest.approx(want), f"{state}: plan {d}, layout {want}"
    svg = (OUT / f"floorplan-{state}.svg").read_text(encoding="utf-8")
    for key, label in (("inside_length", "inside"), ("inside_width", "inside"), ("bed", "bed and desk"), ("living", "living"),
                       ("rear", "wet room"), ("aisle", "aisle"), ("walk_band", "walk band")):
        assert f">{want[key]:,.0f} {label}<" in svg, f"{state}: the figure {want[key]:,.0f} {label} is not on the plan"


def test_the_walls_are_cut_at_their_thickness(plans):
    V = DAY.V
    wr = DAY.find("WR-03").box
    for w in plans["plans"]["day"]["walls"]:
        across = 0 if w["id"] in ("BD-04", "WR-03") else 1            # end walls and the partition run across the trailer
        t = V["wall_t"] if w["id"] != "WR-03" else wr[3] - wr[0]
        assert w["cut"], f"{w['iid']} is not cut by the plane"
        for f in w["cut"]:
            span = max(pt[across] for pt in f[0]) - min(pt[across] for pt in f[0])
            assert span == pytest.approx(t, abs=0.5), f"{w['iid']} is cut {span:.1f} mm thick, the wall is {t:.0f} mm"


def test_the_bed_moves_between_the_plans(plans):
    """By day the bed is above the plane and dashed, at night the plane cuts the mattress and the desk is under it."""
    day = {q["iid"]: q for q in plans["plans"]["day"]["parts"]}
    night = {q["iid"]: q for q in plans["plans"]["night"]["parts"]}
    assert day["LB-01"]["kind"] == "above" and day["LB-03"]["kind"] == "above"
    assert night["LB-01"]["kind"] != "above" and night["LA-09"].get("under") in ("LB-01", "LB-02", "LB-03")
    assert day["LA-09"].get("under") is None

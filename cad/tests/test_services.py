"""The services' budgets (cad/services.py): every load of research report 20's model is in one energy group, the
groups add up to the model's daily totals, the autonomy figures meet decision H3, and the water budget is the one
TRAILER.md quotes."""
import re

import yaml

from cad.partsdb import ROOT
from cad.services import ENERGY_OUT, _cases, services

S = services()
CASES = _cases(ENERGY_OUT.read_text())
TRAILER = (ROOT / "TRAILER.md").read_text()


def test_the_model_output_has_four_cases():
    assert [c["id"] for c in CASES] == ["hot", "hot_diesel", "cold_diesel", "cold_hp"]
    for c in CASES:
        assert c["loads"] and c["total"], c["id"]


def test_every_load_is_in_one_group():
    groups = S["energy"]["groups"]
    for c in CASES:
        for lid in c["loads"]:
            hits = [g["group"] for g in groups if lid in g["ids"] or lid[:2] in g["ids"]]
            assert len(hits) == 1, f"{c['id']} {lid} is in {hits}"


def test_groups_add_up_to_the_model():
    for c in S["energy"]["cases"]:
        got = sum(g["kwh"][c["id"]] for g in S["energy"]["groups"])
        assert abs(got - c["total"]) <= 0.05, f"{c['id']}: groups {got:.2f} kWh, model {c['total']} kWh"


def test_autonomy_meets_h3_and_trailer_md_quotes_it():
    a = S["autonomy"]
    assert a["hours_new"] >= 24 and a["hours_end_of_life"] >= 12, a
    for v in (a["hours_new"], a["hours_end_of_life"]):
        assert f"{v:.1f} h" in TRAILER, f"TRAILER.md does not quote {v:.1f} h"
    hot = next(c for c in S["energy"]["cases"] if c["id"] == "hot")
    assert f"{hot['total']:.1f} kWh" in TRAILER


def test_water_budget_is_the_one_trailer_md_quotes():
    w = S["water"]
    assert f"so {w['fresh_l']} L, {w['grey_l']} L of it to grey" in TRAILER
    assert f"A wash adds {w['wash']['fresh_l']} L" in TRAILER
    for r in w["daily"]:
        assert r["fresh_l"] >= r["grey_l"] >= 0, r["use"]
    # the travel store is the trailer's travel water limit (H13, H21), so a change to it reaches the budget and TRAILER.md
    travel = yaml.safe_load((ROOT / "data/assemblies/trailer.yaml").read_text())["params"]["water_travel_l"]
    days = {d["litres"]: d["days"] for d in w["days"] if d["washes_a_week"] == 0}
    assert travel in days, f"data/services.yaml has no no-laundry store at the {travel} L travel limit"
    assert re.search(rf"The {travel} L aboard lasts about {round(days[travel])} days", TRAILER)

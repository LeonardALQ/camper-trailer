"""The bike box's priced parts list (data/ute/box-parts.yaml): its totals add up from its lines, and its mass is the
model's box mass, part for part, so UGB-01 and the parts list agree."""
from collections import defaultdict

import pytest
import yaml

from cad.partsdb import DATA
from cad.tests.test_ute import GARAGE, GMODEL

BOX = yaml.safe_load((DATA / "ute" / "box-parts.yaml").read_text())
LINES = BOX["lines"]
TOT = BOX["totals"]


def _names(ln):
    mp = ln.get("model_part")
    return [] if not mp else mp if isinstance(mp, list) else [mp]


def test_line_prices_are_qty_times_unit():
    for ln in LINES:
        p = ln["price"]
        if p.get("aud_each") is not None:
            assert abs(p["aud"] - ln["qty"] * p["aud_each"]) < 0.011, f"{ln['id']}: {p['aud']} is not {ln['qty']} x {p['aud_each']}"


def test_totals_add_up():
    by = defaultdict(float)
    for ln in LINES:
        by[ln["group"]] += ln["price"]["aud"]
    for g, v in TOT["by_group"].items():
        assert abs(by[g] - v) < 0.01, f"group {g}: lines {by[g]:.2f}, totals {v}"
    sub = sum(by.values())
    assert abs(sub - TOT["subtotal_aud"]) < 0.01
    cont = sub * TOT["contingency_pct"] / 100
    assert abs(cont - TOT["contingency_aud"]) < 0.01
    assert abs(sub + cont - TOT["total_aud"]) < 0.01
    assert abs(sum(ln["mass"]["kg"] for ln in LINES) - TOT["mass_kg_lines"]) < 0.01


def test_one_total_with_no_hired_labour_or_certification():
    """Leonard builds the box himself and does not certify it (decision H25), so the list has no labour or review line
    and one total."""
    assert not {"fabrication", "compliance"} & set(BOX["groups"]), "the box still has a labour or review group"
    assert not {"fabrication", "compliance"} & {ln["group"] for ln in LINES}
    assert "owner_built_total_aud" not in TOT, "the box has one total"


def test_every_line_with_mass_names_a_model_part():
    parts = GMODEL.prj.parts
    for ln in LINES:
        if ln["mass"]["kg"] > 0:
            assert _names(ln), f"{ln['id']} carries {ln['mass']['kg']} kg but names no model part"
        for n in _names(ln):
            assert n in parts, f"{ln['id']}: unknown model part {n}"


def test_list_mass_is_the_model_box():
    """Every box part in the model is on the list, and the two masses agree (UGB-01 checks the model's)."""
    if not GARAGE:
        pytest.skip("no garage module")
    box = {ln["id"]: ln["kg"] for ln in GARAGE["lines"] if ln["cases"] == ["UC1", "UC2", "UC3", "UC4"]}
    named = {n for ln in LINES for n in _names(ln)}
    assert not set(box) - named, f"model box parts not on the list: {sorted(set(box) - named)}"
    listed = sum(ln["mass"]["kg"] for ln in LINES)
    assert abs(listed - GARAGE["box_kg"]) <= 0.1, f"list {listed:.2f} kg, model {GARAGE['box_kg']:.2f} kg"

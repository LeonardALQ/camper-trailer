"""Lamps, reflectors and the number plate (cad/lamps.py, data/services.yaml `lamps`): every ADR 13/00 and VSB1 3.1 check
passes, the side devices sit on real outriggers, CT-003 has no open rows, and the parts list and TRAILER.md follow."""
from __future__ import annotations

import json

import pytest
import yaml

from cad.lamps import RULES, resolve
from cad.partsdb import DATA, ROOT
from cad.trailer_costs import parts_list

LM = resolve()
DATA_LAMPS = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8"))["lamps"]


@pytest.mark.parametrize("c", LM["checks"], ids=[c["id"] for c in LM["checks"]])
def test_lamp_check_passes(c):
    assert c["ok"], f"{c['id']} {c['what']}: {c['measured']} against {c['limit']}"


def test_every_function_has_a_rule_and_a_device():
    used = {f for d in DATA_LAMPS["devices"] for f in d["does"]}
    assert used <= set(RULES), f"no rule for {used - set(RULES)}"
    assert set(RULES) <= used, f"nothing fitted for {set(RULES) - used}"


def test_pairs_are_mirrored():
    for d in DATA_LAMPS["devices"]:
        mine = [i for i in LM["devices"] if i["dev"] == d["id"]]
        if d.get("single"):
            assert len(mine) == 1
            continue
        kerb = sorted(i["y"] for i in mine if i["side"] == "kerb")
        road = sorted(i["y"] for i in mine if i["side"] == "road")
        assert kerb and [-y for y in reversed(kerb)] == road, d["id"]


def test_side_devices_sit_on_outriggers():
    chs = json.loads((ROOT / "build" / "chassis" / "chassis.json").read_text(encoding="utf-8"))
    half = abs(next(i for i in LM["devices"] if i["face"] == "side")["y"])   # the body's side face
    for d in (d for d in DATA_LAMPS["devices"] if d["face"] == "side"):
        for st in d["stations"]:
            ors = [m for m in chs["members"] if m["role"] == "outrigger" and m["station"] == st]
            assert len(ors) == 2, f"{st} has no outrigger pair"
            assert all(abs(abs(m["p1"][1]) - half) < 1e-6 for m in ors), f"{st}'s outriggers stop short of the body edge"


def test_ct003_has_no_open_rows():
    src = (ROOT / "cad" / "drawings" / "home_sheets.py").read_text(encoding="utf-8")
    assert '("OPEN", "#b06000")' not in src
    assert "NOT DESIGNED YET. THEY GO ON THIS SHEET" not in src


def test_the_lamps_are_priced():
    lines = [ln for ln in parts_list()["lines"] if ln["group"] == "lamps"]
    assert [ln["id"] for ln in lines] == ["LGT-01"]
    assert lines[0]["price"]["aud"] > 0
    assert all(p.get("item") for p in lines[0]["parts"])


def test_trailer_md_quotes_the_lamps():
    text = (ROOT / "TRAILER.md").read_text(encoding="utf-8")
    assert f"its top at {LM['plate']['z1']:,.0f} mm" in text
    assert f"All {len(LM['checks'])} checks to ADR 13/00 and VSB1 3.1 pass" in text

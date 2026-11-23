"""I2-38: every live text that names the water the trailer tows with names `water_travel_l` (data/assemblies/trailer.yaml),
and the days it says the water lasts follow from it.

The live texts are the measurement sheet, the parts list, the load cases' other texts, TRAILER.md with its decision list (I2-56),
and the Trailer and Measurements pages. A sentence about an earlier plate or an earlier figure ("was", "before", "until",
"the 3,500 kg plate") is history and is left alone. Each load case's own text names that case's water instead: its fresh
water `water_l`, its grey water if it carries the grey tank, and the two together.
"""
import re

import pytest
import yaml

from cad.partsdb import ROOT

PARAMS = yaml.safe_load((ROOT / "data" / "assemblies" / "trailer.yaml").read_text(encoding="utf-8"))["params"]
TRAVEL = PARAMS["water_travel_l"]
WATER = {k: PARAMS[k] for k in ("water_travel_l", "water_highway_l", "grey_full_l")}
CASES = yaml.safe_load((ROOT / "data" / "load_cases.yaml").read_text(encoding="utf-8"))
NUM = r"(\d{1,3}(?:,\d{3})*|\d+)"
TOTAL = re.compile(NUM + r" L (?:of (?:fresh and grey )?water\b|aboard\b|in travel\b|in all\b|lasts\b)", re.I)
FRESH = re.compile(NUM + r" L of fresh water\b", re.I)
GREY = re.compile(NUM + r" L of grey water\b", re.I)
DAILY = re.compile(NUM + r" L a day\b", re.I)
LASTS = re.compile(NUM + r" L (?:aboard )?lasts about (\d+(?:\.\d+)?) days", re.I)
HISTORY = re.compile(r"\b(?:was|were|before|until|earlier)\b|3,500 kg plate|at 3,500 kg", re.I)
PAGES = ("site/src/content/docs/trailer.mdx", "site/src/content/docs/measurements.mdx", "site/src/components/Trailer.astro",
         "site/src/components/Measurements.astro")


def _strings(node, where):
    if isinstance(node, str):
        yield where, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, f"{where}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, f"{where}[{i}]")


def _live_texts():
    for name in ("measurements.yaml", "trailer-parts.yaml"):
        yield from _strings(yaml.safe_load((ROOT / "data" / name).read_text(encoding="utf-8")), name)
    yield from _strings({k: v for k, v in CASES.items() if k != "trailer_cases"}, "load_cases.yaml")
    for s in re.split(r"(?m)^## ", (ROOT / "TRAILER.md").read_text(encoding="utf-8")):
        yield f"TRAILER.md ## {s.splitlines()[0] if s else ''}", s
    for p in PAGES:
        if (ROOT / p).exists():
            yield p, (ROOT / p).read_text(encoding="utf-8")


def _sentences(text):
    return [s for s in re.split(r"(?<=[.;:])\s+|\n", text) if s.strip()]


def _n(s):
    return float(s.replace(",", ""))


LIVE = [(w, s) for w, t in _live_texts() for s in _sentences(t) if not HISTORY.search(s)]


def test_the_live_texts_are_found():
    assert len(LIVE) > 500
    assert sum(1 for _, s in LIVE if TOTAL.search(s)) >= 5, "too few live texts name the travel water"


@pytest.mark.parametrize("where,sentence", [(w, s) for w, s in LIVE if TOTAL.search(s) or FRESH.search(s) or LASTS.search(s)])
def test_a_travel_water_volume_is_water_travel_l(where, sentence):
    for m in TOTAL.finditer(sentence):
        assert _n(m.group(1)) == TRAVEL, f"{where}: '{sentence}' names {m.group(1)} L, the travel water is {TRAVEL:g} L"
    for f in FRESH.findall(sentence):
        assert _n(f) == TRAVEL, f"{where}: '{sentence}' names {f} L of fresh water, the travel water is {TRAVEL:g} L"
    daily = [_n(d) for d in DAILY.findall(sentence)]
    for v, days in LASTS.findall(sentence):
        if not daily:
            continue   # the daily use is in a sentence before it: the volume is tested above
        assert abs(float(days) - _n(v) / daily[-1]) <= 0.05 + 1e-9, (
            f"{where}: '{sentence}': {v} L at {daily[-1]:g} L a day lasts {_n(v) / daily[-1]:.2f} days, not {days}")


@pytest.mark.parametrize("case", CASES["trailer_cases"], ids=[c["id"] for c in CASES["trailer_cases"]])
def test_each_load_case_names_its_own_water(case):
    fresh = float(eval(str(case["water_l"]), {"__builtins__": {}}, WATER))
    grey = float(WATER["grey_full_l"]) if "grey" in case["load"] else 0.0
    text = case["aboard"]
    for f in FRESH.findall(text):
        assert _n(f) == fresh, f"{case['id']}: '{text}' names {f} L of fresh water, the case carries {fresh:g} L"
    for g in GREY.findall(text):
        assert _n(g) == grey, f"{case['id']}: '{text}' names {g} L of grey water, the case carries {grey:g} L"
    for m in TOTAL.finditer(text):
        assert _n(m.group(1)) == fresh + grey, f"{case['id']}: '{text}' names {m.group(1)} L, the case carries {fresh + grey:g} L"
    if fresh == TRAVEL or fresh + grey == TRAVEL and grey:
        assert FRESH.search(text) or TOTAL.search(text), f"{case['id']} carries the travel water, {TRAVEL:g} L, and its text names none"

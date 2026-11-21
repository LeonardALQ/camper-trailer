"""docs/decisions.md records every home trailer decision, H1 to H19 with H1a and H4a, each in an entry with its reason,
and keeps to the public text rules."""
from __future__ import annotations

import re

import pytest

from cad.partsdb import ROOT

TEXT = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
ENTRIES = [ln for ln in TEXT.splitlines() if ln.startswith("- ")]
IDS = [f"H{n}" for n in range(1, 20)] + ["H1a", "H4a"]


@pytest.mark.parametrize("h", IDS)
def test_every_h_decision_has_an_entry_with_its_reason(h):
    own = [e for e in ENTRIES if re.search(rf"[(, ]{h}[),]", e.split(":", 1)[0])]
    assert own, f"docs/decisions.md has no entry labelled {h}"
    assert any("Why:" in e for e in own), f"{h}'s entry gives no reason"


def test_entries_are_plain_text():
    assert "**" not in TEXT
    assert ";" not in TEXT and "\u2014" not in TEXT

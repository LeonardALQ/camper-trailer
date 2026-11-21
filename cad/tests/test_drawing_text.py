"""Every drawn sheet's revision descriptions fit REV-01's DESCRIPTION cell at the table's own text height (F6)."""
import yaml

from cad.drawings import sheet as S
from cad.partsdb import ROOT

REG = yaml.safe_load((ROOT / "data" / "drawings.yaml").read_text(encoding="utf-8"))


def test_revision_descriptions_fit_their_cell():
    room = S.rev_room("DESCRIPTION")
    assert S.text_mm("M" * 60, S.REV_TEXT) > room > S.text_mm("i" * 60, S.REV_TEXT)
    over = [f"{d['number']} {r['rev']} {S.text_mm(r['description'], S.REV_TEXT):.1f} mm" for d in REG["drawings"] if not d.get("retired")
            for r in d["revisions"] if S.text_mm(r["description"], S.REV_TEXT) > room]
    assert not over, f"longer than the {room:.0f} mm the DESCRIPTION cell holds: " + ", ".join(over)

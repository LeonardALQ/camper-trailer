"""Sheet text stays legible (F6): every revision description fits REV-01's DESCRIPTION cell at the table's own text
height, and a line crossing a free label is broken at its letters while a table cell's text is left as drawn."""
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


def test_a_line_through_a_label_is_broken_at_it():
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "medium")
    sh.text(45, 100, "WET ROOM", 2.0)
    sh.text(45, 60, "CLEAR", 2.0)
    sh.line(50, 50, 50, 55, "medium")
    sh.text(45, 30, "CELL", 2.0, cell=True)
    sh.line(50, 20, 50, 40, "thin")
    svg = sh.svg()
    assert svg.count('class="masked"') == 1 and svg.count('fill="#fff"/>') == 2
    assert svg.rindex("WET ROOM") > svg.rindex("<path")

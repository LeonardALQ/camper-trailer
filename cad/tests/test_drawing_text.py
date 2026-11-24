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
    sh.line(50, 90, 50, 110, "thin")
    sh.text(45, 100, "WET ROOM", 2.0)
    sh.text(45, 60, "CLEAR", 2.0)
    sh.line(50, 50, 50, 55, "medium")
    sh.text(45, 30, "CELL", 2.0, cell=True)
    sh.line(50, 20, 50, 40, "thin")
    svg = sh.svg()
    assert svg.count('class="masked"') == 1 and svg.count('fill="#fff"/>') == 2
    mask = svg.index("<rect", svg.index("<rect") + 1)
    assert svg.index("<path") < mask < svg.index("WET ROOM")


def test_a_label_across_a_heavy_line_moves_clear_of_it():
    """A free label whose mask would break a 0.35 mm line slides along its baseline clear of it (I2-64), and one that
    moves off its own place gets a leader back to it."""
    from cad.tools.overrun import check
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "medium")
    sh.text(45, 100, "WET ROOM", 2.0)
    svg = sh.svg()
    assert 'class="masked"' not in svg and check(svg)["mask_breaks"] == [] and sh.moves[0]["by"][1] == 0
    sh = S.Sheet()
    for x in range(30, 80, 2):
        sh.line(x, 90, x, 110, "medium")
    sh.text(40, 100, "BOARD", 2.0)
    svg = sh.svg()
    assert check(svg)["mask_breaks"] == [] and sh.moves[0]["leader"]


def test_a_label_under_a_later_white_fill_stays_under_it():
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "medium")
    sh.text(45, 100, "HIDDEN", 2.0)
    sh.fillrect(40, 95, 70, 105)
    assert 'class="masked"' not in sh.svg()

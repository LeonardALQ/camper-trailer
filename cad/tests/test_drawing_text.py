"""Sheet text stays legible (F6): every revision description fits REV-01's DESCRIPTION cell at the table's own text
height, a line crossing a free label is broken at its letters while a table cell's text is left as drawn, and
sheet.clear_labels moves a label clear of the heavy lines with its leader ending at what the label names (I2-64, I2-69)."""
import re

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
    """A free label whose mask would break a 0.35 mm line slides along its baseline clear of it (I2-64), and one boxed
    in by such lines that must leave its place gets a leader to what it names, the box it stood in (I2-69)."""
    from cad.tools.overrun import check
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "medium")
    sh.text(45, 100, "WET ROOM", 2.0)
    svg = sh.svg()
    assert 'class="masked"' not in svg and check(svg)["mask_breaks"] == [] and sh.moves[0]["by"][1] == 0
    sh = S.Sheet()
    for x in range(30, 80, 2):
        sh.line(x, 90, x, 110, "medium")
    sh.text(40, 100, "BOARD", 2.0, names=(30, 90, 80, 110))
    svg = sh.svg()
    r = check(svg)
    assert r["mask_breaks"] == [] and r["leader_faults"] == [] and sh.moves[0]["leader"] == "with a leader to what it names"
    lead = re.search(r'<path d="M[-\d.]+,[-\d.]+ L([-\d.]+),([-\d.]+)"[^>]*class="leader" data-names="box ', svg)
    x, y = float(lead[1]), S.Sheet.H - float(lead[2])
    assert 30 < x < 80 and 90 < y < 110


def test_a_label_whose_sheet_does_not_say_what_it_names_keeps_its_place():
    """A label boxed in by heavy lines with nothing to say what it names gets no leader back to an empty place: it stays
    where it reads, for the overrun check to report (I2-69)."""
    from cad.tools.overrun import check
    sh = S.Sheet()
    for x in range(30, 80, 2):
        sh.line(x, 90, x, 110, "medium")
    sh.text(40, 100, "BOARD", 2.0)
    svg = sh.svg()
    assert 'class="leader"' not in svg and check(svg)["mask_breaks"]


def test_a_letter_in_its_symbol_moves_with_it():
    """A letter drawn inside its own symbol stays in it: a line under the symbol's white disc does not move it, and one
    drawn over the symbol moves the symbol and its letter together, with a leader back to the place it marks (I2-69)."""
    from cad.tools.overrun import check

    def fan(sh, x, y):
        n0 = len(sh.el)
        sh.el.append(f'<circle cx="{x:.2f}" cy="{S.Sheet.H - y:.2f}" r="1.30" fill="#fff" stroke="#000" stroke-width="0.35"/>')
        sh.leads[len(sh.el)] = [(n0, ("circle", 1.3))]
        sh.text(x, y - 0.45, "A", 1.1, "middle", bold=True, names=(x, y))
    sh = S.Sheet()
    sh.line(80, 100, 120, 100, "medium")
    fan(sh, 100, 100)
    sh.svg()
    assert sh.moves == []
    sh = S.Sheet()
    fan(sh, 100, 100)
    sh.line(80, 100, 120, 100, "medium")
    svg = sh.svg()
    c = re.search(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="1.30"', svg)
    t = re.search(r'<text x="([-\d.]+)" y="([-\d.]+)"[^>]*>A</text>', svg)
    assert sh.moves and abs(float(t[1]) - float(c[1])) < 0.01 and abs(float(t[2]) - 0.45 - float(c[2])) < 0.01
    r = check(svg)
    assert r["line_hits"] == [] and r["mask_breaks"] == [] and r["leader_faults"] == [], r


def test_a_moved_leader_crosses_no_other():
    """clear_labels takes no place for a label whose leader would cross a leader already drawn (I2-69)."""
    sh = S.Sheet()
    sh.lead([(50, 50), (60, 60)], names=(50, 50))
    B, H = S._Board(sh), S.Sheet.H
    assert B.crosses_leader((50, H - 60), (60, H - 50), set()) and not B.crosses_leader((52, H - 50), (62, H - 60), set())
    assert not B.crosses_leader((60, H - 60), (70, H - 60), set()) and not B.crosses_leader((50, H - 60), (60, H - 50), {0})


def test_a_label_under_a_later_white_fill_stays_under_it():
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "medium")
    sh.text(45, 100, "HIDDEN", 2.0)
    sh.fillrect(40, 95, 70, 105)
    assert 'class="masked"' not in sh.svg()

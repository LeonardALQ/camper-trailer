"""The label overrun check (cad/tools/overrun.py): it passes a sheet whose labels clear their lines, and it finds a label
moved onto a line, a table cell's text across a line, a mark on a label, two labels on each other and a label under a
white fill drawn after it."""
import re

from cad.drawings import sheet as S
from cad.tools.overrun import check


def _sheet() -> S.Sheet:
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "medium")          # a free label across it is broken at its letters
    sh.text(45, 100, "WET ROOM", 2.0)
    sh.line(100, 20, 100, 60, "thin")
    sh.text(110, 40, "CELL TEXT", 2.0, cell=True)
    sh.text(150, 40, "MOVED", 2.0)
    return sh


def _counts(svg: str) -> tuple[int, int]:
    r = check(svg)
    return len(r["line_hits"]), len(r["text_overlaps"])


def _move(svg: str, text: str, x: float, y: float) -> str:
    """The sheet with one text's anchor moved to SVG point (x, y), as a slip in a sheet's code would put it there."""
    return re.sub(rf'<text ([^>]*?)x="[-\d.]+" y="[-\d.]+"([^>]*)>{text}</text>', rf'<text \1x="{x:.2f}" y="{y:.2f}"\2>{text}</text>', svg)


def test_a_clean_sheet_passes():
    svg = _sheet().svg()
    assert 'class="masked"' in svg and _counts(svg) == (0, 0)


def test_a_label_moved_onto_a_line_is_a_line_hit():
    svg = _move(_sheet().svg(), "MOVED", 98.0, S.Sheet.H - 40.0)
    hits, overlaps = _counts(svg)
    assert (hits, overlaps) == (1, 0)
    assert check(svg)["line_hits"][0]["text"] == "MOVED"


def test_a_cell_text_across_a_line_is_a_line_hit():
    sh = _sheet()
    sh.text(97, 30, "ACROSS", 2.0, cell=True)
    assert _counts(sh.svg()) == (1, 0)


def test_a_dot_on_a_label_is_a_line_hit():
    sh = _sheet()
    sh.circle(152, 40.6, 0.32, "fill")
    assert _counts(sh.svg()) == (1, 0)


def test_labels_on_each_other_and_under_a_fill_are_overlaps():
    sh = _sheet()
    sh.text(152, 40.3, "OVER", 2.0)
    assert _counts(sh.svg()) == (0, 1)
    sh = _sheet()
    sh.fillrect(108, 39, 114, 45)
    assert _counts(sh.svg()) == (0, 1)

"""The label overrun check (cad/tools/overrun.py), on sheets written without sheet.clear_labels, which would move the
faulty labels first: it passes a sheet whose labels clear their lines, and it finds a label
moved onto a line, a table cell's text across a line, a mark on a label, two labels on each other, a label under a white
fill drawn after it, a fill over the tops of a word's capitals, lines of capitals set too close, and a label's mask over a
heavy line (I2-64), while a mask over a thin dimension line passes."""
import re

import pytest

from cad.drawings import sheet as S
from cad.tools.overrun import check


def _sheet() -> S.Sheet:
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "thin")            # a free label across it is broken at its letters
    sh.text(45, 100, "WET ROOM", 2.0)
    sh.line(100, 20, 100, 60, "thin")
    sh.text(110, 40, "CELL TEXT", 2.0, cell=True)
    sh.text(150, 40, "MOVED", 2.0)
    return sh


def _counts(svg: str) -> tuple[int, int, int]:
    r = check(svg)
    return len(r["line_hits"]), len(r["text_overlaps"]), len(r["mask_breaks"])


def _move(svg: str, text: str, x: float, y: float) -> str:
    """The sheet with one text's anchor moved to SVG point (x, y), as a slip in a sheet's code would put it there."""
    return re.sub(rf'<text ([^>]*?)x="[-\d.]+" y="[-\d.]+"([^>]*)>{text}</text>', rf'<text \1x="{x:.2f}" y="{y:.2f}"\2>{text}</text>', svg)


def test_a_clean_sheet_passes():
    svg = _sheet().svg()
    assert 'class="masked"' in svg and _counts(svg) == (0, 0, 0)


def test_a_label_moved_onto_a_line_is_a_line_hit():
    svg = _move(_sheet().svg(), "MOVED", 98.0, S.Sheet.H - 40.0)
    assert _counts(svg) == (1, 0, 0)
    assert check(svg)["line_hits"][0]["text"] == "MOVED"


def test_a_cell_text_across_a_line_is_a_line_hit():
    sh = _sheet()
    sh.text(97, 30, "ACROSS", 2.0, cell=True)
    assert _counts(sh.svg(clear=False)) == (1, 0, 0)


def test_a_dot_on_a_label_is_a_line_hit():
    sh = _sheet()
    sh.circle(152, 40.6, 0.32, "fill")
    assert _counts(sh.svg(clear=False)) == (1, 0, 0)


def test_a_cell_text_under_a_line_through_its_capitals_tops_is_a_line_hit():
    """A line through the top tenth of the capitals crosses the letters, as the capitals stand 0.73 of the size."""
    sh = _sheet()
    sh.text(110, 70, "TOPS", 2.0, cell=True)
    sh.line(105, 70 + 0.68 * 2.0, 130, 70 + 0.68 * 2.0, "thin")
    assert _counts(sh.svg(clear=False)) == (1, 0, 0)


def test_labels_on_each_other_and_under_a_fill_are_overlaps():
    sh = _sheet()
    sh.text(152, 40.3, "OVER", 2.0)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0)
    sh = _sheet()
    sh.fillrect(108, 39, 114, 45)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0)


def test_a_fill_over_the_tops_of_the_capitals_is_an_overlap():
    """A white fill drawn over the top 14 % of a word's capitals hides their tops."""
    sh = _sheet()
    sh.text(200, 100, "DAY", 2.0)
    sh.fillrect(195, 100 + 0.86 * S.CAPS * 2.0, 215, 104)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0)


@pytest.mark.parametrize("apart", [0.58, 0.65, 0.72])
def test_lines_of_capitals_set_too_close_are_an_overlap(apart):
    """Two lines of capitals whose baselines stand less than the capitals' height apart run into each other."""
    sh = _sheet()
    sh.text(200, 150, "PLATE TO THE WEBS", 2.0)
    sh.text(200, 150 + apart * 2.0, "PLATE TO THE WEBS", 2.0)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0)


def test_lines_of_capitals_a_capital_apart_pass():
    sh = _sheet()
    sh.text(200, 150, "PLATE TO THE WEBS", 2.0)
    sh.text(200, 150 + 0.75 * 2.0, "PLATE TO THE WEBS", 2.0)
    assert _counts(sh.svg()) == (0, 0, 0)


@pytest.mark.parametrize("sty", ["thick", "medium"])
def test_a_mask_over_a_heavy_outline_is_a_mask_break(sty):
    """A label across a 0.5 mm or a 0.35 mm outline is masked, and its mask cuts a gap in the outline."""
    sh = _sheet()
    sh.rect(240, 180, 280, 200, sty)
    sh.text(236, 190, "OUTLINE", 2.0)
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 1) and check(svg)["mask_breaks"][0]["text"] == "OUTLINE"


def test_a_mask_over_a_thin_dimension_line_passes():
    """A label across a 0.18 mm dimension line is masked and breaks it, as dimension text may."""
    sh = _sheet()
    S.hdim(sh, 240, 230, 300, 230, 222, "60", size=2.0)
    sh.text(243, 221.3, "ACROSS", 2.0)
    svg = sh.svg()
    assert svg.count('class="masked"') == 2 and _counts(svg) == (0, 0, 0)

"""The label overrun check (cad/tools/overrun.py), on sheets written without sheet.clear_labels, which would move the
faulty labels first: it passes a sheet whose labels clear their lines, and it finds a label
moved onto a line, a table cell's text across a line, a mark on a label, two labels on each other, a label under a white
fill drawn after it, a fill over the tops of a word's capitals, lines of capitals set too close, and a label's mask over a
heavy line (I2-64), while a mask over a thin dimension line passes. Its fourth class finds a leader that ends off what
its label names, two leaders that cross and a leader through a symbol (I2-69), and a letter on its symbol's white disc
passes over the line under the disc. It reads a weld symbol's and every other arrow's line with the leaders, but no
dimension line, and finds a letter drawn in its symbol that ends up outside it (I2-76), while a balloon grows to clear its
letters. Its fifth class finds a text whose letters run past the frame, 2 mm past it among them, or into the title
block, while the title block's own texts pass. Each text is measured where CairoSVG draws it: its letters' box holds
the ink the PNG shows, for capitals, lower case, digits and mixed runs at the sheets' sizes, at each anchor, a line
through a word's last letter is a hit, and a line of a note that starts with spaces is drawn and checked from its
anchor (fx18-ovr). sheet.notes wraps each note by its measured width inside its column and hangs its continuation lines
from its text, and the sixth class finds a continuation line drawn under its note's number (fx20-dwg)."""
import io
import re

import pytest

from cad.drawings import sheet as S
from cad.tools.overrun import CLASSES, check


def _sheet() -> S.Sheet:
    sh = S.Sheet()
    sh.line(50, 90, 50, 110, "thin")            # a free label across it is broken at its letters
    sh.text(45, 100, "WET ROOM", 2.0)
    sh.line(100, 20, 100, 60, "thin")
    sh.text(110, 40, "CELL TEXT", 2.0, cell=True)
    sh.text(150, 40, "MOVED", 2.0)
    return sh


def _counts(svg: str) -> tuple[int, int, int, int, int, int]:
    r = check(svg)
    return tuple(len(r[k]) for k in CLASSES)


def _move(svg: str, text: str, x: float, y: float) -> str:
    """The sheet with one text's anchor moved to SVG point (x, y), as a slip in a sheet's code would put it there."""
    return re.sub(rf'<text ([^>]*?)x="[-\d.]+" y="[-\d.]+"([^>]*)>{text}</text>', rf'<text \1x="{x:.2f}" y="{y:.2f}"\2>{text}</text>', svg)


def test_a_clean_sheet_passes():
    svg = _sheet().svg()
    assert 'class="masked"' in svg and _counts(svg) == (0, 0, 0, 0, 0, 0)


def test_a_label_moved_onto_a_line_is_a_line_hit():
    svg = _move(_sheet().svg(), "MOVED", 98.0, S.Sheet.H - 40.0)
    assert _counts(svg) == (1, 0, 0, 0, 0, 0)
    assert check(svg)["line_hits"][0]["text"] == "MOVED"


def test_a_cell_text_across_a_line_is_a_line_hit():
    sh = _sheet()
    sh.text(97, 30, "ACROSS", 2.0, cell=True)
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 0, 0)


def test_a_dot_on_a_label_is_a_line_hit():
    sh = _sheet()
    sh.circle(152, 40.6, 0.32, "fill")
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 0, 0)


def test_a_cell_text_under_a_line_through_its_capitals_tops_is_a_line_hit():
    """A line through the top tenth of the capitals crosses the letters, as the capitals stand 0.73 of the size."""
    sh = _sheet()
    sh.text(110, 70, "TOPS", 2.0, cell=True)
    sh.line(105, 70 + 0.68 * 2.0, 130, 70 + 0.68 * 2.0, "thin")
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 0, 0)


def test_labels_on_each_other_and_under_a_fill_are_overlaps():
    sh = _sheet()
    sh.text(152, 40.3, "OVER", 2.0)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0, 0, 0, 0)
    sh = _sheet()
    sh.fillrect(108, 39, 114, 45)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0, 0, 0, 0)


def test_a_fill_over_the_tops_of_the_capitals_is_an_overlap():
    """A white fill drawn over the top 14 % of a word's capitals hides their tops."""
    sh = _sheet()
    sh.text(200, 100, "DAY", 2.0)
    sh.fillrect(195, 100 + 0.86 * S.CAPS * 2.0, 215, 104)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0, 0, 0, 0)


@pytest.mark.parametrize("apart", [0.58, 0.65, 0.72])
def test_lines_of_capitals_set_too_close_are_an_overlap(apart):
    """Two lines of capitals whose baselines stand less than the capitals' height apart run into each other."""
    sh = _sheet()
    sh.text(200, 150, "PLATE TO THE WEBS", 2.0)
    sh.text(200, 150 + apart * 2.0, "PLATE TO THE WEBS", 2.0)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0, 0, 0, 0)


def test_lines_of_capitals_a_capital_apart_pass():
    sh = _sheet()
    sh.text(200, 150, "PLATE TO THE WEBS", 2.0)
    sh.text(200, 150 + 0.75 * 2.0, "PLATE TO THE WEBS", 2.0)
    assert _counts(sh.svg()) == (0, 0, 0, 0, 0, 0)


@pytest.mark.parametrize("sty", ["thick", "medium"])
def test_a_mask_over_a_heavy_outline_is_a_mask_break(sty):
    """A label across a 0.5 mm or a 0.35 mm outline is masked, and its mask cuts a gap in the outline."""
    sh = _sheet()
    sh.rect(240, 180, 280, 200, sty)
    sh.text(236, 190, "OUTLINE", 2.0)
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 1, 0, 0, 0) and check(svg)["mask_breaks"][0]["text"] == "OUTLINE"


def test_a_mask_over_a_thin_dimension_line_passes():
    """A label across a 0.18 mm dimension line is masked and breaks it, as dimension text may."""
    sh = _sheet()
    S.hdim(sh, 240, 230, 300, 230, 222, "60", size=2.0)
    sh.text(243, 221.3, "ACROSS", 2.0)
    svg = sh.svg()
    assert svg.count('class="masked"') == 2 and _counts(svg) == (0, 0, 0, 0, 0, 0)


def test_a_leader_on_what_its_label_names_passes():
    """A leader from its label to a point in the box the label names, crossing no leader and no symbol, passes."""
    sh = _sheet()
    sh.rect(250, 100, 270, 110, "medium")
    sh.text(275, 112, "LOCKER", 2.0)
    sh.lead([(275, 112), (262, 105)], names=(250, 100, 270, 110))
    sh.circle(262, 105, 0.3, "fill")
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 0, 0, 0)


def test_a_leader_off_what_its_label_names_is_a_leader_fault():
    """A leader that ends beside the box its label names, as clear_labels' leaders to a label's old middle did (I2-69)."""
    sh = _sheet()
    sh.rect(250, 100, 270, 110, "medium")
    sh.text(275, 116, "LOCKER", 2.0)
    sh.lead([(275, 116), (273, 112)], names=(250, 100, 270, 110))
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 0, 1, 0, 0) and check(svg)["leader_faults"][0]["kind"] == "off what it names"


def test_two_leaders_that_cross_are_a_leader_fault():
    """Two tags' leaders that cross beside them, as CT-602's W D-04 and W D-05, U K-16A did (I2-69)."""
    sh = _sheet()
    sh.lead([(250, 150), (262, 140)], names=(250, 150))
    sh.lead([(262, 150), (250, 140)], names=(262, 150))
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 0, 1, 0, 0) and check(svg)["leader_faults"][0]["kind"] == "crosses or touches a leader"


def test_a_leader_ending_on_another_is_a_leader_fault():
    """A tag's leader that stops 0.1 mm short of another tag's leader reads as joining it."""
    sh = _sheet()
    sh.lead([(250, 150), (262, 140)], names=(250, 150))
    sh.lead([(262, 150), (256.1, 145.1)], names=(262, 150))
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 1, 0, 0)


def test_a_leader_through_a_symbol_is_a_leader_fault():
    """A leader that runs through a gland's circle to what its label names beyond it, as CT-602's G7 did (I2-69)."""
    sh = _sheet()
    sh.circle(260, 200, 0.9, "medium")
    sh.lead([(255, 200), (265, 200)], names=(265, 200))
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 0, 1, 0, 0) and check(svg)["leader_faults"][0]["kind"] == "through a symbol"


def test_a_tag_leader_from_the_gland_it_names_passes():
    """A tag's leader starts on the gland it points into, so that gland's circle and the tag's dot are its own."""
    sh = _sheet()
    sh.circle(260, 230, 0.9, "medium")
    sh.lead([(260, 230), (266, 236)], names=(260, 230))
    sh.circle(260, 230, 0.32, "fill")
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 0, 0, 0)


def test_a_letter_on_its_symbols_white_disc_passes():
    """A fan's letter in its circle, whose white disc is drawn over the heavy line through it, is neither crossed by the
    line nor masked (CT-621's A to D)."""
    sh = _sheet()
    sh.line(280, 250, 320, 250, "medium")
    sh.el.append(f'<circle cx="300.00" cy="{S.Sheet.H - 250:.2f}" r="1.30" fill="#fff" stroke="#000" stroke-width="0.35"/>')
    sh.text(300, 250 - 0.45, "A", 1.1, "middle", bold=True)
    svg = sh.svg(clear=False)
    assert not re.search(r'<text class="masked"[^>]*>A</text>', svg) and _counts(svg) == (0, 0, 0, 0, 0, 0)


def _weld_arrow(sh, tip, elbow):
    """A weld symbol's arrow as cad/drawings/chassis_sheets.weld_symbol draws it: a thin line from the joint to the
    elbow, then the arrowhead at the joint."""
    sh.line(tip[0], tip[1], elbow[0], elbow[1], "thin")
    L = ((tip[0] - elbow[0]) ** 2 + (tip[1] - elbow[1]) ** 2) ** 0.5
    sh.arrow(tip, ((tip[0] - elbow[0]) / L, (tip[1] - elbow[1]) / L), 2.0, 0.4)


def test_a_weld_symbols_arrow_across_a_leader_is_a_leader_fault():
    """A weld symbol's arrow is marked as an arrow's line, so the fourth class reads it with the leaders: one that
    crosses a part's leader fails, as CT-102's detail C showed (I2-76)."""
    sh = _sheet()
    _weld_arrow(sh, (250, 150), (262, 140))
    sh.lead([(262, 150), (250, 140)], names=(262, 150))
    svg = sh.svg(clear=False)
    assert svg.count('class="arrow"') == 1 and _counts(svg) == (0, 0, 0, 1, 0, 0)
    assert check(svg)["leader_faults"][0]["kind"] == "crosses or touches a leader"


def test_two_arrows_that_cross_are_a_leader_fault():
    sh = _sheet()
    _weld_arrow(sh, (250, 150), (262, 140))
    _weld_arrow(sh, (262, 150), (250, 140))
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 1, 0, 0)


def test_a_dimension_lines_arrowheads_mark_no_arrow():
    """A dimension line ends in arrowheads too, but it is no arrow pointing at a part, so it is not marked."""
    sh = _sheet()
    S.hdim(sh, 240, 230, 300, 230, 222, "60", size=2.0)
    S.vdim(sh, 320, 200, 320, 240, 326, "40", size=2.0)
    assert 'class="arrow"' not in sh.svg()


def _letter_on_a_line(sh, registered: bool):
    """A contactor's letter in its circle on a 0.4 mm circuit line through it, as CT-601 draws K2, K4 and S1."""
    sh.line(280, 250, 320, 250, "medium")
    n0 = len(sh.el)
    if registered:      # the circle a white disc over the line, the letter registered with it
        sh.el.append(f'<circle cx="300.00" cy="{S.Sheet.H - 250:.2f}" r="1.40" fill="#fff" stroke="#000" stroke-width="0.35"/>')
        sh.leads[len(sh.el)] = [(n0, ("circle", 1.4))]
        sh.text(300, 250 - 0.45, "K2", 0.95, "middle", bold=True, names=(300, 250, 1.4))
    else:
        sh.circle(300, 250, 1.4, "medium")
        sh.text(300, 250 - 0.45, "K2", 0.95, "middle", bold=True)


def test_a_letter_that_leaves_its_symbol_is_a_leader_fault():
    """A letter drawn in its symbol but not registered with it, with a heavy line through both, is moved off the line by
    clear_labels and out of its circle, as CT-601's contactor letters were by 2.0 mm (I2-69, I2-76)."""
    sh = _sheet()
    _letter_on_a_line(sh, registered=False)
    svg = sh.svg()
    assert 'data-in="' in svg and 'data-sym="' in svg
    r = check(svg)["leader_faults"]
    assert [x["kind"] for x in r] == ["out of its symbol"] and r[0]["names"] == "K2"


def test_a_letter_registered_on_its_white_disc_stays_in_its_symbol():
    """The same letter on its circle's white disc, drawn over the line, and registered with it, stays and passes."""
    sh = _sheet()
    _letter_on_a_line(sh, registered=True)
    svg = sh.svg()
    assert not sh.moves and 'data-in="' in svg and _counts(svg) == (0, 0, 0, 0, 0, 0)


def test_a_letter_moved_out_of_its_symbol_in_the_code_is_a_leader_fault():
    """A revision triangle's letter set 3 mm off its triangle, as a slip in a sheet's code would put it."""
    sh = _sheet()
    S.rev_tag(sh, 340, 120, "B")
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 0, 0, 0, 0)
    assert _counts(_move(svg, "B", 343.5, S.Sheet.H - 120.0 + 0.7)) == (0, 0, 0, 1, 0, 0)


def test_a_weld_arrow_drawn_as_a_leader_counts_once_and_ends_on_its_all_round_circle():
    """chassis_sheets.weld_symbol draws its arrow as a leader to the joint, ending on the elbow's circle when the weld is
    all round: the arrowhead after it marks no second line, and the circle it ends on is no symbol it passes through."""
    sh = _sheet()
    tip, elbow, r = (250.0, 150.0), (262.0, 158.0), 1.2
    L = ((elbow[0] - tip[0]) ** 2 + (elbow[1] - tip[1]) ** 2) ** 0.5
    sh.lead([tip, (elbow[0] + (tip[0] - elbow[0]) / L * r, elbow[1] + (tip[1] - elbow[1]) / L * r)], names=tip)
    sh.arrow(tip, ((tip[0] - elbow[0]) / L, (tip[1] - elbow[1]) / L), 2.0, 0.4)
    sh.line(elbow[0], elbow[1], elbow[0] + 16, elbow[1], "medium")
    sh.circle(elbow[0], elbow[1], r, "thin")
    svg = sh.svg(clear=False)
    assert svg.count('class="leader"') == 1 and 'class="arrow"' not in svg and _counts(svg) == (0, 0, 0, 0, 0, 0)


def _flow(sh, pts, level=None):
    """A flow drawn as the services sheets draw one: its polyline, then its arrowhead at its end (I2-81)."""
    sh.path(pts, "thin")
    (a, b), (c, d) = pts[-2], pts[-1]
    L = ((c - a) ** 2 + (d - b) ** 2) ** 0.5
    sh.arrow((c, d), ((c - a) / L, (d - b) / L), 1.6, 0.45, level=level)


def test_a_polyline_flow_is_read_as_an_arrow_and_its_crossing_fails():
    """I2-81: a flow's polyline with its head at the end is marked as the arrow's line, so a crossing on its first
    segments, far from the head, is a leader fault."""
    sh = _sheet()
    _flow(sh, [(240, 150), (240, 180), (280, 180)])
    _flow(sh, [(230, 165), (260, 165)])
    svg = sh.svg(clear=False)
    assert svg.count('class="arrow"') == 2 and _counts(svg) == (0, 0, 0, 1, 0, 0)


def test_flows_at_different_levels_may_cross_and_one_level_may_not():
    """I2-81: a duct under the floor and the air in the cabin cross in plan without meeting, so two flows marked at
    different levels pass, and two at one level, or a level and none, fail."""
    for lv, faults in ((("floor", "cabin"), 0), (("floor", "floor"), 1), (("floor", None), 1)):
        sh = _sheet()
        _flow(sh, [(240, 150), (240, 180), (280, 180)], lv[0])
        _flow(sh, [(230, 165), (260, 165)], lv[1])
        assert _counts(sh.svg(clear=False)) == (0, 0, 0, faults, 0, 0), lv


def test_a_flow_branching_off_another_at_a_tee_passes():
    """I2-81: a schematic's branch starts on the main line's run, which is a tee, not a crossing."""
    sh = _sheet()
    _flow(sh, [(240, 150), (240, 180), (260, 180)])
    _flow(sh, [(240, 165), (260, 165)])
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 0, 0, 0)


def test_a_head_set_along_its_line_marks_the_line():
    """I2-81: the heat-recovery pairs set a head inside each end of one line, and the line is marked once."""
    sh = _sheet()
    sh.line(240, 150, 300, 150, "thin")
    sh.arrow((295, 150), (1, 0), 1.6, 0.45)
    sh.arrow((245, 150), (-1, 0), 1.6, 0.45)
    assert sh.svg(clear=False).count('class="arrow"') == 1


def test_a_leader_through_a_hardpoints_mark_is_a_leader_fault():
    """I2-81: CT-104's hardpoints are filled triangles, marks rather than arrowheads, and a leader may not pass
    through one, as through any symbol."""
    sh = _sheet()
    sh.path([(260, 151.4), (258.8, 149.2), (261.2, 149.2)], "fill", closed=True)
    sh.el[-1] = sh.el[-1][:-2] + ' class="mark"/>'
    sh.text(240, 160, "TAG", 2.0)
    sh.lead([(244, 159), (276, 140)], names=(276, 140))
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 1, 0, 0)


def test_two_flows_drawn_over_each_other_are_no_tee_at_any_level():
    """I2-85: two flows on one line, one lying 10 mm along the other, are drawn over each other, not a tee, so they
    fail at one level and at two levels apart. A branch that meets the other's run at a right angle still passes."""
    for lv in (("floor", "floor"), ("floor", "cabin"), (None, None)):
        sh = _sheet()
        _flow(sh, [(240, 150), (240, 170)], lv[0])
        _flow(sh, [(240, 160), (240, 190)], lv[1])
        r = check(sh.svg(clear=False))
        assert len(r["leader_faults"]) == 1 and "runs along" in r["leader_faults"][0]["kind"], (lv, r["leader_faults"])
    sh = _sheet()
    _flow(sh, [(240, 150), (240, 190)], "floor")
    _flow(sh, [(240, 170), (262, 170)], "floor")
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 0, 0, 0)


def test_an_end_that_joins_a_run_along_it_is_no_tee():
    """I2-85: a flow whose last segment comes in along the other's run, 6 degrees off it, meets it at no angle a tee
    has, so it fails as a crossing, where the same end turned to meet the run square passes."""
    sh = _sheet()
    _flow(sh, [(240, 150), (240, 190)])
    sh.path([(242.7, 140), (240.3, 165)], "thin")
    S.mark_flow(sh)
    sh2 = _sheet()
    _flow(sh2, [(240, 150), (240, 190)])
    sh2.path([(262, 165), (240, 165)], "thin")
    S.mark_flow(sh2)
    assert _counts(sh.svg(clear=False))[3] == 1 and _counts(sh2.svg(clear=False)) == (0, 0, 0, 0, 0, 0)


def test_a_flow_line_without_a_head_is_read_with_the_arrows():
    """I2-81, I2-85: a flow drawn with no head of its own, as CT-611's joined tank outlets meet the rear tank's line, is
    marked as a flow's line, so a crossing on it fails and its tee passes."""
    sh = _sheet()
    sh.path([(230, 165), (260, 165)], "thin")
    S.mark_flow(sh)
    _flow(sh, [(240, 150), (240, 180), (280, 180)])
    svg = sh.svg(clear=False)
    assert svg.count('class="arrow"') == 2 and _counts(svg) == (0, 0, 0, 1, 0, 0)


def _title_block(sh: S.Sheet) -> None:
    S.title_block(sh, owner="LEONARD AL-QASEER", project="CAMPER TRAILER", number="CT-999", title="Frame rule", subtitle="Test sheet",
                  rev="A", status="CHECK", date="2026-11-25", drawn="Kiro", checked="", approved="", engineer="TO BE ENGAGED",
                  sheet_no=1, sheets=1, size="A3", scale=5, material="AS NOTED", mass_note="", model_ref="build/test.step", git="0000000")


def _framed() -> S.Sheet:
    """A sheet with its frame and title block, as every sheet draws them."""
    sh = S.Sheet()
    S.frame(sh)
    _title_block(sh)
    return sh


def test_a_framed_sheet_and_its_title_blocks_own_texts_pass():
    sh = _framed()
    sh.text(22, 280, "NOTES", 2.5, bold=True)
    sh.text(22, 276, "1. A NOTE INSIDE THE FRAME", 2.0)
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 0, 0, 0)


def test_a_text_2_mm_past_the_frame_is_a_frame_overrun():
    """A note whose letters run 2 mm past the frame's line, as CT-601's arm notes were said to before fx16-svc wrapped
    them 4 mm in. The frame's line runs through its letters, so it is a line hit as well."""
    sh = _framed()
    sh.text(410.35 + 2.0, 150, "THE ARM. THE SEAT WEIGHS 0.057 kg ON K-13", 1.2, "end")
    r = check(sh.svg(clear=False))
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 1, 0) and r["frame_overruns"][0]["kind"] == "past the frame by 2.70 mm"


def test_a_text_in_the_margin_is_a_frame_overrun():
    """A label set below the frame, where no line crosses it, fails by the fifth class alone."""
    sh = _framed()
    sh.text(100, 5.0, "STRAY", 2.0)
    assert _counts(sh.svg(clear=False)) == (0, 0, 0, 0, 1, 0)


def test_a_label_into_the_title_block_is_a_frame_overrun():
    """A label drawn after the title block whose letters reach into it across its top line, and one drawn before it that
    the block's white fill hides in part: both reach into the title block."""
    sh = _framed()
    sh.text(300, 65.2, "INTO THE BLOCK", 2.0)
    r = check(sh.svg(clear=False))
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 1, 0) and r["frame_overruns"][0]["kind"] == "into the title block"
    sh = S.Sheet()
    S.frame(sh)
    sh.text(300, 65.2, "INTO THE BLOCK", 2.0)
    _title_block(sh)
    assert _counts(sh.svg(clear=False)) == (0, 1, 0, 0, 1, 0)


def test_a_line_through_a_words_last_letter_is_a_line_hit():
    """A thin line 0.05 mm inside the ink of a word's last letter crosses its letters: the cores run from the first
    letter's ink to the last one's, where they stopped 0.12 of the size in from the ends of the advance (fx18-ovr)."""
    sh = _sheet()
    sh.text(110, 70, "HELD", 2.0, cell=True)
    x = 110 + S.text_extent("HELD", 2.0).right - 0.05
    sh.line(x, 66, x, 74, "thin")
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 0, 0)


def test_a_note_line_that_starts_with_spaces_is_checked_where_it_is_drawn():
    """CairoSVG draws a text without its leading spaces, from its anchor, so a note's continuation line ('   ' and its
    words) is measured from its anchor, and a line through its first letter is a hit."""
    t = dict(t="   UNDER EACH RAIL", x=110.0, y=S.Sheet.H - 70, s=2.0, anchor="start", bold=False)
    x0, w, _ = S.text_core(t)
    assert x0 == 110.0 and w == pytest.approx(S.text_mm("UNDER EACH RAIL", 2.0))
    sh = _sheet()
    sh.text(110, 70, t["t"], 2.0, cell=True)
    sh.line(110.3, 66, 110.3, 74, "thin")
    assert _counts(sh.svg(clear=False)) == (1, 0, 0, 0, 0, 0)


RUNS = ["EACH ARM IS 300 x 25 x 3 mm 316 STRIP, ITS TORSION SPRING", "EEEEEEEEEEEEEEEEEEEE", "WAVY TAJ AVOW LYTTA",
        "the quick brown fox jumps over the lazy dog", "0123456789 3,639.2 4,497.2", "Tare 2,757 kg, TC2 3,639 kg with growth",
        "   UNDER EACH RAIL, THE LAP 2.5 OPEN", "MODEL: build/trailer.step  DATA REV 8a18dfb  (TB-12)"]
SIZES = (1.2, 1.75, 2.0, 2.5, 3.5)


@pytest.mark.parametrize("bold", [False, True])
@pytest.mark.parametrize("anchor,x", [("start", 30.0), ("middle", 200.0), ("end", 390.0)])
def test_each_texts_letters_lie_where_cairosvg_draws_them(anchor, x, bold):
    """Capitals, lower case, digits, mixed runs, a note's indented line and a run with two spaces, drawn by Sheet.text at
    the sheets' sizes and rendered as sheet.write renders the PNG: the ink each one shows lies inside the box text_ink
    gives it, to the pixel, so no letter runs past what the masks, clear_labels and the check measure (fx18-ovr)."""
    import cairosvg
    import numpy as np
    from PIL import Image
    px = S.PNG_PX / S.Sheet.W
    sh, rows, y = S.Sheet(), [], 285.0
    for s in SIZES:
        for v in RUNS:
            y -= max(2.2 * s, 3.0)
            sh.text(x, y, v, s, anchor, bold=bold, cell=True)
            rows.append(dict(t=v, x=x, y=S.Sheet.H - y, s=s, anchor=anchor, bold=bold))
    png = cairosvg.svg2png(bytestring=sh.svg(clear=False).encode("utf-8"), output_width=S.PNG_PX)
    a = np.asarray(Image.open(io.BytesIO(png)).convert("L")) < 250
    out = []
    for t in rows:
        r0, r1 = int((t["y"] - 1.2 * t["s"]) * px), int((t["y"] + 0.45 * t["s"]) * px) + 1
        cols, lines = np.where(a[r0:r1].any(axis=0))[0], np.where(a[r0:r1].any(axis=1))[0]
        ink = (cols[0] / px, (cols[-1] + 1) / px, (r0 + lines[0]) / px, (r0 + lines[-1] + 1) / px)
        box = S.text_ink(t)
        if ink[0] < box[0] - 1 / px or ink[1] > box[1] + 1 / px or ink[2] < box[2] - 1 / px or ink[3] > box[3] + 1 / px:
            out.append(f"{t['t'][:24]!r} at {t['s']} mm: ink {', '.join(f'{v:.2f}' for v in ink)} outside {', '.join(f'{v:.2f}' for v in box)}")
    assert not out, out


def test_a_balloon_too_small_for_its_letters_grows_to_clear_them():
    """CT-101's equipment balloons asked for a 2.4 mm circle round 2.8 mm letters, which touched it: the circle grows
    until the letters keep sheet.BALLOON_GAP clear of its line, its leader ends on it, and the check passes."""
    sh = _sheet()
    S.balloon(sh, (250, 150), (262, 160), "CM", 2.4)
    svg = sh.svg(clear=False)
    r = float(re.search(r'<circle cx="262.00" cy="[-\d.]+" r="([\d.]+)"', svg)[1])
    assert 2.4 < r < 3.0 and _counts(svg) == (0, 0, 0, 0, 0, 0)


_NOTE = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)" font-size="([\d.]+)"[^>]*data-note="([\d.]+)"[^>]*>(.*?)</text>')
WIDE = "MOW THE WIDE DAMP MEADOW WHEN THE DEW HAS GONE, AND WIND THE WOMBAT'S WOOL ROUND THE MOUNT"


def _note_lines(svg: str) -> list[dict]:
    """The lines sheet.notes drew, in order: each one's anchor, size, note (data-note) and text."""
    return [dict(x=float(m[1]), y=float(m[2]), s=float(m[3]), note=m[4], t=m[5]) for m in _NOTE.finditer(svg)]


def test_notes_wrap_by_width_and_hang_their_continuation_lines_from_their_text():
    """sheet.notes wraps each note by its measured width, so a note of wide capitals keeps inside its column, where 40
    of its letters run past it, and draws each continuation line at x plus the measured width of its "N. " with no
    leading spaces. Rendered as sheet.write renders the PNG, each continuation line's ink starts where its note's text
    starts, clear of the number, and the check passes the sheet (fx20-dwg)."""
    import cairosvg
    import numpy as np
    from PIL import Image
    x, size, width = 30.0, 2.0, 40
    room = width * S.CH * size
    assert S.text_mm(WIDE[:40], size) > room
    sh = S.Sheet()
    S.notes(sh, x, 200, ["A SHORT NOTE", WIDE, "THE LAST NOTE " * 5], size=size, width_chars=width)
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 0, 0, 0, 0)
    lines = _note_lines(svg)
    assert [t["note"] for t in lines].count("1.2") > 2
    px = S.PNG_PX / S.Sheet.W
    a = np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=S.PNG_PX))).convert("L")) < 250
    for t in lines:
        number = t["note"].split(".")[1] + ". "
        hang = S.pen_mm(number, size)
        first = t["t"].startswith(number)
        assert t["x"] == pytest.approx(x if first else x + hang, abs=0.006)
        assert t["x"] + S.text_mm(t["t"], size) <= x + hang + room + 0.01
        if not first:
            r0, r1 = int((t["y"] - S.CAPS * size) * px), int(t["y"] * px)
            left = np.where(a[r0:r1].any(axis=0))[0][0] / px
            assert x + hang - 1 / px <= left <= x + hang + 0.15 * size, (t["t"], left)


def test_a_continuation_line_drawn_under_its_notes_number_is_an_indent_fault():
    """A note's continuation line drawn from the note's own x, as sheet.notes drew it with three leading spaces, which
    CairoSVG drops, starts left of the note's text by the width of its "1. ": an indent fault, and the only fault."""
    sh = S.Sheet()
    S.notes(sh, 30, 200, ["THE FIRST LINE OF A NOTE THAT RUNS ON TO A SECOND LINE"], size=2.0, width_chars=30)
    svg = sh.svg(clear=False)
    assert _counts(svg) == (0, 0, 0, 0, 0, 0)

    def flush(m):
        if m[5].startswith("1. "):
            return m[0]
        return m[0].replace(f'x="{m[1]}"', 'x="30.00"', 1).replace(f">{m[5]}<", f">   {m[5]}<", 1)
    old = _NOTE.sub(flush, svg)
    assert _counts(old) == (0, 0, 0, 0, 0, 1)
    assert check(old)["indent_faults"][0]["kind"] == f"{S.pen_mm('1. ', 2.0):.2f} mm left of its note's text"

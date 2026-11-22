"""The services sheets' run tags and gland lists (I2-17), and the Electrical page's BD-11 figures (I2-19): every run is
tagged at both ends, every change of level is a tag, every gland a run passes is named on CT-602 or CT-612 and listed
on CT-603, and BD-11's unassigned part is read from its own item."""
from __future__ import annotations

from cad import routes as R
from cad.drawings import services_sheets as SS
from cad.services import services
from cad.tests.test_trailer import EV

LAY = EV["layout"]
V = LAY.V
RES = R.resolve(LAY)
GLANDS = {g["id"]: g for g in RES["svc"]["glands"]}


def test_levels_follow_the_heights():
    assert SS.level(V["floor_underside_z"] - 1, V) == "U"
    assert SS.level(V["floor_z"] + SS.FLOOR_BAND, V) == "F"
    assert SS.level(V["floor_z"] + SS.FLOOR_BAND + 1, V) == "W"
    assert SS.level(V["ceiling_z"] - SS.CEILING_BAND, V) == "C"


def test_every_run_is_tagged_at_both_ends_and_at_each_change_of_level():
    for run in RES["runs"]:
        ev = SS.run_events(run, V)
        assert len(ev) >= 2, run["id"]
        d = run["dense"]
        assert ev[0][0] == (d[0][0], d[0][1]) and ev[-1][0] == (d[-1][0], d[-1][1]), run["id"]
        # a change of level reads FROM/TO, and each tag starts at the level the one before it ended
        levels = [code.split("/") for _, code in ev]
        for a, b in zip(levels, levels[1:]):
            assert a[-1] == b[0], (run["id"], levels)


def test_every_run_is_in_a_tag_on_its_sheet():
    for styles, clip in ((SS.ELEC_STYLE, V["body_x0"] - 250.0), (SS.PIPE_STYLE, None)):
        runs = [r for r in RES["runs"] if r["system"] in styles]
        tagged = {rid for c in SS.tag_clusters(runs, V, GLANDS, clip_x=clip) for rid in c["runs"]}
        assert tagged == {r["id"] for r in runs}


def test_every_gland_a_run_passes_heads_a_tag_or_is_listed():
    for styles in (SS.ELEC_STYLE, SS.PIPE_STYLE):
        runs = [r for r in RES["runs"] if r["system"] in styles]
        heads = {c["header"] for c in SS.tag_clusters(runs, V, GLANDS)}
        passed = {g for r in runs for g in r.get("glands") or []}
        assert passed <= heads, sorted(passed - heads)


def test_id_lists_write_ranges():
    assert SS.id_list(["B-06", "B-04", "B-05", "B-08"]) == "B-04 TO B-06, B-08"
    assert SS.id_list(["C9B", "C9", "C10", "C1"]) == "C1, C9, C9B, C10"


def test_bd11_unassigned_part_is_its_allowance_item():
    b = services()["bd11"]
    assert b and b["line"] == "BD-11"
    assert 0 < b["unassigned_kg"] < b["kg"]
    assert b["unassigned_kg"] == round(sum(p["kg"] for p in b["parts"] if p["item"].lower().startswith("allowance")), 1)

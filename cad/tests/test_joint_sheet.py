"""CT-106 (I2-95): the XT hinge joint and the rear bay's shear panel, drawn here as the drawings step draws it and read
against the chassis data. It follows CT-105 in the set, and the figures it gives are the data's."""
from __future__ import annotations

import functools
import html
import re

import yaml

from cad.partsdb import ROOT

REG = yaml.safe_load((ROOT / "data" / "drawings.yaml").read_text(encoding="utf-8"))
_TEXT = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)"[^>]*>(.*)</text>')


@functools.lru_cache(maxsize=1)
def _drawn():
    """CT-106 kept in memory, and its texts."""
    from cad.drawings import joint_sheet
    from cad.drawings import sheet as S
    from cad.partsdb import Project
    dwg = next(d for d in REG["drawings"] if d["number"] == "CT-106")
    got = []
    write = S.write
    S.write = lambda sh, path: got.append(sh)
    try:
        joint_sheet.ct106(Project(), None, None, None, REG, dwg)
    finally:
        S.write = write
    return got[0], [html.unescape(m[3]) for e in got[0].el if (m := _TEXT.match(e))]


def test_ct106_follows_ct105_in_the_set():
    live = [d["number"] for d in REG["drawings"] if not d.get("retired")]
    assert live.index("CT-106") == live.index("CT-105") + 1


def test_ct106_gives_the_datas_figures():
    """The gusset's length on its axis, the rail angles' length and the bolts under the XT centre crossmember come from
    the chassis data, so a change there shows on the sheet."""
    from cad.drawings.chassis_sheets import _layout
    ch = _layout(None, None)[0].chassis
    words = " ".join(_drawn()[1])
    g = ch.hinge_gussets()[0]
    assert f"{round(g['length'], 1):g} ON THE AXIS" in words
    rail = next(p for p in ch.panel_pieces() if p["use"] == "rail")
    assert f"{round(rail['length'], 1):g} ANGLE" in words
    sp = ch.shear_panels()[0]
    rails = next(f for f in ch.data["fittings"] if f["id"] == "CH-P17")["rails"]
    side = sum(1 for b in sp["bolts"] if b["group"] == "rail" and b["y"] > 0)
    assert f"{side} M{sp['fixing']['d']:g} AT {rails['pitch']:g}" in words


def test_ct106_gives_the_hinge_bars_runs_and_the_seams_from_the_data():
    """Review I2-128: detail E gives each of the hinge bar's weld runs a side by its ends inboard of the rail's inner
    face, none under the rail, with its fillet's leg and length, and detail F the twin crossmember's flare-V seams with
    their effective throat and process, welded and dressed flush before the bar is fitted, each from xt_hinges `bar` and
    `seam`, so the sheet follows the data if the welds change."""
    from cad.drawings.chassis_sheets import _layout
    ch = _layout(None, None)[0].chassis
    texts = _drawn()[1]
    words = " ".join(texts)
    b, seam = ch.data["xt_hinges"]["bar"], ch.data["xt_hinges"]["seam"]
    for e in sorted({round(c + s * b["run"] / 2, 1) for c in b["runs"] for s in (-1, 1)}):
        assert f"{e:g}" in texts, f"no ordinate at {e:g} from the rail's inner face"
    assert ", ".join(f"{c - b['run'] / 2:g} TO {c + b['run'] / 2:g}" for c in b["runs"]) in words
    assert "NO WELD UNDER THE RAIL" in texts and "NONE UNDER THE RAIL" in words
    assert f"{len(b['runs'])} RUNS A SIDE, AS DIMENSIONED" in texts and f"{b['run']:g}" in texts and f"{b['leg']:g}" in texts
    cm = next(m for m in ch.members if m.station == "XT centre" and m.role == "cm_xt")
    assert texts.count(f"{round(seam['throat_r'] * cm.sec.ro, 1):g}") >= 2        # the two flare-V symbols, top and bottom
    assert seam["rule"].upper() in words and "DRESS THE BOTTOM ONE FLUSH BEFORE THE HINGE BAR IS FITTED" in words

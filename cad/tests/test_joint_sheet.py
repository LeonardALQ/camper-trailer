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
    front = sum(1 for b in sp["bolts"] if b["group"] == "front")
    assert f"{front} M{sp['fixing']['d']:g} AT {sp['fixing']['front_pitch']:g}" in words

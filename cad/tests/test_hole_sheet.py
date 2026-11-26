"""I2-89: every hole for galvanising in the build's records stands once on the hole schedule CT-105, at the distances its
record gives, and once in the 3D model the viewer and the STEP files show, and CT-103's note 2 sends the fabricator to
CT-105. The sheets are drawn here from the build's records, as the drawings step draws them."""
from __future__ import annotations

import functools
import html
import json
import math
import re
from collections import Counter

import numpy as np
import yaml
from build123d import Compound, GeomType
from OCP.BRepAdaptor import BRepAdaptor_Surface

from cad import chassis_holes as CH
from cad.partsdb import ROOT

REG = yaml.safe_load((ROOT / "data" / "drawings.yaml").read_text(encoding="utf-8"))
HOLE_ID = re.compile(r"(?<![\w-])H-\d+(?![\w-])")
_TEXT = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)"[^>]*>(.*)</text>')


@functools.lru_cache(maxsize=None)
def drawn(number: str):
    """The sheet as the drawings step draws it, kept in memory: its texts as (x, y, text), y down as in the SVG."""
    from cad.drawings import chassis_sheets, hole_sheet
    from cad.drawings import sheet as S
    from cad.partsdb import Project
    dwg = next(d for d in REG["drawings"] if d["number"] == number)
    fn = {"CT-103": chassis_sheets.ct103, "CT-105": hole_sheet.ct105}[number]
    got = []
    write = S.write
    S.write = lambda sh, path: got.append(sh)
    try:
        fn(Project(), None, None, None, REG, dwg)
    finally:
        S.write = write
    texts = [(float(m[1]), float(m[2]), html.unescape(m[3])) for e in got[0].el if (m := _TEXT.match(e))]
    return got[0], texts


def _chassis():
    return json.loads((ROOT / "build" / "chassis" / "chassis.json").read_text(encoding="utf-8"))


def test_every_hole_record_stands_once_on_ct105():
    """Every hole for galvanising and every fixing's bolt or rivet nut hole (CH.bolt_records, I2-109) stands once."""
    recs = CH.records()
    assert len(recs) > 150 and CH.bolt_records()
    _, texts = drawn("CT-105")
    ids = Counter(t for _, _, t in texts if HOLE_ID.fullmatch(t))
    assert ids == Counter(h["id"] for h in recs + CH.bolt_records())
    stray = [t for _, _, t in texts if not HOLE_ID.fullmatch(t) and HOLE_ID.search(t)]
    assert not stray, stray


def test_ct105_gives_each_hole_its_records_size_and_distances():
    """Each row reads its record: the diameter, the distance along the web (u_web) and the height over the underside
    (z_under), or for a rail's own hole, which records its centre only, the distance from the rail's nearer end and the
    height over the rail's underside at that centre."""
    from cad.drawings.hole_sheet import COLS
    _, texts = drawn("CT-105")
    width = sum(c[1] for c in COLS)
    members = {m["id"]: m for m in _chassis()["members"]}
    for h in CH.records() + CH.bolt_records():
        x0, y0 = next((x, y) for x, y, t in texts if t == h["id"])
        row = [t for x, y, t in sorted(texts) if abs(y - y0) < 1e-6 and x0 <= x < x0 + width]
        assert len(row) == len(COLS), (h["id"], row)
        assert row[2] == f"{h['d']:g}", (h["id"], row)
        m = members[h["member"]] if h["member"] in members else None
        if "u_web" in h:
            along, over = h["u_web"], h["z_under"]
        else:
            ends = sorted((m["p0"][0], m["p1"][0]))
            along = min(h["x"] - ends[0], ends[1] - h["x"])
            over = None if CH.is_seam(h) else h["z"] - m["box"][2]          # the rail's underside
        assert row[5] == f"{round(along, 1):g}", (h["id"], row)
        assert row[6] == ("-" if over is None else f"{round(over, 1):g}"), (h["id"], row)


def test_ct105_cells_hold_their_text():
    """Every cell of the schedule holds its text, and each section's heading the column's width, so no rule crosses one."""
    from cad.drawings import sheet as S
    from cad.drawings.hole_sheet import COLS, LEFT, SIZE
    _, texts = drawn("CT-105")
    width = sum(c[1] for c in COLS)
    edges = [sum(c[1] for c in COLS[:i]) for i in range(len(COLS))]
    over = []
    for x, y, t in texts:
        col = next((x0 for x0 in LEFT if x0 <= x < x0 + width), None)
        if col is None or not 0 < 297.0 - y < 283.0:
            continue
        k = next((i for i, e in enumerate(edges) if abs(x - col - e - 0.6) < 1e-6), None)
        if k is None:
            continue
        room = width if k == 0 and not HOLE_ID.fullmatch(t) and t != COLS[0][0] else COLS[k][1]
        if S.text_mm(t, SIZE, t in [c[0] for c in COLS]) > room - 1.2:
            over.append(t)
    assert not over, over


def test_ct103_note_2_sends_the_fabricator_to_ct105():
    sh, _ = drawn("CT-103")
    lines = [t["t"] for t in sh.texts]
    start = next(i for i, t in enumerate(lines) if t.startswith("2. HOT-DIP GALVANISE"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("3. "))
    note = " ".join(t.strip() for t in lines[start:end])
    assert "CT-105" in note, note


def test_ct105_takes_its_place_in_the_set():
    live = [d for d in REG["drawings"] if not d.get("retired")]
    assert [d["sheet"] for d in live] == list(range(1, len(live) + 1)) and REG["sheets_total"] == len(live)
    numbers = [d["number"] for d in live]
    assert numbers.index("CT-105") == numbers.index("CT-104") + 1


# ------------------------------------------------------------------ the 3D model
def _bores(shape) -> list[tuple]:
    """Each cylindrical face of a solid as (radius, a point on its axis, its axis direction, its centre)."""
    out = []
    for f in shape.faces():
        if f.geom_type != GeomType.CYLINDER:
            continue
        cyl = BRepAdaptor_Surface(f.wrapped).Cylinder()
        ax = cyl.Axis()
        p, d, c = ax.Location(), ax.Direction(), f.center()
        out.append((cyl.Radius(), np.array((p.X(), p.Y(), p.Z())), np.array((d.X(), d.Y(), d.Z())), np.array((c.X, c.Y, c.Z))))
    return out


def _leaves(shape):
    kids = list(shape.children) if isinstance(shape, Compound) else []
    if kids:
        for k in kids:
            yield from _leaves(k)
    elif shape.solids():
        yield shape


def _meets(bores, c, n, r) -> bool:
    """A bore of radius r on the line through c along n, in the wall at c: its face within 10 mm of c along that line."""
    for rad, p, d, mid in bores:
        if abs(rad - r) < 0.01 and abs(abs(float(np.dot(d, n))) - 1.0) < 1e-3:
            off = (c - p) - np.dot(c - p, d) * d
            if float(np.linalg.norm(off)) < 0.5 and abs(float(np.dot(mid - c, d))) < 10.0:
                return True
    return False


def test_every_hole_record_is_cut_once_in_the_3d_model():
    """The chassis model the viewer and chassis.step are written from (chassis_compound) carries a bore for each record
    through each wall it names, and in no other solid, and a bore for each shock plate's vent through its plate. The model
    is built here for this test alone, since a compound takes its shapes from any compound built from them before."""
    from cad.tests.test_supported import _layouts
    from cad.trailer_model import TrailerModel, chassis_compound
    ch = _layouts()[0].chassis
    geo = {m.id: (m.p0, m.p1, m.depth_dir, m.sec.t) for m in ch.members}
    gsec = ch.sections[next(f for f in ch.data["fittings"] if f["id"] == "CH-P08")["section"]]
    geo.update({g["id"]: (g["p0"], g["p1"], (0.0, 0.0, 1.0), gsec.t) for g in ch.hinge_gussets()})
    solids = [_bores(s) for s in _leaves(chassis_compound(TrailerModel(_layouts()[0])))]
    short = []
    for h in CH.records():
        p0, p1, dd, t = geo[h["member"]]
        _, n, _, _ = CH.bore(h, p0, p1, dd, t)
        hits = sum(1 for b in solids if _meets(b, CH.centre(h), n, h["d"] / 2))
        if hits != len(CH.targets(h)):
            short.append((h["id"], hits, len(CH.targets(h))))
    assert not short, short
    vents = CH.plate_vents(ch)
    per_plate = len(next(o for o in ch.data["sealed_overlaps"] if o["id"] == "CH-P07")["vents"])
    assert len(vents) == per_plate * len(ch.shock_plates())
    for v in vents:
        assert sum(1 for b in solids if _meets(b, np.array(v["centre"]), np.array((1.0, 0.0, 0.0)), v["d"] / 2)) == 1, v

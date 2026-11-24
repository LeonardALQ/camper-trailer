"""The label overrun check on the built sheets (F6-04, fx10, I2-64): every sheet SVG in a folder, read in its drawing order,
for the text a mark shows through, the texts whose letters overlap and the masks that break a heavy line, sheet by sheet.

- A line hit is a stroked line, an arrowhead, a symbol circle or the frame that crosses the cores of a text's letters
  (cad/drawings/sheet.py text_core, each text measured in DejaVu Sans as CairoSVG draws it, up to its capitals' height,
  each line at its stroke's width) and shows: drawn after the text, or before it with no white mask or fill between
  them. A free label that a line crosses is masked by the sheet (sheet.knockouts), so the line breaks at its letters and
  is not a hit. A table cell's text is never masked, so a line through one is.
- A text overlap is two texts whose letters overlap, or a text that another text's mask or a white fill (a table, the
  title block) drawn after it covers. Here a text's letters run from its baseline up to its capitals' height.
- A mask break is a text's white mask drawn over a heavy line, one of sheet.HEAVY's 0.35 mm or more (medium, symbol,
  thick, cut, frame and the red fail line), so the mask cuts a gap in an outline or a run. A mask may break the thin
  lines under 0.35 mm (thin, hidden, centre, phantom, hatch, grey), as dimension text does.

    python -m cad.tools.overrun build/drawings [report.json]

prints each sheet's counts and the places, writes them to the report, and exits 1 when any sheet has any of the three."""
from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path

from cad.drawings.sheet import CAPS, HEAVY, _enters, _segments, text_core

_TEXT = re.compile(r"<text ([^>]*)>(.*)</text>")
_RECT = re.compile(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)" fill="#fff"([^>]*)/>')
_ROT = re.compile(r'rotate\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)')
G = 5.0
CLASSES = ("line_hits", "text_overlaps", "mask_breaks")


def _attr(a: str, name: str, default=None):
    m = re.search(rf'\b{name}="([^"]*)"', a)
    return m[1] if m else default


def _frame(rot: float, cx: float, cy: float):
    """The maps between the sheet and a frame rotated by `rot` degrees about (cx, cy), SVG coordinates."""
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def to_sheet(p):
        return (cx + (p[0] - cx) * ca - (p[1] - cy) * sa, cy + (p[0] - cx) * sa + (p[1] - cy) * ca)

    def to_local(p):
        return (cx + (p[0] - cx) * ca + (p[1] - cy) * sa, cy - (p[0] - cx) * sa + (p[1] - cy) * ca)
    return to_sheet, to_local


def read_sheet(svg: str) -> dict:
    """A sheet's elements in drawing order, its texts with their letters' cores and their letters' full height, and its
    white masks (`mask`, a text's knockout) and fills."""
    lines = svg.splitlines()
    i0 = next(n for n, e in enumerate(lines) if e.startswith("<svg")) + 1
    el = [e for e in lines[i0:] if not e.startswith("</svg")]
    texts, covers = [], []
    for n, e in enumerate(el):
        m = _TEXT.match(e)
        if m:
            a, raw = m[1], html.unescape(m[2])
            if not raw.strip():
                continue
            rot = _ROT.search(_attr(a, "transform", "") or "")
            t = dict(i=n, x=float(_attr(a, "x")), y=float(_attr(a, "y")), s=float(_attr(a, "font-size")),
                     anchor=_attr(a, "text-anchor", "start"), bold=_attr(a, "font-weight") == "bold", t=raw,
                     rot=float(rot[1]) if rot else 0.0, masked='class="masked"' in a)
            t["core"] = text_core(t)[2]
            t["to_sheet"], t["to_local"] = _frame(t["rot"], t["x"], t["y"])
            t["corners"] = _ring(t)
            t["letters"] = _ring(t, t["y"] - CAPS * t["s"], t["y"])
            t["bbox"] = _bounds(t["letters"])
            texts.append(t)
            continue
        m = _RECT.match(e)
        if m and n > 0:
            x, y, w, h = map(float, m.group(1, 2, 3, 4))
            rot = _ROT.search(m[5])
            covers.append(_cover(n, (x, x + w, y, y + h), *(map(float, rot.groups()) if rot else (0.0, 0.0, 0.0)), mask=True))
    segs, fills = _segments(el, every=True)
    covers += [_cover(n, b, 0.0, 0.0, 0.0) for b, n in fills]
    return dict(el=el, texts=texts, segs=segs, covers=covers)


def _bounds(ring: list) -> tuple:
    return (min(p[0] for p in ring), max(p[0] for p in ring), min(p[1] for p in ring), max(p[1] for p in ring))


def _cover(i: int, box: tuple, rot: float, cx: float, cy: float, mask: bool = False) -> dict:
    """A white mask or fill drawn at element i: its box in its own frame, rotated by `rot` about (cx, cy), its corners
    on the sheet and their bounds."""
    to_sheet, to_local = _frame(rot, cx, cy)
    ring = [to_sheet(p) for p in ((box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3]))]
    return dict(i=i, box=box, to_local=to_local, ring=ring, bbox=_bounds(ring), mask=mask)


def _near(a: tuple, b: tuple) -> bool:
    return not (a[1] < b[0] or b[1] < a[0] or a[3] < b[2] or b[3] < a[2])


def _covers(c: dict, t: dict) -> bool:
    """Does white cover c hide the whole of text t's letters' cores?"""
    x0, x1, y0, y1 = c["box"]
    return all(x0 - 1e-6 <= p[0] <= x1 + 1e-6 and y0 - 1e-6 <= p[1] <= y1 + 1e-6 for p in (c["to_local"](q) for q in t["corners"]))


def _apart(a: list, b: list) -> bool:
    """Separating axis test for two convex quadrilaterals given by their corners in order round them."""
    for poly in (a, b):
        for k in range(4):
            (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % 4]
            nx, ny = y1 - y2, x2 - x1
            pa = [nx * p[0] + ny * p[1] for p in a]
            pb = [nx * p[0] + ny * p[1] for p in b]
            if max(pa) <= min(pb) + 1e-9 or max(pb) <= min(pa) + 1e-9:
                return True
    return False


def _ring(t: dict, top: float | None = None, bottom: float | None = None) -> list:
    """A text's box on the sheet, its corners in order round it: its letters' cores, or the cores' width from `top` to
    `bottom` in its own frame."""
    c = t["core"]
    y0, y1 = (c[2], c[3]) if top is None else (top, bottom)
    return [t["to_sheet"](p) for p in ((c[0], y0), (c[1], y0), (c[1], y1), (c[0], y1))]


def _grid(segs: list) -> dict:
    grid: dict = {}
    for k, (p, q, _, _) in enumerate(segs):
        for gx in range(int(min(p[0], q[0]) // G), int(max(p[0], q[0]) // G) + 1):
            for gy in range(int(min(p[1], q[1]) // G), int(max(p[1], q[1]) // G) + 1):
                grid.setdefault((gx, gy), []).append(k)
    return grid


def _near_segs(grid: dict, bx: tuple, pad: float = 0.5) -> list:
    out = set()
    for gx in range(int((bx[0] - pad) // G), int((bx[1] + pad) // G) + 1):
        for gy in range(int((bx[2] - pad) // G), int((bx[3] + pad) // G) + 1):
            out.update(grid.get((gx, gy), ()))
    return sorted(out)


def _place(t: dict) -> dict:
    return dict(text=t["t"], at=[round(t["x"], 2), round(t["y"], 2)])


def check(svg: str) -> dict:
    """A sheet's line hits, text overlaps and mask breaks, each with the text and what crosses, covers or lies under it."""
    sh = read_sheet(svg)
    texts, segs, covers, el = sh["texts"], sh["segs"], sh["covers"], sh["el"]
    grid = _grid(segs)
    hits, overlaps, breaks = [], [], []
    for t in texts:
        bx, core = t["bbox"], t["core"]
        hidden = [c for c in covers if c["i"] > t["i"] and _near(c["bbox"], bx) and not _apart(c["ring"], t["letters"])]
        if hidden:
            overlaps.append(dict(_place(t), under=el[hidden[0]["i"]][:80]))
            continue
        for k in _near_segs(grid, bx):
            p, q, n, hw = segs[k]
            if not _enters(t["to_local"](p), t["to_local"](q), (core[0] - hw, core[1] + hw, core[2] - hw, core[3] + hw)):
                continue
            if n < t["i"] and any(n < c["i"] < t["i"] and _near(c["bbox"], bx) and _covers(c, t) for c in covers):
                continue
            hits.append(dict(_place(t), line=el[n][:80]))
            break
    for a_, t in enumerate(texts):
        for u in texts[a_ + 1:]:
            if _near(t["bbox"], u["bbox"]) and not _apart(t["letters"], u["letters"]):
                overlaps.append(dict(_place(t), other=u["t"], other_at=[round(u["x"], 2), round(u["y"], 2)]))
    by_index = {t["i"]: t for t in texts}
    for c in (c for c in covers if c["mask"]):
        t = by_index.get(c["i"] + 1)
        for k in _near_segs(grid, c["bbox"], 0.0):
            p, q, n, hw = segs[k]
            if n < c["i"] and 2 * hw >= HEAVY - 1e-9 and _enters(c["to_local"](p), c["to_local"](q), c["box"]):
                breaks.append(dict(_place(t) if t else dict(text="", at=[]), line=el[n][:80]))
                break
    return dict(line_hits=hits, text_overlaps=overlaps, mask_breaks=breaks)


def main(argv: list[str]) -> int:
    folder = Path(argv[0]) if argv else Path("build/drawings")
    sheets = sorted(folder.glob("*.svg"))
    if not sheets:
        print(f"no sheet SVGs in {folder}")
        return 1
    report, bad = {}, 0
    for f in sheets:
        r = check(f.read_text(encoding="utf-8"))
        report[f.stem] = r
        nh, no, nm = (len(r[k]) for k in CLASSES)
        bad += bool(nh or no or nm)
        print(f"{f.stem}: {nh} line hits, {no} text overlaps, {nm} mask breaks")
        for h in r["line_hits"]:
            print(f"  line hit: {h['text']!r} at {h['at']} by {h['line']}")
        for o in r["text_overlaps"]:
            print(f"  text overlap: {o['text']!r} at {o['at']} with " + (f"{o['other']!r} at {o['other_at']}" if "other" in o else f"a cover {o['under']}"))
        for m in r["mask_breaks"]:
            print(f"  mask break: {m['text']!r} at {m['at']} over {m['line']}")
    if len(argv) > 1:
        Path(argv[1]).write_text(json.dumps(report, indent=1), encoding="utf-8")
    n = {k: sum(len(r[k]) for r in report.values()) for k in CLASSES}
    print(f"overrun: {n['line_hits']} line hits, {n['text_overlaps']} text overlaps and {n['mask_breaks']} mask breaks "
          f"on {len(sheets)} sheets, {bad} with any")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

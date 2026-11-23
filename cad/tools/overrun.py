"""The label overrun check on the built sheets (F6-04, fx10): every sheet SVG in a folder, read in its drawing order,
for the text a mark shows through and the texts whose letters overlap, sheet by sheet.

- A line hit is a stroked line, an arrowhead, a symbol circle or the frame that crosses the cores of a text's letters
  (cad/drawings/sheet.py text_core, each text measured in DejaVu Sans as CairoSVG draws it, each line at its stroke's
  width) and shows: drawn after the text, or before it with no white mask or fill between them. A free label that a line
  crosses is masked by the sheet (sheet.knockouts), so the line breaks at its letters and is not a hit. A table cell's
  text is never masked, so a line through one is.
- A text overlap is two texts whose letters' cores overlap, or a text that another text's mask or a white fill (a table,
  the title block) drawn after it covers.

    python -m cad.tools.overrun build/drawings [report.json]

prints each sheet's counts and the places, writes them to the report, and exits 1 when any sheet has either."""
from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path

from cad.drawings.sheet import _enters, _segments, text_core

_TEXT = re.compile(r"<text ([^>]*)>(.*)</text>")
_RECT = re.compile(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)" fill="#fff"([^>]*)/>')
_ROT = re.compile(r'rotate\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)')
G = 5.0


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
    """A sheet's elements in drawing order, its texts with their letters' cores, and its white masks and fills."""
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
            corners = [t["to_sheet"]((u, v)) for u in t["core"][:2] for v in t["core"][2:]]
            t["corners"] = corners
            t["bbox"] = (min(c[0] for c in corners), max(c[0] for c in corners), min(c[1] for c in corners), max(c[1] for c in corners))
            texts.append(t)
            continue
        m = _RECT.match(e)
        if m and n > 0:
            x, y, w, h = map(float, m.group(1, 2, 3, 4))
            rot = _ROT.search(m[5])
            covers.append(_cover(n, (x, x + w, y, y + h), *(map(float, rot.groups()) if rot else (0.0, 0.0, 0.0))))
    segs, fills = _segments(el, every=True)
    covers += [_cover(n, b, 0.0, 0.0, 0.0) for b, n in fills]
    return dict(el=el, texts=texts, segs=segs, covers=covers)


def _cover(i: int, box: tuple, rot: float, cx: float, cy: float) -> dict:
    """A white mask or fill drawn at element i: its box in its own frame, rotated by `rot` about (cx, cy), its corners
    on the sheet and their bounds."""
    to_sheet, to_local = _frame(rot, cx, cy)
    ring = [to_sheet(p) for p in ((box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3]))]
    return dict(i=i, box=box, to_local=to_local, ring=ring,
                bbox=(min(p[0] for p in ring), max(p[0] for p in ring), min(p[1] for p in ring), max(p[1] for p in ring)))


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


def _ring(t: dict) -> list:
    c = t["core"]
    return [t["to_sheet"](p) for p in ((c[0], c[2]), (c[1], c[2]), (c[1], c[3]), (c[0], c[3]))]


def check(svg: str) -> dict:
    """A sheet's line hits and text overlaps, each with the text and what crosses or covers it."""
    sh = read_sheet(svg)
    texts, segs, covers, el = sh["texts"], sh["segs"], sh["covers"], sh["el"]
    grid: dict = {}
    for k, (p, q, _, _) in enumerate(segs):
        for gx in range(int(min(p[0], q[0]) // G), int(max(p[0], q[0]) // G) + 1):
            for gy in range(int(min(p[1], q[1]) // G), int(max(p[1], q[1]) // G) + 1):
                grid.setdefault((gx, gy), []).append(k)
    hits, overlaps = [], []
    for t in texts:
        bx, core = t["bbox"], t["core"]
        hidden = [c for c in covers if c["i"] > t["i"] and _near(c["bbox"], bx) and not _apart(c["ring"], _ring(t))]
        if hidden:
            overlaps.append(dict(text=t["t"], at=[round(t["x"], 2), round(t["y"], 2)], under=el[hidden[0]["i"]][:80]))
            continue
        cand = set()
        for gx in range(int((bx[0] - 0.5) // G), int((bx[1] + 0.5) // G) + 1):
            for gy in range(int((bx[2] - 0.5) // G), int((bx[3] + 0.5) // G) + 1):
                cand.update(grid.get((gx, gy), ()))
        for k in sorted(cand):
            p, q, n, hw = segs[k]
            if not _enters(t["to_local"](p), t["to_local"](q), (core[0] - hw, core[1] + hw, core[2] - hw, core[3] + hw)):
                continue
            if n < t["i"] and any(n < c["i"] < t["i"] and _near(c["bbox"], bx) and _covers(c, t) for c in covers):
                continue
            hits.append(dict(text=t["t"], at=[round(t["x"], 2), round(t["y"], 2)], line=el[n][:80]))
            break
    for a_, t in enumerate(texts):
        for u in texts[a_ + 1:]:
            if _near(t["bbox"], u["bbox"]) and not _apart(_ring(t), _ring(u)):
                overlaps.append(dict(text=t["t"], at=[round(t["x"], 2), round(t["y"], 2)], other=u["t"], other_at=[round(u["x"], 2), round(u["y"], 2)]))
    return dict(line_hits=hits, text_overlaps=overlaps)


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
        nh, no = len(r["line_hits"]), len(r["text_overlaps"])
        bad += bool(nh or no)
        print(f"{f.stem}: {nh} line hits, {no} text overlaps")
        for h in r["line_hits"]:
            print(f"  line hit: {h['text']!r} at {h['at']} by {h['line']}")
        for o in r["text_overlaps"]:
            print(f"  text overlap: {o['text']!r} at {o['at']} with " + (f"{o['other']!r} at {o['other_at']}" if "other" in o else f"a cover {o['under']}"))
    if len(argv) > 1:
        Path(argv[1]).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"overrun: {sum(len(r['line_hits']) for r in report.values())} line hits and "
          f"{sum(len(r['text_overlaps']) for r in report.values())} text overlaps on {len(sheets)} sheets, {bad} with either")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

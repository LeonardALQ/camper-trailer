"""A3 drawing sheet in the AS 1100 / ISO style used in the stack spike: frame, title block (TB-01 to TB-13),
revision table (REV-01), parts list (BOM-01, compact), third-angle symbol, dimensions, balloons and
hidden-line views from build123d / OCCT HLR. Output is SVG with real text, then PDF and PNG via CairoSVG."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

from build123d import Edge, GeomType, Keep, Plane, split
from OCP.BRepLib import BRepLib
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer

try:
    from build123d.topology.shape_core import downcast
except ImportError:  # pragma: no cover
    from build123d.topology.utils import downcast

GAP, EXT, TXT = 1.0, 2.0, 2.5  # projection-line gap and overshoot, dimension text height (mm)
FONT, PNG_PX = "DejaVu Sans", 3508
SYMBOL_R = 3.5   # mm: a circle this small is a symbol (gland, mount, balloon), never broken for a label, so its label moves
# REV-01's columns, their left edges from the table's left edge (mm), its text height and each cell's inset
REV_COLS = (("REV", 0.0), ("DATE", 10.0), ("DESCRIPTION", 30.0), ("DRAWN", 120.0), ("CHECKED", 140.0), ("APPROVED", 160.0))
REV_W, REV_TEXT, REV_PAD = 180.0, 1.9, 1.0


# ------------------------------------------------------------------ hidden-line removal
def hlr(shapes, view_dir, up, hidden=False) -> dict:
    """Orthographic hidden-line removal. view_dir points from the model to the viewer.
    Sharp edges and outlines only; smooth (tangent) edges are left out."""
    algo = HLRBRep_Algo()
    for s in shapes:
        algo.Add(s.wrapped)
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*view_dir))
    ax.SetYDirection(gp_Dir(*up))
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    res: dict[str, list] = {"visible": [], "hidden": []}
    comps = [("visible", h.VCompound()), ("visible", h.OutLineVCompound())]
    if hidden:
        comps += [("hidden", h.HCompound()), ("hidden", h.OutLineHCompound())]
    for key, comp in comps:
        if comp.IsNull():
            continue
        exp = TopExp_Explorer(comp, TopAbs_EDGE)
        while exp.More():
            e = downcast(exp.Current())
            BRepLib.BuildCurves3d_s(e, 1e-6)
            res[key].append(Edge(e))
            exp.Next()
    return res


def edge_pts(e):
    if e.geom_type == GeomType.LINE:
        us = [0.0, 1.0]
    else:
        n = max(8, min(120, int(e.length / 4)))
        us = [i / n for i in range(n + 1)]
    return [(v.X, v.Y) for v in (e.position_at(u) for u in us)]


def section(shapes, plane: Plane, keep=Keep.BOTTOM):
    """Cut shapes with a plane and keep one side (for sectional views)."""
    out = []
    for s in shapes:
        bb = s.bounding_box()
        o, n = plane.origin, plane.z_dir
        # quick reject: keep whole shapes that lie entirely on the kept side
        corners = [(x, y, z) for x in (bb.min.X, bb.max.X) for y in (bb.min.Y, bb.max.Y) for z in (bb.min.Z, bb.max.Z)]
        side = [(c[0] - o.X) * n.X + (c[1] - o.Y) * n.Y + (c[2] - o.Z) * n.Z for c in corners]
        below = keep == Keep.BOTTOM
        if (below and max(side) <= 0) or (not below and min(side) >= 0):
            out.append(s)
            continue
        if (below and min(side) >= 0) or (not below and max(side) <= 0):
            continue
        try:
            r = split(s, bisect_by=plane, keep=keep)
            if r is not None and r.volume > 1e-6:
                out.append(r)
        except Exception:
            pass
    return out


# ------------------------------------------------------------------ sheet
class Sheet:
    W, H = 420.0, 297.0
    STY = {
        "thick": 'stroke="#000" stroke-width="0.5" fill="none" stroke-linecap="round" stroke-linejoin="round"',
        "medium": 'stroke="#000" stroke-width="0.35" fill="none" stroke-linecap="round" stroke-linejoin="round"',
        "thin": 'stroke="#000" stroke-width="0.18" fill="none"',
        "sym": 'stroke="#000" stroke-width="0.35" fill="none"',
        "hidden": 'stroke="#000" stroke-width="0.18" fill="none" stroke-dasharray="1.5,0.8"',
        "centre": 'stroke="#000" stroke-width="0.18" fill="none" stroke-dasharray="6,1,1,1"',
        "phantom": 'stroke="#555" stroke-width="0.18" fill="none" stroke-dasharray="5,1,1,1,1,1"',
        "cut": 'stroke="#000" stroke-width="0.7" fill="none"',
        "frame": 'stroke="#000" stroke-width="0.7" fill="none" class="frame"',
        "hatch": 'stroke="#000" stroke-width="0.13" fill="none"',
        "fill": 'fill="#000" stroke="none"',
        "shade": 'fill="#c8c8c8" stroke="#000" stroke-width="0.25"',
        "white": 'fill="#fff" stroke="none"',
        "grey": 'stroke="#777" stroke-width="0.18" fill="none"',
        "fail": 'stroke="#c00" stroke-width="0.35" fill="none"',
    }

    def __init__(self):
        self.el: list[str] = []
        self.texts: list[dict] = []

    def _y(self, y):
        return self.H - y

    def path(self, pts, sty, closed=False):
        if len(pts) < 2:
            return
        d = "M" + " L".join(f"{x:.2f},{self._y(y):.2f}" for x, y in pts) + (" Z" if closed else "")
        self.el.append(f'<path d="{d}" {self.STY[sty]}/>')

    def line(self, x1, y1, x2, y2, sty="thin"):
        self.path([(x1, y1), (x2, y2)], sty)

    def rect(self, x1, y1, x2, y2, sty="thin"):
        self.path([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], sty, closed=True)

    def fillrect(self, x1, y1, x2, y2, sty="white"):
        self.path([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], sty, closed=True)

    def multipath(self, loops, sty="shade"):
        """Several closed loops in one path with even-odd fill (faces with holes)."""
        d = " ".join("M" + " L".join(f"{x:.2f},{self._y(y):.2f}" for x, y in pts) + " Z" for pts in loops if len(pts) > 2)
        if d:
            self.el.append(f'<path d="{d}" fill-rule="evenodd" {self.STY[sty]}/>')

    def circle(self, cx, cy, r, sty="thin"):
        self.el.append(f'<circle cx="{cx:.2f}" cy="{self._y(cy):.2f}" r="{r:.2f}" {self.STY[sty]}/>')

    def text(self, x, y, s, size=2.5, anchor="start", rot=0.0, bold=False, color="#000", cell=False):
        """`cell`: the text sits in a table's or the title block's cell, so a line through it is a layout fault, never
        broken for it. Any other text breaks the lines that cross its letters (`knockouts`)."""
        raw = str(s)
        s = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tr = f' transform="rotate({rot:.1f} {x:.2f} {self._y(y):.2f})"' if rot else ""
        w = ' font-weight="bold"' if bold else ""
        c = f' fill="{color}"' if color != "#000" else ""
        if not cell and raw.strip():
            self.texts.append(dict(i=len(self.el), x=x, y=self._y(y), s=size, anchor=anchor, rot=rot, bold=bold, t=raw, tr=tr))
        self.el.append(f'<text x="{x:.2f}" y="{self._y(y):.2f}" font-size="{size}" text-anchor="{anchor}" '
                       f'font-family="DejaVu Sans, Arial, sans-serif"{w}{c}{tr}>{s}</text>')

    def arrow(self, tip, direction, length=2.5, half=0.45):
        (x, y), (dx, dy) = tip, direction
        bx, by = x - dx * length, y - dy * length
        px, py = -dy * half, dx * half
        self.path([(x, y), (bx + px, by + py), (bx - px, by - py)], "fill", closed=True)

    def svg(self) -> str:
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W:g}mm" height="{self.H:g}mm" '
                f'viewBox="0 0 {self.W:g} {self.H:g}">\n'
                f'<rect x="0" y="0" width="{self.W:g}" height="{self.H:g}" fill="#fff"/>\n'
                + "\n".join(knockouts(self)) + "\n</svg>\n")


_METRICS: dict = {}


def text_mm(s, size, bold=False) -> float:
    """A text's advance on the sheet, mm, in the font CairoSVG draws it with: the wider of the PDF's unhinted metrics and
    the PNG's at its pixel size."""
    import cairocffi
    out = 0.0
    for png in (False, True):
        c = _METRICS.get((png, bold))
        if c is None:
            if png:
                c = cairocffi.Context(cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, 1, 1))
                c.scale(PNG_PX / Sheet.W, PNG_PX / Sheet.W)
            else:
                c = cairocffi.Context(cairocffi.RecordingSurface(cairocffi.CONTENT_COLOR_ALPHA, None))
            c.select_font_face(FONT, cairocffi.FONT_SLANT_NORMAL, cairocffi.FONT_WEIGHT_BOLD if bold else cairocffi.FONT_WEIGHT_NORMAL)
            _METRICS[(png, bold)] = c
        c.set_font_size(size if png else 100.0)
        out = max(out, c.text_extents(str(s))[4] * (1.0 if png else size / 100.0))
    return out


def wrap_mm(s, width, size, bold=False) -> list[str]:
    """Words into lines no wider than `width` mm at `size`."""
    out, cur = [], ""
    for w in str(s).split():
        if cur and text_mm(cur + " " + w, size, bold) > width:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])


def rev_room(col: str) -> float:
    """The width a REV-01 cell's text may take, mm: the column less its inset at both sides."""
    edges = [x for _, x in REV_COLS] + [REV_W]
    i = [c for c, _ in REV_COLS].index(col)
    return edges[i + 1] - edges[i] - 2 * REV_PAD


_PATH = re.compile(r'<path d="([^"]+)"([^>]*)/>')
_CIRCLE = re.compile(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"([^>]*)/>')


def _arc(p0, rx, ry, phi, large, sweep, p1, n=16):
    """An SVG arc from p0 to p1 as n points (the SVG specification's endpoint to centre conversion)."""
    if not rx or not ry:
        return [p1]
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    hx, hy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = c * hx + s * hy, -s * hx + c * hy
    rx, ry = abs(rx), abs(ry)
    lam = (x1 / rx) ** 2 + (y1 / ry) ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    den = (rx * y1) ** 2 + (ry * x1) ** 2
    k = math.sqrt(max(0.0, ((rx * ry) ** 2 - den) / den)) if den else 0.0
    k = -k if large == sweep else k
    cx1, cy1 = k * rx * y1 / ry, -k * ry * x1 / rx
    cx, cy = c * cx1 - s * cy1 + (p0[0] + p1[0]) / 2, s * cx1 + c * cy1 + (p0[1] + p1[1]) / 2
    t0 = math.atan2((y1 - cy1) / ry, (x1 - cx1) / rx)
    dt = math.atan2((-y1 - cy1) / ry, (-x1 - cx1) / rx) - t0
    if sweep and dt < 0:
        dt += 2 * math.pi
    elif not sweep and dt > 0:
        dt -= 2 * math.pi
    return [(cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
            for t in (t0 + dt * i / n for i in range(1, n + 1))]


def _segments(el, every: bool = False) -> tuple[list, list]:
    """Every stroked straight piece on the sheet in SVG coordinates as (p, q, element index, half its stroke width), arcs
    and circles as chords, the frame's left out, and the boxes of the white fills (the title block's, the tables') as
    (box, element index). `every` keeps the frame, the symbol circles and the outlines of the black fills too (the
    arrowheads), for the overrun check (cad/tools/overrun.py), which finds every mark that shows through a text."""
    out, fills = [], []
    for n, e in enumerate(el):
        if e.startswith("<path"):
            m = _PATH.match(e)
            if not m:
                continue
            if 'fill="#fff" stroke="none"' in m[2]:
                xs, ys = [float(v) for v in re.findall(r"([-\d.]+),", m[1])], [float(v) for v in re.findall(r",([-\d.]+)", m[1])]
                fills.append(((min(xs), max(xs), min(ys), max(ys)), n))
            black = every and 'fill="#000" stroke="none"' in m[2]
            if not black and ('stroke="none"' in m[2] or "stroke=" not in m[2] or ('class="frame"' in m[2] and not every)):
                continue
            sw = re.search(r'stroke-width="([\d.]+)"', m[2])
            hw = 0.0 if black else float(sw[1]) / 2 if sw else 0.5
            tok = re.findall(r"[MLAZ]|[-\d.]+", m[1])
            pts, start, cmd, i = [], None, "M", 0
            while i < len(tok):
                t = tok[i]
                if t in "MLAZ":
                    cmd, i = t, i + 1
                    if t == "Z" and pts:
                        pts.append(start)
                        out += [(p, q, n, hw) for p, q in zip(pts, pts[1:])]
                        pts = []
                    continue
                if cmd == "A":
                    rx, ry, phi, large, sweep, x, y = map(float, tok[i:i + 7])
                    pts += _arc(pts[-1], rx, ry, phi, int(large), int(sweep), (x, y))
                    i += 7
                    continue
                p = (float(tok[i]), float(tok[i + 1]))
                if cmd == "M":
                    out += [(a, b, n, hw) for a, b in zip(pts, pts[1:])]
                    pts, start, cmd = [p], p, "L"
                else:
                    pts.append(p)
                i += 2
            out += [(p, q, n, hw) for p, q in zip(pts, pts[1:])]
        elif e.startswith("<circle"):
            m = _CIRCLE.match(e)
            if not m or (('stroke="none"' in m[4] or float(m[3]) <= SYMBOL_R) and not every):
                continue
            sw = re.search(r'stroke-width="([\d.]+)"', m[4])
            cx, cy, r = float(m[1]), float(m[2]), float(m[3])
            p = [(cx + r * math.cos(math.pi * k / 16), cy + r * math.sin(math.pi * k / 16)) for k in range(33)]
            out += [(a, b, n, float(sw[1]) / 2 if sw else 0.09) for a, b in zip(p, p[1:])]
    return out, fills


def _enters(p, q, box) -> bool:
    """Liang-Barsky: does the segment p-q enter the box (x0, x1, y0, y1)?"""
    u0, u1 = 0.0, 1.0
    dx, dy = q[0] - p[0], q[1] - p[1]
    for a, b in ((-dx, p[0] - box[0]), (dx, box[1] - p[0]), (-dy, p[1] - box[2]), (dy, box[3] - p[1])):
        if abs(a) < 1e-12:
            if b < 0:
                return False
        elif a < 0:
            u0 = max(u0, b / a)
        else:
            u1 = min(u1, b / a)
        if u0 > u1:
            return False
    return True


def text_core(t: dict) -> tuple[float, float, tuple]:
    """A text's start and its letters' advance on the sheet, and the box the cores of its letters fill, in its own
    unrotated frame in SVG coordinates (x0, x1, y0, y1): 0.12 of its size in from each end, from 0.62 to 0.06 of its
    size above the baseline, so a line that only grazes an ascender, a descender or the space round it is not counted.
    `t` holds the text (t), its anchor point (x, y), size (s), anchor and weight (bold)."""
    s, txt = t["s"], t["t"]
    lead = len(txt) - len(txt.lstrip())
    w = text_mm(txt.strip(), s, t["bold"])
    full = text_mm(txt, s, t["bold"])
    x0 = t["x"] if t["anchor"] == "start" else t["x"] - full / 2 if t["anchor"] == "middle" else t["x"] - full
    x0 += text_mm(" " * lead, s, t["bold"]) if lead else 0.0
    return x0, w, (x0 + 0.12 * s, x0 + w - 0.12 * s, t["y"] - 0.62 * s, t["y"] - 0.06 * s)


def knockouts(sh) -> list[str]:
    """The sheet's elements with a white mask behind every text that a stroked line crosses, the text and its mask moved
    to just after the last line that crosses it, so the line breaks at the lettering. Cell texts, the frame and a text
    that a later white fill covers (under the title block or a table) are left as drawn."""
    if not sh.texts:
        return sh.el
    (segs, fills), grid, G = _segments(sh.el), {}, 5.0
    for k, (p, q, _, _) in enumerate(segs):
        for gx in range(int(min(p[0], q[0]) // G), int(max(p[0], q[0]) // G) + 1):
            for gy in range(int(min(p[1], q[1]) // G), int(max(p[1], q[1]) // G) + 1):
                grid.setdefault((gx, gy), []).append(k)
    masked = {}
    for t in sh.texts:
        s = t["s"]
        x0, w, core = text_core(t)
        a = math.radians(t["rot"])
        ca, sa = math.cos(a), math.sin(a)

        def to_sheet(u, v):
            return (t["x"] + (u - t["x"]) * ca - (v - t["y"]) * sa, t["y"] + (u - t["x"]) * sa + (v - t["y"]) * ca)

        def to_local(p):
            return (t["x"] + (p[0] - t["x"]) * ca + (p[1] - t["y"]) * sa, t["y"] - (p[0] - t["x"]) * sa + (p[1] - t["y"]) * ca)
        cs = [to_sheet(u, v) for u in core[:2] for v in core[2:]]
        bx = (min(c[0] for c in cs), max(c[0] for c in cs), min(c[1] for c in cs), max(c[1] for c in cs))
        if any(n > t["i"] and f[0] < bx[1] and bx[0] < f[1] and f[2] < bx[3] and bx[2] < f[3] for f, n in fills):
            continue
        cand = set()
        for gx in range(int((bx[0] - 0.5) // G), int((bx[1] + 0.5) // G) + 1):
            for gy in range(int((bx[2] - 0.5) // G), int((bx[3] + 0.5) // G) + 1):
                cand.update(grid.get((gx, gy), ()))
        hits = [n for p, q, n, hw in (segs[k] for k in cand)
                if _enters(to_local(p), to_local(q), (core[0] - hw, core[1] + hw, core[2] - hw, core[3] + hw))]
        if hits:
            masked[t["i"]] = (max(max(hits), t["i"]), f'<rect x="{x0 - 0.3:.2f}" y="{t["y"] - 0.78 * s - 0.2:.2f}" '
                              f'width="{w + 0.6:.2f}" height="{1.02 * s + 0.4:.2f}" fill="#fff"{t["tr"]}/>')
    if not masked:
        return sh.el
    after: dict = {}
    for i, (last, m) in masked.items():
        after.setdefault(last, []).append(m + "\n" + sh.el[i].replace("<text ", '<text class="masked" ', 1))
    out = []
    for i, e in enumerate(sh.el):
        if i not in masked:
            out.append(e)
        out += after.get(i, [])
    return out


# ------------------------------------------------------------------ views
@dataclass
class View:
    """Orthographic view: model point -> sheet point. right/up are the model directions that map to the
    sheet's +x and +y. ox, oy is where the model point `anchor` lands on the sheet."""
    sheet: Sheet
    view_dir: tuple
    up: tuple
    scale: float
    ox: float
    oy: float
    anchor: tuple = (0.0, 0.0, 0.0)

    @property
    def right(self):
        d, u = self.view_dir, self.up
        # right = up x view_dir (view_dir points towards the viewer)
        return (u[1] * d[2] - u[2] * d[1], u[2] * d[0] - u[0] * d[2], u[0] * d[1] - u[1] * d[0])

    def p(self, x, y, z):
        r, u, a = self.right, self.up, self.anchor
        dx, dy, dz = x - a[0], y - a[1], z - a[2]
        return (self.ox + (dx * r[0] + dy * r[1] + dz * r[2]) / self.scale,
                self.oy + (dx * u[0] + dy * u[1] + dz * u[2]) / self.scale)

    def draw(self, shapes, hidden=False, sty="thick", hsty="hidden", clip=None):
        res = hlr(shapes, self.view_dir, self.up, hidden=hidden)
        # HLR works in the projector frame: its x is the projector's x (right) and y is up, origin at model 0
        a = self.anchor
        r, u = self.right, self.up
        ax = a[0] * r[0] + a[1] * r[1] + a[2] * r[2]
        ay = a[0] * u[0] + a[1] * u[1] + a[2] * u[2]
        for key, st in (("visible", sty), ("hidden", hsty)):
            for e in res[key]:
                pts = [(self.ox + (x - ax) / self.scale, self.oy + (y - ay) / self.scale) for x, y in edge_pts(e)]
                self.sheet.path(pts, st)
        return res


# ------------------------------------------------------------------ dimensions and annotation
def hdim(sh, x1, y1, x2, y2, yd, text, size=TXT, ext=True):
    """Horizontal dimension: thin lines, filled arrows, text above the line (AS 1100.201 / ISO 129)."""
    if ext:
        for x, y in ((x1, y1), (x2, y2)):
            s = 1 if yd > y else -1
            sh.line(x, y + s * GAP, x, yd + s * EXT)
    sh.line(x1, yd, x2, yd)
    lo, hi = min(x1, x2), max(x1, x2)
    if hi - lo > 7:
        sh.arrow((lo, yd), (-1, 0))
        sh.arrow((hi, yd), (1, 0))
    else:  # arrows outside for short dimensions
        sh.line(lo - 5, yd, hi + 5, yd)
        sh.arrow((lo, yd), (1, 0))
        sh.arrow((hi, yd), (-1, 0))
    sh.text((x1 + x2) / 2, yd + 0.8, text, size, "middle")


def vdim(sh, x1, y1, x2, y2, xd, text, size=TXT, ext=True):
    if ext:
        for x, y in ((x1, y1), (x2, y2)):
            s = 1 if xd > x else -1
            sh.line(x + s * GAP, y, xd + s * EXT, y)
    sh.line(xd, y1, xd, y2)
    lo, hi = min(y1, y2), max(y1, y2)
    if hi - lo > 7:
        sh.arrow((xd, lo), (0, -1))
        sh.arrow((xd, hi), (0, 1))
    else:
        sh.line(xd, lo - 5, xd, hi + 5)
        sh.arrow((xd, lo), (0, 1))
        sh.arrow((xd, hi), (0, -1))
    sh.text(xd - 0.8, (lo + hi) / 2, text, size, "middle", rot=-90)


def ordinate_v(sh, x_feat, ys, x_line, labels, size=TXT, base_label="0"):
    """Vertical ordinate dimensions from a datum: one leader per level, value at the end (DIM-02)."""
    for y, lab in zip(ys, labels):
        sh.line(x_feat + GAP, y, x_line, y)
        sh.text(x_line + 1.0, y - 0.9, lab, size)


def ordinate_h(sh, xs, y_feat, y_line, labels, size=TXT, up=True):
    for x, lab in zip(xs, labels):
        sh.line(x, y_feat + (GAP if up else -GAP), x, y_line)
        sh.text(x + 0.9, y_line + (1.0 if up else -1.0), lab, size, "start" if up else "end", rot=-90 if up else -90)


def leader(sh, tip, elbow, text, lines=None, size=2.2):
    (tx, ty), (ex, ey) = tip, elbow
    sh.line(tx, ty, ex, ey)
    L = math.hypot(tx - ex, ty - ey) or 1
    sh.arrow((tx, ty), ((tx - ex) / L, (ty - ey) / L), 2.0, 0.4)
    side = 1 if ex >= tx else -1
    sh.line(ex, ey, ex + 3 * side, ey)
    for i, t in enumerate([text] + (lines or [])):
        sh.text(ex + 4 * side, ey - 0.8 - i * (size + 0.8), t, size, "start" if side > 0 else "end")


def balloon(sh, tip, centre, label, r=3.2):
    (tx, ty), (cx, cy) = tip, centre
    L = math.hypot(cx - tx, cy - ty) or 1
    ux, uy = (cx - tx) / L, (cy - ty) / L
    sh.line(tx, ty, cx - ux * r, cy - uy * r)
    sh.circle(tx, ty, 0.45, "fill")
    sh.circle(cx, cy, r, "medium")
    sh.text(cx, cy - 1.0, label, 2.8 if len(label) < 3 else 2.2, "middle")


def third_angle_symbol(sh, x, y, h=8.0):
    """Third-angle symbol: truncated cone side view on the left, end-view circles on the right."""
    sh.path([(x, y - h / 2), (x + h, y - h / 4), (x + h, y + h / 4), (x, y + h / 2)], "sym", closed=True)
    cx = x + h + 3 + h / 2
    sh.circle(cx, y, h / 2, "sym")
    sh.circle(cx, y, h / 4, "sym")
    sh.line(x - 1.5, y, cx + h / 2 + 1.5, y, "centre")
    sh.line(cx, y - h / 2 - 1.5, cx, y + h / 2 + 1.5, "centre")


def view_label(sh, x, y, title, scale):
    sh.text(x, y, title, 3.2, "middle", bold=True)
    sh.text(x, y - 4.0, f"SCALE 1:{scale:g}", 2.3, "middle")


def cut_marker(sh, p0, p1, look, letter):
    """Cutting plane: chain line with thick ends, arrows showing the viewing direction, and the letters."""
    sh.line(p0[0], p0[1], p1[0], p1[1], "centre")
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    for (x, y), s in ((p0, 1), (p1, -1)):
        sh.line(x, y, x + ux * 4 * s, y + uy * 4 * s, "cut")
        tip = (x + look[0] * 5, y + look[1] * 5)
        sh.line(x, y, tip[0], tip[1], "medium")
        sh.arrow(tip, look, 2.2, 0.5)
        sh.text(tip[0] + look[0] * 2.5 - ux * 2.5 * s, tip[1] + look[1] * 2.5 - uy * 2.5 * s - 1.2, letter, 3.2, "middle", bold=True)


def table(sh, x, y, cols, rows, size=1.8, row_h=3.4, header=True, title=None):
    """Simple ruled table. cols: list of (header, width). Returns the y below the table."""
    w = sum(c[1] for c in cols)
    if title:
        sh.text(x, y + 1.5, title, 2.3, bold=True)
    yy = y
    n = len(rows) + (1 if header else 0)
    sh.rect(x, y - n * row_h, x + w, y, "medium")
    if header:
        cx = x
        for h, cw in cols:
            sh.text(cx + 0.8, yy - row_h + 0.9, h, size, bold=True, cell=True)
            cx += cw
        yy -= row_h
        sh.line(x, yy, x + w, yy, "thin")
    for r in rows:
        cx = x
        for (h, cw), v in zip(cols, r):
            color = "#000"
            if isinstance(v, tuple):
                v, color = v
            sh.text(cx + 0.8, yy - row_h + 0.9, str(v), size, color=color, cell=True)
            cx += cw
        yy -= row_h
        sh.line(x, yy, x + w, yy, "thin")
    cx = x
    for h, cw in cols[:-1]:
        cx += cw
        sh.line(cx, y, cx, y - n * row_h, "thin")
    return y - n * row_h


def hatch_rect(sh, x1, y1, x2, y2, pitch=1.2):
    """45 degree hatching inside a rectangle (sections of thin made parts)."""
    lo_x, hi_x, lo_y, hi_y = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
    w, h = hi_x - lo_x, hi_y - lo_y
    k = -h
    while k < w:
        a = (lo_x + max(k, 0), lo_y + max(-k, 0))
        b_len = min(w - max(k, 0), h - max(-k, 0))
        if b_len > 0:
            sh.line(a[0], a[1], a[0] + b_len, a[1] + b_len, "hatch")
        k += pitch


# ------------------------------------------------------------------ frame, title block, revisions, parts list
def frame(sh):
    sh.rect(20, 10, 410, 287, "frame")
    # centring marks
    for x, y1, y2 in ((210, 287, 292), (210, 5, 10)):
        sh.line(x, y1, x, y2, "medium")
    for y, x1, x2 in ((148.5, 410, 415), (148.5, 15, 20)):
        sh.line(x1, y, x2, y, "medium")


def title_block(sh, *, owner, project, number, title, subtitle, rev, status, date, drawn, checked, approved,
                engineer, sheet_no, sheets, size, scale, material, mass_note, model_ref, git, weld_note=None):
    """180 x 56 title block, bottom right (ISO 7200 width), fields TB-01 to TB-13."""
    x0, x1, y0, y1 = 230.0, 410.0, 10.0, 66.0
    n0 = len(sh.texts)
    sh.fillrect(x0, y0, x1, y1)
    sh.rect(x0, y0, x1, y1, "frame")
    lab = lambda x, y, t: sh.text(x, y, t, 1.6, color="#333")  # noqa: E731
    # row lines
    for y in (52, 42, 32, 22):
        sh.line(x0, y, x1, y)
    # row 1: title and drawing number
    sh.line(345, 52, 345, 66)
    lab(232, 63.6, "TITLE (TB-03)")
    sh.text(232, 58.3, title.upper(), 3.2, bold=True)
    sh.text(232, 54.0, subtitle, 2.0)
    lab(347, 63.6, "DRAWING No. (TB-02)")
    sh.text(347, 56.0, number, 5.0, bold=True)
    # row 2: rev, status, size, scale, sheet, projection
    for x in (250, 285, 302, 322, 350):
        sh.line(x, 42, x, 52)
    lab(232, 49.8, "REV (TB-04)")
    sh.text(236, 44.0, rev, 4.0, bold=True)
    lab(252, 49.8, "STATUS (TB-05)")
    sh.text(252, 44.4, status, 3.4, bold=True, color="#b00")
    lab(287, 49.8, "SIZE")
    sh.text(287, 44.4, size, 3.0)
    lab(304, 49.8, "SCALE")
    sh.text(304, 44.4, f"1:{scale:g}" if isinstance(scale, (int, float)) else str(scale), 3.0)
    lab(324, 49.8, "SHEET (TB-08)")
    sh.text(324, 44.4, f"{sheet_no} of {sheets}", 3.0)
    lab(352, 49.8, "PROJECTION (TB-09)")
    sh.text(352, 44.6, "THIRD ANGLE", 1.9)
    third_angle_symbol(sh, 382, 46.0, 5.5)
    # row 3: drawn, checked, approved, engineer, date
    for x in (270, 305, 340, 375):
        sh.line(x, 32, x, 42)
    lab(232, 39.8, "DRAWN (TB-07)")
    sh.text(232, 34.0, drawn, 2.2)
    lab(272, 39.8, "CHECKED")
    sh.text(272, 34.0, checked or "-", 2.2)
    lab(307, 39.8, "APPROVED")
    sh.text(307, 34.0, approved or "-", 2.2)
    lab(342, 39.8, "ENGINEER REVIEW")
    sh.text(342, 34.0, engineer, 2.0)
    lab(377, 39.8, "DATE OF ISSUE (TB-06)")
    sh.text(377, 34.0, date, 2.2)
    # row 4: owner, project, material
    sh.line(320, 22, 320, 32)
    lab(232, 29.8, "OWNER AND PROJECT (TB-01)")
    sh.text(232, 26.0, owner, 2.0)
    sh.text(232, 23.2, project, 1.9)
    lab(322, 29.8, "MATERIAL AND FINISH (TB-10)")
    sh.text(322, 25.0, material, 2.2)
    # row 5: notes
    sh.text(232, 18.6, "ALL DIMENSIONS IN mm. DO NOT SCALE. GENERAL TOLERANCE ISO 2768-c UNLESS STATED (TO BE CONFIRMED).", 1.75)
    sh.text(232, 15.6, (weld_note or "NO WELDS ON THIS SHEET (WELD SYMBOLS WOULD BE TO AS 1101.3). ") + mass_note, 1.75)
    sh.text(232, 12.4, f"MODEL: {model_ref}  DATA REV {git}  (TB-12)", 1.75)
    del sh.texts[n0:]


def revision_table(sh, revisions, x0=230.0, x1=410.0, ytop=287.0, max_rows=7):
    """REV-01: revision, date, description, drawn, checked, approved. Header row, then one 5 mm row each. Only the
    latest `max_rows` revisions are listed; the drawing register (site Drawings page) keeps every one."""
    revisions = list(revisions)[-max_rows:]
    n = max(1, len(revisions))
    yb = ytop - 10 - 5 * n
    sh.fillrect(x0, yb, x1, ytop)
    sh.rect(x0, yb, x1, ytop, "medium")
    sh.text(x0 + 2, ytop - 3.6, "REVISIONS (REV-01)", 2.2, bold=True)
    sh.line(x0, ytop - 5, x1, ytop - 5)
    cols = [(x0 + dx, labl) for labl, dx in REV_COLS]
    for cx, labl in cols:
        if cx != x0:
            sh.line(cx, yb, cx, ytop - 5)
        sh.text(cx + REV_PAD, ytop - 8.6, labl, 1.7, cell=True)
    sh.line(x0, ytop - 10, x1, ytop - 10)
    for i, r in enumerate(revisions):
        y = ytop - 13.8 - i * 5
        if i:
            sh.line(x0, ytop - 10 - 5 * i, x1, ytop - 10 - 5 * i)
        vals = [r["rev"], r["date"], r["description"], r["drawn"], r["checked"] or "-", r["approved"] or "-"]
        for (cx, _), v in zip(cols, vals):
            sh.text(cx + REV_PAD, y, v, REV_TEXT, cell=True)
    return yb


def parts_list(sh, rows, x0=230.0, x1=410.0, ybase=66.0, row_h=4.6, title="PARTS LIST (BOM-01)", tags=None):
    """Rows: dicts with item, part, description, qty, mass, supplier. Header at the bottom, items upwards.
    `tags` maps an item number to a revision letter, drawn as a revision triangle left of that row."""
    cols = [(x0, "ITEM", 9), (x0 + 9, "PART No.", 17), (x0 + 26, "DESCRIPTION", 70), (x0 + 96, "QTY", 18),
            (x0 + 114, "kg", 12), (x0 + 126, "SUPPLIER / NOTE", 54)]
    n = len(rows)
    top = ybase + row_h * (n + 1)
    sh.fillrect(x0, ybase, x1, top + 5)
    sh.rect(x0, ybase, x1, top, "medium")
    sh.text(x0 + 1, top + 1.3, title, 2.2, bold=True)
    for i in range(1, n + 1):
        sh.line(x0, ybase + row_h * i, x1, ybase + row_h * i, "thin")
    for cx, lab, _ in cols[1:]:
        sh.line(cx, ybase, cx, top, "thin")
    for cx, lab, _ in cols:
        sh.text(cx + 0.8, ybase + 1.5, lab, 1.7, bold=True, cell=True)
    for i, r in enumerate(rows):
        yb = ybase + row_h * (i + 1) + 1.4
        vals = [r["item"], r["part"], r["description"], r["qty"], r["mass"], r.get("supplier", "")]
        for (cx, _, w), v in zip(cols, vals):
            s = str(v)
            maxc = int(w / 1.05)
            if len(s) > maxc:
                s = s[: maxc - 1] + "…"
            sh.text(cx + 0.8, yb, s, 1.75, cell=True)
        if tags and r["item"] in tags:
            rev_tag(sh, x0 - 3.6, ybase + row_h * (i + 1.5) - 0.4, tags[r["item"]], 4.2)
    return top + 5


def notes(sh, x, y, lines, title="NOTES", size=2.0, width_chars=95):
    """Numbered, wrapped notes. Returns (bottom y, [baseline y of each note's first line])."""
    sh.text(x, y, title, 2.5, bold=True)
    yy = y - 4.2
    starts = []
    for i, t in enumerate(lines, 1):
        starts.append(yy)
        words, cur, first = t.split(), "", True
        for w in words:
            if len(cur) + len(w) + 1 > width_chars:
                sh.text(x, yy, (f"{i}. " if first else "   ") + cur, size)
                yy -= size + 1.0
                cur, first = w, False
            else:
                cur = (cur + " " + w).strip()
        sh.text(x, yy, (f"{i}. " if first else "   ") + cur, size)
        yy -= size + 1.3
    return yy, starts


def rev_tag(sh, x, y, rev, size=5.0):
    """Revision triangle (REV-03): an equilateral triangle centred on (x, y) with the revision letter."""
    h = size * math.sqrt(3) / 2
    sh.path([(x - size / 2, y - h / 3), (x + size / 2, y - h / 3), (x, y + 2 * h / 3)], "medium", closed=True)
    sh.text(x, y - h / 3 + 0.7, rev, 2.3, "middle", bold=True)


def revision_cloud(sh, x0, y0, x1, y1, rev, tag_at="tr", bump=3.0):
    """Revision cloud round a changed area (REV-03): scalloped outline with outward bulges and a tag."""
    lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    corners = [(lo_x, hi_y), (hi_x, hi_y), (hi_x, lo_y), (lo_x, lo_y)]  # clockwise on paper, starting top left
    pts = []
    for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
        n = max(1, round(math.hypot(bx - ax, by - ay) / bump))
        pts.extend((ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n))
    d = f"M{pts[0][0]:.2f},{sh._y(pts[0][1]):.2f}"
    for (px, py), (qx, qy) in zip(pts, pts[1:] + pts[:1]):
        r = math.hypot(qx - px, qy - py) / 2 * 1.05
        d += f" A{r:.2f},{r:.2f} 0 0,1 {qx:.2f},{sh._y(qy):.2f}"
    sh.el.append(f'<path d="{d}" {sh.STY["medium"]}/>')
    tx, ty = {"tr": (hi_x + 1.5, hi_y + 1.5), "tl": (lo_x - 1.5, hi_y + 1.5),
              "br": (hi_x + 1.5, lo_y - 1.5), "bl": (lo_x - 1.5, lo_y - 1.5)}[tag_at]
    rev_tag(sh, tx, ty, rev)


def write(sh, out_svg):
    import cairosvg
    svg = sh.svg()
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text(svg, encoding="utf-8")
    cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(out_svg.with_suffix(".pdf")))
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out_svg.with_suffix(".png")), output_width=3508)

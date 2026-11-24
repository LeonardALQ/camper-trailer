"""A3 drawing sheet in the AS 1100 / ISO style used in the stack spike: frame, title block (TB-01 to TB-13),
revision table (REV-01), parts list (BOM-01, compact), third-angle symbol, dimensions, balloons and
hidden-line views from build123d / OCCT HLR. Output is SVG with real text, then PDF and PNG via CairoSVG."""
from __future__ import annotations

import html
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
CAPS = 0.73       # DejaVu Sans capitals stand 1,493 of its 2,048 units, 0.729 of the size, over the baseline
HEAVY = 0.35      # mm: a line this wide or wider (medium, symbol, thick, cut, frame, fail) is never broken by a text's mask
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
        self.leads: dict[int, list[tuple]] = {}    # a text's element: the leader parts that move with it (clear_labels)

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

    def text(self, x, y, s, size=2.5, anchor="start", rot=0.0, bold=False, color="#000", cell=False, names=None):
        """`cell`: the text sits in a table's or the title block's cell, so a line through it is a layout fault, never
        broken for it. Any other text breaks the lines that cross its letters (`knockouts`). `names` is what the label
        names on the sheet, where the sheet knows it: a point (x, y) on it, its box (x0, y0, x1, y1) or a symbol's circle
        (cx, cy, r). A label that clear_labels moves off its place gets a leader to it, and one with no `names` stays."""
        raw = str(s)
        s = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tr = f' transform="rotate({rot:.1f} {x:.2f} {self._y(y):.2f})"' if rot else ""
        w = ' font-weight="bold"' if bold else ""
        c = f' fill="{color}"' if color != "#000" else ""
        if not cell and raw.strip():
            self.texts.append(dict(i=len(self.el), x=x, y=self._y(y), s=size, anchor=anchor, rot=rot, bold=bold, t=raw, tr=tr,
                                   names=self.target(names)))
        self.el.append(f'<text x="{x:.2f}" y="{self._y(y):.2f}" font-size="{size}" text-anchor="{anchor}" '
                       f'font-family="DejaVu Sans, Arial, sans-serif"{w}{c}{tr}>{s}</text>')

    def target(self, names):
        """What a label names, from sheet coordinates (y up) to the sheet's SVG ones: ("point", x, y), ("box", x0, x1,
        y0, y1) or ("circle", cx, cy, r), or None."""
        if names is None:
            return None
        if len(names) == 2:
            return ("point", float(names[0]), self._y(names[1]))
        if len(names) == 3:
            return ("circle", float(names[0]), self._y(names[1]), float(names[2]))
        x0, y0, x1, y1 = names
        return ("box", min(x0, x1), max(x0, x1), self._y(max(y0, y1)), self._y(min(y0, y1)))

    def lead(self, pts, names=None):
        """A thin leader through sheet points `pts`, from its label to what it names: marked as a leader in the SVG, with
        what it names (`names`, as Sheet.text takes it) for the overrun check, which finds a leader that ends off what
        its label names, two leaders that cross and a leader through a symbol."""
        if len(pts) < 2:
            return
        self.path(pts, "thin")
        self.el[-1] = self.el[-1][:-2] + lead_attr(self.target(names)) + "/>"

    def arrow(self, tip, direction, length=2.5, half=0.45):
        (x, y), (dx, dy) = tip, direction
        bx, by = x - dx * length, y - dy * length
        px, py = -dy * half, dx * half
        self.path([(x, y), (bx + px, by + py), (bx - px, by - py)], "fill", closed=True)

    def svg(self, clear: bool = True) -> str:
        """The sheet as SVG, its labels first moved clear of the heavy lines (clear_labels) unless `clear` is False."""
        if clear and not getattr(self, "_cleared", False):
            clear_labels(self)
            self._cleared = True
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
_RECT_D = re.compile(r"M([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+) Z$")
_NAMES = re.compile(r'data-names="(\w+) ([-\d. ]+)"')
LEAD_TOL = 0.3     # mm: a leader's end this near what its label names is on it
LEAD_GAP = 0.5     # mm: two leaders nearer each other than this read as crossing or joining, unless they share an end


def lead_attr(target) -> str:
    """The attributes that mark a path as a leader in the SVG, with what its label names (Sheet.target) where known."""
    if target is None:
        return ' class="leader"'
    return f' class="leader" data-names="{target[0]} ' + " ".join(f"{v:.2f}" for v in target[1:]) + '"'


def read_target(e: str):
    """What a leader element names, as Sheet.target gives it, or None."""
    m = _NAMES.search(e)
    return (m[1], *map(float, m[2].split())) if m else None


def on_target(p, target, tol: float = LEAD_TOL) -> bool:
    """Is sheet point p (SVG mm) on what a label names: at its point, in its box or on its symbol's circle?"""
    kind = target[0]
    if kind == "point":
        return math.hypot(p[0] - target[1], p[1] - target[2]) <= tol
    if kind == "box":
        return target[1] - tol <= p[0] <= target[2] + tol and target[3] - tol <= p[1] <= target[4] + tol
    return abs(math.hypot(p[0] - target[1], p[1] - target[2]) - target[3]) <= tol


@dataclass(frozen=True)
class Fill:
    """A white fill drawn at element n: its bounds (x0, x1, y0, y1) and, for a disc, its circle (cx, cy, r)."""
    box: tuple
    n: int
    circle: tuple | None = None

    def holds(self, pts) -> bool:
        """Does the fill paint over every one of the points?"""
        if self.circle:
            cx, cy, r = self.circle
            return all(math.hypot(p[0] - cx, p[1] - cy) <= r + 1e-6 for p in pts)
        b = self.box
        return all(b[0] - 1e-6 <= p[0] <= b[1] + 1e-6 and b[2] - 1e-6 <= p[1] <= b[3] + 1e-6 for p in pts)

    def meets(self, b) -> bool:
        """Does the fill overlap the box b (x0, x1, y0, y1)?"""
        f = self.box
        if not (b[0] < f[1] and f[0] < b[1] and b[2] < f[3] and f[2] < b[3]):
            return False
        if self.circle:
            cx, cy, r = self.circle
            return math.hypot(max(b[0] - cx, 0.0, cx - b[1]), max(b[2] - cy, 0.0, cy - b[3])) < r
        return True


def _white_fill(n: int, d: str, attrs: str) -> Fill | None:
    """A path's white fill as a cover: any white fill with no stroke, by its bounds, and a stroked one when it is a
    rectangle (a symbol's or a box's background, CT-602's outlets)."""
    if 'fill="#fff"' not in attrs:
        return None
    xs, ys = [float(v) for v in re.findall(r"([-\d.]+),", d)], [float(v) for v in re.findall(r",([-\d.]+)", d)]
    if 'stroke="none"' not in attrs:
        m = _RECT_D.match(d.strip())
        if not m:
            return None
        p = [(float(m[k]), float(m[k + 1])) for k in (1, 3, 5, 7)]
        if not all(abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6 for a, b in zip(p, p[1:] + p[:1])):
            return None
    return Fill((min(xs), max(xs), min(ys), max(ys)), n)


def _hidden(n: int, pts, fills: list, before: int) -> bool:
    """Is a mark drawn at element n hidden at the points `pts` by a white fill drawn after it and before element
    `before`, a symbol's or a box's background under a text?"""
    return any(n < f.n < before and f.holds(pts) for f in fills)


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
    and circles as chords, the frame's left out, and the white fills (the title block's, the tables', a symbol's
    background) as Fill. `every` keeps the frame, the symbol circles and the outlines of the black fills too (the
    arrowheads), for the overrun check (cad/tools/overrun.py), which finds every mark that shows through a text."""
    out, fills = [], []
    for n, e in enumerate(el):
        if e.startswith("<path"):
            m = _PATH.match(e)
            if not m:
                continue
            f = _white_fill(n, m[1], m[2])
            if f:
                fills.append(f)
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
            if m and 'fill="#fff"' in m[4]:
                cx, cy, r = float(m[1]), float(m[2]), float(m[3])
                fills.append(Fill((cx - r, cx + r, cy - r, cy + r), n, (cx, cy, r)))
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
    unrotated frame in SVG coordinates (x0, x1, y0, y1): 0.12 of its size in from each end, from 0.06 of its size above
    the baseline up to CAPS, the capitals' height, so a line that only grazes a descender, the baseline or the space
    round the text is not counted, and one through the capitals' tops is. `t` holds the text (t), its anchor point
    (x, y), size (s), anchor and weight (bold)."""
    s, txt = t["s"], t["t"]
    lead = len(txt) - len(txt.lstrip())
    w = text_mm(txt.strip(), s, t["bold"])
    full = text_mm(txt, s, t["bold"])
    x0 = t["x"] if t["anchor"] == "start" else t["x"] - full / 2 if t["anchor"] == "middle" else t["x"] - full
    x0 += text_mm(" " * lead, s, t["bold"]) if lead else 0.0
    return x0, w, (x0 + 0.12 * s, x0 + w - 0.12 * s, t["y"] - CAPS * s, t["y"] - 0.06 * s)


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
        if any(f.n > t["i"] and f.meets(bx) for f in fills):
            continue
        cand = set()
        for gx in range(int((bx[0] - 0.5) // G), int((bx[1] + 0.5) // G) + 1):
            for gy in range(int((bx[2] - 0.5) // G), int((bx[3] + 0.5) // G) + 1):
                cand.update(grid.get((gx, gy), ()))
        hits = [n for p, q, n, hw in (segs[k] for k in cand)
                if _enters(to_local(p), to_local(q), (core[0] - hw, core[1] + hw, core[2] - hw, core[3] + hw))
                and not _hidden(n, cs, fills, t["i"])]
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


# ------------------------------------------------------------------ labels clear of the heavy lines (I2-64)
_TEXT_EL = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)" font-size="([\d.]+)" text-anchor="(\w+)"([^>]*)>(.*)</text>')
_LINE_EL = re.compile(r'<path d="M([-\d.]+),([-\d.]+) L([-\d.]+),([-\d.]+)" stroke="#[0-9a-f]+" stroke-width="([\d.]+)"')
DRAW_AREA = (21.0, 409.0, 11.0, 286.0)       # inside the frame, SVG mm
ATTACH, REACH = 1.2, 15.0                     # a leader's end this near a label moves with it; the farthest a label moves
PREFER = 8.0      # mm of cost: a place that needs no leader is taken over a nearer one that needs a leader to what it names
SPACE = 1.0       # of the size: a moved label keeps this far from every text that runs the same way, so the two never read as one


def _steps() -> list[tuple]:
    """The moves a label tries, nearest first, as (cost, du, dv): along its baseline before across it, out to REACH mm."""
    out = []
    ds = [0.25 * k for k in range(1, 13)] + [3.0 + 0.5 * k for k in range(1, 15)] + [10.0 + k for k in range(1, int(REACH) - 9)]
    for d in ds:
        for k in range(24):
            a = math.pi * k / 12
            out.append((d * (1.0 if k in (0, 12) else 1.5), d * math.cos(a), d * math.sin(a)))
    return sorted(out)


STEPS = _steps()


class _Frame:
    """A text's own frame, rotated `rot` degrees about its anchor (x, y), SVG mm."""

    def __init__(self, t):
        a = math.radians(t["rot"])
        self.x, self.y, self.c, self.s = t["x"], t["y"], math.cos(a), math.sin(a)

    def local(self, p):
        dx, dy = p[0] - self.x, p[1] - self.y
        return (self.x + dx * self.c + dy * self.s, self.y - dx * self.s + dy * self.c)

    def sheet(self, u, v):
        du, dv = u - self.x, v - self.y
        return (self.x + du * self.c - dv * self.s, self.y + du * self.s + dv * self.c)

    def ring(self, b, du=0.0, dv=0.0):
        return [self.sheet(u + du, v + dv) for u, v in ((b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3]))]


def _sep(a: list, b: list) -> bool:
    """Do two convex quadrilaterals, their corners in order round them, stand apart?"""
    for poly in (a, b):
        for k in range(4):
            (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % 4]
            nx, ny = y1 - y2, x2 - x1
            pa = [nx * p[0] + ny * p[1] for p in a]
            pb = [nx * p[0] + ny * p[1] for p in b]
            if max(pa) <= min(pb) + 1e-9 or max(pb) <= min(pa) + 1e-9:
                return True
    return False


def _bnds(ring) -> tuple:
    return (min(p[0] for p in ring), max(p[0] for p in ring), min(p[1] for p in ring), max(p[1] for p in ring))


class _Grid:
    """Items in 5 mm cells by their bounds (x0, x1, y0, y1)."""

    def __init__(self):
        self.cells: dict = {}

    def add(self, k, b):
        for gx in range(int(b[0] // 5.0), int(b[1] // 5.0) + 1):
            for gy in range(int(b[2] // 5.0), int(b[3] // 5.0) + 1):
                self.cells.setdefault((gx, gy), set()).add(k)

    def near(self, b) -> set:
        out = set()
        for gx in range(int(b[0] // 5.0), int(b[1] // 5.0) + 1):
            for gy in range(int(b[2] // 5.0), int(b[3] // 5.0) + 1):
                out |= self.cells.get((gx, gy), set())
        return out


def _text_items(sh) -> list[dict]:
    """Every text on the sheet, free and in cells, with its frame and its boxes in that frame: its letters' cores, its
    letters up to the capitals and the mask knockouts would draw behind it."""
    free = {t["i"]: t for t in sh.texts}
    out = []
    for n, e in enumerate(sh.el):
        m = _TEXT_EL.match(e)
        if not m:
            continue
        rot = re.search(r'rotate\(([-\d.]+) ', m[5])
        raw = html.unescape(m[6])
        if not raw.strip():
            continue
        t = free.get(n) or dict(i=n, x=float(m[1]), y=float(m[2]), s=float(m[3]), anchor=m[4], bold='font-weight="bold"' in m[5],
                                rot=float(rot[1]) if rot else 0.0, t=raw)
        x0, w, core = text_core(t)
        y, s = t["y"], t["s"]
        out.append(dict(t=t, n=n, free=n in free, fr=_Frame(t), core=core, letters=(core[0], core[1], y - CAPS * s, y),
                        mask=(x0 - 0.3, x0 + w + 0.3, y - 0.78 * s - 0.2, y + 0.24 * s + 0.2)))
    return out


def _blocks(items: list[dict]) -> list[list[dict]]:
    """The free texts in runs that read as one label: drawn one after the other, the same size and turn, each within
    1.5 of its size of the one before."""
    out: list[list[dict]] = []
    for it in (i for i in items if i["free"]):
        last = out[-1][-1] if out else None
        d = 1.5 * it["t"]["s"]
        b = it["letters"]
        if (last is not None and it["n"] == last["n"] + 1 and it["t"]["s"] == last["t"]["s"] and it["t"]["rot"] == last["t"]["rot"]
                and not _sep(it["fr"].ring((b[0] - d, b[1] + d, b[2] - d, b[3] + d)), last["fr"].ring(last["letters"]))):
            out[-1].append(it)
        else:
            out.append([it])
    return out


def _seg_in(fr, p, q, box, du=0.0, dv=0.0, pad=0.0) -> bool:
    return _enters(fr.local(p), fr.local(q), (box[0] + du - pad, box[1] + du + pad, box[2] + dv - pad, box[3] + dv + pad))


def clear_labels(sh) -> list[dict]:
    """Free labels clear of the heavy lines (I2-64, I2-69). A free text, or a run of lines that reads as one label, whose
    mask would break a line of HEAVY mm or more, or that a mark the masks never take (the frame, a symbol, a dot or an
    arrowhead) crosses, moves to the nearest place along its baseline, or failing that round it within REACH mm, where
    its masks would cover only thin lines and no mark, clear of every other text, every white fill and the frame. A
    line hidden under a white fill drawn before the text (a symbol's or a box's background) does not cross it. A leader
    drawn with the label (Sheet.leads) follows it, its arrowhead turned, and a symbol drawn round it (a balloon's circle,
    an outlet's square) moves whole with it. A label that leaves its place and is no longer at what it names (Sheet.text
    `names`) gets a thin leader to that, with a dot in it or on its symbol's circle. One whose sheet does not say what it
    names moves only as far as it still reads at its place. No leader may cross another leader, a text or a symbol. A
    label with no such place stays, for the overrun check to report. Returns the moves."""
    sh.moves = []
    B = _Board(sh)
    if not B.any_fault_possible():
        return []
    moves = []
    for block in _blocks(B.items):
        if not B.faulty(block):
            continue
        mv = _move_block(B, block)
        if mv:
            moves.append(mv)
    sh.moves = moves
    return moves


class _Board:
    """A sheet's lines, marks, fills, texts, leaders and symbols, in grids, as clear_labels moves its labels."""

    def __init__(self, sh):
        self.sh = sh
        self.segs, self.fills = _segments(sh.el, every=True)
        self.plain = {n for _, _, n, _ in _segments(sh.el)[0]}
        self.items = _text_items(sh)
        self.heavy, self.marks, self.thin = _Grid(), _Grid(), _Grid()
        self.seg_of: dict = {}
        self.dead: set = set()
        for k, (p, q, n, hw) in enumerate(self.segs):
            self._file(k, p, q, n, hw, n in self.plain)
            self.seg_of.setdefault(n, []).append(k)
        self.tgrid = _Grid()
        for k, it in enumerate(self.items):
            self.tgrid.add(k, _bnds(it["fr"].ring(it["mask"])))
        self.leaders = {n: _path_pts(e) for n, e in enumerate(sh.el) if e.startswith("<path") and 'class="leader"' in e}
        self.symbols = _symbol_circles(sh.el)

    def _file(self, k, p, q, n, hw, plain):
        b = (min(p[0], q[0]) - hw, max(p[0], q[0]) + hw, min(p[1], q[1]) - hw, max(p[1], q[1]) + hw)
        (self.heavy if 2 * hw >= HEAVY - 1e-9 else self.thin if plain else self.marks).add(k, b)

    def any_fault_possible(self) -> bool:
        return any(n not in self.plain for _, _, n, _ in self.segs) or bool(self.heavy.cells)

    def faulty(self, block) -> bool:
        """Would the block's mask break a heavy line, or does a mark the masks never take cross its letters, where it is?
        A line hidden at the letters under a white fill drawn before them does not count."""
        segs, plain = self.segs, self.plain
        for it in block:
            fr, core, mask = it["fr"], it["core"], it["mask"]
            bc, bm = _bnds(fr.ring(core)), _bnds(fr.ring(mask))
            corners = fr.ring(core)
            near = self.thin.near(bc) | self.heavy.near(bc) | self.marks.near(bc)
            hit = [segs[k][2] for k in near if k not in self.dead and _seg_in(fr, segs[k][0], segs[k][1], core, pad=segs[k][3])
                   and not _hidden(segs[k][2], corners, self.fills, it["n"])]
            if any(n not in plain for n in hit):
                return True
            cross = [n for n in hit if n in plain]
            if cross:
                place = max(max(cross), it["n"])
                mring = fr.ring(mask)
                if any(k not in self.dead and segs[k][2] <= place and _seg_in(fr, segs[k][0], segs[k][1], mask)
                       and not _hidden(segs[k][2], mring, self.fills, place + 1) for k in self.heavy.near(bm)):
                    return True
        return False

    def reseg(self, n, e):
        """Element n drawn anew as e: its old pieces out of the obstacles, its new ones in."""
        self.dead.update(self.seg_of.get(n, ()))
        self.seg_of[n] = []
        plain = bool(_segments([e])[0])
        if plain:
            self.plain.add(n)
        for p, q, _, hw in _segments([e], every=True)[0]:
            k = len(self.segs)
            self.segs.append((p, q, n, hw))
            self.seg_of[n].append(k)
            self._file(k, p, q, n, hw, plain)
        if e.startswith("<path") and 'class="leader"' in e:
            self.leaders[n] = _path_pts(e)
        if e.startswith("<circle"):
            self.symbols = [s for s in self.symbols if s[3] != n] + _symbol_circles([e], n)

    def add(self, e):
        self.sh.el.append(e)
        self.reseg(len(self.sh.el) - 1, e)

    def crosses_leader(self, p, q, skip) -> bool:
        """Does the leader piece p-q cross or touch (LEAD_GAP) a leader drawn on the sheet but those in `skip`?"""
        return any(n not in skip and any(_crossing(p, q, a, b) for a, b in zip(pts, pts[1:])) for n, pts in self.leaders.items())

    def through_symbol(self, p, q, named, skip) -> bool:
        """Does the leader piece p-q pass through a symbol (a circle of SYMBOL_R or less, a dot) but one its named end
        `named` is in (its tag's dot, the gland it points into) and those in `skip`?"""
        for cx, cy, r, n in self.symbols:
            if n in skip or (named is not None and math.hypot(named[0] - cx, named[1] - cy) <= r + 0.05):
                continue
            if _seg_dist((cx, cy), p, q) < r - 0.05:
                return True
        return False


def _path_pts(e: str) -> list:
    m = _PATH.match(e)
    return [(float(a), float(b)) for a, b in re.findall(r"([-\d.]+),([-\d.]+)", m[1])] if m else []


def _symbol_circles(el, n0: int = 0) -> list[tuple]:
    """Every circle of SYMBOL_R or less on the sheet, stroked (a gland, a mount, a balloon, a fan) or filled (a dot), as
    (cx, cy, r, element index)."""
    out = []
    for n, e in enumerate(el, n0):
        m = _CIRCLE.match(e) if e.startswith("<circle") else None
        if m and float(m[3]) <= SYMBOL_R:
            out.append((float(m[1]), float(m[2]), float(m[3]), n))
    return out


def _seg_dist(c, p, q) -> float:
    """The least distance from point c to the segment p-q."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((c[0] - p[0]) * dx + (c[1] - p[1]) * dy) / L2))
    return math.hypot(p[0] + t * dx - c[0], p[1] + t * dy - c[1])


def _seg_gap(p, q, a, b) -> float:
    """The least distance between the segments p-q and a-b, 0 where they cross."""
    def side(u, v, w):
        return (v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0])
    if side(a, b, p) * side(a, b, q) < 0 and side(p, q, a) * side(p, q, b) < 0:
        return 0.0
    return min(_seg_dist(p, a, b), _seg_dist(q, a, b), _seg_dist(a, p, q), _seg_dist(b, p, q))


def _crossing(p, q, a, b, gap: float = LEAD_GAP) -> bool:
    """Do two leader pieces p-q and a-b cross, or come nearer each other than `gap`, so they read as crossing or as
    joining? Two pieces that share an end (a leader's line and its shoulder) do not."""
    if min(math.dist(e, f) for e in (p, q) for f in (a, b)) < 0.05:
        return False
    return _seg_gap(p, q, a, b) < gap


def _dist(p, b) -> float:
    return math.hypot(max(b[0] - p[0], 0.0, p[0] - b[1]), max(b[2] - p[1], 0.0, p[1] - b[3]))


def _gap(a, b) -> float:
    """The distance between two boxes (x0, x1, y0, y1), 0 where they overlap."""
    return math.hypot(max(a[0] - b[1], b[0] - a[1], 0.0), max(a[2] - b[3], b[2] - a[3], 0.0))


def _leads(sh, block) -> list[tuple]:
    """The leader parts drawn with the block's texts (Sheet.leads): (element, the moving ends) for a line, the elbow's
    end of a leader and a shoulder whole, (element, ("arrow", length, half)) for an arrowhead that turns with them, and a
    symbol drawn round the text that moves whole with it, (element, ("circle", r)) or (element, ("path",))."""
    out = []
    for it in block:
        for part in sh.leads.get(it["n"], ()):
            if part not in out:
                out.append(part)
    return out


def _own_leader(leads) -> bool:
    """Has the label a leader of its own (a leader's line, a tag's line, a balloon's), not only a symbol round it?"""
    return any(not how or how[0] not in ("circle", "path", "arrow") for _, how in leads)


def _shift_line(e: str, ends: tuple, dx: float, dy: float) -> tuple:
    m = _LINE_EL.match(e)
    pts = [[float(m[1]), float(m[2])], [float(m[3]), float(m[4])]]
    for k in ends:
        pts[k][0] += dx
        pts[k][1] += dy
    new = f'<path d="M{pts[0][0]:.2f},{pts[0][1]:.2f} L{pts[1][0]:.2f},{pts[1][1]:.2f}"'
    return e.replace(e[:e.index('" ') + 1], new, 1), [tuple(p) for p in pts]


def _moved_leads(sh, leads, dx, dy) -> list[tuple]:
    """The leader's parts with its ends at the label moved by (dx, dy): (element, its new text, its points), an arrowhead
    turned to the leader line drawn just before it, a balloon's circle moved whole and its leader's end kept on it."""
    out, line, centres = [], None, {}
    for n, how in leads:
        if how and how[0] == "arrow":
            (tx, ty), (ex, ey) = line
            L = math.hypot(tx - ex, ty - ey) or 1.0
            ux, uy = (tx - ex) / L, (ty - ey) / L
            bx, by = tx - ux * how[1], ty - uy * how[1]
            px, py = -uy * how[2], ux * how[2]
            pts = [(tx, ty), (bx + px, by + py), (bx - px, by - py)]
            d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
            out.append((n, re.sub(r'^<path d="[^"]*"', f'<path d="{d}"', sh.el[n]), []))
            continue
        if how and how[0] == "path":
            m = re.match(r'<path d="([^"]*)"', sh.el[n])
            xy = [(float(a) + dx, float(b) + dy) for a, b in re.findall(r"([-\d.]+),([-\d.]+)", m[1])]
            d = re.sub(r"[-\d.]+,[-\d.]+", lambda _m, it=iter(xy): "{:.2f},{:.2f}".format(*next(it)), m[1])
            box = (min(x for x, _ in xy), max(x for x, _ in xy), min(y for _, y in xy), max(y for _, y in xy))
            out.append((n, sh.el[n].replace(m[1], d, 1), [("box", *box)]))
            continue
        if how and how[0] == "circle":
            m = _CIRCLE.match(sh.el[n])
            cx, cy = float(m[1]) + dx, float(m[2]) + dy
            centres[n] = (cx, cy)
            out.append((n, re.sub(r'^<circle cx="[-\d.]+" cy="[-\d.]+"', f'<circle cx="{cx:.2f}" cy="{cy:.2f}"', sh.el[n]), [("circle", cx, cy, how[1])]))
            continue
        if how and how[0] == "balloon":
            m = _LINE_EL.match(sh.el[n])
            (tx, ty), (cx, cy) = (float(m[1]), float(m[2])), centres[how[2]]
            L = math.hypot(cx - tx, cy - ty) or 1.0
            ex, ey = cx - (cx - tx) / L * how[1], cy - (cy - ty) / L * how[1]
            new = f'<path d="M{tx:.2f},{ty:.2f} L{ex:.2f},{ey:.2f}"'
            out.append((n, sh.el[n].replace(sh.el[n][:sh.el[n].index('" ') + 1], new, 1), [(tx, ty), (ex, ey)]))
            continue
        e, pts = _shift_line(sh.el[n], how, dx, dy)
        out.append((n, e, pts))
        line = pts
    return out


def _named_end(how, pts):
    """The end of a moved leader piece that stays on what its label names: a leader's tip, a tag's dot, a balloon's
    tip. A shoulder moves whole and names nothing."""
    if how == (1,) or (how and how[0] == "balloon"):
        return pts[0]
    if how == (0,):
        return pts[1]
    return None


def _symbol_bounds(sh, leads):
    """The bounds of the symbols drawn round a label (its leads' circles and paths) where they stand, or None."""
    out = []
    for n, how in leads:
        if how and how[0] == "circle":
            m = _CIRCLE.match(sh.el[n])
            cx, cy, r = float(m[1]), float(m[2]), float(m[3])
            out.append((cx - r, cx + r, cy - r, cy + r))
        elif how and how[0] == "path":
            xy = _path_pts(sh.el[n])
            out.append((min(x for x, _ in xy), max(x for x, _ in xy), min(y for _, y in xy), max(y for _, y in xy)))
    return _union(*out) if out else None


def _union(*boxes):
    bs = [b for b in boxes if b is not None]
    return (min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs))


def _clamp(p, b):
    return (min(max(p[0], b[0]), b[1]), min(max(p[1], b[2]), b[3]))


def _off(orig, body, target, s) -> bool:
    """Has a label, its bounds with its symbol's `body` against `orig` where it stood, moved so far that it no longer
    reads at its place, and off what it names (`target`): out of its box, or more than 1.5 of its size from its point
    or its symbol's circle?"""
    if _gap(orig, body) <= 1.5 * s:
        return False
    if target is None:
        return True
    kind = target[0]
    if kind == "box":
        t = target
        return not (t[1] - 0.05 <= body[0] and body[1] <= t[2] + 0.05 and t[3] - 0.05 <= body[2] and body[3] <= t[4] + 0.05)
    if kind == "point":
        return _dist((target[1], target[2]), body) > 1.5 * s
    return _dist((target[1], target[2]), body) - target[3] > 1.5 * s


def _fallback(B, body, target, centre, shapes, own, skip):
    """The leader from a moved label, its bounds with its symbol `body`, to what it names: (start, end, dot), the end
    at its point, in its box at the nearest place that is clear, or on its symbol's circle (no dot), the start on the
    label's margin or on the symbol moved with it, the leader at least 1 mm long and crossing no text, no other leader
    and no symbol. None where no such leader exists."""
    g = (body[0] - 0.6, body[1] + 0.6, body[2] - 0.6, body[3] + 0.6)
    kind = target[0]
    if kind == "point":
        ends = [((target[1], target[2]), True)]
    elif kind == "box":
        ends = [(p, True) for p in _box_ends(B, target, centre, g)]
    else:
        cx, cy, r = target[1:]
        aim = _clamp((cx, cy), g)
        L = math.hypot(aim[0] - cx, aim[1] - cy) or 1.0
        ends = [((cx + (aim[0] - cx) * r / L, cy + (aim[1] - cy) * r / L), False)]
    for end, dot in ends:
        start = _clamp(end, g)
        for c in shapes:
            if c[0] == "circle":
                L = math.hypot(end[0] - c[1], end[1] - c[2]) or 1.0
                start = (c[1] + (end[0] - c[1]) * c[3] / L, c[2] + (end[1] - c[2]) * c[3] / L)
        if math.dist(start, end) < 1.0:
            continue
        if _crosses_text(B, start, end, own) or B.crosses_leader(start, end, skip) or B.through_symbol(start, end, end, skip):
            continue
        return start, end, dot
    return None


def _box_ends(B, box, centre, g, most: int = 40) -> list:
    """Where a leader into a box may end, nearest the label first: inside the box, in from its outline, at least 1.5 mm
    from the label's margin `g`, clear of the lines, the texts and the other leaders' dots there; failing every one, the
    label's old middle brought into the box."""
    _, x0, x1, y0, y1 = box
    inset = min(1.5, (x1 - x0) / 4, (y1 - y0) / 4)
    inner = (x0 + inset, x1 - inset, y0 + inset, y1 - inset)
    pts = [(inner[0] + 0.5 * i, inner[2] + 0.5 * j) for i in range(int((inner[1] - inner[0]) / 0.5) + 1)
           for j in range(int((inner[3] - inner[2]) / 0.5) + 1)]
    out = []
    for p in sorted((p for p in pts if _dist(p, g) >= 1.5), key=lambda p: _dist(p, g)):
        b = (p[0] - 0.45, p[0] + 0.45, p[1] - 0.45, p[1] + 0.45)
        if any(k not in B.dead and _enters(B.segs[k][0], B.segs[k][1], b) for k in B.thin.near(b) | B.heavy.near(b) | B.marks.near(b)):
            continue
        if any(_dist(p, _bnds(B.items[k]["fr"].ring(B.items[k]["mask"]))) < 0.3 for k in B.tgrid.near(b)):
            continue
        if any(r <= 0.5 and math.hypot(p[0] - cx, p[1] - cy) < r + 1.5 for cx, cy, r, _ in B.symbols):
            continue
        out.append(p)
        if len(out) >= most:
            break
    return out or [_clamp(centre, inner)]


def _move_block(B, block) -> dict | None:
    """The block's nearest place in STEPS where it is clear, preferring one that needs no leader to one up to PREFER
    nearer that does, applied to the sheet, or None."""
    sh = B.sh
    b0 = _bnds([p for it in block for p in it["fr"].ring(it["letters"])])
    corners = [(b0[0], b0[2]), (b0[1], b0[2]), (b0[1], b0[3]), (b0[0], b0[3])]
    leads = _leads(sh, block)
    ctx = dict(own={id(it) for it in block}, centre=((b0[0] + b0[1]) / 2, (b0[2] + b0[3]) / 2),
               walls=[f for f in B.fills if not f.holds(corners)], leads=leads, tied=_own_leader(leads),
               target=next((it["t"]["names"] for it in block if it["t"].get("names")), None),
               skip={n for n, _ in leads} | {it["n"] for it in block}, orig=_union(b0, _symbol_bounds(sh, leads)))
    led = None
    for cost, du, dv in STEPS:
        if led is not None and cost > led[0] + PREFER:
            break
        plan = _place(B, block, ctx, du, dv)
        if plan is None:
            continue
        if plan["extra"] is None:
            return _apply(B, block, ctx, plan)
        if led is None:
            led = (cost, plan)
    return _apply(B, block, ctx, led[1]) if led else None


def _place(B, block, ctx, du, dv) -> dict | None:
    """The block moved (du, dv) in its own frame, if it is clear there with its leader: its moved leader parts and the
    leader to what it names it then needs (`extra`), or None."""
    sh, fr0 = B.sh, block[0]["fr"]
    dx, dy = du * fr0.c - dv * fr0.s, du * fr0.s + dv * fr0.c
    own, walls, skip, leads = ctx["own"], ctx["walls"], ctx["skip"], ctx["leads"]
    if not all(_clear_at(B, it, du, dv, own, walls, skip) for it in block):
        return None
    moved = _bnds([p for it in block for p in it["fr"].ring(it["letters"], du, dv)])
    new = _moved_leads(sh, leads, dx, dy) if leads else []
    shapes = [pts[0] for _, _, pts in new if pts and isinstance(pts[0][0], str)]
    boxes = [(c[1] - c[3], c[1] + c[3], c[2] - c[3], c[2] + c[3]) if c[0] == "circle" else c[1:] for c in shapes]
    if not all(_symbol_clear(B, b, own, walls, skip) for b in boxes):
        return None
    body = _union(moved, *boxes)
    lines = [(pts[0], pts[1], _named_end(how, pts)) for (_, how), (_, _, pts) in zip(leads, new)
             if len(pts) == 2 and not isinstance(pts[0][0], str)]
    extra = None
    if not ctx["tied"] and _off(ctx["orig"], body, ctx["target"], block[0]["t"]["s"]):
        extra = _fallback(B, body, ctx["target"], ctx["centre"], shapes, own, skip) if ctx["target"] else None
        if extra is None:
            return None
        lines = []
    if any(_crosses_text(B, p, q, own) or B.crosses_leader(p, q, skip) or B.through_symbol(p, q, named, skip)
           for p, q, named in lines):
        return None
    return dict(dx=dx, dy=dy, new=new, extra=extra)


def _apply(B, block, ctx, plan) -> dict:
    """Move the block as planned: its texts, its leader parts and symbols, and the leader to what it names."""
    sh, dx, dy, extra = B.sh, plan["dx"], plan["dy"], plan["extra"]
    for it in block:
        _shift_text(sh, it, dx, dy)
        B.tgrid.add(B.items.index(it), _bnds(it["fr"].ring(it["mask"])))
    for n, e, _ in plan["new"]:
        sh.el[n] = e
        B.reseg(n, e)
    how = "with its leader" if ctx["tied"] else "with its symbol" if ctx["leads"] else ""
    if extra:
        (sx, sy), (ex, ey), dot = extra
        B.add(f'<path d="M{sx:.2f},{sy:.2f} L{ex:.2f},{ey:.2f}" {Sheet.STY["thin"]}{lead_attr(ctx["target"])}/>')
        if dot:
            B.add(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="0.30" {Sheet.STY["fill"]}/>')
        how = "with a leader to what it names"
    return dict(text=" / ".join(it["t"]["t"] for it in block), by=(round(dx, 2), round(dy, 2)), leader=how,
                at=(round(block[0]["t"]["x"], 1), round(block[0]["t"]["y"], 1)))


def _symbol_clear(B, box, own, walls, skip) -> bool:
    """Is a symbol that moves with its label (a balloon's circle, an outlet's square), its bounds `box`, clear of every
    line and mark but its own, so no line crosses its letters and no mask is drawn there, every white fill and every
    other text?"""
    b = (box[0] - 0.2, box[1] + 0.2, box[2] - 0.2, box[3] + 0.2)
    if not (DRAW_AREA[0] <= b[0] and b[1] <= DRAW_AREA[1] and DRAW_AREA[2] <= b[2] and b[3] <= DRAW_AREA[3]):
        return False
    segs = B.segs
    if any(k not in B.dead and segs[k][2] not in skip and _enters(segs[k][0], segs[k][1], b)
           for k in B.heavy.near(b) | B.marks.near(b) | B.thin.near(b)):
        return False
    if any(f.meets(b) for f in walls):
        return False
    ring = [(b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])]
    return all(id(B.items[k]) in own or _sep(ring, B.items[k]["fr"].ring(B.items[k]["mask"])) for k in B.tgrid.near(b))


def _clear_at(B, it, du, dv, own, walls, skip=frozenset()) -> bool:
    """Is a text clear moved (du, dv) in its own frame: its mask over no heavy line and no mark but its own parts',
    inside the frame, off every white fill but its own background, its letters and mask off every other text's, and
    SPACE of its size from any other text that runs the same way, so the two never read as one label?"""
    fr = it["fr"]
    mring = fr.ring(it["mask"], du, dv)
    mb = _bnds(mring)
    if not (DRAW_AREA[0] <= mb[0] and mb[1] <= DRAW_AREA[1] and DRAW_AREA[2] <= mb[2] and mb[3] <= DRAW_AREA[3]):
        return False
    segs = B.segs
    if any(k not in B.dead and segs[k][2] not in skip and _seg_in(fr, segs[k][0], segs[k][1], it["mask"], du, dv)
           for k in B.heavy.near(mb) | B.marks.near(mb)):
        return False
    if any(f.meets(mb) for f in walls):
        return False
    lring = fr.ring(it["letters"], du, dv)
    g = SPACE * it["t"]["s"]
    let = it["letters"]
    wide = fr.ring((let[0] - g, let[1] + g, let[2] - g, let[3] + g), du, dv)
    for k in B.tgrid.near(_bnds(wide)):
        o = B.items[k]
        if id(o) in own:
            continue
        oring = o["fr"].ring(o["letters"])
        if not _sep(mring, oring) or not _sep(lring, o["fr"].ring(o["mask"])) or (o["t"]["rot"] == it["t"]["rot"] and not _sep(wide, oring)):
            return False
    return True


def _crosses_text(B, p, q, own) -> bool:
    b = (min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1]))
    return any(id(B.items[k]) not in own and _seg_in(B.items[k]["fr"], p, q, B.items[k]["core"], pad=0.1) for k in B.tgrid.near(b))


def _shift_text(sh, it, dx: float, dy: float):
    """Move a text on the sheet by (dx, dy), SVG mm: its element, its entry in sh.texts and its boxes."""
    t = it["t"]
    t["x"], t["y"] = t["x"] + dx, t["y"] + dy
    e = re.sub(r'^<text x="[-\d.]+" y="[-\d.]+"', f'<text x="{t["x"]:.2f}" y="{t["y"]:.2f}"', sh.el[it["n"]])
    if t["rot"]:
        e = re.sub(r'rotate\(([-\d.]+) [-\d.]+ [-\d.]+\)', rf'rotate(\g<1> {t["x"]:.2f} {t["y"]:.2f})', e)
        t["tr"] = f' transform="rotate({t["rot"]:.1f} {t["x"]:.2f} {t["y"]:.2f})"'
    sh.el[it["n"]] = e
    it["fr"] = _Frame(t)
    for key in ("core", "letters", "mask"):
        b = it[key]
        it[key] = (b[0] + dx, b[1] + dx, b[2] + dy, b[3] + dy)


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
    n0 = len(sh.el)
    sh.lead([(tx, ty), (ex, ey)], names=tip)
    L = math.hypot(tx - ex, ty - ey) or 1
    sh.arrow((tx, ty), ((tx - ex) / L, (ty - ey) / L), 2.0, 0.4)
    side = 1 if ex >= tx else -1
    sh.lead([(ex, ey), (ex + 3 * side, ey)])
    parts = [(n0, (1,)), (n0 + 1, ("arrow", 2.0, 0.4)), (n0 + 2, (0, 1))]
    for i, t in enumerate([text] + (lines or [])):
        sh.leads[len(sh.el)] = parts
        sh.text(ex + 4 * side, ey - 0.8 - i * (size + 0.8), t, size, "start" if side > 0 else "end")


def balloon(sh, tip, centre, label, r=3.2):
    (tx, ty), (cx, cy) = tip, centre
    L = math.hypot(cx - tx, cy - ty) or 1
    ux, uy = (cx - tx) / L, (cy - ty) / L
    n0 = len(sh.el)
    sh.lead([(tx, ty), (cx - ux * r, cy - uy * r)], names=tip)
    sh.circle(tx, ty, 0.45, "fill")
    sh.circle(cx, cy, r, "medium")
    sh.leads[len(sh.el)] = [(n0 + 2, ("circle", r)), (n0, ("balloon", r, n0 + 2))]
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
    for m in getattr(sh, "moves", []):
        print(f"  {out_svg.stem}: moved {m['text'][:48]!r} by {m['by']} to {m['at']}" + (f" {m['leader']}" if m["leader"] else ""))
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text(svg, encoding="utf-8")
    cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(out_svg.with_suffix(".pdf")))
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out_svg.with_suffix(".png")), output_width=3508)

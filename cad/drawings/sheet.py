"""A3 drawing sheet in the AS 1100 / ISO style used in the stack spike: frame, title block (TB-01 to TB-13),
revision table (REV-01), parts list (BOM-01, compact), third-angle symbol, dimensions, balloons and
hidden-line views from build123d / OCCT HLR. Output is SVG with real text, then PDF and PNG via CairoSVG."""
from __future__ import annotations

import math
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
        "frame": 'stroke="#000" stroke-width="0.7" fill="none"',
        "hatch": 'stroke="#000" stroke-width="0.13" fill="none"',
        "fill": 'fill="#000" stroke="none"',
        "shade": 'fill="#c8c8c8" stroke="#000" stroke-width="0.25"',
        "white": 'fill="#fff" stroke="none"',
        "grey": 'stroke="#777" stroke-width="0.18" fill="none"',
        "fail": 'stroke="#c00" stroke-width="0.35" fill="none"',
    }

    def __init__(self):
        self.el: list[str] = []

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

    def text(self, x, y, s, size=2.5, anchor="start", rot=0.0, bold=False, color="#000"):
        s = str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tr = f' transform="rotate({rot:.1f} {x:.2f} {self._y(y):.2f})"' if rot else ""
        w = ' font-weight="bold"' if bold else ""
        c = f' fill="{color}"' if color != "#000" else ""
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
                + "\n".join(self.el) + "\n</svg>\n")


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
            sh.text(cx + 0.8, yy - row_h + 0.9, h, size, bold=True)
            cx += cw
        yy -= row_h
        sh.line(x, yy, x + w, yy, "thin")
    for r in rows:
        cx = x
        for (h, cw), v in zip(cols, r):
            color = "#000"
            if isinstance(v, tuple):
                v, color = v
            sh.text(cx + 0.8, yy - row_h + 0.9, str(v), size, color=color)
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
    sh.text(304, 44.4, f"1:{scale:g}", 3.0)
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
    cols = [(x0, "REV"), (x0 + 10, "DATE"), (x0 + 30, "DESCRIPTION"), (x0 + 120, "DRAWN"), (x0 + 140, "CHECKED"), (x0 + 160, "APPROVED")]
    for cx, labl in cols:
        if cx != x0:
            sh.line(cx, yb, cx, ytop - 5)
        sh.text(cx + 1, ytop - 8.6, labl, 1.7)
    sh.line(x0, ytop - 10, x1, ytop - 10)
    for i, r in enumerate(revisions):
        y = ytop - 13.8 - i * 5
        if i:
            sh.line(x0, ytop - 10 - 5 * i, x1, ytop - 10 - 5 * i)
        vals = [r["rev"], r["date"], r["description"], r["drawn"], r["checked"] or "-", r["approved"] or "-"]
        for (cx, _), v in zip(cols, vals):
            sh.text(cx + 1, y, v, 1.9)
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
        sh.text(cx + 0.8, ybase + 1.5, lab, 1.7, bold=True)
    for i, r in enumerate(rows):
        yb = ybase + row_h * (i + 1) + 1.4
        vals = [r["item"], r["part"], r["description"], r["qty"], r["mass"], r.get("supplier", "")]
        for (cx, _, w), v in zip(cols, vals):
            s = str(v)
            maxc = int(w / 1.05)
            if len(s) > maxc:
                s = s[: maxc - 1] + "…"
            sh.text(cx + 0.8, yb, s, 1.75)
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

"""The trailer's floor plan from the 3D model (decision H28), bed up (day and travel) and bed down (night).

The plan is a horizontal cut 1,000 mm above the floor surface through the shapes of `TrailerModel`, seen from above:
each part below the cut is drawn as its outline from above, each part the plane cuts also shows its cut faces, the
walls and the partition are their cut faces at their real thickness, and the parts wholly above the cut are dashed.
The doors are drawn open at 90 degrees with their swings, the windows in the walls, and the spaces kept clear (K1 to
K6) from the layout. `plan()` gives the geometry in DIM-01 mm, `svg()` draws it for the trailer page with each part
named for hover and the parts table, and drawing CT-010 draws the same geometry (cad/drawings/home_sheets.py).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from build123d import Compound, GeomType, Keep, Plane, split
from PIL import Image, ImageDraw

CUT = 1000.0             # mm above the floor surface
AREAS = {"bed": "Bed and desk", "kit": "Kitchen", "lau": "Laundry", "wet": "Wet room"}
WALLS = ("BD-03", "BD-04", "WR-03")      # cut as walls: the side and end walls and the partition
OPEN_DOORS = ("BD-07", "BD-15", "WR-04")  # drawn open with their swings, so their closed leaves are left out
STATES = {"day": "Bed up, day and travel", "night": "Bed down, night"}
RASTER = 1.0             # mm per cell for the outline of a part that is not a box
TOL = 0.5
FLOOR_TOP = 200.0        # mm: a part whose top is at most this far above the floor is a floor finish (the wet room's tray)


def _leaves(shape) -> list:
    if isinstance(shape, Compound) and shape.children:
        return [x for k in shape.children for x in _leaves(k)]
    return [shape]


def _bbox(shapes) -> tuple:
    bbs = [s.bounding_box() for s in shapes]
    return (min(b.min.X for b in bbs), min(b.min.Y for b in bbs), min(b.min.Z for b in bbs),
            max(b.max.X for b in bbs), max(b.max.Y for b in bbs), max(b.max.Z for b in bbs))


def _is_box(s) -> bool:
    """An axis-aligned box: its volume fills its bounding box."""
    try:
        b = s.bounding_box()
        v = (b.max.X - b.min.X) * (b.max.Y - b.min.Y) * (b.max.Z - b.min.Z)
        return v > 0 and abs(s.volume - v) <= 1e-4 * v
    except Exception:
        return False


def _rect(x0, y0, x1, y1) -> list:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _below(s, zc):
    """The part of a solid below the plane Z = zc, or None."""
    b = s.bounding_box()
    if b.max.Z <= zc + TOL:
        return s
    if b.min.Z >= zc - TOL:
        return None
    try:
        r = split(s, bisect_by=Plane.XY.offset(zc), keep=Keep.BOTTOM)
        return r if r is not None and r.volume > 1e-3 else None
    except Exception:
        return None


def _edge_pts(e) -> list:
    if e.geom_type == GeomType.LINE:
        us = [0.0, 1.0]
    else:
        n = max(8, min(96, int(e.length / 15)))
        us = [i / n for i in range(n + 1)]
    return [(p.X, p.Y) for p in (e.position_at(u) for u in us)]


def _wire_loop(w) -> list:
    try:
        edges = w.order_edges()
    except Exception:
        edges = w.edges()
    pts: list = []
    for e in edges:
        ep = _edge_pts(e)
        if pts and math.dist(ep[-1], pts[-1]) < math.dist(ep[0], pts[-1]):
            ep = ep[::-1]
        pts.extend(ep if not pts else ep[1:])
    if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-6:
        pts.pop()
    return pts


def _cut_faces(piece, zc) -> list:
    """The faces of a piece that lie in the cut plane, each as its loops (outer first)."""
    out = []
    for f in piece.faces():
        b = f.bounding_box()
        if abs(b.min.Z - zc) < TOL and abs(b.max.Z - zc) < TOL and b.max.X - b.min.X > 0.5 and b.max.Y - b.min.Y > 0.5:
            out.append([_wire_loop(f.outer_wire())] + [_wire_loop(w) for w in f.inner_wires()])
    return out


# ------------------------------------------------------------------ outlines seen from above
def _outline(pieces) -> list:
    """The outline of some solids seen from above, as loops of (x, y), outer loops anticlockwise and holes clockwise.
    A single box gives its rectangle. Anything else is drawn from its triangles onto a 1 mm grid and traced."""
    if len(pieces) == 1 and _is_box(pieces[0]):
        x0, y0, _, x1, y1, _ = _bbox(pieces)
        return [_rect(x0, y0, x1, y1)]
    x0, y0, _, x1, y1, _ = _bbox(pieces)
    h = max(RASTER, max(x1 - x0, y1 - y0) / 3000.0)
    nx, ny = int(math.ceil((x1 - x0) / h)) + 2, int(math.ceil((y1 - y0) / h)) + 2
    img = Image.new("1", (nx, ny), 0)
    draw = ImageDraw.Draw(img)
    for s in pieces:
        verts, tris = s.tessellate(0.5, 0.3)
        P = [((v.X - x0) / h + 1, (v.Y - y0) / h + 1) for v in verts]
        for a, b, c in tris:
            draw.polygon([P[a], P[b], P[c]], fill=1)
    loops = _trace(np.array(img, dtype=bool))
    # PIL fills the cells a triangle touches, edges included, and a cell's centre is its integer point: the traced
    # boundary runs on the cell edges, half a cell outside the true edge, so it is moved back by half a cell
    return [[(x0 + (u - 1.5) * h, y0 + (v - 1.5) * h) for u, v in _simplify(lp, 1.0)] for lp in loops if len(lp) >= 4]


def _trace(m) -> list:
    """Boundary loops of the filled cells of a boolean grid (row = y), along the cell edges with the filled cells on the
    left, so outer loops run anticlockwise. A diagonal touch keeps the two cells apart."""
    p = np.pad(m, 1)
    f = p[1:-1, 1:-1]
    i, j = np.nonzero(f & ~p[:-2, 1:-1])          # empty below: an edge along the bottom, +x
    edges = [((x, y), (x + 1, y)) for y, x in zip(i + 1, j + 1)]
    i, j = np.nonzero(f & ~p[2:, 1:-1])           # empty above: along the top, -x
    edges += [((x + 1, y + 1), (x, y + 1)) for y, x in zip(i + 1, j + 1)]
    i, j = np.nonzero(f & ~p[1:-1, 2:])           # empty to the right: +y
    edges += [((x + 1, y), (x + 1, y + 1)) for y, x in zip(i + 1, j + 1)]
    i, j = np.nonzero(f & ~p[1:-1, :-2])          # empty to the left: -y
    edges += [((x, y + 1), (x, y)) for y, x in zip(i + 1, j + 1)]
    nxt: dict = {}
    for a, b in edges:
        nxt.setdefault((int(a[0]), int(a[1])), []).append((int(b[0]), int(b[1])))
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, cur, prev = [start], start, None
        while True:
            outs = nxt.get(cur)
            if not outs:
                break
            if len(outs) > 1 and prev is not None:      # a diagonal touch: take the left turn
                d = (cur[0] - prev[0], cur[1] - prev[1])
                left = (cur[0] - d[1], cur[1] + d[0])
                b = left if left in outs else outs[0]
            else:
                b = outs[0]
            outs.remove(b)
            if not outs:
                del nxt[cur]
            prev, cur = cur, b
            if cur == start:
                break
            loop.append(cur)
        loops.append(loop)
    return loops


def _simplify(pts, tol) -> list:
    """Drop the points on a straight run, then Douglas-Peucker on what stays (a closed loop)."""
    n = len(pts)
    keep = [pts[k] for k in range(n) if (pts[k][0] - pts[k - 1][0]) * (pts[(k + 1) % n][1] - pts[k][1])
            != (pts[k][1] - pts[k - 1][1]) * (pts[(k + 1) % n][0] - pts[k][0])]
    if len(keep) < 8:
        return keep
    ring = keep + [keep[0]]
    mark = [False] * len(ring)
    mark[0] = mark[len(keep) // 2] = mark[-1] = True
    stack = [(0, len(keep) // 2), (len(keep) // 2, len(ring) - 1)]
    while stack:
        i0, i1 = stack.pop()
        a, b = ring[i0], ring[i1]
        L = math.dist(a, b) or 1e-9
        best, k = -1.0, None
        for i in range(i0 + 1, i1):
            q = ring[i]
            d = abs((b[0] - a[0]) * (a[1] - q[1]) - (a[0] - q[0]) * (b[1] - a[1])) / L
            if d > best:
                best, k = d, i
        if k is not None and best > tol:
            mark[k] = True
            stack += [(i0, k), (k, i1)]
    out = [q for q, m in zip(ring[:-1], mark[:-1]) if m]
    return out if len(out) >= 3 else keep


def _hlr_edges(pieces) -> list:
    """The edges seen from above of some solids, hidden edges left out, as polylines of (x, y)."""
    from .drawings.sheet import edge_pts, hlr
    try:
        res = hlr(pieces, (0, 0, 1), (0, 1, 0))
    except Exception:
        return []
    return [edge_pts(e) for e in res["visible"]]


def _area_of(loops) -> float:
    return sum(0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(lp, lp[1:] + lp[:1])) for lp in loops)


def _inside(a, b, tol=0.0) -> bool:
    """Plan box a (x0, y0, x1, y1) lies within plan box b, give or take tol mm."""
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


# ------------------------------------------------------------------ the plan of one bed position
def area_of(block, cx, cy, V) -> str:
    """The area a part belongs to: its system for the bed and the wet room, else where it stands."""
    sys_ = block.system if block is not None else None
    if sys_ == "bed":
        return "bed"
    if sys_ == "wet_room":
        return "wet"
    if cx < V["bed_x1"]:
        return "bed"
    if cx >= V["rear_x0"]:
        return "wet"
    return "kit" if cy > 0 else "lau"


def _r(loops) -> list:
    return [[[round(x, 1), round(y, 1)] for x, y in lp] for lp in loops]


def _doorway(lay):
    """The inner door's opening in the partition (WR-04, layout study 2.3): the walk band's width (K5) through the
    partition, from the floor to the head of its 1,850 mm leaf."""
    V = lay.V
    wr, k5 = lay.find("WR-03").box, lay.find("LA-K5").box
    return (wr[0] - 1, k5[1], V["floor_z"] - 1, wr[3] + 1, k5[4], V["floor_z"] + 1850)


def _doors(lay) -> list:
    """The doors open at 90 degrees: hinge, the closed and open directions, the leaf and its swing (CT-013's
    operations: D1 hinged on its front edge and D2 on its kerb edge, both opening outward, the inner door opening into
    the wet room's walk band)."""
    from .drawings.home_common import MARK
    V = lay.V
    out = []
    d1, d2 = lay.find("BD-07"), lay.find("BD-15")
    dw = _doorway(lay)
    for b, hinge, closed, opened, L, t, gap in (
            (d1, (d1.box[0], -V["half_bw"]), (1, 0), (0, -1), d1.box[3] - d1.box[0], V["wall_t"], d1.box),
            (d2, (V["body_x1"], d2.box[1]), (0, 1), (1, 0), d2.box[4] - d2.box[1], V["wall_t"], d2.box),
            (None, (dw[3] - 1, dw[1]), (0, 1), (1, 0), dw[4] - dw[1], dw[3] - dw[0] - 2, dw)):
        hx, hy = hinge
        tip = (hx + opened[0] * L, hy + opened[1] * L)
        leaf = [hinge, tip, (tip[0] + closed[0] * t, tip[1] + closed[1] * t), (hx + closed[0] * t, hy + closed[1] * t)]
        a0, a1 = math.atan2(opened[1], opened[0]), math.atan2(closed[1], closed[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        arc = [(hx + L * math.cos(a0 + da * k / 24), hy + L * math.sin(a0 + da * k / 24)) for k in range(25)]
        iid = b.iid if b else "WR-04"
        name = b.name if b else next((x.name for x in lay.blocks if x.id == "WR-04"), "Inner door")
        out.append(dict(iid=iid, id=iid, name=name, mark=MARK.get(iid, "Inner door"), kind="door", width=round(L),
                        leaf=_r([leaf])[0], arc=_r([arc])[0], gap=_r([_rect(gap[0], gap[1], gap[3], gap[4])])[0]))
    return out


def _windows(lay, res, zc) -> list:
    """The windows in the walls from the body's openings: cut by the plane, or above it (dashed)."""
    from .drawings.home_common import MARK
    V = lay.V
    out = []
    for o in res["openings"]:
        line = o.get("line") or ""
        if not line.startswith("WN-"):
            continue
        b = lay.find(line)
        x0, y0, _, x1, y1, _ = b.box
        cut = o["z0"] < CUT - TOL and o["z1"] > CUT + TOL
        out.append(dict(iid=b.iid, id=b.id, name=b.name, mark=MARK.get(line, line), kind="window", cut=cut,
                        wall=o["wall"], sill=round(o["z0"]), head=round(o["z1"]), box=[x0, y0, x1, y1]))
    return out


def plan(lay, res, tm=None, state="day") -> dict:
    """The plan of one bed position in DIM-01 mm: the parts with their outlines, edges and cut faces in the order they
    are drawn (lowest top first), the walls, the doors and windows, the spaces kept clear and the main dimensions.
    `tm` is the layout's TrailerModel with the designed body, built here when not given."""
    from .model.prims import box
    from .trailer_model import TrailerModel
    V = lay.V
    tm = tm or TrailerModel(lay, body=True)
    zc = V["floor_z"] + CUT
    by_iid = {b.iid: b for b in lay.blocks}
    xa, xb, ya, yb = V["in_x0"] - 1, V["in_x1"] + 1, -V["half_in"] - 1, V["half_in"] + 1
    dw = _doorway(lay)
    parts, walls = [], []
    for shapes in tm.groups.values():
        for s in shapes:
            iid = s.label.split(" ", 1)[0]
            blk = by_iid.get(iid)
            line = blk.id if blk else iid.split(".")[0]
            name = blk.name if blk else s.label.split(" ", 1)[-1]
            leaves = [k for k in _leaves(s) if k.volume > 1e-3]
            if not leaves or line in OPEN_DOORS:
                continue
            x0, y0, z0, x1, y1, z1 = _bbox(leaves)
            if line in WALLS:
                cut = []
                for k in leaves:
                    k = k - box(*dw[:3], dw[3] - dw[0], dw[4] - dw[1], dw[5] - dw[2]) if line == "WR-03" else k
                    piece = _below(k, zc)
                    cut += _cut_faces(piece, zc) if piece is not None else []
                walls.append(dict(iid=iid, id=line, name=name, area="wall", kind="wall", cut=[_r(f) for f in cut],
                                  box=[x0, y0, x1, y1]))
                continue
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if not (xa < cx < xb and ya < cy < yb) or z0 < V["floor_z"] - 5 or z1 > V["ceiling_z"] + 5:
                continue                     # outside the room: the walls' fillers, the floor, the roof, the lamps
            if blk is not None and blk.system == "body" and blk.zone != "inside":
                continue                     # the body's own parts, such as the roof-to-wall joiner round the wall tops
            area = area_of(blk, (x0 + x1) / 2, (y0 + y1) / 2, V)
            system = blk.system if blk else None
            if z0 >= zc - TOL:
                parts.append(dict(iid=iid, id=line, name=name, area=area, system=system, kind="above", top=z1,
                                  outline=_r(_outline(leaves)), edges=[], cut=[], box=[x0, y0, x1, y1]))
                continue
            pieces = [p for p in (_below(k, zc) for k in leaves) if p is not None]
            boxes = len(pieces) == 1 and _is_box(pieces[0])
            cut = [f for p in pieces for f in _cut_faces(p, zc)] if z1 > zc + TOL else []
            top = max(p.bounding_box().max.Z for p in pieces)
            parts.append(dict(iid=iid, id=line, name=name, area=area, system=system, kind="cut" if cut else "below", top=top,
                              outline=_r(_outline(pieces)), edges=[] if boxes else _r(_hlr_edges(pieces)),
                              cut=[_r(f) for f in cut], box=[x0, y0, x1, y1]))
    # the drawing order: the lowest tops first, so a higher part covers what is under it, the larger first at a tie
    parts.sort(key=lambda p: (p["kind"] == "above", round(p["top"], 1), -abs(_area_of(p["outline"]))))
    # a part the lowered bed covers from above (the desk at night) is named by the bed's line, drawn dashed over it
    for n, q in enumerate(parts):
        if q["kind"] != "above" and q["system"] != "bed":
            q["under"] = next((r["iid"] for r in parts[n + 1:] if r["kind"] != "above" and r["system"] == "bed"
                               and r["top"] > q["top"] and _inside(q["box"], r["box"], 20.0)), None)
    clear = []
    for b in (b for b in lay.blocks if b.keep_clear and b.box is not None):
        x0, y0, _, x1, y1, _ = b.box
        clear.append(dict(iid=b.iid, id=b.id, name=b.name, area="clear", kind="clear", mark=b.iid.split("-")[-1],
                          outline=_r([_rect(x0, y0, x1, y1)]), box=[x0, y0, x1, y1]))
    k4, k5 = lay.find("LA-K4").box, lay.find("LA-K5").box
    well = next((b.box for b in lay.blocks if b.id == "WR-10" and b.box), None)   # the shower stands over its well
    zl = lay.zone_lengths()
    dims = dict(inside_length=V["in_x1"] - V["in_x0"], inside_width=2 * V["half_in"], bed=zl["bed"], living=zl["living"],
                rear=zl["rear"], aisle=k4[4] - k4[1], walk_band=k5[4] - k5[1])
    return dict(state=state, title=STATES[state], cut_mm=CUT, cut_z=zc, floor_z=V["floor_z"],
                body=[V["body_x0"], -V["half_bw"], V["body_x1"], V["half_bw"]],
                inside=[V["in_x0"], -V["half_in"], V["in_x1"], V["half_in"]],
                stations=[V["in_x0"], V["bed_x1"], V["rear_x0"], V["in_x1"]], wall_t=V["wall_t"],
                aisle=[k4[0], k4[1], k4[3], k4[4]], walk_band=[k5[0], k5[1], k5[3], k5[4]], dims=dims,
                shower=[well[0], well[1], well[3], well[4]] if well else None,
                walls=walls, parts=parts, clear=clear, doors=_doors(lay), windows=_windows(lay, res, zc))


# ------------------------------------------------------------------ the plan as SVG for the trailer page
LEFT, RIGHT, TOP, BOTTOM = 620.0, 760.0, 720.0, 780.0   # mm round the body for the dimensions, swings and labels
T_AREA, T_PART, T_DIM, T_MARK = 130.0, 82.0, 84.0, 78.0  # text heights, mm


def _esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text_w(s, size) -> float:
    """Rough width of a text in the site's sans-serif font, mm."""
    up = sum(1 for c in str(s) if c.isupper() or c.isdigit())
    return size * (0.64 * up + 0.52 * (len(str(s)) - up))


def short_name(iid, line, name) -> str:
    """The short name a part is labelled with: the sheets' name for it in sentence case, or its name's first words."""
    from .drawings.home_common import SHORT
    s = SHORT.get(iid) or SHORT.get(line)
    if s is None:
        s = " ".join(name.split(",")[0].split()[:2])
    return s[0] + s[1:].lower() if s.isupper() else s


class _Svg:
    def __init__(self, p):
        self.p = p
        bx0, _, bx1, hb = p["body"]
        self.X0, self.Y1 = bx0 - LEFT, hb + TOP
        self.W, self.H = bx1 - bx0 + LEFT + RIGHT, 2 * hb + TOP + BOTTOM
        self.out: list[str] = []

    def pt(self, x, y) -> str:
        return f"{x - self.X0:.1f},{self.Y1 - y:.1f}"

    def d(self, loops, closed=True) -> str:
        return " ".join("M" + " L".join(self.pt(x, y) for x, y in lp) + (" Z" if closed else "") for lp in loops if len(lp) > 1)

    def text(self, x, y, s, size, cls="", anchor="middle", rot=0):
        tr = f' transform="rotate({rot} {x - self.X0:.1f} {self.Y1 - y:.1f})"' if rot else ""
        self.out.append(f'<text x="{x - self.X0:.1f}" y="{self.Y1 - y:.1f}" font-size="{size:g}" text-anchor="{anchor}" '
                        f'class="fp-t {cls}"{tr}>{_esc(s)}</text>')

    def line(self, x0, y0, x1, y1, cls):
        self.out.append(f'<path class="{cls}" d="M{self.pt(x0, y0)} L{self.pt(x1, y1)}"/>')

    def group(self, item, cls, body):
        self.out.append(f'<g class="fp-part {cls}" data-iid="{_esc(item["iid"])}" data-id="{_esc(item["id"])}" '
                        f'data-name="{_esc(item["name"])}" data-kind="{item["kind"]}">{body}</g>')

    def hdim(self, x0, x1, y, yfrom, label):
        """A dimension along X at height y, with extension lines from yfrom past the line and the figure above it."""
        s = 1 if y >= yfrom else -1
        for x in (x0, x1):
            self.line(x, yfrom + s * 20, x, y + s * 45, "fp-ext")
            self.line(x - 28, y - 28, x + 28, y + 28, "fp-tick")
        self.line(x0 - 60, y, x1 + 60, y, "fp-dim")
        self.text((x0 + x1) / 2, y + 40, label, T_DIM, "fp-t-dim")

    def vdim(self, x, y0, y1, xfrom, label, left=True):
        """A dimension along Y at x, with extension lines from xfrom (none if None), the figure beside the line on its
        left or right, turned to read upward."""
        for y in (y0, y1):
            if xfrom is not None:
                s = 1 if x >= xfrom else -1
                self.line(xfrom + s * 20, y, x + s * 45, y, "fp-ext")
            self.line(x - 28, y - 28, x + 28, y + 28, "fp-tick")
        self.line(x, y0 - 60, x, y1 + 60, "fp-dim")
        self.text(x - 40 if left else x + 40 + 0.75 * T_DIM, (y0 + y1) / 2, label, T_DIM, "fp-t-dim", rot=-90)


NOLABEL = ("WR-01", "EL-01", "EL-02", "LA-14F", "LB-02", "LB-03", "LB-04")   # floors, covered boxes and the bed's layers


def _overlaps(a, b, pad=0.0) -> bool:
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def _label_box(x, y, s, size, rot=False):
    w = text_w(s, size)
    return (x - 0.75 * size / 2 - 0.1 * size, y - w / 2, x + 0.75 * size / 2, y + w / 2) if rot else \
        (x - w / 2, y - 0.2 * size, x + w / 2, y + 0.8 * size)


def _place_labels(g, p, placed):
    """Each part below the cut named inside its outline where the name fits, nothing covers it and no other text is
    there, upright or turned for a tall narrow part."""
    shown = [q for q in p["parts"] if q["kind"] != "above"]
    for n, q in enumerate(shown):
        if q["id"] in NOLABEL:
            continue
        xs = [x for lp in q["outline"] for x, _ in lp]
        ys = [y for lp in q["outline"] for _, y in lp]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        if any(_overlaps((x0 + 5, y0 + 5, x1 - 5, y1 - 5), (min(x for lp in r["outline"] for x, _ in lp),
                                                         min(y for lp in r["outline"] for _, y in lp),
                                                         max(x for lp in r["outline"] for x, _ in lp),
                                                         max(y for lp in r["outline"] for _, y in lp)))
               for r in shown[n + 1:]):
            continue
        s = short_name(q["iid"], q["id"], q["name"])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for size in (T_PART, 0.85 * T_PART):
            flat = text_w(s, size) + 60 <= x1 - x0 and 1.3 * size <= y1 - y0
            tall = text_w(s, size) + 60 <= y1 - y0 and 1.3 * size <= x1 - x0
            if flat or tall:
                bx = _label_box(cx, cy - 0.3 * size, s, size) if flat else _label_box(cx + 0.3 * size, cy, s, size, rot=True)
                if any(_overlaps(bx, o, 20) for o in placed):
                    break
                placed.append(bx)
                if flat:
                    g.text(cx, cy - 0.35 * size, s, size, "fp-t-part")
                else:
                    g.text(cx + 0.35 * size, cy, s, size, "fp-t-part", rot=-90)
                break


def svg(p) -> str:
    """The plan of one bed position as an inline SVG in mm, front to the left and the road side up. Each part is a
    group named by its line (data-iid, data-id, data-name) for the page's hover card and its parts table."""
    g = _Svg(p)
    bx0, _, bx1, hb = p["body"]
    ix0, iy0, ix1, iy1 = p["inside"]
    st = p["stations"]
    g.out.append(f'<path class="fp-floor" d="{g.d([_rect(ix0, iy0, ix1, iy1)])}"/>')
    clear = "".join(f'<g class="fp-part fp-k" data-iid="{_esc(c["iid"])}" data-id="{_esc(c["id"])}" data-name="{_esc(c["name"])}" '
                    f'data-kind="clear"><path class="fp-fill" d="{g.d(c["outline"])}"/></g>' for c in p["clear"])
    for q in p["parts"]:
        if clear and q["top"] > p["floor_z"] + FLOOR_TOP:   # the spaces kept clear lie on the floor and its finishes
            g.out.append(clear)
            clear = ""
        if q["kind"] == "above":
            continue
        body = f'<path class="fp-fill" d="{g.d(q["outline"])}"/>'
        if q["edges"]:
            body += f'<path class="fp-edge" d="{g.d(q["edges"], closed=False)}"/>'
        if q["cut"]:
            body += f'<path class="fp-cut" d="{" ".join(g.d(f) for f in q["cut"])}"/>'
        g.group(q, f'fp-a-{q["area"]} fp-{q["kind"]}', body)
    g.out.append(clear)
    for q in p["parts"]:
        if q.get("under"):
            dd = g.d(q["outline"])
            g.group({**q, "kind": "under"}, f'fp-a-{q["area"]} fp-under', f'<path class="fp-dash" d="{dd}"/><path class="fp-hit" d="{dd}"/>')
    for w in p["walls"]:
        g.group(w, "fp-wall", f'<path class="fp-poche" d="{" ".join(g.d(f) for f in w["cut"])}"/>')
    for w in p["windows"]:
        x0, y0, x1, y1 = w["box"]
        r = [_rect(x0, y0, x1, y1)]
        if not w["cut"]:
            g.group(w, "fp-win fp-high", f'<path class="fp-highwin" d="{g.d(r)}"/>')
            continue
        side = w["wall"] in ("kerb", "road")
        glass = [[(x0, y0 + f * (y1 - y0)), (x1, y0 + f * (y1 - y0))] if side else
                 [(x0 + f * (x1 - x0), y0), (x0 + f * (x1 - x0), y1)] for f in (0.35, 0.65)]
        g.group(w, "fp-win", f'<path class="fp-gap" d="{g.d(r)}"/><path class="fp-glass" d="{g.d(glass, closed=False)}"/>')
    for dr in p["doors"]:
        g.group(dr, "fp-door", f'<path class="fp-gap" d="{g.d([dr["gap"]])}"/><path class="fp-leaf" d="{g.d([dr["leaf"]])}"/>'
                               f'<path class="fp-swing" d="{g.d([dr["arc"]], closed=False)}"/>')
    for q in p["parts"]:
        if q["kind"] == "above":
            dd = g.d(q["outline"])
            g.group(q, f'fp-a-{q["area"]} fp-above' + (" fp-bedup" if q["area"] == "bed" else ""),
                    f'<path class="fp-dash" d="{dd}"/><path class="fp-hit" d="{dd}"/>')
    g.out.append('<g class="fp-notes">')
    _notes(g, p, bx0, bx1, hb, ix0, iy0, ix1, iy1, st)
    g.out.append("</g>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="fp-svg" viewBox="0 0 {g.W:.0f} {g.H:.0f}" role="img" '
            f'aria-label="{_esc(p["title"])}: floor plan cut {p["cut_mm"]:.0f} mm above the floor, front to the left, road side up">'
            + "".join(g.out) + "</svg>\n")


def _notes(g, p, bx0, bx1, hb, ix0, iy0, ix1, iy1, st):
    """The plan's names, dimensions, sides and scale bar."""
    dm, ax0, ay0, ax1, ay1 = p["dims"], *p["aisle"]
    wx0, wy0, wx1, wy1 = p["walk_band"]
    placed = []
    bed_up = any(q["kind"] == "above" and q["area"] == "bed" for q in p["parts"])
    for key, x, y in (("bed", (st[0] + st[1]) / 2 + 150, iy0 + 230), ("kit", (ax0 + ax1) / 2 + 320, ay1 - 120 - 0.8 * T_AREA),
                      ("lau", (ax0 + ax1) / 2 + 320, ay0 + 120), ("wet", (st[2] + st[3]) / 2, iy1 - 120 - 0.8 * T_AREA)):
        g.text(x, y, AREAS[key], T_AREA, f"fp-t-area fp-c-{key}")
        placed.append(_label_box(x, y, AREAS[key], T_AREA))
    if bed_up:                       # between the mattress's dashed edge and the desk
        x, y = (st[0] + st[1]) / 2 + 150, iy1 - 420
        g.text(x, y, "Bed above, dashed", T_PART, "fp-t-note")
        placed.append(_label_box(x, y, "Bed above, dashed", T_PART))
    if p.get("shower"):
        x0, y0, x1, y1 = p["shower"]
        x, y = (x0 + x1) / 2, (y0 + y1) / 2 + 60
        g.text(x, y, "Shower", T_PART, "fp-t-note fp-c-wet")
        placed.append(_label_box(x, y, "Shower", T_PART))
    solid = [q["box"] for q in p["parts"] if q["kind"] != "above" and q["top"] > p["floor_z"] + FLOOR_TOP]
    for c in p["clear"]:                # each mark in the first corner of its space clear of the parts and the names
        x0, y0, x1, y1 = c["box"]
        s, w, h = 0.8 * T_MARK, text_w(c["mark"], 0.8 * T_MARK), 0.8 * T_MARK
        for x, y in ((x0 + 40, y0 + 40), (x0 + 40, y1 - 40 - h), (x1 - 40 - w, y0 + 40), (x1 - 40 - w, y1 - 40 - h)):
            bx = (x, y, x + w, y + h)
            if not any(_overlaps(bx, o) for o in solid) and not any(_overlaps(bx, o, 20) for o in placed):
                g.text(x, y, c["mark"], s, "fp-t-k", anchor="start")
                placed.append(bx)
                break
    inner = next(d for d in p["doors"] if d["iid"] == "WR-04")
    xw = max(x for x, _ in inner["leaf"]) + 40          # the walk band's figure clear of the inner door's swing
    g.vdim(ax0 + 380, ay0, ay1, None, f"{dm['aisle']:,.0f} aisle", left=False)
    g.vdim(xw, wy0, wy1, None, f"{dm['walk_band']:,.0f} walk band", left=False)
    placed += [(ax0 + 340, ay0, ax0 + 480, ay1), (xw - 40, wy0, xw + 140, wy1)]
    _place_labels(g, p, placed)
    # openings' marks outside the walls
    for w in p["windows"]:
        x0, y0, x1, y1 = w["box"]
        cx = (x0 + x1) / 2
        if w["wall"] == "road":
            g.text(cx, hb + 50, w["mark"], T_MARK, "fp-t-mark")
        elif w["wall"] == "kerb":
            g.text(cx, -hb - 50 - 0.75 * T_MARK, w["mark"], T_MARK, "fp-t-mark")
    for dr in p["doors"]:
        tx, ty = dr["leaf"][1]
        if dr["iid"] == "BD-07":
            g.text(tx - 60, ty + 20, f"{dr['mark']} entry door", T_MARK, "fp-t-mark", anchor="end")
        elif dr["iid"] == "BD-15":
            g.text(bx1 + 50, ty - 110 - 0.75 * T_MARK, f"{dr['mark']} rear door", T_MARK, "fp-t-mark", anchor="start")
    # dimensions: the zones and the inside length along the road side, the inside width at the front
    for (a, b), lab in zip(zip(st, st[1:]), (f"{dm['bed']:,.0f} bed and desk", f"{dm['living']:,.0f} living",
                                            f"{dm['rear']:,.0f} wet room")):
        g.hdim(a, b, hb + 330, hb, lab)
    g.hdim(st[0], st[3], hb + 570, hb + 330, f"{dm['inside_length']:,.0f} inside")
    g.vdim(bx0 - 120, iy0, iy1, bx0, f"{dm['inside_width']:,.0f} inside")
    # sides and the front
    g.text(bx0 - LEFT + 30, hb + 100, "Road side", T_DIM, "fp-t-side", anchor="start")
    g.text(bx0 - LEFT + 30, -hb - 100 - 0.75 * T_DIM, "Kerb side", T_DIM, "fp-t-side", anchor="start")
    xa = bx0 - LEFT + 20             # an arrow pointing to the front, drawn, since a symbol font may show it in colour
    g.out.append(f'<path class="fp-arrow" d="{g.d([[(xa, 0.0), (xa + 80, 45.0), (xa + 80, -45.0)]])}"/>')
    g.text(xa + 105, -0.35 * T_DIM, "Front", T_DIM, "fp-t-side", anchor="start")
    # scale bar, 2 m in 500 mm steps
    x0, y = bx1 - 2000, -hb - 520
    for k in range(4):
        cls = "fp-bar fp-bar-on" if k % 2 == 0 else "fp-bar"
        g.out.append(f'<path class="{cls}" d="{g.d([_rect(x0 + 500 * k, y, x0 + 500 * (k + 1), y + 50)])}"/>')
    for v, lab in ((0, "0"), (1000, "1 m"), (2000, "2 m")):
        g.text(x0 + v, y - 40 - 0.75 * T_DIM, lab, T_DIM, "fp-t-dim")


def write_plans(day, night, res, out: Path, tms=None) -> dict:
    """Both bed positions: build/floorplan/floorplan.json for CT-010 and the tests, and an SVG of each for the page.
    `tms` gives each layout's TrailerModel with the designed body, built here when not given."""
    import time
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    plans = {}
    for (state, lay), tm in zip((("day", day), ("night", night)), tms or (None, None)):
        plans[state] = plan(lay, res, tm, state)
        (out / f"floorplan-{state}.svg").write_text(svg(plans[state]), encoding="utf-8")
    # the viewer's plan view (site/src/components/CadViewer.astro) cuts these models at cut_z and frames the body
    data = dict(cut_mm=CUT, floor_z=day.V["floor_z"], cut_z=day.V["floor_z"] + CUT, areas=AREAS, body=plans["day"]["body"],
                models=["trailer", "body-inside", "body-inside-night"], plans=plans)
    (out / "floorplan.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    n = {k: len(v["parts"]) for k, v in plans.items()}
    print(f"floor plan: {n['day']} parts bed up, {n['night']} bed down, cut at Z {data['cut_z']:.0f} ({time.time() - t0:.1f} s)")
    return data

"""H27: nothing in the trailer's 3D models floats (Leonard, 22 Nov 2026: "Many of the models are floating").

Each model the trailer pages show is broken into its solids. Two solids are joined where they touch, or overlap by
1 mm or less, over a real area: a contact patch at least W_MIN wide and A_MIN in area, not a point or an edge. Solids
that overlap by more than 1 mm are joined too, as they are welded, bonded, bolted through or let into one another.

1. Every solid connects through these joints to the ground, through the tyres, the jockey wheel or the corner steadies.
   The Body page's three models show the body off its chassis, so their root is the floor panel BD-01, which stands on
   the chassis's 32 mounts in the trailer model, where the same test reaches it from the tyres.
2. Every line of the fit-out and of the drawbar box stands on something below it, or hangs from what its maker's
   guide fixes it to (HANGS, with that fixing). A line's own pieces do not hold it up.
"""
from __future__ import annotations

import functools
import math

import pytest
from build123d import Compound, GeomType, Vector, extrude

TOL = 1.0       # mm: a joint's gap or shallow overlap
W_MIN = 3.0     # mm: the narrowest contact patch that counts as an area
A_MIN = 25.0    # mm2
STANDS = ("bed", "living", "electrical", "hvac", "wet_room", "stowage", "spare", "payload")
ROOTS = ("RG-02", "DB-05", "CH-B01")           # tyres, jockey wheel, corner steadies: they stand on the ground
# lines that hang from a wall, the ceiling or a frame, by the fixing their maker or the design shows
HANGS = {
    "LB-04": "the rails screw into the hardpoints in the side walls (Lippert's HappiJac guide, LB-06)",
    "LA-11L": "overhead lockers screw through their back rail into the kerb wall's insert strips",
    "LA-11E": "the board cabinet screws to the partition and to the kerb wall",
    "EL-04": "the MultiPlus-II hangs on its wall bracket on the partition (Victron's manual)",
    "EL-05": "the Lynx Smart BMS, the MPPTs and the Orion-Tr converters screw to the board panel",
    "EL-06": "the board panel screws to the cabinet's back, the Lynx Distributor, Cerbo GX and 230 V board to the panel",
    "AC-01": "the indoor unit hangs on its installation plate on the partition (Mitsubishi Electric's guide)",
    "AC-02": "the outdoor unit bolts to its cradle (AC-03)",
    "AC-03": "the cradle bolts to the rear wall and stands on its stays (AC-04, BDY-21)",
    "AC-04": "the stays bolt to the rear wall and to the rear crossmember",
    "VE-01": "each LUNOS e2 sleeve is let into the wall and sealed (LUNOS's guide)",
    "VE-03": "the RA 15-60 sleeve is let into the rear wall (LUNOS's guide)",
    "VE-04": "the RESPA-CF2 bolts to the road wall behind its intake hood (Sy-Klone's guide)",
    "VE-05": "the top-up fan's box screws to the road wall beside the RESPA",
    "VE-07": "the range hood screws to the underside of the cupboard over the bench and to the road wall",
    "WR-08": "the basin, mirror cabinet and towel rail screw to the partition",
    "WR-09": "the DauerShower's technical unit screws to the partition in its dry cabinet",
    "WR-03": "the partition is bonded to the tray, the walls and the ceiling",
    "LA-07A": "the hob drops into its cut-out in the worktop and clamps under it (Dometic's guide)",
    "LA-07B": "the sink drops into its cut-out in the worktop and clamps under it (Dometic's guide)",
    "LB-03": "the platform bolts to the HappiJac carriages on the four rails",
    "LB-01": "the mattress lies on the underlay on the platform",
    "SP-01": "the spare hangs on the carrier posts' hub plate",
    "LG-02": "each cap is riveted over an outrigger's open end",
    "PL-03A": "the gear lies on the drawbar box's shelf",
}


# ------------------------------------------------------------------ the models
@functools.lru_cache(maxsize=None)
def _layouts():
    import json
    from cad.partsdb import ROOT, Project
    from cad.trailer import Trailer
    tr = Trailer(Project(), ute=False)
    rep = ROOT / "build" / "trailer" / "trailer.json"
    over = json.loads(rep.read_text())["solved"]["overrides"] if rep.exists() else {}
    return tr.layout(**over), tr.layout(**{**over, "bed_state": 1})


@functools.lru_cache(maxsize=None)
def model_tree(name: str) -> Compound:
    from cad.trailer_model import TrailerModel, body_models
    day, night = _layouts()
    if name == "trailer":
        return TrailerModel(day, body=True).compound()
    return body_models(day, night)[name]


def _leaves(shape, path=()):
    path = path + (shape.label or "",)
    kids = list(shape.children) if isinstance(shape, Compound) else []
    if kids:
        for k in kids:
            yield from _leaves(k, path)
    elif shape.solids():
        yield path, shape


class Node:
    def __init__(self, path, shape):
        self.path, self.shape = path, shape
        self.key = path[2].split(" ")[0] if len(path) > 2 else path[-1].split(" ")[0]
        self.line = self.key.split(".")[0]
        bb = shape.bounding_box()
        self.bb = (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)
        self.is_box = _is_box(shape, self.bb)
        self._faces = None

    @property
    def name(self):
        return " / ".join(p for p in self.path[2:] if p) or self.path[-1]

    def planar_faces(self):
        if self._faces is None:
            self._faces = []
            for f in self.shape.faces():
                if f.geom_type == GeomType.PLANE:
                    fb = f.bounding_box()
                    self._faces.append((f, f.normal_at(), f.center(), (fb.min.X, fb.min.Y, fb.min.Z, fb.max.X, fb.max.Y, fb.max.Z)))
        return self._faces


def _is_box(shape, bb) -> bool:
    if len(shape.solids()) != 1:
        return False
    fs = shape.faces()
    if len(fs) != 6 or any(f.geom_type != GeomType.PLANE for f in fs):
        return False
    vol = (bb[3] - bb[0]) * (bb[4] - bb[1]) * (bb[5] - bb[2])
    return vol > 0 and abs(shape.volume - vol) < 1e-6 * vol


def _common(a, b):
    """The common volume of two shapes and its bounding box sizes, or (0, None)."""
    c = a.intersect(b)
    if c is None:
        return 0.0, None
    parts = list(c) if not hasattr(c, "volume") else [c]
    vol = sum(p.volume for p in parts if hasattr(p, "volume"))
    if vol <= 1e-2:
        return 0.0, None
    bb = Compound(children=[p for p in parts]).bounding_box() if len(parts) > 1 else parts[0].bounding_box()
    return vol, [bb.size.X, bb.size.Y, bb.size.Z]


def _near(a, b, tol=TOL) -> bool:
    return all(min(a[i + 3], b[i + 3]) - max(a[i], b[i]) >= -tol for i in range(3))


# ------------------------------------------------------------------ joints
def _patch(o, i):
    """A contact across axis i with the in-plane overlaps o: an area, or None for an edge or a point."""
    j, k = [m for m in range(3) if m != i]
    return o[j] >= W_MIN and o[k] >= W_MIN and o[j] * o[k] >= A_MIN


def _side(a, b, i) -> int:
    """+1 if b lies on the positive side of a along axis i."""
    return 1 if (a[i] + a[i + 3]) < (b[i] + b[i + 3]) else -1


def joint(a: Node, b: Node):
    """('embed', None) for a deep overlap, ('face', (axis, side)) for a contact over an area, else None."""
    A, B = a.bb, b.bb
    o = [min(A[i + 3], B[i + 3]) - max(A[i], B[i]) for i in range(3)]
    if min(o) < -TOL:
        return None
    if a.is_box and b.is_box:
        close = [i for i in range(3) if o[i] <= TOL]
        if not close:
            return ("embed", None)
        if len(close) == 1 and _patch(o, close[0]):
            return ("face", (close[0], _side(A, B, close[0])))
        return None
    if a.shape.distance_to(b.shape) > TOL:
        return None
    vol, ext = _common(a.shape, b.shape)
    if vol:
        i = min(range(3), key=lambda m: ext[m])
        if ext[i] > TOL:
            return ("embed", None)
        if _patch(ext, i):
            return ("face", (i, _side(A, B, i)))
        return None
    return _touch(a, b)


def _touch(a: Node, b: Node):
    """Planar faces of a and b that face each other within TOL: the patch is a thin slab off a's face cut by b."""
    best = None
    for fa, na, ca, ba in a.planar_faces():
        if not _near(ba, b.bb):
            continue
        for fb, nb, cb, bbb in b.planar_faces():
            if na.dot(nb) > -0.999 or not _near(ba, bbb):
                continue
            sep = (cb - ca).dot(na)
            if not -TOL <= sep <= TOL:
                continue
            slab = extrude(fa, amount=TOL + 0.5, dir=na)
            vol, ext = _common(slab, b.shape)
            if not vol:
                continue
            i = max(range(3), key=lambda m: abs((na.X, na.Y, na.Z)[m]))
            if _patch(ext, i):
                best = ("face", (i, 1 if (na.X, na.Y, na.Z)[i] > 0 else -1))
                if i == 2:
                    return best
    return best


# ------------------------------------------------------------------ the graph
@functools.lru_cache(maxsize=None)
def graph(name: str):
    nodes = [Node(p, s) for p, s in _leaves(model_tree(name))]
    order = sorted(range(len(nodes)), key=lambda n: nodes[n].bb[0])
    edges: dict[int, list] = {n: [] for n in range(len(nodes))}
    for ii, n in enumerate(order):
        a = nodes[n]
        for m in order[ii + 1:]:
            b = nodes[m]
            if b.bb[0] > a.bb[3] + TOL:
                break
            if not _near(a.bb, b.bb):
                continue
            j = joint(a, b)
            if j is None:
                continue
            kind, d = j
            edges[n].append((m, kind, d))
            edges[m].append((n, kind, None if d is None else (d[0], -d[1])))
    return nodes, edges


def roots(name: str, nodes) -> list[int]:
    import os
    extra = tuple(os.environ.get("SUPPORT_EXTRA_ROOTS", "").split(",")) if os.environ.get("SUPPORT_EXTRA_ROOTS") else ()
    if name == "trailer":
        return [n for n, x in enumerate(nodes) if (x.line in ROOTS and x.bb[2] <= TOL) or x.key in extra]
    return [n for n, x in enumerate(nodes) if x.line == "BD-01"]


def floating(name: str) -> list[str]:
    """The solids that no chain of joints connects to a root, by name."""
    nodes, edges = graph(name)
    seen = set(roots(name, nodes))
    todo = list(seen)
    while todo:
        n = todo.pop()
        for m, _, _ in edges[n]:
            if m not in seen:
                seen.add(m)
                todo.append(m)
    return sorted(nodes[n].name for n in range(len(nodes)) if n not in seen)


def unsupported(name: str) -> list[str]:
    """The fit-out and drawbar box lines that stand on nothing and hang from nothing their maker fixes them to."""
    from cad.trailer import SYSTEM_LABELS
    nodes, edges = graph(name)
    day, _ = _layouts()
    system = {b.iid: b.system for b in day.blocks} | {b.id: b.system for b in day.blocks}
    lines: dict[str, list[int]] = {}
    for n, x in enumerate(nodes):
        if system.get(x.key) in STANDS:
            lines.setdefault(x.key, []).append(n)
    out = []
    for key, ns in sorted(lines.items()):
        line = key.split(".")[0]
        hang = HANGS.get(line) or HANGS.get(line.rstrip("ABCD"))
        held = False
        for n in ns:
            for m, kind, d in edges[n]:
                if nodes[m].key == key:
                    continue
                if hang or kind == "embed" or (d[0] == 2 and d[1] < 0):
                    held = True
                    break
            if held:
                break
        if not held:
            out.append(f"{key} ({SYSTEM_LABELS.get(system[key], system[key])})")
    return out


MODELS = ("trailer", "body", "body-inside", "body-inside-night")


@pytest.mark.parametrize("name", MODELS)
def test_nothing_floats(name):
    nodes, _ = graph(name)
    assert roots(name, nodes), f"{name}: no root solid"
    bad = floating(name)
    assert not bad, f"{name}: {len(bad)} solids float: " + "; ".join(bad[:40])


@pytest.mark.parametrize("name", ("trailer", "body-inside", "body-inside-night"))
def test_the_fit_out_stands_or_hangs(name):
    bad = unsupported(name)
    assert not bad, f"{name}: {len(bad)} lines stand on nothing: " + "; ".join(bad)


if __name__ == "__main__":
    import sys
    import time
    for name in sys.argv[1:] or MODELS:
        t = time.time()
        nodes, edges = graph(name)
        print(f"== {name}: {len(nodes)} solids, {sum(len(e) for e in edges.values()) // 2} joints, {time.time() - t:.1f} s")
        for f in floating(name):
            print("  floats:", f)
        if name != "body":
            for u in unsupported(name):
                print("  stands on nothing:", u)

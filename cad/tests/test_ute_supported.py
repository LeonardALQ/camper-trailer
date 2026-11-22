"""Decision H27: nothing in the ute's 3D models floats. Every solid stands on, hangs from or is fixed to a modelled part.

The check is a contact graph of the solids in the two viewer models, `ute` (travelling) and `ute-loading` (cad/ute_model.py).
Two solids are joined where they touch or come within 1 mm of each other over a real area: pushed 1 mm further
together, their common volume is at least 1 mm3, which a point or a corner contact does not reach. A solid that overlaps
another is joined to it. The ute stands on its four tyres, and in the loading model the assumed ground (C3) carries the
ramp's foot and the bike being loaded. Every solid must reach one of them through the graph. On top of that, each bike
stands on its own tyres with the straps taken out, its tyres stand on the box floor, a chock or the ramp, each strap
touches its bike and a track fitting, and each chock touches the floor.

The graph is built with union-find: pairs whose boxes come within 1 mm are tried cheapest first, and a pair whose two
solids are already connected is skipped, so the costly pairs (a tyre on its rim) are only measured when nothing else
joins them.
"""
from __future__ import annotations

import numpy as np
import pytest
from build123d import Compound, Location
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.Extrema import Extrema_ExtFlag_MIN

TOL = 1.0          # mm, the gap that still counts as touching
MIN_VOL = 1.0      # mm3 of common volume once the pair is pushed TOL further together
_SHARED: dict[tuple, bool] = {}    # measurements by (path, box) of both solids, shared by the two models' graphs


def _nodes(shape, path=""):
    """(path, solid) for every solid in the model tree."""
    here = f"{path}/{shape.label}" if shape.label else path
    kids = list(shape.children) if isinstance(shape, Compound) and shape.children else []
    if kids:
        out = []
        for k in kids:
            out.extend(_nodes(k, here))
        return out
    return [(here, s) for s in shape.solids()]


def _vol(shape) -> float:
    if shape is None:
        return 0.0
    try:
        return sum(abs(s.volume) for s in shape.solids()) if hasattr(shape, "solids") else abs(shape.volume)
    except Exception:
        return 0.0


def _common(a, b) -> float:
    try:
        return _vol(a.intersect(b))
    except Exception:
        return 0.0


class Graph:
    def __init__(self, comp):
        self.nodes = _nodes(comp)
        n = len(self.nodes)
        bbs = [s.bounding_box() for _, s in self.nodes]
        self.lo = np.array([[b.min.X, b.min.Y, b.min.Z] for b in bbs])
        self.hi = np.array([[b.max.X, b.max.Y, b.max.Z] for b in bbs])
        faces = [len(s.faces()) for _, s in self.nodes]
        self._known: dict[tuple[int, int], bool] = {}
        cand = []
        for i in range(n):
            for j in self.near(i, range(i + 1, n)):
                cand.append((faces[i] * faces[j], i, j))
        self.pairs = [(i, j) for _, i, j in sorted(cand)]
        self.parent = self._join(range(n))

    def near(self, i, others):
        """The solids among `others` whose boxes come within TOL of solid i's."""
        js = np.array([j for j in others if j != i], dtype=int)
        if not len(js):
            return []
        ok = np.all((self.lo[js] <= self.hi[i] + TOL) & (self.hi[js] >= self.lo[i] - TOL), axis=1)
        return [int(j) for j in js[ok]]

    def joined(self, i, j) -> bool:
        key = (min(i, j), max(i, j))
        if key not in self._known:
            # the two models share most of their solids, the same parts in the same places: one measurement serves both
            same = tuple(sorted((self.nodes[k][0], tuple(np.round(self.lo[k], 2)), tuple(np.round(self.hi[k], 2))) for k in key))
            if same not in _SHARED:
                _SHARED[same] = self._measure(*key)
            self._known[key] = _SHARED[same]
        return self._known[key]

    def _measure(self, i, j) -> bool:
        a, b = self.nodes[i][1], self.nodes[j][1]
        ext = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped, 0.01, Extrema_ExtFlag_MIN)
        if not ext.IsDone():
            return False
        d = ext.Value()
        if d > TOL:
            return False
        if d > 1e-3:
            p, q = ext.PointOnShape1(1), ext.PointOnShape2(1)
            v = np.array([p.X() - q.X(), p.Y() - q.Y(), p.Z() - q.Z()])
            dirs = [v / np.linalg.norm(v)]
        else:
            if _common(a, b) >= MIN_VOL:
                return True
            # touching faces: push along the axis on which the boxes only just meet first, then the others
            lo, hi = np.maximum(self.lo[i], self.lo[j]), np.minimum(self.hi[i], self.hi[j])
            dirs = [s * np.eye(3)[ax] for ax in np.argsort(hi - lo) for s in (1.0, -1.0)]
        for e in dirs:
            if _common(a, b.moved(Location(tuple(float(x) * (TOL + d) for x in e)))) >= MIN_VOL:
                return True
        return False

    def _join(self, subset):
        """Union-find over the solids in `subset`, joining the candidate pairs inside it, cheapest first."""
        keep = set(subset)
        parent = {i: i for i in keep}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i, j in self.pairs:
            if i in keep and j in keep:
                ri, rj = find(i), find(j)
                if ri != rj and self.joined(i, j):
                    parent[ri] = rj
        return {i: find(i) for i in keep}

    def components(self, subset=None) -> list[set[int]]:
        parent = self.parent if subset is None else self._join(subset)
        groups: dict[int, set[int]] = {}
        for i, r in parent.items():
            groups.setdefault(r, set()).add(i)
        return list(groups.values())

    def touches(self, i, others) -> bool:
        return any(self.joined(i, j) for j in self.near(i, others))

    def find(self, word) -> list[int]:
        return [i for i, (p, _) in enumerate(self.nodes) if word in p]


def _is_root(path) -> bool:
    leaf = path.rsplit("/", 1)[-1]
    return "/WH-" in path and "tyre" in leaf or "/C3 " in path


_GRAPHS: dict[str, Graph] = {}


def graph(name) -> Graph:
    if name not in _GRAPHS:
        from cad.tests.test_ute import GMODEL, UTE
        from cad.ute_model import ute_compound
        _GRAPHS[name] = Graph(ute_compound(UTE, GMODEL, loading=name == "ute-loading"))
    return _GRAPHS[name]


def _product(path) -> str:
    """The node a person points at: the bike, the box part or the ute part, not its sub-solid."""
    bits = path.split("/")
    return "/".join(bits[:5]) if "/Bike garage/" in path else "/".join(bits[:4])


def floating(g: Graph) -> list[str]:
    out = []
    for comp in g.components():
        if not any(_is_root(g.nodes[i][0]) for i in comp):
            out.extend(g.nodes[i][0] for i in comp)
    return sorted(out)


def _report(paths) -> str:
    by: dict[str, int] = {}
    for p in paths:
        by[_product(p)] = by.get(_product(p), 0) + 1
    return "\n".join(f"  {k} ({v} solid{'s' if v > 1 else ''})" for k, v in sorted(by.items()))


@pytest.mark.parametrize("name", ["ute", "ute-loading"])
def test_nothing_floats(name):
    g = graph(name)
    assert any(_is_root(p) for p, _ in g.nodes), "no ute tyres in the model"
    bad = floating(g)
    assert not bad, f"{name}: {len(bad)} of {len(g.nodes)} solids reach neither the ute's tyres nor the ground:\n{_report(bad)}"


def _bikes(g: Graph) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for i, (p, _) in enumerate(g.nodes):
        bits = p.split("/")
        if len(bits) > 4 and bits[3] == "Bikes":
            out.setdefault(bits[4], []).append(i)
    return out


@pytest.mark.parametrize("name", ["ute", "ute-loading"])
def test_bikes_stand_on_their_tyres(name):
    g = graph(name)
    bikes = _bikes(g)
    assert bikes, "no bikes in the model"
    floor = g.find("/B1 ") + g.find("/10.") + g.find("/R2 ") + g.find("/C3 ")
    problems = []
    for bike, ids in bikes.items():
        tyres = [i for i in ids if g.nodes[i][0].endswith("tyre")]
        if not tyres:
            problems.append(f"{bike}: no tyres")
            continue
        by_tyre: dict[str, list[int]] = {}
        for t in tyres:
            by_tyre.setdefault(g.nodes[t][0], []).append(t)
        for path, solids in by_tyre.items():
            if not any(g.touches(t, floor) for t in solids):
                problems.append(f"{bike}: {path.rsplit('/', 1)[-1]} touches neither the floor, a chock nor the ramp")
        own = next(c for c in g.components(ids) if tyres[0] in c)
        loose = sorted({g.nodes[i][0].rsplit("/", 1)[-1] for i in ids if i not in own})
        if loose:
            problems.append(f"{bike}: these parts do not reach its tyres through the bike itself: {', '.join(loose)}")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("name", ["ute", "ute-loading"])
def test_straps_and_chocks_touch_what_holds_them(name):
    g = graph(name)
    bikes = _bikes(g)
    fittings = g.find("/12.")
    floor = g.find("/B1 ")
    problems = []
    for i in g.find("/13."):
        strap = g.nodes[i][0].split("/")[4]
        who = strap.split(".")[1][:2]
        mine = [j for b, ids in bikes.items() if b.startswith(who + " ") for j in ids]
        if not g.touches(i, mine):
            problems.append(f"{strap}: does not touch its bike")
        if not g.touches(i, fittings):
            problems.append(f"{strap}: does not touch a track fitting")
    for i in g.find("/10."):
        if not g.touches(i, floor):
            problems.append(f"{g.nodes[i][0].split('/')[4]}: chock does not stand on the floor")
    assert not problems, "\n".join(problems)

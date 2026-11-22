"""Decision H27: nothing in the ute's 3D models floats. Every solid stands on, hangs from or is fixed to a modelled part.

The check is a contact graph of the solids in the two viewer models, `ute` (travelling) and `ute-loading` (cad/ute_model.py).
Two solids touch where they come within 1 mm of each other over a real area: pushed 1 mm further together, their common
volume is at least W_MIN wide both ways across the push and A_MIN in area, which an edge or a corner does not reach.
Where solids of two parts overlap by more than 1 mm, they are joined only if data/assemblies/fixings.yaml says one is
welded, bonded or let into the other. Anywhere else a deep overlap is two parts in one space, and it holds nothing.
The ute stands on its four tyres, and in the loading model the assumed ground (C3) carries the ramp's foot and the bike
being loaded. Every solid must reach one of them through the graph, and every part must stand on another (the other
below it over an area) or be held by a fixing that fixings.yaml lists, with the same rules as the trailer's test
(test_supported.py). On top of that, each bike stands on its own tyres with the straps taken out, its tyres stand on the
box floor, a chock or the ramp, each strap touches its bike and a track fitting, and each chock touches the floor.

The graph is built with union-find: pairs whose boxes come within 1 mm are tried cheapest first, and a pair whose two
solids are already connected is skipped, so the costly pairs (a tyre on its rim) are only measured when nothing else
joins them.
"""
from __future__ import annotations

import fnmatch
import functools

import numpy as np
import pytest
from build123d import Compound, Location, Plane
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.Extrema import Extrema_ExtFlag_MIN

from cad.tests.test_supported import A_MIN, EMBEDS, EPS, FIX_W, FIXINGS, W_MIN

TOL = 1.0          # mm, the gap that still counts as touching
MIN_VOL = 1.0      # mm3: a smaller common volume is no contact at all
_SHARED: dict[tuple, tuple | None] = {}    # contacts by (path, box) of both solids, shared by the two models' graphs


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


def _solid(shape):
    if shape is None:
        return None
    try:
        sols = shape.solids() if hasattr(shape, "solids") else [shape]
        return sols if sum(abs(s.volume) for s in sols) >= MIN_VOL else None
    except Exception:
        return None


def _common(a, b):
    try:
        return _solid(a.intersect(b))
    except Exception:
        return None


def _across(sols, e) -> tuple[float, float]:
    """The common volume's two widths across the direction e, narrower first."""
    z = np.asarray(e, float) / np.linalg.norm(e)
    ref = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
    x = np.cross(ref, z)
    pl = Plane(origin=(0, 0, 0), x_dir=tuple(x / np.linalg.norm(x)), z_dir=tuple(z))
    bb = Compound(children=[pl.to_local_coords(s) for s in sols]).bounding_box()
    return tuple(sorted((bb.size.X, bb.size.Y)))


def _volume(sols) -> float:
    return sum(abs(s.volume) for s in sols)


def _overlap(c, ca, cb):
    """A common volume c of two solids whose centres are ca and cb: ('embed', ...) if thicker than TOL, else a contact
    across its thin direction, or a seat where it is curved and thin in no one direction."""
    vol, area = _volume(c), sum(s.area for s in c)
    t = 2 * vol / area
    if t > TOL:
        return ("embed", None, 0.0, 0.0)
    bb = Compound(children=list(c)).bounding_box() if len(c) > 1 else c[0].bounding_box()
    size = [bb.size.X, bb.size.Y, bb.size.Z]
    i = int(np.argmin(size))
    if size[i] > 2 * TOL:
        return ("seat", None, (area / 2) ** 0.5, area / 2)
    e = np.eye(3)[i] * (1.0 if cb[i] > ca[i] else -1.0)
    w = sorted(s for k, s in enumerate(size) if k != i)
    return ("face", tuple(e), w[0], vol / max(size[i], 1e-6)) if w[0] >= W_MIN - EPS and vol / max(size[i], 1e-6) >= A_MIN else None


def contact(a, b, lo, hi):
    """How solid b meets solid a (lo and hi are their two boxes' corners, a's first): ('face', e, width, area) with e the
    unit vector from a to b, ('seat', None, width, area), ('embed', None, 0, 0) for an overlap deeper than TOL, or None."""
    ext = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped, 0.01, Extrema_ExtFlag_MIN)
    if not ext.IsDone():
        return None
    d = ext.Value()
    if d > TOL:
        return None
    if d > 1e-3:
        p, q = ext.PointOnShape1(1), ext.PointOnShape2(1)
        v = np.array([q.X() - p.X(), q.Y() - p.Y(), q.Z() - p.Z()])
        dirs = [v / np.linalg.norm(v)]
    else:
        c = _common(a, b)
        if c:
            return _overlap(c, (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
        # touching faces: push along the axis on which the boxes only just meet first, then the others
        top, bot = np.minimum(hi[0], hi[1]), np.maximum(lo[0], lo[1])
        dirs = [s * np.eye(3)[ax] for ax in np.argsort(top - bot) for s in (1.0, -1.0)]
    for e in dirs:
        c = _common(a, b.moved(Location(tuple(-float(x) * (TOL + d) for x in e))))
        if c:
            w0, _ = _across(c, e)
            if w0 >= W_MIN - EPS and _volume(c) / TOL >= A_MIN:
                return ("face", tuple(float(x) for x in e), w0, _volume(c) / TOL)
    return None


def _flip(c):
    return c if c is None or c[1] is None else (c[0], tuple(-x for x in c[1]), c[2], c[3])


# ------------------------------------------------------------------ the fixings (data/assemblies/fixings.yaml, ute)
@functools.lru_cache(maxsize=None)
def rules() -> tuple:
    import yaml
    from cad.partsdb import DATA
    out = tuple(yaml.safe_load((DATA / "assemblies" / "fixings.yaml").read_text())["ute"])
    for r in out:
        assert r["how"] in FIXINGS, f"fixings.yaml: {r['lines']} {r['how']!r} is not one of {FIXINGS}"
        assert r.get("why"), f"fixings.yaml: {r['lines']} gives no why"
    return out


def part_id(path) -> str:
    """A part's id: the first word of its label (B5.K-post-1, CAB, WH-RK, 13.TU-F+, TU)."""
    return _product(path).rsplit("/", 1)[-1].split(" ")[0]


def _is(key: str, pats) -> bool:
    return any(fnmatch.fnmatchcase(key, p) or fnmatch.fnmatchcase(key.split(".")[0], p) for p in pats)


@functools.lru_cache(maxsize=None)
def fixed_how(a: str, b: str) -> frozenset:
    """How fixings.yaml fixes part a to part b, either way round: the set of its `how`s, empty if no rule does."""
    return frozenset(r["how"] for r in rules() if (_is(a, r["lines"]) and _is(b, r["to"])) or (_is(b, r["lines"]) and _is(a, r["to"])))


# ------------------------------------------------------------------ the graph
class Graph:
    def __init__(self, comp):
        self.nodes = _nodes(comp)
        n = len(self.nodes)
        bbs = [s.bounding_box() for _, s in self.nodes]
        self.lo = np.array([[b.min.X, b.min.Y, b.min.Z] for b in bbs])
        self.hi = np.array([[b.max.X, b.max.Y, b.max.Z] for b in bbs])
        self.part = [_product(p) for p, _ in self.nodes]
        self.pid = [part_id(p) for p, _ in self.nodes]
        faces = [len(s.faces()) for _, s in self.nodes]
        self._known: dict[tuple[int, int], tuple | None] = {}
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

    def contact(self, i, j):
        """How solid j meets solid i, as `contact` gives it, seen from i."""
        key = (min(i, j), max(i, j))
        if key not in self._known:
            # the two models share most of their solids, the same parts in the same places: one measurement serves both
            same = tuple((self.nodes[k][0], tuple(np.round(self.lo[k], 2)), tuple(np.round(self.hi[k], 2))) for k in key)
            if same not in _SHARED:
                a, b = key
                _SHARED[same] = contact(self.nodes[a][1], self.nodes[b][1], (self.lo[a], self.lo[b]), (self.hi[a], self.hi[b]))
            self._known[key] = _SHARED[same]
        c = self._known[key]
        return c if i == key[0] else _flip(c)

    def joined(self, i, j) -> bool:
        """Any contact within one part, a contact over an area between two, and an overlap between two parts only where
        one is welded, bonded or let into the other."""
        c = self.contact(i, j)
        if c is None:
            return False
        if self.part[i] == self.part[j] or c[0] != "embed":
            return True
        return bool(fixed_how(self.pid[i], self.pid[j]) & set(EMBEDS))

    def holds(self, i, j) -> bool:
        """Part j holds part i through these two solids: i stands on j, or a fixing fixings.yaml lists joins them."""
        if self.part[i] == self.part[j]:
            return False
        c = self.contact(i, j)
        if c is None:
            return False
        if c[0] == "face" and c[1][2] < -0.7:
            return True
        hows = fixed_how(self.pid[i], self.pid[j])
        if hows & set(EMBEDS):
            return True
        return bool(hows) and c[0] != "embed" and c[2] >= FIX_W - EPS and c[3] >= FIX_W ** 2

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

    def unheld(self) -> list[str]:
        """The parts that stand on nothing and are held by no fixing fixings.yaml lists, with what each touches."""
        by: dict[str, list[int]] = {}
        for i, p in enumerate(self.part):
            by.setdefault(p, []).append(i)
        rank = {pair: k for k, pair in enumerate(self.pairs)}
        out = []
        for part, ids in sorted(by.items()):
            if any(_is_root(self.nodes[i][0]) for i in ids):
                continue
            pairs = sorted(((i, j) for i in ids for j in self.near(i, range(len(self.nodes))) if self.part[j] != part),
                           key=lambda ij: rank.get((min(ij), max(ij)), 0))
            if any(self.holds(i, j) for i, j in pairs):
                continue
            seen = sorted({f"{self.pid[j]} {_says(self.contact(i, j))}" for i, j in pairs if self.contact(i, j)})
            out.append(f"{part.rsplit('/', 1)[-1][:60]} ({', '.join(seen) or 'touches nothing'})")
        return out


def _says(c) -> str:
    if c[0] != "face":
        return c[0]
    k = int(np.argmax(np.abs(c[1])))
    return f"{'XYZ'[k]}{'+' if c[1][k] > 0 else '-'} {c[2]:.0f}/{c[3]:.0f}"


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


@pytest.mark.parametrize("name", ["ute", "ute-loading"])
def test_every_part_stands_or_is_fixed(name):
    bad = graph(name).unheld()
    assert not bad, f"{name}: {len(bad)} parts stand on nothing and no fixing holds them:\n  " + "\n  ".join(bad)


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


def test_fixings_name_parts_that_exist():
    """Every ute rule in fixings.yaml covers a part in the ute's models and fixes it to one, so none is left over."""
    keys = {k for name in ("ute", "ute-loading") for k in graph(name).pid}
    dead = [f"{r['lines']} to {r['to']}" for r in rules() if not any(_is(k, r["lines"]) for k in keys) or not any(_is(k, r["to"]) for k in keys)]
    assert not dead, "fixings.yaml ute rules that match no part: " + "; ".join(dead)


if __name__ == "__main__":
    import sys
    import time
    for name in sys.argv[1:] or ("ute", "ute-loading"):
        t = time.time()
        g = graph(name)
        print(f"== {name}: {len(g.nodes)} solids, {time.time() - t:.1f} s")
        print(_report(floating(g)))
        for u in g.unheld():
            print("  not held:", u)
        print(f"   {time.time() - t:.1f} s")

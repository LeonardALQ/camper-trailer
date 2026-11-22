"""H27: nothing in the trailer's 3D models floats (Leonard, 22 Nov 2026: "Many of the models are floating").

Each model the trailer and body pages show, and the chassis page's frame, is broken into its solids. Two solids touch
where they come within 1 mm of each other, a gap or an overlap of 1 mm or less, over a real area: a contact patch at
least W_MIN wide both ways and A_MIN in area, not a point or an edge. Where solids of two lines overlap by more than
1 mm, they are joined only if data/assemblies/fixings.yaml says one is welded, bonded or let into the other. Anywhere
else a deep overlap is two parts in one space, and it holds nothing.

1. Every solid connects through these joints to the ground, through the tyres, the jockey wheel or the corner steadies.
   In travel the jockey and the steadies are wound up, so the tyres hold the trailer. The Body page's three models
   show the body off its chassis, so their root is the floor panel BD-01, which stands on the bearer strips on the
   raisers and outriggers in the trailer model, where the same test reaches it from the tyres. The chassis page's
   model is the frame and its fittings, rooted on the two main rails.
2. Every line in each model stands on another line, its underside on the other's top over an area, or is held by a
   fixing that fixings.yaml lists with the lines it is fixed to: a screwed, bolted, riveted, clamped or hooked fixing
   needs a contact with one of them at least FIX_W wide both ways, and a welded, bonded or let-in one needs that
   contact or an overlap with one of them. A line's own pieces do not hold it up.
"""
from __future__ import annotations

import fnmatch
import functools

import pytest
from build123d import Compound, GeomType, extrude

TOL = 1.0       # mm: a joint's gap or shallow overlap
W_MIN = 2.0     # mm: the narrowest contact patch that counts as an area, under the 2.5 mm sheet welded edge-on in the
                # ute's box
A_MIN = 25.0    # mm2
FIX_W = 12.0    # mm: the land a fixing needs both ways, an M6 flat washer's outside diameter (ISO 7089)
EPS = 0.01      # mm: rounding in the measured widths
EMBEDS = ("welded", "bonded", "let in", "looped")   # a looped strap or a hook runs through what holds it
FIXINGS = ("screwed", "bolted", "riveted", "clamped", "hooked", "seated") + EMBEDS
ROOTS = ("RG-02", "DB-05", "CH-B01")           # tyres, jockey wheel, corner steadies: they stand on the ground
MODELS = ("trailer", "body", "body-inside", "body-inside-night", "chassis")


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
def _trailer_model():
    from cad.trailer_model import TrailerModel
    return TrailerModel(_layouts()[0], body=True)


@functools.lru_cache(maxsize=None)
def model_tree(name: str) -> Compound:
    """The model as the build writes it: the trailer, the Body page's three and the chassis page's frame."""
    from cad.trailer_model import body_models, chassis_compound
    day, night = _layouts()
    if name == "trailer":
        return _trailer_model().compound()
    if name == "chassis":
        return chassis_compound(_trailer_model())
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
    """The common volume of two shapes, its surface area and its bounding box sizes, or (0, 0, None)."""
    c = a.intersect(b)
    if c is None:
        return 0.0, 0.0, None
    parts = list(c) if not hasattr(c, "volume") else [c]
    vol = sum(p.volume for p in parts if hasattr(p, "volume"))
    if vol <= 1e-2:
        return 0.0, 0.0, None
    area = sum(p.area for p in parts if hasattr(p, "area"))
    bb = Compound(children=[p for p in parts]).bounding_box() if len(parts) > 1 else parts[0].bounding_box()
    return vol, area, [bb.size.X, bb.size.Y, bb.size.Z]


def _near(a, b, tol=TOL) -> bool:
    return all(min(a[i + 3], b[i + 3]) - max(a[i], b[i]) >= -tol for i in range(3))


# ------------------------------------------------------------------ contacts
# A contact is (kind, axis, side, width, area). "face": a flat contact across `axis`, the other solid on its `side`
# (+1 positive), `width` the patch's narrower side and `area` its true area. "seat": a thin curved overlap, a tyre's bead
# on its rim or a post in its clamp, with no one axis. "embed": an overlap deeper than TOL.
EMBED = ("embed", None, 0, 0.0, 0.0)


def _face(o, i, side, area=None):
    """A flat contact across axis i with the in-plane overlaps o, or None for an edge or a point."""
    j, k = [m for m in range(3) if m != i]
    area = o[j] * o[k] if area is None else area
    if min(o[j], o[k]) >= W_MIN - EPS and area >= A_MIN:
        return ("face", i, side, min(o[j], o[k]), area)
    return None


def _side(a, b, i) -> int:
    """+1 if b lies on the positive side of a along axis i."""
    return 1 if (a[i] + a[i + 3]) < (b[i] + b[i + 3]) else -1


def contacts(a: Node, b: Node) -> list:
    """How solid b meets solid a: a list of contacts, [EMBED] for an overlap deeper than TOL, or []."""
    A, B = a.bb, b.bb
    o = [min(A[i + 3], B[i + 3]) - max(A[i], B[i]) for i in range(3)]
    if min(o) < -TOL:
        return []
    if a.is_box and b.is_box:
        close = [i for i in range(3) if o[i] <= TOL]
        if not close:
            return [EMBED]
        f = _face(o, close[0], _side(A, B, close[0])) if len(close) == 1 else None
        return [f] if f else []
    if a.shape.distance_to(b.shape) > TOL:
        return []
    # the faces that meet, and any overlap: a shallow one is a contact, a thin curved shell a seat, else an overlap
    out = _touch(a, b)
    vol, area, ext = _common(a.shape, b.shape)
    if not vol:
        return out
    i = min(range(3), key=lambda m: ext[m])
    if ext[i] <= TOL:
        f = _face(ext, i, _side(A, B, i), vol / ext[i])
        return out + [f] if f else out
    if 2 * vol / area <= TOL:
        return out + [("seat", None, 0, (area / 2) ** 0.5, area / 2)]
    return out + [EMBED]


def _touch(a: Node, b: Node) -> list:
    """Planar faces of a and b that face each other within TOL: each patch is a thin slab off a's face cut by b. The
    largest patch on each side of a is kept."""
    best: dict = {}
    for fa, na, ca, ba in a.planar_faces():
        if not _near(ba, b.bb):
            continue
        n = (na.X, na.Y, na.Z)
        i = max(range(3), key=lambda m: abs(n[m]))
        side = 1 if n[i] > 0 else -1
        for fb, nb, cb, bbb in b.planar_faces():
            if na.dot(nb) > -0.999 or not _near(ba, bbb):
                continue
            sep = (cb - ca).dot(na)
            if not -TOL <= sep <= TOL:
                continue
            vol, _, ext = _common(extrude(fa, amount=TOL + 0.5, dir=na), b.shape)
            f = _face(ext, i, side, vol / ext[i]) if vol else None
            if f is not None and ((i, side) not in best or f[4] > best[(i, side)][4]):
                best[(i, side)] = f
    return list(best.values())


def _flip(cs) -> list:
    return [c if c[1] is None else (c[0], c[1], -c[2], c[3], c[4]) for c in cs]


# ------------------------------------------------------------------ the fixings (data/assemblies/fixings.yaml)
@functools.lru_cache(maxsize=None)
def rules(model: str = "trailer") -> tuple:
    import yaml
    from cad.partsdb import DATA
    out = tuple(yaml.safe_load((DATA / "assemblies" / "fixings.yaml").read_text())[model])
    for r in out:
        assert r["how"] in FIXINGS, f"fixings.yaml: {r['lines']} {r['how']!r} is not one of {FIXINGS}"
        assert r.get("why"), f"fixings.yaml: {r['lines']} gives no why"
    return out


def _is(key: str, line: str, pats) -> bool:
    return any(fnmatch.fnmatchcase(key, p) or fnmatch.fnmatchcase(line, p) for p in pats)


@functools.lru_cache(maxsize=None)
def fixed_how(ka: str, la: str, kb: str, lb: str) -> frozenset:
    """How fixings.yaml fixes line a to line b, either way round: the set of its `how`s, empty if no rule does."""
    hows = set()
    for r in rules():
        if (_is(ka, la, r["lines"]) and _is(kb, lb, r["to"])) or (_is(kb, lb, r["lines"]) and _is(ka, la, r["to"])):
            hows.add(r["how"])
    return frozenset(hows)


def _how(a: Node, b: Node) -> frozenset:
    return fixed_how(a.key, a.line, b.key, b.line)


def joins(a: Node, b: Node, cs) -> bool:
    """Whether the contacts cs join a and b: any contact within one line, a contact over an area between two lines,
    and an overlap between two lines only where one is welded, bonded or let into the other."""
    if not cs:
        return False
    if a.key == b.key or any(c[0] != "embed" for c in cs):
        return True
    return bool(_how(a, b) & set(EMBEDS))


def stands_on(a: Node, b: Node, cs) -> bool:
    """a's underside on b's top over an area."""
    return a.key != b.key and any(c[0] == "face" and c[1] == 2 and c[2] < 0 for c in cs)


def fixed_to(a: Node, b: Node, cs) -> bool:
    """a held by a fixing to b that fixings.yaml lists and the model shows: a weld, a bond or a let-in part by any
    contact or an overlap, a mechanical fixing by a contact with room for its washer, FIX_W both ways."""
    if a.key == b.key or not cs:
        return False
    hows = _how(a, b)
    if hows & set(EMBEDS):
        return True
    return bool(hows) and any(c[0] != "embed" and c[3] >= FIX_W - EPS and c[4] >= FIX_W ** 2 for c in cs)


# ------------------------------------------------------------------ the graph
@functools.lru_cache(maxsize=None)
def _pairs(name: str):
    """The solids of a model and, for each, the solids it meets with their contacts as seen from it."""
    nodes = [Node(p, s) for p, s in _leaves(model_tree(name))]
    order = sorted(range(len(nodes)), key=lambda n: nodes[n].bb[0])
    meets: dict[int, list] = {n: [] for n in range(len(nodes))}
    for ii, n in enumerate(order):
        a = nodes[n]
        for m in order[ii + 1:]:
            b = nodes[m]
            if b.bb[0] > a.bb[3] + TOL:
                break
            if not _near(a.bb, b.bb):
                continue
            cs = contacts(a, b)
            if cs:
                meets[n].append((m, cs))
                meets[m].append((n, _flip(cs)))
    return nodes, meets


def graph(name: str):
    """The solids and, for each, the solids joined to it."""
    nodes, meets = _pairs(name)
    return nodes, {n: [m for m, cs in ms if joins(nodes[n], nodes[m], cs)] for n, ms in meets.items()}


def roots(name: str, nodes) -> list[int]:
    if name == "trailer":
        return [n for n, x in enumerate(nodes) if x.line in ROOTS and x.bb[2] <= TOL]
    if name == "chassis":
        return [n for n, x in enumerate(nodes) if x.line.startswith("RL-")]
    return [n for n, x in enumerate(nodes) if x.line == "BD-01"]


def floating(name: str) -> list[str]:
    """The solids that no chain of joints connects to a root, by name."""
    nodes, edges = graph(name)
    seen = set(roots(name, nodes))
    todo = list(seen)
    while todo:
        n = todo.pop()
        for m in edges[n]:
            if m not in seen:
                seen.add(m)
                todo.append(m)
    return sorted(nodes[n].name for n in range(len(nodes)) if n not in seen)


def unsupported(name: str) -> list[str]:
    """The lines that stand on nothing and are held by no fixing that fixings.yaml lists, with what each touches."""
    nodes, meets = _pairs(name)
    base = {nodes[n].key for n in roots(name, nodes)}
    lines: dict[str, list[int]] = {}
    for n, x in enumerate(nodes):
        lines.setdefault(x.key, []).append(n)
    out = []
    for key, ns in sorted(lines.items()):
        if key in base:
            continue
        if any(stands_on(nodes[n], nodes[m], cs) or fixed_to(nodes[n], nodes[m], cs) for n in ns for m, cs in meets[n]):
            continue
        touch = sorted({f"{nodes[m].key} {_says(cs)}" for n in ns for m, cs in meets[n] if nodes[m].key != key})
        out.append(f"{key} ({', '.join(touch) or 'touches nothing'})")
    return out


def _says(cs) -> str:
    return "/".join("overlap" if c[0] == "embed" else f"{'XYZ'[c[1]]}{'+' if c[2] > 0 else '-'} {c[3]:.0f}x{c[4]:.0f}" for c in cs)


@pytest.mark.parametrize("name", MODELS)
def test_nothing_floats(name):
    nodes, _ = graph(name)
    assert roots(name, nodes), f"{name}: no root solid"
    bad = floating(name)
    assert not bad, f"{name}: {len(bad)} solids float: " + "; ".join(bad[:40])


@pytest.mark.parametrize("name", MODELS)
def test_every_line_stands_or_is_fixed(name):
    bad = unsupported(name)
    assert not bad, f"{name}: {len(bad)} lines stand on nothing and no fixing holds them: " + "; ".join(bad)


def test_fixings_name_lines_that_exist():
    """Every rule in fixings.yaml covers a line in the trailer's models and fixes it to one, so none is left over."""
    keys = {(x.key, x.line) for name in ("trailer", "body-inside-night") for x in _pairs(name)[0]}
    dead = [f"{r['lines']} to {r['to']}" for r in rules()
            if not any(_is(k, ln, r["lines"]) for k, ln in keys) or not any(_is(k, ln, r["to"]) for k, ln in keys)]
    assert not dead, "fixings.yaml rules that match no line: " + "; ".join(dead)


if __name__ == "__main__":
    import sys
    import time
    for name in sys.argv[1:] or MODELS:
        t = time.time()
        nodes, edges = graph(name)
        print(f"== {name}: {len(nodes)} solids, {sum(len(e) for e in edges.values()) // 2} joints, {time.time() - t:.1f} s")
        for f in floating(name):
            print("  floats:", f)
        for u in unsupported(name):
            print("  not held:", u)

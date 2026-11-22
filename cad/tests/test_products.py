"""H27: the trailer's product models (cad/model/products) are the makers' products inside their lines' envelopes.

Every `model:` key in data/assemblies/trailer.yaml names a product that exists, and every chassis fitting in
FITTING_MODELS exists in data/chassis/chassis.yaml. Each product's pieces stay inside the envelope they were built
for, within 1 mm. A line with a box of its own keeps its main product in that box, so the fit checks still see the
space it takes. The models are visual: the mass schedule is the same with the `model:` keys taken out.
"""
from __future__ import annotations

import copy
import functools

import pytest
import yaml

from cad.model import products as PR
from cad.partsdb import DATA, Project
from cad.trailer import TRAILER_YAML, Layout, Trailer

TOL = 1.0
TD = yaml.safe_load(TRAILER_YAML.read_text())
SPECS = {it["id"]: it["model"] for it in TD["items"] if "model" in it}


@functools.lru_cache(maxsize=None)
def layouts():
    tr = Trailer(Project(), ute=False)
    return tr, tr.layout(), tr.layout(bed_state=1)


def _bb(shape):
    b = shape.bounding_box()
    return (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)


def test_every_model_names_a_product():
    from cad.model.products import catalogue  # noqa: F401
    for line, spec in SPECS.items():
        for p in [PR.spec_of(spec)] + [PR.spec_of(e) for e in PR.spec_of(spec).get("extras", [])]:
            assert p["name"] in PR.REGISTRY, f"{line}: no product {p['name']!r}"
    for fid, spec in PR.FITTING_MODELS.items():
        assert spec["name"] in PR.REGISTRY, f"{fid}: no product {spec['name']!r}"


def test_every_fitting_model_is_a_chassis_fitting():
    ch = yaml.safe_load((DATA / "chassis" / "chassis.yaml").read_text())
    ids = {f["id"] for f in ch["fittings"]}
    assert set(PR.FITTING_MODELS) <= ids, sorted(set(PR.FITTING_MODELS) - ids)


def test_a_line_with_a_box_keeps_its_product_in_it():
    for it in TD["items"]:
        if "model" in it and "box" in it:
            assert "box" not in PR.spec_of(it["model"]), f"{it['id']} has a box, so its product must sit in it"


@pytest.mark.parametrize("state", [0, 1], ids=["bed up", "bed down"])
def test_each_product_stays_in_its_envelope(state):
    _, day, night = layouts()
    lay = night if state else day
    checked = 0
    for b in lay.blocks:
        if b.id not in SPECS:
            continue
        for p, env in PR.placements(SPECS[b.id], b, lay):
            for piece in PR.pieces(p, env, lay.V, b):
                got = _bb(piece)
                out = max(max(env[i] - got[i], got[i + 3] - env[i + 3]) for i in range(3))
                assert out <= TOL, f"{b.iid} {p['name']} {piece.label!r} stands {out:.1f} mm outside its envelope"
                checked += 1
    assert checked > 300


def test_fitting_products_stay_on_their_fittings():
    from cad.chassis import fitting_solids
    _, lay, _ = layouts()
    for b in lay.blocks:
        if "fitting" not in b.extra or b.id not in PR.FITTING_MODELS:
            continue
        for k in fitting_solids(lay.chassis, b.extra["fitting"]):
            env = _bb(k)
            comp = PR.build(PR.FITTING_MODELS[b.id], b, lay, b.iid, ("#000000", 1.0), bx=env)
            for piece in comp.children:
                got = _bb(piece)
                out = max(max(env[i] - got[i], got[i + 3] - env[i + 3]) for i in range(3))
                assert out <= TOL, f"{b.iid} {piece.label!r} stands {out:.1f} mm outside the fitting"


def test_every_product_is_labelled_with_its_line():
    from cad.trailer_model import part_shape
    _, lay, _ = layouts()
    for b in lay.blocks:
        if b.id in SPECS:
            s = part_shape(b, lay)
            if s is not None:
                assert s.label.split(" ")[0] == b.iid, f"{b.iid}: labelled {s.label!r}"
                assert s.children, f"{b.iid}: the product has no pieces"


def test_the_models_move_no_mass():
    """The schedule's masses and centres of gravity are the same with every `model:` key taken out."""
    tr, lay, _ = layouts()
    bare = copy.deepcopy(TD)
    for it in bare["items"]:
        it.pop("model", None)
    plain = Layout(bare, tr.prj, tr.base)
    plain.apply_weighed(tr.weighed)
    a = {b.iid: (round(b.mass_kg, 6), tuple(round(c, 6) for c in b.cog or ())) for b in lay.blocks}
    c = {b.iid: (round(b.mass_kg, 6), tuple(round(v, 6) for v in b.cog or ())) for b in plain.blocks}
    assert a == c

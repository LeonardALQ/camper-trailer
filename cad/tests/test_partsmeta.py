"""The part data beside each 3D model (cad/partsmeta.py): every solid in a viewer file belongs to a part, so the site
can say what it is, and the stable parts say what they are made of."""
import json

import pytest

from cad.partsdb import ROOT

MODELS = [("trailer", "trailer"), ("trailer", "chassis"), ("trailer", "body"), ("trailer", "body-inside"),
          ("ute", "ute"), ("ute", "ute-loading")]


def _load(folder, name):
    viewer = ROOT / "build" / folder / f"{name}.viewer.json"
    parts = ROOT / "build" / folder / f"{name}.parts.json"
    if not viewer.exists() or not parts.exists():
        pytest.skip(f"build/{folder}/{name} is not built (make trailer ute)")
    return json.loads(viewer.read_text()), json.loads(parts.read_text())


def _leaves(o, out):
    for p in o.get("parts") or []:
        if p.get("parts"):
            _leaves(p, out)
        else:
            out.append(p["id"])
    return out


@pytest.mark.parametrize("folder,name", MODELS)
def test_every_solid_belongs_to_a_part(folder, name):
    viewer, meta = _load(folder, name)
    nodes = meta["nodes"]

    def owner(path):
        while path.count("/") > 1 and path not in nodes:
            path = path.rsplit("/", 1)[0]
        return nodes.get(path)
    missing = [leaf for leaf in _leaves(viewer, []) if owner(leaf) is None]
    assert not missing, f"{len(missing)} solids with no part, for example {missing[:3]}"


def test_trailer_stable_parts_have_a_material():
    _, meta = _load("trailer", "trailer")
    stable = [p for p in meta["parts"].values()
              if p["system"] == "chassis" or p["id"] in ("BD-01", "BD-02", "BD-03", "BD-04", "DB-03")
              or p["system"] == "running_gear"]
    assert len(stable) > 60
    missing = [p["iid"] for p in stable if not p["material"]]
    assert not missing, f"no material for {missing}"


def test_bike_box_shell_has_a_material():
    _, meta = _load("ute", "ute")
    box = [p for p in meta["parts"].values() if p["system"] in ("body", "subframe", "doors")]
    assert box
    missing = sorted({p["id"] for p in box if not p["material"] and p["mass_kg"] is not None})
    assert not missing, f"no material for {missing}"

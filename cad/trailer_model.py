"""3D block model of the whole trailer from the layout (cad/trailer.py), with the garage and bed module placed
as a sub-assembly. Exports the three-cad-viewer JSON (part tree by zone), STEP and GLB."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from build123d import Box, Compound, Cylinder, Plane, Pos, Rot, export_gltf, export_step

from .model.assembly import GROUP_LABELS
from .model.prims import box, rgba
from .trailer import SYSTEM_LABELS, Layout

SYSTEM_ORDER = ["drawbar", "chassis", "running_gear", "underfloor", "body", "roof", "front", "module", "rear"]
COLOURS = {
    "drawbar": ("#5d6d7e", 1.0), "chassis": ("#566573", 1.0), "running_gear": ("#1c2833", 1.0),
    "underfloor": ("#2e86c1", 0.9), "body": ("#d6dbdf", 0.18), "roof": ("#f4d03f", 0.9),
    "front": ("#a9cce3", 0.9), "rear": ("#d2b4de", 0.9),
}
OVERRIDE = {"BD-01": ("#8c8c8c", 0.6), "DB-05": ("#7f8c8d", 0.35), "RG-01": ("#7b7d7d", 1.0), "FZ-03": ("#58d68d", 0.9),
            "RZ-02": ("#76d7c4", 0.9), "UF-04": ("#f5b041", 1.0), "BD-13": ("#27ae60", 0.8), "DB-06": ("#c0392b", 1.0),
            "DB-07": ("#ecf0f1", 1.0), "DB-09": ("#e74c3c", 1.0), "BD-05": ("#b2bec3", 0.35), "BD-06": ("#b2bec3", 0.5),
            "BD-07": ("#b2bec3", 0.5)}


def _bar(b):
    (x0, y0, z0), (x1, y1, z1) = b.bar["p0"], b.bar["p1"]
    L = math.dist((x0, y0, z0), (x1, y1, z1))
    d = ((x1 - x0) / L, (y1 - y0) / L, (z1 - z0) / L)
    pl = Plane(origin=(x0, y0, z0), x_dir=d, z_dir=(0, 0, 1))
    return pl * Pos(L / 2, 0, 0) * Box(L, b.bar["w"], b.bar["h"])


def _hollow(bx, t=4.0):
    x0, y0, z0, x1, y1, z1 = bx
    outer = box(x0, y0, z0, x1 - x0, y1 - y0, z1 - z0)
    inner = box(x0 + t, y0 + t, z0 + t, x1 - x0 - 2 * t, y1 - y0 - 2 * t, z1 - z0)
    return outer - inner


def block_shape(b):
    if b.bar:
        return _bar(b)
    if b.cyl:
        cx, cy, cz = b.cyl["c"]
        tyre = Pos(cx, cy, cz) * Rot(90, 0, 0) * Cylinder(b.cyl["r"], b.cyl["w"])
        return tyre
    if b.box is None:
        return None
    x0, y0, z0, x1, y1, z1 = b.box
    if b.hollow:
        return _hollow(b.box)
    return box(x0, y0, z0, x1 - x0, y1 - y0, z1 - z0)


class TrailerModel:
    """Shapes for every solid block plus the module's bodies moved into the datum."""

    def __init__(self, lay: Layout, module_model):
        self.lay = lay
        self.groups: dict[str, list] = {}
        self.module_groups: dict[str, list] = {}
        self.names: dict[str, str] = {}
        for b in lay.blocks:
            if b.system == "module" or b.keep_clear or b.box is None and b.cyl is None and b.bar is None:
                continue
            s = block_shape(b)
            if s is None:
                continue
            col, a = OVERRIDE.get(b.id, COLOURS[b.system])
            s.label = f"{b.iid} {b.name}".replace("/", "-")
            s.color = rgba(col, a)
            self.groups.setdefault(b.system, []).append(s)
        dx, dz = lay.V["module_x0"], lay.V["floor_z"]
        prj = module_model.prj
        for mb in module_model.built.values():
            i = mb.inst
            if i.check_only or i.display == "loading_only" or i.group == "context":
                continue
            s = Pos(dx, 0, dz) * copy.copy(mb.shape)
            s.label = f"{i.iid} {i.label}".replace("/", "-")
            part = prj.parts[i.part]
            s.color = rgba(part.color, part.alpha)
            self.module_groups.setdefault(i.group, []).append(s)

    def compound(self, label="ASM-TR"):
        kids = []
        for g in SYSTEM_ORDER:
            if g == "module":
                sub = [Compound(label=GROUP_LABELS[k], children=v) for k, v in self.module_groups.items()]
                kids.append(Compound(label=SYSTEM_LABELS["module"], children=sub))
            elif g in self.groups:
                kids.append(Compound(label=SYSTEM_LABELS[g], children=self.groups[g]))
        return Compound(label=label, children=kids)

    def all_shapes(self):
        out = [s for v in self.groups.values() for s in v]
        out += [s for v in self.module_groups.values() for s in v]
        return out


def write_outputs(tm: TrailerModel, out: Path):
    from .export import _viewer_js
    out.mkdir(parents=True, exist_ok=True)
    comp = tm.compound()
    js = _viewer_js("ASM-TR", comp)
    shapes = json.loads(js[js.index("{"): js.rindex("}") + 1])
    (out / "trailer.viewer.json").write_text(json.dumps(shapes, separators=(",", ":")))
    export_step(comp, str(out / "trailer.step"), timestamp="2026-11-18T00:00:00")
    export_gltf(comp, str(out / "trailer.glb"), binary=True, linear_deflection=0.8, angular_deflection=0.5)

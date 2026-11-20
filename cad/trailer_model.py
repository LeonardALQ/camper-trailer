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

SYSTEM_ORDER = ["drawbar", "chassis", "running_gear", "spare", "underfloor", "body", "roof", "living", "module", "stowage", "payload"]
COLOURS = {
    "drawbar": ("#5d6d7e", 1.0), "chassis": ("#7f8c8d", 1.0), "running_gear": ("#1c2833", 1.0),
    "underfloor": ("#2e86c1", 0.9), "body": ("#d6dbdf", 0.18), "roof": ("#f4d03f", 0.9),
    "living": ("#d2b4de", 0.9), "stowage": ("#e59866", 1.0), "payload": ("#f7dc6f", 1.0), "spare": ("#1c2833", 1.0),
}
OVERRIDE = {"BD-01": ("#8c8c8c", 0.6), "RG-01": ("#7b7d7d", 1.0), "LA-07": ("#58d68d", 0.9),
            "LA-01": ("#76d7c4", 0.9), "UF-04": ("#f5b041", 1.0), "BD-13": ("#27ae60", 0.8), "GS-01": ("#c0392b", 1.0),
            "GS-02": ("#ecf0f1", 1.0), "GS-04": ("#e74c3c", 1.0), "BD-05": ("#b2bec3", 0.35), "BD-06": ("#b2bec3", 0.5),
            "BD-07": ("#b2bec3", 0.5), "DB-03": ("#2c3e50", 1.0), "DB-04": ("#aab7b8", 0.8)}
ROLE_COLOURS = {"rail": "#566573", "raiser": "#7b8a8b", "drawbar": "#34495e", "brace": "#34495e", "outrigger": "#95a5a6",
                "cm_xt": "#5d6d7e", "cm_end": "#5d6d7e", "cm_floor": "#839192", "plan_brace": "#a04000", "spare_post": "#5d6d7e"}


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


def _moved(shape, loc):
    """Move a shape, compounds leaf by leaf, so that the children carry the move too."""
    if isinstance(shape, Compound) and shape.children:
        kids = [_moved(k, loc) for k in shape.children]
        out = Compound(label=shape.label, children=kids)
        out.color = shape.color
        return out
    s = loc * copy.copy(shape)
    s.label, s.color = shape.label, shape.color
    return s


class TrailerModel:
    """Shapes for every solid block plus the module's bodies moved into the datum."""

    def __init__(self, lay: Layout, module_model, body: bool = False, raised: bool = False):
        """`body` replaces the body's envelope blocks by the designed body (cad/body_model.py), with the roof raised if
        `raised`."""
        self.lay = lay
        from .body_model import BODY_IDS, body_solids
        lift = lay.V["roof_lift"] if raised else 0.0
        self.groups: dict[str, list] = {}
        self.module_groups: dict[str, list] = {}
        self.names: dict[str, str] = {}
        from .chassis import fitting_solids, member_solid
        for b in lay.blocks:
            if "member" in b.extra or "fitting" in b.extra:
                if "member" in b.extra:
                    s = member_solid(b.extra["member"])
                    col = ROLE_COLOURS.get(b.extra["role"], COLOURS["chassis"][0])
                    a = 1.0
                else:
                    kids = fitting_solids(lay.chassis, b.extra["fitting"])
                    if not kids:
                        continue
                    s = kids[0] if len(kids) == 1 else Compound(children=kids)
                    col, a = OVERRIDE.get(b.id, ("#d35400", 1.0) if b.system == "chassis" else COLOURS["drawbar"])
                s.label = f"{b.iid} {b.name}".replace("/", "-")
                s.color = rgba(col, a)
                self.groups.setdefault(b.system, []).append(s)
                continue
            if b.system == "module" or b.keep_clear or b.box is None and b.cyl is None and b.bar is None:
                continue
            if body and b.id in BODY_IDS:
                continue
            s = block_shape(b)
            if s is None:
                continue
            if b.system == "roof" and lift:
                s = Pos(0, 0, lift) * s
            col, a = OVERRIDE.get(b.id, COLOURS[b.system])
            s.label = f"{b.iid} {b.name}".replace("/", "-")
            s.color = rgba(col, a)
            self.groups.setdefault(b.system, []).append(s)
        if body:
            for label, shp, (col, a) in body_solids(lay, raised):
                shp.label = label.replace("/", "-")
                shp.color = rgba(col, a)
                self.groups.setdefault("body", []).append(shp)
        dx, dz = lay.V["module_x0"], lay.V["floor_z"]
        prj = module_model.prj
        for mb in module_model.built.values():
            i = mb.inst
            if i.check_only or i.display == "loading_only" or i.group == "context":
                continue
            s = _moved(mb.shape, Pos(dx, 0, dz))
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
    # the chassis and drawbar on their own, for the chassis page and the engineer
    ch = Compound(label="ASM-CH Chassis and drawbar",
                  children=[Compound(label=SYSTEM_LABELS[g], children=tm.groups[g]) for g in ("chassis", "drawbar") if g in tm.groups])
    js = _viewer_js("ASM-CH", ch)
    (out / "chassis.viewer.json").write_text(js[js.index("{"): js.rindex("}") + 1])
    export_step(ch, str(out / "chassis.step"), timestamp="2026-11-20T00:00:00")


def write_body_outputs(lay: Layout, out: Path):
    """The body on its own with the roof down and raised, for the Body page (BODY.md), and its STEP file."""
    from .body_model import body_solids
    from .export import _viewer_js
    lift = lay.V["roof_lift"]
    for raised, name in ((False, "body"), (True, "body-raised")):
        kids = []
        for label, shp, (col, a) in body_solids(lay, raised):
            shp.label, shp.color = label.replace("/", "-"), rgba(col, a)
            kids.append(shp)
        roof = []
        for b in lay.blocks:
            if b.system == "roof" and b.box is not None:
                s = block_shape(b)
                if raised:
                    s = Pos(0, 0, lift) * s
                s.label, s.color = f"{b.iid} {b.name}".replace("/", "-"), rgba(*COLOURS["roof"])
                roof.append(s)
        comp = Compound(label=f"ASM-BD Body, roof {'raised' if raised else 'down'}",
                        children=[Compound(label="Body", children=kids), Compound(label="Solar panels", children=roof)])
        js = _viewer_js("ASM-BD", comp)
        (out / f"{name}.viewer.json").write_text(js[js.index("{"): js.rindex("}") + 1])
        if not raised:
            export_step(comp, str(out / "body.step"), timestamp="2026-11-20T00:00:00")

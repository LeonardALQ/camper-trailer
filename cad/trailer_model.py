"""3D block model of the whole trailer from the layout (cad/trailer.py), with the designed chassis and body. Exports the
three-cad-viewer JSON (part tree by system), STEP and GLB. The bikes ride in the ute's bike box (cad/ute_model.py)."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from build123d import Box, Compound, Cylinder, Plane, Pos, Rot, export_gltf, export_step

from .model.prims import box, rgba
from .trailer import SYSTEM_LABELS, Layout

SYSTEM_ORDER = ["drawbar", "stowage", "chassis", "running_gear", "spare", "underfloor", "body", "roof", "bed", "living", "electrical",
                "hvac", "wet_room", "payload"]
COLOURS = {
    "drawbar": ("#5d6d7e", 1.0), "chassis": ("#7f8c8d", 1.0), "running_gear": ("#1c2833", 1.0),
    "underfloor": ("#2e86c1", 0.9), "body": ("#d6dbdf", 0.18), "roof": ("#f4d03f", 0.9),
    "living": ("#d2b4de", 0.9), "bed": ("#aed6f1", 0.9), "stowage": ("#e59866", 1.0), "payload": ("#f7dc6f", 1.0), "spare": ("#1c2833", 1.0),
    "electrical": ("#f5b041", 1.0), "hvac": ("#85c1e9", 0.9), "wet_room": ("#76d7c4", 0.9),
}
OVERRIDE = {"BD-01": ("#8c8c8c", 0.6), "RG-01": ("#7b7d7d", 1.0), "LA-11T": ("#58d68d", 0.35), "LA-11B": ("#58d68d", 0.35),
            "WR-01": ("#76d7c4", 0.6), "EL-02": ("#f5b041", 0.4), "AC-03": ("#aab7b8", 0.35), "UF-08": ("#7f8c8d", 0.9),
            "BD-15": ("#b2bec3", 0.5), "BD-13": ("#27ae60", 0.8), "GS-01": ("#c0392b", 1.0),
            "GS-04": ("#e74c3c", 1.0), "DX-01": ("#aab7b8", 0.45), "LB-04": ("#d4e6f1", 0.25), "LB-01": ("#f8f9f9", 1.0),
            "BD-07": ("#b2bec3", 0.5), "DB-03": ("#2c3e50", 1.0), "DB-04": ("#aab7b8", 0.8),
            "CH-S01": ("#1c2833", 1.0), "CH-P14": ("#7f8c8d", 1.0)}
LAMP_COLOURS = {"red": "#c0392b", "amber": "#f39c12", "white": "#fdfefe", "red and amber": "#d35400"}
# the viewer files' tessellation: the product models' round parts at 1.5 mm and 0.6 rad keep each file under 8 MB
VIEWER_MESH = {"deviation": 1.5, "angular_tolerance": 0.6}
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


def model_specs(lay) -> dict:
    """The `model:` key of every line in data/assemblies/trailer.yaml that has one, by line id."""
    specs = getattr(lay, "_model_specs", None)
    if specs is None:
        specs = {it["id"]: it["model"] for it in lay.td["items"] if "model" in it}
        lay._model_specs = specs
    return specs


def _label(b) -> str:
    return f"{b.iid} {b.name}".replace("/", "-")


def part_shape(b, lay, colour: tuple | None = None):
    """The one shape every consumer shows for a block (the viewer models, the STEP and GLB files and the drawings): the
    product model where its line names one (cad/model/products, H27), else its envelope. Labelled with the line's
    instance id and name, so a pointer on any piece of a product names the line."""
    spec = model_specs(lay).get(b.id)
    if spec is not None:
        from .model import products as PR
        return PR.build(spec, b, lay, _label(b))
    s = block_shape(b)
    if s is None:
        return None
    s.label, s.color = _label(b), rgba(*(colour or OVERRIDE.get(b.id, COLOURS[b.system])))
    return s


STRIP_ROLES = ("raiser", "outrigger", "cm_floor")   # the members the floor's bearer strips lie on (CH-S01)


def bearer_strips(lay) -> list:
    """The floor's bearer strips (CH-S01): one on the top of every raiser, outrigger and floor crossmember, up to the
    floor's underside, so the body stands on the chassis in the model as it does on the frame."""
    top = lay.V["floor_underside_z"]
    out = []
    for b in lay.blocks:
        if b.extra.get("role") in STRIP_ROLES and "member" in b.extra:
            x0, y0, _, x1, y1, z1 = b.extra["member"].box()
            if top - z1 > 1:
                s = box(x0, y0, z1, x1 - x0, y1 - y0, top - z1)
                s.label = f"strip on {b.iid}"
                out.append(s)
    return out


def nut_plates(lay) -> list:
    """The 32 body mount nut plates (CH-P14) where the body's bolts are: one inside each raiser and each outrigger tip at
    every station (data/body/body.yaml mounts), each spanning the tube's webs, 13 mm under its top. The schedule keeps
    their mass at one point (data/chassis/chassis.yaml)."""
    import yaml
    from .partsdb import DATA
    tip = yaml.safe_load((DATA / "body" / "body.yaml").read_text())["mounts"]["outrigger_tip_y"]
    out = []
    for b in lay.blocks:
        if b.extra.get("role") == "outrigger" and "member" in b.extra:
            x0, y0, _, x1, y1, z1 = b.extra["member"].box()
            s = 1 if y0 + y1 > 0 else -1
            z = z1 - 13 - 5
            tip_plate = box(x0 + 3.5, s * tip - 40, z, x1 - x0 - 7, 80, 10)
            tip_plate.label = f"nut plate in {b.iid}"
            raiser_plate = box((x0 + x1) / 2 - 40, s * lay.V["rail_c"] - 22, z, 80, 44, 10)
            raiser_plate.label = "nut plate in the raiser"
            out += [tip_plate, raiser_plate]
    return out


def fitting_shape(b, lay, col: tuple):
    """A chassis fitting at each of its positions: its product model where FITTING_MODELS names one, else its box."""
    from .chassis import fitting_solids
    from .model import products as PR
    f = b.extra["fitting"]
    if f.kind == "strip":
        kids = bearer_strips(lay)
    elif b.id == "CH-P14":
        kids = nut_plates(lay)
    else:
        kids = fitting_solids(lay.chassis, f)
    if not kids:
        return None
    spec = PR.FITTING_MODELS.get(b.id)
    if spec:
        out = []
        for n, k in enumerate(kids, 1):
            bb = k.bounding_box()
            bx = (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)
            out.append(PR.build(spec, b, lay, f"{n}" if len(kids) > 1 else "", bx=bx))
        s = out[0] if len(out) == 1 else Compound(children=out)
        s.label = _label(b)
        return s
    s = kids[0] if len(kids) == 1 else Compound(children=kids)
    s.label, s.color = _label(b), rgba(*col)
    return s


def lamp_shapes(lay) -> list:
    """The lamps, reflectors and the number plate at their resolved positions (cad/lamps.py, line LG-01), each a housing
    with its lens on the outer face. A side marker on an outrigger's open end stands on a cap riveted over the end (LG-02)."""
    from .lamps import model_parts, resolve
    caps = [b for b in lay.blocks if b.id == "LG-02"]
    tips = [b.extra["member"].box() for b in lay.blocks if b.extra.get("role") == "outrigger" and "member" in b.extra]
    out = []
    for p in model_parts(lay, resolve(lay)):
        x0, y0, z0, x1, y1, z1 = p["box"]
        col = LAMP_COLOURS.get(p["colour"], "#f39c12")
        label = f"{p['key']} {p['name']}".replace("/", "-")
        side = abs(abs(y0 + y1) / 2 - lay.V["half_bw"]) < 40 and (y1 - y0) < 40
        tip = next((t for t in tips if side and t[0] < x1 and t[3] > x0 and t[2] < z1 and t[5] > z0
                    and (abs(t[1] - y1) < 1 or abs(t[4] - y0) < 1)), None)
        if tip is not None and caps:
            inner = y1 if y1 <= 0 else y0                        # the lamp's face against the outrigger's end
            s = -1 if y1 <= 0 else 1
            cap = box(tip[0], min(inner, inner + s * 3), tip[2], tip[3] - tip[0], 3, tip[5] - tip[2])
            cap.label, cap.color = f"LG-02 {caps[0].name}".replace("/", "-"), rgba("#c8cfd2", 1.0)
            out.append(cap)
            y0, y1 = (y0, inner - 3) if s < 0 else (inner + 3, y1)
        if p["key"].endswith("PLATE"):
            s = box(x0, y0, z0, x1 - x0, y1 - y0, z1 - z0)
            s.label, s.color = label, rgba(col, 1.0)
            out.append(s)
            continue
        out.append(_lamp(label, (x0, y0, z0, x1, y1, z1), col, lay.V))
    return out


def _lamp(label, bx, col, V):
    """A lamp: a dark housing on its mounting face and a coloured lens on the outer face, 3 mm thick."""
    x0, y0, z0, x1, y1, z1 = bx
    dx, dy = x1 - x0, y1 - y0
    if dy <= dx and dy < 60:                      # on a side: the outer face is the one away from the centreline
        out_lo = (y0 + y1) / 2 < 0
        hs = box(x0, y0 + (3 if out_lo else 0), z0, dx, dy - 3, z1 - z0)
        lens = box(x0 + 2, y0 if out_lo else y1 - 3, z0 + 2, dx - 4, 3, z1 - z0 - 4)
    else:                                          # on an end: the outer face is the one away from the body
        out_lo = (x0 + x1) / 2 < V["body_x0"] + V["body_length"] / 2
        hs = box(x0 + (3 if out_lo else 0), y0, z0, dx - 3, dy, z1 - z0)
        lens = box(x0 if out_lo else x1 - 3, y0 + 2, z0 + 2, 3, dy - 4, z1 - z0 - 4)
    hs.label, hs.color = "housing", rgba("#2c3e50", 1.0)
    lens.label, lens.color = "lens", rgba(col, 0.9)
    return Compound(label=label, children=[hs, lens])


def _paint(shp, col: tuple):
    """Colour a plain solid. A product's pieces keep their own colours."""
    if not (isinstance(shp, Compound) and shp.children):
        shp.color = rgba(*col)


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
    """Shapes for every solid block, with the designed chassis members and fittings."""

    def __init__(self, lay: Layout, body: bool = False):
        """`body` replaces the body's envelope blocks by the designed body (cad/body_model.py)."""
        self.lay = lay
        from .body_model import BODY_IDS, body_solids
        self.groups: dict[str, list] = {}
        self.names: dict[str, str] = {}
        from .chassis import member_solid
        specs = model_specs(lay)
        for b in lay.blocks:
            if "member" in b.extra:
                s = member_solid(b.extra["member"])
                s.label, s.color = _label(b), rgba(ROLE_COLOURS.get(b.extra["role"], COLOURS["chassis"][0]), 1.0)
                self.groups.setdefault(b.system, []).append(s)
                continue
            if "fitting" in b.extra:
                s = fitting_shape(b, lay, OVERRIDE.get(b.id, ("#d35400", 1.0) if b.system == "chassis" else COLOURS["drawbar"]))
                if s is not None:
                    self.groups.setdefault(b.system, []).append(s)
                continue
            if b.keep_clear or (b.box is None and b.cyl is None and b.bar is None and b.id not in specs):
                continue
            if body and b.id in BODY_IDS:
                continue
            s = part_shape(b, lay)
            if s is None:
                continue
            self.groups.setdefault(b.system, []).append(s)
        if body:
            for label, shp, col in body_solids(lay):
                shp.label = label.replace("/", "-")
                _paint(shp, col)
                self.groups.setdefault("body", []).append(shp)
            self.groups.setdefault("electrical", []).extend(lamp_shapes(lay))

    def compound(self, label="ASM-TR"):
        kids = [Compound(label=SYSTEM_LABELS[g], children=self.groups[g]) for g in SYSTEM_ORDER if g in self.groups]
        return Compound(label=label, children=kids)

    def all_shapes(self):
        return [s for v in self.groups.values() for s in v]


def chassis_compound(tm: TrailerModel) -> Compound:
    """The chassis and drawbar on their own, for the chassis page and the engineer."""
    return Compound(label="ASM-CH Chassis and drawbar",
                    children=[Compound(label=SYSTEM_LABELS[g], children=tm.groups[g]) for g in ("chassis", "drawbar") if g in tm.groups])


def write_outputs(tm: TrailerModel, out: Path):
    from .export import _viewer_js
    out.mkdir(parents=True, exist_ok=True)
    comp = tm.compound()
    js = _viewer_js("ASM-TR", comp, **VIEWER_MESH)
    shapes = json.loads(js[js.index("{"): js.rindex("}") + 1])
    (out / "trailer.viewer.json").write_text(json.dumps(shapes, separators=(",", ":")))
    export_step(comp, str(out / "trailer.step"), timestamp="2026-11-18T00:00:00")
    export_gltf(comp, str(out / "trailer.glb"), binary=True, linear_deflection=0.8, angular_deflection=0.5)
    ch = chassis_compound(tm)
    js = _viewer_js("ASM-CH", ch, **VIEWER_MESH)
    (out / "chassis.viewer.json").write_text(js[js.index("{"): js.rindex("}") + 1])
    export_step(ch, str(out / "chassis.step"), timestamp="2026-11-20T00:00:00")


FIT_SYSTEMS = ("bed", "living", "electrical", "hvac", "wet_room")
# body solids that hang from the chassis, so the Body page's models, which leave the chassis out, leave them out too:
# the mud flaps hang from the XT rear shock outriggers
CHASSIS_HUNG = ("BD-10",)


def body_parts(lay: Layout) -> list:
    """The body's own solids (cad/body_model.py), labelled and coloured, for the Body page's models."""
    from .body_model import body_solids
    kids = []
    for label, shp, col in body_solids(lay):
        shp.label = label.replace("/", "-")
        _paint(shp, col)
        kids.append(shp)
    return kids


def _inside(lay, b) -> bool:
    """A fit-out line inside the body: by its zone, or for a line with only a mass point, by its model's envelope."""
    if b.keep_clear or b.system not in FIT_SYSTEMS:
        return False
    if b.box is not None:
        return b.zone == "inside"
    spec = model_specs(lay).get(b.id)
    if spec is None:
        return False
    from .model import products as PR
    z = lay.zones["inside"]["box"]
    return any(all(bx[i] >= z[i] - 1 and bx[i + 3] <= z[i + 3] + 1 for i in range(3)) for _, bx in PR.placements(spec, b, lay))


def fitout_parts(lay: Layout) -> list:
    """The fit-out inside the body: bed, desk, kitchen, laundry, electrics, HVAC and the wet room."""
    return [s for b in lay.blocks if _inside(lay, b) and (s := part_shape(b, lay)) is not None]


def body_models(lay: Layout, night: Layout | None = None) -> dict:
    """The Body page's three models, by file name: the body with its fixed roof, and the body with the fit-out, bed up
    and, with `night`, bed down. Each is root > group > part, the tree the viewer files and the support check read."""
    kids = [k for k in body_parts(lay) if not k.label.startswith(CHASSIS_HUNG)]
    roof = [part_shape(b, lay, COLOURS["roof"]) for b in lay.blocks if b.system == "roof" and b.box is not None]
    out = {"body": Compound(label="ASM-BD Body, fixed roof",
                            children=[Compound(label="Body", children=kids), Compound(label="Solar panels", children=roof)])}
    for name, ly, title in (("body-inside", lay, "bed up"), ("body-inside-night", night, "bed down")):
        if ly is None:
            continue
        out[name] = Compound(label=f"ASM-BD Body with the fit-out, {title}",
                             children=[Compound(label="Body", children=[copy.copy(k) for k in kids]),
                                       Compound(label="Fit-out", children=fitout_parts(ly))])
    return out


def write_body_outputs(lay: Layout, out: Path, night: Layout | None = None):
    """The body on its own with its fixed roof, and the body with the bed and the living area fitted, for the Body page
    (BODY.md), and the body's STEP file. `night` is the same layout with the bed lowered (bed_state 1): it gives
    body-inside-night.viewer.json beside the day model (H1)."""
    from .export import _viewer_js
    for name, comp in body_models(lay, night).items():
        js = _viewer_js("ASM-BD", comp, **VIEWER_MESH)
        (out / f"{name}.viewer.json").write_text(js[js.index("{"): js.rindex("}") + 1])
        if name == "body":
            export_step(comp, str(out / "body.step"), timestamp="2026-11-20T00:00:00")

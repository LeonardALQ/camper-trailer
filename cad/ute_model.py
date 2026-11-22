"""3D model of the ute (cad/ute.py, data/ute/ute.yaml): the LandCruiser 79 as a product model (decision H27,
cad/model/vehicles/landcruiser.py) with the bike box. Phase U1 shows the box as an envelope. With a built ute garage
module (phase U2) the module's bodies are moved into the ute frame instead. Exports the three-cad-viewer JSON and STEP."""
from __future__ import annotations

import json
import math
from pathlib import Path

from build123d import Compound, Pos, export_step

from .model.assembly import GROUP_LABELS
from .model.prims import box, rgba
from .trailer_model import _moved

# The viewer's tessellation of the ute: 1 mm of chord error and 0.5 rad between facets keep the two product models, the
# LandCruiser and the bikes with their tyres and spokes, under the site's 8 MB a file (decision H27)
TESSELLATION = dict(deviation=1.0, angular_tolerance=0.5)


def vehicle_solids(ute, plain=False) -> list:
    """The LandCruiser in the ute frame (cad/model/vehicles/landcruiser.py): one node per part listed in data/ute/ute.yaml's
    `solids` and one per wheel, each holding its pieces in their colours. plain=True leaves out the tyres' tread and the
    wheel nuts, for the drawings."""
    from .model.vehicles import landcruiser as LC
    V = ute.V
    parts = LC.build(V, plain)
    vehicle = []
    for s in ute.d["solids"]:
        kids = []
        for name, shape, colour, alpha in parts[s["id"]]:
            shape.label, shape.color = name, rgba(colour, alpha)
            kids.append(shape)
        vehicle.append(Compound(label=f"{s['id']} {s['name']}", children=kids))
    for w in ute.d["wheels"]:
        x, y = ute.P.eval(w["x"], {}), ute.P.eval(w["y"], {})
        side = ("front" if w["id"][0] == "F" else "rear") + (", kerb side" if w["id"][1] == "K" else ", road side")
        kids = []
        for name, shape, colour, alpha in LC.wheel_parts(V, plain):
            k = LC.place_wheel(shape, (x, y, V["tyre_slr"]), 1.0 if y > 0 else -1.0)
            k.label, k.color = name, rgba(colour, alpha)
            kids.append(k)
        vehicle.append(Compound(label=f"WH-{w['id']} Wheel and tyre, {side}, ROH Trak 2 with LT265-75R16", children=kids))
    return vehicle


def garage_solids(ute, garage_model, loading=False, groups=None, exclude=()):
    """The garage module's bodies moved into the ute frame, as (instance, shape) pairs."""
    dx, dz = ute.garage["module_x0"], ute.garage["deck_z"]
    out = []
    for mb in garage_model.built.values():
        i = mb.inst
        if i.check_only or (i.display == "loading_only" and not loading) or (i.display == "closed_only" and loading):
            continue
        if (groups and i.group not in groups) or i.ref in exclude or i.iid in exclude:
            continue
        out.append((i, _moved(mb.shape, Pos(dx, 0, dz))))
    return out


def ute_compound(ute, garage_model=None, label="UTE-79", loading=False):
    V = ute.V
    vehicle = vehicle_solids(ute)
    kids = [Compound(label="Cab chassis and accessories", children=vehicle)]
    if garage_model is None:
        b = ute.box_extent()
        shell = box(b["x0"], b["y0"], b["z0"], b["x1"] - b["x0"], b["y1"] - b["y0"], b["z1"] - b["z0"])
        inner = box(b["x0"] + 45, b["y0"] + 45, V["deck_z"], b["x1"] - b["x0"] - 90, b["y1"] - b["y0"] - 90, b["z1"] - V["deck_z"] - 45)
        s = shell - inner
        s.label, s.color = "UT-08 Bike box envelope (report 17, until U2)", rgba("#b2bec3", 0.35)
        kids.append(Compound(label="Bike box", children=[s]))
    else:
        groups: dict[str, list] = {}
        for i, s in garage_solids(ute, garage_model, loading=loading):
            part = garage_model.prj.parts[i.part]
            # a bike shown elsewhere in the loading view (on the ramp) keeps its own id, so hover names the same bike
            who = i.special.get("bike", {}).get("shows", i.iid)
            s.label, s.color = f"{who} {i.label}".replace("/", "-"), rgba(part.color, part.alpha)
            groups.setdefault(i.group, []).append(s)
        kids.append(Compound(label="Bike garage", children=[Compound(label=GROUP_LABELS[g], children=v) for g, v in groups.items()]))
    return Compound(label=label, children=kids)


def _compact(o):
    """Round the tessellation in a viewer file: positions to 0.1 mm and normals to 0.001, which nobody sees and which
    halves the file."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("vertices", "edges", "obj_vertices"):
                o[k] = _rounded(v, 1)
            elif k == "normals":
                o[k] = _rounded(v, 3)
            else:
                _compact(v)
    elif isinstance(o, list):
        for v in o:
            _compact(v)
    return o


def _rounded(v, n):
    if isinstance(v, list):
        return [_rounded(x, n) for x in v]
    return round(v, n) if isinstance(v, float) else v


def _viewer(comp) -> str:
    from .export import _viewer_js
    js = _viewer_js("UTE-79", comp, **TESSELLATION)
    return json.dumps(_compact(json.loads(js[js.index("{"): js.rindex("}") + 1])), separators=(",", ":"))


def write_outputs(ute, out: Path, garage_model=None):
    out.mkdir(parents=True, exist_ok=True)
    comp = ute_compound(ute, garage_model)
    (out / "ute.viewer.json").write_text(_viewer(comp))
    export_step(comp, str(out / "ute.step"), timestamp="2026-11-20T00:00:00")
    if garage_model is not None:
        (out / "ute-loading.viewer.json").write_text(_viewer(ute_compound(ute, garage_model, loading=True)))
    return comp


def bike_box_sweep(ute, garage_model) -> dict:
    """What the trailer's jack-knife checks need from the bike box (TRAILER.md JK-01 and JK-02): the radius its parts
    behind the ball sweep about the ball in plan, and the lowest point of those parts above the ground. Every body of the
    garage module as it travels counts, so the cam bar, the hasp and the subframe are in it."""
    V = ute.V
    bx = V["ball_x"]
    r, under, who = 0.0, None, ""
    for i, s in garage_solids(ute, garage_model):
        if i.group == "context":
            continue
        bb = s.bounding_box()
        if bb.max.X <= bx:
            continue
        d = math.hypot(bb.max.X - bx, max(abs(bb.min.Y), abs(bb.max.Y)))
        if d > r:
            r, who = d, f"{i.iid} {i.label}"
        under = bb.min.Z if under is None else min(under, bb.min.Z)
    ext = ute.box_extent()
    return dict(radius_mm=round(r, 1), governing=who, underside_z=round(under, 1), ball_x=bx, ball_z=V["coupling_z"],
                overhang_mm=round(ext["x1"] - bx, 1), body_overhang_mm=round(ute.garage["module_x0"] + garage_model.prj.P.values["x_end"] - bx, 1),
                half_width_mm=round(max(abs(ute.body_extent()["y0"]), abs(ute.body_extent()["y1"])), 1))

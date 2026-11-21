"""3D model of the ute (cad/ute.py, data/ute/ute.yaml): envelope solids for the cab chassis, wheels, bull bar, towbar
and spare, plus the bike box. Phase U1 shows the box as an envelope. With a built ute garage module (phase U2) the
module's bodies are moved into the ute frame instead. Exports the three-cad-viewer JSON and STEP."""
from __future__ import annotations

import json
import math
from pathlib import Path

from build123d import Compound, Cylinder, Pos, Rot, export_step

from .model.assembly import GROUP_LABELS
from .model.prims import box, rgba
from .trailer_model import _moved


def _solid(ute, s):
    P = ute.P
    if "box" in s:
        x0, y0, z0, dx, dy, dz = P.eval(s["box"], {})
        return box(x0, y0, z0, dx, dy, dz)
    c = P.eval(s["cyl"], {})
    cx, cy, cz = c["c"]
    if c.get("axis", "y") == "z":
        return Pos(cx, cy, cz) * Cylinder(c["r"], c["w"])
    return Pos(cx, cy, cz) * Rot(90, 0, 0) * Cylinder(c["r"], c["w"])


def vehicle_solids(ute) -> list:
    """The cab chassis, wheels and accessories as labelled envelope solids in the ute frame."""
    V = ute.V
    vehicle = []
    for s in ute.d["solids"]:
        shp = _solid(ute, s)
        shp.label, shp.color = f"{s['id']} {s['name']}", rgba(s["color"], s["alpha"])
        vehicle.append(shp)
    for w in ute.d["wheels"]:
        x, y = ute.P.eval(w["x"], {}), ute.P.eval(w["y"], {})
        shp = Pos(x, y, V["tyre_slr"]) * Rot(90, 0, 0) * Cylinder(V["tyre_d"] / 2, V["tyre_w"])
        side = ("front" if w["id"][0] == "F" else "rear") + (", kerb side" if w["id"][1] == "K" else ", road side")
        shp.label, shp.color = f"WH-{w['id']} Wheel and tyre, {side}, ROH Trak 2 with LT265-75R16", rgba("#1c2833")
        vehicle.append(shp)
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
            s.label, s.color = f"{i.iid} {i.label}".replace("/", "-"), rgba(part.color, part.alpha)
            groups.setdefault(i.group, []).append(s)
        kids.append(Compound(label="Bike garage", children=[Compound(label=GROUP_LABELS[g], children=v) for g, v in groups.items()]))
    return Compound(label=label, children=kids)


def write_outputs(ute, out: Path, garage_model=None):
    from .export import _viewer_js
    out.mkdir(parents=True, exist_ok=True)
    comp = ute_compound(ute, garage_model)
    js = _viewer_js("UTE-79", comp)
    shapes = json.loads(js[js.index("{"): js.rindex("}") + 1])
    (out / "ute.viewer.json").write_text(json.dumps(shapes, separators=(",", ":")))
    export_step(comp, str(out / "ute.step"), timestamp="2026-11-20T00:00:00")
    if garage_model is not None:
        comp = ute_compound(ute, garage_model, loading=True)
        js = _viewer_js("UTE-79", comp)
        (out / "ute-loading.viewer.json").write_text(js[js.index("{"): js.rindex("}") + 1])
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

"""Exports: STEP (part numbers as product names), GLB (mass in node extras), three-cad-viewer JSON,
per-step viewer states, BOM JSON and CSV, and the mass schedule."""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from build123d import Compound, export_gltf, export_step

from .model.assembly import GROUP_LABELS, Model
from .model.prims import rgba

GROUP_ORDER = ["bikes", "restraint", "bed", "partitions", "safety", "context"]


def _module_filter(b) -> bool:
    """Bodies that belong to the travelling module (not check variants, not loading-only items)."""
    return not b.inst.check_only and b.inst.display != "loading_only"


def _relabel(shape, label):
    s = copy.copy(shape)
    s.label = label
    return s


def step_compound(model: Model):
    """Assembly tree for STEP: module > group > instance. Instances are named by part number."""
    prj = model.prj
    groups: dict[str, list] = {}
    for b in model.built.values():
        if not _module_filter(b):
            continue
        part = prj.parts[b.inst.part]
        if isinstance(b.shape, Compound) and b.shape.children:
            kids = []
            for k in b.shape.children:
                kk = copy.copy(k)
                kk.label = f"{part.id} {k.label}"
                kk.color = rgba(part.color, part.alpha)
                kids.append(kk)
            s = Compound(label=part.id, children=kids)
        else:
            s = _relabel(b.shape, part.id)
        s.color = rgba(part.color, part.alpha)
        groups.setdefault(b.inst.group, []).append(s)
    kids = [Compound(label=GROUP_LABELS[g], children=groups[g]) for g in GROUP_ORDER if g in groups]
    return Compound(label=f"{prj.assembly.id} {prj.assembly.name}", children=kids)


def write_step(model: Model, path: Path):
    export_step(step_compound(model), str(path), timestamp="2026-11-16T00:00:00")


def write_glb(model: Model, path: Path, mass_by_iid: dict):
    prj = model.prj
    groups: dict[str, list] = {}
    for b in model.built.values():
        if _module_filter(b):
            groups.setdefault(b.inst.group, []).append(b.shape)
    kids = [Compound(label=GROUP_LABELS[g], children=groups[g]) for g in GROUP_ORDER if g in groups]
    export_gltf(Compound(label=prj.assembly.id, children=kids), str(path), binary=True,
                linear_deflection=0.5, angular_deflection=0.5)
    from pygltflib import GLTF2
    g = GLTF2().load(str(path))
    tagged = 0
    for n in g.nodes:
        iid = (n.name or "").split(" ")[0]
        if iid in model.built and iid in mass_by_iid:
            n.extras = mass_by_iid[iid]
            tagged += 1
    g.save(str(path))
    return tagged


def _viewer_name(b) -> str:
    return f"{b.inst.iid} {b.inst.label}".replace("/", "-")


def _viewer_js(root: str, obj, deviation=0.3, angular_tolerance=0.35) -> str:
    """ocp-tessellate's export_three_cad_viewer_js, with coarser tessellation to keep the file small."""
    from ocp_tessellate.convert import numpy_to_js, tessellate_group, to_ocpgroup
    part_group, instances = to_ocpgroup(obj)
    instances, shapes, _ = tessellate_group(part_group, instances,
                                            kwargs={"deviation": deviation, "angular_tolerance": angular_tolerance})

    def walk(o):
        for p in o.get("parts", []) or []:
            walk(p)
        if o.get("type") == "shapes" and isinstance(o.get("shape"), dict) and o["shape"].get("ref") is not None:
            o["shape"] = instances[o["shape"]["ref"]]
    walk(shapes)
    return numpy_to_js(root, shapes)


def write_viewer(model: Model, path: Path, loading: bool = False):
    """three-cad-viewer JSON with the part tree grouped. Returns {iid: leaf path prefix}.
    The main file leaves out the loading-only items (ramp, ground) so the camera frames the module.
    The loading file has everything, for the loading step."""
    prj = model.prj
    root = prj.assembly.id
    groups: dict[str, list] = {}
    paths: dict[str, str] = {}
    for b in model.built.values():
        if b.inst.check_only or (b.inst.display == "loading_only" and not loading):
            continue
        s = copy.copy(b.shape)
        s.label = _viewer_name(b)
        groups.setdefault(b.inst.group, []).append(s)
        paths[b.inst.iid] = f"/{root}/{GROUP_LABELS[b.inst.group]}/{s.label}"
    kids = [Compound(label=GROUP_LABELS[g], children=groups[g]) for g in GROUP_ORDER if g in groups]
    js = _viewer_js(root, Compound(label=root, children=kids))
    shapes = json.loads(js[js.index("{"): js.rindex("}") + 1])
    path.write_text(json.dumps(shapes, separators=(",", ":")))
    return paths


def step_states(model: Model, paths: dict) -> dict:
    """Per-step visibility: earlier work (greyed), new items (highlighted), hidden items."""
    prj = model.prj
    steps = prj.steps
    bikes = {i.iid for i in prj.instances if i.group == "bikes"}
    context = [i.iid for i in prj.instances if i.group == "context" and not i.check_only]
    loading_only = {i.iid for i in prj.instances if i.display == "loading_only"}
    done: list[str] = []
    out = []
    for s in steps:
        new = [i.iid for i in prj.select(s.new, include_check_only=False)]
        hide = {i.iid for i in prj.select(s.hide, include_check_only=False)}
        earlier = [i for i in done if i not in new and i not in hide and i not in bikes]
        ctx = [c for c in context if c not in new and c not in hide and (c not in loading_only)]
        shows_loading = any(i in loading_only for i in new)
        out.append(dict(
            id=s.id, title=s.title, model="garage-bed-loading.json" if shows_loading else "garage-bed.json",
            new=[paths[i] for i in new if i in paths],
            earlier=[paths[i] for i in dict.fromkeys(earlier + ctx) if i in paths],
        ))
        done.extend(n for n in new if n not in done and n not in bikes)
    default_hidden = [paths[i] for i in loading_only if i in paths]
    return dict(steps=out, default_hidden=default_hidden, paths=paths)


def bom_rows(lines: list[dict]) -> list[dict]:
    rows = []
    for r in lines:
        rows.append({
            "ID": r["id"], "Group": r["group"], "Item": r["item"], "Product": r["product"] or "", "Maker": r["maker"] or "",
            "Part no": r["part_no"] or "", "Qty": round(r["qty"], 3) if isinstance(r["qty"], float) else r["qty"],
            "Unit": r["unit"] or "", "Unit mass": "" if r["unit_mass"] is None else r["unit_mass"],
            "Mass basis": r["basis"], "Total kg": round(r["mass_kg"], 3), "Maturity": r["maturity"],
            "Mass source": r["source"], "CoG X": r["cog"][0], "CoG Y": r["cog"][1], "CoG Z": r["cog"][2],
            "Size / rating": ". ".join(x for x in (r["size"], r["rating"]) if x),
            "Maker link": next(iter(r["links"].values()), "") if r["links"] else "",
            "AU stockist": r["stockist_au"] or "", "Removable": "yes" if r["removable"] else "", "Notes": r["notes"] or "",
        })
    return rows


def write_bom_csv(lines: list[dict], path: Path):
    rows = bom_rows(lines)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

"""Pipeline entry point. Run inside the project image from the repo root:

    python -m cad.build data      validate data/, write the JSON Schema and the resolved project
    python -m cad.build model     build the model; STEP, GLB, viewer JSON, step states, BOM, mass schedule
    python -m cad.build trailer   whole-trailer layout: axle solve, load cases, checks, length comparison, 3D model
    python -m cad.build drawings  drawing sheets to SVG, PDF and PNG
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from .partsdb import ROOT, Project, schema

BUILD = ROOT / "build"


def git_hash() -> str:
    import os
    if os.environ.get("GIT_REV"):
        return os.environ["GIT_REV"]
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              timeout=10).stdout.strip() or "uncommitted"
    except Exception:
        return "unknown"


def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def cmd_data():
    t0 = time.time()
    prj = Project()
    _write(BUILD / "data" / "parts.schema.json", schema())
    _write(BUILD / "data" / "project.json", dict(
        assembly=dict(id=prj.assembly.id, name=prj.assembly.name, revision=prj.assembly.revision),
        params=prj.P.values,
        instances=[i.model_dump() for i in prj.instances],
        parts={k: v.model_dump() for k, v in prj.parts.items()},
    ))
    lines = prj.bom_lines()
    print(f"data OK: {len(prj.parts)} parts ({len(lines)} BOM lines), {len(prj.instances)} placed instances, "
          f"{len(prj.checks)} checks, {len(prj.load.load_cases)} load cases, {len(prj.steps)} steps "
          f"({time.time() - t0:.2f} s)")


def cmd_model():
    from . import solve as SV
    if SV.cached() is None:
        t = time.time()
        s = SV.solve()
        print(f"bike spacing solved from the geometry: {s['bike_spacing']:.0f} mm, "
              f"CLR-03 {s['clr03_gap']:.1f} mm ({time.time() - t:.1f} s)")
    from . import export as X
    from . import massprops as MP
    from .model.assembly import Model
    tm = {}
    t = time.time()
    prj = Project()
    model = Model(prj)
    tm["build_model_s"] = round(time.time() - t, 2)
    out = BUILD / "model"
    out.mkdir(parents=True, exist_ok=True)

    t = time.time()
    lines = MP.line_masses(prj, model)
    bikes = MP.bike_rows(prj, model)
    cases = MP.load_cases(prj, lines, bikes)
    totals = MP.group_totals(lines)
    tm["mass_s"] = round(time.time() - t, 2)
    body_mass = dict(MP.BODY_MASS)
    for b in bikes:
        body_mass[b["id"]] = dict(part_id=b["part"], mass_kg=b["mass_kg"], cog_mm=b["cog"], maturity=b["maturity"])

    t = time.time()
    X.write_step(model, out / "garage-bed.step")
    tm["step_s"] = round(time.time() - t, 2)
    t = time.time()
    tagged = X.write_glb(model, out / "garage-bed.glb", body_mass)
    tm["glb_s"] = round(time.time() - t, 2)
    t = time.time()
    paths = X.write_viewer(model, out / "garage-bed.viewer.json")
    paths.update(X.write_viewer(model, out / "garage-bed-loading.viewer.json", loading=True))
    _write(out / "steps.json", X.step_states(model, paths))
    tm["viewer_s"] = round(time.time() - t, 2)

    # bike envelope sizes against the owner's figures
    bike_sizes = {}
    for ref in ("TU", "ST", "TU-2263", "TU-1390"):
        b = model.built[ref]
        bike_sizes[ref] = dict(label=b.inst.label, model=b.info["local_size"], owner=b.info["owner"],
                               pitch_deg=round(b.info["pitch_deg"], 3))
    instances = {}
    for b in model.built.values():
        bb = b.shape.bounding_box()
        instances[b.inst.iid] = dict(
            part=b.inst.part, label=b.inst.label, group=b.inst.group, step=b.inst.step, display=b.inst.display,
            check_only=b.inst.check_only, bbox=[round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)],
            info={k: v for k, v in b.info.items() if k not in ("points",)}, points=b.info.get("points"))
    bom_dir = BUILD / "bom"
    _write(bom_dir / "bom.json", dict(lines=lines, bikes=bikes, totals=totals, load_cases=cases,
                                      towball=prj.load.towball.model_dump(), git=git_hash()))
    X.write_bom_csv(lines, bom_dir / "garage-bed-bom.csv")
    _write(out / "instances.json", dict(instances=instances, bike_sizes=bike_sizes, params=prj.P.values,
                                        glb_nodes_tagged=tagged, timings=tm))
    print(json.dumps(dict(timings=tm, module_empty_kg=round(totals["module_empty"], 2),
                          with_bikes_kg=round(totals["module_empty"] + sum(b["mass_kg"] for b in bikes), 2),
                          load_cases=[(c["id"], round(c["mass_kg"], 1), c["cog"]) for c in cases],
                          bikes=bike_sizes, glb_nodes_tagged=tagged), indent=1))


def cmd_trailer():
    from . import trailer as T
    from .model.assembly import Model
    from .trailer_model import TrailerModel, write_outputs
    t0 = time.time()
    prj = Project()
    model = Model(prj)
    tr = T.Trailer(prj, T.ModuleInfo.from_model(prj, model))
    rep = T.report(tr)
    rep["git"] = git_hash()
    out = BUILD / "trailer"
    _write(out / "trailer.json", rep)
    from .chassis_checks import report as chassis_report
    chs = chassis_report(tr, tr.last_layout)
    chs["git"] = rep["git"]
    _write(BUILD / "chassis" / "chassis.json", chs)
    _cut_list(chs, BUILD / "chassis" / "chassis-cut-list.csv")
    body = tr.body_results(tr.last_layout)
    body["git"] = rep["git"]
    _write(BUILD / "body" / "body.json", body)
    t1 = time.time()
    lay = tr.layout(**rep["solved"]["overrides"])
    write_outputs(TrailerModel(lay, model, body=True), out)
    from .trailer_model import write_body_outputs
    write_body_outputs(lay, out)
    fails = [c["id"] for c in rep["checks"] if c["severity"] == "fail" and not c["ok"]]
    print(json.dumps(dict(
        axle_x=rep["solved"]["axle_x"], method=rep["solved"]["method"], recommended=rep["recommended"],
        cases=[(c["id"], round(c["nominal"]["mass_kg"]), round(c["nominal"]["towball_kg"]), round(c["growth"]["mass_kg"]),
                round(c["growth"]["towball_kg"])) for c in rep["cases"]],
        failed_checks=fails, layout_s=round(t1 - t0, 1), model_s=round(time.time() - t1, 1)), indent=1))
    if not rep["recommended"]["matches_data"]:
        print(f"NOTE: the recommended body length {rep['recommended']['body_length']} differs from the data ({rep['body_length']})")


def _cut_list(chs: dict, path: Path):
    """One row per member and plate, for the fabricator (DRAFT until the engineer reviews CHASSIS.md)."""
    import csv
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Mark", "Item", "Section or plate", "Length mm", "Qty", "kg each", "kg", "Note"])
        for m in chs["members"]:
            w.writerow([m["id"], m["name"], m["section"], round(m["length_mm"]), 1, round(m["mass_kg"], 2), round(m["mass_kg"], 2),
                        m["note"] or ""])
        for f in chs["fittings"]:
            if f["kind"] in ("plate", "tube"):
                size = " x ".join(f"{v:g}" for v in f["dims"]) + " plate" if f["dims"] else f["name"].split(",")[1].strip()
                w.writerow([f["id"], f["name"], size, "", f["qty"], round(f["mass_each_kg"], 2), round(f["mass_kg"], 2), f["source"]])
        w.writerow(["", "DRAFT, NOT FOR CONSTRUCTION until the engineer reviews CHASSIS.md", "", "", "", "", "", ""])


def cmd_ute():
    """The tow vehicle and its bike garage (UTE-GARAGE.md): mass budget, axle loads, checks, the 3D model and STEP."""
    from .ute import Ute
    from .ute_model import write_outputs
    t0 = time.time()
    garage, gmodel = None, None
    try:
        from .ute_garage import build_garage
        garage, gmodel = build_garage()
    except ImportError:
        pass
    ute = Ute(garage)
    rep = ute.report()
    rep["git"] = git_hash()
    if garage:
        rep["garage"] = {k: v for k, v in garage.items() if k != "lines"}
    _write(BUILD / "ute" / "ute.json", rep)
    write_outputs(ute, BUILD / "ute", gmodel)
    fails = [c["id"] for c in rep["checks"] if c["severity"] == "fail" and not c["ok"]]
    print(json.dumps(dict(cases=[(c["id"], round(c["nominal"]["mass_kg"]), round(c["nominal"]["front_kg"]), round(c["nominal"]["rear_kg"]),
                                  round(c["nominal"]["ssf"], 3), round(c["growth"]["mass_kg"]), round(c["growth"]["rear_kg"]))
                                 for c in rep["cases"]],
                          failed_checks=fails, seconds=round(time.time() - t0, 1)), indent=1))


def cmd_drawings():
    from .drawings import sheets
    sheets.main()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "model"
    {"data": cmd_data, "model": cmd_model, "trailer": cmd_trailer, "ute": cmd_ute, "drawings": cmd_drawings}[cmd]()

"""Pipeline entry point. Run inside the project image from the repo root:

    python -m cad.build data      validate data/, write the JSON Schema and the resolved projects
    python -m cad.build model     the bike spacing from the geometry (the ute's bike box)
    python -m cad.build ute       the LandCruiser 79 and its bike box: checks, the 3D model, STEP, the bike box's sweep
    python -m cad.build trailer   whole-trailer layout: axle solve, load cases, checks, chassis and body, 3D model
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
        rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                             timeout=10).stdout.strip() or "uncommitted"
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"], capture_output=True,
                               text=True, timeout=10).stdout.strip()
        return rev + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


def _write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def cmd_data():
    t0 = time.time()
    prj = Project()
    ute = Project(assembly="ute-garage")
    _write(BUILD / "data" / "parts.schema.json", schema())
    _write(BUILD / "data" / "project.json", dict(
        trailer=dict(checks=len(prj.trailer_checks), cases=[c.id for c in prj.load.trailer_cases]),
        ute_garage=dict(assembly=dict(id=ute.assembly.id, name=ute.assembly.name, revision=ute.assembly.revision),
                        params=ute.P.values, instances=[i.model_dump() for i in ute.instances],
                        parts={k: v.model_dump() for k, v in ute.parts.items()}),
    ))
    print(f"data OK: trailer {len(prj.trailer_checks)} checks and {len(prj.load.trailer_cases)} load cases, ute garage "
          f"{len(ute.parts)} parts, {len(ute.instances)} placed instances and {len(ute.checks)} checks ({time.time() - t0:.2f} s)")


def cmd_model():
    """The bike spacing in the ute's bike box from the geometry (cad/solve.py), and the trailer's heaviest towball for the
    ute's towing cases (cad/towball.py), both cached for the later stages."""
    from . import solve as SV
    from . import towball as TB
    t = time.time()
    s = SV.cached() or SV.solve()
    print(f"bike spacing from the geometry: {s['bike_spacing']:.0f} mm, UGC-01 {s['clr03_gap']:.1f} mm ({time.time() - t:.1f} s)")
    t = time.time()
    b = TB.cached() or TB.solve()
    print(f"trailer's heaviest towball with growth: {b['towball_kg']:.1f} kg ({b['case']}, axle X {b['axle_x']:.1f}), "
          f"carried by the ute's towing cases ({time.time() - t:.1f} s)")


def cmd_trailer():
    from . import trailer as T
    from .trailer_model import TrailerModel, write_outputs
    t0 = time.time()
    tr = T.Trailer(Project())
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
    write_outputs(TrailerModel(lay, body=True), out)
    from .trailer_model import write_body_outputs
    write_body_outputs(lay, out, night=tr.layout(**{**rep["solved"]["overrides"], "bed_state": 1}))
    from .floorplan import write_plans    # the floor plan, bed up and bed down, cut from the model (H28)
    write_plans(lay, tr.layout(**{**rep["solved"]["overrides"], "bed_state": 1}), body, BUILD / "floorplan")
    from .partsmeta import trailer_lookup, write as write_parts
    look = trailer_lookup(lay, body)
    for name in ("trailer", "chassis", "body", "body-inside", "body-inside-night"):
        write_parts(out / f"{name}.viewer.json", look)
    fails = [c["id"] for c in rep["checks"] if c["severity"] == "fail" and not c["ok"]]
    print(json.dumps(dict(
        axle_x=rep["solved"]["axle_x"], method=rep["solved"]["method"], tare_kg=rep["tare_kg"],
        cases=[(c["id"], round(c["nominal"]["mass_kg"]), round(c["nominal"]["towball_kg"]), round(c["growth"]["mass_kg"]),
                round(c["growth"]["towball_kg"])) for c in rep["cases"]],
        failed_checks=fails, layout_s=round(t1 - t0, 1), model_s=round(time.time() - t1, 1)), indent=1))


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
        from .ute_model import bike_box_sweep
        rep["bike_box_sweep"] = bike_box_sweep(ute, gmodel)
    _write(BUILD / "ute" / "ute.json", rep)
    write_outputs(ute, BUILD / "ute", gmodel)
    from .partsmeta import ute_lookup, write as write_parts
    look = ute_lookup(ute, gmodel)
    for name in ("ute", "ute-loading"):
        if (BUILD / "ute" / f"{name}.viewer.json").exists():
            write_parts(BUILD / "ute" / f"{name}.viewer.json", look)
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

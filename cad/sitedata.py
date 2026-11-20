"""Copy build outputs into the site and generate the data-driven pages (research, tow vehicle).

Run inside the project image from the repo root:  python -m cad.sitedata
"""
from __future__ import annotations

import json
import re
import shutil

import yaml

from .build import BUILD
from .partsdb import ROOT

SITE = ROOT / "site"
GEN = SITE / "src" / "data" / "generated"
DOCS = SITE / "src" / "content" / "docs"
RESEARCH = [
    ("01-tech-stack.md", "Tech stack for the design site", 1),
    ("02-design-practice.md", "Design, drawing and documentation practice", 2),
    ("03-bike-restraint-garage.md", "Bike restraint and garage fit-out", 3),
    ("04-bed-and-materials.md", "Bed above the bikes, and build materials", 4),
    ("05-bike-geometry.md", "Bike geometry for envelope models", 5),
    ("06-trailer-running-gear.md", "Trailer running gear: suspension, hubs, brakes and sway control", 6),
    ("07-tow-vehicle.md", "Tow vehicle: the 2013 Porsche Cayenne GTS (958), superseded", 7),
    ("08-coupling-and-hitch.md", "Coupling and hitch", 8),
    ("09-trailer-wheels-and-tyres.md", "Trailer wheels, tyres and stud pattern", 9),
    ("10-car-wheels-and-tyres.md", "The Cayenne’s wheels and tyres for towing, superseded", 10),
    ("11-chassis-design.md", "Chassis and drawbar design basis", 11),
    ("12-body-design.md", "Body design basis", 12),
    ("13-equipment.md", "Appliances, equipment and the energy system", 13),
    ("14-engine.md", "LandCruiser 79 V8 engine, rebuild, turbo, exhaust and tune", 14),
    ("15-driveline.md", "LandCruiser 79 V8 driveline and reliability refresh", 15),
    ("16-ute-limits.md", "LandCruiser 79 limits, GVM, GCM, brakes, wheels and towing", 16),
    ("17-ute-garage.md", "The enclosed motorbike garage on the LandCruiser 79", 17),
]
# sections of VEHICLE.md shown on the Tow vehicle page, in order
VEHICLE_SECTIONS = ("Summary", "Decisions", "Budget", "Order of work")
SYSTEMS = {
    "engine": "Engine rebuild and cooling", "fuel_system": "Fuel system", "intake_dpf": "Sealed airbox and DPF service",
    "turbo_exhaust": "Turbo, intercooler and exhaust", "tune_legal": "Tune, gauges and engine certificate",
    "clutch_gearbox": "Clutch and gearbox", "driveline": "Transfer case, tailshafts, diffs and hubs",
    "steering_suspension": "Steering and front suspension",
    "refresh": "Chassis, cab, electrical, fuel lines, air conditioning, fluids",
    "gvm": "GVM kit, fitting and certificate", "brakes": "Brakes", "wheels_tyres": "Wheels and tyres",
    "towing": "Towing", "freight_weighing": "Freight and weighing", "fuel_tank": "Long-range fuel tank",
    "bar_winch": "Bull bar and winch, only if the truck has none", "level_b": "Power level B, later",
}


def _copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _cell(v):
    return "" if v is None else str(v).replace("|", "/").replace("\n", " ")


def _sections(text, names):
    """The level-2 sections of a markdown file with these names, each with its level-3 subsections."""
    parts = re.split(r"(?m)^(?=## )", text)
    keep = {p.split("\n", 1)[0][3:].strip(): p for p in parts[1:]}
    return [keep[n].rstrip() + "\n" for n in names]


def tow_vehicle_page():
    """The Tow vehicle page: VEHICLE.md's summary, decisions, budget and order of work, then the parts list
    rendered from data/vehicle/vehicle-parts.yaml."""
    plan = (ROOT / "VEHICLE.md").read_text(encoding="utf-8")
    data = yaml.safe_load((ROOT / "data" / "vehicle" / "vehicle-parts.yaml").read_text(encoding="utf-8"))
    (GEN / "vehicle.json").write_text(json.dumps(data, indent=1, default=str))
    tot = data["totals_aud"]
    out = ["---\ntitle: Tow vehicle\ndescription: 'The LandCruiser 79 vehicle plan: summary, decisions, budget, "
           "order of work and the parts list.'\n---\n\n",
           "The tow vehicle is a Toyota LandCruiser 79 single cab V8 (VDJ79). It replaces the Porsche Cayenne, "
           "and it carries both motorbikes in an enclosed box on its tray (see the Ute garage page). This page "
           "shows four sections of the vehicle plan, `VEHICLE.md`, and then every part and job in "
           "`data/vehicle/vehicle-parts.yaml`. The engine, driveline, suspension, brakes, wheels, towing, legal "
           "and limits sections are in `VEHICLE.md` itself. The basis is research reports 14, 15 and 16.\n\n"]
    for s in _sections(plan, VEHICLE_SECTIONS):
        out.append(s.replace("`vehicle-parts.yaml`", "the parts list below") + "\n")
    out.append("## Parts list\n\nRendered from `data/vehicle/vehicle-parts.yaml`. Prices are AUD including GST, the line "
               "total. Basis is listing (read from a supplier or regulator page) or estimate. Status is required, "
               "contingency (only if an inspection or test calls for it) or optional.\n\n")
    groups = {}
    for it in data["items"]:
        groups.setdefault(it.get("system"), []).append(it)
    for key, rows in groups.items():
        out.append(f"### {SYSTEMS.get(key, key)}\n\n| ID | Item | Supplier | AUD | Basis | Status |\n|---|---|---|---|---|---|\n")
        for it in rows:
            name = _cell(it["name"])
            if it.get("link"):
                name = f"[{name}]({it['link']})"
            if it.get("note"):
                name += f". {_cell(it['note'])}"
            out.append(f"| {it['id']} | {name} | {_cell(it.get('supplier'))} | {it['price_aud']:,.0f} | "
                       f"{it.get('price_basis', '')} | {it.get('status', '')} |\n")
        out.append("\n")
    out.append("### Lines the merge removed\n\n| Item | AUD | Why |\n|---|---|---|\n")
    for it in data.get("removed", []):
        out.append(f"| {_cell(it['name'])} | {it['price_aud']:,.2f} | {_cell(it['reason'])} |\n")
    out.append(f"\n### Totals\n\n| Total | AUD |\n|---|---|\n| Required | {tot['required']:,} |\n"
               f"| Required with the contingency allowance | {tot['required_plus_contingency']:,} |\n"
               f"| With every cut and the contingency allowance | {tot['with_cuts_plus_contingency']:,} |\n"
               f"| Target | {tot['target']:,} |\n| Bike box, separate | {tot['bike_box_separate']:,} |\n")
    (DOCS / "tow-vehicle.md").write_text("".join(out), encoding="utf-8")
    return len(data["items"])


def main():
    for d in (GEN, SITE / "public" / "models", SITE / "public" / "downloads" / "drawings", SITE / "public" / "drawings",
              DOCS / "research"):
        d.mkdir(parents=True, exist_ok=True)
    # data for the components
    _copy(BUILD / "checks" / "checks.json", GEN / "checks.json")
    _copy(BUILD / "drawings" / "register.json", GEN / "register.json")
    _copy(BUILD / "trailer" / "trailer.json", GEN / "trailer.json")
    # models and downloads
    _copy(BUILD / "trailer" / "trailer.viewer.json", SITE / "public" / "models" / "trailer.json")
    _copy(BUILD / "trailer" / "trailer.step", SITE / "public" / "downloads" / "trailer.step")
    _copy(BUILD / "trailer" / "trailer.glb", SITE / "public" / "downloads" / "trailer.glb")
    _copy(BUILD / "trailer" / "chassis.viewer.json", SITE / "public" / "models" / "chassis.json")
    _copy(BUILD / "trailer" / "chassis.step", SITE / "public" / "downloads" / "chassis.step")
    _copy(BUILD / "trailer" / "body.viewer.json", SITE / "public" / "models" / "body.json")
    _copy(BUILD / "trailer" / "body-inside.viewer.json", SITE / "public" / "models" / "body-inside.json")
    _copy(BUILD / "trailer" / "body.step", SITE / "public" / "downloads" / "body.step")
    _copy(BUILD / "body" / "body.json", GEN / "body.json")
    _copy(BUILD / "ute" / "ute.json", GEN / "ute.json")
    _copy(BUILD / "ute" / "ute.viewer.json", SITE / "public" / "models" / "ute.json")
    _copy(BUILD / "ute" / "ute-loading.viewer.json", SITE / "public" / "models" / "ute-loading.json")
    _copy(BUILD / "ute" / "ute.step", SITE / "public" / "downloads" / "ute.step")
    _copy(BUILD / "chassis" / "chassis.json", GEN / "chassis.json")
    _copy(BUILD / "chassis" / "chassis-cut-list.csv", SITE / "public" / "downloads" / "chassis-cut-list.csv")
    import cairosvg
    reg = json.loads((BUILD / "drawings" / "register.json").read_text())
    live = [d for d in reg["drawings"] if d.get("status") != "RETIRED"]
    for d in live:
        n = d["number"]
        for ext in ("pdf", "svg"):
            _copy(BUILD / "drawings" / f"{n}.{ext}", SITE / "public" / "downloads" / "drawings" / f"{n}.{ext}")
        _copy(BUILD / "drawings" / f"{n}.png", SITE / "public" / "drawings" / f"{n}.png")
        cairosvg.svg2png(url=str(BUILD / "drawings" / f"{n}.svg"),
                         write_to=str(SITE / "public" / "drawings" / f"{n}-preview.png"), output_width=1754)

    # the tow vehicle page
    n_parts = tow_vehicle_page()

    # research reports as pages (copied, with the first heading moved into the title)
    for old in (DOCS / "research").glob("*.md"):
        old.unlink()
    for fname, title, order in RESEARCH:
        text = (ROOT / "research" / fname).read_text(encoding="utf-8")
        text = re.sub(r"\A#\s+[^\n]*\n", "", text, count=1)
        # links between reports point at the .md files in the repository; on the site they go to the report's page
        text = re.sub(r"\]\((\d\d-[a-z0-9-]+)\.md\)", r"](../\1/)", text)
        # the YAML files beside a report are in the repository only, so name them instead of linking
        text = re.sub(r"\[[^\]]+\]\((\d\d-[a-z0-9-]+\.yaml)\)", r"`research/\1`", text)
        body = (f"---\ntitle: '{title}'\nsidebar:\n  order: {order}\n---\n\n"
                f"This is research report {fname[:2]}, copied unchanged from `research/{fname}` apart from its first heading.\n\n"
                + text)
        (DOCS / "research" / fname).write_text(body, encoding="utf-8")
    print(f"site data written: {len(RESEARCH)} research pages, {len(live)} live drawings "
          f"({len(reg['drawings']) - len(live)} retired), tow vehicle page with {n_parts} parts")


if __name__ == "__main__":
    main()

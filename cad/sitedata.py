"""Copy build outputs into the site and generate the data-driven pages (research, car build, bike box parts).

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
    ("03-bike-restraint-garage.md", "Bike restraint and garage fit-out (now in the ute’s bike box)", 3),
    ("04-bed-and-materials.md", "Bed above the bikes, and build materials (trailer garage, retired)", 4),
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
    ("18-trailer-layout-79.md", "The trailer’s layout for the LandCruiser 79", 18),
]
# sections of VEHICLE.md shown on the Car build page, in order. The stage table, the parts list and every total are
# rendered from data/vehicle/vehicle-parts.yaml instead, so the page types no figure itself.
VEHICLE_TOP = ("Summary", "Stage plan")
VEHICLE_END = ("Limits to build and drive to", "Legal path", "Decisions", "Open points and the assumption used")
SYSTEMS = {
    "engine": "Engine rebuild, cooling and baseline tests", "fuel_system": "Fuel system", "intake_dpf": "Sealed airbox and DPF service",
    "turbo_exhaust": "Turbo, intercooler and exhaust", "tune_legal": "Tune, gauges and engine certificate",
    "clutch_gearbox": "Clutch and gearbox", "driveline": "Transfer case, tailshafts, diffs and hubs",
    "steering_suspension": "Steering and front suspension",
    "refresh": "Chassis, cab, electrical, fuel lines, air conditioning, fluids",
    "gvm": "GVM kit, GCM revision and certificate", "brakes": "Brakes", "wheels_tyres": "Wheels and tyres",
    "towing": "Towing and trailer charging", "freight_weighing": "Freight and weighing", "fuel_tank": "Long-range fuel tank",
    "bar_winch": "Bull bar and winch, only if the truck has none",
}
STATUSES = ("required", "contingency", "optional")
PRIORITIES = {"P1": "Safe, legal and reliable towing, or protecting the truck", "P2": "The 224 kW minimum",
              "P3": "Optional, comfort or a cost cut"}

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


def _aud(v):
    return f"{v:,.0f}"


def _cents(v):
    """AUD to the cent, for the tables whose footer adds the rows up, so the footer's sum is the exact total."""
    return f"{v:,.2f}"


def _drop_first_table(text):
    """A section's text without its first Markdown table."""
    out, state = [], "before"
    for ln in text.split("\n"):
        if state == "before" and ln.startswith("|"):
            state = "in"
        if state == "in":
            if ln.startswith("|"):
                continue
            state = "after"
        out.append(ln)
    return "\n".join(out)


def project() -> dict:
    """Leonard's whole-project figures (data/project.yaml): the truck's price and the car build's budget."""
    return yaml.safe_load((ROOT / "data" / "project.yaml").read_text(encoding="utf-8"))


def car_totals(data, budget) -> dict:
    """Every total of the car build, worked out from its lines: by status, priority, stage and system, and the
    figures against Leonard's build budget, with the cuts, in the list's order, that close the gap. The figures against
    the budget add up whole dollars (the required total and the savings rounded first), so the Totals table adds up
    as shown and matches VEHICLE.md."""
    sums = {}
    for it in data["items"]:
        for key in ((it["status"],), ("priority", it["priority"], it["status"]), ("stage", it["stage"], it["status"]),
                    ("system", it["system"], it["status"])):
            sums[key] = sums.get(key, 0.0) + it["price_aud"]
    req = round(sums.get(("required",), 0.0))
    allow = data["totals_aud"]["contingency_allowance"]
    gap = req + allow - budget
    closing, saved = [], 0.0
    for c in data["cuts"]:
        if saved >= gap:
            break
        closing.append(c["id"])
        saved += c["saving_aud"]
    saved, cuts = round(saved), round(sum(c["saving_aud"] for c in data["cuts"]))
    return dict(sums=sums, required=req, contingency_lines=round(sums.get(("contingency",), 0.0)),
                optional=round(sums.get(("optional",), 0.0)), allowance=allow, with_contingency=req + allow, budget=budget,
                gap=gap, closing=closing, closing_saving=saved, with_closing=req + allow - saved, cuts=cuts,
                with_cuts=req - cuts + allow)


def tow_vehicle_page():
    """The Car build page: VEHICLE.md's summary and stage plan with the stage table, the whole parts list as one
    spreadsheet and the totals, all from data/vehicle/vehicle-parts.yaml, then VEHICLE.md's limits, legal path,
    decisions and open points. The URL stays /tow-vehicle/ so earlier links still work."""
    plan = (ROOT / "VEHICLE.md").read_text(encoding="utf-8")
    data = yaml.safe_load((ROOT / "data" / "vehicle" / "vehicle-parts.yaml").read_text(encoding="utf-8"))
    T = car_totals(data, project()["car_build"]["budget_aud"])
    data["computed"] = {k: v for k, v in T.items() if k != "sums"}
    (GEN / "vehicle.json").write_text(json.dumps(data, indent=1, default=str))
    S = T["sums"]
    get = lambda *k: S.get(k, 0.0)
    out = ["---\ntitle: Car build\ndescription: 'The LandCruiser 79 car build: stages, the priced parts list with priority, reason and "
           "stage on every line, the totals, the limits and the legal path.'\n---\n\n",
           "The car build turns a used Toyota LandCruiser 79 single cab V8 (VDJ79) into the tow vehicle for the trailer, with both "
           "motorbikes in the [bike box](../ute-garage/) on its tray. The plan is `VEHICLE.md`, and every part and paid job is a line in "
           "`data/vehicle/vehicle-parts.yaml`. This page shows the plan's summary and stages, then every line and total from the YAML. "
           "The 3D model of the ute with its box is on the [Bike box](../ute-garage/#3d-model) page and the general arrangement is "
           "drawing [CT-701](../drawings/#ct-701). VEH-01 to VEH-27 are on the [Measurements](../measurements/?part=car) page.\n\n"]
    secs = dict(zip(VEHICLE_TOP + VEHICLE_END, _sections(plan, VEHICLE_TOP + VEHICLE_END)))
    out.append(secs["Summary"] + "\n")
    rows = ("| Stage | Work | Required AUD | Contingency lines AUD | Optional AUD | Paid labour | Downtime (est.) | "
            "Place in branch A, B | The ute can then |\n|---|---|---|---|---|---|---|---|---|\n")
    for st in data["stages"]:
        rows += (f"| {st['id']} | {_cell(st.get('work'))} | " +
                 " | ".join(_cents(get("stage", st["id"], s)) for s in STATUSES) +
                 f" | {_cell(st.get('labour'))} | {_cell(st.get('downtime'))} | A {st['order_a'] + 1}, B {st['order_b'] + 1} | "
                 f"{_cell(st['can_do'])} |\n")
    head, rest = secs["Stage plan"].split("\n", 1)
    out.append(head + "\n\nEach stage's lines added up by status, from the YAML. The sheet's footer gives the totals. Contingency "
               "lines are bought only if a test calls for them.\n\n" + rows + _drop_first_table(rest) + "\n")

    # ---------------------------------------------------------------- the parts list, one spreadsheet
    out.append("## Parts list\n\nEvery line of `data/vehicle/vehicle-parts.yaml`, AUD including GST, the line total. Basis is "
               "listing (read from a supplier or regulator page) or estimate. Priority: " +
               ", ".join(f"{p} {d[0].lower() + d[1:]}" for p, d in PRIORITIES.items()) + ". Status is required, contingency (only "
               "if an inspection or test calls for it) or optional. Select rows to total them in the footer, or sort and filter by "
               "stage, priority or status.\n\n"
               "| ID | Item | Part number | Supplier | AUD | Basis | Priority | Why | Stage | Depends on | Status | Note |\n"
               "|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for it in data["items"]:
        name = _cell(it["name"])
        if it.get("link"):
            name = f"[{name}]({it['link']})"
        out.append(f"| {it['id']} | {name} | {_cell(it.get('part_number'))} | {_cell(it.get('supplier'))} | "
                   f"{it['price_aud']:,.2f} | {it.get('price_basis', '')} | {it['priority']} | {_cell(it.get('why'))} | "
                   f"{it['stage']} | {', '.join(it.get('depends_on') or [])} | {it['status']} | {_cell(it.get('note'))} |\n")

    # ---------------------------------------------------------------- totals
    over = "Over" if T["gap"] > 0 else "Under"
    names = " and ".join(T["closing"]) if len(T["closing"]) < 3 else ", ".join(T["closing"][:-1]) + " and " + T["closing"][-1]
    listed = ", ".join(T["closing"])
    out.append("\n### Totals\n\n<div data-sheet=\"off\">\n\n| Total | AUD |\n|---|---|\n"
               f"| Required | {_aud(T['required'])} |\n| Contingency allowance | {_aud(T['allowance'])} |\n"
               f"| Required with the contingency allowance | {_aud(T['with_contingency'])} |\n"
               f"| Leonard's figure for the car build | {_aud(T['budget'])} |\n"
               f"| {over} that figure, with the allowance | {_aud(abs(T['gap']))} |\n"
               f"| Less {names} | -{_aud(T['closing_saving'])} |\n"
               f"| Required with {listed} and the allowance | {_aud(T['with_closing'])} |\n"
               f"| Less every cut | -{_aud(T['cuts'])} |\n| Required with every cut and the allowance | {_aud(T['with_cuts'])} |\n"
               f"| Contingency lines, if every one happened | {_aud(T['contingency_lines'])} |\n| Optional lines | {_aud(T['optional'])} |\n\n"
               "</div>\n\n"
               f"{names} close the gap to Leonard's AUD {_aud(T['budget'])}, each taken only if the old part passes its test (see the "
               "cuts below). The allowance is the plan's own figure (`VEHICLE.md`), not the sum of the contingency lines: those are "
               "bought only if a test calls for them, and a new DPF and a laboratory emissions test are outside it. The truck, the bike "
               "box, the trailer and Leonard's labour are outside these figures (see the cost table on the [home page](../)).\n\n")
    out.append("#### By priority\n\n| Priority | What it is for | Required AUD | Contingency lines AUD | Optional AUD |\n|---|---|---|---|---|\n")
    for p, d in PRIORITIES.items():
        out.append(f"| {p} | {d} | " + " | ".join(_cents(get("priority", p, s)) for s in STATUSES) + " |\n")
    out.append("\n#### By stage\n\n| Stage | Name | Required AUD | Contingency lines AUD | Optional AUD |\n|---|---|---|---|---|\n")
    for st in data["stages"]:
        out.append(f"| {st['id']} | {_cell(st['name'])} | " + " | ".join(_cents(get("stage", st["id"], s)) for s in STATUSES) + " |\n")
    out.append("\n#### By system\n\n| System | Required AUD | Contingency lines AUD | Optional AUD |\n|---|---|---|---|\n")
    for key in dict.fromkeys(it["system"] for it in data["items"]):
        out.append(f"| {SYSTEMS.get(key, key)} | " + " | ".join(_cents(get("system", key, s)) for s in STATUSES) + " |\n")
    out.append("\n### Cuts that keep it reliable\n\nEach cut applies only if the old part passes its test.\n\n"
               "| Cut | What | Replaces | Saves AUD | Risk |\n|---|---|---|---|---|\n")
    for c in data["cuts"]:
        out.append(f"| {c['id']} | {_cell(c['name'])} | {c['replaces']} | {c['saving_aud']:,.0f} | {_cell(c.get('risk'))} |\n")
    out.append("\n### Lines the merges removed\n\nNot counted anywhere.\n\n| Item | AUD | Why |\n|---|---|---|\n")
    for it in data.get("removed", []):
        out.append(f"| {_cell(it['name'])} | {it['price_aud']:,.2f} | {_cell(it['reason'])} |\n")
    out.append("\n")
    for name in VEHICLE_END:
        out.append(secs[name].replace("`vehicle-parts.yaml`", "the parts list above") + "\n")
    (DOCS / "tow-vehicle.md").write_text("".join(out), encoding="utf-8")
    return len(data["items"])


def box_parts() -> dict:
    """The bike box's parts list (data/ute/box-parts.yaml) for the site, with the totals worked out from the lines.
    cad/tests/test_box_parts.py checks that they equal the totals typed in the file."""
    data = yaml.safe_load((ROOT / "data" / "ute" / "box-parts.yaml").read_text(encoding="utf-8"))
    aud, kg = {}, {}
    for ln in data["lines"]:
        aud[ln["group"]] = aud.get(ln["group"], 0.0) + ln["price"]["aud"]
        kg[ln["group"]] = kg.get(ln["group"], 0.0) + ln["mass"]["kg"]
    pct = data["totals"]["contingency_pct"]
    sub = sum(aud.values())
    total = sub * (1 + pct / 100)
    data["totals"] = dict(data["totals"], by_group={g: round(aud[g], 2) for g in data["groups"] if g in aud},
                          kg_by_group={g: round(kg[g], 2) for g in data["groups"] if g in kg},
                          subtotal_aud=round(sub, 2), contingency_aud=round(sub * pct / 100, 2), total_aud=round(total, 2),
                          owner_built_total_aud=round(total - aud.get("fabrication", 0.0) * (1 + pct / 100), 2),
                          mass_kg_lines=round(sum(kg.values()), 2))
    (GEN / "box-parts.json").write_text(json.dumps(data, indent=1, default=str))
    return data


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
    # the part metadata beside each model, for the viewer's tooltip and part card (cad/partsmeta.py)
    for folder, names in (("trailer", ("trailer", "chassis", "body", "body-inside")), ("ute", ("ute", "ute-loading"))):
        for name in names:
            _copy(BUILD / folder / f"{name}.parts.json", SITE / "public" / "models" / f"{name}.parts.json")
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

    # the decision record, from docs/decisions.md, with its first heading moved into the title
    text = (ROOT / "docs" / "decisions.md").read_text(encoding="utf-8")
    text = re.sub(r"\A#\s+[^\n]*\n", "", text, count=1)
    (DOCS / "decisions.md").write_text("---\ntitle: 'Decisions for the LandCruiser 79 plan'\n---\n\n"
                                       "Copied from `docs/decisions.md` in the repository.\n" + text, encoding="utf-8")

    # the car build page (URL /tow-vehicle/) and the bike box's parts list
    n_parts = tow_vehicle_page()
    box = box_parts()

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
        archived = ("**Archived** (decision H9): this report is the record from before the LandCruiser 79 plan, kept as written "
                    "and not updated. Where it differs from the Car build, Bike box and Trailer pages, they are current.\n\n"
                    if order <= 11 else "")
        body = (f"---\ntitle: '{title}'\nsidebar:\n  order: {order}\n---\n\n" + archived +
                f"This is research report {fname[:2]}, copied unchanged from `research/{fname}` apart from its first heading.\n\n"
                + text)
        (DOCS / "research" / fname).write_text(body, encoding="utf-8")
    print(f"site data written: {len(RESEARCH)} research pages, {len(live)} live drawings "
          f"({len(reg['drawings']) - len(live)} retired), car build page with {n_parts} parts, box parts list with {len(box['lines'])} lines")


if __name__ == "__main__":
    main()

"""Copy build outputs into the site and generate the data-driven pages (research, car build, bike box parts).

Run inside the project image from the repo root:  python -m cad.sitedata
"""
from __future__ import annotations

import json
import re
import shutil
from itertools import combinations

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
    ("19-hvac-windows-doors.md", "HVAC, fresh air, windows, doors and the wet room shell", 19),
    ("20-electrical.md", "The trailer’s electrical system and energy model", 20),
    ("21-interior.md", "Lift bed, desk, kitchen, laundry, shower and water system", 21),
    ("22-trailer-prices.md", "Trailer prices outside the new interior", 22),
    ("25-roof.md", "Roof study, fixed roof against a raising roof", 25),
    ("26-elite-wheels.md", "What the Lovells Elite kit needs from the wheels, track and brakes", 26),
    ("27-car-build-scope.md", "The car build’s scope, the injectors, the driveline for level B and the trailer’s weld evidence", 27),
    ("31-ranger-super-duty.md", "The Ford Ranger Super Duty: ratings, price, power and the NSW path", 31),
    ("32-super-duty-power.md", "The Super Duty at about 250 kW: turbo, fuel, the 10-speed, heat, the certificate and the time to 100 km/h", 32),
]
# research reports 23 and 24 are the car build and bike box plans themselves, so the index points at their pages
RESEARCH_PLANS = [("23", "The tow vehicle plan", "`VEHICLE.md`, the Tow vehicle page", "../tow-vehicle/"),
                  ("24", "The bike box design", "`UTE-GARAGE.md`, the Bike box page", "../ute-garage/")]
# sections of VEHICLE.md shown on the Tow vehicle page, in order. The stage table, the three lists and every total are
# rendered from data/vehicle/vehicle-parts.yaml instead, so the page types no figure itself.
VEHICLE_TOP = ("Summary", "The truck against the LandCruiser plan", "Stage plan")
VEHICLE_END = ("Limits to build and drive to", "Legal path", "Decisions", "Open points and the assumption used")
SYSTEMS = {
    "purchase": "Purchase inspection", "touring": "Mirrors, radio, compressor and recovery", "power": "Turbo and intercooler",
    "protection": "Bar, winch, sliders and lights", "engine": "Engine rebuild, cooling and baseline tests", "fuel_system": "Fuel system", "intake_dpf": "Sealed airbox and DPF service",
    "turbo_exhaust": "Turbo, intercooler and exhaust", "tune_legal": "Tune, gauges and engine certificate",
    "clutch_gearbox": "Clutch and gearbox", "driveline": "Transfer case, tailshafts, diffs and hubs",
    "steering_suspension": "Steering and front suspension",
    "refresh": "Chassis, cab, electrical, fuel lines, air conditioning, fluids",
    "gvm": "GVM kit, GCM revision and certificate", "brakes": "Brakes", "wheels_tyres": "Wheels and tyres",
    "towing": "Towing and trailer charging", "freight_weighing": "Freight and weighing", "fuel_tank": "Long-range fuel tank",
    "bar_winch": "Bull bar and winch, only if the truck has none",
}
STATUSES = ("build", "check", "optional")
LISTS = {"build": "Build", "check": "Check list", "optional": "Optional"}
PRIORITIES = {"P1": "Legal, safe and able to tow, or protecting the truck", "P2": "The power stage",
              "P3": "Optional or comfort"}

# the sheet's footer sums every number column of the tables wrapped in these (site/src/scripts/sheet.ts)
SUMS_OPEN, SUMS_CLOSE = '<div data-sheet-sum="sum">\n\n', "\n</div>\n\n"


def _sums(table):
    return SUMS_OPEN + table + SUMS_CLOSE


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
    """Leonard's whole-project figures (data/project.yaml): the truck's price, the car build's budget, and where the
    bike box's and the trailer's prices come from."""
    return yaml.safe_load((ROOT / "data" / "project.yaml").read_text(encoding="utf-8"))


def car_totals(data, budget) -> dict:
    """Every total of the car build, worked out from its lines: by list (build, check, optional), priority, stage and
    system, the build's one allowance by its rule (allowance_pct of each build line by its price basis, decision H24),
    and the figures against Leonard's build budget, with the fewest cuts that close the gap (of those, the set that saves
    least, named in the list's order). A cut saves its line and that line's share of the allowance. The figures against
    the budget add up whole dollars, so the Totals table adds up as shown and matches VEHICLE.md."""
    sums = {}
    for it in data["items"]:
        for key in ((it["status"],), ("priority", it["priority"], it["status"]), ("stage", it["stage"], it["status"]),
                    ("system", it["system"], it["status"])):
            sums[key] = sums.get(key, 0.0) + it["price_aud"]
    pct = data["totals_aud"]["allowance_pct"]
    line = {it["id"]: it for it in data["items"]}
    build = round(sums.get(("build",), 0.0))
    allow = round(sum(it["price_aud"] * pct[it["price_basis"]] / 100 for it in data["items"] if it["status"] == "build"))
    saves = {c["id"]: c["saving_aud"] + line[c["replaces"]]["price_aud"] * pct[line[c["replaces"]]["price_basis"]] / 100
             for c in data["cuts"]}
    gap = build + allow - budget
    closing, saved = [], 0.0
    if gap > 0:
        closing, saved = [c["id"] for c in data["cuts"]], sum(saves.values())
        for n in range(1, len(data["cuts"]) + 1):
            fits = [s for s in combinations(data["cuts"], n) if sum(saves[c["id"]] for c in s) >= gap]
            if fits:
                best = min(fits, key=lambda s: sum(saves[c["id"]] for c in s))
                closing, saved = [c["id"] for c in best], sum(saves[c["id"]] for c in best)
                break
    saved, cuts = round(saved), round(sum(saves.values()))
    return dict(sums=sums, build=build, check=round(sums.get(("check",), 0.0)), optional=round(sums.get(("optional",), 0.0)),
                allowance=allow, allowance_pct=pct, with_contingency=build + allow, budget=budget, gap=gap, closing=closing,
                closing_saving=saved, with_closing=build + allow - saved, cuts=cuts, with_cuts=build + allow - cuts,
                cut_saves={k: round(v) for k, v in saves.items()},
                every_line=round(sum(sums.get((s,), 0.0) for s in STATUSES)))


def _names(ids):
    return " and ".join(ids) if len(ids) < 3 else ", ".join(ids[:-1]) + " and " + ids[-1]


def _car_lists(data, T):
    """The build, the purchase check list and the optional extras, one spreadsheet each."""
    pct = T["allowance_pct"]
    rows = {s: [it for it in data["items"] if it["status"] == s] for s in STATUSES}
    link = lambda it: f"[{_cell(it['name'])}]({it['link']})" if it.get("link") else _cell(it["name"])
    deps = lambda it: ", ".join(it.get("depends_on") or [])
    out = [f"### The build\n\nThe upgrades and what makes them legal and able to tow. Priced and counted, with one allowance of "
           f"{pct['listing']} % of listed prices and {pct['estimate']} % of estimates.\n\n" + SUMS_OPEN +
           "| ID | Item | Part number | Supplier | AUD | Basis | Priority | Why | Stage | Depends on | Note |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|\n"]
    for it in rows["build"]:
        out.append(f"| {it['id']} | {link(it)} | {_cell(it.get('part_number'))} | {_cell(it.get('supplier'))} | "
                   f"{it['price_aud']:,.2f} | {it['price_basis']} | {it['priority']} | {_cell(it['why'])} | {it['stage']} | "
                   f"{deps(it)} | {_cell(it.get('note'))} |\n")
    out.append(SUMS_CLOSE + "### Check list\n\nLines bought only if a check, a test or a certifier calls for them. Each is checked at "
               "the stage in the When column and bought only if it fails, in the stage shown. Not counted, and the check list carries "
               "no allowance.\n\n" + SUMS_OPEN +
               "| ID | Item | AUD if it fails | Basis | When | Check | Pass mark | Why | Fitted in | Note |\n"
               "|---|---|---|---|---|---|---|---|---|---|\n")
    for it in rows["check"]:
        out.append(f"| {it['id']} | {link(it)} | {it['price_aud']:,.2f} | {it['price_basis']} | {it['checked_at']} | "
                   f"{_cell(it['check'])} | {_cell(it.get('pass_mark'))} | {_cell(it['why'])} | {it['stage']} | {_cell(it.get('note'))} |\n")
    out.append(SUMS_CLOSE + f"If every line on the check list were bought, it would come to AUD {_aud(T['check'])}. That is a note, not a "
               "total: each line is an only-if step, priced as if it were needed.\n\n"
               "### Optional extras\n\nExtras the plan does not need. Not counted.\n\n" + SUMS_OPEN +
               "| ID | Item | Part number | Supplier | AUD | Basis | Why | Stage | Note |\n|---|---|---|---|---|---|---|---|---|\n")
    for it in rows["optional"]:
        out.append(f"| {it['id']} | {link(it)} | {_cell(it.get('part_number'))} | {_cell(it.get('supplier'))} | "
                   f"{it['price_aud']:,.2f} | {it['price_basis']} | {_cell(it['why'])} | {it['stage']} | {_cell(it.get('note'))} |\n")
    out.append(SUMS_CLOSE)
    return out


def _car_totals_table(data, T):
    over = "Over" if T["gap"] > 0 else "Under"
    every = len(T["closing"]) == len(data["cuts"])
    closing_rows = "" if every or not T["closing"] else (
        f"| Less {_names(T['closing'])}, with {'its' if len(T['closing']) == 1 else 'their'} share of the allowance | "
        f"-{_aud(T['closing_saving'])} |\n"
        f"| The build with {', '.join(T['closing'])} and the allowance | {_aud(T['with_closing'])} |\n")
    pct = T["allowance_pct"]
    out = ["\n### Totals\n\n<div data-sheet-sum=\"off\">\n\n| Total | AUD |\n|---|---|\n"
           f"| The build | {_aud(T['build'])} |\n"
           f"| Allowance, {pct['listing']} % of listed prices and {pct['estimate']} % of estimates | {_aud(T['allowance'])} |\n"
           f"| The build with its allowance | {_aud(T['with_contingency'])} |\n"
           f"| Leonard's figure for the car build | {_aud(T['budget'])} |\n"
           f"| {over} that figure, with the allowance | {_aud(abs(T['gap']))} |\n" + closing_rows +
           f"| Less every cut, with its share of the allowance | -{_aud(T['cuts'])} |\n"
           f"| The build with every cut and the allowance | {_aud(T['with_cuts'])} |\n"
           f"| Check list, if every line were bought (not counted) | {_aud(T['check'])} |\n"
           f"| Optional extras (not counted) | {_aud(T['optional'])} |\n\n</div>\n\n"]
    if T["gap"] > 0:
        one = len(T["closing"]) == 1
        out.append(("Only every cut together closes" if every else f"{_names(T['closing'])} closes" if one
                    else f"{_names(T['closing'])} close") + f" the gap to Leonard's AUD {_aud(T['budget'])}, "
                   + ("taken only if its condition holds" if one else "each taken only if its condition holds")
                   + " (see the cuts below). ")
    else:
        out.append(f"The build with its allowance is under Leonard's AUD {_aud(T['budget'])}, so it needs no cut. ")
    out.append("The truck's purchase, the bike box, the trailer and Leonard's labour are outside these figures (see the cost table on "
               "the [home page](../)).\n\n")
    return out


def tow_vehicle_page():
    """The Tow vehicle page: VEHICLE.md's summary, its comparison with the LandCruiser plan and its stage plan with the
    stage table, then the build, the check list and the optional extras as three spreadsheets with the totals, all from
    data/vehicle/vehicle-parts.yaml, then VEHICLE.md's limits, legal path, decisions and open points. The URL stays
    /tow-vehicle/ so earlier links still work."""
    plan = (ROOT / "VEHICLE.md").read_text(encoding="utf-8")
    data = yaml.safe_load((ROOT / "data" / "vehicle" / "vehicle-parts.yaml").read_text(encoding="utf-8"))
    T = car_totals(data, project()["car_build"]["budget_aud"])
    data["computed"] = {k: v for k, v in T.items() if k != "sums"}
    (GEN / "vehicle.json").write_text(json.dumps(data, indent=1, default=str))
    S = T["sums"]
    get = lambda *k: S.get(k, 0.0)
    out = ["---\ntitle: Tow vehicle\ndescription: 'The Ford Ranger Super Duty single cab chassis that tows the trailer: the purchase, "
           "the stages, every line with its price, reason and stage, the totals against the LandCruiser plan it replaces, the "
           "limits, the power stage and its legal path.'\n---\n\n",
           "The tow vehicle is a near-new Ford Ranger Super Duty single cab chassis, bought rather than rebuilt, with both "
           "motorbikes in the [bike box](../ute-garage/) on its chassis. It replaced the LandCruiser VDJ79 build on 22 Nov 2026 "
           "(research report 31). The plan is `VEHICLE.md`, and every part and paid job is a line in "
           "`data/vehicle/vehicle-parts.yaml` on one of three lists: the build, which is priced and counted, the check list of lines "
           "bought only if a check calls for them, and the optional extras. The 3D model of the truck with its box is on the "
           "[Bike box](../ute-garage/#3d-model) page and the general arrangement is drawing [CT-701](../drawings/#ct-701).\n\n"]
    secs = dict(zip(VEHICLE_TOP + VEHICLE_END, _sections(plan, VEHICLE_TOP + VEHICLE_END)))
    out.append(secs["Summary"] + "\n")
    out.append(secs["The truck against the LandCruiser plan"] + "\n")
    rows = ("| Stage | Work | Build AUD | Check list AUD | Optional AUD | Paid labour | Downtime (est.) | "
            "The truck can then |\n|---|---|---|---|---|---|---|---|\n")
    for st in data["stages"]:
        rows += (f"| {st['id']} | {_cell(st.get('work'))} | " +
                 " | ".join(_cents(get("stage", st["id"], s)) for s in STATUSES) +
                 f" | {_cell(st.get('labour'))} | {_cell(st.get('downtime'))} | {_cell(st['can_do'])} |\n")
    head, rest = secs["Stage plan"].split("\n", 1)
    out.append(head + "\n\nEach stage's lines added up by list, from the YAML. The sheet's footer gives the totals.\n\n" + _sums(rows) +
               _drop_first_table(rest) + "\n")
    out.append("## Parts list\n\nEvery line of `data/vehicle/vehicle-parts.yaml`, AUD including GST, the line total, sorted into three "
               "lists by research report 31. Basis is listing (read from a supplier or regulator page) or estimate. "
               "Priority: " + ", ".join(f"{p} {d[0].lower() + d[1:]}" for p, d in PRIORITIES.items()) + ". Select rows to total them "
               "in the footer, or sort and filter by stage or priority.\n\n")
    out += _car_lists(data, T)
    out += _car_totals_table(data, T)
    heads = " | ".join(f"{LISTS[s]} AUD" for s in STATUSES)
    out.append("#### By priority\n\n" + SUMS_OPEN + f"| Priority | What it is for | {heads} |\n|---|---|---|---|---|\n")
    for p, d in PRIORITIES.items():
        out.append(f"| {p} | {d} | " + " | ".join(_cents(get("priority", p, s)) for s in STATUSES) + " |\n")
    out.append(SUMS_CLOSE + "#### By stage\n\n" + SUMS_OPEN + f"| Stage | Name | {heads} |\n|---|---|---|---|---|\n")
    for st in data["stages"]:
        out.append(f"| {st['id']} | {_cell(st['name'])} | " + " | ".join(_cents(get("stage", st["id"], s)) for s in STATUSES) + " |\n")
    out.append(SUMS_CLOSE + "#### By system\n\n" + SUMS_OPEN + f"| System | {heads} |\n|---|---|---|---|\n")
    for key in dict.fromkeys(it["system"] for it in data["items"]):
        out.append(f"| {SYSTEMS.get(key, key)} | " + " | ".join(_cents(get("system", key, s)) for s in STATUSES) + " |\n")
    out.append(SUMS_CLOSE + "### Cuts\n\nEach cut applies only if its condition holds, and it saves its line with that line's share of "
               "the allowance.\n\n" + SUMS_OPEN + "| Cut | What | Replaces | Saves AUD | With its allowance AUD | Risk |\n"
               "|---|---|---|---|---|---|\n")
    for c in data["cuts"]:
        out.append(f"| {c['id']} | {_cell(c['name'])} | {c['replaces']} | {c['saving_aud']:,.0f} | {T['cut_saves'][c['id']]:,.0f} | "
                   f"{_cell(c.get('risk'))} |\n")
    out.append(SUMS_CLOSE + "### Lines left out\n\nNot counted in any total.\n\n" + SUMS_OPEN + "| Item | AUD | Why |\n|---|---|---|\n")
    for it in data.get("removed", []):
        out.append(f"| {_cell(it['name'])} | {it['price_aud']:,.2f} | {_cell(it['reason'])} |\n")
    out.append(SUMS_CLOSE)
    for name in VEHICLE_END:
        out.append(secs[name].replace("`vehicle-parts.yaml`", "the parts list above") + "\n")
    (DOCS / "tow-vehicle.md").write_text("".join(out), encoding="utf-8")
    return len(data["items"])


def box_parts() -> dict:
    """The bike box's parts list (data/ute/box-parts.yaml) for the site, with the totals worked out from the lines.
    Leonard builds the box, so it has one total (decision H25). cad/tests/test_box_parts.py checks that they equal the
    totals typed in the file."""
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
                          mass_kg_lines=round(sum(kg.values()), 2))
    (GEN / "box-parts.json").write_text(json.dumps(data, indent=1, default=str))
    return data


def trailer_parts() -> dict:
    """The trailer's priced parts list (cad/trailer_costs.py) for the site, with each line's tare mass from the built
    mass schedule: its own blocks, or the blocks a stock line covers."""
    from .trailer_costs import parts_list, savings
    lst = parts_list()
    lst["savings"] = savings(lst)
    kg: dict[str, float] = {}
    for s in json.loads((BUILD / "trailer" / "trailer.json").read_text())["schedule"]:
        if s["load"] == "tare":
            kg[s["id"]] = kg.get(s["id"], 0.0) + s["mass_kg"]
    for ln in lst["lines"]:
        ids = ln.get("covers") or ([ln["id"]] if ln["id"] in kg else [])
        ln["mass_kg"] = round(sum(kg.get(i, 0.0) for i in ids), 2) if ids else None
    (GEN / "trailer-parts.json").write_text(json.dumps(lst, indent=1, default=str))
    return lst


def _priced_list(path) -> dict:
    """A parts list named in data/project.yaml. A list with `sources` (the trailer's) is put together from its source
    files by cad/trailer_costs.py, the others are read as they are."""
    lst = yaml.safe_load(path.read_text(encoding="utf-8"))
    if lst.get("sources"):
        from .trailer_costs import parts_list
        return parts_list(path)
    return lst


def project_costs(box_totals, proj=None) -> dict:
    """The whole project's cost for the home page (ProjectCost.astro): the truck, the car build, the bike box and the
    trailer, each with its figure before contingency, its contingency, its total and its parts list. From
    data/project.yaml (or proj), the car build's lines (car_totals) and the bike box's totals. The trailer is pending
    until data/project.yaml names its priced parts list, in the bike box list's format (lines with price.aud, and
    totals with contingency_pct, or contingency_aud when the list works it out): then its row is worked out from that
    list's lines. Leonard builds the box and the trailer himself, so each part has one total (decisions H25 and H26).
    The total leaves out what is pending."""
    p = proj or project()
    car = car_totals(yaml.safe_load((ROOT / "data" / "vehicle" / "vehicle-parts.yaml").read_text(encoding="utf-8")),
                     p["car_build"]["budget_aud"])
    bt = box_totals
    rows = [
        dict(id="truck", part="Truck purchase (Ranger Super Duty)", basis=p["truck"]["basis"], before=p["truck"]["purchase_aud"],
             contingency=0, total=p["truck"]["purchase_aud"], link="/tow-vehicle/#s0-buy-inspect-and-weigh",
             link_text="Stage S0, buy, inspect and weigh"),
        dict(id="car", part="Truck upgrades", basis="The build list with its allowance (research report 31)",
             before=car["build"], contingency=car["allowance"], total=car["with_contingency"], link="/tow-vehicle/#the-build",
             link_text="Upgrade list"),
        dict(id="box", part="Bike box", basis=p["bike_box"]["basis"], before=bt["subtotal_aud"], contingency=bt["contingency_aud"],
             total=bt["total_aud"], contingency_pct=bt["contingency_pct"],
             link="/ute-garage/#parts-list", link_text="Bike box parts list"),
    ]
    tr = p["trailer"]
    if tr.get("parts_list"):
        lst = _priced_list(ROOT / tr["parts_list"])
        sub = sum(ln["price"]["aud"] for ln in lst["lines"])
        lt = lst["totals"]
        pct = lt["contingency_pct"]
        cont = lt["contingency_aud"] if "contingency_aud" in lt else sub * pct / 100
        rows.append(dict(id="trailer", part="Trailer", basis=tr["basis"], before=sub, contingency=cont, total=sub + cont,
                         contingency_pct=pct, link=tr["link"], link_text="Trailer parts list"))
    else:
        rows.append(dict(id="trailer", part="Trailer", basis=tr["basis"], pending=True, link=tr["link"],
                         link_text="Mass schedule, no prices yet"))
    known = [r for r in rows if not r.get("pending")]
    return dict(rows=rows, pending=[r["part"] for r in rows if r.get("pending")],
                before=sum(r["before"] for r in known), contingency=sum(r["contingency"] for r in known),
                total=sum(r["total"] for r in known),
                car=dict(budget=car["budget"], gap=car["gap"], closing=car["closing"], with_closing=car["with_closing"],
                         allowance_pct=car["allowance_pct"], check=car["check"], optional=car["optional"]))


RESEARCH_STATUS = {
    12: "Record. The body's design basis, behind `BODY.md`",
    13: "Record. The appliances and equipment, partly replaced by reports 19 to 21",
    14: "Record. The LandCruiser engine plan, replaced by report 31",
    15: "Record. The LandCruiser driveline plan, replaced by report 31",
    16: "Record. The LandCruiser's limits, replaced by report 31",
    17: "Record. The bike box study behind `UTE-GARAGE.md`",
    18: "Record. The trailer's layout study before the home trailer",
    19: "Record, 20 Nov 2026. HVAC, fresh air, windows, doors and the wet room shell, for decisions H4, H7 and H8",
    20: "Record, 20 Nov 2026. The 48 V system, which passes decision H3",
    21: "Record, 20 Nov 2026. The bed, desk, kitchen, laundry, shower and water system, for decisions H1, H1a, H4a, H5 and H6",
    22: "Record, 20 Nov 2026. The prices of the lines the interior left unchanged, the labour and the NSW compliance",
    25: "Record, 20 Nov 2026. The fixed roof with rounded front edges, decision H12",
    26: "Record, 21 Nov 2026. The Elite kit's wheels, rear track and brakes, decisions H18 and H19",
    27: "Record, 22 Nov 2026. The car build's three lists, the injectors, the gearbox and the trailer's weld evidence, decisions H24 and H26",
    31: "Current, 23 Nov 2026. The Ranger Super Duty behind `VEHICLE.md`, which replaced the LandCruiser plan of reports 14 to 16, 26 and 27",
    32: "Current, 24 Nov 2026. The power stage at about 250 kW and the time to 100 km/h towing, for stage S3 of `VEHICLE.md`",
}


def research_index():
    """The research index page: every report with its status, and reports 23 and 24, which are the car build and
    bike box plans in the repository."""
    rows = [(fname[:2], f"[{title}](./{fname[:-3]}/)", "Archived (decision H9)" if order <= 11 else RESEARCH_STATUS[order])
            for fname, title, order in RESEARCH]
    rows += [(n, f"[{title}]({url})", f"In the repository as {where}") for n, title, where, url in RESEARCH_PLANS]
    rows.sort(key=lambda r: r[0])
    out = ["---\ntitle: Research index\nsidebar:\n  order: 0\n---\n\n",
           "The research behind the design, one report per question, with its sources. Reports 01 to 11 are the record "
           "of the Porsche Cayenne plan and the trailer with its own garage, kept as written. Reports 23 and 24 are the car "
           "build plan and the bike box design, `VEHICLE.md` and `UTE-GARAGE.md`. Each report's data files and models are in "
           "`research/` in the repository.\n\n",
           "| Report | Title | Status |\n|---|---|---|\n"]
    out += [f"| {n} | {title} | {status} |\n" for n, title, status in rows]
    (DOCS / "research" / "index.md").write_text("".join(out), encoding="utf-8")


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
    _copy(BUILD / "trailer" / "body-inside-night.viewer.json", SITE / "public" / "models" / "body-inside-night.json")
    _copy(BUILD / "trailer" / "body.step", SITE / "public" / "downloads" / "body.step")
    _copy(BUILD / "body" / "body.json", GEN / "body.json")
    _copy(BUILD / "ute" / "ute.json", GEN / "ute.json")
    _copy(BUILD / "ute" / "ute.viewer.json", SITE / "public" / "models" / "ute.json")
    _copy(BUILD / "ute" / "ute-loading.viewer.json", SITE / "public" / "models" / "ute-loading.json")
    _copy(BUILD / "ute" / "ute.step", SITE / "public" / "downloads" / "ute.step")
    _copy(BUILD / "chassis" / "chassis.json", GEN / "chassis.json")
    _copy(BUILD / "chassis" / "chassis-cut-list.csv", SITE / "public" / "downloads" / "chassis-cut-list.csv")
    # the floor plan for the trailer page, and its cut height and models for the viewer's plan view (cad/floorplan.py)
    for state in ("day", "night"):
        _copy(BUILD / "floorplan" / f"floorplan-{state}.svg", GEN / f"floorplan-{state}.svg")
    fp = json.loads((BUILD / "floorplan" / "floorplan.json").read_text())
    fp["plans"] = {k: dict(title=v["title"], dims=v["dims"]) for k, v in fp["plans"].items()}
    (GEN / "floorplan.json").write_text(json.dumps(fp, indent=1))
    # the part metadata beside each model, for the viewer's tooltip and part card (cad/partsmeta.py)
    for folder, names in (("trailer", ("trailer", "chassis", "body", "body-inside", "body-inside-night")), ("ute", ("ute", "ute-loading"))):
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
    (DOCS / "decisions.md").write_text("---\ntitle: 'Decisions'\n---\n\n"
                                       "Copied from `docs/decisions.md` in the repository.\n" + text, encoding="utf-8")

    # the tow vehicle page (URL /tow-vehicle/) and the bike box's parts list
    n_parts = tow_vehicle_page()
    box = box_parts()
    # the trailer's priced parts list, the services' budgets, and the whole project's cost on the home page
    trailer = trailer_parts()
    from .services import services
    (GEN / "services.json").write_text(json.dumps(services(), indent=1, default=str))
    (GEN / "project.json").write_text(json.dumps(project_costs(box["totals"]), indent=1))

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
        archived = ("Archived (decision H9): the record from before the LandCruiser 79 plan, kept as written. Where it differs "
                    "from the Car build, Bike box and Trailer pages, those pages are current.\n\n" if order <= 11 else "")
        body = (f"---\ntitle: '{title}'\nsidebar:\n  order: {order}\n---\n\n" + archived +
                f"Research report {fname[:2]}, copied from `research/{fname}` apart from its first heading.\n\n"
                + text)
        (DOCS / "research" / fname).write_text(body, encoding="utf-8")
    research_index()
    print(f"site data written: {len(RESEARCH)} research pages, {len(live)} live drawings "
          f"({len(reg['drawings']) - len(live)} retired), tow vehicle page with {n_parts} parts, box parts list with {len(box['lines'])} lines, "
          f"trailer parts list with {len(trailer['lines'])} lines")


if __name__ == "__main__":
    main()

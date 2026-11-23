"""The Ranger Super Duty's parts list (data/vehicle/vehicle-parts.yaml, research report 31): its lines are consistent and
sorted into the build, the check list and the optional extras, the totals typed in the file add up from the lines, the
Car build page's figures are the same, and VEHICLE.md quotes them, with the purchase and the upgrades set against the
LandCruiser plan they replace. The truck's price and the build budget come from data/project.yaml, the bike box's total
from data/ute/box-parts.yaml (test_box_parts.py) and the trailer's from its parts list (test_trailer_parts.py)."""
import re
from collections import defaultdict

import yaml

from cad.partsdb import DATA, ROOT
from cad.sitedata import car_totals, project_costs
from cad.trailer_costs import parts_list

CAR = yaml.safe_load((DATA / "vehicle" / "vehicle-parts.yaml").read_text())
PROJECT = yaml.safe_load((DATA / "project.yaml").read_text())
BOX = yaml.safe_load((DATA / "ute" / "box-parts.yaml").read_text())["totals"]
TRAILER = parts_list()["totals"]
PLAN = (ROOT / "VEHICLE.md").read_text()
ITEMS = CAR["items"]
TYPED = CAR["totals_aud"]
STAGES = [st["id"] for st in CAR["stages"]]
STATUSES = ("build", "check", "optional")
LANDCRUISER = {"truck": 50000, "build": 77777}  # the plan the Super Duty replaces (VEHICLE.md to 22 Nov 2026)
CHECK_FIELDS = ("check", "pass_mark", "checked_at")


def _sum(**match):
    return sum(it["price_aud"] for it in ITEMS if all(it[k] == v for k, v in match.items()))


def _aud(v):
    return f"{round(v):,}"


def _section(name):
    return re.split(r"(?m)^## ", PLAN.split(f"\n## {name}\n", 1)[1], maxsplit=1)[0]


def _rows(text):
    """The body rows of the first Markdown table in text, as lists of cell strings."""
    rows = []
    for ln in text.split("\n"):
        if ln.startswith("|"):
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif rows:
            break
    return rows[2:]


def _num(cell):
    return float(cell.replace(",", ""))


def test_lines_are_consistent():
    ids = [it["id"] for it in ITEMS]
    assert len(ids) == len(set(ids)), f"repeated ids: {sorted(i for i in ids if ids.count(i) > 1)}"
    for it in ITEMS:
        assert it["status"] in STATUSES, it["id"]
        assert it["priority"] in ("P1", "P2", "P3"), it["id"]
        assert it["stage"] in STAGES, it["id"]
        assert it["price_basis"] in ("listing", "estimate"), it["id"]
        assert it.get("why") and "\n" not in it["why"], f"{it['id']} gives no one-line reason"
        if "qty" in it:
            assert abs(it["qty"] * it["unit_aud"] - it["price_aud"]) < 0.01, it["id"]
        for dep in it.get("depends_on") or []:
            assert dep in ids or dep in STAGES, f"{it['id']} depends on unknown {dep}"
            assert dep != it["id"], f"{it['id']} depends on itself"


def test_check_lines_say_what_to_check():
    """Every check line says what to look at, when, and the pass mark, and only check lines carry those fields."""
    for it in ITEMS:
        if it["status"] == "check":
            assert it.get("check") and it.get("pass_mark"), f"{it['id']} gives no check or pass mark"
            assert it["checked_at"] in STAGES, f"{it['id']} checked at {it.get('checked_at')!r}"
        else:
            assert not set(CHECK_FIELDS) & set(it), f"{it['id']} is not a check line but has check fields"


def test_the_build_holds_what_the_truck_needs():
    """The Super Duty comes with Ford's 4,500 kg GVM, 8,000 kg GCM, 4.5 t tow bar and hitch, trailer brake controller and
    12-pin socket, so the build is the purchase inspection, the coupling's tow pin, the supply for the trailer's TSC, the trailer charging, the mirrors,
    radio, compressor and recovery kit, and the power stage with its certificate. Lines that wait on a check are on the
    check list, the bar, winch, sliders and lights are optional, and nothing of the LandCruiser build is left."""
    status = {it["id"]: it["status"] for it in ITEMS}
    for i in ("BI01", "TW01", "TW07", "TC01", "TW06", "TM01", "UH01", "AC01", "RK01", "PW01", "PW02", "TL01", "TL04", "TL05"):
        assert status[i] == "build", f"{i} is {status[i]}"
    for i in ("TW02", "TC02", "TL07", "TX01", "BF01"):
        assert status[i] == "check", f"{i} is {status[i]}"
    for i in ("OP01", "OP02", "OP03"):
        assert status[i] == "optional", f"{i} is {status[i]}"
    for i in ("EN01", "CG01", "GV05", "GV06", "WT01", "TW08", "TX04"):
        assert i not in status, f"{i} is a LandCruiser line"
    assert not any("70 mm ball" in it["name"] for it in ITEMS), "the coupling's tow pin takes the place of a ball"


def test_super_duty_against_the_landcruiser():
    """The purchase and the upgrades with their allowance, shown apart in VEHICLE.md and set against the LandCruiser plan
    they replace: AUD 50,000 for that truck and AUD 77,777 for its build with the allowance."""
    truck, car = PROJECT["truck"]["purchase_aud"], TYPED["build_plus_contingency"]
    assert (truck, car) == (92690, 20289), "the purchase and the upgrades changed: update this test and VEHICLE.md"
    rows = {r[0]: r for r in _rows(_section("The truck against the LandCruiser plan"))}
    want = {"Truck": (truck, LANDCRUISER["truck"]), "Upgrades with the allowance": (car, LANDCRUISER["build"]),
            "Together": (truck + car, LANDCRUISER["truck"] + LANDCRUISER["build"])}
    for name, (sd, lc) in want.items():
        assert name in rows, f"VEHICLE.md's comparison has no {name!r} row"
        got = [_num(c) for c in rows[name][1:4]]
        assert got == [sd, lc, sd - lc], f"VEHICLE.md's {name!r} row is {got}, the data give {[sd, lc, sd - lc]}"


def test_cut_savings_are_the_replaced_line_less_the_job():
    price = {it["id"]: it["price_aud"] for it in ITEMS}
    for c in CAR["cuts"]:
        assert c["replaces"] in price, f"{c['id']} replaces unknown {c['replaces']}"
        job = (c.get("job") or {}).get("price_aud", 0)
        assert abs(price[c["replaces"]] - job - c["saving_aud"]) < 0.01, c["id"]


def test_typed_totals_add_up_from_the_lines():
    pct = TYPED["allowance_pct"]
    build = _sum(status="build")
    allow = sum(it["price_aud"] * pct[it["price_basis"]] / 100 for it in ITEMS if it["status"] == "build")
    line = {it["id"]: it for it in ITEMS}
    cuts = sum(c["saving_aud"] + line[c["replaces"]]["price_aud"] * pct[line[c["replaces"]]["price_basis"]] / 100 for c in CAR["cuts"])
    checks = {
        "build": build, "build_listed": _sum(status="build", price_basis="listing"),
        "build_estimated": _sum(status="build", price_basis="estimate"), "contingency_allowance": allow,
        "build_plus_contingency": round(build) + TYPED["contingency_allowance"], "cuts_with_allowance": cuts,
        "build_with_cuts_plus_contingency": round(build) + TYPED["contingency_allowance"] - TYPED["cuts_with_allowance"],
        "check_if_every_item_failed": _sum(status="check"), "optional": _sum(status="optional"),
        "every_line": sum(it["price_aud"] for it in ITEMS),
    }
    for key, v in checks.items():
        assert abs(TYPED[key] - v) <= 1, f"totals_aud.{key} is {TYPED[key]}, the lines give {v:,.2f}"
    for status, key in (("build", "build_by_system"), ("check", "check_by_system"), ("optional", "optional_by_system")):
        lines = defaultdict(float)
        for it in ITEMS:
            if it["status"] == status:
                lines[it["system"]] += it["price_aud"]
        assert set(TYPED[key]) == set(lines), f"{key}: systems differ"
        for sysid, v in lines.items():
            assert abs(TYPED[key][sysid] - v) <= 1, f"{key}.{sysid} is {TYPED[key][sysid]}, the lines give {v:,.2f}"
    for group, field, ids in (("by_priority", "priority", ("P1", "P2", "P3")), ("by_stage", "stage", STAGES)):
        assert list(TYPED[group]) == list(ids), group
        for i in ids:
            for s in STATUSES:
                v = _sum(**{field: i, "status": s})
                assert abs(TYPED[group][i][s] - v) <= 1, f"{group}.{i}.{s} is {TYPED[group][i][s]}, the lines give {v:,.2f}"


def test_budget_figures():
    budget = PROJECT["car_build"]["budget_aud"]
    assert TYPED["build_budget"] == budget
    ab = TYPED["against_budget"]
    assert ab["build"] == TYPED["build"] - budget
    assert ab["build_plus_contingency"] == TYPED["build_plus_contingency"] - budget
    assert ab["build_with_cuts_plus_contingency"] == TYPED["build_with_cuts_plus_contingency"] - budget


def test_page_figures_are_the_typed_totals():
    T = car_totals(CAR, PROJECT["car_build"]["budget_aud"])
    assert T["build"] == TYPED["build"] and T["allowance"] == TYPED["contingency_allowance"]
    assert T["with_contingency"] == TYPED["build_plus_contingency"]
    assert T["with_cuts"] == TYPED["build_with_cuts_plus_contingency"]
    assert T["cuts"] == TYPED["cuts_with_allowance"]
    assert T["check"] == TYPED["check_if_every_item_failed"] and T["optional"] == TYPED["optional"]
    assert T["gap"] == TYPED["against_budget"]["build_plus_contingency"]
    if T["gap"] > 0:
        assert T["closing_saving"] >= T["gap"] and T["with_closing"] <= T["budget"], "the named cuts do not close the gap"


def test_vehicle_md_quotes_the_totals():
    t = TYPED
    for v in (t["build"], t["build_plus_contingency"], t["build_with_cuts_plus_contingency"], t["contingency_allowance"],
              t["build_budget"], abs(t["against_budget"]["build_plus_contingency"]), t["cuts_with_allowance"],
              t["check_if_every_item_failed"], t["optional"], PROJECT["truck"]["purchase_aud"], BOX["total_aud"]):
        assert any(f in PLAN for f in (f"AUD {_aud(v)}", f"| {_aud(v)} |", f"| -{_aud(v)} |")), f"VEHICLE.md does not quote {_aud(v)}"
    bp = t["by_priority"]
    for v in (bp["P1"]["build"], bp["P2"]["build"], t["optional"]):
        assert f"AUD {_aud(v)}" in PLAN, f"VEHICLE.md does not quote the total {_aud(v)}"
    for word in ("placeholder", "pending R20", "30,000", "required work", "Contingency lines", "VDJ79 single cab built"):
        assert word not in PLAN, f"VEHICLE.md still has {word!r}"
    assert "Ranger Super Duty" in PLAN.split("\n", 1)[0], "VEHICLE.md's title names the truck"


def test_vehicle_md_stage_table():
    rows = {r[0]: r for r in _rows(_section("Stage plan"))}
    for st in STAGES:
        for col, status in ((2, "build"), (3, "check")):
            v = _sum(stage=st, status=status)
            assert abs(_num(rows[st][col]) - v) <= 1, f"VEHICLE.md stage {st} {status}: {rows[st][col]}, the lines give {v:,.2f}"
    assert abs(_num(rows["Total"][2]) - TYPED["build"]) <= 1
    assert abs(_num(rows["Total"][3]) - TYPED["check_if_every_item_failed"]) <= 1


def test_vehicle_md_system_table():
    """Each row of VEHICLE.md's table by system is one system's build, check list and optional sums."""
    left = []
    for sysid in dict.fromkeys(it["system"] for it in ITEMS):
        left.append(tuple(_sum(system=sysid, status=s) for s in STATUSES))
    rows = [r for r in _rows(_section("Parts list by system")) if r[0] != "Total"]
    assert len(rows) == len(left), "VEHICLE.md lists a different number of systems"
    for r in rows:
        got = tuple(_num(c) for c in r[1:4])
        hit = next((x for x in left if all(abs(a - b) <= 1 for a, b in zip(got, x))), None)
        assert hit, f"VEHICLE.md row {r[0]!r} {got} matches no system's sums"
        left.remove(hit)


def test_project_cost_table():
    """The home page's table: the truck, the car build with its allowance, and the box and the trailer, which Leonard
    builds, each with one total. The trailer's row is its parts list's totals (test_trailer_parts.py)."""
    t = project_costs(BOX)
    rows = {r["id"]: r for r in t["rows"]}
    assert [r["id"] for r in t["rows"]] == ["truck", "car", "box", "trailer"]
    assert rows["truck"]["total"] == PROJECT["truck"]["purchase_aud"]
    assert rows["car"]["total"] == TYPED["build_plus_contingency"]
    assert rows["car"]["before"] + rows["car"]["contingency"] == rows["car"]["total"]
    assert abs(rows["box"]["before"] + rows["box"]["contingency"] - rows["box"]["total"]) < 0.01
    assert rows["box"]["total"] == BOX["total_aud"] and "owner_built" not in rows["box"]
    tr = rows["trailer"]
    assert not tr.get("pending") and t["pending"] == []
    assert abs(tr["total"] - TRAILER["total_aud"]) < 0.01 and "owner_built" not in tr
    known = PROJECT["truck"]["purchase_aud"] + TYPED["build_plus_contingency"] + BOX["total_aud"] + TRAILER["total_aud"]
    assert abs(t["total"] - known) < 0.01
    assert "total_owner_built" not in t, "the box and the trailer are owner-built, so the project has one total"
    assert abs(t["before"] + t["contingency"] - t["total"]) < 0.01


def test_project_cost_table_prices_the_trailer_from_its_list(tmp_path):
    """Once data/project.yaml names a priced trailer list, its row and the total work themselves out from its lines."""
    lst = tmp_path / "trailer-parts.yaml"
    lst.write_text(yaml.safe_dump({"totals": {"contingency_pct": 10},
                                   "lines": [{"id": "T1", "price": {"aud": 1000.0}}, {"id": "T2", "price": {"aud": 500.0}}]}))
    proj = dict(PROJECT, trailer=dict(PROJECT["trailer"], parts_list=str(lst), link="/trailer/#parts-list"))
    t = project_costs(BOX, proj)
    tr = t["rows"][-1]
    assert tr["id"] == "trailer" and not tr.get("pending") and t["pending"] == []
    assert abs(tr["before"] - 1500) < 0.01 and abs(tr["contingency"] - 150) < 0.01 and abs(tr["total"] - 1650) < 0.01
    others = PROJECT["truck"]["purchase_aud"] + TYPED["build_plus_contingency"] + BOX["total_aud"]
    assert abs(t["total"] - others - 1650) < 0.01

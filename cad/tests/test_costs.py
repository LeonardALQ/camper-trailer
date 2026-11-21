"""The car build's parts list (data/vehicle/vehicle-parts.yaml): its lines are consistent, the totals typed in the file
add up from the lines, the Car build page's figures are the same, and VEHICLE.md quotes them. The truck's price and the
build budget come from data/project.yaml, the bike box's totals from data/ute/box-parts.yaml (test_box_parts.py) and
the trailer's from its parts list (test_trailer_parts.py)."""
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
STATUSES = ("required", "contingency", "optional")


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
        assert it.get("why"), f"{it['id']} gives no reason"
        for dep in it.get("depends_on") or []:
            assert dep in ids or dep in STAGES, f"{it['id']} depends on unknown {dep}"
            assert dep != it["id"], f"{it['id']} depends on itself"


def test_cut_savings_are_the_replaced_line_less_the_job():
    price = {it["id"]: it["price_aud"] for it in ITEMS}
    for c in CAR["cuts"]:
        assert c["replaces"] in price, f"{c['id']} replaces unknown {c['replaces']}"
        job = (c.get("job") or {}).get("price_aud", 0)
        assert abs(price[c["replaces"]] - job - c["saving_aud"]) < 0.01, c["id"]


def test_typed_totals_add_up_from_the_lines():
    req = _sum(status="required")
    checks = {
        "required": req, "required_listed": _sum(status="required", price_basis="listing"),
        "required_estimated": _sum(status="required", price_basis="estimate"),
        "contingency_lines_if_all_happen": _sum(status="contingency"), "optional": _sum(status="optional"),
        "cuts": sum(c["saving_aud"] for c in CAR["cuts"]),
        "required_plus_contingency": req + TYPED["contingency_allowance"],
        "required_with_cuts": req - sum(c["saving_aud"] for c in CAR["cuts"]),
        "required_with_cuts_plus_contingency": req - sum(c["saving_aud"] for c in CAR["cuts"]) + TYPED["contingency_allowance"],
    }
    for key, v in checks.items():
        assert abs(TYPED[key] - v) <= 1, f"totals_aud.{key} is {TYPED[key]}, the lines give {v:,.2f}"
    for status, key in (("required", "required_by_system"), ("contingency", "contingency_lines_by_system"),
                        ("optional", "optional_by_system")):
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
    assert ab["required"] == TYPED["required"] - budget
    assert ab["required_plus_contingency"] == TYPED["required_plus_contingency"] - budget
    assert ab["required_with_cuts_plus_contingency"] == TYPED["required_with_cuts_plus_contingency"] - budget


def test_page_figures_are_the_typed_totals():
    T = car_totals(CAR, PROJECT["car_build"]["budget_aud"])
    assert T["required"] == TYPED["required"]
    assert T["with_contingency"] == TYPED["required_plus_contingency"]
    assert T["with_cuts"] == TYPED["required_with_cuts_plus_contingency"]
    assert T["cuts"] == TYPED["cuts"]
    assert T["gap"] == TYPED["against_budget"]["required_plus_contingency"]
    if T["gap"] > 0:
        assert T["closing_saving"] >= T["gap"] and T["with_closing"] <= T["budget"], "the named cuts do not close the gap"


def test_vehicle_md_quotes_the_totals():
    t = TYPED
    for v in (t["required"], t["required_plus_contingency"], t["required_with_cuts_plus_contingency"], t["contingency_allowance"],
              t["build_budget"], t["against_budget"]["required_plus_contingency"], t["cuts"],
              PROJECT["truck"]["purchase_aud"], BOX["total_aud"], BOX["owner_built_total_aud"]):
        assert any(f in PLAN for f in (f"AUD {_aud(v)}", f"| {_aud(v)} |", f"| -{_aud(v)} |")), f"VEHICLE.md does not quote {_aud(v)}"
    bp = t["by_priority"]
    for v in (bp["P1"]["required"], bp["P2"]["required"], bp["P3"]["optional"]):
        assert f"AUD {_aud(v)}" in PLAN, f"VEHICLE.md does not quote the priority total {_aud(v)}"
    for word in ("placeholder", "pending R20", "30,000"):
        assert word not in PLAN, f"VEHICLE.md still has {word!r}"


def test_vehicle_md_stage_table():
    rows = {r[0]: r for r in _rows(_section("Stage plan"))}
    for st in STAGES:
        for col, status in ((2, "required"), (3, "contingency")):
            v = _sum(stage=st, status=status)
            assert abs(_num(rows[st][col]) - v) <= 1, f"VEHICLE.md stage {st} {status}: {rows[st][col]}, the lines give {v:,.2f}"
    assert abs(_num(rows["Total"][2]) - TYPED["required"]) <= 1


def test_vehicle_md_system_table():
    """Each row of VEHICLE.md's table by system is one system's required, contingency and optional sums."""
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
    """The home page's table: the truck, the car build with its allowance, and the box and the trailer, each with its
    owner-built total beside it. The trailer's row is its parts list's totals (test_trailer_parts.py)."""
    t = project_costs(BOX)
    rows = {r["id"]: r for r in t["rows"]}
    assert [r["id"] for r in t["rows"]] == ["truck", "car", "box", "trailer"]
    assert rows["truck"]["total"] == PROJECT["truck"]["purchase_aud"]
    assert rows["car"]["total"] == TYPED["required_plus_contingency"]
    assert rows["car"]["before"] + rows["car"]["contingency"] == rows["car"]["total"]
    assert abs(rows["box"]["before"] + rows["box"]["contingency"] - rows["box"]["total"]) < 0.01
    assert rows["box"]["total"] == BOX["total_aud"] and rows["box"]["owner_built"] == BOX["owner_built_total_aud"]
    tr = rows["trailer"]
    assert not tr.get("pending") and t["pending"] == []
    assert abs(tr["total"] - TRAILER["total_aud"]) < 0.01 and tr["owner_built"] == TRAILER["owner_built_total_aud"]
    known = PROJECT["truck"]["purchase_aud"] + TYPED["required_plus_contingency"] + BOX["total_aud"] + TRAILER["total_aud"]
    assert abs(t["total"] - known) < 0.01
    owner = known - BOX["total_aud"] + BOX["owner_built_total_aud"] - TRAILER["total_aud"] + TRAILER["owner_built_total_aud"]
    assert abs(t["total_owner_built"] - owner) < 0.01
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
    others = PROJECT["truck"]["purchase_aud"] + TYPED["required_plus_contingency"] + BOX["total_aud"]
    assert abs(t["total"] - others - 1650) < 0.01

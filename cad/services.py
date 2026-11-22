"""The services' budgets for the site's Electrical, Plumbing and HVAC pages: the energy budget by load group from
research report 20's model output, the battery autonomy and recharge figures from the same output, the water budget,
and the circuits, shedding order, outlets and ventilation modes in data/services.yaml.
"""
from __future__ import annotations

import re

import yaml

from .partsdb import DATA, ROOT

ENERGY_OUT = ROOT / "research" / "models" / "20" / "energy.out"
CASE_RE = re.compile(r"^=== (?P<name>.*) \((?P<id>hot|hot_diesel|cold_diesel|cold_hp)\) ===$")
LOAD_RE = re.compile(r"^(?P<id>[A-Z]{2}-\d\d) (?P<name>.*?)\s+(?P<side>ac|dc|dc12|dc24)\s+(?P<kwh>[\d.]+)$")


def _cases(text: str) -> list[dict]:
    """The energy model's four design cases: each load's daily energy at its own bus, the conversion losses and the
    daily total at the battery bus."""
    cases, cur = [], None
    for line in text.split("\n"):
        m = CASE_RE.match(line)
        if m:
            cur = dict(id=m["id"], name=m["name"], loads={}, total=None)
            cases.append(cur)
            continue
        if cur is None or cur["total"] is not None:
            continue
        lm = LOAD_RE.match(line)
        if lm:
            cur["loads"][lm["id"]] = dict(name=lm["name"].replace(" (prov.)", ""), kwh=float(lm["kwh"]))
        elif line.startswith("Inverter conversion loss"):
            cur["loads"]["INV"] = dict(name="Inverter conversion loss, idle and search", kwh=float(line.split()[-1]))
        elif line.startswith("DC-DC converter loss"):
            cur["loads"]["DCDC"] = dict(name="DC-DC converter loss and idle", kwh=float(line.split()[-1]))
        elif line.startswith("Daily total at the battery bus"):
            cur["total"] = float(line.split()[-1])
    return cases


def _autonomy(text: str, bank: str) -> dict:
    """H3's capacity checks and the chosen bank's hours on the design hot day, from the model output."""
    checks = [dict(case=m[1].strip(), nominal_kwh=float(m[2]), usable_kwh=float(m[3]))
              for m in re.finditer(r"^(Hot day.*?|Cold night.*?)\s{2,}([\d.]+) kWh nominal,\s+([\d.]+) kWh usable$", text, re.M)]
    row = next(ln for ln in text.split("\n") if ln.startswith(bank))
    nums = row[len(bank):].split()
    return dict(checks=checks, bank=bank, kwh=float(nums[0]), kg=float(nums[1]), aud=float(nums[2]),
                hours_new=float(nums[-2]), hours_end_of_life=float(nums[-1]))


def _recharge(text: str) -> list[dict]:
    block = text.split("=== Recharge of one all-electric design hot day ===", 1)[1].split("\n===", 1)[0]
    rows = []
    for ln in block.strip().split("\n")[1:]:
        m = re.match(r"^(.*?)\s{2,}(\d+) W into the battery:\s+(.*)$", ln)
        if m:
            rows.append(dict(source=m[1].strip(), watts=int(m[2]), result=m[3].strip()))
    return rows


def services() -> dict:
    """Everything the services pages show, worked out from the model output and data/services.yaml."""
    data = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8"))
    text = ENERGY_OUT.read_text(encoding="utf-8")
    cases = _cases(text)
    groups = data["energy_groups"]
    table = []
    for g in groups:
        row = dict(group=g["name"], ids=g["ids"], kwh={})
        for c in cases:
            row["kwh"][c["id"]] = round(sum(v["kwh"] for k, v in c["loads"].items() if k in g["ids"] or k[:2] in g["ids"]), 2)
        table.append(row)
    water = data["water_budget"]
    fresh = sum(r["fresh_l"] for r in water["daily"])
    grey = sum(r["grey_l"] for r in water["daily"])
    wash = water["wash"]
    days = [dict(case=d["case"], litres=d["litres"], washes_a_week=d["washes_a_week"],
                 days=round(d["litres"] / (fresh + wash["fresh_l"] * d["washes_a_week"] / 7), 1)) for d in water["stores"]]
    return dict(
        energy=dict(cases=[dict(id=c["id"], name=c["name"], label=data["energy_cases"][c["id"]], total=c["total"])
                           for c in cases], groups=table, source=str(ENERGY_OUT.relative_to(ROOT))),
        autonomy=_autonomy(text, data["battery_bank"]), recharge=_recharge(text),
        water=dict(daily=water["daily"], wash=wash, fresh_l=fresh, grey_l=grey, days=days,
                   grey_tank_l=water["grey_tank_l"], grey_hours_one_wash=water["grey_hours_one_wash"]),
        circuits=data["electrical"]["circuits"], shedding=data["electrical"]["shedding"],
        outlets=data["electrical"]["outlets"],
        buses=dict(v12=data["electrical"]["bus_12v"], v24=data["electrical"]["bus_24v"]),
        modes=data["ventilation_modes"], hvac=data["hvac"], lamps=_lamps(), bd11=_mass_line("BD-11"))


def _mass_line(line: str) -> dict | None:
    """A mass line's items from data/assemblies/trailer.yaml, and how much of it is still unassigned: the items that
    are an allowance not yet given to a part. The Electrical page says so beside the routed runs it prices."""
    items = yaml.safe_load((DATA / "assemblies" / "trailer.yaml").read_text(encoding="utf-8"))["items"]
    e = next((x for x in items if x.get("id") == line), None)
    if e is None:
        return None
    parts = [dict(item=p["item"], kg=p["kg"]) for p in e.get("parts") or []]
    return dict(line=line, name=e["name"], parts=parts, kg=round(sum(p["kg"] for p in parts), 1),
                unassigned_kg=round(sum(p["kg"] for p in parts if p["item"].lower().startswith("allowance")), 1))


def _lamps() -> dict:
    """The lamp schedule and its checks for the Electrical page, from cad/lamps.py."""
    from .lamps import resolve
    r = resolve()
    return {k: r[k] for k in ("table", "checks", "plate", "n_lamps", "n_reflectors", "ok", "src", "plate_src", "outer_edge")}

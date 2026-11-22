"""The trailer's priced parts list: every priced line of the mass schedule, the stock bought for the chassis, the
installation, compliance, freight and consumables, the contingency and the total. Leonard builds the trailer himself,
so no labour is hired and the list has one total (decision H26).

Prices sit on the lines: the items of data/assemblies/trailer.yaml and the bought fittings of data/chassis/chassis.yaml
carry a `price`, and data/trailer-parts.yaml holds the rest and the rules (its header gives the price forms). The site
renders the list (cad/sitedata.py), the home page's cost table takes the trailer's row from it, and the schedule rows
and the 3D model's part cards show each block's share (block_prices). cad/tests/test_trailer_parts.py checks it.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml

from .partsdb import DATA, ROOT

PARTS_YAML = DATA / "trailer-parts.yaml"
BASES = ("listing", "quote", "rate", "estimate")


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def instances(item: dict) -> int:
    """How many blocks a trailer item makes in the layout: the product of the lengths of its `for` lists."""
    n = 1
    for values in (item.get("for") or {}).values():
        n *= len(values)
    return n


def price_parts(price, qty: float) -> list[dict]:
    """A `price` field as its bought parts, each with its AUD for the whole line. An aud_each is multiplied by qty, the
    line's instances in the layout or its quantity in data/trailer-parts.yaml."""
    rows = []
    for p in price if isinstance(price, list) else [price]:
        aud = p["aud"] if "aud" in p else p["aud_each"] * qty
        rows.append(dict(p, aud=round(float(aud), 2), date=str(p["date"])))
    return rows


def _dominant(parts: list[dict]) -> str:
    """The basis that carries most of a line's money, or the first part's when every part is zero."""
    by = defaultdict(float)
    for p in parts:
        by[p["basis"]] += p["aud"]
    return max(by, key=lambda b: (by[b], -BASES.index(b))) if any(by.values()) else parts[0]["basis"]


def _line(lid: str, name: str, group: str, qty: float, unit: str, price, pct: dict, **extra) -> dict:
    parts = price_parts(price, qty)
    aud = round(sum(p["aud"] for p in parts), 2)
    first = parts[0]
    head = dict(aud=aud, basis=_dominant(parts), url=next((p["url"] for p in parts if p.get("url")), None),
                date=max(p["date"] for p in parts))
    for key in ("converted_from", "included_in", "note"):
        if len(parts) == 1 and first.get(key):
            head[key] = first[key]
    cont = round(sum(p["aud"] * pct[p["basis"]] / 100 for p in parts), 2)
    line = dict(id=lid, name=name, group=group, qty=qty, unit=unit, price=head, contingency_aud=cont, **extra)
    if isinstance(price, list):
        line["parts"] = parts
    return line


def parts_list(path: Path = PARTS_YAML) -> dict:
    """The whole priced list with its totals, in the bike box list's shape: `lines` with price.aud, and `totals` with
    the contingency and the total worked out from the lines."""
    from .trailer import SYSTEM_LABELS
    head = _load(path)
    pct = head["totals"]["contingency_pct"]
    labels = dict(SYSTEM_LABELS, **head["groups"])
    lines = []
    src_trailer, src_chassis = head["sources"]
    for it in _load(ROOT / src_trailer)["items"]:
        if "price" in it:
            lines.append(_line(it["id"], it["name"], it["system"], instances(it), "each", it["price"], pct,
                               source=src_trailer, load=it.get("load", "tare")))
    for f in _load(ROOT / src_chassis)["fittings"]:
        if "price" in f:
            group = "drawbar" if f["id"].startswith("DB-") else "chassis"
            qty = f.get("qty", 1)
            lines.append(_line(f["id"], f["name"], group, qty, "each", f["price"], pct, source=src_chassis, load="tare"))
    rel = str(path.relative_to(ROOT)) if path.is_absolute() and ROOT in path.parents else str(path)
    for ln in head["lines"]:
        lines.append(_line(ln["id"], ln["name"], ln["group"], ln["qty"], ln["unit"], ln["price"], pct, source=rel,
                           covers=ln.get("covers") or [], note=ln.get("note")))
    return dict({k: v for k, v in head.items() if k not in ("lines", "totals", "savings")}, group_labels=labels, lines=lines,
                totals=totals(lines, head["totals"]))


def totals(lines: list[dict], rule: dict) -> dict:
    """Totals by group and by basis, the contingency and the total."""
    aud, cont = defaultdict(float), defaultdict(float)
    by_basis = defaultdict(float)
    for ln in lines:
        aud[ln["group"]] += ln["price"]["aud"]
        cont[ln["group"]] += ln["contingency_aud"]
        for p in ln.get("parts") or [dict(aud=ln["price"]["aud"], basis=ln["price"]["basis"])]:
            by_basis[p["basis"]] += p["aud"]
    sub, contingency = sum(aud.values()), sum(cont.values())
    return dict(
        contingency_pct=rule["contingency_pct"], contingency_why=rule.get("contingency_why"), labour_why=rule.get("labour_why"),
        by_group={g: round(v, 2) for g, v in aud.items()}, contingency_by_group={g: round(v, 2) for g, v in cont.items()},
        by_basis={b: round(by_basis[b], 2) for b in BASES if b in by_basis},
        subtotal_aud=round(sub, 2), contingency_aud=round(contingency, 2), total_aud=round(sub + contingency, 2),
        lines=len(lines))


def _with_contingency(parts: list[dict], pct: dict) -> float:
    return sum(p["aud"] * (1 + pct[p["basis"]] / 100) for p in parts)


def savings(lst: dict | None = None, path: Path = PARTS_YAML) -> list[dict]:
    """The options in data/trailer-parts.yaml's `savings`, each worked out from the lines it removes, with their
    contingency, less what replaces it at its own contingency, and its share of the list's total. Largest first. A
    negative saving costs more."""
    head = _load(path)
    lst = lst or parts_list(path)
    pct = head["totals"]["contingency_pct"]
    by_id = {ln["id"]: ln for ln in lst["lines"]}

    def whole(ln):
        return ln["price"]["aud"] + ln["contingency_aud"]

    out = []
    for sv in head.get("savings") or []:
        rm = sv["removes"]
        removed = sum(whole(ln) for ln in lst["lines"] if ln["group"] in rm.get("groups", []))
        removed += sum(whole(by_id[i]) for i in rm.get("lines", []))
        for p in rm.get("parts", []):
            ln = by_id[p["line"]]
            if "share" in p:
                removed += p["share"] * whole(ln)
            else:
                hit = [x for x in ln["parts"] if x["item"].startswith(p["item"])]
                assert len(hit) == 1, f"{sv['id']}: {p['item']!r} matches {len(hit)} parts of {p['line']}"
                removed += _with_contingency(hit, pct)
        added = _with_contingency(price_parts(sv["adds"], 1), pct) if sv.get("adds") else 0.0
        out.append(dict(sv, removed_aud=round(removed, 2), added_aud=round(added, 2), saving_aud=round(removed - added, 2),
                        share_pct=round(100 * (removed - added) / lst["totals"]["total_aud"], 1)))
    return sorted(out, key=lambda s: -s["saving_aud"])


def block_prices(blocks, lst: dict | None = None) -> dict[str, dict]:
    """Each block's price, for the schedule rows and the 3D model's part cards: a priced line's price split evenly over
    its blocks, or a share of the stock line that covers it, in proportion to mass. Blocks with neither (payload,
    water, fuel) are left out."""
    lst = lst or parts_list()
    by_id = defaultdict(list)
    for b in blocks:
        by_id[b.id].append(b)
    out = {}
    for ln in lst["lines"]:
        p = ln["price"]
        meta = dict(price_basis=p["basis"], price_url=p.get("url"), price_date=p["date"], price_line=ln["id"])
        if ln.get("covers"):
            covered = [b for i in ln["covers"] for b in by_id.get(i, [])]
            kg = sum(b.mass_kg for b in covered)
            for b in covered:
                out[b.iid] = dict(meta, price_aud=round(p["aud"] * b.mass_kg / kg, 2),
                                  price_note=f"Its share by mass of {ln['id']}: {ln['name']}")
        elif ln["id"] in by_id:
            own = by_id[ln["id"]]
            note = (f"In the price of {p['included_in']}" if p.get("included_in") else
                    f"One of {len(own)}, the line costs AUD {p['aud']:,.2f}" if len(own) > 1 else None)
            for b in own:
                out[b.iid] = dict(meta, price_aud=round(p["aud"] / len(own), 2), price_note=note)
    return out

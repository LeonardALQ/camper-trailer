"""Part metadata beside each 3D model, for the site's hover tooltip and part card (S-01).

For every part in a three-cad-viewer file: what it is, what it is made of, its mass and where that comes from, and the
drawing it is on. It is written as <model>.parts.json next to <model>.viewer.json. A tree node is matched to a part
by the first word of its name, which the model exports set to the part's line or instance id. A node whose first word
is no part (the sub-solids of a fitting, the pieces of a bike) belongs to the nearest ancestor that is one, and the
site finds that ancestor itself.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

FIELDS = ("id", "iid", "name", "group", "system", "material", "mass_kg", "mass_growth_kg", "maturity", "basis",
          "source", "drawing", "price_aud", "price_basis", "price_note", "load")


def _r(v):
    return None if v is None else round(v + 0.0, 2)


def _nodes(viewer: dict) -> list[tuple[str, str]]:
    """(path, name) of every node below the root, in tree order."""
    out = []

    def walk(o):
        for p in o.get("parts") or []:
            out.append((p["id"], p["name"]))
            walk(p)
    walk(viewer)
    return out


def write(viewer_path: Path, lookup) -> dict:
    """Write <model>.parts.json for one viewer file. `lookup(key)` gives a part's metadata from the first word of a node
    name, or None. `nodes` maps each matched tree path to its part and the node's own label."""
    viewer = json.loads(viewer_path.read_text())
    parts: dict[str, dict] = {}
    nodes: dict[str, list[str]] = {}
    for path, name in _nodes(viewer):
        key, _, label = name.partition(" ")
        meta = lookup(key)
        if meta is None:
            continue
        iid = meta["iid"]
        nodes[path] = [iid, label]
        part = parts.setdefault(iid, {k: meta.get(k) for k in FIELDS} | {"paths": []})
        part["paths"].append(path)
    out = dict(model=viewer.get("name"), parts=parts, nodes=nodes)
    viewer_path.with_name(viewer_path.name.replace(".viewer.json", ".parts.json")).write_text(
        json.dumps(out, separators=(",", ":"), default=str), encoding="utf-8")
    return out


# ------------------------------------------------------------------ the trailer (cad/trailer.py blocks)
def _trailer_drawing(b) -> str:
    if b.system == "drawbar" or b.id.startswith("DB-"):
        return "CT-102"
    return {"chassis": "CT-101", "body": "CT-201", "roof": "CT-201"}.get(b.system, "CT-001")


def _price(bs: list, prices: dict) -> dict:
    """The price of one block or of a whole line's blocks (cad/trailer_costs.py), with its basis and a note."""
    got = [prices[b.iid] for b in bs if b.iid in prices]
    if not got:
        why = "Payload, water and fuel carry no price" if bs[0].load != "tare" else None
        return dict(price_aud=None, price_basis=None, price_note=why)
    note = got[0].get("price_note") if len(bs) == 1 else f"The {len(bs)} parts together"
    return dict(price_aud=round(sum(p["price_aud"] for p in got), 2), price_basis=got[0]["price_basis"], price_note=note)


def trailer_lookup(lay, body: dict):
    """Parts of the trailer's models: the layout's blocks by instance id, then by line id (a line with several
    instances adds them up), and the body's openings, whose mass is in the line each one names (data/body/body.yaml).
    Each block carries its price from the trailer's parts list (cad/trailer_costs.py)."""
    from .trailer import SYSTEM_LABELS
    from .trailer_costs import block_prices
    prices = block_prices(lay.blocks)
    by_iid = {b.iid: b for b in lay.blocks}
    lines: dict[str, list] = {}
    for b in lay.blocks:
        lines.setdefault(b.id, []).append(b)
    openings = {o["id"]: o for o in body.get("openings", [])}

    def meta(key: str):
        bs = [by_iid[key]] if key in by_iid else lines.get(key, [])
        if bs:
            b = bs[0]
            return dict(
                id=b.id, iid=key, name=b.name + (f" ({len(bs)} parts together)" if len(bs) > 1 else ""),
                group=SYSTEM_LABELS[b.system], system=b.system, material=b.material,
                mass_kg=_r(sum(x.mass_kg for x in bs)), mass_growth_kg=_r(sum(x.mass_kg * (1 + x.growth) for x in bs)),
                maturity=b.maturity, basis=b.basis, source=b.source, drawing=_trailer_drawing(b), load=b.load,
                **_price(bs, prices))
        o = openings.get(key)
        if o:
            return dict(id=o["id"], iid=o["id"], name=f"{o['name']}, {o['wall']} wall, cut-out {o['w']:.0f} x {o['h']:.0f} mm",
                        group="Body", system="body", source=f"Its mass is in line {o['line']}" if o.get("line") else "A cut-out in the wall panel",
                        drawing="CT-201", load="tare",
                        price_note=f"A cut-out, priced with line {o['line']}" if o.get("line") else "A cut-out in the wall panel")
        return None
    return meta


# ------------------------------------------------------------------ the ute and its bike box (cad/ute.py, cad/ute_garage.py)
UTE_DRAWING = {"body": "CT-702", "subframe": "CT-702", "doors": "CT-703", "security": "CT-703", "restraint": "CT-704",
               "safety": "CT-704"}


def ute_lookup(ute, gmodel):
    """Parts of the ute's models: the cab chassis envelopes and wheels (data/ute/ute.yaml), and the bike box's
    instances with their part (data/ute/parts) and their own mass (cad/massprops.py)."""
    from .massprops import BODY_MASS
    from .model.assembly import GROUP_LABELS
    from .ute import GROWTH
    lines = {ln["id"]: ln for ln in ute.lines}
    solids = {s["id"]: s for s in ute.d["solids"]}
    prj = gmodel.prj if gmodel is not None else None
    inst = {i.iid: i for i in prj.instances} if prj else {}
    bodies: dict[str, int] = {}
    for i in inst.values():
        if not i.check_only:
            bodies[i.part] = bodies.get(i.part, 0) + 1

    def line_meta(ln, key, name, group, system, drawing, material=None, mass=None):
        kg = ln["kg"] if mass is None else mass
        return dict(id=ln["id"], iid=key, name=name, group=group, system=system, material=material, mass_kg=_r(kg),
                    mass_growth_kg=_r(kg * (1 + GROWTH[ln["maturity"]])), maturity=ln["maturity"], basis="declared",
                    source=ln["source"], drawing=drawing, price_aud=None, load="tare")

    def meta(key: str):
        if key in solids:
            s = solids[key]
            ref = re.search(r"\((UT-\d+)\)", s["name"])
            if ref and ref.group(1) in lines:
                return line_meta(lines[ref.group(1)], key, s["name"], "Cab chassis and accessories", "ute", "CT-701")
            return dict(id="UT-01", iid=key, name=s["name"], group="Cab chassis and accessories", system="ute",
                        source="Envelope of the cab chassis. Its mass is in line UT-01", drawing="CT-701", load="tare")
        if key.startswith("WH-"):
            return dict(id="UT-01", iid=key, name="Wheel and tyre, ROH Trak 2 16 x 7 with LT265/75R16",
                        group="Cab chassis and accessories", system="ute", material="Steel wheel, radial light-truck tyre",
                        source="Part of the cab chassis, line UT-01. The spare is line UT-05", drawing="CT-701", load="tare")
        i = inst.get(key)
        if i is None:
            return None
        part = prj.parts[i.part]
        group, drawing = GROUP_LABELS.get(i.group, i.group), UTE_DRAWING.get(i.group, "CT-701")
        bike = lines.get(f"UB-{key}")
        if bike:
            return line_meta(bike, key, part.name, group, i.group, drawing)
        if part.kind != "bom" or part.mass is None:
            src = f"Included in {part.included_in}" if part.included_in else "Shown for context. It is not part of the box's mass"
            return dict(id=part.included_in or part.id, iid=key, name=part.name, group=group, system=i.group,
                        material=part.material, source=src, drawing=drawing, load="tare")
        body = BODY_MASS.get(key)
        ln = lines.get(part.id)
        kg = body["mass_kg"] if body else (ln["kg"] / max(1, bodies.get(part.id, 1)) if ln else None)
        m = part.mass
        return dict(id=part.id, iid=key, name=part.name, group=group, system=i.group, material=part.material,
                    mass_kg=_r(kg), mass_growth_kg=_r(kg * (1 + GROWTH[m.maturity])) if kg is not None else None,
                    maturity=m.maturity, basis=m.basis, source=m.source, drawing=drawing, price_aud=None,
                    load="payload" if part.payload else "tare")
    return meta

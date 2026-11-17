"""Mass schedule (MASS-01) and mass, centre of gravity per load case.

Line mass:
  declared   unit_kg x qty (or total_kg), spread equally over the line's placed bodies for the CoG
  per_length kg_per_m x the modelled length of each body (beams, ledgers, cleats, track)
  per_area   kg_per_m2 x the modelled face area of each body (deck and partitions)
CoG of a body is its B-rep centre of mass in the module frame, except the bikes (the 05 estimate,
moved with the bike) and lines whose data gives a `cog` (BOM-only lines and the ramp placeholder).
"""
from __future__ import annotations

from build123d import CenterOf

from .partsdb import Project


def _round(v, n=1):
    return None if v is None else round(v + 0.0, n)


BODY_MASS: dict[str, dict] = {}
# MASS-06 growth allowance proposed in research/02 (to be agreed with the engineer): estimate +20 %,
# calculated +7 %. A maker's or retailer's spec mass is taken at 0 % here (assumption, not in MASS-06).
GROWTH = {"estimate": 0.20, "calculated": 0.07, "spec": 0.0}


def line_masses(prj: Project, model) -> list[dict]:
    rows = []
    BODY_MASS.clear()
    built = model.built
    straps_top = [b.info["top"] for b in built.values() if b.inst.part == "G-05" and "top" in b.info]
    for part in [p for p in prj.parts.values() if p.kind == "bom" and not p.payload]:
        bodies = [b for b in built.values() if b.inst.part == part.id and not b.inst.check_only]
        m = part.mass
        per_body: list[tuple[float, tuple[float, float, float], str]] = []
        measured = None
        if m.basis == "declared":
            total = m.total_kg if m.total_kg is not None else m.unit_kg * part.qty
            unit = m.unit_kg if m.unit_kg is not None else None
            qty = part.qty
        elif m.basis == "per_length":
            measured = sum(b.info["length_m"] for b in bodies)
            total = m.kg_per_m * measured
            unit, qty = m.kg_per_m, measured
        else:
            measured = sum(b.info["area_m2"] for b in bodies)
            total = m.kg_per_m2 * measured
            unit, qty = m.kg_per_m2, measured
        cog_basis = ""
        if bodies and not (part.cog and part.cog.at):
            weights = []
            for b in bodies:
                if m.basis == "per_length":
                    w = m.kg_per_m * b.info["length_m"]
                elif m.basis == "per_area":
                    w = m.kg_per_m2 * b.info["area_m2"]
                else:
                    w = total / len(bodies)
                if b.cog_override is not None:
                    c = b.cog_override
                else:
                    v = b.shape.center(CenterOf.MASS)
                    c = (v.X, v.Y, v.Z)
                weights.append((w, c))
                BODY_MASS[b.inst.iid] = dict(part_id=part.id, mass_kg=round(w, 4), cog_mm=[round(x, 1) for x in c],
                                             maturity=m.maturity)
            cog = tuple(sum(w * c[i] for w, c in weights) / sum(w for w, _ in weights) for i in range(3)) if total > 0 else (0, 0, 0)
            cog_basis = "Centre of the modelled bodies" + (" (12 fitted, the 2 spares share their mean)" if part.id == "G-03" else "")
        elif part.cog and part.cog.at:
            cog = tuple(prj.P.eval(part.cog.at, {}))
            cog_basis = part.cog.basis
        elif part.cog and part.cog.from_items == "straps_top":
            cog = tuple(sum(p[i] for p in straps_top) / len(straps_top) for i in range(3))
            cog_basis = part.cog.basis
        else:
            raise ValueError(f"{part.id}: no CoG")
        rows.append(dict(
            id=part.id, group=part.group, item=part.name, product=part.product, maker=part.maker, part_no=part.part_no,
            qty=qty, qty_bom=part.qty, unit=part.unit, basis=m.basis, unit_mass=unit, mass_kg=total,
            growth_pct=round(GROWTH[m.maturity] * 100), mass_with_growth_kg=total * (1 + GROWTH[m.maturity]),
            measured=measured, source=m.source, maturity=m.maturity, mass_note=m.note,
            cog=[_round(c) for c in cog], cog_basis=cog_basis, removable=part.removable,
            bodies=len(bodies), size=part.size, rating=part.rating, use=part.use, links=part.links,
            stockist_au=part.stockist_au, notes=part.notes,
        ))
    order = {"garage": 0, "bed": 1, "partitions": 2, "fixings": 3, "access": 4}
    rows.sort(key=lambda r: (order.get(r["group"], 9), r["id"]))
    return rows


def bike_rows(prj: Project, model) -> list[dict]:
    rows = []
    for ref in ("TU", "ST"):
        b = model.built[ref]
        part = prj.parts[b.inst.part]
        rows.append(dict(id=ref, part=part.id, item=part.name, mass_kg=part.mass.unit_kg, source=part.mass.source,
                         maturity=part.mass.maturity, cog=[_round(c) for c in b.cog_override],
                         cog_basis="05 centre-of-mass estimate, moved with the bike", pitch_deg=round(b.info["pitch_deg"], 3)))
    return rows


def load_cases(prj: Project, lines: list[dict], bikes: list[dict]) -> list[dict]:
    out = []
    bikes_by = {b["id"]: b for b in bikes}
    for lc in prj.load.load_cases:
        items = [(r["mass_kg"], r["cog"]) for r in lines if lc.module == "all" or not r["removable"]]
        items += [(bikes_by[k]["mass_kg"], bikes_by[k]["cog"]) for k in lc.bikes]
        grown = sum(r["mass_with_growth_kg"] for r in lines if lc.module == "all" or not r["removable"])
        grown += sum(bikes_by[k]["mass_kg"] for k in lc.bikes)
        M = sum(m for m, _ in items)
        cog = [sum(m * c[i] for m, c in items) / M for i in range(3)]
        out.append(dict(id=lc.id, name=lc.name, mass_kg=M, mass_with_growth_kg=grown, cog=[_round(c) for c in cog],
                        bikes=lc.bikes, module=lc.module))
    return out


def group_totals(lines: list[dict]) -> dict:
    g: dict[str, float] = {}
    for r in lines:
        g[r["group"]] = g.get(r["group"], 0.0) + r["mass_kg"]
    g["module_empty"] = sum(r["mass_kg"] for r in lines)
    g["removable"] = sum(r["mass_kg"] for r in lines if r["removable"])
    return g

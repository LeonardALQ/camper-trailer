"""Rows of the chassis checks (data/checks.yaml, types chassis_*), from the frame analysis in cad/chassis_fea.py."""
from __future__ import annotations

LOCAL = {"chain_lug": "chain_lug", "front_recovery": "front_recovery", "rear_recovery": "rear_recovery",
         "jacking_pad": "jacking_pad", "spare_posts": "spare_posts", "steady_bracket": "steady_bracket"}
DEFLECTION = {"span": "rail between the drawbar root and the front hub, against the chord", "tip": "rear overhang tip, against the line "
              "through the two hubs", "outrigger": "outrigger tip, against the rail at its root"}


def chassis_row(c, res: dict) -> dict:
    if c.type == "chassis_stress":
        g = res["governing"][c.load_case]
        return dict(limit=f"<= {g['limit']:.0f} MPa (fy / {g['factor']:g})", measured=round(g["eq"], 1), unit="MPa",
                    margin=round(g["limit"] - g["eq"], 1), ok=g["eq"] <= g["limit"] + 1e-6, governing=f"{g['member']}, {g['case']}",
                    detail=(f"{g['eq']:.0f} MPa combined in {g['member']} at X {g['at'][0]}, Y {g['at'][1]:+d}, Z {g['at'][2]}, "
                            f"{g['case']}: utilisation {g['util']:.2f}"), utilisation=round(g["util"], 3))
    if c.type == "chassis_local" and c.item == "holes":
        hs = [h for h in res["holes"] if not h["open"]]
        w = max(hs, key=lambda h: h["util"])
        s = w["static"]
        return dict(limit="<= each case's limit on the net section", measured=round(100 * w["util"], 1), unit="%",
                    margin=round(100 * (1 - w["util"]), 1), ok=all(h["static_ok"] for h in hs),
                    governing=f"{w['id']} in {w['wall']} at X {w['x']:,.0f} ({', '.join(w['runs'])}), {s['lc']}",
                    detail=(f"{len(hs)} holes in the rails and raisers. The worst, {w['id']}, {w['d']:g} mm across in {w['wall']} at X "
                            f"{w['x']:,.0f} mm: {s['mpa']:.0f} MPa on the net section against {s['limit']:.0f} MPa in {s['lc']}, {s['case']}"))
    if c.type == "chassis_local" and c.item == "hole_places":
        hs = [h for h in res["holes"] if not h["open"]]
        bad = [h for h in hs if not h["place_ok"]]
        why = []
        for h in bad:
            parts = []
            if not h["edge_ok"]:
                parts.append(f"edge {h['edge_mm']:.1f} of {h['edge_need']:.0f} mm")
            if not h["toe_ok"]:
                parts.append(f"{h['toe_mm']:.0f} of {h['toe_need']:.0f} mm from the {h['toe_weld']}")
            if not h["fat_ok"]:
                parts.append(f"{h['peak_mpa']:.0f} MPa at its edge against {h['cafl']:.1f}")
            why.append(f"{h['id']} ({', '.join(h['runs'])}, {h['wall']} at X {h['x']:,.0f}): {', '.join(parts)}")
        top = max(hs, key=lambda h: h["peak_mpa"] / h["cafl"])
        return dict(limit="edge 1.25 d, weld toes 1.0 d, edge range <= CAFL", measured=len(bad), unit=f"of {len(hs)} holes", margin=-len(bad),
                    ok=not bad, governing="; ".join(f"{h['id']} {h['member']}" for h in bad[:4]) or f"{top['id']}, its edge range",
                    detail=(f"{len(hs) - len(bad)} of {len(hs)} holes meet the three rules. " + ". ".join(why)
                            + f". The highest range at a hole's edge is {top['peak_mpa']:.1f} MPa at {top['id']}, against {top['cafl']:.1f} MPa"))
    if c.type == "chassis_local":
        r = res["local"][LOCAL[c.item]]
        return dict(limit="<= 100 % of each part's limit", measured=round(100 * r["util"], 1), unit="%", margin=round(100 * (1 - r["util"]), 1),
                    ok=r["util"] <= 1 + 1e-9, governing=f"{r['name']}, {r['governing']}",
                    detail=f"{r['governing']}: {r['mpa']:.0f} MPa against {r['limit_mpa']:.0f} MPa, under {r['load']}", parts=r["parts"])
    if c.type == "chassis_deflection":
        d = res["deflections"][c.item]
        return dict(limit=f"<= {d['limit_mm']:.1f} mm", measured=round(d["mm"], 2), unit="mm", margin=round(d["limit_mm"] - d["mm"], 2),
                    ok=d["mm"] <= d["limit_mm"] + 1e-9, governing=d["case"],
                    detail=f"{d['mm']:.2f} mm at the {DEFLECTION[c.item]}, {d['case']} at ATM, against {d['limit_mm']:.1f} mm")
    if c.type == "chassis_twist":
        t = res["twist"]
        return dict(limit=f"<= {c.max:g} degree", measured=round(t["deg"], 3), unit="deg", margin=round(c.max - t["deg"], 3),
                    ok=t["deg"] <= c.max + 1e-9, governing=t["case"],
                    detail=f"{t['deg']:.3f} degree between the XT front hinge and rear shock crossmembers, {t['case']}")
    if c.type == "chassis_fatigue":
        f = next(r for r in res["fatigue"] if r["id"] == c.item)
        hs = " Hollow-section T-joint: the engineer checks it by the hot-spot method." if f["hot_spot"] else ""
        return dict(limit=f"range <= CAFL {f['cafl']:.1f} MPa, damage <= 0.5", measured=round(f["range_mpa"], 1), unit="MPa",
                    margin=round(f["cafl"] - f["range_mpa"], 1), ok=f["ok"], governing=f"{f['where']}, {f['case']}",
                    detail=(f"IIW {f['iiw']} FAT {f['fat']:g}: frequent range {f['range_mpa']:.1f} MPa against CAFL {f['cafl']:.1f} MPa, "
                            f"occasional range {f['occasional_range_mpa']:.0f} MPa gives Miner damage {f['damage']:.2f} at {f['where']}.{hs}"))
    raise ValueError(c.type)


def report(tr, lay) -> dict:
    """Everything the drawings, the site and CHASSIS.md need about the chassis: members, joints, fittings, mass,
    galvanising, the analysis results and the tyre clearance."""
    from .trailer import _r
    res = tr.chassis_results(lay)
    ch = tr._chassis[1]
    comp = ch.comp
    members = [dict(id=m.id, role=m.role, name=m.name, section=m.sec.name, section_id=m.sec.id, length_mm=m.length, kg_per_m=m.sec.kg_m,
                    mass_kg=m.mass_kg, area_m2=m.area_m2, p0=list(m.p0), p1=list(m.p1), side=m.side, station=m.station, note=m.note,
                    box=list(m.box()))
               for m in ch.members]
    fittings = [dict(id=f.id, name=f.name, kind=f.kind, qty=f.qty, mass_each_kg=f.mass_each, mass_kg=f.mass_kg, maturity=f.maturity,
                     source=f.source, at=[list(p) for p in f.at], dims=list(f.dims) if f.dims else None, t=f.t) for f in ch.fittings]
    schedule = {}
    for m in ch.members:
        key = (m.sec.name, m.role)
        r = schedule.setdefault(key, dict(section=m.sec.name, role=m.role, name=ch.role_name.get(m.role, m.name.split(",")[0]), qty=0,
                                          length_mm=0.0, mass_kg=0.0, lengths=[]))
        r["qty"] += 1
        r["length_mm"] += m.length
        r["mass_kg"] += m.mass_kg
        r["lengths"].append(round(m.length))
    out = dict(
        id=ch.data["id"], name=ch.data["name"], revision=ch.data["revision"], material=ch.data["material"],
        composite=dict(z_bottom=comp.z_bottom, z_centroid=comp.z_centroid, z_top=comp.z_top, A=comp.A, I=comp.I_strong, I_weak=comp.I_weak,
                       J=comp.J, Z_bottom=comp.Z_bottom, Z_top=comp.Z_top, Z_weak=comp.Z_weak),
        members=members, joints=[j.__dict__ for j in ch.joints], fittings=fittings, schedule=list(schedule.values()),
        steel_kg=ch.steel_mass(), galvanising=ch.galvanising(),
        bought_kg=sum(f.mass_kg for f in ch.fittings if f.kind not in ("plate", "tube")),
        suspension=ch.suspension, stations=[dict(st, x_centre=ch.station_x(st), role=ch.role_of(st)) for st in ch.stations],
        load_cases=ch.data["load_cases"],
        results={k: v for k, v in res.items() if k != "envelope"},
        envelope={lc: sorted(({"member": m, **r} for m, r in rows.items()), key=lambda r: -r["util"])
                  for lc, rows in res["envelope"].items()},
        tyre=tr.tyre_arc(lay), params=dict({k: ch.V[k] for k in ch.data["params"]}, spare_z=ch.V["spare_z"]),
    )
    return _r(out)

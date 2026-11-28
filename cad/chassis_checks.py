"""Rows of the chassis checks (data/checks.yaml, types chassis_*), from the frame analysis in cad/chassis_fea.py."""
from __future__ import annotations

LOCAL = {"chain_lug": "chain_lug", "front_recovery": "front_recovery", "rear_recovery": "rear_recovery",
         "jacking_point": "jacking_point", "spare_posts": "spare_posts", "steady_bracket": "steady_bracket", "coupling_plate": "coupling_plate",
         "shear_panel": "shear_panel", "hinge_cheeks": "hinge_cheeks", "arm_limits": "arm_limits",
         "hinge_gussets": "hinge_gussets", "hinge_runs": "hinge_runs", "hinge_bar": "hinge_bar", "hinge_seams": "hinge_seams"}
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
                    detail=(f"{len(hs)} holes in the rails, the raisers, the drawbar members, the crossmembers, outriggers and braces. The worst, {w['id']}, {w['d']:g} mm across in {w['wall']} at X "
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
        names = [f"{h['id']} {h['member']}" for h in bad[:4]]
        return dict(limit="edge 1.25 d, weld toes 1.0 d, edge range <= CAFL", measured=len(bad), unit=f"of {len(hs)} holes", margin=-len(bad),
                    ok=not bad, governing=" and ".join([", ".join(names[:-1]), names[-1]] if len(names) > 1 else names) or f"{top['id']}, its edge range",
                    detail=(f"{len(hs) - len(bad)} of {len(hs)} holes meet the three rules. " + "".join(f"{w}. " for w in why)
                            + f"The highest range at a hole's edge is {top['peak_mpa']:.1f} MPa at {top['id']}, against {top['cafl']:.1f} MPa"))
    if c.type == "chassis_local" and c.item == "galvanising":
        g = res["galvanising"]
        rows = g["sections"]
        bad = [r for r in rows if not r["ok"]]
        w = max(rows, key=lambda r: max(r["low_depth"], r["high_depth"]))
        why = [f"{r['id']}: {'its low point ' + format(r['low_depth'], '.0f') + ' mm under its lowest opening, ' if r['low_depth'] > g['max_depth'] else ''}"
               f"{'its high point ' + format(r['high_depth'], '.0f') + ' mm over its highest, ' if r['high_depth'] > g['max_depth'] else ''}"
               f"{'its holes short of the table' if not r['size_ok'] else ''}".rstrip(", ") for r in bad]
        deep = max(w["low_depth"], w["high_depth"])
        n_holes = sum(r["holes"] for r in rows)
        ov = g.get("overlaps") or []
        ov_bad = [o for o in ov if not o["ok"]]
        ov_text = " ".join(f"{o['id']}, {o['qty']} of {o['area']:,.0f} mm2, vents {' and '.join(format(d, 'g') for d in o['vents'])} mm against "
                           f"{o['need_n']} of {o['need_d']:g} mm{' (fails)' if not o['ok'] else ''}." for o in ov)
        return dict(limit=f"each low and high point within {g['max_depth']:g} mm of an opening, each closed end's holes to the table, each sealed overlap vented",
                    measured=len(bad) + len(ov_bad), unit=f"of {len(rows)} closed sections and {len(ov)} sealed overlaps", margin=-len(bad) - len(ov_bad),
                    ok=not bad and not ov_bad,
                    governing=(", ".join([r["id"] for r in bad[:4]] + [o["id"] for o in ov_bad]) if bad or ov_bad else f"{w['id']}, {deep:.1f} mm"),
                    detail=(f"{len(rows) - len(bad)} of {len(rows)} closed sections drain and vent in every hang, rolled {g['roll']:g} deg either side down "
                            f"and pitched {g['pitches'][0]:g} to {g['pitches'][-1]:g} deg drawbar end down, through their {n_holes} holes for galvanising, "
                            f"the rails' slots and their open ends. "
                            + "".join(f"{x}. " for x in why)
                            + f"The deepest is {w['id']}'s {'low' if w['low_depth'] >= w['high_depth'] else 'high'} point, {deep:.1f} mm from its opening's edge, "
                            f"{w['low_hang'] if w['low_depth'] >= w['high_depth'] else w['high_hang']}. Sealed overlaps against the guide's pages 29 and 30: {ov_text}"))
    if c.type == "chassis_local" and c.item == "ultimate":
        g = res["governing"]["LC8u"]
        hs = [h for h in res["holes"] if not h["open"] and h.get("ultimate")]
        wh = max(hs, key=lambda h: h["ultimate"]["util"])
        u = wh["ultimate"]
        over = sorted({m for m, r in res["envelope"]["LC8u"].items() if r["util"] > 1 + 1e-9}
                      | {f"{h['id']}" for h in hs if h["ultimate"]["util"] > 1 + 1e-9})
        worst = max(g["util"], u["util"])
        return dict(limit="members <= fy on Ze, holes <= 0.85 fu on the net section, at 78.5 kN", measured=round(100 * worst, 1), unit="%",
                    margin=round(100 * (1 - worst), 1), ok=worst <= 1 + 1e-9,
                    governing=(f"{g['member']}, {g['case']}" if g["util"] >= u["util"] else f"{wh['id']} in {wh['wall']}, {u['case']}"),
                    detail=(f"At the 78.5 kN ultimate the worst member is {g['member']}, {g['eq']:.0f} MPa on its effective section against its "
                            f"{g['limit']:.0f} MPa fy at X {g['at'][0]}, {g['case']}, {g['util']:.2f}, and the worst hole {wh['id']} in {wh['wall']} at X "
                            f"{wh['x']:,.0f}, {u['mpa']:.0f} MPa on its net section against 0.85 fu, {u['limit']:.1f} MPa, {u['util']:.2f}. "
                            + (f"Over their limits: {', '.join(over)}." if over else "Every member and hole holds the ultimate pull.")))
    if c.type == "chassis_local" and c.item == "hinge_joints":
        hp = res["hinge_joints"]
        w = hp["worst"]
        fat = ", ".join(f"{f['id']} {f['range_mpa']:.1f} of {f['cafl']:.1f} MPa" for f in hp["fatigue"])
        return dict(limit="each case's limit, FAT-03 and FAT-13 within their CAFL", measured=round(100 * w["util"], 1), unit="%",
                    margin=round(100 * (1 - w["util"]), 1), ok=hp["ok"], governing=f"{w['part']}, {w['lc']}, {w['case']}",
                    detail=(f"With each hinge tied to its crossmember at the hinge bar's welds and to the rail by its cheeks, and the gussets behind "
                            f"each crossmember carrying load, the worst is {w['part']}, "
                            f"{w['mpa']:.0f} MPa against {w['limit']:.0f} MPa in {w['lc']}, {w['case']}, {w['util']:.2f}. At the roots and hinges: {fat}."))
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
        if "fat_shear" in f:                     # a weld's root, normal and shear by IIW's interaction (FAT-26, FAT-27)
            blocks = " ".join(f"{b['id'].capitalize()}'s {b['cycles'] / 1e6:g} million cycles read {b['normal_mpa']:.1f} MPa normal and "
                              f"{b['shear_mpa']:.1f} MPa along, Miner damage {b['damage']:.2f} at {b['where']}, {b['case']}." for b in f["blocks"])
            parts = " and ".join(f"{v:.2f} {k}" for k, v in f["parts"].items())
            return dict(limit=f"(sigma_w / {f['cafl']:.1f})^2 + (tau_w / {f['shear_cafl']:.1f})^2 <= 1, summed damage <= {f['miner_limit']:g}",
                        measured=round(f["range_mpa"], 1), unit="MPa", margin=round(f["cafl"] - f["range_mpa"], 1), ok=f["ok"],
                        governing=f"{f['where']}, {f['case']}",
                        detail=(f"IIW {f['iiw']}, FAT {f['fat']:g} normal to the throat and FAT {f['fat_shear']:g} along it, by IIW's "
                                f"interaction (CV 1.0): the frequent range {f['normal_mpa']:.1f} MPa normal to the throat and "
                                f"{f['shear_mpa']:.1f} MPa along it at {f['where']}, {f['util']:.2f} of their CAFLs, an equivalent normal "
                                f"range of {f['range_mpa']:.1f} MPa against {f['cafl']:.1f} MPa, and the occasional range "
                                f"{f['occasional_range_mpa']:.0f} MPa normal and {f['occasional_shear_mpa']:.0f} MPa along gives Miner damage "
                                f"{f['occasional_damage']:.2f} at {f['occasional_where']}, {f['occasional_case']}. "
                                + (f"{blocks} Summed at each weld point, the worst is {f['damage']:.2f} ({parts}) at {f['damage_where']}, "
                                   f"{f['damage_case']}." if f["blocks"] else "")))
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
        bought_kg=sum(f.mass_kg for f in ch.fittings if f.kind not in ("plate", "tube", "angles")),
        suspension=ch.suspension, stations=[dict(st, x_centre=ch.station_x(st), role=ch.role_of(st)) for st in ch.stations],
        load_cases=ch.data["load_cases"],
        results={k: v for k, v in res.items() if k != "envelope"},
        envelope={lc: sorted(({"member": m, **r} for m, r in rows.items()), key=lambda r: -r["util"])
                  for lc, rows in res["envelope"].items()},
        tyre=tr.tyre_arc(lay), params=dict({k: ch.V[k] for k in ch.data["params"]}, spare_z=ch.V["spare_z"]),
    )
    return _r(out)

"""Clearance, height and contact checks from data/checks.yaml, measured on the B-rep model.

Distances use OCCT's exact shape-to-shape distance (build123d distance_to_with_closest_points) between
every sub-solid of side A and every item of side B, so the result names the governing pair.
Overlap is the boolean intersection volume. Limits come from the data and are never adjusted here.
"""
from __future__ import annotations

import math
import time

from build123d import Compound

from .partsdb import Check, Project


def _solids(shape, label):
    """Leaf solids with readable names."""
    kids = list(shape.children) if isinstance(shape, Compound) and shape.children else []
    if not kids:
        return [(label, shape)]
    out = []
    for k in kids:
        out.extend(_solids(k, f"{label} / {k.label}" if k.label else label))
    return out


def _bbox_gap(a, b):
    A, B = a.bounding_box(), b.bounding_box()
    dx = max(0.0, A.min.X - B.max.X, B.min.X - A.max.X)
    dy = max(0.0, A.min.Y - B.max.Y, B.min.Y - A.max.Y)
    dz = max(0.0, A.min.Z - B.max.Z, B.min.Z - A.max.Z)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _volume(r) -> float:
    if r is None:
        return 0.0
    items = list(r) if isinstance(r, (list, tuple)) else [r]
    tot = 0.0
    for s in items:
        try:
            tot += float(s.volume)
        except Exception:
            pass
    return tot


def min_gap(model, a_names, b_names):
    """Smallest distance between any leaf of A and any item of B, with the pair and closest points."""
    A = []
    for n in a_names:
        for i in model.prj.select(n if isinstance(n, list) else [n]):
            b = model.built[i.iid]
            A.extend(_solids(b.shape, b.inst.label))
    B = []
    for n in b_names:
        for i in model.prj.select([n]):
            bb = model.built[i.iid]
            B.extend(_solids(bb.shape, f"{bb.inst.label} ({i.iid})"))
    best = (math.inf, None, None, None, None)
    pairs = sorted(((la, sa, lb, sb, _bbox_gap(sa, sb)) for la, sa in A for lb, sb in B), key=lambda t: t[4])
    overlap = 0.0
    for la, sa, lb, sb, g0 in pairs:
        if g0 > best[0]:
            break
        d, pa, pb = sa.distance_to_with_closest_points(sb)
        if d < best[0]:
            best = (d, la, lb, (pa.X, pa.Y, pa.Z), (pb.X, pb.Y, pb.Z))
    for la, sa, lb, sb, g0 in pairs:
        if g0 > 0:
            break
        if sa.distance_to(sb) < 1e-6:
            overlap += _volume(sa.intersect(sb))
    return best, overlap


def evaluate(prj: Project, model, checks: list[Check] | None = None) -> list[dict]:
    out = []
    for c in checks or prj.checks:
        t0 = time.time()
        if c.type == "clearance":
            groups = [[e] for e in c.each] if c.each else [c.a]
            for grp in groups:
                (gap, la, lb, pa, pb), ov = min_gap(model, grp, c.b)
                ok = ov < 1.0 and gap >= c.min_gap_mm - 1e-6
                who = model.built[prj.select(grp)[0].iid].inst.label
                out.append(dict(
                    id=c.id, sub=who if c.each else "", title=c.title, type=c.type, severity=c.severity,
                    added_by_build=c.added_by_build, a=grp, b=c.b, limit=f">= {c.min_gap_mm:g} mm",
                    measured_mm=round(gap, 1), margin_mm=round(gap - c.min_gap_mm, 1), overlap_mm3=round(ov, 1),
                    ok=ok, status=("PASS" if ok else "FAIL") if c.severity == "fail" else ("MEETS LIMIT" if ok else "BELOW LIMIT"),
                    governing=f"{la} to {lb}", points=[[round(v, 1) for v in pa], [round(v, 1) for v in pb]],
                    detail=f"gap {gap:.1f} mm (needs {c.min_gap_mm:g}), {la} to {lb}" + (f", overlap {ov:.0f} mm3" if ov >= 1 else ""),
                    why=c.why, seconds=round(time.time() - t0, 2)))
        elif c.type == "height":
            b = model.built[prj.select(c.a)[0].iid]
            bb = b.shape.bounding_box()
            add = prj.P.eval(c.add_mm, {})
            lim = prj.P.eval(c.max_z, {})
            top = bb.max.Z + add
            ok = top <= lim + 1e-6
            out.append(dict(
                id=c.id, sub="", title=c.title, type=c.type, severity=c.severity, added_by_build=c.added_by_build,
                a=c.a, b=[], limit=f"top <= Z {lim:g}", measured_mm=round(top, 1), margin_mm=round(lim - top, 1),
                overlap_mm3=0.0, ok=ok, status="PASS" if ok else "FAIL", governing=f"mattress top Z {bb.max.Z:.1f} + bedding {add:g}",
                points=[], detail=f"mattress top {bb.max.Z:.1f} + {add:g} bedding = {top:.1f} (limit {lim:g}), {lim - top:.1f} mm spare",
                why=c.why, seconds=round(time.time() - t0, 2)))
        elif c.type == "landing":
            # A must rest on B: its lowest point between min_gap_mm and max_gap_mm above B, with no overlap.
            # Above B the gap is the exact shape distance. Into B it is minus the depth of the overlap.
            A = [s for n in c.a for i in prj.select([n]) for _, s in _solids(model.built[i.iid].shape, i.label)]
            B = [(f"{i.label} ({i.iid})", s) for n in c.b for i in prj.select([n])
                 for _, s in _solids(model.built[i.iid].shape, i.label)]
            gap, gap_who, depth, depth_who, ov = math.inf, "", 0.0, "", 0.0
            for sa in A:
                for lb, sb in B:
                    if _bbox_gap(sa, sb) > gap:
                        continue
                    d = sa.distance_to(sb)
                    if d < 1e-6:
                        r = sa.intersect(sb)
                        v = _volume(r)
                        if v > 1e-3:
                            ov += v
                            parts = list(r) if isinstance(r, (list, tuple)) or hasattr(r, "__iter__") and not hasattr(r, "wrapped") else [r]
                            zs = [(p.bounding_box().min.Z, p.bounding_box().max.Z) for p in parts]
                            dz = max(z1 for _, z1 in zs) - min(z0 for z0, _ in zs)
                            if dz > depth:
                                depth, depth_who = dz, lb
                            continue
                    if d < gap:
                        gap, gap_who = d, lb
            measured, who = (-depth, depth_who) if ov >= 1.0 else (gap, gap_who)
            lo, hi = c.min_gap_mm, c.max_gap_mm
            ok = ov < 1.0 and lo - 1e-6 <= measured <= hi + 1e-6
            where = f"{abs(measured):.1f} mm {'below' if measured < 0 else 'above'} the floor surface"
            out.append(dict(
                id=c.id, sub="", title=c.title, type=c.type, severity=c.severity, added_by_build=c.added_by_build,
                a=c.a, b=c.b, limit=f"gap {lo:g} to {hi:g} mm", measured_mm=round(measured, 1),
                margin_mm=round(min(measured - lo, hi - measured), 1), overlap_mm3=round(ov, 1), ok=ok,
                status="PASS" if ok else "FAIL", governing=f"ladder foot to {who}", points=[],
                detail=f"foot {where} (needs a gap of {lo:g} to {hi:g} mm)" + (f", overlap {ov:.0f} mm3" if ov >= 1 else ""),
                why=c.why, seconds=round(time.time() - t0, 2)))
        elif c.type == "restraint":
            from .restraint import strap_loads
            res = strap_loads(prj, model, c.restraint)
            w = res["worst"]
            lc = c.restraint["lc_kg"]
            ok = w["worst_kgf"] <= lc
            out.append(dict(
                id=c.id, sub="", title=c.title, type=c.type, severity=c.severity, added_by_build=c.added_by_build,
                a=[], b=[], limit=f"<= {lc:g} kgf", measured_mm=w["worst_kgf"], margin_mm=round(lc - w["worst_kgf"], 1),
                overlap_mm3=0.0, ok=ok, status=("PASS" if ok else "FAIL") if c.severity == "fail" else ("MEETS LIMIT" if ok else "BELOW LIMIT"),
                governing=f"{w['strap']} {w['worst_case']}", points=[], restraint=res,
                detail=(f"worst strap {w['strap']} {w['worst_kgf']:.0f} kgf ({w['worst_case']}), utilisation "
                        f"{w['worst_kgf'] / lc:.2f} of the {lc:g} kg LC. Chock push in braking: "
                        + ", ".join(f"{b['bike']} {b['chock_push_kgf']:.0f} kgf" for b in res["bikes"])),
                why=c.why, seconds=round(time.time() - t0, 2)))
        elif c.type == "beam":
            # Simply supported beam under a uniform load: deflection 5 W L^3 / (384 E I), stress W L / (8 Z)
            bm = c.beam
            span = model.built[prj.select(c.a)[0].iid].info["length_m"] * 1000
            W = bm["load_kg"] * 9.81 / bm["beams"]
            E, I = bm["e_gpa"] * 1e3, bm["i_cm4"] * 1e4          # N/mm2, mm4
            d = 5 * W * span ** 3 / (384 * E * I)
            sigma = W * span / 8 / (I / (bm["depth_mm"] / 2))
            lim = span / c.span_ratio
            d0 = 5 * W * bm["baseline_span_mm"] ** 3 / (384 * E * I)
            ok = d <= lim + 1e-9
            out.append(dict(
                id=c.id, sub="", title=c.title, type=c.type, severity=c.severity, added_by_build=c.added_by_build,
                a=c.a, b=[], limit=f"sag <= span / {c.span_ratio:g} ({lim:.1f} mm)", measured_mm=round(d, 1), margin_mm=round(lim - d, 1),
                overlap_mm3=0.0, ok=ok, status=("PASS" if ok else "FAIL") if c.severity == "fail" else ("MEETS LIMIT" if ok else "BELOW LIMIT"),
                governing=f"span {span:.0f} mm, {W:.0f} N per beam, stress {sigma:.0f} MPa", points=[],
                detail=f"sag {d:.1f} mm at a {span:.0f} mm span" + (f" ({d0:.1f} mm at {bm['baseline_span_mm']:.0f} mm)" if abs(bm["baseline_span_mm"] - span) > 1 else "")
                       + f", bending stress {sigma:.0f} MPa",
                why=c.why, seconds=round(time.time() - t0, 2)))
        else:  # contact
            rows = []
            all_ok = True
            for a, b in c.pairs:
                sa, sb = model.built[prj.select([a])[0].iid].shape, model.built[prj.select([b])[0].iid].shape
                d = sa.distance_to(sb)
                ov = _volume(sa.intersect(sb)) if d < 1e-6 else 0.0
                ok = d <= c.tolerance_mm and ov < 1e-3
                all_ok &= ok
                rows.append(dict(a=a, b=b, gap_mm=round(d, 3), overlap_mm3=round(ov, 4), ok=ok))
            worst_gap = max(r["gap_mm"] for r in rows)
            worst_ov = max(r["overlap_mm3"] for r in rows)
            bad = [f"{r['a']}/{r['b']}" for r in rows if not r["ok"]]
            out.append(dict(
                id=c.id, sub="", title=c.title, type=c.type, severity=c.severity, added_by_build=c.added_by_build,
                a=[], b=[], limit="touching, no overlap", measured_mm=worst_gap, margin_mm=None, overlap_mm3=worst_ov,
                ok=all_ok, status="PASS" if all_ok else "FAIL", governing=", ".join(bad) if bad else f"{len(rows)} pairs touch",
                points=[], pairs=rows,
                detail=f"{sum(r['ok'] for r in rows)} of {len(rows)} pairs touch without overlap. Largest gap {worst_gap:.3f} mm, largest overlap {worst_ov:.4f} mm3",
                why=c.why, seconds=round(time.time() - t0, 2)))
    return out

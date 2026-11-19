"""Strap loads for the bikes along the trailer (DESIGN.md revision D), by research/03's method and load cases.

Each bike faces forward, so braking pushes it along its length into the chock and cornering pushes it
sideways. The NTC cases (0.8 g forward, 0.5 g rearward, 0.5 g sideways) are multiplied by report 03's
off-road factor of 2, and upward is 1.0 g. Strap directions come from the model's strap end points.

- Sideways: the bike's overturning moment m a h about the tyre contact line is held by the straps on the
  far side. Report 03's design case lets one strap take 60 % of it: T = 0.6 M / arm, where arm is the strap's
  moment arm about the contact line.
- Braking: the chock takes the push. If m a h is more than the bike's weight moment m g d about the front
  tyre's contact (d is the centre of gravity behind it), the rear lifts and the rear pair holds it down.
  One strap takes 60 % of the excess.
- Rearward: the two front straps share it through their forward direction cosine.
- Upward: the four main straps share the bike's weight through their vertical direction cosines.
"""
from __future__ import annotations

import math

G = 9.81


def _unit(a, b):
    d = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in d))
    return [v / L for v in d], L


def strap_loads(prj, model, spec: dict) -> dict:
    f, share = spec["factor"], spec["share"]
    cases = spec["cases"]
    rows, bikes = [], []
    for ref in ("TU", "ST"):
        b = model.built[ref]
        m = prj.parts[b.inst.part].mass.unit_kg
        pb = b.bike
        xf, zf = pb.model.front_axle
        fa = pb.point(xf, 0, zf)
        cy = fa.Y
        h = spec["cg_z"][ref]
        d = b.cog_override[0] - fa.X
        straps = []
        for iid, s in model.built.items():
            if not iid.startswith(f"13.{ref}-") or s.inst.special["strap"]["point"] == "rear_wheel":
                continue
            p, a = s.info["points"][0], s.info["points"][1]
            u, L = _unit(p, a)
            arm = abs((p[1] - cy) * u[2] - p[2] * u[1])
            r = (p[0] - fa.X, p[2])
            k = r[1] * u[0] - r[0] * u[2]               # pitch restoring arm about the front contact, + holds the rear down
            straps.append(dict(iid=iid, front=s.inst.special["strap"]["point"] != "pillion_peg_hangers", p=p, a=a, u=u,
                               length=L, arm=arm, k=k))
        M_lat = m * G * cases["lateral_g"] * f * h
        tip = m * G * (cases["forward_g"] * f * h - d)
        uz = sum(abs(s["u"][2]) for s in straps)
        for s in straps:
            lat = share * M_lat / s["arm"]
            brake = share * tip / s["k"] if (not s["front"] and tip > 0 and s["k"] > 0) else 0.0
            rear = m * G * cases["rearward_g"] * f / 2 / max(1e-6, -s["u"][0]) if s["front"] else 0.0
            up = m * G * cases["up_g"] / uz
            loads = dict(sideways=lat / G, braking=brake / G, rearward=rear / G, upward=up / G)
            case = max(loads, key=loads.get)
            rows.append(dict(strap=s["iid"], bike=ref, length_mm=round(s["length"]), roll_arm_mm=round(s["arm"]),
                             pitch_arm_mm=round(s["k"]) if not s["front"] else None,
                             **{k: round(v, 1) for k, v in loads.items()}, worst_kgf=round(loads[case], 1), worst_case=case))
        bikes.append(dict(bike=ref, mass_kg=m, cg_z_mm=h, cg_behind_front_contact_mm=round(d),
                          chock_push_kgf=round(m * cases["forward_g"] * f, 1),
                          rear_lifts=tip > 0, tip_moment_nm=round(tip / 1000, 1)))
    worst = max(rows, key=lambda r: r["worst_kgf"])
    return dict(rows=rows, bikes=bikes, worst=worst)

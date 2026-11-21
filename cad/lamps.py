"""Lamps, reflectors and the number plate, to ADR 13/00 (which takes UNECE R48/03 as its Appendix A) and VSB1 section
3.1. Places each device in data/services.yaml `lamps` in DIM-01, the side devices on their chassis stations, and checks
the counts, heights, edge distances, spacings, clearances and views that the rules set. CT-003, CT-011 and the
Electrical page show the results.
"""
from __future__ import annotations

import itertools
import json
import math
import re

import yaml

from .partsdb import DATA, ROOT

BUILD = ROOT / "build"
ADR13 = "https://www.legislation.gov.au/F2009L02867/asmade/2009-07-16/text/original/pdf"

# function: (ADR 13/00 Appendix A clause, name, lowest edge, highest edge, outer edge to the extreme outer edge at most,
# inner edges apart at least), mm. None where the clause sets no such limit.
RULES = {
    "stop": ("6.7", "Stop lamps", 350, 1500, None, 600),
    "rear_position": ("6.10", "Rear position lamps", 350, 1500, 400, 600),
    "rear_indicator": ("6.5", "Rear direction indicators", 350, 1500, 400, 600),
    "reversing": ("6.4", "Reversing lamps", 250, 1200, None, None),
    "rear_reflector": ("6.15", "Rear reflectors, triangular", 250, 900, 400, 600),
    "rear_end_outline": ("6.13", "Rear end-outline lamps", None, None, 400, None),
    "plate_lamp": ("6.8", "Number plate lamp", None, None, None, None),
    "front_position": ("6.9", "Front position lamps", 350, 1500, 150, None),
    "front_reflector": ("6.16", "Front reflectors", 250, 900, 150, None),
    "front_end_outline": ("6.13", "Front end-outline lamps", None, None, 400, None),
    "side_marker": ("6.18", "Side marker lamps", 250, 1500, None, None),
    "side_reflector": ("6.17", "Side reflectors", 250, 900, None, None),
}
REFLECTORS = {"rear_reflector", "front_reflector", "side_reflector"}
INWARD_DEG = {"front_position": 5.0, "front_reflector": 10.0}  # the inward view a trailer needs (6.9.5, 6.16.5)
END_OUTLINE_UP_DEG = 5.0                                       # 6.13.5
SIDE_FRONT_MAX, SIDE_GAP_MAX, SIDE_REAR_MAX = 3000.0, 3000.0, 1000.0  # 6.17.4.1 and 6.18.4.1, with the drawbar


def _gap(a, b) -> float:
    """Clear distance between two rectangles (u0, u1, z0, z1), negative by the smaller overlap when they overlap."""
    du = max(a[0] - b[1], b[0] - a[1])
    dz = max(a[2] - b[3], b[2] - a[3])
    if du < 0 and dz < 0:
        return max(du, dz)
    return math.hypot(max(du, 0.0), max(dz, 0.0))


def _add(out, what, clause, measured, limit, margin, ok=None):
    out.append(dict(id=f"LMP-{len(out) + 1:02d}", what=what, clause=clause, measured=measured, limit=limit,
                    margin=None if margin is None else round(margin, 1),
                    ok=bool(ok if ok is not None else margin >= -1e-6)))


def _instances(devs, V, stations) -> list[dict]:
    """Each device placed: pairs mirrored to the kerb side, side devices on both sides of each of their stations."""
    out = []
    for d in devs:
        w, h = d["size"]
        base = dict(dev=d["id"], name=d["name"], does=d["does"], colour=d["colour"], face=d["face"], mount=d["mount"],
                    z0=d["z"] - h / 2, z1=d["z"] + h / 2)
        if d["face"] == "side":
            for n, st in enumerate(d["stations"], 1):
                xc = stations[st]
                for side, s in (("kerb", -1), ("road", 1)):
                    out.append(dict(base, id=f"{d['id']}{side[0].upper()}{n}", side=side, station=st, x=xc,
                                    x0=xc - w / 2, x1=xc + w / 2, y=s * V["half_bw"]))
            continue
        x = V["body_x1"] if d["face"] == "rear" else V["body_x0"]
        sides = [("kerb" if d["y"] < 0 else "road", d["y"])] if d.get("single") else [("kerb", -d["y"]), ("road", d["y"])]
        for side, y in sides:
            out.append(dict(base, id=d["id"] + ("" if d.get("single") else side[0].upper()), side=side, x=x, y=y,
                            y0=y - w / 2, y1=y + w / 2))
    return out


def resolve(lay=None) -> dict:
    """Every device placed and every rule checked. `lay` is the solved Layout from cad/trailer.py, built here if None."""
    data = yaml.safe_load((DATA / "services.yaml").read_text(encoding="utf-8"))["lamps"]
    rep = json.loads((BUILD / "trailer" / "trailer.json").read_text(encoding="utf-8"))
    chs = json.loads((BUILD / "chassis" / "chassis.json").read_text(encoding="utf-8"))
    body = json.loads((BUILD / "body" / "body.json").read_text(encoding="utf-8"))
    if lay is None:
        from .trailer import Trailer
        lay = Trailer().layout(**rep["solved"]["overrides"])
    V, ch = lay.V, rep["chassis"]
    stations = {s["id"]: s["x_centre"] for s in chs["stations"]}
    orr = next(m for m in chs["members"] if m["role"] == "outrigger" and m["station"] == "rear")
    oh, ow = (float(v) for v in re.match(r"RHS (\d+) x (\d+)", orr["section"]).groups())
    floor_under = V["floor_z"] - V["floor_t"]
    # the outriggers' end faces: devices on them may run up to the floor's edge on a backing plate
    face = dict(y0=abs(orr["p0"][1]), y1=abs(orr["p1"][1]), z0=orr["p0"][2] - oh / 2, z1=floor_under, cap_z1=orr["p0"][2] + oh / 2)
    wd = lay.width()   # the extreme outer edges (R48 2.8): the overall width's, which leaves out the lamps and reflectors
    ek, er = wd["kerb_y"], wd["road_y"]
    I = _instances(data["devices"], V, stations)
    need = dict(reversing=2 if ch["overall_length"] > 6000 else 1, plate_lamp=1, side_marker=None, side_reflector=None)
    eo = 2 if V["body_width"] > 2100 else 0
    need.update(rear_end_outline=eo, front_end_outline=eo)
    chk: list[dict] = []
    for f, (cl, name, lo, hi, outer, inner) in RULES.items():
        fi = [i for i in I if f in i["does"]]
        n_need = need.get(f, 2)
        meas, lim, margins = [], [], []
        ok = bool(fi)
        if n_need is not None:
            meas.append(f"{len(fi)} fitted")
            lim.append(f"{n_need}")
            ok = ok and len(fi) >= n_need
        else:
            meas.append(f"{len(fi) // 2} each side")
            lim.append("by spacing")
        if fi and lo is not None:
            zlo, zhi = min(i["z0"] for i in fi), max(i["z1"] for i in fi)
            meas.append(f"{zlo:,.0f} to {zhi:,.0f} high")
            lim.append(f"{lo:,} to {hi:,}")
            margins += [zlo - lo, hi - zhi]
        if fi and outer is not None:
            d = max((i["y0"] - ek) if i["side"] == "kerb" else (er - i["y1"]) for i in fi)
            meas.append(f"outer edge {d:,.0f}")
            lim.append(f"at most {outer}")
            margins.append(outer - d)
        if fi and inner is not None:
            gap = min(i["y0"] for i in fi if i["side"] == "road") - max(i["y1"] for i in fi if i["side"] == "kerb")
            meas.append(f"inner edges {gap:,.0f} apart")
            lim.append(f"at least {inner}")
            margins.append(gap - inner)
        m = min(margins) if margins else None
        _add(chk, name, cl, ", ".join(meas), ", ".join(lim), m, ok and (m is None or m >= -1e-6))
    _more(chk, data, I, V, ch, lay, body, face, ow, floor_under)
    plate = _plate(data["plate"])
    lamps = [i for i in I if set(i["does"]) - REFLECTORS]
    reflecting = [i for i in I if set(i["does"]) & REFLECTORS]
    return dict(devices=I, table=_table(data["devices"], I), plate=plate, checks=chk, ok=all(c["ok"] for c in chk),
                n_lamps=len(lamps), n_reflectors=len(reflecting), outer_edge=dict(kerb=ek, road=er), src=ADR13,
                plate_src=data["plate"]["src"])


def _plate(p: dict) -> dict:
    return dict(p, y0=p["y"] - p["w"] / 2, y1=p["y"] + p["w"] / 2, z0=p["z"] - p["h"] / 2, z1=p["z"] + p["h"] / 2)


def _more(chk, data, I, V, ch, lay, body, face, ow, floor_under):
    """The checks beyond the per-function ones: spacing along the side, the plate, the views and the clearances."""
    side = [i for i in I if i["face"] == "side"]
    w = side[0]["x1"] - side[0]["x0"]
    xs = sorted({i["x"] for i in side})
    x0o, x1o = ch["overall_x0"], ch["overall_x1"]
    a, b = x0o + (x1o - x0o) / 3, x0o + 2 * (x1o - x0o) / 3
    front, rear = xs[0] + w / 2 - x0o, x1o - (xs[-1] - w / 2)
    gaps = [q - p for p, q in zip(xs, xs[1:])]
    mid = max(min(x - w / 2 - a, b - x - w / 2) for x in xs)
    _add(chk, "Side marker lamps and reflectors along each side", "6.17, 6.18",
         f"{front:,.0f} from the front, gaps {' and '.join(f'{g:,.0f}' for g in gaps)}, {rear:,.0f} from the rear, "
         f"{sum(1 for x in xs if a <= x - w / 2 and x + w / 2 <= b)} in the middle third",
         f"at most {SIDE_FRONT_MAX:,.0f}, {SIDE_GAP_MAX:,.0f} and {SIDE_REAR_MAX:,.0f}, one in {a:,.0f} to {b:,.0f}",
         min(SIDE_FRONT_MAX - front, SIDE_GAP_MAX - max(gaps), SIDE_REAR_MAX - rear, mid))
    p = _plate(data["plate"])
    _add(chk, "Number plate, upright on the rear wall", "VSB1 3.1", f"top {p['z1']:,.0f} high",
         f"at most {p['top_max']:,}", p["top_max"] - p["z1"])
    pl = next(i for i in I if "plate_lamp" in i["does"])
    above, off = pl["z0"] - p["z1"], abs(pl["y"] - p["y"])
    _add(chk, "Number plate lamp over the plate", "6.8", f"{above:,.0f} above its top, {off:,.0f} off its centre",
         "above it, within its width", min(above, p["w"] / 2 - off))
    cr = lay.find("AC-03").box
    under = [i for i in I if "rear_end_outline" in i["does"] and i["y1"] > cr[1] and i["y0"] < cr[4]]
    rise = (cr[3] - cr[0]) * math.tan(math.radians(END_OUTLINE_UP_DEG))
    below = min(cr[2] - i["z1"] for i in under) if under else math.inf
    view = min(cr[2] - i["z1"] - rise for i in under) if under else math.inf
    _add(chk, "Rear end-outline lamps under the outdoor unit's cradle", "6.13.4, 6.13.5",
         f"{below:,.0f} below it, the 5 degree view up clears it by {view:,.0f}",
         f"at least {data['clearance_mm']}, clear", min(below - data["clearance_mm"], view))
    fo = [i for i in I if "front_end_outline" in i["does"]]
    radius_z = V["floor_z"] + V["interior_h"] + V["roof_t"] - V["roof_front_r"]
    flat = V["half_bw"] - V["front_vert_r"]
    m1 = min(radius_z - i["z1"] for i in fo)
    m2 = min(flat - max(abs(i["y0"]), abs(i["y1"])) for i in fo)
    _add(chk, "Front end-outline lamps high on the flat front panel", "6.13.4",
         f"{m1:,.0f} below the roof's front radius, {m2:,.0f} inside the corner pieces", "below it, inside them", min(m1, m2))
    dbx = lay.find("DX-01").box
    half = max(abs(dbx[1]), abs(dbx[4]))
    worst = math.inf
    for f, deg in INWARD_DEG.items():
        for i in (i for i in I if f in i["does"]):
            inner = min(abs(i["y0"]), abs(i["y1"]))
            worst = min(worst, inner - (i["x"] - dbx[0]) * math.tan(math.radians(deg)) - half)
    _add(chk, "Front lamps and reflectors seen inward past the drawbar box", "6.9.5, 6.16.5",
         f"the 5 and 10 degree views pass {worst:,.0f} outside it", "outside it", worst)
    fz = V["floor_z"]
    walls = [dict(i, kind=i["id"]) for i in I if i["face"] in ("front", "rear") and i["z0"] >= floor_under]
    walls.append(dict(face="rear", y0=p["y0"], y1=p["y1"], z0=p["z0"], z1=p["z1"], kind="plate"))
    keep = [(o["wall"], (o["u0"], o["u1"], o["z0"] + fz, o["z1"] + fz), o["id"]) for o in body["openings"]]
    keep.append(("rear", (cr[1], cr[4], cr[2], cr[5]), "AC-03"))
    tight = min((_gap((w_["y0"], w_["y1"], w_["z0"], w_["z1"]), r), w_["kind"], k) for w_ in walls for f_, r, k in keep
                if f_ == w_["face"])
    _add(chk, "Wall-mounted devices clear of the openings and the cradle", "BDY-18",
         f"tightest {tight[0]:,.0f}, {tight[1]} to {tight[2]}", f"at least {data['clearance_mm']}", tight[0] - data["clearance_mm"])
    low = [i for i in I if i["face"] in ("front", "rear") and i["z1"] <= floor_under + 1e-6]
    fit = min(min(abs(i["y0"] if i["side"] == "road" else i["y1"]) - face["y0"], face["y1"] - abs(i["y1"] if i["side"] == "road" else i["y0"]),
                  i["z0"] - face["z0"], face["z1"] - i["z1"]) for i in low)
    caps = min(min(ow / 2 - abs(i["x0"] - i["x"]), i["z0"] - face["z0"], face["cap_z1"] - i["z1"]) for i in side)
    _add(chk, "Devices on the outriggers stay on their faces and end caps", "CT-011",
         f"{min(fit, caps):,.0f} to the nearest edge", "on the face", min(fit, caps))
    pairs = [(x, y) for f_ in ("front", "rear") for x, y in itertools.combinations([i for i in I if i["face"] == f_], 2)]
    near = min(pairs, key=lambda q: _gap((q[0]["y0"], q[0]["y1"], q[0]["z0"], q[0]["z1"]), (q[1]["y0"], q[1]["y1"], q[1]["z0"], q[1]["z1"])))
    g = _gap((near[0]["y0"], near[0]["y1"], near[0]["z0"], near[0]["z1"]), (near[1]["y0"], near[1]["y1"], near[1]["z0"], near[1]["z1"]))
    _add(chk, "Devices on one face kept apart", "CT-011", f"{g:,.0f}, {near[0]['id']} to {near[1]['id']}",
         f"at least {data['between_mm']}", g - data["between_mm"])
    th = math.radians(180 - data["rear_door_stay_deg"])
    hinge, reach = V["rear_door_y0"], V["rear_door_y0"] - V["rear_door_w"] * math.cos(th)
    d = (hinge - min(pl["y1"], hinge)) * math.tan(th) if pl["y1"] > reach else math.inf
    _add(chk, "Rear door on its stay clears the plate lamp", "BD-15",
         f"{d:,.0f} off the wall over the lamp", f"more than the lamp's {data['plate_lamp_depth_mm']}",
         d - data["plate_lamp_depth_mm"])


def _table(devs, I) -> list[dict]:
    """One row a device type for the schedules on CT-011 and the Electrical page, marked L1 onwards in data order."""
    rows = []
    for n, d in enumerate(devs, 1):
        mine = [i for i in I if i["dev"] == d["id"]]
        w, h = d["size"]
        if d["face"] == "side":
            along = ", ".join(f"{x:,.0f}" for x in sorted({i["x"] for i in mine}))
        else:
            along = f"{mine[0]['x']:,.0f}"
        side = "kerb side" if d.get("y", 0) < 0 else "road side"
        across = f"{abs(d['y']):,.0f} {side}" if d.get("single") else f"{abs(mine[-1]['y']):,.0f} each side"
        rows.append(dict(mark=f"L{n}", id=d["id"], name=d["name"], colour=d["colour"], mount=d["mount"], face=d["face"],
                         n=len(mine), does=[RULES[f][1] for f in d["does"]], clauses=[RULES[f][0] for f in d["does"]],
                         size=f"{w:.0f} x {h:.0f}", along=along, across=across,
                         height=f"{mine[0]['z0']:,.0f} to {mine[0]['z1']:,.0f}"))
    return rows

"""The tow vehicle: the LandCruiser 79 single cab with the Lovells 4,200 kg GVM kit (UTE-GARAGE.md, research report 16).

Its mass budget, axle loads, centre of gravity and static stability factor per case, and the ute checks, from
data/ute/ute.yaml. Positions are in the ute frame DIM-U1: X from the front axle centre, positive rearward, Y positive
to the road side, Z up from the ground. Axle loads follow from statics about the two axles.

Phase U1 carries the bike box as report 17's 440 kg block. With `garage` (phase U2) the designed box, its parts and
the bikes as placed in the ute garage module replace the lines marked `box: true`.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .partsdb import DATA, Params

UTE_YAML = DATA / "ute" / "ute.yaml"
GROWTH = {"estimate": 0.20, "calculated": 0.07, "spec": 0.0}
G = 9.81


def load_data() -> dict:
    return yaml.safe_load(UTE_YAML.read_text())


class Ute:
    def __init__(self, garage: dict | None = None, data: dict | None = None):
        self.d = data or load_data()
        from .inputs import Inputs
        from .partsdb import ROOT
        raw = dict(self.d["params"])
        inp = Inputs(ROOT)
        raw["coupling_z"] = inp.coupling_z()           # measurements.yaml UTE-01
        raw["ball_behind_axle"] = inp.ball_behind_axle()   # UTE-02
        self.P = Params(raw)
        self.V = self.P.values
        self.limits = {k: v["v"] for k, v in self.d["limits"].items()}
        self.garage = garage
        self.lines = []
        for ln in self.d["lines"]:
            if garage and ln.get("box"):
                continue
            self.lines.append(dict(
                id=ln["id"], item=ln["item"], kg=float(self.P.eval(ln["kg"], {})),
                x=float(self.P.eval(ln["x"], {})), y=float(self.P.eval(ln.get("y", 0), {})), z=float(self.P.eval(ln["z"], {})),
                maturity=ln["maturity"], source=ln["source"], cases=list(ln["cases"]), group="ute", box=bool(ln.get("box"))))
        if garage:
            self.lines.extend(garage["lines"])
        for ln in self.lines:
            ln["growth_pct"] = round(GROWTH[ln["maturity"]] * 100)
            ln["kg_growth"] = ln["kg"] * (1 + GROWTH[ln["maturity"]])

    # ------------------------------------------------------------------ cases
    def case(self, cid: str, growth: bool = False) -> dict:
        wb = self.V["wheelbase"]
        items = [(ln["kg_growth"] if growth else ln["kg"], ln) for ln in self.lines if cid in ln["cases"]]
        M = sum(m for m, _ in items)
        rear = sum(m * ln["x"] for m, ln in items) / wb
        front = M - rear
        cog = [sum(m * ln[k] for m, ln in items) / M for k in ("x", "y", "z")]
        half_track = (self.V["track_front"] + self.V["track_rear"]) / 4
        return dict(id=cid, mass_kg=M, front_kg=front, rear_kg=rear, front_share_pct=100 * front / M, cog=cog,
                    ssf=half_track / cog[2], towball_kg=sum(m for m, ln in items if ln["id"] == "UT-11"))

    def cases(self) -> list[dict]:
        out = []
        for c in self.d["cases"]:
            out.append(dict(c, nominal=self.case(c["id"]), growth=self.case(c["id"], True)))
        return out

    # ------------------------------------------------------------------ geometry the checks read
    def box_extent(self) -> dict:
        """Outside extent of the bike box in the ute frame: from the garage module when it is built, else the U1 block."""
        if self.garage:
            return dict(self.garage["box_extent"])
        V = self.V
        return dict(x0=V["box_x0"], x1=V["box_x1"], y0=-V["box_w"] / 2, y1=V["box_w"] / 2, z0=V["deck_z"] - 135, z1=V["deck_z"] + V["box_h"])

    def rear_most(self) -> dict:
        V, b = self.V, self.box_extent()
        cand = [(b["x1"], "bike box rear doors"), (V["ball_x"] + 60, "coupling on the towbar tongue"),
                (V["frame_x1"], "frame end")]
        x, who = max(cand)
        return dict(x=x, overhang=x - V["wheelbase"], governing=who)

    # ------------------------------------------------------------------ checks
    def checks(self) -> list[dict]:
        V, L = self.V, self.limits
        cases = {c["id"]: c for c in self.cases()}
        out = []
        for c in self.d["checks"]:
            row = dict(id=c["id"], title=c["title"], type=c["type"], severity=c["severity"], why=c["why"])
            t = c["type"]
            if t in ("mass", "gcm", "wheel"):
                bases = ["nominal", "growth"] if c.get("basis", "nominal") == "both" else [c.get("basis", "nominal")]
                worst = None
                for cid in c["cases"]:
                    for bs in bases:
                        r = cases[cid][bs]
                        if t == "gcm":
                            v, lim, low = r["mass_kg"] + V["trailer_atm"] - r["towball_kg"], L["gcm_kg"], False
                        elif t == "wheel":
                            v, lim, low = r["rear_kg"] / 2, min(L["wheel_rating_kg"], L["tyre_rating_kg"]), False
                        else:
                            q = c["quantity"]
                            v = {"mass": r["mass_kg"], "front": r["front_kg"], "rear": r["rear_kg"],
                                 "front_share": r["front_share_pct"], "cog_z": r["cog"][2]}[q]
                            lim = L[c["limit"]]
                            low = q == "front_share"
                        m = v - lim if low else lim - v
                        if worst is None or m < worst[0]:
                            worst = (m, v, lim, cid, bs, low)
                m, v, lim, cid, bs, low = worst
                unit = "%" if c.get("quantity") == "front_share" else ("mm" if c.get("quantity") == "cog_z" else "kg")
                name = next(x["name"] for x in self.d["cases"] if x["id"] == cid)
                row.update(limit=f"{'>=' if low else '<='} {lim:,.0f} {unit}", measured=round(v, 1), unit=unit, margin=round(m, 1),
                           ok=m >= -1e-6, governing=f"{cid} {name} ({'with growth' if bs == 'growth' else 'no growth'})",
                           detail=(f"worst case {cid} {name}, {'with growth' if bs == 'growth' else 'no growth'}: {v:,.1f} {unit}"
                                   + (f" with a {V['trailer_atm']:,.0f} kg trailer" if t == "gcm" else "")
                                   + f", margin {m:,.1f} {unit}"))
            elif t == "towball":
                lim = min(L["towball_plan_kg"], L["towball_rating_kg"])
                v = V["towball_design"]
                row.update(limit=f"<= {lim:.0f} kg", measured=v, unit="kg", margin=lim - v, ok=v <= lim, governing="towball design load",
                           detail=f"{v:.0f} kg on the ball against the plan's {L['towball_plan_kg']:.0f} kg and the towbar's {L['towball_rating_kg']:.0f} kg")
            elif t == "width":
                b = self.box_extent()
                w = b["y1"] - b["y0"]
                lim = L[c["limit"]]
                row.update(limit=f"<= {lim:.0f} mm", measured=round(w, 1), unit="mm", margin=round(lim - w, 1), ok=w <= lim + 1e-6,
                           governing="bike box outside width", detail=f"{w:.0f} mm outside, cab {V['cab_width']:.0f} mm")
            elif t == "overhang":
                r = self.rear_most()
                lim = L[c["limit"]]
                row.update(limit=f"<= {lim:.0f} mm", measured=round(r["overhang"], 1), unit="mm", margin=round(lim - r["overhang"], 1),
                           ok=r["overhang"] <= lim + 1e-6, governing=r["governing"],
                           detail=f"{r['overhang']:.0f} mm behind the rear axle at the {r['governing']}")
            elif t == "ssf":
                ref = L["ssf_reference"]
                rows = [(cid, cases[cid]["nominal"]["ssf"]) for cid in c["cases"]]
                cid, v = min(rows, key=lambda t: t[1])
                b = cases["UCB"]["nominal"]["ssf"]
                row.update(limit=f"reported, against {ref:.2f}", measured=round(v, 3), unit="", margin=round(v - ref, 3), ok=v >= ref,
                           governing=f"{cid}", detail=(f"lowest {v:.3f} ({cid}), against {ref:.2f} in report 17 with the bikes in the trailer "
                                                        f"({b:.3f} in this model's reference case UCB). " +
                                                        ", ".join(f"{k} {s:.3f}" for k, s in rows)))
            elif t == "coupling":
                lo, hi = L["coupling_window_mm"]
                a, b = V["coupling_z"] - V["coupling_tol"], V["coupling_z"] + V["coupling_tol"]
                ok = lo <= a and b <= hi
                row.update(limit=f"{lo:.0f} to {hi:.0f} mm", measured=V["coupling_z"], unit="mm", margin=round(min(a - lo, hi - b), 1), ok=ok,
                           governing="the upper tolerance" if b > hi else "inside", detail=(
                               f"{V['coupling_z']:.0f} mm plus or minus {V['coupling_tol']:.0f} mm gives {a:.0f} to {b:.0f} mm against "
                               f"{lo:.0f} to {hi:.0f} mm" + (f", so set the tongue for {V['coupling_z']:.0f} mm, minus {V['coupling_tol']:.0f} "
                                                              f"or plus {hi - V['coupling_z']:.0f} mm" if b > hi else "")))
            elif t == "cab":
                gap = self.box_extent()["x0"] - V["cab_back_x"]
                lim = L[c["limit"]]
                row.update(limit=f">= {lim:.0f} mm", measured=round(gap, 1), unit="mm", margin=round(gap - lim, 1), ok=gap >= lim - 1e-6,
                           governing="box front wall to the back of the cab", detail=f"{gap:.0f} mm from the cab's back to the box's front wall")
            elif t == "towing":
                v, lim = V["trailer_atm"], L["braked_towing_kg"]
                row.update(limit=f"<= {lim:.0f} kg", measured=v, unit="kg", margin=lim - v, ok=v <= lim, governing="trailer ATM target",
                           detail=f"{v:.0f} kg trailer ATM target against {lim:.0f} kg braked")
            else:
                raise ValueError(f"unknown ute check type {t}")
            row["status"] = ("PASS" if row["ok"] else "FAIL") if c["severity"] == "fail" else ("MEETS LIMIT" if row["ok"] else "REPORTED")
            out.append(row)
        return out

    # ------------------------------------------------------------------ report
    def report(self) -> dict:
        cases = self.cases()
        tare = next(c for c in cases if c["id"] == "UC1")
        return dict(id=self.d["id"], name=self.d["name"], revision=self.d["revision"], params=dict(self.V), limits=self.limits,
                    limit_sources={k: v["src"] for k, v in self.d["limits"].items()}, lines=self.lines, cases=cases,
                    checks=self.checks(), box_extent=self.box_extent(), rear_most=self.rear_most(),
                    unladen_kg=tare["nominal"]["mass_kg"], garage=bool(self.garage))

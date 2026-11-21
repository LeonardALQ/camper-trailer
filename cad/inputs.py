"""Measured inputs (data/measurements.yaml) and the design rules that turn them into parameters.

Each input has an estimate and a measured slot. The value in use is the measured one when present. The rules
below are the `thresholds` in the data, written out as arithmetic. They re-solve parameters (the bike spacing,
the bed beam height, the towball target, the wheel choice) rather than only flag them, and
each rule records what it did so the site can show it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Constants of the rules, with their source (UTE-GARAGE.md unless stated). The bikes ride in the ute's box.
BASE_SPACING = 760          # bike spacing
ST_BAR_REACH = 396          # Street Triple bar end from its centreline (owner's 792 mm width / 2)
CLR03_GAP = 30              # UGC-01 limit (the trailer garage's CLR-03)
MAX_SPACING = 780           # largest spacing at which the Street Triple's belly pan keeps 15 mm from the kerb tool chest (UGC-02)
BOX_HEIGHT = 1460           # inside height of the ute's bike box to the roof bows
CHOCK_RISE = 25
CF_EFF_MAX = 200            # Cruisemaster's C/F chart limit on C/F - ET for the 4,500 kg XT Air tandem (report 09)


@dataclass
class Input:
    id: str
    group: str
    title: str
    how: str
    unit: str
    estimate: Any
    estimate_src: str
    measured: Any
    measured_date: Any
    affects: list[str]
    thresholds: list[dict]
    stage: str = ""
    range: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "measured" if self.measured is not None else ("estimate" if self.estimate is not None else "unknown")

    @property
    def value(self):
        """The measured value when there is one, else the estimate. An input with several values may be measured in
        part: a value not measured yet (null in the list) keeps its estimate."""
        if isinstance(self.measured, list) and isinstance(self.estimate, list):
            return [e if m is None else m for m, e in zip(self.measured, self.estimate)]
        return self.measured if self.measured is not None else self.estimate


class Inputs:
    def __init__(self, root: Path):
        raw = yaml.safe_load((root / "data" / "measurements.yaml").read_text())
        self.items: dict[str, Input] = {}
        for d in raw["inputs"]:
            known = {"id", "group", "part", "title", "how", "unit", "estimate", "measured", "affects", "thresholds", "order",
                     "stage", "range", "covers"}
            extra = set(d) - known
            if extra:
                raise ValueError(f"measurement {d.get('id')}: unknown keys {sorted(extra)}")
            m = d.get("measured") or {}
            self.items[d["id"]] = Input(
                id=d["id"], group=d["group"], title=d["title"], how=d["how"], unit=d["unit"],
                estimate=d["estimate"].get("v"), estimate_src=d["estimate"].get("src", ""), measured=m.get("v"),
                measured_date=m.get("date"), affects=d.get("affects", []), thresholds=d.get("thresholds", []),
                stage=d.get("stage", ""), range=d.get("range") or {},
                extra={k: d[k] for k in ("order", "covers", "part") if k in d} | ({"note": m["note"]} if m.get("note") else {}))
        self.outcomes: dict[str, str] = {}
        self.ranges: dict[str, dict] = {}

    def v(self, iid):
        return self.items[iid].value

    def note(self, iid, text):
        self.outcomes[iid] = text

    # -- the garage and bed module ----------------------------------------------
    def module_overrides(self, use_solved: bool = True) -> dict[str, float]:
        """Module parameters that follow from the bike, chock and pannier measurements."""
        w = self.v("TU-01")
        half = w / 2
        limit_half = BASE_SPACING - ST_BAR_REACH - CLR03_GAP
        fairing_excess = max(0.0, half - limit_half)
        pegs = (self.v("TU-07") + self.v("ST-01")) / 2
        peg_excess = max(0.0, pegs - (BASE_SPACING - CLR03_GAP))
        grow = max(fairing_excess, peg_excess)
        spacing = BASE_SPACING + grow
        self.rule_spacing = spacing
        self.solved = None
        if grow and use_solved:
            from .solve import cached
            self.solved = cached()
            if self.solved:
                spacing = self.solved["bike_spacing"]
        max_spacing = MAX_SPACING
        if fairing_excess:
            txt = f"{w:.0f} mm is over 668 mm, so the rule grows the spacing by {fairing_excess:.0f} mm to {self.rule_spacing:.0f} mm"
        else:
            txt = f"{w:.0f} mm is within 668 mm, so the width keeps the 760 mm spacing"
        if self.solved:
            txt += (f". The geometry sets it at {spacing:.0f} mm, where CLR-03 measures {self.solved['clr03_gap']:.1f} mm "
                    f"({self.solved['governing']})")
        elif grow:
            txt += f". The geometric solve has not run yet, so the rule's {spacing:.0f} mm is in use"
        if spacing > max_spacing:
            txt += (f". The box width is fixed and {spacing:.0f} mm is over the {max_spacing:.0f} mm that fits beside the kerb "
                    "tool chest, so UGC-02 fails and the box layout needs redesigning")
        else:
            txt += f". The box width is fixed, and spacings up to {max_spacing:.0f} mm fit beside the kerb tool chest"
        self.spacing_fits = spacing <= max_spacing
        self.note("TU-01", txt)
        cb_top = self.v("TU-09")
        self.note("TU-09", f"crash bar envelope up to {cb_top:.0f} mm, " + ("below 970 mm, so the Street Triple's bar end passes over it"
                  if cb_top <= 970 else "above 970 mm, so the bars may meet the Street Triple's bar end. The spacing solve re-measures it"))
        top = max(self.v("TU-03"), self.v("TU-04"))
        gov = "screen" if self.v("TU-03") >= self.v("TU-04") else "folded mirrors"
        room = BOX_HEIGHT - CHOCK_RISE - top
        self.note("TU-03", f"the {gov} at {top:.0f} mm stand {room:.0f} mm under the box's {BOX_HEIGHT} mm roof bows with the front wheel "
                           f"{CHOCK_RISE} mm up in the chock" + ("" if room >= 15 else ", under the 15 mm UGC-02 asks for: the walls must grow"))
        self.note("TU-04", "below the screen, so the screen sets the height" if self.v("TU-04") <= self.v("TU-03")
                  else "above the screen, so the mirrors set the height")
        self.note("TU-07", f"half the two peg widths add to {pegs:.0f} mm, {'over' if peg_excess else 'within'} 730 mm")
        self.note("ST-01", self.outcomes["TU-07"])
        nose = self.v("CHK-01")
        self.note("CHK-01", f"front tyres' leading edges at module X {nose:.0f}, that far behind the box's front wall")
        self.note("TU-02", f"Tuareg modelled {self.v('TU-02'):.0f} mm long. UGC-02 measures the gap to the stowed ramp")
        self.note("TU-05", f"pannier outer faces {self.v('TU-05') / 2:.0f} mm either side of the bike's centreline. UGC-02 measures them "
                           "against the road-side wall and UGC-03 against the barn door portal")
        self.note("TU-06", "pannier envelope {:.0f} long and {:.0f} high, front edge {:.0f} behind the front axle, bottom {:.0f} off the floor".format(*self.v("TU-06")))
        return dict(bike_spacing=spacing, front_tyre_x=nose)

    def patch_parts(self, parts: dict):
        """Bike envelope values that come straight from measurements."""
        tu = parts["BIKE-TU"].geometry.params
        est = tu["estimates"]
        est["fairing_half_width"]["v"] = self.v("TU-01") / 2
        cb = est["crash_bars"]
        cb["z"] = [cb["z"][0], self.v("TU-09")]
        est["peg_tip_y"]["v"] = self.v("TU-07") / 2
        tu["owner"]["width_with_bags"] = self.v("TU-05")
        L, H, x0, z0 = self.v("TU-06")
        pn = est["panniers"]
        pn["outer_y"] = self.v("TU-05") / 2
        pn["x"] = [x0, x0 + L]
        pn["z"] = [z0, z0 + H]
        mz = est["mirror_folded"]["z"]
        est["mirror_folded"]["z"] = [min(mz[0], self.v("TU-04") - 10), self.v("TU-04")]
        tu["length"] = self.v("TU-02")
        tu["owner"]["length"] = self.v("TU-02")
        tu["screen_top"]["z"] = self.v("TU-03")
        tu["owner"]["height"] = self.v("TU-03")
        parts["BIKE-ST"].geometry.params["estimates"]["peg_tip_y"]["v"] = self.v("ST-01") / 2

    # -- the trailer -----------------------------------------------------------------
    def coupling_z(self) -> float:
        z = self.v("UTE-01")
        ok = 370 <= z <= 440
        self.note("UTE-01", f"coupling point at Z {z:.0f}" + ("" if ok else ", outside 370 to 440 mm: choose a different tongue"))
        return z

    def ball_behind_axle(self) -> float:
        a = self.v("UTE-02")
        self.note("UTE-02", f"ball {a:.0f} mm behind the ute's rear axle in the ute's axle loads and the bike box's sweep")
        return a

    def wheel(self, wheel: dict) -> dict:
        """The trailer's own wheel (report 09). WHL-01 is its load rating, which MAS-09 checks against the per-wheel
        load that MAS-06 uses with the growth allowance."""
        r = self.v("WHL-01")
        st = self.items["WHL-01"].status
        self.note("WHL-01", f"{r:.0f} kg per wheel ({st}). MAS-09 checks it against 1.2 times the axle group load with growth, over four wheels")
        return dict(wheel, rating_kg=r, rating_status=st)

    def supplier(self, atm: float, towball: float) -> dict:
        gtm, incl = self.v("SUP-01"), bool(self.v("SUP-02"))
        need = 1.2 * (atm - towball)
        margin = f", {need - gtm:.0f} kg short" if gtm < need else f", {gtm - need:.0f} kg to spare"
        self.note("SUP-01", f"MAS-02 limit {gtm:.0f} kg. The 120 % rule at the ATM needs {need:.0f} kg, {need / 2:.0f} kg per axle{margin}")
        answered = self.items["SUP-02"].status == "measured"
        self.note("SUP-02", "ratings include the 120 % rule, so MAS-02 checks the axle load itself" if incl else
                  f"{'ratings do not' if answered else 'not known to'} include the 120 % rule, so MAS-02 checks 1.2 times the axle load")
        return dict(kit_gtm=gtm, includes_120=incl, need_kg=need)

    def cf(self, offset: float, tyre_w: float) -> float:
        cf = self.v("SUP-04")
        eff = cf - offset
        side = eff - tyre_w / 2
        txt = (f"C/F {cf:.0f} mm with ET{offset:+.0f}: effective C/F {eff:.0f} mm, "
               + ("within" if eff <= CF_EFF_MAX else "OVER") + f" Cruisemaster's {CF_EFF_MAX:.0f} mm limit for the 4,500 kg XT Air tandem. "
               f"The tyre's inner sidewall sits {side:.0f} mm outside the rail" + (", under the 40 mm report 06 asks for" if side < 40 else ""))
        self.note("SUP-04", txt)
        return cf

    def weighed(self) -> list[dict]:
        """Weighbridge stages, cumulative: the stage's own mass is its reading less the stage before."""
        out, prev = [], 0.0
        for iid in ("TW-01", "TW-02", "TW-03"):
            it = self.items[iid]
            if it.measured is None:
                break
            out.append(dict(id=iid, stage=it.extra["covers"], mass_kg=it.measured - prev))
            prev = it.measured
        return out

    # -- the acceptable ranges ---------------------------------------------------
    def resolve_ranges(self, refs: dict):
        """Each input's `range` as numbers. A side given as {ref: name} takes the model's figure from `refs`, and
        {ref, rel} spans that figure plus and minus `rel`. A side worked out from the model is rounded inwards to a
        whole number, so a value on the boundary is inside. A reference the model does not give leaves the side open."""
        def inward(v, up: bool):
            return None if v is None else (math.ceil(v - 1e-9) if up else math.floor(v + 1e-9))

        def side(v, up: bool):
            return inward(refs.get(v["ref"]), up) if isinstance(v, dict) else v
        self.ranges = {}
        for it in self.items.values():
            r = it.range
            if "rel" in r:
                ref = refs.get(r["ref"])
                lo, hi = (None, None) if ref is None else (inward(ref * (1 - r["rel"]), True), inward(ref * (1 + r["rel"]), False))
                self.ranges[it.id] = dict(min=lo, max=hi, src=r.get("src", ""), reference=None if ref is None else round(ref, 1))
            else:
                self.ranges[it.id] = dict(min=side(r.get("min"), True), max=side(r.get("max"), False), src=r.get("src", ""),
                                          reference=None)
        return self.ranges

    @staticmethod
    def outside(value, rng: dict) -> list[str]:
        """Which values break the range: 'low' or 'high' for each one (one per value for a list input), or ''."""
        vals = value if isinstance(value, list) else [value]
        out = []
        for k, v in enumerate(vals):
            lo, hi = (b[k] if isinstance(b, list) else b for b in (rng.get("min"), rng.get("max")))
            out.append("" if v is None else "low" if lo is not None and v < lo else "high" if hi is not None and v > hi else "")
        return out

    def report(self) -> list[dict]:
        if not self.ranges:
            self.resolve_ranges({})
        rows = []
        for it in self.items.values():
            rows.append(dict(id=it.id, group=it.group, title=it.title, how=it.how, unit=it.unit, estimate=it.estimate,
                             estimate_src=it.estimate_src, measured=it.measured, measured_date=str(it.measured_date) if it.measured_date else None,
                             status=it.status, value=it.value, affects=it.affects, thresholds=it.thresholds,
                             outcome=self.outcomes.get(it.id, ""), stage=it.stage, range=self.ranges[it.id], **it.extra))
        return rows

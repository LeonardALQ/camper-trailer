"""Measured inputs (data/measurements.yaml) and the design rules that turn them into parameters.

Each input has an estimate and a measured slot. The value in use is the measured one when present. The rules
below are the `thresholds` in the data, written out as arithmetic. They re-solve parameters (the bike spacing,
the bed beam height, the towball target, the wheel choice) rather than only flag them, and
each rule records what it did so the site can show it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Constants of the rules, with their source (DESIGN.md unless stated)
BASE_SPACING = 760          # bike spacing
ST_BAR_REACH = 396          # Street Triple bar end from its centreline (owner's 792 mm width / 2)
CLR03_GAP = 30              # CLR-03 limit
BASE_GARAGE = 2330          # revision D: garage length and width are fixed by the body
MAX_SPACING = 780           # revision D: largest spacing at which the Street Triple's kerb-side straps keep 15 mm from the stowed ramp (CLR-10)
BASE_BEAM = 1460
CHOCK_RISE = 25
BEAM_MARGIN = 45            # 1,460 = 1,390 + 25 + 45
DRIVER_KG = 75              # weighbridge driver (estimate)
CF_EFF_MAX = 200            # Cruisemaster's C/F chart limit on C/F - ET for the 4,500 kg XT Air tandem (report 09)
DRIVER_X = 1150             # behind the front axle (report 07 occupant position)


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
    extra: dict = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "measured" if self.measured is not None else ("estimate" if self.estimate is not None else "unknown")

    @property
    def value(self):
        return self.measured if self.measured is not None else self.estimate


class Inputs:
    def __init__(self, root: Path):
        raw = yaml.safe_load((root / "data" / "measurements.yaml").read_text())
        self.items: dict[str, Input] = {}
        for d in raw["inputs"]:
            known = {"id", "group", "title", "how", "unit", "estimate", "measured", "affects", "thresholds", "order", "stage"}
            extra = set(d) - known
            if extra:
                raise ValueError(f"measurement {d.get('id')}: unknown keys {sorted(extra)}")
            m = d.get("measured") or {}
            self.items[d["id"]] = Input(
                id=d["id"], group=d["group"], title=d["title"], how=d["how"], unit=d["unit"],
                estimate=d["estimate"].get("v"), estimate_src=d["estimate"].get("src", ""), measured=m.get("v"),
                measured_date=m.get("date"), affects=d.get("affects", []), thresholds=d.get("thresholds", []),
                extra={k: d[k] for k in ("order", "stage") if k in d} | ({"note": m["note"]} if m.get("note") else {}))
        self.outcomes: dict[str, str] = {}

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
            txt += (f". The garage width is fixed and {spacing:.0f} mm is over the {max_spacing:.0f} mm that fits beside the kerb-side "
                    "stowage, so CLR-10 fails and the layout needs redesigning")
        else:
            txt += f". The garage width is fixed, and spacings up to {max_spacing:.0f} mm fit beside the kerb-side stowage"
        self.spacing_fits = spacing <= max_spacing
        self.note("TU-01", txt)
        cb_top = self.v("TU-09")
        self.note("TU-09", f"crash bar envelope up to {cb_top:.0f} mm, " + ("below 970 mm, so the Street Triple's bar end passes over it"
                  if cb_top <= 970 else "above 970 mm, so the bars may meet the Street Triple's bar end. The spacing solve re-measures it"))
        self.note("TU-07", f"half the two peg widths add to {pegs:.0f} mm, {'over' if peg_excess else 'within'} 730 mm")
        self.note("ST-01", self.outcomes["TU-07"])
        top = max(self.v("TU-03"), self.v("TU-04"))
        beam = max(BASE_BEAM, top + CHOCK_RISE + BEAM_MARGIN)
        gov = "screen" if self.v("TU-03") >= self.v("TU-04") else "folded mirrors"
        self.note("TU-03", f"the {gov} at {top:.0f} mm need the beam underside at {top + CHOCK_RISE + BEAM_MARGIN:.0f} mm, so it stays at "
                           f"{beam:.0f} mm" if beam == BASE_BEAM else f"the {gov} at {top:.0f} mm raise the beam underside to {beam:.0f} mm")
        self.note("TU-04", "below the screen, so the screen sets the beam height" if self.v("TU-04") <= self.v("TU-03")
                  else "above the screen, so the mirrors set the beam height")
        nose = self.v("CHK-01")
        self.note("CHK-01", f"front tyres' leading edges at X {nose:.0f}, that far behind partition A")
        self.note("TU-02", f"Tuareg modelled {self.v('TU-02'):.0f} mm long. CLR-06 measures the gap to the rear door")
        self.note("TU-05", f"pannier outer faces {self.v('TU-05') / 2:.0f} mm either side of the bike's centreline. CLR-04 measures them "
                           "against the road-side wall and CLR-09 against the rear door's road-side jamb")
        self.note("TU-06", "pannier envelope {:.0f} long and {:.0f} high, front edge {:.0f} behind the front axle, bottom {:.0f} off the floor".format(*self.v("TU-06")))
        return dict(bike_spacing=spacing, beam_underside_z=beam, front_tyre_x=nose)

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

    # -- the car -------------------------------------------------------------------
    def car(self, car: dict) -> dict:
        """The car data with the weighbridge, pin and gear inputs applied."""
        import copy
        c = copy.deepcopy(car)
        F, R = self.v("CAR-01"), self.v("CAR-02")
        L = c["wheelbase_mm"]["v"]
        kerb = F + R - DRIVER_KG
        front = (F - DRIVER_KG * (L - DRIVER_X) / L) / kerb
        st = "measured" if self.items["CAR-01"].status == "measured" and self.items["CAR-02"].status == "measured" else "estimate"
        c["kerb_kg"] = {"v": kerb, "src": f"CAR-01 + CAR-02 less a {DRIVER_KG} kg driver ({st})"}
        c["budget"]["front_share_of_kerb"] = {"v": front, "src": f"From CAR-01 and CAR-02 ({st})"}
        a = self.v("CAR-05")
        c["budget"]["ball_behind_axle_mm"] = {"v": a, "src": "CAR-05"}
        if self.items["CAR-05"].status == "measured":
            c["ball_behind_axle_mm"] = {"v": [a, a], "src": "CAR-05, measured"}
        c["budget"]["planned_gear_kg"] = {"v": self.v("CAR-06"), "src": "CAR-06"}
        self.note("CAR-01", f"kerb mass {kerb:.0f} kg with {100 * front:.1f} % on the front axle")
        self.note("CAR-02", self.outcomes["CAR-01"])
        self.note("CAR-05", f"lever arm {a:.0f} mm in the load budget, bumper {a - c['rear_overhang_mm']['v']:.0f} mm ahead of the ball")
        return c

    def towball_target(self, car: dict, rating: float) -> tuple[float, str]:
        """Highest towball load keeping the rear axle within its limit with the planned gear, capped at the rating."""
        from .trailer import car_axles
        g = car["budget"]["planned_gear_kg"]["v"]
        lo, hi = 0.0, 600.0
        for _ in range(60):
            mid = (lo + hi) / 2
            ax = car_axles(car, mid)
            rear = ax["rear_kg"] + g * car["budget"]["gear_behind_front_axle_mm"]["v"] / car["wheelbase_mm"]["v"]
            if rear <= car["rear_axle_limit_kg"]["v"]:
                lo = mid
            else:
                hi = mid
        target = min(lo, rating)
        why = f"{lo:.0f} kg keeps the rear axle at 1,600 kg with {g:.0f} kg of gear" + (f", capped at the {rating:.0f} kg rating" if lo > rating else "")
        self.note("CAR-06", f"towball target {target:.0f} kg: {why}")
        return target, why

    # -- the trailer -----------------------------------------------------------------
    def coupling_z(self) -> float:
        z = self.v("CAR-04")
        ok = 370 <= z <= 440
        self.note("CAR-04", f"coupling point at Z {z:.0f}" + ("" if ok else ", outside 370 to 440 mm: choose a different tongue"))
        self.note("CAR-03", f"unladen {self.v('CAR-03'):.0f} mm against {z:.0f} mm laden")
        return z

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
            out.append(dict(id=iid, stage=it.extra["stage"], mass_kg=it.measured - prev))
            prev = it.measured
        return out

    def report(self) -> list[dict]:
        rows = []
        for it in self.items.values():
            rows.append(dict(id=it.id, group=it.group, title=it.title, how=it.how, unit=it.unit, estimate=it.estimate,
                             estimate_src=it.estimate_src, measured=it.measured, measured_date=str(it.measured_date) if it.measured_date else None,
                             status=it.status, value=it.value, affects=it.affects, thresholds=it.thresholds,
                             outcome=self.outcomes.get(it.id, ""), **it.extra))
        return rows

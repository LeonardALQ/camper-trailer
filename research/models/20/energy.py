"""Report 20 energy model for the home trailer.

Reads loads.yaml beside this file, builds a one-minute power trace for every load in each design case,
converts every load to battery-bus power (inverter loss at the actual load, inverter idle or search mode,
DC-DC converter loss and idle), and prints the figures decision H3 needs.

Cases. A load gives a spec for "hot" and "cold". The variants fall back to those unless the load
overrides them: hot_diesel falls back to hot, cold_diesel and cold_hp fall back to cold.

Run: timeout 120 uv run -q --with pyyaml python energy.py > energy.out
"""

import itertools
import math
import pathlib

import yaml

MINUTES = 1440
HERE = pathlib.Path(__file__).parent
CASES = {
    "hot": "Design hot day, all electric: hot water from the Combi D 6 E's 230 V element",
    "hot_diesel": "Design hot day, hot water from the Combi D 6 E on diesel",
    "cold_diesel": "Design cold day, Combi D 6 E heats the cabin and the water on diesel (as designed, H7)",
    "cold_hp": "Design cold day, all electric: heat pump heating, hot water from the element",
}
FALLBACK = {"hot": "hot", "hot_diesel": "hot", "cold_diesel": "cold", "cold_hp": "cold"}
COLD_NIGHT = (17.0, 31.0)  # 17:00 to 07:00, 14 h (report 19)


def spec_for(load, key):
    if key in load:
        return load[key] or {}
    return load.get(FALLBACK[key]) or {}


def add_span(trace, start_h, minutes, watts):
    first = int(round(start_h * 60))
    for m in range(first, first + int(round(minutes))):
        trace[m % MINUTES] += watts


def hot_sun_w_m2(hour):
    return max(0.0, 1000.0 * math.sin(math.pi * (hour - 6.0) / 12.0))


def cold_outside_c(hour):
    if 7.0 <= hour <= 17.0:
        return -5.0 + 18.0 * math.sin(math.pi * (hour - 7.0) / 10.0)
    return -5.0


def heat_need_w(hour, thermal):
    """Heat to add on the cold day's daytime hours (report 20 estimate from report 19's envelope and gains)."""
    sun = 0.4 * hot_sun_w_m2(hour) if 7.0 <= hour <= 17.0 else 0.0
    gains = thermal["internal_gain_day_w"] if 7 <= hour < 22 else thermal["internal_gain_night_w"]
    heat = (thermal["ua_w_per_k"] * (thermal["inside_cold_c"] - cold_outside_c(hour))
            - thermal["solar_gain_w_per_w_m2"] * sun - gains)
    return max(0.0, heat)


def heating_electric_w(hour, thermal):
    """Heat-pump input for the same hours, with report 19's COP rising from -5 C."""
    cop = min(thermal["cop_heat_max"],
              thermal["cop_heat_at_minus5c"] + thermal["cop_heat_rise_per_k"] * (cold_outside_c(hour) + 5.0))
    return heat_need_w(hour, thermal) / cop


def profile_trace(name, thermal, window):
    shape = {
        "flat": lambda h: 1.0,
        "heating": lambda h: heating_electric_w(h, thermal),
        "heat_need": lambda h: heat_need_w(h, thermal),
    }[name]
    first, last = window
    return [shape(m / 60.0) if first <= m / 60.0 < last else 0.0 for m in range(MINUTES)]


def load_trace(spec, thermal):
    """Power in W for each minute, on the load's own side, before standby."""
    trace = [0.0] * MINUTES
    for start_h, minutes, watts in spec.get("events", []):
        add_span(trace, start_h, minutes, watts)
    for start_h, end_h, watts in spec.get("runs", []):
        add_span(trace, start_h, (end_h - start_h) * 60.0, watts)
    if "hourly_w" in spec:
        for m in range(MINUTES):
            trace[m] += spec["hourly_w"][m // 60]
    if "kwh" in spec:
        shape = profile_trace(spec.get("profile", "flat"), thermal, spec.get("profile_window", (0, 24)))
        if spec["kwh"] == "auto":
            trace = [t + s * spec.get("scale", 1.0) for t, s in zip(trace, shape)]
        elif sum(shape) > 0:
            scale = spec["kwh"] * 1000.0 * 60.0 / sum(shape)
            trace = [t + s * scale for t, s in zip(trace, shape)]
    return trace


def with_standby(trace, standby_w):
    return [w if w > 0 else standby_w for w in trace]


def kwh(trace):
    return sum(trace) / 60.0 / 1000.0


def clock(hour):
    hour %= 24
    return f"{int(hour):02d}:{int(round(hour % 1 * 60)) % 60:02d}"


class Inverter:
    """Loss = P0 + a P + b P^2, fitted to the zero-load power and the maximum efficiency."""

    def __init__(self, spec):
        self.spec = spec
        self.p0 = spec["no_load_w"]
        self.b = self.p0 / spec["p_at_max_efficiency_w"] ** 2
        self.a = (1.0 / spec["max_efficiency"] - 1.0) - 2.0 * math.sqrt(self.p0 * self.b)

    def dc_w(self, ac_w, awake):
        if not awake:
            return self.spec.get("search_w", 0.0)
        return ac_w + self.p0 + self.a * ac_w + self.b * ac_w ** 2

    def efficiency(self, ac_w):
        return ac_w / self.dc_w(ac_w, True) if ac_w > 0 else 0.0


class Case:
    """One design day: every load's trace and the battery-bus power each minute."""

    def __init__(self, key, data):
        system = data["system"]
        self.key = key
        self.cold = key.startswith("cold")
        self.thermal = system["thermal"]
        self.inverter = Inverter(system["inverter"])
        self.converters = system["converters"]
        location = system["battery_location"]
        self.loads = [l for l in data["loads"] if l.get("when_location", location) == location]
        self.specs = {l["id"]: spec_for(l, key) for l in self.loads}
        self.traces = {}
        for load in self.loads:
            raw = load_trace(self.specs[load["id"]], self.thermal)
            self.traces[load["id"]] = with_standby(raw, load.get("standby_w", 0.0))
        self.ac = self.side_sum("ac")
        always_on = system["inverter"]["always_on"][key]
        self.inverter_dc = [self.inverter.dc_w(w, always_on or w > 5.0) for w in self.ac]
        self.dc_direct = self.side_sum("dc")
        self.converter_in = {side: self.converter_input(side) for side in ("dc24", "dc12")}
        self.bus = [sum(parts) for parts in zip(
            self.inverter_dc, self.dc_direct, self.converter_in["dc24"], self.converter_in["dc12"])]

    def side_sum(self, side):
        total = [0.0] * MINUTES
        for load in self.loads:
            if load["side"] == side:
                total = [t + w for t, w in zip(total, self.traces[load["id"]])]
        return total

    def converter_input(self, side):
        conv = self.converters[side]
        return [w / conv["efficiency"] + conv["idle_w"] for w in self.side_sum(side)]

    def daily_kwh(self):
        return kwh(self.bus)

    def window_kwh(self, hours):
        width = int(hours * 60)
        doubled = self.bus + self.bus
        running = sum(doubled[:width])
        best, best_start = running, 0
        for start in range(1, MINUTES):
            running += doubled[start + width - 1] - doubled[start - 1]
            if running > best:
                best, best_start = running, start
        return best / 60000.0, best_start / 60.0

    def span_kwh(self, start_h, end_h, trace=None):
        trace = trace or self.bus
        return sum(trace[m % MINUTES] for m in range(int(start_h * 60), int(end_h * 60))) / 60000.0

    def hourly_kwh(self, trace):
        return [sum(trace[h * 60:(h + 1) * 60]) / 60000.0 for h in range(24)]

    def inverter_loss_kwh(self):
        return kwh(self.inverter_dc) - kwh(self.ac)

    def converter_loss_kwh(self):
        return sum(kwh(self.converter_in[s]) - kwh(self.side_sum(s)) for s in ("dc24", "dc12"))

    def case_peak_w(self, load):
        """A load's peak in this case, or 0 when it does not run in this case."""
        spec = self.specs[load["id"]]
        if not any(k in spec for k in ("events", "runs", "hourly_w", "kwh")):
            return 0.0
        return spec.get("peak_w", load["peak_w"])


def expand(names, groups):
    out = set()
    for name in names if isinstance(names, list) else [names]:
        out |= set(groups.get(name, [name]))
    return out


def managed_peak(case, interlocks):
    """Worst coincident AC load the interlock rules allow, and the same with nothing managed.

    The HVAC is never shed, so it always counts at its case peak. Small AC loads count at their highest
    scheduled total, plus an allowance for the user outlets. Every combination of the heavy loads is tested
    against the never-together pairs and the caps (a cap lowers a load's peak while another load runs).
    """
    groups = interlocks["groups"]
    heavy = [l for l in case.loads
             if l.get("heavy") and l.get("group") != "hvac" and case.case_peak_w(l) > 0]
    hvac = sum(case.case_peak_w(l) for l in case.loads if l.get("group") == "hvac" and l["side"] == "ac")
    small = [sum(case.traces[l["id"]][m] for l in case.loads
                 if l["side"] == "ac" and not l.get("heavy") and l.get("group") != "hvac")
             for m in range(MINUTES)]
    base = max(small) + interlocks["user_outlets_w"]
    pairs = []
    for first, second in interlocks["never_together"]:
        pairs += [{a, b} for a in expand(first, groups) for b in expand(second, groups) if a != b]
    best, best_set = 0.0, ()
    for n in range(len(heavy) + 1):
        for combo in itertools.combinations(heavy, n):
            ids = {l["id"] for l in combo}
            if any(p <= ids for p in pairs):
                continue
            peaks = {l["id"]: case.case_peak_w(l) for l in combo}
            for cap in interlocks.get("caps", []):
                if set(cap["when"]) <= ids:
                    for target, limit in cap["cap"].items():
                        if target in peaks:
                            peaks[target] = min(peaks[target], limit)
            total = sum(peaks.values())
            if total > best:
                best, best_set = total, tuple(sorted(ids))
    unmanaged = hvac + base + sum(case.case_peak_w(l) for l in heavy if not l.get("duplicate_of"))
    return hvac + base + best, best_set, unmanaged, base, hvac


def dc_bus_checks(case, data):
    """Worst coincident current on the 12 V and 24 V buses against the converters."""
    lines = []
    peaks = {l["id"]: l.get("bus_peak_w", l["peak_w"]) for l in data["loads"]}
    for check in data["interlocks"]["dc_checks"]:
        conv = data["system"]["converters"][check["bus"]]
        watts = sum(peaks[i] for i in check["loads"]) + check.get("allowance_w", 0)
        amps = watts / conv["volts"]
        lines.append(f"{check['name']}: {watts:.0f} W, {amps:.1f} A on the {conv['volts']} V bus, against "
                     f"{conv['continuous_a']:.0f} A continuous ({amps / conv['continuous_a']:.0%}) and "
                     f"{conv['ten_second_a']:.0f} A for 10 s. {check.get('note', '')}")
    return lines


def derating(system, cold):
    table = system["temperature_derating"]
    if system["battery_location"] == "inside":
        return table["inside"]
    return table["underfloor_cold"] if cold else table["underfloor_hot"]


def required_nominal_kwh(bus_kwh, system, cold, end_of_life):
    factor = system["battery_discharge_efficiency"] * derating(system, cold) * system["usable_fraction"]
    if end_of_life:
        factor *= system["eol_capacity_fraction"]
    return bus_kwh / factor


def autonomy_hours(case, nominal_kwh, system, end_of_life, limit_h=72):
    """Hours from full until the usable energy is gone, for the worst starting hour."""
    usable = nominal_kwh * system["usable_fraction"] * derating(system, case.cold)
    if end_of_life:
        usable *= system["eol_capacity_fraction"]
    per_minute = [w / 60000.0 / system["battery_discharge_efficiency"] for w in case.bus]
    worst = float(limit_h)
    for start in range(0, MINUTES, 30):
        left, m = usable, 0
        while left > 0 and m < limit_h * 60:
            left -= per_minute[(start + m) % MINUTES]
            m += 1
        worst = min(worst, m / 60.0)
    return worst


def h3_needs(cases, system):
    hot, hot_d = cases["hot"], cases["hot_diesel"]
    night_d = cases["cold_diesel"].span_kwh(*COLD_NIGHT)
    night_hp = cases["cold_hp"].span_kwh(*COLD_NIGHT)
    return [
        ("hot24", "Hot day all electric, 24 h, new", required_nominal_kwh(hot.daily_kwh(), system, False, False)),
        ("hot12EOL", "Hot day all electric, worst 12 h, end of life",
         required_nominal_kwh(hot.window_kwh(12)[0], system, False, True)),
        ("hotD24", "Hot day, diesel hot water, 24 h, new",
         required_nominal_kwh(hot_d.daily_kwh(), system, False, False)),
        ("nightD", "Cold night 14 h, diesel heating, end of life", required_nominal_kwh(night_d, system, True, True)),
        ("nightHP", "Cold night 14 h, heat pump, end of life", required_nominal_kwh(night_hp, system, True, True)),
    ]


def print_case(case, data):
    system, interlocks = data["system"], data["interlocks"]
    print(f"\n=== {CASES[case.key]} ({case.key}) ===")
    print(f"{'Load':<62}{'side':>6}{'kWh':>8}")
    for load in case.loads:
        energy = kwh(case.traces[load["id"]])
        if energy > 0.0005:
            flag = " (prov.)" if load.get("provisional") or case.specs[load["id"]].get("provisional") else ""
            print(f"{load['id'] + ' ' + load['name'][:48] + flag:<62}{load['side']:>6}{energy:8.2f}")
    print(f"{'Inverter conversion loss, idle and search':<62}{'':>6}{case.inverter_loss_kwh():8.2f}")
    print(f"{'DC-DC converter loss and idle':<62}{'':>6}{case.converter_loss_kwh():8.2f}")
    print(f"{'Daily total at the battery bus':<62}{'':>6}{case.daily_kwh():8.2f}")
    ac = kwh(case.ac)
    print(f"AC-side energy {ac:.2f} kWh, mean inverter efficiency {ac / max(kwh(case.inverter_dc), 1e-9):.3f}")
    worst12, start12 = case.window_kwh(12)
    print(f"Worst 12 h window: {worst12:.2f} kWh, starting {clock(start12)}")
    if case.cold:
        print(f"Cold night 17:00 to 07:00 (14 h): {case.span_kwh(*COLD_NIGHT):.2f} kWh at the battery bus")
    hourly = case.hourly_kwh(case.bus)
    print("Hourly bus energy (kWh), 00 to 23:")
    print("  " + " ".join(f"{h:02d}:{e:.2f}" for h, e in enumerate(hourly[:12])))
    print("  " + " ".join(f"{h + 12:02d}:{e:.2f}" for h, e in enumerate(hourly[12:])))
    print(f"Scheduled peak: {max(case.ac):.0f} W AC at the inverter output, {max(case.bus):.0f} W at the battery")
    managed, combo, unmanaged, base, hvac = managed_peak(case, interlocks)
    inverter = system["inverter"]
    print(f"Managed worst coincident AC load: {managed:.0f} W = HVAC {hvac:.0f} W + {', '.join(combo)} + "
          f"{base:.0f} W of small loads and user outlets. Unmanaged: {unmanaged:.0f} W")
    print(f"Inverter {inverter['model']}: {inverter['continuous_w_25c']} W at 25 C, {inverter['continuous_w_40c']} W "
          f"at 40 C, {inverter['peak_w']} W for 1 min. Managed load is {managed / inverter['continuous_w_40c']:.0%} "
          f"of the 40 C rating and {managed / inverter['continuous_w_25c']:.0%} of the 25 C rating")
    if case.key == "hot":
        for line in dc_bus_checks(case, data):
            print(line)


def print_batteries(cases, data):
    system = data["system"]
    hot = cases["hot"]
    needs = h3_needs(cases, system)
    print("\n=== H3: capacity needed (nominal kWh) ===")
    for _, label, need in needs:
        print(f"{label:<52}{need:6.1f} kWh nominal, {need * system['usable_fraction']:5.1f} kWh usable")
    print("\n=== Candidate battery banks against H3 ===")
    print("Ratios are installed nominal over required nominal (1.00 or more passes). Headroom is the extra load a day")
    print("at the battery bus the bank could carry and still pass the governing H3 check. Autonomy is from full on the")
    print("all-electric hot day, worst starting hour. 24 V banks use the 48 V model's losses, so they read about 2 % low.")
    print(f"{'Bank':<46}{'kWh':>6}{'kg':>6}{'AUD':>7}" + "".join(f"{key:>9}" for key, _, _ in needs)
          + f"{'headroom':>9}{'new h':>7}{'EOL h':>7}")
    governing = max(need for _, _, need in needs)
    for bank in data["battery_candidates"]:
        nominal = bank["modules"] * bank["kwh_each"]
        mass = bank["modules"] * bank.get("kg_each", 0)
        price = bank["modules"] * bank.get("price_each_aud", 0)
        ratios = "".join(f"{nominal / need:9.2f}" for _, _, need in needs)
        headroom = (nominal - governing) * system["usable_fraction"] * system["battery_discharge_efficiency"]
        print(f"{bank['name'][:45]:<46}{nominal:6.1f}{mass:6.0f}{price:7.0f}{ratios}{headroom:9.1f}"
              f"{autonomy_hours(hot, nominal, system, False):7.1f}{autonomy_hours(hot, nominal, system, True):7.1f}")
    print(f"The governing check needs {governing:.1f} kWh nominal.")


def print_recharge(cases, data):
    system = data["system"]
    hot = cases["hot"]
    back_in = hot.daily_kwh() / system["battery_discharge_efficiency"] / system["battery_charge_efficiency"]
    mean_load_w = hot.daily_kwh() * 1000.0 / 24.0
    print("\n=== Recharge of one all-electric design hot day ===")
    print(f"Energy to put back into the cells: {back_in:.1f} kWh. Mean household load {mean_load_w:.0f} W")
    for src in data.get("recharge_sources", []):
        if "dc_w" in src:
            dc_w = src["dc_w"]
        else:
            dc_w = min(src["ac_w"] * src.get("charger_efficiency", 0.93), src.get("charger_limit_w", 1e9))
        hours_idle = back_in * 1000.0 / dc_w
        net = dc_w - mean_load_w
        live = f"{back_in * 1000.0 / net:4.1f} h while the household runs" if net > 100 else "less than the mean household load"
        fuel = src.get("fuel_l_per_h")
        fuel_txt = f", about {fuel * back_in * 1000.0 / max(net, dc_w * 0.5):.1f} L of fuel" if fuel else ""
        drive_txt = f", {dc_w * 5 / 1000.0:.1f} kWh on a 5 h drive" if "dc_w" in src else ""
        print(f"{src['name']:<52} {dc_w:6.0f} W into the battery: {hours_idle:4.1f} h with nothing else on, "
              f"{live}{fuel_txt}{drive_txt}")


def print_solar(cases, data):
    solar = data.get("solar") or {}
    if not solar:
        return
    print("\n=== Solar yield on the flat roof (PVGIS, kWh a day) against the loads ===")
    for site, months in solar.get("sites", {}).items():
        for label, per_kwp in months.items():
            row = "  ".join(f"{share}: {per_kwp * kwp:5.1f}" for share, kwp in solar["arrays_kwp"].items())
            print(f"{site:<16}{label:<22}{per_kwp:5.2f} kWh/kWp  {row}")
    print("Daily totals at the battery bus: " + ", ".join(
        f"{key} {case.daily_kwh():.1f} kWh" for key, case in cases.items()))


def print_sensitivity(data):
    system = data["system"]
    bank = data["battery_candidates"][0]
    kg_per_kwh = bank["kg_each"] / bank["kwh_each"]
    per_bus_kwh = kg_per_kwh / (system["battery_discharge_efficiency"] * system["usable_fraction"])
    per_ac_kwh = per_bus_kwh / Inverter(system["inverter"]).efficiency(800)
    print("\n=== Battery mass per kWh a day of load (H3, new, 24 h) ===")
    print(f"{bank['name']}: {kg_per_kwh:.2f} kg per nominal kWh, so {per_bus_kwh:.1f} kg per kWh a day at the bus "
          f"and {per_ac_kwh:.1f} kg per kWh a day of an 800 W AC load")


def main():
    data = yaml.safe_load((HERE / "loads.yaml").read_text())
    system = data["system"]
    inverter = system["inverter"]
    print("Report 20 energy model. Inputs: loads.yaml. Battery location:", system["battery_location"])
    print(f"Inverter: {inverter['model']}, zero load {inverter['no_load_w']} W, search mode {inverter['search_w']} W, "
          f"max efficiency {inverter['max_efficiency']:.2f}")
    provisional = [l["id"] for l in data["loads"] if l.get("provisional")]
    partly = [l["id"] for l in data["loads"] if any((spec_for(l, k) or {}).get("provisional") for k in CASES)]
    print("Provisional loads (no figure in report 19 or report 21):", ", ".join(provisional) or "none")
    print("Provisional in part:", ", ".join(partly) or "none")
    cases = {key: Case(key, data) for key in CASES}
    for case in cases.values():
        print_case(case, data)
    print_batteries(cases, data)
    print_recharge(cases, data)
    print_solar(cases, data)
    print_sensitivity(data)


if __name__ == "__main__":
    main()

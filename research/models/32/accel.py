"""Research report 32's acceleration model: the Ranger Super Duty single cab chassis towing the trailer from rest to
100 km/h and from 80 to 100 km/h, on a flat road in still air, at four power levels and four combination masses.

    python3 research/models/32/accel.py > research/models/32/accel.out

The truck and trailer move forward in steps of 10 ms through the 10-speed's gears. Each step takes the engine's
full-load torque at its speed, under the gear's torque cap, times the turbo's spool and, in first, the torque
converter's multiplication, through the gearbox, transfer case and axles to the tyres. Rolling resistance and report
25's drag act against it, and every upshift loses drive for a set time. Every input not taken from a cited source is
marked (est.). Standard library only.
"""
import math

G = 9.81  # m/s2
RHO = 1.2  # kg/m3, air at about 20 °C at sea level

# The 10-speed: the Ford 10R80's ratios (Wikipedia, "Ford-GM 10-speed automatic transmission", read 24 Nov 2026).
# Ford names only "10-Speed Automatic" for the Super Duty, and the 10R80 is the Ranger's, the Everest's and the
# Amarok's (report 32 section 4).
RATIOS = (4.696, 2.985, 2.146, 1.769, 1.520, 1.275, 1.000, 0.854, 0.689, 0.636)
FINAL_DRIVE = 3.73  # (est.) the ordinary Ranger V6's. No Ford document read gives the Super Duty's
TYRE_R = 0.406  # m, LT 275/70 R18 (842 mm across) loaded to 0.965 of its free radius (est.)
ETA = 0.85  # crank to wheels (est.). CarExpert measured 158.4 kW at the rear wheels of an ordinary 184 kW Ranger V6, 0.86
N_MAX = 4000  # rpm, the latest upshift at full throttle (est.)
SHIFT_LOST = 0.20  # s with no drive at each upshift (est.)
SPOOL_F0, SPOOL_TAU = 0.50, 0.70  # share of full-load torque when the throttle opens, and the time constant in s (est.)
KICKDOWN = 0.60  # s from full throttle at 80 km/h to the lower gear engaged (est.)
STALL_RPM, TR0, SR_COUPLE = 2000.0, 1.9, 0.87  # converter: full-load stall speed, stall torque ratio, coupling point (est.)
MU = 0.80  # grip of the truck's four tyres on dry bitumen, all four driven in 4A (est.)
I_ENGINE = 0.45  # kg m2, crank, flywheel, converter and gearbox input (est.)
I_DRIVELINE = 0.15  # kg m2 at the gearbox output: tailshafts, axles and differentials (est.)
CRR = 0.011  # rolling resistance, the truck's LT tyres and the trailer's (est.)
CDA = 4.55  # m2, report 25's option A+: the ute, the bike box and the trailer with its radiused front
WHEELS_EQ = 0.6 * 48.0 * 4 + 0.6 * 35.0 * 4  # kg, four 48 kg truck wheels and four 35 kg trailer wheels, I/r2 of 0.6 m (est.)
FIRST_CAP = 600.0  # Nm, Ford's figure, kept in first, reverse and low range at every level
# One factor on the force at the tyres, fitted on 24 Nov 2026 to three measurements of stock Super Duties (calibration()
# below). It stands for what the model cannot separate: the real crank to road efficiency, each engine's real output
# against its rating and how the tests read speed. It applies to every level, as the tuned figures are crank ratings
# like Ford's. 1.00 is the model as first built.
CALIB = 1.08  # (est., fitted)

# The combination's masses, kg. UTE-06's GCM case is the ute with growth (3,748 kg) and the trailer at its 4,000 kg
# plate. TC2 with growth is the trailer fully loaded with 400 L of water and growth (3,575.6 kg, TRAILER.md).
# 7,450 and 7,200 kg are the two lighter masses the plan asked for. The truck's tyres carry the ute and the towball,
# about 4,140 kg with growth (est.), which sets the grip.
MASSES = (("GCM case, the trailer at its plate", 7750.0), ("Lighter, about 300 kg less", 7450.0),
          ("TC2 with growth behind the ute with growth", 7324.0), ("Lighter, about 550 kg less", 7200.0))
N_DRIVE_KG = 4140.0  # (est.)


def curve(points):
    """Full-load torque in Nm at an engine speed in rpm, by straight lines between the points, zero past the last."""
    def torque(rpm):
        if rpm <= points[0][0]:
            return points[0][1]
        for (n0, t0), (n1, t1) in zip(points, points[1:]):
            if rpm <= n1:
                return t0 + (t1 - t0) * (rpm - n0) / (n1 - n0)
        return 0.0
    return torque


def kw(nm, rpm):
    return nm * rpm * 2 * math.pi / 60 / 1000


# Full-load curves (rpm, Nm). Ford gives two points of each stock engine: the Super Duty 154 kW at 3,250 rpm and 600 Nm
# at 1,750 rpm (dealer sheet, BEMM), the ordinary Ranger V6 184 kW at 3,250 rpm and 600 Nm from 1,750 to 2,250 rpm.
# The rest of each curve is (est.). The tuned curves hold their torque cap, then their power to 3,500 or 3,600 rpm.
LEVELS = {
    "stock": ("Stock Super Duty, 154 kW, 600 Nm",
              [(800, 280), (1250, 450), (1750, 600), (2250, 600), (3250, 452), (3750, 360), (4000, 300), (4200, 0)]),
    "ranger": ("Ordinary Ranger V6, 184 kW, 600 Nm",
               [(800, 280), (1250, 450), (1750, 600), (2250, 600), (3250, 541), (3750, 430), (4000, 360), (4200, 0)]),
    "plan": ("The plan, 205 kW, 650 Nm",
             [(800, 290), (1250, 480), (1750, 630), (1900, 650), (3000, 650), (3500, 559), (3750, 480), (4000, 400),
              (4200, 0)]),
    "option": ("The 250 hp option, 220 kW, 650 Nm",
               [(800, 290), (1250, 480), (1750, 630), (1900, 650), (3232, 650), (3500, 600), (3750, 510), (4000, 420),
                (4200, 0)]),
}


def capped(p_kw, cap=700.0, top=3600.0):
    """The new level's family: the cap from 2,100 rpm until p_kw, p_kw held to top rpm, then 91.5 % of it at 3,850 rpm
    and 83.8 % at 4,000 rpm (est.). None when the cap cannot make p_kw by top rpm."""
    n_p = p_kw * 1000 / (cap * 2 * math.pi / 60)
    if n_p > top:
        return None
    nm = lambda share, rpm: share * p_kw * 1000 / (rpm * 2 * math.pi / 60)
    pts = [(800, min(300, cap)), (1250, min(500, cap)), (1750, min(680, cap)), (2100, cap)]
    if n_p > 2100:
        pts.append((n_p, cap))
    pts += [(top, nm(1.0, top)), (3850, nm(0.915, 3850)), (4000, nm(0.838, 4000)), (4200, 0)]
    return pts


LEVELS["new"] = ("The new level, 250 kW, 700 Nm", capped(250.0))
LEVELS["350bhp"] = ("About 350 bhp, 260 kW, 700 Nm", capped(260.0))
LEVELS["cut1"] = ("CUT1 on Ford's turbo, 184 kW, 600 Nm", LEVELS["ranger"][1])
TABLE = ("stock", "cut1", "plan", "option", "new", "350bhp")


class Rig:
    """A vehicle or a combination: its mass, the mass on its driven tyres, drag, rolling resistance, wheels and gearing."""

    def __init__(self, mass, n_drive_kg, cda=CDA, crr=CRR, wheels_eq=WHEELS_EQ, tyre_r=TYRE_R, final=FINAL_DRIVE,
                 eta=ETA, shift_lost=SHIFT_LOST, tau=SPOOL_TAU, tr0=TR0, calib=CALIB):
        self.mass, self.n_drive, self.cda, self.crr = mass, n_drive_kg * G, cda, crr
        self.wheels_eq, self.r, self.final, self.eta = wheels_eq, tyre_r, final, eta
        self.shift_lost, self.tau, self.tr0, self.calib = shift_lost, tau, tr0, calib

    def rpm(self, v, gear):
        return v / self.r * RATIOS[gear] * self.final * 60 / (2 * math.pi)

    def mass_eff(self, gear):
        k = RATIOS[gear] * self.final / self.r
        return self.mass + self.wheels_eq + I_DRIVELINE * (self.final / self.r) ** 2 + I_ENGINE * k * k

    def road(self, v):
        return self.crr * self.mass * G + 0.5 * RHO * self.cda * v * v

    def drive(self, torque, gear, v, spool):
        """Force at the tyres in N. In first the converter slips: the engine holds its stall speed until the turbine
        reaches the coupling point, multiplying torque from TR0 down to 1, then turns at the turbine speed over
        SR_COUPLE. From second up the converter is locked. Grip caps the force."""
        n_t = self.rpm(v, gear)
        if gear == 0:
            n_e = max(STALL_RPM, n_t / SR_COUPLE)
            tr = self.tr0 - (self.tr0 - 1.0) * min(1.0, n_t / n_e / SR_COUPLE)
            t_e = min(FIRST_CAP, torque(n_e))
        else:
            n_e, tr, t_e = n_t, 1.0, torque(n_t)
        f = t_e * spool * tr * RATIOS[gear] * self.final * self.eta * self.calib / self.r
        return min(f, MU * self.n_drive), n_e


def run(rig, torque, v_from, v_to, dt=0.01):
    """Seconds at full throttle from v_from to v_to in km/h. From rest the truck starts in first. From a roll it holds
    its speed for KICKDOWN s, then drops to the gear with the most force under N_MAX, and the turbo spools again."""
    v, v_end, t = v_from / 3.6, v_to / 3.6, 0.0
    if v_from > 0:
        gears = [g for g in range(len(RATIOS)) if rig.rpm(v, g) <= N_MAX]
        gear = max(gears, key=lambda g: rig.drive(torque, g, v, 1.0)[0])
        t, f0 = KICKDOWN, 0.6  # part-load boost before the kickdown (est.)
    else:
        gear, f0 = 0, SPOOL_F0
    t_spool, lost = 0.0, 0.0
    while v < v_end:
        spool = 1.0 - (1.0 - f0) * math.exp(-t_spool / rig.tau)
        if lost > 0:
            f, lost = 0.0, lost - dt
        else:
            f, n_e = rig.drive(torque, gear, v, spool)
            if gear < len(RATIOS) - 1:
                if n_e >= N_MAX or rig.drive(torque, gear + 1, v, spool)[0] > f:
                    gear, lost, f = gear + 1, rig.shift_lost, 0.0
        a = (f - rig.road(v)) / rig.mass_eff(gear)
        if a <= 0 and f > 0:
            return float("inf")
        v += a * dt
        t += dt
        t_spool += dt
        if t > 300:
            return float("inf")
    return t


def steady_speed(rig, torque, extra_n):
    """The highest steady speed in km/h, to 0.25 km/h, at full power against the road load and extra_n of pull."""
    best = 0.0
    for step in range(80, 721):
        v = step / 4 / 3.6
        forces = [rig.drive(torque, g, v, 1.0)[0] for g in range(1, len(RATIOS)) if 1200 <= rig.rpm(v, g) <= N_MAX]
        if forces and max(forces) >= rig.road(v) + extra_n:
            best = step / 4
    return best


def power_for(rig, target_s, lo=180.0, hi=263.0):
    """Peak crank power in kW on the 700 Nm family that reaches 100 km/h from rest in target_s, or None."""
    if run(rig, curve(capped(hi)), 0, 100) > target_s:
        return None
    for _ in range(30):
        mid = (lo + hi) / 2
        if run(rig, curve(capped(mid)), 0, 100) > target_s:
            lo = mid
        else:
            hi = mid
    return hi


def calibration():
    """The three measurements of stock Super Duties, the model's figure for each as first built (factor 1.00) and as
    calibrated (CALIB), and the factor each measurement alone implies. Plus the ordinary Ranger V6 as a check."""
    stock = curve(LEVELS["stock"][1])
    # CarExpert's dual cab chassis: Ford's 2,675 kg kerb (sheet of 29 Oct 2026), a heavy-duty tray, a toolbox, the
    # crew and the gear, 3,150 kg (est., 3,050 to 3,300). Leonard's figure: a stock Super Duty with a tray towing 4 t,
    # about 7,000 kg in all with about 3,300 kg on the truck's tyres (est.), behind a flat deck (CdA 2.5 m2, est.) or a
    # caravan (4.5 m2, est.).
    cab = lambda c, m=3150.0: Rig(m, m, cda=1.85, wheels_eq=0.6 * 48.0 * 4, calib=c)
    tow = lambda c, cda: Rig(7000.0, 3300.0, cda=cda, calib=c)
    figures = [
        ("CarExpert, unladen 0 to 100 km/h, s", 13.23, lambda c: run(cab(c), stock, 0, 100)),
        ("CarExpert, unladen 80 to 120 km/h, s", 11.99, lambda c: run(cab(c), stock, 80, 120)),
        ("CarExpert, 6.0 kN trailer dyno, cool, km/h", 78.0, lambda c: steady_speed(cab(c), stock, 6000)),
        ("CarExpert, 6.0 kN trailer dyno, hot, km/h", 68.0, lambda c: steady_speed(cab(c), stock, 6000)),
        ("Leonard, 4 t, 0 to 100 km/h, flat deck, s", 28.0, lambda c: run(tow(c, 2.5), stock, 0, 100)),
        ("Leonard, 4 t, 0 to 100 km/h, caravan, s", 28.0, lambda c: run(tow(c, 4.5), stock, 0, 100)),
    ]
    print(f"Calibration: three measurements of stock Super Duties, the model at factor 1.00 and at {CALIB:.2f}, and the "
          "factor each alone implies")
    implied = {}
    for label, target, fn in figures:
        lo, hi = 0.70, 1.50
        rising = fn(1.2) > fn(1.0)  # a steady speed rises with the factor, a time falls
        for _ in range(25):
            mid = (lo + hi) / 2
            if (fn(mid) < target) == rising:
                lo = mid
            else:
                hi = mid
        implied[label] = (lo + hi) / 2
        print(f"  {label:44s} tested {target:6.2f}, model {fn(1.0):6.2f} at 1.00, {fn(CALIB):6.2f} at {CALIB:.2f}, "
              f"implies {implied[label]:.3f}")
    for m in (3050.0, 3300.0):
        print(f"  The unladen runs at {m:,.0f} kg: {run(cab(1.0, m), stock, 0, 100):.2f} s and {run(cab(1.0, m), stock, 80, 120):.2f} s "
              f"at 1.00, {run(cab(CALIB, m), stock, 0, 100):.2f} s and {run(cab(CALIB, m), stock, 80, 120):.2f} s at {CALIB:.2f}")
    for c in (1.0, CALIB):
        ranger = Rig(2415.0, 2415.0, cda=1.45, crr=0.010, wheels_eq=0.6 * 40.0 * 4, tyre_r=0.38, calib=c)
        print(f"  Check, ordinary Ranger V6, 2,415 kg with the driver (est.): 0 to 100 km/h "
              f"{run(ranger, curve(LEVELS['ranger'][1]), 0, 100):.1f} s at {c:.2f}, tested 8.2 to 8.5 s")
    print()
    return implied


def results(calib):
    print(f"Towing on a flat road in still air, CdA 4.55 m2, Crr 0.011 (est.), the 10R80's ratios on a 3.73 final drive "
          f"(est.), {SHIFT_LOST:.1f} s lost at each upshift, factor {calib:.2f}. Wheel figures are crank x {ETA:.2f}, the plan's convention")
    print(f"{'Level':38s} {'Crank kW':>8s} {'Wheel kW':>8s} {'Wheel hp':>8s} " +
          " ".join(f"{int(m):>7d} kg" for _, m in MASSES))
    for key in TABLE:
        name, pts = LEVELS[key]
        torque = curve(pts)
        peak = max(kw(torque(n), n) for n in range(1000, 4200, 10))
        cells = []
        for _, m in MASSES:
            rig = Rig(m, N_DRIVE_KG, calib=calib)
            cells.append(f"{run(rig, torque, 0, 100):5.1f}/{run(rig, torque, 80, 100):4.1f}")
        print(f"{name:38s} {peak:8.0f} {peak * ETA:8.0f} {peak * ETA / 0.7457:8.0f} " + " ".join(f"{c:>10s}" for c in cells))
    print("Each cell: 0 to 100 km/h s / 80 to 100 km/h s")
    print("0 to 80 km/h at 7,750 kg: " + ", ".join(
        f"{LEVELS[k][0].split(',')[1].strip()} {run(Rig(7750.0, N_DRIVE_KG, calib=calib), curve(LEVELS[k][1]), 0, 80):.1f} s"
        for k in TABLE))
    print()


def bracket(factors):
    print("0 to 100 km/h / 80 to 100 km/h at 7,750 kg under each factor: " + ", ".join(f"{label} {c:.3f}" for label, c in factors))
    for key in TABLE:
        torque = curve(LEVELS[key][1])
        cells = []
        for _, c in factors:
            rig = Rig(7750.0, N_DRIVE_KG, calib=c)
            cells.append(f"{run(rig, torque, 0, 100):5.1f}/{run(rig, torque, 80, 100):4.1f}")
        print(f"  {LEVELS[key][0]:38s} " + " ".join(f"{x:>11s}" for x in cells))
    print()


def power_for_22(factors):
    print("Peak crank power on the 700 Nm family for 0 to 100 km/h in 22.0 s, under each factor (the cap reaches 264 kW at "
          "3,600 rpm). Wheel figures are crank x 0.85")
    for label, m in MASSES:
        parts = []
        for flabel, c in factors:
            p = power_for(Rig(m, N_DRIVE_KG, calib=c), 22.0, lo=120.0)
            parts.append(f"{flabel}: " + ("over 263 kW" if p is None else f"{p:.0f} kW ({p * ETA:.0f} kW, {p * ETA / 0.7457:.0f} hp)"))
        print(f"  {int(m):,} kg, {label}: " + ", ".join(parts))
    for target in (24.0, 25.0):
        p = power_for(Rig(7750.0, N_DRIVE_KG), target, lo=120.0)
        print(f"  7,750 kg for {target:.0f} s at {CALIB:.2f}: " + ("over 263 kW" if p is None else f"{p:.0f} kW at the crank"))
    print()


def caps():
    print("The torque cap from second gear up, 250 kW or the most the cap makes by 3,600 rpm, at 7,750 kg")
    for cap in (650.0, 700.0, 750.0, 800.0):
        p = min(250.0, 0.999 * cap * 3600 * 2 * math.pi / 60 / 1000)
        torque = curve(capped(p, cap=cap))
        n_from = p * 1000 / (cap * 2 * math.pi / 60)
        rig = Rig(7750.0, N_DRIVE_KG)
        print(f"  {cap:.0f} Nm: {p:.0f} kW from {n_from:,.0f} to 3,600 rpm, 0 to 100 km/h {run(rig, torque, 0, 100):.1f} s, "
              f"80 to 100 km/h {run(rig, torque, 80, 100):.1f} s")
    print()


def sensitivity():
    print(f"{LEVELS['new'][0]} at 7,750 kg and factor {CALIB:.2f}, one input changed at a time (0 to 100 km/h s)")
    torque = curve(LEVELS["new"][1])
    base = run(Rig(7750.0, N_DRIVE_KG), torque, 0, 100)
    cases = [("as above", {}), ("final drive 4.10 (est.)", dict(final=4.10)), ("final drive 3.55 (est.)", dict(final=3.55)),
             ("0.4 s lost at each upshift", dict(shift_lost=0.40)), ("no time lost at upshifts", dict(shift_lost=0.0)),
             ("spool time constant 1.2 s", dict(tau=1.2)), ("converter stall ratio 1.5", dict(tr0=1.5)),
             ("factor 1.00, as first built", dict(calib=1.0)), ("factor 1.19", dict(calib=1.19)),
             ("Crr 0.013", dict(crr=0.013)), ("CdA 15 % more", dict(cda=CDA * 1.15)), ("CdA 15 % less", dict(cda=CDA * 0.85))]
    for label, kwargs in cases:
        t = run(Rig(7750.0, N_DRIVE_KG, **kwargs), torque, 0, 100)
        print(f"  {label:32s} {t:5.1f} s ({t - base:+.1f})")
    print()


def bands():
    print("Engine speed band of each level's peak power (within 1 %)")
    for key in TABLE:
        name, pts = LEVELS[key]
        torque = curve(pts)
        peak = max(kw(torque(n), n) for n in range(1000, 4200, 10))
        band = [n for n in range(1000, 4200, 10) if kw(torque(n), n) >= 0.99 * peak]
        top_nm = max(torque(n) for n in range(1000, 4200, 10))
        print(f"  {name:38s} {peak:5.0f} kW from {band[0]:,} to {band[-1]:,} rpm, at most {top_nm:.0f} Nm "
              f"from second gear up, {FIRST_CAP:.0f} Nm in first")
    print()


def climbs():
    """Speeds held on long grades at 7,750 kg, and the crank power a speed needs there: the heat the cooling must reject."""
    print(f"Long climbs at 7,750 kg and factor {CALIB:.2f}: the steady speed at full power, km/h, and the crank power to "
          "hold 80 and 100 km/h")
    rig = Rig(7750.0, N_DRIVE_KG)
    for grade in (0.04, 0.06, 0.08):
        pull = rig.mass * G * math.sin(math.atan(grade))
        speeds = ", ".join(f"{LEVELS[k][0].split(',')[1].strip()} {steady_speed(rig, curve(LEVELS[k][1]), pull):.0f}"
                           for k in TABLE)
        need = [(rig.road(v / 3.6) + pull) * v / 3.6 / (ETA * CALIB) / 1000 for v in (80, 100)]
        print(f"  {grade * 100:.0f} %: {speeds}. Holding 80 km/h takes {need[0]:.0f} kW at the crank, 100 km/h {need[1]:.0f} kW")
    print()


if __name__ == "__main__":
    implied = calibration()
    caravan = implied["Leonard, 4 t, 0 to 100 km/h, caravan, s"]
    results(CALIB)
    bracket([("as first built", 1.0), ("calibrated", CALIB), ("Leonard's 28 s as a caravan", caravan)])
    bands()
    caps()
    power_for_22([("1.00", 1.0), (f"{CALIB:.2f}", CALIB), (f"{caravan:.2f}", caravan)])
    sensitivity()
    climbs()

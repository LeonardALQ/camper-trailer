"""Report 25 drag and fuel model: LandCruiser VDJ79 single cab with the bike box, towing the home trailer.

research/25-roof.md, question 1. Run: python3 aero.py > aero.out. No third-party modules.

Method: a component build-up of the combination's drag area CdA in m2, still air, zero yaw.
  CdA = CdA_lead (ute and box)
      + Cd_fe x A_exposed     trailer front face outside the box silhouette (forebody, sharp or rounded edges)
      + Cd_fs x A_shielded    trailer front face inside the box silhouette
      + Cd_base x A_rear      trailer rear face (base drag)
      + Cf x S_wet            trailer roof and side skin friction
      + CdA_under             axles, wheels, drawbar, drawbar box, spare, mud flaps
      - CdA_recovered         part of the box's own base drag that the trailer behind it removes
Road load = 0.5 rho V^2 CdA + Crr m g. Engine power = road load x V / driveline efficiency + accessories.
Fuel from a Willans line: kg/h = a + b x engine kW.

Sources for the coefficients (full list in research/25-roof.md section 1):
- Sharp-edged box: NASA coast-down box vehicle, Cd 1.13 square, 0.68 with rounded vertical front corners
  (about 40 % less aerodynamic drag), Saltzman and Meyer, NASA TM X-56023, 1974,
  https://ntrs.nasa.gov/api/citations/19740009590/downloads/19740009590.pdf . Wind tunnel 0.86 for the square box.
- Tandem bluff bodies: a flat-faced body alone has forebody drag 0.75, falling to 0.02 at the best gap
  (Koenig and Roshko, https://authors.library.caltech.edu/records/wd164-yjc15 ). Tractor-trailers: drag jumps
  above a gap of about 0.5 sqrt(A) and the rise sits on the trailer (Hammache and Browand 2004,
  https://www.researchgate.net/publication/267796269_On_the_Aerodynamics_of_Tractor-Trailers ).
  Here the gap is 1.61 m and sqrt(A) of the trailer about 2.2 m, so 0.72: the trailer face sees wake-like flow.
- Car and caravan on the road: Volvo V70 4.96 L/100 km alone and 10.77 L/100 km with a Bailey Ranger 440/4
  (2.19 x 2.70 m) at 90 km/h, Berjoza et al. 2025, https://www.iitf.lbtu.lv/conference/proceedings2025/Papers/TF083.pdf .
  Used below to check the base, friction and underbody terms.
"""

# ---------------------------------------------------------------- air and road
RHO = 1.20                 # kg/m3, 20 C at sea level (as research/models/19/loads.py). 35 C inland: 1.14
G = 9.81
CRR = 0.0095               # LT265/75R16 at highway pressure on chip seal, ute and trailer (est., 0.008 to 0.011)
M_UTE = 3546.3             # kg, ute with bikes and growth (GOAL-TRACKER key numbers)
M_TRAILER = 3400.0         # kg, H2 target fully loaded with growth
ETA_DRIVELINE = 0.88       # 5-speed manual, transfer case in 2H, beam axle (est.)
P_ACCESSORY = 1.5          # kW at the crank: alternator for the Orion-Tr chargers and RESPA fan, cooling fan (est.)
WILLANS_A = 2.0            # kg/h of fuel at zero output, 1VD-FTV at 1,700 to 1,950 rpm (est.)
WILLANS_B = 0.205          # kg per kWh marginal, about 41 % marginal brake efficiency (est.)
DIESEL_KG_L = 0.835        # report 16
PRICE_L = 2.10             # AUD/L (planning assumption)
KM_YEAR = 20000            # km of towing a year (planning assumption)
TANKS = {"130 L factory tank": 130.0, "180 L ARB Frontier (report 16, FT01)": 180.0}
RESERVE = 0.10             # keep 10 % in the tank

# ---------------------------------------------------------------- lead body: ute with the bike box (est.)
UTE_CD, UTE_AREA = 0.60, 3.10        # 79 cab chassis, 1.87 m wide, 1.97 m high, 85 % fill (est.)
BOX_W, BOX_TOP = 1.850, 2.336        # m, report 24 box outside width and top Z (planning assumption)
CAB_ROOF = 1.990                     # m, Z of the cab roof with the GVM lift (report 17 1,970 stock, est. +20)
BOX_STEP_CD = 0.70                   # box face above the cab roof, sharp edges, short gap (est.)
CDA_LEAD = UTE_CD * UTE_AREA + BOX_STEP_CD * BOX_W * (BOX_TOP - CAB_ROOF)
BOX_BASE_CD = 0.20                   # box rear face (est., as the trailer base)
BOX_BOTTOM = 0.895                   # m, the silhouette that matters starts at the trailer floor underside

# ---------------------------------------------------------------- trailer
T_W, T_L = 2.400, 4.420              # m, body width and length (trailer.json)
T_UNDER = 0.895                      # m, floor underside Z (trailer.json)
CD_FE = {"sharp": 0.80, "round": 0.25}   # forebody of the exposed face. Sharp: 30 mm joiner radius. Round: r 150 to 250 mm
CD_FS = 0.15                         # forebody inside the box silhouette at gap 0.72 sqrt(A) (est.)
CD_BASE = 0.20                       # square back, Cp about -0.2 (est.)
CF = 0.0030                          # turbulent plate at Re about 7e6
CDA_UNDER = 0.45                     # tandem XT axles and four wheels, drawbar, drawbar box, spare, mud flaps (est.)
RECOVERED = 0.5                      # share of the box's base drag removed by the trailer behind it (est.)

# Options: (label, roof top Z in m, edge treatment of the top front edge, of the vertical front edges)
OPTIONS = [
    ("A0 fixed 1,950 mm inside (committed model)", 2.917, "sharp", "sharp"),
    ("A  fixed 2,000 mm inside", 2.967, "sharp", "sharp"),
    ("A+ fixed 2,000 mm, radiused front edges", 2.967, "round", "round"),
    ("B  canvas pop-top, roof down", 2.345, "sharp", "sharp"),
    ("C  telescoping hard shell, roof down", 2.345, "sharp", "sharp"),
    ("C+ telescoping, roof down, radiused front edges", 2.345, "round", "round"),
    ("C' telescoping, lowered to 1,600 mm inside", 2.595, "sharp", "sharp"),
]


def areas(top):
    """Front-face areas in m2: exposed above the box, exposed beside the box, shielded, and the rear face."""
    h = top - T_UNDER
    front = T_W * h
    shield_h = max(0.0, min(top, BOX_TOP) - T_UNDER)
    shielded = BOX_W * shield_h
    beside = (T_W - BOX_W) * shield_h
    above = T_W * max(0.0, top - BOX_TOP)
    return {"front": front, "above": above, "beside": beside, "shielded": shielded, "rear": front, "h": h}


def trailer_cda(top, edge_top, edge_side, cd_fe=None, cd_base=CD_BASE):
    """Drag area in m2 that the trailer adds to the lead body, by term."""
    cd_fe = cd_fe or CD_FE
    a = areas(top)
    s_wet = T_L * T_W + 2 * T_L * a["h"]
    terms = {
        "exposed above": cd_fe[edge_top] * a["above"],
        "exposed beside": cd_fe[edge_side] * a["beside"],
        "shielded": CD_FS * a["shielded"],
        "base": cd_base * a["rear"],
        "friction": CF * s_wet,
        "underbody": CDA_UNDER,
        "box base recovered": -RECOVERED * BOX_BASE_CD * BOX_W * (BOX_TOP - BOX_BOTTOM),
    }
    return terms


def fuel(cda, kmh, mass=M_UTE + M_TRAILER, willans_b=WILLANS_B, crr=CRR):
    """Road load N, wheel kW, engine kW, L/h and L/100 km at a steady speed."""
    v = kmh / 3.6
    f = 0.5 * RHO * v * v * cda + crr * mass * G
    p_wheel = f * v / 1000
    p_engine = p_wheel / ETA_DRIVELINE + P_ACCESSORY
    kg_h = WILLANS_A + willans_b * p_engine
    l_h = kg_h / DIESEL_KG_L
    return {"F": f, "p_wheel": p_wheel, "p_engine": p_engine, "l_h": l_h, "l_100": l_h / kmh * 100}


def section(title):
    print("\n" + "=" * 100 + "\n" + title + "\n" + "=" * 100)


def combination(top, edge_top, edge_side, **kw):
    terms = trailer_cda(top, edge_top, edge_side, **kw)
    return CDA_LEAD + sum(terms.values()), terms


def calibration():
    """Volvo V70 and Bailey Ranger 440/4 at 90 km/h (Berjoza et al. 2025) against this model's terms."""
    section("Check: Volvo V70 with a Bailey Ranger 440/4 caravan at 90 km/h (Berjoza et al. 2025)")
    v = 25.0
    # Measured: 4.96 L/100 km alone, 10.77 with the caravan. Rolling coefficient 0.012 to 0.014 (paper).
    extra_g_km = (10.77 - 4.96) / 100 * DIESEL_KG_L * 1000            # g of diesel per km
    for b in (0.205, 0.225):
        wheel_kj_km = extra_g_km / (b * 1000 / 0.92) * 3600          # kJ per km at the wheels, driveline 0.92
        f_extra = wheel_kj_km                                        # N, since kJ/km = N
        f_roll = 1000 * G * 0.013                                    # caravan about 1,000 kg
        cda = (f_extra - f_roll) / (0.5 * RHO * v * v)
        print(f"marginal fuel {b * 1000:.0f} g/kWh: extra road load {f_extra:.0f} N, rolling {f_roll:.0f} N, "
              f"caravan drag area {cda:.2f} m2")
    # Model terms for the Bailey: body 2.19 m wide from Z 0.35 to 2.70, car shield 1.80 x (1.465 - 0.30) m
    front, shield = 2.19 * 2.35, 1.80 * 1.165
    fixed = CD_FS * shield + CD_BASE * front + CF * (4.6 * 2.19 + 2 * 4.6 * 2.35) + 0.20 - RECOVERED * 0.25 * shield
    print(f"model without the forebody term: {fixed:.2f} m2 on {front - shield:.2f} m2 of exposed face")
    for cda in (1.60, 1.75):
        print(f"  measured {cda:.2f} m2 implies a forebody coefficient of {(cda - fixed) / (front - shield):.2f} "
              f"for the Bailey's raked and rounded front")


def main():
    section("Inputs")
    print(f"Lead body CdA {CDA_LEAD:.2f} m2: ute {UTE_CD} x {UTE_AREA} m2, box face above the cab "
          f"{BOX_W} x {BOX_TOP - CAB_ROOF:.3f} m at {BOX_STEP_CD}")
    print(f"Mass {M_UTE + M_TRAILER:.0f} kg, Crr {CRR}, rho {RHO}, driveline {ETA_DRIVELINE}, "
          f"accessories {P_ACCESSORY} kW, Willans {WILLANS_A} kg/h + {WILLANS_B * 1000:.0f} g/kWh")
    print(f"Trailer {T_W} m wide, underside Z {T_UNDER}. Box silhouette {BOX_W} m wide to Z {BOX_TOP}. "
          f"Gap 1.61 m")
    print(f"Cd forebody exposed {CD_FE}, shielded {CD_FS}, base {CD_BASE}, Cf {CF}, underbody {CDA_UNDER} m2")

    section("Areas and drag area by option (m2)")
    print(f"{'option':50s} {'top Z':>6} {'front':>6} {'above':>6} {'beside':>6} {'shield':>6} "
          f"{'trailer':>8} {'total':>6}")
    rows = {}
    for label, top, et, es in OPTIONS:
        cda, terms = combination(top, et, es)
        a = areas(top)
        rows[label] = (cda, terms)
        print(f"{label:50s} {top:6.3f} {a['front']:6.2f} {a['above']:6.2f} {a['beside']:6.2f} "
              f"{a['shielded']:6.2f} {sum(terms.values()):8.2f} {cda:6.2f}")
    label_a = OPTIONS[1][0]
    print("\nTerms for A: " + ", ".join(f"{k} {v:.2f}" for k, v in rows[label_a][1].items()))

    section("Fuel, range and cost (still air, level road)")
    print(f"{'option':50s} {'kmh':>4} {'CdA':>5} {'F N':>6} {'wheel kW':>8} {'L/100':>6} {'d L/100':>7} "
          f"{'range 130 L':>11} {'range 180 L':>11} {'L/yr':>6} {'AUD/yr':>7}")
    base = {}
    out = {}
    for kmh in (90, 100):
        for label, top, et, es in OPTIONS:
            cda = rows[label][0]
            r = fuel(cda, kmh)
            if label == label_a:
                base[kmh] = r["l_100"]
            out[(label, kmh)] = r
    for kmh in (90, 100):
        for label, _, _, _ in OPTIONS:
            r = out[(label, kmh)]
            rng = [t * (1 - RESERVE) / r["l_100"] * 100 for t in TANKS.values()]
            litres = KM_YEAR * r["l_100"] / 100
            print(f"{label:50s} {kmh:4d} {rows[label][0]:5.2f} {r['F']:6.0f} {r['p_wheel']:8.1f} "
                  f"{r['l_100']:6.1f} {r['l_100'] - base[kmh]:+7.1f} {rng[0]:11.0f} {rng[1]:11.0f} "
                  f"{litres:6.0f} {litres * PRICE_L:7.0f}")
        print()

    section("Solo ute with the bike box (Toyota's combined test figure for the V8 is 10.7 L/100 km, 4X4 Australia)")
    solo = CDA_LEAD + BOX_BASE_CD * BOX_W * (BOX_TOP - BOX_BOTTOM) * RECOVERED
    for kmh in (90, 100):
        r = fuel(solo, kmh, mass=M_UTE)
        print(f"{kmh} km/h: CdA {solo:.2f} m2, {r['p_wheel']:.1f} kW at the wheels, {r['l_100']:.1f} L/100 km")

    section("Sensitivity: change against A at 90 km/h, L/100 km (low, central, high)")
    cases = {
        "central": dict(),
        "low drag gain": dict(cd_fe={"sharp": 0.65, "round": 0.40}, cd_base=0.15),
        "high drag gain": dict(cd_fe={"sharp": 0.95, "round": 0.15}, cd_base=0.25),
    }
    for name, kw in cases.items():
        cda_a = combination(2.967, "sharp", "sharp", **kw)[0]
        for b in (0.195, 0.205, 0.220):
            fa = fuel(cda_a, 90, willans_b=b)["l_100"]
            cells = []
            for label, top, et, es in OPTIONS[2:]:
                f = fuel(combination(top, et, es, **kw)[0], 90, willans_b=b)["l_100"]
                cells.append(f"{label[:2].strip()} {f - fa:+.1f}")
            print(f"{name:15s} b {b * 1000:.0f} g/kWh: A {fa:5.1f} L/100 km | " + ", ".join(cells))

    section("Height alone: each 50 mm of fixed roof height at 90 km/h")
    for edge in ("sharp", "round"):
        c1 = combination(2.967, edge, edge)[0]
        c2 = combination(2.917, edge, edge)[0]
        d = fuel(c1, 90)["l_100"] - fuel(c2, 90)["l_100"]
        print(f"{edge} edges: {c1 - c2:.3f} m2 and {d:.2f} L/100 km per 50 mm")

    calibration()
    dyno_check()


def dyno_check():
    """CarExpert: a V8 76 wagon (1VD-FTV) against a constant 3 kN trailer dynamometer used 35.3 L/100 km at about
    100 km/h in fourth (https://www.carexpert.com.au/car-videos/watch/iNcr8P1g). Wagon CdA and mass are est."""
    section("Check: the fuel model against CarExpert's 3 kN dynamometer trailer at 100 km/h")
    v = 100 / 3.6
    f = 3000 + 0.5 * RHO * v * v * 1.9 + CRR * 2800 * G
    p_engine = f * v / 1000 / ETA_DRIVELINE + P_ACCESSORY
    l_100 = (WILLANS_A + WILLANS_B * p_engine) / DIESEL_KG_L
    print(f"road load {f:.0f} N, engine {p_engine:.0f} kW, model {l_100:.1f} L/100 km against 35.3 measured")
    for label, top, et, es in OPTIONS[1:5]:
        r = fuel(combination(top, et, es)[0], 100)
        print(f"{label:50s} needs {r['p_engine']:.0f} kW at the crank at 100 km/h")


if __name__ == "__main__":
    main()

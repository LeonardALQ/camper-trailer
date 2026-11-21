"""Report 19 thermal loads for the home trailer (research/19-hvac-windows-doors.md, question 1 and 10).

Hourly quasi-steady heat balance of the 4,420 x 2,400 mm body, inside 4,350 x 2,330 x 1,950 mm.
Run: python3 loads.py > loads.out. No third-party modules.

Design hot day (planning assumption): 42 C peak at 15:00, 27 C at 03:00, cosine, clear sky, 1,000 W/m2 horizontal at noon, inside 24 C.
Design cold night (planning assumption): -5 C for 14 h (17:00 to 07:00), inside 20 C.
The sandwich skins are thin, so the panels store little heat and an hourly steady balance is close enough.

Report 25 copy (research/25-roof.md, question 3). Report 19's model is unchanged except for the report 25 block below the ventilation
constants and the two terms it feeds (canvas walls and the sliding-seal bridge, both zero by default), so
`python3 loads.py` still prints report 19's results. `python3 loads.py roof > loads.out` runs the roof options.
"""
import math
import sys

# ---------------------------------------------------------------- body geometry (report 12, data/body/body.yaml)
L, W = 4.420, 2.400                  # m, outside
H = 0.030 + 1.950 + 0.040            # m, floor + inside height + roof
IN_L, IN_W, IN_H = 4.350, 2.330, 1.950
VOLUME = IN_L * IN_W * IN_H          # m3, about 19.8 m3 gross. The 25 m3 first assumed is high
RHO_CP = 1.2 * 1006 / 3600           # W per (m3/h . K)
RHO_HFG = 1.2 * 2450 / 3600          # W per (m3/h . g/kg)

# ---------------------------------------------------------------- panel build-ups (report 12 section 2)
K_GRP = 0.30                         # W/m.K, polyester GRP skin (est.)
K_XPS = 0.031                        # W/m.K, Ravatherm XPS X 300 SL (report 12)
K_H80 = 0.031                        # W/m.K, Divinycell H80 (report 12)
RSI_WALL, RSI_UP, RSI_DOWN, RSE = 0.13, 0.10, 0.17, 0.04   # m2K/W, ISO 6946 surface resistances
BRIDGE = 1.20                        # thermal bridges: +20 % on the panel conduction (planning assumption, checked in the report)


def u_panel(core_m, k_core, skins_m, rsi, rse=RSE):
    """U of a sandwich panel in W/m2K."""
    return 1.0 / (rsi + rse + core_m / k_core + sum(s / K_GRP for s in skins_m))


def panels(extra_mm=(0, 0, 0)):
    """Core thicknesses in m for wall, roof and floor, with an optional addition in mm to each."""
    dw, dr, df = (e / 1000 for e in extra_mm)
    return {
        "wall": {"core": 0.032 + dw, "k": K_XPS, "skins": (0.0015, 0.0015)},
        "roof": {"core": 0.0365 + dr, "k": K_XPS, "skins": (0.002, 0.0015)},
        "floor": {"core": 0.026 + df, "k": K_H80, "skins": (0.002, 0.002)},
    }


# ---------------------------------------------------------------- openings (report 19 section 7 schedule; walls are the layout's to set)
# wall: kerb, road, front, rear. Sizes are the glass or leaf in m. Kerb side is the left side of the trailer.
WINDOWS = [
    ("W1 bed, emergency exit", "kerb", 0.90, 0.60),
    ("W2 bed and desk", "road", 0.90, 0.55),
    ("W3 desk", "front", 0.90, 0.45),
    ("W4 kitchen", "road", 0.70, 0.45),
    ("W5 living", "kerb", 0.90, 0.55),
    ("W6 wet room, obscured", "road", 0.50, 0.45),
    ("G1 entry door glass", "kerb", 0.35, 0.50),
    ("G2 rear door glass", "rear", 0.35, 0.50),
]
DOORS = [("D1 entry door leaf", "kerb", 0.622, 1.75), ("D2 rear door leaf", "rear", 0.622, 1.75),
         ("D3 cassette door", "road", 0.45, 0.29)]
U_WINDOW = 2.8                       # W/m2K, double acrylic with frame (est., report 19 section 7)
U_WINDOW_BLIND = 2.0                 # W/m2K, with the pleated blackout blind closed at night (est.)
U_DOOR = 1.6                         # W/m2K, insulated caravan door leaf (est.)
SHGC = 0.55                          # tinted double acrylic (est.)
IAC_BLIND = 0.55                     # fraction of the solar gain left with the pleated blackout blind closed (est.)

# ---------------------------------------------------------------- surface optics and sky (ASHRAE Fundamentals ch. 18)
ALPHA_WHITE = 0.40                   # dusty white gelcoat (est., 0.3 clean)
ALPHA_PV_HEAT = 0.72                 # bonded Sunman eArc: 0.90 absorbed less about 0.18 sent out as electricity (est.)
PV_AREA = 4.108 * 2.168              # m2 of the roof under the bonded array (report 13)
H_OUT = 17.0                         # W/m2K, outside film, 3.4 m/s wind
LW_HORIZONTAL = 3.9                  # K, long-wave loss of a horizontal surface to the sky (ASHRAE)
RHO_GROUND = 0.25                    # red soil
LATITUDE = -25.0                     # central Australia
DECLINATION = -23.44                 # 21 December

# ---------------------------------------------------------------- weather
T_IN_HOT, T_IN_COLD = 24.0, 20.0
W_IN_HOT = 9.3                        # g/kg, 24 C and 50 % RH
W_OUT_HOT = 6.5                       # g/kg, inland dew point about 7 C (est.)


def t_out_hot(hour, peak=42.0, low=27.0):
    """Cosine day, peak at 15:00 and low at 03:00, in C."""
    return (peak + low) / 2 + (peak - low) / 2 * math.cos(2 * math.pi * (hour - 15) / 24)


def sun_vector(hour):
    """Unit vector to the sun (east, north, up) at solar time `hour`, or None below the horizon."""
    phi, dec = math.radians(LATITUDE), math.radians(DECLINATION)
    h = math.radians(15 * (hour - 12))
    up = math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(h)
    if up <= 0.02:
        return None
    east = -math.cos(dec) * math.sin(h)
    north = math.cos(phi) * math.sin(dec) - math.sin(phi) * math.cos(dec) * math.cos(h)
    return east, north, up


def clear_sky(sin_alt):
    """ASHRAE 2009 clear-sky beam normal and diffuse horizontal, tau_b 0.45 and tau_d 2.4 (dusty inland sky)."""
    alt = math.degrees(math.asin(sin_alt))
    m = 1 / (sin_alt + 0.50572 * (6.07995 + alt) ** -1.6364)
    tb, td, e0 = 0.45, 2.4, 1412.0
    ab = 1.454 - 0.406 * tb - 0.268 * td + 0.021 * tb * td
    ad = 0.507 + 0.205 * tb - 0.080 * td - 0.190 * tb * td
    return e0 * math.exp(-tb * m ** ab), e0 * math.exp(-td * m ** ad)


def _noon_scale():
    """Scale factor that makes the horizontal total exactly 1,000 W/m2 at solar noon (planning assumption)."""
    s = sun_vector(12.0)
    dni, dhi = clear_sky(s[2])
    return 1000.0 / (dni * s[2] + dhi)


SCALE = _noon_scale()


def irradiance(hour, wall_azimuth=None):
    """Total irradiance in W/m2 on the roof (azimuth None) or on a vertical wall facing `wall_azimuth` (deg from N)."""
    s = sun_vector(hour)
    if s is None:
        return 0.0, 0.0
    dni, dhi = (SCALE * v for v in clear_sky(s[2]))
    ghi = dni * s[2] + dhi
    if wall_azimuth is None:
        return ghi, dni * s[2]
    a = math.radians(wall_azimuth)
    cos_i = max(0.0, s[0] * math.sin(a) + s[1] * math.cos(a))
    return dni * cos_i + 0.5 * dhi + 0.5 * RHO_GROUND * ghi, dni * cos_i


def wall_azimuths(heading):
    """Outward azimuths of the four walls when the trailer's front faces `heading`. Kerb side is the left."""
    return {"front": heading % 360, "road": (heading + 90) % 360,
            "rear": (heading + 180) % 360, "kerb": (heading + 270) % 360}


# ---------------------------------------------------------------- people and appliances (figures of the kind report 21 gives, est.)
def awake(hour):
    return 7 <= hour < 22


def people(hour):
    """Sensible and latent W for two adults inside all day (ASHRAE Fundamentals ch. 18 table 1)."""
    return (2 * 70, 2 * 45) if awake(hour) else (2 * 60, 2 * 25)


# Heat released into the room in W, by hour of the day (sensible, latent). Energy figures are report 21-type estimates.
def appliances_hot(hour, dryer_vented=False):
    s, lat = 0.0, 0.0
    s += 75                                   # fridge NRX 130C and freezer CFX3 55IM, 1.8 kWh on a hot day (report 13)
    s += 25 + 10 + 3                          # MultiPlus-II idle, router, Cerbo GX (est.)
    s += 10                                   # ERV fans into the supply air (est.)
    s += 20                                   # hot water storage and pipe losses (est., 0.5 kWh a day)
    if 9 <= hour < 17:
        s += 70                               # desk: laptop, monitor and Starlink router (dish outside)
        s += 0.03 * 1200 * math.sin(math.pi * (hour + 0.5 - 6) / 13)   # MPPT losses at up to 1.2 kW of PV (est.)
    if 18 <= hour < 23:
        s += 45                               # lights, screen, chargers
    if hour == 7:
        s += 0.5 * 1000; lat += 0.5 * 120     # breakfast on the hob, half to the hood (est.)
    if hour == 12:
        s += 0.5 * 600; lat += 0.5 * 80
    if hour == 18:
        s += 0.5 * 1400 + 0.7 * 1000; lat += 0.5 * 250   # dinner: hob and a 45 min oven bake (est.)
    if hour in (7, 19):
        s += 120; lat += 150                  # 20 min shower, the wet room extract takes most of it (est.)
    if hour in (10, 11) and not dryer_vented:
        s += 600                              # heat-pump dryer, 1.2 kWh into the room (est.)
    if hour == 9:
        s += 100                              # washer (est.)
    return s, lat


def appliances_cold(hour):
    s, lat = 0.0, 0.0
    s += 0.6 * 75 + 25 + 10 + 3 + 10 + 20     # fridge and freezer at 0.6 of the hot-day figure (report 13), standby
    if 17 <= hour < 22:
        s += 45 + 70
    if hour == 18:
        s += 0.5 * 1400 + 0.7 * 1000; lat += 0.5 * 250
    if hour in (6, 19):
        s += 120; lat += 150
    return s, lat


# ---------------------------------------------------------------- ventilation (report 19 sections 3 to 5)
# Balanced exchange through two pairs of LUNOS e2 60 regenerative fans (section 3). Unrecovered outdoor air comes in
# as the pressurisation top-up from the filtered dust fan (section 4), the makeup for the wet room boost and the
# range hood (section 5), and gusts and door openings.
ERV_FLOW = {"day": 60.0, "night": 45.0}       # m3/h exchanged by the two e2 60 pairs (section 3)
EPS_SENS, EPS_LAT = 0.80, 0.20                 # e2 60: 83 % at up to 60 m3/h (maker), moisture 20 to 30 % (475 Supply)
TOP_UP = 15.0                                  # m3/h of filtered supply above the extract, parked (section 4)
INFILTRATION_ACH = 0.1                         # gusts and door openings (est.)
SHOWER_BOOST = {7: (60.0, 0.5), 19: (60.0, 0.5)}           # hour: (extra m3/h, hours), wet room fan on boost
HOOD = {7: (100.0, 0.5), 12: (100.0, 0.25), 18: (100.0, 1.0)}   # hour: (m3/h, hours), range hood on low


# ---------------------------------------------------------------- report 25 roof options (defaults reproduce report 19)
CANVAS_H = 0.0          # m of canvas skirt all round between the lower walls and the lid (option B)
U_CANVAS = 5.5          # W/m2K, single polycotton layer with its air films, 0.13 + 0.04 + 0.01 m2K/W (est.)
ALPHA_CANVAS = 0.55     # sand or grey canvas (est.)
TAU_CANVAS = 0.03       # sun passing through the canvas as light (est.)
SEAL_UA = 0.0           # W/K, the two aluminium rails at the sliding joint of option C
EXTRA_AIR = 0.0         # m3/h of unrecovered outdoor air through canvas zips or the sliding seal


def awake_flow(hour):
    return ERV_FLOW["day"] if awake(hour) else ERV_FLOW["night"]


def supply(hour):
    """Recovered exchange through the e2 pairs, m3/h."""
    return awake_flow(hour)


def unrecovered(hour):
    """Hour-average m3/h of outdoor air that bypasses heat recovery."""
    q = TOP_UP + INFILTRATION_ACH * VOLUME + EXTRA_AIR
    for table in (SHOWER_BOOST, HOOD):
        if hour in table:
            flow, hours = table[hour]
            q += flow * hours
    return q


# ---------------------------------------------------------------- envelope
def wall_areas():
    """Gross outside areas in m2 of the four walls (panel part only), the roof and the floor."""
    hp = H - CANVAS_H
    return {"kerb": L * hp, "road": L * hp, "front": W * hp, "rear": W * hp, "roof": L * W, "floor": L * W}


def opening_area(items, wall):
    return sum(w * h for _, side, w, h in items if side == wall)


def envelope_ua(extra_mm=(0, 0, 0), night_blinds=False):
    """UA in W/K by element: opaque panels with the bridge factor, windows, doors."""
    p = panels(extra_mm)
    u_wall = u_panel(p["wall"]["core"], p["wall"]["k"], p["wall"]["skins"], RSI_WALL)
    ua = {}
    for wall in ("kerb", "road", "front", "rear"):
        net = wall_areas()[wall] - opening_area(WINDOWS, wall) - opening_area(DOORS, wall)
        ua[wall] = BRIDGE * u_wall * net
    ua["windows"] = (U_WINDOW_BLIND if night_blinds else U_WINDOW) * sum(w * h for _, _, w, h in WINDOWS)
    ua["doors"] = U_DOOR * sum(w * h for _, _, w, h in DOORS)
    return ua, p, u_wall


def hot_hour(hour, heading, extra_mm=(0, 0, 0), blinds="sunlit", roof="pv", dryer_vented=False,
             t_peak=42.0, t_low=27.0, w_out=W_OUT_HOT, w_in=W_IN_HOT):
    """Heat gains in W for one hour of the hot day. Returns a dict of components."""
    t = hour + 0.5
    to = t_out_hot(t, t_peak, t_low)
    ti = T_IN_HOT
    ua, p, u_wall = envelope_ua(extra_mm)
    az = wall_azimuths(heading)
    g = {}
    # roof: PV-covered part and the white margin, sol-air temperature
    ghi, _ = irradiance(t)
    u_roof = u_panel(p["roof"]["core"], p["roof"]["k"], p["roof"]["skins"], RSI_DOWN)
    alpha_pv = ALPHA_PV_HEAT if roof == "pv" else ALPHA_WHITE
    a_roof = L * W
    t_sa_pv = to + alpha_pv * ghi / H_OUT - LW_HORIZONTAL
    t_sa_white = to + ALPHA_WHITE * ghi / H_OUT - LW_HORIZONTAL
    g["roof"] = BRIDGE * u_roof * (PV_AREA * (t_sa_pv - ti) + (a_roof - PV_AREA) * (t_sa_white - ti))
    # floor: the underside sees ground shaded by the body (est. +3 K at noon)
    u_floor = u_panel(p["floor"]["core"], p["floor"]["k"], p["floor"]["skins"], RSI_UP)
    g["floor"] = BRIDGE * u_floor * L * W * (to + 3 * ghi / 1000 - ti)
    # walls, windows and doors
    g["walls"] = g["win_cond"] = g["win_solar"] = g["doors"] = 0.0
    for wall in ("kerb", "road", "front", "rear"):
        iv, beam = irradiance(t, az[wall])
        g["walls"] += ua[wall] * (to + ALPHA_WHITE * iv / H_OUT - ti)
        for _, side, w, h in WINDOWS:
            if side != wall:
                continue
            g["win_cond"] += U_WINDOW * w * h * (to - ti)
            shade_down = blinds == "down" or (blinds == "sunlit" and beam > 50)
            g["win_solar"] += w * h * iv * SHGC * (IAC_BLIND if shade_down else 1.0)
        for _, side, w, h in DOORS:
            if side == wall:
                g["doors"] += U_DOOR * w * h * (to + ALPHA_WHITE * iv / H_OUT - ti)
    # Report 25: canvas skirt (option B) and sliding-seal rails (option C). Both are zero for report 19's body
    g["canvas"] = 0.0
    for wall, length in (("kerb", L), ("road", L), ("front", W), ("rear", W)):
        iv, _ = irradiance(t, az[wall])
        a_c = length * CANVAS_H
        g["canvas"] += U_CANVAS * a_c * (to + ALPHA_CANVAS * iv / H_OUT - ti) + TAU_CANVAS * a_c * iv
    g["seal"] = SEAL_UA * (to - ti)
    # ventilation and infiltration
    q = supply(hour)
    q_inf = unrecovered(hour)
    g["vent_sens"] = RHO_CP * q * (to - ti) * (1 - EPS_SENS) + RHO_CP * q_inf * (to - ti)
    vent_lat = RHO_HFG * q * (w_out - w_in) * (1 - EPS_LAT) + RHO_HFG * q_inf * (w_out - w_in)
    ps, pl = people(hour)
    as_, al = appliances_hot(hour, dryer_vented)
    g["people_sens"], g["appl_sens"] = ps, as_
    g["latent"] = pl + al + vent_lat
    g["sensible"] = sum(g[k] for k in ("roof", "floor", "walls", "win_cond", "win_solar", "doors",
                                       "vent_sens", "people_sens", "appl_sens", "canvas", "seal"))
    g["t_out"] = to
    return g


def cold_hour(hour, extra_mm=(0, 0, 0), gains=True, t_out=-5.0):
    """Heat to add in W for one night hour (positive = heating needed)."""
    ti = T_IN_COLD
    ua, p, _ = envelope_ua(extra_mm, night_blinds=True)
    u_roof = u_panel(p["roof"]["core"], p["roof"]["k"], p["roof"]["skins"], RSI_UP)
    u_floor = u_panel(p["floor"]["core"], p["floor"]["k"], p["floor"]["skins"], RSI_DOWN)
    loss = {}
    loss["roof"] = BRIDGE * u_roof * L * W * (ti - (t_out - 4.0))       # clear night sky (est.)
    loss["floor"] = BRIDGE * u_floor * L * W * (ti - (t_out + 1.0))     # ground under the body (est.)
    loss["walls"] = sum(ua[w] for w in ("kerb", "road", "front", "rear")) * (ti - t_out)
    loss["windows"] = ua["windows"] * (ti - t_out)
    loss["doors"] = ua["doors"] * (ti - t_out)
    loss["canvas"] = U_CANVAS * 2 * (L + W) * CANVAS_H * (ti - t_out)      # report 25, zero for report 19's body
    loss["seal"] = SEAL_UA * (ti - t_out)                                  # report 25, zero for report 19's body
    loss["vent"] = RHO_CP * supply(hour) * (ti - t_out) * (1 - EPS_SENS) + RHO_CP * unrecovered(hour) * (ti - t_out)
    total_loss = sum(loss.values())
    gain = 0.0
    if gains:
        ps, _ = people(hour)
        as_, _ = appliances_cold(hour)
        gain = ps + as_
    loss["gains"] = -gain
    loss["net"] = max(0.0, total_loss - gain)
    loss["gross"] = total_loss
    return loss


NIGHT_HOURS = list(range(17, 24)) + list(range(0, 7))     # 14 h, 17:00 to 07:00

# ---------------------------------------------------------------- cooling and heating units (report 19 section 2)
# cool: three (capacity kW, COP) points at 35 C outside (AS/NZS 3823 T1 or ISO 5151): minimum, rated, maximum.
#       Between the points the COP is interpolated on capacity. Below the minimum the unit cycles.
# heat: (outside C, maximum capacity kW, COP near 1.3 kW). heat_min: lowest steady heating output in kW.
# t_max, t_min_heat: outdoor limits from the maker. dc: runs from the 24 V battery with no inverter loss.
UNITS = {
    "Mitsubishi MSZ-AP25VGKD2 split": dict(
        # maker: 2.5 kW at 0.50 kW, 1.10 kW at 0.21 kW, 3.60 kW at 0.99 kW (mitsubishielectric.com.au)
        cool=[(1.10, 1.10 / 0.21), (2.5, 2.5 / 0.50), (3.60, 3.60 / 0.99)],
        # maker at 7 C: 1.3 to 5.0 kW, rated 3.2 kW at 0.67 kW. Below 7 C: est. from a typical R32 inverter
        heat=[(-15, 2.4, 2.0), (-10, 2.8, 2.4), (-5, 3.3, 2.9), (2, 4.0, 3.7), (7, 5.0, 4.5)],
        heat_min=1.3, t_max=46, t_min_heat=-15, dc=False),
    "Mitsubishi MSZ-AP35VGKD2 split": dict(
        # maker: 3.5 kW at 0.87 kW, 1.10 kW at 0.21 kW, 4.10 kW at 1.18 kW. Heating 1.3 to 5.1 kW, 3.7 kW at 0.82 kW
        cool=[(1.10, 1.10 / 0.21), (3.5, 3.5 / 0.87), (4.10, 4.10 / 1.18)],
        heat=[(-15, 2.5, 2.0), (-10, 2.9, 2.4), (-5, 3.4, 2.8), (2, 4.1, 3.6), (7, 5.1, 4.4)],
        heat_min=1.3, t_max=46, t_min_heat=-15, dc=False),
    "Cool-J iHider220 under-bench inverter": dict(
        # retailer: 2.93 kW cooling at 872 to 1,002 W (EER 3.0), 2.78 kW heat pump COP 3.4, -7 to +43 C. Min est.
        cool=[(2.0, 3.1), (2.93, 3.0)],
        heat=[(-7, 1.8, 2.2), (7, 2.78, 3.4)],
        heat_min=1.5, t_max=43, t_min_heat=-7, dc=False),
    "Dometic FreshJet FJZ7 Pro rooftop": dict(
        # maker: 3.4 kW ISO 5151, 6.1 A max. COP points est. from the 6.1 A (about 1.4 kW at full output)
        cool=[(1.2, 3.3), (3.4, 3.0), (3.7, 2.6)],
        heat=[(-2, 2.2, 2.2), (7, 3.4, 3.0)],
        heat_min=1.2, t_max=52, t_min_heat=-2, dc=False),
    "Truma Saphir Comfort RC under-bench": dict(
        # maker: 2.4 kW cooling at 4.2 A, 1.7 kW heating at 3.7 A, +4 to +43 C. Fixed speed, so one point
        cool=[(2.4, 2.4 / 0.97)],
        heat=[(4, 1.7, 2.0), (7, 1.7, 2.0)],
        heat_min=1.7, t_max=43, t_min_heat=4, dc=False),
    "Dometic FreshWell 3000 under-bench": dict(
        # report 13: 2.7 kW cooling at 990 W, 3.0 kW heat pump. Fixed speed. Limits est. as the Saphir
        cool=[(2.7, 2.7 / 0.99)],
        heat=[(4, 3.0, 2.5), (7, 3.0, 2.5)],
        heat_min=3.0, t_max=43, t_min_heat=4, dc=False),
    "Dometic CoolAir RTX 2000 24 V rooftop": dict(
        # maker: 2.0 kW, 5 to 30 A at 24 V, +5 to +52 C, cooling only. Minimum point est. at 0.5 kW and 120 W
        cool=[(0.5, 0.5 / 0.12), (2.0, 2.0 / 0.72)],
        heat=None, heat_min=None, t_max=52, t_min_heat=None, dc=True),
}
INVERTER_EFF = 0.93                  # MultiPlus-II at 0.3 to 1 kW (Victron efficiency curve, est.)
CYCLING_CD = 0.25                    # cycling degradation below the minimum output (AHRI default)
COP_PER_K = 0.025                    # COP falls about 2.5 % per K above 35 C outside (est.)
CAP_PER_K = 0.010                    # capacity falls about 1 % per K above 35 C outside (est.)


def _interp(points, x):
    pts = sorted(points)
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (x - x0) / (x1 - x0) * (y1 - y0)
    return pts[-1][1]


def cool_cop(unit, t_out, load_kw):
    """Electrical input in kW for a cooling load in kW, and the unmet load in kW."""
    if load_kw <= 0:
        return 0.0, 0.0
    if t_out > unit["t_max"]:
        return 0.0, load_kw
    pts = unit["cool"]
    f_t = max(0.4, 1 - COP_PER_K * max(0.0, t_out - 35))
    cap_max = pts[-1][0] * max(0.6, 1 - CAP_PER_K * max(0.0, t_out - 35))
    cap_min = pts[0][0]
    met = min(load_kw, cap_max)
    if met >= cap_min:
        p = met / (_interp(pts, met) * f_t)
    else:
        plf = 1 - CYCLING_CD * (1 - met / cap_min)
        p = met / (pts[0][1] * f_t * plf)
    return p, load_kw - met


def heat_cop(unit, t_out, load_kw):
    """Electrical input in kW for a heating load in kW, and the unmet load in kW."""
    if not unit["heat"] or load_kw <= 0:
        return 0.0, max(load_kw, 0.0)
    if t_out < unit["t_min_heat"]:
        return 0.0, load_kw
    cap_max = _interp([(t, c) for t, c, _ in unit["heat"]], t_out)
    cop = _interp([(t, k) for t, _, k in unit["heat"]], t_out)
    met = min(load_kw, cap_max)
    base = unit["heat_min"]
    plf = 1.0 if met >= base else 1 - CYCLING_CD * (1 - met / base)
    return met / (cop * plf), load_kw - met


def battery_kwh(unit, ac_kwh):
    return ac_kwh if unit["dc"] else ac_kwh / INVERTER_EFF

# ---------------------------------------------------------------- extra checks (sections 2 to 5 and 10)
CHOSEN = "Mitsubishi MSZ-AP25VGKD2 split"
DIESEL_HEATER_W = 30                 # Truma Combi D 6 fan and controls, 12 V side, average at 1 to 2 kW (est.)
DIESEL_L_PER_KWH = 0.110             # 110 ml/h at an average 1 kW (report 13, Truma)


def chosen_profile(rows, night):
    """Hourly electrical input of the chosen unit, for report 20's energy model."""
    unit = UNITS[CHOSEN]
    section(f"{CHOSEN}: hourly input, AC side W (battery side = AC / {INVERTER_EFF})")
    hot = [cool_cop(unit, r["t_out"], (r["sensible"] + max(0.0, r["latent"])) / 1000)[0] * 1000 for r in rows]
    print("hot day  " + " ".join(f"{h:02d}:{w:4.0f}" for h, w in enumerate(hot)))
    cold = [heat_cop(unit, -5.0, r["net"] / 1000)[0] * 1000 for r in night]
    print("cold     " + " ".join(f"{h:02d}:{w:4.0f}" for h, w in zip(NIGHT_HOURS, cold)))
    worst12 = max(sum((hot + hot)[i:i + 12]) for i in range(24)) / 1000
    print(f"hot day {sum(hot) / 1000:.2f} kWh AC, worst 12 h window {worst12:.2f} kWh AC, peak {max(hot):.0f} W")
    q_night = sum(r["net"] for r in night) / 1000
    print(f"cold night {sum(cold) / 1000:.2f} kWh AC with the heat pump. With the Combi D 6 instead: "
          f"{q_night * DIESEL_L_PER_KWH:.1f} L of diesel and {DIESEL_HEATER_W * 14 / 1000:.2f} kWh at 12 V")


def panel_mass_change(extra_mm):
    """kg added by thicker cores: XPS 33 kg/m3 in walls and roof, H80 80 kg/m3 in the floor, extrusions 0.06 kg/m per mm."""
    dw, dr, df = extra_mm
    walls = sum(wall_areas()[w] for w in ("kerb", "road", "front", "rear")) - 5.0   # less the openings
    kg = 33 * walls * dw / 1000 + 33 * L * W * dr / 1000 + 80 * L * W * df / 1000
    kg += 0.06 * 35.0 * max(extra_mm) / 10        # 35 m of joiners grow with the thickest panel (est.)
    return kg


def insulation_tradeoff(hd):
    unit = UNITS[CHOSEN]
    section("Insulation trade-off: core added to walls, roof and floor (mm), chosen unit, 7 kg of battery per kWh a day")
    base_hot = unit_day(unit, hot_day(hd))[1]
    base_cold = unit_night(unit, [cold_hour(h) for h in NIGHT_HOURS])[1]
    print(f"{'walls/roof/floor +mm':>22} {'hot kWh':>8} {'saved':>6} {'cold kWh':>9} {'saved':>6} {'panel kg':>9} {'battery kg':>11} {'net kg':>7}")
    cases = [(0, 0, 0)] + [(s, 0, 0) for s in (10, 20, 30)] + [(0, s, 0) for s in (10, 20, 30)] \
        + [(0, 0, s) for s in (10, 20, 30)] + [(s, s, 0) for s in (10, 20, 30)] + [(s, s, s) for s in (10, 20, 30)]
    for c in cases:
        hot = unit_day(unit, hot_day(hd, extra_mm=c))[1]
        cold = unit_night(unit, [cold_hour(h, extra_mm=c) for h in NIGHT_HOURS])[1]
        kg = panel_mass_change(c)
        battery = 7 * (base_hot - hot)
        print(f"{str(c):>22} {hot:8.2f} {base_hot - hot:6.2f} {cold:9.2f} {base_cold - cold:6.2f} {kg:9.1f} {battery:11.1f} {kg - battery:7.1f}")


def co2_check():
    """Steady CO2 for two adults (Persily and de Jonge 2017 rates), outdoor 425 ppm."""
    section("CO2 at steady state, two adults, outdoor 425 ppm")
    rates = {"asleep, 1.0 met": 0.0039, "seated, 1.3 met": 0.0050, "light work, 2.0 met": 0.0077}   # L/s per person
    for flow in (20, 30, 40, 50, 60, 80):
        q = flow / 3.6                                              # L/s
        cells = [f"{name} {425 + 2 * g / q * 1e6:5.0f}" for name, g in rates.items()]
        print(f"{flow:3d} m3/h: " + ", ".join(cells) + " ppm")
    for name, g in rates.items():
        print(f"flow for 1,000 ppm, {name}: {2 * g / (1000e-6 - 425e-6) * 3.6:.0f} m3/h")


def w_sat(t):
    """Saturation humidity ratio in g/kg at t C (Magnus formula, 101.3 kPa)."""
    p = 0.61094 * math.exp(17.625 * t / (t + 243.04))
    return 622 * p / (101.325 - p)


def dew_point(w):
    lo, hi = -40.0, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if w_sat(mid) < w else (lo, mid)
    return lo


def condensation_check():
    section("Cold night condensation: steady indoor humidity and the coldest surfaces, -5 C outside, 20 C inside")
    w_out = 0.9 * w_sat(-5.0)
    # g/h reaching the living space: asleep 2 x 40, towels on a rail 50, the evening hour with the hood and the wet
    # room fan on boost (half the cooking steam and a third of the shower steam escape them, est.) 200
    sources = {"two asleep": 80.0, "two asleep + drying towels": 130.0, "evening hour: cooking and a shower": 200.0}
    cases = (("e2 pairs only", ERV_FLOW["night"], EPS_LAT),
             ("e2 + top-up", ERV_FLOW["night"] + TOP_UP, EPS_LAT * ERV_FLOW["night"] / (ERV_FLOW["night"] + TOP_UP)),
             ("e2 boost + top-up", 100.0 + TOP_UP, EPS_LAT * 100.0 / (100.0 + TOP_UP)))
    for name, g_h in sources.items():
        for label, q, eps in cases:
            w_in = w_out + g_h / (1.2 * q * (1 - eps))
            rh = 100 * w_in / w_sat(20.0)
            print(f"{name:38s} {label:14s} {q:4.0f} m3/h: {w_in:4.1f} g/kg, RH {rh:3.0f} %, dew point {dew_point(w_in):5.1f} C")
    surfaces = {"wall panel": 0.825, "window, blind open": U_WINDOW, "window, blind closed (glass face)": 2.4,
                "aluminium corner joiner, f_Rsi 0.60 (est.)": None, "door leaf": U_DOOR}
    for name, u in surfaces.items():
        t = -5 + 0.60 * 25 if u is None else 20 - u * 0.13 * 25
        print(f"inside surface temperature, {name}: {t:5.1f} C")


def pressure_check():
    section("Body pressurisation: excess supply needed, sealed body ELA 30 to 60 cm2 (est.)")
    for ela_cm2 in (30, 45, 60):
        a = ela_cm2 / 1e4
        for dp in (5, 10, 20, 50, 100):
            q = 0.61 * a * math.sqrt(2 * dp / 1.2) * 3600
            print(f"ELA {ela_cm2} cm2, {dp:3d} Pa across the leaks: {q:5.0f} m3/h")
    for kmh in (40, 60, 80, 100):
        v = kmh / 3.6
        q = 0.5 * 1.2 * v * v
        print(f"{kmh:3d} km/h: dynamic pressure {q:4.0f} Pa, rear wake at Cp -0.3: {-0.3 * q:5.0f} Pa, "
              f"upper front at Cp +0.6: {0.6 * q:5.0f} Pa")


# ---------------------------------------------------------------- runs
def hot_day(heading, **kw):
    return [hot_hour(h, heading, **kw) for h in range(24)]


def day_totals(rows):
    sens = sum(r["sensible"] for r in rows) / 1000
    lat = sum(max(0.0, r["latent"]) for r in rows) / 1000
    peak = max(rows, key=lambda r: r["sensible"] + max(0.0, r["latent"]))
    return sens, lat, peak


def worst_heading(**kw):
    """The heading (front facing N, E, S or W) with the largest 24 h heat to remove."""
    return max((0, 90, 180, 270), key=lambda hd: sum(day_totals(hot_day(hd, **kw))[:2]))


def unit_day(unit, rows):
    """AC-side and battery-side kWh of a unit over the hot day, and the unmet heat in kWh."""
    e, unmet = 0.0, 0.0
    for r in rows:
        load = (r["sensible"] + max(0.0, r["latent"])) / 1000
        p, u = cool_cop(unit, r["t_out"], load)
        e, unmet = e + p, unmet + u
    return e, battery_kwh(unit, e), unmet


def unit_night(unit, rows):
    e, unmet = 0.0, 0.0
    for r in rows:
        p, u = heat_cop(unit, -5.0, r["net"] / 1000)
        e, unmet = e + p, unmet + u
    return e, battery_kwh(unit, e), unmet


def section(title):
    print("\n" + "=" * 100 + "\n" + title + "\n" + "=" * 100)


def main():
    ua, p, u_wall = envelope_ua()
    u_roof = u_panel(p["roof"]["core"], p["roof"]["k"], p["roof"]["skins"], RSI_DOWN)
    u_floor = u_panel(p["floor"]["core"], p["floor"]["k"], p["floor"]["skins"], RSI_UP)
    section("Envelope")
    print(f"Inside volume {VOLUME:.1f} m3, floor {IN_L * IN_W:.1f} m2")
    print(f"U wall {u_wall:.3f}, roof {u_roof:.3f} (heat down), floor {u_floor:.3f} W/m2K, bridge factor {BRIDGE}")
    print(f"Glass {sum(w * h for _, _, w, h in WINDOWS):.2f} m2, door leaves {sum(w * h for _, _, w, h in DOORS):.2f} m2")
    ua_roof, ua_floor = BRIDGE * u_roof * L * W, BRIDGE * u_floor * L * W
    print("UA W/K: " + ", ".join(f"{k} {v:.1f}" for k, v in ua.items()) + f", roof {ua_roof:.1f}, floor {ua_floor:.1f}")
    print(f"UA total {sum(ua.values()) + ua_roof + ua_floor:.1f} W/K")

    hd = worst_heading()
    rows = hot_day(hd)
    section(f"Design hot day, PV roof, blinds down on sunlit glass, worst heading: front faces {hd} deg (kerb faces {(hd + 270) % 360})")
    cols = ("t_out", "roof", "floor", "walls", "win_cond", "win_solar", "doors", "vent_sens", "people_sens", "appl_sens", "sensible", "latent")
    print("hour " + " ".join(f"{c:>10}" for c in cols) + "      total")
    for h, r in enumerate(rows):
        print(f"{h:02d}   " + " ".join(f"{r[c]:10.0f}" if c != "t_out" else f"{r[c]:10.1f}" for c in cols)
              + f" {r['sensible'] + max(0, r['latent']):10.0f}")
    sens, lat, peak = day_totals(rows)
    print(f"24 h heat to remove: sensible {sens:.1f} kWh, latent {lat:.1f} kWh, total {sens + lat:.1f} kWh")
    print(f"Peak {peak['sensible'] + max(0, peak['latent']):.0f} W at {peak['t_out']:.1f} C outside")
    comp = {c: sum(r[c] for r in rows) / 1000 for c in cols[1:10]}
    print("24 h by component kWh: " + ", ".join(f"{k} {v:.1f}" for k, v in comp.items()))

    section("Hot day variants (24 h total heat to remove kWh, peak W)")
    variants = {
        "design: PV roof, blinds down on sunlit glass": dict(),
        "blinds up all day": dict(blinds="up"),
        "blinds down all day": dict(blinds="down"),
        "white roof, no PV (the roof first assumed)": dict(roof="white"),
        "vented dryer in place of a heat-pump dryer": dict(dryer_vented=True),
        "tropical day: 35 C peak, 27 C low, dew point 25 C": dict(t_peak=35, t_low=27, w_out=20.0, w_in=10.3),
    }
    for name, kw in variants.items():
        hdv = worst_heading(**kw)
        s, l, pk = day_totals(hot_day(hdv, **kw))
        print(f"{name:55s} heading {hdv:3d}: {s + l:5.1f} kWh (latent {l:4.1f}), peak {pk['sensible'] + max(0, pk['latent']):5.0f} W")
    for heading in (0, 90, 180, 270):
        s, l, pk = day_totals(hot_day(heading))
        print(f"heading {heading:3d}: {s + l:5.1f} kWh, peak {pk['sensible'] + max(0, pk['latent']):5.0f} W")

    night = [cold_hour(h) for h in NIGHT_HOURS]
    section("Design cold night, -5 C outside, 20 C inside, 14 h from 17:00, blinds closed")
    keys = ("roof", "floor", "walls", "windows", "doors", "vent", "gains", "net")
    print("hour " + " ".join(f"{k:>9}" for k in keys))
    for h, r in zip(NIGHT_HOURS, night):
        print(f"{h:02d}   " + " ".join(f"{r[k]:9.0f}" for k in keys))
    gross = cold_hour(2, gains=False)["gross"]
    print(f"Heat loss with no internal gains {gross:.0f} W. Net heat to add over 14 h {sum(r['net'] for r in night) / 1000:.1f} kWh")

    section("Units on the design hot day and the design cold night")
    for name, unit in UNITS.items():
        ac, bat, unmet = unit_day(unit, rows)
        hac, hbat, hunmet = unit_night(unit, night)
        print(f"{name:40s} hot day {ac:5.1f} kWh AC, {bat:5.1f} kWh battery, unmet {unmet:4.1f} kWh | "
              f"cold night {hac:4.1f} kWh AC, {hbat:4.1f} kWh battery, unmet {hunmet:4.1f} kWh")
    chosen_profile(rows, night)
    tropical = dict(t_peak=35, t_low=27, w_out=20.0, w_in=10.3)
    trop_rows = hot_day(worst_heading(**tropical), **tropical)
    section("Units on the tropical day (35 C peak, 27 C low, dew point 25 C)")
    for name, unit in UNITS.items():
        ac, bat, unmet = unit_day(unit, trop_rows)
        print(f"{name:40s} {ac:5.1f} kWh AC, {bat:5.1f} kWh battery, unmet {unmet:4.1f} kWh")
    insulation_tradeoff(hd)
    co2_check()
    condensation_check()
    pressure_check()
    return rows, night, hd


# ---------------------------------------------------------------- report 25 roof options in camp mode
KG_PER_KWH = 8.8              # kg of battery per kWh a day (report 20, 20 Nov 2026)
FLOOR_T, ROOF_T = 0.030, 0.040
R25_UNITS = ("Mitsubishi MSZ-AP25VGKD2 split", "Mitsubishi MSZ-AP35VGKD2 split")
R25_OPTIONS = {
    "A0 fixed, 1,950 mm (report 19 run)": dict(in_h=1.950),
    "A  fixed, 2,000 mm": dict(in_h=2.000),
    "B  canvas skirt 650 mm, no liner": dict(in_h=2.000, canvas_h=0.65, u_canvas=5.5, extra_air=50.0),
    "B  canvas skirt 650 mm, quilted liner": dict(in_h=2.000, canvas_h=0.65, u_canvas=2.3, extra_air=50.0),
    "C  telescoping hard shell, 2,000 mm": dict(in_h=2.000, seal_ua=2.0, extra_air=7.0),
}


def set_option(in_h, canvas_h=0.0, u_canvas=5.5, seal_ua=0.0, extra_air=0.0):
    """Set the module geometry for one roof option in camp mode (roof raised)."""
    global H, IN_H, VOLUME, CANVAS_H, U_CANVAS, SEAL_UA, EXTRA_AIR
    IN_H, H, VOLUME = in_h, FLOOR_T + in_h + ROOF_T, IN_L * IN_W * in_h
    CANVAS_H, U_CANVAS, SEAL_UA, EXTRA_AIR = canvas_h, u_canvas, seal_ua, extra_air


def r25_main():
    section("Report 25 roof options in camp mode: design hot day (worst heading) and design cold night (-5 C, 14 h)")
    print("B: canvas U 5.5 W/m2K bare or 2.3 with a quilted liner (est.), absorptance 0.55, 50 m3/h of extra "
          "unrecovered air through zips and fabric (est.).\nC: two sliding-seal rails at 2.0 W/K and 7 m3/h of "
          "extra air through the seal (est.).")
    out = {}
    for name, opt in R25_OPTIONS.items():
        set_option(**opt)
        hd = worst_heading()
        rows = hot_day(hd)
        sens, lat, peak = day_totals(rows)
        night = [cold_hour(h) for h in NIGHT_HOURS]
        q_night = sum(r["net"] for r in night) / 1000
        canvas = sum(r["canvas"] for r in rows) / 1000
        units = {u: unit_day(UNITS[u], rows) + unit_night(UNITS[u], night) for u in R25_UNITS}
        out[name] = (sens + lat, peak["sensible"] + max(0.0, peak["latent"]), q_night, canvas, units)
    print(f"\n{'option':40s} {'heat kWh':>8} {'peak W':>7} {'canvas':>7} {'night kWh':>9} | "
          f"{'unit':>4} {'hot AC':>6} {'hot bat':>7} {'unmet':>5} {'cold bat':>8} {'unmet':>5} "
          f"{'d bat kWh':>9} {'d bat kg':>8}")
    ref = out["A  fixed, 2,000 mm"][4][R25_UNITS[0]][1]
    for name, (heat, peak, q_night, canvas, units) in out.items():
        for u in R25_UNITS:
            ac, bat, unmet, hac, hbat, hunmet = units[u]
            print(f"{name:40s} {heat:8.1f} {peak:7.0f} {canvas:7.1f} {q_night:9.1f} | {u[15:19]:>4} {ac:6.2f} "
                  f"{bat:7.2f} {unmet:5.2f} {hbat:8.2f} {hunmet:5.2f} {bat - ref:+9.2f} "
                  f"{KG_PER_KWH * (bat - ref):+8.1f}")
    set_option(in_h=1.950)


if __name__ == "__main__":
    if "roof" in sys.argv[1:]:
        r25_main()
    else:
        main()

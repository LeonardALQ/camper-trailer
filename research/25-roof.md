# 25: Roof study, fixed roof against a raising roof

Status: research record, 20 Nov 2026. It compared a fixed roof with raising roofs for drag, mass, comfort and cost, and fed decision H12, a fixed roof with rounded front edges.

Positions are in the project datum DIM-01. "Maker" means a published figure, "calculated" means worked out in `research/models/25/aero.py` or `research/models/25/loads.py`, and "(est.)" marks a judgement with no maker figure. Prices are AUD including GST. Product and option data are in `research/25-roof.yaml`.

## Recommendation

Keep the fixed roof at 2,000 mm inside (H1a) and give the trailer a radiused front: option A+ below. A raising roof saves fuel only by hiding the part of the trailer that stands above the bike box. A 150 mm radius on the roof-to-front-wall edge and 250 mm radii on the two front vertical edges cut the drag of that part and of the strips beside the box, so they recover most of the saving with no moving part.

| Measure | A: fixed, 2,000 mm, square front | A+: fixed, 2,000 mm, radiused front (recommended) | B: hard lid on canvas walls | C: telescoping hard shell |
|---|---|---|---|---|
| Travel height (roof top) | Z 2,967 | Z 2,967 | Z 2,345 | Z 2,345 |
| Camp interior | 2,000 mm | 2,000 mm | 2,000 mm raised, 1,350 mm down | 2,000 mm raised, 1,350 mm down |
| Fuel at 90 km/h | 25.0 L/100 km | 21.3 L/100 km | 20.6 L/100 km | 20.6 L/100 km, 19.3 with the A+ edges |
| Fuel at 100 km/h | 28.7 L/100 km | 24.1 L/100 km | 23.2 L/100 km | 23.2 L/100 km, 21.6 with the edges |
| Range on the 130 L tank at 90 km/h, 10 % kept | 468 km | 549 km | 568 km | 568 km, 606 km with the edges |
| Fuel a year, 20,000 km at 90 km/h | AUD 10,500 | AUD 8,950 | AUD 8,660 | AUD 8,660, 8,110 with the edges |
| Mass against A | 0 | +6 kg (est.) | +46 kg (est.) | +117 kg (est.) |
| AC energy, design hot day, battery side | 9.10 kWh (AP25) | 9.10 kWh | 16.6 kWh bare canvas (AP35, 0.6 kWh unmet), 12.7 kWh with a quilted liner | 9.42 kWh |
| Battery against A (8.8 kg per kWh a day) | 0 | 0 | +66 kg bare, +32 kg lined, so one or two more 37 kg modules | +3 kg, no extra module |
| Cost against A | 0 | +AUD 3,500 (est.) | +AUD 19,600 to 22,500 with one or two battery modules (est.) | +AUD 32,900 (est.) |
| Set-up at each stop | None | None | 3 to 5 min up, 5 to 10 min down (est.) | About 3 min each way (est.) |
| Key risks | None new | Mould and bond quality of the corner pieces | Fails H3 and H7 in camp mode, canvas wear and mould, dust through zips, lower the roof in gusts over about 60 km/h | One-off mechanism and seals, no off-the-shelf doors or windows, roof-down interior unusable, 117 kg the trailer does not have |

Fuel figures are `research/models/25/aero.py` at 6,946 kg combination mass, still air and a level road. The aero figures are estimates, with a spread of 1 to 2 L/100 km either way on the savings (section 1). AC figures are `research/models/25/loads.py`, report 19's model with the Mitsubishi MSZ-AP25VGKD2 unless noted.

Why A+:

- Fuel. A+ saves 3.7 L/100 km at 90 km/h, 15 % of option A's use, for about AUD 3,500 (est.). Lowering the roof to the box top (C) saves 4.4 L/100 km, so the moving roof adds only 0.7 L/100 km over A+, about AUD 290 a year. With the same radiused edges C saves 2.0 L/100 km more than A+, about AUD 840 a year. It costs about AUD 32,900 more than A+, so it pays back in about 39 years.
- Mass. TC2 with growth is 3,035.8 kg. Report 19 (+127.7 kg), report 20 (+150.1 kg), report 21 (+119 kg) and report 22's findings (+61 kg) take it to about 3,490 kg before the layout study reconciles it (est.), against H2's 3,400 kg target and the 3,500 kg ATM. C's 117 kg would break the ATM. A+ costs about 6 kg.
- Comfort and power. B's canvas walls nearly double the hot-day cooling energy unless lined and need a bigger air-conditioner. C matches A within 0.3 kWh a day.
- Function. B and C leave 1,350 mm inside with the roof down, so no standing, no shower, no desk and no walk-in door at a quick stop. They also break report 19's window and door choices and report 21's lift bed (sections 5 to 7).

What the layout needs: interior 2,000 mm, roof top Z 2,967 (2,965 panel plus the bonded array), the radii and corner pieces in section 1, +6 kg on the front edges, AUD 3,500. The reports 19, 20 and 21 layout and products stay as they are.

## 1. Drag and fuel

Method. `research/models/25/aero.py` builds up the drag area CdA of the ute, its bike box and the trailer in still air at zero yaw. The trailer's front face splits into the part inside the box silhouette (1,850 mm wide, Z 895 to Z 2,336), which sits in the box's wake, and the exposed part above and beside it. Each part gets its own forebody coefficient, then base drag, skin friction and the running gear are added. Road load at 6,946 kg (the ute with growth plus H2's 3,400 kg) goes through the driveline to the engine, and a Willans line turns engine power into fuel. Output is `research/models/25/aero.out`.

The 1,610 mm gap matters. It is 0.72 times the square root of the trailer's frontal area. Tractor-trailer tests show low drag up to a gap of about 0.5 √A, then a sharp rise that sits on the trailer's front face ([Hammache and Browand](https://www.researchgate.net/publication/267796269_On_the_Aerodynamics_of_Tractor-Trailers)). So the box shelters only the part of the trailer directly behind it, and the exposed strips see close to free-stream flow.

| Term | Value | Basis |
|---|---|---|
| Ute with the bike box | CdA 2.31 m2 | Ute Cd 0.60 on 3.10 m2, plus the box face 1,850 x 346 mm above the cab roof at Cd 0.70 (est.) |
| Exposed trailer face, square edges | Cd 0.80 | A square-cornered box vehicle coasted down at Cd 1.13, 0.86 in a wind tunnel ([NASA TM X-56023](https://ntrs.nasa.gov/api/citations/19740009590/downloads/19740009590.pdf)). A flat-faced body alone has forebody drag 0.75 ([Koenig and Roshko](https://authors.library.caltech.edu/records/wd164-yjc15)). Base and friction taken out (est.) |
| Exposed face, radiused edges | Cd 0.25 | Rounding the box vehicle's vertical front corners cut its aerodynamic drag about 40 %, Cd 1.13 to 0.68 (NASA, same report). The caravan check below implies 0.07 to 0.12 for a raked caravan front, so 0.25 is cautious |
| Face inside the box silhouette | Cd 0.15 (est.) | Gap 0.72 √A, partly sheltered |
| Base (rear face) | Cd 0.20 (est.) | Square back |
| Skin friction, roof and sides | Cf 0.003 | Turbulent plate at Re about 7 million |
| Axles, wheels, drawbar, drawbar box, spare, mud flaps | CdA 0.45 m2 (est.) | Same for every option |
| Box base drag removed by the trailer | -0.27 m2 (est.) | Half the box's base drag |
| Rolling | Crr 0.0095 (est.) | LT265/75R16 at highway pressure on chip seal |
| Engine and driveline | 2.0 kg/h plus 205 g/kWh (est.), driveline 0.88 (est.), accessories 1.5 kW (est.) | About 41 % marginal brake efficiency |

Checks.

- Fuel model. CarExpert ran a V8 70 Series wagon (the same 1VD-FTV) against a constant 3 kN trailer dynamometer and measured 35.3 L/100 km at about 100 km/h in fourth ([CarExpert](https://www.carexpert.com.au/car-videos/watch/iNcr8P1g)). The model gives 34.9 L/100 km for that load with a wagon CdA of 1.9 m2 (est.).
- Drag terms. A Volvo V70 used 4.96 L/100 km alone and 10.77 L/100 km with a Bailey Ranger 440/4 caravan (2.19 x 2.70 m) at 90 km/h, measured with an AVL fuel meter ([Berjoza et al. 2025](https://www.iitf.lbtu.lv/conference/proceedings2025/Papers/TF083.pdf)). That is a caravan drag area of 1.56 to 1.75 m2. The model's base, friction, sheltered-face and running-gear terms give 1.38 m2 for that caravan, which leaves a forebody coefficient of 0.07 to 0.12 for its raked front. A sharp-edged box front is far worse, which is the point of A+.
- Solo ute with the box: 13.1 L/100 km at 90 km/h and 14.6 L/100 km at 100 km/h. Toyota's combined test figure for the V8 is 10.7 L/100 km ([4X4 Australia](https://www.4x4australia.com.au/reviews/2024-toyota-landcruiser-70-series-towing-showdown-v8-versus-inline-4)), so the margin fits a tall box at highway speed (est.).
- No published fuel logs comparing a pop-top with a full-height van of similar mass behind the same car were found. Makers and dealers state only that pop-tops use less fuel ([RV Daily](https://rvdaily.com.au/10-of-the-best-pop-top-caravans-and-expandables-for-compact-touring/), [Alaskan](https://www.alaskancampers.com/hard-sided/)), so the two measured tests above are the checks.

Results from `research/models/25/aero.out`. Range keeps 10 % in the tank. The 180 L tank is report 16's ARB Frontier (FT01).

| Option | Roof top | CdA m2 | L/100 km at 90 | L/100 km at 100 | Range 130 L at 90 | Range 180 L at 90 | Fuel a year at 90 |
|---|---|---|---|---|---|---|---|
| A0, fixed 1,950 mm (committed model) | Z 2,917 | 5.70 | 24.6 | 28.2 | 475 km | 657 km | 4,929 L, AUD 10,350 |
| A, fixed 2,000 mm | Z 2,967 | 5.82 | 25.0 | 28.7 | 468 km | 648 km | 4,999 L, AUD 10,498 |
| A+, fixed 2,000 mm, radiused front | Z 2,967 | 4.55 | 21.3 | 24.1 | 549 km | 760 km | 4,262 L, AUD 8,950 |
| B and C, roof down at the box top | Z 2,345 | 4.31 | 20.6 | 23.2 | 568 km | 786 km | 4,122 L, AUD 8,656 |
| C+, roof down, radiused front | Z 2,345 | 3.86 | 19.3 | 21.6 | 606 km | 839 km | 3,862 L, AUD 8,110 |
| C', telescoping, 1,600 mm inside roof down | Z 2,595 | 4.92 | 22.4 | 25.4 | 523 km | 724 km | 4,475 L, AUD 9,397 |

Spread. With the forebody coefficients at their low and high ends (square 0.65 to 0.95, radiused 0.40 to 0.15, base 0.15 to 0.25) and a marginal fuel rate of 195 to 220 g/kWh, A+ saves 1.6 to 5.8 L/100 km against A at 90 km/h, C saves 3.3 to 5.6 and C+ saves 3.9 to 7.7. The saving of A+ is the least certain number in this study, because it rests on the radiused coefficient. Its central value is already cautious against the caravan check.

What the numbers show:

- Of the trailer's 3.51 m2 in option A, 1.84 m2 comes from the exposed strips: 1.21 m2 from the 631 mm above the box and 0.63 m2 from the two 275 mm strips beside it. Lowering the roof removes the first. Radiused edges cut both.
- Height alone is worth little. Each 50 mm of fixed roof costs 0.35 L/100 km at 90 km/h with a square front and 0.16 L/100 km with A+. H1a's 50 mm over the committed model costs 0.4 L/100 km.
- A roof that stops above the box keeps little of the gain. Lowered only to 1,600 mm inside (C'), so two people could sit up roof down, C keeps 2.6 of its 4.4 L/100 km.
- Option A at 100 km/h needs about 107 kW at the crank. The stock 1VD-FTV makes about 87 kW in fifth at about 1,930 rpm (430 Nm, report 15's ratios), so A holds 100 km/h only with report 14's tune (about 650 Nm, so about 131 kW there) or in fourth. A+ needs 88 kW and C 85 kW (calculated).
- The 130 L tank gives 468 km with A and 549 km with A+ at 90 km/h. Report 16's 650 to 700 km assumed 18 to 20 L/100 km, which this rig does not reach. With the 180 L tank (FT01) A+ reaches 760 km, so FT01 moves from optional to worth fitting (report 23 to decide).

A+ specification for the layout (est. unless marked).

- Roof-to-front-wall edge: outside radius 150 mm. The arc starts 150 mm behind the front face, so the solar array keeps its start at X 1,976 and its 156 mm margin.
- Kerb-side and road-side front vertical edges: outside radius 250 mm, floor underside to roof. The flat front wall between them is 1,900 mm wide, room for W3 and report 19's high intake.
- The two top front corners: a spherical corner piece joining the three radii.
- Construction: a moulded GRP shell 4 to 6 mm thick over an XPS infill, bonded and riveted to the wall and roof panels in place of the aluminium corner joiners on those three edges. The core stays continuous, so the U-value stays as report 19's. An aluminium rolled-radius cover with foam infill is the alternative.
- Inside: the inner radius is about 215 mm on the vertical edges, so the bed platform's two front corners get a 220 mm radius or a 45 degree chamfer with 220 mm legs. The HappiJac front rails sit about 230 mm behind the front wall and clear it. On the top edge the inner radius is about 110 mm, all of it above the day-position mattress top at 1,820 mm.
- Mass: about +6 kg against the square corner joiners and the panel strips they replace (section 2). Cost: about AUD 3,500 with a one-off mould.
- Rear edges stay square for the rear door, the outdoor unit and the rinse box. Rear-edge shaping is not counted here.

## 2. Mass

Options as studied.

- A: report 19's body with 2,000 mm inside. Walls from the floor to Z 2,925, then the 40 mm roof.
- B: report 12's raising roof scaled down. Lower walls to 1,350 mm inside, a 650 mm canvas skirt, the 40 mm lid on a top ring, four LINAK LA36 with guide posts and six latches. Roof down at Z 2,345, about level with the box top at Z 2,336. Raised 2,000 mm inside.
- C: the same lower body, plus an upper shell of 35 mm sandwich walls 800 mm tall (650 mm lift and 150 mm overlap) that hangs from the lid and slides outside the lower walls, so rain sheds off it as off a box lid (est.). The lower body narrows to 2,310 mm so the shell stays at 2,400 mm. Four LA36 with guide posts, six latches. Roof down at Z 2,345.

Masses against A, in kg. Panel masses are report 12's (walls 6.0 kg/m2). The rest is estimated unless marked.

| Element | B | C | Basis |
|---|---|---|---|
| Lower walls 650 mm shorter, 8.9 m2 | -53.2 | -53.2 | Report 12 panel mass |
| Canvas skirt with zip windows, 10.2 m2 at 0.71 kg/m2 | +7.3 | | Report 12 (9.4 kg for 13.2 m2) |
| Quilted inner liner | +3.0 | | Report 12 |
| Upper shell walls, 11.1 m2 | | +66.7 | Report 12 panel mass |
| Top ring on the lid (the bottom ring replaces A's roof joiner) | +26.1 | | Report 12 BD-12 |
| Two sliding rails with seal tracks, 27.5 m at 1.2 kg/m | | +33.0 | Scaled from DIY Caravans' 1.65 kg/m ring (est.) |
| Four LA36 with guide posts and controls | +30.0 | +34.0 | Report 12 BD-12. C's guides are longer (est.) |
| Six over-centre latches with secondary catches | +2.4 | +2.4 | Report 12 BD-12 |
| Seals | +3.2 | +4.0 | Report 12 BD-12, C est. |
| Lid stiffening for the raised span between four posts | +10.0 | +6.0 | Est. In C the shell walls stiffen the lid |
| Split doors in place of the two Aussie Traveller DC doors | +8.0 | +10.0 | Est., section 7 |
| Upper wet room partition: zip fabric in B, panel with a seal in C | +3.0 | +8.0 | Est., section 7 |
| Roof-hung bed lift in place of report 21's HappiJac (35 kg) | +5.0 | +5.0 | Est., section 6 |
| Cable and duct loops to the roof: array, lights, hood | +1.5 | +1.5 | Est. |
| Total against A | +46 | +117 | Range about +30 to +65 for B and +85 to +145 for C (est.) |

A+ replaces the square aluminium corner joiners (2.0 kg/m, report 12) and the panel strips they join with curved GRP sandwich corner pieces. A 250 mm quarter round is 0.39 m of curved panel in place of 0.50 m of flat panel, so the corner pieces with their bonding flanges come to about +6 kg in all (est., 0 to +12 kg).

The battery adds to B. Section 3 puts B's hot day at +3.6 kWh (lined) to +7.5 kWh (bare) at the battery, so +32 to +66 kg at 8.8 kg per kWh a day, which in report 20's 37 kg modules means one or two more. C adds 0.3 kWh, inside report 20's margin of 28.1 h on the hot day. With battery, B is +78 to +112 kg and C +117 kg.

The budget has no room. TC2 with growth is 3,035.8 kg. Adding report 19 (+127.7 kg), report 20 (+150.1 kg), report 21 (+119 kg) and report 22's findings (+61 kg) gives about 3,490 kg (est., the layout study reconciles it), against H2's 3,400 kg target and the 3,500 kg ATM. C alone would take it past the ATM. A+ and A are the only options that do not make the mass problem worse.

Centre of gravity. C's added mass sits high, but in travel the lid and the solar array (about 132 kg with the roof joiner) drop 620 mm. The travel CoG comes out within about 5 mm of A's at Z 1,131 (calculated). B is similar. Neither changes the ball load by more than a few kilograms, because the roof parts are spread over the body length.

## 3. Thermal

`research/models/25/loads.py` is a copy of report 19's `research/models/19/loads.py`. It reproduces report 19's output unchanged and adds a roof block: a canvas skirt with its own U-value, sun absorption and leakage for B, and the two sliding-seal rails and seal leakage for C. All options are run in camp mode, roof raised, 2,000 mm inside, with report 19's windows, people, appliances, ventilation and the Mitsubishi units. Output is `research/models/25/loads.out`.

Inputs added (est.):

- Canvas: U 5.5 W/m2K for a single polycotton layer with its air films (0.13 + 0.04 + 0.01 m2K/W), or 2.3 W/m2K with a quilted inner liner. Sun absorptance 0.55 for sand or grey canvas, 3 % of the sun passing through as light. The 650 mm skirt is 8.9 m2.
- Canvas leakage: zips, the canvas-to-ring joins and the fabric itself add about 50 m3/h of outdoor air that skips the heat recovery (section 4).
- C: two aluminium rails at the sliding joint, 13.6 m at a ψ of about 0.15 W/m.K, so 2.0 W/K, and 7 m3/h of extra air through the seal.

| Option, camp mode | Heat to remove, hot day | Peak | Unit | AC energy, battery side | Unmet | Change, battery side | Battery change at 8.8 kg per kWh | Cold night heat | Cold night, heat pump, battery side |
|---|---|---|---|---|---|---|---|---|---|
| A0, 1,950 mm (report 19) | 37.1 kWh | 3.29 kW | AP25 | 9.03 kWh | 0 | -0.07 kWh | -0.6 kg | 17.6 kWh | 6.60 kWh |
| A and A+, 2,000 mm | 37.3 kWh | 3.30 kW | AP25 | 9.10 kWh | 0 | 0 | 0 | 17.9 kWh | 6.68 kWh |
| B, bare canvas | 57.2 kWh | 4.25 kW | AP25 | 14.92 kWh | 4.09 kWh | +5.82 kWh | +51 kg | 37.7 kWh | 14.00 kWh |
| B, bare canvas | 57.2 kWh | 4.25 kW | AP35 | 16.56 kWh | 0.64 kWh | +7.47 kWh | +66 kg | 37.7 kWh | 14.50 kWh |
| B, quilted liner | 46.9 kWh | 3.77 kW | AP35 | 12.68 kWh | 0 | +3.59 kWh | +32 kg | 27.8 kWh | 10.68 kWh |
| C, telescoping shell | 38.4 kWh | 3.37 kW | AP25 | 9.42 kWh | 0 | +0.32 kWh | +3 kg | 19.4 kWh | 7.23 kWh |

What it means:

- The canvas is the weak point of B. Its 8.9 m2 lets in 18.6 kWh of heat on the hot day bare, more than A's roof, floor and walls together (15.2 kWh in report 19's run), and 8.3 kWh lined. The bare skirt needs a 5 kW class unit, such as the MSZ-AP50VGKD2 from the same Mitsubishi range (est.), because even the AP35 leaves 0.64 kWh unmet at dinner. The lined skirt needs the AP35. On the cold night B needs 28 to 38 kWh of heat against A's 17.9, so the Combi D 6 burns 3.1 to 4.1 L of diesel in place of 2.0 L (report 19's 0.110 L per kWh).
- B fails H3 as specified. The extra 3.6 to 7.5 kWh a day costs one or two more 37 kg modules (report 20) and AUD 2,900 to 5,800, and report 20's 28.1 h on the hot day falls to about 23 h lined or about 20 h bare without them (scaled on the daily load, est.).
- C is within 0.3 kWh of A on the hot day and 0.55 kWh on the cold night. The AP25 still covers the 3.37 kW peak with its 3.6 kW maximum. No battery change.
- A+ is the same body as A thermally. The curved corner pieces keep the insulation thickness, and their area is a little smaller than the square corners they replace.
- Roof down, B and C have a 1,350 mm interior and less heat gain, but section 8 shows that the trailer is not usable that way, so the camp-mode figures govern.

## 4. Air and dust

Report 19 holds the parked body slightly above outside pressure with a filtered top-up of 15 m3/h on an effective leakage area (ELA) of 30 cm2 or less, about +3 Pa, and pushes 150 to 200 m3/h through the Sy-Klone RESPA-CF2 while towing. The flow needed for a given overpressure follows report 19's orifice relation, Q = 0.61 x ELA x √(2 Δp / 1.2).

| Option, camp mode | ELA (est.) | Flow for +3 Pa | Flow for +20 Pa | Verdict |
|---|---|---|---|---|
| A and A+ | 30 cm2 (report 19 target) | 15 m3/h | 38 m3/h | Report 19's top-up fan does it at 3 to 8 W |
| B | About 200 cm2: zips (about 75 cm2), canvas-to-ring joins (about 50 cm2), fabric permeability (about 75 cm2) | About 100 m3/h | About 255 m3/h | Only the RESPA-CF2 can, at 144 W, 3.5 kWh a day, and its 100 m3/h of unrecovered 42 C air adds about 0.6 kW of cooling at the peak (est.) |
| C | About 45 cm2: report 19's 30 cm2 plus about 15 cm2 at the sliding seal | 22 m3/h | 57 m3/h | The top-up fan at 22 m3/h, inside its 15 to 40 m3/h range |

B cannot meet H7 parked. Holding positive pressure in the canvas costs about 4 to 5 kWh a day of fan and extra cooling on top of section 3 (est.), and a dust storm's windward pressure of 50 to 100 Pa would need several hundred cubic metres an hour. In practice the canvas zips are closed and dust comes in on the windward side, as report 12 found.

C can. The sliding seal adds leakage, so the top-up rises from 15 to about 22 m3/h, and the sliding-seal ELA becomes part of report 19's 30 cm2 acceptance test with the 0 to 125 Pa gauge.

Towing with the roof down.

- A and A+: report 19's scheme unchanged. The radiused front does not touch the high front intake, which goes on the flat part of the front wall.
- B: the lid sits on report 12's bulb seal between the rings, pressed 5 to 8 mm by six latches. On corrugations the body twists under a lid that rests on the seal, so the gap opens and closes along the ring (est.). The RESPA keeps the flow outward, but any dust that does get in lands on the folded canvas and works into the zips.
- C: the shell overlaps the lower walls by 800 mm in travel. The gap between the two skins (5 to 10 mm, est.) is open at the shell's bottom edge about 620 mm above the floor. A brush or lip strip there keeps out the bulk, and the compression seal at the lower body's top rail is the air barrier. Dust that collects in the gap is dragged across the seal every time the roof moves, so the gap needs washing out after a dusty trip (est.). Alaskan describes its campers as the only hard-sided pop-up truck campers on the market ([Alaskan](https://www.alaskancampers.com/hard-sided/)), so the only long field record of this seal is on North American truck campers, not on outback corrugations (est.).

## 5. Windows and blackout

H8 asks for blinds or shades built into the frame. Report 19 chose six Dometic S4 windows with roller blackout blinds and fly screens in the inner frame, plus two clip-in blackout covers for the bed windows. W1 (900 x 600 mm, sill about 960 mm above the floor) is the second way out, with report 19's rule of at least 0.33 m2 clear and no side under 450 mm.

- A and A+. report 19's schedule stands. On A+ the flat front wall between the 250 mm radii is 1,900 mm wide, so W3 and its stone shutter fit as report 19 placed them.
- B. S4 windows fit only in the lower walls, with their heads below the bottom ring, so at most about 1,300 mm above the floor. W1 cannot keep its 960 mm sill and 600 mm height, and dropping it puts most of its opening below the night mattress top (950 to 1,050 mm), so it stops being an escape route from the bed. The escape route then becomes a zip panel in the canvas, as in report 12. Canvas windows have zip blockout flaps, not blinds in a frame, so H8 is met only for the lower-wall windows.
- C. Wherever the shell slides, the faces must be flat. The lower walls' outer face from about 620 to 1,350 mm above the floor takes no S4 outer frame, hinged sash or vent hood. The shell's inner face takes no S4 inner frame or blind cassette. So the S4 does not fit either part. The workable choice is a flush-bonded window with an integrated blind (the Polyplastic Polyvision type, for which report 19 found no Australian stock) in the lower walls, below 1,330 mm. Those windows are covered by the shell roof down, so the interior is dark in travel. The bed window then fits only as a 450 mm tall unit, whose 304 mm clear height fails report 19's escape rule. A separate escape hatch in the shell, with no integrated blind, would be needed. C therefore meets H8 only in part and loses report 19's escape window.

## 6. Lift bed

A and A+. report 21's Lippert HappiJac four-rail lift stays as specified: rails 1,067 mm apart on each side wall, a 1,575 mm rail frame, 204 kg moving rating, motor brake, manual crank and travel locks. Day position: underside 1,600 mm, mattress top 1,820 mm, 180 mm under the 2,000 mm ceiling. Night position: mattress top 990 to 1,050 mm with 950 to 1,010 mm clear above, and the bed stops at least 40 mm above the 730 mm desk. In travel it locks up or down (H1). On A+ the front rails sit about 230 mm behind the front wall, clear of the 215 mm inner radius.

B and C. The fixed side walls stop at 1,350 mm. The HappiJac's rail frame and top drive need the full 2,000 mm, and neither the canvas nor C's shell can carry rails, because the shell's inner face must stay flat (section 5). The only workable layout found is a bed hung from the lid:

- Travel: the bed rests on its night stops above the desk, underside at least 770 mm, mattress top about 990 mm, 360 mm under the lowered lid. The desk is covered while towing.
- Camp, day: a lid-mounted drive winds four straps and pulls the bed up under the lid, underside about 1,600 to 1,780 mm.
- Camp, night: the straps pay out to the night stops. Guide channels on the lower walls steady the platform below 1,350 mm. Above that it hangs on the straps alone (est.).
- Interlocks: the roof may only move with the bed on its stops, and the strap drive must pay in or out with the roof so the straps neither go slack nor lift the bed. That makes two coordinated lifts, the same objection report 18 raised against layout 3 ("two lift systems must work every night").
- No product does this. It is a custom build, with report 21's travel locks, safety edge and manual lowering carried over (est.).

The desk still fits under the bed in B and C, but only with the roof up.

## 7. Layout limits

The lowered interior that gives section 1's saving is 1,350 mm, with the roof top at Z 2,345, about level with the box top. Stopping at 1,600 mm (C') keeps only 2.6 of the 4.4 L/100 km. So in B and C every fixed item must stand 1,330 mm or less above the floor (20 mm clearance under the lid, est.). In C nothing may stand proud of the lower walls' outer face between about 620 and 1,350 mm above the floor.

| Item | Height | A and A+ | B and C |
|---|---|---|---|
| Lift bed, HappiJac | 1,575 mm frame, drive near the ceiling | Fits | Replace with the lid-hung lift (section 6) |
| Wet room walls, inner door, DauerShower 2.0 | 2,000 mm, shower head near the ceiling | Fits | Split partition: fixed to 1,330 mm, upper part hung from the lid (panel with a seal in C, zip fabric in B). Shower only roof up |
| Wardrobe | Full height (est. 1,800 mm or more) | Fits | Cut to 1,330 mm, short hanging only |
| Fridge Dometic NRX 130C | 812 mm (report 13) | Fits | Fits |
| Haier 7 kg heat-pump dryer, Camec 3.5 kg washer | 850 and 730 mm (report 21) | Fit stacked or side by side | Side by side only. Stacked they need 1,580 mm |
| Camec convection microwave | 318 mm (report 21) | Any height | Only at or below about 1,000 mm |
| Range hood (report 19) | Wall-mounted about 1,550 mm up (est.) | Fits | Hang from the lid with a flexible duct loop |
| Mitsubishi indoor unit | 299 mm tall, top 50 mm under the ceiling (report 19) | Fits | Top at 1,330 mm on the fixed partition |
| Mitsubishi outdoor unit | 550 x 800 x 285 mm, high on the rear wall (report 19) | Fits | B: below the bottom ring. C: below the shell's travel edge, Z 980 to 1,530, in the rear spray zone |
| Entry and rear doors, Aussie Traveller DC 1,750 x 622 mm | 1,750 mm leaf | Fit | Split custom doors, no pleated blind |
| LUNOS e2 sleeves | Through the walls | Fit | B: lower walls. C: below 620 mm or in the shell |
| Truma Combi D 6 E, battery box, cassette toilet, basin | 300 mm, 320 mm, bench height | Fit | Fit |

Roof down, B and C give no sitting headroom. H1 takes a seated 95th percentile adult's head at about 1,410 mm, which is more than the 1,350 mm lowered interior, so even the toilet is not usable without raising the roof.

## 8. Use

| | A and A+ | B | C |
|---|---|---|---|
| Set-up at a stop | None | Release six latches (about 1 min), raise 650 mm (about 35 s at the LA36's 18 to 23 mm/s), set the canvas, lower the bed: 3 to 5 min (est.) | Release six latches, raise, lower the bed: about 3 min (est.) |
| Pack-down | None | Fold the canvas in, check that no fabric is caught, latch: 5 to 10 min. Dry wet canvas within a few days (est.) | Clear the roof edge, wipe the gap, lower, latch: about 3 min (est.) |
| Lunch, toilet, a night in a hurry | Full use at any stop | Raise the roof first. 1,350 mm inside roof down | Raise the roof first. 1,350 mm inside roof down |
| Wind | No limit | Report 12: the raised lid's uplift turns positive at about 20 m/s (72 km/h) and reaches 1.8 kN at 25 m/s. Lower it in gusts over about 60 km/h, which also means no bed | The raised shell takes about 1.3 kN of side force at 25 m/s on its 650 mm band (est.) through four guide posts and the overlap. Lower it in gusts over about 80 km/h (est.) |
| Rain, leaves | Nothing | Water and leaves on the lid fall into the folded canvas | Water sheds off the shell outside the lower walls. Leaves and grit on the roof edge fall into the gap, so sweep before lowering |
| Mechanism failure | Not applicable | The LA36 has an integrated brake and a hand crank ([LA36 data sheet](https://docs.rs-online.com/0f7b/A700000011321379.pdf)). 650 mm at 12 mm pitch is about 54 turns on each of four actuators, about 15 to 20 min (est.) | Same. A hydraulic lift lowers by gravity through its release valve, as Alaskan's does |
| Solar array and roof services | Fixed | PV strings, lights and the hood duct reach the lid through a cable loop at one corner. No air-conditioner on the roof (report 19) | Same |

A roof that must go up before anyone can stand, cook, use the toilet or sleep turns every stop into a set-up, and a gusty night into a night without the bed. That is the cost of B and C that the fuel figures do not show.

## 9. Reliability, service and suppliers

Records.

- Alaskan Campers (USA) raised its hard-side shells hydraulically from 1958 to 2025: an electric pump, a reservoir, four steel rams, valves and lines. A restored 1958 system needed only cleaning and refilling after 60 years, and production is under 100 campers a year, sold factory-direct ([Truck Camper Magazine review](https://www.truckcampermagazine.com/camper-reviews/2019-alaskan-8-5fd-review/)). From 2026 Alaskan fits four 12 V linear actuators with a synchronous controller as standard ([Truck Camper Magazine](https://www.truckcampermagazine.com/news/alaskan-campers-debuts-electric-actuator-lifts/)). Not sold in Australia (report 12).
- Hi-Lo (USA) telescoped its trailers with one hydraulic cylinder, cables and pulleys. Owners call it reliable if it is checked, cleaned and lubricated every year ([forum](https://www.hilotrailerforum.com/threads/398686/)). Tops have come down on one corner when cables broke under snow and ice ([forum](https://www.hilotrailerforum.com/threads/what-keeps-it-up.397500/)). The maker closed in 2010 ([RV.com](https://rv.com/archive/hi-lo-trailer-co-closes-shop/)) and built again from 2014 to 2018 ([Mortons on the Move](https://www.mortonsonthemove.com/hi-lo-campers/)). Owners then struggled to find the top-to-bottom seal ([forum](https://www.hilotrailerforum.com/threads/any-one-know-how-to-get-the-top-bottom-seal.397575/)).
- LINAK LA36: IP66 in use and IP69K static, -30 to +65 C, integrated brake, hand crank, 20 % duty at full load up to 600 mm stroke and 15 % above it (data sheet). Ultimate Off-road Campers uses an LA36 to open the shell of its X25 camper trailer, and LINAK calls it maintenance-free ([LINAK](https://www.linak.com/case-stories/camper-trailer-fit-out-with-linak-actuator-enhances-functionality)).
- Canvas pop-tops: latches that unhook in travel, canvas wear and mould, bent lifters and broken cables (report 12, [RV Daily](https://rvdaily.com.au/how-secure-are-the-latches-on-your-pop-top-roof/)).

Hydraulic against electric. For this trailer the electric LA36 set wins. It needs no oil inside a dusty body, the four corners stay level through LINAK's IC Parallel control, it holds position with power off, and LINAK Australia supplies and supports it from Dandenong South. Hydraulics offer gravity lowering and a hand pump, but they need a flow divider to keep four rams level, flexible hoses to a moving roof, and a reservoir and pump that took up two of the Alaskan's cabinets (Truck Camper Magazine review).

Australian suppliers.

- LINAK Australia Pty Ltd, 84 Bazalgette Crescent, Dandenong South VIC, +61 3 8796 9777, with a TECHLINE unit for mobile and industrial actuators ([LINAK terms of sale](https://cdn.linak.com/-/media/files/sales-condition/standard-terms-of-sale-and-delivery-for-linak-australia-pty-ltd.pdf), [linak.com.au](https://www.linak.com.au/)). Vehicle users include a hearse deck lift on four LA36 IC Parallel ([LINAK, Hillier](https://www.linak.com/case-stories/hillier-vehicle-automation)).
- Linear Actuators Australia (ShopLAA), Brisbane: a four-actuator 12 V pop-top kit at AUD 1,694 including GST and shipping, under 10 kg, sized for lifts up to 450 mm, with installers in Brisbane and Adelaide ([ShopLAA](https://shoplaa.com.au/)). Too short for a 650 mm lift without a custom build.
- DIY Caravans: pop-top rings, seals, latches and lifters (report 12).
- Hydraulic 12 V DC power packs and multi-stage rams are sold for tipper trailers, for example 800 mm stroke rams from about AUD 780 ([eBay AU listings](https://www.ebay.com.au/shop/tipper-ram?_nkw=tipper%20ram)).
- Canvas: any caravan canvas maker can build and repair a skirt, for example [Cutting Edge Canvas](https://cuttingedgecanvas.com.au/).

Service in dust and heat. A+ needs nothing beyond the body's own checks. B needs canvas re-proofing every two to three years and zip repairs (est.). C needs the sliding seals inspected every year, the guide posts cleaned and greased, and the actuator rod seals checked (est.). Both need the latches checked after every rough trip.

## 10. Cost

Extras against A in AUD including GST. All lines are estimates unless a source is given. Labour is at report 22's AUD 120 an hour.

| Element | A+ | B | C |
|---|---|---|---|
| Radiused front corner pieces, one-off mould, parts and fitting | 3,500 | | |
| Lower walls 650 mm shorter, 8.9 m2 at about AUD 150 per m2 | | -1,300 | -1,300 |
| Top ring, seals and six latches (report 18: about AUD 800) | | 800 | 700 |
| Canvas skirt with zip windows and screens (report 18: AUD 1,500 to 2,500), quilted liner | | 2,800 | |
| Upper shell walls, 11.1 m2 at about AUD 180 per m2 | | | 2,000 |
| Two sliding rails with seals, 27.5 m | | | 1,900 |
| Four LA36 IC Parallel with guide posts and controls | | 5,000 | 5,500 |
| Lid stiffening | | 600 | 400 |
| Split custom doors, less the two Aussie Traveller DC doors (AUD 1,549.99 each, report 19) | | 2,000 | 2,900 |
| Flush-bonded windows in place of the S4s | | | 1,500 |
| Upper wet room partition | | 300 | 800 |
| Lid-hung bed lift, less report 21's HappiJac (AUD 4,049) | | 500 | 500 |
| Labour and development: B 50 h, C 150 h | | 6,000 | 18,000 |
| Battery: one or two Victron NG 51.2 V 100 Ah at AUD 2,911 each (report 20 listing) | | 2,911 to 5,822 | |
| Total against A | 3,500 | about 19,600 to 22,500 | about 32,900 |

Fuel against A at 90 km/h and 20,000 km a year: A+ saves AUD 1,548 a year, so it pays back in about 2.3 years. C saves AUD 1,842 a year and pays back in about 18 years. Against A+, C with the same radiused edges saves AUD 840 a year for about AUD 32,900 more, so about 39 years.

## 11. Compliance

- Height. VSB1 clause 5.3 allows 4,300 mm including roof-mounted items (report 12). Every option travels under 3,000 mm. Report 12 treats a raised roof as a parked condition.
- Width. VSB1 clause 5.2 allows 2,500 mm including the awning. A and A+ keep the 2,400 mm body and the 100 mm awning. In C the shell slides outside, so the lower body narrows to 2,310 mm, the inside width falls from 2,330 to 2,240 mm (still inside the HappiJac's 2,184 mm minimum if it were kept), and the awning goes on the shell and rises with it. That adds the awning's 41 kg to the lifted mass.
- Lighting. ADR 13/00 requires end-outline marker lamps on vehicles over 2.10 m wide (report 17). Under UN R48, which ADR 13 follows, a trailer's lamps sit at the greatest height the design allows and within 400 mm of the outer edge (est. reading of R48 clause 6.13). On A+ the front pair go on the flat front wall just below the top radius, 250 to 300 mm in from the sides. On B and C they go at the top corners of the fixed lower body, because the roof moves (assumption).
- Latch loads at 40 m/s. The dynamic pressure is 960 Pa. With a mean suction coefficient of -0.6 on the 10.6 m2 lid (est.), the uplift is 6.1 kN, plus 0.2 kN from 20 Pa of RESPA overpressure. Less the lifted mass (B about 146 kg, C about 208 kg, or 249 kg with the awning), the net uplift is 4.9 kN on B and 4.3 kN on C, so 0.8 kN and 0.7 kN on each of six latches. With a factor of 2 and a 1 g bounce allowance, specify each latch for at least 2.0 kN, as report 12 did (2.1 kN), with the self-locking LA36 as the second load path. A and A+ have no latches.
- Wiring to a moving roof. ADR 42/05 clause 21 asks for wiring clear of moving parts, protected from chafe and supported at 600 mm or less (report 12). The cable loop to the lid must meet it.
- Certification. No VSB1 clause, ADR or NSW VSI 06 item covering a lifting roof was found, so the lift needs no certificate of its own (assumption). The trailer's own certification is the same for every option. For B and C the designer applies the project's moving-part rules from report 21's bed: hold-to-run control, latch interlock, obstruction stop and manual lowering.

## Open points and the assumptions to use

1. Forebody coefficient of the radiused front. It carries A+'s saving. Assumption: 0.25 (range 0.15 to 0.40), so A+ uses 21.3 L/100 km at 90 km/h. For fuel and range planning before there are fuel logs, use option A's 25.0 L/100 km at 90 km/h and 28.7 L/100 km at 100 km/h, so the plan errs on the safe side.
2. Drag of the ute with the bike box. Assumption: CdA 2.31 m2. It moves every option's absolute fuel use by the same amount, not the differences. If report 24's box gets a 100 mm radius on its front top edge, rerun `research/models/25/aero.py` with `BOX_STEP_CD` near 0.35 (est.).
3. Towing fuel for report 23 and report 16. Report 16 assumed 18 to 20 L/100 km while towing. Assumption for the car plan: 25 L/100 km at 90 km/h with A and 21 L/100 km with A+. On the 130 L tank that is 468 to 549 km with 10 % kept, so assume the ARB Frontier 180 L (FT01) is fitted, giving 648 to 760 km.
4. Corner piece design. Assumption: moulded GRP 4 to 6 mm over XPS, bonded and riveted to the panels where the aluminium corner joiners were, radii 150 mm (top) and 250 mm (vertical), a spherical piece at each top corner, +6 kg, AUD 3,500. An aluminium rolled-radius cover with foam infill is the fallback. The drawings show them on CT-011 and CT-2xx.
5. Rear edges. Not counted. Assumption: square rear edges, because the rear door, the outdoor unit and the rinse box sit there.
6. A deflector on the bike box roof. A roof spoiler on a car towing a caravan cut fuel use by 13.5 % at 90 km/h in Berjoza's test. On this rig it would stand above the box all the time and add drag solo. Assumption: no deflector. Revisit only if fuel logs with A+ come in high.
7. Mass budget. Assumption: about 3,490 kg fully loaded with growth after reports 19 to 22, before the layout study reconciles it. Any roof option that adds mass is out until the layout shows margin.
8. Canvas properties for B. Assumption: U 5.5 W/m2K bare, 2.3 W/m2K lined, absorptance 0.55, 50 m3/h of extra unrecovered air. Measured values would move B's numbers but not past A's.
9. C's seal and dust record. No field data for a sliding hard-shell seal on outback corrugations was found. Assumption: as section 4, about 15 cm2 of extra leakage and a yearly seal check.
10. Lid suction coefficient for the latch loads. Assumption: mean -0.6 on the lid at 40 m/s, latches rated at least 2.0 kN each. It matters only if B or C is chosen.
11. End-outline marker lamps on A+. Assumption: the front pair on the flat front wall just below the 150 mm top radius, 250 to 300 mm in from the sides, and the rear pair at the square rear top corners. That meets UN R48's 400 mm rule on the reading in section 11.
12. The gap. All drag figures assume the 1,610 mm gap from the box to the trailer front. If the coupling or the box length changes, rerun `research/models/25/aero.py`.

# Home trailer

Status: concept, revision J, 21 Nov 2026. DRAFT, not for construction until the engineer reviews it. Data: `data/assemblies/trailer.yaml`, `data/load_cases.yaml`, `data/checks.yaml`, `data/services.yaml`, `data/measurements.yaml` and the parts list `data/trailer-parts.yaml`. Code: `cad/trailer.py`. CHASSIS.md and BODY.md design the frame and the shell, `docs/decisions.md` records the decisions, and research reports 19 to 22 and 25 hold the research. Positions are in mm in the project datum DIM-01: X rearward from the ball, Y positive to the road side, Z up from the ground.

The brief is a home for long stays off-grid: a lifted bed over a 1.2 m desk, a wet bathroom entered from a rear door, a recirculating shower for two 20 min showers a day, an electric kitchen with an oven, a washer and a dryer, filtered fresh air with the windows shut, blackout blinds, and power for a hot day of air-conditioning for at least 12 h, 24 h if possible.

## Summary

| Measure | Value |
|---|---|
| Body | 4,420 x 2,400 mm outside, X 1,820 to 6,240. Inside 4,350 x 2,330 x 2,000 mm, floor at Z 925 |
| Overall | 6,700 mm long, 2,470 mm wide over the entry door's handle, 3,078 mm high over the awning case |
| Tare | 2,622 kg, 2,879 kg with the growth allowance |
| Fully loaded with 305 L of water (TC2) | 3,106 kg, 3,397 kg with growth, against the 3,500 kg plate |
| Towball | 251 to 292 kg, 8.1 to 10.4 % of the trailer, at most 316.5 kg with growth |
| Ute | Rear axle 2,601 kg with growth against its 2,800 kg plate. Combination 7,135 kg against 7,400 kg, the ute with growth plus the plate |
| Battery | 25.6 kWh. A design hot day runs 25.1 h when new and 17.2 h at end of life |
| Water | 420 L fresh, at most 305 L in travel, about 41 L a day. 130 L grey |
| Cost | AUD 236,416 with contingency, AUD 188,464 owner-built |

Every fail check passes. The tightest are the fully loaded mass with growth (MAS-10, 3,396.9 kg against the 3,400 kg target), the towball share with the grey tank full (MAS-12, 8.1 % against 8.0 %), the heaviest towball (MAS-13, 316.5 kg against 320 kg) and the recovery pull in the road-side rail (CHS-08A, 0.91 of yield).

## Layout

From the front: the drawbar with its sealed box, the bed and desk zone, the living zone, a partition and the wet room across the rear (CT-010).

| Zone | Inside X | Kerb side | Middle | Road side |
|---|---|---|---|---|
| Bed and desk | 1,855 to 3,445 | Window W1, the second way out | Lift bed over the desk, nothing else (H1) | Window W2 |
| Living | 3,445 to 5,185 | Entry door D1, the battery plinth with the washer and dryer on it | Aisle, 905 mm wide at full height | Tower with the Combi, fridge and oven, bench with the hob over the freezer, sink, W4 |
| Partition | 5,185 to 5,205 | 48 V board | Inner door | Inverter, split indoor unit |
| Wet room | 5,205 to 6,205 | Toilet, basin, cassette door | Rear door D2 | Shower over its floor well, W6 |

Under the floor, between the rails, are the fresh tanks over the axles, the grey tank in the rear bay, the heater's diesel tank and the air supply box. The drawbar carries the box with two Honda EU22i and the jerry cans, the jockey wheel, and the spare wheel on the front wall above them. Walkways and landings keep at least 550 mm clear (FIT-01). The air-conditioner's outdoor unit stands high on the rear wall's road half.

Storage is 0.38 m³ inside and 0.09 m³ in the drawbar box, about 0.2 m³ short of a long-stay home (est.), because the bed's footprint stays empty (H16).

## Mass and limits

Masses in kg. The towball comes from moments about the axle group centre at X 4,375 mm. "With growth" adds 20 % to an estimate, 7 % to a calculated mass and nothing to a maker's figure (report 02, MASS-06). CT-002 shows each case's centre of gravity.

| Case | Aboard | Mass | Towball | Share | With growth | Towball with growth |
|---|---|---|---|---|---|---|
| TC1 Tare | Nothing | 2,622 | 255.0 | 9.7 % | 2,879 | 273.5 |
| TC2 Fully loaded | 305 L fresh, fuel, 150 kg of gear | 3,106 | 291.8 | 9.4 % | 3,397 | 316.5 |
| TC3 Highway | 50 L, fuel, gear | 2,851 | 290.0 | 10.2 % | 3,142 | 314.7 |
| TC4 Water, no gear | 305 L, fuel | 2,956 | 272.5 | 9.2 % | 3,217 | 293.4 |
| TC5 Gear, no water | Fuel, gear | 2,801 | 289.7 | 10.3 % | 3,092 | 314.4 |
| TC6 Fuel only | Fuel | 2,651 | 270.4 | 10.2 % | 2,912 | 291.2 |
| TC7 Grey full | 175 L fresh, 130 L grey, fuel, gear | 3,106 | 251.8 | 8.1 % | 3,397 | 276.5 |
| TC8 Grey full, fresh empty | 130 L grey, fuel, gear | 2,931 | 250.6 | 8.5 % | 3,222 | 275.3 |

- Plate: ATM 3,500 kg, the ute's braked towing rating and the limit of the DO35 and the chains (H2). The heaviest case with growth is 3,396.9 kg, 3.1 kg inside H2's 3,400 kg target (MAS-10). The examiner's caps from the tyres, coupling, chains and brakes are 3,500 kg (MAS-07, MAS-08).
- Water: at most 305 L of fresh and grey water while towing, H13's 350 L less 45 L by H21. The tanks hold 420 L and are filled at camp (H13). The grey tank travels empty, and TC7 and TC8 check the trailer with it full.
- Towball: at least 7.5 % in every case and at most 350 kg, the 79's, the towbar's and the DO35's rating (MAS-04, H14). While the masses are estimates the axle sits in the middle of a 14.5 mm window between 8.0 % in the lightest case and 320 kg with growth in the heaviest (MAS-12, MAS-13, H17).
- Ute: the heaviest towball puts the ute's rear axle at 2,601 kg with growth against the Elite kit's 2,800 kg plate (MAS-03, H18). MAS-14 reports the Platinum kit for the car build's cut CUT7.
- GCM: the ute with growth, 3,635 kg, plus the 3,500 kg plate is 7,135 kg against Lovells' 7,400 kg (GCM-01, UTE-06, H20). If the revision is refused, Toyota's 6,900 kg needs the trailer plated at or below 3,264 kg and at most 172 L of water in travel, so the fully loaded trailer with growth stays under that plate.
- Balance: the centre of gravity sits at most 32.9 mm to the kerb side against a 50 mm rule (MAS-11), at Z 1,230 to 1,317 mm with growth. The static stability factor is 0.61 to 0.65 on the 1,655 mm track.
- Roll: with the body rolled onto its bump stops and tyres, the static rollover threshold is about 0.42 g (est., Gillespie's method), over the 0.35 g of PBS level 1 and the 0.40 g target (STB-01, STB-02). Decision H22 widened the track from 1,555 to 1,655 mm for it, through the rails. The ute with the bikes aboard has a static stability factor of 0.89 (UTE-11).
- Sway: the yaw inertia is about 7,300 kg m² fully loaded with growth, and the towball never falls under 8.1 % of the trailer (STB-03). No snaking speed is estimated, because the published models need tyre and hitch data that are not known. The Bosch TSC brakes the trailer when it senses sway.
- Axles: the XT build carries 3,745 kg with VSB1's 120 % rule against its 4,050 kg, and each wheel 953 kg against its 1,400 kg (MAS-02, MAS-09).
- Parked in wind: unhitched on its corner steadies, the trailer slides on wet grass in a side gust of about 27 m/s at tare and 29 m/s fully loaded, forecast gusts of about 106 and 115 km/h, and tips over at about 30 and 33 m/s (STB-04, est.). When a forecast or a Bureau of Meteorology warning gives gusts of 90 km/h or more, close the awning, and hitch the trailer to the ute, strap it down or move it. With the ute away, strap it down whenever such gusts are forecast: four rated lashing points under the outrigger ends take ratchet straps at 45 degrees to screw-in ground anchors, a kit that rides in the bike box's tool chest. Strapped down it holds in region B's 500-year gust, 51.9 m/s at 3 m, with 13.1 kN in each windward strap (STB-05, the anchors' holding capacity est.). 90 km/h is the Bureau's threshold for damaging winds ([BoM](https://www.bom.gov.au/resources/learn-and-explore/severe-weather-knowledge-centre/severe-weather-and-coastal-hazard-warning-services)), under the 95 km/h that leaves a factor of 1.5 on the overturning moment. No stays in the cyclonic regions C and D in the cyclone season, 1 November to 30 April ([BoM](https://www.bom.gov.au/resources/learn-and-explore/tropical-cyclone-knowledge-centre)). The walls are designed for region B's 25-year wind, which takes in the Queensland coast (H23).
- Awning: close the awning in wind, legs pegged. Peg the legs whenever it is out, and close it before gusts reach 40 km/h, Beaufort force 5, and whenever the trailer is left. Fiamma gives no speed. Its roof bolts are checked with the canopy open in a 60 km/h gust (BDY-11), a check of the fixing only: the 40 km/h rule is what protects the canopy, its arms and its legs.

## Structure

The chassis is a galvanised ladder frame (CHASSIS.md revision E, CT-101 to CT-104). Two RHS 150 x 50 x 3 C450L0 rails each carry a continuous RHS 127 x 51 x 3.5 C350L0 raiser, so the floor clears the 805 mm tyres. Eight stations carry crossmembers and outriggers, and the drawbar is RHS 150 x 50 x 5. The rails are 1,275 mm over their outsides for the 1,655 mm track (H22). Steel and zinc weigh 505 kg. Checked at the plate, the recovery pull governs at 0.91 of yield, VSB1's drawbar tests reach 0.76 and the travel cases 0.53. The frame twists 0.373 degree against 0.5, and every fatigue detail stays below its endurance limit. Heavy items bolt through the floor into the raisers and outriggers (CT-104).

## Body and roof

The shell is bonded sandwich panels in aluminium joiners (BODY.md revision C, CT-201 to CT-203): a 30 mm GRP and PVC foam floor, 35 mm GRP and XPS walls 2,000 mm tall, and a fixed 40 mm roof that carries the solar panels. It bolts to the frame at 32 points and takes 98 % of the twist. Six aluminium members on the inner skin, RHS 110 x 19 x 3.5 made to order with 13 mm of XPS behind them, hold each side wall to 19.7 mm in region B's 25-year wind (AS/NZS 1170.2), against 20 mm (BDY-10, H23), and stand at least 25 mm clear of every opening, gland and insert strip (FIT-07). No metal crosses the core, and each stops 10 mm short of the joiners, so on the design cold night, at ISO 13788's surface resistance of 0.25 m²K/W, the inside surface over them stays at 10.2 °C or more to their ends, against report 19's rule of the dew point plus 4 K (BDY-22).

The roof is fixed, with rounded front edges, 150 mm at the roof edge and 250 mm on the front verticals (H12). Towing at 90 km/h it uses 21.3 L/100 km, against 25.0 with a square front and 20.6 with a hard raising roof, which would add 117 kg and about AUD 32,900 and rule out the S4 windows, the stock doors, the lift bed and a full-height wet room (research report 25).

Four Dometic S4 windows (W1 and W2 at the bed, W4 in the kitchen, W6 frosted in the wet room) and the glass in both doors have integrated blackout blinds (H8, H15, CT-011, CT-013). W1's 804 x 454 mm opening is the second way out. All 17 openings keep 300 mm of wall between them (BDY-18).

The awning is a Fiamma F80s 400 on the roof's kerb edge, its case 5 mm inside the wall's skin. Its five brackets bolt through the roof's insert strip with Panelok APLB-1024 bolts, whose grip takes the 40 mm roof (BDY-11). Its legs stand on the ground: set for a 10 degree fall they are about 2,531 mm long and keep about 155 mm of reach for ground that falls away (BDY-23, est.). ADR 43/04 and VSB1 5.2 allow 2,500 mm and leave out only the lamps and reflectors, so every frame, hood, cowl, handle and box on a side wall counts. The S4 frames stand 21 mm proud, the hoods, cowls and flush-mounted inlet boxes at most 30 mm and the entry door's handle 40 mm (est.), so the trailer is 2,470 mm wide against a 2,490 mm design limit (DIM-01, DIM-05, TR-11).

## Lift bed and desk

A Lippert HappiJac four-rail lift carries a 1,550 x 2,290 mm honeycomb platform and a 180 mm queen mattress across the trailer (H1). By day and in travel the platform's underside is 1,600 mm up, so a seated adult clears it. At night it stops at 805 mm, with the mattress top at 1,044 mm, 956 mm clear above it and 75 mm over the desk (BED-01). Index plungers lock it, a safety edge stops it on an obstruction, and a socket at the rail tops lowers it by hand. The lift is rated 272 kg standing and 204 kg moving (Lippert), so at night the bed takes two adults of up to about 208 kg together (BED-02). The desk is 1,200 x 600 mm at 730 mm against the front wall, and nothing else stands under the bed.

## Kitchen

All electric, with no LPG (H5). The road-side tower holds the Truma Combi D 6 E, the Dometic NRX 130C fridge and the Camec 28 L convection microwave as the oven. The bench carries the Dometic CVI1525 induction hob over the CFX3 55IM freezer on a slide, and the sink with the pump and filters below. The hood is ducted outside.

## Wet room and rear door

The rear door D2, hinged on its kerb edge, opens straight into a 1,000 mm deep wet room across the full width (H4). An outdoor shower box beside the door rinses off sand and mud first, and a grate with a sand basket sits just inside. A folding step stows upright in each doorway.

- Floor: one moulded GRP tray with 100 mm upstands and lips at both doors, falling 1:60 to its drains. The walls are the body's gelcoat skins, so the room can be hosed down.
- Shower: a DauerShower 2.0 cleans and reheats the same 5 L, so two 20 min showers use about 10 L and 1.3 kWh. Its switching unit sits in an insulated well 120 mm below the shower floor (H4a).
- Toilet and basin: a Thetford C223-CS cassette toilet with two spare cassettes, and a basin with a mirror cabinet on the partition. An inner door leads forward.

## Laundry

A Camec 3.5 kg washer and a Haier 7 kg heat-pump dryer stand on the battery plinth near the axle (H6). The dryer needs no vent. A wash and dry takes 44 L and about 1.6 kWh.

## HVAC and fresh air

Research report 19's load calculation gives a design hot day of 37.1 kWh of heat to remove, peaking at 3.29 kW, and a design cold night of 17.6 kWh over 14 h (CT-621).

- Cooling and heating: a Mitsubishi Electric 2.5 kW inverter split (H7). The indoor unit sits high on the partition, the outdoor unit high on the rear wall on wire-rope isolators, its cradle on two stays to the chassis (BDY-21). It uses 9.0 kWh of battery on the hot day, 5.1 kWh less than the best rooftop unit.
- Backup: the Truma Combi D 6 E heats air and water on diesel or on its elements.
- Fresh air: two LUNOS e2 60 pairs exchange 60 m³/h by day and 45 m³/h at night through 83 % heat recovery, holding CO₂ near 900 ppm for two. A filtered top-up fan adds 15 m³/h, so the cabin sits about 3 Pa above outside, and a relief valve lets the excess out through the wet room. A wet room extract and the ducted hood remove moisture at the source.
- Dust: while towing, a Sy-Klone RESPA-CF2 with a powered precleaner and MERV 16 and carbon filters holds about 20 Pa, and the other fans stop. No window needs to open.

## Electrical

48 V throughout (research report 20, CT-601, CT-602).

- Battery: five Victron Lithium NG 51.2 V 100 Ah modules, 25.6 kWh and 185 kg, in a sealed, vented and lined aluminium box that forms the plinth, with a heat detector (AS/NZS 3001.2).
- Conversion: a MultiPlus-II 48/6k5 inverter-charger feeds ten 230 V circuits on 30 mA RCBOs. Orion-Tr converters feed the 12 V and 24 V buses, and a Cerbo GX runs the load rules.
- Charging: four Sunman 430 W panels give about 9.3 kWh on the design hot day, the ute's chargers 3.6 kWh on a 5 h drive, and the two EU22i put a hot day back in 8.4 h while the household runs. Shore power and the generators have a 15 A inlet each, side by side, and a SHORE - OFF - GENERATOR changeover switch on the board feeds the MultiPlus-II's one AC input from one of them.
- Generators: they run on the ground at least 6 m from the trailer and downwind of it, exhausts pointing away, never in the drawbar box. Fans C and D of the e2 pairs sit low on the front wall, facing the generators, so on GENERATOR one auxiliary contact of the changeover switch opens their 12 V feed and a second tells the Cerbo GX, on its digital input 3, which shows the mode. Fans A and B on the side walls run on as a pair, and the RESPA-CF2 holds the cabin above outside through its MERV 16 and carbon filters, so the cold night's dew point stays at -1.7 °C (BDY-22). The GENERATOR position also bonds neutral to earth on the generator side, because an inverter generator's neutral commonly floats (Honda to confirm), so the RCBOs keep an earth return. The licensed electrician confirms it under AS/NZS 3001.2 (ELI-01). The switch and the second inlet cost about AUD 250 and weigh 0.5 kg (est.).
- Autonomy (H3): the design hot day, all electric with the air-conditioning, two showers, cooking, a wash and dry, desk work and Starlink, takes 19.6 kWh. With 90 % usable, the battery alone runs it for 25.1 h when new and 17.2 h at end of life. The cold night takes 4.7 kWh on diesel heat or 11.2 kWh on the heat pump.
- Shedding: the shower heater drops out first when the hob or the oven runs, and the shower stays warm on boiler water. The Combi element, washer and dryer follow. The split never sheds. The worst managed load is 89 % of the inverter's 40 °C rating.
- Fire: a 2 kg ABE extinguisher stands by each outside door, D1 and D2, with a fire blanket at D1, a smoke alarm and a CO alarm (VSB1 13.2.2). They cover the wet room whether or not it counts as a second compartment. A dry powder unit will not stop a lithium module in thermal runaway, so if the battery box smokes or burns, open the 300 A isolator, get everyone out and call 000. The extinguishers are for a fire that has not reached the box (LA-16).
- Lamps: the ute drives them at 12 V through the 12-pin plug. The rear lamps and red triangles sit on the rear outriggers, three amber side markers go on each side, and end-outline lamps sit high at both ends. The plate sits on the rear wall's kerb half, its top at 1,224 mm. All 24 checks to ADR 13/00 and VSB1 3.1 pass, the outdoor unit's cradle stays included (CT-003, CT-011).

## Plumbing and water

- Fresh: two welded HDPE tanks over the axles hold 420 L, filled at camp through a Puretec CR45 filter by hose or the creek transfer pump, with a chlorine dose. A Shurflo Trail King 7 at 2.1 bar feeds every outlet, the drinking tap through a CR-Z2 filter and a UV purifier. The Combi's 10 L boiler gives hot water through a 50 °C mixing valve (CT-611, CT-612).
- Grey: every drain falls by gravity to a 130 L tank in the rear bay, with a valve and a camlock on the kerb side. It travels empty (CT-003's operating limits), TC7 and TC8 check the trailer with it full, and a 40 L tote serves longer stays.
- Budget for two a day: showers 10 L, dishes 8, drinking 6, basin 6, outdoor rinse 4, cooking 3, flush 2 and cleaning 2, so 41 L, 27 L of it to grey. A wash adds 44 L. The 305 L aboard lasts about 7 days without laundry, and the full tanks 7 days with three washes. The grey tank holds 72 h with one wash.

## Running gear and coupling

- Cruisemaster XT Freestyle Air, the 4,500 kg build, axles 900 mm apart on LC5 hubs with 12 inch ABS-enabled electric drums, a Bosch TSC for ABS and sway control, and the Level 3 manual air kit, set from its panel. A spare airbag travels with it.
- The ute's ROH Trak 2 16 x 7 ET 0 steel wheel, rated 1,400 kg, with LT265/75R16 123/120 tyres, so each vehicle's spare fits both. The 1,655 mm track (H22) runs each tyre 50 mm outside the ute's 1,555 mm ruts, so 215 of its 265 mm tread stays in them.
- A Cruisemaster DO35 V3Plus at the ute's 440 mm laden ball height, chains to AS 4177.4, a breakaway kit, a 12-pin plug and a grey Anderson SB50 for the 48 V charging feed. The jockey wheel swings up along the drawbar, 157.5 mm under the bike box at a jack-knife (JK-02). Four corner steadies.

## Drawings

CT-001 general arrangement, CT-002 mass and centre of gravity, CT-003 compliance, CT-010 floor plan with the bed up and down, CT-011 elevations, CT-012 sections, CT-013 window, door and hatch schedule, CT-101 to CT-104 chassis, drawbar, details and load paths, CT-201 to CT-203 body, CT-301 body to chassis, CT-601 and CT-602 electrical, CT-611 and CT-612 plumbing, and CT-621 HVAC. `make` draws them from the model.

## Build order

Each stage needs the ones before it. Each weighing, TW-01 to TW-03, takes the lines fitted by then (`build_order` in `data/assemblies/trailer.yaml`). They and the other inputs to measure are on the Measurements page with the range the design accepts.

| Stage | Work | Needs first | Check before moving on |
|---|---|---|---|
| B0 Approvals | Engineer's review, RAV entry and VIN, orders for the XT kit, panels, tray, windows, doors and imports | The documents and drawings | Review closed, VIN issued |
| B1 Chassis | Cut, jig, weld, stamp the VIN | B0, steel and plate parts | Weld inspection (report 02 WLD-03) |
| B2 Galvanising | Hot-dip to AS/NZS 4680, touch up | B1, vent and drain holes | Frame flat and square |
| B3 Rolling chassis | Suspension, brakes, TSC, wheels, mud flaps, coupling, chains, breakaway kit, jockey, steadies, alignment | B2, the XT kit | TW-01 within 2 % of the model |
| B4 Floor | Bearer strips, tanks, guards, diesel tank, air box, the floor on its 32 mounts, the shower well and the tray | B3, the floor panel with its inserts | Tray fill test, 24 h |
| B5 Shell | Walls with their stiffeners, rounded corners and roof bonded into the joiners, doors and windows | B4, panels with their hardpoints laid in | Hose test, TW-02 within 2 % |
| B6 First fix | Cables, the 230 V bulkhead, glands, water pipes, drains at 1:50, ducts and fan sleeves | B5 closed and dry | Water lines pressure tested |
| B7 Fit-out | Battery box, board, partition, cabinetry, appliances, lift bed, split, wet room, awning, steps, blackout covers, stone guard, lamps, drawbar box and generators, spare wheel, solar | B6 | Bed locks and safety edge |
| B8 Commissioning | Electrical test, battery capacity, airflow and pressure, tanks filled and dosed, bed heights, overall width | B7 | AS/NZS 3001.2 certificate, TW-03 to TW-05, TR-01 to TR-11 (TR-11 at most 2,490 mm, DIM-05) |
| B9 Registration | Permit to move it, HVAIS inspection with the identity approval, plate, NSW registration | B8, the weighbridge tickets | Plate at 3,500 kg ATM |

The insert map CT-203 must be final before the panels are ordered, because the maker lays the bed hardpoints, stiffeners and insert strips into the cores.

## Cost and where to save

The parts list is `data/trailer-parts.yaml` with the priced lines of the mass schedule: 153 lines in AUD including GST, each with its source and the date checked. Listed prices carry 10 % contingency and rates and estimates 20 %, so the AUD 204,154 subtotal carries AUD 32,262 (15.8 %), for AUD 236,416. Without hired labour it is AUD 188,464.

| Group | AUD | Group | AUD |
|---|---|---|---|
| Hired labour, 333 h | 39,960 | Chassis | 5,456 |
| Body | 37,642 | Licensed electrician | 4,600 |
| Electrical | 23,708 | Drawbar box | 4,388 |
| Living area | 21,186 | Under the floor | 3,162 |
| Running gear | 14,181 | Roof | 2,926 |
| HVAC and ventilation | 12,667 | Coupling and drawbar | 1,695 |
| Wet room | 11,627 | Lamps, reflectors and the number plate | 905 |
| Bed | 8,028 | Spare wheel | 736 |
| Compliance | 5,976 | Freight and consumables | 5,310 |
| Subtotal | 204,154 | | |

The ten largest savings, with their contingency and what each costs the requirements. The site's parts list works out all fifteen from the lines. Some share lines, so they do not add up.

1. No hired labour: AUD 47,952. About 333 h of Leonard's time, and the chassis welds still need a qualified welder and the engineer's inspection.
2. Only the fit-out done yourself: AUD 25,488, part of the first. About 177 h.
3. Two self-built EVE MB31 packs in place of the Victron modules: AUD 6,113. More capacity, but no AS IEC 62619 test, so the electrician may refuse the certificate, and the cell terminals loosen on corrugations.
4. A plain low-flow shower: AUD 5,779. Two 20 min showers then use about 240 L a day.
5. A fixed bed at night height: AUD 5,450. The desk loses its place under the bed, so H1 fails.
6. A 230 V water heater and the heat pump in place of the Combi: AUD 5,308. No heat or hot water without the battery.
7. No engineer's review: AUD 5,280. Not required in NSW, but the designs stay unchecked.
8. Square front edges: AUD 4,200. About 3.7 L/100 km more towing, about AUD 1,550 a year.
9. No generators: AUD 4,085. Cloud with no drive then needs shore power.
10. No freezer: AUD 2,455. Frozen food fits only the fridge's 8.2 L compartment.

Smaller ones: a Carafan fan for the RESPA (AUD 1,521), one generator (AUD 1,336, 24.7 h to put a hot day back), no UV purifier (AUD 1,207) and no dryer (AUD 1,099). A rooftop air-conditioner costs AUD 3,443 more than the split, because its extra 5.1 kWh a day needs a sixth battery module.

## Decisions

Each is in full in `docs/decisions.md`.

- H1, H1a: a lift bed over a 1.2 m desk with the rest of its footprint empty, 2,000 mm inside. Leonard's ask, and a fixed loft leaves too little room over the mattress.
- H2: a 3,500 kg plate, Lovells' 7,400 kg GCM and at most 3,400 kg fully loaded with growth, so the home fits the 79's ratings.
- H3: 24 h of a design hot day on the battery alone when new and 12 h at end of life. Leonard's power ask.
- H4, H4a: a wet room across the rear with its own door, the shower's unit in a floor well. Rinse before entering, with full headroom.
- H5, H6: an electric kitchen with a convection microwave as the oven, a washer and a heat-pump dryer. No LPG and no vent.
- H7, H8, H15: an inverter split with diesel backup, filtered heat-recovery fresh air, four windows and two door glasses with blackout blinds.
- H12: a fixed roof with rounded front edges. Most of a raising roof's fuel saving without its mass, cost and losses.
- H13: at most 350 L of water in travel with both generators, 305 L since H21. It holds the 3,400 kg target.
- H14, H17: towball limits from the ute's rear axle and the 350 kg ratings, the axle centred in an 8.0 % to 320 kg window. Margin while the masses are estimates.
- H16: the bed's footprint stays empty, as Leonard asked.
- H20: one combination figure, the ute with growth plus the plate, and UTE-04's weighed target retired. UTE-03 checks the rear axle itself.
- H21: mass added after H13 comes off the travel water in 5 L steps, so the 3,400 kg target and the plate stay. The final review's fixes and H22's wider rails took 30 L, and the fix-pass review's fixes 10 L more.
- H22: a 1,655 mm track on 1,275 mm rails lifts the rollover threshold from 0.37 g to 0.42 g, and costs 50 mm of each tyre's 265 mm tread outside the ute's ruts.
- H23: the walls serviceable in region B's 25-year wind and strong at 41 m/s, the highest speed that tips the parked trailer, an operating rule for the parked trailer in wind (STB-04), and tie-downs for when the ute is away (STB-05). Leonard will camp on the Queensland coast, which is region B and non-cyclonic.

## Open points and the assumption used

1. Storage is about 0.2 m³ short (est.). Assumption: the footprint stays empty (H16). Question for Leonard: two 500 x 600 x 700 mm cabinets under the bed beside the desk would add 0.42 m³ and about 20 kg, and break his rule that the rest of that area stays empty.
2. Estimate lines carry 904 kg, 34.5 % of the tare, and estimates set 56.1 % of the price subtotal. Assumption: the growth allowance covers the masses until TW-01 to TW-03 replace them, and the 20 % contingency covers the prices. A towball reading more than 10 % off the model means the centre of gravity estimates are wrong (UTE-03).
3. Assumption: Lovells' 7,400 kg GCM is certified in the ute's LC5 inspection. If not, plate at or below 3,264 kg and tow with at most 172 L (H20).
4. Assumption: the isolators and the line set keep the split working on corrugations, without a maker's warranty. The fallback is a rooftop unit with a sixth battery module.
5. The Dometic fridge, freezer, hob and sink carry converted European prices, and the oven, washer, panels, lamps and labour are estimates. Assumption: these prices stand, with their contingency, until an Australian stockist or a quote replaces them.
6. Assumption: the engineer accepts calculation as VSB1's evidence for the drawbar and chain tests at 3,500 kg (CHASSIS.md).
7. Assumption: no anti-roll bar is fitted, and the 1,655 mm track (H22) meets the 0.40 g target without one. Question for Cruisemaster: the rate of its optional XT anti-roll bar and whether it clears the fresh tanks in the XT bays, as more margin if TR-01's measured centre of gravity comes out higher than the estimate.
8. Fiamma publishes no length for the F80s 400's leg, 98667-04, the same part as on the F80L. Assumption: it reaches 2,686 mm like the 320's leg, which ships in the same carton. If it is shorter, the canopy falls more steeply on the same ground (BDY-23).
9. No published force coefficient fits a box-shaped trailer on its wheels. Assumption: ASCE 7-16's 1.6 for a solid sign of these proportions, the high side, for STB-04's rule. A box's 1.05 would put the overturning speeds about a quarter higher.

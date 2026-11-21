# 19: HVAC, fresh air, windows, doors and the wet room shell

Status: research record, 20 Nov 2026. It sized the cooling and heating from a load calculation and chose the fresh-air system, windows, doors, steps and wet room tray for decisions H4, H7 and H8. Its products are in the trailer's mass schedule and parts list.

Positions are in the project datum DIM-01. "Maker" means a published figure, "calculated" means worked out in `research/models/19/loads.py` or from a maker's data, and "(est.)" marks a judgement with no maker figure. Prices are AUD including GST. The product data is in `research/19-hvac-windows-doors.yaml` beside this report.

## Recommendations

Energy is for the design days of section 1. "AC" is the 230 V side, "battery" includes the MultiPlus at 93 %. Masses marked (est.) are estimates, the rest are maker or listing figures.

| Function | Product | Mass | Power | Energy per design day | Price AUD | Change against the current line |
|---|---|---|---|---|---|---|
| Cooling and heating | Mitsubishi Electric MSZ-AP25VGKD2 indoor and MUZ-AP25VGD2 outdoor, R32, with the vehicle mounting package (section 2) | 56.5 kg: 10.5 indoor, 35 outdoor, 11 package (est.) | Cooling 0.21 to 0.99 kW, heating 0.35 to 1.40 kW, 7.1 A at most | Hot day 8.4 kWh AC (9.0 battery), peak 912 W. Cold night 6.1 kWh AC if the heat pump heats | 1,299 unit (JB Hi-Fi listing) plus about 1,500 package and install (est.) | Replaces LA-10 Saphir (25.0 kg): +31.5 kg, and 8.5 kWh a day less than the Saphir |
| Cold-weather and low-battery heat, hot water | Truma Combi D 6 (keep, H7) | 19.4 kg | 1.8 to 4 A at 12 V | Cold night 1.9 L diesel and 0.42 kWh | No change | LA-03 unchanged |
| Fresh air with heat recovery | LUNOS e2 60 short, two pairs, MERV 13 Comfort Screen covers, sound-insulated stainless hoods, 5/UNI-FT controller | 5.3 kg (est.) | 0.4 to 3.3 W a fan, about 6 W at 60 m3/h | 0.13 kWh at 12 V (est.) | 4,098 (2 kits, USD 1,322 each, converted) | New |
| Wet room extract | LUNOS RA 15-60 on the same controller | 1.2 kg (est.) | 1.6 W at 30 m3/h, 5 W at 60 m3/h | 0.03 kWh at 12 V (est.) | 700 (est.) | Replaces the bathroom vent in BD-09 (1.5 kg) |
| Towing and dust-storm pressurisation | Sy-Klone RESPA-CF2, 24 V, brushless, MERV 16 filter, odour (carbon) filter for smoke | 6 kg (est.) | 144 W running, 288 W at start | None on a parked design day. 144 W from the ute while towing | 3,000 (est.) | Replaces the Carafan CP700 in BD-09 (7.0 kg est.): -1 kg |
| Parked overpressure and smoke-mode fresh air | 24 V EC fan in a box with ISO coarse prefilter, ePM1 80 % panel and carbon cassette (est.) | 2.5 kg (est.) | 3 to 8 W | 0.12 kWh at 24 V (est.) | 350 (est.) | New |
| Pressure relief and monitoring | Automotive body pressure-relief valve (30 cm2) and a 0 to 125 Pa gauge | 0.5 kg (est.) | Under 1 W | Nil | 340 (est.) | New |
| Kitchen extract | Sphere TCR-001 hood, two 12 V fans, ducted through the side wall to a cowl with a backdraft flap | 6 kg with duct (est.) | 25 to 50 W (est.) | 0.06 kWh (est.) | 350 (est.) | New |
| Sensors and Cerbo GX integration | Three RuuviTags with a USB Bluetooth adapter, an SCD41-class CO2 sensor, relay wiring | 0.4 kg (est.) | About 2 W | 0.05 kWh (est.) | 400 (est.) | New |
| Windows | Six Dometic S4 top-hinged with blackout roller and fly screen: 900 x 600 (escape), 2 x 900 x 450, 700 x 450, 900 x 550, 500 x 450 obscured, plus two clip-in blackout covers | 46.6 kg | Nil | Nil | 4,355 (converted, one est.) | BD-09 windows 30.8 kg: +15.8 kg |
| Roof hatches | None | Nil | Nil | Nil | Nil | None today. No change |
| Entry door, kerb side | Aussie Traveller DC door with pleated blind, 1,750 x 622 mm, no vent | 21 kg (listing) | Nil | Nil | 1,549.99 | BD-07 (25 kg, 1,623 mm): -4 kg |
| Rear door into the wet room | The same door, with the opposite hinge as the layout sets | 21 kg (listing) | Nil | Nil | 1,549.99 | New. Replaces the 600 x 450 rear window |
| Steps, both doors | Torklift GlowStep Revolution Uprising, doorway-mounted, four steps with landing gear | 30 kg for two (est.) | Nil | Nil | 2,800 for two (est.) | New |
| Wet room shell | Moulded GRP floor tray with falls, linear grate and sand basket, GRP cove trims, body skins as walls | 26 kg (est.) | Nil | Nil | 2,050 (est.) | Replaces the LA-01 pan (7.5 kg): +18.5 kg. The layout recounts the LA-01 walls |
| Outdoor rinse | Watermarked External Shower Box, hot and cold | 1.5 kg (est.) | Nil | Water only | 159 | New |

Totals. These lines weigh 224.5 kg against 96.8 kg for the lines they replace (+127.7 kg). New functions that H4 and H7 ask for make up 85.4 kg of it: the rear door, the steps, the wet room tray, the ventilation, hood and sensors, and the rinse box. The split's 31.5 kg buys 8.5 kWh a day less than the Saphir, worth about 60 kg of battery at 7 kg per kWh. Ventilation, extract, hood and sensors add about 0.39 kWh a day of DC load for report 20. The lines cost about AUD 24,500, of which about AUD 12,100 is estimates.

## 1. Thermal loads

`research/models/19/loads.py` is an hourly heat balance of the body with no third-party modules. Its output is `research/models/19/loads.out`. The panels have thin skins and store little heat, so each hour is treated as steady.

Inputs.

- Body 4,420 x 2,400 mm outside, 4,350 x 2,330 x 1,950 mm inside. The air volume is 19.8 m3, not the 25 m3 first assumed, and the floor is 10.1 m2.
- Panels from report 12 with λ 0.031 W/m.K for the XPS and the H80 and 0.30 W/m.K for the GRP skins (est.). U is 0.83 W/m2K for the walls, 0.72 for the roof and 1.01 for the floor, plus 20 % for thermal bridges.
- The 20 % holds up. 35 m of aluminium joiners at a ψ of about 0.15 W/m.K (est.), 32 M12 mount bolts at 0.03 W/K each (est.) and the insert strips add about 7.3 W/K. That is 20 % of the 36.8 W/K of the bare panels.
- Glass 2.82 m2 at U 2.8 W/m2K (est. for double acrylic with its frame), SHGC 0.55 (est., tinted), and 0.55 of that gain with the pleated blackout blind closed (est.). The window list is section 7's. Door leaves 2.31 m2 at U 1.6 (est.).
- Sun: ASHRAE's clear-sky model at latitude 25 S on 21 December, scaled to 1,000 W/m2 horizontal at noon. Walls white gelcoat at an absorptance of 0.40 (est., dusty). Red soil reflects 0.25.
- Roof: the four bonded Sunman panels cover 8.9 m2 of the 10.6 m2. They absorb about 0.90 of the sun and send about 0.18 out as electricity, so 0.72 heats the roof (est.). The white roof first assumed is run as a variant.
- Two adults inside for all 24 h (ASHRAE: 70 W sensible and 45 W latent awake, 60 and 25 W asleep).
- Appliance heat (figures of the kind report 21 gives, est.): fridge and freezer 1.8 kWh, standby (MultiPlus-II idle, router, Cerbo GX, fans, hot water losses) 1.6 kWh, desk 0.6 kWh, MPPT losses 0.3 kWh, half the hob heat and 70 % of a 45 min oven bake, two 20 min showers, one wash and one heat-pump dry (1.2 kWh into the room).
- Fresh air (section 3): 60 m3/h by day and 45 m3/h at night through regenerators at 80 % recovery. Unrecovered: a 15 m3/h pressurisation top-up (section 4), the range hood at 100 m3/h while cooking, the wet room boost after each shower, and 0.1 air change an hour for gusts and doors.
- Outdoor dew point on the inland hot day about 7 C (est.).

Design hot day (blinds down on sunlit glass, the worst heading: front to the south, kerb side to the east):

| Item | 24 h heat, kWh |
|---|---|
| Roof | 4.3 |
| Floor | 3.5 |
| Walls | 7.4 |
| Window conduction | 2.0 |
| Window sun | 3.9 |
| Doors | 1.2 |
| Ventilation, sensible | 3.4 |
| People, sensible | 3.2 |
| Appliances | 8.2 |
| Latent, net | 0.0 |
| Total to remove | 37.1 |

The peak is 3.29 kW at 18:00, with the hob, the oven and the hood's makeup air at 39 C outside. Without the dinner hour the peak is 2.7 kW at 11:00 while the dryer runs. Internal gains are 31 % of the day. The net latent load is zero because the inland air is drier than the room. The headings differ by 1.2 kWh at most.

| Variant | 24 h kWh | Peak kW |
|---|---|---|
| Design, as above | 37.1 | 3.29 |
| Blinds up all day | 39.1 | 3.32 |
| Blinds down all day | 36.4 | 3.28 |
| White roof, no PV (the roof first assumed) | 35.9 | 3.29 |
| Vented dryer in place of a heat-pump dryer | 35.9 | 3.29 |
| Tropical day: 35 C peak, 27 C low, dew point 25 C | 46.9, of it 15.7 latent | 4.26 |

Design cold night (-5 C, 20 C inside, 14 h from 17:00, blinds closed): the heat loss is 1.57 kW before internal gains. The net heat to add is 17.6 kWh over the 14 h. Hour-by-hour figures for both days are in `research/models/19/loads.out`.

## 2. Cooling and heating unit

Every class was checked against H7 (an inverter heat pump), the 3.29 kW peak and the 37.1 kWh day of section 1. Energy is from `research/models/19/loads.py` with each unit's published points.

Performance. Cooling at 35 C outside (AS/NZS 3823 T1 or ISO 5151). COP is cooling or heating out over electricity in.

| Unit | Cooling, rated (min to max) | Input, rated (at min) | COP rated, at min | Heating at 7 C | Heating at 0 and -5 C | Start current | Outdoor limits |
|---|---|---|---|---|---|---|---|
| Truma Saphir Comfort RC, under-bench | 2.4 kW, fixed speed | 0.97 kW (4.2 A) | 2.5, cycles | 1.7 kW at 3.7 A | None, stops below +4 C | 20 A for 150 ms | +4 to +43 C ([Truma AU](https://www.truma.com/au/products/air-conditioning-systems-au/saphir-box/saphir-comfort-rc/)) |
| Dometic FreshWell 3000, under-bench | 2.7 kW, fixed speed | 0.99 kW | 2.7, cycles | 3.0 kW | Not published | Soft start | Not published (report 13). Not sold in Australia. Its successor FWX4 is 2.0 kW, EU only ([Dometic](https://www.dometic.com/en/product/dometic-freshwell-fwx4-9620013224)) |
| Cool-J iHider220, under-bench inverter | 2.93 kW | 0.87 to 1.0 kW | 3.0, not published | 2.78 kW, COP 3.4 | Works to -7 C, output not published | Not published | -7 to +43 C ([TrueGear](https://truegear.com.au/products/cool-j-ihider220-inverter-under-bunk-air-conditioner)) |
| Dometic FreshJet FJZ7 Pro, rooftop inverter | 3.4 kW | Not published. 6.1 A at most | 3.0 and 3.3 (est.) | 3.4 kW | Stops below -2 C | Soft start, settable power limit | -2 to +52 C ([Dometic AU](https://www.dometic.com/en-au/product/dometic-freshjet-fjz7-pro-9630000083)). Inverter per its manual |
| Dometic CoolAir RTX 2000, 24 V DC rooftop | 2.0 kW, variable speed | 120 to 720 W (5 to 30 A at 24 V) | 2.8, about 4 (est.) | None, cooling only | None | Soft start, DC | +5 to +52 C ([Dometic](https://www.dometic.com/en/product/dometic-coolair-rtx-2000-9600010233)) |
| Mitsubishi Electric MSZ-AP25VGKD2 / MUZ-AP25VGD2, split | 2.5 kW (1.10 to 3.60) | 0.50 kW (0.21) | 5.0, 5.2 | 3.2 kW (1.3 to 5.0) at 0.67 kW, COP 4.8 | About 4.0 and 3.3 kW at most, COP about 3.7 and 2.9 (est.) | Inverter soft start, 7.1 A at most | Cooling -10 to +46 C, heating -15 to +24 C ([Mitsubishi Electric AU](https://www.mitsubishielectric.com.au/product/msz-ap25-80vgd-split-system-air-conditioner/)) |

Build, service and price.

| Unit | Mass | Size L x W x H mm | Noise | Refrigerant | Record on corrugated roads | Warranty in a caravan | Australian service | Price AUD |
|---|---|---|---|---|---|---|---|---|
| Saphir Comfort RC | 23.5 kg | 628 x 400 x 290 | Not published | Not published | Long in European vans. Sold for Australian vans by Truma Australia | Yes, Truma | Truma Australia | 1,890 (TrueGear listing, 20 Nov 2026) |
| FreshWell 3000 | 21 kg | 628 x 400 x 286 | Not published | Not published | European vans | Yes, Dometic | None found | Not sold here |
| iHider220 | 26 kg | 734 x 405 x 296 | Not published | R32, 0.41 kg | New brand, no record found | Retailer warranty, not published | Cool-J through retailers | 1,690 (TrueGear listing) |
| FJZ7 Pro | 36 kg on the roof | 1,090 x 700 x 242, 400 x 400 roof cut | Brushless fans, sleep mode | R32 | The Dometic rooftop line (Harrier before it) has the longest record on Australian vans | Yes, Dometic (5 years on the FJZ range in the US) | Dometic service agents nationwide | 2,500 (Dometic AU listing) |
| RTX 2000 24 V | 32 kg on the roof | 860 x 645 x 308 | Quiet truck parking cooler | R134a, allowed in vehicles | Long, in truck sleeper cabs | Yes, Dometic | Dometic truck channel, listed for AU | 5,855 (EUR 3,485 converted, Dometic DE) |
| MSZ-AP25 split | Indoor 10.5 kg, outdoor 35 kg | Indoor 798 x 219 x 299, outdoor 800 x 285 x 550 | Indoor 19 to 44 dB(A), outdoor 46 dB(A) | R32, 0.7 kg, pipes to 10 m without extra charge | None found. An owner forum reports a household unit failing from off-road vibration ([DIY Solar Forum](https://diysolarforum.com/threads/residential-air-conditioner-failure-due-to-off-road-vibration.26367/)) | Assume none: it is sold for buildings | Mitsubishi dealers and any licensed refrigeration mechanic, in every regional town | 1,299 supply only (JB Hi-Fi listing, MSZAP25VGKD2KIT) |

Australia's 2024 ban on small high-GWP air-conditioners exempts equipment for vehicles and caravans, so R134a in the RTX is legal ([ARC](https://www.arcltd.org.au/media/jm3lq4p0/arc-media-release-20240702-ban-on-high-gwp-small-ac-equipment.pdf)).

Energy on the design days (`research/models/19/loads.py`, battery side through the MultiPlus at 93 %, the RTX straight from 24 V):

| Unit | Hot day kWh | Hot day unmet kWh | Cold night kWh | Tropical day kWh |
|---|---|---|---|---|
| MSZ-AP25 split | 9.0 | 0 | 6.6 | 10.7 (0.7 unmet at dinner) |
| MSZ-AP35 split | 9.5 | 0 | 6.8 | 11.2 |
| FJZ7 Pro rooftop | 14.1 | 0 | No heat below -2 C | 16.3 |
| iHider220 | 14.6 | 0.5 | 8.3 | 16.3 |
| FreshWell 3000 | 16.7 | 1.0 | No heat | 18.3 |
| Saphir Comfort RC | 17.5 | 2.5 | No heat | 19.1 |
| RTX 2000 24 V | 11.1 | 5.7 | No heat | 12.6 |

Recommendation: Mitsubishi Electric MSZ-AP25VGKD2 indoor and MUZ-AP25VGD2 outdoor (kit MSZAP25VGKD2KIT), with the vehicle mounting package below.

- It uses 5.1 kWh a day less than the next inverter unit (the FJZ7 Pro, whose COP is estimated). At 7 kg of battery per kWh that is about 35 kg, about one 5.12 kWh battery module.
- It heats down to -15 C and cools up to 46 C. Of the others only the iHider220 heats at -5 C, using 1.7 kWh more on the cold night. The under-bench units stop cooling at 43 C, one degree above the design day.
- It leaves the roof to the solar array. A rooftop unit displaces one of the four 430 W panels.
- Its 3.6 kW maximum covers the 3.29 kW peak. The AP35 adds headroom only on a tropical evening and costs 0.5 kWh a day.
- Any licensed refrigeration mechanic in a regional town can service it with standard parts.
- The risk is vibration: no record on corrugated roads, and no warranty in a trailer (assumption). The package below answers it. The body rides on the XT air suspension, which already filters most corrugation input.

Vehicle mounting package (est., for the designer and the installer):

1. Outdoor unit in an aluminium cradle on four stainless wire-rope isolators sized for about 9 kg each, natural frequency 6 to 8 Hz loaded (est.). The cradle bolts through insert strips into the wall. A perforated aluminium guard surrounds it with a lift-off cover over the coil for travel.
2. Refrigerant lines: no flare joint between the isolators and the body. Use a braided vibration absorber on each line at the cradle and brazed or press fittings (Lokring or Zoomlock type) elsewhere. Clamp the lines every 300 mm in rubber-lined clamps. The installer holds an ARC refrigerant licence, pressure tests with nitrogen and evacuates to 500 microns.
3. Indoor unit on its backing plate, screwed into an insert strip and bonded, with two safety straps so it cannot unhook on a bump.
4. Condensate through a trap straight into the wet room floor waste.
5. Unit off and cover on while towing. Inspect the isolators and clamps after each rough trip and leak-test every 12 months.

Fallback: if Leonard wants a vehicle-rated unit with a maker's warranty, use the Dometic FreshJet FJZ7 Pro. It costs 5.1 kWh a day more, one roof panel, 36 kg at roof height and all heating below -2 C.

Where it goes and how air reaches the rooms. The indoor unit mounts high on the living side of the wet room partition, beside the inner door, its top about 50 mm under the ceiling. The door head is too high to put it above the door. It blows forward along the trailer over the kitchen and the desk and onto the bed. No ducts are needed in 4.35 m. The outdoor unit goes high on the rear wall on the side away from the rear door. The pipe run is then about 2 m, the unit is out of the stone spray and the jack-knife sweep, and its hot discharge blows away from the rinse area. The other place is high on the front wall behind a stone guard, which the layout checks against the bike box at a jack-knife. A side wall is out: the 285 mm depth breaks the 2,500 mm width limit of VSB1 clause 5.2. On the rear wall the unit moves the ball load about 18 kg down, and on the front wall about 21 kg up.

Energy for report 20. Design hot day 8.4 kWh AC side, 9.0 kWh battery side. Peak 912 W at 18:00. The worst 12 h window is 6.6 kWh AC. Design cold night 6.1 kWh AC with the heat pump, or 1.9 L of diesel and 0.42 kWh at 12 V with the Combi D 6. The hourly profile is in `research/models/19/loads.out`.

The diesel Combi D 6 stays (H7). On the cold night it saves 6.2 kWh of battery for 1.9 L of diesel, and it heats the water. It is the backup when the battery is low, and the heat pump covers mild nights on solar.

## 3. Fresh air

Rate. CO2 sets the rate. The adult CO2 generation rates of [Persily and de Jonge (2017)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5666301/) for men aged 30 to 40 are 0.0037 L/s at 1.0 met, 0.0046 L/s at 1.2 met and 0.0076 L/s at 2.0 met. The script uses 0.0039 asleep, 0.0050 seated and 0.0077 L/s for light work, with 425 ppm outside. To hold 1,000 ppm two people need 49 m3/h asleep, 63 m3/h seated and 96 m3/h moving about. ASHRAE 62.2 asks less: Qtot = 0.03 Afloor + 7.5 (Nbr + 1) cfm, that is 18 cfm or 31 m3/h for 109 ft2 and one bedroom ([Retrotec summary](https://retrotec.com/blog/residential-ventilation-primer/?v=92a31fc033f7)). So the CO2 figure governs.

Design rates. 60 m3/h through the heat recovery by day and 45 m3/h at night, plus the 15 m3/h filtered top-up of section 4. That gives 75 m3/h by day (3.8 air changes an hour, 905 ppm seated) and 60 m3/h at night (3.0 an hour, 893 ppm asleep). Boost to 120 m3/h plus the top-up for cooking or visitors (836 ppm at 2.0 met).

Candidates.

| Unit | Airflow | Power | Recovery | Filters | Supply | Mass | Size and wall | Price AUD | Filters, cost and interval |
|---|---|---|---|---|---|---|---|---|---|
| LUNOS e2 60 short, two pairs (four fans) | 5 to 60 m3/h a pair | 0.4 to 3.3 W a fan, about 6 W for 60 m3/h (est.) | 83 % up to 60 m3/h, 94 % at most ([LUNOS](https://cdn.shopify.com/s/files/1/2642/2036/files/TechInfo_e260_E348-02.20.pdf?v=1621935013), [e2 60 short](https://www.lunos.de/alle-produkte/e260kurz)) | G3 washable, pollen (MERV 9 to 10), MERV 13 Comfort Screen ([475 Supply](https://cdn.shopify.com/s/files/1/0694/2117/0961/files/lunos-e2-spec-sheet-june-2024.pdf)) | 12 V DC, controller 5/UNI-FT at 12 V | About 1.2 kg a fan with sleeve, hood and cover (est.) | Ø154 mm insert, Ø162 mm hole, 200 mm sleeve | 4,098 for two MERV 13 kits (2 x USD 1,322, converted, [475 Supply](https://475.supply/products/lunos-e-kit)) | G3 3-pack USD 23.87, washable ([475](https://475.supply/products/lunos-filters-multi-pack)). MERV 13 about USD 40 a pair (est.). Check monthly in dust, 3 to 6 months otherwise (est.) |
| Mitsubishi Lossnay VL-100EU5-E | 60 or 105 m3/h | 15 or 31 W | 80 or 73 %, enthalpy paper core | Washable coarse | 230 V | 7.5 kg | 620 x 265 x 200 mm, wall 50 to 550 mm, two 75 mm holes ([Mitsubishi Electric NZ](https://mitsubishi-electric.co.nz/materials/PRODUCT/Ventilation/VL-100EU5-E/00_Publications/02_Brochure/LossnayVL100-EU5.pdf)) | About 1,100 (est.) | Wash every 3 months (est.) |
| Vents Micra 60 | 30, 45 or 60 m3/h | 4.2, 9.6 or 15.4 W | 79, 74 or 70 %, plastic counterflow | G4 both sides | 100 to 240 V | 10.3 kg | About 526 x 393 x 187 mm, two Ø125 mm ducts ([manual](https://cdn.shopify.com/s/files/1/0827/8671/3876/files/Micra_60_Ductless_HRVuser.pdf?v=1695326163)) | Not found | G4, 3 months (est.) |
| Zehnder ComfoAir 70 | 15 to 60 m3/h | 4 to 17 W | 72 % (DIBt), 85 % at 20 to 40 m3/h, humidity 64 % | G4, supply F7 (ePM10 60 %) option | 230 V | 22 kg | 440 x 660 x 145 mm, wall at least 275 mm, outside air to 40 C ([Zehnder](https://zehnderamerica.com/wp-content/uploads/2024/08/CA-70-Technical-Specifications.pdf)) | Not found | G4 and F7 |
| Blauberg Vento Expert A50-1 W V.3 | Up to 50 m3/h a unit | From 5 W | Up to 95 %, alternating ceramic | Not checked | 230 V | Not checked | Ø160 mm duct ([data sheet](https://www.smartfire.pt/wp-content/uploads/2018/02/bl_vento_expert_a50_1_w_v_3_2022_05_en-1.pdf)) | Not found | Not checked |
| Vents Micra 100 ERV | 30 to 100 m3/h | 12 to 45 W | 83 to 96 %, enthalpy | G4, F7 option | 230 V | 31 kg ([Vents](https://ventilation-system.com/product/micra-100-erv/)) | Too heavy | |

Panasonic's small WhisperComfort ERV is a 120 V product for North America and was not taken further. No balanced 12 or 24 V ERV other than LUNOS was found.

Recommendation: two pairs of LUNOS e2 60 short with MERV 13 Comfort Screen inner covers and sound-insulated stainless hoods, on one 5/UNI-FT controller with its humidity sensor.

- It runs from 12 V through the Orion 24/12-70, so ventilation needs no inverter on nights without air-conditioning.
- It uses less than half the power of the 230 V units at 60 m3/h, and has the highest recovery and the lowest mass of the units that fit.
- Each fan sits in a Ø162 mm hole. The 35 mm wall leaves 165 mm of sleeve inside, hidden in an overhead cupboard or a bulkhead box.
- The e2 60 meets pressure stability class S1 (20 Pa) of EN 13141-8, so wind on the wall does not stall it.
- LUNOS has an Australian distributor, Ampvolt in Victoria ([Ampvolt](https://ampvolt-redesign.squarespace.com/ventilation-decentralised)).
- Its weaknesses: it recovers only 20 to 30 % of the moisture, so it helps against winter condensation but gives up latent recovery in the tropics. MERV 13 is about ePM1 50 %, so the ePM1 80 % filter and the carbon sit in the pressurisation unit of section 4.

Positions and settings. One pair in the bed and desk zone, one fan high on each side wall. One pair in the kitchen and living zone, the same way. Each pair then sweeps across the trailer. Settings: day 30 m3/h a pair, night 22.5 m3/h a pair, boost 60 m3/h a pair for 30 min after cooking or a shower, and off in smoke mode (section 6). Seal each sleeve to both skins with MS polymer through a high-density PVC ring bonded into the core.

## 4. Dust and pressure

How off-road vans do it. Report 12 section 8 found two answers: seal every gap, and push filtered air in so the inside stays above the outside. Australian products are the Carafan Sahara CP700 (a fan and filter that pressurise while driving), the Gusto DRS (a wall fan and filter, up to 18 A at 12 V) and the Dometic DRS2 (an unpowered roof scoop, which needs roof space this trailer does not have). Mining cabs solve the same problem harder. ISO 23875 requires a cab to hold between 20 and 200 Pa above outside with the machine's power on ([summary](https://aethair.io/standards/iso_23875/)).

What the body sees. From `research/models/19/loads.py`: at 80 km/h the dynamic pressure is 296 Pa. The rear wake sits about 90 Pa below ambient (Cp -0.3) and the upper front about 180 Pa above it (Cp +0.6). The ute and its bike box shelter the lower front. Dust is drawn in wherever the inside is lower than the outside next to a leak, which is the doors, the rear and the underside.

Body tightness target: an effective leakage area of 30 cm2 or less. That is 60 m3/h at 50 Pa, about 3 air changes an hour at 50 Pa (est., a tight house standard). At that area 15 m3/h of excess supply holds about 3 Pa, 40 m3/h about 20 Pa and 85 m3/h about 100 Pa.

Specification.

1. Parked: the filtered top-up fan supplies 15 m3/h more than the extracts, 25 % of the 60 m3/h exchange, for about +3 Pa in calm air. In wind or dust it goes to 40 m3/h for about +20 Pa.
2. Towing (dust mode): the e2 pairs, the wet room fan and the hood stop. The towing fan supplies 150 to 200 m3/h through its precleaner and filter. With nothing extracting, every leak flows outward, and the inside sits at least 20 Pa above the rear wake (the ISO 23875 band).
3. Intake: high on the front wall, above the line of the bike box, with a mesh stone guard. The air there is faster and cleaner than the dust plume from the ute's tyres, and its ram pressure helps the fan. No intake goes at the rear, on the underside or near the wheels.
4. Pressure relief: one automotive body pressure-relief valve (a rubber flap vent that opens at a few Pa and closes against back-flow), about 30 cm2 free area, low in the rear wall of the wet room under a hood. The excess air then sweeps the wet room and leaves into the lowest-pressure zone. The stopped e2 sleeves also vent outward.
5. Seals: compression seals pulled up by latches on every door and hatch. The rear door and the entry door have three-point or triple compression locks (section 8). The cassette door gets a gasket and two compression latches. Windows stay latched shut while towing. Every penetration goes through a sealed gland (report 12 section 8).
6. Monitoring: a cabin pressure display (Sy-Klone RESPA Advisor+ 2.0 or a 0 to 125 Pa differential gauge) so a falling pressure shows a blocked filter or a failed seal.

Towing fan: Sy-Klone RESPA-CF2, 24 V, brushless motor, RadialSHIELD MERV 16 (F9) filter, with the carbon (odour) filter for smoke.

| Item | Value | Source |
|---|---|---|
| Airflow | 0 to 221 m3/h ideal, 425 m3/h at most | [Sy-Klone](http://www.sy-klone.com/air-quality-systems/fresh-air-systems/) |
| Power | 144 W running, 288 W at start | Same |
| Precleaner | Powered, removes at least 90 % of dust at 5 µm before the filter | Same |
| Filters | HEPA, EPA, MERV 16/F9, odour (carbon), ABEK gas | [CF2 sheet](https://www.sy-klone.com/wp-content/uploads/2026/01/CF2_SLS_0226.pdf) |
| Temperature | -40 to +85 C | Fresh air systems page |
| Mass | About 6 kg (est., not published) | |
| Price | About AUD 3,000 (est., not published. A 24 V motor alone is USD 490 in [Sy-Klone's store](https://store.sy-klone.com/rcf2919-respa-cf2-service-part-24-volt-compact-brushed-motor-and-motor-housing)) | |

Why it beats the CP700: its performance is published, it is built for ISO 23875 cabs in mines, and the precleaner throws most road dust out before it reaches the filter, so a long dusty tow does not choke the filter. Its 144 W comes from the ute through the Orion-Tr while towing. The CP700 is the fallback if Leonard wants a caravan product with caravan dealers: AUD 1,890 ([Carafan](https://carafan.com.au/product/carafan-sahara-white/), listed at 1,718.18 before GST), made by United Safety & Survivability Corporation, about 5.8 A at 12 V (an owner's measurement). Its airflow and filter class are not published.

Top-up fan (est.): a 24 V EC radial fan in a sealed aluminium box with an ISO coarse prefilter, an ePM1 80 % panel and a carbon cassette. 15 to 40 m3/h at up to 100 Pa, 3 to 8 W, 2.5 kg, about AUD 350. It is also the only fresh air in smoke mode. The RESPA-CF2 is assumed to run at one speed, so it cannot do this job at a few watts.

## 5. Extraction and condensation

The NCC sets house exhausts at 25 L/s (90 m3/h) for a bathroom and 40 L/s (144 m3/h) for a kitchen or laundry, discharged to outside air (Housing Provisions 10.8.2, [VBA practice note](https://www.vba.vic.gov.au/__data/assets/pdf_file/0010/187570/Building-GE-15-Condensation-Management-CURRENT-04-Dec-2024.pdf)). A caravan is not under the NCC, but the figures are a fair yardstick.

Kitchen range hood. Sphere TCR-001 touch-control hood from Coast RV: two 12 V fans, variable speed, aluminium mesh filter, venting through the rear or the top ([Coast RV](https://www.coastrv.com.au/products/sphere-range-hood-with-touch-control)). Coast does not publish its flow. Assume 100 to 150 m3/h at full speed, 2 to 4 A at 12 V and 5 kg (est.). Duct it through the side wall, not the roof, in 100 mm duct to a wall cowl with a gravity backdraft flap. The Dometic CK150 is the other 12 V hood sold here, but it vents through a roof dome, and the roof is solar. The loads assume the hood on low (100 m3/h) while cooking, about 1.75 h a day.

Wet room extract: LUNOS RA 15-60. A 12 V radial exhaust fan built for the same Ø162 mm sleeve as the e2 and powered from the same 5/UNI-FT controller. It runs at 15, 30, 45 or 60 m3/h, 1.6 W at 30 m3/h and 5 W at 60 m3/h, IP44 ([LUNOS](https://cdn.shopify.com/s/files/1/2642/2036/files/Installation_Manual_RA_15-60_final.pdf?v=1634725895), [hybrid use](https://site-556247.mozfiles.com/files/556247/RA15-60_en.pdf)). It goes high in the wet room's road-side wall.

- Through the ERV or separate? Separate. Alternating regenerators blow half the time inward, so an e2 in the wet room would push steam back in. The RA 15-60 only extracts. LUNOS designs this mix ("hybrid ventilation"): the e2 pairs recover heat in the living space and the RA fan extracts from the wet room only when needed.
- Settings: 15 m3/h base whenever the top-up fan runs, so the living area stays above the wet room and steam moves outward. 60 m3/h during each 20 min shower and for 30 min after.
- Steam: a 20 min shower puts about 0.3 kg of water into the air (est.). To hold the wet room air near 25 g/kg against 9 g/kg coming in from the living area needs about 47 m3/h, so 60 m3/h clears it. The NCC's 90 m3/h would need a second RA 15-60. That is an owner option (open point 6).

Dryer exhaust, both cases.

- Heat-pump (condenser) dryer: no exhaust duct, no makeup air, no lint outside. Its 1.2 kWh per load (est.) stays in the room as heat, which is in the design-day loads. Condensate goes to the grey tank. Recommended.
- Vented dryer: a 100 mm duct to the road-side wall with a lint trap and a sprung backdraft flap. It pulls about 150 m3/h of conditioned air out while running, so open the top-up fan to full during the cycle. On the hot day it saves 1.2 kWh of heat but costs about 1 kWh of makeup air (est.). The flap is a dust path when towing, so its outlet sits on the leeward rear half of the road side.

Condensation on the cold night (`research/models/19/loads.py`, -5 C outside, 20 C inside):

| Case | Fresh air m3/h | Indoor RH | Dew point |
|---|---|---|---|
| Two asleep | 60 | 25 % | -0.5 C |
| Two asleep, towels drying | 60 | 30 % | 2.3 C |
| Evening hour, cooking and a shower, hood and RA fan on | 60 | 38 % | 5.5 C |
| The same with the e2 pairs on boost | 115 | 28 % | 1.1 C |
| The same with the top-up off | 45 | 48 % | 8.7 C |

Coldest inside surfaces: window glass with the blind open 10.9 C, aluminium corner joiners about 10.0 C (est., temperature factor 0.6), wall panel 17.3 C, door leaf 14.8 C.

How the design avoids it:

1. Remove moisture at the source: the hood while cooking and the RA fan on boost after showers.
2. On cold nights the 5/UNI-FT humidity sensor boosts the e2 pairs above about 40 % RH. That holds the dew point at 6 C or lower, 4 K below the bare joiners.
3. Cover every aluminium corner and roof joiner inside with 10 mm closed-cell foam under the lining, which lifts its surface to about 15 C (est.).
4. Leave a 10 mm air gap behind cupboards on outside walls, with grilles top and bottom.
5. The blinds sit inside the window frame, so no curtain traps cold, damp air against the glass.
6. Panel cores are closed-cell XPS and H80 behind GRP skins, so no vapour reaches the core.

## 6. Controls

Sensing.

| Quantity | Sensor | Where | Used by |
|---|---|---|---|
| Temperature, air-conditioner | The indoor unit's own sensor and remote | Living area | MSZ-AP25 |
| Humidity and temperature, living | Built into the LUNOS 5/UNI-FT | Living area, away from the hob | e2 pairs and RA fan |
| Humidity and temperature, rooms | Three RuuviTag sensors (bed, living, wet room) | Read by the Cerbo GX over Bluetooth, with a USB Bluetooth adapter as Victron recommends ([Venus OS 2.80](https://www.victronenergy.com/blog/2022/1/31/venus-os-v2-80)) | Display, logging, alarms |
| CO2 | One NDIR sensor (Sensirion SCD41 class) with Modbus or MQTT output | Bed zone, at head height when the bed is down | Node-RED boost of the e2 pairs above 900 ppm |
| Cabin pressure | Sy-Klone RESPA Advisor+ 2.0 or a 0 to 125 Pa gauge | One port inside, one in a sheltered spot outside | Towing check, filter alarm |

Who controls what.

- The air-conditioner runs on its own thermostat: 24 C in summer and 20 C in winter. It sits on 230 V from the MultiPlus.
- The 5/UNI-FT runs the two e2 pairs and the RA 15-60 on humidity and on switches. The switches are boost (30 min), night and off.
- A small 24 V controller runs the top-up fan through 0 to 10 V or PWM.
- The RESPA-CF2 switches on from the trailer plug's auxiliary feed while towing, and from a "dust" switch when parked.
- The diesel Combi D 6 keeps its own Truma panel.
- The range hood keeps its own touch panel.

Modes (one rotary switch or Cerbo GX page):

| Mode | e2 pairs | RA 15-60 | Top-up fan | RESPA-CF2 | Air-conditioner |
|---|---|---|---|---|---|
| Normal day | 30 m3/h a pair | 15 m3/h, boost on humidity | 15 m3/h | Off | Thermostat |
| Night (quiet) | 22.5 m3/h a pair | 15 m3/h | 15 m3/h | Off | Quiet fan, outdoor night mode (3 dB lower, maker) |
| Towing (dust) | Off | Off | Off | On, 150 to 200 m3/h | Off |
| Parked, dust storm | Off | Off | 40 m3/h | On | Thermostat |
| Smoke | Off | Off | 15 to 40 m3/h through the carbon | Off, or on with the odour filter | Thermostat |
| Low battery | 22.5 m3/h a pair | 15 m3/h | 15 m3/h | Off | Setpoint up 2 K. Heat by diesel |

Quiet night mode: the indoor unit runs at 19 dB(A) on its quiet speed (maker), and the e2 60 pairs at 22.5 m3/h are about 20 to 30 dB(A) at 1 m (est., between the 10 and 48 dB(A) LUNOS gives for 5 and 60 m3/h).

Victron Cerbo GX integration.

- Venus OS reads RuuviTag temperature and humidity natively. A Cerbo relay can be set to switch on temperature without extra software ([Victron community](https://community.victronenergy.com/t/feature-suggestion-venusos-should-allow-for-temperature-alarms/21226)).
- Venus OS Large adds Node-RED, which can switch relays from any sensor reading ([Victron](https://www.victronenergy.com/live/venus-os:large)). Node-RED then does three jobs: it boosts the e2 pairs on CO2 through a 5/UNI-FT switch input wired to a Cerbo relay, it switches the RESPA and the top-up fan by mode, and it sheds load by raising the air-conditioner setpoint when the battery state of charge falls below about 30 % (assumption, report 20 sets the figure).
- The MSZ-AP25 has built-in Wi-Fi for Mitsubishi's MELCloud app, which needs an internet link. For local control, a CN105-port interface (ESPHome type, owner fitted) can bring setpoint and on-off into Node-RED over MQTT. That part is an option, not needed for the design to work.
- Every subsystem keeps working with the Cerbo off. The Cerbo adds logging, alarms and the CO2 boost.

## 7. Windows and roof hatches

Requirement: no curtains, full blackout, off-road durable, double glazed.

| Family | Glazing | Blackout | Insect screen | Off-road record and Australian support | Mass | Verdict |
|---|---|---|---|---|---|---|
| Dometic S4 (Seitz), top-hinged | Double acrylic, grey tint, ECE R43 | Roller blind with an aluminium-coated face in the inner frame | Roller fly screen in the same frame, clips to the blind | The standard European caravan window for decades. Dometic Australia imports and supports the S4 and S7P ([CaravansPlus](https://www.caravansplus.com.au/brand/seitz/)) | 5.0 kg (500 x 450) to 16.2 kg (1,600 x 600) | Chosen |
| Camec push-out with roller blind and flyscreen | Acrylic, double glazed versions sold | Roller blind | Yes | Australian brand, the most common in local builds ([DIY Caravans](https://www.diycaravans.com.au/diy-guide-caravan-windows-and-skylights/)). Walls 25 to 50 mm, sizes 500 x 350 to 1,200 x 500 ([manual](https://cdn.shopify.com/s/files/1/0810/5925/0474/files/Camec_Window_Manual_v4.pdf?v=1755659777)) | Not published | Fallback. Blind grade and masses not published |
| Polyplastic Polyvision | Flush-bonded double acrylic | Integrated blinds | Yes | European OEM supply. Australian stock not found | Not checked | Not taken further |
| Hinged exterior aluminium shutters | Any window | Full, hard | No | Expedition trucks use them as stone guards | About 3 kg for a 900 x 600 window (est., 2 mm sheet) | Only on a front window |
| Aircraft-style hard sliding shades | | | | None found for caravans | | |
| Switchable films (PDLC, SPD, electrochromic) | Film or laminated | No. PDLC only frosts, SPD stays a see-through dark tint, electrochromic glass bottoms out near 3 % light ([Smart Films](https://www.smartfilmsinternational.com/post/pdlc-vs-spd-smart-glass), [Polytronix](https://polytronixglass.com/smart-glass-overview/)) | | Needs power and a controller | | Rejected |

Recommendation: Dometic S4 top-hinged windows throughout. Double acrylic in a polyurethane frame, friction hinges that hold any opening position, a lock that stops opening from outside, and the blackout roller and fly screen in the inner frame ([Dometic](https://www.dometic.com/en/product/dometic-s4-75), [size and mass table](https://www.wohnwagen-fenster.com/produkt/ausstellfenster/dometic-s4-ausstellfenster-rahmenfenster-rollo-camping-wohnwagen-wohnmobil/)). The inner frame suits 26 mm walls and takes spacer strips up to 53 mm, so the 35 mm wall needs 9 mm strips. The blind runs in side channels, so a little light can show at its edges (est.). For the two bed windows add a clip-in 3 mm black ABS cover in the inner frame, 0.6 kg each (est.), for total darkness. That is the hard cover asked for, and it stows behind the blind cassette.

Schedule (positions are the layout's. Prices converted from [wohnwagen-fenster.com](https://www.wohnwagen-fenster.com/produkt/ausstellfenster/dometic-s4-ausstellfenster-rahmenfenster-rollo-camping-wohnwagen-wohnmobil/), 20 Nov 2026, EUR at 1.68):

| ID | Use | Product, nominal W x H | Cut-out | Clear opening | Mass | Price AUD |
|---|---|---|---|---|---|---|
| W1 | Bed, emergency exit, kerb side | S4 900 x 600, 9104115572 | 902 x 599 | 804 x 454, 0.365 m2 | 9.2 kg | 890 |
| W2 | Bed, road side | S4 900 x 450, 9104115569 | 902 x 448 | 804 x 304 | 8.0 kg | 719 |
| W3 | Desk | S4 900 x 450, 9104115569 | 902 x 448 | 804 x 304 | 8.0 kg | 719 |
| W4 | Kitchen | S4 700 x 450, 9104115558 | 702 x 448 | 604 x 304 | 6.5 kg | 605 |
| W5 | Living area | S4 900 x 550, 9104115571 | 902 x 549 | 804 x 404 | 8.6 kg | 811 (EUR 482.79, [Camping Factory](https://www.camping-factory.com/dometic-seitz-s4-ausstellfenster-900-x-550-mm)) |
| W6 | Wet room, obscured | S4 500 x 450, 9104115546, with frosted film on the inner pane | 500 x 448 | 404 x 304 | 5.1 kg | 551 with film (est. 30) |
| G1 | Entry door glass | In the Aussie Traveller DC door with pleated blind (section 8) | | | In the door | |
| G2 | Rear door glass | The same door | | | In the door | |
| | Two clip-in blackout covers for W1 and W2 | 3 mm black ABS (est.) | | | 1.2 kg | 60 (est.) |

The six windows weigh 45.4 kg against 30.8 kg in BD-09 today (+14.6 kg, mostly because there is one more window and W1 grows for escape).

Rules for the layout. The bed windows sit with their sill about 960 mm above the floor, level with the night mattress top (950 to 1,050 mm), and the outer frame head at most 1,600 mm, so the bed in its day position does not cover the blind cassette. W1 is the second way out: no Australian rule sets an escape window (report 12), so the project rule is a clear opening of at least 0.33 m2 with no side under 450 mm (assumption), which the 900 x 600 meets. Keep report 12's 300 mm of full wall between openings and 150 mm from any opening to a panel edge. Put no window on the front wall unless it gets a hinged aluminium stone shutter, because gravel off the ute's tyres crazes acrylic.

Roof hatches: none. The bonded array covers 4,108 x 2,168 mm of the 4,420 x 2,400 mm roof and leaves 156 mm at each end and 116 mm at each side. A Dometic Mini Heki needs a 400 x 400 mm cut-out ([Dometic AU](https://www.dometic.com/en-au/product/dometic-mini-heki-plus-9104119636)), so any hatch costs one 430 W panel. The design does not need one: the e2 pairs and the RA fan supply and extract all the air, and W1 is the escape route.

## 8. Doors and steps

(a) Rear door into the wet room: Aussie Traveller DC Caravan Door with Pleated Blind, 1,750 x 622 mm, no-vent version, black, round top corners. Part 71917500622080 (left-hand hinge) or 71917500622081 (right-hand hinge), AUD 1,549.99 ([Aussie Traveller](https://aussietraveller.com.au/products/caravan-dc-door-with-pleated-blind-left-hand-hinge), listing, 20 Nov 2026). Listed shipping mass 21 kg.

- Opens outward, as VSB1 clause 13.2.1 requires.
- Triple compression lock: one handle pulls the door onto its seal at three points. Water and dust resistant seal ([catalogue](https://cdn.shopify.com/s/files/1/0542/4939/0251/files/5_Caravan_Doors.pdf?v=1723079234)).
- Tinted UV-resistant acrylic window with a built-in pleated block-out blind running in tracks, so it does not rattle. This is the G2 glass of section 7.
- Security screen door of fibreglass midge mesh and stainless steel, so the door can stand open for a breeze.
- Suits walls of 25 to 40 mm. The leaf is 1,750 mm tall, the minimum asked for, and 622 mm wide, so the clear width is about 570 mm (est.). If the layout wants more width, the 1,750 x 675 mm version (white, left hinge, 71417500675120, AUD 1,579.99) is the only wider door at this height, and its vent would then be sealed.
- Take the no-vent version. The standard door has a fixed passive vent, and in a pressurised body with no LPG it is only a leak.

Also considered: the Coast RV 4-Point Door (four-point lock, acrylic window, screen door, pre-drilled for a Coast roller blind, but with a 248 cm2 passive vent built in, [Coast RV](https://www.coastrv.com.au/products/coast-4-point-door-range)), and the Camec and Hartal doors. The DC door wins on its integrated blind, the no-vent option and the same family as the entry door, so one set of seals, keys and spares serves both.

(b) Steps for a floor 925 mm above the ground. Four risers of about 231 mm are needed.

| Option | Fit | Effect on clearance | Mass, price | Verdict |
|---|---|---|---|---|
| Torklift GlowStep Revolution, 4 steps (A8004), mounted under the sill | Floor heights 826 to 1,016 mm, treads 203 x 572 mm, 170 kg rating, aluminium and stainless, adjustable landing gear ([Torklift Central](https://torkliftcentral.com/rving-and-towing/travel-trailers-and-towables/step-systems/torklift-international-glowstep-revolution)) | Folds under the floor. At the rear wall a stowed step about 350 mm deep (est.) would cut the departure angle from about 29 to about 19 degrees (est., from the rear tyre to the rear wall) | About 14 kg, about AUD 1,240 (est.) | Kerb door only, if the layout accepts the clearance |
| Torklift GlowStep Revolution Uprising, mounted in the doorway | The same scissor step. It stows upright inside the door opening. Landing gear adds up to 190 mm of adjustment ([Torklift](https://www.torklift.com/products/steps-and-handrails/glowstep-revolution-uprising)) | None. Nothing hangs under the body | About 15 kg, about AUD 1,400 (est.) | Chosen for both doors |
| Caravan electric step (Camec, Aussie Traveller) | One or two steps | Hangs under the body | 8 to 12 kg (est.) | Too few steps for 925 mm |
| Removable aluminium step ladder hooked on the sill | Three treads | None, stows on wall clips inside | About 5 kg (est.) | Light fallback, less stable on soft ground |

Assumption: the four-step Uprising reaches 925 mm with its landing gear extended. If the range table says otherwise, take the five-step. In the wet room the stowed Uprising stands inside the rear door, so the wet room's floor plan keeps a 250 mm zone clear for it.

(c) Kerb-side entry door. The Aussie Traveller DC door still suits: it was chosen in report 12 for its triple compression lock and dust seal, and it is the same family as the rear door. Change it in two ways:

- Take the version with the built-in pleated block-out blind. The plain DC door has no integrated blind, only an add-on DC door blind (AUD 79.99).
- Take the no-vent version, 1,750 x 622 mm, in place of 1,623 x 622 mm. The taller door gives about 125 mm more headroom in the doorway and still leaves 200 mm of wall to the roof edge, above report 12's 150 mm rule. It is hinged on its front edge as before, so airflow closes it.

## 9. Wet room shell

The wet room is about 1,000 x 2,330 mm and 1,950 mm high, across the rear of the body (H4). Its outer walls and ceiling are the body's own sandwich panels, whose inner skin is already 1.5 mm gelcoat GRP (report 12).

| Option | Build | Mass (est.) | Leak risk | Verdict |
|---|---|---|---|---|
| One-piece GRP shell (floor, walls, ceiling) | Moulded off a plug, about 15.5 m2 of 3 mm laminate. Goes in before the roof | About 70 kg at 4.5 kg/m2 | Lowest. No joints | Heavy, doubles the body's own GRP, fixes the build order and cannot be replaced later |
| Bonded GRP lining panels on every surface | 2.5 mm GRP sheet bonded over the body skins, plus a tray | About 72 kg (52 kg panels at 4 kg/m2 plus a 20 kg tray) | Joints at every corner | Duplicates the skin that is already there |
| Body skins as the walls and ceiling, a moulded GRP floor tray, cove-sealed corners | Tray bonded to the floor, upstands bonded to the wall skins, GRP cove trims in every corner | About 26 kg (tray 21 kg, grate 2 kg, trims and sealant 3 kg) plus the partition | Corners and the tray upstand, all visible and resealable | Chosen |

Floor tray. One moulding, 1,000 x 2,330 mm, 4 to 5 mm laminate with gelcoat, about 7 kg/m2 (est.). Upstands 100 mm on the three outer walls and against the partition. The flat floor panel carries a foam wedge under the tray (H80 offcuts) so the tray top falls 1:60 to the drains. That is 19 mm of fall over the 1,165 mm half-width, so the tray top stands about 25 to 30 mm above the floor at its edges.

- Drains: a linear channel across the rear door and the shower's own outlet. The shower outlet feeds the recirculating shower's intake with a divert to grey (report 21 owns the shower plumbing). Every drain passes through the floor panel in a bonded HD PVC insert with a sealed gland.
- Rear door threshold: the tray's lip rises 30 mm inside the door frame. A drop-in stainless linear grate about 600 x 100 mm sits in a moulded channel just inside it, over a lift-out sand basket. Sand rinsed off feet stops there and is tipped out through the door. About 2 kg, AUD 150 (est.).
- Inner door threshold: a 30 mm GRP lip at the partition door, rounded so feet do not catch. Water stays in the wet room even with the trailer parked off level by about 1.5 degrees (est., 30 mm over 1,165 mm).

Sealing to the body.

1. Bond the tray to the floor with MS polymer (Sikaflex-552 class) over its whole underside, and bond the upstands to the wall skins.
2. Run a GRP cove trim over every wall-to-tray and wall-to-wall corner, bedded in MS polymer. No screw goes through the tray.
3. The partition stands inside the tray's upstand and is bonded to it and to the ceiling. It is a 20 mm composite panel with GRP skins both sides (the layout sizes it).
4. Seal the cassette door, the rear door and the window frames to the wall skins with butyl and MS polymer, as their makers specify. The extract fan sleeve and the outdoor unit's pipe gland go through high-density PVC rings.
5. Leak test: fill the tray to its lip before fitting out and leave it for 24 h.

Australian suppliers. Innovative Composites (Victoria) makes shower enclosures for caravans ([Innovative Composites](https://innovativecomposites.com.au/)). World Class Composites makes contract mouldings and moulds ([World Class Composites](https://worldclasscomposites.com.au/)). Either can lay up a one-off tray from a plug. A one-off tray with its plug costs about AUD 1,800 (est.).

Outdoor rinse at the rear door. A Watermarked External Shower Box, hot and cold mixer with hand shower in a lockable flush box, AUD 159 ([Campervan Builders](https://campervanbuilders.com.au/products/external-shower-box-watermarked-white), listing). It goes on the rear wall beside the door's handle side, about 1,000 mm above the ground. The person rinses standing on the ground or the bottom step, so the water stays outside. Feed it from the hot-water system and the pump with a non-return valve on each line. Report 21 counts its water, assumed 2 rinses of 5 L a day.

## 10. Insulation trade-off

`research/models/19/loads.py` re-runs both design days with 10, 20 and 30 mm more core in the walls (XPS), the roof (XPS) and the floor (H80), using the MSZ-AP25 on the battery side. The added mass uses report 12's materials: XPS at 33 kg/m3, H80 at 80 kg/m3, and 0.06 kg/m more extrusion per mm of thickness over 35 m of joiners (est.). Battery is credited at 7 kg per kWh a day (planning figure, report 20 to confirm).

| Core added | Hot day kWh saved | Cold night kWh saved | Panel mass added | Battery credit | Net mass |
|---|---|---|---|---|---|
| Walls +10 mm | 0.45 | 0.51 | 9.5 kg | 3.1 kg | +6.4 kg |
| Walls +20 mm | 0.73 | 0.83 | 19.1 kg | 5.1 kg | +13.9 kg |
| Walls +30 mm | 0.93 | 1.06 | 28.6 kg | 6.5 kg | +22.1 kg |
| Roof +10 mm | 0.25 | 0.25 | 5.6 kg | 1.8 kg | +3.8 kg |
| Roof +20 mm | 0.42 | 0.40 | 11.2 kg | 2.9 kg | +8.3 kg |
| Roof +30 mm | 0.54 | 0.51 | 16.8 kg | 3.8 kg | +13.0 kg |
| Floor +10 mm | 0.25 | 0.30 | 10.6 kg | 1.8 kg | +8.8 kg |
| Floor +20 mm | 0.40 | 0.48 | 21.2 kg | 2.8 kg | +18.3 kg |
| Floor +30 mm | 0.51 | 0.59 | 31.8 kg | 3.5 kg | +28.2 kg |
| All three +10 mm | 0.92 | 1.02 | 21.5 kg | 6.5 kg | +15.1 kg |
| All three +30 mm | 1.83 | 2.24 | 64.6 kg | 12.8 kg | +51.8 kg |

Recommendation: keep report 12's thicknesses (floor 30 mm, walls 35 mm, roof 40 mm). Every step adds more panel than it saves in battery. The closest to even is the roof at +10 mm, 3.8 kg heavier net. The reasons:

- Insulation acts on only part of the load. The envelope conduction is 18.4 kWh of the 37.1 kWh day, and people, appliances, sun through the glass and fresh air are untouched by core thickness.
- The split's COP of 4 to 5 means each kWh of heat saved is only 0.2 to 0.25 kWh of battery.
- The cold-night saving does not count toward the battery, because the diesel Combi D 6 heats on cold nights.
- Thicker walls also cost inside width at the fixed 2,400 mm outside: 20 mm for each 10 mm step. Thicker floor or roof panels raise the travel height or squeeze the 1,950 mm inside.

What would change the answer. Walls +10 mm breaks even at 21 kg of battery per kWh a day (9.5 kg for 0.45 kWh) and roof +10 mm at 22 kg (5.6 kg for 0.25 kWh). That happens only if the last kWh forces a whole extra 5.12 kWh module, which report 20 will see in its sizing. Re-run `insulation_tradeoff()` with report 20's figure.

Cheaper ways to cut the hot-day energy (from section 1, as heat to remove):

- Keep the blinds down on sunlit glass: 2.0 kWh a day less than blinds up.
- Run the awning over the kerb wall on the afternoon side: about 1 kWh a day (est., the kerb wall's share of wall and window sun).
- Prefer a heat-pump dryer cycle in the cooler morning, and cook on the outdoor induction hob when it is hot, if report 21 keeps one: up to 1.5 kWh a day of internal heat (est.).
- The bonded panels make the roof 1.2 kWh a day hotter than white gelcoat. A ventilated gap under them would win most of that back, but it needs rails and loses the bonded fixing report 13 chose, so it is not recommended.

## Open points and the assumptions to use

1. MSZ-AP25 heating below 7 C is not in Mitsubishi's Australian table. Use 4.0 kW at most and COP 3.7 at 2 C, and 3.3 kW and COP 2.9 at -5 C.
2. The split has no warranty in a towed trailer (assumption). Use the vehicle mounting package of section 2. The engineer picks the wire-rope isolators from a maker's catalogue for about 9 kg each and 6 to 8 Hz loaded.
3. Outdoor unit position. Use the rear wall, high, on the side away from the rear door. The layout checks the towball and axle loads (the unit moves the ball about 18 kg down) and may move it to the front wall behind a stone guard after a jack-knife check against the bike box.
4. FJZ7 Pro input power is not published. For the fallback use COP 3.0 at 3.4 kW, 3.3 at 1.2 kW and 2.6 at full output.
5. Body airtightness. Use an effective leakage area of 30 cm2. Acceptance test on the bare body: with the e2 sleeves taped, the RESPA-CF2 holds at least 50 Pa.
6. Wet room extract. Use one RA 15-60 at 60 m3/h on boost. A second fan would reach the NCC's 90 m3/h if Leonard wants it.
7. Range hood flow and power are not published. Use 100 m3/h on low while cooking, 150 m3/h at most and 25 to 50 W.
8. RESPA-CF2 mass, price and speed control are not published. Use 6 kg, AUD 3,000 and a single speed, so the separate top-up fan stays.
9. LUNOS e2 60 limits at -5 C and 42 C outside were not found. Assume both work: the ceramic regenerator reverses every 70 s and has no condensate drain to freeze.
10. Each e2 60 short needs a 200 mm sleeve, so 165 mm projects inside the 35 mm wall. The layout allocates four sleeves high on the side walls and one RA 15-60 sleeve in the wet room, all inside cupboards or bulkhead boxes.
11. Escape window. No Australian rule applies. Use a clear opening of at least 0.33 m2 with no side under 450 mm. The S4 900 x 600 gives 804 x 454 mm.
12. The S4 roller blind may leak a little light at its edges. Use the clip-in covers on the two bed windows.
13. GlowStep Uprising reach. Assume the four-step version with its landing gear reaches 925 mm. Take the five-step if the range table says otherwise.
14. Aussie Traveller DC door clear width. Use 570 mm for a 622 mm leaf.
15. Window walls and positions are the layout's. The loads used the schedule in `research/models/19/loads.py`. Moving windows between walls changes the day by 1.2 kWh at most.
16. Internal gains come from figures of the kind report 21 gives. Use a heat-pump dryer putting 1.2 kWh into the room, a 45 min oven bake at about 1 kW, and two 20 min showers. Report 21's figures drop into `appliances_hot()`.
17. Battery value of a kWh a day. Use the planning figure of 7 kg until report 20 confirms, then re-run section 10.
18. Outdoor dew point. Use 7 C on the inland design day and 25 C for the tropical check.
19. Wet room drains feed the grey system and the recirculating shower. Report 21 sizes the grey tank and the shower intake. Use one 40 mm floor waste and the linear channel at the rear door.
20. Prices marked (est.) are judgements. Use them as they stand. Report 22 checks them against listings.

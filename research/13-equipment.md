# 13: Appliances, equipment and the energy system

Note added 20 Nov 2026, for the LandCruiser 79: the tow vehicle is now a Toyota LandCruiser 79 single cab V8 in place of the Porsche Cayenne, and it carries both bikes in an enclosed box on its tray (UTE-GARAGE.md). Reports 14 to 16 and VEHICLE.md cover the vehicle, and TRAILER.md revision H is the smaller trailer without a garage, plated at 3,100 kg ATM. The products of this report stay. The generator and the fuel now ride in a drawbar box, and the DC-DC charger runs from the ute.

Note added 20 Nov 2026, after the equipment went into the design (TRAILER.md revision G). The design takes this report's products with three owner choices as defaults: washer only, no LPG and two batteries. Each one can be reversed in the data, and TRAILER.md lists what reversing it costs. Three things differ from this report. First, the 450 x 525 mm heater box clears the ladder landing but not the ladder itself, which stands beside the landing. So the washer's box is 470 mm wide in place of 600 mm, the washer is turned with its 445 mm width along the trailer, and the heater moves 130 mm towards the road side. The heater then clears the ladder by 5 mm. Second, the mass schedule carries each line's bought parts at 0 % growth and its estimated parts at 20 %, as this report splits them. The winch (G-11) is carried at 20 % on all its 10.5 kg, because the module's part file has one basis per part. Third, the floor is now at Z 872, so the kitchen bench in open question 13 sits about 1,372 mm above the ground, not 1,369 mm. The data for this report is published as `research/13-equipment.yaml`.

Research report, 20 Nov 2026. This report picks real products for the estimated appliance and equipment lines in `data/assemblies/trailer.yaml`, plus the module's loading winch (G-11 in `data/parts/garage.yaml`), so the mass schedule can carry maker figures and the layout can be checked with real sizes. It also sets a planning-level energy system. Products were chosen by the rules in `research/BRIEF.md`: reliability and a record of hard use first, then parts and service in Australia, then field serviceability, then the lightest. Price was ignored. The product data is in `13-equipment.yaml` beside this report.

Terms used:

- Maker figure: a mass or size the maker publishes. Retailer figure: one a stockist publishes. The mass schedule treats both as spec with 0 % growth, as `garage-bed/BOM.md` does.
- Calculated: worked out from the size and a material density, 7 % growth.
- Estimate: a judgement with its basis stated, 20 % growth.
- LFP: lithium iron phosphate, the battery chemistry used here.
- MPPT: the solar charge controller. It matches the panel voltage to the battery.
- DC-DC charger: a charger that takes the car's 12 V and charges the trailer battery while driving.
- kWh: energy. 1 kWh runs a 1,000 W load for one hour.
- Voc: a panel's open-circuit voltage. It sets how many panels can be wired in series.

## Recommendation

| Line | Chosen product | Mass (kg) | Maker or retailer | Calculated | Estimate | Now (kg) | Change (kg) |
|---|---|---|---|---|---|---|---|
| LA-01 | Wet bathroom: Thetford C223-CS cassette toilet, DauerShower 2.0 recirculating shower, GRP floor pan, bypass mixer, and the fabricated walls, door and lining | 57.1 | 17.2 | 0 | 39.9 | 100 | -42.9 |
| LA-02 | Camec 3.5 kg top-load washing machine, part 051879 (washer only, see below) | 16.0 | 16.0 | 0 | 0 | 65 | -49.0 |
| LA-03 | Truma Combi D 6, Australian version, with ducts, flue kit and a 15 L fuel tank | 21.7 | 17.2 | 0 | 4.5 | 30 | -8.3 |
| LA-04 | Victron MultiPlus-II 24/5000/120-50, two SmartSolar MPPT 150/45, Orion-Tr Smart 12/24-15, Orion 24/12-70, Lynx Smart BMS NG 500 A and Cerbo GX on one board | 45.6 | 37.7 | 0 | 7.9 | 60 | -14.4 |
| LA-05 | Dometic NRX 130C, 126 L compressor fridge | 29.0 | 28.0 | 0 | 1.0 | 35 | -6.0 |
| LA-06 | Dometic CFX3 55IM, 53 L chest fridge-freezer run as a freezer | 21.8 | 21.3 | 0 | 0.5 | 30 | -8.2 |
| LA-07 | Kitchen slide-out: Dometic CVI1525 induction hob, Dometic CVS1350G sink, Accuride 9301 slides, tap, and the fabricated box | 50.9 | 9.5 | 0 | 41.4 | 80 | -29.1 |
| LA-10 | Truma Saphir Comfort RC under-bench air-conditioner | 25.0 | 23.5 | 0 | 1.5 | 30 | -5.0 |
| UF-01 | Two custom welded HDPE tanks, 760 x 1,086 x 259 mm, 6 mm walls, baffled | 37.6 | 0 | 37.6 | 0 | 40 | -2.4 |
| UF-04 | Two Victron Lithium NG 25.6 V 200 Ah batteries (10.24 kWh) in a sealed aluminium box | 86.0 | 74.0 | 0 | 12.0 | 110 | -24.0 |
| GS-01 | Honda EU22i inverter generator | 21.1 | 21.1 | 0 | 0 | 40 | -18.9 |
| GS-02, GS-05 | None. No LPG, because the cooking is induction (section 3) | 0 | 0 | 0 | 0 | 18.5 | -18.5 |
| RF-01 | Four Sunman eArc SMF430F-12X12UW 430 W glass-free panels, bonded to the roof | 31.2 | 29.2 | 0 | 2.0 | 90 | -58.8 |
| G-11 | WARN VRX 25-S 12 V winch with synthetic rope, and two quick-release plates | 10.5 | 0 | 1.8 | 8.7 | 9 | +1.5 |
| Total | | 453.5 | 294.7 | 39.4 | 119.4 | 737.5 | -284.0 |

The lines total 737.5 kg in `trailer.yaml` today, all estimates, so they carry 147.5 kg of growth allowance (report 02, MASS-06). With these products they carry 26.6 kg (20 % of 119.4 kg plus 7 % of 39.4 kg). Mass with growth therefore falls by about 405 kg: 284 kg of base mass and 121 kg of allowance.

Three of the choices change what the trailer does. The owner should confirm them (open questions 1 to 3):

- A washer with no dryer. The only washer-dryer found with Australian support, the Whirlpool WWPB8502IW, weighs 66 kg ([Whirlpool sheet](https://hndgwww2.blob.core.windows.net/hnau/Whirlpool_WWPB8502IW_Spec-Sheet.pdf)).
- No LPG. Two 9 kg steel cylinders and a regulator would add about 19.5 kg of tare and 17 kg of gas (section 3).
- 10.24 kWh of battery in place of 12 kWh. A third battery (15.36 kWh) adds 37 kg (section 2).

With all three reversed the lines total 560.0 kg. That is still 177.5 kg under today's figure, and the allowance is about 30.5 kg.

Effect on the towball, approximately: at today's axle position (X 5,013) these changes take about 16 kg off the towball at tare and about 10 kg fully loaded. The kitchen, well ahead of the axle, loses 29 kg and does most of it. The lighter battery, generator and gas behind the axle push the other way. I took moments about the axle with each line's block centre. The axle solve in `cad/trailer.py` moves the axle to restore the 221 kg target. The roof loses 59 kg, which lowers the centre of gravity.

Envelope changes needed in `trailer.yaml`:

- LA-03: from 400 x 400 x 300 to 450 (X) x 525 (Y) x 300 mm for the heater itself. Truma's installation space is 540 x 500 x 350 mm ([Truma Australia](https://www.truma.com/au/products/heating-systems-au/combi-heaters-au/combi-d-6/)). With 450 along X the unit clears the ladder landing (LA-K2 ends at X 4,475) by 10 mm. The XT Air supply (RG-04) on top rises 50 mm if Truma's 350 mm installation height is kept.
- LA-04: depth from 135 to 160 mm. The MultiPlus-II is 149 mm deep ([Victron datasheet](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf)), plus the board.
- LA-10: Y from 600 to 630 mm. The Saphir is 628 mm long ([Truma Australia](https://www.truma.com/au/products/air-conditioning-systems-au/saphir-box/saphir-comfort-rc/)).
- RF-01: four panels of 2,054 x 1,084 x 2 mm in place of 1,722 x 1,134 x 30 mm. The array is 4,108 x 2,168 mm. Its top sits about 45 mm lower, so the travel height falls from 2,759 mm (TRAILER.md) to about 2,714 mm.
- G-11: the winch length from 300 to 335 mm. WARN gives 13.1 inches ([WARN](https://www.warn.com/products/vrx-25-s-winch-101020)).
- UF-01 and UF-04 keep their blocks. The two batteries lie on their sides inside the battery box.
- If LPG goes, the gas locker (G-15, 7 kg estimate in `garage-bed/BOM.md`) and its hatch (BD-06, 4 kg estimate) go too. That frees the kerb-side rear corner of the garage.

Every other chosen product fits its present box.

Mass found outside these lines:

- The heater needs diesel. A 15 L tank holds 12.6 kg of fuel (0.84 kg per litre). It needs a payload line with load `fuel` (open question 6).
- The ARK XO750 jockey wheel weighs about 20 kg against 9 kg in the chassis, and an ARK XO DDS650 corner steady about 8.8 kg against 5.5 kg. Together that is about +24 kg (section 6).

What blocks the fit-out:

1. No recirculating shower has an Australian stockist or service agent. The DauerShower is the pick. It has to be imported, with a normal mixer as a bypass (LA-01).
2. The heater box must grow, and it then clears the ladder landing by only 10 mm (LA-03).
3. The three owner decisions above.

The other chosen products have Australian distributors. I did not check Australian stockists for the Accuride slides, the WARN winch or the CFX3 55IM model itself.

## 1. Products per line

Sections 2 to 5 cover the battery (UF-04), the LPG lines (GS-02, GS-05), the solar panels (RF-01) and the water tanks (UF-01). This section covers the rest.

### LA-01 Wet bathroom, 1 x 1 m

The box is 1,000 x 1,000 x 1,800 mm in the road-side corner against partition A. The cassette leaves through a service door in the road-side wall.

Toilet:

| Candidate | Mass | Size H x W x D | Power and capacity | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| Thetford C223-CS, swivel bowl, electric flush (chosen) | 7.2 kg, maker ([Thetford Australia](https://www.thetford.com/au/products-and-support/c223cs/)) | 534 x 394 x 580 mm | 12 V flush pump, 18 L cassette | Thetford Australia and its caravan dealers | Supported by Thetford Australia. Needs Thetford service door 2680584 ([Thetford Australia](https://www.thetford.com/au/products-and-support/c223cs/)) |
| Dometic CTS 4110, ceramic inlay | 12 kg, retailer ([The Campervan Shop](https://www.thecampervanshop.com/dometic-cts-4110-cassette-toilet-19l/)). Dometic's Dutch page shows 11 kg and a fraction ([Dometic](https://www.dometic.com/nl-nl/product/dometic-cts-4110-9107100630)) | 672 x 382 x 530 mm | 12 V, 19 L cassette | Not checked | The ceramic inlay resists scratches. About 5 kg heavier |

Recirculating shower. It captures the shower water, filters and disinfects it, reheats it and pumps it back to the rose, then drains to grey water at the end.

| Candidate | Mass | Size | Power and water | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| DauerShower 2.0 (chosen) | Under 10 kg, maker ([DauerShower](https://dauershower.com/), earlier page version) | Needs at most 450 W x 200 D x 420 H mm ([DauerShower](https://dauershower.com/), earlier page version) | About 5 L of fresh water and 0.15 kWh per shower ([DauerShower](https://dauershower.com/)). The maker's English FAQ says about 25 Ah at 12 V (0.3 kWh) for a 10-minute hot shower | None. Sold by WOMO Parts ([womo-parts.de](https://womo-parts.de/product/dauershower-2-0-endlos-duschen-mit-minimalem-wasserverbrauch/)) and CamperTobi, EUR 2,610 ([campertobi.de](https://campertobi.de/produkt/dauershower-die-unendliche-dusche-sparsam-duschen-im-camper/)) | An owner on the maker's site reports daily use since 2023. Stainless filter that backflushes itself and a UV-C LED. The maker recommends a normal mixer as a bypass ([DauerShower](https://dauershower.com/)) |
| Infinity Shower | Not published | Core 254 x 343 x 133 mm, filter and UV unit 368 x 206 mm ([Infinity Shower](https://theinfinityshower.com/shop)) | 120 W at 12 V. Needs a tank water heater of at least 4 US gallons, 15 L ([FAQ](https://theinfinityshower.com/faqs)) | None (USA, USD 5,500) | The Truma's 10 L boiler is below its stated minimum |
| Showerloop | About 20 kg as a DIY build ([Instructables](https://www.instructables.com/Showerloop/)) | | | None | Still in development ([Showerloop](https://showerloop.com/)) |

The DauerShower unit sits between the shower drain and the grey-water outlet ([DauerShower](https://dauershower.com/)). It goes beside the toilet base or under the tray step.

Mass of the line:

| Part | Mass (kg) | Basis |
|---|---|---|
| Thetford C223-CS | 7.2 | Maker |
| DauerShower 2.0 kit | 10.0 | Maker states under 10 kg |
| Floor pan, GRP, 1,000 x 1,000 mm with 60 mm upstands and a drain | 7.5 | Estimate: 1.24 m2 of 3 to 4 mm glass-reinforced plastic at 1.8 g/cm3. A custom pan fits the 1 x 1 m wet room better than a stock domestic tray |
| Bypass mixer and hand shower | 1.5 | Estimate |
| Two walls of 20 mm honeycomb, less the door opening, 2.58 m2 at 3.3 kg/m2 | 8.5 | Estimate at the honeycomb rate in `garage-bed/BOM.md` (B-03, P-01) |
| Door, 0.6 x 1.7 m of the same panel, with hinges, latch and seal | 4.4 | Estimate |
| Wet lining on the body wall, partition A and ceiling, 4.6 m2 of 1.5 mm GRP sheet at 1.5 kg/m2 | 6.9 | Estimate |
| Edge trims, 15 m of 25 x 25 x 1.6 aluminium angle at 0.209 kg/m | 3.1 | Estimate of the length, rate from `garage-bed/BOM.md` (P-02) |
| Fold-down basin and tap | 2.5 | Estimate |
| Thetford cassette service door | 1.5 | Estimate |
| Shelf, rails, mirror, drain fittings, hoses and sealant | 4.0 | Estimate |
| Total | 57.1 | 17.2 maker, 39.9 estimate |

Change: -42.9 kg against 100 kg.

### LA-02 Washer-dryer

The box is 600 x 600 x 850 mm against partition A, with the inverter board above it from 1,100 mm.

| Candidate | Mass | Size W x D x H | Power and water | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| Camec 3.5 kg top load, 051879 (chosen) | 16 kg, maker ([Camec brochure](https://www.mygenerator.com.au/assets/files/Camec_053344_Product_Brochure.pdf)) | 445 x 460 x 730 mm | 280 W, 220 to 240 V. 44 L per wash. 800 rpm spin | Camec branches in VIC, NSW, QLD and WA | Camec says its washers are designed for Australian conditions and RV installation. Simple top loader with no heater |
| Camec 2.5 kg wall mount front load, 053224 | 21 kg, maker (same brochure) | 557 x 373 x 618 mm | 1,300 W with a heated wash. 32 L per wash | Camec | Front door, so no lid clearance needed |
| Whirlpool WWPB8502IW slim washer-dryer, 8 kg wash, 4.5 kg dry | 66 kg, maker ([sheet](https://hndgwww2.blob.core.windows.net/hnau/Whirlpool_WWPB8502IW_Spec-Sheet.pdf)) | 595 x 475 x 820 mm | 1,750 W. Its energy label gives 171 kWh a year for one dry a week, about 3.3 kWh per dry | Arisit Pty Ltd, Dandenong South VIC | A household machine. Its sheet says nothing about use in a vehicle |
| Splendide WD2100XC washer-dryer | 148 lb, 67 kg, maker ([manual](https://myrvworks.com/wp-content/uploads/2019/04/2100XC-Combo-User-Manual.pdf)) | 595 x 559 x 845 to 857 mm | 120 V, 60 Hz, 10.5 A only | None | Built for American RVs, but it cannot run on Australian 230 V |

Choice: the Camec 3.5 kg top loader. It is the lightest machine built for RVs with Australian support, and it barely touches the battery. Drying goes on a line under the awning or in the bathroom with a heater outlet (open question 1). The lid hinges at the back and stands about 1,190 mm above the floor when open, while the inverter board starts at 1,100 mm over the back 160 mm. So keep the machine's back at least 160 mm off partition A, which the 600 mm deep box allows, or mount the MultiPlus at the top of its box.

Change: -49.0 kg against 65 kg.

### LA-03 Diesel heater and hot water unit

| Candidate | Mass | Size L x W x H | Output and fuel | Power | Australian stockist | Reliability and service |
|---|---|---|---|---|---|---|
| Truma Combi D 6, Australian version (chosen) | About 15.8 kg, maker ([Truma Australia](https://www.truma.com/au/products/heating-systems-au/combi-heaters-au/combi-d-6/)). 17.2 kg with peripheral devices in the Australian manual ([manual](https://cdn.shopify.com/s/files/1/0093/4877/6032/files/Combi-D-Operating-Instructions.pdf?1165)) | 525 x 450 x 300 mm. Installation space 540 x 500 x 350 mm | 2, 4 or 6 kW. 220 to 630 ml/h, and 110 ml/h at an average 1 kW. 10 L stainless boiler | 1.8 to 4 A at 12 V | Truma Australia | Truma Australia lists and services the diesel D 6 ([range](https://www.truma.com/au/product-category/heating-systems-au/)). Its Australian manual dates from 2009, so the model has been sold here for years ([manual](https://cdn.shopify.com/s/files/1/0093/4877/6032/files/Combi-D-Operating-Instructions.pdf?1165)) |
| Truma Combi D 4 E, next generation | 15.6 kg, maker ([Truma](https://www.truma.com/products/heating-systems/combi/combi-d-4-e-next-generation/)) | 510 x 450 x 300 mm | 4 kW. 0.1 to 0.4 L/h. Electric elements of 900 or 1,800 W at 230 V | 0.4 to 8.1 A at 12 V | Not on Truma Australia's list | The 230 V elements could use surplus solar in summer |
| Webasto Dual Top Evo 6 | 20 kg, retailer ([Barna Campers](https://barnacampers.com/calefaccion-dual-top-evo-6-digital.html)) | 530 x 352 x 256 mm | 1.5 to 6 kW. 0.19 to 0.66 L/h. 11 L boiler | 15 to 65 W at 12 V | CaravansPlus is a Webasto distributor ([CaravansPlus](https://www.caravansplus.com.au/brand/webasto/)) | Webasto has an Australian subsidiary ([CaravansPlus guide](https://www.caravansplus.com.au/pdf/AT2000STC-Air-Top-Installation-Guide.pdf)). 4 kg heavier |

Choice: the Truma Combi D 6. Truma Australia supports it and it is the lightest Australian option. At -5 °C outside the living area loses roughly 1.5 kW (estimate: about 30 m2 of 35 mm foam wall at 0.8 W/m2K, 2 m2 of windows at 3 W/m2K, the raised roof's skirt and one air change an hour). So 6 kW is ample and the unit will mostly run on its 2 kW step.

None of the candidates fits the 400 x 400 x 300 mm box. The new box is 450 (X) x 525 (Y) x 300 mm, with 10 mm to the ladder landing.

Mass: 17.2 kg (maker, with peripherals) plus 4.5 kg of estimates: four 65 mm warm-air ducts and outlets 1.2 kg, flue and air intake kit 1.0 kg, a 15 L HDPE fuel tank 2.0 kg, fuel line and filter 0.3 kg. Total 21.7 kg, a change of -8.3 kg against 30 kg. The fuel itself is payload (open question 6).

### LA-04 Inverter and chargers, on partition A

The board follows from the energy system in section 2. The box is 800 wide and 700 high above the washer and heater.

| Part | Maker, part | Mass (kg) | Basis | Size H x W x D (mm) |
|---|---|---|---|---|
| Inverter-charger | Victron MultiPlus-II 24/5000/120-50 | 30.0 | Maker ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf)) | 607 x 330 x 149 |
| Solar charge controllers, two | Victron SmartSolar MPPT 150/45 | 2.5 | Maker, 1.25 kg each ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-SmartSolar-charge-controller-MPPT-150-35-%26-150-45-EN.pdf)) | 130 x 186 x 70 each |
| DC-DC charger from the car | Victron Orion-Tr Smart 12/24-15 isolated | 1.8 | Maker ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-Smart-DC-DC-chargers-isolated-250-400W-EN.pdf)) | 131 x 187 x 86 |
| 12 V supply for 12 V loads | Victron Orion 24/12-70, 840 W | 1.5 | Retailer, 3.24 lb ([Current Connected](https://www.currentconnected.com/product/orion-ip20-24-12-70a-converter)) | 65 x 88 x 195 |
| Battery management and main contactor | Victron Lynx Smart BMS NG 500 A | 1.9 | Maker ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-Lynx-Smart-BMS-NG-EN.pdf)) | 190 x 180 x 80 |
| DC distribution | Victron Lynx Distributor | 1.5 | Estimate | about 190 x 180 x 80 |
| Monitoring | Victron Cerbo GX and GX Touch 50 | 0.6 | Estimate. Sizes are maker ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-Cerbo-GX-GX-Touch-EN-.pdf)) | 78 x 154 x 48 |
| Fuses and holders | | 0.8 | Estimate | |
| Mounting board, 800 x 700 mm | | 2.5 | Estimate | |
| Wiring on the board | | 2.5 | Estimate | |
| Total | | 45.6 | 37.7 maker or retailer, 7.9 estimate | |

The MultiPlus fills one side of the board and two columns of the smaller units fill the other, so the parts fit in 800 x 700 mm. The depth grows to 160 mm. Everything stays on the living side of partition A and above the garage's 500 mm ignition-free zone (GAR-03).

Change: -14.4 kg against 60 kg.

Lighter and heavier alternatives for the inverter alone:

| Candidate | Continuous output | Mass | Note |
|---|---|---|---|
| MultiPlus-II 24/5000/120-50 (chosen) | 4,000 W at 25 °C, 3,700 W at 40 °C, peak 9,000 W | 30 kg | Runs the hob, the air-conditioner and the washer together |
| MultiPlus-II 24/3000/70-32 | 2,400 W at 25 °C, 2,200 W at 40 °C | 19 kg | 11 kg lighter, but the air-conditioner has to stop while the hob runs |
| MultiPlus-II 12/5000/220-50 | 4,000 W | 33 kg | For a 12 V system |

All three figures are from the [MultiPlus-II datasheet](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf).

### LA-05 Fridge

The box is 600 x 600 x 1,400 mm.

| Candidate | Mass | Size W x H x D | Volume and energy | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| Dometic NRX 130C (chosen) | 28 kg, maker ([Dometic Australia](https://www.dometic.com/en-au/product/dometic-nrx-130c-9620001867)) | 525 x 812 x 568 mm | 126 L. 12/24 V DC ([retailer](https://nomadicsupply.com/dometic-nrx-130c-4-6-cu-ft-dark-silver-refrigerator-9620017097/)) or 100 to 240 V AC at 70 W. Climate class T. Energy not published | Dometic Australia, RRP AUD 1,649 ([NRX range](https://www.dometic.com/en-au/lp/nrx-refrigerators)) | Dometic's national service network. Removable freezer box |
| Thetford T2175C | 42.3 kg, maker ([Thetford Australia](https://www.thetford.com/au/products-and-support/t2175c-compressor-refrigerator-175l/)) | 544 x 1,256 x 613 mm | 174 L. 0.56 kWh a day. 12 V | Thetford Australia | 613 mm deep, so the box grows 13 mm |
| Bushman DC190L-X | 53 kg, maker ([Bushman](https://bushman.com.au/buying-guides/find-the-12v-upright-caravan-fridge-that-fits-your-cavity-cut-out/)) | 600 x 1,380 x 595 mm | 190 L with a 45 L freezer. Secop BD80 compressor. Rated to 43 °C | Bushman, Australian | Secop (Danfoss) BD80 compressor with a 7-year compressor warranty ([Bushman](https://bushman.com.au/buying-guides/find-the-12v-upright-caravan-fridge-that-fits-your-cavity-cut-out/)). 25 kg heavier |

Choice: the NRX 130C. It runs straight from the 24 V battery, and with a separate freezer 126 L is enough for two people. It leaves about 590 mm above it in the box for a cupboard. Mass 28 kg plus 1 kg (estimate) for its frame and latch.

Change: -6.0 kg against 35 kg.

### LA-06 Chest freezer

The box is 550 (X) x 800 (Y) x 850 mm.

| Candidate | Mass | Size W x D x H | Volume and power | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| Dometic CFX3 55IM (chosen) | 21.3 kg, retailer ([Overland Garage](https://overlandgarage.ca/products/dometic-cfx3-55im-cooler-freezer-with-rapid-freeze-plate), [OK4WD](https://ok4wd.com/dometic-cfx3-55im-cooler-freezer-w-rapid-freeze-plate/)) | 720 x 455 x 480 mm | 53 L. Dometic says the CFX3 range cools to -22 °C ([Dometic](https://www.dometic.com/en-us/product/dometic-cfx3-25-9600028370)). 12/24 V DC | Dometic Australia sells the CFX3 range | Built for vehicle use, with a variable-speed compressor ([Dometic](https://www.dometic.com/en-us/product/dometic-cfx3-25-9600028370)) |
| Dometic CFX3 75DZ, dual zone | 27.8 kg, retailer ([Overland Garage](https://overlandgarage.ca/products/dometic-cfx3-75dz-dual-cooler-freezer)) | 892 x 495 x 472 mm ([Dometic information sheet](https://www.moory.se/wp-content/uploads/dometic-cfx3-75dz_9600025332_79460.pdf)) | 75 L in two zones | Dometic Australia | The box grows to 900 mm in Y |
| Engel MT-V80F | 39 kg, maker ([Engel product card](https://www.mygenerator.com.au/assets/images/resource/pdf/Engel_MT-V80F_Product_Card.pdf)) | 790 x 490 x 561 mm | 80 L. 0.5 to 4.2 A at 12 V. 12 V, 24 V and 240 V | Engel, Australia-wide service network | Sawafuji swing motor with one moving part, made for corrugated roads. 18 kg heavier |

Choice: the CFX3 55IM, the lightest with a hard-use record and Australian support. Its lid needs about 455 mm of clear height above the freezer, so the bench over it must lift (480 + 455 = 935 mm against the 850 mm box). Mass 21.3 kg plus a 0.5 kg tie-down kit (estimate).

Change: -8.2 kg against 30 kg.

### LA-07 Outdoor kitchen slide-out, kerb side

The box is 1,500 (X) x 600 (Y) x 450 mm at 50 mm above the floor. It slides out 600 mm across the trailer through the kerb-side wall.

Bought parts:

| Part | Chosen | Mass | Basis | Size | Power or rating |
|---|---|---|---|---|---|
| Hob | Dometic CVI1525 two-zone induction | 7.0 kg | Maker ([Dometic](https://www.dometic.com/fr-fr/produit/dometic-cvi1525-9600050571)) | 525 x 350 x 55 mm, cut-out 505 x 330 mm | 1,000 W and 1,300 W zones, 2,300 W and 10 A in all, 220 to 240 V. Dometic publishes an APAC manual ([manual](https://media.dometic.com/externalassets/cvi1525_9620008712_125117.pdf?ref=-588583111)) and Mars Campers fits it in Australia ([Mars Campers](https://helpcentre.marscampers.com.au/portal/en/kb/articles/dometic-cvi1525-induction-cooktop-how-to-use-safety-cleaning-troubleshooting)) |
| Sink | Dometic CVS1350G square sink with glass lid | 2.5 kg | Maker ([Dometic](https://www.dometic.com/fr-fr/produit/dometic-cvs1350g-9600051161)) | 350 x 350 x 170 mm | Same Cooking Vision series as the hob |
| Slides | Accuride 9301 full-extension, 610 mm (24 inch), one pair | 6.0 kg | Estimate from the section: three steel members of about 2.3 mm on a 76 mm height | 76 mm high | 272 kg a pair in moderate use ([Accuride sheet](https://stage.dbroberts.com/cms/wp-content/uploads/sites/2/2022/06/Accuride_9301_Technical_Sheet.pdf)), 360 lb (163 kg) for mobile use ([Accuride](https://www.accuride.com/en-us/products/drawer-slides/heavy-duty-slides/9300-drawer-slide-series)) |
| Tap | Caravan mixer, for example the Reich Linnea K ([Jacksons Leisure](https://www.jacksonsleisure.com/caravan-campervan-motorhome/reich-linnea-33mm-mixer-tap-for-campervan-caravan-motorhome-marine/)) | 0.8 kg | Estimate | | |

Alternatives: the Camec 053574 induction hob (2,300 W, two zones, Australian) has no published mass ([manual listing](https://www.manualslib.com/manual/3393528/Camec-053574.html)). The gas option would be the Dometic PI8023 three-burner LPG hob with glass lid ([Mars Campers](https://helpcentre.marscampers.com.au/portal/en/kb/articles/dometic-pi8023-how-to-use-clean-troubleshoot-3-burner-gas-cooktop-with-glass-lid)), but section 3 drops LPG.

Fabricated rest, all estimates:

| Part | Mass (kg) | Basis |
|---|---|---|
| Fixed sleeve the drawer runs in: base, ends and back in 1.6 mm aluminium (2.1 m2 at 4.3 kg/m2) and an angle frame | 12.0 | Estimate |
| Slide-out drawer: 2 mm aluminium base, 1.6 mm sides and back, the 35 mm sandwich outer panel that closes the wall opening, its seal and latches, and an internal frame | 14.1 | Estimate |
| Bench top over the drawer, 0.9 m2 at 5 kg/m2 | 4.5 | Estimate |
| Internal drawers and utensil trays | 3.0 | Estimate |
| Stops and a positive lock in both positions | 1.0 | Estimate |
| Total | 34.6 | |

Line total 50.9 kg: 9.5 kg maker and 41.4 kg estimate. Change: -29.1 kg against 80 kg.

### LA-10 Air-conditioner, under the desk

The box is 400 (X) x 600 (Y) x 300 mm under the desk in the road-side front corner.

| Candidate | Mass | Size L x W x H | Cooling and power | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| Truma Saphir Comfort RC (chosen) | About 23.5 kg, maker ([Truma Australia](https://www.truma.com/au/products/air-conditioning-systems-au/saphir-box/saphir-comfort-rc/)) | 628 x 400 x 290 mm | 2,400 W cooling, 1,700 W heating. 230 to 240 V, 4.2 A cooling, 20 A for 150 ms at start. Works from +4 to +43 °C | Truma Australia | Truma's under-bench unit, serviced by Truma Australia |
| Dometic FreshWell 3000 | About 21 kg, retailer ([SVB](https://www.svb24.com/en/dometic-freshwell-3000-under-bench-air-conditioner.html)) | 628 x 400 x 286 mm | 2,700 W cooling at 990 W input. Heat pump 3,000 W. 4.3 A. Soft start | No Australian listing found | European under-bench unit |
| Velit 2000U, DC | Not found | Not checked | 24 V model: 9,000 BTU (2.6 kW), 750 W rated, 10 to 33 A ([Sandy Vans](https://sandyvans.com/products/velit-2000u-12v-24v-48v-under-bench-off-grid-air-conditioner)) | None. Stocked in the USA, Canada and the UK ([Velit](https://velitcamping.com/products/velit-2000u-under-bench-air-conditioner-12v-24v)) | Runs straight from the battery with no inverter |

Houghton, the Australian air-conditioner maker, lists only roof units ([Houghton](https://houghtonleisure.com/products/h3600v/)).

Choice: the Saphir Comfort RC, because Truma Australia supports it. The box grows to 630 mm in Y, which the desk above (1,000 mm in Y) allows. Mass 23.5 kg plus 1.5 kg of ducts and vents (estimate). Change: -5.0 kg against 30 kg.

### GS-01 Generator

The envelope is 520 x 320 x 460 mm in the kerb strip, strapped to the track.

| Candidate | Mass | Size L x W x H | Output and fuel | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| Honda EU22i (chosen) | 21.1 kg dry, maker ([Honda Australia](https://powerequipment.honda.com.au/models/generators/eu22/specifications)) | 509 x 290 x 425 mm | 2,200 VA peak, 1,800 W rated ([spec sheet](https://anythingmarketplace.com.au/wp-content/uploads/2026/09/Honda-EU22i-Spec-Sheet.pdf)). 3.6 L tank. About 1.09 L/h at rated load ([Peter Hill Power](https://peterhillpower.com.au/product/honda-power-equipment-generators-2/)) | Honda Power Equipment dealers across Australia | Honda Australia sells and services it through its dealer network ([Honda Australia](https://powerequipment.honda.com.au/models/generators/eu22)) |
| Yamaha EF2200iS | 25 kg, maker ([Yamaha factsheet](https://cdn2.yamaha-motor.eu/prod/product-assets/2020/EF2200IS/Factsheets/2020-EF2200IS_en.pdf)) | Not checked | 2,200 W peak, 1,800 W rated ([RV Daily](https://rvdaily.com.au/review-yamaha-ef2200is-inverter-generator/)) | Yamaha dealers | 4 kg heavier |

Choice: the Honda EU22i. Section 2 confirms the size. Change: -18.9 kg against 40 kg.

### G-11 Loading winch

The winch pulls the Tuareg (206 kg) up the 3,048 mm ramp at 16.6 degrees. With 2 % rolling resistance that needs about 616 N, or 63 kgf (calculated: 206 x 9.81 x (sin 16.6 + 0.02 cos 16.6)).

| Candidate | Mass | Size | Rating and current | Australian stockist | Reliability and service |
|---|---|---|---|---|---|
| WARN VRX 25-S, part 101020 (chosen) | Not published. Shipping weight 23.46 lb, 10.6 kg ([JEGS](https://www.jegs.com/i/warn-940-101020-101020-vrx-25-s-powersports-winch-with-synthetic-rope)). Estimate 8 kg for the winch | 13.1 x 4.7 x 4.7 in, 333 x 119 x 119 mm ([WARN](https://www.warn.com/products/vrx-25-s-winch-101020)) | 2,500 lb (1,134 kg). 12 V. IP68. 15 m of 4.8 mm synthetic rope. 20 A with no load and 45 A at 227 kg ([sell sheet](https://alltracks.eu/wp-content/uploads/2023/03/VRX-25-SellSheet.pdf)), so about 27 A for this pull | Not checked | WARN's all-metal ATV winch with a lifetime mechanical warranty |
| Superwinch Terra 2500SR | Listed as 24 (lb), about 10.9 kg, likely shipping ([Superwinch](https://www.superwinch.com/products/terra-2500sr-winch-synthetic-rope-12v-1125270)) | Not checked | 2,500 lb. 1.5 hp, 12 V. 12.2 m of 4.76 mm synthetic rope | Not checked | |
| ARK 4,500 lb winch | 11.5 kg, maker ([ARK FAQ](https://www.arkcorp.com.au/faq/)) | 327 x 128 x 122 mm | 4,500 lb | ARK, Australian | Heavier and more than needed |

Choice: the VRX 25-S. Line mass 10.5 kg: the winch 8.0 kg (estimate), two 340 x 160 x 6 mm aluminium plates 1.8 kg (calculated at 2.70 g/cm3), and cable and remote 0.7 kg (estimate). Change: +1.5 kg against 9 kg. The 9 kg allowance left out the plates. The winch runs from the 12 V bus (section 2).

## 2. Energy system, planning basis

This is the planning basis for the later power design. Numbers marked as assumptions are mine. Each has its basis.

### Daily load

A hot day is 38 °C, near the 36.6 °C January mean maximum at Alice Springs ([BoM](https://www.bom.gov.au/climate/averages/tables/cw_015590.shtml)). A cold day is about 13 °C by day and 0 °C at night, as Canberra in July (12.9 °C mean maximum, 0.1 °C mean minimum, [BoM](https://www.bom.gov.au/climate/averages/tables/cw_070351.shtml)). Two people live aboard.

| Load | Hot day (kWh) | Cold day (kWh) | Basis |
|---|---|---|---|
| Fridge, NRX 130C | 0.95 | 0.35 | Assumption: 0.55 kWh a day at 25 °C, like the Thetford T2175C's 0.56 kWh ([Thetford](https://www.thetford.com/au/products-and-support/t2175c-compressor-refrigerator-175l/)), times 1.7 on a hot day and 0.6 on a cold one |
| Freezer, CFX3 55IM at -18 °C | 0.80 | 0.30 | Assumption: about 2.5 A average at 12 V when hot, inside the Engel's 0.5 to 4.2 A range ([Engel](https://www.mygenerator.com.au/assets/images/resource/pdf/Engel_MT-V80F_Product_Card.pdf)) |
| Air-conditioner, Saphir | 5.00 | 0 | 4.2 A at 230 V is about 970 W ([Truma](https://www.truma.com/au/products/air-conditioning-systems-au/saphir-box/saphir-comfort-rc/)). Assumption: 60 % duty for 8 hours from 2 pm to 10 pm, plus 7 % inverter loss |
| Washer, Camec 3.5 kg | 0.10 | 0.10 | 280 W ([Camec](https://www.mygenerator.com.au/assets/files/Camec_053344_Product_Brochure.pdf)). Assumption: about 0.2 kWh a load, one load every two days |
| Heater and hot water, Combi D 6 | 0.05 | 0.55 | 1.8 to 4 A at 12 V running, boiler alone 1.8 A at most ([Truma](https://www.truma.com/au/products/heating-systems-au/combi-heaters-au/combi-d-6/)). Assumption: 2.5 A average for 16 hours when cold |
| Cooking, CVI1525 | 1.40 | 1.80 | Assumption: kettle twice, breakfast and a 40-minute dinner at about 1 kW, plus inverter loss. More hot drinks when cold |
| Recirculating shower, two a day | 0.60 | 0.60 | Upper maker figure of 0.3 kWh a shower ([DauerShower](https://dauershower.com/)) |
| Lights | 0.10 | 0.15 | Assumption: 20 W of LED for 5 to 7 hours |
| Laptops, phones, Starlink Mini and router | 0.80 | 0.80 | Assumption: two 45 W laptops for 4 hours and 30 W of internet for 8 hours |
| Water pump | 0.02 | 0.02 | Assumption |
| Roof fan | 0.15 | 0 | Assumption: 1.5 A at 12 V for 8 hours |
| Inverter, GX, BMS, detectors and alarms standing by | 0.45 | 0.45 | MultiPlus-II 24/5000 at 18 W no load ([Victron](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf)) for 14 hours, plus about 8 W of other standby for 24 hours (assumption) |
| Total | 10.4 | 5.1 | |

About 4 kWh of the hot-day total falls between sunset and sunrise: the evening air-conditioning, the fridge and freezer overnight, an evening shower, and the devices and lights. On the cold day it is about 2.7 kWh, because dinner and the heater fall after a 5 pm sunset.

Solar yield, assumption: 7.5 kWh/m2 a day of sun on a horizontal roof on an inland summer day, 2.5 kWh/m2 on a clear southern winter day and 1.0 kWh/m2 on an overcast one. BoM puts daily solar exposure between about 1 and 35 MJ/m2, that is 0.3 to 9.7 kWh/m2 ([BoM](https://www.bom.gov.au/climate/maps/averages/solar-exposure/metadata.shtml)). The 1,720 W array (section 4), flat and bonded, then gives about 9.3 kWh on the hot day (performance ratio 0.72 for heat, dust and wiring), 3.4 kWh on the clear cold day and 1.4 kWh on the overcast one (ratio 0.8).

| | Hot day | Clear cold day | Overcast cold day |
|---|---|---|---|
| Load (kWh) | 10.4 | 5.1 | 5.1 |
| Solar (kWh) | 9.3 | 3.4 | 1.4 |
| Shortfall (kWh) | 1.1 | 1.7 | 3.7 |

A travel day adds about 1.8 kWh from the car (one Orion-Tr Smart at 360 W for 5 hours).

### System voltage: 24 V

| | 12 V | 24 V (chosen) | 48 V |
|---|---|---|---|
| 4 kW inverter-charger | MultiPlus-II 12/5000/220-50, 33 kg | MultiPlus-II 24/5000/120-50, 30 kg | MultiPlus-II 48/5000/70-50, 30 kg ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf)) |
| Battery current at 3.8 kW | about 330 A | about 165 A | about 85 A |
| Main cable, 3 m each way, 2 % drop | 150 mm2, about 8 kg of copper | 50 mm2, about 2.7 kg | 25 mm2, about 1.3 kg (calculated) |
| Charging from the car's 12 V | Many 12 V units | Victron Orion-Tr Smart 12/24-15 ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-Smart-DC-DC-chargers-isolated-250-400W-EN.pdf)) | No Victron charger ([Victron community](https://community.victronenergy.com/t/best-way-charge-48v-batteries-with-12v-car/8212)). Sterling BBW124830, 30 A input ([12 Volt Planet](https://www.12voltplanet.co.uk/sterling-power-bbw124830-pro-batt-waterproof-battery-to-battery-charger-12v-to-48v-30a.html)) |
| 12 V loads (heater, XT Air compressor, winch, pump) | Direct | One Orion 24/12-70, 840 W | Two Orion-Tr 48/12-30 |
| Parts in a remote town | Everywhere | Truck parts are 24 V | Few |

24 V halves the current of a 12 V system, saves about 5 kg of main cable and 3 kg of inverter, and keeps a proper Victron charger from the car. Fridge, freezer and LED lights run on 24 V directly. 48 V would save another 1.4 kg of cable, but it needs a less common car charger and two converters for the 12 V loads.

### Choices

- Inverter-charger: Victron MultiPlus-II 24/5000/120-50, 4,000 W at 25 °C and 3,700 W at 40 °C, 9,000 W peak, 120 A charger ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf)). The worst evening load is the hob at 2,300 W, the air-conditioner at about 1,000 W and the washer at 280 W, about 3.6 kW plus small loads. The air-conditioner's 20 A start for 150 ms is about 4.6 kVA, well inside the 9 kVA peak. The 3 kVA model (19 kg) would force the air-conditioner off while cooking.
- DC-DC charger from the car: one Victron Orion-Tr Smart 12/24-15 isolated, 430 W at 25 °C and 360 W at 40 °C, input 8 to 17 V ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-Orion-Tr-Smart-DC-DC-chargers-isolated-250-400W-EN.pdf)). It draws about 35 A from the car, so the car needs a 6 B&S feed to an Anderson plug at the towbar. A second unit in parallel doubles the charge if the car's feed is upsized (open question 11). The Cayenne's alternator voltage varies, so wire the Orion's engine-running input to an ignition signal.
- Solar charge controllers: two Victron SmartSolar MPPT 150/45, rated 1,300 W of panels each at 24 V ([datasheet](https://www.victronenergy.com/upload/documents/Datasheet-SmartSolar-charge-controller-MPPT-150-35-%26-150-45-EN.pdf)). Each takes two 430 W panels in series. Two panels of 49.8 V Voc give 99.6 V, and about 110 V at -10 °C if the Voc coefficient is near -0.3 %/°C (assumption), under the controller's 145 V limit. One controller per pair keeps a shaded pair from dragging down the other.
- 12 V bus: one Victron Orion 24/12-70 (70 A, 840 W) for the heater, the XT Air compressor, the water pump and the winch. The winch draws about 27 A for this pull (section 1).
- Battery: two Victron Lithium NG 25.6 V 200 Ah, 10.24 kWh, with the Lynx Smart BMS NG 500 A ([NG datasheet](https://cdn.shopify.com/s/files/1/0497/4749/3026/files/Datasheet-Lithium-NG-batteries-12_8V-25_6V-51_2V-EN.pdf?v=1739576641)). Each is 235 x 648 x 162 mm and 37 kg (Victron marks the mass as an estimate), IP65, 200 A continuous, 2,500 cycles at 80 % depth of discharge. They can lie on their sides but not with the terminals down. Victron's declaration of conformity of October 2025 lists EN IEC 62619:2022 and ECE R10 for the 25.6 V 200 Ah battery ([declaration](https://www.victronenergy.com/upload/documents/Declaration-of-Conformity-Lithium-NG-Batteries.pdf)). That matters because AS/NZS 3001.2:2022 requires caravan batteries to meet AS IEC 62619 ([REDARC](https://www.redarcelectronics.com/au/discover/new-caravan-standards/)). Enerdrive's B-TEC manual says only its cells meet AS IEC 62619 ([manual](https://manuals.plus/enerdrive/b-tec-lithium-batteries-manual)), and Enerdrive's 24 V range stops at 150 Ah ([Enerdrive](https://enerdrive.com.au/product/epower-b-tec-24v-100ah-lithium-battery/)).
- Battery box: sealed 2 mm aluminium, about 600 x 800 x 250 mm, with a lid gasket, cable glands and a vent to the road side. 12 kg (estimate: 1.66 m2 at 5.4 kg/m2 plus brackets). The two batteries lie on their sides, 2 x 235 = 470 mm along X, with the terminals facing sideways so the cable lugs need no extra height. Fuse each battery in the box.

Battery candidates for the 600 x 800 x 250 mm box:

| Candidate | Energy | Mass | Size H x W x D | Ratings | Australian stockist | Reliability and service |
|---|---|---|---|---|---|---|
| Two Victron Lithium NG 25.6 V 200 Ah (chosen) | 10.24 kWh | 74 kg, maker estimate ([datasheet](https://cdn.shopify.com/s/files/1/0497/4749/3026/files/Datasheet-Lithium-NG-batteries-12_8V-25_6V-51_2V-EN.pdf?v=1739576641)) | 235 x 648 x 162 mm each | 200 A each. EN IEC 62619 declared ([declaration](https://www.victronenergy.com/upload/documents/Declaration-of-Conformity-Lithium-NG-Batteries.pdf)) | Victron distributors | Cover removable with screws, so Victron calls it repairable (datasheet) |
| Victron Lithium NG 25.6 V 300 Ah plus one 25.6 V 200 Ah | 12.8 kWh | 89 kg, maker estimate (same datasheet) | The 300 Ah is 206 x 841 x 205 mm | As above | Victron distributors | The 841 mm battery needs the box 850 mm wide in Y. I did not check that Victron allows mixed sizes in one bank |
| Enerdrive B-TEC 24 V 150 Ah, several | 3.84 kWh each | Not checked | Not checked | Its manual says the cells, not the battery, meet AS IEC 62619 ([manual](https://manuals.plus/enerdrive/b-tec-lithium-batteries-manual)) | Enerdrive, now Dometic Power Solutions ([Enerdrive](https://enerdrive.com.au/product/epower-b-tec-24v-100ah-lithium-battery/)) | Australian company. Three would be needed for 11.5 kWh |

### Is 12 kWh the right battery?

Two modules give 10.24 kWh. Used between about 95 % and 15 % that is 8.2 kWh. That holds the night with room to spare: about 4 kWh on a hot night and 2.7 kWh on a cold one. The daily shortfall then eats into it. About 4 hot days, 3 clear winter days or 1.5 overcast winter days pass before the generator has to run. After that the EU22i runs about 45 minutes on a hot day, 70 minutes on a clear winter day or 2.5 hours on an overcast one. 12 kWh would add about a day. Victron's 24 V modules come in 5.12 kWh steps, so the real choice is 10.24 or 15.36 kWh. 10.24 kWh is the planning basis, and it saves 24 kg against the line. A third module (+37 kg) is worth it only if the owner wants the air-conditioner all night. That adds about 4.6 kWh to a hot night, more than two modules hold.

The Lynx BMS stops charging below +5 °C ([NG datasheet](https://cdn.shopify.com/s/files/1/0497/4749/3026/files/Datasheet-Lithium-NG-batteries-12_8V-25_6V-51_2V-EN.pdf?v=1739576641)). The battery sits under the floor, so on winter mornings near 0 °C solar charging waits until the box warms (open question 9).

### Is the generator the right size?

Yes. The Honda EU22i's 1,800 W rated output lets the MultiPlus charge at about 1.5 kW with its AC input limit set to 7.5 A. That replaces a 3.7 kWh overcast winter shortfall in about 2.5 hours on one 3.6 L tank (1.09 L/h at rated load, [Peter Hill Power](https://peterhillpower.com.au/product/honda-power-equipment-generators-2/)). A 3 kVA generator would weigh more for little gain. Dropping the generator is possible in summer, but it is the only backup for a run of overcast winter days, so keep it.

## 3. Gas

With diesel heating and hot water, the only LPG load left is the cooktop. The fridge and freezer are compressor units.

If cooking stays on gas: about 1.1 kWh a day goes into the pots (section 2's 1.4 kWh less about 20 % for inverter and hob losses, assumption). Assuming a burner passes 42 % of its heat to the pot, that is 2.6 kWh or 9.4 MJ of gas a day, about 0.19 kg (calculated with Elgas's 441 MJ per 8.5 kg fill, [Elgas](https://www.elgas.com.au/swapngo/9kg-gas-bottle-4kg-gas-bottle-dimensions-size/)). A 9 kg cylinder then lasts about 45 days and a 4 kg one about 20 days.

| Option | Tare | Gas | Size | Note |
|---|---|---|---|---|
| Two 9 kg steel cylinders and regulator (today) | 7.8 to 10.4 kg each, about 9 kg typical ([Elgas](https://www.elgas.com.au/swapngo/9kg-gas-bottle-4kg-gas-bottle-dimensions-size/)), plus 1.5 kg regulator (estimate) | 8.5 kg each | 309 to 335 mm across, 450 to 525 mm high | About 90 days of cooking |
| One 9 kg steel cylinder | About 9 kg, plus 1.5 kg | 8.5 kg | As above | About 45 days, so enough on its own |
| One 4 kg steel cylinder | 4.5 to 6.6 kg, about 5.5 kg typical ([Elgas](https://www.elgas.com.au/swapngo/9kg-gas-bottle-4kg-gas-bottle-dimensions-size/)) | 3.7 kg | 240 to 265 mm across, 345 to 450 mm high | About 20 days |
| Lighter cylinder types | Aluminium tank cylinders exist in Europe, for example Alugas 27 L at 6.7 kg ([LPG Webshop](https://lpgwebshop.com/de/aluminium-gastankflaschen/791-nachfuellbare-multivalve-lpg-gasflasche-aus-aluminium-27l-80-fuelldeckel-alugas-travel-mate-4250959450067.html)). Composite cylinders appear on eBay Australia ([GasBank](https://www.ebay.com.au/str/lpgparts)) | | | I found no Australian approval for either. Swap-and-go exchanges take steel cylinders |
| No LPG, induction (chosen) | 0 | 0 | | |

Induction makes LPG unnecessary. Removing it saves 18.5 kg on GS-02 and GS-05, 7 kg for the gas locker (G-15) and 4 kg for its hatch (BD-06). That is 29.5 kg of tare (estimates), plus 17 kg of LPG in every loaded case. The induction hob weighs 7 kg against about 4.5 kg for a Dometic slimline gas hob ([The Campervan Shop](https://www.thecampervanshop.com/dometic-slimline-piezo-hob-lh/)), so the net saving is about 27 kg of tare. The battery carries 1.4 kWh a day more when hot and 1.8 kWh when cold, already in section 2's table. With no gas there is no gas installation to certify and no LPG detector for GAR-05. A butane cartridge stove in the gear covers a dead battery.

## 4. Solar panels

| Panel | Output | Mass | Size | Mass on the roof | Fixing | Durability |
|---|---|---|---|---|---|---|
| Jinko Tiger Neo JKM400N-54HL4-B, glass and aluminium frame (today's type) | 400 W, Voc 37.4 V | 22 kg, maker ([Jinko](https://www.jinkosolar.com/uploads/JKM400-420N-54HL4-B-F3-EN.pdf)) | 1,722 x 1,134 x 30 mm | 11.3 kg/m2 | Brackets or rails bolted or bonded to the roof | 3.2 mm tempered glass. 5,400 Pa snow and 2,400 Pa wind load ([Jinko](https://www.jinkosolar.com/uploads/JKM400-420N-54HL4-B-F3-EN.pdf)). The usual hail test is 25 mm ice at 23 m/s ([Maxeon sheet](https://enphase.com/en-gb/download/maxeon-sunpower-performance-6-ac-module-black-back-sheet-data-sheet)). On corrugations the frame-to-bracket joints are where fatigue starts |
| Sunman eArc SMF430F, glass-free with an aluminium frame | 430 W, Voc 49.6 to 49.8 V | 11.2 kg, maker ([pv magazine](https://www.pv-magazine.com/2021/10/29/sunman-unveils-430-w-glass-free-solar-module/)) | 2,125 x 1,051 x 35 mm | 5.0 kg/m2 | Brackets like a glass panel | Glass-fibre reinforced composite face. -0.38 %/°C. 25-year output warranty and 12-year product warranty ([pv magazine](https://www.pv-magazine.com/2021/10/29/sunman-unveils-430-w-glass-free-solar-module/)) |
| Sunman eArc SMF430F-12X12UW, glass-free and frameless (chosen) | 430 W. Vmp 42.0 V, Imp 10.24 A, Voc 49.8 V, Isc 10.74 A ([Battery Specialists](https://batteryspecialists.com.au/products/sunman-430-watt-earc-frameless-flexible-mono-solar-panel-featuring-mono-perc-cells-smf430f-12x12uw)) | 7.3 kg, maker ([Sunman brochure](https://www.master-instruments.com.au/files/battery_information/e_arc_doing_more_web.pdf)) | 2,054 x 1,080 to 1,084 x 2 mm | 3.3 kg/m2 installed ([Sunman brochure](https://www.master-instruments.com.au/files/battery_information/e_arc_doing_more_web.pdf)) | Bonded with no hardware. Sunman says the bonding is CEC approved to wind region D ([brochure](https://www.master-instruments.com.au/files/battery_information/e_arc_doing_more_web.pdf)) | Sunman says it passed IEC 61215 twice and lists a 35 mm hail test at 39.5 m/s (brochure). The panel flexes with the roof and has no frame joints to fatigue |

Choice: four Sunman eArc SMF430F-12X12UW panels, 1,720 W, 29.2 kg plus about 2 kg of adhesive and cable (estimate). Against four glass panels at 90 kg that saves 58.8 kg on the raising roof, which also eases the lift mechanism (BD-12). Master Instruments distributes Sunman in Australia ([Master Instruments](https://www.master-instruments.com.au/files/battery_information/sunman_earc_panels_a4_2pp.pdf)), and Battery Specialists and Solar4RVs sell it ([Solar4RVs](https://www.solar4rvs.com.au/products/sunman-earc-430w-flexible-solar-panel-1)).

The costs of bonding: a bonded panel runs hotter than one on brackets. Assuming 10 to 15 °C hotter at -0.38 %/°C, it gives 4 to 6 % less on a hot day, which section 2's 0.72 ratio includes. A damaged panel has to be cut off and a new one bonded on. The roof's top skin must be flat, clean and stiff over 4,108 x 2,168 mm and clear of hatches (open question 12). Wire the panels in two pairs, each pair in series to its own MPPT (section 2).

## 5. Water tanks

Each bay between the rails is 760 (X) x 1,086 (Y) x 259 mm (`trailer.yaml`: the floor underside less 10 mm, down to the rail underside). The owner wants 400 L in all.

| Option | Mass | Net volume | Basis | Note |
|---|---|---|---|---|
| Custom welded HDPE, 6 mm walls, two cross baffles and one lengthwise baffle (chosen) | 18.8 kg each, 37.6 kg for two | About 195 L each, 390 L for two | Calculated: 2.61 m2 of 6 mm HDPE at 0.95 g/cm3 is 14.9 kg, baffles with 20 % flow holes 3.5 kg, fittings 0.5 kg | Made to size by plastic fabricators such as Plastic Online ([Plastic Online](https://www.plasticonline.com.au/services/plastic-tank-fabrication/)). Use food-grade sheet. 5 mm walls would give about 396 L |
| Off-the-shelf rotomoulded tank, one per bay, Caravan and RV Tanks CRV0096 | Not published, about 8 kg each (estimate) | 96 L each, 192 L for two | Retailer size 1,010 x 660 x 175 mm ([Caravan and RV Tanks](https://www.caravanandrvtanks.com.au/collections/caravan-rv-tanks)) | Australian made. Only one fits each bay, so it falls just short of the 200 L travel case and far short of 400 L |
| Custom 316 stainless, 1.2 mm with 1.0 mm baffles | About 29 kg each | About 210 L each | Calculated at 7.9 g/cm3 | Heavier, and welds can crack on corrugations |

Choice: the welded HDPE tanks, 37.6 kg calculated. Change: -2.4 kg against 40 kg, and the line moves from estimate to calculated, so its allowance falls from 8 kg to 2.6 kg.

Mounting: each tank sits on two aluminium angle cross-bearers bolted to the XT crossmembers, on 10 mm rubber strips. Two stainless straps (40 x 1.5 mm, padded) hold each tank down to the bearers. The tank never hangs from the floor panel. Fill, breather and outlet fittings go on the top and the kerb side, and a drain at the lowest corner. The baffles stop slosh in braking and stiffen the 760 x 1,086 mm faces.

Guarding: UF-03 carries 20 kg for one plate across both bays, 1.61 x 1.19 m (1.91 m2). In 4 mm 5083 aluminium that is 20.5 kg, and in 10 mm UHMW polyethylene 17.8 kg (calculated at 2.68 and 0.93 g/cm3). The polyethylene plate slides over rocks and does not dent, and the aluminium one is stiffer between supports. Either fits the present line.

Water use for scale: two recirculated showers use about 10 L a day (DauerShower). A wash uses 44 L (Camec). With about 20 L a day for drinking, cooking, dishes and flushing, 390 L lasts about a week.

## 6. Published masses for the running gear and drawbar parts

| Part | Mass in the model | Published figure | Source | What to use |
|---|---|---|---|---|
| Cruisemaster XT Freestyle Air tandem kit | 180 kg (estimate) | DIY Caravans lists 180 kg for the air tandem kit and also for the coil tandem kit | [Air kit](https://www.diycaravans.com.au/shop/cruisemaster-xt-freestyle-air-suspension-kit-tandem/), [coil kit](https://www.diycaravans.com.au/shop/cruisemaster-xt-freestyle-coil-suspension-kit-tandem/) | The same figure for both suggests a shipping entry, not a weighed kit. Cruisemaster's XT Air sheet gives no mass ([CIS-006](https://roustaboutsrvclub.com.au/wp-content/uploads/2018/04/Cruisemaster-XT-AIR-Independent-Suspension.pdf)). Keep 180 kg as an estimate |
| Cruisemaster DO35 V3Plus | 9.5 kg (estimate) | DIY Caravans lists 5 kg | [DIY Caravans](https://www.diycaravans.com.au/shop/cruisemaster-do35-v3plus/) | The same shop's suspension figures look like shipping entries, and the chassis notes say other retailers list 8 to 10 kg. Keep 9.5 kg |
| ARK XO750 jockey wheel | 9.0 kg (estimate) | 43.6 lb, 19.8 kg, for the XO750 with dual wheels. ARK's FAQ says the bar weighs twice a standard jockey bar and gives 20 kg | [Croft Trailer](https://www.crofttrailer.com/xo750-swivel-sidewind-trailer-jack-with-dual-wheels-1-650-lb/), [ARK FAQ](https://www.arkcorp.com.au/faq/) | Use 20 kg, +11 kg |
| ARK XO DDS650 corner steady | 5.5 kg each, four (estimate) | 38.9 lb, 17.6 kg, for a set of two with the winding handle | [Amazon](https://www.amazon.com/ARK-XODDS650BUS-Corner-Steadies-650mm/dp/B0CLBPBNTB) | Use 8.8 kg each, +13.2 kg for four |

Together the jockey wheel and steadies add about 24 kg to the chassis lines.

## Open questions

Each ends with the assumption the designer should use.

1. Does the owner need a tumble dryer? A real washer-dryer weighs 66 kg and uses about 3.3 kWh a load. Assumption: washer only (Camec 3.5 kg), drying on a line or in the bathroom with heater air.
2. Is LPG wanted for anything, for example an outdoor barbecue? Assumption: no LPG, induction cooking, a butane cartridge stove in the gear, and the gas locker and its hatch removed.
3. Does the owner want the air-conditioner all night? Assumption: no, evening only, so two batteries (10.24 kWh). If yes, three (15.36 kWh, +37 kg).
4. The DauerShower has no Australian supplier. Assumption: import it, fit a normal mixer as the bypass, and carry a spare filter and UV-C LED.
5. The heater box grows to 450 x 525 x 300 mm and clears the ladder landing by 10 mm. Assumption: keep it at partition A with 450 along X, put Truma's water and drain connections on the walkway side, and raise the XT Air supply 50 mm.
6. Where does the heater's diesel come from? Assumption: a 15 L tank between the rails in the bay ahead of the front water tank, checked against the plan bracing there, with 12.6 kg of diesel added as a payload line with load `fuel`.
7. NRX 130C energy use is not published. Assumption: 0.55 kWh a day at 25 °C, as the similar Thetford T2175C.
8. The freezer's energy at -18 °C is not published. Assumption: 0.8 kWh on a hot day and 0.3 kWh on a cold one.
9. The battery sits under the floor and the BMS stops charging below +5 °C. Assumption: line the battery box with 20 mm closed-cell foam and fit a 30 W pad heater run from the battery when the box is below 5 °C. That uses about 0.2 kWh on a cold morning, which section 2's cold-day total does not yet include.
10. The model has no grey-water tank, and the shower and sinks need one or a drain hose. Assumption: drain through a hose to a portable container outside the mass schedule, until the owner asks for a fixed tank.
11. How much current can the car supply at the towbar? Assumption: one Orion-Tr Smart 12/24-15 on a 6 B&S feed (about 35 A). Two units need a 2 B&S feed from the car's battery.
12. The raising roof's top skin must take bonded panels over 4,108 x 2,168 mm. Assumption: a flat GRP skin free of hatches in that area, bonded with Sunman's specified adhesive.
13. The kitchen bench sits about 1,370 mm above the ground (floor 869 + 50 + 450 mm), high for cooking while standing outside. Assumption: keep the box and add a drop-down or folding step, to be settled in the layout.
14. The Accuride slide has no published mass. Assumption: 6 kg a pair, with a separate lock in both positions.
15. The WARN VRX 25-S net mass is not published. Assumption: 8 kg for the winch, from the 10.6 kg shipping weight.
16. Victron marks the NG battery masses as estimates. Assumption: 37 kg each until weighed.
17. The water tanks give 390 L net against the 400 L wanted. Assumption: accept 390 L, since the trailer carries 200 L fully loaded.

## Could not verify

- The DauerShower's mass and space figures come from an earlier version of the maker's page, quoted in a search result. The current page shows neither.
- The Infinity Shower's mass and the Velit 2000U's mass and size.
- The Dometic NRX 130C's energy use.
- The CFX3 55IM's mass on a Dometic page. Two retailers give 21.3 kg.
- A Dometic Australia listing for the CFX3 55IM, the FreshWell 3000 and the CTS 4110. The Dometic Australia product pages I tried returned errors.
- The Whirlpool washer-dryer's suitability for travel, and transit locks on the Camec washers.
- Whether Truma Australia sells the next-generation Combi D 6 E. Its site lists the Combi D 6.
- Sunman's 35 mm hail figure against a test report. It comes from Sunman's own brochure, which also shows two sets of electrical figures across product versions.
- The Accuride 9301 and WARN VRX 25-S net masses, and their Australian stockists.
- An Australian approval for aluminium or composite LPG cylinders.
- BoM solar exposure for specific stations. Section 2 uses assumed values inside BoM's published range.
- The heat loss of the living area, which is an estimate pending the body design.

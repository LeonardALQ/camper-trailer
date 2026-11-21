# 22: Trailer prices outside the new interior

Status: research record, 20 Nov 2026. It priced the trailer lines the new interior did not change, the labour and the NSW compliance. The trailer's parts list, `data/trailer-parts.yaml`, carries its prices.

Prices in AUD including GST. Foreign prices are converted at 1 USD = 1.55 AUD, 1 EUR = 1.68 AUD and 1 GBP = 1.98 AUD and marked converted. Every line, with its URL, date and basis, is in `research/22-trailer-prices.yaml` beside this report. Lines that reports 19, 20 and 21 price (the interior, HVAC, windows, doors, electrics, bed, kitchen, laundry, shower and water system) are not here.

## 1. Summary by group

| Group | Lines | Total, AUD | Contingency, AUD | Basis of the largest lines |
|---|---:|---:|---:|---|
| Running gear, wheels and tyres | 9 | 14,567.64 | 1,598.86 | Listings for the Cruisemaster kit and the Bosch TSC. Tyres converted, wheels (est.) |
| Coupling and drawbar fittings | 9 | 1,995.25 | 258.71 | Listings from Cruisemaster and ARK |
| Chassis steel | 9 | 3,194.10 | 440.43 | Listings from RHS Steel Supplies. Plate parts (est.) |
| Galvanising | 1 | 1,397.00 | 279.40 | Rate per kg (est.) |
| Hired labour, 213 h and an alignment | 7 | 25,760.00 | 5,152.00 | Hours and rate (est.) |
| Body shell | 13 | 15,762.99 | 3,012.65 | Panel prices scaled from DIY Caravans listings |
| Body fittings | 4 | 2,086.20 | 230.79 | Listings for the awning and the mud flaps |
| Wiring and plumbing allowance (BD-11) | 6 | 3,325.00 | 665.00 | Placeholder (est.) until reports 20 and 21 replace it |
| Tanks and guards | 5 | 2,011.75 | 402.35 | Made-to-size tanks (est.) against DIY Caravans prices |
| Drawbar box and fuel cans | 2 | 489.85 | 97.97 | Sheet listing, hardware (est.) |
| Cabinetry (LA-08B, LA-08C, LA-11) | 7 | 2,714.31 | 380.83 | Listings from DIY Caravans and Ply Online |
| Fire safety (LA-12) | 2 | 118.57 | 19.36 | Listing and estimate |
| Compliance and registration, NSW | 13 | 7,350.00 | 1,420.00 | TfNSW fees. Engineer and insurance (est.) |
| Consumables and freight | 8 | 2,960.00 | 592.00 | Estimates |
| Subtotal | 95 | 83,732.66 | 14,550.35 | |
| Total with contingency | | 98,283.01 | | |

- Without hired labour the total is AUD 67,371.01 with its contingency. Labour is 31 % of the subtotal.
- Compliance splits into AUD 5,318 one-off (AUD 4,400 of it the engineer's review) and AUD 2,032 for the first year's registration, plate and insurance.
- Listings carry 26.2 % of the subtotal, rates 3.2 % and estimates 70.6 %. Labour, the panels and the engineer make up most of the estimated share.
- Contingency is 10 % of listing lines and 20 % of rate and estimate lines, 17.4 % overall (section 2.15).
- Not included: the lines reports 19, 20 and 21 price, the lines left out of this report, and the labour to install wiring, plumbing and HVAC (open point 6).

## 2. Method and assumptions per group

### 2.1 General

Prices were checked on 20 Nov 2026 and include GST. Australian stockists come first. Bought quantities are whole stock lengths and sheets, and offcuts are waste. Hired labour uses one trade rate of AUD 120/h (est.), anchored on mobile welders charging from AUD 110/h and Sydney welder wages of AUD 41 to 86/h. If Leonard does the work himself, the labour lines drop out. Each line in `research/22-trailer-prices.yaml` has its URL, date and basis, and `covers` lists the schedule lines it prices where its id is new.

### 2.2 Running gear, wheels and tyres

DIY Caravans prices the XT Freestyle Air tandem kit by variant. Its "from AUD 5,425" is the 2,800 kg kit with plain drums. The 4,500 kg kit with 12 in ABS-enabled electric drums, LC5 M14 studs and a 110 mm spigot is AUD 7,442.04 with the Level 1 base kit (RG-01). The Level 3 manual air kit adds AUD 1,285.00 (RG-04). It brings a 12 V compressor, an 11 L tank, a panel with a digital gauge and a switch for each side, kerb side and road side. It has no automatic height valves, although the schedule's RG-04 text lists them. Cruisemaster's only automatic option now is its Body Control System, priced on request. The Bosch TSC tandem kit is AUD 1,558.70 (RG-03). A spare XT airbag is AUD 380 and the emergency repair kit AUD 125 at Cruisemaster's shop (RG-05).

No Australian listing for the LT265/75R16 123/120R G015 was readable. The tyre price is a US listing of USD 303.99, converted to AUD 471.18 (RG-02). ROH publishes no wheel price, so the wheel stays at R16's AUD 230 (est.) (RG-06). Five of each are priced, four on the axles and one spare.

### 2.3 Coupling, drawbar fittings and corner steadies

The DO35 V3Plus with handbrake is AUD 515 at Cruisemaster's shop, as expected. ARK's own prices cover the XO750 jockey wheel (AUD 449), the XO DDS650 steadies (AUD 149.95 a pair, two pairs) and the HLS13 shackles (AUD 43.44 each). The 13 mm 3,500 kg chain is priced at ARK's bag rate of AUD 38.92/m for 2 m. No Australian breakaway kit listing was readable, so DB-07 is AUD 250 (est.). The stone guard is priced as material at listed rates, with its labour in LAB-05.

### 2.4 Chassis steel

The take-off comes from the schedule's member list:

| Section | Needed | Bought | Price per length, AUD |
|---|---:|---|---:|
| RHS 150 x 50 x 3.0 | 14.21 m | 2 x 8 m | 205.65 |
| RHS 125 x 50 x 3.0, bought as 127 x 51 x 3.5 | 21.86 m | 3 x 8 m | 294.75 |
| RHS 150 x 50 x 5.0 | 5.30 m | 1 x 8 m | 326.65 |
| RHS 75 x 50 x 3.0 | 0.49 m | 1 x 8 m | 122.05 |
| SHS 40 x 40 x 2.5 | 6.96 m | 1 x 8 m | 63.75 |
| SHS 50 x 50 x 2.5 | 1.80 m | 1 x 8 m | 80.25 |
| SHS 50 x 50 x 3.0 | 0.80 m | 1 x 8 m | 95.65 |

The prices are RHS Steel Supplies' (Revesby NSW) for black tube. 150 x 50 x 3 works out at AUD 25.71/m, about AUD 2.87/kg. The listing does not state the grade, so the order must ask for C450L0 on the mill certificate. RHS 125 x 50 x 3 is not a stocked size (open point 1).

The plate parts weigh 55.3 kg in the schedule: 3.5 kg of 5 mm, 9.9 kg of 6 mm, 2.0 kg of 8 mm, 16.3 kg of 10 mm, 6.2 kg of 12 mm and 17.3 kg of 20 mm. Twelve plan-brace gusset plates of 150 x 150 x 6 mm add 12.7 kg (est.). Plate costs AUD 3.05 to 3.44/kg as 1200 x 2400 sheets. Small, thick, drilled parts cut from a profile cutter's stock are priced at AUD 12/kg (est.), for AUD 816. Instant DXF quotes from Lasercorp or mHub would firm this up once the drawings exist.

### 2.5 Galvanising

Galvanisers charge per kg of galvanised weight. Industrial Galvanizers' specifier manual gives AUD 1.20/kg for light 3 mm fabrications, but the figure is old. The line uses AUD 2.75/kg incl GST (est.) on 508 kg, for AUD 1,397. That is the 474 kg in CHASSIS.md plus about 34 kg (est.) for the heavier section of open point 1. Transport to the galvaniser and back is CON-06.

### 2.6 Labour

| Line | Work | Hours (est.) | AUD |
|---|---|---:|---:|
| LAB-01 | Chassis and drawbar: cut, jig, weld, grind, inspect, prepare for the dip | 70 | 8,400 |
| LAB-02 | Running gear and chassis assembly after galvanising | 16 | 1,920 |
| LAB-03 | Wheel alignment, camber and toe | job | 200 |
| LAB-04 | Body shell from finished panels, two people | 70 | 8,400 |
| LAB-05 | Drawbar box, stone guard, tank guards and bearers, mud-flap hangers | 19 | 2,280 |
| LAB-06 | Cupboards, desk seats, freezer bench, trims | 26 | 3,120 |
| LAB-07 | Fit the bought parts in this report | 12 | 1,440 |

The chassis hours rest on the member count. There are 45 members and about 70 plate parts to cut, cope and drill, with vent and drain holes (12 h). The frame is jigged and tacked square to 2 mm (14 h). Welding covers about 18 m of raiser fillets, 6 m of drawbar fillets, about 50 member ends, 32 nut plates and the XT hinge brackets (28 h). Grinding the weld toes, inspection and the record take 10 h, and handling 6 h.

The body hours assume the panel maker CNC-cuts every opening. Two people set the floor and 32 mounts (10 h), then bond the joiners, walls and roof with four people for the roof lift (24 h). They frame and seal ten openings (16 h), seal inside and out with a hose test (12 h) and lay the vinyl (6 h). Panel makers sell kits for owner assembly, and none publishes an assembly price.

### 2.7 Body shell

The panels are bought finished and cut to the drawing by a panel maker such as Creative Composites, StyroMAX or DIY Caravans. Skins and cores are inside the per-m² price. Each panel is priced on its full sheet, so the cut-outs are waste.

| Line | Panel | Area | AUD/m² | Basis |
|---|---|---:|---:|---|
| BD-01 | Floor, 30 mm, woven roving on H80 | 10.61 m² | 277.05 | DIY Floor Panel D, 32 mm H60, AUD 251.86, plus 10 % for H80 (est.) |
| BD-02 | Roof, 40 mm, 2.0 and 1.5 mm skins on XPS | 10.61 m² | 240.00 | DIY Panel B, 29 mm XPS, AUD 216.88, plus about 10 % (est.) |
| BD-03 | Side walls, 35 mm XPS | 17.24 m² | 225.00 | Panel B plus about 4 % (est.) |
| BD-04 | Front and rear walls, 35 mm XPS | 8.45 m² | 232.42 | Front at 240, rear at 225 (est.) |

The joiners are DIY Caravans' 29 mm series at about AUD 28/m: floor joiner 13.6 m, corner joiner 7.8 m and roof-to-wall joiner 13.6 m, bought as 6.5, 4.0 and 2.5 m lengths. The structural adhesive is FixTech Fix 190 MS polymer at AUD 33.47 a 600 ml sausage. Fourteen sausages (8.4 L) cover about 140 m of bead plus waste (est.). Sealant is ten 290 ml cartridges. Inserts are 30 m of high-density PVC strip and 10 m of pultrusion at listed prices taken as per metre. Mount hardware is AUD 16 a mount (est.) for the 32 mounts. Vinyl is AUD 75/m² (est.). BODY.md specifies MS polymer, so no methacrylate or polyurethane adhesive is priced.

### 2.8 Body fittings

The Fiamma F45 S 4.5 m wall-mount awning is AUD 1,790 on sale at Caravan RV Camping, with AUD 150 (est.) for wall and leg brackets. The 610 x 455 mm flaps are AUD 37.26 each at the Boss Shop. Their galvanised hangers are AUD 35.84 each (est.), strap included.

### 2.9 Wiring and plumbing allowance (BD-11)

BD-11 is the old 60 kg block. It is split into six estimated sub-lines so reports 20 and 21 can replace each one:

| Line | Content | AUD (est.) |
|---|---|---:|
| BD-11a | 150 m of 12 and 24 V tinned twin-core at AUD 4.50/m | 675 |
| BD-11b | 40 m of 2.5 mm² TPS, six outlets, a 15 A inlet | 330 |
| BD-11c | 14 LED lights at AUD 40 | 560 |
| BD-11d | Switches, fuses, terminals, conduit, glands | 650 |
| BD-11e | 30 m of 12 mm PEX, 40 push-fit fittings, tank fittings, two fillers | 710 |
| BD-11f | Rivnuts, screws, brackets, P-clips | 400 |

### 2.10 Tanks, guards and heater fuel

DIY Caravans makes tanks to size from AUD 397, priced on dimensions and fittings. Its standard 250 L tank is AUD 549 and its 180 L tank AUD 499. The two bay tanks are priced at AUD 650 for about 220 L and AUD 620 for about 200 L (est.), with AUD 90 a tank for bearers, rubber and straps. The tank guards are one 1200 x 2400 sheet of 3 mm aluminium checker plate at AUD 261.75 plus AUD 80 of angle and fixings. The 15 L heater fuel tank with its line and filter is AUD 220 (est.).

### 2.11 Drawbar box and fuel cans

The box is fabricated, not bought, because it must fit between the drawbar members behind the stone guard. One 1200 x 2400 sheet of 2 mm aluminium checker plate (AUD 174.85) covers the box's 1.94 m² and the stone guard's 0.30 m². Hinge, gas strut, keyed latch, hasp, seal and mounts add AUD 195 (est.). Two 10 L fuel cans with a strap are AUD 120 (est.). The petrol can must meet AS/NZS 2906.

### 2.12 Cabinetry

The tall cupboard LA-08B uses DIY Caravans' flat-pack example price, AUD 584.11 for an 1,800 x 450 x 580 mm cabinet in white gloss lightweight board. The wall cupboard LA-08C is AUD 420 (est.). LA-11 is priced from board and hardware:

| Material | Price | Per m² | Mass |
|---|---:|---:|---:|
| Lightweight poplar ply, HPL white, 12 mm, 2440 x 1220 | AUD 137 a sheet | AUD 46.02 | 6.7 kg/m² |
| The same, 16 mm | AUD 155 a sheet | AUD 52.07 | 9.1 kg/m² |
| Ultralight poplar and XPS sandwich panel | AUD 161 to 190 a sheet | AUD 54 to 64 | not published |

LA-11 takes four 12 mm sheets and two 16 mm sheets, AUD 374 of hinges, push-button latches and stays (est.), six 6.5 m angle trims at AUD 29.70 and AUD 300 for two seat cushions (est.). DIY Caravans' guide puts a small caravan cabinetry set at AUD 1,500 to 2,500 supplied, close to the AUD 2,714 for these three lines.

### 2.13 Compliance and registration in NSW

A home-built trailer has one path to NSW registration. Every trailer built from 1 July 2023 needs an entry on the Register of Approved Vehicles (RAV), and TfNSW no longer issues VINs to home-built trailers ([AIS Notice 41](https://freight.transport.nsw.gov.au/system/files/media/documents/2024/AIS-Notice-41-Inspecting-Concessional-Trailers.pdf)). The Individually Constructed Vehicle path does not apply. At 3,500 kg ATM the trailer is ADR category TB, a light trailer of over 0.75 t up to 3.5 t ([NHVR category codes](https://www.nhvr.gov.au/document/646)), and a low-ATM trailer under the Road Vehicle Standards Act.

1. Build to VSB1 and the ADRs for a TB trailer, and keep the evidence: drawings, weld records, the engineer's review and the parts' data sheets.
2. Apply on the Commonwealth's ROVER portal for a concessional RAV entry approval, which is open to anyone building four or fewer low-ATM trailers in 12 months. The Commonwealth issues the VIN with it. The RAV entry charge is AUD 0.75 ([charges regulation](https://www.legislation.gov.au/F2021L00141/asmade/2021-02-22/text/original/pdf), s 7). The application fee was not confirmed, so CMP-01 allows AUD 100 (est.).
3. Stamp the VIN into the drawbar and fit the trailer plate (AUD 80, est.).
4. Weigh the trailer at a public weighbridge for the tare and the axle and ball loads (AUD 60, est.).
5. Tow it on an unregistered vehicle permit (AUD 28) to a Heavy Vehicle Authorised Inspection Station. Trailers over 2 t GTM, and any with breakaway brakes, go to an HVAIS, not an AUVIS ([VSI 52](https://nsw.gov.au/sites/default/files/2021-02/RMS-14.354-Certification-of-new-trailers-Vehicle-Standards-Information-No-52-November-2008.pdf)). For a concessional low-ATM trailer the examiner must first get an Identity Approval from TfNSW on [form 5703](https://tfnswforms.transport.nsw.gov.au/45065830-apply-for-identity-approval-concessional-trailer-low-atm.pdf). The inspection fee is in AIS Notice 18, which could not be downloaded, so CMP-04 is AUD 250 (est.).
6. Register it at Service NSW as a caravan ([fees](https://www.nsw.gov.au/topics/vehicle-registration/fees-concessions-forms/fees)): registration fee AUD 84, vehicle tax AUD 330 for a private caravan of 1,501 to 2,500 kg tare after the 40 % caravan discount, and a standard plate AUD 58. Trailers and caravans need no CTP ([nsw.gov.au](https://www.nsw.gov.au/driving-boating-and-transport/vehicle-registration/how-to-register/registering-a-brand-new-vehicle)). NSW has charged no duty on registering caravans and camper trailers since 1 July 2009 ([NSW Government](https://data.nsw.gov.au/data/dataset/47595e94-6031-4649-bcdf-50e036efba49/resource/b2bd7c4d-c940-46fb-aa5a-3d66c11568df/download/20090829_axing_stamp_duty_on_caravans_drives_nsw_economic_and_tourism_growth_33_per_cent_jump_20.pdf)).
7. Insure it. Comprehensive cover is optional, AUD 1,560 for the first year at 1.2 % of an AUD 130,000 agreed value (est.).

Two more lines sit in this group. The engineer's review of the chassis, drawbar, coupling and body mounts is not required by law, but CHASSIS.md and BODY.md are drafts until it happens (CMP-03, 20 h at AUD 220/h, est.). The 240 V installation needs a licensed electrician's certificate to AS/NZS 3001.2 (CMP-13, AUD 400, est.). There is no LPG, so no gas certificate is needed.

### 2.14 Consumables, coating and freight

The frame is galvanised and the body gelcoated, so no paint system is priced. Zinc-rich touch-up and Loctite 567 are AUD 100 (est.). Welding consumables are AUD 450 (est.), which a hired shop usually includes in its rate. Freight is estimated: the Cruisemaster pallet AUD 250, the crated one-piece panels AUD 1,200, steel AUD 110, the frame to the galvaniser and back AUD 400, flat-pack cupboards AUD 150 and fifteen parcels at AUD 20.

### 2.15 Contingency

No Australian trailer builder publishes the contingency it uses. The guidance found is 10 to 15 % for DIY camper trailers ([Parking Day](https://parkingday.org/how-to-build-a-camper-trailer/)), 10 to 20 % for one-off construction and 20 % when the owner manages the build ([River Hills Builder](https://riverhillsbuilder.com/how-do-custom-home-builders-charge/)), and 15 to 25 % for early-stage estimates ([Blaze Estimating](https://blazeestimating.com/contingency-in-estimates-how-much-buffer-is-enough/)). The rule here is 10 % on listing and quote lines and 20 % on rate and estimate lines, which gives AUD 14,550.35, 17.4 % of the subtotal. Recompute it whenever a line changes basis or price.

## 3. Open points and the assumption to use

1. RHS 125 x 50 x 3 is not a stocked size. Austube's C450PLUS range and RHS Steel Supplies both skip it. Assumption: use RHS 127 x 51 x 3.5 for the raisers, outriggers and floor crossmembers. It is within 2 mm of the design section and stocked at AUD 294.75 per 8 m. At about 9.3 kg/m (est.) it adds about 33 kg and AUD 267. The listing states no grade, so the frame model should take C350L0 (fy 350 MPa) until the mill certificate shows more. 150 x 50 x 3 and 125 x 75 x 3 are the stocked alternatives at AUD 205.65 per 8 m.
2. No stocked joiner was found for the 35 mm walls. DIY Caravans' joiners fit 29 mm walls, and its roof joiner takes a 40 mm roof onto a 29 mm wall. Assumption: the panel maker supplies joiners for the 30, 35 and 40 mm panels at about DIY's AUD 28/m. If none exists, the walls change to 29 mm XPS Panel B (AUD 216.88/m², 6.5 kg/m²) on DIY's joiners and BODY.md's wall checks are re-run.
3. BD-08 carries 6.5 kg of adhesive and sealant, but the bead length needs about 8.4 L of MS polymer. Assumption: 12.6 kg at about 1.5 kg/L (est.), 6 kg more than the model.
4. DIY Caravans welds its made-to-size tanks from 10 mm polypropylene, not the modelled 6 mm HDPE. Assumption: tanks of about 31 kg and 29 kg (est., 1.6 times UF-01 and UF-01R), 22 kg more, until a maker quotes the drawing.
5. No Australian price was found for the G015 tyre or the ROH Trak 2 wheel. Assumption: AUD 471.18 a tyre (converted) and AUD 230 a wheel (est.). Report 23 should use the same figures for the ute's matching tyres and wheels.
6. No report 22 line holds the labour to install wiring, plumbing and HVAC. Assumption: reports 20 and 21 add their hours at AUD 120/h. If they do not, allow 120 h (est.), AUD 14,400.
7. The low vehicle tax and the duty exemption depend on registering the trailer as a caravan. Assumption: a private caravan at AUD 330 a year. Above 2,500 kg tare the tax is AUD 516, and above 2,790 kg AUD 586. As a plain trailer the tax would be AUD 550, and motor vehicle duty might apply at 3 % of value to AUD 45,000 and 5 % above ([Revenue NSW](https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/motor-vehicle-duty)).
8. Two fees could not be confirmed: the concessional RAV entry application and the HVAIS inspection. Assumption: AUD 100 and AUD 250 (est.).
9. The schedule's RG-04 text names height valves, and the Level 3 kit has none. Assumption: Level 3 manual, as priced, and the schedule text changes to match. Automatic levelling would need Cruisemaster's Body Control System, priced on request.
10. The panel prices are scaled from DIY Caravans listings, not quoted by a maker using Polydet skins and H80 cores. The panels are AUD 11,329, 20 % of the non-labour subtotal. Assumption: the per-m² prices in section 2.7 stand until a maker prices the drawings.
11. Insurance is priced on an AUD 130,000 agreed value (est.). Assumption: 1.2 % of the final build total once reports 19, 20 and 21 add their lines.

## 4. Sources

- Running gear: [DIY Caravans XT Freestyle Air tandem](https://www.diycaravans.com.au/shop/cruisemaster-xt-freestyle-air-suspension-kit-tandem/), [Cruisemaster Level 3 air](https://cruisemaster.com.au/lvl3-air/), [DIY Caravans Bosch TSC](https://www.diycaravans.com.au/shop/bosch-trailer-safety-control-tsc-abs-enabled/), [Cruisemaster shop](https://cruisemaster.com.au/shop/), [TireMart G015](https://www.tiremart.com/yokohama-geolandar-a-t-g015-lt-265-75r16-123-120r-e-10-ply-at-all-terrain-tire-dc), [ROH Trak 2](https://roh.com.au/wheels/trak-2).
- Fittings: [ARK XO750](https://www.arkcorp.com.au/product/xo750-jockey-wheel/), [ARK corner steadies](https://www.arkcorp.com.au/product/xo-corner-steadies/), [ARK shackles](https://www.arkcorp.com.au/product/hammerlock-shackles/), [ARK chain](https://www.arkcorp.com.au/product/trailer-safety-chain/), [Boss Shop mud flap](https://www.thebossshop.com.au/mudflap-rubber-610mmw-x-455mml-black), [Fiamma F45 S at Caravan RV Camping](https://www.caravanrvcamping.com.au/awnings-screens-mats-covers/caravan-rv-awnings/box-awnings/fiamma-box-awning/fiamma-f45-wall-mount/).
- Steel and coating: [RHS Steel Supplies RHS](https://www.rhssteelsupplies.com.au/hikashop-menu-for-categories-listing/category/13-rhs-mild-steel.html), [SHS](https://www.rhssteelsupplies.com.au/hikashop-menu-for-categories-listing/category/15-shs-mild-steel-square.html), [plate](https://www.rhssteelsupplies.com.au/hikashop-menu-for-categories-listing/category/374-mild-steel-sheet-plates-250gr-as-nzs-3678.html), [checker plate](https://www.rhssteelsupplies.com.au/hikashop-menu-for-categories-listing/category/107-aluminium-5-bar-checker-plate-tread.html), [galvanising cost factors](https://www.steel.org.au/getattachment/2f694ebb-98a7-4273-be94-e0f61bd74328/Cost-factors-for-hot-dip-galvanised-coatings_INGALSM3.pdf).
- Body and fit-out: [DIY Caravans Panel B](https://www.diycaravans.com.au/shop/composite-panel-wall-b-xps-core-29mm-m2/), [Floor Panel D](https://www.diycaravans.com.au/shop/floor-panel-d-pvc-core-20mm-32mm/), [joiners](https://www.diycaravans.com.au/shop/panel-joiner-diy-wall-29-29/), [Fix 190](https://www.diycaravans.com.au/shop/fix-msp-190-white-black-slow/), [custom tanks](https://www.diycaravans.com.au/shop/custom-made-caravan-rv-tanks/), [flat-pack cabinets](https://www.diycaravans.com.au/shop/custom-flat-pack-caravan-cabinets/), [Ply Online poplar](https://www.plyonline.com.au/products/poplar-ply-lightweight-hpl-white), [Jaybro extinguisher](https://www.jaybro.com.au/fire-safety/abe-fire-extinguisher-with-metal-vehicle-bracket-and-hose-1kg/).
- Compliance: [AIS Notice 41](https://freight.transport.nsw.gov.au/system/files/media/documents/2024/AIS-Notice-41-Inspecting-Concessional-Trailers.pdf), [VSI 52](https://nsw.gov.au/sites/default/files/2021-02/RMS-14.354-Certification-of-new-trailers-Vehicle-Standards-Information-No-52-November-2008.pdf), [form 5703](https://tfnswforms.transport.nsw.gov.au/45065830-apply-for-identity-approval-concessional-trailer-low-atm.pdf), [NSW registration fees](https://www.nsw.gov.au/topics/vehicle-registration/fees-concessions-forms/fees), [RVS charges regulation](https://www.legislation.gov.au/F2021L00141/asmade/2021-02-22/text/original/pdf), [registering a new vehicle](https://www.nsw.gov.au/driving-boating-and-transport/vehicle-registration/how-to-register/registering-a-brand-new-vehicle).
- Labour: [mobile welders](https://mobilewelders.com.au/), [Indeed welder wages, Sydney](https://au.indeed.com/career/welder/salaries/Sydney-NSW), [structural engineer salary](https://employmenthero.com/career-advice/structural-engineer/salary/).

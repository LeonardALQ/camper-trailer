# 14: LandCruiser 79 V8 engine, rebuild, turbo, exhaust and tune

Note added 20 Nov 2026, after the vehicle plan (VEHICLE.md). The plan departs from this report in four places. First, the legal path: Transport for NSW's VSI 06 Rev 4, in force since 1 July 2026, adds item 6, so flashing the engine management system in a way that alters emissions output needs a VSCCS certificate. This report read the 2013 revision, so its finding that power level A needs no certificate is wrong. Level A needs an LA4 certificate with emissions evidence too, about AUD 2,000 (estimate), and VEHICLE.md carries it. Second, the truck: the GVM kit needs a VDJ79 built from 01/2017, so the plan takes this report's DPF variant (piezo injectors, DPF-back exhaust), not a pre-DPF truck. Third, the review added a sealed airbox and a DPF inspection and clean as required lines, and prices the rebuild kit as an estimate for the DPF engine. Fourth, level B stays open as a retune on the same hardware. The parts list for this report is published as `research/14-engine-parts.yaml`, and VEHICLE.md's merged list is `data/vehicle/vehicle-parts.yaml`.

Research report 14, 20 Nov 2026. It covers the engine side of the VDJ79 single cab build: the base 1VD-FTV, the rebuild, the power upgrades and the NSW legal path. Report 15 covers the clutch, gearbox, driveline and general refresh. Report 16 covers the GVM (gross vehicle mass) upgrade, brakes, wheels and tyres.

## Recommendation

**Power level A: the legal 20 % tune, on hardware that can go further.** Build the engine for about 181 kW at the crank (243 hp). That is 20 % over the factory 151 kW. Torque is about 650 Nm from about 1,800 to 2,700 rpm (estimate). Use a turbo and intercooler sized for level B (220 to 250 kW), so the engine runs well inside their limits when towing and can be retuned later if a certifier signs it off.

Why this level:

- It is the most power NSW allows without a certificate. *Superseded 20 Nov 2026: VSI 06 Rev 4 item 6 needs a VSCCS certificate for this tune, the LA4 certificate at about AUD 2,000 (estimate). See the note above.* Transport for NSW (TfNSW) requires certification when power rises more than 20 % or when emissions rise ([TfNSW VSI 06](https://www.rms.nsw.gov.au/documents/roads/safety-rules/standards/vsi-06-light-vehicle-modifications.pdf), items 2 and 5).
- It holds about 88 km/h on a 6 % grade at 6.6 t, against about 76 km/h stock (estimate, section 3.8). Level B would hold about 105 km/h, but needs an LA4 certificate (the national code's approval for a modified engine, section 4.1) and a driveline built for about 850 Nm.
- A bigger turbo and a front-mount intercooler lower exhaust and intake temperatures at the same power ([GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf), pages 18 and 28). That margin matters more than peak power for hours of towing in heat.
- The factory clutch slips above about 500 Nm ([GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf), page 23), so even level A needs the clutch from report 15.

The build (full list in section 5):

- A full rebuild to factory specification: the NVP kit (pistons, rings, bearings, genuine gaskets, graded head gaskets, new head bolts), machine-shop work, a genuine timing set, oil pump and water pump, a new radiator, hoses, thermostat and fan clutch.
- Fuel: eight new genuine injectors, a new Denso supply pump and a 30 micron pre-filter with a water separator.
- Air: a GTurbo VD-G333 Titan turbo and a PDI front-mount intercooler in the twin-throttle version, which keeps the EGR (exhaust gas recirculation).
- Exhaust: a Manta 3 inch stainless system. On a truck built without a diesel particulate filter (DPF, before October 2016) it runs turbo-back and keeps the catalytic converters. On a DPF truck it runs DPF-back.
- Tune: custom, with a towing map, peak power capped at 1.2 times the truck's own stock dyno reading, and a fuel limit on exhaust gas temperature (EGT).
- Gauges: boost, EGT before the turbo, coolant and oil temperature.

**Legal path: no VSCCS certificate** (the NSW modification certificate, section 4.3). Keep the catalytic converters or DPF, the EGR and a quiet muffler. Keep before-and-after dyno sheets from the same dyno. Book the free TfNSW emissions test that VSI 06 names, and tell the insurer about every change. Cost about AUD 0 (estimate).

*Superseded 20 Nov 2026: VSI 06 Rev 4 item 6 needs a VSCCS certificate for this tune, the LA4 certificate at about AUD 2,000 (estimate). See the note above.*

**Total: about AUD 32,200** for parts, machining and tune, with estimates included. That is about twice the AUD 15,000 share of the budget. The cheapest reliable version (rebuilt standard turbo, no front mount, aluminised exhaust) is about AUD 27,000. Reusing the injectors, supply pump, radiator and oil pump after they pass tests saves up to about AUD 6,600 more, at some risk. So the AUD 30,000 total budget needs to rise, by at least the AUD 12,000 to 17,000 that the engine side runs over its share.

**Model years.** For the engine alone, prefer a pre-DPF truck built from 2010 to October 2016. Its injectors cost about half as much as the later piezo injectors, and its exhaust has no DPF to keep. A DPF truck (October 2016 to 2024) costs about AUD 3,600 more at this level. Its single cab has a stronger chassis and stability control, so reports 15 and 16 may favour it anyway. *Superseded 20 Nov 2026: the GVM kit needs a truck built from 01/2017, so the plan buys a DPF truck and takes this report's DPF variant (decision log 11:25).*

**Levels B and C.** Level B (220 to 250 kW, about 850 Nm) needs an LA4 certificate (about AUD 2,000, estimate), emissions evidence and a driveline the certifier accepts for the torque. Its engine side costs about AUD 34,700. Level C (about 300 kW, about 1,050 Nm) costs about AUD 38,700 before certification and is not realistic to certify for this use (section 4.5).

## 1. The base engine

### 1.1 The 1VD-FTV in the VDJ79

| Item | Value | Source |
|---|---|---|
| Engine | 1VD-FTV, 4.5 L V8 turbo diesel, 90 degree V, 32 valves | [motorreviewer](https://www.motorreviewer.com/engine.php?engine_id=113), [Drive](https://www.drive.com.au/news/toyota-landcruiser-70-series-specifications/) |
| Output, VDJ79 | 151 kW at 3,400 rpm, 430 Nm from 1,200 to 3,200 rpm | [Drive](https://www.drive.com.au/news/toyota-landcruiser-70-series-specifications/) |
| Bottom end | Nodular graphite cast iron block, forged steel crank on five journals, high-strength steel conrods, aluminium pistons, oil jets under the bores | [motorreviewer](https://www.motorreviewer.com/engine.php?engine_id=113) (third-party) |
| Fuel system | Denso common rail, HP4 supply pump, nine-hole injectors | [motorreviewer](https://www.motorreviewer.com/engine.php?engine_id=113) |
| Turbo | One Garrett variable nozzle turbo (VNT, a turbo whose exhaust vanes swing to change boost). Called GTA2359V, Toyota 17201-51010, by [Turbochargers Plus](https://www.turbochargersplus.com/turbochargers-toyota-land-cruiser-70-series-v8-17201-51010-gta2359v-billet-impeller-upgrade/) and motorreviewer, and GT2559V by [GTurbo](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) (page 8). Top-mount intercooler under the bonnet scoop | As listed |
| Stock power at the wheels | 96 to 120 kW. A chassis dyno measures power at the wheels, written rwkW here. The figure varies with the dyno and the tyres | [4x4 Australia](https://www.4x4australia.com.au/gear/stage-1-hp-f-upgrade-landcruiser-79-build) 96 kW on 34 inch tyres, [GTurbo](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) 100 to 120 kW, [HD Automotive](https://hdautomotive.com.au/blog/2024/01/24/70-series-ecu-remapping-brisbane/) 150 hp (112 kW) |

### 1.2 Model years

| Build | Emissions level | Injectors and exhaust | Other changes that matter here | Sources |
|---|---|---|---|---|
| March 2007 to 2010 | Euro 4 | Solenoid injectors inside the rocker covers, catalytic converters, no DPF | Early engines drew oil consumption reports (section 1.3) | [Drive](https://www.drive.com.au/news/toyota-landcruiser-70-series-specifications/), [NVP kit fitment note](https://gturbo.com.au/products/nvp-engine-rebuild-kit-toyota-1vd-ftv-70-series) |
| 2010 to October 2016 | Euro 4 | As above | None found for the engine | As above |
| October 2016 to late 2024 | Euro 5 | Piezo injectors, DPF, re-routed exhaust | Single cab: thicker chassis with seven crossmembers, stability control, five airbags, one 130 L tank instead of two 90 L tanks, taller second and fifth gears | [4x4 Australia](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched), [Carscoops](https://www.carscoops.com/2016/10/toyota-brings-70-series-land-cruiser-up/) |

Power and torque stayed at 151 kW and 430 Nm through the 2016 update ([Carscoops](https://www.carscoops.com/2016/10/toyota-brings-70-series-land-cruiser-up/)). The V8 ended in late 2024, when the 2.8 L four-cylinder replaced it ([70 Series Store](https://jp.70seriesstore.com/en/blogs/information/79-series-landcruiser-exhaust-systems-the-complete-upgrade-guide), [Hema Maps](https://hemamaps.com/blogs/hema-maps-gear/rebuilding-hema-maps-iconic-76-series-landcruiser-part-2)).

Which years to prefer for this build:

- **Engine only: pre-DPF, 2010 to October 2016.** New genuine injectors cost AUD 4,290 against AUD 9,256 for the piezo set ([GTurbo](https://gturbo.com.au/products/toyota-1vd-ftv-injectors), [GTurbo](https://gturbo.com.au/products/toyota-1vd-ftv-dpf-injectors)). High-flow nozzles cost AUD 1,190 against AUD 2,790. There is no DPF to keep clean or to keep legal. Starting at 2010 avoids the early engines that drew oil consumption reports.
- **Whole vehicle: the DPF truck may still win.** The 2016 single cab chassis and stability control matter for a 3.6 to 3.9 t ute towing 3 t. Reports 15 and 16 decide. A DPF engine at level A costs about AUD 3,600 more (section 5).
- At 400,000 km, most trucks for sale will be pre-DPF. A DPF truck at that distance has averaged at least 40,000 km a year (estimate from its age).

### 1.3 Known failure modes

Sources are labelled by type: Toyota, specialist (a workshop or parts maker that builds these engines), third-party (a general engine site) or owner report.

| Problem | What happens | Source | What the rebuild does about it |
|---|---|---|---|
| Oil consumption, early engines | Owners of early engines reported high oil use. Toyota's bulletin says many reports came from checking the level over too short a distance. A third-party site blames a failed vacuum pump on engines before 2010. One owner quotes about 1 L per 5,000 km when driven gently | [Toyota bulletin, copy on Scribd](https://www.scribd.com/document/340399442/1VD-FTV-service-bulletin-oil-consumption-pdf) (Toyota), [motorreviewer](https://www.motorreviewer.com/engine.php?engine_id=113) (third-party), [ih8mud](https://forum.ih8mud.com/threads/79-serieis-with-1vd-ftv-reliability.954517/) (owner), [Club 4X4](https://www.club4x4.com.au/tune-toyotas-1vd-ftv-engine/) (rumours at launch) | New rings and a fresh hone. Check the vacuum pump for oil passing into the brake vacuum line |
| Injectors | Failures linked to dirty or wet fuel. Injector knock is a common sign an engine is due for a rebuild | [ih8mud](https://forum.ih8mud.com/threads/79-serieis-with-1vd-ftv-reliability.954517/) (owner), [Hema Maps](https://hemamaps.com/blogs/hema-maps-gear/rebuilding-hema-maps-iconic-76-series-landcruiser-part-2) (workshop) | Eight new injectors, a 30 micron pre-filter with water separator |
| Diesel in the sump, pre-DPF | The pre-DPF injectors sit inside the rocker covers. A badly seated leak-off washer lets diesel into the sump. The oil level rises and the engine can run away | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 42 (specialist) | New fitting kit, injectors torqued to 18 Nm, leak-off rail tested with air, oil level watched for 1,000 km |
| Supply pump wear | A 5 micron aftermarket filter starves the pump and speeds wear. Metal from a failing pump can spread through the system and back to the tank | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 43 (specialist) | New pump, 30 micron pre-filter, tank and lines flushed |
| Bearings | On Hema's 1VD the conrod bearing overlay had worn through to the copper backing | [Hema Maps](https://hemamaps.com/blogs/hema-maps-gear/rebuilding-hema-maps-iconic-76-series-landcruiser-part-2) (workshop) | New bearings, crank measured and ground or polished |
| Timing chain tensioners | A workshop found a tensioner fault on a 79 during a tune job | [Just Diesel Performance](https://www.justdieselperformance.com.au/toyota/70-series-land-cruiser/) (owner review) | New chains, tensioners and guides |
| Turbo actuator | The turbo sits low. The actuator's breather draws in water at crossings and the actuator rusts | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 42 (specialist) | New turbo with a stainless actuator and a breather hose run up high |
| Intake pipe | The plastic pipe to the turbo absorbs breather oil, softens and can split or collapse, letting dust in | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 26 (specialist) | Replace the pipe |
| Oil filter collapse | The support pole inside the filter housing comes out with the old filter. Without it the new filter collapses and starves the engine of oil | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 42 (specialist) | Build and service note |
| EGR and intake soot | Oily soot builds up in the EGR and intake | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 43 (specialist) | Strip and clean during the rebuild |
| Starter motor | Hard to change, and suffers in deep water | [ih8mud](https://forum.ih8mud.com/threads/79-serieis-with-1vd-ftv-reliability.954517/) (owner) | Report 15 (electrical) |
| Oil cooler, valley and rear main seal leaks | No source specific to the 1VD was found | None | Every seal and O-ring comes new in the genuine gasket set. Pressure-test the oil cooler |

The same owner thread reports several Australian engines past 500,000 km, and says they are reliable if maintained ([ih8mud](https://forum.ih8mud.com/threads/79-serieis-with-1vd-ftv-reliability.954517/)).

### 1.4 What a 400,000 km engine usually needs

Hema's workshop lists the signs of a 1VD due for a rebuild: injector knock, oil leaks, blow-by, worn bearings and piston slap. It takes an oil sample before stripping to read bearing wear. It notes a hone is often enough for the bores, and a rebore is possible on this block ([Hema Maps](https://hemamaps.com/blogs/hema-maps-gear/rebuilding-hema-maps-iconic-76-series-landcruiser-part-2)). Its workshop recondition with genuine parts and labour cost AUD 22,000 to 29,000 (same source). Doing the labour himself, Leonard pays for parts and machining only.

Assume a 400,000 km engine needs all of it: rings, bearings, a hone or rebore, timing set, injectors, supply pump, turbo, water pump, glow plugs, seals and a cleaned intake. Section 2 prices each part.

Engine checks before buying (report 15 has the full inspection): a compression test on all eight cylinders, injector correction values read with a scan tool, blow-by at the oil filler, an oil sample, coolant checked for oil and oil for coolant, and turbo shaft play. A truck that fails these is still a rebuild candidate. A cracked block or head is the walk-away result.

## 2. The rebuild parts list

Prices are AUD including GST, read from the supplier's page on 20 Nov 2026 unless marked as an estimate. Part numbers are the supplier's or Toyota's where found. Where no number was found, order by VIN from a Toyota dealer. Every item is also in `14-engine-parts.yaml`.

### 2.1 Bottom end and heads

| Item | Part number | Supplier | AUD | Notes |
|---|---|---|---|---|
| NVP engine rebuild kit, 1VD-FTV, 70 Series pre-DPF | Sized by bore, main and rod undersize | [GTurbo, from North Vic Parts](https://gturbo.com.au/products/nvp-engine-rebuild-kit-toyota-1vd-ftv-70-series) | 2,471 | Eight TIK pistons with pins and circlips, TP ring set, genuine full gasket set, genuine LH and RH head gaskets (grade 5), main and conrod bearings, thrust washers, head bolt set. Allow 2 to 4 weeks |
| Head gaskets in other grades | RH 11115-51030-A0 to -E0 (grades), LH by VIN | [Lexus parts](https://parts.lexus.com/products/product/cylinder-head-gasket-right-hand-1111551030a0) | 0 to 400 (estimate) | Grade is chosen per bank from measured piston protrusion. Banks differ ([GTurbo](https://gturbo.com.au/products/genuine-toyota-full-gasket-set-1vd-ftv-vdj76-vdj78-vdj79-pre-dpf)). Swap the kit's grade 5 if the measurement calls for it |
| Head bolts | In the kit | GTurbo | 0 | Torque-to-yield (TTY) bolts. They stretch when tightened and are single use ([GTurbo](https://gturbo.com.au/products/genuine-toyota-full-gasket-set-1vd-ftv-vdj76-vdj78-vdj79-pre-dpf)) |
| Timing set: chains, tensioners, guides | Chain 13506-51020, tensioner 13540-51020, guides 13559-51010 and 13561-51020 | Toyota dealer. Numbers from an [aftermarket listing](https://tr.aliexpress.com/w/wholesale-1vd-ftv.html) | 900 (estimate) | Buy genuine. Confirm quantities per bank by VIN |
| Oil pump | By VIN | Toyota dealer | 700 (estimate) | GTurbo's stroker engine uses new genuine oil, rail and water pumps ([GTurbo](https://gturbo.com.au/products/1vd-ftv-5-0l-stroker)) |
| Glow plugs, eight | By VIN | Toyota dealer | 400 (estimate) | Replace at 400,000 km |
| Engine mounts, two | By VIN | Toyota dealer | 350 (estimate) | More torque loads them harder |

**Head studs.** No head stud kit for the 1VD was found. ARP's Australian listings found cover the older 1HD six-cylinder only ([eBay](https://www.ebay.com.au/itm/302149906815)). So every level uses new genuine TTY head bolts and correctly graded gaskets. This is one reason level C is a poor fit for sustained towing.

**Pistons for high power.** No forged piston set for the 1VD was found from an Australian supplier. GTurbo's 5.0 L stroker long block uses custom pistons, forged 4340 conrods and a billet crank, and costs AUD 34,900 ([GTurbo](https://gturbo.com.au/products/1vd-ftv-5-0l-stroker)).

**DPF engines.** The NVP kit is listed for pre-DPF engines with the injectors inside the rocker covers. Assumption for a DPF engine: a kit of the same parts at the same price, with the DPF-engine gasket set.

### 2.2 Machine shop

No 1VD price list was found. The estimates scale DieselWorks' published unit prices: bore and hone AUD 450 for six cylinders, deck skim AUD 150, full service of a 16-valve head from AUD 350, crack test AUD 50 ([DieselWorks](https://dieselworks.com.au/services/)).

| Work | AUD (estimate) |
|---|---|
| Hot tank clean and crack test, block | 250 |
| Bore and hone eight cylinders with a torque plate, to suit the pistons | 650 |
| Deck both banks | 300 |
| Line hone the mains | 400 |
| Crank: crack test, measure, grind or polish | 400 |
| Conrods: check, resize big ends, new small-end bushes | 400 |
| Two heads: crack and pressure test, resurface, cut seats, reface or replace valves, lap | 1,400 |
| Allowance for valve guides, valves and seals found worn | 400 |
| **Required total** | **4,200** |
| Balance the rotating assembly (optional) | 400 |

Measure first, then order the kit sizes. The kit is built to the selected piston, ring and bearing sizes ([GTurbo](https://gturbo.com.au/products/nvp-engine-rebuild-kit-toyota-1vd-ftv-70-series)).

### 2.3 Fuel system

| Item | Part number | Supplier | AUD | Notes |
|---|---|---|---|---|
| Injectors, eight, genuine new, pre-DPF | GTurbo F I 1VDFTV S1 NEW | [GTurbo](https://gturbo.com.au/products/toyota-1vd-ftv-injectors) | 4,290 | Levels A and B. Level C uses the high-flow set (section 3.6) |
| Injectors, eight, genuine new piezo, DPF | GTurbo DPF set | [GTurbo](https://gturbo.com.au/products/toyota-1vd-ftv-dpf-injectors) | 9,256 | For a DPF truck instead of the line above |
| Injector fitting kit (seals, washers, seats) | 1VD-FTV injector fitting kit | [GTurbo](https://gturbo.com.au/products/1vd-ftv-injector-fitting-kit) | 320 | The DPF kit is AUD 190 ([GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf), page 25) |
| Supply pump, Denso HP4, new | 294050-0280 pre-DPF, 294050-0560 DPF | [GTurbo pre-DPF](https://gturbo.com.au/products/1vd-ftv-injector-pump-pre-dpf-294050-0280), [GTurbo DPF](https://gturbo.com.au/products/1vd-ftv-injector-pump-dpf-294050-0560) | 1,480 | A worn pump spreads metal through the system |
| Pre-filter and water separator, 30 micron | Direction Plus PreLine kit PL625DPK for VDJ76 and VDJ79 | [Direction Plus](https://directionplus.com.au/), [Filters Plus](https://www.filtersplus.co/product/pl625dpk/) | 432 (similar kit) | The PL625DPK page blocked reading. Price taken from the [Fuel Manager FM618DPK kit](https://www.filtersplus.co/product/fm618dpk/). GTurbo advises at least 30 micron, or a lift pump if finer ([booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 43) |
| Factory fuel filter element, genuine | 23390-51070 | [eBay listing](https://www.ebay.com.au/p/16026541355) | 40 | Fit new at the rebuild |

Lift pump: none needed. With a 30 micron pre-filter ahead of the factory filter, the factory pump draws through both, which is the setup GTurbo recommends (same page).

### 2.4 Cooling

| Item | Part number | Supplier | AUD | Notes |
|---|---|---|---|---|
| Radiator, VDJ 2007 to 2025 | Natrad listing | [Natrad](https://natrad.com.au/product/toyota-landcruiser-2007-2025-vdj-radiator-3/) | 1,756 | A 400,000 km radiator is likely part blocked. Towing at more power puts more heat through it |
| Water pump, genuine | By VIN | Toyota dealer | 450 (estimate) | |
| Thermostat and gasket, genuine | By VIN | Toyota dealer | 90 (estimate) | |
| Fan clutch (viscous coupling), genuine | By VIN | Toyota dealer | 450 (estimate) | A tired clutch slips at low speed, which is when towing up a grade |
| Hose set: radiator, heater and bypass | By VIN | Toyota dealer | 400 (estimate) | |
| Coolant, Toyota long life, about 20 L | By VIN | Toyota dealer | 150 (estimate) | |
| Oil cooler | By VIN | Toyota dealer | 0, or 500 if it fails (estimate) | Pressure-test it. Its seals come in the gasket set |

### 2.5 Gaskets, seals and sundries

| Item | Supplier | AUD | Notes |
|---|---|---|---|
| Genuine full gasket set, including front and rear main seals | In the NVP kit. Also sold alone for AUD 600 ([GTurbo](https://gturbo.com.au/products/genuine-toyota-full-gasket-set-1vd-ftv-vdj76-vdj78-vdj79-pre-dpf)) | 0 | Covers every seal except the head gaskets |
| Oil, filters, form-in-place sealant, assembly lube | Toyota dealer, parts store | 400 (estimate) | |

### 2.6 Rebuild subtotal

| Group | AUD |
|---|---|
| Bottom end and heads (kit, timing set, oil pump, glow plugs, mounts) | 4,821 |
| Machine shop | 4,200 |
| Fuel system, pre-DPF | 6,562 |
| Cooling | 3,296 |
| Sundries | 400 |
| **Rebuild total, pre-DPF, before any power parts** | **19,279** |

This is the part of the spend that buys reliability. It is already above the AUD 15,000 target. Parts that may pass a test and be reused: the injectors (a specialist service is about AUD 1,600 for eight, estimate), the supply pump, the radiator and the oil pump. Together they save up to about AUD 6,600.

## 3. Power levels

### 3.1 How power is measured

Tuners in Australia quote power at the wheels from a chassis dyno. Crank power, the figure Toyota quotes, is higher by the driveline loss. A stock VDJ79 reads 96 to 120 rwkW against 151 kW at the crank (section 1.1), so the wheels see 64 to 79 % of crank power. This report converts with 74 %, from HD Automotive's stock 112 rwkW (estimate). Torque at the wheels converts the same way.

The legal test in NSW is a rise of more than 20 % over the original power ([VSI 06](https://www.rms.nsw.gov.au/documents/roads/safety-rules/standards/vsi-06-light-vehicle-modifications.pdf), item 2). The cleanest evidence is a ratio: the truck's own stock run and its tuned run on the same dyno, same tyres, same day conditions. The tuned peak must be at most 1.20 times the stock peak. For example, a 96 rwkW baseline allows 115 rwkW.

This matters because commercial "stage 1" tunes go past 20 %. The HP-F stage 1 tune on a DPF 79 lifted 96 rwkW and 293 Nm to 133.5 rwkW and 548 Nm at the wheels, a 39 % power rise ([4x4 Australia](https://www.4x4australia.com.au/gear/stage-1-hp-f-upgrade-landcruiser-79-build)). A level A tune must be written to the cap.

Torque is not capped by the rule. Power is torque times engine speed, so a tune can raise mid-range torque a lot and still hold peak power to 181 kW. At 650 Nm, power reaches 181 kW at about 2,660 rpm. Above that, the tune holds 181 kW and torque falls to about 510 Nm at 3,400 rpm (calculated).

### 3.2 Turbos sold in Australia for the VDJ79

| Turbo | Type | AUD | Results quoted by the seller (at the wheels) | Source |
|---|---|---|---|---|
| GTurbo VD-STD | Rebuilt factory turbo, exchange | 1,990 | Factory output. GTurbo's table gives a 12 psi design boost | [GTurbo](https://gturbo.com.au/products/vd-std-1vd-ftv-rebuilt-standard-turbo) |
| GTurbo VD-G333 Titan | Upgraded VNT, billet wheel, 30 % larger turbine, journal bearing (ball bearing AUD 5,290) | 4,290 | With remap: 190 to 220 rwkW, 800 to 900 Nm. With all supporting parts: 260 rwkW, 1,000 Nm. Design boost 24 psi | [GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) pages 14 and 15 |
| GTurbo VD-G380 Titan | Larger turbine | 4,290 (5,290 ball bearing) | 190 to 220 rwkW with remap, 290 rwkW and 1,000 Nm with all supporting parts | Same, pages 16 and 17 |
| GTurbo VD-G400Ti | Titanium compressor wheel, 59 % larger | 4,980 (6,290 ball bearing) | 200 to 230 rwkW with remap, 330 rwkW and 1,100 Nm with all supporting parts | Same, pages 13, 18 and 19. Page 18 prints AUD 4,290, page 13 AUD 4,980. The higher is used |
| UFI VDJ330 (HD Automotive) | Wastegated, not VNT, OEM-style bolt-on | Not published | 20 psi: about 240 hp and 750 Nm on factory injectors. 28 psi: about 280 hp and 950 Nm. 300 to 330 hp with high-flow injectors | [HD Automotive](https://hdautomotive.com.au/product/vdj330-turbo-70-1vd-toyota-landcruiser/) |

GTurbo's figures are its own and assume a turbo-back exhaust. Keeping the DPF lowers them slightly (booklet pages 15 to 19). GTurbo reports its first development truck ran over 80,000 km of high-load use at more than 70 % above factory power, and that its race 79 finished three seasons with no engine or turbo failure (booklet pages 9 to 11). These are maker's claims, not independent tests. Warranty is 12 months, or 24 months on some models (booklet, warranty page).

Choice: the **VD-G333 Titan**, journal bearing. GTurbo pitches it at towing and low-end torque. It is a direct fit with a VNT like the factory unit, so the ECU controls boost the factory way, and it has the stainless actuator with a raised breather. At level A it runs far below its design boost, which keeps exhaust drive pressure and EGT down. Add the AUD 299 [VDJ70 turbo gasket kit](https://gturbo.com.au/products/vdj70-turbo-gasket-kit).

### 3.3 Intercoolers

| Option | AUD | What it does | Source |
|---|---|---|---|
| PDI front-mount kit, twin throttle (keeps both factory throttles and the EGR feed) | 2,200 pre-DPF, 2,200 or 2,300 DPF | 700 mm wide core, 3 inch outlets, fits behind a bullbar and winch without cutting. PDI claims intake temperatures as low as 47 °C at full load, three times better than top-mount options | [GTurbo listing](https://gturbo.com.au/products/landcruiser-vdj-76-78-79-series-front-mount-intercooler-kits), [booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) pages 28 and 29 |
| PDI front-mount kit, single entry | 2,595 to 2,695 | Removes the throttle butterflies and EGR feed. Needs tuning to avoid derate. Not used: removing EGR needs certification in NSW | Same |
| GTurbo twin fan kit on the factory top mount | 1,895 | Pulls air through the top mount at low speed to fight heat soak | [GTurbo](https://gturbo.com.au/products/gturbo-vdj70-200-intercooler-fan-kit) |

Choice: the PDI twin-throttle front mount. An intercooler that keeps the emission equipment needs no certification in NSW ([VSI 06](https://www.rms.nsw.gov.au/documents/roads/safety-rules/standards/vsi-06-light-vehicle-modifications.pdf), item 5). Check that the core does not block the radiator's airflow at low speed. The PDI core sits close to the condenser and relies on the engine fan to pull air through it.

### 3.4 Exhaust and the DPF

The factory exhaust necks down to 1 7/8 inch and runs through a baffled muffler, and on later trucks through the DPF ([Manta via GTurbo](https://gturbo.com.au/products/vdj79-v8-4-5l-td-pre-dpf-single-cab-ute-2007-to-2016-turbo-back-exhaust)). Manta systems for the single cab, sold by GTurbo:

| Truck | System | Part (Manta) | AUD | Road legal |
|---|---|---|---|---|
| Pre-DPF, 2007 to 2016 | 3 inch turbo-back with cats, stainless, quiet | SSMKTY0004 | 2,680 | Yes, if noise passes |
| Pre-DPF | Same, aluminised steel | MKTY0004 | 2,000 | Yes |
| Pre-DPF | 3 inch turbo-back without cats | MKTY0007 and others | from 1,500 | No. Manta lists it for off-road or race use only |
| DPF, October 2016 on | 3 inch DPF-back, stainless, quiet | SSMKTY0123 | 1,480 | Yes |
| DPF | 4 inch DPF-back, stainless, medium | SSMKTY0191 | 2,310 | Yes, if noise passes |
| DPF | DPF replacement, with or without cat | MKTY0296 and others | 950 to 1,710 | No. Needs the DPF functions removed from the ECU, off-road only |

Sources: [pre-DPF listing](https://gturbo.com.au/products/vdj79-v8-4-5l-td-pre-dpf-single-cab-ute-2007-to-2016-turbo-back-exhaust), [DPF listing](https://gturbo.com.au/products/vdj79-v8-4-5l-td-dpf-single-cab-ute-oct-2016-to-current-turbo-back-dpf-back-exhaust). A DPF delete is not legal on the road in Australia ([70 Series Store](https://jp.70seriesstore.com/en/blogs/information/79-series-landcruiser-exhaust-systems-the-complete-upgrade-guide)), and removing catalytic converters needs certification in NSW ([VSI 06](https://www.rms.nsw.gov.au/documents/roads/safety-rules/standards/vsi-06-light-vehicle-modifications.pdf), item 5).

Keep the factory rear crossover pipe. GTurbo found a larger one slows spool with no gain even at 1,000 Nm, and some aftermarket pipes use mesh flex joints that can fail into the turbo ([booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 43).

Choice: 3 inch stainless with the cats and the quiet muffler (pre-DPF), or 3 inch stainless DPF-back (DPF). Three inch is GTurbo's minimum for its turbo upgrades (booklet page 41). Four inch adds noise risk for no gain at these power levels.

### 3.5 ECU tuning in Australia

The 1VD keeps its factory ECU and is reflashed through the diagnostic port. Tuners found:

| Tuner | What is offered | Price | Source |
|---|---|---|---|
| GTurbo, Balcatta WA, with dealers | Custom remap on its dyno, engine and transmission tuning | Starter package AUD 3,390 supply only, AUD 5,680 supplied, fitted and tuned. The AUD 2,290 gap covers fitting and the remap | [booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 31 |
| HP-F, using the Diesel Tune Australia calibration | Stage 1 to 4. Stage 1 for the DPF 79 includes tune, 4 inch stainless DPF-back exhaust, snorkel head, catch can, clutch upgrade, fitting and dyno | AUD 4,160 | [4x4 Australia](https://www.4x4australia.com.au/gear/stage-1-hp-f-upgrade-landcruiser-79-build) |
| HD Automotive, Brisbane | In-house tunes, quoted at about 650 Nm at 1,800 rpm, pre-DPF and DPF | Not published | [HD Automotive](https://hdautomotive.com.au/blog/2024/01/24/70-series-ecu-remapping-brisbane/) |
| Just Diesel Performance (Just Autos) | Custom tunes with switchable maps, for example one for towing and one for touring | Not published | [Just Diesel Performance](https://www.justdieselperformance.com.au/toyota/70-series-land-cruiser/) |

Assumption: a custom tune with before-and-after dyno runs costs AUD 2,000 at level A and AUD 2,500 at levels B and C, where the turbo change needs more dyno time (estimate from the GTurbo and HP-F prices).

What to ask the tuner to write: peak power capped at 1.20 times the measured stock peak (level A), a towing map with lower torque below about 1,600 rpm to stop lugging, an EGT-based fuel limit (section 3.8), factory light-load maps left alone, and EGR, DPF and catalyst functions left working.

### 3.6 Injector and pump limits

GTurbo finds the factory injectors become a real restriction at about 200 to 230 rwkW and 800 Nm at the wheels. Past that it fits high-flow injectors: +95 % flow for pre-DPF engines and +100 % (Pro 100) for DPF engines, good for 300 rwkW and 1,000 Nm and more ([booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 41). HD Automotive puts the factory-injector limit at about 280 hp and 900 Nm with its turbo ([HD Automotive](https://hdautomotive.com.au/product/vdj330-turbo-70-1vd-toyota-landcruiser/)).

| High-flow option | Pre-DPF AUD | DPF AUD | Source |
|---|---|---|---|
| Nozzle kits only, for a local fuel shop to fit | 1,190 | 2,790 | [GTurbo pre-DPF](https://gturbo.com.au/products/toyota-vdj70-200-non-dpf-high-flow-injector-nozzles), [GTurbo DPF](https://gturbo.com.au/products/toyota-vdj70-200-dpf-100-high-flow-injector-nozzles) |
| Exchange injectors, high-flowed | 2,500 plus AUD 300 core charge | Not offered | [booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 25 |
| Owner's injectors modified | 2,500 | 4,890 | Same |
| Genuine new injectors, high-flowed | 5,890 | 11,900 | Same, and [GTurbo](https://gturbo.com.au/products/toyota-1vd-ftv-injectors) |

The supply pump is the Denso HP4 (section 1.1). No published limit was found. GTurbo's top single-turbo package reaches 400 hp and 1,100 Nm at the wheels on the factory pump type with high-flow injectors ([Warrior package](https://gturbo.com.au/products/vdj70-warrior-package)). GTurbo explains that larger injectors deliver the fuel at lower rail pressure and so ease the pump's load (booklet page 24). It also sells a AUD 180 [rail relief blank](https://gturbo.com.au/products/gturbo-vdj79-200-rail-relief-blank) for high-power builds. Assumption: the new factory pump is enough at all three levels.

Levels A and B stay inside the factory injector limit. Level C needs high-flow injectors.

### 3.7 Gauges

The factory gauges do not show boost, EGT or oil temperature. For a tuned diesel that tows, fit:

| Gauge | Part | Supplier | AUD |
|---|---|---|---|
| Boost, EGT (pyrometer) and water temperature, combined kit | Autometer combo kit | [GTurbo](https://gturbo.com.au/products/autometer-boost-egt-water-temp-combo-kit) | 990 |
| Oil temperature | Autometer oil temperature gauge | Autometer dealer | 220 (assumed equal to the [water temperature gauge](https://gturbo.com.au/products/autometer-water-temp-gauge-40-120c)) |

Fit the EGT probe in the exhaust manifold before the turbo. That reading is faster and 110 to 170 °C hotter than one after the turbo ([BD Diesel](https://us.bddiesel.com/blogs/r-d-blog/safe-towing-temperatures-egt-transmission-coolant-oil-limits)). The probe tip must sit in the middle of the gas stream ([ih8mud](https://forum.ih8mud.com/threads/how-do-i-install-this-egt-probe.906588/), owner). Mount the gauges below the top of the steering wheel. One NSW owner reports that higher mounts such as A-pillar pods are not allowed in NSW ([ih8mud](https://forum.ih8mud.com/threads/a-pillar-gauge-pod-legality-and-uses-for-the-pods.1303627/), owner report, not checked against the rules).

### 3.8 What each level means for sustained towing

**Power the combination needs.** Estimate for 6.6 t, a drag area of 2.5 m² for the ute and a boxy trailer, rolling resistance 0.011, and wheel power at 74 % of crank power. All inputs are estimates, so treat the results as rough.

| Speed | Grade | At the wheels | At the crank |
|---|---|---|---|
| 100 km/h | flat | 52 kW | 70 kW |
| 80 km/h | 4 % | 90 kW | 121 kW |
| 80 km/h | 6 % | 118 kW | 160 kW |
| 100 km/h | 4 % | 124 kW | 167 kW |
| 100 km/h | 6 % | 160 kW | 216 kW |
| 80 km/h | 8 % | 147 kW | 199 kW |

Speed held on a 6 % grade at full power: stock 151 kW about 76 km/h, level A 181 kW about 88 km/h, level B 230 kW about 105 km/h, level C 300 kW about 125 km/h (calculated). On the flat, any level loafs. On long grades, power is used for minutes at a time, and that is where heat builds.

**Heat.** A diesel at full load sends heat to the coolant and exhaust roughly in step with the fuel it burns. So holding 230 kW up a long grade puts about 50 % more heat into the radiator than the factory 151 kW (estimate). The factory cooling system was sized for 151 kW. This is why the rebuild includes a new radiator and fan clutch, why levels B and C need extra cooling margin, and why the tune needs a temperature-based limit.

**Limits to tune and drive to.** These are general diesel towing figures, not 1VD data:

| Reading | Sustained | Action point | Source |
|---|---|---|---|
| EGT before the turbo | up to 650 to 675 °C | about 730 °C is a common OEM abort point | [BD Diesel](https://us.bddiesel.com/blogs/r-d-blog/safe-towing-temperatures-egt-transmission-coolant-oil-limits), [HP Academy forum](https://www.hpacademy.com/es/foro/puesta-a-punto-practica-del-diesel-1/show/afr-vs-exhaust-temps) |
| Coolant | 90 to 104 °C | over 107 °C for long means an airflow problem | BD Diesel |
| Oil | 99 to 116 °C when towing | over 121 °C sustained means a cooling review | BD Diesel |

Assumption for the tune: start pulling fuel at 650 °C before the turbo and hold no more than 700 °C. Do not lug the engine below about 1,600 rpm under full load, because EGT spikes there (BD Diesel).

**Piston, ring and head gasket life.** No published life data for a tuned 1VD was found. What is known: the pistons are cast aluminium (TIK in the NVP kit), the head bolts are TTY and no head studs exist (section 2.1), and GTurbo claims 80,000 km of high-load use at 70 % over factory power on its test truck (section 3.2). Assumptions used here:

- Level A: life close to a stock engine's, because peak power rises 20 % and the EGT limit caps the heat.
- Level B: shorter but acceptable life if the EGT limit is enforced. Head gasket and ring wear are the first risks.
- Level C: low margin for hours at full load. Cylinder pressure and heat rise about twice as far over stock as at level A, on the same gaskets and bolts.

### 3.9 The three levels

Crank figures are estimates converted from wheel figures at 74 % (section 3.1). Costs are the engine side only: the AUD 19,279 rebuild plus the power parts. Section 5 itemises level A.

| | Level A (recommended) | Level B | Level C |
|---|---|---|---|
| Crank power | up to 181 kW (+20 %) | 220 to 250 kW | about 300 kW |
| Crank torque | about 650 Nm | about 850 Nm | about 1,050 Nm |
| At the wheels | 1.20 times the stock reading, about 115 to 145 rwkW | about 165 to 185 rwkW | about 220 to 230 rwkW |
| Power parts | VD-G333 turbo, PDI front mount, 3 inch exhaust, capped tune, gauges | Same parts, retuned | VD-G400Ti turbo, high-flow injectors, airbox, power pipe, front mount, 3 inch exhaust, tune, gauges |
| Engine side, pre-DPF | AUD 32,208. Cheapest version AUD 27,028 (rebuilt standard turbo, no front mount, aluminised exhaust) | AUD 32,708 plus about AUD 2,000 certification | AUD 38,733 plus certification (section 4.6) |
| Extra for a DPF truck | about AUD 3,600 | about AUD 3,600 | about AUD 4,700 |
| Driveline the engine demands (report 15) | Clutch for about 650 Nm. The factory clutch slips beyond about 500 Nm | Clutch and gearbox for about 850 Nm | Clutch for over 1,000 Nm (for example the 1,600 Nm [NPC kit](https://gturbo.com.au/products/vdj79-extra-heavy-duty-clutch-kit-billet-flywheel-1300nm), AUD 2,178) and a gearbox well beyond factory torque |
| Injectors | Factory type, new | Factory type, new, near their limit | High-flow |
| Sustained towing | Good margin. Holds about 88 km/h on 6 % at 6.6 t | Acceptable with the EGT limit and new radiator | Low margin for hours at full load |
| Legal path in NSW | No certificate. Superseded: LA4 certificate under VSI 06 Rev 4 item 6, about AUD 2,000 | LA4 certificate | LA4 certificate, not realistic for this use |

The level A hardware is the level B hardware. Moving from A to B later costs a retune and the certificate, plus the driveline work. That is why level A uses the VD-G333 and the front mount rather than the cheapest parts.

## 4. Legality in NSW

*Superseded in part, 20 Nov 2026: this section reads the 2013 revision of VSI 06. Rev 4, in force since 1 July 2026, adds item 6, so every tune that alters emissions output needs a VSCCS certificate, level A included. Each passage below that says level A needs none is marked. VEHICLE.md's legal section is current.*

### 4.1 Which rules apply

NSW lists the modifications that need a VSCCS certificate in an Order, summarised in Vehicle Standards Information 6 ([VSI 06](https://www.rms.nsw.gov.au/documents/roads/safety-rules/standards/vsi-06-light-vehicle-modifications.pdf)). VSCCS is the Vehicle Safety Compliance Certification Scheme, which licenses private certifiers. Two items cover this build:

- **Item 2.** Fitting a turbo the maker never offered, or raising the original power by more than 20 %. VSI 06's own example: a 100 kW vehicle modified to more than 120 kW needs certification.
- **Item 5.** Engine or exhaust changes that increase emissions above the ADR levels for the vehicle. Examples that need certification include non-original fuel injection equipment, removing the EGR, crankcase ventilation or catalytic converters, and replacing the original ECU. Examples that do not: exhausts, intakes and intercoolers that keep the emission control equipment. If non-original engine control parts are fitted, the owner must show emissions are retained. VSI 06 adds that certifiers may ask for a TfNSW emissions test, free at the Botany or Penrith heavy vehicle inspection stations, or a 4 or 5 gas analyser test at a repairer.

The national code, VSB 14 Section LA, sets how a certifier assesses the work ([VSB 14 Section LA, version 2.0, copy](https://dl.icdst.org/pdfs/files1/5c5daf35fb353984f640c166f77157fd.pdf)). Its codes:

- LA1: an equivalent replacement engine, at most 20 % more power or mass.
- LA2: a performance replacement engine.
- LA3: fitting a turbo or supercharger the engine or vehicle maker did not offer. It excludes engines that came turbocharged.
- **LA4: modifying the original engine**, including changes to engine management and induction. VSB 14 says these are generally treated like a performance engine conversion.

So a VDJ79 with a bigger turbo and a tune over 20 % is an **LA4** job, not LA2 or LA3. The VDJ79 came with a turbo, so LA3 does not apply.

VSB 14 is stricter in wording than VSI 06. It says that if an engine is modified it must be certified under an LA code. Assumption: NSW registration follows its own Order (VSI 06), so a level A build that stays under 20 % and does not raise emissions needs no certificate. *Superseded 20 Nov 2026: VSI 06 Rev 4 item 6 needs a VSCCS certificate for this tune, the LA4 certificate at about AUD 2,000 (estimate). See the note above.*

### 4.2 What LA4 certification involves for a modified diesel

From [VSB 14 Section LA](https://dl.icdst.org/pdfs/files1/5c5daf35fb353984f640c166f77157fd.pdf) clauses 2 and 3 and code LA4:

- **Emissions.** The vehicle must still meet the emission ADR it was built to. Changes to engine management need proof under code LT3, the gaseous emissions test in VSB 14 Section LT. An aftermarket calibration does not prove compliance unless that combination has been tested (clause 3.1.3). The VDJ79 was built to Euro 4 before the October 2016 update ([Drive](https://www.drive.com.au/news/toyota-landcruiser-70-series-specifications/)), which is ADR 79/02 ([TfNSW ADR emission table](https://www.transport.nsw.gov.au/system/files/media/documents/2023/aust-design-rules-emission-standards.pdf)). After it, the truck is Euro 5 ([4x4 Australia](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). ADR 79/04 applies Euro 5 to all new light vehicles built from 1 November 2016 ([ADR 79/04 explanatory statement](https://www.legislation.gov.au/F2012L01035/asmade/2012-05-15/es/original/pdf)). In NSW the certifier can accept the free TfNSW test (section 4.1).
- **Noise.** A modified exhaust needs proof under code LT4, the noise test, or an ADR test. The NSW in-service limit for vehicles built to ADR 83/00 is the vehicle's ADR 83/00 "signature" stationary noise level plus 5 dB(A). For compliance plates on or before 1 September 2011 it is the higher of that and the Schedule 1 level, which is 90 dB(A) for vehicles built from 1983 ([NSW EPA](https://www.epa.nsw.gov.au/sites/default/files/21p3040-managing-motor-vehicle-noise.pdf)). The VDJ79's signature level was not found. Assumption: a Manta "quiet" system keeps the truck within it.
- **Brakes.** For a more powerful engine, VSB 14 requires "any necessary upgrading of equipment, e.g. brakes" (clause 2.1, written for engine conversions). LA4 says engine modifications are treated on the same basis as a performance engine conversion. Assumption: the certifier asks for brake evidence at the upgraded GVM. Report 16 covers the brakes.
- **Driveline.** Clause 2.1 also says the power and torque must not exceed the capacity of the vehicle driveline. Assumption: the certifier asks for ratings or evidence for the clutch, gearbox, transfer case, tailshafts and axles at the tuned torque. Report 15 covers this.
- **Installation.** Fasteners to VSB 14 Appendix A, guarding, fuel lines clear of the turbo and exhaust, sound workmanship, and engine mounts that take the torque (LA4 checklist). Intercoolers must not need structural changes at the front that affect occupant protection or move airbag sensors (LA1 requirements, applied the same way). The PDI front mount fits without cutting ([booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 28).
- The pre-ADR safety upgrades in LA4 (seat belts, dual brakes, collapsible column) do not apply. The VDJ79 already meets the ADRs.

### 4.3 The VSCCS process in NSW

1. Choose a certifier licensed in category **LC4**: light commercial vehicles, engine, fuel, intake or exhaust systems ([VSCCS Bulletin 1](https://www.transport.nsw.gov.au/system/files/media/documents/2025/VSFC01-VSCCS-Bulletin-1.pdf)). Bulletin 1 lists them.
2. Talk to the certifier before starting. They may ask for photos of the work or for inspections at stages ([NSW Government](https://www.nsw.gov.au/topics/vehicle-registration/how-to/used-or-secondhand/modified-non-standard-vehicles)).
3. The certifier inspects, assesses and tests. If the vehicle complies, they issue a VSCCS compliance certificate (same page).
4. Take the certificate and inspection papers to a service centre to update the registration record. The certificate does not expire (same page).

If report 16's GVM upgrade takes the ute above 4.5 t, it becomes a heavy vehicle and needs an Approved Vehicle Examiner under the national heavy vehicle law instead (Bulletin 1).

Cost. Certifiers set their own fees and none was found published. Assumption: AUD 2,000 for an LA4 certificate, including the noise test (estimate). Dyno sheets come with the tune. The TfNSW emissions test is free (VSI 06). No Australian price was found for a full ADR 79 laboratory emissions test. Assumption: AUD 10,000 or more (estimate).

### 4.4 Insurance

TfNSW warns that insurance could be void if modifications are not assessed and certified, and tells owners to tell their insurer about every modification and its certificate ([NSW Government](https://www.nsw.gov.au/topics/vehicle-registration/how-to/used-or-secondhand/modified-non-standard-vehicles)). Disclose the level A tune, turbo, intercooler and exhaust too, even with no certificate. Keep the dyno sheets and the emissions test result with the policy.

### 4.5 What certifiers certify, and is 220 to 300 kW realistic?

No public record was found of a NSW LA4 certificate for a tuned VDJ79 at any power. The tuner and turbo pages read for this report sell parts, tunes and dyno results and do not offer certification ([GTurbo](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf), [HD Automotive](https://hdautomotive.com.au/blog/2024/01/24/70-series-ecu-remapping-brisbane/), [Just Diesel Performance](https://www.justdieselperformance.com.au/toyota/70-series-land-cruiser/), [4x4 Australia on HP-F](https://www.4x4australia.com.au/gear/stage-1-hp-f-upgrade-landcruiser-79-build)). Exhaust sellers mark their DPF and catalyst deletes as off-road only ([Manta via GTurbo](https://gturbo.com.au/products/vdj79-v8-4-5l-td-dpf-single-cab-ute-oct-2016-to-current-turbo-back-dpf-back-exhaust)). This suggests most tuned 79s on the road carry no certificate. That is the owner's risk and not a path this report recommends.

- **Level B, 220 to 250 kW: possible, not assured.** Its strengths: the factory ECU, EGR, catalysts or DPF all stay, the exhaust is quiet, and the injectors are the factory type. Its risks: the certifier may not accept a TfNSW test and may want laboratory ADR 79 evidence, which would cost AUD 10,000 or more (estimate). The driveline must also be shown to take about 850 Nm. Assumption: talk to an LC4 certifier with the level A truck built, and decide on level B then.
- **Level C, about 300 kW: not realistic for this use.** High-flow injectors are non-original fuel injection equipment, an explicit item 5 example. That makes laboratory emissions evidence likely. The driveline needs to take over 1,000 Nm and the brakes will draw scrutiny at a 3.9 t GVM.

### 4.6 Legal path and cost by level

| Level | Certificate | Evidence to hold | Cost |
|---|---|---|---|
| A, up to 181 kW | VSCCS LA4 from an LC4 certifier (VSI 06 Rev 4 item 6, superseding this report's "none" under items 2 and 5) | Same-dyno stock and tuned sheets showing at most 1.20 times stock power. TfNSW emissions test or the Interim NSW procedure result. Catalysts or DPF, EGR and crankcase ventilation all working. Quiet exhaust. Insurer told | About AUD 2,000 (estimate) |
| B, 220 to 250 kW | VSCCS LA4 from an LC4 certifier | As A, plus LT4 noise test, brake and driveline evidence, and the emissions evidence the certifier asks for | About AUD 2,000. About AUD 12,000 or more if a laboratory test is needed (estimates) |
| C, about 300 kW | VSCCS LA4, unlikely to be granted | As B, with laboratory emissions evidence expected | About AUD 12,000 or more, before any brake or driveline changes the certifier asks for (estimate) |

### 4.7 Victoria, the fallback

Victoria also applies VSB 14 and uses VASS signatories to approve modifications ([VSI 8, copy](https://www.morrisminorvic.org.au/assets/CPS2015/VSI8_VehModGuide.pdf), section 6 covers VSB 14 code LA). Its current rules for diesel engine changes were not checked for this report. Assumption: the same 20 % threshold and LA4 path apply.

## 5. Recommended build and total

Level A, pre-DPF truck. Every line is in `14-engine-parts.yaml` with its link.

| Group | Items | AUD |
|---|---|---|
| Rebuild (section 2.6) | NVP kit, machine shop, timing set, oil pump, glow plugs, mounts, injectors, fitting kit, supply pump, pre-filter, fuel filter, radiator, water pump, thermostat, fan clutch, hoses, coolant, sundries | 19,279 |
| Turbo | GTurbo VD-G333 Titan, journal bearing | 4,290 |
| Turbo gaskets | GTurbo VDJ70 turbo gasket kit | 299 |
| Turbo intake pipe | New genuine pipe, by VIN (estimate). The old plastic pipe softens with breather oil | 250 |
| Intercooler | PDI front mount, twin throttle, pre-DPF, A IC AA T3F-2 | 2,200 |
| Exhaust | Manta 3 inch stainless turbo-back with cats, quiet, SSMKTY0004 | 2,680 |
| Tune | Custom, capped at 1.20 times stock, towing map, EGT limit, before-and-after dyno (estimate) | 2,000 |
| Gauges | Autometer boost, EGT and water combo, plus oil temperature (estimate) | 1,210 |
| Legal | TfNSW emissions test | 0 |
| **Total** | | **32,208** |

*Superseded 20 Nov 2026: the LA4 certificate for the reflash adds about AUD 2,000 (estimate) under VSI 06 Rev 4 item 6, so this total becomes about AUD 34,208. VEHICLE.md carries it as line TL05.*

About a third of the total (about AUD 11,000) is estimates: the machine shop, the Toyota dealer parts without a published price, the pre-filter, the intake pipe, the tune and one gauge.

Variants:

- **DPF truck:** about AUD 35,800. The piezo injectors add AUD 4,966. The DPF fitting kit saves AUD 130 and the 3 inch DPF-back exhaust (SSMKTY0123) saves AUD 1,200.
- **Cheapest reliable version:** about AUD 27,000. It swaps in the rebuilt standard turbo (AUD 1,990), drops the front mount and uses the aluminised exhaust (AUD 2,000). It gives up the level B upgrade path and some towing heat margin.
- **Reuse after testing:** the injectors (specialist service about AUD 1,600 instead of AUD 4,290, estimate), the supply pump, the radiator and the oil pump save up to about AUD 6,600 together. Each one reused is a 400,000 km part on a rebuilt engine.

Not in the total: balancing (AUD 400, optional), the clutch and anything else report 15 specifies, and the GVM and brake work in report 16.

Build notes that protect the engine:

1. Strip, measure piston protrusion per bank, then order the head gasket grades and kit sizes.
2. Torque the pre-DPF injectors to 18 Nm, air-test the leak-off rail, and watch the oil level for the first 1,000 km ([GTurbo booklet](https://cdn.shopify.com/s/files/1/0823/4241/2531/files/1VD-FTV-VDJ70-Booklet-v1_4c.pdf) page 42).
3. Refit the support pole in the oil filter housing at every oil change (same page).
4. Run the turbo actuator breather hose up into the engine bay (same page).
5. Keep the factory rear crossover pipe (page 43).
6. Flush the fuel tank and lines before the new pump and injectors see fuel.
7. Run the engine in on the factory calibration. Then put it on the dyno for the stock baseline, tune it on the same dyno, and keep both sheets.
8. Book the TfNSW emissions test, then tell the insurer about every change.

Upgrade path to level B: the same parts, a retune to 220 to 250 kW, the LA4 certificate (about AUD 2,000) and report 15's driveline for about 850 Nm. Engine side about AUD 34,700.

## Open questions

Each ends with the assumption this report uses.

1. Pre-DPF or DPF truck? Reports 15 and 16 may favour the 2016 single cab chassis and stability control. Assumption: pre-DPF, built 2010 to October 2016. A DPF truck adds about AUD 3,600 to the engine side. *Superseded 20 Nov 2026: a DPF truck built from 01/2017 (decision log 11:25).*
2. Does NSW need a certificate for a different turbo on an engine that came turbocharged, when power stays within 20 % and emissions do not rise? Assumption: no, because VSI 06 items 2 and 5 are the only engine triggers. *Superseded 20 Nov 2026: Rev 4 item 6 adds the reflash as a trigger, so the tune needs a certificate whatever the turbo. A turbo, intercooler or exhaust that keeps the emission controls still needs none of its own (item 5).*
3. Will an LC4 certifier accept the free TfNSW emissions test for an LA4 certificate at level B? Assumption: unknown until asked with the built truck. Plan for level A, and treat level B as a later option.
4. Is the free TfNSW emissions test at Botany and Penrith still offered? Assumption: yes, as VSI 06 states. If not, a 4 or 5 gas analyser test at a repairer, about AUD 200 (estimate).
5. What is the VDJ79's ADR 83/00 stationary noise signature level? Assumption: the Manta "quiet" system stays within signature plus 5 dB(A). Test it before the first registration inspection.
6. How much torque can the clutch, gearbox and the rest of the driveline take? Assumption: the tune caps torque at report 15's rating, with 650 Nm as the level A target.
7. What do the dealer-only Toyota parts cost, and what are their numbers? Assumption: the section 2 and 5 estimates, about AUD 4,100 in total, within 30 %. Order by VIN.
8. What will a machine shop charge for a 1VD? Assumption: AUD 4,200, within 25 %.
9. What wheel-to-crank ratio does the chosen truck show? Assumption: 74 %. The legal test uses the truck's own stock baseline, so the ratio matters only for the crank estimates.
10. Does the factory supply pump suffice at level C? Assumption: yes, as GTurbo's 400 hp package runs the factory pump type. Not needed at level A.
11. Does a worn vacuum pump add to oil use on early engines? Assumption: check it during the rebuild and replace it if oil passes it, about AUD 600 (estimate, not in the total).
12. Does the front mount cut radiator airflow when towing slowly in heat? Assumption: no, because the engine fan pulls through both cores. Watch the coolant gauge on the first long tow. The fallback is the AUD 1,895 fan kit on the factory top mount.
13. Will insurers cover a tuned 79 at level A? Assumption: yes, with full disclosure. Get quotes before buying the parts.
14. Do Victoria's rules match NSW for the fallback? Assumption: the same 20 % threshold and LA4 path.
15. What does a laboratory ADR 79 emissions test cost? Assumption: AUD 10,000 or more.
16. What does an LA4 certificate cost? Assumption: AUD 2,000, including the noise test.

## Could not verify

- Toyota's oil consumption bulletin was read only as a search extract, because Scribd blocks reading. Its date and the engines it covers are unknown.
- The Club 4X4 tuning article looped on redirects and the eng-tips thread returned 403. Only their search extracts were read.
- The Direction Plus PL625DPK page returned 403, so the pre-filter price comes from a similar kit.
- No source specific to the 1VD was found for oil cooler, valley coolant or rear main seal leaks.
- The factory turbo is a GTA2359V by two sources and a GT2559V by GTurbo.
- GTurbo prints two prices for the VD-G400Ti (AUD 4,290 and 4,980). UFI publishes no price for the VDJ330.
- All turbo, tune and injector results are the sellers' own dyno figures.
- The wheel-to-crank ratio is an estimate from three stock dyno readings. The towing power table uses estimated drag area and rolling resistance.
- The EGT, coolant and oil limits are general diesel towing figures from a US parts maker and a tuning forum, not 1VD data.
- VSB 14 Section LA was read from a third-party copy of version 2.0 (January 2011). The official page did not load, and a newer version was not checked. Section LT, with the LT3 and LT4 procedures, was not read.
- VSI 06 is revision 3 (November 2013), later updated to name TfNSW. Whether the emissions test at the heavy vehicle inspection stations is still free was not confirmed.
- No VSCCS certifier fees were found. The LC4 certifiers in Bulletin 1 were not counted.
- The VDJ79's ADR 83/00 noise signature level was not found.
- The pre-2016 truck's ADR 79 version is inferred from Toyota's "Euro IV" description, not checked in the RVCS records.
- Victoria's VSI 8 was read only from a 2015 third-party copy listing.
- The head gasket number comes from a Lexus listing for the same engine family, the timing chain numbers from an AliExpress listing and the fuel filter number from an eBay listing. Fitment to the VDJ79 is unconfirmed for all three.
- The Natrad radiator price came from a search extract. The product page did not show its core size or material.
- The claim that A-pillar gauge pods are not allowed in NSW is an owner report.
- Changes at the 2012 facelift were not checked for the engine.
- Whether the DPF truck's own EGT sensors can be read for monitoring was not checked.

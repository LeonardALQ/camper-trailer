# 15: LandCruiser 79 V8 driveline and reliability refresh

Note added 20 Nov 2026, after the vehicle plan (VEHICLE.md). The plan follows this report: a new genuine Aisin H152F and the NPC Super HD Organic 1300 clutch, with the tune limiting torque in low range, first and reverse to about 450 to 500 Nm. VEHICLE.md lists rebuilding the truck's own H152F (Marks 4WD kit GBK9) as one of six cuts that keep it reliable, only if the gearbox passes inspection. The trailer it tows is now 3,100 kg at its plate (TRAILER.md), not 3,500 kg, so every sum in VEHICLE.md uses 3,100 kg. The parts list for this report is published as `research/15-driveline-parts.yaml`.

Report 15 for the LandCruiser 79 single cab V8 (VDJ79) that replaces the Cayenne as the tow vehicle. It covers the clutch, gearbox, transfer case, tailshafts, diffs, axles and hubs, and the rest of the refresh a 400,000 km vehicle needs. The engine is in report 14. The GVM kit, springs, brakes, wheels and tyres are in report 16. Research date 20 Nov 2026.

## Recommendation

Sized for report 14's expected range of 180 to 300 kW and 650 to 1,000 Nm at the crank, towing a 2.5 to 3 t trailer at a combined 6.3 to 6.8 t.

Clutch: the NPC Super Heavy Duty Organic 1300 kit with its matched billet flywheel (NPC7751-1D, AUD 1,818.50), plus a new master cylinder, slave cylinder, braided line, fork and pivot. The organic disc takes up a heavy trailer smoothly, where ceramic discs can shudder. The kit covers the whole torque range and replaces the 400,000 km flywheel. If report 14 lands at or below about 800 Nm, the Xtreme Outback X-Series organic (KTY29590-1TX, AUD 2,211.45) drives better, with a lighter self-adjusting pedal.

Gearbox: keep the manual and fit a new genuine Aisin H152F (AUD 3,840). It is the factory box from the late-2016 update and bolts into every VDJ79 with no NSW certification. It costs about the same as a specialist rebuild of a worn box and every part is new. Toyota publishes no torque rating for it, so the plan protects it with a tune that caps torque in low range, first and reverse. The AB60 six-speed automatic is the better towing gearbox, but it costs about AUD 20,000 to 30,000 fitted and is rated at 900 Nm. Choose it only if the budget rises and the engine stays at or below about 800 Nm.

Driveline: rebuild the HF1A transfer case (Koyo kit, AUD 653) and both tailshafts. Keep the factory diff ratio and buy a truck with factory diff locks. Rebuild both swivel hubs and renew all four wheel bearings. Ask report 14's tune to hold low range near stock torque (about 450 to 500 Nm), because low range multiplies 1,000 Nm into 11,270 Nm at the transfer output, 2.3 times stock, and the 8-inch front diff and CV joints take it. Fix the rear housing and the 95 mm narrower rear track as part of report 16's GVM upgrade, or add Multidrive's strengthened wide-track housing (AUD 6,570 installed).

Refresh: steering ends, damper and a reconditioned box. Front bushes and greasable shackles. A chassis crack check at the rear spring hangers and behind the cab, rust treatment and new cab mounts. Alternator, starter, batteries and earth straps. Fuel hoses, an air conditioning service and all fluids.

Total for this report: AUD 16,143 required, or AUD 18,543 with a 15% contingency for what the inspection finds. Add AUD 6,570 if the rear housing is not in the GVM kit. With the engine at about AUD 15,000 and report 16's GVM kit, brakes and tyres on top, the vehicle work will land near AUD 45,000 to 55,000. Plan on about AUD 50,000.

Which truck: on driveline grounds, a single cab GXL built after the late-2016 update. It already has the H152F, a thicker chassis with seven crossmembers, factory diff locks, and it suits the Lovells Elite GVM kit, which starts from January 2017 builds. Report 14 weighs that against the DPF those trucks carry, and report 16 sets the build date.

What could block the plan: the budget, the H152F's unpublished torque limit, whether the tune can cap low-range torque, and whether report 16's GVM kit includes a stronger rear housing.

## 1. Clutch and flywheel

### What the VDJ79 has

The VDJ79 has a solid, single-mass flywheel. Xtreme Outback's heavy-duty kits bolt "directly to the factory flywheel", and its kits with a replacement flywheel exist for owners who do not want to resurface the old one or whose flywheel is worn past the resurfacing limit ([Xtreme Outback 70 Series guide](https://cdn.shopify.com/s/files/1/0633/1249/4762/files/Xtreme_Outback_70_Series_Upgrades_Application_Guide.pdf?v=1726817425), [KTY30593-1DX page](https://www.xtremeoutback.com.au/products/kty30593-1dx-stage-1x-dual-friction-extra-heavy-duty-clutch-kit)). The factory clutch is sized for the stock 430 Nm. Unsealed 4X4 lists clutch wear on tuned trucks as a common 70 Series fault ([Unsealed 4X4, July 2026](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)).

### Heavy-duty kits sold in Australia

Two terms first. Xtreme Outback quotes a "recommended torque capacity", which includes its factor of safety, and a higher peak capacity. PDI quotes a "rated" and a "peak" figure in the same way. Clamp load is the force the pressure plate puts on the disc.

| Kit | Part number | Disc | Clamp load | Torque, recommended or rated / peak | Flywheel | Price (AUD) |
|---|---|---|---|---|---|---|
| [Xtreme Outback Stage 1](https://www.xtremeoutback.com.au/products/heavy-duty-clutch-kit-stage-1-sprung-organic-kty30018-1a) | KTY30018-1A | Sprung organic | 25% over factory | 590 / 750 Nm | Factory | 1,055.04 |
| [Xtreme Outback Stage 1X organic](https://www.xtremeoutback.com.au/products/extra-heavy-duty-clutch-kit-stage-1x-extra-heavy-duty-sprung-organic-kty30093-1ax) | KTY30093-1AX | Sprung organic | 1,300 kg | 750 / 930 Nm | Factory. [KTY30593-1AX](https://www.xtremeoutback.com.au/products/extra-heavy-duty-clutch-kit-stage-1x-extra-heavy-duty-sprung-organic-kty30593-1ax) adds a new one for 1,912.80 | 1,524.61 |
| [Xtreme Outback Stage 1X dual friction](https://www.xtremeoutback.com.au/products/kty30093-1dx-stage-1x-dual-friction-extra-heavy-duty-clutch-kit) | KTY30093-1DX | Organic one side, ceramic the other | 1,300 kg | 1,060 / 1,320 Nm | Factory. KTY30593-1DX adds a new one for 2,016.14 | 1,627.95 |
| [Xtreme Outback X-Series organic](https://www.xtremeoutback.com.au/products/kty29590-1tx-xtreme-outback-x-series-organic) | KTY29590-1TX | Sprung organic | 1,600 kg, self-adjusting | 870 / 1,080 Nm | New S45 steel, included | 2,211.45 |
| [Xtreme Outback X-Series dual friction](https://www.xtremeoutback.com.au/products/kty29590-1dx-xtreme-outback-x-series-dual-friction) | KTY29590-1DX | Organic and ceramic | 1,600 kg, self-adjusting | 1,225 / 1,530 Nm | New S45 steel, included | 2,328.15 |
| [PDI Powerdrive (GTurbo)](https://gturbo.com.au/products/pdi-powerdrive-1300nm-clutch-landcruiser) | PDI-PD-CLUTCH-1VD-850 | Organic copper mix | 1,180 kg | 725 / 850 Nm | Factory | 1,300.00 |
| PDI Powerdrive (same page) | PDI-PD-CLUTCH-1VD-935 | Organic copper mix | Not stated | Not stated / 935 Nm | Factory | 1,330.00 |
| PDI Powerdrive (same page) | PDI-PD-CLUTCH-1VD-1315 | Organic copper mix | 1,650 kg | 1,120 / 1,315 Nm | Factory | 1,800.00 |
| [NPC Stage 1 HD organic (GTurbo)](https://gturbo.com.au/products/npc-stage-1-heavy-duty-organic-clutch-kit-suit-factory-flywheel-toyota-landcruiser-2007-current-npc7751-1a) | NPC7751-1A | Organic | Not stated | Not stated | Factory | 983.00 |
| [NPC Super HD organic 1300 (GTurbo)](https://gturbo.com.au/products/npc-super-heavy-duty-organic-1300-clutch-flywheel-kit-toyota-landcruiser-2007-current-npc7751-1d) | NPC7751-1D | Organic | Not stated | 1,300 Nm, basis not stated | Matched billet, included | 1,818.50 |
| [NPC Super HD organic 1600 (GTurbo)](https://gturbo.com.au/products/npc-super-heavy-duty-organic-1600-clutch-flywheel-package-toyota-landcruiser-2007-current-npc7751-1d-1) | NPC7751-1D (1600 package) | Organic | Not stated | 1,600 Nm, basis not stated | Matched billet, included | 2,213.00 |

Prices are the web prices on 20 Nov 2026. The PDI kits need a sound factory flywheel, so add resurfacing or a new flywheel. Xtreme Outback's price gap between kits with and without a flywheel is about AUD 390 (1,912.80 less 1,524.61), which is a fair estimate for a new factory-type flywheel. HD Automotive, which sells new H152 gearboxes, calls the NPC 1300 and 1600 kits the best LandCruiser clutch it can fit ([HD Automotive](https://hdautomotive.com.au/blog/2024/02/15/toyota-land-cruiser-gearbox-options/)). That is a retailer's view.

### Which disc for heavy towing

Choose an organic disc. Xtreme Outback says the ceramic face on its dual-friction discs adds grip and heat capacity "but will also introduce some shudder", with a more direct engagement ([KTY29590-1DX page](https://www.xtremeoutback.com.au/products/kty29590-1dx-xtreme-outback-x-series-dual-friction)). A 6.3 to 6.8 t combination makes the clutch slip hardest during hill starts and while reversing the trailer. An organic disc slips smoothly and recovers after it gets hot, which PDI also claims for its copper-mix disc.

### Sizing across 650 to 1,000 Nm

| Engine torque (report 14) | Kits with an organic disc and margin | Notes |
|---|---|---|
| 650 to 750 Nm | Xtreme Outback X-Series organic, PDI 1315, NPC 1300 | The Stage 1X organic (750 Nm recommended) has no margin left |
| 750 to 870 Nm | Xtreme Outback X-Series organic, PDI 1315, NPC 1300 | The X-Series self-adjusting plate keeps pedal effort steady as the disc wears |
| 870 to 1,000 Nm | PDI 1315 (1,120 Nm rated), NPC 1300, NPC 1600 | Only these organic kits have published figures above 1,000 Nm |

Recommendation: the NPC Super Heavy Duty Organic 1300 kit with its matched billet flywheel (NPC7751-1D, AUD 1,818.50 from [GTurbo](https://gturbo.com.au/products/npc-super-heavy-duty-organic-1300-clutch-flywheel-kit-toyota-landcruiser-2007-current-npc7751-1d)). It covers the whole torque range with an organic disc. It replaces the 400,000 km flywheel instead of relying on it. NPC builds it in Australia to order, with 2 to 4 weeks lead time. HD Automotive recommends NPC's 1,300 Nm kit with the new H152 gearboxes it sells, the box chosen in section 2. NPC warns the pedal is firmer than factory.

The PDI 1315 is the alternative. It publishes a rated figure (1,120 Nm) below its peak and costs about the same once a new flywheel is added. PDI says its pedal needs 33 to 37% more effort. If report 14 lands at or below about 800 Nm, the Xtreme Outback X-Series organic (KTY29590-1TX) is the best-driving choice. It comes with a new flywheel, slave cylinder and braided line, and its self-adjusting plate keeps the pedal lighter.

### Hydraulics and small parts

Xtreme Outback recommends renewing the clutch actuation parts on high-kilometre vehicles ([guide](https://cdn.shopify.com/s/files/1/0633/1249/4762/files/Xtreme_Outback_70_Series_Upgrades_Application_Guide.pdf?v=1726817425)). Fit with the clutch:

- master cylinder, Xtreme Outback [MCTY161](https://www.xtremeoutback.com.au/products/mcty161-clutch-master-cylinder), AUD 131.38, listed in its VDJ guide
- slave cylinder, Toyota genuine by VIN, AUD 150 (estimate)
- braided clutch line, [NPC VDJ line](https://gturbo.com.au/products/npc-braided-line-vdj-toyota-landcruiser-2007-current-b-line-vdj), AUD 154
- clutch fork and pivot ball, Xtreme Outback [ATFKTY28-08](https://www.xtremeoutback.com.au/products/atfkty28-08-clutch-fork-kit), AUD 319.81
- release and spigot bearings if the kit lacks them, AUD 120 (estimate)
- gearbox input shaft seal, [genuine, HD Automotive](https://hdautomotive.com.au/product/genuine-h151-h152-gearbox-input-shaft-seal-suitable-for-toyota-landcruiser-70-80-100-series/), AUD 16.50
- new flywheel bolts, AUD 60 (estimate)

The engine's rear main seal belongs to report 14. Replace it while the gearbox is out.

One driving habit protects the clutch more than any part. Use low range for hill starts and for reversing the trailer. Low range multiplies torque by 2.488 ([Toyota spec sheet, 2014](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf)), so the clutch barely slips.

## 2. Gearbox

### Which gearbox the VDJ79 has

Every V8 70 Series has a five-speed manual. No factory automatic was offered with the V8 ([Toyota Australia, 2023](https://www.toyota.com.au/discover/news/legendary-toyota-landcruiser-70-series-range-upgraded)). The box changed with the late-2016 update, which also added the DPF.

| Build | Gearbox | 1st | 2nd | 3rd | 4th | 5th | Reverse | Source |
|---|---|---|---|---|---|---|---|---|
| 2007 to late 2016 | H150F | 4.529 | 2.464 | 1.490 | 1.000 | 0.881 | 4.313 | [Toyota spec sheet, Sep 2014](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf) |
| Late 2016 on | H152F | 4.529 | 2.294 | 1.490 | 1.000 | 0.750 | 4.313 | [Toyota spec sheet, Sep 2023](https://brookshire.com.au/BrooksHire/media/Media/Spec%20Sheets/LandCruiser-70-Spec-Sheet.pdf) |

Both feed the same HF1A part-time transfer case, with ratios of 1.000 in high range and 2.488 in low range (same sources). 4X4 Australia reported that the 2016 update gave the box taller second and fifth gears, so the truck cruises at "a tad under 2000rpm" at 100 km/h in top ([4X4 Australia, Oct 2016](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). HD Automotive confirms the H150 in early VDJ79s and the H152 from 2016, and says the H152 is a straight bolt-in for both ([HD Automotive](https://hdautomotive.com.au/blog/2024/02/15/toyota-land-cruiser-gearbox-options/)).

### Torque capacity and known failures

Toyota and Aisin publish no torque rating for the H15x boxes. The evidence is indirect:

- HD Automotive says the H150, H151 and H152 are "tough gearboxes and all similar in terms of strength", much stronger than the R151 in six-cylinder 79s ([HD Automotive](https://hdautomotive.com.au/blog/2024/02/15/toyota-land-cruiser-gearbox-options/)).
- Australian clutch makers sell 1,300 to 1,600 Nm kits for this box, and HD Automotive pairs a new H152 with a 1,300 Nm clutch as a package. That suggests tuners accept the box at those torque levels, but it is not a rating.
- The common fault is synchro wear, mostly between second and third. Unsealed 4X4 blames worn high-kilometre boxes, heavy towing and the wrong oil. It specifies GL-4 75W-90, because GL-5 additives attack the synchro brass ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)).
- HD Automotive notes that most of these trucks now have about half a million kilometres and that their gearboxes "are getting a little sad".

Assumption for this report: a fresh H152 survives 650 to 1,000 Nm in high range with sensible driving. The risk sits in shock loads in first, second, reverse and low range, where torque multiplies most. Section 3 covers how to limit those.

### The options

| Option | Parts cost (AUD) | Torque | Reliability | Towing | Cooling | NSW (VSI 06) |
|---|---|---|---|---|---|---|
| Rebuild the old box with new bearings, synchros and seals | [Marks 4WD kit GBK9](https://www.marks4wd.com/driveline/gearbox/) 840.88, plus specialist labour if outsourced, about 2,000 to 3,000 (estimate) | Same box, no published rating | Reuses 400,000 km shafts, gears and case | As the fitted box | None fitted or needed so far | Like-for-like repair, no certification |
| New genuine Aisin H152F | 3,840 at [GTurbo](https://gturbo.com.au/products/genuine-aisin-h152-5-speed-manual-gearbox-toyota-landcruiser-vdj76-vdj78-vdj79-v8-2007-2024), from 3,829 at [HD Automotive](https://hdautomotive.com.au/blog/2024/02/15/toyota-land-cruiser-gearbox-options/) | No published rating, see above | All new Toyota parts, no exchange core | Taller 2nd and 5th than the H150F | None fitted or needed so far | Toyota's own box for the model, fits the tunnel and bolts to the engine, so no certification (item 6) |
| Toyota AB60 six-speed automatic from the 200 Series ([Wholesale Automatics](https://automatictransmission.com.au/toyota-76-78-and-79-series-manual-to-automatic-conversion/), [Drop Bear Engineering](https://dropbearengineering.com.au/)) | No price published. About 20,000 to 30,000 fitted (estimate, see note) | Both rate it at 900 Nm | Proven Toyota box, plus an aftermarket controller, valve body and adapters | Torque converter take-offs with lock-up control, about 1,550 rpm at 100 km/h (Wholesale Automatics) | Kits include a cooler twice the size of the 200 Series one | Wholesale Automatics says no chassis, driveline or tailshaft changes, which item 6 exempts. Allow a certifier's check (estimate 1,000) |
| ZF 8HP eight-speed automatic ([8speed.au](https://www.8speed.au/products/lc79-toyota-landcruiser-8-speed-auto-conversion)) | 33,950 complete (900 Nm) or 37,950 (1,200 Nm). [DIY kit](https://www.8speed.au/products/diy-toyota-landcruiser-vdj-76-78-79-series-8hp-auto-conversion) 16,350 plus a used 8HP and parts | 900 or 1,200 Nm, 1,500 Nm without warranty | Reconditioned BMW box with a 12-month warranty and an aftermarket controller | Eight ratios. Factory cruise control stops working, an aftermarket unit starts at 795 | Cooler lines and thermostat included | Uses a crossmember mount adapter and may need a front tailshaft spacer, so assume certification (items 6 and 9), estimate 1,000 to 2,500 |
| Six-speed manual | None found for the VDJ79 in Australia | | | | | |

Note on the AB60 estimate: neither supplier publishes a price. The 8HP kit sets the upper bound. A retailer's guide quotes AUD 18,000 to 32,000 for an automatic conversion kit and 4,000 to 8,000 for fitting ([70 Series Store](https://jp.70seriesstore.com/blogs/information/79-series-auto-conversion-price-guide)). That guide calls the AB60F an eight-speed, so treat its figures as rough.

NSW rules used here: VSI 06 says fitting a gearbox that fits the original transmission tunnel and bolts to the engine, directly or with an adapter plate, needs no certification. It needs certification when the floor or crossmembers change, or when structural parts are fabricated. A gearbox ratio change needs none if the final drive is unchanged ([TfNSW VSI 06, Rev 3](https://www.nsw.gov.au/sites/default/files/2021-02/RMS-13.464-Light-vehicle-modifications-Vehicle-Standards-Information-No-6-November-2013.pdf), items 6, 7 and 9). Victoria's VSI 8 exempts a gearbox the maker offered for the same model ([VSI 8, Oct 2011, third-party copy](https://www.morrisminorvic.org.au/assets/CPS2015/VSI8_VehModGuide.pdf)).

### Gear ratios with the trailer

The final drive ratio is not in Toyota's spec sheets. This report assumes 3.909. With the H152F's 0.750 fifth gear on Toyota's 265/70 R16 or 7.50 R16 tyres, 3.909 gives 1,930 to 2,000 rpm at 100 km/h, which matches 4X4 Australia's figure. A 4.300 ratio would give about 2,200 rpm. The table assumes a 265/75 R16 tyre (804 mm diameter, about 2.53 m per turn). Report 16 picks the real tyre.

| Gear | H150F, rpm at 100 km/h | H152F, rpm at 100 km/h | H150F, km/h at 2,000 rpm | H152F, km/h at 2,000 rpm |
|---|---|---|---|---|
| 2nd | Over the rev limit | Over the rev limit | 31 | 34 |
| 3rd | 3,840 | 3,840 | 52 | 52 |
| 4th | 2,580 | 2,580 | 78 | 78 |
| 5th | 2,270 | 1,930 | 88 | 103 |

First gear in low range gives an overall ratio of 44:1 (4.529 x 2.488 x 3.909), or about 7 km/h at 2,000 rpm. That is the gear for hill starts and tight reversing with 6.8 t behind.

What this means for towing a 2.5 to 3 t trailer:

- On flat highway, the H152F's fifth holds 100 km/h at about 1,930 rpm. A tuned engine with a larger turbo makes its torque higher in the rev range, so on long grades or into a headwind fifth will lug. Fourth, at about 2,580 rpm at 100 km/h, becomes the towing gear there. Lugging at low revs and high load raises exhaust gas temperature, which report 14 sets limits for.
- The H150F's fifth (about 2,270 rpm) is the better cruise gear for towing and the worse one solo.
- The H152F's gap from first to second is wider (2.0 against 1.8), and from second to third narrower (1.5 against 1.65). Pulling away uphill in second is harder, so use low range.
- HD Automotive's ratio calculator also lists an "H153" with a 0.775 fifth ([HD Automotive](https://hdautomotive.com.au/blog/2026/02/05/gearbox-ratio-calculator-for-toyota-landcruiser/)). No product page was found, so it is not considered.

### Cooling

No factory or aftermarket cooler for the H15x box was found, and none of the sources reports manual gearbox overheating. Fit temperature senders to the gearbox and rear diff for the first season of towing (optional, about AUD 300, estimate). Add a cooler only if the readings call for it. The automatic options need their coolers, which the kits include.

### Recommendation: a new genuine H152F

Fit a new genuine Aisin H152F (AUD 3,840, [GTurbo](https://gturbo.com.au/products/genuine-aisin-h152-5-speed-manual-gearbox-toyota-landcruiser-vdj76-vdj78-vdj79-v8-2007-2024)). The reasons:

1. All parts are new, for roughly the price of a specialist rebuild that reuses 400,000 km shafts, gears and bearings.
2. It bolts to the factory engine, transfer case, mounts and tailshafts on every VDJ79, so NSW needs no certification.
3. Parts and service are everywhere in Australia, and it is the same box as every later VDJ.
4. It leaves money for the rest of the vehicle. Either automatic would take most or all of the AUD 30,000 budget on its own.

The AB60 automatic is the better towing gearbox. It has a torque converter, six ratios and a cooler, and its builders rate it at 900 Nm. Consider it only if the budget rises by about AUD 20,000 and report 14 stays at or below about 800 Nm, which keeps a margin under that rating. Keep the old manual box as a spare core to rebuild later with the Marks 4WD kit, or sell it.

## 3. Transfer case, tailshafts, diffs, axles and hubs

### Where the extra torque goes

The gearbox and transfer case multiply engine torque before it reaches the tailshafts. Using Toyota's ratios:

| Engine torque | 1st gear, high range, gearbox output | 1st gear, low range, transfer output | Times stock |
|---|---|---|---|
| 430 Nm (stock) | 1,950 Nm | 4,850 Nm | 1.0 |
| 650 Nm | 2,940 Nm | 7,320 Nm | 1.5 |
| 1,000 Nm | 4,530 Nm | 11,270 Nm | 2.3 |

In low range with the diff locks in, one axle can take nearly all of that on a rock step. The front axle is the weaker one. Its diff has an 8-inch ring gear against the rear's 9.5-inch ([ARB application chart](https://www.arb.com.au/content/dam/arb/document/diff-locker-service-and-parts-manual/Air_Locker_application_chart.pdf), [ARB RD253](https://www.arb.com.au/product/rd253-arb-air-locker-rear-32-spline-toyota-landcruiser-70-series-9-5-inch-axle)), and its CV joints work at an angle on full lock.

So the plan caps torque where it multiplies most instead of rebuilding every part for 2.3 times the load. Assumption: report 14's tune limits torque to about 450 to 500 Nm in low range and in first and reverse, which keeps those loads near factory. A 44:1 crawl ratio loses nothing useful at that cap. If the tune cannot do this, the driver must avoid full throttle in low range with the locks engaged, and two items below become required: the heavy-duty front CV joints (otherwise a contingency) and the heavy-duty tailshafts (otherwise optional).

### Transfer case

The HF1A is a gear-driven part-time case (1.000 high, 2.488 low). At 400,000 km, budget new bearings and seals. HD Automotive sells a rebuild kit with Koyo bearings for the VDJ76, 78 and 79 ([P004651](https://hdautomotive.com.au/product/hf1a-part-time-transfer-case-rebuild-kit-with-koyo-bearings-suitable-for-toyota-landcruiser-70-series-80-series/), AUD 653). It also sells a brand-new HF1A from a late VDJ ([P002915](https://hdautomotive.com.au/product/brand-new-h152-transfer-case-suitable-for-toyota-landcruiser-part-time-4wd/), AUD 2,950). Rebuild the old case with the kit while the gearbox is out. Buy the new case only if the gears or case are damaged. Renew the rear gearbox mount at the same time (AUD 150, estimate).

### Tailshafts and uni joints

At 400,000 km, renew every uni joint, the rear centre bearing and any worn slip-joint splines, then have the shafts balanced. Assumption: the single cab's long rear tailshaft is a two-piece shaft with a centre bearing. Budget AUD 900 at a driveline shop for both shafts with genuine or Spicer joints (estimate). With the low-range cap, the factory tube sizes are kept. Without it, a driveline shop can build heavier shafts with larger joints (optional, about AUD 1,500 to 2,500 per shaft, estimate). If the GVM kit changes ride height, have the shop check the shaft angles too.

### Diffs, gear sets and lockers

- Keep the factory ratio (assumed 3.909). A ratio change affects the speedometer and needs certification unless the speedometer is corrected ([VSI 06](https://www.nsw.gov.au/sites/default/files/2021-02/RMS-13.464-Light-vehicle-modifications-Vehicle-Standards-Information-No-6-November-2013.pdf), item 7). The tuned engine makes up for slightly larger tyres.
- Factory electric diff locks came on four of the nine 2014 variants ([Toyota, 2014](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf)). In 2016 they were a AUD 1,500 option on the single cab GX and dual cab WorkMate, which implies the GXL had them as standard ([4X4 Australia](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). Buy a truck with them. Without them, an ARB rear Air Locker costs AUD 1,450 plus AUD 1,280 fitting ([RD253](https://www.arb.com.au/product/rd253-arb-air-locker-rear-32-spline-toyota-landcruiser-70-series-9-5-inch-axle)). VSI 06 item 8 lets aftermarket diff locks in without certification.
- At 400,000 km, check both diffs for whine and backlash, renew the pinion seals and refill with GL-5 oil, as ARB specifies for the 9.5-inch. Rebuild a noisy diff with new bearings and a professional set-up (contingency, about AUD 1,300 per diff, estimate).
- Fit breather extensions to both diffs, the gearbox and the transfer case for creek crossings (AUD 120, estimate).

### Axle housings and the narrow rear track

The rear track is narrower than the front on every V8 single cab: 1,460 mm against 1,555 mm on the GX and GXL, and 1,420 mm against 1,515 mm on the WorkMate ([Toyota spec table, Oct 2026](https://www.toyota.com.au/-/media/toyota/main-site/vehicle-hubs/lc70/files/20261008_lc70_spec_table_gto010119.pdf), [2007 brochure](https://xr793.com/wp-content/uploads/2023/10/2007-Toyota-Land-Cruiser-70-AUS.pdf)). Toyota widened the front for the V8 in 2007 and left the rear, so the rear wheels sit 95 mm inside the fronts. 4X4 Australia says the rear then fails to follow the front wheels' ruts in sand and on rutted tracks, and that a heavy load in the tray or on the towbar makes it worse ([4X4 Australia, 2025](https://www.4x4australia.com.au/gear/2024-toyota-landcruiser-79-gxl-multidrive-rear-track-correction)).

The rear housing's strength under heavy loads is the second issue. No Toyota bulletin or measured data on housings bending was found. The evidence is what the GVM specialists now sell:

| Product | What it is | Rating | Price (AUD) | Source |
|---|---|---|---|---|
| Lovells Elite Series GVM upgrade | Lovells-built rear housing, strengthened, wider to match the front, larger bearings, two-piece Cr-Mo full-float axle shafts, exchange diff | Rear axle 2,850 kg, GVM 4,495 kg, GCM 7,400 kg. Housing tested to 10,000 cycles at over 5 t | 18,875 (Sep 2022 on V8) or 19,975 (Jan 2017 to Aug 2022) fitted, plus compliance | [Unsealed 4X4, Oct 2025](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/) |
| Multidrive rear track correction, MDT0039-ESC | Factory housing cut and rebuilt with billet tubes, wider, with the under-housing bracing extended to the ends. Factory centre, stub axles and brakes reused | GVM up to 3,950 kg | 5,850 plus freight, 6,570 installed | [4X4 Australia, 2025](https://www.4x4australia.com.au/gear/2024-toyota-landcruiser-79-gxl-multidrive-rear-track-correction) |
| Multidrive Tru Tracker | Bolt-on wider stub axles and longer axle shafts | GVM up to 3,780 kg | Not found | Same source |

A track change needs engineering approval. Multidrive's is covered by its GVM second-stage manufacturer approval only before first registration. After registration it needs approval in the state of registration. VSB 14 allows at most 50 mm more track on a rigid rear axle without certification, and wheel spacers are not allowed unless the maker fitted them ([VSI 8](https://www.morrisminorvic.org.au/assets/CPS2015/VSI8_VehModGuide.pdf)). A 95 mm correction therefore needs certification. In practice it is certified with the GVM upgrade.

Recommendation: the ute will run at 3,600 to 3,900 kg with a bike box behind the cab and about 250 kg on the towball, which loads the rear housing hardest. Fix the housing and the track together as part of report 16's GVM upgrade. Either choose a GVM kit that includes a strengthened wide-track housing, such as the Lovells Elite, or add the Multidrive housing (AUD 6,570 installed, rated to 3,950 kg). If report 16 keeps the factory housing, this report adds the Multidrive housing as a required item. At purchase, check the old housing for a bend (section 5).

### Axles, CV joints, swivel hubs, wheel bearings and free-wheel hubs

- Front wheel bearings are tapered rollers in the same hub design Toyota has used since the 40 Series. Unsealed 4X4 says they wear commonly on 70s, a mechanic charges about AUD 500 a side, and owners usually do the swivel hubs at the same time ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)). The swivel hub is the steering knuckle that turns on two trunnion bearings around the CV joint. Its chrome ball carries a wiper seal that keeps grease in and dirt out.
- At 400,000 km, rebuild both swivel hubs with trunnion bearings, seals, gaskets and shims (AUD 450, estimate). Renew all four wheel bearings and seals (front AUD 300, rear AUD 350, estimates). Replace the front CV joints if they click on full lock or show pitting (contingency, AUD 1,800 a pair with heavy-duty joints, estimate). Replace a pitted chrome ball, or the new wiper seal will leak.
- Free-wheel hubs: manual hubs until the late-2016 update, then automatic locking hubs with a manual function ([4X4 Australia, 2016](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). Service manual hubs with new seals (AUD 100, estimate). On a later truck, keep working automatic hubs, or convert to genuine Aisin manual hubs ([Marks 4WD MFK41290](https://www.marks4wd.com/free-wheeling-hubs-70-series-landcruiser-auto-to-manual.html), AUD 595, optional).
- The rear has full-floating hubs: the wheel bearings run on stub axles on the housing, as Multidrive's description shows. The axle shafts only carry torque, so a broken shaft does not drop the wheel.

## 4. The rest of the refresh

Prices in this section are estimates unless a link gives them. They assume Leonard does the work and buys genuine Toyota or known Australian aftermarket parts.

### Steering

- The late-2016 update moved the single cab's steering link behind the front axle for crash performance ([4X4 Australia, 2016](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). Steering parts therefore differ before and after that update, so order by VIN.
- The 79 has no suspension ball joints. The swivel hubs (section 3) carry the knuckle. Its ball joints are the two tie-rod ends and the two drag-link ends.
- At 400,000 km, renew all four ends (AUD 500 for a genuine set) and the steering damper (AUD 150 for a heavy-duty damper). Recondition or exchange the power steering box if it has free play or leaks (AUD 1,100), and renew its hoses and fluid (AUD 150). Check the box's chassis mount for cracks while it is off.
- Thicker heavy-duty tie rods and drag links suit rocky tracks but are optional for this use (AUD 1,200).
- Finish with a wheel alignment (AUD 150, outsourced).

### Suspension bushes, shackles and spring hangers

- The front is a live axle on coil springs, located by two leading arms, a panhard rod and an anti-roll bar ([2007 brochure](https://xr793.com/wp-content/uploads/2023/10/2007-Toyota-Land-Cruiser-70-AUS.pdf)). Renew the leading-arm, panhard rod and anti-roll bar bushes and links (AUD 450). Genuine rubber is quieter on long highway runs. Polyurethane lasts longer off-road. If the GVM kit raises the front, use caster-correction bushes in the leading arms.
- The rear leaf springs come with report 16's GVM kit, normally with new eye bushes.
- Fit greasable shackles and pins unless the GVM kit includes them (AUD 250). Ironman 4x4 lists greasable shackles at AUD 61 to 80 each ([Ironman 4x4](https://www.ironman4x4.com.au/products/greasable-shackles-7973)).
- Inspect each rear spring hanger and its weld to the chassis. Replace a worn or cracked hanger (contingency AUD 300 plus welding).

### Chassis

- The documented fault is cracking at the weld between the rear spring hanger and the frame. Unsealed 4X4 says it appears on trucks that run over GVM on rough roads at speed, and that a clunk under heavy load or rear wander in corners can be the symptom ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)). Its fix is a professional weld, added bracing, then a GVM upgrade.
- The late-2016 single cab got a thicker, stronger chassis with seven crossmembers ([4X4 Australia, 2016](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). That favours a later truck for heavy loads.
- No source was found for cracks behind the cab on the single cab. Check there anyway, because the tray and bike box load the rails just behind the cab. Report 16 covers Toyota's tray and canopy mounting rules.
- Crack-test the hangers, the rails behind the cab and the steering box mount with a dye penetrant kit (AUD 60, done by Leonard). Budget a contingency for outsourced repair and bracing (AUD 1,500).
- Ex-mine trucks often have the worst chassis rust (Unsealed 4X4). Treat surface rust and wax the inside of the rails (AUD 250).

### Cab and body mounts

- Coastal trucks rust in the A-pillars, which can let water in. Unsealed 4X4 knows of an owner who paid nearly AUD 15,000 to replace both pillars, and says to walk away from rusty A-pillars ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)). Also check the door bottoms, windscreen frame, roof gutters and the floor under the mats.
- The flat door seals let in dust, noise and fumes as the doors wear (Unsealed 4X4). An extra seal kit is a cheap option ([70 Series Store](https://70seriesstore.com/products/70-series-landcruiser-soundproofing-door-seal-kit), AUD 59).
- Renew the cab mount rubbers (AUD 400). Hard, split mounts let the cab move and pass more load and vibration into the cab and rails.

### Electrical

- The factory alternator is rated 130 to 150 A and sits low in the path of mud and dust, which Unsealed 4X4 names as a common cause of failure. Its fix for heavy loads is a high-output unit, such as Jaylec's 240 A, and a proper DC-DC charger ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)). Budget a new or reconditioned factory alternator (AUD 700). The 240 A unit is optional (about AUD 1,000). Report 16 sizes the trailer charging feed.
- Recondition or replace the starter motor (AUD 450) and both starting batteries (AUD 600). Assumption: the V8 has two batteries wired in parallel.
- Renew the engine, chassis and body earth straps and the battery cables (AUD 150). The late-2016 update added a fuse box and a fused battery terminal for accessories ([4X4 Australia, 2016](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). On older trucks, check for spliced accessory wiring and chafe near the exhaust. Allow AUD 200 for repairs.

### Fuel tank and lines

- Single cabs had two 90 L tanks (180 L) until the late-2016 update. The DPF re-routed the exhaust, so later single cabs have one 130 L tank ([Toyota, 2014](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf), [4X4 Australia, 2016](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)). Long-range tanks are in report 16. Filters and the lift pump are in report 14.
- Renew the rubber fuel hoses and clamps, check the straps, the tank skins and the sender (AUD 150).

### Air conditioning

- Air conditioning was an option (AUD 2,761 in 2016, [4X4 Australia](https://www.4x4australia.com.au/news/toyota-landcruiser-70-series-upgraded-range-launched)), so check the truck has it.
- Unsealed 4X4 calls the factory system under-designed, and says the condenser clogs with dust, grass and bugs off-road. It suggests an amplifier that lowers the evaporator temperature ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)).
- Clean or replace the condenser, renew the receiver-drier and regas (AUD 350). The Freezebrain amplifier for the VDJ 70 Series is optional ([GTurbo](https://gturbo.com.au/products/landcruiser-freezebrain-vdj-70), AUD 328). Keep a contingency for a compressor (AUD 900).

### Fluids and driveline cooling

Refill everything once the work is done: GL-4 75W-90 in the gearbox, GL-5 in both diffs, the transfer case oil Toyota specifies, swivel hub grease and power steering fluid (AUD 250). Section 2 covers driveline temperatures. No cooler is planned.

## 5. Pre-purchase inspection checklist

The engine, clutch, gearbox and wear parts are budgeted for replacement, so their condition matters less. What matters is damage the budget does not cover: the chassis, the cab, the rear housing and the vehicle's legal history. The list builds on Unsealed 4X4's buying checklist ([Unsealed 4X4](https://unsealed4x4.com.au/toyota-landcruiser-70-series-common-problems/)). Items marked "general" are standard used-4WD checks, not from a 70 Series source.

| Area | What to check | Walk away if |
|---|---|---|
| Papers | A [PPSR](https://www.ppsr.gov.au/) search for finance, write-off and theft records (general). Service history, including gearbox oil and wheel bearing work. Build date and grade from the VIN and compliance plate: before or after the late-2016 update, factory diff locks, factory air conditioning | Any write-off record, or no proof of ownership |
| Past use | Ask about towing and loads (Unsealed 4X4). Look for ex-mine signs: beacon and antenna holes, mine-spec bars, heavy corrosion | Heavy corrosion from mine or coastal use |
| Chassis | Rear spring hangers and their welds for cracks, fresh welds or plates (Unsealed 4X4). Rails behind the cab, at the tray mounts and at the steering box mount (general). Rails for kinks, sag and rust holes | Cracks or repair plates, unless the price covers repair and bracing. Rust holes in a rail |
| Cab | A-pillars, door frames, windscreen frame, gutters and floor under the mats. Wet or silty carpet (general) | Rusty A-pillars. Any sign of flood damage |
| Rear housing | Rear tyre wear on the inner or outer edges on both sides. Put a digital angle gauge on each rear hub face: both should read near vertical and match (general). Cracks where the tubes meet the centre, and diff leaks | A bent housing, unless the price covers a replacement (section 3) |
| Front axle | Jack up each front wheel and rock it at 12 and 6 o'clock for bearing play (Unsealed 4X4). Swivel hubs leaking or chrome balls pitted. CV joints clicking on full lock. Hubs lock and unlock (general) | Not alone. Price the work from section 6 |
| Steering | Free play at the wheel, box leaks, tie-rod and drag-link ends, a bent tie rod (general) | Not alone |
| Test drive | Clutch slip and a crunch from second to third are expected (Unsealed 4X4) and budgeted. Check 2H, 4H and 4L engage, the diff lock lights come on, no clunk taking up drive, no vibration at 80 to 100 km/h, no diff whine on or off the throttle (general) | Transfer case jumping out of 4L, or a loud diff (adds a rebuild) |
| Engine | It will be rebuilt, so look for damage a rebuild cannot fix: dust past the air filter (Unsealed 4X4), coolant in the oil, oil in the coolant, knocking, heavy smoke. DPF warnings or limp mode on later trucks (Unsealed 4X4). Report 14 sets the details | A seized engine, or a cracked block or head |
| Electrical | Dash warnings, charging, battery age, quality of accessory wiring (general) | Not alone |
| Air conditioning | Cold air within a few minutes (general) | Not alone |
| Modifications | Lift, tyres, tune, GVM and tray. Ask for certificates and the modification plate (Unsealed 4X4) | Uncertified major work NSW would make him certify or undo |

Not reasons to walk away, because the budget already replaces them: the clutch, gearbox synchros, bushes, wheel bearings, swivel hub seals, steering ends, the alternator, batteries and a weak air conditioner.

## 6. Costs

Every line is in [15-driveline-parts.yaml](15-driveline-parts.yaml) with its part number, supplier and link. Prices are AUD including GST. "Estimate" marks a price not read from a supplier page. Leonard's labour is excluded. The outsourced work assumed is the tailshaft rebuild and balance, the steering box exchange, the wheel alignment, and any diff rebuild or chassis welding the inspection finds.

### Required

| System | Items | Cost (AUD) |
|---|---|---|
| Clutch | NPC 1300 kit with billet flywheel 1,818.50, master cylinder 131.38, slave cylinder 150 (estimate), braided line 154, fork and pivot 319.81, release and spigot bearings 120 (estimate), input seal 16.50, flywheel bolts 60 (estimate) | 2,770 |
| Gearbox | New Aisin H152F 3,840, rear gearbox mount 150 (estimate) | 3,990 |
| Transfer case | HF1A rebuild kit with Koyo bearings | 653 |
| Tailshafts | All uni joints, centre bearing, balance, outsourced (estimate) | 900 |
| Diffs | Pinion seals and checks 200, breather extensions 120 (estimates) | 320 |
| Front axle and hubs | Swivel hub kits 450, wheel bearings and seals 300, manual hub service 100 (estimates) | 850 |
| Rear axle | Wheel bearings and seals (estimate) | 350 |
| Steering | Tie-rod and drag-link ends 500, damper 150, box exchange 1,100, hoses and fluid 150, alignment 150 (estimates) | 2,050 |
| Suspension | Front bushes 450, greasable shackles and pins 250 (estimates) | 700 |
| Chassis and cab | Dye penetrant kit 60, rust treatment 250, cab mounts 400 (estimates) | 710 |
| Electrical | Alternator 700, starter 450, two batteries 600, earth straps and cables 150, wiring repairs 200 (estimates) | 2,100 |
| Fuel | Hoses, clamps and checks (estimate) | 150 |
| Air conditioning | Condenser, receiver-drier, regas (estimate) | 350 |
| Fluids | All driveline and steering fluids (estimate) | 250 |
| Total required | | 16,143 |
| Contingency | 15% for what the inspection finds on a 400,000 km truck: a diff rebuild (1,300 each), front CV joints (1,800 a pair), hanger or chassis repair (300 to 1,500), an air conditioning compressor (900), or a new transfer case (2,950 instead of 653) | 2,400 |
| Total with contingency | | 18,543 |

### Conditional

| Item | When | Cost (AUD) |
|---|---|---|
| Multidrive strengthened wide-track rear housing, installed | If report 16's GVM kit keeps the factory housing | 6,570 |

### Optional

| Item | Cost (AUD) |
|---|---|
| Gearbox and diff temperature senders and gauge (estimate) | 300 |
| Genuine Aisin manual hub conversion for automatic-hub trucks | 595 |
| Heavy-duty tie rod and drag link (estimate) | 1,200 |
| Heavy-duty tailshafts, only if the tune cannot cap low-range torque (estimate, per shaft) | 1,500 to 2,500 |
| High-output 240 A alternator instead of the factory type (estimate, net extra) | 300 |
| Freezebrain air conditioning amplifier | 328 |
| Door seal kit | 59 |
| ARB rear Air Locker and fitting, only on a truck without factory locks | 2,730 |
| AB60 automatic conversion instead of the H152F (estimate) | 20,000 to 30,000 |

### What this does to the AUD 30,000 budget

This report needs about AUD 18,500 with contingency, or AUD 25,100 if it also carries the rear housing. The brief expects the engine to take about half of the AUD 30,000, so about AUD 15,000. Report 16's GVM kit, brakes, wheels and tyres come on top, and the Lovells Elite kit alone costs AUD 18,875 to 19,975 fitted plus compliance. The vehicle work will therefore land near AUD 45,000 to 55,000 (estimate, pending reports 14 and 16). Plan on about AUD 50,000.

Ways to cut this report's share if the budget stays tight:

- Rebuild the old gearbox with the Marks 4WD kit (AUD 841) instead of buying the H152F. This saves about AUD 3,000 if Leonard does it, at the cost of reused 400,000 km shafts and gears.
- Keep the steering box, alternator and starter if the inspection finds them sound. This saves up to AUD 2,250.
- A well-kept truck could bring this report down to about AUD 11,000 to 13,000 (estimate).

## Open questions

Each ends with the assumption this report uses.

1. What torque will report 14 settle on? Assumption: anywhere from 650 to 1,000 Nm. The NPC 1300 clutch and the H152F cover that range. Only the clutch alternative changes (Xtreme Outback X-Series at or below about 800 Nm).
2. What torque can the H152F take? Assumption: a new box survives 650 to 1,000 Nm in high range with sensible driving, based on HD Automotive's view of the H15x boxes and the 1,300 to 1,600 Nm clutches sold for them. Shock loads in low range, first and reverse are the risk.
3. Can report 14's tune cap torque in low range, first and reverse? Assumption: yes, at about 450 to 500 Nm. If not, the heavy-duty front CV joints (AUD 1,800 a pair) and heavy-duty tailshafts (AUD 1,500 to 2,500 each) become required, and low range is driven gently with the locks in.
4. What is the final drive ratio? Assumption: 3.909, because it gives about 1,930 to 2,000 rpm at 100 km/h in the H152F's fifth on Toyota's tyres, matching 4X4 Australia's report.
5. Which tyre will report 16 choose? Assumption: 265/75 R16 (804 mm) for the ratio tables. A taller tyre lowers every rpm figure in proportion.
6. Does report 16's GVM kit include a strengthened rear housing? Assumption: it should, for example the Lovells Elite. If it keeps the factory housing, this report adds the Multidrive housing (AUD 6,570).
7. Which build date? Assumption: a GXL single cab built after the late-2016 update, for the reasons in the recommendation. The plan fits a new H152F on either build.
8. Is the single cab's rear tailshaft a two-piece shaft with a centre bearing? Assumption: yes, given the 3,180 mm wheelbase. The tailshaft budget covers either case.
9. How many starting batteries does the V8 have? Assumption: two in parallel.
10. Where does the speedometer take its signal? Assumption: from the transfer case or the wheel sensors, so a gearbox change does not affect it. VSI 06 item 7 exempts a gearbox ratio change when the final drive is unchanged.
11. Do the automatic hubs on later trucks need converting? Assumption: no, while they work. Convert to manual Aisin hubs (AUD 595) if they fail.
12. Does the NPC 1300 rating mean 1,300 Nm peak at the crank? Assumption: yes, as HD Automotive describes it as a 1,300 Nm kit.

## Could not verify

- No torque rating for the H150F or H152F was found from Toyota, Aisin or a gearbox specialist.
- No price was published for either AB60 automatic conversion (Wholesale Automatics, Drop Bear Engineering). The AUD 20,000 to 30,000 figure is an estimate. The 70 Series Store price guide used for context contains errors, such as calling the AB60F an eight-speed.
- No Toyota bulletin or measured data on 79 rear housings bending was found. The evidence is the strengthened housings that Lovells and Multidrive now sell.
- No source was found for chassis cracks behind the cab on the single cab. The documented crack site is the rear spring hanger weld.
- No six-speed manual conversion for the VDJ79 was found in Australia.
- The final drive ratio and the two-piece rear tailshaft are inferred, not read from a Toyota document.
- The "H153" gearbox in HD Automotive's ratio calculator has no product page.
- The basis of NPC's 1,300 and 1,600 ratings (peak or rated, crank or wheels) is not published. GTurbo's 1600 listing mentions "dyno figures at the wheels".
- Fitment of Xtreme Outback's MCTY161 master cylinder to the VDJ79 is taken from its 70 Series guide, not a fitment list. Fitment of the Marks 4WD GBK9 rebuild kit to the H150F and H152F is assumed from its "70 Series 5-speed, 1998 on" title.
- Prices marked "estimate" in section 6 and in the parts list were not read from supplier pages. Part numbers marked "by VIN" were not looked up. The online stores of Roadsafe, Superior Engineering, Nolathane, SparesBox and Opposite Lock could not be queried, so their prices were not compared.
- VSB 14 Section LB itself could not be downloaded. The rules come from NSW VSI 06 Rev 3 (November 2013) and Victoria's VSI 8 (October 2011, third-party copy). A newer NSW revision may exist.
- The Shufti 70 Series inspection checklist PDF was blocked, so section 5 builds on Unsealed 4X4's checklist and general checks.
- Toyota Australia's November 2023 news page renders in a browser only. Its statement that the V8 came only with the five-speed manual is taken from the search extract.

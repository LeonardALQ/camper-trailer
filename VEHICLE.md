# LandCruiser 79 car build

Revised 20 Nov 2026 (research report 23 and the decisions of the same day) and 21 Nov 2026 (decision H17: the Lovells Elite kit, and decision H18: its 2,800 kg rear axle plate, its own brakes and the fallback wheels). Every part and paid job is a line in `data/vehicle/vehicle-parts.yaml`, whose totals match this page (`cad/tests/test_costs.py` checks them). The site's Car build page renders every line from it. Measurements are VEH-01 to VEH-28 and UTE-01 in `data/measurements.yaml`.

## Summary

The truck is a used Toyota LandCruiser VDJ79 single cab V8 diesel, built 01/2017 to 08/2022, a GXL by preference, with about 400,000 km. It is built in seven stages over a year or more, and every stage leaves it registered and drivable. It ends at power level B, about 230 to 250 kW and 850 Nm at the crank and never below 224 kW (300 hp). It carries both bikes in the box on the Lovells 4,495 kg Elite GVM kit, plated at a 4,450 kg GVM and a 2,800 kg rear axle for its shared 1,400 kg wheels (decisions H17 and H18), and tows the trailer, plated at 3,500 kg, under Lovells' 7,400 kg GCM revision (decision H2). The required work is AUD 91,547, and AUD 95,602 with the AUD 4,055 contingency allowance. Leonard's planning figure for the build is AUD 75,000, so the plan is AUD 20,602 over it with the allowance and AUD 16,547 over without. The five cuts that reuse old parts once they pass their tests (CUT1 to CUT6) save AUD 13,979, not enough on their own. CUT7 returns to the 4,200 kg Platinum kit (AUD 12,855) only if the S3 weighing leaves at least 30 kg under its 2,550 kg rear axle at the trailer's weighed towball. The fewest cuts that close the gap are CUT1, CUT4 and CUT7 (the injectors, the oil pump and the Platinum, AUD 21,211), which give AUD 74,391, AUD 609 under. CUT1 and CUT7 alone fall AUD 91 short. With all six cuts the plan is AUD 68,768, AUD 6,232 under. Estimates are 49 % of the required total. The truck (Leonard's AUD 50,000 planning figure), the bike box (AUD 51,799 shop-built or AUD 26,776 owner-built, `data/ute/box-parts.yaml`), the trailer and Leonard's labour are outside these figures.

## Stage plan

| Stage | Work | Required AUD | Contingency lines AUD | Paid labour | Downtime (est.) | The ute can then |
|---|---|---|---|---|---|---|
| S0 | Buy, baseline tests, weigh, engage certifiers | 1,330 | 0 | Diesel workshop, weighbridge | 1 day | Drive as bought |
| S1 | Driveline and chassis refresh, sealed airbox, DPF clean, new cooling, gauges | 14,037 | 12,597 | Tailshafts, DPF clean, air conditioning | 2 to 3 weeks | Daily driver at stock power, towing only within Toyota's 3,400 kg GVM and 6,900 kg GCM |
| S2 | Factory-spec engine rebuild, new injectors and pump, NPC clutch, new H152F | 27,231 | 1,500 | Machine shop | 6 to 10 weeks, then a 1,000 km run-in | As after S1, rebuilt |
| S3 | Gate: build and weigh the box body, confirm the kit | 0 | 0 | Box engineer (box budget) | None | Unchanged |
| S4 | Wheels, tyres, steering, the Elite GVM kit with its own brakes, 180 L tank, box, towing gear, one LC5 inspection with the GCM revision and the 2,800 kg plate | 33,866 | 3,200 | Lovells fitter, tyre shop, alignment, certifier | 2 to 3 weeks | Carries the bikes and, once certified, tows up to 3,500 kg at stock power |
| S5 | Trailer charging, tongue, final weighing | 1,965 | 0 | Weighbridge, auto electrician | 1 week | Tows the loaded trailer with charging |
| S6 | Turbo, intercooler, exhaust, then the tune and its certificate | 13,119 | 12,000 | Tuner, emissions test, LC4 certifier | 2 to 4 weeks | Tows the trailer with the box at level B |
| Total | | 91,547 | 29,297 | | | |

The S0 tests decide when S2 happens.

- Branch A, rebuild now, if any S0 test fails: compression spread over 10 % (VEH-01), leak-down over 20 % (VEH-02), blow-by over 100 L/min (VEH-03), an injector more than 25 % off the mean (VEH-04), silicon over 20 ppm with high iron and chromium (VEH-05), fuel dilution over 4 % (VEH-06), any glycol (VEH-07), or clutch slip or gearbox noise (VEH-09). Order S0, S1, S2, S3, S4, S5, S6. Do S1's cooling and intake work while the engine is out.
- Branch B, rebuild later, if every test passes. Order S0, S1, S3, S4, S5, S2, S6. The ute tows at stock power on its own engine and gearbox with the new cooling, sealed airbox and clean DPF, and the engine comes out once, just before the power parts.

The tune is last in both branches, so every earlier stage stays legal whatever the LC4 certifier decides.

### S0 Buy and baseline

Goal: buy the right truck and learn what the engine needs before spending.

- Check the compliance plate for 01/2017 to 08/2022 and run a PPSR search. Walk away from a write-off record, a cracked or plated chassis, rusty A-pillars, flood signs, a bent rear housing or a cracked block or head. Test 2H, 4H, 4L and both diff locks.
- A diesel workshop runs the baseline tests (BI01). The new glow plugs (EN04) go in, as the old ones come out for the compression test. Run the clutch and gearbox check.
- Weigh each axle with full fuel (CK01). Measure the cab width and Toyota's deck-mount stations for the box design.
- Engage the LC5 certifier (GVM kit, GCM revision, box and winch in one inspection) and the LC4 certifier (tune). Get each scope and evidence list in writing.
- Get Lovells' written confirmation that its endorsed certifier will plate the Elite at a 2,800 kg rear axle and a 4,450 kg GVM on the 1,400 kg ROH wheels, before GV05 is bought (decision H18, an assumption until then). If not, Toyota's 16 x 7 ET 0 alloys go on all ten wheels (WT04).
- AUD 1,330. Measure VEH-01 to VEH-07, VEH-09, VEH-18 and VEH-19, and read the DPF data for VEH-08.
- Done when the branch is chosen, both certifiers have confirmed their scope and Lovells has confirmed the Elite's plates in writing.

### S1 Refresh and protect at stock power

Goal: a reliable truck at stock power with the engine protected before any towing.

- Driveline: transfer case kit, tailshafts rebuilt and balanced, pinion seals, breathers, swivel hubs, wheel bearings and hub seals (DL01 to DL08).
- Chassis and cab: crack-test the spring hangers, the rails behind the cab and the steering box mount, treat rust, renew the cab mounts (RF01 to RF03).
- Electrics and services: alternator, starter, battery, earths, wiring, fuel hoses, air conditioning service, driveline fluids (RF04 to RF11). GL-4 75W-90 in the gearbox, GL-5 in the diffs.
- Engine protection: sealed airbox and turbo intake pipe (ID01, TX03), DPF clean and flow test (ID02), pre-filter (FS04), radiator, water pump, thermostat, fan clutch, hoses and coolant (EN14 to EN19).
- Gauges: boost, EGT, water and oil (TL02, TL03), gearbox and rear diff senders (CG11). The EGT probe goes in when the manifold is off, in S2 or S6.
- If the steering fails its check, bring SS01 to SS04 forward and add an alignment (AUD 150, est.). If the brakes fail theirs, fit factory pads or rotors only, because the Elite's own brakes replace them at S4.
- AUD 14,037. Contingency lines AUD 12,597: diff rebuilds, a transfer case, a DPF, chassis repair, a spring hanger, a compressor. No certificate is needed.
- Measure VEH-08 and the before-kit heights for VEH-27.
- Done when nothing leaks, no faults are stored, the DPF passes and the coolant holds 85 to 104 °C on a long climb.

### S2 Engine rebuild with the clutch and gearbox

Goal: a factory-spec engine and a clutch and gearbox for level B, with one engine removal.

- Pull the engine and gearbox. The machine shop crack-tests and machines the block, crank, rods and both heads (EN06 to EN13).
- Measure piston protrusion per bank, then order the NVP kit sizes and head gasket grades (EN01, EN21). Fit the timing set, oil pump, mounts, oil and filters (EN02, EN03, EN05, EN20).
- Flush the tank and lines before the new HP4 pump, eight piezo injectors, fitting kit and filter go in (FS01 to FS03, FS05). Pressure-test the oil cooler and check the vacuum pump for oil (EN22, EN23).
- Refit with the NPC clutch, billet flywheel, clutch hydraulics and new H152F (CG01 to CG10).
- Run in on the factory calibration for 1,000 km, watching the oil level. Refit the oil filter housing's support pole at every change.
- Option: fit S6's turbo, intercooler and exhaust now to save labour. They need no certificate on the factory calibration.
- AUD 27,231, of which the injectors are 9,256. Contingency lines AUD 1,500. No certificate: genuine fuel equipment and a factory-spec rebuild (item 5).
- Measure VEH-03 and VEH-05 to VEH-07 again at 1,000 km as the new baseline.
- Done when the run-in is complete and the oil sample is clean.

### S3 Decision gate: the Elite, or back to the Platinum

Goal: confirm the GVM kit on weighed figures.

- Build and weigh the box walls, roof and doors (box budget). Take the floor and subframe masses from the design.
- Add up the rear axle on the weighed figures: VEH-19, bar and winch, two people, box, bikes, tools, spare, towbar, the full 180 L tank and the trailer's weighed towball.
- The plan buys the Lovells 4,495 kg Elite (GV05, decision H17), plated at a 4,450 kg GVM and a 2,800 kg rear axle, twice the ROH wheel's 1,400 kg (decision H18). Return to the 4,200 kg Platinum (cut CUT7, saves AUD 12,855) only if the sum leaves at least 30 kg under its 2,550 kg rear axle at the trailer's weighed towball.
- On the model the trailer's heaviest towball is 317 kg with growth (292 kg on base masses). The Platinum's rear axle would then carry about 2,451 kg on base masses, 99 kg under 2,550 kg, but about 2,574 kg with growth, 24 kg over. So the cut rests on the weighing. The Elite's 2,800 kg plate keeps 214 kg in hand with growth.
- Settle the front bushes from the kit's contents and front lift (SS05). The Elite brings its own front and rear brakes, booster and handbrake kit, so BR01 to BR04 are gone.
- Done when the kit is ordered.

### S4 GVM kit, GCM revision, box and one LC5 inspection

Goal: legal at the Elite's plated 4,450 kg GVM and 7,400 kg GCM with the box and its winch.

- Brakes come with the Elite: its front and rear kits, booster and handbrake kit, bled with DOT 4 by the fitter and the pads bedded in (BR05). Carry a spare set of Elite pads (BR06). Replacement rotors and pads are the Elite's own or certified equivalents (VSI 06 items 18 and 19).
- Wheels: with the Elite fitted, offer one bare ROH Trak 2 to a front hub and turn it a full turn. With 3 mm or more between its centre and the caliper (est.), check its nut seat against Toyota's steel-wheel nuts and fit six wheels and tyres (WT01 to WT03). If it touches, or the certifier refuses the 2,800 kg plate, fit Toyota's 16 x 7 ET 0 alloy on all ten wheels (WT04, contingency, AUD 3,200 est.). Steering ends, damper, exchange box, hoses and front bushes (SS01 to SS05).
- Fit the ARB Frontier 180 L tank (FT01, TAD106) in place of the factory 130 L tank. The trailer's roof study (research report 25) puts towing fuel at about 21.3 L/100 km at 90 km/h with the fixed, radiused-front roof, so the factory tank gives about 550 km between fills and the 180 L tank about 760 km, with 10 % kept. At research report 25's cautious planning figure of 25 L/100 km they are about 470 and 650 km.
- Lovells' authorised fitter fits the Elite kit (GV01, GV02 and GV05). Until the certificate the ute stays rated at 3,400 kg GVM and 6,900 kg GCM, so carry no bikes and tow nothing.
- Measure the rear track on the Elite's housing (VEH-28, about 1,555 mm). Finish the box floor and subframe to the kit's ride height and bump travel and the tubs and rear tub flares to the measured track (decision H19), then bolt the empty box to Toyota's deck-mount stations with the winch, ramp and restraints. Lovells' two mudflaps hang behind the rear tyres from the box's rear outriggers.
- Fit the towbar, the REDARC controller, wiring kit and mount, and the 12-pin socket with the brake output on pin 5 (TW01 to TW05). Check the plugs and chains under the box's 210 mm overhang.
- Align the wheels and reset the LSPV with the box on (GV04).
- One LC5 inspection: the kit, the GCM revision, the box, the winch and the tank (GV03, GV06). The certifier plates the Elite at a 4,450 kg GVM and a 2,800 kg rear axle (decision H18). The box's parts list has no inspection line, because GV03 covers it. A modification plate goes on, Service NSW endorses the record, and the insurer is told.
- AUD 33,866. The Elite fitted is 19,975 (GV01 5,620 and GV02 1,500, both est., plus GV05 12,855 from the listing). The inspection is 1,500 and the GCM revision 1,750 (both est.), the tank 1,557 and the spare pads 350 (est.). Contingency line AUD 3,200, the alloy wheels (WT04). Optional AUD 1,839.
- Measure VEH-25 to VEH-28.
- Done when the plate is on and the record is endorsed.

### S5 Trailer integration

Goal: tow the loaded trailer legally, level and charged.

- Fit the trailer charging (TC01, AUD 1,612, 8.4 kg): two Victron Orion-Tr Smart 12/48-8 chargers in a vented cover in the box front, on the stock alternator, with a 100 A fuse at the battery. They put about 3.6 kWh into the trailer on a 5 h drive and draw about 62 A. The 48 V feed (TW06, AUD 123, 1.9 kg) runs 7 m of 8 B&S cable to a grey Anderson SB50 at the towbar (research report 20, the trailer's electrical research). Their 10.3 kg is in the ute model (UT-14, UT-15).
- Log the ute's battery voltage on the first hot night tow with both chargers running. If it stays under 13.3 V, run one charger until the upgrade (TC02, optional, AUD 1,723): a Jaylec BKS-240LC 240 A alternator and two more chargers, 7.2 kWh on a 5 h drive.
- Weigh the laden ute alone and coupled to the loaded trailer (CK03). Choose the DO35 tongue's drop from the laden coupling height (TW08). Set tyre pressures from the tyre maker's load table.
- Make the first long tow at stock power and record the temperatures.
- AUD 1,965. Measure UTE-01, UTE-03, VEH-14 to VEH-17 and VEH-20 to VEH-24.
- Done when every weighed figure and towing temperature is inside its range.

### S6 Power, then the tune and its certificate

Goal: level B, certified straight away. Needs S2 done and S5's tow inside the temperature ranges.

- Fit the VD-G333 and its gaskets, the front-mount intercooler and the Manta exhaust, keeping the factory rear crossover (TX01, TX02, TX04, TX05). Fit the EGT probe if it is not in, and route the actuator breather high.
- Book the emissions test and the LC4 certifier first, so the uncertified tune is driven only to those appointments.
- Tune day, one dyno: a run on the factory calibration, then the tune and the tuned run (TL01). Keep the factory file.
- Settings: 230 to 250 kW at the crank (about 170 to 185 rwkW), never below 224 kW (166 rwkW). About 850 Nm from 1,800 rpm. 450 to 500 Nm in low range, first and reverse. Less torque below 1,600 rpm on the towing map. Fuel pulled from 650 °C EGT, never above 700 °C. EGR, DPF and catalyst untouched.
- Emissions test with the clean DPF and no faults (TL04), then the VSCCS certificate from the LC4 certifier (TL05). If it is refused, flash the factory file back. Everything else stays legal.
- AUD 13,119. Contingency lines AUD 12,000: laboratory test 10,000, gas test 200, CV joints 1,800. If the tune cannot cap low-range torque, the CV joints and two tailshafts (AUD 5,800) become required.
- Measure VEH-10 to VEH-13, then VEH-14 to VEH-17 on the next long tow.
- Done when the certificate is endorsed and the towing temperatures pass.

## Parts list by system

AUD including GST. Every line, with its priority, reason, stage and dependencies, is in `data/vehicle/vehicle-parts.yaml` and on the site's Car build page.

| System | Required | Contingency lines | Optional | Largest lines |
|---|---|---|---|---|
| Engine rebuild, cooling, baseline tests | 13,618 | 1,500 | 400 | Machine shop 4,200, NVP kit 2,471, radiator 1,757 |
| Fuel system | 11,398 | 0 | 0 | Piezo injectors 9,256, HP4 pump 1,480 |
| Sealed airbox and DPF service | 2,095 | 5,000 | 0 | Airbox 1,495 |
| Turbo, intercooler, exhaust | 8,519 | 0 | 0 | VD-G333 4,290, intercooler 2,200 |
| Tune, gauges, engine certificate | 5,710 | 10,200 | 0 | Tune 2,500, certificate 2,000 |
| Clutch and gearbox | 7,044 | 0 | 0 | H152F 3,840, NPC kit 1,819 |
| Transfer case, tailshafts, diffs, hubs | 3,073 | 6,697 | 7,325 | Tailshafts 900 |
| Steering and front suspension | 2,350 | 300 | 1,200 | Steering box 1,100 |
| Chassis, cab, electrics, air conditioning, fluids | 3,230 | 2,400 | 387 | Alternator 700 |
| GVM kit, GCM revision, certificate | 23,475 | 0 | 0 | Elite net extra 12,855, Platinum kit 5,620, GCM revision 1,750 |
| Brakes | 390 | 0 | 0 | Spare Elite pads 350. The Elite brings its own brakes |
| Wheels and tyres, six of each | 4,110 | 3,200 | 0 | Tyres 2,520. Toyota alloys if needed 3,200 (WT04) |
| Towing and trailer charging | 3,919 | 0 | 2,362 | Charging 1,612, towbar 1,160 |
| Freight and weighing | 1,060 | 0 | 0 | Freight 1,000 |
| Long-range tank | 1,557 | 0 | 0 | ARB Frontier 180 L |
| Bull bar and winch | 0 | 0 | 4,233 | Only if the truck has none |
| Total | 91,547 | 29,297 | 15,907 | |

Each figure is rounded to the dollar, so a column can differ from its total by AUD 1.

| Total | AUD |
|---|---|
| Required | 91,547 |
| Contingency allowance | 4,055 |
| Required with contingency | 95,602 |
| Leonard's build figure | 75,000 |
| Over the build figure, with contingency | 20,602 |
| Less CUT1, CUT4 and CUT7, the fewest cuts that close it | -21,211 |
| Required with CUT1, CUT4, CUT7 and contingency | 74,391 |
| Less every cut, CUT1 to CUT7 | -26,834 |
| Required with every cut and contingency | 68,768 |

By priority: P1 (safe, legal and reliable towing, or protecting the truck) is AUD 78,428 required. P2 (the 224 kW minimum) is AUD 13,119. P3 lines are all optional, AUD 11,907.

The allowance is EN21, EN22, EN23 and TL06 in full (AUD 1,700) plus 15 % of report 15's required lines (AUD 2,355). A new DPF (5,000) and the laboratory test (10,000) are outside it. The cuts are: test and reuse the injectors (saves 7,656) and the pump (1,480), reuse the oil pump (700), rebuild the truck's own gearbox (up to 2,983), keep a rated factory towbar (1,160) and return to the Platinum kit if the S3 weighing allows it (12,855). CUT1, CUT4 and CUT7 are the fewest that close the gap, and CUT1 and CUT7 alone fall AUD 91 short. At level B a tested injector set has less flow margin than a new one.

## Limits to build and drive to

The model is the built ute (`build/ute/ute.json`) on the Elite kit, case UC2 with growth: two people, both bikes, the 436 kg box, tools, one spare, bar and winch, the trailer charging, the full 180 L tank and the Elite's extra 10 kg (est.), 3,620 kg with 1,480 kg front and 2,140 kg rear. The towing cases add the trailer's heaviest towball with growth, 317 kg (TC2, decision H17), which the trailer's MAS-03B and a test keep in step with the trailer.

| Limit | Value | Model with growth |
|---|---|---|
| Ute, laden, ball load included | At most 4,450 kg (the Elite as plated, H18) | 3,937 kg |
| Front axle | At most 1,650 kg | 1,480 kg, no trailer |
| Rear axle | At most 2,800 kg (the Elite plated at twice the ROH wheel's 1,400 kg, H18), or 2,550 kg if CUT7 returns to the Platinum | 2,586 kg, 214 kg in hand |
| Ball load | At most 350 kg (towbar). H17's design range: at least 8.0 % of the trailer and at most 320 kg with growth | 317 kg (292 kg on base masses) |
| Ute plus trailer | At most 7,400 kg with GV06, 6,900 kg without | 7,120 kg, the ute plus the trailer's 3,500 kg plate (H20) |
| Trailer | At most 3,500 kg | 3,397 kg fully loaded, against its 3,400 kg design limit |
| Front axle share | At least 20 % (Toyota BBGJ1007) | 34.3 %, towing |
| Coupling point, laden | 440 mm plus or minus 20 mm (VSB1: 350 to 460 mm) | 440 mm |
| Rear wheel | At most 1,400 kg (ROH), which sets the 2,800 kg plate | 1,293 kg towing, 107 kg in hand |
| Tyres | Load index 121 and speed M or better on the Elite (research report 26, est.) | 123/120 R |
| Box | Body at most 1,850 mm wide and rear tub flares at most 1,910 mm (H19), overhang at most 1,908 mm, unladen centre of gravity under 1,000 mm | 1,850 and 1,890, 1,555 and 781 mm |
| Rear tyre to the box | 30 mm outside it, 40 mm inside it and 25 mm over it at full bump (Toyota BBGJ1007 p. 28) | 31, 40 and 25 mm on the Elite's 1,555 mm rear track |

On the Elite the rear axle keeps 214 kg in hand, and decision H20 retired the plan's 3,850 kg weighed target, which stood for the Platinum's rear axle margin. Each kg on the ball adds 1.41 kg to the rear axle, and each kg at the tray centre about 1.04 kg. Without the GCM revision, Toyota's 6,900 kg less the ute with growth leaves the trailer a 3,280 kg plate, and it tows with at most 232 L of water in place of 350 L, so the fully loaded trailer with growth stays under that plate (H20).

Drive to: coolant 85 to 104 °C towing, oil 90 to 116 °C, EGT at most 700 °C, gearbox oil at most 110 °C sustained (est.), no full load below 1,600 rpm. Use fourth gear on long grades and low range for hill starts and reversing the trailer.

## Legal path

NSW registration, Victoria as the fallback. Items are from TfNSW's [VSI 06 Rev 4](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf), issued 1 July 2026. Certifier categories are from [VSCCS Bulletin 01](https://nsw.gov.au/sites/default/files/2025-01/vsccs-bulletin-01-licensed-certifiers.pdf): LC4 covers engine, fuel, intake and exhaust, and LC5 covers body, chassis, suspension, steering, driveline, wheels, tyres and axles.

GVM kit, GCM revision, box and winch (S4). Item 51 lists re-rating the GVM or the GCM as certifiable. Lovells rates the 4,200 kg kit at 7,400 kg GCM with 3,500 kg braked towing ([Lovells sheet, Oct 2026 ratings](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf)), and the 4,495 kg Elite at the same 7,400 kg GCM (report 16). The certifier plates the Elite at a 4,450 kg GVM and a 2,800 kg rear axle, twice the ROH Trak 2's 1,400 kg rating (assumption, decision H18). Lovells publishes a derate only for its 4,200 kg kit, so its written yes comes in S0, before GV05 is bought. If that is refused, Toyota's 16 x 7 ET 0 alloy, the wheel Lovells rates its kits on, goes on all ten wheels (WT04). Lovells' conditions for the 4,200 kg kit are tyres of load index 117 and speed M or better (research report 26 puts the Elite at about 121 and M, which the 123/120 R tyres pass), a Lovells authorised fitter and a Lovells-endorsed signatory ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)). The plan adds a towbar rated 3,500 kg and 350 kg, and braked towing means the trailer's own brakes on every wheel with a breakaway system (VSB1, above 2,000 kg ATM), driven by the REDARC controller. The revision is assumed to add AUD 1,750 (est.), the midpoint of the AUD 1,000 to 2,500 that [70 Series Store](https://70seriesstore.com/blogs/information/what-is-the-79-series-towing-gcm) gives for post-registration GCM engineering. The certificate also covers the ride height (item 13), the box (items 27 and 34, 1,890 mm over its rear tub flares, inside Toyota's 60 mm beyond the cab on each side, decision H19), the winch as a possible powered loading device (item 35) and the 180 L tank (item 50).

If NSW refuses the GCM revision: Lovells warns it may not be available after registration in every state. Victoria needs a [VASS certificate](https://transport.vic.gov.au/registration-and-licensing/registration/standard-and-non-standard-vehicle-information/modified-and-non-standard-vehicles/vass-approval-certificate) to change the GVM and is stricter about post-registration GCM upgrades (70 Series Store), so assume Victoria refuses it too. The fallback is H20's: the trailer plated at or below 3,280 kg and at most 232 L of water in travel. NSW does not recognise interstate light vehicle certificates (VSI 06 Rev 4 page 3), so choose the state before the first certificate.

The tune (S6). Item 6 needs a certificate for a reflash that alters emissions output. An LC4 certifier issues the LA4 certificate for about AUD 2,000 (est.) on the TfNSW test or the Interim NSW Vehicle Emissions Test Procedure (May 2023). Keep the same-dyno sheets, the emissions result, the DPF clean record and invoices for the genuine Denso injectors and pump. The certifier may ask for evidence that the driveline takes about 850 Nm.

No certificate: the rebuild with genuine fuel equipment, the airbox, intercooler and exhaust (item 5), the H152F (item 7), wheels and tyres at Toyota's size and offset, and the towbar (item 31). The Elite's brakes are certified with the kit, and their replacement rotors and pads must be the Elite's own or certified equivalents (items 18 and 19). Declare every change to the insurer.

## Decisions

| Decision | Reason |
|---|---|
| VDJ79 single cab built 01/2017 to 08/2022, GXL first | The 4,200 kg kit fits single cabs only from 01/2017, and the GXL has factory diff locks |
| Level B from the start, never below 224 kW | 300 hp is Leonard's minimum, and any emissions-altering tune needs a certificate |
| Factory-spec rebuild with new genuine injectors and HP4 pump | Restores a 400,000 km engine with no certificate |
| Sealed airbox and DPF clean, both required | Dust wears the new engine, and the emissions evidence needs a working DPF |
| VD-G333, PDI twin-throttle intercooler, Manta 3 inch DPF-back exhaust | They run inside their limits at level B and keep the emission controls |
| New H152F and NPC 1300 organic clutch, ZF 8-speed as fallback | A new gearbox costs about the same as a rebuild |
| 450 to 500 Nm in low range, first and reverse | Protects the 8 inch front diff and the CV joints |
| Elite kit (GV05) required, back to the Platinum (CUT7) only if the S3 weighing leaves at least 30 kg under 2,550 kg | The home trailer's towball and the 180 L tank leave the Platinum's rear axle no margin (H17) |
| Lovells 7,400 kg GCM revision in the same inspection | The ute with growth plus the trailer's 3,500 kg plate is 7,120 kg (H2, H20) |
| Tune last, certified at once, factory file kept | Every earlier stage stays legal |
| Pre-tune dyno run on the finished hardware | The certifier compares like with like |
| Gearbox and diff senders required (CG11) | The towing checks decide whether a cooler is needed |
| Shared ROH 16 x 7 wheels and LT265/75R16 tyres | Toyota's size and offset, and one spare fits both vehicles |
| Elite plated at a 4,450 kg GVM and a 2,800 kg rear axle on the 1,400 kg ROH wheels, Toyota's alloys as the fallback (WT04) | No 16 inch wheel that fits both vehicles is rated 1,425 kg, and the plate keeps 214 kg in hand (H18) |
| The Elite's own brakes, BR01 to BR04 removed, spare pads carried (BR06) | The kit replaces the front and rear brakes, the booster and the handbrake (research report 26) |
| Box body 1,850 mm, rear tub flares to 1,890 mm | The Elite's 1,555 mm rear track puts the tyre 11 mm from the body's skin, and Toyota allows 60 mm beyond the cab on each side, 1,910 mm (H19) |
| 50 mm tongue for the DO35 pin (TW08) | The trailer's coupling kit has no tongue, and its drop sets the 440 mm height |
| ARB Frontier 180 L tank, required (FT01) | Towing at about 21.3 L/100 km leaves the 130 L tank about 550 km between fills, the 180 L tank about 760 km (research report 25) |
| Two Orion-Tr Smart 12/48-8 chargers on the stock alternator (TC01) | Nothing on the engine changes, both parts have Australian stock, and the 48 V run to the towbar loses little (research report 20) |

## Open points and the assumption used

1. Will the LC5 certifier include the GCM revision after registration? Assumed yes, for AUD 1,750. If not, a trailer plate at or below 3,280 kg and at most 232 L of water in travel (H20).
2. Will the LC4 certifier accept the TfNSW test (assumed free) or the Interim NSW procedure at level B? Assumed yes. If not, a gas analyser test (TL06, AUD 200) or a laboratory test (TL07, AUD 10,000).
3. Can the tune cap low-range torque? Assumed yes. If not, AUD 5,800 of CV joints and tailshafts.
4. What torque does the H152F take? Assumed about 850 Nm in high range with sensible driving, inside report 15's 650 to 1,000 Nm. No rating is published.
5. Does the NVP kit suit the DPF engine? Assumed the same parts and price with the DPF gasket set by VIN. GTurbo still lists it for pre-DPF engines only (20 Nov 2026).
6. Does the clean restore the DPF? Assumed yes. If not, AUD 5,000 (ID03).
7. Does the truck have a bar and winch? Assumed yes, 110 kg in the sums. If not, AUD 4,233.
8. What does the kit lift, and which bushes come with it? Assumed 50 mm (est.) and rear bushes only, so the front bush line stays.
9. Prices without a current listing: the kit AUD 5,620 (a 2024 listing), tyres AUD 420 each (a US listing converts to AUD 471), and the tongue AUD 200 (all est.).
10. When does the gearbox need a cooler? Above 110 °C sustained (est.).
11. Does the front-mount intercooler starve the radiator at low towing speed? Assumed no. Watch VEH-14. GTurbo's AUD 1,895 fan kit is the fallback.
12. Does Victoria have a reflash rule like NSW item 6? Not checked. The LA4 path is assumed.
13. Can the stock alternator carry both chargers? Assumed yes: about 50 to 60 A spare at cruise against their 62 A (research report 20). Log the voltage on the first hot night tow, and run one charger or fit TC02 if it stays under 13.3 V.
14. Does the Jaylec BKS-240LC fit the 2017 VDJ79? Marks 4WD lists it for the VDJ LandCruiser without a model split. Assumed yes. Confirm against the VIN before buying TC02.
15. Will the LC5 certifier plate the Elite at a 4,450 kg GVM and a 2,800 kg rear axle on the 1,400 kg ROH wheels? Assumed yes, in GV03 at no extra cost, as Lovells offers the same derate on its 4,200 kg kit (H18). If not, or if the Elite's front caliper touches the steel wheel at the S4 dry fit, Toyota's 16 x 7 ET 0 alloy on all ten wheels (WT04, AUD 3,200 est.).
16. What rear track does the Elite's housing give? Assumed 1,555 mm, the front track, on ET 0 wheels (research report 26). The model, the box's tubs and its rear tub flares use it (H19). Measure it at S4 (VEH-28) before the tubs and flares are finished, and the tyre-to-flare gap once the box is on (BOX-20).
17. Is the trailer weighed before the kit is ordered at S3? Assumed not. Without the trailer's weighed towball, CUT7's 30 kg margin cannot be shown, so the Elite stays.
18. Does the Elite's rear kit bring longer rear brake lines for the wider housing? Assumed yes, as Multidrive's equivalent housing does (research report 26).
19. What tyre load index and speed does the Elite need? Lovells publishes none. Assumed load index 121 and speed M, from half the 2,850 kg rear axle rounded up to the next index (research report 26). The 123/120 R tyres pass.

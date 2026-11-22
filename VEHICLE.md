# LandCruiser 79 car build

Revised 22 Nov 2026 for decision H24 (research report 27): the build buys the upgrades and what makes them legal and able to tow, and the wear parts move to a purchase check list. Earlier revisions: 20 Nov 2026 (research report 23) and 21 Nov 2026 (H17, the Lovells Elite kit, and H18, its 2,800 kg rear axle plate, own brakes and fallback wheels). Every part and paid job is a line in `data/vehicle/vehicle-parts.yaml`, which the site's Car build page renders as three lists and `cad/tests/test_costs.py` checks against this page. Measurements are VEH-01 to VEH-28 and UTE-01 in `data/measurements.yaml`.

## Summary

The truck is a used Toyota LandCruiser VDJ79 single cab V8 diesel, built 01/2017 to 08/2022, a GXL by preference, with about 400,000 km. Each of its seven stages, over a year or more, leaves it registered and drivable. It ends at power level B, about 230 to 250 kW and 850 Nm at the crank and never below 224 kW (300 hp). It carries both bikes in the box on the Lovells 4,495 kg Elite GVM kit, plated at a 4,450 kg GVM and a 2,800 kg rear axle for its shared 1,400 kg wheels (H17, H18), and tows the trailer, plated at 3,500 kg, under Lovells' 7,400 kg GCM revision (H2).

Decision H24 sorts the work into three lists. The build is the upgrades and what makes them legal and able to tow: the engine rebuild, the clutch, upgraded injectors, the turbo, intercooler and exhaust, and the tune with its certificate, then the GVM kit and the GCM revision with their wheels, tyres and inspection, the towing gear and the trailer charging. It comes to AUD 67,703, or AUD 77,777 with one allowance of 10 % on listed prices and 20 % on estimates (AUD 10,074). That is AUD 2,777 over Leonard's AUD 75,000. Cut CUT7, back to the 4,200 kg Platinum kit if the S3 weighing allows it, closes the gap at AUD 63,637, and both cuts give AUD 62,361. Estimates are 48.8 % of the build.

The upgraded injectors bring one risk the build does not price. The Pro 100 is non-original fuel injection equipment, which report 14 judged makes a laboratory ADR 79 emissions test likely (TL07, AUD 10,000 est., on the check list). The plan assumes the LC4 certifier accepts the free TfNSW test of the finished truck. If its written evidence list at S0 asks for a laboratory test, the build drops the Pro 100 service and its fitting kit (FS01 and FS07, AUD 5,080) and runs level B on the truck's own tested injectors at factory flow, which carry it with about 10 to 25 % in hand (research report 27).

The purchase check list holds what a 400,000 km truck may or may not need: bearings, bushes, hoses, steering joints, the alternator, the starter, the gearbox and the like, and every line bought only if a test or a certifier calls for it. The S0 inspection checks each line against its pass mark, and the S1 refresh buys only what fails. If every line failed, the check list would come to AUD 53,956, which is a note and not a total. The optional extras, among them the lockers, bar, winch, X-Bar and 180 L tank, come to AUD 12,070. Before H24 the required lines were AUD 91,547, or AUD 95,602 with their allowance, because the list priced a full refresh as if every wear part were due. The truck (Leonard's AUD 50,000 planning figure), the bike box (AUD 27,870, built by Leonard, `data/ute/box-parts.yaml`), the trailer and Leonard's labour are outside these figures.

## Stage plan

| Stage | Work | Build AUD | Check list AUD | Paid labour | Downtime (est.) | The ute can then |
|---|---|---|---|---|---|---|
| S0 | Buy, run the purchase check list and the baseline tests, weigh, engage certifiers | 990 | 0 | Diesel workshop, weighbridge | 1 day | Drive as bought |
| S1 | Replace only what the S0 check list failed | 0 | 19,735 | Whatever the failed lines need | None to 3 weeks | Daily driver at stock power, towing only within Toyota's 3,400 kg GVM and 6,900 kg GCM |
| S2 | Factory-spec engine rebuild, NPC clutch on the truck's own H152F, new radiator, sealed airbox and pre-filter | 14,450 | 8,298 | Machine shop | 6 to 10 weeks, then a 1,000 km run-in | As after S1, rebuilt |
| S3 | Gate: build and weigh the box body, confirm the kit | 0 | 0 | None, Leonard builds the box body | None | Unchanged |
| S4 | Wheels, tyres, front bushes, the Elite GVM kit with its own brakes, the box fitted, towing gear, one LC5 inspection with the GCM revision and the 2,800 kg plate | 30,059 | 3,200 | Lovells fitter, tyre shop, alignment, certifier | 2 to 3 weeks | Carries the bikes and, once certified, tows up to 3,500 kg at stock power |
| S5 | Gauges, trailer charging, tongue, final weighing | 3,305 | 1,723 | Weighbridge, auto electrician | 1 week | Tows the loaded trailer with charging |
| S6 | Turbo, intercooler, exhaust, the Pro 100 injectors and the DPF clean, then the tune and its certificate | 18,899 | 21,000 | GTurbo, DPF specialist, tuner, emissions test, LC4 certifier | 2 to 4 weeks | Tows the trailer with the box at level B |
| Total | | 67,703 | 53,956 | | | |

The check list column is what a stage would cost if every check line fitted in it failed, and it is not counted.

The S0 tests decide when S2 happens.

- Branch A, rebuild now, if any S0 test fails: compression spread over 10 % (VEH-01), leak-down over 20 % (VEH-02), blow-by over 100 L/min (VEH-03), an injector more than 25 % off the mean (VEH-04), silicon over 20 ppm with high iron and chromium (VEH-05), fuel dilution over 4 % (VEH-06), any glycol (VEH-07), or clutch slip or gearbox noise (VEH-09). Order S0, S1, S2, S3, S4, S5, S6.
- Branch B, rebuild later, if every test passes. Order S0, S1, S3, S4, S5, S2, S6. The ute tows at stock power on its own engine and gearbox, and the engine comes out once, just before the power parts.

The tune is last in both branches, so every earlier stage stays legal whatever the LC4 certifier decides. The upgraded injectors go in with the tune, because the factory calibration cannot run them (research report 27).

### S0 Buy, inspect and baseline

Goal: buy the right truck, find what it needs, and learn what the engine needs before spending.

- Check the compliance plate for 01/2017 to 08/2022 and run a PPSR search. Walk away from a write-off record, a cracked or plated chassis, rusty A-pillars, flood signs, a bent rear housing or a cracked block or head. Test 2H, 4H, 4L and both diff locks.
- A diesel workshop runs the baseline tests (BI01) and the clutch and gearbox check. The same visit works through the purchase check list. Each line's check and pass mark is on the Car build page, and most need only a hoist, a scan tool and the dye-penetrant kit (RF01).
- Weigh each axle with full fuel (CK01). Measure the cab width and Toyota's deck-mount stations for the box design.
- Engage the LC5 certifier (the GVM kit and the GCM revision in one inspection) and the LC4 certifier (the power, the injectors and the tune). Get each scope and evidence list in writing, which settles TL06 and TL07. Ask the LC4 certifier for the list with the Pro 100 injectors, and if it names a laboratory test, for the list on the factory injectors as well.
- Ask the tuner in writing whether the tune caps low-range torque at 450 to 500 Nm, which settles DL11 and DL13.
- Get Lovells' written confirmation that its endorsed certifier will plate the Elite at a 2,800 kg rear axle and a 4,450 kg GVM on the 1,400 kg ROH wheels, before GV05 is bought (decision H18, an assumption until then). If not, Toyota's 16 x 7 ET 0 alloys go on all ten wheels (WT04).
- AUD 990. Measure VEH-01 to VEH-07, VEH-09, VEH-18 and VEH-19, and read the DPF data for VEH-08.
- Done when the branch is chosen, every check line has a pass or a fail, both certifiers have confirmed their scope and Lovells has confirmed the Elite's plates in writing.

### S1 Refresh what the inspection found

Goal: a reliable truck at stock power, paying only for what failed.

- Replace each check line that failed at S0, in the stage its line names. Most belong here: wheel bearings, swivel hubs, tailshafts, the transfer case, the cab mounts, the alternator, starter and battery, hoses, the water pump and thermostat, the steering joints and the air conditioning. Lines that can be judged only with the engine or gearbox out, such as the oil pump, the clutch fork and the engine mounts, wait for S2.
- If the inspection finds the old radiator part-blocked, bring EN14 forward from S2.
- If the steering fails its check, add an alignment (AUD 150, est.). If the brakes fail theirs, fit factory pads or rotors only, because the Elite's own brakes replace them at S4.
- No build line. AUD 0 to 19,735, by what fails. No certificate is needed.
- Measure the before-kit heights for VEH-27.
- Done when nothing leaks, no faults are stored and the coolant holds 85 to 104 °C on a long climb.

### S2 Engine rebuild with the clutch

Goal: a factory-spec engine and a clutch for level B, with one engine removal.

- Pull the engine and gearbox. The machine shop crack-tests and machines the block, crank, rods and both heads (EN06 to EN13).
- Measure piston protrusion per bank, then order the NVP kit sizes and head gasket grades (EN01, and EN21 if another grade is needed). Fit the timing set, oil and filters (EN02, EN20). Measure the oil pump and check the mounts, the oil cooler and the vacuum pump (EN03, EN05, EN22, EN23).
- Refit the truck's own injectors with a new fitting kit (FS02), with a new genuine injector in place of any that failed at S0 (FS06). Fit the pre-filter and a new factory filter (FS04, FS05).
- Fit the NPC clutch with its billet flywheel, new release and spigot bearings, flywheel bolts and a new input shaft seal (CG01, CG06 to CG08) to the truck's own H152F. Check the fork, the hydraulics and the rear mount on the way (CG02, CG03, CG05, CG10). A new H152F goes in only if the gearbox failed its S0 check (CG09).
- Fit the new radiator and coolant (EN14, EN19) and the sealed airbox (ID01) before the first start. The radiator is new because level B tows on the factory core's full heat rejection, which a flow test cannot show a 400,000 km core still gives (report 14 section 3.9).
- Run in on the factory calibration for 1,000 km, watching the oil level, and refit the oil filter housing's support pole at every change.
- Option: fit S6's turbo, intercooler and exhaust now to save labour. They need no certificate on the factory calibration.
- AUD 14,450. No certificate: a factory-spec rebuild on the truck's own fuel equipment (item 5).
- Measure VEH-03 and VEH-05 to VEH-07 again at 1,000 km as the new baseline.
- Done when the run-in is complete and the oil sample is clean.

### S3 Decision gate: the Elite, or back to the Platinum

Goal: confirm the GVM kit on weighed figures.

- Leonard builds and weighs the box walls, roof and doors. Take the floor and subframe masses from the design.
- Add up the rear axle on the weighed figures: VEH-19, bar and winch, two people, box, bikes, tools, spare, towbar, the fuel and the trailer's weighed towball.
- The plan buys the Lovells 4,495 kg Elite (GV05, decision H17), plated at a 4,450 kg GVM and a 2,800 kg rear axle, twice the ROH wheel's 1,400 kg (decision H18). Return to the 4,200 kg Platinum (cut CUT7, saves AUD 14,140 with its share of the allowance) only if the sum leaves at least 30 kg under its 2,550 kg rear axle at the trailer's weighed towball.
- On the model, which keeps the optional 180 L tank full as the heavier case, the trailer's heaviest towball is 317 kg with growth (292 kg on base masses). The Platinum's rear axle would then carry about 2,503 kg on base masses, 47 kg under 2,550 kg, but about 2,635 kg with growth, 85 kg over, so the cut rests on the weighing. The Elite's 2,800 kg plate keeps 153 kg in hand with growth.
- Settle the front bushes from the kit's contents and front lift (SS05). The Elite brings its own front and rear brakes, booster and handbrake kit, so BR01 to BR04 are gone.
- Done when the kit is ordered.

### S4 GVM kit, GCM revision, towing gear and one LC5 inspection

Goal: legal at the Elite's plated 4,450 kg GVM and 7,400 kg GCM with the box on.

- Brakes come with the Elite: its front and rear kits, booster and handbrake kit, bled with DOT 4 by the fitter and the pads bedded in (BR05). Replacement rotors and pads are the Elite's own or certified equivalents (VSI 06 items 18 and 19).
- Wheels: with the Elite fitted, offer one bare ROH Trak 2 to a front hub and turn it a full turn. With 3 mm or more between its centre and the caliper (est.), check its nut seat against Toyota's steel-wheel nuts and fit six wheels and tyres (WT01 to WT03). If it touches, or the certifier refuses the 2,800 kg plate, fit Toyota's 16 x 7 ET 0 alloy on all ten wheels (WT04, AUD 3,200 est., on the check list). Fit the front bushes (SS05).
- Lovells' authorised fitter fits the Elite kit (GV01, GV02 and GV05). Until the certificate the ute stays rated at 3,400 kg GVM and 6,900 kg GCM, so carry no bikes and tow nothing.
- Measure the rear track on the Elite's housing (VEH-28, about 1,555 mm). Finish the box floor and subframe to the kit's ride height and bump travel and the tubs and rear tub flares to the measured track (decision H19), then bolt the empty box to Toyota's deck-mount stations with the winch, ramp and restraints. Lovells' two mudflaps hang behind the rear tyres from the box's rear outriggers.
- Fit the towbar, the REDARC controller, wiring kit and mount, and the 12-pin socket with the brake output on pin 5 (TW01 to TW05). Check the plugs and chains under the box's 210 mm overhang.
- If the optional ARB Frontier 180 L tank (FT01) is wanted, it goes in now, so the same inspection covers it.
- Align the wheels and reset the LSPV with the box on (GV04).
- One LC5 inspection covers the kit and the GCM revision (GV03, GV06). The certifier plates the Elite at a 4,450 kg GVM and a 2,800 kg rear axle (H18). A modification plate goes on, Service NSW endorses the record, and the insurer is told. Leonard builds the box himself and does not have it certified (H25).
- AUD 30,059. The Elite fitted is 19,975 (GV01 5,620 and GV02 1,500, both est., plus GV05 12,855 from the listing). The inspection is 1,500 and the GCM revision 1,750 (both est.). Check line AUD 3,200, the alloy wheels (WT04). Optional AUD 3,746.
- Measure VEH-25 to VEH-28.
- Done when the plate is on and the record is endorsed.

### S5 Trailer integration

Goal: tow the loaded trailer legally, level and charged.

- Fit the boost, EGT, coolant and oil temperature gauges (TL02, TL03) before the first long tow. The EGT probe goes into the manifold when it is off, at S2 in branch A or at S6 in branch B.
- Fit the trailer charging (TC01, AUD 1,612, 8.4 kg): two Victron Orion-Tr Smart 12/48-8 chargers in a vented cover in the box front, on the stock alternator, with a 100 A fuse at the battery. They put about 3.6 kWh into the trailer on a 5 h drive and draw about 62 A. The 48 V feed (TW06, AUD 158, 2.6 kg) runs 7 m of 6 B&S twin cable (13.3 mm2) to a grey Anderson SB50 at the towbar (research report 20), so the ute half of the feed drops 0.8 % at today's 16 A and 1.6 % at TC02's 32 A. The ute model carries their 11.0 kg (UT-14, UT-15).
- Log the ute's battery voltage on the first hot night tow with both chargers running. If it stays under 13.3 V, run one charger until the upgrade (TC02, on the check list, AUD 1,723): a Jaylec BKS-240LC 240 A alternator and two more chargers, 7.2 kWh on a 5 h drive.
- Weigh the laden ute alone and coupled to the loaded trailer (CK03). Choose the DO35 tongue's drop from the laden coupling height (TW08). Set tyre pressures from the tyre maker's load table.
- Make the first long tow at stock power and record the temperatures.
- AUD 3,305. Measure UTE-01, UTE-03, VEH-14 to VEH-17 and VEH-20 to VEH-24.
- Done when every weighed figure and towing temperature is inside its range.

### S6 Power, then the tune and its certificate

Goal: level B, certified straight away. Needs S2 done and S5's tow inside the temperature ranges.

- Fit the VD-G333 and its gaskets, the front-mount intercooler and the Manta exhaust, keeping the factory rear crossover (TX01, TX02, TX04, TX05). Fit the EGT probe if it is not in, and route the actuator breather high.
- Run the ute on the dyno on the factory calibration with the finished hardware, the first of TL01's two runs. Then post the injectors to GTurbo for the Pro 100 service (FS01, 2 to 5 business days), and refit them with a new fitting kit (FS07). If the LC4 certifier's S0 list asked for a laboratory test with them, skip both and tune on the factory injectors.
- Remove the DPF for the specialist's clean and flow test (ID02). A cracked or melted filter is replaced (ID03, on the check list).
- Book the emissions test and the LC4 certifier first, so the uncertified tune is driven only to those appointments.
- Tune day, on the same dyno: the tune and the tuned run (TL01). Keep the factory file.
- Settings: 230 to 250 kW at the crank (about 170 to 185 rwkW), never below 224 kW (166 rwkW). About 850 Nm from 1,800 rpm. 450 to 500 Nm in low range, first and reverse. Less torque below 1,600 rpm on the towing map. Fuel pulled from 650 °C EGT, never above 700 °C. EGR, DPF and catalyst untouched.
- Emissions test with the clean DPF and no faults (TL04), then the VSCCS certificate from the LC4 certifier (TL05). If it is refused, refit stock-flow nozzles and flash the factory file back (open point 21). Everything else stays legal.
- AUD 18,899. Check lines AUD 21,000: laboratory test 10,000, a new DPF 5,000, tailshafts 4,000, CV joints 1,800 and a gas test 200. If the tune cannot cap low-range torque, the CV joints and two tailshafts (AUD 5,800) are bought.
- Measure VEH-10 to VEH-13, then VEH-14 to VEH-17 on the next long tow.
- Done when the certificate is endorsed and the towing temperatures pass.

## Parts list by system

AUD including GST. Every line, with its list, priority, reason, stage and dependencies, is in `data/vehicle/vehicle-parts.yaml` and on the site's Car build page, where each check line also gives what to check, when, and its pass mark.

| System | Build | Check list | Optional | Largest build lines |
|---|---|---|---|---|
| Engine rebuild, cooling, S0 inspection | 10,778 | 4,340 | 400 | NVP kit 2,471, radiator 1,757, heads 1,400 |
| Fuel system and injectors | 5,742 | 2,637 | 0 | Pro 100 service 4,890, pre-filter 432 |
| Sealed airbox and DPF service | 2,095 | 5,000 | 0 | Airbox 1,495, DPF clean 600 |
| Turbo, intercooler, exhaust | 8,269 | 250 | 0 | VD-G333 4,290, intercooler 2,200, exhaust 1,480 |
| Tune, gauges, engine certificate | 5,710 | 10,200 | 0 | Tune 2,500, certificate 2,000, gauges 990 |
| Clutch and gearbox | 2,015 | 4,591 | 454 | NPC kit 1,819. A new H152F, 3,840, only if the old one fails |
| Transfer case, tailshafts, diffs, hubs | 0 | 14,245 | 2,850 | None. Every line is a check or an extra |
| Steering and front suspension | 450 | 2,200 | 1,200 | Front bushes 450 |
| Chassis, cab, electrics, air conditioning, fluids | 60 | 5,570 | 387 | Crack test kit 60 |
| GVM kit, GCM revision, certificate | 23,475 | 0 | 0 | Elite net extra 12,855, Platinum kit 5,620, GCM revision 1,750 |
| Brakes | 40 | 0 | 350 | DOT 4 flush. The Elite brings its own brakes |
| Wheels and tyres, six of each | 4,110 | 3,200 | 0 | Tyres 2,520. Toyota alloys, 3,200, only if needed (WT04) |
| Towing and trailer charging | 4,049 | 1,723 | 639 | Charging 1,612, towbar 1,160 |
| Freight and weighing | 910 | 0 | 0 | Freight 850 |
| Long-range tank | 0 | 0 | 1,557 | ARB Frontier 180 L, an extra |
| Bull bar and winch | 0 | 0 | 4,233 | Only if the truck has none |
| Total | 67,703 | 53,956 | 12,070 | |

Each figure is rounded to the dollar, so a column can differ from its total by AUD 1.

| Total | AUD |
|---|---|
| The build | 67,703 |
| Allowance, 10 % of listed prices and 20 % of estimates | 10,074 |
| The build with its allowance | 77,777 |
| Leonard's build figure | 75,000 |
| Over the build figure, with the allowance | 2,777 |
| Less CUT7, with its share of the allowance | -14,140 |
| The build with CUT7 and the allowance | 63,637 |
| Less both cuts, CUT6 and CUT7 | -15,416 |
| The build with both cuts and the allowance | 62,361 |
| Purchase check list, if every line failed (not counted) | 53,956 |
| Optional extras (not counted) | 12,070 |

By priority: P1 (legal, safe and able to tow, or protecting the truck) is AUD 49,404 of the build, and P2 (the 224 kW minimum) is AUD 18,299. The optional extras are AUD 12,070.

The allowance follows the trailer's rule: 10 % of the build's listed prices (AUD 34,669) and 20 % of its estimates (AUD 33,035). Research report 27 found no better basis for a one-off build. The check list carries none, because each of its prices is already the price if the line fails, and it is not added to the build.

The cuts are two. Keep a rated factory towbar if the bought truck has one (CUT6, AUD 1,276 with its share of the allowance), and return to the Platinum kit if the S3 weighing allows it (CUT7, AUD 14,140). CUT7 alone closes the gap. The old cuts that tested and reused the injectors, the supply pump, the oil pump and the gearbox are now the plan itself, because those parts sit on the check list.

## Limits to build and drive to

The model is the built ute (`build/ute/ute.json`) on the Elite kit, case UC2 with growth: two people, both bikes, the 437 kg box, tools and the trailer's tie-down straps and ground anchors, one spare, bar and winch, the trailer charging, the optional 180 L tank full, which the model keeps as the heavier case, and the Elite's extra 10 kg (est.), 3,678 kg with 1,475 kg front and 2,203 kg rear. The towing cases add the trailer's heaviest towball with growth, 317 kg (TC2, decision H17), which the trailer's MAS-03B and a test keep in step with the trailer.

| Limit | Value | Model with growth |
|---|---|---|
| Ute, laden, ball load included | At most 4,450 kg (the Elite as plated, H18) | 3,994 kg |
| Front axle | At most 1,650 kg | 1,475 kg, no trailer |
| Rear axle | At most 2,800 kg (the Elite plated at twice the ROH wheel's 1,400 kg, H18), or 2,550 kg if CUT7 returns to the Platinum | 2,649 kg, 151 kg in hand |
| Ball load | At most 350 kg (towbar). H17's design range: at least 8.0 % of the trailer and at most 320 kg with growth | 317 kg (292 kg on base masses) |
| Ute plus trailer | At most 7,400 kg with GV06, 6,900 kg without | 7,178 kg, the ute plus the trailer's 3,500 kg plate (H20) |
| Trailer | At most 3,500 kg | 3,398 kg fully loaded, against its 3,400 kg design limit |
| Front axle share | At least 20 % (Toyota BBGJ1007) | 33.7 %, towing |
| Coupling point, laden | 440 mm plus or minus 20 mm (VSB1: 350 to 460 mm) | 440 mm |
| Rear wheel | At most 1,400 kg (ROH), which sets the 2,800 kg plate | 1,324 kg towing, 76 kg in hand |
| Tyres | Load index 121 and speed M or better on the Elite (research report 26, est.) | 123/120 R |
| Box | Body at most 1,850 mm wide and rear tub flares at most 1,910 mm (H19), overhang at most 1,908 mm, unladen centre of gravity under 1,000 mm | 1,850 and 1,890, 1,555 and 781 mm |
| Rear tyre to the box | 30 mm outside it, 40 mm inside it and 25 mm over it at full bump (Toyota BBGJ1007 p. 28) | 31, 40 and 25 mm on the Elite's 1,555 mm rear track |

Toyota's body builder's guide BBGJ1007 (September 2017) sets the 20 % front axle share, the tyre clearances and the cab chassis' 700 mm centre of gravity that the model uses (UT-01). It is no longer online. Toyota's guide for trucks from January 2007, [LC70BBG](https://myfleet.toyota.com.au/customer/userfiles/LC70BBG.pdf), is, and gives the same rules and 740 mm. At 740 mm the ute's stability factor would read about 0.86 in place of 0.89 (UTE-11, est.).

On the Elite the rear axle keeps 151 kg in hand, and H20 retired the plan's 3,850 kg weighed target, which stood for the Platinum's rear axle margin. Each kg on the ball adds 1.41 kg to the rear axle, and each kg at the tray centre about 1.04 kg. Without the GCM revision, Toyota's 6,900 kg less the ute with growth leaves the trailer a 3,222 kg plate, and it tows with at most 124 L of water in place of 300 L, so the fully loaded trailer with growth stays under that plate (H20).

Drive to: coolant 85 to 104 °C towing, oil 90 to 116 °C, EGT at most 700 °C, gearbox oil at most 110 °C sustained (est.) where the optional senders are fitted, no full load below 1,600 rpm. Use fourth gear on long grades and low range for hill starts and reversing the trailer.

## Legal path

NSW registration, Victoria as the fallback. Items are from TfNSW's [VSI 06 Rev 4](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf), issued 1 July 2026. Certifier categories are from [VSCCS Bulletin 01](https://nsw.gov.au/sites/default/files/2025-01/vsccs-bulletin-01-licensed-certifiers.pdf): LC4 covers engine, fuel, intake and exhaust, and LC5 covers body, chassis, suspension, steering, driveline, wheels, tyres and axles.

GVM kit and GCM revision (S4). Item 51 lists re-rating the GVM or the GCM as certifiable. Lovells rates the 4,200 kg kit at 7,400 kg GCM with 3,500 kg braked towing ([Lovells sheet, Oct 2026 ratings](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf)), and the 4,495 kg Elite at the same 7,400 kg GCM (report 16). The certifier plates the Elite at a 4,450 kg GVM and a 2,800 kg rear axle, twice the ROH Trak 2's 1,400 kg rating (assumption, decision H18). Lovells publishes a derate only for its 4,200 kg kit, so its written yes comes in S0, before GV05 is bought, and if it is refused Toyota's 16 x 7 ET 0 alloy, the wheel Lovells rates its kits on, goes on all ten wheels (WT04). Lovells' conditions for the 4,200 kg kit are tyres of load index 117 and speed M or better (research report 26 puts the Elite at about 121 and M, which the 123/120 R tyres pass), a Lovells authorised fitter and a Lovells-endorsed signatory ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)). The plan adds a towbar rated 3,500 kg and 350 kg. Braked towing means the trailer's own brakes on every wheel with a breakaway system (VSB1, above 2,000 kg ATM), driven by the REDARC controller. The revision is assumed to add AUD 1,750 (est.), the midpoint of the AUD 1,000 to 2,500 that [70 Series Store](https://70seriesstore.com/blogs/information/what-is-the-79-series-towing-gcm) gives for post-registration GCM engineering. The certificate also covers the ride height (item 13) and, if it is fitted, the optional 180 L tank (item 50). Leonard builds the bike box and its winch himself and does not have them certified (H25). The box stays inside Toyota's 60 mm beyond the cab on each side, 1,890 mm over its rear tub flares (H19).

If NSW refuses the GCM revision: Lovells warns it may not be available after registration in every state. Victoria needs a [VASS certificate](https://transport.vic.gov.au/registration-and-licensing/registration/standard-and-non-standard-vehicle-information/modified-and-non-standard-vehicles/vass-approval-certificate) to change the GVM and is stricter about post-registration GCM upgrades (70 Series Store), so assume Victoria refuses it too. The fallback is H20's: the trailer plated at or below 3,222 kg and at most 124 L of water in travel. NSW does not recognise interstate light vehicle certificates (VSI 06 Rev 4 page 3), so choose the state before the first certificate.

The power, the injectors and the tune (S6). Item 6 needs a certificate for a reflash that alters emissions output, item 2 for a power rise of more than 20 %, and items 5 and 49 for non-original fuel injection equipment, which the Pro 100 injectors are. One LC4 certifier issues one LA4 certificate for them all (LA4 is VSB 14's code for an engine modification) for about AUD 2,000 (est.). A modified vehicle must still meet ADR 79/04, and VSCCS Bulletin 2 accepts as evidence an IM240 test at TfNSW's emission testing facility or an equivalent NATA facility, or the gazetted Interim NSW Vehicle Emissions Test Procedure (May 2023). Which test the certifier asks for is its own call. Report 14 judged that non-original injectors make a laboratory test likely, so the plan carries TL07 with FS01 and drops FS01 and FS07 if the certifier's S0 list asks for one. Keep the same-dyno sheets, the emissions result, the DPF clean record and GTurbo's invoice and flow sheet for the injectors. The certifier may ask for evidence that the driveline takes about 850 Nm.

No certificate: the rebuild on the truck's own fuel equipment, the airbox, intercooler and exhaust (item 5), a new H152F if one is needed (item 7), wheels and tyres at Toyota's size and offset, and the towbar (item 31). The Elite's brakes are certified with the kit, and their replacement rotors and pads must be the Elite's own or certified equivalents (items 18 and 19). Declare every change to the insurer.

## Decisions

| Decision | Reason |
|---|---|
| VDJ79 single cab built 01/2017 to 08/2022, GXL first | The 4,200 kg kit fits single cabs only from 01/2017, and the GXL has factory diff locks |
| Level B from the start, never below 224 kW | 300 hp is Leonard's minimum, and any emissions-altering tune needs a certificate |
| Three lists: the build, the purchase check list and the optional extras (H24) | Leonard wants the upgrades and what makes them legal, not a new truck |
| Factory-spec rebuild on the truck's own injectors and pump, each replaced only if it fails its S0 test | Parts that still work stay (H24), and a factory-spec rebuild needs no certificate |
| GTurbo's Pro 100 service of the truck's own injectors, fitted with the tune (FS01), dropped with FS07 if the LC4 certifier asks for a laboratory test with them (TL07) | The upgraded injectors Leonard asked for, at level B's fuel with margin, and the factory calibration cannot run them (research report 27). Non-original injectors make a laboratory test more likely (report 14) |
| Sealed airbox and DPF clean, both in the build | Dust wears the new engine, and the emissions evidence needs a working DPF |
| VD-G333, PDI twin-throttle intercooler, Manta 3 inch DPF-back exhaust | They run inside their limits at level B and keep the emission controls |
| The truck's own H152F with the NPC 1300 organic clutch, a new H152F only if it fails at S0, the ZF 8-speed as the fallback | GTurbo's packages put more torque than level B through the factory gearbox, and its common fault, synchro wear, shows at the S0 check (research report 27) |
| 450 to 500 Nm in low range, first and reverse | Protects the 8 inch front diff and the CV joints |
| Elite kit (GV05) in the build, back to the Platinum (CUT7) only if the S3 weighing leaves at least 30 kg under 2,550 kg | The home trailer's towball and the 180 L tank leave the Platinum's rear axle no margin (H17) |
| Lovells 7,400 kg GCM revision in the same inspection | The ute with growth plus the trailer's 3,500 kg plate is 7,178 kg (H2, H20) |
| Tune last, certified at once, factory file kept | Every earlier stage stays legal |
| Pre-tune dyno run on the finished hardware | The certifier compares like with like |
| Gearbox and diff senders optional (CG11) | No report of the manual gearbox overheating when towing was found (research report 27) |
| Shared ROH 16 x 7 wheels and LT265/75R16 tyres | Toyota's size and offset, and one spare fits both vehicles |
| Elite plated at a 4,450 kg GVM and a 2,800 kg rear axle on the 1,400 kg ROH wheels, Toyota's alloys as the fallback (WT04) | No 16 inch wheel that fits both vehicles is rated 1,425 kg, and the plate keeps 153 kg in hand (H18) |
| The Elite's own brakes, BR01 to BR04 removed, spare pads carried (BR06) | The kit replaces the front and rear brakes, the booster and the handbrake (research report 26) |
| Box body 1,850 mm, rear tub flares to 1,890 mm | The Elite's 1,555 mm rear track puts the tyre 11 mm from the body's skin, and Toyota allows 60 mm beyond the cab on each side, 1,910 mm (H19) |
| 50 mm tongue for the DO35 pin (TW08) | The trailer's coupling kit has no tongue, and its drop sets the 440 mm height |
| ARB Frontier 180 L tank optional (FT01) | The 130 L tank gives about 470 to 550 km towing, past the longest sealed-highway gap of about 274 km (research reports 25 and 27) |
| Two Orion-Tr Smart 12/48-8 chargers on the stock alternator (TC01) | Nothing on the engine changes, both parts have Australian stock, and the 48 V run to the towbar loses little (research report 20) |

## Open points and the assumption used

1. Will the LC5 certifier include the GCM revision after registration? Assumed yes, for AUD 1,750. If not, a trailer plate at or below 3,222 kg and at most 124 L of water in travel (H20).
2. Will the LC4 certifier accept the TfNSW test (assumed free) or the Interim NSW procedure at level B with the Pro 100 injectors? Assumed yes. If its S0 list asks for a laboratory test with them, the build drops FS01 and FS07 (AUD 5,080) and the tune runs on the factory injectors. If it asks for one even then, a gas analyser test (TL06, AUD 200) or a laboratory test (TL07, AUD 10,000).
3. Can the tune cap low-range torque? Assumed yes. If not, AUD 5,800 of CV joints and tailshafts.
4. What torque does the truck's own H152F take? No rating is published. GTurbo's power packages for the VDJ70 reach 850 to 1,100 Nm at the wheels through the factory gearbox, with its NPC clutch as the only driveline part it lists, and the box's common fault is synchro wear (research report 27). Assumed: a box that passes its S0 check carries about 850 Nm at the crank in high range with sensible driving.
5. Does the NVP kit suit the DPF engine? Assumed the same parts and price with the DPF gasket set by VIN. GTurbo still lists it for pre-DPF engines only (20 Nov 2026).
6. Does the clean restore the DPF? Assumed yes. If not, AUD 5,000 (ID03).
7. Does the truck have a bar and winch? Assumed yes, 110 kg in the sums. If not, AUD 4,233.
8. What does the kit lift, and which bushes come with it? Assumed 50 mm (est.) and rear bushes only, so the front bush line stays.
9. Prices without a current listing: the kit AUD 5,620 (a 2024 listing), tyres AUD 420 each (a US listing converts to AUD 471), and the tongue AUD 200 (all est.).
10. When does the gearbox need a cooler? No report of the manual H15x overheating was found, so the senders are optional (CG11). Assumed never at level B. With the senders fitted, above 110 °C sustained (est.).
11. Does the front-mount intercooler starve the radiator at low towing speed? Assumed no. Watch VEH-14. GTurbo's AUD 1,895 fan kit is the fallback.
12. Does Victoria have a reflash rule like NSW item 6? Not checked. The LA4 path is assumed.
13. Can the stock alternator carry both chargers? Assumed yes: about 50 to 60 A spare at cruise against their 62 A (research report 20). Log the voltage on the first hot night tow, and run one charger or fit TC02 if it stays under 13.3 V.
14. Does the Jaylec BKS-240LC fit the 2017 VDJ79? Marks 4WD lists it for the VDJ LandCruiser without a model split. Assumed yes. Confirm against the VIN before buying TC02.
15. Will the LC5 certifier plate the Elite at a 4,450 kg GVM and a 2,800 kg rear axle on the 1,400 kg ROH wheels? Assumed yes, in GV03 at no extra cost, as Lovells offers the same derate on its 4,200 kg kit (H18). If not, or if the Elite's front caliper touches the steel wheel at the S4 dry fit, Toyota's 16 x 7 ET 0 alloy on all ten wheels (WT04, AUD 3,200 est.).
16. What rear track does the Elite's housing give? Assumed 1,555 mm, the front track, on ET 0 wheels (research report 26). The model, the box's tubs and its rear tub flares use it (H19). Measure it at S4 (VEH-28) before the tubs and flares are finished, and the tyre-to-flare gap once the box is on (BOX-20).
17. Is the trailer weighed before the kit is ordered at S3? Assumed not. Without the trailer's weighed towball, CUT7's 30 kg margin cannot be shown, so the Elite stays.
18. Does the Elite's rear kit bring longer rear brake lines for the wider housing? Assumed yes, as Multidrive's equivalent housing does (research report 26).
19. What tyre load index and speed does the Elite need? Lovells publishes none. Assumed load index 121 and speed M, from half the 2,850 kg rear axle rounded up to the next index (research report 26). The 123/120 R tyres pass.
20. Can the factory calibration run the Pro 100 injectors? Assumed not: GTurbo says the tuner sets them to the target (booklet p. 24), so they go in with the tune at S6, and the 1,000 km run-in stays on the truck's own injectors.
21. Can GTurbo return the old nozzles with the service, so a refused certificate can take the engine back to stock? Assumed yes. If not, eight new stock-flow injectors at FS06's AUD 1,157 each, AUD 9,256.
22. Does the Elite's new rear housing bring new wheel bearings and an exchange diff? Assumed yes (report 16 section 2.3), so DL08 and the rear diff in DL10 matter only if CUT7 keeps the factory housing.
23. Do the check list's estimated pass marks hold, such as the charging voltage, the cranking voltage, the earth voltage drop, the air conditioning outlet and the oil change interval? Assumed: they are common workshop figures, and the workshop's own figure for this truck overrides them.
24. Does the LC4 certifier's fee cover the injectors with the tune? Assumed yes, in TL05's AUD 2,000 (est.).

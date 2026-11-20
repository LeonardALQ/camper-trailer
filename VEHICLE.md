# The LandCruiser 79 vehicle plan

Vehicle plan, 20 Nov 2026. It merges research reports 14 (engine), 15 (driveline and refresh) and 16 (limits, GVM, brakes, wheels, towing) with the decisions in the overnight plan's decision log, cited by its time. Every part and outsourced job is in `vehicle-parts.yaml`, and its totals match this page.

Terms used throughout:

- GVM (gross vehicle mass): the most the loaded ute may weigh, including the towball load. GCM (gross combination mass): the most the ute and trailer may weigh together. ATM (aggregate trailer mass): the most the loaded trailer may weigh, as shown on its plate.
- VSCCS: the NSW scheme of licensed certifiers who approve modifications. VSI 06 is Transport for NSW's (TfNSW's) guide to which modifications need a VSCCS certificate. ADRs are the national vehicle standards. VSB1 is the national code for building trailers.
- LC4 and LC5: VSCCS certifier categories for light commercial vehicles. LC4 covers engine, fuel, intake and exhaust work. LC5 covers body, chassis, suspension, steering, driveline, wheels, tyres and axles.
- DPF: the diesel particulate filter in the exhaust. EGR: exhaust gas recirculation. EGT: exhaust gas temperature.
- LSPV: the load-sensing proportioning valve that sets rear brake pressure from the rear axle load.
- rwkW: kilowatts at the wheels, as a chassis dyno reads them. Toyota's 151 kW is measured at the crank.
- Growth allowance: mass added to figures not yet weighed, 20 % on an estimate, 7 % on a calculated figure and none on a maker's figure (the trailer study's rule, layout-79.md section 3.1).

## Summary

The vehicle is a used Toyota LandCruiser 79 single cab chassis with the 4.5 L V8 turbo diesel (VDJ79), built from 01/2017 to 08/2022, a GXL by preference, with about 400,000 km. The GVM kit sets the build date: Lovells' 4,200 kg kit fits single cabs only from 01/2017.

The engine is rebuilt to factory specification with new piezo injectors, a new supply pump, a sealed airbox that keeps dust out of the fresh engine, and a cleaned and flow-tested DPF. It then runs power level A: up to 181 kW and about 650 Nm at the crank. Power rises 20 % over stock (151 kW) and torque about 51 % (430 Nm), and torque is what the clutch and gearbox carry. The turbo (GTurbo VD-G333), the PDI front-mount intercooler and the Manta 3 inch DPF-back exhaust also suit level B (220 to 250 kW) later. A new Aisin H152F gearbox and an NPC 1,300 Nm organic clutch take the torque, and the tune caps torque at 450 to 500 Nm in low range, first and reverse. The transfer case, tailshafts, hubs, steering, bushes and electrics are rebuilt or renewed, and the air conditioning is serviced. Slotted rotors with braided lines, steel wheels and LT265/75R16 tyres shared with the trailer, a Lovells GVM kit and a Hayman Reese towbar with a REDARC brake controller complete it. The GVM kit, Lovells' 4,200 kg Platinum or 4,495 kg Elite, is chosen only once the bike box body is built and weighed.

Cost. The required work is AUD 73,150. With a contingency allowance of AUD 4,010 it is AUD 77,160, about 2.6 times the AUD 30,000 target. Six cuts that keep it reliable, each only if the old part passes its test, save up to AUD 15,735 and bring it to AUD 61,425 with contingency. So the budget needs to rise to about AUD 61,000 with every cut, or about AUD 77,000 for the full plan. The driveline refresh, GVM kit, brakes, wheels, tyres, towing, freight and weighing alone come to AUD 33,211, more than the target. The engine takes the rest: the rebuild with its sealed airbox and DPF service (AUD 26,210, of which the injectors are AUD 9,256) and the power parts, tune and certificate (AUD 13,729). About 54 % of the required total is estimates. The bike box, about AUD 13,900, sits outside these figures.

Legal path in NSW. VSI 06 Rev 4, in force since 1 July 2026, adds item 6. It needs a certificate for flashing the engine management system in a way that alters emissions output, unless the maker approves it. A tune that adds 20 % power does that, so level A needs a VSCCS certificate too, about AUD 2,000 (estimate). Report 14 read the 2013 revision, which needed none. The GVM kit needs its own certificate after Lovells' fitter fits it (about AUD 1,500, estimate). The bike box and its winch go into that same inspection, because a no-certificate box is only an assumption and item 35 may treat the winch as a powered loading device. The gearbox, brakes, wheels and tyres, sealed airbox and towbar need none. Level B later is a retune and an LA4 certificate (the national code's approval for a modified engine).

## Decisions

| Decision | Why | From |
|---|---|---|
| Buy a VDJ79 single cab built 01/2017 to 08/2022. GXL first, GX second | Lovells' 4,200 kg kit fits single cabs only from 01/2017, the 3,900 kg kits' 2,360 kg rear axle is too small, and the GXL has factory front and rear diff locks | Report 16, decision log 11:25 |
| Power level A: up to 181 kW and about 650 Nm at the crank | It keeps heat and stress near stock for hours of towing, holds about 88 km/h on a 6 % grade at 6.6 t, and leaves level B open. The 300 to 400 bhp asked for is 224 to 298 kW, which is level B or C. VSI 06 Rev 4 means levels A and B both need a VSCCS certificate now, and level A still wins: it keeps the driveline inside its margin (the H152F has no published torque rating, and level B needs about 850 Nm) and is the easier emissions case. If the LC4 certifier accepts the driveline and the Interim NSW emissions test at 220 to 250 kW, level B can go on the same certificate | Report 14, decision log 11:15 and 11:50 |
| Level B hardware: GTurbo VD-G333, PDI twin-throttle front mount, Manta 3 inch exhaust that keeps the DPF | The parts run well inside their limits at level A, and level B becomes a retune plus a certificate | Report 14, decision log 11:15 |
| DPF engine variant: piezo injectors and a DPF-back exhaust | It follows from the build date. It costs AUD 3,636 more than the earlier engine | Report 14, decision log 11:25 |
| A sealed GTurbo airbox and a DPF inspection and clean, both required | Dust past the factory airbox seal is a common 70 Series fault and would wear the new rings, bores and turbo. Level A's emissions evidence needs a working DPF, and a high-kilometre filter holds ash that regeneration cannot burn off | Review M4 and M6, decision log 12:45 |
| New genuine Aisin H152F gearbox and NPC Super HD Organic 1300 clutch with billet flywheel | An all-new Toyota box costs about the same as a rebuild and needs no certificate. The organic disc takes up a heavy trailer smoothly and is rated to 1,300 Nm. Automatic conversions cost AUD 20,000 to 34,000 | Report 15, decision log 11:15 |
| The tune caps torque at 450 to 500 Nm in low range, first and reverse | Low range multiplies torque 2.488 times, and the 8 inch front diff and the CV joints are the weak link | Report 15 |
| No wide-track rear housing | Lovells rates the kit's 2,550 kg rear axle on the factory housing, Multidrive's housing is rated only to a 3,950 kg GVM, and a rear-only wheel offset would end the shared wheel. The Lovells Elite is the step up | Decision log 11:25, reports 15 and 16 |
| Lovells 4,200 kg Platinum kit TOYKIT080-GVM, or the 4,495 kg Elite, chosen at a decision gate once the bike box body is weighed. Fitted by Lovells' authorised fitter, LSPV reset | The Platinum carries report 16's planned 3,753 kg ute with 121 kg in hand on the rear axle, but only about 25 kg once growth is added to the estimates. It costs about AUD 8,620 with fitting and certificate, against about AUD 21,500 for the Elite. Choosing before either kit is bought avoids paying for both | Report 16, decision log 11:25 and 12:45 |
| Keep Toyota's 6,900 kg GCM | With the trailer at its 3,100 kg plate the planned combination is 6,603 kg, or 6,700 kg with the ute at its 3,850 kg limit. The rear axle binds before the GCM does | Report 16, decision log 12:10 |
| Factory disc brakes with slotted factory-size rotors, Bendix Ultimate 4WD pads, braided lines and DOT 4 | No certificate is needed. A big brake kit needs 17 inch wheels and would end the shared wheel | Report 16 |
| ROH Trak 2 16 x 7 ET 0 5 x 150 steel wheels with LT265/75R16 123/120 tyres on the ute and the trailer | It is Toyota's own wheel size and offset, so no certificate. One spare under the ute's tray and one on the trailer each fit both | Report 16, decision log 11:25 |
| Hayman Reese 03186RW towbar (or a factory bar rated 3,500 and 350 kg), REDARC Tow-Pro Elite V3, 12-pin flat plug, Anderson SB50 feed on 6 B&S cable with a 50 A fuse | A maker-certified bar on Toyota's mounts needs no certificate. One feed carries the trailer's 35 A charger | Report 16 |
| Coupling point 440 mm laden, plus or minus 20 mm | 450 mm plus 20 mm would go over VSB1's 460 mm limit | Decision log 12:10, layout-79.md section 3.5 |
| Keep the full reliable plan and list the cuts | Leonard asked for high reliability, and even every cut leaves the plan near AUD 61,000 | Decision log 11:25 |
| Bike box in welded aluminium, at most 1,850 mm wide (the cautious reading of Toyota's width rule), on Toyota's deck mounts, lighter than 440 kg, on the lowest deck that works. Its body is built and weighed before the GVM kit is chosen | The rear axle load and the rollover margin are tight with the bikes on board | Decision log 11:15, 11:25 and 12:45, reports 16 and 17 |
| One LC5 inspection for the GVM kit, the bike box and its winch | VSI 06 item 35 may treat the winch as a powered goods loading device, and the box replaces the tray on its own mounts | Review S2, decision log 12:45 |

### Figures reconciled in the merge

- **Engine certificate.** VSI 06 Rev 4 (issued 1 July 2026, the version report 16 cites) is used over Rev 3 (2013, read by report 14). Rev 4's item 6 gives, as a flash that needs a certificate, one "altering vehicle emissions output unless approved by the vehicle manufacturer and done in accordance with the vehicle manufacturer's instructions". A Toyota dealer's update is not caught, but a level A tune changes emissions, so it needs a certificate (line TL05, AUD 2,000, estimate).
- **VSI 06 item numbers.** This plan cites Rev 4. Rev 4 renumbered the driveline items, so report 15's gearbox item 6 is now item 7, its final drive item 7 is now 8 and its diff lock item 8 is now 9. The rules themselves read the same.
- **Rebuild kit.** GTurbo lists the NVP kit (AUD 2,470.68) for pre-DPF engines with the injectors inside the rocker cover only. This plan prices it as an estimate: the same parts and price, with the DPF engine's genuine gasket set ordered by VIN.
- **Trailer plate.** 3,100 kg in every sum (decision log 12:10), in place of report 16's 3,000 kg.
- **Starting batteries.** One battery, from Toyota's body builder's guide (via report 16), over report 15's assumption of two. That saves AUD 300.
- **Alternator.** About 130 A. Report 16 converts Toyota's 1,560 W at 14 V to about 110 A, but at the 12 V nominal it is 130 A, which matches report 15's 130 to 150 A. Either size carries the trailer charger's 35 A.
- **Duplicates.** Report 15's greasable shackles and pins (AUD 250) are in the Lovells kit, and its separate wheel alignment (AUD 150) is covered by the one after the kit. A new H152F comes with its input shaft seal (AUD 16.50) fitted, so the seal now sits in the gearbox cut. Steering fluid was bought twice, so AUD 30 comes out of the fluids line. The LSPV re-check this plan first added (AUD 100) is gone, because the box is now fitted before the one LSPV reset.
- **Contingency allowance.** 15 % of report 15's required lines as merged (AUD 15,396.69, so AUD 2,310), in place of report 15's AUD 2,400, which was 15 % of its lines before the merge.
- **Cuts.** AUD 15,735, not the decision log's AUD 10,000 to 11,000, because the DPF truck's injectors cost AUD 9,256 against AUD 4,290 for the earlier type.
- **Towball position.** 1,300 mm behind the rear axle (report 16) over 1,350 mm (report 17), now one position for every document (decision log 12:45). Moving the ball 50 mm changes the rear axle load by 50 / 3,180 = 0.016 kg per kg on the ball, about 4 kg at 250 kg.
- **Box and tools.** Report 16's 450 kg for tray and box plus 100 kg of tools is used for the limits over report 17's 440 kg body plus 60 kg of tools, because it is the heavier case.
- **Lines this plan adds.** The reflash certificate (AUD 2,000), the DPF inspection and clean (AUD 600), a new DPF as contingency (AUD 5,000), freight (AUD 1,000) and two weighbridge visits (AUD 60), all estimates, and the optional bull bar and winch (AUD 4,233). The sealed airbox (AUD 1,495) is report 14's line, now required.

## Budget

AUD including GST. The budget covers parts, outsourced work and certificates. It excludes buying the truck, Leonard's own labour, insurance, the bike box and the trailer. Every line is in `vehicle-parts.yaml`.

| System | Required | Contingency lines, if all of them happen | Optional |
|---|---|---|---|
| Engine rebuild and cooling | 12,717 | 1,500 | 400 |
| Fuel system | 11,398 | 0 | 0 |
| Sealed airbox and DPF service | 2,095 | 5,000 | 0 |
| Turbo, intercooler and exhaust | 8,519 | 0 | 0 |
| Tune, gauges and engine certificate | 5,210 | 200 | 0 |
| Clutch and gearbox | 6,744 | 0 | 300 |
| Transfer case, tailshafts, diffs and hubs | 3,073 | 6,697 | 7,325 |
| Steering and front suspension | 2,350 | 300 | 1,200 |
| Chassis, cab, electrical, fuel lines, air conditioning, fluids | 3,230 | 2,400 | 687 |
| GVM kit, fitting and certificate | 8,870 | 0 | 12,855 |
| Brakes | 1,540 | 0 | 0 |
| Wheels and tyres | 4,110 | 0 | 0 |
| Towing | 2,234 | 0 | 639 |
| Freight and weighing | 1,060 | 0 | 0 |
| Long-range fuel tank | 0 | 0 | 1,557 |
| Bull bar and winch, only if the truck has none | 0 | 0 | 4,233 |
| **Total** | **73,150** | **16,097** | **29,196** |

Freight is an allowance of AUD 1,000 (estimate). GTurbo in Perth ships the H152F on a 100 kg pallet and the NPC kit at 36 kg, and calculates freight at checkout. The exhaust, intercooler, airbox, radiator and smaller parcels travel too.

The contingency allowance is AUD 4,010. It carries the four small engine and tune lines in full (AUD 1,700) and 15 % of report 15's required lines as merged (AUD 2,310), which covers one or two of the driveline and refresh lines, such as a diff rebuild or a new transfer case. It leaves out a new DPF (AUD 5,000), because a DPF specialist replaces a filter only when it is cracked or melted, which the required clean and flow test shows. If the clean fails, add it. If every contingency line happened, the extra would be AUD 16,097.

The optional column is a menu, not a plan. Its biggest line is the Lovells Elite in place of the Platinum (net AUD 12,855), which the decision gate chooses or rules out. Level B later adds AUD 4,500, or AUD 14,500 with a laboratory emissions test, and is in none of these totals.

| Total | AUD | Against AUD 30,000 |
|---|---|---|
| Required | 73,150 | 43,150 over |
| Plus the contingency allowance | 4,010 | |
| Required with contingency | 77,160 | 47,160 over |
| Less every cut below | -15,735 | |
| With the cuts and contingency | 61,425 | 31,425 over |
| Bike box, outside the vehicle work | 13,900 | separate |

Without contingency, the plan with every cut is AUD 57,415.

### Cuts that keep it reliable

Each cut applies only if the old part passes its test. If it fails, buy the new part and the saving is lost. Report 14 notes that a 2017 to 2022 truck at 400,000 km has averaged at least 40,000 km a year, so most for sale will show less, which makes a pass more likely.

| Cut | Instead of | Saving | Risk |
|---|---|---|---|
| Test and reuse the eight piezo injectors (Denso specialist test and service, AUD 1,600, estimate) | New set, AUD 9,256 | 7,656 | A worn injector can fail early on the fresh engine. The AUD 1,600 is report 14's price for the earlier injector type |
| Bench-test and reuse the supply pump | New pump, AUD 1,480 | 1,480 | A worn pump sheds metal through the injectors and back to the tank |
| Flow-test and reuse the radiator | New radiator, AUD 1,756 | 1,756 | A part-blocked core runs hot on long grades at the higher power |
| Measure and reuse the oil pump | New pump, AUD 700 | 700 | Low, if it measures within specification |
| Rebuild the truck's own H152F with the Marks 4WD GBK9 kit (AUD 840.88) and a new input shaft seal (AUD 16.50), Leonard's labour | New H152F, AUD 3,840 | up to 2,983 | The best case. The kit's fit to the H152F is not confirmed, as its title names the 70, 75, 100 and 105 Series five-speed from 1998. Worn second-to-third synchros can need hubs, sleeves or gears beyond the kit. It reuses 400,000 km shafts and gears under 650 Nm |
| Keep a factory towbar rated 3,500 kg and 350 kg, if fitted | Hayman Reese 03186RW, AUD 1,160 | 1,160 | Low, if the plate shows both ratings and the mounts and receiver show no cracks |
| **Total** | | **up to 15,735** | |

## Order of work

Each step lists what it needs from the steps before it and who does the work when Leonard cannot. Step 6, the bike box body, can run alongside steps 3 to 5.

1. **Buy the truck.** Check the compliance plate for a build date from 01/2017 to 08/2022. Run report 15's pre-purchase checklist: a PPSR search for finance, write-off and theft records, the service history, ex-mine signs (beacon and antenna holes, mine-spec bars) and heavy corrosion, the rear spring hangers and the rails behind the cab for cracks or plates, the A-pillars and floor for rust, both rear hub faces with a digital angle gauge for a bent housing, and 2H, 4H, 4L and both diff locks on the test drive. Add the engine checks: compression on all eight cylinders, DPF warning lights and any limp mode, and by scan tool the injector correction values, the regeneration history and the DPF pressure reading. Then blow-by, an oil sample, oil in the coolant or coolant in the oil, turbo shaft play, and dust on the clean side of the air filter and in the intake pipe. Check that the bull bar is an airbag-compatible bar made for the 79 (its maker's label or papers) and that the winch works. Walk away from a write-off record, heavy corrosion, rusty A-pillars, flood signs, a cracked or plated chassis, a bent rear housing, a cracked block or head, or uncertified major work. Note whether a factory towbar rated 3,500 kg and 350 kg is fitted. Needs: nothing. Leonard does it.
2. **Baseline and certifiers.** Book the tuner who will write the tune and run the truck, as bought, on that dyno. This sheet is the stock baseline for the 20 % power cap. Weigh each axle with full fuel at a public weighbridge, so the decision gate in step 7 starts from real figures. Engage two VSCCS certifiers, or one licensed for both: LC4 for the tune, and a Lovells-endorsed LC5 certifier for the GVM kit, the bike box and its winch. Show the LC5 certifier the box design now. Certifiers may also ask for photos or inspections at stages. Needs: the truck unmodified. Outsourced: the dyno run, the weighbridge and the certifiers.
3. **Strip and refresh.** Pull the engine and gearbox. While they are out, rebuild the transfer case with the Koyo kit, send both tailshafts for new joints, centre bearing and balancing, and renew the pinion seals, breathers, swivel hubs, wheel bearings and hub seals. Remove the DPF and send it to a DPF specialist for an off-car clean and flow test. Crack-test the rear spring hangers, the rails behind the cab and the steering box mount, treat the rust, and renew the cab mounts, alternator, starter, battery, earth straps and fuel hoses. Service the air conditioning. Contingency work shows up here: a noisy diff, pitted CV joints, a cracked hanger, a dead compressor, a cracked DPF. Leave the steering and front bushes for step 8. Needs: step 2's baseline on the truck as bought. Outsourced: the tailshafts, the DPF clean, the air conditioning (a licensed technician), and any diff rebuild or chassis repair.
4. **Engine rebuild.** Strip the engine, take an oil sample, measure, and send the block, crank, rods and heads to the machine shop. Measure piston protrusion per bank, then order the NVP kit sizes, the DPF engine's genuine gasket set by VIN and the head gasket grades. Fit the timing set, oil and water pumps, cooling parts, glow plugs and mounts, clean the EGR and intake, and flush the tank and lines before the new pump and injectors see fuel. Pressure-test the oil cooler and check the vacuum pump for oil. Refit the engine with the NPC clutch, billet flywheel and new H152F, so the gearbox comes out only once. Refit the cleaned DPF, and fit the sealed airbox before the first start, so no dust reaches the new rings. Run the engine in on the factory calibration (assumption: about 1,000 km, report 14's distance for watching the oil level). Needs: the engine out from step 3, the cleaned DPF and the clutch kit, which takes 2 to 4 weeks to arrive. Outsourced: the machine shop, and a Denso specialist to test the old injectors and pump if Leonard takes those cuts.
5. **Power parts, tune and engine certificate.** If step 2's stock run read below about 96 rwkW (the lowest stock reading in report 14), the worn engine read low. Then repeat the stock run now, before these parts go on, and use that run as the baseline. Fit the VD-G333 turbo with its gasket kit, the front-mount intercooler, the DPF-back exhaust (keep the factory rear crossover pipe) and the gauges with the EGT probe before the turbo. Route the turbo actuator breather up high. The tuner writes the tune on the same dyno to the settings in the engine section. Book the TfNSW emissions test only with the cleaned DPF fitted and no stored fault codes. Then get the LC4 certificate for the reflash, have Service NSW endorse the registration record, and tell the insurer. Needs: the run-in engine, the new clutch, the cleaned DPF and step 2's sheet. Outsourced: the tune, the emissions test and the certificate.
6. **Build and weigh the bike box body.** Have an engineer review report 17's design against the limits below. Build the walls, roof and doors in welded aluminium and weigh them. Only the floor and subframe wait for the GVM kit's ride height and bump travel, so take their masses from the design. Needs: the cab width, deck-mount stations and axle weights measured in step 2. Outsourced: the engineer's review. Cost: about AUD 13,900, outside the vehicle work.
7. **Decision gate: Platinum or Elite.** Add up the rear axle load: step 2's weighed axles less any tray the box replaces, the weighed body, the design floor and subframe, the bikes, tools, people, one spare, the towbar and 250 kg on the ball, with growth on every figure that is still an estimate (the limits section shows the sum and the rule). If the rear axle stays at or under 2,550 kg, buy the Platinum. If not, take weight off the box, tray or ball first, then buy the Elite (rear axle 2,850 kg). Settle the front bushes from the chosen kit's contents and front lift: drop the AUD 450 bush line if the kit supplies them, and use caster-correction leading-arm bushes if it lifts the front. If the Elite is chosen, check what its brake upgrade includes before buying step 8's brake parts. Needs: steps 2 and 6, and the kit contents from Lovells' fitter. Leonard decides.
8. **Brakes, wheels, tyres, steering and front bushes.** Fit the slotted rotors, Bendix pads and braided lines, flush with DOT 4 and bed the pads in. Fit the steering ends, damper, exchange steering box and hoses, and the front bushes settled in step 7. Check the ROH wheel's nut seat against Toyota's steel-wheel nuts, then the tyre shop fits the six LT265/75R16 tyres. Needs: a running truck from step 5 and step 7's choices. It comes before the kit because the kit's placard needs tyres of at least load index 117 and speed rating M, and the certifier inspects the brakes bedded in. Outsourced: tyre fitting and balancing.
9. **GVM kit.** Lovells' authorised fitter fits the kit chosen in step 7. Until step 11's certificate the ute is still rated at Toyota's 3,400 kg GVM, so carry no bikes. Needs: step 7's choice, step 8's tyres, brakes, steering and bushes, and a sound chassis from step 3. Outsourced: all of it, because Lovells lets only its own fitters fit the kit for state compliance.
10. **Finish and fit the box, the winch and the towing gear.** Build the box floor and subframe to the kit's ride height and bump travel, bolt the box to Toyota's deck-mount stations, and fit the winch, ramp and restraints. Fit the Hayman Reese 03186RW to Toyota's mounting points (or keep a rated factory bar), the REDARC controller with its wiring kit and mount, the 12-pin socket and the Anderson SB50 feed with a 50 A fuse at the battery. The box overhangs the ball by about 210 mm, so check the plugs and chains under it now. Needs: the kit from step 9. Leonard does it.
11. **Alignment, LSPV reset and one LC5 inspection.** An alignment shop aligns the wheels, which also covers step 8's steering work, and resets the LSPV with the box on, as Toyota asks once a body is complete. The LC5 certifier inspects the kit, the box and the winch together, and a modification plate is fitted. Service NSW endorses the record, and the insurer is told. Needs: steps 8 to 10. Outsourced: all of it.
12. **Final weighbridge check.** Load the ute as it will travel, with people, bikes, tools, full fuel and one spare, and weigh each axle. Weigh again with the trailer coupled. Check every figure in the limits section. Choose the tongue drop for a coupling point of 440 mm, plus or minus 20 mm, laden (layout-79.md section 3.5), and set tyre pressures from the tyre maker's load table at the weighed loads. Needs: everything above. Outsourced: the weighbridge.

## Engine

Level A on a DPF truck, from report 14. Toyota dealer parts are ordered by VIN. GTurbo lists the NVP rebuild kit for pre-DPF engines only, so its price here is an estimate for the same parts with the DPF engine's genuine gasket set.

| Part | Part number | Supplier | AUD |
|---|---|---|---|
| NVP engine rebuild kit (pistons, rings, bearings, head gaskets, head bolts) with the DPF engine's genuine gasket set | Sizes ordered after machining, gasket set by VIN | GTurbo (North Vic Parts) | 2,471 (estimate) |
| Timing set, oil pump, glow plugs, engine mounts, genuine | Timing set 13506-51020 and others, rest by VIN | Toyota dealer | 2,350 (estimate) |
| Machine shop: block, bores, decks, mains, crank, rods, two heads | | Local machine shop | 4,200 (estimate) |
| Radiator | Natrad VDJ 2007 to 2025 | Natrad | 1,756 |
| Water pump, thermostat, fan clutch, hoses, coolant, genuine | By VIN | Toyota dealer | 1,540 (estimate) |
| Oil, filters, sealant, assembly lube | | Toyota dealer, parts store | 400 (estimate) |
| Eight genuine new piezo injectors | GTurbo DPF piezo set | GTurbo | 9,256 |
| Injector fitting kit, DPF engine | GTurbo DPF fitting kit | GTurbo | 190 |
| Supply pump, Denso HP4, new | 294050-0560 | GTurbo | 1,480 |
| Pre-filter and water separator, 30 micron | Direction Plus PL625DPK | Filters Plus | 432 (estimate) |
| Fuel filter element, genuine | 23390-51070 | eBay listing | 40 |
| High-flow airbox, sealed, takes the factory filter | A AB GT VDJ79 | GTurbo | 1,495 |
| DPF inspection, off-car clean and flow test | | DPF cleaning specialist | 600 (estimate) |
| VD-G333 Titan turbo, journal bearing | T T VD-G333T (web), T T 1VD-FTV S2.5B (booklet) | GTurbo | 4,290 |
| Turbo gasket kit | GTurbo VDJ70 kit | GTurbo | 299 |
| Turbo intake pipe, genuine | By VIN | Toyota dealer | 250 (estimate) |
| PDI front-mount intercooler, twin throttle, no radar bracket | A IC AA T3F-2.1 | GTurbo (PDI) | 2,200 |
| Manta 3 inch DPF-back exhaust, stainless, quiet | SSMKTY0123 | GTurbo (Manta) | 1,480 |
| Custom tune with the stock and tuned dyno runs | | GTurbo, HP-F or a local tuner | 2,000 (estimate) |
| Autometer boost, EGT and water temperature gauges | Autometer combo kit | GTurbo | 990 |
| Autometer oil temperature gauge | | Autometer dealer | 220 (estimate) |
| TfNSW emissions test | | Transport for NSW | 0 (assumed free) |
| VSCCS certificate for the reflash | | LC4 certifier | 2,000 (estimate) |
| **Engine total** | | | **39,939** |

Contingency lines: other head gasket grades (AUD 400), the oil cooler if it fails a pressure test (AUD 500), the brake vacuum pump if oil passes it (AUD 600), a new DPF if the filter is cracked or melted (AUD 5,000), and a gas analyser test if the TfNSW test is not available (AUD 200).

The sealed airbox matters because dust past the factory airbox seal is a common 70 Series fault, and it would wear the new rings, bores and turbo. The airbox keeps the emission controls, so it needs no certificate (VSI 06 item 5). The DPF clean comes first because the emissions test and the certificate need a working filter.

Settings for the tuner:

- Peak power at most 1.20 times step 2's stock peak, on the same dyno. For example, a 96 rwkW stock run allows 115 rwkW. On a truck that makes Toyota's 151 kW at the crank, the cap is about 181 kW.
- Torque about 650 Nm at the crank from about 1,800 to 2,700 rpm (estimate). Power reaches the cap near 2,660 rpm. Above that the tune holds power, so torque falls to about 510 Nm at 3,400 rpm (calculated).
- Torque capped at 450 to 500 Nm in low range, first and reverse.
- A towing map with less torque below about 1,600 rpm, to stop lugging.
- Fuel pulled from 650 °C EGT before the turbo, and never more than 700 °C.
- Factory light-load maps, EGR, DPF and catalyst functions left as they are.

Limits to drive to: coolant 90 to 104 °C when towing (over 107 °C for long means an airflow problem), oil 99 to 116 °C (over 121 °C sustained means a cooling review), and no full load below about 1,600 rpm. These are general diesel figures, not 1VD data.

Build notes: refit the support pole in the oil filter housing at every oil change, run the turbo actuator breather hose up into the engine bay, and mount the gauges below the top of the steering wheel (an NSW owner report says higher pods are not allowed).

## Driveline and refresh

From report 15, required list.

| Part | Part number | Supplier | AUD |
|---|---|---|---|
| NPC Super HD Organic 1300 clutch with matched billet flywheel | NPC7751-1D | GTurbo (NPC) | 1,818.50 |
| Clutch master cylinder | MCTY161 | Xtreme Outback | 131.38 |
| Braided clutch line | B-LINE-VDJ | GTurbo (NPC) | 154.00 |
| Clutch fork and pivot ball kit | ATFKTY28-08 | Xtreme Outback | 319.81 |
| Slave cylinder, release and spigot bearings, flywheel bolts, genuine | By VIN | Toyota dealer | 330 (estimate) |
| Genuine Aisin H152F five-speed gearbox, new, input shaft seal fitted | GT-H152-VDJ | GTurbo | 3,840 |
| Rear gearbox mount | By VIN | Toyota dealer | 150 (estimate) |
| HF1A transfer case rebuild kit, Koyo bearings | P004651 | HD Automotive | 653 |
| Both tailshafts: joints, centre bearing, balance | | Driveline shop | 900 (estimate) |
| Pinion seals, diff checks, breather extensions | By VIN | Toyota dealer, 4WD store | 320 (estimate) |
| Swivel hub kits, all wheel bearings, hub seals | By VIN | Toyota dealer | 1,200 (estimate) |
| **Clutch, gearbox, transfer case, tailshafts, diffs and hubs** | | | **9,817** |

The rest of the refresh is AUD 3,230, all estimates: dye penetrant kit 60, rust treatment 250, cab mounts 400, alternator 700, starter 450, one battery 300, earth straps and cables 150, wiring repairs 200, fuel hoses 150, air conditioning service 350, driveline fluids and swivel hub grease 220.

Contingency lines: a new transfer case if the gears or case are damaged (net AUD 2,297), a diff rebuild (AUD 1,300 each), heavy-duty front CV joints (AUD 1,800 a pair), chassis crack repair and bracing (AUD 1,500), an air conditioning compressor (AUD 900).

Settings and habits:

- H152F ratios: 4.529, 2.294, 1.490, 1.000 and 0.750, reverse 4.313. Transfer case 1.000 high and 2.488 low. Final drive assumed 3.909.
- At 100 km/h on the 804 mm tyre, fifth turns about 1,930 rpm and fourth about 2,580 rpm. Use fourth on long grades and into headwinds, so the engine does not lug in fifth.
- First in low range is 44:1, about 7 km/h at 2,000 rpm. Use low range for hill starts and for reversing the trailer. It saves the clutch more than any part.
- GL-4 75W-90 in the gearbox, because GL-5 additives attack the synchro brass. GL-5 in both diffs.
- If the tune cannot cap torque at 450 to 500 Nm in low range, first and reverse, the heavy-duty CV joints and two heavy-duty tailshafts become required (about AUD 5,800), and low range with the locks in is driven gently.
- Keep the factory diff ratio. A ratio change needs a certificate unless the speedometer is corrected.
- No gearbox cooler is planned. Temperature senders for the gearbox and rear diff (AUD 300, optional) show whether one is needed.

## Suspension and GVM

From report 16, plus report 15's steering and front bushes, which go on just before the kit (step 8). The kit itself is chosen at the decision gate (step 7).

| Part | Part number | Supplier | AUD |
|---|---|---|---|
| Lovells 4,200 kg Platinum GVM kit, single cab 2017 to 2022 | TOYKIT080-GVM | Lovells, through an authorised fitter such as Fulcrum Suspensions | 5,620 (estimate, a 2024 preorder listing) |
| Fitting by Lovells' authorised fitter | | Lovells authorised fitter | 1,500 (estimate) |
| VSCCS certification of the GVM kit, the bike box and its winch, one inspection | | Lovells-endorsed LC5 certifier | 1,500 (estimate) |
| Wheel alignment and LSPV reset, with the box fitted | | Alignment or brake shop | 250 (estimate) |
| Tie-rod and drag-link ends, genuine | By VIN | Toyota dealer | 500 (estimate) |
| Steering damper, heavy-duty | | Old Man Emu or Tough Dog stockist | 150 (estimate) |
| Power steering box, reconditioned exchange | | Steering specialist | 1,100 (estimate) |
| Power steering hoses and fluid | By VIN | Toyota dealer | 150 (estimate) |
| Front leading-arm, panhard rod and anti-roll bar bushes and links | | Toyota dealer, Nolathane or SuperPro stockist | 450 (estimate) |
| **Total** | | | **11,220** |

The kit holds front coils, rear leaf packs, remote-reservoir shocks, urethane bushes, U-bolts, greasable shackles and pins, mudflaps, side indicators and a new tyre placard. Contingency line: a cracked rear spring hanger (AUD 300 plus welding).

Ratings and settings:

- After the kit: GVM 4,200 kg, front axle 1,650 kg, rear axle 2,550 kg. The GCM stays at Toyota's 6,900 kg. Accept Lovells' 7,400 kg GCM only if the certifier includes it at no extra cost.
- Tyres of at least load index 117 (1,285 kg) and speed rating M (130 km/h).
- LSPV check with Toyota's gauge set 09709-29018 at Toyota's standard rear axle load: 5.9 MPa in the front circuit gives 4.9 MPa, plus or minus 0.5, at the rear, and 7.8 MPa gives 5.4 MPa, plus or minus 0.7.
- Front bushes: settle them at the gate from the chosen kit's contents and front lift. Drop the AUD 450 bush line if the kit supplies them, and fit caster-correction leading-arm bushes if the kit lifts the front.
- The step up is the Lovells 4,495 kg Elite: a 2,850 kg rear axle, a rear housing widened to the front track, chrome-moly axles, an exchange diff and a brake upgrade, for a net AUD 12,855 more. Choose it at the gate if the rear axle sum with growth tops 2,550 kg, or if the rear housing is found bent. Choosing it later costs more: an Elite after a fitted Platinum costs its full AUD 19,975 plus a second certificate, and the AUD 8,620 spent on the Platinum is lost.

## Brakes

From report 16. Every V8 79 has ventilated discs front and rear, so the factory calipers, master cylinder and booster stay. A different master cylinder or booster would need a certificate.

| Part | Part number | Supplier | AUD |
|---|---|---|---|
| Bendix Ultimate 4WD rear kit, two slotted rotors and pads | U4WD-BUK34 | Marks 4WD | 555.01 |
| Delios slotted front rotors | DLS0790 | Marks 4WD | 280.01 |
| Bendix Ultimate 4WD front pads | | Bendix stockist | 150 (estimate) |
| Braided brake lines, complete set | BQTL70S | Marks 4WD | 515 (midpoint of AUD 435 to 595) |
| DOT 4 fluid flush | | Any automotive store | 40 (estimate) |
| **Total** | | | **1,540** |

Bed the pads in before the LC5 inspection. If the gate chooses the Elite, check what its brake upgrade includes before buying these parts. The trailer's own electric brakes, set through the Tow-Pro controller, stop the trailer, so the ute's brakes do not do its work.

## Wheels and tyres

From report 16. Six of each: four on the ute and two spares, one under the ute's tray and one on the trailer. The trailer's four come from the trailer budget.

| Part | Part number | Supplier | AUD |
|---|---|---|---|
| ROH Trak 2 steel wheel 16 x 7, ET 0, 5 x 150, rated 1,400 kg, six at AUD 230 | | ROH stockists | 1,380 (estimate) |
| LT265/75R16 123/120R load range E, Yokohama Geolandar A/T G015 or Toyo Open Country A/T III, six at AUD 420 | | Tyre retailers | 2,520 (estimate) |
| Fitting and balancing, six at AUD 35 | | Tyre shop | 210 (estimate) |
| **Total** | | | **4,110** |

Settings:

- The tyre is 804 to 805 mm tall and carries 1,550 kg at 80 psi. The kit's rear axle needs 1,275 kg a wheel. The trailer needs 864 kg a wheel at its 3,100 kg plate under VSB1's 120 % rule (layout-79.md section 3.3).
- Pressures (estimates from report 16): rear about 53 psi at the planned 1,215 kg a tyre, front at least the placard's 250 kPa (36 psi), trailer about 26 to 30 psi on the highway. Use the tyre maker's load table at the weighed loads.
- Wheel nuts: assumption, Toyota's M14 x 1.5 steel-wheel nuts with a 21 mm hex suit the ROH wheel's nut seat (report 16). Check the seat against the nut before the tyre shop fits the wheels (step 8), because a nut with the wrong seat can work loose. Torque 209 Nm on these steel wheels. On the trailer, use the lower of 209 Nm and Cruisemaster's stud rating.
- The tyre is smaller than the placard's 225/95R16C, so the speedometer reads slightly high, which is legal.
- Trailer side: Cruisemaster LC5 M14 hubs (5 x 150) on its 12 inch ABS-enabled drums, 110 mm spigot, 900 mm axle spacing.

## Towing

From report 16. The ute is 12 V.

| Part | Part number | Supplier | AUD |
|---|---|---|---|
| Hayman Reese Class 4 towbar, 3,500 kg and 350 kg, 50 mm receiver, self-fitted | 03186RW | ARB | 1,160 |
| REDARC Tow-Pro Elite V3 brake controller | EBRH-ACCV3 | REDARC | 469.04 |
| Universal Tow-Pro wiring kit | TPWKIT-013 | REDARC | 255.99 |
| Tow-Pro universal mount | TPSI-001 | REDARC | 19 |
| 12-pin flat socket to AS 4177.5, with wiring | | Auto electrical supplier | 80 (estimate) |
| Anderson SB50 feed, about 8 m of 6 B&S twin cable, 50 A fuse at the battery | | Auto electrical supplier | 250 (estimate) |
| **Total** | | | **2,234** |

Settings:

- Coupling point 440 mm, plus or minus 20 mm, with the ute laden and the trailer level. The tongue drop sets it at step 12. VSB1 allows 350 to 460 mm laden, so 450 mm plus 20 mm would go over the limit (layout-79.md section 3.5).
- At most 250 kg on the ball. The bar takes 350 kg, but the rear axle binds first. The redesigned trailer puts 185 to 246 kg on it (layout-79.md).
- The controller's output goes to pin 5 of the 12-pin socket.
- The feed serves one Victron Orion-Tr Smart 12/24-15 in the trailer, which draws about 35 A and loses about 0.6 V over the 13 m loop. A second charger would draw about 70 A and need 2 B&S cable, so keep one.
- Fuse every added circuit, clip the cable at about 200 mm intervals and fit a grommet wherever it passes through metal (Toyota's wiring rules).
- No load distribution hitch. Toyota recommends one for a trailer over half the GVM, but none was found for the trailer's DO35 coupling, so the combination runs without one (report 16's assumption).
- The Hayman Reese X-Bar 03237RW with rated recovery points is optional, net AUD 639 more.

## Legal and paperwork

NSW registration, Victoria as the fallback. Item numbers are from TfNSW's VSI 06 Rev 4, issued 1 July 2026.

**Level A.** The plan assumed level A needs no certificate, as report 14 found under the 2013 revision, where only a power rise over 20 % (item 2) or higher emissions (item 5) triggered one. Rev 4 adds item 6, on re-programming or "flashing" the engine management system. Its example of a flash that needs a certificate is one "altering vehicle emissions output unless approved by the vehicle manufacturer and done in accordance with the vehicle manufacturer's instructions". A Toyota dealer's software update is not caught, but a tune that adds 20 % power changes the emissions. So the custom tune needs a VSCCS certificate from an LC4 certifier. Assumption: the certifier assesses it under VSB 14 code LA4 for about AUD 2,000, including the noise test (report 14's estimate), and accepts the TfNSW emissions test or the Interim NSW Vehicle Emissions Test Procedure (May 2023), which Rev 4 names as the alternative to testing to the standards. If the certifier asks for a laboratory ADR 79 test, add about AUD 10,000 or more (report 14's estimate).

Evidence to keep, with the certificate:

- The stock and tuned sheets from the same dyno, showing tuned peak power at most 1.20 times stock.
- The emissions test result, taken with the cleaned DPF fitted and no stored fault codes.
- Proof that the DPF, EGR, catalyst and crankcase ventilation all work, including the DPF specialist's clean and flow-test record. DPF-delete pipes are sold for off-road use only, and none is used here.
- Invoices showing the injectors and supply pump are genuine Toyota or Denso parts, so no non-original fuel equipment is fitted (items 5 and 49).
- Photos of each stage, which certifiers may ask for.

**GVM.** Re-rating the GVM needs a certificate (item 51). A registered ute cannot use the federal pre-registration path. Lovells lets only its authorised fitters fit the kit and only its endorsed signatories inspect it. A Lovells-endorsed LC5 certifier inspects the kit once the bike box and its winch are fitted too, so one inspection covers all three (decision log 12:45). A modification plate goes on and Service NSW endorses the record (about AUD 1,500, estimate, assumed to cover all three). The same certificate covers the kit's ride height change (item 13, assumption). At 4,200 or 4,495 kg the ute stays a light vehicle. Above 4,500 kg it would need a heavy vehicle examiner.

**Bike box and winch.** That the box needs no certificate of its own is an assumption, so it goes into the LC5 inspection. Item 35 needs a certificate for "any powered goods loading device, both internal and external to the vehicle", and the WARN winch that pulls each bike into the box may count as one. Item 27's no-certificate example is a like-for-like body on a full chassis, and a tall closed body in place of a tray may not count as one. Item 34 covers body mountings the maker did not design, and the box's mounts are custom. Assumption: the certifier signs off the box and the winch with the kit, with the engineer's review of the design as evidence.

**Noise and emissions.** The NSW in-service noise limit for a vehicle built to ADR 83/00 is its stationary noise "signature" plus 5 dB(A). The VDJ79's figure was not found. Assumption: the Manta "quiet" system passes, and the certifier's noise test confirms it. An exhaust and intercooler that keep the emission equipment need no certificate of their own (item 5).

**No certificate needed:** the new H152F, which fits the tunnel and bolts to the engine (item 7), the unchanged final drive (item 8), factory-size brake parts (items 18 and 19), the LSPV reset to Toyota's figures (item 20), the wheels and tyres at Toyota's size and offset (items 15 to 17), the sealed airbox, which keeps the emission controls (item 5), and the maker-certified towbar on Toyota's mounts (item 31). The optional 180 L fuel tank needs one (item 50) and goes in the LC5 inspection.

**Insurer.** TfNSW warns that cover can be void for undeclared modifications. Declare every change and both certificates, and keep the dyno sheets and emissions result with the policy. Get quotes before buying parts (assumption: cover is available with full disclosure).

**Level B later.** It needs a retune to 220 to 250 kW and a new LA4 assessment (about AUD 2,500 for the retune and AUD 2,000 for the certificate, estimates), plus emissions evidence at the higher power, possibly a laboratory test. The certifier may also ask for evidence that the driveline takes about 850 Nm (the clutch is rated 1,300 Nm, the H152F has no published rating) and that the brakes suit the GVM. Since level A now needs a certificate anyway, level B no longer adds a new kind of approval, only a second assessment at the higher power. Talk to the certifier with the level A truck built.

**Victoria.** VASS signatories apply VSB 14. Assumption: the same 20 % threshold and LA4 path (report 14). Whether Victoria has a rule like NSW item 6 was not checked. Choose the state of registration before the first certificate, because NSW does not recognise light vehicle certificates issued under an interstate scheme (VSI 06 Rev 4, page 3).

## Limits to build and drive to

From report 16's axle check unless stated. "Planned" is report 16's estimate for the built ute: 2,193 kg cab chassis, two people, bull bar and winch (assumed to come with the truck), 931 kg of tray, box, bikes and tools, two spares, the towbar and 250 kg on the ball.

| Limit | Value | Planned |
|---|---|---|
| Weighed ute, laden, including the ball load | At most 3,850 kg with the Platinum (GVM 4,200 kg) | 3,753 kg |
| Rear axle | At most 2,550 kg with the Platinum, 2,850 kg with the Elite | 2,429 kg, 121 kg in hand |
| Front axle | At most 1,650 kg | 1,324 kg |
| Towball download | At most 250 kg (the bar allows 350 kg) | 250 kg |
| Front axle share of the total, loaded | At least 20 % (Toyota's manual, page 3) | 35 % |
| The weighed ute plus the trailer, less the ball load, which both figures include | At most 6,900 kg (GCM) | 6,603 kg with the 3,100 kg trailer, 6,700 kg with the ute at its 3,850 kg limit |
| Trailer | ATM plate 3,100 kg, ball 185 to 250 kg and at least 6 % of the trailer's mass (decision log 12:10) | 185 to 246 kg on the ball (layout-79.md) |
| Bike box width | At most 1,850 mm, the cautious reading of Toyota's width rule (below) | About 1,760 mm inside, against the 1,680 mm the bikes need |
| Rear overhang, box and anything on it | At most 1,908 mm behind the rear axle (ADR 43/04). Toyota allows two thirds of the wheelbase (2,120 mm) when no cargo sticks out past the rear end (Toyota's manual, page 2) | 1,510 mm, report 17's box |
| Rear overhang with the doors open and a load past the rear end | At most half the wheelbase, 1,590 mm (Toyota's manual, page 2) | 1,510 mm, if nothing sticks out past the box |
| Centre of gravity, unladen, after building | Under 1,000 mm (Toyota) | About 840 mm with report 17's 440 kg box (estimate) |

Toyota's width rule says a mounted part may stand at most 60 mm beyond the outermost point of the cab, mirrors excluded. Read as 60 mm in all, as report 16 did, the box may be 1,850 mm wide. Read as 60 mm a side, as report 17 did, the same sentence allows 1,910 mm. This plan keeps 1,850 mm, the cautious reading.

### The rear axle sum with growth

The decision gate (step 7) uses this sum with weighed figures. Here it uses report 16's figures, with growth on the 469 kg of estimates (bull bar and winch, tray, tools, spares and towbar) at 20 % and on the 300 kg box at 7 %. Toyota's kerb mass, the people, the bikes and the ball limit carry none.

| Case | Ute | Front axle | Rear axle | Rear axle in hand |
|---|---|---|---|---|
| Report 16's planned ute, both spares on it | 3,753 kg | 1,324 kg | 2,429 kg | 121 kg |
| The same with growth | 3,868 kg | 1,343 kg | 2,525 kg | 25 kg |
| With growth and one spare on the trailer, as decided | 3,823 kg | 1,353 kg | 2,471 kg | 79 kg |

Figures are rounded to the kilogram. On a GXL at the heavy end of Toyota's kerb range, the rear axle carries up to 22 kg more. So the Platinum's margin rests on estimates, and the gate replaces them with weighed figures before a kit is bought.

What binds:

- The rear axle binds first. Each kilogram at the tray centre adds about 1.04 kg to it, and each kilogram on the ball adds 1.41 kg. On report 16's figures it reaches 2,550 kg at about 3,870 kg in total, and with growth the planned ute is within 25 kg of it.
- Report 17's rear axle figure of about 2,260 kg leaves out the bull bar, spares and towbar. Report 16's 2,429 kg includes them, so it is the one to build to.
- The plan assumes the bought truck already has an airbag-compatible bull bar and winch, the 110 kg in these sums. If it has none, the optional ARB Deluxe bar and a winch add AUD 4,233.
- The GCM never binds first. With the 3,100 kg trailer the ute could weigh 4,050 kg before reaching it (6,900 less 3,100 plus 250), which is more than the rear axle allows. The growth case comes to 6,718 kg.
- If the gate's sum goes over 2,550 kg on the rear axle, take weight off the box, tray or ball first, then choose the Elite. If the final weighing (step 12) still finds the ute over 3,850 kg or the rear axle over its rating, take weight off before towing.

Rollover margin. The static stability factor (SSF) is half the average track divided by the height of the centre of gravity. A lower SSF means a higher risk of rolling over in a single-vehicle crash. Report 17 puts the ute at about 1.02 with the bikes in the trailer and about 0.80 with the box, both bikes and tools aboard, because the centre of gravity rises about 200 mm. A lower deck at 850 mm wins back about 0.04. Build to the lowest deck that works and a box lighter than 440 kg, and keep heavy tools low. The box also adds about 1.2 m² of frontal area and crosswind load, so corners and crosswinds with the bikes aboard are the case to drive carefully.

## Open questions

Each carries the assumption this plan uses.

1. Will an LC4 certifier certify the level A reflash on the TfNSW test or the Interim NSW procedure, without a laboratory test? Assumption: yes, for about AUD 2,000 (report 14's LA4 estimate).
2. Is the TfNSW emissions test still free? Assumption: yes, as Rev 3 said. Rev 4 names the test but gives no fee. The fallback, a gas analyser test at a repairer for about AUD 200, is in the contingency. Either test is taken with the cleaned DPF fitted.
3. Can the tune cap torque at 450 to 500 Nm in low range, first and reverse? Assumption: yes (report 15). If not, AUD 5,800 of heavy-duty CV joints and tailshafts become required.
4. What torque does the H152F take? Assumption: a new box survives 650 Nm in high range with sensible driving (report 15). No rating is published.
5. Will the worn engine's stock run read low? Assumption: it reads inside the published 96 to 120 rwkW. If lower, repeat it after the rebuild (step 5).
6. Can the eight piezo injectors be tested and reused, and at what cost? Assumption: AUD 1,600, report 14's price for the earlier injector type.
7. Which bushes does the chosen kit supply, and does it lift the front? Assumption: its three urethane bush kits cover the rear springs and the front keeps its height, so report 15's AUD 450 of front bushes stays. Settled at the gate (step 7).
8. What do the bought ute's axles weigh? Assumption: Toyota's mid-range 1,280 kg front and 913 kg rear for the cab chassis (report 16), until step 2's weighing replaces them.
9. Where does the ball sit? Assumption: 1,300 mm behind the rear axle (report 16), one position for every document (decision log 12:45).
10. What is the final drive ratio? Assumption: 3.909, which matches the reported 1,930 rpm at 100 km/h in fifth (report 15).
11. Do the dealer parts and the machine shop cost what report 14 says? Assumption: yes, within 30 % and 25 %.
12. What do Lovells' fitting and the LC5 inspection cost, and does the inspection cost more with the box and the winch? Assumption: AUD 1,500 each, with one inspection covering the kit, the box and the winch (report 16's range for the inspection is AUD 1,000 to 2,500).
13. What do the ROH wheels and the tyres cost, and which nut seat does the wheel take? Assumption: AUD 230 and AUD 420 each, and Toyota's M14 x 1.5 steel-wheel nuts (report 16). Check the seat in step 8.
14. Will the LC5 certifier sign off the box and the winch with the kit? Assumption: yes, in one inspection, with the engineer's review of the design as evidence (items 27, 34 and 35).
15. Does the Manta quiet exhaust meet the noise limit? Assumption: yes, and the certifier's noise test confirms it.
16. Does the front-mount intercooler starve the radiator when towing slowly in heat? Assumption: no. Watch the coolant gauge on the first long tow. The fallback is GTurbo's AUD 1,895 fan kit on the factory top mount (report 14).
17. Does the combination need a load distribution hitch? Assumption: no, as none was found for the DO35 coupling (report 16).
18. Will an insurer cover the tuned ute? Assumption: yes, with full disclosure.
19. Does Victoria have a reflash rule like NSW item 6? Assumption: report 14's 20 % threshold and LA4 path. Not checked.
20. Does the NVP kit's parts set fit the DPF engine? Assumption: the same parts and price as the pre-DPF kit GTurbo lists, with the DPF engine's genuine gasket set ordered by VIN.
21. Does the clean restore the DPF? Assumption: yes, for about AUD 600. A specialist replaces a filter only when it is cracked or melted, about AUD 5,000 (estimate), which is outside the contingency allowance.
22. Does the bought truck have an airbag-compatible bull bar and winch? Assumption: yes, as report 16's 110 kg assumes. If not, the optional lines add AUD 4,233.
23. What does freight cost? Assumption: AUD 1,000 in all.

## Prices that are estimates

Estimates make up AUD 39,503 of the AUD 73,150 required, or 54 %. Each is marked `estimate` in `vehicle-parts.yaml`.

Required lines:

- Engine rebuild and cooling, AUD 10,961: rebuild kit 2,471 (the pre-DPF kit's listed price, assumed for the DPF engine), timing set 900, oil pump 700, glow plugs 400, engine mounts 350, machine shop 4,200 (block clean and crack test 250, bore and hone 650, decks 300, line hone 400, crank 400, rods 400, heads 1,400, valve allowance 400), water pump 450, thermostat 90, fan clutch 450, hoses 400, coolant 150, oil and sundries 400.
- Fuel system, AUD 432: the pre-filter, priced from a similar kit.
- Sealed airbox and DPF service, AUD 600: the DPF inspection and clean.
- Turbo, intercooler and exhaust, AUD 250: the turbo intake pipe.
- Tune, gauges and engine certificate, AUD 4,220: tune 2,000, oil temperature gauge 220, VSCCS certificate for the reflash 2,000, and the emissions test assumed free.
- Clutch and gearbox, AUD 480: slave cylinder 150, release and spigot bearings 120, flywheel bolts 60, rear gearbox mount 150.
- Transfer case, tailshafts, diffs and hubs, AUD 2,420: tailshafts 900, pinion seals and checks 200, breathers 120, swivel hub kits 450, front wheel bearings 300, hub seals 100, rear wheel bearings 350.
- Steering and front suspension, AUD 2,350: every line (ends 500, damper 150, steering box 1,100, hoses and fluid 150, front bushes 450).
- Chassis, cab, electrical, fuel lines, air conditioning and fluids, AUD 3,230: every line (dye kit 60, rust treatment 250, cab mounts 400, alternator 700, starter 450, battery 300, earth straps 150, wiring 200, fuel hoses 150, air conditioning 350, driveline fluids 220).
- GVM, AUD 8,870: every line (kit 5,620 from a 2024 preorder listing, fitting 1,500, certificate 1,500, alignment and LSPV reset 250).
- Brakes, AUD 190: front pads 150, fluid flush 40.
- Wheels and tyres, AUD 4,110: every line (wheels 1,380, tyres 2,520, fitting 210).
- Towing, AUD 330: 12-pin socket 80, charging feed 250.
- Freight and weighing, AUD 1,060: freight 1,000, weighbridge 60.

Contingency lines, AUD 13,800 of AUD 16,097: head gasket grades 400, oil cooler 500, vacuum pump 600, new DPF 5,000, gas analyser test 200, two diff rebuilds 2,600, CV joints 1,800, spring hanger 300, chassis repair 1,500, air conditioning compressor 900. Only the new transfer case (net 2,297) comes from a listing.

Optional lines: balancing 400, temperature senders 300, heavy-duty tailshafts 4,000, Air Locker fitting 1,280, heavy-duty tie rod and drag link 1,200, 240 A alternator 300, the winch 1,500, and level B's retune 2,500, certificate 2,000 and laboratory test 10,000.

Cuts: the injector test and service, AUD 1,600.

Bike box: about AUD 13,900 (report 17).

Listed prices with a caveat: the Natrad radiator (read from a search extract) and the braided brake lines (the midpoint of a listed AUD 435 to 595).

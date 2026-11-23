# Ford Ranger Super Duty tow vehicle

Revised 23 Nov 2026 for Leonard's change of plan of 22 Nov 2026 (research report 31): a near-new Ford Ranger Super Duty single cab chassis, bought, in place of the rebuilt LandCruiser VDJ79. The LandCruiser plan of decisions H17, H18, H20 and H24 and research reports 14 to 16, 23, 26 and 27 is kept as the record in the repository's history and in those reports. From 23 Nov 2026 the trailer is plated at 4,000 kg on a DO45-type coupling, which worker plate4t chooses. Every part and paid job is a line in `data/vehicle/vehicle-parts.yaml`, which the site's Tow vehicle page renders as three lists and `cad/tests/test_costs.py` checks against this page.

## Summary

The truck is a Ford Ranger Super Duty single cab chassis, built 2025 or 2026, with under about 20,000 km. Ford rates it at a 4,500 kg GVM, 1,900 kg on the front axle and 2,800 kg on the rear, 4,500 kg braked towing and an 8,000 kg GCM, and it comes with front and rear lockers, a 130 L tank, a 4.5 t tow bar and hitch, an integrated trailer brake controller, a 12-pin socket and a snorkel (Ford's dealer specification sheet, issued 18 Sep 2025). Leonard wrote 4,495 kg for the GVM, and this plan uses Ford's 4,500 kg. So the plan buys no GVM kit, no GCM revision, no engine rebuild, no clutch and no brakes. It carries both bikes in Leonard's box (H25) on Ford's body mounts and tows the trailer at its new 4,000 kg plate, inside Ford's ratings from the day it is bought.

The truck costs AUD 92,690: the one near-new listing found, a 2025 truck with 13,343 km at AUD 89,990, and AUD 2,700 of NSW duty. A new one costs about the same drive-away, with no tray to sell and Ford's conditional 7-year warranty (report 31 section 4).

Four stages follow, each leaving the truck registered and drivable. The build is AUD 17,302, or AUD 20,550 with one allowance of 10 % on listed prices and 20 % on estimates (AUD 3,248), against Leonard's AUD 75,000 for the car work. Estimates are 88 % of it, because most lines have no published price. P1, what makes the truck legal, safe and able to tow, is AUD 5,882: the purchase inspection, the coupling's tow pin, the trailer charging, towing mirrors, a UHF radio, a compressor, a recovery kit and three weighings. P2, the power stage with its certificate, is AUD 11,420.

Leonard asked for about 250 to 300 hp at the wheels from a turbo upgrade. That cannot be planned as registrable and reliable. 250 hp at the wheels needs about 220 kW at the crank (est.), 43 % over the Super Duty's 154 kW, which leaves the only turbo sold here with a maker's record, Garrett's PowerMax, no flow in hand, and 300 hp needs parts nobody sells for this engine. The plan registers about 205 kW and 650 Nm at the crank, about 232 hp at the wheels (est.), on the PowerMax turbo and intercooler with a calibration of the engine and the 10-speed, the DPF, SCR and EGR untouched, under one LC4 certificate. Ford's warranty will not pay for a failure the stage causes, so it waits until Leonard accepts that or the warranty ends.

The check list holds the lines bought only if a check calls for them, AUD 12,478 if every one were bought, which is a note and not a total. The optional extras, a bar and winch, rock sliders and driving lights, come to AUD 7,400. The bike box (AUD 27,870, built by Leonard, `data/ute/box-parts.yaml`), the trailer and Leonard's labour are outside these figures.

## The truck against the LandCruiser plan

| | Super Duty AUD | LandCruiser plan AUD | Difference AUD |
|---|---|---|---|
| Truck | 92,690 | 50,000 | 42,690 |
| Upgrades with the allowance | 20,550 | 77,777 | -57,227 |
| Together | 113,240 | 127,777 | -14,537 |

The LandCruiser figures are Leonard's AUD 50,000 for a used VDJ79 and that build's AUD 77,777 with its allowance (this file to 22 Nov 2026). The Super Duty costs AUD 42,690 more to buy and AUD 57,227 less to make ready, AUD 14,537 less in all, and it starts with a new engine under warranty in place of a 400,000 km one. Its AUD 20,550 includes the AUD 13,704 power stage with its allowance, so the truck alone, legal and able to tow with the trailer charging, is AUD 6,846 with the allowance.

## Stage plan

| Stage | Work | Build AUD | Check list AUD | Paid labour | Downtime (est.) | The truck can then |
|---|---|---|---|---|---|---|
| S0 | Choose, inspect, buy and weigh the truck | 482 | 0 | Ford dealer, weighbridge | None | Drive, and tow within Ford's ratings once the tow pin is in |
| S1 | The box on Ford's body mounts, the tow pin, towing mirrors, UHF radio, compressor, recovery kit, the trailer's profile, a laden weighing | 3,505 | 650 | None, Leonard fits them | 1 to 2 weeks | Carry both bikes in the box and tow the 4,000 kg trailer at stock power |
| S2 | The trailer charging and the coupled weighing | 1,895 | 928 | Auto electrician, weighbridge | 1 day | Tow the loaded trailer and charge it while driving |
| S3 | PowerMax turbo and intercooler, the calibration, the emissions test and the LC4 certificate | 11,420 | 10,900 | Tuner, emissions test, LC4 certifier | 1 to 2 weeks | Tow at about 205 kW and 650 Nm at the crank (est.), certified |
| Total | | 17,302 | 12,478 | | | |

The check list column is what a stage would cost if every check line fitted in it were bought, and it is not counted. S0 to S2 are the truck Leonard needs, in that order. S3 comes when Leonard accepts the warranty risk or when Ford's warranty ends, and nothing before it depends on it.

### S0 Buy, inspect and weigh

Goal: buy a sound, untuned truck and know what it weighs.

- Look for a 2025 or 2026 single cab chassis under about 20,000 km with a build plate of 4,500 kg GVM. A new or demonstrator truck at about the same drive-away price is as good a buy (report 31 section 4), and one without a tray saves selling the tray.
- Run a PPSR search (BI02). Walk away from money owing, a write-off record or a theft record.
- Have a Ford dealer inspect it (BI01): a scan with Ford's diagnostic tool for stored faults and any non-Ford flash, the DPF and AdBlue data, the frame, body mounts and tow bar for damage, and a road test in Tow/Haul with the lockers tried. Walk away from a tuned or modified engine, a bent frame or a damaged tow bar.
- Check that the truck has Ford's 4.5 t hitch (RB3Z-17D826-A in the BEMM), and read the maximum tow ball download from its owner's manual or the hitch's label. The plan assumes 450 kg (est.) until then.
- Take off the tray, if one is fitted, and sell it (not counted).
- Weigh each axle with a full tank (CK01). Ford publishes no kerb weight on each axle.
- AUD 482.
- Done when the truck is bought, has no fault stored and its axle loads are known.

### S1 Box, towing kit, mirrors and touring gear

Goal: carry both bikes and tow the 4,000 kg trailer legally at stock power.

- Fit the box to Ford's body rules (BEMM sections 1.10, 1.13 and 5.6, 03/2026): at most 1,960 mm wide, at least 28 mm behind the cab and 30 mm over it, a rear overhang of at most 50 % of the 3,270 mm wheelbase, bolted at every standard body mounting location with two M10 bolts of grade 8.8 or better, a cross member at each mounting point, no welding on the frame beyond what the BEMM allows, and no new hole larger than 16.5 mm. The box's own design and checks are `UTE-GARAGE.md` (rsd-ute).
- Keep Ford's Driver Assistance Technology bar, with the rear lamps, camera and blind spot sensors, at its factory place, and keep the box's overhang to it as Ford's BEMM sets (sections 4.3 and 4.5). Check the rear camera, the 360-degree view, the blind spot monitor and the onboard scales with the box on, and have a Ford dealer calibrate them only if one shows a fault (BF01).
- Fit Cruisemaster's DO45Plus tow pin, 32 mm shank, in Ford's 4.5 t hitch (TW01). The pin takes the place of a ball, so no ball is bought. The shank must fit the hitch hole firmly, and the hitch must not be drilled (BEMM section 1.13). If it does not fit, or the coupling sits outside its height range laden, fit a 4.5 t tongue with a 32 mm hole and the right drop (TW02). plate4t confirms the coupling and its height.
- Set up the trailer's profile in SYNC for the integrated trailer brake controller, the blind spot monitor's trailer coverage and Pro Trailer Backup Assist, whose sensor goes on the trailer's drawbar (Ford's towing guide). Set the brake gain on the first tow.
- Fit the Clearview towing mirrors (TM01), the UHF radio (UH01) and carry the compressor (AC01) and the recovery kit (RK01) in the box.
- Weigh the laden truck, each axle (CK02).
- AUD 3,505. Check lines AUD 650.
- Done when the weighed axles and GVM are inside Ford's ratings with the box, bikes, tools and two people aboard.

### S2 Trailer charging

Goal: charge the trailer's 48 V battery from the truck on travel days.

- Fit two Victron Orion-Tr Smart 12/48-8 chargers in a vented cover low in the box front (TC01, 8.4 kg), fed from the spare stud on Ford's power distribution block through a 100 A fuse and grounded at a Ford ground point, never at the battery negative, because the battery sensor must see every load (BEMM section 4.2). Their engine-off detection gives the 12.7 V cut-off Ford asks for on high loads.
- Run the 48 V feed to a grey Anderson SB120 at the tow bar (TW06, 4.2 kg): 4 B&S twin, sized for four chargers, so the feed holds 2 % at 32 A with the trailer's half (SVC-06).
- The two chargers put about 3.6 kWh into the trailer on a 5 h drive and draw about 62 A. Ford's alternator gives 145 A at idle and 250 A from 2,500 rpm (BEMM section 4.2.4), so no alternator upgrade is planned.
- Log the truck's battery voltage on the first hot night tow. Two more chargers (TC02) go in only if the trailer ends travel days short and the voltage holds at 13.5 V or more.
- Weigh the laden truck alone and coupled to the loaded trailer (CK03). Set tyre pressures from the placard, 65 psi in the rear tyres near GVM (Ford's payload guide).
- AUD 1,895. Check line AUD 928.
- Done when the coupled weighing is inside every Ford rating and the chargers run on a long tow.

### S3 Power stage and its certificate

Goal: about 205 kW and 650 Nm at the crank, certified, with every emission control working. Needs S2 done and a long tow logged at stock power.

- Get the LC4 certifier's written evidence list before buying anything (TL05). If it asks for a laboratory emissions test rather than the interim NSW procedure, that is AUD 10,000 (TL07, est.), and the stage waits for Leonard's decision.
- Book the tuner's dyno and run the truck stock first, the first of the same-dyno runs the certifier compares (TL01).
- Leonard fits the Garrett PowerMax turbo 930592-5001S (PW01) and the PowerMax intercooler (PW02), with new gaskets and fluids and Garrett's shaft speed sensor (PW03). Ford's turbo is kept for a return to stock.
- The tuner calibrates the engine and the 10-speed together and keeps Ford's files: about 205 kW at the crank, at most 650 Nm in high range, Ford's 600 Nm in low range, first and reverse, Ford's EGT limits, the turbo under Garrett's 186.2 krpm on the sensor, and the DPF, SCR, EGR and crankcase ventilation untouched.
- Fit the OBD gauge (TL02) for EGT, boost, the 10-speed's temperature and coolant temperature.
- Drive the uncertified calibration only to the emissions test and the certifier. Test to the interim NSW procedure with no stored faults (TL04), then get the certificate (TL05). If it is refused, refit Ford's turbo and flash Ford's files back, and the truck is as bought.
- Tow the trailer up a long grade and watch the 10-speed's temperature. A larger cooler goes in only if it stays above 110 °C (TX01, est.).
- Cut CUT1 tunes on Ford's turbo to the ordinary Ranger's 184 kW instead, about 208 hp at the wheels (est.), saving AUD 3,960 with its share of the allowance.
- AUD 11,420. Check lines AUD 10,900.
- Done when the certificate is endorsed on the registration and a long tow stays inside the temperature limits.

## Parts list by system

AUD including GST. Every line, with its list, priority, reason, stage and dependencies, is in `data/vehicle/vehicle-parts.yaml` and on the site's Tow vehicle page, where each check line also gives what to check, when, and its pass mark.

| System | Build | Check list | Optional | Largest build lines |
|---|---|---|---|---|
| Purchase inspection | 452 | 0 | 0 | Ford dealer inspection 450 |
| Freight and weighing | 210 | 0 | 0 | Freight 120, three weighings 90 |
| Towing and trailer charging | 1,990 | 1,278 | 0 | Charging 1,612, 48 V feed 254, DO45Plus tow pin 125 |
| Mirrors, radio, compressor and recovery | 3,350 | 300 | 0 | Towing mirrors 1,750, UHF 650 |
| Turbo and intercooler | 5,650 | 900 | 0 | PowerMax turbo 3,300, intercooler 1,900 |
| Tune, gauge, emissions test and certificate | 5,650 | 10,000 | 0 | Calibration 2,800, certificate 2,000 |
| Bar, winch, sliders and lights | 0 | 0 | 7,400 | None. Every line is an extra |
| Total | 17,302 | 12,478 | 7,400 | |

Each figure is rounded to the dollar, so a column can differ from its total by AUD 1.

| Total | AUD |
|---|---|
| The build | 17,302 |
| Allowance, 10 % of listed prices and 20 % of estimates | 3,248 |
| The build with its allowance | 20,550 |
| Leonard's figure for the car work | 75,000 |
| Under that figure, with the allowance | 54,450 |
| Less CUT1, with its share of the allowance | -3,960 |
| The build with CUT1 and the allowance | 16,590 |
| Check list, if every line were bought (not counted) | 12,478 |
| Optional extras (not counted) | 7,400 |
| The truck, bought (data/project.yaml) | 92,690 |

By priority: P1 (legal, safe and able to tow, or protecting the truck) is AUD 5,882 of the build, and P2 (the power stage) is AUD 11,420. The optional extras are AUD 7,400.

The allowance follows the trailer's rule: 10 % of the build's listed prices (AUD 2,129) and 20 % of its estimates (AUD 15,174). The check list carries none, because each of its prices is already the price if the line is bought, and it is not added to the build. The one cut, CUT1, is there in case the PowerMax turbo cannot be had or the certifier balks at its power: the calibration then runs on Ford's turbo.

## Limits to build and drive to

Ford's ratings are the limits (dealer specification sheet, 18 Sep 2025, and the BEMM, 03/2026). The estimates below are this plan's base masses: Ford's minimum kerb weight of 2,518 kg with a full tank and no tray, the 437 kg box, both bikes at 390 kg with the Tuareg's panniers, 60 kg of tools with the compressor and recovery kit, two people at 160 kg, and the truck's added lines at 32.6 kg (the tow pin and hitch 9.5, charging 12.6, mirrors 4.0, radio 1.5 and the power stage 5.0, all est.), 3,598 kg in all (est.). The ute model (`build/ute/ute.json`, rsd-ute) carries growth and the axle split and supersedes these figures once it models the Super Duty.

| Limit | Value | Estimate, base masses |
|---|---|---|
| Truck, laden, ball load included | At most 4,500 kg GVM | 3,998 kg with a 400 kg ball, 10 % of the trailer's 4,000 kg plate |
| Front axle | At most 1,900 kg | From the ute model |
| Rear axle | At most 2,800 kg | From the ute model |
| Truck plus trailer | At most 8,000 kg GCM | 7,598 kg, the truck without its ball load plus the trailer's 4,000 kg plate |
| Trailer | At most 4,500 kg braked towing, and the coupling's own rating (plate4t) | 4,000 kg plate |
| Ball load | At most 450 kg until the owner's manual is read (est.), and the coupling's vertical rating | 400 kg at 10 % (est.) |
| Payload | At most 1,982 kg on the minimum kerb weight, ball load included | 1,480 kg |
| Box | At most 1,960 mm wide, 28 mm behind the cab, 30 mm over it, rear overhang at most 1,635 mm, at every standard mounting location (BEMM 1.10 and 5.6) | rsd-ute |
| Added mass's centre of gravity | At GVM: 1,965 to 3,350 mm behind the front axle, at most 530 mm up and 65 mm off the centre line. At 800 kg added: to 3,255 mm, 630 mm and 130 mm (BEMM 1.13.2) | rsd-ute |
| Trailer width for the blind spot monitor | At most 2.4 m wide and 10 m long behind the truck, on the factory tow bar (Ford's towing guide) | 2,400 mm |

Ford's Smart Hitch reads the ball load within 100 kg and recommends 10 to 15 % of the trailer (towing guide). The trailer's own range is plate4t's and the trailer's.

Drive to: Tow/Haul mode on every tow and whenever the truck is heavily loaded (Ford's payload guide), rear tyres at 65 psi near GVM, the trailer's brake gain set on its first tow, and after S3 EGT, boost and the 10-speed's temperature inside the tuner's limits on the gauge, with the 10-speed at most 110 °C sustained (est.). Use low range for steep hill starts and reversing the trailer.

## Legal path

NSW registration. VSI 06 Rev 4 applies to light vehicles of 4.5 t GVM or less (page 1), and the Super Duty, at 4,500 kg, is one.

The truck as bought needs nothing. Ford's 4,500 kg GVM, 8,000 kg GCM and 4,500 kg braked towing apply as built, so the trailer's 4,000 kg plate needs no revision of the truck's ratings. The factory tow bar, Ford's 4.5 t hitch and its integrated brake controller are the maker's, and the trailer's own brakes on every wheel and its breakaway system are the trailer's (VSB1, above 2,000 kg ATM). The coupling is plate4t's.

The box. Leonard builds it and does not have it certified (H25). It is a body on a cab chassis built to take one, mounted to Ford's own rules (S1), so it adds no ratings. The towing mirrors replace the factory pair with the same functions, and the plan assumes they need no certificate.

The power stage (S3). Every tune of this truck needs a VSCCS certificate: VSI 06 Rev 4 item 6 for flashing the engine management system so that it alters emissions output, and item 2 because about 205 kW is more than 20 % over the original 154 kW, the line being 184.8 kW. VSB 14 files it under LA4, modifying the original engine, and treats it like a performance engine conversion: emissions, brakes, installation and noise (report 14 section 4.2). Ford certified the truck to the heavy-duty Euro VI standard, tested on an engine dyno, and VSI 06 lets the Interim NSW Vehicle Emissions Test Procedure for Modified and Individually Constructed Vehicles (May 2023) stand in for testing to the standard (note to item 5). The plan assumes the LC4 certifier accepts it. Keep the same-dyno sheets, the emissions result, the parts invoices, the tuner's description of the calibration and a fault-free scan. The PowerMax intercooler needs no certificate of its own (item 5's examples). Nothing in the plan touches the DPF, the SCR or the EGR.

Ford's warranty. Ford says an aftermarket part does not by itself void the warranty, but a failure it causes is not covered ([Ford Australia](https://www.ford.com.au/support/how-tos/warranty/warranties-and-coverage/do-aftermarket-accessories-affect-the-warranty)). After S3 a failed engine, turbo, 10-speed or transfer case is where a claim would be refused. That is the stage's real cost, and why it waits for Leonard's go or the warranty's end. Declare every change to the insurer.

## Decisions

| Decision | Reason |
|---|---|
| A near-new Ranger Super Duty single cab chassis, bought, in place of the LandCruiser build | Leonard's change of 22 Nov 2026. Ford's ratings carry the box and the trailer with no GVM kit or GCM revision, and it costs AUD 14,537 less than the LandCruiser plan in all |
| Ford's 4,500 kg GVM, not 4,495 kg | Ford's dealer specification sheet and payload guide give 4,500 kg |
| Near-new or new at the same drive-away price | The one near-new listing and a new truck land within about AUD 3,000 of each other, and a new one has no tray to sell and Ford's longer warranty |
| Cruisemaster's DO45Plus tow pin in Ford's own 4.5 t hitch, no 70 mm ball | The trailer's plate went to 4,000 kg on a DO45-type coupling (conductor, 23 Nov 2026), and the BEMM forbids drilling the hitch or fitting a ball that does not fit its hole |
| Clearview towing mirrors in the build | The 2,400 mm trailer is wider than the truck's 2,197 mm mirror span, and these keep the camera and blind spot functions |
| Two chargers on Ford's 250 A alternator, wired as the BEMM says | The alternator gives 145 A at idle, so no upgrade, and the battery sensor must see every load |
| A UHF radio, a compressor and a recovery kit as the only touring gear | Remote roads have no mobile coverage, Ford asks for 65 psi at GVM, and the lockers do not free every bogged truck. Ford already fits the bar, underbody protection, snorkel, lockers, all-terrain tyres and the 130 L tank |
| About 205 kW and 650 Nm at the crank, not 250 to 300 hp at the wheels | The most that can be registered and kept reliable on parts sold here with a record (report 31 section 8) |
| Garrett PowerMax turbo and intercooler with a calibration of the engine and 10-speed | Garrett makes Ford's turbo, and its 27 % more flow keeps about 14 % in hand at 205 kW |
| Torque at most 650 Nm, Ford's 600 Nm in low range, first and reverse | Ford rates the 10-speed's engine at 600 Nm, and power comes from holding torque higher up the rev range |
| The DPF, SCR and EGR untouched | Removing them is unlawful (VSI 06 Rev 4 item 5) and Leonard asked for nothing that needs it |
| The power stage last, when Leonard accepts the warranty risk or the warranty ends | Ford does not pay for failures a tune or turbo causes, and every earlier stage stands without it |

## Open points and the assumption used

1. What is the Super Duty's maximum tow ball download? Not in the Ford documents read on 23 Nov 2026, and the BEMM points to the owner's manual. Assumed 450 kg (est.), 10 % of the 4,500 kg rating. Read it at S0.
2. How does the kerb weight split between the axles? Not published. The ute model estimates it, and CK01 measures it.
3. Does the DO45Plus pin's 32 mm shank fit Ford's 4.5 t hitch hole firmly? Assumed yes. If not, a 4.5 t tongue with a 32 mm hole (TW02, AUD 350 est.). plate4t confirms the coupling.
4. Do the Clearview Next Gen mirrors fit the Super Duty? Assumed yes, as it shares the Ranger's cab and doors. Confirm by VIN.
5. Will an LC4 certifier accept the interim NSW emissions procedure for a heavy-duty Euro VI calibration? Assumed yes. If not, a laboratory test (TL07, AUD 10,000 est.) or the truck stays stock.
6. Can a tuner write the Super Duty's calibration? Assumed yes, since tuners already calibrate the V6 and its 10-speed in the ordinary Ranger. If none can, S3 waits.
7. What do the PowerMax turbo and intercooler cost here? No price is published. Assumed AUD 3,300 and 1,900 (est.).
8. Is the single cab chassis a non-passenger vehicle for NSW duty? Assumed yes, AUD 3 per AUD 100.
9. Does the box keep Ford's driver assistance sensors working? Assumed yes, with the Driver Assistance Technology bar at its factory place. If not, a Ford dealer calibration (BF01, AUD 300 est.).
10. Is the 48 V feed's 7 m right on the Super Duty? Kept at 7 m until the box's route is drawn. The run is probably shorter, which only lowers the drop.

# Whole trailer: layout for the LandCruiser 79

Status: concept, revision H, 20 Nov 2026. This is layout 1 of the layout study (`layout-79.md` in the planning notes): a queen bed across the front, a fixed roof and a 4,420 mm body, towed by the LandCruiser 79. The data is `data/assemblies/trailer.yaml`, `data/load_cases.yaml`, `data/checks.yaml` and `data/measurements.yaml`. The code is `cad/trailer.py`, and drawing CT-001 is the general arrangement. The site's Whole trailer page shows the current build.

Leonard asked: "Then, I'll put an enclosed box at the back to fit the two bikes and some tools. That way, we can make the trailer smaller and lighter." And: "Then, let's redesign our whole plan to to this new vehicle."

## What changed in revision H, 20 Nov 2026

- The bikes ride in the ute's bike box (UTE-GARAGE.md), so the trailer's garage and bed module is gone. Its parts, its checks and drawings CT-401, CT-402 and CT-501 are retired. `DESIGN.md` carries a retired note.
- The body is 4,420 mm long in place of 5,500 mm, with a fixed roof and 1,950 mm inside. The queen bed lies across the front. There is no rear door, no ramp and no raising roof.
- The tow vehicle is the LandCruiser 79 single cab V8 on a Lovells 4,200 kg GVM kit, in place of the Porsche Cayenne. Its limits come from `data/ute/ute.yaml` and the built ute model.
- The ATM is plated at 3,100 kg (decision log 12:10). The towball target is 220 kg fully loaded, and the cap is 250 kg.
- All 400 L of water ride in the trailer. The car's water tank and the ballast are gone.
- The generator and the jerry cans ride in a sealed drawbar box, DX-01. The jockey wheel moves forward to X 1,000 mm.
- The trailer runs the ute's wheel and tyre: ROH Trak 2 16 x 7 ET 0 with LT265/75R16 123/120 on Cruisemaster LC5 hubs. The XT Air axles are 900 mm apart, and the track is 1,555 mm, the ute's front track.
- The coupling point is at Z 440 mm, the ute's laden ball height (UTE-01).
- New checks: GCM-01 for the combination, and JK-01 and JK-02 for the jack-knife sweep of the bike box.
- The first build failed three checks, and each part was resized. The outriggers grew from RHS 100 x 50 x 3 to RHS 125 x 50 x 3 (FAT-05 was 23.5 MPa against a 21.1 MPa limit, now 16.8 MPa). The heater's diesel tank got its own bay between two crossmembers (FIT-03 found a 50 mm overlap). The entry door moved 5 mm rearward (BDY-18 was 298 mm against 300 mm). The cassette toilet and its service door moved forward to keep 150 mm from the rear corner.
- No check limit changed, and no estimate changed to pass a check.

The earlier revisions are in the git history. Revisions C to G placed the garage at the back, gave the trailer its own wheels, added the designed chassis and built in report 13's equipment.

## Datum

The project datum DIM-01 (research report 02): X rearward from the coupling ball centre, Y positive to the road side, Z up from the ground at design ride height, all in mm. It is right-handed, so the model shows the real trailer, with the entry door on the left when you look from behind.

## Body

- 4,420 mm long and 2,400 mm wide outside, from X 1,820 to 6,240 mm. The inside is 4,350 mm long and 2,330 mm wide.
- Floor surface at Z 925 mm. Inside height 1,950 mm, for people up to about 1.88 m tall (assumption, layout-79 open question 3).
- Fixed 40 mm roof bonded to the walls, with the four Sunman solar panels on it. Travel height 2,917 mm to the top of the panels.
- Overall length 6,300 mm, from the coupling head to the body rear. Overall width 2,500 mm with the awning.

BODY.md revision B has the panels, joints, mounts and checks.

## Zones, front to back

| Zone | Inside X (mm) | Kerb side | Middle and road side |
|---|---|---|---|
| Bed | 1,855 to 3,505 | Kitchen slide-out under the bed (hob and sink), under the awning | Queen mattress 1,530 x 2,030 mm across the trailer, its top 750 mm above the floor. Truma Saphir air-conditioner under it. Bedside column of shelves at the road-side end |
| Living area | 3,505 to 5,205 | Entry door (Aussie Traveller DC, 622 mm wide), then the fridge (Dometic NRX 130C) | Desk 1,100 x 550 mm with two seats and its cabinetry, then the washer, the Truma Combi D 6 and the Victron board |
| Rear | 5,205 to 6,205 | Freezer (Dometic CFX3 55IM) on its bench, then the tall cupboard in the rear corner | The 1 x 1 m wet bathroom in the rear corner |

- Under the floor, between the rails: two water tanks over the axles (about 420 L net, estimate), the heater's 15 L diesel tank in its own bay under the bed, and the sealed battery box near the rear wall.
- Floor space stays clear at the entry door, the bathroom door, the desk seats and a walkway between them (FIT-01).
- One sleeper climbs over the other to get out of the bed (layout-79 open question 4). Layout 2 is the fallback, in the open questions.
- The rear-corner rule keeps 150 mm of full wall between an opening and a panel edge, so the cassette toilet and its service door moved forward (BDY-18).

## Running gear, coupling and drawbar

- Suspension: Cruisemaster XT Freestyle Air, the 4,500 kg build, with the axles 900 mm apart. The axle group centre is at X 4,199.8 mm. The kit's GTM is 4,050 kg (Cruisemaster), and MAS-02 applies VSB1's 120 % rule to it.
- Hubs and brakes: Cruisemaster LC5 M14 (5 x 150), 110 mm spigot, on the 12 inch ABS-enabled drums, with the Bosch TSC (ABS and sway control).
- Wheels and tyres: ROH Trak 2 16 x 7 ET 0 steel with Yokohama Geolandar A/T G015 LT265/75R16 123/120, load range E, 1,550 kg per tyre. The wheel's 1,400 kg rating is ROH's fitment table (WHL-01). The trailer and the ute share the wheel, so one spare on each fits both. The trailer's spare rides on the body's front wall above the drawbar.
- Track 1,555 mm, the ute's front track, so the trailer runs in the ute's ruts. With C/F 190 mm (SUP-04) and ET 0, each wheel sits 190 mm outside its rail, inside Cruisemaster's 200 mm limit.
- Coupling: Cruisemaster DO35 at Z 440 mm, the ute's laden ball height. The drawbar drop below the rail underside is solved from it.
- Drawbar: an A-frame of RHS 150 x 50 x 5, 1,820 mm from the ball to the body front, as in revision G. The stone guard, the chains and the breakaway kit are as before.
- Drawbar box DX-01: sealed 2 mm aluminium, X 1,150 to 1,470 mm, 960 mm wide and 520 mm high, 15 kg (estimate), on brackets across the drawbar members. A lockable lid, a low vent and a drain to outside. It holds the Honda EU22i generator and the petrol and diesel jerry cans, so no fuel rides inside the body (FIT-04 checks the fit, with 20 mm in hand). The generator runs outside the box.
- Jockey wheel at X 1,000 mm, ahead of the box.

## Axle position and the towball

The build moves the axle group until the fully loaded case (TC2) carries 220 kg on the ball on base weights. That is the middle of the decision log's 200 to 250 kg band, so the growth allowance stays inside the 250 kg cap. The solve put the axle group centre at X 4,199.8 mm, 170 mm behind the middle of the body. No ballast is needed in any case, because the trailer has no bikes to take out. The water tanks sit over the axles, so the towball barely changes as the water is used.

## Load cases

Mass in kg. The towball comes from moments about the axle group centre (MASS-04). "With growth" adds report 02's growth allowance (MASS-06): 20 % on an estimate, 7 % on a calculated mass and none on a maker's figure.

| Case | What is aboard | Mass | Towball | Share | Axle group | With growth | Towball with growth |
|---|---|---|---|---|---|---|---|
| TC1 Tare as built | Empty tanks, no fuel or gear | 2,196 | 178.6 | 8.1 % | 2,018 | 2,423 | 197.6 |
| TC2 Travel fully loaded | 400 L of water, fuel and gear | 2,776 | 220.0 | 7.9 % | 2,556 | 3,036 | 246.0 |
| TC3 Highway travel | 50 L of water, fuel and gear | 2,426 | 217.5 | 9.0 % | 2,209 | 2,686 | 243.4 |
| TC4 Water full, no gear | 400 L of water and fuel | 2,626 | 196.9 | 7.5 % | 2,429 | 2,856 | 218.2 |
| TC5 Tanks empty, gear aboard | Fuel and gear | 2,376 | 217.1 | 9.1 % | 2,159 | 2,636 | 243.0 |
| TC6 Tanks empty, no gear | Fuel only | 2,226 | 193.9 | 8.7 % | 2,032 | 2,456 | 215.3 |

- The heaviest case with growth is TC2 at 3,036 kg, 64 kg under the 3,100 kg plate (MAS-01).
- The towball runs from 178.6 to 220.0 kg on base weights and from 197.6 to 246.0 kg with growth, inside the 250 kg cap (MAS-03). The lowest share is 7.5 %, above the 6 % floor (MAS-04).
- Fully loaded, the axle group carries 2,790 kg with growth, or 3,349 kg with VSB1's 120 % rule, against the XT build's 4,050 kg GTM (MAS-02). Each tyre carries 837 kg with the rule against 1,550 kg (MAS-06) and 1,400 kg for the wheel (MAS-09).

## Mass

The tare is 2,196.5 kg, or 2,423 kg with growth. That is 167 kg lighter than revision G's 2,363 kg tare with its garage.

| Group | Tare kg | With growth kg |
|---|---|---|
| Chassis and drawbar | 532.3 | 570.2 |
| Body | 578.3 | 645.2 |
| Living area | 371.6 | 411.8 |
| Running gear | 345.6 | 396.6 |
| Under the floor | 145.9 | 155.4 |
| Bed | 72.4 | 84.5 |
| Coupling and drawbar fittings | 46.0 | 50.3 |
| Spare wheel | 37.1 | 40.0 |
| Drawbar box | 36.1 | 37.7 |
| Roof (solar panels) | 31.2 | 31.6 |

The least certain lines are the XT Air kit (180 kg, 36 kg of growth), the cabinetry (70 kg), the body extrusions and fixings (68.5 kg), the wiring and plumbing (60 kg) and the clothes and bedding (60 kg). If the clothes and bedding came out 20 % heavier, the fully loaded towball would rise 4.3 kg, because they sit in the bed zone at the front.

## The ute and the combination

The ute is the Toyota LandCruiser VDJ79 GXL single cab V8 on the Lovells 4,200 kg GVM kit, with the bike box (UTE-GARAGE.md and VEHICLE.md). The trailer build reads its limits from `data/ute/ute.yaml` and its masses from the built ute model, so the ute is built first.

- Towball: the plan caps it at 250 kg, inside the Hayman Reese 03186RW's 350 kg. Each kilogram on the ball adds about 1.4 kg to the ute's rear axle, which is the ute's binding limit (UTE-GARAGE.md section 9).
- Braked towing: the 3,100 kg plate is inside Toyota's 3,500 kg.
- GCM-01 takes the larger of two sums against Toyota's 6,900 kg GCM. The plan's sum is the ute at its 3,850 kg weighed limit, plus the 3,100 kg plate, less the 250 kg the ute already carries on its ball: 6,700 kg. The model's sum is the ute's UC2 case with growth (3,546 kg) plus the heaviest trailer case with growth (3,036 kg): 6,582 kg. GCM-01 measures 6,700 kg, 200 kg in hand.
- Coupling height: the ute's tongue is set so the ball sits at 440 mm laden, plus or minus 20 mm (UTE-01), so the coupling stays inside VSB1's 350 to 460 mm (DIM-03 and the ute's UTE-13).
- Ball position: 1,300 mm behind the ute's rear axle (UTE-02, report 16 and the decision log 12:45, estimate).
- Jack-knife: the bike box overhangs the ball by 210 mm at its body and 255 mm at its door hardware. At 90 degrees it sweeps a radius of 948.5 mm from the ball, set by the road-side wall skin. Its underside sits at Z 780 mm. JK-01 measures from the ball to the nearest trailer part that stands higher than the box's underside less 50 mm, less the sweep radius, and needs 100 mm. It is the drawbar box, 201.5 mm clear. JK-02 takes the highest trailer part inside the sweep radius plus 100 mm, and needs it 50 mm below the box's underside, an allowance for the ute's pitch (assumption). It is the stone guard top at Z 608 mm, 172.5 mm below.

## Chassis inputs

CHASSIS.md revision B designs the frame for this layout. The main figures it takes from the layout:

- Rails: RHS 150 x 50 x 3 with an RHS 125 x 50 x 3 raiser on top, 4,420 mm long, 1,175 mm over their outsides. Rail top at Z 747.5 mm, floor underside at Z 895 mm.
- Eight stations, each with an outrigger at raiser height on both sides. The outriggers are now RHS 125 x 50 x 3, the raiser's section. A fixed station closes the diesel bay.
- Fully loaded centre of gravity at X 3,867 mm and Z 1,124 mm, or Z 1,131 mm with growth, 741 mm above the hub centres.
- The frame analysis scales every case so the heaviest sits at the 3,100 kg plate. The highest utilisation is 0.78, in the kerb-side rail under the rear recovery point (LC8a). The travel cases run from 0.21 (LC1, LC2) to 0.42 (LC3 braking, in the drawbar). The chassis weighs 474 kg galvanised.
- The tyre clears every chassis member by 54 mm through its full travel, against 50 mm (FIT-05).

## Checks

Every fail check passes. The figures that matter most:

| Check | Model | Limit |
|---|---|---|
| MAS-01 heaviest case with growth | 3,036 kg | 3,100 kg plate |
| MAS-03 towball with growth | 246.0 kg | 250 kg |
| MAS-04 lowest towball share | 7.5 % | at least 6 % |
| MAS-05 towball fully loaded | 220.0 kg | 210 to 230 kg |
| GCM-01 combination | 6,700 kg | 6,900 kg |
| DIM-02 front load space against the rear overhang | 2,380 mm | at least 2,040 mm |
| DIM-03 coupling height | 440 mm | 350 to 460 mm |
| DIM-04 running clearance, unladen | 380 mm | at least 100 mm |
| JK-01 sweep clearance | 201.5 mm | at least 100 mm |
| JK-02 below the box | 172.5 mm | at least 50 mm |
| FIT-04 drawbar box fit | 20 mm in hand | no overlap |
| TWS-01 chassis twist | 0.439 degree | 0.5 degree |
| FAT-05 outrigger toe | 16.8 MPa | 21.1 MPa |
| BDY-16 body mounts | 0.32 | 1.00 |

The NSW examiner caps GTM at the lowest of the tyre, coupling, chain and brake ratings and ATM at the lower of the coupling and chain ratings. With four 1,550 kg tyres, the 3,500 kg DO35 and chains and the 4,500 kg drums, both caps are 3,500 kg (MAS-07 and MAS-08). The design plates the trailer lower, at 3,100 kg.

## Power

The power system is report 13's, at 24 V, unchanged from revision G except where it rides:

- Batteries: two Victron Lithium NG 25.6 V 200 Ah (10.24 kWh), 37 kg each, in a sealed aluminium box under the floor near the rear wall, with a Lynx Smart BMS NG.
- Inverter-charger: Victron MultiPlus-II 24/5000, on the board on the road side of the living area.
- Solar: four Sunman eArc 430 W panels (1,720 W) bonded to the fixed roof, in two pairs, each to its own SmartSolar MPPT 150/45.
- From the ute: one Orion-Tr Smart 12/24-15 isolated charger on the ute's Anderson SB50 feed with a 50 A fuse (VEHICLE.md, towing).
- Generator: Honda EU22i in the drawbar box, run outside it.

The daily load is about 10.4 kWh on a hot day and 5.1 kWh on a cold one. The batteries carry about 4 hot days or 1.5 overcast winter days before the generator has to run (report 13).

## Registration

The trailer will be registered in NSW, with Victoria as the fallback, by report 02's path for a concessional trailer: a TfNSW identity approval with form 5703, photos, a weighbridge ticket with the tare and the VIN, and receipts for the materials. The examiner checks the design against VSB1 and sets the plate figures. The plate asked for is 3,100 kg ATM. The tyre placard shows LT265/75R16 123/120 and the cold pressure for the weighed load.

## Measured inputs

Every value the owner will measure is an input in `data/measurements.yaml`, with how to measure it, the estimate and its source, an empty measured slot, and the rules that change the plan. The build uses the measured value when there is one.

- UTE-01, the ute's laden ball height (440 mm, estimate), sets the coupling point and the drawbar drop.
- UTE-02, the ball's distance behind the ute's rear axle (1,300 mm, estimate), sets the ute's axle loads and the bike box's sweep.
- UTE-03, the towball scale reading once the trailer exists, is compared with the model (TBS-01, reported).
- WHL-01 and SUP-01 to SUP-04 are the wheel's rating and Cruisemaster's answers.
- The bike and chock inputs (TU-01 to TU-09, ST-01, CHK-01) now set the ute's bike box, not the trailer.

## Assumptions

Where something is unknown, the design takes the best assumption, records it here with its source, and carries on.

1. The drawbar box DX-01: 960 x 320 x 520 mm, 15 kg (estimate), sized round the Honda EU22i and the jerry cans with 20 mm in hand (FIT-04). It follows report 02's garage rules for fuel: sealed from the body, reached only from outside, vented low and drained.
2. The diesel jerry cans ride in the drawbar box with the petrol, not under the bed. The heater keeps its own 15 L tank under the floor.
3. The jockey wheel at X 1,000 mm, ahead of the box, so the box clears its handle.
4. JK-02's 50 mm allowance for the ute's pitch between the ball and the box's underside. Report 16 gives no figure.
5. The ball 1,300 mm behind the ute's rear axle (report 16 and the decision log 12:45). Report 17 used 1,350 mm.
6. A tyre envelope 272 mm wide (estimate) and a loaded radius 20 mm under the free radius (the repo's estimate). Both set the floor height, the tyre's gap to the rail and the hub height (layout-79 open question 9).
7. The bed ledgers, 2,030 mm on the front wall and 1,650 mm on the kerb wall (3,680 mm in all), carry the whole 255 kg bed at 3 g (BDY-11).
8. The roof uplift scaled to the fixed roof's area: 5,060 N at 40 m/s (BDY-19), from report 12's 6.3 kN on the raising lid.
9. The bond in the roof-to-wall joiner at 2 MPa in tension (MS polymer, estimate), so the joint holds 30 N/mm.
10. The new estimated lines from layout-79 open question 12, each at 20 % growth: the bed base 20 kg, the bedside column 15 kg, the tall cupboard 12 kg, the cupboards over the fridge 8 kg.
11. The fire extinguisher and blanket at 4.8 kg (estimate), by the entry door.
12. The body mount is the M12 8.8 bolt into a welded nut plate on the raiser (CH-P14), at 0.32 of its capacity. The HB10 blind bolt would work at 0.87, but with less margin, so it is not used.
13. The corner steadies at X 2,220 mm and 6,070 mm, bolted to the rails about 400 mm inside the body ends (layout-79 section 4.3).
14. The inside height of 1,950 mm suits both people, up to about 1.88 m tall (layout-79 open question 3).
15. The tanks: two blocks 975 mm wide and 288 mm high over the axles hold about 420 L net (layout-79 open question 8).
16. No roof hatches. Five opening windows, the Carafan CP700 intake and the bathroom vent ventilate the body (layout-79 open question 5).
17. The awning is the Fiamma F45s 450 on brackets within 100 mm of the body.

## Open questions

These are design decisions for the owner. Each carries the assumption the plan uses until it is answered.

1. The ATM plate. Assumption: 3,100 kg. A 3,000 kg plate holds every case on base weights (224 kg in hand) but not TC2 with growth (3,036 kg). Plate 3,000 kg if the largest estimates (the XT Air kit 180 kg, the cabinetry 70 kg, the extrusions 68.5 kg) weigh in about 30 kg lighter on base weights, which takes 36 kg off TC2 with growth.
2. The climb over the bed. Assumption: one sleeper climbing over the other is accepted. The fallback is layout 2 of the layout study: the queen bed along the trailer at the back, with a 400 mm strip on each side, so each sleeper gets out on their own side. It also has a fixed roof and 1,950 mm inside. It costs a body 830 mm longer (5,250 mm) and 137 kg heavier (estimate). Choosing it re-runs every check in this document.
3. The kitchen bench height. With the floor at Z 925 mm the slide-out's bench is about 1,425 mm above the ground. Assumption: report 13's folding step goes with the kitchen.
4. A dryer, LPG or a third battery (report 13 open questions 1 to 3). The defaults are a washer with no dryer, no LPG and two batteries. Each reversal adds tare: about 50 kg for the washer-dryer, 27 kg for LPG and 37 kg for a third battery. With the 64 kg in hand under the plate, only one of them fits without a heavier plate.
5. The drawbar members at the 3,100 kg plate. VSB1's drawbar forces fall 11 % from the 3,500 kg design. Assumption: keep RHS 150 x 50 x 5. The engineer may lighten them to RHS 150 x 50 x 4, about 14 kg.

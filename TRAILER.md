# Whole trailer: block layout (baseline)

Status: concept, revision G, 20 Nov 2026. Revision G builds in the appliances and equipment from research report 13, with three owner choices taken as defaults until the owner answers: a washer with no dryer, no LPG, and two batteries (10.24 kWh). Real products replace 14 estimated lines, so the tare falls 271 kg to 2,363 kg, the axle re-solves from X 5,021 to 5,004, and every mass check now passes with the growth allowance except MAS-03, the towball with the bikes out. Revision F takes the tyre at Yokohama's published 752 mm diameter in place of the calculated 749.4 mm, which raises the floor 2.6 mm to Z 872 and restores the 50 mm clearance over the tyre. It also counts the corner steadies once: BD-10 is now the mud flaps only, because the chassis design carries the four corner steadies (CH-B01). The tare falls 17 kg to 2,634 kg and the axle re-solves from X 5,013 to 5,021. Revision E replaces the block chassis with the designed chassis and drawbar (CHASSIS.md, report 11), which is 73 kg heavier, and the axle re-solves from X 5,036 to 5,013. Revision D, updated on 19 Nov for the car's water tank, carries 200 L in the trailer's tanks fully loaded and the other 200 L in the car. Revision D gives the trailer its own wheels and tyres (report 09), because Porsche confirmed that none of its 18-inch wheels is rated for the trailer's load, and adds a full-size spare on the body's front wall. The car keeps its own 20-inch wheels and carries its own spare (report 10). Revision C moved the garage and bed module to the back of the body with a rear door (DESIGN.md revision D), so the living space is one room, and moved every heavy item towards the back so the towball stays inside the Cayenne's limits. Revision B put Cruisemaster's XT Air in place of the coil. Each block is an envelope with a mass, not a design. Items marked OPEN need the owner's decision. Positions marked PLACEHOLDER in the data are not designed yet. The data is `data/assemblies/trailer.yaml`, the load cases are in `data/load_cases.yaml`, the checks in `data/checks.yaml`, and the arithmetic is in `cad/trailer.py`. Drawing CT-001 is the general arrangement. Sources are research reports 02 and 06 to 11, and the owner's older block model for the item list and most masses. The chassis and drawbar are designed in CHASSIS.md.

## Datum

Every position here is in the project datum from report 02 (DIM-01). X runs along the trailer from the coupling ball centre, positive rearward. Y runs across from the centreline, positive to the road (right) side. Z is up from the ground with the trailer level at design ride height. Units are mm and kg. This is a right-handed frame, so the 3D model, the STEP files and the drawings show the trailer as it is. DIM-01 changed to it on 20 Nov 2026 (report 02 note): before that, Y was positive to the kerb side and the model was a mirror image.

The garage and bed module keeps its own frame, and its axes are the datum's. Module X 0, the rear face of partition A, sits at X 4,955 in the 5,500 mm body, and the garage floor (module Z 0) at Z 872. The module ends at the rear wall's inner face, X 7,285.

## Body

The body is 2,400 mm wide with 35 mm walls, so the inside is 2,330 mm. The interior height is 1,800 mm from the floor with the roof down, as in DESIGN.md. The pop-top roof is designed later, and a 45 kg allowance carries its lift mechanism and skirt. Its lid carries the four bonded solar panels.

The recommended body length is 5,500 mm. It is the shortest of the three compared that holds the living area, and the 5,000 mm body is 470 mm short (see Body length). The floor is flat for the whole length, level with the garage floor, because the ladder lands on the living-area floor at that level.

The floor height follows from the running gear. The tyre is 752 mm across (LT245/70R16, Yokohama's published diameter) and its static loaded radius is taken as 20 mm less than its free radius (estimate), which puts the hubs at Z 356. At full bump the XT rises 60 mm, so the tyre top reaches Z 792. With 50 mm clearance (estimate) the floor underside is at Z 842, and a 30 mm floor panel puts the floor surface at Z 872, 14 mm higher than with the shared 18-inch wheel. The 3,048 mm ramp then sits at 16.6 degrees, or 15.5 degrees with the air bags vented. Travel height to the top of the solar panels is 2,714 mm, roof down. The bonded panels are 2 mm thick, so the travel height fell 48 mm from 2,762 mm with the framed glass panels.

## Zones, front to back

The drawbar carries the coupling, the stone guard and the jockey wheel. There is no drawbar box: its generator, gas and fuel moved into the garage in revision C. The jockey wheel is an ARK XO750, 20 kg (report 13 section 6). The trailer's full-size spare wheel stands on the body's front wall above the drawbar, centred across the trailer, on two carrier posts from the body front crossmember (revision E, CHASSIS.md). There it keeps the rear door and the bike ramp clear.

The living area runs from the front wall to partition A, 3,080 mm inside. The heavy items stand as close to partition A as the plan allows. The wet bathroom (1 x 1 m) fills the road-side corner against partition A, with a Thetford C223-CS cassette toilet and a DauerShower 2.0 recirculating shower. Beside it against partition A stand the Camec 3.5 kg washer, then the Truma Combi D 6 diesel heater and hot water unit with the XT Air supply and the spare airbag on top of it, and the ladder on the kerb side, which hooks on the deck edge. The heater's box grew to 450 x 525 x 300 mm, so the washer's box narrowed to 470 mm and the heater clears the ladder by 5 mm. The Victron 24 V board (inverter, chargers and battery management) hangs on partition A above the washer and the heater, out of the garage and above its 500 mm ignition-free zone. In front of the bathroom on the road side stand the Dometic NRX 130C fridge and then the Dometic CFX3 55IM freezer. The light items are at the front: the desk across the road-side front corner with the Truma Saphir air-conditioner under it and the seat behind it, and on the kerb side the kitchen slide-out under the awning with the wardrobe over it. The kitchen has a Dometic CVI1525 induction hob and a CVS1350G sink. The entry door is in the kerb-side wall just behind the kitchen (PLACEHOLDER), which keeps the VSB1 rule of one door on the left side. Floor space is kept clear at the entry door, at the ladder foot, in front of the bathroom door (on the bathroom's kerb-side face), at the seat, and in a walkway between them. The cabinetry and seat allowance (70 kg) is placed at the seat.

The garage and bed module is 2,330 mm long inside, from partition A to the rear wall, with the bikes standing along the trailer. Its top-hinged rear door is in the rear wall, 1,910 x 1,440 mm. There is no LPG, so the kerb-side rear corner is stowage, not a gas locker. The 380 mm of rear wall beside the door stays. The Honda EU22i generator and the jerry cans of petrol and diesel are strapped against the kerb-side wall in front of the corner. The loading winch is a WARN VRX 25-S. The other gear (40 kg) is stowed in the garage round the bikes.

Under the floor, the two water tanks stay between the rails in the two suspension bays, one each side of the XT centre crossmember. Each tank is a custom welded HDPE tank with 6 mm walls and baffles, 760 x 1,086 x 259 mm, about 195 L net, so 390 L for the 400 L the owner wants (report 13 section 5). Each sits on two aluminium angle bearers on the XT crossmembers and is strapped down, never hung from the floor. The tanks sit over the axles, so the towball barely changes as the water is used. Two Victron Lithium NG 25.6 V 200 Ah batteries (10.24 kWh) lie on their sides in a sealed aluminium box between the rails under the back of the garage floor, its centre 400 mm in front of the rear wall's inner face, vented outside on the road side. The heater's 15 L diesel tank sits between the rails in the braced bay ahead of the XT front hinge crossmember, above the plan bracing (FIT-03 checks it). Both positions are PLACEHOLDERS until the Cruisemaster kit drawing shows the real space round the airbag and shock mounts.

On the roof lid are four Sunman eArc 430 W glass-free panels, 2,054 x 1,084 x 2 mm each, bonded in a 4,108 x 2,168 mm array with no hatches under it. The awning runs along the kerb side at the roof line. It may stand at most 100 mm proud of the body, because VSB1 counts it in the 2,500 mm width limit.

## Running gear, coupling and drawbar

The running gear is report 06's package with XT Air in place of the coil: a Cruisemaster XT Freestyle Air tandem, the 4,500 kg build, with standard arms, Firestone style 26 airbags, 12 inch ABS-enabled electric drums and Bosch TSC. The air kit's weight is not published, so the layout carries the coil kit's 180 kg (retailer figure) as an estimate, plus 10 kg for the air supply and 3 kg for a spare bag. The hubs sit 215 mm below the rail underside at ride height (Cruisemaster gives 205 to 230 mm for air), so the rail underside is at Z 571.

The wheels, tyres and hubs are the trailer's own (report 09):

- Hubs: Cruisemaster's LC6 pattern, 6 x 139.7 with 1/2 inch UNF x 41 mm knurled studs and a 93 mm spigot, on the 12 inch ABS-enabled A/T electric drum. It is one of Cruisemaster's standard patterns on 12 inch drums. Six-stud 6 x 139.7 is the pattern of most Australian utes and 4WDs, so a wheel can be found in a remote town.
- Wheel: ROH Trak 2 16x7 +7 steel, 6 x 139.7, part 4116776, rated 1,250 kg in ROH's published table, 13.5 kg (estimate). A steel rim bent on a rock can usually be hammered back far enough to get home.
- Tyre: Yokohama Geolandar A/T G015 LT245/70R16 118/115R, load range E, rated 1,320 kg at 80 psi, 19.3 kg (maker's figure). It is the tallest LT size that keeps the 830 mm axle spacing, with 78 mm between the tyres.
- Offset and track: ET +7 with C/F 195 mm gives an effective C/F (C/F less ET) of 188 mm. Cruisemaster's C/F chart allows at most 200 mm for the 4,500 kg XT Air tandem. With the rails kept at 1,286 mm outer width, the track is 1,662 mm, and each tyre's inner sidewall sits 62 mm outside its rail.
- Spare: a sixth wheel and tyre on the front wall, 32.8 kg, on two carrier posts from the body front crossmember (CHASSIS.md). The car carries its own 20-inch spare (report 10), so there are two spares.

The tyre has a maker's weight, so the four running tyres carry no growth allowance. Only the wheels' estimated 13.5 kg each does.

Cruisemaster answered the supplier questions on 18 Nov: its ratings do not include VSB1's 120 % rule, but it will design to the rule, and the owner may do the physical installation of the Bosch TSC. Lead time is 6 to 8 weeks after a design session. With standard hubs the 5 x 130 drilling, the custom studs and the measuring of a Porsche wheel fall away.

At the 3,500 kg ATM with 221 kg on the ball, the 120 % rule needs 3,935 kg on the axle group, 1,968 kg per axle. The 4,500 kg XT Air build is rated 4,050 kg (2,025 kg per axle), 115 kg over what the rule needs. The figure is set by the plated ATM, so lighter mass estimates do not change it.

What air changes, from report 06 section 2: the bags keep the bounce near 1.9 Hz at every load and the ride height the same as the load changes. Venting the bags at camp drops the floor about 60 mm for loading the bikes, which takes the ramp from 16.6 to 15.5 degrees. Do it only when parked. A loss of 3 to 4 psi a week is normal, the compressor filter wants checking every 3 months or 5,000 km, and the valves a rebuild every 2 years. A punctured bag cannot be repaired, so a spare bag travels with the trailer (RG-05). The air supply (RG-04) sits in the living area against partition A, on the heater, where it stays dry and out of the garage. The system wants its supply above 12.0 V, which the 12 kWh battery covers.

The coupling is a Cruisemaster DO35 V3Plus with its coupling point at 440 mm, plus or minus 20 mm, at the car's Normal level (report 08). That height is set for the car's 20-inch tyres. The drawbar members run under the main rails, so the coupling end starts 150 mm below the rail underside. The DO35 hangs under a flat plate at the members' underside, and with its coupling point taken as 130 mm below that plate (assumption) it sits at Z 440 with no cranked drawbar. CHASSIS.md designs the drawbar.

The drawbar stays 1,820 mm from the ball to the body front. Revision B set that length so the drawbar box cleared the car at a 90 degree jack-knife. With no box, the spare wheel on the front wall now sets the clearance: it stands 540 mm clear of the Cayenne's side, and the body's front corners 850 mm (JK-01). Two things limit the jack-knife sooner, as before. In plan, the car's rear corner passes over the drawbar members from 75 degrees and over the stone guard from 49 degrees, and whether they touch depends on the bumper height against the drawbar. Cruisemaster quotes the DO35 at "at least 70 degrees" in yaw.

## Axle position

The axle group centre is at X 5,004, solved so that the towball load is 221 kg fully loaded. That target is the highest towball load that keeps the car's rear axle within 1,600 kg with the planned 340 kg of gear in the car, capped at the 280 kg towball rating, and it re-solves when the car is weighed (see Measured inputs). The solve moves the axle group and everything tied to it, the tanks, their guards and the XT crossmembers, along X until the target is met. The garage stays at the back, because the rear wall fixes it. The solve never changes a block size or a limit.

Revision G moved the axle forward 17 mm from X 5,021. Most of the 271 kg it took off sits behind the axles: the LPG and its cylinders, the lighter battery, generator and module, and the roof panels over the middle. Ahead of the axles the kitchen lost 29 kg but the jockey wheel gained 11 kg. On balance the towball rose, so the axle moved forward to bring it back to the target. Revision F moved the axle back 7 mm from X 5,013. It replaced the 25 kg BD-10 line at the middle of the body, ahead of the axles, with 8 kg of mud flaps behind the rear wheels, so the towball fell and the axle moved aft to bring it back to the target. The designed chassis (revision E) had moved the axle forward from X 5,036 by 23 mm. It is 73 kg heavier than the block chassis, and on balance the added mass sits ahead of the axles: the 5 mm drawbar members, the outriggers under the living area, two bays of plan bracing ahead of the front tank and the front corner steadies. More weight ahead of the axles raises the towball, so the axle moves forward to bring it back to the target. The spare wheel on the front wall had moved the axle forward from X 5,088 in revision C.

The bikes' combined centre of gravity is now 1,059 mm behind the axle centre. Taking them out removes their weight from behind the axles, so the towball rises: with the bikes out and the water full it would be 306 kg without ballast (TC4, see Ballast). That is why every heavy item moved aft.

VSB1 5.1.1 asks for the front load space to be at least as long as the rear overhang (report 08). Here the axle sits 3,184 mm behind the body front and the overhang behind it is 2,316 mm, so the rule holds.

## Ballast

With the garage at the back, the cases without bikes carry more on the ball than the car allows. So the build carries a ballast line in the three cases without bikes (TC1, TC4 and TC5): the least mass, at the back of the garage (X 6,985, 300 mm in front of the rear wall, for example water containers or sandbags strapped to the rear track row), that keeps the towball at or under 280 kg on base weights. That is 65 kg, set by TC4. It was 59 kg in revision D, 63 kg in revision E and 62 kg in revision F. TC5 needs 59 kg. TC1, the tare case, needs none. The registration tare excludes the ballast.

With the growth allowance the same cases need 170 kg (TC4), 164 kg (TC5) and 57 kg (TC1), which check BAL-01 reports. That is less than revision D's 218 kg, because the designed chassis is calculated (7 % growth allowance) and report 13's products are mostly maker figures (0 %). The towball with growth is still over 280 kg in those cases with the 65 kg aboard, and MAS-03 fails there. Carrying less water with the bikes out, or less gear at the front, cuts it.

## Load cases

Masses are in kg and CoG positions in mm. The loading kit (chocks, straps, ramp, winch) and the spare wheel stay aboard in every case. The growth columns add the MASS-06 allowance from report 02 (estimate +20 %, calculated +7 %, spec 0 %, ballast 0 %). Margins are to the 3,500 kg ATM and the kit's 4,050 kg GTM.

| Case | What is aboard | Mass | CoG X | CoG Z | Towball | Towball % | Axle group | ATM margin | GTM margin | With growth | Towball with growth |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC1 | Tare as built, ballast 65 kg | 2,428 | 4,505 | 1,183 | 242 | 10.0 | 2,186 | +1,072 | +1,864 | 2,719 | 277 |
| TC2 | Fully loaded: bikes, 200 L of water (the other 200 L in the car), fuel and gear | 3,132 | 4,652 | 1,206 | 221 | 7.0 | 2,912 | +368 | +1,138 | 3,459 | 261 |
| TC3 | Highway: as TC2 with 50 L of water | 2,982 | 4,635 | 1,234 | 220 | 7.4 | 2,762 | +518 | +1,288 | 3,309 | 260 |
| TC4 | Bikes out, water full, ballast 65 kg | 3,007 | 4,538 | 1,140 | 280 | 9.3 | 2,727 | +493 | +1,323 | 3,332 | 321 |
| TC5 | Bikes out, tanks empty, ballast 65 kg | 2,607 | 4,471 | 1,209 | 278 | 10.6 | 2,330 | +893 | +1,720 | 2,932 | 319 |
| TC6 | Tuareg only, water full | 3,157 | 4,597 | 1,166 | 257 | 8.1 | 2,901 | +343 | +1,149 | 3,484 | 297 |
| TC7 | Street Triple only, water full | 3,117 | 4,569 | 1,157 | 271 | 8.7 | 2,846 | +383 | +1,204 | 3,442 | 312 |

On base weights the towball stays between 220 and 280 kg in every case, inside the band from 6 % of the trailer's mass (188 kg fully loaded) to 280 kg from report 07. With growth it runs from 260 to 321 kg. Carrying one bike puts 257 or 271 kg on the ball, because the other bike's weight behind the axles is missing.

Fully loaded, the trailer's tanks carry 200 L of the owner's 400 L. The other 200 L rides in a tank in the car and tops up the trailer's tanks at camp, which keep their full capacity. That brings the fully loaded case to 3,132 kg, 368 kg under the 3,500 kg ATM on base weights. Every other case is under the ATM too, the heaviest being the Tuareg alone with 400 L at 3,157 kg (3,484 kg with growth), so they keep their water. The tanks hold 390 L net, so 400 L is a planning figure 10 L over what they hold (report 13 open question 17). Every case that carries fuel carries the heater's 15 L of diesel, 12.6 kg. The tanks sit just ahead of the axle centre, so the move barely changes the towball.

The car's rear axle, by report 07's load budget method: the car's DIN kerb mass of 2,085 kg with 54 % on the front axle (assumption), two adults of 160 kg 1.15 m behind the front axle, the rear seats out (50 kg), a 30 kg towbar, the car's own 30 kg spare flat on the boot floor 100 mm behind the rear axle (report 10), and the 221 kg towball 1.1 m behind the rear axle. That puts 1,365 kg on the rear axle before any gear, against its 1,600 kg limit, and 1,111 kg on the front. The car can then carry 340 kg of gear on the floor where the rear seats were before the rear axle binds (the GVM would bind at 364 kg). That is report 07's 385 kg less the 45 kg the spare costs. The 340 kg includes the car's water tank, about 215 kg: 200 L of water, about 12 kg of tank and 3 kg of pump and hose (estimates). It stands on the floor where the rear seats were, which leaves about 125 kg for other gear. It must be restrained properly, bolted to the rear-seat anchors or strapped to the boot tie-downs, and sized to report 03's load cases: 0.8 g forward, 0.5 g rearward and sideways, times 2 off road, so about 3.4 kN forward (estimate). With the ball 1.06 to 1.23 m behind the axle the rear axle carries 1,362 to 1,376 kg. With 280 kg on the ball (the bikes-out cases) the car can carry about 120 kg less gear, because each extra kilogram on the ball adds about 1.4 kg to the rear axle and each kilogram of gear adds about 0.7 kg. Weighbridge figures replace all of these assumptions.

The car itself stays on its 20-inch RS Spyder 9.5J x 20 ET47 wheels with Michelin Pilot Sport 4 SUV 275/45 R20 110Y XL tyres, legal in NSW, where it is registered (report 10). An 18-inch dirt set (Porsche 8J x 18 ET53 with BFGoodrich KO3 LT255/55R18 109/105S) is documented in report 10 as the alternative for a Victorian registration only. It is not part of the plan.

## Mass

The tare is 2,363 kg without the ballast: chassis and drawbar 555, coupling and drawbar fittings 46, running gear 328, spare wheel 33, body 633, roof 31, under the floor 146, garage stowage 21 (the generator), living area 382 and the module 188. Report 13's products set the living area, the roof, the tanks, the battery, the generator and the winch. Each line lists its parts with their basis: a maker's or retailer's figure carries no growth allowance, an estimate 20 %. The chassis and drawbar lines are CHASSIS.md's designed members, plates, galvanising and bought parts, including the four corner steadies. The body's BD-10 line is the two mud flaps behind the rear wheels, 4 kg each (estimate: a 600 x 450 x 6 mm rubber flap at 1,500 kg/m3 is 2.4 kg, plus about 1.6 kg for its hanger bracket and bolts), until the body research names a product.

With report 13's products every case is under the ATM with the growth allowance as well as on base weights. Fully loaded with 200 L in the trailer's tanks it weighs 3,132 kg, 368 kg under the 3,500 kg ATM before any allowance, and 3,459 kg with it. The heaviest case with growth is the Tuareg alone with 400 L, 3,484 kg, 16 kg under (MAS-01 and MAS-08). The fully loaded axle group carries 3,198 kg with growth, 302 kg under the NSW examiner's 3,500 kg GTM cap (MAS-07). MAS-02 checks 1.2 times that load, 3,837 kg, 213 kg under the kit's 4,050 kg GTM. Each tyre and wheel then has to carry 959 kg under the 120 % rule, which the 1,320 kg tyre and the 1,250 kg wheel both cover. The towball with growth still fails MAS-03 with the bikes out (321 kg), so no body length passes every mass check.

The water is the largest single variable, at 1 kg per litre. The growth allowance fully loaded is 327 kg, against 458 kg in revision F. The allowance shrinks as estimates become maker figures and weighed parts (0 %). These five lines carry the largest allowances. The towball change is for the line coming out 20 % heavier, fully loaded.

| Line | Mass | Growth allowance | CoG X | Towball change at +20 % |
|---|---|---|---|---|
| RG-01 XT Air kit (4 arms with bags, hubs and brakes), the air kit's weight not published | 180 | 36 | 4,854 | +1 kg |
| BD-01 floor panel, 8.0 kg/m2 from the older model | 106 | 21 | 4,570 | +2 kg |
| BD-03 side walls, 5.0 kg/m2 from the older model | 99 | 20 | 4,570 | +2 kg |
| BD-02 roof panel, 5.56 kg/m2 from the older model | 73 | 15 | 4,570 | +1 kg |
| LA-11 cabinetry and seat | 70 | 14 | 2,505 | +7 kg |

The bikes' centres of gravity are also estimates (report 05, low confidence). A 100 mm error in the bikes' combined CoG along X moves the towball by about 8 kg.

OPEN, the mass. These are the levers, with their size. The first is taken for the fully loaded case, the rest are not.

- Carry less water when the bikes are aboard. Each 100 L is 100 kg off the trailer and barely changes the towball, because the tanks sit over the axles. Taken for TC2: 200 L rides in the car.
- Weigh or source maker figures for the large estimated lines. Every kilogram moved from estimate to weighed removes 0.2 kg of allowance.
- Lighter choices among the estimates, for example the 70 kg of cabinetry and seat. Report 13 took this lever for the appliances and equipment.
- Lighter wheels and tyres (report 09): the ROH Vapour 16x8 +30 alloy, rated 1,250 kg, saves about 15 kg over five wheels, and LT225/75R16 tyres about 10 kg over five.
- Agree the growth allowance with the engineer. MASS-06 calls its percentages a proposal.

## Body length

| Body | Living area | Living area needs | Spare | Axle from ball | Bikes behind the axle | Tare | Fully loaded | With growth | Ballast (with growth) |
|---|---|---|---|---|---|---|---|---|---|
| 5,000 | 2,580 | 3,050 | -470 | 4,702 | 861 | 2,287 | 3,057 | 3,374 | 39 (144) |
| 5,500 (recommended) | 3,080 | 3,050 | +30 | 5,004 | 1,059 | 2,363 | 3,132 | 3,459 | 65 (170) |
| 6,000 | 3,580 | 3,050 | +530 | 5,334 | 1,228 | 2,424 | 3,194 | 3,529 | 82 (189) |

The garage is the same in each body, so only the living area changes. It needs 3,050 mm for every item and keep-clear space. Only the 5,500 and 6,000 mm bodies hold it. The 5,000 mm body is 470 mm short, and nothing is dropped to make it fit. Leaving the chest freezer out saves 360 mm, which still leaves it 110 mm short.

What each length does to the towball: the solve puts 221 kg on the ball fully loaded in every body. A longer body puts the garage further behind the axles (861, 1,059 and 1,228 mm), so the cases with fewer bikes rise more: one bike gives 252 to 265 kg in the 5,000 mm body, 257 to 271 kg in the 5,500 mm body and 260 to 275 kg in the 6,000 mm body, and the ballast for the cases without bikes grows from 39 to 65 to 82 kg. The 6,000 mm body also adds 61 kg of tare. With 200 L in the trailer every body meets the ATM fully loaded on base weights. With growth the 6,000 mm body's heaviest case is 29 kg over it.

## Chassis inputs

The chassis and drawbar are designed in CHASSIS.md from research report 11, with drawings CT-101 to CT-103 and the Chassis page on the site. In short: two RHS 150 x 50 x 3 C450L0 rails from X 1,820 to 7,320, each with a continuous RHS 100 x 50 x 3 raiser so the two act as one 250 mm deep section, crossmembers at nine stations (full rail height at the body ends and the three XT stations, raiser height elsewhere), an RHS 100 x 50 x 3 outrigger each side at every station, three bays of plan bracing, and an RHS 150 x 50 x 5 A-frame drawbar that runs on 1,000 mm under the rails. The whole frame is hot-dip galvanised. A 3D frame analysis covers report 11's load cases on every trailer case at the ATM, and every stress, deflection, twist, fitting and clearance check passes.

| Input | Value |
|---|---|
| Rail outer width at the XT hinges | 1,286 mm. With C/F 195 (input SUP-04) and ET +7 it gives a 1,662 mm track. Cruisemaster's minimum is 1,150 mm |
| Rail underside, rail top, raiser top, floor underside | Z 571, 721, 821 and 842 (a 21 mm bearer strip on the raiser) |
| Axle group centre | X 5,004. Hubs at X 4,589 and 5,419. XT front hinge crossmember rear face X 4,170, rear shock crossmember front face X 5,780 |
| Coupling | DO35 V3Plus under-mounted, coupling point at Z 440 |
| Overall length | 7,380 mm, coupling head to body rear |
| Overall width | 2,500 mm with the awning |
| Travel height | 2,714 mm, roof down |
| CoG for the roll and track check | Fully loaded X 4,652, Z 1,206 (1,219 with growth), 850 mm above the hub centres. Every case is in the load case table |

The floor over the axles is supported at every station by the outriggers at the XT centre and rear shock crossmembers, which the tyre clears by 88.6 mm through its full travel. So the floor spans 557 mm from the raiser to the body edge between supports at most 830 mm apart. The chocks take the bikes' braking push, about 330 kgf for the Tuareg (RES-01).

## Tuareg panniers

The owner leaves his Mosko Moto panniers on the Tuareg in the garage, and he measured the bike at about 970 to 980 mm wide with them. The model gives each pannier a 457 x 203 x 508 mm envelope from Mosko Moto's Backcountry 30L figures, with the outer faces 490 mm from the centreline. Their position along the bike and their height are estimates, the top level with the tail rack. They are part of the Tuareg's envelope, so the module checks CLR-03, CLR-04, CLR-06 and CLR-09 cover them. CLR-08 measures them against the straps and track fittings: the nearest is the Street Triple's right-side rear strap, 56 mm from the Tuareg's left pannier. As the Tuareg rolls out, its road-side pannier clears the rear door's jamb by 35 mm (CLR-09). The panniers' 9 kg (estimate) is carried in the trailer's mass whenever the Tuareg is.

## Checks

The whole-trailer checks are in `data/checks.yaml` under `trailer_checks`. The towball limits are design targets from report 07, not legal limits: 280 kg is the car's and the towbar's rating, used as a ceiling, and 6 % is the floor report 07 sets for stability. VSB1 sets no towball share.

| ID | Check | Result |
|---|---|---|
| MAS-01 | Mass with growth within the 3,500 kg ATM | PASS, 3,484 kg Tuareg only (3,459 kg fully loaded) |
| MAS-02 | Axle group with growth, times 1.2 because Cruisemaster's ratings do not include the 120 % rule, within the kit's 4,050 kg GTM | PASS, 3,837 kg fully loaded |
| MAS-03 | Towball never above 280 kg, with and without growth | FAIL with growth, 321 kg bikes out with water full (280 kg on base weights) |
| MAS-04 | Towball at least 6 % in every case | PASS, 7.0 % fully loaded |
| MAS-05 | Towball within 10 kg of the 221 kg target fully loaded | PASS, 221 kg |
| MAS-06 | Tyre load with VSB1's 120 % rule within the tyre's 1,320 kg | PASS, 959 kg with growth fully loaded |
| MAS-07 | Axle group with growth within the NSW GTM cap (3,500 kg) | PASS, 3,198 kg fully loaded |
| MAS-08 | Mass with growth within the NSW ATM cap (3,500 kg) | PASS, 3,484 kg Tuareg only |
| MAS-09 | Wheel rating covers the same per-wheel load with growth | PASS, 959 kg against 1,250 kg |
| BAL-01 | Ballast at the back of the garage to tow with no bikes, with growth (reported) | 170 kg (65 kg on base weights, carried) |
| CAR-01 | Car's rear axle before gear, with its own spare (reported) | 1,365 kg against 1,600 kg |
| CAR-07 | Towball scale against the model (reported) | Not measured yet |
| FIT-01 | Living area holds its items and keeps its landings and walkway clear | PASS |
| FIT-02 | Gas locker holds the two cylinders and the regulator | Not checked: no LPG (owner option) |
| FIT-03 | Tanks, battery and diesel tank fit between the rails and crossmembers | PASS |
| FIT-04 | Kerb-strip stowage holds the generator and the jerry cans | PASS |
| FIT-05 | Tyres swung through their full travel keep 50 mm from every chassis member | PASS, 62.5 mm to the kerb-side rail |
| DIM-01 | Width with the awning within 2,500 mm | PASS, 2,500 mm |
| DIM-02 | Front load space not shorter than the rear overhang | PASS, 3,184 against 2,316 mm |
| DIM-03 | Coupling height inside 350 to 460 mm with its tolerance | PASS, 420 to 460 mm |
| DIM-04 | Running clearance at least 100 mm | PASS, 380 mm at the coupling head |
| JK-01 | Body corners and the spare wheel at a 90 degree jack-knife | PASS, 540 mm at the spare wheel |
| JK-02 | Drawbar members and stone guard to the car (reported) | In plan from 49 degrees |

The chassis checks (CHS, LOC, DEF, TWS and FAT) are in CHASSIS.md and on the site's Chassis page. Each check row on the site names the measured inputs it uses.

Because MAS-03 fails with growth, `make strict` fails. That is the design's real state, and the limits stay as they are. Report 13's products turned MAS-01, MAS-02, MAS-07 and MAS-08 into passes, and the trailer's own tyre and wheel had turned MAS-06 and MAS-09 into passes.

## Power

The power system is report 13's planning basis (section 2), for the later power design. It runs at 24 V. That halves the current of a 12 V system, saves about 5 kg of main cable, and keeps a Victron charger from the car's 12 V.

- Batteries: two Victron Lithium NG 25.6 V 200 Ah (10.24 kWh), 37 kg each, on their sides in a sealed aluminium box under the back of the garage floor, with a Lynx Smart BMS NG 500 A.
- Inverter-charger: Victron MultiPlus-II 24/5000/120-50, 4,000 W at 25 °C. It runs the hob, the air-conditioner and the washer together.
- Solar: four Sunman eArc 430 W panels (1,720 W) bonded to the lid, in two pairs, each pair to its own SmartSolar MPPT 150/45.
- From the car: one Orion-Tr Smart 12/24-15 isolated charger, about 360 W, on a 6 B&S feed to an Anderson plug at the towbar.
- 12 V bus: one Orion 24/12-70 for the heater, the XT Air compressor, the water pump and the winch.
- Generator: Honda EU22i, 1,800 W rated, the backup for a run of overcast winter days.

The daily load is about 10.4 kWh on a hot day (38 °C, with 5 kWh of evening air-conditioning) and 5.1 kWh on a cold one (13 °C by day, 0 °C at night). The array gives about 9.3 kWh on the hot day, 3.4 kWh on a clear cold day and 1.4 kWh on an overcast one (estimates). The batteries hold about 8.2 kWh between 95 % and 15 % charge, so about 4 hot days, 3 clear winter days or 1.5 overcast winter days pass before the generator has to run. Then it runs about 45 minutes, 70 minutes or 2.5 hours a day.

## Registration

The trailer will be registered in NSW, with Victoria as the fallback. Report 02 sets out the NSW path for a concessional trailer. The owner applies for a TfNSW identity approval with form 5703, four photos of the trailer (each side, front and rear), photos of the vehicle plate and the drawbar, a weighbridge ticket showing the tare and the VIN, and receipts that show where the materials came from. The examiner checks the design against VSB1 and sets the plate figures. The tare on the ticket excludes the ballast. GTM is capped at the lowest of the tyre load capacities, the coupling rating, the safety chain rating and the brake rating. ATM is capped at the lower of the coupling and chain ratings.

With the chosen parts the four tyres carry 5,280 kg (1,320 kg each), the DO35 coupling and the 4177-35 chains are rated 3,500 kg, and the drums 4,500 kg. So the GTM cap is 3,500 kg, set by the coupling and chains, and the ATM cap is 3,500 kg. The ratings are in `data/load_cases.yaml` under `registration`, and MAS-07 and MAS-08 check against the caps. The trailer's tyre placard shows LT245/70R16 118/115R and the cold pressure for the weighed load. No Australian rule sets a speed category for trailer tyres, and the R rating (170 km/h) leaves a wide margin over the 110 km/h towing limit (report 09 section 5).

## Measured inputs

Every value the owner will measure later is an input in `data/measurements.yaml`, which can be edited in GitHub's web editor. Each one has how to measure it, the estimate with its source, an empty measured slot with a date, and the rules that change the plan. The build uses the measured value when there is one. The site's Measurements page lists every input, its status, the value in use, what depends on it and what each rule did.

The rules re-solve the plan where they can. The towball target follows the car's weighbridge figures, the ball position and the planned gear (CAR-06, now 340 kg because the car carries its own spare), and the axle and the ballast re-solve for it. The Tuareg's width at the Street Triple's bar end (TU-01), its peg width (TU-07) and the Street Triple's (ST-01) set the least bike spacing that CLR-03 allows. The garage width is fixed, so a larger spacing moves the Street Triple towards the kerb-side stowage instead of growing the garage, and above 780 mm CLR-10 fails and flags it. The Tuareg's length (TU-02) and the chock nose (CHK-01) set CLR-06. WHL-01 is the trailer wheel's load rating, which MAS-09 checks. SUP-04 is Cruisemaster's C/F: the track follows from it, and its note flags an effective C/F over 200 mm. Cruisemaster's other answers set the kit GTM and whether MAS-02 applies the 120 % rule. Weighbridge figures at each build stage replace the estimates for the parts already built.

The Tuareg measured 585 mm across its side panels at the Street Triple's bar end (owner, 18 Nov), inside the 668 mm threshold, so the spacing stays at 760 mm and CLR-03 measures 71.5 mm. It is 980 mm wide over its panniers.

The bed beams span the 2,330 mm interior width as SHS 50x50x3 (DESIGN.md). BED-01 reports 5.7 mm of sag under 255 kg spread over the bed, at a bending stress of 18 MPa.

## What changed from revisions C to F

Revision G, 20 Nov 2026, builds in report 13's appliances and equipment. Real products replace 14 estimated lines: 737.5 kg of estimates became 453.5 kg, mostly maker figures. Three owner choices are defaults until the owner answers: a washer with no dryer, no LPG, and two batteries. Without LPG the gas cylinders, the regulator, the gas locker and its hatch go, and the kerb-side rear corner of the garage is stowage. The four glass panels on the roof became four bonded Sunman panels, 59 kg lighter, so the travel height fell from 2,762 to 2,714 mm. The jockey wheel (20 kg in place of 9 kg) and the corner steadies (8.8 kg each in place of 5.5 kg) took published masses. The heater gained a 15 L diesel tank under the floor and 12.6 kg of diesel in every case that carries fuel. The heater's box grew to 450 x 525 mm, so the washer's box narrowed to 470 mm to keep the ladder clear. The tare fell from 2,634 to 2,363 kg and the axle moved from X 5,021 to 5,004. Fully loaded the trailer weighs 3,132 kg, 3,459 kg with growth. MAS-01, MAS-02, MAS-07 and MAS-08 now pass. MAS-03 still fails with growth, at 321 kg with the bikes out. The ballast rose from 62 to 65 kg on base weights and fell from 181 to 170 kg with growth.

Revision F, 20 Nov 2026, makes two fixes. The tyre is now Yokohama's published 752 mm diameter everywhere, in place of the calculated 749.4 mm. The hubs rose from Z 355 to Z 356 and the floor from Z 869 to Z 872, so the floor is again 50 mm above the tyre at full bump (it was 48.7 mm against the published diameter). The rails and the raisers rose with the hubs, so the floor bearer strip grew from 20 to 21 mm (50 x 21 mm). The ramp is now 15.5 degrees with the bags vented. BD-10 is now the two mud flaps only, 8 kg (estimate). Its old 25 kg also covered corner legs, which the chassis design already carries as the four corner steadies (CH-B01), so they were counted twice. The tare fell from 2,650 to 2,634 kg, the axle moved from X 5,013 to 5,021, and the ballast fell from 63 to 62 kg on base weights and from 183 to 181 kg with growth. Fully loaded, the trailer is 92 kg under the ATM on base weights. No check changed state.

Revision E replaces the block chassis and drawbar with the designed ones from CHASSIS.md. They weigh 576 kg against the blocks' 503 kg, but their steel is calculated rather than estimated, so they carry less growth allowance. The tare grew from 2,577 to 2,650 kg, the axle moved from X 5,036 to 5,013, and the ballast for the cases without bikes grew from 59 to 63 kg on base weights and fell from 218 to 183 kg with growth. Fully loaded, the trailer is 76 kg under the ATM on base weights. FIT-05 now swings each tyre through its travel against every chassis member.

The trailer stopped sharing the car's Porsche 8J x 18 wheel. It now runs ROH Trak 2 16x7 +7 steel wheels with Yokohama G015 LT245/70R16 tyres on Cruisemaster's standard LC6 hubs, at C/F 195 mm, and carries a full-size spare on the front wall. The floor rose 12 mm to Z 869 and the travel height to 2,759 mm. The track became 1,662 mm on the unchanged 1,286 mm rails. The tare grew from 2,511 to 2,577 kg, the axle moved from X 5,088 to 5,036, and the ballast for the cases without bikes grew from 45 to 59 kg. Fully loaded, 200 L of the water now rides in the car, which brings the trailer 149 kg under the ATM on base weights. The car now carries its own 30 kg spare, so its gear allowance fell from 385 to 340 kg and the towball target stays 221 kg. MAS-06 and MAS-09 pass. Revision C itself moved the garage to the back, removed partition B, the front utility zone and the drawbar box, and moved the battery and every heavy fixed item aft.

## Assumptions to validate later

The plan uses these values now. Each comes from the source named, and each is replaced when the real figure is known.

| Assumption | Value the plan uses | Source |
|---|---|---|
| Hub | Cruisemaster LC6, 6 x 139.7, 1/2 inch UNF x 41 mm studs, 93 mm spigot, is a standard part on the 12 inch ABS-enabled A/T drum, with the tone ring and wheel speed sensor unchanged | Cruisemaster's stud pattern and spigot sheets (report 09 section 1) |
| C/F limit | Cruisemaster's 200 mm limit applies to effective C/F (C/F less ET), so C/F 195 with ET +7 (188 mm) is acceptable | Cruisemaster's C/F sheet as explained by its stockist (report 09) |
| C/F | 195 mm (SUP-04) | Report 09 section 3 |
| Axle spacing | 830 mm with the 752 mm published tyre, 78 mm between the tyres against the 75 mm minimum | Report 06 section 8, report 09 |
| Wheel nuts and studs | 60 degree conical nuts on the 1/2 inch UNF stud, and the 41 mm stud gives full thread engagement through the ROH wheel's mounting disc | Usual practice for Australian steel 4WD wheels (report 09 section 3) |
| Wheel clearance | The ROH Trak 2's centre disc clears the 12 inch backing plate, park brake and ABS flylead, about 30 mm on the radius | Report 09 section 4 |
| Wheel weight | 13.5 kg (RG-06, SP-02) | Estimated from ROH's 14.3 to 14.4 kg for the 16x8 Trak D (report 09 section 6) |
| Wheel centre bore | 93 mm or more, so the wheel goes over the 93 mm spigot | Report 09 section 3 |
| Wheel rating | 1,250 kg (WHL-01), holding at the 80 psi of a load range E tyre | ROH's published table |
| Tyre | 1,320 kg, 19.3 kg, 752 mm diameter | Yokohama Australia's published figures (report 09 section 2) |
| Spare carrier | Two SHS 50 x 50 x 2.5 posts bolted to the body front crossmember and tied to the wall, designed in CHASSIS.md | Report 11 section 6.4 |
| Air kit mass | 180 kg for the four XT Air arms with bags, hubs and brakes | The coil kit's retailer figure (report 06) |
| Kit GTM | 4,050 kg (SUP-01), and the ratings exclude the 120 % rule (SUP-02) | Cruisemaster's published table and its answer of 18 Nov |
| Tank and battery bays | The tanks, the battery box and the diesel tank fit between the rails round the XT airbag and shock mounts as modelled | Report 06 section 8, block sizes |
| The car | 2,085 kg kerb mass, 54 % on the front axle, the ball 1,100 mm behind the rear axle, 340 kg of gear, a 30 kg spare 100 mm behind the rear axle (CAR-01 to CAR-06) | Reports 07 and 10 |
| Car water tank | About 215 kg on the floor where the rear seats were: 200 L of water, about 12 kg of tank, 3 kg of pump and hose. It is part of the 340 kg of gear and leaves about 125 kg for the rest | Owner's plan, masses estimated |
| Car water tank restraint | Bolted to the rear-seat anchors or strapped to the boot tie-downs, sized for report 03's load cases, about 3.4 kN forward on 215 kg | Report 03 load cases, estimate |
| Car tyre placard | The 958 GTS placard lists the 275/45 R20 110 tyre the car runs | Report 10 |
| Coupling height | 440 mm laden at the car's Normal level on the 20-inch tyres (CAR-04) | Report 08 |
| Bumper and ball | The car's rear corner is 980 mm behind its rear axle and the ball 1,060 to 1,230 mm behind it (CAR-05) | Reports 07 and 08 |
| Bike measurements | Peg widths, screen and mirror heights, Tuareg length and pannier position as in `data/measurements.yaml` | Owner's figures and report 05 |
| Growth allowance | Estimate +20 %, calculated +7 %, spec 0 % | Report 02 MASS-06 |
| Arm pivot | 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside (X 4,147 and 4,977, Z 472), ±10 mm. The tyre swings about it through ±60 mm | Scaled from Cruisemaster's drawing 33XT AIR sheet 2 (report 11 section 5.1) |
| Raiser-level outriggers | Outriggers at raiser height at the XT centre and rear shock crossmembers are acceptable to Cruisemaster, whose note asks for full rail height | Report 11 section 5 and open question 2, read as aimed at members that carry suspension loads |
| XT crossmembers | RHS 150 x 50 x 3 suits the 4,500 kg XT Air build, although TB 070's table stops at 4,450 kg | TB 070 (report 11 section 1.3). Fallback 150 x 50 x 4 |
| DO35 coupling offset | The coupling point sits 130 mm below the plate the DO35 is under-mounted on, so it is at Z 440 | Report 11 section 6.4, report 08 open question 4. Measure a DO35 |
| Galvanising bath | A bath takes the frame in one dip: about 7.4 m long, 2.4 m wide across the outriggers and 0.45 m deep | Report 11 open question 5 |
| Floor panel edge | The 30 mm floor panel needs no continuous edge support. It spans 557 mm from the raiser to the body edge between outriggers at most 830 mm apart | Report 11 section 5.3, option A without the edge member |
| Chassis load cases | The engineer accepts report 11's load cases LC1 to LC10, the factor of 2 on twist, the deflection and twist limits, and the planning fatigue method (IIW classes, ±0.5 g frequent case) | Report 11 section 3 |
| Plate strength | Grade 350 plate at fy 350 MPa for every thickness up to 20 mm | AS/NZS 3678 grade 350 (the 20 mm parts are nearer 340 MPa) |
| Chassis bought parts | DO35 9.5 kg, chains and shackles 4.5 kg, breakaway kit 5 kg and the floor bearer strip 1.0 kg/m (estimates, report 11). The ARK XO750 jockey wheel 20 kg and each ARK DDS650 steady 8.8 kg (published figures, report 13 section 6) | Reports 11 and 13 |
| Equipment masses | Report 13's figures per part: maker and retailer figures as spec (0 % growth), the rest estimates (20 %). The NG battery's 37 kg is marked an estimate by Victron but carried as its published figure | Report 13 and `research/13-equipment.yaml` |
| Recirculating shower | The DauerShower 2.0 is imported, with a normal mixer as the bypass and a spare filter and UV-C LED | Report 13 open question 4 |
| Heater and washer | The 450 x 525 x 300 mm heater box at partition A with 450 along X. The washer turned with its 445 mm width along X in a 470 mm box, its back 155 mm off partition A, and the MultiPlus at the top of its board so the open lid clears it. The XT Air supply raised 50 mm on the heater | Report 13 LA-02, LA-03 and open question 5, and the layout's ladder clearance |
| Diesel for the heater | A 15 L tank between the rails in the bay ahead of the XT front hinge crossmember, above the plan bracing, and 12.6 kg of diesel as payload with the fuel | Report 13 open question 6 |
| Fridge and freezer energy | NRX 130C 0.55 kWh a day at 25 °C. CFX3 55IM 0.8 kWh on a hot day and 0.3 kWh on a cold one | Report 13 open questions 7 and 8 |
| Battery in the cold | The battery box lined with 20 mm closed-cell foam and a 30 W pad heater for mornings below 5 °C, about 0.2 kWh | Report 13 open question 9 |
| Grey water | The shower and sinks drain through a hose to a portable container outside, not in the mass schedule, until the owner asks for a fixed tank | Report 13 open question 10 |
| Car feed | One Orion-Tr Smart 12/24-15 on a 6 B&S feed, about 35 A from the car | Report 13 open question 11 |
| Solar on the lid | The lid's top skin is flat GRP, clear of hatches over the 4,108 x 2,168 mm array, and the panels are bonded with Sunman's adhesive | Report 13 open question 12 |
| Kitchen bench height | The bench is about 1,372 mm above the ground (floor 872 + 50 + 450 mm), so a drop-down or folding step goes with the kitchen, settled in the layout | Report 13 open question 13 |
| Slides and winch | Accuride 9301 slides 6 kg a pair with a lock in both positions. WARN VRX 25-S winch 8 kg, from its 10.6 kg shipping weight | Report 13 open questions 14 and 15 |
| Water capacity | The two HDPE tanks hold 390 L net against the 400 L wanted. The cases with full water keep the 400 L planning figure | Report 13 open question 17 |

## Open questions

These are design decisions for the owner.

1. The towball with growth and the bikes out (MAS-03): which of the remaining levers in Mass to use. Every case is under the ATM with growth, the heaviest 16 kg under it, so the margin for the body design is small.
2. The ballast with the bikes out: what it is (water, sand, tools) and where it is strapped, or whether less water and gear make it unnecessary.
3. Steel or alloy trailer wheels, and LT245/70R16 or LT225/75R16 tyres (report 09 open questions 1 and 2).
4. The track: 1,662 mm on the present rails, or wider for roll stability with a wider rail, since the effective C/F cannot pass 200 mm.
5. The entry door position and whether the generator needs its own hatch into the garage's kerb strip.
6. Whether a shorter drawbar is wanted now the box is gone. The spare wheel then sets the jack-knife clearance.
7. Where the car's spare rides when the trailer is coupled: on the car's boot floor, as planned, or in the trailer over its axles, which frees about 45 kg of the car's gear allowance (report 10).
8. A dryer (report 13 open question 1). The default is the Camec 3.5 kg washer with no dryer. Reversing it (`opt_dryer: 1` in `trailer.yaml`) fits the Whirlpool WWPB8502IW washer-dryer: +50 kg of tare and in every case, so the Tuareg-only case is 3,534 kg with growth and MAS-01 and MAS-08 fail by 34 kg. Each dry uses about 3.3 kWh.
9. LPG (report 13 open question 2). The default is no LPG: induction cooking, with heating and hot water on diesel and a butane cartridge stove in the gear as a backup. Reversing it (`lpg: 1` in `garage-bed.yaml`) brings back two 9 kg cylinders, the regulator, the gas locker and its hatch: about +27 kg of tare and +44 kg fully loaded with the gas, so the Tuareg-only case is about 3,537 kg with growth and MAS-01 and MAS-08 fail. It also brings AS/NZS 5601.2, a gas fitter's certificate, a CO alarm and the locker's drain rules back.
10. The battery (report 13 open question 3). The default is two modules, 10.24 kWh, enough unless the air-conditioner runs all night. Reversing it (`opt_batteries: 3`) adds a third module: +37 kg and a 835 mm battery box, so the Tuareg-only case is 3,521 kg with growth and MAS-01 and MAS-08 fail by 21 kg.

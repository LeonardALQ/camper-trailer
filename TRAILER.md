# Whole trailer: block layout (baseline)

Status: concept, revision D, 19 Nov 2026. Revision D gives the trailer its own wheels and tyres (report 09), because Porsche confirmed that none of its 18-inch wheels is rated for the trailer's load, and adds a full-size spare on the body's front wall. The car keeps its own 20-inch wheels and carries its own spare (report 10). Revision C moved the garage and bed module to the back of the body with a rear door (DESIGN.md revision D), so the living space is one room, and moved every heavy item towards the back so the towball stays inside the Cayenne's limits. Revision B put Cruisemaster's XT Air in place of the coil. Each block is an envelope with a mass, not a design. Items marked OPEN need the owner's decision. Positions marked PLACEHOLDER in the data are not designed yet. The data is `data/assemblies/trailer.yaml`, the load cases are in `data/load_cases.yaml`, the checks in `data/checks.yaml`, and the arithmetic is in `cad/trailer.py`. Drawing CT-001 is the general arrangement. Sources are research reports 02 and 06 to 10, and the owner's older block model for the item list and most masses.

## Datum

Every position here is in the project datum from report 02 (DIM-01). X runs along the trailer from the coupling ball centre, positive rearward. Y runs across from the centreline, positive to the kerb (left) side. Z is up from the ground with the trailer level at design ride height. Units are mm and kg.

The garage and bed module keeps its own frame, and its axes are the datum's. Module X 0, the rear face of partition A, sits at X 4,955 in the 5,500 mm body, and the garage floor (module Z 0) at Z 869. The module ends at the rear wall's inner face, X 7,285.

OPEN: DIM-01 as written is a left-handed frame. With X rearward and Z up, a right-handed frame has Y positive to the right. CAD programs are right-handed, so the 3D model is the mirror image of the real trailer, and in the 3D viewer the gas locker appears on the right when you look from behind. Numbers, masses, clearances and checks are not affected, because a mirror changes none of them. Drawing CT-001 mirrors the model before projecting, so its views show the trailer as it will be seen. The module sheets CT-401 to CT-501 show the model as it is. The fix is to change DIM-01 to Y positive to the road side, or to keep it and mirror every view. Either way it is a decision for the owner and the engineer before any sheet goes FOR CONSTRUCTION.

## Body

The body is 2,400 mm wide with 35 mm walls, so the inside is 2,330 mm. The interior height is 1,800 mm from the floor with the roof down, as in DESIGN.md. The pop-top roof is designed later, and a 45 kg allowance carries its lift mechanism and skirt.

The recommended body length is 5,500 mm. It is the shortest of the three compared that holds the living area, and the 5,000 mm body is 470 mm short (see Body length). The floor is flat for the whole length, level with the garage floor, because the ladder lands on the living-area floor at that level.

The floor height follows from the running gear. The tyre is 749.4 mm across (LT245/70R16, calculated; Yokohama publishes 752 mm) and its static loaded radius is taken as 20 mm less than its free radius (estimate), which puts the hubs at Z 355. At full bump the XT rises 60 mm, so the tyre top reaches Z 789. With 50 mm clearance (estimate) the floor underside is at Z 839, and a 30 mm floor panel puts the floor surface at Z 869, 12 mm higher than with the shared 18-inch wheel. The 3,048 mm ramp then sits at 16.6 degrees, or 15.4 degrees with the air bags vented. Travel height to the top of the solar panels is 2,759 mm, roof down.

## Zones, front to back

The drawbar carries the coupling, the stone guard and the jockey wheel. There is no drawbar box: its generator, gas and fuel moved into the garage in revision C. The trailer's full-size spare wheel stands on the body's front wall above the drawbar, centred across the trailer, on a 6 kg bracket (revision D). There it keeps the rear door and the bike ramp clear.

The living area runs from the front wall to partition A, 3,080 mm inside. The heavy items stand as close to partition A as the plan allows. The wet bathroom (1 x 1 m, recirculating shower) fills the road-side corner against partition A. Beside it against partition A stand the washer-dryer, then the diesel heater and hot water unit with the XT Air supply and the spare airbag on top of it, and the ladder on the kerb side, which hooks on the deck edge. The inverter and chargers hang on partition A above the washer-dryer and the heater, out of the garage and above its 500 mm ignition-free zone. In front of the bathroom on the road side stand the fridge and then the chest freezer. The light items are at the front: the desk across the road-side front corner with the air-conditioner under it and the seat behind it, and on the kerb side the kitchen slide-out under the awning with the wardrobe over it. The entry door is in the kerb-side wall just behind the kitchen (PLACEHOLDER), which keeps the VSB1 rule of one door on the left side. Floor space is kept clear at the entry door, at the ladder foot, in front of the bathroom door (on the bathroom's kerb-side face), at the seat, and in a walkway between them. The cabinetry and seat allowance (70 kg) is placed at the seat.

The garage and bed module is 2,330 mm long inside, from partition A to the rear wall, with the bikes standing along the trailer. Its top-hinged rear door is in the rear wall, 1,910 x 1,440 mm. In its kerb-side rear corner a sealed gas locker holds the two 9 kg cylinders and the regulator, reached only through a hatch in the kerb-side wall. The generator and the jerry cans of petrol and diesel are strapped against the kerb-side wall in front of the locker. The other gear (40 kg) is stowed in the garage round the bikes.

Under the floor, the two water tanks stay between the rails in the two suspension bays, one each side of the XT centre crossmember. Each block is 760 x 1,086 x 260 mm, which gives 429 L gross for the 400 L the owner wants. The taller tyre raised the floor and the rails together, so the bays grew 6 mm. The tanks sit over the axles, so the towball barely changes as the water is used. The 12 kWh battery sits between the rails under the back of the garage floor, its centre 400 mm in front of the rear wall's inner face, in a sealed box vented outside on the road side. Both positions are PLACEHOLDERS until the Cruisemaster kit drawing shows the real space round the airbag and shock mounts.

On the roof are four 400 W panels in two rows. The awning runs along the kerb side at the roof line. It may stand at most 100 mm proud of the body, because VSB1 counts it in the 2,500 mm width limit.

## Running gear, coupling and drawbar

The running gear is report 06's package with XT Air in place of the coil: a Cruisemaster XT Freestyle Air tandem, the 4,500 kg build, with standard arms, Firestone style 26 airbags, 12 inch ABS-enabled electric drums and Bosch TSC. The air kit's weight is not published, so the layout carries the coil kit's 180 kg (retailer figure) as an estimate, plus 10 kg for the air supply and 3 kg for a spare bag. The hubs sit 215 mm below the rail underside at ride height (Cruisemaster gives 205 to 230 mm for air), so the rail underside is at Z 570.

The wheels, tyres and hubs are the trailer's own (report 09):

- Hubs: Cruisemaster's LC6 pattern, 6 x 139.7 with 1/2 inch UNF x 41 mm knurled studs and a 93 mm spigot, on the 12 inch ABS-enabled A/T electric drum. It is one of Cruisemaster's standard patterns on 12 inch drums. Six-stud 6 x 139.7 is the pattern of most Australian utes and 4WDs, so a wheel can be found in a remote town.
- Wheel: ROH Trak 2 16x7 +7 steel, 6 x 139.7, part 4116776, rated 1,250 kg in ROH's published table, 13.5 kg (estimate). A steel rim bent on a rock can usually be hammered back far enough to get home.
- Tyre: Yokohama Geolandar A/T G015 LT245/70R16 118/115R, load range E, rated 1,320 kg at 80 psi, 19.3 kg (maker's figure). It is the tallest LT size that keeps the 830 mm axle spacing, with 80 mm between the tyres.
- Offset and track: ET +7 with C/F 195 mm gives an effective C/F (C/F less ET) of 188 mm. Cruisemaster's C/F chart allows at most 200 mm for the 4,500 kg XT Air tandem. With the rails kept at 1,286 mm outer width, the track is 1,662 mm, and each tyre's inner sidewall sits 62 mm outside its rail.
- Spare: a sixth wheel and tyre on the front wall, 32.8 kg plus a 6 kg bracket. The car carries its own 20-inch spare (report 10), so there are two spares.

The tyre has a maker's weight, so the four running tyres carry no growth allowance. Only the wheels' estimated 13.5 kg each does.

Cruisemaster answered the supplier questions on 18 Nov: its ratings do not include VSB1's 120 % rule, but it will design to the rule, and the owner may do the physical installation of the Bosch TSC. Lead time is 6 to 8 weeks after a design session. With standard hubs the 5 x 130 drilling, the custom studs and the measuring of a Porsche wheel fall away.

At the 3,500 kg ATM with 221 kg on the ball, the 120 % rule needs 3,935 kg on the axle group, 1,968 kg per axle. The 4,500 kg XT Air build is rated 4,050 kg (2,025 kg per axle), 115 kg over what the rule needs. The figure is set by the plated ATM, so lighter mass estimates do not change it.

What air changes, from report 06 section 2: the bags keep the bounce near 1.9 Hz at every load and the ride height the same as the load changes. Venting the bags at camp drops the floor about 60 mm for loading the bikes, which takes the ramp from 16.6 to 15.4 degrees. Do it only when parked. A loss of 3 to 4 psi a week is normal, the compressor filter wants checking every 3 months or 5,000 km, and the valves a rebuild every 2 years. A punctured bag cannot be repaired, so a spare bag travels with the trailer (RG-05). The air supply (RG-04) sits in the living area against partition A, on the heater, where it stays dry and out of the garage. The system wants its supply above 12.0 V, which the 12 kWh battery covers.

The coupling is a Cruisemaster DO35 V3Plus with its coupling point at 440 mm, plus or minus 20 mm, at the car's Normal level (report 08). That height is set for the car's 20-inch tyres. The drawbar members run under the main rails, so the coupling end starts 150 mm below the rail underside. The coupling point is 130 mm below the rail underside, so no cranked drawbar is needed.

The drawbar stays 1,820 mm from the ball to the body front. Revision B set that length so the drawbar box cleared the car at a 90 degree jack-knife. With no box, the spare wheel on the front wall now sets the clearance: it stands 540 mm clear of the Cayenne's side, and the body's front corners 850 mm (JK-01). Two things limit the jack-knife sooner, as before. In plan, the car's rear corner passes over the drawbar members from 75 degrees and over the stone guard from 49 degrees, and whether they touch depends on the bumper height against the drawbar. Cruisemaster quotes the DO35 at "at least 70 degrees" in yaw.

## Axle position

The axle group centre is at X 5,034, solved so that the towball load is 221 kg fully loaded. That target is the highest towball load that keeps the car's rear axle within 1,600 kg with the planned 340 kg of gear in the car, capped at the 280 kg towball rating, and it re-solves when the car is weighed (see Measured inputs). The solve moves the axle group and everything tied to it, the tanks, their guards and the suspension crossmembers, along X until the target is met. The garage stays at the back, because the rear wall fixes it. The solve never changes a block size or a limit.

The spare wheel on the front wall moved the axle 54 mm forward, from X 5,088 in revision C. Its 38.8 kg sits about 3.4 m ahead of the axles, and at the old axle it would have added about 26 kg to the ball.

The bikes' combined centre of gravity is now 1,029 mm behind the axle centre. Taking them out removes their weight from behind the axles, so the towball rises: with the bikes out and the water full it would be 302 kg without ballast (TC4, see Ballast). That is why every heavy item moved aft.

VSB1 5.1.1 asks for the front load space to be at least as long as the rear overhang (report 08). Here the axle sits 3,214 mm behind the body front and the overhang behind it is 2,286 mm, so the rule holds.

## Ballast

With the garage at the back, the cases without bikes carry more on the ball than the car allows. Without ballast TC4 (water full) would put 302 kg on the ball and TC5 (tanks empty) 300 kg, both on base weights. So the build carries a ballast line in the three cases without bikes (TC1, TC4 and TC5): the least mass, at the back of the garage (X 6,985, 300 mm in front of the rear wall, for example water containers or sandbags strapped to the rear track row), that keeps the towball at or under 280 kg on base weights. That is 56 kg, set by TC4, up from 45 kg in revision C because of the spare wheel. TC1, the tare case, needs none. The registration tare excludes the ballast.

With the growth allowance the same cases need 215 kg (TC4), 209 kg (TC5) and 125 kg (TC1), which check BAL-01 reports. The towball with growth is therefore over 280 kg in those cases with the 56 kg aboard, and MAS-03 fails there. Carrying less water with the bikes out, or less gear at the front, cuts it.

## Load cases

Masses are in kg and CoG positions in mm. The loading kit (chocks, straps, ramp, winch) and the spare wheel stay aboard in every case. The growth columns add the MASS-06 allowance from report 02 (estimate +20 %, calculated +7 %, spec 0 %, ballast 0 %). Margins are to the 3,500 kg ATM and the kit's 4,050 kg GTM.

| Case | What is aboard | Mass | CoG X | CoG Z | Towball | Towball % | Axle group | ATM margin | GTM margin | With growth | Towball with growth |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC1 | Tare as built, ballast 56 kg | 2,634 | 4,555 | 1,252 | 250 | 9.5 | 2,383 | +866 | +1,667 | 3,108 | 307 |
| TC2 | Fully loaded: bikes, 400 L of water, gas, fuel and gear | 3,551 | 4,721 | 1,230 | 221 | 6.2 | 3,331 | -51 | +719 | 4,064 | 282 |
| TC3 | Highway: as TC2 with 50 L of water | 3,201 | 4,690 | 1,287 | 219 | 6.8 | 2,983 | +299 | +1,067 | 3,714 | 280 |
| TC4 | Bikes out, water full, ballast 56 kg | 3,218 | 4,596 | 1,200 | 280 | 8.7 | 2,938 | +282 | +1,112 | 3,729 | 342 |
| TC5 | Bikes out, tanks empty, ballast 56 kg | 2,818 | 4,538 | 1,272 | 278 | 9.9 | 2,540 | +682 | +1,510 | 3,329 | 339 |
| TC6 | Tuareg only, water full | 3,376 | 4,655 | 1,221 | 254 | 7.5 | 3,122 | +124 | +928 | 3,889 | 315 |
| TC7 | Street Triple only, water full | 3,336 | 4,629 | 1,214 | 268 | 8.0 | 3,068 | +164 | +982 | 3,848 | 330 |

On base weights the towball stays between 219 and 280 kg in every case, inside the 213 kg (6 % of the loaded trailer) to 280 kg band from report 07. With growth it runs from 280 to 342 kg. Carrying one bike puts 254 or 268 kg on the ball, because the other bike's weight behind the axles is missing.

The fully loaded case is now 51 kg over the 3,500 kg ATM on base weights. The new running gear and the spare added 66 kg to the tare: 27 kg on the four running wheels (LT tyres on steel wheels) and 39 kg for the spare and its bracket. The ATM checks look at the mass with growth (MAS-01 and MAS-08), so the base figure shows in this table rather than as a check of its own. 349 L of water instead of 400 L brings the fully loaded case to the ATM on base weights.

The car's rear axle, by report 07's load budget method: the car's DIN kerb mass of 2,085 kg with 54 % on the front axle (assumption), two adults of 160 kg 1.15 m behind the front axle, the rear seats out (50 kg), a 30 kg towbar, the car's own 30 kg spare flat on the boot floor 100 mm behind the rear axle (report 10), and the 221 kg towball 1.1 m behind the rear axle. That puts 1,365 kg on the rear axle before any gear, against its 1,600 kg limit, and 1,111 kg on the front. The car can then carry 340 kg of gear on the floor where the rear seats were before the rear axle binds (the GVM would bind at 364 kg). That is report 07's 385 kg less the 45 kg the spare costs. With the ball 1.06 to 1.23 m behind the axle the rear axle carries 1,362 to 1,376 kg. With 280 kg on the ball (the bikes-out cases) the car can carry about 120 kg less gear, because each extra kilogram on the ball adds about 1.4 kg to the rear axle and each kilogram of gear adds about 0.7 kg. Weighbridge figures replace all of these assumptions.

The car itself stays on its 20-inch RS Spyder 9.5J x 20 ET47 wheels with Michelin Pilot Sport 4 SUV 275/45 R20 110Y XL tyres, legal in NSW, where it is registered (report 10). An 18-inch dirt set (Porsche 8J x 18 ET53 with BFGoodrich KO3 LT255/55R18 109/105S) is documented in report 10 as the alternative for a Victorian registration only. It is not part of the plan.

## Mass

The tare is 2,577 kg without the ballast: drawbar and coupling 117, chassis 381, running gear 328, spare wheel 39, body 654, roof 90, under the floor 170, garage stowage 59 (generator, empty cylinders, regulator), living area 547 and the module 193.

The trailer fails its mass checks with the growth allowance, and on base weights it is now over the ATM fully loaded. Fully loaded with 400 L of water it weighs 3,551 kg, 51 kg over the 3,500 kg ATM before any allowance. With the allowance it weighs 4,064 kg, 564 kg over. The axle group then carries 3,783 kg, which is 283 kg over the NSW examiner's 3,500 kg GTM cap. MAS-02 checks 1.2 times that load, 4,539 kg, which is 489 kg over the kit's 4,050 kg GTM. Each tyre and wheel then has to carry 1,135 kg under the 120 % rule, which the 1,320 kg tyre and the 1,250 kg wheel both cover. No body length passes.

The water is the largest single variable, at 1 kg per litre. With growth it cannot be met by water alone, because the allowance (513 kg) is larger than the water. The allowance shrinks as estimates become maker figures and weighed parts (0 %). These five lines carry the largest allowances. The towball change is for the line coming out 20 % heavier, fully loaded.

| Line | Mass | Growth allowance | CoG X | Towball change at +20 % |
|---|---|---|---|---|
| RG-01 XT Air kit (4 arms with bags, hubs and brakes), the air kit's weight not published | 180 | 36 | 4,884 | +1 kg |
| CH-01 main rails (2), section not sized yet | 128 | 26 | 4,570 | +2 kg |
| UF-04 lithium battery, 12 kWh | 110 | 22 | 6,885 | -8 kg |
| BD-01 floor panel, 8.0 kg/m2 from the older model | 106 | 21 | 4,570 | +2 kg |
| LA-01 wet bathroom, 1 x 1 m | 100 | 20 | 4,435 | +2 kg |

The bikes' centres of gravity are also estimates (report 05, low confidence). A 100 mm error in the bikes' combined CoG along X moves the towball by about 8 kg.

OPEN, the mass. These are the levers, with their size. None is taken here.

- Carry less water when the bikes are aboard. Each 100 L is 100 kg off the trailer and barely changes the towball, because the tanks sit over the axles. 349 L meets the ATM on base weights.
- Weigh or source maker figures for the large estimated lines. Every kilogram moved from estimate to weighed removes 0.2 kg of allowance.
- Lighter choices among the estimates, for example the 40 kg generator, the 65 kg washer-dryer and the 60 kg inverter and chargers.
- Lighter wheels and tyres (report 09): the ROH Vapour 16x8 +30 alloy, rated 1,250 kg, saves about 15 kg over five wheels, and LT225/75R16 tyres about 10 kg over five.
- Agree the growth allowance with the engineer. MASS-06 calls its percentages a proposal.

## Body length

| Body | Living area | Living area needs | Spare | Axle from ball | Bikes behind the axle | Tare | Fully loaded | With growth | Ballast (with growth) |
|---|---|---|---|---|---|---|---|---|---|
| 5,000 | 2,580 | 3,050 | -470 | 4,699 | 864 | 2,519 | 3,493 | 3,994 | 37 (193) |
| 5,500 (recommended) | 3,080 | 3,050 | +30 | 5,034 | 1,029 | 2,577 | 3,551 | 4,064 | 56 (215) |
| 6,000 | 3,580 | 3,050 | +530 | 5,385 | 1,178 | 2,636 | 3,610 | 4,135 | 70 (231) |

The garage is the same in each body, so only the living area changes. It needs 3,050 mm for every item and keep-clear space. Only the 5,500 and 6,000 mm bodies hold it. The 5,000 mm body is 470 mm short, and nothing is dropped to make it fit. Leaving the chest freezer out saves 360 mm, which still leaves it 110 mm short.

What each length does to the towball: the solve puts 221 kg on the ball fully loaded in every body. A longer body puts the garage further behind the axles (864, 1,029 and 1,178 mm), so the cases with fewer bikes rise more: one bike gives 250 to 264 kg in the 5,000 mm body, 254 to 268 kg in the 5,500 mm body and 257 to 271 kg in the 6,000 mm body, and the ballast for the cases without bikes grows from 37 to 56 to 70 kg. The 6,000 mm body also adds 59 kg of tare. Only the 5,000 mm body meets the ATM fully loaded on base weights, by 7 kg, and it does not hold the living area.

## Chassis inputs

These are the figures the chassis design starts from. Sections are block sizes until the engineer sizes them.

| Input | Value |
|---|---|
| Rail outer width at the XT hinges | 1,286 mm, kept from revision C. With C/F 195 (input SUP-04) and ET +7 it gives a 1,662 mm track. A 2,000 mm track needs 1,624 mm. Cruisemaster's minimum is 1,150 mm |
| Wheels, tyres and hubs | ROH Trak 2 16x7 +7 steel, Yokohama G015 LT245/70R16 118/115R, Cruisemaster LC6 6 x 139.7 hubs with 1/2 inch UNF studs and a 93 mm spigot on 12 inch ABS-enabled drums (report 09) |
| Rails | Two 150 x 50 mm rails (block size, report 08), 5,500 mm long from X 1,820 to 7,320. 1,186 mm inside, centres 1,236 mm apart |
| Rail underside and top | Z 570 and Z 720 |
| Raiser height | 120 mm, rail top to the floor underside at Z 839 |
| Drawbar | 1,820 mm from the ball to the body front. Two members of 1,666 mm from the coupling head to the rails, running on 1,000 mm under the rails (PLACEHOLDER) |
| Coupling | Coupling point at Z 440, 130 mm below the rail underside |
| Axle group centre | X 5,034. Hubs at X 4,619 and 5,449. XT front hinge crossmember rear face X 4,200, centre crossmember X 4,980 to 5,030, rear shock crossmember front face X 5,810 |
| Crossmembers under the garage and the tanks | The three XT crossmembers above (150 x 50 x 3 RHS, full rail height). The front hinge one sits under the living area, the other two under the front of the garage |
| Battery bay | Under the back of the garage, from the crossmember at X 6,525 to the rear crossmember at X 7,270. The battery box is X 6,585 to 7,185 |
| Other crossmembers | X 1,820 (body front), 2,415, 2,985 and 3,555 under the living area, and 7,270 (body rear). The intermediate ones come from a 700 mm pitch rule (PLACEHOLDER) |
| Outriggers | At the crossmember stations X 1,820, 2,415, 2,985, 3,555, 4,150, 6,525 and 7,270, from the rail to the body edge |
| Spare wheel | On the body's front wall, X 1,509 to 1,820, centred on Y, centre Z 1,269, on a bracket through the wall to the chassis |
| Overall length | 7,380 mm, coupling head to body rear |
| Overall width | 2,500 mm with the awning |
| Travel height | 2,759 mm, roof down |
| CoG for the roll and track check | Fully loaded X 4,721, Z 1,230 (1,238 with growth), 875 mm above the hub centres. Every case is in the load case table |

The engineer should know one structural gap. No outrigger can pass over the tyres, because the floor underside is only 50 mm above them at full bump. So outboard of the rails there is no support between X 4,200 and 6,525, which covers the back of the living area and the front 1,570 mm of the garage, under the bikes' front wheels and chocks. There the floor has to span 557 mm from the rail raisers to the side walls, or hang from the walls. The chocks also take the bikes' braking push, about 330 kgf for the Tuareg (RES-01). The outrigger at the XT front hinge crossmember is 44 mm from the front tyre at full bump (FIT-05), the tightest running-gear gap.

## Tuareg panniers

The owner leaves his Mosko Moto panniers on the Tuareg in the garage, and he measured the bike at about 970 to 980 mm wide with them. The model gives each pannier a 457 x 203 x 508 mm envelope from Mosko Moto's Backcountry 30L figures, with the outer faces 490 mm from the centreline. Their position along the bike and their height are estimates, the top level with the tail rack. They are part of the Tuareg's envelope, so the module checks CLR-03, CLR-04, CLR-06 and CLR-09 cover them. CLR-08 measures them against the straps and track fittings: the nearest is the Street Triple's right-side rear strap, 56 mm from the Tuareg's left pannier. As the Tuareg rolls out, its road-side pannier clears the rear door's jamb by 35 mm (CLR-09). The panniers' 9 kg (estimate) is carried in the trailer's mass whenever the Tuareg is.

## Checks

The whole-trailer checks are in `data/checks.yaml` under `trailer_checks`. The towball limits are design targets from report 07, not legal limits: 280 kg is the car's and the towbar's rating, used as a ceiling, and 6 % is the floor report 07 sets for stability. VSB1 sets no towball share.

| ID | Check | Result |
|---|---|---|
| MAS-01 | Mass with growth within the 3,500 kg ATM | FAIL, 4,064 kg fully loaded |
| MAS-02 | Axle group with growth, times 1.2 because Cruisemaster's ratings do not include the 120 % rule, within the kit's 4,050 kg GTM | FAIL, 4,539 kg fully loaded |
| MAS-03 | Towball never above 280 kg, with and without growth | FAIL with growth, 342 kg bikes out with water full (280 kg on base weights) |
| MAS-04 | Towball at least 6 % in every case | PASS, 6.2 % fully loaded |
| MAS-05 | Towball within 10 kg of the 221 kg target fully loaded | PASS, 221 kg |
| MAS-06 | Tyre load with VSB1's 120 % rule within the tyre's 1,320 kg | PASS, 1,135 kg with growth |
| MAS-07 | Axle group with growth within the NSW GTM cap (3,500 kg) | FAIL, 3,783 kg fully loaded |
| MAS-08 | Mass with growth within the NSW ATM cap (3,500 kg) | FAIL, 4,064 kg fully loaded |
| MAS-09 | Wheel rating covers the same per-wheel load with growth | PASS, 1,135 kg against 1,250 kg |
| BAL-01 | Ballast at the back of the garage to tow with no bikes, with growth (reported) | 215 kg (56 kg on base weights, carried) |
| CAR-01 | Car's rear axle before gear, with its own spare (reported) | 1,365 kg against 1,600 kg |
| CAR-07 | Towball scale against the model (reported) | Not measured yet |
| FIT-01 | Living area holds its items and keeps its landings and walkway clear | PASS |
| FIT-02 | Gas locker holds the two cylinders and the regulator | PASS |
| FIT-03 | Tanks and battery fit between the rails and crossmembers | PASS |
| FIT-04 | Kerb-strip stowage holds the generator and the jerry cans | PASS |
| FIT-05 | Tyres at full bump clear the chassis and body | PASS, 44 mm to the XT front hinge outrigger |
| DIM-01 | Width with the awning within 2,500 mm | PASS, 2,500 mm |
| DIM-02 | Front load space not shorter than the rear overhang | PASS, 3,214 against 2,286 mm |
| DIM-03 | Coupling height inside 350 to 460 mm with its tolerance | PASS, 420 to 460 mm |
| DIM-04 | Running clearance at least 100 mm | PASS, 380 mm at the coupling head |
| JK-01 | Body corners and the spare wheel at a 90 degree jack-knife | PASS, 540 mm at the spare wheel |
| JK-02 | Drawbar members and stone guard to the car (reported) | In plan from 49 degrees |

Each check row on the site names the measured inputs it uses.

Because MAS-01, MAS-02, MAS-03, MAS-07 and MAS-08 fail with growth, `make strict` fails. That is the design's real state, and the limits stay as they are. The trailer's own tyre and wheel turned MAS-06 and MAS-09 into passes.

## Registration

The trailer will be registered in NSW, with Victoria as the fallback. Report 02 sets out the NSW path for a concessional trailer. The owner applies for a TfNSW identity approval with form 5703, four photos of the trailer (each side, front and rear), photos of the vehicle plate and the drawbar, a weighbridge ticket showing the tare and the VIN, and receipts that show where the materials came from. The examiner checks the design against VSB1 and sets the plate figures. The tare on the ticket excludes the ballast. GTM is capped at the lowest of the tyre load capacities, the coupling rating, the safety chain rating and the brake rating. ATM is capped at the lower of the coupling and chain ratings.

With the chosen parts the four tyres carry 5,280 kg (1,320 kg each), the DO35 coupling and the 4177-35 chains are rated 3,500 kg, and the drums 4,500 kg. So the GTM cap is 3,500 kg, set by the coupling and chains, and the ATM cap is 3,500 kg. The ratings are in `data/load_cases.yaml` under `registration`, and MAS-07 and MAS-08 check against the caps. The trailer's tyre placard shows LT245/70R16 118/115R and the cold pressure for the weighed load. No Australian rule sets a speed category for trailer tyres, and the R rating (170 km/h) leaves a wide margin over the 110 km/h towing limit (report 09 section 5).

## Measured inputs

Every value the owner will measure later is an input in `data/measurements.yaml`, which can be edited in GitHub's web editor. Each one has how to measure it, the estimate with its source, an empty measured slot with a date, and the rules that change the plan. The build uses the measured value when there is one. The site's Measurements page lists every input, its status, the value in use, what depends on it and what each rule did.

The rules re-solve the plan where they can. The towball target follows the car's weighbridge figures, the ball position and the planned gear (CAR-06, now 340 kg because the car carries its own spare), and the axle and the ballast re-solve for it. The Tuareg's width at the Street Triple's bar end (TU-01), its peg width (TU-07) and the Street Triple's (ST-01) set the least bike spacing that CLR-03 allows. The garage width is fixed, so a larger spacing moves the Street Triple towards the kerb-side stowage instead of growing the garage, and above 780 mm CLR-10 fails and flags it. The Tuareg's length (TU-02) and the chock nose (CHK-01) set CLR-06. WHL-01 is the trailer wheel's load rating, which MAS-09 checks. SUP-04 is Cruisemaster's C/F: the track follows from it, and its note flags an effective C/F over 200 mm. Cruisemaster's other answers set the kit GTM and whether MAS-02 applies the 120 % rule. Weighbridge figures at each build stage replace the estimates for the parts already built.

The Tuareg measured 585 mm across its side panels at the Street Triple's bar end (owner, 18 Nov), inside the 668 mm threshold, so the spacing stays at 760 mm and CLR-03 measures 71.5 mm. It is 980 mm wide over its panniers.

The bed beams span the 2,330 mm interior width as SHS 50x50x3 (DESIGN.md). BED-01 reports 5.7 mm of sag under 255 kg spread over the bed, at a bending stress of 18 MPa.

## What changed from revision C

The trailer stopped sharing the car's Porsche 8J x 18 wheel. It now runs ROH Trak 2 16x7 +7 steel wheels with Yokohama G015 LT245/70R16 tyres on Cruisemaster's standard LC6 hubs, at C/F 195 mm, and carries a full-size spare on the front wall. The floor rose 12 mm to Z 869 and the travel height to 2,759 mm. The track became 1,662 mm on the unchanged 1,286 mm rails. The tare grew from 2,511 to 2,577 kg, the axle moved from X 5,088 to 5,034, and the ballast for the cases without bikes grew from 45 to 56 kg. The car now carries its own 30 kg spare, so its gear allowance fell from 385 to 340 kg and the towball target stays 221 kg. MAS-06 and MAS-09 pass. Revision C itself moved the garage to the back, removed partition B, the front utility zone and the drawbar box, and moved the battery and every heavy fixed item aft.

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
| Tyre | 1,320 kg, 19.3 kg, 749.4 mm diameter | Yokohama Australia and its size table (report 09 section 2) |
| Spare bracket | 6 kg, bolted through the front wall to the chassis | Report 09 section 7 range of 4 to 8 kg |
| Air kit mass | 180 kg for the four XT Air arms with bags, hubs and brakes | The coil kit's retailer figure (report 06) |
| Kit GTM | 4,050 kg (SUP-01), and the ratings exclude the 120 % rule (SUP-02) | Cruisemaster's published table and its answer of 18 Nov |
| Tank and battery bays | The tanks and the battery fit between the rails round the XT airbag and shock mounts as modelled | Report 06 section 8, block sizes |
| The car | 2,085 kg kerb mass, 54 % on the front axle, the ball 1,100 mm behind the rear axle, 340 kg of gear, a 30 kg spare 100 mm behind the rear axle (CAR-01 to CAR-06) | Reports 07 and 10 |
| Car tyre placard | The 958 GTS placard lists the 275/45 R20 110 tyre the car runs | Report 10 |
| Coupling height | 440 mm laden at the car's Normal level on the 20-inch tyres (CAR-04) | Report 08 |
| Bumper and ball | The car's rear corner is 980 mm behind its rear axle and the ball 1,060 to 1,230 mm behind it (CAR-05) | Reports 07 and 08 |
| Bike measurements | Peg widths, screen and mirror heights, Tuareg length and pannier position as in `data/measurements.yaml` | Owner's figures and report 05 |
| Growth allowance | Estimate +20 %, calculated +7 %, spec 0 % | Report 02 MASS-06 |

## Open questions

These are design decisions for the owner.

1. DIM-01's handedness (see Datum).
2. The mass: which of the levers in Mass to use, now that the fully loaded trailer is 51 kg over the ATM on base weights.
3. The ballast with the bikes out: what it is (water, sand, tools) and where it is strapped, or whether less water and gear make it unnecessary.
4. Steel or alloy trailer wheels, and LT245/70R16 or LT225/75R16 tyres (report 09 open questions 1 and 2).
5. The track: 1,662 mm on the present rails, or wider for roll stability with a wider rail, since the effective C/F cannot pass 200 mm.
6. The entry door position and whether the generator needs its own hatch into the garage's kerb strip.
7. Whether a shorter drawbar is wanted now the box is gone. The spare wheel then sets the jack-knife clearance.
8. Where the car's spare rides when the trailer is coupled: on the car's boot floor, as planned, or in the trailer over its axles, which frees about 45 kg of the car's gear allowance (report 10).

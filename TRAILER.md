# Whole trailer: block layout (baseline)

Status: concept, revision C, 19 Nov 2026. Revision C moves the garage and bed module to the back of the body with a rear door (DESIGN.md revision D), so the living space is one room, and moves every heavy item towards the back so the towball stays inside the Cayenne's limits. Revision B put Cruisemaster's XT Air in place of the coil. Each block is an envelope with a mass, not a design. Items marked OPEN need the owner's decision. Positions marked PLACEHOLDER in the data are not designed yet. The data is `data/assemblies/trailer.yaml`, the load cases are in `data/load_cases.yaml`, the checks in `data/checks.yaml`, and the arithmetic is in `cad/trailer.py`. Drawing CT-001 is the general arrangement. Sources are research reports 02 and 06 to 08, and the owner's older block model for the item list and most masses.

## Datum

Every position here is in the project datum from report 02 (DIM-01). X runs along the trailer from the coupling ball centre, positive rearward. Y runs across from the centreline, positive to the kerb (left) side. Z is up from the ground with the trailer level at design ride height. Units are mm and kg.

The garage and bed module keeps its own frame, and its axes are the datum's. Module X 0, the rear face of partition A, sits at X 4,955 in the 5,500 mm body, and the garage floor (module Z 0) at Z 858. The module ends at the rear wall's inner face, X 7,285.

OPEN: DIM-01 as written is a left-handed frame. With X rearward and Z up, a right-handed frame has Y positive to the right. CAD programs are right-handed, so the 3D model is the mirror image of the real trailer, and in the 3D viewer the gas locker appears on the right when you look from behind. Numbers, masses, clearances and checks are not affected, because a mirror changes none of them. Drawing CT-001 mirrors the model before projecting, so its views show the trailer as it will be seen. The module sheets CT-401 to CT-501 show the model as it is. The fix is to change DIM-01 to Y positive to the road side, or to keep it and mirror every view. Either way it is a decision for the owner and the engineer before any sheet goes FOR CONSTRUCTION.

## Body

The body is 2,400 mm wide with 35 mm walls, so the inside is 2,330 mm. The interior height is 1,800 mm from the floor with the roof down, as in DESIGN.md. The pop-top roof is designed later, and a 45 kg allowance carries its lift mechanism and skirt.

The recommended body length is 5,500 mm. It is the shortest of the three compared that holds the living area, and the 5,000 mm body is 470 mm short (see Body length). The floor is flat for the whole length, level with the garage floor, because the ladder lands on the living-area floor at that level.

The floor height follows from the running gear. The tyre is 737.7 mm across (255/55 R18, calculated) and its static loaded radius is taken as 20 mm less than its free radius (estimate), which puts the hubs at Z 349. At full bump the XT rises 60 mm, so the tyre top reaches Z 778. With 50 mm clearance (estimate) the floor underside is at Z 828, and a 30 mm floor panel puts the floor surface at Z 858. Travel height to the top of the solar panels is 2,748 mm, roof down.

## Zones, front to back

The drawbar carries the coupling, the stone guard and the jockey wheel. There is no drawbar box in revision C: its generator, gas and fuel moved into the garage.

The living area runs from the front wall to partition A, 3,080 mm inside. The heavy items stand as close to partition A as the plan allows. The wet bathroom (1 x 1 m, recirculating shower) fills the road-side corner against partition A. Beside it against partition A stand the washer-dryer, then the diesel heater and hot water unit with the XT Air supply and the spare airbag on top of it, and the ladder on the kerb side, which hooks on the deck edge. The inverter and chargers hang on partition A above the washer-dryer and the heater, out of the garage and above its 500 mm ignition-free zone. In front of the bathroom on the road side stand the fridge and then the chest freezer. The light items are at the front: the desk across the road-side front corner with the air-conditioner under it and the seat behind it, and on the kerb side the kitchen slide-out under the awning with the wardrobe over it. The entry door is in the kerb-side wall just behind the kitchen (PLACEHOLDER), which keeps the VSB1 rule of one door on the left side. Floor space is kept clear at the entry door, at the ladder foot, in front of the bathroom door (on the bathroom's kerb-side face), at the seat, and in a walkway between them. The cabinetry and seat allowance (70 kg) is placed at the seat.

The garage and bed module is 2,330 mm long inside, from partition A to the rear wall, with the bikes standing along the trailer. Its top-hinged rear door is in the rear wall, 1,910 x 1,440 mm. In its kerb-side rear corner a sealed gas locker holds the two 9 kg cylinders and the regulator, reached only through a hatch in the kerb-side wall. The generator and the jerry cans of petrol and diesel are strapped against the kerb-side wall in front of the locker. The other gear (40 kg) is stowed in the garage round the bikes.

Under the floor, the two water tanks stay between the rails in the two suspension bays, one each side of the XT centre crossmember. Each block is 760 x 1,086 x 254 mm, which gives 419 L gross for the 400 L the owner wants. They sit over the axles, so the towball barely changes as the water is used. The 12 kWh battery moved to the back: it sits between the rails under the garage floor, its centre 400 mm in front of the rear wall's inner face, in a sealed box vented outside on the road side. Both positions are PLACEHOLDERS until the Cruisemaster kit drawing shows the real space round the airbag and shock mounts.

On the roof are four 400 W panels in two rows. The awning runs along the kerb side at the roof line. It may stand at most 100 mm proud of the body, because VSB1 counts it in the 2,500 mm width limit.

## Running gear, coupling and drawbar

The running gear is report 06's package with XT Air in place of the coil: a Cruisemaster XT Freestyle Air tandem, the 4,500 kg build, with standard arms, Firestone style 26 airbags, 12 inch ABS-enabled electric drums and Bosch TSC. The coil kit weighs about 180 kg (retailer figure). The air kit's weight is not published, so the layout carries the same 180 kg as an estimate, plus 10 kg for the air supply and 3 kg for a spare bag. The axles are 830 mm apart, which suits tyres up to 760 mm. The hubs sit 215 mm below the rail underside at ride height (Cruisemaster gives 205 to 230 mm for air), so the rail underside is at Z 564. The Porsche 8J x 18 ET53 wheel stays a parameter because its load rating is not published yet (report 07).

Cruisemaster answered the supplier questions on 18 Nov. It will make the 5 x 130 hubs with custom-machined studs, cut to the thickness of the wheel's mounting pad so the nuts get full thread engagement, and the pattern clears the ABS tone ring and wheel speed sensor. It will check the C/F against the wheel's ET53 offset (input SUP-04). Its ratings do not include VSB1's 120 % rule, but it will design to the rule. The owner may do the physical installation of the Bosch TSC. Lead time is 6 to 8 weeks after a design session in which Cruisemaster measures the wheel, so the wheel has to be chosen and on hand before that session.

At the 3,500 kg ATM with 221 kg on the ball, the 120 % rule needs 3,935 kg on the axle group, 1,968 kg per axle. The 4,500 kg XT Air build is rated 4,050 kg (2,025 kg per axle), 115 kg over what the rule needs. The figure is set by the plated ATM, so lighter mass estimates do not change it.

What air changes, from report 06 section 2: the bags keep the bounce near 1.9 Hz at every load and the ride height the same as the load changes. Venting the bags at camp drops the floor about 60 mm for loading the bikes, which takes the ramp from about 16.4 to 15.2 degrees. Do it only when parked. A loss of 3 to 4 psi a week is normal, the compressor filter wants checking every 3 months or 5,000 km, and the valves a rebuild every 2 years. A punctured bag cannot be repaired, so a spare bag travels with the trailer (RG-05). The air supply (RG-04) now sits in the living area against partition A, on the heater, where it stays dry and out of the garage. The system wants its supply above 12.0 V, which the 12 kWh battery covers.

The coupling is a Cruisemaster DO35 V3Plus with its coupling point at 440 mm, plus or minus 20 mm, at the car's Normal level (report 08). The drawbar members run under the main rails, so the coupling end starts 150 mm below the rail underside. The coupling point is only 124 mm below the rail underside, so no cranked drawbar is needed.

The drawbar stays 1,820 mm from the ball to the body front. Revision B set that length so the drawbar box cleared the car at a 90 degree jack-knife. With no box, the body's front corners now set the clearance, and they stand 850 mm clear of the Cayenne's side. OPEN: a shorter drawbar would save weight and length but moves the ball, so the axle solve and the towball follow. Two things limit the jack-knife sooner, as before. In plan, the car's rear corner passes over the drawbar members from 75 degrees and over the stone guard from 49 degrees, and whether they touch depends on the bumper height against the drawbar, which nobody has measured. Cruisemaster quotes the DO35 at "at least 70 degrees" in yaw.

## Axle position

The axle group centre is at X 5,088, solved so that the towball load is 221 kg fully loaded. That target is the highest towball load that keeps the car's rear axle within 1,600 kg with the planned 385 kg of gear in the car, capped at the 280 kg towball rating, and it re-solves when the car is weighed (see Measured inputs). The solve moves the axle group and everything tied to it, the tanks, their guards and the suspension crossmembers, along X until the target is met. The garage stays at the back, because the rear wall fixes it. The solve never changes a block size or a limit.

The bikes' combined centre of gravity is then 975 mm behind the axle centre. Taking them out removes their weight from behind the axles, so the towball rises: with the bikes out and the water full it would be 297 kg without ballast (TC4, see Ballast). That is why every heavy item moved aft.

VSB1 5.1.1 asks for the front load space to be at least as long as the rear overhang (report 08). Here the axle sits 3,268 mm behind the body front and the overhang behind it is 2,232 mm, so the rule holds.

The study before this revision (a point-mass model that moved the revision B lines) put TC2 at 226 kg with the axle at X 5,122. At the same axle this model gives TC2 about 11 kg more, because the plan here places the kitchen, the freezer, the generator and the jerry cans further forward than the study's fractions, and the washer-dryer and the ramp further back. So this model's solve lands at X 5,088, against the study's 5,110 for 221 kg.

## Ballast

With the garage at the back, the cases without bikes carry more on the ball than the car allows. Without ballast TC4 (water full) would put 297 kg on the ball and TC5 (tanks empty) 295 kg, both on base weights. So the build carries a ballast line in the three cases without bikes (TC1, TC4 and TC5): the least mass, at the back of the garage (X 6,985, 300 mm in front of the rear wall, for example water containers or sandbags strapped to the rear track row), that keeps the towball at or under 280 kg on base weights. That is 45 kg, set by TC4. TC1, the tare case, needs none. The registration tare excludes the ballast.

With the growth allowance the same cases need 214 kg (TC4), 207 kg (TC5) and 114 kg (TC1), which check BAL-01 reports. The towball with growth is therefore over 280 kg in those cases with the 45 kg aboard, and MAS-03 fails there. Carrying less water with the bikes out, or less gear at the front, cuts it.

## Load cases

Masses are in kg and CoG positions in mm. The loading kit (chocks, straps, ramp, winch) stays aboard in every case. The growth columns add the MASS-06 allowance from report 02 (estimate +20 %, calculated +7 %, spec 0 %, ballast 0 %). Margins are to the 3,500 kg ATM and the kit's 4,050 kg GTM.

| Case | What is aboard | Mass | CoG X | CoG Z | Towball | Towball % | Axle group | ATM margin | GTM margin | With growth | Towball with growth |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC1 | Tare as built, ballast 45 kg | 2,556 | 4,593 | 1,252 | 249 | 9.7 | 2,308 | +944 | +1,742 | 3,037 | 306 |
| TC2 | Fully loaded: bikes, 400 L of water, gas, fuel and gear | 3,485 | 4,766 | 1,227 | 221 | 6.3 | 3,265 | +15 | +785 | 4,004 | 283 |
| TC3 | Highway: as TC2 with 50 L of water | 3,135 | 4,734 | 1,286 | 219 | 7.0 | 2,917 | +365 | +1,133 | 3,654 | 281 |
| TC4 | Bikes out, water full, ballast 45 kg | 3,140 | 4,634 | 1,198 | 280 | 8.9 | 2,860 | +360 | +1,190 | 3,658 | 343 |
| TC5 | Bikes out, tanks empty, ballast 45 kg | 2,740 | 4,572 | 1,272 | 278 | 10.1 | 2,463 | +760 | +1,587 | 3,258 | 341 |
| TC6 | Tuareg only, water full | 3,310 | 4,701 | 1,218 | 252 | 7.6 | 3,058 | +190 | +992 | 3,829 | 314 |
| TC7 | Street Triple only, water full | 3,270 | 4,675 | 1,210 | 265 | 8.1 | 3,005 | +230 | +1,045 | 3,788 | 328 |

On base weights the towball stays between 219 and 280 kg in every case, inside the 211 kg (6 % of the loaded trailer) to 280 kg band from report 07. With growth it runs from 281 to 343 kg, so every case is over 280 kg with the allowance. The bikes now move the towball most: carrying one bike puts 252 or 265 kg on the ball, because the other bike's weight behind the axles is missing. The fully loaded case meets the ATM on base weights with 15 kg to spare.

The car's rear axle, by report 07's load budget method: the car's DIN kerb mass of 2,085 kg with 54 % on the front axle (assumption), two adults of 160 kg 1.15 m behind the front axle, the rear seats out (50 kg), a 30 kg towbar and the 221 kg towball 1.1 m behind the rear axle. That puts 1,334 kg on the rear axle before any gear, against its 1,600 kg limit, and 1,112 kg on the front. The car can then carry 385 kg of gear on the floor where the rear seats were before the rear axle binds. With 280 kg on the ball (the bikes-out cases) it can carry about 120 kg less gear, because each extra kilogram on the ball adds about 1.4 kg to the rear axle and each kilogram of gear adds about 0.7 kg. Weighbridge figures replace all of these assumptions.

## Mass

The tare is 2,511 kg without the ballast: drawbar and coupling 117, chassis 381, running gear 301, body 654, roof 90, under the floor 170, garage stowage 59 (generator, empty cylinders, regulator), living area 547 and the module 193.

The trailer still fails its mass checks with the growth allowance. Fully loaded with 400 L of water it weighs 3,485 kg, 15 kg under the 3,500 kg ATM before any allowance. With the allowance it weighs 4,004 kg, 504 kg over. The axle group then carries 3,722 kg, which is 222 kg over the NSW examiner's 3,500 kg GTM cap. MAS-02 checks 1.2 times that load, 4,466 kg, which is 416 kg over the kit's 4,050 kg GTM. Each tyre would need 1,117 kg under the 120 % rule against the tyre's 1,030 kg. No body length passes.

The water is the largest single variable, at 1 kg per litre. With growth it cannot be met by water alone, because the allowance (519 kg) is larger than the water. The allowance shrinks as estimates become maker figures and weighed parts (0 %). These five lines carry the largest allowances. The towball change is for the line coming out 20 % heavier, fully loaded.

| Line | Mass | Growth allowance | CoG X | Towball change at +20 % |
|---|---|---|---|---|
| RG-01 XT Air kit (4 arms with bags, hubs and brakes), the air kit's weight not published | 180 | 36 | 4,938 | +1 kg |
| CH-01 main rails (2), section not sized yet | 128 | 26 | 4,570 | +3 kg |
| UF-04 lithium battery, 12 kWh | 110 | 22 | 6,885 | -8 kg |
| BD-01 floor panel, 8.0 kg/m2 from the older model | 106 | 21 | 4,570 | +2 kg |
| RG-02 wheels and tyres (4), neither weight published | 104 | 21 | 5,088 | 0 kg |

The bikes' centres of gravity are also estimates (report 05, low confidence). A 100 mm error in the bikes' combined CoG along X moves the towball by about 7 kg.

OPEN, the mass. These are the levers, with their size. None is taken here.

- Carry less water when the bikes are aboard. Each 100 L is 100 kg off the trailer and barely changes the towball, because the tanks sit over the axles.
- Weigh or source maker figures for the large estimated lines. Every kilogram moved from estimate to weighed removes 0.2 kg of allowance.
- Lighter choices among the estimates, for example the 40 kg generator, the 65 kg washer-dryer and the 60 kg inverter and chargers.
- Agree the growth allowance with the engineer. MASS-06 calls its percentages a proposal.

## Body length

| Body | Living area | Living area needs | Spare | Axle from ball | Bikes behind the axle | Tare | Fully loaded | With growth | Ballast (with growth) |
|---|---|---|---|---|---|---|---|---|---|
| 5,000 | 2,580 | 3,050 | -470 | 4,749 | 814 | 2,453 | 3,427 | 3,934 | 25 (191) |
| 5,500 (recommended) | 3,080 | 3,050 | +30 | 5,088 | 975 | 2,511 | 3,485 | 4,004 | 45 (214) |
| 6,000 | 3,580 | 3,050 | +530 | 5,443 | 1,119 | 2,570 | 3,544 | 4,075 | 59 (231) |

The garage is the same in each body, so only the living area changes. It needs 3,050 mm for every item and keep-clear space. Only the 5,500 and 6,000 mm bodies hold it. The 5,000 mm body is 470 mm short, and nothing is dropped to make it fit. Leaving the chest freezer out saves 360 mm, which still leaves it 110 mm short.

What each length does to the towball: the solve puts 221 kg on the ball fully loaded in every body. A longer body puts the garage further behind the axles (814, 975 and 1,119 mm), so the cases with fewer bikes rise more: one bike gives 248 to 261 kg in the 5,000 mm body, 252 to 265 kg in the 5,500 mm body and 255 to 268 kg in the 6,000 mm body, and the ballast for the cases without bikes grows from 25 to 45 to 59 kg. The 6,000 mm body also adds 59 kg of tare.

## Chassis inputs

These are the figures the chassis design starts from. Sections are block sizes until the engineer sizes them.

| Input | Value |
|---|---|
| Rail outer width at the XT hinges | 1,286 mm, which gives the Cayenne's 1,660 mm track with C/F 240 (input SUP-04) and ET53. A 2,000 mm track needs 1,626 mm. Cruisemaster's minimum is 1,150 mm |
| Rails | Two 150 x 50 mm rails (block size, report 08), 5,500 mm long from X 1,820 to 7,320. 1,186 mm inside, centres 1,236 mm apart |
| Rail underside and top | Z 564 and Z 714 |
| Raiser height | 114 mm, rail top to the floor underside at Z 828 |
| Drawbar | 1,820 mm from the ball to the body front. Two members of 1,666 mm from the coupling head to the rails, running on 1,000 mm under the rails (PLACEHOLDER) |
| Coupling | Coupling point at Z 440, 124 mm below the rail underside |
| Axle group centre | X 5,088. Hubs at X 4,673 and 5,503. XT front hinge crossmember rear face X 4,254, centre crossmember X 5,034 to 5,084, rear shock crossmember front face X 5,864 |
| Crossmembers under the garage and the tanks | The three XT crossmembers above (150 x 50 x 3 RHS, full rail height). The front hinge one sits under the living area, the other two under the front of the garage |
| Battery bay | Under the back of the garage, from the crossmember at X 6,525 to the rear crossmember at X 7,270. The battery box is X 6,585 to 7,185 |
| Other crossmembers | X 1,820 (body front), 2,429, 3,012 and 3,596 under the living area, and 7,270 (body rear). The intermediate ones come from a 700 mm pitch rule (PLACEHOLDER) |
| Outriggers | At the crossmember stations X 1,820, 2,429, 3,012, 3,596, 4,204, 6,525 and 7,270, from the rail to the body edge |
| Overall length | 7,380 mm, coupling head to body rear |
| Overall width | 2,500 mm with the awning |
| Travel height | 2,748 mm, roof down |
| CoG for the roll and track check | Fully loaded X 4,766, Z 1,227 (1,232 with growth), 878 mm above the hub centres. Every case is in the load case table |

The engineer should know one structural gap. No outrigger can pass over the tyres, because the floor underside is only 50 mm above them at full bump. So outboard of the rails there is no support between X 4,254 and 6,525, which covers the back of the living area and the front 1,570 mm of the garage, under the bikes' front wheels and chocks. There the floor has to span 557 mm from the rail raisers to the side walls, or hang from the walls. The chocks also take the bikes' braking push, about 330 kgf for the Tuareg (RES-01).

## Tuareg panniers

The owner leaves his Mosko Moto panniers on the Tuareg in the garage, and he measured the bike at about 970 to 980 mm wide with them. The model gives each pannier a 457 x 203 x 508 mm envelope from Mosko Moto's Backcountry 30L figures, with the outer faces 490 mm from the centreline. Their position along the bike and their height are estimates, the top level with the tail rack. They are part of the Tuareg's envelope, so the module checks CLR-03, CLR-04, CLR-06 and CLR-09 cover them. CLR-08 measures them against the straps and track fittings: the nearest is the Street Triple's right-side rear strap, 56 mm from the Tuareg's left pannier. As the Tuareg rolls out, its road-side pannier clears the rear door's jamb by 35 mm (CLR-09). The panniers' 9 kg (estimate) is carried in the trailer's mass whenever the Tuareg is.

## Checks

The whole-trailer checks are in `data/checks.yaml` under `trailer_checks`. The towball limits are design targets from report 07, not legal limits: 280 kg is the car's and the towbar's rating, used as a ceiling, and 6 % is the floor report 07 sets for stability. VSB1 sets no towball share.

| ID | Check | Result |
|---|---|---|
| MAS-01 | Mass with growth within the 3,500 kg ATM | FAIL, 4,004 kg fully loaded |
| MAS-02 | Axle group with growth, times 1.2 because Cruisemaster's ratings do not include the 120 % rule, within the kit's 4,050 kg GTM | FAIL, 4,466 kg fully loaded |
| MAS-03 | Towball never above 280 kg, with and without growth | FAIL with growth, 343 kg bikes out with water full (280 kg on base weights) |
| MAS-04 | Towball at least 6 % in every case | PASS, 6.3 % fully loaded |
| MAS-05 | Towball within 10 kg of the 221 kg target fully loaded | PASS, 221 kg |
| MAS-06 | Tyre load with VSB1's 120 % rule within 1,030 kg | FAIL, 1,117 kg with growth |
| MAS-07 | Axle group with growth within the NSW GTM cap (3,500 kg) | FAIL, 3,722 kg fully loaded |
| MAS-08 | Mass with growth within the NSW ATM cap (3,500 kg) | FAIL, 4,004 kg fully loaded |
| MAS-09 | Wheel rating meets the 120 % rule (reported) | 984 kg needed, Porsche's rating not known |
| BAL-01 | Ballast at the back of the garage to tow with no bikes, with growth (reported) | 214 kg (45 kg on base weights, carried) |
| CAR-01 | Car's rear axle before gear (reported) | 1,334 kg against 1,600 kg |
| CAR-07 | Towball scale against the model (reported) | Not measured yet |
| FIT-01 | Living area holds its items and keeps its landings and walkway clear | PASS |
| FIT-02 | Gas locker holds the two cylinders and the regulator | PASS |
| FIT-03 | Tanks and battery fit between the rails and crossmembers | PASS |
| FIT-04 | Kerb-strip stowage holds the generator and the jerry cans | PASS |
| FIT-05 | Tyres at full bump clear the chassis and body | PASS, 50 mm to the floor |
| DIM-01 | Width with the awning within 2,500 mm | PASS, 2,500 mm |
| DIM-02 | Front load space not shorter than the rear overhang | PASS, 3,268 against 2,232 mm |
| DIM-03 | Coupling height inside 350 to 460 mm with its tolerance | PASS, 420 to 460 mm |
| DIM-04 | Running clearance at least 100 mm | PASS, 380 mm at the coupling head |
| JK-01 | Body corners at a 90 degree jack-knife | PASS, 850 mm |
| JK-02 | Drawbar members and stone guard to the car (reported) | In plan from 49 degrees |

Each check row on the site names the measured inputs it uses.

Because MAS-01, MAS-02, MAS-03, MAS-06, MAS-07 and MAS-08 fail with growth, `make strict` fails. That is the design's real state, and the limits stay as they are.

## Registration

The trailer will be registered in NSW, with Victoria as the fallback. Report 02 sets out the NSW path for a concessional trailer. The owner applies for a TfNSW identity approval with form 5703, four photos of the trailer (each side, front and rear), photos of the vehicle plate and the drawbar, a weighbridge ticket showing the tare and the VIN, and receipts that show where the materials came from. The examiner checks the design against VSB1 and sets the plate figures. The tare on the ticket excludes the ballast. GTM is capped at the lowest of the tyre load capacities, the coupling rating, the safety chain rating and the brake rating. ATM is capped at the lower of the coupling and chain ratings.

With the chosen parts the four tyres carry 4,120 kg (1,030 kg each), the DO35 coupling and the 4177-35 chains are rated 3,500 kg, and the drums 4,500 kg. So the GTM cap is 3,500 kg, set by the coupling and chains, and the ATM cap is 3,500 kg. The ratings are in `data/load_cases.yaml` under `registration`, and MAS-07 and MAS-08 check against the caps.

## Measured inputs

Every value the owner will measure later is an input in `data/measurements.yaml`, which can be edited in GitHub's web editor. Each one has how to measure it, the estimate with its source, an empty measured slot with a date, and the rules that change the plan. The build uses the measured value when there is one. The site's Measurements page lists every input, its status, the value in use, what depends on it and what each rule did.

The rules re-solve the plan where they can. The towball target follows the car's weighbridge figures, the ball position and the planned gear, and the axle and the ballast re-solve for it. The Tuareg's width at the Street Triple's bar end (TU-01), its peg width (TU-07) and the Street Triple's (ST-01) set the least bike spacing that CLR-03 allows. The garage width is fixed in revision D, so a larger spacing moves the Street Triple towards the kerb-side stowage instead of growing the garage, and above 780 mm CLR-10 fails and flags it. The Tuareg's length (TU-02) and the chock nose (CHK-01) set CLR-06. Porsche's wheel rating decides between the Porsche wheel and a rated 5 x 130 aftermarket wheel. Cruisemaster's answers set the kit GTM and whether MAS-02 applies the 120 % rule. Weighbridge figures at each build stage replace the estimates for the parts already built.

The Tuareg measured 585 mm across its side panels at the Street Triple's bar end (owner, 18 Nov), inside the 668 mm threshold, so the spacing stays at 760 mm and CLR-03 measures 71.5 mm. It is 980 mm wide over its panniers.

The bed beams now span the 2,330 mm interior width, so they changed from RHS 50x25x2.5 to SHS 50x50x3 (DESIGN.md). BED-01 reports 5.7 mm of sag under 255 kg spread over the bed, at a bending stress of 18 MPa.

## What changed from revision B

The garage moved from over the axles to the back of the body, with a rear door in place of the kerb-side door. Partition B and the front utility zone went, so the living area is one room of 3,080 mm. The drawbar box went, and its generator, gas and fuel moved into the garage, the gas into a sealed locker. The utility zone's door went and a gas locker hatch arrived. The battery moved from behind the rear shock crossmember to under the back of the garage. The washer-dryer, freezer, heater, inverter and air supply moved from the front zone to the living area against partition A, and the fridge and bathroom moved forward with the living area. The loading kit stays aboard in every case, and the cases without bikes carry ballast. The axle moved from X 4,707 to X 5,088. The tare fell from 2,543 to 2,511 kg, mostly because the drawbar box (25 kg), the utility door (20 kg) and partition B went.

## Open questions

1. DIM-01's handedness (see Datum).
2. The mass: which of the levers in Mass to use, and the growth allowance to agree with the engineer.
3. The ballast with the bikes out: what it is (water, sand, tools) and where it is strapped, or whether less water and gear make it unnecessary.
4. The track: matched to the car (1,660 mm) or wider for roll stability (report 06). The rail width follows from it.
5. The entry door position and whether the generator needs its own hatch into the garage's kerb strip.
6. The real space between the rails round the XT airbags and shocks, from Cruisemaster's XT Air kit drawing, for the tanks and the battery.
7. The car's rear bumper height and corner shape, and the ball position, for the jack-knife, and whether a shorter drawbar is wanted now the box is gone.
8. A spare wheel. The trailer shares the Cayenne's wheel, so one spare could serve both. None is in the mass, and its position is not decided.
9. The Porsche 8J x 18 wheel's load rating (reports 06 and 07). Each wheel needs about 984 kg under the 120 % rule at the ATM. It comes before the Cruisemaster design session, because Cruisemaster measures the chosen wheel there.
10. Cruisemaster's design session: its rating for the XT Air build (SUP-01, 4,050 kg in its published table), the C/F for the ET53 wheel (SUP-04), the stud length from the wheel's mounting pad, and which air controls to fit.

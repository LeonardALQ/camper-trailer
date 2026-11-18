# Whole trailer: block layout (baseline)

Status: concept, revision B, 18 Nov 2026. Revision B puts Cruisemaster's XT Air in place of the coil (see Running gear). This is the first layout of the whole trailer. It places the garage and bed module from DESIGN.md over the axles and puts every other zone and system around it as blocks with masses, so that the axle position, the towball load and the chassis inputs can be worked out. Each block is an envelope, not a design. Items marked OPEN need the owner's decision. Positions marked PLACEHOLDER in the data are not designed yet. The data is `data/assemblies/trailer.yaml`, the load cases are in `data/load_cases.yaml`, the checks in `data/checks.yaml`, and the arithmetic is in `cad/trailer.py`. Drawing CT-001 is the general arrangement. Sources are research reports 02 and 06 to 08, and the owner's older block model for the item list and most masses.

## Datum

Every position here is in the project datum from report 02 (DIM-01). X runs along the trailer from the coupling ball centre, positive rearward. Y runs across from the centreline, positive to the kerb (left) side. Z is up from the ground with the trailer level at design ride height. Units are mm and kg.

The garage and bed module keeps its own frame, and its axes point the same way as the datum. Partition A faces the front of the trailer and partition B faces the living zone at the rear, so X does not change sign. Module X 0, the inner face of partition A, sits at X 3,765, and the garage floor (module Z 0) sits at Z 858.

OPEN: DIM-01 as written is a left-handed frame. With X rearward and Z up, a right-handed frame has Y positive to the right. CAD programs are right-handed, so the 3D model is the mirror image of the real trailer, and in the 3D viewer the garage door appears on the right when you look from behind. Numbers, masses, clearances and checks are not affected, because a mirror changes none of them. Drawing CT-001 mirrors the model before projecting, so its views show the trailer as it will be seen. The module sheets CT-401 to CT-501 were drawn before partition A was known to face the front, and their kerb-side views now show the mirror image too. The fix is to change DIM-01 to Y positive to the road side, or to keep it and mirror every view. Either way it is a decision for the owner and the engineer before any sheet goes FOR CONSTRUCTION.

## Body

The body is 2,400 mm wide with 35 mm walls, so the inside is 2,330 mm. The interior height is 1,800 mm from the garage floor with the roof down, as in DESIGN.md. The pop-top roof is designed later, and a 45 kg allowance carries its lift mechanism and skirt.

The recommended body length is 5,500 mm. It is the shortest of the three compared that holds every zone, and the 5,000 mm body is 310 mm short (see Body length). The floor is flat for the whole length, level with the garage floor, because the ladder in DESIGN.md lands on the living-area floor at that level.

The floor height follows from the running gear. The tyre is 737.7 mm across (255/55 R18, calculated) and its static loaded radius is taken as 20 mm less than its free radius (estimate), which puts the hubs at Z 349. At full bump the XT rises 60 mm, so the tyre top reaches Z 778. With 50 mm clearance (estimate) the floor underside is at Z 828, and a 30 mm floor panel puts the garage floor surface at Z 858. That is inside the 800 to 1,000 mm range DESIGN.md allowed. Travel height to the top of the solar panels is 2,748 mm, roof down.

## Zones, front to back

The drawbar box sits on the A-frame, 50 mm ahead of the body. It is 700 x 1,500 x 550 mm and holds the generator, two 9 kg gas bottles and the jerry cans of petrol and diesel.

The front utility zone is 1,890 mm long inside, between the front wall and partition A. The kitchen slide-out (1,500 mm) runs along the kerb wall at floor level with the wardrobe above it. The washer-dryer stands in the road-side front corner, with the chest freezer beside it against the front wall. The zone's own door is in the road-side wall, 650 mm behind the front wall, and a walkway runs from it across to the wardrobe. The diesel heater and hot water unit stand against partition A on the centreline, with the inverter and chargers on the partition above them. The XT Air supply and the spare airbag sit low in the road-side corner against partition A, clear of the door landing. The door side and position come from the older block model (PLACEHOLDER).

The garage and bed module is 1,840 mm long over its partitions, exactly as DESIGN.md sets it, with the bikes over the axles.

The rear living zone is 1,700 mm long inside, from partition B to the rear wall. The fridge stands against partition B on the road side. The 1 x 1 m wet bathroom with its recirculating shower fills the road-side rear corner. The desk runs across the kerb-side rear corner with the under-bench air-conditioner beneath it. The entry door is in the kerb wall just behind the ladder's foot (PLACEHOLDER), which keeps the VSB1 rule of one door on the left side. Floor space is kept clear in front of the partition B doorway, at the ladder's foot, inside the entry door, in front of the bathroom door and at the desk. Cabinetry and a seat (70 kg) are spread over the zone until the furniture is designed.

Under the floor, two water tanks sit between the rails in the two suspension bays, one each side of the XT centre crossmember. Each block is 760 x 1,086 x 254 mm, which gives 419 L gross for the 400 L the owner wants. They sit over the axles, so the towball barely changes as the water is used. The 12 kWh battery sits in its own bay between the rails, just behind the rear shock crossmember. Both positions are PLACEHOLDERS until the Cruisemaster kit drawing shows the real space around the airbag and shock mounts.

On the roof are four 400 W panels in two rows. The awning runs along the kerb side at the roof line. It may stand at most 100 mm proud of the body, because VSB1 counts it in the 2,500 mm width limit.

## Running gear, coupling and drawbar

The running gear is report 06's package with XT Air in place of the coil: a Cruisemaster XT Freestyle Air tandem, the 4,500 kg build, with standard arms, Firestone style 26 airbags, 12 inch ABS-enabled electric drums and Bosch TSC. The coil kit weighs about 180 kg (retailer figure). The air kit's weight is not published, so the layout carries the same 180 kg as an estimate, plus 10 kg for the air supply and 3 kg for a spare bag. The axles are 830 mm apart, which suits tyres up to 760 mm. The hubs sit 215 mm below the rail underside at ride height (Cruisemaster gives 205 to 230 mm for air), so the rail underside is at Z 564. The Porsche 8J x 18 ET53 wheel stays a parameter because its load rating is not published yet (report 07).

Cruisemaster answered the supplier questions on 18 Nov. It will make the 5 x 130 hubs with custom-machined studs, cut to the thickness of the wheel's mounting pad so the nuts get full thread engagement, and the pattern clears the ABS tone ring and wheel speed sensor. It will check the C/F against the wheel's ET53 offset (input SUP-04). It confirmed the 33SC-950 coil with the 33SC-107 bump stop for these masses. Its ratings do not include VSB1's 120 % rule, but it will design to the rule. The owner may do the physical installation of the Bosch TSC. Lead time is 6 to 8 weeks after a design session in which Cruisemaster measures the wheel, so the wheel has to be chosen and on hand before that session.

The coil answer and the 120 % answer pulled against each other, so the owner chose XT Air (18 Nov). At the 3,500 kg ATM with 221 kg on the ball, the rule needs 3,935 kg on the axle group, 1,968 kg per axle. The 3,700 kg coil build is rated 3,330 kg (1,665 kg per axle), 605 kg short. The 4,500 kg XT Air build is rated 4,050 kg (2,025 kg per axle), 115 kg over what the rule needs. The figure is set by the plated ATM, so lighter mass estimates do not change it.

What air changes, from report 06 section 2:

- Ride. The bags keep the bounce near 1.9 Hz at every load, where the coil gave about 1.8 Hz loaded and 2.1 Hz with the bikes out. The ride height stays the same as the load changes.
- Floor height. It does not change, because the bump stop sits in the same place for coil and air. Venting the bags at camp drops the floor about 60 mm for loading the bikes, which takes the ramp from about 16.3 to 15.2 degrees. Do it only when parked.
- Upkeep. A loss of 3 to 4 psi a week is normal. The compressor filter wants checking every 3 months or 5,000 km, and the valves a rebuild every 2 years. The bags must be washed free of mud and stones.
- Field repair. A punctured bag cannot be repaired, so a spare bag travels with the trailer (RG-05). With a dead bag the trailer can only limp home on the bump stops at very slow speed. A failed compressor is less serious, because the bags can be filled from any tyre compressor through the manual inflation points.
- Air supply. The 12 V compressor, 11 litre tank, gauges, pressure switch and height valves sit low in the front zone against partition A on the road side (RG-04), where they stay dry and out of the garage. The system wants its supply above 12.0 V, which the 12 kWh battery covers.

The coupling is a Cruisemaster DO35 V3Plus with its coupling point at 440 mm, plus or minus 20 mm, at the car's Normal level (report 08). The drawbar members run under the main rails, so the coupling end starts 150 mm below the rail underside. The coupling point is only 124 mm below the rail underside, so no cranked drawbar is needed. The DO35's under-mount offset, measured on a real coupling, decides the packer.

The drawbar is 1,820 mm from the ball to the body front. At a 90 degree jack-knife in plan, the body's front corners then stand 850 mm clear of the Cayenne's side, and the drawbar box 100 mm clear. The box sets the length: its front face has to be outside the car's 970 mm half-width. The 100 mm is this layout's allowance for the unmeasured ball position and the car's rounded corners. Two things limit the jack-knife sooner. In plan, the car's rear corner passes over the drawbar members from 75 degrees and over the stone guard from 49 degrees, depending on how far the ball sits behind the car's axle. Whether they touch depends on the bumper height against the drawbar, which nobody has measured. Cruisemaster also quotes the DO35 at "at least 70 degrees" in yaw, so the coupling may stop the turn before 90 degrees.

## Axle position

The axle group centre is at X 4,707, solved so that the towball load is 221 kg fully loaded. That target is no longer a fixed figure. It is the highest towball load that keeps the car's rear axle within 1,600 kg with the planned 385 kg of gear in the car, capped at the 280 kg towball rating, and it re-solves when the car is weighed (see Measured inputs). The solve moves the axle group and everything tied to it, the module, the tanks, the battery and the suspension crossmembers, along X until the target is met. It never changes a block size or a limit.

With the bikes exactly over the axles the solve wanted the garage 33 mm further back, which would leave the living zone short of its 1,700 mm minimum. So the module is held where the living zone just fits and the axle group moves on its own. The bikes' combined centre of gravity is then 33 mm ahead of the axle centre, and taking both bikes and their kit out changes the towball by 4 kg.

VSB1 5.1.1 asks for the front load space to be at least as long as the rear overhang (report 08). Here the axle sits 2,887 mm behind the body front and the overhang behind it is 2,613 mm, so the rule holds. It decided where the battery goes. With the battery ahead of the axles, the 220 kg target put the axle 15 mm ahead of the middle of the body, which VSB1 does not allow. Behind the axles the same target lands the axle well behind the middle.

## Load cases

Masses are in kg and CoG positions in mm. The growth columns add the MASS-06 allowance from report 02 (estimate +20 %, calculated +7 %, spec 0 %). Margins are to the 3,500 kg ATM and the kit's 4,050 kg GTM.

| Case | What is aboard | Mass | CoG X | CoG Z | Towball | Towball % | Axle group | ATM margin | GTM margin | With growth | Towball with growth |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC1 | Tare as built, removable kit fitted | 2,543 | 4,354 | 1,240 | 191 | 7.5 | 2,352 | +957 | +1,698 | 3,030 | 229 |
| TC2 | Fully loaded: bikes and kit, 400 L of water, gas, fuel and gear | 3,517 | 4,412 | 1,212 | 221 | 6.3 | 3,297 | -17 | +754 | 4,043 | 263 |
| TC3 | Highway: as TC2 with 50 L of water | 3,167 | 4,382 | 1,268 | 218 | 6.9 | 2,949 | +333 | +1,101 | 3,693 | 261 |
| TC4 | Bikes and kit out, water full | 3,051 | 4,373 | 1,187 | 216 | 7.1 | 2,835 | +449 | +1,215 | 3,572 | 259 |
| TC5 | Bikes and kit out, tanks empty | 2,651 | 4,327 | 1,263 | 214 | 8.1 | 2,438 | +849 | +1,612 | 3,172 | 256 |
| TC6 | Tuareg only, water full | 3,342 | 4,376 | 1,203 | 235 | 7.0 | 3,107 | +158 | +943 | 3,868 | 277 |
| TC7 | Street Triple only, water full | 3,302 | 4,417 | 1,195 | 203 | 6.2 | 3,099 | +198 | +951 | 3,826 | 246 |

The towball stays between 191 and 235 kg in every case, or 229 to 277 kg with growth. It is never above the 280 kg design ceiling and never below 6 % of the trailer's mass. Carrying one bike moves it most, because the Tuareg sits 349 mm ahead of the bikes' combined CoG and the Street Triple 411 mm behind it. Tuareg only with growth comes within 3 kg of 280 kg.

The car's rear axle, by report 07's load budget method: the car's DIN kerb mass of 2,085 kg with 54 % on the front axle (assumption), two adults of 160 kg 1.15 m behind the front axle, the rear seats out (50 kg), a 30 kg towbar and the 221 kg towball 1.1 m behind the rear axle. That puts 1,334 kg on the rear axle before any gear, against its 1,600 kg limit, and 1,112 kg on the front. The car can then carry 385 kg of gear on the floor where the rear seats were before the rear axle binds (the GVM would bind at 394 kg). With the ball 1.06 to 1.23 m behind the axle the rear axle carries 1,331 to 1,345 kg. Weighbridge figures replace all of these assumptions.

## Mass

The tare is 2,543 kg: drawbar and coupling 199, chassis 380, running gear 301, body 670, roof 90, under the floor 170, front zone 300, living zone 247 and the module 186.

The trailer fails its mass checks. Fully loaded with 400 L of water it weighs 3,517 kg, 17 kg over the 3,500 kg ATM before any growth allowance. With the allowance it weighs 4,043 kg, 543 kg over. The axle group then carries 3,779 kg, which is 279 kg over the NSW examiner's 3,500 kg GTM cap. Cruisemaster's ratings do not include VSB1's 120 % rule, so MAS-02 checks 1.2 times that load, 4,535 kg, which is 485 kg over the kit's 4,050 kg GTM. Each tyre would need 1,134 kg under the 120 % rule against the tyre's 1,030 kg. Even the highway case with 50 L of water is 193 kg over the ATM with growth. No body length passes, because the 5,000 mm body saves only 44 kg.

The water is the largest single variable, at 1 kg per litre. The fully loaded case meets the ATM without growth at 383 L. With growth it cannot be met by water alone, because the allowance (525 kg) is larger than the water. The allowance shrinks as estimates become maker figures and weighed parts (0 %), so the real question is how much of the 2,603 kg of estimated mass in the fully loaded trailer turns out lighter or heavier. These five lines carry the largest allowances. The towball change is for the line coming out 20 % heavier, fully loaded.

| Line | Mass | Growth allowance | CoG X | Towball change at +20 % |
|---|---|---|---|---|
| RG-01 XT Air kit (4 arms with bags, hubs and brakes), the air kit's weight not published | 180 | 36 | 4,557 | +1 kg |
| CH-01 main rails (2), section not sized yet | 128 | 26 | 4,570 | +1 kg |
| UF-04 lithium battery, 12 kWh | 110 | 22 | 5,843 | -5 kg |
| BD-01 floor panel, 8.0 kg/m2 from the older model | 106 | 21 | 4,570 | +1 kg |
| RG-02 wheels and tyres (4), neither weight published | 104 | 21 | 4,707 | 0 kg |

The bikes' centres of gravity are also estimates (report 05, low confidence). A 100 mm error in the bikes' combined CoG along X moves the towball by about 8 kg.

OPEN, the mass. These are the levers, with their size. None is taken here.

- Carry less water when the bikes are aboard. Each 100 L is 100 kg off the trailer and barely changes the towball, because the tanks sit over the axles.
- Weigh or source maker figures for the large estimated lines. Every kilogram moved from estimate to weighed removes 0.2 kg of allowance.
- Lighter choices among the estimates, for example the 40 kg generator, the 65 kg washer-dryer and the 60 kg inverter and chargers.
- The kit is no longer the limit. The 4,500 kg XT Air build's 4,050 kg GTM covers the 120 % rule at the ATM, and MAS-02 fails only through the growth allowance. The 3,500 kg ATM cannot rise, because it is the car's limit.
- Agree the growth allowance with the engineer. MASS-06 calls its percentages a proposal.

## Body length

| Body | Front zone needs | Living zone needs | Room for both | Spare | Axle from ball | Tare | Fully loaded | With growth |
|---|---|---|---|---|---|---|---|---|
| 5,000 | 1,700 | 1,700 | 3,090 | -310 | 4,435 | 2,500 | 3,474 | 3,990 |
| 5,500 (recommended) | 1,700 | 1,700 | 3,590 | +190 | 4,707 | 2,543 | 3,517 | 4,043 |
| 6,000 | 1,700 | 1,700 | 4,090 | +690 | 4,933 | 2,602 | 3,576 | 4,113 |

Room for both is the inside length less the 1,840 mm module. The front zone's minimum is set by the walkway from its door against the heater and hot water unit at partition A. Without the heater there, the kitchen slide-out's 1,500 mm would set it. The living zone's minimum is set by the clear floor in front of the partition B doorway against the bathroom.

Nothing is dropped to make 5,000 mm fit. These options shorten the zones, and the build works each one out from the same blocks.

| Option | Saves | Mass change | Spare at 5,000 mm |
|---|---|---|---|
| OPT-1: move the heater and hot water unit into the drawbar box or under the floor | 200 mm | 0 kg | -110 mm |
| OPT-2: move the partition B doorway 200 mm towards the kerb (DESIGN.md does not place it yet) | 90 mm | 0 kg | -220 mm |
| OPT-3: options 1 and 2 together | 290 mm | 0 kg | -20 mm |
| OPT-4: options 1 and 2 with a 1,200 mm kitchen slide-out and wardrobe | 350 mm | -23 kg (estimate) | +40 mm |

So 5,000 mm works only with option 4, with 40 mm to spare. Option 3 leaves it 20 mm short. OPEN for the owner. The 5,000 mm body also moves the axle to X 4,435 and leaves the module held by the zones, with the bikes 106 mm ahead of the axle. It saves 44 kg and does not change the mass result.

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
| Axle group centre | X 4,707. Hubs at X 4,292 and 5,122. XT front hinge crossmember rear face X 3,873, centre crossmember X 4,653 to 4,703, rear shock crossmember front face X 5,483 |
| Crossmembers under the garage and the tanks | The three XT crossmembers above (150 x 50 x 3 RHS, full rail height) |
| Battery bay | Behind the rear shock crossmember, closed by a crossmember at X 6,153 |
| Other crossmembers | X 1,820 (body front), 2,496 and 3,147 under the front zone, 6,711 and 7,270 (body rear) under the living zone. The intermediate ones come from a 700 mm pitch rule (PLACEHOLDER) |
| Outriggers | At the crossmember stations X 1,820, 2,496, 3,147, 3,823, 6,153, 6,711 and 7,270, from the rail to the body edge |
| Overall length | 7,380 mm, coupling head to body rear |
| Overall width | 2,500 mm with the awning |
| Travel height | 2,748 mm, roof down |
| CoG for the roll and track check | Fully loaded X 4,412, Z 1,212 (1,217 with growth), 863 mm above the hub centres. Every case is in the load case table |

The engineer should know one structural gap. No outrigger can pass over the tyres, because the floor underside is only 50 mm above them at full bump. So outboard of the rails there is no support between X 3,873 and 6,153, which covers the whole garage. There the floor has to span 557 mm from the rail raisers to the side walls, or hang from the walls, and it carries the bikes' wheels and the chocks near the walls.

## Tuareg panniers

The owner leaves his Mosko Moto panniers on the Tuareg in the garage, and he measured the bike at about 970 to 980 mm wide with them. The model gives each pannier a 457 x 203 x 508 mm envelope from Mosko Moto's Backcountry 30L figures, with the outer faces 490 mm from the centreline. Their position along the bike and their height are estimates, the top level with the tail rack. They are part of the Tuareg's envelope, so the existing checks CLR-03, CLR-04 and CLR-06 cover them, and none of those results changed. A new reported check, CLR-08, measures them against the straps and track fittings. The nearest is the Street Triple's right-side rear strap, 56 mm from the Tuareg's left pannier. The panniers' 9 kg (estimate) is carried in the trailer's mass whenever the Tuareg is.

## Checks

The whole-trailer checks are in `data/checks.yaml` under `trailer_checks`. The towball limits are design targets from report 07, not legal limits: 280 kg is the car's and the towbar's rating, used as a ceiling, and 6 % is the floor report 07 sets for stability. VSB1 sets no towball share.

| ID | Check | Result |
|---|---|---|
| MAS-01 | Mass with growth within the 3,500 kg ATM | FAIL, 4,043 kg fully loaded |
| MAS-02 | Axle group with growth, times 1.2 because Cruisemaster's ratings do not include the 120 % rule, within the kit's 4,050 kg GTM | FAIL, 4,535 kg fully loaded |
| MAS-03 | Towball never above 280 kg, with and without growth | PASS, 277 kg Tuareg only with growth |
| MAS-04 | Towball at least 6 % in every case | PASS, 6.2 % Street Triple only |
| MAS-05 | Towball within 10 kg of the 221 kg target fully loaded | PASS, 221 kg |
| MAS-06 | Tyre load with VSB1's 120 % rule within 1,030 kg | FAIL, 1,134 kg with growth (989 kg without) |
| MAS-07 | Axle group with growth within the NSW GTM cap (3,500 kg) | FAIL, 3,779 kg fully loaded |
| MAS-08 | Mass with growth within the NSW ATM cap (3,500 kg) | FAIL, 4,043 kg fully loaded |
| MAS-09 | Wheel rating meets the 120 % rule (reported) | 984 kg needed, Porsche's rating not known |
| CAR-01 | Car's rear axle before gear (reported) | 1,334 kg against 1,600 kg |
| CAR-07 | Towball scale against the model (reported) | Not measured yet |
| FIT-01 to FIT-04 | Front zone, living zone, tanks and battery, drawbar box | PASS |
| FIT-05 | Tyres at full bump clear the chassis and body | PASS, 50 mm to the floor |
| DIM-01 | Width with the awning within 2,500 mm | PASS, 2,500 mm |
| DIM-02 | Front load space not shorter than the rear overhang | PASS, 2,887 against 2,613 mm |
| DIM-03 | Coupling height inside 350 to 460 mm with its tolerance | PASS, 420 to 460 mm |
| DIM-04 | Running clearance at least 100 mm | PASS, 380 mm at the coupling head |
| JK-01 | Body corners and drawbar box at a 90 degree jack-knife | PASS, 100 mm at the box |
| JK-02 | Drawbar members and stone guard to the car (reported) | In plan from 49 degrees |

Each check row on the site names the measured inputs it uses.

Because MAS-01, MAS-02, MAS-06, MAS-07 and MAS-08 fail, `make strict` fails. That is the design's real state, and the limits stay as they are.

## Registration

The trailer will be registered in NSW, with Victoria as the fallback. Report 02 sets out the NSW path for a concessional trailer. The owner applies for a TfNSW identity approval with form 5703, four photos of the trailer (each side, front and rear), photos of the vehicle plate and the drawbar, a weighbridge ticket showing the tare and the VIN, and receipts that show where the materials came from. The examiner checks the design against VSB1 and sets the plate figures. GTM is capped at the lowest of the tyre load capacities, the coupling rating, the safety chain rating and the brake rating. ATM is capped at the lower of the coupling and chain ratings.

With the chosen parts the four tyres carry 4,120 kg (1,030 kg each), the DO35 coupling and the 4177-35 chains are rated 3,500 kg, and the drums 4,500 kg. So the GTM cap is 3,500 kg, set by the coupling and chains, and the ATM cap is 3,500 kg. The ratings are in `data/load_cases.yaml` under `registration`, and MAS-07 and MAS-08 check against the caps. Both fail on the current estimates, for the same reason as MAS-01.

## Measured inputs

Every value the owner will measure later is an input in `data/measurements.yaml`, which can be edited in GitHub's web editor. Each one has how to measure it, the estimate with its source, an empty measured slot with a date, and the rules that change the plan. The build uses the measured value when there is one. The site's Measurements page lists every input, its status, the value in use, what depends on it and what each rule did.

The rules re-solve the plan rather than raise flags. The towball target follows the car's weighbridge figures, the ball position and the planned gear. The Tuareg's width at the Street Triple's bar end sets the bike spacing: at or below 668 mm the 760 mm spacing holds, and above it the spacing grows by the excess, the build finds the smallest spacing at which CLR-03 measures 30 mm, and the garage, the module and the axle position follow. Porsche's wheel rating decides between the Porsche wheel and a rated 5 x 130 aftermarket wheel. Cruisemaster's answers set the kit GTM and whether MAS-02 applies the 120 % rule. Weighbridge figures at each build stage replace the estimates for the parts already built.

Three inputs have answers so far. The Tuareg is 585 mm wide across its side panels at the Street Triple's bar end (owner, 18 Nov), inside the 668 mm threshold, so the spacing stays at 760 mm and the garage at 1,800 mm. CLR-03 measures 71.5 mm, governed by the Street Triple's right bar end against the Tuareg's side panels. The Tuareg is 980 mm wide over its panniers (owner). Cruisemaster said its ratings do not include the 120 % rule (SUP-02), so MAS-02 checks 1.2 times the axle load. The crash bars are modelled as a 965 mm wide box up to 900 mm (estimate), because the owner says they sit much lower than the Street Triple's bar end at about 1,010 mm. If their measured top comes out above 970 mm, the spacing solve re-measures them.

The bed beams were sized for the 1,800 mm span. BED-01 reports their sag under 255 kg spread over the bed: 5.1 mm at 1,800 mm, with a bending stress of 26 MPa. It follows the span if the spacing ever grows.

## What changed from the older block model

The older model assumed a 6,000 mm body, 140 kg on the ball, a garage floor at 1,040 mm, 800 mm tyres, 900 mm axle spacing and 250 L of water. This layout uses 5,500 mm, 220 kg, 858 mm, 737.7 mm, 830 mm and 400 L. Its masses carry over line by line, except that the coupling line loses the sway control (now in the running gear), the gas bottles are split into bottles and gas, and the body panels, rails and crossmembers are worked out from the model's sizes at the older model's rates.

## Open questions

1. DIM-01's handedness (see Datum).
2. The mass: which of the levers in Mass to use, and the growth allowance to agree with the engineer.
3. Whether to take option 3 or 4 for a 5,000 mm body, or stay at 5,500 mm.
4. The track: matched to the car (1,660 mm) or wider for roll stability (report 06). The rail width follows from it.
5. The utility door side, the entry door position and the partition B doorway position.
6. The real space between the rails around the XT airbags and shocks, from Cruisemaster's XT Air kit drawing, for the tanks and the battery.
7. The car's rear bumper height and corner shape, and the ball position, for the jack-knife.
8. A spare wheel. The trailer shares the Cayenne's wheel, so one spare could serve both. None is in the mass.
9. The Porsche 8J x 18 wheel's load rating (reports 06 and 07). Each wheel needs about 984 kg under the 120 % rule at the ATM. It now comes before the Cruisemaster design session, because Cruisemaster measures the chosen wheel there.
10. Cruisemaster's design session: its rating for the XT Air build (SUP-01, 4,050 kg in its published table), the C/F for the ET53 wheel (SUP-04), the stud length from the wheel's mounting pad, and which air controls to fit, manual valves or automatic height valves.

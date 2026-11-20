# 18: The trailer's layout for the LandCruiser 79

Note added 20 Nov 2026, on publication. This is the layout study the trailer redesign started from, published as report 18 with its data file `research/18-trailer-layout-79.yaml`. The design took layout 1 (decision log 12:10, `docs/decisions.md`) and is now TRAILER.md revision H, CHASSIS.md revision D and BODY.md revision B, whose built figures replace this study's estimates. Three study inputs changed in the build. The generator and the petrol ride in a sealed drawbar box, not under the bed (decision log 12:45). The towball sits 1,300 mm behind the ute's rear axle, so the bike box overhangs the ball by 210 mm, not 160 mm (decision log 12:45). The tare is 2,197 kg and the towball 179 to 220 kg on base weights, against this study's 2,183 kg and 185 to 220 kg. Where this study says "today" it means the trailer at commit c38f797, with its garage. The study's change list for the build (section 4.3) is kept as written.

Layout study, 20 Nov 2026. Leonard asked to put the two bikes and some tools in an enclosed box on the ute so the trailer can be smaller and lighter, and to redesign the whole plan for the new vehicle. This study sets the trailer's new layout before the model is built. Sources are the repo at commit c38f797 and reports 02, 06, 11, 12, 13, 16 and 17. Estimates are marked.

## Recommendation

Build layout 1: the queen bed across the front of the trailer, 750 mm above the floor, with the kitchen slide-out, the air-conditioner, a sealed generator and fuel locker and storage under it, and a fixed hard roof with standing room.

- Body 4,420 x 2,400 mm, 1,080 mm shorter than today. Overall 6,300 mm long, 2,917 mm high, 1,950 mm inside.
- Tare 2,183 kg (2,409 kg with the growth allowance), 345 kg lighter than today. Fully loaded with all 400 L of water, 2,763 kg (3,022 kg).
- Towball 185 to 220 kg on base weights and 205 to 246 kg with growth, 7.5 to 9.2 % of the trailer's mass, with no ballast in any case.
- Plate the ATM at 3,100 kg, or at 3,000 kg once about 25 kg comes off the estimates (open question 1).
- Axle group centre at X 4,247. Cruisemaster XT Air, the 4,500 kg build, at 900 mm axle spacing on LC5 M14 hubs. ROH Trak 2 16 x 7 ET 0 wheels with LT265/75R16 tyres, the ute's wheel. Floor at Z 925.
- Track 1,555 mm, the ute's front track, so the trailer runs in the 79's ruts. It tips at 34.5 degrees fully loaded, the same as today's design at 1,662 mm.
- Drawbar 1,820 mm, unchanged. The spare wheel clears the bike box by 525 mm at a jack-knife. Coupling at Z 440, so the ute's tongue is set for 440 mm, not 450 mm.

Nothing blocks the redesign. Three inputs need Leonard: the ATM plate, the inside height (1,950 mm assumed, for people up to about 1.88 m tall), and whether one sleeper climbing over the other is acceptable. Layout 2, the island bed at the back, avoids the climb for 830 mm and 137 kg more.

## 1. Three layouts

### 1.1 What every layout shares

Positions are in the project datum DIM-01 (report 02): X rearward from the ball, Y positive to the road side, Z up from the ground at ride height, in mm. Inside the body, u is the distance from the inner face of the front wall.

- Body 2,400 mm wide with 35 mm walls, so 2,330 mm inside. Report 12's panels, joints and mounting.
- Floor surface at Z 925. The 805 mm tyre puts the hub at Z 382.5 (free radius less 20 mm, the repo's estimate). Full bump adds 60 mm, the tyre top reaches Z 845, and 50 mm of clearance puts the floor underside at Z 895. The 30 mm panel sits on top. That is report 09's rule of tyre diameter plus 120 mm.
- Drawbar 1,820 mm from the ball to the body front, as designed (section 3.6).
- The generator and the jerry cans are petrol, and the garage that held them is gone. They need a sealed locker reached only from outside, vented low, with no opening into the living area. This follows report 02's rules for the petrol garage (GAR-01 to GAR-06).
- The kitchen slide-out (1,500 x 600 x 450 mm) stays in the kerb-side wall at the front corner, its opening 150 mm from the corner, under the awning. Report 12's rules hold: 300 mm of full wall between openings and 150 mm from an opening to a corner.
- Water: two tanks between the rails over the axles. With 900 mm axle spacing the front bay grows 70 mm. The tanks become 830 and 760 mm long, 975 mm wide and 288 mm high, about 420 L net (scaled from report 13's 195 L tank). All 400 L ride in the trailer.
- A 2.5 kg fire extinguisher and a fire blanket inside the entry door (VSB1 13.2.2, one compartment now).

### 1.2 Layout 1: the bed across the front

Body 4,420 mm, 4,350 mm inside. Fixed roof, 1,950 mm inside (section 2).

| Zone | u (mm) | Kerb side | Road side |
|---|---|---|---|
| Bed | 0 to 1,650 | Queen across the trailer, mattress 1,530 x 2,030 mm, top 750 mm above the floor. Under it: the kitchen slide-out | Under the bed: the Truma Saphir, ducted, and the sealed generator and fuel locker, 900 x 400 x 520 mm, with a hatch in the road-side wall. A 300 mm column of shelves and a pull-out hanging rail at the bed's road-side end |
| Living | 1,650 to 3,350 | Entry door (body u 1,950 to 2,572), fridge (2,560 to 3,160), freezer turned along the wall under a lift-up bench (3,160 to 3,960) | Desk 1,100 x 550 mm with two seats (1,650 to 2,750). Washer against the wall and the Truma Combi D 6 beside it, with the XT Air supply and the spare bag on top (2,750 to 3,350) |
| Rear | 3,350 to 4,350 | Tall cupboard, 390 x 600 mm (3,960 to 4,350) | Wet bathroom, 1 x 1 m, door on its kerb-side face. The Victron board hangs on its front wall above the washer and the heater |

- Bed: 537 mm of clear height under the deck holds the slide-out, the air-conditioner, the locker and about 1.2 m3 of storage behind drawers and lift-up panels. Headroom over the bedding is 1,150 mm. No ladder.
- Wardrobe: clothes go in the bedside column (0.7 m3) and the tall cupboard (0.46 m3), with the bed drawers for folded clothes. Together they replace today's wardrobe over the kitchen (1.06 m3).
- Walkway: at least 730 mm wide from the bed to the rear wall, and 1,180 to 1,780 mm at the door and the desk. The door, seat and bathroom landings stay clear (checked box by box).
- Windows: front wall 800 x 400 mm over the bed head, kerb wall 500 x 450 mm over the bed (above the kitchen opening), road wall 900 x 500 mm over the desk, kerb wall 500 x 450 mm over the freezer bench, rear wall 600 x 450 mm at the end of the walkway. The toilet's service door and the locker hatch are in the road-side wall. No roof hatches: the 4,108 x 2,168 mm solar array leaves only 312 mm of roof.
- For two people for weeks: the bed stays made, two can sit at the desk to eat and work, and the fridge is just inside the door from the outdoor kitchen. The bed is against the front wall, so one sleeper climbs over the other at night.

### 1.3 Layout 2: the bed along the trailer at the back

Body 5,250 mm, 5,180 mm inside. Fixed roof, 1,950 mm inside.

| Zone | u (mm) | Kerb side | Road side |
|---|---|---|---|
| Front | 0 to 1,650 | Kitchen slide-out with the wardrobe over it, as today | Desk 400 x 1,000 mm across the front corner, the Truma Saphir under it, the seat behind it (400 to 900) |
| Middle | 900 to 3,050 | Entry door (body u 1,950 to 2,572), washer with the Victron board above it (2,560 to 3,030) | Freezer (900 to 1,450), fridge (1,450 to 2,050), wet bathroom (2,050 to 3,050) |
| Bed | 3,050 to 5,180 | 400 mm strip beside the bed | Queen along the trailer, head on the rear wall, mattress top 700 mm above the floor, 400 mm strips on both sides |

- Bed: 487 mm under the deck holds the Truma Combi D 6, the XT Air supply, the sealed generator and fuel locker with a hatch in the rear wall, and gear. Bedside cupboards at the head. Headroom over the bedding is 1,200 mm.
- Walkway: 860 mm between the washer and the bathroom, 400 mm along each side of the bed.
- Windows: front 800 x 400 mm over the desk, road side 900 x 500 mm at the seat, 500 x 450 mm in each side wall at the bed, rear 600 x 450 mm over the bed head. The roof is long enough for the solar array and both roof hatches at its ends.
- For two people for weeks: the best of the three. Each sleeper gets out on their own side, and the bathroom sits between the bed and the living area. It costs 830 mm of body and about 140 kg against layout 1.

### 1.4 Layout 3: the bed lifting into a raised roof

Body 3,300 mm, 3,230 mm inside. It needs report 12's raising roof: 1,800 mm inside roof down, 825 mm lift, 2,625 mm raised.

| Zone | u (mm) | Kerb side | Road side |
|---|---|---|---|
| Front | 0 to 1,600 | The kitchen slide-out under the kerb-side seat | A U-shaped lounge round a table, entered from the walkway. The Truma Saphir under the front seat, the freezer (turned) and the battery under the road-side seat. Over it, the queen across the trailer on a four-point electric lift |
| Rear | 1,600 to 3,230 | Entry door (body u 1,950 to 2,572), fridge (2,560 to 3,160) | Washer and heater (1,600 to 2,200), wet bathroom (2,200 to 3,200) with the Victron board on its front wall |

- Bed: stowed under the lid for travel, its underside 1,537 mm above the floor. At night it lowers to a mattress top of 1,570 mm, which leaves 1,005 mm of sitting room with the roof raised. By day it rises with the lid and leaves standing room under it. A ladder reaches it.
- The generator and the jerry cans ride in a box on the drawbar, X 1,100 to 1,480, outside the bike box's sweep (section 3.6).
- Wardrobe: clothes go in lockers under the seats and a cupboard over the fridge. There is no full-height wardrobe.
- Walkway: at least 730 mm, between the door landing and the heater and between the fridge and the bathroom.
- Windows: front 800 x 400 mm, road side 900 x 500 mm and kerb side 500 x 450 mm round the lounge, rear 600 x 450 mm at the end of the walkway. No roof hatches.
- Only three solar panels fit, 1,290 W against 1,720 W.
- For two people for weeks: shortest and lightest to tow, and the lounge seats four. But the roof must be up to sleep, and report 12 says to lower it in gusts over 60 km/h. The bed is a ladder climb into a canvas-walled space. Two lift systems must work every night, and roof down the whole inside is 1,800 mm high.

### 1.5 The three side by side

| | Layout 1, front cross bed | Layout 2, rear island bed | Layout 3, roof bed |
|---|---|---|---|
| Body length | 4,420 mm | 5,250 mm | 3,300 mm |
| Overall length, coupling head to body rear | 6,300 mm | 7,130 mm | 5,180 mm |
| Bed height and access | 750 mm, one climbs over | 700 mm, both sides free | 1,570 mm, ladder, roof up |
| Headroom | 1,950 mm everywhere | 1,950 mm everywhere | 1,800 mm roof down, 2,625 mm raised |
| Solar | 1,720 W, no roof hatches | 1,720 W and two hatches | 1,290 W |
| Tare (section 3) | 2,183 kg | 2,320 kg | 2,084 kg |
| Fully loaded, 400 L | 2,763 kg | 2,900 kg | 2,663 kg |

Today's trailer is 5,500 mm long and 7,380 mm overall.

## 2. The roof

The comparison is for layout 1. The fixed roof is report 12's 40 mm lid panel bonded to walls 150 mm taller, so the inside is 1,950 mm high. The raising roof is report 12's: hard lid, canvas walls, four LINAK LA36 actuators, 1,800 mm inside roof down and 2,625 mm raised.

| Measure | Fixed hard roof | Raising roof | Basis |
|---|---|---|---|
| Tare | 2,183 kg | 2,236 kg | The lift, ring, canvas, latches and seals scale to 66 kg for this body. The taller walls add 14 kg. Net about 52 kg lighter fixed (61 kg with growth) |
| Centre of gravity, fully loaded | Z 1,132 | Z 1,148 | The lift hardware sits at the roof line |
| Headroom | 1,950 mm at all times | 1,800 mm roof down, 2,625 mm raised | A low bed needs no raised headroom: 1,150 mm over the bedding fixed, 1,000 mm roof down |
| Wind | No limit | Lower the roof in gusts over about 60 km/h (report 12) | |
| Dust | No moving seal | The bulb seal works roof down. Raised, the canvas zips let dust in (report 12) | |
| Heat and insulation | Walls R 1.0, roof R 1.3 m2K/W everywhere | About 11 m2 of canvas with almost no insulation when raised | Report 12 panel table |
| Field failures | None from the roof | Latches that unhook, canvas wear and mould, actuator or control faults, bent guides (report 12 section 6) | |
| Travel height | 2,917 mm | 2,767 mm | Floor 925 + inside height + 40 mm lid + 2 mm panels |
| Above the ute's box (top about 2,570 mm, report 17) | 347 mm | 197 mm | |
| Frontal area of the body | 4.85 m2 | 4.49 m2 | 2.4 m wide from the floor underside (Z 895) to the top |
| Area above the box, in the wind | 0.83 m2 | 0.47 m2 | |
| Extra fuel at 100 km/h | About 1.2 L/100 km, about 6 % (estimate) | Baseline | 0.36 m2 x drag coefficient 0.8 (estimate) x 463 Pa = 133 N, 3.7 kW at the wheels, 240 g/kWh, 90 % driveline. Towing at 18 to 20 L/100 km (report 16 section 7) |
| Cost of the roof hardware | About AUD 300 more panel and joiners (estimate) | About AUD 4,000 to 7,000 (estimate) | Four synchronised actuators at about AUD 200 to 900 each (IP66 units start at [AUD 207](https://www.progressiveautomations.com/en-au/pages/standard-linear-actuators)), a custom canvas skirt about AUD 1,500 to 2,500, the top ring, latches and seals about AUD 800 |

Recommendation: the fixed hard roof, 1,950 mm inside. With the garage gone the bed no longer sits high, so the raising roof's 2,625 mm buys nothing the two people use. The fixed roof is 52 kg lighter, cheaper by several thousand dollars, has no moving parts to fail in dust and heat, insulates the whole body, and gives standing room at every stop and in any wind. Its cost is 150 mm of travel height, about 0.36 m2 more area above the ute's box, and about 6 % more fuel at highway speed (estimate). Neither roof hides behind the box, so branches that the ute passes under can reach the trailer either way.

Two follow-ons. The second way out from the bed becomes the kerb-side window over the bed, at least 500 x 450 mm and opening from inside, in place of report 12's zip panel in the canvas. Each 50 mm taken off the inside height lowers the travel height by 50 mm and saves about 4 kg, so a lower ceiling suits shorter owners.

## 3. Mass, balance and running gear

### 3.1 How the masses are built

Every line starts from the repo's mass schedule at commit c38f797 (`build/trailer/trailer.json`, tare 2,528 kg) and is scaled, never guessed afresh:

- Chassis: the rails and raisers at 33.4 kg per metre of frame (today's 31.1 kg/m, with an RHS 125 x 50 x 3 raiser in place of the 100 x 50 x 3, section 3.4). Crossmembers and outriggers by the number of stations, and 9 % shorter on the narrower rails. The drawbar, coupling plate, lugs, steadies and fittings are unchanged.
- Body: report 12's panel masses per square metre (floor 8.92, walls 6.0, front wall 6.7, roof 7.0 kg/m2), extrusions per metre of edge, and the products by count. No garage door, rear portal or garage vents.
- Running gear: the LT265/75R16 at 22.6 kg (Yokohama's figure, report 16) and the ROH 16 x 7 ET 0 at 14.5 kg (estimate, report 16).
- Equipment: report 13's products, unchanged. The garage kit (chocks, track, straps, ramp, winch, vents, detector, garage extinguisher, 101 kg) moves to the ute with the bikes (report 17).
- Growth: the repo's MASS-06 allowance by line (estimate 20 %, calculated 7 %, maker's figure 0 %).

Tare, kg (with growth in brackets):

| Group | Today, 5,500 mm | Layout 1 | Layout 2 | Layout 3 |
|---|---|---|---|---|
| Chassis and drawbar | 583 | 525 (562) | 576 (617) | 444 (475) |
| Coupling and drawbar fittings | 46 | 46 (50) | 46 (50) | 46 (50) |
| Running gear and mud flaps | 325 | 342 (391) | 342 (391) | 342 (391) |
| Spare wheel | 33 | 37 (40) | 37 (40) | 37 (40) |
| Body shell, awning, wiring | 761 | 572 (637) | 650 (722) | 526 (591) |
| Solar | 31 | 31 (32) | 31 (32) | 24 (24) |
| Under the floor: tanks, guards, battery, diesel tank | 146 | 146 (155) | 146 (155) | 146 (155) |
| Generator and its locker | 21 | 28 (30) | 28 (30) | 36 (39) |
| Bed | 87 | 58 (67) | 55 (64) | 83 (97) |
| Garage kit | 101 | 0 | 0 | 0 |
| Living area and the XT Air supply | 395 | 400 (446) | 410 (457) | 400 (445) |
| **Tare** | **2,528** | **2,183 (2,409)** | **2,320 (2,559)** | **2,084 (2,308)** |

Where layout 1's 345 kg saving comes from: the garage kit 101 kg, the body shell 189 kg (1,080 mm shorter, no garage door, portal or pop-top, against 150 mm taller walls), the chassis 58 kg and the bed 29 kg. The new wheels, tyres and spare add 21 kg, the locker 7 kg and the living area's extinguisher and blanket 5 kg. Layout 3 saves only 99 kg more than layout 1, because its pop-top (about 49 kg net of the lower walls), bed lift (42 kg) and drawbar box (15 kg) eat most of what its short body saves.

The payload is the same in every layout: 400 L of water (400 kg), 30 kg of fuel (the heater's 15 L of diesel and the jerry cans) and 150 kg of gear (food 50, clothes and bedding 60, other gear 40). So fully loaded is the tare plus 580 kg: 2,763 kg for layout 1, 2,900 kg for layout 2 and 2,663 kg for layout 3.

### 3.2 Axle position and the towball in each case

The axle group moves along X, with everything tied to it (XT crossmembers, tanks, guards, diesel tank, wheels, mud flaps), until the fully loaded case puts 220 kg on the ball on base weights. That is the middle of the 200 to 250 kg band. The towball is then the mass times (axle X less CoG X) divided by the axle X, by moments about the axle (report 02 MASS-04).

| | Layout 1 | Layout 2 | Layout 3 |
|---|---|---|---|
| Axle group centre | X 4,247 | X 4,546 | X 3,490 |
| From the body front, share of the body | 2,427 mm, 54.9 % | 2,726 mm, 51.9 % | 1,670 mm, 50.6 % |
| Rear overhang behind it (VSB1 5.1.1 needs it no longer than the front) | 1,993 mm, passes | 2,524 mm, passes | 1,630 mm, passes |
| Hubs (900 mm spacing) | X 3,797 and 4,697 | X 4,096 and 4,996 | X 3,040 and 3,940 |

Layout 1, case by case:

| Case | Aboard | Mass kg | CoG X | Towball kg = mass x (4,247 - CoG X) / 4,247 | Share | With growth: mass, towball |
|---|---|---|---|---|---|---|
| TC1 | Tare | 2,183 | 3,887 | 2,183 x 359 / 4,247 = 185 | 8.5 % | 2,409, 205 |
| TC2 | 400 L, fuel, gear | 2,763 | 3,909 | 2,763 x 338 / 4,247 = 220 | 8.0 % | 3,022, 246 |
| TC3 | 50 L, fuel, gear | 2,413 | 3,864 | 2,413 x 383 / 4,247 = 217 | 9.0 % | 2,672, 243 |
| TC4 | 400 L, fuel, no gear | 2,613 | 3,929 | 2,613 x 318 / 4,247 = 195 | 7.5 % | 2,842, 216 |
| TC5 | No water, fuel, gear | 2,363 | 3,857 | 2,363 x 390 / 4,247 = 217 | 9.2 % | 2,622, 243 |
| TC6 | No water, fuel, no gear | 2,213 | 3,877 | 2,213 x 370 / 4,247 = 193 | 8.7 % | 2,442, 214 |

The levers are rounded to the millimetre, so a product can differ from the towball shown by up to 0.6 kg.

The water's centre sits 31 mm ahead of the axle centre, so 400 L moves the towball by only 3 kg (TC2 against TC5). The gear sits ahead of the axles, in the fridge, the freezer and under the bed, so taking all 150 kg out drops the towball by 25 kg (TC2 against TC4). No case needs ballast, and the towball never falls below 7.5 % of the trailer's mass.

Layouts 2 and 3, the same cases (mass, then towball, in kg):

| Case | Layout 2 | Layout 2 with growth | Layout 3 | Layout 3 with growth |
|---|---|---|---|---|
| TC1 tare | 2,320, 195 (8.4 %) | 2,559, 218 | 2,084, 188 (9.0 %) | 2,308, 208 |
| TC2 fully loaded | 2,900, 220 (7.6 %) | 3,172, 247 | 2,663, 220 (8.3 %) | 2,921, 244 |
| TC3 highway | 2,550, 218 (8.5 %) | 2,822, 245 | 2,313, 217 (9.4 %) | 2,571, 241 |
| TC4 water full, no gear | 2,750, 192 (7.0 %) | 2,992, 213 | 2,513, 207 (8.2 %) | 2,741, 228 |
| TC5 no water, gear | 2,500, 217 (8.7 %) | 2,772, 244 | 2,263, 217 (9.6 %) | 2,521, 241 |
| TC6 no water, no gear | 2,350, 189 (8.0 %) | 2,592, 211 | 2,113, 203 (9.6 %) | 2,341, 225 |

Towball range on base weights: layout 1 185 to 220 kg, layout 2 189 to 220 kg, layout 3 188 to 220 kg. With growth every case stays at or under 247 kg, inside the ute's 250 kg (report 16).

Centre of gravity height, fully loaded: Z 1,132 (layout 1), Z 1,156 (layout 2), Z 1,158 (layout 3). Today's trailer is at Z 1,206.

### 3.3 ATM and the XT Air build

The plated ATM must cover the heaviest case with growth (the repo's MAS-01). VSB1's 120 % rule then asks the axle group to carry 1.2 times (ATM less the towball), because the XT's two axles do not share load (report 06).

| | Layout 1 | Layout 2 | Layout 3 |
|---|---|---|---|
| Heaviest case with growth (TC2) | 3,022 kg | 3,172 kg | 2,921 kg |
| Plated ATM that covers it | 3,100 kg (78 kg in hand) | 3,250 kg (78 kg) | 3,000 kg (79 kg) |
| 120 % rule: 1.2 x (ATM - 220) | 3,456 kg | 3,636 kg | 3,336 kg |
| XT coil 3,700 kg build, GTM 3,330 kg | Fails | Fails | Fails by 6 kg |
| XT Air 3,400 kg build, GTM about 3,060 kg (assumed 90 % of the ATM rating, as the other builds) | Fails | Fails | Fails |
| XT Air 4,500 kg build, GTM 4,050 kg | Passes, 594 kg in hand | Passes, 414 kg | Passes, 714 kg |
| Load per wheel and tyre at the rule: 1.2 x (ATM - 220) / 4 | 864 kg against 1,400 kg (wheel) and 1,550 kg (tyre) | 909 kg | 834 kg |
| Combination at the ute's 3,850 kg with 250 kg on the ball | 6,700 kg against 6,900 kg | 6,850 kg | 6,600 kg |

Two notes. The brief names a 3,700 kg build, but report 06 lists the XT Air tandem at 2,800, 3,400 and 4,500 kg only. The 3,700 kg tandem is a coil build. And no air build below 4,500 kg covers the rule at any ATM above about 2,770 kg (3,060 / 1.2 + 220). So every layout keeps the 4,500 kg XT Air build the owner already chose. Air also keeps the ride height and the 1.9 Hz bounce the same with the tanks full or empty, which matters more now that all 400 L ride in the trailer.

Only layout 3 meets the 3,000 kg target with growth. Layout 1 meets it on base weights with 237 kg in hand, and is 22 kg over it with growth. Layout 2 is 172 kg over with growth.

### 3.4 Floor height and track

The floor surface is at Z 925 in every layout (section 1.1), 53 mm higher than today's Z 872. The rail underside sits at Z 597.5 (hub 382.5 plus the XT Air standard arm's 215 mm), the rail top at Z 747.5, and the gap to the floor underside at Z 895 is 147.5 mm. An RHS 125 x 50 x 3 raiser with a 22.5 mm bearer strip fills it, so the composite rail is 275 mm deep.

The ute's tracks are 1,555 mm front and 1,460 mm rear on its 265 mm tyres (report 16). Its front tyres cut ruts from 645 to 910 mm either side of the centreline, and the rear tyres widen them inward to 597.5 mm.

| Track | 1,460 mm (the ute's rear) | 1,555 mm (the ute's front) | 1,662 mm (today) |
|---|---|---|---|
| Rails and C/F | Not buildable. It needs rails 1,080 mm wide, under Cruisemaster's 1,150 mm minimum | Rails 1,175 mm outside, C/F 190 mm | Rails 1,286 mm, C/F 188 mm |
| Tyre inner wall to the rail (FIT-05 wants 50 mm) | | 54 mm | 52 mm |
| In the ute's ruts | | Fully, 641 to 913 mm | 57 mm of each tyre runs outside the front ruts |
| Side-slope angle, layout 1, fully loaded (Z 1,132) | | 34.5 degrees rigid, about 31.7 with tyre and suspension give | 36.3, about 33.5 |
| Side-slope angle, layout 1, worst case (TC5, Z 1,198) | | 33.0, about 30.3 | 34.7, about 32.0 |
| Layouts 2 and 3, fully loaded | | 33.9, about 31.2 | 35.7, about 32.9 |

The angle is the slope at which the trailer would tip, arctan(half the track / CoG height). The "give" figure takes 10 % off that ratio for tyre and airbag compliance (estimate). Today's trailer, at 1,662 mm and Z 1,206, tips at 34.6 degrees. The ute with the bike box tips at about 38.7 degrees (report 17's stability factor of 0.80).

Recommendation: 1,555 mm. It runs the trailer in the ruts the 79's front tyres cut in sand and in rutted tracks. The lower centre of gravity of the new layout pays for the narrower track: layout 1 at 1,555 mm tips at 34.5 degrees, the same as today's design at 1,662 mm. The trailer stays the weaker of the two vehicles on a side slope, by about 4 degrees.

### 3.5 Coupling height

The 805 mm tyre lifts the hubs, rails and drawbar 26.5 mm. Today the coupling point sits 131 mm below the rail underside, which would now put it at Z 466.5. VSB1 9.3.2 wants the ball at 350 to 460 mm laden, and the repo's DIM-03 check holds the coupling inside that with its 20 mm tolerance. So:

- Keep the coupling point at Z 440, plus or minus 20 mm (420 to 460 mm). The drop from the rail underside to the coupling point grows from 131 to 157.5 mm. A 26 mm drop block between the drawbar apex and the DO35's plate, or a 26 mm deeper apex, gives it.
- Set the ute's tongue for 440 mm laden, not 450 mm. At 450 plus 20 mm the ball would reach 470 mm, over VSB1's 460 mm.

### 3.6 Drawbar and the jack-knife with the bike box

Report 17 puts the bike box's rear face about 160 mm behind the ball and its sides 950 mm out. Its rear corners therefore sweep a circle of 963 mm radius about the ball (the square root of 160 squared plus 950 squared) as the trailer swings. At about 80 degrees of jack-knife a corner crosses the trailer's centreline at 963 mm from the ball. The repo's JK-01 check wants 100 mm of clearance.

| Item | Nearest point to the ball | Clearance at the worst angle | Rule |
|---|---|---|---|
| Spare wheel on the front wall (60 mm bracket, 272 mm tyre) | X 1,488 on the centreline | 525 mm | Passes. It sets the shortest drawbar at 963 + 100 + 332 = 1,395 mm |
| Body front corners | X 1,820, Y 1,200 | 1,217 mm | Passes |
| Jockey wheel, moved from X 500 to X 1,100 on the kerb-side member | X 1,100, Y -400 | 207 mm | Passes at any height |
| Layout 3's drawbar box, X 1,100 to 1,480 | X 1,100 on the centreline | 137 mm | Passes. It sets layout 3's shortest drawbar at about 1,783 mm |
| Coupling, chains, breakaway box, stone guard | Inside the circle | Under the box | Must stay below the box's rear underside, about 790 mm on report 17's lower tray. All sit below about Z 700 |

Recommendation: keep the drawbar at 1,820 mm in every layout. It could shorten to about 1,400 mm in layouts 1 and 2, but the shorter body already brings the axle 749 mm nearer the ball (X 4,247 against 4,996 today), and the ball to axle distance and the nose mass rank among the largest factors in sway stability (report 11 section 6.1). The designed drawbar and its VSB1 checks also stay as they are. Overall length is still 1,080 mm shorter than today in layout 1.

## 4. The recommended layout and the change list

### 4.1 Layout 1, as recommended

| Item | Value |
|---|---|
| Body | 4,420 x 2,400 mm outside, 4,350 x 2,330 x 1,950 mm inside, X 1,820 to 6,240 |
| Overall | 6,300 mm long (coupling head to body rear), 2,500 mm wide with the awning, 2,917 mm high |
| Floor, ceiling, roof top | Z 925, Z 2,875, Z 2,915. Solar panels to Z 2,917 |
| Zones, front to back | Bed zone u 0 to 1,650 (X 1,855 to 3,505). Living zone u 1,650 to 3,350 (X 3,505 to 5,205). Rear zone u 3,350 to 4,350 (X 5,205 to 6,205) |
| Bed | Queen across the trailer, mattress top Z 1,675, 1,150 mm headroom over the bedding, 537 mm clear under the deck |
| Openings | Kitchen opening X 1,970 to 3,470 (kerb), entry door X 3,770 to 4,392 (kerb), locker hatch X 2,500 to 3,300 (road), toilet service door X 5,630 to 6,080 (road) |
| Roof | Fixed, 40 mm panel, four Sunman panels in a 4,108 x 2,168 mm array from X 1,976, no roof hatches |
| Mass | Tare 2,183 kg (2,409 kg with growth). Fully loaded 2,763 kg (3,022 kg) |
| Towball | 185 to 220 kg on base weights, 205 to 246 kg with growth, 7.5 to 9.2 % |
| ATM | Plate 3,100 kg (section 3.3 and open question 1) |
| Axle group | Centre X 4,247, hubs X 3,797 and 4,697, 900 mm spacing |
| Running gear | Cruisemaster XT Freestyle Air, 4,500 kg build, standard arms, ride height 215 mm, LC5 M14 hubs (5 x 150, 110 mm spigot) on 12 inch ABS-enabled drums, Bosch TSC. ROH Trak 2 16 x 7 ET 0 with LT265/75R16 123/120 |
| Track | 1,555 mm: rails 1,175 mm outside, C/F 190 mm, ET 0 |
| Frame | Rails X 1,820 to 6,240, rail underside Z 597.5, RHS 125 x 50 x 3 raisers, floor underside Z 895. Eight stations |
| Coupling | DO35 V3Plus at Z 440, 157.5 mm below the rail underside |
| Drawbar | 1,820 mm, as designed. Jockey wheel at X 1,100 |
| Under the floor | Water tanks X 3,388 to 4,218 and 4,288 to 5,048, 420 L net. Battery box centre X 5,805. Diesel tank X 2,828 to 3,268 |

The item boxes are in `research/18-trailer-layout-79.yaml`, in the datum, with masses and growth.

### 4.2 Why layout 1

- It holds every living-area item, the queen bed and all 400 L in the shortest body that keeps a made-up bed and standing room: 1,080 mm shorter and 345 kg lighter than today's trailer.
- Its fully loaded mass, 2,763 kg, leaves 237 kg under the 3,000 kg target on base weights. Layout 2 is 137 kg heavier and 830 mm longer for the walk-around bed.
- The towball stays between 185 and 246 kg in every case, with or without growth, and needs no ballast.
- Layout 3 saves another 99 kg and 1,120 mm, but asks two people to raise the roof and climb a ladder every night, loses a quarter of the solar, and cannot be slept in when the wind forces the roof down.
- The price is the climb over at night, which layout 2 avoids.

### 4.3 Change list for the build

| Area | Change |
|---|---|
| Chassis (`data/chassis/chassis.yaml`, `cad/chassis.py`, CHASSIS.md) | Rails X 1,820 to 6,240, 1,175 mm outside. Raiser RHS 125 x 50 x 3, bearer strip 50 x 22.5 mm. Eight stations: front, two at the 700 mm pitch rule, XT front hinge, centre and rear shock about the axle at X 4,247, battery bay (front face X 5,445), rear. Outriggers 612.5 mm to the body edge. Plan bracing in the two bays ahead of the XT front hinge and the bay behind the rear shock. Coupling drop 157.5 mm. Jockey bracket at X 1,100. Corner steadies at about X 2,220 and 6,070. Re-run the frame model at the plated ATM (VSB1: 45.6 kN along, 15.2 kN across and vertical at 3,100 kg) |
| Running gear (`trailer.yaml` params, RG and SP lines) | tyre_d 805, tyre_w 272, axle_spacing 900, wheel_offset 0, cf 190, rail_outer_w 1,175, track 1,555. XT offsets for 900 mm: front hinge rear face -869, centre front face -19, rear shock front face +811, hubs -450 and +450. LC5 M14 hubs with the 110 mm spigot. RG-02 and SP-01 22.6 kg, RG-06 and SP-02 14.5 kg. Wheel rating 1,400 kg, tyre 1,550 kg |
| Body (`data/body/body.yaml`, `cad/body.py`, the BODY.md draft) | body_length 4,420, interior_h 1,950, fixed roof. A full rear wall with a 600 x 450 window and no portal. Windows and openings as section 4.1. A roof-to-wall joiner replaces the pop-top bottom ring. The escape window over the bed. Awning Fiamma F45s 450. Re-run BDY-01 to BDY-18 |
| Roof | Delete BD-12 and roof_lift. Solar array from X 1,976, no Heki hatches. Travel height 2,917 mm |
| Living area and bed | Take the boxes in `research/18-trailer-layout-79.yaml`. New lines LB-01 to LB-04 (bed), LA-08a to LA-08c (storage in place of the wardrobe), LA-12 (extinguisher and blanket), GL-01 (generator locker) with its zone |
| Under the floor | Tanks 830 and 760 x 975 x 288 mm, about 420 L net. Battery box centre 400 mm ahead of the rear wall's inner face, as now. Diesel tank ahead of the XT front hinge, as now |
| Load cases (`data/load_cases.yaml`) | TC1 to TC6 of section 3.2: no bikes, no ballast, 400 L in the trailer. Replace the Cayenne block with the VDJ79: towbar 3,500 and 350 kg, design towball ceiling 250 kg (rear axle), GCM 6,900 kg with the ute at 3,850 kg. Registration: plated ATM, tyre 1,550 kg |
| Checks (`data/checks.yaml`) | MAS-01 and MAS-08 against the plated ATM. MAS-03 at 250 kg. MAS-06 at 1,550 kg and MAS-09 at 1,400 kg. A new GCM check. FIT-01 for the new plan, FIT-04 becomes the locker fit, FIT-05 at the new track (54 mm). JK-01 and JK-02 against the bike box: the 963 mm circle with 100 mm clear, and everything inside it below Z 790. DIM-03 at 440 plus or minus 20 mm |
| Drawings | CT-001 redrawn. CT-101 to CT-103 re-solved. The body sheets for the fixed roof. CT-401, CT-402 and CT-501 retired |
| Docs and site | TRAILER.md, CHASSIS.md and the body draft revised for the 79. DESIGN.md retired or rewritten as the bed and storage. The site's Garage page moves to the ute's bike box. `measurements.yaml`: the bike, chock and pannier inputs move to the bike box, and the ute's laden ball height is added |
| Removed | The garage and bed module (ASM-GB) from the trailer, the rear door, ramp, chocks, straps, track, winch, vents, fume detector, bed beams, ledgers, partition A, ladder, safety net, ballast (BL-01, BAL-01), the car's water tank, PL-04 (the panniers ride with the Tuareg), the CLR, RES, BED and CON checks, the CAR checks, and the loading animation |

## Open questions

Each carries the assumption the plan uses until it is answered.

1. The ATM plate. A 3,000 kg plate holds every case on base weights (237 kg in hand) but is 22 kg short of the heaviest case with growth (MAS-01). Assumption: plate 3,100 kg. It stays inside the ute's GCM by 200 kg and every rating (XT 4,050 kg GTM, DO35 and chains 3,500 kg). Plate 3,000 kg instead if the largest estimates (the XT Air kit 180 kg, the extrusions 69 kg, the cabinetry 70 kg) weigh in about 25 kg lighter.
2. The ute's coupling height. Assumption: its tongue is set so the ball sits at 440 mm laden, plus or minus 20 mm, in place of the decision log's 450 mm (11:25), because 470 mm exceeds VSB1's 460 mm (section 3.5).
3. The inside height. Assumption: 1,950 mm suits both people, up to about 1.88 m tall. Each 50 mm less lowers the trailer 50 mm.
4. The climb over the bed. Assumption: accepted, as in many compact vans. Layout 2 is the fallback.
5. No roof hatches. Assumption: five opening windows, the Carafan CP700 and the bathroom vent ventilate the body. The fallback is three solar panels and a Midi Heki, which costs 430 W.
6. The kitchen bench height. With the floor at Z 925 the slide-out's bench is about 1,425 mm above the ground, 53 mm higher than today. Assumption: report 13's folding step goes with the kitchen.
7. Petrol under the bed. Assumption: the generator locker follows the garage's rules: sealed from the living area, reached only from outside, vented low, nothing electrical inside, and a petrol fume detector with its display by the bed (report 02 GAR-01 to GAR-06). The generator runs outside the locker.
8. The tanks. Assumption: 830 and 760 mm long, 975 mm wide and 288 mm high hold about 420 L net, at report 13's ratio of net to gross volume.
9. The tyre. Assumption: an envelope 272 mm wide (estimate) and a loaded radius 20 mm under the free radius (the repo's estimate). Both set the floor height, the 54 mm to the rail and the hub height.
10. The bike box. Assumption: report 17's rear face 160 mm behind the ball, 1,900 mm wide, its rear underside about 790 mm up (the lower tray). A flat deck raises the underside and only adds clearance.
11. The XT Air 3,400 kg build. Assumption: GTM 3,060 kg, 90 % of its ATM rating like Cruisemaster's other builds. It does not change the choice of the 4,500 kg build.
12. The new estimated lines. Assumption, each at 20 % growth: the bed base 20 kg, the generator locker 7 kg, the bedside column 15 kg, the tall cupboard 12 kg, the cupboards over the fridge 8 kg, the extinguisher and blanket 5 kg.
13. The floor panel. Report 12 sized it for the bike wheels, and a person's foot (span/228) now governs it. Assumption: keep report 12's panel.
14. The drawbar and rails at a 3,100 kg plate. VSB1's drawbar forces fall 11 % from the 3,500 kg design. Assumption: keep CHASSIS.md's members. The engineer may lighten the drawbar members to RHS 150 x 50 x 4, about 14 kg.
15. The awning. Assumption: the Fiamma F45s 450 (4,230 mm case) on brackets that stay within 100 mm of the body, as report 12 assumed for the F45L.

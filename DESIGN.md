# Garage and bed module: design (baseline)

Status: concept, revision D, 19 Nov 2026, with the floor height updated the same day for the trailer's own wheels and tyres (TRAILER.md revision D): 869 mm in place of 858 mm. On 20 Nov 2026 it became 872 mm, with the tyre at Yokohama's published 752 mm diameter (TRAILER.md revision F). Revision D moves the garage to the back of the trailer with a rear door, so the living space is one room (owner's decision). The bikes now stand along the trailer, side by side, noses forward. Partition B goes, partition A becomes the garage's front wall, and the bed covers the whole garage. Revision C placed the module in the trailer and kept the Tuareg's panniers on. Revision B lapped the deck over the partition and made the ladder owner-built. This is the baseline for the 3D model, drawings and website. Items marked OPEN need the owner's decision. Sources are the research reports in `research/` (01 tech stack, 02 design practice, 03 bike restraint and garage, 04 bed and materials, 05 bike geometry).

## Module frame

The module uses its own frame. The origin is on the garage floor surface, at the rear face of partition A, on the trailer centreline. X runs rearward along the trailer towards the rear door. Y runs across the trailer, positive towards the road (right) side. Z is up from the garage floor. Units are mm. These are the axes of the project datum DIM-01 (report 02, changed on 20 Nov 2026 to Y positive to the road side), so the module only moves when it is placed in the trailer. Module X 0 sits at datum X 4,955 in the 5,500 mm body and module Z 0 at datum Z 869 (TRAILER.md).

## Envelope

- Interior width 2,330 mm, so Y runs from -1,165 to +1,165 (2,400 mm body with 35 mm walls).
- Garage interior length 2,330 mm, X from 0 to 2,330, between partition A and the body's rear wall. The garage is square in plan.
- Ceiling with the roof collapsed at Z = 1,800 (target). The hard limit is 2,000.
- The garage floor is flat with no wheel arches. Its surface is 872 mm above the ground at design ride height, set by the running gear and the trailer's own LT245/70R16 tyres (TRAILER.md revision F, 872.0 mm). The 3,048 mm ramp then sits at 16.6 degrees, or about 15.5 degrees with the air bags vented.

## Bikes

- Both bikes stand along the trailer, side by side, noses towards partition A. They load nose first through the rear door and unload backwards.
- Each front tyre's leading edge is at X = 50, which allows 50 mm for the chock nose. This must be measured on a real chock (CHK-01).
- The Tuareg's centreline is at Y = +600, towards the road-side wall. The Street Triple's is at Y = -160, so they are 760 mm apart. That leaves the spare width on the kerb side for the gas locker and the stowage. The Tuareg's panniers sit at its back, and the Street Triple's tail is narrow, so the locker goes beside the Street Triple's tail.
- Why 760 mm works: the Tuareg's bar ends and handguards sit at about 1,190 to 1,215 mm, which is above the Street Triple's tank (1,007 mm) and bars (1,013 mm). The bars overlap in plan without touching. The limit is the Street Triple's bar end (396 mm from its centreline, at 1,013 mm) against the Tuareg's side panels at the same height. The owner measured the Tuareg 585 mm wide there, a half-width of 292.5 mm, so the gap is 71.5 mm against the 30 mm wanted (CLR-03). The crash bars sit much lower (owner), so the bar end passes over them. The bikes' relative position is the same as in revision C, so this result did not change.
- The garage width is fixed. If a later measurement grows the spacing, the Street Triple moves towards the kerb-side stowage. Its kerb-side fittings are 35 mm from the stowed ramp now, so spacings up to 780 mm fit. Above that CLR-10 fails and the layout needs redesigning (measurements.yaml TU-01).
- The Tuareg's mirrors fold down or come off for transport (with mirrors up it is 1,445 mm tall). Its top is then the screen, about 1,390 mm in Aprilia's image (the owner's figure is 1,370 mm). The chock cradle may lift the front wheel by up to 25 mm.
- Bike geometry comes from `research/05-bike-geometry.yaml`. The owner's overall figures govern where they differ.
- The Tuareg keeps its Mosko Moto panniers on in the garage. The owner measured it at about 970 to 980 mm wide with them. Each pannier is modelled as a 457 x 203 x 508 mm envelope from Mosko Moto's Backcountry 30L figures, outer faces 490 mm from the bike's centreline. Their position along the bike and their height are estimates. They weigh about 9 kg with their frames (estimate), carried in the trailer's mass.
- In the bike frame, x points to the bike's rear, y to the bike's right and z up, with the origin on the ground under the front axle. Report 05 records y to the bike's left, so the model negates its lateral values. Placed in the module, bike x becomes module +X, bike y becomes module +Y, and bike z becomes module Z. The front axle sits at X = 50 plus the front overhang (348 mm Tuareg, 300 mm Street Triple).

## Rear door

- The garage door is in the body's rear wall and is top-hinged. Its opening runs from Y = -785 to +1,125, 1,910 mm wide, and from the floor to Z = 1,440. The header above it sits at the bed beams, and the rear wall's frame keeps 40 mm on the road side. The kerb-side jamb is the gas locker's inner face.
- Each bike has to roll straight back through it. CLR-09 measures each bike, as parked, against the door frame extended forward over the whole garage, which is what a bike rolled straight back meets. The Tuareg's road-side pannier clears the road-side jamb by 35 mm and the Street Triple's bar end clears the kerb-side jamb by 229 mm. Going down the ramp a bike pitches nose-up about its front tyre, which only lowers the parts behind the front axle, so the parked position governs.
- The door product and its structure belong to the body design. The header carries the deck's rear edge.

## Gas locker and stowage

- The gas locker sits in the kerb-side rear corner, X 1,570 to 2,330 and Y -1,165 to -785, 690 mm high outside. It holds two 9 kg cylinders and their regulator (envelope 320 x 320 x 500 mm per cylinder). It follows report 02 section 5.2: it holds only the cylinders and their equipment, it is reached only through a 700 x 630 mm hatch in the kerb-side wall, and it is sealed from the garage. A 25 mm drain at its base runs down to an outlet 500 mm below the floor, which offsets it vertically from the rear door sill and the garage's low vents. The battery box's vent is on the road side, about 2 m away, and the garage's kerb-side low vent is at the front of the garage. Each cylinder is clamped for 4 times its filled weight, about 0.7 kN in any direction.
- The generator (520 x 320 x 460 mm envelope) and the jerry cans (300 x 360 x 450 mm) are petrol, like the bikes, so they ride in the garage. They are strapped against the kerb-side wall in front of the gas locker, to a short track row at Y = -985.
- The ramp travels folded (1,524 x 152 x 965 mm) on its edge in a slot from Y = -772 to -620, beside the gas locker and inside the door opening, so it slides out of the rear door first.
- Loading order: generator and jerry cans first, with the garage empty, then the Tuareg, then the Street Triple, then the ramp. Unloading is the reverse, so the generator and jerry cans come out through the Street Triple's empty bay. OPEN: whether the owner wants the generator out without unloading the bikes. That needs a hatch into the kerb strip.

## Restraint (research/03)

- A Condor SC-2000 chock sits on each bike's centreline, its nose against partition A.
- Two flush L-track rows run across the trailer. The front row is at X = 250, 148 mm ahead of the Tuareg's front axle and 100 mm ahead of the Street Triple's. The rear row is at X = 2,048, 1,650 mm behind the Tuareg's front axle, and stops at the gas locker. These are report 03's positions from each bike's axles, so the straps meet each bike exactly as in revision C.
- Each bike has a front strap pair on the front row at Y = centreline ± 450 mm (Tuareg) or ± 400 mm (Street Triple). Its rear pair sits on the rear row at the same offsets, and its rear-wheel strap at centreline ± 250 mm.
- Straps are 35 mm SpanSet ratchets, LC 1,000 kg, on soft loops, with a Canyon Dancer harness on the Street Triple's bars. Every anchor and its floor fixing is designed for 20 kN.

### Strap loads along the trailer

Braking now pushes each bike forward along its length into its chock, and cornering pushes it sideways. RES-01 works out every strap's load by report 03's method, with its off-road factor of 2 on the NTC cases (0.8 g forward, 0.5 g rearward, 0.5 g sideways) and 1.0 g upward. The centre of gravity heights are report 03's design figures (700 mm Tuareg, 600 mm Street Triple), which are above the 05 estimates. Strap directions come from the model.

| Strap | Sideways, one strap takes 60 % | Braking | Rearward | Upward | Worst |
|---|---|---|---|---|---|
| Tuareg front pair | 221 kgf | 0 | 211 kgf | 67 kgf | 221 kgf |
| Tuareg rear pair | 277 kgf | 39 kgf | 0 | 67 kgf | 277 kgf |
| Street Triple front pair | 174 kgf | 0 | 230 kgf | 55 kgf | 230 kgf |
| Street Triple rear pair | 215 kgf | 23 kgf | 0 | 55 kgf | 215 kgf |

The worst strap is the Tuareg's rear pair at 277 kgf, a utilisation of 0.28 on the LC 1,000 kg straps. In revision C it was 395 kgf, because braking then pushed the bikes sideways. At 1.6 g the bikes would pitch over their front tyres (the Tuareg's centre of gravity is 764 mm behind its front tyre's contact and 700 mm up), so the rear pair holds the rear down, which is the braking column. The chocks take the forward push: 330 kgf for the Tuareg and 280 kgf for the Street Triple. Condor rates the chock for a 3,000 lb bike, which is a static figure, so the engineer confirms the chock and its four bolts for that push. Every anchor stays designed for 20 kN.

### Reaching the straps

Every strap is reached from a place where a person can kneel, and nobody has to get between the bikes once both are in.

- The Tuareg goes in first. Its two road-side straps are hooked on their road-side anchors before it goes in and laid over the wall pads, ratchet end up. With the bike in its chock, the person kneels in the empty Street Triple bay, clips those two tops on by reaching across the bike (about 750 mm to the bar loop and 600 mm to the pillion peg hanger), and ratchets them at the top. The kerb-side straps and the rear-wheel strap are in front of the kneeling person.
- The Street Triple's road-side straps are hooked on the anchors between the bays before it goes in, ratchet end up. Its front straps are reached kneeling in the front kerb corner, ahead of the jerry cans (about 610 mm across its narrow bars to the far loop), and its rear straps kneeling inside the rear door beside the gas locker (about 510 mm to the far hanger). The way to the front kerb corner is a floor-level corridor about 425 mm wide between the Street Triple's pegs and the stowage, under the bed. The mock-up checks it (build step S01).

## Bed (research/04)

- The deck covers the whole garage (2,330 x 2,330 mm) and is the sealed garage ceiling.
- Beam underside at Z = 1,460. That clears the Tuareg's screen (1,370 mm plus the chock rise) by 70 mm (CLR-01), or 51 mm with Aprilia's 1,390 mm figure.
- Five SHS 50x50x3 6060-T5 beams run across the trailer at X = 233, 699, 1,165, 1,631 and 2,097, a 466 mm pitch. They span 2,330 mm between 40x40x3 angle ledgers on the two side walls, with the shelf top at 1,460 mm. Ledgers on partition A and on the rear wall's door header carry the deck's front and rear edges with their shelf tops at 1,510 mm.
- The span grew from 1,800 to 2,330 mm, so the revision C beam (RHS 50x25x2.5, I 10.85 cm4) would sag about 11 mm under 255 kg spread over the bed. The SHS 50x50x3 keeps the 50 mm depth, so the deck and bedding heights do not change. Its I is 20.8 cm4 (calculated with square corners), and it sags 5.7 mm at a bending stress of 18 MPa (BED-01, against the span/300 reporting guide of 7.8 mm). The engineer sets the real limit. It weighs 17.7 kg for the five, against 8.5 kg before.
- A 20 mm aluminium honeycomb deck sits at Z 1,510 to 1,530, bonded and riveted, and sealed to partition A and the walls. It runs from X -45 to 2,330, so it laps over the top edge of partition A and the 25 mm cleat on its living-area face.
- A Froli Star Mobil base sits at Z 1,530 to 1,573. The queen mattress is 1,530 (X) x 2,030 (Y) x 150 mm at Z 1,573 to 1,723, across the trailer at the back of the deck (X 800 to 2,330) and centred in Y. That leaves an 845 mm landing along partition A for climbing in.
- Allow 50 mm for bedding, to Z 1,773. That leaves 27 mm under the 1,800 mm ceiling. HyperVent in place of Froli gives 51 mm.
- The ladder stands in the living area on the kerb side (Y = -1,000) and hooks onto the deck edge at partition A. It is owner-built from aluminium SHS, about 1,580 mm long with rubber feet, so it reaches the living-area floor from the deck top (1,530 mm) at a 15 degree lean (CLR-07).
- The safety net clips on along the deck's front edge when the roof is raised.

## Partition A

Partition A is 2,330 x 1,510 mm of 20 mm honeycomb, occupying X = -20 to 0, up to the deck underside. It has no doorway: the garage is reached only through the rear door, and the gas locker only from outside. It is sealed to the floor, both walls and the deck, so the garage is sealed from the living area and the bed (GAR-02). Its 25 mm cleats are on its living-area face. The winch plates on its garage face need hardpoints.

## Loading

Under a fixed bed at 1,460 mm, you walk a bike in stooped. The baseline is a 12 V winch (product to choose, 9 kg allowance) on a quick-release plate on partition A in front of each chock, 650 mm up. It pulls the bike up the ramp and forward into its chock while you steady it, and you kneel to strap it. The bikes unload backwards down the same ramp. The alternative is a powered bed lift used with the raised roof. That costs 9 to 45 kg, and the garage then shares air with the bed.

## Garage safety (research/02, rules GAR-01 to GAR-07)

- Two low vents, one in each side wall near the front of the garage, and one high vent. Petrol vapour is heavier than air (GAR-01).
- No switches, relays, chargers, heaters or inverters in the lowest 500 mm (GAR-03). The inverter and chargers are on the living side of partition A. The winch plates are at 650 mm.
- Fireboy-Xintex fume detector sensors low in the garage, one on partition A and one by the rear door, with the display beside the bed (GAR-05).
- A 2.5 kg ABE extinguisher on the gas locker's lid, within 610 mm of the rear door (GAR-04).
- Partition A, the deck and the gas locker are sealed to the garage (GAR-02).
- No engine running inside the garage, fuel taps off and caps closed, on a placard inside the rear door (GAR-06). GAR-07 (whether people sleep with fuelled bikes aboard) stays with the operating manual.

## Checks the model must pass

| ID | Check | Limit |
|---|---|---|
| CLR-01 | Tuareg to bed beams | gap at least 40 mm |
| CLR-02 | Street Triple to bed beams | gap at least 40 mm |
| CLR-03 | Tuareg to Street Triple, anywhere | gap at least 30 mm |
| CLR-04 | Each bike to partition A, the walls, the closed rear door and everything stowed | gap at least 15 mm |
| CLR-05 | Mattress top plus 50 mm bedding | at or below Z = 1,800 |
| CLR-06 | Tuareg rear-most point to the closed rear door's inner face, owner's 2,220 mm length | gap at least 15 mm |
| CLR-06b | The same with the photo-measured 2,263 mm length (reported, not a build failure) | report the gap |
| CLR-07 | Ladder foot to the living-area floor | 0 to 10 mm |
| CLR-08 | Tuareg's panniers to the straps and track fittings (reported) | report the gap |
| CLR-09 | Each bike rolled straight back clears the rear door frame (revision D) | gap at least 15 mm |
| CLR-10 | Street Triple's kerb-side straps and fittings to the kerb-side stowage (revision D) | gap at least 15 mm |
| BED-01 | Bed beam sag (reported, span/300 guide) | report the sag |
| RES-01 | Worst strap load, report 03's cases along the trailer (revision D) | within the 1,000 kg LC |
| CON-01 | Chock bases, L-track and floor touch without overlap; beams sit on ledgers; deck sits on beams, ledgers and partition A | touching, no overlap |

## Mass

Masses come from `garage-bed/BOM.md`: 193.4 kg empty and 574.4 kg with both bikes. The module load cases are: module with the loading kit fitted and no bikes; both bikes in; bikes out with the loading kit taken out; Tuareg only; Street Triple only. In the whole trailer the loading kit stays aboard in every case, and the towball for each case is worked out in TRAILER.md.

The panniers are part of the Tuareg's envelope, so CLR-03, CLR-04, CLR-06 and CLR-09 cover them.

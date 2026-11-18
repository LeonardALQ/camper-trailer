# Garage and bed module: design v1 (baseline)

Status: concept, revision C, 18 Nov 2026. Revision B came from the first model run: the deck now laps over partition B, the ladder is owner-built to reach the floor, and the note on converting to the trailer datum is corrected. Revision C came from the whole-trailer layout in TRAILER.md: the garage floor height is fixed, the module has its place in the trailer datum, and the Tuareg keeps its panniers on in the garage. This is the baseline for the 3D model, drawings and website. Items marked OPEN need the owner's decision. Sources are the research reports in `research/` (01 tech stack, 02 design practice, 03 bike restraint and garage, 04 bed and materials, 05 bike geometry).

## Module frame

The module uses its own frame. The origin is on the garage floor surface, at the inner face of partition A, on the trailer centreline. X runs along the trailer towards partition B (the living-area side). Y runs across the trailer, positive towards the kerb (left) side, where the garage door is. Z is up from the garage floor. Units are mm. In the whole trailer (revision C, TRAILER.md) partition A faces the front utility zone and partition B the living zone at the rear, so the axes point the same way as the project datum in 02-design-practice (DIM-01: X from the ball centre, positive rearward). Module X 0 sits at datum X 3,765 and module Z 0 at datum Z 858.

## Envelope

- Interior width 2,330 mm, so Y runs from -1,165 to +1,165 (2,400 mm body with 35 mm walls).
- Garage interior length 1,800 mm, X from 0 to 1,800, between partition A (full height) and partition B (up to the deck underside).
- Ceiling with the roof collapsed at Z = 1,800 (target). The hard limit is 2,000.
- The garage floor is flat with no wheel arches. Its surface is 858 mm above the ground at design ride height (revision C). The whole-trailer model works it out from the running gear: hubs at 349 mm on the 737.7 mm tyre, 60 mm of bump travel, 50 mm clearance from the tyre at full bump to the floor underside, and a 30 mm floor panel (TRAILER.md). The 3,048 mm ramp then sits at 16.4 degrees, inside the 15 to 19 degrees the 800 to 1,000 mm range gave.

## Bikes

- Both bikes stand across the trailer, nose towards the road-side wall (Y = -1,165). They are loaded nose first through the kerb-side door, so they face the same way.
- The front tyre's leading edge is at Y = -1,115, which allows 50 mm for the chock nose. This must be measured on a real chock.
- The Tuareg's centreline is at X = 560, next to partition A. The Street Triple's centreline is at X = 1,320, next to partition B, so they are 760 mm apart.
- Why 760 mm works: the Tuareg's bar ends and handguards sit at about 1,190 to 1,215 mm, which is above the Street Triple's tank (1,007 mm) and bars (1,013 mm). The bars can overlap in plan without touching. The limit is the Street Triple's bar end (396 mm from its centreline, at 1,013 mm) against the Tuareg's side panels at the same height. The owner measured the Tuareg 585 mm wide there (revision C), a half-width of 292.5 mm, so the gap is about 71 mm against the 30 mm wanted. The crash bars sit much lower (owner), so the bar end passes over them. The width rule in `data/measurements.yaml` (TU-01) grows the spacing if a later measurement exceeds 668 mm.
- The Tuareg's mirrors fold down or come off for transport (with mirrors up it is 1,445 mm tall). Its top is then the screen, about 1,390 mm in Aprilia's image (the owner's figure is 1,370 mm). The chock cradle may lift the front wheel by up to 25 mm.
- Bike geometry comes from `research/05-bike-geometry.yaml`. The owner's overall figures govern where they differ.
- The Tuareg keeps its Mosko Moto panniers on in the garage (revision C). The owner measured it at about 970 to 980 mm wide with them. Each pannier is modelled as a 457 x 203 x 508 mm envelope from Mosko Moto's Backcountry 30L figures, outer faces 490 mm from the bike's centreline. Their position along the bike and their height are estimates. They weigh about 9 kg with their frames (estimate), carried in the trailer's mass.
- In the bike frame, x points to the bike's rear, y to the bike's left and z up, with the origin on the ground under the front axle. Placed in the module, bike x becomes module +Y, bike y becomes module +X, and bike z becomes module Z. The front axle sits at Y = -1,115 plus the front overhang (348 mm Tuareg, 300 mm Street Triple).

## Restraint (research/03)

- A Condor SC-2000 chock sits on each bike's centreline, its nose against the road-side wall.
- Two flush L-track rows run along X for the full garage length. The front row is at Y = -915 and the rear row at Y = +883.
- Each bike has a front strap pair on the front row at X = centreline ± 450 mm (Tuareg) or ± 400 mm (Street Triple). Its rear pair sits on the rear row at the same offsets, and its rear-wheel strap at centreline ± 250 mm.
- Straps are 35 mm SpanSet ratchets, LC 1,000 kg, on soft loops, with a Canyon Dancer harness on the Street Triple's bars. Every anchor and its floor fixing is designed for 20 kN.

## Bed (research/04)

- The platform covers the whole garage (1,800 x 2,330 mm) and is the sealed garage ceiling.
- Beam underside at Z = 1,460. That clears the Tuareg's screen (1,390 mm plus 25 mm chock rise) by 45 mm.
- Five RHS 50x25x2.5 6106-T6 beams stand on edge. They span 1,800 mm along X between ledgers on the two partitions, at Y = -932, -466, 0, 466 and 932.
- 40x40x3 angle ledgers run round the perimeter: on both partitions under the beam ends, and on both side walls under the deck edges.
- A 20 mm aluminium honeycomb deck sits at Z 1,510 to 1,530, bonded and riveted, and sealed to the partitions and walls. It runs from X 0 to 1,845, so it laps over the top edge of partition B and the 25 mm cleat on its living-area face, for a sealed joint (revision B; in revision A it only met that edge along a corner line).
- A Froli Star Mobil base sits at Z 1,530 to 1,573. The mattress is 1,530 (X) x 2,030 (Y) x 150 mm at Z 1,573 to 1,723, against partition A in X and centred in Y. That leaves a 270 mm landing strip on the partition B side for climbing in.
- Allow 50 mm for bedding, to Z 1,773. That leaves 27 mm under the 1,800 mm ceiling. HyperVent in place of Froli gives 51 mm.
- The ladder stands in the living area and hooks onto the platform edge at partition B. It is owner-built from aluminium SHS, about 1,580 mm long with rubber feet, so it reaches the living-area floor from the deck top (1,530 mm) at a 15 degree lean (revision B). The bought 1,500 mm ladders stop about 80 mm above the floor, and they are rated to only 100 kg.
- The safety net clips on when the roof is raised.

## Partitions and doors

- Partition A is full height, 2,330 x 1,800 mm of 20 mm honeycomb, occupying X = -20 to 0. It carries one edge of the platform.
- Partition B is 2,330 x 1,510 mm, up to the deck underside, occupying X = 1,800 to 1,820. It has a 700 x 1,300 mm doorway into the living area, closed by a sealed hinged door cut from the same panel.
- The garage door is in the kerb-side wall. The opening is about 1,720 mm wide (X 40 to 1,760) and 1,440 mm high, top-hinged. A bike cannot be moved sideways once it is inside, so one door has to span both bikes' paths. The door product and its structure belong to the body design, which comes later.

## Loading (OPEN: owner decision)

Under a fixed bed at 1,460 mm, you would have to walk a bike in stooped. The baseline is a 12 V winch (product to choose, 9 kg allowance) on a quick-release plate at the road-side wall in front of each chock. It pulls the bike in while you steady it from the ramp, and you kneel to strap it. The alternative is a powered bed lift used with the raised roof, so the bed goes up for stand-up loading. That costs 9 to 45 kg, and the garage then shares air with the bed.

## Garage safety (research/02, rules GAR-01 to GAR-07)

- Two low vents and one high vent.
- Fireboy-Xintex fume detector sensors low in the garage.
- A 2.5 kg ABE extinguisher by the garage door.
- No switches, relays or chargers in the lowest 500 mm.

## Checks the model must pass

| ID | Check | Limit |
|---|---|---|
| CLR-01 | Tuareg to bed beams | gap at least 40 mm |
| CLR-02 | Street Triple to bed beams | gap at least 40 mm |
| CLR-03 | Tuareg to Street Triple, anywhere | gap at least 30 mm |
| CLR-04 | Each bike to partitions and side walls, door closed | gap at least 15 mm |
| CLR-05 | Mattress top plus 50 mm bedding | at or below Z = 1,800 |
| CLR-06 | Tuareg rear-most point to the closed door's inner face, owner's 2,220 mm length | gap at least 15 mm |
| CLR-06b | The same with the photo-measured 2,263 mm length (reported, not a build failure) | report the gap |
| CLR-08 | Tuareg's panniers to the straps and track fittings (revision C, reported) | report the gap |
| CON-01 | Chock bases, L-track and floor touch without overlap; beams sit on ledgers; deck sits on beams | touching, no overlap |

## Mass

Masses come from `garage-bed/BOM.md`. Load cases: module with removable kit fitted and no bikes; both bikes in; bikes out with the removable kit taken out; Tuareg only; Street Triple only. The towball load for each is worked out for the whole trailer in TRAILER.md.

The panniers are part of the Tuareg's envelope, so CLR-03, CLR-04 and CLR-06 cover them.

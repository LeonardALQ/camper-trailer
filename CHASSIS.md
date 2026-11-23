# Chassis and drawbar: design (planning level)

Status: proposal, revision E of 21 Nov 2026, updated 22 Nov 2026 for the welding procedure, the welder's qualification and the welding supervisor that AS/NZS 1554.1 clause 1.7.2 asks of the SP welds (CMP-14), and the department's acceptance of the calculation, now an assumption with its fallback, and later that day for the corner steadies folded for travel on ARK's welded brackets and the holes the services make in the rails and raisers, and on 23 Nov 2026 as revision F for the 4,000 kg plate. DRAFT, not for construction until the engineer reviews it. This is the design basis report 02 asks for in LOAD-01: every load case with its factor, direction, combination and source, then the members, joints and protection, the results, and what the engineer must check. It starts from research report 11 and changes a member only where the analysis showed it fails or is oversized. The data is `data/chassis/chassis.yaml` (data revision D) with report 11's section table in `data/chassis/sections.yaml`. The geometry is `cad/chassis.py`, the analysis `cad/chassis_fea.py` and the solver `cad/frame.py`. Drawings CT-101 to CT-104 show it, and the site's Chassis page shows the current build.

## What changed in revision F, 23 Nov 2026

The trailer is plated at 4,000 kg behind the Ranger Super Duty (decision H2 as amended), so every case runs at the new plate.

- VSB1's drawbar and chain forces follow the plate: 58.9 kN along and 19.6 kN across and up and down at the coupling, 39.2 kN along and 19.6 kN up and down at each chain point. LC5a's wheel, LC8a's recovery pull and LC8b's pad follow the 3,700 kg axle group the plate allows with H2's 7.5 % on the ball: 15.1 kNm, 58.9 kN (the 78.5 kN ultimate stays) and 43.6 kN.
- The rails are RHS 150 x 50 x 4 C450L0 in place of 3 mm. At 3 mm the recovery pull reached 1.01 of yield in the rail at the XT centre crossmember. A 5 mm XT rear shock crossmember gave 0.99 and a heavier XT centre crossmember made it worse, so the rails take the load. The 4 mm rails bring LC8a to 0.84, VSB1's drawbar tests to 0.78 and the holes' net section to about 0.8, for 23.5 kg of steel.
- The coupling is a Cruisemaster DO45 Plus on four M14 8.8 bolts at 140 Nm, at the DO45's wider pattern, and LOC-07 checks the bolts and the plate. The chains are 8 mm grade 80 (T) to AS 2321 on 2,000 kg AS 2741 D shackles, as VSB1 9.2.1 asks over 3.5 t.
- The axle group sits at X 4,505.3 mm, in the middle of H17's 9.0 % to 420 kg window, so the XT stations moved 125.5 mm rearward. The diesel tank stays with its rear end at X 3,401, so its braced bay is longer, and the rear bay is 125.5 mm shorter.
- No check limit changed, and no estimate changed to pass a check.

## What changed in revision E, 21 Nov 2026

The frame now carries the home trailer of TRAILER.md revision J. Revision D, the LandCruiser 79 trailer at a 3,100 kg plate, is in the git history.

- Every case is checked at the 3,500 kg plate (decision H2), on all eight trailer cases TC1 to TC8, including the grey-full cases. VSB1's drawbar and chain forces follow the plate: 51.5 kN and 17.2 kN at the coupling, 34.3 kN and 17.2 kN at each chain point.
- The raisers, outriggers and floor crossmembers are RHS 127 x 51 x 3.5 C350L0, because RHS 125 x 50 x 3 is not a stocked size (research report 22). Each member is checked at its own grade, so the composite rail is checked at the raiser's 350 MPa.
- The grey tank fills the rear bay, so a floor crossmember crosses its middle in place of the battery bay's, and the rear bay's plan braces went. The XT rear shock crossmember is RHS 150 x 50 x 4 in place of 150 x 50 x 3, so the rear recovery pull (CHS-08A) passes without them. The tank's 2 mm guard is not counted as a shear plate, because it would buckle at about 4 kN (est.).
- The axle group sits at X 4,379.8 mm, so the XT stations moved 182.8 mm rearward.
- The rails are 1,275 mm over their outsides for the 1,655 mm track (decision H22, 21 Nov 2026), 100 mm wider than report 18's 1,175 mm, so the crossmembers, drawbar brace and plan braces are longer and the outriggers 50 mm shorter. The tanks keep their 975 mm width.
- The drawbar box is 1,480 x 320 x 720 mm for two Honda EU22i. The spare wheel sits 415 mm higher on longer posts, so it lifts off over the box.
- No check limit changed, and no estimate changed to pass a check.

Terms. A raiser is the second tube welded on top of each main rail to lift the floor above the tyres. The composite rail is the rail and its raiser welded together continuously, so they bend as one 277 mm deep section. An outrigger is a short member from the raiser out to the body edge. Utilisation is the stress divided by the case's limit. A FAT class is the IIW fatigue class of a welded detail, the stress range in MPa it survives for 2 million cycles, and the CAFL is 0.585 times it, the range below which the detail is taken to last indefinitely. SP is the structural purpose weld category of AS/NZS 1554.1.

## Material, welding and protection

- Tube: the rails, full-height crossmembers, drawbar and braces are AS/NZS 1163 C450L0, bought as Austube Mills C450PLUS (fy 450 MPa). The raisers, outriggers and floor crossmembers are C350L0 (fy 350 MPa). Each grade goes on the mill certificate.
- Plate: AS/NZS 3678 grade 350, checked at fy 350 MPa and fu 450 MPa up to 20 mm (assumption: over 12 mm it is 340 MPa, about 3 % less margin than shown).
- Welding: every structural weld SP to AS/NZS 1554.1 with E49XX or W50X consumables. The rail-to-raiser and drawbar-to-rail seams are continuous. No weld runs across the width of a rail (Cruisemaster TB 070). Inspection follows report 02 WLD-03. Clause 1.7.2 has every weld made to a qualified welding procedure, by a welder qualified for it and under a welding supervisor, so Leonard welds to a procedure qualified on his own test piece, which qualifies him too, and a qualified welding supervisor and inspector checks the fit-up and inspects the finished welds, the WLD-03 joints by penetrant, before galvanising (TRAILER.md, CMP-14).
- Protection: hot-dip galvanised after fabrication to AS/NZS 4680, vented and drained to report 02 WLD-05. The coupling plate's faces are cleaned flat after dipping.

## Members

A ladder of two composite rails with crossmembers at eight stations, outriggers at every station, an A-frame drawbar that runs on under the rails, and plan bracing in the two front bays. Stations are given by the front face of their crossmember.

| Member | Section | Where | Qty | Mass |
|---|---|---|---|---|
| Main rails | RHS 150 x 50 x 4 C450L0 | X 1,820 to 6,240, 1,275 mm over their outsides (H22), Z 597.5 to 747.5 | 2 | 102.6 kg |
| Raisers | RHS 127 x 51 x 3.5 C350L0, continuous fillets | On each rail, Z 747.5 to 874.5, with a 20.5 mm bearer strip up to the floor at Z 895 | 2 | 80.2 kg |
| Body end crossmembers | RHS 150 x 50 x 3, full height, 1,175 mm | X 1,820 and 6,190 | 2 | 21.0 kg |
| XT crossmembers | RHS 150 x 50 x 3, full height, no holes | Front hinge X 3,586, centre X 4,486 | 2 | 21.0 kg |
| XT rear shock crossmember | RHS 150 x 50 x 4, with a 5 mm shock plate | X 5,316 | 1 | 13.6 kg |
| Floor crossmembers | RHS 127 x 51 x 3.5, top flush with the raisers | X 2,360, the diesel bay at X 2,901 and the grey bay at X 5,733 | 3 | 32.1 kg |
| Outriggers | RHS 127 x 51 x 3.5, top flush, 562 mm out to the body edge | Every station, each side | 16 | 81.6 kg |
| Plan bracing | SHS 40 x 40 x 2.5, an X at rail height | Bays X 2,360 to 2,901 and 2,901 to 3,586 | 4 | 14.8 kg |
| Drawbar members | RHS 150 x 50 x 5 | Apex X 250 at Y ±60, to the rails at X 1,820, then 1,000 mm on under them | 2 (4 lengths) | 75.6 kg |
| Drawbar cross brace | RHS 75 x 50 x 3 | X 900 | 1 | 2.9 kg |
| Spare carrier posts | SHS 50 x 50 x 2.5 | X 1,795, Y ±120, up to Z 1,915 | 2 | 9.4 kg |

CT-101 and CT-102 carry the member and plate lists, and the site's Downloads page offers the cut list as `chassis-cut-list.csv`.

### Changes from report 11, and why

1. Outriggers RHS 127 x 51 x 3.5 in place of 75 x 50 x 3, with 6 mm fillets all round. With 75 x 50 x 3 the frequent fatigue range at the root weld was 34.7 MPa against the FAT 36 root's CAFL of 21.1 MPa (IIW 414). Now it is 17.0 MPa at the 4,000 kg plate (FAT-05).
2. Plan bracing in the two bays ahead of the axles. With no bracing, a recovery pull 30 degrees off the rail axis (LC8a) bent the ladder sideways in a Vierendeel shape. The tanks fill the bays behind, so the thicker XT rear shock crossmember takes the rear pull.
3. Jacking pads on the XT centre crossmember beside the rail, not on the rail's bottom face, so the pad's weld end (IIW 513, FAT 71) sees 20.7 MPa against a CAFL of 41.5 MPa (FAT-11).
4. The weld toes on the rail at the full-height crossmembers are burr-ground (IIW 512, a CAFL of 60.8 MPa). They see 19.0 MPa (FAT-01).
5. 6 mm fillets round the ends of the XT crossmembers. The root (IIW 414) sees 16.5 MPa against 21.1 MPa (FAT-03).
6. Raisers RHS 127 x 51 x 3.5 in place of 100 x 50 x 3, to lift the floor above the 805 mm tyre with 50 mm in hand at full bump.
7. A fixed station at the diesel bay, so the heater's tank sits between two crossmembers, and one at the grey bay over the grey tank.
8. The jacking pads, recovery lugs and chain lugs keep report 11's sizes. The front recovery lugs are 20 mm plate, because a 30 degree pull bends them out of their plane.

## Joints

| Joint | Weld | Fatigue detail |
|---|---|---|
| Raiser to rail | Continuous 4 mm fillets along both edges, vented at each end of each bay | IIW 323, FAT 90 |
| Full-height crossmember to rail | 6 mm (XT) or 5 mm (body ends) fillet all round each end, toe on the rail ground | IIW 512 ground, 413 (FAT 63), root 414 (FAT 36) |
| Raiser-height crossmember to raiser | 5 mm fillet all round | IIW 512 (FAT 80), 413, 414 |
| Outrigger to raiser | 6 mm fillet all round | IIW 413 (FAT 63), root 414 (FAT 36) |
| Drawbar member under the rail | Continuous 5 mm fillets, a profiled root gusset with a 160 mm ground radius at the body front, a 1:2 snipe over 300 mm at X 2,820 with its toe ground | IIW 526 (FAT 90) at the root, 712 (FAT 56) at the end |
| Drawbar A-frame to its overlap part | Mitred full penetration butt weld, ground flush | IIW 526 |
| Cross brace to the drawbar members | 5 mm fillet all round | IIW 413 |
| Chain lugs, recovery lugs and tongues | 6 mm fillets along their length only | IIW 513 |
| ARK's corner steady brackets under the rails | 5 mm fillets along the rail's two bottom corners only, none across the rail (TB 070), welded before galvanising | IIW 513 (FAT 71), FAT-16 |
| Body mount nut plates, coupling plate | Fillets all round | Not frame details. BODY.md checks the mounts. The DO45 bolts to its plate, and LOC-07 checks the bolts and the plate |
| Cruisemaster's hinge, airbag and shock brackets | Cruisemaster's drawing 33XT AIR | Hot-spot classes, IIW Table 3.3-1 |

## Fittings and bought parts

| Item | Basis | Mass |
|---|---|---|
| Cruisemaster DO45 Plus with its handbrake, under a 12 mm plate at the apex on four M14 8.8 bolts at 140 Nm. Its 32 mm tow pin stays on the truck | DO45 Plus guide | 13.5 kg (est.) |
| Chain lugs, 10 mm, at X 400, and 8 mm grade 80 (T) chains to AS 2321 on 2,000 kg AS 2741 D shackles, never welded | VSB1 9.2, ADR 62/02 14.3 | 1.9 kg and 3.2 kg (est.) |
| ARK XO750 jockey wheel on an 8 mm bracket at X 1,000, swung up along the drawbar for travel | Report 11 section 6.4 | 20.0 kg (maker) |
| Stone guard on the cross brace, trimmed on the kerb side round the jockey wheel | Report 11 section 6.4 | 6.5 kg (calculated) |
| Breakaway kit | VSB1 8 | 5.0 kg (est.) |
| Front recovery lugs, 20 mm, at X 2,150, and rear tongues, 20 mm, through the rear crossmember at X 6,170 | LC8a | 7.5 kg and 9.8 kg |
| Jacking pads, 100 x 100 x 10 with a locating cup, on the XT centre crossmember | LC8b | 1.6 kg |
| Four ARK XO DDS650 corner steadies (875 kg) on ARK's chassis mount brackets welded under the rails, the front pair at X 3,000 folded inboard for travel and the rear pair at X 6,070 folded forward, their undersides 422.5 mm up (est.) | ARK's XO fitting guide, LC5b, LOC-06, FAT-16 | 35.2 kg with the brackets (retailer) |
| Four lashing points, forged 1/2 in weld-on D-rings with their clips (4,000 lb working load limit), under the outrigger ends at X 1,845 and 6,215, welded before galvanising | STB-05 | 1.8 kg (est.) |
| 32 body mount nut plates, 10 mm, M12 tapped | BODY.md | 8.8 kg |
| Spare carrier cleats and hub plate | LC2, LC7 | 4.2 kg |
| Floor bearer strip, HDPE with an EPDM face | Report 11 section 2 | 22.9 kg (est.) |
| Galvanising, 33.3 m² inside and out at AS/NZS 4680's minimum coating masses | Report 11 section 1.4 | 15.3 kg (calculated) |

### The corner steadies

ARK's XO fitting guide (RTC614 manual, V1 1/21) has each steady folded flat along the chassis for travel, at 0 degrees, locked at 30 and 60 degrees as a steady only, and at 90 degrees, its rated 875 kg and its only jacking position. Each comes with a chassis mount bracket, 117 x 72.5 x 35 mm, that ARK welds to the chassis, and the steady bolts into it with two 8 mm bolts at 78 mm centres. The design welds that bracket under the rail along the rail's two bottom corners before galvanising, with no weld across the rail (TB 070). It replaces the design's own bolted 6 mm plate, which only doubled ARK's bracket and needed bolt holes through each rail. FAT-16 checks the bracket as a longitudinal attachment on the rail's bottom flange (IIW 513, FAT 71), and LOC-06 its welds and the rail's webs under the steady's rating, at 7 % of their limits.

Folded, a steady is about 600 mm long, 72.5 mm wide and 175 mm deep under the rail (est., inside its share of the pair's 610 x 255 x 178 mm carton). Along the rail at X 3,000 it would fit in neither direction with room to spare, because the 638 mm between the drawbar overlap's end at X 2,820 and the XT front hinge crossmember at X 3,458 leaves 19 mm at each end. So the front pair's brackets lie across the rails and the steadies fold inboard under the diesel bay, where nothing hangs below the rails. Their feet end 142 mm apart either side of the centreline, 55 mm under the plan braces, 144 mm behind the drawbar overlap and 422 mm ahead of the hinge crossmember. The rear pair at X 6,070 folds forward along the rails, its brackets 31 mm outboard of the rail centreline, so it keeps 20 mm from the grey tank guard's hangers on the rails' inner faces, 25 mm from the rear recovery tongues, 62 mm from the rear crossmember and 57 mm from the grey tank's dump line at X 5,450. Folded, every steady's underside is 422.5 mm up (est.), above the coupling's 380 mm, so DIM-04 and DIM-06 read the coupling and DIM-07's breakover is 17.4 degrees, at the swung-up jockey wheel. `cad/tests/test_chassis.py` holds each folded steady 20 mm (est.) from every other rigid part and keeps the box its leg sweeps down to 90 degrees clear.

At 90 degrees each steady stands under its bracket, the jacking station that LC5b and the body's LC5b load use. Wound in, its 19 in bracket height leaves the foot 115 mm off the ground at design ride height, and at full extension, 25 in, the leg reaches the ground with 37.5 mm of its 152 mm stroke left (etrailer's listing of the 25 in XO). That steadies the parked trailer and takes a corner's load, but it does not lift a wheel clear of the ground on the XT arms' 60 mm of droop, so a tyre change uses the jacking pads (CHS-08B, LOC-04). Each rear steady stands 31 mm further out than a front one, so in LC5b's twist couple it takes 95 % of a front steady's 875 kg and the couple balances. The chassis model shows the steadies both ways, folded and, see-through, at 90 degrees.

## Mass

The chassis and drawbar weigh 507.7 kg of steel and 15.9 kg of zinc, 524 kg galvanised, plus 108.2 kg of bought parts and fittings: 632 kg in all. The 4 mm rails add 23.5 kg of steel. The steel and zinc are calculated (7 % growth). The C350L0 sections, 21.4 m of them, are 28 kg heavier than the 125 x 50 x 3 they replace (9.07 against 7.78 kg/m).

## Design basis (report 02 LOAD-01)

Every case runs on the eight trailer cases TC1 to TC8, with the water, fuel and gear each one carries, scaled by one factor so the heaviest, TC2, sits at the 4,000 kg plate (1.223). That keeps each case's balance while designing at the plate, as report 11 asks. LC5b runs at tare.

| Case | Load | Direction and combination | Factor or criterion | Source |
|---|---|---|---|---|
| LC1 | Static, 1 g | Down | Stress ≤ fy / 3. Rail between the drawbar root and the front hub ≤ span / 500, rear overhang tip ≤ overhang / 300, outrigger tip ≤ 2 mm | ARTSA factor of 3 (report 02), limits proposed in report 11 |
| LC2 | Vertical bump, 3 g on the structure, 4 g on local fixings | Down | Stress < fy | Report 11, ARTSA |
| LC3 | Braking, 0.8 g forward with 1 g down, braked at the tyres | Together | Stress ≤ fy / 1.5 | Report 02 |
| LC4 | Cornering, 0.5 g sideways each way with 1 g down | Together, both ways | Stress ≤ fy / 1.5 | Report 02 |
| LC5a | Twist, one wheel in a hole: 15.1 kNm between the axles with 1 g down | Together, both diagonals | Stress ≤ fy / 1.5, twist between the front hinge and rear shock crossmembers ≤ 0.5 degree | Report 11 at the 4,000 kg plate: 925 kg, a quarter of the 3,700 kg axle group, x 9.81 x 0.831 m = 7.54 kNm, times 2 |
| LC5b | Twist at tare, one corner steady wound to 875 kg | With 1 g down | Stress ≤ fy / 1.5 | Report 11, ARK |
| LC6 | Drawbar, VSB1 9.1 at the 4,000 kg plate: 58.9 kN along, 19.6 kN across, 19.6 kN up and down at the coupling | Each separately, each way | Stress < fy | VSB1 9.1 and 14, ADR 62/02 14.2 |
| LC6b | Chain points, VSB1 9.2.2 at the plate: 39.2 kN along, 19.6 kN up and down | Each lug separately | Stress < fy | VSB1 9.2.2, ADR 62/02 14.4.2 |
| LC7 | Cargo fixings: 0.8 g forward, 0.5 g rearward, 0.5 g sideways, 0.2 g up, each times 2 off road | Separately | Fixing forces for the body design, fy / 1.5 | NTC guide via report 02 |
| LC8a | Recovery: 58.9 kN, 1.5 times the plate's weight, at each front and rear point within 30 degrees sideways and 15 degrees up or down, 78.5 kN ultimate | Separately, nine directions each | No yield at 58.9 kN, no fracture at 78.5 kN | Report 11 |
| LC8b | Jacking one side at its pad, gravity times 2, at least 43.6 kN on the pad, 60 % of the plate's 3,700 kg axle group times 2 | Down | Stress < fy, no crushing | Report 11 |
| LC10 | Fatigue: frequent ±0.5 g beyond 10 million cycles, occasional ±1.5 g for 100,000 cycles | Down | Frequent range ≤ CAFL, Miner damage of the occasional range ≤ 0.5 | Report 11 section 3.4, IIW-1823-07 |

## Analysis

The frame is a 3D beam model on the members' centroid axes, solved by the direct stiffness method in `cad/frame.py`, with 237 nodes, 203 beam elements and 60 rigid links. `cad/tests/test_frame.py` checks the solver against closed forms: cantilevers in bending and torsion, a simply supported beam and the equilibrium of a 3D portal frame.

- The composite rail is one beam with the combined section: centroid at Z 733, I = 18.4 x 10⁶ mm⁴, Z = 135.5 x 10³ mm³ at the bottom and 130.1 x 10³ mm³ at the top, with the 4 mm rail. `cad/tests/test_chassis.py` pins it.
- Crossmembers, outriggers, braces and the drawbar members are beams on their own axes, joined to the rail through rigid links, so every joint is rigid. The drawbar's overlap is linked to the rail at every node along its 1,000 mm.
- The coupling is a ball joint. Each XT arm is a free body: its tyre force, its weight and the airbag force balance about the hinge pivot, 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside.

Each mass goes onto the frame by its load path, with its resultant and the moment of its offset kept: the floor spans onto the raisers by the lever rule, the roof goes down the side walls to the outriggers, the tanks, battery box and guards hang between the rails, the spare goes to its posts, and the drawbar box to the drawbar members. Block items are cut into 200 mm cells. The ball and the four wheels react each case by statics, and six supports stop only rigid-body motion, with reactions below 1 N. In LC6, LC6b and LC8a the frame is held at its hinge pivots and airbag brackets, as VSB1 14 holds the body during the test. Stress at each element end combines as √(σ² + 3τ²).

## Results

| Case | Governing member | Where and when | Stress | Limit | Utilisation |
|---|---|---|---|---|---|
| LC1 | Road-side drawbar member | At the body front, TC2 | 51 MPa | 150 MPa | 0.34 |
| LC2 | Road-side drawbar member | At the body front, TC2 | 153 MPa | 450 MPa | 0.34 |
| LC3 | Kerb-side drawbar member | At the body front, TC2 | 187 MPa | 300 MPa | 0.62 |
| LC4 | XT centre crossmember | Its kerb end, X 4,511, TC2 cornering towards the kerb side | 127 MPa | 300 MPa | 0.42 |
| LC5a | Road-side rail | X 4,054, TC7, diagonal A | 66 MPa | 233 MPa | 0.28 |
| LC5b | Road-side rail | X 3,000, at tare, one steady wound to 875 kg | 102 MPa | 233 MPa | 0.44 |
| LC6 | Kerb-side rail | X 3,611, 19.6 kN up at the coupling | 272 MPa | 350 MPa | 0.78 |
| LC6b | Kerb-side rail | X 3,611, kerb-side lug, 19.6 kN down | 265 MPa | 350 MPa | 0.76 |
| LC8a | Road-side rail | X 4,511, the rear road-side point pulled 30 degrees sideways and 15 degrees down | 294 MPa | 350 MPa | 0.84 |
| LC8b | Road-side rail | X 4,511, TC7, road side jacked | 106 MPa | 350 MPa | 0.30 |

The rear recovery pull governs, then VSB1's drawbar tests. The rails' checks use the raiser's 350 MPa, which is where the margin went.

Deflection and twist (LC1, at the plate): the rail between the drawbar root and the front hub deflects 0.18 mm against 4.5 mm, the rear overhang tip 0.93 mm against 5.8 mm, and the worst outrigger tip 0.43 mm against 2.0 mm. Under LC5a the frame twists 0.401 degree against 0.5 degree, a 20 % margin.

Fittings: the chain lugs reach 47 % of their limit (bearing), the front recovery lugs 73 % (plate bending at 78.5 kN), the rear tongues 62 %, the jacking pads 41 % under 43.9 kN, the spare carrier posts 16 %, the corner steady brackets 7 % (LOC-06), and the coupling plate's four M14 bolts 48 % in shear and tension together under the 58.9 kN pull on its 70 mm lever (LOC-07). The tyre swung through its travel comes 53.5 mm from the kerb-side raiser at its closest, against 50 mm (FIT-05).

### Fatigue (LC10)

Every detail passes its frequent check at the 4,000 kg plate, and the largest Miner damage from the occasional case is 0.24, at the drawbar root (FAT-07). The tightest is the drawbar root's profiled gusset (FAT-07, 50.3 MPa against a CAFL of 52.6 MPa, 0.96), whose range follows the towball, then FAT-05 at the outrigger roots (17.0 against 21.1 MPa) and FAT-03 at the XT crossmember roots (16.5 against 21.1 MPa). CT-103 and the Chassis page list every detail.

The hollow-section T-joints are marked HS: the crossmember-to-rail joints, the outrigger roots, the cross brace and the brackets on the rail. Their nominal stress understates the stress at the weld toe, often by a factor of two to four, so the engineer checks them by the hot-spot method or CIDECT design guide 8.

## Holes in the members

The services' runs pass through the rails and raisers in 18 places (data/services.yaml `holes`, review I2-27). Counted once, an outrigger's root face is the raiser's outer web, so they make 14 holes in the steel. The two at the outriggers' open tips pass through the side markers' caps, not through steel. Each hole is the run's diameter and a 6 mm bush across (est.), a slot along the member where the run crosses the wall on a slant.

CHS-09 takes each hole out of the composite rail's section and checks the combined stress at the hole's edge in every case from LC1 to LC8b against that case's limit, the raiser's fy over its factor. AS 4100 clause 7.2's 0.85 fu on the net area is higher for both grades, so yield governs. Every hole passes, the worst H-01 at 279 MPa against 350 MPa in the rear recovery pull, 0.80.

CHS-10 says where a hole may go and checks its fatigue, with three rules. Its centre stays at least 1.25 d from the end of its face's flat, where the tube's corner radius starts, and 1.5 d from the member's sawn end (AS 4100 Table 9.6.2, a rolled and a sawn edge). Its edge stays at least one diameter from every weld toe, and the larger diameter from the next hole, where Kirsch's solution for a hole in a plate leaves the hole's own stress field within 8 % of the nominal stress, so the hole adds nothing to the welds' FAT checks. The frequent range at its edge, Kirsch's 3.0 times the net section's, stays within the 81.9 MPa CAFL of IIW no. 121, a machined edge dressed, FAT 140. A drilled or hole-sawn hole with its burrs taken off is that detail, and IIW's note on it asks that the edge's shape be counted, which the 3.0 does.

| Hole | Run | Wall, at X | Size, mm | Net section, worst case | Edge to the flat's end, need | Clear to a weld toe or hole, need | Range at the edge | CHS-10 |
|---|---|---|---|---|---|---|---|---|
| H-01 | K-08 | Kerb raiser's outer web inside OR-05K's root weld, 4,511 | 16 | 279 of 350 MPa, LC8a | 39.8, 20 | 17.5, 16 | 38.7 of 81.9 MPa | meets |
| H-03 | K-09 | Road raiser's outer web inside OR-05R's root weld, 4,511 | 16 | 269 of 350 MPa, LC8a | 54.8, 20 | 17.5, 16 | 40.5 of 81.9 MPa | meets |
| H-05 | K-01 | Road rail's outer web, 2,360 | 16 x 39 slot | 67 of 233 MPa, LC5b | 63.5, 20 | 23.2, 16, H-06 | 20.5 of 81.9 MPa | meets |
| H-06 | K-10 | Road rail's outer web, 2,415 | 16 x 34 slot | 108 of 350 MPa, LC6 | 33.5, 20 | 23.2, 16, H-05 | 24.7 of 81.9 MPa | meets |
| H-07 | K-10 | Road rail's outer web, 4,215 | 16 x 25 slot | 113 of 350 MPa, LC8a | 44.5, 20 | 83.5, 16 | 43.1 of 81.9 MPa | meets |
| H-08 | K-01 | Road rail's outer web, 6,021 | 16 x 25 slot | 137 of 350 MPa, LC8a | 57.5, 20 | 48.9, 16 | 4.3 of 81.9 MPa | meets |
| H-09 | B-18 | Kerb raiser's inner web, 2,015 | 14 x 54 slot | 93 of 350 MPa, LC6 | 25.8, 17.5 | 81.5, 14 | 35.4 of 81.9 MPa | meets |
| H-10 | B-16 | Kerb raiser's inner web, 2,267 | 28 x 103 slot | 88 of 350 MPa, LC6 | 39.8, 35 | 30.5, 28 | 32.4 of 81.9 MPa | meets |
| H-11 | D-14 | Kerb raiser's outer web, 2,291 | 24 x 74 slot | 110 of 350 MPa, LC6 | 43.8, 30 | 24.4, 24, nut plate | 26.0 of 81.9 MPa | meets |
| H-12 | D-14 | Kerb raiser's inner web, 4,669 | 24 x 58 slot | 186 of 350 MPa, LC8a | 49.8, 30 | 42.5, 24 | 37.5 of 81.9 MPa | meets |
| H-13 | B-16 | Kerb raiser's inner web, 4,840 | 28 x 66 slot | 185 of 350 MPa, LC8a | 43.8, 35 | 32.5, 28, airbag bracket | 35.9 of 81.9 MPa | meets |
| H-14 | B-18 | Kerb raiser's inner web, 4,952 | 14 x 31 slot | 181 of 350 MPa, LC8a | 25.8, 17.5 | 66.3, 28, H-13 | 62.2 of 81.9 MPa | meets |
| H-15 | K-08 | Kerb raiser's inner web, 5,996 | 16 x 23 slot | 144 of 350 MPa, LC8a | 39.8, 20 | 66.5, 16 | 3.1 of 81.9 MPa | meets |
| H-16 | K-09 | Road raiser's inner web, 5,988 | 16 x 33 slot | 91 of 350 MPa, LC8a | 54.8, 20 | 51.5, 16 | 10.9 of 81.9 MPa | meets |

All 14 meet every rule. The services moved twelve of them off the rails' and raisers' 50 mm faces and the welds:

- K-08 and K-09 rise inboard of the rails behind the grey tank, enter the raisers through their inner webs at 78 and 64 mm above the seam (H-15, H-16), and run forward inside them in the inboard lane, K-08 between D-14 and B-18. At the XT centre station each turns square across its raiser into OR-05 through a round 16 mm hole on the outrigger's centre line, tied to it, its edge 17.5 mm from the root weld's toes either side (H-01, H-03). A lamp cable bends at 57 mm, so only a turn that starts in the inboard lane meets the outer web square.
- K-10 leaves the road rail through its outer web at Z 652 beside X 4,215, where the range at its edge is 43.1 MPa, and drops outside the rail to pass under it to the TSC (H-07, was the rail's bottom face).
- K-01 leaves the road rail through its outer web at Z 680 beside X 6,021, ahead of the rear steady's swing, and drops behind it (H-08, was the rail's bottom face 14 mm from K-09's hole).
- B-16 leaves the kerb raiser at Z 796, 30.5 mm from the seam's fillet, under D-14, which rides 16 mm higher from X 2,560 forward (H-10).
- B-18, B-16 and D-14 leave G20's outboard row and come down into the 79.5 mm between the kerb raiser and the rear tank's 20 mm. They run forward against the raiser and enter it on slants through its inner web, B-18 at Z 840, B-16 at Z 800 and D-14 at Z 806, after it runs at Z 760 for its 110 mm bend (H-12 to H-14, were the raiser's top face). G20 became one packing space over the gap with the chase's loom inboard of the three, so they add no hole and no frame. A frame outboard of the raiser would sit within FIT-05's 50 mm of the rear tyre at full travel and in its spray, and a reinforced opening in the top face would put its collar's welds across the composite rail's top flange (TB 070).

## What the engineer must check

1. The load cases, the factor of 2 on twist, the ±0.5 g frequent fatigue case and the deflection and twist limits (report 11 open question 6).
2. The hot-spot stresses at every HS detail, above all the outrigger roots (FAT-04, FAT-05), the XT crossmember roots (FAT-03) and the crossmember toes on the rail (FAT-01).
3. VSB1 9.1 and 9.2.2 evidence at the 4,000 kg plate, by test or by calculation the department accepts. The recovery case reaches 0.84 of yield in the road-side rail. The plan assumes the department accepts this calculation, which covers strength and fatigue, as VSB1 9.1's approved calculation for the concessional entry. If it does not, the drawbar and chain points are tested at an approved facility to VSB1 chapter 14, about AUD 5,000 (est.).
4. The rear bays without plan bracing: the RHS 150 x 50 x 4 XT rear shock crossmember carries the rear recovery pull.
5. The local stability of the 4 mm rail walls at the jacking pad and under the hinge brackets, which a beam model does not see, and the plan bracing's gussets.
6. SP to AS/NZS 1554.1 for every weld, or AS/NZS 1554.5 for the most fatigue-loaded joints, and the C350L0 and C450L0 grades on the mill certificates.
7. The floor panel spanning from the raiser to the body edge between outriggers at most 900 mm apart, with no edge member (BODY.md, BDY-04).
8. ARK's corner steady brackets welded under the rails along the rails' bottom corners only (FAT-16, LOC-06), and the steadies' jacking loads through them into the rails' 4 mm webs.
9. The holes the services make in the rails and raisers (CHS-09, CHS-10), above all the two in the raisers' outer webs inside OR-05's root welds (H-01, H-03), which the hot-spot check of that joint must count.
10. The coupling plate and the DO45 Plus's four M14 8.8 bolts (LOC-07), with the bolt rows' pitch and the pin's lever read from the coupling itself, and the drawbar root's fatigue at the plate (FAT-07, 0.96 of its CAFL).

## Assumptions made for the design

- The XT arm pivot is 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, scaled from Cruisemaster's drawing (±10 mm).
- Raiser-level outriggers at the XT stations are acceptable to Cruisemaster, against its note that outriggers be full rail height.
- RHS 150 x 50 x 3 XT crossmembers, and 150 x 50 x 4 at the rear shocks, suit the 4,500 kg XT Air build in its load-sharing tandem configuration at 900 mm axle spacing.
- The DO45 Plus under-mounted on its plate puts the coupling point at Z 440, the ute's laden ball height. Its bolt rows are 100 mm apart and its pin's centre 70 mm below the plate (est., LOC-07).
- A galvanising bath takes a frame 6.3 m long and 2.4 m wide across the outriggers.
- The department accepts the engineer's calculation, which covers strength and fatigue, as VSB1 9.1's approved calculation for the concessional entry. If not, the chapter 14 drawbar and chain-point test at an approved facility, about AUD 5,000 (est.), takes its place.
- The welds reach SP quality because they are made to the qualified procedure by Leonard, qualified on it, under the supervisor's visits, and pass the inspector's visual and penetrant inspection (CMP-14).
- A folded ARK XO DDS650 is about 600 mm long, 72.5 mm wide and 175 mm deep under the rail, within its share of the pair's carton, and its 19 in and 25 in bracket heights at 90 degrees are etrailer's for the 25 in XO.
- Every hole in a member is drilled or hole-sawn, its burrs taken off, and is the run's diameter and a 6 mm bush across.

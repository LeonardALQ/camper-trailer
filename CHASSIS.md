# Chassis and drawbar: design (planning level)

Status: proposal, revision D, 20 Nov 2026. DRAFT, not for construction until the engineer reviews it. This document is the design basis report 02 asks for in LOAD-01: every load case with its factor, direction, combination and source, then the members, joints and protection, the results, and what the engineer must check. The design starts from research report 11 (`research/11-chassis-design.md`) and changes a member only where the analysis showed it fails or is oversized. The data is `data/chassis/chassis.yaml` (data revision B) with report 11's section table in `data/chassis/sections.yaml`, the geometry is `cad/chassis.py`, the analysis `cad/chassis_fea.py` and the solver `cad/frame.py`. Drawings CT-101 (general arrangement), CT-102 (drawbar and coupling) and CT-103 (details) show it. The results below are from this revision's build. The site's Chassis page always shows the current build.

## What changed in revision D, 20 Nov 2026

The frame now carries the LandCruiser 79 trailer of TRAILER.md revision H: a 4,420 mm body with no garage, plated at 3,100 kg ATM.

- The rails are 4,420 mm long, X 1,820 to 6,240 mm, and 1,175 mm wide over their outsides for the 1,555 mm track on the ute's ET 0 wheel. They were 5,500 mm long and 1,286 mm wide.
- The raisers are RHS 125 x 50 x 3 in place of 100 x 50 x 3, because the ute's 805 mm tyre lifts the floor to Z 925 mm. The composite rail is now 275 mm deep.
- The outriggers grew from RHS 100 x 50 x 3 to 125 x 50 x 3, the raiser's section. With the 100 mm section the outrigger root's weld (FAT-05) saw a frequent range of 23.5 MPa against its CAFL of 21.1 MPa. With 125 mm it sees 16.8 MPa.
- Eight stations in place of nine. A fixed station now closes the heater's diesel tank bay, because the generated station spacing put a crossmember 50 mm into the tank (FIT-03).
- The XT Air axles are 900 mm apart, on Cruisemaster LC5 hubs.
- VSB1's drawbar and chain forces follow the 3,100 kg plate: 45.6 kN and 15.2 kN at the coupling (LC6), and 30.4 kN and 15.2 kN at each chain point (LC6b). Every case is scaled to the plate in place of 3,500 kg.
- The drawbar carries the sealed drawbar box with the generator and the jerry cans. The jockey wheel moves to X 1,000 mm.
- The corner steadies sit at X 2,220 and 6,070 mm, about 400 mm inside the body ends.
- The body bolts to the raisers with 32 M12 bolts into welded 10 mm nut plates (CH-P14), BODY.md revision B.
- No check limit changed, and no estimate changed to pass a check.

Revisions B and C followed TRAILER.md revisions F and G: the published tyre diameter, and report 13's equipment. They are in the git history.

Terms. A raiser is the second tube welded on top of each main rail to lift the floor above the tyres. The composite rail is the rail and its raiser welded together continuously, so they bend as one 275 mm deep section. An outrigger is a short member from the raiser out to the body edge. Utilisation is the stress divided by the case's limit, so 1.00 is at the limit. A FAT class is the IIW fatigue class of a welded detail, the stress range in MPa it survives for 2 million cycles, and the CAFL is 0.585 times it, the range below which the detail is taken to last indefinitely. SP is the structural purpose weld category of AS/NZS 1554.1.

Positions are in the project datum DIM-01: X rearward from the ball centre, Y positive to the road side, Z up from the ground at design ride height, all in mm.

## Material, welding and protection

- Tube: AS/NZS 1163 grade C450L0 RHS and SHS, bought as Austube Mills C450PLUS black tube (fy 450 MPa, fu 500 MPa). Section properties are report 11's, checked against Austube's design capacity tables. The weak-axis modulus is the AS 4100 effective one where the section is slender in that axis.
- Plate: AS/NZS 3678 grade 350. The checks use fy 350 MPa and fu 450 MPa for every thickness up to 20 mm (assumption: grade 350 plate over 12 mm is 340 MPa, so the 20 mm parts have about 3 % less margin than shown).
- Welding: every structural weld SP to AS/NZS 1554.1 with E49XX or W50X consumables. The rail-to-raiser seams and the drawbar-to-rail seams are continuous fillets. No weld runs across the width of a rail (Cruisemaster TB 070). Inspection follows report 02 WLD-03.
- Protection: the whole welded frame is hot-dip galvanised after fabrication to AS/NZS 4680, vented and drained to report 02 WLD-05. The coupling plate faces are cleaned flat after dipping.

## Members

The frame is a ladder of two composite rails with crossmembers at eight stations, outriggers at every station, an A-frame drawbar that runs on under the rails, and three bays of plan bracing.

| Member | Section | Where | Qty | Mass |
|---|---|---|---|---|
| Main rails | RHS 150 x 50 x 3 | X 1,820 to 6,240, centres 562.5 mm from the centreline (1,175 mm outer width), Z 597.5 to 747.5 | 2 | 79.1 kg |
| Raisers | RHS 125 x 50 x 3, continuous fillets to the rail | On each rail, Z 747.5 to 872.5, with a 22.5 mm bearer strip up to the floor underside at Z 895 | 2 | 68.8 kg |
| Body end crossmembers | RHS 150 x 50 x 3, full rail height | Body front (centre X 1,845) and rear (X 6,215) | 2 | 19.2 kg |
| XT crossmembers | RHS 150 x 50 x 3, full rail height, no holes | Front hinge (X 3,306), centre (X 4,206), rear shock (X 5,036, with a 5 mm shock plate) | 3 | 28.9 kg |
| Floor crossmembers | RHS 125 x 50 x 3 at raiser height, top flush with the raisers | X 2,295, the diesel bay at X 2,746, and the battery bay at X 5,470 | 3 | 25.1 kg |
| Outriggers | RHS 125 x 50 x 3 at raiser height, top flush, 612.5 mm to the body edge | At all eight stations, each side | 16 | 76.2 kg |
| Plan bracing | SHS 40 x 40 x 2.5, an X of two diagonals at rail height | Bays X 2,295 to 2,746, 2,746 to 3,306, and 5,036 to 5,470 | 6 | 19.6 kg |
| Drawbar members | RHS 150 x 50 x 5 | Apex X 250 at Y ±60, to the rail centres at X 1,820, then 1,000 mm on under the rails to X 2,820 | 2 (4 lengths) | 75.2 kg |
| Drawbar cross brace | RHS 75 x 50 x 3 at the members' mid-depth | X 900 | 1 | 2.6 kg |
| Spare carrier posts | SHS 50 x 50 x 2.5, bolted to cleats on the front crossmember | X 1,795, Y ±120, up to Z 1,500 | 2 | 6.5 kg |

The member schedule and the plate list with sizes are on CT-101 and CT-102, and the site's downloads page offers the cut list as `chassis-cut-list.csv`.

### Changes from report 11, and why

1. Outriggers RHS 125 x 50 x 3 in place of 75 x 50 x 3, with 6 mm fillets all round. With 75 x 50 x 3 the frequent fatigue range at the root weld was 34.7 MPa against the FAT 36 root's CAFL of 21.1 MPa (IIW 414). Revision A went to 100 x 50 x 3. On the 79 trailer that section reached 23.5 MPa, so revision D uses the raiser's 125 x 50 x 3, at 16.8 MPa. The 16 outriggers weigh 76 kg.
2. Plan bracing in three bays. With no bracing, a recovery pull 30 degrees off the rail axis (LC8a) bent the ladder frame sideways in a Vierendeel shape (revision A: 597 MPa, a utilisation of 1.33). One X of SHS 40 x 40 x 2.5 in each of the two bays ahead of the front tank and one behind the rear tank bring the worst LC8a stress to 349 MPa (0.78). The tanks and the battery fill the other bays.
3. Jacking pads on the XT centre crossmember's underside beside the rail, not on the rail's bottom face. Welded to the rail flange, the pad's weld end (IIW 513, FAT 71) would see the rail's full range. On the crossmember it sees 16.8 MPa against a CAFL of 41.5 MPa (FAT-11).
4. The weld toes on the rail at the full-height crossmembers are burr-ground (IIW 512, 1.3 x FAT 80, a CAFL of 60.8 MPa). They now see 23.4 MPa, so the grinding has a wide margin. It stays in the design because it costs little.
5. 6 mm fillets all round the ends of the three XT crossmembers in place of 5 mm. The weld root (IIW 414, FAT 36) now sees 14.5 MPa against its CAFL of 21.1 MPa.
6. Raisers RHS 125 x 50 x 3 in place of report 11's 100 x 50 x 3, to lift the floor above the 805 mm tyre with 50 mm in hand at full bump.
7. A fixed station at the diesel bay, so the heater's tank sits between two crossmembers.
8. The jacking pads, recovery lugs and chain lugs keep report 11's sizes. The front recovery lugs are 20 mm plate, because a 30 degree sideways pull bends them out of their plane.

## Joints

| Joint | Weld | Fatigue detail |
|---|---|---|
| Raiser to rail | Continuous 4 mm fillets along both edges, vented at each end of each bay | IIW 323, FAT 90 |
| Full-height crossmember to rail | 6 mm (XT) or 5 mm (body ends) fillet all round each end, toe on the rail ground | IIW 512 ground (FAT 104), 413 (FAT 63), root 414 (FAT 36) |
| Raiser-height crossmember to raiser | 5 mm fillet all round | IIW 512 (FAT 80), 413, 414 |
| Outrigger to raiser | 6 mm fillet all round | IIW 413 (FAT 63), root 414 (FAT 36) |
| Drawbar member under the rail | Continuous 5 mm fillets on both edges, profiled root gusset with a 160 mm ground radius at the body front, sniped 1:2 taper over 300 mm at X 2,820 with the toe ground | IIW 526 (FAT 90) at the root, 712 (FAT 56) at the end |
| Drawbar A-frame part to its overlap part | Mitred full penetration butt weld, ground flush | IIW 526 |
| Cross brace to the drawbar members | 5 mm fillet all round at mid-depth | IIW 413 |
| Chain lugs, recovery lugs and tongues | 6 mm fillets along their length only | IIW 513 |
| Body mount nut plates | 10 mm plate inside the raiser or on the outrigger, fillet all round | Not a fatigue detail of the frame. BODY.md checks the bolt, plate and weld |
| Coupling plate to the apex | 6 mm fillets all round | Not a fatigue detail of the frame. The DO35 bolts to it |
| Hinge, airbag and shock brackets (Cruisemaster's) | Cruisemaster's drawing 33XT AIR | Hot-spot classes, IIW Table 3.3-1 |

## Fittings and bought parts

| Item | Basis | Mass |
|---|---|---|
| Cruisemaster DO35 V3Plus, under-mounted on a 12 mm plate at the apex, four M12 8.8 bolts at 90 Nm, with the integrated handbrake | DO35 guide p. 3 | 9.5 kg (estimate) |
| Chain lugs, 10 mm plate, 18 mm hole, at X 400 on the members' outer faces | VSB1 9.2.2 | 1.9 kg |
| Safety chains to AS 4177.4 (4177-35) with ARK HLS13 shackles | VSB1 9.2.1 | 4.5 kg (estimate) |
| ARK XO750 jockey wheel on a bolted 8 mm bracket on the kerb-side member at X 1,000, ahead of the drawbar box | Report 11 section 6.4 | 20.0 kg (ARK, report 13 section 6) |
| Stone guard on the cross brace and member tops, on rubber, its top at Z 608 | Report 11 section 6.4 | 7.0 kg (calculated) |
| Breakaway kit, switch near the coupling | VSB1 8 | 5.0 kg (estimate) |
| Front recovery lugs, 20 mm, on the drawbar members' outer faces at X 2,150, outside the 300 mm root zone | LC8a | 7.5 kg |
| Rear recovery tongues, 20 mm, through slots in the rear crossmember at X 6,170, welded to the rail webs | LC8a | 9.8 kg |
| Jacking pads, 100 x 100 x 10 with a locating cup, on the XT centre crossmember beside each rail | LC8b | 1.6 kg |
| Four ARK XO DDS650 corner steadies (875 kg), at X 2,220 and 6,070, on bolted 6 mm brackets | LC5b | 35.2 kg (retailer, report 13 section 6) |
| Body mount nut plates, 10 mm, M12 tapped, 32 | BODY.md | 8.8 kg (calculated) |
| Spare carrier cleats and hub plate | LC2, LC7 | 4.2 kg |
| Floor bearer strip on the raisers, outriggers and floor crossmembers, 22.5 mm HDPE with an EPDM face | Report 11 section 2 | 23.4 kg (estimate) |
| Galvanising, 33.7 m² inside and out at AS/NZS 4680 minimum coating masses | Report 11 section 1.4 | 13.8 kg (calculated) |

## Mass

The chassis and drawbar weigh 459.9 kg of steel and 13.8 kg of zinc, 474 kg galvanised, plus 104.6 kg of bought parts and fittings: 578 kg in all. The steel and zinc are calculated (7 % growth allowance). In revision C, for the 5,500 mm trailer with its garage, the steel was 479 kg. The shorter rails save more than the deeper raisers and outriggers add.

## Design basis (report 02 LOAD-01)

Every case runs on all six trailer cases (TC1 to TC6), with the water in the tanks, the fuel and the gear as each case carries them. The masses are scaled by one factor so the heaviest case, TC2 fully loaded with 400 L of water, sits at the plated 3,100 kg ATM (a factor of 1.117). That keeps each case's balance while designing at the plate, as report 11 asks. LC5b runs at tare.

| Case | Load | Direction and combination | Factor or criterion | Source |
|---|---|---|---|---|
| LC1 | Static, 1 g | Down | Stress ≤ fy / 3 (150 MPa). Rail between the drawbar root and the front hub ≤ span / 500, rear overhang tip ≤ overhang / 300, outrigger tip ≤ 2 mm | ARTSA factor of 3 (report 02), deflection limits proposed in report 11 |
| LC2 | Vertical bump, 3 g on the structure, 4 g on local fixings | Down | Stress < fy | Report 11, ARTSA |
| LC3 | Braking, 0.8 g forward with 1 g down, braked at the tyres | Together | Stress ≤ fy / 1.5 | Report 02 |
| LC4 | Cornering, 0.5 g sideways each way with 1 g down | Together, both directions | Stress ≤ fy / 1.5 | Report 02 |
| LC5a | Twist, one wheel in a hole: 13.4 kNm between the axles with 1 g down | Together, both diagonals | Stress ≤ fy / 1.5, twist between the front hinge and rear shock crossmembers ≤ 0.5 degree | Report 11: 820 kg x 9.81 x 0.831 m = 6.7 kNm, times 2 |
| LC5b | Twist at tare, one corner steady wound to 875 kg | With 1 g down | Stress ≤ fy / 1.5 | Report 11, ARK |
| LC6 | Drawbar, VSB1 9.1 at the 3,100 kg plate: 45.6 kN along, 15.2 kN across, 15.2 kN up and down at the coupling | Each separately, each way | Stress < fy (no residual deformation) | VSB1 9.1 and 14, ADR 62/02 14.2 |
| LC6b | Chain points, VSB1 9.2.2 at the plate: 30.4 kN along, 15.2 kN up and down | At each lug separately | Stress < fy | VSB1 9.2.2, ADR 62/02 14.4.2 |
| LC7 | Cargo fixings: 0.8 g forward, 0.5 g rearward, 0.5 g sideways, 0.2 g up, each times 2 off road | Separately | Fixing forces for the body design, fy / 1.5 | NTC guide via report 02, factor from report 03 |
| LC8a | Recovery: 51.5 kN at each front and rear point within 30 degrees sideways and 15 degrees up or down, 78.5 kN ultimate | Separately, nine directions each | No yield at 51.5 kN, no fracture at 78.5 kN | Report 11, kept at the 3,500 kg figure |
| LC8b | Jacking one side at its pad, gravity times 2 | Down | Stress < fy, no crushing | Report 11 (38.6 kN on one pad) |
| LC10 | Fatigue: frequent ±0.5 g (a 1 g range) beyond 10 million cycles, occasional ±1.5 g for 100,000 cycles | Down | Frequent range ≤ CAFL, Miner damage of the occasional range ≤ 0.5 | Report 11 section 3.4, IIW-1823-07 |

## Analysis

The frame model is a 3D beam model on the members' centroid axes, solved by the direct stiffness method in `cad/frame.py` (numpy and scipy). `cad/tests/test_frame.py` checks the solver against closed forms: a cantilever's tip deflection and root moment along four axes, a simply supported beam's midspan moment and deflection, a cantilever in torsion, and the equilibrium of a 3D portal frame. The chassis model has 246 nodes, 211 beam elements and 68 rigid links.

- The composite rail is one beam with the combined section: centroid 139 mm above the rail underside (Z 736), I = 14.9 x 10⁶ mm⁴, Z = 107.1 x 10³ mm³ at the bottom and 109.4 x 10³ mm³ at the top. Report 11's 100 mm raiser gave I = 11.6 x 10⁶ mm⁴ by the parallel-axis sum. `cad/tests/test_chassis.py` pins the value.
- Crossmembers, outriggers, braces and the drawbar members are beams on their own axes. They join the rail axis through rigid links, so every joint is rigid. The drawbar's overlap part is linked to the rail at every rail node along its 1,000 mm, which is what the continuous seams do.
- The coupling is a ball joint: it takes the ball force and no moment.
- Each XT arm is solved as a free body. Its tyre contact force, its own weight and the airbag force (straight over the hub, on the rail's inner face) balance about the hinge pivot, and the hinge takes the rest. The pivot is report 11's: 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, rigidly tied to the rail at that crossmember.

Load mapping. Each mass goes onto the frame by its load path, with its exact resultant and the moment of its offset kept:

- the floor spans across the trailer onto the raisers, so a load between the rails is shared by the two rails by the lever rule, and one outside them by the two nearest outriggers on that side;
- the roof and its panels go to the two side walls by the lever rule, then down to the outriggers;
- tanks, water, battery, guards and the TSC hang between the rails;
- the spare wheel goes to its posts on the front crossmember;
- the drawbar box, the generator, the jerry cans and the coupling and drawbar fittings go onto the drawbar members;
- the arms, hubs, wheels and tyres go through the arm free body;
- the designed members carry their own weight with their galvanising.

Block items with a box are cut into 200 mm cells, so the floor, walls, tanks and furniture spread as they do in the body. The ball and the four wheels react each case by statics, with equal vertical loads on the two axles of a side (the XT arms do not share load). The frame is then held by six supports that only stop rigid-body motion. Their reactions come out below 1 N in every case, so the loads and the reactions balance. In LC6, LC6b and LC8a the frame is held at its four hinge pivots and airbag brackets, as VSB1 14 holds the body during the test.

Stress. At each element end the normal stress is the axial stress plus the strong-axis and weak-axis bending stresses at the corner, and the shear is the torsion shear plus the wall shear. They combine as √(σ² + 3τ²).

## Results

| Case | Governing member | Where and when | Stress | Limit | Utilisation |
|---|---|---|---|---|---|
| LC1 | Kerb-side rail | Over the rear hub, TC2 | 32 MPa | 150 MPa | 0.21 |
| LC2 | Kerb-side rail | Over the rear hub, TC2 | 95 MPa | 450 MPa | 0.21 |
| LC3 | Kerb-side drawbar member | At the body front, TC2 | 127 MPa | 300 MPa | 0.42 |
| LC4 | XT centre crossmember | At the kerb-side rail, TC2 cornering to the kerb side | 96 MPa | 300 MPa | 0.32 |
| LC5a | Road-side rail | Over the front hub, TC4 | 78 MPa | 300 MPa | 0.26 |
| LC5b | Road-side drawbar member | Under the rail just behind the body front, TC1, one steady wound to 875 kg | 117 MPa | 300 MPa | 0.39 |
| LC6 | Road-side drawbar member | At the body front, 15.2 kN up | 244 MPa | 450 MPa | 0.54 |
| LC6b | Kerb-side rail | At the XT front hinge crossmember, kerb-side lug 15.2 kN down | 225 MPa | 450 MPa | 0.50 |
| LC8a | Kerb-side rail | At the XT rear shock crossmember, rear kerb-side point pulled 30 degrees sideways and 15 degrees up | 349 MPa | 450 MPa | 0.78 |
| LC8b | Kerb-side rail | At the XT centre crossmember, kerb side jacked, TC2 | 113 MPa | 450 MPa | 0.25 |

The recovery case governs, then the VSB1 cases. The shorter body brings the front hinge crossmember to X 3,306 mm, 1,486 mm behind the body front, so the rail no longer carries VSB1's vertical force as a long cantilever. The travel cases stay below 0.43.

Deflection and twist (LC1, at the plate): the rail between the drawbar root and the front hub deflects 0.11 mm against the chord (limit 3.9 mm), the rear overhang tip 1.37 mm against the line through the hubs (limit 6.8 mm), and the worst outrigger tip 0.69 mm relative to its rail (limit 2.0 mm). Under LC5a the frame twists 0.439 degree between the front hinge and rear shock crossmembers against the 0.5 degree limit. The twist limit still has the least margin of any static check (12 %).

Fittings: the chain lugs reach 41 % of their limit (bearing), the front recovery lugs 73 % (plate bending at 78.5 kN, 30 degrees sideways), the rear tongues 62 %, the jacking pads 36 % under the frame's 34.6 kN, and the spare carrier posts 10 %.

Tyre clearance (FIT-05): each tyre is swung about its pivot through ±60 mm with the ute's 805 mm tyre. The nearest chassis member is the kerb-side rail, 54.0 mm from the front kerb-side tyre at 60 mm of droop, against the 50 mm limit. The floor height is set from the same tyre, so the floor panel is 50.0 mm above it at full bump, the plan's clearance.

LC7 fixing forces for the heavy items are in `build/chassis/chassis.json`. They go to the body and tank designs.

### Fatigue (LC10)

Every detail passes its frequent check, and the largest Miner damage from the occasional case is 0.14, at the outrigger root weld (FAT-05). The tightest are FAT-05 (16.8 MPa against a CAFL of 21.1 MPa, with the RHS 125 outriggers), FAT-03 at the XT crossmember weld roots (14.5 MPa against 21.1 MPa with the 6 mm fillets) and FAT-04, the outrigger toe (23.5 MPa against 36.9 MPa). The table with every detail is on CT-103 and the site's Chassis page.

The hollow-section T-joints are marked HS: the crossmember-to-rail joints, the outrigger roots, the cross brace and the brackets on the rail. Their nominal stress understates the stress at the weld toe, often by a factor of two to four, because the joint bends the thin wall it lands on. The engineer must check them by the hot-spot method or CIDECT design guide 8.

### Against report 11's hand numbers

| Member and case | Report 11 | Frame model | Why they differ |
|---|---|---|---|
| Composite rail, LC2 | 130 MPa | 92 MPa | Report 11 took 13.5 kNm per side on Z = 104 x 10³ mm³. The frame gives 9.7 kNm on the kerb rail over the rear hub, because the trailer is lighter and shorter, and the deeper composite section has Z = 107.1 x 10³ mm³. 130 x (104 / 107.1) x (9.7 / 13.5) = 91 MPa |
| Drawbar member at the body front, LC6 vertical | 264 MPa | 242 MPa | Report 11 used VSB1's 17.2 kN for 3,500 kg. At the 3,100 kg plate the force is 15.2 kN, which alone gives 233 MPa. The member runs at an angle to X, so its lever is about 5 % longer than the 1.82 m report 11 took |
| Outrigger root, LC2 | 177 MPa | 70 MPa | The section changed from 75 x 50 x 3 (Z = 13.9 x 10³ mm³) to 125 x 50 x 3 (Z = 29.9 x 10³ mm³), which takes 177 to 82 MPa. Report 11 assumed 150 kg at the tip. The mapped loads put the equivalent of 117 kg at the tip of the worst outrigger, the kerb-side one at the XT centre station in TC1, which gives 64 MPa. The rest is the torsion and shear the frame adds |

## What the engineer must check

1. The load cases, the factor of 2 on twist, the ±0.5 g frequent fatigue case and the deflection and twist limits (report 11 open question 6).
2. The hot-spot stresses at every HS detail, above all the outrigger roots (FAT-04 and FAT-05), the XT crossmember weld roots (FAT-03) and the full-height crossmember toes on the rail (FAT-01).
3. VSB1 9.1 and 9.2.2 evidence at the 3,100 kg plate: test, or calculation approved by the department (report 11 open question 7). The recovery case reaches 0.78 of yield in the kerb-side rail.
4. The local stability of the 3 mm rail walls at the jacking pad and under the hinge brackets, which a beam model does not see.
5. The plan bracing's gusset plates and their welds, which the model treats as rigid.
6. SP to AS/NZS 1554.1 for every weld, or AS/NZS 1554.5 for the most fatigue-loaded joints (report 11 open question 8).
7. The floor panel spanning 612.5 mm from the raiser to the body edge between outriggers at most 900 mm apart, with no edge member (BODY.md checks it as BDY-04).
8. Whether the drawbar members can drop to RHS 150 x 50 x 4 at the 3,100 kg plate, about 14 kg lighter (TRAILER.md open question 5).

## Assumptions made for the design

Each is in TRAILER.md's assumptions list with its source.

- The XT arm pivot is 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, scaled from Cruisemaster's drawing (±10 mm).
- Raiser-level outriggers at the XT stations are acceptable to Cruisemaster, against its note that outriggers be full rail height.
- 150 x 50 x 3 XT crossmembers suit the 4,500 kg XT Air build at 900 mm axle spacing.
- The DO35's coupling point sits below the plate it is under-mounted on, so the plate at the members' underside puts the coupling point at Z 440, the ute's laden ball height.
- A galvanising bath takes a frame 6.3 m long and 2.4 m wide across the outriggers.
- The floor panel needs no continuous edge support.
- The engineer accepts report 11's load cases and its planning fatigue method.
- Grade 350 plate at 350 MPa for every thickness up to 20 mm.
- The recovery points keep report 11's 51.5 kN, the 3,500 kg figure, though the plate is 3,100 kg.
- The corner steadies at X 2,220 and 6,070 mm, about 400 mm inside the body ends (layout-79 section 4.3).
- The jockey wheel at X 1,000 mm, ahead of the drawbar box.
- Bought part masses where not published: DO35 9.5 kg, chains 4.5 kg, breakaway kit 5 kg, floor bearer strip about 0.9 kg/m. The jockey wheel (20 kg) and the corner steadies (8.8 kg each) use published figures (report 13 section 6).

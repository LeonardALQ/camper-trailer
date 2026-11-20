# Chassis and drawbar: design (planning level)

Status: proposal, revision B, 20 Nov 2026. Revision B follows TRAILER.md revision F: the tyre is Yokohama's published 752 mm, so the frame sits 1.3 mm higher and the bearer strip is 21 mm, and the axle re-solved to X 5,021. DRAFT, not for construction until the engineer reviews it. This document is the design basis report 02 asks for in LOAD-01: every load case with its factor, direction, combination and source, then the members, joints and protection, the results, and what the engineer must check. The design starts from research report 11 (`research/11-chassis-design.md`) and changes a member only where the analysis showed it fails or is oversized. The data is `data/chassis/chassis.yaml` with report 11's section table in `data/chassis/sections.yaml`, the geometry is `cad/chassis.py`, the analysis `cad/chassis_fea.py` and the solver `cad/frame.py`. Drawings CT-101 (general arrangement), CT-102 (drawbar and coupling) and CT-103 (details) show it. The results below are from this revision's build. The site's Chassis page always shows the current build.

Terms. A raiser is the second tube welded on top of each main rail to lift the floor above the tyres. The composite rail is the rail and its raiser welded together continuously, so they bend as one 250 mm deep section. An outrigger is a short member from the raiser out to the body edge. Utilisation is the stress divided by the case's limit, so 1.00 is at the limit. A FAT class is the IIW fatigue class of a welded detail, the stress range in MPa it survives for 2 million cycles, and the CAFL is 0.585 times it, the range below which the detail is taken to last indefinitely. SP is the structural purpose weld category of AS/NZS 1554.1.

Positions are in the project datum DIM-01: X rearward from the ball centre, Y positive to the road side, Z up from the ground at design ride height, all in mm.

## Material, welding and protection

- Tube: AS/NZS 1163 grade C450L0 RHS and SHS, bought as Austube Mills C450PLUS black tube (fy 450 MPa, fu 500 MPa). Section properties are report 11's, checked against Austube's design capacity tables. The weak-axis modulus is the AS 4100 effective one where the section is slender in that axis.
- Plate: AS/NZS 3678 grade 350. The checks use fy 350 MPa and fu 450 MPa for every thickness up to 20 mm (assumption: grade 350 plate over 12 mm is 340 MPa, so the 20 mm parts have about 3 % less margin than shown).
- Welding: every structural weld SP to AS/NZS 1554.1 with E49XX or W50X consumables. The rail-to-raiser seams and the drawbar-to-rail seams are continuous fillets. No weld runs across the width of a rail (Cruisemaster TB 070). Inspection follows report 02 WLD-03.
- Protection: the whole welded frame is hot-dip galvanised after fabrication to AS/NZS 4680, vented and drained to report 02 WLD-05. The coupling plate faces are cleaned flat after dipping.

## Members

The frame is a ladder of two composite rails with crossmembers at nine stations, outriggers at every station, an A-frame drawbar that runs on under the rails, and three bays of plan bracing.

| Member | Section | Where | Qty | Mass |
|---|---|---|---|---|
| Main rails | RHS 150 x 50 x 3 | X 1,820 to 7,320, centres 618 mm from the centreline (1,286 mm outer width), Z 571 to 721 | 2 | 98.4 kg |
| Raisers | RHS 100 x 50 x 3, continuous fillets to the rail | On each rail, Z 721 to 821, with a 21 mm bearer strip up to the floor underside at Z 842 | 2 | 72.6 kg |
| Body end crossmembers | RHS 150 x 50 x 3, full rail height | Body front (centre X 1,845) and rear (X 7,295) | 2 | 21.2 kg |
| XT crossmembers | RHS 150 x 50 x 3, full rail height, no holes | Front hinge (X 4,162), centre (X 4,992), rear shock (X 5,822, with a 5 mm shock plate) | 3 | 31.8 kg |
| Floor crossmembers | RHS 100 x 50 x 3 at raiser height, top flush with the raisers | X 2,437, 3,003, 3,570 and the battery bay at X 6,550 | 4 | 31.3 kg |
| Outriggers | RHS 100 x 50 x 3 at raiser height, top flush, 557 mm to the body edge | At all nine stations, each side | 18 | 66.2 kg |
| Plan bracing | SHS 40 x 40 x 2.5, an X of two diagonals at rail height | Bays X 3,003 to 3,570, 3,570 to 4,162, and 5,822 to 6,550 | 6 | 22.4 kg |
| Drawbar members | RHS 150 x 50 x 5 | Apex X 250 at Y ±60, to the rail centres at X 1,820, then 1,000 mm on under the rails to X 2,820 | 2 (4 lengths) | 75.7 kg |
| Drawbar cross brace | RHS 75 x 50 x 3 at the members' mid-depth | X 900 | 1 | 2.9 kg |
| Spare carrier posts | SHS 50 x 50 x 2.5, bolted to cleats on the front crossmember | X 1,795, Y ±120, up to Z 1,500 | 2 | 6.7 kg |

Plates, lugs, pads and gussets add 49.8 kg (23 pieces, every one calculated from its size). The member schedule and the plate list with sizes are on CT-101 and CT-102, and the site's downloads page offers the cut list as `chassis-cut-list.csv`.

### Changes from report 11, and why

1. Outriggers RHS 100 x 50 x 3 in place of 75 x 50 x 3, with 6 mm fillets all round. With the 75 x 50 x 3 section the frequent fatigue range at the root weld was 34.7 MPa against the FAT 36 root's CAFL of 21.1 MPa (IIW 414). The deeper section and the larger weld bring it to 14 MPa. The bottom now sits at the rail top, Z 721. The swept-arc check (FIT-05) still passes: the tyre comes 88.6 mm from the nearest outrigger, the kerb-side one at the XT centre station, at full bump. Report 11 found 89 mm for an outrigger bottom at Z 720, so the two methods agree. The 18 outriggers weigh 66 kg instead of about 54 kg.
2. Plan bracing in three bays. With no bracing, a recovery pull 30 degrees off the rail axis (LC8a) bent the ladder frame sideways in a Vierendeel shape: 597 MPa in the XT rear shock crossmember, a utilisation of 1.33. One X of SHS 40 x 40 x 2.5 in the free bay behind the rear tank and two in the bays ahead of the front tank bring the worst LC8a stress to 423 MPa (0.94). The tanks and the battery fill the other bays, so the diagonals go where the space is free. 22 kg. SHS 50 x 50 x 3 gave the same result and weighs 11 kg more, so the lighter tube is used.
3. Jacking pads on the XT centre crossmember's underside beside the rail, not on the rail's bottom face. Welded to the rail flange, the pad's weld end (IIW 513, FAT 71) saw the rail's 61.6 MPa frequent range against a CAFL of 41.5 MPa. On the crossmember it sees 25 MPa.
4. The weld toes on the rail at the full-height crossmembers are burr-ground. As welded (IIW 512, FAT 80) the frequent range there is 57 MPa against a CAFL of 46.8 MPa. IIW allows a factor of 1.3 for toe grinding, so FAT 104 and a CAFL of 60.8 MPa. The margin is 7 %. The alternative is a 150 x 50 x 4 rail.
5. 6 mm fillets all round the ends of the three XT crossmembers in place of 5 mm. With 5 mm fillets the weld root (IIW 414, FAT 36) saw 21.3 MPa against its CAFL of 21.1 MPa. With 6 mm fillets it sees 17.7 MPa.
6. The jacking pads, recovery lugs and chain lugs keep report 11's sizes. The front recovery lugs are 20 mm plate, because a 30 degree sideways pull bends them out of their plane.

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
| Coupling plate to the apex | 6 mm fillets all round | Not a fatigue detail of the frame; the DO35 bolts to it |
| Hinge, airbag and shock brackets (Cruisemaster's) | Cruisemaster's drawing 33XT AIR | Hot-spot classes, IIW Table 3.3-1 |

## Fittings and bought parts

| Item | Basis | Mass |
|---|---|---|
| Cruisemaster DO35 V3Plus, under-mounted on a 300 x 220 x 12 plate, four M12 8.8 bolts at 90 Nm, with the integrated handbrake | DO35 guide p. 3 | 9.5 kg (estimate) |
| Chain lugs, 120 x 100 x 10, 18 mm hole, 150 mm behind the coupling plate | VSB1 9.2.2 | 1.9 kg |
| Safety chains to AS 4177.4 (4177-35) with ARK HLS13 shackles | VSB1 9.2.1 | 4.5 kg (estimate) |
| ARK XO750 jockey wheel on a bolted 8 mm bracket on the kerb-side member at X 500 | Report 11 section 6.4 | 9.0 kg (estimate) |
| Stone guard on the cross brace and member tops, on rubber | Report 11 section 6.4 | 7.0 kg (calculated) |
| Breakaway kit, switch near the coupling | VSB1 8 | 5.0 kg (estimate) |
| Front recovery lugs, 200 x 120 x 20, on the drawbar members' outer faces at X 2,150, outside the 300 mm root zone | LC8a | 7.5 kg |
| Rear recovery tongues, 260 x 120 x 20, through slots in the rear crossmember, welded to the rail webs | LC8a | 9.8 kg |
| Jacking pads, 100 x 100 x 10 with a locating cup, on the XT centre crossmember beside each rail | LC8b | 1.6 kg |
| Four ARK XO DDS650 corner steadies (875 kg), front pair at X 3,000, rear pair at X 7,150, on bolted 6 mm brackets | LC5b | 22.0 kg (estimate) |
| Spare carrier cleats and hub plate | LC2, LC7 | 4.2 kg |
| Floor bearer strip on the raisers, outriggers and floor crossmembers, 50 x 21 mm HDPE with an EPDM face, 25.8 m | Report 11 section 2 | 25.8 kg (estimate) |
| Galvanising, 35.9 m² inside and out at AS/NZS 4680 minimum coating masses | Report 11 section 1.4 | 14.6 kg (calculated) |

## Mass

The chassis and drawbar weigh 479 kg of steel, 15 kg of zinc and 83 kg of bought parts and fittings, 576 kg in all. The block chassis it replaces was 503 kg: 117 kg of drawbar and coupling, 381 kg of chassis and the 6 kg spare bracket. The new chassis is 73 kg heavier, but its steel and zinc are calculated (7 % growth allowance) where the blocks were estimates (20 %). The block lines it replaces are CH-01 to CH-03, every CM and OR line, DB-01 to DB-04 and SP-03. CH-03's 50 kg allowance for suspension mounts is not carried on: the hinge, airbag and shock brackets come with the XT kit (RG-01), and the designed shock plates and hinge gussets are lines of their own.

With the designed chassis the axle re-solved from X 5,036 to X 5,013, so the towball stays at its 221 kg target fully loaded. TC2 rose from 3,351 to 3,424 kg on base weights, and from 3,864 to 3,887 kg with growth. The ballast for the cases without bikes rose from 59 to 63 kg on base weights. With growth it fell from 218 to 183 kg, because the calculated chassis carries less allowance. TRAILER.md revision F then took the tyre at its published 752 mm and made BD-10 the mud flaps only, because the four corner steadies here had been counted a second time in it. The axle re-solved to X 5,021 and TC2 is now 3,408 kg on base weights (3,866 kg with growth). The towball in the other cases: TC1 251 kg, TC4 280 kg, TC5 278 kg, TC6 256 kg and TC7 270 kg. The ballast is 62 kg on base weights and 181 kg with growth. TRAILER.md has the full load case table.

## Design basis (report 02 LOAD-01)

Every case runs on all seven trailer cases (TC1 to TC7), with the water in the tanks, the bikes, gas, fuel and gear as each case carries them. The masses are scaled by one factor so the heaviest case, TC6 with the Tuareg and 400 L of water, sits at the plated 3,500 kg ATM (a factor of 1.020). That keeps each case's balance while designing at the ATM, as report 11 asks. LC5b runs at tare.

| Case | Load | Direction and combination | Factor or criterion | Source |
|---|---|---|---|---|
| LC1 | Static, 1 g | Down | Stress ≤ fy / 3 (150 MPa). Rail between the drawbar root and the front hub ≤ span / 500, rear overhang tip ≤ overhang / 300, outrigger tip ≤ 2 mm | ARTSA factor of 3 (report 02), deflection limits proposed in report 11 |
| LC2 | Vertical bump, 3 g on the structure, 4 g on local fixings | Down | Stress < fy | Report 11, ARTSA |
| LC3 | Braking, 0.8 g forward with 1 g down, braked at the tyres | Together | Stress ≤ fy / 1.5 | Report 02 |
| LC4 | Cornering, 0.5 g sideways each way with 1 g down | Together, both directions | Stress ≤ fy / 1.5 | Report 02 |
| LC5a | Twist, one wheel in a hole: 13.4 kNm between the axles with 1 g down | Together, both diagonals | Stress ≤ fy / 1.5, twist between the front hinge and rear shock crossmembers ≤ 0.5 degree | Report 11: 820 kg x 9.81 x 0.831 m = 6.7 kNm, times 2 |
| LC5b | Twist at tare, one corner steady wound to 875 kg | With 1 g down | Stress ≤ fy / 1.5 | Report 11, ARK |
| LC6 | Drawbar, VSB1 9.1: 51.5 kN along, 17.2 kN across, 17.2 kN up and down at the coupling | Each separately, each way | Stress < fy (no residual deformation) | VSB1 9.1 and 14, ADR 62/02 14.2 |
| LC6b | Chain points, VSB1 9.2.2: 34.3 kN along, 17.2 kN up and down | At each lug separately | Stress < fy | VSB1 9.2.2, ADR 62/02 14.4.2 |
| LC7 | Cargo fixings: 0.8 g forward, 0.5 g rearward, 0.5 g sideways, 0.2 g up, each times 2 off road | Separately | Fixing forces for the body design, fy / 1.5 | NTC guide via report 02, factor from report 03 |
| LC8a | Recovery: 51.5 kN at each front and rear point within 30 degrees sideways and 15 degrees up or down, 78.5 kN ultimate | Separately, nine directions each | No yield at 51.5 kN, no fracture at 78.5 kN | Report 11 |
| LC8b | Jacking one side at its pad, gravity times 2 | Down | Stress < fy, no crushing | Report 11 (38.6 kN on one pad) |
| LC10 | Fatigue: frequent ±0.5 g (a 1 g range) beyond 10 million cycles, occasional ±1.5 g for 100,000 cycles | Down | Frequent range ≤ CAFL, Miner damage of the occasional range ≤ 0.5 | Report 11 section 3.4, IIW-1823-07 |

## Analysis

The frame model is a 3D beam model on the members' centroid axes, solved by the direct stiffness method in `cad/frame.py` (numpy and scipy). `cad/tests/test_frame.py` checks the solver against closed forms: a cantilever's tip deflection and root moment along four axes, a simply supported beam's midspan moment and deflection, a cantilever in torsion, and the equilibrium of a 3D portal frame. The chassis model has 271 nodes, 233 beam elements and 70 rigid links.

- The composite rail is one beam with the combined section: centroid 128 mm above the rail underside (Z 698), I = 11.6 x 10⁶ mm⁴, Z = 90.7 x 10³ mm³ at the bottom and 95.2 x 10³ mm³ at the top. Report 11 gives I = 14.2 x 10⁶ mm⁴ and Z = 104 x 10³ mm³, which do not follow from its own section table: the parallel-axis sum is 11.6 x 10⁶ mm⁴. `cad/tests/test_chassis.py` pins the value.
- Crossmembers, outriggers, braces and the drawbar members are beams on their own axes. They join the rail axis through rigid links, so every joint is rigid. The drawbar's overlap part is linked to the rail at every rail node along its 1,000 mm, which is what the continuous seams do.
- The coupling is a ball joint: it takes the ball force and no moment.
- Each XT arm is solved as a free body. Its tyre contact force, its own weight and the airbag force (straight over the hub, on the rail's inner face) balance about the hinge pivot, and the hinge takes the rest. The pivot is report 11's: 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, rigidly tied to the rail at that crossmember.

Load mapping. Each mass goes onto the frame by its load path, with its exact resultant and the moment of its offset kept:

- the floor spans across the trailer onto the raisers, so a load between the rails is shared by the two rails by the lever rule, and one outside them by the two nearest outriggers on that side;
- the roof and its panels go to the two side walls by the lever rule, then down to the outriggers;
- tanks, water, battery, guards and the TSC hang between the rails;
- the spare wheel goes to its posts on the front crossmember;
- the coupling and drawbar fittings go onto the drawbar members;
- the arms, hubs, wheels and tyres go through the arm free body;
- the designed members carry their own weight with their galvanising.

Block items with a box are cut into 200 mm cells, so the floor, walls, tanks and furniture spread as they do in the body. The ball and the four wheels react each case by statics, with equal vertical loads on the two axles of a side (the XT arms do not share load). The frame is then held by six supports that only stop rigid-body motion. Their reactions come out below 1 N in every case, so the loads and the reactions balance. In LC6, LC6b and LC8a the frame is held at its four hinge pivots and airbag brackets, as VSB1 14 holds the body during the test.

Stress. At each element end the normal stress is the axial stress plus the strong-axis and weak-axis bending stresses at the corner, and the shear is the torsion shear plus the wall shear. They combine as √(σ² + 3τ²).

## Results

| Case | Governing member | Where and when | Stress | Limit | Utilisation |
|---|---|---|---|---|---|
| LC1 | Kerb-side rail | Over the rear hub, TC2 | 64 MPa | 150 MPa | 0.43 |
| LC2 | Kerb-side rail | Over the rear hub, TC2 | 193 MPa | 450 MPa | 0.43 |
| LC3 | Kerb-side drawbar member | At the body front, TC7 | 143 MPa | 300 MPa | 0.48 |
| LC4 | Kerb-side rail | At the XT centre crossmember, TC2 cornering to the kerb side | 150 MPa | 300 MPa | 0.50 |
| LC5a | Kerb-side rail | Over the front hub, TC2 | 105 MPa | 300 MPa | 0.35 |
| LC5b | Road-side rail | At the front steady, TC1 | 148 MPa | 300 MPa | 0.49 |
| LC6 | Road-side rail | At the XT front hinge crossmember, 17.2 kN up | 395 MPa | 450 MPa | 0.88 |
| LC6b | Road-side rail | At the XT front hinge crossmember, road-side lug 17.2 kN down | 383 MPa | 450 MPa | 0.85 |
| LC8a | Kerb-side rail | At the XT rear shock crossmember, rear kerb-side point pulled 30 degrees sideways and 15 degrees up | 422 MPa | 450 MPa | 0.94 |
| LC8b | Kerb-side rail | At the XT centre crossmember, kerb side jacked, TC2 | 202 MPa | 450 MPa | 0.45 |

The VSB1 cases govern. In LC6 and LC6b the whole 17.2 kN vertical force is held at the suspension mounts, so the rail between the body front and the front hinge crossmember carries it as a 2.3 m cantilever. That is the test's load path, and the rail passes with a margin of 12 %. In service the body and the axles share the load, and the drawbar members themselves peak at 274 MPa at the body front (0.61).

Deflection and twist (LC1, at ATM): the rail between the drawbar root and the front hub deflects 0.4 mm against the chord (limit 5.6 mm), the rear overhang tip 3.9 mm against the line through the hubs (limit 7.7 mm), and the worst outrigger tip 1.1 mm relative to its rail (limit 2.0 mm). Under LC5a the frame twists 0.48 degree between the front hinge and rear shock crossmembers against the 0.5 degree limit, so the twist limit has the least margin of any static check (4 %).

Fittings: the chain lugs reach 40 % of their limit (bearing), the front recovery lugs 73 % (plate bending at 78.5 kN, 30 degrees sideways), the rear tongues 62 %, the jacking pads 38 % under the frame's 40.6 kN, and the spare carrier posts 9 %.

Tyre clearance (FIT-05): each tyre is swung about its pivot through ±60 mm with Yokohama's published 752 mm diameter. The nearest chassis member is the rail, 62.5 mm from the tyre's inner sidewall, against the 50 mm limit. The nearest outrigger is 88.6 mm from the tyre at full bump, and the nearest XT crossmember 112.7 mm. The floor height is set from the same 752 mm diameter, so the floor panel is 50.0 mm above the tyre at full bump, the plan's clearance.

LC7 fixing forces for the heavy items are in `build/chassis/chassis.json` (for example the 400 L of water, 6.3 kN forward, and the 206 kg Tuareg, 3.2 kN forward). They go to the body and tank designs.

### Fatigue (LC10)

Every detail passes its frequent check, and the largest Miner damage from the occasional case is 0.22, at the full-height crossmember toes on the kerb-side rail (FAT-01). The tightest are FAT-01 (57 MPa against 61 MPa with the toe ground), FAT-03 at the XT front hinge crossmember's weld root (18 MPa against 21 MPa with the 6 mm fillets) and FAT-07, the drawbar root (35 MPa against 53 MPa). The table with every detail is on CT-103 and the site's Chassis page.

The hollow-section T-joints are marked HS: the crossmember-to-rail joints, the outrigger roots, the cross brace and the brackets on the rail. Their nominal stress understates the stress at the weld toe, often by a factor of two to four, because the joint bends the thin wall it lands on. The engineer must check them by the hot-spot method or CIDECT design guide 8.

### Against report 11's hand numbers

| Member and case | Report 11 | Frame model | Why they differ |
|---|---|---|---|
| Composite rail, LC2 | 130 MPa | 190 MPa | Report 11 used Z = 104 x 10³ mm³, but the composite section's Z is 90.7 x 10³ mm³ at the bottom, which alone gives 149 MPa. Its moment, 13.5 kNm per side, came from 9.0 kNm at 1 g for both rails. The frame gives 11.0 kNm at the rear hub at 1 g (5.75 kNm on the kerb rail, 5.28 kNm on the road rail), because its loads include the 200 kg of water report 11 left out, the designed chassis 73 kg heavier than the blocks, and the axle 15 mm further forward, and because the kerb-side rail carries 52 % (the kitchen, gas locker, generator and fuel are on the kerb side). 130 x (104 / 90.7) x (5.75 / 4.5) = 190 MPa |
| Drawbar member at the body front, LC6 vertical | 264 MPa | 274 MPa | Report 11 took the lever as 1.82 m, the ball to the body front along X. The member runs at 19.6 degrees to X, so the lever along it is 1.92 m, and the frame gives a strong-axis moment of 16.2 kNm in place of 15.6 kNm. The rest of the inclined lever becomes 1.2 kNm of torsion |
| Outrigger root, LC2 | 177 MPa | 60 MPa | The section changed from 75 x 50 x 3 (Z = 13.9 x 10³ mm³) to 100 x 50 x 3 (Z = 21.3 x 10³ mm³), which takes 177 to 116 MPa. Report 11 assumed 150 kg at the tip. The mapped loads put the equivalent of 77 kg at the tip of the worst outrigger (the road-side one at the XT front hinge station, in TC6): the wall, its share of the roof and the floor edge. 116 x 77 / 150 = 60 MPa |

## What the engineer must check

1. The load cases, the factor of 2 on twist, the ±0.5 g frequent fatigue case and the deflection and twist limits (report 11 open question 6).
2. The hot-spot stresses at every HS detail, above all the full-height crossmember toes on the rail (FAT-01, 7 % margin with ground toes), the XT crossmember weld roots (FAT-03) and the outrigger roots.
3. VSB1 9.1 and 9.2.2 evidence: test, or calculation approved by the department (report 11 open question 7). In the VSB1 load path the rail carries the drawbar's vertical force to the front hinge at 0.88 of yield, and the recovery case at 0.94.
4. The local stability of the 3 mm rail walls at the jacking pad and under the hinge brackets, which a beam model does not see.
5. The plan bracing's gusset plates and their welds, which the model treats as rigid.
6. SP to AS/NZS 1554.1 for every weld, or AS/NZS 1554.5 for the most fatigue-loaded joints (report 11 open question 8).
7. The floor panel spanning 557 mm from the raiser to the body edge between outriggers at most 830 mm apart, with no edge member (assumption in TRAILER.md).

## Assumptions made for the design

Each is in TRAILER.md's assumptions list with its source.

- The XT arm pivot is 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, scaled from Cruisemaster's drawing (±10 mm).
- Raiser-level outriggers at the XT stations are acceptable to Cruisemaster, against its note that outriggers be full rail height.
- 150 x 50 x 3 XT crossmembers suit the 4,500 kg XT Air build.
- The DO35's coupling point sits 130 mm below the plate it is under-mounted on, so the plate at the members' underside puts the coupling point at Z 440.
- A galvanising bath takes a frame 7.4 m long and 2.4 m wide across the outriggers.
- The floor panel needs no continuous edge support.
- The engineer accepts report 11's load cases and its planning fatigue method.
- Grade 350 plate at 350 MPa for every thickness up to 20 mm.
- Bought part masses where not published: DO35 9.5 kg, jockey wheel 9 kg, chains 4.5 kg, breakaway kit 5 kg, corner steadies 5.5 kg each, floor bearer strip 1.0 kg/m.

# Chassis and drawbar: design (planning level)

Status: proposal, revision E, 21 Nov 2026. DRAFT, not for construction until the engineer reviews it. This is the design basis report 02 asks for in LOAD-01: every load case with its factor, direction, combination and source, then the members, joints and protection, the results, and what the engineer must check. It starts from research report 11 and changes a member only where the analysis showed it fails or is oversized. The data is `data/chassis/chassis.yaml` (data revision C) with report 11's section table in `data/chassis/sections.yaml`. The geometry is `cad/chassis.py`, the analysis `cad/chassis_fea.py` and the solver `cad/frame.py`. Drawings CT-101 to CT-104 show it, and the site's Chassis page shows the current build.

## What changed in revision E, 21 Nov 2026

The frame now carries the home trailer of TRAILER.md revision J. Revision D, the LandCruiser 79 trailer at a 3,100 kg plate, is in the git history.

- Every case is checked at the 3,500 kg plate (decision H2), on all eight trailer cases TC1 to TC8, including the grey-full cases. VSB1's drawbar and chain forces follow the plate: 51.5 kN and 17.2 kN at the coupling, 34.3 kN and 17.2 kN at each chain point.
- The raisers, outriggers and floor crossmembers are RHS 127 x 51 x 3.5 C350L0, because RHS 125 x 50 x 3 is not a stocked size (research report 22). Each member is checked at its own grade, so the composite rail is checked at the raiser's 350 MPa.
- The grey tank fills the rear bay, so a floor crossmember crosses its middle in place of the battery bay's, and the rear bay's plan braces went. The XT rear shock crossmember is RHS 150 x 50 x 4 in place of 150 x 50 x 3, so the rear recovery pull (CHS-08A) passes without them. The tank's 2 mm guard is not counted as a shear plate, because it would buckle at about 4 kN (est.).
- The axle group sits at X 4,373 mm, so the XT stations moved 176 mm rearward.
- The rails are 1,275 mm over their outsides for the 1,655 mm track (decision H22, 21 Nov 2026), 100 mm wider than report 18's 1,175 mm, so the crossmembers, drawbar brace and plan braces are longer and the outriggers 50 mm shorter. The tanks keep their 975 mm width.
- The drawbar box is 1,480 x 320 x 720 mm for two Honda EU22i. The spare wheel sits 415 mm higher on longer posts, so it lifts off over the box.
- No check limit changed, and no estimate changed to pass a check.

Terms. A raiser is the second tube welded on top of each main rail to lift the floor above the tyres. The composite rail is the rail and its raiser welded together continuously, so they bend as one 277 mm deep section. An outrigger is a short member from the raiser out to the body edge. Utilisation is the stress divided by the case's limit. A FAT class is the IIW fatigue class of a welded detail, the stress range in MPa it survives for 2 million cycles, and the CAFL is 0.585 times it, the range below which the detail is taken to last indefinitely. SP is the structural purpose weld category of AS/NZS 1554.1.

## Material, welding and protection

- Tube: the rails, full-height crossmembers, drawbar and braces are AS/NZS 1163 C450L0, bought as Austube Mills C450PLUS (fy 450 MPa). The raisers, outriggers and floor crossmembers are C350L0 (fy 350 MPa). Each grade goes on the mill certificate.
- Plate: AS/NZS 3678 grade 350, checked at fy 350 MPa and fu 450 MPa up to 20 mm (assumption: over 12 mm it is 340 MPa, about 3 % less margin than shown).
- Welding: every structural weld SP to AS/NZS 1554.1 with E49XX or W50X consumables. The rail-to-raiser and drawbar-to-rail seams are continuous. No weld runs across the width of a rail (Cruisemaster TB 070). Inspection follows report 02 WLD-03.
- Protection: hot-dip galvanised after fabrication to AS/NZS 4680, vented and drained to report 02 WLD-05. The coupling plate's faces are cleaned flat after dipping.

## Members

A ladder of two composite rails with crossmembers at eight stations, outriggers at every station, an A-frame drawbar that runs on under the rails, and plan bracing in the two front bays. Stations are given by the front face of their crossmember.

| Member | Section | Where | Qty | Mass |
|---|---|---|---|---|
| Main rails | RHS 150 x 50 x 3 C450L0 | X 1,820 to 6,240, 1,275 mm over their outsides (H22), Z 597.5 to 747.5 | 2 | 79.1 kg |
| Raisers | RHS 127 x 51 x 3.5 C350L0, continuous fillets | On each rail, Z 747.5 to 874.5, with a 20.5 mm bearer strip up to the floor at Z 895 | 2 | 80.2 kg |
| Body end crossmembers | RHS 150 x 50 x 3, full height, 1,175 mm | X 1,820 and 6,190 | 2 | 21.0 kg |
| XT crossmembers | RHS 150 x 50 x 3, full height, no holes | Front hinge X 3,454, centre X 4,354 | 2 | 21.0 kg |
| XT rear shock crossmember | RHS 150 x 50 x 4, with a 5 mm shock plate | X 5,184 | 1 | 13.6 kg |
| Floor crossmembers | RHS 127 x 51 x 3.5, top flush with the raisers | X 2,357, the diesel bay at X 2,894 and the grey bay at X 5,664 | 3 | 32.0 kg |
| Outriggers | RHS 127 x 51 x 3.5, top flush, 562 mm out to the body edge | Every station, each side | 16 | 81.6 kg |
| Plan bracing | SHS 40 x 40 x 2.5, an X at rail height | Bays X 2,357 to 2,894 and 2,894 to 3,454 | 4 | 14.4 kg |
| Drawbar members | RHS 150 x 50 x 5 | Apex X 250 at Y ±60, to the rails at X 1,820, then 1,000 mm on under them | 2 (4 lengths) | 75.7 kg |
| Drawbar cross brace | RHS 75 x 50 x 3 | X 900 | 1 | 2.9 kg |
| Spare carrier posts | SHS 50 x 50 x 2.5 | X 1,795, Y ±120, up to Z 1,915 | 2 | 9.5 kg |

CT-101 and CT-102 carry the member and plate lists, and the site's Downloads page offers the cut list as `chassis-cut-list.csv`.

### Changes from report 11, and why

1. Outriggers RHS 127 x 51 x 3.5 in place of 75 x 50 x 3, with 6 mm fillets all round. With 75 x 50 x 3 the frequent fatigue range at the root weld was 34.7 MPa against the FAT 36 root's CAFL of 21.1 MPa (IIW 414). Now it is 16.2 MPa (FAT-05).
2. Plan bracing in the two bays ahead of the axles. With no bracing, a recovery pull 30 degrees off the rail axis (LC8a) bent the ladder sideways in a Vierendeel shape. The tanks fill the bays behind, so the thicker XT rear shock crossmember takes the rear pull.
3. Jacking pads on the XT centre crossmember beside the rail, not on the rail's bottom face, so the pad's weld end (IIW 513, FAT 71) sees 18.0 MPa against a CAFL of 41.5 MPa (FAT-11).
4. The weld toes on the rail at the full-height crossmembers are burr-ground (IIW 512, a CAFL of 60.8 MPa). They see 26.7 MPa (FAT-01).
5. 6 mm fillets round the ends of the XT crossmembers. The root (IIW 414) sees 15.3 MPa against 21.1 MPa (FAT-03).
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
| Body mount nut plates, coupling plate | Fillets all round | Not frame details. BODY.md checks the mounts, and the DO35 bolts to its plate |
| Cruisemaster's hinge, airbag and shock brackets | Cruisemaster's drawing 33XT AIR | Hot-spot classes, IIW Table 3.3-1 |

## Fittings and bought parts

| Item | Basis | Mass |
|---|---|---|
| Cruisemaster DO35 V3Plus with its handbrake, under a 12 mm plate at the apex on four M12 8.8 bolts | DO35 guide | 9.5 kg (est.) |
| Chain lugs, 10 mm, at X 400, and AS 4177.4 chains with ARK HLS13 shackles | VSB1 9.2 | 1.9 kg and 4.5 kg (est.) |
| ARK XO750 jockey wheel on an 8 mm bracket at X 1,000, swung up along the drawbar for travel | Report 11 section 6.4 | 20.0 kg (maker) |
| Stone guard on the cross brace, trimmed on the kerb side round the jockey wheel | Report 11 section 6.4 | 6.5 kg (calculated) |
| Breakaway kit | VSB1 8 | 5.0 kg (est.) |
| Front recovery lugs, 20 mm, at X 2,150, and rear tongues, 20 mm, through the rear crossmember at X 6,170 | LC8a | 7.5 kg and 9.8 kg |
| Jacking pads, 100 x 100 x 10 with a locating cup, on the XT centre crossmember | LC8b | 1.6 kg |
| Four ARK XO DDS650 corner steadies (875 kg) at X 2,220 and 6,070 | LC5b | 35.2 kg (retailer) |
| Four lashing points, forged 1/2 in weld-on D-rings with their clips (4,000 lb working load limit), under the outrigger ends at X 1,845 and 6,215, welded before galvanising | STB-05 | 1.8 kg (est.) |
| 32 body mount nut plates, 10 mm, M12 tapped | BODY.md | 8.8 kg |
| Spare carrier cleats and hub plate | LC2, LC7 | 4.2 kg |
| Floor bearer strip, HDPE with an EPDM face | Report 11 section 2 | 22.9 kg (est.) |
| Galvanising, 33.5 m² inside and out at AS/NZS 4680's minimum coating masses | Report 11 section 1.4 | 15.4 kg (calculated) |

## Mass

The chassis and drawbar weigh 489.6 kg of steel and 15.4 kg of zinc, 505 kg galvanised, plus 105.4 kg of bought parts and fittings: 610 kg in all. The steel and zinc are calculated (7 % growth). The C350L0 sections, 21.4 m of them, are 28 kg heavier than the 125 x 50 x 3 they replace (9.07 against 7.78 kg/m).

## Design basis (report 02 LOAD-01)

Every case runs on the eight trailer cases TC1 to TC8, with the water, fuel and gear each one carries, scaled by one factor so the heaviest, TC2, sits at the 3,500 kg plate (1.126). That keeps each case's balance while designing at the plate, as report 11 asks. LC5b runs at tare.

| Case | Load | Direction and combination | Factor or criterion | Source |
|---|---|---|---|---|
| LC1 | Static, 1 g | Down | Stress ≤ fy / 3. Rail between the drawbar root and the front hub ≤ span / 500, rear overhang tip ≤ overhang / 300, outrigger tip ≤ 2 mm | ARTSA factor of 3 (report 02), limits proposed in report 11 |
| LC2 | Vertical bump, 3 g on the structure, 4 g on local fixings | Down | Stress < fy | Report 11, ARTSA |
| LC3 | Braking, 0.8 g forward with 1 g down, braked at the tyres | Together | Stress ≤ fy / 1.5 | Report 02 |
| LC4 | Cornering, 0.5 g sideways each way with 1 g down | Together, both ways | Stress ≤ fy / 1.5 | Report 02 |
| LC5a | Twist, one wheel in a hole: 13.4 kNm between the axles with 1 g down | Together, both diagonals | Stress ≤ fy / 1.5, twist between the front hinge and rear shock crossmembers ≤ 0.5 degree | Report 11: 820 kg x 9.81 x 0.831 m = 6.7 kNm, times 2 |
| LC5b | Twist at tare, one corner steady wound to 875 kg | With 1 g down | Stress ≤ fy / 1.5 | Report 11, ARK |
| LC6 | Drawbar, VSB1 9.1 at the 3,500 kg plate: 51.5 kN along, 17.2 kN across, 17.2 kN up and down at the coupling | Each separately, each way | Stress < fy | VSB1 9.1 and 14, ADR 62/02 14.2 |
| LC6b | Chain points, VSB1 9.2.2 at the plate: 34.3 kN along, 17.2 kN up and down | Each lug separately | Stress < fy | VSB1 9.2.2, ADR 62/02 14.4.2 |
| LC7 | Cargo fixings: 0.8 g forward, 0.5 g rearward, 0.5 g sideways, 0.2 g up, each times 2 off road | Separately | Fixing forces for the body design, fy / 1.5 | NTC guide via report 02 |
| LC8a | Recovery: 51.5 kN at each front and rear point within 30 degrees sideways and 15 degrees up or down, 78.5 kN ultimate | Separately, nine directions each | No yield at 51.5 kN, no fracture at 78.5 kN | Report 11 |
| LC8b | Jacking one side at its pad, gravity times 2 | Down | Stress < fy, no crushing | Report 11 |
| LC10 | Fatigue: frequent ±0.5 g beyond 10 million cycles, occasional ±1.5 g for 100,000 cycles | Down | Frequent range ≤ CAFL, Miner damage of the occasional range ≤ 0.5 | Report 11 section 3.4, IIW-1823-07 |

## Analysis

The frame is a 3D beam model on the members' centroid axes, solved by the direct stiffness method in `cad/frame.py`, with 239 nodes, 205 beam elements and 62 rigid links. `cad/tests/test_frame.py` checks the solver against closed forms: cantilevers in bending and torsion, a simply supported beam and the equilibrium of a 3D portal frame.

- The composite rail is one beam with the combined section: centroid at Z 742, I = 16.2 x 10⁶ mm⁴, Z = 111.9 x 10³ mm³ at the bottom and 122.4 x 10³ mm³ at the top. `cad/tests/test_chassis.py` pins it.
- Crossmembers, outriggers, braces and the drawbar members are beams on their own axes, joined to the rail through rigid links, so every joint is rigid. The drawbar's overlap is linked to the rail at every node along its 1,000 mm.
- The coupling is a ball joint. Each XT arm is a free body: its tyre force, its weight and the airbag force balance about the hinge pivot, 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside.

Each mass goes onto the frame by its load path, with its resultant and the moment of its offset kept: the floor spans onto the raisers by the lever rule, the roof goes down the side walls to the outriggers, the tanks, battery box and guards hang between the rails, the spare goes to its posts, and the drawbar box to the drawbar members. Block items are cut into 200 mm cells. The ball and the four wheels react each case by statics, and six supports stop only rigid-body motion, with reactions below 1 N. In LC6, LC6b and LC8a the frame is held at its hinge pivots and airbag brackets, as VSB1 14 holds the body during the test. Stress at each element end combines as √(σ² + 3τ²).

## Results

| Case | Governing member | Where and when | Stress | Limit | Utilisation |
|---|---|---|---|---|---|
| LC1 | Road-side rail | X 4,822, TC7 | 36 MPa | 117 MPa | 0.31 |
| LC2 | Road-side rail | X 4,822, TC7 | 109 MPa | 350 MPa | 0.31 |
| LC3 | Kerb-side drawbar member | At the body front, TC2 | 159 MPa | 300 MPa | 0.53 |
| LC4 | Road-side rail | X 4,379, TC7 cornering towards the road side | 93 MPa | 233 MPa | 0.40 |
| LC5a | Kerb-side rail | X 3,922, TC7, diagonal B | 75 MPa | 233 MPa | 0.32 |
| LC5b | Road-side rail | X 2,820, at tare, one steady wound to 875 kg | 121 MPa | 233 MPa | 0.52 |
| LC6 | Road-side rail | X 3,479, 17.2 kN up at the coupling | 267 MPa | 350 MPa | 0.76 |
| LC6b | Road-side rail | X 3,479, road-side lug, 17.2 kN down | 258 MPa | 350 MPa | 0.74 |
| LC8a | Road-side rail | X 4,379, the rear road-side point pulled 30 degrees sideways and 15 degrees down | 319 MPa | 350 MPa | 0.91 |
| LC8b | Road-side rail | X 4,379, TC7, road side jacked | 122 MPa | 350 MPa | 0.35 |

The rear recovery pull governs, then VSB1's drawbar tests. The rails' checks use the raiser's 350 MPa, which is where the margin went.

Deflection and twist (LC1, at the plate): the rail between the drawbar root and the front hub deflects 0.09 mm against 4.2 mm, the rear overhang tip 1.31 mm against 6.2 mm, and the worst outrigger tip 0.37 mm against 2.0 mm. Under LC5a the frame twists 0.374 degree against 0.5 degree, a 25 % margin.

Fittings: the chain lugs reach 41 % of their limit (bearing), the front recovery lugs 73 % (plate bending at 78.5 kN), the rear tongues 62 %, the jacking pads 37 % under 39.0 kN, and the spare carrier posts 16 %. The tyre swung through its travel comes 53.5 mm from the kerb-side raiser at its closest, against 50 mm (FIT-05).

### Fatigue (LC10)

Every detail passes its frequent check, and the largest Miner damage from the occasional case is 0.12, at the outrigger root weld beside the XT centre station (FAT-05). The tightest are FAT-05 (16.2 MPa against a CAFL of 21.1 MPa), FAT-03 at the XT crossmember roots (15.3 against 21.1 MPa) and the drawbar root (FAT-07, 34.9 against 52.6 MPa). CT-103 and the Chassis page list every detail.

The hollow-section T-joints are marked HS: the crossmember-to-rail joints, the outrigger roots, the cross brace and the brackets on the rail. Their nominal stress understates the stress at the weld toe, often by a factor of two to four, so the engineer checks them by the hot-spot method or CIDECT design guide 8.

## What the engineer must check

1. The load cases, the factor of 2 on twist, the ±0.5 g frequent fatigue case and the deflection and twist limits (report 11 open question 6).
2. The hot-spot stresses at every HS detail, above all the outrigger roots (FAT-04, FAT-05), the XT crossmember roots (FAT-03) and the crossmember toes on the rail (FAT-01).
3. VSB1 9.1 and 9.2.2 evidence at the 3,500 kg plate, by test or by calculation the department accepts. The recovery case reaches 0.91 of yield in the road-side rail.
4. The rear bays without plan bracing: the RHS 150 x 50 x 4 XT rear shock crossmember carries the rear recovery pull.
5. The local stability of the 3 mm rail walls at the jacking pad and under the hinge brackets, which a beam model does not see, and the plan bracing's gussets.
6. SP to AS/NZS 1554.1 for every weld, or AS/NZS 1554.5 for the most fatigue-loaded joints, and the C350L0 and C450L0 grades on the mill certificates.
7. The floor panel spanning from the raiser to the body edge between outriggers at most 900 mm apart, with no edge member (BODY.md, BDY-04).

## Assumptions made for the design

- The XT arm pivot is 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, scaled from Cruisemaster's drawing (±10 mm).
- Raiser-level outriggers at the XT stations are acceptable to Cruisemaster, against its note that outriggers be full rail height.
- RHS 150 x 50 x 3 XT crossmembers, and 150 x 50 x 4 at the rear shocks, suit the 4,500 kg XT Air build at 900 mm axle spacing.
- The DO35 under-mounted on its plate puts the coupling point at Z 440, the ute's laden ball height.
- A galvanising bath takes a frame 6.3 m long and 2.4 m wide across the outriggers.

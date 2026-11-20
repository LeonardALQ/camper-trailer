# Body: design (planning level)

Status: proposal, revision B, 20 Nov 2026. DRAFT, not for construction until the engineer reviews it. This document is the body's design basis as report 02 asks: the panels, the load cases with their criteria and sources, the joints, the mounting, the twist sharing, the fixed roof, the openings, the results and what the engineer must check. It starts from research report 12 (`research/12-body-design.md`) and changes it only where a check failed or the layout asks for it. The data is `data/body/body.yaml`, the checks are `cad/body.py`, the solids `cad/body_model.py`, and the mass lines BD-01 to BD-13 are in `data/assemblies/trailer.yaml`. Drawings CT-201 (body shell), CT-202 (joint details), CT-203 (insert map) and CT-301 (body to chassis) show it. The site's Body page shows the current build.

## What changed in revision B, 20 Nov 2026

Revision A was the body for the 5,500 mm trailer with its rear garage and raising roof. It was drafted on a parked branch and not published. Revision B is the body for the LandCruiser 79 trailer of TRAILER.md revision H.

- The body is 4,420 mm long, 2,400 mm wide and 1,950 mm high inside. There is no garage, no rear door, no rear portal and no pier.
- The raising roof, its canvas, actuators and latches are gone. A fixed 40 mm roof panel is bonded into a roof-to-wall joiner, so the body is one closed cell and takes 98 % of the twist.
- The checks for the bike wheels, the chock bases, the L-track hardpoints, the generator floor edge, the floor deflection under a bike, the lid latches and the rear portal (BDY-01, 02, 05, 08, 12, 15 and 17) are dropped, because their loads left with the garage. Two checks are added: BDY-19, the roof-to-wall joint in a 40 m/s uplift, and BDY-20, the rear wall as the box's rear diaphragm.
- The mounts are 32 M12 8.8 bolts into welded nut plates (CH-P14) at the chassis's 8 stations. The HB10 blind bolt is reported at 0.87 of its safe load and not used, because the nut plate keeps a wider margin.
- The entry door moved 5 mm rearward and the cassette toilet's service door moved forward, so every opening keeps report 12's spacing rules (BDY-18 had been 298 mm against 300 mm).
- The body weighs 578.3 kg, 645.2 kg with growth.
- No check limit changed, and no estimate changed to pass a check.

Terms. A sandwich panel is two thin skins bonded to a light core. D is its bending stiffness per metre width and S its shear stiffness. Wrinkling is a local buckle of a compressed skin into the core. An insert is a dense strip laid into the core where a fixing goes. The body's share of the twist is the part of the bare chassis twist that the body removes when it is bolted on.

Positions are in the project datum DIM-01: X rearward from the ball centre, Y positive to the road side, Z up from the ground at design ride height, all in mm.

## Panels

| Panel | Build-up | Mass | D | Wrinkling |
|---|---|---|---|---|
| Floor, 30 mm | Two 2.0 mm woven roving polyester skins (48 % glass) on 26 mm Divinycell H80 PVC | 8.92 kg/m² (calculated) | 11.0 kNm²/m | 147 MPa |
| Side and rear walls, 35 mm | Two 1.5 mm gelcoat GRP skins (Optiplan Polydet) on 32 mm XPS | 6.0 kg/m² (scaled from the maker) | 5.5 kNm²/m | 51 MPa |
| Front wall, 35 mm | 2.0 mm outer and 1.5 mm inner Polydet skins on 31.5 mm XPS, against stones | 6.7 kg/m² (calculated) | 5.7 kNm²/m | 49 MPa |
| Fixed roof, 40 mm | 2.0 mm top and 1.5 mm bottom Polydet skins on 36.5 mm XPS of about 36 kg/m³, bonded to the walls | 7.0 kg/m² (calculated) | 7.5 kNm²/m | 49 MPa |

The floor, both side walls and the roof are one piece each. Report 12 section 2 has the sheet sizes and the makers. The skins and cores use report 12's data, with the woven roving at 14 GPa and 200 MPa, below the published figures (assumption). The wrinkling stresses take the core's compressive modulus as 2.5 times its shear modulus (assumption). Report 12 sized the floor for the bike wheels. A person's foot now governs it, and the panel is kept (report 18 open question 13).

## Load cases and criteria

The cases follow report 11 and CHASSIS.md. Each panel is checked as a one-way span with an effective width of the load patch plus half the span (report 12 section 3).

| Case | Body load | Criterion | Source |
|---|---|---|---|
| LC1, 1 g | A foot 100 kg on 100 x 150 mm, the roof with the solar array | Deflection: floor span/200, roof span/150 (reported) | Report 12, the engineer sets the limits |
| LC2, 3 g | A foot, the floor edge at 160 kg/m², the roof with the array, the bed on its ledgers | Skins at half their ultimate and half the wrinkling stress, cores at half their shear strength, bearing at half the core's compressive strength | ISO 12215-5 for the skins, report 12 for the rest |
| Wind | 0.5 kPa on a side wall, floor to the roof joiner | As LC2, and deflection span/100 (reported) | Report 12 |
| Wind, 40 m/s | 5.06 kN of uplift on the fixed roof | Half the bond's tension strength over the joiner's width | Report 12 section 3, scaled to the roof's 10.6 m² |
| LC3, LC4 | 0.8 g braking, 0.5 g sideways, on the mounts | Mount bolt shear and tension | Report 11 |
| LC5a | 13.4 kNm of twist between the axles, travelling | Mounts, skins, joints and the rear wall under the body's share | Report 11, report 12 section 4 |
| LC5b | A corner steady wound to 875 kg at tare, parked | As LC5a | Report 11 |
| Inserts | Bed ledgers (255 kg at 3 g), awning brackets (31.5 kg at 3 g) | Half the rated load, then a pull test (LR-09) | Report 02 MAT-05 |

For LC5a and LC5b the checks take the larger of two bounds on the roof joint. In one the bonded roof carries shear, so the body is a closed box. In the other the roof joint is neglected and the body is an open box, as report 12 did for a latched lid. Each body check takes whichever bound loads it more. The chassis checks stay on the bare frame (CHASSIS.md), so they still hold if the body mounts loosen.

## Joints

Every panel edge bonds into an aluminium extrusion with MS polymer, with a bead inside and out (CT-202).

- Floor joiners round the floor edge, 1.4 kg/m. The wall foot sits in the joiner on the floor edge, and the joiner sits on the bearer strip over the outrigger tips.
- Corner joiners at the four vertical corners, 2.0 kg/m.
- A roof-to-wall joiner round the wall tops, 1.65 kg/m, in place of the pop-top rings. The roof panel bonds into it on a 30 mm leg.
- The bed deck bonds and rivets to ledgers on the front and kerb walls, 2,030 mm and 1,650 mm long (assumption). It carries the bed, not the twist.
- Every cut edge is sealed with resin or an edge insert. Cut-out corners are radiused: 68 mm for service doors and 90 mm at the top of the entry door.

Under the body's share of LC5a the shear flow round the box is about 1.0 N/mm in a joiner leg's bond against 22.5 N/mm, and the skins carry 0.25 to 0.34 MPa against 22 to 58 MPa (BDY-14).

## Mounting

The body bolts to the chassis through the EPDM-faced HDPE bearer strip at every station: one bolt into each raiser at Y ±562.5 and one into each outrigger tip at Y ±1,140, 32 mounts at the 8 stations. The body is not bonded to the steel (report 12 option B).

- An M12 8.8 hot-dip galvanised bolt into a 10 mm nut plate, 80 x 44 mm, welded inside the raiser or the outrigger tip before galvanising (CH-P14 in the chassis, 32 plates, 8.8 kg).
- The worst bolt carries 7.37 kN of tension under LC5a, at the plate with TC2's 1,344 kg of body and contents scaled by 1.117. The bolt works at 0.32 of a third of its ultimate tension. The plate spans between the RHS webs at 0.17 in bending, its two 4 mm fillets 80 mm long at 0.10, and the floor's pull-through under the spreader at 0.13 (BDY-16).
- On the floor, a bonded 100 x 100 x 3 mm aluminium spreader over a high-density PVC insert and a GRP crush tube.
- Shear is small: 0.33 kN per bolt in LC3 braking.

Report 12 picked the Lindapter Hollo-Bolt HB10 (8.5 kN safe working load in tension). On this body it would work at 0.87. The nut plate keeps more margin and costs little, so it is the design, and the HB10 figure is reported for comparison.

The bolt counts its full working tension in LC5a and LC5b. The tension comes from the body holding the chassis against its own twist, so it is real only while the body stays stiff. A weighed and pull-tested sample replaces these planning numbers.

Isolation and sealing (MAT-04): galvanised steel touches only the HDPE strip and the bolt. The crush tube keeps aluminium off the steel. Duralac goes on every faying surface and a nylon washer and sleeve on every bolt where an extrusion sits over steel. MS polymer seals every hole and spreader. Each outrigger tip is shimmed to within 2 mm of the raiser plane. Every bolt is re-torqued after the first rough trip (FAIL-03).

## Twist sharing

The frame model takes the body as a torsion box: a chain of elements on the centreline with the box's torsion stiffness only, tied at every station to both raisers by posts that carry force along Z, as the floor bolts do. With the roof bonded, the box is one closed cell of the floor, the walls and the roof, 2,365 mm wide and 1,985 mm high (GJ 8.6 x 10¹³ N mm²). With the roof joint neglected it is an open box (GJ 2.8 x 10¹⁰ N mm²).

| LC5a, TC1, diagonal A | Chassis twist | Body share | Largest body torque | Largest bolt force | Chassis peak stress |
|---|---|---|---|---|---|
| Bare chassis (the chassis checks) | 0.439 degree | 0 | | | 78 MPa |
| Body, roof joint neglected | 0.419 degree | 5 % | 0.1 kNm | 2.5 kN | 81 MPa |
| Body, bonded roof (the design) | 0.009 degree | 98 % | 9.5 kNm | 7.8 kN (7.37 kN after its 1 g share of weight, the BDY-16 figure) | 52 MPa |

So report 12's claim holds for the fixed roof: the bonded body takes almost all the twist, and the chassis twists less than 0.01 degree. The closed box is the bound that loads the mounts and the joints most, and the body checks use it. The chassis results do not change, because the chassis checks keep the bare frame. With the body tied on, the chassis stress in LC5b falls from 117 to 25 MPa.

## The rear wall as a diaphragm

With the garage gone, the rear wall is a full panel with one 600 x 450 mm window, so it closes the box's rear end. It racks in shear under the torque the floor bolts put into the box's rear half. The racking force is T / 2h, with T that torque and h the box's height.

The worst case is LC5a with the bonded roof: 12.4 kNm into the rear half, 3.12 kN of racking over 1,730 mm of full panel. The skins carry 0.60 MPa against 22.2 MPa and the joiner 1.34 N/mm against 22.5 N/mm (BDY-20, 0.06).

## The fixed roof

The roof is one 40 mm sandwich panel, 10.6 m², bonded into the roof-to-wall joiner. The inside is 1,950 mm high. The travel height to the top of the solar panels is 2,917 mm.

- The four Sunman panels are bonded to the flat top skin, with no hatch under them. There are no roof hatches (report 18 open question 5). Five opening windows, the Carafan CP700 intake and the bathroom vent ventilate the body.
- The roof weighs 75.6 kg (BD-02), and 107 kg with the 31.2 kg solar array and its adhesive. The uplift check takes 105.5 kg, the roof panel without its insert strips and the array, as the weight it ignores.
- In a 40 m/s uplift the roof takes 5.06 kN, report 12's 6.3 kN on the 13.2 m² lid scaled to this roof's area (assumption). Over 13.6 m of joiner that is 0.37 N/mm against 30 N/mm, half the bond's assumed 2.0 MPa tension strength over its 30 mm leg. The check takes none of the roof's weight off the uplift (BDY-19, 0.01).

## Openings

Ten openings, listed on CT-201 with their sizes and positions. Report 12's rules hold for every one (BDY-18): 300 mm of full wall between neighbouring openings, 150 mm to a panel edge, and nothing within 300 mm of the rear corners. The tightest is exactly at its limit.

- Kerb wall: the kitchen slide-out opening under the bed (from 150 mm behind the front corner), the entry door, an Aussie Traveller DC 1,623 x 622, from 1,953.5 to 2,578.5 mm along the wall, a Dometic S4 500 x 450 window over the bed, the second way out, and a second over the freezer bench.
- Road wall: a Dometic S4 900 x 500 window over the desk, the Thetford cassette service door, 450 x 290, and the bathroom vent.
- Front wall: a Dometic S4 800 x 400 window over the bed, above the spare wheel, and the Carafan CP700 intake beside the spare wheel.
- Rear wall: a Dometic S4 600 x 450 window at the end of the aisle.

Where an opening crosses a chassis station its outrigger-tip mount moves inboard of the frame and the floor joiner runs unbroken.

## Mass

| Line | Item | Mass | Basis | With growth |
|---|---|---|---|---|
| BD-01 | Floor panel 10.61 m² at 8.92 kg/m², with inserts and vinyl | 112.8 kg | Calculated | 123.1 kg |
| BD-02 | Fixed roof 10.61 m² at 7.0 kg/m², no hatches, with its insert strips | 75.6 kg | Calculated | 81.1 kg |
| BD-03 | Side walls, 8.62 m² each less their openings, with inserts | 92.9 kg | Calculated | 100.2 kg |
| BD-04 | Front and rear walls, full height, no rear portal | 54.6 kg | Calculated | 58.6 kg |
| BD-07 | Entry door, Aussie Traveller DC | 25.0 kg | Retailer listing, carried as an estimate | 30.0 kg |
| BD-08 | Floor, corner and roof-to-wall joiners, adhesive, sealant, 32 mount bolts and spreaders | 68.5 kg | Estimate | 82.2 kg |
| BD-09 | Windows, vents, cassette door, CP700 dust fan | 48.2 kg | Mostly estimates | 55.8 kg |
| BD-10 | Two mud flaps with hangers | 9.2 kg | Flap calculated, hanger estimated | 10.4 kg |
| BD-11 | Wiring, plumbing, lighting and hardware | 60.0 kg | Estimate, kept until the systems design | 72.0 kg |
| BD-13 | Fiamma F45s 450 awning and brackets | 31.5 kg | Maker | 31.9 kg |
| | **Body** | **578.3 kg** | | **645.2 kg** |

The solar panels (31.2 kg) are in the roof group, not the body. BD-05 (the garage door) and BD-12 (the pop-top) are gone. The chassis carries the 8.8 kg of nut plates.

## Results

| Check | What | Result | Utilisation |
|---|---|---|---|
| BDY-03 | Floor under a foot, with bearing | Skin 22.3 MPa, bearing 0.20 MPa of 0.70 MPa | 0.30 |
| BDY-04 | Floor edge between outriggers 900 mm apart | Core 0.076 MPa | 0.13 |
| BDY-06 | Side wall in a 0.5 kPa wind | Skin 4.7 MPa | 0.19 |
| BDY-07 | Fixed roof with the solar array, 3 g | Skin 3.6 MPa | 0.14 |
| BDY-09 | Roof deflection at 1 g (reported) | 5.5 mm of 15.8 mm | |
| BDY-10 | Wall deflection in wind (reported) | 18.1 mm of 19.5 mm | |
| BDY-11 | Inserts: bed ledgers, awning brackets | 0.31 kN of 0.85 kN | 0.36 |
| BDY-13 | Body share of LC5a (reported) | 98 % with the bonded roof, 5 % with the roof joint neglected | |
| BDY-14 | Skins and bonded joints in twist | 1.0 N/mm of 22.5 N/mm | 0.04 |
| BDY-16 | Body mounts, M12 into nut plates | 7.37 kN of 23.3 kN | 0.32 |
| BDY-18 | Opening spacing | Every rule met, the tightest by 0 mm | |
| BDY-19 | Roof-to-wall joint in a 40 m/s uplift | 0.37 N/mm of 30 N/mm | 0.01 |
| BDY-20 | Rear wall as the rear diaphragm | 1.34 N/mm of 22.5 N/mm | 0.06 |

The floor under a foot also deflects 4.5 mm against 5.6 mm (span/200, reported in `build/body/body.json`).

## What the engineer must check

1. The load cases, the planning method (one-way spans with an effective width), and the deflection limits.
2. The twist sharing. The bonded roof puts 98 % of LC5a in the body. A finite element model of the body and frame, or a twist test of the finished trailer, settles it. The mount forces depend on it.
3. The M12 nut-plate mounts: the 7.37 kN worst bolt, the nut plate's welds inside the 3 mm raiser, and the floor's pull-through under the spreader.
4. The roof-to-wall joiner: the bond in tension in uplift, and its shear in twist.
5. The inserts, by pull tests, above all the bed ledger fixings.
6. The skin data (woven roving at 14 GPa and 200 MPa, XPS shear strength 0.25 MPa), which no maker publishes for these panels.

## Assumptions made for the design

Each is in TRAILER.md's assumptions list with its source.

- The bonded roof acts fully with the walls (the upper bound), and the lower bound neglects the roof joint.
- Foam cores have a compressive modulus of 2.5 times their shear modulus, for the wrinkling stress.
- MS polymer: 1.5 MPa in shear and 2.0 MPa in tension in the joiners, each used at half.
- The roof uplift at 40 m/s is report 12's 6.3 kN scaled by area to 5.06 kN.
- The bed ledgers on the front and kerb walls carry the whole 255 kg bed at 3 g.
- The M12 8.8 mount works at up to a third of its ultimate tension. The floor's top skin punches through at 60 MPa and the PVC insert at 6 MPa.
- The Fiamma F45s 450 awning stands within 100 mm of the wall.

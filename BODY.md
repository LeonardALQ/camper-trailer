# Body: design (planning level)

Status: proposal, revision C, 21 Nov 2026. DRAFT, not for construction until the engineer reviews it. This is the body's design basis as report 02 asks: the panels, the load cases with their criteria and sources, the joints, the mounting, the twist sharing, the roof, the openings, the results and what the engineer must check. It starts from research report 12 and changes it only where a check failed or the layout asks for it. The data is `data/body/body.yaml`, the checks `cad/body.py`, the solids `cad/body_model.py`, and the mass lines are in `data/assemblies/trailer.yaml`. Drawings CT-201 (shell), CT-202 (joints), CT-203 (insert map) and CT-301 (body to chassis) show it.

## What changed in revision C, 21 Nov 2026

Revision C is the body of the home trailer, TRAILER.md revision J. Revision B, the LandCruiser 79 trailer with the bed across the front, is in the git history.

- The inside is 2,000 mm high in place of 1,950 mm (decision H1a), so the walls are 2,000 mm tall.
- The rear wall has a door, D2, an Aussie Traveller DC in a 625 x 1,753 mm cut-out into the wet room (H4). The wall keeps 1,335 mm of full panel and still closes the box (BDY-20).
- The front edges are rounded, 150 mm at the roof and 250 mm on the verticals, in bonded GRP corner pieces (H12).
- 17 openings in place of 10: four Dometic S4 windows, the two doors, the cassette door, four fan sleeves, the extract, two cowls, the fresh-air intake hood, the rinse box and the relief valve (BDY-18).
- The lift bed's four rails screw into RHS 40 x 20 x 3 aluminium hardpoints laid in the side wall cores, in place of ledgers (BDY-11).
- An SHS 20 x 20 x 1.6 aluminium stiffener bonded upright in each side wall's living-zone bay keeps the wind deflection at 18.6 mm against 20.0 mm (BDY-10).
- A moulded GRP tray covers the wet room floor, and vinyl covers only the rest.
- The mounts are checked at the 3,500 kg plate (H2).
- The body weighs 618.3 kg, 689.7 kg with growth, with both doors and their steps.
- No check limit changed, and no estimate changed to pass a check.

Terms. A sandwich panel is two thin skins bonded to a light core. D is its bending stiffness per metre width. Wrinkling is a local buckle of a compressed skin into the core. An insert is a dense strip laid into the core where a fixing goes. The body's share of the twist is the part of the bare chassis twist that the body removes when it is bolted on.

## Panels

| Panel | Build-up | Mass | D | Wrinkling |
|---|---|---|---|---|
| Floor, 30 mm | Two 2.0 mm woven roving polyester skins (48 % glass) on 26 mm Divinycell H80 PVC | 8.92 kg/m² (calculated) | 11.0 kNm²/m | 147 MPa |
| Side and rear walls, 35 mm | Two 1.5 mm gelcoat GRP skins (Optiplan Polydet) on 32 mm XPS | 6.0 kg/m² (scaled from the maker) | 5.5 kNm²/m | 51 MPa |
| Front wall, 35 mm | 2.0 mm outer and 1.5 mm inner Polydet skins on 31.5 mm XPS, against stones | 6.7 kg/m² (calculated) | 5.7 kNm²/m | 49 MPa |
| Fixed roof, 40 mm | 2.0 mm top and 1.5 mm bottom Polydet skins on 36.5 mm XPS of about 36 kg/m³ | 7.0 kg/m² (calculated) | 7.5 kNm²/m | 49 MPa |

The floor, both side walls and the roof are one piece each. The skins and cores use report 12's data, with the woven roving at 14 GPa and 200 MPa, below the published figures (assumption). The wrinkling stresses take the core's compressive modulus as 2.5 times its shear modulus (assumption). A person's foot governs the floor.

## Load cases and criteria

The cases follow report 11 and CHASSIS.md. Each panel is checked as a one-way span with an effective width of the load patch plus half the span (report 12 section 3).

| Case | Body load | Criterion | Source |
|---|---|---|---|
| LC1, 1 g | A foot of 100 kg on 100 x 150 mm, the roof with the solar array | Deflection: floor span/200, roof span/150 (reported) | Report 12, the engineer sets the limits |
| LC2, 3 g | A foot, the floor edge at 160 kg/m², the roof with the array | Skins at half their ultimate and half the wrinkling stress, cores at half their shear strength, bearing at half the core's compressive strength | ISO 12215-5 for the skins, report 12 for the rest |
| Wind | 0.5 kPa on a side wall, floor to the roof joiner | As LC2, and deflection span/100 (reported) | Report 12 |
| Wind, 40 m/s | 5.06 kN of uplift on the roof | Half the bond's tension strength over the joiner's width | Report 12, scaled to the roof's 10.6 m² |
| LC3, LC4 | 0.8 g braking, 0.5 g sideways, on the mounts | Mount bolt shear and tension | Report 11 |
| LC5a | 13.4 kNm of twist between the axles, travelling | Mounts, skins, joints and the rear wall under the body's share | Report 11, report 12 section 4 |
| LC5b | A corner steady wound to 875 kg at tare, parked | As LC5a | Report 11 |
| Inserts | The lift bed's rail screws at 1.5 times the 264 kg bed at night, the awning's roof brackets at 3 g | Half the rated load, then a pull test (LR-09) | Report 02 MAT-05 |

For LC5a and LC5b the checks take the larger of two bounds on the roof joint: the bonded roof carries shear and the body is a closed box, or the roof joint is neglected and the body is an open box. The chassis checks stay on the bare frame (CHASSIS.md), so they still hold if the mounts loosen.

## Joints

Every panel edge bonds into an aluminium extrusion with MS polymer, with a bead inside and out (CT-202).

- Floor joiners round the floor edge, 1.4 kg/m. The wall foot sits in the joiner, and the joiner sits on the bearer strip over the outrigger tips.
- Corner joiners at the two rear vertical corners, 2.0 kg/m. At the front the rounded GRP corner pieces bond to both panels in their place.
- A roof-to-wall joiner round the wall tops, 1.65 kg/m. The roof bonds into it on a 30 mm leg.
- The lift bed's rails screw into the hardpoints in the side walls. The partition bonds to the wet room tray's upstand, both walls and the ceiling, and adds a diaphragm at X 5,195.
- Every cut edge is sealed with resin or an edge insert. Cut-out corners are radiused, 90 mm at the tops of the doors.

Under the body's share of LC5a the shear flow in a joiner leg's bond is 0.87 N/mm against 22.5 N/mm, and the skins carry 0.22 to 0.29 MPa against 22 to 58 MPa (BDY-14).

## Mounting

The body bolts to the chassis through the EPDM-faced HDPE bearer strip at every station: one bolt into each raiser and one into each outrigger tip, 32 mounts at the 8 stations. The body is not bonded to the steel (report 12 option B).

- Each mount is an M12 8.8 hot-dip galvanised bolt into a 10 mm nut plate, 80 x 44 mm, welded inside the raiser or the outrigger tip before galvanising (CH-P14). On the floor it bears on a bonded 100 x 100 x 3 mm aluminium spreader over a high-density PVC insert and a GRP crush tube.
- The worst bolt carries 6.67 kN of tension under LC5a, with TC2's 1,793 kg of body and contents scaled by 1.125 to the plate. The bolt works at 0.29 of a third of its ultimate tension, the plate at 0.16 in bending, its welds at 0.09 and the floor's pull-through at 0.12 (BDY-16). Shear is 0.44 kN per bolt in LC3 braking.
- Report 12's Lindapter Hollo-Bolt HB10 would work at 0.78 of its 8.5 kN safe load, so the nut plate is the design.

The tension comes from the body holding the chassis against its own twist, so it is real only while the body stays stiff. A weighed and pull-tested sample replaces these planning numbers.

Isolation and sealing (MAT-04): galvanised steel touches only the HDPE strip and the bolt. The crush tube keeps aluminium off the steel. Duralac goes on every faying surface, and a nylon washer and sleeve on every bolt where an extrusion sits over steel. MS polymer seals every hole. Each outrigger tip is shimmed to within 2 mm of the raiser plane, and every bolt is re-torqued after the first rough trip (FAIL-03).

## Twist sharing

The frame model takes the body as a torsion box on the centreline, tied at every station to both raisers by posts that carry force along Z, as the floor bolts do. With the roof bonded the box is one closed cell, 2,365 mm wide and 2,035 mm high (GJ 9.0 x 10¹³ N mm²). With the roof joint neglected it is an open box (GJ 2.8 x 10¹⁰ N mm²).

| LC5a, TC1, diagonal A | Chassis twist | Body share | Largest body torque | Largest bolt force | Chassis peak stress |
|---|---|---|---|---|---|
| Bare chassis (the chassis checks) | 0.400 degree | 0 | | | 77 MPa |
| Body, roof joint neglected | 0.377 degree | 6 % | 0.1 kNm | 2.6 kN | 71 MPa |
| Body, bonded roof (the design) | 0.008 degree | 98 % | 8.4 kNm | 7.2 kN, 6.67 kN after its 1 g share of weight | 49 MPa |

The bonded body takes almost all the twist. The closed box loads the mounts and joints most, so the body checks use it, and the chassis checks keep the bare frame, which carries 113 MPa at worst in LC5b without the body's help.

## The rear wall as a diaphragm

The rear wall closes the box's rear end and racks in shear under the torque the floor bolts put into the box's rear half. The racking force is T / 2h, with T that torque and h the box's height. The rear door's cut-out leaves 1,335 mm of full panel. The worst case is LC5a with the bonded roof: 12.0 kNm into the rear half, 2.94 kN of racking. The skins carry 0.73 MPa against 22.2 MPa and the joiner 1.26 N/mm against 22.5 N/mm (BDY-20, 0.06), so the door needs no extra posts or header.

## The roof

The roof is one 40 mm sandwich panel, 10.6 m², bonded into the roof-to-wall joiner, with no hatches. The four Sunman panels are bonded to its flat top skin, 70 mm toward the road edge, and the Fiamma F80s 400 awning's case sits on its kerb edge on five angle brackets screwed into an insert strip. The case's top, 3,078 mm up, sets the travel height.

- The roof weighs 75.6 kg (BD-02), and about 107 kg with the solar array.
- In a 40 m/s uplift it takes 5.06 kN, report 12's 6.3 kN on the old lid scaled to this roof's area (assumption). Over 13.6 m of joiner that is 0.37 N/mm against 30 N/mm, half the bond's assumed 2.0 MPa tension strength over its 30 mm leg (BDY-19, 0.01).
- The rounded front edges are curved GRP sandwich pieces bonded over the panel ends, about 6 kg net of the joiners and strips they replace (research report 25 section 2).

## Openings

17 openings, listed on CT-013 and drawn on CT-011. Report 12's rules hold for every one (BDY-18): 300 mm of full wall between neighbouring openings, 150 mm to a panel edge and the roof, and nothing within 300 mm of the rear corners. Doors open outward, and both meet VSB1 13.2.1. The tightest openings are exactly at their limits.

- Kerb wall: window W1 (S4 900 x 600, the second way out), the entry door D1 (DC 1,750 x 622), fan A of the first e2 pair high over the dryer, and the cassette door.
- Road wall: window W2 (S4 900 x 450), the fresh-air intake hood, the Combi's cowl, the hood's cowl, window W4 (S4 500 x 450), fan B of the second pair low in the sink cabinet, and window W6 (S4 500 x 450, frosted).
- Front wall: fans C and D low beside the desk.
- Rear wall: the rear door D2, the rinse box, the relief valve and the wet room extract.

Glands of 60 mm or less are not openings. Where an opening crosses a chassis station, its outrigger-tip mount moves inboard of the frame and the floor joiner runs unbroken.

## Mass

| Line | Item | Mass | Basis | With growth |
|---|---|---|---|---|
| BD-01 | Floor panel 10.61 m², inserts, vinyl outside the wet room | 109.3 kg | Calculated | 118.9 kg |
| BD-02 | Fixed roof 10.61 m², no hatches, insert strips | 75.6 kg | Calculated | 81.1 kg |
| BD-03 | Side walls, less their openings, with inserts | 95.7 kg | Calculated | 103.2 kg |
| BD-04 | Front and rear walls, less their openings | 52.8 kg | Calculated | 56.7 kg |
| BD-07, BD-15 | Entry and rear doors, Aussie Traveller DC with pleated blinds | 42.0 kg | Listing, carried as an estimate | 50.4 kg |
| BD-16 | Two fold-out steps | 30.0 kg | Estimate | 36.0 kg |
| BD-08 | Joiners, adhesive, sealant, 32 mount bolts and spreaders | 75.0 kg | Estimate | 90.0 kg |
| WN-01 to WN-05 | Four S4 windows and two blackout covers | 28.5 kg | Maker, covers estimated | 28.7 kg |
| BD-14, BD-18 | Rounded front edges, wall stiffeners | 7.2 kg | Estimate, calculated | 8.6 kg |
| BD-10, BD-17 | Mud flaps with hangers, cassette door | 10.7 kg | Mostly calculated | 12.2 kg |
| BD-11 | Wiring, plumbing, lighting and hardware | 60.0 kg | Estimate, kept until the fit-out | 72.0 kg |
| BD-13 | Fiamma F80s 400 awning on the roof, and its brackets | 36.5 kg | Maker, brackets estimated | 37.0 kg |
| | Body | 618.3 kg | | 689.7 kg |

The solar panels are in the roof group, the wet room tray in the wet room group, and the 8.8 kg of nut plates in the chassis.

## Results

| Check | What | Result | Utilisation |
|---|---|---|---|
| BDY-03 | Floor under a foot, with bearing | Skin 22.3 MPa, bearing 0.20 of 0.70 MPa | 0.30 |
| BDY-04 | Floor edge between outriggers 900 mm apart | Core 0.076 MPa | 0.13 |
| BDY-06 | Side wall, 2,000 mm, in a 0.5 kPa wind | Skin 5.0 MPa | 0.20 |
| BDY-07 | Fixed roof with the solar array, 3 g | Skin 3.6 MPa | 0.14 |
| BDY-09 | Roof deflection at 1 g (reported) | 5.5 mm of 15.8 mm | |
| BDY-10 | Wall deflection in wind, with the stiffeners | 18.6 mm of 20.0 mm | |
| BDY-11 | Lift-bed rail screws, awning bolts | 0.12 kN of 1.50 kN, 0.30 kN of 10.0 kN | 0.08 |
| BDY-13 | Body share of LC5a (reported) | 98 % with the bonded roof, 6 % without | |
| BDY-14 | Skins and bonded joints in twist | 0.87 N/mm of 22.5 N/mm | 0.04 |
| BDY-16 | Body mounts, M12 into nut plates | 6.67 kN of 23.3 kN | 0.29 |
| BDY-18 | Opening spacing, 17 openings | Every rule met, the tightest by 0 mm | |
| BDY-19 | Roof-to-wall joint in a 40 m/s uplift | 0.37 N/mm of 30 N/mm | 0.01 |
| BDY-20 | Rear wall with its door, as the rear diaphragm | 1.26 N/mm of 22.5 N/mm | 0.06 |

## What the engineer must check

1. The load cases, the planning method (one-way spans with an effective width) and the deflection limits.
2. The twist sharing. A finite element model of the body and frame, or a twist test of the finished trailer, settles the 98 %, and the mount forces depend on it.
3. The M12 nut-plate mounts: the worst bolt, the nut plate's welds inside the raiser, and the floor's pull-through under the spreader.
4. The roof-to-wall joiner and the rounded corner pieces: the bond in uplift and in twist.
5. The rear wall with its door cut-out as the rear diaphragm.
6. The inserts and hardpoints, by pull tests, above all the lift-bed rail screws and the outdoor unit's cradle.
7. The skin data (woven roving at 14 GPa and 200 MPa, XPS shear strength 0.25 MPa), which no maker publishes for these panels.

## Assumptions made for the design

- The bonded roof acts fully with the walls (the upper bound), and the lower bound neglects the roof joint.
- Foam cores have a compressive modulus of 2.5 times their shear modulus, for the wrinkling stress.
- MS polymer: 1.5 MPa in shear and 2.0 MPa in tension in the joiners, each used at half.
- The roof uplift at 40 m/s is report 12's 6.3 kN scaled by area to 5.06 kN.
- The lift bed's 32 rail screws carry 1.5 times the 264 kg bed at night, two people included.
- The M12 8.8 mount works at up to a third of its ultimate tension. The floor's top skin punches through at 60 MPa and the PVC insert at 6 MPa.
- Nothing on a side wall stands more than 40 mm proud of its skin: the S4 frames 21 mm (Dometic's drawing), the hoods, cowls and flush-mounted inlet boxes 30 mm and the entry door's handle 40 mm (est.). The awning's case sits on the roof 5 mm inside the kerb wall's skin.

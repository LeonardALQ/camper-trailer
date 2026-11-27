# Body: design (planning level)

Status: proposal, revision C of 21 Nov 2026, updated 22 Nov 2026 for the fit-out's supports (H27), BD-11's routed runs (H28) and the floor round its cut-outs (BDY-26), and 23 Nov 2026 for the 4,000 kg plate (H2 as amended): the mounts and the twist at the plate's masses and the walls' strength wind at 42 m/s, and 25 Nov 2026 for the strength wind worked out from STB-04's overturning speed, 42.4 m/s at the masses then, 42.5 m/s with the fresh tanks on their bearers and 42.4 m/s again with the XT hinge crossmembers RHS 150 x 100 x 6 and 370 L of water (26 Nov 2026), whose stiffer frame also takes more of the twist, and 42.5 m/s with the 375 L those tanks hold. DRAFT, not for construction until the engineer reviews it. This is the body's design basis as report 02 asks: the panels, the load cases with their criteria and sources, the joints, the mounting, the twist sharing, the roof, the openings, the results and what the engineer must check. It starts from research report 12 and changes it only where a check failed or the layout asks for it. The data is `data/body/body.yaml`, the checks `cad/body.py`, the solids `cad/body_model.py`, and the mass lines are in `data/assemblies/trailer.yaml`. Drawings CT-201 (shell), CT-202 (joints), CT-203 (insert map) and CT-301 (body to chassis) show it.

## What changed in revision C, 21 Nov 2026

Revision C is the body of the home trailer, TRAILER.md revision J. Revision B, the LandCruiser 79 trailer with the bed across the front, is in the git history.

- The inside is 2,000 mm high in place of 1,950 mm (decision H1a), so the walls are 2,000 mm tall.
- The rear wall has a door, D2, an Aussie Traveller DC in a 625 x 1,753 mm cut-out into the wet room (H4). The wall keeps 1,335 mm of full panel and still closes the box (BDY-20).
- The front edges are rounded, 150 mm at the roof and 250 mm on the verticals, in bonded GRP corner pieces (H12).
- 18 openings in place of 10: four Dometic S4 windows, the two doors, the cassette door, four fan sleeves, the extract, two cowls, the fresh-air intake hood, the rinse box, the relief valve and G2's box of inlets (BDY-18).
- The lift bed's four rails screw into aluminium hardpoints on the inner skin, full wall height, in place of ledgers (BDY-11).
- A stiffener stands behind the kitchen bench on the road side, and two jamb members stand either side of the entry door on the kerb side. They and the four hardpoints are RHS 110 x 19 x 3.5 6060-T5, made to order, bonded to the inner skin with 13 mm of XPS behind them and stood on rigid PVC blocks clear of the joiners' legs, so no metal crosses the core. They hold the wall to 19.7 mm in region B's 25-year wind (AS/NZS 1170.2, H23), against 20.0 mm (BDY-10), and to 18.9 mm as plates with the openings cut out (BDY-24), stand at least 25 mm clear of every opening, gland, insert strip and each other, or share one routed channel with an H200 fill (FIT-07), and keep the inside surface over them and over the joiners at 10.2 °C or more on the design cold night, at ISO 13788's Rsi of 0.25 m²K/W (BDY-22).
- The split's outdoor unit stands on two stays to the chassis, so the rear wall's skin carries none of its weight (BDY-21).
- A moulded GRP tray covers the wet room floor, and vinyl covers only the rest.
- The mounts are checked at the 4,000 kg plate (H2 as amended 23 Nov 2026).
- The body weighs 640.5 kg, 713.6 kg with growth, with both doors and their steps.
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
| Wind, parked | A side wall, floor to the roof joiner. Terrain category 2 at 3 m, Cp,e 0.7 and Cp,i -0.3. Region B's 25-year 39 m/s gives 0.76 kPa net, and 42.5 m/s, over the highest speed that tips the parked trailer, 1.08 kPa | Skins at half their ultimate, members at yield over 1.5 and the XPS behind them at half its compressive strength, at 1.08 kPa. Deflection span/100 at 0.76 kPa (reported) | AS/NZS 1170.2 Tables 3.1, 4.1, 5.1(A), 5.2(A), H23 |
| Wind, 40 m/s | 5.06 kN of uplift on the roof | Half the bond's tension strength over the joiner's width | Report 12, scaled to the roof's 10.6 m² |
| LC3, LC4 | 0.8 g braking, 0.5 g sideways, on the mounts | Mount bolt shear and tension | Report 11 |
| LC5a | 15.1 kNm of twist between the axles at the 4,000 kg plate, travelling | Mounts, skins, joints and the rear wall under the body's share | Report 11, report 12 section 4 |
| LC5b | A corner steady wound to 875 kg at tare, parked | As LC5a | Report 11 |
| Inserts | The lift bed's rail screws at 1.5 times the 264 kg bed at night, the awning's roof bolts at 3 g and with the canopy open in a 60 km/h gust, the outdoor unit's cradle at 3 g down, 0.8 g along and 0.5 g sideways | Half the rated load, then a pull test (LR-09) | Report 02 MAT-05 |
| Cold night | -5 °C outside, 20 °C inside, the dew point held at 6 °C, -1.7 °C on the generators | Inside surface over each wall member, to its ends, at least 4 K above the dew point, at ISO 13788's Rsi of 0.25 m²K/W | Research report 19 section 5, ISO 13788 clause 4.4.1 |

For LC5a and LC5b the checks take the larger of two bounds on the roof joint: the bonded roof carries shear and the body is a closed box, or the roof joint is neglected and the body is an open box. The chassis checks stay on the bare frame (CHASSIS.md), so they still hold if the mounts loosen.

## Joints

Every panel edge bonds into an aluminium extrusion with MS polymer, with a bead inside and out (CT-202).

- Floor joiners round the floor edge, 1.4 kg/m. The wall foot sits in the joiner, and the joiner sits on the bearer strip over the outrigger tips.
- Corner joiners at the two rear vertical corners, 2.0 kg/m. At the front the rounded GRP corner pieces bond to both panels in their place.
- A roof-to-wall joiner round the wall tops, 1.65 kg/m. The roof bonds into it on a 30 mm leg.
- The lift bed's rails screw through the inner skin into the hardpoints behind it. The partition bonds to the wet room tray's upstand, both walls and the ceiling, and adds a diaphragm at X 5,195.
- Every cut edge is sealed with resin or an edge insert. Cut-out corners are radiused, 90 mm at the tops of the doors.

Under the body's share of LC5a the shear flow in a joiner leg's bond is 0.97 N/mm against 22.5 N/mm, and the skins carry 0.24 to 0.32 MPa against 22 to 58 MPa (BDY-14).

## Mounting

The body bolts to the chassis through the EPDM-faced HDPE bearer strip at every station: one bolt into each raiser and one into each outrigger tip, 32 mounts at the 8 stations. The body is not bonded to the steel (report 12 option B).

- Each mount is an M12 8.8 hot-dip galvanised bolt into a 10 mm nut plate, 80 x 44 mm, welded inside the raiser or the outrigger tip before galvanising (CH-P14). On the floor it bears on a bonded 100 x 100 x 3 mm aluminium spreader over a high-density PVC insert and a GRP crush tube.
- The worst bolt carries 7.07 kN of tension under LC5a, with TC2's 1,667 kg of body and contents scaled by 1.190 to the 4,000 kg plate, 1,984 kg. The bolt works at 0.30 of a third of its ultimate tension, the plate at 0.17 in bending, its welds at 0.10 and the floor's pull-through at 0.13 (BDY-16). Shear is 0.49 kN per bolt in LC3 braking.
- Report 12's Lindapter Hollo-Bolt HB10 would work at 0.86 of its 8.5 kN safe load, so the nut plate is the design.

The tension comes from the body holding the chassis against its own twist, so it is real only while the body stays stiff. A weighed and pull-tested sample replaces these planning numbers.

Isolation and sealing (MAT-04): galvanised steel touches only the HDPE strip and the bolt. The crush tube keeps aluminium off the steel. Duralac goes on every faying surface, and a nylon washer and sleeve on every bolt where an extrusion sits over steel. MS polymer seals every hole. Each outrigger tip is shimmed to within 2 mm of the raiser plane, and every bolt is re-torqued after the first rough trip (FAIL-03).

## Twist sharing

The frame model takes the body as a torsion box on the centreline, tied at every station to both raisers by posts that carry force along Z, as the floor bolts do. With the roof bonded the box is one closed cell, 2,365 mm wide and 2,035 mm high (GJ 9.0 x 10¹³ N mm²). With the roof joint neglected it is an open box (GJ 2.8 x 10¹⁰ N mm²).

| LC5a, TC1, diagonal A | Chassis twist | Body share | Largest body torque | Largest bolt force | Chassis peak stress |
|---|---|---|---|---|---|
| Bare chassis (the chassis checks) | 0.181 degree | 0 | | | 69 MPa |
| Body, roof joint neglected | 0.177 degree | 2 % | 0.1 kNm | 1.4 kN | 67 MPa |
| Body, bonded roof (the design) | 0.009 degree | 95 % | 8.8 kNm | 7.68 kN, 7.07 kN after its 1 g share of weight | 47 MPa |

The bonded body takes almost all the twist. The closed box loads the mounts and joints most, so the body checks use it, and the chassis checks keep the bare frame, which carries 117 MPa at worst in LC5b without the body's help.

## The rear wall as a diaphragm

The rear wall closes the box's rear end and racks in shear under the torque the floor bolts put into the box's rear half. The racking force is T / 2h, with T that torque and h the box's height. The rear door's cut-out leaves 1,335 mm of full panel. The worst case is LC5a with the bonded roof: 12.2 kNm into the rear half, 3.01 kN of racking. The skins carry 0.75 MPa against 22.2 MPa and the joiner 1.29 N/mm against 22.5 N/mm (BDY-20, 0.06), so the door needs no extra posts or header.

## The side walls in wind

Each side wall spans 2,000 mm from the floor joiner to the roof-to-wall joiner. The sandwich carries the wind together with seven aluminium members on its inner skin: the four lift-bed hardpoints, a stiffener on the road side behind the kitchen bench (BD-18), and two members either side of the entry door on the kerb side, behind it (BD-19) and in front of it (BD-20). All are RHS 110 x 19 x 3.5 6060-T5, 2.306 kg/m, made to order, because no Australian stockist lists a section under 25 mm deep this stiff. Before the panels are ordered, get an extruder's quote for the die, its 100 kg minimum run and its lead time, and ask for an existing die near this section first (BD-18). The panel maker routs a 19 mm channel into the XPS from the inside and bonds each member into it as the inner skin goes on, so 13 mm of XPS stays between the member and the outer skin. With the tower's sides, the partition and the end walls they bound every bay at no more than 1,067 mm, the gap between the bed's rail pairs, and each stands at least 25 mm clear of every cut-out, gland and insert strip, the bench's, the tower's and the lockers' strips included, so the channels leave XPS between (FIT-07, 25 mm at the tightest). The rule has two exceptions. W1 and W2 sit between the hardpoints, 27 to 28 mm from each, and a Dometic S4's two frames screw to each other through the cut-out and clamp the panel. So each of their sides takes a bonded Divinycell H200 insert, 4.5 MPa in compression ([Diab](https://diab-media.azureedge.net/clwjnze4/diab-divinycell-h-may-2026-rev26-imp.pdf)), that fills the core from the cut-out to the hardpoint in the hardpoint's own channel, so the clamp bears on a solid edge as at every other opening. The other is BD-20, which stands 16.5 mm behind the bed's rear kerb-side hardpoint because it must also keep 25 mm from the entry door's insert strip: the panel maker routs one channel for the pair and bonds an H200 fill between them, which leaves no thin fin of XPS to rout (F5-03). A member on one skin bends about its own centroid, so only its own stiffness is added to the sandwich's, which is conservative.

Each member stands on a rigid PVC bearing block, 20 mm wide across its depth, that carries the bed's load down to the floor joiner's base. The floor joiner wraps the wall's foot, and its inner leg runs 34 mm up the inner skin with its flange (CT-202 detail F). The block raises the member's foot 54 mm above the wall's bottom edge, 20 mm clear of that leg, so no leg overlaps a member. At its head the member stops 10 mm under the wall's 25 mm top insert strip on a 10 mm rigid PVC pad, 19 mm below the roof joiner's leg. Block and pad each take the member's wind shear into its joiner through a spigot in the member's hollow end.

- The load is AS/NZS 1170.2's for a parked trailer in terrain category 2 at 3 m, with Cp,e 0.7 on the windward wall and Cp,i -0.3 inside. Decision H23 sets region B's 25-year wind, 39 m/s times 0.91, 0.76 kPa net, for the deflection, because region B, the Queensland coast, is non-cyclonic and Leonard will camp there. The strength wind is 42.5 m/s, 1.08 kPa net: BDY-19's 40 m/s, raised to cover the highest speed that tips the unhitched trailer, just over 42.4 m/s with a box's force coefficient at the trailer's masses, rounded up to 0.1 m/s (STB-04, cad/trailer.py strength_wind). It follows the masses, so it moves when they do.
- In a bay of plain panel the wall deflects 19.7 mm against 20.0 mm, and 30.1 mm without the members (BDY-10). The 20 mm is span/100, report 12's planning limit for the engineer to set. The skins reach 10.8 MPa, a quarter of half their ultimate, each member 41 MPa against 73 MPa, 0.56, and the XPS behind it 0.004 MPa against 0.15 MPa (BDY-06).
- BDY-10 and BDY-06 spread each member over a full bay and leave the openings out, so BDY-24 and BDY-25 take each side wall as a Mindlin plate from the front wall to the rear wall, every opening cut out with its window's or door's wind load on its edges, and each member a beam with its own bending, shear and torsion. The wall between W1 and the entry door needs both the bed's rear hardpoint and BD-20: with the hardpoint alone the door's front edge would deflect 28.8 mm. With both, the kerb wall deflects at most 18.9 mm, at the door's front edge (BDY-24). In the ultimate wind the worst member works at 0.57, the skins at 0.31 and the core at 0.73 of half its shear strength, both read 50 mm or more from the cut-outs' corners, which the model cuts square (F5-02), and the blocks carry 441 N of end shear at 0.13 (BDY-25). The road wall, with the kitchen tower's sides as supports, deflects at most 7.1 mm.
- Strapped down on its lashing points (STB-05), the trailer stands in stronger winds than tip it unhitched. At region B's 500-year gust at 3 m, STB-05's 51.9 m/s, a plain bay's members work at 0.84 and its skins at 0.63 (BDY-06), and the plates reach 1.08, on the core's shear at the floor just behind the entry door, so the core keeps a factor of 1.85 on its strength there.
- On research report 19's design cold night, -5 °C outside and 20 °C inside, with ISO 13788's inside surface resistance of 0.25 m²K/W for condensation, which allows for furniture against the wall, a two-dimensional conduction model of the wall at a member puts the inside surface over it at 10.7 °C at mid-length and the member, with the rails screwed to it, at 10.4 °C. Taken across each member as it stands, with W1's and W2's side inserts and the windows beyond them, the doors' insert strips and the doors, and the two members behind the bed 16.5 mm apart with the H200 fill between them, the coldest is 10.5 °C. Along the member its ends lose heat to the joiners, taken at the outside air as a bound: the surface is 10.2 °C at the foot and 10.2 °C at the head, against the dew point of 6 °C plus report 19's 4 K (BDY-22). The plain wall's surface is 14.9 °C. On the generators, ahead of the drawbar or behind the trailer, e2 fans C and D stop, fans A and B and the RESPA-CF2 run, and the dew point falls to -1.7 °C. Off the kerb side fans A and B stop too and the RESPA-CF2 runs alone, -1.2 °C (F5-04).
- The aluminium joiners run near the outside air. Every joiner's inside face, the floor joiner's flange included, is covered with 15 mm of closed-cell foam under the lining and the skirting, which keeps the surface at 10.8 °C even with the joiner at the outside air (BDY-22). Report 19's 10 mm cover would leave 8.3 °C on the same bound.
- On ISO 6946's heat-loss film the 13.6 m of members add 1.49 W/K, 4.0 % of the bare panels' 36.8 W/K, beside report 19's 7.3 W/K for the joiners, mount bolts and inserts.

## The outdoor unit's cradle

The split's outdoor unit and its cradle, 46 kg, stand 194 mm behind the rear wall's road half, over the rear overhang. Two RHS 40 x 20 x 3 stays (AC-04) run from the cradle's wall-side corners down the wall to brackets on the rear crossmember and carry its weight, 0.68 kN each at 3 g, a third of their buckling load (BDY-21, 0.33). Four M8 bolts on backing pads in an insert strip hold it to the wall against its overturning moment, a pull away from the wall and the sideways load: at most 0.37 kN of tension and 0.06 kN of shear a bolt, 0.02 of half their rated loads.

## The roof

The roof is one 40 mm sandwich panel, 10.6 m², bonded into the roof-to-wall joiner, with no hatches. The four Sunman panels are bonded to its flat top skin, 70 mm toward the road edge, and the Fiamma F80s 400 awning's case sits on its kerb edge on five angle brackets. Each bracket bolts through the roof's kerb-edge insert strip with two Panelok APLB-1024 bolts and APLN-1016 T-nuts, whose 38.1 to 54.3 mm grip takes the 40 mm roof, the 4 mm bracket and a 2 mm EPDM pad under it, 46 mm, rated 14 kN in shear and 20 kN in tension (Rivtec). Nylon shoulder washers and Duralac on the shanks keep the zinc-plated steel off the aluminium. The worst bolt carries 0.32 kN with the canopy open in a 60 km/h gust and its legs pegged, against half of 20 kN (BDY-11). The case's top, 3,078 mm up, sets the travel height.

- The roof weighs 75.6 kg (BD-02), and about 107 kg with the solar array.
- In a 40 m/s uplift it takes 5.06 kN, report 12's 6.3 kN on the old lid scaled to this roof's area (assumption). Over 13.6 m of joiner that is 0.37 N/mm against 30 N/mm, half the bond's assumed 2.0 MPa tension strength over its 30 mm leg (BDY-19, 0.01).
- The rounded front edges are curved GRP sandwich pieces bonded over the panel ends, about 6 kg net of the joiners and strips they replace (research report 25 section 2).

## Openings

18 openings, listed on CT-013 and drawn on CT-011. Report 12's rules hold for every one (BDY-18): 300 mm of full wall between neighbouring openings, 150 mm to a panel edge and the roof, and nothing within 300 mm of the rear corners. Doors open outward, and both meet VSB1 13.2.1. The tightest openings are exactly at their limits.

- Kerb wall: window W1 (S4 900 x 600, the second way out), the entry door D1 (DC 1,750 x 622), G2's box of inlets, fan A of the first e2 pair high over the dryer, and the cassette door.
- Road wall: window W2 (S4 900 x 450), the fresh-air intake hood, the Combi's cowl, the hood's cowl, window W4 (S4 500 x 450), fan B of the second pair low in the sink cabinet, and window W6 (S4 500 x 450, frosted).
- Front wall: fans C and D low beside the desk.
- Rear wall: the rear door D2, the rinse box, the relief valve and the wet room extract.

Glands of 60 mm or less are not openings. G2's 310 x 120 mm box of inlets is larger, so it counts as one. Where an opening crosses a chassis station, its outrigger-tip mount moves inboard of the frame and the floor joiner runs unbroken.

## The floor's cut-outs

Three cut-outs in the floor are over 60 mm, the services' Roxtec transit frames (data/services.yaml `cutouts`, review I2-27): G9, 68 x 167 mm at X 3,400 between the chair space and the aisle, at Roxtec's 60 x 120 mm packing with its C wedge's room (I2-33), G15, 167 x 128 mm at X 5,070 in the corner between the aisle's end and the partition under the MultiPlus-II, at Roxtec's 120 x 120 mm packing with its C wedge's room inside it (I2-33), and G20, 128 x 167 mm at X 5,077 in the plinth's end slot, at Roxtec's 120 x 120 mm packing with its C wedge's room across the trailer (I2-33). G15 sits inboard of the road raiser, 2 mm from its bearer strip, and G9's edge takes 31 mm of that strip, its frame standing on the floor. G20 lies over the gap between the kerb raiser and the rear tank, where its raiser cables come down beside the raiser and enter it through its inner web (CHASSIS.md, CHS-10), and its edge takes 8 mm of the raiser's 50 mm bearer strip over its 128 mm length. TRAILER.md open point 11 assumes a high-density insert round each cut-out. The design makes it Divinycell H200, 30 mm wide round the cut-out (est.), wide enough for the frame's 8 mm rim and its screws, laid into the core by the floor maker, at Diab's minimum 3.2 MPa in shear and 4.5 MPa in compression. Every cut-out's corners are radiused 10 mm (est.).

BDY-26 checks the floor round each one with BDY-03's foot standing beside it and BDY-04's 160 kg/m², both at 3 g on the one-way span between the raisers. The strip under the foot loses the cut-out's length from its effective width, and the skins and the insert at the cut-out's edge take Kirsch's 3.0, the factor of a round hole in a plate, a lower bound for a radiused rectangular cut-out that its bonded frame and insert stiffen (est.). The H80 at the insert's outer edge takes the same field fallen off as Kirsch's solution falls, the cut-out taken as a hole of half its mean side. Where G20's edge lies over the bearer strip, the check takes the strip away under the cut-out, so the floor bridges the gap along the raiser with a foot at its middle and bears on the insert at the gap's ends. G9 governs, at 0.81, and G20 works at 0.71, both with the insert in shear while it bridges the gap. G15 works at 0.51, on the H80 beyond the insert. The criteria are BDY-03's: skins at half their ultimate and half the wrinkling stress, cores at half their shear strength and bearing at half the compressive strength.

## Mass

| Line | Item | Mass | Basis | With growth |
|---|---|---|---|---|
| BD-01 | Floor panel 10.61 m², inserts, vinyl outside the wet room | 109.3 kg | Calculated | 118.9 kg |
| BD-02 | Fixed roof 10.61 m², no hatches, insert strips | 75.6 kg | Calculated | 81.1 kg |
| BD-03 | Side walls, less their openings, with inserts | 96.1 kg | Calculated | 103.7 kg |
| BD-04 | Front and rear walls, less their openings | 52.8 kg | Calculated | 56.7 kg |
| BD-07, BD-15 | Entry and rear doors, Aussie Traveller DC with pleated blinds | 42.0 kg | Listing, carried as an estimate | 50.4 kg |
| BD-16 | Two fold-out steps | 30.0 kg | Estimate | 36.0 kg |
| BD-08 | Joiners and their foam covers, adhesive, sealant, 32 mount bolts and spreaders | 75.8 kg | Estimate | 91.0 kg |
| WN-01 to WN-05 | Four S4 windows and two blackout covers | 28.5 kg | Maker, covers estimated | 28.7 kg |
| BD-14, BD-18 to BD-20 | Rounded front edges, the road wall's stiffener, the entry door's two jamb members | 19.5 kg | Estimate, calculated | 21.6 kg |
| BD-10, BD-17 | Mud flaps with hangers, cassette door | 10.7 kg | Mostly calculated | 12.2 kg |
| BD-11 | Wiring, plumbing and hardware, line by line, with 19.7 kg for the routed runs above their first estimates, 2.5 kg for SVC-12's six cable supports, 2.5 kg for the bench's cleats and the 230 V's conduits under the floor (I2-36) and 0.7 kg left unassigned (the lamps are LG-01) | 63.5 kg | Estimate, kept until the fit-out | 76.2 kg |
| BD-13 | Fiamma F80s 400 awning on the roof, its brackets, bolts and pads | 36.7 kg | Maker, brackets estimated | 37.2 kg |
| | Body | 640.5 kg | | 713.6 kg |

The solar panels are in the roof group, the wet room tray in the wet room group, and the 8.8 kg of nut plates in the chassis.

## Results

| Check | What | Result | Utilisation |
|---|---|---|---|
| BDY-03 | Floor under a foot, with bearing | Skin 22.6 MPa, bearing 0.20 of 0.70 MPa | 0.31 |
| BDY-04 | Floor edge between outriggers 900 mm apart | Core 0.076 MPa | 0.13 |
| BDY-26 | Floor round its three cut-outs with their H200 inserts, and its bearing on the raisers | G9's insert in shear bridging the road raiser's strip, 1.29 MPa of 1.60 MPa | 0.81 |
| BDY-06 | Side wall, 2,000 mm, in the ultimate wind, 1.08 kPa | Skin 10.8 MPa, member 41 MPa of 73 MPa | 0.56 |
| BDY-07 | Fixed roof with the solar array, 3 g | Skin 3.6 MPa | 0.14 |
| BDY-09 | Roof deflection at 1 g (reported) | 5.5 mm of 15.8 mm | |
| BDY-10 | Wall deflection in region B's 25-year wind, 0.76 kPa, with the members | 19.7 mm of 20.0 mm | |
| BDY-11 | Lift-bed rail screws, awning bolts in travel and with the canopy open | 0.12 kN of 1.50 kN, 0.32 kN of 10.0 kN | 0.08 |
| BDY-13 | Body share of LC5a (reported) | 95 % with the bonded roof, 2 % without | |
| BDY-14 | Skins and bonded joints in twist | 0.92 N/mm of 22.5 N/mm | 0.04 |
| BDY-16 | Body mounts, M12 into nut plates | 7.07 kN of 23.3 kN | 0.30 |
| BDY-18 | Opening spacing, 18 openings | Every rule met, the tightest by 0 mm | |
| BDY-19 | Roof-to-wall joint in a 40 m/s uplift | 0.37 N/mm of 30 N/mm | 0.01 |
| BDY-20 | Rear wall with its door, as the rear diaphragm | 1.29 N/mm of 22.5 N/mm | 0.06 |
| BDY-21 | Outdoor unit's cradle: stays to the chassis, wall bolts | 0.68 kN a stay of 2.0 kN, 0.37 kN a bolt of 22.6 kN | 0.33 |
| BDY-22 | Inside surface over the wall members, to their ends, and over the joiners on the cold night, at Rsi 0.25 | 10.2 °C against 10 °C | |
| BDY-24 | Side walls as plates with their openings, in region B's 25-year wind | 18.9 mm of 20.0 mm | |
| BDY-25 | Side walls as plates with their openings, in the ultimate wind | Core shear 0.091 MPa of 0.125 MPa, worst member 42 MPa | 0.73 |
| FIT-07 | Wall members clear of every opening, gland, insert strip and each other, bays within 1,067 mm | 25 mm against 25 mm | |
| BDY-23 | Awning legs at a 10 degree fall on level ground (reported) | 155 mm of reach left (est.) | |

## What the engineer must check

1. The load cases, the planning method (one-way spans with an effective width) and the deflection limits.
2. The twist sharing. A finite element model of the body and frame, or a twist test of the finished trailer, settles the 95 %, and the mount forces depend on it.
3. The M12 nut-plate mounts: the worst bolt, the nut plate's welds inside the raiser, and the floor's pull-through under the spreader.
4. The roof-to-wall joiner and the rounded corner pieces: the bond in uplift and in twist.
5. The rear wall with its door cut-out as the rear diaphragm.
6. The inserts and hardpoints, by pull tests, above all the lift-bed rail screws, the awning's roof bolts and the outdoor unit's cradle bolts, and the cradle's stays and their feet.
7. The wall members' bond to the inner skin, which carries their share of the wind and the bed's rail loads, their blocks and spigots at the joiners, the plate model of the walls with their openings (BDY-24, BDY-25), and the cold-surface model (BDY-22), for example by a thermal image of a finished wall on a cold night.
8. The skin data (woven roving at 14 GPa and 200 MPa, XPS shear strength 0.25 MPa), which no maker publishes for these panels.
9. The floor round its three cut-outs (BDY-26): the H200 inserts' width, the stress concentration at the radiused corners, and the floor's bearing on the kerb raiser's bearer strip beside G20, whose edge lies over 8 mm of it.

## Assumptions made for the design

- The bonded roof acts fully with the walls (the upper bound), and the lower bound neglects the roof joint.
- Foam cores have a compressive modulus of 2.5 times their shear modulus, for the wrinkling stress.
- MS polymer: 1.5 MPa in shear and 2.0 MPa in tension in the joiners, each used at half.
- The roof uplift at 40 m/s is report 12's 6.3 kN scaled by area to 5.06 kN.
- The lift bed's 32 rail screws carry 1.5 times the 264 kg bed at night, two people included.
- The M12 8.8 mount works at up to a third of its ultimate tension. The floor's top skin punches through at 60 MPa and the PVC insert at 6 MPa.
- The wall members act only through their own stiffness, with no composite term through the core. The XPS behind them conducts at 0.035 W/mK and the GRP skins at 0.30 W/mK (est.).
- Nothing on a side wall stands more than 40 mm proud of its skin: the S4 frames 21 mm (Dometic's drawing), the hoods, cowls and flush-mounted inlet boxes 30 mm and the entry door's handle 40 mm (est.). The awning's case sits on the roof 5 mm inside the kerb wall's skin.

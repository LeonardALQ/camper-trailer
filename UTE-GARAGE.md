# UTE-GARAGE: the bike box on the Ford Ranger Super Duty

Revision G, 23 Nov 2026: with the bikes out the ramp travels forward along the Tuareg's bay, so the empty box meets Ford's centre of gravity window held to its 800 kg row (UTE-07, review I2-42), and the box's mass has one figure, 438.2 kg, the parts list's and the model's (I2-49). Revision F, 23 Nov 2026: the box on a near-new Ford Ranger Super Duty single cab chassis in place of the LandCruiser 79 (Leonard, 22 Nov 2026). It bolts to Ford's eight body mounting pads, flexible at the first pair and rigid at the rest, and follows the rules of Ford's body equipment mounting manual for the Super Duty (BEMM, 03/2026, pages as printed). Revision E, 22 Nov 2026: revision D with Leonard's welding gas, filler and abrasives priced, his own weld test before he welds the box, and a proof load on each of Toyota's deck mount brackets. Revision D, 21 Nov 2026: revision C of 20 Nov with the wheel tubs moved out and a flare over each rear tub for the Lovells Elite kit's wider rear track (decisions H18 and H19). Build document for Leonard, who builds the box himself and does not have it certified (decision H25, 22 Nov 2026). Parts list `data/ute/box-parts.yaml`, measurements BOX-01 to BOX-20 and VEH-28 in `data/measurements.yaml`, model `data/assemblies/ute-garage.yaml` and `data/ute/parts/`, drawings CT-701 to CT-704. The site's Bike box page shows the parts list and the checks.

## 1. Purpose and limits

The box carries the Aprilia Tuareg 660 Rally (206 kg) and the Triumph Street Triple 765 (175 kg) side by side, noses forward, 760 mm apart, with about 60 kg of tools. It is locked, sealed against dust and vented for fuelled bikes.

- Body at most 1,960 mm wide, Ford's limit for the single cab with its standard mirrors (BEMM p. 18), and the rear tub flares inside the 2,197 mm span of the truck's mirrors (UTE-09). The body stays 1,850 mm wide. Ford also asks for 28 mm from the cab and 30 mm over its roof (p. 24), the body on every one of its pads (p. 124), 30 mm between the tyre and its guard (p. 122), and no drilling or welding of the frame (p. 155).
- Ford's ratings: GVM 4,500 kg, front axle 1,900 kg, rear axle 2,800 kg, GCM 8,000 kg (p. 33). Ford's window for the added mass's centre of gravity (p. 32, UTE-07 and UTE-08). Box empty under report 17's 440 kg (UGB-01).
- NTC Load Restraint Guide 2018: 0.8 g forward, 0.5 g rearward and sideways, 0.2 g up ([guide, p. 19](https://media.nrspp.org.au/wp-content/uploads/2021/11/06005924/Load-Restraint-Guide-for-light-vehicles-2018.pdf)).
- Ramp at most 20 degrees (report 03).

## 2. The design in brief

A welded aluminium body bolts onto its own aluminium ladder subframe. The subframe stands on Ford's eight body mounting pads, clear of the rail tops, on flexible mounts at the first pair and rigid mounts at the other three, as Ford asks of a body as rigid as a welded box (BEMM p. 124), so the frame twists under the box without loading its walls.

Outside 2,590 x 1,850 x 1,502 mm at the walls, 1,519 mm at the roof's 1:50 crown, and 2,057 mm wide over the rear tub flares. Inside 2,520 x 1,765 x 1,460 mm. Floor 851 mm up laden at GVM, wheel tubs 70 mm high and 1,362 mm apart on Ford's 1,710 mm rear track. The front wall stands 30 mm behind the cab and the barn doors end 101 mm ahead of the tow pin. Rear barn doors open 1,745 x 1,460 mm. A 1,200 x 1,000 mm top-hinged kerb door reaches the Street Triple's kerb strap and the kerb tool chest.

## 3. Materials

| Part | Material, size |
|---|---|
| Walls, front, door skins | 5052-H32 2.5 mm, sheets on end, joints on posts |
| Roof | 5052-H32 1.6 mm on bows crowned 1:50, joints on bows. No step, no kneeling |
| Floor | 5052-H32 4.0 mm, joints on crossmembers |
| Wheel tubs | 5052-H32 3.0 mm |
| Rear tub flares | 5052-H32 2.5 mm, folded |
| Body frame | 6061-T6 SHS 40 x 40 x 3 |
| Door frames | 6061-T6 SHS 25 x 25 x 3 |
| Runners | 6061-T6 RHS 75 x 50 x 3 |
| Crossmembers, outriggers | 6061-T6 SHS 50 x 50 x 3 |
| Mounts | Steel spacers 60 x 50 x 45 mm (51 mm at the rearmost pads), galvanised. Rubber cushions at the first pads |
| Track packers, plates | 5052-H32 5.0 mm |
| Anchor crossmembers | C350L0 RHS 65 x 35 x 4.0, hot-dip galvanised after welding |
| Steel stubs | C350L0 RHS 75 x 50 x 3.0, welded to the front crossmember and galvanised with it |

Buy 6061-T6 with mill certificates from a structural stockist. All Aluminium stocks these tubes only in 6060-T5, which is weaker when welded.

Fasteners: M14 10.9 zinc flake bolts with 50 x 5 mm hardened washers and locknuts at Ford's pads, A4-70 stainless with Tef-Gel through aluminium, G10 pads and shoulder washers at every steel-to-aluminium joint. Sikaflex-291 seals stitched seams and floor penetrations. Trim-Lok EPDM bulb seals clip on each door's skin edge. U-POL Raptor, three coats with traction additive, covers the floor, tubs, sill and lowest 400 mm of wall. No insulation or lining, only EVA pads where bars and pegs can touch. The outside stays mill finish with a white two-pack roof top. A powder coat would cost from about AUD 4,000 ([Tong Metal](https://tongmetal.com.au/)).

Welding:

- TIG (AC) on sheet, pulsed MIG allowed on tube. Filler ER5356 throughout, which ESAB's chart rates for 5052 and 6061 joints ([ESAB guide](https://ldgsesabwe.blob.core.windows.net/manuals/InstructionManuals/XA00248621_ESAB_Aluminum_Technical_Guide_EN.pdf)). Leonard proves his own welds on test coupons before he welds the box (section 11, step 1), because the design values below hold only for sound welds.
- Design welded 6061-T6 at 165 MPa ultimate and 103 MPa yield ([Aluminum Design Manual minimums](https://www.eng-tips.com/threads/accounting-for-haz-in-6061-t6-pipe.435571/)), and welded 5052-H32 at O temper, 170 and 65 MPa (est.). Take the softened zone as 25 mm either side of a weld ([15 to 25 mm](https://industrialmonitordirect.com/blogs/knowledgebase/6061-t6-aluminum-weld-strength-post-weld-yield-values)) and keep bolt holes out of it.
- Every structural weld is looked at once it has cooled. It passes if it runs its full drawn length at its full size, the fillet's leg checked with a fillet gauge, with no crack, no unfilled crater and no lack of fusion at its toes, undercut no deeper than 0.5 mm and no pore over 1.5 mm across (est.). A weld that fails is ground out and welded again.
- Welded: body, subframe, door leaves, keepers, shrouds, and in steel the stubs and cleats to the crossmembers before they are galvanised. Skins continuous on outer edges and butt joints, and the roof skin along the first bow behind the front edge, where the highway suction peaks. Stitched 30 mm at 150 mm pitch elsewhere.
- Rivet-bonded: the roof skin along every bow behind the first, with a Sikaflex-252 bead set to a 15 mm bond line (2.5 MPa lap shear, [Sika](https://industry.sika.com/content/dam/dms/us01/o/sikaflex-252.pdf)) and 4.8 mm sealed blind rivets through it at 75 mm, in place of stitch welds, so no welding heat reaches the bead. The rivets are JC Fasteners E8D35G, an AlMg5 body with a stainless mandrel, because the broken mandrel stays in the head on the roof's top face, rated 2,230 N in shear and 3,070 N in tension ([JC Fasteners](https://www.jcfasteners.com/wp-content/uploads/Blind-Rivet-Closed-DH-E8D35G-AL-SS.pdf)). The 5052 is abraded with a very fine pad, cleaned and wiped with Sika Aktivator-100 first, Sika's pre-treatment for aluminium under 1-part polyurethanes ([Sika](https://aus.sika.com/dam/dms/au01/2/Pre-treatment_Chart_1C_PU_2020.pdf)). The front edge and the first bow stay welded continuously (UGF-01).
- Bolted: aluminium to steel, body to subframe, subframe to Ford's pads, track, chocks, anchors, cam bar, lamps. Hinges riveted with stainless rivets.

## 4. Structure and mounting

The Super Duty's rear frame top sits 740 mm up at GVM with the rear axle at its rating and 850 mm at kerb (BEMM p. 128). Ford's body mounting pads stand 12 mm over the rail top (the rearmost pair 6 mm), on four stations 768, 891 and 506 mm apart, their holes 1,244 mm apart across the truck (p. 125, est. reading of the figure, with the four taken centred on the 2,286 mm of frame behind the cab). So the box's runners lie over the pads at 622 mm from the centreline, clear of the rail tops as Ford prefers (p. 158), and 45 mm mounts, the 50 mm subframe and the 4 mm floor put the floor at 851 mm. The mounts' height keeps the subframe over what Ford lists on the rail tops: the tow bar's bolts (37 mm), the spare's winch (44 mm), the bump stops (28 mm), the diesel exhaust fluid tank (47 mm) and the dampers' upper mounts (66 and 54 mm). The crossmembers stand 57 mm over the rail top, so they are placed on the truck clear of the dampers' mounts (BOX-04). Seven crossmembers join the runners, one at each pad station as Ford asks and none more than 600 mm from the next (p. 157), and four outriggers each side carry the floor to the walls, none over the wheels.

Under each track row a steel RHS 65 x 35 x 4.0 runs the full width, and a 5 mm aluminium packer sets the track 0.3 mm below the floor top. The rear row sits over Ford's rearmost pads, 960 mm behind the rear axle. Ford's first pads are under the box's front wall, 170 mm ahead of the front row, so steel stubs of RHS 75 x 50 x 3.0 are welded to the front crossmember, forward over those pads and back to the first aluminium crossmember, where the aluminium runners start. A strap's breaking load at the front row then reaches Ford's first two pads through steel (UGR-04). The runners bolt to cleats on the steel through G10 sleeves.

- Flexible mounts, station 1 (1,206 mm ahead of the rear axle): one captive M14 10.9 bolt through an upper and a lower rubber cushion either side of Ford's pad, about 1 kN/mm, a sleeve that sets the preload and stops the travel at 12 mm, and a 60 mm safety washer. Ford asks for these at the two forward pads only, under a body this rigid (BEMM p. 124).
- Rigid mounts, stations 2 to 4 (438 mm ahead of the axle, 453 and 960 mm behind): a galvanised steel spacer covering the pad, 6 mm taller at the rearmost pair, a 3 mm G10 pad under the aluminium and one M14 10.9 bolt with 50 x 5 mm hardened washers, Ford's recommended bolt (pp. 124 and 158). No powder coat on the faces. They take all the horizontal load. In Ford's 2 g inputs in each direction (p. 124), the worst bolt carries 3.2 kN of shear and 1.2 kN of tension in cornering, under 1 % of its capacity (UGM-01).
- Ford gives the 2 g inputs a body must withstand at each pad but no pad capacity. The largest loads are 1.35 kN up and 4.04 kN down (UGM-02). Build step 9 proof-loads each pad to 1.25 times these, 1.69 kN up and 5.05 kN down, before the box goes on. The 1.25 is a test margin only, the 25 % over the rated load that a crane's proof test applies (OSHA 29 CFR 1919.71, est. for a pad).

The body bolts down to the subframe from inside, with about 40 sealed M8 bolts into rivet nuts.

Wheel tubs and flares. The tubs follow the rear tyres, 30 mm over them at full bump and 30 mm inside them, Ford's recommended gap between a tyre and its guard (BEMM p. 122). Ford's wheelhouse envelope puts the guard 195 mm over the tyre's top (G), taken at kerb, which leaves about 74 mm of bump travel from GVM (est.). On Ford's 1,710 mm track each LT275/70R18's outer face is 996 mm from the centreline, 71 mm outside the 1,850 mm body's skin. Over each tub the side skin is cut away up to the top of the bottom rail, 114 mm above the floor's underside, and a flare of 2.5 mm sheet, folded into a channel 962 mm long and 103.5 mm deep, closes the opening 30 mm outside the tyre (UGW-03). Its top is welded to the rail and its ends to the skin. The box is 2,057 mm over the flares, inside the mirrors' 2,197 mm (UTE-09). The tool chests are 185 mm wide so they stay on the narrower tubs, and the box's own mudflaps hang behind the tyres from the outriggers behind the tubs, because the Super Duty comes as a cab chassis without guards (ADR 42/05). Measure the rear track (VEH-28) on the bought truck and build the tubs and flares to it.

Roof. The 1.6 mm skin spans bows at most 640 mm apart, crowned 1:50 from the centreline to each side wall, so the box stands 17.6 mm taller at the centre than at its walls. At 110 km/h the flow behind the step over the cab's roof pulls on it at about 0.84 kPa (Cp -1.5, est.). Held at every bow, the sheet drums about 4 mm and its membrane tension puts 38 MPa on the softened sheet at a weld, against 65 MPa. The bead would carry that tension at 0.91 MPa even where the skin ended at a bow, against half its 2.5 MPa, and the rivets alone, as if the bead had let go, 1,024 N each in shear against half of their 2,230 N, 0.92 (UGF-01). A 10 mm film of water sags it 2.3 mm, inside the crown's 17.6 mm fall, so it runs off. A knee, 1.1 kN on roof cladding in AS/NZS 1170.1, would punch a dent at 0.64 kN, so the roof carries no step and no kneeling, marked on CT-701 and by two labels on the roof itself (BX-C03). Hail dents any gauge.

## 5. Doors and security

Aluminium 2.5 mm thick stops nobody with a grinder. The box hides the bikes, defeats quick entry and buys time for the alarm.

- Barn doors: leaves inset flush in the portal on continuous 316 stainless hinges, pins welded over, folding 270 degrees against the walls. Three dog bolts per hinge edge enter the post, so a cut hinge frees nothing.
- Locks: the kerb leaf shoots bolts into header and sill from inside. The road leaf closes over it on a full-height stainless cam bar (Polar 158 or equal). An ABLOY PL362 (15 mm boron shackle, EN 12320 grade 6) locks the cam handle inside a welded shroud. A second PL362 locks the kerb door's shrouded hasp.
- Inside: an ABUS 8008 2.0 alarmed disc lock on each inboard front disc closes a 1.2 m, 12 mm chain round the fork leg to an ABUS WBA100 floor anchor at X 450 mm.
- Alarm: a Teltonika FMC130 4G tracker with backup battery, reed switches on all doors, a siren and the fume alarm as an input. A Monimoto 9 hidden in each bike.
- Attachment: the pad bolts go in from above with their heads under the floor and locknuts below Ford's pads. Turning a nut from below loosens it at best. The bolt cannot drop out and the floor stops it rising. Every other fixing is reached only from inside, so the box comes off only from inside it.

## 6. Restraint

Each bike has a Condor SC-2000 chock on a bolted adapter, four 35 mm SpanSet Tradesman ratchet straps of LC 500 kg (AS/NZS 4380) on soft loops, and a fifth strap through the rear rim. Front straps loop the Tuareg's bars inboard of the handguards and the Street Triple's Canyon Dancer harness. Rear straps loop the pillion peg hangers. Hooks clip into double-stud fittings (WLL 907 kg, break 26.7 kN) in two rows of Kinedyne FE750 track, 240 mm ahead of and 1,754.5 mm behind the Tuareg's front axle, 450 mm (Tuareg) and 400 mm (Street Triple) either side of each bike. Tighten the front straps until each fork compresses a third of its travel, about 80 and 40 mm.

Loads, each case alone, use the model's strap geometry (UGR-01). Sideways, one strap takes 60 % of the moment. The design case doubles the NTC cases and uses 1.0 g up (report 03).

| Case | Tuareg: 206 kg, CoG 700 mm up, 764 mm behind the front contact | Street Triple: 175 kg, 600 mm, 694 mm |
|---|---|---|
| Forward 0.8 g, into the chock | 165 kgf. 0.8 x 700 = 560 mm < 764 mm, rear stays down | 140 kgf. 480 < 694 mm |
| Rearward 0.5 g, two front straps, cosine 0.538 and 0.448 | 206 x 0.5 / 2 / 0.538 = 96 kgf | 175 x 0.5 / 2 / 0.448 = 98 kgf |
| Sideways 0.5 g, moment m g 0.5 h | 707 N m. Rear 0.6 x 707 / 0.286 m = 151 kgf. Front 114 kgf | 515 N m. Rear 0.6 x 515 / 0.269 = 117 kgf. Front 90 kgf |
| Up 0.2 g, strap vertical cosines sum 2.90 and 3.03 | 14 kgf | 12 kgf |
| Worst, NTC | 151 kgf, 0.30 of LC | 117 kgf, 0.23 |
| Worst, design case | 303 kgf, 0.61. Chock 330 kgf | 234 kgf, 0.47. Chock 280 kgf |

The rear row sits over Ford's rearmost pads, 89.5 mm further back than on the LandCruiser, so the rear straps run longer along the box and their arms about the tyres' contact line are shorter, 286 and 269 mm in place of 309 and 289 mm. That raises the worst strap from 280 to 303 kgf. Sideways sliding is held by the chock at the front and by tyre friction under strap tension, about 180 kgf, at the rear.

Anchors must withstand their strap's breaking load (NTC guide p. 201, report 03), about 9.8 kN for LC 500 kg. Each steel crossmember bears on the runners or the stubs over Ford's pads, 622 mm either side of the centreline. The worst anchor, the Street Triple's inner one, is 27 mm off the centreline between them, so 9.8 kN x 0.86 vertical x 595 x 649 / 1,244 mm (0.310 m) = 2.62 kN m on the steel crossmember, against 0.9 x 350 MPa x 8,583 mm3 = 2.70 kN m for the compact RHS 65 x 35 x 4.0 with Australian Tube Mills' corner radii, a utilisation of 0.97 (UGR-03). Revision B's LC 1,000 kg straps would need 5.24 kN m, beyond any 40 mm deep steel section, so the straps change.

At the front row the load reaches Ford's first two pads through the steel stubs (section 4). The worst anchor, the Street Triple's outer one, puts 9.8 kN on the nearer stub 170 mm behind the first pad, on the 768 mm between the first two pads: 1.30 kN m in the steel RHS 75 x 50 x 3.0 against 0.9 x 350 MPa x Ze = 4.07 kN m, and 0.83 kN m in the aluminium runner where the stub ends, 387 mm behind the first pad, against 0.85 x 103 MPa x Ze = 1.13 kN m for welded 6061-T6 (est.), a utilisation of 0.74 (UGR-04).

Clearances (model): bike to bike 71.5 mm (limit 30), the Tuareg to the anchors' bag 25.9 mm and the Street Triple to it 17.5 mm, both to the door portal 49.5 mm (limit 15), panniers to the nearest strap 55.7 mm.

## 7. Loading

The Black Widow MF-12038 ramp (3,048 x 965 mm, 680 kg rating, 34 kg) stands folded on edge across the back while the bikes are aboard. It hooks on a sill angle, its safety straps tied to loops under the sill.

With the bikes out it travels forward instead. Folded, it stands on its edge along the Tuareg's bay, 152 mm thick and centred on the bay 333 mm road side of the centreline, its front end 15 mm behind the Tuareg's chock and its rear end over the rear track row, and the Tuareg's four straps hold it to their own fittings in the front and rear rows. Its 34 kg then sits 1,024 mm further forward, at X 3,489 mm behind the front axle, which keeps the added mass of the empty box and of the truck towing with the bikes out inside Ford's centre of gravity window (UTE-07, section 12 point 10). It stands clear of the chock, the tub, the tool chest, the chain anchors, the fittings and the trailer's anchors' bag (UGC-07). Before the bikes go back in, it comes out through the barn doors to the sill. The change adds no part, no mass and no cost, and lighter rear doors, the other lever, are not needed. From the 921 mm sill with the bikes out and the trailer off it sits at 17.6 degrees, and at 16.2 degrees from the laden 851 mm (UGL-01). The WARN VRX 25-S winch (1,134 kg, synthetic rope) clips onto a plate in front of the bay being loaded, 650 mm up, and pulls a bike with about 75 kgf. It plugs into an Anderson SB50 on the front wall, fed by 6 B&S cable through a 100 A breaker, engine running. The rider walks beside the bike with the corded remote, Tuareg first, trailer unhitched.

## 8. Services

- Air: an Attwood Turbo 4000 ignition-protected blower (2.5 A, about 5.7 m3/min free flow) draws filtered air in above the cab roof and keeps the box above outside pressure. Air and petrol vapour leave through two flap vents 30 mm above the floor in the rear corners.
- Fumes: a Fireboy-Xintex two-sensor detector alarms at 20 % of the lower explosive limit, starts the fan and signals the tracker.
- Drains: two 25 mm duckbills in the rear floor corners.
- Electrics: two door-switched 1 m LED strips, a 12 V and USB outlet fused 15 A, a constant feed through a 12.2 V low-voltage disconnect and an ignition feed.
- A 2.5 kg ABE extinguisher inside the barn doors. ADR rear lamps move to the box.

## 9. Mass

The box weighs 438.2 kg empty, 476.0 kg with growth. That is one figure from two places that must agree to the 0.1 kg: the parts list sums to 438.16 kg, and the model, which carries every line, gives UGB-01 438.2 kg (`cad/tests/test_box_parts.py`). Revision F adds 0.9 kg on the Super Duty: the steel stubs 3.9 kg, the mudflaps 2.6 kg and the deeper flares 1.2 kg more, against 3.0 kg less for Ford's eight mounts in place of Toyota's twelve, and the subframe and tubs on Ford's pads and track 3.8 kg lighter. The list includes the wiring, the winch feed, sealant, the roof bows' adhesive (0.5 kg) and rivets (0.3 kg), pads, plates, the roof coat, the outlet and the drains. The roof is 1.6 mm sheet in place of 2.0 mm, which saves 5.1 kg and leaves 1.8 kg in hand under UGB-01's 440 kg. The roof carries no load, no step and no kneeling, and the bows and end frames under it are at most 640 mm apart (UGF-01), and UGF-01 is the check that the thinner sheet holds highway suction. If more margin is needed, a 10 mm chain in place of the 12 mm one saves about 2 kg (est.).

On the Super Duty, with the home trailer's heaviest towball (395.6 kg with growth, UTE-05), the ute's rear axle carries 2,547.0 kg with growth when towing with the bikes aboard (UC3), 253.0 kg under Ford's 2,800 kg (UTE-03), and the ute weighs 4,143.3 kg against Ford's 4,500 kg GVM (UTE-01). The trailer's tie-down kit rides in the box while towing: its four ratchet straps, 6.4 kg (est.), in the tool chests, and its four Tie Down 59099 ground anchors with their four 59286 stabilizer plates, Tie Down's 59200 soil test probe kit and the turning bar, 38.6 kg (est.), in a bag on the floor between the bikes, loaded last through the barn doors (T2, UGC-02). The bag is about 1,760 x 345 x 230 mm (est.), with the anchors staggered along it so that no rod passes a neighbour's helix, the plates flat in its base, and the probe and its torque wrench out of the kit's 65 in case, which stays home. Two 25 mm ratchet straps of LC 250 kg (est.) lash the bag to the L-track either side: twice the Load Restraint Guide's 0.8 g forward, UGR-01's off-road factor, is 0.61 kN on the bag, against 3.47 kN from one 45 degree leg of each strap, 0.17 (est.). The kit stays with the trailer whenever the ute is unhitched for more than a day (STB-05).

## 10. Parts list summary

| Group | AUD |
|---|---|
| Materials | 7,835 |
| Subframe and mounts | 685 |
| Fasteners and sealants | 1,097 |
| Doors | 1,200 |
| Security | 3,797 |
| Restraint | 1,852 |
| Loading, with freight | 2,973 |
| Services | 1,771 |
| Finish and tool chests | 1,011 |
| Welding and tests | 2,759 |
| Contingency 10 % | 2,498 |
| Total | 27,479 |

Leonard builds the box himself, so no labour is paid, and the box is not certified, so it has no review or inspection line (decision H25). What a shop's labour line used to include is still bought: his argon, ER5356 filler, tungsten and abrasives, AUD 2,129 (est.), sized from the box's 188 h of welding work (BX-W01 to BX-W06). The welding group also holds the two laboratory tests of his weld coupons (AUD 400, est.) and the gauges for the proof load on Ford's pads (AUD 230, est.). The Ranger Super Duty needs no GVM or GCM certification. What makes a box he builds himself safe to carry the two bikes is the design's checks in sections 4 to 9 and the tests of section 11, and every one of them stays. Not in the total: the trackers' subscriptions (about AUD 278 a year) and a full exterior powder coat (from about AUD 4,000).

## 11. Build and test steps

1. Measure the bought truck (BOX-01 to BOX-06), the places and heights of Ford's pads (BOX-04) and the rear track (VEH-28), and update the drawings. The tubs and flares are built to the measured track. Then, before any weld on the box, weld test coupons with the box's filler, gas and settings, each at least 300 mm long (est.): fillets of 6061 SHS 40 x 40 x 3 to 5052 2.5 mm sheet, and butts in 5052 2.5 mm, 5052 4.0 mm and 6061 3 mm. Break half of them in a vice, a fillet folded over its root and a butt bent 120 degrees round a 25 mm bar (est.). Each passes if it breaks or bends with no open crack longer than 3 mm on its stretched face and shows no unfused root, no lack of side fusion and no pore over 1.5 mm across on the broken face (est.). Saw and etch a section of each fillet. Send the 6061 butt for a transverse tensile test and one fillet for a macro section (BX-W07). The butt must reach 165 MPa, the design value for welded 6061-T6. Weld the box only when every coupon passes, and weld new coupons after any change of wire, gas, machine or settings.
2. Weld, drill, vent and hot-dip galvanise the steel crossmembers. Weld the subframe flat within 2 mm (est.) and trial-fit it with the strip and G10 pads.
3. Build the body on the subframe as its jig: floor, tubs, frame, skins. Portal and kerb opening diagonals within 2 mm.
4. Build and hang the doors, set gaps (BOX-09, BOX-10), fit the locking gear.
5. Seal seams, fit door seals, paper test (BOX-11). Coat the floor and roof.
6. Fit track, chock adapters, anchors, winch plates, vents, fan, drains, wiring, alarm, detector, lights, lamps.
7. Weigh and find the centre of gravity (BOX-07, BOX-08).
8. Hose every seam for 5 minutes, fan off then on. No water inside.
9. Before the box goes on, proof-load each of Ford's eight body mounting pads on the bare frame to 1.25 times UGM-02's loads (section 4). Bolt a short 50 x 50 x 6 mm steel angle to the pad with an M14 bolt, set the dial gauge's magnetic base on the rail and zero it on the pad. For the uplift, push the angle up from a bottle jack standing on the platform scale to 1.69 kN, 172 kg on the scale after taring the jack. For the downward load, pull the angle down with a lever hoist and the crane scale in a chain to a steel beam under the nearer axle's tyres, to 5.05 kN, 515 kg on the scale (BX-W08). Hold each load 10 s, then release. A pad passes with no permanent set, the gauge back within 0.1 mm of zero (est.), and no crack in a dye-penetrant test after. Then fit the box to the ute, the rigid mounts' M14 10.9 bolts torqued within Ford's 150 to 200 Nm (BEMM p. 27), the flexible mounts to their sleeves.
10. Test switches, siren, tracker, fan, detector (unlit butane at a sensor) and lights. Proof-load each outer fitting to 4.9 kN with no permanent set.
11. Load both bikes, set fork compression and measure BOX-12 to BOX-20. Drive 20 km with rough road and re-tension. Then dye-penetrant test Ford's eight pads and their brackets, the mount spacers, the stubs' welds and the anchor crossmember welds, and again at each service for the first year.
12. Wheel alignment with the box on, as Ford asks after a change to the load on the suspension (BEMM p. 35).

## 12. Open points and the assumption used

1. Floor height and bump travel: the rear frame top 740 mm at GVM (BEMM p. 128), 74 mm of bump travel from Ford's wheelhouse envelope with its 195 mm taken from the tyre at kerb (est.), tyre radius 393 mm laden (est.) (BOX-01 to BOX-03). If Ford's 195 mm counts from the tyre at GVM, the tubs stand 91 mm higher, 161 mm over the floor, and UGD-01 fails, so the bump travel is measured on the truck before the tubs are built.
2. Ford's pads: their places from the BEMM's spacings and its 1,244 mm across, taken centred on the frame behind the cab (est.), and their loads at Ford's 2 g (UGM-02). Ford publishes no pad capacity. Assumption: each pad carries 1.25 times UGM-02's loads, 1.69 kN up and 5.05 kN down, with no permanent set, which build step 9's proof load shows before the box goes on, and step 11's crack test finds any damage in use. The pads are measured (BOX-04) before the subframe is built.
3. Flexible mounts: an upper and a lower rubber cushion of about 1 kN/mm at Ford's first pads, the travel stopped at 12 mm (Ford's figures, BEMM p. 124). Assumption: Ford counts a welded box on its subframe as an exceptionally rigid body, so its forward mounts are flexible and the rest rigid. Build step 11's rough-road drive and crack test show a knock, bottoming or a cracked pad.
4. Off-road factor 2 and 1.0 g up (report 03). Assumption: these cases cover the box's use, and UGR-01 to UGR-04 are checked at them. UGM-01 and UGM-02 use Ford's 2 g inputs at the pads (BEMM p. 124).
5. Anchors withstand the strap's breaking load, so straps are LC 500 kg. LC 1,000 kg needs the outer anchors tied into the wall frame.
6. Box mass 438.2 kg with the 1.6 mm roof, the flares, the stubs and the mudflaps, against UGB-01's 440 kg (section 9). The 1.6 mm roof holds highway suction and drains on its 1:50 crown (UGF-01), but a knee would dent it, so it carries no step and no kneeling. Assumption: nobody stands on it, and the NO STEP labels (BX-C03) say so. UGF-01 checks the 1.6 mm roof on bows at most 640 mm apart.
7. Prices: 6061-T6 at the 6060-T5 listing plus 25 %, ABLOY from a UK listing, and the detector, the argon, the tungsten, the abrasives, the coupon tests and the gauges estimated.
8. Rear track: Ford's 1,710 mm (BEMM p. 25), with the LT275/70R18 taken as 282 mm wide (est.). The tubs and flares follow the measured track (VEH-28), and the tyre keeps 30 mm to the flare (BOX-20).
9. The box's mudflaps hang from the outriggers behind the tubs, about 300 mm wide with their bottom edge about 230 mm above the ground (assumption), as ADR 42/05 asks for the rear wheels under a body.
10. Ford's centre of gravity window for the added mass (BEMM p. 32) is read from the table's text: its height is taken from the rear frame top (est.) and its limits are interpolated between Ford's 800 kg and GVM rows (est.). Below 800 kg a case is held to the 800 kg row, the lightest Ford gives (UTE-07, UTE-08). With the bikes out the ramp travels along the Tuareg's bay (section 7), so the empty box, 475 kg of added mass, sits at X 3,199 mm, 56 mm ahead of that row's 3,255 mm, and the truck towing with the bikes out, 580 kg, at X 3,226 mm, 29 mm ahead. With the ramp across the back, as before, the empty box sat 27 mm behind it. With the bikes aboard, 970 kg sits at X 3,253 mm and 608 mm over the frame top, 17.9 mm ahead of the interpolated 3,271 mm and 5.1 mm under the interpolated 614 mm, the reading the design uses. Under the stricter reading, each limit at the stricter of Ford's two rows, it is 2 mm ahead of the 800 kg row's 3,255 mm, so it passes along the truck, and 78 mm over the GVM row's 530 mm, so it fails only the height. The 78 mm cannot be found in any box that carries the bikes upright, since the two bikes alone stand about 765 mm over the frame top. Assumption: Ford means the window to vary with the added mass between its rows, as the design reads it, and Ford's drawing, once read, settles both the rows and the height's datum. The box is 438.2 kg of the 970 kg, so its weighed centre of gravity (BOX-08) may sit at most about 40 mm further back or 11 mm higher than the model's before UTE-07 or UTE-08 fails.
11. Ford's maximum tow ball download is in the owner guide (BEMM p. 34), which was not read. Assumption: 450 kg, 10 % of the 4,500 kg braked rating (UTE-05), above the trailer's heaviest towball of 395.6 kg.
12. Ford's Driver Assistance Technology bar carries the rear camera, the parking sensors and the blind spot radars, stays at its factory place, and limits a body's overhang over it: the lowest rearmost point of the body at most 225 mm behind the sensors' faces and at least 240 mm above their midpoints, and its rear corners at most 290 mm outside the outer sensors (BEMM pp. 77 to 79, 85). The text does not give the bar's place. The box's floor and doors end 334 mm behind the frame's end, inside Ford's 480 mm from the rear chassis mount (p. 78), and 797 mm up. Assumption: the bar sits at the frame's end, so the box overhangs its sensors by about 300 mm, about 75 mm over Ford's 225 mm, and the parking sensors and the reverse brake assist may false-alarm with the box on. The box cannot be shorter with both bikes in it, so the bar's place is measured on the truck with Ford's pads (BOX-04) before the box is built, and if the overhang stays over 225 mm the rear parking aid is switched off while the box is on.

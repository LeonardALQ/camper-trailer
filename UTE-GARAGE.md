# UTE-GARAGE: the bike box on the LandCruiser 79

Revision D, 21 Nov 2026: revision C of 20 Nov with the wheel tubs moved out and a flare over each rear tub for the Lovells Elite kit's wider rear track (decisions H18 and H19). Build document for a fabricator to quote from and an engineer to check. Parts list `data/ute/box-parts.yaml`, measurements BOX-01 to BOX-20 and VEH-28 in `data/measurements.yaml`, model `data/assemblies/ute-garage.yaml` and `data/ute/parts/`, drawings CT-701 to CT-704. The site's Bike box page shows the parts list and the checks.

## 1. Purpose and limits

The box carries the Aprilia Tuareg 660 Rally (206 kg) and the Triumph Street Triple 765 (175 kg) side by side, noses forward, 760 mm apart, with about 60 kg of tools. It is locked, sealed against dust and vented for fuelled bikes.

- Body at most 1,850 mm wide, and the rear tub flares at most 1,910 mm (UTE-09, decision H19). Toyota allows a mounted part 60 mm beyond the cab's outermost point, measured on each side (BBGJ1007 section 1-2), so 1,910 mm on the 1,790 mm cab. Toyota BBGJ1007 also asks for 39 mm from the cab, 25 mm over the tyre at full bump, 40 mm inside it, 30 mm outside it, bodies on the deck mount brackets, no drilling or welding of the frame.
- Rear axle at most 2,800 kg with growth: the Lovells Elite kit (decision H17) plated at twice the ROH wheel's 1,400 kg (decision H18), or 2,550 kg if cut CUT7 returns to the Platinum (`VEHICLE.md`). Box empty under report 17's 440 kg (UGB-01).
- NTC Load Restraint Guide 2018: 0.8 g forward, 0.5 g rearward and sideways, 0.2 g up ([guide, p. 19](https://media.nrspp.org.au/wp-content/uploads/2021/11/06005924/Load-Restraint-Guide-for-light-vehicles-2018.pdf)).
- Ramp at most 20 degrees (report 03).

## 2. The design in brief

A welded aluminium body bolts onto its own aluminium ladder subframe. The subframe sits on a 6 mm rubber strip on the rails and bolts to Toyota's six pairs of deck mount brackets, firm at the front two and compliant at the rear four, so the frame twists under the box without loading its walls.

Outside 2,590 x 1,850 x 1,502 mm at the walls, 1,520 mm at the roof's 1:50 crown, and 1,890 mm wide over the rear tub flares. Inside 2,520 x 1,765 x 1,460 mm. Floor 834 mm up laden, wheel tubs 86.5 mm high and 1,201 mm apart on the Elite's 1,555 mm rear track. Rear barn doors open 1,745 x 1,460 mm. A 1,200 x 1,000 mm top-hinged kerb door reaches the Street Triple's kerb strap and the kerb tool chest.

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
| Mount angles | 6061-T6 angle 50 x 50 x 6 |
| Track packers, plates | 5052-H32 5.0 mm |
| Anchor crossmembers | C350L0 RHS 65 x 35 x 4.0, hot-dip galvanised after welding |

Buy 6061-T6 with mill certificates from a structural stockist. All Aluminium stocks these tubes only in 6060-T5, which is weaker when welded.

Fasteners: M12 8.8 hot-dip galvanised at the brackets, A4-70 stainless with Tef-Gel through aluminium, G10 pads and shoulder washers at every steel-to-aluminium joint. Sikaflex-291 seals stitched seams and floor penetrations. Trim-Lok EPDM bulb seals clip on each door's skin edge. U-POL Raptor, three coats with traction additive, covers the floor, tubs, sill and lowest 400 mm of wall. No insulation or lining, only EVA pads where bars and pegs can touch. The outside stays mill finish with a white two-pack roof top. A powder coat would cost from about AUD 4,000 ([Tong Metal](https://tongmetal.com.au/)).

Welding:

- TIG (AC) on sheet, pulsed MIG allowed on tube. Filler ER5356 throughout, which ESAB's chart rates for 5052 and 6061 joints ([ESAB guide](https://ldgsesabwe.blob.core.windows.net/manuals/InstructionManuals/XA00248621_ESAB_Aluminum_Technical_Guide_EN.pdf)). Welders qualified to ISO 9606-2.
- Design welded 6061-T6 at 165 MPa ultimate and 103 MPa yield ([Aluminum Design Manual minimums](https://www.eng-tips.com/threads/accounting-for-haz-in-6061-t6-pipe.435571/)), and welded 5052-H32 at O temper, 170 and 65 MPa (est.). Take the softened zone as 25 mm either side of a weld ([15 to 25 mm](https://industrialmonitordirect.com/blogs/knowledgebase/6061-t6-aluminum-weld-strength-post-weld-yield-values)) and keep bolt holes out of it.
- Welded: body, subframe, mount angles, door leaves, keepers, shrouds. Skins continuous on outer edges and butt joints, and the roof skin along the first bow behind the front edge, where the highway suction peaks. Stitched 30 mm at 150 mm pitch elsewhere.
- Bolted: aluminium to steel, body to subframe, subframe to brackets, track, chocks, anchors, cam bar, lamps. Hinges riveted with stainless rivets.

## 4. Structure and mounting

Laden rail tops sit about 774 mm up (est.), so the 6 mm strip, 50 mm subframe and 4 mm floor put the floor at 834 mm. The runners lie on the rails, eight crossmembers join them and six outriggers each side carry the floor to the walls, none over the wheels. At the first deck mount (879 mm ahead of the rear axle) and the last (1,025 mm behind) a steel RHS 65 x 35 x 4.0 runs the full width under a track row. A 5 mm aluminium packer sets the track 0.3 mm below the floor top. The runners bolt to cleats on the steel through G10 sleeves.

- Firm mounts, stations 1 and 2 (879 and 490 mm ahead of the axle): two M12 8.8 bolts per bracket through a 6 mm plate under the steel crossmember or the runner's angle. They take all horizontal load. The worst bolt carries 1.8 kN in 1.6 g braking, 6 % of its capacity (UGM-01).
- Compliant mounts, stations 3 to 6 (123, 490, 755 and 1,025 mm behind): one M12 8.8 bolt through an upper and a lower Toyota 70 Series cab cushion, a sleeve that sets the preload and a 50 mm safety washer.
- Toyota gives no bracket capacity. The largest loads are 0.8 kN up and 2.5 kN down (UGM-02).

The body bolts down to the subframe from inside, with about 40 sealed M8 bolts into rivet nuts.

Wheel tubs and flares. The tubs follow the rear tyres, 25 mm over them at full bump and 40 mm inside them. The Elite's housing gives a 1,555 mm rear track (research report 26, est.), 95 mm wider than Toyota's 1,460 mm, so each tyre's outer face is 911.5 mm from the centreline, 11 mm from the 1,850 mm body's skin against Toyota's 30 mm. Over each tub the side skin is cut away up to the top of the bottom rail, 130.5 mm above the floor's underside, and a flare of 2.5 mm sheet, folded into a channel 925 mm long and 20 mm deep, closes the opening. Its top is welded to the rail and its ends to the skin. The tyre keeps 31 mm (UGW-03), and the box is 1,890 mm over the flares against UTE-09's 1,910 mm. The mount angles stay over Toyota's brackets, the road-side tool chest is 270 mm wide so it stays on its tub, and Lovells' two mudflaps hang behind the tyres from the rear outriggers, 47.5 mm further out than on the factory track. Measure the rear track (VEH-28) once the kit is fitted and build the tubs and flares to it.

Roof. The 1.6 mm skin spans bows at most 640 mm apart, crowned 1:50 from the centreline to each side wall, so the box stands 17.7 mm taller at the centre than at its walls. At 110 km/h the flow behind the step over the cab's roof pulls on it at about 0.84 kPa (Cp -1.5, est.). Welded to the bows, the sheet drums about 4 mm and its membrane tension puts 38 MPa on the softened sheet at the bow, against 65 MPa (UGF-01). A 10 mm film of water sags it 2.3 mm, inside the crown's 17.7 mm fall, so it runs off. A knee, 1.1 kN on roof cladding in AS/NZS 1170.1, would punch a dent at 0.64 kN, so the roof carries no step and no kneeling, marked on CT-701. Hail dents any gauge.

## 5. Doors and security

Aluminium 2.5 mm thick stops nobody with a grinder. The box hides the bikes, defeats quick entry and buys time for the alarm.

- Barn doors: leaves inset flush in the portal on continuous 316 stainless hinges, pins welded over, folding 270 degrees against the walls. Three dog bolts per hinge edge enter the post, so a cut hinge frees nothing.
- Locks: the kerb leaf shoots bolts into header and sill from inside. The road leaf closes over it on a full-height stainless cam bar (Polar 158 or equal). An ABLOY PL362 (15 mm boron shackle, EN 12320 grade 6) locks the cam handle inside a welded shroud. A second PL362 locks the kerb door's shrouded hasp.
- Inside: an ABUS 8008 2.0 alarmed disc lock on each inboard front disc closes a 1.2 m, 12 mm chain round the fork leg to an ABUS WBA100 floor anchor at X 450 mm.
- Alarm: a Teltonika FMC130 4G tracker with backup battery, reed switches on all doors, a siren and the fume alarm as an input. A Monimoto 9 hidden in each bike.
- Attachment: bracket bolts go in from above with their heads under the floor and nyloc nuts below. Turning a nut from below loosens it at best. The bolt cannot drop out and the floor stops it rising. Every other fixing is reached only from inside, so the box comes off only from inside it.

## 6. Restraint

Each bike has a Condor SC-2000 chock on a bolted adapter, four 35 mm SpanSet Tradesman ratchet straps of LC 500 kg (AS/NZS 4380) on soft loops, and a fifth strap through the rear rim. Front straps loop the Tuareg's bars inboard of the handguards and the Street Triple's Canyon Dancer harness. Rear straps loop the pillion peg hangers. Hooks clip into double-stud fittings (WLL 907 kg, break 26.7 kN) in two rows of Kinedyne FE750 track, 240 mm ahead of and 1,665 mm behind the Tuareg's front axle, 450 mm (Tuareg) and 400 mm (Street Triple) either side of each bike. Tighten the front straps until each fork compresses a third of its travel, about 80 and 40 mm.

Loads, each case alone, use the model's strap geometry (UGR-01). Sideways, one strap takes 60 % of the moment. The design case doubles the NTC cases and uses 1.0 g up (report 03).

| Case | Tuareg: 206 kg, CoG 700 mm up, 764 mm behind the front contact | Street Triple: 175 kg, 600 mm, 694 mm |
|---|---|---|
| Forward 0.8 g, into the chock | 165 kgf. 0.8 x 700 = 560 mm < 764 mm, rear stays down | 140 kgf. 480 < 694 mm |
| Rearward 0.5 g, two front straps, cosine 0.538 and 0.448 | 206 x 0.5 / 2 / 0.538 = 96 kgf | 175 x 0.5 / 2 / 0.448 = 98 kgf |
| Sideways 0.5 g, moment m g 0.5 h | 707 N m. Rear 0.6 x 707 / 0.309 m = 140 kgf. Front 114 kgf | 515 N m. Rear 0.6 x 515 / 0.289 = 109 kgf. Front 90 kgf |
| Up 0.2 g, strap vertical cosines sum 3.00 and 3.13 | 14 kgf | 11 kgf |
| Worst, NTC | 140 kgf, 0.28 of LC | 109 kgf, 0.22 |
| Worst, design case | 280 kgf, 0.56. Chock 330 kgf | 218 kgf, 0.44. Chock 280 kgf |

Sideways sliding is held by the chock at the front and by tyre friction under strap tension, about 180 kgf, at the rear.

Anchors must withstand their strap's breaking load (NTC guide p. 201, report 03), about 9.8 kN for LC 500 kg. The worst anchor is 276 mm from a bracket, so 9.8 kN x 0.86 vertical x 0.276 m = 2.33 kN m on the steel crossmember, against 0.9 x 350 MPa x 8,583 mm3 = 2.70 kN m for the compact RHS 65 x 35 x 4.0 with Australian Tube Mills' corner radii, a utilisation of 0.86 (UGR-03). Revision B's LC 1,000 kg straps would need 4.62 kN m, beyond any 40 mm deep steel section, so the straps change.

Clearances (model): bike to bike 71.5 mm (limit 30), the Tuareg to the roof light 57.2 mm and the Street Triple to the kerb tool chest 25.5 mm, both to the door portal 49.5 mm (limit 15), panniers to the nearest strap 55.7 mm.

## 7. Loading

The Black Widow MF-12038 ramp (3,048 x 965 mm, 680 kg rating, 34 kg) stands folded on edge across the back. It hooks on a sill angle, its safety straps tied to loops under the sill. From the 864 mm sill with the bikes out it sits at 16.5 degrees. The WARN VRX 25-S winch (1,134 kg, synthetic rope) clips onto a plate in front of the bay being loaded, 650 mm up, and pulls a bike with about 75 kgf. It plugs into an Anderson SB50 on the front wall, fed by 6 B&S cable through a 100 A breaker, engine running. The rider walks beside the bike with the corded remote, Tuareg first, trailer unhitched.

## 8. Services

- Air: an Attwood Turbo 4000 ignition-protected blower (2.5 A, about 5.7 m3/min free flow) draws filtered air in above the cab roof and keeps the box above outside pressure. Air and petrol vapour leave through two flap vents 30 mm above the floor in the rear corners.
- Fumes: a Fireboy-Xintex two-sensor detector alarms at 20 % of the lower explosive limit, starts the fan and signals the tracker.
- Drains: two 25 mm duckbills in the rear floor corners.
- Electrics: two door-switched 1 m LED strips, a 12 V and USB outlet fused 15 A, a constant feed through a 12.2 V low-voltage disconnect and an ignition feed.
- A 2.5 kg ABE extinguisher inside the barn doors. ADR rear lamps move to the box.

## 9. Mass

The parts list sums to 436.5 kg empty, 474.1 kg with growth, and the model carries every line, so UGB-01 and the list agree (`cad/tests/test_box_parts.py`). Revision D adds 0.4 kg: the flares 1.9 kg, less 1.6 kg of skin cut away for them, and the tubs and floor re-cut for the wider track (-0.8 and +0.9 kg). The list includes the wiring, the winch feed, sealant, pads, plates, the roof coat, the outlet and the drains. The roof is 1.6 mm sheet in place of 2.0 mm, which saves 5.1 kg and leaves 3.5 kg in hand under UGB-01's 440 kg. The roof carries no load, no step and no kneeling, and the bows and end frames under it are at most 640 mm apart (UGF-01). The engineer confirms the thinner sheet. If more margin is needed, a 10 mm chain in place of the 12 mm one saves about 2 kg (est.).

On the Elite, with the home trailer's heaviest towball (317 kg with growth), the ute's rear axle carries 2,586 kg with growth when towing with the bikes aboard (UC3), 214 kg under the 2,800 kg plate.

## 10. Parts list summary

| Group | AUD |
|---|---|
| Materials | 7,976 |
| Subframe and mounts | 990 |
| Fasteners and sealants | 892 |
| Doors | 1,200 |
| Security | 3,797 |
| Restraint | 1,852 |
| Loading, with freight | 2,973 |
| Services | 1,771 |
| Finish and tool chests | 891 |
| Shop labour, 188 h at AUD 121 | 22,748 |
| Engineer's review | 2,000 |
| Contingency 10 % | 4,709 |
| Total, shop-built | 51,799 |
| Total, owner-built (no shop labour) | 26,776 |

The LC5 inspection is counted once, in the car build's GV03, because one inspection covers the GVM kit, the GCM revision, the box and the winch. The box keeps only the engineer's review. Not in the total: the trackers' subscriptions (about AUD 278 a year) and a full exterior powder coat (from about AUD 4,000).

## 11. Build and test steps

1. Measure the bought ute (BOX-01 to BOX-06) and, once the Elite is fitted, its rear track (VEH-28), and update the drawings. The tubs and flares are built to the measured track.
2. Weld, drill, vent and hot-dip galvanise the steel crossmembers. Weld the subframe flat within 2 mm (est.) and trial-fit it with the strip and G10 pads.
3. Build the body on the subframe as its jig: floor, tubs, frame, skins. Portal and kerb opening diagonals within 2 mm.
4. Build and hang the doors, set gaps (BOX-09, BOX-10), fit the locking gear.
5. Seal seams, fit door seals, paper test (BOX-11). Coat the floor and roof.
6. Fit track, chock adapters, anchors, winch plates, vents, fan, drains, wiring, alarm, detector, lights, lamps.
7. Weigh and find the centre of gravity (BOX-07, BOX-08).
8. Hose every seam for 5 minutes, fan off then on. No water inside.
9. Fit to the ute, firm mounts to the engineer's torque, compliant mounts to their sleeves.
10. Test switches, siren, tracker, fan, detector (unlit butane at a sensor) and lights. Proof-load each outer fitting to 4.9 kN with no permanent set.
11. Load both bikes, set fork compression and measure BOX-12 to BOX-20. Drive 20 km with rough road and re-tension.
12. Wheel alignment and LSPV reset, then the LC5 inspection.

## 12. Open points and the assumption used

1. Floor height and bump travel: rails 774 mm laden, 110 mm travel, tyre radius 380 mm (BOX-01 to BOX-03).
2. Toyota's brackets take M12 bolts and carry 0.8 kN up and 2.5 kN down each.
3. Compliant mounts: Toyota cab cushions, preload set by the engineer.
4. Off-road factor 2 and 1.0 g up (report 03), for the engineer to confirm.
5. Anchors withstand the strap's breaking load, so straps are LC 500 kg. LC 1,000 kg needs the outer anchors tied into the wall frame.
6. Box mass 436.5 kg with the 1.6 mm roof and the flares, against UGB-01's 440 kg. The 1.6 mm roof holds highway suction and drains on its 1:50 crown (UGF-01), but a knee would dent it, so it carries no step and no kneeling. Assumption: nobody stands on it. The engineer confirms the 1.6 mm roof on bows at most 640 mm apart.
7. Prices: 6061-T6 at the 6060-T5 listing plus 25 %, ABLOY from a UK listing, detector and labour hours estimated.
8. Rear track on the Elite: 1,555 mm (research report 26, est.). Lovells says only that the housing brings the rear in line with the front. The tubs and flares follow the measured track (VEH-28), and the tyre keeps 30 mm to the flare (BOX-20). Above 1,577 mm the flares would pass 1,910 mm.
9. Lovells' mudflaps hang from the rear outriggers behind the tyres, about 300 mm wide with their bottom edge about 230 mm above the ground. Confirm the brackets with the kit.

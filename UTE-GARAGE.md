# UTE-GARAGE: the LandCruiser 79 and its bike garage

Revision B, 20 Nov 2026. Design basis for the tow vehicle and the enclosed bike box on its tray. It is a
planning-level proposal for the engineer and the GVM certifier to check. The data is `data/ute/ute.yaml`,
`data/assemblies/ute-garage.yaml`, `data/ute/parts/*.yaml` and `data/ute/garage-checks.yaml`. The code is
`cad/ute.py` and `cad/ute_garage.py`. The drawings are CT-701 to CT-704, and the site page is "Ute garage". The decision
log cited by its time is `docs/decisions.md`.

Leonard asked: "Instead of a porsche cayenne, I'll get a land cruiser single cab 79 V8 ... I'll put an enclosed box at
the back to fit the two bikes and some tools. That way, we can make the trailer smaller and lighter." Then: "Let's
design the motorbike garage on the land cruiser. We want to make sure it's enclosed to make sure the bikes are safer
and not prone to theft."

What changed in revision B, 20 Nov 2026: the trailer was redesigned without its garage (TRAILER.md revision H), and
its ATM is plated at 3,100 kg (decision log 12:10). The towball now sits 1,300 mm behind the rear axle (report 16,
decision log 12:45) in place of report 17's 1,350 mm, and the coupling point is set for 440 mm laden, plus or minus
20 mm (report 18 section 3.5). Section 9 is re-solved for both. The rear axle with growth fell 4 kg to 2,436 kg.
No check limit changed.

## 1. The ute

- Toyota LandCruiser VDJ79R GXL single cab chassis, V8, built 01/2017 to 08/2022 (decision log 11:25, research
  report 16).
- Lovells 4,200 kg GVM kit TOYKIT080-GVM: front axle 1,650 kg, rear axle 2,550 kg. GVM (gross vehicle mass) is the most
  the loaded ute may weigh. The weighed ute stays at or under 3,850 kg.
- GCM (gross combination mass, the ute and trailer together) 6,900 kg. Braked towing 3,500 kg.
- Hayman Reese 03186RW towbar, rated 3,500 kg and 350 kg. The plan caps the towball at 250 kg.
- ROH Trak 2 16 x 7 ET0 wheels rated 1,400 kg, LT265/75R16 tyres rated 1,550 kg and 805 mm in diameter.
- The trailer is plated at 3,100 kg ATM. ATM (aggregate trailer mass) is the most the loaded trailer may weigh.

Ute frame DIM-U1: X from the front axle centre, positive rearward. Y from the centreline, positive to the road
(right) side. Z up from the ground, laden ride height. Module frame of the box: X from the front wall's inner face,
Y as the ute, Z from the floor top. Module X 0 is at ute X 2,142.5 mm and module Z 0 at ute Z 834 mm.

## 2. Requirements for the box

From the brief, the decision log and report 17:

- Enclosed and lockable. Both bikes and some tools inside.
- At most 1,850 mm wide outside (the cab's 1,790 mm plus Toyota's 60 mm). Lighter than report 17's 440 kg.
- The lowest floor that works with the kit's bump travel. Report 17 offers a lower floor at about 850 mm if the wheel
  tubs stand no more than 100 mm above it, or a flat deck at about 1,080 mm.
- Bikes side by side, noses forward, at the 760 mm spacing of the retired trailer garage (`DESIGN.md`).
- Rear barn doors with shoot bolts, a cam bar and an ABLOY padlock. A kerb-side lift-up door to reach the second
  bike's straps. Inset hinges, dust seals, low and high vents for petrol vapour, interior lights.
- Report 17's ramp stowed inside, the WARN winch moved from the trailer, Condor chocks, flush L-track, straps and
  anchors that reach steel.
- Report 17's tracker, door switches and siren, a tracker in each bike, disc locks and anchor chains.
- Tools stowed low and forward.
- Mounted on Toyota's deck mount brackets through a subframe, firm at the front and compliant at the rear, with no
  drilling or welding of the frame.
- Toyota's body rules (BBGJ1007): at least 39 mm from the cab, 25 mm over the tyre at full bump, 40 mm inside it and
  30 mm outside it. Unladen centre of gravity under 1,000 mm. At least 20 % of the mass on the front axle.
- ADR 43/04: rear overhang at most 60 % of the wheelbase, 1,908 mm.

## 3. Loads and criteria

- **Mass.** Every line carries a source and a maturity. A maker's figure (spec) carries no growth allowance, a
  calculated mass 7 % and an estimate 20 % (report 02 MASS-06). The axle, GVM and GCM checks hold with growth.
- **Load cases.** UC1 as built, unladen. UC2 two people, tools and both bikes. UC3 as UC2 towing, with 250 kg on the
  ball. UC4 towing with the bikes out. UCB, for reference, is report 17's case B: the bikes in the trailer and a plain
  tray.
- **Restraint.** The NHVR's 2025 Load Restraint Guide keeps the 2018 performance standards: 0.8 g forward, 0.5 g
  rearward and sideways. Report 03 multiplies them by an off-road factor of 2 and adds 1.0 g upward. One strap takes
  60 % of a bike's sideways moment. Straps are LC 1,000 kg to AS/NZS 4380. Every anchor is designed for 20 kN.
- **Box mounts.** The same factored cases act on the box and everything in it, with growth: braking at 1.6 g,
  cornering at 1.0 g and a net 1.0 g upward. The box is taken as rigid on six pairs of brackets. The firm front pairs
  carry all the horizontal load. Each bolt is checked against AS 4100 design capacities for an M12 property class
  8.8 bolt: 56.0 kN in tension and 31.4 kN in shear with the threads in the shear plane.
- **Clearances.** Bike to bike 30 mm, bike to walls, doors and stowed items 15 mm, bike to the door portal as it rolls
  out 15 mm (the retired trailer garage's CLR-03, CLR-04 and CLR-09). Tyre clearances are Toyota's, measured on a solid the
  tyre sweeps from static up to full bump.
- **Ramp.** Report 03 limits a ramp to 20 degrees for walking a bike up beside it. The angle is reported.

## 4. Structure

**Floor.** The design takes the lower floor. Laden, the rear frame top is about 774 mm up: Toyota's 724 mm plus about
50 mm of Lovells lift (estimate). A 6 mm rubber strip, the 50 mm subframe and the 4 mm floor plate put the floor top at
834 mm. The tyre's top is 782.5 mm up at static (380 mm loaded radius, estimate), and 892.5 mm at full bump on 110 mm
of travel (report 17's estimate). Toyota's 25 mm and the 3 mm tub plate put the tub tops 86.5 mm above the floor,
under report 17's 100 mm. A flat deck would need about 921 mm of floor height plus its own crossmembers. The floor is
75 mm lower than the U1 estimate of 909 mm.

**Box.** A one-piece welded body, as report 17 section 6.1: 5052-H32 skins TIG-welded to a 6061-T6 frame.

| Part | Section | Note |
|---|---|---|
| Wall and front skins | 2.5 mm sheet | The kerb skin has the 1,200 x 1,000 mm door opening |
| Roof skin | 2.0 mm sheet | Carries nothing |
| Floor | 4.0 mm plate | Cut round the tubs and the two track rows |
| Wheel tubs | 3.0 mm sheet | 871 mm long, 86.5 mm high, 553 mm out from the centreline to the wall |
| Frame | SHS 40 x 40 x 3 | Corner posts, four posts each side, top and bottom rails, four roof bows, the rear portal |
| Door leaves | 2.5 mm skin on SHS 25 x 25 x 3 | 27.5 mm thick |

The posts stand at module X 560, 1,200, 1,480 and 2,000 mm. The one at 1,200 mm is the kerb door's rear jamb and
stands on the tub. Over each tub the side wall's bottom rail rides on the tub top. The front wall has two rails at
630 and 790 mm for the winch plates.

**Subframe.** Two runners of aluminium RHS 75 x 50 x 3 lie flat on the rails. Crossmembers of SHS 50 x 50 x 3 join them
at eight stations, and outriggers carry the floor out to the walls at six, none over the wheels. Under each L-track row
a galvanised steel RHS 76 x 38 x 3 crossmember runs the full width at one of Toyota's deck mount stations: the first,
879 mm ahead of the rear axle, and the last, 1,025 mm behind it. The track sits on a 2 mm steel packer on that
crossmember, so its top ends 0.3 mm below the floor top. Aluminium strips 20 x 10 mm either side carry the floor
plate's edges. The runners are cut at the steel crossmembers and bolted to them through steel cleats with nylon
sleeves, so the two metals do not touch.

That puts the front track row 240 mm ahead of the Tuareg's front axle, against 150 mm in report 17. The rear row is
1,665 mm behind it, against 1,650 mm. The restraint check measures the straps at these positions.

## 5. Mounting

Toyota allows no frame modification. Bodies bolt to the deck mount brackets on the rails, at 879 and 490 mm ahead of
the rear axle and 123, 490, 755 and 1,025 mm behind it (BBGJ1007, report 17 section 1.4).

- **Firm, stations 1 and 2.** Two M12 8.8 bolts per bracket with hardened washers and nyloc nuts. Station 1 is a 6 mm
  spacer under the front steel crossmember. Station 2 is an angle on the runner's outer face. These carry the box's
  fore and aft and sideways loads.
- **Compliant, stations 3 to 6.** One M12 8.8 bolt per bracket through two rubber body-mount cushions, a steel sleeve
  that sets the preload, and an oversize safety washer that holds the box if a cushion fails. The frame twists under
  the box here, so the walls and door frames do not take the frame's twist. Station 6 is under the rear steel
  crossmember.
- The mount angles stay 40 mm inside the tyre. Nothing is drilled or welded on the frame.

## 6. Doors, security and air

- **Barn doors.** Two leaves inset in the rear portal, flush with its rear face, over a clear opening 1,745 mm wide and
  1,460 mm high. A continuous stainless hinge runs in the 10 mm gap at each corner post, with its knuckle at the post's
  outer corner, so each leaf folds 270 degrees flat against its side wall. The pins are peened, and dog bolts on each
  leaf's hinge edge engage the post when shut, so a cut hinge does not free a leaf.
- **Locking.** The kerb leaf shuts first and shoots bolts into the header and the sill. The road leaf closes over it on a
  full-height cam bar with keepers at the header and the sill. An ABLOY PL362 (15 mm boron steel shackle, grade 6 to
  EN 12320) on a shrouded hasp locks the cam handle. A pry bar at the middle of the door gets nothing.
- **Kerb door.** A top-hinged door over the front 1,200 mm of the kerb wall, 300 to 1,300 mm above the floor, on two gas
  struts, with a keyed latch and a second PL362 on a hasp. It reaches the Street Triple's kerb-side front strap and the
  kerb tool chest.
- **Inside.** A disc lock on each front disc. A chain from each bike to a ground anchor bolted through the floor into the
  crossmember at module X 1,800 mm, between the bikes.
- **Alarm and trackers.** A Teltonika FMC130 4G tracker with a backup battery, reed switches on the three doors and a
  12 V siren, behind a panel high on the front wall. A Monimoto 9 hidden in each bike.
- **Air.** A filtered, ignition-protected fan high in the front wall, above the cab roof, keeps the box above outside
  pressure. Low vents with flap valves in the two rear corners let air and petrol vapour out at floor level. EPDM bulb
  seals on every door, pulled in by the cam bar and the latches. Drains with one-way valves at the low corners.
- **Light.** Two door-switched 12 V LED strips under the roof.

Aluminium of 2.5 mm stops nobody with a grinder. The box hides the bikes, defeats the quick ways in and buys time for
the alarm and the trackers (report 17 section 4).

## 7. Restraint, loading and tools

- As in the retired trailer garage: a Condor SC-2000 chock on each bike's centreline at the front wall, two flush L-track rows
  across the floor, 35 mm SpanSet straps of LC 1,000 kg, a Canyon Dancer harness on the Street Triple and a rear-wheel
  strap on each bike. The Tuareg sits 333 mm road side of the centreline and the Street Triple 427 mm kerb side, 760 mm
  apart, which leaves 59.5 mm from each bike's widest point to its wall.
- The WARN VRX 25-S moves from the retired trailer garage. It clips to a quick-release plate on the front wall in
  front of each chock, 650 mm up, above the 500 mm ignition-free zone.
- The Black Widow MF-12038 ramp (3,048 mm, 34 kg) stands folded on its edge across the back, 8 mm inside the closed
  leaves, so it comes out first. With the bikes out the sill is about 864 mm up and the ramp sits at 16.5 degrees.
- The Tuareg loads first to the road side and is strapped from the empty Street Triple bay.
- **Tools.** Two aluminium chests ride on the wheel tubs: 780 x 300 x 200 mm on the road side and 780 x 220 x 200 mm on
  the kerb side, 81 L between them. That is low (their tops are 286.5 mm above the floor) and ahead of the ramp. The
  front corners are the obvious place, but the outer front straps run from there up to the handlebars, so the chests
  would block them. Report 17's under-tray boxes would be lower, but they sit outside the locked box and may share the
  space with the fuel tank. The kerb chest is narrower because the Street Triple's belly pan reaches 200 mm out from its
  centreline. Its lid sits under the kerb door's sill, so it opens with the bikes in.

## 8. Mass

The box's lines are calculated from the model's measured areas and lengths where they can be, and estimated where
not. The site page lists every line with its source.

| Group | kg | Main items |
|---|---|---|
| Body | 192.1 | Frame 53.3, wall skins 62.7, floor 43.0, roof 25.7, tubs 7.4 |
| Subframe and mounts | 70.5 | Steel crossmembers 19.2, aluminium crossmembers 18.2, runners 9.4, mounts 12.8 |
| Doors | 48.0 | Leaves 24.8, kerb door 12.0, cam bar 4.0, hinges 3.7, latches and seals 3.5 |
| Restraint, loading and safety | 99.0 | Ramp 34.0, chocks 23.6, winch 10.5, straps 8.0, coating and fixings 5.5, extinguisher 4.3 |
| Security | 13.4 | Anchors and chains 8.0, padlocks and hasps 2.8, disc locks and trackers 1.8, FMC130 and siren 0.8 |
| Tool chests | 10.0 | Two chests, estimate |
| **Box, empty** | **433.1** | **469.5 kg with growth, against report 17's 440 kg** |

The bikes add 206 kg (Tuareg, owner's figure), 9 kg of panniers (estimate) and 175 kg (Street Triple, owner's
figure). Their X and Y come from the bike models as parked, and their heights are report 03's design figures, 700 and
600 mm above the floor, which are higher than the report 05 estimates. The tools are 60 kg (estimate).

## 9. Results

The ute, from `build/ute/ute.json`:

| Case | Mass kg | Front kg | Rear kg | Rear with growth kg | Front share | CoG height mm | SSF |
|---|---|---|---|---|---|---|---|
| UC1 unladen | 2,818 | 1,361 | 1,457 | 1,509 | 48.3 % | 785 | 0.961 |
| UC2 bikes aboard | 3,428 | 1,427 | 2,001 | 2,084 | 41.6 % | 879 | 0.858 |
| UC3 towing with the bikes | 3,678 | 1,324 | 2,353 | 2,436 | 36.0 % | 849 | 0.888 |
| UC4 towing, bikes out | 3,288 | 1,335 | 1,952 | 2,033 | 40.6 % | 773 | 0.975 |
| UCB bikes in the trailer | 2,805 | 1,479 | 1,326 | 1,406 | 52.7 % | 715 | 1.054 |

- Weighed mass in UC3 3,678 kg against the plan's 3,850 kg, 3,796 kg with growth against the 4,200 kg GVM.
- Rear axle 2,436 kg with growth against 2,550 kg, a margin of 114 kg. It is the binding limit. Front axle at most
  1,462 kg with growth against 1,650 kg.
- Towball 250 kg against the plan's 250 kg and the towbar's 350 kg.
- The combination is 6,700 kg against the 6,900 kg GCM, the plan's figure with the ute at its 3,850 kg limit and the trailer at its 3,100 kg plate (GCM-01). On the model with the 3,100 kg trailer it is 6,528 kg, 6,646 kg with growth (UTE-06).
- Front axle share at least 35.8 % against Toyota's 20 %.
- SSF 0.858 with the bikes aboard against 1.054 with them in the trailer (case UCB), reported and not a failure. Report 17 found 1.02 and 0.82.
  Report 17 found 0.82 on a flat deck at about 1,050 mm.
- Unladen centre of gravity 785 mm against Toyota's 1,000 mm. Each rear wheel carries 1,218 kg with growth against its
  1,400 kg rating. Rear overhang 1,555 mm at the cam bar against 1,908 mm. The box is 40 mm behind the cab.
- The coupling point is set for 440 mm laden, plus or minus 20 mm, which gives 420 to 460 mm inside VSB1's 350 to
  460 mm (UTE-13). The box overhangs the ball by 210 mm, and the trailer's JK-01 and JK-02 check its sweep.

The box:

- Bike to bike 71.5 mm (limit 30). Tuareg to the nearest stowed item, the road tool chest, 39.5 mm. Street Triple to
  the kerb tool chest 25.5 mm (limit 15 for both). Each bike clears the door portal by 49.5 mm as it rolls out (limit
  15). The Tuareg at its photo-measured 2,263 mm clears the stowed ramp by 40.8 mm.
- Tyre clearances 25.0 mm over the tyre at full bump, 40.0 mm inside and 58.5 mm outside, against Toyota's 25, 40 and
  30 mm.
- Worst strap 280 kgf (the Tuareg's rear pair, sideways) against LC 1,000 kg, which is 2.75 kN at its anchor against
  20 kN. The chocks take 330 kgf (Tuareg) and 280 kgf (Street Triple) in braking.
- Deck mounts: 933 kg with growth on the subframe, its centre of gravity 593 mm above the brackets. Each firm bolt takes
  1.8 kN of shear in braking. The largest uplift on one bracket is 0.8 kN and the largest downward load 2.5 kN. The worst
  bolt uses about 6 % of its shear capacity, so the bolts are not the question. Toyota's brackets are.
- Ramp 16.5 degrees with the bikes out, 15.9 degrees at the laden floor height, against report 03's 20 degrees.
- The 23 load-path contacts touch without overlap: track on packer on steel crossmember on mount on Toyota's bracket.

### Failing checks and redesigns

- The first model run failed UGC-02 for the Street Triple: its belly pan overlapped the kerb tool chest by 4.2 L.
  The chest was 300 mm wide. It is now 220 mm wide, which leaves 25.5 mm.
- Two layouts were dropped before the model ran. Tool chests in the box's front corners would have covered the outer
  front strap anchors and blocked the straps. Chests 600 mm long there would also have run into the tubs.
- The track could not sit flush on a 38 mm steel crossmember without a floor support either side, so the 20 x 10 mm
  strips were added to carry the floor plate's edges.
- U1 carried the box as a 440 kg block on a 909 mm deck. U2 replaces it with the designed box on an 834 mm floor.

No check limit was changed and no estimate was changed to pass a check.

## 10. Assumptions

Where something is unknown the design takes the best assumption, records it here with its source, and carries on.

Phase U1, the ute:

1. Kerb mass 2,202.5 kg with 922.5 kg on the rear axle and the centre of gravity 700 mm up: the middle of Toyota's
   ranges for the GXL (BBGJ1007). The full 130 L fuel tank is in it.
2. Bull bar and winch 110 kg, towbar 35 kg, spare wheel 37.1 kg, two people 160 kg (report 16, estimates).
3. Towball 1,300 mm behind the rear axle (report 16 and the decision log 12:45, estimate). Revision A used report
   17's 1,350 mm.
4. Rails 1,046 mm over their outsides, with 60 mm flanges (estimate from the frame drawing).
5. Tyre static loaded radius 380 mm, about 22 mm of deflection (estimate).

Phase U2, the box:

6. Rear frame top 774 mm above the ground laden: 724 mm on factory springs (BBGJ1007 pp. 55 and 62) plus about 50 mm
   of Lovells lift (estimate). It sets the floor height.
7. Rear wheel travel to the bump stops 110 mm with the Lovells kit (report 17 section 3.3, estimate). It sets the tub
   height.
8. Tub ends 30 mm fore and aft of the tyre: Toyota's outside figure, as Toyota gives none for these.
9. All six brackets on the frame drawing behind the cab are deck mounts, not spring hangers (report 17 section 1.4).
   Each takes an M12 bolt through a flange about 60 mm out from the rail, its top level with the rail top.
10. With the bikes out, the floor rises about 30 mm (report 17: 1,080 mm empty against 1,050 mm laden).
11. Bike centre of gravity heights 700 mm (Tuareg) and 600 mm (Street Triple) above the floor (report 03). Panniers
    9 kg (estimate).
12. The 60 kg of tools fits in the two chests' 81 L (report 17 open question 5 gives 0.3 m3 for it, so bulky recovery
    gear may need the space beside the ramp).
13. Report 03's factored restraint cases apply to the box on its mounts, with the box rigid and the firm mounts taking
    all the horizontal load.
14. Hardware masses (hinges, cam bar, latches, seals, mounts, lamps, chests, security) are estimates. The cam bar,
    shoot bolts, hinges, disc locks, anchors, siren and fan are products still to choose.
15. The rear lamps and the number plate move from the cab chassis's lamp bracket to the box, which ends 1,510 mm
    behind the rear axle (1,555 mm at the cam bar).
16. A body on Toyota's deck mounts, inside these limits and the upgraded GVM, needs no separate VSB 14 certificate. The
    GVM certifier inspects it and its winch with the vehicle in one LC5 inspection, under VSI 06 items 27 (the body), 34
    (body mountings the maker did not design) and 35 (the winch as a powered goods loading device) (report 17 section
    1.4, decision log 12:45).

## 11. What the engineer checks

1. The floor height and bump travel on the bought ute with its kit and tyres (assumptions 6 and 7). If the tubs would
   stand over 100 mm, the box goes to the flat deck at about 1,080 mm and the checks run again.
2. Which brackets are deck mounts, their capacity, and the bolt size they take (assumption 9). UGM-02 lists the
   loads.
3. The compliant mount: cushion product, preload and travel, and whether the rear steel crossmember's station
   should be firm.
4. The welded frame at welded strength (report 17 section 2.5), the skins between the posts, and the floor plate
   between crossmembers under a bike's wheel.
5. The steel crossmember joints to the aluminium runners, and their isolation.
6. The L-track bolting into the steel crossmembers for 20 kN per anchor.
7. The door portal, the hinges and the cam bar keepers under the load restraint cases.
8. The LSPV (load sensing proportioning valve) reset after the body is fitted (report 16).
9. The coupling height, set for 440 mm laden, plus or minus 20 mm, against VSB1's 460 mm.
10. Whether the 0.858 static stability factor is acceptable for the planned driving.

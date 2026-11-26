# 30. Services routing: the 3D wiring and plumbing plans (H28)

Every cable and pipe of the home trailer is a run in `data/routes.yaml`. `cad/routes.py` resolves each run on the
solved layout, gives it a centreline with real bends, sizes it, measures it and checks it (SVC-01 to SVC-12).
`cad/routes_model.py` sweeps the runs into the two viewer models, `trailer-electrical` and `trailer-plumbing`, and
writes the schedules for the Electrical and Plumbing pages. CT-602 and CT-612 draw the same centrelines in plan.

## 1. What a run is

A run has an id, a system, what it feeds, its two ends (a line of the layout or a fixture, and a point on that line's
envelope box), its cable or pipe kind, its protection and its path. The path's points are expressions on the layout's
parameters, boxes and glands (`data/services.yaml`), so a run follows the layout when it changes. A point written `.`
keeps the previous point's value. `lane` offsets runs that share a way by 14 mm. Runs may name the parts they pass
through by design (`passes`), the parts they are clipped to (`along`, touching allowed) and the closed chassis members
they are threaded through (`inside`).

## 2. Cables: sizes, mass, price and bend radii

- Conductor data: Prysmian's V-90 0.6/1 kV PVC single-core table gives each size's outside diameter, mass and least
  installed bending radius, and its AS/NZS 3008.1.1 ratings enclosed and in free air with the single-phase drop in
  mV/A.m at 75 C, which is the two-wire DC drop ([Prysmian, PVC insulated 0.6/1 kV](https://australia.prysmian.com/sites/australia.prysmian.com/files/media/products/pvc-insulated-0-61-kv.pdf)).
  Twin and pair kinds use two of those cores. Flexible cords use 6 times their diameter (Helukabel's rule for flexing
  cable), and the 7-core trailer cable and the data cables their makers' radii. The `twin` sheath bends at 4 times its
  outside diameter.
- DC sizing: each 12 V, 24 V and 48 V circuit takes the smallest size whose rating carries its design current and whose
  drop at the routed length is at most 2 % (report 20 section 6). That is stricter than AS/NZS 3000:2018's limit for
  extra-low voltage. 1.5 mm2 is the smallest size used, for strength. The 48 V main cables keep report 20's sizes.
- 230 V: round TPS, Prysmian's 450/750 V 2C+E orange circular to AS/NZS 5000.2, 9.8 mm across in 2.5 mm2 and 10.8 mm
  in 4 mm2, 200 and 250 kg a km, installed bending radius 40 and 45 mm ([Prysmian AU00_2CE_OC_450V](https://australia.prysmian.com/sites/australia.prysmian.com/files/media/products/AU00_2CE_OC_450V_0.pdf)),
  so it seals in the glands and in an RM 15 module (3 to 11 mm) (I2-29). AS/NZS 3008.1.1 rates a cable by its
  conductor, insulation and installation, so Prysmian's 0.6/1 kV 2C+E ratings hold for it. 2.5 mm2, 4 mm2 where 2.5 mm2
  is rated under the current or its breaker where it lies (A-02, C1 and C4, SVC-10), within the 5 % drop of AS/NZS
  3000:2018 clause 3.6.2. A-01, the MultiPlus-II's AC-out-1 to the board, runs alone, apart from the 230 V group:
  clipped down the partition beside the dryer and round the pressure gauge SN-02, across the end slot and through a
  module of its own in G20 and G15, so it is grouped with no other circuit. Its protection is a 25 A two-pole breaker
  as the board's main switch, the fuse or breaker in series with AC-out-1 that Victron's installation manual asks for
  ([MultiPlus-II 4k5/6k5 GX, section 8.4](https://www.victronenergy.com/media/pg/MultiPlus-II_4k5_6k5_GX/en/installation.html)).
  It is over the board's managed peak, 5,465 W on the all-electric cold day (report 20 section 4), 23.8 A, and its
  4 mm2 is rated 28.1 A under the floor at 45 C. In the bunched conduit it would need 10 mm2, 16.1 to 16.8 mm across
  ([Prysmian's 2C+E PVC circular](https://australia.prysmian.com)), an RM 30 in each frame in place of an RM 15. 6 mm2 on a 32 A
  breaker is 11.8 mm across, past an RM 15's 11 mm, and is rated 31 A where it crosses the floor.
- Ratings, SVC-10 (I2-15 b): no run line names its installation method. Each stretch of a run takes a zone from where
  it lies, in this order: inside a chassis member it is threaded through, crossing a panel's foam core, under the floor,
  on the drawbar, outside the body, in the board cabinet, in the battery box, in a 230 V conduit, in the ceiling's
  cable covers, else in the cabin. The zone gives the method and the air round the cable on the design hot day (report
  19: 42 C in the shade at 15:00, the split holding 24 C inside): 45 C under the floor and in the members (est.), 50 C
  in a foam core and on the drawbar (est.), 60 C on the sunlit skin (est.), AS/NZS 3008.1.1's 40 C reference inside.
  The twin DC cables take Tycab's tinned V90 ratings to JASO D609 in free air at 30 C, times 0.8 for the circuit's two
  cores together, Tycab's bundling factors and its ambient table ([Tycab marine cable brochure 2017](https://www.ceca.au/uploads/1/3/7/6/13767324/tycab_marine_brochure_2017_web_23.pdf)).
  Each size has its Tycab code in data/routes.yaml: the 0.6/1 kV single core FVK up to 6 mm2 and the battery cable MBS
  from 8 B&S, so 10 mm2 takes MBS132002's 84 A and the table rises with size. Only 25 mm2 is an estimate, between
  MBS128703 at 20.26 mm2 and MBS136403 at 25.7 mm2 by area. Tycab's twin battery cables are 0.8 of its single cores
  (59 A at 7.7 mm2, 82 A at 13.5 mm2), which is the pair factor. Tycab gives its double-insulated range ZDT no rating,
  so the 48 V double-insulated pairs take AS/NZS 3008.1.1's ratings for two V-90 insulated and sheathed single cores, a
  circuit, from Prysmian's table at every size from 4 to 95 mm2, with the standard's own ambient factor (I2-31).
  The 230 V take Prysmian's 2C+E circular ratings, unenclosed and spaced in 40 C air, with the ambient factor the square
  root of (75 - t) over 35 ([Prysmian 2C+E PVC circular](https://nz.prysmian.com/sites/nz.prysmian.com/files/media/documents/2ce-pvc-circular.pdf)). A method's ratio to free air
  at the same size comes from Prysmian's AS/NZS 3008.1.1 single-core table. Groups take AS/NZS 3008.1.1 Table 22:
  bunched in the 230 V conduits, a single layer in the DC ways and under the ceiling. A circuit at or under 30 % of its
  rating is not counted (IEC 60364-5-52), nor data and control cables, and the circuits the load shedding never runs
  together count once. A short crossing of foam at a gland (100 mm at most) takes BS 7671 Table 52.2's factor (0.88
  over 50 mm, 0.78 over 100 mm) with no group's factor. Each run's Iz is its least stretch, its zones read every 10 mm
  along it. Ib <= In <= Iz (AS/NZS 3000 clause 2.5.3), and a run with a design current and no device fails unless its
  line says why it cannot be overloaded (I2-31). The LUNOS controller's fan leads take B-01's 3 A fuse ahead of it, and
  the split's indoor-outdoor link A-05 carries only the indoor unit's own load. A run that sizes itself grows until its
  stretches carry its current and its device.
- SVC-10's sizes: D-07 (144 A, the MultiPlus-II 48/6k5 at 6 kW) goes from 50 to 95 mm2, because its 200 A MEGA, sized
  for the inverter's 11 kW minute, must sit under the pair's rating, and 70 mm2 gives 170 A enclosed in the board. D-13
  goes from 16 to 25 mm2 under its 80 A fuse. The five module pairs D-01 to D-05 share D-06's 150 A, 30 A each and 25 %
  for uneven sharing (est.), on 60 A MEGAs at the busbar, so their 25 mm2 stays. Those five fuses add to 300 A, so D-06,
  the bank's cable through the isolator to the BMS, has its own 200 A MEGA in the six-way holder's sixth way, as large
  as D-07's so the bank's fuse is never the smaller of the two, and goes from 70 to 95 mm2, since 70 mm2 is rated 170 A
  where it is cleated in the board cabinet (I2-31). A sixth module then adds a single MEGA holder on the busbar.
- Mass and price: the routed length times the kind's mass and price per metre, plus 10 % for cut-offs in the price.
  The line that prices each kind is `priced_in` (BD-11 for the house wiring and pipework, EL-07 for the 48 V mains,
  RF-02 for the PV strings, LGT-01 for the lamp loom, AC-03 for the split's line set and condensate hose, UF-06 for the
  diesel line).

## 3. Pipes and hoses

- 12 mm PEX barrier pipe with push-fit fittings. John Guest gives a least bend radius for PEX held in clips. The model
  bends PEX at 130 mm and turns it at a push-fit elbow where a bend that size does not fit, which counts as a fitting
  ([John Guest, installing Speedfit pipework](https://www2.williamwilson.co.uk/dbdocument/1790/Speedfit-Web---Installing-Pipework-0212.pdf),
  [technical specification, minimum bend radii](https://nonprod.docs.rs-online.com/dac7/0900766b803a8529.pdf)).
- Hoses (20 mm fill and balance, 12 mm pump feed, vent and drain hoses) bend at their own radius and turn at a barbed
  elbow where the radius does not fit, as at the tanks' spigots.
- DN40 DWV is rigid: every corner is a bend fitting.
- Every gravity waste falls at least 1:50 (2 %), a little more than the 1.65 % least grade AS/NZS 3500.2 gives a DN40
  fixture discharge pipe. `_apply_fall` lowers each leg so the fall holds, keeping the tank inlet where it is.

## 4. The ways, from the solved layout

- Under the floor nothing crosses a rail: the raiser's top is 21 mm under the floor. Every floor gland that reaches the
  tanks is between the rails, and the 230 V runs in its own conduit there.
- The tank guard closes the gaps beside the fresh tanks from below, so the fill reaches the front tank only from the
  front: G12 is in the floor under the bed's rear end, in front of CM-04, and the hose enters the tank's front face.
  The two tanks share a balance hose over CM-05 on dip tubes to their sumps.
- it2-interior's arm hangers fill the outside of the rails through both wheel bays. The marker lamps' looms K-08 and
  K-09 rise inboard of the rails behind the grey tank, enter the raisers through their inner webs and run inside them
  in the inboard lane, then turn square across them into the outriggers OR-05 through a round hole on the outrigger's
  centre line: a lamp cable bends at 57 mm, so a turn from the outer lane, 10 mm from the web, meets the web on a
  slant and its slot reaches the outrigger's root weld. The lamp loom K-01 and the brake circuit K-10 leave the road
  rail through its outer web, never its bottom face (CHS-10). The ute feed D-14, the compressor feed B-16 and the
  breakaway feed B-18 run inside the kerb raiser RS-K, clear of its seam with the rail. Each enters through a
  slotted hole in the face it arrives at, ahead of CM-02 (B-16 and B-18 the inner face, D-14 from the drawbar the outer
  face, riding 16 mm higher there so B-16 can rise to its exit under it). Each leaves through the raiser's inner web
  on a slant ahead of the kerb frame G20 (CHS-10), runs rearward in the gap between the raiser and the rear tank against
  the raiser, D-14 lowest at Z 777, 20 mm over the rear kerb airbag's top bracket and with room under the floor for
  its 110 mm bend, B-16 at Z 802 and B-18 at Z 843, and rises into G20's outboard row. The chase's loom (B-15, E-07,
  B-04, B-05) rides inboard of them and crosses the end slot at four heights, and the tank senders N-08 and N-09
  come forward from the kerb frame in the UF way's lanes over the same bracket (SVC-13).
  SVC-01 also tests every chassis fitting with no box of its own at each of its positions (cad/chassis.py
  `fitting_boxes`): the drawbar root gussets, the recovery lugs and tongues, the plates, the D-rings, and each corner
  steady over the box its leg sweeps from folded to standing. The drawbar's lamp and brake looms and the ute feed run
  along the A-frame members' outer faces, clipped to them, under the root gussets that stand on the members' top
  faces, and leave them for the rails' outer line in the last 260 mm before the body front. The kerb front lamp loom K-07 comes down outboard of K-10 and crosses the A-frame
  lying on the angle SP-FD, hung 15 mm under the drawbar members' rear ends. The front bay's cables to the kerb corner
  and the front fans (C9B, E-07, B-04, B-05) cross the rails through grommeted holes in both webs, 32 to 48 mm under
  the rails' tops, C9B and B-05 under the XT Air box and E-07 and B-04 behind it, where they used to dip to 400 to
  430 mm under the drawbar members, and B-18 rides over the drawbar's cross brace, clipped to it (I2-41). The ute feed D-14 runs straight along
  the kerb drawbar member's outer face at Z 523, P-clipped to it inside the jockey's bracket plate CH-P11 between the
  two rows of the plate's spacer tubes, which the routes take as the four 25 mm tubes they are (DB-08), where it
  dipped to 430.8 mm under them as one block (I2-53). The running
  clearance and the breakover (DIM-04, DIM-06, DIM-07) take every fixture and run at its outside diameter, as FIT-05
  does. Every hole in a chassis member and every floor
  cut-out over 60 mm is listed in `data/services.yaml` (`holes`, `cutouts`) with its member or panel, point and size.
  SVC-01 skips the parts welded to a member while a run is inside it.
- The brake circuit (I2-50, I2-61). Bosch's TSC drives the magnets from its own supply on the truck's brake request
  (Y265K30237 v4.0, its power harness), and the 12-pin flat's brake pin is a small pin rated 15 A (ARK FPP12, report
  08), under the four magnets' 16 A. So the supply comes from the truck's battery through an Anderson SB50 beside the
  plug, as report 08 section 3.5 asks for a stability control's heavy current, and pin 5 carries the brake request
  only. Bosch's guideline puts a fuse of 40 A at most between the trailer's supply terminal and the TSC harness's
  supply wire (page 6), so a 30 A MIDI fuse stands in the drawbar junction between K-14 and K-10, and its 2.4 milliohm
  with its lugs (est.) is counted in the drop (`inline`). The SB50's 1.28 m lead K-14 (6 B&S twin) and the 12-pin's
  own 1.34 m lead K-13 hang between the vehicles (`rides: between`), so SVC-12 leaves them out, and SVC-06 adds K-14's
  drop and the fuse's to K-10's (`follows`): 0.58 %, 0.32 % and 1.07 % with K-10 at 25 mm2, 1.96 % against 2 %, in two
  30 mm holes in the road rail. An 8 B&S lead would take them to 2.3 %. The 5 % from the truck's battery to the TSC,
  the truck feed's 3 % and the trailer's 2 %, is the design's own, half the 10 % of AS/NZS 3000:2018 clause 7.5.7 for
  extra-low voltage, and SVC-06 holds the TSC at its 10.5 V floor (est.) at 16 A from 12.0 V (I2-62). Coupled, each
  lead is clamped on the leads' bracket DB-HK, whose top plate reaches ahead of the stone guard, and its span from the
  truck's socket runs up over a lined seat at the tip of its own sprung arm, strapped there, and down to the clamp
  (`lift`, I2-78). From the clamp it runs clipped along the drawbar member to the junction. cad/routes.py lifted
  reads each span as two flexible catenaries of fixed length, from the plug to the seat and from the seat to the
  clamp, each pulling with its horizontal pull plus the weight under it, the strap turning with the seat as the arm
  swings (I2-83), and rests the arm where its torsion spring's torque balances them, over every turn and pitch of
  rules.between (est.). The strap stands at the seat's top with the arm 15 degrees below level, the seat runs 155
  degrees ahead of it and 40 behind, and both arms take one spring of 1.5 to 1.0 N m (CT-601). A lead lying loose
  over a saddle or a free sheave gives its slack to the long span from the truck, which pulls hardest, which is why
  the friction band and the sheave's one height were dropped. The cuts, 1.34 m for K-13 and 1.28 m for K-14, leave no
  position taut with 30 mm taken off. DIM-08 reads the lowest point of every part of each lead, from the plug
  over the seat to the clamp and along the drawbar. The least in any turn is at a plug, K-13 no lower than 397 mm
  and K-14 394 mm, 377 and 374 mm with the truck's ball at its low 420 mm, so DIM-08 holds both to DIM-06's 200 mm.
  The spans can sag under their plugs, though. With the truck pitched up relative to the trailer, K-13's span from
  its plug to its seat hangs up to 62 mm under the plug, and in 41 of its 261 positions at the design ball one of
  its spans hangs under the plug, the lead no lower than 432 mm there (est.). Each seat is held on its arm by a web
  cut from 1.6 mm 5052 sheet, a hub bolted through the arm's tip with two M5 bolts and three spokes riveted to the
  channel, and weighs 0.057 kg on K-13's arm and 0.085 kg on K-14's (`seat`, cad/routes.py seat_parts, est.).
  TR-13 measures the leads coupled on 300 mm ramps, each vehicle at its own attitude, where cad/routes.py on_ramps
  reads 439 mm at the least, K-13's span from its plug at full lock (I2-91). Each
  drum's lead runs from its side's junction behind the TSC, a front drum's forward under the TSC and the front tank's
  guard, to a P-clip at its arm's inner bush on a bracket from the hinge crossmember, 100 mm from the centreline,
  101 mm under the pivot and 50 mm inboard of the arm's pivot tube, then in a loop under the inner hinge plate to
  Cruisemaster's harness tray on the A-frame's inner leg (33XT AIR sheet 4 step 7) and along it to the backing plate,
  tied in the tray, its loop long enough for the arm's travel (cad/routes.py lead_slack). The clip stands low enough
  that its loop keeps SVC-01's 20 mm from the arm's hinge plates over the arm's travel, which SVC-13 reads (cad/routes.py
  loop_gaps), 20.3 mm at its least under the inner plate. cad/routes.py lays that arm part on the arm at ride height and
  FIT-05 sweeps it with the arm through its travel (`rides: arm`), 82.0 mm clear at its least. The leads are 2.5 mm2
  (est.), so the front drums' 1.9 m keep 2 % from the TSC with Bosch's harness ahead of them, 1.19 % at the brake.
- The desk reaches the floor, so its outlets and USB panel are in a power module in the desk top, fed up the front
  wall's kerb corner (G17 for 230 V, G23 for 24 V, 70 mm apart) and through the desk's front leg. The e2 fans C and D
  have their own glands under them (G16, G18).
- The road gap beside the rear fresh tank holds the road frame G15 and the slot over CM-06 carries the 230 V and
  D-07. So the wet room's kerb-half fittings (basin, flush, washer tap) are fed from a manifold in the shower's road
  corner (WT-MAN) across the wet room's ceiling over the inner door. The washer's and the dryer's pumped drains
  discharge into the basin. The basin, the shower well and the floor waste drop straight into the grey tank's top.
  The drip tray's drain W-09 joins the basin's waste below its trap, so it passes a Wavin HepvO 32 mm waterless trap
  valve. Its membrane seals with no water to dry out, and Wavin asks for it as close to the appliance as practicable
  ([HepvO in recreational vehicles](https://mediahub.wavin.com/m/1684dc1cbc414752/original/Data-Sheet-HepvO-in-recreational-vehicles.pdf),
  read 23 Nov 2026), so the grey tank's air stops there (I2-45). The valve BV1 is 181 mm long and 64 mm across its
  inlet nut, and with its 87.5 degree knuckle adaptor BV11 it reaches 217 mm from the knuckle's inlet axis (Wavin
  Osma's HepvO product and installation guide), about 275 mm with a 32 mm bend and a hose tail at its outlet (est.),
  where W-09 could drop only 217 mm over the wet room's floor tray. So W-09 comes through the partition 70 mm in from
  the tray's road side corner, clear of A-01, and the knuckle turns the valve along the wet face under the basin, its
  axis 45 mm off the face, arrows underneath and falling at the knuckle's 2.5 degrees, as Wavin allows for a
  horizontal valve. The bend turns the hose down beside the cassette bin, 37 mm clear of it, and it runs
  back to the Y junction (I2-52).
- The road frame G15 stands in the corner between the aisle LA-K4's end and the partition, X 4,978 to 5,161 and Y 450
  to 594 with its rim, clear of the aisle (SVC-09) and inboard of the road raiser. The bench's plinth is notched over
  its front edge (see section 7).

## 5. Checks and their limits

| Check | Rule | Source |
|---|---|---|
| SVC-01 | 20 mm from every envelope box but the run's own ends, and from the keep-clear boxes (aisles, landings, the chair space) above the floor up to 60 mm under the ceiling (est., the ceiling's cable covers), over which the cables cross in that zone | the brief (H28), H27, I2-14 |
| SVC-02 | each bend at or above the least bending radius, or a fitting | makers' tables (sections 2, 3) |
| SVC-03 | 230 V 50 mm from ELV outside its conduit, 150 mm reach at the board and shared appliances | AS/NZS 3000:2018 clause 3.9.8.3, AS/NZS 3001.2:2022 |
| SVC-04 | no water, waste or diesel line within 300 mm of the battery's terminal face, but the washer's sleeved hoses (W-02, F-10) and the tray's sleeved drain (W-09), and none over the face inside a cone widening 1 in 5 (est., parked up to about 11 degrees off level) unless the drip tray EL-09 lies between, read from the tray's own box | AS/NZS 3001.2:2022 clause 5.4.10.2, CT-602, the cone the design's own (I2-18 c, I2-35) |
| SVC-05 | every circuit, DC load, outlet, water outlet and fitting has its run, the runs of each tag join up end to end, and each 230 V circuit runs from the board's AC bar to its load or the outlet it plugs into | data/services.yaml, report 20 section 7 |
| SVC-06 | DC drop at most 2 % at the design current, the ute's half of the ute feed (TW06) added, 230 V at most 5 %, the TSC's supply 2 % from the truck's socket and TW07 3 % of its own, the TSC at least 10.5 V (est.) | the design's own 2 %, stricter than AS/NZS 3000, and AS/NZS 3000:2018 clause 3.6.2 for 230 V. The TSC's 5 % from the truck's battery is the design's own, half of clause 7.5.7's 10 % for extra-low voltage |
| SVC-07 | gravity wastes fall at least 1:50 | AS/NZS 3500.2, CT-611, CT-612 |
| SVC-08 | each run its radius plus 5 mm (est.) from every other, cables of one band in a shared way may touch. Cold water, vents and diesel 25 mm from 230 V, hot water before the mixing valve and wastes 50 mm from 230 V and 25 mm from extra-low-voltage cables above the floor (a solvent-welded DWV waste keeps the gap), and no wet line over a 230 V run within 25 mm in plan | IB 052/2015 for cold water (25 mm), the design's own rule for the rest (IB 052/2015 asks 100 mm for heated water and drains in a building) |
| SVC-09 | every gland's fitting has room in its panel: 12 mm (est.) of spanner room round a locknut, a 10 mm (est.) web elsewhere, no floor fitting in a keep-clear box or under a part on the floor | CMP Products' locknuts by thread, Roxtec CF 8 for the frames' proportions |
| SVC-10 | each cable's design current and its protective device at most its rating where it lies, Ib <= In <= Iz, every stretch rated for its zone's method and air and derated for its group (section 2) | AS/NZS 3000:2018 clause 2.5.3, AS/NZS 3008.1.1 (Table 22), Prysmian, Tycab (JASO D609), BS 7671 Table 52.2, IEC 60364-5-52 (I2-15 b) |
| SVC-11 | every cable 25 mm (ELV) or 50 mm (230 V) from the hot line H-01 before the mixing valve, under the floor too, nothing under the Combi's base, cables and the fuel line 50 mm (est.) from the 100 mm behind it where the exhaust runs to its cowl, cables and pipes 50 mm (est.) from the oven's case inside the tower, but the oven's own lead | Truma Combi D 6 AU installation instructions, IB 052/2015 halved as SVC-08's (I2-18 d) |
| SVC-12 | no cable unsupported over 600 mm: held inside a member it is threaded through, by a clip within 30 mm (est.) of a part it runs along or a support the design adds (the SP fixtures), in the board, a conduit, a box it ends at, a gland or a frame, or by its loom in a shared way. Inside a cabinet only within 30 mm of a panel it is clipped to, and under the floor a 230 V cable only inside its modelled conduit | VSB1 section 7.1 (I2-18 a, I2-36) |

The checks are defined in `data/routes.yaml` beside the runs, as the lamps' checks live in `data/services.yaml`,
because `data/checks.yaml`'s trailer check types are fixed in `cad/partsdb.py`. The build adds their rows to the
trailer's checks (`build/trailer/trailer.json`) and `cad/tests/test_routes.py` fails on any of them.

The floor's multi-cable penetrations are three Roxtec RM transit frames (data/services.yaml, line BD-25): the kerb
frame G20 in the plinth's end slot, over the 135.5 mm gap between the kerb raiser and the rear tank, whose kerb side
stands 36 mm inboard of the front tank's for it, the road frame G15 under the MultiPlus-II and the Combi's frame G9 in the 90 mm of floor between the chair
space and the aisle. Roxtec's C wedge, which compresses the modules, fits packing spaces 60 and 120 mm wide only,
takes 34 mm of the stack and is 84 mm deep, and Roxtec's S frames come with packing spaces 60 or 120 mm wide and 60,
120, 180 or 240 mm long ([Roxtec C wedge](https://www.roxtec.com/de/produkte/systemkomponenten/dichtkomponenten/roxtec-keildichtung-und-keildichtungskit-c/),
Roxtec's S frame tables, read 23 Nov 2026). G9 has the S 3x1's 60 x 120 mm with a C wedge 60 at the packing's end,
and G15 the S 4x1's 120 x 120 mm with a C wedge 120 inside its stack, behind the sink waste W-01 and the pump feed
F-03 and ahead of D-07 and the six 230 V cables. Roxtec allows the wedge anywhere in the frame and asks for a
stayplate on every finished row and two before the last ([installation instructions 124037 rev A](https://varaldur-prod.fra1.cdn.digitaloceanspaces.com/varaldur-prod/media/pim_files/11DF0BD2-D507-46A0-921F-78A5E1448020.pdf),
read 23 Nov 2026). G20 has the S 4x1's 120 x 120 mm too, its stack across the trailer and its C wedge 120 at the
inboard end over the rear tank. In each row the cables that run forward under the floor lie at the front and the ones
that run back to the crossing behind the tank at the rear: the raiser cables along the raiser, the 12 V and 24 V loom
and D-07 at the front, the 230 V group and A-01 at the rear, and the three tank senders in the inboard row. In each
column a cable that crosses the end slot lower lies further outboard, so none passes under another's turn (I2-33,
I2-40). Each frame is modelled at its real depth
(cad/routes.py frame_solids) and stands 30 mm on the floor, and SVC-01 keeps every other run 20 mm from each body and
wedge and no frame inside a part or a bearer strip (I2-33, I2-34). SVC-08, SVC-10 and SVC-11 take each frame's whole
room, its wedge's included, so a module behind the wedge is inside the frame. Each module is sized to its run (RM 15 for 3 to 11 mm, RM 20 for 4 to 14.5 mm, RM 30, RM 40 and
RM 60, Roxtec's product page) and the rest of each packing space is filled with solid modules. The frames are
compressed from above, so nothing is turned under the floor, and stayplates part the 230 V rows from the rest. The
modules seal round cable only, so every run through a frame or a gland is round. SVC-08 does not measure two runs
inside a frame both pass, each in its own module, nor inside the board cabinet, where the control and branch cables
lie in a 60 x 80 mm slotted duct sized to their fill (EL-06) and the four heavy cables are cleated to the panel.
Round glands take nylon cable glands of their hole's thread with CMP's locknut sizes, which SVC-09 spaces.

## 6. Results on the solved layout

All thirteen checks pass. The closest approach of a run to any envelope box is 20.4 mm (SVC-01), the tightest bends,
C8's and C9's right-angle turns, allow exactly their 40 mm least radius (SVC-02), the 230 V keeps 61.8 mm from extra-low voltage (SVC-03), the
nearest wet line is 344 mm from the terminal face (SVC-04) and every one of the 101 needs is served (SVC-05). The
governing drop is D-14's 1.98 % of 2 % (SVC-06). The TSC's supply holds its 2 % from the truck's socket to the TSC,
1.96 % with its fuse, and the truck's own feed to that socket, car build line TW07, 2.03 % of its own 3 %, so the TSC
sees 11.52 V from a 12.0 V battery, over its 10.5 V floor. The flattest waste falls
1:50 (SVC-07), no two of the 72 pairs measured overlap (SVC-08), the gland fittings keep 23.4 mm over their spacing
(SVC-09), the closest cable to its rating keeps 0.1 A (SVC-10), the cables keep 133.4 mm over their distance from the
hot surfaces (SVC-11), the longest unsupported span is 597 mm against 600 mm (SVC-12) and every run keeps 20.0 mm
from the XT kit's parts, D-14 the closest, at the rear kerb airbag's top bracket, and each drum lead's loop 20.3 mm from its arm's inner hinge plate over the arm's travel (SVC-13). The routed cables are
285.0 m and 62.4 kg, the pipes and hoses 50.9 m and 6.0 kg with 73 fittings.

## 7. Open items

- The routed 230 V TPS and cords (76 m) are longer than BD-11's 40 m, the PEX (35 m) longer than its 30 m, and its 47
  fittings more than 40. BD-11's price items are in `data/assemblies/trailer.yaml` and are to be raised with this
  model as their source. The wastes (3.0 m of DWV with 12 bends, 2.5 m of drain hose) are not priced yet.
- The bench's plinth is notched over G15's front edge, where the frame stands 30 mm proud of the floor and its C wedge
  54 mm.
- Moving the SVC checks into `data/checks.yaml` needs a `services` type in `cad/partsdb.py` and one branch in
  `Trailer.checks` that calls `cad/routes_model.check_rows`.

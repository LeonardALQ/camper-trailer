# 30. Services routing: the 3D wiring and plumbing plans (H28)

Every cable and pipe of the home trailer is a run in `data/routes.yaml`. `cad/routes.py` resolves each run on the
solved layout, gives it a centreline with real bends, sizes it, measures it and checks it (SVC-01 to SVC-07).
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
  Twin and pair kinds use two of those cores; flexible cords use 6 times their diameter (Helukabel's rule for flexing
  cable), and the 7-core trailer cable and the data cables their makers' radii. The `twin` sheath bends at 4 times its
  outside diameter.
- DC sizing: each 12 V, 24 V and 48 V circuit takes the smallest size whose rating carries its design current and whose
  drop at the routed length is at most 2 % (report 20 section 6). That is stricter than AS/NZS 3000:2018's limit for
  extra-low voltage. 1.5 mm2 is the smallest size used, for strength. The 48 V main cables keep report 20's sizes.
- 230 V: 2.5 mm2 TPS, 4 mm2 where 2.5 mm2 is rated under the current in the bulkhead (A-01, 26 A), within the 5 % drop
  of AS/NZS 3000:2018 clause 3.6.2.
- Mass and price: the routed length times the kind's mass and price per metre, plus 10 % for cut-offs in the price.
  The line that prices each kind is `priced_in` (BD-11 for the house wiring and pipework, EL-07 for the 48 V mains,
  RF-02 for the PV strings, LGT-01 for the lamp loom, AC-03 for the split's line set and condensate hose, UF-06 for the
  diesel line).

## 3. Pipes and hoses

- 12 mm PEX barrier pipe with push-fit fittings. John Guest gives a least bend radius for PEX held in clips; the model
  bends PEX at 130 mm and turns it at a push-fit elbow where a bend that size does not fit, which counts as a fitting
  ([John Guest, installing Speedfit pipework](https://www2.williamwilson.co.uk/dbdocument/1790/Speedfit-Web---Installing-Pipework-0212.pdf);
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
- it2-interior's arm hangers fill the outside of the rails through both wheel bays. The ute feed, the compressor and
  breakaway cables and the lamp looms run inside the rails there and leave them through the raiser and the outrigger
  (OR-05) or at G8. SVC-01 skips the parts welded to a member while a run is inside it.
- The desk reaches the floor, so its outlets and USB panel are in a power module in the desk top, fed up the front
  wall's kerb corner (G17 for 230 V, G23 for 24 V, 70 mm apart) and through the desk's front leg. The e2 fans C and D
  have their own glands under them (G16, G18).
- The road gap beside the rear fresh tank holds G10, G11, G14 and G15 and the slot over CM-06 carries the 230 V and
  D-07. So the wet room's kerb-half fittings (basin, flush, washer tap) are fed from a manifold in the shower's road
  corner (WT-MAN) across the wet room's ceiling over the inner door. The washer's and the dryer's pumped drains
  discharge into the basin; the basin, the shower well and the floor waste drop straight into the grey tank's top.
- The glands G10, G11, G14 and G15 sit at the bench's front edge (Y 515 to 585), the only floor inboard of the road rail
  there. The bench's plinth has to cover them (see section 7).

## 5. Checks and their limits

| Check | Rule | Source |
|---|---|---|
| SVC-01 | 20 mm from every envelope box but the run's own ends | the brief (H28), H27 |
| SVC-02 | each bend at or above the least bending radius, or a fitting | makers' tables (sections 2, 3) |
| SVC-03 | 230 V 50 mm from ELV outside its conduit, 150 mm reach at the board and shared appliances | AS/NZS 3000:2018 clause 3.9.8.3, AS/NZS 3001.2:2022 |
| SVC-04 | no water, waste or diesel line within 300 mm of the battery's terminal face, but the washer's sleeved hoses (W-02, F-10) | AS/NZS 3001.2:2022 clause 5.4.10.2, CT-602 |
| SVC-05 | every circuit, DC load, outlet, water outlet and fitting has its run | data/services.yaml, report 20 section 7 |
| SVC-06 | DC drop at most 2 %, 230 V at most 5 % | report 20, AS/NZS 3000:2018 clause 3.6.2 |
| SVC-07 | gravity wastes fall at least 1:50 | AS/NZS 3500.2, CT-611, CT-612 |

The checks are defined in `data/routes.yaml` beside the runs, as the lamps' checks live in `data/services.yaml`,
because `data/checks.yaml`'s trailer check types are fixed in `cad/partsdb.py`. The build adds their rows to the
trailer's checks (`build/trailer/trailer.json`) and `cad/tests/test_routes.py` fails on any of them.

## 6. Results on the solved layout

All seven checks pass: the closest approach to any envelope box is 20.3 mm, the tightest bend has 0.1 mm to spare,
the 230 V keeps 56.8 mm from extra-low voltage, the nearest wet line is 344 mm from the terminal face, every one of
the 101 needs is served, the governing drop is 1.93 % of 2 % (E-13) and the flattest waste falls 1:50. The routed
cables are 284 m and 47 kg, the pipes and hoses 50 m and 5.8 kg with 64 fittings.

## 7. Open items

- The routed 230 V TPS and cords (76 m) are longer than BD-11's 40 m, the PEX (35 m) longer than its 30 m, and its 47
  fittings more than 40. BD-11's price items are in `data/assemblies/trailer.yaml` and are to be raised with this
  model as their source. The wastes (2.9 m of DWV with 9 bends, 2.5 m of drain hose) are not priced yet.
- The bench's plinth must come forward to cover G10, G11, G14 and G15.
- Moving the SVC checks into `data/checks.yaml` needs a `services` type in `cad/partsdb.py` and one branch in
  `Trailer.checks` that calls `cad/routes_model.check_rows`.

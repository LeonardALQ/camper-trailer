# 29 The ute and bike models: dimensions and sources

Decision H27 asks for the real vehicles in the 3D models, every part held by something. This report records each dimension the LandCruiser, the Aprilia Tuareg 660 Rally and the Triumph Street Triple 765 RS models use and where it comes from. Checked 22 Nov 2026. Estimates are marked (est.).

## How the models keep the checks

Every ute and bike box check reads either a parameter in `data/ute/ute.yaml` and `data/assemblies/ute-garage.yaml` or the bikes' points in `research/05-bike-geometry.yaml` and the owner's sizes in `data/parts/bikes.yaml`. The models are built on those numbers and never move them. Where a bike part sets a clearance, the product model keeps that part's outer face: the Tuareg's shrouds at the measured 585 mm fairing width (TU-01), its skid plate's lowest edge at 244 mm and as wide as the engine (400 mm, est.), the Street Triple's belly pan at 144 mm and as wide as its engine, the bar ends, the panniers and the number plates. So every ute and box check gives the value it gave at 31ed437. The ute's shapes are never read by a check: UTE-09, UTE-10 and UTE-15 read the box's extent and the parameters.

The test `cad/tests/test_ute_supported.py` builds a contact graph of both viewer models. Two solids are joined when they come within 1 mm over a real area, which it measures by pushing them 1 mm further together and asking for 1 mm3 of common volume. Every solid must reach the ute's tyres, or in the loading view the ground under the ramp.

## The LandCruiser 79 single cab V8

The 2017 body builder guide BBGJ1007 is no longer online. Its figures in `data/ute/ute.yaml` (report 16) set the envelope: wheelbase 3,180 mm, bumper 860 mm ahead of the front axle, cab back 2,060 mm behind it, cab 1,790 mm wide with its roof at 1,955 mm on 265 tyres, tracks 1,555 mm, frame rails 1,046 mm over and 60 by 160 mm (est.), rear frame top 774 mm laden with the Lovells lift.

The shapes come from Toyota's LC70 body builder guide for trucks from January 2007, LC70BBG, drawing 1-5 for the VDJ79R cab and chassis ([Toyota fleet PDF](https://myfleet.toyota.com.au/customer/userfiles/LC70BBG.pdf), p. 85), read at 3.20 mm a pixel from the printed 3,180 mm wheelbase. It gives 5,080 mm overall, 710 mm front overhang, 1,190 mm rear overhang, the cab back at 2,060 mm, 2,725 mm from the grille to the cab back, 1,380 mm from the frame reference line to the roof, 1,790 mm over the cab and 1,870 mm over the flares, and a factory snorkel on the road-side A-pillar. On 265/70R16 tyres its roof stands at 1,894 mm, so the model raises every body point 61 mm, for the 805 mm tyres and the lift, to meet the 1,955 mm roof. The 2017 truck is 150 mm longer in front (860 against 710 mm, 5,230 mm overall), so the bonnet, the guards and the grille run 150 mm further forward than in the drawing.

| Part | Model | Source |
|---|---|---|
| Windscreen | foot at X 700 mm, Z 1,326 mm, top at X 1,150 mm, Z 1,880 mm | drawing 1-5, raised 61 mm |
| Doors | X 712 to 1,782 mm, foot at Z 563 mm, belt line Z 1,299 mm | drawing 1-5 |
| Glasshouse | 870 mm half width, 25 mm in from the body (est.) | estimate |
| Cab floor | Z 820 mm on four rubber mounts on the rails (est.) | estimate |
| Bonnet | front edge Z 1,195 mm, cowl Z 1,322 mm | drawing 1-5, raised |
| V8 scoop | X -380 to -40 mm, 700 mm wide, 40 to 58 mm proud (est.) | drawing 1-5 plan, estimate |
| Grille face | X -805 mm, behind the bull bar | 2017 front, estimate |
| Headlights | 300 by 95 mm each, Z 985 to 1,080 mm | drawing 1-5, raised |
| Flares | 470 to 530 mm round the front axle, out to 1,875 mm | drawing 1-5: 1,870 mm |
| Mirrors | heads 110 by 240 mm, 130 mm outside the cab | drawing 1-5 |
| Snorkel | 90 mm pipe 62 mm ahead of the A-pillar, head 144 mm | drawing 1-5, estimate |
| Bull bar | pan, 76 mm hoop, 60 mm wings, inside report 16's X -940 mm envelope | report 16, estimate |
| Frame | C-section rails, 6 mm web and flanges, six crossmembers | ute.yaml, estimate |
| Axles | 100 mm tubes, 280 mm drums, diffs 250 and 280 mm | estimate |
| Front coils | 62 mm coil radius, 16 mm wire, 36 mm pitch | estimate |
| Rear leaves | 1,400 mm eye to eye, under the axle, 70 mm wide | drawing 1-5, estimate |
| Fuel tank | 700 by 880 by 300 mm round the propeller shaft, on two straps | UT-02, estimate |
| Towbar | side arms on the rails, crossbar behind the spare, 50 mm tongue, DO35 at the ball | report 16, ute.yaml |
| Spare | face down at X 3,880 mm, Z 420 mm, on Toyota's carrier | UT-05 |

### Wheels and tyres

The ROH Trak 2 is a white sunraysia steel wheel, mine-site approved, made in 16 x 7 for the 5 x 150 LandCruiser stud pattern and rated up to 1,400 kg ([ROH](https://roh.com.au/wheels/trak-2)). The model gives it a rolled rim with its bead seats, flanges and drop centre, 406.4 mm at the bead seat and 177.8 mm between the flanges, and a pressed centre with eight triangular windows, five stud holes on the 150 mm circle, a 110 mm centre bore (est.), five nuts and a centre cap. ET 0 puts its mounting face 4 mm inboard of the rim's centre plane, on the hub drum.

The LT265/75R16 tyre is 16 x 25.4 + 2 x 0.75 x 265 = 804 mm across, and ute.yaml takes the Yokohama G015's 805 mm and a 268 mm section. The model's carcass has square shoulders and full sidewalls, and five rows of tread blocks 13 mm deep (est.): a centre row, two inner rows half a pitch round from it and two shoulder rows that run onto the sidewall, 44 blocks round (est.). A block sits at the bottom of each tyre.

## The Aprilia Tuareg 660 Rally

The points and sizes are report 05's, from Aprilia's manual and its side image, with the owner's 2,220 by 965 by 1,370 mm (folded mirrors). Aprilia's specification gives a 1,525 mm wheelbase, 26.7 degrees of rake and 113.3 mm of trail, 240 mm of travel at each end, Kayaba 43 mm upside-down forks, two 300 mm floating front discs and a 260 mm rear disc ([Aprilia](https://wlassets.aprilia.com/wlassets/aprilia/rs/tech_spec/2024/Tuareg660/original/Tuareg660.pdf), [Motoplanete](https://www.motoplanete.us/used-motorcycle/728379/TUAREG-660/fiche.html)). The Rally runs 1.85 x 21 and 4.00 x 18 spoked rims with 90/90-21 and 150/70 R18 tyres, which are 695 and 667 mm across.

The model's wheels have 36 tangential spokes each, crossing two (est.), with hubs 150 mm wide (est.). One spoke on each side of the rear wheel crosses the wheel strap's line straight below the axle, so the strap bears on them. The knobbly tyres carry a centre row and two shoulder rows of knobs, 30 round, 8 mm deep in front and 10 mm at the rear (est.). The fork's offset of 55 mm (est.) follows from the rake and trail. The parts between the points are estimates from Aprilia's image: the steel trellis frame and its swingarm pivot plates, the 270-degree twin with its covers, the radiator and the skid plate, the two headers to the high silencer on the right, the cast swingarm, the shock, the chain on the left between the tyre and the arm, the shrouds and the nose with its headlight and screen, the tank, seat, tail and rack, the bars and their risers, the hand guards, the folded mirrors, the pegs on their hangers, the side stand, the crash bars (their tubes 360 mm out, est., with the top at TU-09) and the Mosko Moto panniers on their racks.

## The Triumph Street Triple 765 RS

Report 05 measured Triumph's 2025 RS images against the 1,399 mm wheelbase, and the owner's 2,055 by 792 by 1,064 mm match the RS without mirrors. Triumph's Australian specification page lists 23.2 degrees of rake and 96.9 mm of trail, cast aluminium five-spoke wheels of 17 x 3.5 and 17 x 5.5 in with 120/70 ZR17 and 180/55 ZR17 tyres, twin 310 mm floating front discs, a single 220 mm rear disc, a 3-into-1 header with a low single silencer, an aluminium twin-spar frame and a twin-sided cast swingarm, and 41 mm upside-down forks ([Triumph](https://www.triumphmotorcycles.com.au/motorcycles/roadsters/street-triple-765/specification)). The model's wheels have five split spokes, its road tyres two grooves, and its fork a 29 mm offset (est.). The twin headlights, fly screen, triple, radiator, belly pan, headers and silencer, shock, chain, tank, split seat, tail, bars, risers, reservoir, pegs and side stand are estimates from report 05's images.

## The box's fittings

The fittings that hold the box's parts are visual. Each is priced and weighed with the part it belongs to (`data/ute/parts/fittings.yaml`), so the parts list and the box mass do not change. The barn doors hang on stainless piano hinges in the 10 mm gap at each corner post, and in the loading view the hinge sits between the skin and the leaf folded 5 mm off it. The kerb-side door's hinge and keyed latch are inside, because a hinge or a hasp on the outside would take the body past UTE-09's 1,850 mm. The fan, the front fume sensor and the tracker sit on a duct, a bracket and a plate on the front wall's skin, 40 mm behind the frame's face, and the extinguisher on its vehicle bracket on a rail on the kerb wall. The Condor chock's cheeks stand on its cradle plate. Lovells' mudflaps hang on a 6 mm bracket under the rear outriggers. The ramp's two hooks lie on the floor inside the sill, and in the loading view the Tuareg stands half way up the ramp on the WARN winch's 4.8 mm rope, its soft loop round the lower triple clamp.

## Size of the viewer models

The viewer tessellates the ute at 1 mm of chord error and 0.5 rad between facets, and its files round positions to 0.1 mm and normals to 0.001, so each model stays under the site's 8 MB with the tyres' tread and the wheels' spokes.

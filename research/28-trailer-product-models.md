# 28. The trailer's product models and their supports (H27)

22 Nov 2026. Decision H27 asks for every part of the 3D models to stand on, hang from or be fixed to something that is modelled, and for the fit-out to be modelled as the real products at their makers' dimensions. This report records each product's size and its source, what holds each one, and the supports that had to be added.

The models are visual. Each product is built in `cad/model/products/` and chosen by a `model:` key on its line in `data/assemblies/trailer.yaml`. It sits inside its line's envelope within 1 mm, so the fit checks still see the space it takes, and the line's mass and centre of gravity stay the schedule's (`cad/tests/test_products.py`). A line that has only a mass point gives its model an envelope of its own, and a line whose parts stand in two places, such as the DauerShower's unit and its panel, places the second part in its own envelope. `cad/tests/test_supported.py` builds a contact graph of every solid in the four trailer models and finds any that no chain of contacts joins to the tyres on the ground, or to the floor in the Body page's models.

Sizes are width by depth by height in mm, as the maker gives them. Where a maker gives no figure the size is the envelope the design already used, marked (est.).

## 1. Wet room

| Product | Line | Size | Source | What the model shows |
|---|---|---|---|---|
| Thetford C223-CS cassette toilet | WR-06 | 394 x 580 x 534, seat 492 high | [Thetford AU](https://www.thetford.com/au/products-and-support/c223cs/) | Moulded base, back pedestal with the flush panel and button, swivel bowl, seat, lid and hinge |
| Two spare cassettes in a GRP bin | WR-07 | 300 x 450 x 800 (est.) | Report 21 section 8 | Bin, gasketed lid, seal and latch |
| Caravan basin, SKU 310221 | WR-08 | 385 x 285 x 115 | [Jacksons Leisure](https://www.jacksonsleisure.com/caravan-basin-rectangular-385mm-x-285mm-campervan-basin/) | Basin and waste in a 15 mm GRP vanity shelf on two brackets on the partition |
| Mirror cabinet, basin mixer, towel rail | WR-08 | 450 x 120 x 600, a wall mixer, 600 mm rail | Report 21 section 9 (est.) | Cabinet with its mirror door, the mixer on its wall plate over the basin, the rail on two brackets over the toilet |
| DauerShower 2.0 | WR-09, WR-08, WR-10 | Technical unit in a 100 x 320 x 230 cabinet (est.) | [DauerShower](https://dauershower.com/) | The unit in its dry cabinet on the partition's living face, the control panel and the hand shower on its rail with the bypass mixer in the wet room, the switching unit in its floor well |
| Floor tray | WR-01 | 1,000 x 2,330 x 130 | Report 19 R19-24 | 30 mm floor on its wedge, 100 mm upstands, 30 mm lips at both doors, the shower zone's 20 mm lip |
| Drains and sand grate | WR-08, WR-02 | 60 mm drains, 600 x 100 grate | Report 21 section 9 | The shower drain over the well, the floor waste by the rear door, the linear grate over its basket |
| Partition and inner door | WR-03, WR-04 | 620 x 1,850 door | Report 21 | The 20 mm panel with the door's opening, the frame, the leaf, two hinges and a lever on each face |
| 40 L grey water tote | WR-11 | 300 x 400 x 600 (est.) | Report 21 section 10 | Tank, wheels, front feet, handle, cap and strap |

The toilet, the bin and the tote stand on the tray's floor. The basin's shelf, the mirror cabinet, the mixer, the rail and the shower's parts screw to the partition or the kerb wall. The partition is bonded to the tray, the walls and the ceiling. The cassette's Thetford 2680584 service door sits in its cut-out in the kerb wall behind the toilet, with its frame, door and lock. The design has no shower screen or curtain, because the whole room is the shower and is hosed down (H4), so the model shows none.

## 2. Laundry and the plinth

| Product | Line | Size | Source | What the model shows |
|---|---|---|---|---|
| Camec Compact RV II 3.5 kg, 051879 | LA-02 | 445 x 460 x 730 | [Camec manual](https://cdn.shopify.com/s/files/1/0578/8326/3042/files/051879_Manual.pdf?v=1718605142) | Cabinet on four feet, the control console with its dial and keys, the lid with its drum window |
| Haier HDHPS70LW1 heat-pump dryer | LA-14 | 595 x 590 x 850 | [Haier](https://www.haier.com.au/laundry/dryers/7kg-300-series-heat-pump-dryer-hdhps70lw1-61444.html) | Cabinet on four feet, round door with its ring, tinted window and handle, the control strip with the dial and display, the water tank drawer |
| Machine base | LA-14F | 1,075 x 700 x 40 | Layout study | Two 40 x 40 x 3 angle rails, three cross members, ten rubber isolators and a 4 mm tread plate deck |
| Battery box | EL-02 | 900 x 700 x 320 | Report 20 E-10 | 2 mm shell, ceramic-fibre lining, tray with rubber pads, the gasketed front panel and its bolts, two cable glands |
| Five Victron Lithium NG 51.2 V 100 Ah | EL-01 | 162 x 648 x 235 each, 10 mm apart | [Victron datasheet](https://cdn.shopify.com/s/files/1/0497/4749/3026/files/Datasheet-Lithium-NG-batteries-12_8V-25_6V-51_2V-EN.pdf?v=1739576641) | Each case and lid, its two terminal covers and handle, and two hold-down straps |
| End slot cover | LA-11P | 175 x 700 x 320 | Layout study | The aisle face and the end panel by the partition |
| Lockers over the machines | LA-11L | 880 x 400 x 400 | Layout study | Carcass, shelf, back rail and two lift-up doors with push latches |

The modules stand on the tray's pads. The machine base stands on the battery box and on the slot cover's end panel, and the washer and dryer stand on its isolators.

## 3. Bed and desk

| Product | Line | Size | Source | What the model shows |
|---|---|---|---|---|
| Lippert HappiJac 42 in kit, four rails | LB-04 | 50 x 20 C-channel, rails 1,067 mm apart | [Lippert manual](https://lci-support-doc.s3.amazonaws.com/manuals/happijac/ccd-0002668.pdf) | Each rail's web and flanges, the carriage in it at the platform's height, and a support rail along each wall from the front carriage to the rear one |
| HappiJac drive | LB-04M | Across the ceiling over the rails | Report 21 section 1 | The gearmotor with its brake, the cross shaft, a gearbox at each wall and the drive tubes over the rails' tops |
| Platform | LB-03 | 1,550 x 2,290 x 40 | Report 21 section 1.3 | The honeycomb panel in its aluminium edge channel |
| Pure Sleep Orion Caravan Deluxe, queen | LB-01 | 1,530 x 2,030 x 180 | [Pure Sleep](https://puresleep.com.au/product/orion-caravan-deluxe-mattress/) | The mattress with its quilted top |
| Desk | LA-09 | 1,200 x 600, top 730 high | Report 21 section 2 | 25 mm top, the angle cleat on the front wall, two 40 mm square legs with feet |
| Two Helinox Cafe Chairs | LA-09S | 560 x 505 x 850 each | [Helinox](https://helinox.eu/products/cafe-chair) | The pole frame on four feet, the seat and the back, at the desk by day only |

The platform lies on the two support rails, which bolt to the carriages through tabs out of the rails' open faces. The rails screw through the walls' inner skins into the hardpoints LB-06. The desk's top rests on its cleat and its legs. The chairs stand on the floor in the chair space LA-K2. They travel packed in a drawer, where the schedule keeps their mass, and the night model leaves them out, because the bed comes down over the chair space.

## 4. Kitchen

| Product | Line | Size | Source | What the model shows |
|---|---|---|---|---|
| Tower carcass | LA-11T | 585 x 600 x 2,000 | Report 21 | Two 18 mm sides on the floor, the top, a shelf under the fridge, the oven and the RESPA, the Combi's door with its air grille and the top cupboard's door |
| Truma Combi D 6 E | LA-03 | 525 x 450 x 300 | [Truma](https://www.truma.com/au/products/heating-systems-au/combi-heaters-au/combi-d-6/) | Casing, cover, four warm-air outlets and the connections |
| Dometic NRX 130C | LA-05 | 525 x 568 x 812 | [Dometic](https://www.dometic.com/en-au/product/dometic-nrx-130c-9620001867) | Cabinet, mounting frame, door with its handle, the freezer flap's line and the control panel |
| Camec 053632 convection microwave | LA-13 | 510 x 418 x 318 | Report 21 section 4 | Case, door with its window, the control panel with its display, dial and door release |
| Bench carcass | LA-11B | 1,155 x 600 x 900 | Report 21 | 30 mm worktop with the hob's cut-out and the sink's rebate, the end panel, the divider, the cleat on the tower, two drawers on runners, the sink cabinet's base and door |
| Dometic CFX3 55IM on its slide | LA-06 | 720 x 455 x 480 | [Dometic CFX3 55IM](https://overlandgarage.ca/products/dometic-cfx3-55im-cooler-freezer-with-rapid-freeze-plate) | The slide's runners, tray and lock, the body, lid, handles, bumpers and control panel |
| Dometic CVI1525 induction hob | LA-07A | 525 x 350 glass | [Dometic](https://www.dometic.com/fr-fr/produit/dometic-cvi1525-9600050571) | The glass on the worktop, the body under it, two 180 mm zones and the touch strip |
| Dometic CVS1350G sink | LA-07B | 350 x 350 | [Dometic](https://www.dometic.com/fr-fr/produit/dometic-cvs1350g-9600051161) | Rim in the worktop's rebate, bowl, glass lid and waste |
| Sink mixer | LA-07D | Single lever (est.) | Report 21 section 9 | Base on the worktop, body, lever, spout over the bowl |
| Sphere TCR-001 range hood | VE-07 | 600 x 300 x 120 | Report 19 | Canopy screwed to the road wall, mesh filter, duct to its cowl |

The Combi and the tower's sides stand on the floor and each appliance stands on its shelf. The worktop rests on the end panel, the divider and the cleat on the tower's side, the hob's glass rests on the worktop round its cut-out, and the sink's rim sits in a 5 mm rebate, flush with the worktop. The freezer's slide stands on the floor and the drawers run on runners screwed to the tower's side and the divider. Every handle is a push latch, so nothing stands proud into the aisle.

## 5. Heating, cooling, fresh air and the electrics

| Product | Line | Size | Source | What the model shows |
|---|---|---|---|---|
| Mitsubishi Electric MSZ-AP25VGKD2 indoor unit | AC-01 | 798 x 219 x 299 | [Mitsubishi Electric](https://www.mitsubishielectric.com.au/product/msz-ap25-80vgd-split-system-air-conditioner/) | Installation plate on the partition, the body, the front panel, the outlet vane, the display |
| MUZ-AP25VGD2 outdoor unit | AC-02 | 800 x 285 x 550 | Report 19 section 2 | Feet, casing, the fan grille, the service cover and valves |
| Cradle on wire-rope isolators | AC-03 | 400 x 825 x 650 | Report 19 R19-03 | Back plate on the rear wall, the floor and sides, four isolators under the unit's feet, the perforated guard |
| LUNOS e2 60 short, four fans | VE-01A to D | 160 mm sleeve, 162 x 162 cover (est.) | Report 19 section 3 | Sleeve with the fan and regenerator let into the wall, the inner cover and its filter |
| LUNOS RA 15-60 | VE-03 | 160 mm sleeve | [LUNOS manual](https://cdn.shopify.com/s/files/1/2642/2036/files/Installation_Manual_RA_15-60_final.pdf?v=1634725895) | Sleeve and fan in the rear wall, the round inner cover |
| Sy-Klone RESPA-CF2 and the top-up fan | VE-04, VE-05 | 300 x 450 x 300 and 250 x 350 x 200 envelopes (est.) | Report 19 section 4 | The RESPA's wall bracket, precleaner drum, filter housing and outlet, the fan's box, filter door and outlet |
| Victron MultiPlus-II 48/6k5 | EL-04 | 155 x 320 x 644 with its bracket | [Victron datasheet](https://www.victronenergy.com/upload/documents/Datasheet-MultiPlus-II-inverter-charger-EN.pdf) | Wall bracket on the partition, housing, front cover, cable compartment and glands |
| Board cabinet and the Victron gear | LA-11E, EL-05, EL-06 | Units 130 to 330 wide (est.) | Report 20 | The cabinet on the partition, the 12 mm board panel, the Lynx Smart BMS and Lynx Distributor side by side, two MPPT 150/35, four Orion-Tr, the Cerbo GX, the 230 V board, the GX Touch 50 on the door |

The units hang on the partition or the walls on their own brackets, as their makers' guides show, and the fans' sleeves are let into the walls.

## 6. Outside the body

| Product | Line | Size | Source | What the model shows |
|---|---|---|---|---|
| Cruisemaster XT Freestyle arm | RG-01 | 480 x 190 beside the rail | Report 06 | Pivot hanger and shock bracket welded to the rail's outer face, the arm, the shock, the stub axle, and in the wheel the 12 in drum and the LC5 hub |
| ROH Trak 2 16 x 7 ET 0 and the LT265/75R16 tyre | RG-06, RG-02, SP-02, SP-01 | 432 x 178 wheel, 805 x 272 tyre | Report 16 | Rim, flanges and disc on the centre plane, the tyre on the bead seats with its tread band |
| Spare wheel carrier | CH-P09 | 300 x 300 x 6 of plate | data/chassis/chassis.yaml | A 200 x 200 hub plate at the wheel's mounting face, two cleats back to the posts and five M14 studs on the 5 x 150 circle |
| Drawbar box | DX-01 | 320 x 1,480 x 720 | Report 20 | 1.6 mm shell and lid, hinge, latch, the shelf on two angles |
| Two Honda EU22i | GS-01 | 290 x 509 x 425 each | [Honda spec sheet](https://anythingmarketplace.com.au/wp-content/uploads/2026/09/Honda-EU22i-Spec-Sheet.pdf) | Casing on rubber feet, the carry handle, fuel cap and control panel |
| Jerry cans, 10 L petrol and diesel | GS-04 | 300 x 180 x 450 each (est.) | Report 20 | Two cans with handles and caps, and their strap |
| ARK XO750 jockey wheel, swung up | DB-05 | 760 x 126 x 200 | [ARK](https://www.arkcorp.com.au/product/xo750-jockey-wheel/) | Swivel clamp on the bracket plate, the post, crank, fork and twin wheels |
| ARK XO DDS650 corner steadies | CH-B01 | 120 x 80 x 300 wound up | [ARK](https://www.arkcorp.com.au/product/xo-corner-steadies/) | Top plate under the rail, the leg, the nut and the foot pad |
| Forged 1/2 in weld-on D-rings | CH-B02 | 60 x 40 x 42.5 | The tie-down design, STB-05 | The clip under the outrigger and the ring |
| HDPE tanks | UF-01, UF-01R, UF-06, UF-08 | The tanks' envelopes | Reports 13, 18 and 21 | 6 mm walls (5 mm for the diesel tank), the outlet fitting and two straps |
| Sunman eArc SMF430F | RF-01 | 2,054 x 1,084 x 2 | [pv magazine](https://www.pv-magazine.com/2021/10/29/sunman-unveils-430-w-glass-free-solar-module/) | The cell laminate in its clear border, bonded to the roof |
| Fiamma F80s 400 case | BD-13 | 153 x 113 section | [Fiamma data sheet](https://files.ekmcdn.com/grasshopper/resources/other/f80s-ducato-information.pdf) | The rounded case, its end caps and five brackets on the roof |
| Dometic S4 windows | WN-01 to WN-04 | The cut-outs | Report 19 R19-14 | The outer frame 21 mm proud, the frame in the cut-out, the double pane, the inner frame and the blind cassette |
| Aussie Traveller DC doors | BD-07, BD-15 | 1,750 x 622 in a 1,753 x 625 cut-out | [Aussie Traveller](https://aussietraveller.com.au/products/caravan-dc-door-with-pleated-blind-left-hand-hinge) | Frame, leaf, tinted window and pleated blind, hinges and both handles |
| Lamps | LG-01 | data/services.yaml | CT-011 | Each housing on its mounting face with its lens on the outer face |

The body stands on the floor's bearer strips CH-S01 on every raiser, outrigger and floor crossmember, as it does on the frame, and the 32 nut plates CH-P14 sit inside the raisers and the outrigger tips under its bolts. The schedule keeps CH-P14's mass at one point, as before.

## 7. Supports that were missing

On the model as it stood at 31ed437 the check found 190 of the trailer's 195 solids floating, because the XT arms met the rails only along an edge, and with that gap closed it still found the outdoor unit, the lashing points, the jockey and its plate, the battery modules, the MultiPlus-II, the generators and the jerry cans, the freezer, the side marker lamps, the gear on the drawbar box's shelf, the XT air box, the spare wheel, the diesel tank, the grey water and the grey tote. The desk touched only the front wall, and the body stood 20.5 mm above the raisers. Most were held by a part that was already in the line but was not modelled, and the product now shows it: the XT arm's hanger, the D-ring's clip, the jockey's clamp, the battery box's tray, the MultiPlus-II's bracket, the freezer's slide, the desk's cleat and legs, the drawbar box's shelf, the outdoor unit's isolators, the HappiJac kit's support rails and the bearer strips. Seven envelopes grew or moved for these, each with its centre of gravity pinned where it was, so no mass moved.

Three supports were in no line. Each is now a line of its own, its mass taken out of BD-11's allowance for parts not yet designed, as the lamps' 4 kg was, and its price in BD-11's general hardware:

- DB-08, the jockey bracket's four spacer tubes on M12 bolts, 1.0 kg (est.). The bracket plate CH-P11 stands 24 to 95 mm off the drawbar member, because the member runs at 19 degrees to the trailer's axis and the jockey's post lies along it.
- UF-06B, the diesel tank's cradle, two aluminium angles bolted across the bay to the raisers, with rubber strips and two straps, 1.1 kg (est.).
- LG-02, six 3 mm aluminium caps riveted over the outriggers' open ends, which carry the side marker lamps, 0.3 kg.

## 8. Open points and the assumption used

1. DauerShower publishes no outline drawing of the technical unit or the control panel. Assumption: the unit fits the 100 x 320 x 230 mm cabinet the design gives it and the panel is 130 x 190 mm (est.).
2. Sy-Klone publishes the RESPA-CF2's parts but not its outline here. Assumption: a 270 mm precleaner drum and filter housing in the 300 x 450 x 300 mm envelope, on a bracket to the road wall (est.).
3. The Victron units' depths off the board are taken as 48 to 110 mm (est.) from the products' datasheets' classes. Only the MultiPlus-II's and the Lithium NG's sizes are read from Victron.
4. The XT's airbag stands under the outrigger inside the tyre's envelope, so the model leaves it out and shows the arm, the shock, the hanger and the hub.
5. The jerry cans' sizes are not given in report 20. Assumption: two 10 L cans, 300 x 180 x 450 mm each (est.), which fit GS-04's envelope and its 17 kg.

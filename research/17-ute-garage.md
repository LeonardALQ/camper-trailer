# 17: The enclosed motorbike garage on the LandCruiser 79

Note added 20 Nov 2026, after the box was designed (UTE-GARAGE.md, drawings CT-701 to CT-704). The design follows this report with these changes. The box is 1,850 mm wide outside, not 1,900 mm, by the decision log's limit. With 2.5 mm skins on a 40 mm frame that leaves 1,765 mm inside and a 1,745 mm clear rear opening, and the bikes keep their 760 mm spacing with 59.5 mm from each bike to its wall. The door leaves are 27.5 mm thick, so the inside length is 2,520 mm. The design takes the lower floor: on the Lovells kit's estimated 110 mm of bump travel the tubs stand 86.5 mm above a floor 834 mm up, so the ramp sits at 16.5 degrees with the bikes out. The subframe is aluminium RHS 75 x 50 x 3 runners and SHS 50 x 50 x 3 crossmembers, with a galvanised steel crossmember under each L-track row at Toyota's first and last deck mounts, so the anchors reach steel. That moves the front track row to 240 mm ahead of the Tuareg's front axle, against 150 mm here. The tools ride in two chests on the wheel tubs, not in under-tray boxes, because the outer front straps fill the box's front corners. The box weighs 433.1 kg empty, 469.5 kg with the growth allowance, against 440 kg here. The product data for this report is published as `research/17-ute-garage-products.yaml`.

Research report, 20 Nov 2026, for the enclosed bike garage on a used VDJ79 single cab. The designer of the box works from it. Sources are linked where they are used, and estimates are marked.

## Recommendation

Leonard asked for an enclosed, theft-resistant box on the 79's tray for both bikes and some tools, so the trailer can shrink. This report sets its requirements and recommends:

- **Build, do not buy.** Every stock canopy for a 79 tray is 850 to 960 mm tall and at most 2,350 mm long, and the Tuareg needs 1,435 mm inside. Build a one-piece welded aluminium body: 2.5 mm 5052 walls and doors, 2.0 mm roof, 4 mm floor, SHS 40 x 40 x 3 frame, on an RHS subframe (section 6).
- **Inside 2,500 x 1,810 x 1,460 mm**, outside about 2,590 x 1,900 x 1,520 mm. That keeps inside Toyota's 1,910 mm width rule and the 1,908 mm legal rear overhang (1,510 mm).
- **Doors and ramp.** Rear barn doors over a clear opening of at least 1,676 x 1,460 mm, and a kerb-side lift-up door to reach the second bike's straps. The 3,048 mm Black Widow MF-12038 ramp stows on edge in a slot behind the bikes. The WARN VRX 25-S winch pulls each bike up while the rider walks beside it.
- **Floor.** A lower tray at about 850 mm (16.2 degree ramp) if the GVM kit's bump travel keeps the wheel tubs under 100 mm, otherwise a flat deck at about 1,080 mm (20.7 degrees). Both heights are estimates.
- **Mounting.** The subframe bolts to Toyota's deck mount brackets, firm at the front and compliant at the rear. No drilling or welding of the frame.
- **Restraint.** `DESIGN.md`'s layout, unchanged: Condor chocks, two flush L-track rows, LC 1,000 kg straps and 20 kN anchors. The NHVR's 2025 performance standards are the ones report 03 used.
- **Security.** Shoot bolts and a cam bar on the barn doors, an ABLOY PL362 padlock, inset hinges, a disc lock and anchor chain per bike, a Teltonika FMC130 tracker with door switches and a siren, and a Monimoto 9 in each bike.
- **Mass and cost.** About 440 kg empty and 880 kg with the bikes and tools. About AUD 13,900 of new spend (estimate), against about AUD 20,000 to 25,000 plus fitting for a custom shop body.

What blocks the design:

1. The rear axle reaches about 2,260 kg with 250 kg on the towball before any accessory, against Toyota's 2,300 kg maximum. Report 16's GVM kit must rate the rear axle for it.
2. The real deck height and bump travel decide between the lower tray and the flat deck. Measure them on the vehicle.
3. The ramp needs about 3.5 m behind the ute, so the trailer must be unhitched to load or unload the bikes. The box also overhangs the towball by about 160 mm (estimate), so the trailer's drawbar must clear it in a jack-knife.
4. The stability factor falls from 1.02 with the bikes in the trailer to about 0.80 with them on the ute.

## 1. Requirements

### 1.1 What the box must do

- Carry both bikes as the trailer's garage does: side by side, noses forward, 760 mm apart between centrelines (`DESIGN.md`). Across the bikes that is about 1,650 mm, from the Street Triple's bar end to the Tuareg's outer pannier face (`research/05-bike-geometry.yaml`).
- Carry "some tools". Assumption: 60 kg in about 0.3 m3 (estimate, no owner figure).
- Be fully enclosed and locked, with no gap a hand or a tool can reach through.
- Keep dust and water out. Doors close on compression seals, and a filtered air intake can hold the box at a slight positive pressure (section 2.4).
- Vent petrol vapour. Report 02's garage rules apply unchanged: low vents on both sides because the vapour is heavier than air (GAR-01), and no switches or chargers in the lowest 500 mm (GAR-03). The fume detector and extinguisher of report 03 section 11 move with the bikes.

### 1.2 The inside envelope the bikes set

These figures use `DESIGN.md`'s clearances (CLR-01, CLR-04, CLR-06) so the box matches the trailer garage that has already been checked.

| Direction | Build-up | Minimum |
|---|---|---|
| Length | Tuareg 2,220 + chock nose 50 + door gap 15 | 2,285 mm. With the photo-measured 2,263 mm length (CLR-06b) it is 2,328 mm |
| Width | Bikes 1,650 + 15 to each wall | 1,680 mm |
| Height | Tuareg 1,370 + chock rise 25 + margin 40 | 1,435 mm. With Aprilia's 1,390 mm screen it is 1,455 mm |

The strap anchors also fit inside 1,680 mm. The outermost anchors sit 450 mm road side of the Tuareg's centreline and 400 mm kerb side of the Street Triple's, so they span 450 + 760 + 400 = 1,610 mm.

### 1.3 The load restraint standard

The NHVR's Load Restraint Guide 2025 keeps the same performance standards as the 2018 guide that report 03 used: 0.8 g forward, 0.5 g sideways and rearward, and 0.2 g upward when friction is relied on ([NHVR performance standards](https://www.nhvr.gov.au/road-access/loading/loading-guides/performance-standards)). The guide covers light vehicles, meaning any car, ute or trailer up to 4.5 t GVM ([NHVR Load Restraint Guide](https://www.nhvr.gov.au/road-access/loading/load-restraint-guide)). GVM (gross vehicle mass) is the most the loaded vehicle may weigh.

Report 03 multiplied the horizontal cases by an off-road factor of 2 and used 1.0 g upward. That stays. On the ute the bikes sit over and just behind a leaf-sprung rear axle, about 180 mm higher than in the trailer (a deck at about 1,050 mm against the trailer floor's 872 mm, section 3.1). I found no published acceleration data for either position, so the factor cannot be refined. Because the bikes still stand noses forward, braking pushes each front tyre into its chock, and `DESIGN.md`'s strap table holds unchanged if the anchors keep their positions relative to each bike: the worst strap is the Tuareg's rear pair at 277 kgf, against an LC of 1,000 kg. LC (lashing capacity) is the rated working load of a strap under AS/NZS 4380. Every anchor stays designed for 20 kN.

The box itself must also be restrained to the tray, for its own mass and the tools at the same factored cases. If the bike anchors bolt through the box floor into the tray's crossmembers, the bike loads go straight to the tray and the box skin carries none of them.

### 1.4 Rules for a body on the 79's cab chassis

The 79's figures here come from Toyota's 2017 Body Builder's Manual for the 70 Series, which covers the Australian VDJ79R single cab (models TJMRYQ3 and TJMNYQ3) ([Toyota BBM, PDF](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20(1984-2007)/2017%207x%20series%20Body%20Builder's%20Manual.pdf), pages 2 to 7, 26, 28, 55, 62 and 76). Report 16 covers the 79's limits in full. Later builds may differ in detail.

| Rule | Limit | Source |
|---|---|---|
| Body width, legal | 2,500 mm | NSW and national light vehicle limit ([Whirlpool summary of NSW VSI 05](https://forums.whirlpool.net.au/archive/2739300), [NHVR](https://www.nhvr.gov.au/road-access/mass-and-dimension/dimension-requirements/size-and-projection-of-loads)) |
| Body width, Toyota | No more than 60 mm beyond the cab's outermost point each side, mirrors excluded. The cab is 1,790 mm wide (1,870 mm over the GXL's flares), so 1,910 mm | BBM p. 2, p. 76 |
| Height, legal | 4,300 mm | National light vehicle limit (assumption, not checked against NSW VSI 05) |
| Rear overhang, legal | 60 % of the wheelbase or 3.7 m, whichever is less. On the 3,180 mm wheelbase that is 1,908 mm, measured from the rear axle centre to the rear-most point | [Transport Victoria](https://transport.vic.gov.au/road-and-active-transport/road-rules-and-safety/overhang-limits-on-trucks-cars-and-trailers), [Isuzu](https://www.isuzu.com.au/news/news-articles/dimensions-beginners-guide/) |
| Rear overhang, Toyota | Two thirds of the wheelbase for a van body, 2,120 mm. The legal 1,908 mm governs | BBM p. 2 |
| Centre of gravity, Toyota | The unladen vehicle's centre of gravity after the body is fitted must stay under 1,000 mm. The bare cab chassis is at 700 mm | BBM p. 3 |
| Front axle share, Toyota | When loaded, the front axle must carry at least 20 % of the vehicle's weight | BBM p. 3 |
| Mounting, Toyota | The frame must not be modified. Bodies use the standard deck mounts on the frame | BBM p. 10 |
| Cab clearance, Toyota | The body's front wall stands at least 39 mm off the cab at the roof, 34.5 mm at the rear window and 24 mm at deck level, so the cab can move on its mounts | BBM p. 26 |
| Wheel house, Toyota | 25 mm above the tyre at full bump, 30 mm outside it and 40 mm inside it | BBM p. 28 |
| Exhaust, Toyota | Body parts 50 mm from the exhaust pipe and 150 mm from the muffler, or heat shielded | BBM p. 28 |
| Brakes, Toyota | The load sensing proportioning valve on the rear brakes is readjusted after the body is fitted | BBM p. 29 |
| Lamps | The tray's combination lamps, reflectors and plate lamp must not be hidden. End-outline marker lamps are required only on vehicles over 2.10 m wide and optional from 1.80 to 2.10 m | BBM pp. 52 and 53, ADR 13/00 ([legislation.gov.au](https://www.legislation.gov.au/F2005L03991/2009-07-17/2009-07-17/text/original/pdf), [UNECE GRE paper](https://unece.org/sites/default/files/datastore/fileadmin/DAM/trans/doc/2009/wp29gre/ECE-TRANS-WP29-GRE-61-39e.pdf)) |

The 79's own numbers that set the box (BBM pp. 55, 62 and 76):

- Wheelbase 3,180 mm. The cab's back is 2,060 mm behind the front axle, so 1,120 mm ahead of the rear axle.
- The frame ends 1,075 mm behind the rear axle (1,190 mm to the lamp bracket). Its rails are 1,046 to 1,090 mm wide outside at the rear.
- Brackets sit on the rails at 1,228, 879 and 490 mm ahead of the rear axle and at 123, 490, 755 and 1,025 mm behind it (read off the frame drawing). Some are spring hangers, so the body maker confirms which are deck mounts on the vehicle.
- Rear track 1,420 mm, or 1,460 mm with 265/70R16 tyres. Kerb mass 2,165 to 2,230 kg, with 900 to 935 kg on the rear axle. GVM 3,400 kg. Axle capacities 1,500 kg front and 2,300 kg rear.

VSB 14 Section LH (body and chassis) sits behind a bot check on the Queensland site and could not be read ([TMR, PDF](https://www.tmr.qld.gov.au/-/media/Safety/Vehicle-standards-and-modifications/Vehicle-modifications/Light-vehicle-modifications/NCOP/7sectionlhbody.pdf?la=en)). Assumption: a body fitted to Toyota's deck mounts, inside the limits above and the upgraded GVM, needs no separate VSB 14 certificate, and the GVM certifier of report 16 inspects it with the vehicle.

## 2. Products and practice

### 2.1 Stock canopies for a 79 tray

| Maker and model | Size (L x W x H) | Mass | Price (AUD) | Fits the bikes? |
|---|---|---|---|---|
| Norweld full-length canopy on a Norweld single cab tray | Tray 2,526 x 1,850 mm. Canopies come in fixed sizes only and fit only Norweld trays | Tray from 300 kg | Not published | No. Norweld builds no custom sizes ([Norweld FAQ](https://norweld.com.au/faqs/), [79 trays](https://norweld.com.au/ute-trays/vehicle/toyota-79-series-landcruiser/single-cab/)) |
| Mits Alloy 2350 mm canopy | 2,350 x 1,870 x 850 mm | 197 kg, 475 kg with tray | Quote | No, 850 mm high. Mits gives the 79's headboard as 960 mm ([Mits Alloy](https://mitsalloy.com.au/canopies/)) |
| Rhinoman Xpedition CapRax, single cab | Not published | 123 kg, 2.5 mm TIG-welded aluminium, gullwing side doors | 9,100 | No, cab-height canopy ([The Bush Company](https://thebushcompany.com/products/landcruiser-70-series-single-cab-caprax-canopy-by-rhinoman)) |
| Alu-Cab Adventure and Explorer, 79 single cab (C-S-TL79-BS) | In diagrams only | 60 to 70 kg. Roof 400 kg parked, 200 kg moving | Not checked | No, cab-height canopy ([Alu-Cab](https://www.alu-cab.com/products/alu-cab-single-cab-adventure-canopy/)) |
| Bushtech canopy and tray, 79 | Not published | 240 kg with tray | Not checked | No, cab-height canopy ([Adventech 4x4](https://adventech4x4.com/nl/toyota-land-cruiser-79/1389-bushtech-canopy-tray-voor-toyota-landcruiser-79-159383.html)) |
| Teralume XGO chassis mount body, 1700 mm with rear door | Canopy 1,700 mm long. Tray and canopy are one TIG-welded body of 2.5 mm 5052, bolted to the chassis rails | 330 kg dry | 16,990 plus 1,850 fitting, indicative October 2026 | No, too short and low. It shows what a one-piece body weighs and costs ([Teralume](https://teralumeindustries.com/pages/chassis-mount-body)) |
| Ironman 4x4 Raid | Tub canopy | 65 kg | 4,500 to 4,950 | No, it fits utes with a tub, not a tray ([Ironman 4x4](https://www.ironman4x4.com.au/pages/raid-aluminium-ute-canopy)) |

Every stock canopy for a 79 tray stops near the cab roof, about 850 to 960 mm above the deck, and the longest is 2,350 mm. The Tuareg needs 1,435 mm inside. So buying means a custom body from a custom shop. I found no motorcycle-specific ute body or bike canopy made in Australia. The nearest practice is the enclosed motorcycle trailer of report 03 and the pantech (van) body on a light truck. I did not check MCC or Tradesman.

### 2.2 Door options

| Door | For | Against |
|---|---|---|
| Rear barn doors, two side-hinged leaves | Simple and strong. A full-height cam bar locks top and bottom on each leaf, as on truck vans. Leaves fold flat against the sides, clear of the ramp. No struts | Hinges sit outside unless the leaves are inset. Needs about 0.9 m clear behind the ute to swing |
| Top-hinged door | Gives shade and rain cover while loading. Used in the trailer design | A 1.9 x 1.5 m door weighs about 30 kg (estimate) and needs two large gas struts. Its lower edge rises to about 2.5 m above the ground, so it needs a pull strap. It catches the wind |
| Door that drops to form the ramp | One piece to carry | At 1.5 m long from a deck about 1,050 mm high it sits at 44 degrees (asin 1,050 / 1,500). It can only be the top of a longer ramp, needs a frame for about 300 kg of bike and rider, and seals worst at the sill |

### 2.3 How a body mounts to a 79

- Toyota allows no frame modification. Bodies bolt to the standard deck mount brackets on the rails (section 1.4).
- A 79's frame twists off road. A tall box bolted rigidly to it takes that twist into its walls and door frames, which cracks welds, pops rivets and lets water in ([DVA Mechanics](https://dvamechanics.com/blogs/grenadier/cab-to-body-torsion-why-your-canopy-build-must-account-for-1-72-of-twist), written for the Grenadier, the same mechanism). So the body sits on its own two-runner subframe. The front mounts hold it firmly and the rear mounts let the frame twist under it, on rubber or spring-loaded bolts. The engineer sets the detail.
- One welded body (floor, walls and roof in one, like Teralume's) beats a box bolted onto a bought tray. Teralume quotes about 100 kg less, like for like, because there is one floor and no tray sides. It also leaves one floor to seal.

### 2.4 Dust, water and petrol vapour

- Doors close on EPDM bulb seals, pulled in by cam-bar locks so the seal is under pressure.
- A filtered fan in the front wall, above the cab roof where the air is cleanest, blows air in. Low vents with flap valves in the two rear corners let it out. The box then stays above outside pressure, so dust is not drawn in at the seals, and the outflow at floor level carries the heavier-than-air vapour out. The fan sits high, outside the lowest 500 mm (GAR-03), and must be an ignition-protected type for petrol vapour. Product not chosen.
- Drains with one-way valves sit at the low corners. Every bolt through the floor is sealed.

### 2.5 Building it himself

Materials, with Australian prices from All Aluminium, Melbourne, November 2026 ([sheet](https://store.allaluminium.com.au/collections/marine-sheet-aluminium), [square tube](https://store.allaluminium.com.au/collections/square-tube), [rectangular tube](https://store.allaluminium.com.au/collections/aluminium-rectangular-hollow)):

- Skins and floor in 5052-H32 sheet, the alloy Teralume and Rhinoman use at 2.5 mm. A 2,400 x 1,200 mm sheet costs AUD 189 at 2.0 mm, 237 at 2.5 mm and 379 at 4.0 mm. 5083 is stronger and suits the floor and mounts, as Norweld uses it ([Norweld Perth](https://norweld.com.au/locations/perth/)).
- Frame in 6061-T6 square tube, or the store's stock alloy, which the listing does not name. SHS (square hollow section) 40 x 40 x 3 costs AUD 135 per 6.5 m and weighs 1.20 kg/m (calculated). Welding softens either alloy next to the weld, so the engineer designs to welded strength.

Mass of a one-piece body, 2,400 x 1,900 x 1,520 mm outside, calculated at 2.68 g/cm3 for 5052 and 2.70 g/cm3 for the tube:

| Part | Basis | kg |
|---|---|---|
| Skins, 2.0 mm | Sides, front, rear doors and roof, 17.6 m2 | 94.5 |
| Floor, 4.0 mm | 2,400 x 1,900 mm | 48.9 |
| Frame | 30 m of SHS 40 x 40 x 3 and 22 m of SHS 25 x 25 x 3 | 51.6 |
| Subframe | Two RHS 100 x 50 x 3 runners and nine RHS 75 x 50 x 3 crossmembers | 44.4 |
| Hinges, locks, seals, mudguards, paint, lamps | Estimate | 45 |
| **Total** | | **284** |

That compares with 240 to 475 kg for the stock tray and canopy sets in section 2.1. Section 6.1 grows it to about 330 kg for the recommended 2,590 mm length, 2.5 mm walls and the kerb-side door. Material cost is about AUD 4,360 for the aluminium (8 sheets of 2.0 mm, 2 of 4.0 mm, 12 tube lengths) and about AUD 9,000 with locks, hinges, seals, paint, lamps, the fan and consumables (estimate). A custom shop building the same body would charge about AUD 20,000 to 25,000 plus fitting (estimate, scaled from Teralume's AUD 16,990 for its 1,700 mm body).

## 3. Loading

### 3.1 Deck height

No source gives a measured deck height for a GVM-upgraded 79, so this is built up from Toyota's drawings (estimate):

- The frame reference line sits about 590 mm above the ground at the cab (1,970 mm overall height less 1,380 mm to the roof), and the frame behind the cab rises 134 mm above it, so the rear frame top is about 724 mm up (BBM pp. 55 and 62).
- The 7.50R16 tyre's static loaded radius is 375 mm (BBM p. 24) and its outside diameter about 805 mm, so its top is about 777 mm up. A flat deck must clear it at full bump plus 25 mm, which puts a stock deck at about 1,000 mm. If Mits Alloy's 960 mm headboard tops out level with the cab roof at 1,955 to 1,970 mm (assumption), the deck is at about 1,000 mm, which agrees.
- A GVM kit lifting the rear about 50 mm and 285/75R16 tyres (834 mm diameter, calculated) add about 65 mm.

Design figure: 1,080 mm with the box empty and about 1,050 mm laden. Weigh and measure the real vehicle (open question 1).

### 3.2 Ramp

Ramp length is the deck height divided by the sine of the angle (report 03 section 10).

| Deck | 15 degrees | 17 degrees | 20 degrees | 25 degrees |
|---|---|---|---|---|
| 850 mm | 3,284 mm | 2,907 mm | 2,485 mm | 2,011 mm |
| 1,050 mm | 4,056 mm | 3,591 mm | 3,069 mm | 2,484 mm |
| 1,100 mm | 4,250 mm | 3,762 mm | 3,216 mm | 2,602 mm |

- The Black Widow MF-12038 of report 03 (3,048 x 965 mm, 680 kg, 34 kg, folds to 1,524 x 965 x 152 mm) sits at 20.7 degrees on a 1,080 mm deck. That is at report 03's 20 degree limit for walking a bike, so the winch does the pulling.
- The 12 ft Black Widow BW-14440-HD (3,658 x 1,016 mm, 680 kg) gives 17.2 degrees ([Discount Ramps](https://www.discountramps.com/motorcycle/ramps/full-width/p/BW-14440-HD/)). It folds to about 1,830 mm (estimate), too long to stow across a 1,810 mm box.
- No walk-beside ramp of 4 m or more was found, so 15 degrees is out of reach on a flat deck.
- On the ramp's crest the Street Triple's belly rises about 120 mm into the gap at 20 degrees (wheelbase / 4 x sin 20), against its 144 mm ground clearance. The arched ramp is needed for it.

### 3.3 Lower floors

- A floor dropped between the chassis rails is not practical. The rails are about 0.9 m apart inside, and the axle, differential, prop shaft, fuel tank and spring hangers fill that space. A channel for the bikes' tyres could be at most about 100 mm deep, because the Street Triple's belly sits 144 mm above its tyres.
- A lower tray is practical. The floor sits on crossmembers laid straight on the rails, at about 850 mm (estimate: the rear frame top at about 790 mm with the GVM lift and tyres, plus about 60 mm of crossmember and plate), with wheel tubs round the tyres. The tubs stand about 100 mm above that floor (estimate, from 110 mm of bump travel), from 548 mm out from the centreline to the wall. Only the bikes' middles stand beside the tubs, because their wheels sit 640 to 890 mm ahead of and behind the rear axle. The Street Triple's belly pan clears the tubs by about 44 mm. The gain is 16.2 degrees on the same 3,048 mm ramp, about 230 mm off the overall height and a lower centre of gravity (section 5). The bump travel with the GVM kit's bump stops sets the tub height, so it must be measured first.

### 3.4 Winch and one person loading alone

The WARN VRX 25-S of report 13 (part 101020, 1,134 kg, 15 m of 4.8 mm synthetic rope) pulls the Tuareg up 20.7 degrees with about 75 kgf (calculated, 2 % rolling resistance), well inside its rating. It mounts on the front wall at 650 mm, as in the trailer, so its motor stays out of the lowest 500 mm (GAR-03).

How one rider loads a 206 kg bike:

1. Park level and unhitch the trailer. The ramp needs about 3.5 m of clear ground behind the ute, and the trailer's drawbar sits there.
2. Hook the ramp on the sill and tie its safety straps to the body.
3. Clip the winch rope to a soft loop round the lower triple clamp.
4. Walk beside the bike on the wide ramp, engine off, hand on the front brake, running the winch from a remote on the bars.
5. The front wheel rolls into the chock. Strap the bike as in `DESIGN.md`.

Unloading is the reverse, with the winch paying out so the bike cannot run away backwards. Riding up the ramp suits neither bike at 20 degrees into a 1,460 mm-high opening.

## 4. Security

Aluminium of 2.0 to 2.5 mm stops nobody with a cordless grinder. The box's job is to hide the bikes, make the quick ways in (prying a door, lifting it off its hinges, popping a lock) fail, and buy time for the alarm and the trackers.

| Layer | Recommended | Why |
|---|---|---|
| Doors | Two barn-door leaves. The kerb-side leaf shoots bolts into the roof and floor from inside. The road-side leaf closes over it on a full-height cam bar, as on truck vans | No lock cylinder holds the door on its own. The cam bar holds the leaf at the top and bottom, so a pry bar at the middle gets nothing |
| Padlock | ABLOY PL362 on a shrouded hasp over the cam handle | 15 mm case-hardened boron steel shackle, raised shoulders against bolt cutters, security grade 6 to EN 12320 ([ABLOY Australia](https://www.abloy.com/au/en/products/padlocks/abloy-pl362), [ABLOY grade 6](https://www.abloy.com/gb/en/products/mechanical-locking/padlocks/grade-6/pl362-protec)) |
| Everyday latch | A keyed compression or T-handle lock on each leaf, for short stops | Generic canopy T-handles sell for about AUD 13 to 15 each ([eBay listings](https://www.ebay.com.au/b/Canopy-Lock-Trailer-Parts/36632/bn_71615179)), so they are a latch, not security |
| Hinges | Leaves inset, with a continuous hinge inside the door gap, or outside hinges with peened pins and hinge-side dog bolts | A cut hinge pin then does not free the leaf |
| Inside | A disc lock on each bike's front disc and a chain through each frame to a ground anchor bolted through the floor into a crossmember | NSW Police advise locking bikes to anchor points even inside a garage ([NSW Police](https://www.police.nsw.gov.au/__data/assets/pdf_file/0007/106891/fact_sheet_motorcycle.pdf)). SA Police advise securing a bike to a fixed object ([SA Police](https://www.police.sa.gov.au/__data/assets/pdf_file/0010/1287262/Motorcycle-and-Scooter-Theft-Prevention-2023.pdf)) |
| Alarm and box tracker | Teltonika FMC130, hard-wired, with reed switches on all doors and a 12 V siren on its output | 4G tracker with a backup battery, door-sensor inputs and outputs for an immobiliser or siren ([Teltonika](https://www.teltonika-gps.com/newsroom/rcm-and-anatel-certification-updates), [GpsGate](https://gpsgate.com/devices/teltonika-fmc130)). Australian stockist: [WISP](https://wisp.net.au/teltonika-fmc130.html) |
| Bike trackers | Monimoto 9 hidden in each bike | Own batteries lasting 12 to 24 months, AUD 280 to 300 each and AUD 79 a year after two free months ([Monimoto Australia](https://www.monimoto.com.au/pages/features), [Adventure On](https://adventureonstore.com/products/mm9), [eBay](https://www.ebay.com.au/itm/276432748865)) |
| The ute | An immobiliser to AS 4601 if the 79 lacks one | Queensland Police name it the best deterrent to opportunistic vehicle theft ([QPS](https://www.police.qld.gov.au/safety-and-preventing-crime/property-identification-and-recording/vehicle-and-bike-security)) |

What insurers ask for: Swann gives a security device discount for an electronic immobiliser or tracking device ([Swann](https://www.swanninsurance.com.au/)). I found no Australian insurer that sets a lock grade or box standard for bikes carried on a vehicle. Assumption: each bike's comprehensive policy covers theft while it rides in the locked box, and the trackers earn the discount. The owner declares the box and trackers when insuring.

## 5. Mass and stability

### 5.1 Inputs

- Cab chassis: 2,200 kg with 919 kg on the rear axle, centre of gravity 700 mm up (BBM pp. 3 and 76). Two people: 160 kg, 1,650 mm behind the front axle, 1,000 mm up (estimate). Accessories, fuel upgrades and the GVM kit are report 16's and are left out, so these are the box's own effects.
- Body: 280 kg, centred 130 mm behind the rear axle, its centre of gravity 1,594 mm up on a 1,050 mm deck (calculated from section 2.5's parts: roof at the top, walls at mid-height, floor and subframe at the deck).
- Bikes noses forward with the front tyres 50 mm from the front wall's inside face. The Tuareg's centre of gravity lands 123 mm behind the rear axle and the Street Triple's 5 mm behind it (report 05 positions). Heights are report 03's design figures above the deck, 700 and 600 mm.
- Tools: 60 kg in under-tray boxes ahead of the rear wheels, 750 mm up (estimate).
- Track: 1,508 mm, the mean of 1,555 mm front and 1,460 mm rear on 265/70R16 tyres (BBM p. 76).

The static stability factor (SSF) is half the average track divided by the centre of gravity height ([NHTSA test report](https://downloads.regulations.gov/NHTSA-2001-9663-0419/attachment_1.pdf)). A lower SSF means a higher risk of rolling over in a single-vehicle crash, which is why NHTSA rated rollover on it ([Federal Register, 2001](https://www.govinfo.gov/content/pkg/FR-2001-01-12/html/01-973.htm)).

### 5.2 Results

| Case | Mass kg | Front axle kg | Rear axle kg | Front share | CoG height mm | SSF |
|---|---|---|---|---|---|---|
| Cab chassis and two people | 2,360 | 1,358 | 1,002 | 57.5 % | 720 | 1.05 |
| A: box, both bikes, tools | 3,081 | 1,351 | 1,730 | 43.9 % | 922 | 0.82 |
| A with the bikes out | 2,700 | 1,360 | 1,340 | 50.4 % | 812 | 0.93 |
| A with 250 kg on the towball | 3,331 | 1,245 | 2,086 | 37.4 % | 890 | 0.85 |
| A on the lower tray (deck 850 mm) | 3,081 | 1,351 | 1,730 | 43.9 % | 879 | 0.86 |
| B: bikes in the trailer, 200 kg plain tray, tools | 2,620 | 1,363 | 1,257 | 52.0 % | 741 | 1.02 |
| B with the trailer's 221 kg on the towball | 2,841 | 1,269 | 1,572 | 44.7 % | 722 | 1.04 |

The towball sits 1,350 mm behind the rear axle (estimate). Each kilogram on it adds 1.42 kg to the rear axle and takes 0.42 kg off the front.

### 5.3 What it means

- The bikes and the box sit almost on the rear axle, so they load it by almost their whole weight. Box, bikes and tools add 728 kg to the rear axle and take 7 kg off the front.
- With 250 kg on the towball the rear axle reaches 2,086 kg before any accessory. Toyota's GVW rear share is 1,930 kg and its maximum permissible axle capacity 2,300 kg (BBM p. 76). The GVM upgrade of report 16 must lift the rear axle rating to suit.
- The front axle keeps at least 37 % of the weight, well above Toyota's 20 % floor.
- The bikes in the box lower the SSF from 1.02 to 0.82, a fifth of the margin, because the centre of gravity rises 181 mm. With report 05's lower bike estimates it is 0.83. The lower tray wins back 0.04.
- Toyota's unladen limit holds: the cab chassis with the empty body has its centre of gravity at about 801 mm, under 1,000 mm.
- The box top stands about 2,570 mm above the ground, 2,370 mm on the lower tray, and about 610 mm above the cab roof. That adds about 1.2 m2 of frontal area (estimate), which costs fuel and adds crosswind load.

Against the trailer: in the trailer the bikes stand on a floor 872 mm up, on a 1,662 mm track and air suspension, and the ute stays near its bare stability. On the ute they cost a fifth of the ute's SSF and about 730 kg of rear axle load, and in return the trailer loses the garage and 381 kg of bikes.

## 6. Recommendation in detail

### 6.1 Build it

Build a one-piece welded aluminium body (floor, walls and roof as one structure, on its own subframe), and have an engineer review the design and the GVM certifier inspect it. No stock canopy is tall or long enough, Norweld builds no custom sizes, and a custom shop would charge roughly twice the DIY cost (section 2.5). The owner welds aluminium, so he can build in the bike anchors, hardpoints and access doors and repair the body in the field. The record of hard use lies in the construction method, which copies the makers above: TIG-welded 5052 skins, 2.5 mm on the walls and doors, 2.0 mm on the roof. With that, the 2,590 mm length of section 6.2 and the kerb-side door, the body is about 330 kg (calculated as in section 2.5, hardware estimated).

### 6.2 Size

| | Inside | Outside |
|---|---|---|
| Length | 2,500 mm: chock nose 50, Tuareg up to 2,263, gap 15, ramp slot 170 | about 2,590 mm |
| Width | 1,810 mm | 1,900 mm, inside Toyota's 1,910 mm |
| Height | 1,460 mm to the roof bows and the door header | about 1,520 mm above the deck |

The box starts 40 mm behind the cab, so its rear face sits 1,510 mm behind the rear axle, under the 1,908 mm limit. The bikes' centrelines sit 333 mm road side and 427 mm kerb side of the vehicle's centreline, 760 mm apart, which leaves 82 mm from each bike to its wall.

### 6.3 Doors and ramp

- Rear: two barn-door leaves over a clear opening at least 1,676 mm wide and 1,460 mm high, so each bike rolls straight back with 15 mm each side (CLR-09).
- Kerb side: a lift-up door over the front 1,200 mm of the wall, from 300 to 1,300 mm above the floor. With only 82 mm beside the second bike, this is the one place to reach the Street Triple's kerb-side front straps. The rear pair is reached through the rear doors.
- Ramp: the Black Widow MF-12038 (3,048 mm), stowed folded on edge in the 170 mm slot across the back, so it comes out first. It sits at 20.7 degrees on the flat deck and 16.2 degrees on the lower tray.
- Winch: the WARN VRX 25-S on the front wall at 650 mm, one quick-release plate in front of each chock.

### 6.4 Floor and mounting

- Take the lower tray (floor about 850 mm) if the GVM kit's bump travel keeps the wheel tubs at or under 100 mm above the floor. Otherwise use the flat deck at about 1,080 mm.
- The subframe bolts to Toyota's deck mount brackets with no drilling or welding of the frame, firm at the front pairs and compliant at the rear pairs (section 2.3).

### 6.5 Restraint

As `DESIGN.md`: a Condor SC-2000 chock on each bike's centreline at the front wall, two flush L-track rows across the floor (150 mm ahead of and 1,650 mm behind the Tuareg's front axle) bolted into floor crossmembers at 20 kN per anchor, 35 mm SpanSet straps of LC 1,000 kg at the same offsets, a Canyon Dancer harness on the Street Triple and a rear-wheel strap on each bike. The Tuareg loads first and is strapped from the empty Street Triple bay.

### 6.6 Security

Barn doors with internal shoot bolts and a cam bar, an ABLOY PL362 padlock on a shrouded hasp, inset hinges, a disc lock and anchor chain per bike, a Teltonika FMC130 with door switches and a siren, and a Monimoto 9 in each bike (section 4).

### 6.7 Mass and cost

| Item | kg | AUD |
|---|---|---|
| Body, built | 330 | about 9,500 (estimate) |
| Restraint kit from report 03 (chocks, track, straps, coating, vents, detector, extinguisher) | 52 | moves from the trailer |
| Ramp and winch | 45 | move from the trailer |
| Security set: two ABLOY PL362, FMC130, siren and switches, two Monimoto 9, two disc locks, two chains and anchors (the cam bar, shoot bolts and latches are in the body) | 13 | about 2,400 (estimate) |
| Engineer's review | | about 2,000 (estimate) |
| **Total, empty** | **440** | **about 13,900** |

With the bikes and tools the ute carries about 880 kg more than the bare cab chassis. The rear axle then reaches about 2,260 kg with 250 kg on the towball, before any accessory. The full set puts the centre of gravity at about 940 mm and the SSF at about 0.80 (section 5 method).

## Open questions

1. Deck height and rear bump travel on the bought 79 with its GVM kit and tyres. Assumption: a flat deck at 1,080 mm empty and 1,050 mm laden, and wheel tubs 100 mm above a lower floor at 850 mm (section 3.1).
2. The rear axle rating after the GVM upgrade. Assumption: report 16's figure once set, and Toyota's 2,300 kg maximum until then.
3. The bikes' centre of gravity heights. Assumption: report 03's design figures, 700 mm (Tuareg) and 600 mm (Street Triple) above the deck.
4. The off-road factor for a load over a leaf-sprung rear axle. Assumption: report 03's factor of 2 on the NHVR cases and 1.0 g upward, for the engineer to confirm.
5. What tools ride along. Assumption: 60 kg in about 0.3 m3, in lockable under-tray boxes ahead of the rear wheels.
6. Where the towball sits. Assumption: 1,350 mm behind the rear axle (estimate), so the box overhangs it by about 160 mm.
7. Whether anything on the redesigned trailer's drawbar rises under the box's rear overhang. Assumption: everything within 600 mm of the ball stays below 750 mm, about 40 mm under the lower tray's rear underside (estimate).
8. Whether loading must work with the trailer hitched. Assumption: no, the trailer is unhitched to load and unload.
9. Which side each bike rides. Assumption: the Tuareg on the road side and the Street Triple on the kerb side, as in the trailer.
10. The kerb-side door's lock. Assumption: a cam lock and an ABLOY PL362, like the rear doors.
11. The tracker's power. Assumption: the FMC130 runs from the ute's auxiliary battery with its own backup battery.
12. The vapour fan. Assumption: an ignition-protected marine blower of about 3 m3 per minute (estimate), high in the front wall, running while the ignition is on.
13. Insurance while the bikes ride in the box. Assumption: each bike's comprehensive policy covers theft there, with the box and trackers declared.
14. Certification. Assumption: no separate VSB 14 certificate, and the GVM certifier inspects the body with the vehicle.
15. Which build the owner buys. Toyota's 2017 manual covers the VDJ79R from 2017. Assumption: an older VDJ79 (2007 on) has the same frame, deck mounts and rear track. Not checked.

## Could not verify

- VSB 14 Section LH: the Queensland copy sits behind a bot check.
- A measured deck height for any 79 tray, and the 79's rear bump travel.
- Norweld's canopy sizes and prices. The heights of the CapRax, Alu-Cab and Bushtech canopies, which are given in diagrams only. MCC and Tradesman products were not checked.
- The Black Widow BW-14440-HD's mass and folded length, and an Australian stockist for any Black Widow ramp.
- The WARN VRX 25-S Australian price. WARN's US site lists the VRX range from USD 625.49 ([WARN](https://www.warn.com/collections/vrx-winches)).
- Australian prices for the Teltonika FMC130 and the ABLOY PL362, and products for the disc locks, chains, anchors, siren and fan. These are estimates.
- The alloy of All Aluminium's tube stock.
- A custom shop's price for a tall bike body. The figure is scaled from Teralume.
- Any Australian insurer's conditions for bikes carried on a vehicle.
- NHTSA's star bands for SSF values.
- The 79's tray deck mount positions, read off a drawing, and which of them are spring hangers.

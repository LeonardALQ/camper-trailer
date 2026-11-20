# 08: Coupling and hitch

Note added 20 Nov 2026, for the LandCruiser 79: the tow vehicle is now a Toyota LandCruiser 79 single cab V8 in place of the Porsche Cayenne, and it carries both bikes in an enclosed box on its tray (UTE-GARAGE.md). Reports 14 to 16 and VEHICLE.md cover the vehicle, and TRAILER.md revision H is the smaller trailer without a garage, plated at 3,100 kg ATM. The trailer keeps the DO35 coupling, the chains and the breakaway kit. The ute's towbar is the Hayman Reese 03186RW (3,500 kg, 350 kg) with a REDARC Tow-Pro Elite V3 and the 12-pin plug (VEHICLE.md, towing), and its ball sits at 440 mm laden. The Cayenne's towbar, ball height and wiring below are superseded.

This report covers the connection between the Cayenne and the trailer: the towbar, the coupling, the brake controller and trailer plug, the breakaway system and safety chains, and the drawbar geometry. Ratings and dimensions come from the linked spec sheets, manuals and maker pages. Figures marked "estimate" are worked out in the text. The Cayenne's limits of 3,500 kg braked and 140 kg towball download are treated as believed values here. The tow vehicle report verifies them.

Note added after reports 06 and 07. Report 07 found that Porsche Australia rated its factory towbar for a 280 kg towball load on Australian cars (140 kg in Europe), and the design now aims for about 220 kg. The car has no towbar fitted yet, so the receiver bar below is the plan. The coupling target is lowered to 440 mm, plus or minus 20 mm, so the whole tolerance stays inside VSB1's 460 mm limit. Report 06 puts the main rail underside at about 565 mm above the ground with the chosen running gear and 255/55 R18 tyres, because the suspension fixes the rail underside 215 mm above the hub centre. The gap from the rails up to a floor that clears the tyres is filled by deeper rails or a raised floor frame. The drawbar then has to come down only about 125 mm from the rail underside. One of the first two options in section 5.2, a drawbar under the main rails or the DO35 bolted under the drawbar head, covers that without a cranked drawbar. The DO35's under-mount offset, measured on a real coupling, decides which. Where this report says 140 kg or 450 mm, read these figures.

## Recommendation

Towbar. Fit an Australian-pattern towbar with a 50 x 50 mm square hitch receiver rated at 3,500 kg. The one found for this car is Parkside's bar for the Cayenne from 01/10, listed at 3,500 kg and a 280 kg ball rating ([Parkside](https://parksidetowbars.com.au/TOWBAR-SUIT-PORSCHE-CAYENNE-110218/8510-eaa262df-753c-4437-9348-d3d96b92134c/)). The car's own 140 kg download limit still governs. A receiver is needed because the recommended coupling bolts its tow pin to a tongue in place of the ball. It also lets the owner set the coupling height by choosing the tongue. The factory and European detachable swan-neck bars are rated 3,500 kg and 140 kg but only carry a 50 mm ball.

Coupling. Use the Cruisemaster DO35 V3Plus. It is ADR rated to 3,500 kg with a 350 kg vertical load, turns 360 degrees in roll and at least 70 degrees in the other directions, and bolts to the standard Australian four-bolt pattern ([Cruisemaster](https://cruisemaster.com.au/do35-v3plus-no-handbrake/)). It can also be bolted under the drawbar, which helps bring the coupling down from a high chassis. It has a long record on Australian off-road vans and campers, a national service network and a full spare parts list.

Not the AL-KO AKS. The friction stabiliser coupling does not suit this trailer. AL-KO Australia's catalogue lists it only as the AKS 3004 kit, rated 2,500 kg ATM ([AL-KO catalogue](http://www.alko.com.au/wp-content/uploads/2020/04/Couplings.pdf)). The 3,500 kg AKS 3504 is a European part that AL-KO Australia does not list. It fits a 60 mm round drawbar tube and has only the normal ball articulation. Its friction pads also lose effect when dust or grease gets on the ball. Sway control should come from the trailer's AL-KO ESC, the car's own trailer stability function, and the mass layout. Swapping between an AKS and a DO35 is possible on paper but is not worth doing (section 2.5).

Brake controller. Fit a REDARC Tow-Pro Elite V3 (EBRH-ACCV3) for either brake option. It works with electric and electric-over-hydraulic brakes, is approved by AL-KO for use with ESC, and is on AL-KO's approved list for the iQ7 hydraulic actuator ([REDARC](https://www.redarcelectronics.com/au/tow-pro-elite)). Bosch's TSC compatibility list, for the sway control chosen in report 06, includes the earlier V2 but not yet the V3, so confirm the V3 with REDARC. Take its brake signal from the trailer socket's stop-lamp terminal with a diode, as REDARC advises for CAN-bus cars.

Plug. Fit a 12-pin flat socket to AS 4177.5, wired to the VSB1 pin table, plus a separate 50 A Anderson-type connector for the ESC power and the trailer battery charging feed.

Breakaway and chains. Use a breakaway kit with its own battery for electric drums, or the hydraulic actuator's own breakaway for discs. Brakes must stay on for at least 15 minutes. Fit two safety chains marked 4177-35, attached to the drawbar either side of the centreline close to the coupling, and connect them to the towbar with rated bow shackles of at least 10 mm, grade S.

Heights. Design the drawbar so the coupling point sits at 450 mm (plus or minus 20 mm) with the trailer level and the car at its Normal air suspension level, laden. The 958 has no towing level. Its self-levelling holds Normal height under the towball load, so the laden ball height equals the levelled ride height. With a garage floor at 800 to 1,000 mm, the drawbar has to bring the coupling down 350 to 550 mm from the floor surface.

## 1. Towbars for the 958 Cayenne

### 1.1 Options

Each option is one towbar on the car. Only one is needed.

| Towbar | Ball mount | Rating | Weight | Links | Notes |
|---|---|---|---|---|---|
| Porsche Tequipment trailer hitch, mechanical, 958.044.801.31 | Steel crossmember with a vertically mounted, manually detachable 50 mm ball | 3,500 kg braked, 140 kg drawbar load | Not found | [Porsche parts listing](https://www.getporschesilverspringparts.com/oem-parts/porsche-trailer-hitch-with-manually-detachable-ball-95804480131), [second listing](https://porscheparts.checkeredflag.com/oem-parts/porsche-trailer-hitch-with-manually-detachable-ball-95804480131), [fitting bulletin 32/10](https://rparts-sites.s3.amazonaws.com/e980818d5653644701b7291f76d89dad/design/installation%20instructions/92A%20HITCH%20INSTALL%20INSTR.pdf) | The bulletin lists 140 kg hook load and a coded trailer control unit (7P0 907 383 G). It notes an electrically extending hitch that was not sold in the USA. The listings say a 13 to 7-pin adapter is an option. The 958.044.801.31 number in the bulletin is the USA kit. Ask a Porsche dealer for the Australian number. |
| Westfalia detachable towbar for Cayenne 92A (listing 137238, type A40V) | Detachable ball inserted from below | 3,500 kg, D value 16.4 kN | Not found | [pkwteile listing](https://www.pkwteile.de/westfalia/25729793) | Westfalia makes the factory part. Listing read from a search snippet only (page blocked). |
| Steinhof A-093 "Invisible" towbar (etowbars SKU 69541) | Vertically detachable swan neck, 50 mm ball | 3,500 kg, 140 kg nose load, D value 16.3 kN, approval E20-55R-0871-00 | 23.1 kg | [etowbars Australia](https://etowbars.com/au/Towbars/Porsche/Cayenne/Porsche-Cayenne-towbars-2nd-gen/Porsche-Cayenne-Invisible-Towbar-from-2010), [fitting instructions](https://etowbars.com/au/pdfs/A-093-Cayenne-towbar.pdf) | Fits Q7, Touareg and Cayenne. Needs a small bumper cut. Sold in Australia as ADR 62/02 compliant. No record of Australian hard use found. |
| Parkside towbar, Porsche Cayenne 01/10 to 02/18 (listing code UC423Y) | Class 4, 50 x 50 mm square receiver with removable tongue and bolt-on 50 mm ball | 3,500 kg WLL, 280 kg ball weight | Not found | [Parkside](https://parksidetowbars.com.au/TOWBAR-SUIT-PORSCHE-CAYENNE-110218/8510-eaa262df-753c-4437-9348-d3d96b92134c/) | Australian maker. Tested to Australian Standards in a NATA lab, lifetime warranty, kit includes wiring, ECU where needed and rated D-shackles. Recommended. |

Hayman Reese and TAG did not list a towbar for the 958 in the searches made. A forum owner reports that the Touareg 7P electric swivel hitch bolts onto a 958 ([Rennlist](https://rennlist.com/forums/cayenne-958-2011-2018/1301525-touareg-electric-tow-hitch-on-a-cayenne-958-a.html)). That is a forum report only.

Whatever bar is fitted, the car's 140 kg limit applies, not the towbar's higher figure.

### 1.2 Air suspension levels and the design ride height

The owner's GTS has air suspension with PASM. A 958 owner's manual, quoted in full on a forum in 2013, gives these levels ([Rennlist](https://rennlist.com/forums/cayenne-955-957-2003-2010/746665-air-suspension-and-pasm-on-the-cayenne-diesel-is-it-worth-it.html)). Porsche Japan's 2015 Cayenne manual shows the same figures for terrain level and both low levels ([Porsche Japan manual](https://www.porsche.co.jp/owner_service/manual/pdf/cayenne.pdf), PDF page 216). Its loading level figures differ and could not be read reliably.

| Level | Front (mm) | Rear (mm) | Change at the ball (mm, estimate) | When it is used |
|---|---|---|---|---|
| Special terrain (high level II) | +58 | +55 | +54 | Manual only, below about 30 km/h. Drops to terrain level above 30 km/h. |
| Terrain (high level I) | +28 | +25 | +24 | Manual or with the off-road program, below about 80 km/h (100 km/h in the off-road program). |
| Normal | 0 | 0 | 0 | The default. Ground clearance about 190 mm in the quoted manual. |
| Low | -22 | -25 | -26 | Automatic from about 138 km/h, or set manually. Returns to Normal below 80 km/h after about 10 s, or below 40 km/h, unless set manually. |
| Low II | -32 | -35 | -36 | Automatic above about 210 km/h for 40 s. |
| Loading | -52 | -55 | -56 | Set at a standstill for loading. Returns to Normal above about 5 km/h. |

The change at the ball is an estimate. The ball sits behind the rear axle, so it moves by the rear change plus the pitch effect: rear change + (rear change - front change) x (ball overhang / wheelbase). With a 2,895 mm wheelbase and a ball about 1.1 m behind the axle, that adds about 1 mm to the rear figure.

There is no towing level. The trailer should be designed for Normal level, for these reasons:

- Normal is the level for all legal towing speeds. The automatic Low level starts at 138 km/h, above any Australian towing limit.
- The rear self-levels, so the ball returns to its Normal height with the towball load on it. The laden ball height is the levelled ride height, not a squatted one.
- Low level can be selected by hand. One owner reports that with the trailer plug connected the car did not lower when Sport was pressed ([Rennlist](https://rennlist.com/forums/cayenne-958-2011-2018/970617-ride-height-settings-when-towing.html)). That is anecdotal, so the owner should simply keep Normal level when towing.
- Terrain level (+24 mm at the ball) is the setting for fire trails and crossings below 80 km/h. Special terrain (+54 mm) is for short slow sections. Loading level (-56 mm) helps when hitching. These change the trailer's pitch by under 1 degree over a drawbar and body of about 4.5 m (56 mm over 4,500 mm is 0.7 degrees), which any coupling here can absorb.

The GTS sits lower than other 958s. A road test of the 2012 GTS says it is 20 mm lower on air suspension ([Top Gear](https://www.topgear.com/car-reviews/porsche/cayenne-estate-2010/gts-5dr-tiptronic-s/first-drive)), and Porsche Japan's 2015 manual gives the GTS 178 mm of ground clearance against 190 mm for other models. No published towball height was found for any 958 towbar. So the owner must measure it: at Normal level, with the engine running, unladen and again with about 140 kg on the ball.

### 1.3 Towball height range

VSB1 requires a 50 mm towball that can be adjusted to between 350 and 460 mm from the ground to the ball centre with the vehicle fully loaded. It adds that trailers should be designed to be level within this range ([VSB1 Rev 6, 9.3.2](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)). With a swan-neck bar the height is fixed. With a receiver the tongue sets it. Hayman Reese, for example, sells an adjustable cast towball mount rated 4,500 kg ([Hayman Reese](https://haymanreese.com.au/)). Check that any tongue's hole suits the DO35's 7/8 in UNF tow pin.

### 1.4 Ball position behind the rear axle

Transport Canada's vehicle data gives the 958 a rear overhang of 98 cm from the rear axle to the bumper, with a 290 cm wheelbase ([Canadian Vehicle Specifications via NHTSA](https://vpic.nhtsa.dot.gov/api/vehicles/GetCanadianVehicleSpecifications/?Year=2013&Make=Porsche&Model=Cayenne&units=Metric&format=json), [field legend](https://vpic.nhtsa.dot.gov/decoder/CaVehSpec?year=2013)). The ball sits behind the bumper by the length of the swan neck or tongue. That adds an estimated 80 to 250 mm, so the ball is about 1.06 to 1.23 m behind the rear axle (estimate). The owner should measure it on the car.

This matters for sway in two ways:

- A side force at the ball turns the car about its rear axle. The longer the overhang, the more the trailer steers the car. A receiver and tongue usually put the ball further back than a swan neck does (not measured on this car), so use the shortest tongue that clears the tailgate and the coupling.
- The towball load lifts the front axle. By moments, 140 kg at 1.06 to 1.23 m behind the rear axle takes about 51 to 60 kg off the front axle and puts 191 to 200 kg on the rear (estimate, 140 x overhang / 2.895 m).

### 1.5 Trailer stability in the car

The 958's Porsche Stability Management includes a trailer stability function, according to Porsche's PSM function list as quoted on a repair forum ([JustAnswer](https://www.justanswer.com/car/o92dv-frank-codes-coming-psm-control-unit.html)). The Porsche fitting bulletin includes coding the trailer control unit with the Porsche tester. We could not confirm from a Porsche document how the car decides a trailer is attached. Fit the Porsche trailer control unit with the aftermarket bar, have a dealer code it, and ask the dealer to confirm the trailer stability function is active.

## 2. Couplings rated for 3,500 kg

### 2.1 Comparison

One coupling is needed. Australian stockists are listed where found.

| Coupling | Rating | Vertical load | Articulation | Car side | Trailer mount | Weight | Links | Reliability and service |
|---|---|---|---|---|---|---|---|---|
| AL-KO AKS 3004 stabiliser kit 618304 (Australia) | 2,500 kg ATM in Australia (3,000 kg in Europe) | 250 kg (Australian kit) | +/-25 deg vertical, +/-20 deg horizontal | AL-KO anti-rotation 50 mm ball and towbar adapter, included | 4 bolts, 184 x 54 mm, 13.5 mm holes | 4.2 kg (head) | [AL-KO catalogue](http://www.alko.com.au/wp-content/uploads/2020/04/Couplings.pdf), [manual](https://www.mb-m.de/cd/documents/01_Bedienungsanleitungen/Bed_1367804__AL-KO_AKS3004_AKS3504.pdf) | Original equipment on most European caravans. Pads wear and must stay clean and dry. No current Australian product page. |
| AL-KO AKS 3504, 1 225 761 (Europe) | 3,500 kg | 350 kg | +/-25 deg vertical, +/-20 deg horizontal | Clean, grease-free 50 mm ball that cannot rotate | 60 mm round drawbar tube, M16 8.8 at 195 Nm (cross-drilled version 1 225 763, M14 10.9 at 175 Nm) | 4.9 kg | [manual](https://www.mb-m.de/cd/documents/01_Bedienungsanleitungen/Bed_1367804__AL-KO_AKS3004_AKS3504.pdf), [brochure](https://www.franssen-remorques.fr/media/aks_3004_3504__074551600_1543_28032015.pdf), [AL-KO store](https://store.alko-tech.com/zubehoer-fuer-wohnwagen/stabilisierungskupplungen/stabilisierungskupplung-aks-3504-m16-anschluss-15-1225761) | UN R55 approval E1 55R-01 1796. Not listed by AL-KO Australia, so Australian parts and service are doubtful. |
| Cruisemaster DO35 V3Plus, with or without handbrake | 3,500 kg (ADR) | 350 kg | 360 deg axial, at least 70 deg in the other directions | Tow pin with 7/8 in UNF shaft on a tongue, 440 Nm | 4 bolts, 185 x 54 mm, M12 8.8 at 90 Nm, flat face, top or underside of drawbar | Not published | [product page](https://cruisemaster.com.au/do35-v3plus-no-handbrake/), [user guide](https://cruisemaster.com.au/content/cis/DO35-V3PLUS-User-Guide-Rev.3.pdf), [Parkside stockist](https://parksidetowbars.com.au/COUPLING-DO35-V3PLUS-WBOLTS-NO-HBRAK/8510-e8933273-52e8-41ed-a643-3833bab29219/), [Repco](https://www.repco.com.au/4wd-adventure-escape/towing-equipment/tow-hitches-couplings/cruisemaster-do35-v3plus-coupling-kit-with-handbrake-18dreo35v3plusi/p/A5747058) | The common off-road coupling in Australia. Greaseable bushes, service check every 10,000 km or 12 months, spare bush, lock, cap and yoke kits, five-year warranty. Recommended. |
| ARK XO ORXOF50 (ORXOF50R with ratchet park brake) | 3,500 kg, electric brakes, AS 4177.3-2004 | Not stated | "Full off-road articulation" (no figures) | Standard 50 mm ball to AS 4177.2, not flat-flange types | 4 bolts, 184 x 55 mm, 14 mm holes | Not found | [ARK catalogue 2024-25](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), pages 77 and 78 | Component type approvals CTA-060735 and CTA-060736. Locks over the whole ball. Shorter record than the DO35. Ask ARK whether it fits a European swan-neck ball. |
| AL-KO Off Road Pin coupling 619400 (Click-Lock, tow pin 619410) | 3,500 kg, electric brakes | Not stated | Not stated | AL-KO XPC-1 tow pin | 4 bolts, 184 x 54 mm | Not found | [AL-KO catalogue](http://www.alko.com.au/wp-content/uploads/2020/04/Couplings.pdf) | In the 2020 catalogue. Not on AL-KO's current coupling pages, so availability is unclear. AL-KO's current off-road ball coupling is 2,000 kg for electric brakes ([AL-KO](https://alko.com.au/product/solutions/couplings/off-road-ball-coupling/)). |
| McHitch automatic coupling, 3.5 t | 3.5 t | Not found | Over 90 deg in all directions (maker) | McHitch car-side receiver | Not found | Not found | [McHitch](https://www.mchitch.com.au/pages/about-us) | Hitches automatically. Data incomplete, not assessed further. |

### 2.2 The AKS in detail

The AKS 3004 and 3504 are ball coupling heads with four friction pads. When the stabiliser handle is pressed down, the pads clamp the car's towball from the left, right, front and rear. AL-KO gives the maximum braking torque of the pads as 300 Nm ([AL-KO manual](https://www.mb-m.de/cd/documents/01_Bedienungsanleitungen/Bed_1367804__AL-KO_AKS3004_AKS3504.pdf)). Its brochure says up to 320 Nm ([brochure](https://www.franssen-remorques.fr/media/aks_3004_3504__074551600_1543_28032015.pdf)). Both meet ISO 11555-1.

What it needs from the towball:

- A 50 mm ball to EC 94/20 (DIN 74058). Class A50-1 balls are not allowed. Class S balls are not allowed except Westfalia type 305417. Screw-in balls must be positively locked ([AL-KO manual](https://www.mb-m.de/cd/documents/01_Bedienungsanleitungen/Bed_1367804__AL-KO_AKS3004_AKS3504.pdf)).
- A ball that cannot unwind. AL-KO Australia warns that the usual Australian ball, held through the tongue by a nut and washer, can loosen under the AKS. It supplies an anti-rotation plate and a ball with flats ([AL-KO bulletin ALK200802](https://alko.com.au/wp-content/uploads/2024/06/ALKAU-Product-Bulletin-ALK200802.pdf)). Parts include ball 618904, high-rise ball 618901 and plates 618100, 618200 and 618205 ([AL-KO catalogue](http://www.alko.com.au/wp-content/uploads/2020/04/Couplings.pdf)).
- A clean, unpainted, grease-free ball of at least 49 mm. Greasy pads must be replaced, and cleaned pads have a much lower damping moment ([AL-KO manual](https://www.mb-m.de/cd/documents/01_Bedienungsanleitungen/Bed_1367804__AL-KO_AKS3004_AKS3504.pdf)).
- Room for the handle. AL-KO UK asks for at least 330 mm above the ball plus 85 to 100 mm of handle stroke ([AKS 3004 handbook](https://img1.wsimg.com/blobby/go/e0c94e9e-f140-4db1-880e-68dc0f8c7eef/downloads/aks-3004-handbook.pdf?ver=1776492766344)).

Does it suit the Cayenne's towbar? The same handbook says swan-neck towbars, fixed or detachable, suit the AKS if they meet EC 94/20 and leave 60 mm of clearance around the ball centre. So the factory, Westfalia or Steinhof bar could carry an AKS, subject to the class S exclusion in the newer manual, which AL-KO should confirm for the Porsche ball. A receiver bar needs AL-KO's anti-rotation ball and plate. The Cayenne has no tailgate spare wheel, so the handle has room.

Does it work with sway control? AL-KO ESC is a separate unit on the trailer that brakes the trailer wheels. AL-KO's ESC manual and FAQ set conditions on brake controllers, brakes and the power feed, and none on the coupling ([ESC FAQ](https://alko.com.au/wp-content/uploads/2021/02/ALKO_ESC_FAQ_NEW_VEHICLES_2023.pdf), [ESC manual](https://alko.com.au/wp-content/uploads/2024/06/ALKO_ESC_USER-MANUAL_062024.pdf)). The car's trailer stability works through the car's brakes and engine. So the AKS can be combined with both. So can the DO35.

### 2.3 Sway damping against articulation

This trailer will spend most of its life at 100 to 110 km/h with a download of only about 140 kg, which is 4% of a 3,500 kg ATM. Yaw damping is valuable. So is articulation on fire trails and creek entries, where the car and trailer can sit on different cross-slopes.

How much damping does the AKS add? An estimate, which the engineer may refine:

- Assume a loaded trailer of 3,200 kg, its centre of mass 4.5 m behind the ball, and the yaw inertia of a uniform 5.5 x 2.4 m box. That gives a yaw inertia about the ball of 3,200 x ((5.5^2 + 2.4^2)/12 + 4.5^2) = about 74,000 kg m^2.
- Assume sway at 0.7 Hz (an assumed typical caravan value, not measured).
- At 1 degree of sway, the peak sway energy is about 220 J. The pads, at 300 Nm, absorb 4 x 300 x 0.0175 = 21 J per cycle. That is about a tenth of the energy each cycle.
- At 3 degrees, the sway energy is about 2,000 J and the pads absorb about 63 J. That is about 3% per cycle.

So the AKS helps most at the very start of sway, as AL-KO says, and much less once sway has built up. It cannot replace correct loading, low yaw inertia, the ESC and the car's trailer stability function.

Against that, the AKS has the standard ball range of +/-25 and +/-20 degrees. AL-KO itself says the standard articulation of a coupling may be insufficient in rough off-road conditions, which is why it sells separate off-road couplings ([AL-KO catalogue](http://www.alko.com.au/wp-content/uploads/2020/04/Couplings.pdf)). Dust and mud on the ball also cut its friction. The DO35's 360 degrees of roll and at least 70 degrees in pitch and yaw remove the risk of the coupling binding and levering the car on a cross-slope.

### 2.4 The coupling decision

Choose the DO35 V3Plus:

- It is rated for the full 3,500 kg ATM and 350 kg vertical load, against 2,500 kg for the only AKS in AL-KO Australia's catalogue.
- It has the articulation fire trails and crossings need.
- It has the strongest Australian record and parts supply of the options found, and it can be serviced in the field: grease points, a replaceable O-ring, and a lock that can be flushed with water when dirt gets in ([user guide](https://cruisemaster.com.au/content/cis/DO35-V3PLUS-User-Guide-Rev.3.pdf)).
- It can mount under the drawbar, which helps the height problem in section 5.

VSB1 asks for the component type approval number of an off-road coupling ([VSB1 Rev 6, 9.3.3](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)). Cruisemaster states the DO35 meets ADR 62/02 locking and exceeds its strength requirements, but its approval number was not found. Get it from Cruisemaster before buying.

Choose the handbrake version only if the park brake will be worked from the coupling. That depends on the brake choice in the running gear report.

### 2.5 Can both be fitted and swapped?

On paper, yes. The DO35 (185 x 54 mm), the ARK XO (184 x 55 mm) and AL-KO's Australian couplings, including the AKS 3004 kit (184 x 54 mm), share the Australian four-bolt pattern. With a receiver on the car, a second tongue carries the other car-side part. In practice it does not work well:

- The only AKS on that pattern is rated 2,500 kg. The trailer could not be loaded above 2,500 kg with it fitted.
- The 3,500 kg AKS 3504 needs a 60 mm round tube, so it would need a custom structural adapter.
- Each swap needs four new bolts, torqued and locked ([DO35 guide](https://cruisemaster.com.au/content/cis/DO35-V3PLUS-User-Guide-Rev.3.pdf)). Each car-side part also sits at a different height, so each tongue has to be set to give the same coupling point height or the trailer will tow nose-up or nose-down.
- The drawbar test or calculation, the engineer's review and the registration inspection would all have to cover both couplings.

If a road-only option is wanted later, a 3,500 kg ball coupling on the same pattern, such as the ARK XO, is a cleaner second choice than the AKS.

## 3. Brake controllers and the trailer plug

### 3.1 Controllers

| Product | Use here | Qty | Weight | Ratings | Links | Reliability and service |
|---|---|---|---|---|---|---|
| REDARC Tow-Pro Elite V3, EBRH-ACCV3 | In-car controller for either brake option | 1 | 200 g | 9 to 32 V, up to 3 axles, 18 A nominal, 25 A maximum on 12 V, standby under 5 mA | [REDARC](https://www.redarcelectronics.com/au/tow-pro-elite), [manual](https://files.autoxtreme.com.au/User-Manuals/Safety-Systems/RedArcTowProEliteV3UserManual.pdf) | Australian maker, two-year warranty. On AL-KO's ESC approved list and iQ7 approved list. Spare knobs and bezels sold. Recommended. |
| Tekonsha Prodigy P3, 90195 | Alternative controller | 1 | Not found | Brake type menu for electric or hydraulic | [Tekonsha](https://www.tekonsha.com/product/90195_trailer-brake-control-proportional), [manual](https://www.tekonsha.com/product-assets/install/N90195.pdf) | On AL-KO's ESC and iQ7 lists. With an iQ7 it shows a warning for low pressure or breakaway, which AL-KO says some states require ([iQ7 manual](https://alko.com.au/wp-content/uploads/2026/05/350636-ALKO-AU-iQ7-A5-ACTUATOR-CONTROL-INSTALLATION-OPERATING-INSTRUCTIONS-052026.pdf)). |

AL-KO's list of controllers approved with ESC includes the Tow-Pro Elite EBRH-ACCV2 and V3 and the Tekonsha P3. It marks the Hayman Reese Sentinel as not approved ([AL-KO ESC controller list](https://alko.com.au/wp-content/uploads/2021/02/ALKO-ESC-Approved-Brake-Controllers-03_2023.pdf)).

### 3.2 Electric drum brakes on the 958

- Power feed. REDARC requires the controller's power wire to go straight to the start battery positive through a 25 A fuse or 30 A circuit breaker, mounted as close to the battery as possible, and not through an ignition circuit. Its minimum wire sizes are 3 mm2 for the 12 V supply and the brake output and 1.25 mm2 for the brake-light trigger ([REDARC manual](https://files.autoxtreme.com.au/User-Manuals/Safety-Systems/RedArcTowProEliteV3UserManual.pdf)).
- Battery position. The 958's battery sits under the driver's seat on left-hand-drive cars, with jump points under the bonnet ([eCarGuides](https://ecarguides.com/maintenance-guides/how-to-test-replace-battery-on-porsche-cayenne-v6-958/)). Confirm the position on this right-hand-drive car.
- Battery sensor. Porsche's technical information for the 92A, including the GTS, says the battery sensor sits between the battery negative terminal and the ground cable and feeds the energy management system. Chargers and jump leads must go to the defined connection points ([Porsche TI 60/12](https://static.nhtsa.gov/odi/tsbs/2017/MC-10120787-9999.pdf)). Our inference is that every added negative should return to body earth, not to the battery post, so the sensor sees the current. A Porsche-experienced auto electrician should confirm this.
- Brake signal. The 958 brakes itself for stability control and adaptive cruise. REDARC advises CAN-bus cars to take the signal from the stop-lamp wire at the trailer socket, which catches every event that lights the brake lamps, with a diode on the car side of that point. The diode stops 12 V back-feeding the car when the manual override is used.
- Remote head. REDARC says the V3 remote head fits the thicker, curved dashes of European cars.

### 3.3 Electric-over-hydraulic discs on the 958

The in-car side is the same: the controller's blue output goes to pin 5 of the plug and drives the actuator. The differences are on the actuator side, which the running gear report chooses.

- Dexter DX series (EH1600, 357160 without box or 357165 with box and breakaway, for discs). Dexter asks for a controller with at least 5 A output and recommends an inertia-type controller. It needs a dedicated 30 to 40 A, 12 V supply, with 12 gauge wire as the minimum and 10 gauge recommended, plus a breakaway battery of at least 9 Ah ([DX manual](https://alko.com.au/wp-content/uploads/2020/07/DXSeriesEHActuatorManual.pdf), [DX and DB35 brochure](https://alko.com.au/wp-content/uploads/2024/06/Db-DX-2024.pdf)). The actuator can also run from a large battery on the trailer. The DX with DB35 calipers is approved for use with AL-KO ESC.
- AL-KO iQ7. It must be used with an approved inertia controller: Hayes Energiser III, Tekonsha Primus IQ, Prodigy P2, P3, or REDARC Tow-Pro Elite. It applies the brakes itself when power is lost, so it needs no separate breakaway battery. It is not waterproof and must never be submerged, so for river crossings it must be mounted high ([iQ7 manual](https://alko.com.au/wp-content/uploads/2026/05/350636-ALKO-AU-iQ7-A5-ACTUATOR-CONTROL-INSTALLATION-OPERATING-INSTRUCTIONS-052026.pdf)).
- ESC with hydraulic brakes. AL-KO approves ESC with hydraulic brakes only with its 299 mm disc and AL-KO hydraulic caliper, driven by the iQ7 or the Dexter EH1600 ([ESC FAQ](https://alko.com.au/wp-content/uploads/2021/02/ALKO_ESC_FAQ_NEW_VEHICLES_2023.pdf)). The running gear report should check that its disc choice falls inside this approval.

### 3.4 Trailer plug wiring

VSB1 requires trailers up to 3,500 kg ATM to use a 7 or 12-pin plug to AS 4177.5-2004, wired as below ([VSB1 Rev 6, 7.2](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)). It recommends keeping pin 5 of a 7-pin plug for the service brakes and using a 12-pin plug when auxiliary circuits are needed.

| Pin (7 and 12-pin) | Circuit | Colour |
|---|---|---|
| 1 | Left-hand indicator | Yellow |
| 2 | Reversing signal | Black |
| 3 | Earth return | White |
| 4 | Right-hand indicator | Green |
| 5 | Service brakes | Blue |
| 6 | Stop lamps | Red |
| 7 | Tail, clearance and side-marker lamps | Brown |
| 8 (12-pin only) | Battery supply | Orange |
| 9 (12-pin only) | Auxiliaries | Pink |
| 10 (12-pin only) | Earth return | White |
| 11 (12-pin only) | Rear fog lamp | Grey |
| 12 (12-pin only) | Auxiliaries | Violet |

Use the 12-pin flat. European kits for the 92A come with a 7-pin or 13-pin European socket ([Westfalia listing](https://www.pkwteile.de/westfalia/25729793)), and a Porsche dealer listing offers a 13 to 7-pin adapter. Fit an AS 4177.5 socket wired to the trailer control unit's outputs and the brake controller rather than relying on an adapter for the brakes. VSB1 also requires an earth return wire between the car and trailer, wiring supported at least every 600 mm, and grommets through metal (section 7.1).

| Product | Use here | Qty | Weight | Ratings | Links | Notes |
|---|---|---|---|---|---|---|
| ARK FSP12A dual power trailer socket | Car side: 12-pin flat socket and 50 A Anderson-style connector in one housing | 1 | Not found | Small pins 15 A, large pins 30 A, Anderson-style pins 50 A, all at 12 V | [ARK catalogue](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), page 20 | Australian brand. Built-in light and reed switch. |
| ARK FPP12 12-pin flat plug | Trailer side, signals and brake output | 1 | Not found | Small pins 15 A, large pins 30 A | [ARK catalogue](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), page 20 | Common part, carry a spare. |
| 50 A Anderson-style plug | Trailer side, ESC power and charging feed | 1 | Not found | 50 A | Product to choose | Must mate with the socket's connector. |

### 3.5 Heavy-current feed

Fit a separate two-pole connector for the heavy current, beside the 12-pin socket. ARK rates its Anderson-style pins at 50 A at 12 V ([ARK catalogue](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), page 19). AL-KO wants the ESC fed straight from the car battery through a 30 A fuse or breaker. For off-road use it recommends a separate two-pin plug, AL-KO part 350350, so the ESC can be unplugged for severe sections ([ESC FAQ](https://alko.com.au/wp-content/uploads/2021/02/ALKO_ESC_FAQ_NEW_VEHICLES_2023.pdf)).

The electrical design will size the trailer battery charging feed later. Two facts from this research bear on it. The 958's AGM battery is part of an energy management system with recuperation ([Porsche TI 60/12](https://static.nhtsa.gov/odi/tsbs/2017/MC-10120787-9999.pdf)), so the charging voltage will vary, which points to a DC-DC charger in the trailer. The cable run is long, about 6 to 8 m one way (estimate: about 3.5 to 4 m from under the front seat to the towbar, from the 2,895 mm wheelbase and 980 mm rear overhang plus routing, and 2 to 4 m along the drawbar to a battery near the front of the trailer).

## 4. Breakaway system and safety chains

### 4.1 Breakaway brakes

VSB1 requires trailers over 2,000 kg GTM to have breakaway brakes that apply at once if the trailer comes off and stay applied for at least 15 minutes ([VSB1 Rev 6, 8.2](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)). AL-KO notes that some states make an in-car breakaway battery monitor compulsory ([AL-KO breakaway](https://alko.com.au/product/solutions/brake-controllers-actuation/break-away/)).

| Product | Use here | Qty | Weight | Rating | Links | Reliability and service |
|---|---|---|---|---|---|---|
| AL-KO 333070 electric breakaway kit and battery (Breaksafe BS6000) | Electric drums, two braked axles | 1 | Not found | 4 wheel brakes, 2 braked axles, no monitor | [AL-KO breakaway sheet](https://alko.com.au/wp-content/uploads/2020/04/Break-Away.pdf) | Switch 333071, pin and coil cable 333072 sold as spares. |
| AL-KO 333075 Breaksafe monitor | In-car low-voltage warning for the breakaway battery | 1 | Not found | Mandatory in some states | [AL-KO breakaway sheet](https://alko.com.au/wp-content/uploads/2020/04/Break-Away.pdf) | |
| ARK EBK24 breakaway system | Alternative kit for electric drums | 1 | Not found | 2 and 4 wheel brakes, battery tester and charger, CTA-060807 | [ARK catalogue](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), page 11 | |
| Dexter DX EH1600 with box and breakaway, 357165 | EOH discs | 1 | Not found | Needs a 12 V battery of at least 9 Ah | [DX brochure](https://alko.com.au/wp-content/uploads/2024/06/Db-DX-2024.pdf) | |
| AL-KO iQ7 | EOH discs | 1 | Not found | Brakes apply when power is lost, no separate battery | [iQ7 manual](https://alko.com.au/wp-content/uploads/2026/05/350636-ALKO-AU-iQ7-A5-ACTUATOR-CONTROL-INSTALLATION-OPERATING-INSTRUCTIONS-052026.pdf) | Not waterproof. |

The breakaway cable needs its own attachment point on the towbar, separate from the safety chain shackles, and enough slack for full articulation and tight turns.

### 4.2 Safety chains

VSB1 requires two safety chains for trailers over 2,500 kg up to 3,500 kg ATM. They must comply with AS 4177.4-2004, or be safety cables with the same certified load rating. A 3,500 kg chain is marked 4177-35, repeated at least every fourth link. Grade T chain should not be welded ([VSB1 Rev 6, 9.2.1](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)).

| Product | Use here | Qty | Weight | Rating | Links | Notes |
|---|---|---|---|---|---|---|
| ARK CHR13Z trailer safety chain, 13 mm, zinc | Two chains, drawbar to towbar | About 2 x 1.0 m (length set by the drawbar) | About 3.6 kg/m (estimate from a 7 m pack packed in 25 kg bags), so about 7 kg for both | 3,500 kg, AS 4177.4 | [ARK catalogue](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), page 82 | Heavy. Look for a lighter chain with the 4177-35 marking. |
| ARK HLS13 hammerlock shackle, 13 mm | Chain to drawbar without welding | 2 | Not found | 5,300 kg | [ARK catalogue](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf), page 82 | Suits a rated chain attachment point on the drawbar. |
| Bow shackle to AS 2741, grade S (6), 10 mm body or larger | Chain to towbar | 2 | Not found | WLL at least 875 kg | [Circular 0-1-3](https://cdn.shopify.com/s/files/1/0288/5038/9027/files/0-1-3-1.pdf?v=1643853626) | Product to choose, stamped with maker, grade and WLL. |

The national guidance on shackles is Circular 0-1-3 from the Administrator of Vehicle Standards. For trailers of 2,501 to 3,500 kg ATM it recommends AS 2741 shackles with a WLL of at least 875 kg: a grade M (4) D-shackle of at least 16 mm, a grade S (6) D-shackle of at least 10 mm, or a grade S (6) bow shackle of at least 10 mm. The shackle should exceed the chain's required rating and suit the chain in size ([Circular 0-1-3](https://cdn.shopify.com/s/files/1/0288/5038/9027/files/0-1-3-1.pdf?v=1643853626)). The caravan industry recommends 10 mm grade S shackles of 1,000 kg WLL and notes that the bow shape allows more angle ([Caravan Industry Association note](https://roustaboutsrvclub.com.au/wp-content/uploads/2018/05/D-shackle-confusion-resolved.pdf)). Use bow shackles, because they take side load and the DO35 lets the trailer swing through large angles.

### 4.3 VSB1 attachment requirements

Each chain attachment point on the drawbar must be on a substantial structural member, as near as practical to the coupling, with one chain each side of the drawbar centreline. Each must hold, for at least 10 seconds and without harmful deformation or cracks, a longitudinal pull of 9.81 x ATM and a vertical pull of 0.5 x 9.81 x ATM ([VSB1 Rev 6, 9.2.2](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)). At 3,500 kg ATM that is 34.3 kN and 17.2 kN on each point. VSB1 gives a test method in chapter 14, with the loads applied at the coupling centreline. The registration file needs evidence that the points meet these forces.

## 5. Drawbar geometry

### 5.1 What VSB1 requires of the drawbar

- It must be securely attached to a substantial structural member of the trailer ([VSB1 Rev 6, 9.1](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf)).
- It must hold these forces for 10 seconds without harmful deformation or cracks: longitudinal tension and compression of 1.5 x 9.81 x ATM (51.5 kN at 3,500 kg), transverse thrust of 0.5 x 9.81 x ATM (17.2 kN), and for a rigid drawbar vertical tension and compression of 0.5 x 9.81 x ATM (17.2 kN).
- Strength may instead be shown by department-approved calculations covering strength and fatigue, or by the ADR 62/02 dynamic test. Report 02 covers which path to agree with the engineer.
- The safety chain points must meet section 4.3.
- For this kind of trailer (VSB1 calls it a pig trailer) the drawbar may be up to 8,500 mm long. The front load space must not be shorter than the rear overhang (VSB1 5.1.1).
- Every part supported by the suspension needs at least 100 mm of running clearance, unladen (VSB1 5.4).
- A drawbar that carries loads such as gas bottles or boxes must be tested in that configuration (VSB1 5.1.1).

### 5.2 How Australian off-road trailers bring the coupling down

A garage floor at 800 to 1,000 mm puts the chassis rails far above a 450 mm coupling. There are four ways to close the gap, and they can be combined:

1. Drawbar under the main rails. The A-frame members run back under the chassis rails rather than butting into them. The coupling end then starts one rail depth lower. This also suits report 02's rule that the drawbar runs back to a crossmember or past the front suspension mount (FAIL-01).
2. Coupling under the drawbar head. The DO35 V3Plus can be bolted to the underside of the drawbar where the design allows ([DO35 guide](https://cruisemaster.com.au/content/cis/DO35-V3PLUS-User-Guide-Rev.3.pdf)). That drops the coupling point by an amount set by the coupling's own geometry, which Cruisemaster does not publish. Measure it on a real coupling.
3. Cranked (dropped) drawbar. The A-frame steps down in a dog-leg ahead of the body. It closes any gap but puts a bend and gussets in the most fatigue-loaded member, so it needs the care in report 02 (tapered gussets, SP welds with crack testing, no transverse welds in tension flanges).
4. Raised body on a lower chassis. The main rails stay low, near drawbar height, and a subframe or risers lift the floor above the tyres at full bump. The drawbar is then straight, but the risers add mass and the body joints get taller.

### 5.3 The height the drawbar must bridge

The working target is a coupling point (ball centre or DO35 pin engagement point) at 450 mm, plus or minus 20 mm, with the trailer level and the car at Normal level, laden. That sits inside VSB1's 350 to 460 mm towball range, so a 50 mm ball coupling stays legal, and it is near the top of that range, which shortens the drop from the high chassis. The final value is set once the owner has measured the car (section 1.2) and chosen the tongue.

| Item | Floor at 800 mm | Floor at 1,000 mm | Basis |
|---|---|---|---|
| Garage floor surface | 800 | 1,000 | DESIGN.md range |
| Floor panel and fixings | 40 | 40 | Assumed, to be set in the chassis design |
| Main rail depth | 150 | 150 | Assumed, to be sized by the engineer |
| Main rail underside | 610 | 810 | Floor minus 190 mm |
| Coupling point | 450 | 450 | Target |
| Drop from floor surface to coupling point | 350 | 550 | Floor minus 450 mm |
| Drop from rail underside to coupling point | 160 | 360 | Rail underside minus 450 mm |
| Remaining drop after a 150 mm drawbar under the rails, before the DO35 under-mount offset | 10 | 210 | Assumes a 150 mm deep drawbar member |

So at an 800 mm floor, a straight drawbar under the rails with the DO35 bolted under the head reaches the target. The under-mount offset may even put the coupling a little low, which a spacer plate or the tongue choice corrects. At 1,000 mm about 210 mm, less the under-mount offset, is left over. That needs a cranked drawbar or a lower chassis with risers. This favours keeping the floor low, which the ramp angle in report 03 also favours.

## Data for the chassis design

| Item | Value | Source or basis |
|---|---|---|
| Coupling point height, trailer level | 450 mm, plus or minus 20 mm | Target, section 5.3. Confirm by measurement. |
| Car ride height to design for | Normal level, laden and levelled | Section 1.2 |
| Coupling point change with car level | +54 (special terrain), +24 (terrain), -26 (low), -36 (low II), -56 mm (loading) | Estimate from Porsche level figures |
| VSB1 towball range | 350 to 460 mm, vehicle fully loaded | VSB1 9.3.2 |
| Ball or pin behind the car's rear axle | About 1.06 to 1.23 m | Estimate, section 1.4. Measure. |
| Towball download limit | 140 kg (car), 350 kg (DO35) | Car figure believed, tow vehicle report to verify |
| Coupling mounting | 4 x M12 8.8 at 90 Nm on a flat plate, 185 x 54 mm pattern, top or underside | DO35 guide |
| Coupling articulation | 360 deg roll, at least 70 deg in pitch and yaw | Cruisemaster |
| Drawbar test loads at 3,500 kg ATM | 51.5 kN longitudinal, 17.2 kN transverse, 17.2 kN vertical | VSB1 9.1 |
| Each chain attachment point at 3,500 kg ATM | 34.3 kN longitudinal, 17.2 kN vertical | VSB1 9.2.2 |
| Chain points | One each side of the centreline, as near the coupling as practical | VSB1 9.2.2 |
| Drop to bridge | 350 to 550 mm from floor surface, 160 to 360 mm below rail underside | Section 5.3 |
| Running clearance | At least 100 mm, unladen | VSB1 5.4 |
| Drawbar-mounted items | 12-pin socket and two-pin connector bracket, breakaway switch and battery (electric drums or DX actuator), EOH actuator if fitted, mounted high | Sections 3 and 4 |

## Open questions

1. Measure the car at Normal level: receiver or ball height unladen and with about 140 kg on the ball, the height at each air suspension level, and the distance from the rear axle centre to the ball or pin. Check whether this GTS offers the special terrain level.
2. Does the car already have a factory hitch or trailer control unit? The VIN option list will show it. Will a dealer code the Porsche control unit with an aftermarket bar and confirm the trailer stability function works?
3. What is the DO35 V3Plus component type approval number, and its weight?
4. How far below its mounting face is the DO35's coupling point when bolted on top and when bolted underneath?
5. Electric drums or EOH discs? This sets the actuator, the breakaway kit, the ESC variant and whether the DO35 needs its handbrake.
6. Does the chosen disc and caliper fall inside AL-KO's ESC approval for hydraulic brakes?
7. Is there a lighter AS 4177.4 chain marked 4177-35 than the 13 mm ARK chain?
8. Where is the battery on this right-hand-drive car, and where should the added earths return?
9. What garage floor height will the tyre and suspension choice allow? Every 100 mm lower removes 100 mm of drawbar drop.

## Could not verify

- These links refused automated checks (HTTP 403) and were read from search snippets only: both Porsche parts listings for 958.044.801.31, the Westfalia listing, the JustAnswer PSM quote and the Repco DO35 listing. All other links in this report returned a page when checked.
- VSB1 Revision 6 was read from a mirror copy, as in report 02.
- The 3,500 kg and 140 kg figures for 958.044.801.31 come from search snippets of two dealer listings and the Porsche bulletin's 140 kg hook load.
- The Australian Porsche part number for the 958 towbar, and whether the electrically extending hitch was sold in Australia.
- A Parkside part number. UC423Y is the listing code on its website.
- The Hayman Reese adjustable towball mount rating comes from a search snippet of the Hayman Reese home page.
- The air suspension levels come from a 2013 forum quote of the owner's manual and from Porsche Japan's 2015 manual, whose text extracts as numbers only. No English Porsche manual could be opened. Whether the GTS has the special terrain level is unclear from the Japanese manual.
- Any published towball height for a 958 towbar. The GTS-specific Normal ground clearance for a 2013 car.
- Whether a connected trailer stops the car lowering. One forum report only.
- How the trailer stability function in PSM detects a trailer. The function list comes from a repair forum quote.
- Whether AL-KO's newer exclusion of class S towballs covers the Porsche ball.
- Whether a UN R55 approved AKS 3504 would be accepted on a 3,500 kg trailer in Australia, given VSB1 9.3.2 calls for AS 4177.3.
- Current availability of AL-KO's AKS 3004 kit and 619400 pin coupling in Australia (2020 catalogue only).
- DO35, ARK XO, McHitch, breakaway kit and towbar weights (not published or not found).
- The Austlift trailer chain set spec sheet (the file could not be opened).
- The right-hand-drive battery position (left-hand-drive guide only).
- The sway energy figures in section 2.3 are our estimate on assumed values.

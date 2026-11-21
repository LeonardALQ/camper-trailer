# 26: What the Lovells Elite kit needs from the wheels, track and brakes

Status: research record, 21 Nov 2026. It checked what the Lovells Elite kit needs from the wheels, the rear track and the brakes, and fed decisions H18 and H19.

Note added 21 Nov 2026: the links to Toyota's body builder's guide BBGJ1007 (September 2017) pointed at a copy that is no longer online. They now point to Toyota's own LC70 guide for trucks from January 2007, which has the same width, front axle share and centre of gravity rules. Its cab chassis centre of gravity is 740 mm, where BBGJ1007 gives 700 mm for the VDJ79R-TJMNYQ3, and the masses and page numbers quoted here are BBGJ1007's.

Products and prices: `research/26-elite-wheels.yaml`. All sources were read on 21 Nov 2026.

## Recommendations

1. Wheel. No 16-inch wheel that fits both vehicles has a published rating of 1,425 kg or more. Keep the ROH Trak 2 16 x 7 ET 0 steel wheel (1,400 kg) on the ute, the trailer and both spares. Have the LC5 certifier plate the ute's rear axle at 2,800 kg (2 x 1,400 kg) and the GVM at 4,450 kg (1,650 + 2,800 kg). Lovells already offers a derate as a remedy for under-rated tyres on its 4,200 kg kit, so this is a plausible path, not a published one (assumption). Get Lovells' written yes before buying the kit. The model's rear axle with growth is 2,586 kg, which leaves 214 kg in hand. The fallback, if the derate is refused or the Elite's front caliper fouls the steel wheel's centre, is Toyota's own 16 x 7 ET 0 alloy on all wheels. Lovells rates its kits on the factory wheels, and that alloy fits the trailer's LC5 hubs too.
2. Tyre. Keep LT265/75R16 123/120, 1,550 kg, speed R or S. The Elite needs load index 121 (1,450 kg) and speed M (130 km/h) (est., section 1).
3. Track. The Elite's rear track is 1,555 mm (est.), 95 mm wider than the factory 1,460 mm. Each rear tyre moves 47.5 mm outward. The width over the rear tyres becomes 1,823 mm. In the bike box the tyre then sits 11 mm from the side wall skin, against Toyota's 30 mm (check UGW-03). The box must change. The best fix is a flare over each rear tub that takes the box to 1,890 mm over the tubs (est.). Toyota's width rule allows that if it is read per side. This needs a decision on UTE-09, since taken as H19 (section 3).
4. Brakes. The Elite brings its own front and rear brakes, a booster and a handbrake kit. Drop BR01 to BR04 (AUD 1,500.02). Keep BR05, the DOT 4 flush, as part of the fitter's bleed. Add one spare set of Elite front and rear pads to carry (AUD 350, est.).
5. Cost effect on the car build: AUD 1,150.02 less (est.). The derate costs nothing inside GV03. The fallback alloy wheels would cost about AUD 3,200 more over 10 wheels (est.).

Numbers for the model:

| File and input | Now | Use | Basis |
|---|---|---|---|
| `data/ute/ute.yaml` `track_rear` | 1,460 mm | 1,555 mm | Lovells: rear in line with the front (est. figure) |
| `data/ute/ute.yaml` `rear_axle_kg` | 2,850 kg | 2,800 kg | Derate to 2 x the wheel's 1,400 kg |
| `data/ute/ute.yaml` `gvm_kg` | 4,495 kg | 4,450 kg | Sum of axle ratings, 1,650 + 2,800 kg |
| `data/ute/ute.yaml` `wheel_rating_kg` | 1,400 kg | 1,400 kg | ROH table |
| `data/assemblies/ute-garage.yaml` `wheel_y` | 730 mm | 777.5 mm | Half the new rear track |
| Box width over the rear tubs | 1,850 mm | 1,888 mm minimum, 1,890 mm (est.) | Tyre outer face 911.5 mm plus 30 mm plus 2.5 mm skin, each side |
| Trailer (`data/assemblies/trailer.yaml`) | ET 0, C/F 190, track 1,555 mm | No change | Same wheel |

What blocks the design: the box width decision (UTE-09, since taken as H19) in section 3. Nothing else blocks.

## 1. Lovells' published requirements for the Elite

Kit TOYKIT084-GVM-ELITE suits the VDJ79 single cab built 01/2017 to 08/2022. Lovells rates it at GVM 4,495 kg, GCM 7,400 kg, front axle 1,650 kg, rear axle 2,850 kg and braked towing 3,500 kg, or 4,000 kg with its separate BTC kit ([Lovells 79 vehicle page](https://lovells.com.au/vehicle/toyota-landcruiser-79-series-03-2007-08-2022/), [Elite brochure](https://lovells.com.au/wp-content/uploads/2025/04/Lovells_4495kg_79_Series_GVM_Upgrade.pdf), [Campbellfield sheet, Oct 2026](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf)). The price is AUD 19,975 fitted, compliance extra ([Unsealed 4x4, Oct 2025](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/)).

The kit list on the vehicle page names: heavy-duty front coils, 12-leaf rear springs, Platinum 8-way adjustable remote-reservoir shocks, an adjustable caster correction bush kit, urethane spring-eye bushes, greasable shackles and pins, four U-bolts, two ADR 42/04 mudflaps, a front brake upgrade kit, a rear brake upgrade kit, a brake booster upgrade (VDJ79 ABS), a handbrake upgrade kit, a handbrake cable extension bracket, a complete rear diff housing with track correction (LSD or E-locker), diff oil, two Category 6 side direction indicators, a 4,495 kg tyre placard decal and an owner's manual. No wheels or tyres are in the kit.

What Lovells publishes, and what it does not:

| Item | Lovells' own words | Value to use |
|---|---|---|
| Rear track | Housing gives "track correction to bring the rear in line with the front" ([Elite kit page](https://lovells.com.au/elite-landcruiser-track-correction/4495-elite-gvm-upgrade-single-cab/)) | 1,555 mm with ET 0 wheels (est., section 3) |
| Brakes | "Brake booster upgrade, larger rotors, and heavy-duty pads" (same page) | Sizes not published (section 4) |
| Tyre load index | Not published for the Elite. The 4,200 kg kit "requires tyres with a minimum load index of 117 on O.E. wheels, or can be derated to 3900kg on O.E. tyres" (Campbellfield sheet) | LI 121 (est.) |
| Tyre speed | Not published for the Elite. Lovells' installer lists L for 3,900 kg and M for 4,200 kg ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)) | M, 130 km/h (est.) |
| Wheel load rating | Not published | 1,425 kg (est.) |
| Wheel size and offset | Not published. The 4,200 kg rule names O.E. wheels | Toyota's 16 x 7 ET 0 (est.) |

How the estimates follow:

- Load index. Lovells' 4,200 kg index is half the 2,550 kg rear axle (1,275 kg) rounded up to the next index, LI 117 at 1,285 kg. The 3,900 kg kit follows the same rule: 2,360 kg gives 1,180 kg and LI 114. The Elite's 2,850 kg rear axle gives 1,425 kg a tyre, so LI 121 at 1,450 kg. The plan's LI 123 at 1,550 kg passes with 9 % in hand.
- Wheel rating. An engineer at Touring Solutions Australia, a GVM certifier, gives the industry method as the rear axle rating divided by two, and says a GVM upgrade needs wheels rated for the new load ([4X4 Australia](https://www.4x4australia.com.au/sponsored/loaded-load-rated-wheels)). For the Elite that is 1,425 kg. The national code also requires tyre capacity for a re-rated GVM "both in total and across individual axles", and allows no drop in load or speed rating on a modified vehicle ([VSB 14 Section LS, clauses 4.1 and 4.3](https://www.tmr.qld.gov.au/-/media/Safety/Vehicle-standards-and-modifications/Vehicle-modifications/Light-vehicle-modifications/NCOP/20sectionlssuspensionsteering.pdf)).
- Wheel size and offset. On a vehicle with modified axles, replacement rims must follow the approval document on overall diameter, tyre width and rim offset (VSB 14 LS clause 4.3). With non-original axle parts, the wheel offset may grow by at most 12.5 mm a side ([NSW VSI 09](https://www.nsw.gov.au/sites/default/files/2021-02/RMS-Guideline-for-alternative-wheels-and-tyres-Vehicle-Standards-Information-No-9-November-2003.pdf)). Toyota's wheels are 16 x 7 ET 0 alloy and 16 x 5.5 ET 20 steel ([wheel-size.com](https://www.wheel-size.com/size/toyota/land-cruiser/70-series-2007-now/)). So keep 16 inch, 7 inch rims and ET 0.

What else the LC5 certifier will check, from the kit list and the NSW rules:

1. A Lovells authorised fitter fits the kit and a Lovells-endorsed signatory inspects it (report 16, from [Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)).
2. The 4,495 kg placard decal, or the derated one, is on the ute. Every tyre, the spare included, meets its load index and speed.
3. Each axle carries one wheel and tyre type. No spacers. The wheels and tyres stay inside the bodywork or mudguards when straight, and touch nothing from lock to lock with the ute laden ([VSB 14 LS clause 4.2.3](https://www.tmr.qld.gov.au/-/media/Safety/Vehicle-standards-and-modifications/Vehicle-modifications/Light-vehicle-modifications/NCOP/20sectionlssuspensionsteering.pdf), [VSI 09](https://www.nsw.gov.au/sites/default/files/2021-02/RMS-Guideline-for-alternative-wheels-and-tyres-Vehicle-Standards-Information-No-9-November-2003.pdf)). This is where the bike box's tubs matter (section 3).
4. Both Category 6 side indicators and both ADR 42/04 mudflaps are fitted. The mudflaps move outward with the rear tyres.
5. The brake parts are the kit's own, and the LSPV is reset with the box on (GV04).
6. GVM stays under 4,500 kg. Report 16 notes that an Approved Vehicle Examiner is needed above 4.5 t, so the Elite, and the derate, keep the ute a light vehicle.

## 2. Wheels

The wheel must be 5 x 150 with at least a 110.1 mm bore and M14 x 1.5 nut seats. The trailer needs zero or positive offset, because Cruisemaster does not allow negative offset (report 06, from Cruisemaster's XT coil guide). The ute needs about ET 0 to keep Lovells' track and its approval (section 1). The target is 1,425 kg.

| Wheel | Size, ET | Type | Rating | Mass | Price each | Ute | Trailer |
|---|---|---|---|---|---|---|---|
| ROH Trak 2 (or Blak Trak, same rim in black) | 16 x 7, 0 | Steel | 1,400 kg ([ROH](https://roh.com.au/wheels/trak-2)) | 14.5 kg (est.) | AUD 230 (est.) | Yes, 25 kg short | Yes |
| Toyota genuine GXL alloy | 16 x 7, 0 | Cast alloy | Not published. Lovells rates its kits on factory wheels | 15.0 kg ([wheel-size.com](https://www.wheel-size.com/size/toyota/land-cruiser/70-series-2007-now/)) | AUD 316 used ([eBay set of 5](https://www.ebay.com.au/b/Toyota-Car-and-Truck-Wheels-16-Wheel-Diameter/179679/bn_7116944418)), AUD 550 new (est.) | Yes | Yes |
| Dynamic Steel, Sunraysia style | 16 x 8, 0 or negative | Steel | 1,400 kg ([4X4 Australia](https://www.4x4australia.com.au/gear/wheels-tyres/dynamic-wheel-product-test)) | Not published | From AUD 110 | No gain on ROH | Yes at ET 0 |
| ROH Hammer | 16 x 9, -12 | Alloy | 1,500 kg ([ROH](https://roh.com.au/wheels/hammer)) | 12.0 kg | Not published | Needs a rim-width certificate, worse box clearance | No, negative |
| ROH Assault | 16 x 9, -12 | Alloy | 1,500 kg ([ROH](https://roh.com.au/wheels/assault)) | Not published | Not published | As Hammer | No, negative |
| Loaded Gibb 1675 | 17 x 9, -12, -25 or -59 | Flow-formed alloy | 1,675 kg ([Loaded](https://shoploadedwheels.com.au/collections/gibb-1675)) | 12.3 kg | AUD 394 | Needs 17-inch tyres | No, negative |
| Lenso M-79 | 17 x 9, -12 or -59 | Alloy | 1,500 kg ([Lenso](https://lensowheels.com.au/pages/landcruiser-wheels)) | Not published | From AUD 300 | Needs 17-inch tyres | No, negative |
| Black Rock Duty or Cargo | 16 x 7, +35 to +55 | Alloy | 1,500 kg ([CNC Wheels](https://cncwheels.com.au/shop/4x4-rims/black-rock-duty-satin-black-16x7-5x150-wheel/)) | Not published | AUD 399 | No. A van wheel, narrows the track 70 to 110 mm | Yes, but no use alone |

Findings:

- Every 5 x 150 wheel found at 1,500 kg or more for the 70 Series has a negative offset, a 9-inch rim or a 17-inch diameter. Most are made to push the 79's narrow rear track out, which the Elite now does in the housing.
- ROH's 1,400 kg is the highest published rating for a 16-inch 5 x 150 steel wheel, as report 09 also found.
- A German recall of the Trak 2 covers only the 17 x 7 version sold in Europe from 2015 to 2020 ([delta4x4](https://delta4x4.com/fr/rappel-de-la-jante-en-acier-roh-trak2/)). The 16 x 7 is not affected.
- A 17-inch route needs a 17-inch wheel with ET 0 to +20 and at least 1,450 kg. None was found. ROH's 17 x 9 ET +35 at 1,500 kg suits the 200 Series and would narrow the 79's track by 70 mm, below Toyota's own minimum. The matching tyre would be LT265/70R17 121S, 804 mm and 1,450 kg ([Toyo AT3 sheet](https://toyotires.s3-ap-southeast-2.amazonaws.com/public/brochures/Toyo%20Tires-Open%20Country%20AT_Three-Product%20Specifications.pdf)).

Choice. Two wheels fit both vehicles: the ROH Trak 2 and Toyota's own alloy. Neither has a published rating of 1,425 kg. Ranked by the project's order:

- Record of hard use. ROH sells the Trak 2 as a mine-site approved rim. Toyota's alloy has run on every GXL 79 since 2007. Both qualify.
- Parts and service. ROH sells through tyre shops nationally. Toyota sells through its dealer network. Both qualify.
- Field service. A bent steel rim can be beaten back far enough to seal. A cracked alloy cannot. The steel wheel wins.
- Mass. 14.5 kg (est.) against 15.0 kg. About equal.

So the steel wheel wins, provided its 1,400 kg rating is made legal. Plate the rear axle at 2,800 kg, which is exactly twice the wheel's rating, and the GVM at 4,450 kg. The model's heaviest rear axle with growth is 2,586 kg, and each rear wheel then carries 1,293 kg, 107 kg under the wheel's rating. The ute keeps 250 kg more rear axle than the Platinum's 2,550 kg, which is the reason H17 chose the Elite.

Fallback. If the certifier or Lovells will not issue the 2,800 kg rating, or the Elite's front caliper touches the steel wheel's centre at the dry fit, use Toyota's 16 x 7 ET 0 alloy on all wheels. It is the wheel Lovells' approval assumes, so it needs no rating check and clears the Elite's brakes by design (assumption).

Effect on the trailer and the spare:

- Primary (ROH Trak 2): no change. The trailer keeps ET 0, C/F 190 mm and its 1,555 mm track. The trailer's heaviest wheel load under VSB 1's 120 % rule is 975 kg at the 3,500 kg plate, so 1,400 kg passes with 44 % in hand. One spare on the trailer and one under the ute's tray fit either vehicle, as now.
- Fallback (Toyota alloy): the same offset, track and C/F. Use Toyota's alloy-wheel nuts at 131 Nm in place of the steel wheel's 209 Nm ([70 Series Store](https://70seriesstore.com/blogs/information/recommended-79-series-wheel-nut-torque)). Cruisemaster machines the studs to the wheel's mounting-pad thickness (report 06), so order the LC5 studs for the alloy's thicker pad. Mass rises about 0.5 kg a wheel (est.), 5 kg over ten wheels. The spare rule is unchanged.

Fit check at the Elite fitting (stage S4): offer one bare wheel to a front hub before tyres are mounted, turn it a full turn, and look for 3 mm or more between the spokes and the caliper (est. allowance). Use the result to confirm the primary or switch to the fallback.

## 3. Track

Toyota gives the 2017 single cab 1,555 mm front and 1,460 mm rear on its ET 0 alloys with 265/70R16, and 1,515 mm and 1,420 mm on the narrow tyres. The rear is 95 mm narrower in both cases (report 16, from Toyota BBGJ1007). Lovells says only that the Elite housing brings the rear in line with the front. Multidrive's track-correction housing for the 79 does the same job with new billet tubes between Toyota's centre and ends, and it needs longer brake lines ([4X4 Australia](https://www.4x4australia.com.au/gear/2024-toyota-landcruiser-79-gxl-multidrive-rear-track-correction)). Assumption: the Elite's rear track is 1,555 mm on the ET 0 wheel, 47.5 mm further out each side. The housing's track change is covered by Lovells' approval, so the VSB 14 limit of 50 mm over the factory track applies only to later wheel changes.

The tyre is the Toyo Open Country A/T III LT265/75R16 123R at 804 mm and 267 mm wide on its 7.5-inch measuring rim, rated 1,550 kg, approved on 7.0 to 9.0-inch rims ([Toyo sheet](https://toyotires.s3-ap-southeast-2.amazonaws.com/public/brochures/Toyo%20Tires-Open%20Country%20AT_Three-Product%20Specifications.pdf)). The model uses 268 mm, which is kept here.

| Measure (ute centreline to) | Factory housing | Elite housing |
|---|---|---|
| Rear track | 1,460 mm | 1,555 mm (est.) |
| Rear tyre centre | 730 mm | 777.5 mm |
| Rear tyre outer face | 864 mm | 911.5 mm |
| Rear tyre inner face | 596 mm | 643.5 mm |
| Width over the rear tyres | 1,728 mm | 1,823 mm |
| Tyre inner face to frame rail outer face (523 mm) | 73 mm | 120.5 mm |
| Tub inboard wall, tyre-side face (`tub_y0`) | 556 mm | 603.5 mm |
| Floor width between the tub walls | 1,106 mm | 1,201 mm |
| Tub top width, tub wall to side skin | 369.5 mm | 322 mm |
| Side skin inner face (box 1,850 mm) | 922.5 mm | 922.5 mm |
| Tyre outer face to side skin, Toyota needs 30 mm | 58.5 mm | 11 mm, fails by 19 mm |

The tub's top height (86.5 mm above the floor) and length do not change if the Elite's springs give the same ride height as the model assumes. Toyota's rules are 25 mm over the tyre at full bump, 30 mm outside it and 40 mm inside it (BBGJ1007, wheel house space, offline, see Toyota's [LC70BBG](https://myfleet.toyota.com.au/customer/userfiles/LC70BBG.pdf)). Checks UGW-01 and UGW-02 still pass, because the tub follows the tyre. UGW-03 fails. The tyre's real shoulder at the tub's height is a few millimetres narrower than the model's 268 mm cylinder, which is not enough to pass.

Ways to restore the 30 mm:

| Fix | Numbers | Cost to the design |
|---|---|---|
| A. A flare on each side wall over the rear tub (recommended) | Skin inner face at 941.5 mm or more over the tub, outer face 944 mm. Box 1,888 mm over the tubs, 1,890 mm with tolerance (est.). Flare length about 925 mm: the 865 mm tub opening plus 30 mm each end | About 2 x 1 kg of 2.5 mm 5052 sheet and rivets (est.). The rest of the box stays 1,850 mm |
| B. Raise the floor until the tyre clears it | Tyre top at full bump is 58.5 mm above today's floor. Floor up 87.5 mm, deck 921.5 mm laden (est.). The tubs go | Bikes and box centre of gravity 87.5 mm higher, or 87.5 mm less headroom |
| C. A rear wheel offset of +19 mm or more | Pulls the tyre back in | No such wheel found, it undoes the track correction and ends the shared wheel |

Fix A needs a decision on UTE-09 (since taken as H19), the 1,850 mm box limit. Toyota's text says "the width of a mounted part should be 60 mm maximum as measured from the outermost point of the cab of the base vehicle (not including the outside mirror)" (BBGJ1007, section 1-2, offline, see Toyota's [LC70BBG](https://myfleet.toyota.com.au/customer/userfiles/LC70BBG.pdf)). The decision log read that as 60 mm in total on the 1,790 mm cab, which gives 1,850 mm. Measured from the cab's outermost point on each side, it allows 1,790 + 2 x 60 = 1,910 mm. The flared box at 1,890 mm stands 50 mm beyond the cab each side, inside that reading. ADR 43/04 allows 2,500 mm. The factory GXL is already 1,870 mm over its own flares (report 16). Assumption for the designer: rule that UTE-09 limits the box body to 1,850 mm and the rear tub flares to 1,910 mm, and model fix A.

Other effects of the wider rear track:

- The floor between the tubs gains 95 mm (1,201 mm). The tool chests on the tubs lose 47.5 mm of width unless the flares add some back (fix A adds about 20 mm).
- Lovells' two ADR 42/04 mudflaps sit behind the rear tyres, so their brackets move out 47.5 mm with the tyres.
- The trailer's 1,555 mm track already matches the ute's front. With the Elite the trailer also runs in the ute's rear ruts.
- The mean track rises from 1,507.5 to 1,555 mm, so the ute's static stability factor rises about 3 % (my arithmetic, same centre of gravity).

## 4. Brakes

The Elite includes the brakes for 2017 to 2022 cab chassis. The kit list names a front brake upgrade kit, a rear brake upgrade kit, a booster upgrade for the ABS VDJ79, a handbrake upgrade kit and a handbrake cable extension bracket ([Lovells 79 vehicle page](https://lovells.com.au/vehicle/toyota-landcruiser-79-series-03-2007-08-2022/)). Lovells describes them as a booster upgrade, larger rotors and heavy-duty pads ([Elite kit page](https://lovells.com.au/elite-landcruiser-track-correction/4495-elite-gvm-upgrade-single-cab/)). The September 2022 J7 V8 kit leaves the brakes out ([Unsealed 4x4](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/)). Lovells publishes no rotor size. Toyota's front disc is 322 mm ([Alcon](https://alconkits.com/blogs/guides/lc76-79-front-brake-kits-alcon-4-piston-vs-6-piston)). Alcon's 328 mm four-piston kit for the 79 clears Toyota's 16-inch wheels, so a larger rotor can fit inside them. The handbrake cable extension bracket suggests the cables now reach drums 47.5 mm further out (assumption).

Assumptions: the Elite's front rotor and caliper clear Toyota's 16-inch wheels, because Lovells sells the kit for a model that leaves the factory on them, puts no wheel in the kit and states no wheel condition. The kit's rear parts include the longer rear lines that the wider housing needs, as Multidrive's equivalent housing does (section 3).

Effect on the car build's brake lines:

| Line | Plan | With the Elite | AUD |
|---|---|---|---|
| BR01 Bendix U4WD-BUK34 rear slotted rotors and pads | Required | Drop. The Elite replaces the rear brakes, and factory-size rotors no longer match its larger ones | -555.01 |
| BR02 Delios DLS0790 front slotted rotors | Required | Drop. The Elite's front kit has its own larger rotors | -280.01 |
| BR03 Bendix front pads | Required | Drop. The Elite has heavy-duty pads | -150.00 |
| BR04 BQTL70S braided line set | Required | Drop. It is made for the factory caliper positions, and the Elite moves the rear calipers out 47.5 mm and changes the front calipers | -515.00 |
| BR05 DOT 4 flush | Required | Keep. The fitter bleeds the new system and fills it with DOT 4 | 0 |
| BR06 (new) spare Elite pads, one front and one rear set, carried | None | Add, required. The larger rotors take pads that remote Toyota dealers are not likely to stock (assumption) | +350 (est.) |
| Total | | | -1,150.02 |

Other points for the car build:

- Replacement rotors and pads for the life of the kit must be the Elite's own or certified equivalents. Brake parts that are not equivalent need certification in NSW ([VSI 06, items 18 and 19](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf), report 16). So aftermarket slotted rotors are out unless they copy the Elite's size.
- GV04 still resets the LSPV with the box on. Bed the pads in before the LC5 inspection, as the plan says now.
- Stage S4 text: replace "Check the Elite's brake upgrade before buying BR01 to BR05" with "BR01 to BR04 are dropped, the Elite carries its own brakes".
- The trailer's electric brakes and the Tow-Pro controller do not change.

## Open points and the assumption to use

| # | Open point | Assumption to use | Basis |
|---|---|---|---|
| 1 | The Elite's rear track in mm | 1,555 mm with ET 0 wheels, 47.5 mm a side over the factory 1,460 mm | Lovells: "in line with the front". Toyota's front is 1,555 mm on ET 0 |
| 2 | The Elite's minimum tyre load index and speed | LI 121 (1,450 kg) and speed M (130 km/h) | Lovells' rule for its 3,900 and 4,200 kg kits, half the rear axle rounded up |
| 3 | The wheel rating the certifier will ask for | Half the rear axle rating, 1,425 kg at 2,850 kg | TSA's method in 4X4 Australia, VSB 14 LS 4.1 and 4.3 |
| 4 | Whether a 2,800 kg rear axle and a 4,450 kg GVM can be plated on the Elite | Yes (assumption), in the same LC5 inspection, at no extra cost. Lovells' written yes comes before GV05 is bought | Lovells offers a derate for under-rated tyres on its 4,200 kg kit |
| 5 | Whether Lovells' approval covers Toyota's 16 x 7 ET 0 alloy at 2,850 kg | Yes | Lovells rates its 4,200 kg kits "on O.E. wheels", and the Elite kit has no wheels |
| 6 | The Elite's front rotor and caliper size and their wheel clearance | Clears Toyota's 16-inch wheels. Dry-fit the Trak 2 at S4, switch to the alloy if it touches | Kit sold for a 16-inch model with no wheel condition. Alcon's 328 mm kit clears 16-inch wheels |
| 7 | Whether the Elite's rear kit includes the longer rear brake lines | Yes | Multidrive's equivalent housing ships with them |
| 8 | Mass of the Elite over the Platinum | Keep the model's current estimate | Lovells publishes no mass. Not changed by this report |
| 9 | Ride height of the Elite's 12-leaf rear springs | Same as the model's Platinum lift, about 50 mm | Lovells publishes no lift figure |
| 10 | UTE-09 box width with the flares | Box body 1,850 mm, rear tub flares up to 1,910 mm | Toyota's 60 mm rule read per side. Needs a decision (section 3), since taken as H19 |
| 11 | Price of the ROH Trak 2 16 x 7 | AUD 230 each (est., unchanged) | ROH publishes no price |
| 12 | Price of Elite spare pads | AUD 350 for a front and a rear set (est.) | Typical heavy-duty 4WD pad sets, no Lovells price found |

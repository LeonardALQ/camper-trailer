# 16: LandCruiser 79 single cab, limits, GVM and GCM, brakes, wheels, towing and dimensions

Note added 20 Nov 2026, after the ute model (UTE-GARAGE.md) and the trailer's redesign (TRAILER.md). The plan departs from this report in four places. The coupling point is set at 440 mm laden, plus or minus 20 mm, not 450 mm, because 450 plus 20 mm would pass VSB1's 460 mm (decision log 12:10). The ball sits 1,300 mm behind the rear axle, the figure here, which puts the bike box's rear face 210 mm behind the ball in the model. The trailer is plated at 3,100 kg, so the combination is 6,700 kg with the ute at its 3,850 kg weighed limit, against the 6,900 kg GCM. And the GVM kit, Lovells' 4,200 kg Platinum or 4,495 kg Elite, is chosen only after the bike box is built and weighed, with one LC5 inspection covering the kit, the box and its winch (decision log 12:45). The data for this report is published as `research/16-ute-limits.yaml` and `research/16-ute-parts.yaml`.

Research report, 20 Nov 2026. The tow vehicle is now a used LandCruiser 79 single cab V8 (VDJ79) with about 400,000 km. It carries both motorbikes in an enclosed box on its tray and tows a 2.5 to 3 t camper trailer. This report sets the ute's legal and physical limits, chooses the GVM and GCM upgrade, the brakes, the wheels and tyres and the towing set-up, and gives the dimensions and Toyota's mounting rules that the bike box (report 17) and the trailer are designed to. Reports 14 and 15 cover the engine and the driveline. The numbers are in `16-ute-limits.yaml` and the parts in `16-ute-parts.yaml`, both beside this file.

Terms used throughout:

- GVM (gross vehicle mass): the most the ute may weigh, loaded, including the towball load.
- GCM (gross combination mass): the most the ute and the trailer may weigh together on the road.
- Axle rating: the most one axle may carry. Toyota calls it the maximum permissible axle capacity.
- Kerb mass: the cab chassis with a full fuel tank and no people or load. Toyota calls it curb weight.
- Towball download: the part of the trailer's weight that sits on the ball.
- Combination mass: the ute's mass plus the trailer's mass less the towball download. The download is counted once, because it sits in both figures.
- NB1: the medium goods vehicle category, GVM over 3.5 t and up to 4.5 t. Up to 3.5 t a goods vehicle is NA.
- VSCCS: the NSW Vehicle Safety Compliance Certification Scheme. A VSCCS licensed certifier inspects a modified vehicle and certifies it.
- SSM (second-stage manufacturer): the federal path for modifying a vehicle before its first registration.
- LSPV (load-sensing proportioning valve): the valve that sets the rear brake pressure from the rear axle load.
- Load index (LI): the tyre's load rating code. LI 117 is 1,285 kg, 120 is 1,400 kg, 123 is 1,550 kg and 126 is 1,700 kg.
- ET (offset): the distance from the wheel's centreline to its mounting face. ET 0 puts the face on the centreline.

## Recommendation

Buy a single cab built from 01/2017 to 08/2022. Lovells' 4,200 and 4,495 kg kits fit single cabs only from 01/2017, and earlier cars stop at 3,900 kg ([Lovells](https://lovells.com.au/wp-content/uploads/2025/04/Lovells_Toyota_79-Series_03-2007-08-2022.pdf)). The 3,900 kg kits' 2,360 kg rear axle is too small for this build (section 2.3). A 2022-on car also takes the kits but costs more. Prefer a GX or GXL. Both came on Toyota's 16 x 7 alloys with 265/70R16 tyres ([BBGJ1007](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf), [Drive](https://www.drive.com.au/news/2023-toyota-landcruiser-70-series-price-and-specs/)), so the planned wheel and tyre match their factory fit. The GXL adds front and rear diff locks (Drive). Report 14 covers the engine of this build range.

GVM: the Lovells 4,200 kg Platinum kit, TOYKIT080-GVM, with axle ratings of 1,650 kg front and 2,550 kg rear. Lovells' authorised fitter fits it, a NSW VSCCS certifier inspects it after registration, and the LSPV is reset. The planned build weighs about 3,753 kg, which leaves 447 kg under the GVM. The binding limit is the rear axle, with 121 kg in hand. It reaches 2,550 kg at about 3,870 kg in total. Hold the weighed ute to 3,850 kg with no more than 250 kg on the ball. The step up is Lovells' 4,495 kg Elite, which raises the rear axle to 2,850 kg and replaces the rear housing, axles and diff, at AUD 19,975 fitted.

GCM: keep Toyota's 6,900 kg. The planned combination is 3,753 kg plus a 3,000 kg trailer less 250 kg on the ball, 6,503 kg. Take Lovells' 7,400 kg revision only if the certifier includes it at no extra cost.

Brakes: the V8 79 already has discs all round. Keep the factory calipers, master cylinder and booster. Fit slotted factory-size rotors, Bendix Ultimate 4WD pads and braided lines, flush with DOT 4, and reset the LSPV. A big brake kit needs 17-inch wheels and would end the shared wheel.

Wheels and tyres: ROH Trak 2 16 x 7 ET 0 5 x 150 steel wheels, rated 1,400 kg, with LT265/75R16 123/120 load range E tyres (Yokohama Geolandar A/T G015 or Toyo Open Country A/T III), 1,550 kg each. Six for the ute, four plus two spares.

Shared trailer wheel: yes. Order the trailer's Cruisemaster XT Freestyle Air with LC5 M14 hubs (5 x 150) on its 12-inch ABS-enabled drums, with the 110 mm spigot. At a 3,000 kg ATM each wheel must carry 825 kg under VSB1's 120 % rule, against 1,400 kg for the wheel and 1,550 kg for the tyre. Set the trailer's axle spacing to 900 mm, because the 804 to 805 mm tyre sits at the XT's 804 mm limit for 880 mm. Carry one spare under the ute's tray and one on the trailer. Each fits either vehicle.

Towing: Hayman Reese 03186RW towbar (3,500 kg, 350 kg), REDARC Tow-Pro Elite V3 with the universal wiring kit, a 12-pin flat plug, and an Anderson SB50 charging feed on 6 B&S cable with a 50 A fuse. The ute is 12 V. Set the coupling point at 450 mm, plus or minus 20 mm, with the ute laden.

| Item | AUD | Basis |
|---|---|---|
| Lovells 4,200 kg Platinum kit | 5,620 | 2024 listing |
| Fitting by a Lovells authorised fitter | 1,500 | Estimate |
| NSW VSCCS certification | 1,500 | Estimate, within AUD 1,000 to 2,500 |
| Alignment and LSPV reset | 250 | Estimate |
| Brakes: rotors, pads, braided lines, fluid | 1,540 | Listings plus estimates |
| Six ROH Trak 2 wheels | 1,380 | Estimate, AUD 230 each |
| Six LT265/75R16 tyres, fitted and balanced | 2,730 | Estimate, AUD 420 plus 35 each |
| Hayman Reese 03186RW towbar, self-fitted | 1,160 | ARB listing |
| Tow-Pro Elite V3, wiring kit and mount | 744 | REDARC listings |
| 12-pin plug, Anderson SB50, cable and fuse | 330 | Estimate |
| Total, required | 16,754 | |
| Optional: ARB Frontier 180 L fuel tank | 1,557 | ARB listing, self-fitted |
| Optional: Lovells Elite in place of the 4,200 kg kit and its fitting | +12,855 | Unsealed 4x4 price |

This report's share takes about AUD 16,750 of the AUD 30,000, leaving about AUD 13,250 for the engine (report 14) and the driveline and refresh (report 15). The whole vehicle plan is likely to need a larger budget. The trailer's four wheels and tyres come from the trailer's budget.

What blocks the plan: nothing outright. Four limits shape it. The rear axle caps the ute at about 3,850 kg. The kit dictates the build range, 01/2017 on. Lovells requires its own fitter, so Leonard cannot fit the GVM kit himself. And the trailer needs its axle spacing moved from 880 to 900 mm.

## 1. Limits by build date

Toyota changed the single cab's ratings three times. Braked towing stays at 3,500 kg and unbraked at 750 kg in every Toyota sheet ([2011 brochure](https://xr793.org/wp-content/uploads/2023/10/2011-Toyota-Land-Cruiser-70-Saver-AUS.pdf), [June 2021 spec data](https://toyotamedia.b-cdn.net/files/2021/11/LC70_Spec_Data_Jun2021.pdf), [September 2023 spec sheet](https://brookshire.com.au/BrooksHire/media/Media/Spec%20Sheets/LandCruiser-70-Spec-Sheet.pdf)). The towball download is 350 kg ([Practical Motoring, 2017 79 review](https://practicalmotoring.com.au/4x4/2017-toyota-landcruiser-79-series-offroad-review/)), which matches the 350 kg rating of the Hayman Reese bar for the 79 ([ARB](https://www.arb.com.au/product/t03186rw-hayman-reese-class-4-tow-bar-3500-350kg-rating-landcruiser-79-series)).

| Build | GVM | GCM | Front axle | Rear axle | Kerb mass, cab chassis | Fuel |
|---|---|---|---|---|---|---|
| 03/2007 to 12/2016 | 3,300 kg | 6,800 kg | 1,460 to 1,480 kg | 2,300 kg | 2,055 to 2,075 kg | 180 L |
| 01/2017 to 08/2022 | 3,400 kg | 6,900 kg | 1,500 kg | 2,300 kg | 2,165 to 2,230 kg | 130 L |
| 09/2022 to 08/2023 | 3,510 kg | 6,900 kg | 1,500 kg | 2,300 kg | Not published (assume as 09/2023) | 130 L |
| 09/2023 on | 3,510 kg | 7,010 kg | 1,500 kg | 2,300 kg | 2,185 to 2,200 kg | 130 L |

Sources by row:

- 2007 to 2016: GVM, kerb mass and fuel from Toyota's [2014 brochure](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf) and [2011 brochure](https://xr793.org/wp-content/uploads/2023/10/2011-Toyota-Land-Cruiser-70-Saver-AUS.pdf). The 2011 brochure prints 3,330 kg, so the lower 3,300 kg is used. GCM and axle ratings from [Lovells](https://lovells.com.au/wp-content/uploads/2025/04/Lovells_Toyota_79-Series_03-2007-08-2022.pdf). A Lovells store sheet gives the front axle as 1,460 kg ([Lovells Campbellfield](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf)), so plan on 1,460 kg.
- 2017 to 2022: Toyota's [June 2021 spec data](https://toyotamedia.b-cdn.net/files/2021/11/LC70_Spec_Data_Jun2021.pdf) and Toyota's 2017 [Body Builder's Guide BBGJ1007](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf) for the Australian VDJ79R-TJMRYQ3 (WorkMate) and TJMNYQ3 (GXL). Lovells confirms 3,400 kg and 6,900 kg "on single cab from 01/2017" ([Lovells Campbellfield](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf)).
- 2022 on: [Drive, December 2022](https://www.drive.com.au/news/2023-toyota-landcruiser-70-series-price-and-specs/), the [Lovells J7 sheet](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_eb6ad9c53f034149b69cc08e5072833e.pdf) and Toyota's [September 2023 spec sheet](https://brookshire.com.au/BrooksHire/media/Media/Spec%20Sheets/LandCruiser-70-Spec-Sheet.pdf).

Kerb axle loads. Only Toyota's Body Builder's Guide gives them. For the 2017 single cab chassis it lists front 1,265 to 1,295 kg and rear 900 to 925 kg (WorkMate) or 910 to 935 kg (GXL), so about 58 % sits on the front axle. Toyota's own split at the 3,400 kg GVM is 1,470 kg front and 1,930 kg rear. The unsprung mass is 250 kg per axle ([BBGJ1007, section 4](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)).

What the 2017 update changed: GVM up 100 kg, GCM up 100 kg, kerb mass up about 110 kg, the fuel tank down from 180 L to 130 L, and new gear ratios (second 2.464 to 2.294, fifth 0.881 to 0.750), from the 2014 and 2021 Toyota sheets. Report 14 covers the engine side of that update.

What the September 2022 update changed: Toyota raised the GVM of every 70 Series to 3,510 kg. That makes the 79 a medium goods vehicle (NB1), which exempts it from the ADR 85 side-impact rule, and Toyota added autonomous emergency braking. Drive could not confirm any suspension or brake change ([Drive](https://www.drive.com.au/news/2023-toyota-landcruiser-70-series-price-and-specs/)). The axle ratings stayed at 1,500 and 2,300 kg, and the GCM stayed until the September 2023 facelift raised it to 7,010 kg ([Lovells J7 sheet](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_eb6ad9c53f034149b69cc08e5072833e.pdf)). Lovells sells its 4,495 kg kit for the 2022-on V8 without the brake upgrade it includes for 2017 to 2022 cars, which suggests the later V8's brakes differ ([Unsealed 4x4](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/)). The V8 has since ended: Toyota's [December 2025 brochure](https://cruiserarchive.com/wp-content/uploads/2025/12/70SeriesCurrentBrochure.pdf) lists only the 2.8 L four-cylinder.

Every V8 79 has ventilated disc brakes front and rear (Toyota 2011 and 2021 sheets above). The 2017 single cab has a 12 V system with a 1,560 W alternator (BBGJ1007, section 4).

## 2. GVM and GCM upgrades

### 2.1 Kits for the single cab

| Kit and part | Fits | GVM | Front / rear axle | GCM | Tyre needed | Price |
|---|---|---|---|---|---|---|
| Lovells 3,900 kg Comfort, TOYKIT061-GVM | 03/2007 to 08/2022 | 3,900 kg | 1,540 / 2,360 kg | Factory (6,800 or 6,900 kg) | LI 114, speed L | Not found |
| Lovells 3,900 kg Touring | 03/2007 to 08/2022 | 3,900 kg | 1,540 / 2,360 kg | 7,400 kg | LI 114, speed L | Not found |
| Lovells 4,200 kg Touring or Platinum, TOYKIT080-GVM | Single cab from 01/2017, and the 2022-on J7 | 4,200 kg | 1,650 / 2,550 kg | 7,400 kg | LI 117, speed M | Platinum kit AUD 5,620 |
| Lovells 4,495 kg Elite | Single cab from 01/2017, and the J7 | 4,495 kg | 1,650 / 2,850 kg | 7,400 kg | LI 121 (my arithmetic, 1,425 kg a tyre) | AUD 19,975 fitted (2017 to 2022), 18,875 (J7 V8) |
| Dobinsons 3,900 or 3,999 kg | 78 and 79 Series | 3,900 or 3,999 kg | Not published | No GCM upgrade | Not published | Not found |
| Terrain Tamer 3,950 or 4,150 kg | The 3,510 kg J7 | 3,950 or 4,150 kg | Not published | Not published | Not published | AUD 5,317.73 plus fitting |
| Outback Armour 3,800 kg | J7 single cab | 3,800 kg | Not published | Not published | Not published | Not found |

Sources: Lovells ratings from the [head-office sheet](https://lovells.com.au/wp-content/uploads/2025/04/Lovells_Toyota_79-Series_03-2007-08-2022.pdf), which says earlier cars are limited to 3,900 kg, and the store sheets for [2007 to 2022](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf) and the [J7](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_eb6ad9c53f034149b69cc08e5072833e.pdf). Part numbers, contents and tyre rules from a Lovells installer ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)), which dates the 4,200 kg single cab kit from 10/2016. The AUD 5,620 Platinum price is a 2024 [Fulcrum Suspensions listing](https://fulcrumsuspensions.com.au/search/product/gvm-btc-upgrade-kits/lovells-gvm-btc-upgrade-kits-for-2017-toyota-land-cruiser-79-series/brand-LOVELLS) seen in a search result, as the page refuses direct requests. Elite contents and prices from [Unsealed 4x4](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/). Dobinsons from a [Dobinsons installer](https://chicken-cornet-9bdj.squarespace.com/gvm-upgrades/landcruiser-79-series), Terrain Tamer from [4x4 Australia](https://www.4x4australia.com.au/gear/2024-toyota-landcruiser-vdj79-build-begins), and Outback Armour from its [brochure title](https://oppositelockgoldcoast.com.au/docs/kits/outback-armour-vehicles-207-a4-brochure-toyota-landcruiser-70-j7-79-single-cab-gvm-upgrade-3800kg.pdf).

What a Lovells 4,200 kg kit contains: two heavy-duty front coil springs, two rear leaf spring packs, four twin-tube shock absorbers, three urethane bush kits, four high-tensile U-bolts, greasable shackles and pins, two mudflaps, two category 6 side indicators, a new tyre placard with the axle ratings, and manuals ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)). The Platinum version uses remote-reservoir shocks ([Lovells J7 sheet](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_eb6ad9c53f034149b69cc08e5072833e.pdf)). The Elite adds a rear housing widened to the front track, two-piece full-floating chrome-moly axles, larger bearings, an exchange rear diff and, on 2017 to 2022 cars, front and rear brake upgrades with a new brake booster ([Unsealed 4x4](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/)).

Lovells also sells a 4,000 kg braked towing upgrade for 2017 to 2022 single cabs, only with its GVM kit. The trailer stays under 3,500 kg, so it is not needed.

### 2.2 The NSW process for a registered ute

- The federal path is closed. Lovells says a registered vehicle cannot be fitted under federal approval and needs state compliance through a Lovells-endorsed engineering signatory ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)). ADR 80/04 has closed the pre-registration path for many V8 79s in any case ([Unsealed 4x4, May 2026](https://unsealed4x4.com.au/gvm-upgrades-australia-2026/)).
- Lovells allows only its authorised fitters to fit the kit, and only its endorsed signatories to inspect it for state compliance ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)). So Leonard buys the fitting, or at least the fitter's sign-off.
- NSW needs certification to re-rate a GVM or a GCM ([TfNSW VSI 06, July 2026, item 51](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf)). A VSCCS licensed certifier inspects the ute ([VSCCS Bulletin 01](https://www.transport.nsw.gov.au/system/files/media/documents/2025/VSFC01-VSCCS-Bulletin-1.pdf)) and a modification plate is issued after the inspection ([Marks 4WD](https://www.marks4wd.com/big-brake-upgrade-landcruiser-70-series.html/)). Above 4.5 t GVM the ute becomes a heavy vehicle and needs an Approved Vehicle Examiner (VSCCS Bulletin 01).
- Cost: post-registration engineering adds about AUD 1,000 to 2,500 ([70 Series Store](https://70seriesstore.com/blogs/information/what-is-the-79-series-towing-gcm)). This plan assumes AUD 1,500 for the GVM, the GCM and the fuel tank in one inspection.
- GCM: Lovells warns that its GCM revision may not be available after registration in every state. Dobinsons says the federal department does not approve GCM upgrades ([Dobinsons installer](https://chicken-cornet-9bdj.squarespace.com/gvm-upgrades/landcruiser-79-series)). VSI 06 item 51 lists GCM re-rating as a certifiable change, so NSW has a path.

### 2.3 Which kit for the planned loads

The binding limit is the rear axle, not the GVM. The bikes, the box and the towball all sit over or behind the rear axle. Each kilogram on the ball, about 1.3 m behind the axle, adds 1.41 kg to the rear axle and takes 0.41 kg off the front.

Axle loads for the planned build, on a 2017 to 2022 cab chassis (positions are along the ute from the front axle, wheelbase 3,180 mm):

| Item | Mass | Position | Front | Rear | Basis |
|---|---|---|---|---|---|
| Cab chassis, kerb | 2,193 kg | | 1,280 kg | 913 kg | Toyota BBGJ1007, mid-range |
| Two people | 160 kg | 1,660 mm | 77 kg | 83 kg | Estimate, 400 mm ahead of the cab back |
| Bull bar and winch | 110 kg | 800 mm ahead | 138 kg | -28 kg | Estimate |
| Tray, box, bikes and tools | 931 kg | 3,310 mm | -38 kg | 969 kg | Tray 150 kg and tools 100 kg estimated, box 300 kg and bikes 381 kg from the brief, centred on the tray |
| Two spare wheels | 74 kg | 3,900 mm | -17 kg | 91 kg | Estimate, 37 kg each (section 4) |
| Towbar | 35 kg | 4,380 mm | -13 kg | 48 kg | Estimate |
| Towball download | 250 kg | 4,480 mm | -102 kg | 352 kg | Brief, ball 1,300 mm behind the axle (estimate) |
| Total | 3,753 kg | | 1,324 kg | 2,429 kg | My arithmetic |

Against each kit:

- Factory (3,400 kg, rear 2,300 kg): over by 353 kg on GVM and 129 kg on the rear axle.
- 3,900 kg kits (rear 2,360 kg): GVM passes, rear axle over by 69 kg. Rejected.
- 4,200 kg kit (front 1,650 kg, rear 2,550 kg): GVM margin 447 kg, rear axle margin 121 kg, front margin 326 kg. It passes. About 116 kg more on the tray takes the rear axle to its limit, at a total of about 3,870 kg. The brief's upper case of 3,900 kg would put the rear axle about 30 kg over.
- 4,495 kg Elite (rear 2,850 kg): rear axle margin 421 kg. It passes every case in the brief.

Recommendation: the Lovells 4,200 kg Platinum kit, TOYKIT080-GVM, on a single cab built from 01/2017. It carries the planned 3,753 kg build with 121 kg in hand on the rear axle and costs about AUD 8,600 with fitting and certification, against about AUD 21,500 for the Elite. Hold the ute to 3,850 kg, weighed, with no more than 250 kg on the ball. The Elite is the step up if the weighed ute comes out heavier, or if report 15 finds that the rear housing, axles and diff need replacing anyway, because the Elite replaces all three.

The front axle carries 35 % of the total, well above the minimum front-axle share in Toyota's Body Builder's Guide.

### 2.4 GCM decision

Combination mass is the ute's mass plus the trailer's mass less the towball download.

- Planned case: 3,753 kg ute plus 3,000 kg trailer less 250 kg gives 6,503 kg, 397 kg under the factory 6,900 kg GCM.
- The brief's heaviest case: 3,900 kg plus 3,000 kg less 250 kg gives 6,650 kg, 250 kg under.
- With the factory GCM and a 3,000 kg trailer, the ute could weigh up to 4,150 kg (6,900 less 3,000 plus 250). That is more than its rear axle allows, so the GCM never binds first.

Decision: keep the factory GCM. A 7,500 or 8,000 kg GCM upgrade buys nothing for a trailer of 3 t or less ([70 Series Store](https://70seriesstore.com/blogs/information/what-is-the-79-series-towing-gcm) describes those upgrades as being for towing the full 3,500 kg while over the factory GVM). They come bundled with a GVM upgrade, because extra GCM is only usable when the GVM has room too (same source), and Lovells' 7,400 kg revision comes only with its GVM kits ([Lovells](https://lovells.com.au/wp-content/uploads/2025/04/Lovells_Toyota_79-Series_03-2007-08-2022.pdf)). Accept Lovells' 7,400 kg revision only if the NSW certifier includes it at no extra cost. It would let a trailer of up to 3,450 kg run behind a 4,200 kg ute.

## 3. Brakes

Every V8 79 has ventilated discs front and rear from 2007 ([Toyota 2011 brochure](https://xr793.org/wp-content/uploads/2023/10/2011-Toyota-Land-Cruiser-70-Saver-AUS.pdf), [Toyota 2021 spec data](https://toyotamedia.b-cdn.net/files/2021/11/LC70_Spec_Data_Jun2021.pdf)). So no drum-to-disc conversion is needed. Bendix also lists its rear kit for the VDJ79 from 2007 to 2024 as a kit for "vehicles with existing rear disc brakes" ([Marks 4WD](https://www.marks4wd.com/rear-brake-upgrade-landcruiser-70-series.html)).

### 3.1 What the GVM kit needs

- The Lovells 4,200 kg kit lists no brake parts ([Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)), so Lovells rates it on the factory brakes. Lovells adds brake upgrades and a new booster only in the 4,495 kg Elite for 2017 to 2022 cars ([Unsealed 4x4](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/)).
- The LSPV must be reset. Toyota says the brake system and piping must not be modified, and that the LSPV must be readjusted once a body or alteration is complete. The check uses Toyota's gauge set 09709-29018: at 5.9 MPa in the front circuit the rear should read 4.9 ± 0.5 MPa, and at 7.8 MPa it should read 5.4 ± 0.7 MPa, at Toyota's standard rear axle load ([BBGJ1007, section 2-5](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)). A GVM kit changes the rear ride height and spring rate, so the valve must be reset after it is fitted. The Lovells fitter or a brake shop does this before the certifier's inspection.

### 3.2 Upgrades that keep the 16-inch wheel

NSW needs certification only for brakes that are not a factory option, or for parts that are not equivalent, such as multi-piston calipers or a different master cylinder ([TfNSW VSI 06, items 18 and 19](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf)). Factory-size rotors, pads and hoses stay outside that.

| Part | What it is | Price | Source |
|---|---|---|---|
| Bendix Ultimate 4WD rear kit U4WD-BUK34 | Two slotted rear rotors, two pairs of ceramic pads, VDJ79 2007 to 2024 | AUD 504.55 ex GST (555.01 with GST) | [Marks 4WD](https://www.marks4wd.com/rear-brake-upgrade-landcruiser-70-series.html) |
| Delios DLS0790 slotted front rotors | LandCruiser 70 and 100 front | AUD 254.55 ex GST (280.01 with GST) | [Marks 4WD](https://www.marks4wd.com/rear-brake-upgrade-landcruiser-70-series.html) (related products) |
| Bendix Ultimate 4WD front pads | Ceramic, to match | AUD 150 (estimate, price not found) | |
| BQTL70S braided brake lines, complete set | LandCruiser 70 | AUD 435 to 595 | [Marks 4WD](https://www.marks4wd.com/rear-brake-upgrade-landcruiser-70-series.html) (related products) |
| DOT 4 fluid flush | | AUD 40 (estimate) | |

Total about AUD 1,540 with GST. Fit the rotors and pads with the GVM kit and bed them in before the certifier's inspection.

### 3.3 Upgrades not recommended

- The Bendix 6-piston front kit, U4WD-BBUK216F, with 340 mm rotors, sells for AUD 4,086 (AUD 5,450 list). It needs 17-inch wheels or larger, is listed for the VDJ79 from 2007 to 08/2014 without ABS, and in NSW needs an engineering inspection before a modification plate is issued ([Marks 4WD](https://www.marks4wd.com/big-brake-upgrade-landcruiser-70-series.html/)). It would rule out the 16-inch wheel the trailer shares (section 4).
- Wilwood's 70 Series front kit uses 6-piston calipers on 13.28-inch (337 mm) rotors ([Wilwood](https://www.wilwood.com/BrakeKits/BrakeKitSearch?axle=Front%20Kit&make=Toyota&model=Land%20Cruiser&option=J70%20Series%20%28Africa,%20MidEast,%20Australia%29&year=2015)). The rotor size implies 17-inch wheels too (assumption).
- A different master cylinder or booster needs certification under item 19. Keep the factory parts at 4,200 kg. Report 15's refresh checks the master cylinder, the booster and its vacuum supply at 400,000 km.

### 3.4 What the extra power changes

The trailer carries its own electric brakes and Bosch TSC (report 06), so the ute's brakes stop the ute's own mass and the share of the towball. The tuned engine adds speed and heat on long descents, which slotted rotors and high-temperature pads handle better than the factory parts. The Tow-Pro controller (section 5) sets how hard the trailer brakes, which keeps the ute's brakes from doing the trailer's work.

## 4. Wheels and tyres

### 4.1 Factory wheels and the NSW rules

- Factory sizes for the 2017 single cab: 225/95R16C as standard, with 7.50R16LT and 265/70R16LT as options. Placard pressures are 250 kPa front and 475 kPa rear, or 350 kPa rear for 265/70R16LT. The track is 1,515 mm front and 1,420 mm rear on the narrow tyres, and 1,555 and 1,460 mm on 265/70R16 ([BBGJ1007, section 4](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)). Earlier cars ran 7.50R16 8-ply LT on steel wheels or 265/70R16 LT on alloys ([Toyota 2011 brochure](https://xr793.org/wp-content/uploads/2023/10/2011-Toyota-Land-Cruiser-70-Saver-AUS.pdf)).
- Toyota's alloy is 16 x 7, ET 0, on the 5 x 150 stud pattern ([genuine wheel listing](https://www.ebay.com.au/itm/155533183032)). Wheel nuts are M14 x 1.5 with a 21 mm hex, torqued to 209 Nm on steel wheels and 131 Nm on alloys ([70 Series Store](https://70seriesstore.com/blogs/information/recommended-79-series-wheel-nut-torque)).
- The factory tyres must go with the GVM kit. Lovells gives the factory load index as 115 and needs 117 and speed M (130 km/h) for 4,200 kg ([Lovells Campbellfield](https://www.lovellscampbellfield.com.au/_files/ugd/a7ab81_cd324b9c9e354c4da0d3ab9103620a6d.pdf), [Powercurve](https://www.powercurve.com.au/lovells-gvm-upgrade-sunshine-coast/toyota-landcruiser-lc79-series-gvm/)).
- NSW needs certification if the tyre diameter grows more than 7 % over the largest size on the placard or the speedometer is affected, if the rim or tyre is more than 25.4 mm wider than the largest factory size, or if the load rating falls below the placard ([VSI 06, items 15 to 17](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf)). Track may grow at most 50 mm beyond the factory maximum on an NA or NB vehicle, every wheel on an axle must match, and spacers are banned ([VSI 09](https://www.nsw.gov.au/sites/default/files/2021-02/RMS-Guideline-for-alternative-wheels-and-tyres-Vehicle-Standards-Information-No-9-November-2003.pdf)).
- NSW speed rule: a tyre's speed rating must equal or exceed the placard's. Only where the placard asks for more than 180 km/h may a lower rating be fitted, and then not below the vehicle's top speed (VSI 09). The kit's placard asks for M. The light-truck all-terrains below are rated R (170 km/h) or S (180 km/h) (report 09 tables), so the rule does not bind here, unlike on the Cayenne (report 07).

### 4.2 The ute's wheel and tyre

Wheel: ROH Trak 2 16 x 7, ET 0, 5 x 150, steel, rated 1,400 kg ([ROH Trak 2 table](https://roh.com.au/wheels/trak-2)). It is the size and offset of Toyota's alloy, so the track stays at Toyota's 1,555 and 1,460 mm and needs no certification. On a WorkMate it widens the track to those GXL figures, which is the factory maximum. The 4,200 kg kit's rear axle needs 1,275 kg a wheel, so the margin is 10 %. ROH publishes neither the weight nor the price. This plan uses 14.5 kg and AUD 230 (estimates). The same table lists other 5 x 150 Trak 2 sizes: 16 x 6 ET 0 at 1,250 kg, 16 x 8 ET 0 at 1,275 kg and 17 x 8 ET 0 at 1,275 kg.

Tyre: LT265/75R16 123/120, load range E, 1,550 kg at 80 psi. Two models on Australian lists: the Yokohama Geolandar A/T G015 123/120R (805 mm, 22.6 kg) and the Toyo Open Country A/T III 123/120R (804 mm), from report 09's tables. It is smaller than the 225/95R16C (834 mm by calculation), so it is inside the 7 % rule and the speedometer reads slightly high, which is legal. This assumes the bought ute's placard lists the 225/95R16C, as Toyota's guide does for both grades. Its 265 mm width matches the factory 265/70R16 option. Price: about AUD 420 a tyre (estimate). An Australian listing of the BFGoodrich KO3 265/75R16 119/116S shows four payments of AUD 96.25, about AUD 385 a tyre ([eBay](https://www.ebay.com.au/itm/176555722266)), and load range E costs more.

Pressures: use the maker's table at the weighed loads. By report 09's method (load in proportion to pressure to the power 0.585, from the 80 psi rating), the planned 1,215 kg per rear tyre needs about 53 psi (estimate). Keep the front at the placard's 250 kPa (36 psi) at least.

Alternatives considered:

- LT285/75R16 126/123, 1,700 kg, 834 mm by calculation. It equals the 225/95R16C's diameter, so it suits a 2017-on placard, but it is heavier and too tall for the trailer (section 4.3).
- LT245/75R16 120/116, 1,400 kg, 774 to 780 mm. It fits the trailer at 880 mm axle spacing, but costs the ute about 13 mm of axle clearance. It is the fall-back if the trailer must keep 880 mm.

Spares: two, on the same wheel and tyre, about 37 kg each (14.5 kg wheel estimate plus 22.6 kg tyre). Report 17 places them. Toyota sells an under-body tyre hanger with its tray ([Toyota 2021 brochure](https://xr793.com/wp-content/uploads/2023/10/2021-Toyota-LC70-AUS.pdf)).

### 4.3 Can the trailer share the ute's wheel and tyre? Yes

- The hub exists. Cruisemaster offers its LC5 M14 pattern (5 x 150 with M14 x 1.5 x 40 mm studs, 52 mm on discs) on its 12-inch drums and discs ([Cruisemaster stud sheet](https://cruisemaster.com.au/content/cis/StudPatterns.Infosheet.Rev.1.April23.pdf)).
- ABS stays. Every Cruisemaster electric drum build is now "ABS Compatible", with an ABS-ready arm, backing plate and drum, and the "ABS Enabled" package that connects to Bosch TSC is offered on 10 and 12-inch electric drums ([Cruisemaster ABS](https://cruisemaster.com.au/absenabled), [ABS hardware](https://cruisemaster.com.au/abs-enabled-hardware/)). Neither page ties ABS to a stud pattern. So the XT Freestyle Air keeps its 12-inch ABS-enabled A/T drums, drilled LC5 M14.
- Spigot: 110 mm, which Cruisemaster describes as the size "traditionally" used for the LandCruiser 200, 100 and 70 Series ([spigot sheet](https://www.diycaravans.com.au/wp-content/uploads/Spigotsize.Infosheet.Rev_.1.April23.pdf)). The wheel then centres on the trailer hub as it does on the ute.
- Offset: ET 0 meets Cruisemaster's rule of zero or positive offset. The effective chassis-to-face distance equals the chassis-to-face distance and must stay at or under 200 mm for the 4,500 kg XT Air tandem (report 09).
- Nuts: the trailer's M14 x 1.5 studs take the ute's nuts. Torque the steel wheel to Toyota's 209 Nm unless Cruisemaster's stud rating is lower, and then use the lower figure.

Load. A 3,000 kg trailer with 250 kg on the ball puts 2,750 kg on its axles. VSB1's 120 % rule for a tandem that does not share load (report 09) asks each wheel and tyre to carry 2,750 x 1.2 / 4 = 825 kg. The Trak 2 (1,400 kg) passes with 70 % in hand and the LT265/75R16 (1,550 kg) with 88 %. Even at a 3,500 kg ATM the need is 975 kg, still a pass.

Pressure. Each trailer tyre carries about 690 kg. By report 09's method the load-matched pressure is about 20 psi. That is very soft for a highway, so run about 26 to 30 psi on the highway (estimate) and use the maker's table. The large carcass leaves room to air down on sand and corrugations.

Axle spacing. The Cruisemaster XT takes tyres up to 804 mm at 880 mm axle spacing and needs at least 75 mm between the tyres (report 06). The LT265/75R16 is 804 to 805 mm, which leaves 75 to 76 mm before the tyre grows at speed. Set the trailer's axle spacing to 900 mm, which leaves about 95 mm. VSB1 allows a tandem that does not share load up to 1,000 mm (report 06). The fall-back is LT245/75R16 on both vehicles at 880 mm (section 4.2).

Floor height. By report 09's rule (floor surface = tyre diameter + 120 mm) a garage-type floor would rise to about 925 mm. The trailer loses its garage in the redesign, so the designer sets the floor from the new layout.

Spares. One wheel and tyre now serves both vehicles, so two spares cover the combination. Carry one under the ute's tray and one on the trailer. Both fit either vehicle. Moving the second spare off the ute takes about 45 kg off its rear axle (my arithmetic, 37 kg at 3,900 mm), which helps the limit in section 2.3. The axle table in section 2.3 keeps both on the ute, so it is the conservative case.

## 5. Towing set-up

### 5.1 Towbar

- Ratings: 3,500 kg braked and 350 kg on the ball (section 1).
- Choice: Hayman Reese Class 4 towbar 03186RW for the 79, 3,500 kg and 350 kg, with a 50 mm square receiver, AUD 1,160 at ARB plus AUD 160 to fit ([ARB](https://www.arb.com.au/product/t03186rw-hayman-reese-class-4-tow-bar-3500-350kg-rating-landcruiser-79-series)). The X-Bar 03237RW adds rated recovery points for AUD 1,799 plus AUD 400 to fit ([ARB](https://www.arb.com.au/product/t03237rw-x-bar-3500-350kg-tow-and-ball-rating-toyota-landcruiser-79-series)). The trailer's Cruisemaster DO35 coupling bolts to a tongue in the receiver (report 08).
- NSW needs no certification for a towbar certified by its maker and fitted to the vehicle maker's mounting points ([VSI 06, item 31](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf)).
- Toyota recommends a load distribution hitch when the trailer weighs more than half the GVM ([Toyota December 2025 brochure](https://cruiserarchive.com/wp-content/uploads/2025/12/70SeriesCurrentBrochure.pdf), towing notes). A 3,000 kg trailer is over that line. Report 08 chose the DO35 off-road coupling, and this research found no load distribution hitch made for it. Assumption: the combination runs without one, so the rear axle limit in section 2.3 stands.

### 5.2 Coupling height

No published receiver or ball height was found for the 79, laden or unladen. VSB1 asks for a towball height of 350 to 460 mm with the vehicle fully loaded (report 08). Estimate: the 250 kg download alone lowers the ball about 20 to 30 mm. That figure uses Toyota's factory spring rates, 42.2 N/mm per front coil and 47.9 to 104.2 N/mm per rear leaf pack ([BBGJ1007, section 4](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)), and the kit's springs are stiffer. The box and bikes lower it further.

Assumption until the ute is measured: set the tongue drop so the coupling point sits at 450 mm, plus or minus 20 mm, with the ute fully laden and the trailer level. That is report 08's target, inside VSB1's window. Measure the receiver pin height unladen, laden without the trailer, and laden with the trailer coupled.

### 5.3 Brake controller and plug

- Controller: REDARC Tow-Pro Elite V3, EBRH-ACCV3, AUD 469.04. It runs on 12 V or 24 V vehicles and gives up to 25 A at 12 V ([REDARC](https://www.redarcelectronics.com/au/tow-pro-elite)). No REDARC harness for the 79 was found, so use the Universal Tow-Pro Wiring Kit TPWKIT-013 (from AUD 255.99) and the universal remote-head mount TPSI-001 (AUD 19), both on the same page.
- Plug: a 12-pin flat socket to AS 4177.5, wired to VSB1's pin table, with the controller's output on pin 5, plus a separate 50 A Anderson-type connector for the trailer's Bosch TSC power and the battery charging feed (report 08).

### 5.4 Charging feed to the trailer battery

- The ute is 12 V: a 12 V, 64 Ah battery and a 1,560 W alternator ([BBGJ1007, section 4](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)). That is about 110 A at 14 V (my arithmetic).
- The trailer charges its 24 V battery through one Victron Orion-Tr Smart 12/24-15, which draws about 35 A from the ute (report 13). Run 6 B&S (13.5 mm²) twin cable from the ute's battery to an Anderson SB50 at the towbar, with a 50 A fuse at the battery. Toyota sizes a fuse at about 1.4 times the load, which gives 49 A.
- Voltage drop: about 13 m of cable there and back (estimate) at 35 A drops about 0.6 V (my arithmetic, copper at 0.0172 ohm mm²/m). The Orion accepts 8 to 17 V (report 13), so it works.
- A second Orion would draw 70 A, more than half of the alternator, and need 2 B&S (33.6 mm²) cable to keep the drop near 0.5 V. Keep one unless report 15 fits a larger alternator.
- Toyota's wiring rules for the run: fuse every added circuit, never add a load to an existing fuse, clamp wiring at about 200 mm intervals and battery cables at under 450 mm with rubber-lined clips, bend no tighter than ten times the cable diameter, and fit a grommet wherever a cable passes through metal (BBGJ1007, sections 8 and 11).

## 6. Dimensions and Toyota's mounting rules

### 6.1 Dimensions of the 2017 single cab chassis

From Toyota's Body Builder's Guide for the Australian VDJ79R-TJMRYQ3 and TJMNYQ3, its cab-and-chassis drawing and its frame drawing ([BBGJ1007, sections 3 and 4](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)), unless the row says otherwise.

| Dimension | Value | Note |
|---|---|---|
| Wheelbase | 3,180 mm | |
| Overall length, cab chassis | 5,220 mm (WorkMate), 5,230 mm (GXL) | |
| Front overhang, bumper to front axle | 850 mm (WorkMate), 860 mm (GXL) | 850 + 3,180 + 1,190 = 5,220 |
| Rear overhang, cab chassis as delivered | 1,190 mm | To its rearmost part |
| Frame length | 4,880 mm | Starts 625 mm ahead of the front axle, ends 1,075 mm behind the rear axle |
| Front axle to back of cab | 2,060 mm | My scaled check of Toyota's side view gives about 2,045 mm |
| Back of cab to rear axle | 1,120 mm | 3,180 less 2,060 |
| Frame behind the cab | 2,195 mm | 1,120 + 1,075 |
| Width across the rear frame | 1,046 mm and 1,090 mm on the drawing | Assumption: 1,046 mm over the rails and 1,090 mm over the mounting brackets. Measure |
| Rear spring hangers | 1,000 mm apart across the frame | Front hanger 689 mm ahead of the rear axle |
| Deck-mount stations | 879 and 490 mm ahead of the rear axle, 123, 490, 755 and 1,025 mm behind it | Toyota's "standard deck mounts". The rear cab mount is 1,952 mm behind the front axle |
| Overall width | 1,790 mm, or 1,870 mm with 265/70R16 and flares | |
| Overall height | 1,970 mm, or 1,955 mm with 265/70R16 | |
| Front track | 1,515 mm, or 1,555 mm with 265/70R16 | |
| Rear track | 1,420 mm, or 1,460 mm with 265/70R16 | 95 mm narrower than the front on both |
| Centre of gravity height, cab chassis | 700 mm | After body building, unladen, under 1,000 mm |
| Running clearance | 235 mm | [Toyota 2014](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf) and [2021](https://toyotamedia.b-cdn.net/files/2021/11/LC70_Spec_Data_Jun2021.pdf). The [2023 sheet](https://brookshire.com.au/BrooksHire/media/Media/Spec%20Sheets/LandCruiser-70-Spec-Sheet.pdf) lists 330 mm (WorkMate) and 316 mm (GX, GXL), apparently measured elsewhere |
| Approach and departure angles | 33 and 27 degrees | [Practical Motoring, 2017 79](https://practicalmotoring.com.au/4x4/2017-toyota-landcruiser-79-series-offroad-review/). Toyota Gambia lists 35 and 29 degrees for a 2.8 L single cab ([Toyota Gambia](https://www.toyota.gm/en/range/toyota-gambia-cfao-motors/land-cruiser-79)). The tray and towbar set the real departure angle |
| Wading depth | 700 mm | Practical Motoring, as above |
| Turning circle, kerb to kerb | 14.4 m | [Toyota 2021](https://toyotamedia.b-cdn.net/files/2021/11/LC70_Spec_Data_Jun2021.pdf) |

The narrow rear track is not limited to early cars. Toyota's sheets give the same 95 mm difference from 2011 to September 2023, and Lovells' 4,495 kg Elite of 2025 is sold to fix it ([Unsealed 4x4](https://unsealed4x4.com.au/lovells-elite-series-79-series-gvm-upgrade/)). The other fix, a rear-only wheel offset, is allowed up to 50 mm over the factory maximum track ([VSI 09](https://www.nsw.gov.au/sites/default/files/2021-02/RMS-Guideline-for-alternative-wheels-and-tyres-Vehicle-Standards-Information-No-9-November-2003.pdf)). It would break the single shared wheel, because the trailer needs zero or positive offset, so this plan keeps ET 0 all round and accepts the narrow rear track.

Tray sizes: no maker's tray data was captured in this research. A forum post says the 79's tray is about 100 mm longer than the 75 Series tray of 6 by 8 ft, 1,830 by 2,440 mm ([IH8MUD](https://forum.ih8mud.com/threads/what-make-of-ute-tray-is-this.1051531/)). Assumption: a single cab tray is 2,400 mm long and at most 1,850 mm wide (section 6.2), starting about 50 mm behind the cab. The forum figure suggests trays up to about 2,540 mm long, which would move the load centre in section 2.3 about 70 mm rearward.

### 6.2 Limits for the tray and the bike box

- Rear overhang: no more than 60 % of the wheelbase or 3.7 m, whichever is less, including any equipment ([ADR 43/04, clause 6.1.2.1](https://www.legislation.gov.au/F2006L01430/2025-01-30/2025-01-30/text/original/pdf)). For the 79 that is 1,908 mm behind the rear axle (my arithmetic). Toyota's guide also limits the rear overhang by body type, but its figures sit in a drawing that did not extract, so ADR 43's figure is used. A box starting 50 mm behind the cab could be up to 2,978 mm long within it (1,120 less 50, plus 1,908), before the axle loads in section 2.3 and the departure angle are counted.
- Width: no more than 2,500 mm for an NA or NB1 vehicle (ADR 43/04, clause 6.1.5.1). Toyota is stricter: a mounted part may stand at most 60 mm beyond the outermost point of the cab, mirrors excluded ([BBGJ1007, section 1-2](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf)). Assumption: the cab is 1,790 mm wide, the WorkMate's overall width, so the box may be up to 1,850 mm wide.
- Centre of gravity: after body building, the unladen vehicle's centre of gravity must stay under 1,000 mm, against 700 mm for the cab chassis. Mount heavy parts near the centre of gravity (BBGJ1007, section 1-2).
- Front axle share: Toyota sets a minimum share of the loaded weight on the front axle. The extracted figure reads 20 %, so that is the assumption. The planned build has 35 %.
- Balance: no difference in weight between the left and right wheels, no local load concentration on the frame, and all wheels on one plane without twisting the frame (BBGJ1007, section 1-2).
- Wheel arch space: the tyre's bump limit plus 25 mm vertically, 30 mm outside the tyre and 40 mm inside it (BBGJ1007, section 2-4).
- Exhaust: keep body parts 50 mm from the exhaust pipe and 150 mm from the muffler, or fit a heat shield (BBGJ1007, section 2-4).
- Weighing: weigh the finished ute with full fuel and all equipment, each axle separately, and check each against its rating (BBGJ1007, section 1-2).

### 6.3 Toyota's mounting rules

All from [BBGJ1007](https://jdmfsm.info/Auto/Japan/Toyota/Land%20Cruiser/70%20Series%20%281984-2007%29/2017%207x%20series%20Body%20Builder%27s%20Manual.pdf) unless noted.

- The frame must not be modified. A conversion uses the frame's standard deck mounts, at the stations in section 6.1 (section 2-2). So the box does not drill or weld the rails or their flanges.
- The front axle, steering and brake parts must not be welded, reinforced, machined or heated (section 1-3).
- The brake system and its pipes must not be modified, and the LSPV is reset after the work (section 2-5).
- Toyota tells body builders not to alter the front suspension (section 2-3). A GVM kit does exactly that, so its own approval and the NSW certificate cover it.
- No added or relocated fuel tank, and the tank stays 100 mm from the exhaust pipe and 200 mm from the muffler (section 2-9). Section 7 covers the NSW path for a larger tank.
- Flexible mounting: Toyota's own trays are bolted and designed to allow a set amount of flex. Toyota's testing found that the rigidity of a welded tray puts higher stress on the chassis, which can crack the tray or the chassis ([Toyota accessories brochure, 2016](https://xr793.com/wp-content/uploads/2023/10/2016-Toyota-Accessories-AUS.pdf)). The brochure describes Toyota's genuine trays in general, and this plan applies the rule to the 79. The bike box mounts so the chassis can twist under it: bolted to the deck mounts, never welded, with flexible elements. Report 17 designs the mount.

NSW rules for the body ([VSI 06](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf)):

- Item 25: a canopy on a ute with the original structure unaltered needs no certification.
- Item 27: replacing the body of a full-chassis vehicle like for like needs no certification.
- Items 28 and 29: reinforcing the chassis or changing the wheelbase needs certification.
- Item 34: body mountings other than the maker's need certification, unless they are optional mounts designed for that make and model that meet the maker's specification.

## 7. Long-range fuel tanks

The single cab holds 180 L from 2007 to 2016 and 130 L from 2017 ([Toyota 2011](https://xr793.org/wp-content/uploads/2023/10/2011-Toyota-Land-Cruiser-70-Saver-AUS.pdf), [2014](https://xr793.com/wp-content/uploads/2023/10/2014-Toyota-Land-Cruiser-70-Saver-AUS.pdf) and [2021](https://toyotamedia.b-cdn.net/files/2021/11/LC70_Spec_Data_Jun2021.pdf) sheets). At about 18 to 20 L/100 km while towing (estimate, against Toyota's 10.7 L/100 km test figure), 130 L gives about 650 to 700 km.

| Tank | Fits | Build | Price, fitting extra | Mass empty |
|---|---|---|---|---|
| ARB Frontier 180 L long-range tank, TAD106 | 79 Series | Polymer, 7 to 9 mm wall, "less than half the weight" of a comparable steel tank | AUD 1,557, fitting AUD 200 | About 15 kg (estimate) |
| The Long Ranger 180 L heavy-duty replacement, TR58WDCHD | 79 single and dual cab, 76 wagon | 2 mm aluminised steel | AUD 2,272, fitting AUD 480 | About 35 kg (estimate) |
| The Long Ranger 110 L auxiliary, TA87 | 79 Series | Steel (assumption) | AUD 2,853 | Not published |
| The Long Ranger 160 L, TR58U | 70 and 79 single cab chassis | 2 mm aluminised steel | Not captured | Not published |

Sources: ARB product pages for [TAD106](https://www.arb.com.au/product/tad106-arb-frontier-long-range-fuel-tank-180l-toyota-landcruiser-79-series), [TR58WDCHD](https://www.arb.com.au/product/tr58wdchd-the-long-ranger-180l-heavy-duty-fuel-tank-landcruiser-76-79-series), [TA87](https://www.arb.com.au/product/ta87-the-long-ranger-110l-auxiliary-diesel-fuel-tank-toyota-landcruiser-79-series) and [TR58U](https://www.arb.com.au/product/tr58u-the-long-ranger-160l-diesel-fuel-tank-landcruiser-70-79-single-cab-chassis). The build years each tank fits did not come through in the page text. Assumption: TAD106 and TR58WDCHD fit the 2017 to 2022 single cab, since both name the 79 cab chassis without excluding it.

Mass. Diesel weighs about 0.835 kg/L, so 50 L more is about 42 kg and a full 180 L about 150 kg. Assumption: the tank sits between the rails ahead of the rear axle, about 2,500 mm behind the front axle, so about 79 % of any added mass lands on the rear axle. A full 180 L Frontier then adds about 33 kg of fuel to the rear axle, plus a few kilograms of tank, against the 121 kg margin in section 2.3.

NSW. A tank of a different capacity, or one on new mounting points, needs certification. A same-capacity replacement on the original mounts does not ([VSI 06, item 50](https://www.nsw.gov.au/sites/default/files/noindex/2026-03/vsi-06-light-vehicle-modification-july-2026.pdf)). Toyota's guide says not to add or relocate a tank (section 6.3), so the certifier relies on the tank maker's compliance data (assumption).

Decision: optional. If a trip needs more than about 650 km between fuel stops, fit the ARB Frontier 180 L. It is the lightest and cheapest of the four, takes the factory tank's place (assumption) and goes through the same NSW inspection as the GVM kit. Otherwise carry spare fuel in jerry cans on the trailer, over its axles, where it barely changes the towball load.

## Open questions

1. What do the bought ute's axles weigh, with its tray, bar and spares? Assumption: Toyota's mid-range kerb loads of 1,280 kg front and 913 kg rear plus the estimates in section 2.3, giving 1,324 and 2,429 kg for the planned build.
2. How far behind the rear axle is the ball? Assumption: 1,300 mm, so each kilogram on the ball adds 1.41 kg to the rear axle.
3. Will the NSW certifier accept Lovells' 7,400 kg GCM after registration? Assumption: not needed. The plan uses Toyota's 6,900 kg.
4. What do Lovells' authorised fitting and the VSCCS inspection cost? Assumption: AUD 1,500 each, the inspection inside 70 Series Store's AUD 1,000 to 2,500 range.
5. Does the 4,200 kg kit need any brake change on a 2017 to 2022 single cab? Assumption: none beyond the LSPV reset, because the kit lists no brake parts.
6. What do the ROH Trak 2 16 x 7 ET 0 5 x 150 weigh and cost, and which nut seat do they take? Assumption: 14.5 kg, AUD 230, and Toyota's M14 x 1.5 steel-wheel nuts.
7. What does an LT265/75R16 123/120 E tyre cost? Assumption: AUD 420, fitted and balanced for AUD 35 more.
8. Will Cruisemaster build the XT at 900 mm axle spacing? Assumption: yes. Spacing is set by the crossmember positions, and VSB1 allows up to 1,000 mm.
9. Is the LC5 M14 hub with a 110 mm spigot stocked on the 12-inch ABS-enabled drum? Assumption: yes, because every Cruisemaster electric drum is now ABS Compatible and LC5 M14 is a standard 12-inch drum pattern.
10. How high is the receiver, unladen and laden? Assumption: a drop tongue sets the coupling point at 450 mm, plus or minus 20 mm, with the ute laden.
11. How wide is the frame over the rails? Assumption: 1,046 mm, with 1,090 mm over the mounting brackets.
12. How wide is the cab at its outermost point? Assumption: 1,790 mm, so the box may be 1,850 mm wide.
13. What are Toyota's rear overhang figures by body type? Assumption: ADR 43's 1,908 mm behind the rear axle.
14. What minimum front-axle share does Toyota set? Assumption: 20 %, as the extracted text reads.
15. Which build years do the ARB Frontier 180 L and Long Ranger 180 L tanks fit, and what do they weigh? Assumption: both fit 2017 to 2022, at about 15 kg and 35 kg empty.
16. What do Bendix Ultimate 4WD front pads cost for the VDJ79? Assumption: AUD 150.
17. Is the 2007 to 2016 front axle rated 1,460 or 1,480 kg? Assumption: 1,460 kg. It does not matter if the bought ute is a 2017 or later car.

## What I could not verify

- The engineering behind the September 2022 update beyond the GVM and the emergency braking. Drive could not confirm any suspension or brake change.
- The placard's tyre speed rating, and the factory 7.50R16's load index. Lovells' figure of LI 115 for the factory tyre is used instead.
- Kits from Ironman 4x4, Pedders and Tough Dog for the 79 single cab. No product page was found. Outback Armour's brochure page refused the request, so only its title (3,800 kg, J7 single cab) is used.
- The Fulcrum price page refused direct requests. Its AUD 5,620 price comes from a 2024 search result.
- Two figures on Toyota's cab-and-chassis drawing, 2,725 mm and 1,380 mm. Their reference points are unclear, so they are not used.
- Tray makers' sizes and masses for the single cab.
- Approach and departure angles for the single cab itself. The 33 and 27 degree figures come from a 2017 79 review that also quotes the dual cab's 3,300 kg GVM, and the 35 and 29 degree figures from an African 2.8 L.
- The text of VSB 14 Sections G (brakes) and S (load capacity). The NSW triggers come from TfNSW's VSI 06 and VSI 09 instead.
- A published towball or receiver height for the 79.
- Toyota's own axle split at the 3,510 kg GVM for 2022-on cars.
- Retail prices in Australia for the tyres and the ROH wheels.

# 05 Bike geometry for envelope models

Both bikes' side views are measured from official maker images, scaled by the published wheelbase. Widths at peg height are not measured for either bike (see Open questions).

## Summary

- **Tuareg 660 Rally.** I used the 2025-on Tuareg Rally (Euro 5+): the Aprilia owner's manual that covers the Tuareg 660 and Tuareg 660 Rally ([Scribd copy, manual 2Q000581](https://www.scribd.com/document/884477164/Aprilia-tuareg-660-Rally-e5-en)), the Aprilia Rally spec sheet ([2026 brochure PDF](https://library.rvusa.com/brochure/2026-Aprilia-Tuareg-Rally-660-brochure.pdf)) and Aprilia's Rally brochure image ([Aprilia Argentina PDF](https://www.apriliaoficial.com.ar/2025/wp-content/uploads/2025/10/ficha_tuareg_rally_comprimida.pdf), page 4).
- **The Tuareg's highest points are its mirrors, not the screen.** The manual gives the Rally a maximum height of 1,445 mm. In Aprilia's image the mirror heads reach at least 1,440 mm (the image is cropped at that height) and the screen top sits at about 1,390 mm. The owner's 1,370 mm is close to the screen. **Remove the mirrors or fold them down for transport, or design the platform to clear 1,445 mm.**
- **The Tuareg may be longer than 2,220 mm.** In the image, the number plate hanger reaches at least 1,915 mm behind the front axle, so the length including the hanger is at least about 2,263 mm. The published 2,220 mm (and the owner's figure) would put the rear-most point at 1,872 mm. The bikes stand across a 2,330 mm interior, so this needs a tape measure.
- **Street Triple.** The owner's figures (2,055 x 792 x 1,064 mm) match the 2023-on Street Triple 765 RS. I measured Triumph's official MY25 RS images. My figures come within 3-6 mm of the published height without mirrors (1,064), the seat height (836) and the length (2,052). With mirrors it stands 1,178 mm. Without the number plate hanger, the length falls to about 2,018 mm.
- Ground clearance: Street Triple 144 mm (belly pan), Tuareg about 244 mm (skid plate).

## Coordinate frame (both bikes)

Origin on the ground directly below the front axle. x is positive towards the rear, y is positive to the bike's left, and z is up. The bike is upright on level ground, unladen, with no rider, at the ride height shown in the maker's studio image. Units are mm.

## Owner figures against published and measured figures

| Bike | Item | Owner (governs) | Published | Measured from image | Flag |
|---|---|---|---|---|---|
| Tuareg 660 Rally | Length | 2,220 | 2,220, both variants ([manual](https://www.scribd.com/document/884477164/Aprilia-tuareg-660-Rally-e5-en) p.114) | at least 2,263 with the plate hanger (image cropped) | **Measure. Possibly 40+ mm longer.** |
| Tuareg 660 Rally | Width | 965 | 935 Rally, 965 standard (manual p.114) | not measured | Owner used the standard figure, or has wider bars or guards. 965 is the safe value. |
| Tuareg 660 Rally | Height | 1,370 | 1,445 Rally, 1,425 standard, "at top fairing" (manual p.114) | mirrors at least 1,440; screen about 1,390 | **Mirrors set the height.** The owner's figure is about the screen. |
| Tuareg 660 Rally | Mass | 206 kg fuelled | 199 kg kerb Rally, 204 standard (manual p.114) | | Owner is 7 kg over the spec, so accessories are likely |
| Street Triple 765 | Length | 2,055 | 2,052, 2023-26 RS ([moto.it](https://www.moto.it/listino/triumph/street-triple/street-triple-765-rs-2023-26/p7frAe)) | 2,056 with hanger, 2,018 without | Matches |
| Street Triple 765 | Width | 792 | 792 across the bars, 2023-on ([Triumph AU](https://www.triumphmotorcycles.com.au/motorcycles/roadsters/street-triple-765/specification)) | | Matches 2023-on. Earlier years are narrower. |
| Street Triple 765 | Height | 1,064 | 1,064 without mirrors RS, 1,047 R (Triumph) | 1,067 without, 1,178 with mirrors | Matches without mirrors |
| Street Triple 765 | Mass | 175 kg fuelled | 188 kg wet RS (Triumph) | | Plausible for a stripped bike |

## Photo measurement method

- **Street Triple.** I used Triumph's MY25 RS studio renders, 1920 x 1080 px: the [right side](https://media.triumphmotorcycles.co.uk/image/upload/sitecoremedialibrary/media-library/images/motorcycles/roadsters-supersports/my25/my25%20colours/street%20triple%20765%20rs/web/1080/street%20triple%20rs_my25_phantom%20black_rhs_1080px.jpeg) and the [left side](https://media.triumphmotorcycles.co.uk/image/upload/sitecoremedialibrary/media-library/images/motorcycles/roadsters-supersports/my25/my25%20colours/street%20triple%20765%20rs/web/1080/street%20triple%20rs_my25_phantom%20black_lhs_1080px.jpeg). Least-squares circle fits to the tyre outlines have a residual of 0.3-0.8 px. The axle centres are 751.4 px apart on both sides, so the 1,399 mm wheelbase gives 1.862 mm/px. The tyre diameters give 1.858 and 1.837 mm/px. The length, the height without mirrors and the seat all agree with published figures within 6 mm. Uncertainty is +/-1.5% +/-4 mm on the centre plane, and +/-15 mm for the bar ends and mirrors, which sit 300-400 mm off the centre plane.
- **Tuareg.** I used Aprilia's Rally brochure image (page 4 of the Argentina PDF above), a right side view, 1372 x 860 px, on a black background. RANSAC and least-squares fits to the gold rims put the axle centres 917.9 px apart, so the 1,525 mm wheelbase gives 1.661 mm/px. The fitted rim flange diameters are 550 and 474 mm, which fits 21 and 18 inch rims (bead seats 533 and 457 mm, plus the flanges). The ground line comes from the calculated tyre radii, and the front and rear agree within 3 mm. The image is cropped at the top (z 1,440) and at the rear. Black parts on the black background reduce edge accuracy. Uncertainty is +/-2% +/-8 mm on the centre plane and +/-20 mm off it.

## Aprilia Tuareg 660 Rally (2025-on)

### Published data

| Item | Value | Source | Confidence |
|---|---|---|---|
| Wheelbase | 1,525 mm | Manual p.114; [Aprilia 2024 Tuareg spec](https://wlassets.aprilia.com/wlassets/aprilia/rs/tech_spec/2024/Tuareg660/original/Tuareg660.pdf) | high |
| Max length | 2,220 mm | Manual p.114 | high (but see measured hanger) |
| Max width at handlebar | 935 mm Rally, 965 mm standard | Manual p.114 | high |
| Max height "at top fairing" | 1,445 mm Rally, 1,425 mm standard | Manual p.114 | high |
| Seat height | 913 mm Rally (Aprilia); 880 mm ([1000PS](https://www.1000ps.com/de-at/modell/12747/aprilia-tuareg-660-rally/2025)); standard 860 mm | [Rally spec](https://library.rvusa.com/brochure/2026-Aprilia-Tuareg-Rally-660-brochure.pdf) | medium (the image shows 860-885) |
| Rake / trail | 26.7 deg / 113.3 mm | Manual p.116; 2024 spec | high |
| Wheel travel | 240 mm front and rear | Manual p.116; Rally spec | high |
| Rear shock | 106.5 mm stroke, 399.5 mm eye to eye | Manual p.116, p.71 | high |
| Kerb weight | 199 kg Rally | Manual p.114 | high |
| Ground clearance | not published | | measured 244 mm |

Fork travel is measured along the fork axis. The vertical drop at the axle is about 240 x cos(26.7 deg) = 214 mm.

### Tyres

| | Size (manual) | Overall diameter (calculated) | Width (nominal) | Rim |
|---|---|---|---|---|
| Front | 90/90-21 M/C 54V | 21 x 25.4 + 2 x 0.90 x 90 = **695 mm** | 90 mm | 1.85 x 21 tube type (Aprilia spec; the manual says 2.15 x 21) |
| Rear | 150/70 R18 M/C 70V | 18 x 25.4 + 2 x 0.70 x 150 = **667 mm** | 150 mm | 4.00 x 18 tube type |

Stock tyres are Pirelli Scorpion Rally STR ([ADV Pulse](https://www.advpulse.com/adv-news/aprilia-tuareg-660-rally-review/), [Motorrad](https://www.motorradonline.de/enduro/mit-der-neuen-aprilia-tuareg-rally-im-gelaende-erster-fahr-test/)). Dirt Bike's test bike had Michelin Anakee Wild ([Dirt Bike](https://dirtbikemagazine.com/aprilia-tuareg-660-rally-edition-review/)). Real knobby diameters can be 5-10 mm over nominal.

### Positions in the bike frame (right-side image)

| Point | x | z | Confidence |
|---|---|---|---|
| Front axle | 0 | 348 | medium (tyre radius) |
| Rear axle | 1,525 | 334 | medium |
| Front tyre leading edge (front-most point) | -348 | 348 | medium |
| High front mudguard tip | -156 | 775 | medium |
| Headlight fairing front | 85 | 950 to 1,010 | medium |
| Lower triple clamp (hidden behind panels) | about 270 | about 860 | low (+/-30) |
| Screen top | 250 | 1,390 | medium (+/-15) |
| Handguard front tip | 385 | 1,215 | low (+/-20) |
| Bar end / handguard outer rear end, y = +/-483 (owner) or +/-468 (manual) | 585 | 1,190 | medium (+/-20) |
| Mirror heads | 533 to 616 | 1,290 to at least 1,440 (manual max 1,445) | medium |
| Tank top | 640 | 1,095 | medium |
| Seat low point | 1,000 to 1,065 | 860 to 885 | medium |
| Rider footpeg | 955 | 360 | low (+/-35) |
| Pillion peg hanger | 1,205 | 505 | low |
| Tail and rack top | 1,450 to 1,800 | 920 to 940 | medium |
| Tail light tip | 1,854 | 895 | medium |
| Rear tyre trailing edge | 1,859 (calculated), 1,851 (measured) | 334 | medium |
| Number plate hanger, rear-most | at least 1,915 (image cropped) | about 645 | low |
| Lowest point: skid plate | 600 to 800 | 244 | medium (+/-10) |
| SC-Project silencer (right side) | 1,380 to 1,780 | 510 to 800 | medium |
| Side stand (left, "Rally sidestand") | TODO | TODO | |

## Triumph Street Triple 765 (2023-on RS geometry)

### Published data, current model

| Item | 765 RS | 765 R | Source |
|---|---|---|---|
| Wheelbase | 1,399 mm | 1,402 mm | [Triumph AU](https://www.triumphmotorcycles.com.au/motorcycles/roadsters/street-triple-765/specification), [Triumph US](https://www.triumphmotorcycles.com/motorcycles/roadsters/street-triple-765/specification) |
| Rake / trail | 23.2 deg / 96.9 mm | 23.7 deg / 97.8 mm | same |
| Seat height | 836 mm | 826 mm | same |
| Width across handlebars | 792 mm | 792 mm | same |
| Height without mirrors | 1,064 mm | 1,047 mm | same |
| Length | 2,052 mm | not checked | [moto.it](https://www.moto.it/listino/triumph/street-triple/street-triple-765-rs-2023-26/p7frAe) |
| Travel front / rear | 115 / 131.2 mm | 115 / 133.5 mm | Triumph |
| Wet weight | 188 kg | 189 kg | Triumph |

### Year differences

| Item | 2017-19 RS | 2020-22 RS | 2023-on RS |
|---|---|---|---|
| Wheelbase | 1,410 ([moto.it](https://www.moto.it/listino/triumph/street-triple/street-triple-rs-2017-19/GdkJpQ)) | 1,405 ([BikeSocial](https://www.bennetts.co.uk/bikesocial/reviews/bikes/triumph/triumph-street-triple-rs-2020-review-price-spec)) | 1,399 |
| Rake / trail | not checked | 23.9 deg / 100 mm ([Triumph handbook 3850186-US](https://static-cdn.cars24.com/prod/new-bike-cms/Triumph/Street-Triple-R/2025/01/01/9247318d-e61e-41be-8606-e1fd232af342-Triumph_Street-Triple-R_Brochure.pdf) p.216) | 23.2 deg / 96.9 mm |
| Seat height | 825 | 825 | 836 |
| Width at bars | 735 (moto.it, low confidence) | 775 ([philharmonicmoto](https://philharmonicmoto.com/product/triumph-street-triple-rs-2020-2022/)) | 792 |
| Height without mirrors | 1,085 | 1,085 | 1,064 |
| Length | 2,065 | about 2,055 (estimate) | 2,052 |

An earlier bike is up to 21 mm taller and up to 57 mm narrower at the bars. Its wheelbase is 6-11 mm longer.

### Tyres

| | Size | Overall diameter (calculated) | Measured | Width (nominal) | Rim |
|---|---|---|---|---|---|
| Front | 120/70 ZR17 | 17 x 25.4 + 2 x 0.70 x 120 = **600 mm** | 601 mm | 120 mm | 17 x 3.5 |
| Rear | 180/55 ZR17 | 17 x 25.4 + 2 x 0.55 x 180 = **630 mm** | 638 mm | 180 mm | 17 x 5.5 |

### Positions in the bike frame

| Point | x | z | Confidence |
|---|---|---|---|
| Front axle | 0 | 300 | high |
| Rear axle | 1,399 | 320 | high |
| Front tyre leading edge (front-most point) | -300 | 300 | high |
| Headlight front | -31 | 802 | medium |
| Lower triple clamp at the fork leg | 157 | 690 | medium (+/-15) |
| Top yoke | 255 | 942 | medium (+/-15) |
| Handlebar riser / clamp | about 292 | about 979 | medium |
| Bar end, y = +/-396 | 428 | 1,013 | medium (+/-15) |
| Mirror heads (if fitted) | 292 to 376 | 1,078 to 1,178 | medium |
| Top without mirrors (front brake reservoir, right side) | about 300 | 1,067 | medium |
| Tank top | 656 | 1,007 | medium |
| Seat low point | 880 to 950 | 830 | medium |
| Swingarm pivot | 819 | 408 | medium |
| Rider footpeg (see note) | 970 | 350 | low (+/-35) |
| Pillion peg pivot | 1,233 | 564 | medium |
| Tail top | 1,290 to 1,330 | 975 | medium |
| Tail light tip | 1,564 | 960 | medium |
| Rear tyre trailing edge | 1,718 | 320 | high |
| Number plate hanger, rear-most | 1,756 | 585 to 635 | medium |
| Lowest point: belly pan and sump | 320 to 640 | 144 | medium (+/-6) |
| Silencer underside | 750 to 920 | 156 | medium |
| Side stand pivot (left, folded) | 764 | 272 | medium |
| Side stand foot (folded) | 1,027 | 253 | medium |

Overhangs: 300 mm ahead of the front axle, and 357 mm behind the rear axle with the hanger fitted (319 mm without it).

Footpeg note: the pegs are seen end-on. Round parts on both sides sit at x 969, z 346 (the lever pivot) and at x 1,024, z 384 (a hanger cap), and the peg is at or between them.

Side stand: the deployed foot lands about 260-300 mm from the pivot, on the left. Its ground position is not measured.

Mirrors: stalk mirrors on the bar clamps, with heads near the bar ends laterally. Width with mirrors is not published. For the track case, use 1,064 mm high and 792 mm wide.

## Suspension and strapping

- Aprilia's manual (p.109) says to transport the bike upright, securely anchored, in first gear, with the tank emptied and dry. Fuelled transport needs the engineer's view and garage ventilation.
- Common practice, with no source fetched in this run, is to compress the fork about one third of its travel and never to the stops. That is about 70-80 mm on the Tuareg and 35-40 mm on the Street Triple. Size the platform clearance to the free, unladen height, because the bikes roll in at free height and straps can slacken.

## Tie-down points

| Bike | Point | Approx x, z | Notes |
|---|---|---|---|
| Street Triple | Fork legs below the bottom yoke (soft loops) | 157, 650-690 | Main front point |
| Street Triple | Handlebar beside the risers, inboard of the controls | 290-330, 980-1,000 | Tubular bar on risers |
| Street Triple | Pillion peg hangers | about 1,233, 564 | Often removed on track bikes |
| Street Triple | Swingarm near the axle, or paddock stand bobbins | 1,250-1,350, 330-360 | Bobbin thread size not verified |
| Tuareg | Fork legs below the bottom yoke, above the high mudguard | about 270, 780-850 | Check loops clear the mudguard and brake lines |
| Tuareg | Handlebar inboard of the handguards and controls | 450-520, about 1,150 | Tapered bar; do not load the handguards |
| Tuareg | Pillion peg hangers | about 1,205, 505 | Bolted to the frame |
| Tuareg | Rear frame, rack or grab rail under the tail | 1,450-1,700, 880-920 | Check for a rack on the owner's bike |
| Tuareg | Swingarm near the axle (soft loops) | 1,350-1,450, 330-380 | |

## Centre of mass

No maker publishes it. These are low-confidence class estimates with no fetched source:

- Street Triple: z 520 +/-60 mm, x 690 +/-50 mm.
- Tuareg: z 600 +/-70 mm, x 760 +/-60 mm. Dirt Bike says the Tuareg carries its fuel low ([Dirt Bike](https://dirtbikemagazine.com/aprilia-tuareg-660-rally-edition-review/)).

To measure them, weigh each wheel, which gives x. Then raise the front wheel by 300-400 mm and weigh again, which gives z.

## Open questions

1. Tuareg: measure the mirror top, the screen top and the overall length including the plate hanger. Decide whether the mirrors come off for transport.
2. Tuareg width: 965 mm (owner) or 935 mm (manual, Rally)?
3. Peg tip-to-tip width and the widest point at peg height for both bikes. These need a tape measure or a front-view photo; neither was measured.
4. Street Triple model year, and whether the hanger and mirrors stay off for transport.
5. Both side stands' deployed foot positions, and the Tuareg's lower triple clamp height.

## Could not verify

- aprilia.com model pages return Access Denied to automated fetches. I used Aprilia PDFs, the manual and the brochure image instead.
- manualslib.com is blocked from this network.
- Strap compression practice and the CoM estimates have no fetched source.
- Street Triple 2017-19 rake and trail are not checked. The 2017-19 width (735 mm) comes from one third-party site.
- Every other link in this report was fetched during the research and worked.

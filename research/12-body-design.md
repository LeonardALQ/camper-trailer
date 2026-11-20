# 12: Body design basis

Note added 20 Nov 2026, after the trailer was redesigned for the LandCruiser 79 (TRAILER.md revision H, BODY.md revision B). The bikes ride in the ute's bike box now, so the body has no garage. It is 4,420 mm long, not 5,500 mm, and its roof is fixed: report 12's 40 mm lid panel bonded into a roof-to-wall joiner on walls 150 mm taller, 1,950 mm inside. So the raising roof of section 6, the rear garage door and the rear portal of section 5 are not used, and the rear wall is a full panel with one window that closes the box's rear end. The panels, joints, extrusions and the opening rules are kept. The floor no longer carries bike wheels, chocks or L-track anchors, so a person's foot governs it. The body mounts are M12 bolts into welded nut plates, report 12's fallback, on 32 mounts. The HB10 would now pass at 0.87 of its safe load, with less margin. There are no roof hatches, because the full Sunman array covers the roof. The data for this report is published as `research/12-body-panels.yaml` and `research/12-body-products.yaml`.

Note added 20 Nov 2026, after the body design (BODY.md). The design follows this report with these changes. There is no LPG (report 13, an owner option), so the gas locker hatch (BD-06) goes, and the lid's top skin stays flat with no hatch under the 4,108 x 2,168 mm bonded solar array: the Midi Heki and the Mini Heki move to the lid's ends and the bathroom vent to the road-side wall. The lifted mass is 164 kg. The twist sharing was checked in the frame model with the body as a torsion box on mount posts at every station. With the latched lid carrying no shear the body removes 82 % of the LC5a chassis twist (0.437 to 0.077 degree), and 98 % if the lid carries shear, so the claim of about 80 % holds. The forces it puts in the mounts are larger than section 4 estimates: up to 13 kN under LC5a and 19 kN under LC5b, against 4.2 kN. The Lindapter HB10 does not pass, so the mounts use this report's fallback, M12 8.8 bolts into 10 mm nut plates welded inside the raisers and outrigger tips (CH-P14). The aluminium rear portal on pinned feet racks about 50 mm and is over-stressed under the body's share of LC5b, so the portal is hot-dip galvanised steel SHS 50 x 50 x 5 and 40 x 40 x 5 with fixed feet, 33 kg in place of 10 kg. The kitchen opening moves 150 mm off the front corner and the entry door sits 300 mm behind it, as section 5's rules ask. The L-track hardpoint strips pass at the 20 kN anchor load (a factor of 1.59 on ultimate), so the rows stay between the stations. The data for this report is published as `research/12-body-panels.yaml` and `research/12-body-products.yaml`.

Status: research for the body design, 20 Nov 2026. Positions are in the project datum DIM-01, masses in kg. "Maker" means a published figure, "calculated" means worked out from a maker's data in the planning scripts, and "estimate" means a judgement with no maker figure. A sandwich panel is two thin skins bonded to a light core. D is its bending stiffness per metre width and S its shear stiffness. Wrinkling is a local buckle of a compressed skin into the core.

## Recommendation

**Panels.**

- Floor: 30 mm, two 2.0 mm woven roving polyester skins (48 % glass, the Lamilux Woven Roving 48 % Plus type) on 26 mm Divinycell H80 PVC foam. 8.9 kg/m2 (calculated). D is 11.0 kNm2/m. A 100 kg bike wheel midway between the raisers, 1,236 mm apart, deflects the floor 4.6 mm (span/269). Recycled PET at 100 kg/m3 is the alternative core, at 9.4 kg/m2.
- Side and rear walls: 35 mm, two 1.5 mm gelcoat GRP skins (Optiplan Polydet, the German skin type Creative Composites uses) on 32 mm XPS foam. 6.0 kg/m2, scaled from Creative Composites' 5.8 kg/m2 for its 29 mm panel. The front wall has a 2.0 mm outer skin against stones, 6.7 kg/m2.
- Raising roof lid: 40 mm, a 2.0 mm top skin and a 1.5 mm bottom skin on XPS of about 36 kg/m3. 7.0 kg/m2 (calculated).
- Inserts: high-density PVC or pultruded GRP strips laid into the core along every fixing line, as Creative Composites and DIY Caravans build them. Every strap anchor and every body mount bolt passes through a strip and a crush tube.

**Joints and the box round the openings.** Every panel edge is bonded into an aluminium extrusion with an MS polymer or PU adhesive: floor joiners, corner joiners and the pop-top bottom and top rings. An aluminium SHS 50 x 50 x 3 portal frames the rear garage opening: a header under the bed deck, two jambs and a post at the gas locker. It is bonded and riveted to the wall skins and its feet bolt through the floor to the rear crossmember. The portal and the 380 mm kerb-side pier keep the rear wall square (3.6 mm of racking and 18 MPa in the SHS in the twist case, calculated). Keep at least 300 mm of full wall between neighbouring openings in the kerb-side wall (assumption).

**Mounting.** Bolt the floor through the 50 x 21 mm EPDM-faced bearer strip into every raiser and every outrigger tip: 36 M10 bolts at the nine stations, as Lindapter Hollo-Bolt HB10 blind bolts (safe working load 8.5 kN in tension and 10 kN in shear). Do not bond the body to the chassis. The bonded body is 8 to 12 times stiffer in torsion than the chassis, so it takes about 80 % of the LC5a twist torque (10.7 kNm) and the chassis twist falls from 0.48 to about 0.10 degree. That torque puts about 0.5 MPa of shear in the wall skins. A torsion-free subframe would add a frame under the floor and raise the trailer, and a chassis this stiff does not need one.

**Roof.** A hard lid on canvas walls, raised level by four 12 V electric linear actuators (LINAK LA36 class) in the corners, with an 825 mm lift. That gives 900 mm of sitting room over the mattress, keeps the roof-down ceiling at 1,800 mm and the travel height at 2,762 mm. Six over-centre latches with secondary catches hold the lid down for travel.

**Doors and windows.** Entry: Aussie Traveller DC door, 1,623 x 622 mm, left hinged. Gas locker: Aussie Traveller service door, 650 x 650 mm. Garage: the rear wall cut-out in an aluminium frame on a piano hinge, with two gas struts and four Southco E3 compression latches. Windows: Dometic S4. Roof hatches: a Midi Heki over the living area and a Mini Heki Style over the bed. A Carafan Sahara CP700 fan pressurises the living area against dust.

**Mass.** The body comes to 741 kg against the brief's 654 kg (+87 kg), and 829 kg with the growth allowance. The floor, the raising roof and the extrusions carry most of the rise. Section 10 has every line.

## 1. Requirements

### 1.1 VSB1 Revision 6

Source: [VSB1 Rev 6, September 2024](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf).

| Clause | Requirement | What it means for the body |
|---|---|---|
| 5.2 Width | 2,500 mm at most, measured across the body, including mudguards, side-mounted spare wheels, racks and awnings. Lamps required for compliance are excluded | The 2,400 mm body and a 100 mm awning reach 2,500 mm. Nothing else on either side may stand proud of the line through the awning face and the opposite wall, so window frames, handles and latches stay inside it |
| 5.3 Height | 4,300 mm at most, including roof-mounted items | 2,762 mm travel height, roof down. The raised roof is a parked condition |
| 10.1, 10.2 Mudguards | Every wheel guarded. The body structure, covers and mud flaps may form the guard. It covers the full tyre width | The floor over the tyres is the guard |
| 10.2.2 Length | GTM up to 3,500 kg may use either approach. With one guard over a tandem, its rear must meet approach 2 for the rear wheel: down to 230 mm above the road, or 300 mm on off-road vehicles, and a mud flap may form it | Mud flaps behind the rear tyres hang to Z 300 or lower, so about 540 mm below the floor underside (Z 842) |
| 13.1.4 Projections | No pointed or sharp exterior or interior fittings | Radiused latch handles, hatch corners and trim ends |
| 13.2.1 Doors | Only outward-opening or sliding doors. At least one door on the left side or the rear gives direct entry and exit, with nothing in the way | The kerb-side entry door meets it. The top-hinged garage door opens outward |
| 13.2.2 Fire extinguishers | At least one, to AS 2444. Multi-compartment caravans carry two of 1A:5B or more. A fire blanket is recommended with cooking appliances. Smoke alarms are recommended and some states require them | Partition A makes this a two-compartment body, so two extinguishers |
| 13.2.4 LPG | LPG installations follow the caravan LPG code and AS/NZS 5601 | Section 1.3 |
| Body attachment | VSB1 has no clause on fixing the body to the chassis. Chapter 14 only says the body is restrained during the drawbar test | Nothing applies. Report 02 FAIL-03 is the project rule |
| Glazing | VSB1 has no glazing clause | See ADR 8 below |

### 1.2 ADRs

- [ADR 42/05](https://www.legislation.gov.au/F2018L01514/2025-12-06/2025-12-06/text/original/pdf) applies to trailers TA to TD built as new models from 1 July 2019 (clause 3). Clauses that touch the body: 12 (no sharp interior fittings), 15.1 (at least half the windows open, or other ventilation), 21 (wiring insulated, clear of moving parts and fuel, protected from chafe, supported at 600 mm or less, grommets in metal holes) and 25 (toilet never discharges on the road and vents outside, basins do not drain into the toilet tank). Its Table 4 also calls up ADR 92 and ADR 95 for trailers.
- [ADR 92/00](https://www.legislation.gov.au/F2018L01520/latest) clause 5.1 bars exterior fittings that are likely to increase injury. Its UN R26 appendix applies only to categories MA, MB and MC, so for a trailer only clause 5.1 applies. Use R26 as the guide: no protruding part with a radius under 2.5 mm, door handles at most 40 mm proud and hinges 30 mm, and outward-opening windows with no forward-facing edge. R26 exempts parts more than 2 m above the ground.
- [ADR 8/01](https://www.legislation.gov.au/F2005L03908/latest) does not apply to trailers TA to TD (its applicability table). Its annex notes that windows in trailer caravans need no headform test. Use windows marked to ECE R43 as good practice. The Dometic S4 carries ECE R43.

### 1.3 AS/NZS 5601.2 and the LP gas locker

The current edition is AS/NZS 5601.2:2020 with [Amendment 2](https://nz.ahsca.org.au/wp-content/uploads/2024/09/107492-AS-NZS-5601.2-2020-Amendment-2-Publication-WEB.pdf), published 30 August 2024 and released in NSW on 6 September 2024 ([NSW Fair Trading](https://www.fairtrading.nsw.gov.au/trades-and-businesses/construction-and-trade-essentials/gasfitters/gas-standards-and-notes)). Report 02 section 5.2 used [SA Gas Bulletin 26](https://www.energymining.sa.gov.au/__data/assets/pdf_file/0005/922964/Gas-Bulletin-26-Conversion-of-buses-and-trucks-to-motor-homes.pdf), which applies the 2020 edition. Its locker rules still stand, because Amendment 2 leaves clause 3.3.2 (cylinders in compartments) unchanged:

- The locker is reached only from outside, holds only the cylinders and their equipment, and is sealed so vapour cannot enter the body. Its divider to the garage is sealed to the floor, the walls and the lid.
- A 25 mm unobstructed drain at its base ends facing rearward, 1 m from openings and 1.5 m from ignition sources unless offset 500 mm vertically. The other option is high and low vents in the hatch of at least 5,000 mm2 each per cylinder.
- Each cylinder is restrained for 4 times its filled weight in any direction.

What Amendment 2 adds:

- Clause 3.1.8 Note 4: vent and drain fittings must be durable, strong enough for weather and debris in travel, and UV stable.
- Clause 7.3.1: where any part of an appliance is inside the caravan, the living space has permanent ventilation of at least 4,000 mm2, or 610U + 650P mm2 (U the input in MJ/h of the appliances that are not room-sealed, P the number of sleeping places), whichever is greater.
- Clause 7.4.3: half of it within 150 mm of the floor. If the vents are covered for travel against dust, the cover must be removed or interlocked before the gas is used, and a CO alarm to EN 50291-2 or UL 2034 is fitted.

For this body: if LPG stays, the pressurised living area needs a CO alarm and vents that open before cooking. Report 13 proposes an all-electric trailer with no LPG. AS/NZS 5601.2 then does not apply, and the locker (G-15) and its hatch (BD-06) go.

### 1.4 Fire and escape

- Smoke alarm, NSW: required in every caravan where people sleep, under the Environmental Planning and Assessment Regulation since 25 February 2011. It must comply with AS 3786, have a hush button, and sit on or near the ceiling between the sleeping area and the rest. A heat alarm may not replace it ([NSW Planning circular BS 11-001](https://planning.nsw.gov.au/sites/default/files/2023-03/planning-circular-bs-11-001-new-smoke-alarm-requirements-for-moveable-dwellings.pdf), [Fire and Rescue NSW](https://www.fire.nsw.gov.au/fire-safety/home-fire-safety/smoke-alarms/smoke-alarms-what-is-the-law)). Here: one photoelectric alarm on the lid underside above the ladder landing at partition A, away from the kitchen and the bathroom. It then works with the roof up or down.
- Extinguishers: VSB1 13.2.2 asks for two of at least 1A:5B to AS 2444. The SA fire service recommends 1A:20B:(E) dry chemical powder for caravans ([MFS](https://mfs.sa.gov.au/community-safety/safety-and-education/fact-sheets/recreational-vehicles)), and [AS 2444 section 5](https://firesys.com.au/wp-content/uploads/2026/10/AS2444-Section-5-Portable-Fire-Extinguishers.pdf) covers vehicles. Fit one 1A:20B:(E) in the living area beside the entry door and one in the garage within 610 mm of the rear door (GAR-04), plus a fire blanket by the kitchen.
- Escape from the bed: no Australian rule found asks a caravan for a second exit or an escape window. VSB1 asks for one door. The Caravan Industry Association code could not be read, and EN 1645-1, the European caravan standard with emergency exit rules, does not apply in Australia. So nothing applies. Project rule (assumption): the bed is used only with the roof raised, because 77 mm of headroom is left with it down, so a zip panel of at least 500 x 450 mm in each side canvas wall beside the bed, opening from inside, is the second way out.

## 2. Panel data

The full table, with sheet sizes, inserts and every source, is `research/12-body-panels.yaml`. Few Australian makers publish stiffness, so D and S are calculated from the skin and core data with D = E t d² / 2 and S = G d² / c (t skin thickness, d distance between skin centres, c core thickness, E skin modulus, G core shear modulus). Wrinkling stress is 0.5 (E Ec G)^(1/3) from the [HexWeb design guide](https://indico.cern.ch/event/502085/contributions/2390123/attachments/1380676/2098699/7586_HexWeb_Sand_Design.pdf). R is the core's thermal resistance.

| Panel | Use | kg/m2 | D kNm2/m | Core shear strength MPa | Wrinkling MPa | R m2K/W | Mass basis |
|---|---|---|---|---|---|---|---|
| Creative Composites Complite 29 mm, XPS | Wall | 5.8 | 3.7 | 0.25 | 46 | 0.81 | Maker |
| Creative Composites 35 mm, XPS (made 21 to 100 mm) | Wall | 6.0 | 5.5 | 0.25 | 46 | 1.0 | Scaled from maker |
| Creative Composites 35 mm, PET 80 | Wall | 7.1 | 5.5 | 0.59 | 103 | 1.0 | Calculated |
| StyroMAX 35 mm, XPS | Wall | 5.6 | 5.5 | 0.25 | 46 | 1.0 | Calculated |
| DIY Caravans Panel B 29 mm, Jackodur XPS, 1.6 mm skins | Wall, roof | 6.5 | 3.9 | 0.25 (assumed) | 46 | 0.76 | Maker |
| DIY Caravans Panel A 29 mm, perforated PVC | Wall | 7 to 7.5 | 4.0 | Not published | 107 | 0.93 | Maker |
| DIY Caravans Floor Panel D 32 mm, H60 PVC | Floor | 7 | 11.2 (skins assumed) | 0.76 | 141 | 1.0 | Maker |
| Lavender Holypan HP30, PP honeycomb, 0.7 mm GF/PP skins | Floor | 4.8 | 3.6 | 0.47 | 127 | 0.29 | Maker |
| PanelMate or Ayrlite 2022, 30 mm aluminium honeycomb, 0.5 mm skins | Floor, partition | 4.4 | 20.8 | Not published | Not critical | 0.01 | Maker |
| Recommended floor, 30 mm, 2 x 2.0 mm woven roving, H80 PVC | Floor | 8.9 | 11.0 | 1.15 | 162 | 0.84 | Calculated |
| Alternative floor, 30 mm, 2 x 2.0 mm woven roving, PET 100 | Floor | 9.4 | 11.0 | 0.80 | 158 | 0.79 | Calculated |
| Recommended lid, 40 mm, 2.0 and 1.5 mm skins, XPS | Roof | 7.0 | 8.0 | 0.25 | 45 | 1.3 | Scaled from maker |

Material data behind the table:

- GRP skins: Polydet 1.5 mm is 2.07 kg/m2 with a tensile strength of 77 MPa and a tensile modulus of 6,500 MPa. The 2.0 mm skin is 2.76 kg/m2, 92 MPa and 6,000 MPa ([Polydet data sheet](https://www.nptab.se/content/files/pdf/optiplan/polydet_performance_datasheet.pdf)). Woven roving polyester laminate is 280 MPa and 16 GPa in flexure ([AZoM](https://www.azom.com/article.aspx?ArticleID=715)). The floor checks use 14 GPa and 200 MPa (assumption, below the AZoM figures). [Lamilux](https://www.lamilux.com/composites/products/gewebe.html) makes 48 % glass woven skins 1.5 to 2.0 mm thick and up to 3.2 m wide, and Lavender is its Australian distributor.
- Cores: Divinycell H80 has 1.15 MPa shear strength, 27 MPa shear modulus, 1.4 MPa compressive strength and 0.031 W/m.K ([Diab](https://diab-media.azureedge.net/clwjnze4/diab-divinycell-h-may-2026-rev26-imp.pdf)). Kerdyn Green 100 PET has 0.80, 25, 1.30 MPa and 0.033 W/m.K ([Gurit](https://pdf.nauticexpo.com/pdf/gurit/gurit-kerdyn-green/27794-106816.html)). XPS for walls has 300 kPa compressive strength and 0.031 W/m.K ([Ravatherm XPS X 300 SL](https://ravagobuildingsolutions.com/uk/wp-content/uploads/sites/30/2025/12/ravatherm-xps-x-300-sl-tds-version-11-20251212.pdf)). Lavender's XPS40 is 40 kg/m3 and 400 kPa ([TDS](https://lavenderpanels.com.au/wp-content/uploads/2020/10/XPS40-TDS.pdf)).
- Sheet sizes: Creative Composites makes one-piece panels up to 12.5 m long ([about our panels](https://www.creativecomposites.com.au/about-our-panels)). StyroMAX makes 2.0, 2.5, 3.0 and 3.2 m widths ([StyroMAX](https://styromax.com.au/about-styromax/)). DIY Caravans Panel A comes up to 3.0 x 10.0 m and Floor Panel D up to 2,400 mm wide ([DIY Caravans](https://www.diycaravans.com.au/product-category/composite-panels/)). So the floor, both side walls and the lid can each be one piece.

Inserts with published ratings (MAT-05, CON-03):

| Insert | Rated load | Source |
|---|---|---|
| bigHead SM1-B38A M6 or M8 stud, bonded to a skin | 0.25 to 3.75 kN tension and 0.1 to 5 kN shear, depending on the adhesive | [bigHead TDS](https://fileserver.mates.it/Prodotti/6_Inserti/TDS/BigHead/bigHead_SM1_B38A_TDS.pdf) |
| Deform-Nut M6, potted | About 2.2 kN tension and 1.7 kN shear | [Chemical Concepts](https://www.chemical-concepts.com/product/deform-nut-tc-dm-honeycomb-anchoring-system-metric-thread-m6-10x/) |
| Panelock APLB-1020 bolt with APLN-1010 nut, through a 31 to 38 mm panel | 14 kN shear, 20 kN tension | [Lavender](https://lavenderpanels.com.au/wp-content/uploads/2020/10/Panelock.pdf) |
| High-density PVC or pultruded GRP strip | Not published. A pull test sets it (LR-09) | [DIY Caravans](https://www.diycaravans.com.au/shop/panel-insertion-pultrusion-50-x-25-mm/) |

## 3. Load cases and criteria

Cases follow report 11 (LC1 to LC10) and CHASSIS.md. The mass the body mounts carry is about 2,020 kg: the body (741 kg), the solar panels (90 kg) and the contents (1,188 kg: living area, module, bikes, panniers and garage stowage). Panel checks treat each panel as a one-way span with an effective width of the load patch plus half the span (planning method, calculated).

| Case | Body load | Result (calculated) |
|---|---|---|
| LC1, 1 g | 100 kg bike wheel on 229 x 635 mm midway between the raisers | Floor deflects 4.6 mm, span/269 |
| LC1, 1 g | 100 kg person on one foot, 100 x 150 mm | 5.4 mm, span/228 |
| LC1, 1 g | Lid with 90 kg of solar over 2,365 mm between the walls | 6.9 mm, span/343 |
| LC2, 3 g | Bike wheel | Skin 14 MPa, core shear 0.06 MPa |
| LC2, 3 g | Foot | Skin 21 MPa, core shear 0.07 MPa, bearing 0.20 MPa |
| LC2, 3 g | Floor edge between outriggers 830 mm apart, 160 kg/m2 of floor and contents | Skin 7 MPa, deflection 3.2 mm |
| LC2, 3 g | 90 kg generator and jerry cans midway between outriggers | Skin 11 MPa |
| LC2, 3 g | Lid with solar | Skin 4 MPa, core 0.01 MPa, 21 mm deflection |
| LC2, 4 g | Each of 16 glass solar panel brackets | 0.22 kN down |
| Wind, 0.5 kPa | Wall over its 1.8 m height | Skin 4 MPa, 13 mm (span/136) |
| Wind, 40 m/s | Roof down at 110 km/h into a 36 km/h headwind. Pressure coefficient 1.0 over the front 4.4 m2 and 0.5 over the rest (assumption) | Net uplift on the lid 6.3 kN, 1.04 kN per latch for six latches. 1.87 kN per solar panel |
| Wind, raised | Lid raised in a 20 and a 25 m/s wind | Net uplift 0.4 and 1.8 kN, side force 1.4 and 2.1 kN |
| Restraint, 20 kN | Strap breaking load at an L-track anchor midway between the raisers | Skin 116 MPa, core shear 0.39 MPa |
| Restraint, 20 kN | The same 150 mm from a raiser | Skin 78 MPa, core shear 1.05 MPa |
| LC3, 0.8 g | Braking, all mounts | 15.9 kN |
| LC4, 0.5 g | Cornering, all mounts | 9.9 kN |
| LC5a | 13.4 kNm twist | Body takes 10.7 kNm (section 4) |
| LC7, times 2 | 1.6 g forward, 1.0 g sideways | 31.7 kN and 19.8 kN on all mounts, 0.9 kN per bolt forward. The 1.0 g overturning moment of 11.8 kNm gives 9.6 kN on each raiser line against 9.9 kN of weight |
| LC8a, 1.5 g | Snatch on a recovery point | 29.7 kN |
| LC9, 3 g | 255 kg bed load on the two 2,330 mm side ledgers | 1.6 kN/m, 0.24 kN per fixing at 150 mm pitch |

Criteria a planning engineer would accept:

- Skin stress at most half the ultimate strength. ISO 12215-5 sets the design stress of FRP at 0.5 times its ultimate ([ISO 12215-5:2019](https://www.iso.org/standard/69552.html)). That allows 38 MPa for a 1.5 mm Polydet skin and 100 MPa for the woven roving skin at the assumed 200 MPa.
- Core shear at most half the core's shear strength (assumption, the same factor as the skins).
- Compressive skin stress at most half the wrinkling stress, and bearing at most half the core's compressive strength (assumption). The HexWeb guide lists these failure modes with strength, stiffness, panel buckling, shear crimping and intra-cell buckling.
- Inserts: working load at most half the rated load, and a pull test in a sample of the real panel (LR-09).
- Breaking-load cases such as the 20 kN anchor: no failure, with a factor of at least 1.5 on ultimate (assumption).
- Deflection at 1 g: floor span/200 under a point load, lid span/150, wall span/100 under 0.5 kPa (assumptions, the deflection limits the engineer sets).

Every case passes except the 20 kN anchor near a support. Midway between the raisers it has a factor of 1.7 on skin and 2.9 on core. Near a raiser the core's factor falls to 1.1. So each L-track hardpoint strip is bolted into the nearest steel: into both raisers where the track row crosses them, and, for the anchors outboard of the raisers (the Tuareg's road-side straps at Y +1,050), through a short strip along the trailer into the nearest outrigger. The two rows sit at X 5,205 and 7,003, between chassis stations, over the rear water tank and the battery, so no crossmember can be added under them (section 4).

## 4. Body-to-chassis mounting and the twist

Under LC5a the bare chassis twists 0.48 degree between the XT front hinge and rear shock crossmembers, 20.1 mm across 2,400 mm at one corner (calculated). Its torsional stiffness over that zone is 1.6 x 10⁶ Nm/rad. The bonded body is far stiffer: about 1.9 x 10⁷ Nm/rad for the closed garage box and 1.2 x 10⁷ Nm/rad for the living area (planning estimate from the skin shear stiffness). Any mount that holds the floor on the raisers makes the two share the twist torque by stiffness.

| Option | What the body sees from the twist | Added mass | What cracks or leaks in service | Source |
|---|---|---|---|---|
| A. Bonded and bolted through the floor into the raisers and outriggers | About 80 % of the 13.4 kNm, 10.7 kNm. The chassis twist falls to about 0.10 degree. Skin shear about 0.5 MPa | About 5 kg of bolts and crush tubes | Bolts loosen as the strip and core creep, sealant at bolt holes fails, the bond to the steel tears | Report 02 FAIL-03, report 11 section 4.2, [DIY Caravans chassis guide](https://www.diycaravans.com.au/diy-guide-caravan-and-trailer-chassis-design/) |
| B. As A, bolted through the EPDM-faced bearer strip with no bond to the steel | The same 80 %, because the raiser bolts carry most of it | As A | As A without the torn bond. The strip seals and isolates | CHASSIS.md bearer strip |
| C. Angle brackets from the walls to the outrigger tips | The twist goes in at the wall foot | 10 to 15 kg (estimate) | Skins crack round each bracket, brackets loosen | Report 02 section 4 |
| D. Rubber or spring mounts | With rubber at the outrigger tips (0.3 kN/mm) the share stays 80 %, because the raisers still carry it. Isolation needs every mount soft | 10 to 20 kg (estimate) | Rubber ages, the body moves against the plumbing and cables. Unicat calls this a compromise even on road trucks | [Unicat](https://unicatexpeditionvehicles.com/frame-assembly/) |
| E. Three-point subframe: one fixed bearing and one or more pivots | Almost none. The chassis twists freely | 60 to 100 kg and 75 to 100 mm of height (estimate) | Pivots wear. Every pipe, cable and tank link must flex | [Foundation Vehicles](https://www.foundationvehicles.com/technology/3-point-vs-4-point-vs-5-point-subframes/), Unicat |
| F. Four- or five-point subframe | Low, staged along a long body | More than E | As E, and over-constraint if the layout fights the frame | Foundation Vehicles |

Truck campers need E or F because a truck frame twists many degrees (Foundation quotes up to 22 degrees of articulation for its E-Series subframe). This chassis twists less than half a degree at its design torque, and the floor needs the outriggers under its 557 mm edge, which a subframe would replace with its own frame. So **B is recommended**.

**Mount positions.** At each of the nine stations (X 1,845, 2,437, 3,003, 3,570, 4,162, 4,992, 5,822, 6,550 and 7,295): one bolt through the floor into each raiser at Y ±618, and one into each outrigger tip at about Y ±1,140, just inside the wall line. 36 bolts.

**Loads per bolt.** Shear about 0.9 kN (LC7 forward, 31.7 kN shared by 36 bolts). Tension up to 4.2 kN at the raiser bolts next to the axle group in LC5a. About 1.1 kN at each raiser bolt from the LC7 overturning moment.

**Fastener.** Lindapter Hollo-Bolt HB10-3, hot-dip galvanised, grip 41 to 60 mm, which takes the 3 mm raiser wall, the 21 mm strip, the 30 mm floor and a 3 mm spreader. Its safe working load is 8.5 kN in tension and 10 kN in single shear at a factor of 5 in S275 hollow section, so the worst bolt works at 0.49 ([Lindapter Hollo-Bolt data](https://www.abbots-uk.com/files/ww/lindapter-type-hb-datasheet.pdf)). Lindapter warns that a thin wide face can fail first, so the engineer checks the 3 mm raiser top.

**Isolation (MAT-04).** Galvanised steel touches only the HDPE strip and the bolt. A pultruded GRP crush tube through the floor keeps aluminium off the steel. Where an aluminium extrusion or the portal foot sits over steel: Duralac on the faying surface and a nylon washer and sleeve on the bolt. Tef-Gel on any stainless thread in aluminium (report 04 section 6).

**Sealing and service.** Each bolt passes through a high-density insert, never bare foam. MS polymer sealant in the hole and under a bonded 50 x 50 mm spreader plate. Shim each outrigger tip to within 2 mm of the raiser plane (DIY Caravans' tolerance). Re-torque every bolt after the first rough trip (FAIL-03).

## 5. The rear wall and the openings

The rear wall keeps a 40 mm strip on the road side (Y 1,125 to 1,165), a 380 mm pier on the kerb side in front of the gas locker (Y -1,165 to -785) and 360 mm above the 1,440 mm opening. Solid, it would resist racking with about 9,700 N/mm in its plane. The pier alone gives about 180 N/mm (calculated). Without a frame the garage end of the box is an open tube, and the twist and the bed loads go into the side walls, the floor and the bed deck.

How the box keeps its shape:

- **A portal round the rear opening.** Header: aluminium SHS 50 x 50 x 3, 6060-T5 (Capral EB1004, 1.52 kg/m, I = 20.8 cm4), 1,910 mm long, top at module Z 1,490, carrying the ledger under the bed deck's rear edge. Kerb-side post: the same SHS at Y -785 to -835, floor to header. It is also the frame of the gas locker's sealed divider. Road-side jamb: RHS 80 x 40 x 3 (Capral EL8019), 40 mm across in the 40 mm strip and 80 mm along the trailer, bonded to the side wall's inner skin. It keeps the full 1,910 mm opening, so CLR-09 does not change. Joints: bolted aluminium corner gussets, then the frame bonded and riveted to the wall skins. The feet bolt through the floor into the rear body crossmember at X 7,295 with the isolation in section 4. About 10 kg (calculated). With the portal and the pier together the rear wall racks 3.6 mm under the body's share of LC5a, and the SHS corners see about 18 MPa, against a 6060-T5 yield of 110 MPa (report 04 section 5).
- **The rest of the garage box.** Partition A (20 mm honeycomb, sealed) closes the front of the garage and the 20 mm honeycomb bed deck closes its top. Bond and rivet both into the side walls on angles, so each acts as a diaphragm. With the portal they make the garage a closed box again.
- **Edges.** Aluminium corner joiners at the four vertical corners (DIY Caravans' wall joiner is 1.8 kg/m), floor joiners round the floor edge (1.27 kg/m for 29 mm panels) and the pop-top bottom ring along the wall tops. Each edge is bonded with MS polymer, which DIY Caravans and the pop-top kit specify ([joiners](https://www.diycaravans.com.au/product-category/composite-panel-joiners-adhesives/), [pop-top kit](https://www.diycaravans.com.au/shop/pop-top-extrusion-kit-2-up-to-4-8m-x-2-4m/)).
- **Framed openings.** Every cut edge is sealed and framed. Doors and windows bring their own frames: the DC door frame is about 36 mm deep, and the S4 window has an inner frame. Large cut-outs without a bought frame (the garage door and the kitchen opening) take DIY Caravans' 2 mm aluminium door profile, which it sells for food trucks and toy haulers ([door profile kit](https://www.diycaravans.com.au/shop/diy-door-profile-kit-parts-a-b/)). Cut-out corners are radiused, never square: 68 mm for Aussie Traveller service doors and 90 mm at the top of a DC door ([Aussie Traveller doors catalogue](https://cdn.shopify.com/s/files/1/0542/4939/0251/files/5_Caravan_Doors.pdf?v=1723079234)).

The kerb side wall carries the kitchen opening (1,500 x 450 mm, 50 mm above the floor), the entry door (622 x 1,623 mm), the gas locker hatch (650 x 650 mm) and a 500 x 450 mm window. That is 2,775 mm of openings along the 5,500 mm wall. The wall stands on the floor edge, which the outriggers carry at most 830 mm apart, so it does not have to span between supports as a beam. It does carry its share of the twist and the roof. Rules for the layout (assumptions, from the practice above):

- At least 300 mm of full-height wall between openings, and 150 mm from an opening to a panel edge or corner.
- A continuous aluminium sill under the kitchen opening, because only 50 mm of wall is left below it.
- Under the living area the stations are only 566 to 592 mm apart, so the 622 mm entry door and the 1,500 mm kitchen opening must cross a station. Where one does, that outrigger-tip bolt moves inboard of the door or hatch frame, and the floor joiner runs unbroken under the sill.
- No opening in the 380 mm rear pier or within 300 mm of the rear corners.

## 6. The raising roof

The lifted load is the lid (90 kg), the solar panels (90 kg glass, or 31 kg for report 13's Sunman panels), the top ring extrusion (26 kg), the roof hatches (12 kg) and half the canvas (5 kg): 223 kg, 2.19 kN, or 164 kg with the Sunman panels (calculated).

### 6.1 Roof types

| Type | Mass of the moving walls | Dust and water | Insulation when raised | Wind when raised | Field failures | Australian supply |
|---|---|---|---|---|---|---|
| **Hard lid on canvas walls, parallel lift (recommended)** | Canvas about 9 kg, top ring 26 kg (calculated from DIY Caravans' 3.3 kg/m for both rings) | Roof down, a bulb seal between the rings is compressed by the latches. Raised, the canvas zips leak dust, but the roof travels down | Canvas has almost none. 13 m2 of skirt at an 825 mm lift | The canvas flaps and the lid sways, so the corner posts take the side force | Latches that unhook in travel, canvas wear and mould, bent lifters, broken cables ([RV Daily](https://rvdaily.com.au/how-secure-are-the-latches-on-your-pop-top-roof/)) | DIY Caravans pop-top extrusions, corner joiners, seals and lifters ([pop-top kits](https://www.diycaravans.com.au/product-category/pop-top-roof-kits/)) |
| Folding hard walls | About 80 kg of 35 mm panel for the sides and ends, plus hinges (estimate) | Many hinge lines to seal | Like the walls | Stiff | Hinge seals leak and hinges loosen | No maker found for a 5.5 m trailer |
| Telescoping hard walls | An inner or outer box, 80 to 100 kg (estimate) | Sliding seals | Like the walls | Stiff | Sliding seals wear and bind | Alaskan Campers (USA), not sold in Australia ([Alaskan](https://www.alaskancampers.com/hard-sided/)) |
| Front-hinged wedge | Triangular canvas ends, about 6 kg | As the canvas lid | As canvas | The lid acts as a sail about the hinge | Hinge and strut wear | Common on camper trailers |

The wedge is simpler, but it gives the full 825 mm only at one end. Hinged at the front it lifts the bed end and leaves the living area at 1,800 mm. The parallel lift gives the height everywhere and keeps the solar panels level.

### 6.2 Lift systems

| System | Products | Force and speed | Mass | Failure modes |
|---|---|---|---|---|
| **Electric linear actuators, four corners (recommended)** | LINAK LA36, 12 V, 100 to 999 mm stroke ([LINAK LA36](https://www.linak.com/products/linear-actuators/la36/)). DIY Caravans' four-actuator kit: 300 kg each, 600 to 1,000 mm stroke, IP66, synchronised remote, assembled in Australia ([kit](https://www.diycaravans.com.au/shop/in-line-linear-actuators-kits-4/)) | LA36 at 12 mm pitch: 2,600 N push and pull at 31 to 41 mm/s, 4,500 N at 18 to 23 mm/s, 6,800 N at 12 to 16 mm/s. Self-lock 3,400 to 8,800 N. IP66 in use. 20 % duty at full load. Fitted length 250 mm plus stroke | About 3.5 kg each (estimate) plus guide posts and controls, 30 kg in all (estimate) | Corners out of step rack the lid, so use Hall feedback and parallel control (LA36 IC Parallel). Motors need 12 V at about 20 A each at full load. A hand crank is the fallback |
| Hydraulic rams with a hand or electric pump | Alaskan Campers used hydraulics from 1958 and now offers electric actuators ([Truck Camper Magazine](https://www.truckcampermagazine.com/news/alaskan-campers-debuts-electric-actuator-lifts/)). No pop-top ram kit found in Australia | High force, a hand pump works with flat batteries | 25 to 35 kg with pump and lines (estimate) | Seal leaks, uneven rams without a flow divider, oil in a dusty body |
| Gas struts | Generic | Force falls with cold | Light | Hard to balance on a 223 kg lid, struts fade and leak (DIY Caravans) |
| Spring scissor canopy lifters | DIY Caravans: 900 mm lift, 35 kg per lifter, 5.5 kg ([large lifter](https://www.diycaravans.com.au/shop/pop-top-canopy-lifter-large/)) | Seven needed for 223 kg | 38 kg for seven | Arms bend if over-extended. DIY Caravans advises 70 to 80 % of full lift |
| Cable winders | Jayco-style winch and cables | Winch force | 10 to 15 kg (estimate) | Cables and crimps break, damage if a latch is left on (RV Daily) |

### 6.3 Lift height and the roof-down ceiling

900 mm of sitting room over the 1,723 mm mattress top puts the raised ceiling at 2,623 mm.

| Roof-down ceiling | Lift | Travel height | Effect |
|---|---|---|---|
| **1,800 mm (recommended)** | 823 mm, so 825 mm | 2,762 mm | As planned. Inside the LA36's 999 mm stroke and DIY Caravans' 1,000 mm kit |
| 2,000 mm | 623 mm | 2,962 mm | 0.48 m2 more frontal area on a body of about 6.6 m2, so about 7 % more drag (estimate). About 19 kg more wall (calculated). Higher centre of gravity and side area. Standing room in the living area roof down |

Recommendation: keep 1,800 mm and lift 825 mm. The longer stroke costs nothing in the actuator, while the taller body costs drag, mass and roll margin on every kilometre towed. The bed stays unusable roof down either way (77 or 277 mm of headroom).

### 6.4 Actuator choice and hold-down

- Four LA36 actuators, the 4,500 N version (36120 series, gear G, 12 V), with Hall feedback and IC Parallel control, one in each corner inside the wall line. Each lifts 0.55 kN, an eighth of its rating. Retracted, each is 1,075 mm long, so it fits under the 1,800 mm ceiling.
- Telescopic aluminium guide posts beside each actuator take the side force, so the actuator rod sees only axial load. LINAK allows the rod eye to turn only 0 to 90 degrees.
- Wind when raised: the lid's net uplift turns positive at about 20 m/s (72 km/h) and reaches 1.8 kN at 25 m/s, with 2.1 kN of side force and 0.44 kNm on each post (calculated). The self-locking actuators hold the lid down. Rule for the manual (assumption): lower the roof in gusts over about 60 km/h, or guy the lid corners to the chassis.
- Travel: six over-centre latches with a spring secondary catch (UNISEG's Snap-Flat design answers the unhooking failure, [RV Daily](https://rvdaily.com.au/how-secure-are-the-latches-on-your-pop-top-roof/)), two on each side and one at each end. Each sees 1.04 kN at 40 m/s and is specified for at least 2.1 kN (assumption, a factor of 2). The retracted actuators are a second hold-down path. An interlock stops the lift while any latch is closed.

### 6.5 Sealing, insulation and the bed guard

- Seal: a bulb seal on the bottom ring, compressed 5 to 8 mm by the latches (assumption), and a drip lip on the top ring outside it ([DIY Caravans weather seal](https://www.diycaravans.com.au/shop/pop-top-weather-seal-m/)).
- Canvas: a heavy canvas with zip windows and flyscreens, plus a quilted inner liner for cold nights (3 kg, estimate). The zip panel beside the bed is the second way out (section 1.4).
- Bed guard (report 04 section 8): the net's bottom edge clips to bigHead studs along the deck's front edge. Its top hangs on four straps from D-rings in the lid's bottom ring. With a parallel lift the D-rings rise 825 mm, so the straps take up the gap above a 580 mm net. The straps come off before the roof goes down, and the lowering switch sits where a person sees the bed edge.
- Awning: it mounts on the fixed wall below the bottom ring, so the lid lifts clear of it, and the canvas hangs inside the awning's roller.

## 7. Doors, hatches and windows

Every product below suits a 35 mm sandwich wall. Part numbers, sizes and sources are in `research/12-body-products.yaml`.

| Opening | Recommended | Size and cut-out | Wall range or frame depth | Mass | Dust sealing |
|---|---|---|---|---|---|
| Garage door, rear (BD-05) | The rear wall cut-out as the leaf, in DIY Caravans' 2 mm door profile, on a stainless piano hinge under the header with a drip rail. Two gas struts of about 750 N, because the door's hinge moment is about 230 Nm and the struts act at about 150 mm (calculated). Four Southco E3 vise-action compression latches | Opening 1,910 x 1,440 mm, leaf 1,905 x 1,435 mm | Profile made for 28.5 to 29.5 mm panels, so a 35 mm version is made to order (assumption) | 30.2 kg (calculated) | E3 latches give 6.4 mm of pull-up onto a bulb seal ([Southco](https://southco.com/en_au_int/e3-55-32)). A second D seal inside it, and a 5 mm rubber strip under the hinge, as DIY Caravans specifies |
| Entry door, kerb side (BD-07) | Aussie Traveller DC door, round corners, hinged on its front edge so airflow closes it | 1,623 x 622 mm, cut-out H+3 x W+3 with a 90 mm top radius | Standard seal for 29 to 35 mm walls. Frame about 36 mm deep | 25 kg (retailer listing) | Triple compression lock and a water and dust resistant seal ([catalogue](https://cdn.shopify.com/s/files/1/0542/4939/0251/files/5_Caravan_Doors.pdf?v=1723079234), [DIY Caravans](https://www.diycaravans.com.au/shop/atrv-dc-caravan-door/)) |
| Gas locker hatch (BD-06) | Aussie Traveller service door, bottom hinged, two key locks | 650 x 650 mm frame, 600 x 600 mm clear, cut-out 653 x 653 mm with 68 mm corners | 30 to 45 mm | 5 kg (retailer listing) | Seals matched to the wall, self-tightening locks. The locker vents through its 25 mm drain, so the hatch needs no vents |
| Kitchen slide-out (LA-07) | The drawer's own 35 mm outer panel closes the opening (counted in LA-07). The body gives a framed opening with a bulb seal and two Southco E3 latches | 1,500 x 450 mm, 50 mm above the floor | As the garage door profile | 6 kg for the frame, seal and latches (estimate) | Compression latches pull the panel onto the seal |
| Windows (BD-09) | Dometic S4, hinged or sliding, ECE R43 | 900 x 500 road side, 500 x 450 kerb side, 800 x 400 front above the spare wheel. Cut-out 500 x 448 for the 500 x 450 | 27 to 41 mm | 5.0 kg for the 500 x 450 (maker). 8.2 and 6.6 kg for the others (scaled by area, estimate) | Seals in the frame. Hinged sashes open top-hinged, so no edge faces forward |
| Roof hatches (BD-09) | Dometic Midi Heki 700 x 500 over the living area, Mini Heki Style 400 x 400 over the bed, a small vent over the bathroom | Midi Heki outer size 858 x 617 mm | 25 to 42 mm, which suits the 40 mm lid | 7.5 kg (estimate), 3.3 kg (maker), 1.5 kg (estimate) | Hatch seals. Fit them at the lid's ends, outside the solar array (report 13 wants a 4,108 x 2,168 mm clear area) |
| Toilet cassette door, road side | Small service door, about 450 x 290 mm (report 13 bathroom) | As listed | 30 to 45 mm | 1.5 kg (estimate) | Gasket |

Dometic product data: [S4 window](https://www.dometic.com/fr-fr/produit/dometic-s4-1), [roof hatches](https://www.dometic.com/fr-be/categorie/vehicules-de-loisirs-et-fourgons-amenages/baies-pour-vehicules-de-loisirs/domes-de-toit). These are Dometic's European pages. Australian stock and the masses of the larger S4 sizes and the Midi Heki are not confirmed.

Garage vents (GAR-01): petrol vapour is heavier than air. No Australian rule sizes a petrol garage vent. The US small-craft rule for natural ventilation gives A = 5 ln(V/5) square inches for a compartment of V cubic feet ([33 CFR 183.630](https://www.ecfr.gov/current/title-33/chapter-I/subchapter-S/part-183/subpart-K/section-183.630)). For the 280 ft3 garage that is about 13,000 mm2 of inlet and the same of outlet (calculated). So: two low vents of at least 6,500 mm2 free area, one in each side wall near partition A, and one high vent of 13,000 mm2 in the road-side wall just under the bed deck, towards the rear (the rear wall above the header opens into the bed space, not the garage). Double each opening where mesh covers it (AS/NZS 5601.2 note 6 to clause 7.3.1). 3 kg for the three (estimate).

## 8. Dust and water

**Why dust gets in.** On a dirt road the air flowing round the body leaves the inside below outside pressure, and dust is drawn through vents and gaps (report 02 FAIL-05). Australian off-road vans answer it two ways: seal every gap, and push filtered air in so the inside stays above outside pressure.

| Product | How it works | Power | Mass | Fitting | Source |
|---|---|---|---|---|---|
| **Carafan Sahara CP700 (recommended)** | Fan and filter that pressurise the van, moving or parked | About 5.8 A at 12 V (an owner's measurement) | Not published, 7 kg with ducts (estimate) | Inside a cabinet with the intake through the wall | [Carafan](https://carafan.com.au/), [Victron community](https://community.victronenergy.com/t/mppt-75-15-settings-and-carafan-dust-extraction-instal/27393) |
| Gusto DRS | Wall-mounted fan and filter, intake facing forward, not for use in rain | 18 A at most, on a 30 A fused supply | Not published | 310 x 310 mm wall cut-out, 260 x 260 mm cabinet vent | [Gusto manual](https://www.coastrv.com.au/cdn/shop/files/Gusto_DRS_Manual.pdf?v=6428087926919287103), [flyer](https://atlref.websitedevserver.com/wp-content/uploads/2024/06/Gusto_DRS-_Flyer_2023.pdf) |
| Dometic DRS2 | Unpowered roof scoop and filter, works only while moving | None | About 5 kg (estimate) | Roof 30 to 65 mm thick, so it would sit on the lid and take solar area | [Dometic manual](https://www.caravansplus.com.au/pdf/Dometic-DRS2-Manual.pdf) |

The CP700 is chosen because it works parked as well as moving and needs no roof space. Put its intake high on the front wall, beside the spare wheel, where it is clear of wheel spray (assumption).

**Seals and joints.**

- Doors and hatches: EPDM bulb seals pulled tight by compression latches. The DC door's triple compression lock, Southco E3 latches on the garage door and the kitchen opening, and a second D seal on the garage door. One Australian toy hauler maker triple-seals its garage-to-cabin door ([Titanium Caravans](https://titaniumcaravans.com.au/toy-hauler-caravans/)).
- Panel joints: bonded into extrusions with MS polymer, a bead inside and out.
- Penetrations: every cable, hose, filler and vent passes through a gland or grommet sealed on both skins (ADR 42 clause 21.1.1 asks for grommets in metal). Every cut edge of a panel is sealed with resin or an edge insert, so water cannot track along the skin bond.
- The lid: the bulb seal on the bottom ring and a drip lip on the top ring (section 6.5).

**The garage (GAR-02).** Partition A runs from the floor to the bed deck, and above the deck the bed space is open to the living area. So pressurising the living area also pressurises the bed space, and any leak at partition A or the deck runs from the bed side into the garage. That keeps petrol vapour and dust on the garage side even where a seal is imperfect. Seal partition A and the deck to the floor, walls and each other with Sikaflex-221 (report 04 section 9), and draw every penetration through them. The garage itself is not pressurised and its low vents admit some dust, which the bikes tolerate.

**Garage venting for petrol vapour (GAR-01).** Two low vents and one high vent, sized in section 7. The low vents sit 500 mm or more from the gas locker's drain outlet and away from the battery box vent on the road side.

**Water.** Drip rails over the garage door, the entry door and the kitchen opening. Drainage paths drawn for each opening (FAIL-06). The garage door seal closes onto a 10 mm raised lip at the sill, so spray running down the closed door stays outside (assumption).

**Test.** Report 02 FAIL-05: a dust run on a dirt road before the fit-out, with the CP700 on and off.

## 9. The awning and the mud flaps

### 9.1 Awning (BD-13)

The awning runs along the kerb side over the kitchen and the entry door. It mounts on the fixed wall just below the pop-top bottom ring, so the lid rises clear of it, and it may stand at most 100 mm proud of the body (VSB1 5.2).

| Product | Case length | Extension | Mass | Source |
|---|---|---|---|---|
| **Fiamma F45L 500, Polar White, 06530A01R (recommended)** | 5,020 mm (canopy 4,350 mm) | 2,500 mm, 10.9 m2 of shade | 39.0 kg (maker) | [Fiamma F45 data sheet](https://www.fiammausa.com/en/f45s-en.html) |
| Fiamma F45s 450 | 4,230 mm | 2,500 mm, 10.8 m2 | 29.5 kg (65 lb, maker) | Same |
| Thule 4200 cassette | 3,500 to 4,500 mm | Not found | 21.7 kg for 3.5 m (retailer) | [DIY Caravans](https://www.diycaravans.com.au/shop/thule-4200-cassette-awning/) |
| Aussie Traveller cassette awning | Several | Not found | 28 kg (retailer listing, probably shipping) | [DIY Caravans](https://www.diycaravans.com.au/shop/atrv-cassette-awning/) |
| Camec roll-out | 12 to 21 ft | Not found | 28 kg (retailer listing) | [DIY Caravans](https://www.diycaravans.com.au/shop/camec-roll-out-awning-black-white-fade/) |

The F45L 500 is the only one found that covers the 4.9 m the layout wants. It is 39 kg, so BD-13 becomes 41 kg with 2 kg of wall brackets and bolts (estimate). The bracket bolts land on a pultruded insert strip along the wall top. Fiamma's case depth was not found, so the 100 mm limit is checked when the brackets are chosen. The F45s 450 saves 9.5 kg if 4.2 m is enough.

### 9.2 Mud flaps (BD-10)

The floor is the guard over the tandem's tyres (VSB1 10.2). With one guard over both axles, its rear must reach down to 300 mm above the road on an off-road trailer (approach 2), and a mud flap may form that part. The floor underside is at Z 842, so the flap must hang 542 mm below it.

- Product: a 610 x 455 mm (24 x 18 in) black rubber flap, 24X18B from The Boss Shop ([listing](https://www.thebossshop.com.au/mudflap-rubber-610mmw-x-455mml-black)). At 6 mm thick and 1,500 kg/m3 of rubber it is 2.5 kg (calculated, thickness assumed).
- Hanger: a galvanised bracket from the outrigger at the XT rear shock station (X 5,822) down to Z 755, so the flap's bottom edge sits at about Z 300 behind each rear tyre at Y ±831. 2.1 kg with bolts (estimate). The flap must clear the tyre through its 60 mm bump travel, during which the hub moves 11.6 mm rearward (report 11 section 5.1).
- Width: 610 mm covers the 245 mm tyre with margin (VSB1 10.2.1).
- BD-10: 9.2 kg for the pair (estimate), against 8.0 kg in the repo now and 25 kg in the brief.

## 10. Mass

Growth allowances follow MASS-06: 7 % on calculated lines, 20 % on estimates and retailer listings, 0 % on a maker's figure. Panel masses: floor 8.92 kg/m2 (two 3.22 kg/m2 woven roving skins at 48 % glass, 2.08 kg/m2 of H80, 0.4 kg/m2 of adhesive), walls 6.0 kg/m2, front wall 6.7 kg/m2, lid 7.0 kg/m2.

| Line | Item | Mass | Basis | With growth | Brief | Change |
|---|---|---|---|---|---|---|
| BD-01 | Floor: 13.2 m2 of panel (117.7 kg), hardpoint strips and crush tubes (3.0 kg, estimate), vinyl over the 7.2 m2 living area at 1.5 kg/m2 (10.8 kg, estimate) | 131.5 | Calculated | 140.7 | 105.6 | +25.9 |
| BD-02 | Lid: 13.2 m2 less 0.59 m2 of hatch cut-outs, plus 2 kg of insert strips | 90.0 | Calculated | 96.3 | 73.4 | +16.6 |
| BD-03 | Side walls: 19.8 m2 less 2.92 m2 of openings, plus 6 kg of insert strips. The kitchen panel is in LA-07 | 107.3 | Calculated | 114.8 | 99.0 | +8.3 |
| BD-04 | End walls: front 3.87 m2 at 6.7 kg/m2 (25.9 kg), rear 1.44 m2 (8.7 kg), SHS portal (10.1 kg), brackets (1.0 kg) | 45.7 | Calculated | 48.8 | 41.9 | +3.8 |
| BD-05 | Garage door: leaf 16.4, profiles 6.4, hinge 3.0, struts 1.1, latches 1.4, seals 1.0, drip rail 1.0 | 30.2 | Calculated | 32.4 | 45.0 | -14.8 |
| BD-06 | Gas locker hatch, Aussie Traveller service door 650 x 650 | 5.0 | Retailer listing | 6.0 | 4.0 | +1.0 |
| BD-07 | Entry door, Aussie Traveller DC 1,623 x 622 | 25.0 | Retailer listing | 30.0 | 20.0 | +5.0 |
| BD-08 | Extrusions and fixings: floor joiners 15.7 m at 1.4 kg/m (21.9), corner joiners 7.2 m at 2.0 kg/m (14.4), pop-top bottom ring 15.8 m at 1.65 kg/m (26.1), adhesive and sealant (8.0), 36 mount bolts, crush tubes and spreaders (5.0) | 75.4 | Calculated from DIY Caravans' extrusion masses, scaled to 35 mm panels (estimate) | 90.5 | 50.0 | +25.4 |
| BD-09 | Windows, hatches and vents: S4 windows 8.2, 5.0 and 6.6, Midi Heki 7.5, Mini Heki Style 3.3, bathroom vent 1.5, Carafan CP700 7.0, kitchen opening frame 6.0, garage vents 3.0, cassette door 1.5 | 49.6 | Mixed, mostly estimates | 59.5 | 50.0 | -0.4 |
| BD-10 | Two mud flaps with hangers | 9.2 | Estimate | 11.0 | 25.0 | -15.8 |
| BD-11 | Wiring, plumbing, lighting and hardware | 60.0 | Estimate, kept until the systems design | 72.0 | 60.0 | 0 |
| BD-12 | Pop-top lift and skirt: top ring 26.1, canvas 9.4, four actuators with guide posts and controls 30.0, six latches 2.4, seals 3.2 | 71.0 | Mixed, ring calculated, the rest estimates | 85.2 | 45.0 | +26.0 |
| BD-13 | Fiamma F45L 500 (39.0, maker) and brackets (2.0, estimate) | 41.0 | Maker | 41.4 | 35.0 | +6.0 |
| | **Total** | **740.9** | | **828.6** | **653.9** | **+87.0** |

The repo carries the body at 636.9 kg now (BD-10 at 8 kg), so this design basis adds 104 kg to the tare, or 64 kg with growth (764.3 to 828.6 kg). Most of it sits near the body's middle, so the towball barely moves, but the gross mass does. On its own it takes the fully loaded case TC2 from 3,408 to about 3,512 kg, 12 kg over the 3,500 kg ATM, and TC6 to about 3,536 kg. Report 13's equipment changes, for example 58.8 kg off the roof with glass-free solar panels, are needed to bring every case back under the ATM.

Where the 104 kg comes from: the floor (+26 kg, a stiffer 30 mm floor with woven skins for the bike wheels and 20 kN anchors), the raising roof (+43 kg for the lid, the top ring and four actuators), and the extrusions (+25 kg, the older model had no pop-top ring). Lighter options: the PET floor core costs 7 kg more and Holypan HP30 saves 54 kg but deflects 13 mm under a bike wheel. Glass-free solar panels cut the lifted mass from 223 to 164 kg.

## Open questions

Each ends with the assumption the designer should use.

1. LPG or an all-electric trailer? Assumption: keep the gas locker and its 650 x 650 hatch in the design until the owner decides on report 13's all-electric proposal, which would remove BD-06 (5 kg) and AS/NZS 5601.2.
2. The floor core: H80 PVC or recycled PET? Assumption: H80, which is lighter (8.9 against 9.4 kg/m2), stronger in shear (1.15 against 0.80 MPa) and more ductile in shear (30 % against 16 % strain), which suits fatigue.
3. The L-track rows at X 5,205 and 7,003 sit between chassis stations, over the rear tank and the battery. Assumption: hardpoint strips bolted into both raisers and the nearest outrigger carry the 20 kN anchors, and a pull test on a floor sample confirms it before panels are ordered (LR-09). Fallback: move each row onto a chassis station and re-run RES-01.
4. Will the engineer accept a body that shares the twist? Assumption: yes, with the 36 bolts and the body joints checked for LC5a at 10.7 kNm, as most Australian composite vans are mounted.
5. A Hollo-Bolt in the 3 mm C450 raiser top. Assumption: HB10 at 8.5 kN safe working load holds. Fallback: nut plates welded inside the raisers and outriggers before galvanising, which must then be in the chassis drawings.
6. The raised roof in wind. Assumption: lower the roof in gusts over 60 km/h, written in the manual.
7. Solar panels on the lid. Assumption: the masses here keep the repo's 90 kg of glass panels. If report 13's bonded Sunman panels are taken, the lid's top skin stays flat and free of hatches over 4,108 x 2,168 mm and the hatches go to the lid's ends.
8. The garage door frame. Assumption: DIY Caravans' door profile is made to order for 35 mm, or a 2 mm aluminium angle frame of the same section is fabricated.
9. The escape route from the bed. Assumption: a zip panel of at least 500 x 450 mm in each side canvas wall beside the bed.
10. The awning's depth. Assumption: the F45L 500 on Fiamma wall brackets stays within 100 mm. If not, the F45s 450.

## Could not verify

- Masses that are retailer listings and may be shipping masses: the DC door (25 kg) and the service door (5 kg).
- Masses that are estimates: the larger S4 windows, the Midi Heki, the Carafan CP700, the LA36 actuator, the guide posts, the latches, the canvas and the mud flap hangers.
- XPS shear strength (0.25 MPa) and shear modulus (8 MPa): taken from an earlier Ravatherm sheet. The 2025 data sheet gave the compressive strength and conductivity but its shear values could not be re-read.
- Woven roving skin data: the checks use 14 GPa and 200 MPa, below AZoM's 16 GPa and 280 MPa, because no Lamilux strength figure was found.
- Creative Composites, StyroMAX and PanelMate publish no stiffness, no insert ratings and, apart from Creative Composites' 29 mm panel, no masses. The 35 mm masses are scaled or calculated.
- No pull-out or shear rating is published for high-density PVC or pultruded insert strips.
- The LA36 figures come from LINAK's LA36 data sheet. The link given is LINAK's product page.
- Australian stock of the Dometic S4 and Heki ranges, which were read on Dometic's European pages.
- The Fiamma F45L case depth and its bracket depth.
- The Caravan Industry Association code and EN 1645-1's emergency exit clauses.
- A load rating for over-centre pop-top latches and for the Southco E3. The 2.1 kN latch figure is an assumption.
- The body's torsional stiffness is a thin-walled box estimate, not a finite element model. The twist share and the bolt forces should be rechecked with the body in the frame model.
- The effect of report 13's equipment changes on the trailer cases is not added here.

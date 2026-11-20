# 02: Design, drawing and documentation practice

Note added 20 Nov 2026. DIM-01 now has Y positive to the right (road) side, not the left (kerb) side. With X rearward and Z up, the old definition was a left-handed frame, so the right-handed CAD model was the mirror image of the trailer. The project datum is now X along the trailer from the coupling ball centre, positive rearward, Y across from the centreline, positive to the road side, and Z up from the ground with the trailer level at design ride height. Read rule DIM-01 below with that change.

Status: draft 2. Items marked TODO still need a source or a check. Links were checked on 16 Nov 2026 with one batch request each; links marked "bot check" returned a Cloudflare challenge to automated requests and were taken from search results.

This report sets out how to draw, document and sequence the camper trailer build so that (a) the reviewing engineer can check and sign it off quickly and (b) the builder can follow it step by step without mistakes. It is written as rules the project website can enforce. Each rule has an ID. "Must" rules block a sheet, calculation or build step from being marked as issued. "Should" rules raise a warning.

Several standards named here are paywalled (AS 1100, ISO 128, ISO 129, ISO 2768, ISO 13920, AS 1101.3, AS/NZS 1554.1, AS/NZS 4680, AS/NZS 5601.2, AS/NZS 3001.2, NFPA 1192). Where I could not read the standard, the claim comes from the publisher's preview or catalogue page, a regulator's summary, or an industry summary, and says so.

---

## 1. Drawings

### 1.1 Standards to use

| Standard | What it covers | How this project uses it | Source checked |
|---|---|---|---|
| AS 1100.101-1992 (R2014) Technical drawing, general principles | Sheet layout, lines, lettering, scales, projection, sections, dimensioning | Base rules for every sheet | [ANSI catalogue](https://webstore.ansi.org/standards/sai/11001011992r2014) (bot check) |
| AS 1100.201-1992 (R2014) Mechanical engineering drawing | Mechanical practice, surface texture, weld representation | Chassis, brackets, machined parts | [ANSI catalogue](https://webstore.ansi.org/standards/sai/11002011992r2014) (bot check) |
| HB 47-1993 | Explains AS 1100 dimensioning and tolerancing | Reference for whoever draws | [Accuris catalogue](https://store.accuristech.com/standards/hb-47-1993?product_id=2047235) (bot check) |
| ISO 7200:2004 | Data fields in title blocks | Title block template | [ISO 7200 preview](https://cdn.standards.iteh.ai/samples/35446/ada1fb53a4c24991b955ed8061f2d394/ISO-7200-2004.pdf) (read) |
| ISO 128 and ISO 129-1 | International views, lines, sections; dimensioning | Only where AS 1100 is silent | TODO confirm current parts and editions |
| ISO 2768-1 and -2 | General tolerances for machined and cut parts | Tolerance note on part drawings | TODO confirm values before putting them on the template |
| ISO 13920:2023 | General tolerances for welded constructions: four classes (A to D) for lengths and angles, plus separate classes for straightness, flatness and parallelism (E to H in the 1996 edition) | Tolerance note on weldments | [Modulus Metal summary](https://www.modulusmetal.com/iso-13920-welding-general-tolerances-for-welded-constructions/) (search snippet, not fetched); 2023 edition from the [preview contents](https://site-296502.mozfiles.com/files/296502/ISO-13920-2023.pdf) (not fetched) |
| AS 1101.3 | Australian weld symbols, based on ANSI/AWS A2.4 | Every weld callout | [draftsperson.net summary](https://blog.draftsperson.net/weld-symbols/) (read) |
| ISO 2553:2019 | International weld symbols, systems A and B | Reading European supplier drawings | [ISO 2553 preview](https://cdn.standards.iteh.ai/samples/72740/08d72a37dd1d4fb6b92ed5119d4b5902/ISO-2553-2019.pdf) (read) |
| AS/NZS 1554.1 | Structural steel welding: procedures, weld categories SP (structural purpose) and GP (general purpose), acceptance criteria | Weld category on every structural weld | [ASTCAD summary](https://astcad.com.au/welding-symbols-structural-steel-drawings/) and [ASI weld quality guide](https://steel.org.au/getattachment/9e3a138d-08d3-413d-8add-875e01b7498a/Welds-quality-capacity_bk122.pdf) (search snippets, not fetched) |
| AS/NZS 4680 | Hot-dip galvanised coatings on fabricated steel | Coating callout | Design rules via [GAA venting and draining guide](https://gaa.com.au/venting-draining-guide/) (read) |
| ASME Y14.35 | Revision of engineering drawings | Model for the revision system | [ASME page](https://www.asme.org/codes-standards/find-codes-standards/y14-35-revision-engineering-drawings-associated-documents) (read) |

**Projection.** Australian practice uses third-angle projection. AS 1100 is paywalled, so this rests on Australian drafting and teaching summaries ([ASTCAD](https://astcad.com.au/engineering-drawing-tips-to-improve-engineering-drawing-skills/), [AIMS Industrial](https://aimsindustrial.com.au/blogs/product-guides/engineering-drawing-symbols-guide), [NSW Department of Education graphics course](https://sites.google.com/education.nsw.gov.au/year8graphics/unit-1-hand-drawing-portfolio/3-types-of-drawings)). European supplier drawings (couplings, axles, hinges) are often first-angle.

- **DRW-01 (must)** Every sheet uses third-angle projection and shows the third-angle symbol.
- **DRW-02 (must)** Every sheet says "All dimensions in mm" and "Do not scale".
- **DRW-03 (must)** Bought-in drawings filed with the set are marked with their own projection method and weld symbol system if they differ from ours.

### 1.2 Title block: every sheet has

ISO 7200 makes these identifying fields mandatory: legal owner, identification number, date of issue and sheet number. Revision index, number of sheets and language code are optional in ISO 7200 ([ISO 7200 preview, Table 1](https://cdn.standards.iteh.ai/samples/35446/ada1fb53a4c24991b955ed8061f2d394/ISO-7200-2004.pdf)). The preview stops before the descriptive and administrative fields (title, approval, creator, document type), so those are not verified here. This project makes more fields mandatory than ISO does, because the shed print must be self-checking.

- **TB-01 (must)** Legal owner (the builder) and project name.
- **TB-02 (must)** Drawing number, unique and never reused (numbering in 1.7).
- **TB-03 (must)** Title, plus subtitle if useful ("Garage floor, tie-down anchor layout").
- **TB-04 (must)** Revision, matching the revision table on the same sheet.
- **TB-05 (must)** Status: DRAFT, FOR REVIEW, FOR CONSTRUCTION or AS BUILT. Only FOR CONSTRUCTION sheets can be printed for the shed.
- **TB-06 (must)** Date of issue.
- **TB-07 (must)** Drawn by, checked by, approved by. Structural sheets (drawbar, chassis, body mounts, anchor points, bed structure, heavy-item mounts) also show the engineer's review status and date.
- **TB-08 (must)** Sheet n of N, sheet size (A3 default) and scale.
- **TB-09 (must)** Projection symbol, units, weld symbol standard and general tolerance note.
- **TB-10 (must)** Material and finish (part drawings) or "See parts list" (assemblies).
- **TB-11 (should)** Calculated mass and the mass schedule ID.
- **TB-12 (should)** CAD model file and model revision the sheet came from.
- **TB-13 (should)** QR code that opens the current revision on the project website, so the builder can check a print is current before cutting.

### 1.3 Dimensioning and tolerances

One coordinate system for the CAD model, drawings, mass schedule, restraint calculations and structural calculations removes a whole class of interface errors.

- **DIM-01 (must)** Project datum: X along the trailer, zero at the coupling ball centre, positive rearward. Y across, zero on the centreline, positive to the left (kerb) side. Z up, zero at the ground with the trailer level at design ride height. Every GA, mass schedule and calculation states it.
- **DIM-02 (must)** Hole patterns that must line up with another part (panel inserts, body mounts, anchor points, hinge and latch fixings) are dimensioned from a shared datum (baseline or ordinate), never chained, and name the mating drawing.
- **DIM-03 (must)** Each feature is dimensioned once. Reference dimensions are in brackets.
- **DIM-04 (must)** Functional fits carry their own tolerance (hinge pins, wheel chock width, door openings, roof-down clearances).
- **DIM-05 (must)** The general tolerance note names the class. Proposed: ISO 2768-m for machined aluminium, ISO 2768-c for cut and folded plate, and ISO 13920 class B for lengths and angles plus class F for straightness and flatness on welded frames (the engineer or fabricator may choose differently). TODO: buy ISO 2768-1 and ISO 13920:2023 and copy the value tables onto the template; the online summaries I found were garbled.
- **DIM-06 (should)** Dimensions measured with a tape in the shed are whole millimetres. Tighter values only where a part is machined or jig-located.
- **DIM-07 (must)** Every clearance that the brief treats as a limit (2,400 mm body width, roof-down interior height, platform underside above the Tuareg's 1,370 mm top plus margin) is a toleranced, checkable dimension on the GA with the margin stated.

### 1.4 Weld symbols and weld notes

Australia has its own weld symbol standard, AS 1101.3, rather than ISO 2553. The current AS 1101.3 dates from 2005, was reconfirmed in 2018, and follows ANSI/AWS A2.4 with a single reference line ([draftsperson.net](https://blog.draftsperson.net/weld-symbols/)). ISO 2553:2019 allows two systems: system A uses a dual reference line (solid and dashed), and system B uses a single reference line and is based on Pacific Rim standards ([ISO 2553:2019 preview, introduction and scope](https://cdn.standards.iteh.ai/samples/72740/08d72a37dd1d4fb6b92ed5119d4b5902/ISO-2553-2019.pdf)). A European drawing in system A puts the other-side weld on the dashed line, which an AWS-trained welder can misread.

- **WLD-01 (must)** Every sheet with welds says "Weld symbols to AS 1101.3".
- **WLD-02 (must)** Every weld has type, size (fillet leg or butt throat, stated which), length and pitch if intermittent, and the all-round symbol where it applies.
- **WLD-03 (must)** Every structural weld note gives the weld category to AS/NZS 1554.1 (SP for drawbar, chassis, axle and spring hangers, anchor points; GP for non-structural brackets) and the inspection: visual on all welds, plus dye penetrant or magnetic particle on drawbar-to-chassis, coupling mount and spring hangers. SP welds have tighter imperfection limits than GP welds; an Australian Steel Institute guide links GP welds to a capped share (about two-thirds) of an SP weld's design capacity (search snippet only, context not read, so confirm with the engineer).
- **WLD-04 (must)** A weld detail sheet shows each structural joint as a large-scale section: joint preparation, size, start and stop positions, wrap-around at RHS corners, and any toe grinding.
- **WLD-05 (must)** Every closed or overlapping section that will be galvanised shows its vent and drain holes with size and position. The Galvanizers Association of Australia (GAA) guide asks for: external vent holes as close as possible to each hollow-section connection; internal vents totalling at least 50% of the connecting section's internal diameter (ideally the full internal diameter), plus a 10 mm external check hole at each internal vent; overlaps of 10,000-40,000 mm2 vented with at least a 10 mm hole and larger overlaps with at least 12 mm; and corner snipes of at least 25 x 25 mm on stiffeners and gussets ([GAA venting and draining guide](https://gaa.com.au/venting-draining-guide/); [GAA hot-rolled welded connections](https://gaa.com.au/venting-and-draining/hot-rolled-welded-connections/)). A galvaniser's poster gives a 10 mm minimum hole, and at least the steel thickness ([GB Galvanizing poster](http://gbgal.com.au/wp-content/uploads/2017/08/GB-Galvanizing-Design-for-Galvanizing-Poster.pdf)). Agree hole positions with the galvaniser before cutting.
- **WLD-06 (must)** No welding after galvanising unless the drawing gives the repair method.

### 1.5 Material, coating and fastener callouts

- **MAT-01 (must)** Every material callout gives form, size, grade and supply standard, for example "RHS 100 x 50 x 3.0, C450L0 to AS/NZS 1163", "Plate 6, grade 250 to AS/NZS 3678", "Angle 50 x 50 x 5, 6061-T6". TODO: confirm the aluminium supply standards (AS/NZS 1734 for sheet and plate, AS/NZS 1866 for extrusions).
- **MAT-02 (must)** Every coating callout gives process and standard ("Hot-dip galvanise after fabrication to AS/NZS 4680").
- **MAT-03 (must)** Every fastener callout gives size and pitch, length, head type, property class (8.8, or A4-70 stainless), coating, washers, nut type, locking method, tightening torque and the lubrication condition the torque assumes.
- **MAT-04 (must)** Where aluminium touches galvanised or stainless steel, the drawing shows and calls out the isolation (washer, tape or sealant).
- **MAT-05 (must)** Every sandwich-panel insert gives insert part number, drilled hole size, potting or bonding adhesive and cure time, and the rated pull-out and shear loads the design uses, with the source of those ratings.

### 1.6 Revision control

ASME Y14.35 is the reference model for drawing revisions ([ASME](https://www.asme.org/codes-standards/find-codes-standards/y14-35-revision-engineering-drawings-associated-documents)). Van's Aircraft runs a simple scheme that suits a builder working from prints: change memos for wording or process changes that do not change the finished configuration (date changes, revision level does not), change notices for dimensional, part or configuration changes (revision level changes), and service bulletins when a step already done must be redone; builders print the new page and destroy the old one ([Van's RV-12 manual, section 1](https://www.vansaircraft.com/wp-content/uploads/2019/01/01_12.pdf)).

- **REV-01 (must)** Every sheet has a revision table: revision, date, description, drawn, checked, approved.
- **REV-02 (must)** Pre-release revisions use letters (A, B, C). The first FOR CONSTRUCTION issue is revision 0, then 1, 2, 3.
- **REV-03 (must)** Changed areas are clouded and tagged with the revision.
- **REV-04 (must)** Each change is classed as a memo (no configuration change), a notice (configuration change), or a rework bulletin (something already built must change). A rework bulletin lists the steps to redo.
- **REV-05 (must)** A change is not closed until every affected document is updated: drawing, parts list, cut list, mass schedule, calculations and build steps. The website shows a "where used" list for every part number.
- **REV-06 (must)** Superseded prints are marked SUPERSEDED and removed from the shed. The website offers only the current revision for printing and keeps history.
- **REV-07 (must)** A change to any structural item after engineer review goes back to the engineer before it is built (see 7.6).

### 1.7 Minimum useful drawing set

Numbering: CT-[group][nn]. Groups follow the build systems, so a number tells you where a part lives.

| No. | Sheet | Content | Main user |
|---|---|---|---|
| CT-000 | Cover and drawing register | Every sheet with current revision and status | All |
| CT-001 | General arrangement (GA) | Plan, side, front and rear views; overall length, 2,400 mm body width, height roof down and up, towball height, axle position, door positions, datum, mass summary | Engineer, inspector |
| CT-002 | Mass and CG schedule | Drawing form of the mass schedule, one table per load case (2.3) | Engineer |
| CT-003 | Compliance sheet | VSB1 items on one page: lamp and reflector positions and heights, number plate, mudguards, plate and VIN locations, coupling, chains, brakes, plug, doors, extinguishers | Inspector |
| CT-1xx | Chassis and drawbar | Reserved (chassis out of scope now) | Engineer, fabricator |
| CT-2xx | Body shell | Panel layout, joint details, insert map, one cut drawing per panel | Builder |
| CT-3xx | Body-to-chassis mounting | Mount positions and details, load path, isolation, sealing | Engineer, builder |
| CT-4xx | Garage | Floor, anchor layout, wheel chocks, ramp, side door, restraint arrangement per bike, ventilation | Engineer, builder |
| CT-5xx | Bed platform | Structure, supports, fixings, load path, any lift mechanism | Engineer, builder |
| CT-6xx | Furniture and cabinetry | Carcasses, fixings, latches, drawer stops | Builder |
| CT-7xx | Electrical | 12 V and 230 V schematics, cable routes and support points, fuse and isolator schedule | Electrician, inspector |
| CT-8xx | Gas and fuel safety | LPG (if fitted), garage vents, detectors, extinguishers | Gasfitter, engineer |
| CT-9xx | Water | Tanks, mounts, routing | Builder |
| CT-Wxx | Weld details | Large-scale weld details called up from assemblies | Fabricator, engineer |
| CT-Pxx | Parts lists | One per assembly | Builder |
| CT-Cxx | Cut lists | One per stock type | Builder |
| CT-Txx | Templates | 1:1 printable templates for cut-outs and drilling | Builder |

- **SET-01 (must)** CT-001, CT-002 and CT-003 exist before the first engineer review.
- **SET-02 (must)** Every assembly balloons every part, and every balloon matches a parts-list line.
- **SET-03 (must)** Every cut or drilled part has a part drawing, a cut-list line or a template. "Make to suit" is allowed only if the drawing says how the part is measured and the result recorded.

### 1.8 Parts lists, cut lists and templates

- **BOM-01 (must)** Parts list columns: item, part number, description, material and standard, quantity, unit mass, total mass, supplier and supplier part number, mass schedule ID, notes.
- **CUT-01 (must)** Cut list columns: part number, stock (form, size, grade), cut length, quantity, end cuts (square, mitre angle, cope), holes with positions from a named end, edge finish, and the stock length each part is nested in.
- **CUT-02 (should)** Parts are nested to stock lengths so offcuts are planned; longest parts are cut first.
- **TPL-01 (must)** Every template prints at 1:1 with a 100 mm scale bar in both directions, registration marks for tiling A4 or A3 sheets, and drawing number and revision on every tile. The build step tells the builder to check the scale bar with a rule before use.

### 1.9 Sheet checklist (website check before FOR CONSTRUCTION)

1. TB-01 to TB-10 complete.
2. Projection symbol, units, "Do not scale", weld symbol standard and tolerance note present.
3. Revision table updated and changes clouded.
4. Project datum shown.
5. Every part ballooned and in the parts list.
6. Material, coating and fastener callouts complete (MAT-01 to MAT-05).
7. Welds symbolised with size, category and inspection (WLD-01 to WLD-04).
8. Vent and drain holes shown on galvanised parts (WLD-05).
9. Interfaces dimensioned from datum and cross-referenced to the mating drawing.
10. Checked by a second person, or for a one-person project checked at least 24 hours later against this list.
11. Engineer review status recorded on structural sheets.

---

## 2. What the engineer needs from the builder

### 2.1 The approval path that shapes the documents

- Since 1 July 2023 every new trailer needs an entry on the Register of Approved Vehicles (RAV) to be registered. Small-volume builders apply for a Concessional RAV entry through the Commonwealth ROVER portal and receive the VIN with it ([TfNSW AIS Notice 41](https://freight.transport.nsw.gov.au/system/files/media/documents/2024/AIS-Notice-41-Inspecting-Concessional-Trailers.pdf)). NSW describes these builders as making fewer than four trailers in 12 months ([TfNSW VIB 78](https://www.bts.nsw.gov.au/system/files/media/documents/2023/VIB-78-Inspecting-RVSA-Trailers.pdf)); WA, NT and Victorian pages say four or fewer (search snippets only, see "Could not verify").
- VSB1 Revision 6 (September 2024) summarises the ADR requirements for trailers up to 4.5 t ATM. Where it disagrees with the ADRs, the ADRs take precedence ([VSB1 Rev 6, 1.2](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf); read from a mirror because infrastructure.gov.au would not load here).
- ATM and GTM are builder ratings, and VSB1 says both must be developed through engineering calculations considering chassis strength, wheel, axle and tyre ratings, and towing stability (VSB1 Rev 6, p. 9). Tare includes all fitted equipment ready for service, but caravan water and waste tanks are not counted as fluid reservoirs, so water is payload (p. 8). ATM minus GTM is the towball download (p. 9).
- The vehicle plate shows make ("Concessional trailer" is allowed for a home-built trailer), VIN, ATM, GTM and tare, embossed, indented, etched or engraved in block letters at least 2.5 mm high, and must match the RAV entry (VSB1 Rev 6, 13.1.1). NSW inspectors also look for trailer model and date of manufacture (VIB 78, rule 221.04).

**State differences that change what must be documented**

| State | What changes | Source |
|---|---|---|
| NSW | A concessional low-ATM trailer needs a TfNSW Identity Approval before the inspection report is issued. The package: form 5703, four photos (each side, front, rear), a photo of the vehicle plate, a photo of the drawbar, a weighbridge ticket showing tare and VIN, and receipts proving where the materials came from. The examiner design-checks against VSB1 Rev 6 and caps GTM at the lowest of the tyre load capacities, coupling rating, safety chain rating and brake rating, and ATM at the lower of coupling and chain rating. Disputed ratings go to a VSCCS licensed certifier. | [VIB 78](https://www.bts.nsw.gov.au/system/files/media/documents/2023/VIB-78-Inspecting-RVSA-Trailers.pdf), rules 221.04 and 361.03 |
| QLD | VIN by application through the Road Vehicle Regulator (ROVER) system, then a pre-registration identity inspection. Trailers over 750 kg ATM or with more than one axle need a pre-registration inspection, done as a self-assessment on TMR's trailer inspection sheet. A gas inspection certificate less than 3 months old is needed if gas is fitted. | [qld.gov.au, Register your trailer or caravan](https://www.qld.gov.au/transport/registration/register/caravan) |
| QLD | Professional engineering services carried out in or for Queensland must be provided by a Registered Professional Engineer of Queensland (RPEQ) or under an RPEQ's direct supervision. | [BPEQ](https://bpeq.qld.gov.au/) (bot check); [Qld Building Newsflash 465](https://www.housing.qld.gov.au/__data/assets/pdf_file/0015/4605/newsflash-465.pdf) (bot check) |
| VIC | TODO. Transport Victoria pages block automated access. Search snippets say to get a VASS signatory's approval letter if unsure whether a design or change complies with VSB1. | [VASS page](https://transport.vic.gov.au/road-and-active-transport/business/vehicle-assessment-signatory-scheme) (bot check) |

- **REG-01 (must)** Keep a build evidence folder from day one: dated photos of each stage, material and component receipts, component type approval numbers (coupling, brakes, chains, lamps), weighbridge tickets. NSW asks for receipts and photos, and the same folder serves every state. This mirrors the FAA's guidance for amateur-built aircraft, which accepts comprehensive builder's logs with photographs and receipts for materials as evidence of construction ([FAA AC 20-27G](https://faa.gov/documentLibrary/media/Advisory_Circular/AC_20-27G.pdf)).
- **REG-02 (must)** Photograph the drawbar, VIN stamping location and plate before and after galvanising or paint.

### 2.2 VSB1 numbers the documents must show

Formulas are from VSB1 Rev 6. Worked figures assume ATM = 3,500 kg (the Cayenne's braked towing limit) and must be recalculated once the real ATM is set.

| Item | VSB1 Rev 6 requirement | At ATM 3,500 kg | Section |
|---|---|---|---|
| Drawbar, longitudinal tension and compression | 1.5 x 9.81 x ATM held 10 s, no harmful deformation, cracks or separation | 51.5 kN | 9.1, 14.2.1 |
| Drawbar, transverse | 0.5 x 9.81 x ATM | 17.2 kN | 9.1 |
| Drawbar, vertical (rigid drawbar) | 0.5 x 9.81 x ATM | 17.2 kN | 9.1 |
| Drawbar by calculation | Only by "approved calculation procedures" (approved by the department) that consider strength and fatigue. Tests must be done at a facility approved under section 111 of the Rules | n/a | 9.1, 14 |
| Safety chains | Two chains above 2,500 kg ATM, to AS 4177.4 (3,500 kg chain marked 4177-35) | 2 chains | 9.2.1 |
| Each chain attachment point | Longitudinal 9.81 x ATM; vertical 0.5 x 9.81 x ATM | 34.3 kN; 17.2 kN | 9.2.2, 14.2.2 |
| Coupling | AS 4177.3, 3,500 kg rating for a 50 mm ball, or an off-road coupling with a component type approval number | n/a | 9.3 |
| Towball height | Tow vehicle ball adjustable 350-460 mm loaded; trailer designed level within that range | n/a | 9.3.2 |
| Brakes | Over 2,000 kg GTM: brakes on all wheels and breakaway brakes held at least 15 min | n/a | 8.2 |
| Running clearance | At least 100 mm, unladen | n/a | 5.4 |
| Width | Measured across the body including mudguards, side racks and awnings (definition, ch. 2). Light vehicle limit 2.5 m ([LRG for Light Vehicles, p. 9](https://media.nrspp.org.au/wp-content/uploads/2021/11/06005924/Load-Restraint-Guide-for-light-vehicles-2018.pdf)) | n/a | 2, 5.2 |
| Number plate | No part above 1,300 mm; lit | n/a | 3.1 |
| Wiring | Supported at least every 600 mm, joints insulated, grommets through metal, earth return wire | n/a | 7.1 |
| Plug | 7 or 12 pin to AS 4177.5 | n/a | 7.2 |
| 230 V installation | VSB1 cites AS/NZS 3001:2008; AS/NZS 3001.2:2022 now covers RV installations (see 5.3) | n/a | 7.3 |
| Caravan doors | Outward-opening or sliding; at least one on the left side or rear, usable as a normal door | n/a | 13.2.1 |
| Fire extinguishers | 1A:5B, one for single-compartment and two for multi-compartment caravans; fire blanket and smoke alarms recommended, smoke alarms required in some states | n/a | 13.2.2 |
| LPG | Caravan LPG code and AS/NZS 5601 | n/a | 13.2.4 |

Consequences for this design:

- If the garage counts as a separate compartment, VSB1 asks for two extinguishers. Ask the inspector early.
- The bike door is in a side wall. If it is on the right (road) side, a left-side or rear door is still needed (13.2.1). A left-side bike door also keeps loading off the road side.

### 2.3 Mass schedule

The mass schedule sets ATM, GTM, axle and tyre ratings and towball download, and proves the plated tare is true. It is the most useful single document for the engineer.

- **MASS-01 (must)** One line per item: ID, item, system, drawing number, quantity, unit mass, total mass, mass source (weighed, spec sheet URL, calculated from geometry, estimate), maturity, and the item's CG as X, Y, Z in the project datum (DIM-01).
- **MASS-02 (must)** Load-case flags on every line: tare, bike 1, bike 2, water, food and gear, removable items.
- **MASS-03 (must)** Outputs per load case: total mass, axle group load, towball load, CG X, Y, Z, and margin against ATM, GTM, axle rating, sum of tyre ratings, coupling rating, chain rating, the Cayenne's 3,500 kg towing limit and its towball limit (about 140 kg per the brief).
- **MASS-04 (must)** Towball load by moments about the axle group centre: ball load = sum of m_i x (x_axle - x_i) / x_axle, with X rearward from the ball. Every load case shows it; none may be negative or above the tow vehicle limit.
- **MASS-05 (must)** Load cases at minimum: tare; tare plus both bikes fully fuelled (owner's figures 175 kg and 206 kg); each bike alone in each garage position; full ATM; bikes out at camp; the most nose-heavy and most tail-heavy arrangements the owner would actually use.
- **MASS-06 (must)** Every line carries a maturity code and a growth allowance until weighed. Aerospace practice (AIAA S-120A) grades masses as estimated, calculated or actual and applies the allowance at component level ([NASA presentation on S-120 mass growth allowance](https://ntrs.nasa.gov/api/citations/20130014267/downloads/20130014267.pdf)). Proposed project allowances, to be agreed with the engineer: estimate +20%, calculated from a drawing +7%, weighed 0%. These percentages are a proposal, not taken from the standard.
- **MASS-07 (must)** Every part is weighed before fitting and its line becomes "weighed". Whole-trailer weights are taken at milestones on a weighbridge (axle group and coupling separately) and compared with the schedule. A difference over 2% is explained before work continues.
- **MASS-08 (must)** Keep the final weighbridge ticket showing tare and VIN (NSW requires it, VIB 78).

**Towball share.** TfNSW says the tow ball mass capacity must not be exceeded and should be measured with a ball weight scale ([TfNSW caravans](https://www.transport.nsw.gov.au/roadsafety/road-users/drivers/caravans)). The common Australian rule of thumb of about 10% of loaded trailer mass appears in blogs, but I found no official source for it. About 140 kg is only 4% of a 3,500 kg ATM, so the engineer must see towball load and stability together. This is a design issue as much as a documentation one.

**Measuring CG height.** Weigh the coupling load with the trailer level (F0), then with the coupling raised so the trailer tilts nose-up by angle t (Ft). With L the horizontal distance from coupling to axle centre and W the total weight, CG height above the axle centre is h = (F0 - Ft) x L / (W x tan t). Do it at two angles and record both. This comes from taking moments about the axle; ask the engineer to accept the method before relying on it.

### 2.4 Load cases and dynamic factors

VSB1 gives only the drawbar and chain forces above and requires drawbar calculations to cover strength and fatigue. It gives no off-road load factors, and I found no Australian standard that does. Two indicative sources:

- The Australian Road Transport Suppliers Association says chassis rails, crossmembers and subframes of hard-working trucks and trailers should have a design factor of safety of 3 or more, so that bump stresses stay below yield and do not cause fatigue cracking ([ARTSA technical article, 2016](https://artsai.wildapricot.org/resources/Documents/2016_07.pdf)).
- An off-road trailer maker's blog quotes 1.8-2.8 g at 12-18 Hz on corrugations, 2.5-4.2 g spikes on rubble and 6-12 g on step impacts ([BlackSeries](https://blackseries.net/blogs/news/off-road-trailer-chassis-guide-suspension-frame-design)). It gives no test method or source, so treat these as indicative only.

Proposed load cases for the engineer to accept or change:

| ID | Case | Proposed basis |
|---|---|---|
| LC1 | Static at ATM | 1 g vertical |
| LC2 | Vertical bump | Factor set by the engineer; indicative 3 g on structure (ARTSA factor of safety of 3), higher for local fixings |
| LC3 | Braking | 0.8 g forward plus 1 g vertical |
| LC4 | Cornering | 0.5 g lateral plus 1 g vertical |
| LC5 | Chassis twist | One wheel raised or dropped by a height the engineer sets |
| LC6 | Drawbar | VSB1 9.1 forces |
| LC7 | Cargo, furniture and heavy items | NTC performance standards: 0.8 g forward, 0.5 g rearward, 0.5 g sideways, 0.2 g upward |
| LC8 | Recovery and jacking | Point loads at the stated jacking and recovery points |
| LC9 | Bed in use | Two occupants, mass and dynamic factor set by the engineer |
| LC10 | Fatigue | Stress ranges at each welded detail from LC2 to LC4 or measured data, checked against a fatigue detail category (AS 4100 section 11, TODO confirm) |

- **LOAD-01 (must)** The design basis lists every load case with factor, direction, combination and source.
- **LOAD-02 (should)** Log accelerations on the chassis and body during early trips on the owner's intended roads, and feed the results back into LC2 to LC4 and LC10.

### 2.5 Material specs and connection details

- **CON-01 (must)** A material schedule: every structural material with grade, supply standard, and the yield and ultimate strengths used, with source.
- **CON-02 (must)** A connection detail for every load path: drawbar to chassis, axle and suspension mounts, body to chassis, bed platform to body, anchor points to floor and chassis, heavy items (batteries, water, fridge) to structure. Each shows members, welds or bolts, edge distances, plates or spreaders, isolation and sealing.
- **CON-03 (must)** For sandwich panels: the panel maker's data sheet (skin and core properties), insert type and rated loads, and the test or data that supports them.

### 2.6 How calculations should be presented

- **CALC-01 (must)** One calculation package: cover and revision table, scope, design basis (standards, load cases, materials, factors), assumptions, a summary table of every check with utilisation (demand over capacity, 1.0 or less), then the detailed checks.
- **CALC-02 (must)** Every check names the drawing number and revision it covers, and every structural drawing names its calculation.
- **CALC-03 (must)** SI units, formula before numbers, so any line can be checked by hand.
- **CALC-04 (must)** Finite element results show model, mesh, supports, loads, material, software and version, stress plots with a stated scale, and a hand check that reactions equal applied loads.
- **CALC-05 (must)** The engineer's report lists what was reviewed (document numbers and revisions), the ratings accepted (ATM, GTM, tare basis), conditions, and the engineer's registration (RPEQ if the work is done in or for Queensland).

---

## 3. Cargo restraint: method and how to document it

Another worker sizes the straps. This section covers method and documentation only. Page numbers are the guide's printed page numbers.

**Performance standards.** A restraint system must withstand, separately, 0.8 g forward, 0.5 g rearward and 0.5 g lateral, plus 0.2 g vertical if friction or limited vertical movement is relied on ([NTC Load Restraint Guide 2018, pp. 4 and 241](https://www.transafewa.com.au/wp-content/uploads/2022/08/Load-Restraint-Guide-2018.pdf)). The light vehicle edition gives the same figures as 80%, 50%, 50% and 20% of load weight, and applies to trailers up to 4.5 t ([LRG for Light Vehicles 2018, p. 2](https://media.nrspp.org.au/wp-content/uploads/2021/11/06005924/Load-Restraint-Guide-for-light-vehicles-2018.pdf)). NHVR now hosts the guide ([NHVR](https://www.nhvr.gov.au/road-access/loading/load-restraint-guide)).

**Method rules from the guide**

- Restraint is tie-down (friction from clamping) or direct (containing, blocking, attaching). Attaching suits loads on wheels (light guide p. 11).
- If blocking or containing is used without tie-down that resists 0.2 g upward, friction must be left out of the capacity, because a bump breaks friction contact (LRG 2018, p. 250).
- Direct lashing angle effect = horizontal distance in the direction of restraint divided by lashing length. A slope of 1 in 2 (about 25 degrees) gives 90% effectiveness (pp. 252-253).
- Tie-down angle effect = height divided by lashing length; minimum effective angle 35 degrees; tie-down lashings must clamp with at least 20% of load weight (p. 245; light guide p. 12).
- Paired direct lashings should match in type, length and angle; mixing stiffness can overload one lashing first (p. 254).
- The guide's worked example assumes the opposing lashings go slack, and sets lashing tension = restraint force per lashing divided by angle effect (p. 256).
- Lashing tension must not exceed the manufacturer's lashing capacity (p. 245).
- Anchor points should be designed for the minimum breaking load of the lashing fitted to them (p. 201).
- A load can tip forward if its length along the vehicle is under 80% of its height, or sideways if its width across the vehicle is under 50% of its height (light guide p. 6).

**Bike-specific point.** With the bikes standing across the trailer, the trailer's 0.8 g forward and 0.5 g rearward cases act sideways on each bike, the direction in which a motorcycle is least stable and its suspension gives no help. The calculation must resolve the four performance-standard directions into each bike's own axes and show every lashing's contribution in each.

**What the restraint document contains** (adapted from the LRG certification contents, p. 238, and template, p. 239)

- **LR-01 (must)** Name and revision of the restraint system, date, author, reviewing engineer.
- **LR-02 (must)** Load per bike: mass (owner's figures), CG in the project datum, tie-down points used on the bike.
- **LR-03 (must)** Vehicle: floor surface and its friction value, anchor type, rating and fixing into structure.
- **LR-04 (must)** Equipment: strap or chain type, width, lashing capacity, tensioner, assumed pre-tension, soft loops, chocks.
- **LR-05 (must)** Plan and elevation of the loaded arrangement with each lashing's end coordinates, so angle effects can be checked from the drawing.
- **LR-06 (must)** A table per direction (forward, rearward, left, right, upward): required force, each lashing's contribution (capacity x angle effect), blocking contribution, friction contribution (zero unless tie-down resists 0.2 g up), total and margin.
- **LR-07 (must)** Anchor check: each anchor rated for its lashing's minimum breaking load, with the load path through floor, inserts and chassis calculated.
- **LR-08 (must)** Operating instructions: loading order, strap routing, tension check, re-check intervals on the first trip and after rough sections, strap replacement criteria.
- **LR-09 (should)** Pull test of each anchor type in a sample of the real floor panel, with the result recorded.

---

## 4. Common failure modes and the design rules that prevent them

Public engineering evidence on Australian caravan failures is thin. The best documented case I found is an independent engineer's 2011 report tabled in the Queensland Parliament on one maker's caravans: floors and superstructure were deformed, chassis had bent along the length fore and aft of the axle group with one measured chassis twist, and bending at the front changed the drawbar angle and so the towball and axle loads. The author judged chassis reinforcement a superficial repair ([Qld Parliament tabled paper 5312t6458](https://www.parliament.qld.gov.au/Work-of-the-Assembly/Tabled-Papers/docs/5312t6458/5312t6458.pdf)). The lesson is that chassis bending and twist stiffness drive body damage.

| Failure mode | Typical cause | Design rule |
|---|---|---|
| Chassis bending and drawbar cracking | Chassis that yields in bending; fatigue at abrupt stiffness changes, weld toes on tension flanges, holes near peak stress | **FAIL-01 (must)** Chassis bending and twist stiffness are stated in the calcs; drawbar runs back to a crossmember or past the front hanger; gusset ends tapered; no transverse welds or holes in tension flanges at peak moment; each welded detail has a fatigue category; ARTSA factor of safety of 3 used as a starting point (2.4) |
| Spring hanger and axle mount cracking | Concentrated loads into thin rail walls | **FAIL-02 (must)** Hanger loads spread through the full rail section with plates or sleeves |
| Body-to-chassis mounts cracking, bolts loosening | Chassis twist forced into a stiff body; bolts relaxing | **FAIL-03 (must)** Drawing states whether the body is rigidly mounted or isolated; mounts designed for LC5; spreader plates and bonded hardpoints in panels; prevailing-torque nuts; a re-torque step after the first rough trip |
| Cabinetry and fixings shaking loose on corrugations | Screws into ply or foam, staples and glue only, no positive latches | **FAIL-04 (must)** Every fixing into a panel goes into a rated insert or through-bolt; carcasses glued and mechanically fixed; every door and drawer has a positive latch; heavy items restrained to LC7 |
| Dust ingress | Towing on dirt roads creates low pressure inside the van that draws dust through vents and gaps ([Dust Mate](https://www.dustmate.com.au/)); filtered fans pressurise the interior to stop it ([CaraFan](https://carafan.com.au/)) | **FAIL-05 (must)** Every penetration sealed and drawn; filtered positive pressurisation of the living area designed in; garage-to-living door sealed (one Australian toy hauler maker uses a triple-sealed door between garage and cabin to keep dust and mud out, [Titanium Caravans](https://titaniumcaravans.com.au/toy-hauler-caravans/)); dust test on a dirt road before final fit-out |
| Water ingress | Failed sealant at joints, hatches and penetrations | **FAIL-06 (must)** Every penetration has a detail with sealant and mechanical fixing; drainage paths drawn |
| Bed and furniture fixings failing | Occupant and corrugation loads | **FAIL-07 (must)** Bed platform designed for LC9 and LC2 with its load path drawn |
| Wiring chafe and connector failure | Vibration | **FAIL-08 (must)** VSB1 7.1 support at 600 mm or less, grommets, strain relief at every connector |

---

## 5. Fuelled motorcycles under a sleeping area

### 5.1 What the US RV standard says

NFPA 1192 is the US recreational vehicle fire and life safety standard ([NFPA](https://www.nfpa.org/product/nfpa-1192-standard/p1192code)). It is paywalled. From NFPA's published revision report for the 2018 edition: an RV with a permanent wall of separation between the cargo area and the living area must carry an additional listed extinguisher rated at least 10-B:C in the "special transportation area", within 610 mm (24 in) of the exterior door serving it; a towable without such a wall must have its required extinguisher rated at least 10-B:C ([NFPA 1192 second revision report, revisions 3 and 6.4.6.5.1](https://docinfofiles.nfpa.org/files/AboutTheCodes/1192/1192_A2017_REC_AAA_SRReport.pdf)). The current edition is 2026 ([NFPA development page](https://www.nfpa.org/codes-and-standards/nfpa-1192-standard-development/1192)). TODO: the standard's other cargo-area rules (ventilation, detectors, fuel stations) and RVIA's position could not be read.

### 5.2 Closest Australian rules: LPG compartments

There is no Australian rule for petrol in a caravan garage that I could find. The nearest is the treatment of LPG, which is also heavier than air. A South Australian gas bulletin applying AS/NZS 5601.2:2020 to motorhomes requires a cylinder compartment that is reached only from outside, holds only cylinders and their equipment, and prevents gas vapour entering the vehicle; a 25 mm drain at the base, or high and low vents in the door of at least 5,000 mm2 each per cylinder; drain outlets at least 1 m from openings and 1.5 m from ignition sources unless offset vertically; and cylinders secured against 4 times their filled weight in any direction ([SA Gas Bulletin 26](https://www.energymining.sa.gov.au/__data/assets/pdf_file/0005/922964/Gas-Bulletin-26-Conversion-of-buses-and-trucks-to-motor-homes.pdf)). AS/NZS 5601.2:2020 is the current edition, enforced in Victoria from 1 April 2021 apart from quick-connect changes ([Energy Safe Victoria amendments briefing](https://www.energysafe.vic.gov.au/sites/default/files/2022-12/ASNZS5601.2_amendments_pres.pdf)). New Zealand's regulator says cylinders should sit in an enclosure that vents escaping gas away from the cabin and ignition sources ([WorkSafe NZ](https://www.worksafe.govt.nz/managing-health-and-safety/consumers/safe-living-with-gas/recreational-safety/gas-safety-for-caravans-and-motorhomes/)).

### 5.3 Electrics

AS/NZS 3001.2:2022 replaced AS/NZS 3001:2008 for connectable installations including caravans, and covers wiring, inverters, solar and batteries; suppliers report it requires batteries to comply with AS IEC 62619 ([Redarc FAQ](https://www.redarcelectronics.com/nz/discover/new-caravan-standards/); [Accuris catalogue](https://store.accuristech.com/standards/as-nzs-3001-2-2022?product_id=2506083), bot check). VSB1 Rev 6 still cites the 2008 edition, so ask the inspector which edition they will check. TODO: whether AS/NZS 3001.2 restricts electrical equipment near fuel or gas spaces.

### 5.4 What makers do

Australian toy haulers seal the garage from the cabin ([Titanium Caravans TS1](https://titaniumcaravans.com.au/toy-hauler-caravans/)) and provide integrated tie-down points in a heavy-duty garage floor ([Jayco Basestation](https://www2.jayco.com.au/range/toy-haulers/basestation-toy-hauler)). Neither page gives ventilation or detection details. European makers were not researched (see "Could not verify").

### 5.5 Rules for this trailer

These rules apply the sources above by analogy. Where a rule is a project choice rather than a quoted requirement, it says so.

- **GAR-01 (must)** The garage has permanent low-level vents to outside, because petrol vapour, like LPG, is heavier than air. Size them with the engineer; the LPG compartment figure of 5,000 mm2 per opening per cylinder is a floor, not a design value.
- **GAR-02 (must)** The barrier between garage and sleeping area is continuous, sealed and has no openings at low level. Every penetration through it is drawn and sealed.
- **GAR-03 (must)** No ignition sources (switches, relays, chargers, heaters, inverters) in the lowest 500 mm of the garage. Project choice by analogy with the 500 mm vertical offset for LPG drain outlets.
- **GAR-04 (must)** An extinguisher rated for petrol fires within 610 mm of the garage's exterior door (NFPA 1192 practice), plus the VSB1 extinguisher or extinguishers in the living area.
- **GAR-05 (must)** Smoke alarm and carbon monoxide alarm in the sleeping area; a petrol vapour detector at low level in the garage; an LPG detector if LPG is fitted.
- **GAR-06 (must)** No engine running inside the garage; fuel taps off and caps closed for transport. Written in the operating manual and on a placard inside the garage door.
- **GAR-07 (must)** The operating manual says whether people may sleep with fuelled bikes inside. If yes, the drawings show how vapour is kept out of the sleeping area in still air with the trailer closed.

---

## 6. How the best build manuals are designed

**Evidence on instruction design.** Agrawala and colleagues derived design principles for assembly instructions from cognitive psychology studies: group parts the way people think of sub-assemblies; work in two levels (significant parts, then their fasteners); use action diagrams that separate the new parts from the existing assembly and show where they attach with guidelines, which beat plain structural diagrams for furniture; make every new part visible in its step, with enough of the earlier assembly visible for context ([Agrawala et al., SIGGRAPH 2003](http://vis-ucb-maneesh.stanford.edu/papers/assySiggraph/assembly.pdf)). In a follow-up user study, instructions built on these principles cut furniture assembly time by an average of 35% and errors by 50% ([Heiser et al., CHI 2004](http://vis-ucb-maneesh.stanford.edu/papers/assyDesignPrinciples/assemblyuserstudy.pdf)). The same paper notes that LEGO mostly uses structural diagrams because LEGO parts all fasten the same way.

**IKEA.** Parts that need special attention are marked with a pointing finger or an "i", or drawn enlarged ([IKEA customer service](https://www.ikea.com/kr/en/customer-service/knowledge/articles/360gf9eg-0b0e-4815-9342-348g3gg579g6.html)). A documentation consultancy notes IKEA renders every step from one unchanging viewpoint so the reader stays oriented ([Instrktiv](https://instrktiv.com/en/ikea-manual/), secondary source).

**Van's Aircraft.** Older RV kits pair large drawings with a separate construction manual; newer kits (RV-10 to RV-14) break the build into steps with nearly every step illustrated, drawings and instructions combined on 11 x 17 in sheets ([Van's plans and manuals](https://www.vansaircraft.com/plans-manuals/)). A common section covers standard construction practice and hardware for all models ([Van's section 5](https://www.vansaircraft.com/wp-content/uploads/2019/01/RV-ALL_05.pdf)). The model manual assumes the builder knows basic practice and points to FAA AC 43.13 and other handbooks, and it is treated as part of the aircraft's documentation, defining its exact configuration ([Van's RV-12 section 1](https://www.vansaircraft.com/wp-content/uploads/2019/01/01_12.pdf)).

**Manual structure for this build**

- **MAN-01 (must)** Chapter 0: standard practices used throughout (fastener torques, insert bonding, sealing, wiring, weld inspection, galvanising repairs). Steps refer to it instead of repeating it.
- **MAN-02 (must)** One chapter per system in build order, each starting with its drawings, parts list, cut list, tools and consumables.
- **MAN-03 (must)** The manual and build log stay with the trailer as its configuration record.

**Every build step has**

- **STEP-01 (must)** One action, verb first ("Drill", "Bond", "Torque").
- **STEP-02 (must)** Parts used (part number, quantity, picture), tools, consumables, and the drawing number and revision it comes from.
- **STEP-03 (must)** An action diagram: new parts visible, pulled out from the assembly with guidelines to where they attach, from the same viewpoint as the previous step where possible, with new parts highlighted.
- **STEP-04 (must)** Torque and lubrication condition for every fastener, and a tick box for the torque stripe.
- **STEP-05 (must)** A check step before every step that cannot be undone (cut, drill, bond, weld, seal): measure, compare with the drawing, tick.
- **STEP-06 (must)** Hold points: nothing is covered (wiring, inserts, welds, sealant, backing plates) until it is inspected, photographed and ticked. Photos go into the build log (REG-01).
- **STEP-07 (must)** Attention markers ("i" or pointing finger) on steps with a known trap, such as handed parts or orientation.
- **STEP-08 (should)** Sequenced to avoid rework: inserts, backing plates, conduits and draw wires go in before panels close; trial-fit before bonding; weigh before fitting (MASS-07).

---

## 7. Design process for a one-off vehicle

NASA's Systems Engineering Handbook is a free, recognised reference for staged design reviews, requirements, interface management and configuration control ([NASA](https://www.nasa.gov/reference/systems-engineering-handbook/)). The steps below are a scaled-down version for a one-person build.

- **PROC-01 (must) Requirements.** A numbered list (dimensions, masses, use cases, regulatory limits from 2.2), each with how it will be verified (measure, weigh, calculate, test, inspect).
- **PROC-02 (must) Mass budget.** Budget per system against ATM and towball limits, with maturity and growth allowance (MASS-06), updated whenever a design changes and checked against weighed parts (MASS-07).
- **PROC-03 (must) Full-size mock-ups.** Garage and bed mocked up in cheap material with both bikes loaded through the real door opening, before any panel is ordered. Check loading, restraint access, platform clearance and roof-down headroom.
- **PROC-04 (must) Engineer reviews.** Concept review (layout, mass schedule, load cases, regulatory path, what is calculated versus tested) and detail review (FOR REVIEW drawings and calcs). Agree the evidence path for the drawbar before detail design (VSB1 9.1).
- **PROC-05 (must) Interface control.** An interface list: every fixing into a panel (position, insert type, load, mating part) is fixed, drawn and frozen before panels are ordered. Panel cut drawings come from the interface list, not the other way round.
- **PROC-06 (must) Service access.** Every serviceable item (bearings, brakes, wiring junctions, fuses, pumps, tank fittings, detector batteries) can be reached without removing structure or bonded panels, and the drawing shows how.
- **PROC-07 (must) Change control.** After a review, every change follows REV-04 to REV-07.

---

## Appendix: records the website should hold

| Record | Required fields |
|---|---|
| Drawing sheet | Number, title, revision, status, date, drawn, checked, approved, engineer status, sheet size, scale, model reference, linked calcs, linked steps |
| Part | Part number, description, material and standard, finish, mass and maturity, supplier part number, where used |
| Mass line | MASS-01 fields plus load-case flags |
| Calculation check | ID, drawing and revision checked, load case, demand, capacity, utilisation, status |
| Build step | Step ID, action, parts, tools, consumables, drawing references, torque values, check results, photos, date, signature |
| Change | Type (memo, notice, rework), description, affected documents, engineer review needed, closed date |

---

## Open questions

- Will the engineer accept calculations for the drawbar, given VSB1 9.1 limits calculation to "approved calculation procedures", or must it be tested at an approved facility? Or will a component type approved drawbar or chassis be bought?
- Is the trailer a caravan for VSB1 13.2 (doors, extinguishers), and is the garage a separate compartment?
- Which state will it be registered in? That decides the inspection paperwork and whether an RPEQ is needed.
- What off-road load factors and twist case will the engineer use?
- Will people ever sleep with fuelled bikes inside? The answer changes the garage ventilation design.
- With a towball limit of about 140 kg, what ATM can the engineer accept for towing stability?

## Could not verify

- infrastructure.gov.au (official VSB1 page) would not load from this machine; VSB1 Rev 6 was read from a mirror copy.
- Transport Victoria, NT Government, BPEQ, iso.org, ANSI webstore, Accuris, Intertek Inform and ACM pages returned bot checks to automated requests. Their claims here come from search-result snippets.
- The four-or-fewer trailer threshold (WA, NT, Victoria) is from search snippets only.
- Paywalled standards were not read: AS 1100, ISO 128, ISO 129, ISO 2768, ISO 13920, AS 1101.3, AS/NZS 1554.1, AS/NZS 4680, AS/NZS 5601.2, AS/NZS 3001.2, NFPA 1192, AIAA S-120A.
- NFPA 1192's ventilation and detection rules for cargo areas, and RVIA's position, were not found.
- European toy hauler practice and marine petrol vapour practice were not researched in this run.
- The 10% towball rule of thumb has no official source that I found.
- The off-road acceleration figures come from a maker's blog without a stated method.

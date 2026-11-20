# 11: Chassis and drawbar design basis

Note added 20 Nov 2026, after the chassis design (CHASSIS.md). Two of this report's numbers are wrong, and the design uses the corrected ones. The composite rail's second moment is 11.6 x 10⁶ mm⁴, not 14.2 x 10⁶, so its section modulus is 90.7 x 10³ mm³ at the bottom, not 104 x 10³. The moment diagram in section 3.1 placed 3,151 kg for TC2, not the 3,351 kg the model then held: the missing 200 kg was the water, which the model adds through the tank positions. The frame analysis takes every load from the full case data. CHASSIS.md compares its results with this report's hand numbers. The section table is `data/chassis/sections.yaml` in the repository.

Research report, 20 Nov 2026. It gives the chassis designer the requirements, section data, load cases and acceptance criteria for the camper trailer chassis (drawing group CT-1xx), and recommends a solution for the floor beside and over the axles and for the drawbar. The section table is in `chassis-sections.yaml`, published as `data/chassis/sections.yaml`.

Positions are in the project datum (X rearward from the ball, Z up from the ground at design ride height, mm). Across the trailer this report gives magnitudes from the centreline and the words kerb side and road side, because the sign of Y is being changed in the repo. Inputs come from TRAILER.md revision D and reports 02, 06, 08 and 09. Numbers marked "estimate" are mine and need the engineer's acceptance.

Terms used throughout:

- Raiser: a second steel section welded on top of each main rail to lift the floor above the tyres.
- Outrigger: a short member that runs from the rail or raiser out to the body edge to support the floor edge and the wall.
- Composite rail: the main rail and its raiser welded together continuously so they bend as one deep section.
- FAT class: the IIW fatigue class of a welded detail, the stress range in MPa it survives for 2 million cycles. A higher FAT is a better detail.
- CAFL: constant amplitude fatigue limit, the stress range below which a detail is taken to have unlimited life (IIW puts it at 10 million cycles, 0.585 x FAT).
- SP and GP: the structural purpose and general purpose weld categories of AS/NZS 1554.1.
- HDG: hot-dip galvanising after fabrication to AS/NZS 4680.

---

## Recommendation

### Material, welding and protection

- Steel: cold-formed RHS and SHS to AS/NZS 1163 grade C450L0 for every primary member, bought as Austube Mills C450PLUS black tube (fy 450 MPa, fu 500 MPa). Cruisemaster's minimum at the suspension is C350L0, 50 mm wide sections and a 3 mm rail wall ([TB 070, p. 2](https://cruisemaster.com.au/content/cis/TB%20070%20-%20Chassis%20Design%20Recommendations.pdf)), and C450L0 meets all three. Plate: AS/NZS 3678 grade 250 or 350.
- Protection: hot-dip galvanise the whole welded chassis and drawbar after fabrication to AS/NZS 4680. On 3 mm walls that gives at least 55 µm (390 g/m²) inside and out, against about 14 µm (100 g/m²) on DuraGal ([GAA coating table](https://gaa.com.au/coating-thickness-and-factors-influencing-thickness/), [InfraBuild DuraGal](https://www.infrabuild.com/steel/products/duragal/duragal-galvanized-steel-rhs-and-shs-structur/)). It adds about 15 to 25 kg (estimate, section 1.4). Buy black tube rather than DuraGal when the frame will be dipped, because the pickling removes the in-line coat anyway and welding through zinc gives porous welds and fumes.
- Welding: every structural weld SP to AS/NZS 1554.1. The ASI allows GP only where a weld is "essentially statically loaded" ([ASI weld quality guide](https://steel.org.au/getattachment/9e3a138d-08d3-413d-8add-875e01b7498a/Welds-quality-capacity_bk122.pdf)), and no chassis weld is. Rail-to-raiser and drawbar-to-rail seams are continuous fillet welds, not stitch welds (section 3.6). No weld runs across the width of a rail ([TB 070](https://cruisemaster.com.au/content/cis/TB%20070%20-%20Chassis%20Design%20Recommendations.pdf)).

### Member sizes to start from

| Member | Section (C450L0) | Where | Basis |
|---|---|---|---|
| Main rails | RHS 150 x 50 x 3 | X 1,820 to 7,320, outer width 1,286 mm | TB 070 minimum section, made strong enough by acting with the raiser (section 3.2) |
| Raisers | RHS 100 x 50 x 3, continuous on each rail, plus a 20 mm floor bearer or isolation strip | Full rail length, top at Z 819.7, floor underside Z 839.4 | Makes a 250 mm deep composite rail (I = 14.2 x 10⁶ mm⁴, Z = 104 x 10³ mm³ per side). 120 mm is not a standard RHS depth |
| XT front hinge and centre crossmembers | RHS 150 x 50 x 3, full rail height, fully welded, no holes. Change to 150 x 50 x 4 if Cruisemaster will not confirm 3 mm for the 4,500 kg build | X 4,152 to 4,202 and 4,982 to 5,032 | TB 070 lists 150 x 50 x 3 for an XT tandem up to 4,450 kg ATM (4,005 kg GTM), and the kit is the 4,500 kg build |
| XT rear shock crossmember | RHS 150 x 50 x 3 with a 5 mm full-height shock support plate | X 5,812 to 5,862 | [XT Air guide, sheets 2 and 3](https://cruisemaster.com.au/content/Installation/33XTAIR-INSTALLATIONGUIDE-Rev2.pdf) |
| Body front and rear crossmembers | RHS 150 x 50 x 3, full rail height | X 1,820 and 7,270 | They take the drawbar root, the spare wheel posts and the recovery points |
| Other crossmembers | RHS 100 x 50 x 3 (as modelled) | X 2,416, 2,986, 3,557, 6,525 | Floor support across 1,186 mm |
| Outriggers | RHS 75 x 50 x 3, 75 mm vertical, top flush with the raiser top, bottom at Z 744.7 | Every crossmember station, plus two new stations each side at the XT centre (X 4,982 to 5,032) and rear shock (X 5,812 to 5,862) crossmembers | Section 5 |
| Drawbar members | RHS 150 x 50 x 5, A-frame | Apex at X 250, 60 mm each side of the centreline, to the rail centres at X 1,820, then 1,000 mm on under the rails to X 2,820 | Section 6 |
| Drawbar cross brace | RHS 75 x 50 x 3, welded at the members' mid-depth | About X 900 | Stone guard and jockey wheel support |

Against the model, which carries 11.6 kg/m (150 x 50 x 4) rails, these sizes save about 29 kg on the rails and add about 14 kg on the drawbar, 3 kg net on the outriggers and 6 kg on the body-end crossmembers, so about 6 kg less steel. Galvanising then adds 15 to 25 kg, so the chassis and drawbar end about 9 to 19 kg heavier than the model (estimates).

### Load cases and criteria

The design basis is the plated ATM of 3,500 kg, towball up to 280 kg (the car's rating), axle group up to 3,280 kg. Peak stress under the 3 g bump stays below yield (ARTSA factor of safety of 3). VSB1's drawbar and chain forces may cause no residual deformation, so they are checked elastically. Fatigue is checked at every welded detail with an IIW FAT class, against a frequent ±0.5 g vertical increment (estimate). Section 3 has the full table.

### The floor over the axles

Add an outrigger each side at the XT centre crossmember and at the XT rear shock crossmember, at raiser height. Using the arm geometry scaled from Cruisemaster's drawing, the closest the tyre comes to these outriggers through its full ±60 mm travel is 105 mm with the outrigger bottom at Z 744.7 (89 mm if it came down to the rail top at Z 720). That is more than the 50 mm the plan allows between the tyre and the floor. The unsupported floor edge then falls from 2,323 mm to 780 mm, for about 12 kg. The brief's estimate of 120 to 230 mm was the gap in plan at Z 720. The true closest distance, measured to the outrigger's lower corner, is smaller (section 5).

### The drawbar

Keep the 1,820 mm length and the A-frame. Two 150 x 50 x 5 members run from a flat coupling plate at the apex to the rail centres and on under the rails for 1,000 mm, welded with continuous longitudinal fillets and ending in a sniped taper with no transverse weld. Chain lugs go one each side near the coupling. A 750 kg rated jockey wheel mounts on the kerb-side member, and a DO35 integrated or side-mount handbrake works the XT drums. The spare wheel posts land on the body front crossmember, not on the drawbar. Section 6 gives the reasons.

### What blocks the design

1. Cruisemaster has to confirm three things: the arm pivot position (scaled here, ±10 mm), whether raiser-level outriggers at the suspension are acceptable against its note that "crossmembers and outriggers must be full chassis rail height", and the hinge crossmember wall for the 4,500 kg build.
2. The DO35 coupling point offset from its mounting face sets the coupling plate height (report 08, open question 4).
3. The galvaniser's bath must take a frame about 7.4 m long and 2.4 m wide across the outriggers. If it cannot, the outriggers are bolted on, or the frame is double-dipped, which raises the distortion risk.
4. The engineer has to accept the load cases, the planning fatigue criterion and the evidence path for VSB1 9.1 and 9.2.2 (test or approved calculation).

---

## 1. Requirements

### 1.1 VSB1 Revision 6

Read from the [VSB1 Rev 6 mirror](https://img1.wsimg.com/blobby/go/630d18fb-e7b9-4863-b5b6-b89af2cdedee/vsb1-revision-6-.pdf) used in report 02. VSB1 marks chapters 9 and 14 "currently under review".

| Clause | Requirement | At ATM 3,500 kg |
|---|---|---|
| 2 (ATM and GTM) | ATM and GTM "must be developed through engineering calculations" that consider chassis strength among other things | Calculation package required |
| 5.1.1 | Pig trailer drawbar at most 8,500 mm. Front load space not shorter than the rear overhang. A drawbar that carries gas bottles or boxes must be tested in that configuration | 3,216 mm against 2,284 mm, passes. Keep loads off the drawbar |
| 5.4 | Running clearance at least 100 mm unladen, for parts supported by the suspension. Ground clearance at the midpoint between two consecutive axles at least 33.33 mm per metre of axle spacing | 27.7 mm between the hubs. Lowest chassis point today: coupling head at 380 mm |
| 8 (brakes) | Over 2,000 kg GTM: brakes on all wheels and breakaway brakes held at least 15 minutes | Breakaway battery and switch on the drawbar |
| 9.1 | Drawbar "securely attached to a substantial structural member". Holds, for 10 s, without residual deformation that degrades function and without cracks: longitudinal tension and compression 1.5 x 9.81 x ATM, transverse 0.5 x 9.81 x ATM, vertical tension and compression (rigid drawbar) 0.5 x 9.81 x ATM. Strength may instead be shown by "approved calculation procedures" that consider strength and fatigue, and approved means approved by the department | 51.5 kN, 17.2 kN, 17.2 kN |
| 9.2.1 | Over 2,500 kg up to 3,500 kg ATM: two chains to AS 4177.4-2004 (3,500 kg chain marked 4177-35, every fourth link). Grade T chain should not be welded | 2 chains, bolted shackles |
| 9.2.2 | Each chain point on a substantial structural member, as near the coupling as practical, one each side of the centreline. Holds for 10 s: longitudinal 9.81 x ATM, vertical 0.5 x 9.81 x ATM. Evidence needed before the RAV entry | 34.3 kN and 17.2 kN per point |
| 9.3.1, 9.3.3 | Quick release coupling with a positive lock. Couplings other than 50 mm balls are covered by ADR 62, and an off-road coupling needs its component type approval number | DO35 V3Plus, approval number still to get (report 08) |
| 9.3.2 | Trailer designed level within the 350 to 460 mm towball range | Coupling point Z 440 ± 20 |
| 14 | Test method: static loads at the coupling centreline, trailer body restrained, loads held 10 s, then inspection. "All testing must be conducted by testing facilities approved under section 111 of the Rules" | Test or approved calculation, see open questions |
| Stone guards (lamps chapter) | Stone guards must not hide the front reflectors, or the reflectors move the reflectors onto the guard or the body | Detail on the stone guard drawing |

VSB1 says nothing on drawbar or chassis materials, welding standards, jockey wheels or coupling bolts. TB 070 and the coupling maker cover those. VSB1 also does not ask for a parking brake, and ADR 38/05 exempts trailers up to 4.5 t ATM from everything after clause 5.4, including its parking brake clause 6.3 ([ADR 38/05 compilation, cl. 5.5 and 6.3](https://www.legislation.gov.au/F2018L00692/2025-01-30/2025-01-30/text/original/pdf)).

### 1.2 ADR 62/02 and mounting the coupling

ADR 62/02 compilation 1 (2010) was read ([legislation.gov.au](https://www.legislation.gov.au/F2007L02226/2010-02-05/2010-02-05/text/original/pdf)). What applies to the trailer side:

- Cl. 5.1 and 12.2.2: up to 3.5 t ATM the coupling must be quick release, with a positive lock and a separate automatic means of holding it locked, visible on inspection.
- Cl. 12.1: a coupling other than a 50 mm ball "must comply with the 'Coupling' manufacturer's installation instructions". So the DO35 guide is the legal mounting rule ([DO35 V3Plus guide, p. 3](https://cruisemaster.com.au/content/cis/DO35-V3PLUS-User-Guide-Rev.3.pdf)): four new bolts each time, at least M12 class 8.8 at 90 Nm (or 1/2 inch grade 5 at 100 Nm), nylon insert nuts or spring washers, never weld the coupling, mount it flat on a flat drawbar plate, and the V3Plus may go under the drawbar "where drawbar design allows". Drawbar download 50 to 350 kg. Do not use the tow pin or coupling for recovery (p. 5).
- Cl. 14.1 and 14.2: the same drawbar forces as VSB1 9.1, or the dynamic test of 14.2.2.1 (for pig trailers up to 3.5 t, ±0.6 x D-value longitudinal for 2 million cycles), or approved calculations covering strength and fatigue (14.2.3).
- Cl. 14.4.2: chain points 9.81 x ATM longitudinal and 0.5 x 9.81 x ATM vertical. The 2007 as-made text referred the longitudinal figure to 1.5 x 9.81 x ATM ([2007 text](https://www.tjmproducts.com/files/media/original/6cb/7ac/2d1/ADR62.pdf)), and amendment 1 corrected it to 9.81 x ATM, which matches VSB1.

### 1.3 Cruisemaster: TB 070 and the XT Air installation guide

From [TB 070](https://cruisemaster.com.au/content/cis/TB%20070%20-%20Chassis%20Design%20Recommendations.pdf) (28 Nov 2018) and [drawing 33XT AIR, sheets 1 to 6](https://cruisemaster.com.au/content/Installation/33XTAIR-INSTALLATIONGUIDE-Rev2.pdf):

| Item | Rule or value | Source |
|---|---|---|
| Responsibility | "Chassis design responsibility lies with manufacturer". Cruisemaster engineering gives advice | 33XT AIR sheet 2 |
| Material | All sections in the suspension area AS/NZS 1163 C350L0 minimum, 50 mm wide only, 3 mm minimum for main rails. Fabrication to AS/NZS 1554. Care when thinning walls with a higher grade, because crossmember deflection rises and heat-affected zones grow | TB 070 pp. 1 to 2 |
| Rails | Minimum outer width 1,150 mm, minimum section height 100 mm. "Do not weld ACROSS the WIDTH of chassis rails" | Sheet 2, TB 070 p. 2 |
| Crossmembers and outriggers | "Crossmembers and outriggers must be full chassis rail height". Suspension crossmembers fully welded to the rails (TB 040), no holes, cut-outs or slots | Sheet 2, TB 070 p. 2 |
| Fatigue | Chassis stresses within the recommendations of BS 7608 | TB 070 p. 2 |
| Hinge crossmember | XT tandem up to 3,700 kg ATM (3,300 GTM): 150 x 50 x 3 or 100 x 50 x 4. Up to 4,450 kg (4,005 GTM): 150 x 50 x 3 or 100 x 50 x 5. If smaller, use a full-width hinge mount or build up the crossmember, for example a 50 x 50 x 5 tube stitch-welded on top or below with mitred, capped ends. Gussets at the hinge crossmember to rail joints where possible | TB 070 pp. 3 to 4 |
| Hinges | Square to the rail, long end of the hinge bar flush with the outside of the rail. 6 mm fillets marked "3-80" on the drawing (I read three 80 mm runs, to confirm). "Weld should not continue under main chassis rail". Recommended gusset 50 x 50 x 3 RHS at 45 degrees, full-width crossmembers only. Hinge nuts M16 at 190 Nm | Sheets 2 to 4 |
| Airbag top bracket | 33SA 013 for a 150 x 50 chassis (33SA 012 for 100 x 50). Welded to the rail's inner face, flush and welded full length along the top, 6 mm fillets continued at least 20 mm round both ends. Airbag bolts 3/8 UNC at 16 Nm. Bump stop clearance H at ride 85 mm for the AB 0140-V bag | Sheets 2 to 4 |
| Shock mounts | Brackets on the crossmember face, 6 mm fillets, clevises 123 mm apart on a 150 mm bracket. A 5 mm full-height shock support plate (not supplied) welded all round with 5 mm fillets. Single shocks in the inboard mount. Shock bolts M12 at 120 Nm | Sheets 2 to 4 |
| Positions | From each hinge crossmember's rear face: hub 418 mm (standard arm), 780 mm to the next crossmember face, 830 mm wheelbase, 1,610 mm from the front hinge crossmember's rear face to the rear shock crossmember's front face, 75 mm minimum between tyres, 760 mm maximum tyre on 830 mm | Sheet 2 |
| Ride height | Hub 205 to 230 mm below the rail underside at rated load, ±60 mm travel | Sheet 2 |
| Cables | Brake and ABS cables run along the supplied tray on the arm. Handbrake cable guide on the arm: route the cable through before attaching it to the brake | Sheets 4 and 6 |
| Alignment | Set fully loaded on flat ground. Front axle 2 mm toe-in, rear axle parallel to the rail. 1 degree positive camber built in, 0 to 0.5 degree negative at rated load | Sheet 5 |
| Bosch TSC | ECU between the axles within ±300 mm of the centreline on an RHS face flat to 0.3 mm | Report 06 section 8 |

What limits brackets and outriggers near the suspension: everything Cruisemaster welds on sits inboard of or under the rail (hinges under the crossmembers, airbag brackets on the rail inner face, bump stops and shock brackets between the rails). Outboard of the rail and above Z 720, the only thing that moves is the tyre. The limits are therefore the tyre's swept envelope (section 5), the ban on welds across the rail width, the full-rail-height note, and keeping the hinge's outer face clear for the alignment adjusters, which go in from the outside of the hinge.

The model labels the hinge crossmembers "tandem trailer up to 3,700 kg ATM". The kit is the 4,500 kg build, which sits 50 kg above TB 070's 4,450 kg XT row. The label and the section want Cruisemaster's confirmation.

### 1.4 Materials and protection

**AS/NZS 1163 grades.** C350L0: fy 350 MPa, fu 430 MPa. C450L0: fy 450 MPa, fu 500 MPa. "L0" means impact-tested at 0 °C. Austube's C450PLUS meets both grades, with C350's elongation ([Austube DCT 2013, table notes](https://www.austubemills.com.au/wp-content/uploads/sites/9/2022/02/atm_dct_sshs_aug13_new-1.pdf)). AS 4100 sections in C450 can be non-compact or slender in their weak axis, so the yaml carries Austube's effective section moduli. Example: 150 x 50 x 3 is compact about x (Ze = 51.4 x 10³ mm³) and slender about y (Ze = 14.5 x 10³).

**AS/NZS 1554.1 weld categories.** SP (structural purpose) has tighter imperfection limits and a capacity factor of 0.8 on fillet welds. GP (general purpose) has 0.6 and may be used only where the weld is "essentially statically loaded" and loaded to no more than 75% of an SP weld's capacity ([ASI guide](https://steel.org.au/getattachment/9e3a138d-08d3-413d-8add-875e01b7498a/Welds-quality-capacity_bk122.pdf)). A trailer chassis is fatigue-loaded, so every structural weld is SP. Report 02 WLD-03 already sets the inspection: visual on every weld, plus dye penetrant or magnetic particle on the drawbar-to-chassis joint, the coupling mount and the suspension brackets.

**Hot-dip galvanising to AS/NZS 4680.** Minimum average coating on articles that are not centrifuged ([GAA](https://gaa.com.au/coating-thickness-and-factors-influencing-thickness/)):

| Steel thickness | Average thickness | Average mass |
|---|---|---|
| up to 1.5 mm | 45 µm | 320 g/m² |
| over 1.5 to 3 mm | 55 µm | 390 g/m² |
| over 3 to 6 mm | 70 µm | 500 g/m² |
| over 6 mm | 85 µm | 600 g/m² |

- Mass. A 150 x 50 x 3 rail has about 0.76 m² per metre inside and out, so the minimum coat is about 0.30 kg/m, 3.3% of its 8.96 kg/m. Over the whole chassis and drawbar (about 32 m², estimate) that is 12 to 16 kg at the minimum, and nearer 15 to 25 kg with drips, thicker coats on 5 mm parts and the usual excess. RV Daily quotes galvanisers at "around five percent" of chassis mass ([RV Daily](https://rvdaily.com.au/chassis-the-things-we-thought-we-knew-but-didnt/)), about 24 kg here.
- Venting and draining. Report 02 WLD-05 carries the GAA rules: vent holes close to every hollow-section joint, internal vents at least 50% of the connecting section's internal diameter, a 10 mm check hole at each internal vent, and overlaps vented with holes of at least 10 to 12 mm ([GAA guide](https://gaa.com.au/venting-draining-guide/)). The rail-raiser and drawbar-rail overlaps are sealed seams with continuous welds, so each needs vent holes at both ends of each bay. Agree the hole plan with the galvaniser before cutting.
- Distortion. At bath temperature (about 455 °C) steel's yield strength drops by about 50%. Galvanisers ask for uniform thickness, symmetric details (no cleats on one side only of an RHS), balanced welding sequences, and a structure that carries its own weight at half its yield strength ([Valmont Coatings tech tip 10](https://webassetsprod.valmont.com/valmontproduction/docs/valmontcoatings2025libraries/tech-tips/tech-tips-10-how-to-minimise-distortion-when-hot-dip-galvanizing.pdf?sfvrsn=d6379239_1)). Here that means the 5 mm drawbar and 10 to 12 mm plates next to 3 mm walls need care, and a long thin frame should go in once, not double-dipped.
- Cold-formed corners. Cold work at RHS corners can lead to strain-age embrittlement and corner cracking in the bath ([AGA on corner cracking](https://galvanizeit.org/knowledgebase/article/corner-cracking-of-round-and-rectangular-hss)). Australian practice routinely galvanises C350 and C450 RHS chassis, but the galvaniser should know the grade.
- Flat faces. The Bosch TSC ECU needs a face flat to 0.3 mm, and the DO35 needs a flat plate. Zinc runs can spoil both, so the ECU goes on a bolted bracket and the coupling plate faces are cleaned or machined after dipping.

**DuraGal against HDG after fabrication.** DuraGal is C450PLUS tube in-line galvanised to AS/NZS 4792 with at least 100 g/m² inside and out, about 14 µm by the GAA's 0.14 µm per g/m² ([InfraBuild](https://www.infrabuild.com/steel/products/duragal/duragal-galvanized-steel-rhs-and-shs-structur/)). RV Daily puts DuraGal and Supagal at "approximately seven microns" against 56 to 80 µm for hot dip ([RV Daily](https://rvdaily.com.au/chassis-the-things-we-thought-we-knew-but-didnt/)). The weld zones lose the coat and need zinc-rich primer outside, and inside a closed section they cannot be reached. DuraGal costs less and does not distort in the bath. HDG gives four to six times the zinc everywhere, including inside the tubes and over the welds, and premium off-road vans specify it ([Wonderland XTR](https://wonderlandrv.com.au/range/xtr/), [Van Cruiser X Diesel Machine](https://vancruisercaravans.com.au/caravans/x-diesel-machine-19-2026/)). For corrugations, river crossings and coastal camps, HDG is the better choice.

---

## 2. Section data

`chassis-sections.yaml` (`data/chassis/sections.yaml`) lists 19 sections: the 17 the brief named plus RHS 127 x 51 x 3.5 (a raiser option) and RHS 150 x 50 x 5 (the drawbar). Each entry gives b, d, t, the corner radius, mass, A, Ix, Zx, Sx, Iy, Zy, Sy, J, C, the C450 effective moduli and compactness where published, the grade and fy, the source, and the intended use.

Method. I computed the hollow sections from the AS/NZS 1163 nominal shape with Austube's corner radii (outside radius 2.0t up to 3 mm wall and 2.5t above, inner radius ro - t), steel at 7,850 kg/m³, and Austube's thin-wall torsion formulas (appendix A). Then I compared 15 of them with the [Austube Mills design capacity tables (Aug 2013)](https://www.austubemills.com.au/wp-content/uploads/sites/9/2022/02/atm_dct_sshs_aug13_new-1.pdf), pages 3-12 to 3-17. Every one agrees with the published values to the published rounding (all nine properties within 1.2%). Three of the checks:

| Section | Source | A mm² | Ix 10⁶ mm⁴ | Zx 10³ mm³ | Sx 10³ mm³ | Iy 10⁶ mm⁴ | J 10⁶ mm⁴ | C 10³ mm³ | kg/m |
|---|---|---|---|---|---|---|---|---|---|
| RHS 150 x 50 x 3 | Computed | 1,141 | 2.99 | 39.8 | 51.4 | 0.526 | 1.50 | 38.3 | 8.95 |
| | Austube p. 3-12 | 1,140 | 2.99 | 39.8 | 51.4 | 0.526 | 1.50 | 38.3 | 8.96 |
| RHS 150 x 50 x 5 | Computed | 1,814 | 4.44 | 59.2 | 78.8 | 0.765 | 2.30 | 56.8 | 14.24 |
| | Austube p. 3-12 | 1,810 | 4.44 | 59.2 | 78.9 | 0.765 | 2.30 | 56.8 | 14.2 |
| SHS 100 x 100 x 4 | Computed | 1,481 | 2.23 | 44.6 | 52.6 | 2.23 | 3.63 | 68.0 | 11.63 |
| | Austube p. 3-16 | 1,480 | 2.23 | 44.6 | 52.6 | 2.23 | 3.63 | 68.0 | 11.6 |

Notes:

- RHS 125 x 50 x 3 is not in the Austube C450PLUS range I read (125 x 75 is). I computed it but did not check that anyone stocks it.
- The angles are computed with square corners and no root fillet, and are not checked against a table. Their torsion constant is about 1/400 of a 150 x 50 x 3 RHS, so they suit trim and brackets only.
- A raiser of exactly 120 mm does not exist as a standard RHS. The choices are 100 x 50 with a 20 mm floor bearer or isolation strip (recommended), 127 x 51 x 3.5 with the floor 7 mm higher, or a fabricated section.

---

## 3. Load cases and acceptance criteria

### 3.1 Design masses

| Quantity | Value | Source |
|---|---|---|
| ATM | 3,500 kg | Plate (TRAILER.md, registration) |
| Towball load, design | 280 kg (220 to 280 kg in the load cases, DO35 accepts 350 kg) | TRAILER.md, DO35 guide |
| Axle group, design | 3,280 kg (ATM less 220 kg) | TRAILER.md |
| Wheel load at ATM | 820 kg | Axle group / 4 |
| Static hogging moment over the rear hub, fully loaded (TC2) | 8.1 kNm both rails together, about 9.0 kNm scaled to ATM | My moment diagram from the model's mass schedule (build/trailer/trailer.json), with equal airbag loads per axle (estimate) |

### 3.2 Load cases LC1 to LC10

| ID | Case | Load (planning numbers) | Criterion | Source and reasoning |
|---|---|---|---|---|
| LC1 | Static at ATM | 1 g vertical, 3,500 kg | Stress ≤ fy / 3 (150 MPa in C450). Rails: deflection ≤ span / 500 between the drawbar root and the front hub, rear overhang tip ≤ overhang / 300 (7.6 mm). Outrigger tip ≤ 2 mm | ARTSA factor of 3 (report 02 section 2.4, [ARTSA 2016](https://artsai.wildapricot.org/resources/Documents/2016_07.pdf)). Deflection limits are my proposal, chosen so the body panels and their joints see little imposed movement (estimate) |
| LC2 | Vertical bump | 3 g on the structure. 4 g on local fixings: tanks, battery, spare wheel, airbag and shock brackets, heavy items | Peak stress < fy | ARTSA factor of 3 keeps bump stresses below yield. 4 g on fixings covers the 2.5 to 4.2 g rubble spikes BlackSeries quotes ([BlackSeries](https://blackseries.net/blogs/news/off-road-trailer-chassis-guide-suspension-frame-design), maker blog, indicative only) |
| LC3 | Braking | 0.8 g forward plus 1 g vertical | Stress ≤ fy / 1.5 | Report 02. The drawbar sees the trailer's inertia less its own braking, bounded by LC6 |
| LC4 | Cornering | 0.5 g lateral plus 1 g vertical, applied at the CoG (Z 1,258) | Stress ≤ fy / 1.5 | Report 02. Governs outriggers, body mounts and hinge crossmember bending |
| LC5a | Twist, wheel in a hole | One wheel unloaded at ATM, its 820 kg redistributed. Torque across the axle group T = 820 x 9.81 x 0.831 = 6.7 kNm, factored by 2 for dynamics = 13.4 kNm, reacted between the four wheel stations | Stress ≤ fy / 1.5. Relative twist between the front hinge and rear shock crossmembers ≤ 0.5 degree (estimate) | With independent non-load-sharing arms, the largest static twist is set by one wheel losing its load. The DO35 rolls freely through 360 degrees, so the ball reacts no torque and the twist stays in the axle group. The factor of 2 is my proposal |
| LC5b | Twist, corner steady | At tare, one corner steady wound to its 875 kg rating with the other three touching: about 5.3 kNm | Stress ≤ fy / 1.5 | ARK warns that corner steadies impose twisting forces ([ARK catalogue 2024, p. 67](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf)) |
| LC6 | Drawbar, VSB1 9.1 | At the coupling centreline, separately: ±51.5 kN longitudinal, ±17.2 kN transverse, ±17.2 kN vertical | No residual deformation, so elastic: peak stress < fy. No weld or bolt failure | VSB1 9.1 and 14.2.1; ADR 62/02 14.2 |
| LC6b | Chain points, VSB1 9.2.2 | Each point separately: 34.3 kN longitudinal, 17.2 kN vertical | As LC6 | VSB1 9.2.2 and 14.2.2; ADR 62/02 14.4.2 |
| LC7 | Cargo and heavy items | 0.8 g forward, 0.5 g rearward, 0.5 g sideways, 0.2 g up, separately, times 2 off road | Stress ≤ fy / 1.5 in the chassis members and mounts | NTC Load Restraint Guide via report 02. The factor of 2 off road is report 03's |
| LC8a | Recovery points | 51.5 kN (1.5 x 9.81 x ATM) anywhere within ±30 degrees horizontally and ±15 degrees vertically of the rail axis. Ultimate 78.5 kN (8 t) | No yield at 51.5 kN and no fracture at 78.5 kN | 51.5 kN matches the drawbar case, so the load path is already proven. 8 t is the load TJM uses to test recovery points ([Practical Motoring](https://practicalmotoring.com.au/car-advice/rated-recovery-points-explained/)). Proposal |
| LC8b | Jacking points | 38.6 kN on one pad (60% of the axle group on one side, times 2) | No yield, no local crushing of the rail wall | Proposal |
| LC9 | Bed in use | Not a chassis case | | Report 04, DESIGN.md |
| LC10 | Fatigue | Frequent: ±0.5 g vertical on the whole trailer and ±0.5 x the static ball load at the coupling, for 10⁷ cycles and more. Occasional: ±1.5 g for 10⁵ cycles | Frequent stress range ≤ the detail's CAFL (IIW 0.585 x FAT). Occasional cases summed with Miner's rule, damage ≤ 0.5 | Proposal, section 3.4. Replace with logged accelerations (report 02 LOAD-02) |

### 3.3 Planning checks with these numbers

| Member | Case | Demand | Section | Stress | Against |
|---|---|---|---|---|---|
| Main rail, composite with raiser | LC2, 3 g at ATM | 27 kNm both sides, 13.5 kNm per side | 150 x 50 x 3 + 100 x 50 x 3, Z = 104 x 10³ | 130 MPa | fy 450, passes |
| Main rail alone (no composite action) | LC2 | 13.5 kNm | 150 x 50 x 3, Z = 39.8 x 10³ | 339 MPa | Passes yield, fails fatigue (below) |
| Main rail, composite | LC10 frequent | 4.5 kNm range per side | Z = 104 x 10³ | 43 MPa range | FAT 80 crossmember-to-rail toe (CAFL 47): passes. Stitch weld ends at FAT 56 to 63 (CAFL 33 to 37): fail |
| Drawbar member at the body front | LC6 vertical | 8.6 kN x 1.82 m = 15.6 kNm per member | 150 x 50 x 3 / x 4 / x 5 | 393 / 314 / 264 MPa | fy 450: margins 1.15 / 1.43 / 1.70 |
| Drawbar member | LC6 transverse and longitudinal | 25.6 kN and 27.3 kN axial per member (19.6 degree half-angle) | 150 x 50 x 5 | 14 and 15 MPa, plus 1.4 kNm from the 55 mm coupling eccentricity | Small |
| Drawbar member at the body front | LC10 frequent | ±0.5 x (280 kg ball plus about 50 kg of drawbar fittings): 3.2 kN range, 2.75 kNm range per member | 150 x 50 x 4 / x 5 | 55 / 46 MPa range | Needs a FAT 80 or better root detail (CAFL 47) with x 5; x 4 fails. Section 6 |
| Outrigger, 557 mm cantilever | LC2 | 150 kg at the tip (estimate: wall, roof share, floor edge and the kerb-side stowage) x 3 g = 4.4 kN, 2.46 kNm | 75 x 50 x 3, Z = 13.9 x 10³ | 177 MPa | Passes yield |
| Outrigger | LC10 frequent | 0.82 kNm range | 75 x 50 x 3 | 59 MPa range | Over the FAT 63 toe CAFL (37). Needs a gusset or tapered root, or the engineer's lower tip load. Open question |

### 3.4 Fatigue at the planning stage

TB 070 asks for chassis stresses within BS 7608. AS 4100 section 11 and the IIW recommendations use the same idea: each welded detail gets a class, and the nominal stress range at the detail is compared with that class's S-N curve. I used the [IIW recommendations, IIW-1823-07 (2008)](http://dl1.icdst.org/pdfs/files3/4e587a8b160611ccc163ba1ad935e4a7.pdf), which are public. Their S-N curves have slope 3 and a knee at 10⁷ cycles (p. 42). AS 4100 section 11 has its own curve with a knee at 5 x 10⁶ and a cut-off at 10⁸ cycles, and I did not read the paywalled tables.

Method proposed for planning:

1. Give every welded joint a detail class on the CT-Wxx weld sheets (report 02 FAIL-01).
2. Check the frequent case (±0.5 g, 10⁷ cycles and more) against the CAFL, 0.585 x FAT. A corrugated road at 12 to 18 Hz gives 10⁷ cycles in under 200 hours, so these details will pass their knee.
3. Check the occasional case with Miner's rule.
4. Where a detail fails, improve the detail before adding steel: move the weld out of the high-stress zone, taper the end, grind the toe, or use a better joint type.
5. Replace the ±0.5 g assumption with logged data from early trips (report 02 LOAD-02).

Detail classes for the common chassis joints (IIW 2008, Table 3.2-1 and Table 3.3-1):

| Joint | Governing stress | IIW detail | FAT | CAFL (0.585 FAT) |
|---|---|---|---|---|
| Crossmember end welded all round to the rail web: toe in the rail | Rail bending stress at the weld | 512, transverse attachment on a web, fillet as welded | 80 | 47 |
| Same joint: toe in the crossmember | Crossmember bending stress | 413, T-joint fillet weld, toe | 63 | 37 |
| Same joint: weld root | Stress on the weld throat | 414, root crack, a/t ≤ 1/3 | 36 | 21 |
| Outrigger to raiser or rail (cantilever) | Outrigger root bending | 413 and 414 as above | 63 / 36 | 37 / 21 |
| Rail to raiser, continuous fillets, manual | Rail flange stress | 323, continuous manual longitudinal weld | 90 | 53 |
| Rail to raiser, stitch welded | Flange stress, with the web shear ratio | 324, intermittent fillet, τ/σ 0 to over 0.7 | 80 to 36 | 47 to 21 |
| Drawbar under the rail: start and end of the overlap | Stress in the drawbar or rail flange at the weld toe | 711, end of a long doubling plate, welded ends (tD ≤ 0.8t to > 1.5t) | 56 to 45 | 33 to 26 |
| Same, with the end sniped and the toe ground | As above | 712 | 71 to 56 | 42 to 33 |
| Gusset with a ground radius transition at the drawbar root | Drawbar stress | 526, r > 150 mm or r/w > 1/3 | 90 | 53 |
| Suspension hinge to crossmember (load-carrying fillets) | Hot spot stress (structural stress at the weld toe) | Table 3.3-1 no. 6 and 7, load-carrying fillet welds | 90 | 53 (hot spot) |
| Airbag bracket and shock brackets on the rail or crossmember | Hot spot stress | Table 3.3-1 no. 3 and 4, non-load-carrying attachments and bracket ends | 100 | 58 (hot spot) |
| Short pad or lug on a member, length L | Member stress | 513, L ≤ 50 / 150 / 300 / > 300 mm | 80 / 71 / 63 / 50 | 47 / 42 / 37 / 29 |

The hollow-section T-joints (crossmember to rail, outrigger to raiser) bend the thin wall of the member they land on, so the real stress at the toe is often two to four times the nominal one. IIW points to special hot-spot curves for tubular joints (section 3.3.1). The engineer should check the crossmember-to-rail and outrigger joints by the hot-spot method or CIDECT design guide 8 (not read), not by nominal stress alone.

### 3.5 Reasons behind three of the choices

- Why the raiser must work with the rail. On its own a 150 x 50 x 3 rail passes the 3 g check at 339 MPa, but the frequent stress range is 113 MPa, three times any CAFL. Welded continuously to a 100 x 50 x 3 raiser, the same moment gives 43 MPa. So the raiser is structure, not packing, and its welds must carry the shear between the two sections.
- Why continuous welds, not stitch welds. RV Daily reports that chassis are "typically stitch welded" with runs every 350 to 400 mm, on the view that full welds make the chassis too rigid and crack it ([RV Daily](https://rvdaily.com.au/chassis-the-things-we-thought-we-knew-but-didnt/)). The IIW classes say the opposite for fatigue: every stitch end is a weld start and stop, so detail 324 falls from FAT 80 to FAT 36 as the web shear rises, while a continuous manual weld is FAT 90 (323). On the composite rail, stitch ends fail the frequent check and continuous welds pass.
- Why the hinge crossmember question matters. TB 070's table stops at 4,450 kg for the XT, 50 kg under the kit's 4,500 kg rating. On today's real loads (3,280 kg on the axles) the 3,700 kg row already covers it, but Cruisemaster sizes by rated capacity, so it should say which applies.

---

## 4. Practice and failure modes

### 4.1 How Australian off-road vans at about 3.5 t are built

| Source | What it says | Kind |
|---|---|---|
| [RV Daily, "Caravan chassis: the things we thought we knew"](https://rvdaily.com.au/chassis-the-things-we-thought-we-knew-but-didnt/) | 150 x 50 and 100 x 50 RHS, 50 x 25 and 50 x 50 SHS, grades C350 to C450, walls about 2 to 5 mm. Raisers are "a second section of RHS welded onto the chassis" for a flat floor and wheel articulation. Stitch welding every 350 to 400 mm. Hot dip galvanising adds about 5% mass and 56 to 80 µm. Galvanising heat can warp a chassis unless it is designed for it | Trade press, interviewing chassis makers and galvanisers |
| [Wonderland RV XTR](https://wonderlandrv.com.au/range/xtr/) | 6 inch extended A-frame, 12 inch truss chassis, hot-dip galvanised or 2K PU coated, skid plates and recovery points, drop-down corner stabilisers, DO45 coupling, Cruisemaster ATX air 4.5 t | Maker spec |
| [Van Cruiser X Diesel Machine](https://vancruisercaravans.com.au/caravans/x-diesel-machine-19-2026/) | DO35 coupling, 6 inch A-frame "extended 88 inch" (about 2.2 m), 12 inch truss chassis (flat floor), hot-dip galvanised, four stabiliser legs, recovery shackles at the rear, stone guard on the A-frame, 8 inch jockey wheel | Maker spec |
| [S&M Chassis warranty booklet](https://irp.cdn-website.com/cbac8180/files/uploads/SM%20warranty%20book_website%20March%202024.pdf) | Builds chassis for Cruisemaster XT and ATX, AL-KO and Tuffride. Offers pre-coated steel painted, or hot-dip galvanised. Excludes off-road use from the warranty | Chassis maker |
| [ARV warranty booklet](https://cadillacrv.com.au/wp-content/uploads/2026/09/ARV-Warranty-book-revised-Mar-2025-1.pdf) | Chassis plate with ATM and GTM on the A-frame. Jack only at the jacking points. Stabiliser legs are not jacks. Inspect the A-frame and rails for cracks and distortion | Chassis maker |

The pattern is consistent: 150 mm main rails, a raiser or a second upper rail (sold as a "12 inch truss" chassis), outriggers to the body edge, a 150 mm A-frame that runs back along the chassis, and hot-dip galvanising on the better vans. "Truss" here is my reading of a lower rail and an upper rail joined by posts and diagonals, and the makers do not define it. Our 150 mm rail plus 100 mm raiser is a 250 mm version of the same idea.

### 4.2 Where they crack

| Failure | Evidence | Kind | Design response |
|---|---|---|---|
| Chassis bending fore and aft of the axle group, chassis twist, drawbar angle change, floors and walls distorted | Independent engineer's report on Supreme caravans tabled in the Queensland Parliament, 2011 ([5312t6458](https://www.parliament.qld.gov.au/Work-of-the-Assembly/Tabled-Papers/docs/5312t6458/5312t6458.pdf)) | Engineering report | Composite rails, LC1 deflection limits, LC5 twist |
| A-frame cracked where it meets the main frame, front crossmember cracked and distorted | Owner on the Alaska Highway ([MyGrandRV forum](https://www.mygrandrv.com/threads/alaska-and-back-unscathed-almost.77813/)) | Owner report (US) | Long overlap, tapered end, FAT 80 root detail |
| A-frame weld failure that could drop the trailer's front | US recall summary for Somerset trailers ([RV Travel, June 2018](https://www.rvtravel.com/rv-and-rv-related-recalls-for-june-2018/), [OEMDTC](https://blog.oemdtc.com/937/weld-joint-failure-on-front-a-frame-2016-2017-somerset-chesapeake-somerset-newport-recreational-trailers/)) | Recall | SP welds, crack testing at the drawbar joint (report 02 WLD-03) |
| Shock absorber bracket failure on New Age vans with Cruisemaster XT | Recall seen only in a search listing ([Choice forum](https://choice.community/t/new-age-caravans-new-age-caravans-fitted-with-cruisemaster-xt-suspension-my2019-2020-recall/23184), via report 06) | Recall, text not read | 5 mm shock support plate, hot-spot fatigue check |
| Hinge bolts working loose, lost alignment | [4WDing Australia](https://www.4wdingaustralia.com/camping/cruisemaster-suspension-alignment/), via report 06 | Owner report | Torque check after the first rough trip |
| Towball bolt working loose | [RV Daily](https://rvdaily.com.au/is-your-caravan-drawbar-set-to-kill-you/) | Trade press | DO35 nuts and pin torque in the pre-trip check |
| Damage from loads hung on the A-frame or rear bar | RV Daily (chassis article above) | Trade press | No boxes on the drawbar (VSB1 5.1.1) |

---

## 5. The floor beside and over the axles

### 5.1 The arm geometry

Cruisemaster does not dimension the hinge pivot. I scaled it from the vector side view on [33XT AIR sheet 2](https://cruisemaster.com.au/content/Installation/33XTAIR-INSTALLATIONGUIDE-Rev2.pdf), using its dimensioned 780 mm crossmember spacing, 100 mm rail and 418 mm hub offset as the scale (1.42 px/mm at 300 dpi). The drawing is marked "do not scale", but it reproduces both the 418 mm hub position and the 215 mm ride height, so I take the scaled pivot as ±10 mm.

- Pivot: 23 mm ahead of the hinge crossmember's rear face and 99 mm below the rail underside, so at X 4,179 and X 5,009, Z 471.
- Arm, pivot to hub: 441 mm along X and 116 mm down at ride height, radius 456 mm, 14.7 degrees below horizontal.
- Hub at ride: X 4,620 and 5,450, Z 355. At full bump (+60 mm): X 4,632 and 5,462, Z 415, because the trailing arm swings the hub 11.6 mm rearward as it rises. At full droop (-60): 20 mm forward.
- Airbag over the hub, on a bracket on the rail's inner face. Bump stop about 665 mm behind the crossmember face, inboard. Shocks from near the hub up to the next crossmember's front face. None of these is outboard of the rail.

Each tyre moves in its own vertical plane on an arc about the pivot, and the only part above Z 720 is the top of the tyre. At full bump the tyre (752 mm published diameter) crosses Z 720 between X 4,412 and 4,851 (front) and between X 5,242 and 5,681 (rear). At ride height it barely reaches Z 720.

### 5.2 Clearance from the tyre to outriggers at raiser height

Closest distance from the tyre surface to the outrigger's lower corner, searched through the full ±60 mm travel of both arms, with a 50 mm wide outrigger (appendix A):

| Outrigger station | Outrigger bottom Z 720 (rail top) | Bottom Z 744.7 (75 deep, top flush with the raiser) | Bottom Z 769.7 (50 deep) | Critical tyre |
|---|---|---|---|---|
| XT front hinge, X 4,152 to 4,202 (exists) | 151 | 165 | 181 | Front, full bump |
| XT centre, X 4,982 to 5,032 (new) | 89 | 105 | 123 | Front, full bump |
| Midway between the bump positions, X 5,022 to 5,072 | 119 | 134 | 151 | Rear, full bump |
| XT rear shock, X 5,812 to 5,862 (new) | 89 | 105 | 123 | Rear, full bump |
| Battery bay, X 6,525 to 6,575 (exists) | 730 | | | Rear |

So the rough check in the brief was right that the outriggers fit, but the clearance is smaller than 120 to 230 mm. That range was the gap in plan at Z 720 (130 and 210 mm). The tyre is round, so it comes nearer the outrigger's corner than the plan gap suggests. The worst case, 105 mm at the recommended depth, is still double the 50 mm the plan allows between the tyre and the floor. The answer is not sensitive to the pivot: moving the pivot 10 mm in X or Z changes the clearance by about 10 mm.

Also, the model's FIT-05 reports 44 mm from the front tyre to the XT front hinge outrigger, where this geometry gives 151 mm. A member at full rail height (Z 570 to 720) at that station would give about 54 mm, so FIT-05 probably tests a full-height member or the tyre's full diameter. FIT-05 should use the swept-arc test above.

### 5.3 Options compared

| Option | What it is | Added mass (estimate) | Tyre clearance | Floor edge span | Notes |
|---|---|---|---|---|---|
| A. Outriggers at the XT centre and rear shock stations (recommended) | 75 x 50 x 3 outriggers at raiser height, in line with the two crossmembers, welded to the raiser's outer face, with a gusset or tapered root | +12 kg for four (all outriggers changed to 75 x 50 x 3 saves 9 kg on the others) | 105 mm minimum | Longest unsupported edge 780 mm (X 4,202 to 4,982 and 5,032 to 5,812), 663 mm behind | Same detail as every other outrigger. Lines up with the crossmembers, so the outrigger moment passes into the crossmember. Needs Cruisemaster's view on the full-height note |
| B. Perimeter side rails outboard of the tyres | A longitudinal edge member at the body edge, 1,150 to 1,200 mm from the centreline, spanning between the outriggers at X 4,177 and 6,550 | +25 kg (2 x 2.32 m of 75 x 50 x 3) | No conflict: the tyre's outer face is about 956 mm from the centreline, 194 mm inboard of the rail | Edge supported continuously, but the beam spans 2,323 mm (3.6 mm deflection at 1 g on 100 kg/m, estimate) and loads the two end outriggers double | Heavier. The wheel still comes off sideways under it (wheel top at droop is about Z 670) |
| A + light edge member | Option A plus a 50 x 25 x 2.5 member tying the outrigger tips | +12 kg plus 12 kg | As A | Floor panel supported on all four edges, spans 557 x 780 mm | Use if the floor panel maker asks for continuous edge support |
| C. Self-supporting composite floor and wall | No outriggers. The 30 mm floor cantilevers 557 mm from the raiser, and the 1.8 m side wall carries itself as a deep beam between X 4,177 and 6,550 | 0 kg steel, a few kg of panel reinforcement | No conflict | 2,323 mm, carried by the wall-to-floor joint | Depends on panel data and a bonded joint that survives LC10. Point loads near the edge (generator, jerry cans) go through the panel. Needs the panel maker's design and a test |
| D. Wider rails | Move the rails outboard to put outriggers outside the tyres | 0 | | | Not possible: with the effective C/F at its 175 mm minimum the rails could widen only about 20 mm each side for the same track |
| E. Wheel arches | Local boxes over the tyres | | | | Rejected. The flat floor is a requirement |

Recommendation: option A. It is the lightest steel solution, it reuses the outrigger detail used everywhere else, and it cuts the floor edge span by two-thirds. Add the light edge member only if the floor panel maker needs it. The outriggers at the XT stations also give body mount points every 780 to 830 mm, the same as the rest of the chassis.

Effect on the floor: the floor panel now spans 557 mm from the raiser to the body edge on supports at most 780 mm apart, close to the 570 to 596 mm outrigger pitch under the living area.

---

## 6. The drawbar

### 6.1 Length

Keep 1,820 mm from the ball to the body front.

- Stability. Studies of car-trailer high-speed stability rank the trailer's yaw inertia, its nose mass and its axle position as the dominant factors ([summary of the 1980 handling simulations](https://scispace.com/papers/handllng-characteristics-simulations-of-car-trailer-systems-378actjg1n)). For a given body, a shorter drawbar brings the axle group closer to the ball. The axle is now 5,036 mm from the ball. Shortening the drawbar by 300 mm would also bring the towball load nearer the car's limit when the bikes are out, because each item behind the axle gains leverage.
- Jack-knife. The spare wheel on the front wall clears the Cayenne by 540 mm at 90 degrees (JK-01). A 300 mm shorter drawbar would cut that to about 240 mm and bring the car's rear corner over the stone guard earlier than today's 49 degrees.
- Mass. Each 100 mm of drawbar is about 3 kg of 150 x 50 x 5 member, plus the leverage on the ball.

### 6.2 A-frame against parallel members

Use the A-frame. With the members converging at a single coupling plate, VSB1's 17.2 kN transverse force becomes about 25.6 kN of axial force in each member (14 MPa). With parallel members the same force bends both members about their weak axis over 1.8 m, about 31 kNm, which a 150 x 50 RHS cannot carry. The A-frame also gives one central flat plate for the DO35, and both makers above use it.

### 6.3 Section and how far it runs back

- Section: 150 x 50 x 5 C450L0. Under VSB1's vertical case each member carries 15.6 kNm at the body front: 264 MPa, a margin of 1.70 on yield. A 150 x 50 x 4 member passes the same case statically at 314 MPa (margin 1.43), but its frequent fatigue range at the root is 55 MPa, which no as-welded detail class tolerates. With 5 mm walls and a FAT 80 root detail the range is 46 MPa against a CAFL of 47.
- Overlap: run the members under the rails to X 2,820 (1,000 mm, as modelled), past the body front crossmember and the one at X 2,416. Weld them to the rail underside with continuous longitudinal fillets along both edges. End the overlap with a sniped taper and no weld across the rail width (TB 070), between crossmembers and not at one. This follows report 02's FAIL-01 rule that the drawbar runs back to a crossmember or past the front suspension mount, and the "extended A-frame" practice above. It spreads the drawbar moment into the composite rails before the overlap ends, so the stress at the end of the overlap (FAT 56 to 71, detail 711 and 712) is low.
- Root detail: at the body front, where the drawbar moment is largest, give the start of the drawbar-to-rail weld a FAT 80 or better detail. Options are a profiled gusset with a ground radius (detail 526, FAT 90), a toe-ground weld start (712), or a doubler that tapers forward. Put no other welds on the drawbar's top or bottom faces within 300 mm of the body front. That zone holds the chain lugs and spare wheel posts, so move them.
- Cross brace: a 75 x 50 x 3 brace between the members at about X 900, welded at the members' mid-depth, where vertical bending stress is near zero. It carries the stone guard and stiffens the members against buckling under the 51.5 kN push.

### 6.4 Coupling, chains and fittings

| Item | Recommendation | Basis |
|---|---|---|
| DO35 under-mount | A flat plate between the members at the apex, both faces flat, four M12 8.8 bolts at 90 Nm, nylon insert nuts. The plate's height is set by the coupling point offset from the plate. The drawbar members span Z 420 to 570 at the body front, so the coupling point at Z 440 needs, for example, an offset of 130 mm below a plate at the members' top face. Measure a DO35 before drawing the plate. Keep the apex clear for the coupling's 70 degrees of pitch and yaw | DO35 guide p. 3; report 08 open question 4 |
| Chain attachment points | One lug each side, welded to the outer side face of each member 100 to 200 mm behind the coupling plate, at mid-depth. A 10 mm plate lug 60 mm wide with an 18 mm hole is about 82 MPa net tension and 214 MPa bearing at 34.3 kN (estimate). Use ARK HLS13 hammerlock shackles (5,300 kg) on the AS 4177.4 chains, never weld the chain. Test both lugs, or prove them by calculation, to 34.3 kN longitudinal and 17.2 kN vertical | VSB1 9.2; report 08 section 4 |
| Breakaway | Battery box (AL-KO 333070 kit or ARK EBK24) high on the drawbar or on the front wall behind the stone guard, switch near the coupling, its cable on its own point on the car's towbar, not the chain shackles | Report 08 section 4.1; VSB1 8 |
| Jockey wheel | Rated at least 500 kg, preferably 750 kg off road (ARK XO500 or XO750 tube mount), on the kerb-side member at about X 400 to 600. With the ball at 280 kg, a jockey 500 mm behind the ball carries about 311 kg. Bolt it to a bracket plate rather than welding a tube to the member. Stowed, it must stay above the 100 mm running clearance | [ARK catalogue 2024, pp. 50 to 59](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf); VSB1 5.4 |
| Stone guard | 25 x 25 x 2 SHS or 65 x 35 frame with aluminium checker plate, bolted to the cross brace and the member tops on rubber, kept low (car corner from 49 degrees, JK-02), reflectors not hidden. About 10 to 15 kg | VSB1 stone guard note; TRAILER.md JK-02 |
| Handbrake | The Cruisemaster A/T drums take a handbrake cable (the XT arm carries a handbrake cable guide). Fit the DO35's integrated handbrake (part ending -I) or, if the under-mount restricts it, the side-mount 56A-HB-S/M. Not required by ADR 38/05 below 4.5 t, but the breakaway system holds the brakes for only 15 minutes, so it is the only parking brake | DO35 guide p. 5; 33XT AIR sheet 4; ADR 38/05 cl. 5.5 |
| Spare wheel carrier | Two 50 x 50 x 2.5 SHS posts bolted to cleats on the body front crossmember and raiser ends at X 1,820, up the front wall to about Z 1,500, with a light tie to the wall at the top. Under 4 g the 38.8 kg wheel, 155 mm ahead of the wall, gives about 0.24 kNm shared by the two post bases, about 18 MPa in each post (estimate). Nothing goes on the drawbar | TRAILER.md (spare wheel), LC2 |

---

## 7. Recovery points, jacking points and corner steadies

| Item | Position | Rating and design | Mounting |
|---|---|---|---|
| Rear recovery points | Two, at the rail ends, X 7,270 to 7,320, through the rear crossmember | Each takes a 4.75 t bow shackle (the common rated size, [Practical Motoring](https://practicalmotoring.com.au/car-advice/rated-recovery-points-explained/)). LC8a: no yield at 51.5 kN within ±30 degrees horizontally and ±15 degrees vertically, no fracture at 78.5 kN | 12 to 16 mm plate tongue through a slot in the crossmember, welded to the crossmember and the rail web with longitudinal welds. Not across the rail width |
| Front recovery points | Two, at the drawbar root where the members meet the rails (X about 1,820 to 2,000), one each side | As the rear. Never the coupling or tow pin (DO35 guide p. 5) | Lug on the outer side face of each drawbar member at mid-depth, behind the 300 mm root zone, or on the front crossmember |
| Jacking points | Two, under each rail at the XT centre crossmember station (X 4,982 to 5,032), so one jack lifts both wheels on that side once the arms reach droop (about 60 mm plus tyre recovery) | LC8b: 38.6 kN with no yield and no crushing of the rail wall | 10 mm pad, 100 x 100 mm with a locating cup, welded only along its edges parallel to the rail. The crossmember behind it backs the rail wall. ARV's booklet sets the procedure: chock the other side, loosen the nuts, jack at the point nearest the wheel ([ARV](https://cadillacrv.com.au/wp-content/uploads/2026/09/ARV-Warranty-book-revised-Mar-2025-1.pdf)) |
| Corner steadies | Four. Front pair under the rails just behind the drawbar overlap (X about 2,900 to 3,100) or on the front outriggers. Rear pair under the rails at about X 7,000 to 7,200 | ARK XO DDS650 drop-down steady and jack, 875 kg each, 500 mm closed and 650 mm extended. From the rail underside at Z 570 it reaches the ground with 80 mm to spare. LC5b covers the twist they impose | Bolted brackets at crossmember stations. ARK warns of the twisting forces of jacking from each corner ([ARK catalogue, p. 67](https://www.arkcorp.com.au/wp-content/uploads/2024/02/ARK-Catalogue-2024-Final-Web-resize.pdf)). Stowed, above the 100 mm running clearance |

---

## Open questions

1. Cruisemaster: confirm the hinge pivot (scaled here 23 mm ahead of the hinge crossmember's rear face, 99 mm below the rail underside), and supply a tyre and arm envelope for the 752 mm tyre at full bump.
2. Cruisemaster: are raiser-level outriggers at the XT centre and rear shock crossmembers acceptable, given the note "crossmembers and outriggers must be full chassis rail height"? I read the note as aimed at members that carry suspension loads.
3. Cruisemaster: hinge crossmember wall for the 4,500 kg XT Air build, 150 x 50 x 3 or 4, since TB 070's XT table stops at 4,450 kg. Are its weld-on brackets supplied bare and fit to galvanise? What is the "250 MAX" dimension on sheet 2's end view?
4. DO35: the coupling point offset from the mounting face, for top and under mounting (report 08, question 4), and whether the integrated handbrake clears an under-mount.
5. Galvaniser: bath length, width and depth for a frame about 7.4 x 2.4 x 0.45 m. If it is too wide, bolt the outriggers on and galvanise them separately.
6. Engineer: accept the load cases, the factor of 2 on twist, the ±0.5 g frequent fatigue case and the deflection limits, or give their own.
7. Engineer: which evidence satisfies VSB1 9.1 and 9.2.2 for a concessional trailer in NSW? VSB1 14 calls for a facility approved under section 111 of the Rules, and "approved calculations" means approved by the department. The NSW examiner design-checks against VSB1 (report 02).
8. Engineer: AS/NZS 1554.1 SP for all welds, or AS/NZS 1554.5 for the most fatigue-loaded joints? Does AS/NZS 1554.7 (sheet steel) apply to any 2.5 mm parts?
9. Floor panel maker: edge support needed, span tables for 557 x 780 mm, and insert ratings.
10. Outrigger tip load: the 150 kg planning figure depends on what hangs on the kerb-side wall over the axles (generator and jerry cans). Its frequent fatigue range at the root (59 MPa) needs the engineer's check or a gusseted root.
11. Model fixes for the designer (not edited here): FIT-05's test, the hinge crossmember label, the outrigger stations, the raiser section, and the rail mass (the model carries 11.6 kg/m, which is 150 x 50 x 4).

## Could not verify

- AS/NZS 1163, 1554.1, 4680, 4100 section 11 and BS 7608 are paywalled. Their content here comes from Austube Mills, the ASI, the GAA and the IIW document. The AS 4100 knee at 5 x 10⁶ and cut-off at 10⁸ cycles are from memory of the standard.
- The IIW detail classes are from the 2008 edition (IIW-1823-07). Newer editions exist (2016 and the 2024 Springer book) and may have changed some classes.
- The arm pivot is scaled from a drawing marked "do not scale", checked only against two dimensioned features.
- The ARTSA factor of 3 is via report 02, and I did not refetch the article.
- BlackSeries' accelerations have no test method, and the ±0.5 g frequent case is my assumption.
- The outrigger tip load of 150 kg, the 100 kg/m edge load and the galvanising mass are estimates.
- The moment diagram used the model's case flags. Its TC2 total came to 3,151 kg against 3,351 kg in TRAILER.md, so about 200 kg was not placed. I scaled the moment to ATM.
- The equal angles and RHS 125 x 50 x 3 are computed only. The 300PLUS angle yield of 320 MPa is from memory.
- "Truss chassis" is my reading of the makers' term.
- The New Age XT shock bracket recall text was not read, and the A-frame crack reports are owner reports or US recall summaries.
- Jockey wheel, corner steady and breakaway kit masses were not found.
- DuraGal's coating thickness: the GAA conversion gives about 14 µm for 100 g/m², while RV Daily says about 7 µm. I used the GAA figure.

---

## Appendix A: calculation scripts

Section properties. The rounded rectangle polygon with ro = 2t (t ≤ 3) or 2.5t, minus the inner one with ro - t. Second moments by the polygon formula, plastic moduli by strip integration, torsion by J = t³h/3 + 2kAh and C = J/(t + k/t), where h is the midline perimeter 2((d - t) + (b - t)) - 2rm(4 - π), Ah = (b - t)(d - t) - rm²(4 - π), rm = ro - t/2, and k = 2Ah t/h.

Tyre clearance. Pivot at (X 4,179 and 5,009, Z 471), arm radius 456 mm, hub at pivot + (√(456² - (116 - s)²), -(116 - s)) for travel s from -60 to +60 mm. The clearance is the least distance from the hub to the outrigger rectangle, less the tyre radius (376 mm published, 374.7 mm calculated, which adds 1 mm).

Bending moment. Every mass line in the model's TC2 schedule as a point load at its CoG X, the ball reaction at X 0, and equal loads at the two hubs (X 4,621 and 5,451) from moments about the ball.

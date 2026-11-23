# Camper trailer design

Design data, parametric models, checks, drawings and a static website for a one-off off-road home trailer and its
tow vehicle. The tow vehicle is a Toyota LandCruiser 79 single cab V8 that carries two motorcycles in an enclosed box
on its tray. The trailer has a 4,420 mm body with a lift bed across the front, a wet room across the rear and a fixed
roof, plated at 4,000 kg ATM.

The site is https://leonardalq.github.io/camper-trailer/. Every push to `main` is built and checked, and the site is
published from the `live` branch.

The design documents:

- `TRAILER.md`: the whole trailer, its load cases, checks, build order, cost, assumptions and open points.
- `CHASSIS.md`: the chassis and drawbar.
- `BODY.md`: the body and its fixed roof.
- `UTE-GARAGE.md`: the bike box on the LandCruiser 79.
- `VEHICLE.md`: the car build (engine, driveline, GVM kit, brakes, wheels, towing, legal path, budget and stages), with its parts list in `data/vehicle/vehicle-parts.yaml`.
- `docs/decisions.md`: the decision record, by time, that the documents cite.
- `research/`: research reports 01 to 22, 25 and 26 with their data files, and the models of reports 19, 20 and 25 in `research/models/`. Reports 23 and 24 are `VEHICLE.md` and `UTE-GARAGE.md`.
- `DESIGN.md` and `garage-bed/BOM.md`: the retired garage and bed module, kept for the record.

The build reads these files and never edits them.

## Layout

```
data/                   the single source of truth
  assemblies/           trailer.yaml: the whole trailer in the project datum (TRAILER.md)
                        ute-garage.yaml: the bike box on the ute (UTE-GARAGE.md)
  parts/bikes.yaml      the two bikes, for the ute's bike box
  chassis/              chassis.yaml: members, fittings, load cases and fatigue details (CHASSIS.md), and sections.yaml
  body/body.yaml        panels, loads, joints, mounts and openings (BODY.md)
  ute/                  ute.yaml: the LandCruiser 79, its limits and checks, garage-checks.yaml, box-parts.yaml (the
                        bike box's parts list) and parts/*.yaml for the box
  vehicle/              vehicle-parts.yaml: every part and job in VEHICLE.md, with the totals
  checks.yaml           the whole-trailer checks
  load_cases.yaml       the eight trailer load cases, the towball target and the registration ratings
  measurements.yaml     the values the owner will measure, with the rules that re-solve the plan
  services.yaml         the electrical, plumbing and HVAC services and the lamps
  trailer-parts.yaml    the trailer's priced lines outside the mass schedule, and the contingency rules
  project.yaml          the whole-project cost: the truck, the car build's budget and the parts lists
  drawings.yaml         drawing register, revisions and status (retired sheets keep a note)
cad/
  partsdb.py            Pydantic models, loader, parameter expressions, instance expansion
  model/                build123d generators: bikes from research/05, bought envelopes, made parts
  massprops.py          mass schedule (MASS-01), growth allowance (MASS-06), CoG per load case
  checks.py             clearance and contact checks on the B-rep model
  solve.py              the bike spacing solve in the ute's box
  inputs.py             applies the measured inputs and their rules
  trailer.py            the whole trailer: axle solve, load cases, towball, GCM, jack-knife sweep, fit and mass checks
  towball.py            the trailer's heaviest towball, which the ute's towing cases carry
  trailer_model.py      the trailer's 3D block model, and the body models for the site
  trailer_costs.py      the trailer's priced parts list, its totals and the savings
  services.py           the energy, water and HVAC budgets for the services pages
  lamps.py              the lamps, reflectors and number plate, checked to ADR 13/00 and VSB1
  chassis.py            the chassis and drawbar: members, joints, fittings, galvanising, the frame model, the tyre swept arc
  chassis_fea.py        load mapping and the frame analysis of every chassis load case, fatigue and fitting checks
  chassis_checks.py     the chassis checks
  frame.py              direct-stiffness 3D frame solver (numpy), checked in tests/test_frame.py
  body.py, body_model.py  the body checks and its solids
  ute.py, ute_garage.py, ute_model.py  the ute's limits and cases, the bike box and its 3D model
  restraint.py          strap loads by research/03's method (RES-01), for the bike box
  partsmeta.py          the part metadata for the 3D viewer's tooltip and part card
  export.py             STEP, GLB and three-cad-viewer JSON
  drawings/             A3 sheets: CT-001 (ga.py), CT-002, CT-003 and CT-010 (home_sheets.py), CT-011 to CT-013
                        (layout_sheets.py), CT-101 to CT-103 (chassis_sheets.py), CT-104 (structure_sheets.py),
                        CT-201 to CT-301 (body_sheets.py), CT-601 to CT-621 (services_sheets.py), CT-701 to CT-704
                        (ute_sheets.py)
  sitedata.py           copies build outputs into the site and generates the research, Car build and parts list pages
  tests/                pytest: design checks and data rules
site/                   Astro 7 + Starlight 0.43 static site, three-cad-viewer 5.1.3
shot/                   Playwright screenshot, scroll and table-footer checks
docker/                 the build image (Python 3.12, build123d 0.13, OCCT 8, Node 24)
.github/workflows/      builds the site in the same image and publishes the live branch to GitHub Pages
build/                  generated, git-ignored
```

## Build

Everything runs in Docker, so the host only needs Docker and make. The OCCT kernel's wheels need glibc 2.28 or
newer, which older Linux hosts do not have.

```
make            # image, data, model, ute, trailer, check, drawings, site (about 10 minutes from scratch)
make strict     # the same, but fail if a design check fails
make serve      # python3 -m http.server 8791 --bind 127.0.0.1 --directory site/dist
make shots      # screenshots and scroll checks into build/shots (needs make serve running)
make clean      # remove generated files
```

The ute builds before the trailer, because the trailer reads the ute's limits and masses. A plain `make` builds the
site for the root of a local server. The GitHub Pages build sets `SITE_URL` and `SITE_BASE=/camper-trailer`, so every
link and model path gets that prefix.

`make check` runs pytest over the checks on the real geometry and prints every measured value. Its result goes to
`build/checks/` and onto the site. A failing check does not stop `make`, so the site can show it in red. Use
`make strict` where a failure must stop the build. Every fail check passes on the current design.

Outputs: `build/trailer/trailer.json`, `.step` and `.glb`, the chassis and body models, `build/ute/ute.json` and
`ute.step`, `build/drawings/CT-*.pdf|svg|png`, `build/checks/checks.json`, and the site in `site/dist`.

## Conventions

- Project datum (DIM-01, research/02): X rearward from the ball centre, Y towards the road side, Z up from the
  ground. The trailer uses it. It is a right-handed frame, so the CAD model shows the real trailer.
- Ute frame (DIM-U1): X rearward from the ute's front axle, Y towards the road side, Z up from the ground.
- Masses that depend on size are computed from the model: kg/m for extrusions and tube, kg/m² for panels.
  Bought items keep their declared mass. Each line records its source and maturity (spec, calculated, estimate).
- Never change geometry, an estimate or a limit to make a check pass. Resize the part and record it.
- Placeholders for things the design does not yet place are marked PLACEHOLDER in the data.

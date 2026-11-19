# Camper trailer design

Design data, parametric model, checks, drawings and a static website for a one-off off-road camper trailer.
Version 1 covers the garage and bed module: two motorcycles in a garage under a queen bed. The whole-trailer block
layout places that module at the back of the body with a rear door and lays out every other system around it.

The site is published at https://leonardalq.github.io/camper-trailer/ and rebuilds from this repository on every
push to `main`.

The design baseline is `DESIGN.md`, its parts list is `garage-bed/BOM.md`, the whole-trailer layout is
`TRAILER.md`, and the research behind them is in `research/`. The build reads those files and never edits them.

## Layout

```
data/                 the single source of truth
  parts/*.yaml        one entry per BOM line (G-01 to A-02), the bikes, and context parts (no mass)
  assemblies/         garage-bed.yaml: named parameters and every placement from DESIGN.md
                      trailer.yaml: the whole-trailer block layout in the project datum (TRAILER.md)
  checks.yaml         module checks CLR-01 to CLR-10, BED-01, RES-01 and CON-01, and the whole-trailer checks
  load_cases.yaml     the five module load cases, the seven trailer load cases and the car's limits
  steps.yaml          eleven draft build steps (STEP-01 to STEP-08)
  drawings.yaml       drawing register, revisions and status
cad/
  partsdb.py          Pydantic models, loader, parameter expressions, instance expansion
  model/              build123d generators: bikes from research/05, bought envelopes, made parts
  massprops.py        mass schedule (MASS-01), growth allowance (MASS-06), CoG per load case
  checks.py           clearance, height and contact checks on the B-rep model
  fixsearch.py        smallest passing change for a failing check, in 10 mm steps (report only)
  trailer.py          whole-trailer layout: axle solve, ballast, load cases, towball, fit and mass checks, length comparison
  restraint.py        strap loads along the trailer by research/03's method (RES-01)
  trailer_model.py    the trailer's 3D block model with the module placed in it
  export.py           STEP, GLB, three-cad-viewer JSON, per-step viewer states, BOM CSV
  drawings/           A3 sheet module and the sheets CT-001 (ga.py), CT-401, CT-402, CT-501
  sitedata.py         copies build outputs into the site and generates the step and research pages
  tests/              pytest: design checks and data rules
site/                 Astro 7 + Starlight 0.43 static site, three-cad-viewer 5.1.3
shot/                 Playwright screenshot and scroll-check scripts
docker/               the build image (Python 3.12, build123d 0.13, OCCT 8, Node 24)
.github/workflows/    builds the site in the same image and publishes it to GitHub Pages
build/                generated, git-ignored
```

## Build

Everything runs in Docker, so the host only needs Docker and make. The OCCT kernel's wheels need glibc 2.28 or
newer, which older Linux hosts do not have.

```
make            # image, data, model, trailer, check, drawings, site (about 5 minutes from scratch)
make strict     # the same, but fail if a design check fails
make serve      # python3 -m http.server 8791 --bind 127.0.0.1 --directory site/dist
make shots      # screenshots and scroll checks into build/shots (needs make serve running)
make clean      # remove generated files
```

A plain `make` builds the site for the root of a local server. The GitHub Pages build sets `SITE_URL` and
`SITE_BASE=/camper-trailer`, so every link and model path gets that prefix.

`make check` runs pytest over `data/checks.yaml` on the real geometry and prints every measured value. Its
result is written to `build/checks/` and shown on the site. A failing check does not stop `make`, so the site can
show it in red. Use `make strict` where a failure must stop the build.

Outputs: `build/model/garage-bed.step` and `.glb`, `build/bom/garage-bed-bom.csv`, `build/trailer/trailer.json`,
`.step` and `.glb`, `build/drawings/CT-*.pdf|svg|png`, `build/checks/checks.json`, and the site in `site/dist`.

`make check` also runs the whole-trailer checks. Five of them, the mass and towball checks with the growth allowance,
fail on the current estimates, so `make strict` fails until the trailer's mass comes down (TRAILER.md).

## Conventions

- Module frame (DESIGN.md): origin on the garage floor at partition A's rear face on the centreline. X rearward
  towards the rear door, Y towards the kerb side, Z up, millimetres.
- Project datum (DIM-01, research/02): X rearward from the ball centre, Y towards the kerb side, Z up from the
  ground. The trailer layout uses it. It is a left-handed frame, so the CAD model is a mirror image (TRAILER.md).
- Masses that depend on size are computed from the model: kg/m for extrusions and track, kg/m2 for panels.
  Bought items keep their declared mass. Each line records its source and maturity (spec, calculated, estimate).
- Limits in `checks.yaml` are DESIGN.md's. Never change geometry or limits to make a check pass.
- Placeholders for things DESIGN.md does not place are marked PLACEHOLDER in the data.

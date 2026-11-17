# 01 Tech stack for the camper-trailer design site

Research and spike done on 2026-11-16 on the original build host, an older Linux machine with glibc 2.26. Every version below was read from PyPI, the npm registry or GitHub on that day. The spike was a throwaway proof of the stack, and the project in this repository grew out of it.

## Recommendation

| Layer | Pick (version, Nov 2026) | Why, in one line |
|---|---|---|
| Parts data | YAML files validated by Pydantic 2.14.3 models, with a JSON Schema exported for editors | One typed source for weight, dimensions, position and supplier links that the CAD code, the checks and the site all read |
| Modelling | build123d 0.13.0 on OCCT 8.0.1 (cadquery-ocp-novtk 8.0.1.1.0) | True B-rep in plain Python that an LLM writes reliably, with named and coloured STEP, hidden-line projection and distance/boolean queries, all headless |
| Neutral CAD files | STEP AP214 from `export_step`, plus GLB from `export_gltf` | Proven: part names, colours, mm units and a real assembly tree (one BLOCK-01 product used twice); GLB carries mass in node extras |
| Engineering drawings | build123d hidden-line projection plus our own AS 1100 sheet module writing SVG; CairoSVG 2.9.1 for PDF | build123d's own dimension and title-block helpers are not AS 1100 style, so the sheet layer (about 250 lines) is ours and fully controllable |
| Clearance checks | pytest 9 over rules in the YAML, using build123d `distance_to` and boolean intersection volume | Proven: a deliberate clash fails the build with the gap and overlap volume in the message |
| Web 3D viewer | three-cad-viewer 5.1.3, fed by ocp-tessellate 3.6.3 | CAD-grade viewer with B-rep edges, part tree with eye toggles, three clip planes, measuring, explode and animation tracks |
| Site | Astro 7.4.12 with Starlight 0.43.1, static output | An MDX page per build step, the viewer as an island, BOM tables from typed content collections, search built in |
| Build environment on this host | One Docker image: python:3.12-slim-bookworm plus Node 24 | This host has glibc 2.26 and no OCCT wheel installs on it natively; the image built in 54 s |
| Serving | Static files on 127.0.0.1 now; any static host later | Nothing server-side to run or secure |

Runner-up for modelling is CadQuery 2.8.0 (same kernel, larger user base, weaker drawing tools). It cannot share an environment with build123d 0.13 because they pin different OCP versions (CadQuery `cadquery-ocp>=7.9.3.1,<8.0`, build123d `cadquery-ocp-novtk>=8.0,<8.1`, from their PyPI metadata), so pick one. FreeCAD is the fallback if we ever need TechDraw-grade drawings without writing our own sheet code.

## Comparison tables

### a) Code CAD

| Option | Current version | Kernel | STEP names, colours, assembly | 2D drawings | Headless on Linux | Distance and interference | How reliably an LLM writes it | Maintenance |
|---|---|---|---|---|---|---|---|---|
| build123d | 0.13.0, 2026-09-21 ([PyPI](https://pypi.org/project/build123d/)) | OCCT 8.0.1 B-rep | Yes, proven in the spike | Hidden-line projection, SVG/DXF export with ISO line types, `DimensionLine`, `ExtensionLine`, `TechnicalDrawing` ([tutorial](https://build123d.readthedocs.io/en/latest/tech_drawing_tutorial.html)) | Yes; wheels need glibc 2.28+ | `distance_to`, `distance_to_with_closest_points`, `intersect` then volume; proven | Good: plain Python, algebra and builder styles, docs publish an [llms.txt](https://build123d.readthedocs.io/en/latest/llms.txt). The spike code ran first time | Active: 3.7k stars, pushed 2026-11-16, two releases in Sept 2026 ([GitHub](https://github.com/gumyr/build123d)) |
| CadQuery | 2.8.0, 2026-06-20 ([PyPI](https://pypi.org/project/cadquery/)) | OCCT 7.9.3 | Yes, through `Assembly` ([docs](https://cadquery.readthedocs.io/en/latest/assy.html)) | SVG/DXF export of projections with hidden lines, no dimensioning ([docs](https://cadquery.readthedocs.io/en/latest/importexport.html)) | Yes; wheels need glibc 2.31+ | Through OCP and Shape methods | Most public examples of any code CAD, but its chained selectors are where generated code most often breaks | Active: 6.1k stars, pushed 2026-11-16 ([GitHub](https://github.com/CadQuery/cadquery)) |
| OpenSCAD | Stable 2021.01; 2026.11-RC0 pre-release on 2026-11-07 ([releases](https://github.com/openscad/openscad/releases)) | CSG on meshes | No B-rep, so no useful STEP ([export manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Export)) | `projection()` outlines only | Yes, CLI | None built in | Writes well, simple language | Active repo, rare stable releases. Wrong tool for engineering STEP |
| replicad | 1.2.1 on npm ([registry](https://registry.npmjs.org/replicad)) | OCCT compiled to WebAssembly | STEP export (names and colours not tested) | Projection to SVG (not tested) | Yes, Node plus WASM, so glibc does not matter | Not verified | JS/TS, small example base | One main maintainer, 722 stars ([GitHub](https://github.com/sgenoud/replicad)) |
| Zoo KCL (Design Studio) | v1.5.5 and kcl-196 on 2026-11-09 ([releases](https://github.com/KittyCAD/modeling-app/releases)); `zoo-kcl` 0.3.196 ([PyPI](https://pypi.org/project/zoo-kcl/)) | Zoo's own engine, run as a cloud service ([KCL docs](https://zoo.dev/docs/kcl-lang)) | STEP through Zoo's service (not tested) | None found | Needs a Zoo account and token (not tested; the brief forbids accounts) | Not verified | New language, little public training data | Very active, 1.4k open issues |
| FreeCAD scripting | 1.1.4 stable ([release](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4)); weekly builds to 2026-11-11 | OCCT | Yes (not tested here) | TechDraw: templates, dimensions, sections, hatching, BOM ([wiki](https://wiki.freecad.org/TechDraw_Workbench)) | `freecadcmd` runs headless; some TechDraw exports need the GUI ([wiki](https://wiki.freecad.org/Headless_FreeCAD), not run) | Yes | Large stateful API; generated code mixes pre-1.0 and 1.x calls | Very active, 35.5k stars, LGPL |
| Onshape | SaaS ([FeatureScript](https://cad.onshape.com/FsDoc/), [API](https://onshape-public.github.io/docs/)) | Parasolid | Yes, by API | Best drawings of this list, in the browser | Cloud API only | Yes in the app | FeatureScript is niche | Commercial, needs an account (not tested) |
| Newer: nanocct | 8.0.1.5, 2026-10-23 ([PyPI](https://pypi.org/project/nanocct/)) | New nanobind OCCT 8 bindings | Binding layer, not a modeller | n/a | Wheels need glibc 2.28+ | n/a | n/a | New. ocp-tessellate already supports it, so build123d may move to it |

### b) 2D drawings

| Path | Hidden lines | Dimensions | Title block, parts list, revisions | Sections | AS 1100 / ISO 128 fit | Output | Verdict |
|---|---|---|---|---|---|---|---|
| build123d drafting helpers plus `ExportSVG` | Yes, OCCT HLR | Yes, but the text sits in a gap in the dimension line and lines, arrows and text are filled outlines (read in `drafting.py` of 0.13.0) | `TechnicalDrawing` draws a border and a box with title, subtitle, number, sheet, scale, date and designer. No revision block, parts list or projection symbol | Boolean section, no hatching helper | Partial. ISO line types exist; the dimension style is closer to ASME | SVG, DXF | Good engine, not enough alone |
| build123d HLR plus our own sheet module (the spike) | Yes; tangent edges left out, as drawings normally do | ISO 129 / AS 1100.201 style: thin lines, filled 3 mm arrows, text above the line reading from the bottom or right, projection lines with 1 mm gap and 2 mm overshoot | Revision block, parts list filled from the BOM data, ISO 7200-width title block, third-angle symbol, checked and engineer sign-off boxes | Removed section A-A at 1:1 with 45 degree hatching clipped by OCCT | Meets the conventions above; the template needs the engineer's review | SVG with real text, PDF via CairoSVG with fonts embedded, PNG preview | Recommended |
| FreeCAD TechDraw, driven headless | Yes | Full tools, ISO and ASME styles | Templates, BOM from spreadsheet | Yes, hatch patterns | Good once a template exists | SVG, PDF, DXF | Strong, but a second CAD stack and GUI-dependent exports (not tested) |
| ezdxf 1.4.5 ([PyPI](https://pypi.org/project/ezdxf/)) | n/a, 2D only; feed it projected edges | Real DXF DIMENSION entities with a DIMSTYLE ([tutorial](https://ezdxf.readthedocs.io/en/stable/tutorials/linear_dimension.html)) | By hand | Hatch entities | Good | DXF; SVG/PDF through its [drawing add-on](https://ezdxf.readthedocs.io/en/stable/addons/drawing.html) | Add later if the engineer wants editable DXF. Already installed as a build123d dependency |

Third angle: AS 1100.101-1992 clause 6.3.3 prefers third-angle projection, and the third-angle symbol shows the truncated cone's short side towards the circles ([Wikipedia](https://en.wikipedia.org/wiki/Multiview_orthographic_projection)), with the circles on the right ([AIMS Industrial](https://aimsindustrial.com.au/blogs/product-guides/engineering-drawing-symbols-guide)). The spike draws it that way.

SVG to PDF: [CairoSVG](https://cairosvg.org/) 2.9.1 from pip, which needs the system `libcairo2`, worked first time and embedded DejaVu Sans. Alternatives are `rsvg-convert`, the Inkscape CLI or headless Chromium printing; none are installed on the host.

### c) Web 3D viewers

| Viewer | Version | Input | Edge lines | Part tree with toggles | Explode and per-step animation | Section planes | Measuring | Licence | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| three-cad-viewer | 5.1.3, 2026-10-12 ([GitHub](https://github.com/bernhard-42/three-cad-viewer), [examples](https://bernhard-42.github.io/three-cad-viewer/example.html)) | ocp-tessellate JSON ([GitHub](https://github.com/bernhard-42/ocp-tessellate)) | Yes, true B-rep edges | Yes, plus `setStates()` for step pages (proven) | Explode tool, `addPositionTrack`, `setRelativeTime` (exploded step proven) | Three clip planes with caps (Clip tab) | Distance and properties tools with a built-in backend | MIT | Recommended |
| three.js r187 or react-three-fiber 9.8.2 with glTF | r187, 2026-10-30 ([releases](https://github.com/mrdoob/three.js/releases)), [R3F](https://github.com/pmndrs/react-three-fiber) | glTF/GLB | Build it | Build it | Build it with AnimationMixer | `clippingPlanes` exists, UI is yours | Build it | MIT | Most flexible, most work |
| Online 3D Viewer | 0.18.0, 2025-12-18 ([GitHub](https://github.com/kovacsv/Online3DViewer), [site](https://3dviewer.net/)) | STEP and IGES through occt-import-js, many mesh formats | Yes | Yes | No | Not verified | Yes | MIT; occt-import-js is LGPL-2.1, last release 2024-12-03 ([GitHub](https://github.com/kovacsv/occt-import-js)) | Good "open the raw STEP" page, not a build-doc viewer |
| xeokit-sdk | 2.6.114 ([GitHub](https://github.com/xeokit/xeokit-sdk)) | XKT, glTF, IFC | Yes | Yes | Not built in | Yes | Yes | AGPL-3.0 or paid | Built for huge BIM models; licence adds friction |
| model-viewer | 4.4.0, 2026-10-09 ([GitHub](https://github.com/google/model-viewer), [site](https://modelviewer.dev/)) | One glTF | No | No | glTF clips only | No | No | Apache-2.0 | Product shots only |

Performance with about 200 parts was not measured. The spike's viewer JSON is 286 KB for five parts (the beam alone is 1,592 vertices), so 200 parts could reach tens of MB unless we use ocp-tessellate's shared instances and binary buffers and load per step. The viewer's JS bundle is 1.43 MB.

### d) Site and build-doc frameworks

| Framework | Version | Page per build step | Interactive components | Tables from YAML/JSON | Static output | Notes |
|---|---|---|---|---|---|---|
| Astro + Starlight | 7.4.12 and 0.43.1, both 2026-11-13 ([registry](https://registry.npmjs.org/astro), [Starlight](https://starlight.astro.build/)) | MDX file per step, sidebar autogenerated | Islands; the spike uses a plain custom element | Content collections with `file()` loader and a Zod schema ([docs](https://docs.astro.build/en/guides/content-collections/)); proven | Yes; 4 pages in 1.6 s | Needs Node 22.23.4+; Pagefind search included |
| VitePress | 1.6.4 stable, 2.0.0-alpha.21 ([registry](https://registry.npmjs.org/vitepress)) | Markdown per page | Vue components | Data loaders ([docs](https://vitepress.dev/guide/data-loading)) | Yes | Stable line still on Vite 5; 2.0 still alpha |
| Docusaurus | 3.10.2 ([registry](https://registry.npmjs.org/@docusaurus/core), [docs](https://docusaurus.io/docs)) | MDX | React | JSON imports, plugins | Yes | Heavier; strong at versioned docs |
| Next.js | 16.4.6 ([registry](https://registry.npmjs.org/next)) | MDX by plugin | React | Anything | `output: 'export'` ([docs](https://nextjs.org/docs/app/guides/static-exports)) | An app framework; more than we need |
| GitBuilding | 0.14.9, 2025-09-20 ([PyPI](https://pypi.org/project/gitbuilding/), [site](https://gitbuilding.io/), [GitLab](https://gitlab.com/gitbuilding/gitbuilding)) | Markdown per step, made for hardware (OpenFlexure) | Limited | BOM built from part links in the steps | Yes | Worth copying its "parts used per step" idea; weak for interactive 3D |

### e) Parts data model and the mass, CoG and towball calculations

Proposed model, as proven in a small form by `data/parts.yaml` and the Pydantic classes in `cad/spike.py`:

- **materials**: name, density in g/cm3, source URL.
- **parts** keyed by part number: name; `kind` (made, bought or envelope); `generator` and `params` (the dimensions that drive the model); `mounts` (named mounting points in the part's own frame); `contacts` (named contact faces); either `material` (mass from CAD volume) or a declared `mass_kg` with `mass_source` (spec sheet URL, or "owner" for the bikes); maker and Australian stockist URLs; colour.
- **assemblies**: items with a ref (1, 2A, 2B), part number and placement in trailer coordinates (x along, y across, z up).
- **checks**: clearance rules (minimum gap) and contact rules (touching, no overlap) between item refs.
- **load cases** (to add): which optional items are aboard (bikes, water, gear).

Pydantic rejects unknown keys, bad colours, unknown references and parts with neither a material nor a mass, and writes `parts.schema.json` so an editor can validate the YAML as you type.

Calculations, per load case:

- Mass of a made part = density × B-rep volume. Bought parts use the declared mass. The spike's beam came out at 397,510 mm3, which matches a hand calculation of the section (398.5 mm2 × 1,000 mm, less 1,039 mm3 for the holes) to 1 mm3.
- Centre of gravity on each axis = Σ(mᵢ·xᵢ) / Σmᵢ, with xᵢ the OCCT centre of mass of each placed part, or the envelope centre when a maker gives no CoG.
- Towball download = M × (x_axle − x_cg) / (x_axle − x_hitch), and axle load = M − download. This holds for a single axle or a load-sharing tandem treated as one support at its centre. Then check it against the 140 kg towball limit from the brief.
- Spike result: 2.023 kg, CoG (500.0, 0.0, 51.5) mm, and 0.096 kg on the ball for an illustrative hitch at x = -1,500 and axle at x = 600.

### f) Where to get models of bought items

| Source | What you get | Access | Redistribution | Use here |
|---|---|---|---|---|
| Maker CAD downloads | STEP of the real product | Often free, sometimes a login | Usually not allowed | Best for small hardware: latches, hinges, tie-down track |
| TraceParts and CADENAS PARTcommunity ([TraceParts](https://www.traceparts.com/), [PARTcommunity](https://www.partcommunity.com/)) | Catalogue STEP for many makers | Free account | Restricted by their terms | Fasteners, bearings, gas struts |
| McMaster-Carr ([site](https://www.mcmaster.com/)) | STEP on product pages | Free | For your own designs | Standard parts (US catalogue, so check AU equivalents) |
| GrabCAD ([library](https://grabcad.com/library)) | Community models | Free account | Varies by model | Reference only; accuracy unknown |
| Envelope from the spec sheet | Box or cylinder with the true overall size, mounting points and contact faces | n/a | Ours | Default for bikes, appliances, batteries and anything big |

Rule of thumb: keep any vendor STEP in `vendor/` with its source URL and licence recorded in the part's YAML, use it locally for checks, and publish only our envelopes on the site.

## Spike results

Goal met: a 6061 RHS beam with two holes on two blocks, each part named, coloured and given a mass, exported to STEP, GLB and viewer JSON; one A3 drawing as SVG and PDF; clearance checks that pass and fail on purpose; the model shown in three-cad-viewer inside a Starlight page, built, served on 127.0.0.1, fetched with curl and screenshotted.

### Host facts and blockers

| Item | Finding | What I did |
|---|---|---|
| OS and glibc | glibc 2.26, system Python 3.7.16 | Used Docker 25.0.18, which works and reaches Docker Hub |
| OCCT wheels | `uv pip install build123d==0.13.0` fails: "cadquery-ocp-novtk>=8.0.1.0.0 has no wheels with a matching platform tag (e.g., `manylinux_2_26_x86_64`)". cadquery-ocp 8.x wheels are manylinux_2_28 and 7.9.x are manylinux_2_31 ([PyPI](https://pypi.org/project/cadquery-ocp/), [manylinux](https://github.com/pypa/manylinux)) | Container `python:3.12-slim-bookworm` (glibc 2.36) |
| Earlier venv from a previous experiment | It holds cadquery 2.3.0 without OCP. `import cadquery` fails with `ModuleNotFoundError: No module named 'OCP'`, so it never had a working kernel. cadquery 2.3.0 declares no OCP dependency, which is why pip "succeeded" | Read only, not modified |
| npm registry | The host's default npm registry is a private mirror that needs a login | Inside the container npm uses registry.npmjs.org. On the host, add a project `.npmrc` with `registry=https://registry.npmjs.org/` |
| Node | Host has Node 20.20.2 and 22.23.2 (mise, glibc-217 builds); Astro 7.4.12 needs 22.23.4+ | Node 24.22.3 in the image. mise's [unofficial glibc-217 builds](https://unofficial-builds.nodejs.org/) also offer v24.22.3 for the host |
| Headless browser | No Chromium on the host; Firefox 153 ESR only | The Playwright image `mcr.microsoft.com/playwright:v1.63.0-noble` (already on the host, 2.51 GB) with `--network host`, see [Playwright Docker docs](https://playwright.dev/docs/docker) |
| Starlight 0.43 | A sidebar group with `autogenerate` and a `label` is rejected (changed in 0.39) | Group with `items: [{ autogenerate }]` |
| three-cad-viewer packaging | CSS must be imported as `three-cad-viewer/css` (exports map) | Fixed |
| three-cad-viewer sizing | Display options alone gave an 800 × 600 canvas that overflowed the page | `viewer.resizeCadView()` after `render()` |
| Remaining layout defect | The viewer's small info panel overlaps the text under it | Fixed later in the project by reserving the viewer's full height |
| GitHub API | Unauthenticated rate limit (60 per hour) hit | Used release redirects and PyPI/npm data |

### Exact commands

```
cd stack-spike
timeout 1200 docker build -t camper-spike:0.1 docker            # 54 s, image 1.48 GB
D="docker run --rm --user $(id -u):$(id -g) -e HOME=/work/.home -e ASTRO_TELEMETRY_DISABLED=1 -v $PWD:/work -w /work camper-spike:0.1"
$D python cad/spike.py                                           # STEP, GLB, viewer JSON, BOM, checks, drawing
$D sh -c 'cd cad && python -m pytest -q test_checks.py -p no:cacheprovider'
$D sh -c 'cd site && npm install --no-audit --no-fund'           # 13.1 s, node_modules 273 MB
$D sh -c 'cd site && npx astro build'                            # site/dist, 3.1 MB
python3.12 -m http.server 8765 --bind 127.0.0.1 --directory site/dist &
docker run --rm --network host --shm-size=1g --user $(id -u):$(id -g) -e HOME=/work/.home \
  -v $PWD:/work -w /work/shot mcr.microsoft.com/playwright:v1.63.0-noble \
  sh -c 'npm i --no-audit --no-fund playwright@1.63.0 && node shot.mjs'
```

`docker/requirements.txt` pins build123d 0.13.0, ocp-tessellate 3.6.3, cairosvg 2.9.1, pydantic 2.14.3, pyyaml 6.0.3 and pytest 9.1.1. Resolved in the image: Python 3.12.16, Debian 12.15, cadquery-ocp-novtk 8.0.1.1.0, ezdxf 1.4.5, numpy 2.5.5, scipy 1.18.1, pygltflib 1.16.5, lib3mf 2.5.0, Node 24.22.3, npm 11.19.1. Site: astro 7.4.12, @astrojs/starlight 0.43.1, three-cad-viewer 5.1.3, three 0.183.2, vite 8.3.8, zod 4.6.7.

### Timings

| Step | Time |
|---|---|
| Docker image build (pip and apt) | 54 s |
| Load and validate YAML, write JSON Schema | 0.014 s |
| Build B-rep model | 0.075 s |
| Mass properties and four checks | 0.061 s |
| STEP export | 0.077 s |
| GLB export with extras | 0.068 s |
| Viewer JSON (tessellation) | 0.129 s |
| Drawing: 5 HLR views, section, SVG, PDF, PNG | 1.0 s |
| Whole `spike.py` inside Python / with container start | 1.41 s / 5.4 s |
| pytest checks (in pytest / with container start) | 2.63 s / 4.5 s |
| `astro build`, 4 pages (Astro / with container start) | 1.6 s / 3.6 s |
| Screenshot run (Playwright install and two pages) | 10.3 s |

### What came out

- **Model**: RHS 50 × 25 × 3, outside corner R4.5, 1,000 long, two 10.5 mm holes through both walls at x = 100 and 900, resting on two 100 × 100 × 50 HDPE blocks. Masses: beam 1.073 kg (6061 at 2.70 g/cm3, [source](https://en.wikipedia.org/wiki/6061_aluminium_alloy)), blocks 0.475 kg each (HDPE at 0.95 g/cm3, an estimate from the 0.93 to 0.97 range, [source](https://en.wikipedia.org/wiki/High-density_polyethylene)).
- **STEP** (`out/spike.step`, 99 KB): AP214, millimetres, three NEXT_ASSEMBLY_USAGE_OCCURRENCE entries, products `ASM-SPIKE Beam on blocks`, `BEAM-01` and `BLOCK-01` (one block product used twice, two MANIFOLD_SOLID_BREP), and both colours. Re-imported with build123d, it gives the same tree, labels, colours and volumes. Lesson learned: shared geometry gets one product name, so name STEP products by part number. The first run named both blocks `2B BLOCK-01`.
- **GLB** (`out/spike.glb`, 137 KB): nodes `1 BEAM-01`, `2A BLOCK-01`, `2B BLOCK-01`, each with `extras` holding part number, mass, CoG and material.
- **Viewer JSON** (`site/public/models/spike.json`): tree `/ASM-SPIKE/Parts/...` and `/ASM-SPIKE/Envelopes/...`, envelopes at 45 % opacity.
- **Drawing** CT-SPK-001: A3 sheet as `out/CT-SPK-001.svg` (86 KB), `out/CT-SPK-001.pdf` (30 KB, 420 × 297 mm page, fonts embedded) and a preview at `out/CT-SPK-001.png`. It has front, top and right views at 1:5 in third angle with hidden lines and centre lines, removed section A-A at 1:1 with hatching, an isometric view, dimensions, a `2× Ø10.5 THRU` callout, balloons, a parts list, a revision block and a title block with the projection symbol and sign-off boxes. I viewed the PNG; it renders correctly after one fix (a leader note ran past the frame).
- **Checks**: `pytest` reported 3 passed and 1 failed, exit code 1. CLR-01 passes with an 18.00 mm gap against 10 mm required. CLR-02 fails on purpose: gap 0.00 mm, overlap 3,904 mm3, because the 60 mm hose envelope is taller than the 50 mm blocks. CON-01 and CON-02 prove the beam touches both blocks without overlap.
- **Site**: Starlight pages `/`, `/steps/01-place-blocks/` and `/steps/02-fit-beam/` with the viewer, a BOM table from the content collection, a checks table and download links. Served by `http.server` bound to 127.0.0.1:8765 (netstat showed `127.0.0.1:8765 LISTEN`). `curl` got 200 for all three pages, the model JSON, STEP, GLB, PDF, SVG and the Pagefind script. The server was then stopped and a further curl was refused.
- **Screenshots**: headless Chromium with SwiftShader WebGL2; the viewer was ready 0.6 to 0.8 s after load. I viewed the images. The model renders with edges, the tree and toolbar. Step 1 shows only the blocks, and step 2 opens exploded.

## Proposed repository layout and build pipeline

```
camper-trailer/
  data/
    materials.yaml
    parts/              one YAML per part or bought item: dimensions, mass and source, suppliers, mounts
    assemblies/         trailer.yaml, garage.yaml: item refs and placements
    checks.yaml         clearance and contact rules
    load_cases.yaml     empty, bikes loaded, water full, ...
    drawings.yaml       drawing numbers, revisions, sign-off status
  cad/
    partsdb.py          Pydantic models, loader, JSON Schema export
    model/              build123d generators per family: chassis, panels, bed, envelopes
    massprops.py        mass, CoG, towball and axle load per load case
    export.py           STEP, GLB, viewer JSON (whole model and per step), BOM JSON and CSV
    drawings/sheet.py   AS 1100 frame, title block, revision block, parts list, dimensions
    drawings/*.py       one script per drawing sheet
    tests/              checks, data rules, mass budget
  vendor/               maker STEP files (git LFS), licence noted, never published
  site/                 Astro + Starlight: steps/*.mdx, CadViewer.astro, DataTable.astro
  build/                generated and git-ignored: step/, glb/, viewer/, drawings/, bom/
  docker/Dockerfile     pinned toolchain (the spike's file is a working start)
  Makefile
```

Pipeline, each stage failing fast:

1. `make data`: validate all YAML, write the JSON Schema, stop on bad references.
2. `make model`: generate parts and assemblies; export STEP, GLB, viewer JSON, BOM and mass properties.
3. `make check`: pytest over `checks.yaml` and the mass budget (towball 140 kg or less in every load case). Any failure stops the build.
4. `make drawings`: sheet scripts to SVG, then PDF with CairoSVG; the revision comes from `drawings.yaml` and each sheet prints the data's git hash.
5. `make site`: copy build outputs into `site/public` and `site/src/data`, then `astro build`.
6. `make serve`: `python3 -m http.server --bind 127.0.0.1`. Later, the same container runs in CI and `site/dist` goes to any static host.

## Risks

- This host can only build the CAD layer in Docker. If Docker goes away, the untested fallback is a conda-forge environment.
- build123d is still 0.x and its API moves. The online "latest" tutorial already uses `drawing_view` where 0.13.0 has `project_to_viewport`. Pin versions and upgrade on purpose.
- The drawing sheet code is ours. It needs an engineer's review once, and every dimension is placed by hand in code, which is fine for 10 to 30 sheets but slow.
- three-cad-viewer is mostly one maintainer's work. GLB export keeps a fallback to plain three.js.
- Viewer data for about 200 parts may be large. Use instancing, binary buffers and per-step files, and lazy-load the 1.43 MB viewer bundle.
- STEP AP214 carries no mass. Mass travels in the BOM and in GLB extras, and the engineer's CAD will recompute it from density.
- On a non-load-sharing tandem the axle split is statically indeterminate, so the towball formula above is only an approximation there.
- Drawings omit tangent edges, so rounded edges show no line. Confirm the engineer is happy with that.

## Open questions

1. Which CAD package does the engineer use, and do they want STEP AP214 or AP242, and DXF as well?
2. Does the engineer have a drawing template or title block they want used?
3. Will the site become public? That decides what vendor models and bike data we can publish.
4. Is Docker acceptable as the standard build on this machine, or should I test a native conda-forge environment?
5. What axle and suspension (single, or tandem with or without load sharing) should the towball calculation assume?
6. How will drawings be signed: on paper, or as a signed PDF?

## Could not verify

- Zoo KCL running without an account (not tested; the brief forbids creating accounts). Onshape for the same reason.
- FreeCAD TechDraw's headless limits, replicad's STEP naming and drawing API, and OpenSCAD 2026.11-RC0's export list: read from project pages or not at all, not run.
- Online 3D Viewer, xeokit and model-viewer features are from their project pages and were not tested. Online 3D Viewer section planes were not confirmed.
- Viewer performance with about 200 parts was not measured.
- The pages for TraceParts, PARTcommunity and GrabCAD return 403 to scripted fetches (bot protection), so they are unverified. npmjs.com package pages also return 403, so npm versions were read from the registry API (registry.npmjs.org), which answered.
- I did not read the AS 1100.101 and AS 1100.201 texts (they are paywalled). The conventions come from the secondary sources cited above and need the engineer's confirmation.
- A conda-forge native install on this host was not tried.

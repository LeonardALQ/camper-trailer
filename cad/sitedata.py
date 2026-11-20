"""Copy build outputs into the site and generate the data-driven pages (build steps, research).

Run inside the project image from the repo root:  python -m cad.sitedata
"""
from __future__ import annotations

import json
import re
import shutil

import yaml

from .build import BUILD
from .partsdb import ROOT

SITE = ROOT / "site"
GEN = SITE / "src" / "data" / "generated"
DOCS = SITE / "src" / "content" / "docs"
RESEARCH = [
    ("01-tech-stack.md", "Tech stack for the design site", 1),
    ("02-design-practice.md", "Design, drawing and documentation practice", 2),
    ("03-bike-restraint-garage.md", "Bike restraint and garage fit-out", 3),
    ("04-bed-and-materials.md", "Bed above the bikes, and build materials", 4),
    ("05-bike-geometry.md", "Bike geometry for envelope models", 5),
    ("06-trailer-running-gear.md", "Trailer running gear: suspension, hubs, brakes and sway control", 6),
    ("07-tow-vehicle.md", "Tow vehicle: the 2013 Porsche Cayenne GTS (958)", 7),
    ("08-coupling-and-hitch.md", "Coupling and hitch", 8),
    ("09-trailer-wheels-and-tyres.md", "Trailer wheels, tyres and stud pattern", 9),
    ("10-car-wheels-and-tyres.md", "The car’s own wheels and tyres for towing", 10),
    ("11-chassis-design.md", "Chassis and drawbar design basis", 11),
]


def _copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    for d in (GEN, SITE / "public" / "models", SITE / "public" / "downloads" / "drawings", SITE / "public" / "drawings",
              DOCS / "steps", DOCS / "research"):
        d.mkdir(parents=True, exist_ok=True)
    # data for the components
    _copy(BUILD / "bom" / "bom.json", GEN / "bom.json")
    _copy(BUILD / "checks" / "checks.json", GEN / "checks.json")
    _copy(BUILD / "drawings" / "register.json", GEN / "register.json")
    _copy(BUILD / "model" / "instances.json", GEN / "instances.json")
    _copy(BUILD / "trailer" / "trailer.json", GEN / "trailer.json")
    steps = yaml.safe_load((ROOT / "data" / "steps.yaml").read_text())
    (GEN / "steps_data.json").write_text(json.dumps(steps, indent=1, default=str))
    # model and downloads
    _copy(BUILD / "model" / "garage-bed.viewer.json", SITE / "public" / "models" / "garage-bed.json")
    _copy(BUILD / "model" / "garage-bed-loading.viewer.json", SITE / "public" / "models" / "garage-bed-loading.json")
    _copy(BUILD / "model" / "steps.json", SITE / "public" / "models" / "steps.json")
    _copy(BUILD / "model" / "garage-bed.step", SITE / "public" / "downloads" / "garage-bed.step")
    _copy(BUILD / "model" / "garage-bed.glb", SITE / "public" / "downloads" / "garage-bed.glb")
    _copy(BUILD / "bom" / "garage-bed-bom.csv", SITE / "public" / "downloads" / "garage-bed-bom.csv")
    _copy(BUILD / "trailer" / "trailer.viewer.json", SITE / "public" / "models" / "trailer.json")
    _copy(BUILD / "trailer" / "trailer.step", SITE / "public" / "downloads" / "trailer.step")
    _copy(BUILD / "trailer" / "trailer.glb", SITE / "public" / "downloads" / "trailer.glb")
    _copy(BUILD / "trailer" / "chassis.viewer.json", SITE / "public" / "models" / "chassis.json")
    _copy(BUILD / "trailer" / "chassis.step", SITE / "public" / "downloads" / "chassis.step")
    _copy(BUILD / "chassis" / "chassis.json", GEN / "chassis.json")
    _copy(BUILD / "chassis" / "chassis-cut-list.csv", SITE / "public" / "downloads" / "chassis-cut-list.csv")
    import cairosvg
    reg = json.loads((BUILD / "drawings" / "register.json").read_text())
    for d in reg["drawings"]:
        n = d["number"]
        for ext in ("pdf", "svg"):
            _copy(BUILD / "drawings" / f"{n}.{ext}", SITE / "public" / "downloads" / "drawings" / f"{n}.{ext}")
        _copy(BUILD / "drawings" / f"{n}.png", SITE / "public" / "drawings" / f"{n}.png")
        cairosvg.svg2png(url=str(BUILD / "drawings" / f"{n}.svg"),
                         write_to=str(SITE / "public" / "drawings" / f"{n}-preview.png"), output_width=1754)

    # one page per build step
    for old in (DOCS / "steps").glob("*.mdx"):
        old.unlink()
    for k, s in enumerate(steps["steps"], 1):
        words, slug = re.sub(r"[^a-z0-9]+", " ", s["title"].lower()).split(), ""
        for w in words:
            if len(slug) + len(w) + 1 > 36:
                break
            slug = f"{slug}-{w}" if slug else w
        parts = slug.split("-")
        while parts and parts[-1] in ("and", "the", "a", "its", "of", "to", "then", "with", "for", "on", "in"):
            parts.pop()
        slug = "-".join(parts)
        title = f"Step {k}: {s['title']}".replace("'", "’")
        (DOCS / "steps" / f"{k:02d}-{slug}.mdx").write_text(
            "---\n"
            f"title: '{title}'\n"
            f"description: '{s['action'].replace(chr(39), '’')}'\n"
            f"sidebar:\n  order: {k}\n"
            "tableOfContents: false\n"
            "---\n\n"
            "import StepDetail from '../../../components/StepDetail.astro';\n\n"
            f"<StepDetail id=\"{s['id']}\" />\n", encoding="utf-8")

    # research reports as pages (copied, with the first heading moved into the title)
    for old in (DOCS / "research").glob("*.md"):
        old.unlink()
    for fname, title, order in RESEARCH:
        text = (ROOT / "research" / fname).read_text(encoding="utf-8")
        text = re.sub(r"\A#\s+[^\n]*\n", "", text, count=1)
        # links between reports point at the .md files in the repository; on the site they go to the report's page
        text = re.sub(r"\]\((\d\d-[a-z0-9-]+)\.md\)", r"](../\1/)", text)
        body = (f"---\ntitle: '{title}'\nsidebar:\n  order: {order}\n---\n\n"
                f"This is research report {fname[:2]}, copied unchanged from `research/{fname}` apart from its first heading.\n\n"
                + text)
        (DOCS / "research" / fname).write_text(body, encoding="utf-8")
    print(f"site data written: {len(steps['steps'])} step pages, {len(RESEARCH)} research pages, "
          f"{len(reg['drawings'])} drawings")


if __name__ == "__main__":
    main()

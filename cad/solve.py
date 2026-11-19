"""Bike spacing from the geometry (measurements.yaml TU-01, addendum 1).

The rule in cad/inputs.py gives a first spacing from the measured width. This sets the final one: the smallest
whole-millimetre spacing at which CLR-03 (Tuareg to Street Triple) meets its limit on the B-rep bikes. The garage
width is fixed (revision D), so the Street Triple moves towards the kerb-side stowage and CLR-10 flags a spacing
that no longer fits. The result is cached in build/solved/module.json, keyed by a hash of the data
it depends on, and Project reads it back. It never changes the CLR-03 limit.
"""
from __future__ import annotations

import hashlib
import json
import math

from .partsdb import ROOT

OUT = ROOT / "build" / "solved" / "module.json"
DEPENDS = ["data/measurements.yaml", "data/parts/bikes.yaml", "data/assemblies/garage-bed.yaml", "data/checks.yaml",
           "research/05-bike-geometry.yaml", "cad/model/bike.py", "cad/inputs.py", "cad/solve.py"]


def key() -> str:
    h = hashlib.sha256()
    for p in DEPENDS:
        h.update((ROOT / p).read_bytes())
    return h.hexdigest()[:16]


def cached() -> dict | None:
    if not OUT.exists():
        return None
    d = json.loads(OUT.read_text())
    return d if d.get("key") == key() else None


def solve() -> dict:
    from .checks import evaluate
    from .model.assembly import Model
    from .partsdb import Project
    from .inputs import BASE_SPACING
    base = Project(use_solved=False)
    rule = base.P.values["bike_spacing"]
    chk = next(c for c in base.checks if c.id == "CLR-03")

    def gap(s):
        prj = Project(overrides={"bike_spacing": s}, use_solved=False)
        res = evaluate(prj, Model(prj, only={"TU", "ST"}), [chk])[0]
        return res["measured_mm"], res["governing"]

    lo, hi = float(BASE_SPACING), max(rule + 60.0, BASE_SPACING + 60.0)
    g_lo, gov_lo = gap(lo)
    if g_lo >= chk.min_gap_mm:
        s, g, gov = lo, g_lo, gov_lo
    else:
        while gap(hi)[0] < chk.min_gap_mm:
            hi += 100
        while hi - lo > 0.5:
            mid = (lo + hi) / 2
            if gap(mid)[0] >= chk.min_gap_mm:
                hi = mid
            else:
                lo = mid
        s = float(math.ceil(hi))
        g, gov = gap(s)
    out = dict(key=key(), rule_spacing=rule, bike_spacing=s, clr03_gap=g,
               governing=gov)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(solve(), indent=1))

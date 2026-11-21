"""The trailer's heaviest towball with growth, which the ute's towing cases carry (UC3 and UC4, data/ute/ute.yaml).

The trailer's axle solve uses decision H17's design targets (data/load_cases.yaml `axle_window`), so it needs nothing
from the ute model and the ute can be built after it. The result is cached in build/solved/towball.json, keyed by a hash
of the data and code it depends on, and the ute model reads it back (cad/ute.py). The trailer's MAS-03B check and
cad/tests/test_trailer.py fail if the trailer ever puts more on the ball than the ute's cases assume.
"""
from __future__ import annotations

import hashlib
import json
import math

from .partsdb import ROOT

OUT = ROOT / "build" / "solved" / "towball.json"


def depends() -> list:
    """Every data file and every model module, so a change anywhere upstream of the trailer re-solves the axle."""
    files = sorted((ROOT / "data").rglob("*.yaml")) + sorted(p for p in (ROOT / "cad").rglob("*.py") if "tests" not in p.parts)
    return [p for p in files if p.is_file()]


def key() -> str:
    h = hashlib.sha256()
    for p in depends():
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def cached() -> dict | None:
    if not OUT.exists():
        return None
    d = json.loads(OUT.read_text())
    return d if d.get("key") == key() else None


def solve() -> dict:
    from .trailer import Trailer
    tr = Trailer(ute=False)
    solved = tr.solve()
    lay = tr.layout(**solved["overrides"])
    cases = [lay.evaluate_case(c) for c in tr.cases]
    heavy = max(cases, key=lambda c: c["growth"]["towball_kg"])
    ball = heavy["growth"]["towball_kg"]
    out = dict(key=key(), towball_kg=math.ceil(ball * 10) / 10, exact_kg=ball, case=heavy["id"], axle_x=solved["axle_x"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    return out


def towball_kg() -> float:
    """The trailer's heaviest towball with growth, rounded up to 0.1 kg."""
    return (cached() or solve())["towball_kg"]


if __name__ == "__main__":
    print(json.dumps(solve(), indent=1))

"""Design checks from data/checks.yaml, measured on the B-rep model (pytest).

A `fail` check that does not meet its limit fails the test. A `report` check (CLR-01b, CLR-06b) is
reported and marked xfail when below its limit, because DESIGN.md says it is not a build failure.
Every measured gap is printed in the terminal summary (see conftest.py) and written to
build/checks/checks.json for the site, with the smallest passing change for any row below its limit.
"""
import json
import time

import pytest

from cad.build import BUILD, git_hash
from cad.checks import evaluate
from cad.fixsearch import search
from cad.model.assembly import Model
from cad.partsdb import Project

T0 = time.time()
PRJ = Project()
MODEL = Model(PRJ)
RESULTS = evaluate(PRJ, MODEL)
for r in RESULTS:
    r["fix"] = None if r["ok"] else search(PRJ, r)
OUT = BUILD / "checks"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "checks.json").write_text(json.dumps(dict(results=RESULTS, git=git_hash(), seconds=round(time.time() - T0, 1)), indent=1))


def _key(r):
    return f"{r['id']}{'-' + r['sub'].split()[1] if r['sub'] else ''}"


@pytest.mark.parametrize("row", RESULTS, ids=[_key(r) for r in RESULTS])
def test_check(row):
    msg = f"{row['id']} {row['sub']} {row['title']}: {row['detail']}"
    if row["fix"]:
        f = row["fix"]
        msg += f". Smallest passing change: {f['param']} {f['baseline']:g} -> {f['value']:g} ({f['change_mm']:+g} mm), gap {f['measured_mm']} mm"
    if row["severity"] == "report":
        if not row["ok"]:
            pytest.xfail("reported, not a build failure: " + msg)
        return
    assert row["ok"], msg

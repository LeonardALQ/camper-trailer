"""The drawing set's entry point and the view helpers the sheets share (A3, third angle).

The garage and bed module's sheets CT-401, CT-402 and CT-501 are retired: the bikes ride in the ute's bike box, so the
bike restraint moved to the ute's sheets CT-701 to CT-704 (UTE-GARAGE.md) and the bed to the body (CT-201, BODY.md).
The register (data/drawings.yaml) keeps them, marked RETIRED with that note. Every view shows its subject as seen,
because DIM-01 is right-handed (Y positive to the road side).
"""
from __future__ import annotations

import json
import math
import time

from build123d import Box, Compound, Pos

from ..build import BUILD
from ..partsdb import Project

OUT = BUILD / "drawings"


# ------------------------------------------------------------------ helpers
def _leaves(shapes):
    out = []
    for s in shapes:
        if isinstance(s, Compound) and s.children:
            out.extend(_leaves(list(s.children)))
        else:
            out.append(s)
    return out


def _cut_faces(shapes, axis, value, tol=0.05):
    faces = []
    for s in shapes:
        for f in s.faces():
            bb = f.bounding_box()
            if abs(getattr(bb.min, axis) - value) < tol and abs(getattr(bb.max, axis) - value) < tol:
                faces.append(f)
    return faces


def _wire_pts(view, w):
    try:
        edges = w.order_edges()
    except Exception:
        edges = w.edges()
    pts = []
    for e in edges:
        us = [0, 1] if e.geom_type.name == "LINE" else [k / 16 for k in range(17)]
        ep = [view.p(v.X, v.Y, v.Z) for v in (e.position_at(u) for u in us)]
        if pts and math.dist(ep[-1], pts[-1]) < math.dist(ep[0], pts[-1]):
            ep = ep[::-1]
        pts.extend(ep)
    return pts


def _shade(sh, view, faces):
    for f in faces:
        loops = [_wire_pts(view, f.outer_wire())] + [_wire_pts(view, w) for w in f.inner_wires()]
        sh.multipath(loops, "shade")


def _clip(shapes, x0, x1, y0, y1, z0, z1):
    box = Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)
    out = []
    for s in shapes:
        bb = s.bounding_box()
        if bb.max.X < x0 or bb.min.X > x1 or bb.max.Y < y0 or bb.min.Y > y1 or bb.max.Z < z0 or bb.min.Z > z1:
            continue
        try:
            r = s & box
            if r is not None and r.volume > 1e-6:
                out.append(r)
        except Exception:
            pass
    return out



def main(only: list[str] | None = None):
    import sys
    import yaml
    t0 = time.time()
    prj = Project()
    reg = yaml.safe_load((prj.root / "data" / "drawings.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    only = only or [a for a in sys.argv[2:] if a.startswith("CT-")]
    tm = {}
    from .body_sheets import ct201, ct202, ct203, ct301
    from .chassis_sheets import ct101, ct102, ct103
    from .ga import ct001
    from .home_sheets import ct002, ct003, ct010
    from .layout_sheets import ct011, ct012, ct013
    from .services_sheets import ct601, ct602, ct611, ct612, ct621
    from .structure_sheets import ct104
    from .ute_sheets import ct701, ct702, ct703, ct704
    fns = {"CT-001": ct001, "CT-002": ct002, "CT-003": ct003, "CT-010": ct010, "CT-011": ct011, "CT-012": ct012, "CT-013": ct013,
           "CT-101": ct101, "CT-102": ct102, "CT-103": ct103, "CT-104": ct104, "CT-201": ct201, "CT-202": ct202, "CT-203": ct203,
           "CT-301": ct301, "CT-601": ct601, "CT-602": ct602, "CT-611": ct611, "CT-612": ct612, "CT-621": ct621,
           "CT-701": ct701, "CT-702": ct702, "CT-703": ct703, "CT-704": ct704}
    for dwg in reg["drawings"]:
        if dwg.get("retired") or (only and dwg["number"] not in only):
            continue
        tm[dwg["number"]] = round(fns[dwg["number"]](prj, None, None, None, reg, dwg), 1)
        print(f"{dwg['number']} written in {tm[dwg['number']]} s", flush=True)
    register = [dict(number=d["number"], title=d["title"], subtitle=d["subtitle"], revision=d["revisions"][-1]["rev"],
                     status=d["status"], date=str(d["revisions"][-1]["date"]), scale=d["scale"], size=d["size"],
                     sheet=d["sheet"], retired=d.get("retired")) for d in reg["drawings"]]
    (OUT / "register.json").write_text(json.dumps(dict(drawings=register, timings=tm, total_s=round(time.time() - t0, 1)), indent=1))

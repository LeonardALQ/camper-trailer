"""Every hole for galvanising as the build records it, read for the hole schedule CT-105 and cut in the 3D model (I2-89).

The records are build/chassis/chassis.json's `results.holes`, the sites CHS-09 and CHS-10 read: cad/chassis_dip.py places
each member's drains and vents, and the frame analysis (cad/chassis_fea.py hole_sites) adds the rails' own, the internal
holes through the rails' inner webs with their check holes, and the seam vents. Nothing here places a hole. A record
gives its centre, diameter, wall and use, and the dip's holes also give u_web, their distance along the web from the end
they serve, and z_under, their height over the member's underside. The rails' holes give their centre only, so their
distance from the rail's nearer end and their height over its underside are read from that centre.

The sealed overlaps' vents through the shock support plates CH-P07 are data (sealed_overlaps in data/chassis/chassis.yaml),
each `u` along the plate from its first end and `v` up from its bottom edge, read here as the plate's outboard end, the
one by the rail, on both sides, so the road side mirrors the kerb side.
"""
from __future__ import annotations

import json
import math

import numpy as np

from .partsdb import ROOT

RECORDS = ROOT / "build" / "chassis" / "chassis.json"
GALV_USES = {"vent", "drain", "drain and vent", "check", "seam vent"}   # a hole for galvanising among the holes' runs
BOLT_USES = ("bolt for ", "rivet nut for ")      # a fixing's hole among the holes' runs (Layout.fixing_holes)
SEAM = "seam"            # a record whose wall is the rail-to-raiser seam goes through the rail's top and the raiser's bottom
_cache: dict = {}


def records() -> list[dict]:
    """The holes for galvanising in the build's records, in their order, or none before the trailer step has written them."""
    return _read()["holes"]


def bolt_records() -> list[dict]:
    """The holes the fresh tanks' bearers' bolts and the front guard's hangers' bolts and rivet nuts make in the frame
    (Layout.fixing_holes, I2-109, I2-116), in the build's records' order, for the hole schedule CT-105."""
    return _read()["bolts"]


def _read() -> dict:
    if not RECORDS.exists():
        return dict(holes=[], bolts=[])
    key = RECORDS.stat().st_mtime_ns
    if _cache.get("key") != key:
        holes = json.loads(RECORDS.read_text(encoding="utf-8"))["results"]["holes"]
        _cache.update(key=key, holes=[h for h in holes if set(h.get("runs") or []) & GALV_USES],
                      bolts=[h for h in holes if any(str(r).startswith(BOLT_USES) for r in h.get("runs") or [])])
    return _cache


def is_seam(h: dict) -> bool:
    return SEAM in h["wall"]


def targets(h: dict) -> list[str]:
    """The members a hole goes through: its own, and for a seam vent the raiser over the rail too."""
    if is_seam(h):
        return [h["member"], "RS-" + h["member"][-1]]
    return [h["member"]]


def member_axes(p0, p1, depth_dir=(0.0, 0.0, 1.0)):
    """A tube's unit vectors as member_solid lays its section: along its axis, across its width (the webs' normal) and
    along its depth."""
    ex = np.subtract(p1, p0, dtype=float)
    ex /= np.linalg.norm(ex)
    ez = np.array(depth_dir, float) - ex * np.dot(depth_dir, ex)
    ez /= np.linalg.norm(ez)
    return ex, np.cross(ez, ex), ez


def centre(h: dict) -> np.ndarray:
    return np.array((h["x"], h["y"], h["z"]), float)


def bore(h: dict, p0, p1, depth_dir, t: float, sec=None) -> tuple[np.ndarray, np.ndarray, float, float] | None:
    """The hole's bore in a member from p0 to p1 of wall thickness t: a start point, the unit direction out of the wall
    and the length that takes it through that one wall and no other, or None where its centre lies off the member's
    length (a member drawn short on a sheet). A web's hole runs across the member's width from inside its web, a seam
    vent up through the rail's top wall and the raiser's bottom wall."""
    ex, ey, ez = member_axes(p0, p1, depth_dir)
    c = centre(h)
    s = float(np.dot(c - np.asarray(p0, float), ex))
    if not -1.0 <= s <= math.dist(p0, p1) + 1.0:
        return None
    if is_seam(h):
        return c - 8.0 * ez, ez, 16.0, s
    off = float(np.dot(c - np.asarray(p0, float), ey))
    side = 1.0 if off > 0 else -1.0
    n = side * ey
    if sec is not None and getattr(sec, "cells", 1) > 1 and abs(off) < sec.b / 2 - sec.t:   # through a twin's two webs at its seam
        return c - (t + 2.0) * n, n, 2 * t + 4.0, s
    return c - (t + 2.0) * n, n, t + 4.0, s


def cut_member(m, solid):
    """The member's tube with its holes for galvanising cut through, from the records (member_solid calls it)."""
    from .model.prims import cyl
    tools = []
    for h in records():
        if m.id not in targets(h):
            continue
        b = bore(h, m.p0, m.p1, m.depth_dir, m.sec.t, m.sec)
        if b is None:
            continue
        a, n, length, _ = b
        tools.append(cyl(tuple(a), tuple(a + length * n), h["d"] / 2))
    return solid.cut(*tools) if tools else solid


# ------------------------------------------------------------------ the shock support plates' vents (sealed_overlaps)
def plate_vents(ch) -> list[dict]:
    """Each vent through a plate a sealed overlap names (sealed_overlaps `through: plate`), at its place on each of the
    plate's positions: its centre, diameter, the plate's box and the vent's `u` from the plate's outboard end and `v` over
    its bottom edge."""
    from .chassis import fitting_boxes
    out = []
    for o in ch.data.get("sealed_overlaps") or []:
        if o.get("through") != "plate":
            continue
        f = next(f for f in ch.fittings if f.id == o["id"])
        for bx in fitting_boxes(ch, f):
            x0, y0, z0, x1, y1, z1 = bx
            s = 1 if y0 + y1 > 0 else -1
            y_out = y1 if s > 0 else y0
            for k, v in enumerate(o["vents"], 1):
                c = ((x0 + x1) / 2, y_out - s * float(v["u"]), z0 + float(v["v"]))
                out.append(dict(plate=o["id"], side=s, vent=k, d=float(v["d"]), u=float(v["u"]), v=float(v["v"]), box=bx, centre=c,
                                l=float(o["l"]), w=float(o["w"]), t=float(o["t"])))
    return out


def cut_plates(ch, f, solids: list) -> list:
    """A plate's boxes with the vents its sealed overlap gives cut through them (fitting_solids calls it)."""
    from .model.prims import cyl
    vents = [v for v in plate_vents(ch) if v["plate"] == f.id]
    if not vents:
        return solids
    out = []
    for s in solids:
        bb = s.bounding_box()
        mine = [v for v in vents if bb.min.Y - 1 <= v["centre"][1] <= bb.max.Y + 1]
        tools = [cyl((bb.min.X - 2, v["centre"][1], v["centre"][2]), (bb.max.X + 2, v["centre"][1], v["centre"][2]), v["d"] / 2) for v in mine]
        out.append(s.cut(*tools) if tools else s)
    return out

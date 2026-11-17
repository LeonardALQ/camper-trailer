"""Smallest change that would make a failing check pass, found in 10 mm steps of one named parameter.

This only reports. It never changes the data: the baseline values stay as DESIGN.md sets them.
"""
from __future__ import annotations

from .checks import evaluate
from .partsdb import Project

STEP_MM = 10
MAX_STEPS = 30


def candidates(row: dict) -> list[tuple[str, int, str]]:
    """(parameter, direction, plain-English description) to try for a failing row."""
    cid = row["id"]
    gov = row.get("governing", "")
    if cid in ("CLR-01", "CLR-01b", "CLR-02"):
        return [("beam_underside_z", +1, "raise the beam underside")]
    if cid == "CLR-03":
        return [("bike_spacing", +1, "increase the bike spacing")]
    if cid in ("CLR-06", "CLR-06b"):
        return [("front_tyre_y", -1, "move both bikes towards the road-side wall (front tyre Y), which shrinks the chock nose allowance")]
    if cid == "CLR-05":
        return [("mattress_t", -1, "use a thinner mattress")]
    if cid == "CLR-07":
        if row["measured_mm"] < 0:
            return [("ladder_length", -1, "shorten the ladder")]
        return [("ladder_length", +1, "lengthen the ladder")]
    if cid == "CLR-04":
        if "(C2)" in gov:
            return [("front_tyre_y", +1, "move both bikes away from the road-side wall")]
        if "(C3)" in gov or "(C4)" in gov:
            return [("front_tyre_y", -1, "move both bikes towards the road-side wall")]
        if "(1)" in gov:
            return [("tuareg_x", +1, "move the Tuareg away from partition A")]
        if "(2)" in gov or "(3)" in gov:
            return [("bike_spacing", -1, "reduce the bike spacing")]
    return []


def search(prj: Project, row: dict) -> dict | None:
    from .model.assembly import Model
    check = next(c for c in prj.checks if c.id == row["id"])
    needed = set((check.a or []) + (check.b or []) + (check.each or []))
    for param, sign, words in candidates(row):
        base = prj.P.values[param]
        for k in range(1, MAX_STEPS + 1):
            val = base + sign * STEP_MM * k
            p2 = Project(overrides={param: val})
            m2 = Model(p2, only=needed)
            res = evaluate(p2, m2, [check])
            mine = [r for r in res if r["sub"] == row["sub"]] or res
            if all(r["ok"] for r in mine):
                return dict(param=param, baseline=base, value=val, change_mm=sign * STEP_MM * k, words=words,
                            measured_mm=mine[0]["measured_mm"], steps=k)
    return None

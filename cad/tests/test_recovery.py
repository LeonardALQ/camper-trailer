"""LC8a's reaction (cad/chassis_fea.py recovery_reactions, review I2-124): every tyre's side force within its grip on
LC8a's bound of mu, a held wheel read at LC8a's five headings with the trailer turning about the held hub only as far as
the free tyres' grip lets it, every wheel free under the same cap, the coupling's pulls along the rail axis only, and
the arms' limits read when no arm reaches its droop limit. Each test reads the reaction the way a reviewer would check
it: the forces in balance, each tyre's side force against mu times its own load, and the turn against the moment the
free tyres' grip holds about the held hub."""
import math

import numpy as np

from cad.chassis_fea import Analysis
from cad.tests.test_chassis import CH, RES
from cad.tests.test_trailer import EV, TRAILER

LC8 = next(lc for lc in CH.data["load_cases"] if lc["id"] == "LC8a")
MUS = LC8["reaction"]["mu"]
AN = Analysis(EV["layout"], TRAILER, CH)
SUP = AN.recovery_supports(AN.scaled_cases())
WHEELS = {w["id"]: w for w in CH.suspension}
BALL = np.array([0.0, 0.0, CH.V["coupling_z"]])


def _pull(mag: float, sx: int, hdeg: float, v: float) -> np.ndarray:
    h, vv = math.radians(hdeg), math.radians(v)
    return mag * np.array([sx * math.cos(h) * math.cos(vv), math.sin(h) * math.cos(vv), math.sin(vv)])


def _left(R: dict, p, sup: dict) -> np.ndarray:
    """What the pull, the ground at the tyres and hubs, the nose and the trailer's weight leave unbalanced on the
    trailer, forces in N and moments in Nmm about the origin."""
    tot = np.r_[R["pull"], np.cross(np.asarray(p, float), R["pull"])]
    for wid, w in WHEELS.items():
        c = R["contact"][wid]
        tot = tot + np.r_[c, np.cross(np.asarray(w["contact"], float), c)]
        if wid in R["hub"]:
            tot = tot + np.r_[R["hub"][wid], np.cross(np.asarray(w["hub"], float), R["hub"][wid])]
    tot = tot + np.r_[R["nose"], np.cross(BALL, R["nose"])]
    for it in sup["items"]:
        Fw = np.array([0.0, 0.0, -it.m * 9.81])
        tot = tot + np.r_[Fw, np.cross(np.asarray(it.p, float), Fw)]
    return tot


def _cases():
    """A spread of LC8a's pulls: each point, every wheel free, each wheel held and each axle held, 30 degrees either way
    and along the axis (the coupling along it only), 15 degrees up and down, on every weight and nose support, at the
    limits' ultimates, at each bound of the grip."""
    for where, s in [(w, s) for w in ("front", "rear") for s in (-1, 1)] + [("coupling", 0)]:
        p, _, sx = AN.recovery_point(where, s)
        helds = [(None, LC8.get("free_n", LC8["force_n"]))] + [(w, LC8["held_wheel_n"]) for w in WHEELS]
        helds += [(tuple(w for w in WHEELS if WHEELS[w]["axle"] == a), LC8["held_axle_n"]) for a in ("front", "rear")]
        for held, lim in helds:
            for h in ((-30, 0, 30) if s else (0,)):
                for v in (-15, 15):
                    for sup in SUP:
                        for mu in MUS:
                            F = _pull(lim * LC8["ultimate_n"] / LC8["force_n"], sx, h, v)
                            yield where, s, p, held, F, sup, mu, AN.recovery_reactions(F, p, held, sup["base"], sup["nose"], mu)


CASES = list(_cases())


def test_every_reaction_balances_the_pull_and_the_weight():
    """Every force along, across and up and every moment on the trailer balance in each case read, the pull as the
    trailer takes it, turned or scaled, included."""
    worst = max(np.max(np.abs(_left(R, p, sup) * np.array([1, 1, 1, 1e-3, 1e-3, 1e-3]))) for _, _, p, _, _, sup, _, R in CASES)
    assert worst < 1.0, worst                           # N, and N m for the moments


def test_no_tyre_holds_more_across_than_its_grip():
    """Each tyre's side force is at most mu times its own load from the vertical solve, so a tyre off the ground holds
    nothing across, and a held wheel's axle-mate rolls along and takes nothing across."""
    for where, s, p, held, F, sup, mu, R in CASES:
        held_ids = held if isinstance(held, tuple) else ((held,) if held else ())
        for wid, w in WHEELS.items():
            if wid in held_ids:
                continue
            fy, fz = R["contact"][wid][1], R["contact"][wid][2]
            assert abs(fy) <= mu * fz + 1.0, (where, s, held, wid, mu, fy, fz)
            if isinstance(held, str) and w["axle"] == WHEELS[held]["axle"]:
                assert fy == 0.0


def test_a_held_wheel_turns_the_trailer_only_as_far_as_the_grip_lets_it():
    """With one wheel held, a pull whose moment about the held hub the free tyres' grip cannot hold turns the trailer
    about the hub: the pull's heading moves from the one asked toward the line through the hub and stops where its
    moment about the hub is what the other axle's tyres hold sliding across at their grip, and the hub takes the rest.
    A pull within their grip does not turn it, and no held wheel's pull is turned onto the hub's line."""
    turned = held_kept = 0
    for where, s, p, held, F, sup, mu, R in CASES:
        if not isinstance(held, str):
            continue
        t, h = R["turn"], np.asarray(WHEELS[held]["hub"], float)
        others = [w for w in WHEELS.values() if w["axle"] != WHEELS[held]["axle"]]
        grip = sum(mu * R["contact"][w["id"]][2] * abs(w["contact"][0] - h[0]) for w in others)
        Fp = R["pull"]
        m = (p[0] - h[0]) * Fp[1] - (p[1] - h[1]) * Fp[0]
        if t["turned"]:
            turned += 1
            lo, hi = sorted((t["asked"], t["through"]))
            assert lo - 1e-6 <= t["taken"] <= hi + 1e-6, (where, s, held, t)
            assert abs(abs(m) - grip) < 0.01 * grip + 2000.0, (where, s, held, mu, m, grip)
            for w in others:
                c = R["contact"][w["id"]]
                assert abs(abs(c[1]) - mu * c[2]) < 2.0, (where, held, w["id"], c)
        else:
            held_kept += 1
            assert t["taken"] == t["asked"] and abs(m) <= grip + 2000.0
    assert turned and held_kept


def test_every_wheel_free_slides_where_its_tyres_cannot_hold_the_side_force():
    """With every wheel free the tyres' grip caps the side force, so a pull the tyres cannot hold across slides the
    trailer sideways and reaches only the share it holds, its tyres then at their grip, and on the higher bound of mu
    the same pull holds at least that share. Where no tyre reaches its grip the reaction is the rates' own."""
    slid = kept = 0
    for where, s, p, held, F, sup, mu, R in CASES:
        if held is not None:
            continue
        if R["limit"] == "slides":
            slid += 1
            side = sum(abs(R["contact"][w][1]) for w in WHEELS)
            grip = sum(mu * R["contact"][w][2] for w in WHEELS)
            assert side > 0.99 * grip, (where, s, mu, side, grip)
            hi = AN.recovery_reactions(F, p, None, sup["base"], sup["nose"], max(MUS))
            assert hi["scale"] >= R["scale"] - 1e-9 or hi["limit"] == "tips"
        elif not R["grip"]["sliding"] and not [o for o in R["off"] if o != "nose"]:
            kept += 1
            rates = AN.recovery_reactions(F, p, None, sup["base"], sup["nose"], None)
            assert all(np.allclose(R["contact"][w], rates["contact"][w], atol=1e-6) for w in WHEELS)
    assert slid and kept


def test_lc8a_reads_a_held_wheel_at_five_headings_and_each_bound_of_the_grip():
    """LC8a reads every pull at both bounds of mu (I2-124), a held wheel at the lugs and tongues at LC8a's five headings
    as an axle is, and at the coupling every pull along the rail axis only, so every case there reads +0 degrees."""
    pts = RES["recovery"]["LC8a"]["points"]
    k = len(LC8["reaction"]["weight"]) * len(LC8["reaction"]["nose"]) * len(MUS) * 3      # supports, bounds, up, level, down
    n = len(CH.suspension)
    for w in ("front", "rear"):
        assert pts[f"{w}, every wheel free"] == 2 * 3 * k
        assert pts[f"{w}, wheel held"] == 2 * n * 5 * k
        assert pts[f"{w}, axle held"] == 2 * 2 * 5 * k
    assert (pts["coupling, every wheel free"], pts["coupling, wheel held"], pts["coupling, axle held"]) == (k, n * k, 2 * k)
    cases = [r["case"] for rows in RES["envelope"].values() for r in rows.values()]
    cases += [h[x]["case"] for h in RES["holes"] for x in ("static", "ultimate") if h.get(x)]
    cases += [r["case"] for lc_id in ("LC8a", "LC8u") for r in RES["recovery"][lc_id]["mu"][f"{MUS[0]:g}"]["runs"].values()]
    assert all("+0 deg sideways" in c for c in cases if c.startswith("the coupling"))
    assert not any("through wheel" in c for c in cases)


def test_the_worse_bound_of_the_grip_governs_the_runs_and_the_other_stands_beside():
    """CHS-18 reads LC8a and LC8u at the worse of the two bounds of mu on each frame model, and the recovery summary
    keeps each bound's reading, named by its bound, beside it."""
    parts = {p["part"]: p for p in RES["local"]["hinge_runs"]["parts"]}
    for lc_id in ("LC8a", "LC8u"):
        by_mu = RES["recovery"][lc_id]["mu"]
        assert sorted(by_mu) == sorted(f"{m:g}" for m in MUS)
        for bar in by_mu[f"{MUS[0]:g}"]["runs"]:
            readings = [by_mu[f"{m:g}"]["runs"][bar] for m in MUS]
            assert parts[f"{lc_id}, the hinge bars {bar}"]["mpa"] == max(r["mpa"] for r in readings)
            for m, r in zip(MUS, readings):
                assert f"mu {m:g}" in r["case"] or f"or {m:g}" in r["case"]


def test_the_arms_limits_read_none_where_no_arm_reaches_its_droop_limit():
    """CHS-15 and the recovery summary read an LC8a in which no arm reaches its droop limit (FX36-JOINT-PROGRESS.md
    item 6) as no droop limit engaged, the limits' eye bolts and brackets at nothing, the airbags' brackets as read."""
    an = Analysis(EV["layout"], TRAILER, CH)
    bag = {w: dict(n=5000.0, case="a case", off=[]) for w in WHEELS}
    an.lc8_arms = {lc: dict(cases=1, lifted=0, nose_off=0, tipped=[], axle_tipped=[], axle_cases=0, droop={}, bag=dict(bag), hinge={},
                            lift=dict(mm=0.0), nose=dict(up=0.0, down=0.0), slid=[], turns={}) for lc in ("LC8a", "LC8u")}
    lim = an.arm_limits()
    assert "no arm reaches its droop limit" in lim["load"]
    assert all(p["mpa"] == 0.0 for p in lim["parts"] if "droop limit" in p["part"])
    assert lim["util"] > 0.0
    rec = an.recovery_summary()
    assert rec["LC8u"]["droop"]["n"] == 0.0 and rec["LC8u"]["droop"]["wheel"] is None

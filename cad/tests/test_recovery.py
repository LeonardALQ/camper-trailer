"""LC8a's reaction (cad/chassis_fea.py recovery_reactions, review I2-124): every tyre's side force within its grip on
LC8a's bound of mu, a held wheel read at LC8a's five headings with the trailer turning about the held hub only as far as
the free tyres' grip lets it, every wheel free under the same cap, the coupling's pulls along the rail axis only, and
the arms' limits read when no arm reaches its droop limit. Each test reads the reaction the way a reviewer would check
it: the forces in balance, each tyre's side force against mu times its own load, and the turn against the moment the
free tyres' grip holds about the held hub."""
import math
import re
from pathlib import Path

import numpy as np

from cad.chassis_fea import Analysis, recovery_rule
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
    """LC8a reads every pull at both bounds of mu (I2-124), every wheel free and a held wheel at the lugs and tongues at
    LC8a's five headings as an axle is (I2-127), and at the coupling every pull along the rail axis only, so every case
    there reads +0 degrees."""
    pts = RES["recovery"]["LC8a"]["points"]
    k = len(LC8["reaction"]["weight"]) * len(LC8["reaction"]["nose"]) * len(MUS) * 3      # supports, bounds, up, level, down
    n = len(CH.suspension)
    for w in ("front", "rear"):
        assert pts[f"{w}, every wheel free"] == 2 * 5 * k
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


# ------------------------------------------------------------------ the recovery classes and their tipping pulls (I2-127)
CLASSES = LC8["classes"]
TIP = RES["tipping"]
RULE = recovery_rule(RES, LC8)
KINDS = {"free": {"free"}, "unseen": {"free", "wheel", "axle"}}
ROOT = Path(__file__).resolve().parents[2]


def _class_cells(c: dict) -> list[dict]:
    """The tipping table's least entries a class covers, chosen here from the class's own fields: its point on both
    sides, every wheel state a wheel not seen free could be in, and its lines, level with either."""
    vd = LC8["vertical_deg"]
    lines = {"low": {-vd, 0}, "up": {0, vd}, "any": {-vd, 0, vd}}[c["line"]]
    return [x for x in TIP["least"] if x["where"] == c["at"] and x["wheels"] in KINDS[c["wheels"]] and x["v"] in lines]


def _rule_n(c: dict) -> float:
    """The fail checks' limit for the wheel states a class allows: free_n with every wheel seen free, and with a wheel
    not seen free the least of free_n, held_wheel_n and held_axle_n, since it may be free, held or one of an axle held."""
    return LC8["free_n"] if c["wheels"] == "free" else min(LC8["free_n"], LC8["held_wheel_n"], LC8["held_axle_n"])


def test_the_tipping_table_reads_every_point_wheel_state_and_line():
    """The build reads the least pull that tips the trailer at every recovery point, with every wheel free, a wheel held
    and an axle held, at LC8a's three lines, at its five headings at the lugs and tongues and between them, and along
    the rail axis at the coupling, with the pull solved at the points' 78.5 kN ultimate as the reach."""
    vd, sd = LC8["vertical_deg"], LC8["sideways_deg"]
    assert TIP["reach_kn"] == LC8["tip"]["reach_n"] / 1000 == LC8["ultimate_n"] / 1000
    keys = {(x["where"], x["side"], x["wheels"], x["v"]) for x in TIP["least"]}
    pts = [(w, s) for w in ("front", "rear") for s in (-1, 1)] + [("coupling", 0)]
    assert keys == {(w, s, k, v) for w, s in pts for k in ("free", "wheel", "axle") for v in (-vd, 0, vd)}
    cells = {(x["where"], x["side"], x["wheels"], x["h"], x["v"]) for x in TIP["table"]}
    assert cells == {(w, s, k, h, v) for w, s in pts for k in ("free", "wheel", "axle") for v in (-vd, 0, vd)
                     for h in ((-sd, -sd // 2, 0, sd // 2, sd) if s else (0,))}
    assert all(x["headings"] >= 2 * sd // LC8["tip"]["step_deg"] + 1 for x in TIP["least"] if x["side"])
    for x in TIP["least"]:                  # the least over the headings read is at most the least at LC8a's own
        own = [c["tip"]["kn"] for c in TIP["table"] if c["tip"] and (c["where"], c["side"], c["wheels"], c["v"]) ==
               (x["where"], x["side"], x["wheels"], x["v"])]
        assert not own or (x["tip"] and x["tip"]["kn"] <= min(own) + 1e-9)


def test_every_situation_a_user_can_see_falls_in_one_class():
    """The classes are what a user tells apart in the field without instruments: the point the line is on, whether every
    wheel is seen free, and whether the line rises from the point. Each such situation falls in exactly one class, and a
    wheel not seen free is read with every state it could be in, free, one wheel held or an axle held, on any line."""
    for at in ("front", "rear", "coupling"):
        for seen in (True, False):
            for line in ("falling", "level", "rising"):
                hits = [c["id"] for c in CLASSES if c["at"] == at and (c["wheels"] == "free") == seen
                        and (c["line"] == "any" or (c["line"] == "low") == (line != "rising"))]
                assert len(hits) == 1, (at, seen, line, hits)
    for c in CLASSES:
        assert {x["wheels"] for x in _class_cells(c)} == KINDS[c["wheels"]], c["id"]
        assert c["line"] == "any" or c["wheels"] == "free"


def test_each_class_limit_is_the_lesser_of_the_frame_and_three_quarters_of_its_least_tip():
    """COMMON-RULES-29 and I2-127: each class's limit, one entry in the data, is the lesser of the fail checks' limit for
    the wheel states it allows and LC8a `tip` `margin` of the least pull that tips the trailer in it, over its points,
    wheel states, lines and headings, empty and fully loaded, coupled and uncoupled and at both bounds of the grip,
    rounded down to 5 kN, and recovery_rule gives the same."""
    margin = LC8["tip"]["margin"]
    assert margin == 0.75
    for c in CLASSES:
        tips = [x["tip"]["kn"] for x in _class_cells(c) if x["tip"]]
        lesser = _rule_n(c) if not tips else min(_rule_n(c), 5000 * math.floor(margin * min(tips) / 5 + 1e-9))
        assert c["limit_n"] == lesser, (c["id"], c["limit_n"], lesser, min(tips, default=None))
        assert c["limit_n"] % 5000 == 0 and 0 < c["limit_n"] <= LC8["force_n"]
        assert not tips or c["limit_n"] <= margin * min(tips) * 1000         # 4/3 of every limit still holds the trailer
        r = next(x for x in RULE["classes"] if x["id"] == c["id"])
        assert r["lesser_kn"] == r["limit_kn"] == c["limit_n"] / 1000 and r["cells"] == len(_class_cells(c))


def test_each_class_source_names_the_figures_it_rests_on():
    """Each class's source gives the fail checks' figure for it, its least tipping pull to 0.1 kN with the way that pull
    leans up or down, and where tipping sets the limit, 75 % of that pull."""
    for r in RULE["classes"]:
        src = next(c for c in CLASSES if c["id"] == r["id"])["source"]
        assert f"{r['rule_kn']:g} kN" in src, r["id"]
        t = r["tip"]
        if t:
            assert f"{t['kn']:.1f} kN" in src, r["id"]
        if r["governs"] == "tipping":
            assert f"{r['share_kn']:.1f} kN" in src and f"{abs(t['v']):g} degrees {'up' if t['v'] > 0 else 'down'}" in src, r["id"]
            assert t["h"] == 0 or f"{abs(t['h']):g} degrees across" in src, r["id"]


def test_each_class_least_tip_is_where_the_trailer_starts_to_tip():
    """Each class's least tipping pull, solved again at its own point, heading, line, wheel state, weight, nose and bound
    of the grip: the trailer holds the pull 1 % under it and tips 1 % over it."""
    for r in RULE["classes"]:
        t = r["tip"]
        if not t:
            continue
        p, _, sx = AN.recovery_point(t["where"], t["side"])
        sup = next(s for s in SUP if s["label"].split(",")[0] == t["weight"] and bool(s["nose"].get("holds_down")) == t["coupled"])
        held = tuple(t["held"]) if isinstance(t["held"], list) else t["held"]
        for k, holds in ((0.99, True), (1.01, False)):
            R = AN.recovery_reactions(_pull(k * t["kn"] * 1000, sx, t["h"], t["v"]), p, held, sup["base"], sup["nose"], t["mu"])
            assert (R["limit"] is None) == holds and (R["limit"] in (None, "tips")), (r["id"], k, R["limit"], R["scale"])


def test_the_tipping_pulls_along_the_line_agree_with_a_hand_moment_balance():
    """Pulled along the trailer's line, up at the coupling or down at a rear tongue, the empty trailer uncoupled tips
    once its nose and front tyres have lifted and its rear tyres carry it all, so a moment balance about the rear tyres'
    contact line gives the pull, the ground's force along the trailer acting at the hubs:
    at the coupling F (x_r sin v - (z_c - z_h) cos v) = W (x_r - x_g), and at the tongue
    F ((x_t - x_r) sin v + (z_t - z_h) cos v) = W (x_r - x_g)."""
    sup = next(s for s in SUP if s["label"] == "TC1 at tare, uncoupled")
    m = sum(it.m for it in sup["items"])
    W, xg = m * 9.81, sum(it.m * it.p[0] for it in sup["items"]) / m
    rear = [w for w in CH.suspension if w["axle"] == "rear"]
    xr, zh = rear[0]["contact"][0], rear[0]["hub"][2]
    v = math.radians(LC8["vertical_deg"])
    zc = CH.V["coupling_z"]
    pt, _, _ = AN.recovery_point("rear", -1)
    hand = {("coupling", LC8["vertical_deg"]): W * (xr - xg) / (xr * math.sin(v) - (zc - zh) * math.cos(v)),
            ("rear", -LC8["vertical_deg"]): W * (xr - xg) / ((pt[0] - xr) * math.sin(v) + (pt[2] - zh) * math.cos(v))}
    for (where, vv), F in hand.items():
        cell = next(c for c in TIP["table"] if c["where"] == where and c["wheels"] == "free" and c["h"] == 0 and c["v"] == vv
                    and c["side"] in (0, -1))
        assert cell["tip"]["weight"] == "TC1 at tare" and not cell["tip"]["coupled"]
        assert abs(cell["tip"]["kn"] * 1000 - F) < 0.002 * F, (where, cell["tip"]["kn"], F / 1000)


def test_the_least_slide_with_every_wheel_free_is_on_wet_grass_at_tare():
    """The least pull that slides the trailer sideways with every wheel free, which the texts give, is where the tyres
    hold least across: at the lower bound of the grip, at tare and at the full sideways heading. It is the least in the
    table's every-wheel-free entries at the lugs and tongues."""
    s = RULE["slide"]
    assert s["mu"] == min(MUS) and s["weight"] == "TC1 at tare" and abs(s["h"]) == LC8["sideways_deg"]
    assert s["kn"] == min(x["slide"]["kn"] for x in TIP["least"] if x["slide"] and x["wheels"] == "free" and x["side"])


def _bullet(text: str, head: str) -> str:
    """A markdown list item that starts with `head`, with its indented lines."""
    lines = text.splitlines()
    i = next(k for k, x in enumerate(lines) if x.startswith(head))
    out = [lines[i]]
    for x in lines[i + 1:]:
        if x.startswith("- ") or x.startswith("#"):
            break
        out.append(x)
    return "\n".join(out)


def _tip_text(t: dict) -> str:
    """A tipping pull in the texts' words: its size, its point, its heading across the trailer or outward from it, read
    from the point's side and the heading's sign, and its line up or down."""
    at = {"front": "a front lug", "rear": "a rear tongue"}.get(t["where"], "the coupling")
    way = f"{abs(t['v']):g} degrees {'up' if t['v'] > 0 else 'down'}"
    if not t["h"]:
        return f"{t['kn']:.1f} kN at {at} pulled along its line and {way}"
    side = "across the trailer" if (t["h"] > 0) != (t["side"] > 0) else "outward"
    return f"{t['kn']:.1f} kN at {at} pulled {abs(t['h']):g} degrees {side} and {way}"


def _check_text(text: str, where: str):
    """A recovery text gives the table, a row for each point and a column for each class, and the rules with it."""
    names = {"front": "A front lug", "rear": "A rear tongue", "coupling": "The coupling"}
    cols = [("free", "low"), ("free", "up"), ("unseen", "any")]
    flat = re.sub(r"\s+", " ", text)
    for at, name in names.items():
        row = next((x.strip() for x in text.splitlines() if x.strip().startswith(f"| {name} |")), None)
        assert row, (where, name)
        cells = [x.strip() for x in row.strip("|").split("|")][1:]
        want = [f"{next(c for c in CLASSES if (c['at'], c['wheels'], c['line']) == (at, w, ln))['limit_n'] / 1000:g} kN" for w, ln in cols]
        assert cells == want, (where, name, cells, want)
    from cad.drawings.home_sheets import recovery_tips
    for t in recovery_tips(RULE):
        assert _tip_text(t) in flat, (where, _tip_text(t))
    for phrase in ("load cell", "rated line pull on the layer in use", "snatch block at the point doubles", "kinetic rope",
                   "snatch strap", f"slides the empty trailer toward it from {RULE['slide']['kn']:.1f} kN", "1.5 times", "75 %",
                   "counts as held", f"within {RULE['sideways_deg']:g} degrees", f"within {RULE['vertical_deg']:g} degrees up or down",
                   f"{RULE['reach_kn']:.1f} kN ultimate"):
        assert phrase in flat, (where, phrase)
    assert ("Pulled level it does not tip" in flat) == (not RULE["level_tips"]), where


def test_trailer_md_and_the_chassis_page_give_the_recovery_table_and_rules():
    """TRAILER.md's recovery line and the Chassis page's recovery section give each class's limit in a table by the point
    and what can be seen, each tipping pull a limit rests on with its own direction, how the force at the point is known,
    the slide on wet grass and where people stand, all from the data and the build (I2-127)."""
    _check_text(_bullet((ROOT / "TRAILER.md").read_text(encoding="utf-8"), "- Recovery:"), "TRAILER.md")
    page = (ROOT / "site" / "src" / "content" / "docs" / "chassis.mdx").read_text(encoding="utf-8")
    _check_text(page.split("## Recovery limits", 1)[1].split("\n## ", 1)[0], "chassis.mdx")


def test_ct003_gives_the_recovery_table_and_each_tip_its_own_direction():
    """CT-003's recovery texts (home_sheets.recovery_texts) give the classes' limits in their table cells, and each
    tipping pull a limit rests on with its own point, heading and line, up or down as the build reads it
    (FX38-MRG-PROGRESS.md item 6), with the rules TRAILER.md gives."""
    from cad.drawings.home_sheets import RECOVERY_COLUMNS, RECOVERY_POINTS, recovery_texts, recovery_tips
    rec = recovery_texts(RES, LC8, TRAILER.tv)
    for (at, _), row in zip(RECOVERY_POINTS, rec["rows"]):
        for ((w, ln), _), cell in zip(RECOVERY_COLUMNS, row[1:]):
            assert cell == f"{next(c for c in CLASSES if (c['at'], c['wheels'], c['line']) == (at, w, ln))['limit_n'] / 1000:g} kN"
    notes = " ".join(rec["notes"])
    for t in recovery_tips(RULE):
        assert _tip_text(t).upper().replace(" KN ", " kN ") in notes
    for phrase in ("LOAD CELL", "RATED LINE PULL ON THE LAYER IN USE", "SNATCH BLOCK AT THE POINT DOUBLES", "KINETIC ROPE",
                   "SNATCH STRAP", f"{RULE['slide']['kn']:.1f} kN", "1.5 TIMES", "NOT FREE"):
        assert phrase in notes, phrase
    assert f"WITHIN {LC8['sideways_deg']:g} DEGREES SIDEWAYS" in rec["where"] and f"WITHIN {LC8['vertical_deg']:g} DEGREES UP OR DOWN" in rec["where"]

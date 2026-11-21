"""The trailer's priced parts list (data/trailer-parts.yaml with the priced lines of data/assemblies/trailer.yaml and
data/chassis/chassis.yaml, put together by cad/trailer_costs.py): every tare line of the mass schedule is priced once,
the steel bought covers the cut list, the totals add up from the lines, the blocks' shares add up to the list, and the
home page's cost table quotes the list's totals."""
import re
from collections import defaultdict

import yaml

from cad.partsdb import DATA
from cad.sitedata import project_costs
from cad.tests.test_trailer import EV
from cad.trailer_costs import BASES, block_prices, instances, parts_list

LIST = parts_list()
LINES = LIST["lines"]
TOT = LIST["totals"]
PCT = TOT["contingency_pct"]
BLOCKS = EV["layout"].blocks
TARE = [b for b in BLOCKS if b.load == "tare" and not b.keep_clear]
ITEMS = yaml.safe_load((DATA / "assemblies" / "trailer.yaml").read_text())["items"]
BOX = yaml.safe_load((DATA / "ute" / "box-parts.yaml").read_text())["totals"]
PUBLIC_WORDS = re.compile(r";|\u2014|\bconductor|\bworker|\bR(19|2[0-6])\b")


def _parts(ln):
    return ln.get("parts") or [dict(aud=ln["price"]["aud"], basis=ln["price"]["basis"])]


def test_every_tare_line_is_priced_once():
    own = {ln["id"] for ln in LINES if not ln.get("covers")}
    covered = defaultdict(list)
    for ln in LINES:
        for i in ln.get("covers") or []:
            covered[i].append(ln["id"])
    ids = {b.id for b in BLOCKS}
    assert not set(covered) - ids, f"lines cover unknown schedule lines: {sorted(set(covered) - ids)}"
    for b in TARE:
        n = (b.id in own) + len(covered[b.id])
        assert n == 1, f"{b.iid} is priced {n} times: own {b.id in own}, covered by {covered[b.id]}"


def test_each_priced_item_has_the_layouts_instances():
    count = defaultdict(int)
    for b in BLOCKS:
        count[b.id] += 1
    for it in ITEMS:
        if "price" in it:
            assert instances(it) == count[it["id"]], f"{it['id']}: {instances(it)} instances priced, {count[it['id']]} in the layout"


def test_prices_are_well_formed():
    lines = {ln["id"] for ln in LINES}
    for ln in LINES:
        for p in ln.get("parts") or [ln["price"]]:
            assert p["basis"] in BASES, f"{ln['id']}: basis {p['basis']}"
            assert re.fullmatch(r"2026-\d\d-\d\d", str(p["date"])), f"{ln['id']}: date {p['date']}"
            assert p["aud"] >= 0, ln["id"]
            assert not p.get("url") or p["url"].startswith("http"), f"{ln['id']}: url {p['url']}"
            if ln.get("parts"):
                assert p.get("item"), f"{ln['id']}: a part without an item"
        inc = ln["price"].get("included_in")
        if inc:
            assert inc in lines and ln["price"]["aud"] == 0, f"{ln['id']} is included in {inc}"
        elif ln["price"]["aud"] == 0:
            assert False, f"{ln['id']} costs nothing but names no line that includes it"


def test_public_text_follows_the_style_rules():
    for ln in LINES:
        texts = [ln["name"], ln.get("note") or "", ln["price"].get("note") or ""]
        texts += [f"{p.get('item', '')} {p.get('note', '')}" for p in ln.get("parts") or []]
        for s in texts:
            assert not PUBLIC_WORDS.search(s), f"{ln['id']}: {s!r}"
    for s in (TOT["contingency_why"], TOT["owner_built_why"], *(x["note"] for x in LIST["not_in_total"])):
        assert not PUBLIC_WORDS.search(s), s


def test_totals_add_up():
    by, cont = defaultdict(float), defaultdict(float)
    for ln in LINES:
        assert abs(sum(p["aud"] for p in _parts(ln)) - ln["price"]["aud"]) < 0.011, ln["id"]
        by[ln["group"]] += ln["price"]["aud"]
        c = sum(p["aud"] * PCT[p["basis"]] / 100 for p in _parts(ln))
        assert abs(c - ln["contingency_aud"]) < 0.011, f"{ln['id']}: contingency {ln['contingency_aud']}, its parts give {c:.2f}"
        cont[ln["group"]] += c
    assert set(by) == set(TOT["by_group"])
    for g, v in by.items():
        assert abs(TOT["by_group"][g] - v) < 0.011, f"group {g}: totals {TOT['by_group'][g]}, lines {v:.2f}"
        assert abs(TOT["contingency_by_group"][g] - cont[g]) < 0.011, g
    sub, c = sum(by.values()), sum(cont.values())
    assert abs(TOT["subtotal_aud"] - sub) < 0.011 and abs(TOT["contingency_aud"] - c) < 0.011
    assert abs(TOT["total_aud"] - sub - c) < 0.011
    hired = sum(by[g] + cont[g] for g in TOT["owner_built_leaves_out"])
    assert hired > 0 and abs(TOT["owner_built_total_aud"] - (sub + c - hired)) < 0.011
    assert abs(sum(TOT["by_basis"].values()) - sub) < 0.05


def test_the_steel_bought_covers_the_cut_list():
    by_id = defaultdict(list)
    for b in BLOCKS:
        by_id[b.id].append(b)
    for ln in LINES:
        covered = [b for i in ln.get("covers") or [] for b in by_id[i]]
        if ln["unit"] == "8 m length":
            need = sum(b.qty for b in covered)
            assert ln["qty"] * 8 >= need, f"{ln['id']}: {ln['qty']} lengths for {need:.2f} m of cut members"
        elif ln["unit"] in ("kg", "kg galvanised"):
            need = sum(b.mass_kg for b in covered)
            if ln["unit"] == "kg galvanised":
                need += sum(b.mass_kg for b in BLOCKS if b.system == "chassis" and b.extra.get("member")
                            or b.extra.get("fitting") and b.extra["fitting"].kind in ("plate", "tube"))
            assert ln["qty"] >= need, f"{ln['id']}: {ln['qty']} kg bought for {need:.1f} kg"


def test_block_shares_add_up_to_the_list():
    prices = block_prices(BLOCKS, LIST)
    ids = {b.id for b in BLOCKS}
    on_blocks = sum(ln["price"]["aud"] for ln in LINES if ln.get("covers") or ln["id"] in ids)
    assert abs(sum(p["price_aud"] for p in prices.values()) - on_blocks) < 0.005 * len(prices) + 0.01
    for b in TARE:
        assert b.iid in prices, f"{b.iid} has no price"


def test_the_cost_table_quotes_the_list():
    t = project_costs(BOX)
    row = next(r for r in t["rows"] if r["id"] == "trailer")
    assert not row.get("pending") and t["pending"] == []
    assert abs(row["before"] - TOT["subtotal_aud"]) < 0.011
    assert abs(row["contingency"] - TOT["contingency_aud"]) < 0.011
    assert abs(row["total"] - TOT["total_aud"]) < 0.011
    assert abs(row["owner_built"] - TOT["owner_built_total_aud"]) < 0.011

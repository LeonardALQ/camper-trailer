"""Data rules: bike envelopes match the owner's figures, and the masses reproduce garage-bed/BOM.md."""
import pytest

from cad import massprops as MP
from cad.tests.test_checks import MODEL, PRJ

# garage-bed/BOM.md revision B totals (kg)
BOM_MD = {"garage": 95.6, "bed": 54.2, "partitions": 30.2, "fixings": 3.1, "access": 2.6,
          "module_empty": 185.7, "removable": 75.7, "with_bikes": 566.7}
LINES = MP.line_masses(PRJ, MODEL)
BIKES = sum(b["mass_kg"] for b in MP.bike_rows(PRJ, MODEL))


def _total(key, rounded):
    """Model total for a BOM.md row. With rounded=True each line is first rounded to 0.1 kg, as BOM.md does."""
    def m(r):
        return round(r["mass_kg"], 1) if rounded else r["mass_kg"]
    if key == "module_empty":
        return sum(m(r) for r in LINES)
    if key == "removable":
        return sum(m(r) for r in LINES if r["removable"])
    if key == "with_bikes":
        return sum(m(r) for r in LINES) + BIKES
    return sum(m(r) for r in LINES if r["group"] == key)


def _lines_in(key):
    if key in ("module_empty", "with_bikes"):
        return len(LINES)
    if key == "removable":
        return sum(1 for r in LINES if r["removable"])
    return sum(1 for r in LINES if r["group"] == key)


@pytest.mark.parametrize("ref", ["TU", "ST"])
@pytest.mark.parametrize("dim", ["length", "width", "height"])
def test_bike_matches_owner(ref, dim):
    b = MODEL.built[ref]
    got, want = b.info["local_size"][dim], b.info["owner"][dim]
    assert abs(got - want) <= 10, f"{ref} {dim}: model {got:.1f} mm, owner {want} mm"


def test_tuareg_mirrors_not_above_screen():
    s = MODEL.built["TU"].bike.model.solids
    screen = s["screen"].bounding_box().max.Z
    for side in ("left", "right"):
        assert s[f"mirror {side} (folded)"].bounding_box().max.Z <= screen


def test_tuareg_width_with_bags_matches_owner():
    b = MODEL.built["TU"]
    got, want = b.info["width_with_bags"], b.info["owner"]["width_with_bags"]
    assert abs(got - want) <= 10, f"Tuareg with panniers: model {got:.1f} mm wide, owner {want} mm"


@pytest.mark.parametrize("key", list(BOM_MD))
def test_mass_matches_bom_md(key):
    """Each line rounded to 0.1 kg (as BOM.md rounds them) must sum to the BOM.md total, and the
    unrounded total may differ only by that rounding (at most 0.05 kg per line)."""
    rounded, exact = _total(key, True), _total(key, False)
    assert abs(rounded - BOM_MD[key]) < 0.051, f"{key}: lines rounded to 0.1 kg sum to {rounded:.2f}, BOM.md {BOM_MD[key]}"
    assert abs(exact - BOM_MD[key]) <= 0.05 * _lines_in(key) + 1e-9, f"{key}: model {exact:.2f} kg, BOM.md {BOM_MD[key]}"

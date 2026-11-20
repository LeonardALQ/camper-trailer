"""Data rules: the bike envelopes in the ute's bike box match the owner's figures."""
import pytest

from cad.tests.test_ute import GMODEL


@pytest.mark.parametrize("ref", ["TU", "ST"])
@pytest.mark.parametrize("dim", ["length", "width", "height"])
def test_bike_matches_owner(ref, dim):
    b = GMODEL.built[ref]
    got, want = b.info["local_size"][dim], b.info["owner"][dim]
    assert abs(got - want) <= 10, f"{ref} {dim}: model {got:.1f} mm, owner {want} mm"


def test_tuareg_mirrors_not_above_screen():
    s = GMODEL.built["TU"].bike.model.solids
    screen = s["screen"].bounding_box().max.Z
    for side in ("left", "right"):
        assert s[f"mirror {side} (folded)"].bounding_box().max.Z <= screen


def test_tuareg_width_with_bags_matches_owner():
    b = GMODEL.built["TU"]
    got, want = b.info["width_with_bags"], b.info["owner"]["width_with_bags"]
    assert abs(got - want) <= 10, f"Tuareg with panniers: model {got:.1f} mm wide, owner {want} mm"

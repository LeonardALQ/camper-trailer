"""DIM-01 is right-handed: X rearward, Y positive to the road side (the right), Z up. These tests pin which side
each item is on, so the 3D model, the STEP file and the drawings show the real trailer and ute, not their mirror
images."""
from cad.tests.test_trailer import EV
from cad.tests.test_ute import GMODEL

LAYOUT = EV["layout"]


def _centre_y(shape):
    bb = shape.bounding_box()
    return (bb.min.Y + bb.max.Y) / 2


def _block_centre_y(iid):
    b = LAYOUT.find(iid).box
    return (b[1] + b[4]) / 2


def test_entry_door_awning_battery_and_toilet_are_on_the_kerb_side():
    for iid in ("BD-07", "BD-13", "EL-01", "WR-06"):
        assert _block_centre_y(iid) < 0, iid


def test_kitchen_shower_tote_and_outdoor_unit_are_on_the_road_side():
    for iid in ("LA-11T", "LA-11B", "LA-07A", "WR-11", "AC-02"):
        assert _block_centre_y(iid) > 0, iid


def test_desk_is_centred_under_the_bed():
    assert abs(_block_centre_y("LA-09")) < 1


def test_tuareg_stands_on_the_road_side_of_the_bike_box():
    assert _centre_y(GMODEL.built["TU"].shape) > 0


def test_tuareg_silencer_on_its_right_and_side_stand_on_its_left():
    pb = GMODEL.built["TU"].bike
    centre = GMODEL.prj.P.values["tuareg_y"]
    solids = pb.model.solids
    assert _centre_y(pb.place(solids["silencer (right)"])) > centre
    assert _centre_y(pb.place(solids["side stand (folded)"])) < centre


def test_bike_box_kerb_door_is_on_the_kerb_side():
    assert _centre_y(GMODEL.built["D4"].shape) < 0

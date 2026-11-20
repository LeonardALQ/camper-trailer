"""DIM-01 is right-handed: X rearward, Y positive to the road side (the right), Z up. These tests pin which side
each item is on, so the 3D model, the STEP file and the drawings show the real trailer and not its mirror image."""
from cad.tests.test_checks import MODEL, PRJ
from cad.trailer import ModuleInfo, Trailer

LAYOUT = Trailer(PRJ, ModuleInfo.from_model(PRJ, MODEL)).layout()


def _centre_y(shape):
    bb = shape.bounding_box()
    return (bb.min.Y + bb.max.Y) / 2


def _block_centre_y(iid):
    b = LAYOUT.find(iid).box
    return (b[1] + b[4]) / 2


def test_gas_locker_and_its_hatch_are_on_the_kerb_side():
    if "21" not in MODEL.built:   # no LPG (owner option): the corner is stowage, which the kerb-strip zone covers
        assert LAYOUT.zones["kerb_strip"]["box"][4] < 0
        return
    assert _centre_y(MODEL.built["21"].shape) < 0
    assert _centre_y(MODEL.built["C9"].shape) < 0
    assert _block_centre_y("BD-06") < 0


def test_entry_door_is_on_the_kerb_side():
    assert _block_centre_y("BD-07") < 0


def test_tuareg_stands_on_the_road_side():
    assert _centre_y(MODEL.built["TU"].shape) > 0


def test_tuareg_silencer_on_its_right_and_side_stand_on_its_left():
    pb = MODEL.built["TU"].bike
    centre = PRJ.P.values["tuareg_y"]
    solids = pb.model.solids
    assert _centre_y(pb.place(solids["silencer (right)"])) > centre
    assert _centre_y(pb.place(solids["side stand (folded)"])) < centre

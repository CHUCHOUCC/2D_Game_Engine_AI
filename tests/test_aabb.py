from app.physics import AABB


def box(cx, cy, w=32, h=32):
    return AABB(cx, cy, w / 2, h / 2)


def test_edges_come_from_centre_and_half_size():
    b = box(100, 50, 40, 20)
    assert (b.left, b.right, b.top, b.bottom) == (80, 120, 40, 60)



def test_of_object_uses_the_kind_size():
    house = AABB.of_object({"id": "h", "kind": "house", "x": 200, "y": 200})
    assert (house.half_w, house.half_h) == (48, 48)
    unknown = AABB.of_object({"id": "u", "kind": "ufo", "x": 0, "y": 0})
    assert unknown.half_w == 16



def test_overlap_and_touching_edges():
    assert box(0, 0).overlaps(box(31, 0))
    assert not box(0, 0).overlaps(box(32, 0))  # edges touch, no overlap
    assert box(0, 0).overlaps(box(34, 0), padding=4)



def test_penetration_pushes_along_the_axis_of_least_overlap():
    assert box(0, 0).penetration(box(30, 5)) == (-2.0, 0.0)
    assert box(0, 0).penetration(box(5, -30)) == (0.0, 2.0)
    assert box(0, 0).penetration(box(100, 100)) == (0.0, 0.0)

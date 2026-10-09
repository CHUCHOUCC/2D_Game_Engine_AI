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

from app.physics import AABB


def box(cx, cy, w=32, h=32):
    return AABB(cx, cy, w / 2, h / 2)


def test_edges_come_from_centre_and_half_size():
    b = box(100, 50, 40, 20)
    assert (b.left, b.right, b.top, b.bottom) == (80, 120, 40, 60)

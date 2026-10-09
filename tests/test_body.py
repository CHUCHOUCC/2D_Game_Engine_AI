from app.physics import KIND_PHYSICS, Body


def test_walls_are_static_and_boxes_dynamic():
    wall = Body.of_object({"id": "w", "kind": "wall", "x": 10, "y": 10})
    crate = Body.of_object({"id": "b", "kind": "box", "x": 10, "y": 10})
    assert wall.static and not crate.static
    assert crate.mass == 2.0 and crate.drag == 400.0

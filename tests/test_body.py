from app.physics import KIND_PHYSICS, Body


def test_walls_are_static_and_boxes_dynamic():
    wall = Body.of_object({"id": "w", "kind": "wall", "x": 10, "y": 10})
    crate = Body.of_object({"id": "b", "kind": "box", "x": 10, "y": 10})
    assert wall.static and not crate.static
    assert crate.mass == 2.0 and crate.drag == 400.0


def test_every_kind_has_physics():
    from app.world import ALL_KINDS

    assert set(KIND_PHYSICS) == set(ALL_KINDS)


def test_coins_and_spikes_do_not_block():
    assert not Body.of_object({"id": "c", "kind": "coin", "x": 0, "y": 0}).solid
    assert not Body.of_object({"id": "s", "kind": "spike", "x": 0, "y": 0}).solid
    assert Body.of_object({"id": "e", "kind": "enemy", "x": 0, "y": 0}).solid


def test_to_object_round_trip():
    obj = {"id": "b", "kind": "box", "x": 12.34, "y": 50}
    assert Body.of_object(obj).to_object() == {"id": "b", "kind": "box", "x": 12.3, "y": 50.0}

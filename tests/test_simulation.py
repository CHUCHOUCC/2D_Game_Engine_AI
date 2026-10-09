from app.physics import Body, PhysicsWorld


def obj(id, kind, x, y):
    return {"id": id, "kind": kind, "x": x, "y": y}


def test_velocity_moves_a_dynamic_body_and_drag_slows_it():
    world = PhysicsWorld()
    crate = world.add(Body.of_object(obj("b", "box", 100, 100)))
    crate.vx = 200
    world.step(0.1)
    assert crate.box.cx == 120
    assert crate.vx == 160  # 200 - drag 400 * 0.1



def test_static_bodies_ignore_velocity():
    world = PhysicsWorld()
    wall = world.add(Body.of_object(obj("w", "wall", 100, 100)))
    wall.vx = 500
    world.step(1)
    assert wall.box.cx == 100



def test_drag_stops_but_never_reverses():
    world = PhysicsWorld()
    crate = world.add(Body.of_object(obj("b", "box", 100, 100)))
    crate.vx, crate.vy = 10, -10
    world.step(1)
    assert (crate.vx, crate.vy) == (0, 0)



def test_bodies_are_kept_inside_the_world():
    world = PhysicsWorld()
    enemy = world.add(Body.of_object(obj("e", "enemy", 20, 20)))
    enemy.vx = -1000
    world.step(0.1)
    assert enemy.box.left == 0
    assert enemy.vx > 0  # bounced

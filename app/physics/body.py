from dataclasses import dataclass, field

from .aabb import AABB

# Arcade Physics settings per kind; the frontend uses the same numbers.
# (static, mass, drag, bounce)
KIND_PHYSICS = {
    "player": (False, 1.0, 600.0, 0.0),
    "box": (False, 2.0, 400.0, 0.1),
    "wall": (True, 1.0, 0.0, 0.0),
    "house": (True, 1.0, 0.0, 0.0),
    "tree": (True, 1.0, 0.0, 0.0),
    "spike": (True, 1.0, 0.0, 0.0),
    "coin": (True, 1.0, 0.0, 0.0),
    "enemy": (False, 1.5, 200.0, 0.2),
}



@dataclass
class Body:
    """A simulated object: its box, velocity and how it reacts to collisions."""

    id: str
    kind: str
    box: AABB
    static: bool = True
    mass: float = 1.0
    drag: float = 0.0
    bounce: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    touching: set = field(default_factory=set)

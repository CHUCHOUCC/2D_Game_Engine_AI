from dataclasses import asdict, dataclass, field

from app.world import OBSTACLE_KINDS

MODEL_VERSION = 1
MIN_DIFFICULTY = 0.05
MAX_DIFFICULTY = 0.95
MIN_WEIGHT = 0.05

# How likely each kind is to be picked when the AI places an obstacle.
DEFAULT_WEIGHTS = {
    "box": 1.0,
    "wall": 1.0,
    "tree": 0.7,
    "house": 0.3,
    "spike": 0.5,
    "enemy": 0.6,
}

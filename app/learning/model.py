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



@dataclass
class LevelModel:
    """Everything the AI knows about one level, learned from the runs played on it.

    - difficulty: 0 (trivial) to 1 (brutal); drives how many and how nasty obstacles are.
    - win_rate, coin_ratio, damage, run_seconds: moving averages of what players did.
    - weights: preference for each obstacle kind.
    """

    difficulty: float = 0.5
    runs: int = 0
    win_rate: float = 0.5
    coin_ratio: float = 0.5
    damage: float = 0.0
    run_seconds: float = 60.0
    weights: dict = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    version: int = MODEL_VERSION

    def to_dict(self) -> dict:
        return asdict(self)

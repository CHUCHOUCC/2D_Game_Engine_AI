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

    @classmethod
    def from_dict(cls, data) -> "LevelModel":
        """Read a model sent by the backend. Missing or bad values fall back to
        defaults, so a corrupted row can never crash the service."""
        model = cls()
        if not isinstance(data, dict):
            return model
        model.difficulty = _number(data.get("difficulty"), model.difficulty, MIN_DIFFICULTY, MAX_DIFFICULTY)
        model.runs = int(_number(data.get("runs"), 0, 0, 10**9))
        model.win_rate = _number(data.get("win_rate"), model.win_rate, 0, 1)
        model.coin_ratio = _number(data.get("coin_ratio"), model.coin_ratio, 0, 1)
        model.damage = _number(data.get("damage"), model.damage, 0, 1000)
        model.run_seconds = _number(data.get("run_seconds"), model.run_seconds, 0, 3600)
        weights = data.get("weights")
        if isinstance(weights, dict):
            for kind in OBSTACLE_KINDS:
                model.weights[kind] = _number(weights.get(kind), model.weights[kind], MIN_WEIGHT, 10)
        return model

    def obstacle_budget(self) -> int:
        """The AI learns to create more obstacles as players master the level:
        4 at difficulty 0 up to 20 at difficulty 1."""
        return round(4 + 16 * self.difficulty)

    def probabilities(self) -> dict:
        total = sum(self.weights.values())
        return {kind: weight / total for kind, weight in self.weights.items()}


def _number(value, default: float, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value != value:
        return default
    return min(high, max(low, float(value)))

import math

from .features import RunFeatures, RunSummary
from .model import MAX_DIFFICULTY, MIN_DIFFICULTY, MIN_WEIGHT, LevelModel
from .reward import TARGET_PERFORMANCE, reward_with_quit_penalty

# Weight of the newest run in the moving averages.
AVERAGE_RATE = 0.3


class Learner:
    """Online learning from each finished run (no training data set needed).

    After every run the model moves its difficulty towards the point where
    players perform near the target, and shifts its preference between
    obstacle kinds according to what hurt or did not hurt the player.
    """

    def learning_rate(self, runs: int) -> float:
        """Big steps for a new level, smaller ones as evidence piles up."""
        return max(0.05, 0.3 / math.sqrt(runs + 1))

    def _update_averages(self, model: LevelModel, features: RunFeatures) -> None:
        a = AVERAGE_RATE if model.runs else 1.0
        model.win_rate += a * (features.won - model.win_rate)
        model.coin_ratio += a * (features.coin_ratio - model.coin_ratio)
        model.damage += a * (features.damage - model.damage)
        model.run_seconds += a * (features.seconds - model.run_seconds)

    def _update_difficulty(self, model: LevelModel, performance: float, rate: float) -> None:
        # Played well -> harder; struggled -> easier.
        change = 2 * rate * (performance - TARGET_PERFORMANCE)
        model.difficulty = min(MAX_DIFFICULTY, max(MIN_DIFFICULTY, model.difficulty + change))

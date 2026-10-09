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

    def _update_weights(self, model: LevelModel, features: RunFeatures, rate: float) -> None:
        w = model.weights
        hurt = min(features.damage / 5.0, 1.0)
        if features.won and hurt < 0.4:
            # Easy win: enemies and spikes were not a threat, use them more.
            w["enemy"] *= 1 + rate
            w["spike"] *= 1 + rate
        elif not features.won and hurt >= 0.6:
            # The player was overwhelmed by hazards: fewer of them.
            w["enemy"] *= 1 - rate / 2
            w["spike"] *= 1 - rate / 2
        if not features.won and features.coin_ratio < 0.5:
            # Coins were hard to reach: the maze is too closed.
            w["wall"] *= 1 - rate / 2
            w["house"] *= 1 - rate / 2
        if features.won and features.coin_ratio == 1.0:
            # Every coin was collected easily: build more walls and boxes around them.
            w["wall"] *= 1 + rate / 2
            w["box"] *= 1 + rate / 2
        if features.kills >= 3:
            # A good fighter: more enemies make the level interesting.
            w["enemy"] *= 1 + rate / 2
        for kind in w:
            w[kind] = round(min(10.0, max(MIN_WEIGHT, w[kind])), 4)

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

import pytest
from pydantic import ValidationError

from app.learning import RunFeatures, RunSummary, reward
from app.learning.reward import TARGET_PERFORMANCE, reward_with_quit_penalty

BASE = dict(outcome="won", score=100, coins_collected=4, coins_total=4, enemies_defeated=1,
            damage_taken=0, deaths=0, duration_ms=30000)


def run(**changes):
    return RunSummary(**{**BASE, **changes})


def test_run_summary_rejects_unknown_outcomes_and_negatives():
    with pytest.raises(ValidationError):
        run(outcome="draw")
    with pytest.raises(ValidationError):
        run(score=-1)



def test_features_of_a_run():
    features = RunFeatures.of(run(coins_collected=2, damage_taken=3, duration_ms=1500))
    assert features.won == 1.0 and features.quit == 0.0
    assert features.coin_ratio == 0.5
    assert features.damage == 3.0
    assert features.seconds == 1.5



def test_a_level_without_coins_counts_as_all_coins_taken():
    assert RunFeatures.of(run(coins_collected=0, coins_total=0)).coin_ratio == 1.0



def test_performance_from_perfect_to_crushed():
    assert RunFeatures.of(run()).performance() == 1.0
    crushed = run(outcome="lost", coins_collected=0, damage_taken=9, deaths=3)
    assert RunFeatures.of(crushed).performance() == 0.0
    middle = RunFeatures.of(run(outcome="lost", coins_collected=2, damage_taken=0)).performance()
    assert 0.0 < middle < 1.0

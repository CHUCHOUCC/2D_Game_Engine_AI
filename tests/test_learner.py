from app.learning import Learner, LevelModel, RunSummary

EASY_WIN = dict(outcome="won", score=200, coins_collected=5, coins_total=5, enemies_defeated=0,
                damage_taken=0, deaths=0, duration_ms=20000)
HARD_LOSS = dict(outcome="lost", score=10, coins_collected=1, coins_total=5, enemies_defeated=0,
                 damage_taken=6, deaths=2, duration_ms=60000)


def learn(model, data, times=1):
    rewards = []
    for _ in range(times):
        model, value = Learner().learn(model, RunSummary(**data))
        rewards.append(value)
    return model, rewards


def test_learning_rate_shrinks_but_never_reaches_zero():
    learner = Learner()
    assert learner.learning_rate(0) == 0.3
    assert learner.learning_rate(3) < learner.learning_rate(0)
    assert learner.learning_rate(10_000) == 0.05



def test_easy_wins_raise_difficulty_and_the_obstacle_budget():
    model, _ = learn(LevelModel(), EASY_WIN, times=5)
    assert model.difficulty > 0.5
    assert model.obstacle_budget() > LevelModel().obstacle_budget()
    assert model.runs == 5



def test_hard_losses_lower_difficulty():
    model, _ = learn(LevelModel(), HARD_LOSS, times=5)
    assert model.difficulty < 0.5



def test_difficulty_stays_within_bounds():
    high, _ = learn(LevelModel(), EASY_WIN, times=200)
    low, _ = learn(LevelModel(), HARD_LOSS, times=200)
    assert high.difficulty <= 0.95
    assert low.difficulty >= 0.05

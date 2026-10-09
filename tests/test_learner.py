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


def test_easy_wins_favour_hazards():
    model, _ = learn(LevelModel(), EASY_WIN, times=3)
    assert model.weights["enemy"] > 0.6
    assert model.weights["spike"] > 0.5


def test_overwhelmed_players_get_fewer_hazards_and_more_open_levels():
    model, _ = learn(LevelModel(), HARD_LOSS, times=3)
    assert model.weights["enemy"] < 0.6
    assert model.weights["wall"] < 1.0


def test_first_run_sets_the_averages_and_later_runs_blend():
    model, _ = learn(LevelModel(), EASY_WIN)
    assert model.win_rate == 1.0
    model, _ = learn(model, HARD_LOSS)
    assert 0 < model.win_rate < 1.0


def test_rewards_improve_while_the_model_adapts_to_a_strong_player():
    model, rewards = learn(LevelModel(), EASY_WIN, times=1)
    first = rewards[0]
    # A stronger level makes the same player perform closer to the target.
    model.difficulty = 0.9
    tougher = dict(EASY_WIN, coins_collected=4, damage_taken=2)
    _, later = learn(model, tougher)
    assert later[0] > first

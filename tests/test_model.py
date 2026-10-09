from app.learning import LevelModel
from app.world import OBSTACLE_KINDS


def test_a_new_model_starts_in_the_middle():
    model = LevelModel()
    assert model.difficulty == 0.5
    assert model.runs == 0
    assert set(model.weights) == set(OBSTACLE_KINDS)


def test_to_dict_and_from_dict_round_trip():
    model = LevelModel(difficulty=0.7, runs=3)
    model.weights["enemy"] = 2.5
    assert LevelModel.from_dict(model.to_dict()) == model


def test_garbage_falls_back_to_defaults():
    assert LevelModel.from_dict(None) == LevelModel()
    assert LevelModel.from_dict("nonsense") == LevelModel()
    broken = LevelModel.from_dict({"difficulty": "hard", "runs": True, "weights": {"wall": "lots"}})
    assert broken.difficulty == 0.5
    assert broken.runs == 0
    assert broken.weights["wall"] == 1.0


def test_out_of_range_values_are_clamped():
    model = LevelModel.from_dict({"difficulty": 9, "win_rate": -3, "weights": {"spike": 0, "box": 99}})
    assert model.difficulty == 0.95
    assert model.win_rate == 0
    assert model.weights["spike"] == 0.05
    assert model.weights["box"] == 10
    assert LevelModel.from_dict({"difficulty": float("nan")}).difficulty == 0.5


def test_obstacle_budget_grows_with_difficulty():
    assert LevelModel(difficulty=0.05).obstacle_budget() == 5
    assert LevelModel(difficulty=0.5).obstacle_budget() == 12
    assert LevelModel(difficulty=0.95).obstacle_budget() == 19


def test_probabilities_sum_to_one():
    probabilities = LevelModel().probabilities()
    assert abs(sum(probabilities.values()) - 1) < 1e-9
    assert probabilities["box"] > probabilities["house"]

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

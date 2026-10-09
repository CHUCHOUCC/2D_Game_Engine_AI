from app.learning import LevelModel
from app.world import OBSTACLE_KINDS


def test_a_new_model_starts_in_the_middle():
    model = LevelModel()
    assert model.difficulty == 0.5
    assert model.runs == 0
    assert set(model.weights) == set(OBSTACLE_KINDS)

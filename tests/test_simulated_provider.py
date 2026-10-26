import json

from app.providers import SimulatedProvider


def ask(text):
    return json.loads(SimulatedProvider().complete("system", f"scene\nRequest: {text}"))


def test_every_kind_keyword():
    words = {"coin": "moneda", "enemy": "enemigo", "house": "casa", "wall": "pared",
             "tree": "arbol", "spike": "pinchos", "box": "caja"}
    for kind, word in words.items():
        assert ask(f"una {word}")[0]["kind"] == kind


def test_counts_in_digits_and_words():
    assert len(ask("3 monedas")) == 3
    assert len(ask("tres monedas")) == 3
    assert len(ask("two walls")) == 2
    assert len(ask("50 coins")) == 10  # capped


def test_several_kinds_in_one_request():
    kinds = [o["kind"] for o in ask("2 monedas y una casa, un enemigo")]
    assert kinds == ["coin", "coin", "house", "enemy"]


def test_position_after_en_or_at():
    obj = ask("una pared en 400 300")[0]
    assert (obj["x"], obj["y"]) == (400, 300)
    assert ask("a tree at (90, 70)")[0]["x"] == 90


def test_unknown_request_gives_one_box_in_the_middle():
    assert ask("algo bonito") == [{"id": "box-1", "kind": "box", "x": 800.0, "y": 480.0}]


def test_ids_are_unique():
    ids = [o["id"] for o in ask("3 monedas y 2 cajas")]
    assert len(ids) == len(set(ids)) == 5


def test_2d_characters_in_spanish_and_english():
    kinds = [o["kind"] for o in ask("un aldeano, 2 caballeros y un mago en 300 200")]
    assert kinds == ["villager", "knight", "knight", "wizard"]
    assert ask("a wizard")[0]["kind"] == "wizard"


def test_enemies_items_and_obstacles_in_spanish():
    request = ("un murciélago, una araña, un fantasma, un ogro, un cofre, una poción, "
               "una espada, un hacha, una varita, un arco, un barril, una valla y un arbusto")
    kinds = [o["kind"] for o in ask(request)]
    assert kinds == ["bat", "spider", "ghost", "brute", "chest", "potion", "sword", "axe", "wand", "bow",
                     "barrel", "fence", "bush"]

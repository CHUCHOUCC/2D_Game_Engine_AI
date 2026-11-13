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


def test_without_a_position_each_kind_gets_its_own_zone():
    objects = ask("4 casas, 6 árboles y 8 monedas")
    centres = {}
    for o in objects:
        centres.setdefault(o["kind"], []).append((o["x"], o["y"]))
    middle = {kind: (sum(x for x, _ in spots) / len(spots), sum(y for _, y in spots) / len(spots)) for kind, spots in centres.items()}
    # Three kinds, three different places, not one row in the middle.
    assert len({(round(x), round(y)) for x, y in middle.values()}) == 3
    assert len({o["y"] for o in objects}) > 1


def test_every_object_stays_inside_the_world():
    from app.world import SIZES, WORLD_HEIGHT, WORLD_WIDTH
    request = "10 casas, 10 árboles, 10 muros, 10 monedas, 10 cofres, 10 fantasmas, 10 tanques, 10 rocas, 10 torres, 10 cajas, 10 barriles, 10 arbustos, 10 vallas"
    for o in ask(request):
        w, h = SIZES[o["kind"]]
        assert w / 2 <= o["x"] <= WORLD_WIDTH - w / 2
        assert h / 2 <= o["y"] <= WORLD_HEIGHT - h / 2


def test_a_lake_or_a_road_is_a_patch_of_tiles():
    assert [o["kind"] for o in ask("un lago")].count("water") == 6
    assert [o["kind"] for o in ask("un camino")].count("path") == 6
    assert len(ask("una arena")) == 1  # only lakes, rivers, beaches and roads grow


def test_a_big_request_never_passes_the_agent_limit():
    assert len(ask("10 casas, 10 árboles, 10 muros, 10 monedas")) == 30

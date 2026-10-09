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

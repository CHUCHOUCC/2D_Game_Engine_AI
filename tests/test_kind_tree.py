from app.kind_tree import SCENERY_KINDS, build_kind_tree, category_of
from app.world import ALL_KINDS, ENEMY_KINDS, REWARD_KINDS


def test_every_kind_is_in_the_tree_exactly_once():
    tree = build_kind_tree()
    leaves = [leaf.value for category in tree.root.children for leaf in category.children]
    assert sorted(leaves) == sorted(ALL_KINDS)


def test_the_tree_has_three_levels():
    tree = build_kind_tree()
    assert tree.height() == 2 and tree.root.value == "world"


def test_categories_match_the_sets_of_the_world():
    tree = build_kind_tree()
    assert all(category_of(tree, kind) == "enemy" for kind in ENEMY_KINDS)
    assert all(category_of(tree, kind) == "reward" for kind in REWARD_KINDS)


def test_what_is_left_over_is_scenery():
    tree = build_kind_tree()
    assert {"wall", "house", "tree", "box"} <= SCENERY_KINDS
    assert category_of(tree, "wall") == "scenery" and category_of(tree, "coin") == "collectible"


def test_an_unknown_kind_has_no_category():
    assert category_of(build_kind_tree(), "dragon") is None


def test_preorder_lists_a_category_before_its_kinds():
    values = list(build_kind_tree().preorder())
    assert values.index("enemy") < values.index("bat") < values.index("reward")

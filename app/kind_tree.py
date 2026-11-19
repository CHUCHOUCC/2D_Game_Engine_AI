"""The kinds of the world as a tree: world -> category -> kind.

The flat sets of app/world.py say what is an enemy or a reward; this tree puts
every kind under its category, so the editor's library (and the AI's prompt) can
walk the whole catalogue in one traversal.
"""
from .structures import Tree
from .world import ALL_KINDS, CHARACTER_KINDS, ENEMY_KINDS, GROUND_KINDS, REWARD_KINDS, TERRAIN_KINDS

CATEGORIES = (
    ("player", frozenset({"player"})),
    ("character", CHARACTER_KINDS),
    ("enemy", ENEMY_KINDS),
    ("reward", REWARD_KINDS),
    ("ground", GROUND_KINDS),
    ("terrain", TERRAIN_KINDS),
    ("hazard", frozenset({"spike"})),
    ("collectible", frozenset({"coin"})),
)
_CLASSIFIED = frozenset().union(*(kinds for _, kinds in CATEGORIES))
SCENERY_KINDS = frozenset(kind for kind in ALL_KINDS if kind not in _CLASSIFIED)


def build_kind_tree() -> Tree:
    """Root 'world', one child per category, and the kinds of each category as its children."""
    tree = Tree("world")
    for name, kinds in CATEGORIES + (("scenery", SCENERY_KINDS),):
        category = tree.root.add_child(name)
        for kind in ALL_KINDS:  # ALL_KINDS fixes the order, so the tree is always the same
            if kind in kinds:
                category.add_child(kind)
    return tree


def category_of(tree: Tree, kind: str):
    """The category a kind belongs to, or None when the kind does not exist."""
    for category in tree.root.children:
        if category.children.find(lambda leaf: leaf.value == kind) is not None:
            return category.value
    return None

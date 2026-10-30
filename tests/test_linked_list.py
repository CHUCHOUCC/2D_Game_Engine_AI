from app.structures.linked_list import LinkedList


def build(*values):
    items = LinkedList()
    for value in values:
        items.add(value)
    return items


def test_elements_keep_the_order_they_were_added_in():
    assert list(build(1, 2, 3)) == [1, 2, 3]


def test_add_first_goes_before_everything():
    items = build(2, 3)
    items.add_first(1)
    assert list(items) == [1, 2, 3]


def test_add_first_on_an_empty_list_also_sets_the_tail():
    items = LinkedList()
    items.add_first("a")
    items.add("b")
    assert list(items) == ["a", "b"]


def test_find_returns_the_first_match_or_none():
    items = build(1, 2, 3, 4)
    assert items.find(lambda n: n % 2 == 0) == 2
    assert items.find(lambda n: n > 10) is None


def test_remove_the_head_the_middle_and_the_tail():
    items = build(1, 2, 3, 4)
    assert items.remove(lambda n: n == 1)
    assert items.remove(lambda n: n == 3)
    assert items.remove(lambda n: n == 4)
    assert list(items) == [2] and items.size() == 1


def test_the_tail_is_updated_when_the_last_node_is_removed():
    items = build(1, 2)
    items.remove(lambda n: n == 2)
    items.add(3)
    assert list(items) == [1, 3]


def test_removing_something_that_is_not_there_changes_nothing():
    items = build(1)
    assert not items.remove(lambda n: n == 9)
    assert len(items) == 1


def test_clear_empties_the_list():
    items = build(1, 2)
    items.clear()
    assert items.is_empty() and list(items) == []

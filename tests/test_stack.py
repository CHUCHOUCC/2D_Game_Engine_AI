import pytest

from app.structures.stack import EmptyStackError, Stack


def test_a_new_stack_is_empty():
    stack = Stack()
    assert stack.is_empty()
    assert stack.size() == 0


def test_the_last_element_in_is_the_first_out():
    stack = Stack()
    for value in (1, 2, 3):
        stack.push(value)
    assert [stack.pop(), stack.pop(), stack.pop()] == [3, 2, 1]


def test_peek_does_not_remove():
    stack = Stack()
    stack.push("a")
    assert stack.peek() == "a"
    assert stack.size() == 1


def test_popping_or_peeking_an_empty_stack_raises():
    stack = Stack()
    with pytest.raises(EmptyStackError):
        stack.pop()
    with pytest.raises(EmptyStackError):
        stack.peek()


def test_the_stack_can_be_reused_after_emptying_it():
    stack = Stack()
    stack.push(1)
    stack.pop()
    stack.push(2)
    assert stack.peek() == 2 and stack.size() == 1

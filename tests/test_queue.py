import pytest

from app.structures.queue import EmptyQueueError, Queue


def test_the_first_element_in_is_the_first_out():
    queue = Queue()
    for value in (1, 2, 3):
        queue.enqueue(value)
    assert [queue.dequeue(), queue.dequeue(), queue.dequeue()] == [1, 2, 3]


def test_front_and_rear_do_not_remove():
    queue = Queue()
    queue.enqueue("a")
    queue.enqueue("b")
    assert (queue.front(), queue.rear(), queue.size()) == ("a", "b", 2)


def test_emptying_the_queue_clears_the_rear_too():
    queue = Queue()
    queue.enqueue(1)
    queue.dequeue()
    assert queue.is_empty()
    with pytest.raises(EmptyQueueError):
        queue.rear()
    queue.enqueue(2)
    assert queue.front() == queue.rear() == 2


def test_an_empty_queue_raises():
    queue = Queue()
    for action in (queue.dequeue, queue.front, queue.rear):
        with pytest.raises(EmptyQueueError):
            action()

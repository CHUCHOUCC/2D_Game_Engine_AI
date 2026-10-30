from .node import Node


class EmptyQueueError(Exception):
    """Raised when reading or removing an element from an empty queue."""


class Queue:
    """FIFO queue built on linked nodes: the first element in is the first out.

    Keeps a reference to the front (where elements leave) and to the rear (where
    they arrive), so the chain is never walked.
    Invariant: _front and _rear are both None (empty) or both point into the same
    chain, and _rear.next is None.
    Costs: enqueue, dequeue, front, rear and is_empty are O(1).
    Empty-queue rule: dequeue(), front() and rear() raise EmptyQueueError.
    """

    def __init__(self):
        self._front = None
        self._rear = None
        self._size = 0

    def is_empty(self) -> bool:
        return self._front is None

    def size(self) -> int:
        return self._size

    def enqueue(self, data) -> None:
        new_node = Node(data)
        if self._rear is None:
            # Empty queue: the new node is both front and rear.
            self._front = new_node
        else:
            self._rear.next = new_node
        self._rear = new_node
        self._size += 1

    def dequeue(self):
        if self._front is None:
            raise EmptyQueueError("Cannot dequeue: the queue is empty")
        data = self._front.data
        self._front = self._front.next
        if self._front is None:
            # The last element left: the rear must be cleared as well.
            self._rear = None
        self._size -= 1
        return data

    def front(self):
        if self._front is None:
            raise EmptyQueueError("No front element: the queue is empty")
        return self._front.data

    def rear(self):
        if self._rear is None:
            raise EmptyQueueError("No rear element: the queue is empty")
        return self._rear.data

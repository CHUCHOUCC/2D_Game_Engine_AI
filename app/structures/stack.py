from .node import Node


class EmptyStackError(Exception):
    """Raised when reading or removing an element from an empty stack."""


class Stack:
    """LIFO stack built on linked nodes: the last element in is the first out.

    Invariant: _top is None if and only if _size is 0.
    Costs: push, pop, peek and is_empty are O(1); only the top node is touched.
    Empty-stack rule: pop() and peek() raise EmptyStackError.
    """

    def __init__(self):
        self._top = None
        self._size = 0

    def is_empty(self) -> bool:
        return self._top is None

    def size(self) -> int:
        return self._size

    def push(self, data) -> None:
        # The new node points to the previous top and becomes the new top.
        self._top = Node(data, self._top)
        self._size += 1

    def pop(self):
        if self._top is None:
            raise EmptyStackError("Cannot pop: the stack is empty")
        data = self._top.data
        self._top = self._top.next
        self._size -= 1
        return data

    def peek(self):
        if self._top is None:
            raise EmptyStackError("No top element: the stack is empty")
        return self._top.data

from __future__ import annotations
from typing import Optional


class EmptyElement:    

    def __init__(self):
        self._e = None

    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return -1

    @property
    def element(self) -> None:
        return self._e 

    def get_attrib(self, attribname:str, namespace:Optional[str]=None) -> None:
        return None

    def set_attrib(self, attribname:str, value:str, namespace:Optional[str]=None) -> None:
        pass

    @property
    def parent(self) -> EmptyElement:
        return EmptyElement()

    @property
    def parents(self) -> list:

        return []

    @property
    def root(self) -> None:
        return None

    @property
    def tag(self) -> None:
        return None

    @property
    def tail(self) -> str:
        return ''

    @tail.setter
    def tail(self, value:str):
        pass

    @property
    def text(self) -> str:
        return ''

    def __repr__(self):
        return f"<Element object empty>"

    def __add__(self, other):
        return other
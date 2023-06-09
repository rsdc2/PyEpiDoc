from __future__ import annotations
from collections import namedtuple
import abc
from typing import Sequence, TypeVar
_T = TypeVar('_T') 


class Showable:
    @abc.abstractmethod
    def __str__(self) -> str:
        ...


class ExtendableSeq(Sequence[_T]):
    @abc.abstractmethod
    def __add__(self, other) -> ExtendableSeq[_T]:
        ...

Tag = namedtuple('Tag', ['ns', 'name'])
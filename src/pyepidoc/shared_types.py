from __future__ import annotations

from collections import namedtuple
from enum import Enum
from typing import Sequence, TypeVar

import abc
import operator

_T = TypeVar('_T') 


class EnumerableEnum(Enum):

    @classmethod
    def values(cls) -> list:
        return [item.value for item in cls]
    
    @classmethod
    def value_set(cls) -> set:
        return set(cls.values())


class Showable:
    @abc.abstractmethod
    def __str__(self) -> str:
        ...


class ExtendableSeq(Sequence[_T]):
    @abc.abstractmethod
    def __add__(self, other) -> ExtendableSeq[_T]:
        ...

class SetRelation(Enum):
    @staticmethod
    def intersection(set1:set, set2:set) -> bool:
        return not set.isdisjoint(set1, set2)
        
    @staticmethod
    def propersubset(set1:set, set2:set | list) -> bool:
        return set.issubset(set1, set2) and set(set1) != set(set2)

    subset = set.issubset
    equal = set.__eq__
    disjoint = set.isdisjoint


class GtLtRelation(Enum):
    gt = operator.gt
    lt = operator.lt


Tag = namedtuple('Tag', ['ns', 'name'])
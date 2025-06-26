"""
Collection class for abbreviations grouping and containing
convenience methods for operating on abbreviations
"""

from __future__ import annotations

from typing import (
    Callable,
    SupportsIndex,
    overload,
    TypeVar
)
from functools import cached_property

from .edition_elements.expan import Expan
from pyepidoc.shared.iterables import top, contains, listfilter
from pyepidoc.epidoc.enums import AbbrType
from pyepidoc.shared.generic_collection import GenericCollection

T = TypeVar('T')

class Abbreviations(GenericCollection[Expan]):
    """
    Collection class for abbreviations grouping and containing
    convenience methods for operating on abbreviations
    """

    _values: list[Expan]

    def __init__(self, expans: list[Expan]):
        self._expans = expans

    def __getitem__(self, i: SupportsIndex) -> Expan:
        return self._expans[i]

    def __repr__(self) -> str:
        return f'Abbreviations({self._expans})'
    
    @cached_property
    def contractions(self) -> Abbreviations:
        """
        Return all the contractions
        """

        return Abbreviations([abbr for abbr in self._expans 
               if contains(abbr.abbr_types, AbbrType.contraction)])

    @cached_property
    def contractions_with_suspension(self) -> Abbreviations:
        """
        Return all the contractions with suspension
        """

        return Abbreviations([abbr for abbr in self._expans 
               if contains(
                   abbr.abbr_types, 
                   AbbrType.contraction_with_suspension)])

    @property
    def count(self) -> int:
        """
        Alias for length property
        """
        return self.length

    @property
    def length(self) -> int:
        """
        Return the number of items in the underlying
        list of <expan> elements
        """
        return len(self._expans)
    
    def map(self, func: Callable[[Expan], T]) -> GenericCollection[T]:
        """
        Map a function to the abbreviations
        """
        mapped = list(map(func, self._expans))
        return GenericCollection(mapped)
    
    @cached_property
    def multiplications(self) -> Abbreviations:
        """
        Return all the contractions with suspension
        """

        return Abbreviations([abbr for abbr in self._expans 
               if contains(abbr.abbr_types, AbbrType.multiplication)])

    @cached_property
    def suspensions(self) -> Abbreviations:
        """
        Return all the suspensions
        """

        return Abbreviations([abbr for abbr in self._expans 
               if contains(abbr.abbr_types, AbbrType.suspension)])
    
    
    def where(self, predicate: Callable[[Expan], bool]) -> Abbreviations:
        """
        Filter abbreviations according to a predicate
        """

        return Abbreviations(list(filter(predicate, self._expans)))
    
    def where_ancestor_is(self, localname: str) -> Abbreviations:
        """
        Filter for elements with a certain localname among ancestor elements
        e.g. 'name'
        """

        return Abbreviations(
            [expan for expan in self._expans
             if expan.has_ancestor_by_name(localname)]
        )
    
    def where_ancestor_is_not(self, localname: str) -> Abbreviations:
        """
        Filter for elements without a certain localname among ancestor elements
        e.g. 'name'
        """

        return Abbreviations(
            [expan for expan in self._expans
             if not expan.has_ancestor_by_name(localname)]
        )
"""
Collection class for abbreviations grouping and containing
convenience methods for operating on abbreviations
"""

from __future__ import annotations

from typing import (
    Callable,
    Generic,
    SupportsIndex,
    overload,
    TypeVar
)

from pyepidoc.shared.utils import top, contains, listfilter

T = TypeVar('T')
U = TypeVar('U')

class GenericCollection(Generic[T]):
    """
    Collection class for abbreviations grouping and containing
    convenience methods for operating on abbreviations
    """

    _values: list[T]

    def __init__(self, values: list[T]):
        self._values = values

    def __getitem__(self, i: SupportsIndex) -> T:
        return self._values[i]
    
    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        return f'GenericCollection({self._values})'
    
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
        list of <T> elements
        """
        return len(self._values)
    
    def map(self, func: Callable[[T], U]) -> GenericCollection[U]:
        """
        Map a function to the abbreviations
        """
        return GenericCollection(list(map(func, self._values)))
    
    def unique(self) -> GenericCollection[T]:
        """
        Return the unique elements in the collection
        """

        return GenericCollection(list(set(self._values)))

    def where(self, predicate: Callable[[T], bool]) -> GenericCollection[T]:
        """
        Filter abbreviations according to a predicate
        """

        return GenericCollection(list(filter(predicate, self._values)))
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
    TypeVar,
    Hashable
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
    
    def foreach(self, action: Callable[[T], None]) -> None:
        """
        Call an action on each element
        """

        for item in self._values:
            action(item)
    
    def frequencies(self) -> GenericCollection[tuple[T, int]]:
        """
        Return a dictionary with the frequencies of each item
        """

        d = {k: self._values.count(k) 
                for k in self.unique()._values}

        l = ([(value, frequency) for value, frequency in d.items()])
        sorted_l = sorted(l, key=lambda item: item[1], reverse=True)
        return GenericCollection(sorted_l)

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
    
    def sort(self, key=lambda x: x, reverse: bool=False) -> GenericCollection[T]:
        """
        Sort the values according to a key function
        """
        sorted_values = sorted(self._values, key=key, reverse=reverse)
        return GenericCollection(sorted_values)

    def to_list(self) -> list[T]:
        """
        Return the underlying _values `list` object
        """
        return self._values

    def top(self, n: int) -> GenericCollection[T]:
        """
        Take the top `n` items
        """
        if self.count > n:
            return GenericCollection(self._values[0:n])
        
        return GenericCollection(self._values)
    
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
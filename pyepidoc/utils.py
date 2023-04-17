from __future__ import annotations

"""
This file provides generic utility functions especially for handling
lists and strings.
"""

from typing import (
    TypeVar, 
    Optional, 
    Union, 
    Callable, 
    Sequence,
    Iterable
)

from functools import reduce

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


def is_xd(xd_list: list) -> bool:
    return any([type(item) is list for item in xd_list])


def flatlist(xd_list:list) -> list:

    def reduce_list(acc:list, l:list): 
        return acc + l

    if is_xd(xd_list):
        l:list = reduce(reduce_list, xd_list, [])
        return flatlist(l)

    return xd_list


def listfilter(func, iterable:Iterable[T]) -> list[T]:
    return list(filter(func, iterable))


def top(l:Sequence[T], length:Optional[int]=10) -> Sequence[T]:
    if length is None:
        return l

    if len(l) >= 0:
        return l[0:length]

    return l


def update(set1:set, set2:set):
    set1.update(set2)
    return set1


def remove_none(l:list[Optional[T]]) -> list[T]:
    return [item for item in l if item is not None]


def maxone(
    lst:list[T], 
    defaultval: Optional[T]=None, 
    throw_if_more_than_one:bool=True,
    idx:int=0
) -> Optional[T]:

    """
    Returns a maximum of one item from a |list|.
    If more than one items are present, returns the item 
    at index 0, if cls is None; 
    otherwise calls callback with lst[idx] as the argument. 
    If no items are present, returns the defaultval: 
    if defaultval is a class, an instance of the class is returned.
    """

    if len(lst) == 0:
        return defaultval

    if len(lst) > 1:
        if throw_if_more_than_one:
            raise ValueError(f'More than one {type(lst[idx])} present.')

        return lst[idx]

    # Only one item in list
    return lst[0]

def head(
    lst:list[T],
    defaultval:Optional[T]=None,
    throw_if_more_than_one:bool=False
):
    return maxone(lst, defaultval, throw_if_more_than_one, 0)

def last(
    lst:list[T],
    defaultval:Optional[T]=None,
    throw_if_more_than_one:bool=False
):
    return maxone(lst, defaultval, throw_if_more_than_one, len(lst) - 1)


def maxoneT(
    lst:list[T], 
    defaultval: T, 
    # callback:Optional[Callable[[T], V]]=None, 
    throw_if_more_than_one:bool=True,
    idx:int=0
) -> T:

    """
    Returns a maximum of one item from a |list|.
    If more than one items are present, returns the item 
    at index idx. 
    If no items are present, returns the defaultval.
    """

    if len(lst) == 0:
        return defaultval

    if len(lst) > 1:
        if throw_if_more_than_one:
            raise ValueError(f'More than one {type(lst[idx])} present.')

        return lst[idx]

    # Only one item in list
    return lst[0]


def default_str(str_or_none:Optional[str]):
    if str_or_none is None:
        return ''
    if type(str_or_none) is str:
        return str_or_none
    
    raise TypeError('str_or_none must be str or None.')



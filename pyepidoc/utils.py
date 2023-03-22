from typing import TypeVar, Optional, Union
from itertools import chain

T = TypeVar('T')


def is_xd(xd_list: list) -> bool:
    return any([type(item) is list for item in xd_list])


def flatlist(xd_list: list) -> list:

    if is_xd(xd_list):
        return flatlist(list(chain(*xd_list)))

    return xd_list
    

def head(l:list[T], length:Optional[int]=10) -> list[T]:
    if length is None:
        return l

    if len(l) >= 0:
        return l[0:length]

    return l

def update(set1:set, set2:set):
    set1.update(set2)
    return set1


def maxone(
    lst:list[T], 
    defaultval:Optional[Union[type, T]]=None, 
    cls:Optional[type]=None, 
    suppress_more_than_one_error:bool=False,
    idx:int=0
):

    if len(lst) == 0:
        if type(defaultval) == type:
            return defaultval()
        return defaultval

    if len(lst) == 1:
        return cls(lst[idx]) if cls else lst[idx]

    if len(lst) > 1:
        if not suppress_more_than_one_error:
            raise ValueError(f'More than one {type(lst[idx])} present.')

        return cls(lst[idx]) if cls else lst[idx]

    raise ValueError('Unexpected lst value.')


def default_str(str_or_none:Optional[str]):
    if str_or_none is None:
        return ''
    if type(str_or_none) is str:
        return str_or_none
    
    raise TypeError('str_or_none must be str or None.')



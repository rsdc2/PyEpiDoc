from __future__ import annotations
from typing import Optional
from lxml.etree import _Element, _ElementUnicodeResult
from pyepidoc.xml.utils import local_name


def cls_from_elem(
            elem: _Element | _ElementUnicodeResult,
            classes: dict[str, type]
        ) -> Optional[str]:

    """
    Returns an object according 
    to the tag of param:elem
    """

    if type(elem) is _ElementUnicodeResult:
        return str(elem)
    
    if type(elem) is _Element:
        elem_cls = classes.get(local_name(elem), None)

    else:
        raise TypeError(f'Element is of type {type(elem)}: '
                        f'should be either _Element '
                         'or _ElementUnicodeResult')

    if elem_cls is None:
        return None

    return elem_cls(elem)

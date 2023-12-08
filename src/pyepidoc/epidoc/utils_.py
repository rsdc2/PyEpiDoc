from __future__ import annotations
from typing import Optional
from lxml.etree import _Element, _ElementUnicodeResult

from .elem_types import element_classes
from pyepidoc.xml.utils import local_name


def cls_from_elem(
            elem: _Element | _ElementUnicodeResult
        ) -> Optional[str]:

    """
    Returns an object according 
    to the tag of param:elem
    """

    if type(elem) is _ElementUnicodeResult:
        return str(elem)
    
    if type(elem) is _Element:
        elem_cls = element_classes.get(local_name(elem), None)

    else:
        raise TypeError(f'Element is of type {type(elem)}: '
                        f'should be either BaseElement, _Element '
                         'or _ElementUnicodeResult')

    if elem_cls is None:
        return None

    return elem_cls(elem.e)

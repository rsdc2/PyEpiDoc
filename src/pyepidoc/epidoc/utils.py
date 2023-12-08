from __future__ import annotations

from lxml.etree import _Element, _ElementUnicodeResult
from pyepidoc.xml.utils import local_name


def leiden_str(elem: _Element, classes: dict[str, type]) -> str:
    """
    Returns a Leiden-formatted string representation
    of the children of param:elem
    """

    return str(cls_from_elem(elem, classes))


def children_elems_leiden_str(
        elem: _Element, 
        classes: dict[str, type]) -> str:

    objs = [cls_from_elem(elem, classes) 
                 for elem in elem.getchildren()
                 if local_name(elem) in classes.keys()]
    # breakpoint()
    return ''.join([str(obj) for obj in objs])


def get_text(elem: _Element | _ElementUnicodeResult) -> str:
    if type(elem) is _ElementUnicodeResult:
        return str(elem)
    
    return ''.join(map(str, elem.xpath('.//text()')))


def children_nodes_leiden_str(
        elem: _Element, 
        classes: dict[str, type]) -> str:

    objs = [classes.get(local_name(elem), get_text)(elem)
                 for elem in elem.xpath('child::node()')]
    # breakpoint()
    return ''.join([str(obj) for obj in objs])


def cls_from_elem(
            elem: _Element | _ElementUnicodeResult,
            classes: dict[str, type]
        ) -> str | None:

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

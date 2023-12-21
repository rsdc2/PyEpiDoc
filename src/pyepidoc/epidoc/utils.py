from __future__ import annotations

from typing import Literal
import re

from lxml.etree import _Element, _ElementUnicodeResult
from lxml import etree
from pyepidoc.xml.utils import local_name
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.epidoc.epidoc_types import OrigTextType, RegTextType
from pyepidoc.constants import TEINS


def epidoc_elem_to_str(xml: str, epidoc_elem_type: type[BaseElement]):
    """
    Returns the string representation of the element specified in 
    "epidoc_elem_type"
    """
    elem = etree.fromstring(xml, None)
    epidoc_elem = epidoc_elem_type(elem)
    return str(epidoc_elem)


def leiden_str(elem: _Element, classes: dict[str, type]) -> str:
    """
    Returns a Leiden-formatted string representation
    of the children of param:elem
    """

    return str(callable_from_localname(elem, classes))


def descendant_text(elem: _Element | _ElementUnicodeResult) -> str:
    """
    Returns descendant text
    """

    if type(elem) is _ElementUnicodeResult:
        s = str(elem)
    else: 
        s = ''.join(map(str, elem.xpath('.//text()'))) 

    return re.sub(r'[\n\t]|\s+', '', s)


def leiden_str_from_children(
        parent: _Element,
        classes: dict[str, type],
        child_type: Literal['element', 'node']) -> str:

    """
    Return a Leiden string from a parent element.

    param:child_type sets whether or not the children are elements or
    nodes (where nodes include text content)
    """
    
    non_ancestors = RegTextType.values()
    child_str = 'child::node()' if child_type == 'node' else 'child::*'
    ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                for ancestor in non_ancestors])
    
    xpath_str = f'{child_str}[{ancestors_str}]'

    children: list[_Element | _ElementUnicodeResult] = \
        [child for child in parent.xpath(xpath_str, namespaces={'ns': TEINS})]
    objs = [classes.get(local_name(child), descendant_text)(child) for child in children]
    return ''.join([str(obj) for obj in objs])


def callable_from_localname(
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

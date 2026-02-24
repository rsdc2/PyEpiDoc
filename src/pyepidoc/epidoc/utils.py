from __future__ import annotations

from typing import Literal, cast
import re

from lxml.etree import _Element, _ElementUnicodeResult
from pyepidoc.xml.utils import localname
from pyepidoc.xml.xml_element import XmlElement, XmlText
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.shared.enums import (
    NonNormalized, 
    RegTextType, 
    AtomicTokenType
)
from pyepidoc.shared.constants import TEINS
from pyepidoc.epidoc.tokenizable_element import TokenizableElement


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
        elem_cls = classes.get(localname(elem), None)

    else:
        raise TypeError(f'Element is of type {type(elem)}: '
                        f'should be either _Element '
                         'or _ElementUnicodeResult')

    if elem_cls is None:
        return None

    return elem_cls(elem)


def descendant_atomic_tokens(elem: TokenizableElement) -> list[TokenizableElement]:
    desc_tokens = map(TokenizableElement, elem.get_desc(AtomicTokenType.values()))

    return [token for token 
        in desc_tokens
        if set([ancestor.localname 
                for ancestor in token._e.ancestors_excl_self])
                    .isdisjoint(AtomicTokenType.value_set()) 
    ]


def epidoc_elem_to_str(xml: str, epidoc_elem_type: type[XmlElement]):
    """
    Returns the string representation of the element specified in 
    "epidoc_elem_type"
    """
    elem = XmlElement.from_str(xml)
    epidoc_elem = epidoc_elem_type(elem)
    return str(epidoc_elem)


def get_leiden_str(obj: TeiElement | XmlText | str) -> str:
    if isinstance(obj, XmlText):
        return obj.text
    
    if isinstance(obj, str):
        return obj
    
    if obj._e.localname in RegTextType.values():
        return ''
    
    if hasattr(obj, 'leiden_form'):
        leiden_str = obj.leiden_form
    else:
        raise AttributeError(f'No leiden_form attribute on {type(obj)}')

    if obj._e.localname in AtomicTokenType.values():
        ancestor_local_names = [ancestor.localname for ancestor in obj._e.ancestors_excl_self]
        if set(ancestor_local_names).intersection(AtomicTokenType.values()) == set():
            leiden_str = leiden_str.strip() + ' '

    return leiden_str


def leiden_form_from_children(parent: XmlElement, classes: dict[str, type]) -> str:
    """
    Return a Leiden string from a parent element.
    """

    assert isinstance(parent, XmlElement)
    if parent.has_ancestors_by_names(RegTextType.values()):
        return ''
    
    children = parent.child_nodes
    if len(children) == 0:
        return parent.text or ''
    
    ctors = [classes.get(child.localname, lambda x: x.descendant_text) for child in children]
    objs = [ctor(child) for (ctor, child) in zip(ctors, children)]

    # for obj in objs:
    #     if not isinstance(obj, (TeiElement, XmlText)):
    #         if isinstance(obj, XmlElement):
    #             raise TypeError(f'obj is an <{obj.localname}/>, parent is <{parent.localname}/> element.')
    #         raise TypeError(f'obj is {type(obj)}. Expected: TeiElement or XmlText')

    nodes: list[TeiElement | XmlText | str] = objs
    strings = [get_leiden_str(node) for node in nodes]

    leiden_str = ''.join(strings)
    return leiden_str


def normalized_form_from_children(
        parent: XmlElement,
        classes: dict[str, type],
        child_type: Literal['element', 'node']) -> str:

    """
    Return a normalized string from a parent element.

    param:child_type sets whether or not the children are elements or
    nodes (where nodes include text content)
    """
    assert isinstance(parent, XmlElement)
    
    non_ancestors = NonNormalized.values()
    child_str = 'child::node()' if child_type == 'node' else 'child::*'
    ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                for ancestor in non_ancestors])
    
    xpath_str = f'{child_str}[{ancestors_str}]'
    
    children = [child for child in parent.xpath(xpath_str, namespaces={'ns': TEINS})]
    objs = cast(list[TokenizableElement], [classes.get(child.localname, lambda c: c.descendant_text)(child) 
            for child in children])
    
    s = ''.join([obj.normalized_form 
                 if hasattr(obj, 'normalized_form') 
                 else str(obj) for obj in objs])
    return re.sub(r'[·\,\.\;\:]|\s+', '', s)

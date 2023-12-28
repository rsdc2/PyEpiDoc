from __future__ import annotations
from typing import Iterable
from lxml.etree import _Element, _ElementUnicodeResult
from lxml import etree
from copy import deepcopy


def localname(node: _Element | _ElementUnicodeResult) -> str:
    """
    Return the local name of a node.
    Returns '#text' if node is |_ElementUnicodeResult|
    """
    if type(node) is _ElementUnicodeResult:
        return '#text'
    
    return str(node.xpath('local-name(.)'))


def remove_children(elem: _Element) -> _Element:
    elem_ = deepcopy(elem)
    for child in elem_.getchildren():
        elem_.remove(child)

    return elem_


def elem_from_str(xml: str) -> _Element:
    """
    Return an lxml _Element from a string
    """
    return etree.fromstring(xml, None)



# def 


# def filter_by_non_ancestors(
#         node: _Element | _ElementUnicodeResult,
#         non_ancestors: Iterable[str]):

#     if type(node) is _Element:

#         ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
#                                     for ancestor in non_ancestors])

#         normalized_text = node.xpath(f'descendant::text()[{ancestors_str}]')
#         return self._clean_text(''.join([str(t) for t in normalized_text]))    
    

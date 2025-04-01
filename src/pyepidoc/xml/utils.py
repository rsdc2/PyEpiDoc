from __future__ import annotations

from lxml.etree import _Element, _ElementUnicodeResult
from lxml import etree
from copy import deepcopy

from pyepidoc.shared.constants import TEINS


def abify(xml_str: str): 
    """
    Enclose a string in <ab> tags

    :param xml_str: XML content 
    """
    return f'<ab xmlns="{TEINS}">{xml_str}</ab>'


def editionify(xml_str: str, wrap_in_ab: bool) -> str: 
    """
    Enclose a string in <ab> tags 

    :param xml_str: XML content 
    :param wrap_in_ab: If True, wraps the content in an `<ab>` 
    element inside the `<div type="edition>` element
    """
    if wrap_in_ab:
        return f'<div type="edition" xmlns="{TEINS}">{abify(xml_str)}</div>'

    return f'<div type="edition" xmlns="{TEINS}">{xml_str}</div>'


def elem_from_str(xml: str) -> _Element:
    """
    Return an lxml _Element from a string
    """
    return etree.fromstring(xml, None)


def localname(node: _Element | _ElementUnicodeResult) -> str:
    """
    Return the local name of a node.
    Returns '#text' if node is |_ElementUnicodeResult|
    """
    node_ = node

    if isinstance(node_, _ElementUnicodeResult):
        return '#text'
    
    return str(node_.xpath('local-name(.)'))


def remove_children(elem: _Element) -> _Element:
    elem_ = deepcopy(elem)
    for child in elem_.getchildren():
        elem_.remove(child)

    return elem_
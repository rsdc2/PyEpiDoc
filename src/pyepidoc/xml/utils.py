from __future__ import annotations
from pyepidoc.xml.xml_node_types import XmlNode, XmlElement
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


def localname(node: XmlNode) -> str:
    """
    Return the local name of a node.
    Returns '#text' if node is XmlText
    """
    return node.localname


def remove_children(elem: XmlElement) -> XmlElement:
    """
    Removes children and returns a copy of the element without children
    """
    elem_ = elem.deepcopy()
    elem_.remove_children()
    return elem_


def descendant_text(node: XmlNode) -> str:
    """
    Returns descendant text
    """
    return node.descendant_text
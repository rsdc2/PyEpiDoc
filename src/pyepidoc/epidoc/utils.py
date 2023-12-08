from __future__ import annotations

from lxml.etree import _Element
from pyepidoc.xml.utils import local_name
from .utils_ import cls_from_elem


def leiden_str(elem: _Element, classes: dict[str, type]) -> str:
    """
    Returns a Leiden-formatted string representation
    of the children of param:elem
    """

    return str(cls_from_elem(elem, classes))


def children_elems_leiden_str(elem: _Element, classes: dict[str, type]) -> str:

    objs = [cls_from_elem(elem, classes) 
                 for elem in elem.getchildren()
                 if local_name(elem) in classes.keys()]

    return ''.join([str(obj) for obj in objs])


def children_nodes_leiden_str(elem: _Element, classes: dict[str, type]) -> str:

    objs = [cls_from_elem(elem, classes) 
                 for elem in elem.xpath('child::node()')
                 if local_name(elem) in classes.keys()]

    return ''.join([str(obj) for obj in objs])
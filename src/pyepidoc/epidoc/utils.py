from __future__ import annotations

from lxml.etree import _Element
from pyepidoc.xml.utils import local_name
from .utils_ import cls_from_elem

from .elem_types import element_classes


def leiden_str(elem: _Element) -> str:
    """
    Returns a Leiden-formatted string representation
    of the children of param:elem
    """

    return str(cls_from_elem(elem))


def children_elems_leiden_str(elem: _Element) -> str:

    objs = [cls_from_elem(elem) 
                 for elem in elem.getchildren()
                 if local_name(elem) in element_classes.keys()]

    return ''.join([str(obj) for obj in objs])


def children_nodes_leiden_str(elem: _Element) -> str:

    objs = [cls_from_elem(elem) 
                 for elem in elem.xpath('child::node()')
                 if local_name(elem) in element_classes.keys()]

    return ''.join([str(obj) for obj in objs])
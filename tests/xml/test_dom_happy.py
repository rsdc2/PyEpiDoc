from pyepidoc.xml.utils import elem_from_str, abify
from pyepidoc.epidoc.elements.ab import Ab
from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.shared.constants import XMLNS
from pyepidoc.xml.namespace import Namespace as ns
import pytest


tests = [
    ('<expan><abbr>abbr</abbr><ex>eviation</ex></expan> hello', 
     ['expan', '#text']), 
]


@pytest.mark.parametrize(['xml', 'child_node_names'], tests)
def test_child_node_names(
    xml: str, 
    child_node_names: list[str]):
    """
    Tests names of child nodes, esp. of text nodes
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert ab.child_node_names == child_node_names


def test_remove_attr():

    """
    Test that can remove atribute
    """

    elem = BaseElement(elem_from_str('<w n="2">hello</w>'))
    elem.remove_attr('n', None)
    assert elem.xml_str == '<w>hello</w>'


def test_remove_attr_with_xml_ns():

    """
    Test that can remove attribute with xml namespace
    """
    string = f'<w>hello</w>'
    lxml_elem = elem_from_str(string)
    elem = BaseElement(lxml_elem)
    elem.set_attrib('id', '2', XMLNS)
    assert elem.xml_str == '<w xml:id="2">hello</w>'
    elem.remove_attr('id', XMLNS)
    assert elem.xml_str == '<w>hello</w>'
from pyepidoc.xml.utils import abify
from pyepidoc.epidoc.edition_elements.ab import Ab
from pyepidoc.xml.lxml_node_types import XmlElement
from pyepidoc.shared.namespaces import XMLNS
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
    element = XmlElement.from_str(abify(xml))
    ab = Ab(element)
    assert ab._e.child_node_names == child_node_names


def test_remove_attr():

    """
    Test that can remove atribute
    """

    elem = XmlElement.from_str('<w n="2">hello</w>')
    elem.remove_attr('n', None)
    assert elem.xml_str == '<w>hello</w>'


def test_remove_attr_with_xml_ns():

    """
    Test that can remove attribute with xml namespace
    """
    string = f'<w>hello</w>'
    elem = XmlElement.from_str(string)
    elem.set_attr('id', '2', XMLNS)
    assert elem.xml_str == '<w xml:id="2">hello</w>'
    elem.remove_attr('id', XMLNS)
    assert elem.xml_str == '<w>hello</w>'
from pyepidoc.xml.utils import elem_from_str, abify
from pyepidoc.epidoc.elements.ab import Ab
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

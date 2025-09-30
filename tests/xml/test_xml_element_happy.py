import pytest
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.xml.utils import abify    

previous_sibling_cases = [
    ('<w n="5">hello</w> <persName n="10"><w n="15">goodbye</w></persName>',
     "15",
     None),
    ('<w n="5">hello</w> <persName n="10"><w n="15">goodbye</w></persName>',
     "10",
     "5"),
]
@pytest.mark.parametrize(('xml_str', 'next_id', 'expected_previous_id'), previous_sibling_cases)
def test_previous_sibling(xml_str: str, next_id: str, expected_previous_id: str | None):
    # Arrange
    ab = XmlElement.from_xml_str(abify(xml_str))
    next_elem = list(filter(lambda e: e.get_attrib('n') == next_id, ab.descendant_elements))[0]

    # Act
    previous_elem = next_elem.previous_sibling

    # Assert
    if previous_elem is None:
        assert expected_previous_id is None
    else:
        assert previous_elem.get_attrib('n') == expected_previous_id
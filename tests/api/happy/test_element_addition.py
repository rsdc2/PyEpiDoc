from pyepidoc.shared.constants import TEINS
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.xml.xml_element import XmlElement
import pytest

xmls =[
    (f'<w xmlns="{TEINS}">domin</w>',
     f'<hi xmlns="{TEINS}">us</hi>', 
     f'<w xmlns="{TEINS}">domin<hi>us</hi></w>'),

    (f'<w xmlns="{TEINS}">d</w>',
     f'<hi xmlns="{TEINS}" rend="apex">u</hi>',
     f'<w xmlns="{TEINS}">d<hi rend="apex">u</hi></w>')
]

@pytest.mark.parametrize("xml_pair", xmls)
def test_w_hi(xml_pair: tuple[str, str, str]):

    # Arrange
    xml1, xml2, result = xml_pair
    bytes_result = result.encode()

    e1 = XmlElement.from_str(xml1)
    e2 = XmlElement.from_str(xml2)

    elem1 = EditionElement(e1)
    elem2 = EditionElement(e2)

    # Act
    elem = elem1 + elem2

    # Assert
    assert elem[0]._e.to_bytes() == bytes_result


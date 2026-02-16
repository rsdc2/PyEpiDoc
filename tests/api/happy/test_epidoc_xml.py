from pyepidoc.xml.utils import descendant_text
from pyepidoc.xml import XmlElement


def test_get_descendant_text():
    # from ISic000481
    # Arrange
    xmlstr = '<expan><abbr>A<am>A</am>u</abbr></expan>'
    elem = XmlElement.from_str(xmlstr)

    # Act
    desc_text = descendant_text(elem)

    # Assert
    assert desc_text == 'AAu'

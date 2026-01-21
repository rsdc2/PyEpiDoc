from pyepidoc.epidoc.utils import descendant_text
from pyepidoc.xml import XmlElement
from lxml import etree


def test_get_descendant_text():
    # from ISic000481
    xmlstr = "<expan><abbr>A<am>A</am>u</abbr></expan>"

    elem = XmlElement.from_str(xmlstr)

    assert descendant_text(elem) == "AAu"



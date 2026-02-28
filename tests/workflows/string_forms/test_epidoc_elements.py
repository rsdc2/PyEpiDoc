from pyepidoc.epidoc.utils import epidoc_elem_to_str
from pyepidoc.epidoc.epidoc import Expan
from pyepidoc.epidoc.edition_elements.edition import Edition
from pyepidoc.epidoc.edition_elements.abbr import Abbr
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.xml.xml_element import XmlElement


def test_abbr():
    """
    Tests that <abbr> within <expan> is represented correctly
    as a string
    """
    # Arrange
    xmlstr = "<expan><abbr>F</abbr><ex>ilius</ex></expan>"
    assert epidoc_elem_to_str(xmlstr, Expan) == r"F(ilius)"
    

def test_abbr_normalized_form():
    # Arrange
    xml_str = '<lb n="3"/><w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>'
    edition = Edition.from_xml_str(xml_str)
    assert edition != None
    token = edition.tokens_no_nested[0]

    # Act / Assert
    assert token.normalized_form == 'duoviro'


def test_abbr_leiden_form():
    # Arrange
    xml_str = '<lb n="3"/><w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>'
    edition = Edition.from_xml_str(xml_str)
    assert edition != None
    token = edition.tokens_no_nested[0]

    # Act / Assert
    assert token.leiden_form == 'IIvir(o)'
    

def test_abbr_leiden_plus_form():
    # Arrange
    xml_str = '<lb n="3"/><w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>'
    edition = Edition.from_xml_str(xml_str)
    assert edition != None
    token = edition.tokens_no_nested[0]

    # Act / Assert
    assert token.leiden_plus_form == ' | IIvir(o)'


def test_am():
    """
    Tests that <am> within <expan> is represented correctly
    as a string
    """
    # from ISic000481
    xmlstr = "<expan><abbr>A<am>A</am>u<am>u</am>g<am>g</am></abbr><ex>ustorum</ex></expan>"
    assert epidoc_elem_to_str(xmlstr, Expan) == r"A{A}u{u}g{g}(ustorum)"


def test_am_2():
    """
    Tests that <am> within <expan> is represented correctly
    as a string
    """
    # from ISic000481
    xmlstr = "<expan><abbr>A<am>A</am>u</abbr></expan>"
    assert epidoc_elem_to_str(xmlstr, Expan) == r"A{A}u"


def test_am_3():
    # from ISic000481
    xmlstr = "<expan><abbr>Au</abbr></expan>"
    assert epidoc_elem_to_str(xmlstr, Expan) == r"Au"


def test_am_4():
    # from ISic000481
    xmlstr = "<expan><abbr>A<am>A</am>u</abbr></expan>"

    elem = XmlElement.from_str(xmlstr)

    epidoc_elem = XmlElement(elem)
    text_nodes = epidoc_elem.xpath("descendant::text()")
    text_node_strs = list(map(str, text_nodes))
    assert text_node_strs == ['A', 'A', 'u']


def test_am_5():
    # from ISic000481
    xmlstr = "<abbr><am>A</am>u</abbr>"
    assert epidoc_elem_to_str(xmlstr, Abbr) == r"{A}u"


def test_am_6():
    # from ISic000501
    xmlstr = '<expan><hi rend="supraline"><abbr>d<am>d</am></abbr></hi><ex cert="low">ominis</ex></expan>'
    assert epidoc_elem_to_str(xmlstr, Expan) == r"d{d}(ominis)"

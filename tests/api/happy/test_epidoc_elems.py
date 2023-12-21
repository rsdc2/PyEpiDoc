from lxml import etree

from pyepidoc.epidoc.utils import epidoc_elem_to_str
from pyepidoc.epidoc.epidoc import EpiDoc, Expan
from pyepidoc.epidoc.abbr import Abbr
from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.utils import head
from pyepidoc.constants import TEINS


relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'api/files/single_files_tokenized/ISic000552.xml',
    'persName_nested': 'api/files/persName_nested.xml',
    'langs_1': 'api/files/langs_1.xml',
    'langs_2': 'api/files/langs_2.xml',
    'langs_3': 'api/files/langs_3.xml',
    'line_1': 'api/files/line_1.xml',
    'line_2': 'api/files/line_2.xml',
    'gap': 'api/files/gap.xml',
    'comma': 'api/files/comma.xml',
    'leiden': 'api/files/leiden.xml',
    'abbr': 'api/files/abbr.xml'
}

line_2_output = 'api/files/line_2_output.xml'


def test_abbr():
    """
    Tests that <abbr> within <expan> is represented correctly
    as a string
    """
    # made up example
    xmlstr = "<expan><abbr>F</abbr><ex>ilius</ex></expan>"
    assert epidoc_elem_to_str(xmlstr, Expan) == r"F(ilius)"
    

def test_abbr_forms():
    fp = relative_filepaths['abbr']

    doc = EpiDoc(fp)
    edition = head(doc.editions())

    assert edition != None

    token = edition.tokens[0]

    assert token.normalized_form == 'IIviro'
    assert token.leiden_form == 'IIvir(o)'
    assert token.leiden_plus_form == '|IIvir(o)'


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

    elem = etree.fromstring(xmlstr, None)

    epidoc_elem = BaseElement(elem)
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


def test_expans_1():
    filepath = relative_filepaths['ISic000001']
    
    doc = EpiDoc(filepath)
    edition = head(doc.editions())

    assert edition != None
    assert len(edition.expan_elems) == 3


def test_expans_2():
    xml = f'<expan xmlns="{TEINS}">Kal<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = etree.fromstring(xml, None)
    expan = Expan(elem)
    # breakpoint()
    assert expan._desc_textnode_is_desc_of('1', 'expan')


def test_expans_3():
    xml = f'<expan xmlns="{TEINS}">Kal<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = etree.fromstring(xml, None)
    expan = Expan(elem)
    assert not expan._desc_textnode_is_desc_of('1', 'abbr')


def test_expans_4():
    xml = f'<expan xmlns="{TEINS}"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = etree.fromstring(xml, None)
    expan = Expan(elem)
    assert expan._desc_textnode_is_desc_of('last()', 'abbr')    


def test_expans_5():
    xml = f'<expan xmlns="{TEINS}"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr>s</expan>'
    elem = etree.fromstring(xml, None)
    expan = Expan(elem)
    assert not expan._desc_textnode_is_desc_of('last()', 'abbr')    


def test_gaps():
    doc = EpiDoc(relative_filepaths['gap'])
    has_gaps = doc.has_gap(reasons=['lost'])
    assert has_gaps == True


def test_nested():
    doc = EpiDoc(relative_filepaths['persName_nested'])
    assert doc.tokens_list_str == ['Maximus', 'Decimus', 'meridius']
    assert [str(token) for token in doc.w_tokens] == ['meridius']
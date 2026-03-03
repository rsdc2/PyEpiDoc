from pyepidoc.epidoc.epidoc import EpiDoc, Expan
from pyepidoc.xml.xml_node_types import XmlElement
from pyepidoc.xml.xml_node_types import XmlElement
from pyepidoc.shared import head
from pyepidoc.shared.constants import TEINS


relative_filepaths = {
    'ISic000001': 'tests/api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'tests/api/files/single_files_tokenized/ISic000552.xml',
    'persName_nested': 'tests/api/files/persName_nested.xml',
    'langs_1': 'tests/api/files/langs_1.xml',
    'langs_2': 'tests/api/files/langs_2.xml',
    'langs_3': 'tests/api/files/langs_3.xml',
    'line_1': 'tests/api/files/line_1.xml',
    'line_2': 'tests/api/files/line_2.xml',
    'gap': 'tests/api/files/gap.xml',
    'comma': 'tests/api/files/comma.xml',
    'leiden': 'tests/api/files/leiden.xml',
    'abbr': 'tests/api/files/abbr.xml'
}

line_2_output = 'api/files/line_2_output.xml'


def test_expans_1():
    filepath = relative_filepaths['ISic000001']
    
    doc = EpiDoc(filepath)
    edition = head(doc.editions())

    assert edition != None
    assert len(edition.expan_elems) == 3


def test_expans_2():
    # Arrange
    xml = f'<expan xmlns="{TEINS}">Kal<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = XmlElement.from_str(xml)
    expan = Expan(elem)
    
    # Assert
    assert expan._desc_textnode_is_desc_of('1', 'expan')


def test_expans_3():
    xml = f'<expan xmlns="{TEINS}">Kal<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = XmlElement.from_str(xml)
    expan = Expan(elem)
    assert not expan._desc_textnode_is_desc_of('1', 'abbr')


def test_expans_4():
    xml = f'<expan xmlns="{TEINS}"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = XmlElement.from_str(xml)
    expan = Expan(elem)
    assert expan._desc_textnode_is_desc_of('last()', 'abbr')    


def test_expans_5():
    xml = f'<expan xmlns="{TEINS}"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr>s</expan>'
    elem = XmlElement.from_str(xml)
    expan = Expan(elem)
    assert not expan._desc_textnode_is_desc_of('last()', 'abbr')    


def test_gaps():
    doc = EpiDoc(relative_filepaths['gap'])
    has_gaps = doc.has_gap(reasons=['lost'])
    assert has_gaps == True


def test_nested():
    doc = EpiDoc(relative_filepaths['persName_nested'])
    assert [token.normalized_form 
            for token in doc.tokens_normalized_no_nested] == ['Maximus', 'Decimus', 'Meridius']
    assert [str(token) for token in doc.w_tokens] == ['Meridius']
from lxml.etree import _Element
from lxml import etree

from pyepidoc.epidoc.epidoc import EpiDoc, Token, Expan
from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.utils import head
from pyepidoc.epidoc.funcs import lang, line

import pytest

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


def test_collect_tokens():
    filepath = relative_filepaths['ISic000001']
    doc = EpiDoc(filepath)

    assert doc.tokens_list_str == [
        'dis', 
        'manibus', 
        'Zethi', 
        'vixit', 
        'annis', 
        'VI'
    ]

def test_collect_normalized():
    """
    Tests that tokens with <orig> / <reg> or <sic> / <corr> distinctions
    are use the normalized version
    """

    filepath = relative_filepaths['ISic000552']
    doc = EpiDoc(filepath)

    assert doc.tokens_list_str[0:2] == [
        'Flamma', 
        'secutor'
    ]


def test_leiden_plus_text():
    """
    Tests that collects the leiden plus text of a 
    token correctly
    """

    fp = relative_filepaths['leiden']
    doc = EpiDoc(fp)

    leiden_strs = [token.leiden_plus_form for token in doc.tokens]
    
    assert leiden_strs[0] == '| · Dis · '


def test_expans():
    filepath = relative_filepaths['ISic000001']
    
    doc = EpiDoc(filepath)
    edition = head(doc.editions())

    assert edition != None
    assert len(edition.expan_elems) == 3


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
    elem = etree.fromstring(xmlstr)
    token = Expan(elem)
    assert str(token) == r"A{A}U{U}G{G}ustorum"


def test_langs():
    """
    Tests that the collecting of language information happens in the correct way.
    """

    doc_1 = EpiDoc(relative_filepaths['langs_1'])

    expan_1 = head(doc_1.expans)
    token_1 = head(doc_1.tokens)
    assert expan_1 is not None and token_1 is not None

    assert doc_1.langs == ['la', 'grc']
    assert lang(expan_1) == 'la'
    assert lang(token_1) == 'grc'

    doc_2 = EpiDoc(relative_filepaths['langs_2'])
    expan_2 = head(doc_2.expans)
    token_2 = head(doc_2.tokens)
    assert expan_2 is not None and token_2 is not None

    assert lang(expan_2) == 'la'
    assert lang(token_2) == 'grc'

    doc_3 = EpiDoc(relative_filepaths['langs_3'])
    expan_3 = head(doc_3.expans)
    token_3 = head(doc_3.tokens)
    assert expan_3 is not None and token_3 is not None

    assert lang(expan_3) == 'la'
    assert lang(token_3) == 'grc'


def test_lines():
    doc_1 = EpiDoc(relative_filepaths['line_1'])

    token = head(doc_1.tokens)
    assert token is not None

    l1 = line(token)
    assert l1 is not None
    assert l1.n == '1'

    supplied = head(token.supplied)
    assert supplied is not None
    
    l2 = line(supplied)
    assert l2 is not None

    assert l2.n == '1'

    doc_2 = EpiDoc(relative_filepaths['line_2'])
    token = head(doc_2.tokens)
    assert token is not None

    l3 = line(token)
    assert l3 is not None

    assert l3.n == '1'
    
    second_token = doc_2.tokens[1]
    assert second_token.text_desc == 'ambulavit'

    l4 = line(second_token)
    assert l4 is not None
    assert l4.n == '2'


def test_gaps():
    doc = EpiDoc(relative_filepaths['gap'])
    has_gaps = doc.has_gap(reasons=['lost'])
    assert has_gaps == True


def test_nested():
    doc = EpiDoc(relative_filepaths['persName_nested'])
    assert doc.tokens_list_str == ['Maximus', 'Decimus', 'meridius']
    assert [str(token) for token in doc.w_tokens] == ['meridius']


def test_punct():
    """
    Tests that comma is removed from string version of token
    """
    doc = EpiDoc(relative_filepaths['comma']) 
    assert str(doc.tokens[0]) == "hello"


@pytest.mark.parametrize("filepath", relative_filepaths.values())
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath)
    assert doc.tokens_list_str != []


def test_reproduces_processing_instructions():
    doc = EpiDoc(relative_filepaths['line_2'])
    doc.to_xml_file(line_2_output)
    doc_ = EpiDoc(line_2_output)
    assert len(doc.processing_instructions) == len(doc_.processing_instructions)
    assert all([str(instr) in list(map(str, doc.processing_instructions)) 
                for instr in doc_.processing_instructions])
    
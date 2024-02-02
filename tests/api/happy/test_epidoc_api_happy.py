
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.utils import head
from pyepidoc.epidoc.dom import lang, line

import pytest

relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'api/files/single_files_tokenized/ISic000552.xml',
    'persName_nested': 'api/files/persName_nested.xml',
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
        'Dis', 
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


@pytest.mark.parametrize("filepath", relative_filepaths.values())
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath)
    assert doc.tokens_list_str != []


def test_materialclasses():
    doc = EpiDoc(relative_filepaths['ISic000001'])
    assert doc.materialclasses == ['#material.stone.marble']


def test_punct():
    """
    Tests that comma is removed from string version of token
    """
    doc = EpiDoc(relative_filepaths['comma']) 
    assert str(doc.tokens[0]) == "hello"


def test_check_ns_on_load():
    """
    
    """
    _ = EpiDoc(relative_filepaths['ISic000001'])


def test_reproduces_processing_instructions():
    doc = EpiDoc(relative_filepaths['line_2'])
    doc.to_xml_file(line_2_output)
    doc_ = EpiDoc(line_2_output)
    assert len(doc.processing_instructions) == len(doc_.processing_instructions)
    assert all([str(instr) in list(map(str, doc.processing_instructions)) 
                for instr in doc_.processing_instructions])
    
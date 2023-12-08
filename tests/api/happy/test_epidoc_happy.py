from pyepidoc.epidoc.epidoc import EpiDoc
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
    'leiden': 'api/files/leiden.xml'
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


def test_langs():
    """
    Tests that the collecting of language information happens in the correct way.
    """

    doc_1 = EpiDoc(relative_filepaths['langs_1'])

    assert doc_1.langs == ['la', 'grc']
    assert lang(head(doc_1.expans)) == 'la'
    assert lang(head(doc_1.tokens)) == 'grc'

    doc_2 = EpiDoc(relative_filepaths['langs_2'])
    assert lang(head(doc_2.expans)) == 'la'
    assert lang(head(doc_2.tokens)) == 'grc'

    doc_3 = EpiDoc(relative_filepaths['langs_3'])
    assert lang(head(doc_3.expans)) == 'la'
    assert lang(head(doc_3.tokens)) == 'grc'


def test_lines():
    doc_1 = EpiDoc(relative_filepaths['line_1'])

    token = head(doc_1.tokens)
    assert line(token).n == '1'

    supplied = head(token.supplied)
    assert line(supplied).n == '1'

    doc_2 = EpiDoc(relative_filepaths['line_2'])
    token = head(doc_2.tokens)

    assert line(token).n == '1'
    
    second_token = doc_2.tokens[1]
    assert second_token.text_desc == 'ambulavit'
    assert line(second_token).n == '2'


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
    
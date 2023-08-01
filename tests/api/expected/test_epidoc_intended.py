from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.utils import head
from pyepidoc.epidoc.funcs import lang, line

import pytest

relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'persName_nested': 'api/files/persName_nested.xml',
    'langs_1': 'api/files/langs_1.xml',
    'langs_2': 'api/files/langs_2.xml',
    'langs_3': 'api/files/langs_3.xml',
    'line_1': 'api/files/line_1.xml',
    'line_2': 'api/files/line_2.xml',
    'gap': 'api/files/gap.xml'
}


def test_collect_tokens():
    filepath = relative_filepaths['ISic000001']
    doc = EpiDoc(filepath, fullpath=False)

    assert doc.tokens_list_str == [
        'dis', 
        'manibus', 
        'Zethi', 
        'vixit', 
        'annis', 
        'VI'
    ]


def test_expans():
    filepath = relative_filepaths['ISic000001']
    
    doc = EpiDoc(filepath, fullpath=False)
    edition = head(doc.editions())

    assert edition != None
    assert len(edition.expan_elems) == 3


def test_langs():
    """
    Tests that the collecting of language information happens in the correct way.
    """

    doc_1 = EpiDoc(relative_filepaths['langs_1'], fullpath=False)

    assert doc_1.langs == ['la', 'grc']
    assert lang(head(doc_1.expans)) == 'la'
    assert lang(head(doc_1.tokens)) == 'grc'

    doc_2 = EpiDoc(relative_filepaths['langs_2'], fullpath=False)
    assert lang(head(doc_2.expans)) == 'la'
    assert lang(head(doc_2.tokens)) == 'grc'

    doc_3 = EpiDoc(relative_filepaths['langs_3'], fullpath=False)
    assert lang(head(doc_3.expans)) == 'la'
    assert lang(head(doc_3.tokens)) == 'grc'


def test_lines():
    doc_1 = EpiDoc(relative_filepaths['line_1'], fullpath=False)

    token = head(doc_1.tokens)
    assert line(token).n == '1'

    supplied = head(token.supplied)
    assert line(supplied).n == '1'

    doc_2 = EpiDoc(relative_filepaths['line_2'], fullpath=False)
    token = head(doc_2.tokens)

    assert line(token).n == '1'
    
    second_token = doc_2.tokens[1]
    assert second_token.text_desc == 'ambulavit'
    assert line(second_token).n == '2'


def test_gaps():
    doc = EpiDoc(relative_filepaths['gap'], fullpath=False)
    has_gaps = doc.has_gap(reasons=['lost'])
    assert has_gaps == True


def test_nested():
    doc = EpiDoc(relative_filepaths['persName_nested'], fullpath=False)
    assert doc.tokens_list_str == ['Maximus', 'Decimus', 'meridius']
    assert [str(token) for token in doc.w_tokens] == ['meridius']


@pytest.mark.parametrize("filepath", relative_filepaths.values())
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath, fullpath=False)
    assert doc.tokens_list_str != []
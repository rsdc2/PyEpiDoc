from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.utils import head
from pyepidoc.epidoc.funcs import lang

import pytest

relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'langs_1': 'api/files/langs_1.xml',
    'langs_2': 'api/files/langs_2.xml',
    'langs_3': 'api/files/langs_3.xml'
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


@pytest.mark.parametrize("filepath", relative_filepaths.values())
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath, fullpath=False)
    assert doc.tokens_list_str != []
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.utils import head
from pyepidoc.epidoc.funcs import lang

import pytest

relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'lang': 'api/files/langs.xml'
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
    edition = head(doc.editions)

    assert edition != None
    assert len(edition.expan_elems) == 3


def test_langs():
    """
    Tests that the collecting of language information happens in the correct way.
    """

    doc = EpiDoc(relative_filepaths['lang'], fullpath=False)

    assert doc.textlangs == {'la', 'grc'}
    assert lang(head(doc.expans)) == 'la'
    assert lang(head(doc.tokens)) == 'grc'


@pytest.mark.parametrize("filepath", relative_filepaths.values())
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath, fullpath=False)
    assert doc.tokens_list_str != []
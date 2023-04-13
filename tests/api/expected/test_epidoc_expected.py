from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.utils import head

import pytest

relative_filepaths = [
    'api/files/single_files_untokenized/ISic000001.xml'
]


def test_collect_tokens():
    filepath = relative_filepaths[0]
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
    filepath = relative_filepaths[0]
    
    doc = EpiDoc(filepath, fullpath=False)
    edition = head(doc.editions)

    assert edition != None
    assert len(edition.expan_elems) == 3


@pytest.mark.parametrize("filepath", relative_filepaths)
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath, fullpath=False)
    assert doc.tokens_list_str != []
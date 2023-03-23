from pyepidoc.epidoc.epidoc import EpiDoc
import pytest

relative_filepaths = [
    'tests/api/files/single_files_untokenized/ISic000001.xml'
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

@pytest.mark.parametrize("filepath", relative_filepaths)
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath, fullpath=False)
    assert doc.tokens_list_str != []


from pyepidoc import EpiDoc
from pathlib import Path
from pyepidoc.epidoc.errors import (
    TEINSError, 
    EpiDocValidationError
)
import pytest

test_files_path = "tests/api/files/"

def test_does_not_create_folderpath():
    """
    Test that error is raised if try to write to folderpath
    that does not exist
    """
    test_file = 'tests/api/files/line_2_output.xml'
    doc = EpiDoc(test_file)

    with pytest.raises(FileExistsError):
        doc.to_xml_file('filepath/testfile.xml')


def test_check_ns_on_load():
    test_file = 'tests/api/files/isic_file_no_tei_ns.xml'
    with pytest.raises(TEINSError):
        _ = EpiDoc(test_file)

test_doc_main_edition_is_empty_files = [
    'ISic000001.xml'
]
@pytest.mark.parametrize("filename", test_doc_main_edition_is_empty_files)
def test_doc_main_edition_is_empty(filename: str):
    path = Path(test_files_path + "single_files_untokenized") / Path(filename)
    doc = EpiDoc(path)

    assert not doc.main_edition.has_only_whitespace
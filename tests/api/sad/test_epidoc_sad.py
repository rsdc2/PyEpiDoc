from pyepidoc import EpiDoc
from pyepidoc.epidoc.errors import (
    TEINSError, 
    EpiDocValidationError
)
import pytest


def test_does_not_create_folderpath():
    """
    Test that error is raised if try to write to folderpath
    that does not exist
    """
    test_file = 'api/files/line_2_output.xml'
    doc = EpiDoc(test_file)

    with pytest.raises(FileExistsError):
        doc.to_xml_file('filepath/testfile.xml')


def test_check_ns_on_load():
    test_file = 'api/files/isic_file_no_tei_ns.xml'
    with pytest.raises(TEINSError):
        _ = EpiDoc(test_file)


def test_validate_on_load():
    with pytest.raises(EpiDocValidationError) as err:
        _ = EpiDoc(
            'api/files/single_files_untokenized/ISic000001_invalid.xml', 
            validate_on_load=True
        )
    assert ('196:0:ERROR:RELAXNGV:RELAXNG_ERR_CONTENTVALID: '
            'Element body failed to validate content') in str(err.value)
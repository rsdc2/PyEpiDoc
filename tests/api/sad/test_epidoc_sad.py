from pyepidoc import EpiDoc
import pytest

test_file = 'api/files/line_2_output.xml'

def test_does_not_create_folderpath():
    """
    Test that error is raised if try to write to folderpath
    when createfolderpath parameter is False
    """
    doc = EpiDoc(test_file)

    with pytest.raises(FileExistsError):
        doc.to_xml_file('filepath/testfile.xml')

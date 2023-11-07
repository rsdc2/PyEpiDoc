from pyepidoc.file import FileInfo, FileMode
import pytest

def test_file_does_not_exist_read():

    """
    Tests that asking FileInfo to read a non-existent file 
    raises a FileExistsError.
    """

    fp = "file/files/non_existent_file.xml"

    with pytest.raises(FileExistsError):
        f = FileInfo(
            filepath=fp,
            mode=FileMode.r,
            create_folderpath=False,
            fullpath=False
        )


def test_filepath_does_not_exist_write():

    """
    Tests that asking FileInfo to open a file in a 
    non-existent folder raises the right error.
    """
    
    fp = "file/non_existent_folder/non_existent_file.xml"

    with pytest.raises(FileExistsError):
        f = FileInfo(
            filepath=fp,
            mode=FileMode.w,
            create_folderpath=False,
            fullpath=False
        )        


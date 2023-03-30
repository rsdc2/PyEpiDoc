from pyepidoc.file import FileInfo, FileMode
import pytest
import os


def test_file_exists_read():

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


def test_filepath_does_not_exist_create_folderpath_write():

    """
    Tests that asking FileInfo to open a file in a 
    non-existent folder raises the right error.
    """
    
    fp = "file/non_existent_folder/non_existent_file.xml"

    # Load the FileInfo and create the folderpath

    try:
        f = FileInfo(
            filepath=fp,
            mode=FileMode.w,
            create_folderpath=True,
            fullpath=False
        )   

    except FileExistsError:
        pytest.fail("FileExistsError: there was a problem creating the folderpath.")     


    # Now that the folder path has been created,
    # Remove the folderpath and check that it has been 
    # removed.

    os.rmdir(f.full_folderpath)

    with pytest.raises(FileExistsError):
        f = FileInfo(
            filepath=fp,
            mode=FileMode.w,
            create_folderpath=False,
            fullpath=False
        )   
        

def test_write_file():
    s = "test string"

    fp = "file/non_existent_file.txt"

    fi = FileInfo(
        filepath=fp,
        mode=FileMode.w,
        create_folderpath=False,
        fullpath=False
    )

    # Write the file
    with open(fi.full_filepath, "w") as f:
        f.write(s)

    # Remove the file
    os.remove(fi.full_filepath)

    # Check the file has been removed
    with pytest.raises(FileExistsError):
        f = FileInfo(
            filepath=fp,
            mode=FileMode.r,
            create_folderpath=False,
            fullpath=False
        )  
import pytest
from pyepidoc import EpiDocCorpus
import os

corpus_folderpath = "api/files/corpus"


def test_load_corpus_local():
    """
    Test that raises an error if asked to load a corpus
    from a non-existent local folder
    """
    with pytest.raises(FileExistsError):
        _ = EpiDocCorpus('api/files/non_existent_folder', fullpath=False)


def test_load_corpus_root():
    """
    Test that raises an error if asked to load a corpus
    from a non-existent folder specified from root
    """

    with pytest.raises(FileExistsError):
        _ = EpiDocCorpus(os.getcwd() + '/api/files/non_existent_folder', fullpath=True)


def test_write_corpus_root():

    """
    Tests that raises a file exists error if tries to write to a non-existent folder
    without the create_folderpath parameter having been set to True
    """
    corpus = EpiDocCorpus(
        inpt=os.getcwd() + '/' + corpus_folderpath,
        head=None,
        fullpath=True
    )

    with pytest.raises(FileExistsError):
        corpus.tokenize_to_folder(os.getcwd() + '/' + corpus_folderpath + '/nonexistent_folder', 
                                  fullpath=True)

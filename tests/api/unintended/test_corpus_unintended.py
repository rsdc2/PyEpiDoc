import pytest
from pyepidoc import EpiDocCorpus
import os

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

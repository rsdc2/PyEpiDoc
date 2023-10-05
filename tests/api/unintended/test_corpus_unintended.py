import pytest
from pyepidoc import EpiDocCorpus
import os

def test_load_corpus_local():
    with pytest.raises(FileExistsError):
        _ = EpiDocCorpus('api/files/non_existent_folder', fullpath=False)


def test_load_corpus_root():
    with pytest.raises(FileExistsError):
        _ = EpiDocCorpus(os.getcwd() + '/api/files/non_existent_folder', fullpath=True)

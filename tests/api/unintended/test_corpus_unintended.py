import pytest
from pyepidoc import EpiDocCorpus


def test_load_corpus():
    with pytest.raises(FileExistsError):
        _ = EpiDocCorpus('api/files/non_existent_folder', fullpath=False)

from pyepidoc import EpiDocCorpus
from pathlib import Path

corpus_folderpath = "api/files/corpus"


def test_load_corpus_local():
    """
    Test that a corpus of files loads correctly.
    """

    corpus = EpiDocCorpus(inpt=corpus_folderpath)

    assert corpus.doc_count == 2
    assert corpus.token_count > 0


def test_load_corpus_root():
    """
    Test that a corpus of files loads correctly.
    """
    
    corpus = EpiDocCorpus(inpt=Path(corpus_folderpath).absolute())

    assert corpus.doc_count == 2
    assert corpus.token_count > 0
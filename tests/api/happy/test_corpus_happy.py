from pyepidoc import EpiDocCorpus
import os

corpus_folderpath = "api/files/corpus"


def test_load_corpus_local():
    """
    Test that a corpus of files loads correctly.
    """

    corpus = EpiDocCorpus(
        inpt=corpus_folderpath,
        head=None,
        fullpath=False
    )

    assert corpus.doc_count == 2
    assert corpus.token_count > 0


def test_load_corpus_root():
    """
    Test that a corpus of files loads correctly.
    """

    corpus = EpiDocCorpus(
        inpt=os.getcwd() + '/' + corpus_folderpath,
        head=None,
        fullpath=True
    )

    assert corpus.doc_count == 2
    assert corpus.token_count > 0

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


def test_materialclasses():
    """
    Test identification of material classes
    """

    corpus = EpiDocCorpus(inpt=corpus_folderpath)

    assert corpus.materialclasses == {
        '#material.stone.limestone', 
        '#material.stone.marble'
    }


def test_filter_materialclasses():
    """
    Test filtering of material classes
    """

    corpus = EpiDocCorpus(inpt=corpus_folderpath)
    filtered_corpus = corpus.filter_by_materialclass(
        ['#material.stone'], 
        'substring'
    )
    assert filtered_corpus.doc_count == 2

    corpus = EpiDocCorpus(inpt=corpus_folderpath)
    filtered_corpus = corpus.filter_by_materialclass(
        ['#material.stone.marble'], 
        'equal'
    )
    assert filtered_corpus.doc_count == 1
    assert filtered_corpus.docs[0].id == 'ISic000001'

from pyepidoc import EpiDocCorpus
from pathlib import Path

CORPUS_FOLDERPATH = 'tests/api/files/corpus'
CORPUS_ROLENAME_FOLDERPATH = 'tests/api/files/corpus_role_name'


def test_daterange():
    corpus = EpiDocCorpus(inpt=CORPUS_FOLDERPATH)
    assert corpus.daterange == (1, 300)


def test_load_corpus_local():
    """
    Test that a corpus of files loads correctly.
    """

    corpus = EpiDocCorpus(inpt=CORPUS_FOLDERPATH)

    assert corpus.doc_count == 2
    assert corpus.token_count > 0


def test_load_corpus_root():
    """
    Test that a corpus of files loads correctly.
    """
    
    corpus = EpiDocCorpus(inpt=Path(CORPUS_FOLDERPATH).absolute())

    assert corpus.doc_count == 2
    assert corpus.token_count > 0


def test_materialclasses():
    """
    Test identification of material classes
    """

    corpus = EpiDocCorpus(inpt=CORPUS_FOLDERPATH)

    assert corpus.materialclasses == {
        '#material.stone.limestone', 
        '#material.stone.marble'
    }


def test_filter_materialclasses():
    """
    Test filtering of material classes
    """

    corpus = EpiDocCorpus(inpt=CORPUS_FOLDERPATH)
    filtered_corpus = corpus.filter_by_materialclass(
        ['#material.stone'], 
        'substring'
    )
    assert filtered_corpus.doc_count == 2

    corpus = EpiDocCorpus(inpt=CORPUS_FOLDERPATH)
    filtered_corpus = corpus.filter_by_materialclass(
        ['#material.stone.marble'], 
        'equal'
    )
    assert filtered_corpus.doc_count == 1
    assert filtered_corpus.docs[0].id == 'ISic000001'


def test_filter_rolenames():
    """
    Test filtering of role names
    """

    corpus = EpiDocCorpus(inpt=CORPUS_ROLENAME_FOLDERPATH)
    filtered_corpus = corpus.filter_by_role_name_type(
        ['supracivic']
    ).filter_by_role_name_subtype(['imperator'])
    assert filtered_corpus.doc_count == 2
    assert corpus.doc_count == 4
    # assert filtered_corpus.docs[0].role_names.__len__() == 1


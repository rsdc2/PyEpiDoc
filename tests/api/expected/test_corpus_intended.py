from pyepidoc import EpiDocCorpus

corpus_folderpath = "api/files/corpus"


def test_load_corpus():
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
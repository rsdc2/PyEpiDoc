from pyepidoc import EpiDocCorpus

corpus_folderpath = "tests/api/files/corpus"


def test_load_corpus():
    """
    Test that a corpus of files loads correctly.
    """

    corpus = EpiDocCorpus(
        folderpath=corpus_folderpath,
        head=None,
        fullpath=False
    )

    print(corpus.tokens)
    breakpoint()
    assert corpus.doccount == 2
    assert corpus.tokencount > 0
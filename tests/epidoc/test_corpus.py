from pyepidoc import EpiDocCorpus

def test_corpus_lemmatizable():
    # Arrange
    corpus = EpiDocCorpus(r'tests/api/files/corpus')

    # Act
    lemmatizable_count = corpus.lemmatizable_files().count

    # Assert
    assert lemmatizable_count == 2
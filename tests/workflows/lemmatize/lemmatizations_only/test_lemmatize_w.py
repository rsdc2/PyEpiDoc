from pyepidoc import EpiDoc

from pyepidoc.shared.file import remove_file
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark, save_and_reload
from tests.config import FILE_WRITE_MODE
unlemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/unlemmatized/'
lemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/lemmatized/'


def test_set_lemma():
    
    """
    Test that can set the lemma attribute
    of a token element
    """

    # Arrange 
    filename = 'lemmatized.xml'
    doc = EpiDoc(unlemmatized_path + 'single_token.xml')

    ws = doc.w_tokens
    w = ws[0]
    assert w.text_desc == 'σώματος'

    # Act
    w.lemma = 'σῶμα'
    doc = doc.prettify('pyepidoc')
    doc_ = save_and_reload(doc, lemmatized_path + filename, FILE_WRITE_MODE)

    # Assert
    assert doc_.w_tokens[0].lemma == 'σῶμα'
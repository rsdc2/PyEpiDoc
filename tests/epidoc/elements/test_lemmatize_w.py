from pyepidoc import EpiDoc
from pyepidoc.epidoc.elements.w import W

from pyepidoc.shared.file import remove_file

unlemmatized_path = 'epidoc/elements/files/unlemmatized/'
lemmatized_path = 'epidoc/elements/files/lemmatized/'


def test_set_lemma():
    """
    Test that can set the lemma attribute
    of a token element
    """
    filename = 'lemmatized.xml'
    remove_file(lemmatized_path + filename)

    doc = EpiDoc(unlemmatized_path + 'unlemmatized.xml')
    ws = doc.w_tokens
    w = ws[0]
    assert w.text_desc == 'σώματος'

    w.lemma = 'σῶμα'
    
    doc.to_xml_file(lemmatized_path + filename)
    
    doc_ = EpiDoc(lemmatized_path + filename)

    assert doc_.w_tokens[0].lemma == 'σῶμα'
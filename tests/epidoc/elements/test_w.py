from pyepidoc import EpiDoc
from pyepidoc.epidoc.elements.w import W


def test_set_lemma():
    path = 'epidoc/elements/files/'

    doc = EpiDoc(path + 'lemmatize.xml')
    ws = doc.w_tokens
    w = ws[0]
    assert w.text == 'σώματος'

    w.lemma = 'σῶμα'
    
    doc.to_xml_file(path + 'lemmatized.xml')
    
    doc_ = EpiDoc(path + 'lemmatized.xml')

    assert doc_.w_tokens[0].lemma == 'σῶμα'
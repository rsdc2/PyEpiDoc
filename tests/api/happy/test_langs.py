"""
Tests for picking up language information correctly from
EpiDoc files
"""

from pyepidoc import EpiDoc
from pyepidoc.utils import head
from pyepidoc.epidoc.dom import lang


relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'api/files/single_files_tokenized/ISic000552.xml',
    'langs_1': 'api/files/langs_1.xml',
    'langs_2': 'api/files/langs_2.xml',
    'langs_3': 'api/files/langs_3.xml',
}

def test_langs():
    """
    Tests that the collecting of language information happens in the correct way.
    """

    doc_1 = EpiDoc(relative_filepaths['langs_1'])

    expan_1 = head(doc_1.expans)
    token_1 = head(doc_1.tokens)
    assert expan_1 is not None and token_1 is not None

    assert doc_1.langs == ['la', 'grc']
    assert lang(expan_1) == 'la'
    assert lang(token_1) == 'grc'

    doc_2 = EpiDoc(relative_filepaths['langs_2'])
    expan_2 = head(doc_2.expans)
    token_2 = head(doc_2.tokens)
    assert expan_2 is not None and token_2 is not None

    assert lang(expan_2) == 'la'
    assert lang(token_2) == 'grc'

    doc_3 = EpiDoc(relative_filepaths['langs_3'])
    expan_3 = head(doc_3.expans)
    token_3 = head(doc_3.tokens)
    assert expan_3 is not None and token_3 is not None

    assert lang(expan_3) == 'la'
    assert lang(token_3) == 'grc'
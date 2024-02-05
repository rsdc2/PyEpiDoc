"""
Tests for picking up language information correctly from
EpiDoc files
"""

from pyepidoc import EpiDoc
from pyepidoc.shared import head
from pyepidoc.epidoc.dom import lang

import pytest

tests = [
    ('api/files/langs_1.xml', ['la', 'grc'], 'la', 'grc'), 
    ('api/files/langs_2.xml', ['la', 'grc'], 'la', 'grc'),
    ('api/files/langs_3.xml', ['la', 'grc'], 'la', 'grc'),
    ('api/files/langs_4.xml', ['la'], 'la', 'la'),
]


@pytest.mark.parametrize([
    'fp', 
    'langs', 
    'first_expan_lang', 
    'first_token_lang'], tests)
def test_langs(
    fp: str, 
    langs: list[str], 
    first_expan_lang: str, 
    first_token_lang: str
    ):
    """
    Tests that the collecting of language information happens in the correct way.
    """

    doc_1 = EpiDoc(fp)

    expan_1 = head(doc_1.expans)
    token_1 = head(doc_1.tokens)
    assert expan_1 is not None and token_1 is not None

    assert doc_1.langs == langs
    assert lang(expan_1) == first_expan_lang
    assert lang(token_1) == first_token_lang

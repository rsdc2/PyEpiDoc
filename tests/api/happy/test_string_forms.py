"""
Tests that the string representations of individual tokens,
or sequences of tokens, are as expected.
"""

from pyepidoc.epidoc.elements.ab import Ab
from pyepidoc.xml.utils import elem_from_str, abify

import pytest

tests = [
    ('<w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>', 
     ['IIviro'], ['IIvir(o)']), 
    ('<w><expan><abbr><num value="2">II</num>vir</abbr><ex>o</ex></expan></w>', 
     ['IIviro'], ['IIvir(o)']),
    ('<w><expan><abbr><num value="11">XI</num></abbr><ex>Undeci</ex><abbr>manorum</abbr></expan></w>',
     ['XIUndecimanorum'], ['XI(Undeci)manorum'])
]


@pytest.mark.parametrize(['xml', 'normalized_tokens', 'leiden_tokens'], tests)
def test_normalized_string_forms(
    xml: str, 
    normalized_tokens: list[str],
    leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert ab.tokens_list_normalized_str == normalized_tokens


@pytest.mark.parametrize(['xml', 'normalized_tokens', 'leiden_tokens'], tests)
def test_leiden_string_forms(
    xml: str, 
    normalized_tokens: list[str], 
    leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert ab.tokens_list_leiden_str == leiden_tokens

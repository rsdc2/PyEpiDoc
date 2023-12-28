"""
Tests that the string representations of individual tokens,
or sequences of tokens, are as expected.
"""

from pyepidoc.epidoc.elements.ab import Ab
from pyepidoc.xml.utils import elem_from_str, abify

import pytest

tests = [
    ('<w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>', 
     ['IIviro']), 
    ('<w><expan><abbr><num value="2">II</num>vir</abbr><ex>o</ex></expan></w>', 
     ['IIviro']), 
]


@pytest.mark.parametrize(['xml', 'tokens'], tests)
def test_normalized_string_forms(xml: str, tokens: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert ab.tokens_list_normalized_str == tokens



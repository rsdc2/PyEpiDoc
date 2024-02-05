"""
Test that <corr> / <sic> and <orig> / <reg> pairs display
correct Leiden plus text
"""

import pytest
from pyepidoc.epidoc.token import Token
from pyepidoc.xml.utils import elem_from_str
from pyepidoc.shared.constants import TEINS

tests = [
    (f'<w xmlns="{TEINS}"><choice><sic>que</sic><corr>quae</corr></choice></w>',
     'que',
     'quae')
]

@pytest.mark.parametrize(['xml', 'sic', 'corr'], tests)
def test_corr(xml: str, sic: str, corr: str):

    w = Token(elem_from_str(xml))
    assert w.normalized_form == corr


@pytest.mark.parametrize(['xml', 'sic', 'corr'], tests)
def test_sic(xml: str, sic: str, corr: str):

    w = Token(elem_from_str(xml))
    assert w.leiden_plus_form == sic

"""
Test that <corr> / <sic> and <orig> / <reg> pairs display
correct Leiden plus text
"""

import pytest
from lxml import etree
from pyepidoc.epidoc.token import Token

tests = [
    ('<w><choice><sic>que</sic><corr>quae</corr></choice></w>',
     'que',
     'quae')
]

@pytest.mark.parametrize(['test'], tests)
def test_corr_sic(test: tuple[str, str, str]):
    xml, sic, corr = test

    e = etree.fromstring(xml, None)
    
    w = Token(xml)
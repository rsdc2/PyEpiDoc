"""
Test that <corr> / <sic> and <orig> / <reg> pairs display
correct Leiden plus text
"""

import pytest
from pyepidoc.xml.xml_node_types import XmlElement
from pyepidoc.epidoc.token import Token
from pyepidoc.shared.constants import TEINS

tests = [
    (f'<w xmlns="{TEINS}"><choice><sic>que</sic><corr>quae</corr></choice></w>',
     'que',
     'quae')
]

@pytest.mark.parametrize(['xml', 'sic', 'corr'], tests)
def test_corr(xml: str, sic: str, corr: str):

    elem = XmlElement.from_str(xml)
    w = Token(elem)
    assert w.normalized_form == corr


@pytest.mark.parametrize(['xml', 'sic', 'corr'], tests)
def test_sic(xml: str, sic: str, corr: str):

    w = Token(XmlElement.from_str(xml))
    assert w.leiden_plus_form == sic

"""
Tests that the string representations of individual tokens,
or sequences of tokens, are as expected.
"""

from pyepidoc.epidoc.elements.ab import Ab
from pyepidoc.xml.utils import elem_from_str, abify

import pytest

leiden_and_normalized_tests = [
    ('<w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>', 
     ['IIviro'], ['IIvir(o)']), 
    ('<w><expan><abbr><num value="2">II</num>vir</abbr><ex>o</ex></expan></w>', 
     ['IIviro'], ['IIvir(o)']),
    ('<w><expan><abbr><num value="11">XI</num></abbr><ex>Undeci</ex><abbr>manorum</abbr></expan></w>',
     ['Undecimanorum'], ['XI(Undeci)manorum']),
    ('<w><expan><abbr><num value="11">XI</num></abbr><ex>Undeci</ex><abbr>manorum</abbr></expan></w>',
     ['Undecimanorum'], ['XI(Undeci)manorum']),
    ('<w><expan><abbr><am><g ref="#christogram">☧</g></am></abbr><ex>Christi</ex></expan></w>',
     ['Christi'], ['{☧}(Christi)']),
    ('<w>die<surplus>e</surplus>s</w>',
     ['dies'], [r'die{e}s']),
    ('<w><expan><abbr>no<hi rend="small">v</hi>e<choice><corr>m</corr><sic>n</sic></choice>b</abbr><ex>res</ex></expan></w>',
     ['novembres'], ['novenb(res)']),
    ('<w><expan><abbr>A<am>A</am>U<am>U</am></abbr><ex>gustis</ex></expan></w>',
     ['Augustis'], [r'A{A}U{U}(gustis)']),
    ('<w>ἐτελεύτη<g ref="#ivy-leaf">❦</g><lb n="2" break="no"/>σεν</w>',
     ['ἐτελεύτησεν'], [r'ἐτελεύτη · |σεν']) 
]

leiden_plus_tests = [
    ('<w>ἐτῶν</w>\n<lb n="7"/>',
     ['ἐτῶν'], [r'ἐτῶν|']),
    ('<lb n="7"/><num value="37">λζ</num>  ',
     ['λζ'], [r'|λζ'])  
]


@pytest.mark.parametrize(['xml', 'normalized_tokens', 'leiden_tokens'], leiden_and_normalized_tests)
def test_normalized_string_forms(
    xml: str, 
    normalized_tokens: list[str],
    leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert ab.tokens_list_normalized_str == normalized_tokens


@pytest.mark.parametrize(['xml', 'normalized_tokens', 'leiden_tokens'], leiden_and_normalized_tests)
def test_leiden_string_forms(
    xml: str, 
    normalized_tokens: list[str], 
    leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert ab.tokens_list_leiden_str == leiden_tokens


@pytest.mark.parametrize(['xml', 'leiden_forms', 'leiden_plus_forms'], leiden_and_normalized_tests)
def test_leiden_plus_forms(
    xml: str, 
    leiden_forms: list[str], 
    leiden_plus_forms: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert [token.leiden_plus_form for token in ab.tokens] == leiden_plus_forms

"""
Tests that the string representations of individual tokens,
or sequences of tokens, are as expected.
"""

from pyepidoc.epidoc.edition_elements.ab import Ab
from pyepidoc.xml.utils import elem_from_str, abify
from pyepidoc.epidoc.representable import Representable

import pytest

leiden_and_normalized_tests = [
    ('<w><expan><abbr><num value="2"><hi rend="intraline">II</hi></num>vir</abbr><ex>o</ex></expan></w>', 
     ['duoviro'], ['IIvir(o)']), 
    ('<w><expan><abbr><num value="2">II</num>vir</abbr><ex>o</ex></expan></w>', 
     ['duoviro'], ['IIvir(o)']),
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
     ['ἐτελεύτησεν'], [r'ἐτελεύτη❦|σεν']), 
    ('<w><expan><abbr><g ref="#christogram">☧</g></abbr><ex>ιστῷ</ex></expan></w>',
     ['Χριστῷ'], [r'☧(ιστῷ)']) ,
    ('<w><expan><abbr><hi rend="ligature"><am>dt</am></hi></abbr><ex>depositio</ex></expan></w>',
     ['depositio'], [r'{dt}(depositio)']),
    ('<w><expan><abbr><hi rend="reversed"><am>Ↄ</am></hi></abbr><ex>circiter</ex></expan></w>',
     ['circiter'], [r'{Ↄ}(circiter)']),
    ('<num value="3"><choice><orig>tris</orig><reg>tres</reg></choice></num>',
     ['tres'], ['tris']),
    ('<num value="73">ο <g ref="#ivy-leaf">❦</g> γ </num>',
     ['ογ'], ['ο❦γ']),
    ('<w>mere<hi rend="ligature">nt<surplus><hi rend="tall">t</hi></surplus></hi>i</w>',
     ['merenti'], [r'merent{t}i'])
]

leiden_plus_tests = [
    ('<w>ἐτῶν</w>\n<lb n="7"/>',
     ['ἐτῶν'], [r'ἐτῶν|']),
    ('<lb n="7"/><num value="37">λζ</num>  ',
     ['λζ'], [r'|λζ'])  
]


@pytest.mark.parametrize(['xml', 'expected_normalized_tokens', 'leiden_tokens'], leiden_and_normalized_tests)
def test_normalized_string_forms(
    xml: str, 
    expected_normalized_tokens: list[str],
    leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    # Arrange
    ab = Ab(elem_from_str(abify(xml)))

    # Act
    normalized_tokens = ab.tokens_list_normalized_str

    # Assert
    assert normalized_tokens == expected_normalized_tokens


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


@pytest.mark.parametrize(['xml', 'leiden_forms', 'leiden_plus_forms'], leiden_plus_tests)
def test_leiden_plus_forms(
    xml: str, 
    leiden_forms: list[str], 
    leiden_plus_forms: list[str]):
    """
    Tests token strings correct
    """

    ab = Ab(elem_from_str(abify(xml)))
    assert [token.leiden_form for token in ab.tokens] == leiden_forms

    test_leiden_plus_forms = [token.leiden_plus_form for token in ab.tokens]
    if test_leiden_plus_forms != leiden_plus_forms:
        breakpoint()

    assert [token.leiden_plus_form for token in ab.tokens] == leiden_plus_forms


non_token_tests = [
    ('<gap reason="lost" unit="line" quantity="1"><desc>[-?-]</desc></gap>', 
     ['[-?-]'], [' [-?-] ']),
    ('<gap reason="lost" unit="line" quantity="1">[-?-]</gap>', 
     ['[-?-]'], [' [-?-] '])
]
@pytest.mark.parametrize(['xml', 'expected_normalized_tokens', 'leiden_tokens'], non_token_tests)
def test_non_tokens_normalized_string_forms(
    xml: str, 
    expected_normalized_tokens: list[str],
    leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    # Arrange
    ab = Ab(elem_from_str(abify(xml)))

    # Act
    normalized_tokens = [Representable(child).normalized_form for child in ab.children]

    # Assert
    assert normalized_tokens == expected_normalized_tokens


@pytest.mark.parametrize(['xml', 'expected_normalized_tokens', 'expected_leiden_tokens'], non_token_tests)
def test_non_tokens_leiden_string_forms(
    xml: str, 
    expected_normalized_tokens: list[str],
    expected_leiden_tokens: list[str]):
    """
    Tests token strings correct
    """

    # Arrange
    ab = Ab(elem_from_str(abify(xml)))

    # Act
    leiden_tokens = [Representable(child).leiden_form for child in ab.children]

    # Assert
    assert leiden_tokens == expected_leiden_tokens
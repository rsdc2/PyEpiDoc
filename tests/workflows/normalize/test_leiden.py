import pytest
from pyepidoc.epidoc.elements.edition import Edition
from pyepidoc.epidoc.elements.w import W
from pyepidoc.epidoc.token import Token
from pyepidoc.epidoc.element import EpiDocElement


token_elements = [
    ('<persName><name type="cognomen"><w>Melant<supplied reason="undefined" '
     'evidence="previouseditor">hi</supplied> '
     '<supplied reason="lost" evidence="previouseditor"><g ref="#interpunct">·</g></supplied>'
     '<lb n="5" break="no"/><g ref="#interpunct">·</g> n</w></name></persName>', 
     'Melanthi··n'),
    ('<w><choice><orig>decebris</orig><reg>decembres</reg></choice></w>',
     'decebris'),
    ('<w><expan><choice><orig><abbr>evok</abbr></orig><reg><abbr>evoc</abbr></reg></choice><ex>ato</ex></expan></w>',
     'evok(ato)'),
    ('<orig>CHEDONI</orig>', 'CHEDONI')
]

@pytest.mark.parametrize('inpt', token_elements)
def test_token_leiden_form(inpt: tuple[str, str]):

    xml_str, leiden_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)
    token = Token(elem.e)
    assert token.leiden_form == leiden_form


token_elements = [
    ('<persName><name type="cognomen"><w>Melant<supplied reason="undefined" '
     'evidence="previouseditor">hi</supplied> '
     '<supplied reason="lost" evidence="previouseditor"><g ref="#interpunct">·</g></supplied>'
     '<lb n="5" break="no"/><g ref="#interpunct">·</g> n</w></name></persName>', 
     'Melanthi··n'),
    ('<w><choice><orig>decebris</orig><reg>decembres</reg></choice></w>',
     'decebris'),
    ('<w><expan><choice><orig><abbr>evok</abbr></orig><reg><abbr>evoc</abbr></reg></choice><ex>ato</ex></expan></w>',
     'evok(ato)'),
    ('<orig>CHEDONI</orig>', 'CHEDONI')
]

@pytest.mark.parametrize('inpt', token_elements)
def test_token_leiden_plus_form(inpt: tuple[str, str]):

    xml_str, leiden_plus_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)
    token = Token(elem.e)
    assert token.leiden_plus_form == leiden_plus_form


@pytest.mark.parametrize(['xml_str', 'expected'], [
    ('<orig>CHEDONI</orig>', 'CHEDONI'),
    ('<name><w>Nearchia<supplied reason="lost">e</supplied></w></name>',
     'Nearchia[e]'),
    ('<name><w>Nearchia<supplied reason="lost">e</supplied></w></name> <gap reason="lost" extent="unknown" unit="character"/>',
     'Nearchia[e] [-?-]')
])
def test_edition_leiden(xml_str: str, expected: str):
    # Arrange
    edition = Edition.from_xml_str(xml_str=xml_str)

    # Act
    leiden_text = edition.get_text('leiden')

    # Assert
    assert leiden_text == expected
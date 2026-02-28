import pytest
from pyepidoc.epidoc.edition_elements.edition import Edition
from pyepidoc.epidoc.edition_elements.w import W
from pyepidoc.epidoc.token import Token
from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.xml.xml_element import XmlElement


token_elements = [
    ('<persName><name type="cognomen"><w>Melant<supplied reason="undefined">hi</supplied> '
     '<supplied reason="lost"><g ref="#interpunct">·</g></supplied>'
     '<lb n="5" break="no"/><g ref="#interpunct">·</g> n</w></name></persName>', 
     'Melant[hi][·]|·n'),
    ('<persName><name><w>Joe</w></name><name><w>Bloggs</w></name></persName>', 'Joe Bloggs'),
    ('<w><choice><orig>decebris</orig><reg>decembres</reg></choice></w>',
     'decebris'),
    ('<w><expan><choice><orig><abbr>evok</abbr></orig><reg><abbr>evoc</abbr></reg></choice><ex>ato</ex></expan></w>',
     'evok(ato)'),
    ('<w>Jo<lb break="no"/>e</w>', 'Jo|e'),
    ('<persName><name><w>Asi<lb break="no"/>atico</w></name></persName>', 'Asi|atico'),
    ('<w><expan><abbr>evok</abbr><ex>ato</ex></expan></w>', 'evok(ato)'),
    ('<w><expan><abbr>evok</abbr><ex>ato</ex></expan></w>', 'evok(ato)'),
    ('<w><orig>CHEDONI</orig></w>', 'CHEDONI'),
    ('<orig>hello</orig>', 'HELLO')
]

@pytest.mark.parametrize('inpt', token_elements)
def test_leiden_form_of_single_tokens(inpt: tuple[str, str]):

    # Arrange
    xml_str, expected_leiden_form = inpt
    elem = XmlElement.from_str(xml_str)
    token = Token(elem)
    
    # Act
    leiden_form = token.leiden_form

    # Assert
    assert leiden_form == expected_leiden_form


token_elements = [
    ('<persName><name type="cognomen"><w>Melant<supplied reason="undefined" '
     'evidence="previouseditor">hi</supplied> '
     '<supplied reason="lost" evidence="previouseditor"><g ref="#interpunct">·</g></supplied>'
     '<lb n="5" break="no"/><g ref="#interpunct">·</g> n</w></name></persName>', 
     'Melant[hi][·]|·n'),
    ('<w><choice><orig>decebris</orig><reg>decembres</reg></choice></w>',
     'decebris'),
    ('<w><expan><choice><orig><abbr>evok</abbr></orig><reg><abbr>evoc</abbr></reg></choice><ex>ato</ex></expan></w>',
     'evok(ato)'),
    ('<orig>CHEDONI</orig>', 'CHEDONI'),
    
]

@pytest.mark.parametrize('inpt', token_elements)
def test_token_leiden_plus_form_of_single_tokens(inpt: tuple[str, str]):
    # Arrange
    xml_str, leiden_plus_form = inpt
    elem = XmlElement.from_str(xml_str)
    token = Token(elem)

    # Act / Assert
    assert token.leiden_plus_form == leiden_plus_form


def test_leiden_plus_forms_of_tokens_in_context():
    # Arrange
    xml_str = '<lb n="1"/><g>·</g> <w>Dis</w> <g>·</g>'
    edition = Edition.from_xml_str(xml_str)

    # Act
    leiden_plus_str = edition.tokens_leiden_str

    # Assert
    assert leiden_plus_str == '| · Dis ·'
    

@pytest.mark.parametrize(['xml_str', 'expected'], [
    ('<orig>CHEDONI</orig>', 'CHEDONI'),
    ('<w>hello</w><lb n="1"/><w>hello</w>', 'hello\nhello'),
    ('<gap reason="lost" unit="character" extent="1"/>', '[-1-]'),
    ('<name><w>Nearchia<supplied reason="lost">e</supplied></w></name>',
     'Nearchia[e]'),
    ('<name><w>Nearchia<supplied reason="lost">e</supplied></w></name> <gap reason="lost" extent="unknown" unit="character"/>',
     'Nearchia[e-?-]'),
    ('<persName><w><expan><abbr>f</abbr><ex>ilio</ex></expan></w> <g ref="#interpunct">·</g> <name><w>Asi <lb break="no"/>atico</w></name></persName>', 
     'f(ilio) · Asi\natico'),
    ('<supplied><w>Joe</w></supplied><supplied><w>Bloggs</w></supplied><w>is</w>', '[Joe Bloggs] is'),
    ('<persName>'
        '<name>'
            '<supplied>'
                '<expan>'
                    '<abbr>Cn</abbr>'
                    '<ex>aei</ex>'
                '</expan>'
            '</supplied>'
        '</name>'
    '</persName>'
    '<w>'
        '<supplied>'
            '<expan>'
                '<abbr>f</abbr>'
                '<ex>ilio</ex>'
            '</expan>'
        '</supplied>'
    '</w>',
     '[Cn(aei) f(ilio)]')
])
def test_leiden_edition(xml_str: str, expected: str):
    # Arrange
    edition = Edition.from_xml_str(xml_str=xml_str)

    # Act
    leiden_text = edition.get_text('leiden')

    # Assert
    assert leiden_text == expected


if __name__ == '__main__':
    test_leiden_form_of_single_tokens(token_elements[1])
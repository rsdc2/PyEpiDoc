import pytest
from pyepidoc.epidoc.edition_elements.w import W
from pyepidoc.epidoc.token import Token
from pyepidoc.epidoc.representable import Representable
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.epidoc.edition_elements.edition import Edition

w_elements = [
    ('<persName><name type="cognomen"><w>Melant<supplied reason="undefined" '
     'evidence="previouseditor">hi</supplied> '
     '<supplied reason="lost" evidence="previouseditor"><g ref="#interpunct">·</g></supplied>'
     '<lb n="5" break="no"/><g ref="#interpunct">·</g> n</w></name></persName>', 
     'Melanthin'),
    ('<w><choice><orig>decebris</orig><reg>decembres</reg></choice></w>',
     'decembres'),
    ('<w><expan><choice><orig><abbr>evok</abbr></orig><reg><abbr>evoc</abbr></reg></choice><ex>ato</ex></expan></w>',
     'evocato')
    ]


@pytest.mark.parametrize('inpt', w_elements)
def test_w_normalization(inpt: tuple[str, str]):

    # Arrange
    xml_str, normalized_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)

    # Act 
    try:
        w = W(elem.desc_elems_by_local_name('w')[0].e)
    except IndexError:
        w = W(elem.e)

    # Assert
    assert w.normalized_form == normalized_form

token_elements = [
    ('<persName><name type="cognomen"><w>Melant<supplied reason="undefined" '
     'evidence="previouseditor">hi</supplied> '
     '<supplied reason="lost" evidence="previouseditor"><g ref="#interpunct">·</g></supplied>'
     '<lb n="5" break="no"/><g ref="#interpunct">·</g> n</w></name></persName>', 
     'Melanthin'),
    ('<w><choice><orig>decebris</orig><reg>decembres</reg></choice></w>',
     'decembres'),
    ('<w><expan><choice><orig><abbr>evok</abbr></orig><reg><abbr>evoc</abbr></reg></choice><ex>ato</ex></expan></w>',
     'evocato'),
    ('<orig>CHEDONI</orig>', 'CHEDONI'),
    ('<name>Prim<gap reason="lost" extent="unknown" unit="character"/>ius</name>', 'Prim[-?-]ius'),
    ('<w>Prim<gap reason="lost" extent="unknown" unit="character"/>ius</w>', 'Prim[-?-]ius')
]

@pytest.mark.parametrize('inpt', token_elements)
def test_token_normalization(inpt: tuple[str, str]):

    # Arrange
    xml_str, normalized_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)
    
    # Act
    token = Token(elem.e)
    
    # Assert
    assert token.normalized_form == normalized_form


representable_elements = [
    ('<orig>CHEDONI</orig>', 'CHEDONI'),
    ('<orig>hello</orig>', 'HELLO')
]

@pytest.mark.parametrize('inpt', representable_elements)
def test_representable_normalization(inpt: tuple[str, str]):

    # Arrange
    xml_str, normalized_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)
    
    # Act
    representable = Representable(elem.e)
    # breakpoint()
    # Assert
    assert representable.normalized_form == normalized_form


edition_elements = [
    ('<orig>CHEDONI</orig>', 'CHEDONI'),
    ('<orig>hello</orig>', 'HELLO')
]

@pytest.mark.parametrize('inpt', edition_elements)
def test_edition_normalization(inpt: tuple[str, str]):

    # Arrange
    xml_str, expected_normalized_text = inpt
    edition = Edition.from_xml_str(xml_str)
    
    # Act
    normalized = edition.get_text('normalized')
    
    # Assert
    assert normalized == expected_normalized_text


if __name__ == '__main__':
    # test_w_normalization(w_elements[0])
    test_representable_normalization(representable_elements[1])

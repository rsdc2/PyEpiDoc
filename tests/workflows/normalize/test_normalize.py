import pytest
from pyepidoc.epidoc.elements.w import W
from pyepidoc.epidoc.token import Token
from pyepidoc.epidoc.element import EpiDocElement

elements = [
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


@pytest.mark.parametrize('inpt', elements)
def test_w_normalization(inpt: tuple[str, str]):

    xml_str, normalized_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)
    try:
        w = W(elem.desc_elems_by_local_name('w')[0].e)
    except IndexError:
        w = W(elem.e)

    assert w.normalized_form == normalized_form


@pytest.mark.parametrize('inpt', elements)
def test_token_normalization(inpt: tuple[str, str]):

    xml_str, normalized_form = inpt
    elem = EpiDocElement.from_xml_str(xml_str)
    token = Token(elem.e)
    assert token.normalized_form == normalized_form


if __name__ == '__main__':
    test_w_normalization(elements[0])
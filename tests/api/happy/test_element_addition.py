from pyepidoc.constants import TEINS
from lxml import etree
from pyepidoc.epidoc.element import EpiDocElement
import pytest

xmls =[
    (f'<w xmlns="{TEINS}">domin</w>',
     f'<hi xmlns="{TEINS}">us</hi>', 
     f'<w xmlns="{TEINS}">domin<hi>us</hi></w>'),

    (f'<w xmlns="{TEINS}">d</w>',
     f'<hi xmlns="{TEINS}" rend="apex">u</hi>',
     f'<w xmlns="{TEINS}">d<hi rend="apex">u</hi></w>')
]

@pytest.mark.parametrize("xml_pair", xmls)
def test_w_hi(xml_pair: tuple[str, str, str]):
    xml1, xml2, result = xml_pair
    result_ = result.encode()

    e1 = etree.fromstring(xml1, None)
    e2 = etree.fromstring(xml2, None)

    elem1 = EpiDocElement(e1)
    elem2 = EpiDocElement(e2)

    elem = elem1 + elem2

    assert etree.tostring(elem[0].e) == result_


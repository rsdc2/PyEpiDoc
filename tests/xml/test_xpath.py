import pytest
from lxml import etree
from pyepidoc.xml import BaseElement

xpath_true = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
        'descendant::text()[position()=1] = descendant::text()[ancestor::ns:abbr][position()=1]')
]


xpath_false = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
     'descendant::text()[position()=1] = descendant::text()[ancestor::ns:abbr][position()=1]')
]


xpath_count = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
     'count(descendant::text()[ancestor::ns:abbr])',
     2.0)
]


@pytest.mark.parametrize("triple", xpath_count)
def test_xpath_count(triple: tuple[str, str, float]):
    xml, xpath, result = triple
    elem = etree.fromstring(xml, None)
    baseelem = BaseElement(elem)
    assert baseelem.xpath_float(xpath) == result


@pytest.mark.parametrize("pair", xpath_true)
def test_xpath_bool_true(pair: tuple[str, str]):

    xml, xpath = pair
    elem = etree.fromstring(xml, None)
    baseelem = BaseElement(elem)

    assert baseelem.xpath_bool(xpath)


@pytest.mark.parametrize("pair", xpath_false)
def test_xpath_bool_false(pair: tuple[str, str]):

    xml, xpath = pair
    elem = etree.fromstring(xml, None)
    baseelem = BaseElement(elem)

    assert not baseelem.xpath_bool(xpath)

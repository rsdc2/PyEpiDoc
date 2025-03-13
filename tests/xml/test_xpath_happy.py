from __future__ import annotations
import pytest
from typing import cast, List, Union
from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult
from pyepidoc.xml import BaseElement

xpath_true = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
        'descendant::text()[position()=1] = descendant::text()[ancestor::ns:abbr][position()=1]'),
    ('<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
        'local-name(descendant::text()[position()=1]/parent::*[position()=1]) = "abbr"'),
    
]


xpath_false = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
     'descendant::text()[position()=1] = descendant::text()[ancestor::ns:abbr][position()=1]')
]


xpath_count = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
     'count(descendant::text()[ancestor::ns:abbr])',
     2.0),
    ('<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
     'count(descendant::text()[ancestor::ns:abbr[position()=last()]][position()=1]/preceding::text()[ancestor::ns:expan[position()=last()]])',
     1.0)
]

xpathlist = [
    ('<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
        'descendant::text()[ancestor::ns:abbr][position()=1]/preceding::text()[ancestor::ns:expan[position()=1]]',
        cast(List[Union[_Element, _ElementUnicodeResult]], ['K'])),
    # ('<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
    #     'descendant::text()[position()=1]/ancestor::*',
    #     cast(List[Union[_Element, _ElementUnicodeResult]], ['K']))
]


@pytest.mark.parametrize("triple", xpath_count)
def test_xpath_count(triple: tuple[str, str, float]):
    xml, xpath, result = triple
    elem = etree.fromstring(xml, None)
    baseelem = BaseElement(elem)
    assert baseelem.xpath_float(xpath) == result


@pytest.mark.parametrize("triple", xpathlist)
def test_xpath(triple: tuple[str, str, list[_Element | _ElementUnicodeResult]]):
    xml, xpath, result = triple
    elem = etree.fromstring(xml, None)
    baseelem = BaseElement(elem)
    assert baseelem.xpath(xpath) == result


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

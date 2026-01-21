from __future__ import annotations
import pytest
from pyepidoc.xml import XmlElement

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
        ['K']),
    # ('<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>',
    #     'descendant::text()[position()=1]/ancestor::*',
    #     ['K'])
]


@pytest.mark.parametrize("triple", xpath_count)
def test_xpath_count(triple: tuple[str, str, float]):
    xml, xpath, result = triple
    elem = XmlElement.from_str(xml)
    assert elem.xpath_float(xpath) == result


@pytest.mark.parametrize("triple", xpathlist)
def test_xpath(triple: tuple[str, str, str]):
    # Arrange
    xml, xpath, expected_result = triple
    elem = XmlElement.from_str(xml)

    # Act
    result = [str(result) for result in elem.xpath(xpath)]
    
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("pair", xpath_true)
def test_xpath_bool_true(pair: tuple[str, str]):
    xml, xpath = pair
    elem = XmlElement.from_str(xml)
    assert elem.xpath_bool(xpath)


@pytest.mark.parametrize("pair", xpath_false)
def test_xpath_bool_false(pair: tuple[str, str]):

    xml, xpath = pair
    elem = XmlElement.from_str(xml)
    assert not elem.xpath_bool(xpath)

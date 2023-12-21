from lxml import etree
from pyepidoc.xml import BaseElement


def test_xpath_bool_true():
    xml = '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = etree.fromstring(xml, None)

    baseelem = BaseElement(elem)

    xpath = "descendant::text()[position()=1] = descendant::text()[ancestor::ns:abbr][position()=1]" 

    assert baseelem.xpath_bool(xpath)


def test_xpath_bool_false():
    xml = '<expan xmlns="http://www.tei-c.org/ns/1.0">K<abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = etree.fromstring(xml, None)

    baseelem = BaseElement(elem)

    xpath = "descendant::text()[position()=1] = descendant::text()[ancestor::ns:abbr][position()=1]" 

    assert not baseelem.xpath_bool(xpath)

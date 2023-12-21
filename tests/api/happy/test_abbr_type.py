import pytest

from pyepidoc.epidoc.abbr import Abbr
from pyepidoc.epidoc.expan import Expan
from pyepidoc.epidoc.epidoc_types import AbbrType
from lxml import etree


multiplications = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><hi rend="supraline"><abbr>d<am>d</am></abbr></hi><ex cert="low">ominis</ex></expan>',     # from ISic000501
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>d<am>d</am></abbr><ex>ominis</ex></expan>',
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr><am>d</am>d</abbr><ex>ominis</ex></expan>',
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>imp<am>p</am></abbr><ex>eratorum</ex></expan>',

]

non_multiplications = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr><am>Ͻ</am></abbr><ex>mulieris</ex></expan>',
]

suspensions = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>d</abbr><ex>omninis</ex></expan>'
]

contractions = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
]

non_contractions = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr><am><num value="6">VI</num></am></abbr><ex>se</ex><abbr>vir</abbr></expan>'
]


@pytest.mark.parametrize("xmlstr", multiplications)
def test_multiplicative(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert expan.is_multiplicative


@pytest.mark.parametrize("xmlstr", non_multiplications)
def test_non_multiplicative(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert not expan.is_multiplicative


@pytest.mark.parametrize("xmlstr", suspensions)
def test_suspensions(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert expan.abbr_type == AbbrType.suspension


@pytest.mark.parametrize("xmlstr", contractions)
def test_contractions(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert expan.abbr_type == AbbrType.contraction


@pytest.mark.parametrize("xmlstr", non_contractions)
def test_non_contractions(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert expan.abbr_type != AbbrType.contraction


def test_first_desc_node_is_desc_of_abbr():
    xml = '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>Kal</abbr><ex>enda</ex><abbr>s</abbr></expan>'
    elem = etree.fromstring(xml, None)
    expan = Expan(elem)
    assert expan.first_desc_textnode_is_desc_of('abbr') == True
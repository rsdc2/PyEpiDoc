import pytest

from pyepidoc.epidoc.abbr import Abbr
from pyepidoc.epidoc.expan import Expan
from pyepidoc.epidoc.epidoc_types import AbbrType
from lxml import etree


multiplications = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><hi rend="supraline"><abbr>d<am>d</am></abbr></hi><ex cert="low">ominis</ex></expan>',     # from ISic000501
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>d<am>d</am></abbr><ex>ominis</ex></expan>',
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr><am>d</am>d</abbr><ex>ominis</ex></expan>'
]

non_multiplications = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>d<am>d</am></abbr><ex>ominis</ex></expan>',
]

suspensions = [
    '<expan xmlns="http://www.tei-c.org/ns/1.0"><abbr>d</abbr><ex>omninis</ex></expan>'
]

@pytest.mark.parametrize("xmlstr", multiplications)
def test_multiplicative(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert expan.is_multiplicative


@pytest.mark.parametrize("xmlstr", suspensions)
def test_suspensions(xmlstr: str):

    elem = etree.fromstring(xmlstr, None)
    expan = Expan(elem)
    assert expan.abbr_type == AbbrType.suspension

from pyepidoc import EpiDoc
from pyepidoc.epidoc.epidoctypes import AbbrType

def test_abbr():
    doc = EpiDoc('api/files/abbreviations/multiplication.xml')

    assert len(doc.expans) == 1

    expan = doc.expans[0]
    assert len(expan.abbr) == 1
    assert len(expan.ex) == 1

    abbr = expan.abbr[0]
    assert len(abbr.am) == 1
    assert abbr.first_am is not None
    assert abbr.is_multiplicative == True
    assert expan.abbr_type == AbbrType.multiplication
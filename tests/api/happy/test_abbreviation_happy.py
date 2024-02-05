from pyepidoc import EpiDoc
from pyepidoc.epidoc.enums import AbbrType
from pyepidoc.shared import contains

def test_abbr():
    doc = EpiDoc('api/files/abbreviations/multiplication.xml')

    assert len(doc.expans) == 1

    expan = doc.expans[0]
    assert len(expan.abbrs) == 1
    assert len(expan.exs) == 1

    abbr = expan.abbrs[0]
    assert len(abbr.am) == 1
    assert abbr.first_am is not None
    assert abbr.is_multiplicative == True
    assert contains(expan.abbr_types, AbbrType.multiplication)
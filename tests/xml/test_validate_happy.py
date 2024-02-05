from __future__ import annotations
from pyepidoc import EpiDoc


def test_validate_relax_ng():
    """
    Test that validates against a RelaxNG schema
    """
    doc = EpiDoc('xml/files/ISic000002.xml')
    # doc = EpiDoc('xml/files/ex.xml')
    assert doc.validate_relaxng(doc._rng_path)[0] == True


# def test_validate_isoschematron():
#     # doc = EpiDoc('xml/files/ISic000002.xml')
#     doc = EpiDoc('xml/files/ex.xml')
#     assert doc.validate_isoschematron('../validation/ircyr-checking_.sch')

def test_validate_on_load():
    _ = EpiDoc('xml/files/ISic000001_no_xinclude.xml', 
               validate_on_load=True)


def test_validate_on_load_2():
    _ = EpiDoc('xml/files/ISic000001_with_xinclude.xml', 
               validate_on_load=True)
from __future__ import annotations
from pyepidoc import EpiDoc
from pathlib import Path
from lxml.etree import RelaxNG

# def test_validate_relax_ng():
#     """
#     Test that validates against a RelaxNG schema
#     """
#     doc = EpiDoc('xml/files/ISic000002.xml')
#     assert doc.validate_relaxng('../tei-epidoc.rng')


def test_validate_schematron():
    doc = EpiDoc('xml/files/ISic000002.xml')
    assert doc.validate_schematron('../ircyr-checking.sch')
    # assert doc.validate_schematron('../tei-epidoc.xml')

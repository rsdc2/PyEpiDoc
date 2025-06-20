"""
Tests for converting ids in EpiDoc files
"""

import pytest
from tests.config import FILE_WRITE_MODE
from pyepidoc.xml.utils import abify, editionify
from pyepidoc.epidoc.elements.edition import Edition
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc import EpiDoc


tests = [
    '<lb n="1" xml:id="AAKAK"/><w xml:id="AAKAU">Dis</w>'
]

# @pytest.mark.parametrize('xml', tests)
# def test_set_ids_in_epidoc_with_existing_ids_raises_error(xml: str):
#     # Arrange
#     edition_text = editionify(xml, wrap_in_ab=True)
#     element = EpiDocElement.from_xml_str(edition_text)
#     edition = Edition(element)
#     doc = EpiDoc('tests/workflows/ids_full/files/input/set_id_template.xml')
#     doc.edition


#     # Act
#     with pytest.raises(Exception):
#         edition.set_ids(100)

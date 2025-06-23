"""
Tests for converting ids in EpiDoc files
"""

import pytest
from tests.config import FILE_WRITE_MODE
from pyepidoc.xml.utils import abify, editionify
from pyepidoc.epidoc.edition_elements.edition import Edition
from pyepidoc.epidoc.edition_elements.ab import Ab

from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc import EpiDoc


tests = [
    '<lb n="1" xml:id="AAKAK"/><w xml:id="AAKAU">Dis</w>'
]

@pytest.mark.parametrize('xml', tests)
def test_set_ids_in_epidoc_with_existing_ids_raises_error(xml: str):
    # Arrange
    doc = EpiDoc('templates/empty_template.xml')
    doc.file_desc.ensure_publication_stmt().set_idno_by_type('filename', 'ISic000001')
    ab = Ab(XmlElement.from_xml_str(abify(xml)))
    _ = doc.main_edition.append_ab(ab)

    # Act
    with pytest.raises(Exception):
        doc.main_edition.set_ids(100)

"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pyepidoc import EpiDoc
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.edition_elements.ab import Ab
from pyepidoc.xml.utils import abify
from pyepidoc.shared.testing import save_and_reload
from tests.config import FILE_WRITE_MODE

# make_path = lambda s: Path(s + '.xml') 

# tests = map(make_path, [
#     'set_ids_1', 
#     'ISic001470'
# ])

set_ids_tests = [('ISic000001', '<lb n="1"/><w>Dis</w> <w>Man\n<lb n="2" break="no"/>ibus</w>', ['AAKAK', 'AAKAU', 'AAKAe', 'AAKAo']),
         
         ('ISic001470', '<lb n="1"/>Διον'  # ISic001470
         '<lb n="1a" break="no"/>ύσιος'
         '<lb n="2"/>τόδε'
         '<lb n="3"/>σᾶμα'
         '<lb n="4"/>το̄ <g ref="#dipunct">:</g> Σε'
         '<lb n="4a" break="no"/>λίν<supplied reason="lost">ιο</supplied>'
         '<lb n="5" break="no"/><supplied reason="lost">ς</supplied>', 
         
         ['BvAAK', "BvAAU", "BvAAe", "BvAAo", "BvAAy", "BvAAΙ", "BvAAΤ", "BvAAε", "BvAAο", "BvABA"])
         ]


@pytest.mark.parametrize(('isic_id', 'xml_str', 'expected'), set_ids_tests)
def test_set_ids_in_epidoc(isic_id: str, xml_str: str, expected: list[str]):
    # Arrange
    doc = EpiDoc('templates/empty_template.xml')
    doc.file_desc.publication_stmt.set_idno_by_type('filename', isic_id)
    ab = Ab(XmlElement.from_xml_str(abify(xml_str)))
    doc.main_edition.append_ab(ab)

    # Act
    doc.set_ids(base=100)

    # Assert
    assert doc.xml_ids == expected


set_missing_ids_tests = [
    ('ISic000001', '<lb xml:id="AAKAK" n="1"/><w>Dis</w> <w xml:id="AAKAe">Man\n<lb xml:id="AAKAo" n="2" break="no"/>ibus</w>', 
     ['AAKAK', 'AAKAU', 'AAKAe', 'AAKAo'])
]

@pytest.mark.parametrize(('isic_id', 'xml_str', 'expected'), set_missing_ids_tests)
def test_set_ids_in_epidoc(isic_id: str, xml_str: str, expected: list[str]):
    # Arrange
    doc = EpiDoc('templates/empty_template.xml')
    doc.file_desc.publication_stmt.set_idno_by_type('filename', isic_id)
    ab = Ab(XmlElement.from_xml_str(abify(xml_str)))
    doc.main_edition.append_ab(ab)

    # Act
    doc.set_missing_ids(base=100)

    # Assert
    assert doc.xml_ids == expected


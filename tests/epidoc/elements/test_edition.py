from pyepidoc import EpiDoc
from pyepidoc.epidoc.elements.edition import Edition
import pytest

@pytest.mark.parametrize(['xml_str', 'expected'], [
    ("<w>dis</w> <w>manibus</w> <w>sacrum</w> <orig>xyz</orig>", 75.00),
    ("<w>dis</w> <w>manibus</w> <w>sacrum</w>", 100.00),
    ("<persName><w>dis</w> <w>manibus</w></persName> <w>sacrum</w>", 100.00),
    ("<persName><orig>hasdfa</orig></persName> <w>sacrum</w>", 50.00)
])
def test_edition_lemmatizability(xml_str: str, expected: float):
    # Arrange
    edition = Edition.from_xml_str(xml_str=xml_str)

    # Act
    lemmatizability = edition.lemmatizability

    # Assert
    assert lemmatizability.percentage() == expected
    
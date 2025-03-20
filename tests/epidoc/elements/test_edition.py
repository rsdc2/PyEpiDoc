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


@pytest.mark.parametrize(['xml_str', 'expected'], [
    ('<roleName type="civic" subtype="duumvir"><w><expan><abbr><num value="2"><supplied reason="lost">I</supplied><unclear>I</unclear></num>vir</abbr><ex>o</ex></expan></w></roleName>', 1),
    ('<num value="2" xml:id="AJΤRU"><w><hi rend="supraline" xml:id="AJΤRe">II</hi></w></num>', 1)
])
def test_tokens_no_nested_count(xml_str: str, expected: float):
    # Arrange
    edition = Edition.from_xml_str(xml_str=xml_str)

    # Act
    tokens = edition.tokens_no_nested

    # Assert
    assert len(tokens) == expected
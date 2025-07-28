import pytest
from pyepidoc import EpiDoc
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.edition_elements.ab import Ab
from pyepidoc.epidoc.edition_elements.name import Name
from pyepidoc.epidoc.edition_elements.num import Num
from pyepidoc.xml.utils import abify
from pyepidoc.shared.testing import save_and_reload
from tests.config import FILE_WRITE_MODE, EMPTY_TEMPLATE_PATH


move_ids_tests = [
        ('<lb n="1"/><name xml:id="xyz"><w>Dis</w></name>', ['xyz']),
        ('<lb n="1"/><num xml:id="xyz"><w>Dis</w></num>', ['xyz'])
    ]
@pytest.mark.parametrize(['xml_str', 'xml_ids'], move_ids_tests)
def test_set_ids_in_epidoc(xml_str: str, xml_ids: list[str]):
    # Arrange
    doc = EpiDoc(EMPTY_TEMPLATE_PATH)
    ab = Ab(XmlElement.from_xml_str(abify(xml_str)))
    doc.main_edition.append_ab(ab)
    names = [Name(token.e) for token in doc.tokens if token.localname == 'name']
    nums =  [Num(token.e) for token in doc.tokens if token.localname == 'num']

    for xml_id in xml_ids:
        token = doc.main_edition.token_by_xml_id(xml_id)
        assert token.localname in ['name', 'num']

    # Act
    for name in names:
        name.move_xml_id_to_inner_w()
    for num in nums:
        num.move_xml_id_to_inner_w()

    # Assert
    for xml_id in xml_ids:
        token = doc.main_edition.token_by_xml_id(xml_id)
        assert token.localname == 'w'
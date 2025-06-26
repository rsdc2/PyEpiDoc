"""
These tests relate to the setting of @n ids on edition
elements.
"""

from pathlib import Path

import pytest

from tests.config import EMPTY_TEMPLATE_PATH
from pyepidoc import EpiDoc
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.edition_elements.ab import Ab
from pyepidoc.xml.utils import abify

input_path = Path('tests/workflows/ids_local/files/input')
output_path = Path('tests/workflows/ids_local/files/output')
benchmark_path = Path('tests/workflows/ids_local/files/benchmark')

paths = [
    ('set_n_ids_1.xml', ['5', '10']),
    ('set_n_ids_2.xml', ['5', '10', '15', '20', '25', '30']) 
            # Check that ignore <gap/> element
]

@pytest.mark.parametrize('filename_with_result', paths)
def test_set_local_ids(filename_with_result: tuple[str, list[str]]):

    """
    Check that sets `@n` ids correctly on elements that can receive these
    """

    filename, result = filename_with_result

    doc = EpiDoc(input_path / Path(filename))
    with_local_ids = doc.set_local_ids()

    assert [token.local_id for token in with_local_ids.local_idable_elements] == result
    

test_local_id_elements_main = [
    ('<w n="5">a</w> <w>b</w> <w n="10">c</w>', ['5', '7', '10']),
    ('<w n="5">a</w> <w>b</w> <w>c</w> <w n="20"/>', ['5', '10', '15', '20']),
    ('<w n="5">a</w> <w>b</w> <w>c</w> <w/> <w/> <w n="10"/>', ['5', '6', '7', '8', '9', '10'])
]
@pytest.mark.parametrize(('xml_str', 'expected_local_ids'), test_local_id_elements_main)
def test_set_missing_local_ids_on_main_edition(xml_str: str, expected_local_ids: list[str]):
    # Arrange
    doc = EpiDoc(EMPTY_TEMPLATE_PATH)
    ab = Ab(XmlElement.from_xml_str(abify(xml_str)))
    doc.main_edition.append_ab(ab)

    # Act
    doc.main_edition.set_missing_local_ids()

    # Assert
    assert doc.main_edition.local_ids == expected_local_ids


test_local_id_elements_main_and_simple_lemmatized = [
    '<w n="5">a</w> <w>b</w> <w n="10">c</w>',
    '<w n="5">a</w> <w>b</w> <w>c</w> <w n="20"/>',
    '<w n="5">a</w> <w>b</w> <w>c</w> <w/> <w/> <w n="10"/>'
]
@pytest.mark.parametrize('xml_str', test_local_id_elements_main_and_simple_lemmatized)
def test_set_missing_local_ids_on_main_edition_and_lemmatized_edition(xml_str: str):
    # Arrange
    doc = EpiDoc(EMPTY_TEMPLATE_PATH)
    ab = Ab(XmlElement.from_xml_str(abify(xml_str)))
    doc.main_edition.append_ab(ab)
    doc.lemmatize(lambda s: 'lemma', where='separate')

    # Act
    doc.main_edition.set_missing_local_ids()
    doc.edition_by_subtype('simple-lemmatized').set_missing_local_ids()

    # Assert
    assert doc.main_edition.local_ids == doc.edition_by_subtype('simple-lemmatized').local_ids
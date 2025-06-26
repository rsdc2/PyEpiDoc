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


test_local_id_elements = [
    '<w n="5">a</w> <w>b</w> <w n="6"/>',
    '<w n="5">a</w> <w>b</w> <w/> <w n="7"/>',
]
@pytest.mark.parametrize('xml_str', test_local_id_elements)
def test_set_missing_local_ids(xml_str: str):
    # Arrange
    doc = EpiDoc(EMPTY_TEMPLATE_PATH)
    ab = Ab(XmlElement.from_xml_str(abify(xml_str)))
    doc.main_edition.append_ab(ab)

    # Act
    with pytest.raises(ValueError):
        doc.main_edition.set_missing_local_ids()

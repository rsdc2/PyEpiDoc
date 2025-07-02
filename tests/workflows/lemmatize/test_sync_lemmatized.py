import pytest

from pyepidoc import EpiDoc
from pyepidoc.xml.utils import abify
from pyepidoc.processing.processor import Processor
from pyepidoc.processing.operations import sync_lemmatized
from pyepidoc.epidoc.edition_elements.ab import Ab
from pyepidoc.xml.xml_element import XmlElement

from pyepidoc.epidoc.enums import StandoffEditionElements
from tests.config import EMPTY_TEMPLATE_PATH

test_data = [
    ('<w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [5, 10, 15]),
              
    ('<w n="0">yes</w> <w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [0, 5, 10, 15]),

    ('<w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w> <w n="20">yes</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [5, 10, 15, 20]),
               
    ('<space n="0"/> <w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [0, 5, 10, 15]),

    ('<space n="0"/> <persName/> <w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [0, 5, 10, 15]),

    ('<space n="0"/> <persName><w n="2">b</w></persName> <w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [0, 2, 5, 10, 15]),

    ('<space n="0"/> <w n="5">hello</w> <persName><w n="7">b</w></persName>  <w n="10">world</w> <w n="15">goodbye</w>',
     '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
     [0, 5, 7, 10, 15])
]

@pytest.mark.parametrize(('main_xml', 'lemmatized_xml', 'expected_ids'), test_data)
def test_sync_lemmatized(main_xml: str, lemmatized_xml: str, expected_ids: list[int]):
    # Arrange
    doc = EpiDoc(EMPTY_TEMPLATE_PATH)
    main_ab = Ab(XmlElement.from_xml_str(abify(main_xml)))
    lemmatized_ab = Ab(XmlElement.from_xml_str(abify(lemmatized_xml)))

    if doc.main_edition is None: raise TypeError()
    doc.main_edition.append_ab(main_ab)
    doc.ensure_lemmatized_edition().append_ab(lemmatized_ab)
    assert doc.main_edition.local_ids != doc.ensure_lemmatized_edition().local_ids

    # Act
    synced = Processor(doc).sync_lemmatized_edition().epidoc

    # Assert    
    if synced.main_edition is None: raise TypeError()
    assert synced.ensure_lemmatized_edition().local_ids == [str(id) for id in expected_ids]


test_data = [('<w n="5">hello</w> <w n="10">world</w> <w n="15">goodbye</w>',
              '<w n="5" lemma="lemma">hello</w> <w n="15" lemma="lemma">goodbye</w>',
              ['hello', 'world', 'goodbye'])]
@pytest.mark.parametrize(('main_xml', 'lemmatized_xml', 'expected_tokens'), test_data)
def test_sync_lemmatized_texts(main_xml: str, lemmatized_xml: str, expected_tokens: list[str]):
    # Arrange
    doc = EpiDoc(EMPTY_TEMPLATE_PATH)
    main_ab = Ab(XmlElement.from_xml_str(abify(main_xml)))
    lemmatized_ab = Ab(XmlElement.from_xml_str(abify(lemmatized_xml)))

    if doc.main_edition is None: raise TypeError()
    doc.main_edition.append_ab(main_ab)
    doc.ensure_lemmatized_edition().append_ab(lemmatized_ab)
    
    token_texts = [token.text for token in doc.ensure_lemmatized_edition().w_tokens]
    assert token_texts != expected_tokens

    # Act
    synced = Processor(doc).sync_lemmatized_edition().epidoc

    # Assert    
    if synced.main_edition is None: raise TypeError()
    token_texts = [token.text for token in synced.ensure_lemmatized_edition().w_tokens]
    assert token_texts == expected_tokens

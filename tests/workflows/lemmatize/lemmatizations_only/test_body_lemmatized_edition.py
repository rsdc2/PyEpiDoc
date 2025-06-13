from pyepidoc import EpiDoc
from pyepidoc.shared.file import remove_file
from pyepidoc.shared.testing import save_and_reload

import pytest
from tests.config import FILE_WRITE_MODE

unlemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/unlemmatized/'
lemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/lemmatized/'


def test_create_lemmatized_edition():

    """
    Tests that can create a lemmatized edition
    """
    
    filename = 'lemmatized_edition.xml'
    
    # Create the edition
    doc = EpiDoc(unlemmatized_path + 'single_token.xml')
    doc.body.create_edition('simple-lemmatized')
    doc.prettify('pyepidoc')

    # Save and check that the edition is there
    doc_ = save_and_reload(
        doc, 
        path=lemmatized_path + filename, 
        mode=FILE_WRITE_MODE
    )
    new_edition = doc_.edition_by_subtype('simple-lemmatized')

    assert new_edition is not None


def test_copy_edition_content():
    
    """
    Tests that can copy the elements of an edition 
    to another edition element
    """

    filename = 'lemmatized_edition_with_content_no_lemmas.xml'

    # Get the doc
    doc = EpiDoc(unlemmatized_path + 'single_token.xml')

    # Get the source (main) edition
    source = doc.body.edition_by_subtype(None)
    if source is None:
        raise ValueError('No source edition could be found.')

    target = doc.body.create_edition('simple-lemmatized')

    # Copy the edition content
    doc.body.copy_edition_items_to_appear_in_lemmatized_edition(source, target)

    doc.prettify('pyepidoc')

    # Check edition content copied correctly
    doc_ = save_and_reload(
        doc, 
        path=lemmatized_path + filename,
        mode=FILE_WRITE_MODE
    )
    new_source_edition = doc_.body.edition_by_subtype(None)
    new_target_edition = doc_.body.edition_by_subtype('simple-lemmatized')

    assert new_target_edition is not None
    assert new_source_edition is not None

    assert len(new_target_edition.desc_elems) == 2
    

def test_copy_edition_content_parametrized_no_lemmas():

    filename = 'lemmatized_edition_with_content_parametrized_no_lemmas.xml'

    # Get the doc
    doc = EpiDoc(unlemmatized_path + 'single_token.xml')

    # Get the source (main) edition
    source = doc.body.edition_by_subtype(None)
    if source is None:
        raise ValueError('No source edition could be found.')

    target = doc.body.create_edition('simple-lemmatized')

    # Copy the edition content
    doc.body.copy_edition_items_to_appear_in_lemmatized_edition(source, target)

    doc = doc.prettify('pyepidoc')

    # Check edition content copied correctly
    doc_ = save_and_reload(
        doc, 
        path=lemmatized_path + filename,
        mode=FILE_WRITE_MODE
    )
    new_source_edition = doc_.body.edition_by_subtype(None)
    new_target_edition = doc_.body.edition_by_subtype('simple-lemmatized')

    assert new_target_edition is not None
    assert new_source_edition is not None

    assert len(new_target_edition.desc_elems) == 2
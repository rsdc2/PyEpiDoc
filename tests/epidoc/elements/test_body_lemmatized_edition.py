from pyepidoc import EpiDoc
from pyepidoc.shared.file import remove_file
from pyepidoc.shared.testing import save_and_reload

import pytest

unlemmatized_path = 'epidoc/elements/files/unlemmatized/'
lemmatized_path = 'epidoc/elements/files/lemmatized/'


def test_create_lemmatized_edition():

    """
    Tests that can create a lemmatized edition
    """
    
    filename = 'lemmatized_edition.xml'

    # Remove a pre-existing file
    remove_file(lemmatized_path + filename)
    
    # Create the edition
    doc = EpiDoc(unlemmatized_path + 'unlemmatized.xml')
    doc.body.create_edition('simple-lemmatized')

    # Save and check that the edition is there
    doc_ = save_and_reload(doc, lemmatized_path + filename)
    new_edition = doc_.edition_by_subtype('simple-lemmatized')

    assert new_edition is not None


def test_copy_edition_content():
    
    """
    Tests that can copy the elements of an edition 
    to another edition element
    """

    filename = 'lemmatized_edition_with_content.xml'
    remove_file(lemmatized_path + filename)

    # Get the doc
    doc = EpiDoc(unlemmatized_path + 'unlemmatized.xml')

    # Get the source (main) edition
    source = doc.body.edition_by_subtype(None)
    if source is None:
        raise ValueError('No source edition could be found.')

    target = doc.body.create_edition('simple-lemmatized')

    # Copy the edition content
    doc.body.copy_edition_content(source, target)

    # Check edition content copied correctly
    doc_ = save_and_reload(
        doc, 
        lemmatized_path + filename)
    new_source_edition = doc_.body.edition_by_subtype(None)
    new_target_edition = doc_.body.edition_by_subtype('simple-lemmatized')

    assert new_target_edition is not None
    assert new_source_edition is not None

    assert len(new_source_edition.desc_elems) == \
        len(new_target_edition.desc_elems)
    

tags_to_include_list = [
    ([], 0),
    (['ab', 'w'], 2)
]


@pytest.mark.parametrize(
        "tags_to_include_with_count", 
        tags_to_include_list)
def test_copy_edition_content_parametrized(
    tags_to_include_with_count: tuple[list[str], int]):

    tags_to_include, count = tags_to_include_with_count

    filename = 'lemmatized_edition_with_content_parametrized.xml'
    remove_file(lemmatized_path + filename)

    # Get the doc
    doc = EpiDoc(unlemmatized_path + 'unlemmatized.xml')

    # Get the source (main) edition
    source = doc.body.edition_by_subtype(None)
    if source is None:
        raise ValueError('No source edition could be found.')

    target = doc.body.create_edition('simple-lemmatized')

    # Copy the edition content
    doc.body.copy_edition_content(
        source, 
        target,
        tags_to_include)

    # Check edition content copied correctly
    doc_ = save_and_reload(
        doc, 
        lemmatized_path + filename)
    new_source_edition = doc_.body.edition_by_subtype(None)
    new_target_edition = doc_.body.edition_by_subtype(
        'simple-lemmatized')

    assert new_target_edition is not None
    assert new_source_edition is not None

    assert len(new_target_edition.desc_elems) == count
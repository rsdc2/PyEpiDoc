from pyepidoc import EpiDoc
from pyepidoc.shared.file import remove_file

unlemmatized_path = 'epidoc/elements/files/unlemmatized/'
lemmatized_path = 'epidoc/elements/files/lemmatized/'


def test_create_lemmatized_edition():

    """
    Tests that can create a lemmatized edition
    """
    
    # Remove a pre-existing file
    remove_file(lemmatized_path + 'lemmatized_edition.xml')
    
    # Create the edition
    doc = EpiDoc(unlemmatized_path + 'lemmatize.xml')
    doc.body.create_edition('simple-lemmatized')

    # Save and check that the edition is there
    doc.to_xml_file(lemmatized_path + 'lemmatized_edition.xml')
    doc_ = EpiDoc(lemmatized_path + 'lemmatized_edition.xml')
    new_edition = doc_.edition_by_subtype('simple-lemmatized')

    assert new_edition is not None


def test_copy_edition_content():
    
    """
    Tests that can copy the elements of an edition 
    to another edition element
    """
    remove_file(lemmatized_path + 'lemmatized.xml')

    # Get the doc
    doc = EpiDoc(unlemmatized_path + 'lemmatize.xml')

    # Get the source (main) edition
    source = doc.body.edition_by_subtype(None)
    if source is None:
        raise ValueError('No source edition could be found')

    target = doc.body.create_edition('simple-lemmatized')

    # Copy the edition content
    doc.body.copy_edition_content(source, target)

    # Check edition content copied correctly
    doc.to_xml_file(lemmatized_path + 'lemmatized_edition_with_content.xml')
    doc_ = EpiDoc(lemmatized_path + 'lemmatized_edition_with_content.xml')
    new_source_edition = doc_.body.edition_by_subtype(None)
    new_target_edition = doc_.body.edition_by_subtype('simple-lemmatized')

    assert new_target_edition is not None
    assert new_source_edition is not None

    assert len(new_source_edition.desc_elems) == \
        len(new_target_edition.desc_elems)
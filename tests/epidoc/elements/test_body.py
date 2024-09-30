from pyepidoc import EpiDoc



def test_create_lemmatized_edition():

    path = 'epidoc/elements/files/unlemmatized/'

    doc = EpiDoc(path + 'lemmatize.xml')

    doc.body.add_edition('simple-lemmatized')

    doc.to_xml_file(path + 'lemmatized_edition.xml')

    doc_ = EpiDoc(path + 'lemmatized_edition.xml')

    new_edition = doc_.edition_by_subtype('simple-lemmatized')

    assert new_edition is not None
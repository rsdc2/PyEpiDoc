from pyepidoc import EpiDoc
from pyepidoc.shared.file import remove_file
from pyepidoc.shared.testing import save_and_reload

import pytest
from tests.config import FILE_WRITE_MODE

@pytest.mark.parametrize(
        "filename", 
        map(lambda filename_with_tag_counts: filename_with_tag_counts[0], filenames_with_tag_counts))
def test_lemmatize_on_separate_edition_creates_resp_stmt(filename: str):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document with a <respStmt> puts the 
    <respStmt> on the document
    """
    # Arrange
    doc = EpiDoc(unlemmatized_path + filename)
    resp_stmt = RespStmt.from_details(
        name='Joe Bloggs',
        initials='JB',
        ref='xyz',
        resp_text='Lemmatization'
    )

    # Act
    doc.lemmatize(dummy_lemmatizer, 'separate', resp_stmt=resp_stmt)
    doc.prettify()
    doc_ = save_and_reload(
        doc, 
        lemmatized_with_resp_path + filename, 
        mode=FILE_WRITE_MODE
    )

    # Assert
    if doc_.title_stmt is None: 
        assert False
    last_resp_stmt = doc_.title_stmt.resp_stmts[-1]
    assert last_resp_stmt == resp_stmt


@pytest.mark.parametrize(
        "filename", 
        map(lambda filename_with_tag_counts: filename_with_tag_counts[0], filenames_with_tag_counts))
def test_lemmatize_on_separate_edition_has_resp_attribute(filename: str):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document with a <respStmt> puts the 
    <respStmt> on the document
    """
    # Arrange
    doc = EpiDoc(unlemmatized_path + filename)
    resp_stmt = RespStmt.from_details(
        name='Joe Bloggs',
        initials='JB',
        ref='xyz',
        resp_text='Lemmatization'
    )

    # Act
    doc.lemmatize(dummy_lemmatizer, 'separate', resp_stmt=resp_stmt)
    doc.prettify()
    doc_ = save_and_reload(
        doc, 
        lemmatized_with_resp_path + filename, 
        mode=FILE_WRITE_MODE
    )

    # Assert
    if doc_.simple_lemmatized_edition is None: 
        assert False
    assert doc_.simple_lemmatized_edition.resp == '#JB'

from typing import Callable

import pytest

from pyepidoc import EpiDoc
from pyepidoc.epidoc.metadata.resp_stmt import RespStmt
from pyepidoc.shared.testing import (
    save_and_reload, 
    save_reload_and_compare_with_benchmark
)

from pyepidoc.shared.constants import SEPARATE_LEMMATIZED_ITEMS
from tests.config import FILE_WRITE_MODE

unlemmatized_path = 'tests/workflows/lemmatize/lemmatizations_with_metadata/files/unlemmatized/'
lemmatized_with_resp_path = 'tests/workflows/lemmatize/lemmatizations_with_metadata/files/lemmatized_with_resp/'
benchmark_path = 'tests/workflows/lemmatize/lemmatizations_with_metadata/files/benchmark/'

dummy_lemmatizer: Callable[[str], str] = lambda form: 'lemma'


filenames = [
    'single_token.xml',
    'ISic000001.xml',
    'gap_and_orig.xml',
    'textpart_fragment_physical.xml',
    'persName.xml'
] 

@pytest.mark.parametrize("filename", filenames)
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


@pytest.mark.parametrize("filename", filenames)
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

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

unlemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/unlemmatized/'
lemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/lemmatized/'
lemmatized_with_resp_path = 'tests/workflows/lemmatize/lemmatizations_only/files/lemmatized_with_resp/'
benchmark_path = 'tests/workflows/lemmatize/lemmatizations_only/files/benchmark/'

dummy_lemmatizer: Callable[[str], str] = lambda form: 'lemma'


filenames_with_tag_counts = [
    ('single_token.xml', {'w': 1, 'orig': 0, 'gap': 0}),
    ('ISic000001.xml', {'w': 6, 'orig': 0, 'gap': 0}),
    ('gap_and_orig.xml', {'w': 2, 'orig': 1, 'gap': 1}),
    ('textpart_fragment_physical.xml', {'w': 0, 'gap': 4, 'orig': 2}),
    ('persName.xml', {'w': 2, 'gap': 0, 'orig': 0})
] 

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

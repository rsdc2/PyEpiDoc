from typing import Callable

import pytest

from pyepidoc import EpiDoc
from pyepidoc.tei.metadata.change import Change
from pyepidoc.shared.testing import (
    save_and_reload, 
    save_reload_and_compare_with_benchmark
)

from tests.config import FILE_WRITE_MODE

unlemmatized_path = 'tests/workflows/lemmatize/lemmatizations_with_metadata/files/unlemmatized/'
lemmatized_with_change_path = 'tests/workflows/lemmatize/lemmatizations_with_metadata/files/lemmatized_with_change/'
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
def test_lemmatize_on_separate_edition_creates_change_stmt(filename: str):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document with a <respStmt> puts the 
    <respStmt> on the document
    """
    # Arrange
    doc = EpiDoc(unlemmatized_path + filename)
    change = Change.from_details("2025-06-12", "#JB", "Joe Bloggs lemmatized the text")

    # Act
    doc.lemmatize(dummy_lemmatizer, 'separate', change=change)
    doc.prettify()
    doc_ = save_and_reload(
        doc, 
        lemmatized_with_change_path + filename, 
        mode=FILE_WRITE_MODE
    )

    # Assert
    last_change = doc_.ensure_tei_header().ensure_revision_desc().list_change.changes[-1]
    assert last_change == change


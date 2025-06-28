from typing import Callable

import pytest

from pyepidoc import EpiDoc
from pyepidoc.epidoc.metadata.resp_stmt import RespStmt
from pyepidoc.shared.testing import (
    save_and_reload, 
    save_reload_and_compare_with_benchmark
)
from pyepidoc.processing.processor import Processor

from pyepidoc.epidoc.enums import StandoffEditionElements
from tests.config import FILE_WRITE_MODE

unlemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/unlemmatized/'
lemmatized_path = 'tests/workflows/lemmatize/lemmatizations_only/files/lemmatized/'
lemmatized_with_resp_path = 'tests/workflows/lemmatize/lemmatizations_only/files/lemmatized_with_resp/'
benchmark_path = 'tests/workflows/lemmatize/lemmatizations_only/files/benchmark/'

dummy_lemmatizer: Callable[[str], str] = lambda form: 'lemma'


def test_lemmatize_on_main_edition():
    
    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document puts lemmata on the main 
    <div type="edition"/> element.
    """

    # Arrange
    filename = 'lemmatized_main_edition_with_dummy.xml'

    doc = EpiDoc(unlemmatized_path + 'single_token.xml')
    proc = Processor(doc)

    # Act
    lemmatized = proc.lemmatize(dummy_lemmatizer, 'main').epidoc

    doc_ = save_and_reload(
        lemmatized, 
        path=lemmatized_path + filename, 
        mode=FILE_WRITE_MODE
    )
    edition_ = doc_.body.edition_by_subtype(None)

    # Assert
    assert edition_ is not None
    assert edition_.w_tokens[0].lemma == 'lemma'


filenames_with_tag_counts = [
    ('single_token.xml', {'w': 1, 'orig': 0, 'gap': 0}),
    ('ISic000001.xml', {'w': 6, 'orig': 0, 'gap': 0}),
    ('gap_and_orig.xml', {'w': 2, 'orig': 1, 'gap': 1}),
    ('textpart_fragment_physical.xml', {'w': 0, 'gap': 4, 'orig': 2}),
    ('persName.xml', {'w': 2, 'gap': 0, 'orig': 0})
] 
@pytest.mark.parametrize(
        "filename_with_tag_counts", 
        filenames_with_tag_counts)
def test_lemmatize_on_separate_edition(
    filename_with_tag_counts: tuple[str, dict[str, int]]
):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document produces a separate
    <div type="edition"/> element, and that the
    correct elements are copied across (i.e. only
    <w>, <orig> and <gap>).
    """
    # Arrange
    filename, tag_counts = filename_with_tag_counts
    doc = EpiDoc(unlemmatized_path + filename)

    # Act
    doc.lemmatize(dummy_lemmatizer, 'separate')
    lemmatized_ed = doc.body.edition_by_subtype('simple-lemmatized')

    # Assert
    assert lemmatized_ed is not None
    if len(lemmatized_ed.w_tokens) != 0:
        assert lemmatized_ed.w_tokens[0].lemma == 'lemma'

    assert len(lemmatized_ed.descendant_elements_by_local_name('w')) \
        == tag_counts['w']
    assert len(lemmatized_ed.descendant_elements_by_local_name('orig')) \
        ==  tag_counts['orig']
    assert len(lemmatized_ed.descendant_elements_by_local_name('gap')) \
        == tag_counts['gap']
    
    # Check that only those elements have been copied across
    assert lemmatized_ed.descendant_element_name_set - \
        set(StandoffEditionElements) == set()


@pytest.mark.parametrize(
        "filename_with_tag_counts", 
        filenames_with_tag_counts)
def test_lemmatize_on_separate_edition_compare_file(
    filename_with_tag_counts: tuple[str, dict[str, int]]
):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document produces a separate
    <div type="edition"/> element, and that the
    correct elements are copied across (i.e. only
    <w>, <orig> and <gap>).
    """
    # Arrange
    filename, _ = filename_with_tag_counts
    doc = EpiDoc(unlemmatized_path + filename)

    # Act
    doc.lemmatize(dummy_lemmatizer, 'separate')

    # Assert    
    assert save_reload_and_compare_with_benchmark(
        doc, 
        lemmatized_path + filename, 
        benchmark_path + filename,
        FILE_WRITE_MODE
    )



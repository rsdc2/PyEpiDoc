from typing import Callable

import pytest

from pyepidoc import EpiDoc
from pyepidoc.shared.file import remove_file 
from pyepidoc.shared.testing import save_and_reload

unlemmatized_path = 'tests/workflows/lemmatize/files/unlemmatized/'
lemmatized_path = 'tests/workflows/lemmatize/files/lemmatized/'


dummy_lemmatizer: Callable[[str], str] = lambda form: 'lemma'


def test_lemmatize_on_main_edition():
    
    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document puts lemmata on the main 
    <div type="edition"/> element.
    """

    filename = 'lemmatized_main_edition_with_dummy.xml'
    remove_file(lemmatized_path + filename)

    doc = EpiDoc(unlemmatized_path + 'unlemmatized_single_token.xml')
    doc.lemmatize(dummy_lemmatizer, 'main')

    # Check correct
    doc_ = save_and_reload(doc, lemmatized_path + filename)
    edition_ = doc_.body.edition_by_subtype(None)

    assert edition_ is not None
    assert edition_.w_tokens[0].lemma == 'lemma'


filenames_with_tag_counts = [
    ('unlemmatized_single_token.xml', {'w': 1, 'orig': 0, 'gap': 0}),
    ('unlemmatized_full.xml', {'w': 6, 'orig': 0, 'gap': 0}),
    ('unlemmatized_with_gap_and_orig.xml', {'w': 2, 'orig': 1, 'gap': 1})
] 


@pytest.mark.parametrize(
        "filename_with_tag_names", 
        filenames_with_tag_counts)
def test_lemmatize_on_separate_edition(
    filename_with_tag_names: tuple[str, dict[str, int]]
):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document produces a separate
    <div type="edition"/> element, and that the
    correct elements are copied across (i.e. only
    <w>, <orig> and <gap>).
    """

    filename, tag_counts = filename_with_tag_names


    remove_file(lemmatized_path + filename)

    doc = EpiDoc(unlemmatized_path + filename)
    doc.lemmatize(dummy_lemmatizer, 'separate')
    doc.to_xml_file(lemmatized_path + filename)

    # Check correct
    doc_ = save_and_reload(doc, lemmatized_path + filename)
    lemmatized_ed = doc_.body.edition_by_subtype('simple-lemmatized')

    assert lemmatized_ed is not None
    assert lemmatized_ed.w_tokens[0].lemma == 'lemma'
    # breakpoint()
    assert len(lemmatized_ed.desc_elems_by_local_name('w')) == tag_counts['w']
    assert len(lemmatized_ed.desc_elems_by_local_name('orig')) == tag_counts['orig']
    assert len(lemmatized_ed.desc_elems_by_local_name('gap')) == tag_counts['gap']
    
    # Check that only those elements have been copied across
    assert lemmatized_ed.desc_elem_name_set - {'w', 'orig', 'gap', 'ab'} == set()



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
    on an EpiDoc document produces a lemmatized version
    on the main edition.
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


unlemmatized_filenames = [
    'unlemmatized_single_token.xml',
    'unlemmatized_full.xml'] 

@pytest.mark.parametrize(
        "unlemmatized_filename", 
        unlemmatized_filenames)
def test_lemmatize_on_separate_edition(
    unlemmatized_filename: str
):

    """
    Test that calling the `lemmatize` method 
    on an EpiDoc document produces a lemmatized version
    on a separate edition.
    """
    
    filename = 'lemmatized_separate_edition_with_dummy.xml'
    remove_file(lemmatized_path + filename)

    doc = EpiDoc(unlemmatized_path + unlemmatized_filename)
    doc.lemmatize(dummy_lemmatizer, 'separate')
    doc.to_xml_file(lemmatized_path + filename)

    # Check correct
    doc_ = save_and_reload(doc, lemmatized_path + filename)
    edition_ = doc_.body.edition_by_subtype('simple-lemmatized')

    assert edition_ is not None
    assert edition_.w_tokens[0].lemma == 'lemma'


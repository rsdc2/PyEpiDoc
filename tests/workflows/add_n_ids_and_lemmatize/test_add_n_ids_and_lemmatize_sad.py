"""
Testing the workflow:
    - add @n ids to all <w> and <orig> elements
    - create a simple lemmatized <div>
"""
from pathlib import Path
import pytest
from pyepidoc import EpiDoc

from .paths import *


def test_add_n_ids_and_lemmatize():

    """
    Check that raise an error if an element already has
    a @n attribute
    """

    with pytest.raises(AttributeError):
        doc = EpiDoc(INPUT / Path('ISic000001_sad.xml'))

        doc.set_n_ids()
        doc.lemmatize(lambda _: 'lemma', where = 'separate')

        doc.to_xml_file(OUTPUT / Path('ISic000001_sad.xml'))
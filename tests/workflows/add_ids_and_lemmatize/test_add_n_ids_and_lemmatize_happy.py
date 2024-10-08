"""
Testing the workflow:
    - add @n ids to all <w> and <orig> elements
    - create a simple lemmatized <div>
"""
from pathlib import Path
from pyepidoc import EpiDoc
from .paths import *


def test_add_n_ids_and_lemmatize():

    doc = EpiDoc(INPUT / Path('ISic000001_happy.xml'))

    doc.set_n_ids()
    doc.lemmatize(lambda _: 'lemma', where = 'separate')

    doc.to_xml_file(OUTPUT / Path('ISic000001_happy.xml'))

    # Need to add test here
    assert False
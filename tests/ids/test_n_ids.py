"""
These tests relate to the setting of @n ids on edition
elements.
"""

from pathlib import Path

from pyepidoc import EpiDoc

input_path = Path('ids/files/input')
output_path = Path('ids/files/output')
benchmark_path = Path('ids/files/benchmark')


def test_set_n_ids():
    doc = EpiDoc(input_path / Path('set_n_ids_1.xml'))
    with_n_ids = doc.set_n_ids()
    with_n_ids.to_xml_file(output_path / Path('set_n_ids_1.xml'))
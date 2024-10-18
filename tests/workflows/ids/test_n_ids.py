"""
These tests relate to the setting of @n ids on edition
elements.
"""

from pathlib import Path

from pyepidoc import EpiDoc

input_path = Path('tests/workflows/ids/files/input')
output_path = Path('tests/workflows/ids/files/output')
benchmark_path = Path('tests/workflows/ids/files/benchmark')


def test_set_n_ids():
    doc = EpiDoc(input_path / Path('set_n_ids_1.xml'))
    with_n_ids = doc.set_n_ids()
    with_n_ids.to_xml_file(output_path / Path('set_n_ids_1.xml'))

    assert [token.get_attrib('n') for token in with_n_ids.w_tokens] == ['5', '10']
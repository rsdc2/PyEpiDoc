"""
These tests relate to the setting of @n ids on edition
elements.
"""

from pathlib import Path

import pytest

from pyepidoc import EpiDoc

input_path = Path('tests/workflows/ids_local/files/input')
output_path = Path('tests/workflows/ids_local/files/output')
benchmark_path = Path('tests/workflows/ids_local/files/benchmark')

paths = [
    ('set_n_ids_1.xml', ['5', '10']),
    ('set_n_ids_2.xml', ['5', '10', '15', '20', '25', '30']) 
            # Check that ignore <gap/> element
]

@pytest.mark.parametrize('filename_with_result', paths)
def test_set_n_ids(filename_with_result: tuple[str, list[str]]):

    """
    Check that sets `@n` ids correctly on elements that can receive these
    """

    filename, result = filename_with_result

    doc = EpiDoc(input_path / Path(filename))
    with_n_ids = doc.set_n_ids()

    assert [token.get_attrib('n') 
            for token in with_n_ids.n_id_elements] == result
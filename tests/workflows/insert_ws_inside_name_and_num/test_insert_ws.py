"""
These tests relate to the setting of @n ids on edition
elements.
"""

from pathlib import Path
import pytest
from pyepidoc import EpiDoc
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark
from ...config import FILE_WRITE_MODE

input_path = Path('tests/workflows/insert_ws_inside_name_and_num/files/input')
output_path = Path('tests/workflows/insert_ws_inside_name_and_num/files/output')
benchmark_path = Path('tests/workflows/insert_ws_inside_name_and_num/files/benchmark')

paths = [
    'insert_ws_1.xml',
    'insert_ws_2.xml'
]

@pytest.mark.parametrize('filename', paths)
def test_insert_ws(filename: str):

    """
    Check that inserts <w> into <name> and <num> tags correctly
    """

    doc = EpiDoc(input_path / Path(filename))

    if doc.main_edition is None:
        raise ValueError('No main edition.')
    
    doc.main_edition.insert_ws_inside_named_entities()

    assert save_reload_and_compare_with_benchmark(
        doc, 
        output_path / Path(filename), 
        benchmark_path / Path(filename), 
        output_write_mode = FILE_WRITE_MODE) == True


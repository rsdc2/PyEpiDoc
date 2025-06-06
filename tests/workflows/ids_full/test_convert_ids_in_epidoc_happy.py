"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pathlib import Path
from pyepidoc import EpiDoc
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark, save_and_reload
from tests.config import FILE_WRITE_MODE

make_path = lambda s: Path(s + '.xml') 

tests = map(make_path, [
    'convert_ids_1',
    'convert_ids_2'
])

input_path = Path('tests/workflows/ids_full/files/input')
output_path = Path('tests/workflows/ids_full/files/output')
benchmark_path = Path('tests/workflows/ids_full/files/benchmark')


@pytest.mark.parametrize('filename', tests)
def test_convert_ids_in_epidoc(filename: Path):
    
    # Arrange
    doc = EpiDoc(input_path / filename)
    benchmark = EpiDoc(benchmark_path / filename)

    # Act
    doc.convert_ids(52, 100)
    output = save_and_reload(doc, output_path / filename, FILE_WRITE_MODE)

    # Assert
    # Check the ids
    assert output.ids == benchmark.ids
    assert output.ids != []    

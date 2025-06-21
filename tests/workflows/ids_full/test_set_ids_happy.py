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
    'set_ids_1', 
    'ISic001470'
])

input_path = Path('tests/workflows/ids_full/files/input')
output_path = Path('tests/workflows/ids_full/files/output')
benchmark_path = Path('tests/workflows/ids_full/files/benchmark')


@pytest.mark.parametrize('filename', tests)
def test_set_ids_in_epidoc(filename: Path):
    # Arrange
    # Set the IDs
    doc = EpiDoc(input_path / filename)

    # Act
    doc.set_ids(base=100)

    # Act
    # Output to a new XML file
    output = save_and_reload(doc, output_path / filename, FILE_WRITE_MODE)
    benchmark = EpiDoc(benchmark_path / filename)

    # Assert
    # Check the ids
    assert output.xml_ids == benchmark.xml_ids
    assert output.xml_ids != []
    

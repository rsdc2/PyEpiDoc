"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pathlib import Path
from pyepidoc import EpiDoc

make_path = lambda s: Path(s + '.xml') 

tests = map(make_path, [
    'set_ids_1', 
    'ISic001470'
])

input_path = Path('tests/workflows/ids/files/input')
output_path = Path('tests/workflows/ids/files/output')
benchmark_path = Path('tests/workflows/ids/files/benchmark')


@pytest.mark.parametrize('filename', tests)
def test_set_ids_in_epidoc(filename: Path):
    # Set the IDs
    doc = EpiDoc(input_path / filename)
    doc.set_ids(base=100)
    doc.to_xml_file(output_path / filename)

    # Output to a new XML file
    output = EpiDoc(output_path / filename)
    benchmark = EpiDoc(benchmark_path / filename)

    # Check the ids
    assert output.ids == benchmark.ids
    assert output.ids != []
    

"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pathlib import Path
from pyepidoc import EpiDoc

make_path = lambda s: Path(s + '.xml') 

tests = map(make_path, [
    'convert_ids_1',
    'convert_ids_2'
])

input_path = Path('tests/ids/files/input')
output_path = Path('tests/ids/files/output')
benchmark_path = Path('tests/ids/files/benchmark')


@pytest.mark.parametrize('filename', tests)
def test_convert_ids_in_epidoc(filename: Path):
    # Convert the IDs
    doc = EpiDoc(input_path / filename)
    doc.convert_ids(52, 100)
    doc.to_xml_file(output_path / filename)

    # Output to a new XML file
    output = EpiDoc(output_path / filename)
    benchmark = EpiDoc(benchmark_path / filename)

    # Check the ids
    assert output.ids == benchmark.ids
    assert output.ids != []
    
    # Do the tests    
    

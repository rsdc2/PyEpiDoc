"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pathlib import Path
from pyepidoc import EpiDoc

make_path = lambda s: Path(s + '.xml') 

tests = map(make_path, [
    'convert_ids_1'
])

input_path = Path('ids/files/input')
output_path = Path('ids/files/output')
benchmark_path = Path('ids/files/benchmark')


@pytest.mark.parametrize('file', tests)
def test_convert_ids_in_epidoc(file: Path):
    # Convert the IDs
    doc = EpiDoc(input_path / file)

    # Do the tests    
    

"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pathlib import Path
from pyepidoc import EpiDoc
from pyepidoc.epidoc.ids.errors import *

make_path = lambda s: Path(s + '.xml') 

tests = map(make_path, [
    'convert_ids_3'
])

input_path = Path('ids/files/input')
output_path = Path('ids/files/output')
benchmark_path = Path('ids/files/benchmark')


@pytest.mark.parametrize('filename', tests)
def test_convert_ids_in_epidoc(filename: Path):
    # Attempt to convert the IDs
    doc = EpiDoc(input_path / filename)

    with pytest.raises(ConversionError):
        doc.convert_ids(100, 52)

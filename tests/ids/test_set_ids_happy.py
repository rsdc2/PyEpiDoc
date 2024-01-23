"""
Tests for converting ids in EpiDoc files
"""

import pytest
from pathlib import Path
from pyepidoc import EpiDoc

make_path = lambda s: Path(s + '.xml') 

tests = map(make_path, [
    'set_ids_1'
])

input_path = Path('ids/files/input')
output_path = Path('ids/files/output')
benchmark_path = Path('ids/files/benchmark')


@pytest.mark.parametrize('filename', tests)
def test_set_ids_in_epidoc(filename: Path):
    # Convert the IDs
    doc = EpiDoc(input_path / filename)
    doc.set_ids(base=100)
    doc.to_xml_file(output_path / filename)

    # Output to a new XML file
    output = EpiDoc(output_path / filename).editions()[0].abs[0]
    benchmark = EpiDoc(benchmark_path / filename).editions()[0].abs[0]

    output_elem_ids = [elem.id_xml for elem in output.desc_elems]
    benchmark_elem_ids = [elem.id_xml for elem in benchmark.desc_elems]

    assert output_elem_ids == benchmark_elem_ids
    

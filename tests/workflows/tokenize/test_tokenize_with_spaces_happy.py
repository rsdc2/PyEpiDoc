import pytest
from pathlib import Path
from lxml import etree

from ...config import FILE_WRITE_MODE

from pyepidoc.shared.file import remove_file
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark
from pyepidoc.epidoc.scripts import tokenize, tokenize_to_file_object
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.epidoc.elements.ab import Ab
from pyepidoc.xml.utils import abify


input_path = Path('tests/workflows/tokenize/files/untokenized')
output_path = Path('tests/workflows/tokenize/files/tokenized_output')
benchmark_path = Path('tests/workflows/tokenize/files/tokenized_benchmark')


xml_to_tokenize = [
     (
         '<gap reason="lost" extent="unknown" unit="character"/> <g ref="#interpunct">·</g>',
         '<gap reason="lost" extent="unknown" unit="character"/> <g ref="#interpunct">·</g>'
     ),
     (
         '<unclear><g ref="#ivy-leaf">❦</g></unclear> <num value="17">XVII</num>',
         '<unclear><g ref="#ivy-leaf">❦</g></unclear> <num value="17">XVII</num>'
     ),
     (
         '<supplied reason="undefined" evidence="previouseditor"><g ref="#interpunct">·</g></supplied> <num value="40"><w n="40">μ</w></num>',
         '<supplied reason="undefined" evidence="previouseditor"><g ref="#interpunct">·</g></supplied> <num value="40"><w n="40">μ</w></num>'
     )
]


@pytest.mark.parametrize("xml_pair", xml_to_tokenize)
def test_tokenize_epidoc_fragments_with_spaces(xml_pair: tuple[str, str]):
    
    # Arrange
    xml_pair_abs = tuple(map(abify, xml_pair))

    xml, tokenized_xml = xml_pair_abs
    untokenized = Ab(etree.fromstring(xml, None))
    tokenized_benchmark = Ab(etree.fromstring(tokenized_xml, None))

    # Act
    tokenized = untokenized.tokenize()

    if tokenized is None:
        return False

    tokenized.space_tokens()    
    benchmark_strs = [etree.tostring(t.e)
                      for t in tokenized_benchmark.tokens]
    
    tokenized_strs = [etree.tostring(t.e) 
                      for t in tokenized.tokens]
    
    benchmark_bstr: bytes = etree.tostring(tokenized_benchmark.e)
    benchmark_str = benchmark_bstr.decode()

    tokenized_bstr: bytes = etree.tostring(tokenized.e)
    tokenized_str = tokenized_bstr.decode()

    result = tokenized_str == benchmark_str
    
    if not result:
        # breakpoint()
        pass

    # Assert
    assert tokenized_str == benchmark_str
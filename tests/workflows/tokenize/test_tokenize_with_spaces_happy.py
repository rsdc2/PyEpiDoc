import pytest
from pathlib import Path
from lxml import etree

from ...config import FILE_WRITE_MODE

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
     ),
     (
         '<w><unclear>abc</unclear> <unclear/></w>',
         '<w><unclear>abc</unclear><unclear/></w>'
     ),
     (
         '<w n="25">vix<unclear>i</unclear> <supplied reason="lost">t</supplied></w>',
         '<w n="25">vix<unclear>i</unclear><supplied reason="lost">t</supplied></w>'
     ),
     (
         '<orig n="25">Δ</orig> <g ref="#interpunct" n="30">·</g>',
         '<orig n="25">Δ</orig><g ref="#interpunct" n="30">·</g>'
     ),
     (
         '<orig n="25">Δ</orig><g ref="#interpunct" n="30">·</g>',
         '<orig n="25">Δ</orig><g ref="#interpunct" n="30">·</g>'
     ),
     (
         '<w>annis</w> <unclear><g>xyz</g></unclear>',
         '<w>annis</w> <unclear><g>xyz</g></unclear>'
     ),
     (
         '<space unit="character" quantity="1"/>',
         '<space unit="character" quantity="1"/>'
     ),
     (
         '<space unit="character" quantity="1"/> xyz',
         '<space unit="character" quantity="1"/> <w>xyz</w>'
     ),
     (
         'xyz <space unit="character" quantity="1"/>',
         '<w>xyz</w> <space unit="character" quantity="1"/>'
     ),
     (
         'xyz abc <space unit="character" quantity="1"/>',
         '<w>xyz</w> <w>abc</w> <space unit="character" quantity="1"/>'
     ),
     (
         '<w>xyz</w> <space unit="character" quantity="1"/>',
         '<w>xyz</w> <space unit="character" quantity="1"/>'
     ),
     (
         '<g>.</g> <space unit="character" quantity="1"/> xyz',
         '<g>.</g> <space unit="character" quantity="1"/> <w>xyz</w>'
     )
    #  (
    #      '<w>annis</w><unclear><g>xyz</g></unclear>',
    #      '<w>annis</w> <unclear><g>xyz</g></unclear>'
    #  )

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
                      for t in tokenized.get_child_tokens()]
    
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
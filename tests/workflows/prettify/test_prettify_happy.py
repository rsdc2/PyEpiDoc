from __future__ import annotations

from lxml import etree
from pathlib import Path

from pyepidoc.epidoc.enums import *
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc.epidoc.elements.edition import Edition
from pyepidoc.epidoc.elements.edition import Ab
from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.shared import head
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark
from pyepidoc.epidoc.dom import lang, line

from pyepidoc.xml.utils import abify, editionify

from ...config import FILE_WRITE_MODE

import pytest

test_files_path = "tests/api/files/"

    # 'benchmark_lxml': 'tests/api/files/prettifying/benchmark/ISic000552_prettified_lxml.xml',
    # 'benchmark_pyepidoc': 'tests/api/files/prettifying/benchmark/ISic000552_prettified_pyepidoc.xml',
    # 'prettified_lxml': 'tests/api/files/prettifying/prettified/ISic000552_prettified_lxml.xml',
    # 'prettified_pyepidoc': 'tests/api/files/prettifying/prettified/ISic000552_prettified_pyepidoc.xml',

# def test_prettify_doc_with_lxml():
#     """
#     Tests that the entire document is prettified correctly
#     using lxml's inbuilt prettifier.
#     Prettifies both the main document and the editions.
#     """

#     ugly = EpiDoc(relative_filepaths['ugly'])
#     prettified = ugly.prettify('lxml')
#     prettified.to_xml_file(relative_filepaths['prettified_lxml'])
#     prettified_str = etree.tostring(prettified._e)

#     benchmark = EpiDoc(relative_filepaths['benchmark_lxml'])
#     benchmark_str = etree.tostring(benchmark._e)

#     assert prettified_str == benchmark_str


prettify_pyepidoc_paths = [
    (
        'tests/workflows/prettify/files/ugly/ISic000552.xml',
        'tests/workflows/prettify/files/prettified/ISic000552_prettified_pyepidoc.xml',
        'tests/workflows/prettify/files/benchmark/ISic000552_prettified_pyepidoc.xml'
    ),
    (
        'tests/workflows/prettify/files/ugly/ISic000002.xml',
        'tests/workflows/prettify/files/prettified/ISic000002_prettified_pyepidoc.xml',
        'tests/workflows/prettify/files/benchmark/ISic000002_prettified_pyepidoc.xml'
    )

]
@pytest.mark.parametrize(("ugly", "prettified", "benchmark"), prettify_pyepidoc_paths)
def test_prettify_doc_with_pyepidoc(ugly: str, prettified: str, benchmark: str):

    """
    Tests that the entire document is prettified correctly
    using pyepidoc's prettifier.
    Prettifies both the main document and the editions.
    """

    ugly_doc = EpiDoc(ugly)
    prettified_doc = ugly_doc.prettify('pyepidoc')

    assert save_reload_and_compare_with_benchmark(
        doc=prettified_doc,
        target_path=prettified,
        benchmark_path=benchmark,
        output_write_mode=FILE_WRITE_MODE
    )


fragments = [
    (
        '<x><provenance>xyz<geo cert="medium">37.509637, 15.088925</geo></provenance></x>',
        '<x>\n    <provenance>xyz<geo cert="medium">37.509637, 15.088925</geo></provenance>\n</x>',
        'Test that child nodes of <provenance> are not prettified',
    ),
    (
        ('<dimensions><!-- from ILPalermo --><height unit="cm">19</height></dimensions>'),
        ('<dimensions><!-- from ILPalermo -->\n'
         '    <height unit="cm">19</height>\n'
         '</dimensions>'),
         'Test that comments are not put on a new line'
    ),
    (
        ('<handNote><!--ILPalermo--><locus from="line1" to="line1">Line 1</locus></handNote>'),
        ('<handNote><!--ILPalermo-->\n    <locus from="line1" to="line1">Line 1</locus>\n</handNote>'),
         'Test that comments are not put on a new line'
    ),
    (
        ('<handNote><!--ILPalermo--></handNote>'),
        ('<handNote><!--ILPalermo--></handNote>'),
         'Test that an element whose children are only comments is ignored for prettifying'
    ),
    (
        ('<handNote><!--ILPalermo--><!--ILPalermo--></handNote>'),
        ('<handNote><!--ILPalermo--><!--ILPalermo--></handNote>'),
         'Test that an element whose children are only comments is ignored for prettifying'
    )

]
@pytest.mark.parametrize(("ugly", "benchmark", "_"), fragments)
def test_prettify_fragment(ugly: str, benchmark: str, _: str):

    """
    Tests that fragments of xml are prettified correctly
    """

    # Arrange
    ugly_xml = BaseElement(etree.fromstring(ugly.strip()))
    benchmark_xml = BaseElement(etree.fromstring(benchmark.strip()))

    # Act
    prettified = ugly_xml.prettify_element_with_pyepidoc(' ', 4, DoNotPrettifyChildren.values())

    # Assert
    assert benchmark_xml.xml_byte_str.strip() == prettified.xml_byte_str.strip()
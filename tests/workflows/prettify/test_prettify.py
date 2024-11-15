from lxml import etree
from pyepidoc import EpiDoc
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark


relative_filepaths = {
    'ugly': 'tests/workflows/prettify/input/ISic000552.xml',
    'benchmark_lxml': 'tests/workflows/prettify/benchmark/ISic000552_prettified_lxml.xml',
    'benchmark_pyepidoc': 'tests/workflows/prettify/benchmark/ISic000552_prettified_pyepidoc.xml',
    'prettified_lxml': 'tests/workflows/prettify/output/ISic000552_prettified_lxml.xml',
    'prettified_pyepidoc': 'tests/workflows/prettify/output/ISic000552_prettified_pyepidoc.xml',
}


def test_prettify_doc_with_lxml():
    """
    Tests that the entire document is prettified correctly
    using lxml's inbuilt prettifier.
    Prettifies both the main document and the editions.
    """

    ugly = EpiDoc(relative_filepaths['ugly'])
    prettified = ugly.prettify('lxml')
    prettified.to_xml_file(relative_filepaths['prettified_lxml'])
    prettified_str = etree.tostring(prettified._e)

    benchmark = EpiDoc(relative_filepaths['benchmark_lxml'])
    benchmark_str = etree.tostring(benchmark._e)

    assert prettified_str == benchmark_str


def test_prettify_doc_with_pyepidoc():

    """
    Tests that the entire document is prettified correctly
    using pyepidoc's prettifier.
    Prettifies both the main document and the editions.
    """

    ugly = EpiDoc(relative_filepaths['ugly'])
    prettified = ugly.prettify('pyepidoc')

    assert save_reload_and_compare_with_benchmark(
        doc=prettified,
        target_path=relative_filepaths['prettified_pyepidoc'],
        benchmark_path=relative_filepaths['benchmark_pyepidoc']
    )
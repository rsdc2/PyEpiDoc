from __future__ import annotations

from lxml import etree
from pathlib import Path

from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.shared import head
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark
from pyepidoc.epidoc.dom import lang, line

import pytest

test_files_path = "tests/api/files/"

relative_filepaths = {
    'ugly': 'tests/api/files/prettifying/ugly/ISic000552.xml',
    'benchmark_lxml': 'tests/api/files/prettifying/benchmark/ISic000552_prettified_lxml.xml',
    'benchmark_pyepidoc': 'tests/api/files/prettifying/benchmark/ISic000552_prettified_pyepidoc.xml',
    'prettified_lxml': 'tests/api/files/prettifying/prettified/ISic000552_prettified_lxml.xml',
    'prettified_pyepidoc': 'tests/api/files/prettifying/prettified/ISic000552_prettified_pyepidoc.xml',
    'ISic000001': 'tests/api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'tests/api/files/single_files_tokenized/ISic000552.xml',
    'persName_nested': 'tests/api/files/persName_nested.xml',
    'line_1': 'tests/api/files/line_1.xml',
    'line_2': 'tests/api/files/line_2.xml',
    'gap': 'tests/api/files/gap.xml',
    'comma': 'tests/api/files/comma.xml',
    'leiden': 'tests/api/files/leiden.xml',
    'abbr': 'tests/api/files/abbr.xml'
}

line_2_output = 'tests/api/files/line_2_output.xml'


def test_collect_tokens():
    filepath = relative_filepaths['ISic000001']
    doc = EpiDoc(filepath)

    assert [token.normalized_form 
            for token in doc.tokens_normalized] == [
        'Dis', 
        'manibus', 
        'Zethi', 
        'vixit', 
        'annis', 
        'VI'
    ]


def test_collect_normalized():
    """
    Tests that tokens with <orig> / <reg> or <sic> / <corr> distinctions
    are use the normalized version
    """

    filepath = relative_filepaths['ISic000552']
    doc = EpiDoc(filepath)

    assert [token.normalized_form for token in doc.tokens_normalized][0:2] == [
        'Flamma', 
        'secutor'
    ]


test_date_not_before_files_and_ids = [
    ("ISic000001.xml", "ISic000001"),
    ("ISic000552.xml", "ISic000552")
]
@pytest.mark.parametrize(["filename", "doc_id"], test_date_not_before_files_and_ids)
def test_doc_id(filename: str, doc_id: str):
    """
    Test that document ID collected correctly
    """

    fp = Path(test_files_path + "single_files_untokenized") / Path(filename)
    doc = EpiDoc(fp)
    assert doc.id == doc_id 


test_doc_main_edition_is_empty_files = [
    'ISic000001_empty_main_edition.xml',
    'ISic000001_empty_main_edition_ab.xml'
]
@pytest.mark.parametrize("filename", test_doc_main_edition_is_empty_files)
def test_doc_main_edition_is_empty(filename: str):
    """
    Test that can recognise a main edition that is empty, i.e.
    no usable / tokenizable content
    """
    path = Path(test_files_path + "single_files_untokenized") / Path(filename)
    doc = EpiDoc(path)

    assert doc.main_edition is not None and doc.main_edition.is_empty
    

test_date_not_before_files_and_ids2 = [
    ("ISic000001.xml", (50, 300)),
    ("ISic000552.xml", (200, 500)),
    ("ISic000001_dateNotBefore.xml", (50, 300))
]
@pytest.mark.parametrize(["filename", "date_range"], test_date_not_before_files_and_ids2)
def test_date_not_before(filename: str, date_range: tuple[int | None, int | None]):
    """
    Test that document daterange collected correctly depending on whether
    the document uses @notBefore or @notBefore-Custom
    """

    fp = Path(test_files_path + "single_files_untokenized") / Path(filename)
    doc = EpiDoc(fp)
    assert doc.date_range == date_range


def test_leiden_plus_text():
    """
    Tests that collects the leiden plus text of a 
    token correctly
    """

    fp = relative_filepaths['leiden']
    doc = EpiDoc(fp)

    leiden_strs = [token.leiden_plus_form for token in doc.tokens_no_nested]
    
    assert leiden_strs[0] == '| · Dis · '


def test_lines():
    doc_1 = EpiDoc(relative_filepaths['line_1'])

    token = head(doc_1.tokens_no_nested)
    assert token is not None

    l1 = line(token)
    assert l1 is not None
    assert l1.n == '1'

    supplied = head(token.supplied)
    assert supplied is not None
    
    l2 = line(supplied)
    assert l2 is not None

    assert l2.n == '1'

    doc_2 = EpiDoc(relative_filepaths['line_2'])
    token = head(doc_2.tokens_no_nested)
    assert token is not None

    l3 = line(token)
    assert l3 is not None

    assert l3.n == '1'
    
    second_token = doc_2.tokens_no_nested[1]
    assert second_token.text_desc == 'ambulavit'

    l4 = line(second_token)
    assert l4 is not None
    assert l4.n == '2'


@pytest.mark.parametrize("filepath", relative_filepaths.values())
def test_load_relative_filepath_from_str(filepath:str):
    doc = EpiDoc(filepath)
    assert doc.tokens_normalized != []


def test_materialclasses():
    doc = EpiDoc(relative_filepaths['ISic000001'])
    assert doc.materialclasses == ['#material.stone.marble']


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


def test_punct():
    """
    Tests that comma is removed from string version of token
    """
    doc = EpiDoc(relative_filepaths['comma']) 
    assert str(doc.tokens_no_nested[0]) == "hello"


def test_check_ns_on_load():
    """
    
    """
    _ = EpiDoc(relative_filepaths['ISic000001'])


def test_reproduces_processing_instructions():
    doc = EpiDoc(relative_filepaths['line_2'])
    doc.to_xml_file(line_2_output)
    doc_ = EpiDoc(line_2_output)
    assert len(doc.processing_instructions) == len(doc_.processing_instructions)
    assert all([str(instr) in list(map(str, doc.processing_instructions)) 
                for instr in doc_.processing_instructions])
    
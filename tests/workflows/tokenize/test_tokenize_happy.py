import pytest
from pathlib import Path
from lxml import etree

from tests.config import FILE_WRITE_MODE

from pyepidoc.shared.file import remove_file
from pyepidoc.shared.testing import save_reload_and_compare_with_benchmark
from pyepidoc.epidoc.enums import NamedEntities
from pyepidoc.epidoc.scripts import tokenize, tokenize_to_file_object
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.epidoc.elements.edition import Edition
from pyepidoc.epidoc.elements.ab import Ab
from pyepidoc.xml.utils import abify, editionify, xml_to_str


input_path = Path('tests/workflows/tokenize/files/untokenized')
output_path = Path('tests/workflows/tokenize/files/tokenized_output')
benchmark_path = Path('tests/workflows/tokenize/files/tokenized_benchmark')

tests = [
    'abbr_lone',
    'space',
    'expan', 
    'plain', 
    'persName', 
    'break_equals_no_1',
    'break_equals_no_2',
    'break_equals_no_with_comment',
    'break_equals_no_without_comment', 
    'break_equals_no_unclear',
    'foreign',
    'persName_spacing_1',
    'persName_spacing_2',
    'persName_spacing_3',
    'persName_spacing_4',
    'persName_spacing_ISic000263',
    'hi', # tests that does nothing when a <hi> contains a token
    'interpunct_1', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_3', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_4', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_5', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_6', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_7', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_8', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_9', # tests that recognises interpuncts correctly and puts in <g> tag
    'interpunct_word_space',
    'interpunct_no_word_space',
    'link_1',
    'name_1',
    'note_1',   # Tests that <note> is never separated from the previous space-separated token by a space
    'note_2',   # Tests that <note> is never separated from the previous space-separated token by a space
    'roleName',
    'orgName_1',
    'orgName_2',
    'orgName_3',
    'orgName_4',
    'del_1',
    'del_2',
    'choice',
    'orig',
    'gap',
    'gap2',
    'gap3',
    'gap4',
    'name_inside_choice',
    'no_lb',
    'supplied_1',
    'supplied_2',
    'supplied_3',
    'supplied_4',
    'supplied_with_num',
    'surplus_1',
    'unclear_1',
    'unclear_2', 
    'unclear_3'
]


def get_path_vars(tokenize_type:str) -> tuple[str, str, str, str, str, str]:
    filename = f'{tokenize_type}.xml'
    untokenized_folderpath = 'tests/workflows/tokenize/files/untokenized'
    tokenized_folderpath = 'tests/workflows/tokenize/files/tokenized_output'
    benchmark_folderpath = 'tests/workflows/tokenize/files/tokenized_benchmark'
    tokenized_filepath = Path(tokenized_folderpath) / Path(filename)
    benchmark_filepath = Path(benchmark_folderpath) / Path(filename)

    return (filename, 
            untokenized_folderpath, 
            tokenized_folderpath, 
            benchmark_folderpath, 
            str(tokenized_filepath), 
            str(benchmark_filepath))


def tokenize_epidoc(tokenize_type: str) -> tuple[EpiDoc, EpiDoc]:
    (filename, 
            untokenized_folderpath, 
            tokenized_folderpath, 
            benchmark_folderpath, 
            tokenized_filepath, 
            benchmark_filepath) = get_path_vars(tokenize_type)

    # Remove old output file if exists
    remove_file(tokenized_filepath)
    
    # Tokenize the files
    tokenize(
        src_folderpath=untokenized_folderpath, 
        dst_folderpath=tokenized_folderpath,
        isic_ids=[tokenize_type],
        space_words=True,
        set_universal_ids=False,
        set_n_ids=False
    )
    
    tokenized_epidoc = EpiDoc(tokenized_filepath)
    tokenized_benchmark = EpiDoc(benchmark_filepath)

    return tokenized_epidoc, tokenized_benchmark


def tokenize_epidoc_using_file_object(tokenize_type: str) -> tuple[EpiDoc, EpiDoc]:
    (_, untokenized_folderpath, _, _, _, benchmark_filepath) = get_path_vars(tokenize_type)
    
    tokenized_file = tokenize_to_file_object(
        src_folderpath=untokenized_folderpath, 
        filename=tokenize_type,
        space_words=True,
        set_universal_ids=False,
        set_n_ids=False
    )
    tokenized_epidoc = EpiDoc(tokenized_file)
    tokenized_benchmark = EpiDoc(benchmark_filepath)
    return tokenized_epidoc, tokenized_benchmark


def test_model_headers():
    # Tokenize the files
    if FILE_WRITE_MODE == 'file_object':
        tokenize_func = tokenize_epidoc_using_file_object
    else:
        tokenize_func = tokenize_epidoc

    tokenized_epidoc, tokenized_benchmark = tokenize_func(tokenize_type='xml_model_headers_1')
    assert tokenized_epidoc.processing_instructions_str == tokenized_benchmark.processing_instructions_str

named_entities_xml = [
    ('<lb n="1"/>Dis Manibus sacrum <name>Corneliae</name>',
     '<lb n="1"/><w>Dis</w> <w>Manibus</w> <w>sacrum</w> <name><w>Corneliae</w></name>'),

    ('<measure type="currency" unit="litra" cert="low"><expan><abbr><hi rend="inverted">Δ</hi></abbr><ex>εκάλιτρον</ex></expan></measure>',
     '<measure type="currency" unit="litra" cert="low"><w><expan><abbr><hi rend="inverted">Δ</hi></abbr><ex>εκάλιτρον</ex></expan></w></measure>')

]
@pytest.mark.parametrize("xml_pair", named_entities_xml)
def test_tokenize_and_insert_ws_inside_named_entities(xml_pair: tuple[str, str]):
    
    """
    Tests that tokenizes and inserts <w> elements inside named entities
    """

    # Arrange
    inpt, expected = xml_pair
    edition = Edition.from_xml_str(inpt, wrap_in_ab=True)

    expected_edition = Edition.from_xml_str(expected, wrap_in_ab=True)

    # Act
    edition.tokenize()
    edition.insert_ws_inside_named_entities()
    edition.space_tokens()

    # Assert
    assert edition.xml_str == expected_edition.xml_str


@pytest.mark.parametrize("tokenize_type", tests)
def test_tokenize_special_cases(tokenize_type: str):
    if FILE_WRITE_MODE == 'file_object':
        tokenize_func = tokenize_epidoc_using_file_object
    else:
        tokenize_func = tokenize_epidoc

    # Tokenize the files
    tokenized_epidoc, tokenized_benchmark = \
        tokenize_func(tokenize_type=tokenize_type)

    # Do the tests    
    if [str(word) for word in tokenized_epidoc.tokens_no_nested] != [str(word) for word in tokenized_benchmark.tokens_no_nested]:
        assert False
    
    if [word.xml_byte_str for word in tokenized_epidoc.tokens_no_nested] != [word.xml_byte_str for word in tokenized_benchmark.tokens_no_nested]:
        assert False
    
    if [word.xml_byte_str for word in tokenized_epidoc.compound_words] != [word.xml_byte_str for word in tokenized_benchmark.compound_words]:
        assert False

    # breakpoint()
    if [edition.xml_byte_str for edition in tokenized_epidoc.editions()] != [edition.xml_byte_str for edition in tokenized_benchmark.editions()]:
        assert False


xml_to_tokenize = [
    ('<abbr>a</abbr>',
     '<w><abbr>a</abbr></w>'),

    ('<roleName type="civic" subtype="duumviralis">d<hi rend="apex">u</hi>mviralium</roleName>',
     '<roleName type="civic" subtype="duumviralis"><w>d<hi rend="apex">u</hi>mviralium</w></roleName>'),

    ('<roleName type="civic" subtype="duumviralis">duumviralium</roleName>',
     '<roleName type="civic" subtype="duumviralis"><w>duumviralium</w></roleName>'),
    
    ('<name type="civic" subtype="duumviralis">d<hi rend="apex">u</hi>mviralium</name>',
     '<name type="civic" subtype="duumviralis">d<hi rend="apex">u</hi>mviralium</name>'),
    
    ('d<hi rend="apex">u</hi>mviralium',
     '<w>d<hi rend="apex">u</hi>mviralium</w>'),
    
    ('dominus',
     '<w>dominus</w>'),

    ('<expan><abbr><num value="11">XI</num></abbr><ex>Undeci</ex><abbr>manorum</abbr></expan>',
     '<w><expan><abbr><num value="11">XI</num></abbr><ex>Undeci</ex><abbr>manorum</abbr></expan></w>'),

    ('<hi rend="supraline"><num value="88">πη</num></hi> · ἐτελεύτ<supplied reason="lost">η</supplied>',
     '<hi rend="supraline"><num value="88">πη</num></hi><g ref="#interpunct">·</g><w>ἐτελεύτ<supplied reason="lost">η</supplied></w>'),
     
    ('<hi rend="supraline"><num value="15">ιε</num></hi> <w>καλα<supplied reason="lost">ν</supplied></w>',
     '<hi rend="supraline"><num value="15">ιε</num></hi><w>καλα<supplied reason="lost">ν</supplied></w>'),

    # <hi> is treated as subsumable
    ('<num value="15"><hi rend="supraline">ιε</hi></num> καλα<supplied reason="lost">ν</supplied>',
     '<num value="15"><hi rend="supraline">ιε</hi></num><w>καλα<supplied reason="lost">ν</supplied></w>'),

    ('<placeName ref="https://pleiades.stoa.org/places/678374">Μά'
     '<lb n="3" break="no"/>κρης κώ'
     '<lb n="4" break="no"/>μης</placeName>',

     '<placeName ref="https://pleiades.stoa.org/places/678374"><w>Μά'
     '<lb n="3" break="no"/>κρης</w><w>κώ'
     '<lb n="4" break="no"/>μης</w></placeName>'
    ),

    ('<persName><supplied><name>John</name></supplied></persName>',
     '<persName><supplied><name>John</name></supplied></persName>'),

    ('<persName>'
        '<supplied>'
            '<name>John</name>'
        '</supplied>'
     '</persName>',
     
     '<persName>'
        '<supplied>'
            '<name>John</name>'
        '</supplied>'
     '</persName>'),


    ('<supplied>John</supplied>',
     '<w><supplied>John</supplied></w>'),

    (
     '<persName type="attested">'
		'<supplied reason="lost">'
			'<name type="praenomen"><expan><abbr>M</abbr><ex>arci</ex></expan></name>'
		'</supplied>' 
     '</persName>',

     '<persName type="attested">'
        '<supplied reason="lost">'
            '<name type="praenomen"><expan><abbr>M</abbr><ex>arci</ex></expan></name>'
        '</supplied>' 
     '</persName>'
     ),

    (
     '<persName>'
		'<supplied>'
			'<name><expan><abbr>M</abbr><ex>arci</ex></expan></name>'
		'</supplied>' 
     '</persName>',

     '<persName>'
        '<supplied>'
            '<name><expan><abbr>M</abbr><ex>arci</ex></expan></name>'
        '</supplied>' 
     '</persName>'
     ),

    (
     '<persName>'
		'<supplied>'
			'<name>Marci</name>'
		'</supplied>' 
     '</persName>',

     '<persName>'
        '<supplied>'
            '<name>Marci</name>'
        '</supplied>' 
     '</persName>'
     ),
     (
      'fecerunt.',
      '<w>fecerunt.</w>'
     ),
     ( # Check that does not tokenize more than once
         '<roleName type="civic" subtype="duumvir"><expan><abbr><num value="2"><supplied reason="lost">I</supplied><unclear>I</unclear></num>vir</abbr><ex>o</ex></expan></roleName>',
         '<roleName type="civic" subtype="duumvir"><w><expan><abbr><num value="2"><supplied reason="lost">I</supplied><unclear>I</unclear></num>vir</abbr><ex>o</ex></expan></w></roleName>'
     ),
     (
        '<roleName type="supracivic" subtype="consularis">consul<supplied reason="lost">aris</supplied></roleName>',
        '<roleName type="supracivic" subtype="consularis"><w>consul<supplied reason="lost">aris</supplied></w></roleName>'
     ),
     (
        '<persName>consul<supplied reason="lost">aris</supplied></persName>',
        '<persName><w>consul<supplied reason="lost">aris</supplied></w></persName>'
     ),
     (
        'consul<supplied reason="lost">aris</supplied>',
        '<w>consul<supplied reason="lost">aris</supplied></w>'
     ),
     (
         """<lb n="3"/>
                <expan>
                    <abbr>Cla</abbr>
                    <ex>udia</ex>
                </expan>
                ·""",
         '<lb n="3"/><w><expan><abbr>Cla</abbr><ex>udia</ex></expan></w><g ref="#interpunct">·</g>'
     ),
     
    ('<roleName type="civic" subtype="duumvir"><num value="2"><hi rend="supraline">II</hi></num> <g ref="#interpunct">·</g> v<hi rend="tall">i</hi>r</roleName>',
     '<roleName type="civic" subtype="duumvir"><num value="2"><hi rend="supraline">II</hi></num><g ref="#interpunct">·</g><w>v<hi rend="tall">i</hi>r</w></roleName>'),

    ('<persName type="civic" subtype="duumvir"><num value="2"><hi rend="supraline">II</hi></num> <g ref="#interpunct">·</g> v<hi rend="tall">i</hi>r</persName>',
     '<persName type="civic" subtype="duumvir"><num value="2"><hi rend="supraline">II</hi></num><g ref="#interpunct">·</g><w>v<hi rend="tall">i</hi>r</w></persName>'),

    ('<roleName type="civic" subtype="duumvir"><hi rend="supraline">II</hi> <g ref="#interpunct">·</g> v<hi rend="tall">i</hi>r</roleName>',
     '<roleName type="civic" subtype="duumvir"><w><hi rend="supraline">II</hi></w><g ref="#interpunct">·</g><w>v<hi rend="tall">i</hi>r</w></roleName>'),

    ('<persName type="civic" subtype="duumvir"><hi rend="supraline">II</hi> <g ref="#interpunct">·</g> v<hi rend="tall">i</hi>r</persName>',
     '<persName type="civic" subtype="duumvir"><w><hi rend="supraline">II</hi></w><g ref="#interpunct">·</g><w>v<hi rend="tall">i</hi>r</w></persName>'),

    ('<g ref="#interpunct">·</g> v<hi rend="tall">i</hi>r',
     '<g ref="#interpunct">·</g><w>v<hi rend="tall">i</hi>r</w>'),

     ("""
       <persName>
            <name>
                <expan>
                    <abbr>Q</abbr>
                    <ex>uinto</ex>
                </expan>
            </name>
            · <name>Atilio</name>
        </persName>
      """,
      '<persName><name><expan><abbr>Q</abbr><ex>uinto</ex></expan></name><g ref="#interpunct">·</g><name>Atilio</name></persName>'),

     ('<roleName type="military" subtype="primipilus"><w>primo</w> <g ref="#interpunct">·</g> <w>p<hi rend="tall">i</hi>lo</w></roleName>',
      '<roleName type="military" subtype="primipilus"><w>primo</w><g ref="#interpunct">·</g><w>p<hi rend="tall">i</hi>lo</w></roleName>'),

    ('Tr<unclear>u</unclear>t<supplied reason="undefined" evidence="previouseditor">tedi</supplied><supplied reason="lost">us</supplied>',
     '<w>Tr<unclear>u</unclear>t<supplied reason="undefined" evidence="previouseditor">tedi</supplied><supplied reason="lost">us</supplied></w>'),

    # Test that space is not tokenized
    ('<space unit="character" quantity="1"/>',
     '<space unit="character" quantity="1"/>')
]


@pytest.mark.parametrize("xml_pair", xml_to_tokenize)
def test_tokenize_epidoc_fragments(xml_pair: tuple[str, str]):

    # Arrange
    xml_pair_abs = tuple(map(abify, xml_pair))

    xml, tokenized_xml = xml_pair_abs
    untokenized = Ab(etree.fromstring(xml, None))
    tokenized_benchmark = Ab(etree.fromstring(tokenized_xml, None))

    # Act

    tokenized = untokenized.tokenize()

    if tokenized is None:
        return False
    
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
    assert tokenized.get_child_tokens() != []
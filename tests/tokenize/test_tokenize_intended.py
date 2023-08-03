from pyepidoc.epidoc.scripts import tokenize
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.file import FileInfo, FileMode
from pyepidoc.file.funcs import filepath_from_list

import os
import pytest


tests = [
    'space',
    'expan', 
    'plain', 
    'persName', 
    'break_equals_no_1',
    'break_equals_no_2',
    # 'break_equals_no_with_comment',
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
    'interpunct_2', # tests that recognises interpuncts correctly and puts in <g> tag
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
    'no_lb',
    'supplied_1',
    'supplied_2',
    'supplied_3',
    'supplied_4',
    'supplied_with_num',
    'surplus_1',
    'unclear_1',
    'unclear_2'
]


def remove_file(filepath:str):
    try:
        tokenized_f = FileInfo(
            filepath=filepath,
            mode = FileMode.r.value,
            fullpath=False
        )
        if tokenized_f.exists:
            os.remove(tokenized_f.full_filepath)
    except FileExistsError:
        pass


def get_path_vars(tokenize_type:str) -> tuple[str, str, str, str, str, str]:
    filename = f'{tokenize_type}.xml'
    untokenized_folderpath = 'tokenize/files/untokenized'
    tokenized_folderpath = 'tokenize/files/tokenized_output'
    benchmark_folderpath = 'tokenize/files/tokenized_benchmark'
    tokenized_filepath = filepath_from_list([tokenized_folderpath], filename)
    benchmark_filepath = filepath_from_list([benchmark_folderpath], filename)

    return (filename, 
            untokenized_folderpath, 
            tokenized_folderpath, 
            benchmark_folderpath, 
            tokenized_filepath, 
            benchmark_filepath)


def tokenize_epidoc(tokenize_type:str) -> tuple[EpiDoc, EpiDoc]:
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
        set_ids=False,
        fullpath=False
    )

    tokenized_f = FileInfo(
        filepath=tokenized_filepath,
        mode = FileMode.r.value,
        fullpath=False
    )

    benchmark_f = FileInfo(
        filepath=benchmark_filepath,
        mode = FileMode.r.value,
        fullpath=False
    )

    tokenized_epidoc = EpiDoc(tokenized_f)
    tokenized_benchmark = EpiDoc(benchmark_f)

    return tokenized_epidoc, tokenized_benchmark


def test_model_headers():
    # Tokenize the files
    tokenized_epidoc, tokenized_benchmark = tokenize_epidoc(tokenize_type='xml_model_headers_1.xml')


    

@pytest.mark.parametrize("tokenize_type", tests)
def test_tokenize(tokenize_type:str):
    # Tokenize the files
    tokenized_epidoc, tokenized_benchmark = tokenize_epidoc(tokenize_type=tokenize_type)

    # Do the tests    
    assert [str(word) for word in tokenized_epidoc.tokens] == [str(word) for word in tokenized_benchmark.tokens]
    assert [word.xml for word in tokenized_epidoc.tokens] == [word.xml for word in tokenized_benchmark.tokens]
    assert [word.xml for word in tokenized_epidoc.compound_words] == [word.xml for word in tokenized_benchmark.compound_words]
    assert [edition.xml for edition in tokenized_epidoc.editions()] == [edition.xml for edition in tokenized_benchmark.editions()]
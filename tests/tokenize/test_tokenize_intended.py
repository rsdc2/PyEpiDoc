from pyepidoc.epidoc.funcs import tokenize
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.file import FileInfo, FileMode
from pyepidoc.file.funcs import filepath_from_list

import os
import pytest


tests = [
    'expan', 
    'plain', 
    'persName', 
    'break_equals_no',
    # 'break_equals_no_with_comment',
    'break_equals_no_without_comment', 
    'break_equals_no_unclear',
    'persName_spacing',
    'persName_spacing_3',
    'persName_spacing_2',
    'persName_spacing_3',
    'persName_spacing_4',
    'persName_spacing_ISic000263',
    'interpunct_word_space',
    'interpunct_no_word_space',
    'roleName',
    'orgName',
    'del',
    'del2',
    'choice',
    'orig',
    'gap',
    'gap2',
    'gap3',
    'no_lb'
]


@pytest.mark.parametrize("tokenize_type", tests)
def test_tokenize(tokenize_type:str):
    filename = f'{tokenize_type}.xml'
    untokenized_folderpath = 'tokenize/files/untokenized'
    tokenized_folderpath = 'tokenize/files/tokenized_output'
    benchmark_folderpath = 'tokenize/files/tokenized_benchmark'
    untokenized_filepath = filepath_from_list([untokenized_folderpath], filename)
    tokenized_filepath = filepath_from_list([tokenized_folderpath], filename)
    benchmark_filepath = filepath_from_list([benchmark_folderpath], filename)

    # Remove old output files if they exist
    try:
        tokenized_f = FileInfo(
            filepath=tokenized_filepath,
            mode = FileMode.r.value,
            fullpath=False
        )
        if tokenized_f.exists:
            os.remove(tokenized_f.full_filepath)
    except FileExistsError:
        pass

    
    # Tokenize the files
    tokenize(
        src_folderpath=untokenized_folderpath, 
        dst_folderpath=tokenized_folderpath,
        filenames=[tokenize_type],
        space_words=True,
        ids=False,
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
    
    assert [str(word) for word in tokenized_epidoc.tokens] == [str(word) for word in tokenized_benchmark.tokens]
    assert [word.xml for word in tokenized_epidoc.tokens] == [word.xml for word in tokenized_benchmark.tokens]
    assert [word.xml for word in tokenized_epidoc.compound_words] == [word.xml for word in tokenized_benchmark.compound_words]
    assert [edition.xml for edition in tokenized_epidoc.editions()] == [edition.xml for edition in tokenized_benchmark.editions()]

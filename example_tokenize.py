from pyepidoc.epidoc import scripts

from pyepidoc.epidoc.scripts import tokenize
from pyepidoc.epidoc.epidoc import EpiDoc
from pyepidoc.file import FileInfo, FileMode
from pyepidoc.file.funcs import filepath_from_list

import os

untokenized_folderpath = 'tests/tokenize/files/untokenized'
tokenized_folderpath = 'data/tokenize/tokenized_output'


def tokenize_file(tokenize_type:str):

    filename = f'{tokenize_type}.xml'
    # untokenized_folderpath = 'tokenize/files/untokenized'
    # tokenized_folderpath = 'tokenize/files/tokenized_output'
    # benchmark_folderpath = 'tokenize/files/tokenized_benchmark'
    untokenized_filepath = filepath_from_list([untokenized_folderpath], filename)
    tokenized_filepath = filepath_from_list([tokenized_folderpath], filename)
    # benchmark_filepath = filepath_from_list([benchmark_folderpath], filename)

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
        isic_ids=[tokenize_type],
        space_words=True,
        set_ids=False,
        fullpath=False
    )

# tokenize_file('break_equals_no_unclear')
tokenize_file('unclear_2')
# tokenize_file('interpunct_10')
# tokenize_file('gap')
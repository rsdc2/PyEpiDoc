from typing import Optional, Sequence
from os import getcwd

from .epidoc_types import (
    SpaceUnit
)
from .epidoc import EpiDoc
from .corpus import EpiDocCorpus
from .ab import Ab
from .edition import Edition
from .lb import Lb

from ..file import FileInfo
from ..file.funcs import filepath_from_list
from ..constants import *
from ..utils import maxone, flatlist, head


def tokenize(
    src_folderpath:str, 
    dst_folderpath:str, 
    isic_ids:list[str],
    space_words:bool,
    set_ids:bool,
    fullpath=False
) -> None:

    for filename in isic_ids:
        if fullpath == False:
            src_filepath = filepath_from_list([getcwd(), src_folderpath], filename + ".xml")
            dst_filepath = filepath_from_list([getcwd(), dst_folderpath], filename + ".xml")
        else:
            src_filepath = filepath_from_list([src_folderpath], filename + ".xml")
            dst_filepath = filepath_from_list([dst_folderpath], filename + ".xml")

        src = FileInfo(
            filepath=src_filepath, 
            mode='r', 
            create_folderpath=False,
            fullpath=True
        )

        dst = FileInfo(
            filepath=dst_filepath,
            mode='w', 
            create_folderpath=False,
            fullpath=True
        )

        doc = EpiDoc(src)
        doc.tokenize()
        
        if space_words: 
            doc.space_tokens()
        if set_ids:
            doc.set_ids()

        doc.convert_ws_to_names()
        doc.prettify_edition(spaceunit=SpaceUnit.Space, number=4)

        doc.to_xml_file(
            dst.full_filepath,
            verbose=True,
            create_folderpath=False,
            fullpath=True
        )


def tokenize_corpus(
    src_folderpath:str, 
    dst_folderpath:str, 
    fullpath:bool,
    head:Optional[int]=None
) -> None:
    corpus = EpiDocCorpus(src_folderpath, head=head)
    corpus.tokenize_to_folder(dstfolder=dst_folderpath, fullpath=fullpath)


def set_ids(
    src_folderpath:str, 
    dst_folderpath:str, 
    ids:list[str],
    fullpath=False
):
    for filename in ids:
        if fullpath == False:
            src_filepath = filepath_from_list([getcwd(), src_folderpath], filename + ".xml")
            dst_filepath = filepath_from_list([getcwd(), dst_folderpath], filename + ".xml")
        else:
            src_filepath = filepath_from_list([src_folderpath], filename + ".xml")
            dst_filepath = filepath_from_list([dst_folderpath], filename + ".xml")

        src = FileInfo(
            filepath=src_filepath, 
            mode='r', 
            create_folderpath=False,
            fullpath=True
        )

        dst = FileInfo(
            filepath=dst_filepath,
            mode='w', 
            create_folderpath=False,
            fullpath=True
        )

        doc = EpiDoc(src)
        doc.set_ids()

        doc.convert_ws_to_names()
        doc.prettify_edition(spaceunit=SpaceUnit.Space, number=4)

        doc.to_xml_file(
            dst.full_filepath,
            verbose=True,
            create_folderpath=False,
            fullpath=True
        )

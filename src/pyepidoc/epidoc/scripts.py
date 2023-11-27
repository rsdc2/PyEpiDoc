from typing import Optional
from pathlib import Path

from .epidoc_types import (
    SpaceUnit
)
from .epidoc import EpiDoc
from .corpus import EpiDocCorpus
from ..constants import *


def tokenize(
    src_folderpath: str, 
    dst_folderpath: str, 
    isic_ids: list[str],
    space_words: bool,
    set_ids: bool
) -> None:

    
    for filename in isic_ids:
        src = Path(src_folderpath) / Path(filename + '.xml')
        dst = Path(dst_folderpath) / Path(filename + '.xml')

        doc = EpiDoc(src)
        doc.tokenize(
            prettify_edition=True, 
            add_space_between_words=space_words, 
            set_ids=set_ids, 
            convert_ws_to_names=True, 
            verbose=False
        )

        doc.to_xml_file(dst)


def tokenize_corpus(
    src_folderpath:str, 
    dst_folderpath:str
) -> None:
    corpus = EpiDocCorpus(src_folderpath)
    corpus.tokenize_to_folder(dstfolder=dst_folderpath)


def set_ids(
    src_folderpath:str, 
    dst_folderpath:str, 
    ids:list[str]
):
    for filename in ids:
        src = Path(src_folderpath) / Path(filename + '.xml')
        dst = Path(dst_folderpath) / Path(filename + '.xml')

        doc = EpiDoc(src)
        doc.set_ids()

        doc.convert_ws_to_names()
        doc.prettify_edition(spaceunit=SpaceUnit.Space, number=4)

        doc.to_xml_file(dst.absolute())

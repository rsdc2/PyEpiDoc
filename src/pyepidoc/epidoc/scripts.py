from pathlib import Path
from io import BytesIO

from ..shared.enums import (
    SpaceUnit
)
from .epidoc import EpiDoc
from .corpus import EpiDocCorpus
from ..shared.constants import *


def tokenize(
    src_folderpath: str, 
    dst_folderpath: str, 
    isic_ids: list[str],
    space_words: bool,
    set_universal_ids: bool,
    set_n_ids: bool
) -> None:

    for filename in isic_ids:
        src = Path(src_folderpath) / Path(filename + '.xml')
        dst = Path(dst_folderpath) / Path(filename + '.xml')

        doc = EpiDoc(src)
        doc.tokenize(
            prettify_edition=True, 
            add_space_between_words=space_words, 
            set_universal_ids=set_universal_ids,
            set_n_ids=set_n_ids, 
            convert_ws_to_names=True, 
            verbose=False
        )

        doc.to_xml_file(dst)


def tokenize_to_file_object(
    src_folderpath: str, 
    filename: str,
    space_words: bool,
    set_universal_ids: bool,
    set_n_ids: bool
) -> BytesIO:
    
    src = Path(src_folderpath) / Path(filename + '.xml')

    doc = EpiDoc(src)
    doc.tokenize(
        prettify_edition=True, 
        add_space_between_words=space_words, 
        set_n_ids=set_n_ids, 
        set_universal_ids=set_universal_ids,
        convert_ws_to_names=True, 
        verbose=False
    )

    f = doc.to_xml_file_object()
    return f


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
        doc.prettify_main_edition(spaceunit=SpaceUnit.Space.value, number=4)

        doc.to_xml_file(dst.absolute())

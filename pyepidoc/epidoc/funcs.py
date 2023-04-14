from typing import Optional
from os import getcwd

from .epidoctypes import (
    SpaceUnit, 
    Morphology, 
    TokenInfo, 
    Morphology
)
from .epidoc import EpiDoc
from .abbr import AbbrInfo
from .corpus import EpiDocCorpus
from ..base import Element

from ..file import FileInfo
from ..file.funcs import filepath_from_list
from ..constants import *


def doc_id(elem: Element) -> Optional[str]:
    """
    Finds the document id containing a given element.
    """
    roottree = elem.roottree

    if roottree is None: 
        return None

    doc = EpiDoc(roottree)
    return doc.id


def wordinfo_factory(lemmata:list[str]=[], morphologies:list[Morphology]=[]) -> list[TokenInfo]:
    if lemmata and morphologies:
        return [TokenInfo(lemma, morphology) 
            for lemma in set(lemmata) 
                for morphology in set(morphologies)]

    else:
        raise ValueError("Both lemmata and morphologies must be specified.")


def abbrinfo_factory(forms:list[str]=[], abbrs:list[str]=[]) -> list[AbbrInfo]:
    if forms and abbrs:
        return [AbbrInfo(form, abbr) 
            for form in set(forms) 
                for abbr in set(abbrs)]

    else:
        raise ValueError("Both lemmata and morphologies must be specified.")


def tokenize(
    src_folderpath:str, 
    dst_folderpath:str, 
    filenames:list[str],
    space_words:bool,
    ids:bool,
    fullpath=False
) -> None:


    for filename in filenames:
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
            doc.add_space_between_tokens(override=True)
        if ids:
            doc.set_ids(override=True)

        doc.convert_ws_to_names()
        doc.prettify_edition(spaceunit=SpaceUnit.Space, number=4)

        doc.to_xml(
            dst.full_filepath,
            verbose=True,
            create_folderpath=False,
            fullpath=True
        )


def tokenize_corpus(
    src_folderpath:str, 
    dst_folderpath:str, 
    head:Optional[int]=None
) -> None:
    corpus = EpiDocCorpus(folderpath=src_folderpath, head=head)
    corpus.tokenize(dstfolder=dst_folderpath)
from typing import Optional, Sequence
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
from .ab import Ab
from .edition import Edition

from ..file import FileInfo
from ..file.funcs import filepath_from_list
from ..constants import *
from ..utils import maxone, flatlist, head


def ancestor_abs(elem: Element) -> Sequence[Ab]:
    """
    Returns a |Sequence| of |Ab|s containing an |Element|,
    starting with the ancestor closest to the |Element|
    """
    return [Ab(elem) for elem in elem.parents 
        if elem.name_no_namespace == 'ab']


def owner_doc(elem:Element) -> Optional[EpiDoc]:
    """
    Returns the |EpiDoc| document owning an element.
    """
    roottree = elem.roottree

    if roottree is None: 
        return None

    return EpiDoc(roottree)


def ancestor_edition(elem: Element) -> Optional[Edition]:

    """
    Returns the |Edition| containing an element (if any).
    """

    editions = [Edition(elem) for elem in elem.parents 
        if elem.is_edition]

    edition = maxone(
        lst=editions,
        defaultval=None,
        throw_if_more_than_one=False
    )

    if edition is None:
        return None
    
    return edition


def doc_id(elem: Element) -> Optional[str]:
    """
    Finds the document id containing a given element.
    """
    roottree = elem.roottree

    if roottree is None: 
        return None

    doc = EpiDoc(roottree)
    return doc.id


def lang(elem: Element) -> Optional[str]:
    """
    Returns the language of the element, based on 
    the language specified either in the 
    <div> or <ab> parent.
    """

    ab_ancestors = ancestor_abs(elem)
    ab_langs = flatlist([ab.lang for ab in ab_ancestors 
        if ab.lang is not None])

    ab_lang = head(ab_langs, throw_if_more_than_one=False)

    if ab_lang is not None:
        return ab_lang

    edition = ancestor_edition(elem)
    if edition is not None and edition.lang is not None:
        return edition.lang

    doc = owner_doc(elem)
    if doc is None:
        return None

    if doc.langs is None:
        return None
    
    return doc.mainlang
    

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
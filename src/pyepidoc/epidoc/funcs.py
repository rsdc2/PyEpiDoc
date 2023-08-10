from typing import Optional, Sequence
from os import getcwd

from .epidoctypes import (
    SpaceUnit, 
    Morphology, 
    Morphology
)
from .epidoc import EpiDoc
from .corpus import EpiDocCorpus
from ..base import Element
from .ab import Ab
from .edition import Edition
from .lb import Lb

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
        if elem.local_name == 'ab']


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
        if Element(elem).is_edition]

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
    

def line(elem:Element) -> Optional[Lb]:
    lb = elem.lb_in_preceding_or_ancestor
    if lb is None:
        return None
    return Lb(elem.lb_in_preceding_or_ancestor)
"""
Functions for navigating the DOM from elements within 
the document
"""

from typing import Optional, Sequence

from .epidoc import EpiDoc
from .element import EpiDocElement
from .elements.ab import Ab
from .elements.edition import Edition
from .elements.lb import Lb

from ..shared.constants import *
from ..shared import maxone, head


def ancestor_abs(elem: EpiDocElement) -> Sequence[Ab]:
    """
    Returns a |Sequence| of |Ab|s containing an |Element|,
    starting with the ancestor closest to the |Element|
    """
    return [Ab(elem) for elem in elem.ancestors_incl_self 
        if elem.localname == 'ab']


def owner_doc(elem:EpiDocElement) -> Optional[EpiDoc]:
    """
    Returns the |EpiDoc| document owning an element.
    """
    roottree = elem.roottree

    if roottree is None: 
        return None

    return EpiDoc(roottree)


def ancestor_edition(elem: EpiDocElement) -> Optional[Edition]:

    """
    Returns the |Edition| containing an element (if any).
    """

    editions = [Edition(elem) for elem in elem.ancestors_incl_self 
        if EpiDocElement(elem).is_edition]

    edition = maxone(
        lst=editions,
        defaultval=None,
        throw_if_more_than_one=False
    )

    if edition is None:
        return None
    
    return edition


def doc_id(elem: EpiDocElement) -> Optional[str]:
    """
    Finds the document id containing a given element.
    """
    roottree = elem.roottree

    if roottree is None: 
        return None

    doc = EpiDoc(roottree)
    return doc.id


def lang(elem: EpiDocElement) -> Optional[str]:
    """
    Returns the language of the element, based on 
    the language specified either in the 
    <div> or <ab> parent.
    If neither of those specify the language, 
    then reports the mainLang attribute
    """

    ab_ancestors = ancestor_abs(elem)
    ab_langs = [ab.lang for ab in ab_ancestors 
        if ab.lang is not None]

    ab_lang = head(ab_langs, throw_if_more_than_one=True)

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
    

def line(elem: EpiDocElement) -> Optional[Lb]:
    lb = elem.lb_in_preceding_or_ancestor
    
    if lb is None:
        return None
    
    return Lb(lb)


def materialclasses(elem: EpiDocElement) -> list[str]:
    """
    Returns a list of the material classes of the owner
    document
    """

    doc = owner_doc(elem)
    if doc is None:
        return []
    
    return doc.materialclasses
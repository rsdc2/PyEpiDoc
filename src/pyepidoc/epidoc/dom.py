"""
Functions for navigating the DOM from elements within 
the document
"""
from __future__ import annotations
from typing import Optional, Sequence
from lxml.etree import _Element, _ElementUnicodeResult

from pyepidoc.shared.constants import *
from pyepidoc.shared import maxone, head
from pyepidoc.xml.utils import localname

from .epidoc import EpiDoc
from .epidoc_element import EpiDocElement
from .edition_elements.ab import Ab
from .edition_elements.edition import Edition
from .edition_elements.lb import Lb


def ancestor_abs(elem: EpiDocElement) -> Sequence[Ab]:
    """
    Returns a |Sequence| of |Ab|s containing an |Element|,
    starting with the ancestor closest to the |Element|
    """
    return [Ab(elem) for elem in elem.get_ancestors_incl_self()
        if elem.localname == 'ab']


def owner_doc(elem: EpiDocElement) -> Optional[EpiDoc]:
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

    editions = [Edition(elem) for elem in elem.get_ancestors_incl_self()
        if EpiDocElement(elem).is_edition]

    edition = maxone(
        lst=editions,
        defaultval=None,
        throw_if_more_than_one=False
    )

    if edition is None:
        return None
    
    return edition


def ancestor_ab(elem: EpiDocElement) -> Optional[Ab]:
    """
    Returns the Ab containing the element (if any)
    """

    abs = filter(
        lambda elem: localname(elem.e) == 'ab', 
        elem.ancestors_excl_self
    )

    try:
        return Ab(next(abs))
    except StopIteration:
        return None


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
    

def last_in_ab(elem: EpiDocElement) -> bool:
    """
    Return True if the element is last in its <ab/>
    """

    ab = ancestor_ab(elem)
    if ab is None:
        return False
    
    return id(elem.e) == id(ab.tokens[-1].e)


def line(elem: EpiDocElement) -> Optional[Lb]:
    lb = elem.has_lb_in_preceding_or_ancestor
    
    if lb is None:
        return None
    
    return Lb(lb)


def line_ends_inside(elem: EpiDocElement) -> int:
    """
    Count the number of <lb/> elements that are 
    descendants of the element
    """

    lbs = filter(
        lambda elem: localname(elem.e) == 'lb', 
        elem.desc_elems
    )

    return len(list(lbs))


def line_end_after(elem: EpiDocElement) -> bool:
    """
    Returns True if the token or part of the token
    appears at a line end
    """

    def _filter_nodes(node: _ElementUnicodeResult | _Element) -> bool:
        """
        Filter out text nodes that contain line breaks and nothing else
        """
        if type(node) is _Element:
            return True
        elif type(node) is _ElementUnicodeResult:
            if '\n' in node and node.strip() == '':
                return False
            
            return True
        
        return False


    if last_in_ab(elem):
        return True

    following = filter(_filter_nodes, elem.following_nodes_in_ab)
    localnames = map(localname, following)
    try:
        first = next(localnames)
        if first == 'lb':
            return True
        else:
            return False
            
    except StopIteration:
        return False
    

def line_ends(elem: EpiDocElement) -> int:
    inside = line_ends_inside(elem)
    after = line_end_after(elem)

    if after:
        return inside + 1
    else:
        return inside

def materialclasses(elem: EpiDocElement) -> list[str]:
    """
    Returns a list of the material classes of the owner
    document
    """

    doc = owner_doc(elem)
    if doc is None:
        return []
    
    return doc.materialclasses
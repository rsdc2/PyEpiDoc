"""
Functions for navigating the DOM from elements within 
the document
"""
from __future__ import annotations
from typing import Optional, Sequence

from pyepidoc.shared.constants import *
from pyepidoc.shared import maxone, head
from pyepidoc.xml.utils import localname
from pyepidoc.xml.xml_text import XmlText
from pyepidoc.xml.xml_element import XmlNode, XmlElement

from .epidoc import EpiDoc
from .tokenizable_element import TokenizableElement
from .edition_elements.ab import Ab
from .edition_elements.edition import Edition
from .edition_elements.lb import Lb


def ancestor_abs(elem: TokenizableElement) -> Sequence[Ab]:
    """
    Returns a |Sequence| of |Ab|s containing an |Element|,
    starting with the ancestor closest to the |Element|
    """
    return [Ab(elem) for elem in elem._e.get_ancestors_incl_self()
        if elem.localname == 'ab']


def owner_doc(elem: TokenizableElement) -> Optional[EpiDoc]:
    """
    Returns the |EpiDoc| document owning an element.
    """
    roottree = elem._e.roottree

    if roottree is None: 
        return None

    return EpiDoc(roottree)


def ancestor_edition(elem: TokenizableElement) -> Optional[Edition]:

    """
    Returns the |Edition| containing an element (if any).
    """

    editions = [Edition(elem) for elem in elem._e.get_ancestors_incl_self()
        if TokenizableElement(elem).is_edition]

    edition = maxone(
        lst=editions,
        defaultval=None,
        throw_if_more_than_one=False
    )

    if edition is None:
        return None
    
    return edition


def ancestor_ab(elem: TokenizableElement) -> Ab | None:
    """
    Returns the Ab containing the element (if any)
    """

    abs = filter(
        lambda elem: elem.localname == 'ab', 
        elem._e.ancestors_excl_self
    )

    try:
        return Ab(next(abs))
    except StopIteration:
        return None


def doc_id(elem: TokenizableElement) -> Optional[str]:
    """
    Finds the document id containing a given element.
    """
    roottree = elem._e.roottree

    if roottree is None: 
        return None

    doc = EpiDoc(roottree)
    return doc.id


def lang(elem: TokenizableElement) -> Optional[str]:
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
    

def last_in_ab(elem: TokenizableElement) -> bool:
    """
    Return True if the element is last in its <ab/>
    """

    ab = ancestor_ab(elem)
    if ab is None:
        return False
    
    return id(elem._e._e) == id(ab.tokens[-1]._e._e)


def line(elem: TokenizableElement) -> Optional[Lb]:
    lb = elem.has_lb_in_preceding_or_ancestor
    
    if lb is None:
        return None
    
    return Lb(lb)


def contains_line_end(elem: TokenizableElement) -> int:
    """
    Count the number of <lb/> elements that are descendants of the element
    """
    lbs = elem.get_desc('lb')
    return len(lbs)


def has_line_end_after(elem: TokenizableElement) -> bool:
    """
    Returns True if the token or part of the token
    appears at a line end
    """

    def not_whitespace(node: XmlNode) -> bool:
        """
        Filter out text nodes that contain whitespace and nothing else
        """
        if isinstance(node, XmlElement):
            return True
        elif isinstance(node, XmlText):
            if node.text.strip() == '':
                return False
            return True
        return False

    if last_in_ab(elem):
        return True

    following = [node for node in elem.following_nodes_in_ab
                 if not_whitespace(node)]
    localnames = (node.localname for node in following)
    try:
        next_element_name = next(localnames)
        if next_element_name == 'lb':
            return True
        return False        
    except StopIteration:
        return False
    
def contains_line_end_or_has_line_end_after(elem: TokenizableElement) -> int:
    line_ends_contained = contains_line_end(elem)
    line_end_is_after = has_line_end_after(elem)

    if line_end_is_after:
        return line_ends_contained + 1
    else:
        return line_ends_contained

def materialclasses(elem: TokenizableElement) -> list[str]:
    """
    Returns a list of the material classes of the owner
    document
    """

    doc = owner_doc(elem)
    if doc is None:
        return []
    
    return doc.materialclasses
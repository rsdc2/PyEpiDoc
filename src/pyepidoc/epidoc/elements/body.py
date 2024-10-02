
from __future__ import annotations
from copy import deepcopy

from lxml import etree
from lxml.etree import _Element

from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc.epidoc.elements.edition import Edition
from pyepidoc.epidoc.token import Token

from pyepidoc.xml.namespace import Namespace as ns

from pyepidoc.shared.constants import (A_TO_Z_SET, 
                         TEINS, 
                         XMLNS, 
                         SubsumableRels,
                         ROMAN_NUMERAL_CHARS,
                         VALID_BASES)

from pyepidoc.shared.utils import maxone, listfilter
from pyepidoc.shared.dicts import dict_remove_none
from typing import Optional


class Body(EpiDocElement):    

    """
    Provides services for the <body> element of the EpiDoc file
    """

    def __init__(
        self, 
        e: _Element | EpiDocElement | BaseElement
    ) -> None:
        
        super().__init__(e, False)
        body_tag = ns.give_ns('body', TEINS)

        if e.tag != body_tag:
            raise ValueError(f'Cannot make <body> element from '
                             f'<{self.tag}> element.')

    def copy_edition_content(
            self,
            source: Edition,
            target: Edition,
            tags_to_include: list[str] | None = None
    ) -> Edition:
        
        """
        Copies the elements from one edition to another within
        the body, and returns a reference the edition 
        receiving the new information.

        :param tags_to_include: a list of tag names (no namespaces)
        to include in the copy. If this is None, all elements are copied.
        """

        def append_children(
                source_elem: EpiDocElement, 
                target_elem: EpiDocElement):

            for child in source_elem.child_elements:
                if tags_to_include is None or child.tag.name in tags_to_include:
                    child_for_target = EpiDocElement(deepcopy(child._e))
                    target_elem._e.append(child_for_target._e)
                    append_children(EpiDocElement(child), child_for_target)

        append_children(source, target)
        return target

    def create_edition(
            self, 
            subtype: str | None = None, 
            lang: str | None = None) -> Edition:

        """
        Add an edition of the specified subtype to the Body
        """

        edition_elem = etree.Element(
            _tag = ns.give_ns('div', TEINS), 
            attrib = dict_remove_none({
                'type': 'edition', 
                'subtype': subtype,
                ns.give_ns('space', XMLNS): 'preserve',
                'lang': lang
            }),
            nsmap = None
        )
        
        new_edition = Edition(edition_elem)
        self._e.append(edition_elem)
        return new_edition

    def edition_by_subtype(self, subtype: str | None) -> Edition | None:

        """
        Return any edition with the required subtype 
        parameter. If subtype is None, tries to return
        an edition that has no subtype attribute.
        """

        # Find the edition with the correct subtype.
        # There should only be one
        if subtype is None:
            subtype_editions = [ed for ed in self.editions(True)
                                if ed.subtype is None]
        else:
            subtype_editions = [ed for ed in self.editions(True)
                        if ed.subtype == subtype]

        return maxone(
            subtype_editions, 
            defaultval=None, 
            throw_if_more_than_one=True
        )

    def editions(self, include_transliterations=False) -> list[Edition]:

        """
        Return a list of Edition elements
        """

        editions = [Edition(edition) 
            for edition in self.get_div_descendants('edition')]

        if include_transliterations:
            return editions

        else:
            return listfilter(
                lambda ed: ed.subtype != 'transliteration', 
                editions
            )

    def token_by_id_from_edition(
            self, 
            token_id: str,
            edition_subtype: str | None) -> Token | None:
        
        """
        Return a token with a particular ID from an 
        edition with a subtype named `edition_subtype`.
        Raises a ValueError if no edition with the named
        subtype is found.

        :param edition_subtype: the name of the edition
        subtype to retrieve the token from. If None,
        returns the main edition.
        """

        edition = self.edition_by_subtype(edition_subtype)

        if edition is None:
            raise ValueError(
                f'No edition found with subtype {edition_subtype}.')

        return edition.token_by_id(token_id)
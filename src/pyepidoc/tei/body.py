from __future__ import annotations
from typing import Literal

from lxml import etree
from lxml.etree import _Element

from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.metadata.resp_stmt import RespStmt
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.epidoc.edition_elements.edition import Edition
from pyepidoc.epidoc.token import Token

from pyepidoc.xml.namespace import Namespace as ns

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.enums import (
    StandoffEditionElements, 
    ContainerStandoffEditionType
)
from pyepidoc.shared.iterables import maxone, listfilter
from pyepidoc.shared.dicts import dict_remove_none


class Body(EditionElement):    

    """
    Provides services for the <body> element of the EpiDoc file
    """

    def __init__(
        self, 
        e: _Element | EditionElement | XmlElement
    ) -> None:
        
        super().__init__(e, False)
        body_tag = ns.give_ns('body', TEINS)

        if e.e.tag != body_tag:
            raise ValueError(f'Cannot make <body> element from '
                             f'<{self.tag}> element.')

    def copy_lemmatizable_to_lemmatized_edition(
            self,
            source: Edition,
            target: Edition) -> Edition:
        
        """
        Copies the elements due to appear in the lemmatized edition.

        NB this method does not actually carry out the
        lemmatization.

        :param tags_to_include: a list of tag names (no namespaces)
        to include in the copy. If this is None, all elements are copied.
        """

        def append_items(
                source_elem: EditionElement, 
                target_elem: EditionElement) -> None:
            
            """
            Recursive function appending children of elements
            to the new Edition.
            """

            for child in source_elem.child_elems:
                
                child_copy = child.deepcopy()

                if child.tag.name in ContainerStandoffEditionType.values() and child.tag.name != 'ab':
                    child_copy.remove_children()
                    child_copy.remove_attr('id', XMLNS)
                    target_elem._e.append(child_copy._e)
                    append_items(EditionElement(child), EditionElement(child_copy))

                elif child.tag.name == 'ab':
                    ab = child
                    ab_copy = child_copy
                    ab_copy.remove_children()
                    target_elem._e.append(child_copy._e)
                    
                    for desc in ab.descendant_elements:
                        representable = Token(desc).representable_cls_inst
                        if desc.localname in StandoffEditionElements and representable is None:
                            breakpoint()
                            raise ValueError(f'{desc} should have a representable instance.')
                        if desc.localname in StandoffEditionElements and representable is not None:
                            desc_copy_token = representable.simple_lemmatized_edition_element    
                            desc_copy_token.remove_attr('id', XMLNS)
                            ab_copy._e.append(desc_copy_token.e)   

        append_items(source, EditionElement(target))
        return target

    def append_new_edition(
            self, 
            subtype: str | None = None, 
            lang: str | None = None,
            resp_stmts: RespStmt | list[RespStmt] | None = None,
            xmlspace_preserve: Literal['preserve', None] = None) -> Edition:

        """
        Add an edition of the specified subtype to the Body,
        and insert it directly after the main edition.
        """
        initials = None
        # Generate initials
        if isinstance(resp_stmts, RespStmt):
            initials = '#' + resp_stmts.initials if resp_stmts.initials else None
        elif isinstance(resp_stmts, list):
            initials = ' '.join(('#' + resp_stmt.initials if resp_stmt.initials else '') for resp_stmt in resp_stmts)
            if initials.strip() == '':
                initials = None

        # Create the edition element
        edition_elem: _Element = etree.Element(
            _tag = ns.give_ns('div', TEINS), 
            attrib = dict_remove_none({
                'type': 'edition', 
                'subtype': subtype,
                ns.give_ns('space', XMLNS): xmlspace_preserve,
                'lang': lang,
                'resp': initials
            }),
            nsmap = None
        )
        
        new_edition = Edition(edition_elem)

        # Insert the new edition after the main edition
        main_edition = self.edition_by_subtype(None)
        if main_edition is None:
            raise ValueError("No main edition present.")
        
        main_edition_idx = self._e.index(main_edition._e, None, None)
        self._e.insert(main_edition_idx + 1, edition_elem)
        return new_edition

    def edition_by_subtype(self, subtype: str | None) -> Edition | None:

        """
        Return any edition with the required subtype 
        parameter. If subtype is None, tries to return
        an edition that has no subtype attribute, i.e.
        the 'main' edition.
        """

        # Find the edition with the correct subtype.
        # There should only be one
        if subtype is None:
            subtype_editions = [ed for ed in self.editions(True)
                                if ed.subtype is None]
        else:
            subtype_editions = [ed for ed in self.editions(True)
                        if ed.subtype == subtype]

        try:
            return maxone(
                subtype_editions, 
                defaultval=None, 
                throw_if_more_than_one=False
            )
        except ValueError as e:
            raise ValueError(f"There is more than one edition present "
                             f"with the subtype {subtype}.")

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

        return edition.token_by_xml_id(token_id)
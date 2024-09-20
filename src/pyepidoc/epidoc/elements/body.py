
from __future__ import annotations

from lxml.etree import _Element

from pyepidoc.xml.baseelement import BaseElement
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc.epidoc.elements.edition import Edition

from pyepidoc.shared.utils import maxone, listfilter
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
        
        if e.tag.name != 'body':
            raise ValueError(f'Cannot make <body> element from '
                             f'<{self.tag}> element.')
        
    
    def edition_by_subtype(self, subtype: str) -> Edition | None:

        """
        Return any edition with the required subtype 
        parameter.
        """

        # Find the edition with the correct subtype.
        # There should only be one
        subtype_editions = [ed for ed in self.editions(True)
                    if ed.subtype == subtype]

        return maxone(
            subtype_editions, 
            defaultval=None, 
            throw_if_more_than_one=True)

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
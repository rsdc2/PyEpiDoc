from __future__ import annotations
from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from .idno import Idno

class PublicationStmt(EpiDocElement):
    """
    The <publicationStmt> node, including collections of
    <publicationStmt>
    """

    @property
    def idnos(self) -> list[Idno]:

        elements = self.child_elements_by_local_name('idno')
        return list(map(Idno, elements))

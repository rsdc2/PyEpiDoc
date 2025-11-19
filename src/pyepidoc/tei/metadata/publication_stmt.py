from __future__ import annotations
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.shared.iterables import maxone
from .idno import Idno


class PublicationStmt(EditionElement):
    """
    The <publicationStmt> node, including collections of
    <publicationStmt>
    """

    def append_idno(self, idno: Idno) -> Idno:
        self._e.append_node(idno)
        return idno

    @property
    def idnos(self) -> list[Idno]:
        elements = self._e.child_elements_by_local_name('idno')
        return list(map(Idno, elements))
    
    def get_idno_by_type(self, idno_type: str) -> Idno | None:
        matches = [idno for idno in self.idnos 
                   if idno.type == idno_type]
        return maxone(matches, None, True)
    
    def set_idno_by_type(self, idno_type: str, value: str) -> None:
        idno = self.get_idno_by_type(idno_type)
        if idno is None:
            idno_element = EditionElement.create('idno', {'type': idno_type})
            self.append_idno(Idno(idno_element))
            return
        idno.value = value


        




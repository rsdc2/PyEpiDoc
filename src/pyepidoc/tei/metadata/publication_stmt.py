from __future__ import annotations
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.shared.iterables import maxone
from .idno import Idno


class PublicationStmt(TeiElement):
    """
    The `<publicationStmt>` node, including collections of
    `<publicationStmt>`
    """

    @property
    def authority(self) -> str | None:
        if self.authority_element is None:
            return None
        return self.authority_element._e.text
    
    @authority.setter
    def authority(self, value: str | None):
        if self.authority_element is None:
            self._insert_authority(value)
        if self.authority_element is None:
            raise ValueError('No authority element present, and PyEpidoc failed to add one')
        self.authority_element._e.text = value

    @property
    def authority_element(self) -> TeiElement | None:
        authority_element = self._e.child_element_by_local_name('authority')
        if authority_element is None:
            return None
        return TeiElement(authority_element)

    def _insert_authority(self, value: str | None) -> PublicationStmt:
        if self._e.child_element_by_local_name('authority') is None:
            authority = TeiElement.create('authority')
            authority._e.text = value
            self._e.append_node(authority._e)
        return self
    
    @property
    def idnos(self) -> list[Idno]:
        elements = self._e.child_elements_by_local_name('idno')
        return list(map(Idno, elements))
    
    def get_idno_by_type(self, idno_type: str) -> Idno | None:
        matches = [idno for idno in self.idnos 
                   if idno.type == idno_type]
        return maxone(matches, None, True)
    
    def _append_idno(self, idno: Idno) -> Idno:
        self._e.append_node(idno)
        return idno

    def set_idno_by_type(self, idno_type: str, value: str) -> None:
        idno = self.get_idno_by_type(idno_type)
        if idno is None:
            idno_element = TeiElement.create('idno', {'type': idno_type})
            self._append_idno(Idno(idno_element))
            return
        idno.value = value
        




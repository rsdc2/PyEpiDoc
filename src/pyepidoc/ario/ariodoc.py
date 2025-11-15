from typing import override

from pyepidoc.tei.tei_doc import TeiDoc
from .ariobody import ArioBody


class ArioDoc(TeiDoc):
    
    @override
    @property
    def body(self) -> ArioBody:

        """
        Return the body element of the XML file
        as a `Body` object.
        """
        
        body_element = super().body.e
        return ArioBody(body_element)
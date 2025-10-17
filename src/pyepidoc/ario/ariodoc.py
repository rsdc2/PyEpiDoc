from typing import override

from pyepidoc.epidoc.epidoc import EpiDoc
from .ariobody import ArioBody

class ArioDoc(EpiDoc):
    
    @override
    @property
    def body(self) -> ArioBody:

        """
        Return the body element of the XML file
        as a `Body` object.
        """
        
        body_element = super().body.e
        return ArioBody(body_element)
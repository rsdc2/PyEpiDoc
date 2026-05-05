from typing import overload
from pyepidoc.xml.xml_node_types import XmlElement

class ProielElement:
    _e: XmlElement

    def __init__(self, e: XmlElement):
        error_msg = (f'Expected type is XmlElement or TeiElement '
                     f'type or None. Actual type is {type(e)}.')
        
        if not isinstance(e, XmlElement):
            raise TypeError(error_msg)
        elif isinstance(e, XmlElement):
            self._e = e
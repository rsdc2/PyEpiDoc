from lxml.etree import _Element
from pyepidoc.epidoc.edition_element import TokenizableElement
from pyepidoc.epidoc.utils import localname
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement

class Hi(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <hi> elements.
    """

    def __init__(self, e: _Element | XmlElement | TeiElement | TokenizableElement):
        super().__init__(e)

        if self._e.localname != 'hi':
            raise TypeError('Element should be <hi>.')

    @property
    def leiden_form(self) -> str:
        from .expan import Expan
        from .abbr import Abbr
        from .ex import Ex
        from .am import Am
        from .num import Num
        from .surplus import Surplus

        element_classes: dict[str, type] = {
            'expan': Expan,
            'abbr': Abbr,
            'ex': Ex,
            'am': Am,
            'num': Num,
            'surplus': Surplus
        }
        
        return leiden_str_from_children(self._e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .abbr import Abbr
        from .ex import Ex
        from .am import Am
        from .num import Num
        from .surplus import Surplus

        element_classes: dict[str, type] = {
            'expan': Expan,
            'abbr': Abbr,
            'ex': Ex,
            'am': Am,
            'num': Num,
            'surplus': Surplus
        }
        
        return normalized_str_from_children(self._e, element_classes, 'node')        
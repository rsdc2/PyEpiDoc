from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.utils import leiden_form_from_children, normalized_form_from_children
from pyepidoc.xml.xml_node_types import XmlElement
from pyepidoc.tei.tei_element import TeiElement


class Hi(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <hi> elements.
    """

    def __init__(self, e: XmlElement | TeiElement | TokenizableElement):
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
        
        return leiden_form_from_children(self._e, element_classes)
    
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
        
        return normalized_form_from_children(self._e, element_classes, 'node')        
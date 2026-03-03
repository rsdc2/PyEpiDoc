from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.utils import leiden_form_from_children, normalized_form_from_children

from pyepidoc.xml.lxml_node_types import XmlElement
from pyepidoc.tei.tei_element import TeiElement

from .orig import Orig
from .reg import Reg
from .sic import Sic
from .corr import Corr


class Choice(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <choice> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):

        super().__init__(e)

        if self._e.localname != 'choice':
            raise TypeError(f'Element should be <choice> not {self._e.localname}.')

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan,
            'orig': Orig,
            'reg': Reg,
            'sic': Sic,
            'corr': Corr
        }
    
        return leiden_form_from_children(self._e, element_classes)
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan,
            'orig': Orig,
            'reg': Reg,
            'sic': Sic,
            'corr': Corr
        }        

        return normalized_form_from_children(self._e, element_classes, 'node')

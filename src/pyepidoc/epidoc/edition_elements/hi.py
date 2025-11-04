from lxml.etree import _Element
from ..edition_element import EditionElement
from pyepidoc.epidoc.utils import localname
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children


class Hi(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <hi> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if localname(e) != 'hi':
            raise TypeError(f'Element should be of type <hi>, '
                            f'but is of type <{localname(e)}>.')

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
        
        return leiden_str_from_children(self.e, element_classes, 'node')
    
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
        
        return normalized_str_from_children(self.e, element_classes, 'node')        
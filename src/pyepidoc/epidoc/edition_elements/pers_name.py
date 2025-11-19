from lxml.etree import _Element
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.epidoc.utils import (
    leiden_str_from_children, 
    normalized_str_from_children
)


class PersName(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <roleName> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self._e.localname != 'persName':
            raise TypeError('Element should be <persName>.')

    def __repr__(self) -> str:
        return f'PersName({self.leiden_form}, type: "{self.pers_name_type}")'

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan
        from .hi import Hi
        from .name import Name
        from .num import Num
        from .surplus import Surplus
        from .w import W

        element_classes: dict[str, type] = {
            'expan': Expan,
            'hi': Hi,
            'name': Name,
            'num': Num,
            'surplus': Surplus,
            'w': W
        }
        
        return leiden_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .hi import Hi
        from .w import W
        from .name import Name
        from .num import Num
        from .surplus import Surplus


        element_classes: dict[str, type] = {
            'expan': Expan,
            'hi': Hi,
            'name': Name,
            'num': Num,
            'surplus': Surplus,
            'w': W
        }
        
        return normalized_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )
    
    @property
    def pers_name_type(self) -> str:
        return self.get_attrib("type") or ""
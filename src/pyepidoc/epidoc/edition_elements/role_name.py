from lxml.etree import _Element
from ..edition_element import EditionElement
from ..utils import (
    leiden_str_from_children, 
    normalized_str_from_children
)


class RoleName(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <roleName> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'roleName':
            raise TypeError('Element should be <roleName>.')

    def __repr__(self) -> str:
        return f'RoleName({self.leiden_form}, type: "{self.role_name_type}", subtype: "{self.role_name_subtype})'

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
    def role_name_type(self) -> str:
        return self.get_attrib("type") or ""
    
    @property
    def role_name_subtype(self) -> str:
        return self.get_attrib("subtype") or ""
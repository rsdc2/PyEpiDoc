from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.epidoc.utils import (
    leiden_str_from_children, 
    normalized_str_from_children
)


class RoleName(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <roleName> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'roleName':
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
            self._e, 
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
            self._e, 
            element_classes, 
            'node'
        )
    
    @property
    def role_name_type(self) -> str:
        return self.get_attr("type") or ""
    
    @property
    def role_name_subtype(self) -> str:
        return self.get_attr("subtype") or ""
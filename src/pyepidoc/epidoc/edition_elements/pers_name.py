from __future__ import annotations
import re
from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.lxml_node_types import XmlElement
from pyepidoc.epidoc.utils import (
    leiden_form_from_children, 
    normalized_form_from_children,
    final_leiden_str_process
)

class PersName(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <roleName> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):

        super().__init__(e)

        if self._e.localname != 'persName':
            raise TypeError(f'Element should be <persName> not {self._e.localname}.')

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
        from .g import G
        from .lb import Lb
        from .role_name import RoleName
        from .supplied import Supplied
        from .gap import Gap

        element_classes: dict[str, type] = {
            'expan': Expan,
            'hi': Hi,
            'name': Name,
            'num': Num,
            'surplus': Surplus,
            'w': W,
            'g': G,
            'persName': PersName,
            'roleName': RoleName,
            'lb': Lb,
            'supplied': Supplied,
            'gap': Gap
        }
        
        leiden = leiden_form_from_children(self._e, element_classes)

        with_normalized_spaces = re.sub('\s+', ' ', leiden)
        return with_normalized_spaces
    
    @property
    def finalised_leiden_form(self) -> str:
        return final_leiden_str_process(self.leiden_form)
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .hi import Hi
        from .w import W
        from .name import Name
        from .num import Num
        from .surplus import Surplus
        from .g import G

        element_classes: dict[str, type] = {
            'expan': Expan,
            'hi': Hi,
            'name': Name,
            'num': Num,
            'surplus': Surplus,
            'w': W,
            'g': G
        }
        
        return normalized_form_from_children(self._e, element_classes, 'node')
    
    @property
    def pers_name_type(self) -> str:
        return self.get_attr('type') or ''
    
    @property
    def pers_names(self) -> list[PersName]:
        pers_name_elems = self._e.descendant_elements_by_local_name('persName')
        pers_names = [PersName(name) for name in pers_name_elems]
        return pers_names
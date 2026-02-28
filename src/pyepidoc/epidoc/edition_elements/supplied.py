from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.utils import leiden_form_from_children, normalized_form_from_children
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement


class Supplied(TokenizableElement):
    """
    Represents <supplied> elements
    """

    def __init__(self, e: TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'supplied':
            raise TypeError(f'Element should be <unclear> not {self._e.localname}.')

    @property
    def leiden_form(self) -> str:
        
        from .abbr import Abbr
        from .am import Am
        from .ex import Ex
        from .expan import Expan
        from .role_name import RoleName
        from .g import G
        from .name import Name
        from .w import W
        from .num import Num

        element_classes: dict[str, type] = {
            'abbr': Abbr,
            'am': Am,
            'ex': Ex,
            'expan': Expan,
            'roleName': RoleName,
            'g': G,
            'name': Name,
            'w': W,
            'num': Num
        }
        
        return ''.join([
            '[',
            leiden_form_from_children(self._e, element_classes),
            ']'
        ])
    
    @property
    def normalized_form(self) -> str:
        return normalized_form_from_children(self._e, dict(), 'node')
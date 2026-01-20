from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement


class Supplied(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
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

        element_classes: dict[str, type] = {
            'abbr': Abbr,
            'am': Am,
            'ex': Ex,
            'expan': Expan,
            'roleName': RoleName
        }
        
        return ''.join([
            '[',
            leiden_str_from_children(self._e, element_classes, 'node'),
            ']'
        ])
    
    @property
    def normalized_form(self) -> str:
        return normalized_str_from_children(self._e, dict(), 'node')
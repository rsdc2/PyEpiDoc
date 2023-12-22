from lxml.etree import _Element
from ..element import EpiDocElement
from ..utils import leiden_str_from_children


class Supplied(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.local_name != 'supplied':
            raise TypeError('Element should be <supplied>.')

    def __str__(self) -> str:
        
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
            leiden_str_from_children(self.e, element_classes, 'node'),
            ']'
        ])
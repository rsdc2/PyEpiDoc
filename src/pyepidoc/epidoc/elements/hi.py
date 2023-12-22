from lxml.etree import _Element
from ..element import EpiDocElement
from pyepidoc.epidoc.utils import local_name
from pyepidoc.epidoc.utils import leiden_str_from_children


class Hi(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <hi> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if local_name(e) != 'hi':
            raise TypeError(f'Element should be of type <hi>, '
                            f'but is of type <{local_name(e)}>.')


    def __str__(self) -> str:
        from .expan import Expan
        from .abbr import Abbr
        from .ex import Ex
        from .am import Am

        element_classes: dict[str, type] = {
            'expan': Expan,
            'abbr': Abbr,
            'ex': Ex,
            'am': Am
        }
        
        return leiden_str_from_children(self.e, element_classes, 'node')
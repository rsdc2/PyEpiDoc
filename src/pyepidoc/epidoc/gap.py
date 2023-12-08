from lxml.etree import _Element
from .element import EpiDocElement


class Supplied(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <gap> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.local_name != 'gap':
            raise TypeError('Element should be <gap>.')

    def __str__(self) -> str:
        return '[-?-]'
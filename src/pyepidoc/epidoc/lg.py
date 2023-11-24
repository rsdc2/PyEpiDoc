from __future__ import annotations
from typing import Optional, Sequence, cast

from copy import deepcopy
from functools import reduce
from lxml.etree import _Element 

from .element import EpiDocElement
from .textpart import TextPart
from .token import Token
from .expan import Expan
from .epidoc_types import (
    TokenCarrier, 
    AtomicTokenType, 
    CompoundTokenType,
    SpaceSeparated,
    NoSpace
)
from pyepidoc.shared_types import SetRelation
from ..utils import head

from ..xml import BaseElement
from ..utils import update_set_inplace, flatlist, flatten
from ..constants import XMLNS

from .ab import Ab


class Lg(Ab):

    """
    <lg> = line group (for poetic texts)
    """

    def __init__(self, e:Optional[_Element | EpiDocElement | BaseElement]=None):

        if type(e) not in [_Element, EpiDocElement, BaseElement] and e is not None:
            raise TypeError('e should be _Element or Element type, or None.')

        if type(e) is _Element:
            self._e = e
        elif type(e) is EpiDocElement:
            self._e = e.e
        elif type(e) is BaseElement:
            self._e = e.e

        if self.tag.name != 'lg':
            raise TypeError('Element should be of type <lg>.')


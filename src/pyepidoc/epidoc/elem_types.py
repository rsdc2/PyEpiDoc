from __future__ import annotations
from typing import Optional
from lxml.etree import _Element, _ElementUnicodeResult

from .am import Am
from .ex import Ex
from .abbr import Abbr
from .supplied import Supplied


element_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'ex': Ex,
    'supplied': Supplied
}



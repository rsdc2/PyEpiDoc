from __future__ import annotations

from typing import Optional, Union
from lxml.etree import _Element # type: ignore

from ..base.namespace import Namespace

from .abbr import Abbr
from .ex import Ex
from .expan import Expan


element_classes: dict[str, type] = {
    'ex': Ex,
    'abbr': Abbr
}


def get_elem_obj(e: _Element) -> Optional[Union[Expan, Abbr ,Ex]]:
    tag = Namespace.remove_ns(e.tag)
    cls = element_classes.get(tag, None)

    if cls is None:
        return None

    return cls(e)

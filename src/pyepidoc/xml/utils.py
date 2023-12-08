from __future__ import annotations

from lxml.etree import _Element, _ElementUnicodeResult


def local_name(node: _Element | _ElementUnicodeResult) -> str:
    """
    Return the local name of a node.
    Returns '#text' if node is |_ElementUnicodeResult|
    """
    if type(node) is _ElementUnicodeResult:
        return '#text'
    
    return str(node.xpath('local-name(.)'))
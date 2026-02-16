from __future__ import annotations

from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml import XmlElement
from pyepidoc.epidoc.token_container import TokenContainer


class Ab(TokenContainer):

    """
    The Ab class provides services for interaction with 
    a documents <ab> elements.
    <ab> stands for 'anonymous block', see 
    https://epidoc.stoa.org/gl/latest/ref-ab.html:

    "<ab> (anonymous block) contains any arbitrary component-level 
    unit of text, acting as an anonymous container for 
    phrase or inter level elements analogous to, 
    but without the semantic baggage of, a paragraph." 
    (last accessed 2023-03-27)

    From the perspective of accessing / creating tokens,
    <ab> is the domain of tokens.
    The Ab class therefore carries the method for 
    actually doing the tokenization / collecting the tokens.
    Equivalent methods in the Edition and EpiDocCorpus
    classes call these methods for each <ab> contained
    within them.
    """

    def __init__(self, e: TeiElement | XmlElement):
        super().__init__(e)
        
        if self._e.tag.name != 'ab':
            raise TypeError('Element should be of type <ab>.')

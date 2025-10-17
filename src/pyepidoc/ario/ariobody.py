from pyepidoc.shared.iterables import maxone, listfilter

from pyepidoc.epidoc.body import Body
from pyepidoc.epidoc.edition_elements.edition import Edition

class ArioBody(Body):
    
    def editions(self, include_transliterations=False) -> list[Edition]:

        """
        Return a list of Edition elements
        """

        editions = [Edition(edition) 
            for edition in self.get_div_descendants('edition')]

        if include_transliterations:
            return editions
        else:
            return listfilter(
                lambda ed: ed.subtype != 'transliteration', 
                editions
            )
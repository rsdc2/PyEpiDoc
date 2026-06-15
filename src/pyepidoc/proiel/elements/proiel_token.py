from .proiel_element import ProielElement
from .proiel_morphology import ProielMorphology
from .proiel_bible_ref import ProielBibleRef

class ProielToken(ProielElement):

    @property
    def id_str(self) -> str:
        id_str = self._e.get_attr('id')
        if id_str is None:
            raise ValueError('ID cannot be None')
        return id_str

    @property
    def citation_part(self) -> str:
        citation_part = self._e.get_attr('citation-part')
        if citation_part is None:
            return ''
        return citation_part
    
    @property
    def citation(self) -> ProielBibleRef:
        return ProielBibleRef.from_proiel_citation(self.citation_part)
    
    @property
    def form(self) -> str | None:
        form = self._e.get_attr('form')
        return form
    
    @property
    def lemma(self) -> str:
        lemma = self._e.get_attr('lemma')
        if lemma is None:
            return ''
        return lemma
    
    @property
    def part_of_speech(self) -> str:
        pos = self._e.get_attr('part-of-speech')
        if pos is None:
            return ''
        return pos
    
    @property
    def morphology(self) -> ProielMorphology | None:
        morphology = self._e.get_attr('morphology')
        if morphology is None:
            return None
        return ProielMorphology(morphology)

    @property
    def head_id_str(self) -> str | None:
        return self._e.get_attr('head-id')
    
    @property
    def relation(self) -> str | None:
        return self._e.get_attr('relation')


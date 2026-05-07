from .proiel_element import ProielElement
from .proiel_morphology import ProielMorphology
from .proiel_bible_citation import ProielBibleCitation

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
            raise ValueError('Citation part cannot be None')
        return citation_part
    
    @property
    def citation(self) -> ProielBibleCitation:
        return ProielBibleCitation.from_str(self.citation_part)
    
    @property
    def form(self) -> str:
        form = self._e.get_attr('form')
        if form is None:
            raise ValueError('Form cannot be None')
        return form
    
    @property
    def lemma(self) -> str:
        lemma = self._e.get_attr('lemma')
        if lemma is None:
            raise ValueError('Lemma cannot be None')
        return lemma
    
    @property
    def part_of_speech(self) -> str:
        pos = self._e.get_attr('part-of-speech')
        if pos is None:
            raise ValueError('Part of speech cannot be None')
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


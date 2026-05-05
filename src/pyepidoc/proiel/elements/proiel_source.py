from .proiel_element import ProielElement
from .proiel_div import ProielDiv
from .proiel_token import ProielToken
from .proiel_sentence import ProielSentence
from .has_proiel_sentences import HasProielSentences

class ProielSource(HasProielSentences):

    @property
    def divs(self) -> list[ProielDiv]:
        div_elems = self._e.child_elements_by_local_name('div')
        divs = [ProielDiv(div) for div in div_elems]
        return divs
    
    @property
    def sentences(self) -> list[ProielSentence]:
        sentences = []
        for d in self.divs:
            sentences.extend(d.sentences)
        return sentences
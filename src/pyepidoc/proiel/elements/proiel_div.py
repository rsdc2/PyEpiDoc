from .proiel_sentence import ProielSentence
from .has_proiel_sentences import HasProielSentences


class ProielDiv(HasProielSentences):

    @property
    def id_str(self) -> str:
        id_str = self._e.get_attr('id')
        if id_str is None:
            raise ValueError('ID cannot be None')
        return id_str

    @property
    def sentences(self) -> list[ProielSentence]:
        sentence_elems = self._e.child_elements_by_local_name('sentence')
        sentences = [ProielSentence(sentence) for sentence in sentence_elems]
        return sentences

    @property
    def title(self) -> str:
        title = self._e.get_attr('id')
        if title is None:
            raise ValueError('Title cannot be None')
        return title
    

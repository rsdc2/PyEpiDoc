from .proiel_sentence import ProielSentence
from .has_proiel_sentences import HasProielSentences
from .proiel_verse import ProielVerse
from .proiel_bible_ref import ProielBibleRef
from .proiel_token import ProielToken

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
        
    def verse(self, verse: int) -> ProielVerse | None:
        acc: list[ProielToken] = []
        for token in self.tokens:
            if token.citation.verse == verse:
                acc.append(token)

        proiel_verse = ProielVerse(acc[0].citation.book, verse, acc)
        return proiel_verse
    

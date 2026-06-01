from pyepidoc.shared.bible_refs.bible_token_ref import BibleTokenRef

from .proiel_sentence import ProielSentence
from .has_proiel_sentences import HasProielSentences
from .proiel_verse import ProielVerse
from .proiel_bible_ref import ProielBibleRef
from .proiel_verse_token import ProielVerseToken

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
        tokens_in_verse: list[ProielVerseToken] = []
        verse_token_counter = 1
        for token in self.tokens:
            if token.citation.verse == verse:
                verse_token = ProielVerseToken(token, verse_token_counter)
                verse_token_counter += 1
                tokens_in_verse.append(verse_token)
            elif len(tokens_in_verse) > 0:
                break

        book = tokens_in_verse[0].proiel_token.citation.book
        proiel_verse = ProielVerse(book, verse, tokens_in_verse)
        return proiel_verse
    

from pyepidoc.shared.bible_refs.bible_book import BibleBook
from .proiel_div import ProielDiv
from .proiel_verse import ProielVerse


class ProielChapter(ProielDiv):

    @property
    def book_ref(self) -> BibleBook:
        return self.sentence_tokens[0].citation.book
    
    @property
    def chapter_ref(self) -> int:
        return self.sentence_tokens[0].citation.chapter
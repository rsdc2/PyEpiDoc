from pyepidoc.shared.bible_refs.bible_book import BibleBook
from .proiel_div import ProielDiv

class ProielChapter(ProielDiv):

    @property
    def book_ref(self) -> BibleBook:
        return self.tokens[0].citation.book
    
    @property
    def chapter(self) -> int:
        return self.tokens[0].citation.chapter
    
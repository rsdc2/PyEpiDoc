from __future__ import annotations
from dataclasses import dataclass
from .bible_book import BibleBook


@dataclass
class BibleRef:
    book: BibleBook
    chapter: int
    verse: int
    verse_token_id: int

    def with_verse_token_id(self, verse_token_id: int) -> BibleRef:
        return BibleRef(self.book, self.chapter, self.verse, verse_token_id)
    
    def __str__(self) -> str:
        verse_token_id_str = '' if self.verse_token_id == 0 else '.' + str(self.verse_token_id)
        return f'{str(self.book)} {self.chapter}:{self.verse}{verse_token_id_str}'

    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BibleRef):
            return False
        
        return self.book == other.book and \
            self.chapter == other.chapter and \
                self.verse == other.verse and \
                    self.verse_token_id == other.verse_token_id
from __future__ import annotations
from dataclasses import dataclass
from .bible_book import BibleBook


@dataclass
class BibleRef:
    book: BibleBook
    chapter: int
    verse: int

    def __init__(self, book: str, chapter: int, verse: int):
        self.book = BibleBook(book)
        self.chapter = chapter
        self.verse = verse
    
    def verse_eq(self, other) -> bool:
        if not isinstance(other, BibleRef):
            return False
        return self.book == other.book and \
            self.chapter == other.chapter and \
                self.verse == other.verse
    
    def __str__(self) -> str:
        return f'{str(self.book)} {self.chapter}:{self.verse}'

    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BibleRef):
            return False
        
        return self.book == other.book and \
            self.chapter == other.chapter and \
                self.verse == other.verse
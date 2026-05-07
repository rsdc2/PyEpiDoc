from __future__ import annotations
from dataclasses import dataclass

@dataclass
class BibleCitation:
    book: str
    chapter: str
    verse: str
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BibleCitation):
            return False
        
        return self.book == other.book and \
            self.chapter == other.chapter and \
                self.verse == other.verse
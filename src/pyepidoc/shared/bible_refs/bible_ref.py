from dataclasses import dataclass
from .bible_book import BibleBook


@dataclass
class BibleRef:
    book: BibleBook
    chapter: str
    verse: str
    verse_token_id: str

    @property
    def chapter_int(self) -> int:
        return int(self.chapter)
    
    @property
    def verse_int(self) -> int:
        return int(self.verse)
    
    @property
    def verse_token_id_int(self) -> int:
        if self.verse_token_id.strip() in ['', '0', None]:
            return 0
        return int(self.verse_token_id) 
    
    def __str__(self) -> str:
        verse_token_id_str = '' if self.verse_token_id_int == 0 else '.' + str(self.verse_token_id_int)
        return f'{str(self.book)} {self.chapter_int}:{self.verse_int}{verse_token_id_str}'

    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BibleRef):
            return False
        
        return self.book == other.book and \
            self.chapter == other.chapter and \
                self.verse == other.verse and \
                    self.verse_token_id == other.verse_token_id
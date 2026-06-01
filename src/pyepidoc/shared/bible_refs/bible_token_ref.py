from dataclasses import dataclass
from pyepidoc.shared.bible_refs.bible_ref import BibleRef


@dataclass
class BibleTokenRef:
    bible_ref: BibleRef
    verse_token_id: int

    @property 
    def book(self):
        return self.bible_ref.book
    
    @property
    def chapter(self):
        return self.bible_ref.chapter
    
    @property
    def verse(self):
        return self.bible_ref.verse

    @property
    def verse_token_id_str(self) -> str:
        return str(self.verse_token_id).rjust(5)

    def __str__(self) -> str:
        return f'{str(self.bible_ref.book)} {self.bible_ref.chapter}:{self.bible_ref.verse}.{self.verse_token_id}'

    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BibleTokenRef):
            return False
        
        return self.book == other.book and \
            self.chapter == other.chapter and \
                self.verse == other.verse and \
                    self.verse_token_id == other.verse_token_id
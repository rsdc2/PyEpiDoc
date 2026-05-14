from __future__ import annotations
from dataclasses import dataclass
from pyepidoc.shared.bible_refs.bible_ref import BibleRef
from pyepidoc.shared.bible_refs.bible_book import BibleBook


@dataclass
class ProielBibleRef(BibleRef):
    @staticmethod
    def from_proiel_citation(citation: str) -> ProielBibleRef:
        space_split = citation.split(' ')
        book = space_split[0]
        bible_book = BibleBook(book)
        chapter_verse = space_split[1].split('.')
        chapter = chapter_verse[0]
        verse = chapter_verse[1]
        return ProielBibleRef(bible_book, int(chapter), int(verse), 0)
    
    



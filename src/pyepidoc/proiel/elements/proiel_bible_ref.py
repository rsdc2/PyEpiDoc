from __future__ import annotations
from dataclasses import dataclass
from pyepidoc.shared.bible_refs.bible_ref import BibleRef
from pyepidoc.shared.bible_refs.bible_book import BibleBook


@dataclass
class ProielBibleRef(BibleRef):
    @staticmethod
    def from_proiel_citation(citation: str) -> ProielBibleRef:
        """
        e.g. JOHN 1.1
        """
        if citation.strip() == '':
            return EmptyProielBibleRef()
        space_split = citation.split(' ')
        book = space_split[0]
        bible_book = BibleBook(book)
        chapter_verse = space_split[1].split('.')
        chapter = chapter_verse[0]
        verse = chapter_verse[1]
        return ProielBibleRef(bible_book, int(chapter), int(verse))
    
    @staticmethod
    def from_citation(citation: str) -> ProielBibleRef:
        """
        e.g. John 1:1
        """
        verse_separator = '.' if '.' in citation else ':'
        space_split = citation.split(' ')
        book = space_split[0]
        bible_book = BibleBook(book)
        chapter_verse = space_split[1].split(verse_separator)
        chapter = chapter_verse[0]
        verse = chapter_verse[1]
        return ProielBibleRef(bible_book, int(chapter), int(verse))

@dataclass
class EmptyProielBibleRef(ProielBibleRef):
    def __init__(self):
        pass

    
    



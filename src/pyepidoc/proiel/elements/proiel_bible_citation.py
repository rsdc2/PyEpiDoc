from __future__ import annotations
from dataclasses import dataclass
from pyepidoc.shared.bible_citation import BibleCitation


@dataclass
class ProielBibleCitation(BibleCitation):
    @staticmethod
    def from_str(citation: str) -> ProielBibleCitation:
        space_split = citation.split(' ')
        book = space_split[0]
        chapter_verse = space_split[1].split('.')
        chapter = chapter_verse[0]
        verse = chapter_verse[1]
        return ProielBibleCitation(book, chapter, verse)
    



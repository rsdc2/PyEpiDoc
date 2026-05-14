from dataclasses import dataclass
from typing import Iterable
from pyepidoc.shared.bible_refs.bible_book import BibleBook
from .proiel_verse import ProielVerse
from .proiel_token import ProielToken


@dataclass
class ProielChapter:
    book_ref: BibleBook
    verses: list[ProielVerse]

    @property
    def tokens(self) -> Iterable[ProielToken]:
        for verse in self.verses:
            for token in verse.tokens:
                yield token
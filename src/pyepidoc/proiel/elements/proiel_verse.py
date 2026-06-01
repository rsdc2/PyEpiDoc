from typing import Iterable
from dataclasses import dataclass
from pyepidoc.shared.bible_refs.bible_book import BibleBook
from .proiel_token import ProielToken
from .proiel_verse_token import ProielVerseToken


@dataclass
class ProielVerse:
    """
    Abstract structure representing a verse in PROIEL. 
    This has no counterpart in the XML structure.
    """

    book_ref: BibleBook
    verse_ref: int
    tokens: list[ProielVerseToken]
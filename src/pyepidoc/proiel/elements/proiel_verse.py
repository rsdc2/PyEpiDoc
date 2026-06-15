from dataclasses import dataclass
from pyepidoc.shared.bible_refs.bible_book import BibleBook
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

    @property
    def text(self) -> str:
        return ' '.join([token.form for token in self.tokens 
                         if token.form.strip() != ''])

    @property
    def key_form_pairs(self) -> tuple[str, str]:
        return [(token.verse_token_id, token.form) for token in self.tokens]
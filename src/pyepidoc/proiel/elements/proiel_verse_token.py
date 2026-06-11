from pyepidoc.shared.bible_refs.bible_token_ref import BibleTokenRef

from dataclasses import dataclass
from .proiel_token import ProielToken


@dataclass
class ProielVerseToken:
    proiel_token: ProielToken
    verse_token_id: int

    @property
    def form(self) -> str:
        return self.proiel_token.form

    @property
    def token_ref(self) -> BibleTokenRef:
        return BibleTokenRef(self.proiel_token.citation, self.verse_token_id)
    

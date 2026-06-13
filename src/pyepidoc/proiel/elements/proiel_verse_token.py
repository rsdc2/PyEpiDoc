from pyepidoc.shared.bible_refs.bible_token_ref import BibleTokenRef
from .proiel_morphology import ProielMorphology

from dataclasses import dataclass
from .proiel_token import ProielToken


@dataclass
class ProielVerseToken:
    proiel_token: ProielToken
    verse_token_id: int

    @property
    def csv_str(self) -> str:
        return f'{self.id_str},{self.form},{self.lemma},{self.tense},{self.mood},{self.voice}'

    @property
    def id_str(self) -> str:
        return self.token_ref.id_str

    @property
    def form(self) -> str:
        return self.proiel_token.form

    @property
    def lemma(self) -> str:
        return self.proiel_token.lemma

    @property
    def mood(self) -> str:
        if self.morphology is None:
            return ''
        return self.morphology.mood
    
    @property
    def morphology(self) -> ProielMorphology | None:
        return self.proiel_token.morphology
    
    @property
    def morphology_str(self) -> str:
        if self.morphology is None:
            return ''
        return self.morphology._morph_str

    @property
    def tense(self) -> str:
        if self.morphology is None:
            return ''
        return self.morphology.tense

    @property
    def token_ref(self) -> BibleTokenRef:
        return BibleTokenRef(self.proiel_token.citation, self.verse_token_id)

    @property
    def voice(self) -> str:
        if self.morphology is None:
            return ''
        return self.morphology.voice
    

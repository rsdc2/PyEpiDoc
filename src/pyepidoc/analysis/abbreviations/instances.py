"""
Functions for providing instances of abbreviation distributions in 
an EpiDoc corpus
"""
from __future__ import annotations
from typing import Iterable, Optional, TypedDict, Literal
from functools import reduce

from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.elements.expan import Expan
from pyepidoc.shared.classes import SetRelation
from pyepidoc.epidoc.enums import AbbrType
from pyepidoc.epidoc.dom import lang, doc_id


class RawResult(TypedDict):
    isic_id: str
    expansion: str


class CountResult(TypedDict):
    frequency: int
    isic_ids: set[str]


def raw_abbreviations(
        corpus: EpiDocCorpus,
        abbr_type: Optional[AbbrType]=None, 
        language: Optional[Literal['la', 'grc']]=None
        ) -> list[RawResult]:
    """
    Generates a table of abbreviations and their frequencies
    """

    expans = corpus.expans

    if abbr_type is not None:
        filt = list(filter(lambda expan: abbr_type 
                           in expan.abbr_types, expans))
    else:
        filt = expans

    if language is not None:
        filt = list(filter(lambda expan: lang(expan) == language, filt))

    results: list[RawResult] = [{
        'isic_id': doc_id(expan) or 'None', 
        'expansion': str(expan)
        } for expan in filt]

    return results


def abbreviation_count(
        raw: list[RawResult]
    ) -> dict[str, CountResult]:

    def f(acc: dict[str, CountResult], item: RawResult) -> dict[str, CountResult]:
        expansion = item['expansion'].lower()

        if expansion in acc.keys():
            record = acc[expansion]
            record['isic_ids'].update([item['isic_id']])
            record['frequency'] += 1
            return acc
        
        acc[expansion] = {
            'frequency': 1,
            'isic_ids': {item['isic_id']}
        }

        return acc
        
    return reduce(f, raw, dict())


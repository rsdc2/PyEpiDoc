"""
Functions for analysing abbreviation distributions in 
an EpiDoc corpus
"""
from typing import Iterable
from pyepidoc import EpiDocCorpus, EpiDoc
from pyepidoc.epidoc.expan import Expan
from pyepidoc.utils import contains
from pyepidoc.shared_types import SetRelation
from pyepidoc.epidoc.funcs import lang
from copy import deepcopy

# def filter_on(expan: Expan)


def distribution_from_corpus(corpus: EpiDocCorpus) -> dict[str, int]:
    """
    Provides statistics for the distribution of 
    abbreviations in an EpiDoc corpus.
    Returned as dict
    """

    return distribution_from_expans(corpus.expans)



def distribution_from_expans(expans: Iterable[Expan]) -> dict[str, int]:
    suspensions = filter(lambda expan: expan.is_suspension, expans)
    contractions = filter(lambda expan: expan.is_contraction, expans)
    contractions_with_suspension = filter(lambda expan: expan.is_contraction_with_suspension, expans)
    multiplications = filter(lambda expan: expan.is_multiplicative, expans)

    return {
        'suspensions': len(list(suspensions)),
        'contractions': len(list(contractions)),
        'contractions_with_suspension': len(list(contractions_with_suspension)),
        'multiplations': len(list(multiplications))
    }



def expans(corpus: EpiDocCorpus) -> list[str]:
    return list(map(str, corpus.expans))


def overall_distribution_via_expans(corpus: EpiDocCorpus) -> dict[str, dict[str, int]]:

    expans = corpus.expans
    latin_expans = filter(lambda expan: lang(expan) == 'la', expans)
    greek_expans = filter(lambda expan: lang(expan) == 'grc', expans)
    other_expans = filter(lambda expan: lang(expan) not in ['la', 'grc'], expans)

    latin_stats = distribution_from_expans(list(latin_expans))
    greek_stats = distribution_from_expans(list(greek_expans))
    other_stats = distribution_from_expans(list(other_expans))

    return {
        'Greek': greek_stats,
        'Latin': latin_stats,
        'Other': other_stats
    }


def overall_distribution_via_corpus(corpus: EpiDocCorpus) -> dict[str, dict[str, int]]:
    latin = corpus.filter_by_languages(['la'])
    greek = corpus.filter_by_languages(['grc'])
    other = corpus.filter_by_languages(['la', 'grc'], SetRelation.disjoint)

    latin_stats = distribution_from_corpus(latin)
    greek_stats = distribution_from_corpus(greek)
    other_stats = distribution_from_corpus(other)

    return {
        'Greek': greek_stats,
        'Latin': latin_stats,
        'Other': other_stats
    }


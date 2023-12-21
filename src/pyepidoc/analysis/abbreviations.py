"""
Functions for analysing abbreviation distributions in 
an EpiDoc corpus
"""
from pyepidoc import EpiDocCorpus, EpiDoc
from pyepidoc.epidoc.expan import Expan
from pyepidoc.utils import contains
from pyepidoc.shared_types import SetRelation


# def filter_on(expan: Expan)


def distribution(corpus: EpiDocCorpus) -> dict[str, int]:
    """
    Provides statistics for the distribution of 
    abbreviations in an EpiDoc corpus.
    Returned as dict
    """

    expans = corpus.expans

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


def overall_distribution(corpus: EpiDocCorpus) -> dict[str, dict[str, int]]:
    latin = corpus.filter_by_languages(['la'])
    greek = corpus.filter_by_languages(['grc'])
    other = corpus.filter_by_languages(['la', 'grc'], SetRelation.disjoint)

    latin_stats = distribution(latin)
    greek_stats = distribution(greek)
    other_stats = distribution(other)

    return {
        'Greek': greek_stats,
        'Latin': latin_stats,
        'Other': other_stats
    }



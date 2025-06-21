"""
Functions for analysing abbreviation distributions in 
an EpiDoc corpus
"""
from typing import Iterable, Callable
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.epidoc.elements.expan import Expan
from pyepidoc.shared.classes import SetRelation
from pyepidoc.epidoc.dom import lang


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
    multiplications = filter(lambda expan: expan.is_multiplication, expans)

    return {
        'suspensions': len(list(suspensions)),
        'contractions': len(list(contractions)),
        'contractions_with_suspension': len(list(contractions_with_suspension)),
        'multiplications': len(list(multiplications))
    }


def expans(corpus: EpiDocCorpus) -> list[str]:
    return list(map(str, corpus.expans))


def overall_distribution_via_expans(corpus: EpiDocCorpus) -> dict[str, dict[str, int]]:

    """
    First takes all the expans, and then filters by language
    """
    tokens = corpus.tokens.to_list()
    expans = corpus.expans

    latin_pred: Callable[[EpiDocElement], bool] = lambda token: lang(token) == 'la'

    latin_tokens = filter(latin_pred, tokens)
    greek_tokens = filter(lambda token: lang(token) == 'grc', tokens)
    other_tokens = filter(lambda token: lang(token) not in ['la', 'grc'], tokens)

    latin_expans = filter(lambda expan: lang(expan) == 'la', expans)
    greek_expans = filter(lambda expan: lang(expan) == 'grc', expans)
    other_expans = filter(lambda expan: lang(expan) not in ['la', 'grc'], expans)

    latin_stats = distribution_from_expans(list(latin_expans))
    greek_stats = distribution_from_expans(list(greek_expans))
    other_stats = distribution_from_expans(list(other_expans))

    return {
        'Greek': {'tokens': len(list(greek_tokens)), **greek_stats},
        'Latin': {'tokens': len(list(latin_tokens)), **latin_stats},
        'Other': {'tokens': len(list(other_tokens)), **other_stats}
    }


def overall_distribution_via_corpus(corpus: EpiDocCorpus) -> dict[str, dict[str, int]]:
    """
    First filters the corpus by languages, then counts expan types
    """
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
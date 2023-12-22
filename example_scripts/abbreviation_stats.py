from pathlib import Path
import timeit
import csv

from pyepidoc.analysis.abbreviations.overall import *
from pyepidoc.analysis.abbreviations.output import overall_analysis_to_csv, abbr_count_all_to_csvs
from pyepidoc.analysis.abbreviations.instances import abbreviation_count, raw_abbreviations
from pyepidoc.analysis.utils.csv_ops import pivot_dict
from pyepidoc.epidoc.epidoc_types import AbbrType
from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.displayutils import show_elems
from pyepidoc.shared_types import SetRelation

MASTER_PATH = '/data/ISicily/ISicily/inscriptions/'
corpus_path = MASTER_PATH # insert path to your corpus here 


def print_overall_distribution():
    corpus = EpiDocCorpus(corpus_path)
    
    # print(timeit.timeit(lambda: overall_distribution_via_corpus(corpus), number=10))

    print(overall_distribution_via_corpus(corpus))
    # print(timeit.timeit(lambda: overall_distribution_via_expans(corpus), number=10))
    print(overall_distribution_via_expans(corpus))


def write_overall_distribution():
    overall_analysis_to_csv(EpiDocCorpus(corpus_path), 'example.csv')


def write_abbr_count_all():
    corpus = EpiDocCorpus(corpus_path)
    abbr_count_all_to_csvs(corpus=corpus)


def other():
    corpus = EpiDocCorpus(corpus_path)
    # greek = corpus.filter_by_languages(['grc'])
    # latin = corpus.filter_by_languages(['la'])
    # other = corpus.filter_by_languages(['la', 'grc'], SetRelation.disjoint)
    # other = corpus.filter_by_languages(['xly-Grek'])
    # print(len(other.docs))

    doc = EpiDoc(MASTER_PATH + 'ISic020131.xml')
    print(doc.langs)



def print_instances():
    corpus = EpiDocCorpus(corpus_path)
    # greek = corpus.filter_by_languages(['grc'])
    # latin = corpus.filter_by_languages(['la'])
    other = corpus.filter_by_languages(['la', 'grc'], SetRelation.disjoint)
    # other = corpus.filter_by_languages(['xly-Grek'])
    
    results = list(filter(lambda expan: expan, other.expans))        
    print(show_elems(results))





if __name__ == '__main__':
    write_abbr_count_all()
    # write_overall_distribution()
    # abbr_count('example.csv')
    # print_overall_distribution()
    # print_instances()
    # other()
    
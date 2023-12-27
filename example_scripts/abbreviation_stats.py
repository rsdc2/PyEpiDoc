from pathlib import Path
import timeit
import csv

from pyepidoc.analysis.abbreviations.overall import *
from pyepidoc.analysis.abbreviations.output import overall_analysis_to_csv, abbr_count_all_to_csvs
from pyepidoc.analysis.abbreviations.instances import abbreviation_count, raw_abbreviations
from pyepidoc.analysis.utils.csv_ops import pivot_dict
from pyepidoc.epidoc.enums import AbbrType, TextClass
from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.displayutils import show_elems
from pyepidoc.classes import SetRelation

MASTER_PATH = '/data/ISicily/ISicily/inscriptions/'
corpus_path = MASTER_PATH # insert path to your corpus here 


def print_overall_distribution():
    corpus = EpiDocCorpus(corpus_path)
    
    # print(timeit.timeit(lambda: overall_distribution_via_corpus(corpus), number=10))

    print(overall_distribution_via_corpus(corpus))
    # print(timeit.timeit(lambda: overall_distribution_via_expans(corpus), number=10))
    print(overall_distribution_via_expans(corpus))


def write_overall_distribution():
    overall_analysis_to_csv(EpiDocCorpus(corpus_path), 'overall_distribution.csv')


def write_overall_distribution_stone():
    overall_analysis_to_csv(
        EpiDocCorpus(corpus_path).filter_by_materialclass(
            ['#material.stone'], 'substring'), 
            'overall_distribution_stone.csv'
        )


def write_overall_distribution_funerary():
    corpus = EpiDocCorpus(corpus_path).filter_by_textclass([TextClass.Funerary])
    overall_analysis_to_csv(corpus, 'overall_distribution_funerary.csv')


def write_overall_distribution_stone_funerary():
    overall_analysis_to_csv(
        EpiDocCorpus(corpus_path)
            .filter_by_materialclass(['#material.stone'], 'substring')
            .filter_by_textclass([TextClass.Funerary]), 
        filepath='overall_distribution_stone_funerary.csv'
    )


def write_abbr_count_all():
    corpus = EpiDocCorpus(corpus_path)
    abbr_count_all_to_csvs(corpus=corpus)


def write_abbr_count_funerary():
    corpus = EpiDocCorpus(corpus_path).filter_by_textclass([TextClass.Funerary])
    abbr_count_all_to_csvs(corpus=corpus, output_filename_prefix='funerary_')


def write_abbr_count_non_funerary():
    corpus = EpiDocCorpus(corpus_path).filter_by_textclass([TextClass.Funerary], SetRelation.disjoint)
    abbr_count_all_to_csvs(corpus=corpus, output_filename_prefix='nonfunerary_')


def write_abbr_count_stone_funerary():
    corpus = (EpiDocCorpus(corpus_path)
              .filter_by_textclass([TextClass.Funerary])
              .filter_by_materialclass(['#material.stone'], 'substring'))
    abbr_count_all_to_csvs(corpus=corpus, output_filename_prefix='stone_funerary_')


def write_abbr_count_stone_non_funerary():
    corpus = (EpiDocCorpus(corpus_path)
              .filter_by_textclass([TextClass.Funerary])
              .filter_by_materialclass(['#material.stone'], 'substring'))
    abbr_count_all_to_csvs(corpus=corpus, output_filename_prefix='stone_nonfunerary_')


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
    # write_abbr_count_all()
    # write_overall_distribution_funerary()
    # write_abbr_count_non_funerary()
    # write_abbr_count_stone_funerary()
    write_overall_distribution_stone_funerary()
    # abbr_count('example.csv')
    # print_overall_distribution()
    # print_instances()
    # other()
    
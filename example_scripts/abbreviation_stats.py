from pathlib import Path
import timeit
import csv

from pyepidoc.analysis.abbreviations.overall import *
from pyepidoc.analysis.abbreviations.output import overall_analysis_to_csv
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


def abbr_count(fp: str):
    corpus = EpiDocCorpus(corpus_path)
    raw = raw_abbreviations(
        corpus, 
        abbr_type=AbbrType.suspension, 
        language='la'
    )
    count = abbreviation_count(raw)
    count_dict = {k: {'frequency': v['frequency'], 'isic_ids': v['isic_ids']} for k, v in count.items()}
    list_dict = pivot_dict(count_dict)
    list_dict = sorted(list_dict, key=lambda result: result['frequency'], reverse=True)
    
    fieldnames = list(list_dict[0].keys())
    csv_file = open(fp, mode='w')
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(list_dict)


if __name__ == '__main__':

    # write_overall_distribution()
    abbr_count('example.csv')
    # print_overall_distribution()
    # print_instances()
    # other()
    
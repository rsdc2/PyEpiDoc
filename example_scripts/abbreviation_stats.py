from pyepidoc.analysis.abbreviations import *
from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.displayutils import show_elems
from pyepidoc.shared_types import SetRelation

MASTER_PATH = '/data/ISicily/ISicily/inscriptions/'
corpus_path = MASTER_PATH # insert path to your corpus here 

if __name__ == '__main__':
    corpus = EpiDocCorpus(corpus_path)

    greek = corpus.filter_by_languages(['grc'])
    latin = corpus.filter_by_languages(['la'])
    other = corpus.filter_by_languages(['la', 'grc'], SetRelation.disjoint)

    results = list(filter(lambda expan: expan, other.expans))
    print(show_elems(results))

    # print(overall_distribution(corpus))
    
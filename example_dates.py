from pyepidoc.epidoc.corpus import EpiDocCorpus
    
def corpus_dates():
    corpus = EpiDocCorpus(folderpath='/home/robert/Documents/programming/python/crossreads/pyarethusadoc/PyArethusaDoc/data/ud_linguistic_annotation', fullpath=True).filter_by_form(['vixit', 'ἔζησεν'])
    print(corpus.datemin)
    print(corpus.datemax)

corpus_dates()
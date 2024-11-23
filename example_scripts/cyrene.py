from pyepidoc import EpiDoc, EpiDocCorpus

corpus = EpiDocCorpus(r'..\..\..\Data\Cyrene_small')
corpus.doc_count
corpus.datemean
corpus.docs[1].id
print(corpus.docs[1].text_leiden)
corpus.languages
corpus.filter_by_languages(['la'], language_attr='div_langs').doc_count


textclasses = corpus._get_textclasses(False)

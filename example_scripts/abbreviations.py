"""
Scripts for extracting abbreviations and 
information about abbreviations from an EpiDoc corpus
"""

from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.epidoc.enums import AbbrType
from pyepidoc.epidoc.funcs import lang, owner_doc
from pyepidoc.utils import top, contains, listfilter
from pyepidoc.displayutils import show_elems

MASTER_PATH = '/data/ISicily/ISicily/inscriptions/'
corpus_path = MASTER_PATH # insert path to your corpus here 

corpus = EpiDocCorpus(corpus_path)

abbreviations = [expan for expan in corpus.expans]
print('Total abbreviations in I.Sicily corpus: ', len(abbreviations))

suspensions = [abbr for abbr in abbreviations 
               if contains(abbr.abbr_types, AbbrType.suspension)]
print('Total suspensions in corpus: ', len(suspensions))

latin_susp = [susp for susp in suspensions 
    if lang(susp) == 'la']

print('of which Latin: ', len(latin_susp))

greek_susp = [susp for susp in suspensions
    if lang(susp) == 'grc']

print('of which Greek: ', len(greek_susp))

other_susp = [susp for susp in suspensions
    if lang(susp) not in ['grc', 'la']]
print('of which other: ', len(other_susp))

print(show_elems(top(other_susp, 10)))

print('First 10 examples:')
print(show_elems(top(suspensions, 10)))

doc000001 = owner_doc(suspensions[0])
if doc000001 is not None:
    print(doc000001.edition_text)
else:
    raise TypeError("doc is None")

contractions = [abbr for abbr in abbreviations 
                if contains(abbr.abbr_types, AbbrType.contraction)]
print('Total contractions in corpus: ', len(contractions))

latin_contractions = [contraction for contraction in contractions 
    if lang(contraction) == 'la']
print('of which Latin: ', len(latin_contractions))

greek_contractions = [contraction for contraction in contractions 
    if lang(contraction) == 'grc']
print('of which Greek: ', len(greek_contractions))

other_contractions = [contraction for contraction in contractions 
    if lang(contraction) not in ['grc', 'la']]
print('of which other: ', len(other_contractions))

top_10_contractions = [contraction for contraction in top(contractions, 10)]

print('First 10 examples:')
print(show_elems(top_10_contractions))

c_with_s = [abbr for abbr in abbreviations 
    if contains(abbr.abbr_types, AbbrType.contraction_with_suspension)]
print('Total contractions with suspension in corpus: ', len(c_with_s))

latin_c_with_s = listfilter(lambda x: lang(x) == 'la', c_with_s)
print('of which Latin: ', len(latin_c_with_s))

greek_c_with_s = listfilter(lambda x: lang(x) == 'grc', c_with_s)
print('of which Greek: ', len(greek_c_with_s))

other_c_with_s = listfilter(lambda x: lang(x) not in ['grc', 'la'], c_with_s)
print('of which Greek: ', len(other_c_with_s))

print(show_elems(top(c_with_s, 10)))

multiplications = [abbr for abbr in abbreviations 
    if contains(abbr.abbr_types, AbbrType.multiplication)]

print('Total multiplications in corpus: ', len(multiplications))

latin_mult = listfilter(lambda x: lang(x) == 'la', multiplications)
print('of which Latin: ', len(latin_mult))

greek_mult = listfilter(lambda x: lang(x) == 'grc', multiplications)
print('of which Greek: ', len(greek_mult))

print(show_elems(multiplications))

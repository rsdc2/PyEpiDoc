
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.epidoctypes import TextClass
from pyepidoc.file.funcs import str_to_file
from pyepidoc.utils import remove_none

# Load the corpus
corpus = EpiDocCorpus(folderpath='corpus/')

# Filter the corpus to find the funerary inscriptions
funerary_corpus = corpus.filter_by_textclass([TextClass.Funerary.value])

# Within the funerary corpus, find all the Latin inscriptions from Catania / Catina:
catina_funerary_corpus = (
    funerary_corpus
        .filter_by_orig_place(['Catina'])
        .filter_by_languages(['la'])
)

# Output the of this set of documents to a file ```catina_funerary_ids_la.txt``` 
# in the current working directory.
catina_funerary_ids = '\n'.join(remove_none(catina_funerary_corpus.ids))
str_to_file(catina_funerary_ids, 'catina_funerary_ids_la.txt')
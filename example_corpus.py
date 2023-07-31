from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.epidoc.epidoctypes import AbbrType
from pyepidoc.utils import head, top, last
from pyepidoc.epidoc.funcs import doc_id, owner_doc, lang, line
from pyepidoc.epidoc.lb import Lb
from pyepidoc.displayutils import show_elems
from pyepidoc.epidoc.epidoctypes import AbbrType, TextClass
from pyepidoc.file.funcs import str_to_file
from pyepidoc.utils import flatlist

def example():

    corpus = EpiDocCorpus(folderpath='data/isicily_master')

    multiplications = [expan for expan in corpus.expans   
        if expan.abbr_type == AbbrType.suspension and lang(expan) not in ['grc', 'la']]

    print(show_elems(top(multiplications, 10)))


def example_tokenize():
    corpus = EpiDocCorpus(folderpath='data/isicily_master')
    corpus.tokenize(dstfolder='data/isicily_tokenized', add_space_between_words=True)


def christian_corpus():
    corpus = EpiDocCorpus(folderpath='data/isicily_tokenized')
    funerary_corpus = corpus.filter_by_textclass([TextClass.Funerary.value])

    catina_funerary_corpus = (
        funerary_corpus
            .filter_by_supplied(has_supplied=False)
            .filter_by_gap(has_gap=False, reasons=['lost'])
            .filter_by_languages(['la'])
            .filter_by_form(['pace'])
    )
    catina_funerary_ids = '\n'.join(catina_funerary_corpus.ids)
    str_to_file(catina_funerary_ids, 'data/in_pace.txt')



def catina_corpus():

    corpus = EpiDocCorpus(folderpath='data/isicily_master')
    funerary_corpus = corpus.filter_by_textclass([TextClass.Funerary.value])
    orig_places = funerary_corpus.list_unique_orig_places(sort_on='freq', min_freq=20)

    for place in orig_places:
        print(*place)

    catina_funerary_corpus = (
        funerary_corpus
            .filter_by_orig_place(['Catina'])
            .filter_by_supplied(has_supplied=False)
            .filter_by_gap(has_gap=False, reasons=['lost'])
            .filter_by_languages(['la'])
    )
    print(*catina_funerary_corpus.ids, sep='\n')

    catina_funerary_ids = '\n'.join(catina_funerary_corpus.ids)
    str_to_file(catina_funerary_ids, 'data/catina_funerary_ids_la.txt')

    # print(top(funerary_corpus.docs))    
    # places = [doc.orig_place for doc in funerary_corpus.docs]
    # unique_places = set(places)
    
    # for unique_place in unique_places:
    #     print(unique_place, len([place for place in places if place == unique_place]))


def clusters_corpus():
    # ids_str = 'ISic000002 ISic000043 ISic000083 ISic000307 ISic000311 ISic000323 ISic000325 ISic000327 ISic000329 ISic000330 ISic000331 ISic000332 ISic000334 ISic000335 ISic000336 ISic000338 ISic000339 ISic000340 ISic000341 ISic000343 ISic000344 ISic000346 ISic000347 ISic000348 ISic000349 ISic000358 ISic000359 ISic000362 ISic000364 ISic000368 ISic000373 ISic000375 ISic000376 ISic000378 ISic000381 ISic000383 ISic000394 ISic000397 ISic000447 ISic000451 ISic000477 ISic000576 ISic000577 ISic000619 ISic000704 ISic001308 ISic001312 ISic001313 ISic001315 ISic001316 ISic001318 ISic001319 ISic001322 ISic001325 ISic001327 ISic001331 ISic001344 ISic001345 ISic001354 ISic001358 ISic001360 ISic001361 ISic001362 ISic001364 ISic001365 ISic001370 ISic001547 ISic001626 ISic003149 ISic003150 ISic003215 ISic003217 ISic003223 ISic003228 ISic003229 ISic003231 ISic003233 ISic003237 ISic003238 ISic003241 ISic003242 ISic003244 ISic003245 ISic004400 ISic004444'    
    
    ids_str = 'ISic000002 ISic000043 ISic000311 ISic000323 ISic000325 ISic000327 ISic000329 ISic000330 ISic000331 ISic000332 ISic000334 ISic000335 ISic000336 ISic000338 ISic000339 ISic000340 ISic000341 ISic000343 ISic000344 ISic000346 ISic000347 ISic000349 ISic000358 ISic000359 ISic000362 ISic000364 ISic000368 ISic000373 ISic000375 ISic000376 ISic000378 ISic000381 ISic000383 ISic000394 ISic000397 ISic000447 ISic000451 ISic000576 ISic000577 ISic000704 ISic001308 ISic001312 ISic001313 ISic001315 ISic001316 ISic001318 ISic001319 ISic001322 ISic001325 ISic001327 ISic001331 ISic001344 ISic001345 ISic001354 ISic001358 ISic001360 ISic001361 ISic001362 ISic001364 ISic001365 ISic001370 ISic001626 ISic003149 ISic003150 ISic003215 ISic003217 ISic003223 ISic003228 ISic003231 ISic003233 ISic003237 ISic003238 ISic003241 ISic003242 ISic003244 ISic003245 ISic004400 ISic004444'
    ids = ids_str.split()
    corpus = EpiDocCorpus(folderpath='data/isicily_master').filter_by_ids(ids)

    docs_size = len(corpus.docs)
    locs_list = [doc.orig_place for doc in corpus.docs]
    locs_set = set(locs_list)
    locs_count_dict = {loc: locs_list.count(loc) for loc in locs_set}
    print(locs_count_dict)

    get_lang = lambda langs_list: 'biling' if len(langs_list) > 1 else langs_list[0]

    langs_list = [get_lang(doc.langs) for doc in corpus.docs]
    # print(langs_list)
    print('number of docs:', docs_size)

    # langs_list_2 = [lang for lang in langs_list]
    langs_set = set(langs_list)
    langs_count_dict = {lang: langs_list.count(lang) for lang in langs_set}
    print(langs_count_dict)
    (locs_count_dict)

    catania_dates = [doc.date_mean for doc in corpus.docs if doc.orig_place == 'Catina' and doc.date_mean is not None]
    non_catania_dates = [doc.date_mean for doc in corpus.docs if doc.orig_place != 'Catina' and doc.date_mean is not None]

    types = set(flatlist([doc.textclasses for doc in corpus.docs]))
    print(types)
    print(min(catania_dates), max(catania_dates))
    print(min(non_catania_dates), max(non_catania_dates))

    corpus = corpus.filter_by_textclass(['#function.honorific'])
    print([doc.id for doc in corpus.docs])

    # df.to_csv('cluster_corpus.csv')

if __name__ == '__main__':
    # example()
    example_tokenize()
    # example_textclasses()
    # christian_corpus()
    # clusters_corpus()

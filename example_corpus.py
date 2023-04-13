from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.epidoc.epidoctypes import AbbrType

def example():

    corpus = EpiDocCorpus(folderpath='data/isicily_master')

    expans = [expan for expan in corpus.expans ]
        # if expan.abbr_count > 1]

    print([expan for expan in expans if expan.abbr_type == AbbrType.multiplication])
    # print([expan.xml for expan in expans 
    #     if 'nnostr' in expan.text_desc])
    # print([expan.xml for expan in expans])
    print(len(expans))


if __name__ == '__main__':
    example()
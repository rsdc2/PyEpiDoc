from pyepidoc import EpiDoc, EpiDocCorpus

def example():

    corpus = EpiDocCorpus(folderpath='data/isicily_master_small')

    expans = [expan for expan in corpus.expans 
        if expan.abbr_count > 1]

    print([expan for expan in expans])
    print(len(expans))


if __name__ == '__main__':
    example()
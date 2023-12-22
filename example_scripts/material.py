from pyepidoc import EpiDoc, EpiDocCorpus

MASTER_PATH = '/data/ISicily/ISicily/inscriptions/'
corpus_path = MASTER_PATH # insert path to your corpus here 


def print_material_classes():
    corpus = EpiDocCorpus(corpus_path)

    print(corpus.materialclasses)


if __name__ == '__main__':
    print_material_classes()
from pyepidoc import EpiDoc
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.enums import TextClass
from pyepidoc.utils.file import str_to_file


corpus_folderpath = "api/files/corpus"


def test_tokens_example():
    from pyepidoc import EpiDoc

    doc = EpiDoc("readme_examples/files/input/ISic000001_tokenized.xml")

    tokens = doc.tokens
    tokens_str = ' '.join([str(token) for token in tokens])

    assert tokens_str == 'Dis manibus Zethi vixit annis VI'


def test_tokenize_example():
    # Load the EpiDoc file
    doc = EpiDoc("readme_examples/files/input/ISic000032_untokenized.xml")

    # Tokenize the edition with default settings
    doc.tokenize()

    # Save the results to a new XML file
    doc.to_xml_file("readme_examples/files/tokenized_output/ISic000032_tokenized.xml")

    tokenized_doc = EpiDoc("readme_examples/files/tokenized_output/ISic000032_tokenized.xml")
    tokenized_benchmark = EpiDoc("readme_examples/files/tokenized_benchmark/ISic000032_tokenized.xml")
    try:
        # breakpoint()
        assert [str(word) for word in tokenized_doc.tokens] == [str(word) for word in tokenized_benchmark.tokens]
        assert [word.xml_byte_str for word in tokenized_doc.tokens] == [word.xml_byte_str for word in tokenized_benchmark.tokens]
        assert [word.xml_byte_str for word in tokenized_doc.compound_words] == [word.xml_byte_str for word in tokenized_benchmark.compound_words]
        assert [edition.xml_byte_str for edition in tokenized_doc.editions()] == [edition.xml_byte_str for edition in tokenized_benchmark.editions()]
    except AssertionError as e:
        raise e


def test_corpus_example():

    # Load the corpus
    corpus = EpiDocCorpus(corpus_folderpath)

    # Filter the corpus to find the funerary inscriptions
    funerary_corpus = corpus.filter_by_textclass([TextClass.Funerary.value])

    # Within the funerary corpus, find all the Latin inscriptions from Panhormus:
    panhormus_funerary_corpus = (
        funerary_corpus
            .filter_by_orig_place(['Panhormus'])
            .filter_by_languages(['la'])
    )

    panhormus_funerary_ids = '\n'.join(panhormus_funerary_corpus.ids)
    assert panhormus_funerary_ids == ''



def test_corpus_example_2():

    # Load the corpus
    corpus = EpiDocCorpus(corpus_folderpath)


    # Find all the Latin inscriptions from Panhormus:
    panhormus_corpus = (
        corpus
            .filter_by_orig_place(['Panhormus'])
            .filter_by_languages(['la'])
    )

    panhormus_ids = '\n'.join(panhormus_corpus.ids)
    assert panhormus_ids == 'ISic000032'

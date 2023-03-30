from pyepidoc import EpiDoc


def test_tokens_example():
    from pyepidoc import EpiDoc

    doc = EpiDoc("readme_examples/files/input/ISic000001_tokenized.xml")

    tokens = doc.tokens
    tokens_str = ' '.join([str(token) for token in tokens])

    assert tokens_str == 'dis manibus Zethi vixit annis VI'


def test_tokenize_example():
    # Load the EpiDoc file
    doc = EpiDoc("readme_examples/files/input/ISic000032_untokenized.xml")

    # Tokenize the edition
    doc.tokenize()

    # Prettify the edition
    doc.prettify_edition()

    # Add spaces between tokens
    doc.add_space_between_tokens()

    # Save the results to a new XML file
    doc.to_xml("readme_examples/files/tokenized_output/ISic000032_tokenized.xml", create_folderpath=True)


    tokenized_doc = EpiDoc("readme_examples/files/tokenized_output/ISic000032_tokenized.xml")
    tokenized_benchmark = EpiDoc("readme_examples/files/tokenized_benchmark/ISic000032_tokenized.xml")

    assert [str(word) for word in tokenized_doc.tokens] == [str(word) for word in tokenized_benchmark.tokens]
    assert [word.xml for word in tokenized_doc.tokens] == [word.xml for word in tokenized_benchmark.tokens]
    assert [word.xml for word in tokenized_doc.compound_words] == [word.xml for word in tokenized_benchmark.compound_words]
    assert [edition.xml for edition in tokenized_doc.editions] == [edition.xml for edition in tokenized_benchmark.editions]

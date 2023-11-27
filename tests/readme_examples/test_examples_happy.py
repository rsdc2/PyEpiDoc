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

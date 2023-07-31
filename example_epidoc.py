from pyepidoc import EpiDoc
from pyepidoc.utils import head, top
from pyepidoc.epidoc.funcs import doc_id
from pyepidoc.displayutils import show_elems
from pyepidoc.epidoc.epidoctypes import AbbrType

def example():

    # Load the EpiDoc file
    # doc = EpiDoc("examples/ISic000032_untokenized.xml")
    doc = EpiDoc("ISic000001_tokenized.xml")

    # Tokenize the edition
    doc.tokenize()

    # Prettify
    doc.prettify_edition()

    # Add spaces between tokens
    doc.add_space_between_tokens()

    # Save the results to a new XML file
    doc.to_xml("examples/ISic000032_tokenized.xml")


def tokenize_interpunct():
    doc = EpiDoc("tests/tokenize/files/untokenized/interpunct_3.xml")

    from pyepidoc.epidoc.scripts import tokenize

    tokenize("tests/tokenize/files/untokenized", "", ['interpunct_3'], True, False)


def tokenize_orgName():
    from pyepidoc.epidoc.scripts import tokenize

    tokenize("tests/tokenize/files/untokenized", "", ['orgName_2'], True, False)


def tokenize_lb_break_no():
    from pyepidoc.epidoc.scripts import tokenize

    # tokenize("tests/tokenize/files/untokenized", "", ['break_equals_no_2'], True, False)
    tokenize("tests/tokenize/files/untokenized", "", ['space'], True, False)


def tokenize_isic_file():
    from pyepidoc.epidoc.scripts import tokenize
    tokenize("data/isicily_master", "trial", ['ISic001344'], True, False)


def tokenize_example():
    from pyepidoc.epidoc.scripts import tokenize
    tokenize("tests/tokenize/files/untokenized", "trial", ['interpunct_9'], True, False)


if __name__ == '__main__':
    # tokenize_lb_break_no()
    tokenize_isic_file()
    # tokenize_example()
    
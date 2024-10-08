from pyepidoc import EpiDoc
from pyepidoc.epidoc.dom import line_end_after, line_ends 
import pytest



relative_filepaths = {
    'ISic000001': 'tests/api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'tests/api/files/single_files_tokenized/ISic000552.xml',
    'persName_nested': 'tests/api/files/persName_nested.xml',
    'langs_1': 'tests/api/files/langs_1.xml',
    'langs_2': 'tests/api/files/langs_2.xml',
    'langs_3': 'tests/api/files/langs_3.xml',
    'line_1': 'tests/api/files/line_1.xml',
    'line_2': 'tests/api/files/line_2.xml',
    'gap': 'tests/api/files/gap.xml',
    'comma': 'tests/api/files/comma.xml',
    'leiden': 'tests/api/files/leiden.xml',
    'abbr': 'tests/api/files/abbr.xml'
}



def test_line_end():
    filepath = relative_filepaths['ISic000001']
    doc = EpiDoc(filepath)
    tokens = doc.tokens

    manibus = tokens[1]

    assert line_end_after(manibus) == True


@pytest.mark.parametrize('fp', list(relative_filepaths.values()))
def test_count_line_ends(fp):
    doc = EpiDoc(fp)
    doc.tokenize()

    edition = doc.first_edition
    if edition is None:
        return 0
    
    tokens = edition.tokens_incl_nested
    
    linecount = len(edition.lbs)
    lineends = sum(map(line_ends, tokens))

    assert linecount == lineends
from pyepidoc import EpiDoc
from pyepidoc.epidoc.dom import line_end_after, line_ends 
import pytest



relative_filepaths = {
    'ISic000001': 'api/files/single_files_untokenized/ISic000001.xml',
    'ISic000552': 'api/files/single_files_tokenized/ISic000552.xml',
    'persName_nested': 'api/files/persName_nested.xml',
    'langs_1': 'api/files/langs_1.xml',
    'langs_2': 'api/files/langs_2.xml',
    'langs_3': 'api/files/langs_3.xml',
    'line_1': 'api/files/line_1.xml',
    'line_2': 'api/files/line_2.xml',
    'gap': 'api/files/gap.xml',
    'comma': 'api/files/comma.xml',
    'leiden': 'api/files/leiden.xml',
    'abbr': 'api/files/abbr.xml'
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
    lineends = sum([line_ends(token) for token in tokens])

    assert linecount == lineends
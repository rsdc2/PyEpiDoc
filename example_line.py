from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.epidoc.funcs import line
from pyepidoc.utils import last


def example_line():
    doc = EpiDoc(input='tests/api/files/line_2.xml', fullpath=False)

    tokens = doc.tokens

    ln = line(last(tokens))
    print(ln)


example_line()
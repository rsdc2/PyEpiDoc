from pyepidoc import EpiDoc, EpiDocCorpus
from pyepidoc.epidoc.funcs import line
from pyepidoc.utils import last, head


def example_line():
    doc = EpiDoc(input='tests/api/files/line_2.xml', fullpath=False)

    tokens = doc.tokens

    ln = line(head(tokens))
    print(ln)


example_line()
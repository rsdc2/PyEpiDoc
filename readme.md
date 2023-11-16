# PyEpiDoc

PyEpiDoc is a Python (>=3.9) library for parsing and interacting with [TEI](https://tei-c.org/) XML
[EpiDoc](https://epidoc.stoa.org/) files. It has been tested on Python 3.9.16 on Linux (Ubuntu) 
with both ```venv``` and ```--user``` installations, and a Python 3.10.0 ```venv``` on Windows. 
It should work on later Python versions.

PyEpiDoc has been designed for use, in the first instance, 
with the [I.Sicily](http://sicily.classics.ox.ac.uk/) corpus.
For information on the encoding of I.Sicily texts in TEI EpiDoc, see
the [I.Sicily GitHub wiki](https://github.com/ISicily/ISicily/wiki).

**NB: PyEpiDoc is currently under active development.**


## Install (no dev dependencies)

### Locally

To install PyEpiDoc along with its dependencies (```lxml```):

1. Clone or download the repository;

2. Navigate into the cloned / downloaded repository.

3. From within the cloned repository, install at the ```user``` level with:

    ```
    pip install . --user
    ```

### In a virtual environment

If you are using a ```venv``` virtual environment:

1. Make sure the virtual environment has been activated, e.g. on Linux:

    ```source env/bin/activate```

2. Install with ```pip```:

    ```pip install .```

## Uninstall
```
pip uninstall pyepidoc
```

## Install for development

To install PyEpiDoc along with its dependencies (```lxml```) and development dependencies (```pytest```, ```mypy```), e.g. in a virtual environment:

1. Clone or download the repository;

2. Navigate into the cloned / downloaded repository.

3. From within the cloned repository, install with:

    ```
    pip install .[dev]
    ```

## Example usage

Given a tokenized EpiDoc file ```ISic000001.xml``` in an ```examples/``` folder in the current working directory.

### Load the EpiDoc file

```
from pyepidoc import EpiDoc

doc = EpiDoc("examples/ISic000001_tokenized.xml")
```


### Print the text of the edition

```
print(doc.edition_text)
```

### Print all tokens in an edition (e.g. ```<w>```, ```<name>``` etc.)

```
tokens = doc.tokens
print(' '.join([str(token) for token in tokens]))
```

### Produce a tokenized version of a given EpiDoc file

Given an untokenized EpiDoc file ```ISic000032_untokenized.xml``` in an ```examples``` folder in the current working directory:

```
from pyepidoc import EpiDoc

# Load the EpiDoc file
doc = EpiDoc("examples/ISic000032_untokenized.xml")

# Tokenize the edition
doc.tokenize()

# Prettify the <div type="edition"> XML
doc.prettify_edition()

# Add spaces between tokens
doc.add_space_between_tokens()

# Print list of tokens
print('Tokens: ', doc.tokens_list_str)

# Save the results to a new XML file
# Creates the folderpath if it does not exist
doc.to_xml("examples/ISic000032_tokenized.xml", create_folderpath=True)
```

### Corpus level analysis

Given a corpus of EpiDoc XML files in a folder ```corpus/``` in the current working directory, the following code filters the corpus and writes a text file containing the ids of all Latin funerary inscriptions from Catania / Catina:

```
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.epidoctypes import TextClass
from pyepidoc.file.funcs import str_to_file

# Load the corpus
corpus = EpiDocCorpus('corpus')

# Filter the corpus to find the funerary inscriptions
funerary_corpus = corpus.filter_by_textclass([TextClass.Funerary.value])

# Within the funerary corpus, find all the Latin inscriptions from Catania / Catina:
catina_funerary_corpus = (
    funerary_corpus
        .filter_by_orig_place(['Catina'])
        .filter_by_languages(['la'])
)

# Output the of this set of documents to a file ```catina_funerary_ids_la.txt``` 
# in the current working directory.
catina_funerary_ids = '\n'.join(catina_funerary_corpus.ids)
str_to_file(catina_funerary_ids, 'catina_funerary_ids_la.txt')

```

## Run the tests

with ```pytest``` installed (the dev installation will do this for you):

1. Navigate to the ```tests/``` folder. 

2. To run all the tests:

    ```
    pytest
    ```

If ```pytest``` is not available to the currently active version of Python, 
it may be necessary to specify the Python executable with ```pytest``` 
installed, e.g.:

    ```
    python3.10 -m pytest
    ```

## Check the types

To check the integrity of the type annotations, 
with ```mypy``` installed (the dev installation will
do this for you):

```
mypy src/pyepidoc
```

If ```mypy``` is not available to the currently active version of Python, 
it may be necessary to specify the Python executable with ```mypy``` 
installed, e.g.:

    ```
    python3.10 -m mypy src/pyepidoc
    ```


## Tokenizer behaviour

The treatement of a given token by the tokenizer may be affected by one or more of the following:

- Status in ```pyepidoc/epidoc/epidoctypes.py```
- Presence in ```pyepidoc/constants.py``` in ```SubsumableRels```

The token will be subsumed into a neighbouring ```<w>``` token if it is not separated by whitespace if:
- it is listed in as a ```dep``` of e.g. ```<w>``` in ```SubsumableRels```

The token will be subsumed into a neighbouring ```<w>``` token regardless of the presence of intervening whitespace if:
- it is listed in as a ```dep``` of e.g. ```<w>``` in ```SubsumableRels``` and
- it is a member of ```AlwaysSubsumableType``` in ```epidoctypes.py```


## Package structure

The PyEpiDoc package has three subpackages:

- ```file``` containing modules for file handling;
- ```base``` containing modules with base classes for EpiDoc XML handling;
- ```epidoc``` containing modules for handling EpiDoc specific XML nodes, e.g. ```<ab>```, ```<w>``` etc.

In addition ```utils.py``` provides general utility functions, in particular for handling Python 
```list```s.

## Features to be included in future

### XML comments

XML comments should now be handled correctly, and reproduced in new files.

## Dependencies

PyEpiDoc depends on [lxml](https://lxml.de/) ([BSD](https://github.com/lxml/lxml/blob/master/LICENSE.txt)). 
Development dependencies are [mypy](https://mypy.readthedocs.io/en/stable/) ([MIT](https://github.com/python/mypy/blob/master/LICENSE)) 
and [pytest](https://docs.pytest.org/en/7.4.x/) ([MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE)). Licenses for these dependencies are included in the `LICENSES` directory.


## Acknowledgements

The software for PyEpiDoc was written by Robert Crellin as part of the Crossreads project at the Faculty of Classics, University of Oxford, and is licensed under the BSD 3-clause license. This project has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation programme (grant agreement No 885040, “Crossreads”).

Example and test ```.xml``` files, contained in the ```examples/``` and ```tests/``` subfolders, are either directly form, or derived from, the [I.Sicily corpus](https://github.com/ISicily/ISicily), which are made available under the [CC-BY-4.0 licence](https://creativecommons.org/licenses/by/4.0/).

For further details and acknowledgements on the generation of ISicily token IDs (```pyepidoc/epidoc/ids```), see [https://github.com/rsdc2/ISicID](https://github.com/rsdc2/ISicID).
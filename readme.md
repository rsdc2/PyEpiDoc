# PyEpiDoc (α)

PyEpiDoc is a Python (>=3.9) library for parsing and interacting with [TEI](https://tei-c.org/) XML
[EpiDoc](https://epidoc.stoa.org/) files. It has been tested on Python 3.9.16 on Linux (Ubuntu) 
with both ```venv``` and ```--user``` installations, and a Python 3.10.0 ```venv``` on Windows. 
It should work on later Python versions.

PyEpiDoc has been designed for use, in the first instance, 
with the [I.Sicily](http://sicily.classics.ox.ac.uk/) corpus.
For information on the encoding of I.Sicily texts in TEI EpiDoc, see
the [I.Sicily GitHub wiki](https://github.com/ISicily/ISicily/wiki).

**NB: PyEpiDoc is currently under active development.**

## Dependencies

PyEpiDoc depends on [```lxml```](https://lxml.de/) for parsing XML.
```lxml``` is used as rather than ```ElementTree``` primarily to 
make use of its full ```xpath``` support.

To run the tests you need [```pytest```](https://docs.pytest.org/en/7.2.x/).
You can use [```mypy```](https://www.mypy-lang.org/) to check the types.


## Install
To install PyEpiDoc along with its dependencies (```lxml```, ```pytest```, ```mypy```):

1. Clone or download the repository;

2. Navigate into the cloned / downloaded repository.

3. From within the cloned repository, install at the ```user``` level with:

    ```
    pip install . --user
    ```

### Virtual environments

If you are using a ```venv``` virtual environment:

1. Make sure the virtual environment has been activated, e.g. on Linux:

    ```source env/bin/activate```

2. Install with ```pip```:

    ```pip install .```


## Uninstall
```
pip uninstall pyepidoc
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
# Load the EpiDoc file
doc = EpiDoc("examples/ISic000032_untokenized.xml")

# Tokenize the edition
doc.tokenize()

# Prettify the <div type="edition"> XML
doc.prettify_edition()

# Add spaces between tokens
doc.add_space_between_tokens()

# Save the results to a new XML file
# Creates the folderpath if it does not exist
doc.to_xml("examples/ISic000032_tokenized.xml", create_folderpath=True)
```

### Corpus analysis

Given a corpus of EpiDoc XML files in a folder ```corpus/``` in the current working directory, the following code filters the corpus and writes a text file containing the ids of all Latin funerary inscriptions from Catania / Catina:

```
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.epidoctypes import TextClass
from pyepidoc.file.funcs import str_to_file

# Load the corpus
corpus = EpiDocCorpus(folderpath='corpus')

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

1. Navigate to the ```tests/``` folder. 

2. To run all the tests:

    ```
    pytest
    ```


## Check the types

To check the integrity of the type annotations:

```
mypy pyepidoc
```

## Package structure

The PyEpiDoc package has three subpackages:

- ```file``` containing modules for file handling;
- ```base``` containing modules with base classes for EpiDoc XML handling;
- ```epidoc``` containing modules for handling EpiDoc specific XML nodes, e.g. ```<ab>```, ```<w>``` etc.

In addition ```utils.py``` provides general utility functions, in particular for handling Python 
```list```s.

## Features to be included in future

### XML comments

At the moment the parser ignores XML comments, so any new XML files produced (e.g. through tokenization) will not reproduce the comments.
This will be implemented soon.


## Acknowledgements

The software for PyEpiDoc was written by Robert Crellin as part of the Crossreads project at the Faculty of Classics, University of Oxford, and is licensed under the MIT license. This project has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation programme (grant agreement No 885040, “Crossreads”).

Example and test ```.xml``` files, contained in the ```examples/``` and ```tests/``` subfolders, are either directly form, or derived from, the [I.Sicily corpus](https://github.com/ISicily/ISicily), which are made available under the [CC-BY-4.0 licence](https://creativecommons.org/licenses/by/4.0/).

# PyEpiDoc (α)

PyEpiDoc is a Python (>=3.9.16) library for parsing and interacting with [TEI](https://tei-c.org/) XML
[EpiDoc](https://epidoc.stoa.org/) files. It has been tested on Python 3.9.16 on Linux (Ubuntu) with both ```venv``` and ```--user``` installations, and a Python 3.10.0 ```venv``` on Windows. It should work on later Python versions.

PyEpiDoc has been designed for use, in the first instance, 
with the [I.Sicily](http://sicily.classics.ox.ac.uk/) corpus.

**PyEpiDoc is currently under active development, and may contain bugs!**

## Dependencies

PyEpiDoc depends on [```lxml```](https://lxml.de/) for parsing XML.
To run the tests you need [```pytest```](https://docs.pytest.org/en/7.2.x/).
You can use [```mypy```](https://www.mypy-lang.org/) to check the types.


## Install
To install PyEpiDoc along with its dependencies (```lxml```, ```pytest```, ```mypy```), first clone or download the repository.



### ```venv``` virtual environment

If you are using a ```venv``` virtual environment, once the virtual environment has been activated:

```
pip install ./pyepidoc
```


### User installation
If you are using a local Python instance, 
in the cloned / downloaded folder's **parent** folder type:

```
pip install ./pyepidoc --user
```


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

    # Prettify
    doc.prettify()

    # Add spaces between tokens
    doc.add_space_between_tokens()

    # Save the results to a new XML file
    doc.to_xml("examples/ISic000032_tokenized.xml")
```

## Run the tests

From the **parent** folder of ```tests```:

```
pytest
```

will run all the tests.

## Check the types

To check the integrity of the type annotations:

```
mypy pyepidoc
```

## Package structure

The PyEpiDoc package has three subpackages:

- ```file``` containing modules for file handling;
- ```xml``` containing modules for XML handling;
- ```epidoc``` containing modules for handling EpiDoc XML specifically.

In addition ```utils.py``` provides general utility functions, in particular for handling Python 
```list```s.

## Features to be included in future

### XML comments

At the moment the parser ignores XML comments, so any new XML files produced (e.g. through tokenization) will not reproduce the comments.
This will be implemented soon.


## Acknowledgements

The software for PyEpiDoc was written by Robert Crellin as part of the Crossreads project at the Faculty of Classics, University of Oxford, and is licensed under the MIT license. This project has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation programme (grant agreement No 885040, “Crossreads”).

Example and test ```.xml``` files, contained in the ```examples/``` and ```tests/``` subfolders, are either directly form, or derived from, the [I.Sicily corpus](https://github.com/ISicily/ISicily), which are made available under the [CC-BY-4.0 licence](https://creativecommons.org/licenses/by/4.0/).

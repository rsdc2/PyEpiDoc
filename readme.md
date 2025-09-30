<div>
  <img align="left" valign="center" src="assets/ISicily.jpg?raw=true" alt="isicily logo" height="80" >
  <img align="left" valign="center" src="assets/oxford.png?raw=true" alt="oxford logo" height="80"  style="padding-top: 80px" >
  <img align="left" valign="center" src="assets/EU_ERC.jpg?raw=true" alt="erc logo" height="80" >
</div>
<br clear="all">

# PyEpiDoc


PyEpiDoc is a Python (>=3.10) library for parsing and interacting with [TEI](https://tei-c.org/) XML
[EpiDoc](https://epidoc.stoa.org/) files. It has been tested on Python on Linux (Ubuntu) and Windows.

PyEpiDoc has been designed for use, in the first instance, 
with the [I.Sicily](http://sicily.classics.ox.ac.uk/) corpus.
For information on the encoding of I.Sicily texts in TEI EpiDoc, see
the [I.Sicily GitHub wiki](https://github.com/ISicily/ISicily/wiki).

**NB: PyEpiDoc is currently under active development.**


## Install (no dev dependencies)

### Locally

To install PyEpiDoc along with its dependencies (```lxml```):

1. Clone or download the repository.

2. Navigate into the cloned / downloaded repository.

3. From within the cloned repository, install at the ```user``` level with:

```bash
pip install . --user
```

### In a virtual environment

If you are using a ```venv``` virtual environment:

1. Make sure the virtual environment has been activated, e.g. on Linux:

```bash
source env/bin/activate
```

2. Install with ```pip```:

```bash
pip install .
```

## Uninstall
```bash
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

## Running the Jupyter Notebooks

Jupyter notebooks are included in the repository under `notebooks/` to provide example usage:

- `getting_started.ipynb`
- `abbreviations.ipynb`
- `setting_ids.ipynb`

For instructions on installing Jupyter notebook, see https://docs.jupyter.org/en/latest/install/notebook-classic.html. Alternatively, see also https://jupyter.org/install.

Once Jupyter notebook is installed, to run `getting_started.ipynb`, type:

```
jupyter notebook getting_started.ipynb
```

## Example usage

Given a tokenized EpiDoc file ```ISic000001.xml``` in an ```examples/``` folder in the current working directory.

### Load the EpiDoc file

```python
from pyepidoc import EpiDoc

doc = EpiDoc("examples/ISic000001_tokenized.xml")
```


### Print the text of the edition

```
print(doc.edition_text)
```

### Print all tokens in an edition (e.g. ```<w>```, ```<name>``` etc.)

```python
tokens = doc.tokens
print(' '.join([str(token) for token in tokens]))
```

### Produce a tokenized version of a given EpiDoc file

Given an untokenized EpiDoc file ```ISic000032_untokenized.xml``` in an ```examples``` folder in the current working directory:

```python
from pyepidoc import EpiDoc

# Load the EpiDoc file
doc = EpiDoc("examples/ISic000032_untokenized.xml")

# Tokenize the edition with default settings
doc.tokenize()

# Print list of tokens
print('Tokens: ', doc.tokens_list_str)

# Save the results to a new XML file
doc.to_xml_file("examples/ISic000032_tokenized.xml")
```

### Corpus level analysis

Given a corpus of EpiDoc XML files in a folder ```corpus/``` in the current working directory, the following code filters the corpus and writes a text file containing the ids of all Latin funerary inscriptions from Catania / Catina:

```python
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.enums import TextClass
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

### Validate EpiDoc XML

There are two ways to validate an EpiDoc XML file: 

1. Validate on load, e.g.:

```python
from pyepidoc import EpiDoc

doc = EpiDoc('examples/ISic000001_tokenized.xml', validate_on_load=True)
```

- This validates according to the RelaxNG schema `tei-epidoc.rng` 
in the `pyepidoc` root directory.
- By default `validate_on_load` is set to `False`.

2. Validate against a custom RelaxNG schema:

```python
from pyepidoc import EpiDoc
doc = EpiDoc('examples/ISic000001_tokenized.xml')

doc.validate_by_relaxng(fp='path/to/relaxngschema.rng')
```

# Code organisation

## Package structure

The PyEpiDoc package has four subpackages:

- `xml` containing modules with base classes for XML handling;
- `epidoc` containing modules for handling EpiDoc specific XML handling, e.g. ```<ab>```, ```<w>``` etc.;
- `analysis` containing modules for analysing EpiDoc files and corpora, e.g. of abbreviations;
- `shared` containing modules and classes for use generally in the project.

Probably the most useful subpackage in the first instance will be `epidoc`, and in particular 
`epidoc.py` and `corpus.py`, which, via the classes `EpiDoc` and `EpiDocCorpus`, provide
APIs to EpiDoc files and corpora respectively.


## Modifying tokenizer behaviour

The treatment of a given token by the tokenizer may be affected by one or more of the following:

- Status in ```pyepidoc/epidoc/epidoctypes.py```
- Presence in ```pyepidoc/constants.py``` in ```SubsumableRels```

The token will be subsumed into a neighbouring ```<w>``` token if it is not separated by whitespace if:
- it is listed in as a ```dep``` of e.g. ```<w>``` in ```SubsumableRels```

The token will be subsumed into a neighbouring ```<w>``` token regardless of the presence of intervening whitespace if:
- it is listed in as a ```dep``` of e.g. ```<w>``` in ```SubsumableRels``` and
- it is a member of ```AlwaysSubsumableType``` in ```epidoctypes.py```

# Code integrity

## Run the tests

with ```pytest``` installed (the dev installation will do this for you):


2. To run all the tests, in the project root directory, type:

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

## Features to be included in future

### XML comments

XML comments should now be handled correctly, and reproduced in new files.

## Dependencies

PyEpiDoc depends on [lxml](https://lxml.de/) ([BSD](https://github.com/lxml/lxml/blob/master/LICENSE.txt)). 
Development dependencies are [mypy](https://mypy.readthedocs.io/en/stable/) ([MIT](https://github.com/python/mypy/blob/master/LICENSE)), [pytest](https://docs.pytest.org/en/7.4.x/) ([MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE)) and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) ([MIT](https://github.com/pytest-dev/pytest-cov?tab=MIT-1-ov-file#readme)). Licenses for these dependencies are included in the `LICENSES` directory.


## Acknowledgements and licencing

- The software for PyEpiDoc was written by Robert Crellin as part of the Crossreads project at the Faculty of Classics, University of Oxford, and is licensed under the MIT license (see [LICENSES/LICENSE-pyepidoc](LICENSES/LICENSE-pyepidoc)). 

- Example and test ```.xml``` files, contained in the ```examples/```, ```example_corpus/``` and ```tests/``` subfolders, as well as elsewhere in the source code, are either directly form, or derived from, the [I.Sicily corpus](https://github.com/ISicily/ISicily), which are made available under the [CC-BY-4.0 licence](https://creativecommons.org/licenses/by/4.0/) (see [LICENSES/LICENSE-texts](LICENSES/LICENSE-texts)).

- The [TEI EpiDoc schema](src/pyepidoc/tei-epidoc.rng) is licensed under the GNU General Public license (see the license on the [EpiDoc repository](https://github.com/EpiDoc/Source/blob/main/schema/LICENSE.txt)).

- For further details and acknowledgements on the generation of ISicily token IDs (```pyepidoc/epidoc/ids```), see [https://github.com/rsdc2/ISicID](https://github.com/rsdc2/ISicID).


## Funding

This project has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation programme (grant agreement No 885040, “Crossreads”).

<div>
  <img align="left" valign="center" src="assets/ISicily.jpg?raw=true" alt="isicily logo" height="80" >
  <img align="left" valign="center" src="assets/oxford.png?raw=true" alt="oxford logo" height="80"  style="padding-top: 80px" >
  <img align="left" valign="center" src="assets/EU_ERC.jpg?raw=true" alt="erc logo" height="80" >
</div>
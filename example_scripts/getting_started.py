# Load the API
from pyepidoc import EpiDoc, EpiDocCorpus

# Load an EpiDoc file without validation
doc = EpiDoc('examples/ISic000001_tokenized.xml')

# Load an EpiDoc file and validate
doc2 = EpiDoc('examples/ISic000001_tokenized.xml', validate_on_load=True)

# Print normalized tokens as a string
print(doc.text_normalized)

# Print Leiden tokens as a string
print(doc.text_leiden)

# Print the translation text
print(doc.translation_text)
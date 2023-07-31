
from pyepidoc import EpiDoc

# Load the EpiDoc file
doc = EpiDoc("examples/ISic000032_untokenized.xml")

# Tokenize the edition
doc.tokenize()

# Prettify the <div type="edition"> XML
doc.prettify_edition()

# Add spaces between tokens
doc.space_tokens()

# Print list of tokens
print('Tokens: ', doc.tokens_list_str)

# Print list of complete tokens
complete = [token for token in doc.tokens if not token.has_gap()]
print('Complete tokens: ', complete)

# Save the results to a new XML file
# Creates the folderpath if it does not exist
doc.to_xml("examples/ISic000032_tokenized.xml", create_folderpath=True)
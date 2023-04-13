from pyepidoc import EpiDoc

# Load the EpiDoc file
doc = EpiDoc("examples/ISic000032_untokenized.xml")

# Tokenize the edition
doc.tokenize()

# Prettify
doc.prettify_edition()

# Add spaces between tokens
doc.add_space_between_tokens()

# Save the results to a new XML file
doc.to_xml("examples/ISic000032_tokenized.xml")

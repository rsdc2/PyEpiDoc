from pyepidoc import EpiDoc

def save_and_reload(doc: EpiDoc, path: str) -> EpiDoc:
    """
    Saves an EpiDoc file and reloads it; 
    for use in testing to check properties of 
    modified files.
    """

    doc.to_xml_file(path)
    return EpiDoc(path)
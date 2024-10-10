from __future__ import annotations
from pathlib import Path
from pyepidoc import EpiDoc

def save_and_reload(doc: EpiDoc, path: str | Path) -> EpiDoc:
    
    """
    Saves an EpiDoc file and reloads it; 
    for use in testing to check properties of 
    modified files.
    """

    doc.to_xml_file(path)
    return EpiDoc(path)


def save_reload_and_compare(
        doc: EpiDoc, 
        target_path: str | Path, 
        benchmark: str | Path) -> bool:

    """
    Saves an EpiDoc file, reloads it and checks it against a benchmark file.
    """

    doc_ = save_and_reload(doc, target_path)
    benchmark_doc = EpiDoc(benchmark)

    return doc_.xml_byte_str == benchmark_doc.xml_byte_str



        
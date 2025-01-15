from __future__ import annotations
from pathlib import Path
from typing import Literal
from pyepidoc import EpiDoc
from pyepidoc.shared.types import FileWriteMode


def save_and_reload(doc: EpiDoc, path: str | Path) -> EpiDoc:
    
    """
    Saves an EpiDoc file and reloads it; 
    for use in testing to check properties of 
    modified files.
    """

    doc.to_xml_file(path, collapse_empty_elements=True)
    return EpiDoc(path)


def save_and_reload_to_file_object(doc: EpiDoc) -> EpiDoc:
    """
    Saves an EpiDoc file object and reloads the EpiDoc file from the object; 
    for use in testing to check properties of modified files.
    """

    f = doc.to_xml_file_object(collapse_empty_elements=True)
    return EpiDoc(f)


def save_reload_and_compare_with_benchmark(
        doc: EpiDoc, 
        target_path: str | Path, 
        benchmark_path: str | Path,
        output_write_mode: FileWriteMode) -> bool:

    """
    Saves an EpiDoc file, reloads it and checks it against a benchmark file.
    """
    if output_write_mode == 'file_object':
        doc_ = save_and_reload_to_file_object(doc)
    elif output_write_mode == 'file_on_disk':
        doc_ = save_and_reload(doc, target_path)
        
    benchmark_doc = EpiDoc(benchmark_path)
    return doc_.xml_byte_str == benchmark_doc.xml_byte_str

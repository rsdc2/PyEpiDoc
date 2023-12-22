from __future__ import annotations
import csv
from pathlib import Path
from .overall import overall_distribution_via_expans 
from pyepidoc import EpiDocCorpus
from ..utils.csv_ops import pivot_dict


def overall_analysis_to_csv(
        corpus: EpiDocCorpus, 
        filepath: str | Path) -> None:
    
    """
    Writes overall analysis of abbreviation 
    distribution to CSV file
    """

    fp = Path(filepath)
    f = open(fp, mode='w')
    d = overall_distribution_via_expans(corpus)
    list_dict = pivot_dict(d)
    fieldnames = list(list_dict[0].keys())
    
    writer = csv.DictWriter(f, fieldnames)
    writer.writeheader()
    writer.writerows(list_dict)

    f.close()
from __future__ import annotations
import csv
from pathlib import Path
from typing import Literal, Optional

from .distribution import overall_distribution_via_expans 
from .instances import raw_abbreviations, abbreviation_count

from pyepidoc.epidoc.enums import AbbrType
from pyepidoc import EpiDocCorpus
from pyepidoc.shared.csv import pivot_dict


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

    print(f'Written results to {fp}...')
    f.close()


def abbr_count_to_csv(
        fp: str, 
        corpus: EpiDocCorpus, 
        language: Optional[Literal['la', 'grc']]=None, 
        abbr_type: Optional[AbbrType]=None
    ) -> None:
    
    """
    Writes abbreviation frequencies to CSV file
    """
    
    raw = raw_abbreviations(
        corpus, 
        abbr_type=abbr_type, 
        language=language
    )
    count = abbreviation_count(raw)
    count_dict = {k: {'frequency': v['frequency'], 'isic_ids': f'{", ".join(list(v["isic_ids"]))}'} 
                  for k, v in count.items()}

    list_dict = pivot_dict(count_dict)
    sorted_list_dict = sorted(
        list_dict, 
        key=lambda result: result['frequency'], reverse=True
    )
    
    if len(sorted_list_dict) == 0:  # Abort if there are no records
        print(f'Aborting with {fp} since there are no records.')
        return 
    
    fieldnames = list(sorted_list_dict[0].keys())
    csv_file = open(fp, mode='w')
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    print(f'Writing {fp}...')
    writer.writeheader()
    writer.writerows(sorted_list_dict)
    csv_file.close()


def abbr_count_all_to_csvs(
        corpus: EpiDocCorpus, 
        output_filename_prefix: str='') -> None:
    
    """
    Writes out frequency CSVs for all permutations
    """

    abbr_types = [
        AbbrType.suspension, 
        AbbrType.contraction, 
        AbbrType.contraction_with_suspension, 
        AbbrType.multiplication
    ]

    Lang = Literal['la', 'grc']
    langs = list[Lang](['la', 'grc'])

    for lang in langs:
        for abbr_type in abbr_types:
            abbr_count_to_csv(
                f'{output_filename_prefix}{lang}_{abbr_type.value}.csv', 
                corpus=corpus, 
                language=lang, 
                abbr_type=abbr_type)

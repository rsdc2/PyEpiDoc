from typing import Any

def pivot_dict(d: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:

    """
    Converts a dict of dicts into a list of dicts for output to
    CSV
    """

    row_names = list(d.keys())
    list_dict = list[dict[str, str]]()

    for row_name in row_names:
        list_dict += [{'': row_name, **d[row_name]}]

    return list_dict
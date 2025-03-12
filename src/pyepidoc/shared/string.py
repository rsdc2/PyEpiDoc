
def format_year(year: int) -> str:
    """
    Format an int representing a year in the format
    {year} BCE / CE
    """

    if year < 0:
        return f'{abs(year)} BCE'
    else:
        return f'{abs(year)} CE'
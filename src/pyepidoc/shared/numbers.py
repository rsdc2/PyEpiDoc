def percentage(
        x: int | float, 
        y: int | float, 
        decimal_places: int = 1) -> float:

    """
    Calculate the percentage and round to `decimal_places`
    """
    if y == 0: 
        return -1

    return round((x / y) * 100, decimal_places)
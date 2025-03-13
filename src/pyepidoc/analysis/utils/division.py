
class Division:

    """
    Convenience class for handling division-related operations
    including calculating percentages
    """

    _numerator: int | float
    _denominator: int | float

    def __init__(
            self, 
            numerator: float | int, 
            denominator: float | int) -> None:
        
        self._numerator = numerator
        self._denominator = denominator

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'Division(num: {self._numerator}, denom: {self._denominator}, value: {self._eval()}, pc: {self.percentage(2)})'

    @property
    def division_by_zero(self) -> bool:
        return self._denominator == 0

    def _eval(self) -> float:
        return self._numerator / self._denominator

    def percentage(self, digits: int = 2) -> float:
        division = self._eval() * 100
        return round(division, digits)
    
    @property
    def value(self) -> float:
        return self._eval()

class CompressedIDLengthError(Exception):
    """
    Class for handling errors associated with ID generation
    and conversion
    """

    def __init__(self, length: int):
        msg = f'Value is of incorrect length ({length}): should be 5'
        self.args = (msg,)


class UncompressedIDLengthError(Exception):
    """
    Class for handling errors associated with ID generation
    and conversion
    """

    def __init__(self, actual_length: int, required_length: int):
        msg = (f'Value is of incorrect length ({actual_length}): '
               f'should be {required_length}')
        self.args = (msg,)


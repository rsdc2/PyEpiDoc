
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


class IDSizeError(Exception):
    """
    Class for handling errors where the integer size of an ID is 
    too big
    """

    def __init__(self, actual_size: int, required_size: int):
        msg = (f'Value is too big ({actual_size}): '
               f'should be less than or equal to {required_size}')
        self.args = (msg,)
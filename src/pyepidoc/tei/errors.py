
class TEINSError(Exception):
    def __init__(self, msg: str = ""):
        self.args = (f'TEI namespace error: + {msg}',)
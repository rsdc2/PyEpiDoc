class TEINSError(Exception):
    def __init__(self):
        self.args = ('No TEI namespace "http://www.tei-c.org/ns/1.0" present',)
from typing import Optional
import re

class Namespace:

    def __init__(self):
        pass

    @classmethod
    def give_ns(cls, name:str, ns:Optional[str]) -> str:
        return cls.give_brace(ns) + name

    @staticmethod
    def give_brace(ns:Optional[str]) -> str:
        if ns is None:
            return ""

        return "{" + ns + "}"

    @staticmethod
    def remove_ns(tag_with_ns:str) -> str:
        pattern = r'^\{.+?\}'
        return re.sub(pattern, '', tag_with_ns)
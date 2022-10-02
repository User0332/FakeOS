import ast

dumps = str
dump = lambda obj, f: f.write(dumps(obj))
loads = ast.literal_eval
load = lambda f: loads(f.read())

class Object:
    def __init__(self, obj: dict):
        self.__dict__ = obj

    @classmethod
    def fromstr(cls, obj: str):
        return cls(loads(obj))
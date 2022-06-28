import ast

dumps = str
dump = lambda obj, f: f.write(dumps(obj))
loads = ast.literal_eval
load = lambda f: loads(f.read())
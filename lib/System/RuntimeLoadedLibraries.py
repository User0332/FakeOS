from .IO import File, M_RDONLY
from .Locals import *
from importlib import import_module

def ImportAttribute(filename, attr):
	mod = File(filename, M_RDONLY)
	code = mod.Read()
	
	with open("System/systemp.py", "w") as f:
		f.write(code)

	module = import_module("System.systemp")

	with open("System/systemp.py", "w") as f:
		pass

	if hasattr(module, attr):
		return getattr(module, attr)
	else:
		return NULL

def ImportLibrary(filename):
	mod = File(filename, M_RDONLY)
	code = mod.Read()

	with open("System/systemp.py", "w") as f:
		f.write(code)


	module = import_module("System.systemp")

	with open("System/systemp.py", "w") as f:
		pass

	return module
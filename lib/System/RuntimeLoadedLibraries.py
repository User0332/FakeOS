from System.IO import File
from System.Locals import *
from importlib import import_module

def ImportAttribute(filename, attr):
	mod = File(filename)
	code = mod.ReadAll()
	
	with open("System/systemp.py", "w") as f:
		f.write(code)

	print(code)
	module = import_module("System.systemp")

	with open("System/systemp.py", "w") as f:
		pass

	if hasattr(module, attr):
		return getattr(module, attr)
	else:
		return NULL

def ImportLibrary(filename):
	mod = File(filename)
	code = mod.ReadAll()

	with open("System/systemp.py", "w") as f:
		f.write(code)


	module = import_module("System.systemp")

	with open("System/systemp.py", "w") as f:
		pass

	return module

def LoadToFile(libname, filename):
	mod = File(libname)
	code = mod.ReadAll()
	
	try:
		with open(filename, "w") as f:
			f.write(code)
	except OSError as e:
		return e
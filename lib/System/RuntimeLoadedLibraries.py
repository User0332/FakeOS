def ImportAttribute(filename, attr):
	from System.IO import File, Console
	from System.Locals import NULL
	from importlib import import_module

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
		Console.ErrWriteLine(f"Could not find attribute {attr} in module {filename}")
		return NULL

def ImportLibrary(filename):
	from System.IO import File
	from importlib import import_module

	mod = File(filename)
	code = mod.ReadAll()

	with open("System/systemp.py", "w") as f:
		f.write(code)


	module = import_module("System.systemp")

	with open("System/systemp.py", "w") as f:
		pass

	return module

def LoadToFile(libname, filename):
	from System.IO import File
	mod = File(libname)
	code = mod.ReadAll()
	
	try:
		with open(filename, "w") as f:
			f.write(code)
	except OSError as e:
		return e
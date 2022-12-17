from .IO import File, M_RDONLY
from .Locals import *
from importlib import import_module
import os

class AttributeNotFound(Exception):
	def __init__(self, mod: str, attr: str): 
		self.mod = mod
		self.attr = attr

	def __str__(self):
		return f"Module '{self.mod}' doesn't contain attribute '{self.attr}'!"

_systemp = "lib/System/systemp.py"

def ImportAttribute(filename, attr):
	module = ImportLibrary(filename)

	if hasattr(module, attr):
		return getattr(module, attr)
	
	raise AttributeNotFound(filename, attr)

def ImportLibrary(filename):
	mod = File(filename, M_RDONLY)
	code = mod.Read()

	with open(_systemp, 'w') as f:
		f.write(code)


	module = import_module("System.systemp")

	open(_systemp, 'w').close()

	return module
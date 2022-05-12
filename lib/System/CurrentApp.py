from System.Locals import *
from System.Machine.FakeOS import AwaitSystemResponse

def InitApp():
	with open("other/init.fakeos", "w") as f:
		f.write("True")

	return AwaitSystemResponse()
	

def AddFlag(flagname):
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{"type" : "AppendApplicationFlag", "data" : "{flagname}"}')
	
	return AwaitSystemResponse()
	

def RemoveFlag(flagname):
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{"type" : "RemoveApplicationFlag", "data" : "{flagname}"}}')

	return AwaitSystemResponse()

def GetFlags():
	with open(f"proc/{PROC_ID}/flags.fakeos", "r") as f:
		return f.read().splitlines()
from .Locals import *
from .PyDict import dump
from .Machine.FakeOS import AwaitSystemResponse

def InitApp() -> SYS_RESP:
	with open("other/init.fakeos", "w") as f:
		f.write("True")

	return AwaitSystemResponse()
	

def AddFlag(flagname: str) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		dump(
			{
				"type" : "AppendApplicationFlag", 
				"data" : f'"{flagname}"'
			},
			f
		)
	
	return AwaitSystemResponse()
	

def RemoveFlag(flagname: str) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		dump(
			{
				"type" : "RemoveApplicationFlag",
				"data" : f'"{flagname}"'
			},
			f
		)

	return AwaitSystemResponse()

def GetFlags():
	with open(f"proc/{PROC_ID}/flags.fakeos", "r") as f:
		return f.read().splitlines()
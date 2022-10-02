from .Locals import *
from .PyDict import dump
from .Machine.FakeOS import AwaitSystemResponse
from os import listdir

def Kill(proc_id: int) -> SYS_RESP:
	with open(REQUEST_FILE, "w") as f:
		dump(
			{
				"type" : "KillProcess", 
				"data" : proc_id
			},
			f
		)
	
	if proc_id == PROC_ID: # process is killing itself
		return
	
	return AwaitSystemResponse()

def GetRunningProcesses() -> list:
	return listdir('proc')

def InitProcess(*args) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		dump(
			{
				"type" : "InitProcess", 
				"data" : args
			},
			f
		)

	return AwaitSystemResponse()

def GetProcessFlags(proc_id) -> list:
	with open(f'proc/{proc_id}/flags.fakeos', 'r') as f:
		return f.read().splitlines()
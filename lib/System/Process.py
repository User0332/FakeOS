from .Locals import *
from .PyDict import dump
from .Machine.FakeOS import (
	AwaitSystemResponse, 
	WriteRequest,
	SystemError
)
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

def GetRunningProcesses() -> list[int]:
	return [
		int(x) for x in listdir('proc')
	]

def InitProcess(args: list[str], stdin: str=None, stdout: str=None, stderr: str=None) -> int:
	resp = WriteRequest(
		{
			"type" : "InitProcess", 
			"data" : {
				"args": args,
				"iostreams": [
					stdin, 
					stdout, 
					stderr
				]
			}
		}
	)

	if resp["code"] != 2:
		raise SystemError(resp["value"])

	return resp["value"]
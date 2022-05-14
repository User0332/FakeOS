from System.Locals import *
from System.Machine.FakeOS import AwaitSystemResponse
from os import listdir

def Kill(proc_id) -> SYS_RESP:
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{ "type" : "KillProcess", "data" : {proc_id} }}')
	
	return AwaitSystemResponse()

def GetRunningProcesses() -> list:
	return listdir('proc')

def InitProcess(*args) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "InitProcess", "data" : {str(list(args)).replace(chr(39), chr(34))} }}')

	return AwaitSystemResponse()

def GetProcessFlags(proc_id) -> list:
	with open(f'proc/{proc_id}/flags.fakeos', 'r') as f:
		return f.read().splitlines()
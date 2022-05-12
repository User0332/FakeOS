from System.Locals import *
from System.Machine.FakeOS import AwaitSystemResponse

def Kill(proc_id):
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{ "type" : "KillProcess", "data" : {proc_id} }}')
	
	return AwaitSystemResponse()

def GetRunningProcesses():
	from os import listdir

	return listdir('proc')

def InitProcess(*args):
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "InitProcess", "data" : {str(list(args)).replace(chr(39), chr(34))} }}')

	return AwaitSystemResponse()

def GetProcessFlags(proc_id):
	with open(f'proc/{proc_id}/flags.fakeos', 'r') as f:
		return f.read().splitlines()
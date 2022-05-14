from System.Locals import *
from json import load
from os.path import getsize

def SysCommand(command) -> SYS_RESP:
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{"type" : "SystemCommand", "data" : "{command}"}}')

	return AwaitSystemResponse()

def AwaitSystemResponse() -> SYS_RESP:

	data = ""

	while getsize(RESPONSE_FILE) == 0: pass #wait for sys to write response

	with open(RESPONSE_FILE, "r") as f:
		data = load(f)

	response_code = data['code']
	value = data['value']

	open(RESPONSE_FILE, "w").close() #clear response
		
	return response_code, value
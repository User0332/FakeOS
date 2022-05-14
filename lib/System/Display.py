from System.Locals import *
from System.Machine.FakeOS import AwaitSystemResponse

def ChangePixel(pos, color) -> SYS_RESP:
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{ "type" : "ChangePixel", "data" : [{list(pos)}, {list(color)}] }}')

	return AwaitSystemResponse()

def ChangeBackground(color) -> SYS_RESP:
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{ "type" : "ChangeBackground", "data" : {list(color)}}}')

	return AwaitSystemResponse()
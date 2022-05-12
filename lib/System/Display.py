from System.Locals import *
from System.Machine.FakeOS import AwaitSystemResponse

def ChangePixel(pos, color):
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{ "type" : "ChangePixel", "data" : [{list(pos)}, {list(color)}] }}')

	return AwaitSystemResponse()


def GetPixels():
	import ast

	with open("display/pixel.fakeos") as f:
		data = ast.literal_eval(f.read())

	return data

def ChangeBackground(color):
	with open(REQUEST_FILE, "w") as f:
		f.write(f'{{ "type" : "ChangeBackground", "data" : {list(color)}}}')

	return AwaitSystemResponse()
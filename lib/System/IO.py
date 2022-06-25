from .Locals import *
from json import load, loads, dumps
from .Machine.FakeOS import AwaitSystemResponse, SystemError

M_RDONLY = 0
M_WRONLY = 1

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

class File:
	def __init__(self, filename: str, mode: int) -> None:
		res = OpenFile(filename, mode)
		if res[0]["code"] not in (1, 2):
			raise SystemError(res[0]["value"])

		self._fd = res["data"]

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.Close()

	def Write(self, buff) -> int:
		res = WriteFile(self._fd, buff)

		if res[0]["code"] not in (1, 2):
			raise SystemError(res[0]["value"])
		
		return res["data"]

	def Read(self, numb: int=None) -> str:
		if numb == None:
			with open(f"proc/{PROC_ID}/fd/table.json", 'r') as f:
				numb = len(load(f)[self._fd]["contents"])

		res = ReadFile(self._fd, numb)

		if res[0]["code"] not in (1, 2):
			raise SystemError(res[0]["value"])
		
		return res["data"]

	def Seek(self, offset: int, whence: int) -> int:
		res = SeekFile(self._fd, offset, whence)
		if res[0]["code"] not in (1, 2):
			raise SystemError(res[0]["value"])
		return res["data"]

	def Tell(self) -> int:
		res = Tell(self._fd)
		if res[0]["code"] not in (1, 2):
			raise SystemError(res[0]["value"])

		return res["data"]

	def Close(self) -> None:
		res = Close(self._fd)
		
		if res[0]["code"] not in (1, 2):
			raise SystemError(res[0]["value"])

	def LoadJSON(self) -> dict:
		return loads(self.Read())

	def DumpJSON(self, json: dict) -> None:
		return self.Write(dumps(dict))

	def __del__(self) -> None:
		if hasattr(self, '_fd'):
			self.Close()
		
				
	

def OpenFile(filename: str, mode: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.OpenFile", "data" : {{ "filename" : {filename}, "mode" : {mode} }} }}')

	return AwaitSystemResponse()

def SeekFile(fd: int, offset: int, whence: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.SeekFile", "data" : {{ "fd" : {fd}, "offset" : {offset}, "whence" : {whence} }} }}')

	return AwaitSystemResponse()

def Tell(fd: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.Tell", "data" : {{ "fd" : {fd} }} }}')

	return AwaitSystemResponse()

def WriteFile(fd: int, buff: str) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.WriteFile", "data" : {{ "fd" : {fd}, "buff" : buff }} }}')

	return AwaitSystemResponse()

def ReadFile(fd: int, numb: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.ReadFile", "data" : {{ "fd" : {fd}, "numb" : numb }} }}')

	return AwaitSystemResponse()
	
def Close(fd: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.Close", "data" : {{ "fd" : {fd} }}')

	return AwaitSystemResponse()
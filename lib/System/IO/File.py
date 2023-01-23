from os.path import normpath as os_norm
from ..Locals import *
from ..PyDict import load, loads, dumps
from ..Machine.FakeOS import (
	AwaitSystemResponse, 
	GetCwd,
	NormPath,
	SystemError
)

M_RDONLY = 0
M_WRONLY = 1
M_RBYTES = 2
M_WBYTES = 3

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

class IOBase: pass

class File(IOBase):
	def __init__(self, filename: str, mode: Union[int, str]) -> None:
		if isinstance(mode, str):
			if mode == 'r': mode = M_RDONLY
			elif mode == 'w': mode = M_WRONLY
			elif mode == 'rb': mode = M_RBYTES
			elif mode == 'wb': mode = M_WBYTES
			else: mode = None #invalid mode for sys to throw error


		res = OpenFile(filename, mode)
		if res["code"] not in (1, 2):
			raise SystemError(res["value"])

		self._fd = res["value"]
		self.filename = filename
		self.mode = mode

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.Close()

	def Write(self, buff: Union[str, bytes]) -> int:
		res = WriteFile(self._fd, buff)

		if res["code"] not in (1, 2):
			raise SystemError(res["value"])
		
		return res["value"]

	def Read(self, numb: int=None) -> Union[str, bytes]:
		if numb == None:
			with open(f"proc/{PROC_ID}/fd/table.py", 'r') as f:
				numb = len(load(f)[self._fd]["contents"])

		res = ReadFile(self._fd, numb)

		if res["code"] not in (1, 2):
			raise SystemError(res["value"])
		
		return res["value"]

	def Seek(self, offset: int, whence: int) -> int:
		res = SeekFile(self._fd, offset, whence)
		if res["code"] not in (1, 2):
			raise SystemError(res["value"])
		return res["value"]

	def Tell(self) -> int:
		res = Tell(self._fd)
		if res["code"] not in (1, 2):
			raise SystemError(res["value"])

		return res["value"]

	def Close(self) -> None:
		res = Close(self._fd)
		
		if res["code"] not in (1, 2):
			raise SystemError(res["value"])

	def LoadPyDict(self) -> dict:
		return loads(self.Read())

	def DumpPyDict(self, dictionary: dict) -> None:
		return self.Write(dumps(dictionary))

	def __del__(self) -> None:
		if hasattr(self, '_fd'):
			self.Close()

class UnOpenedFile(IOBase):
	def __init__(self, filename: str, mode: Union[int, str]) -> None:
		self.mode = mode
		self.filename = filename

	def Open(self) -> File:
		return File(
			self.filename,
			self.mode
		)

	def Write(self, buff: Union[str, bytes], mode=None) -> int:
		if mode: return UnOpenedFile(self.filename, mode).Write(buff)
		return self.Open().Write(buff)

	def Read(self, numb: int=None, mode=None) -> Union[str, bytes]:
		if mode: return UnOpenedFile(self.filename, mode).Read(numb)
		return self.Open().Read(numb)

	def Seek(self, offset: int, whence: int) -> int:
		return self.Open().Seek(offset, whence)

	def Tell(self) -> int:
		return self.Open().Tell()

def OpenFile(filename: str, mode: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.OpenFile", "data" : {{ "filename" : "{NormPath(GetCwd()+filename)}", "mode" : {mode} }} }}')

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
		f.write(f'{{ "type" : "Sys.WriteFile", "data" : {{ "fd" : {fd}, "buff" : "{buff}" }} }}')

	return AwaitSystemResponse()

def ReadFile(fd: int, numb: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.ReadFile", "data" : {{ "fd" : {fd}, "numb" : {numb} }} }}')

	return AwaitSystemResponse()
	
def Close(fd: int) -> SYS_RESP:
	with open(REQUEST_FILE, 'w') as f:
		f.write(f'{{ "type" : "Sys.Close", "data" : {{ "fd" : {fd} }} }}')

	return AwaitSystemResponse()
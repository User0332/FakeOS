from ..Locals import *
from ..PyDict import load, dump
from ..Process import InitProcess
from os.path import getsize

class SystemError(Exception): pass

class StatObject:
	def __init__(self, name: str, path: str, size: int):
		self.name = name
		self.path = path
		self.size = size

_CWD = '/' # set this to the directory the process was launched in

def _RetrieveFileSystemObject() -> dict:
	with open("filesystem/files.py", 'r') as f:
		return load(f)

def _SetFileSystemObject(filesystem: str) -> None:
	with open("filesystem/files.py", 'w') as f:
		dump(filesystem, f)


def _GetStart(directory: str):
	return (
		GetCwdObject()
		if not directory or directory[0] != '/' 
		else _RetrieveFileSystemObject()['/'] 
	)

def _ParseDirectory(from_dir, to_dir) -> dict:
	for dir in (x for x in to_dir.split('/') if x):
		available_dirs = from_dir['dirs']
		if dir in available_dirs:
			from_dir = from_dir['dirs'][dir]
		else:
			return None

	return from_dir

def AwaitSystemResponse() -> SYS_RESP:
	data = ""

	while getsize(RESPONSE_FILE) == 0: pass #wait for sys to write response

	with open(RESPONSE_FILE, 'r') as f:
		data = load(f)

	open(RESPONSE_FILE, 'w').close() #clear response
		
	return data

def SysCommand(command: str) -> SYS_RESP:
	return InitProcess(*command.split())

def GetCwd() -> str:
	return _CWD

def Chdir(directory: str) -> None:
	if IsDir(directory):
		if directory.startswith('/'):
			globals['_CWD'] = directory
			return
		
		globals['_CWD']+=f"{directory}/"
		return

	raise SystemError("Directory not found!")

def GetCwdObject() -> dict:
	return _ParseDirectory(_RetrieveFileSystemObject()['/'], GetCwd())
		
def Exists(path: str) -> bool:
	return IsDir(path) or IsFile(path)

def IsDir(directory: str) -> bool:
	return _ParseDirectory(_GetStart(directory), directory) is not None

def IsFile(path: str) -> bool:
	path = path.split('/')
	directory = '/'.join(path[:-1])
	file = path[-1]
	
	if not IsDir(directory):
		return False

	return file in ListFilesInDir(directory)
		

def ListFilesInDir(directory: str) -> list:
	if not IsDir(directory):
		raise SystemError("Directory not found!")

	dirobj = _ParseDirectory(_GetStart(directory), directory)
	
	return list(dirobj['files'].keys())

def ListDirsInDir(directory: str) -> list:
	if not IsDir(directory):
		raise SystemError("Directory not found!")

	dirobj = _ParseDirectory(_GetStart(directory), directory)
	
	return list(dirobj['dirs'].keys())

def ListDir(directory: str) -> list:
	return ListFilesInDir(directory)+ListDirsInDir(directory)

def Stat(path: str) -> StatObject:
	if not IsFile(path):
		raise SystemError("File not found!")

	path = path.split('/')
	directory = '/'.join(path[:-1])
	filename = path[-1]

	dirobj = _ParseDirectory(_GetStart(directory), directory)

	return StatObject(
		filename, 
		path, 
		len(dirobj["files"][filename])
	)
"""REQ - Fulfiller of program requests and 'Real Execution Queries'

This module provides an interface to the kernel-level FakeOS functions. 
Functions called from this library are executed on the spot, you do not 
have to wait for a system response. It is recommended that you use the 
System API and not this library for executing functions. All modules in 
the src/ folder should only be used by the kernel. This library also 
contains a function for reading and responding to requests from programs.
That function, fulfill_requests, is called periodically by the system. 
All functions in the System API except for most under System.Machine 
eventually correspond to one or more indirect (through the request system) 
calls to this library."""

import os
import subprocess
import shutil
import pygame
import dill
import sys
from typing import TypedDict, Union
from types import ModuleType, FunctionType
import System.PyDict as json
from System.Machine.FakeOS import (
	_ParseDirectory, 
	_RetrieveFileSystemObject, 
	_SetFileSystemObject, 
	IsFile,
	ListFilesInDir,
	Stat,
	NormPath,
	SystemError
)
from System.IO import (
	M_RDONLY,
	M_WRONLY,
	M_RBYTES,
	M_WBYTES,
	SEEK_SET,
	SEEK_CUR,
	SEEK_END,
)

class DescriptorTableEntry(TypedDict):
	contents: Union[bytes, None]
	filename: str
	mode: int
	pos: int

class WindowType(TypedDict):
	id: str
	x: int
	y: int
	surface: pygame.Surface
	rect: pygame.Rect
	closerect: pygame.Rect
	vars: dict[str]
	update: FunctionType
	event_handler: FunctionType

class ProcType(TypedDict):
	name: str
	module: Union[ModuleType, subprocess.Popen]
	windows: list[WindowType]

procs: dict[int, ProcType] = {
	0 : {
		"name" : "sys",
		"module" : sys.modules['__main__'],
		"windows": []
	}
}

NO_RESP = 257
IN_USE = []

def GetPath() -> list[str]:
	syspathfd = Sys_OpenFile("/cfg/system.path", M_RDONLY, 0)["value"]
	path: list[str] = Sys_ReadFile(syspathfd, Stat("/cfg/system.path").size, 0)["value"].splitlines()
	Sys_Close(syspathfd, 0)
	return path

def GetAbsolutePath(filename: str) -> str:
	for path in GetPath():
		try: files_in_dir = ListFilesInDir(path)
		except SystemError: continue

		if filename in files_in_dir:
			return f"{path}/{filename}"

def FileIsInPath(filename: str) -> bool:
	return (GetAbsolutePath(filename) is not None)

def LoadToFile(filename: str, win_filename: str, proc_id: int):
	mod = Sys_OpenFile(filename, M_RDONLY, proc_id)["value"]

	numb = Stat(filename).size

	code = Sys_ReadFile(mod, numb, proc_id)["value"]
	
	try:
		with open(win_filename, "w") as f:
			f.write(code)
	except OSError as e:
		return e
	finally:
		Sys_Close(mod, proc_id)

def _GetDescriptorTable(proc_id) -> dict[int, DescriptorTableEntry]:
	with open(f"proc/{proc_id}/fd/table.py", 'r') as f:
		return json.load(f)

def _WriteDescriptorTable(proc_id, table: dict[int, DescriptorTableEntry]) -> None:
	with open(f"proc/{proc_id}/fd/table.py", 'w') as f:
		json.dump(table, f)

def Sys_OpenFile(filename: str, mode: int, proc_id: int):
	'''Returns the file descriptor of the specified file'''
	filename = NormPath(filename)

	path = filename.split('/')
	directory = '/'.join(path[:-1])
	file = path[-1]

	table = _GetDescriptorTable(proc_id)
	fd: int = max(table.keys() if table else (0,))+1

	if directory.startswith("/proc"):
		actual = filename.removeprefix('/')

		if os.path.isfile(actual):
			if mode in (M_RDONLY, M_RBYTES):
				table[fd] = {
					"mode" : mode,
					"pos" : 0,
					"filename" : filename, # for closing
					"contents" : open(actual, 'r').read()
				}

				_WriteDescriptorTable(proc_id, table)
				IN_USE.append(filename)

				return {
					"code" : 2,
					"value" : fd
				}

			elif mode in (M_WRONLY, M_WBYTES):
				open(actual, 'w').close()

				table[fd] = {
					"mode" : mode,
					"filename" : filename,
					"pos" : 0
				}

				_WriteDescriptorTable(proc_id, table)
				IN_USE.append(filename)

				return {
					"code" : 2,
					"value" : fd
				}
			else:
				return {
					"code" : 6,
					"value" : "Invalid file mode"
				}

	if not IsFile(filename) and mode in (M_RDONLY, M_RBYTES):
		return {
			"code" : 5,
			"value" : "File doesn't exist"
		}

	dirobj = _ParseDirectory(_RetrieveFileSystemObject()['/'], directory)
	
	if dirobj is None:
		return {
			"code" : 5,
			"value" : "File's directory does not exist"
		}

	if filename in IN_USE:
		return {
			"code" : 3,
			"value" : "Another process has opened this file"
		}
	
	if mode in (M_RDONLY, M_RBYTES):
		table[fd] = {
			"mode" : mode,
			"pos" : 0,
			"filename" : filename, # for closing
			"contents" : dirobj["files"][file]
		}

		_WriteDescriptorTable(proc_id, table)
		IN_USE.append(filename)

		return {
			"code" : 2,
			"value" : fd
		}
		
	if mode in (M_WRONLY, M_WBYTES):
		directory = (x for x in path[:-1] if x)
		filesystem = _RetrieveFileSystemObject()

		working_dir = filesystem['/']

		for subdir in directory:
			working_dir = working_dir['dirs'][subdir]

		working_dir['files'][file] = b"" # clear file as if opening new

		_SetFileSystemObject(filesystem)

		table[fd] = {
			"mode" : mode,
			"filename" : filename,
			"pos" : 0
		}

		_WriteDescriptorTable(proc_id, table)
		IN_USE.append(filename)

		return {
			"code" : 2,
			"value" : fd
		}

	return {
		"code" : 6,
		"value" : "Invalid file mode"
	}

def Sys_WriteFile(fd: int, buff: Union[str, bytes], proc_id: int):
	table = _GetDescriptorTable(proc_id)
	filesystem = _RetrieveFileSystemObject()
	working_dir = filesystem['/']
	
	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}

	path: str = table[fd]["filename"]
	directory = (x for x in path.split('/')[:-1] if x)
	file = path.split('/')[-1]

	if path.startswith("/proc"):
		try:
			actual = path.removeprefix('/')

			contents_len = os.path.getsize(actual)

			to_write = b""

			if table[fd]["pos"] > contents_len:
				to_write = (b'\0'*(table[fd]["pos"]-contents_len))

			if table[fd]["mode"] == M_WRONLY and type(buff) is str:
				to_write+=buff.encode()
			elif table[fd]["mode"] == M_WBYTES and type(buff) is bytes:
				to_write+=buff
			else:
				return {
					"code" : 6,
					"value" : "Invalid mode or tried to write unsupported type"
				}

			open(actual, 'wb').write(to_write)

			return {
				"code": 1,
				"value": len(to_write)
			}
		except FileNotFoundError:
			return {
				"code": 6,
				"value": "The file was removed from the host filesystem"
			}

	for subdir in directory:
		working_dir = working_dir['dirs'][subdir]

	contents = working_dir['files'][file]
	to_add = b""
		
	if table[fd]["pos"] > len(contents):
		to_add+=(b'\0'*(table[fd]["pos"]-len(contents)))

	if table[fd]["mode"] == M_WRONLY and type(buff) is str:
		contents+=to_add+buff.encode()
	elif table[fd]["mode"] == M_WBYTES and type(buff) is bytes:
		contents+=to_add+buff
	else:
		return {
			"code" : 6,
			"value" : "Invalid mode or tried to write unsupported type"
		}

	working_dir[file] = contents

	_SetFileSystemObject(filesystem)

	return {
		"code" : 1, 
		"value" : len(buff)+len(to_add)
	}

def Sys_ReadFile(fd: int, numb: int, proc_id: int):
	table = _GetDescriptorTable(proc_id)

	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}

	pos = table[fd]["pos"]

	table[fd]["pos"] = pos+numb

	_WriteDescriptorTable(proc_id, table)

	if table[fd]["mode"] ==  M_RDONLY:
		return {
			"code" : 2,
			"value" : table[fd]["contents"].decode()[pos:numb]
		}
	elif table[fd]["mode"] == M_RBYTES:
		return {
			"code" : 2,
			"value" : table[fd]["contents"][pos:numb]
		}
	else:
		return {
			"code" : 6,
			"value" :"Tried to read from a write only fd"
		}
	
def Sys_SeekFile(fd: int, offset: int, whence: int, proc_id: int):
	table = _GetDescriptorTable(proc_id)

	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}
	
	if whence == SEEK_SET:
		pos = 0
	if whence == SEEK_CUR:
		pos = table[fd]["pos"]
	if whence == SEEK_END:
		if table[fd]["mode"] == M_RDONLY:
			pos = len(table[fd]["contents"])-1
		else:
			pos = 0

	pos+=offset

	table[fd]["pos"] = pos

	_WriteDescriptorTable(proc_id, table)
	
	return {
		"code" : 1,
		"value" : pos
	}

def Sys_Tell(fd: int, proc_id: int):
	table = _GetDescriptorTable(proc_id)

	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}
		
	return {
		"code" : 2,
		"value" : table[fd]["pos"]
	}
	
def Sys_Close(fd: int, proc_id: int):
	table = _GetDescriptorTable(proc_id)

	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}

	filename = table[fd]["filename"]

	IN_USE.remove(filename)

	del table[fd]

	_WriteDescriptorTable(proc_id, table)

	return {
		"code" : 1,
		"value" : None
	}

def InitProcess(
	name: str, 
	args: list, 
	new_id: int, 
	caller_id: int, 
	caller_name: str, 
	iostreams: str
):
	if not FileIsInPath(name):
		return {
			"code" : 5,
			"value" : "execuable not found in PATH"
		}

	filename = GetAbsolutePath(name)

	try: os.mkdir(f"proc/{new_id}/")
	except FileExistsError:
		shutil.rmtree(f"proc/{new_id}/")
		os.mkdir(f"proc/{new_id}/")

	os.mkdir(f"proc/{new_id}/fd/")

	open(f"proc/{new_id}/request.fakeos", 'w').close()

	open(f"proc/{new_id}/response.fakeos", 'w').close()

	# if the process wants to use these pseudo-files
	open(f"proc/{new_id}/stdout", 'w').close()
	open(f"proc/{new_id}/stdin", 'w').close()
	open(f"proc/{new_id}/stderr", 'w').close()
	#

	with open(f"proc/{new_id}/name.fakeos", 'w') as f:
		f.write(name)

	with open(f"proc/{new_id}/parent.fakeos", 'w') as f:
		f.write(f"{caller_id} {caller_name}")

	with open(f"proc/{new_id}/fd/table.py", 'w') as f:
		f.write("{}")

	LoadToFile(filename, f"proc/{new_id}/module.fakeos", caller_id)

	procs[new_id] = {
		"name" : name,
		"module" : subprocess.Popen(["python", f"proc/{new_id}/module.fakeos"]+args),
		"windows": []
	}

	# Standard I/O stream buff files
	open(f"proc/{new_id}/iostreams.fakeos", 'w').write(iostreams)

	return {
			"code" : 2,
			"value" : new_id
	}

def AllocateWindow(caller_id: int, x: int, y: int, id: str):
	for win in procs[caller_id]["windows"]:
		if win["id"] == id: return {
			"code": 3,
			"value": "A window with the specified ID has already been allocated!"
		}

	surface = pygame.Surface((x, y))
	rect = surface.get_rect(topleft=(0, 0))

	close = pygame.image.load("assets/close.png")
	closerect = close.get_rect(topright=(x, 0))

	surface.blit(close, closerect)

	surface.fill("white")

	procs[caller_id]["windows"].append(
		{
			"id": id,
			'x': x,
			'y': y,
			"surface": surface,
			"rect": rect,
			"vars": {},
			"update": None
		}
	)

	return {
		"code": 2,
		"value": id
	}

def DeAllocateWindow(caller_id: int, id: str):
	for win in procs[caller_id]["windows"]:
		if win["id"] == id:
			
			procs[caller_id]["windows"].remove(win)
			return {
				"code": 1,
				"value": id
			}

	return {
		"code": 5,
		"value": f"No window found with id '{id}'!"
	}

def Window_EvalExpr(caller_id: int, id: str, expr: str):
	for win in procs[caller_id]["windows"]:
		if win["id"] == id:
			surface = win["surface"]
			try:
				res = eval(expr, { "window": surface, "pygame": pygame, **win["vars"] })
			except Exception as e:
				return {
					"code": 6,
					"value": str(e)
				}

			return {
				"code": 1,
				"value": dill.dumps(res)
			}

	return {
		"code": 5,
		"value": f"No window found with id '{id}'!"
	}

def Window_StoreVariable(caller_id: int, id: str, name: str, expr: str, _globals: dict[str]):
	for win in procs[caller_id]["windows"]:
		if win["id"] == id:
			try:
				res = eval(expr, { "window": win["surface"], "pygame": pygame, **win["vars"], **dill.loads(_globals) })
			except Exception as e:
				return {
					"code": 6,
					"value": str(e)
				}

			win["vars"][name] = res

			return {
				"code": 1,
				"value": f"{name}={res!r}"
			}

	return {
		"code": 5,
		"value": f"No window found with id '{id}'!"
	}

def Window_AttachUpdateFunction(caller_id: int, id: str, func: bytes):
	for win in procs[caller_id]["windows"]:
		if win["id"] == id:
			win["update"] = dill.loads(func)
			
			return {
				"code": 1,
				"value": "Update function sucessfully attached."
			}

	return {
		"code": 5,
		"value": f"No window found with id '{id}'!"
	}

def Window_AttachEventHandler(caller_id: int, id: str, func: bytes):
	for win in procs[caller_id]["windows"]:
		if win["id"] == id:
			win["event_handler"] = dill.loads(func)
			
			return {
				"code": 1,
				"value": "Event handler function sucessfully attached."
			}

	return {
		"code": 5,
		"value": f"No window found with id '{id}'!"
	}

def KillProcess(caller_id: int, id: int):
	if id in procs:
		try: procs[id]["module"].kill()
		except AttributeError: return {
			"code": 4,
			"value": "You can't kill sys!"

		} # someone is trying to kill sys?

		del procs[id]

		for file in _GetDescriptorTable(id).values():
			filename = file["filename"]

			if filename in ("<stdin>", "<stdout>", "<stderr>"):
				continue #these are fake files

			IN_USE.remove(filename)

		shutil.rmtree(f"proc/{id}")

		if id != caller_id: # if the process didn't kill itself
			return {
				"code" : 2,
				"value" : None
			}
		else:
			return NO_RESP

	return {
		"code" : 5,
		"value" : f"Process with {id=} doesn't exist!"
	}


# ?NOTE:?TODO => MAKE ASYNC?
def fulfill_reqests():
	for caller_id, caller in list(procs.items()): #use list to create a copy of the dict
		try:
			if os.path.getsize(f"proc/{caller_id}/request.fakeos") == 0: continue
		except FileNotFoundError: continue # process probably just killed
			
		directory = f"proc/{caller_id}"

		with open(f"{directory}/request.fakeos", "r") as f:
			request = json.load(f)		
			if not request: continue
			req = request["type"]
			data = request["data"]

		if req == "InitProcess":
			proc_name = data["args"][0]
			try:
				args = data["args"][1:]
			except IndexError:
				args = []

			new_id = max(procs)+1

			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					InitProcess(
						proc_name, 
						args, 
						new_id, 
						caller_id, 
						caller["name"],
						data["iostreams"]
					),
					f
				)
	
		elif req == "KillProcess":
			resp = KillProcess(caller_id, data)
			if resp is NO_RESP: continue

			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					resp,
					f
				)

		elif req == "Sys.OpenFile":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Sys_OpenFile(data["filename"], data["mode"], caller_id),
					f
				)
		elif req == "Sys.ReadFile":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Sys_ReadFile(data["fd"], data["numb"], caller_id),
					f
				)
		elif req == "Sys.WriteFile":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Sys_WriteFile(data["fd"], data["buff"], caller_id),
					f
				)
		elif req == "Sys.SeekFile":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Sys_SeekFile(data["fd"], data["offset"], data["whence"], caller_id),
					f
				)
		elif req == "Sys.Tell":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Sys_Tell(data["fd"], caller_id),
					f
				)
		elif req == "Sys.Close":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Sys_Close(data["fd"], caller_id),
					f
				)
		elif req == "Window.Allocate":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					AllocateWindow(
						caller_id, **data
					),
					f
				)
		elif req == "Window.DeAllocate":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					DeAllocateWindow(
						caller_id, data["id"]
					),
					f
				)
		elif req == "Window.EvalExpr":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Window_EvalExpr(caller_id, **data),
					f
				)
		
		elif req == "Window.StoreVariable":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Window_StoreVariable(caller_id, **data),
					f
				)
		elif req == "Window.AttachUpdateFunction":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Window_AttachUpdateFunction(caller_id, **data),
					f
				)
		elif req == "Window.AttachEventHandler":
			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					Window_AttachEventHandler(caller_id, **data),
					f
				)

		if os.path.exists(f"{directory}/request.fakeos"):
			open(f"{directory}/request.fakeos", "w").close() #clear request
		#if the file doesn't exist the process been killed
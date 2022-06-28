import os
import subprocess
import shutil
import sys
import System.PyDict as json
from System.Machine.FakeOS import (
	_ParseDirectory, 
	_RetrieveFileSystemObject, 
	_SetFileSystemObject, 
	IsFile,
	ListFilesInDir,
	Stat,
	SystemError
)
from System.IO import (
	M_RDONLY, 
	M_WRONLY, 
	SEEK_SET,
	SEEK_CUR,
	SEEK_END,
)

procs = {
	0 : {
		"name" : "sys",
		"module" : sys.modules['__main__']
	}
}

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

def _GetDescriptorTable(proc_id) -> dict:
	with open(f"proc/{proc_id}/fd/table.py", 'r') as f:
		return json.load(f)

def _WriteDescriptorTable(proc_id, table: dict) -> None:
	with open(f"proc/{proc_id}/fd/table.py", 'w') as f:
		json.dump(table, f)

def Sys_OpenFile(filename: str, mode: int, proc_id: int):
	'''Returns the file descriptor of the specified file'''
	path = filename.split('/')
	directory = '/'.join(path[:-1])
	file = path[-1]
	if not IsFile(filename) and mode == M_RDONLY:
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

	table = _GetDescriptorTable(proc_id)
	fd: int = max(table.keys())+1
	
	if mode == M_RDONLY:
		table[fd] = {
			"mode" : mode, # for compatibility with other read modes in the future
			"pos" : 0,
			"filename" : filename, # for closing
			"contents" : dirobj['files'][file]
		}

		_WriteDescriptorTable(proc_id, table)
		IN_USE.append(filename)

		return {
			"code" : 2,
			"value" : fd
		}
		
	if mode == M_WRONLY:
		directory = (x for x in path[:-1] if x)
		filesystem = _RetrieveFileSystemObject()

		working_dir = filesystem['/']

		for subdir in directory:
			working_dir = working_dir['dirs'][subdir]

		working_dir['files'][file] = "" # clear file as if opening new

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

def Sys_WriteFile(fd: int, buff: str, proc_id: int):
	table = _GetDescriptorTable(proc_id)
	filesystem = _RetrieveFileSystemObject()
	working_dir = filesystem['/']
	
	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}

	if table[fd]["mode"] !=  M_WRONLY:
		return {
			"code" : 6,
			"value" : "Tried to write to a read only fd"
		}

	path: str = table[fd]["filename"]
	directory = (x for x in path.split('/')[:-1] if x)
	file = path.split('/')[-1]

	for subdir in directory:
		working_dir = working_dir['dirs'][subdir]

	contents = working_dir['files'][file]
 
	print(contents)
		
	if table[fd]["pos"] > len(contents):
		contents+=("\0"*(table[fd]["pos"]-len(contents)))

	contents+=buff

	working_dir[file] = contents

	_SetFileSystemObject(filesystem)

	return {
		"code" : 1, 
		"value" : len(buff)
	}

def Sys_ReadFile(fd: int, numb: int, proc_id: int):
	table = _GetDescriptorTable(proc_id)

	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}

	if table[fd]["mode"] !=  M_RDONLY:
		return {
			"code" : 6,
			"value" :"Tried to read from a write only fd"
		}

	pos = table[fd]["pos"]

	table[fd]["pos"] = pos+numb

	_WriteDescriptorTable(proc_id, table)

	return {
		"code" : 2,
		"value" : table[fd]["contents"][pos:][:numb]
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

def InitProcess(name: str, args: list, new_id: int, caller_id: int, caller: dict):
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

	with open(f"proc/{new_id}/name.fakeos", 'w') as f:
		f.write(name)

	with open(f"proc/{new_id}/parent.fakeos", 'w') as f:
		f.write(f"{caller_id} {caller['name']}")

	with open(f"proc/{new_id}/fd/table.py", 'w') as f:
		json.dump(
			{
				0 : {
					"mode" : M_RDONLY,
					"pos" : 0,
					"contents" : "",
					"filename" : "<stdin>"
				},
				1 : {
					"mode" : M_WRONLY,
					"pos" : 0,
					"filename" : "<stdout>"
				},
				2 : {
					"mode" : M_WRONLY,
					"pos" : 0,
					"filename" : "<stderr>"
				}
			},
			f
		)

	LoadToFile(filename, f"proc/{new_id}/module.fakeos", caller_id)

	procs[new_id] = {
		"name" : name,
		"module" : subprocess.Popen(["python", f"proc/{new_id}/module.fakeos"]+args)
	}

	return {
			"code" : 2,
			"value" : new_id
	}


def fulfill_reqests():
	for caller_id, caller in list(procs.items()): #use list to create a copy of the dict
		if os.path.getsize(f"proc/{caller_id}/request.fakeos") == 0:
			continue
			
		directory = f"proc/{caller_id}"

		with open(f"{directory}/request.fakeos", "r") as f:
			request  = json.load(f)
			if not request: continue
			req = request['type']
			data = request['data']

		if req == "InitProcess":
			proc_name = data[0]
			try:
				args = data[1:]
			except IndexError:
				args = []

			new_id = max(procs)+1

			with open(f"{directory}/response.fakeos", 'w') as f:
				json.dump(
					InitProcess(proc_name, args, new_id, caller_id, caller),
					f
				)
	
		elif req == "KillProcess":
			if data in procs:
				procs[data]["module"].kill()
				del procs[data]

				for file in _GetDescriptorTable(data).values():
					filename = file["filename"]

					if filename in ("<stdin>", "<stdout>", "<stderr>"):
						continue #these are fake files

					IN_USE.remove(filename)

				shutil.rmtree(f"proc/{data}")

				if data != caller_id: # if the process didn't kill itself
					with open(f"{directory}/response.fakeos", "w") as f:
						response = {
							"code" : 2,
							"value" : None
						}
						json.dump(response, f)
			else:
				with open(f"{directory}/response.fakeos", "w") as f:
					response = {
						"code" : 5,
						"value" : None
					}
					json.dump(response, f)

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

		if os.path.exists(f"{directory}/request.fakeos"):
			open(f"{directory}/request.fakeos", "w").close() #clear request
		#if the file doesn't exist the process been killed
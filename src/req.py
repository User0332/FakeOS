import os
import subprocess
import json
import shutil
import sys
from System.RuntimeLoadedLibraries import LoadToFile
from System.Machine.FakeOS import (
	_ParseDirectory, 
	_RetrieveFileSystemObject, 
	_SetFileSystemObject, 
	IsFile
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

def _GetDescriptorTable(proc_id) -> dict:
	with open(f"proc/{proc_id}/fd/table.json", 'r') as f:
		return json.load(f)

def _WriteDescriptorTable(proc_id, table: dict) -> None:
	with open(f"proc/{proc_id}/fd/table.json", 'r') as f:
		json.dump(table, f)

def Sys_OpenFile(filename: str, mode: int, proc_id: int):
	'''Returns the file descriptor of the specified file'''
	path = filename.split('/')
	directory = ''.join(path[:-1])
	file = path[-1]
	if not IsFile(filename) and mode == M_RDONLY:
		return {
			"code" : 5,
			"value" : "File doesn't exist"
		}

	dirobj = _ParseDirectory('/', directory)
	
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
	fd = max(table.keys())+1
	
	if mode == M_RDONLY:
		table[fd] = {
			"mode" : mode, # for compatibility with other read modes in the future
			"pos" : 0,
			"contents" : dirobj['files'][file]
		}
		_WriteDescriptorTable(proc_id, table)
		
		return {
			"code" : 2,
			"value" : fd
		}
		
	if mode == M_WRONLY:
		table[fd] = {
			"mode" : mode,
			"file" : filename,
			"pos" : 0
		}

		_WriteDescriptorTable(table)

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

	path = table[fd]["filename"]
	directory = path.split('/')[:-1]
	file = path[-1]

	for subdir in directory:
		working_dir = working_dir['dirs'][subdir]

	contents = working_dir[file]
		
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
	table = _GetDescriptorTable()

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

	_WriteDescriptorTable(table)
	
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
	table = _GetDescriptorTable()

	if fd not in table:
		return {
			"code" : 5,
			"value" : "Bad file descriptor"
		}

	filename = table[fd]["filename"]

	IN_USE.remove(filename)

	del table[fd]

	_WriteDescriptorTable(table)

	return {
		"code" : 1,
		"value" : None
	}

def InitProcess(name: str, args: list, new_id: int, caller_id, caller):
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

	open(f"proc/{new_id}/fd/table.json", 'w').close()

	LoadToFile(name, f"proc/{new_id}/module.fakeos")

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

				for file in _GetDescriptorTable(data).items():
					filename = file["filename"]
					IN_USE.remove(filename)
				
				shutil.rmtree(f"proc/{data}")
			
				if data != caller_id:
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
import os
import subprocess
import json
import shutil
import sys
from System.RuntimeLoadedLibraries import LoadToFile

procs = {
	0 : {
		"name" : "sys",
		"module" : sys.modules['__main__']
	}
}

def fulfill_reqests():
	for caller_id, caller in list(procs.items()): #use list to create a copy of the dict
		if os.path.getsize(f"proc/{caller_id}/request.fakeos") != 0:
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

				if proc_name not in os.listdir("applications"):
					response = {
						"code" : 5,
						"value" : None
					}
					with open(f"{directory}/response.fakeos", "w") as f:
						json.dump(response, f)
				else:
					for i, procid in enumerate(procs):
						if i != procid:
							break
						elif i == len(procs)-1:
							i+=1

					try: os.mkdir(f"proc/{i}/")
					except FileExistsError:
						shutil.rmtree(f"proc/{i}/")
						os.mkdir(f"proc/{i}/")

					with open(f"proc/{i}/request.fakeos", "w") as f:
						f.write("{}")

					with open(f"proc/{i}/response.fakeos", "w") as f:
						pass

					with open(f"proc/{i}/name.fakeos", "w") as f:
						f.write(proc_name)

					with open(f"proc/{i}/parent.fakeos", "w") as f:
						f.write(f"{caller_id} {caller['name']}")

					LoadToFile(proc_name, f"proc/{i}/module.fakeos")

					procs[i] = {
						"name" : proc_name,
						"module" : subprocess.Popen(["python", f"proc/{i}/module.fakeos"]+args)
					}

					with open(f"{directory}/response.fakeos", "w") as f:
						response = {
							"code" : 2,
							"value" : i
						}
						json.dump(response, f)

			elif req == "KillProcess":
				if data in procs:
					procs[data]["module"].kill()
					del procs[data]
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

			try:
				open(f"{directory}/request.fakeos", "w").close() #clear request
			except FileNotFoundError:
				pass #process has already been killed
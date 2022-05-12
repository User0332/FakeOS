from System.Locals import *

class File:
	def __init__(self, name):
		import json
		self.name = name
		if name in (0, 1, 2):
			self._file = name
		else:
			self._file = NULL
			with open("filesystem/files.json", "r") as f:
				files = json.load(f)
		
			if name not in files.keys():
				new = list(files.values())[-1]+1
				files[name] = new
				
				with open("filesystem/files.json", "w") as f:
					json.dump(files, f, indent=4)

				with open("filesystem/contents.json", "r") as f:
					contents = json.load(f)

				contents[str(new)] = ""

				with open("filesystem/contents.json", "w") as f:
					json.dump(contents, f, indent=4)
	
				self.idx = str(new)
			else:
				self.idx = str(files[name])

	def ReadAll(self):
		import json

		if self._file == 0:
			with open("filesystem/stdin.fakeos", "r") as f:
				return f.read()
		elif self._file in (1, 2):
			Console.ErrWriteLine("Cannot read from stdout or stderr!")
			return NULL
		with open("filesystem/contents.json", "r") as f:
			return json.load(f)[self.idx]

	def Read(self):
		import json

		if self._file == 0:
			with open("filesystem/stdin.fakeos", "r") as f:
				contents = list(f.read())
		elif self._file in (1, 2):
			Console.ErrWriteLine("Cannot read from stdout or stderr!")
			return NULL
		with open("filesystem/contents.json", "r") as f:
			contents = list(json.load(f)[self.idx])

		for content in contents:
			yield content

	def Write(self, string):
		import json

		if self._file == 0:
			Console.ErrWriteLine("Cannot write to stdin!")
		elif self._file == 1:
			with open("filesystem/stdout.fakeos", "a") as f:
				f.write(string)
		elif self._file == 2:
			with open("filesystem/stderr.fakeos", "a") as f:
				f.write(string)
		else:
			with open("filesystem/contents.json", "r") as f:
				contents = json.load(f)
				contents[self.idx]+=string

			
			with open("filesystem/contents.json", "w") as f:
				json.dump(contents, f, indent=4)

	def Clear(self):
		import json

		if self._file in (0, 1, 2):
			Console.ErrWriteLine("Cannot use clear on stdout, stderr, or stdin!")
			return NULL

		with open("filesystem/contents.json", "r") as f:
			contents = json.load(f)

		contents[self.idx] = ""

		with open("filesystem/contents.json", "w") as f:
			json.dump(contents, f)


STDIN = File(0)
STDOUT = File(1)
STDERR = File(2)

class Console:
	def Write(*strings):
		for string in strings:
			STDOUT.Write(string)
	
	def WriteLine(*strings):
		for string in strings:
			STDOUT.Write(string)

		STDOUT.Write("\n")

	def ErrWrite(*strings):
		for string in strings:
			STDERR.Write(string)

	def ErrWriteLine(*strings):
		for string in strings:
			STDERR.Write(string)

		STDERR.Write("\n")

	def ReadLine(prompt):
		Console.Write(prompt)
		inp = ""
		for char in STDIN.Read():
			if char == "\n":
				break
			else:
				inp+=char

		return inp

	def Getch():
		return STDIN.Read()[0]

	def ShowOutputFrom(*streams):
		for stream in streams:
			if not isinstance(stream, File):
				Console.ErrWriteLine("Streams passed to ShowOutputFrom() must be an object of System.File")
				return

			with open("other/output_streams.fakeos", "a") as f:
				f.write(stream.name+"\n")

	def HideOutputFrom(*streams):
		with open("other/output_streams.fakeos", "r") as f:
				out_streams = f.read().splitlines()
		for stream in streams:
			if not isinstance(stream, File):
				Console.ErrWriteLine("Streams passed to HideOutputFrom() must be an object of System.File")
				return

			try:
				out_streams.remove(stream)
			except ValueError:
				pass

		with open("other/output_streams.fakeos", "w") as f:
				f.write("\n".join(out_streams))

def WinCommand(command):
	from os import system
	system(command)

def ImportDLL(dllname):
	from ctypes import windll
	try:
		return windll.LoadLibrary(dllname)
	except OSError:
		from System import Console, NULL
		Console.ErrWriteLine(f"DLL {dllname} not found.")

		return NULL
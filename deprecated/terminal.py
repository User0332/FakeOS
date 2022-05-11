import os
import readline
import subprocess
import msvcrt
from sys import exit, argv

def main(argc: int, argv: list[str]):
	if msvcrt.kbhit():
		cmd = input()
	
		if cmd.startswith("cd"):
			try:
				os.chdir(cmd.removeprefix("cd"))
			except OSError as e:
				print("Invalid path!")
		elif cmd == "":
			pass
		elif cmd == "exit":
			raise Exception
		elif cmd.startswith("./"):
			cmd = cmd.removeprefix("./")
			try:
				current = os.getcwd()
				os.chdir("E:\\Users\\carlf\\FakeVM\\onstart\\")
				subprocess.call(cmd)
				os.chdir(current)
				with open("E:\\Users\\carlf\\FakeVM\\other\\onstart.fakeos", "r") as f:
					started = bool(f.read())
				os.remove("E:\\Users\\carlf\\FakeVM\\other\\onstart.fakeos")
				return started
			except OSError:
				os.chdir(current)
				print(f"{cmd.split()[0]} is not recognized as an executable file or command.")
		else:
			print(cmd)
		
		print("startup$ ", end = "")		
		return 0



if __name__ == "__main__":
	exit(main(len(argv), argv))


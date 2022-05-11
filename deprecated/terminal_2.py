import os
import readline
import subprocess
import msvcrt
from sys import exit, argv

print("shell$ ", end="")

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
				os.chdir("E:\\Users\\carlf\\FakeVM\\applications\\")
				subprocess.call(cmd+".bat")
				os.chdir(current)
			except OSError:
				os.chdir(current)
				print(f"{cmd.split()[0]} is not recognized as an executable file or command.")
		else:
			print(cmd)
		
		print("shell$ ", end = "")		
		return 0



if __name__ == "__main__":
	exit(main(len(argv), argv))


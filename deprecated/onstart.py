import os
import ctypes

ctypes.windll.user32.BringWindowToTop(ctypes.windll.kernel32.GetConsoleWindow())

txtpass = 'fj0BNf0a7wq9hfhw09e08HFJoihaij348UF0o9jq083huifj0ih'

with open(f"E:\\Users\\carlf\\myprograms\\password\\properties.txt:{txtpass}", "a"): pass  

with open(f"E:\\Users\\carlf\\myprograms\\password\\properties.txt:{txtpass}", "r") as f:
	password = f.read()

if password == "":
	password = input("Please set a password: ")
	with open(f"E:\\Users\\carlf\\myprograms\\password\\properties.txt:{txtpass}", "w") as f:
		f.write(password)
		
pwd = input("Enter Password: ")
with open("E:\\Users\\carlf\\FakeVM\\other\\onstart.fakeos", "w") as f:
	if pwd == password:
			f.write("True")
			ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
	else:
		os.system("python E:\\Users\\carlf\\FakeVM\\other\\onstart.py")
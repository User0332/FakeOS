from System.Locals import *
from System.Process import Kill
from os import chdir

chdir("E:\\Users\\carlf\\FakeVM\\")
del chdir

def Exit(code: int):
	Kill(PROC_ID)
	exit(code)
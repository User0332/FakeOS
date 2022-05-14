from System.Locals import *
from System.Process import Kill

def Exit(code: int) -> None:
	Kill(PROC_ID)
	exit(code)
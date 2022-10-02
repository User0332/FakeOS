from sys import modules, argv
from os import getcwd
from os.path import join
from typing import Any, TypedDict, Union

ARGV = argv #for constant recognition

NULL = "System.NULL"

#proc id should be parent directory name
try: PROC_ID = join(getcwd(), ARGV[0]).replace('\\', '/').split('/')[-2]
except IndexError: PROC_ID = 0 #if this fails, then the process is sys

if hasattr(modules["__main__"], "_SYSTEM_INIT_OVERRIDE_PROC_ID"):
	#just to be safe in case sys is run from another directory
	PROC_ID = modules["__main__"]._SYSTEM_INIT_OVERRIDE_PROC_ID

PROC_ID = int(PROC_ID)

PROC_DIR = f"proc/{PROC_ID}"

REQUEST_FILE = f"{PROC_DIR}/request.fakeos"

RESPONSE_FILE = f"{PROC_DIR}/response.fakeos"

SYSTEM_RESPONSE_CODES = {
	0 : "Not repsonded",
	1 : "Information recieved",
	2 : "Requested resource provided",
	3 : "Resource in use",
	4 : "Permission Denied",
	5 : "Resource not found",
	6 : "Exceptional Error"
}

class SYS_RESP(TypedDict):	
	code: int
	value: Union[int, str]

class SYS_REQ(TypedDict):
	type: str
	data: Any
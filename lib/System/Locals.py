from sys import argv as ARGV
from os import stat

ARGV = ARGV #for constant recognition

NULL = "System.NULL"

try: PROC_ID = ARGV[0].split('/')[-2]
except IndexError: PROC_ID = 0 #if this fails, then the process is sys

REQUEST_FILE = f"proc/{PROC_ID}/request.fakeos"

RESPONSE_FILE = f"proc/{PROC_ID}/response.fakeos"

SYSTEM_RESPONSE_CODES = {
	0 : "Not repsonded",
	1 : "Information recieved",
	2 : "Requested resource provided",
	3 : "Resource in use",
	4 : "Permission Denied",
	5 : "Resource not found",
	6 : "Exceptional Error"
}
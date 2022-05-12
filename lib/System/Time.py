def Sleep(ms):
	import time
	time.sleep(ms/1000)

def GetCurrentTime():
	import time
	return time.time()

def GetUTC():
	import time
	return time.gmtime()

def GetDatetime():
	import datetime
	return datetime.datetime.now()
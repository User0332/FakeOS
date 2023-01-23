# Need to have a DefaultConsole so programs launched from `terminal` don't create a new console
	# Have procs use stdin/out/err files
	

# >>

# Problem: All processes now need stdin/out/err files to launch
	# If no other file was provided, default these to /proc/{id}/fd/std[out|in|err]
		# Proc must be mounted to the FakeOS fs on launch for this to work, and must continue to mirror itself on both Windows/FakeOS while the OS is running

# >>

# Have Console class write to stdin on input (as option to use stdin/stdout in console creation)
	# Either expose sys file functions to the handle/update functions
	# Or make the entire system async
		# Allows any functions to be called from System API without causing the program to halt, waiting for a sys resp
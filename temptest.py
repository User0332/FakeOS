## FOR TERMINAL
import System
import System.IO
from System.Process import InitProcess


Console = System.IO.Console(800, 400) # use args in the future

# the 'defaultconsole (x=0, y=0) (invisible)' used by the program will write to the stdin, stdout, stderr



procid = InitProcess("the", "process")["value"]

# here, read the stdin, stdout, and stderr
stdin, stdout, stderr: str = read_table(procid)

while process_is_still_alive: 
	Console.Write(stdout)
import System
import System.IO
from System.IO import Console
from System.Process import GetRunningProcesses
from System.User import StopKeyEcho, StartKeyEcho
from System.CurrentApp import GetFlags, AddFlag, InitApp, RemoveFlag
from System.App import GetApplicationFlags
from System.Time import Sleep
from System.Machine.FakeOS import SysCommand
from System.Machine.Windows import WinCommand, ImportDLL
from System.RuntimeLoadedLibraries import ImportLibrary


InitApp()

WinCommand("echo Hello World!")
user32 = ImportDLL("User32.dll")
virtual_module = ImportLibrary("virtual_module.py")



virtual_module.init()
virtual_module.otherfunc()

print(f"NULL: {System.NULL}, STDIN: {System.IO.STDIN}, STDOUT: {System.IO.STDOUT}, STDERR: {System.IO.STDERR}")
Console.WriteLine("Hi")
SysCommand("echo I am in the FakeOS terminal!")
AddFlag("--testflag--")
StopKeyEcho()
print("Flags: ", GetFlags())
Sleep(1000)
StartKeyEcho()
print("Processes: ", GetRunningProcesses())
Sleep(1000)
RemoveFlag("--testflag--")
print("Flags: ", GetApplicationFlags("current"))
Sleep(1000)
System.Exit(0)


# FakeOS

A simulation of an operating system/VM made in Python 3.9

<br/>
<br/>

## General Info About Files

**.fakeos files** - These files are used and maintained by the system, they should not be modified unless you are aware of their effects

(**filesystem/files.py** - This file contains the filesystem in a JSON-like format, here files can be created and manipulated outside of the system

**assets/** - General items to be used with pygame

**src/** - Source of the fake kernel

**lib/System/** - This is the folder that holds the System API, adding {fakeos-directory}/lib/ to PYTHONPATH will allow the OS to run and will allow your to import and use the System API

**proc/** - Windows filesystem holding process information, each folder number represents a process id

<br/>
<br/>

## Running FakeOS

To run FakeOS, you must run the fakeos.py file from the root directory of the project (ex. `python src/fakeos.py`). You must then type in `boot` and hit enter. Following that, you must enter the root password (defaulted to nothing, so just hit enter), and then it will bring you to a shell where you can execute any program specified in the system PATH (`/cfg/system.path`).

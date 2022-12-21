{
	'/': {
		'dirs': {
			'bin': {
				'dirs': {
					'sys': {
						'dirs': {},
						'files': {

						}
					}
				}, 
				'files': {
					"testimport": b"import time\nimport System.Display\nfrom System.RuntimeLoadedLibraries import ImportAttribute\n\nwindow = System.Display.Window(200, 200, \"mywindow\")\nwindow.AddText(ImportAttribute(\"/users/root/virtual_module.py\", \"some_text\"), 50, 50, 20)\n\ntime.sleep(5)\n\nSystem.Exit(0)",
					"helloworld": b"import time\nimport System.IO\n\nConsole = System.IO.Console(400, 200)\n\nConsole.WriteLine(\"Hello World!\")\ntime.sleep(2)\nConsole.WriteLine(\"Line 2!\")\ntime.sleep(1)\nConsole.WriteLine(\"This is a really long line of text that needs to be wrapped to the next line!\")\n\ntime.sleep(10)\nSystem.Exit(0)",
					"echoinput": b"import time\nimport System.IO\n\nConsole = System.IO.Console(400, 200)\n\nConsole.Write(\"Type Some Input: \")\ninput = Console.ReadLine()\ntime.sleep(1)\nConsole.WriteLine(f\"You typed: {input!r}\")\n\ntime.sleep(10)\nSystem.Exit(0)"
				}
			},
			'cfg': {
				'dirs': {
					'users': {
						'dirs': {}, 
						'files': {
							'list': b'root', 
							'permissions': b"{'ADMIN' : {'/' : 'rwx'}}", 
							'groups': b"{'ADMIN' : ['root']}", 
							'passwds': b"{'root' : 'd404559f602eab6fd602ac7680dacbfaadd13630335e951f097af3900e9de176b6db28512f2e000b9d04fba5133e8b1c6e8df59db3a8ab9d60be4b97cc9e81db' }"
						}
					}, 
					'security': {
						'dirs': {},
						'files': {
							'passwd': b"{'max_days' : 30, 'min_days' : 0, 'min_length' : 6, 'store_method' : 'sha512'}"
						}
					}
				}, 
				'files': {
					'system.path': b'/bin\nbin\n/\n/bin/sys', 
					'path.ext': b'.py\n.pyc\n.sh', # have this actually do stuff later
					'startup.scripts': b'[]', 	   # ^
					'shutdown.scripts': b'[]'	   # ^
				}
			}, 
			'users': {
				'dirs': {
					'root': {
						'dirs': {}, 
						'files': {
							'virtual_module.py': b"some_text = 'text from virutal_module.py!'"
						}
					}
				}, 
				'files': {}
			}
		}, 
		'files': {}
	}
}
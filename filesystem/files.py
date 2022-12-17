{
	'/': {
		'dirs': {
			'bin': {
				'dirs': {}, 
				'files': {
					'myproc': b"import System\nprint('hello world!')\nSystem.Exit(0)", 
					'testwindow': b"import time\nimport System.Display\n\nwindow = System.Display.Window(200, 200, \"mywindow\")\nwindow.AddText(\"My Window!\", 50, 50, 20)\n\ntime.sleep(5)\n\nSystem.Exit(0)",
					"testimport": b"import time\nimport System.Display\nfrom System.RuntimeLoadedLibraries import ImportAttribute\n\nwindow = System.Display.Window(200, 200, \"mywindow\")\nwindow.AddText(ImportAttribute(\"/users/root/virtual_module.py\", \"some_text\"), 50, 50, 20)\n\ntime.sleep(5)\n\nSystem.Exit(0)"
				}
			},
			'cfg': {
				'dirss': {
					'users': {
						'dirs': {}, 
						'files': {
							'list': b'root', 
							'permissions': b"{'ADMIN' : {'/' : 'rwx'}}", 
							'groups': b"{'ADMIN' : ['root']}", 
							'passwds': b"{'root' : 5004213034220426749 }"
						}
					}, 
					'security': {
						'dirs': {},
						'files': {
							'passwd': b"{'max_days' : 30, 'min_days' : 0, 'min_length' : 6, 'store_method' : 'pyhash-common'}"
						}
					}
				}, 
				'files': {
					'system.path': b'/bin\nbin', 
					'path.ext': b'.py\n.pyc\n.sh', 
					'startup.scripts': b'[]', 
					'shutdown.scripts': b'[]'
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
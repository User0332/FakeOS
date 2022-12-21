# set flag for System.Locals to recognize
# module as sys
_SYSTEM_INIT_OVERRIDE_PROC_ID = 0

import unittest.mock
import contextlib
with contextlib.redirect_stdout(unittest.mock.Mock()):
	import pygame
import req # for procs variable
import os
import time as t
import traceback as trace
from ctypes import windll
from System.PyDict import loads
from fakeos_utils import (
	valid_chars,
	read_file,
	write_file,
	exec_update,
	exec_event_handler,
	hash_algorithms,
	log
)
from req import (
	fulfill_reqests,
	InitProcess
)

user32 = windll.user32

del (
	unittest,
	contextlib
)

def display_terminal_text(text, pos, screen: pygame.Surface, font: pygame.font.Font, color = "white", update: bool=True):
		screen.blit(font.render(text, True, color), pos)
		pygame.display.update() if update else None


pygame.init()

# Get dimensions/resolution of the screen.
MAX_X, MAX_Y = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

SYSTEM_CONF = {}

def sysconf_load(): # load all config data of the system
	try:
		PASSWDS: dict[str, str] = loads(read_file("/cfg/users/passwds"))
		if "root" not in PASSWDS: raise SyntaxError()
	except SyntaxError:
		log(
			"Fatal Error: configuration file "
			"'/cfg/users/passwds' is not in the right format! "
			"Defaulting to { 'root' : '' }"
		)

		PASSWDS = { "root": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e" }
		input("Enter to continue... ")

	try:
		PASSWD_CONFIG: dict[str, str] = loads(
			read_file("/cfg/security/passwd")
		)

		all_keys_valid = (
			(type(PASSWD_CONFIG.get("max_days")) is int) and
			(type(PASSWD_CONFIG.get("min_days")) is int) and
			(type(PASSWD_CONFIG.get("min_length")) is int) and
			(
				PASSWD_CONFIG.get("store_method") in
				("sha512",) # add more possibilites later??? maybe
				# to change hash algorithm, verify the user's passwd and then take
				# the raw input to hash with the new algorithm
				# ALSO CHG the above `in` check to `method in hash_algorithms.keys()`
			)
		)

		if not all_keys_valid: raise SyntaxError()
	except SyntaxError:
		log(
			"Fatal Error: configuration file "
			"'/cfg/security/passwd' is not in the right format! "
			" Defaulting to {'max_days' : 30, 'min_days' : 0, 'min_length' : 6, 'store_method' : 'fakehash-common'}"
		)

		PASSWD_CONFIG = {
			"max_days": 30, 
			"min_days": 0, 
			"min_length": 6, 
			"store_method" : "sha512"
		}

	SYSTEM_CONF["PASSWDS"] = PASSWDS
	SYSTEM_CONF["PASSWD_CONF"] = PASSWD_CONFIG

middle = (MAX_X/2, MAX_Y/2)

screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("User0332's FakeOS")

console = pygame.font.SysFont("Lucida Console", 35)

fakeos_icon = pygame.image.load("assets/background.png")
pygame.display.set_icon(fakeos_icon)


user_input_text = "> "
running = True
uptimes = 0

os.system("cls" if os.name == "nt" else "clear")

while running:
	screen.fill("black")
	display_terminal_text(user_input_text, (0, 0), screen, console)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type == pygame.KEYDOWN:
			char = event.unicode
			if char in valid_chars:
				user_input_text+=char
			elif event.key == pygame.K_BACKSPACE:
				if len(user_input_text) > 2: user_input_text = user_input_text[:-1]
			elif event.key == pygame.K_RETURN:
				if user_input_text == "> boot":
					screen.fill("black")

					user_input_text = "Searching for required windows directories..."

					display_terminal_text(user_input_text, (0, 0), screen, console)
					t.sleep(0.1)

					windirokay = (
						os.path.exists("lib") and os.path.isdir("lib") and
						os.path.exists("assets") and os.path.isdir("assets") and
						os.path.exists("filesystem") and os.path.isdir("filesystem") and
						os.path.exists("proc") and os.path.isdir("proc")
						)

					if windirokay:
						user_input_text = "[ OK ] Critical Windows directories intact"
						display_terminal_text(user_input_text, (0, 40), screen, console)
						t.sleep(1)
					else:
						user_input_text = "[ FAIL ] Critical Windows directories missing"
						display_terminal_text(user_input_text, (0, 40), screen, console)
						t.sleep(1)
						user_input_text = "> "				
						continue

					user_input_text = "Initializing System API..."

					display_terminal_text(user_input_text, (0, 80), screen, console)
					t.sleep(0.1)

					try:
						import System
						user_input_text = "[ OK ] System API Loaded"
					except Exception as e:
						user_input_text = f"[ FAIL ] System API failed to Load - {e}"
						log(f"{type(e).__name__}: {e}, trace: {trace.format_exc()}")
						continue
					finally:
						display_terminal_text(user_input_text, (0, 120), screen, console)
						t.sleep(1)
						user_input_text = "> "

					user_input_text = "Loading System Configurations"

					display_terminal_text(user_input_text, (0, 160), screen, console)
					t.sleep(0.1)

					try:
						sysconf_load()
						user_input_text = "[ OK ] System Config Loaded"
					except Exception as e:
						user_input_text = f"[ FAIL ] System Config Failed to Load - {e}"
						log(f"{type(e).__name__}: {e}, trace: {trace.format_exc()}")
						continue
					finally:
						display_terminal_text(user_input_text, (0, 200), screen, console)
						t.sleep(1)
						user_input_text = "> "

					running = False

				user_input_text = "> "


# SYS PROC

prompt = "passwd (root) => "
input_passwd = ""
get_passwd = True

user_input_text = "[ OK ] Sys Proc Launched"

display_terminal_text(user_input_text, (0, 240), screen, console)

t.sleep(0.5)

while get_passwd:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type == pygame.KEYDOWN:
			char = event.unicode
			if char in valid_chars:
				input_passwd+=char
			elif event.key == pygame.K_BACKSPACE:
				input_passwd = input_passwd[:-1]
			elif event.key == pygame.K_RETURN:
				# implement check for hashing type later when new
				# hash types are acutally introduced
				if (
					hash_algorithms[
						SYSTEM_CONF["PASSWD_CONF"]["store_method"]
					]
					(input_passwd) == SYSTEM_CONF["PASSWDS"]["root"]
				):
					input_passwd = ""
					get_passwd = False
				else:
					input_passwd = ""
					prompt = "ROOT PASSWD> "


	screen.fill("black")		
	display_terminal_text(prompt+("*"*len(input_passwd)), (0, 0), screen, console)

	pygame.display.update()

log("NORMAL-ON-LAUNCH: running base semi-kernel program launch => run sysui or terminal to use a dist of FakeOS")

prompt = "root@fakeos$ "
cmd_locals = {}
cmd_globals = {}
input_cmd = ""
result = ""
moving_win = None
selected_win = None

while True:
	events = pygame.event.get()

	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type == pygame.MOUSEBUTTONDOWN:
			mousepos = pygame.mouse.get_pos()

			found = False
			for proc in req.procs.values():
				for win in proc["windows"]:
					if win["rect"].collidepoint(mousepos):
						moving_win = win
						selected_win = win

						found = True

			if not found: selected_win = None # if no window was hit, no window was selected
		
		if event.type == pygame.MOUSEBUTTONUP:
			moving_win = None # window released from mouse
		if event.type == pygame.KEYDOWN:
			# have selected window handle its own input
			if selected_win: continue

			char = event.unicode
			if char in valid_chars:
				input_cmd+=char
			elif event.key == pygame.K_BACKSPACE:
				input_cmd = input_cmd[:-1]
			elif event.key == pygame.K_RETURN:
				# if no command was entered, do nothing
				if not input_cmd: continue
				
				args = input_cmd.split()
				name = args[0]
				args = [] if len(args) < 2 else args[1:]

				if name == "exit": 
					pygame.quit()
					exit(0)

				res = InitProcess(
					name,
					args,
					max(req.procs)+1,
					0,
					req.procs[0]
				)
				
				if res["code"] != 2: # process could not be initialized
					log(f"kernel shell err: {res['value']} (failed on '{name}')")

				result = ""
				input_cmd = ""

	fulfill_reqests() 

	screen.fill("black")

	display_terminal_text(prompt+input_cmd, (0, 0), screen, console, update=False)
	display_terminal_text(result, (0, 40), screen, console, update=False)

	if moving_win:
		moving_win["rect"] = \
			moving_win["surface"].get_rect(
				center=pygame.mouse.get_pos()
			)

	if selected_win:
		exec_event_handler(
			selected_win,
			events
		)

	for proc in req.procs.values():
		for window in proc["windows"]:
			exec_update(window)

			screen.blit(
				window["surface"],
				window["rect"]
			)



	pygame.display.update()
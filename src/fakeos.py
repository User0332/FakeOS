import pygame
import os
# set flag for System.Locals
_SYSTEM_INIT_OVERRIDE_PROC_ID = 0
import time as t
from fakeos_utils import TextButton, valid_chars
from req import fulfill_reqests
from System.Process import InitProcess
from System.IO import File, M_RDONLY

def display_terminal_text(text, pos, screen: pygame.Surface, font: pygame.font.Font, color = "white"):
		screen.blit(font.render(text, True, color), pos)
		pygame.display.update()


pygame.init()

MAX_X = 1680
MAX_Y = 1050

with File("/cfg/users/passwds", M_RDONLY) as f:
	ROOT_PASSWD: str = f.LoadJSON()["root"] #currently ignores password storage style

print(ROOT_PASSWD)

middle = (MAX_X/2, MAX_Y/2)

screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("User0332's FakeOS")

arial = pygame.font.SysFont("Arial", 35)

fakeos_icon = pygame.image.load("assets/background.png")
pygame.display.set_icon(fakeos_icon)


user_input_text = "> "
running = True
uptimes = 0

os.system("cls" if os.name == "nt" else "clear")

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type == pygame.KEYDOWN:
			char = event.unicode
			if char in valid_chars:
				user_input_text+=char
			elif event.key == pygame.K_BACKSPACE:
				user_input_text = user_input_text[:-1]
			elif event.key == pygame.K_RETURN:
				if user_input_text == "> boot":
					screen.fill("black")

					user_input_text = "Searching for required windows directories..."

					display_terminal_text(user_input_text, (0, 0), screen, arial)
					t.sleep(0.1)

					windirokay = (
						os.path.exists("applications") and os.path.isdir("applications") and
						os.path.exists("assets") and os.path.isdir("assets") and
						os.path.exists("filesystem") and os.path.isdir("filesystem") and
						os.path.exists("proc") and os.path.isdir("proc")
						)

					if windirokay:
						user_input_text = "[ OK ] Critical Windows directories intact"
					else:
						user_input_text = "[ FAIL ] Critical Windows directories missing"
						continue

					display_terminal_text(user_input_text, (0, 40), screen, arial)
					t.sleep(0.1)

					user_input_text = "Initializing System API..."

					display_terminal_text(user_input_text, (0, 80), screen, arial)
					t.sleep(0.1)

					try:
						import System
						user_input_text = "[ OK ] System API Loaded"
					except Exception as e:
						user_input_text = f"[ FAIL ] System API failed to Load - {e}"
						continue
					
					display_terminal_text(user_input_text, (0, 120), screen, arial)
					t.sleep(0.1)

					running = False

				user_input_text = "> "
				
	screen.fill("black")
	display_terminal_text(user_input_text, (0, 0), screen, arial)


# SYS PROC

prompt = "ROOT PASSWD> "
input_passwd = ""
get_passwd = True

user_input_text = "[ OK ] Sys Proc Launched"

display_terminal_text(user_input_text, (0, 160), screen, arial)

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
				if input_passwd == ROOT_PASSWD:
					input_passwd = ""
					get_passwd = False

				else:
					input_passwd = ""
					prompt = "ROOT PASSWD> "


	screen.fill("black")		
	display_terminal_text(prompt+("*"*len(input_passwd)), (0, 0), screen, arial)

	pygame.display.update()

prompt = "root@fakeos:~$ "
cmd_locals = {}
cmd_globals = {}
input_cmd = ""
result = ""

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type == pygame.KEYDOWN:
			char = event.unicode
			if char in valid_chars:
				input_cmd+=char
			elif event.key == pygame.K_BACKSPACE:
				input_cmd = input_cmd[:-1]
			elif event.key == pygame.K_RETURN:
				try:
					InitProcess(*input_cmd.split()) #sys can fulfill its own requests but for the sake of uniformity and simplicity it will send a request to itself
					result = ""
				except BaseException as e:
					result = str(e)

				input_cmd = ""

	fulfill_reqests() 

	screen.fill("black")

	display_terminal_text(prompt+input_cmd, (0, 0), screen, arial)
	display_terminal_text(result, (0, 40), screen, arial)

	pygame.display.update()
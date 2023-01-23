import pygame
import dill
import hashlib
import datetime as date
import System.Locals
from System.IO import M_RDONLY, M_WRONLY
from System.Machine.FakeOS import Stat
from types import FunctionType
from req import (
	Sys_Close,
	Sys_OpenFile, 
	Sys_ReadFile,
	Sys_WriteFile,
	DeAllocateWindow,
	Window_AttachUpdateFunction,
	Window_AttachEventHandler,
	WindowType
)

hash_algorithms = {
	"sha512": lambda s: hashlib.sha512(s.encode()).hexdigest(),
	"sha256": lambda s: hashlib.sha256(s.encode()).hexdigest(),
	"sha224": lambda s: hashlib.sha224(s.encode()).hexdigest()
}

def log(data: str):
	fmtd = f"{date.datetime.now()} - {data}\n"

	print(fmtd)

	with open("./sys.log", 'a') as f:
		f.write(fmtd)

def exec_update(win: WindowType, proc_id: int):
	func = win["update"]
	id = win["id"]

	if not isinstance(func, FunctionType): return

	System.Locals.reload(proc_id=proc_id)

	try: exec(
		"""func(
			pygame,
			_get_win_funcs(id),
			win['vars'],
			win['surface'],
			win['rect']
		)""", {
			"func": func,
			"pygame": pygame,
			"_get_win_funcs": _get_win_funcs,
			"win": win
		}
	)
	except BaseException as e: log(e)
	finally: System.Locals.reload()

def exec_event_handler(proc_id: int, win: WindowType, events: list[pygame.event.Event]):
	func = win["event_handler"]
	id = win["id"]

	if not isinstance(func, FunctionType): return

	System.Locals.reload(proc_id=proc_id)

	try: exec(
		"""func(
			pygame,
			events,
			_get_win_funcs(id),
			win['vars'],
			win['surface'],
			win['rect']
		)""", {
			"func": func,
			"pygame": pygame,
			"events": events,
			"_get_win_funcs": _get_win_funcs,
			"win": win
		}
	)
	except BaseException as e: log(e)
	finally: System.Locals.reload()

def _get_win_funcs(id):
	return {
		"close": lambda: DeAllocateWindow(0, id),
		"chgupdate": lambda func: Window_AttachUpdateFunction(0, id, dill.dumps(func)),
		"chghandler": lambda func: Window_AttachEventHandler(0, id, dill.dumps(func))
	}


def read_file(fname: str) -> str:
	file = Sys_OpenFile(fname, M_RDONLY, 0)["value"]
	numb = Stat(fname).size
	
	data: str = Sys_ReadFile(file, numb, 0)["value"]

	Sys_Close(file, 0)

	return data

def write_file(fname: str, data: str) -> System.Locals.SYS_RESP:
	file = Sys_OpenFile(fname, M_WRONLY, 0)["value"]
	
	resp = Sys_WriteFile(file, data, 0)

	Sys_Close(file, 0)

	return data

class Button:
	def __init__(self, pos: tuple, surface: pygame.Surface, screen: pygame.Surface):
		self.screen = screen
		self.surface  = surface
		self.rect: pygame.rect.Rect = self.surface.get_rect(topleft=pos)


	def render(self):
		self.screen.blit(self.surface, self.rect)

	def is_pressed(self, event: pygame.event.Event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				return True

		return False


class TextButton(Button):
	def __init__(self, pos, text, screen, font, textcolor = "black"):
		super().__init__(pos, font.render(text, True, textcolor), screen, )

valid_chars = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-_+={}[]:;\"'\\|/?.><,~` "+"abcdefghijklmnopqrstuvwxyz".upper()
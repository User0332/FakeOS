from System.IO import M_RDONLY, M_WRONLY
from System.Locals import SYS_RESP
from System.Machine.FakeOS import Stat
import pygame
from req import (
	Sys_Close,
	Sys_OpenFile, 
	Sys_ReadFile,
	Sys_WriteFile
)


def read_file(fname: str) -> str:
	file = Sys_OpenFile(fname, M_RDONLY, 0)["value"]
	numb = Stat(fname).size
	
	data: str = Sys_ReadFile(file, numb, 0)["value"]

	Sys_Close(file, 0)

	return data

def write_file(fname: str, data: str) -> SYS_RESP:
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
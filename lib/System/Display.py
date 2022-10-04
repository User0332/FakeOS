from typing import Union
import dill
import contextlib
import unittest.mock
with contextlib.redirect_stdout(unittest.mock.Mock()):
	import pygame
from types import FunctionType
from .Machine.FakeOS import WriteRequest, SystemError

del (
	contextlib,
	unittest
)

ColorType = Union[tuple[int, int, int], str]

pygame.init() # for font and other libraries

class Button:
	def __init__(self, surface: pygame.Surface, x: int, y: int, onclick: FunctionType):
		self.surface = surface
		self.rect = surface.get_rect(center=(x, y))
		self.onclick = onclick

class Window:
	def __init__(self, x: int, y: int, id: str):
		self._x = x
		self._y = y
		self._id = id

		resp = WriteRequest(
			{
				"type": "Window.Allocate",
				"data": {
					'x': x,
					'y': y,
					"id": id
				}
			}
		)

		if resp["code"] != 2: raise SystemError(resp["value"])

	def Delete(self):
		WriteRequest(
			{
				"type": "Window.DeAllocate",
				"data": {
					"id": self.id
				}
			}
		)

	def WindowEval(self, expr: str):
		resp = WriteRequest(
			{
				"type": "Window.EvalExpr",
				"data": {
					"id": self.id,
					"expr": expr
				}
			}
		)

		if resp["code"] != 1: raise SystemError(resp["value"])

		return dill.loads(
			resp["value"]
		)

	def AddText(
		self, 
		text: str, x: int, y: int, size: int, 
		color: ColorType="black", 
		font: str="Arial", antialias: bool=False,
		background: ColorType=None
		):
		
		return self.WindowEval(
			f"window.blit(pygame.font.SysFont('{font}', {size})"
			f".render('{text}', {antialias}, {repr(color)}, {repr(background)}), ({x}, {y}))"
		)


	def __del__(self):
		self.Delete()

	@property
	def x(self): return self._x

	@property
	def y(self): return self._y

	@property
	def id(self): return self._id
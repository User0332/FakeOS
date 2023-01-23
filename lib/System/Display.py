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
Coordinate = tuple[int, int]

_EVENT_HANDLERS = [
	"OnMouseClick",
	"OnKeyDown",
	"OnClose",
	# add more here later
]

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

	def StoreSystemSideVariable(self, name: str, expr: str, names: dict[str]=None) -> str:
		names = names if names else dict()

		resp = WriteRequest(
			{
				"type": "Window.StoreVariable",
				"data": {
					"name": name,
					"expr": expr,
					"id": self.id,
					"_globals": dill.dumps(names)
				}
			}
		)

		if resp["code"] != 1: raise SystemError(resp["value"])

		return resp["value"]


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

	def CreateSurface(self, name: str, *args: list[str]):
		"""Args must be a string of evaluatable expressions"""
		return self.StoreSystemSideVariable(
			name, ""f"pygame.Surface({', '.join(*args)})"
		)

	def BlitSurface(self, name: str):
		return self.WindowEval(f"window.blit({name})")

	def DefineUpdateFunction(self, update: FunctionType):
		"""
		Receives a function 'update' ->
		```py
		(
			pygame: Module[pygame], 
			window_functions: {
				"close": () -> SYS_RESP,
				"chgupdate": (update: UpdateFunctionType) -> SYS_RESP
			},
			win_vars: dict[str, Any], # can be modified
			surface: pygame.Surface # your window surface
			rect: pygame.Rect[surface]
		) -> None,
		```

		NOTE: This function will be serialized and rebuilt by sys on the other
		side, so global variable references cannot be used and will not work.
		"""

		resp = WriteRequest(
			{
				"type": "Window.AttachUpdateFunction",
				"data": {
					"func": dill.dumps(update),
					"id": self.id
				}
			}
		)

		if resp["code"] != 1: raise SystemError(resp["value"])

	def AttachEventHandlerFunction(self, handler: FunctionType):
		"""
		Triggered every frame with `pygame.event.get()` if the current window is selected.
		
		Receives a function 'handler' ->
		```py
		(
			pygame: Module[pygame],
			events: list[pygame.event.Event]
			window_functions: {
				"evalexpr": (expr: str) -> SYS_RESP
				"close": () -> SYS_RESP,
				"storevar": (name: str, expr: str) -> SYS_RESP,
				"chgupdate": (update: UpdateFunctionType) -> SYS_RESP
			},
			win_vars: dict[str, Any], # can be modified
			surface: pygame.Surface # your window surface
			rect: pygame.Rect[surface]
		) -> None,
		```

		NOTE: This function will be serialized and rebuilt by sys on the other
		side, so references to non-serializable objects (like `pygame.Surface()`)
		defined outside the function will not work.
		"""

		resp = WriteRequest(
			{
				"type": "Window.AttachEventHandler",
				"data": {
					"func": dill.dumps(handler),
					"id": self.id
				}
			}
		)

		if resp["code"] != 1: raise SystemError(resp["value"])

	def OutlineBorder(self, color="black", size: int=1):
			self.WindowEval(
				f"window.fill({repr(color)},"
				f"window.get_rect().inflate(-{size}, -{size}))"
			)

	def __del__(self):
		self.Delete()

	@property
	def x(self): return self._x

	@property
	def y(self): return self._y

	@property
	def id(self): return self._id
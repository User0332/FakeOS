import textwrap
import time
from System import Display
from .Standard import (
	stdin, stdout, stderr, 
	M_RDONLY, M_WRONLY
)

pygame = Display.pygame

class Console:
	def __init__(self, x: int, y: int, /, id: str="_console"):
		self._inner = Display.Window(x, y, id)
		self._text = ""
		self._inner.StoreSystemSideVariable("text", "''")
		self._inner.StoreSystemSideVariable("stdin_buff", "''")
		self._inner.StoreSystemSideVariable("scroll_y", '0')
		
		font_size = y//10
		scroll_mod = (font_size//2)

		self._inner.StoreSystemSideVariable("font", f"pygame.font.SysFont('Lucida Console', {font_size})")

		
		def handle_events(
			pygame: pygame,
			events: list[pygame.event.Event],
			win_funcs: dict[str, Display.FunctionType],
			win_vars: dict[str, Display.Union[str, pygame.font.Font, Display.FunctionType]],
			surface: pygame.Surface,
			rect: pygame.Rect
		):
			for event in events:
				if event.type == pygame.KEYDOWN:
					key: str = event.unicode

					win_vars["stdin_buff"]+=key
					stdin.Write(win_vars["stdin_buff"], M_WRONLY)
					print()
				elif event.type == pygame.MOUSEWHEEL:
					win_vars["scroll_y"]+=(event.y*scroll_mod)

					# make sure this never goes positive, e.g. disallow scrolling up past the top of the terminal
					win_vars["scroll_y"] = min(win_vars["scroll_y"], 0)

		def update(
			pygame: pygame,
			win_funcs: dict[str, Display.FunctionType],
			win_vars: dict[str, Display.Union[str, pygame.font.Font, int]],
			surface: pygame.Surface,
			rect: pygame.Rect
		):
			font: pygame.font.Font = win_vars["font"]
			scroll_y: int = win_vars["scroll_y"]

			surface.fill("black")

			str_lines = []

			for line in win_vars["text"].splitlines(): #wrap text if necessary
				if font.size(line)[0] > x:
					i = 0

					while font.size(line[:i])[0] < x and i < len(line): i+=1

					str_lines.extend(
						textwrap.wrap(line, i-1) # i-1 to stay on the safe side (no cutting into border)
					)

					continue

				str_lines.append(line)

			ACTUAL_SCREEN_TOP = (0-scroll_y)
			ACTUAL_SCREEN_BOTTOM = (y-scroll_y)
				
			visible_lines = []


			# basically get all the lines inside the screen borders
			for i, line in enumerate(str_lines):
				line_pos_y = i*font_size

				if ACTUAL_SCREEN_BOTTOM >= line_pos_y >= ACTUAL_SCREEN_TOP:
					visible_lines.append(line)


			wrapped_lines = (
				font.render(line, False, "white")
				for line in visible_lines
			)

			curr_y = 0

			for i, line in enumerate(wrapped_lines):
				surface.blit(
					line,
					(0, curr_y)
				)

				curr_y+=font_size

			# OUTLINE/BORDER THE TERMINAL
			end_x = x-2
			end_y = y-2

			pygame.draw.line(
				surface, "white",
				(0, 0), (end_x, 0)
			)

			pygame.draw.line(
				surface, "white",
				(0, 0), (0, end_y)
			)

			pygame.draw.line(
				surface, "white",
				(end_x, 0), (end_x, end_y)
			)

			pygame.draw.line(
				surface, "white",
				(0, end_y), (end_x, end_y),
			)

			# END OUTLINE/BORDER TERMINAL

		self._inner.DefineUpdateFunction(update)
		self._inner.AttachEventHandlerFunction(handle_events)

	def Flush(self):
		self._inner.StoreSystemSideVariable("text", repr(self._text))

	def Write(self, string: str):
		self._text+=string

		stdout.Write(self._text)

		if string[-1] in ('\r', '\n'): self.Flush() # autoflush

	def WriteLine(self, string: str):
		self._text+=string+'\r'

		stdout.Write(self._text)

		self.Flush()

	def GetChar(self) -> str:
		self.Flush() # make sure all output is printed before proceeding

		# wait until something is actually pushed to the input buff
		while not self._inner.WindowEval("stdin_buff"):	time.sleep(0.05) # don't request things too fast

		# read and remove char from input buffer
		char = self._inner.WindowEval("stdin_buff[0]")
		self._inner.StoreSystemSideVariable("stdin_buff", "stdin_buff[1:]")

		stdin.Write(self._inner.WindowEval("stdin_buff"), M_WRONLY)

		return char

	def ReadLine(self) -> str:
		res = '\0' # null char so the below `while` check doesn't throw IndexError

		while res[-1] != '\r':
			char = self.GetChar()
			
			# delete the character if backspace pressed
			# and the current input string isn't empty
			# don't do `and` here in case the \b gets written
			# to the screen and deletes printed text
			if char == '\b':
				if (res != '\0'):
					# DELETE CHAR FROM SCREEN
					self._text = self._text[:-1]

					res = res[:-1]
			else:
				self.Write(char)
				res+=char

		self.Flush() # final char put to screen

		return res[1:-1] # strip leading null char and trailing newline off of the input
			

	def ChangeFont(self, pg_font_expr: str):
		self._inner.StoreSystemSideVariable("font", pg_font_expr)
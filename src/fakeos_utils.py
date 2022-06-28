import pygame

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
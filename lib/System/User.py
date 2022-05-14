import pygame

# these functions do not work

def GetCurrentKey():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			return pygame.key.name(event.key)


def KeyIsPressed():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			return True

	return False

def KeyModifierIsPressed():
	for event in pygame.event.get():
		if hasattr(event, "mod"):
			return True

	return False

def GetKeyModifier():
	for event in pygame.event.get():
		if hasattr(event, "mod"):
			return pygame.key.name(event.mod)
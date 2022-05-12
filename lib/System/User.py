def GetCurrentKey():
	import pygame
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			return pygame.key.name(event.key)


def KeyIsPressed():
	import pygame
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			return True

	return False

def KeyModifierIsPressed():
	import pygame
	for event in pygame.event.get():
		if hasattr(event, "mod"):
			return True

	return False

def GetKeyModifier():
	import pygame
	for event in pygame.event.get():
		if hasattr(event, "mod"):
			return pygame.key.name(event.mod)

def StopKeyEcho():
	from System import CurrentApp
	CurrentApp.AddFlag("--noecho--")

def StartKeyEcho():
	from System import CurrentApp
	CurrentApp.RemoveFlag("--noecho--")
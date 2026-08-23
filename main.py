import pygame  # import the pygame library
from managers.game_manager import GameManager
import sys

pygame.init()  # initialize pygame modules

SCREEN_WIDTH = 800  # width of the game window
SCREEN_HEIGHT = 600  # height of the game window

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # create the display surface
pygame.display.set_caption("Space Invaders by: Cabardo, Sonjeev C.")  # set the window title

game_manager = GameManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

clock = pygame.time.Clock()
running = True  # main loop control flag

while running:  # game loop runs while running is True

    events = pygame.event.get()  # get all pending events
    for event in events:  # iterate through all pending events
        if event.type == pygame.QUIT:  # if the close window event is triggered
            running = False  # stop the game loop

    game_manager.update(events)

    pygame.display.update()  # update the full display surface to the screen
    clock.tick(60)  # limit frame rate to 60 FPS

pygame.quit()  # uninitialize all pygame modules
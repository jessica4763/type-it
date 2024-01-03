import pygame

import constants
from helper import get_sprite_frames
import displays


def main():
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.init()
    dungeon_ambience = pygame.mixer.Sound(constants.SOUNDS_PATH + 'dungeon_ambience.wav')
    dungeon_ambience.set_volume(0.25)
    dungeon_ambience.play(loops=-1, fade_ms=5000)

    # set screen
    view = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    pygame.display.init()

    # make an offscreen surface for drawing pygame to
    screen = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

    # preload all images
    get_sprite_frames()

    # creates the display that handles all game mechanics and drawing
    display = displays.Display(view, screen)

    # initialize the clock
    clock = pygame.time.Clock()

    # set the name of the window
    pygame.display.set_caption("Type It")

    # set the icon of the window
    icon = pygame.image.load(constants.ICON_PATH).convert_alpha()
    pygame.display.set_icon(icon)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha() or event.unicode == ' ':
                    display.press_key(event.unicode)
                elif event.key == pygame.K_BACKSPACE:
                    display.press_key('backspace')
                elif event.key == pygame.K_RETURN:
                    display.press_key('return')

        # store time since last call of clock.tick
        display.time = clock.tick(constants.FPS)

        # draws and updates the display
        display.update()
        display.draw()

        # blits the 'screen' surface to the screen the player actually sees
        view.blit(screen, next(display.offset))

        # update the screen
        pygame.display.flip()


if __name__ == '__main__':
    main()

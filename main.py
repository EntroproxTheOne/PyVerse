# main.py
import pygame
from pygame.locals import *
from menu import run_menu
from simulation import run_simulation
from splash import show_splash
from settings import Settings
from config import STATE_MENU, STATE_SETTINGS, STATE_SIM

def main():
    pygame.init()

    # Set window icon
    try:
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
    except pygame.error as e:
        print(f"⚠️ Icon not found: {e}")

    # Set initial window
    screen = pygame.display.set_mode((1000, 800), RESIZABLE)
    pygame.display.set_caption("PyVerse")
    clock = pygame.time.Clock()

    # Show splash screen
    show_splash(screen, clock)

    settings = Settings()
    state = STATE_MENU

    while True:
        if state == STATE_MENU:
            result = run_menu(screen, clock, settings)
        elif state == STATE_SIM:
            result = run_simulation(settings)
        else:
            result = "exit"

        if result == "exit":
            break
        else:
            state = result

    pygame.quit()

if __name__ == "__main__":
    main()
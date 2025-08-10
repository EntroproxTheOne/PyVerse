# menu.py
import pygame
from pygame.locals import *
from config import *

# Shared screen state
screen_state = {'width': SCREEN_WIDTH, 'height': SCREEN_HEIGHT}

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = HOVER_BLUE if self.hovered else BLUE
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=12)
        font = pygame.font.SysFont("Arial", 40)
        txt_surf = font.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.hovered


class FloatingPlanet:
    """Simple 2D animated planet for menu background"""
    def __init__(self, x, y, vx, vy, radius, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color

    def update(self, width, height):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > width: self.vx *= -1
        if self.y < 0 or self.y > height: self.vy *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


def run_menu(screen, clock, settings):
    # Initialize animated planets
    bg_planets = [
        FloatingPlanet(200, 100, 0.5, 0.3, 4, (0, 100, 255)),
        FloatingPlanet(700, 600, -0.4, 0.6, 3, (255, 200, 0)),
        FloatingPlanet(400, 300, 0.2, -0.5, 5, (100, 255, 100)),
        FloatingPlanet(900, 200, -0.3, -0.4, 3, (150, 100, 200)),
    ]

    title_font = pygame.font.SysFont("Arial", 80, bold=True)
    button_w, button_h = 240, 60

    def update_layout():
        cx = (screen_state['width'] - button_w) // 2
        for b in buttons:
            b.rect.x = cx

    def go_settings(): return STATE_SETTINGS
    def exit_game(): return "exit"
    def go_sim(): return STATE_SIM

    buttons = [
        Button(0, 300, button_w, button_h, "Play", go_sim),
        Button(0, 380, button_w, button_h, "Settings", go_settings),
        Button(0, 460, button_w, button_h, "Exit", exit_game),
    ]
    update_layout()

    current_screen = screen
    clock = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit"

            elif event.type == VIDEORESIZE:
                current_screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
                screen_state.update(width=event.w, height=event.h)
                update_layout()

            for btn in buttons:
                btn.update(mouse_pos)
                if btn.is_clicked(event):
                    return btn.action()

        # Update background planets
        for p in bg_planets:
            p.update(screen_state['width'], screen_state['height'])

        # Draw 2D-only
        current_screen.fill(BLACK)

        # Draw bg planets
        for p in bg_planets:
            p.draw(current_screen)

        # Draw title
        title = title_font.render("PyVerse", True, WHITE)
        title_rect = title.get_rect(center=(screen_state['width'] // 2, 150))
        current_screen.blit(title, title_rect)

        # Draw buttons
        for btn in buttons:
            btn.draw(current_screen)

        pygame.display.flip()
        clock.tick(60)
# pyverse.py
# A fully working gravity sandbox with reliable menu and settings

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# ------------------------------
# Global Settings
# ------------------------------
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
FPS = 60

# States
STATE_MENU = "menu"
STATE_SETTINGS = "settings"
STATE_SIM = "sim"
state = STATE_MENU

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
HOVER_BLUE = (150, 150, 255)
GRAY = (80, 80, 80)

# Gravity physics
G = 5000
DT = 0.01
SOFTENING = 0.1

# Camera
CAM_POS = [0.0, 0.0, 100.0]
ZOOM = 1.0
ZOOM_SPEED = 1.1

# ------------------------------
# Font & UI Setup
# ------------------------------
pygame.display.set_caption("PyVerse")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), RESIZABLE)
clock = pygame.time.Clock()

# Load fonts
title_font = pygame.font.SysFont("Arial", 80, bold=True)
menu_font = pygame.font.SysFont("Arial", 40)
small_font = pygame.font.SysFont("Arial", 28)

# ------------------------------
# Button Class
# ------------------------------
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

        txt_surf = menu_font.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.hovered

# ------------------------------
# Planet Class
# ------------------------------
class Planet:
    def __init__(self, x, y, z, vx, vy, vz, radius, color, mass=None):
        self.pos = np.array([x, y, z], dtype=float)
        self.vel = np.array([vx, vy, vz], dtype=float)
        self.radius = radius
        self.color = color
        self.mass = mass if mass else radius * 100

    def update(self, planets, dt):
        acc = np.array([0.0, 0.0, 0.0])
        for other in planets:
            if other is self:
                continue
            r_vec = other.pos - self.pos
            r_sq = np.dot(r_vec, r_vec)
            if r_sq < SOFTENING:
                continue
            r = np.sqrt(r_sq)
            force_mag = G * other.mass / r_sq
            acc += force_mag * r_vec / r
        self.vel += acc * dt
        self.pos += self.vel * dt

    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        glColor3f(*self.color)
        quad = gluNewQuadric()
        gluSphere(quad, self.radius * 1.0, 16, 12)
        glPopMatrix()

# ------------------------------
# Create Solar System
# ------------------------------
def create_solar_system():
    return [
        Planet(0, 0, 0, 0, 0, 0, 15, (1.0, 0.8, 0.2), mass=50000),  # Sun
        Planet(200, 0, 0, 0, 0, 30, 8, (0.0, 0.5, 1.0)),           # Earth
        Planet(350, 0, 0, 0, 0, 25, 6, (0.6, 0.4, 0.2)),           # Mars
        Planet(500, 0, 0, 0, 0, 18, 12, (0.9, 0.7, 0.3)),          # Jupiter
        # Add 50 asteroids
        *[Planet(
            np.random.uniform(100, 800),
            np.random.uniform(-20, 20),
            np.random.uniform(100, 800),
            np.random.uniform(-5, 5),
            np.random.uniform(-1, 1),
            np.random.uniform(-5, 5),
            np.random.uniform(1.5, 2.5),
            (0.5, 0.5, 0.5)
        ) for _ in range(50)]
    ]

# ------------------------------
# Menu Buttons
# ------------------------------
def go_to_settings():
    global state
    state = STATE_SETTINGS

def go_to_menu():
    global state
    state = STATE_MENU

def start_simulation():
    global state, planets
    state = STATE_SIM
    planets = create_solar_system()

def exit_game():
    pygame.quit()
    quit()

# Create buttons
button_w, button_h = 240, 60
menu_buttons = [
    Button(380, 300, button_w, button_h, "Play", start_simulation),
    Button(380, 380, button_w, button_h, "Settings", go_to_settings),
    Button(380, 460, button_w, button_h, "Exit", exit_game),
]

settings_buttons = [
    Button(380, 600, button_w, button_h, "Back", go_to_menu),
]

# ------------------------------
# Initialize OpenGL for Simulation
# ------------------------------
def init_opengl():
    global gl_screen
    gl_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    resize_gl(SCREEN_WIDTH, SCREEN_HEIGHT)

def resize_gl(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)

# ------------------------------
# Main Loop
# ------------------------------
def main():
    global state, CAM_POS, ZOOM, screen

    # Game variables
    planets = []
    dragging = False
    last_mouse = (0, 0)
    is_paused = False

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        event_list = pygame.event.get()

        for event in event_list:
            if event.type == QUIT:
                running = False

            elif event.type == VIDEORESIZE and state == STATE_SIM:
                # Only resize matters in sim
                pass  # Handled when re-init
            elif event.type == VIDEORESIZE and state != STATE_SIM:
                screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
                # Update button positions if needed
                cx = event.w // 2 - 120
                for btn in menu_buttons + settings_buttons:
                    btn.rect.x = cx

            # Handle button clicks
            if state == STATE_MENU:
                for btn in menu_buttons:
                    btn.update(mouse_pos)
                    if btn.is_clicked(event):
                        btn.action()

            elif state == STATE_SETTINGS:
                for btn in settings_buttons:
                    btn.update(mouse_pos)
                    if btn.is_clicked(event):
                        btn.action()

            elif state == STATE_SIM:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        is_paused = not is_paused
                    elif event.key == K_r:
                        CAM_POS = [0.0, 0.0, 100.0]
                        ZOOM = 1.0

                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        ZOOM = min(ZOOM * ZOOM_SPEED, 10.0)
                    elif event.button == 5:
                        ZOOM = max(ZOOM / ZOOM_SPEED, 0.1)
                    elif event.button == 1:
                        dragging = True
                        last_mouse = event.pos

                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False

                elif event.type == MOUSEMOTION:
                    if dragging:
                        dx, dy = event.pos[0] - last_mouse[0], event.pos[1] - last_mouse[1]
                        CAM_POS[0] += dx * 0.5 / ZOOM
                        CAM_POS[1] -= dy * 0.5 / ZOOM
                        last_mouse = event.pos

        # ------------------------------
        # Render Based on State
        # ------------------------------

        if state == STATE_MENU:
            screen.fill(BLACK)
            # Draw Title
            title = title_font.render("PyVerse", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
            screen.blit(title, title_rect)

            # Draw buttons
            for btn in menu_buttons:
                btn.update(mouse_pos)
                btn.draw(screen)

        elif state == STATE_SETTINGS:
            screen.fill((20, 20, 40))
            header = menu_font.render("Settings", True, WHITE)
            screen.blit(header, (SCREEN_WIDTH // 2 - 80, 100))

            text = small_font.render("Gravity: Strong | Zoom: Smooth | Theme: Dark", True, GRAY)
            screen.blit(text, (SCREEN_WIDTH // 2 - 250, 200))

            for btn in settings_buttons:
                btn.update(mouse_pos)
                btn.draw(screen)

        elif state == STATE_SIM:
            if state == STATE_SIM and 'gl_screen' not in globals():
                init_opengl()

            # Physics
            if not is_paused:
                for p in planets:
                    p.update(planets, DT)

            # OpenGL Render
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslatef(-CAM_POS[0], -CAM_POS[1], -CAM_POS[2])
            glScalef(ZOOM, ZOOM, ZOOM)

            for p in planets:
                p.draw()

            # 2D Overlay
            glDisable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            # Pause indicator
            pause_text = "⏸ PAUSED" if is_paused else "▶ RUNNING"
            color = (255, 255, 100) if is_paused else (100, 255, 100)
            txt_surf = small_font.render(pause_text, True, color)
            pygame.display.get_surface().blit(txt_surf, (SCREEN_WIDTH - 150, 20))

            instructions = "Drag: Pan | Scroll: Zoom | Space: Pause | R: Reset"
            instr_surf = small_font.render(instructions, True, (200, 200, 200))
            pygame.display.get_surface().blit(instr_surf, (10, 10))

            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glEnable(GL_DEPTH_TEST)

            pygame.display.flip()
            continue  # Skip 2D clear

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
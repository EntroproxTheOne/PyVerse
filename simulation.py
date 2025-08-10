# simulation.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from config import *

# === Global Settings ===
settings = None

# === Grid Settings ===
GRID_SIZE = 1000
GRID_STEP = 20
GRID_COLOR = (0.1, 0.3, 0.5)
GRID_ALPHA = 0.3

# === Planet Class ===
class Planet:
    def __init__(self, x, y, z, vx, vy, vz, radius, color, mass=None):
        self.pos = np.array([x, y, z], dtype=float)
        self.vel = np.array([vx, vy, vz], dtype=float)
        self.radius = radius
        self.color = color
        self.mass = mass if mass else radius * 100

    def update(self, planets, dt):
        acc = np.zeros(3)
        for other in planets:
            if other is self:
                continue
            r_vec = other.pos - self.pos
            r_sq = np.dot(r_vec, r_vec)
            if r_sq < 0.1:  # Softening
                continue
            r = np.sqrt(r_sq)
            force_mag = G * other.mass / r_sq
            acc += force_mag * r_vec / r
        self.vel += acc * dt
        self.pos += self.vel * dt

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glColor3f(*self.color)
        quad = gluNewQuadric()
        gluSphere(quad, self.radius, 16, 12)
        glPopMatrix()


def create_solar_system():
    """Create initial solar system with Sun and planets"""
    return [
        Planet(0, 0, 0, 0, 0, 0, 15, (1.0, 0.8, 0.2), mass=50000),  # Sun
        Planet(200, 0, 0, 0, 0, 30, 8, (0.0, 0.5, 1.0)),           # Earth
        Planet(350, 0, 0, 0, 0, 25, 6, (0.6, 0.4, 0.2)),           # Mars
        Planet(500, 0, 0, 0, 0, 18, 12, (0.9, 0.7, 0.3)),          # Jupiter
        # Add random asteroids
        *[Planet(
            np.random.uniform(100, 800),
            np.random.uniform(-20, 20),
            np.random.uniform(100, 800),
            np.random.uniform(-5, 5),
            np.random.uniform(-1, 1),
            np.random.uniform(-5, 5),
            np.random.uniform(1.5, 3.0),
            (0.5, 0.5, 0.5)
        ) for _ in range(30)]
    ]


def screen_to_world(x, y, width, height, cam_pos, zoom):
    """Convert screen pixel to 3D world coordinates"""
    world_x = (x - width / 2) / zoom + cam_pos[0]
    world_y = (height - y - height / 2) / zoom + cam_pos[1]
    world_z = cam_pos[2]
    return world_x, world_y, world_z


def draw_grid(cam_pos, zoom):
    """Draw X-Z plane grid at Y=0"""
    glLineWidth(1.0 + zoom * 0.05)
    glColor4f(*GRID_COLOR, GRID_ALPHA)
    glBegin(GL_LINES)
    half = GRID_SIZE // 2
    for i in range(-half, half + 1, GRID_STEP):
        # X lines (Z fixed)
        glVertex3f(-half, 0, i)
        glVertex3f(half, 0, i)
        # Z lines (X fixed)
        glVertex3f(i, 0, -half)
        glVertex3f(i, 0, half)
    glEnd()


def run_simulation(settings_obj):
    """
    Main simulation loop
    Returns: next state ('menu', 'exit')
    """
    global settings
    settings = settings_obj

    # Initialize window
    pygame.display.set_caption("PyVerse - Simulation")
    screen = pygame.display.set_mode((1000, 800), DOUBLEBUF | OPENGL | RESIZABLE)
    clock = pygame.time.Clock()

    # OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resize():
        w, h = pygame.display.get_surface().get_size()
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    resize()

    # === Simulation State ===
    planets = create_solar_system()
    CAM_POS = [0.0, 0.0, 100.0]  # Camera position
    ZOOM = 1.0
    ZOOM_SPEED = 1.1
    is_paused = False
    show_grid = settings.get("show_grid", True)

    # === Input State ===
    dragging = False
    last_mouse_pos = (0, 0)
    click_start_pos = None
    DRAG_THRESHOLD = 5  # pixels

    # === Main Loop ===
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit"

            elif event.type == VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), DOUBLEBUF | OPENGL | RESIZABLE)
                resize()

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    is_paused = not is_paused
                elif event.key == K_ESCAPE:
                    return "menu"  # Back to menu
                elif event.key == K_g:
                    show_grid = not show_grid

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse down
                    click_start_pos = mouse_pos
                    last_mouse_pos = mouse_pos
                    dragging = True

                elif event.button == 3:  # Right-click → spawn star
                    wx, wy, wz = screen_to_world(event.pos[0], event.pos[1], 1000, 800, CAM_POS, ZOOM)
                    star = Planet(wx, wy, wz, 0, 0, 0, 12, (1.0, 0.9, 0.4), mass=30000)
                    planets.append(star)

                elif event.button == 4:  # Scroll up
                    ZOOM = min(ZOOM * ZOOM_SPEED, 10.0)
                elif event.button == 5:  # Scroll down
                    ZOOM = max(ZOOM / ZOOM_SPEED, 0.1)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse released
                    if dragging and click_start_pos is not None:
                        end_pos = event.pos
                        dx = end_pos[0] - click_start_pos[0]
                        dy = end_pos[1] - click_start_pos[1]
                        distance = (dx**2 + dy**2)**0.5

                        if distance < DRAG_THRESHOLD:
                            # It was a click, not a drag → spawn planet
                            wx, wy, wz = screen_to_world(click_start_pos[0], click_start_pos[1], 1000, 800, CAM_POS, ZOOM)
                            p = Planet(
                                x=wx, y=wy, z=wz,
                                vx=np.random.uniform(-5, 5),
                                vy=np.random.uniform(-5, 5),
                                vz=0,
                                radius=3,
                                color=(0.4, 0.6, 1.0)  # Blue-green
                            )
                            planets.append(p)

                    # Always reset drag state
                    dragging = False
                    click_start_pos = None

            elif event.type == MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    sensitivity = 0.7
                    CAM_POS[0] += dx * sensitivity / ZOOM
                    CAM_POS[1] -= dy * sensitivity / ZOOM
                    last_mouse_pos = event.pos

        # === Update Physics ===
        if not is_paused:
            for p in planets:
                p.update(planets, DT)

        # === Render ===
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply camera transform
        glTranslatef(-CAM_POS[0], -CAM_POS[1], -CAM_POS[2])
        glScalef(ZOOM, ZOOM, ZOOM)

        # Draw grid (X-Z plane)
        if show_grid:
            draw_grid(CAM_POS, ZOOM)

        # Draw planets
        for p in planets:
            p.draw()

        # === 2D Overlay (UI) ===
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 1000, 800, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # UI Font
        font = pygame.font.SysFont("Arial", 18)
        get_surface = pygame.display.get_surface

        # Status: Paused/Running
        status = "⏸ PAUSED" if is_paused else "▶ RUNNING"
        color = (255, 255, 100) if is_paused else (100, 255, 100)
        txt = font.render(status, True, color)
        get_surface().blit(txt, (850, 20))

        # Instructions
        instr = "L-click: Add | Drag: Pan | R-click: Star | G: Grid | Esc: Menu"
        get_surface().blit(font.render(instr, True, (200, 200, 200)), (10, 10))

        # Mode indicator
        mode = "Mode: Pan" if dragging else "Mode: Click"
        mode_surf = font.render(mode, True, (180, 180, 100))
        get_surface().blit(mode_surf, (10, 40))

        # Pop matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)

        # === Finalize Frame ===
        pygame.display.flip()
        clock.tick(60)

    # End of loop
    return "menu"
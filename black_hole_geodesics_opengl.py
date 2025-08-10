# black_hole_geodesics_opengl.py

import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import math

# ------------------------------
# Physical Constants (Geometric Units: G = c = 1)
# ------------------------------
MASS = 1.0
HORIZON = 2 * MASS  # Event horizon radius

# Particle types: set kappa and initial conditions
KAPPA = 0      # 1 for massive (e.g. planets), 0 for photons (light)
PARTICLE_COUNT = 1000
MAX_L = 5.0    # Max angular momentum
TRAIL_LENGTH = 100
DT = 0.01      # Step in affine parameter λ

# ------------------------------
# OpenGL Setup
# ------------------------------
def init_opengl():
    pygame.init()
    display = (800, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Black Hole Geodesics (General Relativity)")

    glOrtho(0, display[0], 0, display[1], -1, 1)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glColor3f(1.0, 1.0, 1.0)

# Convert (r, ϕ) to screen coordinates
def to_screen(x, y, width=800, height=800, scale=150, offset=400):
    sx = offset + x * scale
    sy = offset + y * scale
    return sx, height - sy  # Flip Y

# ------------------------------
# Geodesic Integration: dr²/dλ²
# ------------------------------
def acceleration(r, L):
    if r <= 0:
        return 0
    L2 = L * L
    # dp/dλ = d²r/dλ²
    term1 = L2 / (r**3)
    term2 = -3 * L2 / (r**4)
    if KAPPA == 1:
        term3 = -1 / (r**2) + 1 / (r**3)
    else:  # KAPPA == 0 (photon)
        term3 = 0
    return term1 + term2 + term3

# RK4 integrator for one particle
def rk4_step(r, p, phi, L, dt):
    # dr/dλ = p
    # dp/dλ = acc(r, L)
    # dϕ/dλ = L / r²

    # RK4 for r and p
    k1_r = p
    k1_p = acceleration(r, L)
    k1_phi = L / (r*r) if r > 0.1 else 0

    k2_r = p + 0.5 * dt * k1_p
    k2_p = acceleration(r + 0.5 * dt * k1_r, L)
    k2_phi = L / ((r + 0.5 * dt * k1_r)**2) if r > 0.1 else 0

    k3_r = p + 0.5 * dt * k2_p
    k3_p = acceleration(r + 0.5 * dt * k2_r, L)
    k3_phi = L / ((r + 0.5 * dt * k2_r)**2) if r > 0.1 else 0

    k4_r = p + dt * k3_p
    k4_p = acceleration(r + dt * k3_r, L)
    k4_phi = L / ((r + dt * k3_r)**2) if r > 0.1 else 0

    r_new = r + (dt / 6.0) * (k1_r + 2*k2_r + 2*k3_r + k4_r)
    p_new = p + (dt / 6.0) * (k1_p + 2*k2_p + 2*k3_p + k4_p)
    phi_new = phi + (dt / 6.0) * (k1_phi + 2*k2_phi + 2*k3_phi + k4_phi)

    return r_new, p_new, phi_new

# ------------------------------
# Particle Class
# ------------------------------
class Particle:
    def __init__(self, L, r0=5.0, phi0=0.0):
        self.L = L  # Angular momentum
        self.r = r0
        self.p = 0.0  # dr/dλ
        self.phi = phi0
        self.trail = []

    def update(self):
        if self.r < HORIZON * 0.9:  # Fallen in
            return False

        self.r, self.p, self.phi = rk4_step(self.r, self.p, self.phi, self.L, DT)

        # Convert to Cartesian
        x = self.r * math.cos(self.phi)
        y = self.r * math.sin(self.phi)

        self.trail.append((x, y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)

        return True  # Still active

# ------------------------------
# Create Particles
# ------------------------------
def create_particles():
    particles = []
    for _ in range(PARTICLE_COUNT):
        L = np.random.uniform(2.0, MAX_L)  # Try different angular momenta
        phi0 = np.random.uniform(0, 2 * math.pi)
        r0 = np.random.uniform(4.0, 10.0)  # Start outside
        particles.append(Particle(L=L, r0=r0, phi0=phi0))
    return particles

# ------------------------------
# Main Loop
# ------------------------------
def main():
    init_opengl()
    particles = create_particles()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT)

        # Draw black hole shadow (r = 1.5 for photon sphere, but shadow is ~2.6 rs)
        # Event horizon: r = 2 → draw at scaled size
        glBegin(GL_TRIANGLE_FAN)
        glColor3f(0.0, 0.0, 0.0)  # Black
        num_segments = 32
        cx, cy = to_screen(0, 0)
        radius = 2 * (800 / 15)  # Scale horizon
        for i in range(num_segments + 1):
            theta = 2 * math.pi * i / num_segments
            x = cx + radius * math.cos(theta)
            y = cy + radius * math.sin(theta)
            glVertex2f(x, y)
        glEnd()

        # Optional: photon sphere ring (r = 3M = 3)
        glColor3f(0.3, 0.3, 0.5)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            theta = 2 * math.pi * i / 32
            x, y = to_screen(3 * math.cos(theta), 3 * math.sin(theta))
            glVertex2f(x, y)
        glEnd()

        # Update and draw particles
        alive_particles = []
        for p in particles:
            if p.update():
                alive_particles.append(p)

                # Draw trail
                if len(p.trail) > 1:
                    glLineWidth(0.8)
                    glBegin(GL_LINE_STRIP)
                    alpha = 0.1
                    for i, (x, y) in enumerate(p.trail):
                        alpha += 0.08
                        glColor4f(1.0, 1.0, 1.0, alpha)  # Fade trail
                        sx, sy = to_screen(x, y)
                        glVertex2f(sx, sy)
                    glEnd()

                # Draw current point
                x, y = p.trail[-1]
                sx, sy = to_screen(x, y)
                glBegin(GL_POINTS)
                glColor3f(1.0, 1.0, 1.0)
                glVertex2f(sx, sy)
                glEnd()

        particles = alive_particles

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
# splash.py
import pygame
from pygame.locals import *
import time

def show_splash(screen, clock):
    """
    Show a splash screen with a smooth white loading bar.
    No percentages — just clean animation.
    """
    w, h = screen.get_size()

    # Load splash background
    try:
        splash_img = pygame.image.load("splashscr.png")
        # Scale to fit width, preserve aspect
        img_w, img_h = splash_img.get_size()
        scale = w / img_w
        new_size = (int(img_w * scale), int(img_h * scale))
        splash_img = pygame.transform.scale(splash_img, new_size)
        x = 0
        y = (h - new_size[1]) // 2
    except pygame.error:
        print("⚠️ splashscr.png not found, using black screen")
        splash_img = None
        x = y = 0
        new_size = (w, h)

    # Font for loading text
    font = pygame.font.SysFont("Arial", 28)
    loading_text = font.render("Loading PyVerse...", True, (170, 200, 255))  # Soft blue

    # Loading bar settings
    bar_width = 400
    bar_height = 6
    bar_x = (w - bar_width) // 2
    bar_y = y + (new_size[1] + 60) if splash_img else h - 100

    # Timing
    start_time = time.time()
    fade_in_duration = 0.8
    hold_duration = 2.5
    fade_out_duration = 0.8
    total_duration = fade_in_duration + hold_duration + fade_out_duration

    running = True
    while running:
        elapsed = time.time() - start_time
        if elapsed >= total_duration:
            break  # Exit after full animation

        for event in pygame.event.get():
            if event.type == QUIT:
                return False

        # Fade alpha: 0 → 255 → 0
        if elapsed < fade_in_duration:
            alpha = int(255 * (elapsed / fade_in_duration))
        elif elapsed < fade_in_duration + hold_duration:
            alpha = 255
        else:
            alpha = int(255 * (1 - (elapsed - fade_in_duration - hold_duration) / fade_out_duration))

        # Draw background
        screen.fill((247, 0, 0))
        if splash_img:
            splash_img.set_alpha(alpha)
            screen.blit(splash_img, (x, y))
        else:
            # Solid black if no image
            pass

        # Only show text and bar when visible
        if alpha > 30:
            # Draw loading text
            text_x = (w - loading_text.get_width()) // 2
            screen.blit(loading_text, (text_x, bar_y - 40))

            # Simulate progress: smooth back-and-forth motion
            progress_width = (1 + (elapsed * 1.5) % 2) * (bar_width / 2)

            # Draw loading bar (outline)
            outline_rect = pygame.Rect(bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2)
            pygame.draw.rect(screen, (80, 80, 80), outline_rect)

            # Draw fill (white)
            fill_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
            pygame.draw.rect(screen, (255, 255, 255), fill_rect, border_radius=2)

        pygame.display.flip()
        clock.tick(60)

    return True  # Success
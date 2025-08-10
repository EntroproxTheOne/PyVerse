# config.py
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

G = 5000
DT = 0.01
SOFTENING = 0.1

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
HOVER_BLUE = (150, 150, 255)
GRAY = (80, 80, 80)

STATE_MENU = "menu"
STATE_SETTINGS = "settings"
STATE_SIM = "sim"   
# At bottom of config.py
__all__ = [
    'SCREEN_WIDTH', 'SCREEN_HEIGHT',
    'G', 'DT', 'SOFTENING',
    'BLACK', 'WHITE', 'BLUE', 'HOVER_BLUE', 'GRAY',
    'STATE_MENU', 'STATE_SETTINGS', 'STATE_SIM'
]
# settings.py
import json
import os

DEFAULT_SETTINGS = {
    "gravity_multiplier": 1.0,
    "zoom_speed": 1.1,
    "fullscreen": False,
    "show_grid": True,
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "window_size": [1000, 800]
}

SETTINGS_FILE = "user_settings.json"


class Settings:
    def __init__(self):
        self.data = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    for k, v in loaded.items():
                        if k in self.data:
                            self.data[k] = v
            except:
                pass
        self.save()

    def save(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        if key in self.data:
            self.data[key] = value
            self.save()
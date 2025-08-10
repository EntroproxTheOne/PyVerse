# save_load.py
import json
import os
import numpy as np

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_FILE = os.path.join(SAVE_DIR, "auto_save.pyv")


def save_universe(planets):
    data = []
    for p in planets:
        data.append({
            "pos": p.pos.tolist(),
            "vel": p.vel.tolist(),
            "radius": p.radius,
            "color": p.color,
            "mass": p.mass
        })
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Saved universe")
    except Exception as e:
        print(f"❌ Save failed: {e}")


def load_universe():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        from simulation import Planet
        return [Planet(
            x=p["pos"][0], y=p["pos"][1], z=p["pos"][2],
            vx=p["vel"][0], vy=p["vel"][1], vz=p["vel"][2],
            radius=p["radius"], color=p["color"], mass=p["mass"]
        ) for p in data]
    except:
        return None
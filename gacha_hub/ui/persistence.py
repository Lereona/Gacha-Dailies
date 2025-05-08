import os
import json
from pathlib import Path

def get_save_path():
    # Prefer project root for development, fallback to user app data dir
    project_root = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(project_root, 'games.json')
    try:
        # Try to write to project root
        with open(save_path, 'a') as f:
            pass
        return save_path
    except Exception:
        # Fallback to user app data dir
        app_dir = os.path.join(os.path.expanduser('~'), '.gacha_game_hub')
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'games.json')

def save_games(games):
    save_path = get_save_path()
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=2)

def load_games():
    save_path = get_save_path()
    if not os.path.exists(save_path):
        return []
    with open(save_path, 'r', encoding='utf-8') as f:
        return json.load(f) 
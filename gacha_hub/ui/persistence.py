import os
import json
from pathlib import Path

def get_save_path():
    # Always use project root for games.json
    project_root = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(project_root, 'games.json')
    print(f"[DEBUG] Using games.json path: {save_path}")
    return save_path

def save_games(games):
    save_path = get_save_path()
    tmp_path = save_path + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, save_path)

def load_games():
    save_path = get_save_path()
    if not os.path.exists(save_path):
        return []
    with open(save_path, 'r', encoding='utf-8') as f:
        return json.load(f) 
import os
from pathlib import Path
from typing import Optional
from datetime import timedelta

def format_playtime(seconds: int) -> str:
    """Format playtime in seconds to a human-readable string"""
    time = timedelta(seconds=seconds)
    hours = time.seconds // 3600
    minutes = (time.seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

def get_app_data_dir() -> Path:
    """Get the application data directory"""
    app_name = "GachaGameHub"
    if os.name == "nt":  # Windows
        base_dir = os.getenv("LOCALAPPDATA")
    else:  # Linux/Mac
        base_dir = os.path.expanduser("~/.local/share")
    
    app_dir = Path(base_dir) / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_database_path() -> Optional[Path]:
    """Get the database path from environment variable"""
    db_path = os.getenv("DB_PATH")
    if not db_path:
        return None
    return get_app_data_dir() / db_path 
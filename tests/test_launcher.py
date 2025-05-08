import pytest
from pathlib import Path
from gacha_hub.core.launcher import GameLauncher

def test_launch_nonexistent_game():
    """Test launching a non-existent game executable"""
    launcher = GameLauncher()
    result = launcher.launch_game("nonexistent.exe")
    assert result is None

def test_launch_game_invalid_path():
    """Test launching a game with invalid path"""
    launcher = GameLauncher()
    result = launcher.launch_game("")
    assert result is None 
import subprocess
from pathlib import Path
from typing import Optional

class GameLauncher:
    @staticmethod
    def launch_game(executable_path: str) -> Optional[subprocess.Popen]:
        """
        Launch a game executable and return the process object.
        
        Args:
            executable_path: Path to the game executable
            
        Returns:
            subprocess.Popen object if successful, None if failed
        """
        try:
            path = Path(executable_path)
            if not path.exists():
                raise FileNotFoundError(f"Game executable not found: {executable_path}")
            
            # Launch the game
            process = subprocess.Popen(
                [str(path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return process
            
        except Exception as e:
            print(f"Error launching game: {e}")
            return None 
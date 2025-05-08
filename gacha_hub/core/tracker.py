import psutil
import time
from typing import Optional, Dict
from datetime import datetime

class GameTracker:
    def __init__(self):
        self.tracked_processes: Dict[int, dict] = {}
    
    def start_tracking(self, process_id: int, game_id: int) -> bool:
        """
        Start tracking a game process.
        
        Args:
            process_id: The process ID to track
            game_id: The game ID in our database
            
        Returns:
            bool: True if tracking started successfully
        """
        try:
            if process_id in self.tracked_processes:
                return False
                
            self.tracked_processes[process_id] = {
                'game_id': game_id,
                'start_time': time.time(),
                'last_check': datetime.utcnow()
            }
            return True
            
        except Exception as e:
            print(f"Error starting process tracking: {e}")
            return False
    
    def stop_tracking(self, process_id: int) -> Optional[float]:
        """
        Stop tracking a process and return the elapsed time.
        
        Args:
            process_id: The process ID to stop tracking
            
        Returns:
            float: Elapsed time in seconds, or None if error
        """
        try:
            if process_id not in self.tracked_processes:
                return None
                
            process_info = self.tracked_processes.pop(process_id)
            elapsed_time = time.time() - process_info['start_time']
            return elapsed_time
            
        except Exception as e:
            print(f"Error stopping process tracking: {e}")
            return None
    
    def is_process_running(self, process_id: int) -> bool:
        """Check if a process is still running"""
        try:
            return psutil.pid_exists(process_id)
        except Exception:
            return False 
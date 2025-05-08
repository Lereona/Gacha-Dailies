from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from database.models import Game, DailyTask, Event

class StatsManager:
    def __init__(self, session: Session):
        self.session = session
    
    def update_playtime(self, game_id: int, additional_time: int) -> bool:
        """
        Update the total playtime for a game.
        
        Args:
            game_id: The game ID to update
            additional_time: Time to add in seconds
            
        Returns:
            bool: True if update successful
        """
        try:
            game = self.session.get(Game, game_id)
            if not game:
                return False
                
            game.total_playtime += additional_time
            game.last_played = datetime.utcnow()
            self.session.commit()
            return True
            
        except Exception as e:
            print(f"Error updating playtime: {e}")
            return False
    
    def get_daily_tasks(self, game_id: int) -> List[DailyTask]:
        """Get all daily tasks for a game"""
        statement = select(DailyTask).where(DailyTask.game_id == game_id)
        return list(self.session.exec(statement))
    
    def complete_daily_task(self, task_id: int) -> bool:
        """Mark a daily task as completed"""
        try:
            task = self.session.get(DailyTask, task_id)
            if not task:
                return False
                
            task.completed = True
            task.completed_at = datetime.utcnow()
            self.session.commit()
            return True
            
        except Exception as e:
            print(f"Error completing daily task: {e}")
            return False
    
    def get_active_events(self, game_id: int) -> List[Event]:
        """Get all active events for a game"""
        now = datetime.utcnow()
        statement = select(Event).where(
            Event.game_id == game_id,
            Event.start_date <= now,
            Event.end_date >= now
        )
        return list(self.session.exec(statement)) 
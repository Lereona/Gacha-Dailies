from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    executable_path: str
    total_playtime: int = Field(default=0)  # in seconds
    last_played: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DailyTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    name: str
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    name: str
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow) 
import pytest
from datetime import datetime
from sqlmodel import Session, SQLModel, create_engine
from gacha_hub.database.models import Game, DailyTask, Event

@pytest.fixture
def session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_game(session):
    """Test creating a new game"""
    game = Game(
        name="Test Game",
        executable_path="test.exe"
    )
    session.add(game)
    session.commit()
    
    assert game.id is not None
    assert game.total_playtime == 0
    assert game.last_played is None

def test_create_daily_task(session):
    """Test creating a daily task"""
    game = Game(name="Test Game", executable_path="test.exe")
    session.add(game)
    session.commit()
    
    task = DailyTask(
        game_id=game.id,
        name="Test Task"
    )
    session.add(task)
    session.commit()
    
    assert task.id is not None
    assert not task.completed
    assert task.completed_at is None 
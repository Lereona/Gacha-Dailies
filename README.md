# Gacha Game Hub

A desktop application for managing and tracking your gacha games. Features include game launching, playtime tracking, daily task management, and event tracking.

## Features

- Game launcher with executable management
- Playtime tracking using psutil
- Daily task completion tracking
- Event tracking and notifications
- SQLite database for persistent storage
- Modern PySide6-based GUI

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env.example` to `.env`
- Update database path if needed

4. Run the application:
```bash
python -m gacha_hub.main
```

## Development

- Project uses SQLModel for database operations
- PySide6 for the GUI
- psutil for process tracking
- Rich for console output
- Python-dotenv for environment management

## Project Structure

```
gacha_hub/
├── gacha_hub/          # Main package
│   ├── ui/            # GUI components
│   ├── database/      # Database models and operations
│   ├── core/          # Core functionality
│   └── utils.py       # Utility functions
├── tests/             # Test suite
└── requirements.txt   # Project dependencies
``` 